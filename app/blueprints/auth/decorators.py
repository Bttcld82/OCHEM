from functools import wraps
from flask import abort, redirect, url_for, session, request
from flask_login import current_user

def disclaimer_required(f):
    """Richiede che l'utente abbia accettato il disclaimer"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth_bp.login"))
        
        if not current_user.accepted_disclaimer_at:
            # Salva la pagina richiesta per dopo
            session["disclaimer_next"] = request.url
            return redirect(url_for("auth_bp.disclaimer"))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name):
    """Richiede un ruolo globale specifico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth_bp.login"))
            
            if not current_user.accepted_disclaimer_at:
                session["disclaimer_next"] = request.url
                return redirect(url_for("auth_bp.disclaimer"))
            
            if not current_user.has_role(role_name):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def lab_role_required(min_role="viewer"):
    """Richiede un ruolo minimo per un laboratorio"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth_bp.login"))
            
            if not current_user.accepted_disclaimer_at:
                session["disclaimer_next"] = request.url
                return redirect(url_for("auth_bp.disclaimer"))
            
            # Estrai lab_code dai parametri della route
            lab_code = kwargs.get("lab_code") or request.args.get("lab")
            
            if not lab_code:
                abort(400, "Codice laboratorio richiesto")
            
            # Usa il metodo del modello User per verificare il ruolo
            if not current_user.has_lab_min_role(lab_code, min_role):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def has_lab_min_role(user, lab_code, min_role):
    """Funzione helper per verificare ruoli minimi nei laboratori"""
    return user.has_lab_min_role(lab_code, min_role)