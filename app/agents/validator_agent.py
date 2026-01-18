from langgraph.graph import StateGraph, END
from app.agents.nodes import AgentState, extract_node, validate_node, correct_node, should_continue
from app.services.llm_service import LLMService
from functools import partial

def create_validator_agent(llm_service: LLMService, max_attempts: int = 3):
    """Create LangGraph agent with feedback loops."""
    
    # Create graph
    graph = StateGraph(AgentState)
    
    # Add nodes with LLM service injected
    graph.add_node("extract", partial(extract_node, llm_service=llm_service))
    graph.add_node("validate", validate_node)
    graph.add_node("correct", partial(correct_node, llm_service=llm_service))
    
    # Define edges
    graph.set_entry_point("extract")
    graph.add_edge("extract", "validate")
    
    # Conditional edge: continue correcting or end
    graph.add_conditional_edges(
        "validate",
        partial(should_continue, max_attempts=max_attempts),
        {
            "correct": "correct",
            "end": END
        }
    )
    graph.add_edge("correct", "validate")
    
    return graph.compile()

def run_validation(raw_input: str, schema_name: str, llm_service: LLMService) -> AgentState:
    """Execute the validation agent."""
    agent = create_validator_agent(llm_service)
    
    initial_state: AgentState = {
        "raw_input": raw_input,
        "schema_name": schema_name,
        "extracted_data": None,
        "validation_errors": [],
        "corrected_data": None,
        "attempt_count": 0,
        "is_valid": False,
        "audit_log": []
    }
    
    final_state = agent.invoke(initial_state)  # type: ignore
    return final_state