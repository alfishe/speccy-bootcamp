[← Home](../../README.md) · [Display & Timing](README.md)

# Contention Timing — Per-T-state Delay Tables, Per-Instruction Costs

Memory contention is the single most predictable — yet most often misunderstood — timing constraint on the ZX Spectrum. Once you know the **exact T-state position within a scanline** and the **address being accessed**, the delay the ULA imposes is fully deterministic. This article is the **numerical reference**: every delay value, every per-instruction contended cost, every edge case.

For the conceptual model (why contention exists, which ranges are contended per model), see [contention_model.md](../03_memory_and_io/contention_model.md). For beam-position synchronization, see [raster_timing.md](raster_timing.md). For floating bus values at each T-state, see [floating_bus.md](floating_bus.md).

---

## The Delay Rule (one paragraph)

When the CPU performs a contended memory or I/O access during the paper area, the ULA may insert wait states before granting the bus. The number of wait states depends on **how far into the current 8-T-state "contention slot"** the CPU is when the access begins. The slot is aligned to the ULA's pixel-fetch cadence, not to the start of the scanline. The rule is:

```
delay_at_T = delay_table[T mod 8]
```

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

The pattern `1, 0, 7, 6, 5, 4, 3, 2` is shifted relative to Ferranti: the worst-case delay is **7T** (vs 6T on Ferranti) and occurs at offset 2 instead of offset 0.

> [!WARNING]
> Code tuned to the Ferranti pattern will break on the +2A/+3. The peak delay (7T) is **one T-state worse**, and it occurs at a different T-state offset. Any cycle-exact multicolor effect that works on a 48K needs a separate +2A/+3 code path.

### Other Models

| Model | Delay pattern |
|---|---|
| Pentagon, Leningrad, ZX Evolution | **None** — no ULA, no contention |
| Scorpion ZS-256 | Revision-dependent: mild or none |
| Kay 1024, Byte, Quorum, LEC, Profi | **None** |
| ATM Turbo | Minimal / none (discrete logic video) |
| Sprinter | **None** (SVGA-derived video, separate VRAM) |
| ZX Spectrum Next | **Configurable** per timing mode |
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
| Scorpion (revision-dependent) | ~64 | ~255 | 0 or 192 | ~T=14,344 | 224 T |
| ZX Evolution | (no contention at any line) | — | 0 | — | — |

> [!IMPORTANT]
> The 128K/+2 and +2A/+3 have **63 scanlines of top border** (not 64 like the 48K) because their scanlines are 228 T-states long (not 224). Paper therefore starts at scanline 63, and the contention pattern starts at T=14,361 (not T=14,335 as on the 48K). This 1-scanline offset is a common source of bugs when porting cycle-exact code from 48K to 128K. Sources: [WoS 128K FAQ](https://worldofspectrum.org/faq/reference/128kreference.htm), [Sinclair Wiki — Contended memory](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_memory).

### Within Each Contended Scanline (Ferranti ULA — 48K, 128K, +2)

A single scanline is 224 T-states (48K) or 228 T-states (128K/+2). Of those, only 128 are within contention "active" windows — the remaining 96 (48K) or 100 (128K) are free time:

```
T-state offset within scanline (relative to scanline start):
0─────────16─────────32─────────48─────────64──── ... ────128─────────224
│ horizontal │  contended "active" region  │   free  │      │   free    │
│ retrace    │  16 × 8-T contention slots   │  time   │      │   free    │
                                                                        
Contention pattern within "active" region:
  Slot 0 (T=16-23):  6,5,4,3,2,1,0,0
  Slot 1 (T=24-31):  6,5,4,3,2,1,0,0
  ... (16 slots total)
  Slot 15 (T=136-143): 6,5,4,3,2,1,0,0
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
> The exact T-state offset of the *first* contention slot within the scanline depends on the model. On the 48K, contention starts at T-state 16 of each paper scanline (after horizontal retrace). The pattern above is simplified; for cycle-exact work, always verify with the reference timing table for your specific model.

> [!IMPORTANT]
> **The 14335 vs 14336 issue.** Different authoritative sources cite both T=14,335 and T=14,336 as the "start of contention" on the 48K. Both are correct from different viewpoints: T=14,335 is the T-state at which the **first delay can be observed** (slot 0 begins, delay 6 if CPU accesses contended memory at this instant); T=14,336 is the T-state at which **paper display begins** (scanline 64, first pixel output). The 1-T ambiguity is the foundation of the "early vs late timing" issue documented across 48K ULA revisions (5C/6C/7C/8C). Source: [Sinclair Wiki — Contended memory](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_memory).

### Within Each Contended Scanline (Amstrad Gate Array — +2A, +3, +2B, +3B)

The Amstrad gate array (40084/40085) uses a **shifted and inverted** pattern: peak delay 7T (vs Ferranti's 6T) and the worst-case slot sits at offset 2 instead of offset 0:

```
T-state offset within scanline (relative to scanline start):
0─────────16─────────32─────────48─────────64──── ... ────128─────────228
│ horizontal │  contended "active" region  │   free  │      │   free    │
│ retrace    │  16 × 8-T contention slots   │  time   │      │  (+4 T)   │
                                                                        
Contention pattern within "active" region (different from Ferranti!):
  Slot 0 (T=16-23):  1,0,7,6,5,4,3,2
  Slot 1 (T=24-31):  1,0,7,6,5,4,3,2
  ... (16 slots total)
  Slot 15 (T=136-143): 1,0,7,6,5,4,3,2
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
| 14,488 | 2 | Slot 15 end | Last contended T-state of scanline 63 |
| 14,489–14,588 | **0** | — | 100 T-states free (border/horizontal retrace) |
| 14,589 | **1** | Slot 0 of scanline 64 | Pattern resumes — T offset = 228 from start |

The pattern repeats every **228 T-states** on +2A/+3 (one scanline). The peak delay of 7T is **one T-state worse** than Ferranti's 6T, and occurs at slot offset 2 instead of offset 0 — this means any cycle-exact timing loop tuned for the 48K's 6,5,4,3,2,1,0,0 cadence will be off by 1-2 T-states per slot on a +2A/+3.

> [!IMPORTANT]
> **MREQ gating — the most important +2A/+3 difference.** The Ferranti ULA applies contention **whenever the CPU is on the bus**, regardless of whether the access is memory or I/O. The Amstrad gate array applies contention **only when the Z80's `MREQ` line is active** (i.e., a real memory access). I/O port accesses (`IORQ` active, `MREQ` inactive) are **never contended** on +2A/+3. This is why `OUT (#FE),A` (border color), `OUT (#7FFD),A` (128K paging), and `OUT (#BFFD),A` (AY chip) all run at full speed during the paper area on +2A/+3, but pay up to 6T of contention delay on 48K/128K/+2. Code that uses tight `OUT (#FE),A` loops for multicolor border effects will run **too fast** when ported from +2A/+3 to 48K unless padded with NOPs. Source: [Sinclair Wiki — Contended memory](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_memory).

---

## Per-Instruction Contended Costs

### How to Compute the Cost of an Instruction

For a contended instruction (one that accesses contended memory), the total cost is:

```
total = base_cycles + contention_delay

where contention_delay = delay_table[(T_state_at_start_of_memory_access) mod 8]
```

The memory access happens at a specific T-state within the instruction's cycle breakdown, not at the instruction start. For most instructions, the contended access happens on cycle 3 (the M2 cycle) — but it varies.

### Quick Cost Reference — Common Instructions

For instructions that **fetch opcodes from contended memory** (PC in `#4000`–`#7FFF`):

| Instruction | Base | Worst case | Notes |
|---|---|---|---|
| `NOP` | 4T | **10T** | Pure opcode fetch — full contention applies |
| `LD B,N` | 7T | **13T** | Opcode + immediate both contended |
| `LD A,(HL)` | 7T | **13T** | Opcode + memory read |
| `LD (HL),A` | 7T | **13T** | Opcode + memory write |
| `INC HL` | 6T | **12T** | Opcode fetch only |
| `INC (HL)` | 11T | **17T** | Opcode + read + write (worst case ×2) |
| `LD (HL),r` | 4T base + 3T write | **13T** | Worst case at slot offset 0 |
| `LD (NN),HL` | 16T | **22T** | Multiple memory writes |
| `LD (NN),A` | 13T | **19T** | |
| `JP (HL)` | 4T | **10T** | No real memory access — just opcode |
| `JR NZ,e` | 12/7T | **18/13T** | Branch-taken is 12T (worst case) |
| `CALL nn` | 17T | **23T** | Stack pushes contended if SP in range |
| `RET` | 10T | **16T** | Stack read contended if SP in range |
| `LDIR` | 21/16T | **27/22T per iteration** | Each iteration has both read and write |
| `HALT` | 4T + N×4T wait | Variable | HALT itself is short; N = number of waited cycles |

For instructions executing from **uncontended memory** (`#8000`+ or ROM) but **accessing contended data** (HL pointing into `#4000`–`#7FFF`):

| Instruction | Base | Worst case | Notes |
|---|---|---|---|
| `LD A,(HL)` | 7T | **10T** | Opcode uncontended, only memory read contended |
| `LD (HL),A` | 7T | **10T** | Same — opcode free, write contended |
| `INC (HL)` | 11T | **14T** | Read-modify-write — single contention delay |
| `LDIR` | 21/16T | **24/19T per iter** | Read + write, both contended |

> [!IMPORTANT]
> The second case (uncontended code, contended data) is **the recommended pattern** for any code that must touch the screen during the paper area. You save one round of contention on the opcode fetch — typically 6T per instruction.

### Stack in Contended Memory

If `SP` points into `#4000`–`#7FFF` (which is rare but possible — e.g., stack at the top of screen RAM), then `PUSH`, `POP`, `CALL`, and `RET` all suffer contention delays on their stack accesses. **Always place the stack in uncontended RAM** (`#8000`+ on 48K).

---

## I/O Port Contention

On the Ferranti ULA, **I/O writes to ports with A0=0** (the ULA port and its aliases) also suffer contention. This is critical for `OUT (#FE),A` (border color) and `OUT (C),r` (AY chip writes). The root cause is that the Ferranti ULA keys contention off the CPU bus generally — it cannot distinguish a memory access from an I/O access.

The Amstrad gate array (+2A/+3/+2B/+3B) is more selective: it keys contention off the Z80's **`MREQ`** line, which is only active during memory accesses. I/O accesses activate **`IORQ`** instead, leaving `MREQ` inactive, so **I/O is never contended** on the gate array regardless of port address.

| Port | A0 | Contended on Ferranti? | Contended on +2A/+3? |
|---|---|---|---|
| `#FE` (ULA) | 0 | **Yes** (6-5-4-3-2-1-0-0) | No (`IORQ` active, `MREQ` inactive) |
| `#7FFD` (128K paging) | 0 | **Yes** | No (same — `MREQ` gating) |
| `#BFFD` / `#FFFD` (AY) | 0 | **Yes** | No (same) |
| `#F4` / `#1F` (Kempston) | 1 | No | No |
| `#FADF` (Fuller) | 1 | No | No |

> [!IMPORTANT]
> Code that does `OUT (#FE),A` to change the border color during the paper area on a 48K or 128K will pay a contention delay of up to **6 extra T-states**. On the +2A/+3, the same instruction takes the same time regardless of beam position. This means **timing-tight border-effect code that works on +2A will run too fast on 48K** unless you pad with NOPs. See also the [MREQ gating](#within-each-contended-scanline-amstrad-gate-array--2a-3-2b-3b) note above for the underlying cause.

---

## Predicting the Delay — A Worked Example

Suppose we are at T-state **T=14340** (paper line 0, T=4 within scanline), about to execute `LD (HL),A` where `HL` points to `#4000`. We want to know how long the instruction will actually take.

**Step 1**: Where in the 8-T contention slot are we?
```
slot_offset = 4 mod 8 = 4
```

**Step 2**: Look up the delay:
```
delay_table[4] = 2  (Ferranti)
```

**Step 3**: Add to base:
```
LD (HL),A base = 7T
Total = 7 + 2 = 9T
```

**Step 4**: After the instruction, we are at T-state **T=14349** (within the same scanline).

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

When the ULA is fetching bytes from screen RAM during the paper area, those bytes appear on the data bus. A CPU read from contended memory at the right moment can sample them — this is the **floating bus**. The values you see correlate with the ULA's fetch position, not the actual address you read.

```
T-state within paper scanline   What appears on floating bus read
─────────────────────────────   ──────────────────────────────────
slot 0 (T=16-19, pixel)         Pixel byte 0 of scanline
slot 1 (T=20-23, attribute)     Attribute byte 0
slot 2 (T=24-27, pixel)         Pixel byte 1
slot 3 (T=28-31, attribute)     Attribute byte 1
...
slot 30 (T=136-139)             Attribute byte 15
slot 31+ (T=140+)               No fetch — bus value is "previous" (unreliable)
```

This is detailed fully in [floating_bus.md](floating_bus.md). For contention purposes, the key fact is: **a floating bus read is itself a contended memory access** — the read pays the contention delay, then returns the ULA's current fetch value.

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
│    I/O:       Contended (A0=0 ports)                     │
│                                                          │
│  +2A, +3 (Amstrad):                                     │
│    Pattern:   1-0-7-6-5-4-3-2                            │
│    Worst:     +7T per contended access                   │
│    I/O:       NOT contended                              │
│                                                          │
│  Pentagon, Leningrad, ZX Evolution, Kay, Profi:          │
│    Pattern:   None                                       │
│    Worst:     0T                                         │
│    I/O:       Not contended                              │
│                                                          │
│  Scorpion:                                               │
│    Pattern:   Varies by revision (often none)            │
│                                                          │
│  ZX Spectrum Next:                                       │
│    Pattern:   Configurable (48K/128K/+2A/Pentagon modes) │
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
- **ZXMAK2 emulator source** — documents per-revision Scorpion contention and the differences between Ferranti revisions (5C/6C/7C/8C).
- **Ramsoft ZX Spectrum FAQ** — original community documentation of contention timing, the basis for all emulator implementations.
- **[zx-pk.ru](https://zx-pk.ru) forum threads** — real-hardware measurements confirming contention patterns on specific machine revisions. Notable: "Ferranti ULA contention probe results", "+2A gate array timing measurements".
