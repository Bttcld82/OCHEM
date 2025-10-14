from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import Provider
from app.forms import ProviderForm
from datetime import datetime
from .routes_main import admin_bp

# ===========================
# GESTIONE FORNITORI
# ===========================

@admin_bp.route("/providers")
def providers_list():
    """Lista fornitori"""
    q = request.args.get("q", "").strip()
    
    query = Provider.query
    if q:
        query = query.filter((Provider.name.ilike(f"%{q}%")) | (Provider.code.ilike(f"%{q}%")))
    
    providers = query.order_by(Provider.name.asc()).all()
    
    return render_template("providers_list.html", providers=providers, q=q)

@admin_bp.route("/providers/new", methods=["GET", "POST"])
def providers_new():
    """Creazione nuovo fornitore"""
    form = ProviderForm()
    
    if form.validate_on_submit():
        provider = Provider(
            code=form.code.data,
            name=form.name.data
        )
        db.session.add(provider)
        db.session.commit()
        flash("Fornitore creato con successo.", "success")
        return redirect(url_for("admin_bp.providers_list"))
    
    return render_template("providers_form.html", form=form, provider=None)

@admin_bp.route("/providers/<int:provider_id>/edit", methods=["GET", "POST"])
def providers_edit(provider_id):
    """Modifica fornitore esistente"""
    provider = Provider.query.get_or_404(provider_id)
    form = ProviderForm(original_code=provider.code, obj=provider)
    
    if form.validate_on_submit():
        form.populate_obj(provider)
        provider.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Fornitore aggiornato con successo.", "success")
        return redirect(url_for("admin_bp.providers_list"))
    
    return render_template("providers_form.html", form=form, provider=provider)

@admin_bp.route("/providers/<int:provider_id>/delete", methods=["POST"])
def providers_delete(provider_id):
    """Elimina fornitore"""
    provider = Provider.query.get_or_404(provider_id)
    
    # Verifica se il fornitore è usato (assumendo che ci possano essere relazioni future)
    # Per ora non ci sono relazioni, ma lasciamo la struttura per il futuro
    
    db.session.delete(provider)
    db.session.commit()
    flash("Fornitore eliminato con successo.", "success")
    return redirect(url_for("admin_bp.providers_list"))