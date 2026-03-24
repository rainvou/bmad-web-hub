import uuid
from datetime import datetime, timezone

from app.db import get_db
from app.models import SessionCreate, SessionResponse, MessageResponse


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid() -> str:
    return str(uuid.uuid4())


async def create_session(data: SessionCreate) -> SessionResponse:
    db = await get_db()
    try:
        session_id = _uid()
        now = _now()
        title = data.title or data.skill_name.replace("bmad-", "").replace("-", " ").title()
        await db.execute(
            """INSERT INTO sessions (id, skill_name, title, created_by, created_at, updated_at, status)
               VALUES (?, ?, ?, ?, ?, ?, 'in_progress')""",
            (session_id, data.skill_name, title, data.created_by, now, now),
        )
        await db.commit()
        return SessionResponse(
            id=session_id,
            skill_name=data.skill_name,
            title=title,
            created_by=data.created_by,
            created_at=now,
            updated_at=now,
            status="in_progress",
        )
    finally:
        await db.close()


async def list_sessions(status: str | None = None, skill_name: str | None = None) -> list[SessionResponse]:
    db = await get_db()
    try:
        query = """
            SELECT s.*, COUNT(m.id) as message_count
            FROM sessions s LEFT JOIN messages m ON s.id = m.session_id
        """
        params = []
        conditions = []
        if status:
            conditions.append("s.status = ?")
            params.append(status)
        if skill_name:
            conditions.append("s.skill_name = ?")
            params.append(skill_name)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " GROUP BY s.id ORDER BY s.updated_at DESC"

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [SessionResponse(**dict(row)) for row in rows]
    finally:
        await db.close()


async def get_session(session_id: str) -> SessionResponse | None:
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT s.*, COUNT(m.id) as message_count
               FROM sessions s LEFT JOIN messages m ON s.id = m.session_id
               WHERE s.id = ? GROUP BY s.id""",
            (session_id,),
        )
        row = await cursor.fetchone()
        return SessionResponse(**dict(row)) if row else None
    finally:
        await db.close()


async def update_session(session_id: str, **kwargs) -> None:
    db = await get_db()
    try:
        kwargs["updated_at"] = _now()
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [session_id]
        await db.execute(f"UPDATE sessions SET {sets} WHERE id = ?", values)
        await db.commit()
    finally:
        await db.close()


async def delete_session(session_id: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


async def add_message(session_id: str, role: str, content: str) -> MessageResponse:
    db = await get_db()
    try:
        msg_id = _uid()
        now = _now()
        await db.execute(
            "INSERT INTO messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (msg_id, session_id, role, content, now),
        )
        await db.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id)
        )
        await db.commit()
        return MessageResponse(
            id=msg_id, session_id=session_id, role=role, content=content, created_at=now
        )
    finally:
        await db.close()


async def get_messages(session_id: str) -> list[MessageResponse]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        )
        rows = await cursor.fetchall()
        return [MessageResponse(**dict(row)) for row in rows]
    finally:
        await db.close()
