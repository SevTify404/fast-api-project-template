from typing import TypeVar, Generic, Optional

from app.globals.app_result import GenericAppResult
from app.globals.businnes_error import AppError
from app.globals.services_names import ServicesNames

T = TypeVar("T")


class IntegrationServiceResult(GenericAppResult[T, AppError], Generic[T]):
    """
    Classe générique pour typer les réponses d'opérations CRUD dans les Repository.

    Elle encapsule soit une donnée de succès (data), soit un message d'erreur (error).
    """

    def __init__(self, ok: bool, service_name: str, status_code: int, data: Optional[T] = None,
                 error: Optional[AppError] = None):
        super().__init__(ok=ok, data=data, error=error)
        self._service_name: str = service_name
        self._status_code: int = status_code

    # --- Méthodes utilitaires (Optional) ---

    def __repr__(self) -> str:
        if self.is_success():
            return f"<IntegrationServiceResult {self._service_name} Success: {self._data!r}>"
        return f"<IntegrationServiceResult {self._service_name} Error: {self._error!r}>"

    @property
    def service_name(self) -> str:
        return self._service_name

    @property
    def status_code(self) -> int:
        return self._status_code

    # --- Fonctions d'aide (Helpers) ---

    @classmethod
    def integration_service_succes(cls, data: T, status_code: int = 200,
                                   service_name: str = ServicesNames.UNKNOWN_SERVICE) -> "IntegrationServiceResult[T]":
        """Crée une réponse de succès avec les données fournies."""
        return cls(ok=True, data=data, status_code=status_code, service_name=service_name)

    @classmethod
    def crud_error(cls, error: AppError, status_code: int = 500,
                   service_name: str = ServicesNames.UNKNOWN_SERVICE) -> "IntegrationServiceResult[T]":
        """Crée une réponse d'erreur avec l'objet d'erreur fourni."""
        return cls(ok=False, error=error, status_code=status_code, service_name=service_name)
