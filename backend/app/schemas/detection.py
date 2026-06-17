from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DetectionType(str, Enum):
    phishing = "phishing"
    weak_password = "weak_password"
    sensitive_info = "sensitive_info"


class RiskLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    safe = "safe"


class DetectRequest(BaseModel):
    content: str = Field(..., min_length=1, description="要检测的文本内容")
    detection_type: Optional[DetectionType] = Field(
        None, description="检测类型，不指定则运行全部检测"
    )


class DetectResponse(BaseModel):
    success: bool
    result: Optional[dict] = Field(None, description="单类型检测结果")
    results: Optional[dict] = Field(None, description="全部检测结果（detection_type为空时）")


class HistoryItem(BaseModel):
    id: int
    detection_type: str
    risk_level: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryList(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    page_size: int


class HistoryDetail(BaseModel):
    id: int
    input_content: str = Field(..., description="解密后的输入内容")
    detection_type: str
    risk_level: str
    result_detail: dict = Field(..., description="解密后的检测结果")
    created_at: datetime

    model_config = {"from_attributes": True}
