from pydantic import BaseModel, Field
from datetime import datetime


class SkillMeta(BaseModel):
    name: str
    display_name: str = ""
    description: str = ""
    description_ko: str = ""
    type: str = "skill"  # skill or agent
    icon: str = ""
    module: str = "core"
    role: str = ""
    capabilities: str = ""
    has_workflow: bool = False


class SessionCreate(BaseModel):
    skill_name: str
    title: str = ""
    created_by: str = "anonymous"


class SessionResponse(BaseModel):
    id: str
    type: str | None = None
    skill_name: str | None = None
    title: str | None = None
    created_by: str = "anonymous"
    created_at: str
    updated_at: str
    status: str = "in_progress"
    claude_session_id: str | None = None
    output_file: str | None = None
    message_count: int = 0


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: str


class WSIncoming(BaseModel):
    type: str  # user_message, cancel
    content: str = ""
