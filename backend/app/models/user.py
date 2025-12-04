"""User model for authentication"""
from typing import Optional, List
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User account"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Profile
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(String(500))

    # Preferences
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    preferred_format: Mapped[str] = mapped_column(String(20), default="standard")

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    tournaments: Mapped[List["Tournament"]] = relationship("Tournament", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.username}>"


# Import here to avoid circular imports
from app.models.tournament import Tournament
