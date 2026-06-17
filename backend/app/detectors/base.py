from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DetectionResult:
    type: str
    risk_level: str
    confidence: float
    details: Dict = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)


class BaseDetector:
    def detect(self, content: str) -> DetectionResult:
        raise NotImplementedError
