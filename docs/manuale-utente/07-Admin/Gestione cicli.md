# Gestione cicli

Gli amministratori gestiscono i cicli PT dalla creazione alla pubblicazione.

## Cicli in attesa di revisione

**URL:** `/admin/cycles/pending`

Mostra i cicli in stato `draft` con:
- Nome e codice ciclo
- Provider
- Data creazione
- Azioni: **Apri**, **Approva**, **Rigetta**

## Revisione di un ciclo

**URL:** `/admin/cycles/<id>/review`

La pagina di revisione mostra:
- Dettagli del ciclo (nome, provider, date)
- Lista dei **parametri** con Xpt e sigma PT
- **Documenti PDF** allegati
- Segnalazioni di problemi

## Pubblicare un ciclo

Per pubblicare un ciclo (passarlo da `draft` a `published`):

1. Verifica che tutti i parametri abbiano **Xpt** e **sigma PT** definiti
2. Verifica che sia presente almeno un **documento PDF**
3. Clicca su **"Pubblica"**

> [!danger] Requisiti obbligatori
> La pubblicazione viene bloccata se:
> - Manca il documento PDF (`doc_id` nullo)
> - Uno o piu' parametri non hanno Xpt o sigma PT definiti

## Vedi anche
- [[05-Cicli/Cosa sono i cicli|Cosa sono i cicli]]
- [[05-Cicli/Stati di un ciclo|Stati di un ciclo]]
- [[Gestione parametri]]
