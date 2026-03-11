from fastapi.responses import FileResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, PatternFill
import datetime
from .pdf_conversion import excel2pdf, autofit_columns
from app.schemas import ReceiptRequest
from .quote import slugify_name
from app.database import get_db
from fastapi import APIRouter, Depends
import re
from app.models import Invoices
import os

router = APIRouter()

@router.post("/invoice")
def receipt(data: ReceiptRequest, db = Depends(get_db)):
    new_invoice = Invoices(
        client_name=data.client_name,
        client_address=data.client_address,
        client_number=data.client_number,
        client_date=datetime.date.today(),
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    # generate global sequential invoice number
    slug = slugify_name(data.client_name)
    sequence = f"{new_invoice.id:04d}"
    invoice_number = f"{slug}-{sequence}"

    # generate invoice pdf
    os.makedirs("generated_invoices", exist_ok=True)
    pdf_path = f"generated_invoices/{invoice_number}.pdf"

    # Defalut font style
    font = Font(bold=True, color="0000FF", name="Arial")

    # Block fill
    fill = PatternFill(start_color="FF98AFC7", end_color="FF98AFC7", fill_type="solid")

    header_fill = PatternFill(start_color="3960FA", end_color="3960FA", fill_type="solid")
    tab_fill1 = PatternFill(start_color="C7D1F7", end_color="C7D1F7", fill_type="solid")
    tab_fill2 = PatternFill(start_color="93A2DC", end_color="93A2DC", fill_type="solid")


    wb = Workbook()
    ws = wb.active
    ws.title = "City Light Receipt"
    ws["A1"] = "Invoice"
    ws["A1"].font = Font(size=16, bold=True, color="0000FF")
    ws.merge_cells("A1:F1")

    ws["A2"] = f"Date: {datetime.date.today().strftime('%Y-%m-%d')}"
    

    ws["A4"] = "Customer Details"
    ws["A4"].font = font
    ws["A5"] = data.client_name
    ws ["A6"] = data.client_address
    ws["A7"] = data.client_number

    ws.merge_cells("A6:D6")
    ws.merge_cells("A7:D7")
    ws.merge_cells("A8:D8")
    ws.merge_cells("A9:D9")

    from openpyxl.styles import Alignment

    headers = [
        "#",
        "Item Description",
        "Quantity",
        "Price Ex.\nVat",
        "Price Inc.\nVat",
        "Total Price"
    ]

    wrap_align = Alignment(wrap_text=True, horizontal="center", vertical="center")

    ws["A11"].value = headers[0]
    ws["B11"].value = headers[1]
    ws.merge_cells("B11:D11")
    ws["F11"].value = headers[2]
    ws["G11"].value = headers[3]
    ws["H11"].value = headers[4]
    ws["I11"].value = headers[5]

    for col in ["A", "B", "F", "G", "H", "I"]:
        ws[f"{col}11"].alignment = wrap_align

    # Required: limit column width (forces wrap)
    ws.column_dimensions["G"].width = 12
    ws.column_dimensions["H"].width = 12

    # Required: force row height
    ws.row_dimensions[11].height = 26


    header_row = 11
    start_row =  header_row +1

    for i, item in enumerate(data.items.values(), start=1):
        row =  start_row + i - 1
        percentage_rate = data.client_rate / 100 + 1
        unit_price = round((item.unit_price * percentage_rate) ,2)
        total = total = round((item.quantity * unit_price), 2)
        labour_cost = item.unit_price + ((item.quantity - 1) * (item.unit_price - 100)) if item.quantity > 0 else 0 
        
        
        # A: Row number
        ws.cell(row=row, column=1, value= i)

        # B-D: Item Description
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=5)
        ws.cell(row=row, column=2, value=item.description)

        # F: Quantity
        try:
            if item.description.lower() == "tax total":
                ws.cell(row=row, column=6, value="")
            else:
                ws.cell(row=row, column=6, value=item.quantity)
        except Exception as e:
            return {"error": f"Quantity error: {e}"}
        
        # G: Net Unit Price
        try:
            if percentage_rate is not None and percentage_rate > 0:
                if item.description.lower() == "labour":
                    ws.cell(row=row, column=7, value="")
                else:
                    ws.cell(row=row, column=7, value=item.unit_price)
            else: 
                ws.delete_cols(7)
        except Exception as e:
            return {"error": f"Net Unit Price error: {e}"}

        # H: Unit Price
        try: 
            if percentage_rate is not None and percentage_rate > 0: 
                if item.description.lower() == "labour":
                    ws.cell(row=row, column=8, value=item.unit_price)
                else:
                    ws.cell(row=row, column=8, value=unit_price)
            else:
                ws.cell(row=row, column=8, value=item.unit_price)
        except Exception as e:
            return {"error": f"Unit price error: {e}"}

        # I: Total Price 
        try :
            if item.description.lower() == "labour":
                ws.cell(row=row, column=9, value=labour_cost)
            elif item.description.lower() == "tax total":
                ws.cell(row=row, column=9, value=item.unit_price * 1.1)
            else:
                ws.cell(row=row, column=9, value=total)
        except Exception as e:
            return {"error": f"Total price error: {e}"}
        
    # Add data rows
    start_row = 11 
    current_row = start_row + len(data.items) + 1

    for row in range(start_row + 1, current_row):
        for col in range(2, 4):
                ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col)

    grand_total_cell = ws.cell(row=current_row, column=8, value="Grand Total")
    grand_total_cell.font = Font(bold=True)
    grand_total_cell.alignment = Alignment(horizontal="right")

    total_coumn_letter = get_column_letter(9)
    grand_total_formula = f"=SUM({total_coumn_letter}{start_row + 1}:{total_coumn_letter}{current_row - 1})"
    totals = ws.cell(row=current_row, column=9, value=grand_total_formula)
    totals.font = Font(bold=True)
    ws.cell(row=current_row, column=9).number_format = '"R"#,##0.00'

    for col in range(1, 10):
        ws.cell(11, col).font = Font(bold=True)
        ws.cell(11, col).alignment = Alignment(horizontal="center")
        ws.cell(11, col).fill = header_fill


    # fill table rows color
    for row in range(start_row + 1, current_row, 2):
        for col in range(1, 10):
            ws.cell(row, col).fill = tab_fill1
    for row in range(start_row + 2, current_row, 2):
        for col in range(1, 10):
            ws.cell(row, col).fill = tab_fill2
        
    #ws.add_table(tab)
    # Autofit only table area
    autofit_columns(
        ws,
        start_row=11,
        end_row=current_row + 1,
        start_col=1,
        end_col=1
    )
    autofit_columns(
        ws,
        start_row=11, 
        end_row=current_row + 1,
        start_col=9,
        end_col=9
    )

    # banking details
    ws["A" + str(current_row + 2)] = "Banking Details"
    ws["A" + str(current_row + 2)].font = font
    ws["A" + str(current_row + 3)] = "Bank: Bidvest Bank Alliance"
    ws["A" + str(current_row + 4)] = "Branch Code: 683000"
    ws["A" + str(current_row + 5)] = "Account Holder: Leeroy Antony Muzondi"
    ws["A" + str(current_row + 6)] = "Account Number: 7860 2801 824"
    ws["A" + str(current_row + 7)] = "Account Type: Current"
    ws["A" + str(current_row + 9)] = "Note: Make sure the bank is BidvestBank Alliance and the Branch Code is 683000."

    ws.merge_cells(f"A{current_row + 2}:H{current_row + 2}")
    ws.merge_cells(f"A{current_row + 3}:H{current_row + 3}")
    ws.merge_cells(f"A{current_row + 4}:H{current_row + 4}")
    ws.merge_cells(f"A{current_row + 5}:H{current_row + 5}")
    ws.merge_cells(f"A{current_row + 6}:H{current_row + 6}")
    ws.merge_cells(f"A{current_row + 7}:H{current_row + 7}")
    ws.merge_cells(f"A{current_row + 9}:H{current_row + 9}")

    ws["A" + str(current_row + 11)].font = font
    ws["A" + str(current_row + 9)].font = Font(bold=False, italic=True)
    ws["A" + str(current_row + 9)].alignment = Alignment(wrap_text=True,horizontal="center")
    
    excel_path = f"generated_invoices/{invoice_number}.xlsx"
    wb.save(excel_path)
    pdf = excel2pdf(excel_path)
    pdf_path = f"generated_invoices/{invoice_number}.pdf"
    new_invoice.invoice_number = invoice_number
    new_invoice.client_invoice_pdf = pdf_path
    db.commit()
    db.refresh(new_invoice)
    return FileResponse(
        path=pdf_path,
        media_type='application/pdf',
        filename=f"{invoice_number} - invoice.pdf"
    )

