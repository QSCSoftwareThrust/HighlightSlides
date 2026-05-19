# Create DOE Highlight Slides From a Paper

You are running in the DOE/NQISRC/QSC highlight-maker project. This may be a
host Python environment or the container environment. The user will ask for a
highlight slide input from a paper, usually with a request like:

```text
Read highlight.md and create the highlight slides for 2601.03185.
```

If the user has not logged in to Codex yet, tell them to run either:

```bash
codex login --device-auth
```

or:

```bash
codex login
```

In the host Python environment, browser login should use the machine's normal
browser. In the container, device authentication is usually more reliable.

If Codex and Claude login are unavailable and Ollama is available, use the local
Ollama workflow:

```bash
curl http://ollama:11434/api/tags
curl http://ollama:11434/api/pull -d '{"name":"gemma3n:e4b"}'
highlight local <PAPER_SOURCE> --insecure-tls --model gemma3n:e4b
```

If the first `curl` cannot connect in the container, the container was not
started with the local LLM profile. Ask the user to restart it from the host
with:

```bash
docker compose --profile local-llm up --build
```

This writes `paper_key_information.md` directly in the generated project folder.

The paper source may be:

- an arXiv ID, such as `2601.03185`
- an arXiv URL, such as `https://arxiv.org/abs/2601.03185`
- a local PDF path

## Required Output

Create these files in the generated project folder:

```text
paper_key_information.md
output/highlight_slides.pptx
```

Use `FY26_Highlight_Template.pptx` as the PowerPoint template. The output deck
must contain only the first two highlight slides populated from
`paper_key_information.md`.

## Workflow

1. Identify the paper source from the user's request.
2. Run the deterministic preparation command:

```bash
highlight <PAPER_SOURCE>
```

If the command fails with a certificate verification error, rerun it with:

```bash
highlight <PAPER_SOURCE> --insecure-tls
```

3. Read the command output and identify the generated project directory. It will
usually be one of these:

```text
/work/projects/arxiv-<ARXIV_ID_WITH_DASHES>
./work/arxiv-<ARXIV_ID_WITH_DASHES>
```

For example:

```text
/work/projects/arxiv-2601-03185
./work/arxiv-2601-03185
```

4. Change into the generated project folder.
5. Read `prompt.md`.
6. Read every file that `prompt.md` points to, especially:

```text
extracted/paper.md
extracted/figures/FIGURE_CANDIDATES.md
```

7. Write `paper_key_information.md` in the project root using exactly the
structure requested by `prompt.md`.
8. Run the deck generation command with the generated project name:

```bash
highlight deck --project arxiv-<ARXIV_ID_WITH_DASHES>
```

For example:

```bash
highlight deck --project arxiv-2601-03185
```

## Content Rules

- Use plain language for a mixed technical and non-technical DOE audience.
- Do not invent results, acknowledgements, DOI, funding roles, facilities, or
  institutional contributions.
- Use `Unknown` when the paper does not support an answer.
- For slide 2, follow the detailed role/funding rubric in the generated
  `prompt.md`. Do not guess QSC/NQISRC intellectual role or funding share from
  author order, affiliation count, or grant count.
- Format slide 2 funding-contribution bullets as:
  `- <Funding source/facility/program>: <specific contribution supported by the paper>.`
- Keep `Scientific Achievement` to 50 words or fewer.
- Keep `Significance and Impact` to 50 words or fewer.
- Use 2-4 concise bullets for `Research Details`.
- Recommend one figure candidate when possible.
- The QSC logo is handled automatically by the deck generator. For
  `Institution Logos`, only find/download official PNG/JPG logos for the
  institution or institutions that the paper supports as QSC-funded or
  QSC-supported. Check `assets/logos/` and
  `assets/logos/qsc_partner_logo_catalog.json` before searching the web. Do not
  list every author affiliation.
- Do not write speaker notes.
- Do not modify the PowerPoint template in place. Write a new output deck.

## Final Response To User

When done, report:

- the project directory
- the path to `paper_key_information.md`
- the path to `output/highlight_slides.pptx`
- any fields that remain `Unknown`
- any figure candidate you recommend
