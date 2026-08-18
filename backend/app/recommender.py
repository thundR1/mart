from __future__ import annotations

import json
import math
from datetime import datetime
from typing import List, Optional, Sequence

import numpy as np
from sqlalchemy.orm import Session

from app.config import settings
from app import models

RECENCY_HALF_LIFE_DAYS = 14.0

EVENT_WEIGHTS = {
    models.EventType.VIEW: 1.0,
    models.EventType.SEARCH: 1.5,
    models.EventType.ADD_TO_CART: 3.0,
    models.EventType.PURCHASE: 5.0,
}


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class TfidfBackend:
    name = "tfidf"

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(max_features=512, stop_words="english")
        self._fitted = False

    def fit(self, texts: Sequence[str]) -> None:
        self.vectorizer.fit(texts)
        self._fitted = True

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        if not self._fitted:
            self.fit(texts)
        matrix = self.vectorizer.transform(texts).toarray().astype(np.float32)
        return _l2_normalize(matrix)


class TransformerBackend:
    name = "transformer"

    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def fit(self, texts: Sequence[str]) -> None:
        return

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        vectors = self.model.encode(list(texts), convert_to_numpy=True, show_progress_bar=False)
        return _l2_normalize(vectors.astype(np.float32))


_backend_instance = None


def get_backend():
    global _backend_instance
    if _backend_instance is not None:
        return _backend_instance

    if settings.embedding_backend == "transformer":
        try:
            _backend_instance = TransformerBackend()
        except Exception as exc:
            print(f"[recommender] transformer backend unavailable ({exc}); falling back to tfidf")
            _backend_instance = TfidfBackend()
    else:
        _backend_instance = TfidfBackend()
    return _backend_instance


def product_text(product: models.Product) -> str:
    return f"{product.name}. {product.category}. {product.description}"


def reindex_all_products(db: Session) -> int:
    products = db.query(models.Product).all()
    if not products:
        return 0
    texts = [product_text(p) for p in products]
    backend = get_backend()
    backend.fit(texts)
    vectors = backend.encode(texts)
    for product, vector in zip(products, vectors):
        product.embedding = json.dumps(vector.tolist())
    db.commit()
    return len(products)


def _load_matrix(db: Session, exclude_ids: Optional[set] = None):
    products = db.query(models.Product).filter(models.Product.embedding.isnot(None)).all()
    if exclude_ids:
        products = [p for p in products if p.id not in exclude_ids]
    if not products:
        return [], np.zeros((0, 1), dtype=np.float32)
    matrix = np.array([json.loads(p.embedding) for p in products], dtype=np.float32)
    return products, matrix


def _recency_weight(created_at: datetime) -> float:
    age_days = max((datetime.utcnow() - created_at).total_seconds() / 86400.0, 0.0)
    return math.exp(-age_days / RECENCY_HALF_LIFE_DAYS)


def _user_events(db: Session, user_id: Optional[int], session_id: str, limit: int = 200):
    q = db.query(models.ActivityEvent)
    if user_id:
        q = q.filter(models.ActivityEvent.user_id == user_id)
    else:
        q = q.filter(models.ActivityEvent.session_id == session_id)
    return q.order_by(models.ActivityEvent.created_at.desc()).limit(limit).all()


def build_user_profile(db: Session, user_id: Optional[int], session_id: str):
    events = _user_events(db, user_id, session_id)
    if not events:
        return None, []

    backend = get_backend()
    weighted_vectors = []
    source_products: dict[int, tuple[models.Product, float]] = {}

    search_texts, search_weights = [], []

    for event in events:
        weight = EVENT_WEIGHTS.get(event.event_type, 1.0) * _recency_weight(event.created_at)
        if event.product and event.product.embedding:
            vec = np.array(json.loads(event.product.embedding), dtype=np.float32)
            weighted_vectors.append(vec * weight)
            prev = source_products.get(event.product_id)
            if not prev or weight > prev[1]:
                source_products[event.product_id] = (event.product, weight)
        elif event.event_type == models.EventType.SEARCH and event.query:
            search_texts.append(event.query)
            search_weights.append(weight)

    if search_texts:
        search_vectors = backend.encode(search_texts)
        for vec, weight in zip(search_vectors, search_weights):
            weighted_vectors.append(vec * weight)

    if not weighted_vectors:
        return None, []

    user_vector = np.sum(weighted_vectors, axis=0)
    norm = np.linalg.norm(user_vector)
    if norm > 0:
        user_vector = user_vector / norm

    ranked_sources = sorted(source_products.values(), key=lambda t: t[1], reverse=True)
    return user_vector, ranked_sources


def _reason_for(candidate_vector: np.ndarray, sources: list) -> Optional[str]:
    if not sources:
        return None
    best_product, best_sim = None, -1.0
    for product, _weight in sources[:8]:
        if not product.embedding:
            continue
        vec = np.array(json.loads(product.embedding), dtype=np.float32)
        sim = float(np.dot(candidate_vector, vec))
        if sim > best_sim:
            best_sim, best_product = sim, product
    if best_product is None:
        return None
    return f"Because you liked {best_product.name}"


def popular_products(db: Session, top_k: int, exclude_ids: Optional[set] = None):
    from sqlalchemy import func
    q = (
        db.query(models.ActivityEvent.product_id, func.count(models.ActivityEvent.id).label("cnt"))
        .filter(models.ActivityEvent.product_id.isnot(None))
        .group_by(models.ActivityEvent.product_id)
        .order_by(func.count(models.ActivityEvent.id).desc())
        .limit(top_k + len(exclude_ids or []))
    )
    ranked_ids = [row[0] for row in q.all()]
    products = []
    for pid in ranked_ids:
        if exclude_ids and pid in exclude_ids:
            continue
        product = db.query(models.Product).get(pid)
        if product:
            products.append((product, "Trending now"))
        if len(products) >= top_k:
            break
    if len(products) < top_k:
        seen = {p.id for p, _ in products} | (exclude_ids or set())
        for product in db.query(models.Product).order_by(models.Product.created_at.desc()).all():
            if product.id in seen:
                continue
            products.append((product, "New arrival"))
            seen.add(product.id)
            if len(products) >= top_k:
                break
    return products


def recommend_for_user(db: Session, user_id: Optional[int], session_id: str, top_k: int = 8,
                        exclude_ids: Optional[set] = None):
    exclude_ids = set(exclude_ids or set())
    user_vector, sources = build_user_profile(db, user_id, session_id)

    if user_vector is None:
        return popular_products(db, top_k, exclude_ids)

    products, matrix = _load_matrix(db, exclude_ids)
    if len(products) == 0:
        return []

    scores = matrix @ user_vector
    order = np.argsort(-scores)[:top_k]

    results = []
    for idx in order:
        product = products[idx]
        vec = matrix[idx]
        reason = _reason_for(vec, sources) or "Picked for you"
        results.append((product, reason))
    return results


def similar_products(db: Session, product_id: int, top_k: int = 6):
    target = db.query(models.Product).get(product_id)
    if not target or not target.embedding:
        return []
    target_vec = np.array(json.loads(target.embedding), dtype=np.float32)
    products, matrix = _load_matrix(db, exclude_ids={product_id})
    if len(products) == 0:
        return []
    scores = matrix @ target_vec
    order = np.argsort(-scores)[:top_k]
    return [products[i] for i in order]


def semantic_search(db: Session, query: str, top_k: int = 24):
    backend = get_backend()
    products, matrix = _load_matrix(db)
    if len(products) == 0:
        return []
    query_vec = backend.encode([query])[0]
    scores = matrix @ query_vec
    order = np.argsort(-scores)[:top_k]
    return [(products[i], float(scores[i])) for i in order]
