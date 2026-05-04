import hashlib
import hmac
import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuthSession, User
from app.services.persistence import create_workspace


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"{salt}${derived_key.hex()}"


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash or "$" not in password_hash:
        return False

    salt, stored_hash = password_hash.split("$", 1)
    candidate_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    ).hex()
    return hmac.compare_digest(candidate_hash, stored_hash)


def _create_auth_session(session: Session, user: User, *, mode: str) -> AuthSession:
    auth_session = AuthSession(
        user_id=user.id,
        mode=mode,
        access_token=secrets.token_urlsafe(32),
    )
    session.add(auth_session)
    session.commit()
    session.refresh(auth_session)
    return auth_session


def get_user_by_access_token(session: Session, access_token: str) -> tuple[User, AuthSession] | None:
    auth_session = session.scalar(select(AuthSession).where(AuthSession.access_token == access_token))
    if auth_session is None:
        return None

    user = session.scalar(select(User).where(User.id == auth_session.user_id))
    if user is None:
        return None

    return user, auth_session


def register_user(
    session: Session,
    *,
    full_name: str,
    email: str,
    password: str,
) -> dict[str, str]:
    normalized_email = email.strip().lower()
    existing_user = session.scalar(select(User).where(User.email == normalized_email))
    if existing_user is not None:
        raise ValueError("An account with this email already exists")

    user = User(
        full_name=full_name.strip(),
        email=normalized_email,
        password_hash=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    auth_session = _create_auth_session(session, user, mode="member")
    return {
        "access_token": auth_session.access_token,
        "mode": "member",
        "display_name": user.full_name,
        "email": user.email,
    }


def login_user(session: Session, *, email: str, password: str) -> dict[str, str]:
    normalized_email = email.strip().lower()
    user = session.scalar(select(User).where(User.email == normalized_email))
    if user is None or not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")

    auth_session = _create_auth_session(session, user, mode="member")
    return {
        "access_token": auth_session.access_token,
        "mode": "member",
        "display_name": user.full_name,
        "email": user.email,
    }


def create_guest_session(session: Session) -> dict[str, str]:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    suffix = secrets.token_hex(3)
    user = User(
        full_name="Guest Reviewer",
        email=f"guest-{timestamp}-{suffix}@clauselens.local",
        password_hash=None,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    auth_session = _create_auth_session(session, user, mode="guest")
    create_workspace(
        session,
        actor=user,
        name="Guest Sandbox Review",
        description="A private starter workspace for exploring uploads, evidence views, and AI Q&A.",
    )
    return {
        "access_token": auth_session.access_token,
        "mode": "guest",
        "display_name": user.full_name,
        "email": user.email,
    }
