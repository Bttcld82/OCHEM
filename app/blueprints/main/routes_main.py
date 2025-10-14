from flask import jsonify, render_template
from app.blueprints.main import bp

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/health")
def health():
    return jsonify(status="ok"), 200
