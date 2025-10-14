"""
Stats Blueprint - Modulo Statistiche per Laboratori
Funzionalità:
- Download template CSV per inserimento risultati
- Upload e calcolo z-score, sz², rsz 
- Visualizzazione grafici di controllo
- Gestione risultati cicli PT per laboratori
- Statistiche generali per tutti i laboratori
"""

from flask import Blueprint

# Blueprint principale per statistiche specifiche del laboratorio
stats_bp = Blueprint('stats_bp', __name__, 
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/l/<lab_code>/stats')

# Blueprint per statistiche generali (senza lab_code)
stats_general_bp = Blueprint('stats_general_bp', __name__,
                           template_folder='templates',
                           static_folder='static',
                           url_prefix='/stats')

# Import delle route (necessario per registrare le route)
from . import routes_stats
from . import api_routes