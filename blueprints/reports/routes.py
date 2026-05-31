from flask import render_template, session, redirect
from blueprints.reports import reports_bp

@reports_bp.route("/reports")
def reports():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "reports/reports.html",
        active_page="reports"
    )