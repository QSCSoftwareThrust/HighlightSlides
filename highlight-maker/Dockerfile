FROM codercom/code-server:4.98.2

ARG DEBIAN_FRONTEND=noninteractive
ARG INSTALL_LLM_CLIS=true

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    WORKDIR=/work

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        build-essential \
        ca-certificates \
        curl \
        git \
        gnupg \
        jq \
        nodejs \
        npm \
        poppler-utils \
        procps \
        python3 \
        python3-pip \
        python3-venv \
        socat \
        tini \
        unzip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /work /work/input /work/output /work/cache /work/templates /work/projects \
    && chown -R coder:coder /work

RUN python3 -m venv /opt/highlight-venv \
    && /opt/highlight-venv/bin/python -m pip install --upgrade pip \
    && /opt/highlight-venv/bin/python -m pip install \
        "markitdown[pdf]" \
        "pymupdf" \
        "Pillow" \
        "python-pptx" \
        "requests" \
        "typer[all]" \
        "pydantic" \
        "rich"

RUN ln -sf /opt/highlight-venv/bin/python /usr/local/bin/python \
    && ln -sf /opt/highlight-venv/bin/pip /usr/local/bin/pip \
    && ln -sf /opt/highlight-venv/bin/highlight /usr/local/bin/highlight

RUN if [ "$INSTALL_LLM_CLIS" = "true" ]; then \
        npm install -g @openai/codex @anthropic-ai/claude-code; \
    fi

WORKDIR /workspaces/highlight-maker
COPY --chown=coder:coder . /workspaces/highlight-maker
RUN /opt/highlight-venv/bin/pip install -e .

ENV PATH="/opt/highlight-venv/bin:${PATH}"

USER coder
EXPOSE 8080
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash"]
