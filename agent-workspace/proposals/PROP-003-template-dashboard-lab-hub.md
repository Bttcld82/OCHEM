---
id: PROP-003
title: "Creazione template mancanti dashboard utente e lab hub"
status: approved
priority: P1
effort: M
category: ux
gap_refs:
  - GAP-C03
created_at: 2026-03-16
updated_at: 2026-03-16
decision: approved
decision_notes: "non specificata"
plan_file: "piano generato in conversazione il 2026-03-16"
---

# PROP-003 — Creazione template mancanti dashboard utente e lab hub

## Descrizione
Il blueprint `main` ha due route critiche che fanno `render_template` su file inesistenti:
- `dashboard()` in `routes_main.py` renderizza `main/dashboard.html` — il file non esiste nella
  cartella `app/blueprints/main/templates/` (presente solo `index.html`).
- `lab_hub()` renderizza `main/lab_hub.html` — file anch'esso assente.

Qualsiasi accesso a `/dashboard` o `/l/<lab_code>` genera un `TemplateNotFound` 500.

## Motivazione
La dashboard utente e l'hub laboratorio sono i punti di ingresso principali per i laboratori
partecipanti. Senza questi template nessun utente non-admin può operare. Questo blocca l'intero
flusso operativo del laboratorio (inserimento dati, visualizzazione z-score, grafici).

## Soluzione Proposta
Creare i template mancanti estendendo `base.html`:

**`main/dashboard.html`** — dashboard multi-lab:
- Card per ogni laboratorio dell'utente con ruolo, ultimo upload, cicli attivi
- Link rapidi: "Inserisci risultati", "Visualizza grafici", "Upload CSV"
- Sezione cicli recenti pubblicati

**`main/lab_hub.html`** — hub specifico del laboratorio:
- Header con nome lab, ruolo utente, contatti
- Card sezione QC: n. risultati, cicli attivi, parametri
- Tabella ultimi upload con stato e data
- Link alle sezioni: dati (`/l/<lab_code>/dati/`), stats (`/l/<lab_code>/stats/`), grafici
- Se ruolo `owner_lab`: link gestione utenti del lab

Entrambi i template devono gestire il contesto già passato dalle route (variabili `user_labs`,
`lab_cycles`, `lab_uploads`, `is_owner`, `stats`).

## Acceptance Criteria
- [ ] `GET /dashboard` risponde 200 per qualsiasi utente autenticato con disclaimer accettato
- [ ] `GET /l/<lab_code>` risponde 200 per utenti con ruolo minimo `viewer` sul laboratorio
- [ ] La dashboard mostra tutti i laboratori dell'utente con i rispettivi ruoli
- [ ] L'hub laboratorio mostra gli ultimi 10 upload e i cicli recenti
- [ ] I link verso le sottosezioni (dati, stats, grafici) sono presenti e corretti
- [ ] I template estendono `base.html` e mostrano i messaggi flash

## File da Modificare / Creare
| File | Tipo | Descrizione modifica |
|---|---|---|
| `app/blueprints/main/templates/main/dashboard.html` | crea | template dashboard multi-lab |
| `app/blueprints/main/templates/main/lab_hub.html` | crea | template hub laboratorio |

## Dipendenze
- **Richiede prima:** nessuna
- **Blocca:** nessuna (abilitante per flusso lab completo)

## Rischi
- **Percorso template:** Flask cerca i template in `blueprints/main/templates/`. Il sotto-path
  `main/` è necessario perché la route usa `render_template("main/dashboard.html")`.
  Verificare che la cartella `main/` esista dentro `templates/`.

## Stima Effort
- **Complessità:** M (4-8h) — due template con logica condizionale Bootstrap/Jinja2
- **File coinvolti:** 2 nuovi template
- **Nuova migrazione DB:** no
- **Dipendenze esterne:** nessuna
