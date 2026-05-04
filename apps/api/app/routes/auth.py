from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.auth import AuthSessionResponse, LoginRequest, RegisterRequest
from app.services.auth import create_guest_session, login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthSessionResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthSessionResponse:
    try:
        response = register_user(
            db,
            full_name=payload.full_name,
            email=payload.email,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AuthSessionResponse(**response)


@router.post("/login", response_model=AuthSessionResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthSessionResponse:
    try:
        response = login_user(db, email=payload.email, password=payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return AuthSessionResponse(**response)


@router.post("/guest", response_model=AuthSessionResponse)
def guest_login(db: Session = Depends(get_db)) -> AuthSessionResponse:
    response = create_guest_session(db)
    return AuthSessionResponse(**response)
