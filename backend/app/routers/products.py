from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.recommender import semantic_search

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[schemas.ProductOut])
def list_products(
    category: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    if q:
        like = f"%{q}%"
        query = query.filter(models.Product.name.ilike(like))
    return query.order_by(models.Product.id).all()


@router.get("/categories", response_model=list[str])
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(models.Product.category).distinct().all()
    return sorted(r[0] for r in rows)


@router.get("/search", response_model=list[schemas.ProductWithReason])
def search_products(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    results = semantic_search(db, query, top_k=24)
    out = []
    for product, score in results:
        item = schemas.ProductWithReason.model_validate(product)
        item.score = score
        out.append(item)
    return out


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
