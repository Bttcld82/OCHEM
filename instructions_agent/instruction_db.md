# 🧩 ISTRUZIONE AGENTE VS CODE – CREAZIONE DATABASE E DATI DI TEST (OCHEM)

## 🎯 Obiettivo
Creare e popolare il database **SQLite (`instance/ochem.sqlite3`)** per il progetto **OCHEM**, secondo lo schema approvato.  
Lo script deve:
1. Inizializzare il DB via **Alembic**.  
2. Popolare i dati base (unità, parametri, tecniche, provider, laboratori, cicli, risultati).  
3. Calcolare `z`, `sz2`, `rsz` e salvare statistiche (`pt_stats`).

---

## 📁 Struttura del progetto (riferimento attuale)
OCHEM/
│
├── app/
│ ├── blueprints/
│ │ ├── admin/
│ │ │ ├── templates/
│ │ │ │ ├── admin_dashboard.html
│ │ │ │ ├── labs_form.html
│ │ │ │ ├── labs_list.html
│ │ │ │ ├── params_form.html
│ │ │ │ └── params_list.html
│ │ │ ├── init.py
│ │ │ └── routes_admin.py
│ │ ├── main/
│ │ └── dati/
│ ├── templates/
│ │ ├── base.html
│ │ ├── flash.html
│ │ ├── login.html
│ │ └── _partials/
│ ├── static/
│ ├── models.py
│ └── init.py
│
├── deploy/
│
├── instance/
│ └── ochem.sqlite3
│
├── migrations/
│ ├── versions/
│ ├── env.py
│ ├── README
│ ├── alembic.ini
│ └── script.py.mako
│
├── scripts/
│ └── seed_data.py ← (da creare)
│
├── instructions_agent/
│ └── instruction_db.md ← (questo file)
│
├── requirements.txt
└── README.md

yaml
Copy code

---

## ⚙️ 1. Requisiti
- Python 3.11+
- SQLite 3.x
- Pacchetti:  
  ```bash
  pip install SQLAlchemy alembic python-dotenv Faker pandas numpy
Variabile d’ambiente:

ini
Copy code
DATABASE_URL=sqlite:///instance/ochem.sqlite3
🧱 2. Struttura dati (sintesi tabelle principali)
Categoria	Tabelle principali	Descrizione
Core	user, lab, role, user_lab_role	utenti, laboratori, ruoli
Anagrafiche	unit, matrix, parameter, technique, provider	dati di base
Documenti	doc_file, cycle_doc	PDF e allegati dei cicli
Cicli	cycle, cycle_parameter	definizione dei cicli e parametri associati
Partecipazioni	lab_participation, result	risultati caricati dai laboratori
Derivati QC	z_score, pt_stats, control_chart_config	z, sz², rsz, limiti carte
Audit	upload_file, job_log	log caricamenti e calcoli

🧩 3. Script di creazione DB
File: scripts/init_db.py

Istruzioni per l’agente:

Leggere DATABASE_URL da .env.

Creare un engine SQLAlchemy e connettersi.

Applicare PRAGMA SQLite:

python
Copy code
with engine.connect() as conn:
    conn.execute(sa.text("PRAGMA foreign_keys=ON;"))
    conn.execute(sa.text("PRAGMA journal_mode=WAL;"))
Eseguire:

bash
Copy code
alembic upgrade head
Verificare la creazione di instance/ochem.sqlite3.

🌱 4. Script di popolamento (Faker + calcoli)
File: scripts/seed_data.py

Obiettivo
Creare dati realistici per testare le funzioni base e le carte di controllo.

Contenuti
Entità	Dati generati
unit	mg/L, µS/cm, pH
parameter	NH₄⁺, NO₃⁻, TOC
technique	POTENZ, SPETTRO
provider	UNICHIM
lab	LAB_ALPHA, LAB_BETA
cycle	2025-01 (published), 2025-02 (draft)
cycle_parameter	3 parametri per ciclo, XPT/SigmaPT casuali
user	2 owner, accepted_disclaimer_at = now()
lab_participation	ogni lab in ciclo 2025-01
result	100 risultati casuali
z_score / pt_stats	calcolati da pandas (robusto)
control_chart_config	CL=0, UCL=±3, LCL=±3

Calcolo (semplificato)
python
Copy code
import pandas as pd, numpy as np
MAD_K = 1.4826

z = (x - xpt)/spt
sz2 = z**2
rsz = MAD_K * abs(z - np.median(z)).median()
Output finale
ochem.sqlite3 popolato con dati dimostrativi.

Stampa riepilogo a console:

yaml
Copy code
Cicli pubblicati: 1
Laboratori: 2
Risultati: 100
Z-score calcolati: 100
Statistiche PT: 6
🔍 5. Comandi da eseguire
bash
Copy code
# 1. Crea ambiente virtuale
python -m venv .venv
source .venv/bin/activate

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Crea DB con Alembic
alembic upgrade head

# 4. Popola dati di esempio
python scripts/seed_data.py
📋 6. Validazione
Dopo il popolamento:

sql
Copy code
-- Verifica numero record
SELECT COUNT(*) FROM cycle;
SELECT COUNT(*) FROM result;
SELECT COUNT(*) FROM z_score;
SELECT * FROM pt_stats LIMIT 5;
Controlla che:

I cicli pubblicati abbiano status='published' e doc_id non nullo.

z_score contenga lo stesso numero di righe di result.

Ogni pt_stats raggruppi un ciclo, un parametro e un laboratorio.

📦 7. Note per migrazione futura a Postgres
Nessun JSON nativo: usare TEXT + validazione.

Tipi Numeric(18,6) per valori misurati.

DateTime(timezone=True) già compatibile.

Enum → String(32) + vincoli logici.

FK con ondelete='CASCADE'.

Basterà modificare DATABASE_URL e rieseguire alembic upgrade head.

✅ 8. Criteri di successo
File instance/ochem.sqlite3 generato e popolato.

Tutte le tabelle create senza errori.

Seed completato con almeno:

2 laboratori

1 ciclo pubblicato

≥ 100 risultati con z-score calcolati.

📅 Versione: 2025.10
🧑‍💻 Autore: Claudio Bettinelli
🔧 Progetto: OCHEM — Open Chemistry Data Platform