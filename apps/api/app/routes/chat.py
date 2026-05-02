from fastapi import APIRouter

from app.schemas.chat import ChatAnswer, ChatQuestion
from app.services.demo_store import answer_question

router = APIRouter(prefix="/workspaces/{workspace_id}/chat", tags=["chat"])


@router.post("", response_model=ChatAnswer)
def ask_question(workspace_id: str, payload: ChatQuestion) -> ChatAnswer:
    response = answer_question(workspace_id=workspace_id, question=payload.question)
    return ChatAnswer(**response)

