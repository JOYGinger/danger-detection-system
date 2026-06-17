from typing import Dict

from app.detectors.base import BaseDetector, DetectionResult
from app.detectors.phishing_email import PhishingEmailDetector
from app.detectors.sensitive_info import SensitiveInfoDetector
from app.detectors.weak_password import WeakPasswordDetector

_DETECTORS: Dict[str, type] = {
    "phishing": PhishingEmailDetector,
    "weak_password": WeakPasswordDetector,
    "sensitive_info": SensitiveInfoDetector,
}


def get_detector(detection_type: str) -> BaseDetector:
    cls = _DETECTORS.get(detection_type)
    if cls is None:
        raise ValueError(f"未知的检测类型: {detection_type}")
    return cls()


def detect_all(content: str) -> Dict[str, DetectionResult]:
    results = {}
    for name, cls in _DETECTORS.items():
        results[name] = cls().detect(content)
    return results
