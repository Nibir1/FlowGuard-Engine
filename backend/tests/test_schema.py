import pytest
from pydantic import ValidationError
from src.core.schema import DiagnosticResult, MaintenanceStep

def test_diagnostic_result_valid():
    """Test that a valid payload passes validation."""
    data = {
        "fault_summary": "Test fault",
        "root_cause_hypothesis": "Test cause",
        "severity_score": 5,
        "cited_manual_references": ["Man-01"],
        "recommended_actions": [
            {"step_order": 1, "instruction": "Fix it", "tool_required": "Hammer"}
        ],
        "safety_warnings": ["Watch out"]
    }
    result = DiagnosticResult(**data)
    assert result.severity_score == 5

def test_severity_score_bounds():
    """Test that severity score must be 1-10."""
    base_data = {
        "fault_summary": "Test",
        "root_cause_hypothesis": "Test",
        "cited_manual_references": [],
        "recommended_actions": [],
        "safety_warnings": []
    }

    # Test > 10
    with pytest.raises(ValidationError):
        DiagnosticResult(**base_data, severity_score=11)

    # Test < 1
    with pytest.raises(ValidationError):
        DiagnosticResult(**base_data, severity_score=0)

def test_missing_required_fields():
    """Test that missing fields trigger validation error."""
    with pytest.raises(ValidationError):
        DiagnosticResult(fault_summary="Just this")