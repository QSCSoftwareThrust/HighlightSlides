#!/usr/bin/env bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "${ROOT_DIR}/.venv/bin/activate" ]]; then
  echo "Missing ${ROOT_DIR}/.venv. Run ./install.sh first." >&2
  return 1 2>/dev/null || exit 1
fi

source "${ROOT_DIR}/.venv/bin/activate"
export HIGHLIGHT_MAKER_HOME="${ROOT_DIR}/highlight-maker"
export HIGHLIGHT_PROJECTS_DIR="${ROOT_DIR}/work"
export HIGHLIGHT_TEMPLATE="${ROOT_DIR}/FY26_Highlight_Template.pptx"
export HIGHLIGHT_QSC_LOGO="${ROOT_DIR}/assets/qsc-logo-white.png"
export PATH="${ROOT_DIR}/.npm-global/bin:${PATH}"
cd "${ROOT_DIR}" || return 1 2>/dev/null || exit 1

echo "Activated highlight host environment."
echo "Working directory: ${ROOT_DIR}"
echo "Paper projects: ${HIGHLIGHT_PROJECTS_DIR}"
