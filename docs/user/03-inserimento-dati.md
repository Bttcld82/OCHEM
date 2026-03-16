---
title: "Inserimento Dati"
description: "Come inserire i risultati di un ciclo PT: form manuale e upload CSV"
tags: [utente, dati, risultati, upload, csv]
role: user
order: 3
related:
  - user/02-hub-laboratorio
  - user/04-statistiche-zscore
---

# Inserimento Dati

Per partecipare a un ciclo PT devi inserire i risultati della tua analisi su OCHEM.
Puoi farlo in due modi: **inserimento manuale** (un risultato alla volta) o **upload CSV**.

## Inserimento Manuale

Vai su **Upload Dati** dalla navbar, oppure clicca il pulsante **Inserisci Dati** nella
card del ciclo nell'Hub Laboratorio (`/dati/insert`).

### Campi del Modulo

| Campo | Obbligatorio | Note |
|-------|-------------|------|
| Ciclo | Sì | Seleziona il ciclo PT attivo |
| Parametro | Sì | Si aggiorna automaticamente dopo aver scelto il ciclo |
| Tecnica | Sì | Metodo analitico usato |
| Valore misurato | Sì | Il risultato numerico della tua analisi |
| Incertezza | No | Incertezza estesa (k=2) se disponibile |
| Note | No | Osservazioni libere |

> **Attenzione:** dopo aver selezionato il **Ciclo**, l'elenco dei parametri si aggiorna
> automaticamente mostrando solo gli analiti previsti per quel ciclo. Attendi il caricamento
> prima di procedere.

### Modificare un Risultato

Se hai già inserito un risultato e vuoi correggerlo:
1. Vai su **Upload Dati → I miei risultati** (`/dati/results`)
2. Clicca **Modifica** sul risultato da correggere
3. Aggiorna il valore e salva

## Upload CSV

Per inserire più risultati in una sola operazione, usa l'upload CSV (`/dati/upload`).

### Formato del File CSV

```csv
cycle_code,parameter_code,technique_code,value,uncertainty,notes
PT-2024-01,CD,ICPMS,0.045,0.003,
PT-2024-01,PB,ICPMS,0.012,,misura ripetuta
```

| Colonna | Obbligatoria | Formato |
|---------|-------------|---------|
| `cycle_code` | Sì | Codice esatto del ciclo |
| `parameter_code` | Sì | Codice esatto del parametro |
| `technique_code` | Sì | Codice esatto della tecnica |
| `value` | Sì | Numero decimale (usa `.` come separatore) |
| `uncertainty` | No | Numero decimale o vuoto |
| `notes` | No | Testo libero |

> Se un codice non esiste nel sistema, la riga viene saltata con un messaggio di errore.

## Vedi anche

- [[user/04-statistiche-zscore|Statistiche e Z-Score]] — come vengono elaborati i tuoi dati
- [[user/02-hub-laboratorio|Hub Laboratorio]] — dove trovare i cicli attivi
