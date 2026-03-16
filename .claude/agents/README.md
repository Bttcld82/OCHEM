---
name: agents-readme
description: Documentazione dell'architettura multi-agente per testing OCHEM
type: reference
---

# Agenti OCHEM — Guida all'Uso

## Architettura Completa

```
LAYER PIANIFICAZIONE (evolutivo)
────────────────────────────────────────
feature-analyst   →  agent-workspace/feature-inventory.md
    │
    ▼
idea-proposer     →  agent-workspace/proposals/PROP-*.md  (origin: gap-analysis)
                     agent-workspace/PROPOSALS_INDEX.md

user-proposer     →  agent-workspace/proposals/PROP-*.md  (origin: user)
    │  (idea verbale utente → proposta strutturata)
    │
    ▼
proposal-coordinator  →  agent-workspace/decisions.md
    │  (se approvata + confermata)
    ▼
plan-writer  ◄──────────── condiviso con layer testing

LAYER TESTING (qualità)
────────────────────────────────────────
orchestrator
├── code-reviewer   (analisi statica, sicurezza, coerenza)
├── e2e-tester      (test browser con Playwright)
├── route-tester    (test HTTP rapidi via test client Flask)
└── plan-writer     (piani di implementazione e fix)
```

## Flusso Raccomandato

### Prima sessione (analisi iniziale)
1. `Usa feature-analyst` → produce inventario gap (10-15 min)
2. `Usa idea-proposer per i gap critici` → genera PROP-001..N (5-10 min)
3. `Usa proposal-coordinator` → revisione interattiva proposte

### Sessioni successive (dopo sviluppo)
1. `Usa feature-analyst` → verifica cache, rigenera solo se ci sono nuovi commit su app/
2. `Usa idea-proposer per i nuovi gap` → solo proposte mancanti
3. `Usa proposal-coordinator` → mostra solo le "proposed"

### Solo revisione proposte esistenti
```
Usa il proposal-coordinator per vedere le proposte in attesa
```
Non serve rianalizzare nulla — le proposte sono già in `agent-workspace/proposals/`.

## Come usarli — Layer Testing

### Sessione completa (raccomandato)
```
Usa l'agente orchestrator per avviare una sessione completa di analisi
```
L'orchestrator coordina automaticamente gli altri agenti nell'ordine corretto.

### Agenti singoli (uso diretto)

| Agente | Quando usarlo | Prerequisiti |
|--------|---------------|--------------|
| `feature-analyst` | Analizzare gap funzionali rispetto a ISO 13528 | Nessuno |
| `idea-proposer` | Generare proposte strutturate dai gap | feature-inventory.md presente |
| `user-proposer` | Trasformare idea verbale in proposta strutturata | Nessuno |
| `proposal-coordinator` | Revisionare/approvare proposte, avviare piani | proposals/ presenti |
| `code-reviewer` | Analisi statica veloce, prima di un commit | Nessuno |
| `e2e-tester` | Test UI completi | Server Flask attivo su :5000 |
| `route-tester` | Verifica rapida status code | Python + venv attivo |
| `plan-writer` | Dopo aver trovato bug o pianificando feature | Lista bug/feature in input |
| `file-cleaner` | Pulizia file Python orfani (script one-off, debug, seed temporanei) | Nessuno |

## Skill (Slash Commands)

Le skill sono shortcut per l'utente che possono concatenare più agenti:

| Skill | Cosa fa | Agenti coinvolti |
|-------|---------|-----------------|
| `/cleanup` | Analizza e archivia file Python orfani | `file-cleaner` |
| `/review` | Code review + test route sui file git-modified | `code-reviewer` + `route-tester` |

## Hook Automatici

Configurati in `.claude/settings.local.json`:

| Evento | Trigger | Comportamento |
|--------|---------|---------------|
| `PreToolUse` su Edit/Write | File è `models.py` | Avvisa di creare migrazione Alembic |
| `PostToolUse` su Bash | Comando contiene `alembic upgrade head` | Conferma migrazione applicata |

### Esempi di invocazione

**Analisi gap:**
```
Usa il feature-analyst per aggiornare l'inventario
```

**Nuove proposte:**
```
Usa idea-proposer per generare proposte per tutti i gap critici
```

**Revisione proposte:**
```
Usa il proposal-coordinator — mostrami le proposte P1 in attesa
```

**Solo code review:**
```
Usa il code-reviewer per analizzare i file routes_cycles.py e routes_dati.py
```

**Solo E2E (server già avviato):**
```
Usa l'e2e-tester per verificare il flusso di login e la dashboard admin
```

**Pianificazione fix:**
```
Usa il plan-writer per pianificare i fix di questi 3 bug: [...]
```

## Configurazione Server per E2E

```bash
cd C:/Users/betti/LOCALE_Office/OCHEM
source venv/Scripts/activate
flask run
# oppure
python manage.py
```

**URL:** `http://127.0.0.1:5000`
**Admin:** `admin@ochem.local` / `admin123`

## Note
- `feature-analyst`, `idea-proposer`, `code-reviewer`, `route-tester` → sola lettura
- Solo `proposal-coordinator` può scrivere in `agent-workspace/`
- Solo `plan-writer` e l'utente possono avviare modifiche al codice
- I report del layer testing vengono prodotti come testo nella conversazione
- Le proposte del layer pianificazione sono persistenti in `agent-workspace/` (gittracked)
