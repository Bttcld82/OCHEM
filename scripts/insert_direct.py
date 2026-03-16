from app import create_app, db
from app.models import Result

app = create_app()
with app.app_context():
    dati = [
        ('NH4', 'SPETTRO', 2.48,  0.05, 'Test inserimento NH4'),
        ('NO3', 'CROMATO', 14.85, 0.20, 'Test inserimento NO3'),
        ('TOC', 'POTENZ',  12.30, 0.10, 'Test inserimento TOC'),
    ]
    for param, tecnica, valore, inc, note in dati:
        r = Result(
            lab_code='LAB_ALPHA',
            cycle_code='2025-01',
            parameter_code=param,
            technique_code=tecnica,
            measured_value=valore,
            uncertainty=inc,
            notes=note,
        )
        db.session.add(r)
    db.session.commit()

    totale = Result.query.filter_by(lab_code='LAB_ALPHA', cycle_code='2025-01').count()
    print(f'OK - Inseriti 3 risultati. Totale ora: {totale}')
    for r in Result.query.filter_by(lab_code='LAB_ALPHA', cycle_code='2025-01').order_by(Result.id.desc()).limit(3).all():
        print(f'  id={r.id}  param={r.parameter_code}  valore={r.measured_value}  tecnica={r.technique_code}')
