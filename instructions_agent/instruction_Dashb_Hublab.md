# 🧭 ISTRUZIONE AGENTE VS CODE — DASHBOARD UTENTE & HUB LAB (OCHEM)

## 🎯 Obiettivo
Implementare la **UI lato laboratorio**:
1) **Dashboard utente** `/dashboard` con i laboratori a cui appartiene e i relativi ruoli.  
2) **Hub laboratorio** `/l/<lab_code>` con panoramica e link rapidi (Cicli, QC, Documenti).  
3) Navigazione protetta da `@login_required` e `@lab_role_required("viewer")`.

Non modificare quanto già esiste; integrare con `auth_bp` e `admin_bp`.

---

## 📁 Struttura interessata
## 📁 Struttura interessata

```
app/
    blueprints/
        main/
            __init__.py
            routes_main.py   # ← CREARE/AGGIORNARE
    templates/
        main/
            dashboard.html   # ← NUOVO
            lab_hub.html     # ← NUOVO
            _cards/
                card_cycles.html   # ← NUOVO
                card_uploads.html  # ← NUOVO
                card_qc.html       # ← NUOVO
    templates/
        base.html         # ← navbar già integra login/logout
    models.py
```

---

## 🔐 Guardie & permessi
- Tutte le route: `@login_required`.
- Rotte per-lab: `@lab_role_required("viewer")` (già definito in `auth/decorators.py`).
- Recupero `lab_code` dalla URL: `/l/<lab_code>`.

---

## 🧱 Query e dati (SQLAlchemy)
### Per `/dashboard`:
- Laboratori dell’utente corrente con ruolo: join `user_lab_role` → `lab`.
- Conteggi rapidi:
  - `cycle` pubblicati recenti (ultimi N, opzionale)
  - numero upload utente/lab (da `upload_file`)

### Per `/l/<lab_code>`:
- Info lab: nome, slug/`lab_code`.
- **Cicli pubblicati** (ultimi 5): `cycle.status='published'` (se serve, filtra per provider).
- **Ultimi upload** (ultimi 10): da `upload_file` per `lab_code`.
- **Parametri attivi** (opz.): `cycle_parameter` del ciclo pubblicato più recente.
- Link a:
  - `/app/cycles/...` (revisione/uso cicli quando sarà pronto)
  - `/app/qc/template.csv` (prossimo step)
  - `/app/qc/upload`
  - `/app/qc/carte`

---

## 🧑‍💻 Route da implementare (Blueprint `main_bp`)
File: `app/blueprints/main/routes_main.py`

### 1) `GET /dashboard`
- Recupera tutti i lab dell’utente con ruolo.
- Render `main/dashboard.html` con tabella:
  - Colonne: **Laboratorio**, **Ruolo**, **Azioni**
  - Azioni: “Apri hub” → `/l/<lab_code>`

### 2) `GET /l/<lab_code>`
- Verifica permesso `viewer+`.
- Compone 3 “card” (inclusioni template):
  - **Cicli pubblicati recenti**: lista con `code`, `start_date`, `end_date`
  - **Ultimi upload**: tabella (filename, righe, data)
  - **QC**: link rapidi a `template.csv`, `upload`, `carte`
- Render `main/lab_hub.html`.

---

## 🖼️ Template (Jinja)
### `templates/main/dashboard.html`
- Titolo: “I miei laboratori”
- Tabella:
  - `{{ lab.name }}` / `{{ lab.slug }}` / `{{ role.name }}` / `Apri`
- Se nessun lab: messaggio e link “Contatta admin / Invia richiesta”.

### `templates/main/lab_hub.html`
- Header con nome lab e ruolo corrente.
- Include:
  - `{% include 'main/_cards/card_cycles.html' %}`
  - `{% include 'main/_cards/card_uploads.html' %}`
  - `{% include 'main/_cards/card_qc.html' %}`

### `templates/main/_cards/card_cycles.html`
- Card con tabella 5 righe max:
  - `code`, `start_date`, `end_date`, `status` (badge “published”)
- Link “Vedi tutti i cicli” (placeholder).

### `templates/main/_cards/card_uploads.html`
- Card con ultimi 10 upload:
  - `filename`, `rows`, `received_at` (formato leggibile)
- Link “Tutti gli upload” (placeholder).

### `templates/main/_cards/card_qc.html`
- Card con 3 pulsanti:
  - “Scarica **template CSV**”
  - “**Upload risultati**”
  - “Apri **Carte**”
- I link possono puntare a placeholder `/app/qc/...` (verranno implementati nello step successivo).

---

## 🎯 UX & dettagli
- Navbar: evidenziare “Dashboard” quando attiva.
- In hub lab, mostra il **ruolo** dell’utente (badge: owner/analyst/viewer).
- Se utente è **owner_lab**, mostra in una sidebar (o badge) link “Gestisci utenti lab” → `/admin/labs/<lab_code>/users`.
- Tutte le date in **UTC → locale** (puoi lasciare formato ISO per ora).

---

## 🧪 Criteri di accettazione (QA manuale)
1. Login come **owner_lab** → `/dashboard` mostra i suoi lab e ruoli.  
2. Click su un lab → `/l/<lab_code>` mostra 3 card con dati coerenti.  
3. Un utente senza ruolo per quel lab → 403 su `/l/<lab_code>`.  
4. Se **non autenticato** → redirect a `/auth/login`.  
5. Link QC presenti (anche se placeholder): template, upload, carte.

---

## 📌 Step successivo (a seguire)
Dopo il merge di questa consegna, creare l’MVP QC:
- `GET /l/<lab>/app/qc/template.csv`
- `GET/POST /l/<lab>/app/qc/upload` (validazioni + salvataggi + calcolo sincrono)
- `GET /l/<lab>/app/qc/carte` (Plotly, UCL/LCL ±3)

(vedi prossimo documento: **`instruction_qc_mvp.md`**)