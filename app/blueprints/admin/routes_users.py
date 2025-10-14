from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Lab, Role, Result, JobLog, UserLabRole
from app.services.roles import RoleService, RoleManagementError
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
        query = query.filter((User.email.ilike(f"%{q}%")) |
                           (User.first_name.ilike(f"%{q}%")) |
                           (User.last_name.ilike(f"%{q}%")))
    users = query.order_by(User.first_name.asc(), User.last_name.asc()).all()
    return render_template("users_list.html", users=users, q=q)

@admin_bp.route("/users/new", methods=["GET", "POST"])
def users_new():
    """Creazione nuovo utente"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        password = request.form.get("password", "").strip()
        
        if not email or not first_name or not password:
            flash("Email, nome e password sono obbligatori.", "danger")
            return redirect(url_for("admin_bp.users_new"))
        
        if User.query.filter_by(email=email).first():
            flash("Email già esistente.", "warning")
            return redirect(url_for("admin_bp.users_new"))
        
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Utente creato con successo.", "success")
        return redirect(url_for("admin_bp.users_list"))
    
    roles = Role.query.order_by(Role.name.asc()).all()
    labs = Lab.query.filter_by(is_active=True).order_by(Lab.name.asc()).all()
    return render_template("users_form.html", user=None, roles=roles, labs=labs)

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
    return render_template("users_form.html", user=user, roles=roles, labs=labs)

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
    try:
        user = User.query.get_or_404(user_id)
        
        # Genera una password temporanea più sicura
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        user.set_password(temp_password)  # Usa il metodo del modello User
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        message = f"🔑 Password di {user.name} resettata con successo! Nuova password temporanea: <strong>{temp_password}</strong><br><small>⚠️ Comunicare questa password all'utente e richiedere di cambiarla al primo accesso.</small>"
        flash(message, "success")
        
        # Se è una richiesta AJAX, restituisci JSON
        if request.content_type == 'application/json':
            return jsonify({
                'success': True, 
                'message': f'Password resettata. Nuova password: {temp_password}',
                'temp_password': temp_password
            })
        
        # Altrimenti redirect
        return redirect(url_for("admin_bp.users_edit", user_id=user_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Errore durante il reset della password: {str(e)}", "danger")
        
        if request.content_type == 'application/json':
            return jsonify({'success': False, 'message': str(e)}), 400
        
        return redirect(url_for("admin_bp.users_edit", user_id=user_id))

# ===========================
# GESTIONE RUOLI ADMIN
# ===========================

@admin_bp.route("/users/<int:user_id>/make-admin", methods=["POST"])
def make_admin(user_id):
    """Rende un utente amministratore"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_admin = True
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f"Utente {user.name} promosso ad amministratore.", "success")
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@admin_bp.route("/users/<int:user_id>/remove-admin", methods=["POST"])
def remove_admin(user_id):
    """Rimuove privilegi admin da un utente"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Verifica che non sia l'ultimo admin
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            return jsonify({'success': False, 'message': 'Impossibile rimuovere l\'ultimo amministratore'}), 400
        
        user.is_admin = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f"Rimossi privilegi admin da {user.name}.", "success")
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@admin_bp.route("/users/<int:user_id>/detail")
def user_detail(user_id):
    """Dettaglio utente con laboratori associati"""
    user = User.query.get_or_404(user_id)
    
    # Ottieni laboratori dell'utente con ruoli
    user_labs = RoleService.get_labs_for_user(user_id)
    
    # Ottieni tutti i laboratori disponibili per l'aggiunta
    all_labs = Lab.query.filter_by(is_active=True).all()
    available_labs = [lab for lab in all_labs if lab.id not in [ul[0].id for ul in user_labs]]
    
    # Ottieni tutti i ruoli lab disponibili
    lab_roles = Role.query.filter(Role.name.in_(RoleService.LAB_ROLES)).all()
    
    return render_template("user_detail.html", 
                         user=user, 
                         user_labs=user_labs,
                         available_labs=available_labs,
                         lab_roles=lab_roles)

# ===========================
# GESTIONE RUOLI LABORATORIO
# ===========================

@admin_bp.route("/users/<int:user_id>/labs/add", methods=["POST"])
def add_user_to_lab(user_id):
    """Aggiungi utente a un laboratorio"""
    try:
        lab_id = request.form.get("lab_id")
        role_name = request.form.get("role_name")
        
        if not lab_id or not role_name:
            flash("Laboratorio e ruolo sono obbligatori.", "danger")
            return redirect(url_for("admin_bp.user_detail", user_id=user_id))
        
        RoleService.assign_lab_role(user_id, int(lab_id), role_name)
        
        lab = Lab.query.get(lab_id)
        flash(f"Utente aggiunto al laboratorio {lab.name} con ruolo {role_name}.", "success")
        
    except RoleManagementError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Errore nell'aggiunta: {e}", "danger")
    
    return redirect(url_for("admin_bp.user_detail", user_id=user_id))

@admin_bp.route("/users/<int:user_id>/labs/<int:lab_id>/update-role", methods=["POST"])
def update_user_lab_role(user_id, lab_id):
    """Cambia il ruolo di un utente in un laboratorio"""
    try:
        new_role = request.form.get("role_name")
        
        if not new_role:
            flash("Ruolo richiesto.", "danger")
            return redirect(url_for("admin_bp.user_detail", user_id=user_id))
        
        RoleService.change_lab_role(user_id, lab_id, new_role)
        
        lab = Lab.query.get(lab_id)
        flash(f"Ruolo aggiornato a {new_role} per il laboratorio {lab.name}.", "success")
        
    except RoleManagementError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Errore nell'aggiornamento: {e}", "danger")
    
    return redirect(url_for("admin_bp.user_detail", user_id=user_id))

@admin_bp.route("/users/<int:user_id>/labs/<int:lab_id>/remove", methods=["POST"])
def remove_user_lab_role(user_id, lab_id):
    """Rimuove un utente da un laboratorio"""
    try:
        RoleService.remove_lab_role(user_id, lab_id)
        
        lab = Lab.query.get(lab_id)
        flash(f"Utente rimosso dal laboratorio {lab.name}.", "success")
        
    except RoleManagementError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Errore nella rimozione: {e}", "danger")
    
    return redirect(url_for("admin_bp.user_detail", user_id=user_id))

# ===========================
# RUOLI
# ===========================

@admin_bp.route("/roles")
def roles_list():
    """Lista ruoli"""
    roles = Role.query.order_by(Role.name.asc()).all()
    return render_template("roles_list.html", roles=roles)

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
    
    return render_template("roles_form.html", role=None)

@admin_bp.route("/roles/<int:role_id>/edit", methods=["GET", "POST"])
def roles_edit(role_id):
    """Modifica ruolo esistente"""
    role = Role.query.get_or_404(role_id)
    
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        
        role.description = description or None
        role.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Ruolo aggiornato con successo.", "success")
        return redirect(url_for("admin_bp.roles_list"))
    
    return render_template("roles_form.html", role=role)

@admin_bp.route("/roles/<int:role_id>/delete", methods=["POST"])
def roles_delete(role_id):
    """Elimina ruolo"""
    role = Role.query.get_or_404(role_id)
    
    # Verifica che non sia un ruolo di sistema
    system_roles = ["admin", "owner_lab", "analyst", "viewer"]
    if role.name in system_roles:
        flash("Impossibile eliminare un ruolo di sistema.", "danger")
        return redirect(url_for("admin_bp.roles_list"))
    
    # Verifica che non sia in uso
    if len(role.user_roles) > 0:
        flash(f"Impossibile eliminare: ruolo assegnato a {len(role.user_roles)} utenti.", "danger")
        return redirect(url_for("admin_bp.roles_list"))
    
    db.session.delete(role)
    db.session.commit()
    flash("Ruolo eliminato con successo.", "success")
    return redirect(url_for("admin_bp.roles_list"))