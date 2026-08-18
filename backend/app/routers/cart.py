from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_session_id, get_current_user_optional
from app import models, schemas

router = APIRouter(prefix="/cart", tags=["cart"])


def _owner_filter(query, user, session_id):
    if user:
        return query.filter(models.CartItem.user_id == user.id)
    return query.filter(models.CartItem.session_id == session_id)


@router.get("", response_model=list[schemas.CartItemOut])
def get_cart(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    user: models.User | None = Depends(get_current_user_optional),
):
    query = _owner_filter(db.query(models.CartItem), user, session_id)
    return query.all()


@router.post("", response_model=schemas.CartItemOut, status_code=201)
def add_to_cart(
    payload: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    user: models.User | None = Depends(get_current_user_optional),
):
    product = db.query(models.Product).get(payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    query = _owner_filter(db.query(models.CartItem), user, session_id).filter(
        models.CartItem.product_id == payload.product_id
    )
    item = query.first()
    if item:
        item.quantity += payload.quantity
    else:
        item = models.CartItem(
            user_id=user.id if user else None,
            session_id=session_id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        db.add(item)
    db.commit()
    db.refresh(item)

    db.add(models.ActivityEvent(
        user_id=user.id if user else None,
        session_id=session_id,
        product_id=payload.product_id,
        event_type=models.EventType.ADD_TO_CART,
    ))
    db.commit()
    return item


@router.delete("/{item_id}", status_code=204)
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    user: models.User | None = Depends(get_current_user_optional),
):
    query = _owner_filter(db.query(models.CartItem), user, session_id).filter(
        models.CartItem.id == item_id
    )
    item = query.first()
    if item:
        db.delete(item)
        db.commit()
    return None
