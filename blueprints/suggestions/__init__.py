from flask import Blueprint

suggestions_bp = Blueprint(
    "suggestions",
    __name__,
    template_folder="../../views"
)

from . import routes