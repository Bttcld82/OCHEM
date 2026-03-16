# manage.py
from app import create_app
from flask_migrate import upgrade, init as mig_init, migrate as mig_migrate, stamp
import click
import os
import pathlib

app = create_app()

@click.group()
def cli():
    pass

@cli.command("db_init")
def db_init():
    os.makedirs("instance", exist_ok=True)
    with app.app_context():
        if not pathlib.Path("migrations").exists():
            mig_init()
            stamp()
        mig_migrate(message="initial")
        upgrade()
    click.echo("Database inizializzato.")

@cli.command("run")
@click.option('--host', default='127.0.0.1', help='Host su cui ascoltare')
@click.option('--port', default=5000, help='Porta')
def run_dev(host, port):
    """Avvia il server di sviluppo con debug e reloader."""
    app.run(host=host, port=port, debug=True, use_reloader=True)

if __name__ == "__main__":
    cli()
