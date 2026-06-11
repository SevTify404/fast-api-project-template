from enum import Enum

from pydantic import BaseModel


class AppErrorType(str, Enum):
    LOCKED_CONTENT = "LOCKED_CONTENT"
    NOT_FOUND = "NOT_FOUND"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class AppError(BaseModel):
    """Modèle de données pour représenter une erreur métier."""
    type: AppErrorType
    error_message: str

