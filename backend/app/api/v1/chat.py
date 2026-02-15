"""AI chat API route handlers."""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.dependencies import DBSession
from app.integrations import ClaudeClient
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import chat_service


router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(db: DBSession, request: ChatRequest) -> ChatResponse:
    """Send a message to the AI assistant and receive a response."""
    try:
        # Build context
        deck_context = ""
        if request.deck_id:
            deck_context = await chat_service.build_deck_context(db, request.deck_id)

        meta_context = await chat_service.build_meta_context(db)
        system_prompt = chat_service.build_system_prompt(deck_context, meta_context)

        # Format history
        history = chat_service.format_history_for_api(
            [msg.model_dump() for msg in request.history]
        )

        client = ClaudeClient()
        response_text = await client.chat(
            message=request.message,
            system_context=system_prompt,
            history=history,
        )
        return ChatResponse(response=response_text)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(exc)}",
        )


@router.post("/stream")
async def stream_message(db: DBSession, request: ChatRequest):
    """Stream a chat response using Server-Sent Events."""

    async def event_generator():
        try:
            # Build context
            deck_context = ""
            if request.deck_id:
                deck_context = await chat_service.build_deck_context(
                    db, request.deck_id
                )

            meta_context = await chat_service.build_meta_context(db)
            system_prompt = chat_service.build_system_prompt(
                deck_context, meta_context
            )

            # Format history
            history = chat_service.format_history_for_api(
                [msg.model_dump() for msg in request.history]
            )

            client = ClaudeClient()
            async for chunk in client.chat_stream(
                message=request.message,
                system_context=system_prompt,
                history=history,
            ):
                data = json.dumps({"type": "text", "content": chunk})
                yield f"data: {data}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as exc:
            error_data = json.dumps({"type": "error", "content": str(exc)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
