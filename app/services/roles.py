# app/services/roles.py
"""
Service layer per la gestione dei ruoli
"""
from datetime import datetime
from flask import current_app
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Lab, Role, UserLabRole

class RoleManagementError(Exception):
    """Eccezione per errori nella gestione dei ruoli"""
    pass

class RoleService:
    """Service per la gestione dei ruoli"""
    
    ROLE_HIERARCHY = {
        "owner_lab": 3,
        "analyst": 2, 
        "viewer": 1
    }
    
    LAB_ROLES = ["owner_lab", "analyst", "viewer"]
    GLOBAL_ROLES = ["admin"]
    
    @staticmethod
    def ensure_roles_exist():
        """Garantisce che tutti i ruoli necessari esistano nel database"""
        all_roles = RoleService.LAB_ROLES + RoleService.GLOBAL_ROLES
        
        for role_name in all_roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(
                    name=role_name,
                    description=f"Ruolo {role_name}"
                )
                db.session.add(role)
        
        db.session.commit()
    
    @staticmethod
    def assign_lab_role(user_id, lab_id, role_name):
        """Assegna un ruolo a un utente per un laboratorio"""
        if role_name not in RoleService.LAB_ROLES:
            raise RoleManagementError(f"Ruolo {role_name} non valido per i laboratori")
        
        user = User.query.get_or_404(user_id)
        lab = Lab.query.get_or_404(lab_id)
        role = Role.query.filter_by(name=role_name).first()
        
        if not role:
            raise RoleManagementError(f"Ruolo {role_name} non trovato")
        
        # Verifica se esiste già un ruolo per questo utente e laboratorio
        existing = UserLabRole.query.filter_by(
            user_id=user_id,
            lab_id=lab_id
        ).first()
        
        if existing:
            # Aggiorna il ruolo esistente
            existing.role_id = role.id
            existing.updated_at = datetime.utcnow()
            existing.assigned_at = datetime.utcnow()
        else:
            # Crea nuovo ruolo
            user_lab_role = UserLabRole(
                user_id=user_id,
                lab_id=lab_id,
                role_id=role.id,
                assigned_at=datetime.utcnow()
            )
            db.session.add(user_lab_role)
        
        try:
            db.session.commit()
            current_app.logger.info(f"Assegnato ruolo {role_name} a utente {user.email} per lab {lab.code}")
        except IntegrityError:
            db.session.rollback()
            raise RoleManagementError("Errore nell'assegnazione del ruolo")
    
    @staticmethod
    def change_lab_role(user_id, lab_id, new_role_name):
        """Cambia il ruolo di un utente in un laboratorio"""
        # Verifica che non sia l'ultimo owner
        if new_role_name != "owner_lab":
            RoleService._ensure_not_last_owner(user_id, lab_id)
        
        return RoleService.assign_lab_role(user_id, lab_id, new_role_name)
    
    @staticmethod
    def remove_lab_role(user_id, lab_id):
        """Rimuove un utente da un laboratorio"""
        # Verifica che non sia l'ultimo owner
        RoleService._ensure_not_last_owner(user_id, lab_id)
        
        user_lab_role = UserLabRole.query.filter_by(
            user_id=user_id,
            lab_id=lab_id
        ).first()
        
        if not user_lab_role:
            raise RoleManagementError("Utente non associato al laboratorio")
        
        user = User.query.get(user_id)
        lab = Lab.query.get(lab_id)
        
        db.session.delete(user_lab_role)
        db.session.commit()
        
        current_app.logger.info(f"Rimosso utente {user.email} dal lab {lab.code}")
    
    @staticmethod
    def _ensure_not_last_owner(user_id, lab_id):
        """Verifica che l'utente non sia l'ultimo owner del laboratorio"""
        owner_role = Role.query.filter_by(name="owner_lab").first()
        if not owner_role:
            return  # Se non esiste il ruolo owner, non può essere l'ultimo
        
        user_role = UserLabRole.query.filter_by(
            user_id=user_id,
            lab_id=lab_id,
            role_id=owner_role.id
        ).first()
        
        if user_role:  # L'utente è un owner
            # Conta quanti owner ci sono per questo lab
            owners_count = UserLabRole.query.filter_by(
                lab_id=lab_id,
                role_id=owner_role.id
            ).count()
            
            if owners_count <= 1:
                lab = Lab.query.get(lab_id)
                raise RoleManagementError(f"Impossibile rimuovere l'ultimo owner del laboratorio {lab.name}")
    
    @staticmethod
    def ensure_at_least_one_owner(lab_id):
        """Verifica che il laboratorio abbia almeno un owner"""
        owner_role = Role.query.filter_by(name="owner_lab").first()
        if not owner_role:
            raise RoleManagementError("Ruolo owner_lab non trovato")
        
        owners_count = UserLabRole.query.filter_by(
            lab_id=lab_id,
            role_id=owner_role.id
        ).count()
        
        if owners_count == 0:
            lab = Lab.query.get(lab_id)
            raise RoleManagementError(f"Il laboratorio {lab.name} deve avere almeno un owner")
        
        return True
    
    @staticmethod
    def make_admin(user_id):
        """Rende un utente amministratore"""
        user = User.query.get_or_404(user_id)
        
        # Implementiamo usando un campo is_admin o un ruolo globale
        # Per ora aggiungiamo un campo is_admin al modello User
        if not hasattr(user, 'is_admin'):
            # Se non esiste il campo, usiamo la logica email-based temporanea
            # In una migrazione futura dovremmo aggiungere il campo is_admin
            current_app.logger.warning(f"Campo is_admin non trovato, usando logica email-based per {user.email}")
            return
        
        user.is_admin = True
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"Utente {user.email} promosso ad admin")
    
    @staticmethod
    def remove_admin(user_id):
        """Rimuove privilegi admin da un utente"""
        user = User.query.get_or_404(user_id)
        
        # Verifica che non sia l'ultimo admin
        RoleService._ensure_not_last_admin(user_id)
        
        if not hasattr(user, 'is_admin'):
            current_app.logger.warning(f"Campo is_admin non trovato per {user.email}")
            return
        
        user.is_admin = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        current_app.logger.info(f"Rimossi privilegi admin da {user.email}")
    
    @staticmethod
    def _ensure_not_last_admin(user_id):
        """Verifica che l'utente non sia l'ultimo admin del sistema"""
        # Per ora usiamo la logica email-based
        admin_users = User.query.filter(User.email.like('admin%')).all()
        
        if len(admin_users) <= 1:
            user = User.query.get(user_id)
            if user and user.email.startswith('admin'):
                raise RoleManagementError("Impossibile rimuovere l'ultimo amministratore del sistema")
    
    @staticmethod
    def get_users_for_lab(lab_id):
        """Ottieni tutti gli utenti associati a un laboratorio con i loro ruoli"""
        return db.session.query(User, Role).join(
            UserLabRole, User.id == UserLabRole.user_id
        ).join(
            Role, UserLabRole.role_id == Role.id
        ).filter(
            UserLabRole.lab_id == lab_id
        ).all()
    
    @staticmethod
    def get_labs_for_user(user_id):
        """Ottieni tutti i laboratori a cui un utente è associato con i suoi ruoli"""
        return db.session.query(Lab, Role).join(
            UserLabRole, Lab.id == UserLabRole.lab_id
        ).join(
            Role, UserLabRole.role_id == Role.id
        ).filter(
            UserLabRole.user_id == user_id
        ).all()
    
    @staticmethod
    def has_lab_min_role(user, lab_code, min_role):
        """Verifica se un utente ha almeno il ruolo minimo per un laboratorio"""
        if user.has_role("admin"):
            return True
        
        min_level = RoleService.ROLE_HIERARCHY.get(min_role, 0)
        
        for lab_role in user.lab_roles:
            if (lab_role.lab.code == lab_code and 
                RoleService.ROLE_HIERARCHY.get(lab_role.role.name, 0) >= min_level):
                return True
        
        return False
    
    @staticmethod
    def add_existing_user_to_lab(email, lab_id, role_name):
        """Aggiungi un utente esistente a un laboratorio"""
        user = User.query.filter_by(email=email).first()
        if not user:
            raise RoleManagementError(f"Utente con email {email} non trovato")
        
        # Verifica che non sia già nel laboratorio
        existing = UserLabRole.query.filter_by(
            user_id=user.id,
            lab_id=lab_id
        ).first()
        
        if existing:
            raise RoleManagementError(f"Utente {email} già associato al laboratorio")
        
        RoleService.assign_lab_role(user.id, lab_id, role_name)
        return user