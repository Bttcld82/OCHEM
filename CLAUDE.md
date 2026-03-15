# OCHEM - Proficiency Testing Platform

## Panoramica Progetto
OCHEM e' una piattaforma web per la gestione di **Proficiency Testing (PT)** tra laboratori chimici.
Permette a laboratori di partecipare a cicli di prove interlaboratorio, caricare risultati,
calcolare z-score e visualizzare carte di controllo qualita'.

## Stack Tecnologico
- **Backend:** Python 3.11+ / Flask 3.x
- **Database:** SQLite via SQLAlchemy 2.x + Alembic (migrazioni)
- **Auth:** Flask-Login + werkzeug password hashing
- **Frontend:** Template Jinja2 + Bootstrap + Plotly (grafici)
- **Calcoli:** pandas, numpy (z-score, sz2, rsz con MAD_K=1.4826)

## Struttura Progetto
```
OCHEM/
├── app/
│   ├── __init__.py          # Factory create_app(), init estensioni
│   ├── models.py            # Tutti i modelli SQLAlchemy (18 tabelle)
│   ├── forms.py             # WTForms
│   ├── services/            # Business logic (roles.py)
│   ├── blueprints/
│   │   ├── main/            # Dashboard utente, Hub laboratorio
│   │   ├── admin/           # Pannello admin (cicli, lab, utenti, parametri)
│   │   ├── auth/            # Login, logout, disclaimer, registrazione, inviti
│   │   ├── dati/            # Upload dati
│   │   └── stats/           # Statistiche, grafici, upload CSV risultati
│   └── templates/           # Template Jinja2
├── config.py                # Configurazione Flask (DB, upload, CSRF)
├── migrations/              # Alembic migrations
├── scripts/                 # Script seed e init DB
├── instructions_agent/      # Documentazione requisiti (7 file .md)
├── requirements.txt         # Dipendenze Python
├── manage.py                # Entry point
└── wsgi.py                  # WSGI entry point
```

## Modello Dati (Tabelle Principali)
- **Core:** User, Lab, Role, UserLabRole
- **Anagrafiche:** Unit, Matrix, Parameter, Technique, Provider
- **Documenti:** DocFile, CycleDoc
- **Cicli:** Cycle (draft/published), CycleParameter (xpt, sigma_pt)
- **Partecipazioni:** LabParticipation, Result
- **QC:** ZScore (z, sz2), PtStats (mean_z, rsz), ControlChartConfig
- **Audit:** UploadFile, JobLog
- **Auth:** RegistrationRequest, InviteToken

## Sistema Ruoli
- **Globale:** `admin` (campo is_admin su User)
- **Per laboratorio:** `owner_lab` > `analyst` > `viewer` (tabella user_lab_role)
- Decoratori: `@role_required('admin')`, `@lab_role_required('viewer'|'analyst'|'owner_lab')`

## Funzionalita' Implementate (da commit history)
1. DB e sistema admin
2. Autenticazione (login/logout/disclaimer)
3. Ruoli (globali + per laboratorio)
4. LabHub (dashboard utente + hub laboratorio)
5. Multiselect dipendente
6. Grafici Z-score (carte di controllo)

## Comandi Utili
```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Database
alembic upgrade head
python scripts/seed_data.py

# Run
flask run  # oppure python manage.py
```

## Convenzioni
- Lingua codice: inglese per nomi variabili/funzioni, italiano per messaggi UI
- Foreign key spesso su codici naturali (lab.code, cycle.code, parameter.code) anziche' su id
- Blueprint pattern con url_prefix
- Template: base.html con blocchi content, Bootstrap 5
