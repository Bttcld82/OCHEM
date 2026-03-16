---
title: "Gestione Cicli PT"
description: "Come creare, configurare e pubblicare un ciclo di Proficiency Testing"
tags: [admin, cicli, workflow, pubblicazione]
role: admin
order: 1
related:
  - admin/03-parametri-unita
  - admin/05-documenti
  - admin/00-panoramica
---

# Gestione Cicli PT

Il **ciclo PT** è l'unità centrale di OCHEM: rappresenta una sessione di prove interlaboratorio
su uno o più analiti, in un periodo definito.

## Creare un Nuovo Ciclo

Vai su **Admin → Cicli → Nuovo Ciclo** (`/admin/cycles/new`).

Campi obbligatori:

| Campo | Descrizione |
|-------|-------------|
| Codice | Identificativo univoco (es. `PT-2024-01`) |
| Nome | Descrizione estesa |
| Provider | Ente organizzatore |
| Data inizio / fine | Periodo di raccolta risultati |

Il ciclo viene creato in stato **draft**: non è ancora visibile ai laboratori.

## Configurare i Parametri del Ciclo

Dopo la creazione, entra nel dettaglio del ciclo e aggiungi i **parametri analitici**
da monitorare (es. Cadmio, Piombo, pH...).

Per ogni parametro imposta:

| Campo | Significato |
|-------|-------------|
| `xpt` | Valore assegnato (riferimento atteso) |
| `sigma_pt` | Deviazione standard di proficiency |

> **Attenzione:** `xpt` e `sigma_pt` sono necessari per il calcolo dello z-score.
> Senza di essi il sistema non può produrre statistiche.

Lo z-score si calcola come:

```
z = (x - xpt) / sigma_pt
```

## Pubblicare il Ciclo

Quando la configurazione è completa, clicca **Pubblica** nel dettaglio del ciclo.

- Lo stato passa da `draft` a `published`
- I laboratori con una partecipazione attiva vedono il ciclo nella loro dashboard
- I laboratori possono iniziare a inserire i risultati

## Revisione e Chiusura

Dopo la raccolta dati, l'admin può:

1. **Upload CSV risultati** — carica il file con i risultati aggregati di tutti i lab (`/stats/upload`)
2. Il sistema calcola automaticamente: z-score, sz2 (z robusto), rsz, statistiche generali
3. Revisiona i risultati dalla sezione Statistiche
4. Chiudi il ciclo (opzionale, per bloccare ulteriori inserimenti)

## Stati del Ciclo

```
draft → published → (closed)
```

| Stato | Visibile ai lab | Inserimento dati |
|-------|-----------------|------------------|
| draft | No | No |
| published | Sì | Sì |
| closed | Sì | No |

## Vedi anche

- [[admin/03-parametri-unita|Parametri e Unità]] — configurare l'anagrafica degli analiti
- [[admin/05-documenti|Documenti]] — allegare circolari PDF al ciclo
