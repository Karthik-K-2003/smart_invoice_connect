from flask import render_template, session, redirect
from blueprints.customers import customers_bp

@customers_bp.route("/customers")
def customers():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "customers/customers.html",
        active_page="customers"
    )