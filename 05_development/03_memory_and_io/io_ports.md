[← Home](../../README.md) · [Memory & I/O](README.md)

# I/O Ports — Partial Decoding, the #FE Port, and Per-Model Differences

The Z80 has a separate **16-bit I/O address space** accessed via `IN` and `OUT` instructions (distinct from the 64 KB memory space). On the ZX Spectrum, the hardware uses **partial address decoding** — only a few address lines are actually checked by each peripheral. This means a single physical port appears at **thousands of addresses**, and different peripherals can accidentally overlap if their decoding masks conflict.

> [!NOTE]
> This article covers the **I/O port architecture** — how partial decoding works, the key ports every Spectrum programmer needs, and per-model differences. For memory addresses (RAM/ROM layout), see [memory_map_48k.md](memory_map_48k.md). For hardware-level signal timing, see [z80_timing.md](../../01_cpu/z80_timing.md).

---

## How Partial Address Decoding Works

When the Z80 executes `OUT (n), A`, it places `n` on the **low 8 bits** of the address bus (A0–A7) and `A` on the **high 8 bits** (A8–A15). The hardware does **not** decode all 16 address lines. Instead, each peripheral checks only the lines it cares about:

```
Z80 OUT (C), A instruction:  places B on A8–A15, C on A0–A7, A on data bus

Example: OUT (#FE), A
  Address bus:  A15-A8 = #FF (accumulator doesn't matter — it's A0-A7 that selects the port)
                A7-A0  = #FE = 11111110

ULA checks:    A0 = 0 (only checks one line!)
               All other address lines are DON'T CARE

So the ULA responds to ANY address where A0 = 0:
  #FE, #FC, #FA, #F8, #F6, #F4, ... #00, #02, #04, ...
  That's 32,768 addresses out of 65,536 — half the entire I/O space!
```

### Decoding Masks

Each peripheral can be described by a **decoding bitmask**: which address bits it checks and what values it expects:

```
Port #FE (ULA):
  Mask:   ______ _______0    (only A0 is checked)
  Match:  xxxxxx xxxxxxx0    (A0 must be 0)
  
Port #1F (Kempston joystick):
  Mask:   ______ _____xxxx   (only A0–A4 are checked by some implementations)
  Match:  xxxxxx xxxx_11111  (A0–A4 must be #1F)

Port #7FFD (128K paging):
  Mask:   _______0 1111_110_  (A15=0, A14–A12=#7, A1=0 — checks 6 lines)
  Match:  xxxxxxxx 0111_110x  (A15=0, A14-A11=0111, A1=0)
```

The **more lines a peripheral checks**, the **fewer addresses** it mirrors to — and the less chance of conflict with other peripherals.

> [!IMPORTANT]
> Always use the **canonical address** when accessing a port (e.g., `OUT (#FE), A`, not `OUT (#FC), A`). While both are decoded identically by the hardware, the canonical form is clearer and avoids confusion. The ROM always uses canonical addresses.

---

## The #FE Port — ULA Control

The most important port on the ZX Spectrum. **Address `#FE`** (bit 0 = 0) controls four functions simultaneously:

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
                  Reads the currently-selected keyboard row
  Bit 0:          Always 1 (pull-up resistor)
  Bits 5–6:       Floating (undefined, varies by machine)
```

### Border Color

The border is the area outside the 256×192 pixel display — it's visible as a frame around the screen. Setting the border color:

```z80
; Set border to blue (color 1)
LD   A,#01            ; Blue
OUT  (#FE),A          ; Write to ULA port

; Set border to bright yellow (color 6 + bright = #46... no, border doesn't support BRIGHT)
; Border only supports 8 colors (0-7), no BRIGHT flag
LD   A,#06            ; Yellow
OUT  (#FE),A

; CAUTION: bits 0 (EAR) must be considered!
; If you only want to change the border, preserve bit 0:
LD   A,#02            ; Red border, EAR=0
OUT  (#FE),A

; Or use the ROM routine:
LD   A,color          ; Border color (0-7)
CALL #229B            ; ROM BEEPER routine sets border as side effect
```

> [!WARNING]
> Every `OUT (#FE), A` writes ALL bits — border color AND EAR output. If you toggle the border rapidly (for raster effects or beeper music), the EAR output will also toggle. This is why border color changes during tape loading cause buzzing on the MIC output.

### Keyboard Reading

The keyboard is read through the same `#FE` port, combined with address line selection:

```
Keyboard matrix: 8 half-rows × 5 keys each

To read half-row N (0-7):
  - Set address lines A8–A15 = all high (#FF)
  - Set A0–A4 such that only the desired row is selected
  - Actually: OUT (#FE) isn't used for keyboard reading.
    Instead, IN from addresses with specific high-byte patterns.

Standard keyboard reading:
  IN A, (#xxFE) where xx selects the row via partial decoding:

  Row address    Keys (bit positions in result, 0 = pressed)
  ────────────────────────────────────────────────────────────
  #FEFE    #7FFE    Row 0:  SHIFT  Z  X  C  V       (bits 0-4)
  #FDFE    #FBFE    Row 1:  A  S  D  F  G           (bits 0-4)  
  #FBFE    #F7FE    Row 2:  Q  W  E  R  T           (bits 0-4)
  #F7FE    #EFFE    Row 3:  1  2  3  4  5           (bits 0-4)
  #EFFE    #DFFE    Row 4:  0  9  8  7  6           (bits 0-4)
  #DFFE    #BFFE    Row 5:  P  O  I  U  Y           (bits 0-4)
  #BFFE    #7FFE    Row 6:  ENTER  L  K  J  H      (bits 0-4)
  #7FFE    ...      Row 7:  SPACE  SYM  M  N  B     (bits 0-4)
```

Wait — let me correct the standard addresses. The Spectrum keyboard uses **one address line low per half-row**:

```
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
    OUT  (#FE),A       ; EAR toggles but we set it back
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

For advanced beeper techniques (multi-channel, PWM), see [beeper.md](../07_audio/beeper.md).

---

## 128K Paging Port — #7FFD

On the 128K, +2, +2A, and +3 models, port `#7FFD` controls memory paging:

```
OUT (#7FFD), A — 128K paging register:

  Bit   7  6  5  4  3  2  1  0
      ┌────┬────┬────┬────┬────┬────┬────┬────┐
      │DIS │ x  │ x  │ROM │SCR │B2  │B1  │B0  │
      └────┴────┴────┴────┴────┴────┴────┴────┘

  Bits 0–2 (B0–B2): RAM bank to page into #C000–#FFFF (0–7)
  Bit  3    (SCR):   Screen select (0 = bank 5 at #4000, 1 = bank 7)
  Bit  4    (ROM):   ROM select (0 = 128K editor ROM, 1 = 48K BASIC ROM)
  Bit  5:            Unused
  Bit  6:            Unused
  Bit  7    (DIS):   Disable paging (1 = lock further writes to #7FFD)
```

```z80
; Page RAM bank 2 into #C000–#FFFF
LD   A,#02            ; Bank 2
OUT  (#7FFD),A        ; Page it in

; Switch to shadow screen (bank 7) and 48K ROM
LD   A,%00011000      ; ROM=1, SCR=1, bank=0
OUT  (#7FFD),A

; Lock paging (prevent further changes until reset)
LD   A,#80|%00000010  ; DIS=1, bank=2
OUT  (#7FFD),A        ; After this, #7FFD is locked!
```

> [!WARNING]
> Port `#7FFD` is **write-only**. Reading it returns floating bus garbage, not the current paging state. Your program must track the current state in a variable.

For full 128K paging details, see [memory_map_128k.md](memory_map_128k.md).

---

## AY Sound Chip Ports — #FFFD / #BFFD

The AY-3-8912 PSG ( Programmable Sound Generator) is present on the 128K, +2, +2A, +3, Pentagon, Scorpion, and most clones:

```
OUT (#FFFD), A — Select AY register (register address port)
OUT (#BFFD), A — Write to selected AY register (register data port)
IN  A, (#FFFD) — Read from selected AY register
```

The decoding checks A1 and A0:

```
#FFFD:  A1=0, A0=1    → Register select
#BFFD:  A1=1, A0=1    → Register data
```

```z80
; Set AY channel A tone to 440 Hz (approximately)
; AY clock = 1.7734 MHz on 128K, divider = 16
; Tone period = clock / (16 × frequency) = 1773400 / (16 × 440) ≈ 252

LD   A,#00           ; Register 0 = Channel A tone period fine
LD   BC,#FFFD
OUT  (C),A           ; Select register 0
LD   B,#BF           ; BC = #BFFD
LD   A,#252 & #FF    ; Fine = #FC
OUT  (C),A           ; Write value

LD   A,#01           ; Register 1 = Channel A tone period coarse
LD   B,#FF           ; BC = #FFFD
OUT  (C),A
LD   B,#BF           ; BC = #BFFD
LD   A,#252 >> 8     ; Coarse = 0
OUT  (C),A
```

For complete AY programming, see [ay_programming.md](../07_audio/ay_programming.md).

---

## +2A/+3 Extra Paging — #1FFD

The +2A and +3 models add a second paging register:

```
OUT (#1FFD), A — +2A/+3 extended control:

  Bit 0:   Paging mode (0 = 128K compatible, 1 = special modes)
  Bit 1-2: Memory map mode (when bit 0 = 1)
  Bit 3:   ROM bank select (combined with bit 4 of #7FFD)
  Bit 4:   Disk motor control
  Bit 5:   Printer strobe
```

When bit 0 = 1, bits 1–2 select between four special memory maps used for CP/M compatibility. See [memory_map_plus3.md](memory_map_plus3.md).

---

## Kempston Joystick — #1F

The Kempston joystick interface decodes A5–A0:

```
IN A, (#1F) — Read Kempston joystick

  Bit 4:  Up
  Bit 3:  Down
  Bit 2:  Left
  Bit 1:  Right
  Bit 0:  Fire

Active high (1 = pressed), unlike keyboard (active low)
```

```z80
; Read Kempston joystick
IN   A,(#1F)         ; Read joystick state
AND  #1F             ; Mask to 5 bits
; Bits are active HIGH — bit 0 = fire, bit 1 = right, etc.
BIT  0,A
JR   NZ,fire_pressed
BIT  1,A
JR   NZ,right_pressed
```

---

## Per-Model Port Differences

| Port | 48K | 128K/+2 | +2A/+3 | Pentagon | Scorpion |
|------|-----|---------|--------|----------|----------|
| `#FE` (ULA) | ✅ Border + EAR + keyboard | ✅ Same | ✅ Same | ✅ Same (but some clones add extra bits) | ✅ Same |
| `#7FFD` (paging) | ❌ | ✅ RAM bank + ROM + screen | ✅ Same + DIS bit | ✅ Extended (EFF7 for 512K+) | ✅ Extended |
| `#1FFD` (+3 paging) | ❌ | ❌ | ✅ Special modes + disk | ❌ | ❌ |
| `#FFFD/#BFFD` (AY) | ❌ (no AY) | ✅ | ✅ | ✅ | ✅ |
| `#1F` (Kempston) | ✅ If interface present | ✅ If present | ✅ If present | ✅ Built-in | ✅ Built-in |
| `#1FFD` (Beta 128 FDC) | ❌ | ❌ | ❌ | ✅ (TR-DOS) | ✅ (TR-DOS) |

### Pentagon Extensions (EFF7)

The Pentagon 128K with the EFF7 extension (most common configuration) adds an extra paging port:

```
OUT (#EFF7), A — Pentagon extended memory control:
  Controls access to RAM banks 8–31 (512K total) or banks 8–63 (1024K)
  Bit 2:   ROM page select for #0000–#3FFF area  
  Bits 0-1: Extended RAM bank selection
```

See [memory_map_pentagon.md](memory_map_pentagon.md) for details.

---

## Port Conflict Map

Because of partial decoding, some ports **overlap** on certain models:

```
#FE: A0=0 — 32,768 mirrors (#FE, #FC, #FA, ... #00, #02, ...)
  Conflicts: Beta 128 FDC (#1F, #3F, #5F, ...) — different A5-A0 patterns
  
#7FFD: 6 lines checked — 64 mirrors
  Relatively well-decoded, fewer conflicts
  
#FFFD/#BFFD: 2 lines checked — many mirrors
  Can conflict with other peripherals using A0/A1 decoding

#1F: Kempston (5 lines checked on good implementations)
  Poor implementations check only A5-A7 → many more mirrors
```

> [!TIP]
> When writing software that must work across models, **always use canonical port addresses** and be aware that some peripherals may be present or absent depending on the machine. Check for hardware presence before accessing ports.

---

## Quick Reference — Canonical Ports

```
Port    Decoding     Direction   Function
──────────────────────────────────────────────────────────────
#FE     A0=0         R/W         ULA: border, EAR, keyboard
#1F     A5-A0=011111 R           Kempston joystick
#7FFD   A15=0,etc    W           128K paging (bank, ROM, screen)
#1FFD   varies       W           +2A/+3 extended paging
#FFFD   A1=0,A0=1    R/W         AY register select
#BFFD   A1=1,A0=1    W           AY register data
#DFFD   varies       W           Pentagon extended paging (some configs)
#EFF7   varies       W           Pentagon EFF7 extension
──────────────────────────────────────────────────────────────

For the complete port map covering ALL peripherals (FDC, IDE, mouse, etc.),
see the References: [io_port_map.md](../../08_references/io_port_map.md)
```

---

## Cross-References

- **48K memory map**: [memory_map_48k.md](memory_map_48k.md)
- **128K paging register**: [memory_map_128k.md](memory_map_128k.md)
- **Z80 I/O timing** (T-states for IN/OUT): [z80_timing.md](../../01_cpu/z80_timing.md)
- **Beeper programming**: [beeper.md](../07_audio/beeper.md)
- **AY chip programming**: [ay_programming.md](../07_audio/ay_programming.md)
- **Keyboard reading in depth**: [keyboard.md](../../03_io/peripherals/keyboard.md)
- **Complete port map**: [io_port_map.md](../../08_references/io_port_map.md)
- **Hardware ports reference** (World of Spectrum): [ports.htm](https://worldofspectrum.org/faq/reference/ports.htm)
- **Black_Cat's full port table** (per-model differences): [zx-ports-full-table.txt](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt)
