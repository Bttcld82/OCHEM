# 🧩 ISTRUZIONE AGENTE VS CODE — MODULO ADMIN (OCHEM)

## 🎯 Obiettivo
Realizzare (o aggiornare) il **Blueprint Admin** all’interno di `app/blueprints/admin/` per gestire:
1. Validazione e pubblicazione dei **Cicli** e dei **Parametri** associati.  
2. Verifica e approvazione dei **PDF di prova (XPT/SigmaPT)**.  
3. Gestione dei **Laboratori** e degli **Utenti** con ruoli.  
4. Pannello di controllo amministrativo (dashboard).  

L’agente deve modificare o completare ciò che già esiste nella struttura corrente, senza cancellare il codice esistente ma adattandolo alle specifiche attuali.

---

## 📁 Struttura di riferimento (esistente)

app/
├── blueprints/
│ ├── admin/
│ │ ├── templates/
│ │ │ ├── admin_dashboard.html
│ │ │ ├── labs_form.html
│ │ │ ├── labs_list.html
│ │ │ ├── params_form.html
│ │ │ ├── params_list.html
│ │ ├── init.py
│ │ └── routes_admin.py
│ ├── main/
│ └── dati/
│
├── models.py
└── templates/

pgsql
Copy code

---

## 🧱 1. Blueprint: `admin_bp`

File: `app/blueprints/admin/routes_admin.py`

### A) Import e definizione base
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app import db
from app.models import Lab, User, Cycle, CycleParameter, DocFile, Parameter, Unit, Technique
from datetime import datetime

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")
🧩 2. FUNZIONALITÀ DA IMPLEMENTARE
🧭 2.1 Dashboard amministrativa
Template: admin_dashboard.html

Route:

python
Copy code
@admin_bp.route("/dashboard")
def dashboard():
    total_labs = db.session.query(Lab).count()
    total_cycles = db.session.query(Cycle).count()
    total_docs = db.session.query(DocFile).count()
    pending_cycles = db.session.query(Cycle).filter_by(status="pending_review").count()
    return render_template(
        "admin/admin_dashboard.html",
        total_labs=total_labs,
        total_cycles=total_cycles,
        total_docs=total_docs,
        pending_cycles=pending_cycles
    )
Contenuto pagina:

Statistiche riassuntive (laboratori, cicli, documenti).

Link rapidi: “Rivedi cicli in attesa”, “Gestisci laboratori”, “Elenco parametri”.

🧪 2.2 Revisione cicli (workflow)
Obiettivo: gestire lo stato dei cicli (draft → pending_review → published/rejected).

A) Lista cicli in revisione
python
Copy code
@admin_bp.route("/cycles/pending")
def cycles_pending():
    cycles = Cycle.query.filter(Cycle.status == "pending_review").all()
    return render_template("admin/cycles_pending.html", cycles=cycles)
Template: templates/admin/cycles_pending.html

Tabella con: codice ciclo, provider, data, numero parametri, stato.

Azioni: “Apri revisione”, “Approva”, “Rigetta”, “Richiedi modifiche”.

B) Revisione singolo ciclo
python
Copy code
@admin_bp.route("/cycles/<int:id>/review", methods=["GET", "POST"])
def cycle_review(id):
    cycle = Cycle.query.get_or_404(id)
    params = CycleParameter.query.filter_by(cycle_id=id).all()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "approve":
            cycle.status = "published"
            cycle.reviewed_by = "admin"
            cycle.reviewed_at = datetime.utcnow()
            db.session.commit()
            flash(f"Ciclo {cycle.code} pubblicato con successo.", "success")
        elif action == "reject":
            cycle.status = "rejected"
            db.session.commit()
            flash(f"Ciclo {cycle.code} rigettato.", "warning")
        elif action == "request_changes":
            cycle.status = "changes_requested"
            db.session.commit()
            flash(f"Ciclo {cycle.code}: richieste modifiche all’operatore.", "info")
        return redirect(url_for("admin_bp.cycles_pending"))

    return render_template("admin/cycle_review.html", cycle=cycle, params=params)
Template: cycle_review.html

Tabella parametri con colonne:

parameter.name

assigned_xpt

assigned_spt

doc_file.filename

Stato (draft/pending_review/published)

Pulsanti: “Approva”, “Richiedi modifiche”, “Rigetta”.

📄 2.3 Verifica PDF di prova (doc_file)
Obiettivo: assicurare che ogni cycle_parameter abbia doc_id con PDF valido prima della pubblicazione.

Route:
python
Copy code
@admin_bp.route("/docs/<int:id>/preview")
def doc_preview(id):
    doc = DocFile.query.get_or_404(id)
    return send_file(doc.storage_path, mimetype=doc.content_type)
Check automatico (da eseguire in cycle_review o pulsante dedicato):

python
Copy code
missing_pdf = [
    p for p in params if not p.doc_id or not p.assigned_xpt or not p.assigned_spt
]
if missing_pdf:
    flash(f"{len(missing_pdf)} parametri senza PDF o XPT/SigmaPT!", "danger")
🧪 2.4 Gestione Parametri (Admin)
Route:

python
Copy code
@admin_bp.route("/params")
def params_list():
    params = Parameter.query.all()
    return render_template("admin/params_list.html", params=params)
Form di creazione/validazione (params_form.html):

python
Copy code
@admin_bp.route("/params/new", methods=["GET", "POST"])
def params_new():
    if request.method == "POST":
        name = request.form["name"]
        code = request.form["code"]
        unit_id = request.form["unit_id"]
        param = Parameter(name=name, code=code, default_unit_id=unit_id)
        db.session.add(param)
        db.session.commit()
        flash("Parametro creato con successo.", "success")
        return redirect(url_for("admin_bp.params_list"))
    units = Unit.query.all()
    return render_template("admin/params_form.html", units=units)
🧪 2.5 Gestione Laboratori (Admin)
Lista laboratori:

python
Copy code
@admin_bp.route("/labs")
def labs_list():
    labs = Lab.query.all()
    return render_template("admin/labs_list.html", labs=labs)
Creazione nuovo laboratorio:

python
Copy code
@admin_bp.route("/labs/new", methods=["GET", "POST"])
def labs_new():
    if request.method == "POST":
        name = request.form["name"]
        slug = name.lower().replace(" ", "_")
        lab = Lab(name=name, slug=slug, created_at=datetime.utcnow())
        db.session.add(lab)
        db.session.commit()
        flash("Laboratorio creato con successo.", "success")
        return redirect(url_for("admin_bp.labs_list"))
    return render_template("admin/labs_form.html")
🧮 3. Template principali da aggiornare o creare
File	Scopo
admin_dashboard.html	Riepilogo generale e link rapidi
cycles_pending.html	Elenco cicli in revisione
cycle_review.html	Revisione e pubblicazione di un ciclo
params_list.html	Lista parametri globali
params_form.html	Form creazione parametro
labs_list.html	Elenco laboratori
labs_form.html	Form creazione laboratorio

Tutti i template devono estendere base.html e mostrare flashed messages.

⚖️ 4. Regole e validazioni Admin
Controllo	Azione
cycle.status='published' senza doc_id o assigned_xpt/spt → ❌	bloccare pubblicazione, flash errore
cycle_parameter.doc_id non esiste o file mancante → ❌	segnalare
cycle.status='pending_review' e nessun parameter → ⚠️	warning
cycle.status='published' → campi disabilitati in form	

🧾 5. Ruoli e accesso
Accesso al blueprint admin_bp riservato agli utenti con ruolo admin.

Decoratore @login_required e controllo:

python
Copy code
if not current_user.has_role('admin'):
    abort(403)
📋 6. Criteri di successo
L’admin può:

Vedere la dashboard e il riepilogo dati.

Approvare, rigettare o richiedere modifiche per un ciclo.

Visualizzare i PDF associati ai parametri del ciclo.

Creare nuovi parametri e laboratori.

Tutte le azioni mostrano flash() di conferma.

Tutti i template estendono base.html.

📅 Versione: 2025.10
🧑‍💻 Autore: Claudio Bettinelli
🔧 Progetto: OCHEM – Open Chemistry Data Platform
🏗️ Blueprint: admin_bp