#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_DIR="${ROOT_DIR}/highlight-maker"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INSTALL_LLM_CLIS="false"
SETUP_ONLY="false"
LLM_CMD="${HIGHLIGHT_LLM:-auto}"

for arg in "$@"; do
  case "${arg}" in
    --with-llm-clis)
      INSTALL_LLM_CLIS="true"
      ;;
    --setup-only)
      SETUP_ONLY="true"
      ;;
    --codex)
      LLM_CMD="codex"
      ;;
    --claude)
      LLM_CMD="claude"
      ;;
    *)
      echo "Unknown option: ${arg}" >&2
      echo "Usage: ./install.sh [--with-llm-clis] [--codex|--claude] [--setup-only]" >&2
      exit 2
      ;;
  esac
done

if [[ ! -f "${TOOL_DIR}/pyproject.toml" ]]; then
  echo "Missing highlight-maker package at ${TOOL_DIR}" >&2
  exit 1
fi

cd "${ROOT_DIR}"

"${PYTHON_BIN}" -m venv .venv
source .venv/bin/activate
export HIGHLIGHT_MAKER_HOME="${TOOL_DIR}"
export HIGHLIGHT_PROJECTS_DIR="${ROOT_DIR}/work"
export HIGHLIGHT_TEMPLATE="${ROOT_DIR}/FY26_Highlight_Template.pptx"
export HIGHLIGHT_QSC_LOGO="${ROOT_DIR}/assets/qsc-logo.png"
export PATH="${ROOT_DIR}/.npm-global/bin:${PATH}"

python -m pip install --upgrade pip setuptools wheel
python -m pip install -e "${TOOL_DIR}"

mkdir -p work

if [[ "${INSTALL_LLM_CLIS}" == "true" ]]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm was not found; skipping Codex/Claude CLI installation." >&2
    echo "Install Node.js/npm or use preinstalled codex/claude commands." >&2
  else
    mkdir -p .npm-global
    npm install --prefix "${ROOT_DIR}/.npm-global" @openai/codex @anthropic-ai/claude-code
  fi
fi

if ! command -v pdfimages >/dev/null 2>&1; then
  cat >&2 <<'EOF'

Warning: pdfimages was not found.
Embedded figure extraction will be skipped, but PyMuPDF page rendering will still work.
Install Poppler if you want embedded image extraction:
  macOS:  brew install poppler
  Ubuntu: sudo apt-get install poppler-utils
  RHEL:   sudo dnf install poppler-utils
EOF
fi

if [[ "${SETUP_ONLY}" == "true" ]]; then
  cat <<EOF

Highlight host environment is ready.

Next:
  ./install.sh

Then ask:
  Read highlight.md and create the highlight slides for 2601.03185
EOF
  exit 0
fi

if [[ "${LLM_CMD}" == "auto" ]]; then
  if command -v codex >/dev/null 2>&1; then
    LLM_CMD="codex"
  elif command -v claude >/dev/null 2>&1; then
    LLM_CMD="claude"
  else
    cat >&2 <<'EOF'

Highlight host environment is ready, but neither `codex` nor `claude` was found.

Install one of those CLIs, or rerun with local npm installation enabled:
  ./install.sh --with-llm-clis
EOF
    exit 1
  fi
fi

if ! command -v "${LLM_CMD}" >/dev/null 2>&1; then
  cat >&2 <<EOF

Highlight host environment is ready, but `${LLM_CMD}` was not found.

Install it, choose another CLI, or rerun with:
  ./install.sh --with-llm-clis
EOF
  exit 1
fi

cat <<EOF

Highlight host environment is ready.
Launching ${LLM_CMD} from ${ROOT_DIR}

Ask:
  Read highlight.md and create the highlight slides for 2601.03185

EOF

exec "${LLM_CMD}"
