from flask import Blueprint

settings_bp = Blueprint(
    "settings",
    __name__,
    template_folder="../../views"
)

from . import routes