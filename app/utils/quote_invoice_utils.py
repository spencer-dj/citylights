from datetime import date, timedelta
from app.schemas import QuoteRequest, InvoiceRequest
import re

def slugify_name(name: str):
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', '', name)
    return name

# Calculate quute totals
def calculate_quote_totals(items: dict):
    subtotal = 0
    structured_items = []

    for item in items.values():
        unit_price = item.unit_price * 1.2
        line_total = item.quantity * unit_price
        subtotal += line_total

        structured_items.append({
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "line_total": line_total 
        })
    return subtotal, structured_items

# Build Quote Payload
def build_quote_payload(data: QuoteRequest, quote_number: str):
    total_amount, structured_items = calculate_quote_totals(data.items)

    payload = {
        "quote_number": quote_number,
        "client_name": data.client_name,
        "client_address": data.client_address,
        "client_city": data.client_city,
        "date_created": date.today().isoformat(),
        "valid_until": (date.today() + timedelta(days=14)).isoformat(),
        "currency": "R",
        "items": structured_items,
        "subtotal": total_amount,
        "tax": 0,
        "discount": 0,
        "total": total_amount,
        "notes": "Quotation valid for 14 days"
    }

    return payload, total_amount

def calculate_invoice_totals(data: InvoiceRequest):
    percentage_rate = data.client_rate / 100 + 1
    subtotal = 0
    structured_items = []

    for item in data.items.values():
        unit_price_ex_vat = round(item.unit_price, 2)
        unit_price_inc_vat = round(item.unit_price * percentage_rate, 2)
        line_total = round(item.quantity * unit_price_inc_vat, 2)

        if "labour" in item.description.lower():
            line_total = round(
                item.unit_price + ((item.quantity - 1) * (item.unit_price - 100))
                if item.quantity > 1 else item.unit_price,
                2
            )

        elif "tax total" in item.description.lower():
            line_total = round(item.unit_price * 1.1, 2)

        structured_items.append({
            "description": item.description,
            "quantity": item.quantity,
            "unit_price_ex_vat": unit_price_ex_vat,
            "unit_price_inc_vat": unit_price_inc_vat,
            "line_total": line_total
        })

        subtotal += line_total

    return round(subtotal, 2), structured_items


def build_invoice_payload(data: InvoiceRequest, invoice_number: str):
    total_amount, structured_items = calculate_invoice_totals(data)

    payload = {
        "invoice_number": invoice_number,
        "client_name": data.client_name,
        "client_address": data.client_address,
        "client_number": data.client_number,
        "date_created": date.today().isoformat(),
        "currency": "R",
        "client_rate": data.client_rate,
        "items": structured_items,
        "subtotal": total_amount,
        "tax": 0,
        "discount": 0,
        "total": total_amount,
        "notes": "Finalized invoice"
    }

    return payload, total_amount
