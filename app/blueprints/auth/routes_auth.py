from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models import User

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
            return render_template("login_simple.html")
        
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if not user or not user.check_password(password):
            flash("Credenziali non valide.", "danger")
            return render_template("login_simple.html")
        
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