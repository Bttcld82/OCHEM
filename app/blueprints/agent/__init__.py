from flask import Blueprint

agent_bp = Blueprint(
    "agent",
    __name__,
    template_folder="templates",
)

from . import routes_agent  # noqa: F401, E402
