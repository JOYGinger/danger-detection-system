from __future__ import annotations

import math
from typing import Dict, List

from app.detectors.base import BaseDetector, DetectionResult

try:
    from zxcvbn import zxcvbn
except ImportError:  # pragma: no cover - fallback only used when dependency missing
    zxcvbn = None


class WeakPasswordDetector(BaseDetector):
    """弱密码检测器：优先使用 zxcvbn，缺失时降级为规则评分。"""

    def detect(self, content: str) -> DetectionResult:
        password = content or ""
        if not password:
            return DetectionResult(
                type="weak_password",
                risk_level="safe",
                confidence=1.0,
                details={
                    "score": 0,
                    "entropy": 0.0,
                    "crack_time": "立即",
                    "feedback": ["密码为空"],
                },
                suggestions=["请输入有效密码进行检测"],
            )

        if zxcvbn is not None:
            analysis = zxcvbn(password)
            score = int(analysis.get("score", 0))
            risk_level = self._risk_level_from_score(score)
            entropy = float(analysis.get("guesses_log10", 0.0) * math.log2(10))
            crack_time = self._extract_crack_time(analysis)
            feedback = self._extract_feedback(analysis)
            suggestions = self._build_suggestions(score, feedback)
            details = {
                "score": score,
                "entropy": round(entropy, 2),
                "crack_time": crack_time,
                "feedback": feedback,
                "sequence_count": len(analysis.get("sequence", [])),
            }
            confidence = 0.95 if score >= 3 else 0.9 if score == 2 else 0.85
            return DetectionResult(
                type="weak_password",
                risk_level=risk_level,
                confidence=confidence,
                details=details,
                suggestions=suggestions,
            )

        return self._fallback_detect(password)

    def _fallback_detect(self, password: str) -> DetectionResult:
        length = len(password)
        categories = sum(
            [
                any(c.islower() for c in password),
                any(c.isupper() for c in password),
                any(c.isdigit() for c in password),
                any(not c.isalnum() for c in password),
            ]
        )
        score = 0
        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if categories >= 3:
            score += 1
        if categories == 4:
            score += 1
        score = min(score, 4)
        risk_level = self._risk_level_from_score(score)
        details = {
            "score": score,
            "entropy": round(length * max(categories, 1), 2),
            "crack_time": "未知",
            "feedback": ["未安装 zxcvbn，已使用规则评分"],
        }
        return DetectionResult(
            type="weak_password",
            risk_level=risk_level,
            confidence=0.6,
            details=details,
            suggestions=self._build_suggestions(score, details["feedback"]),
        )

    def _risk_level_from_score(self, score: int) -> str:
        return ["high", "high", "medium", "low", "safe"][max(0, min(score, 4))]

    def _extract_crack_time(self, analysis: Dict) -> str:
        times = analysis.get("crack_times_display", {})
        return (
            times.get("offline_slow_hashing_1e4_per_second")
            or times.get("online_throttling_100_per_hour")
            or "未知"
        )

    def _extract_feedback(self, analysis: Dict) -> List[str]:
        feedback = analysis.get("feedback", {}) or {}
        items = list(feedback.get("warning") and [feedback["warning"]] or [])
        items.extend(feedback.get("suggestions", []) or [])
        return [item for item in items if item]

    def _build_suggestions(self, score: int, feedback: List[str]) -> List[str]:
        suggestions = ["避免使用常见密码或重复密码"]
        if score <= 1:
            suggestions.append("建议长度不少于 12 位，并混合大小写字母、数字和特殊字符")
        elif score == 2:
            suggestions.append("建议进一步增加随机性，减少可预测模式")
        else:
            suggestions.append("建议继续使用密码管理器生成和保存强密码")
        for item in feedback:
            if item and item not in suggestions:
                suggestions.append(item)
        return suggestions
