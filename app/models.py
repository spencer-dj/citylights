from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from sqlalchemy import Computed

class Quotes(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, index=True)
    client_address = Column(String, index=True)
    client_quote_pdf = Column(String, nullable=True)
    client_date = Column(DateTime, index=True)
    client_quote_number = Column(String, nullable=True)
    
    
class Invoices(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, index=True)
    client_number = Column(String, index=True)
    client_address = Column(String, index=True)
    client_invoice_pdf = Column(String, nullable=True)
    client_date = Column(DateTime, index=True)

