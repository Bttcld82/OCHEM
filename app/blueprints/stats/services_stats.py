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
from app.models import Lab, Cycle, CycleParameter, Parameter

# Costante per calcolo RSZ (Robust Z-Score)
MAD_K = 1.4826


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
    
    cycle_params = CycleParameter.query.filter_by(cycle_id=latest_cycle.id).all()
    for cycle_param in cycle_params:
        if cycle_param.parameter:
            param_code = cycle_param.parameter.code
            reference_values[param_code] = {
                'xpt': cycle_param.assigned_xpt or 100.0,  # Default se None
                'spt': cycle_param.assigned_spt or 5.0     # Default se None
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
            cycle_params = CycleParameter.query.filter_by(cycle_id=latest_cycle.id).all()
            
            template_data = {
                'parameter_code': [],
                'result_value': [],
                'technique_code': [],
                'unit_code': [],
                'date_performed': [],
                'assigned_xpt': [],
                'assigned_spt': []
            }
            
            for cp in cycle_params:
                if cp.parameter:
                    template_data['parameter_code'].append(cp.parameter.code)
                    template_data['result_value'].append('')  # Campo da riempire
                    template_data['technique_code'].append('')
                    template_data['unit_code'].append(cp.parameter.unit.code if cp.parameter.unit else '')
                    template_data['date_performed'].append('')
                    template_data['assigned_xpt'].append(cp.assigned_xpt or '')
                    template_data['assigned_spt'].append(cp.assigned_spt or '')
        
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
        dict: Dati formattati per Plotly
    """
    from app.models import Result, ZScore
    from datetime import datetime, timedelta
    
    # Query base per z-scores
    query = db.session.query(ZScore).join(Result).filter(Result.lab_code == lab_code)
    
    # Applica filtri multipli
    if parameter_codes:
        query = query.filter(Result.parameter_code.in_(parameter_codes))
    
    if technique_codes:
        query = query.filter(Result.technique_code.in_(technique_codes))
        
    if cycle_codes:
        query = query.filter(Result.cycle_code.in_(cycle_codes))
    
    # Filtra per data se limit_days specificato
    if limit_days:
        cutoff_date = datetime.utcnow() - timedelta(days=limit_days)
        query = query.filter(Result.submitted_at >= cutoff_date)
    
    # Ordina per data
    z_scores = query.order_by(Result.submitted_at).all()
    
    if not z_scores:
        return {"x": [], "y": [], "parameter_codes": []}
    
    # Prepara i dati per il grafico
    chart_data = {
        "x": [z.result.submitted_at.strftime('%Y-%m-%d %H:%M') if z.result else 'N/A' for z in z_scores],
        "y": [float(z.z) for z in z_scores],
        "parameter_codes": [z.result.parameter_code if z.result else 'N/A' for z in z_scores],
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