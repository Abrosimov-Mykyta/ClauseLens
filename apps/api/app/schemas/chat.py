from pydantic import BaseModel


class ChatQuestion(BaseModel):
    question: str


class ChatAnswer(BaseModel):
    answer: str
    citations: list[str]


class ChatHistoryMessage(BaseModel):
    id: str
    role: str
    content: str
    citations: list[str]
    created_at: str
