"""
Main FastAPI Application for Trivya Backend

This module initializes the FastAPI application, configures middleware,
and includes API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add parent directory to path for imports if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger
from backend.app.api.v1.endpoints import auth

# Initialize config and logger
config = Config()
logger = get_logger(config).get_logger("BackendApp")

app = FastAPI(
    title="Trivya Platform API",
    description="Backend API for Trivya AI Customer Support Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Frontend dev server
    "http://localhost:8000",  # Backend dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])


@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info("Trivya Backend API starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("Trivya Backend API shutting down")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Welcome to Trivya Platform API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "database": "connected",  # Mocked for now
            "redis": "connected"      # Mocked for now
        }
    }
