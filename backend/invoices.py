from datetime import timedelta, timezone
from fpdf import FPDF

SHOP_NAME = "Shop Manager Demo Store"
IST = timezone(timedelta(hours=5, minutes=30))


def safe(text) -> str:
    # The built-in PDF font only supports basic characters, so replace anything else
    return str(text).encode("latin-1", "replace").decode("latin-1")


def money(value) -> str:
    return f"Rs. {value:,.2f}"


def build_invoice_pdf(sale) -> bytes:
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, SHOP_NAME, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Invoice #{sale.id}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Date: {sale.created_at.astimezone(IST):%d %b %Y, %I:%M %p}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Customer: {safe(sale.customer_name or 'Walk-in customer')}", new_x="LMARGIN", new_y="NEXT")
    if sale.created_by:
        pdf.cell(0, 7, f"Served by: {safe(sale.created_by.username)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Table header
    widths = [90, 25, 35, 40]
    headers = ["Item", "Qty", "Unit price", "Amount"]
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(241, 245, 249)
    for width, header in zip(widths, headers):
        align = "L" if header == "Item" else "R"
        pdf.cell(width, 9, header, border=1, align=align, fill=True)
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 11)
    for item in sale.items:
        pdf.cell(widths[0], 8, safe(item.product.name), border=1)
        pdf.cell(widths[1], 8, str(item.quantity), border=1, align="R")
        pdf.cell(widths[2], 8, money(item.unit_price), border=1, align="R")
        pdf.cell(widths[3], 8, money(item.line_total), border=1, align="R")
        pdf.ln()

    # Total
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(sum(widths[:3]), 10, "Total", border=1, align="R")
    pdf.cell(widths[3], 10, money(sale.total_amount), border=1, align="R")
    pdf.ln(16)

    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 7, "Thank you for your business!", align="C")

    return bytes(pdf.output())