"""
Generatore report PDF per cicli PT — OCHEM
Conforme ISO 13528 §7.4 e ACCREDIA RT-25 §4.4.3

Due modalità:
  admin_view=True  → tutti i laboratori con dati nominali
  admin_view=False → solo i dati del lab_code + statistiche aggregate anonimizzate
"""
from io import BytesIO
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)

from app.models import Cycle, CycleParameter, PtStats, Result, Lab


# ── Costanti colori OCHEM ───────────────────────────────────────────────────
_BLUE   = colors.HexColor('#003366')
_GREEN  = colors.HexColor('#1a7a1a')
_ORANGE = colors.HexColor('#cc7700')
_RED    = colors.HexColor('#cc0000')
_LGREY  = colors.HexColor('#f2f2f2')


def _perf_label(z) -> tuple[str, object]:
    """Restituisce (etichetta, colore) per un valore z."""
    if z is None:
        return 'N/D', colors.grey
    az = abs(float(z))
    if az <= 2.0:
        return 'Eccellente', _GREEN
    if az <= 3.0:
        return 'Accettabile', _ORANGE
    return 'Fuori controllo', _RED


def _fmt(val, decimals=4) -> str:
    if val is None:
        return '—'
    try:
        return f'{float(val):.{decimals}f}'
    except (TypeError, ValueError):
        return '—'


def generate_cycle_report_pdf(
    cycle_id: int,
    admin_view: bool = True,
    lab_code: str = None,
) -> BytesIO:
    """
    Genera il PDF per un ciclo PT e restituisce un BytesIO pronto per send_file.

    Args:
        cycle_id:    ID del ciclo (Cycle.id)
        admin_view:  True = report nominale completo; False = report del singolo lab
        lab_code:    Obbligatorio quando admin_view=False
    """
    cycle = Cycle.query.get_or_404(cycle_id)
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=f'Report PT {cycle.code}',
        author='OCHEM',
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'OchemTitle', parent=styles['Title'],
        textColor=_BLUE, spaceAfter=4,
    )
    h2_style = ParagraphStyle(
        'OchemH2', parent=styles['Heading2'],
        textColor=_BLUE, spaceBefore=12, spaceAfter=4,
    )
    small_style = ParagraphStyle(
        'OchemSmall', parent=styles['Normal'],
        fontSize=8, textColor=colors.grey,
    )
    caption_style = ParagraphStyle(
        'OchemCaption', parent=styles['Normal'],
        fontSize=9, textColor=_BLUE, alignment=TA_CENTER,
    )

    story = []

    # ── Intestazione ────────────────────────────────────────────────────────
    story.append(Paragraph('OCHEM — Report Ciclo PT', title_style))
    story.append(Paragraph(f'{cycle.name}  ({cycle.code})', styles['Heading2']))

    meta_rows = [
        ['Stato ciclo', cycle.status],
        ['Provider', cycle.provider.name if cycle.provider else '—'],
        ['Data inizio', cycle.start_date.strftime('%d/%m/%Y') if cycle.start_date else '—'],
        ['Data fine', cycle.end_date.strftime('%d/%m/%Y') if cycle.end_date else '—'],
        ['Data generazione', date.today().strftime('%d/%m/%Y')],
    ]
    if not admin_view and lab_code:
        lab = Lab.query.filter_by(code=lab_code).first()
        meta_rows.append(['Laboratorio', f'{lab.name} ({lab_code})' if lab else lab_code])

    meta_table = Table(meta_rows, colWidths=[4 * cm, 13 * cm])
    meta_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, _LGREY]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width='100%', color=_BLUE, spaceAfter=8))

    # ── Sezione per ogni parametro del ciclo ────────────────────────────────
    cycle_params = CycleParameter.query.filter_by(cycle_code=cycle.code).order_by(
        CycleParameter.parameter_code
    ).all()

    if not cycle_params:
        story.append(Paragraph('Nessun parametro configurato per questo ciclo.', styles['Normal']))
    else:
        for cp in cycle_params:
            param_name = cp.parameter.name if cp.parameter else cp.parameter_code

            # Header parametro
            story.append(Paragraph(
                f'Parametro: {cp.parameter_code} — {param_name}',
                h2_style,
            ))

            # Sub-tabella valori di riferimento
            ref_data = [
                ['XPT (valore assegnato)', _fmt(cp.xpt)],
                ['SigmaPT', _fmt(cp.sigma_pt)],
            ]
            if cp.xpt_robust is not None:
                ref_data.append(['XPT robusto (ISO 13528 Annex C)', _fmt(cp.xpt_robust)])
            if cp.sigma_pt_robust is not None:
                ref_data.append(['Sigma robusto', _fmt(cp.sigma_pt_robust)])

            ref_table = Table(ref_data, colWidths=[8 * cm, 9 * cm])
            ref_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, _LGREY]),
            ]))
            story.append(ref_table)
            story.append(Spacer(1, 0.25 * cm))

            # Tabella risultati
            if admin_view:
                _build_admin_param_table(story, cycle.code, cp.parameter_code, styles)
            else:
                _build_lab_param_table(story, cycle.code, cp.parameter_code, lab_code, styles)

            story.append(Spacer(1, 0.5 * cm))

    # ── Footer ──────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', color=colors.lightgrey, spaceBefore=8))
    story.append(Paragraph(
        f'Report generato da OCHEM il {date.today()} — '
        f'Conforme ISO 13528 §7.4 e ACCREDIA RT-25 §4.4.3',
        small_style,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ── Helper: tabella risultati admin (nominale) ──────────────────────────────

def _build_admin_param_table(story, cycle_code, parameter_code, styles):
    """Tabella completa con tutti i laboratori (vista admin)."""
    pt_records = PtStats.query.filter_by(
        cycle_code=cycle_code,
        parameter_code=parameter_code,
    ).order_by(PtStats.lab_code).all()

    header = ['Laboratorio', 'n', 'mean z', 'RSZ', 'Valutazione']
    rows = [header]

    for pt in pt_records:
        label, col = _perf_label(pt.mean_z)
        rows.append([
            pt.lab_code,
            str(pt.n_results),
            _fmt(pt.mean_z, 3),
            _fmt(pt.rsz, 3),
            label,
        ])

    if len(rows) == 1:
        story.append(Paragraph('Nessun risultato registrato per questo parametro.', styles['Normal']))
        return

    col_w = [5 * cm, 1.5 * cm, 3 * cm, 3 * cm, 4.5 * cm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(_result_table_style(len(rows)))
    story.append(t)

    # Riepilogo aggregato
    z_vals = [float(pt.mean_z) for pt in pt_records if pt.mean_z is not None]
    if z_vals:
        import statistics
        n_exc = sum(1 for z in z_vals if abs(z) <= 2)
        n_acc = sum(1 for z in z_vals if 2 < abs(z) <= 3)
        n_poor = sum(1 for z in z_vals if abs(z) > 3)
        story.append(Spacer(1, 0.15 * cm))
        story.append(Paragraph(
            f'Riepilogo: {len(z_vals)} lab — '
            f'Eccellenti: {n_exc} ({100*n_exc//len(z_vals)}%) — '
            f'Accettabili: {n_acc} — Fuori controllo: {n_poor}',
            ParagraphStyle('sum', parent=styles['Normal'], fontSize=8, textColor=colors.grey),
        ))


# ── Helper: tabella risultato singolo lab ───────────────────────────────────

def _build_lab_param_table(story, cycle_code, parameter_code, lab_code, styles):
    """Tabella con solo i dati del laboratorio richiedente."""
    pt = PtStats.query.filter_by(
        cycle_code=cycle_code,
        parameter_code=parameter_code,
        lab_code=lab_code,
    ).first()

    if not pt:
        story.append(Paragraph('Nessun risultato per questo parametro.', styles['Normal']))
        return

    result = Result.query.filter_by(
        cycle_code=cycle_code,
        parameter_code=parameter_code,
        lab_code=lab_code,
    ).order_by(Result.submitted_at.desc()).first()

    label, _ = _perf_label(pt.mean_z)

    rows = [
        ['Valore misurato', _fmt(result.measured_value) if result else '—'],
        ['n risultati', str(pt.n_results)],
        ['Z-score (mean)', _fmt(pt.mean_z, 3)],
        ['RSZ', _fmt(pt.rsz, 3)],
        ['Valutazione', label],
    ]

    t = Table(rows, colWidths=[6 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, _LGREY]),
    ]))
    story.append(t)

    # Statistiche aggregate anonimizzate (ISO 13528 §7.4.1)
    all_pts = PtStats.query.filter_by(
        cycle_code=cycle_code,
        parameter_code=parameter_code,
    ).all()
    z_vals = [float(p.mean_z) for p in all_pts if p.mean_z is not None]
    if len(z_vals) >= 2:
        import numpy as np
        story.append(Spacer(1, 0.15 * cm))
        story.append(Paragraph(
            f'Statistiche aggregate (tutti i lab, anonimizzate) — '
            f'n={len(z_vals)}, mean z={np.mean(z_vals):.3f}, '
            f'n eccellenti: {sum(1 for z in z_vals if abs(z)<=2)}/{len(z_vals)}',
            ParagraphStyle('agg', parent=styles['Normal'], fontSize=8, textColor=colors.grey),
        ))


# ── Stile tabella risultati ──────────────────────────────────────────────────

def _result_table_style(n_rows: int) -> TableStyle:
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), _BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, _LGREY]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    return TableStyle(style)
