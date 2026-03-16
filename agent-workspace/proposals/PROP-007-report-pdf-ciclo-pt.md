---
id: PROP-007
title: "Report PDF riepilogativo per ciclo PT con z-score per laboratorio"
status: approved
priority: P2
effort: XL
category: reporting
gap_refs:
  - GAP-C07
created_at: 2026-03-16
updated_at: 2026-03-16
decision: approved
decision_notes: "non specificata"
plan_file: "piano generato in conversazione il 2026-03-16"
---

# PROP-007 — Report PDF riepilogativo per ciclo PT con z-score per laboratorio

## Descrizione
Non esiste alcuna funzionalità di esportazione o report per un ciclo PT completato.
L'admin e i laboratori non possono scaricare un documento riepilogativo con:
- Elenco parametri del ciclo con XPT e SigmaPT
- Risultati di ogni laboratorio con z-score
- Valutazione performance (Eccellente/Accettabile/Fuori controllo per |z|)
- Statistiche aggregate (mean_z, rsz per parametro)

Questo è un requisito fondamentale dei PT: ogni ciclo deve produrre un rapporto finale
distribuito ai partecipanti (ACCREDIA RT-25 §4.4.3; ISO 13528 §7.4).

## Motivazione
Senza report il ciclo PT non può essere considerato "concluso" in modo formale. I laboratori
non hanno documentazione da conservare per accreditamento. L'assenza di questo modulo rende
OCHEM inutilizzabile come strumento PT ufficiale.

## Soluzione Proposta
Implementare un modulo di export basato su `reportlab` o `weasyprint` (da aggiungere a
requirements.txt):

**Struttura report:**
1. Intestazione: nome ciclo, codice, date, provider
2. Per ogni parametro: XPT, SigmaPT, n. partecipanti
3. Tabella risultati: codice lab (anonimizzato o nominale per l'admin), valore misurato, z-score,
   performance class
4. Carta di controllo Plotly esportata come immagine PNG
5. Statistiche finali: mean_z, rsz, % eccellenti

**Route da aggiungere:**
- `GET /admin/cycles/<int:cycle_id>/report.pdf` — report completo con dati nominali (admin only)
- `GET /l/<lab_code>/stats/cycles/<cycle_code>/report.pdf` — report personale del lab (solo i
  propri dati + statistiche aggregate anonimizzate, come da ISO 13528 §7.4.1)

**Tecnica consigliata:** generazione HTML + CSS con `weasyprint` (più flessibile per layout
Bootstrap-like), oppure `reportlab` per PDF strutturato.

## Acceptance Criteria
- [ ] L'admin può scaricare un PDF per ogni ciclo pubblicato o chiuso
- [ ] Il PDF admin include tutti i laboratori con dati nominali
- [ ] Il laboratorio può scaricare un PDF con i soli propri risultati + statistiche aggregate anonimizzate
- [ ] Il PDF include per ogni parametro: XPT, SigmaPT, z-score del lab, performance class
- [ ] Il PDF ha intestazione con nome ciclo, date, provider, data generazione
- [ ] La generazione non blocca il server per > 5 secondi (cicli tipici < 50 lab, < 20 parametri)

## File da Modificare / Creare
| File | Tipo | Descrizione modifica |
|---|---|---|
| `app/blueprints/admin/routes_cycles.py` | modifica | aggiungere route `cycle_report_pdf` |
| `app/blueprints/stats/routes_stats.py` | modifica | aggiungere route `lab_cycle_report_pdf` |
| `app/blueprints/admin/templates/cycle_detail.html` | modifica | aggiungere pulsante download report PDF |
| `app/blueprints/stats/templates/stats/results_table.html` | modifica | aggiungere pulsante download report personale |
| `app/services/report_generator.py` | crea | servizio di generazione report (logica di query + rendering) |
| `requirements.txt` | modifica | aggiungere `weasyprint` o `reportlab` |

## Dipendenze
- **Richiede prima:** PROP-002 (PtStats consistenti come sorgente dati del report)
- **Blocca:** nessuna

## Rischi
- **Dipendenza esterna `weasyprint`:** richiede librerie di sistema (cairo, pango) non sempre
  disponibili. Alternativa: `reportlab` (pura Python, meno dipendenze ma layout più rigido).
  Valutare in base all'ambiente di deploy.
- **Tempi di generazione:** per cicli con molti laboratori la generazione PDF può richiedere
  diversi secondi. Mitigazione: aggiungere un job asincrono (fuori scope di questa proposta).

## Stima Effort
- **Complessità:** XL (>2gg)
- **File coinvolti:** 6
- **Nuova migrazione DB:** no
- **Dipendenze esterne:** `weasyprint` o `reportlab` (da valutare)
