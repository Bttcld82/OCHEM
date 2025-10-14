"""
API Routes per il modulo Statistics
Endpoint API separati per mantenere la leggibilità del codice
"""

from flask import request, jsonify, current_app
from flask_login import login_required
from app import db
from app.models import Result, Parameter, Technique, Cycle
from app.blueprints.auth.decorators import lab_role_required
from app.blueprints.stats.services_stats import get_control_chart_data
from app.blueprints.stats import stats_bp


@stats_bp.route("/api/chart-data")
@login_required
@lab_role_required("viewer")
def get_chart_data_api(lab_code):
    """
    API endpoint per ottenere i dati del grafico via AJAX
    
    Returns:
        JSON: Dati formattati per Plotly
    """
    try:
        # Parametri dalla query string
        parameter_codes = request.args.getlist('parameters[]') or [request.args.get('parameter')]
        parameter_codes = [p for p in parameter_codes if p]  # Rimuovi valori vuoti
        
        days_limit = request.args.get('days', None)
        days_limit = int(days_limit) if days_limit else 30
        
        technique_codes = request.args.getlist('techniques[]')
        cycle_codes = request.args.getlist('cycles[]')
        
        # Recupera i dati per il grafico con filtri multipli
        chart_data = get_control_chart_data(
            lab_code=lab_code, 
            parameter_codes=parameter_codes, 
            limit_days=days_limit,
            technique_codes=technique_codes,
            cycle_codes=cycle_codes
        )
        
        return jsonify({
            'success': True,
            'data': chart_data,
            'filters': {
                'parameters': parameter_codes,
                'days': days_limit,
                'techniques': technique_codes,
                'cycles': cycle_codes
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in chart data API for {lab_code}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500





@stats_bp.route("/api/filter-options")
@login_required
@lab_role_required("viewer")
def get_filter_options(lab_code):
    """
    API endpoint per ottenere le opzioni dei filtri disponibili
    
    Returns:
        JSON: Opzioni filtri con dipendenze
    """
    try:
        # Parametri filtro correnti dalla query string
        selected_parameters = request.args.getlist('parameters[]')
        selected_techniques = request.args.getlist('techniques[]')
        selected_cycles = request.args.getlist('cycles[]')
        
        # Ottieni tutti i parametri disponibili (sempre visibili)
        available_parameters = db.session.query(Result.parameter_code, Parameter.name).join(
            Parameter, Result.parameter_code == Parameter.code
        ).filter(Result.lab_code == lab_code).distinct().all()
        
        # Per tecniche e cicli: mostra solo quelli compatibili con i parametri selezionati
        techniques_query = db.session.query(Result.technique_code, Technique.name).join(
            Technique, Result.technique_code == Technique.code, isouter=True
        ).filter(Result.lab_code == lab_code, Result.technique_code.isnot(None))
        
        cycles_query = db.session.query(Result.cycle_code, Cycle.name).join(
            Cycle, Result.cycle_code == Cycle.code
        ).filter(Result.lab_code == lab_code)
        
        # Se sono selezionati parametri, filtra tecniche e cicli di conseguenza
        if selected_parameters:
            techniques_query = techniques_query.filter(Result.parameter_code.in_(selected_parameters))
            cycles_query = cycles_query.filter(Result.parameter_code.in_(selected_parameters))
        
        available_techniques = techniques_query.distinct().all()
        available_cycles = cycles_query.distinct().all()
        
        # Formatta le opzioni per il frontend
        parameters_options = [
            {'code': param[0], 'name': param[1] or param[0]} 
            for param in available_parameters
        ]
        
        techniques_options = [
            {'code': tech[0], 'name': tech[1] or tech[0]} 
            for tech in available_techniques
        ]
        
        cycles_options = [
            {'code': cycle[0], 'name': cycle[1] or cycle[0]} 
            for cycle in available_cycles
        ]
        
        return jsonify({
            'success': True,
            'options': {
                'parameters': parameters_options,
                'techniques': techniques_options,
                'cycles': cycles_options
            },
            'selected': {
                'parameters': selected_parameters,
                'techniques': selected_techniques,
                'cycles': selected_cycles
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting filter options for {lab_code}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stats_bp.route("/api/statistics")
@login_required
@lab_role_required("viewer")
def get_statistics_api(lab_code):
    """
    API endpoint per ottenere statistiche riassuntive con filtri
    
    Returns:
        JSON: Statistiche aggregate
    """
    try:
        from app.models import ZScore
        
        # Parametri filtro
        parameter_codes = request.args.getlist('parameters[]')
        technique_codes = request.args.getlist('techniques[]')
        cycle_codes = request.args.getlist('cycles[]')
        days_limit = request.args.get('days', None)
        
        # Base query per risultati con Z-scores
        results_query = db.session.query(Result, ZScore).join(
            ZScore, Result.id == ZScore.result_id
        ).filter(Result.lab_code == lab_code)
        
        # Applica filtri
        if parameter_codes:
            results_query = results_query.filter(Result.parameter_code.in_(parameter_codes))
        if technique_codes:
            results_query = results_query.filter(Result.technique_code.in_(technique_codes))
        if cycle_codes:
            results_query = results_query.filter(Result.cycle_code.in_(cycle_codes))
        
        if days_limit:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=int(days_limit))
            results_query = results_query.filter(Result.submitted_at >= cutoff_date)
        
        results_data = results_query.all()
        
        if not results_data:
            return jsonify({
                'success': True,
                'statistics': {
                    'total_results': 0,
                    'performance': {'excellent': 0, 'acceptable': 0, 'poor': 0},
                    'z_score_stats': {}
                }
            })
        
        z_scores = [float(z.z) for _, z in results_data]
        
        # Calcola statistiche performance
        excellent = sum(1 for z in z_scores if abs(z) < 2)
        acceptable = sum(1 for z in z_scores if 2 <= abs(z) < 3)
        poor = sum(1 for z in z_scores if abs(z) >= 3)
        
        statistics = {
            'total_results': len(results_data),
            'performance': {
                'excellent': excellent,
                'acceptable': acceptable, 
                'poor': poor,
                'excellent_pct': round((excellent / len(z_scores)) * 100, 1) if z_scores else 0,
                'acceptable_pct': round((acceptable / len(z_scores)) * 100, 1) if z_scores else 0,
                'poor_pct': round((poor / len(z_scores)) * 100, 1) if z_scores else 0
            },
            'z_score_stats': {
                'mean': round(sum(z_scores) / len(z_scores), 3) if z_scores else 0,
                'min': round(min(z_scores), 3) if z_scores else 0,
                'max': round(max(z_scores), 3) if z_scores else 0,
                'std_dev': round((sum((z - sum(z_scores)/len(z_scores))**2 for z in z_scores) / len(z_scores))**0.5, 3) if len(z_scores) > 1 else 0
            }
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting statistics for {lab_code}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stats_bp.route("/api/table-data")
@login_required
@lab_role_required("viewer")
def get_table_data_api(lab_code):
    """
    API endpoint per ottenere i dati della tabella risultati con informazioni collegate
    
    Returns:
        JSON: Lista dei risultati con dati delle tabelle collegate
    """
    try:
        from app.models import Parameter, Technique, Provider, ZScore
        from datetime import datetime, timedelta
        
        # Parametri filtro dalla query string
        parameter_codes = request.args.getlist('parameters[]')
        technique_codes = request.args.getlist('techniques[]')
        cycle_codes = request.args.getlist('cycles[]')
        days_limit = request.args.get('days', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Query base con JOIN per ottenere tutte le informazioni collegate
        query = db.session.query(
            Result.id,
            Result.measured_value,
            Result.uncertainty,
            Result.submitted_at,
            Result.notes,
            ZScore.z.label('z_score'),
            Parameter.name.label('parameter_name'),
            Parameter.code.label('parameter_code'),
            Technique.name.label('technique_name'),
            Technique.code.label('technique_code'),
            Cycle.name.label('cycle_name'),
            Cycle.code.label('cycle_code'),
            Provider.name.label('provider_name')
        ).join(
            ZScore, Result.id == ZScore.result_id
        ).join(
            Parameter, Result.parameter_code == Parameter.code
        ).join(
            Cycle, Result.cycle_code == Cycle.code
        ).join(
            Provider, Cycle.provider_id == Provider.id, isouter=True
        ).join(
            Technique, Result.technique_code == Technique.code, isouter=True
        ).filter(
            Result.lab_code == lab_code
        )
        
        # Applica filtri
        if parameter_codes:
            query = query.filter(Result.parameter_code.in_(parameter_codes))
        if technique_codes:
            query = query.filter(Result.technique_code.in_(technique_codes))
        if cycle_codes:
            query = query.filter(Result.cycle_code.in_(cycle_codes))
        if days_limit:
            cutoff_date = datetime.utcnow() - timedelta(days=int(days_limit))
            query = query.filter(Result.submitted_at >= cutoff_date)
        
        # Ordina per data di invio (più recenti per primi)
        query = query.order_by(Result.submitted_at.desc())
        
        # Paginazione
        total_count = query.count()
        results = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Formatta i risultati per la tabella
        table_data = []
        for row in results:
            # Determina la classe CSS del colore basata sul z-score
            z_score = float(row.z_score) if row.z_score else 0
            if abs(z_score) < 2:
                performance_class = 'success'
                performance_text = 'Eccellente'
            elif abs(z_score) < 3:
                performance_class = 'warning'
                performance_text = 'Accettabile'
            else:
                performance_class = 'danger'
                performance_text = 'Scarso'
            
            table_data.append({
                'id': row.id,
                'parameter_code': row.parameter_code,
                'parameter_name': row.parameter_name,
                'technique_code': row.technique_code or '-',
                'technique_name': row.technique_name or 'Non specificata',
                'cycle_code': row.cycle_code,
                'cycle_name': row.cycle_name,
                'provider_name': row.provider_name or 'Non specificato',
                'measured_value': float(row.measured_value) if row.measured_value else 0,
                'uncertainty': float(row.uncertainty) if row.uncertainty else None,
                'z_score': round(z_score, 3),
                'performance_class': performance_class,
                'performance_text': performance_text,
                'submitted_at': row.submitted_at.strftime('%d/%m/%Y %H:%M') if row.submitted_at else '-',
                'notes': row.notes or ''
            })
        
        return jsonify({
            'success': True,
            'data': table_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            },
            'filters': {
                'parameters': parameter_codes,
                'techniques': technique_codes,
                'cycles': cycle_codes,
                'days': days_limit
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting table data for {lab_code}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500