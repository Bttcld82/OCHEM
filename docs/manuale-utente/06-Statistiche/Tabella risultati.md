# Tabella risultati

La tabella risultati mostra tutti i risultati caricati dal laboratorio con i relativi calcoli statistici.

**URL:** `/l/<lab_code>/stats/results`

## Colonne della tabella

| Colonna | Descrizione |
|---------|-------------|
| **Parametro** | Codice del parametro analizzato |
| **Valore misurato** | Il risultato del laboratorio |
| **z** | Z-score calcolato |
| **sz2** | Z-score al quadrato |
| **rsz** | Deviazione standard robusta |

## Colorazione z-score

I valori di z-score sono colorati per facilitare la lettura:

| Colore | Condizione | Significato |
|--------|-----------|-------------|
| 🟢 Verde | \|z\| < 2 | Prestazione **soddisfacente** |
| 🟠 Arancione | 2 <= \|z\| < 3 | Prestazione **discutibile** - attenzione |
| 🔴 Rosso | \|z\| >= 3 | Prestazione **insoddisfacente** - azione richiesta |

Approfondisci in [[Interpretare lo z-score]].

## Ruolo minimo richiesto
`viewer`

## Vedi anche
- [[Caricare i risultati]]
- [[Carte di controllo]]
- [[Interpretare lo z-score]]
