---
title: "Statistiche e Grafici"
description: "Come leggere z-score, sz2, rsz e le carte di controllo qualità"
tags: [utente, statistiche, zscore, grafici, qualita]
role: user
order: 4
related:
  - user/03-inserimento-dati
  - user/00-panoramica
---

# Statistiche e Grafici

Dopo che l'amministratore ha elaborato i dati del ciclo, puoi consultare le tue
statistiche di prestazione dalla sezione **Statistiche** del tuo Hub Laboratorio.

## Indicatori Calcolati

### Z-Score (`z`)

Misura quanto il tuo risultato si discosta dal valore atteso del ciclo (`xpt`),
normalizzato per la deviazione standard di proficiency (`sigma_pt`).

```
z = (x - xpt) / sigma_pt
```

| Intervallo | Giudizio |
|-----------|----------|
| \|z\| ≤ 2 | Soddisfacente ✓ |
| 2 < \|z\| ≤ 3 | Questionabile ⚠ |
| \|z\| > 3 | Non soddisfacente ✗ |

### Z-Score Robusto (`sz2`)

Calcolato con la mediana e la MAD (Median Absolute Deviation) invece di media e deviazione standard.
Più robusto rispetto a valori anomali degli altri laboratori.

```
MAD_K = 1.4826
sz2 = (x - mediana) / (MAD_K × MAD)
```

### RSZ (Relative Z-Score)

Indica la posizione relativa del tuo risultato rispetto alla distribuzione di tutti i lab.

## Carta di Controllo

La **carta di controllo** visualizza l'andamento del tuo z-score nel tempo,
ciclo dopo ciclo. Permette di identificare trend sistematici.

### Come Leggere il Grafico

- **Asse X**: cicli PT (in ordine cronologico)
- **Asse Y**: valore z
- **Linee rosse orizzontali**: soglie ±2 (azione) e ±3 (allarme)
- **Punti colorati**: ogni punto è un tuo risultato
  - Verde: |z| ≤ 2
  - Arancione: 2 < |z| ≤ 3
  - Rosso: |z| > 3

### Accedere ai Grafici

Dalla tua Hub Laboratorio → **Statistiche** → seleziona parametro e ciclo.

Puoi anche accedere direttamente da `/l/<codice-lab>/stats`.

## Statistiche Generali del Ciclo

Oltre ai tuoi dati individuali, puoi consultare le statistiche aggregate del ciclo
(media, deviazione standard, numero di partecipanti) nella sezione **Statistiche Generali**.

> I tuoi risultati individuali rimangono anonimi agli altri laboratori.

## Vedi anche

- [[user/03-inserimento-dati|Inserimento Dati]] — come inserire i risultati prima dell'elaborazione
- [[user/00-panoramica|Panoramica]] — cos'è il Proficiency Testing
