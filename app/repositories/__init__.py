from typing import TypeVar, Generic, Optional

from app.globals.app_result import GenericAppResult
from app.globals.businnes_error import AppError

T = TypeVar("T")

class CrudResult(GenericAppResult[T, AppError], Generic[T]):
    """
    Classe générique pour typer les réponses d'opérations CRUD dans les Repository.

    Elle encapsule soit une donnée de succès (data), soit un message d'erreur (error).
    """


    def __init__(self, ok: bool, status_code: int, data: Optional[T] = None, error: Optional[AppError] = None):
        super().__init__(ok=ok, data=data, error=error)
        self._status_code: int = status_code

    # --- Méthodes utilitaires (Optional) ---

    def __repr__(self) -> str:
        if self.is_success():
            return f"<CRUDResponse Status {self._status_code} Success: {self._data!r}>"
        return f"<CRUDResponse Status {self._status_code} Error: {self._error!r}>"

    # --- Fonctions d'aide (Helpers) ---

    @classmethod
    def crud_success(cls, data: T, status_code: int = 200) -> "CrudResult[T]":
        """Crée une réponse de succès avec les données fournies."""
        return cls(ok=True, data=data, status_code=status_code)

    @classmethod
    def crud_error(cls, error: AppError, status_code: int = 500) -> "CrudResult[T]":
        """Crée une réponse d'erreur avec l'objet d'erreur fourni."""
        return cls(ok=False, error=error, status_code=status_code)

    @property
    def status_code(self) -> int:
        return self._status_code