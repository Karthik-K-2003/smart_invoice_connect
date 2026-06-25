from flask import render_template, session, redirect, request, send_file, flash, url_for
from database.db import get_db_connection
from blueprints.invoices import invoices_bp
import json

from utils.pdf_generator import generate_invoice_pdf


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


# Recommendation
@invoices_bp.route("/recommendations/<int:product_id>")
def recommendations(product_id):

    if "user_id" not in session:
        return {"products": []}

    exclude = request.args.get("exclude", "")
    exclude_ids = []
    if exclude:
        exclude_ids = exclude.split(",")

    conn = get_db_connection()

    business = conn.execute(
        """
        SELECT shop_type
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if not business or business["shop_type"] not in [
        "Clothing Store",
        "Electronics Store"
    ]:
        conn.close()
        return {"products": []}

    invoice_ids = conn.execute(
        """
        SELECT DISTINCT invoice_id
        FROM invoice_items
        WHERE product_id = ?
        """,
        (product_id,)
    ).fetchall()

    if not invoice_ids:
        conn.close()
        return {"products": []}

    invoice_list = [str(row["invoice_id"]) for row in invoice_ids]
    placeholders = ",".join(["?"] * len(invoice_list))

    query = f"""
    SELECT
        products.*,
        COUNT(*) AS purchase_count
    FROM invoice_items
    JOIN products
        ON invoice_items.product_id = products.id
    WHERE invoice_items.invoice_id IN ({placeholders})
    AND invoice_items.product_id != ?
    AND products.user_id = ?
    """

    params = invoice_list + [product_id, session["user_id"]]

    if exclude_ids:

        exclude_placeholders = ",".join(["?"] * len(exclude_ids))

        query += f"""
        AND products.id NOT IN ({exclude_placeholders})
        """

        params += exclude_ids

    query += """
    GROUP BY products.id
    ORDER BY purchase_count DESC
    LIMIT 4
    """

    recommendations = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return {
        "products": [
            dict(product)
            for product in recommendations
        ]
    }


# Add Save
@invoices_bp.route("/invoices/save", methods=["POST"])
def save_invoice():

    if "user_id" not in session:
        return redirect("/login")

    customer_id = request.form["customer_id"]
    subtotal = request.form["subtotal"]
    gst_amount = request.form["gst_amount"]
    grand_total = request.form["grand_total"]
    discount_percent = request.form["discount_percent"]
    discount_amount = request.form["discount_amount"]

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
            discount_percent,
            discount_amount,
            grand_total,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            customer_id,
            subtotal,
            gst_amount,
            discount_percent,
            discount_amount,
            grand_total,
            "Pending"
        )
    )

    invoice_id = cursor.lastrowid

    for item in invoice_items:

        if item["quantity"] <= 0:
            flash(
                "Quantity must be greater than 0!",
                "error"
            )
            conn.close()
            return redirect("/invoices")

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
    flash("Invoice deleted successfully!", "success")
    conn.close()

    return redirect("/invoices/history")


# Download PDF
@invoices_bp.route("/invoices/pdf/<int:invoice_id>")
def download_pdf(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

    pdf_path = generate_invoice_pdf(invoice_id, session["user_id"])

    return send_file(
        pdf_path,
        as_attachment=True
    )
