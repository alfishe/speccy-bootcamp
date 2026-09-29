[← Home](../../README.md) · [Display & Timing](README.md)

# Contention Timing — Per-T-state Delay Tables, Per-Instruction Costs

Memory contention is the single most predictable — yet most often misunderstood — timing constraint on the ZX Spectrum. Once you know the **exact T-state position within a scanline** and the **address being accessed**, the delay the ULA imposes is fully deterministic. This article is the **numerical reference**: every delay value, every per-instruction contended cost, every edge case.

For the conceptual model (why contention exists, which ranges are contended per model), see [contention_model.md](../03_memory_and_io/contention_model.md). For beam-position synchronization, see [raster_timing.md](raster_timing.md). For floating bus values at each T-state, see [floating_bus.md](floating_bus.md).

---

## The Delay Rule (one paragraph)

When the CPU performs a contended access during the paper area, the video chip holds the CPU before granting the bus — the Ferranti ULA (48K/128K/+2) by **stopping the CPU clock**, the Amstrad gate array (+2A/+3) by pulling the Z80 **`/WAIT`** pin. The number of lost T-states depends on **how far into the current 8-T-state "contention slot"** the CPU is when the bus cycle begins. The slot is aligned to the ULA's pixel-fetch cadence, not to the start of the scanline. The rule is:

```
offset      = (T - onset) mod line_length        ; onset = 14335 (48K), 14361 (128K/+2/+2A/+3)
delay_at_T  = delay_table[offset mod 8]  if line is a paper line and offset < 128
                                          (offset < 129 on the +2A/+3 gate array)
            = 0                          otherwise
```

On the Ferranti ULA the check applies to every T-state the CPU spends with a contended address on the bus — memory cycles, **internal (no-MREQ) T-states**, and I/O cycles (by port address, see [I/O Port Contention](#io-port-contention)). On the gate array it applies only to `/MREQ` cycles.

Where `delay_table` depends on which ULA / gate array is generating video. The CPU effectively sees each contended T-state stretched by the wait, so **T-state counting continues through the delay** — it doesn't restart.

---

## The Two Delay Tables

### Ferranti ULA (48K, 128K, +2)

Applies to all Sinclair-built Spectrums with the original ULA family (5C, 6C, 7C, 8C):

| T-state offset within 8-T slot | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| **Delay (T-states)** | **6** | **5** | **4** | **3** | **2** | **1** | **0** | **0** |

The pattern `6, 5, 4, 3, 2, 1, 0, 0` repeats 16 times per scanline during the paper area. The first 6 T-states of each slot have contention (decreasing); the last 2 are free.

### Amstrad Gate Array (+2A, +3)

Applies to Amstrad-built machines with the 40084/40085 gate array:

| T-state offset within 8-T slot | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| **Delay (T-states)** | 1 | 0 | **7** | **6** | **5** | **4** | **3** | **2** |

The pattern `1, 0, 7, 6, 5, 4, 3, 2` is **not** a rotation of the Ferranti values: the worst-case delay is **7T** (vs 6T on Ferranti), it occurs at offset 2 instead of offset 0, and only one T-state per slot is free. The Sinclair Wiki's table gives the same delays T-state by T-state (14361 → 1, 14362 → 0, 14363 → 7, …, 14369 → 1, 14370 → 0, …) and says the pattern "repeats until 14490 tstates" — consistent with a 129-T window (last delayed T-state 14489). Real-hardware runs of Rak's Timing Test (a +3 in 2023, a +2A in 2025; redcode wiki "Timing-Test") show a **129-T** contended window per line — one T-state (delay 1) beyond the 128 T that Fuse, MAME, ZXMAK2 and Xpeccy use.

> [!WARNING]
> Code tuned to the Ferranti pattern will break on the +2A/+3. The peak delay (7T) is **one T-state worse**, and it occurs at a different T-state offset. Any cycle-exact multicolor effect that works on a 48K needs a separate +2A/+3 code path.

### Other Models

| Model | Delay pattern |
|---|---|
| Pentagon 128/512/1024 | **None** — video and CPU use fixed, separate DRAM slots |
| Leningrad-1 | Disputed (no schematic-level source): Russian Wikipedia claims 48K-style slowdown at `#4000`–`#7FFF`; ZXMAK2 models an Even M1 alignment instead |
| ZX Evolution (BaseConf) | **None** in the default Pentagon raster; 48K-style contention **emulated** in its optional 48K/128K rasters, at 3.5 MHz only |
| Scorpion ZS-256 (all boards) | **None** (no memory or I/O contention). Its one delay is **"Even M1"**: an opcode fetch from RAM that would start on an odd T-state waits 1 T — see [Scorpion](../../02_hardware/clones/scorpion.md#contention-and-the-even-m1-wait) |
| Kay 1024, Profi | **None** at 3.5 MHz |
| Byte, Quorum, LEC | Believed none (no primary source found) |
| ATM Turbo | **None** (discrete-logic slot interleave) |
| Sprinter | **None** ULA-style (separate VRAM); in turbo, accesses to the slower main DRAM wait |
| ZX Spectrum Next | 48K / 128K / +3 contention **emulated in the matching timing mode at 3.5 MHz only**; none in Pentagon timing or at any turbo speed |
| ZX-Uno, MiSTer (48K mode) | Replicates Ferranti 6-5-4-3-2-1-0-0 |
| ZX-Uno, MiSTer (+2A mode) | Replicates Amstrad 1-0-7-6-5-4-3-2 |

---

## Per-Scanline Contention Maps

### When Contention Is Active

Contention only occurs during the **paper area** — the 192 scanlines where the video circuit fetches pixel and attribute bytes. Outside the paper area, no contention.

| Model | First contended scanline | Last contended scanline | Contended scanlines | Pattern starts at T | Repeats every |
|---|---|---|---|---|---|
| 48K | 64 | 255 | 192 | T=14,335 | 224 T (1 scanline) |
| 128K / +2 | **63** | **254** | 192 | **T=14,361** | **228 T** (1 scanline) |
| +2A / +3 | **63** | **254** | 192 | **T=14,361** | **228 T** (1 scanline) |
| Pentagon | (no contention at any line) | — | 0 | — | — |
| Scorpion (all boards) | (no contention at any line — only the Even M1 fetch alignment, see [Scorpion](../../02_hardware/clones/scorpion.md#contention-and-the-even-m1-wait)) | — | 0 | — | — |
| ZX Evolution (Pentagon raster) | (no contention at any line) | — | 0 | — | — |

> [!IMPORTANT]
> The 128K/+2 and +2A/+3 have **63 scanlines of top border** (not 64 like the 48K) because their 311-line frame (of 228-T-state lines) has one fewer top-border line than the 48K's 312. Paper therefore starts at scanline 63, and the contention pattern starts at T=14,361 (not T=14,335 as on the 48K). This 1-scanline offset is a common source of bugs when porting cycle-exact code from 48K to 128K. Sources: [WoS 128K FAQ](https://worldofspectrum.org/faq/reference/128kreference.htm), [Sinclair Wiki — Contended memory](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_memory).

### Within Each Contended Scanline (Ferranti ULA — 48K, 128K, +2)

A single scanline is 224 T-states (48K) or 228 T-states (128K/+2). Of those, only 128 are within contention "active" windows — the remaining 96 (48K) or 100 (128K) are free time:

```
T-state offset relative to this line's contention onset (onset + n × 224 on the 48K):
0──────8──────16── ... ──120──────128────────────────────────224
│ slot 0│ slot 1│   ...   │ slot 15│   free (border, retrace)  │
│    16 × 8-T contention slots     │   96 T (48K) / 100 T (128K)│

Contention pattern within the contended region:
  Slot 0 (offset 0-7):      6,5,4,3,2,1,0,0
  Slot 1 (offset 8-15):     6,5,4,3,2,1,0,0
  ... (16 slots total)
  Slot 15 (offset 120-127): 6,5,4,3,2,1,0,0
```

#### First Paper Scanline — T-state by T-state (Ferranti)

The pattern's first slot is aligned to the frame, not the scanline. On the 48K, contention begins at **T=14,335** (the last T-state of the last top-border scanline — the ULA is already prefetching the first paper byte) and continues 6,5,4,3,2,1,0,0 across every 8-T slot:

| T-state | Delay | Pattern slot | Notes |
|---|---|---|---|
| 14,335 | **6** | Slot 0 begin | Last T-state of top border — ULA prefetch |
| 14,336 | **5** | Slot 0 | First T-state of scanline 64 (paper line 0) |
| 14,337 | **4** | Slot 0 | |
| 14,338 | **3** | Slot 0 | |
| 14,339 | **2** | Slot 0 | |
| 14,340 | **1** | Slot 0 | |
| 14,341 | 0 | Slot 0 | |
| 14,342 | 0 | Slot 0 end | |
| 14,343 | **6** | Slot 1 begin | |
| 14,344 | **5** | Slot 1 | |
| 14,345 | **4** | Slot 1 | |
| 14,346 | **3** | Slot 1 | |
| 14,347 | **2** | Slot 1 | |
| 14,348 | **1** | Slot 1 | |
| 14,349 | 0 | Slot 1 | |
| 14,350 | 0 | Slot 1 end | |
| ... | ... | ... | Pattern continues |
| 14,462 | 0 | Slot 15 end | Last contended T-state of scanline 64 |
| 14,463–14,558 | **0** | — | 96 T-states free (border/horizontal retrace) |
| 14,559 | **6** | Slot 0 of scanline 65 | Pattern resumes — T offset = 224 from start |

The pattern repeats every **224 T-states** on 48K (one scanline). Over the 192 paper scanlines, the pattern fires 192 × 16 = 3,072 slots in total. After scanline 255 (T=57,344), no further contention until the next frame's T=14,335.

> [!NOTE]
> The position of the first contention slot within the scanline depends on the model and on where you put the line origin. Counting lines from the interrupt (line n starts at n × 224 on the 48K), the first contended T-state 14,335 = 64 × 224 − 1 is the **last** T-state of line 63, so each paper line's contended region starts 1 T before the line origin. For cycle-exact work, count from the onset values in the table above.

> [!IMPORTANT]
> **The 14335 vs 14336 issue.** Different authoritative sources cite both T=14,335 and T=14,336 as the "start of contention" on the 48K. Both describe the same event counted from a different origin: FUSE's convention puts the first 6-T delay at T=14,335; sources that count the interrupt's first T-state as 1 (or measure from a slightly different reference, as Rak's Timing Test does) give 14,336. This counting difference is **not** the same thing as "early vs late timing": that is a real shift of up to 1 T-state in the contention onset that the Sinclair Wiki attributes to ULA temperature (a warm ULA drifts from early to late), not to board issue or ULA revision. Source: [Sinclair Wiki — Contended memory](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_memory).

### Within Each Contended Scanline (Amstrad Gate Array — +2A, +3, +2B, +3B)

The Amstrad gate array (40084/40085) uses a **different** pattern — not a rotation of the Ferranti values: peak delay 7T (vs Ferranti's 6T), the worst-case T-state sits at offset 2 instead of offset 0, and the window is 129 T long on real hardware:

```
T-state offset relative to this line's contention onset (onset + n × 228):
0──────8──────16── ... ──120──────128─129────────────────────228
│ slot 0│ slot 1│   ...   │ slot 15│ 1 │   free (border, retrace) │
│    16 × 8-T contention slots     │   │   99 T                   │

Contention pattern within the contended region (different from Ferranti!):
  Slot 0 (offset 0-7):      1,0,7,6,5,4,3,2
  Slot 1 (offset 8-15):     1,0,7,6,5,4,3,2
  ... (16 slots total)
  Slot 15 (offset 120-127): 1,0,7,6,5,4,3,2
  Offset 128:               1   (real +3 / +2A; emulators use 0)
```

#### First Paper Scanline — T-state by T-state (Amstrad Gate Array)

On the +2A/+3, contention begins at **T=14,361** (3 T-states before scanline 63 begins at T=14,364 — again, ULA prefetch) and follows the 1,0,7,6,5,4,3,2 pattern across every 8-T slot:

| T-state | Delay | Pattern slot | Notes |
|---|---|---|---|
| 14,361 | **1** | Slot 0 begin | Still in scanline 62 (top border) — ULA prefetch |
| 14,362 | 0 | Slot 0 | |
| 14,363 | **7** | Slot 0 | Peak delay 7T at offset 2 within slot |
| 14,364 | **6** | Slot 0 | First T-state of scanline 63 (paper line 0) |
| 14,365 | **5** | Slot 0 | |
| 14,366 | **4** | Slot 0 | |
| 14,367 | **3** | Slot 0 | |
| 14,368 | **2** | Slot 0 end | |
| 14,369 | **1** | Slot 1 begin | |
| 14,370 | 0 | Slot 1 | |
| 14,371 | **7** | Slot 1 | Peak delay 7T at offset 2 within slot |
| 14,372 | **6** | Slot 1 | |
| 14,373 | **5** | Slot 1 | |
| 14,374 | **4** | Slot 1 | |
| 14,375 | **3** | Slot 1 | |
| 14,376 | **2** | Slot 1 end | |
| ... | ... | ... | Pattern continues |
| 14,488 | 2 | Slot 15 end | Last T-state of the 128-T window |
| 14,489 | **1** | — | 129th T-state: contended on a real +3/+2A (Rak's Timing Test); 0 in Fuse, MAME, ZXMAK2, Xpeccy |
| 14,490–14,588 | **0** | — | 99 T-states free (border/horizontal retrace) |
| 14,589 | **1** | Slot 0 of scanline 64 | Pattern resumes — T offset = 228 from start |

The pattern repeats every **228 T-states** on +2A/+3 (one scanline). The peak delay of 7T is **one T-state worse** than Ferranti's 6T, and occurs at slot offset 2 instead of offset 0 — this means any cycle-exact timing loop tuned for the 48K's 6,5,4,3,2,1,0,0 cadence will be off by 1-2 T-states per slot on a +2A/+3.

> [!IMPORTANT]
> **MREQ gating — the most important +2A/+3 difference.** The Ferranti ULA applies contention **whenever a contended address is on the bus** — memory cycles, internal (no-MREQ) T-states and I/O cycles alike. The Amstrad gate array applies contention **only when the Z80's `MREQ` line is active** (i.e., a real memory access). I/O port accesses (`IORQ` active, `MREQ` inactive) and internal T-states are **never contended** on +2A/+3. So the I/O cycle of `OUT (#FE),A` (border color) or of an `OUT (C),A` to `#7FFD` (128K paging) runs at full speed during the paper area on +2A/+3, but is contended on 48K/128K/+2 (`#FE` because A0 = 0; `#7FFD` because its high byte `#7F` is in `#40`–`#7F`). An AY write to `#BFFD` is uncontended on both. Code with tight `OUT (#FE),A` loops tuned on a +2A/+3 will therefore run **slower** on a 48K/128K/+2 during the paper area. Source: [Sinclair Wiki — Contended memory](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_memory), [Contended I/O](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_I/O).

---

## Per-Instruction Contended Costs

### How to Compute the Cost of an Instruction

For a contended instruction (one that accesses contended memory), the total cost is:

```
total = base_cycles + contention_delay

where contention_delay = sum over the instruction's contended bus cycles of
                         delay_table[(T_at_start_of_that_cycle - onset) mod 8]   ; see The Delay Rule
```

The memory access happens at a specific T-state within the instruction's cycle breakdown, not at the instruction start. For most instructions, the contended access happens on cycle 3 (the M2 cycle) — but it varies.

### Quick Cost Reference — Common Instructions

> [!WARNING]
> **Requires contended memory timing.** The "base + 6T" column below adds **one** maximal delay to the base cost — it is a quick upper-bound feel for a single access, not the true worst case. In reality **every** contended bus cycle pays its own delay (and on the Ferranti ULA so does every internal T-state with a contended address on the bus, e.g. `JR`'s 5 internal T-states on `PC`, `INC (HL)`'s extra T-state on `HL`), and each delay shifts the slot offset of the next cycle. For exact costs, step through the instruction's bus cycles with the delay rule above (Fuse's per-instruction contention tables do exactly this).

For instructions that **fetch opcodes from contended memory** (PC in `#4000`–`#7FFF`):

| Instruction | Base | Base + one 6T delay | Notes |
|---|---|---|---|
| `NOP` | 4T | **10T** | Pure opcode fetch — full contention applies |
| `LD B,N` | 7T | **13T** | Opcode + immediate both contended |
| `LD A,(HL)` | 7T | **13T** | Opcode + memory read |
| `LD (HL),A` | 7T | **13T** | Opcode + memory write |
| `INC HL` | 6T | **12T** | Opcode fetch only; its 2 internal T-states put `IR` on the bus (contended only if `I` is `#40`–`#7F`) |
| `INC (HL)` | 11T | **17T** | Opcode + read + internal T + write — each can pay its own delay if HL is contended |
| `LD (HL),r` | 4T base + 3T write | **13T** | Worst case at slot offset 0 |
| `LD (NN),HL` | 16T | **22T** | Multiple memory writes |
| `LD (NN),A` | 13T | **19T** | |
| `JP (HL)` | 4T | **10T** | No memory access beyond the opcode fetch |
| `JR NZ,e` | 12/7T | **18/13T** | Plus the offset read, and on the Ferranti ULA the 5 internal T-states of a taken branch (address = the offset byte) |
| `CALL nn` | 17T | **23T** | Stack pushes contended if SP in range |
| `RET` | 10T | **16T** | Stack read contended if SP in range |
| `LDIR` | 21/16T | **27/22T per iteration** | Each iteration has both read and write |
| `HALT` | 4T + N×4T wait | Variable | HALT itself is short; N = number of waited cycles |

For instructions executing from **uncontended memory** (`#8000`+ or ROM) but **accessing contended data** (HL pointing into `#4000`–`#7FFF`):

| Instruction | Base | Base + one 6T delay | Notes |
|---|---|---|---|
| `LD A,(HL)` | 7T | **13T** | Opcode uncontended, only memory read contended (a single access: 7–13T) |
| `LD (HL),A` | 7T | **13T** | Same — opcode free, write contended |
| `INC (HL)` | 11T | **17T** | Read, internal T (Ferranti only) and write each pay their own delay |
| `LDIR` | 21/16T | **27/22T per iter** | Read + write, and on the Ferranti ULA the internal T-states on `DE` and the repeat cycles on `PC` |

> [!IMPORTANT]
> The second case (uncontended code, contended data) is **the recommended pattern** for any code that must touch the screen during the paper area. You save one round of contention on the opcode fetch — typically 6T per instruction.

### Stack in Contended Memory

If `SP` points into `#4000`–`#7FFF` (which is rare but possible — e.g., stack at the top of screen RAM), then `PUSH`, `POP`, `CALL`, and `RET` all suffer contention delays on their stack accesses. **Always place the stack in uncontended RAM** (`#8000`+ on 48K).

---

## I/O Port Contention

On the Ferranti ULA, I/O reads and writes are contended by **port address**, in one of four patterns. Two conditions decide which: whether the port's **high byte** is in `#40`–`#7F` (it looks like a contended memory address), and whether **A0 = 0** (the ULA's own port and its aliases). The high byte comes from the **A register** for `IN A,(n)` / `OUT (n),A` and from the **B register** for `IN r,(C)` / `OUT (C),r` and the block I/O instructions — never from the program counter.

| High byte in `#40`–`#7F`? | A0 = 0? | Pattern (4 T of the I/O cycle) |
|---|---|---|
| No | No | `N:4` — uncontended |
| No | Yes | `N:1, C:3` |
| Yes | No | `C:1, C:1, C:1, C:1` |
| Yes | Yes | `C:1, C:3` |

`C:n` = apply the delay for the current T-state, then n T-states; `N:n` = n T-states with no check. On the 128K/+2 a high byte in `#C0`–`#FF` also counts as contended while an odd page is mapped at `#C000`. Source: [Sinclair Wiki — Contended I/O](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_I/O).

The Amstrad gate array (+2A/+3/+2B/+3B) is more selective: it contends only when the Z80's **`MREQ`** line is active. I/O cycles activate **`IORQ`** instead, leaving `MREQ` inactive, so **I/O is never contended** on the gate array regardless of port address.

| Port (as `OUT (C),A`) | A0 | High byte | Contended on 48K / 128K / +2? | Contended on +2A/+3? |
|---|---|---|---|---|
| `#xxFE` (ULA) | 0 | any | **Yes** — `N:1, C:3`, or `C:1, C:3` when B is `#40`–`#7F` | No |
| `#7FFD` (128K paging) | 1 | `#7F` | **Yes** — `C:1, C:1, C:1, C:1` | No |
| `#BFFD` (AY data) | 1 | `#BF` | No (`N:4`) | No |
| `#FFFD` (AY register select) | 1 | `#FF` | 48K: no. 128K/+2: only while an odd page is at `#C000` | No |
| `#001F` (Kempston) | 1 | `#00` | No | No |

> [!IMPORTANT]
> Code that does `OUT (#FE),A` to change the border color during the paper area on a 48K or 128K will pay an I/O contention delay of up to **6 extra T-states** (more when A holds `#40`–`#7F`, since the pattern then has two check points). On the +2A/+3, the I/O cycle takes the same time regardless of beam position. This means **timing-tight border-effect code tuned on a +2A/+3 will run slower on a 48K/128K** during the paper area, and needs less padding there. See also the [MREQ gating](#within-each-contended-scanline-amstrad-gate-array--2a-3-2b-3b) note above for the underlying cause.

---

## Predicting the Delay — A Worked Example

Suppose we are on a 48K at T-state **T=14340** (paper line 0), about to execute `LD (HL),A` from uncontended code at `#8000`, where `HL` points to `#4000`. We want to know how long the instruction will actually take.

**Step 1**: The opcode fetch (M1, 4T) reads `#8000` — uncontended. It runs T=14340–14343.

**Step 2**: The memory write starts at T=14344. Where in the 8-T contention slot is that?
```
slot_offset = (14344 - 14335) mod 8 = 1
```

**Step 3**: Look up the delay:
```
delay_table[1] = 5  (Ferranti)
```

**Step 4**: Add to base:
```
LD (HL),A base = 7T
Total = 7 + 5 = 12T
```

**Step 5**: After the instruction, we are at T-state **T=14352** (within the same scanline).

This is the basis for cycle-exact multicolor effects: maintain a running T-state counter and look up the delay for each instruction.

### Practical Pseudocode

```python
def execute_instruction(addr, opcode_T_at_start, instr_cycles, is_contended):
    if not is_contended:
        return instr_cycles
    # Memory access happens at some T-state offset into the instruction
    access_T = opcode_T_at_start + (instr_cycles - 3)  # crude approximation
    delay = delay_table_ferranti[access_T % 8]
    return instr_cycles + delay
```

Real implementations (Fuse, ZEsarUX, Unreal) use detailed per-instruction timing tables that account for exactly which T-state within each instruction triggers the memory access.

---

## Contention and the Floating Bus

When the ULA is fetching bytes from screen RAM during the paper area, those bytes appear on the ULA's data bus. An **I/O read from a port that no device decodes** (e.g. `IN A,(#FF)`) at the right moment samples them — this is the **floating bus** (Ferranti machines only; the +2A/+3 differs). Memory reads always return the addressed byte. The values you see correlate with the ULA's fetch position, not with the port you read.

```
Offset within each 8-T fetch group    What a floating-bus read returns (Ferranti)
──────────────────────────────────    ──────────────────────────────────────────
0                                     Pixel byte n
1                                     Attribute byte n
2                                     Pixel byte n+1
3                                     Attribute byte n+1
4-7                                   #FF (ULA idle)
```

This is detailed fully in [floating_bus.md](floating_bus.md), including the exact first T-state per model. For contention purposes, the key fact is: **a floating-bus read is an I/O cycle**, so it follows the I/O rules above — `IN A,(#FF)` (A0 = 1) is contended only when the port's high byte (the value in A) is `#40`–`#7F`.

---

## Contention Test Routine

A canonical routine to measure contention on an unknown machine:

```z80
; Measure contention pattern by reading from #4000 at varying offsets
; Returns delay profile in a buffer
MeasureContention:
    LD   HL,BUFFER         ; Output buffer (32 bytes)
    LD   B,32              ; Test 32 offsets
    LD   DE,8              ; Step size (one contention slot)
    LD   IX,T_BASE         ; Base T-state counter
.loop:
    ; Sync to known scanline start
    HALT
    ; Burn delay to reach test offset
    ; ... (calculated based on iteration)
    
    ; Read contended memory — measure actual cycle count
    LD   A,(#4000)         ; This instruction pays contention
    ; ... record T-state delta ...
    
    ADD  IX,DE
    DJNZ .loop
    RET
```

Real-world contention probes (e.g., the ones used by emulator authors to validate Ferranti timing) are more elaborate but follow this structure: sync to a known T-state, perform a contended access, measure the actual cost.

---

## Contention Comparison Cheat Sheet

```
┌──────────────────────────────────────────────────────────┐
│             HOW BAD IS CONTENTION ON MY MACHINE?          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  48K, 128K, +2 (Ferranti):                              │
│    Pattern:   6-5-4-3-2-1-0-0                            │
│    Worst:     +6T per contended access                   │
│    I/O:       Contended (A0=0 or high byte #40-#7F)      │
│                                                          │
│  +2A, +3 (Amstrad):                                     │
│    Pattern:   1-0-7-6-5-4-3-2                            │
│    Worst:     +7T per contended access                   │
│    I/O:       NOT contended                              │
│                                                          │
│  Pentagon, ATM, ZX Evolution (Pentagon raster), Kay,    │
│  Profi:                                                  │
│    Pattern:   None                                       │
│    Worst:     0T                                         │
│    I/O:       Not contended                              │
│                                                          │
│  Scorpion ZS-256 (all boards):                           │
│    Pattern:   None                                       │
│    Other:     Even M1 — RAM opcode fetch on an odd T     │
│               waits 1T (never ROM, data, I/O)            │
│                                                          │
│  ZX Spectrum Next:                                       │
│    Pattern:   48K/128K/+3 timing at 3.5 MHz only;        │
│               none in Pentagon timing or turbo           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Cross-References

- [Contention model](../03_memory_and_io/contention_model.md) — conceptual reference (what contention is, which addresses are contended)
- [Floating bus](floating_bus.md) — ULA data reads during contention cycles
- [Raster timing](raster_timing.md) — beam position calculation and synchronization techniques
- [Video frame 48K](video_frame_48k.md) — base Ferranti timing reference
- [Video frame +2A/+3](video_frame_plus2a_plus3.md) — gate array timing reference
- [Video frame Pentagon](video_frame_pentagon.md) — zero-contention reference
- [Clone timing overview](../../02_hardware/clones/clone_timing.md) — per-clone contention comparison
- [ULA timing](../../02_hardware/original/ula_timing.md) — hardware-level contention mechanism
- [Z80 timing](../../01_cpu/z80_timing.md) — per-instruction T-state costs (base, before contention)
- [Border effects](border_effects.md) — practical code using contention timing
- [Video frame comparison](video_frame_comparison.md) — all models side-by-side

---

## Primary Sources

- [Chris Smith, The ZX Spectrum ULA: How to Design a Microcomputer](http://www.zxdesign.info/) — the definitive hardware reference for Ferranti ULA contention. Documents the exact delay mechanism and the 6-5-4-3-2-1-0-0 pattern.
- ** Fuse emulator source** ([github.com/fuse-emulator/fuse](https://github.com/fuse-emulator/fuse)) — `peripherals/ula.c` contains the contention model implementation. The reference for Ferranti timing.
- **ZEsarUX emulator source** ([github.com/chernandezba/zesarux](https://github.com/chernandezba/zesarux)) — implements both Ferranti and Amstrad contention with detailed per-cycle accuracy.
- **Unreal Speccy emulator** ([github.com/mkoloberdin/unrealspeccy](https://github.com/mkoloberdin/unrealspeccy)) — `unreal.ini` defines `CONTENTION=` per model preset (0 for Pentagon, 1 for 48K, 2 for +2A/+3).
- **ZXMAK2 emulator source** — models no contention on the Scorpion; its yellow-board Scorpion applies an Even M1 alignment to opcode fetches at `#4000`–`#FFFF` (see [Scorpion](../../02_hardware/clones/scorpion.md#contention-and-the-even-m1-wait) for the circuit-level rule).
- **[Sinclair Wiki — Contended I/O](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_I/O)** — the four I/O contention patterns; "the ULA pauses the processor by stopping its clock"; no I/O contention on the +3.
- **Rak's Timing Test v0.3** (redcode wiki "Timing-Test", "Results on real hardware") — photos from a real +3 (2023) and +2A (2025) showing the 129-T gate array window.
- **Ramsoft ZX Spectrum FAQ** — original community documentation of contention timing, the basis for all emulator implementations.
- **[zx-pk.ru](https://zx-pk.ru) forum threads** — clone hardware discussions, including the Scorpion EPLD equations behind its Even M1 wait.
