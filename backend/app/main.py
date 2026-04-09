from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.database import engine, Base
from app.db import models
from app.api import health, analyze, history, stats

setup_logging()

# Generate database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Phishing Detector API for Bachelor Thesis"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(stats.router, prefix="/api", tags=["stats"])

@app.get("/")
def root():
    return {"message": "Phishing Detector API - See /docs for API documentation"}