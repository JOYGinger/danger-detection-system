import re
from collections import Counter
from typing import Dict, List
from urllib.parse import urlparse

from app.detectors.base import BaseDetector, DetectionResult
from app.ml.phishing_model import PhishingHybridModel


class PhishingEmailDetector(BaseDetector):
    """钓鱼邮件检测器：规则引擎 + 机器学习混合方案。"""

    def __init__(self) -> None:
        self.hybrid_model = PhishingHybridModel()

    URGENCY_WORDS = [
        "立即",
        "紧急",
        "马上",
        "尽快",
        "限时",
        "最后机会",
        "今日截止",
        "即将过期",
        "24小时",
        "账户将被",
        "验证失败",
    ]

    THREAT_WORDS = [
        "冻结",
        "封禁",
        "异常",
        "风险",
        "安全",
        "验证",
        "锁定",
        "暂停",
        "停止服务",
        "违规",
        "未验证",
    ]

    LURE_WORDS = [
        "点击",
        "链接",
        "验证身份",
        "确认信息",
        "领取奖励",
        "免费",
        "优惠",
        "中奖",
        "登录",
        "重新登录",
        "查看详情",
    ]

    DISGUISE_WORDS = [
        "官方",
        "客服",
        "银行",
        "支付宝",
        "微信支付",
        "淘宝",
        "京东",
        "税务局",
        "公安局",
        "Microsoft",
        "Google",
        "Apple",
        "PayPal",
    ]

    SUSPICIOUS_DOMAINS = [
        "bit.ly",
        "t.co",
        "tinyurl.com",
        "goo.su",
        "rebrand.ly",
        "cutt.ly",
    ]

    def detect(self, content: str) -> DetectionResult:
        text = content or ""
        urls = re.findall(r"https?://[^\s<>()\"]+|www\.[^\s<>()\"]+", text)
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        findings: List[Dict] = []
        signals = Counter()

        for word in self.URGENCY_WORDS:
            if word in text:
                signals["urgency"] += 1
                findings.append({"type": "urgency_language", "keyword": word})

        for word in self.THREAT_WORDS:
            if word in text:
                signals["threat"] += 1
                findings.append({"type": "threat_language", "keyword": word})

        for word in self.LURE_WORDS:
            if word in text:
                signals["lure"] += 1
                findings.append({"type": "lure_language", "keyword": word})

        for word in self.DISGUISE_WORDS:
            if word.lower() in text.lower():
                signals["disguise"] += 1
                findings.append({"type": "brand_impersonation", "keyword": word})

        if urls:
            signals["urls"] = len(urls)
            for url in urls:
                parsed = urlparse(url if url.startswith("http") else f"http://{url}")
                hostname = parsed.hostname or url
                findings.append({"type": "url", "value": url, "hostname": hostname})
                if any(domain in hostname.lower() for domain in self.SUSPICIOUS_DOMAINS):
                    signals["short_url"] += 1
                    findings.append({"type": "shortened_url", "value": url})
                if hostname.count("-") >= 3 or hostname.count(".") >= 4:
                    signals["suspicious_domain"] += 1
                    findings.append({"type": "suspicious_domain", "value": hostname})

        if emails:
            signals["emails"] = len(emails)

        if re.search(r"(?:verify|validation|confirm|login|signin|reset).*?(?:account|password|credential)", text, re.I):
            signals["credential_theft"] += 1
            findings.append({"type": "credential_theft", "pattern": "credential_request"})

        if re.search(r"(?:attachment|附件|invoice|receipt|document|合同|发票)", text, re.I):
            signals["attachment_bait"] += 1
            findings.append({"type": "attachment_bait", "pattern": "attachment_bait"})

        score = (
            signals["urgency"] * 2
            + signals["threat"] * 2
            + signals["lure"]
            + signals["disguise"] * 2
            + signals["short_url"] * 2
            + signals["suspicious_domain"] * 2
            + signals["credential_theft"] * 3
            + signals["attachment_bait"]
        )

        ml_prediction = self.hybrid_model.predict(text)
        ml_score = 0
        if ml_prediction.label == "phishing":
            ml_score = int(round(ml_prediction.probability * 5))
        elif ml_prediction.source == "random_forest":
            ml_score = int(round(max(0.0, ml_prediction.probability - 0.5) * 4))

        combined_score = score + ml_score

        if combined_score >= 8:
            risk_level = "high"
        elif combined_score >= 4:
            risk_level = "medium"
        elif combined_score > 0:
            risk_level = "low"
        else:
            risk_level = "safe"

        if ml_prediction.source == "random_forest":
            confidence = max(ml_prediction.confidence, min(0.95, 0.5 + combined_score * 0.08))
        else:
            confidence = min(0.95, 0.5 + combined_score * 0.08) if combined_score else 0.92

        suggestions = self._build_suggestions(signals, urls, emails)
        if ml_prediction.source == "random_forest" and ml_prediction.label == "phishing":
            suggestions.insert(0, "机器学习模型判定为钓鱼邮件，建议优先拦截并复核")

        details = {
            "signals": dict(signals),
            "findings": findings,
            "url_count": len(urls),
            "email_count": len(emails),
            "rule_score": score,
            "ml_prediction": {
                "label": ml_prediction.label,
                "probability": ml_prediction.probability,
                "confidence": ml_prediction.confidence,
                "source": ml_prediction.source,
                "features": ml_prediction.features,
            },
            "combined_score": combined_score,
        }

        return DetectionResult(
            type="phishing",
            risk_level=risk_level,
            confidence=round(confidence, 2),
            details=details,
            suggestions=suggestions,
        )

    def _build_suggestions(self, signals: Counter, urls: List[str], emails: List[str]) -> List[str]:
        suggestions: List[str] = []
        if signals["urgency"] or signals["threat"]:
            suggestions.append("邮件包含紧迫或威胁性措辞，请核实发送方身份")
        if signals["credential_theft"]:
            suggestions.append("不要通过邮件中的链接输入账号、密码或验证码")
        if urls:
            suggestions.append("检查链接域名是否与官方域名一致，避免点击可疑短链")
        if signals["disguise"]:
            suggestions.append("确认邮件是否冒充品牌、银行、客服或政府机构")
        if emails:
            suggestions.append("核对发件人邮箱地址与正文中的联系方式是否一致")
        if not suggestions:
            suggestions.append("未发现明显钓鱼特征，但仍建议核实发件来源与链接安全性")
        return suggestions
