import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": "ERR_NOT_FOUND",
                        "message": exc.detail,
                        "retryable": False,
                    }
                },
            )
        # Fallback for other HTTP exceptions
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"ERR_HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "retryable": False,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "ERR_VALIDATION",
                    "message": "Invalid request payload or parameters",
                    "retryable": False,
                }
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "ERR_INTERNAL",
                    "message": "An internal server error occurred",
                    "retryable": True,
                }
            },
        )
