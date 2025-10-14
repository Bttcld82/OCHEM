#!/usr/bin/env python3
"""
Script per creare un utente admin di test
"""

import sys
from pathlib import Path

# Aggiungi la directory root del progetto al Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import User
from datetime import datetime

def create_admin_user():
    """Crea un utente admin di test"""
    app = create_app()
    
    with app.app_context():
        # Verifica se esiste già un admin
        existing_admin = User.query.filter_by(email="admin@ochem.local").first()
        if existing_admin:
            print("❌ Utente admin già esistente!")
            print(f"Email: {existing_admin.email}")
            print(f"Nome: {existing_admin.full_name}")
            return
        
        # Crea nuovo utente admin
        admin_user = User(
            email="admin@ochem.local",
            first_name="Amministratore",
            last_name="Sistema",
            is_active=True
        )
        
        # Imposta password
        admin_user.set_password("admin123")
        
        # Salva nel database
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Utente admin creato con successo!")
        print(f"📧 Email: admin@ochem.local")
        print(f"🔑 Password: admin123")
        print(f"👤 Nome: Amministratore Sistema")
        print(f"🆔 ID: {admin_user.id}")
        print("\n⚠️  IMPORTANTE: Cambia la password al primo accesso!")

if __name__ == "__main__":
    create_admin_user()