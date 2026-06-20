from fastapi import Request
from fastapi.responses import JSONResponse

from backend.core.logging import logger


async def http_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )
