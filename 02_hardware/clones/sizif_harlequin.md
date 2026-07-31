[← Home](../../README.md) · [Clone Hardware](README.md)

# Sizif-512 and Harlequin — Modern Hardware Recreations of the 48K

The **Harlequin** (designed by **Chris Smith**, 2010) and the **Sizif-512** (designed by **Eugene Lozovoy** / `UzixLS`, 2017) are modern hardware recreations of the Sinclair 48K Spectrum — built from contemporary components (CPLD, FPGA, or discrete CMOS logic) rather than the original Ferranti ULA. Both machines aim to produce a **cycle-accurate 48K** that runs the full Spectrum software library, including the most timing-sensitive demos, with perfect fidelity. The Harlequin is the foundational design that documented the ULA's behavior in discrete logic; the Sizif-512 builds on that foundation with a more compact CPLD implementation and adds the **Pentagon, 128K, 48K, and +3e modes**, turbo speeds, a real AY-3-8910, ULAplus, DivMMC, and a long list of community-validated expansions.

From a programmer's perspective, both machines are **transparent substitutes** for a real 48K. They implement the same memory map, the same I/O ports, the same contention pattern, the same floating-bus behavior, and the same INT timing. Software that runs on a real 48K runs identically on the Harlequin and Sizif — without any adaptation. The Sizif extends this compatibility further by allowing the developer to **switch machine personality** (Pentagon / 128 / 48 / +3e) at runtime through its Magic menu, making it a single-board cross-clone test platform.

> [!NOTE]
> **Project lineage.** The Sizif-512 source code acknowledges four direct inspirations: Chris Smith's Harlequin (48K ULA recreation), the Karabas-128 (Russian CPLD-based clone that pioneered the half-size 48K form factor), the ZX Evolution (the Russian Z80 + FPGA hybrid that proved a real Z80 + CPLD architecture works), and the open-source `zx_ula` Verilog implementation. The Sizif is the spiritual successor to all three.

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

The **Sizif-512** is Eugene Lozovoy's (`UzixLS`) compact CPLD-based recreation, built around an **Altera MAX II EPM1270 CPLD**. Where the Harlequin uses ~40 discrete CMOS chips to recreate the ULA, the Sizif collapses the entire ULA into a single 144-pin CPLD. The board is sized to **fit inside an original 48K rubber-key case** (half-size PCB) — letting owners transplant the Sizif into a Sinclair-issue case and use the original rubber keyboard. This makes the Sizif the smallest modern recreation that preserves the *original tactile feel* of the 48K.

### Architecture

| Component | Sizif-512 |
|---|---|
| **Video/memory controller** | **Altera MAX II CPLD** (EPM1270T144C5) — single chip replaces the entire ULA |
| **CPU** | **Real Z80** (CMOS, Z84C0020 — 20 MHz-rated part) running at 3.5 / 4.4 / 5.2 / 7 / 14 MHz |
| **RAM** | **512 KB SRAM** (AS6C4008) — 128 KB standard, 384 KB via `#DFFD`, 128 KB reserved for DivMMC |
| **ROM** | **512 KB flash** (SST39SF040) — holds 48K / 128K / +3e / Pentagon ROMs simultaneously |
| **Sound** | **Real AY-3-8910** (not emulated) with switchable **ABC / ACB / mono** stereo routing + beeper |
| **Video output** | **Composite (PAL) + RGB** via Sega Mini-DIN/9 connector + digital video header (EGA / VGA scandoubler) |
| **Joystick** | **Sega 3/6-button gamepad** support (Kempston or Sinclair modes) + standard Sinclair joystick ports |
| **Storage** | **Integrated DivMMC + Z-Controller** — single microSD socket, preloaded with esxDOS |
| **Keyboard** | Original 48K rubber membrane + optional PS/2 keyboard header (F1=Pause, F2=Fast-forward, F5=Magic, F10/F12=Reboot) |
| **Tape I/O** | 3.5 mm EAR jack + **Bluetooth tape input** via M18 module (rev.D+) |
| **Power** | **9–12 V DC, any polarity** (internal regulator) — barrel jack or original Sinclair 9 V supply |
| **Form factor** | Half-size PCB (fits inside an original 48K rubber-key case) |

The Sizif-512 uses a **real Z80 CPU** — not an FPGA soft-core. The CPLD handles only the ULA functions (video generation, memory arbitration, I/O decoding). This means the CPU's instruction timing is guaranteed to match a real Z80, with no soft-core approximation errors. The AY-3-8910 is likewise a **real IC**, not emulated, which gives authentic envelope and noise behavior for AY-targeted music.

### Five Machine Modes

The Sizif-512 supports four machine personalities out of the box, plus the +3e DOS extension. Selection is done through the **Magic menu** (hold the Magic button for one second):

| Mode | RAM | Video timing | Disk | Notes |
|---|---|---|---|---|
| **Spectrum 48K** | 48 KB | 69,888 T-states, 312 lines, 50 Hz | None | Cycle-accurate 48K — contention + floating bus |
| **Spectrum 128** | 128 KB (`#7FFD`) | 70,908 T-states, 311 lines, 50 Hz | Beta 128 (optional) | Late 128K / +2 personality |
| **Spectrum +3e** | 128 KB (`#7FFD` + `#1FFD`) | 70,908 T-states, 311 lines | **+3DOS floppy** | +3 personality with esxDOS extensions |
| **Pentagon 128** | 128 KB (`#7FFD`) + 384 KB (`#DFFD`) | 71,680 T-states, 320 lines, 48.83 Hz | Beta 128 (optional) | No contention, Pentagon timing |

> [!TIP]
> The Pentagon mode enables the extended `#DFFD` paging port for 384 KB extra RAM. If the SD card is inserted (DivMMC active), the Sizif reserves one 128 KB bank for DivMMC internal use, leaving 256 KB of extended RAM available.

### Turbo Modes

The Sizif's five clock speeds give the developer fine control over compatibility vs performance:

| Speed | Wait states | Use case |
|---|---|---|
| **3.5 MHz** | None (default) | Cycle-exact — all software works |
| **4.4 MHz** | None | Slight speedup; most software still works |
| **5.2 MHz** | None | Common clone speed; useful for Pentagon software |
| **7 MHz** | None (no-wait turbo) | ~2× speed — fast code that ignores cycles-per-frame |
| **14 MHz** | Inserted (turbo with wait states) | 4× speed — bottlenecked by DRAM access patterns |

> [!WARNING]
> Turbo modes accelerate access to **all** peripherals, including the Beta 128 FDC, the AY-3-8910, and the DivMMC SPI controller. Always restore 3.5 MHz before accessing these peripherals, or use esxDOS wrappers that handle it automatically.

### Extended Features Beyond the Stock 48K

The Sizif-512 includes several community-developed extensions that go beyond the original 48K specification:

| Feature | Port / mechanism | Notes |
|---|---|---|
| **ULAplus** | `#BF3B` / `#FF3B` | 256-color palette, RGB444 — software-transparent when disabled |
| **Mono Covox** | Pentagon + SpecDrum standards | 8-bit DAC on standard Pentagon covox port |
| **SounDrive** | 4-channel stereo covox | Dedicated 4-channel DAC for SounDrive-format modules |
| **Magic menu** | Magic button hold (1 sec) | Runtime configuration without reboot — Kempston / Sinclair / Cursor / QAOP navigation |
| **NMI button** | Magic button short press | Standard NMI handler — drops to esxDOS browser |
| **WiFi addon** | ESP-12 module on header | TCP/UDP sockets, HTTP client — community firmware |

### Optional Extension Board

For users needing even more capability, the Sizif-512 has an expansion header that accepts an extension board adding **TurboSound FM** (second AY + YM2203), **General Sound** (12 MHz Z80 + 512 KB RAM — the Russian 4-channel sampler), **SAA1099** (Philips sound chip), and **MIDI out**. The expansion header is pin-compatible with the ZX-Bus spec, so most existing ZX-Bus peripherals work too.

### Tested Compatibility

The Sizif-512 project maintainers have validated a long list of add-ons. Highlights include: AYX-32 (multichannel AY expander), BDI-ZX + MVcomp floppy interface, ZX Dandanator! Mini, PLUS 2A floppy controller, DivIDE, DMA 2.02 by ShamaZX, Kempston + TurboSound interface, ZX-HD (HDMI adapter), ZX-VGA-JOY, Spectranet (both ByteDelight and ShamaZX versions), and the ZXKit1 VGA converter. This is one of the **broadest expansion-compatibility lists** of any modern Spectrum recreation.

### Programming Compatibility

The Sizif-512 matches the Harlequin's 48K compatibility, and adds three more personalities on top:

| Feature | Sizif-512 (48K mode) | Sizif-512 (128 mode) | Sizif-512 (+3e mode) | Sizif-512 (Pentagon mode) |
|---|---|---|---|---|
| **Memory contention** | 48K pattern at `#4000`–`#7FFF` | 128K pattern (banks 1/3/5/7) | 128K + `#1FFD` paging | None (Pentagon has no slow RAM) |
| **Floating bus** | 48K behavior | 128K behavior | 128K behavior | Pentagon behavior (reads `#FF`) |
| **Frame timing** | 69,888 T-states | 70,908 T-states | 70,908 T-states | 71,680 T-states |
| **Scanlines** | 312 | 311 | 311 | 320 |
| **Extended paging** | No | No | `#1FFD` (ROM + paging) | `#DFFD` (384 KB extended) |
| **Disk interface** | Beta 128 (optional) | Beta 128 (optional) | **+3DOS floppy** | Beta 128 (optional) |
| **DivMMC** | Yes (always available) | Yes | Yes | Yes |

> [!TIP]
> The Sizif-512's multi-machine capability makes it the **best single hardware platform** for testing cross-clone software. Write your code, then switch the Sizif between 48K / 128 / +3e / Pentagon modes via the Magic menu to verify it works on all four without needing four separate machines.

---

## Harlequin vs Sizif — Comparison

| Criterion | Harlequin | Sizif-512 |
|---|---|---|
| **Designer** | Chris Smith (UK, 2010) | Eugene Lozovoy / `UzixLS` (Russia, 2017) |
| **Logic implementation** | Discrete CMOS (74HC) | Altera MAX II CPLD (EPM1270T144C5) |
| **Chip count** | ~40 ICs | ~5 ICs + CPLD |
| **Build difficulty** | Moderate (through-hole soldering) | Easy (mostly pre-assembled) |
| **Modifiability** | Hardware changes only | CPLD reprogramming |
| **Multi-machine** | 48K only (v3+: 128K via jumper) | **4 modes** — 48K / 128 / +3e / Pentagon |
| **Extended memory** | No | **512 KB** (Pentagon mode: `#DFFD` paging) |
| **Turbo modes** | No | **5 speeds** — 3.5 / 4.4 / 5.2 / 7 / 14 MHz |
| **Sound** | Beeper only | **Real AY-3-8910** (switchable ABC/ACB/mono) + beeper + SounDrive + Covox |
| **Palette extension** | No | **ULAplus** (256 colors) |
| **Storage** | Tape only | **DivMMC + Z-Controller** (microSD + esxDOS) |
| **Joystick** | None (add-on) | **Sega 3/6-button + Sinclair/Kempston** |
| **Magic menu** | No | **Runtime config** (turbo, mode, sound routing, etc.) |
| **Form factor** | Full-size PCB, separate case | **Half-size PCB** — fits original 48K rubber case |
| **Video output** | Composite + VGA | Composite + **RGB (Sega Mini-DIN/9)** + digital video header |
| **Power** | 5 V regulated | **9–12 V any polarity** (works with original Sinclair PSU) |
| **WiFi option** | No | **Yes** (ESP-12 module on header) |
| **Bluetooth tape input** | No | **Yes** (M18 module, rev.D+) |
| **Best for** | Purists who want discrete logic | Developers who need flexibility + multi-clone testing |

Both machines are **equally compatible** with 48K software in their default configurations. The choice between them is about the build experience (Harlequin = hands-on discrete logic; Sizif = modern CPLD) and the feature set (Harlequin = bare 48K with beeper; Sizif = multi-machine with turbo, real AY, SD storage, and broad peripheral support).

### Revision History

The Sizif-512 has gone through five major PCB revisions. Each revision added features, fixed errata, or refined the design:

| Revision | Year | Key changes |
|---|---|---|
| **Rev.A** | 2017 | First public release (errata documented in Russian) |
| **Rev.B** | 2017 | Abandoned — files kept for historical reference |
| **Rev.C / C1** | 2018 | Removed BDI, improved video circuit, larger CPLD, better power circuit, mono AY mode; fixed JTAG pinout and silkscreen |
| **Rev.D / D1** | 2019 | Added ZX-Bus connector, +3DOS floppy support, Sega 3/6-button gamepad, PS/2, Bluetooth tape input, alternative microSD socket footprint |
| **Rev.E / E1** | 2020 | Added fuse + protection diode, rotated keyboard connector, TRS→TRRS audio+video, film capacitor footprints, 5 V Sega wireless gamepad support; some experimental analog changes reverted in E1 |

> [!NOTE]
> Rev.E introduced experimental analog circuits (LM386 speaker amp, LM311 tape input, ICS501 clock generator) that were ultimately **reverted in Rev.E1**. If you have a Rev.E1 board, the analog path matches Rev.D — the experimental changes were a tangent.

### ZX Spectrum Neo — Sizif Derivative

The **ZX Spectrum Neo** (designed by Eugene Lozovoy, the same author as Sizif-512) is a directly derived platform — electronically compatible with the Sizif-512 but in a different physical form factor. The Neo targets users who want the Sizif feature set in a non-48K-case form, with modern connectivity (HDMI video, USB power, integrated keyboard) at the cost of incompatibility with the original Sinclair case.

---

## Impact on Software Development

The Harlequin and Sizif-512 have become **standard reference platforms** for ZX Spectrum software development. Their cycle-accurate timing makes them ideal for:

1. **Multicolor effect testing** — the exact contention pattern and floating-bus behavior let developers verify that timing-critical effects work on real hardware (not just emulators)
2. **Cross-clone compatibility testing** — the Sizif's multi-machine mode lets developers test on 48K, 128, +3e, and Pentagon without owning four separate machines
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
- **Harlequin project page** (zxhardware.net / zxdesign.info) — schematics, PCB layouts, and build guides for all Harlequin revisions
- **Tynemouth Software build guide** — practical assembly notes for the Harlequin v4 (Superfo) board
- **Sizif-512 GitHub repo** ([`UzixLS/zx-sizif-512`](https://github.com/UzixLS/zx-sizif-512)) — CPLD source, schematics, machine modes, revision changelog, and tested-addon list
- **Retro-Spektro Sizif-512 product page** (retro-spektro.com) — assembled board specifications and Sega gamepad button mapping
- **8bity.cz Sizif-512 review** (Martin's 8-bit blog, Czech) — independent hands-on review with photos and demonstrations
- **The Retro Shack YouTube review** — hands-on video demonstration of the Sizif-512 across all four machine modes
- **ZX Spectrum Neo documentation** (mumio.dev) — derived-platform docs confirming Lozovoy's authorship and Sizif lineage
- **Chris Smith's Harlequin documentation** — design rationale, ULA verification methodology, and compatibility testing results
- **zx-pk.ru forum** — *Harlequin* and *Sizif* subforums contain compatibility reports, modifications, and software testing threads
- **ZX Spectrum Next forums** — comparative discussions of Harlequin/Sizif vs the Next's hardware compatibility modes
