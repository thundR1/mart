from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import auth, products, activity, cart, orders, recommendations

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mart API", version="1.0.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(activity.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(recommendations.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "meridian-api"}
