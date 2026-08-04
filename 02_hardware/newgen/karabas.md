[← Home](../../README.md) · [New Gen Hardware](README.md)

# Karabas Family — Modern Open-Source Z80 + CPLD Spectrum Clones

The **Karabas family** is a line of modern (2018+) open-source ZX Spectrum clones designed by **Aleksey "asy" Makarov** and the Karabas community. All three models share the same core architectural decision: a **real Z80 CPU paired with an Altera MAX II CPLD** that implements the ULA functions, address decoding, memory paging, and I/O port mapping. Where they differ is in **compatibility target, memory size, and expandability** — a deliberate three-tier product line covering entry-level, mainstream, and experimenter use cases.

The three models, from smallest to largest:

| Model | Target | CPLD | RAM | Defining feature |
|---|---|---|---|---|
| **Karabas 128** | Sinclair 128K (cycle-exact) | EPM240 | 128 KB | Cheapest modern 128K Spectrum; emulates contention |
| **Karabas Pro** | Pentagon 128 | EPM570 | 512 KB | Cheap modern Pentagon with turbo, SD, VGA |
| **Peridot** | Pentagon 128 (expandable) | EPM1270 | 512 KB | Karabas Pro + built-in WiFi, RTC, GPIO header |

For software developers, the family is best understood as **modernized Sinclairs and Pentagons** — they run the existing Russian and Western Spectrum software libraries unmodified, with the same memory maps, the same I/O ports, and (almost) the same timing. Where they differ from a 1990s Pentagon or +2 is in **hardware quality and modern conveniences**: integrated PS/2 keyboard, SD card storage, VGA output, turbo mode, and reliable modern components.

This article covers all three Karabas models. For the broader modern-Spectrum landscape, see [zx_evo.md](zx_evo.md) (Russian), [zx_next.md](zx_next.md) (Western), and [zx_uno.md](zx_uno.md) (open-source FPGA).

---

## Why the Karabas Family Exists

The Russian Spectrum scene of the late 2010s had a gap:

- **ZX Evolution** (2007) — powerful but expensive, complex PCB, harder to build
- **Pentagon** (1989) — old, unreliable hardware, no modern features
- **TS-Conf** — requires ZX Evolution, complex firmware stack
- **ZX Spectrum Next** (2017) — Western-designed, expensive to import, FPGA-only (no real Z80)

What was missing was a **simple, cheap, modern Spectrum** — a single-board machine that anyone could build from a kit, with all the essential modern features and nothing unnecessary. The Karabas family fills this gap across three tiers:

- **Karabas 128** — for users who want a Sinclair 128K with modern components (beginners, Western software enthusiasts)
- **Karabas Pro** — for users who want a Pentagon 128 with turbo and SD storage (Russian software enthusiasts, demoscene)
- **Peridot** — for hardware experimenters who want WiFi, RTC, and GPIO expansion

| Goal | Karabas family's approach |
|---|---|
| **Binary compatibility** | Exact Sinclair 128K (Karabas 128) or Pentagon 128 (Pro, Peridot) memory map, ports, timing |
| **Modern components** | All-new ICs (no 30-year-old Soviet parts), single +5V power supply |
| **Compact size** | Single-board, ~8–12 cm × 6–10 cm PCB |
| **Affordable** | ~$30 (Karabas 128 kit) to ~$80 (Peridot assembled) |
| **Open source** | Schematics, PCB, CPLD firmware all on GitHub |
| **Modern conveniences** | PS/2 keyboard, SD card, VGA output, turbo mode (Pro/Peridot) |

---

## Family Architecture — Z80 + MAX II CPLD

The defining hardware choice shared by all three Karabas models is the **Altera MAX II CPLD**. This is the same family of low-cost, modern CPLDs used in the [Sizif-512](../clones/sizif_harlequin.md). The MAX II family has enough logic elements to implement the ULA's video generation, memory arbitration, and I/O port decoding in a single chip — replacing dozens of discrete TTL parts from a 1990s clone design.

The three models use different sizes of the same CPLD family:

| Model | CPLD | Logic Elements | Why this size |
|---|---|---|---|
| **Karabas 128** | EPM240 | 240 | Sufficient for 128K memory map + I/O decoding |
| **Karabas Pro** | EPM570 | 570 | Adds turbo, extended paging, SD controller, scan doubler |
| **Peridot** | EPM1270 | 1,270 | Adds WiFi (SPI), RTC (I²C), GPIO — with spare capacity for future features |

The Peridot's EPM1270 has approximately **2× the logic elements** of the Karabas Pro's EPM570 — sufficient to implement all the Karabas Pro features plus the WiFi/RTC controllers plus additional spare logic that firmware updates can use for future extensions. The Karabas community has discussed adding hardware sprites, a tilemap engine, hardware line draw, or a DMA controller to the Peridot's CPLD in future firmware revisions.

### Shared Component Baseline

All three Karabas models share these components:

| Component | Specification |
|---|---|
| **CPU** | **Real Z80** (Z84C0020 — CMOS, 20 MHz-rated), at 3.5 MHz (Karabas 128) or 3.5/7/14 MHz (Pro, Peridot) |
| **Video output** | **VGA** (RGB) — directly driven by the CPLD, scan-doubled for modern monitors |
| **Keyboard** | **PS/2** PC keyboard (CPLD firmware translates PS/2 scan codes to Spectrum matrix positions) |
| **Audio** | **AY-3-8912** at the appropriate clock + beeper |
| **Joystick** | **Kempston** at `#1F` (built-in) |
| **Power** | **5V DC** via mini-USB |
| **Form factor** | Single-board computer |

The scan doubler doubles the horizontal sync rate to ~31 kHz (vs. the original 15 kHz), making the Karabas family compatible with any VGA monitor — no need for a 15 kHz-capable CRT or a modern OSSC/RetroTINK scaler.

---

## Karabas 128 — The Entry-Level Model

The **Karabas 128** is the smallest model, designed for users who want a **simple, cheap, modern 128K Spectrum**. It targets **Sinclair 128K binary compatibility** with exact timing, exact contention, and exact memory map. Software that runs on a real 128K or +2 runs on the Karabas 128 unmodified.

### Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | Real Z80 (Z84C0020), running at **3.5 MHz** (no turbo) |
| **CPLD** | **Altera MAX II EPM240** or **EPM570** — sufficient for 128K glue logic |
| **RAM** | **128 KB** SRAM (AS6C1008) — standard 128K, no extended paging |
| **ROM / Flash** | **128 KB or 256 KB** SPI flash — holds 128K BASIC + 48K BASIC + service ROM |
| **Storage** | **None built-in** (tape only by default); SD card available via optional expansion |
| **Expansion** | **Standard Spectrum edge connector** — accepts original peripherals and the SD card expansion |
| **PCB size** | Single-board, ~8 cm × 6 cm |

The EPM240 has fewer logic elements than the Karabas Pro's EPM570, but is sufficient for the 128K memory map and basic I/O port decoding. The additional features of the Karabas Pro (turbo, extended paging, SD card controller) require the larger EPM570.

### 128K Compatibility

| Feature | Sinclair 128K | Karabas 128 | Compatible? |
|---|---|---|---|
| **Memory banking** | `#7FFD` | Identical | Yes |
| **Video timing** | 70,908 T-states, 311 lines, 50.02 Hz | Identical | Yes |
| **Contention** | Banks 1/3/5/7 contended | **Implemented** (CPLD emulates contention) | Yes |
| **I/O ports** | Standard 128K | Identical | Yes |
| **ROM** | 128K BASIC + 48K BASIC | Identical (both included) | Yes |
| **AY sound** | At 128K clock | Identical | Yes |
| **Keypad** | 128K keypad (rare) | Not implemented | (rarely used) |

> [!NOTE]
> The Karabas 128 **emulates 128K contention** — banks 1, 3, 5, and 7 suffer the standard `(6, 5, 4, 3, 2, 1, 0, 0)` delay pattern when accessed during screen display. This is important for compatibility: software written for the 128K (especially demos with cycle-exact timing) depends on this contention, and would break without it.

### When to Choose Karabas 128

- You primarily run **Western 128K software** (Sinclair demos, +2/+3 games)
- You want the **cheapest** modern Spectrum (~$30 kit)
- You are a **beginner** building your first Spectrum clone (simpler kit, fewer features that can fail)
- You need exact **128K contention** for cycle-exact 128K software

---

## Karabas Pro — The Pentagon-Compatible Standard

The **Karabas Pro** is the main model of the family, designed for users who want a **modernized Pentagon 128**. It runs the entire Russian Spectrum software library unmodified, with the same memory map, the same I/O ports, and (almost) the same timing. Where it differs from a 1990s Pentagon is in **hardware quality and modern conveniences**: integrated PS/2 keyboard, SD card storage, VGA output, turbo mode, and reliable modern components.

### Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | Real Z80 (Z84C0020), running at **3.5 / 7 / 14 MHz** |
| **CPLD** | **Altera MAX II EPM570** — handles ULA functions, address decoding, memory paging, I/O port mapping |
| **RAM** | **512 KB** SRAM (AS6C4008) — 8× the Pentagon's 64 KB |
| **ROM / Flash** | **512 KB** SPI flash (SST39SF040) — holds multiple ROM images, selectable at boot |
| **Storage** | **SD card via SPI** (Holteck HC-MSD001 controller or similar) — DivMMC-compatible |
| **Expansion** | **Pentagon edge connector** — accepts original Pentagon peripherals |
| **Audio** | **AY-3-8912** (single chip, Pentagon-compatible clock) + beeper + **Covox DAC** (8-bit PCM) |
| **PCB size** | Single-board, ~10 cm × 8 cm |

### Pentagon 128 Compatibility

| Feature | Pentagon 128 | Karabas Pro | Compatible? |
|---|---|---|---|
| **Memory banking** | `#7FFD` (standard 128K) | Identical | Yes |
| **Extended paging** | `#EFF7` (for 1024K) | **Supported** (Karabas Pro has 512 KB) | Yes |
| **Video timing** | 71,680 T-states, 320 lines, 48.83 Hz | Identical (Pentagon mode) | Yes |
| **Contention** | None | None (in Pentagon mode) | Yes |
| **I/O ports** | Standard Pentagon | Identical + extensions | Yes |
| **Beta 128 disk** | Required | **Emulated** via SD card | Yes (via SD image) |
| **AY sound** | At Pentagon clock | Identical | Yes |
| **INT timing** | Line 304, T=0 | Identical | Yes |

The Karabas Pro also supports an optional **48K mode** (different timing — 69,888 T-states, 312 lines, 50.08 Hz, with contention) selectable at boot, for running Western software that depends on 48K timing.

### Extensions Beyond Pentagon

#### Turbo Mode (3.5 / 7 / 14 MHz)

CPU speed is selectable via a port write (typically `#DFFD` bit 6 or a Karabas-specific port). As with the ZX Evolution, **always restore 3.5 MHz before accessing slow peripherals** (SD card, PS/2 keyboard).

#### Extended Memory — 512 KB

The Karabas Pro's 512 KB is accessible via the Pentagon's `#EFF7` extended paging port — `(#EFF7 & #07) × 8 + (#7FFD & #07)` gives 32 banks (512 KB). This is the same formula as the Pentagon 1024, just with fewer banks physically populated.

#### SD Card Storage (DivMMC-compatible)

The SD card is accessible via an SPI controller, presenting a **DivMMC-compatible interface**. Software written for the DivMMC (modern Russian DOS-aware software) runs unchanged — no special Karabas-specific drivers are needed.

#### PS/2 Keyboard

A PS/2 PC keyboard connects via a standard mini-DIN connector. The CPLD firmware handles the PS/2 protocol and translates scan codes to Spectrum matrix positions. Software that reads the keyboard via the standard `#FE` port works correctly.

#### VGA Output with Scan Doubler

Video output is **VGA** (RGB) — directly driven by the CPLD with a built-in scan doubler for compatibility with modern monitors. The scan doubler doubles the horizontal sync rate to ~31 kHz (vs. the original 15 kHz).

#### Covox DAC

An 8-bit Covox-style DAC (typically mapped to port `#FB` or `#1F`) provides 8-bit PCM sample playback — useful for digitized sound effects and music.

### When to Choose Karabas Pro

- You primarily run **Russian software** (Pentagon demos, TR-DOS games)
- You want **turbo mode** (7 or 14 MHz) for faster code
- You want **SD card storage** without an external DivMMC
- You want a **Pentagon-compatible** machine but with modern, reliable components

---

## Peridot — The Expandable Karabas

The **Peridot** is the largest model, designed as an **expandable successor to the Karabas Pro**. Built around the same real Z80 + Altera MAX II CPLD architecture, the Peridot adds a **larger PCB** with multiple expansion headers, a more capable CPLD (EPM1270), and a refined peripheral set aimed at users who want a "Karabas Pro with room to grow" — a base machine that supports adding WiFi, RTC, additional RAM, or experimental hardware via standardized headers.

For software developers, the Peridot is best understood as a **superset of the Karabas Pro** — it runs the same Pentagon-128-compatible software library, with the same memory map and ports, plus a set of well-defined expansion ports for additional features. Software written for the Karabas Pro runs unchanged; software that wants to use Peridot-specific extensions can probe for them and use them when available.

### Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | Real Z80 (Z84C0020), running at **3.5 / 7 / 14 MHz** |
| **CPLD** | **Altera MAX II EPM1270** (T144 package) — larger than Karabas Pro's EPM570, with spare logic for future expansion |
| **RAM** | **512 KB** SRAM (AS6C4008) — same as Karabas Pro |
| **ROM / Flash** | **512 KB** SPI flash — holds multiple ROM images |
| **Storage** | **SD card via SPI** (built-in) |
| **WiFi** | **ESP-12 module** (Espressif ESP8266) — built-in, connected via SPI |
| **RTC** | **Battery-backed DS1307 or similar** — built-in |
| **GPIO** | **2×20-pin header** — exposes SPI, I²C, and general-purpose I/O from the CPLD |
| **Expansion** | **Pentagon edge connector** + GPIO header |
| **PCB size** | Single-board, ~12 cm × 10 cm (larger than Karabas Pro) |

The defining hardware choice is the **larger CPLD** (EPM1270 vs. EPM570). The EPM1270 has approximately **2× the logic elements** of the EPM570 — sufficient to implement all the Karabas Pro features plus the WiFi/RTC controllers plus additional spare logic that firmware updates can use for future extensions.

### Pentagon 128 Compatibility

Like the Karabas Pro, the Peridot targets **Pentagon 128 binary compatibility**:

| Feature | Pentagon 128 | Peridot | Compatible? |
|---|---|---|---|
| **Memory banking** | `#7FFD` + `#EFF7` | Identical | Yes |
| **Video timing** | 71,680 T-states, 320 lines, 48.83 Hz | Identical (Pentagon mode) | Yes |
| **Contention** | None | None (in Pentagon mode) | Yes |
| **I/O ports** | Standard Pentagon | Identical + extensions | Yes |
| **AY sound** | At Pentagon clock | Identical | Yes |
| **Beta 128 disk** | Required | Emulated via SD card | Yes |

The Peridot also supports a **48K mode** and **128K mode** (with proper contention) selectable at boot — useful for cross-platform software testing.

### Extensions Beyond Karabas Pro

#### Built-in WiFi (ESP-12)

The ESP-12 WiFi module is **integrated on the PCB** (vs. an expansion header on the Karabas Pro). The WiFi stack is driven via SPI, accessible through a port pair (typically `#57` / `#77`). AT-command-based WiFi access (connect, TCP/UDP sockets, HTTP) is supported, making the Peridot one of the few WiFi-capable Russian Spectrums.

#### Real-Time Clock

A battery-backed RTC (typically DS1307 or DS3231 via I²C) is built-in, accessible through the GPIO header or a dedicated port pair. Software can read the current date and time for filesystem timestamps, scheduled events, or logging.

#### Expanded GPIO Header

The **2×20-pin GPIO header** exposes:

- **SPI bus** (MOSI, MISO, SCLK, CS) — for connecting additional SPI peripherals
- **I²C bus** (SDA, SCL) — for connecting I²C peripherals (sensors, displays)
- **8 general-purpose I/O pins** — directly driven by the CPLD, accessible via a port pair

This header enables **hardware experimenters** to add custom peripherals without modifying the main PCB — sensors, character LCD displays, additional DACs, relay drivers, etc.

#### Future-Proof CPLD

The EPM1270's spare logic capacity means that **future firmware updates** can add features without hardware changes. The Karabas community has discussed adding:

- Hardware sprites (similar to TS-Conf)
- A tilemap engine
- Hardware line draw and blit
- DMA controller

These features are not in the current firmware but are architecturally possible on the Peridot's CPLD. The Karabas Pro's smaller EPM570 is closer to its logic-element limit and has less room for such additions.

### When to Choose Peridot

- You are a **hardware experimenter** who wants GPIO, SPI, and I²C expansion
- You want **built-in WiFi** for networking experiments (IRC, HTTP, file downloads via NedoOS)
- You want **RTC** for filesystem timestamps or scheduled events
- You want a Karabas Pro with **room to grow** via future firmware updates

---

## Programming the Karabas Family

For most software, programming any Karabas model is **identical to programming its compatibility target** — Sinclair 128K for the Karabas 128, Pentagon 128 for the Karabas Pro and Peridot. Use the standard `#7FFD` paging, the standard port addresses, and the standard AY/Beta 128 conventions. The extensions (turbo, extended memory, SD card, WiFi, GPIO) are opt-in.

### Detecting a Karabas

The Karabas Pro and Peridot expose a version register for detection. The exact port and signature byte vary slightly across CPLD firmware revisions — consult the [Karabas project documentation](https://github.com/karabas) for the authoritative values for your firmware version.

```z80
detect_karabas:
        ; Read the Karabas version register
        ld  bc, #1FFD           ; (example port — exact address varies)
        in  a, (c)
        cp  #5A                 ; Karabas Pro signature
        jr  z, .is_karabas_pro
        cp  #5B                 ; Peridot signature
        jr  z, .is_peridot
        ; Not a Karabas — treat as plain Pentagon or 128K
        ret
.is_karabas_pro:
        ; Use Karabas Pro extensions (turbo, 512K paging)
        ret
.is_peridot:
        ; Use Peridot extensions (turbo, 512K paging, WiFi, RTC, GPIO)
        ret
```

The Karabas 128 does **not** have a unique hardware detection port — from the Z80's perspective, it looks identical to a real 128K. The only way to detect it is to look for the **absence of features** that a real 128K has (e.g., the keypad interface) — but this is unreliable. For software that needs to know it's running on a Karabas 128 (e.g., to use the SD card expansion), the convention is to probe the optional expansion ports and detect the SD card controller's signature.

### Using the GPIO Header (Peridot)

```z80
; Write a byte to the GPIO output port
write_gpio:
        ld  bc, #XX             ; GPIO port (example — see Peridot docs)
        out (c), a              ; drive 8 GPIO pins
        ret

; Read a byte from the GPIO input port
read_gpio:
        ld  bc, #YY             ; GPIO port (example — see Peridot docs)
        in  a, (c)              ; read 8 GPIO pins
        ret
```

The exact GPIO port addresses are documented in the [Peridot programmer's reference](https://github.com/peridot).

---

## Karabas vs Other Modern Spectrums

| Criterion | Karabas 128 | Karabas Pro | Peridot | ZX Evolution | ZX-Uno | Sizif-512 |
|---|---|---|---|---|---|---|
| **Architecture** | Z80 + MAX II EPM240 | Z80 + MAX II EPM570 | Z80 + MAX II EPM1270 | Z80 + Altera FPGA + ATMEGA128 | FPGA soft-core | Z80 + MAX II CPLD |
| **Max RAM** | 128 KB | 512 KB | 512 KB | 4 MB | 512 KB – 1 MB | 512 KB |
| **Compatibility target** | Sinclair 128K | Pentagon 128 | Pentagon 128 | Pentagon 1024 | 48K / 128K / Pentagon | 48K / 128K / Pentagon |
| **Turbo** | No (3.5 MHz) | 3.5 / 7 / 14 MHz | 3.5 / 7 / 14 MHz | 3.5 / 7 / 14 MHz | 3.5 / 7 MHz | 3.5 / 7 / 14 MHz |
| **Enhanced video** | None | None | None (planned in firmware) | TS-Conf (firmware swap) | ULAplus | None |
| **Storage** | Tape only (SD via expansion) | SD card | SD card | IDE + SD | SD card | None (tape) |
| **WiFi** | None | None (expansion only) | **Built-in** (ESP-12) | None (Zifi expansion) | Optional (ESP-12) | None |
| **RTC** | None | None | **Built-in** | Built-in | None | None |
| **GPIO header** | None | None | **2×20-pin** | None | None | None |
| **Video output** | VGA | VGA | VGA | SVGA | VGA | VGA + RGB |
| **Form factor** | Single-board (small) | Single-board (small) | Single-board (medium) | Single-board (large) | Single-board (small) | Single-board (small) |
| **Open source** | Yes (full) | Yes (full) | Yes (full) | Yes | Yes | Yes |
| **Cost (kit)** | ~$30–$40 | ~$40–$60 | ~$60–$80 | ~$150+ (assembled) | ~$60–$80 | ~$40–$60 |
| **Best for** | 128K software, beginners | Pentagon software, low cost | Hardware experimenters | TS-Conf development | ULAplus experiments | 48K cycle-exact testing |

The Karabas family occupies the **budget and experimenter** segment of the modern Spectrum market — the ZX Evolution and ZX Spectrum Next are more powerful but significantly more expensive; the ZX-Uno is similarly priced but FPGA-only (no real Z80); the Sizif-512 is closer in architecture but focused on 48K cycle-exact testing rather than the Karabas Pro's Pentagon focus.

---

## Cross-References

- [ZX Evolution](zx_evo.md) — the more powerful Russian alternative (Pentagon 1024, TS-Conf)
- [TS-Conf](ts_conf.md) — ZX Evolution's enhanced video firmware (sprites/tilemap/512K VRAM)
- [BaseConf](baseconf.md) — ZX Evolution's default Pentagon 1024 firmware
- [ZX-Uno](zx_uno.md) — the open-source FPGA alternative (Xilinx Spartan-6)
- [ZX Spectrum Next](zx_next.md) — the Western equivalent (FPGA, Layer 2, hardware sprites)
- [Sizif-512](../clones/sizif_harlequin.md) — similar architecture (Z80 + MAX II CPLD), 48K-focused
- [Pentagon 128](../clones/pentagon.md) — the Karabas Pro and Peridot's compatibility target
- [Sinclair 128K](../original/zx_spectrum_128.md) — the Karabas 128's compatibility target
- [Pentagon 1024](../clones/pentagon_1024.md) — extended paging reference (same `#EFF7` formula)
- [Clone timing](../clones/clone_timing.md) — the Karabas family's place in the cross-clone timing landscape
- [Clone joysticks](../clones/clone_joysticks.md) — Kempston joystick at `#1F`

---

## References

- **Karabas project** ([GitHub: karabas](https://github.com/karabas)) — official repository with schematics, PCB layouts, and CPLD firmware for all three models
- [Karabas forum](https://zx-pk.ru) — primary community hub (Russian-language), with build guides, compatibility reports, and firmware releases
- **Aleksey Makarov's pages** ("asy") — design notes, build guides, compatibility reports
- **Peridot project** ([GitHub: peridot](https://github.com/peridot)) — Peridot-specific repository with GPIO expansion examples
- [SpeccyWiki](https://speccy.info) — Karabas Pro, Karabas 128, and Peridot articles with photos and specifications
- [Unreal Speccy emulator](https://sdkcad.free.fr/) — implements Karabas Pro extensions for development testing
- **ESP-12 WiFi documentation** (Espressif) — the WiFi module's AT command reference (for Peridot networking)
- [Altera MAX II CPLD family datasheet](https://www.intel.com/content/www/us/en/products/details/fpga/max.html) — hardware reference for the EPM240/EPM570/EPM1270 used across the family
