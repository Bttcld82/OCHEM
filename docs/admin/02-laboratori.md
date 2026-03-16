---
title: "Gestione Laboratori"
description: "Come registrare laboratori, assegnare owner e gestire le partecipazioni ai cicli"
tags: [admin, laboratori, ruoli]
role: admin
order: 2
related:
  - admin/04-utenti-ruoli
  - admin/01-cicli
---

# Gestione Laboratori

I **laboratori** sono i soggetti partecipanti ai cicli PT. Ogni lab ha un codice univoco
e almeno un utente con ruolo `owner_lab`.

## Creare un Laboratorio

Vai su **Admin → Laboratori → Nuovo** (`/admin/labs/new`).

| Campo | Note |
|-------|------|
| Codice | Identificativo breve, univoco (es. `LAB001`) |
| Nome | Denominazione completa |
| Email di contatto | Facoltativa |
| Attivo | Spunta per abilitare il lab |

## Assegnare un Owner al Laboratorio

Dopo aver creato il lab, assegna almeno un utente come `owner_lab`:

1. Vai su **Admin → Utenti** e individua l'utente
2. Clicca **Gestisci Ruoli Lab** sull'utente
3. Seleziona il laboratorio e assegna il ruolo `owner_lab`

In alternativa, l'owner può essere assegnato dalla scheda dettaglio del laboratorio.

## Gerarchia dei Ruoli per Laboratorio

| Ruolo | Permessi |
|-------|----------|
| `owner_lab` | Gestione completa del lab, invita altri utenti |
| `analyst` | Inserisce e modifica dati |
| `viewer` | Solo lettura di risultati e statistiche |

> Un utente può avere ruoli diversi in laboratori diversi.

## Partecipazioni ai Cicli

Un lab partecipa a un ciclo quando viene creata una **LabParticipation**.
Puoi gestirle dalla scheda dettaglio del ciclo: aggiungi i laboratori che partecipano
alla sessione corrente.

## Disattivare un Laboratorio

Dalla scheda del lab, togli la spunta **Attivo**. Il lab non potrà inserire nuovi dati
ma i dati storici restano accessibili.

## Vedi anche

- [[admin/04-utenti-ruoli|Utenti e Ruoli]] — come assegnare e modificare i ruoli
- [[admin/01-cicli|Gestione Cicli]] — collegare i lab a un ciclo tramite partecipazioni
