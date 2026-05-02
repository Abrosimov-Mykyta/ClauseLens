from fastapi import FastAPI

from app.core.config import settings
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router
from app.routes.workspaces import router as workspaces_router

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(workspaces_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

