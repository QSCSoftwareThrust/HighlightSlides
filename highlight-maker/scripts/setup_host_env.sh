#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INSTALL_LLM_CLIS="false"

for arg in "$@"; do
  case "${arg}" in
    --with-llm-clis)
      INSTALL_LLM_CLIS="true"
      ;;
    *)
      echo "Unknown option: ${arg}" >&2
      echo "Usage: scripts/setup_host_env.sh [--with-llm-clis]" >&2
      exit 2
      ;;
  esac
done

cd "${PROJECT_DIR}"

"${PYTHON_BIN}" -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .

mkdir -p work

if [[ "${INSTALL_LLM_CLIS}" == "true" ]]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm was not found; skipping Codex/Claude CLI installation." >&2
    echo "Install Node.js/npm or use preinstalled codex/claude commands." >&2
  else
    mkdir -p .npm-global
    npm install --prefix "${PROJECT_DIR}/.npm-global" @openai/codex @anthropic-ai/claude-code
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

cat <<EOF

Host environment is ready.

Next:
  source scripts/activate_highlight_env.sh
  codex

Then ask:
  Read highlight.md and create the highlight slides for 2601.03185
EOF
