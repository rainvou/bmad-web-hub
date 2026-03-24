import json
import logging
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.models import WSIncoming
from app.services import session_store
from app.services.claude_runner import ClaudeRunner, active_runners

logger = logging.getLogger(__name__)
router = APIRouter()


def _list_outputs() -> set[str]:
    """Snapshot the output directory."""
    output_dir = settings.OUTPUT_DIR
    if not output_dir.exists():
        return set()
    return {str(f.relative_to(output_dir)) for f in output_dir.rglob("*.md")}


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(ws: WebSocket, session_id: str):
    await ws.accept()

    session = await session_store.get_session(session_id)
    if not session:
        await ws.send_json({"type": "error", "message": "Session not found"})
        await ws.close()
        return

    # Send session init with history
    messages = await session_store.get_messages(session_id)
    await ws.send_json({
        "type": "session_init",
        "session": session.model_dump(),
        "messages": [m.model_dump() for m in messages],
    })

    try:
        while True:
            raw = await ws.receive_text()
            try:
                incoming = WSIncoming(**json.loads(raw))
            except Exception:
                await ws.send_json({"type": "error", "message": "Invalid message format"})
                continue

            if incoming.type == "cancel":
                runner = active_runners.get(session_id)
                if runner:
                    await runner.cancel()
                    del active_runners[session_id]
                await ws.send_json({"type": "error", "message": "Cancelled by user"})
                continue

            if incoming.type != "user_message" or not incoming.content.strip():
                continue

            # Reject if already processing
            if session_id in active_runners:
                await ws.send_json({"type": "error", "message": "Please wait for the current response to complete."})
                continue

            # Persist user message
            await session_store.add_message(session_id, "user", incoming.content)

            # Refresh session to get claude_session_id
            session = await session_store.get_session(session_id)
            is_first_turn = session.claude_session_id is None

            runner = ClaudeRunner(
                skill_name=session.skill_name or "",
                claude_session_id=session.claude_session_id,
            )
            active_runners[session_id] = runner

            # Snapshot outputs before turn
            outputs_before = _list_outputs()

            await ws.send_json({"type": "assistant_start"})

            text_chunks: list[str] = []
            usage_info = {}
            result_text = ""

            try:
                async for event in runner.invoke(incoming.content, is_first_turn=is_first_turn):
                    etype = event.get("type")

                    if etype == "system" and event.get("subtype") == "init":
                        claude_sid = event.get("session_id")
                        if claude_sid:
                            await session_store.update_session(
                                session_id, claude_session_id=claude_sid
                            )

                    elif etype == "assistant":
                        msg = event.get("message", {})
                        contents = msg.get("content", [])
                        for block in contents:
                            btype = block.get("type")
                            if btype == "text":
                                text = block.get("text", "")
                                if text:
                                    text_chunks.append(text)
                                    await ws.send_json({
                                        "type": "assistant_chunk",
                                        "text": text,
                                    })
                            elif btype == "tool_use":
                                # Notify the user that a tool is being used
                                tool_name = block.get("name", "unknown")
                                await ws.send_json({
                                    "type": "tool_use",
                                    "tool": tool_name,
                                })

                    elif etype == "result":
                        result_text = event.get("result", "")
                        usage_info = {
                            "cost_usd": event.get("total_cost_usd"),
                            "duration_ms": event.get("duration_ms"),
                        }

                    elif etype == "error":
                        await ws.send_json({
                            "type": "error",
                            "message": event.get("message", "Unknown error"),
                        })

            except Exception as e:
                logger.exception("Error in Claude runner")
                await ws.send_json({"type": "error", "message": str(e)})

            # Determine the final text: prefer streamed chunks, fallback to result
            full_text = "".join(text_chunks) if text_chunks else result_text

            # Persist assistant message
            if full_text:
                await session_store.add_message(session_id, "assistant", full_text)

            await ws.send_json({
                "type": "assistant_end",
                "content": full_text,
                "usage": usage_info,
            })

            # Check for new outputs
            outputs_after = _list_outputs()
            new_outputs = outputs_after - outputs_before
            for out_path in new_outputs:
                parts = Path(out_path).parts
                category = parts[0] if len(parts) > 1 else "uncategorized"
                await ws.send_json({
                    "type": "output_detected",
                    "file": out_path,
                    "category": category,
                })
                await session_store.update_session(session_id, output_file=out_path)

            # Cleanup runner
            active_runners.pop(session_id, None)

    except WebSocketDisconnect:
        runner = active_runners.pop(session_id, None)
        if runner:
            await runner.cancel()
    except Exception as e:
        logger.exception("WebSocket error")
        active_runners.pop(session_id, None)
