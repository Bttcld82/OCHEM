---
id: PROP-009
title: "Fix HTTP 500 su POST /admin/cycles/new: coerce provider_id e variabili mancanti nel template"
status: done
priority: P1
effort: S
category: admin
gap_refs: []
origin: user
created_at: 2026-03-16
updated_at: 2026-03-16
decision: approved
decision_notes: "non specificata"
plan_file: ""
---

# PROP-009 — Fix HTTP 500 su POST /admin/cycles/new

## Descrizione

La route `GET /admin/cycles/new` funziona correttamente (la pagina si carica),
ma la `POST` (submit del form) genera un HTTP 500 Internal Server Error.

L'analisi del codice ha identificato due difetti distinti che si sommano:

### Difetto 1 — coerce incompatibile su provider_id (causa principale del 500)

In `app/forms.py`, `CycleForm.provider_id` è definito come:

```python
provider_id = SelectField('Fornitore', validators=[Optional()],
                          coerce=lambda x: int(x) if x else None)
```

Le `choices` del campo sono costruite con la stringa vuota `''` come primo elemento:

```python
self.provider_id.choices = [('', '— Nessun fornitore —')] + [...]
```

WTForms, durante la validazione POST, applica la `coerce` al valore ricevuto dalla
request e poi controlla che il risultato sia presente nelle `choices`.
La `coerce` trasforma `''` in `None`, ma le choices contengono `''` (non `None`):
il confronto fallisce e WTForms solleva un `ValueError` non gestito, producendo il 500.

La correzione consiste nell'allineare il valore sentinel nelle `choices` con quello
prodotto dalla `coerce`: usare `None` come valore della scelta vuota oppure
cambiare la `coerce` in modo che lasci `''` invariato e tratti la conversione
solo in fase di utilizzo del valore (nella route).

### Difetto 2 — variabili mancanti nel template cycle_form.html in modalità edit

Il template `cycle_form.html` usa `participations_count` e `results_count`
(righe 95-96) all'interno del blocco `{% if cycle %}`. La route `cycle_edit`
(in `routes_cycles.py`, riga 231) richiama:

```python
return render_template("cycle_form.html", form=form, cycle=cycle)
```

senza passare `participations_count` e `results_count`. In modalità creazione
(`cycle=None`) il blocco `{% if cycle %}` non viene eseguito quindi il 500 non
si manifesta qui; ma in modalità edit il template causa un `UndefinedError`
di Jinja2 quando si accede a `participations_count`.

Questo secondo difetto non colpisce la POST di `/cycles/new` ma colpisce la
GET e POST di `/cycles/<id>/edit` e viene corretto contestualmente per
completezza e per evitare un bug latente.

## Motivazione

Senza la correzione del Difetto 1 è impossibile creare qualsiasi ciclo PT dalla
UI amministrativa. La creazione di un ciclo è il prerequisito di tutta la
partecipazione dei laboratori, del caricamento risultati e del calcolo z-score.
Il bug blocca l'intero flusso PT.

## Soluzione Proposta

### Fix Difetto 1 — `app/forms.py`

Modificare la `CycleForm` in modo che il valore sentinel della scelta vuota
sia coerente con la `coerce`.

**Opzione A (consigliata):** mantenere `coerce=int` standard, usare `0` come
valore sentinel e trattare `0` come "nessun fornitore" nella route.

**Opzione B:** usare `coerce=str`, lasciare `''` come sentinel nelle choices,
e convertire nella route solo se il valore ricevuto è una stringa numerica.

**Opzione C (minimale):** sostituire la lambda con una funzione che restituisce
`None` solo per `None` (non per `''`) e aggiornare le choices per usare il
valore intero `0` oppure una stringa numerica dummy riconoscibile.

La scelta più pulita è l'**Opzione A**: WTForms gestisce nativamente
`SelectField` con `coerce=int` quando le choices contengono valori interi;
la scelta vuota si gestisce con il valore `0` o con `coerce=lambda x: int(x) if x and x != '0' else None`
applicata in modo simmetrico sia alle choices che al valore sentinel.

In ogni caso la correzione richiede che il valore nella lista `choices` e
il valore prodotto dalla `coerce` siano dello stesso tipo e valore per la
scelta vuota.

### Fix Difetto 2 — `app/blueprints/admin/routes_cycles.py`

Nella route `cycle_edit`, calcolare i conteggi e passarli al template:

```python
participations_count = LabParticipation.query.filter_by(cycle_code=cycle.code).count()
results_count = Result.query.filter_by(cycle_code=cycle.code).count()
return render_template("cycle_form.html", form=form, cycle=cycle,
                       participations_count=participations_count,
                       results_count=results_count)
```

La route `cycle_create` non è interessata perché passa `cycle=None` e il
blocco `{% if cycle %}` nel template non viene eseguito.

## Acceptance Criteria

- [ ] La POST su `/admin/cycles/new` con tutti i campi obbligatori compilati
      e nessun fornitore selezionato non genera un 500 e crea il ciclo.
- [ ] La POST su `/admin/cycles/new` con un fornitore selezionato crea il ciclo
      con il `provider_id` corretto salvato nel DB.
- [ ] La validazione del form (codice duplicato, date incoerenti) funziona
      regolarmente e mostra gli errori inline senza 500.
- [ ] La GET e la POST su `/admin/cycles/<id>/edit` non generano un
      `UndefinedError` Jinja2 per `participations_count` o `results_count`.
- [ ] Il pulsante "Elimina" nella pagina di modifica ciclo appare correttamente
      disabilitato se il ciclo ha partecipazioni o risultati.

## File da Modificare / Creare

| File | Tipo | Descrizione modifica |
|---|---|---|
| `app/forms.py` | modifica | Correggere `coerce` e/o sentinel nelle `choices` di `CycleForm.provider_id` |
| `app/blueprints/admin/routes_cycles.py` | modifica | Aggiungere `participations_count` e `results_count` nella chiamata `render_template` di `cycle_edit` |

## Dipendenze

- **Richiede prima:** nessuna
- **Blocca:** nessuna (ma sblocca di fatto l'intero flusso di creazione cicli)

## Rischi

- **Migrazione DB:** nessuna. Il fix è interamente a livello applicativo.
- **Regressione `cycle_edit`:** il calcolo dei conteggi aggiunto è una query
  di sola lettura; rischio di regressione nullo.
- **Comportamento `provider_id` già in DB:** nessuna modifica al modello dati;
  i cicli esistenti con `provider_id` NULL non sono influenzati.

## Stima Effort

- **Complessità:** S (1-2h)
- **File coinvolti:** 2
- **Nuova migrazione DB:** no
- **Dipendenze esterne:** nessuna
