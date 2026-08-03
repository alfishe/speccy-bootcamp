[← Home](../README.md) · [References](README.md)

# Timing Reference — ZX Spectrum Cycle-Exact Timing Tables

Every timing number that matters for cycle-exact programming on the ZX Spectrum: CPU clock rates, video frame timings, contentions delay tables, instruction T-state counts, and interrupt timing. For the *concepts* behind contention (why it exists, how the ULA stalls the CPU), see [contention_model.md](../05_development/03_memory_and_io/contention_model.md); this article is the **lookup table** — you come here when you need the exact number of T-states for an access.

> [!NOTE]
> All timing values are in **Z80 T-states** unless otherwise noted. On the 48K Spectrum, one T-state = 286 ns (1 / 3.5 MHz). On the 128K/+2, one T-state = 282 ns (1 / 3.5469 MHz). One video frame = 69,888 T-states on 48K, 70,908 T-states on 128K/+2 — both are exactly 50 Hz (well, 50.08 Hz on 48K, 50.02 Hz on 128K).

---

## CPU Clock Summary

| Model | Clock frequency | T-state duration | T-states per video frame | Frames per second |
|---|---|---|---|---|
| **48K / 16K** | 3.500000 MHz | 285.7 ns | 69,888 | 50.08 |
| **128K / +2 (grey)** | 3.546900 MHz | 281.9 ns | 70,908 | 50.02 |
| **+2A / +3** | 3.546900 MHz | 281.9 ns | 70,908 | 50.02 |
| **Pentagon 128** | 3.500000 MHz | 285.7 ns | 71,680 (320×224) | 48.83 |
| **Pentagon 1024** | 3.500000 MHz | 285.7 ns | 71,680 | 48.83 |
| **Scorpion** | 3.500000 MHz (or 7.0 MHz Turbo) | 285.7 ns | 69,888 | 50.08 |
| **ATM Turbo** | 3.5 / 7.0 MHz (selectable) | 285.7 / 142.9 ns | varies by mode | varies |
| **ZX Spectrum Next** | 3.5 / 7 / 14 / 28 MHz (selectable) | 285.7 / 142.9 / 71.4 / 35.7 ns | varies | 50 / 60 Hz |

The ZX Spectrum Next supports multiple clock speeds and refresh rates — the table above lists the 48K-compatible default.

---

## Video Frame Timing — 48K / 16K

The 48K's ULA generates a PAL-standard composite video signal. The frame structure is:

| Component | Count | Per-pixel T-states | Total T-states |
|---|---|---|---|
| Horizontal sync (HSYNC) | — | — | 96 |
| Horizontal back porch | — | — | 48 |
| Active display (left border) | 48 pixels | 4 | 192 |
| Active display (paper) | 256 pixels | 4 | 1024 |
| Active display (right border) | 48 pixels | 4 | 192 |
| Horizontal front porch | — | — | 48 |
| **Total per scanline** | — | — | **224** |

| Component | Count | T-states per scanline | Total T-states |
|---|---|---|---|
| Vertical sync (VSYNC) lines | 8 | 224 | 1,792 |
| Top border lines | 56 | 224 | 12,544 |
| Active display lines | 192 | 224 | 43,008 |
| Bottom border lines | 56 | 224 | 12,544 |
| **Total per frame** | **312** | — | **69,888** |

Frame rate = 3,500,000 / 69,888 = **50.080 Hz**.

### Scanline Raster Positions

The ULA starts each scanline at the **horizontal sync pulse**. Key positions relative to scanline start:

| Position | T-states from scanline start | What is happening |
|---|---|---|
| 0–95 | HSYNC active | Sync pulse |
| 96–143 | Back porch | Black |
| 144–335 | Left border | BORDER color displayed |
| 336–1359 | Paper display | Pixel/attribute fetch |
| 1360–1551 | Right border | BORDER color displayed |
| 1552–1599 | Front porch | Black |
| 1600–1791 | Right border continued | BORDER color displayed (in real-time) |
| 1792–2239 | Horizontal retrace | (some sources count this as part of the front porch) |

The exact start of active display is critical for cycle-exact code (e.g., split-raster effects). The traditional reference is **T-state 1436 from start of scanline** for the first pixel column.

### Vertical Raster Positions

| Scanline | Position |
|---|---|
| 0–7 | VSYNC |
| 8–63 | Top border (56 lines) |
| 64–255 | Paper display (192 lines) |
| 256–311 | Bottom border (56 lines) |

The INT (interrupt) is asserted at **scanline 64**, the start of paper display. This is the canonical sync point for assembly programs.

---

## Memory Contention — 48K Late Timing

When the ULA is reading display RAM (`#4000–#7FFF`) during paper display, it asserts `WAIT_n` to stall the CPU if the CPU tries to access that same range. The contention pattern is **late timing**: each contended access adds 0–6 T-states, depending on where in the ULA cycle the CPU access happens.

### 48K Contention Delay Table

| CPU access T-state (mod 8) | Delay added | Effective T-states |
|---|---|---|
| 0 | +6 | 6 |
| 1 | +5 | 6 |
| 2 | +4 | 6 |
| 3 | +3 | 6 |
| 4 | +2 | 6 |
| 5 | +1 | 6 |
| 6 | +0 | 6 |
| 7 | +0 | 7 |

The contention pattern repeats every 8 T-states. So an opcode that takes 4 T-states and starts on T-state 0 of the cycle takes 4+6=10 T-states if it accesses `#4000–#7FFF`, but only 4 T-states if it accesses uncontended memory (`#8000–#FFFF` or ROM).

### When Contention Is Active

| Range | Contended? |
|---|---|
| `#4000–#7FFF` | **Yes** — during paper display only |
| `#0000–#3FFF` (ROM) | No |
| `#8000–#FFFF` | No |

Paper display = scanlines 64–255, T-states 336–1359 within each scanline. Outside of these windows, the ULA is not touching `#4000–#7FFF` and access is uncontended.

### 48K Floating Bus

Reading port `#FF` (or any port where `A0=1` and no peripheral decodes the address) returns **whatever the ULA is fetching** during contention. This is the **floating bus** — used to detect the current raster position without hardware timers. The byte returned is:

- During paper display: the next display byte the ULA will fetch (pixel or attribute)
- Outside paper display: `#FF`

The floating bus is **not** reliable for cycle-exact timing — it has its own quirks and is best used for coarse position detection. See [floating_bus.md](../05_development/05_display_and_timing/floating_bus.md) for details.

---

## Memory Contention — 128K / +2 / +2A / +3

The 128K and later models have a **different contention scheme** because the ULA's behavior changed (and the +2A/+3 use a different gate array entirely). Banks 1, 3, 5, and 7 (when paged into the contended region) are late-timing; banks 0, 2, 4, and 6 are uncontended. The pattern still repeats every 8 T-states, but the exact delay vs T-state value differs.

### 128K Contended Banks

| Bank | Mapped at | Contended? |
|---|---|---|
| 0 | (when paged at `#C000`) | No |
| 1 | (when paged at `#C000`) | Yes |
| 2 | `#8000–#BFFF` (fixed) | No |
| 3 | (when paged at `#C000`) | Yes |
| 4 | (when paged at `#C000`) | No |
| 5 | `#4000–#7FFF` (fixed) | Yes |
| 6 | (when paged at `#C000`) | No |
| 7 | (when paged at `#C000`) | Yes |

### 128K Contention Delay Table

The 128K contention pattern is also based on T-state mod 8, but the pattern is offset by 1 from the 48K:

| CPU access T-state (mod 8) | Delay added |
|---|---|
| 0 | +0 |
| 1 | +5 |
| 2 | +4 |
| 3 | +3 |
| 4 | +2 |
| 5 | +1 |
| 6 | +0 |
| 7 | +0 |

### +2A / +3 Contention

The +2A/+3 use the **Amstrad gate array** which behaves differently from the Sinclair ULA. Banks 4, 5, 6, and 7 are contended; banks 0, 1, 2, 3 are uncontended. The contention pattern is similar to the 128K but with subtle differences at the top of the screen (where the gate array's prefetch differs).

For most code, treating the +2A/+3 contention as "same as 128K" works correctly. For cycle-exact effects, see the deep dive in [contention_model.md](../05_development/03_memory_and_io/contention_model.md).

---

## Pentagon Timing Differences

The Pentagon uses "early" contention (different from Sinclair's "late") and a slightly different video frame (320×224 pixels instead of 256×192). The exact T-state layout:

| Item | Pentagon | 48K Sinclair |
|---|---|---|
| Scanline T-states | 224 | 224 |
| Frame scanlines | 320 | 312 |
| Frame T-states | 71,680 | 69,888 |
| Frame rate (Hz) | 48.83 | 50.08 |
| INT line | 0 (start of frame) | 64 |
| Contention type | Early (1 T-state delay) | Late (1–6 T-state delay) |

The Pentagon's **48.83 Hz** is **not** standard PAL — it was chosen for hardware simplicity. This causes drift on European CRTs but is irrelevant on modern displays. Some Russian demos and games check for this difference.

### Pentagon Contention Pattern

| CPU access T-state (mod 8) | Delay added |
|---|---|
| 0 | +0 |
| 1 | +0 |
| 2 | +0 |
| 3 | +0 |
| 4 | +0 |
| 5 | +0 |
| 6 | +0 |
| 7 | +1 |

The Pentagon contention is **much gentler** than the Sinclair 48K — only one T-state of delay per access, and only at one specific position in the 8-T-state cycle.

---

## Interrupt Timing — INT and NMI

### Maskable Interrupt (INT)

The ULA pulls `INT_n` low at the start of every frame:

| Model | INT line | INT T-state |
|---|---|---|
| 48K / 16K | Scanline 64 | ~T-state 14,336 (relative to frame start) |
| 128K / +2 / +2A / +3 | Scanline 64 | ~T-state 14,336 |
| Pentagon | Scanline 0 (start) | T-state 0 |
| Scorpion | Scanline 64 (Sinclair mode) | ~T-state 14,336 |
| ZX Spectrum Next | Configurable (line register) | Configurable |

The Z80 takes about 13 T-states to acknowledge an INT (depending on interrupt mode), so the effective entry to your ISR is **~T-state 14,349 from frame start** on a 48K/128K. This is the canonical "first ISR instruction" timing reference for cycle-exact code.

### Non-Maskable Interrupt (NMI)

The Spectrum's NMI line is wired to the **NMI button** on some peripherals (e.g., Multiface) and to the `Magic` button on Russian clones. Pulling NMI low causes the Z80 to call `#0066` after the current instruction completes. The Z80 takes 13 T-states to acknowledge an NMI.

The 48K ROM's `#0066` handler does a soft reset. Custom NMI handlers are used by the Multiface, Kempston E, and Russian-clone Magic buttons.

### Interrupt Response Latency

The Z80's worst-case interrupt response latency is **21 T-states** (when an interrupt arrives during the slowest instruction, e.g., `LD (HL),n` with contention). Typical latency is **13 T-states** (no contention, simple instruction completing).

For frame-cycle-accurate code (e.g., raster splits), assume your ISR entry is at **T-state ~14,349** plus the latency for the instruction that was in progress when INT fired. Most rasters handle this by inserting a known delay before doing anything timing-sensitive.

---

## Common Instruction T-State Counts

Quick reference for the most-used instructions. For the complete table, see [z80_opcode_table.md](z80_opcode_table.md).

### Load Instructions

| Instruction | T-states (uncontended) | T-states (contended, worst case) |
|---|---|---|
| `LD r,n` | 7 | 13 |
| `LD r,(HL)` | 7 | 13 |
| `LD (HL),r` | 7 | 13 |
| `LD A,(BC)` | 7 | 13 |
| `LD A,(DE)` | 7 | 13 |
| `LD A,(nn)` | 13 | 13 (ROM/uncontended) |
| `LD (nn),A` | 13 | 13 |
| `LD rr,nn` | 10 | 10 |
| `LD HL,(nn)` | 16 | 16 |
| `LD rr,(nn)` | 20 | 20 |
| `LD SP,HL` | 6 | 6 |
| `EX DE,HL` | 4 | 4 |
| `EXX` | 4 | 4 |
| `PUSH rr` | 11 | 11 |
| `POP rr` | 10 | 10 |

### Arithmetic Instructions

| Instruction | T-states |
|---|---|
| `ADD A,r` | 4 |
| `ADD A,(HL)` | 7 |
| `ADD A,n` | 7 |
| `SUB r` | 4 |
| `AND r` | 4 |
| `INC r` | 4 |
| `INC (HL)` | 11 |
| `INC rr` | 6 |
| `ADD HL,rr` | 11 |

### Control Flow

| Instruction | T-states (taken / not taken) |
|---|---|
| `JP nn` | 10 |
| `JP cc,nn` | 10 / 10 |
| `JR n` | 12 / — |
| `JR cc,n` | 12 / 7 |
| `DJNZ n` | 13 / 8 |
| `CALL nn` | 17 |
| `CALL cc,nn` | 17 / 10 |
| `RET` | 10 |
| `RET cc` | 11 / 5 |
| `RST n` | 11 |

### I/O Instructions

| Instruction | T-states (uncontended) | T-states (contended) |
|---|---|---|
| `IN A,(n)` | 11 | 11–17 |
| `IN r,(C)` | 12 | 12–18 |
| `OUT (n),A` | 11 | 11–17 |
| `OUT (C),r` | 12 | 12–18 |
| `INI` | 16 | 16–22 |
| `OTIR` | 21/16 (per iteration) | 21–27/16–22 |
| `IND` | 16 | 16–22 |
| `OUTD` | 16 | 16–22 |

I/O instructions contend on the addressed port — `#FE` reads and writes contend if the ULA is mid-display, even when the CPU is otherwise idle. The contended T-state count varies with the cycle position, like memory contention.

### Stack Operations

| Instruction | T-states |
|---|---|
| `PUSH AF` | 11 |
| `POP AF` | 10 |
| `EX (SP),HL` | 19 |
| `EX (SP),IX` | 23 |

### Block Operations

| Instruction | T-states (per iteration) |
|---|---|
| `LDI` | 16 |
| `LDIR` | 16/21 (last/intermediate) |
| `CPI` | 16 |
| `CPIR` | 16/21 |
| `OUTI` | 16 |
| `OTIR` | 16/21 |
| `IND` | 16 |
| `INDR` | 16/21 |

> [!NOTE]
> Block operations repeat with auto-increment and auto-decrement. The last iteration (when `B` reaches 0) takes 16 T-states; intermediate iterations take 21 T-states. So `LDIR` of N bytes takes `16 + 21*(N-1)` T-states.

---

## Useful Timing Constants

Quick reference for the most-used frame-relative T-state counts:

| Constant | Value | Use |
|---|---|---|
| T-states per scanline (48K/128K) | 224 | Position in scanline |
| Scanlines per frame | 312 (48K) / 311 (128K) | Position in frame |
| T-states per frame | 69,888 (48K) / 70,908 (128K) | Total budget |
| INT latency (typical) | 13 T-states | From INT_n low to ISR entry |
| INT line | 64 (48K/128K) | Scanline where INT fires |
| INT T-state | 14,336 | Relative to frame start |
| ISR entry T-state | 14,349 | Realistic, with INT latency |
| Paper display start | scanline 64 | Top of paper area |
| Paper display end | scanline 255 | Bottom of paper area |
| Border lines (top) | 8–63 | Above paper |
| Border lines (bottom) | 256–311 | Below paper |
| HSYNC T-states | 96 | Per scanline |
| Active paper T-states | 1024 | Per scanline (paper only) |

---

## Cross-References

- [z80_opcode_table.md](z80_opcode_table.md) — full Z80 instruction timing table
- [io_port_map.md](io_port_map.md) — I/O port decoding
- [memory_maps.md](memory_maps.md) — contended vs uncontended regions
- [pinouts.md](pinouts.md) — chip pinouts
- [contention_model.md](../05_development/03_memory_and_io/contention_model.md) — contention deep dive
- [video_frame_48k.md](../05_development/05_display_and_timing/video_frame_48k.md) — 48K video frame deep dive
- [video_frame_128k.md](../05_development/05_display_and_timing/video_frame_128k.md) — 128K video frame deep dive
- [contention_timing.md](../05_development/05_display_and_timing/contention_timing.md) — contention timing patterns
- [floating_bus.md](../05_development/05_display_and_timing/floating_bus.md) — floating bus technique
- [race_the_beam.md](../05_development/04_interrupts/race_the_beam.md) — cycle-exact beam racing (pending)
- [interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md) — interrupt handling overview and programming reference

---

## References

- Zilog — *Z80 CPU Product Specification*, 1998 (last rev) — T-state counts for every instruction
- Sean Young — *Z80 Undocumented Instructions* — T-states for undocumented instructions and quirks
- Chris Smith — *The ZX Spectrum ULA*, 2010 — ULA timing, contention scheme, and floating bus
- Ramsoft — *ZX Spectrum 48K/128K Timing FAQ*, 1998 — the canonical community reference for cycle-exact timing
- World of Spectrum — [Reference FAQ](https://worldofspectrum.org/faq/reference/reference.htm)
- Patrik Rak — *Arkanoid Timing Tables* — exact T-state delays for emulation
- Geoff Wearmouth — *48K ROM Disassembly*, [wearmouth.demon.co.uk](https://www.wearmouth.demon.co.uk/zxsp2.htm)
