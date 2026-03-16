---
id: PROP-006
title: "Correzione bug cycle_code nullable in UploadFile durante upload CSV"
status: rejected
priority: P1
effort: S
category: workflow
gap_refs:
  - GAP-C06
created_at: 2026-03-16
updated_at: 2026-03-16
decision: rejected
decision_notes: "Upload CSV non previsto al momento, i dati verranno inseriti manualmente"
plan_file: ""
---

# PROP-006 — Correzione bug cycle_code nullable in UploadFile durante upload CSV

## Descrizione
In `routes_stats.py::upload_results`, il campo `cycle_code` dell'`UploadFile` viene assegnato
solo se esiste un ciclo pubblicato:

```python
current_cycle = Cycle.query.filter_by(status='published')...first()
if current_cycle:
