[← Home](../../README.md) · [New Gen Hardware](README.md) · [Karabas Pro](karabas_pro.md)

# Karabas 128 — The Minimalist Modern Spectrum

The **Karabas 128** is the smaller sibling of the [Karabas Pro](karabas_pro.md), designed by **Aleksey "asy" Makarov** and the Karabas community. Where the Karabas Pro targets Pentagon 128 compatibility with modern extensions (turbo, 512 KB RAM, SD card), the Karabas 128 targets the **absolute minimum** for a working 128K Spectrum: standard 128K memory, no turbo, no extended storage, no advanced features. The result is a machine that is **smaller, simpler, and cheaper** than the Karabas Pro — and that runs the same 128K Spectrum software library.

The Karabas 128 is best understood as a **modern Sinclair 128K** — a single-board machine that replaces the aging ULA and 4116 DRAM of a 1986 +2 with reliable modern components (CPLD + SRAM), while preserving the exact 128K memory map, port layout, and timing.

This article covers the Karabas 128 as a hardware platform. For the more feature-rich Karabas Pro, see [karabas_pro.md](karabas_pro.md). For the expandable Karabas-compatible platform, see [peridot.md](peridot.md).

---

## Why Karabas 128?

The Karabas 128 exists for users who want a **simple, cheap, modern 128K Spectrum** without the cost or complexity of the Karabas Pro:

| Goal | Karabas 128's approach |
|---|---|
| **128K compatibility** | Exact Sinclair 128K memory map, ports, and timing |
| **Minimal cost** | ~$30–$40 (kit), ~$50–$70 (assembled) |
| **Minimal size** | Single-board, ~8 cm × 6 cm PCB |
| **Reliability** | All modern ICs, single +5V power supply |
| **Beginner-friendly** | Fewer features means simpler build and easier debugging |

The Karabas 128 is the recommended **first build** for someone learning to assemble a Spectrum clone — the kit can be completed in an evening, and the minimal feature set means there are fewer things that can go wrong.

---

## Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | **Real Z80** (Z84C0020 — CMOS, 20 MHz-rated part), running at **3.5 MHz** (no turbo) |
| **CPLD** | **Altera MAX II EPM240** or **EPM570** — smaller than the Karabas Pro's EPM570, sufficient for 128K glue logic |
| **RAM** | **128 KB SRAM** (AS6C1008) — standard 128K, no extended paging |
| **ROM / Flash** | **128 KB or 256 KB SPI flash** — holds 128K BASIC + 48K BASIC + service ROM |
| **Video output** | **VGA** (RGB) — directly driven by the CPLD, scan-doubled for modern monitors |
| **Storage** | **None built-in** (tape only by default); SD card available via optional expansion |
| **Keyboard** | **PS/2** PC keyboard (handled by CPLD firmware) |
| **Audio** | **AY-3-8912** at standard 128K clock + beeper |
| **Joystick** | **Kempston** at `#1F` (built-in) |
| **Expansion** | **Standard Spectrum edge connector** — accepts original peripherals and the SD card expansion |
| **Power** | **5V DC** via mini-USB |
| **Form factor** | Single-board, ~8 cm × 6 cm |

The defining hardware choice is the **smaller CPLD** (EPM240 vs. Karabas Pro's EPM570). The EPM240 has fewer logic elements but is sufficient for the 128K memory map and basic I/O port decoding — the additional features of the Karabas Pro (turbo, extended paging, SD card controller) require the larger EPM570.

---

## 128K Compatibility

The Karabas 128 targets **Sinclair 128K binary compatibility** — software that runs on a real 128K or +2 runs on the Karabas 128 unmodified:

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
> The Karabas 128 **emulates 128K contention** — banks 1, 3, 5, and 7 suffer the standard `(6,5,4,3,2,1,0,0)` delay pattern when accessed during screen display. This is important for compatibility: software written for the 128K (especially demos with cycle-exact timing) depends on this contention, and would break without it.

---

## Karabas 128 vs Karabas Pro

| Criterion | Karabas 128 | Karabas Pro |
|---|---|---|
| **Compatibility target** | Sinclair 128K | Pentagon 128 |
| **RAM** | 128 KB (no extended) | 512 KB (`#EFF7` paging) |
| **Turbo mode** | No (3.5 MHz only) | Yes (3.5 / 7 / 14 MHz) |
| **Storage** | Tape only (SD via expansion) | SD card built-in |
| **CPLD** | EPM240 (smaller) | EPM570 (larger) |
| **PCB size** | ~8 cm × 6 cm | ~10 cm × 8 cm |
| **Cost (kit)** | ~$30–$40 | ~$40–$60 |
| **Timing** | 128K contention (banks 1/3/5/7) | No contention (Pentagon mode) |
| **Best for** | 128K software, beginners | Pentagon software, advanced users |

The choice between Karabas 128 and Karabas Pro comes down to **compatibility target and budget**:

- Choose **Karabas 128** if you primarily run **Western 128K software** (Sinclair demos, +2 / +3 games)
- Choose **Karabas Pro** if you primarily run **Russian software** (Pentagon demos, TR-DOS games) and want turbo mode and SD storage

---

## Programming the Karabas 128

Programming the Karabas 128 is **identical to programming a Sinclair 128K** — there are no extensions or special features to learn. Use the standard `#7FFD` paging, the standard AY port addresses, and the standard 128K ROM calls.

The only difference from a real 128K is the **PS/2 keyboard** — the Karabas 128 translates PS/2 scan codes to the Spectrum matrix in CPLD firmware, so software that reads the matrix via `#FE` works correctly, but software that reads raw PS/2 codes (rare) will not see them.

### Detecting a Karabas 128

The Karabas 128 does not have a unique hardware detection port — from the Z80's perspective, it looks identical to a real 128K. The only way to detect it is to look for the **absence of features** that a real 128K has (e.g., the keypad interface) — but this is unreliable.

For software that needs to know it's running on a Karabas 128 (e.g., to use the SD card expansion), the convention is to probe the optional expansion ports and detect the SD card controller's signature.

---

## Cross-References

- [Karabas Pro](karabas_pro.md) — the larger, more feature-rich sibling
- [Peridot](peridot.md) — the expandable Karabas-compatible platform
- [ZX-Uno](zx_uno.md) — open-source FPGA alternative
- [Sizif-512](../clones/sizif_harlequin.md) — another modern Z80 + CPLD platform
- [Sinclair 128K](../original/zx_spectrum_128.md) — the Karabas 128's compatibility target
- [Sinclair +2](../original/zx_spectrum_plus2.md) — the +2 hardware (similar to 128K)
- [Clone timing](../clones/clone_timing.md) — Karabas 128's 128K-exact timing

---

## References

- **Karabas 128 project** ([GitHub: karabas](https://github.com/karabas)) — official repository with schematics and CPLD firmware
- **Karabas forum** (zx-pk.ru) — community hub (Russian-language)
- **Aleksey Makarov's pages** — design notes and build guides
- **SpeccyWiki (speccy.info)** — Karabas 128 article
- **Unreal Speccy emulator** — implements 128K timing accurately for development testing
