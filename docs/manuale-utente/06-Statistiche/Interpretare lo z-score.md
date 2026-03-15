# Interpretare lo z-score

Lo **z-score** e' l'indicatore principale per valutare le prestazioni di un laboratorio nel Proficiency Testing.

## Formula

$$z = \frac{x_{lab} - X_{pt}}{\sigma_{pt}}$$

| Simbolo | Significato |
|---------|-------------|
| **x_lab** | Valore misurato dal laboratorio |
| **Xpt** | Valore assegnato (riferimento del provider) |
| **sigma_pt** | Deviazione standard target per la valutazione |

## Interpretazione

### Valutazione standard (ISO 13528)

| Intervallo | Giudizio | Azione |
|-----------|----------|--------|
| \|z\| < 2.0 | **Soddisfacente** | Nessuna azione richiesta |
| 2.0 <= \|z\| < 3.0 | **Discutibile** | Investigare le cause, monitorare |
| \|z\| >= 3.0 | **Insoddisfacente** | Azione correttiva necessaria |

### Significato pratico

- **z = 0**: il risultato del laboratorio coincide perfettamente con il valore di riferimento
- **z positivo**: il laboratorio ha misurato un valore **superiore** al riferimento
- **z negativo**: il laboratorio ha misurato un valore **inferiore** al riferimento

## Altre statistiche calcolate

### sz2 (z-score al quadrato)
$$sz2 = z^2$$

Utile per valutare l'entita' dello scostamento indipendentemente dal segno.

### rsz (Robust Standard Deviation)
Calcolata con il metodo MAD (Median Absolute Deviation):

$$rsz = MAD\_K \times mediana(|z_i - mediana(z)|)$$

Dove **MAD_K = 1.4826** (fattore di consistenza per distribuzione normale).

La rsz e' una stima robusta della dispersione degli z-score, meno sensibile a valori anomali.

## Esempio pratico

> Supponiamo un ciclo con parametro Ammonio:
> - Xpt = 2.500 mg/L
> - Sigma PT = 0.300 mg/L
> - Il tuo laboratorio misura: 2.800 mg/L
>
> z = (2.800 - 2.500) / 0.300 = **1.0** → Soddisfacente ✅

> Se avessi misurato 3.500 mg/L:
> z = (3.500 - 2.500) / 0.300 = **3.33** → Insoddisfacente ❌

## Vedi anche
- [[Tabella risultati]]
- [[Carte di controllo]]
- [[05-Cicli/Parametri del ciclo|Parametri del ciclo]]
- [[08-Glossario/Glossario|Glossario]]
