# Scaricare il template CSV

Prima di caricare i risultati, puoi scaricare un **template CSV precompilato** con i parametri del ciclo.

**URL:** `/l/<lab_code>/stats/template.csv`

## Come fare

1. Accedi all'[[04-Dashboard/Hub Laboratorio|Hub Laboratorio]]
2. Vai alla sezione **Statistiche** o **Upload**
3. Clicca su **"Scarica template"**
4. Il file CSV verra' scaricato automaticamente

## Struttura del template

Il file CSV scaricato contiene le seguenti colonne:

| Colonna | Descrizione | Esempio |
|---------|-------------|---------|
| `parameter_code` | Codice del parametro | `NH4` |
| `result_value` | Valore misurato (da compilare) | `2.45` |
| `technique_code` | Codice tecnica analitica usata | `ICP_OES` |
| `unit_code` | Unita' di misura | `MG_L` |
| `date_performed` | Data dell'analisi | `2024-03-15` |

## Come compilarlo

1. Apri il file con Excel, LibreOffice Calc o un editor di testo
2. Compila la colonna `result_value` con i tuoi risultati
3. Compila `technique_code` con la tecnica utilizzata
4. Inserisci la data in `date_performed`
5. **Non modificare** la colonna `parameter_code`
6. Salva come CSV (separatore: virgola)

> [!warning] Formato numeri
> Usa il **punto** come separatore decimale (es. `2.450`, non `2,450`).

## Ruolo minimo richiesto
`analyst`

## Vedi anche
- [[Caricare i risultati]]
- [[05-Cicli/Parametri del ciclo|Parametri del ciclo]]
