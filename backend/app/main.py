from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routes.health import router as health_router
from app.routes.images import router as images_router

app = FastAPI(
    title="EL-VERIFY API",
    description="Evidence-based digital content inspection. Early development.",
    version="0.2.0",
)

app.include_router(health_router, prefix="/api")
app.include_router(images_router, prefix="/api")


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/app/")


@app.get("/api", include_in_schema=False)
def api_root():
    return {
        "name": "EL-VERIFY",
        "status": "early-development",
        "message": "Verify what you see. Trust what you know.",
    }


frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="frontend")
