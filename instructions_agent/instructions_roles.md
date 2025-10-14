# instructions_roles.md

## 🔑 ISTRUZIONE AGENTE VS CODE — GESTIONE RUOLI & ASSEGNAZIONI (OCHEM)

### 🎯 Obiettivo
Implementare la **gestione dei ruoli**:
- **Globali**: `admin`
- **Per laboratorio**: `owner_lab`, `analyst`, `viewer`
Integrata con UI admin e guardie esistenti, usando le tabelle già presenti (`user`, `lab`, `role`, `user_lab_role`) e le richieste/registrazioni create in precedenza.

---

### 📁 Ambito progetto da aggiornare
```
app/
blueprints/
admin/
    routes_admin.py ← AGGIORNARE
    templates/admin/
        users_list.html ← NUOVO
        user_detail.html ← NUOVO (opzionale)
        lab_users.html ← GIÀ PREVISTO/AGGIORNARE
auth/
    decorators.py ← AGGIORNARE (mappa gerarchia ruoli)
    models.py ← VERIFICARE vincoli/indici
migrations/
    versions/ ← SE NECESSARIO: indici/unique
scripts/
    seed_data.py ← AGGIORNARE (almeno 1 owner per lab)
```

---

### 🧱 Modello dati & vincoli (verifica/integrazione)
1. **role** (globale):
     - Deve contenere almeno: `admin`, `owner_lab`, `analyst`, `viewer`
     - Se non presenti, **seed** in migrazione o nel `seed_data.py`.

2. **user_lab_role**
     - Campi attesi: `user_id`, `lab_id` **o** `lab_code`, `role_id`
     - **UNIQUE(user_id, lab_id)** per evitare duplicati  
     - **CHECK** applicativo: per ogni `lab` deve esistere **≥ 1 `owner_lab`**

3. **user**
     - Campo `is_active` e (già presente) `accepted_disclaimer_at`

> Se manca `UNIQUE(user_id, lab_id)` su SQLite, creare migrazione Alembic **batch** per aggiungerlo.

---

### 🧭 Gerarchia ruoli (da usare nei controlli)
- **Globale**: `admin` > (nessun altro)
- **Lab**: `owner_lab` > `analyst` > `viewer`

Aggiornare `auth/decorators.py`:
- `def has_lab_min_role(user, lab, min_role) -> bool`
- `@lab_role_required(min_role="viewer")` usa la gerarchia sopra.

---

### 🛠️ UI Admin — Pagine/Route da creare o aggiornare

#### 1) Elenco utenti globali
**Route:** `GET /admin/users`
- Tabella con: `email`, `is_active`, **ruoli globali** (badge `admin` se presente), numero di lab associati.
- Azioni (riga):
    - “Imposta Admin / Rimuovi Admin”
    - “Dettaglio utente” (`/admin/users/<id>`)

**Template:** `templates/admin/users_list.html`

**Azioni POST:**
- `POST /admin/users/<id>/make-admin`
- `POST /admin/users/<id>/remove-admin`

> Se usi `role` come tabella unica per globali & lab, la flag `admin` può essere un record in `user_lab_role` con `lab_id=NULL`. In alternativa, mantieni un flag `is_admin` su `user`. Scegli la soluzione già adottata nel tuo progetto e mantienila coerente.

---

#### 2) Dettaglio utente (opzionale ma utile)
**Route:** `GET /admin/users/<id>`
- Mostra: email, stato, data ultimo login, **laboratori associati** con ruolo.
- Azioni:
    - “Rimuovi dal laboratorio”
    - “Cambia ruolo nel laboratorio” (select: owner/analyst/viewer)
    - “Aggiungi al laboratorio” (select lab + ruolo)

**Route POST:**
- `POST /admin/users/<id>/labs/add`
- `POST /admin/users/<id>/labs/<lab_id>/update-role`
- `POST /admin/users/<id>/labs/<lab_id>/remove`

**Template:** `templates/admin/user_detail.html`

---

#### 3) Utenti del laboratorio (pagina dal lab)
**Route:** `GET /admin/labs/<lab_code>/users`
- Tabella con: `email`, ruolo lab, azioni.
- Pulsanti:
    - “Cambia ruolo”
    - “Rimuovi dal lab”
    - “Aggiungi utente esistente” (email → aggiungi con ruolo scelto)
    - “Invita utente” (già previsto nel flusso inviti)

**Route POST:**
- `POST /admin/labs/<lab_code>/users/add-existing` (email + ruolo)
- `POST /admin/labs/<lab_code>/users/<user_id>/update-role`
- `POST /admin/labs/<lab_code>/users/<user_id>/remove`

**Vincolo forte (backend + UI):**
- Non consentire di rimuovere **l’ultimo** `owner_lab` del laboratorio; mostrare alert.

**Template:** `templates/admin/lab_users.html` (aggiornare se già esiste)

---

### 🔒 Convalide & regole operative
- **Ruoli consentiti per-lab**: solo `owner_lab`, `analyst`, `viewer`  
- **Cambio ruolo**: ammesso in qualsiasi momento **tranne** degradare l’**ultimo owner** → bloccare.
- **Rimozione utente dal lab**: se è l’ultimo owner → bloccare.
- **Make/Remove Admin**: disponibile solo per altri utenti (non su sé stessi) per evitare lock-out; almeno 1 admin deve rimanere nel sistema (controllo lato backend).

---

### ⚙️ Service layer (consigliato)
Creare funzioni riusabili (in `app/services/roles.py`):
- `assign_lab_role(user_id, lab_id, role_name)`
- `change_lab_role(user_id, lab_id, role_name)`
- `remove_lab_role(user_id, lab_id)`
- `ensure_at_least_one_owner(lab_id)` → lancia eccezione se violato
- `make_admin(user_id)` / `remove_admin(user_id)` (se il modello lo prevede)
- funzioni di **lookup**: utenti per lab, lab per utente

> Così le route restano leggere, e puoi testare la logica separatamente.

---

### 🌱 Seed & QA
Aggiornare `scripts/seed_data.py`:
- Garantire **≥1 `owner_lab`** per ogni lab seed.
- Aggiungere un paio di utenti `analyst` o `viewer` di esempio.
- Se usi admin come ruolo globale: creare admin e assegnargli tale ruolo (o `is_admin=True`).

---

### 🧪 Casi di test manuali (accettazione)
1. **Lista utenti globali** mostra correttamente badge admin e conteggio lab.  
2. **Make/Remove admin** funziona; non si può rimuovere l’ultimo admin del sistema.  
3. **Pagina lab utenti**:
     - aggiungi utente esistente con ruolo `analyst`  
     - cambia ruolo `analyst → viewer`  
     - prova a rimuovere l’ultimo `owner_lab` ⇒ **bloccato** con messaggio chiaro  
4. **Guardie**:
     - utente non admin → **403** su `/admin/users*`  
     - `@lab_role_required("analyst")` blocca un `viewer` in una route di upload  
5. **Persistenza**: reload e verifica che le modifiche ai ruoli siano in DB (`user_lab_role`).

---

### 🧷 Sicurezza & UX
- CSRF attivo sui POST (se usi Flask-WTF).  
- Flash messages chiari (“Ruolo aggiornato”, “Impossibile rimuovere l’ultimo owner”).  
- Conferma (modal) prima di rimozioni e downgrade critici.  
- Log applicativo su cambi ruolo (chi ha fatto cosa, quando).

---

### ✅ Criteri di completamento
- UI admin per **assegnare/cambiare/rimuovere ruoli** globali e di laboratorio operativa.  
- Vincolo “**almeno un owner per lab**” rispettato a livello applicativo.  
- Guardie funzionanti con gerarchia `owner > analyst > viewer`.  
- Seed aggiornato e test manuali superati.

---