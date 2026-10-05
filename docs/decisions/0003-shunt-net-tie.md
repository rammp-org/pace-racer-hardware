# 0003 Shunt net-tie clearance rule

Status: accepted (V1R2)

The three low-side shunts (R1, R2, R3) use a net-tie footprint (NT1..NT3,
`specific-parts-lib:shunt-net-tie`) to make a Kelvin connection: the sense
net (`shunt-x-n`) and `GND` meet only at the shunt pad. The net-tie pads
intentionally overlap the shunt pads and sit inside the ground pour.

KiCad's default clearance flags those overlaps. Instead of point exclusions
(which were stale after the V1 re-layout), `pace-core.kicad_dru` waives
clearance for anything touching NT1..NT3. The bridge copper inside the
footprint is now part of pad 2 as a custom pad shape, so no free copper
polygon exists and `shorting_items` no longer fires.

Consequence: DRC in CI runs with zero exclusions. If the net tie moves or a
fourth shunt is added, extend the rule condition.
