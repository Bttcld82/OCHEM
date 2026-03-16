Avvia una pipeline di code review sui file modificati nel progetto OCHEM.

## Comportamento

1. Recupera i file Python modificati con:
   ```bash
   git diff --name-only HEAD
   git diff --name-only --cached
   ```
   Se non ci sono file modificati, chiedi all'utente quali file analizzare.

2. Filtra solo i file rilevanti:
   - `app/blueprints/**/routes_*.py` → analisi sicurezza route
   - `app/models.py` → analisi coerenza modelli
   - `app/forms.py` → analisi validazione form
   - `app/blueprints/**/templates/*.html` → analisi XSS e variabili
   - `scripts/*.py` o file root → analisi qualità/utilità

3. Usa l'agente **code-reviewer** per analisi statica:
   - Sicurezza route (login_required, CSRF, ruoli)
   - Coerenza modelli/FK
   - Gestione errori
   - Vulnerabilità XSS nei template

4. Se tra i file modificati ci sono `routes_*.py`, usa anche **route-tester** per:
   - Verificare che le route nuove/modificate rispondano con status code attesi
   - Controllare che le protezioni di accesso funzionino

5. Consolida i risultati in un report unico con priorità CRITICO / MEDIO / BASSO.

## Uso diretto su file specifici

Se vuoi analizzare file specifici invece di quelli git-modified:
```
/review app/blueprints/admin/routes_cycles.py app/blueprints/dati/routes_dati.py
```

## Output atteso
- Lista problemi con file:riga, descrizione, impatto, fix suggerito
- Risultati test route (se applicabile)
- Eventuale suggerimento di invocare plan-writer per i fix critici
