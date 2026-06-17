import re
from typing import List, Dict

from app.detectors.base import BaseDetector, DetectionResult


class SensitiveInfoDetector(BaseDetector):
    """敏感信息检测器：正则+规则引擎，参考earlybird设计"""

    # 检测规则：优先级、类型标签、中文名、正则、风险等级、掩码方式
    RULES: List[Dict] = [
        # P0 - 密钥类
        {
            "label": "api_key_openai",
            "display": "OpenAI API密钥",
            "pattern": r"sk-[a-zA-Z0-9_-]{20,}",
            "risk": "high",
            "mask": "api_key",
        },
        {
            "label": "api_key_aws",
            "display": "AWS访问密钥",
            "pattern": r"AKIA[0-9A-Z]{16}",
            "risk": "high",
            "mask": "api_key",
        },
        {
            "label": "api_key_github",
            "display": "GitHub Token",
            "pattern": r"ghp_[a-zA-Z0-9]{36}",
            "risk": "high",
            "mask": "api_key",
        },
        {
            "label": "api_key_google",
            "display": "Google API密钥",
            "pattern": r"AIza[0-9A-Za-z-_]{35}",
            "risk": "high",
            "mask": "api_key",
        },
        {
            "label": "api_key_stripe",
            "display": "Stripe密钥",
            "pattern": r"sk_live_[0-9a-zA-Z]{24}",
            "risk": "high",
            "mask": "api_key",
        },
        {
            "label": "jwt_token",
            "display": "JWT Token",
            "pattern": r"eyJ[a-zA-Z0-9-_]+\.",
            "risk": "high",
            "mask": "token",
        },
        {
            "label": "password_field",
            "display": "密码字段",
            "pattern": r"(?:password|passwd|pwd)\s*[=:]\s*\S+",
            "risk": "high",
            "mask": "password",
        },
        # P1 - 个人信息
        {
            "label": "email",
            "display": "邮箱地址",
            "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "risk": "medium",
            "mask": "email",
        },
        {
            "label": "phone_cn",
            "display": "手机号(中国)",
            "pattern": r"1[3-9]\d{9}",
            "risk": "medium",
            "mask": "phone",
        },
        # P2 - 证件类
        {
            "label": "id_card_cn",
            "display": "身份证号",
            "pattern": r"[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]",
            "risk": "high",
            "mask": "id_card",
        },
        {
            "label": "private_key",
            "display": "私钥文件",
            "pattern": r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
            "risk": "high",
            "mask": "key_file",
        },
    ]

    def detect(self, content: str) -> DetectionResult:
        findings = []
        for rule in self.RULES:
            for match in re.finditer(rule["pattern"], content):
                value = match.group()
                findings.append({
                    "type": rule["label"],
                    "label": rule["display"],
                    "masked_value": self._mask(value, rule["mask"]),
                    "position": {"start": match.start(), "end": match.end()},
                    "risk": rule["risk"],
                })

        if not findings:
            return DetectionResult(
                type="sensitive_info",
                risk_level="safe",
                confidence=1.0,
                details={"findings": [], "count": 0},
                suggestions=["未检测到敏感信息"],
            )

        risk_level = self._compute_risk(findings)
        suggestions = self._generate_suggestions(findings)

        return DetectionResult(
            type="sensitive_info",
            risk_level=risk_level,
            confidence=0.95,
            details={"findings": findings, "count": len(findings)},
            suggestions=suggestions,
        )

    def _mask(self, value: str, mask_type: str) -> str:
        if mask_type == "api_key":
            if len(value) <= 10:
                return "*" * len(value)
            return f"{value[:7]}****{value[-3:]}"
        elif mask_type == "token":
            if len(value) <= 10:
                return "*" * len(value)
            return f"{value[:6]}****"
        elif mask_type == "password":
            return re.sub(r"([=:]\s*)\S+", r"\1******", value)
        elif mask_type == "email":
            parts = value.split("@")
            if len(parts) != 2:
                return "***@***.***"
            return f"{parts[0][0]}***@{parts[1]}"
        elif mask_type == "phone":
            if len(value) == 11:
                return f"{value[:3]}****{value[7:]}"
            return "***-****-****"
        elif mask_type == "id_card":
            if len(value) == 18:
                return f"{value[:6]}********{value[-4:]}"
            return "*" * len(value)
        elif mask_type == "key_file":
            return "-----BEGIN **** PRIVATE KEY-----"
        return "*" * len(value)

    def _compute_risk(self, findings: List[Dict]) -> str:
        risks = {f["risk"] for f in findings}
        if "high" in risks:
            return "high"
        if "medium" in risks:
            return "medium"
        return "low"

    def _generate_suggestions(self, findings: List[Dict]) -> List[str]:
        suggestions = []
        labels = {f["label"] for f in findings}
        if labels & {"OpenAI API密钥", "AWS访问密钥", "GitHub Token", "Google API密钥", "Stripe密钥"}:
            suggestions.append("使用环境变量代替硬编码密钥")
            suggestions.append("敏感信息不应提交到版本控制系统")
        if "密码字段" in labels:
            suggestions.append("避免在代码中硬编码密码，使用配置文件或密钥管理服务")
        if "JWT Token" in labels:
            suggestions.append("JWT令牌应存储在安全位置，不要在URL或日志中暴露")
        if labels & {"邮箱地址", "手机号(中国)", "身份证号"}:
            suggestions.append("个人身份信息(PII)应加密存储，展示时进行掩码处理")
        if "私钥文件" in labels:
            suggestions.append("私钥文件应设置严格权限，不要提交到代码仓库")
        if not suggestions:
            suggestions.append("检测到潜在敏感信息，请确认是否需要保护")
        return suggestions
