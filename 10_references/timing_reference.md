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

The INT (interrupt) is asserted at **T=0 of the frame**, 64 lines (14,336 T-states) **before** the first paper line; the first contended T-state follows at T=14,335. This is the canonical sync point for assembly programs.

---

## Memory Contention — 48K

When the ULA is fetching display data during the paper area and the CPU puts an address in `#4000–#7FFF` on the bus, the ULA **stops the CPU clock** (it does not use the Z80 `WAIT_n` pin) until its fetch is done. Each contended bus cycle adds 0–6 T-states, depending on where in the ULA's 8-T fetch group it starts.

> [!WARNING]
> **Requires contended memory timing.** On the Ferranti ULA (48K, 128K, +2) the check covers every T-state with a contended address on the bus — opcode fetches, data reads and writes, **internal (no-MREQ) T-states** such as `INC (HL)`'s extra T on `HL` or `JR`'s 5 extra T on `PC`, and I/O cycles (see [I/O Instructions](#io-instructions)). Naive per-instruction counts will be wrong.

### 48K Contention Delay Table

The first contended T-state is **T=14,335** after the start of the interrupt (FUSE convention; some sources say 14,336 — the same event counted from 1). Each paper line then has a **128-T** contended window starting at 14,335 + n × 224 (n = 0–191); offset = (T − 14,335) mod 224.

| Offset within the 8-T group (offset mod 8, for offset < 128) | Delay added |
|---|---|
| 0 | +6 |
| 1 | +5 |
| 2 | +4 |
| 3 | +3 |
| 4 | +2 |
| 5 | +1 |
| 6 | +0 |
| 7 | +0 |

So an opcode fetch from `#4000–#7FFF` that starts on offset 0 takes 4+6=10 T-states; from uncontended memory (`#8000–#FFFF` or ROM) it takes 4. "Early/late timing": on some machines the whole pattern starts up to 1 T-state later; the Sinclair Wiki attributes this to ULA temperature, not to the board issue.

### When Contention Is Active

| Range | Contended? |
|---|---|
| `#4000–#7FFF` | **Yes** — inside the 128-T window of each of the 192 paper lines |
| `#0000–#3FFF` (ROM) | No |
| `#8000–#FFFF` | No |

Outside these windows (top and bottom border, and the other 96 T-states of each paper line), the ULA is not fetching and access is uncontended.

### 48K Floating Bus

Reading port `#FF` (or any port where `A0=1` and no peripheral decodes the address) returns **whatever the ULA is fetching** at that moment. This is the **floating bus** — used to detect the current raster position without hardware timers. The byte returned is:

- During the ULA's fetches in the paper area: the pixel or attribute byte being fetched
- Outside the fetches (idle T-states of each 8-T group, border, blanking): `#FF`

The floating bus is **not** reliable for cycle-exact timing — it has its own quirks and is best used for coarse position detection. See [floating_bus.md](../05_development/05_display_and_timing/floating_bus.md) for details.

---

## Memory Contention — 128K / +2 / +2A / +3

The 128K/+2 keep the 48K's Ferranti-style contention — same `6,5,4,3,2,1,0,0` table, same clock stopping, internal cycles and I/O contended — but contend **pages** rather than an address range, start at **T=14,361**, and repeat every **228** T-states. The +2A/+3 use the Amstrad gate array, which contends differently (see below).

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

### 128K / +2 Contention Delay Table

Identical to the 48K table, counted from the 128K onset: offset = (T − 14,361) mod 228, contended for offset < 128 on each of the 192 paper lines.

| Offset mod 8 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Delay added | +6 | +5 | +4 | +3 | +2 | +1 | +0 | +0 |

### +2A / +3 Contention

The +2A/+3 use the **Amstrad gate array**, which pulls the Z80 `WAIT_n` pin, and **only during `MREQ` cycles**: no I/O contention and no contention of internal T-states. Banks 4, 5, 6 and 7 are contended **in any slot** (including `#0000` in the all-RAM special paging modes); banks 0–3 never. The pattern starts at T=14,361, repeats every 228 T-states, and uses different values:

| Offset mod 8 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Delay added | +1 | +0 | +7 | +6 | +5 | +4 | +3 | +2 |

The Sinclair Wiki's table gives the same delays T-state by T-state (14361 → 1, 14362 → 0, 14363 → 7, …, 14369 → 1, 14370 → 0, …) and says the pattern "repeats until 14490 tstates" — consistent with a 129-T window (last delayed T-state 14489). The contended window is **129 T** per line on real hardware — offset 128 still adds 1 T (Rak's Timing Test photos from a real +3 and +2A, redcode wiki "Timing-Test"); Fuse, MAME, ZXMAK2 and Xpeccy use 128. Treating the +2A/+3 as "same as 128K" gives wrong results for any contended access. For the deep dive see [contention_model.md](../05_development/03_memory_and_io/contention_model.md).

---

## Pentagon Timing Differences

The Pentagon has **no contention at all** — no memory contention and no I/O contention. Its video logic and the CPU use fixed, separate DRAM slots, so the CPU never waits ("128k of NOT-CONTENDED memory (no slow areas)", Pentagon FAQ). Its video frame is also longer. The exact T-state layout:

| Item | Pentagon | 48K Sinclair |
|---|---|---|
| Scanline T-states | 224 | 224 |
| Frame scanlines | 320 | 312 |
| Frame T-states | 71,680 | 69,888 |
| Frame rate (Hz) | 48.83 | 50.08 |
| Contention | **None** | 0–6 T per contended bus cycle, `#4000–#7FFF` |

The Pentagon's **48.83 Hz** is **not** standard PAL — it was chosen for hardware simplicity. This causes drift on European CRTs but is irrelevant on modern displays. Some Russian demos and games check for this difference.

The Scorpion ZS-256 has no contention either; its one timing quirk is **"Even M1"** — an opcode fetch from RAM that would start on an odd T-state waits 1 T (ROM fetches, data accesses, I/O and interrupt acknowledge never wait). See [Scorpion](../02_hardware/clones/scorpion.md#contention-and-the-even-m1-wait).

---

## Interrupt Timing — INT and NMI

### Maskable Interrupt (INT)

The ULA pulls `INT_n` low at the start of every frame:

| Model | INT line | INT T-state |
|---|---|---|
| 48K / 16K | Frame start, 64 lines before paper | T-state 0 (paper and contention start 14,335–14,336 T later) |
| 128K / +2 / +2A / +3 | Frame start, 63 lines before paper | T-state 0 (contention starts 14,361 T later) |
| Pentagon | Frame start | T-state 0 |
| Scorpion | Frame start | T-state 0 |
| ZX Spectrum Next | Configurable (line register) | Configurable |

The Z80 takes about 13 T-states to acknowledge an INT (depending on interrupt mode), so the effective entry to your ISR is **~13 T-states after INT** (plus the time to finish the instruction in progress) on a 48K/128K — well before the first contended T-state at 14,335 (48K) / 14,361 (128K).

### Non-Maskable Interrupt (NMI)

The Spectrum's NMI line is wired to the **NMI button** on some peripherals (e.g., Multiface) and to the `Magic` button on Russian clones. Pulling NMI low causes the Z80 to call `#0066` after the current instruction completes. The Z80 takes 13 T-states to acknowledge an NMI.

The 48K ROM's `#0066` handler does a soft reset. Custom NMI handlers are used by the Multiface, Kempston E, and Russian-clone Magic buttons.

### Interrupt Response Latency

The Z80's worst-case interrupt response latency is **21 T-states** (when an interrupt arrives during the slowest instruction, e.g., `LD (HL),n` with contention). Typical latency is **13 T-states** (no contention, simple instruction completing).

For frame-cycle-accurate code (e.g., raster splits), assume your ISR entry is at **T-state ~13** plus the latency for the instruction that was in progress when INT fired. Most rasters handle this by inserting a known delay before doing anything timing-sensitive.

---

## Common Instruction T-State Counts

Quick reference for the most-used instructions. For the complete table, see [z80_opcode_table.md](z80_opcode_table.md).

### Load Instructions

| Instruction | T-states (uncontended) | Memory bus cycles (each can add 0–6 T when its address is contended) |
|---|---|---|
| `LD r,n` | 7 | 2 (fetch, operand) |
| `LD r,(HL)` | 7 | 2 (fetch, read) |
| `LD (HL),r` | 7 | 2 (fetch, write) |
| `LD A,(BC)` | 7 | 2 |
| `LD A,(DE)` | 7 | 2 |
| `LD A,(nn)` | 13 | 4 (fetch, 2 operand bytes, read) |
| `LD (nn),A` | 13 | 4 |
| `LD rr,nn` | 10 | 3 |
| `LD HL,(nn)` | 16 | 5 |
| `LD rr,(nn)` | 20 | 6 (2 fetches for the `ED` prefix) |
| `LD SP,HL` | 6 | 1 (+2 internal T on `IR`) |
| `EX DE,HL` | 4 | 1 |
| `EXX` | 4 | 1 |
| `PUSH rr` | 11 | 3 (fetch, 2 stack writes; +1 internal T on `IR`) |
| `POP rr` | 10 | 3 |

Each cycle's delay depends on its own start T-state, so delays are not simply additive worst cases. On the Ferranti ULA the internal T-states are contended too when the address they leave on the bus is contended (e.g. `IR` when `I` is `#40`–`#7F`).

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

The "contended" column is indicative only. On the Ferranti ULA (48K, 128K, +2) the 4-T I/O cycle is contended by **port address**: the high byte (from A for `IN A,(n)`/`OUT (n),A`, from B for the `(C)` forms and block I/O — never from the program counter) and A0 select one of four patterns — high byte not `#40`–`#7F` and A0 = 1: `N:4` (uncontended); not `#40`–`#7F`, A0 = 0: `N:1, C:3`; `#40`–`#7F`, A0 = 1: `C:1, C:1, C:1, C:1`; `#40`–`#7F`, A0 = 0: `C:1, C:3` (Sinclair Wiki, *Contended I/O*). So `#FE` reads and writes are always contended inside the paper windows. On the 128K/+2 a high byte in `#C0`–`#FF` also counts while an odd page is at `#C000`. The +2A/+3 gate array never contends I/O. The opcode fetches are contended separately if the code runs from contended memory.

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
| ISR entry T-state | ~13 | Realistic, with INT latency (IM 1, no instruction in progress) |
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
- [Chris Smith — *The ZX Spectrum ULA](http://www.zxdesign.info/)*, 2010 — ULA timing, contention scheme, and floating bus
- Ramsoft — *ZX Spectrum 48K/128K Timing FAQ*, 1998 — the canonical community reference for cycle-exact timing
- World of Spectrum — [Reference FAQ](https://worldofspectrum.org/faq/reference/reference.htm)
- Patrik Rak — *Arkanoid Timing Tables* — exact T-state delays for emulation
- Geoff Wearmouth — *48K ROM Disassembly*, [wearmouth.demon.co.uk](https://www.wearmouth.demon.co.uk/zxsp2.htm)
