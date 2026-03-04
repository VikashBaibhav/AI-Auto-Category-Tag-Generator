"""
FastAPI Application — main entry point.
Configures CORS, static files, and routes.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import router
from lib.logger import logger


# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
APP_DIR = os.path.join(BASE_DIR, "app")


app = FastAPI(
    title="AI Auto-Category & Tag Generator",
    description="AI-powered e-commerce product categorization using Google Gemini",
    version="1.0.0",
)

# CORS — allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router)

# Serve static frontend files
app.mount("/static", StaticFiles(directory=APP_DIR), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    index_path = os.path.join(APP_DIR, "index.html")
    return FileResponse(index_path)


@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("AI Auto-Category & Tag Generator — Server Started")
    logger.info("Open http://localhost:8000 in your browser")
    logger.info("API docs at http://localhost:8000/docs")
    logger.info("=" * 60)
