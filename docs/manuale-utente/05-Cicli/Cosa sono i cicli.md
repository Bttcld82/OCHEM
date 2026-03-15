# Cosa sono i cicli

Un **Ciclo PT (Proficiency Testing)** e' un round di prove interlaboratorio organizzato da un provider.

## Il concetto

Un provider (ente organizzatore) distribuisce **campioni identici** a piu' laboratori. Ogni laboratorio analizza il campione e riporta i risultati. I risultati vengono poi confrontati con il **valore di riferimento (Xpt)** e la **deviazione standard target (sigma PT)** per calcolare lo z-score.

## Struttura di un ciclo

Ogni ciclo contiene:

| Campo | Descrizione |
|-------|-------------|
| **Codice** | Identificativo univoco (es. `CY2024_01`) |
| **Nome** | Nome descrittivo del ciclo |
| **Provider** | Ente organizzatore |
| **Stato** | Fase attuale del ciclo (vedi [[Stati di un ciclo]]) |
| **Date** | Data inizio e fine |
| **Parametri** | Lista di parametri da analizzare con valori Xpt e sigma PT |
| **Documenti** | PDF di istruzioni e report allegati |

## Parametri del ciclo

Ogni ciclo ha uno o piu' **parametri** associati (es. pH, Ammonio, Nitrati, TOC). Per ogni parametro il provider definisce:
- **Xpt**: valore assegnato (valore "vero" di riferimento)
- **Sigma PT**: deviazione standard per la valutazione delle prestazioni

Questi valori servono per il [[06-Statistiche/Interpretare lo z-score|calcolo dello z-score]].

## Vedi anche
- [[Stati di un ciclo]]
- [[Partecipare a un ciclo]]
- [[Parametri del ciclo]]
