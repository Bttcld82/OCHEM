from flask import render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required
from app import db
from app.models import Cycle, CycleParameter, DocFile, CycleDoc, LabParticipation, Lab, Parameter, Provider, Result
from datetime import date as _date
from app.forms import CycleForm, CycleParameterForm, LabParticipationForm, DocUploadForm
from app.blueprints.auth.decorators import disclaimer_required, role_required
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import os
from .routes_main import admin_bp

# ===========================
# GESTIONE CICLI PT
# ===========================

@admin_bp.route("/cycles")
@login_required
@disclaimer_required
@role_required("admin")
def cycles_list():
    """Lista tutti i cicli per amministrazione"""
    status_filter = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()
    provider_id_filter = request.args.get("provider_id", "").strip()

    query = Cycle.query
    if status_filter:
        query = query.filter(Cycle.status == status_filter)
    if q:
        query = query.filter(Cycle.code.ilike(f"%{q}%"))
    if provider_id_filter:
        query = query.filter(Cycle.provider_id == int(provider_id_filter))

    cycles = query.order_by(Cycle.created_at.desc()).all()

    # Arricchisci con informazioni aggiuntive
    cycles_data = []
    for cycle in cycles:
        param_count = CycleParameter.query.filter_by(cycle_code=cycle.code).count()
        cycles_data.append({
            'cycle': cycle,
            'param_count': param_count
        })

    providers = Provider.query.order_by(Provider.name).all()
    return render_template("cycles_list.html", cycles_data=cycles_data, status_filter=status_filter, providers=providers)


@admin_bp.route("/cycles/bulk_assign_provider", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycles_bulk_assign_provider():
    """Assegna un provider a più cicli selezionati"""
    cycle_ids = request.form.getlist("cycle_ids")
    provider_id = request.form.get("bulk_provider_id", "").strip()

    if not cycle_ids:
        flash("Nessun ciclo selezionato.", "warning")
        return redirect(url_for("admin_bp.cycles_list"))

    provider = Provider.query.get(int(provider_id)) if provider_id else None

    updated = 0
    for cid in cycle_ids:
        cycle = Cycle.query.get(int(cid))
        if cycle:
            cycle.provider_id = provider.id if provider else None
            cycle.updated_at = datetime.utcnow()
            updated += 1

    db.session.commit()
    provider_name = provider.name if provider else "nessuno"
    flash(f"Provider '{provider_name}' assegnato a {updated} cicli.", "success")
    return redirect(url_for("admin_bp.cycles_list"))

@admin_bp.route("/cycles/pending")
@login_required
@disclaimer_required
@role_required("admin")
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
    
    today = datetime.utcnow().date()
    return render_template("cycles_pending.html", cycles=cycles, today=today)

@admin_bp.route("/cycles/<int:cycle_id>/review", methods=["GET", "POST"])
@login_required
@disclaimer_required
@role_required("admin")
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
@login_required
@disclaimer_required
@role_required("admin")
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
@login_required
@disclaimer_required
@role_required("admin")
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
@login_required
@disclaimer_required
@role_required("admin")
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


# ===========================
# CRUD COMPLETO CICLI
# ===========================

@admin_bp.route("/cycles/new", methods=["GET", "POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_create():
    """Crea un nuovo ciclo PT"""
    form = CycleForm()
    if form.validate_on_submit():
        cycle = Cycle(
            code=form.code.data.strip(),
            name=form.name.data.strip(),
            status=form.status.data,
            provider_id=form.provider_id.data if form.provider_id.data else None,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(cycle)
        db.session.commit()
        flash(f"Ciclo {cycle.code} creato con successo.", "success")
        return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle.id))
    return render_template("cycle_form.html", form=form, cycle=None)


@admin_bp.route("/cycles/<int:cycle_id>/edit", methods=["GET", "POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_edit(cycle_id):
    """Modifica un ciclo esistente"""
    cycle = Cycle.query.get_or_404(cycle_id)
    form = CycleForm(original_code=cycle.code, obj=cycle)
    if form.validate_on_submit():
        cycle.code = form.code.data.strip()
        cycle.name = form.name.data.strip()
        cycle.status = form.status.data
        cycle.provider_id = form.provider_id.data if form.provider_id.data else None
        cycle.start_date = form.start_date.data
        cycle.end_date = form.end_date.data
        cycle.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f"Ciclo {cycle.code} aggiornato.", "success")
        return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle.id))
    return render_template("cycle_form.html", form=form, cycle=cycle)


@admin_bp.route("/cycles/<int:cycle_id>/delete", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_delete(cycle_id):
    """Elimina un ciclo (solo se senza partecipazioni o risultati)"""
    cycle = Cycle.query.get_or_404(cycle_id)
    participations = LabParticipation.query.filter_by(cycle_code=cycle.code).count()
    results = Result.query.filter_by(cycle_code=cycle.code).count()
    if participations > 0 or results > 0:
        flash(f"Impossibile eliminare: il ciclo ha {participations} partecipazioni e {results} risultati.", "danger")
        return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))
    # Elimina cascade: CycleParameter, CycleDoc
    CycleParameter.query.filter_by(cycle_code=cycle.code).delete()
    for cd in CycleDoc.query.filter_by(cycle_code=cycle.code).all():
        db.session.delete(cd)
    db.session.delete(cycle)
    db.session.commit()
    flash(f"Ciclo {cycle.code} eliminato.", "success")
    return redirect(url_for("admin_bp.cycles_list"))


@admin_bp.route("/cycles/<int:cycle_id>/detail")
@login_required
@disclaimer_required
@role_required("admin")
def cycle_detail(cycle_id):
    """Hub admin del ciclo: info, parametri, laboratori, documenti"""
    cycle = Cycle.query.get_or_404(cycle_id)
    params = CycleParameter.query.filter_by(cycle_code=cycle.code).all()
    participations = LabParticipation.query.filter_by(cycle_code=cycle.code).all()
    cycle_docs = CycleDoc.query.filter_by(cycle_code=cycle.code).all()
    param_form = CycleParameterForm()
    lab_form = LabParticipationForm()
    doc_form = DocUploadForm()
    # Rimuovi lab già iscritti dalle scelte
    existing_lab_codes = {p.lab_code for p in participations}
    lab_form.lab_code.choices = [c for c in lab_form.lab_code.choices if c[0] not in existing_lab_codes]
    # Rimuovi parametri già aggiunti dalle scelte
    existing_param_codes = {p.parameter_code for p in params}
    param_form.parameter_code.choices = [c for c in param_form.parameter_code.choices if c[0] not in existing_param_codes]
    return render_template("cycle_detail.html",
                           cycle=cycle,
                           params=params,
                           participations=participations,
                           cycle_docs=cycle_docs,
                           param_form=param_form,
                           lab_form=lab_form,
                           doc_form=doc_form)


# ===========================
# GESTIONE PARAMETRI DEL CICLO
# ===========================

@admin_bp.route("/cycles/<int:cycle_id>/parameters/add", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_param_add(cycle_id):
    cycle = Cycle.query.get_or_404(cycle_id)
    if cycle.status == "published":
        flash("Non è possibile modificare i parametri di un ciclo pubblicato.", "warning")
        return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))
    form = CycleParameterForm()
    if form.validate_on_submit():
        existing = CycleParameter.query.filter_by(cycle_code=cycle.code, parameter_code=form.parameter_code.data).first()
        if existing:
            flash("Parametro già presente in questo ciclo.", "warning")
        else:
            cp = CycleParameter(
                cycle_code=cycle.code,
                parameter_code=form.parameter_code.data,
                xpt=form.xpt.data,
                sigma_pt=form.sigma_pt.data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(cp)
            db.session.commit()
            flash(f"Parametro {form.parameter_code.data} aggiunto.", "success")
    else:
        for field, errors in form.errors.items():
            for e in errors:
                flash(f"{field}: {e}", "danger")
    return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))


@admin_bp.route("/cycles/<int:cycle_id>/parameters/<int:cp_id>/edit", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_param_edit(cycle_id, cp_id):
    cycle = Cycle.query.get_or_404(cycle_id)
    cp = CycleParameter.query.get_or_404(cp_id)
    if cycle.status == "published":
        flash("Non è possibile modificare i parametri di un ciclo pubblicato.", "warning")
        return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))
    try:
        cp.xpt = float(request.form.get("xpt", cp.xpt))
        cp.sigma_pt = float(request.form.get("sigma_pt", cp.sigma_pt))
        cp.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f"Valori {cp.parameter_code} aggiornati.", "success")
    except (ValueError, TypeError):
        flash("Valori non validi per XPT o Sigma PT.", "danger")
    return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))


@admin_bp.route("/cycles/<int:cycle_id>/parameters/<int:cp_id>/delete", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_param_delete(cycle_id, cp_id):
    cycle = Cycle.query.get_or_404(cycle_id)
    cp = CycleParameter.query.get_or_404(cp_id)
    if cycle.status == "published":
        flash("Non è possibile rimuovere parametri da un ciclo pubblicato.", "warning")
        return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))
    db.session.delete(cp)
    db.session.commit()
    flash(f"Parametro {cp.parameter_code} rimosso dal ciclo.", "success")
    return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))


# ===========================
# GESTIONE LABORATORI DEL CICLO
# ===========================

@admin_bp.route("/cycles/<int:cycle_id>/labs/add", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_lab_add(cycle_id):
    cycle = Cycle.query.get_or_404(cycle_id)
    form = LabParticipationForm()
    if form.validate_on_submit():
        existing = LabParticipation.query.filter_by(cycle_code=cycle.code, lab_code=form.lab_code.data).first()
        if existing:
            flash("Laboratorio già iscritto a questo ciclo.", "warning")
        else:
            lp = LabParticipation(
                cycle_code=cycle.code,
                lab_code=form.lab_code.data,
                status=form.status.data,
                registered_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(lp)
            db.session.commit()
            flash(f"Laboratorio {form.lab_code.data} iscritto al ciclo.", "success")
    else:
        for field, errors in form.errors.items():
            for e in errors:
                flash(f"{field}: {e}", "danger")
    return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))


@admin_bp.route("/cycles/<int:cycle_id>/labs/<int:lp_id>/remove", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_lab_remove(cycle_id, lp_id):
    lp = LabParticipation.query.get_or_404(lp_id)
    lab_code = lp.lab_code
    db.session.delete(lp)
    db.session.commit()
    flash(f"Laboratorio {lab_code} rimosso dal ciclo.", "success")
    return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))


# ===========================
# GESTIONE DOCUMENTI DEL CICLO
# ===========================

def _get_doc_upload_path():
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    doc_path = os.path.join(upload_folder, "docs")
    os.makedirs(doc_path, exist_ok=True)
    return doc_path


@admin_bp.route("/cycles/<int:cycle_id>/docs/upload", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_doc_upload(cycle_id):
    cycle = Cycle.query.get_or_404(cycle_id)
    form = DocUploadForm()
    if form.validate_on_submit():
        f = form.doc_file.data
        original_filename = secure_filename(f.filename)
        ext = os.path.splitext(original_filename)[1]
        unique_filename = uuid.uuid4().hex + ext
        save_path = os.path.join(_get_doc_upload_path(), unique_filename)
        f.save(save_path)
        file_size = os.path.getsize(save_path)
        doc = DocFile(
            filename=unique_filename,
            original_filename=original_filename,
            file_size=file_size,
            mime_type=f.content_type or "application/octet-stream",
            uploaded_at=datetime.utcnow(),
        )
        db.session.add(doc)
        db.session.flush()
        cd = CycleDoc(
            cycle_code=cycle.code,
            doc_id=doc.id,
            doc_type=form.doc_type.data,
            created_at=datetime.utcnow(),
        )
        db.session.add(cd)
        db.session.commit()
        flash(f"Documento '{original_filename}' caricato.", "success")
    else:
        for field, errors in form.errors.items():
            for e in errors:
                flash(f"{field}: {e}", "danger")
    return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))


@admin_bp.route("/cycles/<int:cycle_id>/docs/<int:cd_id>/delete", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_doc_delete(cycle_id, cd_id):
    cd = CycleDoc.query.get_or_404(cd_id)
    doc = cd.doc
    db.session.delete(cd)
    # Elimina il DocFile solo se non usato altrove
    if CycleDoc.query.filter_by(doc_id=doc.id).count() == 0:
        try:
            filepath = os.path.join(_get_doc_upload_path(), doc.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        db.session.delete(doc)
    db.session.commit()
    flash("Documento eliminato.", "success")
    return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))


@admin_bp.route("/cycles/<int:cycle_id>/report.pdf")
@login_required
@disclaimer_required
@role_required("admin")
def cycle_report_pdf(cycle_id):
    """Scarica il report PDF completo del ciclo (dati nominali, solo admin)"""
    from app.services.report_generator import generate_cycle_report_pdf
    cycle = Cycle.query.get_or_404(cycle_id)
    buffer = generate_cycle_report_pdf(cycle_id, admin_view=True)
    filename = f'report_PT_{cycle.code}_{_date.today()}.pdf'
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')


@admin_bp.route("/cycles/<int:cycle_id>/recalculate-consensus", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def cycle_recalculate_consensus(cycle_id):
    """Ricalcola statistiche consenso cross-lab (ISO 13528 Annex C) per tutti i parametri del ciclo"""
    from app.blueprints.stats.services_stats import calculate_cycle_consensus_stats

    cycle = Cycle.query.get_or_404(cycle_id)
    params = CycleParameter.query.filter_by(cycle_code=cycle.code).all()

    if not params:
        flash("Nessun parametro configurato per questo ciclo.", "warning")
        return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))

    results = []
    for cp in params:
        res = calculate_cycle_consensus_stats(cycle.code, cp.parameter_code)
        results.append((cp.parameter_code, res))

    ok = [r for _, r in results if 'error' not in r]
    errors = [f"{p}: {r['error']}" for p, r in results if 'error' in r]
    warnings = [f"{p}: {r['warning']}" for p, r in results if r.get('warning')]

    if ok:
        flash(
            f"Statistiche consenso ricalcolate per {len(ok)} parametro/i. "
            f"XPT robusto e sigma robusto aggiornati in CycleParameter.",
            "success"
        )
    for w in warnings:
        flash(w, "warning")
    for e in errors:
        flash(e, "danger")

    return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))


@admin_bp.route("/cycles/<int:cycle_id>/docs/<int:doc_id>/download")
@login_required
@disclaimer_required
@role_required("admin")
def cycle_doc_download(cycle_id, doc_id):
    doc = DocFile.query.get_or_404(doc_id)
    filepath = os.path.join(_get_doc_upload_path(), doc.filename)
    if not os.path.exists(filepath):
        flash("File non trovato sul server.", "danger")
        return redirect(url_for("admin_bp.cycle_detail", cycle_id=cycle_id))
    return send_file(filepath, as_attachment=True, download_name=doc.original_filename)