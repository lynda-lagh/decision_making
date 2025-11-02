"""
WeeFarm Predictive Maintenance API
FastAPI Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="REST API for WeeFarm Predictive Maintenance System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "WeeFarm Predictive Maintenance API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Import routers
from .routers import equipment, predictions, schedule, kpis, maintenance, analytics

# Include routers
app.include_router(equipment.router, prefix=settings.API_PREFIX, tags=["Equipment"])
app.include_router(predictions.router, prefix=settings.API_PREFIX, tags=["Predictions"])
app.include_router(schedule.router, prefix=settings.API_PREFIX, tags=["Schedule"])
app.include_router(kpis.router, prefix=settings.API_PREFIX, tags=["KPIs"])
app.include_router(maintenance.router, prefix=settings.API_PREFIX, tags=["Maintenance"])
app.include_router(analytics.router, prefix=settings.API_PREFIX, tags=["Analytics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
