from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from decimal import Decimal

from app import db
from app.models import Lab, Cycle, CycleParameter, LabParticipation, Result, ZScore, Technique
from app.forms import ManualResultForm
from app.blueprints.auth.decorators import lab_role_required
from app.blueprints.dati import bp
from app.blueprints.stats.services_stats import recalculate_pt_stats


def _calculate_zscore(measured_value, xpt, sigma_pt):
    """Calcola z e sz2 per un singolo risultato."""
    z = float((float(measured_value) - float(xpt)) / float(sigma_pt))
    return z, z ** 2



# ===========================
# API HTMX: parametri di un ciclo
# ===========================

@bp.route("/<lab_code>/api/cycle-params")
@login_required
@lab_role_required("viewer")
def get_cycle_params(lab_code):
    """Restituisce le opzioni <option> per i parametri del ciclo scelto (HTMX)."""
    cycle_code = request.args.get("cycle_code", "")
    if not cycle_code:
        return '<option value="">— Seleziona prima il ciclo —</option>'
    cps = CycleParameter.query.filter_by(cycle_code=cycle_code).all()
    options = ['<option value="">— Seleziona parametro —</option>']
    for cp in cps:
        name = cp.parameter.name if cp.parameter else cp.parameter_code
        options.append(f'<option value="{cp.parameter_code}">{cp.parameter_code} - {name}</option>')
    return "\n".join(options)


# ===========================
# INSERIMENTO MANUALE RISULTATO
# ===========================

@bp.route("/<lab_code>/insert", methods=["GET", "POST"])
@login_required
@lab_role_required("analyst")
def result_insert(lab_code):
    """Form inserimento manuale di un risultato per un parametro del ciclo."""
    lab = Lab.query.filter_by(code=lab_code).first_or_404()
    selected_cycle = request.form.get("cycle_code") or request.args.get("cycle_code")
    form = ManualResultForm(lab_code=lab_code, cycle_code=selected_cycle)

    if form.validate_on_submit():
        cycle_code = form.cycle_code.data
        parameter_code = form.parameter_code.data
        measured_value = form.measured_value.data

        # Verifica CycleParameter (necessario per z-score)
        cp = CycleParameter.query.filter_by(cycle_code=cycle_code, parameter_code=parameter_code).first()
        if not cp:
            flash("Parametro non trovato per questo ciclo.", "danger")
            return redirect(request.url)
        if not cp.xpt or not cp.sigma_pt:
            flash("XPT o SigmaPT non definiti per questo parametro.", "danger")
            return redirect(request.url)

        # Verifica partecipazione lab al ciclo
        lp = LabParticipation.query.filter_by(lab_code=lab_code, cycle_code=cycle_code, status='active').first()
        if not lp:
            flash("Il laboratorio non è iscritto attivamente a questo ciclo.", "warning")
            return redirect(request.url)

        # Calcolo z-score
        try:
            z, sz2 = _calculate_zscore(measured_value, cp.xpt, cp.sigma_pt)
        except (ZeroDivisionError, ValueError):
            flash("Errore nel calcolo z-score: verifica XPT e SigmaPT del ciclo.", "danger")
            return redirect(request.url)

        # Salva Result
        result = Result(
            lab_code=lab_code,
            cycle_code=cycle_code,
            parameter_code=parameter_code,
            technique_code=form.technique_code.data or None,
            measured_value=measured_value,
            uncertainty=form.uncertainty.data or None,
            notes=form.notes.data or None,
            submitted_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(result)
        db.session.flush()

        # Salva ZScore
        zscore = ZScore(
            result_id=result.id,
            z=z,
            sz2=sz2,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(zscore)

        # Aggiorna PtStats
        recalculate_pt_stats(cycle_code, parameter_code, lab_code)

        db.session.commit()

        abs_z = abs(z)
        if abs_z < 2:
            perf = "Eccellente"
        elif abs_z < 3:
            perf = "Accettabile"
        else:
            perf = "Fuori controllo"
        flash(f"Risultato inserito. Z-score = {z:.3f} ({perf})", "success")
        return redirect(url_for("dati.result_list", lab_code=lab_code))

    return render_template("dati_insert.html", form=form, lab=lab, lab_code=lab_code, selected_cycle=selected_cycle)


# ===========================
# LISTA RISULTATI
# ===========================

@bp.route("/<lab_code>/results")
@login_required
@lab_role_required("viewer")
def result_list(lab_code):
    """Lista risultati inseriti manualmente per il laboratorio."""
    lab = Lab.query.filter_by(code=lab_code).first_or_404()
    cycle_filter = request.args.get("cycle", "")

    query = db.session.query(Result, ZScore).outerjoin(
        ZScore, Result.id == ZScore.result_id
    ).filter(Result.lab_code == lab_code)

    if cycle_filter:
        query = query.filter(Result.cycle_code == cycle_filter)

    results_data = query.order_by(Result.submitted_at.desc()).limit(200).all()

    # Cicli disponibili per filtro
    cycles = db.session.query(Result.cycle_code).filter_by(lab_code=lab_code).distinct().all()
    available_cycles = [c[0] for c in cycles if c[0]]

    return render_template("dati_results.html",
                           lab=lab,
                           lab_code=lab_code,
                           results_data=results_data,
                           available_cycles=available_cycles,
                           cycle_filter=cycle_filter)


# ===========================
# MODIFICA RISULTATO
# ===========================

@bp.route("/<lab_code>/results/<int:result_id>/edit", methods=["GET", "POST"])
@login_required
@lab_role_required("analyst")
def result_edit(lab_code, result_id):
    """Modifica un risultato esistente."""
    lab = Lab.query.filter_by(code=lab_code).first_or_404()
    result = Result.query.get_or_404(result_id)

    if result.lab_code != lab_code:
        flash("Non puoi modificare risultati di altri laboratori.", "danger")
        return redirect(url_for("dati.result_list", lab_code=lab_code))

    form = ManualResultForm(lab_code=lab_code, cycle_code=result.cycle_code, obj=result)
    # Preseleziona il ciclo e il parametro
    form.cycle_code.data = result.cycle_code
    form.parameter_code.choices = [
        (cp.parameter_code,
         f"{cp.parameter_code} - {cp.parameter.name if cp.parameter else cp.parameter_code}")
        for cp in CycleParameter.query.filter_by(cycle_code=result.cycle_code).all()
    ] or [('', '—')]
    form.parameter_code.data = result.parameter_code

    if form.validate_on_submit():
        cp = CycleParameter.query.filter_by(
            cycle_code=result.cycle_code, parameter_code=result.parameter_code
        ).first()
        if not cp or not cp.xpt or not cp.sigma_pt:
            flash("XPT o SigmaPT non disponibili per ricalcolare.", "danger")
            return redirect(request.url)

        measured_value = form.measured_value.data
        try:
            z, sz2 = _calculate_zscore(measured_value, cp.xpt, cp.sigma_pt)
        except (ZeroDivisionError, ValueError):
            flash("Errore nel calcolo z-score.", "danger")
            return redirect(request.url)

        result.measured_value = measured_value
        result.technique_code = form.technique_code.data or None
        result.uncertainty = form.uncertainty.data or None
        result.notes = form.notes.data or None
        result.updated_at = datetime.utcnow()

        zscore = ZScore.query.filter_by(result_id=result.id).first()
        if zscore:
            zscore.z = z
            zscore.sz2 = sz2
            zscore.updated_at = datetime.utcnow()
        else:
            db.session.add(ZScore(
                result_id=result.id, z=z, sz2=sz2,
                created_at=datetime.utcnow(), updated_at=datetime.utcnow()
            ))

        # Ricalcola PtStats dopo modifica
        recalculate_pt_stats(result.cycle_code, result.parameter_code, lab_code)

        db.session.commit()
        flash(f"Risultato aggiornato. Z-score = {z:.3f}", "success")
        return redirect(url_for("dati.result_list", lab_code=lab_code))

    return render_template("dati_edit.html", form=form, lab=lab, lab_code=lab_code, result=result)


# ===========================
# ELIMINA RISULTATO
# ===========================

@bp.route("/<lab_code>/results/<int:result_id>/delete", methods=["POST"])
@login_required
@lab_role_required("analyst")
def result_delete(lab_code, result_id):
    """Elimina un risultato e il relativo z-score."""
    result = Result.query.get_or_404(result_id)

    if result.lab_code != lab_code:
        flash("Non puoi eliminare risultati di altri laboratori.", "danger")
        return redirect(url_for("dati.result_list", lab_code=lab_code))

    # Salva dati per ricalcolo (prima della delete)
    cycle_code = result.cycle_code
    parameter_code = result.parameter_code

    # Elimina ZScore e Result
    ZScore.query.filter_by(result_id=result.id).delete()
    db.session.delete(result)
    db.session.flush()

    # Ricalcola PtStats sui z-score residui
    recalculate_pt_stats(cycle_code, parameter_code, lab_code)

    db.session.commit()
    flash("Risultato eliminato.", "success")
    return redirect(url_for("dati.result_list", lab_code=lab_code))
