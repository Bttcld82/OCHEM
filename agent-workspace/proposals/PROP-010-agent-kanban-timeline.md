---
id: PROP-010
title: "Kanban orizzontale e timeline storico nel blueprint agent"
status: done
priority: P3
effort: S
category: ux
gap_refs: []
origin: user
created_at: 2026-03-16
updated_at: 2026-03-16
decision: "approved"
decision_notes: "già implementata nei template index.html e proposal.html"
plan_file: ""
---

# PROP-010 — Kanban orizzontale e timeline storico nel blueprint agent

## Descrizione

Il blueprint `/agent` mostra le proposte in una tabella piana. Non esiste una vista
immediata per capire la distribuzione per stato, né un riepilogo cronologico
delle decisioni prese su una singola proposta.

Questa proposta aggiunge due enhancement puramente front-end al blueprint esistente,
senza modifiche al DB e senza variazioni al formato dei file `.md`:

1. **Pannello Kanban orizzontale** — sotto la tabella in `index.html`, quattro colonne
   Bootstrap (`proposed`, `approved`, `rejected`, `done`) mostrano i titoli linkati
   delle proposte raggruppati per stato, offrendo una lettura a colpo d'occhio dello
   stato del backlog.

2. **Timeline storico** — in fondo a `proposal.html`, una sezione "Storico" ricostruisce
   gli eventi significativi della proposta leggendo esclusivamente i campi frontmatter
   già presenti:
   - `created_at` + `origin` → "Proposta creata da [origin]"
   - `updated_at` + `decision` + `decision_notes` → "Decisione: [decision] — [note]"
     (visualizzata solo se `decision` non è vuoto)
   - `plan_file` (se valorizzato) → "Piano di implementazione generato"

La fonte dati è esclusivamente il frontmatter YAML già caricato da `_load_all_proposals()`
e da `_load_md()` — nessuna lettura aggiuntiva di file o query DB.

## Motivazione

Il pannello Kanban permette all'admin di valutare lo stato dell'intero backlog PT
in pochi secondi, senza scorrere la tabella. La timeline storico rende leggibile
il ciclo di vita di ogni proposta (quando è stata creata, quando approvata/rifiutata,
se esiste un piano di implementazione) senza navigare tra file Markdown separati.
Non esistono riferimenti normativi pertinenti per questa feature.

## Soluzione Proposta

### Enhancement 1 — Kanban in `index.html`

- Aggiungere sotto la tabella un blocco `<div class="row g-3 mt-2">` con quattro colonne
  `col-md-3` (una per stato: `proposed`, `approved`, `rejected`, `done`).
- Ciascuna colonna ha un header colorato con Bootstrap (`bg-warning`, `bg-success`,
  `bg-danger`, `bg-secondary`) e una lista di card minimali con `id` + `title` della
  proposta, linkati a `url_for('agent.proposal_detail', prop_id=p.id)`.
- Il filtraggio per stato avviene in Jinja2 con `selectattr('status', 'equalto', stato)`.
- Se una colonna è vuota, mostra un testo `<span class="text-muted small">Nessuna</span>`.
- Nessuna modifica a `routes_agent.py`: i dati `proposals` sono già passati al template.

### Enhancement 2 — Timeline in `proposal.html`

- Aggiungere in fondo al corpo del dettaglio (dopo `<div class="help-content">`, prima
  del footer con il pulsante "Torna all'indice") una sezione con titolo `<h5>Storico</h5>`.
- La timeline è una lista verticale con CSS inline (linea verticale via `border-left`
  su Bootstrap, nessuna libreria aggiuntiva).
- Gli eventi sono costruiti in Jinja2 dal dict `meta` già disponibile nel template:
  - Evento 1 (sempre presente): `created_at` — "Proposta creata da [origin]"
    con badge colorato per `origin` (`user` → `bg-info`, `gap-analysis` → `bg-secondary`).
  - Evento 2 (se `decision` non è stringa vuota): `updated_at` —
    "Decisione: [decision]" + eventuale nota `decision_notes`
    (omessa se uguale alla stringa letterale `"non specificata"`).
  - Evento 3 (se `plan_file` non è stringa vuota): `updated_at` —
    "Piano di implementazione generato: [plan_file]".
- Nessuna modifica a `routes_agent.py`: il dict `meta` è già passato al template.

## Acceptance Criteria

- [ ] In `/agent/` il pannello Kanban appare sotto la tabella con quattro colonne distinte,
      ognuna con header colorato e badge di conteggio.
- [ ] Ogni card nel Kanban riporta `id` e `title` della proposta ed è cliccabile verso
      il dettaglio.
- [ ] Le colonne con zero proposte mostrano "Nessuna" e non colonne vuote/rotte.
- [ ] In `/agent/proposals/PROP-009` (approvata) la timeline mostra almeno due eventi:
      "Proposta creata" e "Decisione: approved".
- [ ] In `/agent/proposals/PROP-001` (rifiutata) la timeline mostra "Decisione: rejected".
- [ ] In una proposta con `plan_file` valorizzato, la timeline mostra il terzo evento.
- [ ] In una proposta senza `decision` (es. `proposed`) la timeline mostra solo
      l'evento di creazione.
- [ ] Nessuna modifica al DB, ai file `.md` esistenti, né a `routes_agent.py`.
- [ ] La pagina rimane responsive su viewport mobile (colonne Kanban impilate su `xs`).

## File da Modificare / Creare

| File | Tipo | Descrizione modifica |
|---|---|---|
| `app/blueprints/agent/templates/agent/index.html` | modifica | Aggiungere pannello Kanban orizzontale dopo la tabella proposte |
| `app/blueprints/agent/templates/agent/proposal.html` | modifica | Aggiungere sezione "Storico" con timeline verticale prima del footer |

## Dipendenze

- **Richiede prima:** nessuna
- **Blocca:** nessuna

## Rischi

- **Rischio 1 — campo `status` mancante o non standard nel frontmatter:**
  Qualche file `.md` potrebbe avere `status` assente o con un valore non in
  `{proposed, approved, rejected, done, in_progress}`. Mitigazione: il filtro
  Jinja2 con `selectattr` gestisce silenziosamente l'assenza e la colonna
  `in_progress` può essere aggiunta come quinta colonna opzionale.
- **Rischio 2 — `decision_notes` con valore sentinel "non specificata":**
  Il codice esistente usa questa stringa come placeholder. Mitigazione: la
  timeline la omette esplicitamente con un `{% if meta.decision_notes and
  meta.decision_notes != 'non specificata' %}`.

## Stima Effort

- **Complessità:** S (1-2h)
- **File coinvolti:** 2
- **Nuova migrazione DB:** no
- **Dipendenze esterne:** nessuna
