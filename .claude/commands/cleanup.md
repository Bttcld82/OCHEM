Avvia una sessione di pulizia file orfani nel progetto OCHEM.

Usa l'agente **file-cleaner** per:
1. Mappare tutti i file Python fuori da `app/` e `migrations/`
2. Verificare per ciascuno se è importato, referenziato o recente
3. Classificarli in KEEP / REVIEW_NEEDED / SAFE_TO_ARCHIVE
4. Mostrare la lista dei candidati all'archiviazione e chiedere conferma
5. Spostare i file approvati in `_archive/YYYY-MM-DD/`
6. Produrre un report finale

Se vuoi limitare l'analisi a una sottocartella specifica, indicala dopo il comando (es. `/cleanup scripts/`).
Se hai già identificato file specifici da archiviare, elencali dopo il comando (es. `/cleanup debug_chart_data.py fix_nh4_no3_toc.py`).
