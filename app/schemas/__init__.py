from app.schemas.invoice import InvoiceSchema, SurveySchema

# Registry of all available schemas
SCHEMA_REGISTRY = {
    "invoice": InvoiceSchema,
    "survey": SurveySchema,
}

def get_schema_class(schema_name: str):
    """Get schema class by name."""
    schema_cls = SCHEMA_REGISTRY.get(schema_name.lower())
    if schema_cls is None:
        available = ", ".join(SCHEMA_REGISTRY.keys())
        raise ValueError(f"Unknown schema: {schema_name}. Available: {available}")
    return schema_cls
