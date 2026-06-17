import pytest
from sqlalchemy import inspect
from app.database import engine, Base, init_db, SessionLocal
import app.models


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)


def test_detection_history_table_created():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "detection_history" in tables


def test_detection_history_columns():
    inspector = inspect(engine)
    columns = {col["name"]: col for col in inspector.get_columns("detection_history")}
    assert "id" in columns
    assert "input_content_encrypted" in columns
    assert "detection_type" in columns
    assert "risk_level" in columns
    assert "result_detail_encrypted" in columns
    assert "created_at" in columns


def test_detection_history_column_types():
    inspector = inspect(engine)
    columns = {col["name"]: col for col in inspector.get_columns("detection_history")}
    assert columns["id"]["primary_key"] == 1
    assert columns["input_content_encrypted"]["nullable"] is False
    assert columns["detection_type"]["nullable"] is False
    assert columns["risk_level"]["nullable"] is False
    assert columns["result_detail_encrypted"]["nullable"] is True


def test_detection_history_indexes():
    inspector = inspect(engine)
    indexes = inspector.get_indexes("detection_history")
    index_names = [idx["name"] for idx in indexes]
    assert "idx_created_at" in index_names
    assert "idx_detection_type" in index_names


def test_insert_and_query():
    from app.models.detection import DetectionHistory
    db = SessionLocal()
    record = DetectionHistory(
        input_content_encrypted="encrypted_content",
        detection_type="phishing",
        risk_level="high",
        result_detail_encrypted="encrypted_result",
    )
    db.add(record)
    db.commit()
    result = db.query(DetectionHistory).first()
    assert result is not None
    assert result.input_content_encrypted == "encrypted_content"
    assert result.detection_type == "phishing"
    assert result.risk_level == "high"
    assert result.created_at is not None
    db.close()
