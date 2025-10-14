# 🧩 ISTRUZIONE AGENTE VS CODE — MODULO ADMIN (OCHEM)

## 🎯 Obiettivo
Aggiornare o completare il **Blueprint Admin** in `app/blueprints/admin/` per gestire:
1. Validazione e pubblicazione di **Cicli** e relativi **Parametri**
2. Verifica e approvazione dei **PDF di prova (XPT/SigmaPT)**
3. Gestione di **Laboratori** e **Utenti** con ruoli
4. Pannello di controllo amministrativo (dashboard)

L’agente deve adattare la struttura esistente senza rimuovere codice, ma aggiornandolo secondo le specifiche.

---

## 📁 Struttura di riferimento

```
app/
├── blueprints/
│   ├── admin/
│   │   ├── templates/
│   │   │   ├── admin_dashboard.html
│   │   │   ├── labs_form.html
│   │   │   ├── labs_list.html
│   │   │   ├── params_form.html
│   │   │   ├── params_list.html
│   │   ├── init.py
│   │   └── routes_admin.py
│   ├── main/
│   └── dati/
├── models.py
└── templates/
```

---

## 🧱 1. Blueprint: `admin_bp`

**File:** `app/blueprints/admin/routes_admin.py`

### Import e definizione base

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app import db
from app.models import Lab, User, Cycle, CycleParameter, DocFile, Parameter, Unit, Technique
from datetime import datetime

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")
```

---

## 🧭 2. Funzionalità da implementare

### 2.1 Dashboard amministrativa

**Route:**
```python
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
```
**Contenuto:** Statistiche riassuntive e link rapidi (“Rivedi cicli in attesa”, “Gestisci laboratori”, “Elenco parametri”).

---

### 2.2 Revisione cicli (workflow)

**A) Lista cicli in revisione**
```python
@admin_bp.route("/cycles/pending")
def cycles_pending():
    cycles = Cycle.query.filter(Cycle.status == "pending_review").all()
    return render_template("admin/cycles_pending.html", cycles=cycles)
```
Tabella: codice ciclo, provider, data, numero parametri, stato.  
Azioni: “Apri revisione”, “Approva”, “Rigetta”, “Richiedi modifiche”.

**B) Revisione singolo ciclo**
```python
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
```
Tabella parametri: `parameter.name`, `assigned_xpt`, `assigned_spt`, `doc_file.filename`, stato.  
Pulsanti: “Approva”, “Richiedi modifiche”, “Rigetta”.

---

### 2.3 Verifica PDF di prova (doc_file)

**Route:**
```python
@admin_bp.route("/docs/<int:id>/preview")
def doc_preview(id):
    doc = DocFile.query.get_or_404(id)
    return send_file(doc.storage_path, mimetype=doc.content_type)
```
**Check automatico (in cycle_review o pulsante dedicato):**
```python
missing_pdf = [
    p for p in params if not p.doc_id or not p.assigned_xpt or not p.assigned_spt
]
if missing_pdf:
    flash(f"{len(missing_pdf)} parametri senza PDF o XPT/SigmaPT!", "danger")
```

---

### 2.4 Gestione Parametri (Admin)

**Lista parametri:**
```python
@admin_bp.route("/params")
def params_list():
    params = Parameter.query.all()
    return render_template("admin/params_list.html", params=params)
```
**Form creazione/validazione:**
```python
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
```

---

### 2.5 Gestione Laboratori (Admin)

**Lista laboratori:**
```python
@admin_bp.route("/labs")
def labs_list():
    labs = Lab.query.all()
    return render_template("admin/labs_list.html", labs=labs)
```
**Creazione nuovo laboratorio:**
```python
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
```

---

## 🧮 3. Template principali

| File                | Scopo                                 |
|---------------------|---------------------------------------|
| admin_dashboard.html| Riepilogo generale e link rapidi      |
| cycles_pending.html | Elenco cicli in revisione             |
| cycle_review.html   | Revisione e pubblicazione di un ciclo |
| params_list.html    | Lista parametri globali               |
| params_form.html    | Form creazione parametro              |
| labs_list.html      | Elenco laboratori                     |
| labs_form.html      | Form creazione laboratorio            |

Tutti i template devono estendere `base.html` e mostrare messaggi flash.

---

## ⚖️ 4. Regole e validazioni Admin

| Controllo                                                        | Azione                       |
|------------------------------------------------------------------|------------------------------|
| cycle.status='published' senza doc_id o assigned_xpt/spt         | Bloccare pubblicazione, errore flash |
| cycle_parameter.doc_id non esiste o file mancante                | Segnalare                    |
| cycle.status='pending_review' e nessun parameter                 | Warning                      |
| cycle.status='published'                                         | Campi disabilitati in form   |

---

## 🧾 5. Ruoli e accesso

Accesso a `admin_bp` riservato agli utenti con ruolo admin.  
Decoratore `@login_required` e controllo:

```python
if not current_user.has_role('admin'):
    abort(403)
```

---

## 📋 6. Criteri di successo

L’admin può:
- Vedere la dashboard e il riepilogo dati
- Approvare, rigettare o richiedere modifiche per un ciclo
- Visualizzare i PDF associati ai parametri del ciclo
- Creare nuovi parametri e laboratori
- Tutte le azioni mostrano `flash()` di conferma
- Tutti i template estendono `base.html`

---

📅 Versione: 2025.10  
🧑‍💻 Autore: Claudio Bettinelli  
🔧 Progetto: OCHEM – Open Chemistry Data Platform  
🏗️ Blueprint: admin_bp
