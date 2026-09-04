# Highlight Slides Host Workflow

Use this workflow on lab machines where containers are not practical.

Supported host platforms:

- macOS with Homebrew dependencies.
- Linux with Python, Git, and Poppler installed through the system package
  manager.
- Windows through WSL/Ubuntu. Native PowerShell is not the recommended path for
  this version.

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

Platform prerequisites:

```bash
# macOS
brew install python git poppler

# Ubuntu/Debian Linux or Windows WSL/Ubuntu
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git poppler-utils
```

The workflow writes per-paper files under `work/`, for example:

```text
work/arxiv-2601-03185/paper_key_information.md
work/arxiv-2601-03185/output/highlight_slides.pptx
```

`pdfimages` from Poppler is optional. Without it, the tool still extracts
caption/image-block crops. Full-page PDF renders are skipped by default because
they are slower and usually less useful than image-only candidates; request
them only with `--full-page-renders`.
