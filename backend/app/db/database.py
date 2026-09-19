from __future__ import annotations

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.utils.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.db import models  # noqa: F401 ensures models are registered
    Base.metadata.create_all(bind=engine)
    # Lightweight, idempotent SQLite schema evolution. Do not delete existing history.
    if engine.dialect.name == "sqlite":
        required = {
            "health_label": "VARCHAR",
            "health_confidence": "FLOAT",
            "health_is_demo": "BOOLEAN DEFAULT 1",
            "health_top3_json": "TEXT",
        }
        current = {column["name"] for column in inspect(engine).get_columns("leaf_results")}
        with engine.begin() as connection:
            for name, definition in required.items():
                if name not in current:
                    connection.execute(text(f"ALTER TABLE leaf_results ADD COLUMN {name} {definition}"))
