from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DetectionHistory(Base):
    __tablename__ = "detection_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    input_content_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    detection_type: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    result_detail_encrypted: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("idx_created_at", "created_at"),
        Index("idx_detection_type", "detection_type"),
    )
