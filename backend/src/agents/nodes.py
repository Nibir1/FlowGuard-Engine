"""
nodes.py
--------
The functional units of the LangGraph.
Each function takes the current AgentState, performs work, and returns an update.
"""

from src.agents.state import AgentState
from src.services.vector_service import vector_service
from src.services.llm_service import llm_service
from src.core.schema import DiagnosticResult

# ---------------------------------------------------------
# NODE 1: Context Retrieval
# ---------------------------------------------------------
def retrieve_node(state: AgentState) -> AgentState:
    """
    Looks at the telemetry error codes and fetches relevant manuals.
    """
    print("--- Node: Retrieving Context ---")
    telemetry = state["telemetry"]
    
    # Construct a query from error codes + ID
    # In a real system, we might expand this query
    search_queries = telemetry.error_codes if telemetry.error_codes else ["general maintenance"]
    
    all_docs = []
    for query in search_queries:
        docs = vector_service.search_similar(query, limit=2)
        all_docs.extend(docs)
    
    # Deduplicate by chunk_id
    unique_docs = {doc.chunk_id: doc for doc in all_docs}.values()
    
    return {"retrieved_docs": list(unique_docs)}

# ---------------------------------------------------------
# NODE 2: AI Diagnosis
# ---------------------------------------------------------
def diagnose_node(state: AgentState) -> AgentState:
    """
    Synthesizes Telemetry + Manuals into a Report.
    """
    print("--- Node: Generating Diagnosis ---")
    
    analyzer = llm_service.get_analyzer()
    
    # Construct the Prompt Context
    telemetry_context = state["telemetry"].model_dump_json(indent=2)
    
    # Handle retrieved docs (ensure they are strings, not objects)
    manual_context = "\n\n".join(
        [f"Source: {d.source_doc} (Pg {d.page_number}): {d.content}" 
         for d in state["retrieved_docs"]]
    )
    
    # Inject previous errors if we are retrying
    retry_context = ""
    if state.get("validation_error"):
        retry_context = f"""
        CRITICAL INSTRUCTION: Your previous attempt failed validation.
        ERROR: {state['validation_error']}
        
        Reflect on this error. ensure 'recommended_actions' is a LIST OF OBJECTS with 'instruction', 'action_type', and 'estimated_time_minutes'.
        Do NOT return simple strings for actions.
        """

    prompt = f"""
    You are an expert KONE Industrial IoT Engineer. 
    Analyze the following Elevator Telemetry and Technical Manuals to produce a diagnostic report.
    
    TELEMETRY DATA:
    {telemetry_context}
    
    TECHNICAL MANUALS (Reference these explicitly):
    {manual_context}
    
    {retry_context}
    
    REQUIREMENTS:
    1. Identify the root cause based on sensor values and error codes.
    2. Cite specific manuals in your findings.
    3. Assign a severity score (1-10).
    4. Provide a step-by-step action plan for the technician.
    
    IMPORTANT SCHEMA NOTE:
    - 'recommended_actions' must be a list of objects.
    - EACH object must have: 'step_order' (int), 'instruction' (str), 'action_type' (str), and 'estimated_time_minutes' (int).
    
    Example:
    [
      {{ "step_order": 1, "instruction": "Check door track", "action_type": "inspection", "estimated_time_minutes": 15 }},
      {{ "step_order": 2, "instruction": "Clean debris", "action_type": "repair", "estimated_time_minutes": 10 }}
    ]
    """
    
    # Invoke LLM
    try:
        response: DiagnosticResult = analyzer.invoke(prompt)
        return {"diagnostic_report": response}
    except Exception as e:
        # Fallback for LLM parsing errors
        print(f"LLM Generation Error: {e}")
        return {"validation_error": str(e)}

# ---------------------------------------------------------
# NODE 3: Safety Guardrail
# ---------------------------------------------------------
def validate_node(state: AgentState) -> AgentState:
    """
    Post-processing check.
    Ensures that high-severity issues have explicit safety warnings.
    """
    print("--- Node: Validating Output ---")
    report = state["diagnostic_report"]
    
    if not report:
        return {"validation_error": "No report generated."}
    
    # --- FIX START: Handle Dictionary Conversion Safely ---
    if isinstance(report, dict):
        try:
            report = DiagnosticResult(**report)
        except Exception as e:
            # PRINT THE ERROR so we know why it's failing
            print(f"!!! Pydantic Conversion Error: {e} !!!")
            return {
                "validation_error": f"Invalid report format: {e}",
                # CRITICAL: Increment retry count to prevent infinite loops
                "retry_count": state.get("retry_count", 0) + 1
            }
    # --- FIX END ---
    
    # RULE: If Severity > 7, there MUST be a "Safety" or "Lockout" warning
    if report.severity_score >= 7:
        has_safety_term = any(
            term in " ".join(report.safety_warnings).lower() 
            for term in ["lock out", "power off", "safety", "danger", "stop"]
        )
        if not has_safety_term:
            print("!!! Guardrail Triggered: Missing Safety Warning !!!")
            return {
                "validation_error": "High severity detected but no 'Lock Out' or 'Safety' warning provided.",
                "retry_count": state.get("retry_count", 0) + 1
            }
            
    # If we get here, it's valid
    return {"validation_error": None}