# Caricare i risultati

Gli analisti possono caricare i risultati delle analisi tramite **upload di file CSV**.

**URL:** `/l/<lab_code>/stats/upload`

## Procedura

1. [[Scaricare il template CSV|Scarica il template CSV]] e compilalo con i risultati
2. Accedi alla sezione **Upload** dall'[[04-Dashboard/Hub Laboratorio|Hub Laboratorio]]
3. Seleziona il **file CSV** compilato
4. Clicca su **"Carica"**
5. Il sistema elabora automaticamente i risultati

## Cosa succede dopo l'upload

Il sistema esegue in sequenza:

1. **Validazione** - Verifica che le colonne del CSV siano corrette
2. **Inserimento Result** - Salva ogni riga come `Result` nel database
3. **Calcolo z-score** - Per ogni risultato calcola z, sz2
4. **Calcolo rsz** - Calcola le statistiche aggregate (PtStats)
5. **Registrazione upload** - Salva il file in `UploadFile` con stato

## Validazioni

Il sistema controlla:
- Le colonne obbligatorie siano presenti
- I `parameter_code` corrispondano a parametri del ciclo
- I `result_value` siano numerici validi
- Le `technique_code` esistano nel sistema

> [!danger] Errori nel CSV
> Se il file contiene errori, l'upload verra' rifiutato con un messaggio che indica il problema. Correggi il file e riprova.

## Ruolo minimo richiesto
`analyst`

## Vedi anche
- [[Scaricare il template CSV]]
- [[Tabella risultati]]
- [[Interpretare lo z-score]]
