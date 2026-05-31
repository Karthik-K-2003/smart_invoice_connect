from flask import render_template, redirect, session
from blueprints.dashboard import dashboard_bp

@dashboard_bp.route("/dashboard")
def dashboard():

    # CHECK USER LOGIN
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard/dashboard.html", active_page="dashboard")