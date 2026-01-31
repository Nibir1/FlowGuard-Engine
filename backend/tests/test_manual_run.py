"""
test_manual_run.py
------------------
A manual script to invoke the Graph directly.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from src.agents.graph import app_graph
from src.core.schema import TelemetryReading, DiagnosticResult
import asyncio

# Mock Input
mock_telemetry = TelemetryReading(
    elevator_id="TEST-ELV-01",
    velocity_m_s=0.0,
    door_cycles_count=50000,
    vibration_level_hz=0.2,
    error_codes=["E-302"] 
)

async def run_test():
    print("Starting Graph Execution...")
    
    inputs = {
        "telemetry": mock_telemetry,
        "retry_count": 0,
        "validation_error": None
    }
    
    # Invoke Graph
    result = await app_graph.ainvoke(inputs)
    
    print("\n\n=== FINAL DIAGNOSIS ===")
    report = result.get("diagnostic_report")

    if report:
        # Helper to safely get attributes whether it's Dict or Pydantic
        def get_attr(obj, key):
            if isinstance(obj, dict):
                return obj.get(key)
            return getattr(obj, key, None)

        print(f"Fault: {get_attr(report, 'fault_summary')}")
        print(f"Severity: {get_attr(report, 'severity_score')}/10")
        print(f"Root Cause: {get_attr(report, 'root_cause_hypothesis')}")
        
        print("Actions:")
        actions = get_attr(report, 'recommended_actions') or []
        for step in actions:
            # Handle nested action objects similarly
            instruction = step.get('instruction') if isinstance(step, dict) else getattr(step, 'instruction', str(step))
            print(f" - {instruction}")
            
        if result.get("validation_error"):
            print(f"\n[WARNING] Final output had validation errors: {result['validation_error']}")
    else:
        print("Failed to generate report.")

if __name__ == "__main__":
    asyncio.run(run_test())