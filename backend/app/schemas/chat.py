"""Pydantic schemas for AI chat endpoints."""

from typing import Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Request body for sending a chat message."""

    message: str
    system_context: Optional[str] = None
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    """Response from the AI chat endpoint."""

    response: str
    tokens_used: Optional[int] = None
