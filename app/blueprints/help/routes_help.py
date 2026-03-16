import os
import re
import frontmatter
import markdown
from flask import render_template, abort, current_app
from flask_login import login_required

from . import help_bp
from ..auth.decorators import disclaimer_required

# Cartella radice dei documenti MD (v2)
DOCS_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "docs")
print(">>> HELP TEMPLATE DIR:", os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "help", "_sidebar.html"))


def _docs_root():
    return os.path.abspath(DOCS_ROOT)


def _load_doc(slug: str):
    """Carica e parsa un file MD dato il suo slug (es: 'admin/01-cicli')."""
    path = os.path.join(_docs_root(), slug + ".md")
    # Sicurezza: verifica che il path resti dentro docs/
    real_path = os.path.realpath(path)
    if not real_path.startswith(os.path.realpath(_docs_root())):
        abort(403)
    if not os.path.isfile(real_path):
        abort(404)
    post = frontmatter.load(real_path)
    return post


def _render_content(raw: str, base_dir: str = "") -> str:
    """Converte wikilinks e poi markdown → HTML.

    base_dir: prefisso da anteporre ai wikilink relativi (es. 'manuale-utente').
    """
    prefix = base_dir + "/" if base_dir else ""

    # [[slug|testo]] → [testo](/help/{prefix}slug)
    raw = re.sub(
        r"\[\[([^\]|]+)\|([^\]]+)\]\]",
        lambda m: f"[{m.group(2)}](/help/{prefix}{m.group(1)})",
        raw,
    )
    # [[slug]] → [slug](/help/{prefix}slug)
    raw = re.sub(
        r"\[\[([^\]]+)\]\]",
        lambda m: f"[{m.group(1)}](/help/{prefix}{m.group(1)})",
        raw,
    )
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "attr_list"]
    )
    return md.convert(raw)


def _build_manual_tree():
    """Costruisce la struttura gerarchica di docs/manuale-utente/."""
    base = os.path.join(_docs_root(), "manuale-utente")
    sections = []
    if not os.path.isdir(base):
        return sections
    for folder in sorted(
        d for d in os.listdir(base)
        if os.path.isdir(os.path.join(base, d)) and not d.startswith(".")
    ):
        items = []
        section_path = os.path.join(base, folder)
        for fname in sorted(f for f in os.listdir(section_path) if f.endswith(".md")):
            slug = f"manuale-utente/{folder}/{fname[:-3]}"
            try:
                post = frontmatter.load(os.path.join(section_path, fname))
                title = post.get("title") or fname[:-3]
            except Exception:
                title = fname[:-3]
            items.append({"slug": slug, "title": title})
        if items:
            sections.append({"name": folder, "items": items})
    return sections


def _build_sidebar():
    """Costruisce la struttura della sidebar leggendo tutti i .md."""
    sidebar = {"admin": [], "user": [], "manuale": _build_manual_tree()}
    for section in ("admin", "user"):
        section_dir = os.path.join(_docs_root(), section)
        if not os.path.isdir(section_dir):
            continue
        files = sorted(
            f for f in os.listdir(section_dir) if f.endswith(".md")
        )
        for fname in files:
            slug = f"{section}/{fname[:-3]}"
            try:
                post = frontmatter.load(os.path.join(section_dir, fname))
                sidebar[section].append(
                    {
                        "slug": slug,
                        "title": post.get("title", fname[:-3]),
                        "order": post.get("order", 99),
                    }
                )
            except Exception:
                pass
        sidebar[section].sort(key=lambda x: x["order"])
    return sidebar


def _resolve_related(related_slugs: list) -> list:
    """Risolve la lista di slug related in dizionari {slug, title}."""
    result = []
    for slug in related_slugs or []:
        path = os.path.join(_docs_root(), slug + ".md")
        if os.path.isfile(path):
            try:
                post = frontmatter.load(path)
                result.append({"slug": slug, "title": post.get("title", slug)})
            except Exception:
                pass
    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@help_bp.route("/")
@disclaimer_required
def index():
    sidebar = _build_sidebar()
    # Carica anche il doc principale se esiste
    try:
        post = _load_doc("index")
        intro = _render_content(post.content)
    except Exception:
        intro = None
    return render_template("help/index.html", sidebar=sidebar, intro=intro)


@help_bp.route("/<path:slug>")
@disclaimer_required
def article(slug: str):
    post = _load_doc(slug)
    meta = dict(post.metadata)

    # Fallback titolo: se manca frontmatter, estrai il primo H1 dal contenuto
    if not meta.get("title"):
        h1 = re.search(r"^#\s+(.+)$", post.content, re.MULTILINE)
        meta["title"] = h1.group(1).strip() if h1 else slug.split("/")[-1]

    # Controllo accesso: articoli role=admin solo per admin
    role = meta.get("role", "all")
    if role == "admin":
        from flask_login import current_user
        if not current_user.is_admin:
            abort(403)

    # base_dir = directory del file (es. "manuale-utente" per HOME, "manuale-utente/01-Introduzione" per i file interni)
    parts = slug.split("/")
    base_dir = "/".join(parts[:-1]) if len(parts) > 1 else ""
    content_html = _render_content(post.content, base_dir=base_dir)
    sidebar = _build_sidebar()
    related = _resolve_related(meta.get("related", []))

    # Breadcrumb: sezione + titolo
    section = parts[0] if len(parts) > 1 else None

    return render_template(
        "help/article.html",
        meta=meta,
        content=content_html,
        sidebar=sidebar,
        related=related,
        current_slug=slug,
        section=section,
    )
