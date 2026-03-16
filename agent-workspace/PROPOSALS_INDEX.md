# PROPOSALS INDEX — OCHEM
_Aggiornato automaticamente da idea-proposer e proposal-coordinator_
_Ultima modifica: 2026-03-16_

## Contatori
- Totale proposte: 8
- Proposed: 0 | Approved: 6 | Rejected: 2 | In Progress: 0 | Done: 0

## P1 — Critici
_Senza queste funzionalità un ciclo PT non può concludersi_

| ID | Titolo | Stato | Effort | Categoria | Gap Refs | Data |
|---|---|---|---|---|---|---|
| PROP-001 | Selezione esplicita del ciclo nell'upload CSV risultati | rejected | M | workflow | GAP-C01 | 2026-03-16 |
| PROP-002 | Ricalcolo consistente di PtStats (mean_z e rsz) dopo ogni modifica risultato | approved | M | statistics | GAP-C02 | 2026-03-16 |
| PROP-003 | Creazione template mancanti dashboard utente e lab hub | approved | M | ux | GAP-C03 | 2026-03-16 |
| PROP-004 | Flusso completo di approvazione richiesta registrazione con creazione utente | approved | L | admin | GAP-C04 | 2026-03-16 |
| PROP-006 | Correzione bug cycle_code nullable in UploadFile durante upload CSV | rejected | S | workflow | GAP-C06 | 2026-03-16 |

## P2 — Importanti
_Funzionalità presente ma incompleta, degrada correttezza o esperienza_

| ID | Titolo | Stato | Effort | Categoria | Gap Refs | Data |
|---|---|---|---|---|---|---|
| PROP-005 | Reset password admin: rimozione esposizione password in chiaro nel flash | approved | S | admin | GAP-C05 | 2026-03-16 |
| PROP-007 | Report PDF riepilogativo per ciclo PT con z-score per laboratorio | approved | XL | reporting | GAP-C07 | 2026-03-16 |
| PROP-008 | Calcolo RSZ cross-laboratorio conforme ISO 13528 Annex C | approved | L | statistics | GAP-C08 | 2026-03-16 |

## P3 — Migliorativi
_Migliorano usabilità/automazione ma non bloccano il PT_

| ID | Titolo | Stato | Effort | Categoria | Gap Refs | Data |
|---|---|---|---|---|---|---|
| _(nessuna)_ | | | | | | |

---

## Note sulle dipendenze
```
PROP-006 → superata da PROP-001 (entrambe rifiutate: upload CSV fuori scope MVP)
PROP-001 → bloccava PROP-007 (rifiutata: upload CSV fuori scope MVP)
PROP-002 → blocca PROP-007 (PtStats deve essere consistente) e PROP-008
PROP-008 → dipende da PROP-002
```

## Gap identificati dall'analisi codebase (2026-03-16)
| Gap ID | Descrizione | Proposta | Stato |
|---|---|---|---|
| GAP-C01 | Upload CSV usa sempre l'ultimo ciclo pubblicato invece del ciclo scelto dall'utente | PROP-001 | rejected |
| GAP-C02 | PtStats.rsz mai calcolato; mean_z non ricalcolato su edit/delete risultato | PROP-002 | approved |
| GAP-C03 | Template `main/dashboard.html` e `main/lab_hub.html` non esistono → HTTP 500 | PROP-003 | approved |
| GAP-C04 | Approvazione RegistrationRequest non crea l'utente né assegna il laboratorio | PROP-004 | approved |
| GAP-C05 | Reset password admin non mostra la password generata → flusso inutilizzabile | PROP-005 | approved |
| GAP-C06 | UploadFile.cycle_code NOT NULL ma può restare None → IntegrityError silenzioso | PROP-006 | rejected |
| GAP-C07 | Nessun export/report PDF per ciclo PT (richiesto da ISO 13528 §7.4 e ACCREDIA RT-25) | PROP-007 | approved |
| GAP-C08 | RSZ calcolato per singolo CSV, non cross-laboratorio come da ISO 13528 Annex C | PROP-008 | approved |
