import asyncio
import json
import logging
import re
import shlex
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class BrightDataServiceError(Exception):
    def __init__(self, message: str, code: str, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class BrightDataResultNormalizer:
    @staticmethod
    def normalize_cli_result(stdout: bytes, stderr: bytes) -> tuple[str, list[dict[str, Any]]]:
        """
        Extracts snapshot ID and payload from the CLI raw JSON output.
        Also inspects stderr for 'response_id: ...' to extract the true Bright Data execution ID.
        """
        try:
            data = json.loads(stdout.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise BrightDataServiceError(
                f"Invalid JSON from CLI: {str(e)}", "ERR_CLI_MALFORMED", False
            ) from e

        # Extract response_id from stderr
        stderr_str = stderr.decode("utf-8", errors="replace")
        match = re.search(r"response_id:\s*([a-zA-Z0-9_]+)", stderr_str)
        extracted_id = match.group(1) if match else None

        if isinstance(data, list):
            # No envelope, just the payload array
            payload = data
            snapshot_id = extracted_id
        elif isinstance(data, dict):
            # Assumed envelope
            snapshot_id = data.get("snapshot_id") or data.get("collection_id") or extracted_id
            payload = data.get("data", data)
            if not isinstance(payload, list):
                payload = [payload]
        else:
            raise BrightDataServiceError(
                "Unexpected CLI JSON structure", "ERR_CLI_MALFORMED", False
            )

        if not snapshot_id:
            # The spec requires bright_data_snapshot_id for idempotency.
            # If the real CLI does not provide one, we generate a trace ID
            import uuid

            snapshot_id = f"trace_{uuid.uuid4().hex[:12]}"

        return snapshot_id, payload


class BrightDataService:
    @staticmethod
    async def run_collector(collector_id: str, target_url: str) -> tuple[str, list[dict[str, Any]]]:
        """
        Executes 'bdata scraper run <collector_id> <url>' securely.
        Uses asyncio.create_subprocess_exec for bounded streaming capture.
        NEVER uses shell=True.
        """
        cmd_args = shlex.split(settings.bdata_cli_path)
        args = cmd_args + ["scraper", "run", collector_id, target_url]
        timeout = settings.bdata_cli_timeout_seconds
        max_bytes = settings.bdata_cli_max_output_bytes

        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise BrightDataServiceError(
                "Bright Data CLI executable not found.", "ERR_CLI_MISSING", False
            ) from e

        async def read_stream_bounded(stream: asyncio.StreamReader | None) -> bytes:
            if stream is None:
                return b""
            chunks = []
            total_bytes = 0
            while True:
                # Read chunks of up to 64KB
                chunk = await stream.read(65536)
                if not chunk:
                    break
                chunks.append(chunk)
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    process.kill()
                    raise BrightDataServiceError(
                        "CLI output exceeded max bound.", "ERR_CLI_OUTPUT_BOUND", False
                    )
            return b"".join(chunks)

        try:
            # Wait for output or timeout
            stdout_data, stderr_data = await asyncio.wait_for(
                asyncio.gather(
                    read_stream_bounded(process.stdout), read_stream_bounded(process.stderr)
                ),
                timeout=timeout,
            )
            await process.wait()
        except TimeoutError as e:
            import contextlib

            with contextlib.suppress(OSError):
                process.kill()
            raise BrightDataServiceError("Execution timed out.", "ERR_CLI_TIMEOUT", True) from e

        if process.returncode != 0:
            # Do NOT log the raw error message if it might contain secrets.
            logger.error(f"bdata CLI failed with code {process.returncode}")
            raise BrightDataServiceError(
                f"CLI exited with non-zero code {process.returncode}", "ERR_CLI_FAILED", False
            )

        if not stdout_data:
            raise BrightDataServiceError("CLI returned empty output", "ERR_CLI_EMPTY", True)

        snapshot_id, payload = BrightDataResultNormalizer.normalize_cli_result(
            stdout_data, stderr_data
        )
        return snapshot_id, payload

    @staticmethod
    async def request_heal(collector_id: str, what_broke: str) -> dict[str, Any]:
        """
        Executes 'bdata scraper heal <collector_id> "<what_broke>"' securely.
        Uses asyncio.create_subprocess_exec for bounded streaming capture.
        NEVER uses shell=True.
        """
        cmd_args = shlex.split(settings.bdata_cli_path)
        args = cmd_args + ["scraper", "heal", collector_id, what_broke]
        timeout = settings.bdata_cli_timeout_seconds
        max_bytes = settings.bdata_cli_max_output_bytes

        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise BrightDataServiceError(
                "Bright Data CLI executable not found.", "ERR_CLI_MISSING", False
            ) from e

        async def read_stream_bounded(stream: asyncio.StreamReader | None) -> bytes:
            if stream is None:
                return b""
            chunks = []
            total_bytes = 0
            while True:
                chunk = await stream.read(65536)
                if not chunk:
                    break
                chunks.append(chunk)
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    import contextlib
                    with contextlib.suppress(OSError):
                        process.kill()
                    raise BrightDataServiceError(
                        "CLI output exceeded max bound.", "ERR_CLI_OUTPUT_BOUND", False
                    )
            return b"".join(chunks)

        try:
            # Wait for output or timeout
            stdout_data, stderr_data = await asyncio.wait_for(
                asyncio.gather(
                    read_stream_bounded(process.stdout), read_stream_bounded(process.stderr)
                ),
                timeout=timeout,
            )
            await process.wait()
        except TimeoutError as e:
            import contextlib
            with contextlib.suppress(OSError):
                process.kill()
            raise BrightDataServiceError("Execution timed out.", "ERR_CLI_TIMEOUT", True) from e

        if process.returncode != 0:
            logger.error(f"bdata CLI failed with code {process.returncode}")
            raise BrightDataServiceError(
                f"CLI exited with non-zero code {process.returncode}", "ERR_CLI_FAILED", False
            )

        if not stdout_data:
            raise BrightDataServiceError("CLI returned empty output", "ERR_CLI_EMPTY", True)

        try:
            payload = json.loads(stdout_data.decode("utf-8"))
            if not isinstance(payload, dict):
                raise BrightDataServiceError(
                    "Unexpected CLI JSON structure (expected dict)", "ERR_CLI_MALFORMED", False
                )
            return payload
        except json.JSONDecodeError as e:
            raise BrightDataServiceError(
                f"Invalid JSON from CLI: {str(e)}", "ERR_CLI_MALFORMED", False
            ) from e
