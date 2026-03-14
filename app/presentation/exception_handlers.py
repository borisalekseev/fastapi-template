import logging
from typing import Final

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.error(
        "Validation error | method=%s path=%s content_type=%s errors=%s",
        request.method,
        request.url.path,
        request.headers.get("content-type"),
        exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": jsonable_encoder(exc.errors())},
    )


EXCEPTION_HANDLERS: Final[dict] = {  # type: ignore[type-arg]
    RequestValidationError: validation_exception_handler,
}
