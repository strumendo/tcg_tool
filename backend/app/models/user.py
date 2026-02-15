"""User ORM model."""

from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Represents an application user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    email: Mapped[str | None] = mapped_column(
        String(200), unique=True, nullable=True
    )
    language: Mapped[str] = mapped_column(
        String(2), default="en", server_default="en", nullable=False
    )

    # Relationships
    decks: Mapped[List["Deck"]] = relationship(
        "Deck", back_populates="user", cascade="all, delete-orphan"
    )
    battles: Mapped[List["Battle"]] = relationship(
        "Battle", back_populates="user", cascade="all, delete-orphan"
    )
    collection: Mapped[List["UserCollection"]] = relationship(
        "UserCollection", back_populates="user", cascade="all, delete-orphan"
    )
