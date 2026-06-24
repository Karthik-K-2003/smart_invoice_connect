from flask import render_template, redirect, session
from blueprints.dashboard import dashboard_bp
from database.db import get_db_connection


@dashboard_bp.route("/dashboard")
def dashboard():

    # CHECK USER LOGIN
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    #TOTAL PRODUCTS
    total_products = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM products
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    # TOTAL CUSTOMERS
    total_customers = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM customers
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    # TOTAL INVOICES
    total_invoices = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM invoices
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    # COLLECTED REVENUE
    collected_revenue = conn.execute(
        """
        SELECT SUM(grand_total) AS revenue
        FROM invoices
        WHERE user_id = ?
        AND status = 'Paid'
        """,
        (session["user_id"],)
    ).fetchone()

    #PENDING INVOICES
    pending_invoices = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM invoices
        WHERE user_id = ?
        AND status = 'Pending'
        """,
        (session["user_id"],)
    ).fetchone()

    #PAID INVOICES
    paid_invoices = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM invoices
        WHERE user_id = ?
        AND status = 'Paid'
        """,
        (session["user_id"],)
    ).fetchone()

    #PENDING REVENUE
    pending_revenue = conn.execute(
        """
        SELECT SUM(grand_total) AS total
        FROM invoices
        WHERE user_id = ?
        AND status = 'Pending'
        """,
        (session["user_id"],)
    ).fetchone()

    recent_invoices = conn.execute(
        """
        SELECT invoices.*,
            customers.customer_name
        FROM invoices
        JOIN customers
        ON invoices.customer_id = customers.id
        WHERE invoices.user_id = ?
        ORDER BY invoices.id DESC
        LIMIT 5
        """,
        (session["user_id"],)
    ).fetchall()

    recent_payments = conn.execute(
        """
        SELECT payments.*,
            invoices.id AS invoice_number
        FROM payments
        JOIN invoices
        ON payments.invoice_id = invoices.id
        WHERE payments.user_id = ?
        ORDER BY payments.id DESC
        LIMIT 3
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    shop_type = session.get("shop_type")

    return render_template(
        "dashboard/dashboard.html",
        shop_type=shop_type,
        total_products=total_products["total"],
        total_customers=total_customers["total"],
        total_invoices=total_invoices["total"],
        collected_revenue=collected_revenue["revenue"] or 0,
        pending_invoices=pending_invoices["total"],
        paid_invoices=paid_invoices["total"],
        pending_revenue=pending_revenue["total"] or 0,
        recent_invoices=recent_invoices,
        recent_payments=recent_payments,
        active_page="dashboard"
    )
