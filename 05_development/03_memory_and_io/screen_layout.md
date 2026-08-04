[← Home](../../README.md) · [Memory & I/O](README.md)

# Screen Pixel Layout — The Nonlinear Framebuffer

The ZX Spectrum's pixel display at `#4000`–`#57FF` (6,144 bytes) stores a **256×192 monochrome image**. But unlike modern framebuffers where pixels are laid out sequentially row by row, the Spectrum uses a **nonlinear addressing scheme** inherited from the DRAM refresh pattern of the Ferranti ULA. This layout is the source of both the Spectrum's most frustrating programming constraint and its most creative demoscene tricks.

> [!NOTE]
> This article covers the **pixel buffer layout only** — how to calculate the address of any pixel and how to access the screen efficiently. For the attribute file (linearly addressed at `#5800`–`#5AFF`), see [memory_and_io_48k.md](memory_and_io_48k.md). For timing constraints on screen access (contention), see [contention_model.md](contention_model.md).

---

## Why Nonlinear?

The Ferranti ULA generates the video signal by reading the screen RAM directly — there is no dedicated video memory or DMA. During each scanline, the ULA fetches 32 bytes of pixel data and 32 bytes of attribute data from RAM while simultaneously allowing the CPU to access memory.

The ULA reads pixels in **raster scan order** (left to right, top to bottom). But the address it generates on the RAM bus is structured for efficient DRAM access:

```
ULA video address (14-bit, covers #4000–#57FF + #5800–#5AFF):

  Bit position:  13  12  11  10  9   8   7   6   5   4   3   2   1   0
                 ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
  Pixel addr:    │ T2│ T1│ T0│ Y2│ Y1│ Y0│ R2│ R1│ R0│ C4│ C3│ C2│ C1│ C0│
                 └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

  T (bits 13-11): Third number      (0–2, selects which third of the screen)
  Y (bits 7-5):   Pixel row within character row (0–7, sub-row within 8-pixel line)
  R (bits 10-8):  Character row within third     (0–7, which 8-pixel line in this third)
  C (bits 4-0):   Column byte         (0–31, which byte in the row)
```

The key insight: **pixel row (Y) is in bits 7-5 while character row (R) is in bits 10-8**. This means that consecutive scanlines (same character row, pixel row incrementing) are **256 bytes apart** in memory, not 32 bytes apart as you'd expect in a linear layout.

---

## The Three-Thirds Structure

The screen is divided into **three vertical thirds**, each 64 scanlines (8 character rows × 8 pixels):

```
Third 0 (rows 0–63):     #4000–#47FF    (2048 bytes)
Third 1 (rows 64–127):   #4800–#4FFF    (2048 bytes)
Third 2 (rows 128–191):  #5000–#57FF    (2048 bytes)
```

Within each third, 8 character rows of 8 pixels each:

```
Third 0, Character Row 0 (screen rows 0–7):    #4000–#401F (row 0), #4100–#411F (row 1), ... #4700–#471F (row 7)
Third 0, Character Row 1 (screen rows 8–15):   #4020–#403F (row 0), #4120–#413F (row 1), ... #4720–#473F (row 7)
...
Third 2, Character Row 7 (screen rows 184–191): #57E0–#57FF (row 0), #57E0 ... wait
```

### Visual Layout (Partial)

```
Address     Screen Row  Character Row  Third
──────────────────────────────────────────────
#4000       0           0              0      ← First byte of first pixel row
#401F       0           0              0      ← Last byte of first pixel row (32 bytes = 256 pixels)
#4100       1           0              0      ← Second pixel row, 256 bytes later!
#411F       1           0              0
#4200       2           0              0
...
#4700       7           0              0      ← 8th pixel row of char row 0
#471F       7           0              0
#4020       8           1              0      ← Back to #4020 for next character row!
#4120       9           1              0
...
#4800       64          0              1      ← Third 1 starts
#5000       128         0              2      ← Third 2 starts
```

---

## Address Calculation

### Standard Formula

To calculate the address of the byte containing pixel at screen position **(column C, row R)** where C = 0–255 and R = 0–191:

```
Address = #4000
        + ((R & #C0) << 5)     ; Third × 2048 (bits 6-7 → bits 13-11)
        + ((R & #07) << 8)     ; Pixel row within char row × 256 (bits 0-2 → bits 10-8)
        + ((R & #38) << 2)     ; Character row within third × 32 (bits 3-5 → bits 7-5)
        + (C >> 3)             ; Column byte (0–31)
```

Or equivalently, building the address by bit manipulation:

```
H = %010_T_TTTT       ; 010 = fixed, T_TTTT = third (bits 6-7) + char row (bits 3-5)
L = RRR_C_CCCC        ; RRR = pixel row (bits 0-2), C_CCCC = column byte
```

Wait — the standard reference uses a cleaner decomposition:

```
Given: row (0–191), col (0–255)

Third = row / 64                    (0, 1, or 2)
CharRow = (row % 64) / 8            (0–7, character row within third)
PixelRow = row % 8                  (0–7, pixel row within character row)
ByteCol = col / 8                   (0–31, byte column)

High byte = #40 | (Third << 3) | CharRow    →  #40–#57
Low byte  = (PixelRow << 5) | ByteCol       →  #00–#FF
```

### Z80 Assembly Implementation

```z80
; Calculate screen address for pixel at (B, C) where B=row (0-191), C=column (0-255)
; Returns address in HL

ScreenAddr:
    LD   A,B             ; A = row (0-191)
    AND  %11000000       ; Isolate third (bits 6-7)
    RRCA                 ; Rotate to bits 4-5
    RRCA
    RRCA
    LD   H,A             ; H = third contribution to high byte
    
    LD   A,B             ; A = row again
    AND  %00111000       ; Isolate char row (bits 3-5)
    RLCA                 ; Rotate to bits 4-6
    RLCA
    OR   H               ; Combine with third
    OR   %01000000       ; Set base address bit (screen starts at #4000)
    LD   H,A             ; H = high byte
    
    LD   A,B             ; A = row again
    AND  %00000111       ; Isolate pixel row (bits 0-2)
    RLCA                 ; Shift to bits 5-7
    RLCA
    RLCA
    LD   L,A             ; L = pixel row contribution
    
    LD   A,C             ; A = column
    AND  %11111000       ; Clear low 3 bits (keep byte column)
    RRCA                 ; Shift to bits 0-4
    RRCA
    RRCA
    OR   L               ; Combine with pixel row
    LD   L,A             ; L = low byte
    
    RET                  ; HL = screen address
```

### Lookup Table Approach (Faster)

For performance-critical code (games, demos), use a 192-byte lookup table for the high byte of each row:

```z80
; Build row address table (192 entries, each 2 bytes)
BuildRowTable:
    LD   HL,RowTable
    LD   B,192
    LD   DE,#4000
.row_loop:
    LD   A,E
    AND  %11000000       ; Third
    RRCA \ RRCA \ RRCA
    LD   C,A
    LD   A,E
    AND  %00111000       ; Char row
    RLCA \ RLCA
    OR   C
    OR   %01000000
    LD   (HL),A          ; High byte
    INC   HL
    LD   (HL),#00        ; Low byte placeholder
    INC   HL
    INC   E              ; Next row (simplified - doesn't handle bit crossing)
    DJNZ .row_loop
    RET
```

In practice, most games pre-build this table at startup and then use it as:

```z80
; Fast screen access using pre-built table
    LD   L,B             ; B = row (0-191)
    LD   H,#00
    ADD  HL,HL           ; 2 bytes per entry
    LD   DE,RowTable
    ADD  HL,DE
    LD   A,(HL)          ; High byte
    INC   HL
    LD   L,(HL)          ; Low byte base
    LD   H,A
    LD   A,C             ; C = column byte (0-31)
    RRCA \ RRCA \ RRCA   ; Convert pixel column to byte offset
    ADD  A,L
    LD   L,A             ; HL = final screen address
```

---

## Attribute File (Linear)

Unlike the pixel buffer, the attribute file at `#5800`–`#5AFF` is **linearly addressed**:

```
Attribute address for cell at (column_byte, character_row):
  Address = #5800 + (character_row × 32) + column_byte

Where: character_row = screen_row / 8 (0–23)
       column_byte   = column / 8     (0–31)
```

This means there are **24 character rows** (192 pixels / 8 = 24) × **32 columns** = **768 bytes**.

```
Screen row 0–7   (char row 0):  #5800–#581F
Screen row 8–15  (char row 1):  #5820–#583F
Screen row 16–23 (char row 2):  #5840–#585F
...
Screen row 184–191 (char row 23): #5AE0–#5AFF
```

### Attribute Access Pattern

```z80
; Set attribute for character cell at (row, col) where row=0-23, col=0-31
SetAttr:
    LD   A,row
    AND  %00011111       ; Limit to 0-23
    RLCA \ RLCA \ RLCA   ; × 32 (with 3 RLCA, but need 5 shifts for ×32)
    ; Better: use lookup or multiply
    LD   H,#58
    LD   L,A             ; L = row * 32
    LD   A,col
    AND  %00011111
    ADD  A,L
    LD   L,A             ; HL = attribute address
    LD   (HL),attr_val
    RET
```

---

## Column-Major Access

The pixel layout is **column-major within each character row** — bytes are arranged by scanline, with 32 bytes per line. This means that to draw a **vertical line** (same column, different rows), you must jump 256 bytes between consecutive pixel rows within the same character row, then return to a nearby address for the next character row:

```
Drawing a vertical line at column 0, char row 0:

Row 0: #4000  →  byte 0
Row 1: #4100  →  byte 0 (+256)
Row 2: #4200  →  byte 0 (+256)
...
Row 7: #4700  →  byte 0 (+256)
Row 8: #4020  →  byte 0 (+32, back near start! — different char row)
Row 9: #4120  →  byte 0 (+256)
```

This is why **vertical scrolling** is harder than horizontal scrolling on the Spectrum — the pixel layout is optimized for horizontal access (one scanline = 32 consecutive bytes).

---

## Practical Implications

### What the Layout Makes Easy

1. **Horizontal line drawing** — each scanline is 32 consecutive bytes. `LD HL,address; LD B,32; .loop: LD (HL),#FF; INC L; DJNZ .loop` fills one row.

2. **Character-based text** — writing an 8×8 character at character position (col, row) requires writing 8 bytes, each 256 bytes apart. The ULA's address pattern makes this a simple `INC H` sequence:

```z80
; Write 8-byte font glyph at pixel position (HL)
; HL points to top-left pixel byte
    LD   B,8
.loop:
    LD   A,(DE)          ; Get font byte
    LD   (HL),A          ; Write to screen
    INC  H               ; Next pixel row (+256 bytes!)
    INC  DE
    DJNZ .loop
```

3. **Attribute updates** — linear, so `LDIR` or sequential `INC L` works.

### What the Layout Makes Hard

1. **Vertical pixel access** — 256-byte jumps between pixel rows within a character row, then a jump back for the next character row.

2. **Pixel-perfect sprite placement** — a sprite at an arbitrary (x, y) position may span up to 3 character rows and 2 byte columns, requiring complex masking.

3. **Smooth vertical scrolling** — the entire pixel buffer must be reorganized because the third/row interleaving means you can't just shift bytes by 32.

---

## Memory Map Summary

```
Pixel buffer (#4000–#57FF, 6144 bytes):
  3 thirds × 8 char rows × 8 pixel rows × 32 bytes = 6144 bytes
  
  Third 0: #4000–#47FF  (rows 0–63)
  Third 1: #4800–#4FFF  (rows 64–127)
  Third 2: #5000–#57FF  (rows 128–191)

Attribute file (#5800–#5AFF, 768 bytes):
  24 char rows × 32 columns = 768 bytes (linear)
  
  Char row 0:  #5800  (screen rows 0–7)
  Char row 1:  #5820  (screen rows 8–15)
  ...
  Char row 23: #5AE0  (screen rows 184–191)
```

---

## Cross-References

- **48K memory and ports** (what lives where): [memory_and_io_48k.md](memory_and_io_48k.md)
- **128K memory and ports** (banking, shadow screen): [memory_and_io_128k.md](memory_and_io_128k.md)
- **Contention model** (why screen access is slow during display): [contention_model.md](contention_model.md)
- **Graphics techniques** (sprites, scrolling, multicolor): [06_graphics/README.md](../06_graphics/README.md)
- **Attribute color system** (INK, PAPER, BRIGHT, FLASH): [color_system.md](../05_display_and_timing/color_system.md)
- **Complete I/O port map** (all ports, all models, decoding bitmasks): [io_port_map.md](../../10_references/io_port_map.md)

## References

### External references

- [Chris Smith — The ZX Spectrum ULA](http://www.zxdesign.info/) — definitive reference for the pixel/attribute interleaving scheme (every 3rd display byte is an attribute byte), the display file address-decode logic, and the off-screen memory holes at `#4000`–`#57FF` (display) and `#5800`–`#5AFF` (attributes).
- [Sinclair ZX Specifications](http://problemkaputt.de/zxdocs.htm) — the canonical pixel addressing formula (`((Y&192)<<5) | ((Y&7)<<8) | ((Y&56)<<5) | X`) and the attribute address formula.
- [Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip) — annotated 48K ROM showing how the `PRINT`, `PLOT`, and `CLS` routines compute display addresses using the standard formula.
- [Spectrumpedia](https://speccy.wiki/) — cross-model reference covering the 128K shadow screen at `#C000`–`#FFAF` and the Soviet clones' alternate screen banks.
- [zx-pk.ru screen layout discussions](https://zx-pk.ru) — Russian-language threads on Pentagon / Scorpion alternate-screen banking and the demoscene techniques that exploit multiple screen buffers.
