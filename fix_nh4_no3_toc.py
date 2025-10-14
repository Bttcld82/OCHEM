"""
Script per migliorare i dati NH4, NO3, TOC
- Assegna provider ai cicli esistenti
- Distribuisce le date dei risultati nel tempo
"""
import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Provider, Cycle, Result
from datetime import datetime, timedelta
import random

def update_nh4_no3_toc_data():
    """Aggiorna i dati per NH4, NO3, TOC"""
    
    app = create_app()
    
    with app.app_context():
        print("🔄 Aggiornamento dati NH4, NO3, TOC...")
        
        # 1. Assegna provider ai cicli esistenti
        print("\n📋 Assegnazione provider ai cicli...")
        
        aquatest_provider = Provider.query.filter_by(code='AQUATEST_INT').first()
        ecolab_provider = Provider.query.filter_by(code='ECOLAB_NORD').first()
        
        if aquatest_provider and ecolab_provider:
            # Ciclo 2025-01 -> AquaTest (specializzato in analisi acque)
            cycle_2025_01 = Cycle.query.filter_by(code='2025-01').first()
            if cycle_2025_01:
                cycle_2025_01.provider_id = aquatest_provider.id
                print(f"✅ Ciclo 2025-01 assegnato a {aquatest_provider.name}")
            
            # Ciclo 2025-02 -> EcoLab
            cycle_2025_02 = Cycle.query.filter_by(code='2025-02').first() 
            if cycle_2025_02:
                cycle_2025_02.provider_id = ecolab_provider.id
                print(f"✅ Ciclo 2025-02 assegnato a {ecolab_provider.name}")
        
        # 2. Distribuisci le date dei risultati NH4, NO3, TOC
        print("\n📅 Distribuzione temporale dei risultati...")
        
        # Definisci finestre temporali per ogni parametro
        base_date = datetime(2025, 1, 15)  # Data base: metà gennaio
        
        parameters_config = {
            'NH4': {
                'start_days': 0,    # Gennaio
                'span_days': 45,    # Distribuiti in 45 giorni
                'cycle': '2025-01'
            },
            'NO3': {
                'start_days': 10,   # Un po' dopo NH4
                'span_days': 40,    # Distribuiti in 40 giorni  
                'cycle': '2025-01'
            },
            'TOC': {
                'start_days': 35,   # Febbraio-Marzo
                'span_days': 50,    # Distribuiti in 50 giorni
                'cycle': '2025-01'
            }
        }
        
        for param_code, config in parameters_config.items():
            results = Result.query.filter_by(
                parameter_code=param_code, 
                lab_code='LAB_ALPHA',
                cycle_code=config['cycle']
            ).all()
            
            print(f"\n{param_code}: {len(results)} risultati da aggiornare")
            
            for i, result in enumerate(results):
                # Calcola una data casuale nella finestra temporale
                days_offset = config['start_days'] + random.randint(0, config['span_days'])
                hours_offset = random.randint(8, 18)  # Orario lavorativo
                minutes_offset = random.randint(0, 59)
                
                new_date = base_date + timedelta(
                    days=days_offset, 
                    hours=hours_offset, 
                    minutes=minutes_offset
                )
                
                # Aggiorna la data
                result.submitted_at = new_date
                
                if i < 3:  # Mostra le prime 3 per verifica
                    print(f"  Risultato {i+1}: {new_date.strftime('%d/%m/%Y %H:%M')}")
        
        # 3. Aggiungi alcuni risultati per il ciclo 2025-02
        print("\n➕ Aggiunta risultati per ciclo 2025-02...")
        
        # Aggiungi alcuni risultati NH4 e NO3 per febbraio
        feb_base = datetime(2025, 2, 10)
        new_results_count = 0
        
        for param in ['NH4', 'NO3']:
            for i in range(8):  # 8 risultati per parametro in febbraio
                days_offset = random.randint(0, 18)  # Distribuiti in 18 giorni
                hours_offset = random.randint(9, 17)
                
                new_date = feb_base + timedelta(
                    days=days_offset,
                    hours=hours_offset,
                    minutes=random.randint(0, 59)
                )
                
                # Genera z-score realistico
                z_score = random.gauss(0, 1.2)  # Media 0, deviazione 1.2
                
                # Calcola valore misurato basato su z-score
                if param == 'NH4':
                    assigned_value = 2.5  # valore assegnato tipico
                    uncertainty = 0.15
                elif param == 'NO3':
                    assigned_value = 1.8
                    uncertainty = 0.12
                
                measured_value = assigned_value + (z_score * uncertainty)
                
                # Crea nuovo risultato
                new_result = Result(
                    lab_code='LAB_ALPHA',
                    cycle_code='2025-02',
                    parameter_code=param,
                    technique_code=random.choice(['SPETTRO', 'CROMATO', 'TITRIM']),
                    measured_value=round(measured_value, 4),
                    uncertainty=round(uncertainty, 4),
                    submitted_at=new_date,
                    notes=f'Risultato aggiunto per distribuzione temporale - {param}'
                )
                
                db.session.add(new_result)
                new_results_count += 1
        
        print(f"✅ Aggiunti {new_results_count} nuovi risultati per 2025-02")
        
        try:
            db.session.commit()
            print("\n✅ Tutti gli aggiornamenti sono stati salvati con successo!")
            
            # Verifica i risultati
            print("\n📊 Verifica aggiornamenti:")
            
            for param in ['NH4', 'NO3', 'TOC']:
                results = Result.query.filter_by(parameter_code=param, lab_code='LAB_ALPHA').all()
                dates = [r.submitted_at.date() for r in results]
                unique_dates = len(set(dates))
                date_range = f"{min(dates)} → {max(dates)}" if dates else "Nessuna"
                
                print(f"• {param}: {len(results)} risultati, {unique_dates} date uniche")
                print(f"  Range: {date_range}")
                
                # Conta per ciclo
                cycle_01_count = len([r for r in results if r.cycle_code == '2025-01'])
                cycle_02_count = len([r for r in results if r.cycle_code == '2025-02'])
                print(f"  2025-01: {cycle_01_count}, 2025-02: {cycle_02_count}")
            
            # Verifica provider cicli
            print("\n🏢 Provider assegnati ai cicli:")
            for cycle_code in ['2025-01', '2025-02']:
                cycle = Cycle.query.filter_by(code=cycle_code).first()
                if cycle and cycle.provider:
                    print(f"• {cycle_code}: {cycle.provider.name}")
                else:
                    print(f"• {cycle_code}: Nessun provider")
                    
        except Exception as e:
            db.session.rollback()
            print(f"❌ Errore durante il salvataggio: {str(e)}")

if __name__ == '__main__':
    update_nh4_no3_toc_data()