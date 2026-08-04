[← Overview](README.md) · [Hardware Models](hardware_models.md)

# Hardware Models — Cross-Track Catalog and Comparison Matrices

> **Scope**: This article is the **navigational hub** for ZX Spectrum hardware across all three tracks (Original, Soviet Clones, New Gen). It provides high-level comparison matrices that help you choose the right model for a given task, then links to the per-model deep-dive articles for the details.

For the **chronological story** of how these models came to be, see [history.md](history.md). For the **detailed timing comparison** that matters for software development (contention patterns, frame timing, INT position), see [video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md). For the **deep technical documentation** of any specific model, follow the cross-references from the per-track tables below.

---

## Article Roadmap

- §1 — The three-track model taxonomy
- §2 — Original Sinclair/Amstrad models (1982–1992)
- §3 — Soviet clone models (1989–2000s)
- §4 — New Generation models (2010s–present)
- §5 — Cross-track comparison matrices
- §6 — How to choose a model

---

## 1. The Three-Track Model Taxonomy

Every ZX Spectrum-compatible machine falls into one of three historical tracks. Each track has its own design philosophy, target market, and technical characteristics.

| Track | Era | Region | Design philosophy | Primary models |
|---|---|---|---|---|
| **Original** | 1982–1992 | UK / Spain | Sinclair's "cheap and clever" → Amstrad's cost-reduction | 16K, 48K, Spectrum+, 128K, +2, +2A, +3 |
| **Soviet Clones** | 1989–2000s | USSR / post-Soviet states | Buildable from discrete TTL, optimized for hobbyist construction | Pentagon, Scorpion, ATM Turbo, Kay, Profi, Byte, Leningrad |
| **New Generation** | 2010s–present | International | FPGA-based, extends Spectrum architecture with modern features | ZX Spectrum Next, ZX Uno, ZX Evolution (TS-Conf/BaseConf), Sprinter, Karabas |

The tracks are not mutually exclusive — a modern MiSTer FPGA can emulate any model from any track, and a modern game might target Pentagon timing while running on a ZX Spectrum Next. But for understanding the hardware landscape, the three-track division remains useful.

For the **timing families** that matter for software compatibility (Sinclair-derived vs Pentagon-derived vs Divergent), see [video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md) §1.

---

## 2. Original Sinclair/Amstrad Models (1982–1992)

The Original track covers every machine designed and built by Sinclair Research or Amstrad under the Sinclair brand. These are the reference platforms — every clone and every FPGA implementation aims to be compatible with at least one Original-track model.

| Model | Year | RAM | ROM | Sound | Notable features | Article |
|---|---|---|---|---|---|---|
| **ZX Spectrum 16K** | 1982 | 16 KB | 16 KB | Beeper | Entry model; no upper RAM fitted | [zx_spectrum_16k_48k.md](../02_hardware/original/zx_spectrum_16k_48k.md) |
| **ZX Spectrum 48K** | 1982 | 48 KB | 16 KB | Beeper | The canonical reference platform; ~5M units sold | [zx_spectrum_16k_48k.md](../02_hardware/original/zx_spectrum_16k_48k.md) |
| **ZX Spectrum+** | 1984 | 48 KB | 16 KB | Beeper | Full-travel keyboard, reset key, new case | [zx_spectrum_16k_48k.md](../02_hardware/original/zx_spectrum_16k_48k.md) |
| **ZX Spectrum 128K** ("Toast Rack") | 1985/1986 | 128 KB | 32 KB (2 banks) | Beeper + **AY-3-8912** | Sinclair's last; `#7FFD` paging, keypad, RS-232 | [zx_spectrum_128.md](../02_hardware/original/zx_spectrum_128.md) |
| **ZX Spectrum +2** (grey) | 1986 | 128 KB | 32 KB (2 banks) | Beeper + AY-3-8912 | Amstrad; integrated tape, full-travel keyboard | [zx_spectrum_plus2.md](../02_hardware/original/zx_spectrum_plus2.md) |
| **ZX Spectrum +2A** (black) | 1987 | 128 KB | 64 KB (4 banks) | Beeper + AY-3-8912 | Amstrad ASIC redesign; new contention model; `#1FFD` paging | [zx_spectrum_plus2a_plus3.md](../02_hardware/original/zx_spectrum_plus2a_plus3.md) |
| **ZX Spectrum +3** | 1987 | 128 KB | 64 KB (4 banks) | Beeper + AY-3-8912 | +2A with internal 3" floppy; +3DOS disk OS | [zx_spectrum_plus2a_plus3.md](../02_hardware/original/zx_spectrum_plus2a_plus3.md) |

### Original-track key characteristics

- **CPU**: Zilog Z80A at 3.5 MHz (3.500000 MHz exactly), all models.
- **Frame timing**: 69,888 T-states (48K) or 70,908 T-states (128K/+2/+2A/+3) per frame. ~50 Hz refresh. See [video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md).
- **Memory contention**: 48K/128K/+2 use the Ferranti 6-5-4-3-2-1-0-0 pattern; +2A/+3 use the Amstrad ASIC's 1-0-7-6-5-4-3-2 pattern gated by `MREQ`. See [ula_contention.md](../02_hardware/original/ula_contention.md).
- **Video**: 256×192 pixels with 8×8 attribute cells giving 2 colors per 8×8 cell, 15-color palette + bright bit. Plus a 32×24 border that can be colored via port `#FE`.
- **Sound**: 1-bit beeper on all models; AY-3-8912 added from the 128K onward.
- **Storage**: cassette tape via port `#FE` (all models); +3 added 3" floppy.

For the per-model technical deep dives, see the [02_hardware/original/](../02_hardware/original/README.md) section.

---

## 3. Soviet Clone Models (1989–2000s)

The Soviet clone track emerged from the hobbyist-built DIY culture of the late 1980s and grew into a vast ecosystem of commercial designs in the 1990s. By 1995 the post-Soviet clone market was substantially larger than the Western Spectrum market had ever been.

| Model | Year | RAM | Sound | Notable features | Article |
|---|---|---|---|---|---|
| **Leningrad-1** | 1987 | 48 KB | Beeper | First major DIY Soviet clone; ~50 ICs; Sergey Zonov design | [other_clones.md](../02_hardware/clones/other_clones.md) |
| **Pentagon 48K** | 1989 | 48 KB | Beeper | Most popular Soviet clone; discrete TTL, no contention | [pentagon.md](../02_hardware/clones/pentagon.md) |
| **Pentagon 128K** | 1990 | 128 KB | Beeper + AY | `#7FFD` paging, Beta 128 FDC, built-in Kempston | [pentagon.md](../02_hardware/clones/pentagon.md) |
| **Pentagon 1024 / 1024SL** | 1995 | 1024 KB | Beeper + AY | Extended memory via `#EFF7`; some IDE/GS variants | [pentagon_1024.md](../02_hardware/clones/pentagon_1024.md) |
| **Scorpion ZS-256** | 1993 | 256 KB | Beeper + AY | Developer-focused; Shadow Service Monitor debugger; ProfROM | [scorpion.md](../02_hardware/clones/scorpion.md) |
| **ATM Turbo 1/2** | 1990s | 256K–1024K | Beeper + AY + Covox | EGA-like graphics modes, IDE HDD, 7 MHz turbo, CP/M in ROM | [atm_turbo.md](../02_hardware/clones/atm_turbo.md) |
| **Kay 1024** | 1990s | 1024 KB | Beeper + AY | Professional-oriented; multiple ROM banks, IDE | [kay.md](../02_hardware/clones/kay.md) |
| **Profi 5103** | 1990s | 512 KB | Beeper + AY | ISA-like expansion, VGA output option | [profi.md](../02_hardware/clones/profi.md) |
| **Byte** | 1990s | varies | Beeper + AY | Ukrainian compact design | [byte.md](../02_hardware/clones/byte.md) |
| **Others (Hobbit, Quorum, LEC, Moscow, Balansir)** | various | varies | varies | Locally significant DIY designs | [other_clones.md](../02_hardware/clones/other_clones.md) |

### Soviet-clone key characteristics

- **CPU**: Z80-compatible (Soviet KR1858VM1 or similar) at 3.5 MHz, often with 7 MHz turbo options.
- **Frame timing**: **Pentagon timing** (320 scanlines, 71,680 T-states, ~48.83 Hz) became the standard. **No memory contention** is the defining feature compared to original Sinclair hardware. See [clone_timing.md](../02_hardware/clones/clone_timing.md).
- **Memory**: `#7FFD` paging scheme inherited from Sinclair 128K; extended to 512K/1024K via `#EFF7` (Pentagon) or model-specific ports.
- **Storage**: Beta 128 disk interface with TR-DOS is standard; tape is secondary.
- **Sound**: AY-3-8912 (or Soviet clone Т34ВГ1) standard from 128K models onward.
- **Joystick**: Kempston is built-in on nearly all models (vs Sinclair's external interface). See [clone_joysticks.md](../02_hardware/clones/clone_joysticks.md).

For the per-model technical deep dives, see the [02_hardware/clones/](../02_hardware/clones/README.md) section.

---

## 4. New Generation Models (2010s–present)

The New Gen track emerged from the modern retro-computing movement and combines Spectrum compatibility with modern FPGA-based hardware capabilities. Some models (Harlequin, Sizif, Karabas) aim for faithful hardware recreation; others (ZX Uno, TS-Conf, ZX Spectrum Next) extend the architecture.

| Model | Year | FPGA / logic | Key features | Article |
|---|---|---|---|---|
| **Harlequin** | 2012+ | Discrete 74-series | Faithful 48K recreation; Chris Smith design | [sizif_harlequin.md](../02_hardware/clones/sizif_harlequin.md) |
| **Sizif-512** | 2010s | FPGA | Modern 48K/128K recreation with Pentagon extensions | [sizif_harlequin.md](../02_hardware/clones/sizif_harlequin.md) |
| **ZX Evolution (BaseConf)** | 2010+ | CPLD + real Z80 | Pentagon evolution; Beta 128, IDE, SMUC ISA bridge | [zx_evo.md](../02_hardware/newgen/zx_evo.md), [baseconf.md](../02_hardware/newgen/baseconf.md) |
| **ZX Evolution (TS-Conf)** | 2010+ | CPLD + real Z80 | BaseConf + tile-based video, hardware sprites, 640×200 modes | [ts_conf.md](../02_hardware/newgen/ts_conf.md) |
| **Sprinter** | 2000s | CPLD + real Z80 | PC-like Spectrum; SVGA output, ~70 Hz frame, ISA-ish expansion | [sprinter.md](../02_hardware/newgen/sprinter.md) |
| **ZX Uno** | 2016+ | FPGA (Altera Cyclone IV) | 28 MHz accelerator, expanded memory, SD storage; Spanish design | [zx_uno.md](../02_hardware/newgen/zx_uno.md) |
| **Karabas** | 2010s+ | FPGA | Modern Russian recreation; Karabas 128 + Peridot variants | [karabas.md](../02_hardware/newgen/karabas.md) |
| **ZX Spectrum Next** | 2020+ | FPGA (Spartan-6 LX16) | Z80N CPU @ 28 MHz, Layer 2, hardware sprites, tilemap, copper, 3× AY, Raspberry Pi socket | [zx_next.md](../02_hardware/newgen/zx_next.md) |

### New Gen key characteristics

- **CPU**: Z80-compatible CPU (some use real Z80 chips, others use FPGA-synthesized Z80 cores). The Next uses a custom **Z80N** core with new instructions including `MUL D,E`, `PIXELADD`, `SWAPNIB`, and barrel-shift operations.
- **Frame timing**: Typically **configurable** — most can emulate 48K, 128K, +2A, and Pentagon timing via configuration switches.
- **Memory**: 512 KB to 2 MB is common, with extended paging schemes (e.g., the Next's MMU slots). The Next has 2 MB with 8 KB slot granularity.
- **Video**: Original Spectrum video + extensions. The Next's Layer 2 (256-color framebuffer), hardware sprites (64 per scanline, 16×16), tilemap (320×256), and copper (raster coprocessor) substantially extend the architecture. See [next_graphics.md](../05_development/06_graphics/next_graphics.md).
- **Sound**: AY-3-8912 (synthesized) standard; Next supports 3× AY ("TurboSound") plus DMA-based sample playback.

For the per-model technical deep dives, see the [02_hardware/newgen/](../02_hardware/newgen/README.md) section.

---

## 5. Cross-Track Comparison Matrices

These matrices compare models across tracks on the dimensions that matter most for software development. For full per-instruction timing, see [timing_reference.md](../10_references/timing_reference.md) and [contention_timing.md](../05_development/05_display_and_timing/contention_timing.md).

### Frame timing comparison

| Model | Scanlines | T-states/line | T-states/frame | Frame rate | Contention | Family |
|---|---|---|---|---|---|---|
| ZX Spectrum 16K/48K | 312 | 224 | 69,888 | 50.08 Hz | Yes (`6-5-4-3-2-1-0-0`) | A (Sinclair) |
| ZX Spectrum 128K / +2 | 311 | 228 | 70,908 | 49.90 Hz | Yes (odd banks only) | A (Sinclair) |
| ZX Spectrum +2A / +3 | 311 | 228 | 70,908 | 49.90 Hz | Yes (`1-0-7-6-5-4-3-2`) | A (Sinclair) |
| Pentagon 128K/1024K | 320 | 224 | 71,680 | 48.83 Hz | **None** | B (Pentagon) |
| Scorpion ZS-256 | 312 | 228 | 70,944 | ~49.93 Hz | Revision-dependent | A (Sinclair) |
| ATM Turbo (3.5 MHz) | 312 | 228 | 70,908 | 49.90 Hz | None | A (Sinclair) |
| ATM Turbo (7 MHz) | varies | varies | ~99,880 | varies | None | C (Divergent) |
| Sprinter | varies | varies | ~285,714 | ~70 Hz | None | C (Divergent) |
| ZX Spectrum Next | Configurable | Configurable | matches selected | matches selected | matches selected | All |
| MiSTer (per selected core) | matches | matches | matches | matches | matches | All |

For the full per-model timing reference and the family classification rationale, see [video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md).

### Memory architecture comparison

| Model | Total RAM | Paging register | Bank granularity | ROM | Special modes |
|---|---|---|---|---|---|
| ZX Spectrum 16K | 16 KB | n/a | n/a | 16 KB | n/a |
| ZX Spectrum 48K | 48 KB | n/a (contiguous) | n/a | 16 KB | n/a |
| ZX Spectrum 128K | 128 KB | `#7FFD` | 16 KB | 32 KB (2 switchable banks) | 48K mode via `USR 0` |
| ZX Spectrum +2/+2A/+3 | 128 KB | `#7FFD` + (`#1FFD` on +2A/+3) | 16 KB | 32 KB (+2) / 64 KB (+2A/+3, 4 banks) | CP/M mode (+3 via `#1FFD` special paging) |
| Pentagon 128K | 128 KB | `#7FFD` | 16 KB | 32 KB (Sinclair-compatible) | None |
| Pentagon 1024K | 1024 KB | `#7FFD` + `#EFF7` | 16 KB | 32 KB | None |
| Scorpion ZS-256 | 256 KB | `#7FFD` + `#1FFD` | 16 KB | 64 KB ProfROM | None |
| ATM Turbo 2+ | 1024 KB | `#7FFD` + `#EFF7` + model-specific | 16 KB | 128 KB (4 banks) | CP/M mode in ROM |
| ZX Spectrum Next | 2 MB | NextRegs `50`-`57` (MMU slots) | 8 KB | 1 MB | Layer 2 banks, hardware sprite banks, RAM disk |

For the per-model memory map details, see [memory_maps.md](../10_references/memory_maps.md).

### Sound capability comparison

| Model | Beeper | AY chip | Covox / DAC | TurboSound (3× AY) | Sample playback |
|---|---|---|---|---|---|
| 16K / 48K / Spectrum+ | Yes (port `#FE`) | No | Add-on only | No | Software bit-banging only |
| 128K / +2 / +2A / +3 | Yes | Yes (AY-3-8912) | Add-on only | No | Software bit-banging via AY |
| Pentagon 128K+ | Yes | Yes (Т34ВГ1) | Add-on | Add-on | Software + General Sound external |
| ATM Turbo | Yes | Yes | **Built-in** | Add-on | Covox + AY |
| Scorpion ZS-256 | Yes | Yes | Add-on | Add-on | Software + AY |
| ZX Spectrum Next | Yes | Yes (3× via TurboSound) | Yes (DMA) | **Yes** | **DMA-based at up to ~50 kHz** |

For sound synthesis techniques, see [ay_ym_synthesis.md](../06_sound/synthesis/ay_ym_synthesis.md) and [beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md).

---

## 6. How to Choose a Model

The right model depends on what you are doing:

| If you are... | Choose... | Because... |
|---|---|---|
| Writing a game for the original Spectrum experience | **48K** (real iron or MiSTer core) | Largest original-era software base; the reference platform for 1982–1986 games |
| Writing a game that uses AY music | **128K** or **+2** | Standard AY chip; full compatibility with 128K-era software |
| Writing a game for the post-Soviet demoscene | **Pentagon 128K** | Standard target for Russian-language Spectrum software; TR-DOS disk distribution |
| Writing a multicolor/race-the-beam effect | **48K** (real iron or accurate FPGA) | Contention-based timing is the only way these effects work; no-clone hardware breaks them |
| Writing modern Spectrum software with extended graphics | **ZX Spectrum Next** | Layer 2, sprites, tilemap, copper remove the original constraints; 28 MHz gives 8× CPU performance |
| Studying Soviet clone architecture | **Pentagon 128K + Scorpion** | The two most popular clones with different design philosophies |
| Testing software across the whole ecosystem | **MiSTer** | One FPGA platform, switchable timing models, cycle-exact emulation of all original-track and Pentagon models |
| Doing hardware-level reverse engineering | **48K + Pentagon** (real iron) | Real hardware has analog subtleties (contention edge cases, floating bus behavior) that emulation sometimes misses |

---

## 7. Cross-References

- [history.md](history.md) — Chronological story of how these models came to be.
- [glossary.md](glossary.md) — Definitions of every term used in this article (ULA, AY, contention, `#7FFD`, etc.).
- [02_hardware/original/](../02_hardware/original/README.md) — Section index for Original-track models.
- [02_hardware/clones/](../02_hardware/clones/README.md) — Section index for Soviet clone models.
- [02_hardware/newgen/](../02_hardware/newgen/README.md) — Section index for New Generation models.
- [video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md) — Deep dive on per-model timing, contention, and INT position differences.
- [clone_timing.md](../02_hardware/clones/clone_timing.md) — Soviet-clone timing reference and cross-platform strategies.
- [memory_maps.md](../10_references/memory_maps.md) — Per-model memory map catalog.
- [io_port_map.md](../10_references/io_port_map.md) — Per-model I/O port reference.
- [timing_reference.md](../10_references/timing_reference.md) — T-state timing tables for every instruction and addressing mode.
- [next_graphics.md](../05_development/06_graphics/next_graphics.md) — The Next's Layer 2 / sprites / tilemap / copper architecture.

## References

### External references

- [Chris Smith — The ZX Spectrum ULA](http://www.zxdesign.info/) — the definitive reference for the original Sinclair 48K and 128K hardware; covers the Ferranti ULA variants, the +2's ASIC evolution, and the gate-array layout.
- [Sinclair ZX Specifications](http://problemkaputt.de/zxdocs.htm) — the canonical cross-model hardware reference; documents every Sinclair-released Spectrum variant (Issue 1/2/3/4/5/6 mainboards, +2, +2A, +3, +2B, Spanish 128K).
- [Spectrumpedia](https://speccy.wiki/) — the most complete print reference for Soviet-clone hardware; covers Pentagon, Scorpion, Kay, Profi, Leningrad, ATM Turbo, and the modern FPGA reimplementations.
- [zx-pk.ru hardware reference wiki](https://zx-pk.ru) — community-maintained cross-reference of Soviet clone hardware specs, including rare variants (Pentagon 1024SL V2, Scorpion ZS-256 Turbo+, Kay 2006 NB CPLD).
- [ZX Spectrum Next Weekend Assembly documentation](https://zxnext.io) — the canonical reference for the Next's hardware (2-layer board, expansion bus, the FPGA core), and for the modern extensions to the original architecture.
