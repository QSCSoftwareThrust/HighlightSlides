# Logo Library

Store reusable PNG/JPG logo files here.

Policy for generated highlight slides:

- `../qsc-logo.png` is the fixed QSC logo and is inserted automatically when
  present.
- Per-paper logos should be used only for institution(s) that the paper supports
  as QSC-funded or QSC-supported.
- Do not include every author affiliation.
- Prefer full-color logo variants because the template places logos in a white
  band immediately above the blue footer. Keep white/knockout variants only as
  fallbacks for dark-background templates.
- Prefer official institution brand/media pages or official websites.
- Keep original aspect ratio. The deck generator sizes logos automatically.

Use `qsc_partner_logo_catalog.json` as the source-of-truth checklist:

- `ready_logos`: files that are already available locally and are reasonable to
  use when the paper supports that institution.
- `possible_qsc_partners_not_yet_downloaded`: current QSC partners that should
  not be used until a suitable logo file is added.
- `related_non_qsc_or_historical`: use only when the paper explicitly supports
  the institution as QSC-funded or QSC-supported.

Add files using the `slug` names when possible, for example:

```text
ornl.png
lanl.png
pnnl.png
caltech.png
```
