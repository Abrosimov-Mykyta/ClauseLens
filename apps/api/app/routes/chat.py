from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.auth import CurrentViewer, get_current_viewer
from app.schemas.chat import ChatAnswer, ChatQuestion
from app.services.persistence import create_chat_exchange

router = APIRouter(prefix="/workspaces/{workspace_id}/chat", tags=["chat"])


@router.post("", response_model=ChatAnswer)
def ask_question(
    workspace_id: str,
    payload: ChatQuestion,
    db: Session = Depends(get_db),
    viewer: CurrentViewer = Depends(get_current_viewer),
) -> ChatAnswer:
    try:
        response = create_chat_exchange(db, workspace_id, payload.question, actor=viewer.user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ChatAnswer(**response)
