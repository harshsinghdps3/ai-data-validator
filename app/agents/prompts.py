EXTRACTION_PROMPT = """
You are a data extraction specialist. Extract structured data from the following unstructured text.
Target Schema: {schema_name}
Schema Fields: {schema_fields}

Raw Input:
{raw_input}

Instructions:
1. Extract all relevant fields matching the schema
2. Infer missing values where possible (e.g., calculate totals)
3. Standardize formats (dates as YYYY-MM-DD, currency codes as 3-letter ISO)
4. Return ONLY valid JSON matching the schema structure

Output JSON:
"""

CORRECTION_PROMPT = """
You are a data correction specialist. Fix the validation errors in this extracted data.

Original Extracted Data:
{extracted_data}

Validation Errors:
{validation_errors}

Schema Requirements:
{schema_fields}

Instructions:
1. Analyze each error and determine the correction
2. Apply fixes while preserving valid data
3. If a field cannot be corrected, use a sensible default or null
4. Return the corrected JSON

Corrected JSON:
"""