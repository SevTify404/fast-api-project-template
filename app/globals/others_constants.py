from typing import Any

from app.schemas.globals.others_schemas import AuthErrorMessage


class OtherConstants:
    COMMON_API_RESPONSES: dict[int | str, dict[str, Any]] = {
        401: {"description": "Unauthorized", "model": AuthErrorMessage},
        403: {"description": "Forbidden", "model": AuthErrorMessage},
    }
