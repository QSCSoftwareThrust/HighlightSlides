# DOE Highlight Maker

Portable host or Docker/Podman workflow for producing DOE/NQISRC/QSC highlight
slide decks from arXiv or local PDF papers.

The workflow writes an intermediate `paper_key_information.md` for review, then
uses `FY26_Highlight_Template.pptx` to create a two-slide PowerPoint deck.

## Host Python Workflow

For the user-facing host workflow, use the scripts in the parent
`HighlightSlides` folder:

```bash
cd HighlightSlides
./install.sh
```

This `highlight-maker` folder also has developer scripts that run the package
directly from here.

Use this path only when you intentionally want to work inside `highlight-maker`.

From this folder:

```bash
cd HighlightSlides/highlight-maker
scripts/setup_host_env.sh
source scripts/activate_highlight_env.sh
```

If Codex and Claude are not already installed on the machine and local npm
installs are allowed, run setup with:

```bash
scripts/setup_host_env.sh --with-llm-clis
source scripts/activate_highlight_env.sh
```

The setup script creates `.venv`, installs this package and its Python
dependencies, and creates `work/` for per-paper projects. The activation script
sets:

```bash
HIGHLIGHT_PROJECTS_DIR=./work
```

Then start either LLM CLI from the same folder:

```bash
codex
```

or:

```bash
claude
```

Ask:

```text
Read highlight.md and create the highlight slides for 2601.03185
```

The LLM should run `highlight`, read the generated project-level `prompt.md`,
write `paper_key_information.md`, and then run `highlight deck` to create
`work/arxiv-2601-03185/output/highlight_slides.pptx`.

For a deterministic preparation-only run without opening an LLM:

```bash
highlight 2601.03185 --insecure-tls
```

Then:

```bash
cd work/arxiv-2601-03185
codex
```

Ask:

```text
Read prompt.md, create the highlight deck autonomously, and do not ask me routine setup questions.
```

### Host System Dependencies

Python dependencies are installed into `.venv`. `pdfimages` from Poppler is
optional: if it is unavailable, embedded figure extraction is skipped. The
default workflow still extracts image-block and caption crops; full-page renders
are opt-in through `--full-page-renders`.

Install Poppler only if you want embedded image extraction:

```bash
brew install poppler
```

or:

```bash
sudo apt-get install poppler-utils
```

## Build

```bash
docker build -t qsc-highlight-maker .
```

or:

```bash
podman build -t qsc-highlight-maker .
```

## Browser VS Code

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8080
```

The compose setup starts `code-server` without a password for local use. If this
is deployed on a shared server, put it behind authentication or set code-server
auth explicitly.

To also start the local Ollama model server, use the `local-llm` profile:

```bash
docker compose --profile local-llm up --build
```

## Terminal Workflow

Create a per-paper project from an arXiv ID or URL with one command:

```bash
highlight 2401.01234
```

If your institution performs TLS inspection and arXiv downloads fail with a
`self-signed certificate in certificate chain` error, either add your
institutional CA certificate to the container or use:

```bash
highlight 2401.01234 --insecure-tls
```

For a local PDF:

```bash
highlight /work/highlight-slides/my_paper.pdf
```

Then enter the project folder:

```bash
cd /work/projects/arxiv-2401-01234
```

Run either LLM CLI interactively:

```bash
codex
```

or:

```bash
claude
```

For Codex login inside the container, prefer device authentication:

```bash
codex login --device-auth
```

Follow the URL/code shown in the terminal. This avoids the browser callback that
can open a container-local `localhost` URL. Login state is persisted in the
Docker volume mounted at `/home/coder`.

Regular Codex browser login is also supported by publishing and forwarding
callback port `1455`:

```bash
codex login
```

If it prints a long authentication URL, open that URL in your normal browser.

Ask the LLM:

```text
Read prompt.md, create the highlight deck autonomously, and do not ask me routine setup questions.
```

The generated `prompt.md` is placed in the project root so it is in the same
folder where you launch `codex` or `claude`.

## LLM-Orchestrated Workflow

You can also let Codex or Claude run the preparation command and write the final
Markdown. Start the container, open a terminal in browser VS Code, and run:

```bash
codex login --device-auth
codex
```

or:

```bash
claude
```

Then ask:

```text
Read highlight.md and create the highlight slides for 2601.03185.
```

The LLM should run `highlight`, read the generated `prompt.md`, and write
`paper_key_information.md` in the generated project folder, then run
`highlight deck` to create `output/highlight_slides.pptx`.

## Local Model Workflow

The compose file includes an optional Ollama service for local models. Start it
with the `local-llm` profile:

```bash
docker compose --profile local-llm up --build
```

Pull one model once from the browser VS Code terminal:

```bash
curl http://ollama:11434/api/pull -d '{"name":"gemma3n:e4b"}'
```

Then generate the Markdown without Codex or Claude login:

```bash
highlight local 2601.03185 --insecure-tls --model gemma3n:e4b
```

This writes both `paper_key_information.md` and
`output/highlight_slides.pptx`.

The default local model is `gemma3n:e4b`, the Ollama-published effective 4B
Gemma model. You can try a different Ollama model name with `--model`.

## Included Tools

- MarkItDown for PDF-to-Markdown extraction.
- Poppler `pdfimages` for embedded image extraction.
- PyMuPDF for rendered page images and PDF fallbacks.
- `@openai/codex` and `@anthropic-ai/claude-code` installed with npm.
- `code-server@4.98.2` for browser-based VS Code through the official
  `codercom/code-server` base image. This avoids installing code-server through
  npm, which is brittle on managed TLS networks.

Note: MarkItDown is the Microsoft package named `markitdown`; the container uses
that package because it is the maintained tool with this name.
