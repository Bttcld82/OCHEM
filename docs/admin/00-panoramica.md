---
title: "Panoramica Amministratore"
description: "Visione d'insieme del pannello admin e del flusso operativo"
tags: [admin, panoramica, workflow]
role: admin
order: 0
related:
  - admin/01-cicli
  - admin/02-laboratori
  - admin/04-utenti-ruoli
---

# Panoramica Amministratore

Il pannello admin (`/admin`) è accessibile solo agli utenti con ruolo **admin globale**.
Da qui si governa l'intera piattaforma: anagrafica, cicli PT, laboratori e utenti.

## Flusso Operativo Tipico

Il ciclo di vita di una sessione di Proficiency Testing segue questi passi:

```
1. Configurazione anagrafica
       ↓
2. Creazione laboratori e assegnazione owner
       ↓
3. Creazione ciclo PT (stato: draft)
       ↓
4. Configurazione parametri del ciclo (xpt, sigma_pt)
       ↓
5. Pubblicazione ciclo → i lab possono inserire dati
       ↓
6. Raccolta risultati dai laboratori
       ↓
7. Upload CSV risultati aggregati → calcolo z-score
       ↓
8. Revisione e chiusura ciclo
```

## Sezioni del Pannello Admin

| Sezione | Percorso | Scopo |
|---------|----------|-------|
| Dashboard | `/admin` | Contatori globali e alert |
| Cicli | `/admin/cycles` | Crea e gestisci i cicli PT |
| Laboratori | `/admin/labs` | Gestisci i lab partecipanti |
| Parametri | `/admin/parameters` | Analiti monitorati |
| Unità | `/admin/units` | Unità di misura |
| Tecniche | `/admin/techniques` | Metodi analitici |
| Provider | `/admin/providers` | Enti organizzatori |
| Utenti | `/admin/users` | Elenco utenti e ruoli |
| Registrazioni | `/admin/registrations` | Richieste di accesso in attesa |
| Documenti | `/admin/docs` | Upload PDF circolari |

## Vedi anche

- [[admin/01-cicli|Gestione Cicli]] — guida completa alla creazione e pubblicazione di un ciclo
- [[admin/02-laboratori|Gestione Laboratori]] — registrare lab e assegnare gli owner
- [[admin/04-utenti-ruoli|Utenti e Ruoli]] — approvare registrazioni e assegnare ruoli
