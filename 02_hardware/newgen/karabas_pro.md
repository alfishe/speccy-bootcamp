[← Home](../../README.md) · [New Gen Hardware](README.md)

# Karabas Pro — The Compact Modern Z80 + CPLD Spectrum

The **Karabas Pro** is a modern (2018+) Russian ZX Spectrum clone designed by **Aleksey "asy" Makarov** and the Karabas community. It is a **compact single-board** computer pairing a real **Z80 CPU** with an **Altera MAX II CPLD** (EPM570) for the ULA functions, address decoding, and I/O port mapping. The design is fully open-source — schematics, PCB layout, and CPLD firmware are all available on GitHub.

For software developers, the Karabas Pro is best understood as a **modernized Pentagon 128** — it runs the entire Russian Spectrum software library unmodified, with the same memory map, the same I/O ports, and (almost) the same timing. Where it differs from a 1990s Pentagon is in **hardware quality and modern conveniences**: integrated PS/2 keyboard, SD card storage, VGA output, turbo mode, and reliable modern components.

This article covers the Karabas Pro as a hardware platform. For the broader modern-Spectrum landscape, see [zx_evo.md](zx_evo.md) (Russian), [zx_next.md](zx_next.md) (Western), and [zx_uno.md](zx_uno.md) (open-source FPGA). For comparison with the smaller **Karabas 128**, see [karabas_128.md](karabas_128.md).

---

## Why Karabas Pro?

The Russian Spectrum scene of the late 2010s had a gap:

- **ZX Evolution** (2007) — powerful but expensive, complex PCB, harder to build
- **Pentagon** (1989) — old, unreliable hardware, no modern features
- **TS-Conf** — requires ZX Evolution, complex firmware stack

What was missing was a **simple, cheap, modern Pentagon** — a single-board machine that anyone could build from a kit, with all the essential modern features and nothing unnecessary. The Karabas Pro fills this gap.

| Goal | Karabas Pro's approach |
|---|---|
| **Pentagon compatibility** | Exact memory map, port layout, and (almost) timing |
| **Modern components** | All-new ICs (no 30-year-old Soviet parts), single +5V power supply |
| **Compact size** | Single-board, ~10 cm × 8 cm PCB |
| **Affordable** | ~$40-60 (kit), ~$80-100 (assembled) |
| **Open source** | Schematics, PCB, CPLD firmware all on GitHub |
| **Modern conveniences** | PS/2 keyboard, SD card, VGA output, turbo mode |

---

## Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | **Real Z80** (Z84C0020 — 20 MHz-rated CMOS part), running at 3.5 / 7 / 14 MHz |
| **CPLD** | **Altera MAX II EPM570** — handles the ULA functions, address decoding, memory paging, and I/O port mapping |
| **RAM** | **512 KB** SRAM (AS6C4008) — 8x the Pentagon's 64 KB |
| **ROM / Flash** | **512 KB** SPI flash (SST39SF040) — holds multiple ROM images, selectable at boot |
| **Video output** | **VGA** (RGB) — directly driven by the CPLD, scan-doubled for modern monitors |
| **Storage** | **SD card via SPI** (Holteck HC-MSD001 controller or similar) |
| **Keyboard** | **PS/2** PC keyboard (handled by the SD controller's auxiliary firmware) |
| **Audio** | **AY-3-8912** (single chip, Pentagon-compatible clock) + beeper + DAC (Covox-style) |
| **Joystick** | **Kempston** at `#1F` (built-in) |
| **Expansion** | **Pentagon edge connector** — accepts original Pentagon peripherals |
| **Power** | **5V DC** via mini-USB |
| **Form factor** | Single-board, ~10 cm × 8 cm |

The defining hardware choice is the **MAX II CPLD** — the same part used in the Sizif-512 (see [sizif_harlequin.md](../clones/sizif_harlequin.md)). It is a **low-cost, modern CPLD** (vs. the older MAX 7000 series used in the ZX Evolution) with enough logic elements to implement the ULA's video generation and memory arbitration in a single chip.

---

## Pentagon 128 Compatibility

The Karabas Pro targets **Pentagon 128 binary compatibility**. Software that runs on a real Pentagon 128 should run on the Karabas Pro with no modifications:

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

The Karabas Pro also supports an optional **48K mode** (different timing — 69,888 T-states, 312 lines, 50.08 Hz, with contention) selectable at boot. This mode is for running Western software that depends on 48K timing.

---

## Extensions Beyond Pentagon

The Karabas Pro adds several modern features the original Pentagon lacked:

### Turbo Mode

3.5 / 7 / 14 MHz selectable via a port write (typically `#DFFD` bit 6 or a Karabas-specific port). As with the ZX Evolution, **always restore 3.5 MHz before accessing slow peripherals**.

### Extended Memory — 512 KB

The Karabas Pro's 512 KB is accessible via the Pentagon's `#EFF7` extended paging port — `(#EFF7 & 0x07) × 8 + (#7FFD & 0x07)` gives 32 banks (512 KB). This is the same formula as the Pentagon 1024, just with fewer banks physically populated.

### SD Card Storage

The SD card is accessible via a SPI controller, presenting a DivMMC-compatible interface. Software written for the DivMMC (modern Russian DOS-aware software) runs unchanged.

### PS/2 Keyboard

A PS/2 PC keyboard connects via a standard mini-DIN connector. The Karabas Pro's CPLD firmware handles the PS/2 protocol and translates scan codes to Spectrum matrix positions.

### VGA Output

Video output is **VGA** (RGB) — directly driven by the CPLD with a built-in scan doubler for compatibility with modern monitors. The scan doubler doubles the horizontal sync rate to ~31 kHz (vs. the original 15 kHz), making the Karabas Pro compatible with any VGA monitor.

### Covox DAC

An 8-bit Covox-style DAC (typically mapped to port `#FB` or `#1F`) provides 8-bit PCM sample playback — useful for digitized sound effects and music.

---

## Programming the Karabas Pro

For most software, programming the Karabas Pro is **identical to programming a Pentagon 128** — use the standard `#7FFD` paging, the standard port addresses, and the standard AY/Beta 128 conventions. The extensions (turbo, extended memory, SD card) are opt-in.

### Detecting a Karabas Pro

```z80
detect_karabas:
        ; Read the Karabas Pro version register
        ld  bc, #1FFD           ; (example port — exact address varies)
        in  a, (c)
        cp  #5A                 ; Karabas Pro signature
        jr  z, .is_karabas
        ; Not a Karabas — treat as plain Pentagon
        ret
.is_karabas:
        ; Use Karabas extensions (turbo, 512K paging)
        ret
```

For the exact detection port and signature byte, see the [Karabas Pro documentation](https://github.com/karabas) — these vary slightly across CPLD firmware revisions.

---

## Karabas Pro vs. Other Modern Spectrums

| Criterion | Karabas Pro | ZX Evolution | ZX-Uno | Sizif-512 |
|---|---|---|---|---|
| **Architecture** | Z80 + MAX II CPLD | Z80 + MAX 7000 CPLDs + ATmega | FPGA soft-core | Z80 + MAX II CPLD |
| **Max RAM** | 512 KB | 4 MB | 512 KB – 1 MB | 512 KB |
| **Compatibility target** | Pentagon 128 | Pentagon 1024 | 48K / 128K / Pentagon | 48K / 128K / Pentagon |
| **Enhanced video** | None | TS-Conf (firmware swap) | ULAplus | None |
| **Storage** | SD card | IDE + SD | SD card | None (tape) |
| **Video output** | VGA | SVGA | VGA | VGA + RGB |
| **Form factor** | Single-board (small) | Single-board (large) | Single-board (small) | Single-board (small) |
| **Open source** | Yes (full) | Yes | Yes | Yes |
| **Best for** | Pentagon compatibility, low cost | TS-Conf development | ULAplus experiments | 48K cycle-exact testing |

The Karabas Pro is **the right choice for developers who want a cheap, reliable, modern Pentagon** without the complexity of the ZX Evolution or the FPGA-only approach of the ZX-Uno.

---

## Cross-References

- [Karabas 128](karabas_128.md) — the smaller 128K-only sibling
- [Peridot](peridot.md) — the expandable Karabas-compatible platform
- [ZX Evolution](zx_evo.md) — the more powerful Russian alternative
- [ZX-Uno](zx_uno.md) — the open-source FPGA alternative
- [Sizif-512](../clones/sizif_harlequin.md) — similar architecture (Z80 + MAX II CPLD), 48K-focused
- [Pentagon 128](../clones/pentagon.md) — the Karabas Pro's compatibility target
- [Pentagon 1024](../clones/pentagon_1024.md) — extended paging reference
- [Clone timing](../clones/clone_timing.md) — Karabas Pro's place in the cross-clone landscape

---

## References

- **Karabas Pro project** ([GitHub: karabas](https://github.com/karabas)) — official repository with schematics, PCB layouts, and CPLD firmware
- **Karabas Pro forum** (zx-pk.ru) — primary community hub (Russian-language)
- **Aleksey Makarov's pages** — design notes, build guides, compatibility reports
- **Karabas Pro wiki** — community-maintained documentation (Russian)
- **SpeccyWiki (speccy.info)** — Karabas Pro article with photos and specifications
- **Unreal Speccy emulator** — implements Karabas Pro extensions for development testing
