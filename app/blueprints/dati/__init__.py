from flask import Blueprint
bp = Blueprint("dati", __name__, template_folder="templates")
from . import routes_dati  # noqa
