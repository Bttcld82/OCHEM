# Gestione laboratori

Gli amministratori possono creare e gestire i laboratori della piattaforma.

## Lista laboratori

**URL:** `/admin/labs`

Mostra tutti i laboratori con:
- Codice e nome
- Citta'
- Email di contatto
- Stato (attivo/inattivo)
- Azioni (modifica, visualizza utenti)

## Creare un laboratorio

**URL:** `/admin/labs/new`

1. Clicca su **"Nuovo laboratorio"**
2. Compila i campi:
   - **Codice**: identificativo univoco (es. `LAB_ALPHA`)
   - **Nome**: nome completo del laboratorio
   - **Citta'**: sede del laboratorio
   - **Email contatto**: email di riferimento
   - **Telefono contatto**: (opzionale)
3. Clicca su **"Salva"**

## Gestire utenti del laboratorio

**URL:** `/admin/labs/<lab_code>/users`

Da questa pagina puoi:
- Vedere tutti gli utenti del laboratorio con il loro ruolo
- **Cambiare ruolo** di un utente (viewer, analyst, owner_lab)
- **Rimuovere** un utente dal laboratorio
- **Invitare** nuovi utenti (vedi [[Inviti utenti]])

> [!warning] Vincolo Owner
> Non puoi rimuovere o declassare l'ultimo `owner_lab` di un laboratorio.

## Vedi anche
- [[Gestione utenti]]
- [[Inviti utenti]]
- [[Dashboard admin]]
