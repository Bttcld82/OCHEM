"""
Script per aggiungere provider e cicli fake per demo
"""
import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Provider, Cycle, Result
from datetime import datetime

def create_fake_providers_and_cycles():
    """Crea provider e cicli fake per demo"""
    
    app = create_app()
    
    with app.app_context():
        print("🏭 Creazione provider fake...")
        
        # Provider fake
        providers = [
            {
                'code': 'METLAB_EU', 
                'name': 'MetalLab Europe - Laboratorio Metalli (Germania)'
            },
            {
                'code': 'AQUATEST_INT', 
                'name': 'AquaTest International - Analisi Acque (Francia)'
            },
            {
                'code': 'ECOLAB_NORD', 
                'name': 'EcoLab Nordic - Controlli Ambientali (Svezia)'
            }
        ]
        
        for prov_data in providers:
            existing = Provider.query.filter_by(code=prov_data['code']).first()
            if not existing:
                provider = Provider(
                    code=prov_data['code'],
                    name=prov_data['name']
                )
                db.session.add(provider)
                print(f"✅ Provider creato: {provider.code} - {provider.name}")
            else:
                print(f"⚠️  Provider già esistente: {prov_data['code']}")
        
        print("\n🔄 Creazione cicli fake...")
        
        # Ottieni gli ID dei provider per i cicli
        metlab_provider = Provider.query.filter_by(code='METLAB_EU').first()
        aquatest_provider = Provider.query.filter_by(code='AQUATEST_INT').first()
        ecolab_provider = Provider.query.filter_by(code='ECOLAB_NORD').first()
        
        # Cicli fake per i metalli e altre analisi
        cycles = [
            {
                'code': 'CYCLE_METALS', 
                'name': 'Ciclo Metalli Pesanti - 2025',
                'provider_id': metlab_provider.id if metlab_provider else None,
                'start_date': datetime(2025, 1, 1),
                'end_date': datetime(2025, 3, 31),
                'status': 'active'
            },
            {
                'code': '2025-03', 
                'name': 'Ciclo PT Marzo 2025',
                'provider_id': aquatest_provider.id if aquatest_provider else None,
                'start_date': datetime(2025, 3, 1),
                'end_date': datetime(2025, 3, 31),
                'status': 'active'
            },
            {
                'code': '2025-04', 
                'name': 'Ciclo PT Aprile 2025',
                'provider_id': ecolab_provider.id if ecolab_provider else None,
                'start_date': datetime(2025, 4, 1),
                'end_date': datetime(2025, 4, 30),
                'status': 'draft'
            }
        ]
        
        for cycle_data in cycles:
            existing = Cycle.query.filter_by(code=cycle_data['code']).first()
            if not existing:
                cycle = Cycle(
                    code=cycle_data['code'],
                    name=cycle_data['name'],
                    provider_id=cycle_data['provider_id'],
                    start_date=cycle_data['start_date'],
                    end_date=cycle_data['end_date'],
                    status=cycle_data['status']
                )
                db.session.add(cycle)
                print(f"✅ Ciclo creato: {cycle.code} - {cycle.name}")
            else:
                print(f"⚠️  Ciclo già esistente: {cycle_data['code']}")
        
        try:
            db.session.commit()
            print("✅ Tutti i dati sono stati salvati con successo!")
            
            # Verifica i risultati
            print("\n📊 Verifica risultati:")
            providers_count = Provider.query.count()
            cycles_count = Cycle.query.count()
            print(f"• Provider totali: {providers_count}")
            print(f"• Cicli totali: {cycles_count}")
            
            # Controlla i risultati per ciclo
            for cycle_code in ['CYCLE_METALS', '2025-01', '2025-02']:
                count = Result.query.filter_by(cycle_code=cycle_code).count()
                print(f"• Risultati in {cycle_code}: {count}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Errore durante il salvataggio: {str(e)}")

if __name__ == '__main__':
    create_fake_providers_and_cycles()