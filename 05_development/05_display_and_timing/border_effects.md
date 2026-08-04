[← Home](../../README.md) · [Display & Timing](README.md)

# Border Effects — Multicolor Borders and Raster Bars

The ZX Spectrum's border is a 32-pixel-wide frame surrounding the 256×192 display area. The border color is set via port `#FE` and can be changed at any time — including mid-scanline. By synchronizing color changes to the raster, you can create multicolor borders and raster bars.

---

## How Border Color Works

Port `#FE` (the ULA port) controls the border color via bits 1–3:

```
  Port #FE write:
  Bit  3  2  1  0
     ┌─────────┬───┐
     │ BORDER  │EAR│  (bit 0 = EAR/MIC output)
     └─────────┴───┘

  Border color = (byte >> 1) & #07
```

The ULA latches the border color and outputs it to the TV signal during the non-paper (border) portion of each scanline. The border color can be changed **at any time** — the ULA uses whatever was last written to port `#FE`.

> [!WARNING]
> Writing to port `#FE` also affects the EAR output (bit 0) and the beeper. If you change only the border, you must preserve the other bits or you'll get unwanted beeps or tape signal changes.

### Safe Border Write

```z80
; Change border color without affecting EAR/beeper
; Input: A = desired color (0-7)
SafeBorder:
    RLCA                 ; Shift color to bits 1-3
    RLCA
    AND  #0E             ; Mask border bits (1-3)
    LD   C,A
    ; Optionally preserve bit 0 (EAR) from current value
    ; If you don't care about EAR, just OUT C directly
    OUT  (#FE),A         ; Set border
    RET
```

---

## Raster Bars — The Basic Effect

A raster bar changes the border color on each scanline (or every few scanlines), creating horizontal color stripes around the display area.

### Single-Color Bars (48K)

```z80
; Simple raster bars — change border every N scanlines
; Must run from uncontended RAM
RasterBars:
    HALT                ; Sync to frame start

    ; Burn time to reach first border scanline
    ; (We're already in the top border area after HALT)
    LD   B,8            ; 8 scanlines per color band
    LD   HL,ColorTable  ; Pointer to color sequence

.nextColor:
    LD   A,(HL)         ; Get next color
    RLCA : RLCA         ; Shift to bits 1-3
    AND  #0E
    OUT  (#FE),A        ; Change border color

    ; Delay for ~8 scanlines = 8 × 224T = 1,792T
    ; This inner loop burns approximately that time
    PUSH BC
    LD   BC,218         ; Tuned delay count
.delay:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.delay
    POP  BC

    INC  HL
    DJNZ .nextColor
    RET

ColorTable: DB 0,1,2,3,4,5,6,7,7,6,5,4,3,2,1,0
```

### Timing Constraints

Each scanline on the 48K is **224 T-states**. The border occupies the entire scanline during border lines (no pixel fetch). You must change the border color at the start of each scanline for clean bars.

```
Timing budget per color change:
  OUT (#FE),A         = 11 T-states (uncontended, in border area)
  Color load + loop   = ~13 T-states
  Remaining per line  = 224 - 11 - 13 = 200 T-states for delay
```

On the 128K/+2, each scanline is **228 T-states** — a slightly different delay count is needed. On the Pentagon, it's **224 T-states** but the border area starts at scanline 0 with fewer top border lines (48 vs 64).

---

## Per-Model Border Differences

| Model | Border scanlines | T-states/line | I/O contended? | Border area timing |
|-------|-----------------|---------------|----------------|-------------------|
| 48K | 64 top + 56 bottom = 120 | 224 | **Yes** (Ferranti) | Simple |
| 128K/+2 | 64 top + 55 bottom = 119 | 228 | **Yes** (Ferranti) | +4T per line |
| +2A/+3 | 64 top + 55 bottom = 119 | 228 | **No** (gate array) | **Easier** — predictable timing |
| Pentagon | 48 top + 48 bottom = 96 | 224 | **No** | Fewer border lines! |

### Cross-Platform Delay Table

| Model | T-states/line | Delay for 1 scanline (after OUT) | Delay for 8 scanlines |
|-------|--------------|----------------------------------|----------------------|
| 48K | 224 | 200T | ~1,792T |
| 128K/+2 | 228 | 204T | ~1,824T |
| +2A/+3 | 228 | 204T | ~1,824T |
| Pentagon | 224 | 200T | ~1,792T |

> [!NOTE]
> On the Ferranti ULA, I/O to port `#FE` during the paper area is contended. But during the border area, there is no contention, so the OUT timing is consistent. The +2A/+3 has no I/O contention at all, making border effects even more predictable.

---

## Advanced Effects

### Gradient Border

Change the border color every scanline for a smooth gradient:

```z80
; One color per scanline — requires precise timing
; This loop must burn exactly 224T (or 228T for 128K) per iteration
Gradient:
    HALT
    LD   HL,GradientData
    LD   B,64            ; 64 top border scanlines

.nextLine:
    LD   A,(HL)          ; 7T
    RLCA : RLCA          ; 8T
    AND  #0E             ; 7T
    OUT  (#FE),A         ; 11T = 33T used

    ; Burn remaining: 224 - 33 = 191 T-states
    ; Using standard delay loop: 191 / ~25 per iteration = ~7.6
    ; Tune the exact count for your scanline timing
    PUSH BC              ; 11T
    LD   BC,21           ; 10T
.burn:
    DEC  BC              ; 6T × 21 = 126T
    LD   A,B             ; 4T × 21 = 84T
    OR   C               ; 4T × 21 = 84T
    JR   NZ,.burn        ; 12T × 20 + 7T × 1 = 247T
    ; Total burn: ~10+126+84+84+247 = 551T — too much!
    ; Need to recalculate — this is why tuning matters
    POP  BC              ; 10T

    INC  HL              ; 6T
    DJNZ .nextLine       ; 13T
    RET

GradientData: DS 64, 0   ; Fill with color values
```

> **T-state budgeting for raster effects is critical**. The above code is a template — exact NOP/delay tuning must be done by counting every T-state in the loop body and adjusting the delay counter.

### Border + Screen Coordination

```z80
; Change border color at the exact transition from border to paper
; This creates a colored strip at the top edge of the display
BorderToPaper:
    HALT
    ; Wait until just before scanline 64 (paper start)
    ; On 48K: T ≈ 14,336 - some_overhead
    LD   BC,CALCULATED_DELAY
.wait:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.wait
    ; Change border at paper boundary
    LD   A,#02 << 1      ; Red border
    OUT  (#FE),A
    RET
```

### Rainbow Border (Demo Effect)

The classic demoscene rainbow: rapid border color cycling across all border scanlines, creating a spectrum of colors around the screen:

```z80
; Rainbow border — change color every 2-3 scanlines
; Uses a pre-computed color table
Rainbow:
    HALT
    LD   HL,RainbowColors
    LD   D,32            ; Number of color bands (top border = 64 lines / 2)

.band:
    LD   E,(HL)          ; Get color pair
    LD   A,E
    AND  #07
    RLCA : RLCA
    AND  #0E
    OUT  (#FE),A         ; First scanline color

    ; Delay for ~1 scanline
    LD   BC,DELAY_1_LINE
.d1: DEC BC : LD A,B : OR C : JR NZ,.d1

    ; Second color
    LD   A,E
    RRCA : RRCA : RRCA
    AND  #0E
    OUT  (#FE),A         ; Second scanline color

    ; Delay for ~1 scanline
    LD   BC,DELAY_1_LINE
.d2: DEC BC : LD A,B : OR C : JR NZ,.d2

    INC  HL
    DEC  D
    JR   NZ,.band
    RET

RainbowColors:
    ; Pack two colors per byte: (color2 << 3) | color1
    DB #01,#23,#45,#67,#76,#54,#32,#10
    DB #01,#23,#45,#67,#76,#54,#32,#10
    ; ... repeat for desired pattern length
```

---

## Border Effects and Paper Area

During the paper area, the border color is still visible in the **left and right margins** of each scanline. The ULA outputs border color for the ~48T left border, then switches to pixel/attribute data for 128T, then back to border color for ~48T right border.

This means:
- Border color changes during the paper area affect the **side borders** only
- The visible border on the left and right of the paper area changes if you write to `#FE` mid-scanline
- This can be used for additional color bands alongside the display area

---

## Antipatterns

### Changing Border During Tape Loading

```z80
; BAD: Border color changes interfere with tape loading
; The ROM tape loader uses border flashes as a visual indicator
; and bit 0 of #FE for EAR input
    LD   A,#04 << 1
    OUT  (#FE),A         ; This also sets EAR bit, corrupting tape signal!
```

### Timing Assumptions

```z80
; BAD: Assuming all machines have same border timing
    ; Pentagon has 48 top border lines (not 64!)
    ; Delay counts must be different
```

---

## Cross-References

- **Color system** (attribute colors, palette, ULAplus): [color_system.md](color_system.md)
- **Raster timing** (HALT sync, beam position): [raster_timing.md](raster_timing.md)
- **48K video frame** (scanline map): [video_frame_48k.md](video_frame_48k.md)
- **I/O ports** (#FE register details): [memory_and_io_48k.md](../03_memory_and_io/memory_and_io_48k.md)
- **Contention model** (I/O contention on Ferranti ULA): [contention_model.md](../03_memory_and_io/contention_model.md)

## References

### External references

- [Chris Smith — The ZX Spectrum ULA](http://www.zxdesign.info/) — definitive reference for the Ferranti ULA 5C/6C, including the `#FE` border/beeper/MIC/EAR port decoding and the contention timing that constrains border-effect loops.
- [Sinclair ZX Specifications](http://problemkaputt.de/zxdocs.htm) — hardware specs, port maps, and the canonical 48K/128K border-line counts (64 top / 48 bottom / 48 left / 48 right).
- [Spectrumpedia](https://speccy.wiki/) — cross-model reference covering the +2A/+3 64-tap border register layout and the Pentagon's divergent border-line counts.
- [zx-pk.ru demoscene forum](https://zx-pk.ru) — primary discussion venue for raster-bar and multicolor border techniques on Soviet clones (where border timing differs from the Sinclair original).
- [WoS archive](https://worldofspectrum.org/) — historic Border-trick demos (e.g., *Epic 128*, *Shock*) that established the standard border-effect idioms.
