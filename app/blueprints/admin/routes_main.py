from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.models import Lab, User, Cycle, DocFile, Parameter
from app.blueprints.auth.decorators import disclaimer_required, role_required

# Crea il blueprint admin secondo instruction_admin.md
admin_bp = Blueprint("admin_bp", __name__, template_folder="templates")

# ===========================
# DASHBOARD AMMINISTRATIVA
# ===========================

@admin_bp.route("/dashboard")
@login_required
@disclaimer_required
@role_required("admin")
def dashboard():
    """Dashboard amministrativa con statistiche riassuntive"""
    total_labs = db.session.query(Lab).count()
    total_cycles = db.session.query(Cycle).count()
    total_docs = db.session.query(DocFile).count()
    pending_cycles = db.session.query(Cycle).filter_by(status="pending_review").count()
    published_cycles = db.session.query(Cycle).filter_by(status="published").count()
    total_parameters = db.session.query(Parameter).count()
    total_users = db.session.query(User).count()
    
    return render_template(
        "admin_dashboard.html",
        total_labs=total_labs,
        total_cycles=total_cycles,
        total_docs=total_docs,
        pending_cycles=pending_cycles,
        published_cycles=published_cycles,
        total_parameters=total_parameters,
        total_users=total_users
    )

# Redirect per compatibilità
@admin_bp.route("/")
def index():
    return redirect(url_for("admin_bp.dashboard"))

# Importa le route dai moduli separati
from . import routes_cycles
from . import routes_labs
from . import routes_parameters
from . import routes_users
from . import routes_docs