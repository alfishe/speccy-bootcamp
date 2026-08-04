[← Home](../../README.md) · [Memory & I/O](README.md)

# Contention Model — Unified Developer Reference

Memory contention is the ZX Spectrum's most important timing constraint. When the ULA (or gate array) reads screen memory to generate the video signal, it **steals bus cycles from the CPU** — making code that accesses shared RAM slower and nondeterministic unless you account for contention explicitly.

This article is a **developer-focused reference** that consolidates contention behavior across all models. For the hardware-level mechanism (why contention exists, how the ULA arbitrates the bus), see [ula_timing.md](../../02_hardware/original/ula_timing.md).

---

## Quick Reference — Per-Model Contention

| Model | Contended range | Contention type | Delay pattern | I/O contended? |
|-------|----------------|-----------------|---------------|----------------|
| **48K** | `#4000`–`#7FFF` (address-based) | Ferranti ULA | 6-5-4-3-2-1-0-0 | Yes (A0=0 ports) |
| **128K / +2** | Banks 1, 3, 5, 7 (DRAM set B) | Ferranti ULA | 6-5-4-3-2-1-0-0 | Yes (A0=0 ports) |
| **+2A / +3** | Banks 4, 5, 6, 7 (all high) | Amstrad gate array | 1-0-7-6-5-4-3-2 | MREQ only |
| **Pentagon** | **None** | N/A | N/A | N/A |
| **Scorpion** | Varies by revision | Mild or none | — | — |
| **Kay** | **None** | N/A | N/A | N/A |
| **ATM Turbo** | Minimal | — | — | — |
| **ZX Spectrum Next** | **Configurable** | Configurable per mode | Configurable | Configurable |

> **Key insight for cross-platform code**: If your code works perfectly on a Pentagon but breaks on a 48K, contention is the most likely culprit. If it works on a 48K but breaks on a +2A/+3, the different contention pattern is the cause.

---

## When Contention Happens

Contention only occurs **during the paper (display) area** — the 192 scanlines where the ULA fetches pixel and attribute bytes. During border lines and vertical blank, the ULA does not access screen RAM and **there is no contention**.

```
Frame layout (48K):

  Top border    64 lines     → No contention (ULA idle)
  Paper area   192 lines     → CONTENTION ACTIVE
  Bottom border 56 lines     → No contention (ULA idle)
  VBlank        included     → No contention (ULA idle)
```

### T-state windows

Within each paper scanline, contention follows a repeating cycle:

**Ferranti ULA (48K, 128K, +2):**

| T-state offset | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Delay | **6** | **5** | **4** | **3** | **2** | **1** | 0 | 0 |

The first 6 T-states of each 8-T-state window have contention; the last 2 are free. The window repeats 16 times per scanline (128T contention window + 96T free).

**Amstrad gate array (+2A, +3):**

| T-state offset | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Delay | 1 | 0 | **7** | **6** | **5** | **4** | **3** | **2** |

The peak delay (7T) is at offset 2 — the pattern is shifted and inverted compared to Ferranti.

---

## What Gets Contended

### Memory Access

| Access type | Contended? | Notes |
|---|---|---|
| Opcode fetch from contended range | **Yes** | The M1 cycle is delayed |
| Memory read from contended range | **Yes** | Any read operation |
| Memory write to contended range | **Yes** | Any write operation |
| Access to ROM (`#0000`–`#3FFF`) | No | ROM is not shared |
| Access to uncontended RAM (48K: `#8000`+) | No | Separate physical RAM |

### I/O Port Access

| Port type | Contended? | Notes |
|---|---|---|
| `#FE` (ULA) and any A0=0 port | **Yes** (Ferranti ULA) | Same contention pattern as memory |
| `#FE` (ULA) on +2A/+3 | **No** | Gate array only contends MREQ |
| `#7FFD` (128K paging) | **Yes** (Ferranti ULA) | Port with A0=0 → contended |
| `#BFFD` / `#FFFD` (AY) | **Yes** (Ferranti ULA) | Port with A0=0 → contended |
| Kempston `#1F` | **No** | A0=1, no ULA contention |

> [!IMPORTANT]
> On the Ferranti ULA, **any port with A0=0** (the ULA port `#FE`, plus 32,767 other aliased addresses) triggers contention during the paper area. This includes `#7FFD` and AY ports — paging the RAM bank or writing to the AY during the display area costs extra T-states.

---

## Per-Model Details

### 48K — Address-Based Contention

The simplest model: addresses `#4000`–`#7FFF` are contended. Everything else is not.

```
Contended:    #4000 - #7FFF   (upper 16K — screen + attributes + system vars)
Uncontended:  #0000 - #3FFF   (ROM)
Uncontended:  #8000 - #FFFF   (lower 32K RAM)
```

The contention pattern is 6-5-4-3-2-1-0-0 during the 128T contention window per scanline. **Pattern starts at T=14,335** (the last T-state of top border, with the ULA prefetching the first paper byte) and repeats every **224 T-states** (one scanline). The closely-related value T=14,336 is the first T-state of scanline 64 (paper display proper) — both values appear in the literature depending on whether one is describing the first delayable access or the first paper pixel. See [contention_timing.md](../05_display_and_timing/contention_timing.md#first-paper-scanline--t-state-by-t-state-ferranti) for the per-T-state delay progression table.

### 128K / +2 — Bank-Based Contention

Contention is determined by **which physical DRAM chip set** the address lives in, not the CPU address directly:

```
DRAM set A (uncontended):  Banks 0, 2, 4, 6 (even banks)
DRAM set B (contended):    Banks 1, 3, 5, 7 (odd banks)
```

- RAM at `#4000`–`#7FFF` is **always contended** because bank 5 (set B) is permanently mapped there as the default screen.
- RAM at `#C000`–`#FFFF` is **conditionally contended** — contended if and only if an odd bank (1, 3, 5, or 7) is paged into that range via `#7FFD`. Page in bank 0, 2, 4, or 6 and code at `#C000` runs at full speed even during the paper area.

The delay **pattern** is the same 6-5-4-3-2-1-0-0 as the 48K, but the **timing differs**: pattern starts at **T=14,361** (not T=14,335) and repeats every **228 T-states** (not 224) because the 128K/+2 scanline is 228T long. Source: [WoS 128K FAQ](https://worldofspectrum.org/faq/reference/128kreference.htm).

### +2A / +3 — Gate Array Contention

The Amstrad gate array (ASIC 40084 in the +2A/+3, 40085 in the +2B/+3B) uses a completely different contention model from the Ferranti ULA:

- **Different contended banks**: 4, 5, 6, 7 (not 1, 3, 5, 7 as on the 128K/+2). Banks 0–3 are never contended regardless of where they're paged.
- **Different delay pattern**: 1-0-7-6-5-4-3-2 (shifted and inverted relative to Ferranti 6-5-4-3-2-1-0-0). Peak delay is **7T** (one worse than Ferranti's 6T) at slot offset 2.
- **MREQ gating**: The gate array applies contention **only when the Z80's `MREQ` line is active** (i.e., a real memory access). I/O port accesses activate `IORQ` instead, leaving `MREQ` inactive, so I/O is **never contended** regardless of port address. This is the underlying reason `OUT (#FE),A`, `OUT (#7FFD),A`, and `OUT (#BFFD),A` all run at full speed during the paper area on +2A/+3.
- **No early/late timing**: The gate array is a single stable ASIC and does not exhibit the thermal drift / ULA-revision variance of the Ferranti chips (5C/6C/7C/8C).
- **Pattern starts at T=14,361** (not T=14,335 as on 48K), repeating every 228 T-states (not 224). For the full per-T-state delay progression table, see [contention_timing.md](../05_display_and_timing/contention_timing.md#first-paper-scanline--t-state-by-t-state-amstrad-gate-array).

> [!WARNING]
> Code that relies on the exact Ferranti contention pattern (6-5-4-3-2-1-0-0) for timing will break on the +2A/+3. The peak delay is 7T instead of 6T, and it occurs at a different T-state offset (slot offset 2 vs slot offset 0).

### Pentagon — No Contention

The Pentagon has **zero memory contention**. There is no ULA — video address generation uses discrete counter chips that run independently of the CPU bus. Code runs at full speed regardless of address or display position.

This means:
- Multicolor effects that depend on contention delays **will not work** without adaptation
- Code in the screen area runs measurably faster than on 48K/128K
- Floating bus behavior is absent or different

---

## Practical Impact on Code

### Instruction Timing Variance

The same instruction can take different amounts of time depending on where it executes and when:

```z80
; LD (HL),A — base cost 7T, but in contended memory during paper area:
; T-state offset 0:  7 + 6 = 13T (worst case)
; T-state offset 6:  7 + 0 =  7T (no contention)
; During border:      7T (never contended)
```

For cycle-exact multicolor effects, you must know your **exact T-state position** within the scanline and account for each instruction's contended cost.

### Worst-Case vs Best-Case Code

```z80
; Code in uncontended RAM (#8000+) accessing contended screen:
LD   HL,#4000       ; HL = contended address
LD   (HL),A         ; 7T base + 0-6T contention on the write cycle
                     ; Opcode fetch is uncontended (PC in #8000+)
                     ; Only the (HL) write is contended

; Code IN contended RAM (#4000+) accessing contended screen:
; BOTH the opcode fetch AND the memory access are contended
; Worst case: 4T fetch + 6T + 3T write + 6T = 19T for LD (HL),A
```

### Contentious Code Pattern — What to Avoid

```z80
; BAD: Tight loop in contended memory during paper area
; Timing is unpredictable due to contention variance
.loop:
    LD   (HL),A       ; 7T + 0-6T contention
    INC  HL            ; 6T + 0-6T contention
    DJNZ .loop         ; 8/13T + 0-6T contention
    ; Total per iteration: 21-31T (47% variance!)
```

### Uncontended Code Pattern — Reliable Timing

```z80
; GOOD: Code in uncontended RAM, data access to contended memory
; Only memory operations are contended — opcode fetch is free
    ; Assume this code is at #8000+ (uncontended)
    LD   HL,#4000       ; 10T — no contention
.wait:
    IN   A,(#FE)        ; 11T base — but I/O IS contended on Ferranti!
    ; Better: use HALT + precise delay for timing
```

---

## Cross-Platform Strategy

### Detect the Machine

```z80
; Simplified detection (see clone_timing.md for full method)
DetectMachine:
    LD   BC,#7FFD
    LD   A,#80
    OUT  (C),A           ; Try 128K paging
    IN   A,(#FF)          ; Check if paging worked
    CP   #80
    JR   Z,.is128K

    ; Could be 48K or clone
    ; Check for Pentagon by timing a frame
    HALT
    LD   BC,0
.delay:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.delay
    ; If BC > 0 after one frame → Pentagon (longer frame)
    ; Exact threshold depends on HALT latency
    RET

.is128K:
    ; Further checks for +2A/+3 vs plain 128K
    RET
```

### Contention Guard Macros

```z80
; For cross-platform code, use conditional assembly:

IF CONTESTED_PLATFORM
    ; 48K/128K: account for contention in T-state budgets
    ; Add NOP padding where contention would steal cycles
ELSE
    ; Pentagon/clone: exact timing, no contention compensation
ENDIF
```

---

## Contention Quick-Reference Card

```
┌──────────────────────────────────────────────────────┐
│              IS MY ACCESS CONTENDED?                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  48K: Address in #4000-#7FFF AND during paper?  YES │
│  128K: Address in odd bank AND during paper?    YES │
│  +2A/+3: Address in bank 4-7 AND during paper?  YES │
│  Pentagon: Never                             NEVER │
│                                                      │
│  During border/VBlank on any model?             NO  │
│  ROM access on any model?                      NO  │
│  I/O on +2A/+3?                               NO  │
│                                                      │
├──────────────────────────────────────────────────────┤
│  Maximum delay: 6T (Ferranti) or 7T (gate array)   │
│  Pattern repeats every 8T during paper scanlines    │
└──────────────────────────────────────────────────────┘
```

---

## Cross-References

- **ULA timing deep dive** (hardware mechanism, contention patterns): [ula_timing.md](../../02_hardware/original/ula_timing.md)
- **Clone timing** (per-clone contention behavior): [clone_timing.md](../../02_hardware/clones/clone_timing.md)
- **48K memory and ports** (contended address ranges): [memory_and_io_48k.md](memory_and_io_48k.md)
- **128K memory and ports** (bank-based contention): [memory_and_io_128k.md](memory_and_io_128k.md)
- **+2A/+3 memory and ports** (gate array contention): [memory_and_io_plus3.md](memory_and_io_plus3.md)
- **48K video frame** (contention windows per scanline): [video_frame_48k.md](../05_display_and_timing/video_frame_48k.md)
- **Z80 timing** (per-instruction T-state costs): [z80_timing.md](../../01_cpu/z80_timing.md)
- **Complete I/O port map** (which ports are contended per model): [io_port_map.md](../../10_references/io_port_map.md)

---

## References

### External references

- [Chris Smith — *The ZX Spectrum ULA: How to Design a Microcomputer* (2010)](http://www.zxdesign.info/) — the definitive reference for the Ferranti ULA's bus-arbitration mechanism that causes contention on the 48K. Documents the exact T-state windows during which the ULA steals cycles from the CPU for video refresh.
- [Sinclair ZX Specifications (Martin Korth)](http://problemkaputt.de/zxdocs.htm) — canonical hardware reference covering the gate-array variants in the 128K / +2 / +2A / +3 and how their contention patterns differ from the 48K Ferranti ULA.
- [World of Spectrum — Contended Memory FAQ](https://worldofspectrum.org/faq/reference/rampages.htm) — community-verified contention tables and timing diagrams for every Sinclair model.
- [zx-pk.ru — contention and clone timing subforum](https://zx-pk.ru/) — primary source for Soviet-clone timing differences (Pentagon has no contention; Scorpion and ATM Turbo vary by revision).
- [Zilog Z80 CPU User Manual (PDF)](https://www.zilog.com/docs/z80/um0080.pdf) — official Z80 timing diagrams; required reading for understanding T-state budgets that contention consumes.
