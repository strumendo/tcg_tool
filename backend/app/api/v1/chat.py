"""AI chat API route handlers."""

from fastapi import APIRouter, HTTPException

from app.integrations import ClaudeClient
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest) -> ChatResponse:
    """Send a message to the AI assistant and receive a response."""
    try:
        client = ClaudeClient()
        response_text = await client.chat(
            message=request.message,
            system_context=request.system_context or "",
        )
        return ChatResponse(response=response_text)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(exc)}",
        )
