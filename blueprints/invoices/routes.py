from flask import render_template, session, redirect
from database.db import get_db_connection
from blueprints.invoices import invoices_bp

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