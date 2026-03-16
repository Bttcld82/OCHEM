import os
import frontmatter
import markdown
from flask import render_template, abort

from . import agent_bp
from ..auth.decorators import disclaimer_required, role_required

WORKSPACE_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "agent-workspace")


def _workspace_root():
    return os.path.abspath(WORKSPACE_ROOT)


def _load_md(rel_path):
    """Carica un file MD da agent-workspace con path traversal check."""
    path = os.path.join(_workspace_root(), rel_path)
    real_path = os.path.realpath(path)
    if not real_path.startswith(os.path.realpath(_workspace_root())):
        abort(403)
    if not os.path.isfile(real_path):
        abort(404)
    return frontmatter.load(real_path)


def _render_md(raw):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "attr_list"])
    return md.convert(raw)


def _load_all_proposals():
    """Carica tutte le proposte PROP-*.md da agent-workspace/proposals/."""
    proposals_dir = os.path.join(_workspace_root(), "proposals")
    if not os.path.isdir(proposals_dir):
        return []
    proposals = []
    for fname in os.listdir(proposals_dir):
        if not fname.startswith("PROP-") or not fname.endswith(".md"):
            continue
        try:
            post = frontmatter.load(os.path.join(proposals_dir, fname))
            proposals.append(dict(post.metadata))
        except Exception:
            pass
    proposals.sort(key=lambda p: p.get("id", ""))
    return proposals


def _find_proposal_file(prop_id):
    """Trova il file proposta con prefisso {prop_id}- in agent-workspace/proposals/."""
    proposals_dir = os.path.join(_workspace_root(), "proposals")
    if not os.path.isdir(proposals_dir):
        abort(404)
    for fname in os.listdir(proposals_dir):
        if fname.startswith(f"{prop_id}-") and fname.endswith(".md"):
            return os.path.join("proposals", fname)
    abort(404)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@agent_bp.route("/")
@disclaimer_required
@role_required("admin")
def index():
    proposals = _load_all_proposals()
    totale = len(proposals)
    approvate = sum(1 for p in proposals if p.get("status") == "approved")
    rifiutate = sum(1 for p in proposals if p.get("status") == "rejected")
    in_corso = sum(1 for p in proposals if p.get("status") == "in_progress")
    return render_template(
        "agent/index.html",
        proposals=proposals,
        totale=totale,
        approvate=approvate,
        rifiutate=rifiutate,
        in_corso=in_corso,
        current_page="index",
    )


@agent_bp.route("/proposals/<prop_id>")
@disclaimer_required
@role_required("admin")
def proposal_detail(prop_id):
    rel_path = _find_proposal_file(prop_id)
    post = _load_md(rel_path)
    meta = dict(post.metadata)
    content = _render_md(post.content)
    proposals = _load_all_proposals()
    return render_template(
        "agent/proposal.html",
        meta=meta,
        content=content,
        prop_id=prop_id,
        proposals=proposals,
        current_page="proposal",
        current_prop_id=prop_id,
    )


@agent_bp.route("/decisions")
@disclaimer_required
@role_required("admin")
def decisions():
    post = _load_md("decisions.md")
    content = _render_md(post.content)
    proposals = _load_all_proposals()
    return render_template(
        "agent/decisions.html",
        content=content,
        proposals=proposals,
        current_page="decisions",
    )
