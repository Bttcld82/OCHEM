# Gestione parametri

Gli amministratori possono creare e gestire i parametri chimici disponibili nella piattaforma.

## Lista parametri

**URL:** `/admin/params`

Mostra tutti i parametri con:
- Codice e nome
- Unita' di misura
- Tecnica analitica
- Matrice
- Stato (attivo/inattivo)

## Creare un parametro

**URL:** `/admin/params/new`

1. Clicca su **"Nuovo parametro"**
2. Compila:
   - **Codice**: identificativo (es. `NH4`, `NO3`, `PH`)
   - **Nome**: nome completo (es. "Ammonio", "Nitrati")
   - **Unita' di misura**: seleziona dall'elenco (es. mg/L)
   - **Tecnica**: tecnica analitica associata (opzionale)
   - **Matrice**: tipo di campione (opzionale)
   - **Min/Max**: valori limite (opzionale)
   - **Cifre decimali**: precisione (opzionale)
3. Clicca su **"Salva"**

## Altre anagrafiche gestibili

Dalla sezione admin puoi gestire anche:
- **Unita' di misura** (`/admin/units`)
- **Tecniche analitiche** (`/admin/techniques`)
- **Provider** (`/admin/providers`)

## Vedi anche
- [[Gestione cicli]]
- [[05-Cicli/Parametri del ciclo|Parametri del ciclo]]
