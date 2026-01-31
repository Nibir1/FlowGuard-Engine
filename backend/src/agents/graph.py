"""
graph.py
--------
Constructs the LangGraph Workflow.
"""

from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.nodes import retrieve_node, diagnose_node, validate_node

# 1. Initialize Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("diagnose", diagnose_node)
workflow.add_node("validate", validate_node)

# 3. Define Entry Point
workflow.set_entry_point("retrieve")

# 4. Define Edges (Standard Flow)
workflow.add_edge("retrieve", "diagnose")
workflow.add_edge("diagnose", "validate")

# 5. Define Conditional Logic (The Loop)
def should_retry(state: AgentState):
    """
    Decides if we are done or need to loop back.
    """
    error = state.get("validation_error")
    retries = state.get("retry_count", 0)
    
    if error and retries < 3:
        # Loop back to 'diagnose' to fix the mistake
        return "diagnose"
    return END

# Add the conditional edge
workflow.add_conditional_edges(
    "validate",
    should_retry,
    {
        "diagnose": "diagnose", # Map return value to node name
        END: END
    }
)

# 6. Compile
app_graph = workflow.compile()