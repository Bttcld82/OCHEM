# 🔐 ISTRUZIONE AGENTE VS CODE — MODULO AUTENTICAZIONE & RUOLI (OCHEM)

## 🎯 Obiettivo
Realizzare (o aggiornare) il **Blueprint `auth_bp`** per il progetto **OCHEM (Flask)** che gestisce:
1) **Login/Logout** con Flask-Login e password hash sicuro  
2) **Accettazione Disclaimer** obbligatoria al primo accesso  
3) **Ruoli** globali (`admin`) e **ruoli per laboratorio** (`owner_lab`, `analyst`, `viewer`)  
4) **Guardie/Decorators** per proteggere Admin, Lab e moduli futuri  

L’agente **deve modificare quanto già esiste**, senza rompere la struttura, adeguandosi a quanto definito nelle istruzioni precedenti (DB, relazioni, admin).

---

## 📁 Struttura progetto (riferimento)
app/
init.py
models.py
blueprints/
admin/
routes_admin.py
templates/...
main/
dati/
auth/ ← (CREARE)
init.py
routes_auth.py
forms.py ← (facoltativo, se usi WTForms; altrimenti non servirà)
templates/
login.html
disclaimer.html
register.html ← (facoltativo)
templates/
base.html
migrations/
scripts/
instance/ochem.sqlite3

yaml
Copy code

---

## 📦 Dipendenze richieste
Aggiornare `requirements.txt` (o installare) con:
Flask-Login
email-validator # se serve validare email in register
passlib[bcrypt] # oppure usare werkzeug.security per hash
python-dotenv

markdown
Copy code

> **Scelta hashing:** usare **werkzeug.security** (`generate_password_hash`, `check_password_hash`) per semplicità su Flask.

---

## 🧱 Aggiornamenti ai Modelli (se mancanti)
Nel file `app/models.py`, assicurarsi che il modello **User** abbia:
- `email` (UNIQUE), `pw_hash` (STRING), `is_active` (BOOL, default True)  
- `accepted_disclaimer_at` (DateTime, **NULL** se non accettato)  
- `last_login_at` (DateTime, opzionale)

Aggiornare anche:
- **User** deve implementare **Flask-Login** (`UserMixin` + `get_id()`).
- **Role** + **UserLabRole** già presenti (viewer/analyst/owner_lab/admin).
- Se non presente: metodo helper **User.has_role(role)** e **User.has_lab_role(lab_code, role)**.

> **Nota:** nessuna migrazione DB obbligatoria qui se i campi già esistono; altrimenti creare revisione Alembic ad hoc.

---

## ⚙️ Inizializzazione Flask-Login
In `app/__init__.py`:
- Creare e inizializzare `LoginManager`, settare `login_view = "auth_bp.login"`.
- Registrare il blueprint `auth_bp`.

Esempio (conciso):
```python
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"

def create_app():
    app = Flask(__name__)
    # ... config DB, blueprint admin/main ...
    login_manager.init_app(app)
    from app.blueprints.auth.routes_auth import auth_bp
    app.register_blueprint(auth_bp)
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
🧩 Blueprint auth_bp — Rotte da implementare
File: app/blueprints/auth/routes_auth.py

1) GET/POST /auth/login
Form con email, password.

Verifiche:

utente esistente e is_active

password corretta (check_password_hash)

se accepted_disclaimer_at is NULL ⇒ redirect a /auth/disclaimer dopo login di successo

Aggiornare last_login_at a utcnow().

login_user(user, remember=...) e redirect:

Se next presente → rispettare

Altrimenti: dashboard utente (o /admin/dashboard se admin)

2) GET /auth/logout
logout_user() e redirect a home/login.

3) GET/POST /auth/disclaimer
Mostrare testo disclaimer (quello approvato).

Bottone “Accetto e continuo”:

set accepted_disclaimer_at = utcnow()

redirect alla pagina precedente o dashboard

Se utente già ha accepted_disclaimer_at valorizzato → redirect immediato (no-op).

4) (Opzionale) GET/POST /auth/register
Solo se vuoi self-service:

email, password, lab_name

Creare Lab(slug derivato), associare UserLabRole con ruolo owner_lab

Altrimenti: lasciare la registrazione in mano all’Admin (già presente nel blueprint admin).

🛡️ Decorators di autorizzazione
Creare file app/blueprints/auth/decorators.py (o inserirli in routes_auth.py se preferisci):

@login_required
Usare quello di Flask-Login dove serve.

@disclaimer_required
Se current_user.accepted_disclaimer_at is None → redirect a /auth/disclaimer.

@role_required("admin")
Consente l’accesso solo a utenti con ruolo globale admin.

@lab_role_required(min_role="viewer")
Recupera lab_code da:

parametri della route (/<lab_code>/...) oppure

querystring ?lab=... oppure

contesto sessione (opzionale)

Verifica che current_user abbia UserLabRole compatibile col lab_code richiesto e con il min_role richiesto (gerarchia: owner_lab > analyst > viewer).

In caso negativo: abort(403).

Importante: applicare @role_required("admin") a tutte le route di admin_bp.
Applicare @lab_role_required a blueprint come qc e cycles nelle rotte per-lab.

🧭 Integrazione nel Layout (base.html)
Aggiungere in navbar:

se non autenticato: link “Login”

se autenticato: menu con email utente, “Profilo”, “Logout”

se ruolo admin: link “Admin”

Mostrare eventuale banner se accepted_disclaimer_at is NULL (“Devi accettare il disclaimer per continuare”).

🧪 Template minimi
Creare sotto app/blueprints/auth/templates/:

login.html

Campi: email, password

Link “Password dimenticata?” (placeholder)

disclaimer.html

Mostrare testo del disclaimer legale (già definito)

Pulsante “Accetto e continuo”

register.html (opzionale)

Campi: email, password, ripeti password, lab_name

Tutti i template estendono templates/base.html e usano i flash messages.

🔒 Protezione blueprint esistenti
In app/blueprints/admin/routes_admin.py:

Aggiungere in alto:

python
Copy code
from flask_login import login_required, current_user
from app.blueprints.auth.decorators import role_required
Decorare tutte le route admin con:

python
Copy code
@login_required
@role_required("admin")
Nei blueprint “per-lab” (es. qc, cycles):

Importare lab_role_required e applicarlo alle route che richiedono un lab_code.

🌱 Seed utenti (aggiornare scripts/seed_data.py)
Creare 1 utente admin:

email="admin@ochem.local", pw_hash hash di “admin123!”, is_active=True, accepted_disclaimer_at=utcnow()

Aggiungere Role(name="admin") se non esiste e legarlo come ruolo globale oppure trattare admin come flag/ruolo separato (coerente con i modelli).

Creare 2 utenti owner (uno per ogni lab presente nel seed):

owner_alpha@..., owner_beta@... con hash password, accepted_disclaimer_at=utcnow()

Inserire righe UserLabRole con ruolo owner_lab.

Stampare a fine seed le credenziali demo.

🧪 Test rapidi (manuali)
Login con admin:

Accedi a /admin/dashboard senza 403

Login con owner_lab:

403 su /admin/dashboard

Accesso consentito alle rotte per il proprio lab

Utente senza disclaimer:

Dopo login, redirect a /auth/disclaimer

Dopo accettazione, prosegue alla pagina richiesta

Utente senza ruolo su lab X:

Tentativo di accesso a /l/X/... → 403

🧷 Sicurezza & dettagli
Usare HTTPS in produzione; in dev basta HTTP.

Impostare REMEMBER_COOKIE_SECURE, SESSION_COOKIE_SECURE in prod.

Rate-limit su /auth/login (Flask-Limiter) — opzionale ora, consigliato poi.

Password hashing: werkzeug.security.generate_password_hash(pw, method="pbkdf2:sha256", salt_length=16).

✅ Criteri di accettazione
Esiste il blueprint auth_bp con le rotte login, logout, disclaimer (e register se richiesto).

Flask-Login inizializzato, user_loader funzionante.

Decorators role_required, lab_role_required, disclaimer_required disponibili e usati.

Navbar aggiornata (login/logout/admin).

Seed: utente admin e 2 owner lab creati con hash password.

Accesso a /admin/... possibile solo a admin; 403 per altri.

Dopo login, se disclaimer non accettato → redirect a /auth/disclaimer.