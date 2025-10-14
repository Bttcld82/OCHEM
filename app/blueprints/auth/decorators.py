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
    role_hierarchy = {"owner_lab": 3, "analyst": 2, "viewer": 1}
    
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
            
            # Verifica ruolo laboratorio
            min_level = role_hierarchy.get(min_role, 1)
            user_roles = current_user.lab_roles
            
            has_access = any(
                ulr.lab_code == lab_code and 
                role_hierarchy.get(ulr.role.name, 0) >= min_level
                for ulr in user_roles
            )
            
            if not has_access and not current_user.has_role("admin"):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator