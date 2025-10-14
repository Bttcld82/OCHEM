# 🔐 MODULO AUTENTICAZIONE & RUOLI - OCHEM

## 🎯 Obiettivo

Implementare il **Blueprint `auth_bp`** per il sistema **OCHEM (Flask)** con le seguenti funzionalità:

1. **Login/Logout** con Flask-Login e hash password sicuro
2. **Accettazione Disclaimer** obbligatoria al primo accesso  
3. **Sistema ruoli** globali (`admin`) e per laboratorio (`owner_lab`, `analyst`, `viewer`)
4. **Decorators di autorizzazione** per proteggere sezioni Admin e Lab

> **⚠️ Importante:** Modificare solo quanto necessario senza rompere la struttura esistente.

---

## 📁 Struttura Progetto

```
app/
├── __init__.py
├── models.py
├── blueprints/
│   ├── admin/
│   │   ├── routes_*.py
│   │   └── templates/...
│   ├── main/
│   ├── dati/
│   └── auth/          ← DA CREARE
│       ├── __init__.py
│       ├── routes_auth.py
│       ├── forms.py   ← (opzionale con WTForms)
│       └── templates/
│           ├── login.html
│           ├── disclaimer.html
│           └── register.html  ← (opzionale)
├── templates/
│   └── base.html
├── migrations/
├── scripts/
└── instance/
    └── ochem.sqlite3
```

---

## 📦 Dipendenze Richieste

Aggiungere a `requirements.txt`:

```txt
Flask-Login>=0.6.0
email-validator>=2.0.0
python-dotenv>=1.0.0
```

> **💡 Hash Password:** Utilizzare `werkzeug.security` (`generate_password_hash`, `check_password_hash`) per semplicità.

---

## 🧱 Aggiornamenti Modelli

### User Model (verificare in `app/models.py`)

Il modello **User** deve includere:

```python
class User(UserMixin, db.Model):
    # ... campi esistenti ...
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    accepted_disclaimer_at = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pw_hash, password)
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.pw_hash = generate_password_hash(password)
    
    def has_role(self, role_name):
        """Verifica ruolo globale"""
        return any(r.name == role_name for r in self.roles)
    
    def has_lab_role(self, lab_code, role_name):
        """Verifica ruolo per laboratorio specifico"""
        return any(
            ulr.lab_code == lab_code and ulr.role.name == role_name 
            for ulr in self.lab_roles
        )
```

---

## ⚙️ Configurazione Flask-Login

### Aggiornare `app/__init__.py`

```python
from flask_login import LoginManager

# Inizializzazione
login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"
login_manager.login_message = "Accesso richiesto per visualizzare questa pagina."
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)
    
    # ... configurazione esistente ...
    
    # Inizializza Flask-Login
    login_manager.init_app(app)
    
    # Registra blueprints
    from .blueprints.auth.routes_auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    # ... altri blueprints ...
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
```

---

## 🧩 Blueprint Authentication

### Creare `app/blueprints/auth/__init__.py`

```python
from flask import Blueprint

bp = Blueprint("auth_bp", __name__, template_folder="templates")

from . import routes_auth
```

### Implementare `app/blueprints/auth/routes_auth.py`

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from app import db
from app.models import User

auth_bp = Blueprint("auth_bp", __name__, template_folder="templates")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
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
            return redirect(url_for("auth_bp.disclaimer"))
        
        # Redirect alla pagina richiesta o dashboard
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        
        # Dashboard diverso per admin
        if user.has_role("admin"):
            return redirect(url_for("admin_bp.dashboard"))
        else:
            return redirect(url_for("main_bp.index"))
    
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout effettuato con successo.", "success")
    return redirect(url_for("main_bp.index"))

@auth_bp.route("/disclaimer", methods=["GET", "POST"])
@login_required
def disclaimer():
    # Se già accettato, redirect
    if current_user.accepted_disclaimer_at:
        return redirect(url_for("main_bp.index"))
    
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
                return redirect(url_for("main_bp.index"))
    
    return render_template("disclaimer.html")
```

---

## 🛡️ Decorators di Autorizzazione

### Creare `app/blueprints/auth/decorators.py`

```python
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
```

---

## 🧪 Templates di Autenticazione

### `app/blueprints/auth/templates/login.html`

```html
{% extends "base.html" %}

{% block title %}Login - OCHEM{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white text-center">
                    <h4 class="mb-0">🔐 Accesso OCHEM</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="remember" name="remember">
                            <label class="form-check-label" for="remember">
                                Ricordami
                            </label>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-sign-in-alt"></i> Accedi
                            </button>
                        </div>
                    </form>
                </div>
                <div class="card-footer text-center text-muted">
                    <small>Sistema OCHEM - Controllo Qualità Laboratori</small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### `app/blueprints/auth/templates/disclaimer.html`

```html
{% extends "base.html" %}

{% block title %}Disclaimer - OCHEM{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-sm">
                <div class="card-header bg-warning text-dark text-center">
                    <h4 class="mb-0">⚠️ Disclaimer e Condizioni d'Uso</h4>
                </div>
                <div class="card-body">
                    <div class="alert alert-info">
                        <strong>Attenzione:</strong> È necessario accettare le condizioni d'uso per procedere.
                    </div>
                    
                    <div class="border p-3 mb-4" style="max-height: 400px; overflow-y: auto;">
                        <h5>Termini e Condizioni d'Uso Sistema OCHEM</h5>
                        
                        <h6>1. Finalità del Sistema</h6>
                        <p>Il sistema OCHEM è destinato esclusivamente alla gestione e controllo qualità dei dati analitici di laboratorio. L'utilizzo è riservato al personale autorizzato.</p>
                        
                        <h6>2. Responsabilità dell'Utente</h6>
                        <ul>
                            <li>Mantenere riservate le credenziali di accesso</li>
                            <li>Utilizzare il sistema conformemente alle procedure operative</li>
                            <li>Non condividere dati sensibili con soggetti non autorizzati</li>
                            <li>Segnalare immediatamente eventuali anomalie o violazioni</li>
                        </ul>
                        
                        <h6>3. Protezione dei Dati</h6>
                        <p>Tutti i dati inseriti nel sistema sono protetti secondo le normative vigenti in materia di privacy e protezione dei dati personali (GDPR).</p>
                        
                        <h6>4. Limitazioni di Responsabilità</h6>
                        <p>L'organizzazione non si assume responsabilità per utilizzi impropri del sistema o per danni derivanti da un uso non conforme alle presenti condizioni.</p>
                        
                        <p><strong>Ultimo aggiornamento:</strong> {{ moment().format('DD/MM/YYYY') }}</p>
                    </div>
                    
                    <form method="POST">
                        <div class="form-check mb-3">
                            <input class="form-check-input" type="checkbox" id="accept" name="accept" required>
                            <label class="form-check-label" for="accept">
                                <strong>Dichiaro di aver letto e di accettare integralmente i termini e le condizioni d'uso</strong>
                            </label>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-check"></i> Accetto e Continuo
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 🔒 Protezione Blueprint Esistenti

### Aggiornare routes admin

Aggiungere agli imports di ogni file `routes_*.py` in admin:

```python
from flask_login import login_required
from app.blueprints.auth.decorators import role_required, disclaimer_required
```

Decorare le route admin:

```python
@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    # ... resto del codice ...
```

---

## 🌱 Seed Dati Utenti

### Aggiornare `scripts/seed_data.py`

```python
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_users():
    # Admin utente
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Amministratore sistema")
        db.session.add(admin_role)
    
    admin_user = User.query.filter_by(email="admin@ochem.local").first()
    if not admin_user:
        admin_user = User(
            name="Amministratore Sistema",
            email="admin@ochem.local",
            pw_hash=generate_password_hash("admin123!"),
            is_active=True,
            accepted_disclaimer_at=datetime.utcnow()
        )
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
    
    # Utenti owner per laboratori
    labs = Lab.query.all()
    for i, lab in enumerate(labs):
        email = f"owner_{lab.code.lower()}@ochem.local"
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(
                name=f"Responsabile {lab.name}",
                email=email,
                pw_hash=generate_password_hash("owner123!"),
                is_active=True,
                accepted_disclaimer_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()  # Per ottenere l'ID
            
            # Ruolo owner per il lab
            owner_role = Role.query.filter_by(name="owner_lab").first()
            if owner_role:
                lab_role = UserLabRole(
                    user_id=user.id,
                    lab_code=lab.code,
                    role_id=owner_role.id
                )
                db.session.add(lab_role)
    
    db.session.commit()
    
    print("✅ Utenti seed creati:")
    print("   Admin: admin@ochem.local / admin123!")
    print("   Owner labs: owner_[codice]@ochem.local / owner123!")
```

---

## ✅ Checklist Implementazione

- [ ] Installare dipendenze Flask-Login
- [ ] Aggiornare modello User con campi autenticazione
- [ ] Configurare Flask-Login in `__init__.py`
- [ ] Creare blueprint auth con route login/logout/disclaimer
- [ ] Implementare decorators di autorizzazione
- [ ] Creare template login e disclaimer
- [ ] Proteggere route admin con decorators
- [ ] Aggiornare seed dati con utenti di test
- [ ] Testare flusso completo autenticazione
- [ ] Aggiornare navbar con menu utente

---

## 🧪 Test di Verifica

1. **Login Admin**: Accesso a `/admin/dashboard` senza 403
2. **Login Owner Lab**: 403 su admin, accesso al proprio lab
3. **Disclaimer**: Redirect automatico se non accettato
4. **Protezione Route**: 403 per utenti non autorizzati
5. **Logout**: Funzionalità corretta e redirect

> **🎉 Risultato Atteso:** Sistema di autenticazione completo e sicuro integrato con la struttura esistente.