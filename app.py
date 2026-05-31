from flask import Flask, render_template, request, redirect, session, flash
from datetime import timedelta
from config import *
from utils.mail import mail

from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.products import products_bp
from blueprints.customers import customers_bp
from blueprints.invoices import invoices_bp
from blueprints.payments import payments_bp
from blueprints.reports import reports_bp
from blueprints.suggestions import suggestions_bp

app = Flask(__name__, template_folder="views")
app.secret_key = SECRET_KEY
app.config["MAIL_SERVER"] = MAIL_SERVER
app.config["MAIL_PORT"] = MAIL_PORT
app.config["MAIL_USE_TLS"] = MAIL_USE_TLS
app.config["MAIL_USERNAME"] = MAIL_USERNAME
app.config["MAIL_PASSWORD"] = MAIL_PASSWORD

mail.init_app(app)

app.permanent_session_lifetime = timedelta(days=7)


#HOME
@app.route("/")
def home():
    return redirect("/login")


#BLUEPRINTS
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(products_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(invoices_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(suggestions_bp)


if __name__ == "__main__":
    app.run(debug=True)
