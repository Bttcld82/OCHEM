from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import RegistrationRequest, User, Lab, Role, UserLabRole
from app.blueprints.auth.decorators import disclaimer_required, role_required
from .routes_main import admin_bp

# ===========================
# GESTIONE REGISTRAZIONI
# ===========================

@admin_bp.route("/registrations")
@login_required
@disclaimer_required
@role_required("admin")
def registrations_list():
    """Lista richieste di registrazione"""
    status_filter = request.args.get("status", "").strip()
    
    query = RegistrationRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    registrations = query.order_by(RegistrationRequest.created_at.desc()).all()
    
    # Contatori per le statistiche
    stats = {
        'total': RegistrationRequest.query.count(),
        'submitted': RegistrationRequest.query.filter_by(status='submitted').count(),
        'under_review': RegistrationRequest.query.filter_by(status='under_review').count(),
        'approved': RegistrationRequest.query.filter_by(status='approved').count(),
        'rejected': RegistrationRequest.query.filter_by(status='rejected').count()
    }
    
    return render_template(
        "registrations_list.html",
        registrations=registrations,
        stats=stats,
        status_filter=status_filter
    )

@admin_bp.route("/registrations/<int:registration_id>")
@login_required
@disclaimer_required
@role_required("admin")
def registration_detail(registration_id):
    """Dettaglio richiesta di registrazione"""
    registration = RegistrationRequest.query.get_or_404(registration_id)
    
    # Verifica se esiste già un utente con questa email
    existing_user = User.query.filter_by(email=registration.email).first()
    
    # Verifica se il lab target esiste (se specificato)
    target_lab = None
    if registration.target_lab_code:
        target_lab = Lab.query.filter_by(code=registration.target_lab_code).first()
    
    return render_template(
        "registration_detail.html",
        registration=registration,
        existing_user=existing_user,
        target_lab=target_lab
    )

@admin_bp.route("/registrations/<int:registration_id>/review", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def registration_review(registration_id):
    """Mette la richiesta in stato 'under_review'"""
    registration = RegistrationRequest.query.get_or_404(registration_id)
    
    if registration.status != 'submitted':
        flash("Questa richiesta non può essere messa in revisione.", "warning")
        return redirect(url_for("admin_bp.registration_detail", registration_id=registration_id))
    
    registration.status = 'under_review'
    registration.decided_by = current_user.email
    db.session.commit()
    
    flash("Richiesta messa in revisione.", "info")
    return redirect(url_for("admin_bp.registration_detail", registration_id=registration_id))

@admin_bp.route("/registrations/<int:registration_id>/approve", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def registration_approve(registration_id):
    """Approva una richiesta di registrazione"""
    registration = RegistrationRequest.query.get_or_404(registration_id)
    
    if not registration.is_pending:
        flash("Questa richiesta è già stata processata.", "warning")
        return redirect(url_for("admin_bp.registration_detail", registration_id=registration_id))
    
    admin_note = request.form.get("admin_note", "").strip()
    
    try:
        # 1. Crea/attiva l'utente
        user = User.query.filter_by(email=registration.email).first()
        if not user:
            # Estrai nome e cognome dal full_name
            name_parts = registration.full_name.split() if registration.full_name else ["Utente"]
            first_name = name_parts[0] if name_parts else "Utente"
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            user = User(
                email=registration.email,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            db.session.add(user)
            db.session.flush()  # Per ottenere l'ID
        else:
            user.is_active = True
        
        # 2. Gestisci il laboratorio
        target_lab = None
        if registration.desired_lab_name:
            # Crea nuovo laboratorio
            # Genera codice lab sicuro
            lab_code = registration.desired_lab_name.lower().replace(" ", "_")[:20]
            counter = 1
            base_code = lab_code
            while Lab.query.filter_by(code=lab_code).first():
                lab_code = f"{base_code}_{counter}"
                counter += 1
            
            target_lab = Lab(
                code=lab_code,
                name=registration.desired_lab_name,
                is_active=True
            )
            db.session.add(target_lab)
            db.session.flush()
            
            # Owner del nuovo lab
            desired_role = "owner_lab"
            
        elif registration.target_lab_code:
            # Unisciti a lab esistente
            target_lab = Lab.query.filter_by(code=registration.target_lab_code).first()
            if not target_lab:
                flash("Il laboratorio specificato non esiste più.", "danger")
                return redirect(url_for("admin_bp.registration_detail", registration_id=registration_id))
            
            desired_role = registration.desired_role or "analyst"
        
        # 3. Assegna ruolo se c'è un lab
        if target_lab:
            # Verifica se esiste già il ruolo
            existing_role = UserLabRole.query.filter_by(
                user_id=user.id,
                lab_id=target_lab.id
            ).first()
            
            if not existing_role:
                role = Role.query.filter_by(name=desired_role).first()
                if not role:
                    # Crea il ruolo se non esiste
                    role = Role(name=desired_role, description=f"Ruolo {desired_role}")
                    db.session.add(role)
                    db.session.flush()
                
                user_lab_role = UserLabRole(
                    user=user,
                    lab=target_lab,
                    role=role
                )
                db.session.add(user_lab_role)
        
        # 4. Approva la richiesta
        registration.approve(current_user.email, admin_note)
        
        db.session.commit()
        
        success_msg = f"Richiesta approvata! Utente {user.email} creato"
        if target_lab:
            success_msg += f" e assegnato al lab {target_lab.name} ({target_lab.code}) con ruolo {desired_role}"
        success_msg += "."
        
        flash(success_msg, "success")
        
        # TODO: Invia email di notifica all'utente
        
    except Exception as e:
        db.session.rollback()
        flash(f"Errore durante l'approvazione: {str(e)}", "danger")
    
    return redirect(url_for("admin_bp.registration_detail", registration_id=registration_id))

@admin_bp.route("/registrations/<int:registration_id>/reject", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def registration_reject(registration_id):
    """Rifiuta una richiesta di registrazione"""
    registration = RegistrationRequest.query.get_or_404(registration_id)
    
    if not registration.is_pending:
        flash("Questa richiesta è già stata processata.", "warning")
        return redirect(url_for("admin_bp.registration_detail", registration_id=registration_id))
    
    admin_note = request.form.get("admin_note", "").strip()
    if not admin_note:
        flash("È necessario fornire una motivazione per il rifiuto.", "danger")
        return redirect(url_for("admin_bp.registration_detail", registration_id=registration_id))
    
    registration.reject(current_user.email, admin_note)
    db.session.commit()
    
    flash("Richiesta rifiutata.", "info")
    
    # TODO: Invia email di notifica all'utente
    
    return redirect(url_for("admin_bp.registration_detail", registration_id=registration_id))