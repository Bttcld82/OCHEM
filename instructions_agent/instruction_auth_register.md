# 🔐 ISTRUZIONE AGENTE VS CODE — REGISTRAZIONE UTENTI & INVITI (OCHEM)

## 🎯 Obiettivo
Implementare due flussi di onboarding utente:
1. **Autoregistrazione con approvazione Admin**  
    (registration request → approve → activate)
2. **Invito da Admin**  
    (invite link → accept → set password)

Entrambi con **login Flask-Login** e **accettazione disclaimer** obbligatoria al primo accesso.

> Non rompere quanto esiste. Integrare in `auth_bp` e in `admin_bp`. Usare SQLite con Alembic (schema portabile a Postgres).

---

## 📁 Struttura di progetto interessata

```
app/
├── blueprints/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes_auth.py      # ← AGGIUNGERE/AGGIORNARE
│   │   └── decorators.py       # ← GIÀ PREVISTO
│   └── admin/
│       └── routes_admin.py     # ← AGGIUNGERE sez. Registrazioni & Inviti
├── templates/
│   ├── login.html              # ← ESISTE
│   ├── disclaimer.html         # ← ESISTE
│   ├── register.html           # ← NUOVO
│   ├── accept_invite.html      # ← NUOVO
│   ├── activate.html           # ← NUOVO (minimal)
│   └── admin/
│       ├── registrations_list.html   # ← NUOVO
│       ├── registration_review.html # ← NUOVO
│       └── lab_users.html           # ← NUOVO (lista utenti di un lab + inviti)
├── models.py                   # ← AGGIUNGERE 2 TABELLINE
├── migrations/
│   └── versions/               # ← NUOVA revisione Alembic
└── scripts/
     └── seed_data.py            # ← AGGIORNARE per admin + owner demo
```

---

## 🧱 Modello dati — nuove tabelle (SQLAlchemy/Alembic)

### 1. `registration_request`
| Campo            | Tipo      | Note |
|------------------|-----------|------|
| id               | PK        |      |
| email            | STRING    | required |
| full_name        | STRING    | NULL ok |
| desired_lab_name | STRING    | NULL ok |
| target_lab_code  | STRING    | NULL ok (se vuole unirsi a lab esistente) |
| desired_role     | STRING    | default: `"owner_lab"` |
| note             | TEXT      | NULL ok |
| status           | STRING    | `'submitted'|'under_review'|'approved'|'rejected'|'expired'`, default `'submitted'` |
| admin_note       | TEXT      | NULL ok |
| created_at       | DateTime  | UTC now |
| decided_at       | DateTime  | NULL ok |
| decided_by       | STRING    | NULL ok |

**Indici:**  
- `ix_registration_request_email`
- `ix_registration_request_status`

### 2. `invite_token`
| Campo      | Tipo      | Note |
|------------|-----------|------|
| id         | PK        |      |
| lab_code   | STRING    | required |
| email      | STRING    | required |
| role       | STRING    | `'owner_lab'|'analyst'|'viewer'` |
| token      | STRING(96)| unique, base64url 32–48 bytes |
| expires_at | DateTime  | required |
| used_at    | DateTime  | NULL ok |
| created_by | STRING    | required |
| created_at | DateTime  | UTC now |

**Indici:**  
- `ux_invite_token_token` (UNIQUE)
- `ix_invite_token_lab_code`
- `ix_invite_token_email`

> **Niente email_verification_token** per ora (facoltativa).

---

## 🔧 Migrazione Alembic

- Creare una revisione:  
  ```bash
  alembic revision -m "auth registration & invite"
  ```
- Implementare le due tabelle sopra con indici indicati.
- Applicare con:  
  ```bash
  alembic upgrade head
  ```

---

## 🔐 Blueprint `auth_bp` — nuove route

### 1. `GET /auth/register` (form autoregistrazione)
- **Form fields:** `full_name`, `email`, `password`, `desired_lab_name` (opz), `target_lab_code` (opz), `note` (opz)
- **POST:** valida email, password minima (≥10 char), crea `registration_request(status='submitted')`
- **UI:** messaggio “Richiesta inviata. Riceverai una email dopo la revisione.”

### 2. `GET /auth/activate?token=...` (attivazione utente)
- **Input:** `token` firmato (generato alla `approval` della richiesta)
- **Azione:** crea/attiva `User` se non esistente, set `is_active=True`, chiede set/reset password se necessario, imposta `last_login_at`
- **Redirect:** `/auth/disclaimer`

> Se non vuoi usare token separato, l’Admin può impostare password provvisoria e flag `is_active=True`. Tenere comunque la route per uniformità UX.

### 3. `GET/POST /auth/accept-invite?token=...` (invito)
- **GET:** valida `invite_token` (non usato, non scaduto). Mostra lab/ruolo e email.
- **POST:** imposta password, crea/associa `UserLabRole`, marca `used_at=now()`, `login_user()` e redirect a `/auth/disclaimer`

**Regole token:**  
- scadenza 7 giorni  
- una sola volta  
- invalidare alla prima accettazione

---

## 🛡️ Admin — nuove sezioni e azioni

### A. Registrazioni
- **`GET /admin/registrations`** → tabella richieste con filtri per `status` (submitted, under_review, approved, rejected)
- **`GET /admin/registrations/<id>`** → dettaglio + pulsanti:
  - **Under review**: set `status='under_review'`
  - **Approve**:
     - Se `desired_lab_name` valorizzato e non esiste lab → creare `Lab` (slug sicuro)
     - Assegnare ruolo: se crea lab → `owner_lab`, altrimenti da `desired_role`
     - Creare/attivare `User` (se non esiste) **oppure** generare `activate token` ed inviare (opzionale)
     - Set `status='approved'`, `decided_at`, `decided_by`
  - **Reject**: set `status='rejected'` + `admin_note`
- **Template:**  
  - `templates/admin/registrations_list.html`
  - `registration_review.html`

### B. Inviti
- **`GET/POST /admin/labs/<lab_code>/users`**
  - Lista utenti del lab (email, ruoli)
  - Form “Invita utente”: `email`, `role`
  - Azione POST: crea `invite_token`, invia email con link `/auth/accept-invite?token=...`

> In sviluppo, al posto dell’email mostrare il link in pagina (debug banner).

---

## 🧭 Integrazione nel layout

- Nel menu Admin aggiungere “**Registrazioni**” e, nella pagina lab, tab “**Utenti & Inviti**”
- In navbar utente: se logged-in e senza `accepted_disclaimer_at` → banner “Devi accettare il disclaimer”

---

## 🧪 Validazioni & Sicurezza

- **Rate limit:** `/auth/register` e `/auth/login` (es. 5/min/IP)
- **reCAPTCHA:** (solo prod) su `/auth/register`
- **Password hashing:**  
  ```python
  werkzeug.security.generate_password_hash(pw, method="pbkdf2:sha256", salt_length=16)
  ```
- **Token:**  
  ```python
  secrets.token_urlsafe(48)
  ```
- **Scadenze:** `activate` 72h; `invite` 7d
- **Audit:** loggare `decided_by`, `decided_at`, `created_by` negli inviti

---

## 🌱 Seed & Demo

Aggiornare `scripts/seed_data.py`:
- Creare utente **admin** (`admin@ochem.local`, pw hash di `admin123!`, `is_active=True`, `accepted_disclaimer_at=now()`)
- Creare 2 lab (`lab_alpha`, `lab_beta`) e 2 owner (uno per lab) con password hash e disclaimer accettato
- (Opz) Inserire 1 `invite_token` valido per `lab_alpha` con ruolo `analyst` e stampare in console il link di invito

**Output seed (console):**
```
Admin: admin@ochem.local / admin123!
Invite demo: /auth/accept-invite?token=<...> (lab=lab_alpha, role=analyst, expires=YYYY-MM-DD)
```

---

## ✅ Criteri di accettazione (QA manuale)

1. **Autoregistrazione:** submit form → voce appare in `/admin/registrations` (status `submitted`)
2. **Approvazione:** Admin approva → se serve crea Lab; l’utente può attivarsi ed entrare
3. **Invito:** Admin crea invito da pagina lab; il link funziona e porta a set password + login
4. **Disclaimer:** dopo login, se non accettato → redirect a `/auth/disclaimer` e salva timestamp all’accettazione
5. **Permessi:**
    - utente non admin → 403 su `/admin/*`
    - utente senza ruolo su `lab_X` → 403 sulle route `lab_X`
6. **Indici:** le nuove tabelle hanno gli indici/elencati

---

## 📌 Note di implementazione

- Non usare ENUM DB: usare `String` + costanti Python (compatibile SQLite)
- Date/ora sempre in **UTC** (`timezone=True`)
- Nessun JSONB: per note usare `Text` o `VARCHAR` + formato JSON validato in app
- Per email in dev, usare **stampa console** del link; in prod integrare SMTP più avanti

---