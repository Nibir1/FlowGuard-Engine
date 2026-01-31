"""
main.py
-------
Entry point for the FlowGuard-Engine Backend.
Initializes the FastAPI application, CORS middleware, and global routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import get_settings

# Load configuration
settings = get_settings()

def get_application() -> FastAPI:
    """
    Factory function to create the FastAPI application.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Industrial IoT GenAI Diagnostic Backend",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Configure Cross-Origin Resource Sharing (CORS)
    # Vital for the React Frontend to communicate with this Backend
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application

app = get_application()

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint for container orchestration.
    Returns:
        JSON: Status of the API.
    """
    return {
        "status": "active",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    # In development, we run programmatically. In Docker, the CMD handles this.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)