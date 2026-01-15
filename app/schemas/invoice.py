from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from decimal import Decimal

class InvoiceLineItem(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: int = Field(..., ge=1)
    unit_price: Decimal = Field(..., ge=0, decimal_places=2)
    total: Decimal = Field(..., ge=0, decimal_places=2)

class InvoiceSchema(BaseModel):
    invoice_number: str = Field(..., pattern=r'^INV-\d{6,}$')
    vendor_name: str = Field(..., min_length=2, max_length=200)
    vendor_address: Optional[str] = None
    invoice_date: date
    due_date: date
    line_items: List[InvoiceLineItem] = Field(..., min_length=1)
    subtotal: Decimal = Field(..., ge=0)
    tax_amount: Decimal = Field(..., ge=0)
    total_amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD", pattern=r'^[A-Z]{3}$')
    
    @field_validator('due_date')
    @classmethod
    def due_date_after_invoice(cls, v, info):
        if 'invoice_date' in info.data and v < info.data['invoice_date']:
            raise ValueError('Due date must be after invoice date')
        return v

class SurveySchema(BaseModel):
    respondent_id: str = Field(..., min_length=1)
    submitted_at: str
    responses: dict = Field(..., min_length=1)
    completion_status: str = Field(..., pattern=r'^(complete|partial|abandoned)$')