from __future__ import annotations

import shutil
import subprocess
import re
from pathlib import Path

import fitz
from markitdown import MarkItDown


MIN_CROP_WIDTH = 120
MIN_CROP_HEIGHT = 120
CAPTION_RE = re.compile(r"^\s*(?:fig\.|figure)\s*\d+", re.IGNORECASE)


def convert_pdf_to_markdown(pdf_path: Path, output_md: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()
    result = converter.convert(str(pdf_path))
    output_md.write_text(result.text_content, encoding="utf-8")


def extract_with_pdfimages(pdf_path: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if not shutil.which("pdfimages"):
        return []

    prefix = output_dir / "embedded"
    subprocess.run(
        ["pdfimages", "-png", str(pdf_path), str(prefix)],
        check=True,
        text=True,
        capture_output=True,
    )
    return sorted(output_dir.glob("embedded-*.png"))


def extract_image_block_crops(pdf_path: Path, output_dir: Path, zoom: float = 2.0) -> list[Path]:
    """Crop page image blocks without surrounding text when the PDF exposes them."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            image_index = 0
            for block in page.get_text("dict").get("blocks", []):
                if block.get("type") != 1:
                    continue
                bbox = fitz.Rect(block["bbox"])
                if bbox.width < MIN_CROP_WIDTH or bbox.height < MIN_CROP_HEIGHT:
                    continue
                pix = page.get_pixmap(matrix=matrix, clip=bbox, alpha=False)
                out = output_dir / f"page-{page_number:03d}-image-{image_index:02d}.png"
                pix.save(out)
                rendered.append(out)
                image_index += 1

    return rendered


def extract_caption_figure_crops(pdf_path: Path, output_dir: Path, zoom: float = 2.0) -> list[Path]:
    """Crop vector/raster figure regions above detected captions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            caption_blocks = []
            for block in page.get_text("blocks"):
                text = block[4].strip().replace("\n", " ")
                if CAPTION_RE.match(text):
                    caption_blocks.append(fitz.Rect(block[:4]))

            if not caption_blocks:
                continue

            drawing_rects = [drawing["rect"] for drawing in page.get_drawings() if not drawing["rect"].is_empty]
            image_rects = []
            for block in page.get_text("dict").get("blocks", []):
                if block.get("type") == 1:
                    image_rects.append(fitz.Rect(block["bbox"]))
            graphic_rects = drawing_rects + image_rects

            for caption_index, caption in enumerate(caption_blocks):
                above_caption = caption.y0 - 6
                selected = [
                    rect
                    for rect in graphic_rects
                    if rect.y0 < above_caption
                    and rect.y1 > 0
                    and rect.width >= 8
                    and rect.height >= 8
                    and rect.get_area() >= 64
                ]
                if not selected:
                    continue

                figure_rect = selected[0]
                for rect in selected[1:]:
                    figure_rect |= rect

                figure_rect.y1 = min(figure_rect.y1, above_caption)
                figure_rect.x0 = max(0, figure_rect.x0 - 8)
                figure_rect.y0 = max(0, figure_rect.y0 - 8)
                figure_rect.x1 = min(page.rect.x1, figure_rect.x1 + 8)
                figure_rect.y1 = min(page.rect.y1, figure_rect.y1 + 8)

                if figure_rect.width < MIN_CROP_WIDTH or figure_rect.height < MIN_CROP_HEIGHT:
                    continue

                pix = page.get_pixmap(matrix=matrix, clip=figure_rect, alpha=False)
                out = output_dir / f"page-{page_number:03d}-figure-{caption_index:02d}.png"
                pix.save(out)
                rendered.append(out)

    return rendered


def render_pages_with_pymupdf(pdf_path: Path, output_dir: Path, zoom: float = 2.0) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    matrix = fitz.Matrix(zoom, zoom)
    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            out = output_dir / f"page-{page_number:03d}.png"
            pix.save(out)
            rendered.append(out)
    return rendered


def write_figure_index(output_dir: Path, crops: list[Path], embedded: list[Path], rendered: list[Path]) -> Path:
    index = output_dir / "FIGURE_CANDIDATES.md"
    lines = [
        "# Figure Candidates",
        "",
        "Prefer image-only crops when possible. Use rendered pages only as a fallback",
        "when no crop or embedded image contains the figure needed for the highlight.",
        "",
        "## Image-Only Crops",
        "",
    ]
    lines.extend(f"- `{path.relative_to(output_dir)}`" for path in crops)
    if not crops:
        lines.append("- None found by PyMuPDF image-block extraction.")
    lines.extend([
        "",
        "## Embedded Images",
        "",
    ])
    lines.extend(f"- `{path.relative_to(output_dir)}`" for path in embedded)
    if not embedded:
        lines.append("- None found by `pdfimages`.")
    lines.extend(["", "## Rendered Pages", ""])
    lines.extend(f"- `{path.relative_to(output_dir)}`" for path in rendered)
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index
