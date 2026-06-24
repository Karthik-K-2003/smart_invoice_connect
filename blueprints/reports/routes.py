from flask import render_template, session, redirect, request, Response
from database.db import get_db_connection
from blueprints.reports import reports_bp

import csv
from io import StringIO

# Report Page


@reports_bp.route("/reports")
def reports():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    # FILTER VALUES
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")

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

    # OUTSTANDING REVENUE
    outstanding_revenue = conn.execute(
        """
        SELECT SUM(grand_total) AS revenue
        FROM invoices
        WHERE user_id = ?
        AND status = 'Pending'
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

    # SALES REPORT
    query = """
    SELECT invoices.*,
           customers.customer_name
    FROM invoices
    JOIN customers
    ON invoices.customer_id = customers.id
    WHERE invoices.user_id = ?
    """

    params = [session["user_id"]]

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
        "reports/reports.html",
        total_invoices=total_invoices["total"],
        collected_revenue=collected_revenue["revenue"] or 0,
        outstanding_revenue=outstanding_revenue["revenue"] or 0,
        total_customers=total_customers["total"],
        invoices=invoices,
        from_date=from_date,
        to_date=to_date,
        active_page="reports"
    )


# Export CSV
@reports_bp.route("/reports/export-csv")
def export_csv():

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
        ORDER BY invoices.id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Invoice ID",
        "Customer",
        "Amount",
        "Status",
        "Date"
    ])

    for invoice in invoices:

        writer.writerow([
            f"INV{invoice['id']:04d}",
            invoice["customer_name"],
            invoice["grand_total"],
            invoice["status"],
            str(invoice["created_at"]).split(" ")[0]
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=sales_report.csv"

    return response
