---
id: PROP-004
title: "Flusso completo di approvazione richiesta registrazione con creazione utente"
status: approved
priority: P1
effort: L
category: admin
gap_refs:
  - GAP-C04
created_at: 2026-03-16
updated_at: 2026-03-16
decision: approved
decision_notes: "non specificata"
plan_file: "piano generato in conversazione il 2026-03-16"
---

# PROP-004 — Flusso completo di approvazione richiesta registrazione con creazione utente

## Descrizione
Il modello `RegistrationRequest` ha i metodi `approve()` e `reject()` e la route
`/admin/registrations` (templates `registrations_list.html` e `registration_detail.html` esistono),
ma analizzando `routes_users.py` e `routes_main.py` admin non esiste nessuna route che:
1. Mostri la lista delle `RegistrationRequest` in stato `submitted`
2. Permetta all'admin di approvare una richiesta **creando effettivamente l'utente** nel DB
3. Assegni al nuovo utente il laboratorio e il ruolo desiderato (`target_lab_code` / `desired_role`)
4. Comunichi l'esito al richiedente

Il metodo `RegistrationRequest.approve()` aggiorna solo i campi status/decided_by/decided_at
della richiesta, ma non crea l'`User` corrispondente. L'utente rimane bloccato in uno stato
approvato ma senza account funzionante.

## Motivazione
Senza questo flusso nessun nuovo laboratorio può accedere alla piattaforma tramite autoregistrazione.
Il meccanismo degli inviti (`InviteToken`) è alternativo ma richiede che l'admin conosca a priori
l'email dell'utente. L'autoregistrazione è il percorso principale per i nuovi laboratori.

## Soluzione Proposta
Aggiungere le route mancanti nel blueprint admin:

1. **`GET /admin/registrations`** — lista richieste raggruppate per stato con badge contatori
2. **`GET /admin/registrations/<int:id>`** — dettaglio singola richiesta
3. **`POST /admin/registrations/<int:id>/approve`** — flusso approvazione:
   - Chiama `request.approve(admin_email, admin_note)`
   - Crea `User` se non esiste già (email come identificatore)
   - Genera password temporanea con `secrets.token_urlsafe(12)`
   - Se `target_lab_code` valorizzato: crea `UserLabRole` con il ruolo desiderato
   - Se `desired_lab_name` valorizzato e nessun lab esistente: crea nuovo `Lab`
   - Registra in `JobLog` l'operazione
   - Flash con password temporanea (da comunicare all'utente fuori banda)
4. **`POST /admin/registrations/<int:id>/reject`** — rifiuto con nota admin

## Acceptance Criteria
- [ ] La dashboard admin mostra il contatore `pending_registrations` (già presente, già calcolato)
- [ ] La lista registrazioni è accessibile da `/admin/registrations`
- [ ] Approvando una richiesta, viene creato un `User` con `is_active=True`
- [ ] Se `target_lab_code` è valorizzato, l'utente riceve il `UserLabRole` corretto
- [ ] Se `desired_lab_name` è valorizzato, viene creato un nuovo `Lab` con `code` derivato dal nome
- [ ] L'operazione viene tracciata in `JobLog`
- [ ] La password temporanea generata viene mostrata nell'interfaccia admin (per comunicazione fuori banda)
- [ ] Non è possibile approvare due volte la stessa richiesta (check `is_decided`)

## File da Modificare / Creare
| File | Tipo | Descrizione modifica |
|---|---|---|
| `app/blueprints/admin/routes_users.py` | modifica | aggiungere route `registrations_list`, `registration_detail`, `registration_approve`, `registration_reject` |
| `app/blueprints/admin/templates/registrations_list.html` | modifica | verificare che gestisca correttamente i link alle nuove route |
| `app/blueprints/admin/templates/registration_detail.html` | modifica | aggiungere form POST per approve/reject con campo note admin |

## Dipendenze
- **Richiede prima:** nessuna
- **Blocca:** nessuna

## Rischi
- **Creazione Lab con code duplicato:** se `desired_lab_name` produce un codice già esistente.
  Mitigazione: verificare unicità prima del commit, mostrare errore flash se duplicato.
- **Password in chiaro nell'interfaccia:** la password temporanea è visibile solo all'admin
  nell'interfaccia; l'utente deve cambiarla al primo accesso. Rischio accettabile in assenza
  di un sistema email configurato.

## Stima Effort
- **Complessità:** L (1-2gg)
- **File coinvolti:** 3
- **Nuova migrazione DB:** no
- **Dipendenze esterne:** nessuna (email opzionale, fuori scope)
