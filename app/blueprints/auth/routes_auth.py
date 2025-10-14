from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import secrets
from app import db
from app.models import User, RegistrationRequest, InviteToken, Lab, UserLabRole, Role

auth_bp = Blueprint("auth_bp", __name__, template_folder="templates")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Route di login"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))
        
        if not email or not password:
            flash("Email e password sono obbligatori.", "danger")
            return render_template("login.html")
        
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if not user or not user.check_password(password):
            flash("Credenziali non valide.", "danger")
            return render_template("login.html")
        
        # Aggiorna ultimo accesso
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # Login utente
        login_user(user, remember=remember)
        
        # Verifica disclaimer
        if not user.accepted_disclaimer_at:
            next_page = request.args.get("next")
            if next_page:
                session["disclaimer_next"] = next_page
            return redirect(url_for("auth_bp.disclaimer"))
        
        # Redirect alla pagina richiesta o dashboard
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        
        # Dashboard diverso per admin
        if user.has_role("admin"):
            return redirect(url_for("admin_bp.dashboard"))
        else:
            return redirect(url_for("main.index"))
    
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    """Route di logout"""
    logout_user()
    flash("Logout effettuato con successo.", "success")
    return redirect(url_for("main.index"))

@auth_bp.route("/disclaimer", methods=["GET", "POST"])
@login_required
def disclaimer():
    """Route per accettazione disclaimer"""
    # Se già accettato, redirect
    if current_user.accepted_disclaimer_at:
        next_page = session.get("disclaimer_next")
        if next_page:
            session.pop("disclaimer_next", None)
            return redirect(next_page)
        
        if current_user.has_role("admin"):
            return redirect(url_for("admin_bp.dashboard"))
        else:
            return redirect(url_for("main.index"))
    
    if request.method == "POST":
        if request.form.get("accept"):
            current_user.accepted_disclaimer_at = datetime.utcnow()
            db.session.commit()
            flash("Disclaimer accettato con successo.", "success")
            
            # Redirect alla pagina originale o dashboard
            next_page = session.get("disclaimer_next")
            if next_page:
                session.pop("disclaimer_next", None)
                return redirect(next_page)
            
            if current_user.has_role("admin"):
                return redirect(url_for("admin_bp.dashboard"))
            else:
                return redirect(url_for("main.index"))
    
    return render_template("disclaimer.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Route per autoregistrazione utenti"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        desired_lab_name = request.form.get("desired_lab_name", "").strip()
        target_lab_code = request.form.get("target_lab_code", "").strip()
        note = request.form.get("note", "").strip()
        
        # Validazioni
        if not email or not full_name or not password:
            flash("Email, nome completo e password sono obbligatori.", "danger")
            return render_template("register.html")
        
        if len(password) < 10:
            flash("La password deve essere di almeno 10 caratteri.", "danger")
            return render_template("register.html")
        
        # Verifica se email già in uso
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Un utente con questa email esiste già.", "danger")
            return render_template("register.html")
        
        # Verifica se c'è già una richiesta pendente
        existing_request = RegistrationRequest.query.filter(
            RegistrationRequest.email == email,
            RegistrationRequest.status.in_(['submitted', 'under_review'])
        ).first()
        if existing_request:
            flash("Hai già una richiesta di registrazione in corso.", "warning")
            return render_template("register.html")
        
        # Determina ruolo desiderato
        desired_role = "owner_lab" if desired_lab_name else "analyst"
        
        # Crea richiesta di registrazione
        registration = RegistrationRequest(
            email=email,
            full_name=full_name,
            desired_lab_name=desired_lab_name or None,
            target_lab_code=target_lab_code or None,
            desired_role=desired_role,
            note=note or None
        )
        
        db.session.add(registration)
        db.session.commit()
        
        flash(
            "Richiesta di registrazione inviata con successo! "
            "Riceverai una comunicazione dopo la revisione da parte dell'amministratore.",
            "success"
        )
        return redirect(url_for("auth_bp.login"))
    
    # GET request
    labs = Lab.query.filter_by(is_active=True).order_by(Lab.name.asc()).all()
    return render_template("register.html", labs=labs)

@auth_bp.route("/activate")
def activate():
    """Route per attivazione utente (placeholder per token-based activation)"""
    token = request.args.get("token")
    if not token:
        flash("Token di attivazione mancante.", "danger")
        return redirect(url_for("auth_bp.login"))
    
    # TODO: Implementare verifica token firmato
    flash("Funzionalità di attivazione non ancora implementata.", "info")
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/accept-invite", methods=["GET", "POST"])
def accept_invite():
    """Route per accettazione inviti"""
    token_str = request.args.get("token")
    if not token_str:
        flash("Token di invito mancante.", "danger")
        return redirect(url_for("auth_bp.login"))
    
    # Trova e valida il token
    invite = InviteToken.query.filter_by(token=token_str).first()
    if not invite:
        flash("Token di invito non valido.", "danger")
        return redirect(url_for("auth_bp.login"))
    
    if not invite.is_valid:
        if invite.is_used:
            flash("Questo invito è già stato utilizzato.", "warning")
        elif invite.is_expired:
            flash("Questo invito è scaduto.", "warning")
        return redirect(url_for("auth_bp.login"))
    
    if request.method == "POST":
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        
        if not password or len(password) < 10:
            flash("La password deve essere di almeno 10 caratteri.", "danger")
            return render_template("accept_invite.html", invite=invite)
        
        if password != password_confirm:
            flash("Le password non corrispondono.", "danger")
            return render_template("accept_invite.html", invite=invite)
        
        # Crea o trova utente
        user = User.query.filter_by(email=invite.email).first()
        if not user:
            # Crea nuovo utente
            names = invite.email.split('@')[0].split('.')
            first_name = names[0].title() if names else "Utente"
            last_name = names[1].title() if len(names) > 1 else ""
            
            user = User(
                email=invite.email,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            db.session.add(user)
        
        # Imposta password
        user.set_password(password)
        user.is_active = True
        
        # Crea associazione lab-ruolo se non esiste
        lab = Lab.query.filter_by(code=invite.lab_code).first()
        if lab:
            existing_role = UserLabRole.query.filter_by(
                user_id=user.id,
                lab_id=lab.id
            ).first()
            
            if not existing_role:
                role = Role.query.filter_by(name=invite.role).first()
                if role:
                    user_lab_role = UserLabRole(
                        user=user,
                        lab=lab,
                        role=role
                    )
                    db.session.add(user_lab_role)
        
        # Marca invito come usato
        invite.use_token()
        
        db.session.commit()
        
        # Effettua login automatico
        login_user(user)
        flash(f"Benvenuto! Sei stato aggiunto al laboratorio {invite.lab_code} con ruolo {invite.role}.", "success")
        
        # Redirect al disclaimer se non accettato
        if not user.accepted_disclaimer_at:
            return redirect(url_for("auth_bp.disclaimer"))
        
        return redirect(url_for("main.index"))
    
    # GET request - mostra form
    lab = Lab.query.filter_by(code=invite.lab_code).first()
    return render_template("accept_invite.html", invite=invite, lab=lab)