from fastapi import APIRouter, HTTPException, Query

from app.models import SessionCreate, SessionResponse, MessageResponse
from app.services import session_store

router = APIRouter(tags=["sessions"])


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(data: SessionCreate):
    return await session_store.create_session(data)


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    status: str | None = Query(None),
    skill_name: str | None = Query(None),
):
    return await session_store.list_sessions(status=status, skill_name=skill_name)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    session = await session_store.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str):
    deleted = await session_store.delete_session(session_id)
    if not deleted:
        raise HTTPException(404, "Session not found")


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(session_id: str):
    session = await session_store.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return await session_store.get_messages(session_id)
