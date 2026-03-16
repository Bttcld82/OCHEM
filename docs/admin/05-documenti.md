---
title: "Documenti e Circolari"
description: "Caricare PDF e associarli ai cicli PT come documenti ufficiali"
tags: [admin, documenti, pdf, circolari]
role: admin
order: 5
related:
  - admin/01-cicli
---

# Documenti e Circolari

OCHEM permette di allegare **documenti PDF** ai cicli PT: circolari, istruzioni operative,
rapporti, moduli di partecipazione.

I documenti caricati sono visibili ai laboratori dalla loro dashboard nel ciclo corrispondente.

## Caricare un Documento

Vai su **Admin → Documenti → Carica** (`/admin/docs/upload`).

| Campo | Note |
|-------|------|
| File | PDF (dimensione massima configurabile) |
| Titolo | Nome descrittivo del documento |
| Ciclo | Ciclo PT a cui associare il documento (facoltativo) |
| Tipo | Es. Circolare, Istruzioni, Rapporto |

## Associare Documenti a un Ciclo

Puoi associare un documento a un ciclo in due modi:

1. **Durante l'upload** — seleziona il ciclo nel campo apposito
2. **Dalla scheda ciclo** — nella sezione Documenti, clicca **Collega documento esistente**

Un documento può essere associato a più cicli.

## Visualizzazione da Parte dei Laboratori

I laboratori vedono i documenti associati al ciclo nella loro **Hub Lab**,
nella card del ciclo attivo. Possono scaricare il PDF direttamente.

## Eliminare un Documento

Dalla lista documenti (`/admin/docs`), clicca **Elimina** sul documento.

> L'eliminazione rimuove anche tutte le associazioni con i cicli.
> Il file fisico viene cancellato dal server.

## Vedi anche

- [[admin/01-cicli|Gestione Cicli]] — gestione completa del ciclo PT
