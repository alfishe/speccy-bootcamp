[← Home](../../README.md) · [Memory & I/O](README.md)

# ZX Spectrum 16K / 48K — Memory Map and I/O Ports

The Z80 CPU has a 16-bit address bus — it can address **65,536 bytes (64 KB)** of memory. The ZX Spectrum 48K uses the entire 64 KB address space without paging: the lower 16 KB is ROM, the upper 48 KB is RAM. The 16K model is identical except RAM stops at `#7FFF` (only 16 KB of RAM fitted).

The 48K has **one I/O port that does almost everything**: `#FE` controls the border color, speaker output, tape signal, and keyboard reading — all through a single partial-decoded address.

> [!NOTE]
> This article covers the **48K/16K memory layout and I/O ports**. For 128K paging and bank switching, see [memory_and_io_128k.md](memory_and_io_128k.md). For I/O port decoding concepts (partial decoding, masks, conflicts), see [io_port_decoding.md](io_port_decoding.md).

---

## Memory Map Overview

| Address range | Size | Contents | Notes |
|---|---|---|---|
| `#0000`–`#3FFF` | 16384 | ROM (16 KB) | Read-only, Sinclair BASIC + editor |
| `#4000`–`#57FF` | 6144 | Screen pixel buffer (PIX) | 256×192 pixels, 1 bpp, nonlinear layout |
| `#5800`–`#5AFF` | 768 | Attribute file (ATTR) | 32×24 cells, 1 byte each (INK/PAPER/BRIGHT/FLASH) |
| `#5B00`–`#5BFF` | 256 | Printer buffer | Unused if no printer attached |
| `#5C00`–`#5CB5` | 182 | System variables | ROM workspace, flags, pointers |
| `#5CB6`–`#5CCF` | 26 | Channel information | Channel definitions (K, S, P, R) |
| `#FF58`¹ | — | Stream data | 16 streams × 2 bytes |
| `#5D00`–`#FF57` | — | BASIC program area ↕ Free RAM / machine code | Grows upward (LIST) |
| `#FF58`² | — | UDG area (optional) | Grows downward from RAMTOP |

¹ Exact address depends on BASIC program size and number of variables.
² RAMTOP defaults to `#FF58` on 48K, `#7FFF` on 16K.

---

## I/O Port — #FE (ULA Control)

The 48K has **one hardware port** that the programmer uses directly. Port `#FE` (decoded by A0=0 — see [io_port_decoding.md](io_port_decoding.md)) controls four functions simultaneously:

```
OUT (#FE), A — write to ULA control port:

  Bit   7  6  5  4  3  2  1  0
      ┌────┬────┬────┬────┬────┬────┬────┬────┐
      │ x  │ x  │ x  │ x  │B2  │B1  │B0  │EAR │
      └────┴────┴────┴────┴────┴────┴────┴────┘

  Bit 0 (EAR):    MIC output signal (1 = high, 0 = low)
                  Used for tape SAVE — modulates the MIC socket
                  Also controls the internal speaker on 48K
  Bits 1–3 (B0–B2): Border color (0–7)
                  Determines the color of the border area around the screen
  Bits 4–7:       Unused (should be 0 on write)
```

```
IN A, (#FE) — read from ULA port:

  Bit   7  6  5  4  3  2  1  0
      ┌────┬────┬────┬────┬────┬────┬────┬────┐
      │EAR │ x  │ x  │ x  │R4  │R3  │R2  │R1  │
      └────┴────┴────┴────┴────┴────┴────┴────┘

  Bit 7 (EAR):    EAR input signal (from tape or external source)
  Bits 1–4 (R1–R4): Keyboard matrix row result
  Bit 0:          Always 1 (pull-up resistor)
  Bits 5–6:       Floating (undefined, varies by machine)
```

### Border Color

The border is the area outside the 256×192 pixel display. Setting the border color:

```z80
; Set border to blue (color 1)
LD   A,#01            ; Blue
OUT  (#FE),A          ; Write to ULA port

; Border only supports 8 colors (0-7), no BRIGHT flag
LD   A,#06            ; Yellow
OUT  (#FE),A
```

> [!WARNING]
> Every `OUT (#FE), A` writes ALL bits — border color AND EAR output. If you toggle the border rapidly (for raster effects or beeper music), the EAR output will also toggle. This is why border color changes during tape loading cause buzzing on the MIC output.

For timing-precise border changes (raster bars), see [border_effects.md](../05_display_and_timing/border_effects.md).

### Keyboard Reading

The keyboard is read through the same `#FE` port, combined with address line selection:

```
Keyboard matrix: 8 half-rows × 5 keys each

Address    Low bit  Half-row    Keys (bit 0 = rightmost key listed)
──────────────────────────────────────────────────────────────────
#FEFE      A0=0     Row 7       SHIFT, Z, X, C, V
#FDFE      A1=0     Row 6       A, S, D, F, G
#FBFE      A2=0     Row 5       Q, W, E, R, T
#F7FE      A3=0     Row 4       1, 2, 3, 4, 5
#EFFE      A4=0     Row 3       0, 9, 8, 7, 6
#DFFE      A5=0     Row 2       P, O, I, U, Y
#BFFE      A6=0     Row 1       ENTER, L, K, J, H
#7FFE      A7=0     Row 0       SPACE, SYM SHIFT, M, N, B
```

```z80
; Check if SPACE is pressed (row 0, bit 0)
IN   A,(#7FFE)       ; Read half-row 0
BIT  0,A             ; Bit 0 = SPACE
JR   Z,space_pressed ; Z flag set = key pressed (active low)

; Read all 8 half-rows into a buffer
LD   HL,keyBuffer
LD   B,#FE           ; Starting address low byte (row 7)
LD   C,8             ; 8 rows
.readLoop:
    IN   A,(B)       ; Read current row
    CPL              ; Invert (now 1 = pressed)
    AND  #1F         ; Mask to 5 bits
    LD   (HL),A
    INC  HL
    RLC  B           ; Next row: rotate the single 0 bit left
    DEC  C
    JR   NZ,.readLoop
```

For complete keyboard programming, see [keyboard.md](../../03_io/peripherals/keyboard.md).

### Beeper (1-Bit Sound)

The same `#FE` port controls the built-in speaker. Toggling bit 0 (EAR) produces audible clicks:

```z80
; Simple beep — toggle EAR bit at a specific frequency
Beep:
    LD   DE,frequency  ; Delay count (higher = lower pitch)
.beepLoop:
    XOR  A             ; Toggle EAR bit
    OUT  (#FE),A       ; EAR=0, border=0
    LD   B,D
    LD   C,E
.delay1:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.delay1

    LD   A,#08         ; EAR=0, border=color (preserve border)
    OUT  (#FE),A       ; EAR toggles
    LD   B,D
    LD   C,E
.delay2:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.delay2

    DEC  HL            ; Duration counter
    LD   A,H
    OR   L
    JR   NZ,.beepLoop
    RET
```

For advanced beeper techniques (multi-channel, PWM), see [beeper.md](../../06_sound/synthesis/beeper_synthesis.md).

---

## ROM (#0000–#3FFF)

The 16 KB ROM contains:

| Address range | Contents |
|---------------|----------|
| `#0000`–`#0037` | RST vectors and error handler entry points |
| `#0038`–`#003F` | IM1 interrupt service routine (unused in user programs — just `EI; RET`) |
| `#0066`–`#0073` | NMI handler |
| `#0090`–`#1097` | Keyboard scanning, beeper, tape I/O routines |
| `#1098`–`#15DE` | Calculator stack and floating-point arithmetic |
| `#15DF`–`#1A9B` | Cassette (tape) LOAD/SAVE routines |
| `#1A9C`–`#24FB` | Character set (96 characters × 8 bytes = 768 bytes) at `#1A9C`–`#1D9B` |
| `#24FC`–`#38FF` | BASIC interpreter, expression evaluator, editor |
| `#3900`–`#3FFF` | BASIC runtime, channel/stream system, PRINT, INPUT |

> [!TIP]
> You can **read** ROM (it's always present in the address space) but any write to `#0000`–`#3FFF` is silently ignored. Many programs copy small routines into RAM and jump there — self-modifying code requires RAM.

For a full ROM disassembly, see [rom_48k.md](../../04_operating_systems/rom_48k.md).

---

## Screen Pixel Buffer (#4000–#57FF)

The pixel (bitmap) display occupies **6,144 bytes** at `#4000`–`#57FF`. It stores a **256×192 monochrome image** at 1 bit per pixel.

The layout is **nonlinear** — organized as **three thirds** of 64 scanlines each, where each third is organized by character row × pixel row within that row:

```
Address calculation for pixel at screen position (x, y):
  Third:      (y / 64)           → bits 15-14 of address
  Character row: (y % 64) / 8    → bits 13-11
  Pixel row:     (y % 8)         → bits 7-5
  Column byte:   x / 8           → bits 4-0
```

For a complete explanation with lookup tables and fast access patterns, see [screen_layout.md](screen_layout.md).

### Contention Warning

The pixel buffer falls within the **contended memory range** (`#4000`–`#7FFF`). During the visible screen area (scanlines 64–255), the ULA steals bus cycles. Code that accesses this region runs **slower** — each M-cycle may be delayed by up to 6 T-states. See [contention_model.md](contention_model.md) for details.

---

## Attribute File (#5800–#5AFF)

The attribute file occupies **768 bytes** at `#5800`–`#5AFF`, organized as a **32×24 grid** of 8×8-pixel cells:

```
Attribute byte layout (1 byte per 8×8 cell):

  Bit   7      6    5    4    3    2    1    0
      ┌──────┬────┬────┬────┬────┬────┬────┬────┐
      │FLASH │BRT │P2  │P1  │P0  │I2  │I1  │I0  │
      └──────┴────┴────┴────┴────┴────┴────┴────┘

  Bits 0–2 (I0–I2):  INK color    (0–7)
  Bits 3–5 (P0–P2):  PAPER color  (0–7)
  Bit  6    (BRT):    BRIGHT       (0 = normal, 1 = bright)
  Bit  7    (FLASH):  FLASH        (0 = steady, 1 = flash between ink/paper)
```

Unlike the pixel buffer, attributes are **linearly addressed**: `Address = #5800 + (row × 32) + col`.

For color palette, FLASH timing, and hidden pixel tricks, see [color_system.md](../05_display_and_timing/color_system.md).

---

## Printer Buffer (#5B00–#5BFF)

A 256-byte buffer reserved for printer output. If no printer is attached, this area is **free for user programs** — the first area most machine code programs target for lookup tables, small routines, or buffers.

---

## System Variables (#5C00–#5CB5)

The system variables are **182 bytes** at `#5C00`–`#5CB5`. The ROM uses these to track BASIC interpreter state, editor, display, and I/O.

### Critical System Variables

| Address | Name | Length | Purpose |
|---------|------|--------|---------|
| `#5C00` | `KSTATE` | 8 | Keyboard state buffer |
| `#5C08` | `LAST_K` | 1 | Last key pressed |
| `#5C36` | `CHARS` | 2 | Character set address pointer |
| `#5C3A` | `ERR_NR` | 1 | Error report number (`#FF` = no error) |
| `#5C3B` | `FLAGS` | 1 | BASIC system flags |
| `#5C3D` | `ERR_SP` | 2 | Machine stack pointer for error recovery |
| `#5C4B` | `VARS` | 2 | Address of start of variables area |
| `#5C4F` | `CHANS` | 2 | Address of channel data |
| `#5C53` | `PROG` | 2 | Address of BASIC program start |
| `#5C59` | `E_LINE` | 2 | Address of edit line |
| `#5C78` | `FRAMES` | 3 | Frame counter (incremented every 20ms interrupt) |
| `#5C7B` | `UDG` | 2 | Address of first user-defined graphic |
| `#5CB2` | `RAMTOP` | 2 | Address of last byte in BASIC system area |
| `#5CB4` | `P_RAMT` | 2 | Address of last byte of physical RAM |

### Using System Variables from Assembly

```z80
; Read frame counter (3 bytes at FRAMES = #5C78)
LD   HL,(#5C78)     ; Low 16 bits
LD   A,(#5C7A)      ; High byte

; Check if a key was pressed (LAST_K = #5C08)
LD   A,(#5C08)      ; Get last key code
CP   #FF            ; #FF = no key
JR   Z,no_key

; Get BASIC program start address
LD   HL,(#5C53)     ; PROG
```

For a complete list of all system variables, see [system_variables.md](../../04_operating_systems/system_variables.md).

---

## Channel Information and Streams

Immediately after the system variables:

| Address range | Contents |
|---------------|----------|
| `#5CB6`–`#5CCF` | Channel definitions — 4 channels: **K** (keyboard), **S** (screen), **P** (printer), **R** (edit buffer) |
| After channels | Stream data — 16 streams × 2 bytes each |
| After streams | Calculator's memory area (`MEMBOT`, 30 bytes) |

---

## BASIC Program Area and Dynamic Layout

Above the fixed system areas, the memory layout is **dynamic** — it grows and shrinks as the BASIC program runs:

```
Growth direction  Area
────────────────  ─────────────────────────────────────────────────
                  PROG (BASIC program)         ──→ grows down
                  E_LINE (edit line)           ──→ grows down
                  WORKSP (workspace)           ──→ grows down
                  STKBOT (calculator stack)    ──→ grows down
                  STKEND (free space start)    ──→

                  ┆ FREE RAM ┆                    Available for machine code

                  VARS (variables)              ←── grows up
                  (numeric arrays)              ←── grows up
                  (string variables)            ←── grows up
                  (free space)
                  UDG (user-defined graphics)  ←── grows up from RAMTOP
                  RAMTOP (#FF58 on 48K)
                  P-RAMT (#FFFF on 48K)
────────────────  ─────────────────────────────────────────────────
```

---

## Reserving Memory for Machine Code

### Strategy 1: `CLEAR addr` — Coexist with BASIC

```basic
CLEAR 32767          ; Set RAMTOP to #7FFF
LOAD "game" CODE 32768, 9182   ; Load code at #8000
RANDOMIZE USR 32768  ; Execute
```

### Strategy 2: Use All RAM — No BASIC

Games typically claim **all memory from `#5B00` upward**:

```
#5B00 - #5BFF    Printer buffer     (256 bytes)
#5C00 - #5CB5    System variables   (182 bytes — keep for ROM routines)
#5CB6 - #FFFF    ALL FREE           (66,505 bytes ≈ 64.9 KB)
```

> [!TIP]
> Even in "use all RAM" mode, keep the system variables intact at `#5C00`–`#5CB5`. Many ROM routines (keyboard scan, tape load, beeper) reference these variables.

---

## 16K Model Differences

```
Address range    48K              16K
──────────────────────────────────────────
#0000 - #3FFF    ROM (16 KB)      ROM (16 KB)
#4000 - #57FF    Screen pixels    Screen pixels
#5800 - #5AFF    Attributes       Attributes
#5B00 - #5BFF    Printer buffer   Printer buffer
#5C00 - #5CB5    System vars      System vars
#5CB6 - #7FFF    BASIC + free RAM BASIC + free RAM (much less)
#8000 - #FFFF    More free RAM    ─── NOT PRESENT ───
```

Key differences: `P-RAMT` = `#7FFF` on 16K (vs `#FFFF` on 48K), much smaller BASIC area (~9 KB vs ~42 KB), but screen and system variables occupy the same addresses.

---

## Memory Map Quick Reference

| Address | 48K contents | Size | Contended |
|---|---|---|---|
| `#0000` | ROM | 16384 | No |
| `#4000` | Screen pixels (PIX) | 6144 | Yes |
| `#5800` | Attributes (ATTR) | 768 | Yes |
| `#5B00` | Printer buffer | 256 | Yes |
| `#5C00` | System variables | 182 | Yes |
| `#5CB6` | Channels + streams | — | Yes |
| | BASIC program + free RAM | — | Yes |
| `#FF58` | UDG area (default) | — | Yes |
| `#FFFF` | End of RAM | 1 | Yes |

> **Note:** Only `#4000`–`#7FFF` suffers ULA contention during screen display. Code in `#8000`–`#FFFF` is never contended on the 48K.

---

## Cross-References

- **I/O port decoding** (partial decoding, masks, conflicts): [io_port_decoding.md](io_port_decoding.md)
- **128K/+2 memory and ports** (banking, #7FFD, AY, shadow screen): [memory_and_io_128k.md](memory_and_io_128k.md)
- **Screen pixel layout** (nonlinear addressing, lookup tables): [screen_layout.md](screen_layout.md)
- **Contention model** (timing impact, per-model): [contention_model.md](contention_model.md)
- **System variables** (complete reference): [system_variables.md](../../04_operating_systems/system_variables.md)
- **48K ROM disassembly** (routines, entry points): [rom_48k.md](../../04_operating_systems/rom_48k.md)
- **Z80 address bus** (how 16-bit addressing works): [z80_architecture.md](../../01_cpu/z80_architecture.md)
- **Complete I/O port map** (all ports, all models, decoding bitmasks): [io_port_map.md](../../10_references/io_port_map.md)
