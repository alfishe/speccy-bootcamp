[← Home](../../README.md) · [Display & Timing](README.md)

# 48K Video Frame — T-State Map, Contention, and the Floating Bus

The ZX Spectrum 48K generates a **312-scanline, 69,888 T-state frame** at approximately **50.08 Hz**. Every scanline, every contention delay, every interrupt timing is precisely determined by the Ferranti ULA's internal state machine. This article provides the complete T-state map for the 48K frame — the reference that all cycle-exact code is built on.

> [!NOTE]
> This article builds on the [video frame overview](video_frame_overview.md). If you haven't read it yet, start there for PAL fundamentals and the general frame structure. This article adds the 48K-specific details: exact contention patterns, the floating bus, and practical timing tables.

---

## Frame Parameters (48K)

```
┌─────────────────────────────────────────────────────┐
│  ZX Spectrum 48K Frame Timing                       │
├─────────────────────────────────────────────────────┤
│  T-states per scanline:     224                     │
│  Total scanlines:           312                     │
│  Total T-states per frame:  69,888                  │
│  Frame rate:                3,500,000 / 69,888      │
│                             ≈ 50.080086 Hz          │
│  Frame duration:            19.968 ms               │
│                                                     │
│  Top border:       64 lines  (T=0 – T=14335)        │
│  Paper area:      192 lines  (T=14336 – T=57343)    │
│  Bottom border:    56 lines  (T=57344 – T=69887)    │
│                                                     │
│  INT asserted:    T-state 0, line 0                 │
│  INT duration:    32 T-states                       │
│  Contended range: #4000–#7FFF (during paper area)   │
└─────────────────────────────────────────────────────┘
```

---

## Complete Scanline Map

| Line | T-state range | Region | Contention | Notes |
|------|---------------|--------|------------|-------|
| 0 | 0–223 | Top border | No | INT at T=0 |
| 1 | 224–447 | Top border | No | |
| 2 | 448–671 | Top border | No | |
| ... | ... | Top border | No | |
| 63 | 14064–14287 | Top border | No | |
| 64 | 14336–14559 | Paper line 0 | **Yes** | First paper scanline |
| 65 | 14560–14783 | Paper line 1 | **Yes** | |
| 66 | 14784–15007 | Paper line 2 | **Yes** | |
| ... | ... | Paper area | **Yes** | |
| 255 | 57024–57247 | Paper line 191 | **Yes** | Last paper scanline |
| 256 | 57344–57567 | Bottom border | No | Contention ends |
| 257 | 57568–57791 | Bottom border | No | |
| ... | ... | Bottom border | No | |
| 311 | 69664–69887 | Bottom border | No | Last scanline |
| (312) | 69888 = 0 | Frame wraps | | New INT at T=0 |

### Interrupt Position

The interrupt fires at **T-state 0 of scanline 0** — the very start of the top border:

```
T-state   Event
───────   ─────────────────────────────────────────
0         INT line goes low (asserted)
1–31      INT remains asserted (32 T-states total)
32        INT line goes high (de-asserted)
...
14336     Paper area begins (64 lines after INT)
───────   ─────────────────────────────────────────

The Z80 has 14,336 T-states (64 scanlines) between INT and the
first paper scanline — uncontended time for setup operations.
```

---

## Contention Pattern

During the paper area (scanlines 64–255), the ULA reads pixel and attribute data from RAM. When the CPU accesses the contended range (`#4000`–`#7FFF`), the ULA may **delay the CPU** by inserting wait states.

### Per-Scanline Contention

The contention pattern repeats every **8 T-states** within each paper scanline:

```
T-state offset within scanline (during paper area):
Offset:  0  1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  ...
Delay:   6  5  4  3  2  1  0  0  6  5   4   3   2   1   0   0  ...

Pattern repeats: 6, 5, 4, 3, 2, 1, 0, 0 (period = 8 T-states)
```

This means:
- At the start of each 8-T-state cycle, the ULA is accessing RAM and the CPU may be delayed by up to **6 T-states**
- In the middle of each cycle, the ULA is not accessing RAM and there is **no delay**

### Practical Impact

```z80
; Example: LD A,(HL) in contended memory
; Normal: 7 T-states
; In contended area: 7 + up to 6 = up to 13 T-states
; Average overhead: ~3.5 T-states per instruction in worst case

; This makes T-state counting in contended area UNRELIABLE
; unless you know the exact T-state offset within the scanline
```

### Contention Window

Contention is active **only during the paper area**:

```
Scanlines 0–63:    No contention (top border)
Scanlines 64–255:  Contention active when accessing #4000–#7FFF
Scanlines 256–311: No contention (bottom border + blanking)
```

Code running in **non-contended RAM** (`#8000`–`#FFFF`) is never delayed, even during the paper area. Only accesses to `#4000`–`#7FFF` trigger contention.

---

## The Floating Bus

When the CPU reads from contended memory during a ULA fetch cycle, it may read **the data the ULA is currently fetching** rather than the actual memory contents. This is the **floating bus** — an unintended feature that became a programming tool.

### What Value Appears

```
During the paper area, reading from contended memory (#4000–#7FFF):

If the read occurs during a ULA pixel fetch:
  → Returns the pixel byte the ULA just read
  
If the read occurs during a ULA attribute fetch:
  → Returns the attribute byte the ULA just read
  
If the read occurs during a non-fetch cycle:
  → Returns the previous value on the data bus (unpredictable)
```

### Using the Floating Bus as Raster Sync

The floating bus can be used to **detect the current scanline position** without any port access:

```z80
; Wait for a specific attribute pattern on the floating bus
; This is used in some multicolor effects to synchronize to the raster
WaitForRaster:
    IN   A,(#FF)         ; Read floating bus (any even port works)
    CP   #47             ; Looking for specific attribute value
    JR   NZ,WaitForRaster
    ; We're now synchronized to a specific raster position
```

> [!WARNING]
> The floating bus behavior is **different on different models** and even between emulators. The 128K/+2 has a different floating bus pattern from the 48K, and the +2A/+3 may not have a usable floating bus at all. Code that relies on the floating bus should detect the machine type and use alternative sync methods on non-48K hardware.

### Floating Bus Values During Paper Area

```
T-state within scanline (relative to paper start):
Offset  0-3:    Pixel byte 0 (of current scanline)
Offset  4-7:    Attribute byte 0
Offset  8-11:   Pixel byte 1
Offset  12-15:  Attribute byte 1
...
Offset  124-127: Pixel byte 31 (last pixel byte)
Offset  128-131: Attribute byte 31 (last attribute byte)
Offset  132+:   Previous bus value (unreliable)

Pattern repeats every 4 T-states: pixel, pixel, pixel, pixel,
then attribute, attribute, attribute, attribute
```

---

## Timing-Sensitive Code Patterns

### HALT-Based Raster Sync

```z80
; Synchronize to the start of the paper area
; HALT waits for the next interrupt (INT)
SyncToFrame:
    HALT                ; Wait for INT (T=0 of frame)
    ; Now at T≈13 (after HALT wakes up and executes next instruction)
    
    ; Delay to a specific scanline
    ; Each scanline = 224 T-states
    ; To reach scanline N (in top border):
    ;   T-states to waste = N × 224 - (current T-state)
    
    ; Example: wait for scanline 64 (start of paper)
    LD   BC,2380        ; Approximate delay count
.delay:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.delay
    ; Now near the start of the paper area
```

### Precise Contention-Aware Timing

```z80
; For cycle-exact multicolor effects, you must account for
; contention delays. This requires knowing your exact T-state
; position within the scanline.

; Example: change border color at a specific T-state
; Uses OUT (#FE),A which takes 11 T-states uncontended

BorderEffect:
    HALT               ; Sync to frame start
    ; ... precise delay to desired scanline ...
    
    ; At this point we know our T-state position
    ; The next OUT instruction takes 11 T-states
    ; But if we're in contended area, it may take more
    
    LD   A,#02          ; Red border
    OUT  (#FE),A        ; Change border (11 T-states + contention)
    
    ; The border color changes exactly when the ULA reads
    ; the new value — which is the NEXT scanline after the OUT
```

---

## Performance Budget

```
Per-frame CPU time budget (48K):

Total T-states:            69,888
Time at 3.5 MHz:           19.968 ms

Available (uncontended):   26,880 T-states (top + bottom border)
  Top border:              14,336 T-states (64 lines × 224)
  Bottom border:           12,544 T-states (56 lines × 224)
  
Available (contended):     ~32,000 effective T-states
  Paper area:              42,888 T-states total
  ULA steals:              ~12,288 T-states (192 × 64)
  Net for CPU:             ~30,600 T-states (in non-contended code)
  Code in screen area:     Even less due to contention delays

Total useful T-states:     ~57,000 per frame
As percentage:             ~82% of frame time usable by CPU
ULA overhead:              ~18% stolen for video generation
```

---

## Cross-References

- **Video frame overview** (PAL basics, all models): [video_frame_overview.md](video_frame_overview.md)
- **128K frame** (contention differences, shadow screen): [video_frame_128k.md](video_frame_128k.md)
- **ULA timing deep dive** (contention patterns, early/late timing, **snow effect**): [ula_timing.md](../../02_hardware/original/ula_timing.md)
- **Pentagon frame** (320 lines, no contention): [video_frame_pentagon.md](video_frame_pentagon.md)
- **Race the beam** (raster sync techniques): [race_the_beam.md](raster_timing.md)
- **Z80 interrupt system**: [z80_interrupts.md](../../01_cpu/z80_interrupts.md)
- **Floating bus reference**: [floating_bus.md](floating_bus.md)

## References

### External references

- **Chris Smith — *The ZX Spectrum ULA*** (book) — the definitive reference for the 48K's Ferranti ULA 5C/6C: every scanline count, every T-state, the 69888-T-state frame, the 64-line top border, the 56-line bottom border, the 256-line display, and the contention pattern.
- **Sinclair ZX Specifications** (Martin Korth) — hardware reference covering the 48K bus timing, the CPU clock, and the INT pulse placement that anchors every frame-sensitive technique.
- **Complete Spectrum ROM Disassembly** (Logan / O'Hara) — annotated 48K ROM showing how the standard frame budget is used by the BASIC interrupt handler and the BEEP routine.
- **`zx-pk.ru` 48K timing threads** — primary discussion venue for Soviet-clone deviations from 48K timing; documents why Pentagon code written against 48K frame parameters fails.
- **SpecEmu / ZEsarUX source code** — emulator references for the 48K's exact scanline-by-scanline contention and the floating-bus reference values used in test software.
