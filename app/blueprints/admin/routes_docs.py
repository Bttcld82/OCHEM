import os
from flask import render_template, request, redirect, url_for, flash, send_from_directory, current_app, abort
from flask_login import login_required
from app import db
from app.models import DocFile, CycleDoc, UploadFile, JobLog
from app.blueprints.auth.decorators import disclaimer_required, role_required
from .routes_main import admin_bp

# ===========================
# GESTIONE DOCUMENTAZIONE
# ===========================

@admin_bp.route("/docs")
@login_required
@disclaimer_required
@role_required("admin")
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
@login_required
@disclaimer_required
@role_required("admin")
def doc_preview(id):
    """Serve il file PDF direttamente al browser (apre inline in nuova tab)."""
    doc = DocFile.query.get_or_404(id)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, doc.filename)
    if not os.path.isfile(file_path):
        flash(f"File '{doc.original_filename}' non trovato sul server.", "danger")
        return redirect(url_for("admin_bp.docs_list"))
    return send_from_directory(
        upload_folder,
        doc.filename,
        mimetype=doc.mime_type,
        as_attachment=False,
        download_name=doc.original_filename,
    )

@admin_bp.route("/docs/<int:doc_id>/details")
@login_required
@disclaimer_required
@role_required("admin")
def doc_details(doc_id):
    """Dettagli documento"""
    doc = DocFile.query.get_or_404(doc_id)
    return render_template("doc_details.html", doc=doc)

@admin_bp.route("/docs/<int:doc_id>/delete", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def docs_delete(doc_id):
    """Elimina documento"""
    doc = DocFile.query.get_or_404(doc_id)
    
    # Verifica se il documento è associato a cicli
    cycle_usage = CycleDoc.query.filter_by(doc_id=doc.id).count()
    
    if cycle_usage > 0:
        flash(f"Impossibile eliminare: documento usato in {cycle_usage} cicli.", "danger")
        return redirect(url_for("admin_bp.docs_list"))
    
    db.session.delete(doc)
    db.session.commit()
    flash("Documento eliminato con successo.", "success")
    return redirect(url_for("admin_bp.docs_list"))



# ===========================
# FILE UPLOAD E JOB LOG
# ===========================

@admin_bp.route("/uploads")
@login_required
@disclaimer_required
@role_required("admin")
def uploads_list():
    """Lista upload files"""
    uploads = UploadFile.query.order_by(UploadFile.uploaded_at.desc()).all()
    return render_template("uploads_list.html", uploads=uploads)

@admin_bp.route("/uploads/<int:upload_id>/details")
@login_required
@disclaimer_required
@role_required("admin")
def upload_details(upload_id):
    """Dettagli upload"""
    upload = UploadFile.query.get_or_404(upload_id)
    return render_template("upload_details.html", upload=upload)

@admin_bp.route("/jobs")
@login_required
@disclaimer_required
@role_required("admin")
def jobs_list():
    """Lista job log"""
    jobs = JobLog.query.order_by(JobLog.started_at.desc()).all()
    return render_template("jobs_list.html", jobs=jobs)

@admin_bp.route("/jobs/<int:job_id>/details")
@login_required
@disclaimer_required
@role_required("admin")
def job_details(job_id):
    """Dettagli job"""
    job = JobLog.query.get_or_404(job_id)
    return render_template("job_details.html", job=job)