#!/usr/bin/env python3
"""
Script di seed data per OCHEM - Schema attuale
Popola le tabelle esistenti: Lab, Parametro, Analisi
"""

import sys
from pathlib import Path
import random

from faker import Faker
from dotenv import load_dotenv

# Aggiungi la directory root al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Inizializza Faker
fake = Faker('it_IT')

def create_app():
    """Crea l'app Flask per il seed"""
    from app import create_app
    return create_app()

def seed_labs(app):
    """Popola tabella Lab"""
    with app.app_context():
        from app.models import Lab
        from app import db
        
        labs_data = [
            ('LAB_ALPHA', 'Laboratorio Alpha'),
            ('LAB_BETA', 'Laboratorio Beta'),
            ('LAB_GAMMA', 'Laboratorio Gamma'),
            ('LAB_DELTA', 'Laboratorio Delta'),
            ('LAB_EPSILON', 'Laboratorio Epsilon')
        ]
        
        labs_created = 0
        for code, name in labs_data:
            if not Lab.query.filter_by(code=code).first():
                lab = Lab(code=code, name=name)
                db.session.add(lab)
                labs_created += 1
        
        db.session.commit()
        print(f"✅ Creati {labs_created} laboratori")
        return labs_created

def seed_parametri(app):
    """Popola tabella Parametro"""
    with app.app_context():
        from app.models import Parametro
        from app import db
        
        parametri_data = [
            ('NH4', 'Azoto ammoniacale', 'mg/L'),
            ('NO3', 'Azoto nitrico', 'mg/L'),
            ('NO2', 'Azoto nitroso', 'mg/L'),
            ('TOC', 'Carbonio organico totale', 'mg/L'),
            ('COD', 'Domanda chimica di ossigeno', 'mg/L'),
            ('BOD5', 'Domanda biochimica di ossigeno', 'mg/L'),
            ('PO4', 'Fosfati', 'mg/L'),
            ('SO4', 'Solfati', 'mg/L'),
            ('CL', 'Cloruri', 'mg/L'),
            ('COND', 'Conducibilità', 'µS/cm'),
            ('PH', 'pH', 'pH'),
            ('TURB', 'Torbidità', 'NTU'),
            ('TSS', 'Solidi sospesi totali', 'mg/L'),
            ('TDS', 'Solidi disciolti totali', 'mg/L'),
            ('ALK', 'Alcalinità', 'mg/L CaCO3')
        ]
        
        parametri_created = 0
        for codice, nome, unita in parametri_data:
            if not Parametro.query.filter_by(codice=codice).first():
                parametro = Parametro(codice=codice, nome=nome, unita=unita)
                db.session.add(parametro)
                parametri_created += 1
        
        db.session.commit()
        print(f"✅ Creati {parametri_created} parametri")
        return parametri_created

def seed_analisi(app, num_analisi=100):
    """Popola tabella Analisi con dati casuali"""
    with app.app_context():
        from app.models import Lab, Parametro, Analisi
        from app import db
        
        # Ottieni tutti i lab e parametri
        labs = Lab.query.all()
        parametri = Parametro.query.all()
        
        if not labs or not parametri:
            print("❌ Impossibile creare analisi: mancano lab o parametri")
            return 0
        
        tecniche = [
            'Spettrofotometria UV-VIS',
            'Cromatografia ionica',
            'Potenziometria',
            'Turbidimetria',
            'Conduttimetria',
            'Titolazione',
            'Spettroscopia ICP-MS',
            'Elettrodo selettivo'
        ]
        
        matrici = ['acqua', 'acque reflue', 'acque superficiali', 'acque sotterranee']
        
        # Genera valori realistici per parametro
        def get_realistic_value(parametro_codice, unita):
            """Genera valori realistici per tipo di parametro"""
            if parametro_codice in ['NH4', 'NO3', 'NO2']:
                return round(random.uniform(0.1, 10.0), 2)
            elif parametro_codice in ['TOC', 'COD', 'BOD5']:
                return round(random.uniform(1.0, 100.0), 1)
            elif parametro_codice in ['PO4', 'SO4', 'CL']:
                return round(random.uniform(0.5, 50.0), 2)
            elif parametro_codice == 'COND':
                return round(random.uniform(100, 2000), 0)
            elif parametro_codice == 'PH':
                return round(random.uniform(6.0, 8.5), 1)
            elif parametro_codice == 'TURB':
                return round(random.uniform(0.1, 20.0), 2)
            elif parametro_codice in ['TSS', 'TDS']:
                return round(random.uniform(5.0, 500.0), 1)
            elif parametro_codice == 'ALK':
                return round(random.uniform(50, 300), 1)
            else:
                return round(random.uniform(1.0, 50.0), 2)
        
        analisi_created = 0
        for _ in range(num_analisi):
            lab = random.choice(labs)
            parametro = random.choice(parametri)
            tecnica = random.choice(tecniche)
            matrice = random.choice(matrici)
            ciclo_n = random.randint(1, 3)
            
            valore = get_realistic_value(parametro.codice, parametro.unita)
            
            analisi = Analisi(
                lab_id=lab.id,
                parametro_id=parametro.id,
                tecnica=tecnica,
                valore=valore,
                unita=parametro.unita,
                ciclo_n=ciclo_n,
                matrice=matrice,
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
            
            db.session.add(analisi)
            analisi_created += 1
        
        db.session.commit()
        print(f"✅ Create {analisi_created} analisi")
        return analisi_created

def print_summary(app):
    """Stampa riepilogo del database"""
    with app.app_context():
        from app.models import Lab, Parametro, Analisi
        
        labs_count = Lab.query.count()
        parametri_count = Parametro.query.count()
        analisi_count = Analisi.query.count()
        
        print("\n" + "="*50)
        print("📊 RIEPILOGO DATABASE OCHEM")
        print("="*50)
        print(f"Laboratori................ {labs_count:>6}")
        print(f"Parametri................. {parametri_count:>6}")
        print(f"Analisi................... {analisi_count:>6}")
        print("="*50)
        
        # Mostra alcuni esempi
        if analisi_count > 0:
            print("\n📝 Ultime 5 analisi:")
            analisi_recenti = Analisi.query.order_by(Analisi.created_at.desc()).limit(5).all()
            for analisi in analisi_recenti:
                lab = Lab.query.get(analisi.lab_id)
                parametro = Parametro.query.get(analisi.parametro_id)
                print(f"  - {lab.code}: {parametro.codice} = {analisi.valore} {analisi.unita}")

def main():
    """Funzione principale"""
    print("🌱 Seed data per OCHEM - Schema attuale")
    print("=" * 50)
    
    # Carica variabili d'ambiente
    load_dotenv(root_dir / '.env')
    
    # Crea app Flask
    app = create_app()
    
    try:
        # 1. Popola laboratori
        labs_created = seed_labs(app)
        
        # 2. Popola parametri
        parametri_created = seed_parametri(app)
        
        # 3. Popola analisi
        analisi_created = seed_analisi(app, num_analisi=150)
        
        # 4. Riepilogo
        print_summary(app)
        
        print(f"\n🎉 Seed completato con successo!")
        print(f"   - {labs_created} laboratori aggiunti")
        print(f"   - {parametri_created} parametri aggiunti")
        print(f"   - {analisi_created} analisi create")
        
    except Exception as e:
        print(f"\n❌ Errore durante il seed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)