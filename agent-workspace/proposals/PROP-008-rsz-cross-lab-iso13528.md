---
id: PROP-008
title: "Calcolo RSZ cross-laboratorio conforme ISO 13528 Annex C"
status: approved
priority: P2
effort: L
category: statistics
gap_refs:
  - GAP-C08
created_at: 2026-03-16
updated_at: 2026-03-16
decision: approved
decision_notes: "non specificata"
plan_file: "piano generato in conversazione il 2026-03-16"
---

# PROP-008 — Calcolo RSZ cross-laboratorio conforme ISO 13528 Annex C

## Descrizione
Il campo `PtStats.rsz` è documentato come "Robust Z-score" ma il suo significato è ambiguo
e la sua implementazione attuale è scorretta rispetto a ISO 13528.

In `services_stats.py::_calculate_statistics`, la funzione `calculate_rsz_group` calcola RSZ
come `MAD_K * MAD(z_i)` **per gruppo di parametro all'interno del singolo file CSV caricato**.
Questo non corrisponde a nessuno dei calcoli definiti in ISO 13528:

- ISO 13528 §6.2: `z = (x - X_pt) / sigma_pt` — z-score standard (già implementato correttamente)
- ISO 13528 Annex C: `z_r` (robust z) si calcola con l'algoritmo A (QIAP) sull'insieme dei
  risultati di **tutti i laboratori** per un dato parametro e ciclo, non su quelli di un singolo lab

Il campo `rsz` in `PtStats` sembra voler rappresentare una statistica robusta per il laboratorio,
ma la formula applicata non ha significato statistico definito.

## Motivazione
Un sistema PT conforme ISO 13528 deve poter calcolare statistiche robuste multi-laboratorio.
Il confronto tra laboratori richiede che i parametri di riferimento (media, deviazione standard)
siano calcolati su tutti i partecipanti. Attualmente OCHEM non ha nessuna funzione che aggreghi
i risultati cross-laboratorio per un ciclo.

## Soluzione Proposta
Aggiungere in `services_stats.py` una funzione `calculate_cycle_consensus_stats(cycle_code, parameter_code)` che:

1. Recupera tutti i `Result.measured_value` di tutti i laboratori per il ciclo e parametro.
2. Calcola la media robusta e la deviazione standard robusta con l'algoritmo A (QIAP) di ISO 13528 Annex C:
   - `x_pt_robust = median(x_i)` (stima iniziale)
   - Iterazione: `x* = median(x_i)`, `s* = 1.4826 * median(|x_i - x*|)`
   - Windsorizzazione al 1.5*s*
3. Salva i risultati in una nuova struttura dati (può estendere `CycleParameter` con campi
   `xpt_robust` e `sigma_pt_robust` opzionali, oppure creare una nuova tabella `CycleStat`).
4. Ricalcola il `z_robust = (x - xpt_robust) / sigma_pt_robust` per ogni laboratorio.

Il campo `PtStats.rsz` viene ridefinito come `z_robust` calcolato con i parametri consenso.

Questa funzione deve essere richiamabile manualmente dall'admin dopo la chiusura di un ciclo.

## Acceptance Criteria
- [ ] Esiste una funzione `calculate_cycle_consensus_stats` che calcola media e sigma robusti su tutti i laboratori partecipanti
- [ ] L'algoritmo implementa almeno l'approccio mediano (stima robusta di primo livello) come descritto in ISO 13528 Annex C §C.2
- [ ] I parametri robusti sono separati da XPT/SigmaPT assegnati (non sovrascrivono i valori del provider)
- [ ] L'admin può triggerare il ricalcolo dal pannello ciclo
- [ ] `PtStats.rsz` viene aggiornato con il z-score robusto calcolato con i parametri consenso

## File da Modificare / Creare
| File | Tipo | Descrizione modifica |
|---|---|---|
| `app/blueprints/stats/services_stats.py` | modifica | aggiungere `calculate_cycle_consensus_stats(cycle_code, parameter_code)` |
| `app/blueprints/admin/routes_cycles.py` | modifica | aggiungere route `cycle_recalculate_stats` (POST) per triggering manuale |
| `app/blueprints/admin/templates/cycle_detail.html` | modifica | aggiungere pulsante "Ricalcola statistiche consenso" |
| `migrations/` | modifica | nuova migrazione se si aggiungono colonne a `cycle_parameter` |

## Dipendenze
- **Richiede prima:** PROP-002 (PtStats deve essere popolato correttamente prima di aggiungere statistiche robuste cross-lab)
- **Blocca:** PROP-007 (il report PDF può includere statistiche consenso solo dopo questa proposta)

## Rischi
- **Requisito minimo partecipanti:** l'algoritmo A di ISO 13528 richiede almeno 8 laboratori
  per avere significatività statistica. Mitigazione: mostrare avviso se n < 8 (ISO 13528 §6.4.2).
- **Complessità iterativa dell'algoritmo A:** la convergenza deve essere verificata. Aggiungere
  un limite di iterazioni (es. max 50) per prevenire loop infiniti.

## Stima Effort
- **Complessità:** L (1-2gg)
- **File coinvolti:** 4
- **Nuova migrazione DB:** possibile (campi opzionali su `cycle_parameter`)
- **Dipendenze esterne:** nessuna (numpy già disponibile)
