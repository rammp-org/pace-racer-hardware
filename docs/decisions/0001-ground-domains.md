# 0001 Ground domains and USB isolation

Status: accepted (V0R1)

The board has two ground nets, not three:

- `GND` is the logic ground and also the power-stage return. The `GNDPWR`
  power symbols on the inverter and power sheets are shorted to `GND` by the
  low-side shunt net ties, so KiCad merges them and ERC reports
  `multiple_net_names`. See 0002.
- `GND-USB` is the upstream, computer-side USB ground. It is separated from
  `GND` by the ADUM3160 digital isolator (U4). The DPDT switch SW3 can bond
  the two grounds for bench work where isolation is not wanted.

Why: a live 48 V power stage with a bench PC attached over USB is the most
common way to destroy a laptop port. Isolation is the default; bonding is a
deliberate switch action.
