# create_db.py
from app import create_app, db
import os

app = create_app()
with app.app_context():
    os.makedirs(app.instance_path, exist_ok=True)
    print("Instance path ->", app.instance_path)
    print("DB URI ->", app.config["SQLALCHEMY_DATABASE_URI"])
    db.create_all()  # crea tutte le tabelle dei modelli importati
    # verifica esistenza file (solo per SQLite)
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if uri.startswith("sqlite:///"):
        db_file = uri.replace("sqlite:///", "")
        print("DB file atteso ->", db_file)
        print("Esiste? ->", os.path.exists(db_file))

