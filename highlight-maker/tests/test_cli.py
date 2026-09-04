from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from highlight_tool import cli


class HighlightCliTests(unittest.TestCase):
    def test_figure_preparation_skips_full_page_renders_when_crops_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory)
            pdf_path = base / "source" / "paper.pdf"
            pdf_path.parent.mkdir(parents=True)
            pdf_path.write_bytes(b"placeholder PDF")

            def caption_crops(_pdf: Path, output_dir: Path) -> list[Path]:
                output_dir.mkdir(parents=True)
                crop = output_dir / "crop.png"
                crop.write_bytes(b"crop")
                return [crop]

            def empty_result(_pdf: Path, output_dir: Path) -> list[Path]:
                output_dir.mkdir(parents=True, exist_ok=True)
                return []

            def page_renders(_pdf: Path, _output_dir: Path) -> list[Path]:
                raise AssertionError("full-page rendering should be skipped when a crop is available")

            def write_index(output_dir: Path, _crops: list[Path], _embedded: list[Path], rendered: list[Path]) -> Path:
                self.assertEqual([], rendered)
                output_dir.mkdir(parents=True, exist_ok=True)
                index = output_dir / "FIGURE_CANDIDATES.md"
                index.write_text("# Figure Candidates\n", encoding="utf-8")
                return index

            with (
                patch("highlight_tool.extract.extract_caption_figure_crops", caption_crops),
                patch("highlight_tool.extract.extract_image_block_crops", empty_result),
                patch("highlight_tool.extract.extract_with_pdfimages", empty_result),
                patch("highlight_tool.extract.render_pages_with_pymupdf", page_renders),
                patch("highlight_tool.extract.write_figure_index", write_index),
            ):
                index = cli.extract_project_figures(base)

            self.assertTrue(index.exists())

    def test_prepare_reuses_matching_local_source_and_generated_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            source = temporary_root / "input.pdf"
            source.write_bytes(b"same source")
            calls: list[str] = []

            def extract(base: Path) -> Path:
                calls.append("extract")
                output = base / "extracted" / "paper.md"
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text("paper", encoding="utf-8")
                return output

            def figures(base: Path, *, include_page_renders: bool = False) -> Path:
                calls.append(f"figures:{include_page_renders}")
                output = base / "extracted" / "figures" / "FIGURE_CANDIDATES.md"
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text("figures", encoding="utf-8")
                return output

            def prompt(base: Path) -> Path:
                calls.append("prompt")
                output = base / "prompt.md"
                output.write_text("prompt", encoding="utf-8")
                return output

            with (
                patch.object(cli, "extract_project", extract),
                patch.object(cli, "extract_project_figures", figures),
                patch.object(cli, "write_project_prompt", prompt),
            ):
                cli.prepare_project(str(source), "paper", temporary_root, insecure_tls=False)
                cli.prepare_project(str(source), "paper", temporary_root, insecure_tls=False)

            self.assertEqual(["extract", "figures:False", "prompt", "prompt"], calls)
            base = temporary_root / "paper"
            for relative in ("source", "extracted/figures", "llm", "logos", "output"):
                self.assertTrue((base / relative).is_dir())


if __name__ == "__main__":
    unittest.main()
