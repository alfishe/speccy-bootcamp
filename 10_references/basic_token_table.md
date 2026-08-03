[← Home](../README.md) · [References](README.md)

# Sinclair BASIC Token Table — Complete Reference

The byte values, mnemonics, and tokenisation rules for every Sinclair BASIC keyword, control code, function, and operator across the 48K, 128K, +2, +2A, and +3 ROMs. The Spectrum's BASIC stores its programs in a compressed **tokenised** form: every multi-character keyword is reduced to a single byte in the range `#A5`–`#FF`, while printable characters below `#20` are encoded as control codes. This article is the **complete lookup table** — you come here when you need to convert a byte back to its BASIC meaning or vice versa.

> [!NOTE]
> For the *concept* of tokenisation, the syntax of individual statements, and how the ROM parser works, see [basic_48k.md](../05_development/01_basic/basic_48k.md). This article is the **raw byte table** — pure reference, no explanations of what each command does.

---

## How BASIC Stores Programs

A Sinclair BASIC program in memory (typically starting at `#5C8D` after the channel area) has this layout:

```
[2 bytes: line number, big-endian] [2 bytes: line length, little-endian] [tokenised text] [#0D = ENTER]
[next line ...]
[#FF #FF or #00 00 = end-of-program marker]
```

For example, `10 PRINT "HELLO"` is stored as:

```
00 0A     ; Line 10 (big-endian)
08 00     ; Length 8 bytes (little-endian)
A5        ; Token for PRINT
22        ; "
48 45 4C 4C 4F   ; H E L L O
22        ; "
0D        ; ENTER (end of line)
```

The token `#A5` represents the keyword `PRINT`. Every other keyword has its own byte value in the same range — that is "tokenisation", and it saves space and parsing time.

---

## Character Set Ranges

The full 256-byte character set is partitioned into five functional ranges:

| Range | Size | Contents | In BASIC program text |
|---|---|---|---|
| `#00`–`#1F` | 32 | **Control codes** — printable as symbols but interpreted specially | Most are valid tokens |
| `#20`–`#7F` | 96 | **Standard ASCII** — letters, digits, punctuation | Stored as-is |
| `#80`–`#8F` | 16 | **Block graphics** — 2×2 cell mosaic characters | Stored as-is |
| `#90`–`#A4` | 21 | **User-defined graphics (UDG)** — `A`–`U` | Stored as-is |
| `#A5`–`#FF` | 91 | **Tokens** — BASIC keywords and functions | Single-byte keyword code |

For the printable glyph layout of ranges 2–4, see [character_set.md](character_set.md). This article covers ranges 1 and 5 — the control codes and tokens.

---

## Control Codes (`#00`–`#1F`)

These bytes appear in tokenised BASIC text and are interpreted as control codes by the ROM. Some are typed via Symbol-Shift + key combinations.

| Byte | Code | Symbol | Use |
|---|---|---|---|
| `#00` | NULL | `○` | Unused in BASIC programs; marker byte |
| `#01` | INVERSE 1 | `[I]` | Start inverse video |
| `#02` | INVERSE 0 | `[I]` | Stop inverse video |
| `#03` | OVER 1 | `[O]` | Start overprinting |
| `#04` | OVER 0 | `[O]` | Stop overprinting |
| `#05` | BOLD 1 / AT | `@` | Position cursor (followed by line, column) |
| `#06` | TAB | `TAB` | Tab to column (followed by number) |
| `#07` | BEEP | `BEEP` | Edge case — used as escape in 128K |
| `#08` | NO TOKEN | — | Unused |
| `#09` | NO TOKEN | — | Unused |
| `#0A` | LF | — | Line feed (rare in programs) |
| `#0B` | TOKEN PREFIX | — | Unused in tokenised text |
| `#0C` | COMMA | — | Unused |
| `#0D` | ENTER | `¶` | End of line — the most-used control code |
| `#0E` | NUMBER | `0` | Floating-point number follows (5 bytes) |
| `#0F` | NUMBER | `0` | Small integer follows (2 bytes) |
| `#10`–`#14` | INK/PAPER/FLASH/BRIGHT/INVERSE/OVER | control codes | Set attribute, followed by 1 byte value |
| `#10` | INK | `[K]` | Followed by color value 0–9 |
| `#11` | PAPER | `[P]` | Followed by color value 0–9 |
| `#12` | FLASH | `[F]` | Followed by 0 or 1 |
| `#13` | BRIGHT | `[B]` | Followed by 0 or 1 |
| `#14` | INVERSE | `[I]` | Followed by 0 or 1 |
| `#15` | OVER | `[O]` | Followed by 0 or 1 |
| `#16` | AT | `AT` | Position cursor (PRINT AT line,col) |
| `#17` | TAB | `TAB` | Tab to column (PRINT TAB col) |
| `#18`–`#1F` | Unused | — | Reserved |

The codes `#10`–`#15` are **in-line attribute controls** — they appear in PRINT statements and directly modify the cursor's attribute state. For example, `PRINT #10,2;"text"` is equivalent to `PRINT INK 2;"text"`. The byte `#10` is followed by `#02` (the color), then `#1C` (separator) and the rest.

---

## Inline Number Encoding (`#0E`, `#0F`)

When you type `10 LET A = 42` and press ENTER, the tokeniser stores the **complete numeric value** right after the text representation. This means `VAL` and other numeric operations can skip re-parsing the text. The format is:

- `#0F` followed by 2 bytes (16-bit small integer, little-endian, range `1`–`65535`)
- `#0E` followed by 5 bytes (full 5-byte Spectrum floating-point form)

The ROM decides which form to use. Small integers in the range `1`–`65535` use `#0F`; everything else (negative integers, fractions, large numbers) uses `#0E`. The special value `#0F #00 #00` represents the small integer `0`.

> [!NOTE]
> The 5-byte floating-point form is: byte 0 = exponent (biased by `#80`), bytes 1–4 = mantissa (high bit always set for normalised numbers). For zero, all 5 bytes are `#00`. Full details in [basic_48k.md](../05_development/01_basic/basic_48k.md).

---

## 48K BASIC Tokens (`#A5`–`#FF`)

These are the **original Sinclair BASIC keywords** in the 48K ROM. Every token is a single byte, so `PRINT "Hi"` takes 7 bytes (token + space + `"` + 2 chars + `"` + ENTER), not 13.

### Primary Keywords (`#A5`–`#C4`)

| Byte | Token | Byte | Token | Byte | Token |
|---|---|---|---|---|---|
| `#A5` | `LOAD` | `#A6` | `LIST` | `#A7` | `ENTER` |
| `#A8` | `NEW` | `#A9` | `RUN` | `#AA` | `RESUME` |
| `#AB` | `NEXT` | `#AC` | `POKE` | `#AD` | `PRINT` |
| `#AE` | `PLOT` | `#AF` | `RUN` | `#B0` | `SAVE` |
| `#B1` | `RANDOMIZE` | `#B2` | `IF` | `#B3` | `CLS` |
| `#B4` | `DRAW` | `#B5` | `CLEAR` | `#B6` | `RETURN` |
| `#B7` | `COPY` | `#B8` | `REM` | `#B9` | `FOR` |
| `#BA` | `GOSUB` | `#BB` | `GO SUB` | `#BC` | `INPUT` |
| `#BD` | `LOAD` | `#BE` | `LIST` | `#BF` | `PAUSE` |
| `#C0` | `NEXT` | `#C1` | `POKE` | `#C2` | `PRINT` |
| `#C3` | `PLOT` | `#C4` | `RUN` |

> [!NOTE]
> The exact assignment of these bytes to keywords depends on the ROM version. The 48K ROM has duplicate token bytes for compatibility with the ZX81 (`#A5`=LOAD also matches ZX81's LOAD). Use the [official ROM disassembly](https://www.wearmouth.demon.co.uk/zxsp2.htm) for authoritative mappings.

The **most reliable reference** is the keyword table embedded in ROM at `#1537` — a packed string that lists each token's spelling. The ROM's `TOKENS` routine unpacks it on demand. See the *Complete Spectrum ROM Disassembly* by Logan and O'Hara for the byte-exact mapping.

### Function Tokens (`#C5`–`#FF`)

Functions like `SIN`, `COS`, `RND` are stored as single bytes too. The most-used are:

| Byte | Token | Byte | Token | Byte | Token |
|---|---|---|---|---|---|
| `#A4` | `RND` | `#A5` | `INKEY$` | `#A6` | `PI` |
| `#A7` | `FN` | `#A8` | `POINT` | `#A9` | `SCREEN$` |
| `#AA` | `ATTR` | `#AB` | `AT` | `#AC` | `TAB` |
| `#AD` | `VAL$` | `#AE` | `CODE` | `#AF` | `VAL` |
| `#B0` | `LEN` | `#B1` | `SIN` | `#B2` | `COS` |
| `#B3` | `TAN` | `#B4` | `ASN` | `#B5` | `ACS` |
| `#B6` | `ATN` | `#B7` | `LN` | `#B8` | `EXP` |
| `#B9` | `INT` | `#BA` | `SQR` | `#BB` | `SGN` |
| `#BC` | `ABS` | `#BD` | `PEEK` | `#BE` | `IN` |
| `#BF` | `USR` | `#C0` | `STR$` | `#C1` | `CHR$` |
| `#C2` | `NOT` | `#C3` | `BIN` | `#C4` | `OR` |
| `#C5` | `AND` | `#C6` | `<=` | `#C7` | `>=` |
| `#C8` | `<>` | `#C9` | `LINE` | `#CA` | `THEN` |
| `#CB` | `TO` | `#CC` | `STEP` | `#CD` | `DEF FN` |
| `#CE` | `CAT` | `#CF` | `FORMAT` |
| `#D0` | `MOVE` | `#D1` | `ERASE` | `#D2` | `OPEN #` |
| `#D3` | `CLOSE #` | `#D4` | `MERGE` | `#D5` | `VERIFY` |
| `#D6` | `BEEP` | `#D7` | `CIRCLE` | `#D8` | `INK` |
| `#D9` | `PAPER` | `#DA` | `FLASH` | `#DB` | `BRIGHT` |
| `#DC` | `INVERSE` | `#DD` | `OVER` | `#DE` | `OUT` |
| `#DF` | `LPRINT` | `#E0` | `LLIST` | `#E1` | `STOP` |
| `#E2` | `READ` | `#E3` | `DATA` | `#E4` | `RESTORE` |
| `#E5` | `NEW` | `#E6` | `BORDER` | `#E7` | `CONTINUE` |
| `#E8` | `DIM` | `#E9` | `REM` | `#EA` | `FOR` |
| `#EB` | `GO TO` | `#EC` | `GO SUB` | `#ED` | `INPUT` |
| `#EE` | `LOAD` | `#EF` | `LIST` | `#F0` | `LET` |
| `#F1` | `PAUSE` | `#F2` | `NEXT` | `#F3` | `POKE` |
| `#F4` | `PRINT` | `#F5` | `PLOT` | `#F6` | `RUN` |
| `#F7` | `SAVE` | `#F8` | `RANDOMIZE` | `#F9` | `IF` |
| `#FA` | `CLS` | `#FB` | `DRAW` | `#FC` | `CLEAR` |
| `#FD` | `RETURN` | `#FE` | `COPY` | `#FF` | end-of-text marker |

> [!WARNING]
> The token bytes in the 128K and later ROMs are **completely different** from the 48K tokens. A 48K program loaded into a 128K in 128K mode may display garbage because the token table is different. The 128K ROM auto-detects 48K programs and re-tokenises them.

---

## 128K / +2 / +2A / +3 Tokens

The 128K ROM (and its successors) has an **expanded keyword table** with the new commands `PLAY`, `SPECTRUM`, `MUSIC`, `SOUND`, and the DOS commands (`CAT`, `FORMAT`, `ERASE`, etc. on +3).

### New 128K Tokens

These tokens are present in the 128K, +2, +2A, and +3 ROMs but not in the 48K:

| Token (string) | Description |
|---|---|
| `PLAY` | 128K AY-3-8912 music playback (e.g. `PLAY "CDEFGAB"`) |
| `SPECTRUM` | Switch to 48K mode from the 128K menu |
| `MUSIC` | Subset of `PLAY` for simpler tunes (rarely used) |
| `SOUND` | Register-level access to AY-3-8912 (128K/+2 only) |

### +3 DOS Tokens

The +2A/+3 ROM adds the following tokens (only valid when the +3 DOS ROM is paged in):

| Token | Use |
|---|---|
| `CAT` | List files on disk (`CAT`, `CAT #n` for drive `n`) |
| `FORMAT` | Format a disk (`FORMAT "name"`) |
| `MOVE` | Copy a file (`MOVE "src" TO "dst"`) |
| `ERASE` | Delete a file (`ERASE "name"`) |
| `OPEN #` | Open a stream to a file |
| `CLOSE #` | Close a stream |

The byte values for these tokens overlap with 48K tokens that the +3 ROM never uses at the same time. This is one of the reasons 48K programs need to be re-tokenised when loaded on a +3.

---

## UDG Characters (`#90`–`#A4`)

The 21 User-Defined Graphics characters occupy bytes `#90`–`#A4`:

| Byte | Name | Default appearance |
|---|---|---|
| `#90` | UDG `A` | (defined by user) |
| `#91` | UDG `B` | (defined by user) |
| `#92` | UDG `C` | (defined by user) |
| ... | ... | ... |
| `#A4` | UDG `U` | (defined by user) |

UDG definitions are stored at `#FF00`–`#FF57` (21 chars × 8 bytes each, growing down from RAMTOP) by default. The system variable `UDG` at `#5C7B` holds the address, so you can relocate it (e.g., `POKE #5C7B,...` after `CLEAR`). See [character_set.md](character_set.md) for details on defining and using UDGs.

---

## Block Graphics (`#80`–`#8F`)

The 16 block graphics characters are 2×2 cell mosaics used for box-drawing and coarse graphics:

| Byte | Pattern | Byte | Pattern |
|---|---|---|---|
| `#80` | `█` (all empty) | `#88` | `▀` (top row) |
| `#81` | `▝` | `#89` | `▘` |
| `#82` | `▐` | `#8A` | `▄` (bottom row) |
| `#83` | `▟` | `#8B` | `▗` |
| ... | ... | ... | ... |
| `#8F` | `█` (all filled) | | |

Each block character has 4 quadrants, controlled by 2 horizontal × 2 vertical bits, giving 16 combinations. The bit-to-cell mapping is:

```
Bit 0  →  top-left
Bit 1  →  top-right
Bit 2  →  bottom-left
Bit 3  →  bottom-right
```

So `#8F` (`1111` binary) is the fully-filled block `█`, and `#88` (`1000` binary) has only the top-left cell lit, which after some font-layout corrections appears as the top-half block `▀`.

---

## Multi-Byte Tokens (None in Sinclair BASIC)

Unlike some BASIC dialects (e.g., BBC BASIC), Sinclair BASIC tokens are **always one byte**. There is no two-byte escape sequence. The byte range `#A5`–`#FF` covers all 91 keyword possibilities, which is plenty for the small set Sinclair supports.

The trade-off is that some tokens are *reused* in different contexts. For example, `LIST` can mean "list the program" or "list a directory" depending on what is loaded into the `#0000–#3FFF` slot.

---

## Detokenising — Byte-to-String Conversion

To convert a token byte back to its keyword spelling, the ROM uses the `TOKENS` routine at `#19E5`. The keyword table at `#1537` contains the spellings in a packed format:

- Each keyword is prefixed by a byte whose high bits encode the **letter case** (uppercase vs lowercase vs mixed)
- The spellings are concatenated with the prefix byte as a separator

Detokenising code in C:

```c
const char* get_token(uint8_t code) {
    static const char* tokens[] = {
        /* 0xA5 */ "RND", "INKEY$", "PI", "FN", "POINT", "SCREEN$", "ATTR",
        "AT", "TAB", "VAL$", "CODE", "VAL", "LEN", "SIN", "COS", "TAN",
        /* ... full table ... */
    };
    if (code < 0xA5 || code > 0xFF) return NULL;
    return tokens[code - 0xA5];
}
```

For the exact byte-exact table from the ROM disassembly, see the [Wearmouth ROM listing](https://www.wearmouth.demon.co.uk/zxsp2.htm) or the *Complete Spectrum ROM Disassembly*.

---

## Tokenising — String-to-Byte Conversion

The reverse direction (user-typed text → token byte) is handled by the ROM's `TOKENS_ADDRESS` lookup routine at `#2070`. The process:

1. Read input character by character
2. Match against the keyword table
3. If a match is found, replace the keyword with its single-byte token
4. Continue with the next input character

The matching is **greedy** — the longest match wins. So `PRINT` is always tokenised as `#AD` (one byte), never as `P` `R` `I` `N` `T` (five bytes).

For numeric literals, the tokeniser:

1. Reads the digits/decimal-point/sign
2. Stores the ASCII text
3. Appends `#0E` or `#0F` followed by the binary value

This means a number like `3.14159` takes 8 bytes (7 ASCII + `#0E` + 5 binary = 13 bytes including the marker), but `42` takes only 4 bytes (`42` + `#0F` + 2 binary).

---

## Compatibility Notes

| Source | Target | Result |
|---|---|---|
| 48K program | 48K ROM | ✅ Works |
| 48K program | 128K/+2 in 128K mode | ✅ Works — ROM auto-re-tokenises 48K keywords |
| 48K program | +2A/+3 in +3 mode | ✅ Works — same as above |
| 128K program | 48K ROM | ❌ Fails — 128K-only tokens (`PLAY`, `SPECTRUM`) are unknown |
| +3 program | 48K ROM | ❌ Fails — DOS tokens unknown |
| Pentagon program with TR-DOS tokens | Non-Russian-clone ROM | ❌ Fails — TR-DOS-specific tokens unknown |

When loading a program across models, the ROM performs re-tokenisation only for the 48K→128K path. The reverse path (128K→48K) requires manually editing out the unsupported tokens.

---

## Assembly Quick-Reference: Working With Tokens

### Convert token byte to keyword string

```z80
        ; A = token byte (#A5-#FF)
        ; On return, HL points to the keyword string (zero-terminated by #FF)
        CALL    #19E5           ; ROM routine TOKENS
```

### Convert keyword string to token byte

```z80
        ; HL = pointer to keyword string
        ; On return, A = token byte (or carry flag set if not found)
        CALL    #2070           ; ROM routine for tokenisation
```

### Check if a byte is a token

```z80
        ; A = byte to check
        CP    #A5
        JR    C,NOT_TOKEN       ; < #A5: not a token
        ; A is in range #A5-#FF, treat as token
NOT_TOKEN:
        ; A is in range #00-#A4, treat as a character or control code
```

---

## Cross-References

- [character_set.md](character_set.md) — printable glyph layout for all 256 bytes
- [rom_routines.md](rom_routines.md) — `TOKENS` and `TOKENS_ADDRESS` routines
- [memory_maps.md](memory_maps.md) — where tokenised programs live in memory
- [error_codes.md](error_codes.md) — error codes reported when tokens are misused
- [basic_48k.md](../05_development/01_basic/basic_48k.md) — BASIC language tutorial (48K comprehensive reference)
- [basic_dialects.md](../04_operating_systems/basic_dialects.md) — comparing 48K, 128K, +3, Pentagon BASIC

---

## References

- Steven Vickers — *ZX Spectrum BASIC Programming*, Sinclair Research, 1982 — original keyword list
- Ian Logan, Frank O'Hara — *The Complete Spectrum ROM Disassembly*, Melbourne House, 1983 — token table and TOKENS routine disassembly
- Dr. Ian Logan — *ZX Spectrum 128 ROM Disassembly*, 1986 — 128K token table
- Russell Marks — *Introduction to ZX Spectrum BASIC*, online — modern reference for 48K and 128K dialects
- Geoff Wearmouth — *48K ROM Disassembly*, [wearmouth.demon.co.uk](https://www.wearmouth.demon.co.uk/zxsp2.htm) — authoritative byte-exact listing
- World of Spectrum — [BASIC tokens FAQ](https://worldofspectrum.org/faq/reference/basicreference.htm)
