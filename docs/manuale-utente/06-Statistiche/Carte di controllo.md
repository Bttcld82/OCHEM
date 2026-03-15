# Carte di controllo

Le carte di controllo sono **grafici interattivi** che mostrano l'andamento dello z-score nel tempo.

**URL:** `/l/<lab_code>/stats/charts`

## Cosa mostrano

Il grafico presenta:
- **Asse X**: cicli PT (in ordine cronologico) o date
- **Asse Y**: valore z-score
- **Punti**: ogni punto rappresenta il risultato del laboratorio per un parametro in un ciclo

## Linee di riferimento

| Linea | Valore | Significato |
|-------|--------|-------------|
| **CL** (Center Line) | 0 | Linea centrale - prestazione perfetta |
| **UCL** (Upper Control Limit) | +3 | Limite superiore di controllo |
| **LCL** (Lower Control Limit) | -3 | Limite inferiore di controllo |

## Colorazione dei punti

I punti sul grafico seguono la stessa colorazione della [[Tabella risultati]]:
- 🟢 **Verde**: \|z\| < 2 (soddisfacente)
- 🟠 **Arancione**: 2 <= \|z\| < 3 (discutibile)
- 🔴 **Rosso**: \|z\| >= 3 (insoddisfacente)

## Interattivita'

I grafici sono realizzati con **Plotly** e offrono:
- **Hover**: passa il mouse su un punto per vedere i dettagli
- **Zoom**: seleziona un'area per ingrandire
- **Pan**: trascina per spostare la vista
- **Download**: scarica il grafico come immagine PNG

## Come interpretare il grafico

> [!tip] Segnali di attenzione
> - Punti **fuori dai limiti** UCL/LCL → azione correttiva necessaria
> - **Trend crescente/decrescente** → possibile deriva sistematica
> - Punti che **oscillano frequentemente** tra arancione e rosso → instabilita' del metodo

## Ruolo minimo richiesto
`viewer`

## Vedi anche
- [[Tabella risultati]]
- [[Interpretare lo z-score]]
