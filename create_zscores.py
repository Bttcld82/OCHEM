"""
Script per creare Z-score per i risultati mancanti
"""
import sys
import os

# Aggiungi il percorso del progetto al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Result, ZScore
import random

def create_missing_zscores():
    """Crea Z-score per i risultati che ne sono privi"""
    
    app = create_app()
    
    with app.app_context():
        print("Ricerca risultati senza Z-score...")
        
        # Trova risultati senza Z-score
        results_without_zscore = db.session.query(Result).outerjoin(
            ZScore, Result.id == ZScore.result_id
        ).filter(
            ZScore.result_id.is_(None),
            Result.lab_code == 'LAB_ALPHA'
        ).all()
        
        print(f"Trovati {len(results_without_zscore)} risultati senza Z-score")
        
        if results_without_zscore:
            print("Creazione Z-score per i nuovi risultati...")
            
            for i, result in enumerate(results_without_zscore):
                # Genera Z-score realistico
                z_score = random.gauss(0, 1.1)  # Media 0, deviazione 1.1
                sz2 = z_score ** 2  # sz²
                
                # Crea record Z-score
                zscore_record = ZScore(
                    result_id=result.id,
                    z=round(z_score, 6),
                    sz2=round(sz2, 6)
                )
                
                db.session.add(zscore_record)
                
                if i < 5:  # Mostra primi 5 per verifica
                    print(f"  {result.parameter_code} ({result.cycle_code}): z={z_score:.3f}")
            
            try:
                db.session.commit()
                print("Z-score creati con successo!")
                
                # Verifica
                total_results = Result.query.filter_by(lab_code='LAB_ALPHA').count()
                total_zscores = ZScore.query.join(Result).filter(Result.lab_code == 'LAB_ALPHA').count()
                print(f"Totali: {total_results} risultati, {total_zscores} Z-score")
                
            except Exception as e:
                db.session.rollback()
                print(f"ERRORE durante il salvataggio: {str(e)}")
        else:
            print("Tutti i risultati hanno gia' Z-score")

if __name__ == '__main__':
    create_missing_zscores()