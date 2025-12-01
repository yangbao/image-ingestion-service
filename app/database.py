from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from contextlib import contextmanager
from .config import settings

# ORM Base
Base = declarative_base()

# 初始化 Engine
engine = create_engine(
    settings.DATABASE_URL,
    # SQLite 特有参数，PostgreSQL 不需要
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

def init_db(engine=engine):
    """Create a database table structure (if it does not exist)"""
    #Must import models.py first to ensure model registration to Base
    from . import models
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Session:
    """
    Database session dependency.
    Use contextmanager to ensure that the session closes correctly at the end of the request.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db  # <-- 此时 yield 的 db 就是 Session 实例
    finally:
        db.close()