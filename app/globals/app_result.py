from logging import getLogger, Logger
from typing import Generic, Any
from typing_extensions import TypeVar

from app.globals.businnes_error import AppError

logger: Logger = getLogger(__name__)

MISSING = object()


# Définition d'une variable de type (TypeVar)
# 'T' représentera le type de la donnée en cas de succès
# 'U' représentera le type de l'erreur en cas d'échec
# IMPORTANT: Aucune contrainte pour permettre la modularité maximale
# (tout type d'erreur personnalisé fonctionne, pas seulement AppError)
T = TypeVar("T")
U = TypeVar("U", default=AppError)


class GenericAppResult(Generic[T, U]):
    """
    Classe Générique pour typer les réponses d'opérations dans tout le systeme.

    Elle encapsule soit une donnée de succès (data), soit un message d'erreur (error).
    """

    __slots__ = ("_ok", "_data", "_error")

    def __init__(self, ok: bool, data: Any = MISSING, error: Any = MISSING):
        """
        Initialise une instance de GenericAppResult. Valide les arguments pour assurer la cohérence des données.
        NE PAS UTILISER DIRECTEMENT, UTILISER LES FONCTIONS DE CLASSE success() et failure() POUR CRÉER DES INSTANCES.
        Args:
            ok: bool: Indique si la réponse est un succès (True) ou une erreur (False).
            data: T | object: Les données de succès, requis si ok est True. Ignoré si ok est False.
            error: U | object: Le message d'erreur, requis si ok est False. Ignoré si ok est True.
        """
        if ok and data is MISSING:
            raise ValueError("Une réponse de succès doit contenir des données.")

        if not ok and error is MISSING:
            raise ValueError("Une réponse d'erreur doit contenir un message d'erreur.")

        self._ok: bool = ok
        self._data: T | object = data
        self._error: U | object = error

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
        return self._data  # type: ignore

    @property
    def error(self) -> U:
        """
        Retourne le message d'erreur. Lève une exception si c'est un succès.
        Returns:
            str: Le message d'erreur.
        Raises:
            RuntimeError: Si la réponse est un succès et que l'on tente d'accéder à l'erreur
        """
        if not self.is_error():
            raise RuntimeError(
                "Tentative d'accéder à l'erreur sur une réponse de succès."
            )
        return self._error  # type: ignore

    @classmethod
    def failure(cls, error: U) -> "GenericAppResult[T, U]":
        """
        Crée une réponse d'erreur avec le message d'erreur fourni.
        Args:
            error (U) : Le message d'erreur à inclure dans la réponse.
        Returns:
            GenericAppResult[T, U] : Une instance de GenericAppResult représentant une erreur.
        """
        # pyrefly: ignore [bad-return]
        return cls(ok=False, error=error)

    @classmethod
    def success(cls, data: T) -> "GenericAppResult[T, U]":
        """
        Crée une réponse de succès avec les données fournies.
        Args:
            data (T) : Les données à inclure dans la réponse de succès.
        Returns:
            GenericAppResult[T, U] : Une instance de GenericAppResult représentant un succès.
        """
        # pyrefly: ignore [bad-return]
        return cls(ok=True, data=data)

    def __repr__(self) -> str:
        if self.is_success():
            return f"GenericAppResult(Status=SUCCESS, Data={self._data})"
        return f"GenericAppResult(Status=FAILURE, Error={self._error})"
