from abc import ABC
from typing import TypeVar, Generic, Optional

from pydantic.v1.generics import GenericModel

# Définition d'une variable de type (TypeVar)
# 'T' représentera le type de la donnée en cas de succès
T = TypeVar("T")

class GlobalAppResult(GenericModel, Generic[T], ABC):
    """
    Classe Générique + Abstraite pour typer les réponses d'opérations dans tout le systeme.

    Elle encapsule soit une donnée de succès (data), soit un message d'erreur (error).
    """

    _ok: bool
    _data: Optional[T]
    _error: Optional[str]

    def is_success(self) -> bool:
        """
        Verifie si la réponse est une reponse de succès.
        Returns:
            bool: True si c'est une reponse de succès, False sinon.
        """
        return self._ok

    def is_error(self) -> bool:
        """
        Verifie si la réponse est une reponse d'erreur.
        Returns:
            bool: True si c'est une reponse d'erreur, False sinon.
        """
        return not self._ok

    @property
    def data(self) -> T:
        """
        Retourne les données de succès. Lève une exception si c'est une erreur.
        Returns:
            T: Les données de succès.
        Raises:
            RuntimeError: Si la réponse est une erreur et que l'on tente d'accéder aux données.
        """
        if self.is_error():
            raise RuntimeError(
                "Tentative d'accéder aux données sur une réponse d'erreur."
            )
        return self._data

    @property
    def error(self) -> str:
        """
        Retourne le message d'erreur. Lève une exception si c'est un succès.
        Returns:
            str: Le message d'erreur.
        Raises:
            RuntimeError: Si la réponse est un succès et que l'on tente d'accéder à l'erreur
        """
        if not self._error:
            raise RuntimeError(
                "Tentative d'accéder à l'erreur sur une réponse de succès."
            )
        return self._error