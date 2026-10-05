# PACE Racer motor controller (KiCad hardware)
Welcome to the official hardware repository for the **PACE V0 (RACER)** motor controller board. This repository contains all KiCad design schematics, layout files, and hardware documentation required to manufacture, test, and interface with the RACER platform. 
The companion firmware for this board is under active development in the companion repository: `pace-racer-firmware`.

**How this repo works:** humans commit KiCad sources; CI (KiBot) runs ERC and DRC on every PR and builds gerbers, BOM, position, ibom, PDFs, STEP and renders. Tagging `VnRm` publishes those as a GitHub Release. See `docs/style-guide.md` for conventions and `docs/decisions/` for the why behind unusual choices.
<div align="center">
<img width="1050" height="750" alt="PaceRacerV0R1 Splash2" src="https://github.com/user-attachments/assets/96b0adf5-5786-436b-93e1-1e5da7add888" />

## Documentation & Resources
### Access the [schematics and an interactive board viewer here!](https://kicanvas.org/?repo=https%3A%2F%2Fgithub.com%2Frammp-org%2Fpace-racer-hardware%2Ftree%2Fmain%2Fpace-core)
<a href="https://kicanvas.org/?repo=https%3A%2F%2Fgithub.com%2Frammp-org%2Fpace-racer-hardware%2Ftree%2Fmain%2Fpace-core">
  <img width="1000" height="300" alt="Access Interactive KiCanvas Board Viewer & Schematics" src="https://github.com/user-attachments/assets/14aa4976-df60-4273-b14f-487551fd1604" />
</a>
---

<div align="left">

## Hardware Architecture Overview

The PACE V0 (RACER) is a high-performance, intelligent 3-phase inverter platform powered by an ESP32-S3. It is engineered to support both high-frequency **Field-Oriented Control (FOC)** and traditional **Trapezoidal (Block) Commutation** strategies. 

``` mermaid
flowchart TD
    %% Upstream USB Environment
    subgraph Upstream ["Upstream Side (Isolated USB Environment)"]
        USB["USB-C Connector<br>(USB1)"] -->|VBUS / GND_USB| VUSB["+5V-USB Rail<br>& GND-USB Rail"]
        VUSB -->|Powers Upstream Side| ISO_In["ADUM3160 Digital Isolator<br>(U4 Upstream Pins)"]
    end

    %% Galvanic Isolation Barrier
    subgraph Barrier ["Galvanic Isolation Boundary"]
        ISO_In -.->|Optical/Magnetic Data Isolation| ISO_Out["ADUM3160 Digital Isolator<br>(U4 Downstream Pins)"]
        SW3{"SW3 Switch<br>(DPDT)"}
    end

    %% High Voltage Input Power Stage
    subgraph HV_Stage ["High-Voltage Input Power Stage"]
        BATT["+BATT Input Rail<br>(48V Nominal Target)"] --> Caps["DC-Link Capacitor Buffers<br>(100V Continuous Rating Limit)"]
        Caps --> XLBuck["XL7015E1 Buck Converter<br>(U6 Stage)"]
    end

    %% Main Logic Subsystems
    subgraph Logic_Rails ["Downstream Logic & Control Subsystem"]
        XLBuck -->|Step Down| V5["+5V Local Rail"]
        
        V5 -->|Linear Regulation| AMS["AMS1117-3.3 LDO (U5)"]
        AMS -->|Logic Power| V33["+3V3 Main MCU Rail"]
        
        V5 -->|Precision Division| REF["REF35160 Reference IC (U7)"]
        REF -->|ADC Baseline Shift| V16["1V6-REF Precision Rail"]
        
        V33 -->|Powers MCU| MCU["ESP32-S3 Processing Core<br>(System GND)"]
        V16 -->|Shunt Offset Bias| MCU
        ISO_Out -->|Isolated USB Signals| MCU
    end

    %% Isolation Mode Controls
    VUSB -->|Route Bus Voltage| SW3
    SW3 -->|Flipped State: Breaks Ground Loops| Logic_Rails
```

### 1. Processing & Inverter Stage
* **Core MCU**: An ESP32-S3-WROOM-1 module handles raw motor control mathematics, wireless telemetry, and hardware interrupt management.
* **Gate Driver**: A TI DRV8353SRTAT 3-phase gate driver provides independent high-side/low-side drive configurations, hardware fault line triggers, and runtime register adjustments via SPI.
* **Power MOSFETs**: 6x ISC0802NLSATMA1 MOSFETs are structured in a traditional 3-phase half-bridge bridge array.
* **Current Sensing**: Dual-purpose inline, low-side 1.0 mΩ current sense shunts (`R1`, `R2`, `R3`) are deployed on all three phases to capture fast current waveforms for precision FOC.

### 2. Sensor Framework
* **Rotor Position Feedback**: Supports dual encoder paradigms:
  * High-speed SPI telemetry via the MT6701 Magnetic Rotary Encoder interface.
  * Discrete input lines for standard 3-phase Hall effect sensor elements (`hall-a`, `hall-b`, `hall-c`).
* **Thermal Management**: 4x LM75ADP I2C digital temperature monitors are distributed across key thermal zones on a single I2C bus. Fixed hardware addressing assigns them respectively to `0x4C`, `0x4D`, `0x4E`, and `0x4F`.

### 3. Communications & Safety
* **Wired Networking**: A Wiznet W5500 Ethernet Coprocessor configuration allows stable, high-throughput network communication over a shared high-speed SPI bus.
* **Galvanic Isolation**: The upstream USB-C debugging connection features an ADUM3160BRWZ-RL digital isolation chip to safely separate logic lines from high-voltage battery transient grounds (see `docs/decisions/0001-ground-domains.md`) during live tuning.

---

## Hardware Pin Mapping Reference

This table is generated from the schematic netlist by `tools/gen_readme.py` and checked in CI. Do not edit it by hand.
Net names follow `docs/style-guide.md` (lowercase domain-kebab); the firmware `hal_pins.h` should use these names.

<!-- BEGIN GENERATED: pinmap -->
| MCU pin | Net | Connected to |
| :-- | :-- | :-- |
| IO0/st-boot (pin 27) | `mcu-boot` | R8, SW1 |
| RXD0 (pin 36) | `uart-rx` | J4 |
| TXD0 (pin 37) | `uart-tx` | J4 |
| IO1/adc1-0 (pin 39) | `vref-1v6` | C23, C27, TP24, U2, U7 |
| IO2/adc1-1 (pin 38) | `mcu-io2` | J4 |
| IO3/st-jtag/adc1-2 (pin 15) | `hall-a` | C42, R34 |
| IO4/adc1-3 (pin 4) | `isense-a` | C30, R10 |
| IO5/adc1-4 (pin 5) | `isense-b` | C29, R21 |
| IO6/adc1-5 (pin 6) | `isense-c` | C28, R22 |
| IO7/adc1-6 (pin 7) | `pwm-c-low` | R26, U2 |
| IO8/adc1-7 (pin 12) | `pwm-a-high` | R31, U2 |
| IO9/adc1-8 (pin 17) | `hall-c` | C40, R25 |
| IO10/adc1-9/FSPI-CS (pin 18) | `eth-spi-cs` | J2, R23 |
| IO11/FSPI-D (pin 19) | `spi-copi` | J2, U2 |
| IO12/FSPI-CLK (pin 20) | `spi-clk` | J2, U2 |
| IO13/FSPI-Q (pin 21) | `spi-cipo` | J2, R17, U2 |
| IO14 (pin 22) | `eth-irq` | J2 |
| IO15 (pin 8) | `pwm-c-high` | R27, U2 |
| IO16 (pin 9) | `pwm-b-low` | R28, U2 |
| IO17 (pin 10) | `pwm-b-high` | R29, U2 |
| IO18 (pin 11) | `pwm-a-low` | R30, U2 |
| IO19/USBD- (pin 13) | `usb-dm` | U4 |
| IO20/USBD+ (pin 14) | `usb-dp` | U4 |
| IO21 (pin 23) | `eth-reset` | J2 |
| IO35 (pin 28) | `enc-spi-cipo` | U12 |
| IO36 (pin 29) | `enc-spi-copi` | J4, U12 |
| IO37 (pin 30) | `enc-spi-clk` | U12 |
| IO38 (pin 31) | `enc-spi-cs` | R24, U12 |
| IO39 (pin 32) | `drv-spi-cs` | U2 |
| IO40 (pin 33) | `drv-fault` | R16, U2 |
| IO41 (pin 34) | `led-green` | D2, J4 |
| IO42 (pin 35) | `led-blue` | D1, J4 |
| IO45/st-spi-v (pin 26) | `i2c-sda` | J4, R39, U10, U11, U8, U9 |
| IO46/st-rom (pin 16) | `hall-b` | C41, R33 |
| IO47 (pin 24) | `drv-enable` | R32, U2 |
| IO48 (pin 25) | `i2c-scl` | J4, R40, U10, U11, U8, U9 |
| EN (pin 3) | `mcu-reset` | R9, SW2 |
<!-- END GENERATED: pinmap -->

---

## Power Distribution & Topology

The RACER PCB layout handles standard heavy industrial current loops alongside sensitive logic rails. Care must be taken during low-level development to understand the distinct ground rules and supply behavior.

* **Main DC Power Stage Input (`+BATT`)**: Accepts high-voltage input up to 60V DC. High and low-frequency buffer capacitor banks are placed immediately across each half-bridge phase to suppress heavy inductive switching ripples up to 25MHz.
* **Logic Subsystem Buck (5V Rail)**: Driven by an XL7015E1 high-voltage buck regulator topology, dropping the high-voltage input down to a common local 5V line.
* **Microcontroller Supply (3.3V Rail)**: An AMS1117-3.3 linear regulator drops the local 5V line to a stable 3.3V rail dedicated to powering the ESP32-S3 and onboard sensors.
* **Analog Ingestion Bias Reference (`vref-1v6`)**: Formed via a REF35160QDBVR high-precision reference generator connected to the 5V line. This outputs a fixed 1.6V reference bias to calibrate the inline current shunt amplifiers, permitting measurement of negative and positive phase currents across the full bi-directional stroke.
* **Isolation Boundary Notice**: The 5V-USB rail is strictly limited to powering the upstream digital isolator components. Flipping the physical isolation switch (`SW3`) cleanly detaches the target ground (`GND`) from development computer USB shields (`GND-USB`) to protect computer infrastructure against high-power faults.

---

## First-Stage Firmware Initialization Blueprint

To quickly bring up prototype firmware on `pace-racer-firmware`, organize your driver initializations using this execution checklist:

### Phase 1: Core Systems & Diagnostic Telemetry
1. Define the physical I/O allocations outlined in the pin reference table.
2. Initialize diagnostic LEDs (`IO41`, `IO42`) to indicate a booting state.
3. Fire up the shared I2C bus over `IO45` and `IO48` to loop and register responses from the four LM75ADP temperature sensor configurations at addresses `0x4C` through `0x4F`. 

### Phase 2: Inverter Protection & Commutation Interfaces
1. Configure `IO40` (`drv-fault`) as an active-low hardware interrupt line. Ensure its handler instantly forces all PWM generation lines into a low (disabled) safety state if triggered.
2. Initialize the main SPI communications bus over pins `spi-copi`, `spi-clk`, and `spi-cipo`. Pull the gate driver chip select (`IO39`) low to configure the DRV8353 operational state registers.
3. For **Field-Oriented Control (FOC)**, configure high-speed SPI capture over the encoder subsystem (`IO35`, `IO37`, `IO38`) to decode magnetic orientation data from the MT6701.
4. For **Trapezoidal Commutation**, establish change-of-state interrupt routines tracking discrete pin changes across Hall effect inputs (`IO3`, `IO46`, `IO9`).

### Phase 3: Ethernet Networking
1. Cycle the hardware reset pin `IO21` to clear the internal registers of the W5500 Ethernet chip.
2. Configure SPI tracking over the controller chip select pin `IO10`.
3. Initialize the raw sockets over network stacks using the standard `eth-irq` (`IO14`) interrupt pin to manage incoming and outgoing network interface events without blocking the high-frequency motor control loops.
