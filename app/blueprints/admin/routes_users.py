from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Lab, Role, Result, JobLog
from datetime import datetime
from .routes_main import admin_bp

# ===========================
# GESTIONE UTENTI
# ===========================

@admin_bp.route("/users")
def users_list():
    """Lista utenti"""
    q = request.args.get("q", "").strip()
    query = User.query
    if q:
        query = query.filter((User.username.ilike(f"%{q}%")) | 
                           (User.email.ilike(f"%{q}%")) |
                           (User.full_name.ilike(f"%{q}%")))
    users = query.order_by(User.full_name.asc()).all()
    return render_template("admin/users_list.html", users=users, q=q)

@admin_bp.route("/users/new", methods=["GET", "POST"])
def users_new():
    """Creazione nuovo utente"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "").strip()
        role_id = request.form.get("role_id")
        lab_id = request.form.get("lab_id")
        
        if not username or not email or not full_name or not password:
            flash("Username, email, nome completo e password sono obbligatori.", "danger")
            return redirect(url_for("admin_bp.users_new"))
        
        if User.query.filter_by(username=username).first():
            flash("Username già esistente.", "warning")
            return redirect(url_for("admin_bp.users_new"))
        
        if User.query.filter_by(email=email).first():
            flash("Email già esistente.", "warning")
            return redirect(url_for("admin_bp.users_new"))
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=generate_password_hash(password),
            role_id=int(role_id) if role_id else None,
            lab_id=int(lab_id) if lab_id else None,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        flash("Utente creato con successo.", "success")
        return redirect(url_for("admin_bp.users_list"))
    
    roles = Role.query.order_by(Role.name.asc()).all()
    labs = Lab.query.filter_by(is_active=True).order_by(Lab.name.asc()).all()
    return render_template("admin/users_form.html", user=None, roles=roles, labs=labs)

@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def users_edit(user_id):
    """Modifica utente esistente"""
    user = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "").strip()
        role_id = request.form.get("role_id")
        lab_id = request.form.get("lab_id")
        
        if not username or not email or not full_name:
            flash("Username, email e nome completo sono obbligatori.", "danger")
            return redirect(url_for("admin_bp.users_edit", user_id=user.id))
        
        if User.query.filter(User.id != user.id, User.username == username).first():
            flash("Username già usato da un altro utente.", "warning")
            return redirect(url_for("admin_bp.users_edit", user_id=user.id))
        
        if User.query.filter(User.id != user.id, User.email == email).first():
            flash("Email già usata da un altro utente.", "warning")
            return redirect(url_for("admin_bp.users_edit", user_id=user.id))
        
        user.username = username
        user.email = email
        user.full_name = full_name
        if password:
            user.password_hash = generate_password_hash(password)
        user.role_id = int(role_id) if role_id else None
        user.lab_id = int(lab_id) if lab_id else None
        user.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Utente aggiornato con successo.", "success")
        return redirect(url_for("admin_bp.users_list"))
    
    roles = Role.query.order_by(Role.name.asc()).all()
    labs = Lab.query.filter_by(is_active=True).order_by(Lab.name.asc()).all()
    return render_template("admin/users_form.html", user=user, roles=roles, labs=labs)

@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
def users_delete(user_id):
    """Elimina utente"""
    user = User.query.get_or_404(user_id)
    
    # Verifica se l'utente è usato in risultati o log
    result_usage = Result.query.filter_by(created_by=user.username).count()
    job_usage = JobLog.query.filter_by(user_id=user.id).count()
    
    if result_usage > 0 or job_usage > 0:
        flash(f"Impossibile eliminare: utente usato in {result_usage} risultati e {job_usage} log.", "danger")
        return redirect(url_for("admin_bp.users_list"))
    
    db.session.delete(user)
    db.session.commit()
    flash("Utente eliminato con successo.", "success")
    return redirect(url_for("admin_bp.users_list"))

@admin_bp.route("/users/<int:user_id>/toggle_active", methods=["POST"])
def user_toggle_active(user_id):
    """Attiva/disattiva utente"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    status = "attivato" if user.is_active else "disattivato"
    flash(f"Utente {user.full_name} {status} con successo.", "success")
    return redirect(url_for("admin_bp.users_list"))

@admin_bp.route("/users/<int:user_id>/reset_password", methods=["POST"])
def user_reset_password(user_id):
    """Reset password utente"""
    user = User.query.get_or_404(user_id)
    temp_password = "temp123"
    user.password_hash = generate_password_hash(temp_password)
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f"Password di {user.full_name} resettata a: {temp_password}", "success")
    return redirect(url_for("admin_bp.users_list"))

# ===========================
# RUOLI
# ===========================

@admin_bp.route("/roles")
def roles_list():
    """Lista ruoli"""
    roles = Role.query.order_by(Role.name.asc()).all()
    return render_template("admin/roles_list.html", roles=roles)

@admin_bp.route("/roles/new", methods=["GET", "POST"])
def roles_new():
    """Creazione nuovo ruolo"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        
        if not name:
            flash("Il nome è obbligatorio.", "danger")
            return redirect(url_for("admin_bp.roles_new"))
        
        if Role.query.filter_by(name=name).first():
            flash("Nome ruolo già esistente.", "warning")
            return redirect(url_for("admin_bp.roles_new"))
        
        role = Role(name=name, description=description or None)
        db.session.add(role)
        db.session.commit()
        flash("Ruolo creato con successo.", "success")
        return redirect(url_for("admin_bp.roles_list"))
    
    return render_template("admin/roles_form.html", role=None)