"""
FastAPI Main Application Entry Point.
Provides RESTful APIs and serves the interactive Web Dashboard.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api import health, predict, transactions, analytics

app = FastAPI(
    title="AI-Based Financial Fraud Detection Platform",
    description="End-to-End Cybersecurity & Machine Learning Transaction Risk Scoring Engine",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on Startup
@app.on_event("startup")
def on_startup():
    init_db()

# Mount API Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(predict.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)

# Serve Frontend Static Assets
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_root():
        return FileResponse(os.path.join(frontend_dir, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
