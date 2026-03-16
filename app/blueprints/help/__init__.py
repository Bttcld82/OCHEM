from flask import Blueprint

help_bp = Blueprint(
    "help",
    __name__,
    template_folder="templates",
    url_prefix="/help",
)

from . import routes_help  # noqa: F401, E402
