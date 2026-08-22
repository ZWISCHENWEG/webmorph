from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.brightdata_service import (
    BrightDataResultNormalizer,
    BrightDataService,
    BrightDataServiceError,
)


@pytest.mark.asyncio
async def test_subprocess_security():
    """Test that subprocess is called with shell=False and bounded."""
    with patch("app.services.brightdata_service.asyncio.create_subprocess_exec") as mock_exec, \
         patch("app.services.brightdata_service.asyncio.wait_for") as mock_wait:
        
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.wait = AsyncMock()
        
        mock_stdout = AsyncMock()
        mock_stdout.read = AsyncMock(side_effect=[b'[{"feature_name": "test"}]', b''])
        mock_stderr = AsyncMock()
        mock_stderr.read = AsyncMock(side_effect=[b'response_id: d2test', b''])
        
        mock_process.stdout = mock_stdout
        mock_process.stderr = mock_stderr
        
        mock_exec.return_value = mock_process
        
        mock_wait.return_value = (b'[{"feature_name": "test"}]', b'response_id: d2test')
        
        await BrightDataService.run_collector("c_test", "https://test.com")
        
        mock_exec.assert_called_once()
        args, kwargs = mock_exec.call_args
        
        assert "npx" in args
        assert "bdata" in args
        assert mock_exec.call_args[0][0] != "/bin/sh"
        
@pytest.mark.asyncio
async def test_normalizer_raw_array_extracts_id():
    """Test normalizer properly extracts response_id from stderr."""
    raw_bytes = b'[{"feature_name": "test"}]'
    stderr_bytes = b'Triggered (response_id: d2test_123)'
    snapshot_id, payload = BrightDataResultNormalizer.normalize_cli_result(raw_bytes, stderr_bytes)
    assert snapshot_id == "d2test_123"
    assert isinstance(payload, list)
    assert payload[0]["feature_name"] == "test"

@pytest.mark.asyncio
async def test_normalizer_fallback_id():
    """Test normalizer generates synthetic trace ID if missing."""
    raw_bytes = b'[{"feature_name": "test"}]'
    stderr_bytes = b'Some logs without ID'
    snapshot_id, payload = BrightDataResultNormalizer.normalize_cli_result(raw_bytes, stderr_bytes)
    assert snapshot_id.startswith("trace_")
    
@pytest.mark.asyncio
async def test_cli_failure_non_zero():
    with patch("app.services.brightdata_service.asyncio.create_subprocess_exec") as mock_exec, \
         patch("app.services.brightdata_service.asyncio.wait_for") as mock_wait:
        
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.wait = AsyncMock()
        
        mock_stdout = AsyncMock()
        mock_stdout.read = AsyncMock(side_effect=[b'', b''])
        mock_stderr = AsyncMock()
        mock_stderr.read = AsyncMock(side_effect=[b'Some error', b''])
        
        mock_process.stdout = mock_stdout
        mock_process.stderr = mock_stderr
        
        mock_exec.return_value = mock_process
        
        mock_wait.return_value = (b'', b'Some error')
        
        with pytest.raises(BrightDataServiceError) as exc:
            await BrightDataService.run_collector("c_test", "https://test.com")
        
        assert exc.value.code == "ERR_CLI_FAILED"
        assert exc.value.retryable is False

@pytest.mark.asyncio
async def test_cli_timeout():
    with patch("app.services.brightdata_service.asyncio.create_subprocess_exec") as mock_exec, \
         patch("app.services.brightdata_service.asyncio.wait_for") as mock_wait:
         
        mock_process = MagicMock()
        mock_process.wait = AsyncMock()
        
        mock_stdout = AsyncMock()
        mock_stdout.read = AsyncMock(side_effect=[b'', b''])
        mock_stderr = AsyncMock()
        mock_stderr.read = AsyncMock(side_effect=[b'', b''])
        
        mock_process.stdout = mock_stdout
        mock_process.stderr = mock_stderr
        
        mock_exec.return_value = mock_process
        mock_wait.side_effect = TimeoutError()
        
        with pytest.raises(BrightDataServiceError) as exc:
            await BrightDataService.run_collector("c_test", "https://test.com")
        
        assert exc.value.code == "ERR_CLI_TIMEOUT"
        assert exc.value.retryable is True
        mock_process.kill.assert_called_once()
