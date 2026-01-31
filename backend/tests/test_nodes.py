import pytest
from src.agents.nodes import validate_node, retrieve_node
from src.agents.graph import should_retry, END
from src.core.schema import DiagnosticResult, TelemetryReading, ManualChunk

# ---------------------------------------------------------
# TEST 1: The Safety Guardrail (validate_node)
# ---------------------------------------------------------

def test_validate_node_blocks_unsafe_high_severity():
    """
    Scenario: LLM outputs Severity 9 but forgets 'Lock out power'.
    Expectation: Validator detects it and returns an error.
    """
    unsafe_report = DiagnosticResult(
        fault_summary="Critical motor failure",
        root_cause_hypothesis="Overheating",
        severity_score=9,  # HIGH SEVERITY
        cited_manual_references=["M-1"],
        recommended_actions=[],
        safety_warnings=["Wear gloves"] # MISSING 'Lock out'
    )
    
    state = {
        "diagnostic_report": unsafe_report,
        "retry_count": 0
    }
    
    result = validate_node(state)
    
    assert result["validation_error"] is not None
    # Fixed: Match the actual error message from nodes.py
    assert "High severity detected but no 'Lock Out' or 'Safety' warning provided." in result["validation_error"]
    assert result["retry_count"] == 1

def test_validate_node_allows_safe_high_severity():
    """
    Scenario: LLM outputs Severity 9 AND includes 'Lock out power'.
    Expectation: Validation passes.
    """
    safe_report = DiagnosticResult(
        fault_summary="Critical motor failure",
        root_cause_hypothesis="Overheating",
        severity_score=9,
        cited_manual_references=["M-1"],
        recommended_actions=[],
        safety_warnings=["Lock out power before servicing"] # CORRECT
    )
    
    state = {
        "diagnostic_report": safe_report,
        "retry_count": 0
    }
    
    result = validate_node(state)
    assert result["validation_error"] is None

# ---------------------------------------------------------
# TEST 2: The Loop Logic (should_retry)
# ---------------------------------------------------------

def test_should_retry_logic():
    # Case: Error exists, retries < 3 -> LOOP
    state_loop = {"validation_error": "Some error", "retry_count": 1}
    assert should_retry(state_loop) == "diagnose"

    # Case: Error exists, retries = 3 -> STOP (Give up)
    state_stop = {"validation_error": "Some error", "retry_count": 3}
    assert should_retry(state_stop) == END

    # Case: No error -> STOP (Success)
    state_success = {"validation_error": None, "retry_count": 0}
    assert should_retry(state_success) == END

# ---------------------------------------------------------
# TEST 3: Context Retrieval (Mocked Vector DB)
# ---------------------------------------------------------
from unittest.mock import MagicMock, patch

@patch("src.agents.nodes.vector_service")
def test_retrieve_node_uses_error_codes(mock_vector_service):
    """
    Test that the retrieve node actually queries Qdrant with the error codes.
    """
    # Setup Mock
    mock_vector_service.search_similar.return_value = [
        ManualChunk(chunk_id="1", content="Test", source_doc="Doc", page_number=1, related_error_codes=[])
    ]

    # Input State
    telemetry = TelemetryReading(
        elevator_id="ID", velocity_m_s=0, door_cycles_count=0, vibration_level_hz=0,
        error_codes=["E-302", "E-501"]
    )
    state = {"telemetry": telemetry}

    # Execute
    result = retrieve_node(state)

    # Verify Logic
    assert len(result["retrieved_docs"]) == 1
    # Verify it called search for BOTH error codes
    assert mock_vector_service.search_similar.call_count == 2
    mock_vector_service.search_similar.assert_any_call("E-302", limit=2)
    mock_vector_service.search_similar.assert_any_call("E-501", limit=2)
