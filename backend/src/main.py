"""
main.py
-------
Entry point for the FlowGuard-Engine Backend.
Exposes the LangGraph Agent via a RESTful API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.routers import admin
from src.core.config import get_settings
from src.core.schema import TelemetryReading, DiagnosticResult
from src.agents.graph import app_graph

# Load configuration
settings = get_settings()

def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Industrial IoT GenAI Diagnostic Backend",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

    return application

app = get_application()

@app.get("/health")
async def health_check():
    return {
        "status": "active",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }

# ---------------------------------------------------------
# NEW: Diagnostic Endpoint
# ---------------------------------------------------------
@app.post("/api/v1/diagnose", response_model=DiagnosticResult)
async def run_diagnostic(telemetry: TelemetryReading):
    """
    Triggers the Agentic RAG Workflow.
    1. Receives Telemetry.
    2. Initializes Agent State.
    3. Runs the Graph (Retrieve -> Diagnose -> Validate).
    4. Returns Structured Report.
    """
    # Initialize the state for the graph
    initial_state = {
        "telemetry": telemetry,
        "retry_count": 0,
        "validation_error": None
    }

    try:
        # Run the graph
        # ainvoke waits for the entire graph to finish execution
        final_state = await app_graph.ainvoke(initial_state)
        
        report = final_state.get("diagnostic_report")
        
        if not report:
            raise HTTPException(status_code=500, detail="Agent failed to generate a report.")
        
        # Ensure we return a proper Pydantic object to FastAPI
        # (FastAPI handles the JSON serialization automatically)
        if isinstance(report, dict):
            return DiagnosticResult(**report)
            
        return report

    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)