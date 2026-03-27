"""POST /api/chat — SSE streaming endpoint."""

import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from server.schemas import ChatRequest

router = APIRouter()


@router.post("/api/chat")
async def chat(request: Request, body: ChatRequest):
    session_store = request.app.state.session_store
    session_id, agent = session_store.get_or_create(body.session_id)

    async def event_generator():
        # Send session_id as first event so client knows it
        yield {
            "event": "session",
            "data": json.dumps({"session_id": session_id}),
        }
        async for event in agent.run_stream(body.message):
            yield event

    return EventSourceResponse(event_generator())
