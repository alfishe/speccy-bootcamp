[← Home](../README.md) · [References](README.md)

# Pinouts — ZX Spectrum Chip and Connector Reference

Pin-by-pin reference for every chip, bus, and connector on the ZX Spectrum and its clones: the 48K edge connector, the Z80 CPU, the AY-3-8912 sound chip, joystick ports, the Kempston mouse, and the tape/EAR/MIC jacks. For the *concepts* of bus protocols (timing, control signals, partial decoding), see the linked deep-dive articles.

> [!NOTE]
> This article is the **raw pinout table** — voltage levels, signal names, direction. You come here when wiring a cable or designing an adapter. For bus cycle timing, see [timing_reference.md](timing_reference.md); for I/O port decoding logic, see [io_port_map.md](io_port_map.md).

---

## Spectrum 48K / 128K / +2 Expansion Edge Connector

The expansion edge connector is a 2×28-way (56-pin) PCB edge with 0.1-inch pitch. The pin numbering convention: component side is **A** (pins A1–A28), solder side is **B** (pins B1–B28), numbered from the rear-panel (joystick/TV) end of the board toward the front. The same connector is fitted to the 48K, 128K, and grey +2; the +2A/+3 use a slightly different pin assignment because the AY chip moved.

### Pin Numbering Diagram

```
       Component side (top)          Solder side (bottom)
       ─────────────────────         ─────────────────────
       A1  A2 ... A28                B1  B2 ... B28
       │   │      │                  │   │      │
       └───┴──────┴──────────────────┴───┴──────┘
                              ▲
                              │
                  Rear of Spectrum (TV/EAR jacks)
```

Insert an expansion cartridge component-side **down** — the SIL/SIMM-style notch faces away from the rear of the machine.

### Component Side (Pins A1–A28)

| Pin | Signal | Dir | Description |
|---|---|---|---|
| A1 | `A15` | OUT | Z80 address bus, bit 15 (MSB) |
| A2 | `A14` | OUT | Z80 address bus, bit 14 |
| A3 | `A13` | OUT | Z80 address bus, bit 13 |
| A4 | `A12` | OUT | Z80 address bus, bit 12 |
| A5 | `A11` | OUT | Z80 address bus, bit 11 |
| A6 | `A10` | OUT | Z80 address bus, bit 10 |
| A7 | `A9` | OUT | Z80 address bus, bit 9 |
| A8 | `A8` | OUT | Z80 address bus, bit 8 (high byte) |
| A9 | `GND` | — | Ground (0 V) |
| A10 | `+5V` | PWR | +5 V regulated supply, max ~700 mA on 48K issue 2, ~1.5 A on issue 6+ |
| A11 | `–5V` | PWR | –5 V (used only by DRAM, not on later models) |
| A12 | `WAIT_n` | IN | Z80 WAIT input — used by ULA for memory contention and by peripherals to extend cycles |
| A13 | `RFSH_n` | OUT | Z80 refresh signal — pulses during `RFSH` cycle of every opcode fetch |
| A14 | `ROMCS_n` | OUT | ROM chip select (active low) — pulled low when ROM is addressed at `#0000–#3FFF` |
| A15 | `A7` | OUT | Z80 address bus, bit 7 |
| A16 | `A6` | OUT | Z80 address bus, bit 6 |
| A17 | `A5` | OUT | Z80 address bus, bit 5 |
| A18 | `A4` | OUT | Z80 address bus, bit 4 |
| A19 | `A3` | OUT | Z80 address bus, bit 3 |
| A20 | `A2` | OUT | Z80 address bus, bit 2 |
| A21 | `A1` | OUT | Z80 address bus, bit 1 |
| A22 | `A0` | OUT | Z80 address bus, bit 0 (LSB) |
| A23 | `CPU_CLK` | OUT | Z80 clock (3.5 MHz on 48K, 3.5469 MHz on 128K/+2) — derived from ULA crystal |
| A24 | `BUSRQ_n` | IN | Bus request — asserted by a peripheral to take over the bus (DMA-style) |
| A25 | `INT_n` | OUT | Interrupt request — driven low by the ULA every 20 ms (INT mode) |
| A26 | `BUSACK_n` | OUT | Bus acknowledge — Z80 acknowledges `BUSRQ_n` |
| A27 | `IORQULA_n` | OUT | Decoded IORQ to ULA — active when `A0=0` (port `#FE`) |
| A28 | `SPK_DATA` | OUT | Speaker data (raw 1-bit audio output from port `#FE` bit 4) |

> [!NOTE]
> A-side pins 1–8 are address bus **high byte** (A15→A8), A-side pins 15–22 are address bus **low byte** (A7→A0). This split layout was a Sinclair routing convenience — not the chip's natural pin order.

### Solder Side (Pins B1–B28)

| Pin | Signal | Dir | Description |
|---|---|---|---|
| B1 | `D7` | I/O | Z80 data bus, bit 7 (MSB) |
| B2 | `D6` | I/O | Z80 data bus, bit 6 |
| B3 | `D5` | I/O | Z80 data bus, bit 5 |
| B4 | `D4` | I/O | Z80 data bus, bit 4 |
| B5 | `D3` | I/O | Z80 data bus, bit 3 |
| B6 | `D2` | I/O | Z80 data bus, bit 2 |
| B7 | `D1` | I/O | Z80 data bus, bit 1 |
| B8 | `D0` | I/O | Z80 data bus, bit 0 (LSB) |
| B9 | `GND` | — | Ground (0 V) |
| B10 | `+9V` | PWR | +9 V unregulated supply from the input jack — useful for deriving other rails on peripherals |
| B11 | `+12V` | PWR | +12 V supply (48K issue 2 only; removed on later issues) |
| B12 | `NMI_n` | IN | Non-maskable interrupt — peripherals pull low to force Z80 to call `#0066` |
| B13 | `HALT_n` | OUT | Z80 halt state — low when CPU is in HALT (waiting for interrupt) |
| B14 | `M1_n` | OUT | Z80 machine cycle 1 (opcode fetch) — low during first T-state of any opcode fetch |
| B15 | `IORQ_n` | OUT | Z80 I/O request — active during `IN`/`OUT` instructions |
| B16 | `WR_n` | OUT | Z80 write strobe — active during memory/I/O write |
| B17 | `RD_n` | OUT | Z80 read strobe — active during memory/I/O read |
| B18 | `RFSH_n` | OUT | Refresh cycle indicator (mirror of A13; some peripherals use this side) |
| B19 | `MREQ_n` | OUT | Z80 memory request — active during memory read/write |
| B20 | `A0_ULA_n` | OUT | Decoded `A0=0` — used by Kempston and other partial-decoded peripherals |
| B21 | `CSROM_n` | OUT | ROM chip select (mirror of A14) |
| B22 | `CPU_CLK` | OUT | Z80 clock (mirror of A23 — two pins provide clock for redundancy) |
| B23 | `AY_CLK` | OUT | AY-3-8912 clock (1.7734 MHz derived from CPU clock / 2) — **128K/+2 only** |
| B24 | `+12V` | PWR | +12 V (mirror of B11; 48K issue 2 only) |
| B25 | `–12V` | PWR | –12 V (48K issue 2 only) |
| B26 | `BUSRQ_n` | IN | Bus request (mirror of A24) |
| B27 | `BUSACK_n` | OUT | Bus acknowledge (mirror of A26) |
| B28 | `SPK_OUT` | OUT | Internal speaker output (post-amplifier) — for diagnostic purposes |

> [!WARNING]
> The +12V and –12V rails were **removed on later 48K issues** (3+) and on all 128K/+2/+3 models. Never assume these pins are live — check the model before wiring. The –5V rail on A11 is similarly unavailable on most models.

---

## Z80 CPU — 40-Pin DIP

The Zilog Z80 (and second-source parts from Mostek, SGS, and Russian KR1858VM1) is a 40-pin DIP. Pin 1 is at the top-left, looking down on the chip with the notch/dot upward.

### Pin Layout

```
              ┌─────────────────┐
     A11  1   │                 │  40  A10
     A9   2   │                 │  39  A12
     A8   3   │                 │  38  A13
     A7   4   │      Z80        │  37  A14
     A6   5   │      CPU        │  36  A15
     A5   6   │                 │  35  CLK
     A4   7   │                 │  34  INT_n
     A3   8   │                 │  33  M1_n
     A2   9   │                 │  32  RESET_n
     A1  10   │                 │  31  IORQ_n
     A0  11   │                 │  30  MREQ_n
     GND 12   │                 │  29  WR_n
     D4  13   │                 │  28  HALT_n
     D3  14   │                 │  27  RFSH_n
     D5  15   │                 │  26  BUSRQ_n
     D6  16   │                 │  25  BUSACK_n
     D2  17   │                 │  24  WAIT_n
     D7  18   │                 │  23  NMI_n
     D0  19   │                 │  22  VCC
     D1  20   │                 │  21  RD_n
              └─────────────────┘
```

### Pin Functions

| Pin | Name | Dir | Function |
|---|---|---|---|
| 1–5, 30–40 | `A0–A15` | OUT (3-state) | 16-bit address bus |
| 6–17 (13–18, 20) | `D0–D7` | I/O (3-state) | 8-bit data bus |
| 19 | `D0` | I/O | Data bus bit 0 (matches the layout above; pin 19 is D0, not D1) |
| 12 | `GND` | — | Ground |
| 22 | `VCC` | PWR | +5 V supply (±5% tolerance) |
| 21 | `RD_n` | OUT (3-state) | Read strobe — active low during memory/I/O read |
| 28 | `WR_n` | OUT (3-state) | Write strobe — active low during memory/I/O write |
| 30 | `MREQ_n` | OUT (3-state) | Memory request — active low during memory access |
| 31 | `IORQ_n` | OUT (3-state) | I/O request — active low during `IN`/`OUT` and INT acknowledge |
| 33 | `M1_n` | OUT | Machine cycle 1 — active low during opcode fetch (also during INT acknowledge with `IORQ_n`) |
| 27 | `RFSH_n` | OUT | Refresh cycle — active low during the refresh portion of an opcode fetch |
| 32 | `RESET_n` | IN | Reset — pulled low for at least 3 clock cycles to reset the CPU |
| 34 | `INT_n` | IN | Maskable interrupt — peripherals pull low to request interrupt |
| 23 | `NMI_n` | IN | Non-maskable interrupt — always honored (cannot be disabled) |
| 24 | `WAIT_n` | IN | Wait — peripherals pull low to extend the current bus cycle |
| 25 | `BUSACK_n` | OUT | Bus acknowledge — Z80 has released the bus in response to `BUSRQ_n` |
| 26 | `BUSRQ_n` | IN | Bus request — peripherals pull low to take over the bus |
| 28 | `HALT_n` | OUT | Halt — Z80 has executed `HALT` and is waiting for an interrupt |
| 35 | `CLK` | IN | Single-phase clock input — driven by the ULA on the Spectrum (3.5 MHz 48K, 3.5469 MHz 128K/+2) |

> [!NOTE]
> Z80 chips are marked with a maximum clock rating (e.g., Z84C0006PEC = 6 MHz). The Spectrum drives them at 3.5 MHz, well below the maximum. Overclocking to 7 MHz is the basis of the Russian “Turbo” clones — usually works on a 6 MHz-rated part, marginal on a 4 MHz part.

---

## AY-3-8912 Sound Chip — 28-Pin DIP

The General Instrument AY-3-8912 (and the Yamaha YM2149 pin-compatible clone, plus the Russian KR1518VG94) is a 28-pin DIP used in the 128K/+2/+3 and many Russian clones. Pin 1 is at the top-left.

### Pin Layout

```
              ┌─────────────────┐
    VSS   1   │                 │  28  VCC
    ANALOG_2   │                 │  27  IO_B7
    ANALOG_3   │   AY-3-8912     │  26  IO_B6
    OUT_B     │   YM2149        │  25  IO_B5
    OUT_C     │                 │  24  IO_B4
    VSS   6   │                 │  23  IO_B3
    ANALOG_1   │                 │  22  IO_B2
    OUT_A     │                 │  21  IO_B1
    ENABLE 9  │                 │  20  IO_B0
    CLK_   10 │                 │  19  BDIR
    RESET_11  │                 │  18  BC2
    IO_A7 12  │                 │  17  BC1
    IO_A6 13  │                 │  16  DA7
    IO_A5 14  │                 │  15  DA6
              └─────────────────┘
```

### Pin Functions

| Pin | Name | Dir | Function |
|---|---|---|---|
| 1 | `VSS` | — | Ground (0 V) |
| 2 | `ANALOG_CH2` | I | Analog multiplex input 2 (unused on Spectrum — leave floating) |
| 3 | `ANALOG_CH3` | I | Analog multiplex input 3 (unused on Spectrum) |
| 4 | `OUT_B` | O | Channel B audio output |
| 5 | `OUT_C` | O | Channel C audio output |
| 6 | `VSS` | — | Ground (separate from pin 1 to reduce noise) |
| 7 | `ANALOG_CH1` | I | Analog multiplex input 1 (unused on Spectrum) |
| 8 | `OUT_A` | O | Channel A audio output |
| 9 | `ENABLE_n` | I | Enable input — pulled low on Spectrum |
| 10 | `CLOCK` | I | Clock input — 1.7734 MHz derived from CPU clock on 128K/+2, 1.75 MHz on Pentagon |
| 11 | `RESET_n` | I | Reset — pulled high via pull-up; pull low for at least 5 clock cycles to reset |
| 12–18 | `IO_A0–IO_A7` | I/O | I/O port A (8 bits) — used for the serial Keypad / RS232 on +2 |
| 19 | `BDIR` | I | Bus direction — combined with `BC1` and `BC2` to select inactive/read-address/write-data mode |
| 20 | `BC2` | I | Bus control 2 — usually tied high on Spectrum |
| 21 | `BC1` | I | Bus control 1 — combined with `BDIR` to form the 2-bit control mode |
| 22–27 | `IO_B0–IO_B5` | I/O | I/O port B (only 6 pins available on the 28-pin package; 2 are missing vs the 40-pin AY-3-8910) |
| 20–27 (DA lines) | `DA0–DA7` | I/O | Multiplexed address/data bus — register number latch on one cycle, data on next |
| 28 | `VCC` | PWR | +5 V supply |

### Control Mode Encoding

The three control pins `BDIR`, `BC1`, `BC2` select one of four bus modes:

| `BDIR` | `BC1` | `BC2` (always 1) | Mode |
|---|---|---|---|
| 0 | 0 | 1 | **INACTIVE** — chip is idle, bus high-impedance |
| 0 | 1 | 1 | **READ** — read selected register onto DA bus |
| 1 | 0 | 1 | **WRITE** — write DA bus into selected register |
| 1 | 1 | 1 | **LATCH ADDRESS** — latch DA bus into register-number latch |

The Spectrum 128K/+2/+3 decoding logic at port `#FFFD`/`#BFFD` maps Z80 `WR_n` and `RD_n` to these pins automatically — programmers see only a 2-port interface. For programming details, see [ay_3_8912.md](../06_sound/hardware/ay_3_8912.md).

---

## Joystick Ports

Three incompatible joystick standards are in common use on the Spectrum: **Kempston** (external interface, port `#1F`), **Sinclair 1** (Interface 2, port decoded via keyboard matrix), and **Sinclair 2** (mirror of Sinclair 1 with different keys). The Atari-style 9-pin D-Sub is the physical connector on all three.

### Atari 9-Pin D-Sub — Standard Pinout

The 9-pin D-Sub is the **de-facto** joystick connector for retro machines. Used by Atari 2600, Commodore 64, Amiga, MSX, and the Spectrum's Kempston interface.

| Pin | Signal (standard) | Kempston use | Sinclair Interface 2 use |
|---|---|---|---|
| 1 | Up | Up | Up |
| 2 | Down | Down | Down |
| 3 | Left | Left | Left |
| 4 | Right | Right | Right |
| 5 | Pot Y (analog) | n/c | n/c |
| 6 | Fire button | Fire | Fire |
| 7 | +5 V | +5 V (limited) | +5 V (limited) |
| 8 | GND | GND | GND |
| 9 | Pot X (analog) | n/c | n/c |

### Kempston Joystick Interface

The Kempston joystick is read at **port `#1F`** (decoded by `A5=0`, so mirrors appear at `#001F`, `#011F`, …). The interface connects to the Spectrum expansion bus and decodes the joystick lines onto the Z80 data bus.

| Bit | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|---|
| Use | n/c | n/c | n/c | Fire | Up | Down | Left | Right |

Reading the joystick:

```z80
LD   A,(IY+$1F)   ; or IN A,(#1F) — Kempston port
; A = %0001XXXX where X = direction/fire bits
AND  #1F          ; Mask off unused bits
CP   #01          ; Is fire pressed (bit 0)?
```

A button is **pressed** when its bit is **1** (active high). This is opposite to the Sinclair joysticks below.

### Sinclair Interface 2 Joysticks (Joystick Ports 1 and 2)

The Interface 2 maps the joystick to **keys 6–0** for port 1 (left socket) and **keys 1–5** for port 2 (right socket). The joystick lines are wired into the keyboard matrix.

#### Sinclair Port 1 (left) — Keys 6–0

| Joystick action | Equivalent key |
|---|---|
| Up | `6` |
| Down | `7` |
| Left | `5` |
| Right | `8` |
| Fire | `0` |

#### Sinclair Port 2 (right) — Keys 1–5

| Joystick action | Equivalent key |
|---|---|
| Up | `9` |
| Down | `0` |
| Left | `6` |
| Right | `7` |
| Fire | `4` |

Programs detect these by reading the keyboard matrix at port `#FE` with the appropriate high address byte set. The bits are **active low** (pressed = 0).

### Fuller Joystick Box — Port `#7F`

The Fuller joystick box decodes at port `#7F` and uses a different bit layout:

| Bit | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|
| Use | Fire | Right | Left | Down | Up | n/c | n/c |

Like Kempston, **active high**.

For the full history and clone-specific joystick conventions, see [joystick.md](../03_io/peripherals/joystick.md) and [clone_joysticks.md](../02_hardware/clones/clone_joysticks.md).

---

## Kempston Mouse Interface

The Kempston mouse (a 1980s trackball-style mouse for the Spectrum) uses **three ports** to report X position, Y position, and button state:

| Port | Read | Bits |
|---|---|---|
| `#FBDF` | X position counter | D0–D7 (8-bit signed) |
| `#FFDF` | Y position counter | D0–D7 (8-bit signed) |
| `#FADF` / `#BFDF` | Buttons | bit 0 = right, bit 1 = left, bit 2 = middle (active low) |

The counters wrap around at `#00`/`#FF` — there is no absolute position, only deltas. Reading too slowly loses movement information. See [mouse.md](../03_io/peripherals/mouse.md) for programming patterns.

---

## Tape Connector (EAR / MIC)

The Spectrum has two 3.5 mm jack sockets for cassette tape operation: **EAR** (input from tape) and **MIC** (output to tape). Both use mono 3-conductor jacks (tip, ring, sleeve), though most cables are 2-conductor (tip and sleeve only).

### EAR Socket — Tape Input

| Connection | Signal |
|---|---|
| Tip | Audio signal from tape (AC coupled) |
| Sleeve | Ground |
| Ring | (often unused; ground on some cables) |

The EAR signal is fed through a Schmidt trigger into ULA port `#FE` bit 6 (read). Threshold is approximately 0.7 V.

### MIC Socket — Tape Output

| Connection | Signal |
|---|---|
| Tip | Audio signal to tape (TTL level, ~0–5 V) |
| Sleeve | Ground |
| Ring | (unused) |

The MIC signal is driven directly by ULA port `#FE` bit 3 (write). When the bit is set, the MIC line is high; when clear, low.

> [!NOTE]
> Some modern tape adapters use stereo 3-conductor jacks and bridge tip-ring to provide a more reliable signal — Spectrum hardware is tolerant of this.

---

## Power Connector — 48K / 128K / +2

The original Sinclair power supply uses a **3.5 mm barrel jack** (outer negative, inner positive), supplying **9 V DC** at approximately 1.4 A (48K) or 1.8 A (128K). The on-board regulator drops this to 5 V for the logic.

| Model | Input voltage | Input current | Center polarity |
|---|---|---|---|
| 48K issue 2 | 9 V DC | 1.2 A | Positive center |
| 48K issue 3–6 | 9 V DC | 1.4 A | Positive center |
| 128K / +2 | 9 V DC | 1.8 A | Positive center |
| +2A / +3 | 9 V AC (not DC) | 1.96 A | (no polarity — AC) |

> [!WARNING]
> The +2A and +3 require **9 V AC**, not 9 V DC. Plugging a DC adapter into a +2A or +3 may damage the regulator. The AC requirement arises because the +2A/+3 power supply uses a voltage doubler internally to derive the +12 V rail for the floppy drive.

---

## Cross-References

- [io_port_map.md](io_port_map.md) — I/O port decoding tables
- [timing_reference.md](timing_reference.md) — cycle-exact timing tables
- [memory_maps.md](memory_maps.md) — memory layout reference
- [z80_architecture.md](../01_cpu/z80_architecture.md) — Z80 CPU deep dive
- [ula_architecture.md](../02_hardware/original/ula_architecture.md) — Ferranti ULA internals
- [ay_3_8912.md](../06_sound/hardware/ay_3_8912.md) — AY sound chip programming
- [joystick.md](../03_io/peripherals/joystick.md) — joystick programming patterns
- [mouse.md](../03_io/peripherals/mouse.md) — Kempston mouse programming
- [keyboard_matrix.md](../02_hardware/original/keyboard_matrix.md) — keyboard matrix and connector

---

## References

- [Sinclair Research — *ZX Spectrum 48K Service Manual](https://www.worldofspectrum.org/hardware.html)*, 1982 — edge connector and chip pinouts
- [Sinclair Research — *ZX Spectrum 128 Service Manual](https://www.worldofspectrum.org/hardware.html)*, 1986 — 128K pinouts
- Amstrad — *ZX Spectrum +2 / +2A / +3 Service Manuals*, 1987–88 — Amstrad-era pinouts
- Zilog — *[Z84C00](https://www.zilog.com/docs/z80/um0080.pdf) Z80 CPU Product Specification* — Z80 40-pin DIP pinout and timing
- General Instrument — *[AY-3-8910/8912 Programmers Manual* — AY chip pinout and register](http://www.worldofspectrum.org/) map
- [Chris Smith — *The ZX Spectrum ULA](http://www.zxdesign.info/)*, 2010 — definitive ULA and edge connector reference
- Geoff Wearmouth — *ZX Spectrum Hardware Manual*, [wearmouth.demon.co.uk](https://www.wearmouth.demon.co.uk/zxspectr.htm) — community-maintained pinout tables
- World of Spectrum — [Hardware FAQ](https://worldofspectrum.org/faq/hardware/hardware.htm)
