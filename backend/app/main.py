from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.images import router as images_router

app = FastAPI(
    title="EL-VERIFY API",
    description="Evidence-based digital content inspection. Early development.",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api")
app.include_router(images_router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "EL-VERIFY",
        "status": "early-development",
        "message": "Verify what you see. Trust what you know.",
    }
