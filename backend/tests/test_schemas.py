import pytest
from pydantic import ValidationError
from app.schemas.detection import (
    DetectionType,
    RiskLevel,
    DetectRequest,
    DetectResponse,
    HistoryItem,
    HistoryList,
    HistoryDetail,
)


class TestDetectionType:
    def test_valid_values(self):
        assert DetectionType.phishing == "phishing"
        assert DetectionType.weak_password == "weak_password"
        assert DetectionType.sensitive_info == "sensitive_info"

    def test_invalid_value(self):
        with pytest.raises(ValueError):
            DetectionType("invalid")


class TestRiskLevel:
    def test_valid_values(self):
        assert RiskLevel.high == "high"
        assert RiskLevel.medium == "medium"
        assert RiskLevel.low == "low"
        assert RiskLevel.safe == "safe"


class TestDetectRequest:
    def test_valid_with_type(self):
        req = DetectRequest(content="测试内容", detection_type=DetectionType.phishing)
        assert req.content == "测试内容"
        assert req.detection_type == DetectionType.phishing

    def test_valid_without_type(self):
        req = DetectRequest(content="测试内容")
        assert req.detection_type is None

    def test_empty_content_rejected(self):
        with pytest.raises(ValidationError):
            DetectRequest(content="")

    def test_missing_content_rejected(self):
        with pytest.raises(ValidationError):
            DetectRequest()

    def test_invalid_detection_type_rejected(self):
        with pytest.raises(ValidationError):
            DetectRequest(content="测试", detection_type="invalid")


class TestDetectResponse:
    def test_single_result(self):
        resp = DetectResponse(success=True, result={"type": "phishing"})
        assert resp.success is True
        assert resp.result is not None
        assert resp.results is None

    def test_all_results(self):
        resp = DetectResponse(success=True, results={"phishing": {}, "weak_password": {}})
        assert resp.results is not None
        assert resp.result is None


class TestHistoryItem:
    def test_create(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        item = HistoryItem(
            id=1,
            detection_type="phishing",
            risk_level="high",
            created_at=now,
        )
        assert item.id == 1
        assert item.detection_type == "phishing"
        assert "input_content" not in item.model_fields


class TestHistoryList:
    def test_create(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        item = HistoryItem(id=1, detection_type="all", risk_level="high", created_at=now)
        hist = HistoryList(items=[item], total=1, page=1, page_size=10)
        assert len(hist.items) == 1
        assert hist.total == 1


class TestHistoryDetail:
    def test_create(self):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        detail = HistoryDetail(
            id=1,
            input_content="解密后的内容",
            detection_type="phishing",
            risk_level="high",
            result_detail={"confidence": 0.85},
            created_at=now,
        )
        assert detail.input_content == "解密后的内容"
        assert detail.result_detail == {"confidence": 0.85}
