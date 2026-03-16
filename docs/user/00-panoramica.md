---
title: "Panoramica Utente"
description: "Cosa è OCHEM, come funziona un ciclo PT e cosa fa il laboratorio"
tags: [utente, panoramica, pt, zscore]
role: user
order: 0
related:
  - user/01-accesso-registrazione
  - user/02-hub-laboratorio
  - user/03-inserimento-dati
---

# Panoramica Utente

OCHEM è la piattaforma che gestisce i **Proficiency Testing (PT)** — prove interlaboratorio
che permettono ai laboratori di verificare la qualità delle proprie analisi confrontandosi
con altri laboratori.

## Come Funziona un Ciclo PT

```
1. L'admin pubblica un ciclo PT
       ↓
2. Il tuo laboratorio è invitato a partecipare
       ↓
3. Analizzi il campione di riferimento
       ↓
4. Inserisci il risultato su OCHEM
       ↓
5. L'admin elabora i dati aggregati
       ↓
6. OCHEM calcola il tuo z-score
       ↓
7. Consulti le statistiche e i grafici
```

## Il Tuo Ruolo

A seconda del ruolo che ti è stato assegnato nel laboratorio:

| Ruolo | Cosa puoi fare |
|-------|---------------|
| `owner_lab` | Tutto: inserire dati, vedere statistiche, invitare colleghi |
| `analyst` | Inserire e modificare risultati, vedere statistiche |
| `viewer` | Solo consultare risultati e grafici |

## Lo Z-Score: Cosa Significa

Lo z-score misura quanto il tuo risultato si discosta dal valore atteso:

```
z = (x - xpt) / sigma_pt
```

| Valore z | Interpretazione |
|----------|----------------|
| \|z\| ≤ 2 | Soddisfacente |
| 2 < \|z\| ≤ 3 | Questionabile |
| \|z\| > 3 | Non soddisfacente |

## Vedi anche

- [[user/01-accesso-registrazione|Accesso e Registrazione]] — come creare il tuo account
- [[user/02-hub-laboratorio|Hub Laboratorio]] — la tua dashboard principale
- [[user/03-inserimento-dati|Inserimento Dati]] — come inserire i tuoi risultati
