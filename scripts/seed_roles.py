#!/usr/bin/env python3
"""
Script per inizializzare i ruoli e assegnazioni secondo instructions_roles.md
"""

import sys
from pathlib import Path
from datetime import datetime

# Aggiungi la directory root al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app import create_app, db
from app.models import Role, User, Lab, UserLabRole
from app.services.roles import RoleService

def seed_roles():
    """Crea i ruoli base nel database"""
    print("🔑 Creazione ruoli base...")
    
    roles_data = [
        ('admin', 'Amministratore globale del sistema'),
        ('owner_lab', 'Proprietario del laboratorio'),
        ('analyst', 'Analista del laboratorio'),
        ('viewer', 'Visualizzatore del laboratorio')
    ]
    
    for role_name, description in roles_data:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=description)
            db.session.add(role)
            print(f"  ✅ Creato ruolo: {role_name}")
        else:
            print(f"  ⚠️  Ruolo già esistente: {role_name}")
    
    db.session.commit()
    print(f"✅ Ruoli creati/verificati")

def create_admin_user():
    """Crea un utente amministratore se non esiste"""
    print("👤 Verifica utente amministratore...")
    
    admin_email = "admin@ochem.local"
    admin_user = User.query.filter_by(email=admin_email).first()
    
    if not admin_user:
        admin_user = User(
            email=admin_email,
            first_name="Admin",
            last_name="System",
            is_active=True,
            is_admin=True,
            accepted_disclaimer_at=datetime.utcnow()
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.commit()
        print(f"  ✅ Creato utente admin: {admin_email}")
    else:
        # Assicurati che sia admin
        if not admin_user.is_admin:
            admin_user.is_admin = True
            db.session.commit()
            print(f"  ✅ Aggiornato utente a admin: {admin_email}")
        else:
            print(f"  ⚠️  Utente admin già esistente: {admin_email}")

def assign_lab_owners():
    """Assegna owner ai laboratori esistenti"""
    print("🏭 Assegnazione owner ai laboratori...")
    
    labs = Lab.query.filter_by(is_active=True).all()
    owner_role = Role.query.filter_by(name="owner_lab").first()
    
    if not owner_role:
        print("  ❌ Ruolo owner_lab non trovato!")
        return
    
    for lab in labs:
        # Verifica se il lab ha già degli owner
        existing_owners = UserLabRole.query.filter_by(
            lab_id=lab.id,
            role_id=owner_role.id
        ).count()
        
        if existing_owners == 0:
            # Trova un utente esistente o creane uno per questo lab
            lab_email = f"owner_{lab.code.lower()}@ochem.local"
            lab_user = User.query.filter_by(email=lab_email).first()
            
            if not lab_user:
                lab_user = User(
                    email=lab_email,
                    first_name=f"Owner",
                    last_name=lab.code,
                    is_active=True,
                    accepted_disclaimer_at=datetime.utcnow()
                )
                lab_user.set_password("password123")
                db.session.add(lab_user)
                db.session.flush()  # Per ottenere l'ID
            
            # Assegna il ruolo owner
            try:
                RoleService.assign_lab_role(lab_user.id, lab.id, "owner_lab")
                print(f"  ✅ Assegnato owner {lab_user.email} al lab {lab.code}")
            except Exception as e:
                print(f"  ❌ Errore assegnazione owner al lab {lab.code}: {e}")
        else:
            print(f"  ⚠️  Lab {lab.code} ha già {existing_owners} owner")

def add_sample_users():
    """Aggiunge alcuni utenti di esempio con diversi ruoli"""
    print("👥 Creazione utenti di esempio...")
    
    users_data = [
        ("analyst1@ochem.local", "Mario", "Rossi", "analyst"),
        ("analyst2@ochem.local", "Luigi", "Bianchi", "analyst"), 
        ("viewer1@ochem.local", "Paolo", "Verdi", "viewer"),
        ("viewer2@ochem.local", "Anna", "Neri", "viewer")
    ]
    
    labs = Lab.query.filter_by(is_active=True).limit(2).all()  # Prime 2 lab
    
    for email, first_name, last_name, role_name in users_data:
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                accepted_disclaimer_at=datetime.utcnow()
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
        
        # Assegna il ruolo al primo laboratorio disponibile
        if labs:
            try:
                existing = UserLabRole.query.filter_by(
                    user_id=user.id,
                    lab_id=labs[0].id
                ).first()
                
                if not existing:
                    RoleService.assign_lab_role(user.id, labs[0].id, role_name)
                    print(f"  ✅ Assegnato {role_name} {email} al lab {labs[0].code}")
                else:
                    print(f"  ⚠️  Utente {email} già associato al lab {labs[0].code}")
            except Exception as e:
                print(f"  ❌ Errore assegnazione {email}: {e}")

def print_roles_summary():
    """Stampa un riepilogo dei ruoli assegnati"""
    print("\n📊 Riepilogo ruoli:")
    print("=" * 50)
    
    # Ruoli globali
    admin_count = User.query.filter_by(is_admin=True).count()
    print(f"Amministratori globali: {admin_count}")
    
    # Ruoli per laboratorio
    labs = Lab.query.filter_by(is_active=True).all()
    for lab in labs:
        print(f"\nLab {lab.code} ({lab.name}):")
        
        roles = db.session.query(Role.name, db.func.count(UserLabRole.id)).join(
            UserLabRole, Role.id == UserLabRole.role_id
        ).filter(
            UserLabRole.lab_id == lab.id
        ).group_by(Role.name).all()
        
        for role_name, count in roles:
            print(f"  - {role_name}: {count}")
        
        if not roles:
            print("  - Nessun utente assegnato")

def main():
    """Funzione principale"""
    print("🔑 Inizializzazione sistema ruoli OCHEM")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Inizializza ruoli base
            RoleService.ensure_roles_exist()
            seed_roles()
            
            # 2. Crea utente admin
            create_admin_user()
            
            # 3. Assegna owner ai lab esistenti
            assign_lab_owners()
            
            # 4. Aggiungi utenti di esempio
            add_sample_users()
            
            # 5. Riepilogo
            print_roles_summary()
            
            print("\n🎉 Inizializzazione ruoli completata!")
            
        except Exception as e:
            print(f"\n❌ Errore durante l'inizializzazione: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    main()