from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict
from datetime import date, datetime


# Quote Schemas
class QuoteItem(BaseModel):
    description: str
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)


class QuoteRequest(BaseModel):
    client_name: str
    client_address: str
    client_city: Optional[str] = None
    items: Dict[str, QuoteItem]


class QuoteUpdateRequest(BaseModel):
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    client_city: Optional[str] = None
    items: Optional[Dict[str, QuoteItem]] = None
    status: Optional[str] = None


class QuoteOut(BaseModel):
    client_quote_number: Optional[str] = ""
    client_name: Optional[str] = ""
    client_address: Optional[str] = ""
    client_date: Optional[datetime] = None
    total_amount: Optional[float] = 0.0
    cached_pdf_path: Optional[str] = ""
    convert: Optional[str] = ""

    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceItem(BaseModel):
    description: str
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)


class InvoiceRequest(BaseModel):
    client_name: str
    client_address: str
    client_number: Optional[str] = None
    client_rate: Optional[float] = None
    items: Dict[str, InvoiceItem]



class InvoiceFromQuoteRequest(BaseModel):
    source_quote_id: int
    client_number: Optional[str] = None


class InvoiceOut(BaseModel):
    invoice_number: Optional[str] = ""
    client_name: Optional[str] = ""
    client_address: Optional[str] = ""
    client_date: Optional[datetime] = None
    invoice: Optional[str] = ""

    class Config:
        from_attributes = True


# Customer Reuse Schemas
class QuoteCustomerReuse(BaseModel):
    client_name: Optional[str] = None
    client_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InvoiceCustomerReuse(BaseModel):
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    client_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Payment Schemas
class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None


class PaymentOut(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_date: date
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: str
    description: Optional[str] = None
    entry_date: Optional[date] = None
    quote_id: Optional[int] = None
    invoice_id: Optional[int] = None


class ProfitLossEntryOut(BaseModel):
    id: int
    quote_id: Optional[int] = None
    invoice_id: Optional[int] = None
    entry_type: str
    category: str
    description: Optional[str] = None
    amount: float
    entry_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfitLossSummaryOut(BaseModel):
    total_income: float
    total_expenses: float
    net_profit_loss: float