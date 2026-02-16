"""
Main FastAPI Application
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Callable

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, patients, encounters, prescriptions, abdm, clinical

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info("Starting IntegMed API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Version: {settings.API_VERSION}")
    
    # Create database tables (in production, use Alembic migrations)
    # Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    logger.info("Shutting down IntegMed API...")


# Create FastAPI app
app = FastAPI(
    title="IntegMed API",
    description="Integrated Healthcare Platform - Allopathy + AYUSH",
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s"
        )
    
    return response


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": "server_error"
        }
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check
    """
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check (includes database connectivity)
    """
    try:
        # Test database connection
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "ready",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "disconnected",
                "error": str(e)
            }
        )


# Include routers
app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}/auth", tags=["Authentication"])
app.include_router(patients.router, prefix=f"/api/{settings.API_VERSION}/patients", tags=["Patients"])
app.include_router(encounters.router, prefix=f"/api/{settings.API_VERSION}/encounters", tags=["Encounters"])
app.include_router(prescriptions.router, prefix=f"/api/{settings.API_VERSION}/prescriptions", tags=["Prescriptions"])
app.include_router(abdm.router, prefix=f"/api/{settings.API_VERSION}/abdm", tags=["ABDM"])
app.include_router(clinical.router, prefix=f"/api/{settings.API_VERSION}/clinical", tags=["Clinical"])


@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint
    """
    return {
        "message": "IntegMed API - Integrated Healthcare Platform",
        "version": settings.API_VERSION,
        "docs": f"/api/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
