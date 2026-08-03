[← Home](../../README.md) · [Display & Timing](README.md)

# ZX Spectrum Next Video Frame — Configurable Timing, 28 MHz CPU, and a Copper Coprocessor

The ZX Spectrum Next (2017–2020) is an FPGA-based modern recreation of the Spectrum that ships in a desktop case with new hardware features: Layer 2 256-color graphics, hardware sprites, tilemap, DMA, and a **copper coprocessor** for raster-precise register writes. Its video timing is **configurable at runtime** — a single machine can run with 48K, 128K, +2A, or Pentagon timing depending on the mode select.

> [!NOTE]
> This article covers the **video frame timing** of the Next. For hardware architecture (FPGA, Z80N CPU, memory map), see [memory_and_io_next.md](../03_memory_and_io/memory_and_io_next.md). For the copper's instruction set, see [zx_next.md#the-copper-coprocessor](../../02_hardware/newgen/zx_next.md#the-copper-coprocessor). For DMA, sprites, and Layer 2, see [zx_next.md](../../02_hardware/newgen/zx_next.md).

---

## Frame Parameters (ZX Spectrum Next)

```
┌──────────────────────────────────────────────────────────┐
│  ZX Spectrum Next Frame Timing (default 48K mode)        │
├──────────────────────────────────────────────────────────┤
│  FPGA:                   Xilinx Spartan-6 (Issue 2B)     │
│                           or Artix-7 (Issue 4 / KS2)     │
│  CPU core:                Z80N (extended Z80)            │
│                                                          │
│  CPU clock (selectable): 3.5 / 7 / 14 / 28 MHz           │
│  Active CPU speed:        runtime-switchable via #1F      │
│                                                          │
│  T-states per frame:      69,888 (48K mode, at 3.5 MHz)  │
│  Scanlines:               312 (48K mode)                 │
│  T-states per scanline:   224 (48K mode)                 │
│  Frame rate:              50.08 Hz (48K mode)            │
│                                                          │
│  At 7 MHz:                139,776 T-states/frame         │
│  At 14 MHz:               279,552 T-states/frame         │
│  At 28 MHz:               559,104 T-states/frame         │
│                                                          │
│  INT position:            Line 0, T=0 (48K mode)         │
│  Contention:              Configurable per timing mode   │
│                                                          │
│  Copper coprocessor:      Programmable raster sync       │
│  Copper clock:            Same as video timing (~7 MHz)  │
│  Copper instructions:     WAIT + MOVE + long immediate   │
└──────────────────────────────────────────────────────────┘
```

---

## Timing Modes — The Next's Killer Feature

Unlike every other Spectrum clone, the Next lets software select which classic timing model it wants to use **at runtime**, via a port write. This means a single piece of software can adapt to whichever timing it was originally written for.

### Available Timing Modes

| Mode | Frame T-states | Scanlines | Contention | Frame rate | Compatible with |
|---|---|---|---|---|---|
| **48K** (default) | 69,888 | 312 | Strict 6-5-4-3-2-1-0-0 | 50.08 Hz | All original 48K software |
| **128K** | 70,908 | 311 | 1-0-7-6-5-4-3-2 pattern | ~50.02 Hz | All 128K / +2 / Pentagon-targeted software that doesn't need 320 lines |
| **+2A/+3** | 70,908 | 311 | Amstrad gate array contention | ~50.02 Hz | All +2A/+3 software |
| **Pentagon** | **71,680** | **320** | **None** | 48.83 Hz | All Russian demoscene software |

The mode is selected via a port write early in the program's startup. The Next's ROM (NextZXOS) selects 48K mode by default; ESXDOS-based software typically uses 128K mode; Russian software typically requests Pentagon mode.

### Why This Matters

```
On real hardware:
  - A 48K game's race-the-beam multicolor effect works on 48K, breaks on Pentagon
  - A Pentagon demo's no-contention code runs full speed on Pentagon, slows on 48K
  
On the Next:
  - The same 48K game runs correctly in 48K mode
  - Switch to Pentagon mode: the same Pentagon demo runs at correct speed
  - No need for separate builds or even detection — the software requests the timing
```

The Next is the only platform where this is possible. Emulators can do it (they have no fixed timing), but real hardware previously couldn't.

---

## CPU Speed Modes

The Next's CPU runs at one of four speeds selected via port `#1F` bits 5–4:

| Speed | T-states/frame | Notes |
|---|---|---|
| 3.5 MHz (default) | 69,888 | Standard Spectrum speed; all classic software works |
| 7 MHz (2×) | 139,776 | Like Scorpion/Kay/ATM Turbo turbo; ~2× effective speed |
| 14 MHz (4×) | 279,552 | Next-native software; very fast |
| 28 MHz (8×) | 559,104 | Maximum; only for pure-compute work (decrunch, audio DSP) |

```z80
; Set CPU speed to 14 MHz (28 MHz requires NextZXOS or custom core)
LD   BC,#243F           ; Next register select port
LD   A,#07              ; Register 7: CPU speed
OUT  (C),A
LD   BC,#253F           ; Next register data port
LD   A,%00010000        ; Bit 4=1 enables turbo
OUT  (C),A
```

### Speed Caveats

- **Memory access doesn't fully scale** — DRAM/flash access has its own timing constraints; the speedup from 14→28 MHz is less than 2× for memory-heavy loops.
- **I/O timing changes** — but the Next's I/O ports include wait-state insertion for legacy peripherals, so classic 48K-style port access still works correctly.
- **Contention is re-derived** — when in 48K mode with contention enabled, the contention pattern matches the 48K ULA regardless of CPU speed.
- **Copper doesn't change** — the copper runs at video timing, not CPU timing.

---

## The Copper Coprocessor

The Next's copper is a small programmable state machine that runs in parallel with the CPU and can write to hardware registers at exact T-state positions within the frame. It eliminates the need for carefully timed CPU loops for many classic Spectrum effects.

### Copper Programming Model

Two instructions:

| Instruction | Format | Effect |
|---|---|---|
| `WAIT line, T` | `01 LLLLLLLL TTTTTTT` | Wait until raster reaches (line, T) |
| `MOVE port, value` | `0 PPPPPPPP VVVVVVVV` | Write byte `value` to port `port` (in 16-bit copper address space) |
| `STOP` | `0 00000000 00000000` | Halt copper |

A copper program is a flat byte sequence written into the copper's RAM (separate from main RAM). It auto-starts at line 0 of each frame and runs until it executes `STOP` or reaches the end.

### Example: Border color bars without CPU cycles

```
COPPER_DATA:
    DB  %01_000000_0_00000_000       ; WAIT scanline 0, T=0
    DB  %0_0FE_0_00_0000_00          ; MOVE port #FE (border), value BLUE
    DB  %01_011111_0_0000_000        ; WAIT scanline 63, T=0 (paper start)
    DB  %0_0FE_0_00_0000_01          ; MOVE port #FE, value BLACK
    DB  %01_111111_0_0000_000        ; WAIT scanline 255, T=0 (paper end)
    DB  %0_0FE_0_00_0000_10          ; MOVE port #FE, value RED
    DB  %0_0_00_00_00_00_00_00       ; STOP
```

This copper program produces three border bars (blue above paper, black during paper, red below paper) — **zero CPU cost per frame**. The equivalent 48K code would require cycle-counted OUT instructions during every scanline.

### Copper Limits

- **Single register write per cycle** — the copper can do at most one port write per T-state pair
- **Address space is separate** — copper can't access main RAM directly; it writes only to its own register-mapped port space
- **Cannot read** — pure write-only device
- **Tied to video timing** — copper WAIT references the video frame position (line, T), not CPU T-states

For multicolor effects that need to write to ATTR RAM at varying positions, copper alone isn't enough — you still need CPU loops with T-state-counted OUTs. But copper removes a large class of pure register-write effects (palettes, border, sprite positions, scrolling offsets) from the CPU's responsibility.

---

## Layer 2, Tilemap, Sprites — Independent of Base Timing

The Next's three enhanced graphics layers (Layer 2 256-color, hardware sprites, tilemap) all read from their own dedicated video memory and **do not affect the base frame timing**:

- Layer 2 fetches 256×192 bytes per frame from a dedicated RAM region
- Sprites are fetched from a 64 KB sprite pattern memory
- Tilemap reads a 40×32 tile grid plus a 256-entry pattern table

All of this happens in parallel with the standard Spectrum screen fetch. The CPU sees no additional contention from these layers (beyond the base timing-mode contention).

> [!NOTE]
> For details on programming these layers, see [Layer 2](../../02_hardware/newgen/zx_next.md#layer-2-framebuffer), [Sprites](../../02_hardware/newgen/zx_next.md#hardware-sprites), and [Tilemap](../../02_hardware/newgen/zx_next.md#hardware-tilemap) in the New Generation hardware section.

---

## INT Position and ISR Design

INT timing matches 48K exactly when in 48K mode:

```
INT asserted at:   Line 0, T=0
INT duration:      32 T-states
After INT:         14,336 T-states of top border before paper (48K mode)
                   10,752 T-states before paper (Pentagon mode)
```

The Next's ISR pattern is identical to 48K — there is nothing Next-specific about ISR code unless you take advantage of the extra CPU cycles available at higher clock speeds.

### Next-Native ISR Pattern

```z80
; Next ISR running at 14 MHz in 48K timing mode
; Has 4× more T-states available than 48K
music_isr:
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL
    PUSH IX
    PUSH IY
    
    ; At 14 MHz, the entire register-preserve sequence takes
    ; ~150 T-states of CPU time, but only ~37 T-states of wall-clock
    ; frame timing. This gives the ISR nearly the full 14,336 T-states
    ; of frame time for actual work.
    
    LD   HL,music_module
    CALL pt3_play           ; ~3000 T-states at 3.5 MHz = 750 wall-clock
    
    ; Update copper program for next frame's effects
    LD   HL,copper_buffer
    LD   BC,#503F           ; Copper data port
    OTIR                    ; Blast copper program
    
    ; etc.
    
    POP  IY
    POP  IX
    POP  HL
    POP  DE
    POP  BC
    POP  AF
    EI
    RETI
```

At 14 MHz with 48K timing, the CPU has 279,552 T-states per frame — about 4× the 48K's 69,888. That's enough to run a full AY music player, update sprites, decompress a screen region, and run game logic in a single frame.

---

## Hardware Scrolling and the Copper

The Next's `#xx` horizontal-scroll and vertical-scroll registers can be updated by the copper on a per-scanline basis. This enables:

- **Smooth per-line horizontal scrolling** — copper updates H-SCROLL every line, producing pixel-precise scroll offsets that aren't possible on classic hardware
- **Vertical parallax** — different lines scroll at different rates
- **Scanline-synchronized palette swaps** — copper writes to Layer 2 palette registers, producing per-line 256-color gradients

These effects require precise copper programming — see [zx_next.md#the-copper-coprocessor](../../02_hardware/newgen/zx_next.md#the-copper-coprocessor) for the full copper programming reference.

---

## Detecting the Next at Runtime

```z80
; Detect ZX Spectrum Next
; Method: probe the Next's machine ID register
DetectNext:
    LD   BC,#243B           ; Next register select port
    LD   A,#00              ; Register 0 = machine ID
    OUT  (C),A
    INC  B                  ; Port changes from #243B to #253B
    IN   A,(C)              ; Read machine ID
    
    ; Hardware version byte:
    ;   #0A = KS1 (Issue 2B, Spartan-6)
    ;   #0B = KS2 (Issue 4, Artix-7)
    ;   Other values = not a Next
    
    CP   #0A
    JR   Z,isNextKS1
    CP   #0B
    JR   Z,isNextKS2
    
notNext:
    ; Fall through to classic Spectrum code
    RET
    
isNextKS1:
isNextKS2:
    ; Next detected — enable extended features
    RET
```

This is **reliable** because the machine ID register exists only on real Next hardware (and Next-compatible FPGA cores like the MiSTer Next core). Classic Spectrums return an undefined value from port `#253B` that is never `#0A` or `#0B`.

---

## What Gets Easier on the Next

1. **No more cycle-counted multicolor loops** for register-write effects — copper handles them in parallel with CPU.
2. **4×–8× CPU speed** available on demand — most "tight" frame budgets become trivial.
3. **Layer 2 / sprites / tilemap** offload graphics work from the CPU entirely.
4. **DMA** handles memory copies, pattern fills, and port I/O without CPU cycles.
5. **Timing-mode flexibility** means you can support 48K, 128K, +2A, and Pentagon from one binary.

### What Still Requires Classic Techniques

1. **ATTR-based multicolor** (8×1 pixel color) still requires CPU loops writing to screen RAM — copper doesn't have main-RAM access.
2. **Floating bus tricks** for raster sync are still needed if you don't want to commit to copper programming.
3. **Contention-dependent timing** in classic 48K mode is fully emulated — old code behaves exactly as on real 48K.

---

## Cross-References

- [Next memory map and I/O ports](../03_memory_and_io/memory_and_io_next.md) — full hardware reference (MMU, port decoding, 8K paging)
- [Next audio subsystem](../../06_sound/hardware/zx_next_audio.md) — 3×AY + beeper + DMA sample playback
- [NextZXOS](../../04_operating_systems/nextzxos.md) — Next's OS, derived from ESXDOS
- [Video frame 48K](video_frame_48k.md) — base reference for the timing mode the Next defaults to
- [Video frame Pentagon](video_frame_pentagon.md) — the Next can emulate this exactly
- [Video frame +2A/+3](video_frame_plus2a_plus3.md) — another mode the Next can emulate
- [Video frame comparison](video_frame_comparison.md) — all models side-by-side
- [Cycle-exact accuracy](../../11_emulation/software/cycle_exact_accuracy.md) — how the Next's configurable timing solves emulator-host sync issues

---

## Primary Sources

- **ZX Spectrum Next Official Documentation** — [zxnext.io](https://zxnext.io). The TBBlue board specification, hardware reference manual, and per-feature technical documents.
- **ZX Spectrum Next Register Reference** — the canonical list of all Next-specific I/O ports (`#243B`/`#253B` register-indexed access) and their effects.
- **NextBASIC Manual** — chapter on copper programming and the WAIT/MOVE instruction format.
- **CSpect emulator** ([cspect.org](https://cspect.org)) — primary development emulator for the Next, implements all timing modes and the copper.
- **ZEsarUX** — full Next timing emulation including 48K/128K/+2A/Pentagon mode switching.
- **The "Definitive ZX Spectrum Next Tester" ROM** — community test suite that verifies copper timing, CPU speed switching, and per-mode contention behavior on real hardware.
