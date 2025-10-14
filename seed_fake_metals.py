#!/usr/bin/env python3
"""
Popola LAB_ALPHA con dati fake per 10 metalli su 3 mesi
"""
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Lab, Result, ZScore, Parameter

METALS = ['Fe', 'Cu', 'Zn', 'Pb', 'Cd', 'Ni', 'Cr', 'Mn', 'As', 'Hg']
N_RESULTS = 120  # 12 risultati per metallo

random.seed(42)

def seed_metals():
    app = create_app()
    with app.app_context():
        lab = Lab.query.filter_by(code='LAB_ALPHA').first()
        if not lab:
            print('LAB_ALPHA non trovato!')
            return
        # Crea parametri se non esistono
        for metal in METALS:
            if not Parameter.query.filter_by(code=metal).first():
                db.session.add(Parameter(code=metal, name=f"{metal} (metallo)", unit_code="mg/L"))
        db.session.commit()
        # Genera risultati
        base_date = datetime.utcnow() - timedelta(days=90)
        for metal in METALS:
            for i in range(12):
                date = base_date + timedelta(days=random.randint(0, 90))
                value = round(random.uniform(0.01, 2.5), 3)
                z = round(random.gauss(0, 1.2), 3)
                sz2 = round(random.uniform(0.2, 1.5), 3)
                # Crea Result
                result = Result(
                    lab_code='LAB_ALPHA',
                    cycle_code='CYCLE_METALS',
                    parameter_code=metal,
                    measured_value=value,
                    technique_code='ICP-MS',
                    submitted_at=date
                )
                db.session.add(result)
                db.session.flush()
                # Crea ZScore
                zscore = ZScore(
                    result_id=result.id,
                    z=z,
                    sz2=sz2
                )
                db.session.add(zscore)
        db.session.commit()
        print(f"Dati fake per metalli inseriti in LAB_ALPHA!")

if __name__ == '__main__':
    seed_metals()
