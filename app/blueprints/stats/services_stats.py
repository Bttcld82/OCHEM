"""
Services per il modulo Statistics
Contiene la logica di calcolo z-score, sz², rsz usando pandas
"""

import pandas as pd
import numpy as np
from datetime import datetime
from io import StringIO
from flask import current_app
from app import db
from app.models import Lab, Cycle, CycleParameter, Parameter, Result, ZScore, PtStats

# Costante per calcolo RSZ (Robust Z-Score)
MAD_K = 1.4826


def recalculate_pt_stats(cycle_code: str, parameter_code: str, lab_code: str) -> None:
    """
    Ricalcola PtStats (mean_z, rsz, n_results) per la tripletta ciclo/parametro/lab
    basandosi su tutti i ZScore attivi. Crea il record se non esiste, lo elimina se
    non ci sono z-score residui.

    Formula RSZ: MAD_K * median(|z_i - median(z_i)|)  con MAD_K=1.4826 (ISO 13528 §8)
    Deve essere chiamata dopo ogni insert/edit/delete di Result+ZScore.
    """
    z_values = (
        db.session.query(ZScore.z)
        .join(Result, ZScore.result_id == Result.id)
        .filter(
            Result.cycle_code == cycle_code,
            Result.parameter_code == parameter_code,
            Result.lab_code == lab_code,
        )
        .all()
    )
    z_list = [float(row.z) for row in z_values]

    pt = PtStats.query.filter_by(
        cycle_code=cycle_code,
        parameter_code=parameter_code,
        lab_code=lab_code,
    ).first()

    if not z_list:
        if pt:
            db.session.delete(pt)
        return

    n = len(z_list)
    mean_z = float(np.mean(z_list))

    if n >= 2:
        median_z = float(np.median(z_list))
        mad = float(np.median(np.abs(np.array(z_list) - median_z)))
        rsz = MAD_K * mad if mad > 0 else 0.0
    else:
        rsz = 0.0

    if pt is None:
        pt = PtStats(
            cycle_code=cycle_code,
            parameter_code=parameter_code,
            lab_code=lab_code,
            created_at=datetime.utcnow(),
        )
        db.session.add(pt)

    pt.n_results = n
    pt.mean_z = mean_z
    pt.rsz = rsz
    pt.updated_at = datetime.utcnow()


def calculate_cycle_consensus_stats(cycle_code: str, parameter_code: str) -> dict:
    """
    Calcola media e sigma robusti cross-laboratorio per un ciclo/parametro
    usando l'algoritmo A (QIAP) di ISO 13528 Annex C.

    Aggiorna CycleParameter.xpt_robust e sigma_pt_robust.
    Aggiorna PtStats.rsz per ogni laboratorio con z_robust = (x - xpt_robust) / sigma_pt_robust.

    Restituisce un dizionario con i risultati del calcolo.
    Avverte se n < 8 (ISO 13528 §6.4.2).
    """
    from app.models import CycleParameter

    # Recupera tutti i valori misurati per ciclo/parametro
    rows = (
        db.session.query(Result.lab_code, Result.measured_value)
        .filter(
            Result.cycle_code == cycle_code,
            Result.parameter_code == parameter_code,
        )
        .all()
    )

    if not rows:
        return {'error': 'Nessun risultato trovato per questo ciclo/parametro.'}

    values = np.array([float(r.measured_value) for r in rows])
    n = len(values)

    warning = None
    if n < 8:
        warning = f'Solo {n} risultati disponibili (ISO 13528 §6.4.2 raccomanda almeno 8).'

    # Algoritmo A — QIAP (ISO 13528 Annex C §C.2)
    x_star = float(np.median(values))
    s_star = MAD_K * float(np.median(np.abs(values - x_star)))

    if s_star == 0:
        # Deviazione standard robusta nulla: tutti valori identici
        xpt_robust = x_star
        sigma_pt_robust = None
        return {
            'n': n,
            'xpt_robust': xpt_robust,
            'sigma_pt_robust': None,
            'warning': warning or 'Sigma robusto nullo: tutti i valori misurati sono identici.',
        }

    # Iterazione di Winsorizzazione (max 50 iterazioni)
    delta = 1.5 * s_star
    for _ in range(50):
        x_w = np.clip(values, x_star - delta, x_star + delta)
        x_new = float(np.mean(x_w))
        s_new = MAD_K * float(np.median(np.abs(values - x_new)))
        delta_new = 1.5 * s_new
        if abs(x_new - x_star) < 1e-9 * s_star:
            break
        x_star, s_star, delta = x_new, s_new, delta_new

    xpt_robust = x_star
    sigma_pt_robust = s_star

    # Aggiorna CycleParameter
    cp = CycleParameter.query.filter_by(
        cycle_code=cycle_code, parameter_code=parameter_code
    ).first()
    if cp:
        cp.xpt_robust = xpt_robust
        cp.sigma_pt_robust = sigma_pt_robust
        cp.updated_at = datetime.utcnow()

    # Aggiorna PtStats.rsz per ogni laboratorio con z_robust
    for row in rows:
        pt = PtStats.query.filter_by(
            cycle_code=cycle_code,
            parameter_code=parameter_code,
            lab_code=row.lab_code,
        ).first()
        if pt:
            z_robust = (float(row.measured_value) - xpt_robust) / sigma_pt_robust
            pt.rsz = z_robust
            pt.updated_at = datetime.utcnow()

    db.session.commit()

    return {
        'n': n,
        'xpt_robust': round(xpt_robust, 6),
        'sigma_pt_robust': round(sigma_pt_robust, 6),
        'warning': warning,
    }


def process_results_csv(file_stream, lab_code):
    """
    Processa un file CSV con risultati di laboratorio e calcola le statistiche
    
    Args:
        file_stream: Stream del file CSV caricato
        lab_code: Codice del laboratorio
        
    Returns:
        tuple: (df_clean, stats_summary)
            - df_clean: DataFrame pandas con risultati e calcoli
            - stats_summary: Dizionario con statistiche riassuntive
            
    Raises:
        ValueError: Se mancano colonne obbligatorie o dati non validi
    """
    try:
        # Leggi il CSV
        df = pd.read_csv(file_stream)
        
        # Pulisci i nomi delle colonne
        df.columns = df.columns.str.strip().str.lower()
        
        # Validazione colonne obbligatorie
        required_cols = ["parameter_code", "result_value"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Pulizia e conversione dei dati
        df["result_value"] = pd.to_numeric(df["result_value"], errors="coerce")
        
        # Rimuovi righe con valori NaN in result_value
        initial_rows = len(df)
        df.dropna(subset=["result_value"], inplace=True)
        final_rows = len(df)
        
        if final_rows == 0:
            raise ValueError("No valid result_value data found after cleaning")
        
        # Log delle righe rimosse
        if initial_rows != final_rows:
            current_app.logger.info(f"Removed {initial_rows - final_rows} rows with invalid result_value")
        
        # Recupera valori XPT e SPT dal database
        df = _add_reference_values(df, lab_code)
        
        # Calcoli statistici
        df = _calculate_statistics(df)
        
        # Genera statistiche riassuntive
        stats_summary = _generate_summary_stats(df)
        
        return df, stats_summary
        
    except Exception as e:
        current_app.logger.error(f"Error processing CSV for lab {lab_code}: {str(e)}")
        raise


def _add_reference_values(df, lab_code):
    """
    Aggiunge i valori di riferimento XPT e SPT dal database
    
    Args:
        df: DataFrame con i risultati
        lab_code: Codice del laboratorio
        
    Returns:
        DataFrame: DataFrame con colonne xpt e spt aggiunte
    """
    # Recupera il ciclo attivo più recente
    latest_cycle = Cycle.query.filter_by(status='published').order_by(Cycle.created_at.desc()).first()
    
    if not latest_cycle:
        current_app.logger.warning("No published cycle found, using default values")
        # Usa valori di default se non ci sono cicli pubblicati
        df["xpt"] = 100.0  # Valore di riferimento di default
        df["spt"] = 5.0    # Deviazione standard di default
        return df
    
    # Crea un mapping parameter_code -> (xpt, spt)
    reference_values = {}
    
    cycle_params = CycleParameter.query.filter_by(cycle_code=latest_cycle.code).all()
    for cycle_param in cycle_params:
        if cycle_param.parameter:
            param_code = cycle_param.parameter.code
            reference_values[param_code] = {
                'xpt': cycle_param.xpt or 100.0,
                'spt': cycle_param.sigma_pt or 5.0
            }
    
    # Applica i valori di riferimento
    def get_xpt(param_code):
        return reference_values.get(param_code, {}).get('xpt', 100.0)
    
    def get_spt(param_code):
        return reference_values.get(param_code, {}).get('spt', 5.0)
    
    df["xpt"] = df["parameter_code"].map(get_xpt)
    df["spt"] = df["parameter_code"].map(get_spt)
    
    return df


def _calculate_statistics(df):
    """
    Calcola z-score, sz², rsz per ogni risultato
    
    Args:
        df: DataFrame con result_value, xpt, spt
        
    Returns:
        DataFrame: DataFrame con colonne statistiche aggiunte
    """
    # Calcolo Z-score
    df["z_score"] = (df["result_value"] - df["xpt"]) / df["spt"]
    
    # Calcolo SZ² (Squared Z-score)
    df["sz2"] = df["z_score"] ** 2
    
    # Calcolo RSZ (Robust Z-score) per gruppo di parametri
    def calculate_rsz_group(group):
        z_values = group["z_score"]
        if len(z_values) < 2:
            return pd.Series([0.0] * len(group), index=group.index)
        
        median_z = np.median(z_values)
        mad = np.median(np.abs(z_values - median_z))
        rsz = MAD_K * mad if mad > 0 else 0.0
        
        return pd.Series([rsz] * len(group), index=group.index)
    
    # Calcola RSZ per gruppo di parameter_code
    df["rsz"] = df.groupby("parameter_code").apply(calculate_rsz_group).reset_index(level=0, drop=True)
    
    # Aggiungi timestamp del calcolo
    df["calculated_at"] = datetime.utcnow()
    
    return df


def _generate_summary_stats(df):
    """
    Genera statistiche riassuntive per il report
    
    Args:
        df: DataFrame con i calcoli completati
        
    Returns:
        dict: Statistiche riassuntive
    """
    summary = {
        "total_rows": len(df),
        "parameters_count": df["parameter_code"].nunique(),
        "mean_z_score": float(df["z_score"].mean()),
        "median_z_score": float(df["z_score"].median()),
        "std_z_score": float(df["z_score"].std()),
        "max_abs_z_score": float(df["z_score"].abs().max()) if len(df) > 0 else 0.0,
        "min_z_score": float(df["z_score"].min()),
        "max_z_score": float(df["z_score"].max()),
        "mean_sz2": float(df["sz2"].mean()),
        "mean_rsz": float(df["rsz"].mean()),
        
        # Conteggi per fasce di performance
        "z_excellent": int((df["z_score"].abs() < 2).sum()),      # |z| < 2
        "z_acceptable": int(((df["z_score"].abs() >= 2) & (df["z_score"].abs() < 3)).sum()),  # 2 ≤ |z| < 3
        "z_poor": int((df["z_score"].abs() >= 3).sum()),          # |z| ≥ 3
        
        # Percentuali
        "percent_excellent": 0.0,
        "percent_acceptable": 0.0,
        "percent_poor": 0.0,
    }
    
    # Calcola percentuali
    if summary["total_rows"] > 0:
        summary["percent_excellent"] = (summary["z_excellent"] / summary["total_rows"]) * 100
        summary["percent_acceptable"] = (summary["z_acceptable"] / summary["total_rows"]) * 100
        summary["percent_poor"] = (summary["z_poor"] / summary["total_rows"]) * 100
    
    return summary


def generate_template_csv(lab_code):
    """
    Genera un template CSV per il caricamento dei risultati
    
    Args:
        lab_code: Codice del laboratorio
        
    Returns:
        str: Contenuto CSV come stringa
    """
    try:
        # Recupera il ciclo pubblicato più recente
        latest_cycle = Cycle.query.filter_by(status='published').order_by(Cycle.created_at.desc()).first()
        
        if not latest_cycle:
            # Template generico se non ci sono cicli
            template_data = {
                'parameter_code': ['NH4', 'NO3', 'TOC', 'pH'],
                'result_value': ['', '', '', ''],
                'technique_code': ['', '', '', ''],
                'unit_code': ['mg/L', 'mg/L', 'mg/L', 'units'],
                'date_performed': ['', '', '', '']
            }
        else:
            # Template basato sui parametri del ciclo
            cycle_params = CycleParameter.query.filter_by(cycle_code=latest_cycle.code).all()

            template_data = {
                'parameter_code': [],
                'result_value': [],
                'technique_code': [],
                'unit_code': [],
                'xpt': [],
                'sigma_pt': []
            }

            for cp in cycle_params:
                if cp.parameter:
                    template_data['parameter_code'].append(cp.parameter.code)
                    template_data['result_value'].append('')
                    template_data['technique_code'].append('')
                    template_data['unit_code'].append(cp.parameter.unit.code if cp.parameter.unit else '')
                    template_data['xpt'].append(cp.xpt or '')
                    template_data['sigma_pt'].append(cp.sigma_pt or '')
        
        # Crea DataFrame e converti in CSV
        df_template = pd.DataFrame(template_data)
        
        # Converti in CSV string
        csv_buffer = StringIO()
        df_template.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        
        return csv_content
        
    except Exception as e:
        current_app.logger.error(f"Error generating template CSV for lab {lab_code}: {str(e)}")
        # Template di fallback
        fallback_template = """parameter_code,result_value,technique_code,unit_code,date_performed
NH4,,ICP-MS,mg/L,
NO3,,IC,mg/L,
TOC,,TOC-V,mg/L,
pH,,Electrode,units,"""
        return fallback_template


def get_control_chart_data(lab_code, parameter_codes=None, limit_days=30, technique_codes=None, cycle_codes=None):
    """
    Recupera i dati per i grafici di controllo con filtri multipli
    
    Args:
        lab_code: Codice del laboratorio
        parameter_codes: Lista codici parametri (opzionale)
        limit_days: Limite giorni per i dati (default 30)
        technique_codes: Lista codici tecniche (opzionale)
        cycle_codes: Lista codici cicli (opzionale)
        
    Returns:
        dict: Dati formattati per Plotly con nomi completi
    """
    from app.models import Result, ZScore, Technique, Provider
    from datetime import datetime, timedelta
    
    # Query con join per ottenere nomi completi
    query = db.session.query(
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
    ).filter(Result.lab_code == lab_code)
    
    # Applica filtri multipli
    if parameter_codes:
        query = query.filter(Result.parameter_code.in_(parameter_codes))
    
    if technique_codes:
        query = query.filter(Result.technique_code.in_(technique_codes))
        
    if cycle_codes:
        query = query.filter(Result.cycle_code.in_(cycle_codes))
    
    # Filtra per data se limit_days specificato
    if limit_days is not None and limit_days > 0:
        cutoff_date = datetime.utcnow() - timedelta(days=limit_days)
        query = query.filter(Result.submitted_at >= cutoff_date)
    
    # Debug: Log della query
    from flask import current_app
    try:
        current_app.logger.info(f"Query SQL: {str(query.statement.compile(compile_kwargs={'literal_binds': True}))}")
    except Exception:
        current_app.logger.info(f"Query being executed for lab_code={lab_code}, parameters={parameter_codes}")
    
    # Ordina per data
    results = query.order_by(Result.submitted_at).all()
    
    current_app.logger.info(f"Query returned {len(results)} results")
    
    if not results:
        # Debug: Verifica se esistono dati di base per questi parametri
        basic_query = db.session.query(Result).filter(Result.lab_code == lab_code)
        if parameter_codes:
            basic_query = basic_query.filter(Result.parameter_code.in_(parameter_codes))
        basic_results = basic_query.all()
        current_app.logger.info(f"Basic query (only Results) returned {len(basic_results)} results")
        
        # Verifica se ci sono ZScore associati
        zscore_query = db.session.query(ZScore).join(Result).filter(Result.lab_code == lab_code)
        if parameter_codes:
            zscore_query = zscore_query.filter(Result.parameter_code.in_(parameter_codes))
        zscore_results = zscore_query.all()
        current_app.logger.info(f"ZScore query returned {len(zscore_results)} results")
        
        return {"x": [], "y": [], "parameter_codes": [], "parameter_names": [], "technique_names": [], "cycle_names": [], "provider_names": []}
    
    # Prepara i dati per il grafico con nomi completi
    chart_data = {
        "x": [result.Result.submitted_at.strftime('%Y-%m-%d %H:%M') if result.Result else 'N/A' for result in results],
        "y": [float(result.ZScore.z) for result in results],
        "parameter_codes": [result.Result.parameter_code if result.Result else 'N/A' for result in results],
        "parameter_names": [result.Parameter.name if result.Parameter else 'N/A' for result in results],
        "technique_names": [result.Technique.name if result.Technique else 'N/A' for result in results],
        "cycle_names": [result.Cycle.name if result.Cycle else 'N/A' for result in results],
        "provider_names": [result.Provider.name if result.Provider else 'N/A' for result in results],
        "colors": []
    }
    
    # Assegna colori basati sui valori z
    for z_val in chart_data["y"]:
        abs_z = abs(z_val)
        if abs_z < 2:
            chart_data["colors"].append("green")
        elif abs_z < 3:
            chart_data["colors"].append("orange") 
        else:
            chart_data["colors"].append("red")
    
    return chart_data