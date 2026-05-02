from pydantic import BaseModel


class AuditEvent(BaseModel):
    id: str
    event_type: str
    message: str
    created_at: str

