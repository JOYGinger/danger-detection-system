from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.detection import DetectRequest, DetectResponse, HistoryList, HistoryDetail
from app.detectors import get_detector, detect_all
from app.services import history

router = APIRouter(prefix="/api", tags=["检测"])


@router.post("/detect/text", response_model=DetectResponse)
async def detect_text(request: DetectRequest, db: Session = Depends(get_db)):
    if request.detection_type:
        detector = get_detector(request.detection_type.value)
        result = detector.detect(request.content)
        result_dict = {
            "type": result.type,
            "risk_level": result.risk_level,
            "confidence": result.confidence,
            "details": result.details,
            "suggestions": result.suggestions,
        }
        history.save_history(
            db, request.content, result.type, result.risk_level, result_dict
        )
        return DetectResponse(success=True, result=result_dict)
    else:
        results = detect_all(request.content)
        results_dict = {
            name: {
                "type": r.type,
                "risk_level": r.risk_level,
                "confidence": r.confidence,
                "details": r.details,
                "suggestions": r.suggestions,
            }
            for name, r in results.items()
        }
        risk_levels = [r.risk_level for r in results.values()]
        overall_risk = "high" if "high" in risk_levels else "medium" if "medium" in risk_levels else "low" if "low" in risk_levels else "safe"
        history.save_history(
            db, request.content, "all", overall_risk, results_dict
        )
        return DetectResponse(success=True, results=results_dict)


@router.get("/history", response_model=HistoryList)
async def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return history.get_history_list(db, page=page, page_size=page_size)


@router.get("/history/{record_id}", response_model=HistoryDetail)
async def get_history(record_id: int, db: Session = Depends(get_db)):
    detail = history.get_history_detail(db, record_id)
    if not detail:
        raise HTTPException(status_code=404, detail="记录不存在")
    return detail


@router.delete("/history/{record_id}")
async def delete_history(record_id: int, db: Session = Depends(get_db)):
    if not history.delete_history(db, record_id):
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"success": True}


@router.delete("/history")
async def clear_history(db: Session = Depends(get_db)):
    count = history.clear_history(db)
    return {"success": True, "deleted_count": count}
