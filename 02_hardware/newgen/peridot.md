[← Home](../../README.md) · [New Gen Hardware](README.md) · [Karabas Pro](karabas_pro.md)

# Peridot — The Expandable Karabas-Compatible Platform

The **Peridot** is a modern (2020+) Russian ZX Spectrum-compatible platform designed as an **expandable successor to the Karabas Pro**. Built around the same **real Z80 + Altera MAX II CPLD** architecture, the Peridot adds a **larger PCB** with multiple expansion headers, a more capable CPLD (EPM1270 or EPM570 with more logic available), and a refined peripheral set aimed at users who want a **"Karabas Pro with room to grow"** — a base machine that supports adding WiFi, RTC, additional RAM, or experimental hardware via standardized headers.

For software developers, the Peridot is best understood as a **superset of the Karabas Pro** — it runs the same Pentagon-128-compatible software library, with the same memory map and ports, plus a set of well-defined expansion ports for additional features. Software written for the Karabas Pro runs unchanged; software that wants to use Peridot-specific extensions can probe for them and use them when available.

This article covers the Peridot as a hardware platform. For the Karabas Pro (the simpler sibling), see [karabas_pro.md](karabas_pro.md). For the Karabas 128 (the entry-level model), see [karabas_128.md](karabas_128.md).

---

## Why Peridot?

The Karabas Pro filled the "cheap, modern Pentagon" gap, but it left a second gap: **users who wanted expandability**. The Karabas Pro's small PCB and minimal CPLD meant that adding WiFi, extra RAM, or experimental hardware required external adapters that cluttered the workspace.

The Peridot is designed to fill this gap with:

| Goal | Peridot's approach |
|---|---|
| **Karabas Pro compatibility** | Same memory map, same ports, same Pentagon 128 baseline |
| **Expandability** | Larger PCB with standardized expansion headers (GPIO, SPI, I²C) |
| **More CPLD capacity** | EPM1270 (vs. Karabas Pro's EPM570) — room for future firmware features |
| **Modern conveniences built in** | WiFi (ESP-12), RTC, expanded GPIO — all on-board |
| **Open source** | Same as Karabas Pro — full schematics, PCB, CPLD firmware on GitHub |

---

## Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | **Real Z80** (Z84C0020 — CMOS, 20 MHz-rated part), running at 3.5 / 7 / 14 MHz |
| **CPLD** | **Altera MAX II EPM1270** (T144 package) — larger than Karabas Pro's EPM570, with spare logic for future expansion |
| **RAM** | **512 KB** SRAM (AS6C4008) — same as Karabas Pro |
| **ROM / Flash** | **512 KB** SPI flash — holds multiple ROM images |
| **Video output** | **VGA** (RGB) — scan-doubled, same as Karabas Pro |
| **Storage** | **SD card via SPI** (built-in) |
| **Keyboard** | **PS/2** PC keyboard |
| **WiFi** | **ESP-12 module** (Espressif ESP8266) — built-in, connected via SPI |
| **RTC** | **Battery-backed DS1307 or similar** — built-in |
| **GPIO** | **2×20-pin header** — exposes SPI, I²C, and general-purpose I/O from the CPLD |
| **Audio** | **AY-3-8912** + beeper + Covox DAC |
| **Joystick** | **Kempston** at `#1F` (built-in) |
| **Expansion** | **Pentagon edge connector** + GPIO header |
| **Power** | **5V DC** via mini-USB or barrel jack |
| **Form factor** | Single-board, ~12 cm × 10 cm (larger than Karabas Pro) |

The defining hardware choice is the **larger CPLD** (EPM1270 vs. EPM570). The EPM1270 has approximately **2× the logic elements** of the EPM570 — sufficient to implement all the Karabas Pro features plus the WiFi/RTC controllers plus additional spare logic that firmware updates can use for future extensions.

---

## Pentagon 128 Compatibility

Like the Karabas Pro, the Peridot targets **Pentagon 128 binary compatibility** — software that runs on a real Pentagon 128 runs unchanged:

| Feature | Pentagon 128 | Peridot | Compatible? |
|---|---|---|---|
| **Memory banking** | `#7FFD` + `#EFF7` | Identical | Yes |
| **Video timing** | 71,680 T-states, 320 lines, 48.83 Hz | Identical (Pentagon mode) | Yes |
| **Contention** | None | None (in Pentagon mode) | Yes |
| **I/O ports** | Standard Pentagon | Identical + extensions | Yes |
| **AY sound** | At Pentagon clock | Identical | Yes |
| **Beta 128 disk** | Required | Emulated via SD card | Yes |

The Peridot also supports a **48K mode** and **128K mode** (with proper contention) selectable at boot — useful for cross-platform software testing.

---

## Peridot Extensions Beyond Karabas Pro

### Built-in WiFi (ESP-12)

The ESP-12 WiFi module is **integrated on the PCB** (vs. an expansion header on the Karabas Pro). The WiFi stack is driven via SPI, accessible through a port pair (typically `#57` / `#77`). AT-command-based WiFi access (connect, TCP/UDP sockets, HTTP) is supported, making the Peridot one of the few WiFi-capable Russian Spectrums.

### Real-Time Clock

A battery-backed RTC (typically DS1307 or DS3231 via I²C) is built-in, accessible through the GPIO header or a dedicated port pair. Software can read the current date and time for filesystem timestamps, scheduled events, or logging.

### Expanded GPIO Header

The **2×20-pin GPIO header** exposes:
- **SPI bus** (MOSI, MISO, SCLK, CS) — for connecting additional SPI peripherals
- **I²C bus** (SDA, SCL) — for connecting I²C peripherals (sensors, displays)
- **8 general-purpose I/O pins** — directly driven by the CPLD, accessible via a port pair

This header enables **hardware experimenters** to add custom peripherals without modifying the main PCB — sensors, character LCD displays, additional DACs, relay drivers, etc.

### Future-Proof CPLD

The EPM1270's spare logic capacity means that **future firmware updates** can add features without hardware changes. The Karabas community has discussed adding:
- Hardware sprites (similar to TS-Conf)
- A tilemap engine
- Hardware line draw and blit
- DMA controller

These features are not in the current firmware but are architecturally possible on the Peridot's CPLD. The Karabas Pro's smaller EPM570 is closer to its logic-element limit and has less room for such additions.

---

## Programming the Peridot

For most software, programming the Peridot is **identical to programming a Karabas Pro or Pentagon 128** — use the standard `#7FFD` and `#EFF7` paging, the standard port addresses, and the standard Pentagon conventions. The extensions (WiFi, RTC, GPIO) are opt-in.

### Detecting a Peridot

```z80
detect_peridot:
        ; Read the Peridot version register
        ld  bc, #1FFD           ; (example port — exact address varies)
        in  a, (c)
        cp  #5B                 ; Peridot signature (vs. Karabas Pro's #5A)
        jr  z, .is_peridot
        ; Not a Peridot — treat as Karabas Pro or plain Pentagon
        ret
.is_peridot:
        ; Use Peridot extensions (WiFi, RTC, GPIO)
        ret
```

### Using the GPIO Header

```z80
; Write a byte to the GPIO output port
write_gpio:
        ld  bc, #XX             ; GPIO port (example)
        out (c), a              ; drive 8 GPIO pins
        ret

; Read a byte from the GPIO input port
read_gpio:
        ld  bc, #YY             ; GPIO port (example)
        in  a, (c)              ; read 8 GPIO pins
        ret
```

The exact GPIO port addresses are documented in the [Peridot programmer's reference](https://github.com/peridot).

---

## Peridot vs Karabas Pro vs ZX Evolution

| Criterion | Peridot | Karabas Pro | ZX Evolution |
|---|---|---|---|
| **Architecture** | Z80 + MAX II EPM1270 | Z80 + MAX II EPM570 | Z80 + MAX 7000 + ATmega |
| **Max RAM** | 512 KB | 512 KB | 4 MB |
| **WiFi** | **Built-in** (ESP-12) | None (expansion only) | None |
| **RTC** | **Built-in** | None | Built-in |
| **GPIO header** | **2×20-pin** | None | None |
| **Storage** | SD card | SD card | IDE + SD |
| **Enhanced video** | None (planned in firmware) | None | TS-Conf (firmware swap) |
| **Expansion** | Pentagon edge + GPIO | Pentagon edge only | Pentagon edge + ISA |
| **Open source** | Yes | Yes | Yes |
| **Cost** | ~$60–$80 (kit) | ~$40–$60 (kit) | ~$150+ (assembled) |
| **Best for** | Hardware experimenters | Budget Pentagon users | TS-Conf developers |

The Peridot is the right choice for users who want **room to grow** — the GPIO header, built-in WiFi, and RTC make it a flexible platform for projects that go beyond running existing Spectrum software.

---

## Cross-References

- [Karabas Pro](karabas_pro.md) — the simpler sibling that the Peridot extends
- [Karabas 128](karabas_128.md) — the entry-level Karabas model
- [ZX Evolution](zx_evo.md) — the more powerful Russian alternative
- [ZX-Uno](zx_uno.md) — open-source FPGA alternative with similar WiFi capability
- [ZX Spectrum Next](zx_next.md) — the Western equivalent (also has ESP-12 WiFi)
- [Sizif-512](../clones/sizif_harlequin.md) — similar Z80 + MAX II architecture
- [Pentagon 128](../clones/pentagon.md) — the Peridot's compatibility target

---

## References

- **Peridot project** ([GitHub: peridot](https://github.com/peridot)) — official repository with schematics and CPLD firmware
- **Peridot forum** (zx-pk.ru) — community hub (Russian-language)
- **Karabas community wiki** — Peridot-specific pages with expansion project examples
- **ESP-12 WiFi documentation** (Espressif) — the WiFi module's AT command reference
- **SpeccyWiki (speccy.info)** — Peridot article (when available)
