from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import Technique, Parameter
from app.forms import TechniqueForm
from datetime import datetime
from .routes_main import admin_bp

# ===========================
# GESTIONE TECNICHE ANALITICHE
# ===========================

@admin_bp.route("/techniques")
def techniques_list():
    """Lista tecniche analitiche"""
    q = request.args.get("q", "").strip()
    
    query = Technique.query
    if q:
        query = query.filter((Technique.name.ilike(f"%{q}%")) | (Technique.code.ilike(f"%{q}%")))
    
    techniques = query.order_by(Technique.name.asc()).all()
    
    return render_template("techniques_list.html", techniques=techniques, q=q)

@admin_bp.route("/techniques/new", methods=["GET", "POST"])
def techniques_new():
    """Creazione nuova tecnica analitica"""
    form = TechniqueForm()
    
    if form.validate_on_submit():
        technique = Technique(
            code=form.code.data,
            name=form.name.data
        )
        db.session.add(technique)
        db.session.commit()
        flash("Tecnica analitica creata con successo.", "success")
        return redirect(url_for("admin_bp.techniques_list"))
    
    return render_template("techniques_form.html", form=form, technique=None)

@admin_bp.route("/techniques/<int:technique_id>/edit", methods=["GET", "POST"])
def techniques_edit(technique_id):
    """Modifica tecnica analitica esistente"""
    technique = Technique.query.get_or_404(technique_id)
    form = TechniqueForm(original_code=technique.code, obj=technique)
    
    if form.validate_on_submit():
        form.populate_obj(technique)
        technique.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Tecnica analitica aggiornata con successo.", "success")
        return redirect(url_for("admin_bp.techniques_list"))
    
    return render_template("techniques_form.html", form=form, technique=technique)

@admin_bp.route("/techniques/<int:technique_id>/delete", methods=["POST"])
def techniques_delete(technique_id):
    """Elimina tecnica analitica"""
    technique = Technique.query.get_or_404(technique_id)
    
    # Verifica se la tecnica è usata da parametri
    parameter_usage = Parameter.query.filter_by(technique_id=technique.id).count()
    
    if parameter_usage > 0:
        flash(f"Impossibile eliminare: tecnica usata da {parameter_usage} parametri.", "danger")
        return redirect(url_for("admin_bp.techniques_list"))
    
    db.session.delete(technique)
    db.session.commit()
    flash("Tecnica analitica eliminata con successo.", "success")
    return redirect(url_for("admin_bp.techniques_list"))