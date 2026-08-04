[← Home](../../README.md) · [Display & Timing](README.md)

# Raster Timing — Beam Position and Synchronization

Every visual effect on the ZX Spectrum that goes beyond static screens — multicolor, raster bars, sprite multiplexing, smooth scrolling — requires knowing **exactly where the CRT beam is** at every T-state. This article covers how to calculate beam position and the synchronization techniques that work across models.

> [!NOTE]
> This article focuses on **synchronization techniques and cross-platform strategies**. Per-model timing data (scanline counts, T-state maps, contention patterns) is in dedicated articles:
> - [video_frame_48k.md](video_frame_48k.md) — 48K: 312 lines, 224T/line, ULA contention
> - [video_frame_128k.md](video_frame_128k.md) — 128K/+2: 311 lines, 228T/line, odd-bank contention
> - [video_frame_plus2a_plus3.md](video_frame_plus2a_plus3.md) — +2A/+3: gate array contention
> - [video_frame_pentagon.md](video_frame_pentagon.md) — Pentagon: 320 lines, zero contention
> - [clone_timing.md](../../02_hardware/clones/clone_timing.md) — Scorpion, Kay, ATM Turbo, ZX Evolution, Next, MiSTer

---

## The Raster Model

The video signal is generated scanline by scanline, top to bottom. At any instant, the "beam" is at a specific (scanline, T-state) position. The beam sweeps left-to-right across each scanline, then returns (horizontal blanking) to start the next line.

```
Scanline 0   ──────────────────────────→   (INT fires here, T=0)
Scanline 1   ──────────────────────────→
...
              (top border region)
...
              ══════════════════════════→   (first paper line, contention starts)
...
              ══════════════════════════→   (last paper line)
...
              ──────────────────────────→   (bottom border)
...
              ──────────────────────────→   (last line, VBlank)
                            ↓
              Next frame, scanline 0, T=0 (INT fires)
```

The exact scanline numbers for each region **vary by model**. See the per-model articles linked above for precise boundaries.

### Beam Position from T-state Count

Given a T-state count since the last INT:

```
scanline   = T_state / T_states_per_line
line_t     = T_state % T_states_per_line
```

| Model | T-states/line | Total lines | Paper start | Paper end |
|-------|--------------|-------------|-------------|-----------|
| 48K | 224 | 312 | Scanline 64 | Scanline 255 |
| 128K/+2 | 228 | 311 | **Scanline 63** | **Scanline 254** |
| +2A/+3 | 228 | 311 | **Scanline 63** | **Scanline 254** |
| Pentagon | 224 | 320 | Scanline 48 | Scanline 239 |
| Scorpion | 224 | 312 | Scanline 64 | Scanline 255 |

> [!WARNING]
> The Pentagon's paper area starts at **scanline 48** (not 64 as on Sinclair models). Code that hardcodes "paper starts at scanline 64" will have a 16-scanline offset error on the Pentagon and other clones with different border sizes.
>
> The 128K/+2 and +2A/+3 have **63 scanlines of top border** (not 64) because each scanline is 228 T-states (not 224). Paper starts at scanline 63 (T=14,364) and ends at scanline 254 (T=58,140). The 1-scanline offset vs the 48K is a common source of porting bugs. Source: [WoS 128K FAQ](https://worldofspectrum.org/faq/reference/128kreference.htm).

For a complete per-clone comparison including Kay, ATM Turbo, ZX Evolution, and FPGA implementations, see the [Per-Clone Comparison](../../02_hardware/clones/clone_timing.md#per-clone-comparison) table in `clone_timing.md`.

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

    ; Calculate delay: (target_scanline × T_per_line) - 13 T-states
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

**Model considerations**:
- On 128K/+2/+2A/+3, T-states per line is **228** (not 224). Use `LD DE,228` for the per-line multiplier.
- On the Pentagon, T-states per line is 224 (same as 48K), but paper starts at line 48 (not 64).
- On all models, contention affects delay loop timing if the loop executes from contended memory during the paper area. Place timing-critical loops in **uncontended RAM** (`#8000`+ on 48K, any upper bank on 128K).

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

**Not available on all models**: The floating bus is unreliable or absent on the +2A/+3, Pentagon, Scorpion, and most clones. See [floating_bus.md](floating_bus.md) for per-model availability.

### Technique 4: Interrupt Timer — Cross-Platform

For machines without a reliable floating bus (Pentagon, +2A/+3, clones):

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

### Technique 5: Hardware Line Interrupt (Next, TS-Conf)

The ZX Spectrum Next and ZX Evolution (TS-Conf) provide a **programmable line interrupt** that fires at a specific scanline. This eliminates the need for timing loops:

```z80
; ZX Spectrum Next: set line interrupt at scanline 100
    LD   BC,#243B        ; NextReg select port
    LD   A,#22            ; NextReg $22 = line interrupt line
    OUT  (C),A
    LD   BC,#253B        ; NextReg data port
    LD   A,100            ; Fire at scanline 100
    OUT  (C),A
    ; Line interrupt fires automatically at the selected scanline
```

For details, see [interrupt_programming.md](../04_interrupts/interrupt_programming.md) (peripheral interrupt sources).

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

> [!IMPORTANT]
> These exact-T-state loops only work in **uncontended memory** during the **non-display period**. During the paper area on contended-memory models (48K, 128K, +2A/+3), each T-state may be stretched by contention wait states. On the **Pentagon and most clones**, there is no contention, so timing loops work reliably at all times. See [contention_model.md](../03_memory_and_io/contention_model.md) for details.

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
    ; T-states/line = 224, paper starts line 64
    RET

.sync128K:
    ; Floating bus works with minor differences
    HALT
    ; ... floating bus raster lock
    ; T-states/line = 228 (NOT 224!), paper starts line 63 (NOT 64!)
    RET

.syncPentagon:
    ; No floating bus — use HALT + calculated delay
    HALT
    ; T-states/line = 224, paper starts line 48 (NOT 64!)
    ; Zero contention — timing loops are reliable everywhere
    RET

.syncGeneric:
    ; Safe fallback: HALT + delay, no floating bus
    ; Assume 224T/line, paper at line 64
    ; May be wrong — caller should detect the machine first
    HALT
    RET
```

### Machine Detection for Raster Timing

The most common detection method reads a timing-sensitive port and measures the response:

- **FRAMES counter method**: Read the 3-byte FRAMES variable (`#5C78`), wait a known number of T-states, read again. The difference reveals the frame rate → machine type.
- **Floating bus test**: Attempt to read the floating bus pattern. If it matches the 48K reference, it's a ULA machine. If absent, it's a clone.
- **Port `#7FFD` test**: Write to the paging register. If it works, it's a 128K or better. If not, it's a 48K or clone without paging.

For a complete machine detection routine, see [video_frame_pentagon.md](video_frame_pentagon.md#runtime-detection) which includes a detection code example.

---

## Cross-References

- **Per-model frame timing** (scanline maps, contention patterns):
  - [video_frame_48k.md](video_frame_48k.md)
  - [video_frame_128k.md](video_frame_128k.md)
  - [video_frame_plus2a_plus3.md](video_frame_plus2a_plus3.md)
  - [video_frame_pentagon.md](video_frame_pentagon.md)
- **Clone timing comparison** (Scorpion, Kay, ATM Turbo, ZX Evolution, Next, MiSTer): [clone_timing.md](../../02_hardware/clones/clone_timing.md)
- **Floating bus** (ULA data reads for raster sync): [floating_bus.md](floating_bus.md)
- **Border effects** (raster bars, timing-safe writes): [border_effects.md](border_effects.md)
- **Contention model** (how contention affects timing loops): [contention_model.md](../03_memory_and_io/contention_model.md)
- **ULA timing** (hardware-level raster generation): [ula_timing.md](../../02_hardware/original/ula_timing.md)
- **Interrupt programming** (HALT, IM2, hardware line interrupts): [interrupt_programming.md](../04_interrupts/interrupt_programming.md)

## References

### External references

- [Chris Smith — The ZX Spectrum ULA](http://www.zxdesign.info/) — the canonical reference for VSYNC / HSYNC placement, the 64µs line period, and the 69888-T-state 48K frame that underpins every raster-sync technique.
- [Sinclair ZX Specifications](http://problemkaputt.de/zxdocs.htm) — hardware timing diagrams and the canonical INT pulse placement at the top of the VBLank interval.
- [Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip) — annotated 48K ROM showing how the `HALT` instruction is used in standard ROM routines to synchronize with the raster.
- [zx-pk.ru raster sync threads](https://zx-pk.ru) — primary venue for Soviet-clone raster research; documents the Pentagon's 48.83 Hz frame and the detection heuristics used in cross-platform demoscene code.
- [ZEsarUX / UnrealSpeccy documentation](https://sdkcad.free.fr/) — emulator references for the floating-bus read patterns that substitute for direct raster-position polling on the 48K.
