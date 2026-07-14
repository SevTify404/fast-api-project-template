from logging import getLogger

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.globals.businnes_error import AppError, AppErrorType
from app.globals.messages import Messages
from app.schemas.globals.api_base_response import DefaultAppApiResponse

logger = getLogger("exception_handler")


async def handle_exceptions(request: Request, call_next) -> Response:
    """
    Middleware pour intercepter et gérer les exceptions globales non gérées par FastAPI.

    Ce middleware:
    1. Log l'exception avec le traceback complet pour le débogage
    2. Retourne une réponse 500 standardisée utilisant ApiBaseResponse

    Args:
        request: La requête entrante
        call_next: Fonction pour appeler le prochain middleware/endpoint

    Returns:
        Response: La réponse HTTP (soit normale, soit une réponse d'erreur 500)
    """
    try:
        return await call_next(request)
    except Exception as e:
        # Logger l'exception avec le traceback complet
        logger.exception(
            f"Exception non gérée: {e.__class__.__name__} - {e}", exc_info=e
        )

        error_response = DefaultAppApiResponse.error_response(
            error_message=AppError(
                error_type=AppErrorType.UNKNOWN_ERROR,
                error_message=Messages.INTERNAL_SERVER_ERROR,
            ),
            response=Response(),
            status_code=500,
        )

        return JSONResponse(content=error_response.model_dump(), status_code=500)


def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Gestionnaire d'exceptions pour standardiser les HTTPExceptions de l'application (ex: 401, 403, 404).
    """
    if isinstance(exc.detail, AppError):
        app_error = exc.detail
    else:
        # Déterminer le type d'erreur en fonction du code statut HTTP
        if exc.status_code == 401:
            error_type = AppErrorType.UNAUTHORIZED
        elif exc.status_code == 403:
            error_type = AppErrorType.FORBIDDEN
        elif exc.status_code == 404:
            error_type = AppErrorType.NOT_FOUND
        elif exc.status_code == 400:
            error_type = AppErrorType.BAD_REQUEST
        elif exc.status_code == 422:
            error_type = AppErrorType.VALIDATION_ERROR
        else:
            error_type = AppErrorType.UNKNOWN_ERROR

        app_error = AppError(
            error_type=error_type,
            error_message=str(exc.detail),
        )

    error_response = DefaultAppApiResponse.error_response(
        error_message=app_error,
        response=Response(),
        status_code=exc.status_code,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers=exc.headers if hasattr(exc, "headers") else None,
    )


def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Gestionnaire d'exceptions pour uniformiser les erreurs de validation de schéma (422).
    """
    errors_details = []
    for error in exc.errors():
        loc_path = [str(x) for x in error["loc"] if x != "body"]
        loc = ".".join(loc_path)
        msg = error["msg"]
        if loc:
            errors_details.append(f"Champ '{loc}': {msg}")
        else:
            errors_details.append(msg)

    error_message = "Erreur de validation: " + "; ".join(errors_details)

    app_error = AppError(
        error_type=AppErrorType.VALIDATION_ERROR,
        error_message=error_message,
    )

    error_response = DefaultAppApiResponse.error_response(
        error_message=app_error,
        response=Response(),
        status_code=422,
    )

    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(),
    )
