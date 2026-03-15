# Approvazione registrazioni

Gli amministratori gestiscono le richieste di registrazione degli utenti.

## Lista richieste

**URL:** `/admin/registrations`

La tabella mostra le richieste con:
- Email del richiedente
- Nome completo
- Laboratorio desiderato (nuovo o esistente)
- Ruolo richiesto
- Stato della richiesta
- Data di invio

## Filtrare per stato

Puoi filtrare le richieste per:
- **Submitted**: appena inviate, da prendere in carico
- **Under review**: in fase di valutazione
- **Approved**: approvate
- **Rejected**: rifiutate

## Processo di approvazione

**URL:** `/admin/registrations/<id>`

1. Apri il **dettaglio** della richiesta
2. Valuta le informazioni fornite
3. Scegli un'azione:

### Approvare
- Se il richiedente vuole un **nuovo laboratorio**: viene creato automaticamente
- L'utente viene creato e assegnato al laboratorio con il ruolo richiesto
- Viene generato un link di attivazione per impostare la password

### Rifiutare
- La richiesta viene marcata come rifiutata
- Puoi aggiungere una **nota admin** con la motivazione

> [!info] Audit
> Ogni decisione registra chi ha approvato/rifiutato (`decided_by`) e quando (`decided_at`).

## Vedi anche
- [[02-Accesso/Registrazione|Registrazione (lato utente)]]
- [[Inviti utenti]]
- [[Gestione utenti]]
