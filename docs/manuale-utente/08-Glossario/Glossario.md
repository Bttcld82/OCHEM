# Glossario

Termini e acronimi utilizzati nella piattaforma OCHEM.

---

## A

### Analyst
Ruolo per laboratorio. Puo' caricare risultati e consultare statistiche. Vedi [[03-Ruoli/Ruolo Analyst|Ruolo Analyst]].

### Admin
Ruolo globale con accesso completo alla piattaforma. Vedi [[03-Ruoli/Ruolo Admin|Ruolo Admin]].

---

## C

### Carta di controllo
Grafico che mostra l'andamento dello z-score nel tempo per monitorare le prestazioni di un laboratorio. Vedi [[06-Statistiche/Carte di controllo|Carte di controllo]].

### CL (Center Line)
Linea centrale nella carta di controllo, corrispondente a z = 0 (prestazione perfetta).

### Ciclo PT
Un round di prove interlaboratorio organizzato da un provider. Vedi [[05-Cicli/Cosa sono i cicli|Cosa sono i cicli]].

### CSV
Comma-Separated Values. Formato file usato per caricare i risultati sulla piattaforma.

---

## I

### ISO 13528
Standard internazionale per i metodi statistici utilizzati nel Proficiency Testing.

### ISO/IEC 17025
Standard per la competenza dei laboratori di prova e taratura. Il PT e' uno dei requisiti per l'accreditamento.

---

## L

### LCL (Lower Control Limit)
Limite inferiore di controllo nella carta di controllo, corrispondente a z = -3.

---

## M

### MAD (Median Absolute Deviation)
Metodo robusto per stimare la dispersione. Utilizzato nel calcolo della rsz.

### MAD_K
Fattore di consistenza per la MAD, pari a **1.4826** per la distribuzione normale.

### Matrice
Tipo di campione analizzato (es. acqua, suolo, aria).

---

## O

### Owner Lab
Responsabile del laboratorio sulla piattaforma. Ruolo con il livello piu' alto per laboratorio. Vedi [[03-Ruoli/Ruolo Owner Lab|Ruolo Owner Lab]].

---

## P

### Parametro
Grandezza chimica analizzata (es. pH, Ammonio, Nitrati). Ha un codice, unita' di misura e tecnica associata.

### Provider
Ente organizzatore che crea e gestisce i cicli PT, distribuisce campioni ai laboratori.

### Proficiency Testing (PT)
Processo di valutazione delle prestazioni di un laboratorio tramite confronto interlaboratorio.

### PtStats
Statistiche aggregate per laboratorio/parametro/ciclo: numero risultati, media z, rsz.

---

## R

### rsz (Robust Standard Deviation of z-scores)
Stima robusta della dispersione degli z-score, calcolata come `MAD_K * mediana(|z - mediana(z)|)`.

---

## S

### Sigma PT (σ_pt)
Deviazione standard target per la valutazione delle prestazioni, definita dal provider per ogni parametro in ogni ciclo.

### sz2
Z-score al quadrato (z²). Misura dell'entita' dello scostamento, indipendente dal segno.

---

## U

### UCL (Upper Control Limit)
Limite superiore di controllo nella carta di controllo, corrispondente a z = +3.

---

## V

### Viewer
Ruolo base per laboratorio con accesso in sola lettura. Vedi [[03-Ruoli/Ruolo Viewer|Ruolo Viewer]].

---

## X

### Xpt (Valore assegnato)
Valore di riferimento stabilito dal provider per un parametro in un ciclo PT. Rappresenta il "valore vero" atteso.

---

## Z

### Z-score
Indicatore di prestazione: `z = (x_lab - Xpt) / sigma_pt`. Vedi [[06-Statistiche/Interpretare lo z-score|Interpretare lo z-score]].

| Intervallo | Giudizio |
|-----------|----------|
| \|z\| < 2 | Soddisfacente |
| 2 <= \|z\| < 3 | Discutibile |
| \|z\| >= 3 | Insoddisfacente |
