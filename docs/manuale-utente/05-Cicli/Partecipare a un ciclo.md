# Partecipare a un ciclo

La partecipazione di un laboratorio a un ciclo PT viene gestita tramite la tabella delle **partecipazioni** (`LabParticipation`).

## Come funziona

1. Un ciclo viene **pubblicato** dall'amministratore
2. Il laboratorio viene **iscritto** al ciclo (stato: `active`)
3. Gli analisti del laboratorio possono:
   - [[06-Statistiche/Scaricare il template CSV|Scaricare il template CSV]] con i parametri del ciclo
   - [[06-Statistiche/Caricare i risultati|Caricare i risultati]] delle analisi
4. I risultati vengono elaborati e gli z-score calcolati automaticamente

## Stato della partecipazione

| Stato | Significato |
|-------|-------------|
| `active` | Partecipazione attiva, il lab puo' caricare risultati |

## Dove vedere i cicli attivi

- Dall'[[04-Dashboard/Hub Laboratorio|Hub Laboratorio]], nella **Card Cicli** sono elencati gli ultimi cicli pubblicati

## Ruolo minimo richiesto

| Azione | Ruolo minimo |
|--------|-------------|
| Vedere i cicli | `viewer` |
| Caricare risultati | `analyst` |

## Vedi anche
- [[Cosa sono i cicli]]
- [[06-Statistiche/Scaricare il template CSV|Scaricare il template CSV]]
