from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from pydantic import BaseModel
from typing import Dict

class QuoteOut(BaseModel):
    client_name: str
    client_address: str
    client_date: date
    client_quote_pdf: Optional[str] = None
    client_quote_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InvoiceOut(BaseModel):
    client_name: str
    client_address: str
    client_date: date
    client_number: Optional[str] = None
    client_invoice_pdf: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class QuoteItem(BaseModel):
    description: str
    quantity: float
    unit_price: float


class QuoteRequest(BaseModel):
    client_name: str
    client_address: str
    client_city: str
    items: Dict[str, QuoteItem]


class ReceiptItem(BaseModel):
    description: str
    quantity: float
    unit_price: float


class ReceiptRequest(BaseModel):
    client_name: str
    client_address: str
    client_number: str
    client_rate: float
    items: Dict[str, ReceiptItem]