# Hardware style guide

This is the house style for KiCad projects. It exists so a reviewer can tell
"different" from "wrong" in under a minute. When a rule is broken on purpose,
write a decision record in `docs/decisions/` and link it from the schematic note.

## Repository

- Humans commit sources; CI produces everything else. Never commit gerbers, PDFs,
  STEP, ibom or renders. They come from KiBot on every PR and are attached to a
  GitHub Release on tags.
- Revision scheme is `VnRm` (`V1R2`). The git tag, the `REV` text variable, the
  silkscreen and the fab zip name are all that string. CI sets `REV` from the tag.
- Large binaries (Blender, PSD, video, curated renders) go through Git LFS.
- Every fab release gets a tag, a release and an entry in `docs/errata.md`.
- Close KiCad before scripted or git edits to `.kicad_pro`, `.kicad_sch` or
  `.kicad_pcb`. KiCad rewrites those files from memory on save and will
  silently discard outside changes.

## Schematic

- One subsystem per sheet. Sheet title blocks use `${TITLE} - <Subsystem>`,
  `${REV}`, `${COMPANY}` and a one-line purpose in comment 1.
- Net names are lowercase domain-kebab: `<domain>-<signal>[-<qualifier>]`.
  Examples: `pwm-a-high`, `isense-a`, `hall-b`, `enc-spi-cs`, `eth-irq`,
  `i2c-sda`, `usb-dp`, `vref-1v6`, `mcu-boot`. Power nets keep KiCad style:
  `+BATT`, `+5V`, `+3V3`, `GND`, `GND-USB`.
- Every net that crosses a sheet is a hierarchical pin or a global label; never
  rely on a power symbol as a signal.
- Every symbol carries `Manufacturer`, `MPN`, `LCSC Part`, `Datasheet` and
  `Description`. Blank is allowed only for generic passives, and the BOM step
  will show the blank.
- Every ERC exception has a decision record. ERC errors block merge; warnings
  are triaged into `docs/errata.md`.
- Each sheet has a notes block: purpose, key numbers (voltages, currents,
  frequencies), and the calculations behind component values.
- Custom symbols and footprints live in `specific-parts/`. Anything used on a
  second project gets promoted to the shared library repo.

## Layout

- Stackup is defined in Board Setup and matches the fab's stock stackup.
- Net classes drive track and via sizes. Do not hand-set widths that should be
  a class; if a net needs its own width, it needs its own class.
  Current classes (schematic colour in brackets): `Default` 0.2 mm,
  `GND` 0.356 mm (black), `3V3` 0.356 mm (gold), `5V` 0.356 mm (orange),
  `GND-USB` 0.356 mm (blue), `Batt` 1.0 mm (red), `Motor-A/B/C` 1.0 mm
  (yellow / green / blue, also coloured on the board). Colours are part of
  the house style: they make rail and phase mistakes visible at a glance.
- DRC runs with schematic parity and must have zero errors. Custom rules live
  in `pace-core.kicad_dru` with a comment linking the decision record.
  Point exclusions are not used; they go stale when parts move.
- Silkscreen: reference designators readable at 1 mm text, connector pin 1
  marked, polarity marked, `${REV}` and project name on the top silk.
- Test points are numbered `TP<n>` and listed in `docs/bringup.md`.
- Mechanical exchange goes through `mech/` (outline DXF in, board STEP out).

## Review

- Every design change is a PR. The kiri diff is the first thing a reviewer opens.
- The PR template checklist is the definition of done.
