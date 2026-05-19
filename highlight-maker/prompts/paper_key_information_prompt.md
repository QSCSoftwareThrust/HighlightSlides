You are preparing input for a DOE Office of Science highlight slide for an
NQISRC/QSC paper.

Read the paper Markdown and any available extracted figure list. Produce exactly
one file named `paper_key_information.md` using the structure below.

Rules:

- Use plain language for a mixed technical and non-technical DOE audience.
- Do not invent results, facilities, funding roles, acknowledgements, DOI, or
  institutional contributions. Use `Unknown` when the paper does not support an
  answer.
- Define acronyms on first use unless they are universally known.
- Keep `Scientific Achievement` to 50 words or fewer.
- Keep `Significance and Impact` to 50 words or fewer.
- Use 2-4 concise bullets for `Research Details`.
- Choose one recommended figure from the extracted candidates when possible.
  Prefer `crops/...` image-only candidates over full `pages/...` renderings.
  Use full-page renderings only as a fallback because they can include
  surrounding paper text.
- If the paper has more than six authors, format `Citation` as
  `<First Author> et al., "<Title>", <venue/arXiv>, <year>.`
- `Citation` must include only the authors, paper title, and arXiv ID or DOI.
  Do not include acknowledgements, funding statements, facilities, or extra
  institutional text in `Citation`.
- Do not write speaker notes.
- The final PowerPoint will use only the first two slides of
  `FY26_Highlight_Template.pptx`.
- In `Recommended Figure`, include the relative path to the recommended image
  candidate when possible, for example
  `extracted/figures/crops/page-016-image-00.png`.
- The QSC logo is added automatically by the PowerPoint generator. Do not list
  QSC/NQISRC in `Institution Logos`.
- For `Institution Logos`, identify only the institution or institutions that
  the paper supports as being funded by, supported by, or directly performing
  QSC/NQISRC-funded work. Do not include every author affiliation. Do not
  include general facilities or unrelated funders unless the paper links them to
  the QSC-supported contribution.
- If web access is available, download official PNG or JPG logo files into the
  project `logos/` directory. Use official institutional pages, press kits, or
  brand pages when possible. Do not use low-resolution screenshots or images
  with unrelated text. Do not use SVG files unless you convert them to PNG/JPG.
- Before searching the web, check the reusable logo library at
  `assets/logos/qsc_partner_logo_catalog.json` and `assets/logos/` when those
  paths are available from the current workspace. Use files from `ready_logos`
  only when the paper supports that institution as QSC-funded or
  QSC-supported. Do not use `possible_qsc_partners_not_yet_downloaded` entries
  unless you first download a suitable official logo file.
- Prefer white/knockout logo variants because the template places logos on the
  blue bottom band.
- In `Institution Logos`, list one bullet per logo using this format:
  `- <Institution name>: logos/<filename>.png`
- If a logo cannot be found or downloaded reliably, write
  `- <Institution name>: Unknown`.
- The PowerPoint generator will always include the QSC logo when
  `assets/qsc-logo.png` is available, and will preserve each logo's aspect
  ratio in the bottom slide-1 logo band.
- Slide 2 will follow the guidance in `FY26_Highlight_Template.pptx` slide 8:
  `NQISRC Intellectual Role` and `NQISRC Funding Role` must be selected only
  from the supported paper evidence, and `Funding Institution Contributions`
  must delineate what each funding source contributed and why multiple funded
  projects or facilities are appropriate to mention.

Slide 2 input rules:

- Build slide 2 from the paper's acknowledgements, funding statement, author
  affiliations, facility-use statement, and any contribution statements.
- `NQISRC Intellectual Role` must be exactly one of:
  - `Lead`: use only when QSC/NQISRC is clearly the lead institution or primary
    intellectual driver of the published result.
  - `Collaborator`: use when QSC/NQISRC is one of several roughly equal
    contributing institutions or projects.
  - `Minor`: use when QSC/NQISRC contributed to work led mainly outside the
    center.
  - `Unknown`: use when the paper acknowledges QSC/NQISRC funding but does not
    support an intellectual-role classification.
- `NQISRC Funding Role` must be exactly one of:
  - `Sole`: use only when QSC/NQISRC is the only stated funding source.
  - `Majority`: use only when the paper supports that QSC/NQISRC provided most
    of the support.
  - `Minority`: use when QSC/NQISRC is one of several funding sources and the
    paper does not support majority or sole support.
  - `Unknown`: use when funding shares cannot be inferred safely.
- For `Funding Institution Contributions`, write one bullet per funding source,
  facility, or program using this format:
  `- <Funding source/facility/program>: <specific contribution supported by the paper>.`
- Contribution bullets should explain why each source belongs on slide 2, for
  example student/postdoc support, user facility computing time, laboratory
  operations support, complementary project scope, or direct QSC/NQISRC support.
- If the paper names a funding source but does not state its specific role,
  write a conservative contribution such as
  `<source>: acknowledged as supporting the work; specific role not stated.`
- Do not infer funding percentages from author order, affiliations, or grant
  count. Use `Unknown` when the paper is not explicit.

Output format:

```markdown
# Paper Key Information

## Highlight Title

## Scientific Achievement

## Significance and Impact

## Research Details
- 

## Recommended Figure

## Figure Caption

## Citation

## DOI

## Acknowledgements

## User Facilities

## Institution Logos
- 

## NQISRC Intellectual Role
Lead | Collaborator | Minor | Unknown

## NQISRC Funding Role
Sole | Majority | Minority | Unknown

## Funding Institution Contributions
- 
```
