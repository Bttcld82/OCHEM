from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from app import db
from app.models import (Lab, User, Cycle, CycleParameter, DocFile, Parameter, 
                       Unit, Technique, Provider, LabParticipation, Result)
from datetime import datetime
import os

# Crea il blueprint admin secondo instruction_admin.md
admin_bp = Blueprint("admin_bp", __name__, )

# Per compatibilità con il codice esistente
bp = admin_bp

# Dashboard semplice con link
@bp.route("/")
def dashboard():
    labs_count = Lab.query.count()
    params_count = Parameter.query.count()
    return render_template("admin_dashboard.html", labs_count=labs_count, params_count=params_count)

# ---------- LAB ----------
@bp.route("/labs")
def labs_list():
    q = request.args.get("q", "").strip()
    query = Lab.query
    if q:
        query = query.filter((Lab.name.ilike(f"%{q}%")) | (Lab.code.ilike(f"%{q}%")))
    labs = query.order_by(Lab.name.asc()).all()
    return render_template("labs_list.html", labs=labs, q=q)

@bp.route("/labs/new", methods=["GET", "POST"])
def labs_new():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        code = (request.form.get("code") or "").strip() or None
        if not name:
            flash("Il nome è obbligatorio.", "danger")
            return redirect(url_for("admin.labs_new"))
        if code and Lab.query.filter_by(code=code).first():
            flash("Code già esistente.", "warning")
            return redirect(url_for("admin.labs_new"))
        db.session.add(Lab(name=name, code=code))
        db.session.commit()
        flash("Laboratorio creato.", "success")
        return redirect(url_for("admin.labs_list"))
    return render_template("labs_form.html", lab=None)

@bp.route("/labs/<int:lab_id>/edit", methods=["GET", "POST"])
def labs_edit(lab_id):
    lab = Lab.query.get_or_404(lab_id)
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        code = (request.form.get("code") or "").strip() or None
        if not name:
            flash("Il nome è obbligatorio.", "danger")
            return redirect(url_for("admin.labs_edit", lab_id=lab.id))
        if code and Lab.query.filter(Lab.id != lab.id, Lab.code == code).first():
            flash("Code già usato da un altro laboratorio.", "warning")
            return redirect(url_for("admin.labs_edit", lab_id=lab.id))
        lab.name, lab.code = name, code
        db.session.commit()
        flash("Laboratorio aggiornato.", "success")
        return redirect(url_for("admin.labs_list"))
    return render_template("labs_form.html", lab=lab)

@bp.route("/labs/<int:lab_id>/delete", methods=["POST"])
def labs_delete(lab_id):
    lab = Lab.query.get_or_404(lab_id)
    db.session.delete(lab)
    db.session.commit()
    flash("Laboratorio eliminato.", "success")
    return redirect(url_for("admin.labs_list"))

# ---------- PARAMETRO ----------
@bp.route("/params")
def params_list():
    q = request.args.get("q", "").strip()
    query = Parameter.query
    if q:
        query = query.filter((Parameter.name.ilike(f"%{q}%")) | (Parameter.code.ilike(f"%{q}%")))
    params = query.order_by(Parameter.code.asc()).all()
    return render_template("params_list.html", params=params, q=q)

@bp.route("/params/new", methods=["GET", "POST"])
def params_new():
    if request.method == "POST":
        codice = (request.form.get("codice") or "").strip()
        nome = (request.form.get("nome") or "").strip()
        unita = (request.form.get("unita") or "mg/L").strip()
        if not codice or not nome:
            flash("Codice e Nome sono obbligatori.", "danger")
            return redirect(url_for("admin.params_new"))
        if Parameter.query.filter_by(code=codice).first():
            flash("Codice parametro già esistente.", "warning")
            return redirect(url_for("admin.params_new"))
        db.session.add(Parameter(code=codice, name=nome, unit=unita))
        db.session.commit()
        flash("Parametro creato.", "success")
        return redirect(url_for("admin.params_list"))
    return render_template("params_form.html", parametro=None)

@bp.route("/params/<int:param_id>/edit", methods=["GET", "POST"])
def params_edit(param_id):
    parametro = Parameter.query.get_or_404(param_id)
    if request.method == "POST":
        codice = (request.form.get("codice") or "").strip()
        nome = (request.form.get("nome") or "").strip()
        unita = (request.form.get("unita") or "mg/L").strip()
        if not codice or not nome:
            flash("Codice e Nome sono obbligatori.", "danger")
            return redirect(url_for("admin.params_edit", param_id=parametro.id))
        if Parameter.query.filter(Parameter.id != parametro.id, Parameter.code == codice).first():
            flash("Codice parametro in uso su un altro record.", "warning")
            return redirect(url_for("admin.params_edit", param_id=parametro.id))
        parametro.codice, parametro.nome, parametro.unita = codice, nome, unita
        db.session.commit()
        flash("Parametro aggiornato.", "success")
        return redirect(url_for("admin.params_list"))
    return render_template("params_form.html", parametro=parametro)

@bp.route("/params/<int:param_id>/delete", methods=["POST"])
def params_delete(param_id):
    parametro = Parameter.query.get_or_404(param_id)
    db.session.delete(parametro)
    db.session.commit()
    flash("Parametro eliminato.", "success")
    return redirect(url_for("admin.params_list"))
