[← Home](../../README.md) · [Interrupts](README.md)

# Race the Beam — Multicolor Effects via Cycle-Counted ISRs

The ZX Spectrum's display hardware is attribute-based: each 8×8 pixel cell carries one INK color, one PAPER color, one BRIGHT bit, and one FLASH bit. This produces the machine's signature look — and its most derided limitation, **attribute clash**. Demoscene coders refused to accept the 8×8 vertical granularity and engineered a workaround: change the attribute bytes **while the CRT beam is mid-frame**, so different rows of the same 8×8 cell receive different colors. The result is **8×1 pixel color resolution** — sixty-four times finer than the hardware specifies.

This technique, called **race the beam** (or **multicolor**, or **color-per-line**), is the most timing-critical code that exists on the Spectrum. The CPU has exactly 224 T-states per scanline on the 48K, and a single `LDIR`, a single `CALL`, a single wasted `NOP` in the wrong place is the difference between a clean effect and a visible glitch. This article covers the cycle-budgeting math, the synchronization strategies that work, the published engines that solve the problem, and a complete worked example annotated to the T-state.

> [!NOTE]
> This article assumes you already understand beam position calculation and synchronization primitives. Those topics live in [raster_timing.md](../05_display_and_timing/raster_timing.md) (beam math, sync techniques) and [floating_bus.md](../05_display_and_timing/floating_bus.md) (the floating-bus hardware quirk). Here we focus on **synthesizing those primitives into actual on-screen effects**.

---

## Why Race the Beam

### The 8×8 Constraint, Reframed

Hardware reality: the ULA reads one attribute byte per 8-pixel column per 8 scanlines. Whatever byte sits at `#5800 + (row * 32) + col` when the beam crosses scanline `64 + row * 8` is what gets displayed for the entire 8-row cell.

Software loophole: the ULA reads that attribute byte **once**, at a specific T-state, then reuses it for the next 7 scanlines. If the CPU **overwrites the byte after the ULA's read but before the next cell's read**, the next 8-row strip will use the new value. Push this to the extreme — change the attribute **every scanline** — and you have 8×1 color.

The constraint is not "the hardware can't do it." The constraint is "the CPU must hit a specific T-state window, every scanline, for 192 scanlines, without drift."

### Why This Is Hard

A scanline on the 48K is **224 T-states long** (3.5 MHz / 15.625 kHz horizontal sync). The attribute area is 32 bytes wide. To rewrite all 32 attributes of one row, you need at minimum:

| Operation | T-states |
|---|---|
| 32 × `LD (HL),n` (immediate store) | 32 × 13 = 416 (too slow!) |
| 32 × `LD (HL),r` (register store) | 32 × 7 = 224 (entire scanline budget) |
| 32 × `LDD (HL),A` + `INC L` (pair) | 32 × 11 = 352 (too slow) |
| 16 × `PUSH` to attribute address (2 bytes each) | 16 × 11 = 176 (fast enough) |

The stack-push technique — point `SP` at the attribute row, then `PUSH` 16 register pairs — is the standard solution. It costs 176 T-states for the writes, leaving 48 T-states for setup, incrementing to the next row's address, and any per-row logic. There is no slack.

### What Multicolor Buys You

| Resolution | Pixels per color cell | Use case |
|---|---|---|
| Standard attribute | 8 × 8 | Stock Spectrum — every commercial game |
| 8 × 2 multicolor | 8 × 2 | Safe effect: 2 scanlines of jitter tolerance |
| 8 × 1 multicolor | 8 × 1 | Maximum resolution: cycle-exact code required |
| 8 × 1 + per-pixel dithering | 1 × 1 (effective) | Used by some 2010+ demos (BIFROST* Engine) |

---

## T-State Budget

### Per-Scanline Budget

| Model | T-states / scanline | Implication |
|---|---|---|
| 48K | 224 | Reference target; most engines assume this |
| 128K / +2 | 228 | 4 extra T-states per scanline (different ULA timing) |
| +2A / +3 | 228 | Same horizontal timing as 128K, different contention model |
| Pentagon | 224 | Same as 48K horizontally, but zero contention and 320 scanlines |
| Scorpion | 224 | Same; +9 T-states horizontal shift in some revisions |
| ZX Spectrum Next (3.5 MHz mode) | 224 / 228 / 228 / 224 | Configurable per video mode |

Code that assumes 224 T-states per scanline breaks on 128K machines because the per-scanline timing window is 4 T-states wider — your writes happen "too early" and land on the previous attribute row.

### Per-Character-Row Budget

An 8-scanline character row at 224 T-states/line gives **1,792 T-states** between attribute-row boundaries. Within that budget you must:
1. Write the 32 attributes for the current row (~176 T-states with `PUSH`)
2. Advance to the next row's attribute address (~20 T-states)
3. Optionally fetch the next row's color data from a buffer (~30 T-states)
4. Wait out the remaining 7 scanlines (1,566 T-states) doing useful work or `NOP` padding

The wait is the killer. You cannot simply `HALT` — `HALT` waits for an interrupt, not a scanline. You must either:
- Run a calibrated `DJNZ` loop (waste cycles, but predictable)
- Do useful work like music playback or sprite updates (advanced — see [im2_effects.md](im2_effects.md))
- Use a hardware line interrupt (Next/TS-Conf only — see [im2_advanced.md](im2_advanced.md))

---

## Synchronization Strategies

Five techniques exist, in increasing order of precision and complexity.

### Strategy Comparison Matrix

| Strategy | Precision | Works on 48K | Works on +2A/+3 | Works on Pentagon | CPU cost |
|---|---|---|---|---|---|
| `HALT`-based | ±10-20 T-states | Yes | Yes | Yes | Low |
| Floating-bus sync | ±1 T-state | Yes | No (use +2A variant) | No | Medium |
| Port-`#FF` sync (Sidewize) | ±2 T-states | Yes | Yes | Yes | Medium |
| Hardware line interrupt | ±1 T-state | No | No | No (Next/TS-Conf only) | Very low |
| Copper coprocessor | Exact (hardware) | No | No | No (Next only) | Zero |

### Strategy 1: HALT-Based (Entry Level)

`HALT` puts the CPU to sleep until the next maskable interrupt. On 48K, the interrupt fires at T-state 0 of scanline 0 (top border start). Code after `HALT` begins executing ~13 T-states later (the interrupt acknowledge cycle).

```z80
    HALT                  ; CPU sleeps until INT
    ; T-state ≈ 13 (IM1) or 19 (IM2) after INT assertion
    ; Remaining jitter: depends on where HALT was in the main loop
```

**Jitter**: the CPU finishes whatever instruction was executing when INT fired, then acknowledges. Worst case: a 21-T-state `LDIR` block was midway through. This gives ±10-20 T-states of jitter from frame to frame.

**Use case**: raster bars in the border area where the beam position tolerance is one full scanline (224 T-states). Inside the paper area doing 8×1 work, HALT alone is not enough — you need a fine-tuning step.

```z80
    HALT
    ; Now do a calibrated delay to reach the target scanline
    LD   B,32             ; 32 iterations of DJNZ = 448 T-states (2 scanlines)
.delay:
    DJNZ .delay           ; 13T per iteration (3T for last)
    ; Now near scanline 2-3 — begin effect
```

This is what most simple raster-bar and border-effect demos use. It works in the border because the border has no contention and a 224-T-state tolerance.

### Strategy 2: Floating-Bus Sync

The 48K's floating bus returns the byte the ULA just fetched from screen memory. The ULA fetches one attribute byte per scanline at a predictable T-state. By polling `IN A,(#FF)` in a tight loop, you can detect when the ULA has just read a specific attribute value — and thus which scanline the beam is on.

```z80
; Wait for the ULA to fetch a specific attribute (e.g. #47 = white-on-red bright)
WaitForAttr:
    IN   A,(#FF)          ; 11T
    CP   #47              ; 7T  -- total 18T per poll iteration
    JR   NZ,WaitForAttr   ; 12/7T
    ; When we exit, the ULA just read #47 from screen
    ; Beam is on the scanline that contains that attribute byte
    RET
```

**Precision**: ±1 T-state. Each poll iteration is 18 T-states; if the byte appears mid-iteration, you catch it on the next poll, which is at most 18 T-states later. With careful code, you can pin the beam to a 4-T-state window.

**Caveat — +2A/+3**: the floating bus behaves differently on the Amstrad gate array. Some T-states return `#FF` instead of the ULA's fetched byte. The classic floating-bus sync loop **does not work**. The workaround discovered by Ast A. Moore around 2015 (about 30 years after the +2A shipped) uses a different attribute value with bit 0 set and reads from a different port — see the code in the cross-references.

**Caveat — Pentagon**: there is no ULA contention and no floating bus. The technique is completely unavailable.

For the full per-model behavior table, see [floating_bus.md](../05_display_and_timing/floating_bus.md).

### Strategy 3: Port-`#FF` Sync (the Sidewize Trick)

Some commercial games (notably Sidewize and Crosswize by Steve Wetherill) use a different sync method: read from a partially-decoded I/O port in a tight loop. Because I/O reads on the Spectrum take a fixed number of T-states and the address bus changes predictably, this can be made into a deterministic timer without relying on the floating bus.

The Sidewize approach reads port `#40FF` — a Kempston joystick mirror — and uses the timing of the read cycle itself as a sync marker:

```z80
; Simplified Sidewize sync (no floating bus dependency)
    HALT                  ; Coarse sync to INT
    LD   BC,#40FF         ; Kempston joystick port
.sync:
    IN   A,(C)            ; 20T — fixed duration
    ; Loop until a known number of cycles have elapsed
    DEC  DE               ; 6T
    LD   A,D              ; 4T
    OR   E                ; 4T
    JR   NZ,.sync         ; 12/7T
    ; Beam is now at a known position relative to INT
```

The advantage is that this works on every model — there is no ULA dependency. The disadvantage is that you must calibrate the loop count per model.

### Strategy 4: Hardware Line Interrupt (Next, TS-Conf)

The ZX Spectrum Next and TS-Conf configuration of the ZX Evolution provide a programmable scanline interrupt via hardware register. You write a scanline number to the register, and the hardware fires an interrupt when the beam reaches that scanline.

```z80
; Next: set line interrupt at scanline 64 (first paper line)
    LD   BC,#243B         ; NextReg select port
    LD   A,#22            ; NextReg #22 = line interrupt line
    OUT  (C),A
    LD   B,#25            ; NextReg data port
    LD   A,64             ; scanline 64
    OUT  (C),A
    ; From now on, an interrupt fires at scanline 64 every frame
```

This eliminates the need for cycle-counted delays entirely. See [im2_advanced.md](im2_advanced.md) for the full Next interrupt model.

### Strategy 5: Copper Coprocessor (Next Only)

The Next includes a tiny programmable state machine called the **copper** that can write hardware registers at specific beam positions with zero CPU cost. Where you would normally write an ISR to change a palette entry mid-frame, you program the copper instead and the CPU is completely free.

```text
Copper program (32 instructions max):
  WAIT 0,64        ; wait for beam at column 0, scanline 64
  MOVE palette[0],#03
  WAIT 0,72        ; scanline 72
  MOVE palette[0],#07
  ...
```

The copper is not a general-purpose processor — it can only `WAIT` and `MOVE`. For per-scanline attribute changes you still need CPU-driven multicolor (because attribute RAM is not a copper-writable register). For palette changes, layer 2 bank switches, and sprite priorities, the copper is strictly better than ISR code.

---

## The BIFROST* Engine

The BIFROST* Engine, written by Einar Saukas in 2012, is the canonical open-source multicolor engine for the 48K Spectrum. It demonstrates that 8×1 multicolor is achievable in a reusable library, not just hand-crafted per demo.

### Design Constraints

| Parameter | Value |
|---|---|
| Display area | 18 × 18 character cells (144 × 144 pixels) |
| Tile size | 16 × 16 pixels (4 × 4 attribute cells) |
| Tile count | 9 rows × 9 columns = 81 tile slots |
| Frame rate | 50 Hz (one tile pipeline pass per frame) |
| Memory | ~2 KB code + ~3 KB tile data |
| Compatibility | 48K, 128K, +2, +2A, +3 |

### The Tile Pipeline

BIFROST* updates **one tile row per frame**, cycling through 9 tile rows. Each tile row is 4 scanlines tall (16 pixels ÷ 4 = 4 rows per pass = 4 frames to redraw one tile row). The pipeline:

1. At frame N, BIFROST* redraws tile row `(N mod 9)`
2. Each redraw is a stack-pushed attribute update of 4 rows × 9 tiles × 2 columns = 72 attribute bytes
3. The 8 scanlines of each row are rewritten during the beam's pass through that row's screen position

The key insight: **BIFROST* does not update the entire screen every frame**. It updates 1/9th of it, accepting a 9-frame latency for any tile change. This is invisible at 50 Hz (180 ms) for animation but would be unacceptable for a game with frame-perfect collisions.

### Why It Works on Stock 48K

BIFROST* runs in IM2 with an ISR that does nothing more than increment a frame counter. The actual attribute rewriting happens in the **main loop**, not the ISR. The main loop:

1. `HALT` for frame sync
2. Compute which tile row to update this frame
3. Set up register pairs with precomputed attribute data
4. Run a cycle-counted loop that pushes attributes to screen as the beam passes
5. Return to step 1

The cycle-counted loop is hand-tuned to take exactly 224 T-states per iteration (one scanline). There is no early-exit, no branch, no flexibility — it is more like hardware than software.

### BIFROST*2

The 2016 successor (also by Saukas) extended the display area to 20 columns × 22 rows at the cost of stricter timing requirements. The original BIFROST* remains the recommended starting point for studying how these engines work.

---

## Worked Example — 16-Row Attribute Bar

This example redraws 16 consecutive attribute rows with 16 different colors, producing horizontal color bars at 8×1 resolution in the top portion of the paper area. The code targets the 48K Spectrum.

### Setup

```z80
    ORG  #8000

Start:
    ; --- Install IM2 handler ---
    DI
    LD   A,#FE
    LD   I,A
    LD   HL,#FE00
    LD   (HL),#80          ; All vectors → #8080
    LD   DE,#FE01
    LD   BC,#0100          ; 256 more bytes (257 total)
    LDIR
    IM   2
    EI

    ; --- Initialize frame flag ---
    XOR  A
    LD   (frame_flag),A

    ; --- Main loop ---
MainLoop:
    HALT                   ; Wait for INT
    LD   A,(frame_flag)
    OR   A
    JR   Z,MainLoop        ; (shouldn't happen)
    XOR  A
    LD   (frame_flag),A

    CALL DrawBars
    JR   MainLoop

; --- IM2 ISR ---
    ORG  #8080
ISR:
    EX   AF,AF'
    LD   A,1
    LD   (frame_flag),A
    EX   AF,AF'
    EI
    RET

frame_flag:  DB  0
```

### DrawBars — Cycle-Counted Attribute Push

```z80
DrawBars:
    ; Sync to start of paper area (scanline 64) using floating bus
    ; ISR exits at T-state ~19, we need to wait until T-state 14336
    ; (64 scanlines × 224 T-states)
    ;
    ; First, coarse wait via HALT-equivalent delay loop
    LD   BC,400             ; ~5720 T-states
.coarse:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.coarse

    ; Now fine-sync with floating bus
    ; Wait until ULA fetches attribute byte at row 0 (scanline 64)
.fb_loop:
    IN   A,(#FF)
    CP   #07                ; ATTR byte we expect (white-on-black, dark blue paper)
    JR   NZ,.fb_loop

    ; --- The beam is now at scanline 64 ---
    ; --- Begin cycle-counted attribute push ---
    ; We have exactly 224 T-states per scanline
    ; PUSH layout: 16 PUSHes = 176 T-states, leaves 48 for loop overhead

    LD   HL,#5800           ; First attribute row address
    LD   BC,attr_table      ; Source: 16 bytes per row × 16 rows

.row_loop:
    ; --- Point SP at the attribute row ---
    LD   SP,HL              ; 10T
    INC  H                  ; 4T -- advance to next row (HL += 256)
    ; Note: attribute rows are 256 bytes apart in the Speccy's nonlinear layout,
    ; but only for the first 8 rows of each 1/3 of the screen. Cross-third
    ; transitions need HL adjustment. For 16 rows we stay within the top third.
    PUSH BC                 ; 11T -- placeholder, real code uses index into attr_table
    ; ... load 8 register pairs from attr_table + offset ...
    ; ... 16 × PUSH = 176T ...
    ; --- Total per row: 10 + 4 + 176 = 190T, plus loop control ~20T = 210T ---
    ; --- Remainder to 224: 14T of NOPs or useful work ---
    NOP
    NOP
    NOP
    DJNZ .row_loop          ; 13/8T

    ; Restore SP to safe RAM
    LD   SP,#FF00
    RET

attr_table:
    DB   #02,#02,#02,#02,#02,#02,#02,#02,#02,#02,#02,#02,#02,#02,#02,#02
    DB   #06,#06,#06,#06,#06,#06,#06,#06,#06,#06,#06,#06,#06,#06,#06,#06
    ; ... 14 more rows ...
```

### T-State Budget Per Row (Annotated)

| Operation | T-states | Cumulative |
|---|---|---|
| `LD SP,HL` (set stack to attr row) | 10 | 10 |
| `INC H` (advance to next row) | 4 | 14 |
| `LD DE,(BC)` etc. (load regs from table) | ~40 | 54 |
| `EX DE,HL` × 8 (cycle through regs) | 32 | 86 |
| 16 × `PUSH` (write 32 bytes) | 176 | 262 |
| `DJNZ .row_loop` (loop control) | 13 | 275 |
| **Total per iteration** | **275** | — |

**Problem**: 275 T-states per iteration exceeds the 224 T-state scanline budget. The example above is intentionally wrong — it illustrates the budgeting trap.

The actual fix is one of:
- **Drop registers**: load only 8 bytes per row (4 PUSHes), update half the screen per frame, alternate halves.
- **Pre-shift data**: store attribute bytes in registers before the timing-critical section, so no `LD` happens inside.
- **Use SMC**: self-modifying code to bake the bytes directly into `PUSH` operands.

Here is a corrected version using preloaded registers:

```z80
    ; --- Registers preloaded before this section ---
    ; AF, BC, DE, HL, BC', DE', HL' all hold attribute pairs
    ; We use shadow registers + EXX to fit 16 bytes worth of PUSHes

.row_loop:
    LD   SP,HL              ; 10T
    INC  H                  ; 4T
    EXX                     ; 4T -- swap to shadow set for more PUSHes
    PUSH AF                 ; 11T
    PUSH BC                 ; 11T
    PUSH DE                 ; 11T
    PUSH HL                 ; 11T -- 8 bytes written
    EXX                     ; 4T
    EX   AF,AF'             ; 4T
    PUSH AF                 ; 11T
    PUSH BC                 ; 11T
    PUSH DE                 ; 11T
    PUSH HL                 ; 11T -- 16 bytes
    ; ... 4 more PUSHes from IX/IY for 32 bytes total ...
    PUSH IX                 ; 15T
    PUSH IY                 ; 15T
    ; 16 bytes × 2 = 32 bytes total: row complete
    ; T-states so far: 10 + 4 + 4 + 11*4 + 4 + 4 + 11*4 + 15*2 = 162T
    ; Loop overhead: 13T for DJNZ, 4T for DEC counter = ~17T
    ; Total: 179T, leaving 45T of slack per scanline
    LD   A,(row_count)     ; 13T
    DEC  A                  ; 4T
    LD   (row_count),A     ; 13T
    JR   NZ,.row_loop      ; 12/7T

row_count:  DB 16
```

With 45 T-states of slack, you have room for: a `LD` to fetch the next row's color from a buffer, a `CP` to check for end-of-effect, or a `CALL` to a music player (though the music player probably costs more than 45 T-states — see [im2_disk_music.md](im2_disk_music.md) for ISR budgeting against a music player).

---

## Per-Model Timing Differences

### Decision Tree

```text
Target hardware?
├── 48K only
│   └── Use floating-bus sync, 224T/scanline, full ISR budget available
├── 48K + 128K
│   └── Use floating-bus sync with model-detection branch; 128K uses 228T/scanline
├── 48K + 128K + +2A/+3
│   └── Branch: floating-bus on 48K/128K, Ast A. Moore variant on +2A/+3
├── Includes Pentagon
│   └── Branch: HALT + DJNZ loop on Pentagon (no floating bus, no contention)
├── Includes Next
│   └── Use hardware line interrupt or copper for max precision, fallback for compat
└── Cross-platform max portability
    └── HALT + DJNZ everywhere; accept 8×2 resolution; write per-model calibrated delay tables
```

### Per-Model Quick Reference

| Model | T-states / line | Sync method | Contention |
|---|---|---|---|
| 48K | 224 | Floating bus or port-`#FF` | Standard ULA |
| 128K / +2 | 228 | Floating bus (slight shift) | Same ULA, different bank layout |
| +2A / +3 | 228 | Ast A. Moore variant | Gate array (different pattern) |
| Pentagon | 224 | HALT + DJNZ only | None |
| Scorpion | 224 (some revisions +9) | HALT + DJNZ | Revision-dependent |
| Next (3.5 MHz) | 224 / 228 | Hardware line interrupt / copper | Configurable |
| Sprinter | Variable (SVGA timing) | Not supported well | None |

### Per-Model Calibration

For a delay-loop-based effect targeting multiple models, you need per-model loop constants:

```z80
; Per-model delay constant
model_48k:    EQU  200     ; 200 iterations of DJNZ ≈ 2600 T-states
model_128k:   EQU  208     ; 4 more iterations to absorb the wider scanline
model_pent:   EQU  200     ; Same as 48K horizontally
```

Detect the model at startup (see [contention_model.md](../03_memory_and_io/contention_model.md) for the standard detection techniques) and select the appropriate constant.

---

## Antipatterns

### Naive `DJNZ` Delay Loops in Contended Memory

```z80
    ; BAD: delay loop placed in contended memory
    ORG  #5000              ; #5000-#7FFF = contended on 48K during paper
.delay:
    DJNZ .delay             ; 13T nominal, but 13-19T when contended
```

The contention pattern adds **variable** delay depending on which T-state of the scanline the CPU is on. Your carefully calibrated 200-iteration loop becomes 200–230 iterations worth of T-states, ruining beam sync.

**Fix**: place timing-critical code in uncontended memory (`#8000`–`#FFFF` on 48K).

### Ignoring Contention for Screen Writes

```z80
    ; BAD: assumes every PUSH takes 11T
    PUSH HL                 ; 11T in uncontended, 11-15T if SP points at screen
```

When `SP` points into contended memory (which it must for screen writes), every `PUSH` and `POP` is subject to contention. The 11-T-state `PUSH` becomes 12, 13, 14, or 15 T-states depending on the beam position.

**Fix**: include contention correction in your T-state budget. On 48K, the worst-case contention delay per memory access is 6 T-states. Plan for `PUSH = 11-17T` and budget for the worst case.

### Missing +2A/+3 Floating-Bus Fallback

Many open-source multicolor demos work on 48K and 128K but crash or glitch on +2A/+3 because the floating bus returns `#FF` in places where 48K would return a screen byte. The sync loop spins forever waiting for an attribute value that never appears.

**Fix**: detect +2A/+3 at startup and switch to the Ast A. Moore variant:

```z80
    ; Detect +2A/+3 by reading the banking port
    XOR  A
    LD   BC,#7FFD
    OUT  (C),A             ; Try to write a known value
    ; On +2A/+3, port #1FFD also exists; on 128K/+2 it doesn't
    LD   BC,#1FFD
    IN   A,(C)             ; Reads back #FF on 128K, valid data on +2A/+3
    CP   #FF
    JR   Z,.model_128k
    JR   .model_plus2a
```

### Using `HALT` for Fine Sync

`HALT` only wakes on interrupt — it does not have a "wake up at scanline N" mode. Code that does:

```z80
    ; BAD: trying to use HALT for scanline sync
    HALT                   ; Wakes at scanline 0
    ; ... some code ...
    HALT                   ; Wakes at scanline 0 of the NEXT frame, not 224T later
```

The second `HALT` sleeps until the next INT — a full frame later. Use a delay loop, not `HALT`, for sub-frame positioning.

### Assuming Stack Safety During Effect

Setting `SP` to point at screen memory is mandatory for the stack-push technique. But if an interrupt fires during the effect, the ISR's stack operations corrupt your carefully-timed writes.

```z80
    ; BAD: ISR can fire during the PUSH loop
    LD   SP,#5800
    PUSH HL                 ; 11T
    ; If INT fires here, ISR pushes return address to #57FE
    PUSH DE                 ; Now SP has been corrupted by ISR prologue/epilogue
```

**Fix**: disable interrupts during the timing-critical section:

```z80
    DI                     ; No interrupt can disturb the PUSH sequence
    LD   SP,#5800
    PUSH HL : PUSH DE : PUSH BC : PUSH AF
    PUSH HL : PUSH DE : PUSH BC : PUSH AF
    ; ... etc ...
    LD   SP,safe_stack     ; Restore
    EI                     ; Re-enable after critical section
```

This costs 8 T-states total (4 for `DI`, 4 for `EI`) but eliminates an entire class of bugs.

---

## Cross-References

- **[floating_bus.md](../05_display_and_timing/floating_bus.md)** — The hardware quirk that makes fine-grained raster sync possible on 48K/128K
- **[raster_timing.md](../05_display_and_timing/raster_timing.md)** — Beam position calculation and synchronization primitives
- **[contention_timing.md](../05_display_and_timing/contention_timing.md)** — Per-T-state contention delay tables needed for budgeting PUSH loops
- **[video_frame_48k.md](../05_display_and_timing/video_frame_48k.md)** — Reference 48K frame timing (224T/line, scanline layout)
- **[border_effects.md](../05_display_and_timing/border_effects.md)** — Simpler effects that work in the border area (no contention)
- **[interrupt_programming.md](interrupt_programming.md)** — Foundational IM1/IM2 setup, ISR design patterns
- **[im2_effects.md](im2_effects.md)** — Demoscene IM2 effects catalog (per-scanline palettes, line-sync dispatchers)
- **[im2_advanced.md](im2_advanced.md)** — Hardware line interrupt and copper coprocessor on Next / TS-Conf

## Sources

- [Einar Saukas](https://github.com/einar-saukas), *BIFROST* Engine documentation* (2012) — open-source multicolor engine, reference implementation
- Dave "R-Tape" Hughes, *BIFROST2 Engine* (2016) — extended display area
- Steve Wetherill, *Chasing the raster on the ZX Spectrum in Sidewize* (2022) — port-`#FF` sync technique
- Ast A. Moore, *The Definitive Programmer's Guide to Using the Floating Bus Trick on the ZX Spectrum* — +2A/+3 floating-bus workaround
- [Gasman, *Compatibility](https://zxpress.ru/): An open letter to the Russian scene* (Subliminal Extacy #3, zxpress.ru) — vector table placement, multicolor cross-platform notes
- rejunity, *zx-racing-the-beam* (GitHub) — open-source experiments with cycle-exact border opening

