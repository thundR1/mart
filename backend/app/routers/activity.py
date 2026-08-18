from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_session_id, get_current_user_optional
from app import models, schemas

router = APIRouter(prefix="/activity", tags=["activity"])


@router.post("", status_code=201)
def log_activity(
    payload: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    user: models.User | None = Depends(get_current_user_optional),
):
    event = models.ActivityEvent(
        user_id=user.id if user else None,
        session_id=session_id,
        product_id=payload.product_id,
        event_type=payload.event_type,
        query=payload.query,
    )
    db.add(event)
    db.commit()
    return {"status": "logged"}
