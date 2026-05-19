# Highlight Slides Host Workflow

Use this workflow on lab machines where containers are not practical.

```bash
cd HighlightSlides
./install.sh
```

The installer creates or updates `.venv`, activates it internally, and launches
the first available LLM CLI, preferring Codex and then Claude.

To force one CLI:

```bash
./install.sh --codex
```

or:

```bash
./install.sh --claude
```

Then ask:

```text
Read highlight.md and create the highlight slides for 2601.03185
```

If Codex or Claude are not installed and local npm installs are allowed:

```bash
./install.sh --with-llm-clis
```

The workflow writes per-paper files under `work/`, for example:

```text
work/arxiv-2601-03185/paper_key_information.md
work/arxiv-2601-03185/output/highlight_slides.pptx
```

`pdfimages` from Poppler is optional. Without it, the tool skips embedded image
extraction and still renders full-page candidates with PyMuPDF.
