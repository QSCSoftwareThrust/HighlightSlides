from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .arxiv import download_pdf, parse_arxiv_source
from .local_llm import DEFAULT_MODEL, DEFAULT_OLLAMA_URL


app = typer.Typer(
    help="Prepare DOE/NQISRC/QSC highlight slide input files.",
)
console = Console()

KNOWN_COMMANDS = {
    "init",
    "fetch",
    "import-pdf",
    "extract",
    "figures",
    "prompt",
    "prepare",
    "local",
    "deck",
}

DEFAULT_ROOT = Path(os.environ.get("HIGHLIGHT_PROJECTS_DIR", Path.cwd() / "work"))
PROMPT_TEMPLATE = Path(__file__).resolve().parents[2] / "prompts" / "paper_key_information_prompt.md"


def default_template_path() -> Path:
    candidates = [
        os.environ.get("HIGHLIGHT_TEMPLATE"),
        Path.cwd() / "FY26_Highlight_Template.pptx",
        Path.cwd().parent / "FY26_Highlight_Template.pptx",
        Path(__file__).resolve().parents[3] / "FY26_Highlight_Template.pptx",
        Path("/work/highlight-slides/FY26_Highlight_Template.pptx"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            return path
    return Path(__file__).resolve().parents[3] / "FY26_Highlight_Template.pptx"


def project_dir(project: str, root: Path) -> Path:
    return root / project


def require_pdf(base: Path) -> Path:
    pdf = base / "source" / "paper.pdf"
    if not pdf.exists():
        raise typer.BadParameter(f"No PDF found at {pdf}. Run fetch or import-pdf first.")
    return pdf


def create_project(base: Path) -> None:
    for relative in ["source", "extracted/figures", "llm", "logos", "output"]:
        (base / relative).mkdir(parents=True, exist_ok=True)


def fetch_arxiv_to_project(arxiv: str, base: Path, insecure_tls: bool = False) -> None:
    source = parse_arxiv_source(arxiv)
    pdf = base / "source" / "paper.pdf"
    download_pdf(source, pdf, verify_tls=not insecure_tls)
    (base / "source" / "arxiv_source.txt").write_text(
        f"id: {source.identifier}\nabs: {source.abs_url}\npdf: {source.pdf_url}\n",
        encoding="utf-8",
    )
    console.print(f"Downloaded {source.pdf_url} -> {pdf}")


def import_pdf_to_project(pdf_path: Path, base: Path) -> None:
    destination = base / "source" / "paper.pdf"
    shutil.copy2(pdf_path, destination)
    console.print(f"Imported {pdf_path} -> {destination}")


def extract_project(base: Path) -> Path:
    from .extract import convert_pdf_to_markdown

    pdf = require_pdf(base)
    output_md = base / "extracted" / "paper.md"
    convert_pdf_to_markdown(pdf, output_md)
    console.print(f"Wrote {output_md}")
    return output_md


def extract_project_figures(base: Path) -> Path:
    from .extract import (
        extract_caption_figure_crops,
        extract_image_block_crops,
        extract_with_pdfimages,
        render_pages_with_pymupdf,
        write_figure_index,
    )

    pdf = require_pdf(base)
    figure_dir = base / "extracted" / "figures"
    crops = extract_caption_figure_crops(pdf, figure_dir / "crops")
    crops.extend(extract_image_block_crops(pdf, figure_dir / "crops"))
    embedded = extract_with_pdfimages(pdf, figure_dir / "embedded")
    rendered = render_pages_with_pymupdf(pdf, figure_dir / "pages")
    index = write_figure_index(figure_dir, crops, embedded, rendered)
    console.print(f"Wrote {index}")
    return index


def write_project_prompt(base: Path) -> Path:
    paper_md = base / "extracted" / "paper.md"
    figure_index = base / "extracted" / "figures" / "FIGURE_CANDIDATES.md"
    if not paper_md.exists():
        raise typer.BadParameter(f"Missing {paper_md}. Run extract first.")

    prompt_text = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    prompt_text += "\n\n# Files to Read\n\n"
    prompt_text += f"- Paper Markdown: `{paper_md}`\n"
    if figure_index.exists():
        prompt_text += f"- Figure candidates: `{figure_index}`\n"
    prompt_text += f"\nWrite the completed file to `{base / 'paper_key_information.md'}`.\n"

    out = base / "prompt.md"
    out.write_text(prompt_text, encoding="utf-8")

    legacy_out = base / "llm" / "prompt.md"
    legacy_out.parent.mkdir(parents=True, exist_ok=True)
    legacy_out.write_text(prompt_text, encoding="utf-8")

    console.print(f"Wrote {out}")
    return out


def default_project_name(source: str) -> str:
    source_path = Path(source).expanduser()
    if source_path.exists():
        return source_path.stem
    return f"arxiv-{parse_arxiv_source(source).identifier.replace('.', '-')}"


def prepare_project(source: str, project: Optional[str], root: Path, insecure_tls: bool) -> None:
    source_path = Path(source).expanduser()
    project_name = project or default_project_name(source)

    base = project_dir(project_name, root)
    create_project(base)
    console.print(f"Prepared project directory: {base}")

    if source_path.exists():
        import_pdf_to_project(source_path, base)
    else:
        fetch_arxiv_to_project(source, base, insecure_tls=insecure_tls)

    extract_project(base)
    extract_project_figures(base)
    prompt_path = write_project_prompt(base)
    console.print("")
    console.print(f"Next: cd {base}")
    console.print("Then run: codex  # or claude")
    console.print(f"Ask the LLM to read {prompt_path.name} and write paper_key_information.md.")


@app.command()
def init(
    project: str,
    root: Path = typer.Option(DEFAULT_ROOT, help="Root directory for per-paper projects."),
) -> None:
    """Create the directory layout for one paper."""
    base = project_dir(project, root)
    create_project(base)
    console.print(f"Created project: {base}")


@app.command()
def fetch(
    arxiv: str = typer.Argument(..., help="arXiv ID or arXiv abs/pdf URL."),
    project: str = typer.Option(..., help="Per-paper project name."),
    root: Path = typer.Option(DEFAULT_ROOT, help="Root directory for per-paper projects."),
    insecure_tls: bool = typer.Option(
        False,
        "--insecure-tls",
        help="Disable TLS certificate verification for managed networks with TLS inspection.",
    ),
) -> None:
    """Download a paper PDF from arXiv."""
    base = project_dir(project, root)
    init(project, root)
    fetch_arxiv_to_project(arxiv, base, insecure_tls=insecure_tls)


@app.command("import-pdf")
def import_pdf(
    pdf_path: Path = typer.Argument(..., exists=True, readable=True, help="Local PDF path."),
    project: str = typer.Option(..., help="Per-paper project name."),
    root: Path = typer.Option(DEFAULT_ROOT, help="Root directory for per-paper projects."),
) -> None:
    """Copy a local PDF into a project."""
    base = project_dir(project, root)
    init(project, root)
    import_pdf_to_project(pdf_path, base)


@app.command()
def extract(
    project: str = typer.Option(..., help="Per-paper project name."),
    root: Path = typer.Option(DEFAULT_ROOT, help="Root directory for per-paper projects."),
) -> None:
    """Convert the PDF to Markdown with MarkItDown."""
    base = project_dir(project, root)
    extract_project(base)


@app.command()
def figures(
    project: str = typer.Option(..., help="Per-paper project name."),
    root: Path = typer.Option(DEFAULT_ROOT, help="Root directory for per-paper projects."),
) -> None:
    """Extract embedded images and render page candidates."""
    base = project_dir(project, root)
    extract_project_figures(base)


@app.command()
def prompt(
    project: str = typer.Option(..., help="Per-paper project name."),
    root: Path = typer.Option(DEFAULT_ROOT, help="Root directory for per-paper projects."),
) -> None:
    """Create the LLM prompt for paper_key_information.md."""
    base = project_dir(project, root)
    write_project_prompt(base)


@app.command()
def prepare(
    source: str = typer.Argument(..., help="arXiv ID/URL or local PDF path."),
    project: Optional[str] = typer.Option(None, help="Per-paper project name."),
    root: Path = typer.Option(DEFAULT_ROOT, help="Root directory for per-paper projects."),
    insecure_tls: bool = typer.Option(
        False,
        "--insecure-tls",
        help="Disable TLS certificate verification for managed networks with TLS inspection.",
    ),
) -> None:
    """Run fetch/import, Markdown extraction, figure extraction, and prompt generation."""
    prepare_project(source, project, root, insecure_tls)


@app.command("local")
def local(
    source: str = typer.Argument(..., help="arXiv ID/URL or local PDF path."),
    project: Optional[str] = typer.Option(None, help="Per-paper project name."),
    root: Path = typer.Option(DEFAULT_ROOT, help="Root directory for per-paper projects."),
    insecure_tls: bool = typer.Option(
        False,
        "--insecure-tls",
        help="Disable TLS certificate verification for managed networks with TLS inspection.",
    ),
    model: str = typer.Option(DEFAULT_MODEL, help="Ollama model name."),
    ollama_url: str = typer.Option(DEFAULT_OLLAMA_URL, help="Ollama API base URL."),
) -> None:
    """Prepare the paper and generate paper_key_information.md with local Ollama."""
    from .local_llm import generate_key_information
    from .pptx_export import build_highlight_deck

    prepare_project(source, project, root, insecure_tls)
    project_name = project or default_project_name(source)
    base = project_dir(project_name, root)
    key_output = generate_key_information(base, ollama_url=ollama_url, model=model)
    deck_output = build_highlight_deck(base, template_path=default_template_path())
    console.print("")
    console.print(f"Wrote local-model output: {key_output}")
    console.print(f"Wrote highlight deck: {deck_output}")


@app.command()
def deck(
    project: str = typer.Option(..., help="Per-paper project name."),
    root: Path = typer.Option(DEFAULT_ROOT, help="Root directory for per-paper projects."),
    template: Optional[Path] = typer.Option(
        None,
        help="PowerPoint template path. Defaults to FY26_Highlight_Template.pptx.",
    ),
    output: Optional[Path] = typer.Option(None, help="Output .pptx path."),
) -> None:
    """Create the two-slide highlight deck from paper_key_information.md."""
    from .pptx_export import build_highlight_deck

    base = project_dir(project, root)
    template_path = template or default_template_path()
    output_path = build_highlight_deck(base, template_path=template_path, output_path=output)
    console.print(f"Wrote highlight deck: {output_path}")


def entrypoint() -> None:
    """CLI wrapper that preserves compact `highlight 2601.03185` usage."""
    args = sys.argv[1:]
    if args and args[0] not in KNOWN_COMMANDS and not args[0].startswith("-"):
        args = ["prepare", *args]
    app(args=args, prog_name="highlight")


if __name__ == "__main__":
    entrypoint()
