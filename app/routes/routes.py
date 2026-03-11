import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from typing import List
from datetime import date, timedelta

from app.database import get_db
from app.models import Invoices, Quotes
from app.schemas import InvoiceOut, QuoteOut

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

    if start_date and end_date:
        query = query.filter(Quotes.client_date >= start_date, Quotes.client_date <= end_date)
    else:
        last_month = date.today() - timedelta(days=30)
        query = query.filter(Quotes.client_date >= last_month)

    query = query.order_by(Quotes.client_date.desc())
    quotes = query.limit(limit).all()
    return quotes


@router.get("/invoice_db", response_model=List[InvoiceOut])
def get_all_invoices(
    db: Session = Depends(get_db),
    limit: int = 5,
    start_date: date = Query(None),
    end_date: date = Query(None)
):
    query = db.query(Invoices)

    if start_date and end_date:
        query = query.filter(Invoices.client_date >= start_date, Invoices.client_date <= end_date)
    else:
        last_month = date.today() - timedelta(days=30)
        query = query.filter(Invoices.client_date >= last_month)

    query = query.order_by(Invoices.client_date.desc())
    invoices = query.limit(limit).all()
    return invoices


@router.get("/pdf/{type}/{filename}")
def serve_pdf(type: str, filename: str):
    filename = os.path.basename(filename)

    if type == "quote":
        path = os.path.join(QUOTE_PDF_FOLDER, filename)
    elif type == "invoice":
        path = os.path.join(INVOICE_PDF_FOLDER, filename)
    else:
        raise HTTPException(status_code=400, detail="Invalid type")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Accept-Ranges": "bytes"
        }
    )