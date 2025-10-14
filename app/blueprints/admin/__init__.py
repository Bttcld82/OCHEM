from flask import Blueprint
bp = Blueprint("admin", __name__, template_folder="templates")

# Importa tutti i moduli delle routes per registrare le route
from . import routes_main      # Dashboard e routes principali  # noqa
from . import routes_cycles    # Gestione cicli  # noqa
from . import routes_labs      # Gestione laboratori  # noqa
from . import routes_parameters  # Gestione parametri  # noqa
from . import routes_units     # Gestione unità di misura  # noqa
from . import routes_techniques  # Gestione tecniche analitiche  # noqa
from . import routes_providers  # Gestione fornitori  # noqa
from . import routes_users     # Gestione utenti e ruoli  # noqa
from . import routes_docs      # Gestione documentazione  # noqa
