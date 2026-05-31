from flask import render_template, session, redirect
from blueprints.payments import payments_bp

@payments_bp.route("/payments")
def payments():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "payments/payments.html",
        active_page="payments"
    )