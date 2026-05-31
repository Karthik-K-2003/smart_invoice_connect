from flask import Blueprint

payments_bp = Blueprint(
    "payments",
    __name__,
    template_folder="../../views"
)

from . import routes