# Kicad Hardware files and docs for the PACE V0 board (RACER)
Welcome to the official hardware repository for the **PACE V0 (RACER)** motor controller board. This repository contains all KiCad design schematics, layout files, and hardware documentation required to manufacture, test, and interface with the RACER platform. 
The companion firmware for this board is under active development in the companion repository: `pace-racer-firmware`.
<div align="center">
<img width="1050" height="750" alt="PaceRacerV0R1 Splash2" src="https://github.com/user-attachments/assets/a066d634-d60a-4260-9740-7f3dba9589d4" />


    
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
  * Discrete input lines for standard 3-phase Hall effect sensor elements (`A-halls`, `B-Halls`, `C-Halls`).
* **Thermal Management**: 4x LM75ADP I2C digital temperature monitors are distributed across key thermal zones on a single I2C bus. Fixed hardware addressing assigns them respectively to `0x4C`, `0x4D`, `0x4E`, and `0x4F`.

### 3. Communications & Safety
* **Wired Networking**: A Wiznet W5500 Ethernet Coprocessor configuration allows stable, high-throughput network communication over a shared high-speed SPI bus.
* **Galvanic Isolation**: The upstream USB-C debugging connection features an ADUM3160BRWZ-RL digital isolation chip to safely separate logic lines from high-voltage battery transient grounds (`GNDPWR`) during live tuning.

---

## Hardware Pin Mapping Reference

This register map serves as the single source of truth for constructing your firmware's hardware abstraction layer (e.g., `hal_pins.h`).

| ESP32-S3 Pin | Schematic Net Name | Destination Peripheral | Description / Implementation Guidance |
| :--- | :--- | :--- | :--- |
| **IO1 / ADC1_0** | `1V6-REF` | Internal ADC / Bias Reference | Monitors the 1.6V current-shunt offset reference voltage. |
| **IO4 / ADC1_3** | `A-isense` | Phase A Shunt Amplifier | Low-side shunt analog current feedback input. |
| **IO5 / ADC1_4** | `B-isense` | Phase B Shunt Amplifier | Low-side shunt analog current feedback input. |
| **IO6 / ADC1_5** | `C-isense` | Phase C Shunt Amplifier | Low-side shunt analog current feedback input. |
| **IO8 / ADC1_7** | `A-high` | DRV8353 INHA (`Pin 32`) | PWM Output: Phase A High-Side Switching. |
| **IO18** | `A-low` | DRV8353 INLA (`Pin 33`) | PWM Output: Phase A Low-Side Switching. |
| **IO17** | `B-high` | DRV8353 INHB (`Pin 34`) | PWM Output: Phase B High-Side Switching. |
| **IO16** | `B-low` | DRV8353 INLB (`Pin 35`) | PWM Output: Phase B Low-Side Switching. |
| **IO15** | `C-high` | DRV8353 INHC (`Pin 36`) | PWM Output: Phase C High-Side Switching. |
| **IO7 / ADC1_6** | `C-low` | DRV8353 INLC (`Pin 37`) | PWM Output: Phase C Low-Side Switching. |
| **IO19 / USBD-** | `usb_d-` | ADUM3160 Isolated Port | Hardware Native USB- Data Line. |
| **IO20 / USBD+** | `usb_d+` | ADUM3160 Isolated Port | Hardware Native USB+ Data Line. |
| **IO40** | `motor-fault` | DRV8353 nFAULT (`Pin 26`) | Active-Low Fault Input Interrupt (10k pull-up). |
| **IO39** | `drv-spi-cs` | DRV8353 nSCS (`Pin 30`) | Dedicated SPI Chip Select for Gate Driver configuration. |
| **IO38** | `enc-spi-cs` | MT6701 Encoder Port | Dedicated SPI Chip Select for Magnetic Encoder. |
| **IO37** | `enc-spi-clk` | MT6701 Encoder Port | Dedicated SPI Clock Line for Magnetic Encoder. |
| **IO35** | `enc-spi-cipo` | MT6701 Encoder Port | SPI Master In / Slave Out data from Encoder. |
| **IO45 / SPI-V** | `12c-SDA` | Local Temperature Sensors | Shared I2C Data Line (10k external pull-up). |
| **IO48** | `12c-SCL` | Local Temperature Sensors | Shared I2C Clock Line (10k external pull-up). |
| **IO10 / FSPI-CS** | `comm-spi-cs` | W5500 Ethernet Coprocessor | Dedicated SPI Chip Select for Ethernet Controller. |
| **IO12 / FSPI-CLK** | `comm-spi-clk` | W5500 Ethernet / DRV8353 | Shared High-Speed Communications SPI Clock. |
| **IO11 / FSPI-D** | `comm-spi-copi` | W5500 Ethernet / DRV8353 | Shared High-Speed Communications SPI MOSI. |
| **IO13 / FSPI-Q** | `comm-spi-cipo` | W5500 Ethernet / DRV8353 | Shared High-Speed Communications SPI MISO. |
| **IO14** | `comm-irq` | W5500 Ethernet Controller | Hardware Event Line Input Interrupt. |
| **IO21** | `comm-reset` | W5500 Ethernet Controller | Hardware Device Reset Control Line. |
| **IO3 / ADC1-2** | `A-halls` | Hall Sensor Input Header | Discrete Input Phase A Hall Effect (10k pull-up). |
| **IO46** | `B-Halls` | Hall Sensor Input Header | Discrete Input Phase B Hall Effect (10k pull-up). |
| **IO9 / ADC1-8** | `C-Halls` | Hall Sensor Input Header | Discrete Input Phase C Hall Effect (10k pull-up). |
| **IO42** | `blue-ind` | Diagnostic LED Blue | Hardware status indicator light. |
| **IO41** | `green-ind` | Diagnostic LED Green | Hardware status indicator light. |

---

## Power Distribution & Topology

The RACER PCB layout handles standard heavy industrial current loops alongside sensitive logic rails. Care must be taken during low-level development to understand the distinct ground rules and supply behavior.

* **Main DC Power Stage Input (`+BATT`)**: Accepts high-voltage input up to 60V DC. High and low-frequency buffer capacitor banks are placed immediately across each half-bridge phase to suppress heavy inductive switching ripples up to 25MHz.
* **Logic Subsystem Buck (5V Rail)**: Driven by an XL7015E1 high-voltage buck regulator topology, dropping the high-voltage input down to a common local 5V line.
* **Microcontroller Supply (3.3V Rail)**: An AMS1117-3.3 linear regulator drops the local 5V line to a stable 3.3V rail dedicated to powering the ESP32-S3 and onboard sensors.
* **Analog Ingestion Bias Reference (`1V6-REF`)**: Formed via a REF35160QDBVR high-precision reference generator connected to the 5V line. This outputs a fixed 1.6V reference bias to calibrate the inline current shunt amplifiers, permitting measurement of negative and positive phase currents across the full bi-directional stroke.
* **Isolation Boundary Notice**: The 5V-USB rail is strictly limited to powering the upstream digital isolator components. Flipping the physical isolation switch (`SW3`) cleanly detaches the target ground (`GND`) from development computer USB shields (`GND-USB`) to protect computer infrastructure against high-power faults.

---

## First-Stage Firmware Initialization Blueprint

To quickly bring up prototype firmware on `pace-racer-firmware`, organize your driver initializations using this execution checklist:

### Phase 1: Core Systems & Diagnostic Telemetry
1. Define the physical I/O allocations outlined in the pin reference table.
2. Initialize diagnostic LEDs (`IO41`, `IO42`) to indicate a booting state.
3. Fire up the shared I2C bus over `IO45` and `IO48` to loop and register responses from the four LM75ADP temperature sensor configurations at addresses `0x4C` through `0x4F`. 

### Phase 2: Inverter Protection & Commutation Interfaces
1. Configure `IO40` (`motor-fault`) as an active-low hardware interrupt line. Ensure its handler instantly forces all PWM generation lines into a low (disabled) safety state if triggered.
2. Initialize the main SPI communications bus over pins `IO11`, `IO12`, and `IO13`. Pull the gate driver chip select (`IO39`) low to configure the DRV8353 operational state registers.
3. For **Field-Oriented Control (FOC)**, configure high-speed SPI capture over the encoder subsystem (`IO35`, `IO37`, `IO38`) to decode magnetic orientation data from the MT6701.
4. For **Trapezoidal Commutation**, establish change-of-state interrupt routines tracking discrete pin changes across Hall effect inputs (`IO3`, `IO46`, `IO9`).

### Phase 3: Ethernet Networking
1. Cycle the hardware reset pin `IO21` to clear the internal registers of the W5500 Ethernet chip.
2. Configure SPI tracking over the controller chip select pin `IO10`.
3. Initialize the raw sockets over network stacks using the standard `comm-irq` (`IO14`) interrupt pin to manage incoming and outgoing network interface events without blocking the high-frequency motor control loops.
