from flask import jsonify, render_template
from flask_login import login_required, current_user
from app.blueprints.main import bp
from app.blueprints.auth.decorators import lab_role_required
from app.models import Lab, Cycle, UploadFile
from app.services.roles import RoleService

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/health")
def health():
    return jsonify(status="ok"), 200

# ===========================
# DASHBOARD UTENTE
# ===========================

@bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard principale dell'utente con i suoi laboratori"""
    # Recupera tutti i laboratori dell'utente con i rispettivi ruoli
    user_labs = RoleService.get_labs_for_user(current_user.id)
    
    # Statistiche rapide
    total_labs = len(user_labs)
    recent_cycles = Cycle.query.filter_by(status='published').order_by(Cycle.created_at.desc()).limit(5).all()
    
    # Upload dell'utente (se la tabella ha un campo user_id)
    user_uploads_count = 0
    try:
        # Assumiamo che UploadFile abbia un campo per tracciare l'uploader
        user_uploads_count = UploadFile.query.filter_by(uploaded_by=current_user.id).count()
    except Exception:
        # Se la tabella non ha il campo, ignoriamo
        pass
    
    return render_template("main/dashboard.html",
                         user_labs=user_labs,
                         total_labs=total_labs,
                         recent_cycles=recent_cycles,
                         user_uploads_count=user_uploads_count)

# ===========================
# HUB LABORATORIO
# ===========================

@bp.route("/l/<lab_code>")
@login_required
@lab_role_required("viewer")
def lab_hub(lab_code):
    """Hub specifico per un laboratorio"""
    # Recupera il laboratorio
    lab = Lab.query.filter_by(code=lab_code).first_or_404()
    
    # Recupera il ruolo dell'utente per questo laboratorio
    user_role = None
    for lab_role in current_user.lab_roles:
        if lab_role.lab.code == lab_code:
            user_role = lab_role.role
            break
    
    # Tutti i cicli del laboratorio
    lab_cycles = Cycle.query.order_by(Cycle.created_at.desc()).limit(10).all() if Cycle.query.first() else []
    
    # Ultimi upload per questo laboratorio (ultimi 10)
    lab_uploads = []
    try:
        lab_uploads = UploadFile.query.filter_by(lab_code=lab_code).order_by(UploadFile.uploaded_at.desc()).limit(10).all()
    except Exception:
        # Se la tabella non ha lab_code, recuperiamo tutti gli upload recenti
        lab_uploads = UploadFile.query.order_by(UploadFile.uploaded_at.desc()).limit(10).all()
    
    # Utenti del laboratorio con ruoli
    lab_users = RoleService.get_users_for_lab(lab.id) if hasattr(RoleService, 'get_users_for_lab') else []
    
    # Verifica se l'utente è owner per mostrare link di gestione
    is_owner = current_user.has_lab_role(lab_code, "owner_lab")
    
    # Statistiche per la card QC (importiamo i modelli necessari)
    from app.models import Result, Parameter
    stats = {
        'total_results': 0,
        'active_cycles': len([c for c in lab_cycles if c.status == 'published']),
        'parameters_count': Parameter.query.count() if Parameter.query.first() else 0
    }
    
    # Conta i risultati totali se la tabella esiste
    try:
        stats['total_results'] = Result.query.join(Cycle).filter(
            Cycle.status == 'published'
        ).count()
    except Exception:
        pass
    
    return render_template("main/lab_hub.html",
                         lab=lab,
                         user_role=user_role,
                         is_owner=is_owner,
                         lab_cycles=lab_cycles,
                         lab_uploads=lab_uploads,
                         lab_users=lab_users,
                         stats=stats)
