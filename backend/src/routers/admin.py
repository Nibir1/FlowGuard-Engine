"""
admin.py
--------
Administrative endpoints for managing the Knowledge Base.
Allows the frontend to trigger RAG ingestion (ETL Pipeline) and view indexed documents.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.services.vector_service import vector_service
from src.core.schema import ManualChunk
import uuid

router = APIRouter()

# Mock data source (simulating a PDF parser output)
MOCK_MANUALS = [
    ManualChunk(
        chunk_id=str(uuid.uuid4()),
        content="Error E-302 indicates a door obstruction during the closing cycle. Check for debris in the sill groove.",
        source_doc="KONE_Door_Systems_Maintenance_2024.pdf",
        page_number=42,
        related_error_codes=["E-302"]
    ),
    ManualChunk(
        chunk_id=str(uuid.uuid4()),
        content="High vibration (> 4.0 Hz) suggests guide rail roller wear. Verify lubrication immediately.",
        source_doc="KONE_Ride_Comfort_Standards.pdf",
        page_number=12,
        related_error_codes=["W-104", "VIB-HIGH"]
    ),
    ManualChunk(
        chunk_id=str(uuid.uuid4()),
        content="Safety Protocol: Engage pit stop switch before entering. Never enter if water is present.",
        source_doc="KONE_Global_Safety_Manual.pdf",
        page_number=5,
        related_error_codes=[]
    )
]

@router.post("/seed")
async def seed_knowledge_base(background_tasks: BackgroundTasks):
    """
    Triggers the ETL pipeline to ingest technical manuals into Qdrant.
    Runs in the background to avoid blocking the UI.
    """
    try:
        # We run this in the background because real vectorization takes time
        background_tasks.add_task(vector_service.upsert_manuals, MOCK_MANUALS)
        return {"status": "success", "message": "Ingestion pipeline triggered. Data is being vectorised."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents():
    """
    Returns a list of documents currently indexed (Mocked for this view).
    In a real app, we would query Qdrant points, but Qdrant doesn't support 'select *' easily.
    """
    # Simply returning the source docs we know about for the UI display
    return {
        "count": len(MOCK_MANUALS),
        "documents": list(set(d.source_doc for d in MOCK_MANUALS))
    }