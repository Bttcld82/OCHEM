---
id: PROP-001
title: "Selezione esplicita del ciclo nell'upload CSV risultati"
status: rejected
priority: P1
effort: M
category: workflow
gap_refs:
  - GAP-C01
created_at: 2026-03-16
updated_at: 2026-03-16
decision: rejected
decision_notes: "Upload CSV non previsto al momento, i dati verranno inseriti manualmente"
plan_file: ""
---

# PROP-001 — Selezione esplicita del ciclo nell'upload CSV risultati

## Descrizione
Attualmente in `routes_stats.py::upload_results` il ciclo PT viene selezionato automaticamente come
l'ultimo ciclo pubblicato (`Cycle.query.filter_by(status='published').order_by(Cycle.created_at.desc()).first()`).
Se un laboratorio partecipa a più cicli attivi, tutti i risultati vengono associati al ciclo sbagliato
senza alcun avviso.

Lo stesso problema si ripropone in `services_stats.py::_add_reference_values` dove i valori XPT/SigmaPT
