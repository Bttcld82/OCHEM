---
title: "Database e Tabelle"
description: "Schema del database SQLite di OCHEM: struttura delle 18 tabelle, colonne e relazioni"
tags: [admin, database, schema, tabelle]
role: admin
order: 6
related:
  - admin/00-panoramica
  - admin/01-cicli
  - admin/03-parametri-unita
---

# Database e Tabelle

OCHEM usa **SQLite** come database relazionale, gestito tramite **SQLAlchemy 2.x** e migrazioni **Alembic**.
Il file del database si trova in `instance/ochem.sqlite3` (path configurabile in `config.py`).

---

## Schema generale

Il database è organizzato in 6 gruppi logici:

```
┌─────────────────────────────────────────────────────────────────┐
│  CORE             │  ANAGRAFICHE      │  CICLI                  │
│  user             │  unit             │  cycle                  │
│  lab              │  matrix           │  cycle_parameter        │
│  role             │  parameter        │                         │
│  user_lab_role    │  technique        │                         │
│                   │  provider         │                         │
├─────────────────────────────────────────────────────────────────┤
│  PARTECIPAZIONI   │  QC / STATISTICHE │  AUDIT / AUTH           │
│  lab_participation│  z_score          │  upload_file            │
│  result           │  pt_stats         │  job_log                │
│                   │  control_chart_   │  registration_request   │
│                   │  config           │  invite_token           │
│                   │                   │  doc_file               │
│                   │                   │  cycle_doc              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Gruppo CORE

### `user`
Utenti della piattaforma.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `email` | String(120) | univoca |
| `first_name` | String(80) | |
| `last_name` | String(80) | |
| `password_hash` | String(255) | werkzeug hash |
| `is_admin` | Boolean | accesso pannello admin |
| `is_active` | Boolean | default True |
| `accepted_disclaimer_at` | DateTime | null = disclaimer non accettato |
| `last_login_at` | DateTime | |
| `created_at` / `updated_at` | DateTime | |

### `lab`
Laboratori partecipanti.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `code` | String(50) | chiave naturale univoca |
| `name` | String(200) | |
| `city` | String(100) | opzionale |
| `contact_email` | String(120) | opzionale |
| `contact_phone` | String(30) | opzionale |
| `is_active` | Boolean | |
| `created_at` / `updated_at` | DateTime | |

### `role`
Ruoli disponibili nel sistema (seed iniziale: `owner_lab`, `analyst`, `viewer`).

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `name` | String(50) | univoco |
| `description` | String(200) | |

### `user_lab_role`
Associazione molti-a-molti tra utente, laboratorio e ruolo.
Un utente può avere **un solo ruolo** per laboratorio (vincolo `UNIQUE(user_id, lab_id)`).

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `user_id` | FK → user.id | |
| `lab_id` | FK → lab.id | |
| `role_id` | FK → role.id | |
| `assigned_at` | DateTime | |

---

## Gruppo ANAGRAFICHE

### `unit`
Unità di misura (es. `mg/L`, `µg/kg`).

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `code` | String(20) | chiave naturale univoca |
| `description` | String(200) | |

### `matrix`
Matrici analitiche (es. `acqua`, `suolo`, `aria`).

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `code` | String(20) | chiave naturale univoca |
| `description` | String(200) | |

### `parameter`
Parametri analitici misurabili.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `code` | String(20) | chiave naturale univoca |
| `name` | String(200) | |
| `unit_code` | FK → unit.code | |
| `technique_id` | FK → technique.id | opzionale |
| `matrix` | String(100) | campo libero opzionale |
| `min_value` / `max_value` | Float | range accettabile |
| `precision_digits` | Integer | cifre decimali |
| `active` | Boolean | |

### `technique`
Tecniche analitiche (es. `ICP-MS`, `HPLC`).

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `code` | String(20) | univoco |
| `name` | String(200) | |

### `provider`
Enti organizzatori dei cicli PT.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `code` | String(20) | univoco |
| `name` | String(200) | |

---

## Gruppo CICLI

### `cycle`
Cicli di Proficiency Testing.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `code` | String(20) | chiave naturale univoca |
| `name` | String(200) | |
| `status` | String(20) | `draft` → `published` |
| `provider_id` | FK → provider.id | opzionale |
| `doc_id` | FK → doc_file.id | documento principale opzionale |
| `start_date` / `end_date` | DateTime | |

### `cycle_parameter`
Parametri inclusi in un ciclo, con i valori di riferimento PT.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `cycle_code` | FK → cycle.code | |
| `parameter_code` | FK → parameter.code | |
| `xpt` | Numeric(18,6) | valore assegnato (valore vero) |
| `sigma_pt` | Numeric(18,6) | deviazione standard del PT |

> `xpt` e `sigma_pt` sono i parametri fondamentali per il calcolo dello z-score:
> `z = (risultato - xpt) / sigma_pt`

---

## Gruppo PARTECIPAZIONI

### `lab_participation`
Iscrizione di un laboratorio a un ciclo.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `lab_code` | FK → lab.code | |
| `cycle_code` | FK → cycle.code | |
| `status` | String(20) | `active`, ecc. |
| `registered_at` | DateTime | |

### `result`
Risultati analitici inviati dai laboratori.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `lab_code` | FK → lab.code | |
| `cycle_code` | FK → cycle.code | |
| `parameter_code` | FK → parameter.code | |
| `technique_code` | FK → technique.code | opzionale |
| `lab_participation_id` | FK → lab_participation.id | opzionale |
| `measured_value` | Numeric(18,6) | valore misurato |
| `uncertainty` | Numeric(18,6) | incertezza opzionale |
| `notes` | Text | note libere |
| `submitted_at` | DateTime | |

---

## Gruppo QC / STATISTICHE

### `z_score`
Z-score calcolati per ogni risultato.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `result_id` | FK → result.id | 1:1 con result |
| `z` | Numeric(18,6) | z-score standard |
| `sz2` | Numeric(18,6) | z-score robusto (MAD_K=1.4826) |

### `pt_stats`
Statistiche aggregate per laboratorio/ciclo/parametro.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `cycle_code` | FK → cycle.code | |
| `parameter_code` | FK → parameter.code | |
| `lab_code` | FK → lab.code | |
| `n_results` | Integer | numero risultati |
| `mean_z` | Numeric(18,6) | z medio |
| `rsz` | Numeric(18,6) | z-score robusto aggregato |

### `control_chart_config`
Configurazione delle carte di controllo qualità.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `name` | String(100) | |
| `chart_type` | String(50) | tipo carta |
| `center_line` | Numeric(18,6) | linea centrale |
| `upper_control_limit` | Numeric(18,6) | UCL |
| `lower_control_limit` | Numeric(18,6) | LCL |
| `upper_warning_limit` | Numeric(18,6) | UWL opzionale |
| `lower_warning_limit` | Numeric(18,6) | LWL opzionale |

---

## Gruppo DOCUMENTI

### `doc_file`
File PDF/documenti caricati sul server.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `filename` | String(255) | nome salvato su disco (univoco) |
| `original_filename` | String(255) | nome originale |
| `file_size` | Integer | byte |
| `mime_type` | String(100) | |
| `uploaded_at` | DateTime | |

### `cycle_doc`
Collegamento tra documenti e cicli (un ciclo può avere più documenti di tipo diverso).

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `cycle_code` | FK → cycle.code | |
| `doc_id` | FK → doc_file.id | |
| `doc_type` | String(50) | es. `istruzioni`, `risultati` |

---

## Gruppo AUDIT / AUTH

### `upload_file`
Traccia storica di ogni file CSV caricato dai laboratori.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `filename` | String(255) | nome su disco |
| `original_filename` | String(255) | |
| `lab_code` | FK → lab.code | |
| `cycle_code` | FK → cycle.code | |
| `uploaded_by` | FK → user.id | |
| `uploaded_at` | DateTime | |
| `processed_at` | DateTime | null = non ancora elaborato |
| `status` | String(20) | `pending`, `processed`, `error` |

### `job_log`
Log dei job di elaborazione in background.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `job_type` | String(50) | tipo operazione |
| `status` | String(20) | |
| `started_at` | DateTime | |
| `completed_at` | DateTime | |
| `error_message` | Text | |
| `details` | Text | |

### `registration_request`
Richieste di registrazione autonoma (senza invito).

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `email` | String(120) | |
| `full_name` | String(160) | |
| `desired_lab_name` | String(100) | nuovo lab richiesto |
| `target_lab_code` | String(20) | lab esistente a cui aderire |
| `desired_role` | String(20) | default `owner_lab` |
| `status` | String(20) | `submitted` → `approved`/`rejected` |
| `admin_note` | Text | note dell'admin |
| `created_at` | DateTime | |
| `decided_at` | DateTime | |
| `decided_by` | String(120) | email admin che ha deciso |

### `invite_token`
Token di invito generati dall'admin per l'accesso diretto.

| Colonna | Tipo | Note |
|---------|------|------|
| `id` | Integer PK | |
| `lab_code` | FK → lab.code | |
| `email` | String(120) | destinatario invito |
| `role` | String(20) | ruolo assegnato |
| `token` | String(96) | token casuale univoco |
| `expires_at` | DateTime | scadenza (default +7 giorni) |
| `used_at` | DateTime | null = non ancora usato |
| `created_by` | String(120) | email admin che ha creato |

---

## Convenzioni chiavi esterne

La maggior parte delle FK usa **codici naturali** anziché ID numerici:
- `lab.code` invece di `lab.id`
- `cycle.code` invece di `cycle.id`
- `parameter.code` invece di `parameter.id`

Questo semplifica le query e rende i dati leggibili direttamente nel DB.

---

## Comandi utili

```bash
# Applicare migrazioni pendenti
alembic upgrade head

# Creare una nuova migrazione dopo modifiche ai modelli
alembic revision --autogenerate -m "descrizione modifica"

# Vedere lo stato corrente delle migrazioni
alembic current

# Aprire il DB con sqlite3 (solo lettura)
sqlite3 instance/ochem.sqlite3 ".tables"
```
