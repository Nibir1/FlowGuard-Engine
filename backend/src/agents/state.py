"""
state.py
--------
Defines the State Schema for the LangGraph agent.
This TypedDict serves as the 'Shared Memory' between the different nodes (functions)
in the graph.
"""

from typing import TypedDict, List, Optional
from src.core.schema import TelemetryReading, ManualChunk, DiagnosticResult

class AgentState(TypedDict):
    # INPUT: The raw sensor data from the request
    telemetry: TelemetryReading
    
    # PROCESS: Documentation retrieved from Vector DB
    retrieved_docs: List[ManualChunk]
    
    # OUTPUT: The structured diagnosis (can be None during processing)
    diagnostic_report: Optional[DiagnosticResult]
    
    # CONTROL FLOW: Tracking retries for the cyclic loop
    retry_count: int
    validation_error: Optional[str]