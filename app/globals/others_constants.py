from app.schemas.globals.others_schemas import AuthErrorMessage


class OtherConstants:
    COMMON_API_RESPONSES = {
        401: {"description": "Unauthorized", "model": AuthErrorMessage},
        403: {"description": "Forbidden", "model": AuthErrorMessage},
    }
