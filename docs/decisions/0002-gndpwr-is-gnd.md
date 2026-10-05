# 0002 GNDPWR symbols resolve to GND

Status: accepted with an open question

`GNDPWR` symbols are used on the inverter and power sheets to show intent
(power-stage return), but the low-side shunt net ties connect that return to
`GND`, so there is one net. ERC reports one `multiple_net_names` warning for
this and the netlist uses `GND`.

The former `High-Current-GND` net class matched a net (`GND-HC`) that never
existed and was removed in the V1R2 cleanup. The power-stage return relies on
the ground pours, not on a class.

Open question for V2: either replace the `GNDPWR` symbols with `GND` to
silence the warning, or make the split real with a single-point net tie at the
shunts and a dedicated pour. Decide before the next layout change in the
inverter area.
