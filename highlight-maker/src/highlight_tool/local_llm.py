from __future__ import annotations

import json
import textwrap
from pathlib import Path

import requests


DEFAULT_OLLAMA_URL = "http://ollama:11434"
DEFAULT_MODEL = "gemma3n:e4b"


def _read_limited(path: Path, max_chars: int) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2]
    tail = text[-max_chars // 2 :]
    return head + "\n\n[... middle of source paper omitted for context budget ...]\n\n" + tail


def ensure_model_available(ollama_url: str, model: str) -> None:
    response = requests.get(f"{ollama_url}/api/tags", timeout=20)
    response.raise_for_status()
    models = response.json().get("models", [])
    names = {item.get("name") for item in models}
    if model not in names:
        raise RuntimeError(
            textwrap.dedent(
                f"""
                Ollama model `{model}` is not installed.

                Pull it once from the browser VS Code terminal:

                    curl http://ollama:11434/api/pull -d '{{"name":"{model}"}}'

                This can take several minutes because the model is several GB.
                """
            ).strip()
        )


def generate_key_information(
    project_dir: Path,
    *,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    model: str = DEFAULT_MODEL,
    max_paper_chars: int = 60000,
) -> Path:
    ensure_model_available(ollama_url, model)

    prompt_path = project_dir / "prompt.md"
    paper_path = project_dir / "extracted" / "paper.md"
    figure_path = project_dir / "extracted" / "figures" / "FIGURE_CANDIDATES.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Missing {prompt_path}")
    if not paper_path.exists():
        raise FileNotFoundError(f"Missing {paper_path}")

    prompt = prompt_path.read_text(encoding="utf-8")
    paper = _read_limited(paper_path, max_paper_chars)
    figures = figure_path.read_text(encoding="utf-8", errors="replace") if figure_path.exists() else "No figure index found."

    user_prompt = f"""
    Follow the DOE highlight instructions below and write only the final
    paper_key_information.md content. Do not wrap it in backticks.

    # Instructions

    {prompt}

    # Paper Markdown

    {paper}

    # Figure Candidates

    {figures}
    """

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You create concise DOE/NQISRC/QSC highlight-slide input Markdown from research papers.",
            },
            {"role": "user", "content": user_prompt},
        ],
        "options": {
            "temperature": 0.2,
            "num_ctx": 32768,
        },
    }
    response = requests.post(f"{ollama_url}/api/chat", data=json.dumps(payload), timeout=600)
    response.raise_for_status()
    content = response.json()["message"]["content"].strip() + "\n"

    output = project_dir / "paper_key_information.md"
    output.write_text(content, encoding="utf-8")
    return output
