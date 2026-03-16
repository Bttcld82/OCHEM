from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Matrix, Parameter
from app.forms import MatrixForm
from app.blueprints.auth.decorators import disclaimer_required, role_required
from datetime import datetime
from .routes_main import admin_bp


# ===========================
# GESTIONE MATRICI
# ===========================

@admin_bp.route("/matrices")
@login_required
@disclaimer_required
@role_required("admin")
def matrices_list():
    """Lista tutte le matrici"""
    q = request.args.get("q", "").strip()
    query = Matrix.query
    if q:
        query = query.filter(
            (Matrix.code.ilike(f"%{q}%")) | (Matrix.description.ilike(f"%{q}%"))
        )
    matrices = query.order_by(Matrix.code).all()
    return render_template("matrices_list.html", matrices=matrices, q=q)


@admin_bp.route("/matrices/new", methods=["GET", "POST"])
@login_required
@disclaimer_required
@role_required("admin")
def matrices_new():
    """Crea una nuova matrice"""
    form = MatrixForm()
    if form.validate_on_submit():
        matrix = Matrix(
            code=form.code.data.strip(),
            description=form.description.data.strip(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(matrix)
        db.session.commit()
        flash(f"Matrice '{matrix.code}' creata.", "success")
        return redirect(url_for("admin_bp.matrices_list"))
    return render_template("matrices_form.html", form=form, matrix=None)


@admin_bp.route("/matrices/<int:matrix_id>/edit", methods=["GET", "POST"])
@login_required
@disclaimer_required
@role_required("admin")
def matrices_edit(matrix_id):
    """Modifica una matrice"""
    matrix = Matrix.query.get_or_404(matrix_id)
    form = MatrixForm(original_code=matrix.code, obj=matrix)
    if form.validate_on_submit():
        matrix.code = form.code.data.strip()
        matrix.description = form.description.data.strip()
        matrix.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f"Matrice '{matrix.code}' aggiornata.", "success")
        return redirect(url_for("admin_bp.matrices_list"))
    return render_template("matrices_form.html", form=form, matrix=matrix)


@admin_bp.route("/matrices/<int:matrix_id>/delete", methods=["POST"])
@login_required
@disclaimer_required
@role_required("admin")
def matrices_delete(matrix_id):
    """Elimina una matrice"""
    matrix = Matrix.query.get_or_404(matrix_id)
    usage = Parameter.query.filter(Parameter.matrix == matrix.code).count()
    if usage > 0:
        flash(f"Impossibile eliminare: matrice usata in {usage} parametri.", "danger")
        return redirect(url_for("admin_bp.matrices_list"))
    db.session.delete(matrix)
    db.session.commit()
    flash(f"Matrice '{matrix.code}' eliminata.", "success")
    return redirect(url_for("admin_bp.matrices_list"))
