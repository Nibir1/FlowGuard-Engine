"""
test_api.py
-----------
Integration tests for the FastAPI endpoints.
Simulates real HTTP requests to ensure the Agent is correctly exposed.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.core.schema import TelemetryReading

# We use the ASGI transport to test the app without spinning up a real server
@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

@pytest.mark.asyncio
async def test_diagnose_endpoint():
    """
    Tests the full RAG pipeline via the API.
    This asserts that:
    1. The API accepts valid Telemetry JSON.
    2. The Agent runs successfully.
    3. The output adheres to the DiagnosticResult schema.
    """
    # Mock Telemetry Data
    payload = {
        "elevator_id": "TEST-INT-001",
        "velocity_m_s": 0.0,
        "door_cycles_count": 12000,
        "vibration_level_hz": 0.1,
        "error_codes": ["E-302"] # Door obstruction (matches our seed data)
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Set a higher timeout because GPT-4o takes a few seconds to think
        response = await ac.post("/api/v1/diagnose", json=payload, timeout=30.0)

    # Assertions
    assert response.status_code == 200, f"Request failed: {response.text}"
    
    data = response.json()
    
    # Check structure
    assert "fault_summary" in data
    assert "severity_score" in data
    assert "recommended_actions" in data
    
    # Check Logic (Did it actually find the door issue?)
    # We check for keywords related to the seed data
    summary_lower = data["fault_summary"].lower()
    assert "door" in summary_lower or "obstruction" in summary_lower

    print("\n\n✅ Integration Test Passed: Agent successfully diagnosed 'Door Obstruction' via API.")