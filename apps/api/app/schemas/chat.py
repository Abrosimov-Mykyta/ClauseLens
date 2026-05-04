from pydantic import BaseModel


class ChatQuestion(BaseModel):
    question: str


class ChatEvidenceItem(BaseModel):
    citation: str
    label: str
    content_preview: str


class ChatAnswer(BaseModel):
    answer: str
    citations: list[str]
    evidence: list[ChatEvidenceItem]


class ChatHistoryMessage(BaseModel):
    id: str
    role: str
    content: str
    citations: list[str]
    created_at: str
