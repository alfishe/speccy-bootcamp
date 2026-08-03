[← Home](../README.md) · [References](README.md)

# ZX Spectrum Character Set — Codes, ROM Font, UDG, Tokens

The ZX Spectrum's character set is an 8-bit code with the lower 96 entries modeled on ASCII (with Spectrum-specific symbols replacing the standard punctuation at `#5B`–`#60`), the middle range used for **block graphics** characters, and the upper range used for **BASIC keyword tokens**. This article is the reference table: code → character, ROM address, pixel pattern, and how to redirect or replace the font.

For the 48K ROM internals (including token system, line storage, character routines), see [rom_48k.md](../04_operating_systems/rom_48k.md). For the system variable table, see [system_variables.md](../04_operating_systems/system_variables.md).

---

## Code Ranges

| Range | Count | Type | Notes |
|---|---|---|---|
| `#00`–`#1F` | 32 | **Control** | `#0D` = newline, `#06` = comma-print, `#16` = `INK`/`PAPER` control — see ROM docs |
| `#20`–`#5A` | 59 | **ASCII printable** | Space, punctuation, digits `0`–`9`, uppercase `A`–`Z` |
| `#5B`–`#60` | 6 | **Spectrum-specific** | `£` `#5B`, `?` `#5C`, `©` `#5D`, `→` `#5E`, `←` `#5F`, `` ` `` `#60` |
| `#61`–`#7A` | 26 | **ASCII lowercase** | `a`–`z` (lowercase sits on baseline — no descenders) |
| `#7B`–`#7E` | 4 | **ASCII punctuation** | `{` `|` `}` `~` |
| `#7F` | 1 | **Inverse space** | Solid block of ink color — the classic "ink block" character |
| `#80`–`#8F` | 16 | **Mosaic graphics (2×2)** | All 16 combinations of a 2×2 sub-cell × 4 pixels per row |
| `#90`–`#A4` | 21 | **UDG (built-in)** | User-definable graphics `A`–`U` (default patterns in ROM) |
| `#A5`–`#C4` | 32 | **Statement tokens** | `RND`, `INKEY$`, `PI`, `FN`, `POINT`, `SCREEN$`, `ATTR`, `AT`, `TAB`, `VAL$`, `CODE`, `VAL`, `LEN`, `SIN`, `COS`, `TAN`, `ASN`, `ACS`, `ATN`, `LN`, `EXP`, `INT`, `SQR`, `SGN`, `ABS`, `PEEK`, `IN`, `USR`, `STR$`, `CHR$`, `NOT`, `BIN` |
| `#C5`–`#FF` | 59 | **Keyword tokens** | `STEP`, `TO`, `THEN`, `LINE`, `+`, `-`, `*`, `/`, … `COPY`, `CLEAR`, `CLS`, `DOT`, … `LLIST`, `STOP`, `LPRINT`, …, `INK`, `PAPER`, `FLASH`, `BRIGHT`, `INVERSE`, `OVER`, `OUT`, `BORDER`, `CONTINUE`, `DIM`, `REM`, `FOR`, `GO TO`, `GO SUB`, `INPUT`, `LOAD`, `LIST`, `LET`, `PAUSE`, `NEXT`, `POKE`, `PRINT`, `PLOT`, `RUN`, `SAVE`, `RANDOMIZE`, `IF`, `CLS`, `DRAW`, `CLEAR`, `RETURN`, `COPY` |

> [!NOTE]
> Code `#7F` is **not ASCII DEL** on the Spectrum — it is the **inverse space** (solid ink block), commonly used for filled rectangles in BASIC graphics. The character is so useful that many programs start by POKEing `#7F` patterns of various widths into UDGs.

---

## ROM Font Layout

The 96 printable characters (`#20`–`#7F`) are stored as **96 × 8 = 768 bytes of pixel patterns** at the **end of the 48K ROM**:

| Symbol | Address | Notes |
|---|---|---|
| Character patterns | `#3D00`–`#3FFF` | 96 chars × 8 bytes each, occupying the final 768 bytes of the 16K ROM |
| Token spelling table | `#009C`–`#0239` | Keyword spellings (e.g., `PRINT` → bytes `P`,`R`,`I`,`N`,`T` with bit 7 set on last char) |
| `CHARS` system variable | `#5C36` | Default value `#3C00` = `#3D00 − #0100` (the −256 offset simplifies address calculation: font byte for code `c` = `CHARS + #0100 + (c − #20) × 8`) |

Each character is 8 bytes, one byte per pixel row. Bit 7 is the **leftmost** pixel, bit 0 is the rightmost. There are no descenders — lowercase letters `g`, `p`, `q` sit on the baseline, which keeps the cell boundary simple but reduces readability.

### Pixel Order in a Byte

```
Byte:  B7  B6  B5  B4  B3  B2  B1  B0
Pixel: █   █   █   █   █   █   █   █
       ←─── left            right ───→
```

To set/clear a specific pixel column within a character row, use `AND`/`OR` masks:

```z80
; Turn on pixel column N (0-7, left to right) of byte at (HL)
SetPixelCol:
    LD   A,#80           ; Bit 7 = leftmost pixel
    RRCA                 ; Rotate right N times (N in B)
    DJNZ SetPixelCol-1   ; (B = 0 means column 0; B = 7 means column 7)
    OR   (HL)
    LD   (HL),A
    RET
```

---

## UDG — User-Defined Graphics

21 user-defined graphic characters occupy codes `#90`–`#A4`, displayed on screen as letters `A`–`U` (capital letters to distinguish from tokens). The default patterns are stored in the ROM and copied to RAM at boot.

| Item | Address | Notes |
|---|---|---|
| `UDG` system variable | `#5C7B` | Points to first UDG byte; default `#FF58` on 48K |
| Default UDG area | `#FF58`–`#FFCB` | 21 chars × 8 bytes = 168 bytes, sits below `RAMTOP` |
| UDG character codes | `#90`–`#A4` | `A`=144, `B`=145, …, `U`=164 |

### Defining a UDG from BASIC

```basic
10 POKE 23675, PEEK 23675 : REM ensure UDG pointer is at default
20 FOR n = USR "A" TO USR "A" + 7
30 READ d : POKE n, d
40 NEXT n
50 DATA 60, 126, 219, 255, 219, 126, 60, 0
```

`USR "A"` evaluates to `#FF58` (UDG for letter `A`); `USR "U"` evaluates to `#FF58 + 20 × 8 = ##FF58 + 160 = ##FFF8`.

### Defining a UDG from Assembly

```z80
; Point the UDG system variable at a custom 168-byte table
    LD   HL,CustomUDGs
    LD   (#5C7B),HL       ; Set UDG pointer
    RET

CustomUDGs:
    ; 21 chars × 8 bytes = 168 bytes
    DB   60,126,219,255,219,126,60,0    ; Char A — smiley face
    DB   ...                            ; Char B
    ; ... (21 total)
```

### Inverse Video of UDGs

The ROM provides inverse video by OR-ing the pattern bytes with `#FF` and toggling bit 7 of the character code. Code `#90` + `#80` = `#10` is not used — instead, the ROM reuses the same bytes with the video inversion handled at print time. To **manually invert** a UDG, flip all bits of its 8 bytes.

---

## CHARS System Variable — Custom Fonts

The `CHARS` system variable at `#5C36` points to the start of the printable character table **minus 256 bytes** (this offset lets the ROM multiply a character code by 8 and add without subtracting the code-space offset). To redirect font output to a custom table:

```z80
; Install a custom font at #8000 (must be 768 bytes for codes #20-#7F)
    LD   HL,#8000 - 256      ; CHARS stores address - 256
    LD   (#5C36),HL          ; Update CHARS
    RET

CustomFont:
    ; 96 chars × 8 bytes = 768 bytes
    ; Char #20 (space) = 8 zero bytes
    ; Char #21 (!) = pixel pattern for '!'
    DB   0,0,0,0,0,0,0,0
    ; ... 760 more bytes
```

> [!WARNING]
> Custom fonts must be **contended RAM-aware** if placed in `#4000`–`#7FFF`. Reading from contended font RAM during the paper area slows down character printing. Place custom fonts in **uncontended RAM** (`#8000`+) for maximum speed.

---

## Printing Characters from Assembly

### Method 1: Direct Screen Write

```z80
; Print character A at row D, col E using a custom font
PrintChar:
    ; Convert row/col to screen address
    LD   H,#40              ; Screen base
    LD   L,D                ; (Simplified — real code uses attr/pixel split)

    ; Get font address for char A
    PUSH HL
    LD   L,A
    LD   H,0
    ADD  HL,HL              ; × 8 (3 shifts)
    ADD  HL,HL
    ADD  HL,HL
    LD   DE,(#5C36)         ; CHARS - 256
    INC   D                  ; + 256 (one INC D = +256)
    ADD  HL,DE              ; HL = address of 8-byte pattern
    POP  DE                  ; (Restore screen address)

    ; Copy 8 bytes to screen (one per row, with row stride)
    LD   B,8
.loop:
    LD   A,(HL)
    LD   (DE),A
    INC  HL
    INC  D                  ; Next screen row (attr line stride)
    DJNZ .loop
    RET
```

### Method 2: ROM `RST #10` (PRINT_CHAR)

```z80
; Use the ROM's character printer (handles colours, cursor, scrolling)
    LD   A,(#5C3C)          ; CURCH system variable holds char to print
    RST  #10                ; ROM routine PRINT_CHAR
```

`RST #10` prints the character in register A at the current cursor position, advances `S_POSN`, handles scrolling, and respects `ATTR_P`/`INK`/`PAPER`/`FLASH`/`BRIGHT`/`INVERSE`/`OVER`. Slower than direct screen write but maintains consistency with BASIC output.

---

## Token Encoding — BASIC Keywords

BASIC keywords (`PRINT`, `IF`, `GOTO`, etc.) are stored as **single bytes** `#A5`–`#FF` rather than ASCII text. This saves RAM (1 byte vs 5 for "PRINT") and speeds parsing.

| Token byte | Keyword | Token byte | Keyword |
|---|---|---|---|
| `#A5` | `RND` | `#CE` | `<` |
| `#A6` | `INKEY$` | `#CF` | `>` |
| `#A7` | `PI` | `#D0` | `LINE` |
| `#C0` | `NOT` | `#CB` | `THEN` |
| `#C1` | `BIN` | `#CD` | `TO` |
| `#C2` | `OR` | `#CC` | `STEP` |
| `#C3` | `AND` | `#CA` | `<>` |
| `#F5` | `PRINT` | `#EA` | `LET` |
| `#F6` | `RUN` | `#EB` | `PAUSE` |
| `#F7` | `LOAD` | `#EC` | `NEXT` |
| `#F8` | `LIST` | `#ED` | `POKE` |
| `#F9` | `SAVE` | `#EF` | `PRINT` (alt form) |
| `#FA` | `RANDOMIZE` | `#F1` | `PLOT` |
| `#FB` | `IF` | `#F2` | `RUN` (alt) |
| `#FC` | `CLS` | `#F3` | `SAVE` (alt) |
| `#FD` | `DRAW` | `#F4` | `RANDOMIZE` (alt) |
| `#FE` | `CLEAR` | | |
| `#FF` | `RETURN` | | |

For the complete keyword list (32 statement keywords + 27 function/ operator tokens), see [basic_token_table.md](basic_token_table.md) (planned).

### Tokenizing and Detokenizing

When BASIC parses user input (`P` `R` `I` `N` `T` typed as keystrokes), it matches the characters against the token spelling table at `#009C` and replaces the matched sequence with the single token byte. The matching is greedy — longest match wins.

To detokenize (display a stored BASIC line), the ROM walks the token table at `#009C` for each token byte and emits the stored spelling with bit 7 of the **last character** cleared (so `PRINT` is stored as `P`,`R`,`I`,`N`,$`T` — `$T` meaning `T` with bit 7 set).

---

## International Variants

The Spectrum's character set was customized for different markets:

| Region | Character | Code | Notes |
|---|---|---|---|
| UK (default) | `£` | `#5B` | Pound sign |
| Spanish (Investronica) | `Ñ`, `Ü`, `¿`, `¡` | mixed | Spanish ROM adds accented chars and inverted punctuation |
| Russian (Pentagon clones) | Cyrillic `А`–`Я` | replaces UDG | Custom ROM banks swap the font with Cyrillic |
| Russian ProfROM | Mixed Latin/Cyrillic | mixed | Scorpion's ProfROM supports both Latin and Cyrillic |

On the Pentagon and other Soviet clones, a common convention is to store **two font tables** (Latin + Cyrillic) and switch between them by toggling a ROM bank or updating `CHARS`. The Cyrillic font uses the same 8×8 cell layout but replaces the UDG block-graphics characters with Cyrillic letters.

---

## Cross-References

- **48K ROM internals** (token table, character routines, font address): [rom_48k.md](../04_operating_systems/rom_48k.md)
- **System variables** (`CHARS`, `UDG`, `RASP`, `CH_ADD`): [system_variables.md](../04_operating_systems/system_variables.md)
- **48K memory map** (where the font lives in RAM/ROM): [memory_and_io_48k.md](../05_development/03_memory_and_io/memory_and_io_48k.md)
- **Custom fonts, proportional text, 64-column modes** (uses UDG mechanism): see the [Graphics section](../05_development/06_graphics/README.md) for coverage of font rendering techniques
- **Screen layout** (attribute/pixel byte mapping): [screen_layout.md](../05_development/03_memory_and_io/screen_layout.md)
- **BASIC token table** (complete keyword→token mapping): [basic_token_table.md](basic_token_table.md) (planned)
