[← Home](../../README.md) · [Emulation](../README.md) · [FPGA Cores](README.md)

# Cycle-Exact Timing in Spectrum FPGA Cores

The defining promise of an FPGA Spectrum recreation is **timing fidelity** — that software which depends on cycle-precise hardware behavior will run identically on the FPGA as on a real Spectrum. This is what separates a faithful FPGA core from a software emulator: the latter can approximate the timing but cannot reproduce it exactly, because it runs on a host CPU that is many orders of magnitude faster than the original Z80 but is not synchronized to the Spectrum's pixel clock.

Achieving cycle-exact timing in an FPGA core is a substantial engineering challenge. The Spectrum's hardware has subtle, undocumented timing behaviors that software depends on — sometimes intentionally (demoscene effects), sometimes accidentally (copy protection, timing-sensitive loops). This article covers the timing requirements, the implementation techniques, common pitfalls, and verification methods used in modern Spectrum FPGA cores.

For the broader context of how FPGA cores are designed, see [fpga_implementation.md](fpga_implementation.md). For specific implementations and their timing fidelity, see [mist_mister_core.md](mist_mister_core.md), [zx_uno_core.md](zx_uno_core.md), [harlequin_sizif.md](harlequin_sizif.md), and [zxevo.md](zxevo.md).

---

## Why Timing Matters

### The Spectrum's Timing Sensitivity

The ZX Spectrum is a remarkably timing-sensitive machine. Because the ULA shares memory between the CPU and the video fetch circuitry, accessing contended memory (`#4000`–`#7FFF` in the 48K; specific pages in the 128K) causes the CPU to be held off for **specific numbers of cycles** depending on where the video beam is on the screen. This creates an indirect but precise relationship between CPU execution and video position.

Software can detect this relationship in several ways:

- **Reading the floating bus** — port `#FF` reads during specific cycles return the byte the ULA is fetching from video memory, revealing the current screen position
- **Timing instruction sequences** — by executing a known instruction sequence and checking how long it took, software can infer contention and thus video position
- **Raster interrupts** — the INT signal is asserted at a known point in the frame, and software can use `HALT` + instruction counting to position itself relative to the video beam

These techniques are used by:

- **Demoscene effects** — multicolor (changing attributes mid-frame), raster bars, sync-scrollers effects, border color cycling
- **Game copy protection** — timing checks that detect emulators (Latenite, Speedlock, Alkatraz)
- **Loader routines** — tape loaders and custom disk loaders that rely on exact timing for data recovery
- **Timing-based software** — some games use contention timing for animation pacing

### Demoscene Effects

The most demanding timing-dependent effects are in the demoscene:

- **Multicolor** — changing attribute bytes during the horizontal border to produce a 2-pixel-wide color effect (8 attributes per character line × 8 lines = 64 colors per character cell position per frame)
- **Bobs** — software sprites drawn via attribute changes timed to specific scanlines
- **Sync-scroller** — synchronizing to a specific scanline and using timed memory writes to produce smooth horizontal scrolling
- **Copper bars** — changing the BORDER register at specific horizontal positions to produce colored vertical bars

These effects require **T-state-precise** timing — a 1-cycle error is visible as a misaligned pixel. A core that is off by even one T-state in its contention pattern will produce visible glitches in multicolor demos.

### Copy Protection

Many commercial Spectrum games include **anti-emulator protection** that detects non-cycle-exact execution:

- **Speedlock** — measures the contention pattern at boot and refuses to run if it doesn't match
- **Alkatraz** — uses timing to verify it's running on real hardware
- **Latenite** — checks instruction timing including undocumented instructions

A core that is not cycle-exact will fail these checks, making protected software unrunnable.

---

## Timing Models: Scanline-Precise vs T-State-Precise

Two broad approaches exist for handling Spectrum timing in HDL:

### Scanline-Precise (Approximate)

In a scanline-precise core, the implementation models the **gross** video timing — the screen has the right number of scanlines, the INT is asserted at the right line, the border is the right width — but the **fine** timing details are approximated. Specifically:

- The contention pattern is implemented as **uniform delays** per contended access, rather than the specific per-cycle pattern of the real ULA
- The floating bus returns either a fixed value, a random value, or an approximate "current video byte"
- The CPU/video arbitration is simplified — typically the CPU is held off for a fixed number of cycles per video fetch, rather than the asymmetric pattern of the original

Scanline-precise cores are **easier to implement** and work for the vast majority of software (95%+ of commercial games and most demos). They fail on:

- Multicolor demos and other T-state-precise effects
- Floating-bus-dependent software (some games detect screen position via floating bus)
- Copy protection that checks contention patterns

Most early software emulators (and some FPGA cores for the ZX Spectrum Next, which is less timing-sensitive due to its hardware features) are scanline-precise.

### T-State-Precise (Cycle-Exact)

A T-state-precise core reproduces the Spectrum's timing **exactly** — every T-state of CPU execution is in the right relationship to the video beam. This requires:

- **Exact contention pattern** — the precise pattern of WAIT assertions on each scanline, matching the original ULA's behavior documented in Chris Smith's *The ZX Spectrum ULA: How to Design a Microcomputer*
- **Exact floating bus behavior** — port `#FF` reads return the exact byte the ULA is fetching in each specific cycle, with the right latency
- **Exact INT timing** — the INT signal is asserted at the exact cycle, and the CPU's response time matches
- **Exact CPU cycle counts** — every Z80 instruction takes the documented number of T-states, including the undocumented cycle counts of `LD A,I`, `LD A,R`, `RLD`, `RRD`, `LDI`, `CPI`, etc.

T-state-precise cores are substantially more complex to implement but pass the FUSE test suite, Sensible tests, and run essentially all Spectrum software. Modern high-quality cores — MiSTer's Spectrum, ZX-Uno's core, the Harlequin, and the Sizif-512 — are all T-state-precise.

---
## ULA Timing Internals

### The Frame Timing

The Spectrum's video frame is constructed from CPU clock cycles (T-states). The 48K Spectrum's timing is:

- **CPU clock** — 3.5 MHz (actually 3.504690 MHz; one T-state = ~285 ns)
- **Scanline** — 224 T-states (64 µs)
- **Frame** — 311 scanlines (19.9 ms; ~50.08 Hz vertical refresh)
- **Active display** — 192 scanlines of 256 pixels each, with 32-character left border, 32-character right border
- **Vertical blank** — the remaining scanlines (top border 64, bottom border 56, VSync pulse within bottom border)

The 128K Spectrums have slightly different frame timing (with a longer top border and shorter bottom border) and use a contention scheme that differs in detail. The Pentagon has its own frame layout (largely because of its different clock-divider logic).

Reproducing these values exactly in the FPGA's video counter is the foundation of cycle-exact timing.

### Contended Memory Pattern

The ULA shares the DRAM between CPU and video fetches. During the active display area, the ULA needs to fetch:

- **Pixel byte** + **attribute byte** every 8 pixel positions (every 4 CPU T-states)
- That is **2 bytes every 4 T-states**, or one byte per 2 T-states during the active portion of each scanline

To accomplish this without halting the CPU entirely, the ULA uses a clever asymmetric arbitration:

- **T1 of each 4-cycle "pixel character"** — ULA fetches pixel byte; CPU may be held
- **T2** — ULA fetches attribute byte; CPU may be held
- **T3** — CPU has free access (no contention)
- **T4** — CPU has free access (no contention)

But the actual pattern is more nuanced: the WAIT signal is asserted based on a **specific timing schedule**, not uniformly. The pattern depends on:

- Whether the access is to contended memory (`#4000`–`#7FFF` in 48K)
- The position within the current 4-T-state character cycle
- The screen position (some scanlines have slightly different contention)

Chris Smith's book documents the exact pattern, which is reproduced in the FPGA core via a small state machine that drives the WAIT_n signal synchronously with the video counter.

### Implementation: The Contention State Machine

A typical FPGA contention implementation includes:

1. **Video position counter** — tracks current scanline and pixel position
2. **Contention window detector** — asserts an internal `in_contention` signal during the active display period (or specific sub-portions)
3. **WAIT pattern generator** — a small state machine that drives `WAIT_n` according to the documented contention pattern, synchronized to the CPU's T-state counter
4. **Address range check** — only assert WAIT when the CPU is actually accessing contended memory (`A[15] = 0` and `A[14] = 1` for the 48K; similar logic for 128K's contended pages)

A simplified Verilog sketch:

```verilog
// Simplified contention logic
wire is_contended_addr = (cpu_addr >= 16'h4000) && (cpu_addr <= 16'h7FFF);
wire in_active_display = (v_count >= 8'd64) && (v_count < 8'd256);
wire contention_cycle = in_active_display && is_contended_addr;

// The actual pattern is driven by a small state machine that asserts
// wait_n at specific T-state offsets within each 4-cycle character
assign wait_n = ~(contention_cycle && contention_pattern_strobe);
```

The `contention_pattern_strobe` is the complex part — it's a small lookup or counter-based waveform that produces the exact contention pattern per scanline.

### Floating Bus

The "floating bus" is one of the most distinctive Spectrum timing features. When the CPU reads from port `#FF` (the keyboard/MIC port) during specific cycles, instead of reading the keyboard, it reads **whatever byte the ULA is currently fetching from video memory**. This happens because the ULA's video data is left on the shared bus during specific cycles.

The floating bus's exact behavior:

- Returns valid video bytes only during specific cycles (when the ULA is performing a video fetch)
- Returns `#FF` (or random / last value) during other cycles
- The exact cycle offsets and the byte returned depend on the scanline position

Reproducing this in FPGA requires routing the ULA's internal video fetch data onto the CPU data bus at the right cycles. The Harlequin and Sizif-512 cores implement this exactly; many software emulators approximate it (or omit it entirely, breaking some software).

### INT Timing

The ULA asserts INT every 20 ms (50 Hz) at a specific scanline — line 64 of the 48K frame (the start of the top of the active display). The CPU responds to INT after the current instruction completes (variable latency of 4–13 T-states depending on the instruction).

The exact INT-to-CPU-response relationship matters for software that uses `HALT` to wait for the next interrupt and then counts cycles to position itself on a specific scanline. An FPGA core must assert INT at the exact T-state and must not add any extra latency beyond what the real Z80's interrupt response provides.

### Memory Banking Timing (128K)

On the 128K / +2 / +3 Spectrums, the contended memory range changes depending on which RAM page is banked into `#4000`–`#7FFF`. Only certain pages are contended (page 5 in the original 128K layout), while others are uncontended. The FPGA core must track the current banking register and apply contention only to the appropriate pages.

---
## Common Pitfalls

Achieving T-state precision requires care. Common pitfalls that cause cores to be "almost but not quite" cycle-exact include:

### PLL Jitter

The FPGA's PLL (Phase-Locked Loop) generates the 3.5 MHz CPU clock from a higher-frequency reference (e.g., 50 MHz on the DE10-Nano). PLLs have inherent **phase jitter** — small variations in the output clock's timing relative to the ideal period.

For most FPGA applications, PLL jitter is negligible. But for cycle-exact Spectrum timing, jitter can cause:

- INT assertion timing drift across frames
- Pixel clock jitter that affects HDMI/video output stability
- Bus arbitration races if the WAIT_n signal timing is sensitive to PLL phase

Mitigation: use a PLL with low jitter specification, or derive the CPU clock directly from a crystal oscillator rather than a PLL. Some cores use **dual-clock designs** (one for video, one for CPU) but these add complexity.

### Asynchronous Clock Domains

If the FPGA core uses multiple clocks (e.g., a 28 MHz video clock divided down to 3.5 MHz, plus a separate 50 MHz clock for HDMI output), then signals crossing between clock domains need **synchronization**. Improper synchronization causes:

- Metastability (signals in an indeterminate state for one or more cycles)
- Glitches on critical signals (INT, WAIT_n)
- Intermittent failures that depend on temperature, voltage, or PLL phase

Mitigation: use proper two-flop synchronisers for cross-domain signals, or design the entire core to run from a single master clock divided down internally.

### Bus Arbitration Races

The CPU/video memory arbitration is a critical race condition. If the WAIT_n signal is asserted at the wrong cycle relative to the CPU's bus cycle, the CPU can:

- Latch incorrect data (read or write the wrong byte)
- Miss the WAIT (continue executing when it should be held)
- Enter a deadlock state (permanently held)

Mitigation: carefully design the arbitration logic to assert WAIT_n early enough for the CPU's bus cycle setup, and to release it at the right cycle. The T80 documentation specifies the WAIT_n setup/hold timing requirements precisely.

### Banking / Memory Map Errors

On the 128K / +2 / +3 Spectrums, the memory banking is non-trivial. Errors in the banking register handling can cause:

- Wrong page banked into a window
- Contention applied to the wrong page
- ROM page selection errors

Mitigation: exhaustive testing of all banking combinations, using both commercial software and dedicated banking test ROMs.

### Undocumented Z80 Behavior

The Z80 has several undocumented but well-known instructions and behaviors:

- **`SLL (HL)`** and variants — shift-left-logical with a 1 shifted in (different from `SLA`)
- **`LD A,I` / `LD A,R` flags** — these instructions set the parity/overflow flag to the value of IFF2, which software can use to detect interrupts
- **`LD A,B` after `LDI/CPI/INI`** — partially decoded flags
- **`OUT (C),0`** — on NMOS Z80, writes 0; on CMOS Z80, writes #FF (this affects some software)

The T80 core reproduces these correctly, but custom Z80 implementations may not. If a core uses a non-T80 Z80, it must verify these behaviors match a real NMOS Z80.

---

## Verification Methods

A core claimed to be cycle-exact must be **verified** against real hardware. Several verification methods are used:

### Test Programs

Standard test programs that exercise specific timing behaviors:

- **FUSE test suite** — the emulator's reference test ROMs, covering Z80 instruction timing, contention patterns, INT timing, video timing. A core that passes FUSE tests matches real hardware on the tested behaviors.
- **Sensible tests** (by Andrew Owen) — focused tests for floating bus behavior and contention patterns
- **ZEXALL / ZEXDOC** — exhaustive Z80 instruction tests covering every opcode including undocumented ones
- **Pentagon Diag ROM** — diagnostic ROM for Russian Pentagon clones, testing memory, video, sound, disk
- **Float Spell** — a multicolor demo that produces visible errors if the contention pattern is off by even one T-state

Running these in the core's simulation (via test bench) and on the actual FPGA hardware confirms cycle-exact behavior.

### Oscilloscope / Logic Analyser Comparison

The definitive verification: connect logic analysers or oscilloscopes to both a real Spectrum and the FPGA core, and compare:

- **HSYNC / VSYNC timing** — exact cycles of horizontal and vertical sync pulses
- **WAIT_n signal waveform** — the exact pattern of WAIT assertions on each scanline
- **INT pulse timing** — exact cycles of INT assertion
- **CPU bus signals** — M1, MREQ, RD, WR timing relationships

Any difference between the real hardware and the FPGA reveals a timing bug.

### Software Compatibility Testing

Running a large corpus of real Spectrum software and checking for visual/audio glitches:

- **Commercial games** — especially those with copy protection (Speedlock, Alkatraz, Latenite)
- **Demoscene productions** — multicolor demos (e.g., **BIFTRO**, **Refresh**, **_NUMBERS_**, **Eye of the Lizard**), raster effects, sync-scrollers demos
- **System software** — TR-DOS, 128K BASIC, etc.
- **Peripheral-using software** — Beta 128 disk software, +3 DOS, AY music players

Any visual glitch, crash, or protection failure indicates a timing discrepancy.

### Frame-Accurate Visual Diffing

For video timing, the most sensitive test is to capture the exact pixel-by-pixel output of both real hardware and the FPGA core, and diff them. Differences as small as one pixel reveal timing errors. This is usually done by capturing composite video with a frame grabber and comparing frame buffers.

---
## Timing Accuracy Across Implementations

Different Spectrum implementations achieve different levels of timing accuracy:

| Implementation | Approach | Cycle-Exact? | FUSE Tests | Demoscene Multicolor | Copy Protection |
|---|---|---|---|---|---|
| **Real Spectrum (48K/128K)** | Original hardware | ✅ Reference | ✅ | ✅ | ✅ |
| **MiSTer Spectrum core** | T80 + cycle-exact ULA | ✅ | ✅ | ✅ | ✅ |
| **ZX-Uno core** | T80 + cycle-exact ULA | ✅ | ✅ | ✅ | ✅ |
| **Harlequin** | T80 + ULA recreation (Smith's book) | ✅ | ✅ | ✅ | ✅ |
| **Sizif-512** | T80 + ULA recreation | ✅ | ✅ | ✅ | ✅ |
| **ZX Evolution BaseConf** | Real Z80 + CPLD (Pentagon timing) | ✅ (Pentagon) | ✅ | ✅ (Pentagon demos) | ✅ |
| **ZX Spectrum Next (FPGA)** | Hardware acceleration (less timing-sensitive) | Approximate | Mostly | Partial | Mostly |
| **Fuse (software emulator)** | T-state simulation | ✅ | ✅ (reference) | ✅ | ✅ |
| **ZEsarUX (software emulator)** | T-state simulation | ✅ | ✅ | ✅ | ✅ |
| **CSpect (Next emulator)** | Scanline-precise | Partial | Partial | Partial | Partial |
| **UnrealSpeccy (software)** | T-state simulation | ✅ | ✅ | ✅ | ✅ |
| **Older emulators (x128, etc.)** | Scanline-precise | Partial | Partial | ❌ | ❌ |

Key observations:

- **All modern high-quality FPGA cores are cycle-exact** — MiSTer, ZX-Uno, Harlequin, Sizif-512, and ZX Evolution all achieve T-state precision
- **High-quality software emulators are also cycle-exact** — Fuse, ZEsarUX, and UnrealSpeccy simulate every T-state in software. Their limitation is host CPU speed (real-time only on modern hardware), not timing precision
- **The ZX Spectrum Next is intentionally less timing-sensitive** — its hardware features (hardware sprites, tilemap, layer 2, copper) make cycle-exact CPU/video contention less critical, so the Next's FPGA implementation can be scanline-precise without breaking software
- **CSpect (Next emulator) is scanline-precise** — appropriate for Next software, but cannot run classic 48K timing-sensitive demos perfectly

---

## FAQ

**Q: My FPGA core passes all FUSE tests but some demos still glitch. Why?**

A: The FUSE tests cover the *commonly tested* timing behaviors, but some demos probe edge cases that the tests don't exercise. Examples: very specific contention patterns on specific scanlines, floating bus behavior during border area, or interactions between contention and `HALT`. The only complete verification is running a large corpus of real software and visual diffing.

**Q: Do I need a real Spectrum for verification?**

A: Not strictly — high-quality software emulators (Fuse) are themselves verified against real hardware and can serve as a reference. But for ultimate fidelity, a real Spectrum captured via oscilloscope is the gold standard. Most core developers do not have this equipment; they rely on the FUSE tests + demoscene compatibility.

**Q: Why does my core run commercial games but crash on copy-protected ones?**

A: Copy protection (Speedlock, Alkatraz) measures contention patterns or specific instruction latencies that vary subtly between implementations. A 1-cycle error in contention is invisible in normal software but detected by protection. Diagnose by running the Sensible tests, which exercise these edge cases specifically.

**Q: Does T-state precision matter for the Pentagon?**

A: Yes, but the Pentagon's timing is *different* from the original Spectrum's (different scanline length, frame layout, contention pattern). For Pentagon compatibility (Russian software), the core must reproduce the *Pentagon's* specific timing, not the Sinclair's. The ZX Evolution does this exactly because it's a Pentagon successor.

**Q: Can I use T80n instead of T80?**

A: T80n is a variant with some improvements (better undocumented instruction handling, smaller area). It's used by several modern cores. Verify it passes ZEXALL before deploying.

**Q: How do I handle the 128K's different contention?**

A: The 128K Spectrums have a different contention scheme from the 48K — only certain RAM pages are contended, and the contention pattern differs in detail. Implement a banking-aware contention detector that applies contention only to the contended pages (page 5 in 128K, plus additional pages in +2A/+3 depending on the special banking mode).

**Q: What's the impact of FPGA device family on timing precision?**

A: Minimal at 3.5 MHz — any modern FPGA can run a Spectrum core at this speed with plenty of timing margin. At 14 MHz turbo or for the Next's higher-resolution video modes, device speed grade matters more. Cyclone IV, Cyclone V, and Spartan-6 all have ample performance for Spectrum-class cores.

**Q: Why does my core work in simulation but glitch on hardware?**

A: This is the classic sim-vs-hardware gap. Causes: PLL jitter, asynchronous signal crossings, timing violations not modeled in simulation, or RTL that synthesises differently than expected. Use static timing analysis (STA) to confirm the synthesized design meets timing at the target clock, and verify with on-hardware logic analyser (e.g., Altera SignalTap, Xilinx ChipScope).

---

## Summary

Cycle-exact timing is the defining quality metric for a Spectrum FPGA core. Achieving it requires:

1. **T80 or equivalent cycle-accurate Z80** — including undocumented instructions and flags
2. **ULA recreation** with the exact contention pattern, floating bus behavior, INT timing, and video address generation documented in Chris Smith's *The ZX Spectrum ULA* book
3. **Careful handling of clock domains, PLL jitter, and bus arbitration** to avoid subtle race conditions
4. **Comprehensive verification** via FUSE tests, Sensible tests, ZEXALL, software compatibility, and ideally oscilloscope comparison with real hardware

Modern high-quality cores — MiSTer, ZX-Uno, Harlequin, Sizif-512, ZX Evolution — all achieve T-state precision, passing all standard tests and running essentially all Spectrum software, including demoscene productions that probe the hardware's timing edge cases. This is what makes them indistinguishable from real hardware in practice, and what justifies the FPGA approach over software emulation for users who demand maximum fidelity.

---

## References

- **[Chris Smith**, *The ZX Spectrum ULA](http://www.zxdesign.info/): How to Design a Microcomputer* (2010) — the definitive reference on ULA timing, contention patterns, and video signal generation
- **T80 Verilog Z80 core** — OpenCores / GitHub (Daniel Wallner and contributors)
- [Zilog Z84C00 Z80 CPU Product Specification](https://www.zilog.com/docs/z80/um0080.pdf) — official datasheet with instruction timing
- **MiSTer Spectrum core** — GitHub (sorgelig) — reference T-state-precise implementation
- [ZX-Uno Verilog core](https://github.com/zxdos/zx-uno) — GitHub (Antonio Villena) — open-source cycle-exact core
- **Harlequin project** — Chris Smith's project pages
- **Sizif-512** — GitHub (Victor Trucco) — open-source drop-in core
- [FUSE emulator test suite](https://fuse-emulator.sourceforge.net/) — the standard test ROMs for Z80 and ULA timing verification
- **Sensible tests** — Andrew Owen's floating bus / contention tests
- [World of Spectrum forums](https://worldofspectrum.org/) — discussions of timing edge cases and software compatibility
- **The Demoscene timing tests** — Float Spell, BIFTRO, and other multicolor demos used as integration tests

## Cross-references

- [FPGA Implementation](fpga_implementation.md) — the broader process of building a Spectrum FPGA core
- [MiST/MiSTer](mist_mister_core.md) — T-state-precise implementation
- [ZX-Uno](zx_uno_core.md) — T-state-precise single-board FPGA
- [ZX Evolution](zxevo.md) — Pentagon-precise hybrid design
- [Harlequin / Sizif](harlequin_sizif.md) — ULA recreation based on Smith's reverse engineering
- [Emulator Comparison](../software/emulator_comparison.md) — software emulator timing fidelity
- [Test Suites](../software/test_suites.md) — FUSE / Sensible / ZEXALL test ROMs
