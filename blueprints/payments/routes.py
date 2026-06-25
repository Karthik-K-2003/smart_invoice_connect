from flask import render_template, session, redirect, request, flash, current_app
from blueprints.payments import payments_bp
from database.db import get_db_connection

from flask_mail import Message
from utils.mail import mail
from utils.pdf_generator import generate_invoice_pdf
import os

# Payment
@payments_bp.route("/payments")
def payments():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    invoices = conn.execute(
        """
        SELECT invoices.*,
               customers.customer_name
        FROM invoices
        JOIN customers
        ON invoices.customer_id = customers.id
        WHERE invoices.user_id = ?
        AND invoices.status = 'Pending'
        ORDER BY invoices.id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "payments/payments.html",
        invoices=invoices,
        active_page="payments"
    )


#Mail to Customer
def send_invoice_email(customer_email, customer_name, pdf_path):

    msg = Message(
        subject="Payment Confirmation - Smart Invoice",
        recipients=[customer_email]
    )

    msg.body = f"""
        Dear {customer_name},

        Thank you for your payment.

        Your payment has been received successfully.

        Please find your invoice attached with this email.

        Regards,
        Smart Invoice
        """

    with current_app.open_resource(pdf_path) as pdf:

        msg.attach(
            os.path.basename(pdf_path),
            "application/pdf",
            pdf.read()
        )

    mail.send(msg)


# Save Payment
@payments_bp.route("/payments/save", methods=["POST"])
def save_payment():

    if "user_id" not in session:
        return redirect("/login")

    invoice_id = request.form["invoice_id"]

    if not invoice_id:
        flash(
            "Please select an invoice!",
            "error"
        )
        return redirect("/payments")

    payment_method = request.form["payment_method"]
    paid_amount = request.form["paid_amount"]

    if not payment_method:
        flash(
            "Please select a payment method!",
            "error"
        )

        return redirect("/payments")

    if float(paid_amount) <= 0:
        flash(
            "Paid amount must be greater than 0!",
            "error"
        )
        return redirect("/payments")

    conn = get_db_connection()

    invoice = conn.execute(
        """
        SELECT invoices.*,
            customers.customer_name,
            customers.email AS customer_email
        FROM invoices
        JOIN customers
        ON invoices.customer_id = customers.id
        WHERE invoices.id = ?
        """,
        (invoice_id,)
    ).fetchone()

    if float(paid_amount) != float(invoice["grand_total"]):
        conn.close()
        flash(
            "Paid amount must match invoice total!",
            "error"
        )

        return redirect("/payments")

    existing_payment = conn.execute(
        """
    SELECT *
    FROM payments
    WHERE invoice_id = ?
    """,
        (invoice_id,)
    ).fetchone()

    if existing_payment:

        conn.close()

        flash(
            "Payment already recorded for this invoice!",
            "error"
        )

        return redirect("/payments")

    conn.execute(
        """
        INSERT INTO payments
        (
            invoice_id,
            user_id,
            payment_method,
            paid_amount
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            invoice_id,
            session["user_id"],
            payment_method,
            paid_amount
        )
    )

    conn.execute(
        """
        UPDATE invoices
        SET status = 'Paid'
        WHERE id = ?
        """,
        (invoice_id,)
    )

    conn.commit()

    pdf_path = generate_invoice_pdf(invoice_id, session["user_id"])

    send_invoice_email(invoice["customer_email"], invoice["customer_name"], pdf_path)

    conn.close()

    flash(
        "Payment recorded successfully!",
        "success"
    )

    return redirect("/payments")


# Payment History
@payments_bp.route("/payments/history")
def payment_history():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    search = request.args.get("search", "")
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")

    query = """
    SELECT payments.*,
           invoices.id AS invoice_number,
           customers.customer_name
    FROM payments
    JOIN invoices
    ON payments.invoice_id = invoices.id
    JOIN customers
    ON invoices.customer_id = customers.id
    WHERE payments.user_id = ?
    """

    params = [session["user_id"]]

    # SEARCH
    if search:

        query += """
        AND (
            customers.customer_name LIKE ?
            OR invoices.id LIKE ?
        )
        """

        params.append(f"%{search}%")
        params.append(f"%{search}%")

    # DATE FILTER
    if from_date:

        query += """
        AND DATE(payments.payment_date) >= ?
        """

        params.append(from_date)

    if to_date:

        query += """
        AND DATE(payments.payment_date) <= ?
        """

        params.append(to_date)

    query += """
    ORDER BY payments.id DESC
    """

    payments = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return render_template(
        "payments/history.html",
        payments=payments,
        search=search,
        from_date=from_date,
        to_date=to_date,
        active_page="payments"
    )
