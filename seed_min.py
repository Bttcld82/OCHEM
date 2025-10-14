# seed_min.py
from app import create_app, db
from app.models import Lab, Parametro
app = create_app()
with app.app_context():
    if not Lab.query.filter_by(code="LAB01").first():
        db.session.add(Lab(name="Lab Demo", code="LAB01"))
    if not Parametro.query.filter_by(codice="N-NH4").first():
        db.session.add(Parametro(codice="N-NH4", nome="Azoto ammoniacale", unita="mg/L"))
    db.session.commit()
    print("Seed ok.")