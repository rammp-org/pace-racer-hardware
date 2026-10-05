# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the KiCad hardware repository for the **PACE V0 (RACER)** — a 3-phase motor controller board built around an ESP32-S3-WROOM-1. The companion firmware repo is `pace-racer-firmware`.

All KiCad project files live under `pace-core/`. The board targets 48V nominal input (up to 60V DC) and supports both FOC and trapezoidal commutation.

## KiCad Project Structure

The schematic is hierarchical with 5 sheets:
- `pace-core.kicad_sch` — root/top-level sheet
- `pace-connectors-sheet.kicad_sch` — connector definitions
- `pace-power-reg.kicad_sch` — power regulation (XL7015E1 buck → 5V, AMS1117 → 3.3V, REF35160 1.6V bias ref)
- `pace-mechanicals.kicad_sch` — sensing, mechanicals, config
- `pace-3-phase-inverter.kicad_sch` — gate driver (DRV8353) and 6x MOSFET half-bridge array

Custom footprints and symbols are in `pace-core/specific-parts/`:
- `specific-parts-lib.kicad_sym` — custom schematic symbols
- `specific-parts-lib.pretty/` — custom footprints
- `specific-parts-lib.3dshapes/` — custom 3D models

## Repository Layout and Hygiene Rule

**Humans commit sources; CI produces everything else.** Do not commit layer PDFs, STEP exports, ibom HTML, or other regenerable outputs into `pace-core/`. They are gitignored and CI (KiBot) rebuilds them.

- `pace-core/` — KiCad sources only (project, schematics, board, lib tables, custom library, KiBot config)
- `pace-core/production/` — archived fab packages for boards that were actually built (`Pace-RacerV0R1`, `Pace-RacerV1R2`: zip, BOM, positions, designators) plus `netlist.ipc`. Treat as historical record; new releases will come from CI on tags.
- `docs/` — documentation; `docs/media/renders/` holds curated renders and the Blender scene (Git LFS)
- `graphics/` — brand and silkscreen artwork (not KiCad project files)
- `_local/` — gitignored scratch area for regenerable exports and render frames

Git LFS is required (`brew install git-lfs && git lfs install`). Patterns are in `.gitattributes`.

## Tooling

A `.venv` at the repo root contains `easyeda2kicad` for importing parts from EasyEDA/LCSC into the custom parts library.

```bash
source .venv/bin/activate
easyeda2kicad --full --lcsc_id=C<LCSC_ID> --output pace-core/specific-parts/specific-parts-lib
```

CI is KiBot (`pace-core/.kibot.yaml`, `.github/workflows/kibot.yml`): ERC and DRC block PRs; outputs land in `pace-core/output/` (gitignored) and on GitHub Releases for `V*R*` tags. Verify locally with kicad-cli (`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`): `sch erc`, `pcb drc --schematic-parity`, `sch export netlist`.

## Key Design Notes

**Ground topology**: Two ground nets exist — `GND` (logic and power-stage return) and `GND-USB` (upstream USB, isolated by the ADUM3160 and bondable via `SW3`). `GNDPWR` symbols resolve to `GND`; there is no separate high-current ground net. See `docs/decisions/0001` and `0002`.

**Net naming**: lowercase domain-kebab (`pwm-a-high`, `isense-a`, `hall-b`, `spi-clk`, `eth-spi-cs`, `drv-spi-cs`, `enc-spi-*`, `i2c-sda`, `usb-dp`, `vref-1v6`, `mot-a`). Rules in `docs/style-guide.md`. Bulk renames go through `tools/rename_nets.py` with a JSON map and are verified with `tools/verify_netlist.py`.

**Net classes** (`pace-core.kicad_pro`) carry both widths and colours; keep the colours when editing: `Default` 0.2 mm, `GND` 0.356 mm black, `3V3` 0.356 mm gold, `5V`/`+5V-USB` 0.356 mm orange, `GND-USB` 0.356 mm blue, `Batt` 1.0 mm red, `Motor-A/B/C` (`mot-a/b/c`) 1.0 mm yellow/green/blue with matching PCB colours.

**DRC**: zero errors, zero point exclusions. The shunt net-tie overlaps are waived by a rule in `pace-core.kicad_dru` (see `docs/decisions/0003`). Known warnings are listed in `docs/errata.md`.

**Text variables**: `TITLE`, `PROJECT_CODE`, `REV`, `COMPANY` live in the project file and feed every sheet title block. CI overrides `REV` from the git tag (`VnRm`).

**SPI bus sharing**: `spi-clk/copi/cipo` (IO12/11/13) is shared by the W5500 (`eth-spi-cs`, IO10) and the DRV8353 (`drv-spi-cs`, IO39). The MT6701 encoder has its own bus (`enc-spi-*`, IO35/37/38).

**README pin map** is generated: run `tools/gen_readme.py --netlist <kicad sexpr netlist>` after any pin change; CI fails if it is stale.
