---
title: "Utenti e Ruoli"
description: "Approvare registrazioni, inviare inviti e gestire i ruoli degli utenti"
tags: [admin, utenti, ruoli, registrazioni, inviti]
role: admin
order: 4
related:
  - admin/02-laboratori
  - admin/00-panoramica
---

# Utenti e Ruoli

OCHEM usa un sistema di ruoli a due livelli:
- **Ruolo globale** — `admin`: accesso completo al pannello admin
- **Ruoli per laboratorio** — `owner_lab`, `analyst`, `viewer`: accesso specifico a un lab

## Approvare una Richiesta di Registrazione

Quando un nuovo utente si registra, la sua richiesta resta in attesa di approvazione.

1. Vai su **Admin → Registrazioni** (`/admin/registrations`)
2. Vedi la lista delle richieste pendenti con: nome, email, laboratorio richiesto
3. Clicca **Approva** per creare l'account utente
4. Clicca **Rifiuta** per scartare la richiesta (con messaggio opzionale)

Dopo l'approvazione, l'utente riceve un'email e può accedere al sistema.

## Invitare Direttamente un Utente

Per creare un account senza passare dalla richiesta pubblica:

1. Vai su **Admin → Utenti → Invia Invito**
2. Inserisci l'email del destinatario
3. Il sistema genera un **token di invito** (link unico)
4. L'utente clicca il link e completa la registrazione

> Gli inviti hanno una scadenza. Se il link scade, genera un nuovo invito.

## Assegnare Ruoli di Laboratorio

Ogni utente può avere ruoli diversi in laboratori diversi.

1. Vai su **Admin → Utenti** e clicca sull'utente
2. Nella sezione **Ruoli Lab**, clicca **Aggiungi ruolo**
3. Seleziona laboratorio e ruolo

| Ruolo | Cosa può fare |
|-------|--------------|
| `owner_lab` | Tutto: invita collaboratori, vede e modifica dati |
| `analyst` | Inserisce e modifica risultati |
| `viewer` | Solo lettura |

## Promuovere un Utente ad Admin

Dalla scheda utente, attiva la spunta **Admin globale**.

> Attenzione: gli admin hanno accesso completo a tutti i dati e configurazioni.

## Revocare un Ruolo

Dalla scheda dell'utente, nella sezione **Ruoli Lab**, clicca **Rimuovi** sul ruolo da togliere.

Per revocare l'accesso completo a un lab, rimuovi tutti i ruoli di quell'utente su quel laboratorio.

## Vedi anche

- [[admin/02-laboratori|Gestione Laboratori]] — creare lab e assegnare il primo owner
