from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import User
from app.services.auth import get_user_by_access_token


@dataclass
class CurrentViewer:
    user: User
    mode: str
    access_token: str


def get_current_viewer(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> CurrentViewer:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    access_token = authorization.removeprefix("Bearer ").strip()
    viewer = get_user_by_access_token(db, access_token)
    if viewer is None:
        raise HTTPException(status_code=401, detail="Invalid session")

    user, auth_session = viewer
    return CurrentViewer(user=user, mode=auth_session.mode, access_token=auth_session.access_token)
