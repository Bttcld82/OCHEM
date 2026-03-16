---
id: PROP-005
title: "Reset password admin: rimozione esposizione password in chiaro nel flash"
status: done
priority: P2
effort: S
category: admin
gap_refs:
  - GAP-C05
created_at: 2026-03-16
updated_at: 2026-03-16
decision: approved
decision_notes: "non specificata"
plan_file: "piano generato in conversazione il 2026-03-16"
---

# PROP-005 — Reset password admin: rimozione esposizione password in chiaro nel flash

## Descrizione
In `routes_users.py::user_reset_password`, la password temporanea generata con `secrets.choice`
viene loggata implicitamente nel flash ma non viene mai mostrata all'admin per la comunicazione
all'utente. Il messaggio flash dice solo "Comunicare la nuova password temporanea all'utente via
canale sicuro" senza mostrare quale sia la password.

Due problemi distinti:
1. La password è generata ma **non viene mai mostrata** — l'admin non sa quale password comunicare.
2. La password viene impostata senza che l'utente sia obbligato a cambiarla al primo accesso
   (non c'è flag `password_must_change` nel modello `User`).

Il flash attuale è fuorviante: suggerisce di comunicare la password ma non la fornisce.

## Motivazione
Il flusso di reset password è inutilizzabile nello stato attuale: l'admin resetta la password
ma non la conosce, quindi non può comunicarla all'utente. L'utente rimane bloccato.

## Soluzione Proposta
**Opzione A (minima, senza modifiche al modello):** Mostrare la password temporanea direttamente
nel messaggio flash, rendendolo esplicito e contestuale alla pagina di dettaglio utente.
Aggiungere un avviso visivo (alert Bootstrap `warning`) che sparisce al ricaricamento.

**Opzione B (consigliata):** Aggiungere campo `password_must_change` (Boolean, default False) al
modello `User` + migrazione. Impostarlo a `True` al reset. Il decorator `disclaimer_required`
(o uno nuovo `password_change_required`) intercetta il flag e redirige a una route
`/auth/change-password` prima di procedere.

La proposta copre l'Opzione A (immediata, senza migrazione) con un commento per la futura
implementazione dell'Opzione B.

## Acceptance Criteria
- [ ] Dopo il reset, il messaggio flash mostra chiaramente la password temporanea generata
- [ ] La pagina di dettaglio utente presenta la password in un elemento copiabile (input readonly o `<code>`)
- [ ] Il log applicativo (`current_app.logger`) **non** registra la password in chiaro
- [ ] Il messaggio flash indica esplicitamente che la password è temporanea e deve essere cambiata

## File da Modificare / Creare
| File | Tipo | Descrizione modifica |
|---|---|---|
| `app/blueprints/admin/routes_users.py` | modifica | modificare `user_reset_password` per includere la password nel flash e nella response JSON; rimuovere log della password |
| `app/blueprints/admin/templates/user_detail.html` | modifica | aggiungere sezione per visualizzare la password temporanea in modo sicuro (input readonly) |

## Dipendenze
- **Richiede prima:** nessuna
- **Blocca:** nessuna

## Rischi
- **Sicurezza minima:** mostrare la password nel flash è accettabile solo come soluzione
  temporanea in assenza di sistema email. Documentare come debt tecnico.

## Stima Effort
- **Complessità:** S (1-2h)
- **File coinvolti:** 2
- **Nuova migrazione DB:** no (Opzione A)
- **Dipendenze esterne:** nessuna
