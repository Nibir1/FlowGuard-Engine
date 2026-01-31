"""
schema.py
---------
Domain models for FlowGuard-Engine.
This file defines the strict data contracts using Pydantic V2.
These models serve as the bridge between raw IoT data, the Vector DB, and the LLM's structured output.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

# ------------------------------------------------------------------
# INPUT MODELS (IoT Telemetry)
# ------------------------------------------------------------------

class TelemetryReading(BaseModel):
    """
    Represents a single snapshot of elevator sensor data.
    In a real scenario, this comes from an MQTT broker or IoT Hub.
    """
    elevator_id: str = Field(..., description="Unique identifier for the asset")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Sensor Metrics
    velocity_m_s: float = Field(..., description="Current cabin velocity in meters/second")
    door_cycles_count: int = Field(..., description="Total door open/close cycles since maintenance")
    vibration_level_hz: float = Field(..., description="Vibration frequency detected in the cabin rail")
    
    # Error state
    error_codes: List[str] = Field(
        default=[], 
        description="List of active error codes reported by the control board (e.g., 'E-501')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "elevator_id": "KONE-ESPOO-01",
                "velocity_m_s": 1.2,
                "door_cycles_count": 15000,
                "vibration_level_hz": 4.5,
                "error_codes": ["E-302", "W-104"]
            }
        }


# ------------------------------------------------------------------
# STORAGE MODELS (RAG Context)
# ------------------------------------------------------------------

class ManualChunk(BaseModel):
    """
    Represents a specific section of a technical manual stored in the Vector DB.
    """
    chunk_id: str = Field(..., description="Unique hash of the content")
    content: str = Field(..., description="The actual text of the manual section")
    source_doc: str = Field(..., description="Filename of the manual (e.g., 'Maintenance_Guide_v2.pdf')")
    page_number: int = Field(..., description="Page reference for verification")
    
    # Metadata for filtering
    related_error_codes: List[str] = Field(default=[], description="Tags for error codes mentioned in this chunk")


# ------------------------------------------------------------------
# OUTPUT MODELS (LLM Diagnostic)
# ------------------------------------------------------------------

class MaintenanceStep(BaseModel):
    """A single actionable step for the field technician."""
    step_order: int
    instruction: str
    tool_required: Optional[str] = None

class DiagnosticResult(BaseModel):
    """
    The final structured output expected from the Agent.
    This structure forces the LLM to think in 'Engineering Terms'.
    """
    fault_summary: str = Field(..., description="Concise technical summary of the issue")
    
    # Classification
    root_cause_hypothesis: str = Field(..., description="The AI's best guess at the physical cause")
    severity_score: int = Field(..., ge=1, le=10, description="1 (Cosmetic) to 10 (Critical/Safety Risk)")
    
    # Grounded References
    cited_manual_references: List[str] = Field(..., description="List of Manual IDs or Pages used to derive this")
    
    # Action Plan
    recommended_actions: List[MaintenanceStep]
    
    # Safety is paramount at KONE
    safety_warnings: List[str] = Field(..., description="Crucial safety protocols (e.g., 'Lock out power')")

    @field_validator('severity_score')
    @classmethod
    def check_severity_range(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError('Severity score must be between 1 and 10')
        return v