from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_session_id, get_current_user_required
from app import models, schemas

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=schemas.OrderOut, status_code=201)
def checkout(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
    user: models.User = Depends(get_current_user_required),
):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = sum(item.product.price * item.quantity for item in cart_items)
    order = models.Order(user_id=user.id, total=total)
    db.add(order)
    db.flush()

    for item in cart_items:
        db.add(models.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.product.price,
        ))
        db.add(models.ActivityEvent(
            user_id=user.id,
            session_id=session_id,
            product_id=item.product_id,
            event_type=models.EventType.PURCHASE,
        ))
        db.delete(item)

    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db), user: models.User = Depends(get_current_user_required)):
    return (
        db.query(models.Order)
        .filter(models.Order.user_id == user.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )
