## What changed

<!-- One or two sentences. Link the issue or decision record if there is one. -->

## Review checklist

Schematic
- [ ] ERC has zero errors; any new warning is listed in `docs/errata.md`
- [ ] Every new symbol has Manufacturer, MPN and LCSC Part filled (or explicitly blank with a note)
- [ ] Net names follow `docs/style-guide.md` (lowercase domain-kebab)
- [ ] Sheet title blocks and notes updated where the circuit changed

Layout
- [ ] DRC has zero errors with schematic parity on; no new exclusions without a decision record
- [ ] New nets are in the right net class; no hand-set track widths that should be a class
- [ ] Silkscreen refs, polarity marks and connector labels checked on the kiri diff
- [ ] Board STEP exported and mechanical owner notified if outline, holes or tall parts moved

Repo
- [ ] No generated outputs committed (PDF, STEP, ibom, gerbers)
- [ ] `README.md` generated sections pass the CI check
- [ ] Revision text variable bumped if this PR is a fab release
