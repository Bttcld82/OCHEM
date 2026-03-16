---
id: PROP-002
title: "Ricalcolo consistente di PtStats (mean_z e rsz) dopo ogni modifica risultato"
status: approved
priority: P1
effort: M
category: statistics
gap_refs:
  - GAP-C02
created_at: 2026-03-16
updated_at: 2026-03-16
decision: approved
decision_notes: "non specificata"
plan_file: "piano generato in conversazione il 2026-03-16"
---

# PROP-002 — Ricalcolo consistente di PtStats (mean_z e rsz) dopo ogni modifica risultato

## Descrizione
La tabella `pt_stats` contiene `mean_z` e `rsz` aggregati per tripletta (ciclo, parametro, laboratorio).
Attualmente il campo `rsz` non viene mai popolato correttamente:
- In `routes_dati.py::_update_pt_stats` viene salvato solo `mean_z` iniziale con `n_results=1` e
  `rsz` non viene scritto (campo None).
- In `routes_dati.py::result_delete` viene decrementato `n_results` ma `mean_z` non viene ricalcolato.
- In `routes_stats.py::_save_results_to_db` `rsz` viene scritto solo al primo inserimento del record,
  ma il valore RSZ calcolato è basato sul dataset CSV corrente, non sull'intero storico del laboratorio.
- Nessuna funzione ricalcola `mean_z` dopo un `result_edit`.

Il modello `ZScore` ha solo `z` e `sz2`; `rsz` vive solo in `PtStats`, ma il suo calcolo non è mai
coerente con ISO 13528 §8 (RSZ deve essere calcolato sull'insieme dei z-score del laboratorio per
parametro e ciclo).

## Motivazione
`PtStats` è la sorgente dati per le statistiche visualizzate nel modulo stats. Dati inconsistenti
rendono le statistiche di performance del laboratorio inaffidabili. ISO 13528 Annex C richiede che
RSZ (Robust Z-score) sia calcolato con la formula MAD-based sull'intero set di z-score di un
laboratorio per un dato parametro e ciclo.

## Soluzione Proposta
Estrarre la logica di aggiornamento `PtStats` in una funzione di servizio dedicata
`recalculate_pt_stats(cycle_code, parameter_code, lab_code)` che:
1. Recupera tutti i `ZScore` attivi per la tripletta.
2. Calcola `mean_z = mean(z_i)`, `n_results = count`, `rsz = MAD_K * median(|z_i - median(z_i)|)`.
3. Crea o aggiorna il record `PtStats`.

Questa funzione deve essere chiamata da:
- `result_insert` (dopo flush)
- `result_edit` (dopo aggiornamento ZScore)
- `result_delete` (dopo eliminazione ZScore)
- `_save_results_to_db` (dopo ogni batch CSV)

## Acceptance Criteria
- [ ] Dopo ogni inserimento, `PtStats.mean_z` e `PtStats.rsz` riflettono i valori corretti calcolati su tutti i z-score del lab per quel ciclo/parametro
- [ ] Dopo eliminazione di un risultato, `PtStats` viene ricalcolato (non solo decrementato `n_results`)
- [ ] Dopo modifica di un risultato, lo z-score aggiornato si riflette in `PtStats`
- [ ] `PtStats.rsz` usa la formula `MAD_K * MAD(z)` con `MAD_K=1.4826` (coerente con `services_stats.py`)
- [ ] Se non esistono z-score, il record `PtStats` viene eliminato o `n_results` impostato a 0

## File da Modificare / Creare
| File | Tipo | Descrizione modifica |
|---|---|---|
| `app/blueprints/dati/routes_dati.py` | modifica | sostituire `_update_pt_stats` con chiamata alla nuova funzione di servizio |
| `app/blueprints/stats/routes_stats.py` | modifica | sostituire logica PtStats in `_save_results_to_db` con chiamata al nuovo servizio |
| `app/blueprints/stats/services_stats.py` | modifica | aggiungere funzione `recalculate_pt_stats(cycle_code, parameter_code, lab_code)` esportata |

## Dipendenze
- **Richiede prima:** nessuna (indipendente)
- **Blocca:** PROP-007 (report PDF usa PtStats come sorgente dati)

## Rischi
- **Performance con molti risultati:** il ricalcolo full-scan ad ogni insert potrebbe essere lento.
  Mitigazione: la query è limitata alla tripletta ciclo/parametro/lab; con volumi PT normali (< 500 risultati per tripletta) è accettabile senza ottimizzazioni.

## Stima Effort
- **Complessità:** M (4-8h)
- **File coinvolti:** 3
- **Nuova migrazione DB:** no (i campi esistono già)
- **Dipendenze esterne:** nessuna
