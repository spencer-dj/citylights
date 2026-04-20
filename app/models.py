from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, ForeignKey
from .database import Base
from datetime import datetime

class Quotes(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    client_quote_number = Column(String, nullable=True)
    client_date = Column(DateTime, index=True)
    client_name = Column(String, index=True)
    client_address = Column(String, index=True)
    total_amount = Column(Float, nullable=True)
    status = Column(String, nullable=True, default="pending")
    quote_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
    cached_pdf_path = Column(String, nullable=True)
    
    
    
class Invoices(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client_number = Column(String, index=True)
    source_quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)
    client_name = Column(String, index=True)
    client_address = Column(String, index=True)
    client_date = Column(DateTime, index=True)
    total_amount = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="pending")
    is_finalized = Column(Boolean, nullable=False, default=False)
    invoice_data = Column(JSON, nullable=True)
    final_pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime, index=True)
    invoice_number = Column(String, nullable=False, unique=True, index=True)
    