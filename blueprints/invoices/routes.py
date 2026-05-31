from flask import render_template, session, redirect
from blueprints.invoices import invoices_bp

@invoices_bp.route("/invoices")
def invoices():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "invoices/invoices.html",
        active_page="invoices"
    )