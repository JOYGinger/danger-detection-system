import json
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.detection import DetectionHistory
from app.schemas.detection import HistoryList, HistoryDetail
from app.services import history as history_service
from app.utils.crypto import generate_key


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestSession()
    yield db
    db.close()


_TEST_KEY = generate_key()


@pytest.fixture(autouse=True)
def set_encryption_key():
    os.environ["ENCRYPTION_KEY"] = _TEST_KEY
    history_service._encryptor = None
    yield
    if "ENCRYPTION_KEY" in os.environ:
        del os.environ["ENCRYPTION_KEY"]
    history_service._encryptor = None


class TestSaveHistory:
    def test_save_history_basic(self, db_session):
        record = history_service.save_history(
            db_session,
            content="sk-proj-abc123",
            detection_type="sensitive_info",
            risk_level="high",
            result_detail={"count": 1},
        )
        assert record.id is not None
        assert record.detection_type == "sensitive_info"
        assert record.risk_level == "high"
        assert record.input_content_encrypted != "sk-proj-abc123"
        assert record.result_detail_encrypted is not None

    def test_save_history_encrypts_content(self, db_session):
        record = history_service.save_history(
            db_session,
            content="敏感内容test",
            detection_type="sensitive_info",
            risk_level="medium",
            result_detail={"key": "value"},
        )
        raw = db_session.query(DetectionHistory).filter(DetectionHistory.id == record.id).first()
        assert raw.input_content_encrypted != "敏感内容test"
        assert "敏感" not in raw.input_content_encrypted

    def test_save_history_encrypts_result(self, db_session):
        result = {"type": "sensitive_info", "findings": [{"masked": "sk-***"}]}
        record = history_service.save_history(
            db_session,
            content="test",
            detection_type="sensitive_info",
            risk_level="high",
            result_detail=result,
        )
        raw = db_session.query(DetectionHistory).filter(DetectionHistory.id == record.id).first()
        assert "sensitive_info" not in raw.result_detail_encrypted


class TestGetHistoryList:
    def test_empty_list(self, db_session):
        result = history_service.get_history_list(db_session)
        assert result.total == 0
        assert result.items == []
        assert result.page == 1

    def test_pagination(self, db_session):
        for i in range(15):
            history_service.save_history(
                db_session,
                content=f"content_{i}",
                detection_type="sensitive_info",
                risk_level="high",
                result_detail={"index": i},
            )
        page1 = history_service.get_history_list(db_session, page=1, page_size=10)
        assert len(page1.items) == 10
        assert page1.total == 15
        assert page1.page == 1
        assert page1.page_size == 10

        page2 = history_service.get_history_list(db_session, page=2, page_size=10)
        assert len(page2.items) == 5
        assert page2.page == 2

    def test_list_ordered_by_created_at_desc(self, db_session):
        history_service.save_history(
            db_session, content="first", detection_type="sensitive_info",
            risk_level="low", result_detail={},
        )
        history_service.save_history(
            db_session, content="second", detection_type="sensitive_info",
            risk_level="high", result_detail={},
        )
        result = history_service.get_history_list(db_session)
        assert result.items[0].risk_level == "high"
        assert result.items[1].risk_level == "low"

    def test_list_does_not_contain_sensitive_fields(self, db_session):
        history_service.save_history(
            db_session, content="secret content", detection_type="sensitive_info",
            risk_level="high", result_detail={"secret": "data"},
        )
        result = history_service.get_history_list(db_session)
        item = result.items[0]
        assert not hasattr(item, "input_content")
        assert not hasattr(item, "result_detail")
        assert item.detection_type == "sensitive_info"
        assert item.risk_level == "high"


class TestGetHistoryDetail:
    def test_get_existing_detail(self, db_session):
        history_service.save_history(
            db_session, content="test content 中文", detection_type="sensitive_info",
            risk_level="high", result_detail={"count": 2, "findings": ["a"]},
        )
        record = db_session.query(DetectionHistory).first()
        detail = history_service.get_history_detail(db_session, record.id)
        assert detail is not None
        assert detail.input_content == "test content 中文"
        assert detail.result_detail["count"] == 2
        assert detail.detection_type == "sensitive_info"
        assert detail.risk_level == "high"

    def test_get_nonexistent_detail(self, db_session):
        detail = history_service.get_history_detail(db_session, 9999)
        assert detail is None


class TestDeleteHistory:
    def test_delete_existing(self, db_session):
        history_service.save_history(
            db_session, content="to delete", detection_type="sensitive_info",
            risk_level="medium", result_detail={},
        )
        record = db_session.query(DetectionHistory).first()
        result = history_service.delete_history(db_session, record.id)
        assert result is True
        assert db_session.query(DetectionHistory).count() == 0

    def test_delete_nonexistent(self, db_session):
        result = history_service.delete_history(db_session, 9999)
        assert result is False


class TestClearHistory:
    def test_clear_all(self, db_session):
        for i in range(5):
            history_service.save_history(
                db_session, content=f"content_{i}", detection_type="sensitive_info",
                risk_level="low", result_detail={},
            )
        count = history_service.clear_history(db_session)
        assert count == 5
        assert db_session.query(DetectionHistory).count() == 0

    def test_clear_empty(self, db_session):
        count = history_service.clear_history(db_session)
        assert count == 0
