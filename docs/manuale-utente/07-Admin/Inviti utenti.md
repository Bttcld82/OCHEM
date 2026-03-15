# Inviti utenti

Gli amministratori possono invitare utenti direttamente a un laboratorio tramite **token di invito**.

## Come invitare un utente

**URL:** `/admin/labs/<lab_code>/users`

1. Vai alla gestione utenti del laboratorio
2. Compila il form di invito:
   - **Email**: indirizzo email dell'utente da invitare
   - **Ruolo**: il ruolo da assegnare (viewer, analyst, owner_lab)
3. Clicca su **"Invia invito"**

## Cosa succede

1. Il sistema genera un **token univoco** (64 caratteri, `secrets.token_urlsafe`)
2. Viene creato un record `InviteToken` con scadenza **7 giorni**
3. Il link di invito viene mostrato (in ambiente di sviluppo, stampato in console)
4. L'utente invitato riceve il link e puo' [[02-Accesso/Accettare un invito|accettare l'invito]]

## Gestione token

| Stato token | Significato |
|-------------|-------------|
| **Valido** | Non scaduto e non ancora usato |
| **Scaduto** | Superati i 7 giorni - generarne uno nuovo |
| **Usato** | L'utente ha gia' accettato l'invito |

## Vedi anche
- [[02-Accesso/Accettare un invito|Accettare un invito (lato utente)]]
- [[Gestione laboratori]]
- [[Gestione utenti]]
