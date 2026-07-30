[← Home](../../README.md) · [Clone Hardware](README.md)

# Sizif-512 and Harlequin — Modern Hardware Recreations of the 48K

The **Harlequin** (designed by **Chris Smith**, 2010) and the **Sizif-512** (designed by **Vladimir "Vexp" Kladov**, 2016) are modern hardware recreations of the Sinclair 48K Spectrum — built from contemporary components (CPLD, FPGA, or discrete CMOS logic) rather than the original Ferranti ULA. Both machines aim to produce a **cycle-accurate 48K** that runs the full Spectrum software library, including the most timing-sensitive demos, with perfect fidelity.

From a programmer's perspective, both machines are **transparent substitutes** for a real 48K. They implement the same memory map, the same I/O ports, the same contention pattern, the same floating-bus behavior, and the same INT timing. Software that runs on a real 48K runs identically on the Harlequin and Sizif — without any adaptation.

> [!NOTE]
> This article covers the **hardware platform** — what these machines are, how they differ from each other, and their programming compatibility profile. For the **FPGA internals** (gate-level ULA recreation, memory arbitration implementation, verification methodology), see [harlequin_sizif.md](../../11_emulation/fpga/harlequin_sizif.md).

---

## Why Build a Modern 48K?

The original Sinclair 48K is over 40 years old. Real hardware is increasingly rare, and the Ferranti ULA — the custom chip at the heart of the machine — is unobtainable. Modern recreations solve several problems:

| Problem | Modern recreation's solution |
|---|---|
| **ULA failure** | The ULA is the most common point of failure on aging 48K boards. Modern recreations replace it with readily available CPLD/FPGA parts. |
| **4116 DRAM deaths** | The 48K's lower 16 KB uses the unreliable 4116 triple-rail DRAM, which fails at high rates. Modern recreations use SRAM or single-rail DRAM. |
| **Timing drift** | Original ULAs have measurable timing differences between revisions (early vs late). Modern recreations can target a specific ULA revision or implement all of them. |
| **Floating bus** | The floating bus behavior is critical for multicolor effects but varies between ULA revisions. Modern recreations implement the exact 48K floating-bus timing. |
| **Video output** | Original 48Ks output RF or composite only. Modern recreations add VGA/HDMI output for contemporary displays. |

---

## The Harlequin

The **Harlequin** is Chris Smith's open-source 48K recreation. Smith is the author of *"The ZX Spectrum ULA"* (2010), the definitive reference on the ULA's internal design. The Harlequin is the physical embodiment of that research — a board that recreates the ULA's behavior using discrete CMOS logic (74HC series) rather than an FPGA.

### Architecture

| Component | Original 48K | Harlequin |
|---|---|---|
| **Video/memory controller** | Ferranti 6C001E / 7K010E ULA | **Discrete CMOS logic** (74HC series, ~40 chips) |
| **Lower RAM** | 8 × 4116 (triple-rail DRAM) | **62256 SRAM** (single +5V rail, 32 KB) |
| **Upper RAM** | 8 × 4532 / 4164 (single-rail DRAM) | **62256 SRAM** (same chip as lower) |
| **ROM** | 2364 mask ROM (16 KB) | **27C128 EPROM** or flash (16 KB) |
| **Video output** | RF + composite | **Composite + VGA** (via add-on) |
| **Power** | 9V DC (external), internal 7805 | **5V DC** (regulated, no heatsink needed) |

The Harlequin's use of discrete CMOS logic — rather than an FPGA — is a deliberate design choice. It makes the Harlequin **buildable by hobbyists** without FPGA development tools, using only standard logic chips and a soldering iron. The trade-off is a higher chip count than an FPGA solution (~40 ICs vs ~5).

### Harlequin Revisions

| Revision | Year | Key features |
|---|---|---|
| **Harlequin v1** | 2010 | Original design, 48K only, composite output |
| **Harlequin v2** | 2012 | Improved video timing, VGA output option |
| **Harlequin v3** | 2014 | 128K support (via jumper configuration) |
| **Harlequin v4 (Superfo)** | 2016 | Redesigned PCB by Superfo, smaller form factor |

### Programming Compatibility

The Harlequin is **cycle-accurate** to the 48K. All timing-sensitive features work:

- **Memory contention**: Implemented exactly — the `(6,5,4,3,2,1,0,0)` delay pattern is present at `#4000`–`#7FFF`
- **Floating bus**: Reads return the byte the video circuit is fetching, matching the 48K's behavior
- **INT timing**: 50 Hz, 312 scanlines, 69,888 T-states/frame — exact match
- **EAR/MIC timing**: Tape loading works at the same thresholds as the original
- **Port `#FE`**: Border, beeper, MIC, keyboard — all function identically

> [!NOTE]
> The Harlequin targets the **late ULA revision** (6C001E-7 / 7K010E). Early ULA quirks (the "cockroach" mod for Issue 1 boards) are not reproduced. Software that depends on early-ULA-specific behavior will not behave identically — but such software is extremely rare.

---

## The Sizif-512

The **Sizif-512** is Vladimir Kladov's 48K/128K recreation, built around an **Altera MAX II CPLD** (EPM1270 or EPM570). Where the Harlequin uses discrete logic to recreate the ULA, the Sizif uses a **programmable logic device** — making it more compact and easier to modify, but requiring FPGA development tools to change the design.

### Architecture

| Component | Sizif-512 |
|---|---|
| **Video/memory controller** | **Altera MAX II CPLD** (EPM1270T144C5) |
| **RAM** | 512 KB SRAM (AS6C4008) — only 48 KB used in 48K mode |
| **ROM** | 512 KB flash (SST39SF040) — holds multiple ROM images |
| **CPU** | **Real Z80** (CMOS, Z84C0020 — 20 MHz-rated part) |
| **Video output** | **Composite + VGA + RGB** (via headers) |
| **Power** | 5V DC (USB or barrel jack) |

The Sizif-512 uses a **real Z80 CPU** — not an FPGA soft-core. The CPLD handles only the ULA functions (video generation, memory arbitration, I/O decoding). This means the CPU's instruction timing is guaranteed to match a real Z80, with no soft-core approximation errors.

### 512 KB RAM

The Sizif-512's name comes from its 512 KB of SRAM. In 48K mode, only 48 KB is used. In 128K mode, the standard 128K map is used. The remaining RAM is accessible via **extended paging ports** — the Sizif implements `#7FFD` (128K paging) and optionally `#EFF7` (Pentagon-compatible extended paging).

This makes the Sizif-512 a **multi-machine** — it can emulate a 48K, a 128K, or a Pentagon 512K, depending on which CPLD configuration is loaded. Machine selection is typically done at power-on via a DIP switch or a configuration menu.

### Programming Compatibility

The Sizif-512 matches the Harlequin's compatibility, with additions:

| Feature | Sizif-512 (48K mode) | Sizif-512 (128K mode) | Sizif-512 (Pentagon mode) |
|---|---|---|---|
| **Memory contention** | 48K pattern at `#4000`–`#7FFF` | 128K pattern (banks 1/3/5/7) | None |
| **Floating bus** | 48K behavior | 128K behavior | Pentagon behavior (`#FF`) |
| **Frame timing** | 69,888 T-states | 70,908 T-states | 71,680 T-states |
| **Scanlines** | 312 | 311 | 320 |
| **Extended paging** | No | No | `#EFF7` |

> [!TIP]
> The Sizif-512's multi-machine capability makes it the **best single hardware platform** for testing cross-clone software. Write your code, then switch the Sizif between 48K / 128K / Pentagon modes to verify it works on all three without needing three separate machines.

---

## Harlequin vs Sizif — Comparison

| Criterion | Harlequin | Sizif-512 |
|---|---|---|
| **Logic implementation** | Discrete CMOS (74HC) | CPLD (Altera MAX II) |
| **Chip count** | ~40 ICs | ~5 ICs + CPLD |
| **Build difficulty** | Moderate (through-hole soldering) | Easy (mostly pre-assembled) |
| **Modifiability** | Hardware changes only | CPLD reprogramming |
| **Multi-machine** | 48K only (v3+: 128K via jumper) | 48K / 128K / Pentagon |
| **Extended memory** | No | 512 KB |
| **Video output** | Composite + VGA | Composite + VGA + RGB |
| **Cost (2024)** | ~$50 (kit) | ~$80 (assembled) |
| **Best for** | Purists who want discrete logic | Developers who need flexibility |

Both machines are **equally compatible** with 48K software in their default configurations. The choice between them is about the build experience (Harlequin = hands-on discrete logic; Sizif = modern CPLD) and the feature set (Harlequin = 48K only; Sizif = multi-machine).

---

## Impact on Software Development

The Harlequin and Sizif-512 have become **standard reference platforms** for ZX Spectrum software development. Their cycle-accurate timing makes them ideal for:

1. **Multicolor effect testing** — the exact contention pattern and floating-bus behavior let developers verify that timing-critical effects work on real hardware (not just emulators)
2. **Cross-clone compatibility testing** — the Sizif's multi-machine mode lets developers test on 48K, 128K, and Pentagon without owning three separate machines
3. **Tape loading** — both machines implement the 48K's EAR input thresholds, so turbo loaders and custom tape formats work identically
4. **Hardware-bug reproduction** — the floating-bus and contention behaviors let developers reproduce and work around subtle timing bugs that emulators may not model

> [!WARNING]
> Despite their accuracy, the Harlequin and Sizif are **not** original hardware. They may differ from a real 48K in subtle analog characteristics (video signal quality, audio amplifier response, RF modulator artifacts). Software that depends on analog behaviors — for example, the PAL chroma-bleed effect used by some multicolor demos — may look slightly different. Always test on original hardware if analog fidelity is critical.

---

## Cross-References

- [Harlequin and Sizif FPGA internals](../../11_emulation/fpga/harlequin_sizif.md) — ULA recreation, gate-level design, verification methodology
- [ZX Spectrum 16K / 48K](../original/zx_spectrum_16k_48k.md) — the original machine being recreated
- [ULA Architecture](../original/ula_architecture.md) — the Ferranti ULA's internal design
- [ULA Timing](../original/ula_timing.md) — contention, floating bus, multicolor constraints
- [Memory contention deep dive](../original/ula_contention.md) — the `(6,5,4,3,2,1,0,0)` pattern
- [Floating bus](../../05_development/05_display_and_timing/floating_bus.md) — programmer's guide to the floating bus
- [Pentagon 128K](pentagon.md) — the Sizif's Pentagon mode target
- [FPGA timing accuracy](../../11_emulation/fpga/fpga_timing_accuracy.md) — how FPGA/CPLD recreations compare to original hardware
- [ZX-Uno](../newgen/zx_uno.md) — another modern recreation (FPGA-based)
- [ZX Evolution](../newgen/zx_evo.md) — multi-machine FPGA platform

---

## References

- **Chris Smith — *"The ZX Spectrum ULA"*** (2010) — the definitive ULA reference that underpins the Harlequin design
- **Harlequin project page** (zxhardware.net) — schematics, PCB layouts, and build guides for all Harlequin revisions
- **Sizif-512 project** (GitHub: vexp/sizif-512) — CPLD source code, schematics, and machine configuration documentation
- **Chris Smith's Harlequin documentation** — design rationale, ULA verification methodology, and compatibility testing results
- **zx-pk.ru forum** — *Harlequin* and *Sizif* subforums contain compatibility reports, modifications, and software testing threads
- **ZX Spectrum Next forums** — comparative discussions of Harlequin/Sizif vs the Next's hardware compatibility modes
