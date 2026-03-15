# Gestione utenti

Gli amministratori possono gestire tutti gli utenti della piattaforma.

## Lista utenti

**URL:** `/admin/users`

La tabella mostra:

| Colonna | Descrizione |
|---------|-------------|
| Nome | Nome completo dell'utente |
| Email | Indirizzo email |
| Admin | Badge se l'utente e' admin |
| Laboratori | Numero di laboratori associati |
| Stato | Attivo/Inattivo |
| Ultimo login | Data dell'ultimo accesso |
| Azioni | Dettaglio, make/remove admin |

## Dettaglio utente

**URL:** `/admin/users/<id>`

Mostra:
- Informazioni personali (nome, email, date)
- Lista dei laboratori con relativi ruoli
- Possibilita' di cambiare ruolo per ogni laboratorio
- Possibilita' di rimuovere da un laboratorio

## Promuovere/rimuovere Admin

Dalla lista utenti puoi:
- **Make Admin**: promuovere un utente a ruolo admin globale
- **Remove Admin**: rimuovere il privilegio admin

> [!warning] Ultimo Admin
> Non puoi rimuovere il privilegio admin all'ultimo amministratore del sistema.

## Vedi anche
- [[Gestione laboratori]]
- [[Approvazione registrazioni]]
- [[03-Ruoli/Panoramica ruoli|Panoramica ruoli]]
