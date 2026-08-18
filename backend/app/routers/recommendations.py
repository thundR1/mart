from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_session_id, get_current_user_optional
from app import models, schemas
from app.recommender import recommend_for_user, similar_products, reindex_all_products

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/for-you", response_model=list[schemas.ProductWithReason])
def for_you(
    limit: int = 8,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    user: models.User | None = Depends(get_current_user_optional),
):
    pairs = recommend_for_user(db, user.id if user else None, session_id, top_k=limit)
    out = []
    for product, reason in pairs:
        item = schemas.ProductWithReason.model_validate(product)
        item.reason = reason
        out.append(item)
    return out


@router.get("/similar/{product_id}", response_model=list[schemas.ProductOut])
def also_like(product_id: int, limit: int = 6, db: Session = Depends(get_db)):
    return similar_products(db, product_id, top_k=limit)


@router.post("/reindex")
def reindex(db: Session = Depends(get_db)):
    count = reindex_all_products(db)
    return {"reindexed": count}
