[← Home](../../README.md) · [Memory & I/O](README.md)

# ZX Spectrum 16K / 48K Memory Map

The Z80 CPU has a 16-bit address bus — it can address **65,536 bytes (64 KB)** of memory. The ZX Spectrum 48K uses the entire 64 KB address space without paging: the lower 16 KB is ROM, the upper 48 KB is RAM. The 16K model is identical except RAM stops at `#7FFF` (only 16 KB of RAM fitted).

> [!NOTE]
> This article covers the **static memory layout** — what lives at each address and why it matters to programmers. For memory contention (why code in `#4000`–`#7FFF` runs slower during screen display), see [ula_timing.md](../../02_hardware/original/ula_timing.md). For 128K paging and bank switching, see [memory_map_128k.md](memory_map_128k.md).

---

## Overview

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

---

## Screen Pixel Buffer (#4000–#57FF)

The pixel (bitmap) display occupies **6,144 bytes** at `#4000`–`#57FF`. It stores a **256×192 monochrome image** at 1 bit per pixel.

The layout is **nonlinear** — it does not map sequentially row by row. Instead, it is organized as **three thirds** of 64 scanlines each, where each third is organized by character row × pixel row within that row:

```
Address calculation for pixel at screen position (x, y):
  x = column (0–255), y = row (0–191)

  Third:      (y / 64)           → bits 15-14 of address
  Character row: (y % 64) / 8    → bits 13-11
  Pixel row:     (y % 8)         → bits 7-5
  Column byte:   x / 8           → bits 4-0

  Address = 010T_TTTT_RRR_C_CCCC  (binary)
  T = third (0–2), R = row within third (0–7), C = column byte (0–31)
```

For a complete explanation of the nonlinear layout with lookup tables and fast access patterns, see [screen_layout.md](screen_layout.md).

### Contention Warning

The entire pixel buffer (`#4000`–`#57FF`) falls within the **contended memory range** (`#4000`–`#7FFF`). During the visible screen area (scanlines 64–255), the ULA steals bus cycles to fetch pixel and attribute data. Code that reads or writes the pixel buffer during this window runs **slower** — each M-cycle may be delayed by up to 6 T-states. See [ula_timing.md](../../02_hardware/original/ula_timing.md) for the exact contention pattern.

---

## Attribute File (#5800–#5AFF)

The attribute file occupies **768 bytes** at `#5800`–`#5AFF`. It stores the color and flash information for the screen, organized as a **32×24 grid** of 8×8-pixel cells:

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

```
Standard color palette:

  Code  Normal    Bright    Binary
  0     Black     Black     000
  1     Blue      Blue      001
  2     Red       Red       010
  3     Magenta   Magenta   011
  4     Green     Green     100
  5     Cyan      Cyan      101
  6     Yellow    Yellow    110
  7     White     White     111
```

Unlike the pixel buffer, the attribute file **is** linearly addressed:

```
Attribute address for cell at column c (0–31), row r (0–23):
  Address = #5800 + (r × 32) + c
```

This means updating attributes is straightforward — `LD HL,#5800` gives you the start, and you can use `INC L` or `LDIR` to walk through sequentially.

> [!IMPORTANT]
> The attribute file is also in contended memory. Updating attributes during the visible screen area is subject to contention delays. For timing-critical multicolor effects (changing attributes mid-scanline), see [race_the_beam.md](../04_interrupts/race_the_beam.md).

### Flash Timing — ULA-Internal Counter

The FLASH bit does **not** rely on any software timer or the `FRAMES` system variable. The ULA has a **free-running frame counter** inside the chip: it increments on every video field and uses **bit 4** of that counter as the flash-phase signal. The phase flips once every **16 video frames** whether or not the CPU is running — even `DI:HALT` doesn't stop it.

The visual flash speed therefore **depends on the machine's frame rate**:

| Machine | Frame rate | Phase length | Full cycle |
|---------|-----------|-------------|------------|
| ZX Spectrum 48K | ~50.08 Hz | ~319 ms | ~639 ms |
| ZX Spectrum 128K / +2 / +3 | ~50.02 Hz | ~320 ms | ~640 ms |
| Pentagon 128K | ~48.83 Hz | ~328 ms | ~655 ms |
| Scorpion ZS-256 | ~48.83 Hz | ~328 ms | ~655 ms |
| ZX Spectrum Next (50/60 Hz) | 50 / 60 Hz | 320 / 267 ms | 640 / 533 ms |

Demos that use FLASH as a **timing aid** (rather than decoration) will appear noticeably slower on Pentagon vs original Sinclair hardware. When exporting flashing screens as animated GIF, use ~320 ms per phase for 48K/128K-authentic playback; Pentagon-authentic would need ~328 ms.

### Hidden Pixels — Ink Equals Paper

When a cell's INK and PAPER are the same color index, **every pixel in that 8×8 block renders as a single solid color** — the underlying bitmap bits are invisible but still stored in memory. This "hidden pixel" trick was widely exploited:

- **Artist signatures**: Names or initials drawn in black-ink-on-black-paper, invisible during gameplay but readable when attributes are changed in an editor. Many commercial loader screens carry such hidden tags.
- **Cracker tags**: Scene groups added names the same way; competing groups would find them by cycling attributes.
- **Easter eggs**: Extra artwork hidden behind solid-color areas (sky, UI panels).
- **Copy-protection / fingerprinting**: A known hidden pattern verifies the file is unmodified. Tools that re-encode through PNG and back destroy the watermark.
- **Compression quirks**: Two cells that look identical on screen can have wildly different bitmap bytes, affecting how well RLE/delta encoders compress the `.SCR`. Loaders that de-dup "solid" cells by attribute alone will corrupt such data.

> [!WARNING]
> Exporting a `.SCR` to `.PNG`/`.JPG`/`.GIF`/`.BMP` collapses each cell to a solid block — the hidden bitmap data is **lost permanently**. This is a one-way conversion.

---

## Printer Buffer (#5B00–#5BFF)

A 256-byte buffer reserved for printer output. If no printer is attached, this area is **free for user programs**. On a 48K Spectrum with no printer:

```
#5B00 - #5BFF    256 bytes    FREE (printer buffer, unused without printer)
```

This is the first area most machine code programs target — it's small but useful for lookup tables, small routines, or buffers.

---

## System Variables (#5C00–#5CB5)

The system variables are **182 bytes** at `#5C00`–`#5CB5`. The ROM uses these to track the state of the BASIC interpreter, editor, display, and I/O system. Key variables:

### Critical System Variables

| Address | Name | Length | Purpose |
|---------|------|--------|---------|
| `#5C00` | `KSTATE` | 8 | Keyboard state buffer (for key scanning) |
| `#5C08` | `LAST_K` | 1 | Last key pressed |
| `#5C36` | `CHARS` | 2 | `#0000` less than address of character set (points to `#19AD` = start of font - 256) |
| `#5C3A` | `ERR_NR` | 1 | One less than error report number (`#FF` = no error) |
| `#5C3B` | `FLAGS` | 1 | BASIC system flags |
| `#5C3D` | `ERR_SP` | 2 | Machine stack pointer for error recovery |
| `#5C4B` | `VARS` | 2 | Address of start of variables area |
| `#5C4F` | `CHANS` | 2 | Address of channel data |
| `#5C53` | `PROG` | 2 | Address of BASIC program start |
| `#5C59` | `E_LINE` | 2 | Address of edit line (command being typed) |
| `#5C78` | `FRAMES` | 3 | Frame counter ( incremented every 20ms interrupt ) |
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

; Set border color via BORDCR system variable
LD   A,#07          ; White border
LD   (#5C48),A      ; BORDCR

; Get BASIC program start address
LD   HL,(#5C53)     ; PROG
```

For a complete list of all system variables, see the [ROM disassembly sysvars table](https://skoolkid.github.io/rom/buffers/sysvars.html).

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

> [!NOTE]
> The BASIC program, variables, and edit buffer all grow **downward** from the system area. UDG and spare space grow **upward** from RAMTOP. The gap between STKEND and VARS is the free RAM available for machine code or BASIC data.

---

## Reserving Memory for Machine Code

Two strategies:

### Strategy 1: `CLEAR addr` — Coexist with BASIC

The `CLEAR` command sets `RAMTOP` to a lower address, protecting everything above it from BASIC:

```basic
CLEAR 32767          ; Set RAMTOP to #7FFF
LOAD "game" CODE 32768, 9182   ; Load code at #8000
RANDOMIZE USR 32768  ; Execute
```

After `CLEAR 32767`, BASIC programs and variables cannot use memory above `#7FFF`. Your machine code at `#8000` is safe. This reduces BASIC's available memory but allows returning to BASIC after execution.

### Strategy 2: Use All RAM — No BASIC

Games typically claim **all memory from `#5B00` upward**:

```
#5B00 - #5BFF    Printer buffer     (256 bytes)
#5C00 - #5CB5    System variables   (182 bytes — keep for ROM routines)
#5CB6 - #FFFF    ALL FREE           (66,505 bytes ≈ 64.9 KB)
```

The program takes over the entire machine. The only way back to BASIC is a reset. This gives the maximum available RAM but means you must implement your own I/O (keyboard reading via `IN`, screen writing via `LD`, sound via `OUT`).

> [!TIP]
> Even in "use all RAM" mode, keep the system variables intact at `#5C00`–`#5CB5`. Many ROM routines (keyboard scan, tape load, beeper) reference these variables. If you trash them, ROM calls will crash.

---

## 16K Model Differences

The 16K Spectrum has only 16 KB of RAM installed:

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

Key differences:
- `P-RAMT` (`#5CB4`) = `#7FFF` on 16K (vs `#FFFF` on 48K)
- `RAMTOP` defaults to lower address
- Screen and system variables occupy the same addresses — the 16K model has the same screen at `#4000`
- BASIC program area is much smaller (~9 KB vs ~42 KB)

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
| | BASIC program | — | Yes |
| | Free RAM | — | Yes |
| | Variables | — | Yes |
| `#FF58` | UDG area (default) | — | Yes |
| `#FFFF` | End of RAM | 1 | Yes |

> **Note:** ALL RAM (`#4000`–`#FFFF`) is in the contended range on 48K. Only `#4000`–`#7FFF` suffers ULA contention during screen display. Code in `#8000`–`#FFFF` is never contended on the 48K model.

---

## Cross-References

- **Screen pixel layout** (nonlinear addressing, lookup tables): [screen_layout.md](screen_layout.md)
- **128K memory map** (banking, paging register): [memory_map_128k.md](memory_map_128k.md)
- **Memory contention** (timing impact, per-model): [ula_timing.md](../../02_hardware/original/ula_timing.md)
- **I/O ports** (#FE border/speaker, #7FFD paging): [io_ports.md](io_ports.md)
- **System variables** (complete reference): [ROM disassembly sysvars](https://skoolkid.github.io/rom/buffers/sysvars.html)
- **Z80 address bus** (how 16-bit addressing works): [z80_architecture.md](../../01_cpu/z80_architecture.md)
- **Bedazzle, "SpectraLab — ZX Spectrum Graphics Guide"** ([github.com/Bedazzle/SpectraLab](https://github.com/Bedazzle/SpectraLab)) — Flash timing (ULA internal counter), hidden pixels / ink-equals-paper steganography
