#!/usr/bin/env python3
"""
Script per controllare i dati disponibili per LAB_ALPHA
"""

from app import create_app, db
from app.models import Lab, Result, ZScore, PtStats, Cycle, Parameter, User, UserLabRole

def check_lab_alpha_data():
    app = create_app()
    
    with app.app_context():
        print("=== CONTROLLO DATI LAB_ALPHA ===\n")
        
        # 1. Verifica se LAB_ALPHA esiste
        lab_alpha = Lab.query.filter_by(code='LAB_ALPHA').first()
        if not lab_alpha:
            print("❌ LAB_ALPHA non trovato nel database!")
            return
        
        print(f"✅ LAB_ALPHA trovato: {lab_alpha.name}")
        print(f"   - ID: {lab_alpha.id}")
        print(f"   - Attivo: {lab_alpha.is_active}")
        print(f"   - Città: {lab_alpha.city}")
        print()
        
        # 2. Utenti del laboratorio
        print("👥 UTENTI DEL LABORATORIO:")
        lab_roles = UserLabRole.query.filter_by(lab_id=lab_alpha.id).all()
        if lab_roles:
            for role in lab_roles:
                user = User.query.get(role.user_id)
                print(f"   - {user.username} ({user.email}) - Ruolo: {role.role.name}")
        else:
            print("   Nessun utente assegnato al laboratorio")
        print()
        
        # 3. Risultati per LAB_ALPHA
        print("📊 RISULTATI:")
        results = Result.query.filter_by(lab_code='LAB_ALPHA').all()
        print(f"   Totale risultati: {len(results)}")
        
        if results:
            # Raggruppa per parametro
            params = {}
            for result in results:
                if result.parameter_code not in params:
                    params[result.parameter_code] = 0
                params[result.parameter_code] += 1
            
            print("   Risultati per parametro:")
            for param, count in params.items():
                print(f"     - {param}: {count} risultati")
                
            print(f"   Date: {min(r.date_performed for r in results)} → {max(r.date_performed for r in results)}")
        else:
            print("   ❌ Nessun risultato trovato")
        print()
        
        # 4. Z-Scores per LAB_ALPHA
        print("🧮 Z-SCORES:")
        z_scores = db.session.query(ZScore).join(Result).filter(Result.lab_code == 'LAB_ALPHA').all()
        print(f"   Totale Z-scores: {len(z_scores)}")
        
        if z_scores:
            z_values = [float(z.z) for z in z_scores]
            print(f"   Min Z-score: {min(z_values):.3f}")
            print(f"   Max Z-score: {max(z_values):.3f}")
            print(f"   Media Z-score: {sum(z_values)/len(z_values):.3f}")
            
            # Performance distribution
            excellent = sum(1 for z in z_values if abs(z) < 2)
            acceptable = sum(1 for z in z_values if 2 <= abs(z) < 3)
            poor = sum(1 for z in z_values if abs(z) >= 3)
            
            print(f"   Performance:")
            print(f"     - Eccellente (|z| < 2): {excellent}")
            print(f"     - Accettabile (2 ≤ |z| < 3): {acceptable}")
            print(f"     - Scadente (|z| ≥ 3): {poor}")
        else:
            print("   ❌ Nessun Z-score trovato")
        print()
        
        # 5. PT Stats per LAB_ALPHA
        print("📈 STATISTICHE PT:")
        pt_stats = PtStats.query.filter_by(lab_code='LAB_ALPHA').all()
        print(f"   Totale PT Stats: {len(pt_stats)}")
        
        if pt_stats:
            for stat in pt_stats:
                print(f"     - Ciclo: {stat.cycle_code}, Parametro: {stat.parameter_code}")
                print(f"       N.risultati: {stat.n_results}, Mean Z: {stat.mean_z}, RSZ: {stat.rsz}")
        else:
            print("   ❌ Nessuna statistica PT trovata")
        print()
        
        # 6. Cicli disponibili
        print("🔄 CICLI:")
        cycles = Cycle.query.all()
        print(f"   Totale cicli: {len(cycles)}")
        
        if cycles:
            for cycle in cycles[:5]:  # Mostra solo i primi 5
                print(f"     - {cycle.code}: {cycle.name} (Status: {cycle.status})")
            if len(cycles) > 5:
                print(f"     ... e altri {len(cycles) - 5} cicli")
        else:
            print("   ❌ Nessun ciclo trovato")
        print()
        
        # 7. Parametri disponibili
        print("🧪 PARAMETRI:")
        parameters = Parameter.query.all()
        print(f"   Totale parametri: {len(parameters)}")
        
        if parameters:
            for param in parameters[:10]:  # Mostra solo i primi 10
                print(f"     - {param.code}: {param.name}")
            if len(parameters) > 10:
                print(f"     ... e altri {len(parameters) - 10} parametri")
        else:
            print("   ❌ Nessun parametro trovato")
        print()

if __name__ == '__main__':
    check_lab_alpha_data()