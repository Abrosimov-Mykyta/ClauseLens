from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.bootstrap import seed_database
from app.core.config import settings
from app.core.db import Base, SessionLocal, engine, ensure_runtime_schema
from app.models import AuditLog, AnalysisRun, ChatMessage, ChatSession, Document, DocumentChunk, User, Workspace, WorkspaceMember
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router
from app.routes.workspaces import router as workspaces_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_runtime_schema()
    with SessionLocal() as session:
        seed_database(session)


app.include_router(health_router)
app.include_router(auth_router, prefix="/api")
app.include_router(workspaces_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
