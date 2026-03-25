from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Quotes, Invoices
from app.schemas import QuoteCustomerReuse, InvoiceCustomerReuse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/quotes", response_model=list[QuoteCustomerReuse])
def get_quote_customers(db: Session = Depends(get_db)):
    """
    Return unique customer details from previous quotes
    for reuse when creating a new quote.
    """
    quotes = (
        db.query(Quotes)
        .order_by(Quotes.id.desc())
        .all()
    )

    seen = set()
    customers = []

    for quote in quotes:
        name = (quote.client_name or "").strip()
        address = (quote.client_address or "").strip()

        # skip empty records
        if not name and not address:
            continue

        # unique key
        key = (name.lower(), address.lower())

        if key in seen:
            continue

        seen.add(key)

        customers.append(
            QuoteCustomerReuse(
                client_name=name,
                client_address=address
            )
        )

    return customers


@router.get("/invoices", response_model=list[InvoiceCustomerReuse])
def get_invoice_customers(db: Session = Depends(get_db)):
    """
    Return unique customer details from previous invoices
    for reuse when creating a new invoice.
    """
    invoices = (
        db.query(Invoices)
        .order_by(Invoices.id.desc())
        .all()
    )

    seen = set()
    customers = []

    for invoice in invoices:
        name = (invoice.client_name or "").strip()
        address = (invoice.client_address or "").strip()
        number = (invoice.client_number or "").strip()

        # skip fully empty rows
        if not name and not address and not number:
            continue

        # unique key
        key = (
            name.lower(),
            address.lower(),
            number.lower()
        )

        if key in seen:
            continue

        seen.add(key)

        customers.append(
            InvoiceCustomerReuse(
                client_name=name,
                client_address=address,
                client_number=number
            )
        )

    return customers