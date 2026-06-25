from database.db import get_db_connection

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# GENERATE PDF(HELPER FUNCTION)
def generate_invoice_pdf(invoice_id, user_id):

    conn = get_db_connection()

    invoice = conn.execute(
        """
        SELECT invoices.*,
               customers.customer_name
        FROM invoices
        JOIN customers
        ON invoices.customer_id = customers.id
        WHERE invoices.id = ?
        """,
        (invoice_id,)
    ).fetchone()

    items = conn.execute(
        """
        SELECT invoice_items.*,
               products.product_name
        FROM invoice_items
        JOIN products
        ON invoice_items.product_id = products.id
        WHERE invoice_id = ?
        """,
        (invoice_id,)
    ).fetchall()

    business = conn.execute(
        """
        SELECT *
        FROM business_settings
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    invoice_id = int(invoice_id)
    pdf_path = f"INV{invoice_id:04d}.pdf"

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    content = []

    # TITLE
    content.append(
        Paragraph(
            "SMART INVOICE",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 10))

    # BUSINESS DETAILS
    if business:

        content.append(
            Paragraph(
                business["shop_name"] or "",
                styles["Heading2"]
            )
        )

        content.append(
            Paragraph(
                business["address"] or "",
                styles["Normal"]
            )
        )

        content.append(
            Paragraph(
                f"Phone: {business['phone'] or ''}",
                styles["Normal"]
            )
        )

        content.append(
            Paragraph(
                business["email"] or "",
                styles["Normal"]
            )
        )

        if business["gst_number"]:

            content.append(
                Paragraph(
                    f"GST No: {business['gst_number']}",
                    styles["Normal"]
                )
            )

    content.append(Spacer(1, 15))

    # INVOICE INFO
    content.append(
        Paragraph(
            f"Invoice ID : INV{invoice['id']:04d}",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            f"Invoice Date : {invoice['created_at']}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"Customer Name : {invoice['customer_name']}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 20))

    # ITEMS TABLE
    table_data = [
        ["Product", "Qty", "Price", "GST %"]
    ]

    for item in items:

        table_data.append([
            item["product_name"],
            str(item["quantity"]),
            f"Rs. {item['price']}",
            f"{item['gst_percentage']}%"
        ])

    table = Table(
        table_data,
        colWidths=[220, 60, 100, 80]
    )

    table.setStyle(
        TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("ALIGN", (1, 1), (-1, -1), "CENTER"),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        ])
    )

    content.append(table)

    content.append(Spacer(1, 20))

    # TOTALS
    content.append(
        Paragraph(
            f"Subtotal : Rs. {invoice['subtotal']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"GST Amount : Rs. {invoice['gst_amount']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Discount ({invoice['discount_percent']}%) : Rs. {invoice['discount_amount']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Grand Total : Rs. {invoice['grand_total']}",
            styles["Heading1"]
        )
    )

    content.append(Spacer(1, 20))

    # FOOTER
    content.append(
        Paragraph(
            "Thank You For Shopping With Us!",
            styles["Italic"]
        )
    )

    doc.build(content)

    return pdf_path
