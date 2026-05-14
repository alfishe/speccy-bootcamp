[← Home](../../README.md) · [Display & Timing](README.md)

# Raster Timing — Beam Position and Synchronization

Every visual effect on the ZX Spectrum that goes beyond static screens — multicolor, raster bars, sprite multiplexing, smooth scrolling — requires knowing **exactly where the CRT beam is** at every T-state. This article covers how to calculate beam position and the synchronization techniques that work across models.

---

## The Raster Model

The video signal is generated scanline by scanline, top to bottom. At any instant, the "beam" is at a specific (scanline, T-state) position. The beam sweeps left-to-right across each scanline, then returns (horizontal blanking) to start the next line.

```
Scanline 0   ──────────────────────────→   (INT fires here, T=0)
Scanline 1   ──────────────────────────→
...
Scanline 63  ──────────────────────────→   (last top border line)
Scanline 64  ══════════════════════════→   (first paper line, contention starts)
...
Scanline 255 ══════════════════════════→   (last paper line)
Scanline 256 ──────────────────────────→   (first bottom border)
...
Scanline 311 ──────────────────────────→   (last line, VBlank)
                              ↓
              Next frame, scanline 0, T=0 (INT fires)
```

### Beam Position from T-state Count

Given a T-state count since the last INT:

```
scanline   = T_state / T_states_per_line
line_t     = T_state % T_states_per_line
```

| Model | T-states/line | Total lines | Paper start | Paper end |
|-------|--------------|-------------|-------------|-----------|
| 48K | 224 | 312 | Scanline 64 (T=14,336) | Scanline 255 (T=57,344) |
| 128K/+2 | 228 | 311 | Scanline 64 (T=14,592) | Scanline 255 (T=58,140) |
| Pentagon | 224 | 320 | Scanline 48 (T=10,752) | Scanline 239 (T=53,536) |

### Working Backward: T-state from Desired Position

```z80
; Calculate T-state at which a given scanline starts (48K)
; Input: B = target scanline (0-311)
; Output: HL = T-state count
ScanlineToTstate:
    LD   HL,0
    LD   A,B
    OR   A
    RET  Z               ; Scanline 0 = T-state 0
    LD   DE,224           ; T-states per scanline
.loop:
    ADD  HL,DE
    DJNZ .loop
    RET
```

---

## Synchronization Techniques

### Technique 1: HALT — The Standard Frame Sync

`HALT` puts the Z80 to sleep until the next interrupt. This is the foundation of all frame-locked code.

```z80
SyncToFrame:
    HALT                ; CPU halts, waits for INT
    ; Execution resumes here at T≈13 after the INT fires
    ; (HALT finishes at the end of the current M-cycle,
    ;  then the next instruction fetch takes a few more T-states)
```

**Timing uncertainty**: After `HALT` returns, you're at approximately T=13 (varies by 1-2 T-states due to where in the instruction pipeline the HALT was reached). This is precise enough for per-frame effects but **not** for per-scanline effects.

### Technique 2: HALT + Delay — Scanline-Precise

```z80
; Reach a specific scanline after HALT
; Input: B = target scanline (0-311 on 48K)
SyncToScanline:
    HALT                ; T≈13 (start of frame, scanline 0)

    ; Calculate delay: (target_scanline × 224) - 13 T-states
    ; This loop burns exactly 23 T-states per iteration:
    ;   DEC BC = 6T, LD A,B = 4T, OR C = 4T, JR NZ = 12/7T
    ; Total loop: 26T when running, 23T on last iteration

    ; Simplified: approximate delay
    LD   HL,(TargetTstate)
    LD   DE,13
    AND  A
    SBC  HL,DE           ; Subtract HALT overhead
    ; HL = T-states to burn
    ; Convert to loop iterations: HL / 23
    LD   BC,HL/23        ; Pre-calculated
.delay:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.delay
    ; Now at the desired scanline
    RET
```

### Technique 3: Floating Bus — Raster Lock (48K/128K Only)

See [floating_bus.md](floating_bus.md) for full details. The floating bus lets you detect the exact scanline by reading what the ULA is currently fetching.

```z80
; Wait for a specific pixel pattern on the floating bus
; This gives scanline-precise synchronization
WaitForRasterPosition:
    IN   A,(#FF)         ; Read floating bus
    CP   #XX             ; Expected value at target position
    JR   NZ,WaitForRasterPosition
    ; Beam is now at the exact scanline + column
    RET
```

### Technique 4: Interrupt Timer — Cross-Platform

For machines without a reliable floating bus (Pentagon, +2A/+3):

```z80
; Use IM2 interrupt to maintain a scanline counter
; ISR increments a counter each frame
; Main code uses FRAMES system variable for coarse sync
; plus calculated delays for fine positioning

    ; In your ISR:
ISR_Timer:
    PUSH AF
    LD   A,(ScanlineCount)
    INC  A
    LD   (ScanlineCount),A
    POP  AF
    EI
    RETI

ScanlineCount: DB 0
```

---

## Per-Model Raster Position Tables

### 48K Raster Map

| Scanline | T-state start | Region | Content |
|----------|--------------|--------|---------|
| 0 | 0 | Top border | Border color |
| 1–63 | 224–14,111 | Top border | Border color |
| 64 | 14,336 | Paper start | First display line, contention begins |
| 64–255 | 14,336–57,119 | Paper area | 192 display lines with contention |
| 256 | 57,344 | Bottom border | Contention ends |
| 256–311 | 57,344–69,663 | Bottom border + VBlank | No contention |
| → 0 | 69,888 | Next frame | INT fires |

### Pentagon Raster Map

| Scanline | T-state start | Region | Content |
|----------|--------------|--------|---------|
| 0 | 0 | Top border | Border color |
| 1–47 | 224–10,527 | Top border | Border color (shorter than 48K!) |
| 48 | 10,752 | Paper start | First display line, **no contention** |
| 48–239 | 10,752–53,375 | Paper area | 192 display lines, no contention |
| 240 | 53,376 | Bottom border | — |
| 240–319 | 53,376–71,455 | Bottom border + VBlank | — |
| → 0 | 71,680 | Next frame | INT fires |

> [!WARNING]
> The Pentagon's paper area starts at **scanline 48** (not 64 as on 48K). Code that hardcodes "paper starts at scanline 64" will have a 16-scanline error on the Pentagon.

---

## Timing-Critical Loop Patterns

### Burn Exactly N T-states (uncontended RAM)

```z80
; Precise delays in uncontended RAM (#8000+)
; Each pattern burns exact T-states

; Burn 4T:  NOP
; Burn 7T:  RL (HL)  or equivalent
; Burn 10T: DJNZ to NOP
; Burn 13T: CALL + RET

; 23T loop (standard raster timing loop):
;   DEC BC (6T) + LD A,B (4T) + OR C (4T) + JR NZ (12T) = 26T (looping)
;   DEC BC (6T) + LD A,B (4T) + OR C (4T) + JR Z (7T)   = 21T (final)
;   Average ≈ 25T per iteration (close to one scanline's 128T / 5)
```

### Precise 224T Delay (One Scanline on 48K/Pentagon)

```z80
; Burn exactly 224 T-states
; Used to step from one scanline to the next
; Must run in uncontended RAM

    ; 224T = 9 × 24T + 8T
    ; Using a 24T inner loop:
    LD   B,9             ; 7T
.oneLine:
    NOP                  ; 4T × 6 = 24T per iteration
    NOP
    NOP
    NOP
    NOP
    NOP
    DJNZ .oneLine        ; 8T (last) / 13T (looping) → adjusts timing
    ; Remaining: fine-tune with NOPs
    NOP                  ; 4T
    NOP                  ; 4T
    ; Total ≈ 224T (adjust NOP count based on exact B loop overhead)
```

---

## Cross-Platform Raster Sync Strategy

```z80
; Detect machine and use appropriate sync method
RasterSync:
    CALL DetectMachine
    CP   MACHINE_48K
    JR   Z,.sync48K
    CP   MACHINE_128K
    JR   Z,.sync128K
    CP   MACHINE_PENTAGON
    JR   Z,.syncPentagon
    ; +2A/+3 or unknown: use HALT + delay
    JR   .syncGeneric

.sync48K:
    ; Can use floating bus for precision
    HALT
    ; ... floating bus raster lock
    RET

.sync128K:
    ; Floating bus works with minor differences
    HALT
    ; ... floating bus raster lock (same as 48K mostly)
    RET

.syncPentagon:
    ; No floating bus — use HALT + calculated delay
    HALT
    ; Paper starts at scanline 48 (T=10,752), not 64!
    ; ... calculated delay loop
    RET

.syncGeneric:
    ; Safe fallback: HALT + delay, no floating bus
    HALT
    ; ... conservative delay
    RET
```

---

## Cross-References

- **Floating bus** (ULA data reads for raster sync): [floating_bus.md](floating_bus.md)
- **48K video frame** (complete scanline map): [video_frame_48k.md](video_frame_48k.md)
- **128K video frame** (timing differences): [video_frame_128k.md](video_frame_128k.md)
- **Pentagon frame** (different scanline count): [video_frame_pentagon.md](video_frame_pentagon.md)
- **Contention model** (contention during timed delays): [contention_model.md](../03_memory_and_io/contention_model.md)
- **ULA timing** (hardware-level raster generation): [ula_timing.md](../../02_hardware/original/ula_timing.md)
