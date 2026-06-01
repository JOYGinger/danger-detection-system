import math
import re
from typing import Dict, List

from zxcvbn import zxcvbn

from app.detectors.base import BaseDetector, DetectionResult

SCORE_TO_RISK = ["high", "high", "medium", "low", "low"]

PATTERN_LABELS: Dict[str, str] = {
    "dictionary": "字典攻击",
    "spatial": "键盘连续模式",
    "repeat": "重复字符",
    "sequence": "连续序列",
    "date": "日期模式",
    "regex": "常见弱密码模式",
    "bruteforce": "暴力破解",
}

FEEDBACK_ZH: Dict[str, str] = {
    "This is a top-10 common password": "这是最常见的10个密码之一",
    "This is a top-100 common password": "这是最常见的100个密码之一",
    "This is a very common password": "这是非常常见的密码",
    "This is similar to a commonly used password": "与常见密码相似",
    "A word by itself is easy to guess": "单个词语容易被字典攻击猜中",
    "Names and surnames by themselves are easy to guess": "姓名单独使用容易被猜中",
    "Common names and surnames are easy to guess": "常见姓名容易被猜中",
    "Repeats like \"aaa\" are easy to guess": "重复字符（如 aaa）容易被猜中",
    "Repeats like \"abcabcabc\" are only slightly harder to guess than \"abc\"": "重复模式（如 abcabc）安全性很低",
    "Sequences like abc or 6543 are easy to guess": "连续序列（如 abc、6543）容易被猜中",
    "Recent years are easy to guess": "近期年份容易被猜中",
    "Dates are often easy to guess": "日期格式容易被猜中",
    "Straight rows of keys are easy to guess": "键盘连续按键（如 qwerty）容易被猜中",
    "Short keyboard patterns are easy to guess": "短键盘模式容易被猜中",
    "Use a few words, avoid common phrases": "使用多个不常见词语组合，避免常见短语",
    "No need for symbols, digits, or uppercase letters": "passphrase 长度足够时不必刻意添加符号",
    "Add another word or two. Uncommon words are better.": "增加更多不常见词语",
    "Capitalization doesn't help very much": "单纯大写变换对安全性提升有限",
    "All-uppercase is almost as easy to guess as all-lowercase": "全大写与全小写安全性相近",
    "Reversed words aren't much harder to guess": "反转单词并不比原词更难猜",
    "Predictable substitutions like '@' instead of 'a' don't help very much": "可预测的字符替换（如 @ 代替 a）效果有限",
}


class WeakPasswordDetector(BaseDetector):
    """弱密码检测器：zxcvbn-python 评估 + 密码学解读层"""

    def detect(self, content: str) -> DetectionResult:
        password = content.strip()

        if not password:
            return DetectionResult(
                type="weak_password",
                risk_level="safe",
                confidence=1.0,
                details={"skipped": True, "reason": "empty_input"},
                suggestions=["请输入待检测的密码"],
            )

        if not self._looks_like_password_input(content):
            return DetectionResult(
                type="weak_password",
                risk_level="safe",
                confidence=1.0,
                details={"skipped": True, "reason": "not_password_like"},
                suggestions=["弱密码检测请直接输入密码字符串，不适合长文本或多行内容"],
            )

        raw = zxcvbn(password)
        score = raw["score"]
        risk_level = SCORE_TO_RISK[score]
        confidence = (score + 1) / 5

        entropy_bits = round(raw["guesses_log10"] / math.log10(2), 1)
        crack_time = raw["crack_times_display"]["offline_slow_hashing_1e4_per_second"]
        feedback = self._build_feedback(raw)
        patterns = self._extract_patterns(raw)
        suggestions = self._generate_suggestions(password, score, raw, patterns)

        return DetectionResult(
            type="weak_password",
            risk_level=risk_level,
            confidence=confidence,
            details={
                "score": score,
                "score_max": 4,
                "entropy_bits": entropy_bits,
                "guesses": raw["guesses"],
                "crack_time": crack_time,
                "feedback": feedback,
                "patterns": patterns,
            },
            suggestions=suggestions,
        )

    def _looks_like_password_input(self, content: str) -> bool:
        if "\n" in content or "\r" in content:
            return False
        stripped = content.strip()
        return 4 <= len(stripped) <= 128

    def _build_feedback(self, raw: dict) -> List[str]:
        items: List[str] = []
        fb = raw.get("feedback", {})
        warning = fb.get("warning", "")
        if warning:
            items.append(FEEDBACK_ZH.get(warning, warning))
        for suggestion in fb.get("suggestions", []):
            items.append(FEEDBACK_ZH.get(suggestion, suggestion))
        return items

    def _extract_patterns(self, raw: dict) -> List[Dict]:
        patterns = []
        for item in raw.get("sequence", []):
            pattern_type = item.get("pattern", "unknown")
            token = item.get("token", "")
            patterns.append({
                "pattern": pattern_type,
                "label": PATTERN_LABELS.get(pattern_type, pattern_type),
                "token": token,
            })
        return patterns

    def _generate_suggestions(
        self, password: str, score: int, raw: dict, patterns: List[Dict]
    ) -> List[str]:
        suggestions = self._build_feedback(raw)

        pattern_types = {p["pattern"] for p in patterns}
        if "dictionary" in pattern_types:
            suggestions.append("避免使用字典词汇或常见密码，可改用随机 passphrase")
        if "spatial" in pattern_types:
            suggestions.append("避免键盘连续按键（如 qwerty、123456），此类模式在模式匹配攻击中极易被识别")
        if "repeat" in pattern_types:
            suggestions.append("避免重复字符模式，增加字符多样性可提升熵值")
        if "sequence" in pattern_types:
            suggestions.append("避免连续字母或数字序列（如 abc、1234）")
        if "date" in pattern_types:
            suggestions.append("避免在密码中使用生日等日期信息")

        if len(password) < 8:
            suggestions.append("NIST SP 800-63B 建议：用户自选密码至少 8 个字符")
        elif len(password) < 12:
            suggestions.append("建议密码长度达到 12 位以上，可显著增加暴力破解所需时间")

        if not re.search(r"[A-Z]", password):
            suggestions.append("添加大写字母以增加字符集大小")
        if not re.search(r"[0-9]", password):
            suggestions.append("添加数字以增加字符集大小")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?]", password):
            suggestions.append("添加特殊字符以扩大搜索空间")

        entropy_bits = round(raw["guesses_log10"] / math.log10(2), 1)
        suggestions.append(
            f"估算熵约 {entropy_bits} bits（基于攻击者猜测模型，非简单字符集熵）"
        )

        if score >= 3:
            suggestions.append("密码强度良好，请妥善保管，不要与他人共享或明文存储")
        elif score <= 1:
            suggestions.append("建议使用密码管理器生成随机强密码")

        seen = set()
        unique: List[str] = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        return unique[:8]
