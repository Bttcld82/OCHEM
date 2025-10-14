"""
Routes per il modulo Statistics
Gestisce download template, upload risultati, visualizzazione dati e grafici
"""

from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for, Response, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import io
from datetime import datetime
import pandas as pd

from app import db
from app.models import Lab, Cycle, Result, ZScore, PtStats, UploadFile
from app.blueprints.auth.decorators import lab_role_required
from app.blueprints.stats.services_stats import process_results_csv, generate_template_csv, get_control_chart_data
import plotly.graph_objects as go
import plotly.utils
import json

# Blueprint già definito in __init__.py
from . import stats_bp, stats_general_bp

@stats_bp.route("/test-chart")
def test_chart(lab_code):
    """Test temporaneo per Plotly"""
    return send_file("../../test_chart.html")


@stats_bp.route("/template.csv")
@login_required
@lab_role_required("analyst")
def download_template(lab_code):
    """
    Download del template CSV per inserimento risultati
    
    GET /l/<lab_code>/stats/template.csv
    
    Genera un file CSV con:
    - parameter_code: Codici parametri del ciclo attivo
    - result_value: Campo vuoto da riempire
    - technique_code: Campo tecnica (vuoto)
    - unit_code: Unità di misura del parametro
    - date_performed: Data esecuzione analisi (vuota)
    - assigned_xpt: Valore di riferimento
    - assigned_spt: Deviazione standard
    """
    try:
        # Genera il contenuto CSV
        csv_content = generate_template_csv(lab_code)
        
        # Crea response con il file
        filename = f"template_{lab_code}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
    except Exception as e:
        current_app.logger.error(f"Error downloading template for {lab_code}: {str(e)}")
        flash(f"Errore nella generazione del template: {str(e)}", "danger")
        return redirect(url_for('main.lab_hub', lab_code=lab_code))


@stats_bp.route("/upload", methods=['GET', 'POST'])
@login_required
@lab_role_required("analyst")
def upload_results(lab_code):
    """
    Upload e processamento dei risultati
    
    GET: Mostra form di upload
    POST: Processa il file caricato e calcola statistiche
    """
    if request.method == 'GET':
        return render_template('stats/upload_form.html', lab_code=lab_code)
    
    # POST - Processamento file
    try:
        # Verifica che il file sia presente
        if 'file' not in request.files:
            flash("Nessun file selezionato", "warning")
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash("Nessun file selezionato", "warning")
            return redirect(request.url)
        
        # Verifica estensione file
        if not file.filename.lower().endswith('.csv'):
            flash("Solo file CSV sono supportati", "danger")
            return redirect(request.url)
        
        # Salva informazioni del file
        original_filename = secure_filename(file.filename)
        file_size = len(file.read())
        file.seek(0)  # Reset stream position
        
        # Processa il CSV
        df_clean, stats_summary = process_results_csv(file, lab_code)
        
        # Salva record UploadFile
        upload_record = UploadFile(
            filename=f"results_{lab_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            original_filename=original_filename,
            file_size=file_size,
            mime_type='text/csv',
            lab_code=lab_code,
            uploaded_by=current_user.id,
            uploaded_at=datetime.utcnow(),
            status='processed'
        )
        
        # Trova o crea il ciclo corrente per associare i risultati
        current_cycle = Cycle.query.filter_by(status='published').order_by(Cycle.created_at.desc()).first()
        if current_cycle:
            upload_record.cycle_code = current_cycle.code
        
        db.session.add(upload_record)
        db.session.flush()  # Per ottenere l'ID
        
        # Salva i risultati nel database
        _save_results_to_db(df_clean, lab_code, upload_record.id, current_cycle)
        
        db.session.commit()
        
        flash(f"File processato con successo! {stats_summary['total_rows']} risultati caricati.", "success")
        flash(f"Statistiche: Media Z-score = {stats_summary['mean_z_score']:.3f}, "
              f"Performance Eccellente = {stats_summary['percent_excellent']:.1f}%", "info")
        
        return redirect(url_for('stats_bp.results_view', lab_code=lab_code))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading results for {lab_code}: {str(e)}")
        flash(f"Errore nel processamento del file: {str(e)}", "danger")
        return redirect(request.url)


@stats_bp.route("/results")
@login_required
@lab_role_required("viewer")
def results_view(lab_code):
    """
    Visualizzazione tabella risultati con z-scores
    
    Mostra tutti i risultati del laboratorio con:
    - Colori condizionali basati su |z|
    - Statistiche riassuntive
    - Link ai grafici di controllo
    """
    try:
        # Recupera gli ultimi risultati con Z-scores (limitiamo a 100 per performance)
        # Nota: PtStats sono statistiche aggregate, non collegate ai singoli risultati
        results_query = db.session.query(Result, ZScore).join(
            ZScore, Result.id == ZScore.result_id, isouter=True
        ).filter(Result.lab_code == lab_code).order_by(Result.submitted_at.desc()).limit(100)
        
        results_data = results_query.all()
        
        # Prepara i dati per il template
        results_list = []
        for result, z_score in results_data:
            result_dict = {
                'id': result.id,
                'parameter_code': result.parameter_code,
                'result_value': result.measured_value,
                'technique_code': result.technique_code,
                'unit_code': result.parameter.unit.code if result.parameter and result.parameter.unit else '',
                'date_performed': result.submitted_at,
                'z_score': z_score.z if z_score else None,
                'sz2': z_score.sz2 if z_score else None,
                'rsz': None,  # RSZ non è nel modello ZScore
                'performance_class': _get_performance_class(z_score.z if z_score else 0)
            }
            results_list.append(result_dict)
        
        # Calcola statistiche riassuntive
        z_scores = [r['z_score'] for r in results_list if r['z_score'] is not None]
        summary_stats = None
        if z_scores:
            summary_stats = {
                'total_results': len(results_list),
                'mean_z': sum(z_scores) / len(z_scores),
                'excellent_count': sum(1 for z in z_scores if abs(z) < 2),
                'acceptable_count': sum(1 for z in z_scores if 2 <= abs(z) < 3),
                'poor_count': sum(1 for z in z_scores if abs(z) >= 3),
                'max_abs_z': max(abs(z) for z in z_scores) if z_scores else 0
            }
        
        return render_template('stats/results_table.html', 
                             lab_code=lab_code,
                             results=results_list,
                             summary=summary_stats)
        
    except Exception as e:
        current_app.logger.error(f"Error loading results for {lab_code}: {str(e)}")
        flash(f"Errore nel caricamento dei risultati: {str(e)}", "danger")
        return redirect(url_for('main.lab_hub', lab_code=lab_code))


@stats_bp.route("/charts", methods=['GET', 'POST'])
@login_required
@lab_role_required("viewer") 
def control_charts(lab_code):
    """
    Grafici di controllo 100% Python - NO JavaScript!
    """
    try:
        from app.forms import ChartsForm
        
        # Inizializza il form
        form = ChartsForm(lab_code=lab_code)
        
        # Variabili per il template
        chart_html = None
        chart_data = None
        
        if form.validate_on_submit():
            # Ottieni i dati selezionati dal form
            selected_params = form.parameters.data or []
            selected_techs = form.techniques.data or []
            selected_cycles = form.cycles.data or []
            days = int(form.days.data) if form.days.data else 30
            
            current_app.logger.info(f"Form submitted - Params: {selected_params}, Techs: {selected_techs}, Cycles: {selected_cycles}")
            
            # Carica i dati per il grafico
            if selected_params:  # Almeno un parametro deve essere selezionato
                chart_data = get_control_chart_data(
                    lab_code=lab_code,
                    parameter_codes=selected_params,
                    technique_codes=selected_techs if selected_techs else None,
                    cycle_codes=selected_cycles if selected_cycles else None,
                    limit_days=days
                )
                
                # Genera il grafico HTML usando Plotly Python
                if chart_data and len(chart_data.get('x', [])) > 0:
                    chart_html = generate_plotly_chart(chart_data, lab_code)
                else:
                    flash("Nessun dato trovato per i filtri selezionati.", "warning")
            else:
                flash("Seleziona almeno un parametro per visualizzare il grafico.", "info")
        
        return render_template('stats/charts_simple.html',
                             lab_code=lab_code,
                             form=form,
                             chart_html=chart_html,
                             chart_data=chart_data)
        
    except Exception as e:
        current_app.logger.error(f"Error in control_charts for {lab_code}: {str(e)}")
        flash(f"Errore: {str(e)}", "danger")
        return redirect(url_for('main.lab_hub', lab_code=lab_code))

def generate_plotly_chart(chart_data, lab_code):
    """Genera il grafico Plotly lato server"""
    import plotly.graph_objects as go
    import plotly.utils
    
    # Crea il grafico
    fig = go.Figure()
    
    # Trace principale con i dati
    fig.add_trace(go.Scatter(
        x=chart_data['x'],
        y=chart_data['y'],
        mode='markers+lines',
        name='Z-Score',
        marker=dict(
            color=[get_point_color(z) for z in chart_data['y']],
            size=8,
            line=dict(color='white', width=1)
        ),
        line=dict(color='blue', width=2)
    ))
    
    # Linee di controllo
    x_range = [chart_data['x'][0], chart_data['x'][-1]]
    
    # Limite superiore di controllo (+3σ)
    fig.add_trace(go.Scatter(
        x=x_range,
        y=[3, 3],
        mode='lines',
        name='UCL (+3σ)',
        line=dict(color='red', dash='dash', width=2)
    ))
    
    # Limite inferiore di controllo (-3σ)
    fig.add_trace(go.Scatter(
        x=x_range,
        y=[-3, -3],
        mode='lines',
        name='LCL (-3σ)',
        line=dict(color='red', dash='dash', width=2)
    ))
    
    # Limiti di warning (±2σ)
    fig.add_trace(go.Scatter(
        x=x_range,
        y=[2, 2],
        mode='lines',
        name='UWL (+2σ)',
        line=dict(color='orange', dash='dot', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=x_range,
        y=[-2, -2],
        mode='lines',
        name='LWL (-2σ)',
        line=dict(color='orange', dash='dot', width=1)
    ))
    
    # Linea centrale (0σ)
    fig.add_trace(go.Scatter(
        x=x_range,
        y=[0, 0],
        mode='lines',
        name='CL (0σ)',
        line=dict(color='green', width=2)
    ))
    
    # Layout del grafico
    fig.update_layout(
        title=f'Control Chart Z-Score - Lab {lab_code}',
        xaxis_title='Data/Ora',
        yaxis_title='Z-Score',
        yaxis=dict(range=[-4, 4]),
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    # Converti in HTML
    return fig.to_html(include_plotlyjs='cdn', div_id='chart')

def get_point_color(z_score):
    """Determina il colore del punto basato sul Z-score"""
    abs_z = abs(z_score)
    if abs_z >= 3:
        return 'red'
    elif abs_z >= 2:
        return 'orange'
    else:
        return 'green'


def _save_results_to_db(df, lab_code, upload_file_id, cycle=None):
    """
    Salva i risultati processati nel database
    
    Args:
        df: DataFrame con i risultati calcolati
        lab_code: Codice laboratorio
        upload_file_id: ID del file di upload
        cycle: Oggetto Cycle corrente (opzionale)
    """
    for _, row in df.iterrows():
        try:
            # Crea record Result
            result = Result(
                lab_code=lab_code,
                parameter_code=row['parameter_code'],
                result_value=float(row['result_value']),
                technique_code=row.get('technique_code', ''),
                unit_code=row.get('unit_code', ''),
                date_performed=row.get('date_performed') or datetime.utcnow(),
                upload_file_id=upload_file_id,
                cycle_code=cycle.code if cycle else None,
                user_id=current_user.id
            )
            db.session.add(result)
            db.session.flush()  # Per ottenere l'ID
            
            # Crea record ZScore
            z_score = ZScore(
                result_id=result.id,
                z=float(row['z_score']),
                sz2=float(row['sz2'])
            )
            db.session.add(z_score)
            
            # Crea record PtStats (statistiche aggregate per ciclo/parametro/lab)
            # Verifichiamo se esiste già per questo ciclo/parametro/lab
            existing_stats = PtStats.query.filter_by(
                cycle_code=result.cycle_code,
                parameter_code=result.parameter_code,
                lab_code=result.lab_code
            ).first()
            
            if not existing_stats:
                pt_stats = PtStats(
                    cycle_code=result.cycle_code,
                    parameter_code=result.parameter_code,
                    lab_code=result.lab_code,
                    n_results=1,
                    mean_z=float(row['z_score']),
                    rsz=float(row['rsz']) if row.get('rsz') else None
                )
                db.session.add(pt_stats)
            else:
                # Aggiorna le statistiche esistenti
                existing_stats.n_results += 1
                existing_stats.updated_at = datetime.utcnow()
            
        except Exception as e:
            current_app.logger.error(f"Error saving result row: {str(e)}")
            continue  # Continua con la prossima riga


def _get_performance_class(z_score):
    """
    Determina la classe di performance basata sul z-score
    
    Args:
        z_score: Valore z-score
        
    Returns:
        str: Classe CSS per il coloring
    """
    if z_score is None:
        return 'secondary'
    
    abs_z = abs(z_score)
    if abs_z < 2:
        return 'success'  # Verde - Eccellente
    elif abs_z < 3:
        return 'warning'  # Arancione - Accettabile
    else:
        return 'danger'   # Rosso - Scarso


def _calculate_performance_score(z_score):
    """
    Calcola uno score numerico per la performance
    
    Args:
        z_score: Valore z-score
        
    Returns:
        int: Score da 0 a 100
    """
    abs_z = abs(z_score)
    if abs_z < 1:
        return 100
    elif abs_z < 2:
        return 85
    elif abs_z < 3:
        return 70
    else:
        return max(0, 50 - int(abs_z * 5))


# ==== ROUTE PER STATISTICHE GENERALI ====

@stats_general_bp.route("/general")
@login_required
def general_stats():
    """
    Statistiche generali di tutti i laboratori dell'utente
    GET /stats/general
    """
    try:
        # Recupera tutti i laboratori dell'utente
        from app.services.roles import RoleService
        user_labs = RoleService.get_labs_for_user(current_user.id)
        
        # Statistiche aggregate per tutti i lab
        total_results = 0
        total_excellent = 0
        total_acceptable = 0 
        total_poor = 0
        lab_stats = []
        
        for lab, role in user_labs:
            # Statistiche per questo laboratorio
            lab_results = db.session.query(Result, ZScore).join(
                ZScore, Result.id == ZScore.result_id, isouter=True
            ).filter(Result.lab_code == lab.code).all()
            
            lab_total = len(lab_results)
            lab_excellent = sum(1 for _, z in lab_results if z and abs(z.z) < 2)
            lab_acceptable = sum(1 for _, z in lab_results if z and 2 <= abs(z.z) < 3)
            lab_poor = sum(1 for _, z in lab_results if z and abs(z.z) >= 3)
            
            # Calcola media z-score del lab
            z_scores = [z.z for _, z in lab_results if z]
            lab_mean_z = sum(z_scores) / len(z_scores) if z_scores else 0
            
            lab_stats.append({
                'lab': lab,
                'role': role,
                'total_results': lab_total,
                'excellent': lab_excellent,
                'acceptable': lab_acceptable,
                'poor': lab_poor,
                'mean_z_score': lab_mean_z,
                'performance_percent': (lab_excellent / lab_total * 100) if lab_total > 0 else 0
            })
            
            # Aggiungi ai totali
            total_results += lab_total
            total_excellent += lab_excellent
            total_acceptable += lab_acceptable
            total_poor += lab_poor
        
        # Statistiche aggregate
        aggregate_stats = {
            'total_labs': len(user_labs),
            'total_results': total_results,
            'total_excellent': total_excellent,
            'total_acceptable': total_acceptable,
            'total_poor': total_poor,
            'overall_performance': (total_excellent / total_results * 100) if total_results > 0 else 0
        }
        
        return render_template('stats/general_stats.html',
                             lab_stats=lab_stats,
                             aggregate_stats=aggregate_stats,
                             is_single_lab=False)
        
    except Exception as e:
        current_app.logger.error(f"Error loading general stats: {str(e)}")
        flash(f"Errore nel caricamento delle statistiche: {str(e)}", "danger")
        return redirect(url_for('main.dashboard'))


@stats_bp.route("/general")
@login_required
@lab_role_required("viewer")
def general_stats_lab(lab_code):
    """
    Statistiche generali per un singolo laboratorio
    GET /l/<lab_code>/stats/general
    """
    try:
        # Recupera il laboratorio
        lab = Lab.query.filter_by(code=lab_code).first_or_404()
        
        # Recupera il ruolo dell'utente per questo laboratorio
        user_role = None
        for lab_role in current_user.lab_roles:
            if lab_role.lab.code == lab_code:
                user_role = lab_role.role
                break
        
        # Statistiche dettagliate del laboratorio
        lab_results = db.session.query(Result, ZScore).join(
            ZScore, Result.id == ZScore.result_id, isouter=True
        ).filter(Result.lab_code == lab_code).all()
        
        total_results = len(lab_results)
        excellent = sum(1 for _, z in lab_results if z and abs(z.z) < 2)
        acceptable = sum(1 for _, z in lab_results if z and 2 <= abs(z.z) < 3)
        poor = sum(1 for _, z in lab_results if z and abs(z.z) >= 3)
        
        # Z-scores per analisi temporali
        z_scores = [z.z for _, z in lab_results if z]
        mean_z = sum(z_scores) / len(z_scores) if z_scores else 0
        
        # Statistiche per parametri
        parameter_stats = {}
        for result, z_score in lab_results:
            if z_score:
                param = result.parameter_code
                if param not in parameter_stats:
                    parameter_stats[param] = {'count': 0, 'z_values': []}
                parameter_stats[param]['count'] += 1
                parameter_stats[param]['z_values'].append(z_score.z)
        
        # Calcola medie per parametro
        for param in parameter_stats:
            z_values = parameter_stats[param]['z_values']
            parameter_stats[param]['mean_z'] = sum(z_values) / len(z_values)
            parameter_stats[param]['excellent'] = sum(1 for z in z_values if abs(z) < 2)
            parameter_stats[param]['performance'] = (parameter_stats[param]['excellent'] / len(z_values)) * 100
        
        lab_stats = [{
            'lab': lab,
            'role': user_role,
            'total_results': total_results,
            'excellent': excellent,
            'acceptable': acceptable,
            'poor': poor,
            'mean_z_score': mean_z,
            'performance_percent': (excellent / total_results * 100) if total_results > 0 else 0,
            'parameter_stats': parameter_stats
        }]
        
        aggregate_stats = {
            'total_labs': 1,
            'total_results': total_results,
            'total_excellent': excellent,
            'total_acceptable': acceptable,
            'total_poor': poor,
            'overall_performance': (excellent / total_results * 100) if total_results > 0 else 0
        }
        
        return render_template('stats/general_stats.html',
                             lab_stats=lab_stats,
                             aggregate_stats=aggregate_stats,
                             is_single_lab=True,
                             current_lab=lab)
        
    except Exception as e:
        current_app.logger.error(f"Error loading lab stats for {lab_code}: {str(e)}")
        flash(f"Errore nel caricamento delle statistiche: {str(e)}", "danger")
        return redirect(url_for('main.lab_hub', lab_code=lab_code))