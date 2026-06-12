"""
Modèle pour la table users.
Tous les utilisateurs de la plateforme.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Index,
    String,
    Boolean,
    func,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.config import Base
from app.db.mixins.integrity_error_mixin import IntegrityMapperMixin
from app.db.models.enums.enums import SexeType, UserType

if TYPE_CHECKING:
    # Import your models here for avoid circular imports and keep IDE type cheek
    pass

# Noms des contraintes
UQ_USERS_USERNAME = "uq_users_username"
UQ_USERS_EMAIL = "uq_users_email"
IDX_USERS_CREATED_AT_ID = "idx_users_created_at_id"
IDX_USERS_ROLE = "idx_users_role"
IDX_USERS_DELETED_AT = "idx_users_deleted_at"


class User(Base, IntegrityMapperMixin):
    """Utilisateurs de la plateforme (étudiants, modérateurs, etc.)."""

    __tablename__ = "users"

    # Attributs
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4, init=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Informations personnelles
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sexe: Mapped[SexeType] = mapped_column(SQLEnum(SexeType), nullable=False)

    # Rôle et permissions
    role: Mapped[UserType] = mapped_column(
        SQLEnum(UserType), default=UserType.USER, nullable=False, init=False
    )

    # Métadonnées

    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, init=False
    )

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, init=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False, init=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Index
    __table_args__ = (
        Index(
            IDX_USERS_CREATED_AT_ID,
            "created_at",
            "id",
            postgresql_where=(deleted_at == None),
        ),
        Index(
            UQ_USERS_EMAIL, "email", unique=True, postgresql_where=(deleted_at == None)
        ),
        Index(
            UQ_USERS_USERNAME,
            "username",
            unique=True,
            postgresql_where=(deleted_at == None),
        ),
        Index(IDX_USERS_ROLE, "role", postgresql_where=(deleted_at == None)),
        Index(
            IDX_USERS_DELETED_AT, "deleted_at", postgresql_where=(deleted_at != None)
        ),
    )

    # Relationships

    # Messages d'erreur
    ERROR_MESSAGES = {
        UQ_USERS_EMAIL: "Cet email est déjà utilisé.",
        UQ_USERS_USERNAME: "Ce nom d'utilisateur est déjà pris.",
    }
