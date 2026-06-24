from flask import render_template, session, redirect, request, Response, send_file
from database.db import get_db_connection
from blueprints.reports import reports_bp

from datetime import datetime
import csv
import io

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


# Report
@reports_bp.route("/reports")
def reports():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")
    status = request.args.get("status", "")

    total_invoices = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM invoices
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()["total"]

    paid_count = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM invoices
        WHERE user_id = ?
        AND status='Paid'
        """,
        (session["user_id"],)
    ).fetchone()["total"]

    pending_count = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM invoices
        WHERE user_id = ?
        AND status='Pending'
        """,
        (session["user_id"],)
    ).fetchone()["total"]

    collected_revenue = conn.execute(
        """
        SELECT SUM(grand_total) AS revenue
        FROM invoices
        WHERE user_id = ?
        AND status='Paid'
        """,
        (session["user_id"],)
    ).fetchone()["revenue"] or 0

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

    if status:

        query += """
        AND invoices.status = ?
        """

        params.append(status)

    query += """
    ORDER BY invoices.id DESC
    """

    invoices = conn.execute(
        query,
        params
    ).fetchall()

    report_total = sum(
        invoice["grand_total"]
        for invoice in invoices
    )

    sales_chart = conn.execute(
        """
        SELECT
            DATE(created_at) AS report_date,
            SUM(grand_total) AS total
        FROM invoices
        WHERE user_id = ?
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
        """,
        (session["user_id"],)
    ).fetchall()

    chart_labels = [
        row["report_date"]
        for row in sales_chart
    ]

    chart_values = [
        row["total"]
        for row in sales_chart
    ]

    conn.close()

    return render_template(
        "reports/reports.html",
        invoices=invoices,
        total_invoices=total_invoices,
        paid_count=paid_count,
        pending_count=pending_count,
        collected_revenue=collected_revenue,
        report_total=report_total,
        from_date=from_date,
        to_date=to_date,
        status=status,
        current_date=datetime.now().strftime("%d-%b-%Y"),
        chart_labels=chart_labels,
        chart_values=chart_values,
        active_page="reports"
    )


# Export CSV
@reports_bp.route("/reports/export")
def export_csv():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")
    status = request.args.get("status", "")

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

    if status:

        query += """
        AND invoices.status = ?
        """

        params.append(status)

    query += """
    ORDER BY invoices.id DESC
    """

    invoices = conn.execute(
        query,
        params
    ).fetchall()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "Invoice ID",
            "Customer",
            "Amount",
            "Status",
            "Date"
        ]
    )

    for invoice in invoices:

        writer.writerow(
            [
                f"INV{invoice['id']:04d}",
                invoice["customer_name"],
                f"Rs {invoice["grand_total"]:.2f}",
                invoice["status"],
                invoice["created_at"][:10]
            ]
        )

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=sales_report.csv"

    conn.close()

    return response


# Export pdf
@reports_bp.route("/reports/export-pdf")
def export_pdf():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")
    status = request.args.get("status", "")

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

    if status:

        query += """
        AND invoices.status = ?
        """

        params.append(status)

    query += """
    ORDER BY invoices.id DESC
    """

    invoices = conn.execute(
        query,
        params
    ).fetchall()

    buffer = BytesIO()

    pdf = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "Smart Invoice - Sales Report",
        styles["Title"]
    )

    elements.append(title)

    elements.append(Spacer(1, 12))

    data = [[
        "Invoice",
        "Customer",
        "Amount",
        "Status",
        "Date"
    ]]

    for invoice in invoices:

        data.append([
            f'INV{invoice["id"]:04d}',
            invoice["customer_name"],
            f'Rs {invoice["grand_total"]:.2f}',
            invoice["status"],
            invoice["created_at"][:10]
        ])

    table = Table(data)

    table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ])
    )

    elements.append(table)

    pdf.build(elements)

    buffer.seek(0)

    conn.close()

    return send_file(
        buffer,
        as_attachment=True,
        download_name="sales_report.pdf",
        mimetype="application/pdf"
    )
