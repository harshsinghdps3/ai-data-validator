from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, ValidationError
import json

class AgentState(TypedDict):
    raw_input: str
    schema_name: str
    extracted_data: dict | None
    validation_errors: list[str]
    corrected_data: dict | None
    attempt_count: int
    is_valid: bool
    audit_log: list[dict]

def extract_node(state: AgentState, llm_service) -> AgentState:
    """Extract structured data from raw input using LLM."""
    from app.agents.prompts import EXTRACTION_PROMPT
    from app.schemas import get_schema_class
    
    schema_cls = get_schema_class(state["schema_name"])
    schema_fields = json.dumps(schema_cls.model_json_schema(), indent=2)
    
    prompt = EXTRACTION_PROMPT.format(
        schema_name=state["schema_name"],
        schema_fields=schema_fields,
        raw_input=state["raw_input"]
    )
    
    response = llm_service.generate(prompt)
    extracted = json.loads(response)
    
    state["extracted_data"] = extracted
    state["audit_log"].append({
        "step": "extraction",
        "attempt": state["attempt_count"],
        "result": extracted
    })
    return state

def validate_node(state: AgentState) -> AgentState:
    """Validate extracted data against Pydantic schema."""
    from app.schemas import get_schema_class
    
    schema_cls = get_schema_class(state["schema_name"])
    data = state["corrected_data"] or state["extracted_data"]
    
    try:
        validated = schema_cls.model_validate(data)
        state["corrected_data"] = validated.model_dump(mode="json")
        state["is_valid"] = True
        state["validation_errors"] = []
    except ValidationError as e:
        state["is_valid"] = False
        state["validation_errors"] = [str(err) for err in e.errors()]
    
    state["audit_log"].append({
        "step": "validation",
        "attempt": state["attempt_count"],
        "is_valid": state["is_valid"],
        "errors": state["validation_errors"]
    })
    return state

def correct_node(state: AgentState, llm_service) -> AgentState:
    """Use LLM to correct validation errors."""
    from app.agents.prompts import CORRECTION_PROMPT
    from app.schemas import get_schema_class
    
    schema_cls = get_schema_class(state["schema_name"])
    schema_fields = json.dumps(schema_cls.model_json_schema(), indent=2)
    
    prompt = CORRECTION_PROMPT.format(
        extracted_data=json.dumps(state["extracted_data"], indent=2),
        validation_errors="\n".join(state["validation_errors"]),
        schema_fields=schema_fields
    )
    
    response = llm_service.generate(prompt)
    corrected = json.loads(response)
    
    state["corrected_data"] = corrected
    state["attempt_count"] += 1
    state["audit_log"].append({
        "step": "correction",
        "attempt": state["attempt_count"],
        "corrections_applied": corrected
    })
    return state

def should_continue(state: AgentState, max_attempts: int = 3) -> Literal["correct", "end"]:
    """Decide whether to continue correction loop or end."""
    if state["is_valid"]:
        return "end"
    if state["attempt_count"] >= max_attempts:
        return "end"
    return "correct"