from flask import render_template, session, redirect, request, send_file, flash
from database.db import get_db_connection
from blueprints.invoices import invoices_bp
import json

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os


@invoices_bp.route("/invoices")
def invoices():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    customers = conn.execute(
        """
        SELECT * FROM customers
        WHERE user_id = ?
        ORDER BY customer_name
        """,
        (session["user_id"],)
    ).fetchall()

    products = conn.execute(
        """
        SELECT * FROM products
        WHERE user_id = ?
        ORDER BY product_name
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "invoices/invoices.html",
        customers=customers,
        products=products,
        active_page="invoices"
    )


# Add Save
@invoices_bp.route("/invoices/save", methods=["POST"])
def save_invoice():

    if "user_id" not in session:
        return redirect("/login")

    customer_id = request.form["customer_id"]
    subtotal = request.form["subtotal"]
    gst_amount = request.form["gst_amount"]
    grand_total = request.form["grand_total"]

    if not customer_id:
        flash(
            "Please select a customer!",
            "error"
        )
        return redirect("/invoices")

    invoice_items = json.loads(
        request.form["invoice_items"]
    )

    if len(invoice_items) == 0:
        flash(
            "Please add at least one item!",
            "error"
        )
        return redirect("/invoices")

    conn = get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO invoices
        (
            user_id,
            customer_id,
            subtotal,
            gst_amount,
            grand_total,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            customer_id,
            subtotal,
            gst_amount,
            grand_total,
            "Pending"
        )
    )

    invoice_id = cursor.lastrowid

    if item["quantity"] <= 0:
        flash(
            "Quantity must be greater than 0!",
            "error"
        )
        conn.close()
        return redirect("/invoices")

    for item in invoice_items:

        conn.execute(
            """
            INSERT INTO invoice_items
            (
                invoice_id,
                product_id,
                quantity,
                price,
                gst_percentage
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                invoice_id,
                item["product_id"],
                item["quantity"],
                item["price"],
                item["gst_percentage"]
            )
        )

    conn.commit()
    conn.close()

    return redirect("/invoices/history")


# Invoice History
@invoices_bp.route("/invoices/history")
def invoice_history():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    search = request.args.get("search", "")
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")

    query = """
    SELECT invoices.*,
        customers.customer_name
    FROM invoices
    JOIN customers
    ON invoices.customer_id = customers.id
    WHERE invoices.user_id = ?
    """

    params = [session["user_id"]]

    if search:

        query += """
        AND (
            customers.customer_name LIKE ?
            OR invoices.id LIKE ?
        )
        """

        params.append(f"%{search}%")
        params.append(f"%{search}%")

    if from_date and to_date:

        query += """
        AND DATE(invoices.created_at)
        BETWEEN ? AND ?
        """

        params.append(from_date)
        params.append(to_date)

    query += """
    ORDER BY invoices.id DESC
    """

    invoices = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return render_template(
        "invoices/history.html",
        invoices=invoices,
        search=search,
        from_date=from_date,
        to_date=to_date,
        active_page="invoices"
    )


# View Invoice
@invoices_bp.route("/invoices/view/<int:invoice_id>")
def view_invoice(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

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
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "invoices/view_invoice.html",
        invoice=invoice,
        items=items,
        business=business,
        active_page="invoices"
    )


# Delete Invoice
@invoices_bp.route("/invoices/delete/<int:invoice_id>")
def delete_invoice(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM invoice_items WHERE invoice_id = ?",
        (invoice_id,)
    )

    conn.execute(
        "DELETE FROM invoices WHERE id = ?",
        (invoice_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/invoices/history")


# PDF Download
@invoices_bp.route("/invoices/pdf/<int:invoice_id>")
def download_pdf(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

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
        (session["user_id"],)
    ).fetchone()

    conn.close()

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

    return send_file(
        pdf_path,
        as_attachment=True
    )
