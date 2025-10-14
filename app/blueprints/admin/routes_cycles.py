from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import Cycle, CycleParameter, DocFile
from datetime import datetime
from .routes_main import admin_bp

# ===========================
# GESTIONE CICLI PT
# ===========================

@admin_bp.route("/cycles")
def cycles_list():
    """Lista tutti i cicli per amministrazione"""
    status_filter = request.args.get("status", "").strip()
    
    query = Cycle.query
    if status_filter:
        query = query.filter(Cycle.status == status_filter)
    
    cycles = query.order_by(Cycle.created_at.desc()).all()
    
    # Arricchisci con informazioni aggiuntive
    cycles_data = []
    for cycle in cycles:
        param_count = CycleParameter.query.filter_by(cycle_code=cycle.code).count()
        cycles_data.append({
            'cycle': cycle,
            'param_count': param_count
        })
    
    return render_template("cycles_list.html", cycles_data=cycles_data, status_filter=status_filter)

@admin_bp.route("/cycles/pending")
def cycles_pending():
    """Lista cicli in revisione"""
    cycles = Cycle.query.filter(Cycle.status == "pending_review").all()
    
    # Arricchisci con informazioni aggiuntive
    cycles_data = []
    for cycle in cycles:
        param_count = CycleParameter.query.filter_by(cycle_code=cycle.code).count()
        cycles_data.append({
            'cycle': cycle,
            'param_count': param_count
        })
    
    return render_template("cycles_pending.html", cycles=cycles_data)

@admin_bp.route("/cycles/<int:cycle_id>/review", methods=["GET", "POST"])
def cycle_review(cycle_id):
    """Revisione singolo ciclo"""
    cycle = Cycle.query.get_or_404(cycle_id)
    params = CycleParameter.query.filter_by(cycle_code=cycle.code).all()
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "approve":
            # Verifica che tutti i parametri abbiano XPT e SigmaPT
            missing_data = [p for p in params if not p.xpt or not p.sigma_pt]
            if missing_data:
                flash(f"Impossibile approvare: {len(missing_data)} parametri senza XPT/SigmaPT!", "danger")
                return redirect(url_for("admin_bp.cycle_review", cycle_id=cycle_id))
            
            cycle.status = "published"
            cycle.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f"Ciclo {cycle.code} pubblicato con successo.", "success")
            
        elif action == "reject":
            cycle.status = "rejected"
            cycle.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f"Ciclo {cycle.code} rigettato.", "warning")
            
        elif action == "request_changes":
            cycle.status = "changes_requested"
            cycle.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f"Ciclo {cycle.code}: richieste modifiche all'operatore.", "info")
        
        return redirect(url_for("admin_bp.cycles_pending"))
    
    # Controlla parametri con dati mancanti
    missing_pdf = [p for p in params if not p.xpt or not p.sigma_pt]
    if missing_pdf:
        flash(f"{len(missing_pdf)} parametri senza XPT o SigmaPT!", "warning")
    
    return render_template("cycle_review.html", cycle=cycle, params=params)

@admin_bp.route("/cycles/<int:cycle_id>/toggle_status", methods=["POST"])
def cycle_toggle_status(cycle_id):
    """Cambia stato del ciclo"""
    cycle = Cycle.query.get_or_404(cycle_id)
    new_status = request.form.get("new_status")
    
    valid_statuses = ["draft", "pending_review", "published", "rejected", "changes_requested"]
    if new_status not in valid_statuses:
        flash("Stato non valido.", "danger")
        return redirect(url_for("admin_bp.cycles_list"))
    
    cycle.status = new_status
    cycle.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f"Ciclo {cycle.code} aggiornato a stato '{new_status}'.", "success")
    return redirect(url_for("admin_bp.cycles_list"))

@admin_bp.route("/cycles/<int:id>/quick_approve", methods=["POST"])
def cycle_quick_approve(id):
    """Approvazione rapida ciclo dalla lista pending"""
    cycle = Cycle.query.get_or_404(id)
    
    if cycle.status != "pending_review":
        flash("Il ciclo non è in stato 'pending_review'.", "warning")
        return redirect(url_for("admin_bp.cycles_pending"))
    
    cycle.status = "published"
    cycle.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f"Ciclo {cycle.code} approvato rapidamente.", "success")
    return redirect(url_for("admin_bp.cycles_pending"))

@admin_bp.route("/cycles/<int:id>/quick_reject", methods=["POST"])
def cycle_quick_reject(id):
    """Rigetto rapido ciclo dalla lista pending"""
    cycle = Cycle.query.get_or_404(id)
    
    if cycle.status != "pending_review":
        flash("Il ciclo non è in stato 'pending_review'.", "warning")
        return redirect(url_for("admin_bp.cycles_pending"))
    
    cycle.status = "rejected"
    cycle.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f"Ciclo {cycle.code} rigettato.", "warning")
    return redirect(url_for("admin_bp.cycles_pending"))