from flask import Blueprint

products_bp = Blueprint(
    "products",
    __name__,
    template_folder="../../views"
)

from . import routes