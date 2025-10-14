from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import DocFile, Cycle, Provider, UploadFile, JobLog
from datetime import datetime
from .routes_main import admin_bp

# ===========================
# GESTIONE DOCUMENTAZIONE
# ===========================

@admin_bp.route("/docs")
def docs_list():
    """Lista documenti"""
    q = request.args.get("q", "").strip()
    query = DocFile.query
    if q:
        query = query.filter((DocFile.filename.ilike(f"%{q}%")) | 
                           (DocFile.original_filename.ilike(f"%{q}%")))
    docs = query.order_by(DocFile.uploaded_at.desc()).all()
    return render_template("docs_list.html", docs=docs, q=q)

@admin_bp.route("/docs/<int:id>/preview")
def doc_preview(id):
    """Preview documento PDF"""
    # Verifichiamo che il documento esista
    DocFile.query.get_or_404(id)
    # Per ora ritorniamo un messaggio di non implementato
    flash("Funzione preview non ancora implementata.", "info")
    return redirect(url_for("admin_bp.docs_list"))

@admin_bp.route("/docs/<int:doc_id>/details")
def doc_details(doc_id):
    """Dettagli documento"""
    doc = DocFile.query.get_or_404(doc_id)
    return render_template("doc_details.html", doc=doc)

@admin_bp.route("/docs/<int:doc_id>/delete", methods=["POST"])
def docs_delete(doc_id):
    """Elimina documento"""
    doc = DocFile.query.get_or_404(doc_id)
    
    # Verifica se il documento è associato a cicli
    cycle_usage = Cycle.query.filter((Cycle.sample_doc_id == doc.id) |
                                   (Cycle.instructions_doc_id == doc.id) |
                                   (Cycle.results_doc_id == doc.id)).count()
    
    if cycle_usage > 0:
        flash(f"Impossibile eliminare: documento usato in {cycle_usage} cicli.", "danger")
        return redirect(url_for("admin_bp.docs_list"))
    
    db.session.delete(doc)
    db.session.commit()
    flash("Documento eliminato con successo.", "success")
    return redirect(url_for("admin_bp.docs_list"))

# ===========================
# FORNITORI
# ===========================

@admin_bp.route("/providers")
def providers_list():
    """Lista fornitori"""
    providers = Provider.query.order_by(Provider.name.asc()).all()
    return render_template("providers_list.html", providers=providers)

@admin_bp.route("/providers/new", methods=["GET", "POST"])
def providers_new():
    """Creazione nuovo fornitore"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip()
        contact_email = request.form.get("contact_email", "").strip()
        contact_phone = request.form.get("contact_phone", "").strip()
        website = request.form.get("website", "").strip()
        address = request.form.get("address", "").strip()
        
        if not name:
            flash("Il nome è obbligatorio.", "danger")
            return redirect(url_for("admin_bp.providers_new"))
        
        if code and Provider.query.filter_by(code=code).first():
            flash("Codice già esistente.", "warning")
            return redirect(url_for("admin_bp.providers_new"))
        
        provider = Provider(
            name=name,
            code=code or None,
            contact_email=contact_email or None,
            contact_phone=contact_phone or None,
            website=website or None,
            address=address or None
        )
        db.session.add(provider)
        db.session.commit()
        flash("Fornitore creato con successo.", "success")
        return redirect(url_for("admin_bp.providers_list"))
    
    return render_template("providers_form.html", provider=None)

@admin_bp.route("/providers/<int:provider_id>/edit", methods=["GET", "POST"])
def providers_edit(provider_id):
    """Modifica fornitore esistente"""
    provider = Provider.query.get_or_404(provider_id)
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip()
        contact_email = request.form.get("contact_email", "").strip()
        contact_phone = request.form.get("contact_phone", "").strip()
        website = request.form.get("website", "").strip()
        address = request.form.get("address", "").strip()
        
        if not name:
            flash("Il nome è obbligatorio.", "danger")
            return redirect(url_for("admin_bp.providers_edit", provider_id=provider.id))
        
        if code and Provider.query.filter(Provider.id != provider.id, Provider.code == code).first():
            flash("Codice già usato da un altro fornitore.", "warning")
            return redirect(url_for("admin_bp.providers_edit", provider_id=provider.id))
        
        provider.name = name
        provider.code = code or None
        provider.contact_email = contact_email or None
        provider.contact_phone = contact_phone or None
        provider.website = website or None
        provider.address = address or None
        provider.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Fornitore aggiornato con successo.", "success")
        return redirect(url_for("admin_bp.providers_list"))
    
    return render_template("providers_form.html", provider=provider)

# ===========================
# FILE UPLOAD E JOB LOG
# ===========================

@admin_bp.route("/uploads")
def uploads_list():
    """Lista upload files"""
    uploads = UploadFile.query.order_by(UploadFile.uploaded_at.desc()).all()
    return render_template("uploads_list.html", uploads=uploads)

@admin_bp.route("/uploads/<int:upload_id>/details")
def upload_details(upload_id):
    """Dettagli upload"""
    upload = UploadFile.query.get_or_404(upload_id)
    return render_template("upload_details.html", upload=upload)

@admin_bp.route("/jobs")
def jobs_list():
    """Lista job log"""
    jobs = JobLog.query.order_by(JobLog.timestamp.desc()).all()
    return render_template("jobs_list.html", jobs=jobs)

@admin_bp.route("/jobs/<int:job_id>/details")
def job_details(job_id):
    """Dettagli job"""
    job = JobLog.query.get_or_404(job_id)
    return render_template("job_details.html", job=job)