
from pydantic import BaseModel
from typing import List

#User 
class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Invoice
class InvoiceItemCreate(BaseModel):
    product_service_type: str
    description: str
    unit_price: float
    quantity: int
    discount: float
    vat_percentage: float

class InvoiceCreate(BaseModel):
    invoice_date: str
    customer_id: str
    due_date: str
    gross_discount: float
    gross_total: float
    terms_and_conditions: str
    invoiceItems: List[InvoiceItemCreate]

