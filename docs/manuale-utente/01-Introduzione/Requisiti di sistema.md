# Requisiti di sistema

## Per gli utenti
OCHEM e' un'applicazione web accessibile da qualsiasi browser moderno.

| Requisito | Dettaglio |
|-----------|-----------|
| Browser | Chrome, Firefox, Edge, Safari (versioni recenti) |
| JavaScript | Abilitato (necessario per i grafici Plotly) |
| Connessione | Connessione internet attiva |
| File CSV | Per l'upload dei risultati, servono file in formato CSV |

> [!warning] Browser non supportati
> Internet Explorer non e' supportato.

## Per gli amministratori di sistema

| Requisito | Versione minima |
|-----------|----------------|
| Python | 3.11+ |
| SQLite | 3.x |
| pip | Ultima versione stabile |

### Dipendenze principali
- Flask >= 3.0
- SQLAlchemy >= 2.0
- pandas >= 2.0
- numpy >= 1.24
- Plotly (per i grafici lato client)

## Vedi anche
- [[Cos'e' OCHEM]]
