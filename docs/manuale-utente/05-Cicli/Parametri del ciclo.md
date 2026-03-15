# Parametri del ciclo

Ogni ciclo PT include una lista di **parametri chimici** che i laboratori devono analizzare.

## Struttura

Per ogni parametro nel ciclo sono definiti:

| Campo | Descrizione | Esempio |
|-------|-------------|---------|
| **Codice parametro** | Identificativo del parametro | `NH4`, `NO3`, `PH` |
| **Nome** | Nome descrittivo | Ammonio, Nitrati, pH |
| **Unita' di misura** | Unita' del risultato | mg/L, pH units |
| **Xpt** | Valore assegnato (riferimento) | 2.450 |
| **Sigma PT** | Deviazione standard target | 0.320 |

## Cosa sono Xpt e Sigma PT

### Xpt (valore assegnato)
E' il valore di riferimento stabilito dal provider per quel parametro in quel ciclo. Rappresenta il "valore vero" atteso.

### Sigma PT (deviazione standard target)
E' la deviazione standard di riferimento usata per valutare le prestazioni. Definisce quanto scostamento dal valore Xpt e' "accettabile".

## Relazione con lo z-score

Il calcolo dello z-score usa direttamente questi valori:

$$z = \frac{x_{lab} - X_{pt}}{\sigma_{pt}}$$

Dove `x_lab` e' il valore misurato dal laboratorio.

Approfondisci in [[06-Statistiche/Interpretare lo z-score|Interpretare lo z-score]].

## Vedi anche
- [[Cosa sono i cicli]]
- [[06-Statistiche/Interpretare lo z-score|Interpretare lo z-score]]
- [[07-Admin/Gestione parametri|Gestione parametri (Admin)]]
