from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import decode_access_token
from app import models


def get_session_id(x_session_id: Optional[str] = Header(default=None)) -> str:
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Session-Id header",
        )
    return x_session_id


def get_current_user_optional(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    email = decode_access_token(token)
    if not email:
        return None
    return db.query(models.User).filter(models.User.email == email).first()


def get_current_user_required(
    user: Optional[models.User] = Depends(get_current_user_optional),
) -> models.User:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
