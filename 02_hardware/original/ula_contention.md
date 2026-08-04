[← Home](../../README.md) · [Original Hardware](README.md)

# ULA Contention — The Hardware Story Across All Spectrum Models

**Memory contention** is the most consequential hardware design choice in the ZX Spectrum's history. It defines how every timing-sensitive program on the platform behaves, it forces every emulator and FPGA core to model a subtle per-T-state delay, and it is the **single biggest difference between the Sinclair-designed Spectrums (16K/48K/128K/+2) and the Amstrad-redesigned ones (+2A/+3)**.

This article tells the **hardware story**: why contention exists at the electrical level, how the Ferranti ULA implements it, why the Sinclair 8K5/7K0 gate array inherited the same model, and why Amstrad's 40084/40085 ASIC changed it. For the **per-T-state delay tables and per-instruction cycle costs**, see [contention_timing.md](../../05_development/05_display_and_timing/contention_timing.md). For the **developer-facing model** (which ranges are contended, how to write contention-aware code), see [contention_model.md](../../05_development/03_memory_and_io/contention_model.md).

> [!NOTE]
> This article is **hardware-perspective** and complementary to the developer references. If you only need to know *"when I access `#4000` during the paper area, how many T-states does my LD cost?"*, go to [contention_timing.md](../../05_development/05_display_and_timing/contention_timing.md). If you want to understand *"why does the 128K contend banks 1, 3, 5, 7 but the +2A/+3 contends banks 4, 5, 6, 7"*, read on.

---

## Why Contention Exists — The Cost Decision

The ZX Spectrum was designed in 1981–1982 to a **£50 BOM target** for the 16K model and **£100 for the 48K**. Two architectural decisions, both made by Sinclair engineer Richard Altwasser, created contention as an unavoidable consequence:

1. **No dedicated video RAM** — the screen is stored in main DRAM, shared with the CPU.
2. **No dual-ported DRAM** — DRAM chips of the era could only serve one master at a time, so the CPU and ULA must time-share access.

The alternative — used by the Commodore 64 (VIC-II has its own dedicated SRAM) and BBC Micro (6845 CRTC with proper bus arbitration) — was significantly more expensive. Altwasser's cost-driven decision was:

> *Let the ULA always win.* Whenever the ULA needs to read screen bytes, it asserts the CPU's `/WAIT` pin. The CPU stalls until the ULA finishes its read. The CPU is none the wiser — it just sees a slower memory access.

This is the entire mechanism of contention: **the ULA asserts `/WAIT` to pause the CPU for a few T-states while the ULA takes its turn with the shared DRAM**. The complexity is not in the *mechanism* but in the *timing*: the ULA's video fetch cadence determines exactly when and for how long `/WAIT` is asserted, and that cadence is what every contention-aware program must model.

---

## The DRAM Electrical Foundation

To understand why the contention pattern is `(6, 5, 4, 3, 2, 1, 0, 0)` on the 48K — and why the +2A/+3's pattern is `(1, 0, 7, 6, 5, 4, 3, 2)` — you need to look at the DRAM chip's electrical interface and the ULA's video fetch cadence.

### Multiplexed Address DRAM

The 48K's upper RAM uses **4116 DRAM** chips (16 Kbit × 1 bit each, 8 chips per byte). Each 4116 has a **14-bit address** but only **7 address pins** — the address is presented in two phases via a technique called **address multiplexing**:

```
DRAM access sequence (4116):

  Phase 1 (RAS):  Place row address (A6-A0) on the 7 address pins
                  Assert /RAS (Row Address Strobe) low
                  → DRAM latches the row internally

  Phase 2 (CAS):  Place column address (A13-A7) on the same 7 pins
                  Assert /CAS (Column Address Strobe) low
                  → DRAM latches the column, outputs the data byte
```

A complete DRAM access therefore takes **two address phases** plus internal cell access time. The 4116 datasheet specifies roughly **200 ns** for a full read at the access time the Spectrum uses.

### ULA Paged-Mode Reads

To generate one scanline of display, the ULA must fetch:

- **32 bytes of pixels** (256 pixels ÷ 8 pixels per byte) — from `#4000–#401F` for the top row
- **32 bytes of attributes** (32 cells × 1 byte each) — from `#5800–#581F` for the top row

Total: **64 bytes per scanline** of screen data, fetched while the beam traces from the left edge of the paper to the right edge.

The ULA exploits a 4116 feature called **"paged mode"** (sometimes called "half-page mode"): once the row address is latched by `/RAS`, **multiple column reads from the same row** can be performed by toggling `/CAS` without re-asserting `/RAS`. The row address setup time (~100 ns) is amortised over many column accesses (~80 ns each).

The ULA's per-byte fetch cadence during the paper area:

```
T-state offset within 8-T slot:   0   1   2   3   4   5   6   7
                                  │   │   │   │   │   │   │   │
ULA action:                      RAS  CAS  ...  ...  RAS  CAS ...
                                 (pixel byte)         (attr byte)
```

In each **8-T-state window**, the ULA fetches **2 bytes**: one pixel byte and one attribute byte (both for the same screen column). The pattern repeats 16 times per scanline, producing 32 pixel bytes + 32 attribute bytes = 64 bytes total per scanline.

### Where the 6-5-4-3-2-1-0-0 Pattern Comes From

The `/WAIT` pattern is the ULA's defense against the CPU disrupting its paged-mode read sequence. If the CPU initiates a memory access **while `/RAS` is being driven by the ULA**, the ULA must:

1. Finish its current DRAM access (can't abort mid-RAS without corrupting video)
2. Yield the address bus to the CPU
3. Let the CPU perform its access
4. Re-establish its own RAS/CAS for the next video fetch

The worst case is a CPU access that arrives **just as the ULA is about to assert `/RAS`** — the ULA has to push back the CPU by up to 6 T-states to complete its current fetch cycle. The delay decreases as the CPU arrives later in the window, because the ULA has less remaining work to finish:

| CPU arrives at T-offset | ULA's remaining work | Delay imposed |
|---|---|---|
| 0 (start of window) | Full RAS+CAS for 2 bytes | **6T** (worst case) |
| 1 | Most of RAS+CAS remaining | **5T** |
| 2 | About half remaining | **4T** |
| 3 | Less than half | **3T** |
| 4 | Just finishing second byte | **2T** |
| 5 | Nearly done | **1T** |
| 6 | ULA idle (between fetches) | **0T** |
| 7 | ULA idle | **0T** |

This is the famous `(6, 5, 4, 3, 2, 1, 0, 0)` pattern. It is **not arbitrary** — it is the minimum delay the ULA must impose to protect its video fetch, given the DRAM chip's electrical characteristics.

---

## The 48K Contention Model — Address-Based

The 48K uses **address-based contention**: any access to addresses `#4000–#7FFF` (the upper 16 KB of RAM) is contended. There is no concept of "banks" because the 48K has only one 16 KB block of contended RAM — the screen memory plus the 8 KB of upper RAM immediately above it.

### Why the Range Is `#4000–#7FFF` (Not Just the Screen)

The 48K's screen memory is at `#4000–#5AFF` (pixel file `#4000–#57FF`, attribute file `#5800–#5AFF`). But the contended range extends to `#7FFF` — covering nearly 2.5 KB of RAM that is **not** screen memory (`#5B00–#7FFF`).

The reason is electrical: the **4116 DRAM chips that hold the screen also hold the upper RAM**. The 48K's upper 16 KB is built from **two banks of 8 × 4116 chips** — one bank for `#4000–#5FFF`, another for `#6000–#7FFF`. These banks share `/RAS` and `/CAS` lines with the ULA, because the ULA needs to address them when fetching screen bytes. Even though the ULA only reads `#4000–#5AFF`, the entire 16 KB of upper RAM is on the ULA's address bus, so any CPU access to any of it can collide with the ULA's RAS/CAS sequencing.

### Why I/O Accesses Are Also Contended

The 48K's ULA contends **any access whose address bits fall in the contended range**, regardless of whether it is a memory access (`/MREQ`) or an I/O access (`/IORQ`). This means `OUT (#FE), A` — the border/sound port — is contended if the address bus happens to have bit 14 set (which it almost always does during the paper area, because the program counter is in screen memory).

This was a **simplification** in the ULA's design: rather than separately decode `/MREQ` vs `/IORQ`, the ULA keys on the address bits alone. It cost the platform a small amount of `OUT` instruction time but simplified the gate count. This decision has consequences decades later: every multicolor effect that uses `OUT (#FE), A` is implicitly contended on the 48K/128K/+2.

---

## The 128K / +2 Contention Model — Bank-Based

The 128K introduces **128 KB of bank-switched RAM**, organized as **8 banks of 16 KB**. The decision about which banks should be contended was a clean-slate design question — and Sinclair's engineers chose to contend banks **1, 3, 5, 7** (the odd-numbered banks).

### Why Banks 1, 3, 5, 7?

The 128K's 128 KB of DRAM is physically organized as **two 64 KB blocks**:

- **Block A** ("uncontended") = banks **0, 2, 4, 6** — uses one set of DRAM chips
- **Block B** ("contended") = banks **1, 3, 5, 7** — uses a different set of DRAM chips, shared with the ULA's video circuitry

Bank 5 (which holds the visible screen, paged at `#4000`–`#7FFF`) and bank 7 (the shadow screen) are by necessity in the contended block, because the ULA reads them for video. Banks 1 and 3 are in the contended block as a consequence of the chip organization: 4 banks × 16 KB = 64 KB per DRAM chip set, and Sinclair filled out the chip set with two extra banks rather than leave the silicon unused.

The pattern is preserved in the +2 unchanged — the +2 uses the same Sinclair 8K5/7K0 gate array and the same DRAM organization, so its contention model is identical.

### Why the 128K Pattern Starts at T=14361 (Not T=14335)

The 128K's scanline is **228 T-states** long (vs 224 on the 48K). This 4-T-state difference exists because the 128K's ULA fetches screen bytes slightly more slowly than the 48K's ULA — a design choice that gives the 128K DRAM chips more recovery time between accesses (allowing cheaper, lower-spec chips to be used).

The 128K has 311 scanlines per frame (vs 312 on the 48K), so the paper area starts one scanline earlier than the 48K. The net effect: contention starts at T=14361 on the 128K, vs T=14335 on the 48K — a shift of **+26 T-states** that breaks 48K→128K porting of cycle-exact effects.

### The Contention Pattern Is Unchanged

The 128K/+2 inherits the **same contention delay pattern** as the 48K: `(6, 5, 4, 3, 2, 1, 0, 0)` repeating every 8 T-states. The 7K0 gate array does not change the ULA's per-cell timing; it only adds the bank-decode logic that decides *whether* a given access is contended. From the CPU's perspective, an access to a contended bank on the 128K experiences the same delay progression as an access to `#4000`–`#7FFF` on the 48K.

This is **important for emulator authors**: the contention delay lookup table is identical for all Ferranti-ULA Spectrums (48K, 128K, +2). Only the address-range check (which banks are contended) and the start-T-state value (T=14361 for 128K vs T=14335 for 48K) differ between the models.

The 4 extra T-states per scanline on the 128K (228 vs 224) are absorbed by **more non-contention time at the end of each scanline** — they do not affect the per-cell contention pattern. This is why 48K multicolor effects can in principle be ported to the 128K by adjusting only the start-of-frame T-state count, without recalculating per-instruction delay tables.

---

## The +2A/+3 Contention Model — Amstrad ASIC Redesign

The +2A and +3 replace the Sinclair 8K5/7K0 gate array with a pair of Amstrad-designed ASICs (**40084** for video/banking/contention, **40085** for disk/special paging). The contention model is **fundamentally redesigned** — not a refinement of the Sinclair design, but a clean-sheet reimplementation with different bank selection, different gating, and a different delay pattern.

### Why Banks 4, 5, 6, 7?

The +2A/+3 organizes its 128 KB of DRAM as **two 64 KB blocks**, but **different from the 128K/+2's split**:

- **Low block** ("uncontended") = banks **0, 1, 2, 3** — own DRAM chip set
- **High block** ("contended") = banks **4, 5, 6, 7** — own DRAM chip set, shared with the video circuitry

This is the most natural grouping: the contended banks are the high-numbered banks (4–7), all in one DRAM chip set. The Amstrad ASIC's address decoder just looks at bit 14 of the bank number (banks ≥ 4 = high block = contended).

The Sinclair 128K's grouping (banks 1, 3, 5, 7) was a quirk of the Sinclair gate array's interleaved DRAM organization. Amstrad's redesign grouped the contended banks contiguously for simpler decoding — a side effect of integrating more logic into the ASIC.

### Why MREQ Gating?

The most consequential Amstrad change is **MREQ gating**: contention is only applied when the CPU asserts `/MREQ` (memory request). I/O accesses (`/IORQ`) **never trigger contention**, even if the address bits match a contended bank.

The Sinclair/Ferranti design applied contention based on **address bits alone** — it did not distinguish `/MREQ` from `/IORQ`. The Amstrad ASIC adds this distinction.

The effect:

| Instruction | 48K / 128K / +2 | +2A / +3 |
|---|---|---|
| `LD A, (HL)` with HL in contended bank | Contended | Contended |
| `OUT (#FE), A` from contended address | **Contended** (because PC bits match) | **Uncontended** (no MREQ) |
| `OUT (#BFFD), A` (AY register write) | **Contended** if PC in contended bank | **Uncontended** |
| `IN A, (#FE)` from contended address | Contended | Uncontended |

This is the source of most 128K→+2A/+3 timing incompatibilities. Demoscene productions that depend on the cycle count of `OUT (#FE), A` (the standard multicolor instruction) for cycle-exact timing **must have separate code paths** for Sinclair vs Amstrad machines.

### Why the Pattern Shifted to `(1, 0, 7, 6, 5, 4, 3, 2)`

The Amstrad ASIC's delay pattern is the same eight values as the Sinclair pattern, but **rotated** so that the worst-case delay is at T-state offset 2 instead of offset 0:

```
Ferranti / Sinclair 8K5/7K0 (48K, 128K, +2):
  T-offset:  0  1  2  3  4  5  6  7
  Delay:     6  5  4  3  2  1  0  0
                              ↑↑
                         Free T-states

Amstrad 40084 (+2A, +3):
  T-offset:  0  1  2  3  4  5  6  7
  Delay:     1  0  7  6  5  4  3  2
             ↑↑              ↑
        Free T-states   Worst-case (7T)
```

The pattern is rotated because the Amstrad ASIC's video-fetch phase is shifted relative to the contention window's T-state 0. The Amstrad ASIC's internal RAS/CAS sequencing starts 2 T-states later in the window than the Sinclair ULA's — so the peak-delay T-state is offset 2 instead of offset 0.

The total contention **budget** per window is the same (28 T-states of delay distributed across 8 cells), but the per-T-state distribution is different. Code that was hand-tuned for the Ferranti pattern will hit the worst-case delay at the wrong T-state on the +2A/+3.

### The 100-T-state Free Gap at Frame Start

The +2A/+3 has one more quirk: **contention does not start at the very first contended scanline**. There is a **100 T-state free gap** between the start of the contention period (T=14361) and the actual resumption of contention activity (T=14589).

During this 100 T-state window, code can access contended banks with **zero contention delay**. This is a side effect of the Amstrad ASIC's startup sequence: it takes ~100 T-states for the video-fetch pipeline to stabilise after the paper area begins.

This gap is not present on the 48K, 128K, or +2. Emulators must model it for cycle-exact +2A/+3 reproduction.

---

## The Full Per-Model Comparison

| Parameter | 16K/48K | 128K | +2 grey | **+2A** | **+3** |
|---|---|---|---|---|---|
| **Gate array** | Ferranti ULA (5C/6C/7C) | Sinclair 8K5/7K0 | Sinclair 8K5/7K0 | **Amstrad 40084/40085** | **Amstrad 40084/40085** |
| **Contended range** | `#4000`–`#7FFF` (address) | Banks 1, 3, 5, 7 | Banks 1, 3, 5, 7 | **Banks 4, 5, 6, 7** | **Banks 4, 5, 6, 7** |
| **Contention cell** | 8 T-states | 8 T-states | 8 T-states | 8 T-states | 8 T-states |
| **Delay pattern** | `(6,5,4,3,2,1,0,0)` | `(6,5,4,3,2,1,0,0)` | `(6,5,4,3,2,1,0,0)` | **`(1,0,7,6,5,4,3,2)`** | **`(1,0,7,6,5,4,3,2)`** |
| **Worst-case delay** | 6T | 6T | 6T | **7T** | **7T** |
| **Gating** | Address bits only | Address bits only | Address bits only | **MREQ only** | **MREQ only** |
| **`OUT` contended?** | Yes (if A0=0 and PC in range) | Yes | Yes | **No** | **No** |
| **Scanline** | 224 T-states | 228 T-states | 228 T-states | 228 T-states | 228 T-states |
| **Pattern starts at T** | 14335 | 14361 | 14361 | 14361 | 14361 |
| **Free gap at start** | — | — | — | **100 T (resumes 14589)** | **100 T (resumes 14589)** |
| **Contention scanlines** | 64–255 | 63–254 | 63–254 | 63–254 | 63–254 |
| **Frame rate** | 50.08 Hz | 49.89 Hz | 49.89 Hz | 49.89 Hz | 49.89 Hz |
| **Early/late drift** | Yes (thermal) | Yes (thermal) | Yes (thermal) | **No** | **No** |
| **Snow effect (RFSH bug)** | Yes | No (ULA fixed) | No (ULA fixed) | No | No |

---

## Implications for Emulators and FPGA Cores

Accurate contention emulation is **the make-or-break feature** of a credible ZX Spectrum emulator. Several long-standing emulators got the +2A/+3 contention wrong for over a decade before hardware-based measurements (particularly by Ramsoft and the SpeccyWiki community) settled the canonical values.

### Required Behaviors

A cycle-exact emulator or FPGA core must implement:

1. **Per-T-state delay lookup** — not per-instruction. An instruction that spans multiple T-states may be contended on some accesses and not others. The contention check must happen on **every memory-accessing T-state**, with the delay depending on the T-state's position in the scanline.

2. **Per-model contended-range check** — the same address can be contended on one model and uncontended on another. The bank-number-to-physical-DRAM mapping must be modeled correctly (especially for the 128K/+2's odd-bank scheme and the +2A/+3's high-bank scheme).

3. **MREQ vs IORQ distinction on +2A/+3** — emulators that don't track the bus cycle type will incorrectly apply contention to `OUT` instructions on the +2A/+3.

4. **The 100 T-state gap** on +2A/+3 — applies to the first scanline of contention only.

5. **Early vs late timing on Ferranti models** — configurable toggle for the +1 T-state drift caused by thermal behavior. Defaults to "early" (cold machine) for compatibility.

6. **The snow effect on 48K only** — `/RFSH` collision with `/RAS` corrupts the DRAM row address; see [ula_timing.md](ula_timing.md) for implementation notes.

### Common Emulator Bugs

- **Applying the Ferranti pattern to the +2A/+3** — produces subtly wrong timing for cycle-exact demos. Fixed in modern Fuse, ZEsarUX, and CSpect, but still present in some older emulators.
- **Treating I/O as contended on +2A/+3** — results in `OUT (#FE), A` taking too long, breaking multicolor effects that depend on cycle counting.
- **Missing the 100 T-state gap** — minor effect, but visible in cycle-exact demos that run during the first contended scanline.
- **Not modeling early/late timing** — demoscene productions may pass on emulator but fail on cold real hardware.

For an in-depth treatment of accurate contention modeling, see [fpga_timing_accuracy.md](../../11_emulation/fpga/fpga_timing_accuracy.md) and [mcu_ula.md](../../11_emulation/mcu/mcu_ula.md).

---

## Detecting the Hardware Model from Software

Because the contention model varies across models, demoscene and game code often needs to **detect the host machine** at startup and switch to the appropriate code path. The classic technique:

```z80
; Detect 48K vs 128K/+2/+2A/+3 by reading the paging register
LD   BC,#7FFD
IN   A,(C)             ; On 48K, this returns floating-bus junk
                         ; On 128K/+2/+2A/+3, returns last-written value (often #17)
CP   #17               ; Common ROM default
JR   Z,is_128k_class

; To distinguish 128K/+2 from +2A/+3, time an OUT instruction
; in a contended bank and measure the cycle count
is_128k_class:
LD   B,#FE
LD   A,#0
HALT                   ; Sync to interrupt
LD   A,(contended_addr); Trigger contention (bank 5, contended on both)
; ... precise timing loop ...
; On 128K/+2: OUT cycle count matches contended model
; On +2A/+3: OUT cycle count matches uncontended (MREQ-gated) model
```

For a canonical detection routine, see the World of Spectrum FAQ's "How to detect the machine type" article ([worldofspectrum.org/faq/reference/48kreference.htm](https://worldofspectrum.org/faq/reference/48kreference.htm)). The detection logic is also embedded in most modern demo shells and game loaders.

---

## Cross-References

- [ula_timing.md](ula_timing.md) — frame timing, multicolor constraints, snow effect, early/late timing drift
- [ula_architecture.md](ula_architecture.md) — internal architecture of the Ferranti ULA and Sinclair gate arrays
- [zx_spectrum_16k_48k.md](zx_spectrum_16k_48k.md) — the original Sinclair hardware (the design that established contention)
- [zx_spectrum_128.md](zx_spectrum_128.md) — the 128K, where bank-based contention was introduced
- [zx_spectrum_plus2.md](zx_spectrum_plus2.md) — the +2 grey (same contention as the 128K)
- [zx_spectrum_plus2a_plus3.md](zx_spectrum_plus2a_plus3.md) — the +2A/+3 (where the Amstrad ASIC contention model was introduced)
- [contention_model.md](../../05_development/03_memory_and_io/contention_model.md) — developer-facing unified contention reference
- [contention_timing.md](../../05_development/05_display_and_timing/contention_timing.md) — per-T-state delay tables and per-instruction cycle costs
- [memory_and_io_48k.md](../../05_development/03_memory_and_io/memory_and_io_48k.md) — 48K memory map and I/O ports (programmer view)
- [memory_and_io_128k.md](../../05_development/03_memory_and_io/memory_and_io_128k.md) — 128K/+2 memory map and I/O ports
- [memory_and_io_plus3.md](../../05_development/03_memory_and_io/memory_and_io_plus3.md) — +2A/+3 memory map and I/O ports
- [video_frame_comparison.md](../../05_development/05_display_and_timing/video_frame_comparison.md) — frame timing comparison across all models
- [fpga_timing_accuracy.md](../../11_emulation/fpga/fpga_timing_accuracy.md) — accurate contention modeling in FPGA cores
- [mcu_ula.md](../../11_emulation/mcu/mcu_ula.md) — microcontroller-based ULA replacement timing notes

---

## References

- [Chris Smith, *The ZX Spectrum ULA](http://www.zxdesign.info/): How to Design a Microcomputer* (Eigenbom, 2010) — the definitive hardware reference for the Ferranti ULA's video and contention design, with die-level analysis of the gate layout
- Sinclair Wiki, "Contended memory" ([sinclair.wiki.zxnet.co.uk/wiki/Contended_memory](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_memory)) — canonical per-T-state delay tables and per-model behavior
- [World of Spectrum](https://worldofspectrum.org/), "48K Technical Reference" and "128K Technical Reference" FAQs — frame timing, contention start T-states, and contended bank lists
- Ramsoft, *The Complete ZX Spectrum ROM Disassembly* and the fault-logging ROM test — real-hardware contention measurements used to verify emulator accuracy
- [Fuse emulator](https://fuse-emulator.sourceforge.net/) source (`peripherals/ula.c`, `peripherals/dck.c`, `machines/plus3.c`) — open-source reference implementation of contention for all Sinclair and Amstrad models
- [ZEsarUX](https://github.com/chernandezba/zesarux) source — cycle-exact contention for +2A/+3 including the 100 T-state gap
- [comp.sys.sinclair](https://groups.google.com/g/comp.sys.sinclair) FAQ — historical discussion of when the +2A/+3 contention differences were first documented (mid-1990s)
- The +3E ROM project notes ([Andrew Owen](https://github.com/spectrum-pi/spectranet)) — discussion of how +3 DOS ROM code paths were adjusted for +2A/+3 timing

