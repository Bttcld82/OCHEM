from flask import render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Lab, LabParticipation, Result, User, Role, UserLabRole
from app.services.roles import RoleService, RoleManagementError
from datetime import datetime
from .routes_main import admin_bp

# ===========================
# GESTIONE LABORATORI
# ===========================

@admin_bp.route("/labs")
def labs_list():
    """Lista laboratori"""
    q = request.args.get("q", "").strip()
    active = request.args.get("active")
    
    query = Lab.query
    if q:
        query = query.filter((Lab.name.ilike(f"%{q}%")) | (Lab.code.ilike(f"%{q}%")))
    if active == "1":
        query = query.filter_by(is_active=True)
    elif active == "0":
        query = query.filter_by(is_active=False)
    
    labs = query.order_by(Lab.name.asc()).all()
    total_users = db.session.query(User).count()
    total_participations = db.session.query(LabParticipation).count()
    
    return render_template("labs_list.html", 
                         labs=labs, 
                         q=q,
                         total_users=total_users,
                         total_participations=total_participations)

@admin_bp.route("/labs/new", methods=["GET", "POST"])
def labs_new():
    """Creazione nuovo laboratorio"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip()
        city = request.form.get("city", "").strip()
        contact_email = request.form.get("contact_email", "").strip()
        contact_phone = request.form.get("contact_phone", "").strip()
        
        if not name:
            flash("Il nome è obbligatorio.", "danger")
            return redirect(url_for("admin_bp.labs_new"))
        
        if code and Lab.query.filter_by(code=code).first():
            flash("Codice già esistente.", "warning")
            return redirect(url_for("admin_bp.labs_new"))
        
        lab = Lab(
            name=name,
            code=code or None,
            city=city or None,
            contact_email=contact_email or None,
            contact_phone=contact_phone or None
        )
        db.session.add(lab)
        db.session.commit()
        flash("Laboratorio creato con successo.", "success")
        return redirect(url_for("admin_bp.labs_list"))
    
    return render_template("labs_form.html", lab=None)

@admin_bp.route("/labs/<int:lab_id>/edit", methods=["GET", "POST"])
def labs_edit(lab_id):
    """Modifica laboratorio esistente"""
    lab = Lab.query.get_or_404(lab_id)
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip()
        city = request.form.get("city", "").strip()
        contact_email = request.form.get("contact_email", "").strip()
        contact_phone = request.form.get("contact_phone", "").strip()
        
        if not name:
            flash("Il nome è obbligatorio.", "danger")
            return redirect(url_for("admin_bp.labs_edit", lab_id=lab.id))
        
        if code and Lab.query.filter(Lab.id != lab.id, Lab.code == code).first():
            flash("Codice già usato da un altro laboratorio.", "warning")
            return redirect(url_for("admin_bp.labs_edit", lab_id=lab.id))
        
        lab.name = name
        lab.code = code or None
        lab.city = city or None
        lab.contact_email = contact_email or None
        lab.contact_phone = contact_phone or None
        lab.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Laboratorio aggiornato con successo.", "success")
        return redirect(url_for("admin_bp.labs_list"))
    
    return render_template("labs_form.html", lab=lab)

@admin_bp.route("/labs/<int:lab_id>/delete", methods=["POST"])
def labs_delete(lab_id):
    """Elimina laboratorio"""
    lab = Lab.query.get_or_404(lab_id)
    
    # Verifica se il laboratorio è usato in partecipazioni o risultati
    participation_usage = LabParticipation.query.filter_by(lab_code=lab.code).count()
    result_usage = Result.query.filter_by(lab_code=lab.code).count()
    
    if participation_usage > 0 or result_usage > 0:
        flash(f"Impossibile eliminare: laboratorio usato in {participation_usage} partecipazioni e {result_usage} risultati.", "danger")
        return redirect(url_for("admin_bp.labs_list"))
    
    db.session.delete(lab)
    db.session.commit()
    flash("Laboratorio eliminato con successo.", "success")
    return redirect(url_for("admin_bp.labs_list"))

@admin_bp.route("/labs/<int:lab_id>/toggle_active", methods=["POST"])
def lab_toggle_active(lab_id):
    """Attiva/disattiva laboratorio"""
    lab = Lab.query.get_or_404(lab_id)
    lab.is_active = not lab.is_active
    lab.updated_at = datetime.utcnow()
    db.session.commit()
    
    status = "attivato" if lab.is_active else "disattivato"
    flash(f"Laboratorio {lab.name} {status} con successo.", "success")
    return redirect(url_for("admin_bp.labs_list"))

# ===========================
# GESTIONE UTENTI LABORATORIO
# ===========================

@admin_bp.route("/labs/<int:lab_id>/users")
def lab_users(lab_id):
    """Lista utenti di un laboratorio"""
    lab = Lab.query.get_or_404(lab_id)
    
    # Ottieni utenti con i loro ruoli per questo lab
    lab_users = RoleService.get_users_for_lab(lab_id)
    
    # Ottieni tutti i ruoli disponibili per i laboratori
    lab_roles = Role.query.filter(Role.name.in_(RoleService.LAB_ROLES)).all()
    
    return render_template("lab_users.html", 
                         lab=lab, 
                         lab_users=lab_users,
                         lab_roles=lab_roles)

@admin_bp.route("/labs/<int:lab_id>/users/add-existing", methods=["POST"])
def add_existing_user_to_lab(lab_id):
    """Aggiungi utente esistente a un laboratorio"""
    try:
        email = request.form.get("email", "").strip()
        role_name = request.form.get("role_name")
        
        if not email or not role_name:
            flash("Email e ruolo sono obbligatori.", "danger")
            return redirect(url_for("admin_bp.lab_users", lab_id=lab_id))
        
        user = RoleService.add_existing_user_to_lab(email, lab_id, role_name)
        flash(f"Utente {user.name} aggiunto al laboratorio con ruolo {role_name}.", "success")
        
    except RoleManagementError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Errore nell'aggiunta: {e}", "danger")
    
    return redirect(url_for("admin_bp.lab_users", lab_id=lab_id))

@admin_bp.route("/labs/<int:lab_id>/users/<int:user_id>/update-role", methods=["POST"])
def update_lab_user_role(lab_id, user_id):
    """Cambia il ruolo di un utente nel laboratorio"""
    try:
        new_role = request.form.get("role_name")
        
        if not new_role:
            flash("Ruolo richiesto.", "danger")
            return redirect(url_for("admin_bp.lab_users", lab_id=lab_id))
        
        RoleService.change_lab_role(user_id, lab_id, new_role)
        
        user = User.query.get(user_id)
        flash(f"Ruolo di {user.name} aggiornato a {new_role}.", "success")
        
    except RoleManagementError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Errore nell'aggiornamento: {e}", "danger")
    
    return redirect(url_for("admin_bp.lab_users", lab_id=lab_id))

@admin_bp.route("/labs/<int:lab_id>/users/<int:user_id>/remove", methods=["POST"])
def remove_lab_user(lab_id, user_id):
    """Rimuove un utente dal laboratorio"""
    try:
        RoleService.remove_lab_role(user_id, lab_id)
        
        user = User.query.get(user_id)
        flash(f"Utente {user.name} rimosso dal laboratorio.", "success")
        
    except RoleManagementError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Errore nella rimozione: {e}", "danger")
    
    return redirect(url_for("admin_bp.lab_users", lab_id=lab_id))