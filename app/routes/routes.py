import os
import json
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from typing import List
from datetime import date, timedelta
from app.database import get_db
from app.models import Invoices, Quotes
from app.schemas import InvoiceOut, QuoteOut
from app.utils.quote_invoice_utils import slugify_name, build_quote_payload, build_invoice_payload
from app.schemas import QuoteRequest, InvoiceRequest
from app.services.quote import generate_quote_file
from app.services.invoice import generate_invoice_file
from app.services.quote_to_invoice import convert_quote_to_invoice



router = APIRouter()

QUOTE_PDF_FOLDER = "generated_quotes"
INVOICE_PDF_FOLDER = "generated_invoices"


#@router.get("/quote_db", response_model=List[QuoteOut])
@router.get("/quote_db")
def get_all_quotes(
    db: Session = Depends(get_db),
    limit: int = 5,
    start_date: date = Query(None),
    end_date: date = Query(None)
):
    query = db.query(Quotes)

    if start_date and end_date:
        query = query.filter(
            Quotes.client_date >= start_date,
            Quotes.client_date <= end_date
        )
    else:
        last_month = date.today() - timedelta(days=30)
        query = query.filter(Quotes.client_date >= last_month)

    quotes = query.order_by(Quotes.client_date.desc()).limit(limit).all()

    return [
        {
            "id": q.id,
            "client_quote_number": q.client_quote_number or "",
            "client_name": q.client_name or "",
            "client_address": q.client_address or "",
            "client_date": q.client_date,
            "total_amount": float(q.total_amount or 0.0),
            "cached_pdf_path": q.cached_pdf_path or f"generated_quotes/{q.client_quote_number}.pdf" or "",
            "status": q.status or "pending"
        }
        for q in quotes
    ]

@router.get("/invoice_db", response_model=List[InvoiceOut])
def get_all_invoices(
        db: Session = Depends(get_db),
        limit: int = 5,
        start_date: date = Query(None),
        end_date: date = Query(None)
    ):
        try:
            query = db.query(Invoices)

            if start_date and end_date:
                query = query.filter(
                    Invoices.client_date >= start_date,
                    Invoices.client_date <= end_date
                )
            else:
                last_month = date.today() - timedelta(days=30)
                query = query.filter(Invoices.client_date >= last_month)

            invoices = query.order_by(Invoices.client_date.desc()).limit(limit).all()
            # create invoice number if not exists and return pdf path
            for inv in invoices:
                client_name = inv.client_name 
                id = inv.id
        
                if id < 10:
                    sequence = f"000{id}"
                elif id < 100:
                    sequence = f"00{id}"
                invoice_number = f"{slugify_name(client_name)}-{sequence}"
                pdf_path = f"generated_invoices/{invoice_number}.pdf"

            return({
                "invoice_number": inv.invoice_number or invoice_number or  "",
                "client_name": inv.client_name or "",
                "client_address": inv.client_address or "",
                "client_date": inv.client_date,
                "invoice": inv.final_pdf_path or pdf_path or ""
            }
            for inv in invoices
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))



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

# quote preview api
@router.post("/quote/preview")
def preview_quote(data: QuoteRequest):

    slug = slugify_name(data.client_name)

    preview_number = f"{slug}-preview"

    payload, _ = build_quote_payload(data, slug)

    pdf_path = generate_quote_file(payload, preview_number)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="quote-preview.pdf"
    )

@router.post("/quote/finalize")
def finalize_quote(data: QuoteRequest, db: Session = Depends(get_db)):
    try:
        new_quote = Quotes(
            client_name=data.client_name,
            client_address=data.client_address,
            client_date=date.today(),
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_quote)
        db.flush()   

        slug = slugify_name(data.client_name)
        sequence = f"{new_quote.id:04d}"

        quote_number = f"{slug}-{sequence}"

        payload, total_amount = build_quote_payload(data, quote_number)

        pdf_path = generate_quote_file(payload, quote_number)

        new_quote.client_quote_number = quote_number
        new_quote.total_amount = total_amount
        new_quote.quote_data = payload

        new_quote.cached_pdf_path = pdf_path
        new_quote.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(new_quote)

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{quote_number}-quote.pdf"
        )
    except Exception as e:
        db.rollback()
        return {"failed to finalize quote": str(e)}
    
@router.post("/invoice")
def create_invoice(data: InvoiceRequest, db: Session = Depends(get_db)):
    try:
        new_invoice = Invoices(
        client_name=data.client_name,
        client_address=data.client_address,
        client_number=data.client_number,
        client_date=date.today(),
        status="issued",
        is_finalized=True,
        created_at=datetime.utcnow()
        )

        db.add(new_invoice)
        db.flush()

        # Generate invoice number after getting DB id
        slug = slugify_name(data.client_name)
        sequence = f"{new_invoice.id:04d}"
        invoice_number = f"{slug}-{sequence}"

        payload, total_amount = build_invoice_payload(data, invoice_number)

        pdf_path = generate_invoice_file(payload, invoice_number)
        new_invoice.invoice_number = invoice_number
        new_invoice.total_amount = total_amount
        new_invoice.invoice_data = json.dumps(payload)
        new_invoice.final_pdf_path = pdf_path

        db.commit()
        db.refresh(new_invoice)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{invoice_number}-invoice.pdf"
        )

    except Exception as e:
        db.rollback()
        return {"failed to create invoice": str(e)}
    

# Quote to Invoice conversion route
@router.post("/quotes/{quote_id}/convert-to-invoice")
def convert_quote_to_invoice_route(
    quote_id: int,
    amount_paid: float = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    return convert_quote_to_invoice(quote_id, amount_paid, db)