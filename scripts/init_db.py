#!/usr/bin/env python3
"""
Script di inizializzazione del database OCHEM
Legge DATABASE_URL da .env e applica le migrazioni Alembic
"""

import os
import sys
from pathlib import Path
import sqlalchemy as sa
from dotenv import load_dotenv

# Aggiungi la directory root al path per importare l'app
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def init_database():
    """Inizializza il database OCHEM"""
    
    # Carica variabili d'ambiente
    load_dotenv(root_dir / '.env')
    
    # Ottieni DATABASE_URL
    database_url = os.getenv('DATABASE_URL', 'sqlite:///instance/ochem.sqlite3')
    
    print(f"🔗 Connessione a: {database_url}")
    
    # Crea engine SQLAlchemy
    engine = sa.create_engine(database_url)
    
    # Applica PRAGMA SQLite se necessario
    if 'sqlite' in database_url.lower():
        with engine.connect() as conn:
            conn.execute(sa.text("PRAGMA foreign_keys=ON;"))
            conn.execute(sa.text("PRAGMA journal_mode=WAL;"))
            print("✅ PRAGMA SQLite applicati")
    
    # Verifica connessione
    try:
        with engine.connect() as conn:
            result = conn.execute(sa.text("SELECT 1")).fetchone()
            if result:
                print("✅ Connessione al database riuscita")
    except Exception as e:
        print(f"❌ Errore connessione database: {e}")
        return False
    
    print("🗄️ Database inizializzato correttamente")
    return True

def run_alembic_upgrade():
    """Esegue alembic upgrade head"""
    import subprocess
    
    try:
        # Cambia directory nella root del progetto
        os.chdir(root_dir)
        
        # Esegui alembic upgrade head
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, check=True)
        
        print("✅ Alembic upgrade head completato")
        if result.stdout:
            print(f"Output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante alembic upgrade: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Alembic non trovato. Installare con: pip install alembic")
        return False

def verify_database():
    """Verifica che il file database sia stato creato"""
    db_path = root_dir / 'instance' / 'ochem.sqlite3'
    
    if db_path.exists():
        print(f"✅ File database creato: {db_path}")
        print(f"   Dimensione: {db_path.stat().st_size} bytes")
        return True
    else:
        print(f"❌ File database non trovato: {db_path}")
        return False

if __name__ == "__main__":
    print("🚀 Inizializzazione database OCHEM")
    print("=" * 50)
    
    # Step 1: Inizializza connessione database
    if not init_database():
        sys.exit(1)
    
    # Step 2: Esegui migrazioni Alembic
    if not run_alembic_upgrade():
        sys.exit(1)
    
    # Step 3: Verifica creazione database
    if not verify_database():
        sys.exit(1)
    
    print("\n🎉 Inizializzazione database completata con successo!")