import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base, engine
from app.routes.auth_routes import router as auth_router
from app.routes.blog_routes import router as blog_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.prediction_routes import router as prediction_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Crop Disease Detection System")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "change-me-in-production"),
    max_age=60 * 60 * 24 * 7,
    same_site="lax",
    https_only=False,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(prediction_router)
app.include_router(blog_router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
