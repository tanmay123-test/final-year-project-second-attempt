"""
AI Groups FastAPI Main Application
Production-ready FastAPI application for AI Groups functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from database.ai_groups_connection import init_db
from database.routes import ai_groups

# Create FastAPI application
app = FastAPI(
    title="AI Groups API",
    description="AI Groups - Phase 1 Core Infrastructure",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include AI Groups routes
app.include_router(ai_groups.router)

@app.on_event("startup")
async def startup_event():
    """
    Initialize database on application startup
    """
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown
    """
    print("🔄 Application shutting down...")

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "AI Groups API - Phase 1",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "service": "ai-groups-api"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler
    """
    return {
        "error": "Internal server error",
        "message": str(exc),
        "status_code": 500
    }

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
