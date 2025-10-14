from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import Unit, Parameter
from app.forms import UnitForm
from datetime import datetime
from .routes_main import admin_bp

# ===========================
# GESTIONE UNITÀ DI MISURA
# ===========================

@admin_bp.route("/units")
def units_list():
    """Lista unità di misura"""
    q = request.args.get("q", "").strip()
    
    query = Unit.query
    if q:
        query = query.filter((Unit.description.ilike(f"%{q}%")) | (Unit.code.ilike(f"%{q}%")))
    
    units = query.order_by(Unit.description.asc()).all()
    
    return render_template("units_list.html", units=units, q=q)

@admin_bp.route("/units/new", methods=["GET", "POST"])
def units_new():
    """Creazione nuova unità di misura"""
    form = UnitForm()
    
    if form.validate_on_submit():
        unit = Unit(
            code=form.code.data,
            description=form.name.data  # name field maps to description in DB
        )
        db.session.add(unit)
        db.session.commit()
        flash("Unità di misura creata con successo.", "success")
        return redirect(url_for("admin_bp.units_list"))
    
    return render_template("units_form.html", form=form, unit=None)

@admin_bp.route("/units/<int:unit_id>/edit", methods=["GET", "POST"])
def units_edit(unit_id):
    """Modifica unità di misura esistente"""
    unit = Unit.query.get_or_404(unit_id)
    form = UnitForm(original_code=unit.code, obj=unit)
    
    # Map description to name field for form
    form.name.data = unit.description
    
    if form.validate_on_submit():
        unit.code = form.code.data
        unit.description = form.name.data
        unit.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Unità di misura aggiornata con successo.", "success")
        return redirect(url_for("admin_bp.units_list"))
    
    return render_template("units_form.html", form=form, unit=unit)

@admin_bp.route("/units/<int:unit_id>/delete", methods=["POST"])
def units_delete(unit_id):
    """Elimina unità di misura"""
    unit = Unit.query.get_or_404(unit_id)
    
    # Verifica se l'unità è usata da parametri
    parameter_usage = Parameter.query.filter_by(unit_code=unit.code).count()
    
    if parameter_usage > 0:
        flash(f"Impossibile eliminare: unità usata da {parameter_usage} parametri.", "danger")
        return redirect(url_for("admin_bp.units_list"))
    
    db.session.delete(unit)
    db.session.commit()
    flash("Unità di misura eliminata con successo.", "success")
    return redirect(url_for("admin_bp.units_list"))