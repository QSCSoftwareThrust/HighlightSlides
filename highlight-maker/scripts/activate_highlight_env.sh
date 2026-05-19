#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ ! -f "${PROJECT_DIR}/.venv/bin/activate" ]]; then
  echo "Missing ${PROJECT_DIR}/.venv. Run scripts/setup_host_env.sh first." >&2
  return 1 2>/dev/null || exit 1
fi

source "${PROJECT_DIR}/.venv/bin/activate"
export HIGHLIGHT_MAKER_HOME="${PROJECT_DIR}"
export HIGHLIGHT_PROJECTS_DIR="${PROJECT_DIR}/work"
export PATH="${PROJECT_DIR}/.npm-global/bin:${PATH}"
cd "${PROJECT_DIR}" || return 1 2>/dev/null || exit 1

echo "Activated highlight-maker host environment."
echo "Project directory: ${PROJECT_DIR}"
echo "Paper projects: ${HIGHLIGHT_PROJECTS_DIR}"
