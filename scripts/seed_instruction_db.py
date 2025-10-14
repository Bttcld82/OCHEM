#!/usr/bin/env python3
"""
Script di popolamento database OCHEM secondo instruction_db.md
Implementa esattamente la struttura e i dati specificati nelle istruzioni
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
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

def create_app():
    """Crea l'app Flask per il seed"""
    from app import create_app
    return create_app()

def seed_base_data(app):
    """Popola dati anagrafici base secondo instruction_db.md"""
    with app.app_context():
        from app.models import Unit, Parameter, Technique, Provider, Lab
        from app import db
        
        print("📝 Popolamento dati anagrafici base...")
        
        # 1. UNIT - Unità di misura
        units_data = [
            ('mg/L', 'Milligrammi per litro'),
            ('µS/cm', 'Microsiemens per centimetro'), 
            ('pH', 'Potenziale idrogeno'),
            ('µg/L', 'Microgrammi per litro'),
            ('NTU', 'Nephelometric Turbidity Units'),
            ('mg/L_CaCO3', 'Milligrammi per litro come CaCO3')
        ]
        
        units_created = 0
        for code, description in units_data:
            if not Unit.query.filter_by(code=code).first():
                unit = Unit(code=code, description=description)
                db.session.add(unit)
                units_created += 1
        
        # 2. PARAMETER - Parametri chimici
        parameters_data = [
            ('NH4', 'Azoto ammoniacale', 'mg/L'),
            ('NO3', 'Azoto nitrico', 'mg/L'), 
            ('TOC', 'Carbonio organico totale', 'mg/L'),
            ('PO4', 'Fosfati', 'mg/L'),
            ('COND', 'Conducibilità', 'µS/cm'),
            ('PH', 'pH', 'pH')
        ]
        
        parameters_created = 0
        for code, name, unit_code in parameters_data:
            if not Parameter.query.filter_by(code=code).first():
                parameter = Parameter(code=code, name=name, unit_code=unit_code)
                db.session.add(parameter)
                parameters_created += 1
        
        # 3. TECHNIQUE - Tecniche analitiche
        techniques_data = [
            ('POTENZ', 'Potenziometria'),
            ('SPETTRO', 'Spettrofotometria'),
            ('CROMATO', 'Cromatografia ionica'),
            ('TITRIM', 'Titolazione')
        ]
        
        techniques_created = 0
        for code, name in techniques_data:
            if not Technique.query.filter_by(code=code).first():
                technique = Technique(code=code, name=name)
                db.session.add(technique)
                techniques_created += 1
        
        # 4. PROVIDER
        if not Provider.query.filter_by(code='UNICHIM').first():
            provider = Provider(code='UNICHIM', name='Ente Nazionale Italiano di Unificazione')
            db.session.add(provider)
            providers_created = 1
        else:
            providers_created = 0
        
        # 5. LAB - Laboratori
        labs_data = [
            ('LAB_ALPHA', 'Laboratorio Alpha', 'Milano', 'alpha@lab.it'),
            ('LAB_BETA', 'Laboratorio Beta', 'Roma', 'beta@lab.it')
        ]
        
        labs_created = 0
        for code, name, city, email in labs_data:
            if not Lab.query.filter_by(code=code).first():
                lab = Lab(code=code, name=name, city=city, contact_email=email)
                db.session.add(lab)
                labs_created += 1
        
        db.session.commit()
        print(f"✅ Creati: {units_created} unità, {parameters_created} parametri, {techniques_created} tecniche, {providers_created} provider, {labs_created} laboratori")
        
        return {
            'units': units_created,
            'parameters': parameters_created, 
            'techniques': techniques_created,
            'providers': providers_created,
            'labs': labs_created
        }

def seed_cycles_and_docs(app):
    """Crea cicli PT e documenti secondo instruction_db.md"""
    with app.app_context():
        from app.models import DocFile, Cycle, CycleParameter, Parameter
        from app import db
        
        print("📋 Creazione cicli PT...")
        
        # 1. DOC_FILE - Documento di esempio
        doc_created = 0
        if not DocFile.query.filter_by(filename='ciclo_2025_01.pdf').first():
            doc = DocFile(
                filename='ciclo_2025_01.pdf',
                original_filename='Ciclo PT 2025-01.pdf',
                file_size=1024000,
                mime_type='application/pdf'
            )
            db.session.add(doc)
            db.session.flush()  # Per ottenere l'ID
            doc_id = doc.id
            doc_created = 1
        else:
            doc_id = DocFile.query.filter_by(filename='ciclo_2025_01.pdf').first().id
        
        # 2. CYCLE - Cicli PT
        cycles_data = [
            ('2025-01', 'Ciclo PT Gennaio 2025', 'published', doc_id, datetime(2025, 1, 15), datetime(2025, 2, 15)),
            ('2025-02', 'Ciclo PT Febbraio 2025', 'draft', None, datetime(2025, 2, 15), datetime(2025, 3, 15))
        ]
        
        cycles_created = 0
        for code, name, status, doc_id, start_date, end_date in cycles_data:
            if not Cycle.query.filter_by(code=code).first():
                cycle = Cycle(
                    code=code,
                    name=name, 
                    status=status,
                    doc_id=doc_id,
                    start_date=start_date,
                    end_date=end_date
                )
                db.session.add(cycle)
                cycles_created += 1
        
        # 3. CYCLE_PARAMETER - Parametri per cicli con XPT e SigmaPT
        cycle_params_created = 0
        parameters = Parameter.query.limit(3).all()  # Prime 3 parametri
        
        for cycle_code in ['2025-01', '2025-02']:
            for param in parameters:
                if not CycleParameter.query.filter_by(cycle_code=cycle_code, parameter_code=param.code).first():
                    # Valori XPT e SigmaPT casuali ma realistici
                    if param.code == 'NH4':
                        xpt, sigma_pt = 2.5, 0.3
                    elif param.code == 'NO3':
                        xpt, sigma_pt = 15.0, 1.5
                    elif param.code == 'TOC':
                        xpt, sigma_pt = 12.0, 1.2
                    else:
                        xpt = round(random.uniform(1.0, 50.0), 2)
                        sigma_pt = round(xpt * 0.1, 2)  # 10% del valore
                    
                    cycle_param = CycleParameter(
                        cycle_code=cycle_code,
                        parameter_code=param.code,
                        xpt=xpt,
                        sigma_pt=sigma_pt
                    )
                    db.session.add(cycle_param)
                    cycle_params_created += 1
        
        db.session.commit()
        print(f"✅ Creati: {doc_created} documenti, {cycles_created} cicli, {cycle_params_created} parametri ciclo")
        
        return cycles_created, cycle_params_created

def seed_users_and_participations(app):
    """Crea utenti e partecipazioni secondo instruction_db.md"""
    with app.app_context():
        from app.models import User, LabParticipation, Lab
        from app import db
        
        print("👥 Creazione utenti e partecipazioni...")
        
        # 1. USER - 2 owner con accepted_disclaimer_at
        users_data = [
            ('mario.rossi@alpha.it', 'Mario', 'Rossi'),
            ('luigi.bianchi@beta.it', 'Luigi', 'Bianchi')
        ]
        
        users_created = 0
        for email, first_name, last_name in users_data:
            if not User.query.filter_by(email=email).first():
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    accepted_disclaimer_at=datetime.utcnow()
                )
                db.session.add(user)
                users_created += 1
        
        # 2. LAB_PARTICIPATION - Ogni lab nel ciclo 2025-01
        labs = Lab.query.all()
        participations_created = 0
        
        for lab in labs:
            if not LabParticipation.query.filter_by(lab_code=lab.code, cycle_code='2025-01').first():
                participation = LabParticipation(
                    lab_code=lab.code,
                    cycle_code='2025-01',
                    status='active'
                )
                db.session.add(participation)
                participations_created += 1
        
        db.session.commit()
        print(f"✅ Creati: {users_created} utenti, {participations_created} partecipazioni")
        
        return users_created, participations_created

def seed_results_and_calculate_stats(app, num_results=100):
    """Genera risultati e calcola statistiche secondo instruction_db.md"""
    with app.app_context():
        from app.models import Lab, Parameter, Technique, CycleParameter, Result, ZScore, PtStats
        from app import db
        
        print("🧪 Generazione risultati e calcolo statistiche...")
        
        # Ottieni dati necessari
        labs = Lab.query.all()
        cycle_params = CycleParameter.query.filter_by(cycle_code='2025-01').all()
        techniques = Technique.query.all()
        
        results_data = []
        results_created = 0
        
        # Genera risultati per ogni combinazione lab-parametro
        for lab in labs:
            for cycle_param in cycle_params:
                # 10-15 risultati per combinazione
                n_results = random.randint(10, 15)
                
                for _ in range(n_results):
                    # Valore casuale attorno a XPT con rumore realistico
                    noise = random.gauss(0, float(cycle_param.sigma_pt) * 0.8)
                    measured_value = float(cycle_param.xpt) + noise
                    
                    technique = random.choice(techniques)
                    
                    result = Result(
                        lab_code=lab.code,
                        cycle_code=cycle_param.cycle_code,
                        parameter_code=cycle_param.parameter_code,
                        technique_code=technique.code,
                        measured_value=round(measured_value, 4)
                    )
                    
                    db.session.add(result)
                    db.session.flush()  # Per ottenere l'ID
                    
                    # Calcola Z-score: z = (x - xpt) / sigma_pt
                    z = (measured_value - float(cycle_param.xpt)) / float(cycle_param.sigma_pt)
                    sz2 = z ** 2
                    
                    z_score = ZScore(
                        result_id=result.id,
                        z=round(z, 4),
                        sz2=round(sz2, 4)
                    )
                    db.session.add(z_score)
                    
                    results_data.append({
                        'lab_code': lab.code,
                        'parameter_code': cycle_param.parameter_code,
                        'z': z
                    })
                    
                    results_created += 1
        
        db.session.commit()
        
        # Calcola PT_STATS usando pandas per calcoli robusti
        print("📊 Calcolo statistiche PT...")
        
        df = pd.DataFrame(results_data)
        stats_created = 0
        
        for (lab_code, param_code), group in df.groupby(['lab_code', 'parameter_code']):
            z_values = group['z'].values
            
            # Calcola RSZ usando metodo robusto (MAD)
            rsz = MAD_K * np.median(np.abs(z_values - np.median(z_values)))
            
            pt_stat = PtStats(
                cycle_code='2025-01',
                parameter_code=param_code,
                lab_code=lab_code,
                n_results=len(group),
                mean_z=round(np.mean(z_values), 4),
                rsz=round(rsz, 4)
            )
            db.session.add(pt_stat)
            stats_created += 1
        
        db.session.commit()
        print(f"✅ Creati: {results_created} risultati, {results_created} z-score, {stats_created} statistiche PT")
        
        return results_created, stats_created

def seed_control_charts(app):
    """Crea configurazioni carte di controllo secondo instruction_db.md"""
    with app.app_context():
        from app.models import ControlChartConfig
        from app import db
        
        print("📊 Configurazione carte di controllo...")
        
        # CL=0, UCL=±3, LCL=±3 come specificato
        if not ControlChartConfig.query.filter_by(name='Z-Score Standard').first():
            config = ControlChartConfig(
                name='Z-Score Standard',
                chart_type='z_score',
                center_line=0.0,
                upper_control_limit=3.0,
                lower_control_limit=-3.0,
                upper_warning_limit=2.0,
                lower_warning_limit=-2.0
            )
            db.session.add(config)
            db.session.commit()
            print("✅ Configurazione carte di controllo creata")
            return 1
        else:
            print("✅ Configurazione carte di controllo già esistente")
            return 0

def print_summary(app):
    """Stampa riepilogo secondo instruction_db.md"""
    with app.app_context():
        from app.models import Cycle, Lab, Result, ZScore, PtStats
        
        print("\n" + "="*60)
        print("📊 RIEPILOGO DATABASE OCHEM (secondo instruction_db.md)")
        print("="*60)
        
        cycles_published = Cycle.query.filter_by(status='published').count()
        labs_count = Lab.query.count()
        results_count = Result.query.count()
        zscores_count = ZScore.query.count()
        stats_count = PtStats.query.count()
        
        print(f"Cicli pubblicati........... {cycles_published:>6}")
        print(f"Laboratori................ {labs_count:>6}")
        print(f"Risultati................. {results_count:>6}")
        print(f"Z-score calcolati......... {zscores_count:>6}")
        print(f"Statistiche PT............ {stats_count:>6}")
        
        print("="*60)
        
        # Verifica criteri di successo dalle istruzioni
        success = True
        if cycles_published < 1:
            print("❌ Manca almeno 1 ciclo pubblicato")
            success = False
        if labs_count < 2:
            print("❌ Mancano almeno 2 laboratori") 
            success = False
        if results_count < 100:
            print("❌ Mancano almeno 100 risultati")
            success = False
        if zscores_count != results_count:
            print("❌ Numero z-score diverso da numero risultati")
            success = False
            
        if success:
            print("✅ Tutti i criteri di successo soddisfatti!")

def main():
    """Funzione principale secondo instruction_db.md"""
    print("🌱 Popolamento database OCHEM secondo instruction_db.md")
    print("=" * 70)
    
    # Carica variabili d'ambiente
    load_dotenv(root_dir / '.env')
    
    # Crea app Flask
    app = create_app()
    
    try:
        # 1. Dati anagrafici base
        base_counts = seed_base_data(app)
        
        # 2. Cicli e documenti
        cycles_count, cycle_params_count = seed_cycles_and_docs(app)
        
        # 3. Utenti e partecipazioni 
        users_count, participations_count = seed_users_and_participations(app)
        
        # 4. Risultati e statistiche (almeno 100 risultati)
        results_count, stats_count = seed_results_and_calculate_stats(app, num_results=100)
        
        # 5. Carte di controllo
        charts_count = seed_control_charts(app)
        
        # 6. Riepilogo finale
        print_summary(app)
        
        print("\n🎉 Popolamento completato secondo instruction_db.md!")
        
    except Exception as e:
        print(f"\n❌ Errore durante il popolamento: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)