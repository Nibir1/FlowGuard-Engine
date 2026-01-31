"""
seed_db.py
----------
Utility script to populate the Vector Database with mock KONE technical data.
Run this once to give the AI a "Knowledge Base".
"""

import sys
import os

# Add parent directory to path so we can import src
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from src.services.vector_service import vector_service
from src.core.schema import ManualChunk
import asyncio

def run_seed():
    """
    Creates fake technical manual entries and uploads them to Qdrant.
    """
    print("Starting Knowledge Base Seeding...")
    
    mock_data = [
        ManualChunk(
            chunk_id="1",
            content="Error E-302 indicates a door obstruction during the closing cycle. "
                    "This is often caused by debris in the bottom track or a misaligned photo-eye sensor. "
                    "Technicians should inspect the sill groove and clean any particulate matter.",
            source_doc="KONE_Door_Systems_Maintenance_2024.pdf",
            page_number=42,
            related_error_codes=["E-302"]
        ),
        ManualChunk(
            chunk_id="2",
            content="High vibration levels (> 4.0 Hz) in the main cabin often suggest "
                    "wear on the guide rail rollers. If accompanied by screeching noise, "
                    "verify lubrication levels on the guide shoes immediately to prevent rail damage.",
            source_doc="KONE_Ride_Comfort_Standards.pdf",
            page_number=12,
            related_error_codes=["W-104", "VIB-HIGH"]
        ),
        ManualChunk(
            chunk_id="3",
            content="Safety Protocol for Pit Access: Before entering the elevator pit, "
                    "engage the pit stop switch and verify the car is secured. "
                    "Never enter the pit if water is present.",
            source_doc="KONE_Global_Safety_Manual.pdf",
            page_number=5,
            related_error_codes=[]
        )
    ]

    try:
        vector_service.upsert_manuals(mock_data)
        print("Seeding Complete! Qdrant is now populated.")
    except Exception as e:
        print(f"Error during seeding: {e}")

if __name__ == "__main__":
    run_seed()