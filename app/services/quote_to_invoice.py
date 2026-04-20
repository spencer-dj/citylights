from datetime import datetime, date
from sqlalchemy.orm import Session
import json
from app.models import Quotes, Invoices
from app.utils.quote_invoice_utils import slugify_name
from app.services.invoice import generate_invoice_file


def _load_quote_data(quote):
    
    if isinstance(quote.quote_data, dict):
        return quote.quote_data

    if isinstance(quote.quote_data, str):
        return json.loads(quote.quote_data)

    raise ValueError("quote_data is not in a supported format")


def get_quote_by_id(quote_id: int, db: Session):
    return db.query(Quotes).filter(Quotes.id == quote_id).first()


def get_quote_amount_paid(quote, amount_paid: float | None = None) -> float:
    
    if amount_paid is None:
        return 0.0
    return float(amount_paid)


def can_convert_quote_to_invoice(quote, amount_paid: float):
    if not quote:
        return False, "Quote not found"

    if not quote.quote_data:
        return False, "Quote has no stored quote_data"

    if quote.status == "converted":
        return False, "Quote has already been converted to an invoice"

    if amount_paid <= 0:
        return False, "Quote must have some amount paid before conversion"

    return True, None


def build_invoice_payload_from_quote(quote, invoice_number: str, amount_paid: float):
    quote_data = _load_quote_data(quote)

    total_amount = float(quote_data.get("total", 0))
    subtotal = float(quote_data.get("subtotal", total_amount))
    tax = float(quote_data.get("tax", 0))
    discount = float(quote_data.get("discount", 0))
    client_number = quote_data.get("client_number")
    currency = quote_data.get("currency", "R")
    items = quote_data.get("items", [])
    converted_items = []

    for item in quote_data["items"]:
        unit_price = float(item.get("unit_price", 0))
        quantity = float(item.get("quantity", 0))

        unit_price_ex_vat = unit_price * 0.8
        unit_price_inc_vat = unit_price  
        line_total = unit_price * quantity

        converted_items.append({
            "description": item.get("description"),
            "quantity": quantity,
            "unit_price_ex_vat": round(unit_price_ex_vat, 2),
            "unit_price_inc_vat": round(unit_price_inc_vat, 2),
            "line_total": round(line_total, 2)
        })

    balance_due = total_amount - amount_paid
    if balance_due < 0:
        balance_due = 0.0

    payload = {
        "invoice_number": invoice_number,
        "source_quote_id": quote.id,
        "client_name": quote.client_name,
        "client_address": quote.client_address,
        "client_number": client_number,
        "date_created": date.today().isoformat(),
        "currency": currency,
        "items": converted_items,
        "subtotal": subtotal,
        "tax": tax,
        "discount": discount,
        "total": total_amount,
        "amount_paid": amount_paid,
        "balance_due": balance_due,
        "notes": "Generated from quote"
    }

    return payload, total_amount


def mark_quote_as_converted(quote, db: Session):
    quote.status = "converted"

    if hasattr(quote, "updated_at"):
        quote.updated_at = datetime.utcnow()

    db.add(quote)


def convert_quote_to_invoice(quote_id: int, amount_paid: float, db: Session):
    try:
        quote = get_quote_by_id(quote_id, db)
        paid = get_quote_amount_paid(quote, amount_paid)

        allowed, reason = can_convert_quote_to_invoice(quote, paid)
        if not allowed:
            return {"failed to convert quote": reason}

        # create invoice row first so we can get invoice id
        new_invoice = Invoices(
            source_quote_id=quote.id,
            client_name=quote.client_name,
            client_address=quote.client_address,
            client_number=_load_quote_data(quote).get("client_number"),
            client_date=date.today(),
            status="issued",
            is_finalized=True,
            created_at=datetime.utcnow()
        )

        db.add(new_invoice)
        db.flush()

        # generate invoice number from new invoice id
        slug = slugify_name(quote.client_name)
        sequence = f"{new_invoice.id:04d}"
        invoice_number = f"{slug}-{sequence}"

        payload, total_amount = build_invoice_payload_from_quote(
            quote=quote,
            invoice_number=invoice_number,
            amount_paid=paid
        )

        # generate final invoice pdf
        pdf_path = generate_invoice_file(payload, invoice_number)

        if not isinstance(pdf_path, str):
            db.rollback()
            return {"failed to convert quote": "Invoice PDF generation did not return a valid file path"}

        new_invoice.invoice_number = invoice_number
        new_invoice.total_amount = total_amount

        # If invoice_data column is JSON, this is correct:
        new_invoice.invoice_data = payload

        # If invoice_data is String instead, use:
        # new_invoice.invoice_data = json.dumps(payload)

        new_invoice.final_pdf_path = pdf_path

        mark_quote_as_converted(quote, db)

        db.commit()
        db.refresh(new_invoice)

        return {
            "message": "Quote converted to invoice successfully",
            "invoice_id": new_invoice.id,
            "invoice_number": new_invoice.invoice_number,
            "source_quote_id": quote.id,
            "final_pdf_path": new_invoice.final_pdf_path
        }

    except Exception as e:
        db.rollback()
        return {"failed to convert quote": str(e)}