import pytest
from app.detectors import get_detector, detect_all
from app.detectors.base import BaseDetector, DetectionResult
from app.detectors.sensitive_info import SensitiveInfoDetector


class TestBaseDetector:
    def test_not_implemented(self):
        detector = BaseDetector()
        with pytest.raises(NotImplementedError):
            detector.detect("test")


class TestDetectorFactory:
    def test_get_sensitive_info_detector(self):
        detector = get_detector("sensitive_info")
        assert isinstance(detector, SensitiveInfoDetector)

    def test_get_unknown_detector(self):
        with pytest.raises(ValueError, match="未知"):
            get_detector("unknown")

    def test_detect_all(self):
        results = detect_all("sk-1234567890abcdef1234567890")
        assert "sensitive_info" in results
        assert isinstance(results["sensitive_info"], DetectionResult)


class TestSensitiveInfoDetector:
    def setup_method(self):
        self.detector = SensitiveInfoDetector()

    def test_openai_api_key(self):
        result = self.detector.detect("API密钥：sk-proj-abc123def456ghi789jkl")
        assert result.type == "sensitive_info"
        assert result.risk_level == "high"
        assert any(f["type"] == "api_key_openai" for f in result.details["findings"])

    def test_aws_key(self):
        result = self.detector.detect("AWS Key: AKIAIOSFODNN7EXAMPLE")
        assert any(f["type"] == "api_key_aws" for f in result.details["findings"])

    def test_github_token(self):
        result = self.detector.detect("token: ghp_" + "a" * 36)
        assert any(f["type"] == "api_key_github" for f in result.details["findings"])

    def test_jwt_token(self):
        result = self.detector.detect("Authorization: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyIn0.sig")
        assert any(f["type"] == "jwt_token" for f in result.details["findings"])

    def test_password_field(self):
        result = self.detector.detect("password=admin123")
        assert any(f["type"] == "password_field" for f in result.details["findings"])

    def test_email(self):
        result = self.detector.detect("联系邮箱：test@example.com")
        assert any(f["type"] == "email" for f in result.details["findings"])

    def test_phone_cn(self):
        result = self.detector.detect("手机号：13812345678")
        assert any(f["type"] == "phone_cn" for f in result.details["findings"])

    def test_id_card(self):
        result = self.detector.detect("身份证：110101199001011234")
        assert any(f["type"] == "id_card_cn" for f in result.details["findings"])

    def test_private_key(self):
        result = self.detector.detect("-----BEGIN RSA PRIVATE KEY-----")
        assert any(f["type"] == "private_key" for f in result.details["findings"])

    def test_no_sensitive_info(self):
        result = self.detector.detect("这是一段普通文本，没有敏感信息")
        assert result.risk_level == "safe"
        assert result.details["count"] == 0

    def test_multiple_findings(self):
        text = "密钥：sk-proj-abc123def456ghi789jkl 邮箱：test@example.com password=admin123"
        result = self.detector.detect(text)
        assert result.details["count"] >= 3

    def test_mask_api_key(self):
        result = self.detector.detect("sk-proj-abc123def456ghi789jkl")
        finding = result.details["findings"][0]
        masked = finding["masked_value"]
        assert "****" in masked
        assert masked.startswith("sk-proj")
        assert masked.endswith("jkl")

    def test_mask_email(self):
        result = self.detector.detect("test@example.com")
        finding = result.details["findings"][0]
        assert finding["masked_value"] == "t***@example.com"

    def test_mask_phone(self):
        result = self.detector.detect("13812345678")
        finding = result.details["findings"][0]
        assert finding["masked_value"] == "138****5678"

    def test_mask_password(self):
        result = self.detector.detect("password=admin123")
        finding = result.details["findings"][0]
        assert "******" in finding["masked_value"]

    def test_position_info(self):
        text = "key=sk-proj-abc123def456ghi789jkl end"
        result = self.detector.detect(text)
        finding = result.details["findings"][0]
        assert "start" in finding["position"]
        assert "end" in finding["position"]

    def test_suggestions_not_empty(self):
        result = self.detector.detect("sk-proj-abc123def456ghi789jkl")
        assert len(result.suggestions) > 0
