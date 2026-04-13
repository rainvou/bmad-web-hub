import json
import logging
import re
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.models import WSIncoming
from app.services import session_store
from app.services.api_runner import APIRunner, active_api_runners

logger = logging.getLogger(__name__)
router = APIRouter()


def _list_outputs() -> set[str]:
    output_dir = settings.OUTPUT_DIR
    if not output_dir.exists():
        return set()
    return {str(f.relative_to(output_dir)) for f in output_dir.rglob("*.md")}


def _generate_title(message: str, max_len: int = 40) -> str:
    text = re.sub(r'https?://\S+', '', message).strip()
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        text = message[:max_len]
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0]
        if not text:
            text = message[:max_len]
        text += '...'
    return text


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(ws: WebSocket, session_id: str):
    await ws.accept()

    session = await session_store.get_session(session_id)
    if not session:
        await ws.send_json({"type": "error", "message": "Session not found"})
        await ws.close()
        return

    messages = await session_store.get_messages(session_id)
    await ws.send_json({
        "type": "session_init",
        "session": session.model_dump(),
        "messages": [m.model_dump() for m in messages],
    })

    # Get or create API runner for this session
    runner = active_api_runners.get(session_id)
    if not runner:
        runner = APIRunner(skill_name=session.skill_name or "")
        # Replay existing conversation history into runner
        for msg in messages:
            if msg.role in ("user", "assistant"):
                runner.conversation.append({"role": msg.role, "content": msg.content})
        active_api_runners[session_id] = runner

    try:
        while True:
            raw = await ws.receive_text()
            try:
                incoming = WSIncoming(**json.loads(raw))
            except Exception:
                await ws.send_json({"type": "error", "message": "Invalid message format"})
                continue

            if incoming.type == "cancel":
                runner.cancel()
                await ws.send_json({"type": "error", "message": "Cancelled by user"})
                continue

            if incoming.type != "user_message" or not incoming.content.strip():
                continue

            # Persist user message
            await session_store.add_message(session_id, "user", incoming.content)

            # Auto-generate title on first message
            session = await session_store.get_session(session_id)
            if session.message_count <= 1:
                title = _generate_title(incoming.content)
                await session_store.update_session(session_id, title=title)
                await ws.send_json({"type": "title_updated", "title": title})

            await ws.send_json({"type": "assistant_start"})

            full_text = ""
            usage_info = {}

            try:
                async for event in runner.invoke(incoming.content):
                    etype = event.get("type")

                    if etype == "text_delta":
                        text = event["text"]
                        full_text += text
                        await ws.send_json({
                            "type": "assistant_chunk",
                            "text": text,
                        })

                    elif etype == "result":
                        full_text = event.get("content", full_text)
                        usage_info = event.get("usage", {})

                    elif etype == "error":
                        await ws.send_json({
                            "type": "error",
                            "message": event.get("message", "Unknown error"),
                        })

            except Exception as e:
                logger.exception("Error in API runner")
                await ws.send_json({"type": "error", "message": str(e)})

            if full_text:
                await session_store.add_message(session_id, "assistant", full_text)

            await ws.send_json({
                "type": "assistant_end",
                "content": full_text,
                "usage": usage_info,
            })

            # Check for new outputs
            outputs_after = _list_outputs()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.exception("WebSocket error")
    finally:
        # Keep runner alive for session resume
        pass
