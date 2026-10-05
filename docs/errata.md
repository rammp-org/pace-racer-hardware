# Errata and known warnings

## Known ERC/DRC warnings (not errors)

| Check | Count | Why it is tolerated | Fix planned |
| :-- | :-- | :-- | :-- |
| ERC `pin_to_pin` (Unspecified pins) | ~195 | Imported symbols from EasyEDA carry `unspecified` pin types | Assign pin types when parts are promoted to the shared library |
| ERC `lib_symbol_mismatch` | ~15 | Embedded symbol copies drifted from the library | Run *Update Symbols from Library* in the GUI and commit |
| ERC `multiple_net_names` GND/GNDPWR | 1 | See decisions/0002 | Decide GNDPWR split in V2 |
| DRC `lib_footprint_mismatch` | 6 | Embedded footprints drifted from library (C17, USB1, U6, C19..C21) | Run *Update Footprints from Library* and commit |
| DRC `connection_width` on ground pour | 5 | Thin necks in the pour between vias | Widen pour necks in the next layout pass |

## Open design items

- `C5` (47uF 100V) is deliberately not fitted: the buck converter's bulk input capacitance is shared with the motor-drive DC-link caps (C19..C21). Mark it DNP in the schematic so the BOM and parity stay clean.
- Passives lack MPN and LCSC fields; the BOM shows blanks. Fill from the
  assembly quote when the next order is placed.

## Board revision history

| Rev | Built | Notes |
| :-- | :-- | :-- |
| V0R1 | yes | First article. Fab package archived under production/ until retro-tagged. |
| V1R2 | in progress | Re-packaged connectors and layout. |
