#!/usr/bin/env python3
"""
Script di popolamento database OCHEM secondo instruction_db.md
Implementa esattamente la struttura e i dati specificati nelle istruzioni
"""

import sys
from pathlib import Path
from datetime import datetime
import random

import pandas as pd
import numpy as np
from faker import Faker
from dotenv import load_dotenv

# Aggiungi la directory root al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Costante MAD per calcoli robusti
MAD_K = 1.4826

# Inizializza Faker
fake = Faker('it_IT')

def get_database_session():
    """Crea sessione database"""
    load_dotenv(root_dir / '.env')
    database_url = os.getenv('DATABASE_URL', 'sqlite:///instance/ochem.sqlite3')
    
    engine = sa.create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def seed_base_data(session):
    """Popola dati anagrafici base"""
    
    print("📝 Popolamento dati base...")
    
    # Unità di misura
    units_data = [
        ('mg/L', 'Milligrammi per litro'),
        ('µS/cm', 'Microsiemens per centimetro'),
        ('pH', 'Potenziale idrogeno'),
        ('µg/L', 'Microgrammi per litro'),
        ('NTU', 'Nephelometric Turbidity Units')
    ]
    
    units = []
    for code, description in units_data:
        unit_insert = sa.text("""
            INSERT OR IGNORE INTO unit (code, description, created_at, updated_at) 
            VALUES (:code, :description, :created_at, :updated_at)
        """)
        session.execute(unit_insert, {
            'code': code,
            'description': description,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        units.append(code)
    
    # Parametri
    parameters_data = [
        ('NH4', 'Azoto ammoniacale', 'mg/L'),
        ('NO3', 'Azoto nitrico', 'mg/L'),
        ('TOC', 'Carbonio organico totale', 'mg/L'),
        ('COND', 'Conducibilità', 'µS/cm'),
        ('PH', 'pH', 'pH'),
    ]
    
    parameters = []
    for code, name, unit in parameters_data:
        param_insert = sa.text("""
            INSERT OR IGNORE INTO parameter (code, name, unit_code, created_at, updated_at)
            VALUES (:code, :name, :unit_code, :created_at, :updated_at)
        """)
        session.execute(param_insert, {
            'code': code,
            'name': name,
            'unit_code': unit,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        parameters.append(code)
    
    # Tecniche analitiche
    techniques_data = [
        ('POTENZ', 'Potenziometria'),
        ('SPETTRO', 'Spettrofotometria'),
        ('CROMATO', 'Cromatografia'),
        ('TITRIMETRIA', 'Analisi volumetrica')
    ]
    
    techniques = []
    for code, name in techniques_data:
        tech_insert = sa.text("""
            INSERT OR IGNORE INTO technique (code, name, created_at, updated_at)
            VALUES (:code, :name, :created_at, :updated_at)
        """)
        session.execute(tech_insert, {
            'code': code,
            'name': name,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        techniques.append(code)
    
    # Provider
    provider_insert = sa.text("""
        INSERT OR IGNORE INTO provider (code, name, created_at, updated_at)
        VALUES (:code, :name, :created_at, :updated_at)
    """)
    session.execute(provider_insert, {
        'code': 'UNICHIM',
        'name': 'Ente Nazionale Italiano di Unificazione',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })
    
    # Laboratori
    labs_data = [
        ('LAB_ALPHA', 'Laboratorio Alpha', 'Milano', 'lab.alpha@example.com'),
        ('LAB_BETA', 'Laboratorio Beta', 'Roma', 'lab.beta@example.com'),
        ('LAB_GAMMA', 'Laboratorio Gamma', 'Napoli', 'lab.gamma@example.com')
    ]
    
    labs = []
    for code, name, city, email in labs_data:
        lab_insert = sa.text("""
            INSERT OR IGNORE INTO lab (code, name, city, contact_email, created_at, updated_at)
            VALUES (:code, :name, :city, :email, :created_at, :updated_at)
        """)
        session.execute(lab_insert, {
            'code': code,
            'name': name,
            'city': city,
            'email': email,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        labs.append(code)
    
    session.commit()
    print(f"✅ Creati: {len(units)} unità, {len(parameters)} parametri, {len(techniques)} tecniche, {len(labs)} laboratori")
    
    return {
        'units': units,
        'parameters': parameters,
        'techniques': techniques,
        'labs': labs
    }

def seed_cycles_and_docs(session, base_data):
    """Crea cicli PT e documenti associati"""
    
    print("📋 Creazione cicli PT...")
    
    # Crea documento di esempio
    doc_insert = sa.text("""
        INSERT OR IGNORE INTO doc_file (filename, original_filename, file_size, mime_type, uploaded_at)
        VALUES (:filename, :original_filename, :file_size, :mime_type, :uploaded_at)
    """)
    
    session.execute(doc_insert, {
        'filename': 'ciclo_2025_01.pdf',
        'original_filename': 'Ciclo PT 2025-01.pdf',
        'file_size': 1024000,
        'mime_type': 'application/pdf',
        'uploaded_at': datetime.utcnow()
    })
    
    # Ottieni l'ID del documento
    doc_result = session.execute(sa.text("SELECT id FROM doc_file WHERE filename = :filename"), 
                                {'filename': 'ciclo_2025_01.pdf'}).fetchone()
    doc_id = doc_result[0] if doc_result else None
    
    # Cicli PT
    cycles_data = [
        ('2025-01', 'Ciclo PT Gennaio 2025', 'published', doc_id, datetime(2025, 1, 15), datetime(2025, 2, 15)),
        ('2025-02', 'Ciclo PT Febbraio 2025', 'draft', None, datetime(2025, 2, 15), datetime(2025, 3, 15))
    ]
    
    cycles = []
    for code, name, status, doc_id, start_date, end_date in cycles_data:
        cycle_insert = sa.text("""
            INSERT OR IGNORE INTO cycle (code, name, status, doc_id, start_date, end_date, created_at, updated_at)
            VALUES (:code, :name, :status, :doc_id, :start_date, :end_date, :created_at, :updated_at)
        """)
        
        session.execute(cycle_insert, {
            'code': code,
            'name': name,
            'status': status,
            'doc_id': doc_id,
            'start_date': start_date,
            'end_date': end_date,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        cycles.append(code)
    
    # Associa parametri ai cicli con valori XPT e SigmaPT
    cycle_params = []
    for cycle_code in cycles:
        for param_code in base_data['parameters'][:3]:  # Prime 3 parametri
            xpt = round(random.uniform(1.0, 50.0), 3)
            sigma_pt = round(random.uniform(0.1, 5.0), 3)
            
            cycle_param_insert = sa.text("""
                INSERT OR IGNORE INTO cycle_parameter (cycle_code, parameter_code, xpt, sigma_pt, created_at, updated_at)
                VALUES (:cycle_code, :parameter_code, :xpt, :sigma_pt, :created_at, :updated_at)
            """)
            
            session.execute(cycle_param_insert, {
                'cycle_code': cycle_code,
                'parameter_code': param_code,
                'xpt': xpt,
                'sigma_pt': sigma_pt,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            
            cycle_params.append((cycle_code, param_code, xpt, sigma_pt))
    
    session.commit()
    print(f"✅ Creati: {len(cycles)} cicli con {len(cycle_params)} parametri associati")
    
    return cycles, cycle_params

def seed_users_and_participations(session, base_data, cycles):
    """Crea utenti e partecipazioni ai cicli"""
    
    print("👥 Creazione utenti e partecipazioni...")
    
    # Utenti (owner dei laboratori)
    users_data = [
        ('user1@alpha.com', 'Mario', 'Rossi', 'LAB_ALPHA'),
        ('user2@beta.com', 'Luigi', 'Bianchi', 'LAB_BETA'),
        ('user3@gamma.com', 'Paolo', 'Verdi', 'LAB_GAMMA')
    ]
    
    for email, first_name, last_name, lab_code in users_data:
        user_insert = sa.text("""
            INSERT OR IGNORE INTO user (email, first_name, last_name, accepted_disclaimer_at, created_at, updated_at)
            VALUES (:email, :first_name, :last_name, :accepted_disclaimer_at, :created_at, :updated_at)
        """)
        
        session.execute(user_insert, {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'accepted_disclaimer_at': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    
    # Partecipazioni ai cicli (solo ciclo pubblicato)
    participations = []
    for lab_code in base_data['labs']:
        participation_insert = sa.text("""
            INSERT OR IGNORE INTO lab_participation (lab_code, cycle_code, status, created_at, updated_at)
            VALUES (:lab_code, :cycle_code, :status, :created_at, :updated_at)
        """)
        
        session.execute(participation_insert, {
            'lab_code': lab_code,
            'cycle_code': '2025-01',  # Solo ciclo pubblicato
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        participations.append((lab_code, '2025-01'))
    
    session.commit()
    print(f"✅ Creati: {len(users_data)} utenti e {len(participations)} partecipazioni")
    
    return participations

def seed_results_and_calculate_stats(session, base_data, cycle_params, participations):
    """Genera risultati casuali e calcola statistiche PT"""
    
    print("🧪 Generazione risultati e calcolo statistiche...")
    
    results_data = []
    
    # Genera risultati per ogni combinazione lab-ciclo-parametro
    result_id = 1
    for lab_code, cycle_code in participations:
        for param_tuple in cycle_params:
            if param_tuple[0] == cycle_code:  # Stesso ciclo
                cycle_c, param_code, xpt, sigma_pt = param_tuple
                
                # Genera 10-15 risultati per combinazione
                num_results = random.randint(10, 15)
                
                for i in range(num_results):
                    # Valore casuale attorno a XPT con deviazione realistica
                    noise = random.gauss(0, sigma_pt * 0.8)
                    measured_value = round(xpt + noise, 3)
                    
                    # Tecnica casuale
                    technique_code = random.choice(base_data['techniques'])
                    
                    result_insert = sa.text("""
                        INSERT INTO result (
                            id, lab_code, cycle_code, parameter_code, technique_code,
                            measured_value, created_at, updated_at
                        ) VALUES (
                            :id, :lab_code, :cycle_code, :parameter_code, :technique_code,
                            :measured_value, :created_at, :updated_at
                        )
                    """)
                    
                    session.execute(result_insert, {
                        'id': result_id,
                        'lab_code': lab_code,
                        'cycle_code': cycle_code,
                        'parameter_code': param_code,
                        'technique_code': technique_code,
                        'measured_value': measured_value,
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    })
                    
                    results_data.append({
                        'result_id': result_id,
                        'lab_code': lab_code,
                        'cycle_code': cycle_code,
                        'parameter_code': param_code,
                        'measured_value': measured_value,
                        'xpt': xpt,
                        'sigma_pt': sigma_pt
                    })
                    
                    result_id += 1
    
    session.commit()
    
    # Calcola statistiche usando pandas
    df = pd.DataFrame(results_data)
    
    z_scores = []
    pt_stats = []
    
    # Calcola Z-score per ogni risultato
    for _, row in df.iterrows():
        z = (row['measured_value'] - row['xpt']) / row['sigma_pt']
        sz2 = z ** 2
        
        z_score_insert = sa.text("""
            INSERT INTO z_score (result_id, z, sz2, created_at, updated_at)
            VALUES (:result_id, :z, :sz2, :created_at, :updated_at)
        """)
        
        session.execute(z_score_insert, {
            'result_id': row['result_id'],
            'z': round(z, 4),
            'sz2': round(sz2, 4),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        z_scores.append(z)
    
    # Calcola statistiche PT per ogni gruppo (ciclo, parametro, laboratorio)
    for (cycle_code, param_code, lab_code), group in df.groupby(['cycle_code', 'parameter_code', 'lab_code']):
        z_values = [(row['measured_value'] - row['xpt']) / row['sigma_pt'] for _, row in group.iterrows()]
        z_array = np.array(z_values)
        
        # Calcola RSZ usando metodo robusto (MAD)
        rsz = MAD_K * np.median(np.abs(z_array - np.median(z_array)))
        
        pt_stat_insert = sa.text("""
            INSERT INTO pt_stats (
                cycle_code, parameter_code, lab_code, n_results, mean_z, rsz, 
                created_at, updated_at
            ) VALUES (
                :cycle_code, :parameter_code, :lab_code, :n_results, :mean_z, :rsz,
                :created_at, :updated_at
            )
        """)
        
        session.execute(pt_stat_insert, {
            'cycle_code': cycle_code,
            'parameter_code': param_code,
            'lab_code': lab_code,
            'n_results': len(group),
            'mean_z': round(np.mean(z_array), 4),
            'rsz': round(rsz, 4),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        pt_stats.append({
            'cycle_code': cycle_code,
            'parameter_code': param_code,
            'lab_code': lab_code,
            'n_results': len(group),
            'rsz': rsz
        })
    
    session.commit()
    print(f"✅ Creati: {len(results_data)} risultati, {len(z_scores)} z-score, {len(pt_stats)} statistiche PT")
    
    return len(results_data), len(z_scores), len(pt_stats)

def seed_control_charts(session):
    """Crea configurazioni per carte di controllo"""
    
    print("📊 Configurazione carte di controllo...")
    
    # Configurazione standard per carte di controllo Z-score
    control_config = sa.text("""
        INSERT OR IGNORE INTO control_chart_config (
            name, chart_type, center_line, upper_control_limit, lower_control_limit,
            upper_warning_limit, lower_warning_limit, created_at, updated_at
        ) VALUES (
            :name, :chart_type, :cl, :ucl, :lcl, :uwl, :lwl, :created_at, :updated_at
        )
    """)
    
    session.execute(control_config, {
        'name': 'Z-Score Standard',
        'chart_type': 'z_score',
        'cl': 0.0,
        'ucl': 3.0,
        'lcl': -3.0,
        'uwl': 2.0,
        'lwl': -2.0,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })
    
    session.commit()
    print("✅ Configurazione carte di controllo creata")

def print_summary(session):
    """Stampa riepilogo finale del database"""
    
    print("\n" + "="*60)
    print("📊 RIEPILOGO DATABASE OCHEM")
    print("="*60)
    
    # Conta record nelle tabelle principali
    queries = [
        ("Cicli pubblicati", "SELECT COUNT(*) FROM cycle WHERE status = 'published'"),
        ("Laboratori", "SELECT COUNT(*) FROM lab"),
        ("Parametri", "SELECT COUNT(*) FROM parameter"),
        ("Risultati", "SELECT COUNT(*) FROM result"),
        ("Z-score calcolati", "SELECT COUNT(*) FROM z_score"),
        ("Statistiche PT", "SELECT COUNT(*) FROM pt_stats")
    ]
    
    for description, query in queries:
        try:
            result = session.execute(sa.text(query)).fetchone()
            count = result[0] if result else 0
            print(f"{description:.<30} {count:>6}")
        except Exception as e:
            print(f"{description:.<30} ERROR: {e}")
    
    print("="*60)

def main():
    """Funzione principale"""
    
    print("🌱 Popolamento database OCHEM con dati di test")
    print("=" * 60)
    
    # Crea sessione database
    session, engine = get_database_session()
    
    try:
        # 1. Dati anagrafici base
        base_data = seed_base_data(session)
        
        # 2. Cicli e documenti
        cycles, cycle_params = seed_cycles_and_docs(session, base_data)
        
        # 3. Utenti e partecipazioni
        participations = seed_users_and_participations(session, base_data, cycles)
        
        # 4. Risultati e statistiche
        n_results, n_zscores, n_stats = seed_results_and_calculate_stats(
            session, base_data, cycle_params, participations
        )
        
        # 5. Carte di controllo
        seed_control_charts(session)
        
        # 6. Riepilogo finale
        print_summary(session)
        
        print("\n🎉 Popolamento database completato con successo!")
        
    except Exception as e:
        print(f"\n❌ Errore durante il popolamento: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()