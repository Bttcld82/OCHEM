from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import Parameter, Unit, Technique, CycleParameter, Result, Cycle
from app.forms import ParameterForm, UnitForm, TechniqueForm, SearchForm
from datetime import datetime
from .routes_main import admin_bp

# ===========================
# GESTIONE PARAMETRI
# ===========================

@admin_bp.route("/parameters")
def parameters_list():
    """Lista parametri"""
    q = request.args.get("q", "").strip()
    technique_id = request.args.get("technique_id")
    
    query = Parameter.query
    if q:
        query = query.filter((Parameter.name.ilike(f"%{q}%")) | (Parameter.code.ilike(f"%{q}%")))
    if technique_id:
        query = query.filter_by(technique_id=technique_id)
    
    parameters = query.order_by(Parameter.name.asc()).all()
    techniques = Technique.query.order_by(Technique.name.asc()).all()
    units = Unit.query.order_by(Unit.description.asc()).all()
    active_cycles = db.session.query(Cycle).filter_by(status="published").count()
    
    return render_template("params_list.html", 
                         parameters=parameters, 
                         q=q, 
                         techniques=techniques, 
                         units=units,
                         active_cycles=active_cycles)

@admin_bp.route("/parameters/new", methods=["GET", "POST"])
def parameters_new():
    """Creazione nuovo parametro"""
    form = ParameterForm()
    
    if form.validate_on_submit():
        parameter = Parameter(
            code=form.code.data,
            name=form.name.data,
            unit_code=form.unit_code.data,
            technique_id=form.technique_id.data if form.technique_id.data else None,
            matrix=form.matrix.data or None,
            min_value=form.min_value.data,
            max_value=form.max_value.data,
            precision_digits=form.precision_digits.data,
            description=form.description.data or None,
            active=form.active.data
        )
        db.session.add(parameter)
        db.session.commit()
        flash("Parametro creato con successo.", "success")
        return redirect(url_for("admin_bp.parameters_list"))
    
    # For GET request or form errors
    units = Unit.query.order_by(Unit.code.asc()).all()
    techniques = Technique.query.order_by(Technique.name.asc()).all()
    return render_template("params_form.html", form=form, parameter=None, units=units, techniques=techniques)

@admin_bp.route("/parameters/<int:parameter_id>/edit", methods=["GET", "POST"])
def parameters_edit(parameter_id):
    """Modifica parâmetro existente"""
    parameter = Parameter.query.get_or_404(parameter_id)
    form = ParameterForm(original_code=parameter.code, obj=parameter)
    
    if form.validate_on_submit():
        form.populate_obj(parameter)
        parameter.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Parametro aggiornato con successo.", "success")
        return redirect(url_for("admin_bp.parameters_list"))
    
    # For GET request or form errors
    units = Unit.query.order_by(Unit.code.asc()).all()
    techniques = Technique.query.order_by(Technique.name.asc()).all()
    return render_template("params_form.html", form=form, parameter=parameter, units=units, techniques=techniques)

@admin_bp.route("/parameters/<int:parameter_id>/delete", methods=["POST"])
def parameters_delete(parameter_id):
    """Elimina parametro"""
    parameter = Parameter.query.get_or_404(parameter_id)
    
    # Verifica se il parametro è usato in cicli o risultati
    cycle_usage = CycleParameter.query.filter_by(parameter_code=parameter.code).count()
    result_usage = Result.query.filter_by(parameter_code=parameter.code).count()
    
    if cycle_usage > 0 or result_usage > 0:
        flash(f"Impossibile eliminare: parametro usato in {cycle_usage} cicli e {result_usage} risultati.", "danger")
        return redirect(url_for("admin_bp.parameters_list"))
    
    db.session.delete(parameter)
    db.session.commit()
    flash("Parametro eliminato con successo.", "success")
    return redirect(url_for("admin_bp.parameters_list"))



