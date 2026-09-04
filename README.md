# QSC Highlight Slides

Automation for producing QSC/DOE highlight slides from an arXiv paper or a
local PDF. The workflow extracts paper text and figures, asks an LLM CLI such as
Codex or Claude to write `paper_key_information.md`, and then creates a
PowerPoint deck from `FY26_Highlight_Template.pptx`.

The recommended workflow is the host Python installer in this repository. Docker
support is still available in `highlight-maker/` for users who prefer a
container.

## What You Need

- Python 3.10 or newer.
- Git.
- One LLM CLI available in your terminal:
  - Codex: `codex`
  - Claude Code: `claude`
- Optional but recommended: Poppler, which provides `pdfimages` for better PDF
  figure extraction.

The installer creates a local `.venv` and installs the Python package and
dependencies there. It does not require Docker or Podman.

## macOS

Install prerequisites with Homebrew:

```bash
brew install python git poppler
```

Clone and install:

```bash
git clone https://github.com/QSCSoftwareThrust/HighlightSlides.git
cd HighlightSlides
./install.sh
```

If Codex or Claude are not installed and npm installs are allowed on your
machine:

```bash
./install.sh --with-llm-clis
```

## Linux

On Ubuntu or Debian:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git poppler-utils
```

Clone and install:

```bash
git clone https://github.com/QSCSoftwareThrust/HighlightSlides.git
cd HighlightSlides
./install.sh
```

If Codex or Claude are not installed and npm installs are allowed on your
machine:

```bash
./install.sh --with-llm-clis
```

For other Linux distributions, install the equivalent packages for Python,
Git, and Poppler.

## Windows

Use Windows Subsystem for Linux. This is the supported Windows path because the
installer and PDF tooling are Unix-style.

From PowerShell:

```powershell
wsl --install
```

Restart if Windows asks you to. Then open Ubuntu from the Start menu and run:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git poppler-utils
git clone https://github.com/QSCSoftwareThrust/HighlightSlides.git
cd HighlightSlides
./install.sh
```

If Codex or Claude are not installed inside WSL and npm installs are allowed:

```bash
./install.sh --with-llm-clis
```

Native PowerShell is not the recommended path for this version because Poppler
and shell activation differ across Windows installations.

## Usage

After `./install.sh` finishes, it opens the first available LLM CLI, preferring
Codex and then Claude. If both are available, you can force one:

```bash
./install.sh --codex
```

or:

```bash
./install.sh --claude
```

Inside Codex or Claude, ask:

```text
Read highlight.md and create the highlight slides for 2601.03185
```

You can replace `2601.03185` with another arXiv ID or arXiv URL.

The workflow writes each paper under `work/`. For example:

```text
work/arxiv-2601-03185/paper_key_information.md
work/arxiv-2601-03185/output/highlight_slides.pptx
```

To prepare a project without opening an LLM:

```bash
./install.sh --setup-only
source ./activate_highlight_env.sh
highlight 2601.03185
```

Then open an LLM from the project folder:

```bash
cd work/arxiv-2601-03185
codex
```

and ask:

```text
Read prompt.md, create the highlight deck autonomously, and do not ask me routine setup questions.
```

## Local PDFs

Place the PDF somewhere accessible and pass the file path in the same prompt:

```text
Read highlight.md and create the highlight slides for /path/to/paper.pdf
```

On Windows with WSL, files on the Windows `C:` drive are usually available under
`/mnt/c/`.

## Container Option

The container workflow is in `highlight-maker/`:

```bash
cd highlight-maker
docker compose up --build
```

Then open:

```text
http://localhost:8080
```

See `highlight-maker/README.md` for container and local-model details.
