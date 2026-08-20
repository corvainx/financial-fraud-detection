"""
Database Connection & Session Management.
Compatible with both SQLite (zero-config local) and MySQL (production/academic).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session and ensures closure after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initializes database tables.
    """
    import backend.app.models.transaction  # noqa: F401
    Base.metadata.create_all(bind=engine)
    db_type = settings.DATABASE_URL.split("://")[0].upper()
    print(f"[DB] Database initialized successfully ({db_type})")
