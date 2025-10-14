from flask import render_template
from app.blueprints.dati import bp

@bp.route("/upload")
def upload_index():
    return render_template("dati_upload.html")
