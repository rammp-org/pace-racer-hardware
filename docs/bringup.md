# Bring-up checklist

Fill in per board serial. Copy this file to `docs/bringup/<rev>-<serial>.md`.

1. Visual: solder bridges on U1, U2, USB1; polarity on C19..C21, D4.
2. Power off: resistance `+BATT` to `GND` (> 10 kΩ), `+5V` to `GND`, `+3V3` to `GND`.
3. Bench supply 12 V, 100 mA limit on `+BATT`: measure `+5V`, `+3V3`, `vref-1v6`.
4. USB with SW3 in isolated position: ESP32 enumerates; measure `GND-USB` to `GND` (open).
5. Flash firmware, LEDs blink, I2C scan finds `0x4C`..`0x4F`.
6. DRV8353 SPI: read device ID; nFAULT high.
7. Encoder SPI: MT6701 angle reads.
8. Motor, 12 V, no load: open-loop spin each direction; check phase current waveforms.
9. Raise to 48 V; thermal check after 5 min at target current.
