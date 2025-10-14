"""
Debug script per verificare i dati NH4, NO3, TOC nel database
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import Result, ZScore, Parameter, Technique, Cycle, Provider, Lab

app = create_app()

with app.app_context():
    print("=== DEBUG CHART DATA ===")
    
    # Trova tutti i lab codes disponibili
    labs = Lab.query.all()
    print(f"Labs disponibili: {[lab.code for lab in labs]}")
    
    if not labs:
        print("Nessun laboratorio trovato!")
        sys.exit(1)
    
    lab_code = labs[0].code  # Usa il primo lab
    print(f"Usando lab_code: {lab_code}")
    
    # Cerca parametri NH4, NO3, TOC
    target_params = ['NH4', 'NO3', 'TOC']
    print(f"\n=== Cerca parametri {target_params} ===")
    
    for param_code in target_params:
        print(f"\n--- Parametro {param_code} ---")
        
        # Verifica se il parametro esiste
        param = Parameter.query.filter_by(code=param_code).first()
        if param:
            print(f"Parametro trovato: {param.code} - {param.name}")
        else:
            print(f"ERRORE: Parametro {param_code} non trovato nella tabella Parameter!")
            continue
        
        # Verifica Results per questo parametro
        results = Result.query.filter_by(
            lab_code=lab_code,
            parameter_code=param_code
        ).all()
        print(f"Results trovati: {len(results)}")
        
        if results:
            for i, result in enumerate(results[:3]):  # Primi 3 risultati
                print(f"  Result {i+1}: ID={result.id}, value={result.measured_value}, submitted_at={result.submitted_at}")
        
        # Verifica ZScores per questi results
        zscores = db.session.query(ZScore).join(Result).filter(
            Result.lab_code == lab_code,
            Result.parameter_code == param_code
        ).all()
        print(f"ZScores trovati: {len(zscores)}")
        
        if zscores:
            for i, zscore in enumerate(zscores[:3]):  # Primi 3 zscores
                print(f"  ZScore {i+1}: result_id={zscore.result_id}, z={zscore.z}")
    
    # Verifica join completo come nella query originale
    print(f"\n=== Test Query Completa ===")
    
    complex_query = db.session.query(
        ZScore, 
        Result, 
        Parameter, 
        Technique, 
        Cycle, 
        Provider
    ).join(
        Result, ZScore.result_id == Result.id
    ).outerjoin(
        Parameter, Result.parameter_code == Parameter.code
    ).outerjoin(
        Technique, Result.technique_code == Technique.code  
    ).outerjoin(
        Cycle, Result.cycle_code == Cycle.code
    ).outerjoin(
        Provider, Cycle.provider_id == Provider.id
    ).filter(
        Result.lab_code == lab_code,
        Result.parameter_code.in_(target_params)
    )
    
    complex_results = complex_query.all()
    print(f"Query completa: {len(complex_results)} risultati")
    
    if complex_results:
        for i, result in enumerate(complex_results[:3]):
            print(f"  Risultato {i+1}:")
            print(f"    ZScore: {result.ZScore.z if result.ZScore else 'None'}")
            print(f"    Parameter: {result.Parameter.code if result.Parameter else 'None'}")
            print(f"    Result: {result.Result.measured_value if result.Result else 'None'}")
            print(f"    Date: {result.Result.submitted_at if result.Result else 'None'}")
    
    print(f"\n=== Fine Debug ===")