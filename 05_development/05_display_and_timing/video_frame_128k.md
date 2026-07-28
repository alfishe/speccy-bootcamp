[← Home](../../README.md) · [Display & Timing](README.md)

# 128K / +2 Video Frame — Contention Differences, Shadow Screen, and Timing Divergence

The ZX Spectrum 128K (toastrack) and +2 (grey) use the **same Ferranti ULA core** as the 48K for video generation — but the frame is **311 scanlines at 70,908 T-states** (vs the 48K's 312 scanlines at 69,888 T-states), and the **contention behavior is different** because the 128K has 8 RAM banks instead of one contiguous block, and the ULA's screen fetches affect different banks depending on the paging configuration.

> [!NOTE]
> This article covers **only the differences** from the 48K frame. For the complete frame structure (PAL timing, scanline layout, INT position), see [video_frame_48k.md](video_frame_48k.md). For 128K memory paging, see [memory_and_io_128k.md](../03_memory_and_io/memory_and_io_128k.md).

---

## Frame Parameters (128K / +2)

```
┌────────────────────────────────────────────────────┐
│  ZX Spectrum 128K / +2 Frame Timing                │
├────────────────────────────────────────────────────┤
│  T-states per scanline:     228   (NOT 224 — differs from 48K)│
│  Total scanlines:           311   (NOT 312 — differs from 48K)│
│  Total T-states per frame:  70,908 (NOT 69,888 — differs)    │
│  Frame rate:                ~50.02 Hz (slightly slower)       │
│                                                                │
│  Top border:       63 lines   (NOT 64 — 1 scanline less)      │
│  Paper area:      192 lines   (same as 48K)                   │
│  Bottom border:    56 lines   (same as 48K)                    │
│                                                                │
│  INT position:    T=0, line 0 (same as 48K)                   │
│  INT duration:    32 T-states (same as 48K)                    │
│                                                                │
│  Contention:      Same 6-5-4-3-2-1-0-0 pattern as 48K         │
│  Contention start: T=14,361   (NOT 14,335 — shifted by +26 T) │
│  Contended banks: 1, 3, 5, 7 (odd banks)                      │
│  Screen bank:     Bank 5 (or bank 7 if shadow)                │
└────────────────────────────────────────────────────┘
```

The frame structure is **similar** to the 48K but **not identical** — scanlines are 228 T-states (not 224), there are 311 of them (not 312), and the top border is only 63 lines (not 64). The differences are subtle but matter for cycle-exact code: paper starts at scanline 63 (T=14,364) and contention starts at T=14,361, both shifted slightly later than the 48K's scanline 64 / T=14,336. The contention delay **pattern** itself (6,5,4,3,2,1,0,0 repeating) is identical to the 48K.

---

## Contention Model Differences

### 48K vs 128K Contention

```
48K contention:
  Address range:  #4000–#7FFF (always contended during paper area)
  All other RAM:  Never contended
  Pattern:        6, 5, 4, 3, 2, 1, 0, 0 (same as 128K per-line)

128K contention:
  Contended banks: 1, 3, 5, 7 (the "odd" banks)
  Uncontended:     0, 2, 4, 6 (the "even" banks)
  
  Bank 5 is ALWAYS at #4000–#7FFF → always contended (screen)
  Banks 1, 3, 7 can be paged into #C000–#FFFF → contended there too
  Banks 0, 2, 4, 6 are NEVER contended regardless of address
```

### Why Odd Banks Are Contended

The 128K uses 4164 DRAM chips (64K × 1 bit each, 8 chips for 64 KB). The ULA can only access one "side" of the DRAM at a time. The memory is physically organized as:

```
Physical DRAM layout:
  Chip set A (4 chips): Stores even banks (0, 2, 4, 6) at column 0 + row 0-3
  Chip set B (4 chips): Stores odd banks (1, 3, 5, 7) at column 1 + row 0-3

ULA fetches pixels from bank 5 → accesses chip set B
CPU accessing bank 5, 3, 7, or 1 → also chip set B → contention!
CPU accessing bank 0, 2, 4, or 6 → chip set A → no contention
```

The ULA always fetches screen data from chip set B (where bank 5 lives). Any CPU access to the same chip set during a ULA fetch cycle is delayed.

### Per-Instruction Impact

```z80
; Example: LD A,(HL) in different banks

; HL in bank 2 (at #8000-#BFFF, never contended):
LD A,(HL)   ; Always 7 T-states

; HL in bank 5 (at #4000-#7FFF, always contended):
LD A,(HL)   ; 7 T-states + 0-6 T-states contention delay

; HL in bank 3 (paged at #C000-#FFFF, contended!):
LD A,(HL)   ; 7 T-states + 0-6 T-states contention delay
; NOTE: On 48K, #C000 is NEVER contended!
; This is a critical difference for porting 48K code to 128K.
```

---

## Shadow Screen Timing

The 128K's shadow screen (bank 7) has timing implications:

### Screen Fetch Source

```
When screen select bit (bit 3 of #7FFD) = 0:
  ULA fetches pixels from bank 5's #4000-#57FF range
  ULA fetches attributes from bank 5's #5800-#5AFF range
  Contention applies to bank 5 (and other odd banks)

When screen select bit = 1:
  ULA fetches pixels from bank 7's pixel area
  ULA fetches attributes from bank 7's attribute area
  Contention STILL applies to bank 7 (odd bank) when paged in
  Bank 5's contention is reduced (ULA no longer fetching from it)
```

### Double Buffering Timing

```z80
; Frame-synchronized double buffer flip
DoubleBufferFlip:
    ; Wait for frame start (top border = safe time)
    HALT               ; Sync to INT
    
    ; Currently displaying bank 5, drawing to bank 7
    ; Flip: now display bank 7, draw to bank 5
    
    ; Read current screen select state
    ; (We track it because #7FFD is write-only)
    LD   A,(screenBank)   ; 0 = bank 5 displayed, 1 = bank 7 displayed
    XOR  %00001000        ; Toggle screen select bit
    LD   (screenBank),A
    OUT  (#7FFD),A        ; Apply
    
    ; Bank 7 is now displayed (or bank 5 if toggled back)
    ; During the top border, we can safely write to the
    ; non-displayed bank's screen area without visual glitches
    
    ; ... draw to the non-displayed bank ...
    RET
```

> [!TIP]
> The screen flip (writing to `#7FFD`) takes effect **immediately** — the ULA switches which bank it fetches from on the very next scanline. To avoid a visible tear, flip during the **vertical blanking period** (bottom border) or during the top border (before paper area begins).

---

## Early vs Late Timing

The 128K/+2 has the same **early/late timing** issue as the 48K — the ULA's contention delay depends on the exact T-state offset within the scanline. However, there is a subtle difference:

```
48K:   Contention delay starts at T-state 0 of each paper scanline
128K:  Same contention delay pattern, but the exact T-state alignment
       may differ by ±1 T-state depending on the 128K's ULA revision

This means multicolor effects that are cycle-exact on 48K may be
off by 1 T-state on some 128K machines — the effect may appear
shifted by one pixel column.
```

For most practical purposes, this difference is negligible. Only the most demanding multicolor effects (8×1 attribute changes) are affected.

---

## Floating Bus Differences

The floating bus behaves **differently on the 128K** compared to the 48K:

```
48K floating bus:
  During paper area: returns pixel/attribute bytes being fetched by ULA
  Pattern is predictable and well-documented

128K floating bus:
  Returns similar data but timing may differ slightly
  Some 128K revisions return different values during certain T-states
  The shadow screen bank affects what the floating bus returns

+2A/+3 floating bus:
  The Amstrad gate array has significantly different floating bus behavior
  Some T-states return #FF (no useful data)
  Floating bus is NOT reliable for raster sync on +2A/+3
```

> [!WARNING]
> If your code uses the floating bus for raster synchronization, you **must** detect the machine type and use different techniques for different models. On the +2A/+3, use the interrupt timer or HALT-based synchronization instead.

---

## Summary: 48K vs 128K Frame Differences

| Feature | 48K | 128K/+2 |
|---------|-----|----------|
| Frame size | 69,888 T-states | **70,908 T-states** (+1,020 T) |
| Scanlines | 312 | **311** (one less) |
| T-states per scanline | 224 | **228** (+4 T per line) |
| Top border | 64 lines | **63 lines** (one less) |
| Paper start | Scanline 64 (T=14,336) | **Scanline 63 (T=14,364)** |
| Contention pattern start | T=14,335 | **T=14,361** (shifted +26 T) |
| Frame rate | 50.08 Hz | 50.02 Hz (slightly slower) |
| INT position | T=0, line 0 | T=0, line 0 (identical) |
| Contended address range | `#4000`–`#7FFF` always | Banks 1, 3, 5, 7 (odd banks) |
| Non-contended RAM | `#8000`–`#FFFF` | Banks 0, 2, 4, 6 |
| Shadow screen | No | Yes (bank 7) |
| Floating bus | Predictable | Slightly different, varies by revision |
| Screen buffer | 1 (bank 5) | 2 (bank 5 + bank 7) |

### Porting 48K Code to 128K

Most 48K code runs correctly on the 128K because the frame structure is **similar** — but not identical. Watch out for:

1. **Frame timing**: The 128K has 311 scanlines at 228 T-states each (70,908 T/frame), vs the 48K's 312 at 224 T-states (69,888 T/frame). Cycle-exact code that hardcodes 69,888 or 224 will be off.

2. **Contention start**: Contention begins at T=14,361 on 128K (vs T=14,335 on 48K) — shifted by +26 T-states. Code that synchronizes to paper start needs re-timing.

3. **Top border is 63 lines**: One less scanline of free time before paper starts. ISRs that assumed 64 scanlines × 224 T-states = 14,336 T of setup time actually have 63 × 228 = 14,364 T (28 T more — usually fine, but worth verifying).

4. **Memory**: If your code relied on `#8000`–`#FFFF` being uncontended, it still is — on the 128K, banks 2 and 0 are not contended. But if you page in an odd bank at `#C000`, code running there will be contended.

5. **Timing-sensitive code**: Multicolor effects and raster sync may need adjustment for floating bus differences.

6. **Memory layout**: The BASIC program area starts at a different address. Use `PROG` (`#5C53`) system variable to find it dynamically.

7. **ROM differences**: When in 128K mode, ROM 0 is paged in, which has different routines from the 48K ROM. Switch to ROM 1 (48K) for compatibility: `LD A,%00010000; OUT (#7FFD),A`.

---

## Cross-References

- **48K frame** (base reference): [video_frame_48k.md](video_frame_48k.md)
- **+2A/+3 frame** (Amstrad gate array): [video_frame_plus2a_plus3.md](video_frame_plus2a_plus3.md)
- **128K memory map** (paging, banks): [memory_and_io_128k.md](../03_memory_and_io/memory_and_io_128k.md)
- **ULA timing deep dive**: [ula_timing.md](../../02_hardware/original/ula_timing.md)
- **Clone timing** (Pentagon, Scorpion): [clone_timing.md](../../02_hardware/clones/clone_timing.md)
- **Floating bus** (complete reference): [floating_bus.md](floating_bus.md)
