from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.middlewares.exception_handler_middleware import (
    handle_exceptions,
    http_exception_handler,
    validation_exception_handler,
)
from app.middlewares.request_logging_middleware import log_requests


def setup_middlewares(app: FastAPI) -> None:
    app.middleware("http")(handle_exceptions)
    app.middleware("http")(log_requests)

    # pyrefly: ignore [bad-argument-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    # pyrefly: ignore [bad-argument-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
