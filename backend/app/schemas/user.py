"""Pydantic schemas for user endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    """Serialization schema for a user."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[str] = None
    language: str
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str
    email: Optional[str] = None
    language: str = "en"
