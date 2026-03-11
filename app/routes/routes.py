import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Invoices, Quotes
from app.schemas import InvoiceOut, QuoteOut
from typing import List
from fastapi import Query
from datetime import date, timedelta
from fastapi.responses import FileResponse
import os

router = APIRouter()

QUOTE_PDF_FOLDER = "generated_quotes"
INVOICE_PDF_FOLDER = "generated_invoices"


@router.get("/quote_db", response_model=List[QuoteOut])
def get_all_quotes(
    db: Session = Depends(get_db),
    limit: int = 5,
    start_date: date = Query(None),
    end_date: date = Query(None)
):
    query = db.query(Quotes)

    # Filter by date range if provided
    if start_date and end_date:
        query = query.filter(Quotes.client_date >= start_date, Quotes.client_date <= end_date)
    else:
        # Default: last month
        last_month = date.today() - timedelta(days=30)
        query = query.filter(Quotes.client_date >= last_month)

    # Order by newest first
    query = query.order_by(Quotes.client_date.desc())

    # Limit the number of rows returned
    qoutes = query.limit(limit).all()
    return qoutes

# Invoice endpoint
@router.get("/invoice_db", response_model=List[InvoiceOut])
def get_all_invoices(
    db: Session = Depends(get_db),
    limit: int = 5, 
    start_date: date = Query(None),
    end_date: date = Query(None)
):
    query = db.query(Invoices)

    # Filter by date range if provided
    if start_date and end_date:
        query = query.filter(Invoices.client_date >= start_date, Invoices.client_date <= end_date)
    else:
        # Default: last month
        last_month = date.today() - timedelta(days=30)
        query = query.filter(Invoices.client_date >= last_month)

    # Order by newest first
    query = query.order_by(Invoices.client_date.desc())

    # Limit number of rows
    invoices = query.limit(limit).all()
    return invoices

@router.get("/pdf/{type}/{filename}")
def serve_pdf(type: str, filename: str):
    """
    Serve PDFs for quotes or invoices.
    type: "quote" or "invoice"
    filename: e.g., quote1.pdf or invoice5.pdf
    """
    if type == "quote":
        path = os.path.join(QUOTE_PDF_FOLDER, filename)
    elif type == "invoice":
        path = os.path.join(INVOICE_PDF_FOLDER, filename)
    else:
        return {"detail": "Invalid type"}

    if os.path.exists(path):
        return FileResponse(path, media_type="application/pdf")
    else:
        return {"detail": "not found"}