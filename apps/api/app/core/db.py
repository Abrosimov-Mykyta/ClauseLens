from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


database_url = settings.database_url if settings.database_url_override else settings.local_database_url
engine_kwargs = {"future": True}

if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def ensure_runtime_schema() -> None:
    inspector = inspect(engine)
    if "document_chunks" not in inspector.get_table_names():
        return

    document_chunk_columns = {column["name"] for column in inspector.get_columns("document_chunks")}
    if "embedding_json" not in document_chunk_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE document_chunks ADD COLUMN embedding_json TEXT"))


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
