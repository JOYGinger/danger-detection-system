import json
from typing import Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.detection import DetectionHistory
from app.schemas.detection import HistoryItem, HistoryDetail, HistoryList
from app.utils.crypto import DataEncryptor

_encryptor: DataEncryptor | None = None


def _get_encryptor() -> DataEncryptor:
    global _encryptor
    if _encryptor is None:
        _encryptor = DataEncryptor()
    return _encryptor


def save_history(
    db: Session,
    content: str,
    detection_type: str,
    risk_level: str,
    result_detail: dict,
) -> DetectionHistory:
    encryptor = _get_encryptor()
    encrypted_content = encryptor.encrypt(content)
    encrypted_result = encryptor.encrypt(json.dumps(result_detail, ensure_ascii=False))
    record = DetectionHistory(
        input_content_encrypted=encrypted_content,
        detection_type=detection_type,
        risk_level=risk_level,
        result_detail_encrypted=encrypted_result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_history_list(
    db: Session, page: int = 1, page_size: int = 10
) -> HistoryList:
    offset = (page - 1) * page_size
    total = db.query(DetectionHistory).count()
    records = (
        db.query(DetectionHistory)
        .order_by(desc(DetectionHistory.created_at))
        .offset(offset)
        .limit(page_size)
        .all()
    )
    items = [
        HistoryItem(
            id=r.id,
            detection_type=r.detection_type,
            risk_level=r.risk_level,
            created_at=r.created_at,
        )
        for r in records
    ]
    return HistoryList(items=items, total=total, page=page, page_size=page_size)


def get_history_detail(db: Session, record_id: int) -> HistoryDetail | None:
    record = db.query(DetectionHistory).filter(DetectionHistory.id == record_id).first()
    if not record:
        return None
    encryptor = _get_encryptor()
    decrypted_content = encryptor.decrypt(record.input_content_encrypted)
    decrypted_result = encryptor.decrypt(record.result_detail_encrypted)
    result_detail = json.loads(decrypted_result) if decrypted_result else {}
    return HistoryDetail(
        id=record.id,
        input_content=decrypted_content,
        detection_type=record.detection_type,
        risk_level=record.risk_level,
        result_detail=result_detail,
        created_at=record.created_at,
    )


def delete_history(db: Session, record_id: int) -> bool:
    record = db.query(DetectionHistory).filter(DetectionHistory.id == record_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def clear_history(db: Session) -> int:
    count = db.query(DetectionHistory).count()
    db.query(DetectionHistory).delete()
    db.commit()
    return count
