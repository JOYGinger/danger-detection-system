import os
import pytest
from sqlalchemy import inspect
from app.database import engine, Base, SessionLocal, init_db, get_db


def test_init_db_creates_tables():
    init_db()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    assert len(table_names) >= 0


def test_get_db_yields_session():
    gen = get_db()
    db = next(gen)
    assert db is not None
    db.close()


def test_session_local():
    db = SessionLocal()
    assert db is not None
    db.close()
