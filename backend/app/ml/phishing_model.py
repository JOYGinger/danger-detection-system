from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

MODEL_DIR = Path(__file__).resolve().parents[3] / "models"
TFIDF_PATH = MODEL_DIR / "phishing_tfidf.joblib"
RF_PATH = MODEL_DIR / "phishing_random_forest.joblib"
META_PATH = MODEL_DIR / "phishing_metadata.json"

LABEL_MAP = {
    "phishing email": 1,
    "phishing": 1,
    "spam": 1,
    "safe email": 0,
    "ham": 0,
    "legit": 0,
    "legitimate": 0,
    "not phishing": 0,
}


@dataclass
class HybridPrediction:
    label: str
    probability: float
    confidence: float
    features: Dict[str, float]
    source: str


class PhishingHybridModel:
    def __init__(self) -> None:
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.classifier: Optional[RandomForestClassifier] = None
        self.metadata: Dict[str, Any] = {}
        self._load_if_available()

    def _load_if_available(self) -> None:
        if TFIDF_PATH.exists() and RF_PATH.exists():
            self.vectorizer = joblib.load(TFIDF_PATH)
            self.classifier = joblib.load(RF_PATH)
        if META_PATH.exists():
            self.metadata = json.loads(META_PATH.read_text(encoding="utf-8"))

    def is_trained(self) -> bool:
        return self.vectorizer is not None and self.classifier is not None

    def predict(self, text: str) -> HybridPrediction:
        if not self.is_trained():
            return HybridPrediction(
                label="unknown",
                probability=0.0,
                confidence=0.0,
                features={},
                source="rule_fallback",
            )

        text = text or ""
        X = self.vectorizer.transform([text])
        proba = self.classifier.predict_proba(X)[0]
        classes = list(self.classifier.classes_)
        phishing_index = classes.index(1) if 1 in classes else int(max(range(len(classes)), key=lambda idx: classes[idx]))
        phishing_probability = float(proba[phishing_index])
        label = "phishing" if phishing_probability >= 0.5 else "safe"
        confidence = max(phishing_probability, 1 - phishing_probability)
        return HybridPrediction(
            label=label,
            probability=phishing_probability,
            confidence=round(confidence, 4),
            features=self._extract_rule_features(text),
            source="random_forest",
        )

    def train_from_dataframe(self, df: pd.DataFrame, text_col: str, label_col: str) -> Dict[str, Any]:
        cleaned = df[[text_col, label_col]].dropna().copy()
        cleaned[text_col] = cleaned[text_col].astype(str)
        cleaned[label_col] = cleaned[label_col].map(self._normalize_label)
        cleaned = cleaned.dropna()
        cleaned[label_col] = cleaned[label_col].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            cleaned[text_col], cleaned[label_col], test_size=0.2, random_state=42, stratify=cleaned[label_col]
        )

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=5000,
            token_pattern=r"(?u)\b\w+\b",
        )
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        self.classifier = RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        )
        self.classifier.fit(X_train_vec, y_train)

        preds = self.classifier.predict(X_test_vec)
        metrics = {
            "accuracy": float(accuracy_score(y_test, preds)),
            "precision": float(precision_score(y_test, preds, zero_division=0)),
            "recall": float(recall_score(y_test, preds, zero_division=0)),
            "f1": float(f1_score(y_test, preds, zero_division=0)),
            "samples": int(len(cleaned)),
        }
        self.metadata = metrics
        return metrics

    def save(self) -> None:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        if self.vectorizer is None or self.classifier is None:
            raise RuntimeError("模型尚未训练")
        joblib.dump(self.vectorizer, TFIDF_PATH)
        joblib.dump(self.classifier, RF_PATH)
        META_PATH.write_text(json.dumps(self.metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    def _normalize_label(self, value: Any) -> Optional[int]:
        if pd.isna(value):
            return None
        if isinstance(value, (int, np.integer)):
            return int(value)
        text = str(value).strip().lower()
        if text in LABEL_MAP:
            return LABEL_MAP[text]
        if text in {"1", "true", "yes", "phish", "malicious", "phishing email"}:
            return 1
        if text in {"0", "false", "no", "safe", "ham", "safe email"}:
            return 0
        return None

    def _extract_rule_features(self, text: str) -> Dict[str, float]:
        patterns = {
            "has_url": r"https?://|www\\.",
            "has_urgency": r"立即|紧急|马上|限时|expire|urgent|verify",
            "has_threat": r"冻结|封禁|锁定|suspend|locked|risk",
            "has_action": r"点击|login|sign in|confirm|verify|reset|update",
            "has_money": r"\$|人民币|美元|refund|invoice|payment",
        }
        features = {name: float(bool(re.search(pattern, text, re.I))) for name, pattern in patterns.items()}
        features["url_count"] = float(len(re.findall(r"https?://|www\\.", text, re.I)))
        features["exclamation_count"] = float(text.count("!"))
        features["uppercase_ratio"] = float(sum(1 for c in text if c.isupper()) / max(len(text), 1))
        return features


def load_dataset(path: str) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        candidate = MODEL_DIR.parent / path
        if candidate.exists():
            csv_path = candidate
        else:
            data_candidate = MODEL_DIR.parent / "data" / csv_path.name
            if data_candidate.exists():
                csv_path = data_candidate
    df = pd.read_csv(csv_path)
    columns = {c.lower(): c for c in df.columns}
    text_col = columns.get("email text") or columns.get("text") or columns.get("content")
    label_col = columns.get("email type") or columns.get("label") or columns.get("class")
    if not text_col or not label_col:
        raise ValueError(f"无法识别数据列: {list(df.columns)}")
    return df[[text_col, label_col]].rename(columns={text_col: "text", label_col: "label"})


def train_model_from_csv(csv_path: str) -> Dict[str, Any]:
    df = load_dataset(csv_path)
    model = PhishingHybridModel()
    metrics = model.train_from_dataframe(df, text_col="text", label_col="label")
    model.save()
    return metrics
