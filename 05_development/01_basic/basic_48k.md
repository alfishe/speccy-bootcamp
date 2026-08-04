[← Home](../../README.md) · [BASIC](README.md)

# Sinclair BASIC (48K) — Comprehensive Reference

The ZX Spectrum boots straight into BASIC. There is no operating system, no shell, no `COMMAND.COM` — the moment the ROM finishes its power-on self-test, the user is staring at a `(C) 1982 Sinclair Research Ltd` banner and a flashing K cursor, ready to type a BASIC line. On a 16K machine with nothing loaded, BASIC *is* the entire user-facing environment.

Sinclair BASIC is **not a fast language**. A `FOR/NEXT` loop counting to 1000 takes roughly 10 seconds — about a hundredth the speed of the same loop in compiled Z80 machine code. What it is, however, is **the universal entry point** to the machine: every Spectrum programmer starts here, every demo and game ultimately boots through some ROM interaction, and every article on assembly development on this site assumes the reader has internalized BASIC's quirks.

This article is a **single comprehensive reference** to the 48K BASIC dialect: the token system, the variable model, the memory layout, the floating-point format, the parser, the graphics commands (`PLOT`, `DRAW`, `CIRCLE`, `POINT`, `ATTR`), sound (`BEEP`), and the bridge to machine code (`PEEK`, `POKE`, `USR`). The 128K-specific extensions (extended editor, `PLAY`/`SOUND`/`MUSIC`, AY-3-8912 access, `BANK`) are covered in the companion article [basic_128k.md](basic_128k.md).

> [!NOTE]
> For the byte-level token table (every keyword's numeric code), see [basic_token_table.md](../../10_references/basic_token_table.md). For ROM routines callable from assembly, see [rom_routines.md](../../10_references/rom_routines.md).

---

## What Sinclair BASIC Is (and Isn't)

Sinclair BASIC is a dialect of BASIC derived from the ZX81's ROM, itself derived from the ZX80's. It conforms roughly to the **ECMA-55 Minimal BASIC standard**, with extensions for graphics and sound that were specific to the Spectrum hardware. The defining characteristics:

| Trait | Sinclair BASIC | Typical Microsoft BASIC (C64, MSX, IBM PC) |
|---|---|---|
| **Storage** | In ROM (16 KB on 48K) | In ROM (varies) |
| **Tokenization** | Single-byte tokens for all keywords | Multi-byte tokens, sometimes abbreviated |
| **Line entry** | **One line at a time** (immediate syntax check) | Whole-screen editor, RUN to check |
| **Variables** | Floating-point default, no integer type | Integer (`%`) and floating-point (`!`) variants |
| **String type** | Single string variable (`A$`), no string arrays in 48K | String arrays supported |
| **ELSE** | **Not supported** — every IF is one branch | `IF ... THEN ... ELSE ...` |
| **DO/WHILE** | **Not supported** — only `FOR` and `IF/GOTO` | Supported |
| **Editor** | **Per-line**, ENTER submits, full line is re-tokenized | Full-screen editor |
| **Graphics** | `PLOT`, `DRAW`, `CIRCLE` — hardware-aware | Usually `PSET`, `LINE` — generic |
| **Sound** | `BEEP` only (beeper) | `PLAY`, `SOUND`, AY/SID access |
| **Floating point** | 5 bytes (1 exponent + 4 mantissa) | Same 5-byte Microsoft format |

The lack of `ELSE`, the lack of `DO/WHILE`, the lack of an integer variable type, and the per-line editor are the four things that most often surprise programmers coming from Microsoft BASIC dialects. Each is a deliberate design choice — Sinclair optimized for **minimal ROM footprint** over programmer convenience.

### The Three ROM Versions

| ROM | Used in | BASIC behavior | Notes |
|---|---|---|---|
| **48K ROM** | Spectrum 16K, 48K, +, Spanish 128K (in 48K mode) | Original dialect | All examples in this article work on this ROM |
| **128K ROM** | 128K, +2 (grey) | Adds `PLAY`, `SPECTRUM`, `MUSIC`, `SOUND`, plus a menu-driven editor | Token table is **different** — programs auto-retokenize on load |
| **+2A/+3 ROM** | +2A (black), +3 | Adds +3DOS file commands (`CAT`, `FORMAT`, `ERASE`, `MOVE`, `OPEN #`) | Bugs fixed, but slower `LOAD`/`SAVE` detection |

The 128K ROM's different token table is a frequent source of confusion. Loading a 48K program saved with `SAVE "X" LINE 0` into a 128K Spectrum running in 128K mode will work — the 128K ROM detects the old token set and re-tokenizes. But inspecting the bytes in memory will show **different byte values** for the same keywords. The 128K-specific extensions are covered in [basic_128k.md](basic_128k.md).

---

## Memory Layout — Where BASIC Lives

The Spectrum's 16 KB ROM contains the BASIC interpreter, editor, floating-point library, and a fixed set of system variables at the bottom of RAM. The interpreter manipulates memory through a set of **system variables** in the range `#5C00`–`#5CB6`. Every BASIC program lives in a single contiguous region of RAM called `PROG`:

```
ROM (#0000–#3FFF): BASIC interpreter, editor, calculator
─────────────────────────────────────────────────────────
RAM (#8000 onwards on 48K, but RAM starts at #5CB3):
  #5C00–#5CB6   System variables (183 bytes)
  #5CB3–?       Printer buffer (256 bytes, but variable)
  #5CCB–?       Channel information area (varies)
  #5C8D / PROG  Program area — your BASIC program in tokenized form
  ...           Variables area (numeric, string, array variables)
  ...           Free RAM (grows down from top of RAM)
  #FF57 / RAMTOP  Top of RAM, set by NEW on boot
```

The key system variables a BASIC programmer needs to know:

| Address | Name | Purpose |
|---|---|---|
| `#5C8D` | `PROG` | Start of the BASIC program (always `#5C8D` after NEW) |
| `#5C53` | `VARS` | Start of the variables area (moves up as variables are created) |
| `#5C4B` | `E_LINE` | Address of the line being edited (or the work area) |
| `#5C59` | `STKEND` | End of the calculator stack (grows upward) |
| `#5C78` | `FRAMES` | 3-byte frame counter (incremented every 20 ms by the ROM ISR) |
| `#5C8B` | `RAMTOP` | Top of usable RAM (`#FF57` on a 48K) |
| `#5C36` | `ATTR_P` | Permanent attribute state (INK, Paper, etc.) |
| `#5C38` | `ATTR_T` | Temporary attribute state (used during PRINT) |
| `#5C3D` | `STRMS` | I/O stream table (5 bytes per stream, 16 streams max) |

For machine-code programmers, these are the variables you read or write to integrate with the BASIC environment. For BASIC programmers, they mostly matter when you start using `PEEK` and `POKE` — see the [PEEK, POKE, USR](#peek-poke-and-usr-bridging-basic-and-machine-code) section below.

### Program Storage Format

A BASIC program in memory is a sequence of **line records**, each consisting of a 4-byte header followed by the tokenized line text terminated by `#0D` (ENTER):

```
┌──────────────────────────────────────────────┐
│ Line number    │ 2 bytes, big-endian (0–9999) │
│ Line length    │ 2 bytes, little-endian        │
│ Tokenized text │ (length-2) bytes              │
│ ENTER          │ #0D                           │
└──────────────────────────────────────────────┘
Next line record ...
End-of-program marker: #FF #FF (or #80 #00 on 48K ROMs)
```

> [!IMPORTANT]
> The line length field is **little-endian** (low byte first) but the line number field is **big-endian** (high byte first). This is inconsistent and a frequent source of bugs in hand-written POKE-driven editors. The reason is historical: line numbers were inherited from the ZX81 which used big-endian for easier comparison (`CP` on the high byte first); lengths were added later and followed the Z80's natural little-endian convention.

The tokenized text is a mix of:

- **Tokens** (`#A5`–`#FF`) — single bytes for keywords like `PRINT`, `LET`, `GOTO`
- **ASCII characters** (`#20`–`#7F`) — variable names, numbers, operators, punctuation
- **Control codes** (`#10`–`#17`) — embedded attribute changes like `[K]` (INK)
- **Inline numbers** (`#0E` + 5 bytes or `#0F` + 2 bytes) — see [Floating-Point Format](#floating-point-format) below

For a worked example: the line `10 PRINT "HELLO"` is stored as 13 bytes:

```
00 0A        ; Line number 10 (big-endian)
08 00        ; Length 8 (little-endian) — covers 8 bytes after this field
F5           ; Token for PRINT  (48K token = #F5)
20           ; ASCII space
22           ; ASCII "
48 45 4C 4C 4F  ; ASCII "HELLO"
22           ; ASCII "
0D           ; ENTER
```

The full byte table is in [basic_token_table.md](../../10_references/basic_token_table.md).

---

## The Token System

Sinclair BASIC uses **single-byte tokens** for every keyword. There are no abbreviations in storage — `PRINT` is always exactly one byte (`#F5` in 48K tokens). This is one of the most compact BASIC storage formats ever designed; a Microsoft BASIC program for the C64 takes roughly 30–40% more bytes for the same source.

### Typing Tokens

The Spectrum keyboard has no separate letter keys for keywords. Instead, the user types tokens via the **keyword entry system**:

| Mode | Trigger | Result |
|---|---|---|
| **K mode** (keyword) | Press a key in the top row at the start of a line | Token is inserted: `p` produces `PRINT`, `r` produces `RUN` |
| **L mode** (letter) | Press a key after typing a token or letter | Letter is inserted: `p` produces lowercase `p` |
| **C mode** (extended) | Press `Caps Shift` + `Symbol Shift` together | Symbols and extended functions (`CODE`, `PEEK`, `USR`, etc.) |
| **E mode** (extended) | Press `Symbol Shift` then a key | Extended-mode functions (`READ`, `DATA`, `RESTORE`, etc.) |

The mode indicator is shown at the bottom-left of the screen: `K`, `L`, `C`, `E`, or `G` (for graphics characters in the `#90`–`#A4` range). The ROM's editor automatically switches modes based on context — after a token, it switches to L mode; at the start of a new statement, it switches back to K mode.

### Abbreviations

Because of the keyword entry system, the Spectrum has a unique feature: **abbreviations**. Most keywords have a short form that can be typed by holding `Symbol Shift` and pressing a sequence of letter keys:

| Abbreviation | Full keyword | Typed as |
|---|---|---|
| `P.` | `PRINT` | Symbol-Shift + P |
| `L.` | `LIST` | Symbol-Shift + L |
| `R.` | `RUN` | Symbol-Shift + R |
| `G.` | `GOTO` | Symbol-Shift + G |
| `F.` | `FOR` | Symbol-Shift + F |
| `N.` | `NEXT` | Symbol-Shift + N |

The ROM expands abbreviations on entry — the stored program always uses the full token, regardless of how it was typed. There are 42 abbreviations in total, listed in the Spectrum manual.

> [!NOTE]
> Abbreviations are an **editor feature**, not a separate token form. A line typed as `10 P. "HI"` is stored in memory exactly the same way as `10 PRINT "HI"` — both produce the 13-byte sequence shown above. The abbreviation only saves keystrokes, not memory.

---

## Variable Types

Sinclair BASIC has only **three variable types**, and all numeric variables are floating-point by default. There is no integer type (`A%` in Microsoft BASIC), no double-precision type, no unsigned type. This is a frequent source of confusion for programmers coming from other BASIC dialects.

### Numeric Variables

A numeric variable is created on first assignment:

```basic
10 LET SCORE = 0
20 LET HIGH_SCORE = 1000
30 LET PI_APPROX = 3.14159
```

Names can be **one letter** (`A`–`Z`) or **one letter followed by one digit** (`A0`–`Z9`). This gives 26 + 260 = **286 possible numeric variable names**. Names are case-sensitive in the sense that the ROM stores only uppercase letters and digits — typing `let score = 0` is stored as `LET SCORE = 0`.

> [!WARNING]
> The 48K ROM treats `SCORE` and `SC` as the **same variable** — it ignores trailing characters after the first letter or letter-digit pair. This means `LET TOTAL = 100` and `LET TIME = 50` both refer to the same variable `T`. The 128K ROM is stricter and rejects ambiguous names. Always use single-letter names or single-letter-plus-digit names to avoid this trap.

Each numeric variable occupies **5 bytes** in the variables area when stored — the 5-byte floating-point format described below.

### String Variables

String variables are denoted with a `$` suffix: `A$`, `B$`, ..., `Z$` (no digit suffix allowed for strings). There are exactly **26 string variable names** in 48K BASIC.

```basic
10 LET A$ = "HELLO"
20 LET N$ = "WORLD"
30 PRINT A$; " "; N$
```

A string variable is stored in memory as a 1-byte length field followed by the string's bytes. Assignments to the same name **replace** the previous value — strings are not accumulated. The maximum string length is limited only by free RAM (typically ~30 KB on a 48K).

### Arrays

Arrays are created with `DIM` and can be numeric or string. Multi-dimensional arrays are supported:

```basic
10 DIM A(10)              : REM 11-element numeric array (0 through 10)
20 DIM B(3, 4)            : REM 4x5 = 20-element 2D numeric array
30 DIM C$(3, 10)          : REM 4-element string array, each up to 10 chars
40 DIM D$(3, 5, 20)       : REM 3D string array (rarely used)
```

> [!IMPORTANT]
> Sinclair BASIC arrays are **1-indexed by default** but allow index 0. `DIM A(10)` creates elements `A(0)` through `A(10)` — eleven elements, not ten. This is the opposite of C and most modern languages.

---

## Floating-Point Format

Every numeric value in Sinclair BASIC — variable contents, array elements, constants in expressions — is stored as a **5-byte binary floating-point number**. The format is:

```
┌─────────┬─────────────────────────────────────┐
│ Byte 0  │ Exponent (biased, range #00–#FF)     │
│ Bytes 1–4 │ Mantissa (high bit always set)     │
└─────────┴─────────────────────────────────────┘
```

### Exponent

The exponent byte encodes a power of 2. The biased value `e_byte = exponent + #80`, where `exponent` ranges from -127 (`#00`) to +127 (`#FE`). The special value `#00` (biased) means **zero** — the entire 5 bytes are zero, regardless of mantissa.

### Mantissa

The mantissa is normalized so that **0.5 ≤ mantissa < 1.0** — the binary point is to the left of bit 7 of byte 1. Since the high bit is always set for a normalized number, the ROM could in principle use only 31 bits of storage and reuse bit 7 as a sign bit. Instead, the Spectrum keeps all 32 bits and uses a separate sign bit in the exponent byte's bit 7 — but only when the number is stored as a small integer (see below).

### Worked Examples

| Decimal value | Exponent byte | Mantissa bytes 1–4 |
|---|---|---|
| `0` | `#00` | `#00 #00 #00 #00` |
| `1` | `#81` | `#00 #00 #00 #00` (mantissa = 0.5, × 2^1 = 1) |
| `2` | `#82` | `#00 #00 #00 #00` |
| `0.5` | `#80` | `#00 #00 #00 #00` |
| `-1` | `#81` | `#00 #00 #00 #00` (sign bit handled differently — see below) |
| `3.14159` | `#82` | `#49 #0F #DB #22` (approximate) |

> [!WARNING]
> The Spectrum's sign handling is non-obvious. Negative numbers store the mantissa as a positive value, and the sign is tracked in a separate location during computation — typically the calculator's internal sign byte. When stored in a variable, the 5-byte form holds the magnitude only, and a sign bit is encoded in **exponent byte bit 7 of the next byte**. The full details are in the *Complete Spectrum ROM Disassembly*, chapters 10 and 11. Practically: do not try to bit-twiddle negative numbers in BASIC.

### Small Integer Optimization (`#0F`)

When the ROM tokenizes a literal small integer (range 1–65535), it stores it in a more compact form: `#0F` followed by 2 bytes little-endian. So `10 LET A = 42` stores 42 as:

```
0F 2A 00    ; #0F marker, then 42 little-endian (2A = 42)
```

This is the **inline integer form** — it is 3 bytes instead of the 6 bytes (`#0E` + 5-byte float) that the full floating-point form would take. The ROM's expression evaluator knows how to read either form.

---

## The Expression Evaluator (Calculator Stack)

When the BASIC interpreter encounters an expression like `2 + 3 * SIN(0.5)`, it does **not** generate a parse tree and walk it. Instead, it uses a **stack-based calculator** — the same kind of architecture as a Hewlett-Packard HP-15C or a Java VM. The ROM has a "calculator" routine at address `#30CB` (`STACK-COMMON`) that takes a single byte operand specifying the operation, performs it on the top one or two values of the calculator stack, and pushes the result.

The calculator stack lives just below the main program work area, growing downward from `STKEND` (system variable `#5C59`). Each stack slot is 5 bytes — one floating-point value.

### Operations

The ROM calculator has 44 built-in operations, each identified by a single byte:

| Byte | Operation | Effect |
|---|---|---|
| `#0F` | `ADD` | Push arg1 + arg2 |
| `#11` | `SUBTRACT` | Push arg1 − arg2 |
| `#13` | `MULTIPLY` | Push arg1 × arg2 |
| `#15` | `DIVIDE` | Push arg1 ÷ arg2 |
| `#1D` | `POWER` | Push arg1 ^ arg2 |
| `#1F` | `OR` | Logical OR (operands treated as 0 or 1) |
| `#21` | `AND` | Logical AND |
| `#23` | `NOT` | Logical NOT |
| `#27` | `SIN` | Push sin(arg) — argument in radians |
| `#28` | `COS` | Push cos(arg) |
| `#29` | `TAN` | Push tan(arg) |
| `#2A` | `ASN` | Push arcsin(arg) |
| `#2B` | `ACS` | Push arccos(arg) |
| `#2C` | `ATN` | Push arctan(arg) |
| `#2D` | `LN` | Push ln(arg) — natural log |
| `#2E` | `EXP` | Push e^arg |
| `#31` | `SQR` | Push sqrt(arg) |
| `#32` | `SGN` | Push sgn(arg): -1, 0, or +1 |
| `#33` | `ABS` | Push abs(arg) |
| `#34` | `PEEK` | Push byte value at address arg |
| `#35` | `IN` | Push byte read from port arg |
| `#36` | `USR` | Push return value of machine code routine at arg |

For BASIC programmers, this is mostly invisible — you write `2 + 3 * SIN(0.5)` and get the answer. For assembly programmers, the calculator stack is **the bridge between BASIC and machine code**: you can call the same routines (`STACK-NUM` at `#2DE3` to push, `FP-TO-A` at `#2DD9` to pop, etc.) from your own code.

> [!NOTE]
> The calculator's `#36 USR` operation is what makes `LET A = USR 30000` work — it pushes 30000 onto the stack, then `USR` calls the machine code at address 30000, and the routine's return value (in BC register pair) is pushed back. This is the standard BASIC-to-machine-code interface.

---

## The Parser — How Typed Text Becomes a Program

The ROM's parser is unusual compared to other BASIC interpreters: **each line is fully tokenized at entry time**, not at RUN time. This is why pressing ENTER on a line with a syntax error produces the error immediately — the parser has already tried to tokenize the line and rejected it.

### Tokenization Pipeline

```
User types text in editor
        │
        ▼
   ENTER pressed
        │
        ▼
┌────────────────────────┐
│ 1. Syntax check        │  Parser walks the line, checks for
│    (no execution)      │  valid token sequences
└────────────────────────┘
        │ fail
        ▼
   Report error
   (e.g. "Nonsense in BASIC")
        │ pass
        ▼
┌────────────────────────┐
│ 2. Tokenize and store  │  Replace keywords with token bytes,
│                        │  encode numbers inline
└────────────────────────┘
        │
        ▼
   Line is in PROG area
   Ready for next line
```

When `RUN` is executed, the interpreter walks `PROG` line by line and **executes tokens directly** — there is no further parsing step. This makes execution relatively fast for a tokenized BASIC (still slow by machine-code standards, but much faster than a fully interpreted language like a shell script).

The ROM's syntax check is strict about **statement structure** but loose about **expression validity**. For example, `10 LET A = B / 0` is **accepted** at ENTER time (division by zero is a runtime error, not a syntax error), while `10 LET A = B +` produces `Nonsense in BASIC` at ENTER time (`+` needs a right operand).

---

## Graphics Commands — PLOT, DRAW, CIRCLE, POINT, ATTR

The Sinclair BASIC ROM includes five graphics statements that map directly to the Spectrum's pixel-based display: `PLOT` (set one pixel), `DRAW` (line and arc), `CIRCLE` (circle outline), `POINT` (test one pixel), and `ATTR` (read an attribute cell). These are not library calls — they are wired into the ROM's interpreter and execute via the same calculator stack used for arithmetic. They are also the **only high-level graphics commands a 48K BASIC programmer has** — there is no `LINE` statement, no `BOX`, no `PAINT`, no `SPRITE`. Anything more sophisticated requires either assembly language or layered use of these five primitives.

### Coordinate System

Sinclair BASIC uses a **mathematical** coordinate system, not a screen-memory coordinate system:

- **Origin (0, 0)** is at the **bottom-left** of the paper area
- **X increases to the right** — range 0 to 255
- **Y increases upward** — range 0 to 175
- Coordinates outside these ranges produce `B Integer out of range, 0:1`

```
(0,175) ──────────────────────────── (255,175)
   │                                     │
   │      Y increases upward             │
   │      (mathematical convention)      │
   │                                     │
(0, 0) ───────────────────────────── (255, 0)
   ▲
   Origin
```

This is the opposite of the screen memory layout, where address `#4000` is the top-left pixel and addresses increase downward and rightward. The ROM's graphics routines internally translate `(x, y)` to the correct screen address every call.

> [!WARNING]
> The coordinate system is **relative to the paper area**, not the full screen. The border (controlled via `BORDER n`) is outside the coordinate space — you cannot `PLOT` into the border.

### The Current Plot Position (CPP)

All drawing commands maintain a shared **current plot position** (CPP), which is the (x, y) coordinate where the last graphics command left off. `PLOT` updates the CPP, `DRAW` extends from the CPP to a new point and updates the CPP, `CIRCLE` draws around the CPP and leaves it unchanged (or updates it to the last point drawn, depending on ROM version). Commands that reset the CPP to (0, 0): `CLS`, `RUN`, `CLEAR`, `NEW`.

### PLOT — Set One Pixel

```basic
PLOT x, y
PLOT INK color; x, y
PLOT PAPER color; x, y
PLOT INVERSE 1; x, y
PLOT OVER 1; x, y
```

`PLOT` sets a single pixel at coordinate (x, y) and updates the current plot position. The pixel takes its color from the **attribute cell** at that location — you do not specify a color directly with PLOT. To control color, either set the attribute cell first (via `PRINT` with embedded INK/PAPER codes, or `POKE` the attribute byte directly), or use `PLOT INK n; x, y` to set a temporary color for the duration of the PLOT.

| Form | Effect |
|---|---|
| `PLOT x, y` | Set pixel at (x, y), using current attribute state |
| `PLOT INK 2; x, y` | Use red ink for this pixel only (does not change the attribute cell permanently) |
| `PLOT OVER 1; x, y` | Toggle pixel (set if clear, clear if set) — useful for erasing |
| `PLOT INVERSE 1; x, y` | Invert pixel (rarely useful — `OVER 1` is preferred) |
| `PLOT PAPER 6; x, y` | Use yellow paper for this pixel only |

> [!IMPORTANT]
> `PLOT INK n;` sets the color **temporarily** for the single PLOT operation. It does not modify the underlying attribute byte at that screen cell — only the pixel bit. To make the color permanent, you must write directly to the attribute byte (`POKE ATTR_ADDR, attr_byte`) or use PRINT with attribute codes.

### DRAW — Line and Arc

```basic
DRAW x, y                : REM line from CPP to (CPP.x + x, CPP.y + y)
DRAW x, y; a             : REM arc turning through angle a radians
DRAW INK n; x, y
```

`DRAW` has two forms:

1. **Straight line**: `DRAW dx, dy` draws a line from the current plot position to a point offset by (dx, dy). The offsets can be negative.
2. **Arc**: `DRAW dx, dy; angle` draws a curve from the CPP to the offset point, where the curve turns through `angle` radians. `angle = 0` is a straight line; positive angles curve to the left (counterclockwise); negative angles curve to the right.

```basic
10 PLOT 0, 0              : REM start at bottom-left
20 DRAW 255, 175          : REM diagonal line to top-right

10 PLOT 128, 87           : REM center
20 DRAW -50, 0            : REM 50 pixels left
30 DRAW 0, 50             : REM 50 pixels up
40 DRAW 50, 0             : REM 50 pixels right
50 DRAW 0, -50            : REM 50 pixels down (draws a 50x50 square)

10 PLOT 50, 87
20 DRAW 150, 0; PI        : REM semicircle curving upward
```

The angle is in **radians** (like all of Sinclair BASIC's trigonometry). `PI` is a built-in constant equal to approximately 3.14159. An angle of `PI` (180 degrees) draws a semicircle, `PI/2` draws a quarter circle, and `2 * PI` would draw a full circle but produces `B Integer out of range` because the curve math divides by zero at 360 degrees.

> [!NOTE]
> The arc form takes two parameters separated by a comma, then the angle separated by a **semicolon**. This is the only place in Sinclair BASIC where a semicolon separates parameters. A common mistake is `DRAW 100, 0, PI / 2` (comma) — that is a syntax error.

A common idiom for **erasing** a previously drawn line uses `OVER 1` (toggle mode):

```basic
10 PLOT 0, 0
20 DRAW 255, 175          : REM draw visible line
30 PAUSE 50
40 PLOT 0, 0
50 DRAW OVER 1; 255, 175  : REM erase by toggling pixels back
```

### CIRCLE — Circle Outline

```basic
CIRCLE x, y, radius
CIRCLE INK n; x, y, radius
```

`CIRCLE` draws the outline of a circle centered at (x, y) with the specified radius.

```basic
10 CIRCLE 128, 87, 50     : REM circle in the center
20 CIRCLE INK 2; 128, 87, 80   : REM larger red circle
30 CIRCLE 128, 87, 30     : REM smaller circle inside
```

> [!WARNING]
> `CIRCLE` does **not** fill the circle — it draws only the outline. To fill a circle, you must use a loop of `DRAW` statements or `PLOT` individual pixels. BASIC does not have a `PAINT` or `FILL` command. A common workaround is concentric circles of decreasing radius (slow — about 2 seconds for a 50-pixel-radius circle).

### POINT — Test a Pixel

```basic
LET A = POINT(x, y)
```

`POINT` is a **function**, not a statement — it returns 1 if the pixel at (x, y) is set, 0 if it is clear. This is the inverse of `PLOT`: where `PLOT` sets a pixel, `POINT` reads it. `POINT` is used for **collision detection** in BASIC games — typically by testing the pixel at the leading edge of a moving object.

> [!IMPORTANT]
> `POINT` is **slow** — about 200 T-states per call when running interpreted. For real-time games, assembly-language pixel reads (via direct attribute-byte or screen-byte inspection) are preferred.

### ATTR — Read an Attribute Cell

```basic
LET A = ATTR(line, column)
```

`ATTR` is a function that returns the **attribute byte** (color settings) for a specific character cell. The arguments are not pixel coordinates — they are **character cell coordinates**, where line ranges 0–23 and column ranges 0–31, with (0, 0) at the **top-left** of the paper area.

This is the opposite of `POINT`/`PLOT`/`DRAW`/`CIRCLE`, which all use pixel coordinates with origin at the bottom-left. The two coordinate systems coexist because they reflect two different aspects of the screen:

- **Pixel coordinates** (0–255 × 0–175, origin bottom-left): the 256×192 pixel grid
- **Character coordinates** (0–31 × 0–23, origin top-left): the 32×24 attribute grid

The attribute byte encodes ink, paper, bright, and flash:

| Bits | Meaning |
|---|---|
| 0–2 | **Ink** color (0–7) |
| 3–5 | **Paper** color (0–7) |
| 6 | **Bright** (0 = normal, 1 = bright) |
| 7 | **Flash** (0 = steady, 1 = flashing) |

So `ATTR(0, 0)` returns 56 (`#38`) on a freshly-booted Spectrum — paper 7 (white), ink 0 (black), no bright, no flash. To extract the ink color from an attribute byte in BASIC:

```basic
10 LET A = ATTR(10, 5)         : REM read attribute of cell at line 10, col 5
20 LET INK_COLOR = A - INT (A / 8) * 8    : REM ink = A mod 8
30 LET PAPER_COLOR = INT (A / 8) - INT (A / 64) * 8   : REM paper = (A / 8) mod 8
```

> [!NOTE]
> Sinclair BASIC has no bitwise AND operator — `A mod 8` etc. must be computed via `A - INT (A / N) * N`. This is one of the most painful omissions for programmers coming from other BASICs. To do bitwise operations efficiently, you must call machine code via `USR`.

### Performance — How Slow Is BASIC Graphics?

Sinclair BASIC graphics are **slow** by machine-code standards. Approximate timings on a 48K Spectrum:

| Operation | Time | Notes |
|---|---|---|
| `PLOT x, y` | ~3.5 ms (~12,000 T-states) | Includes coordinate translation + pixel write + attribute update |
| `DRAW 100, 0` (horizontal) | ~15 ms (~52,000 T-states) | 100 pixels at ~150 µs/pixel |
| `DRAW 100, 100` (diagonal) | ~20 ms (~70,000 T-states) | Slightly slower due to non-trivial Bresenham |
| `CIRCLE 100, 100, 50` | ~50 ms (~175,000 T-states) | 50 pixels of radius, ~1 ms per degree |
| `POINT(x, y)` | ~3 ms (~10,000 T-states) | Comparable to PLOT |
| `ATTR(line, col)` | ~2 ms (~7,000 T-states) | Just reads the attribute byte |

A frame is 19.97 ms (50.08 Hz) on a 48K. So:

- A single `PLOT` consumes about 17% of a frame
- A `DRAW` across the screen consumes an entire frame
- A `CIRCLE` consumes 2–3 frames

This is why BASIC animation typically uses small moves (10–20 pixels per frame) and why "racing the beam" effects are **impossible in BASIC** — the interpreter simply cannot keep up with the 50 Hz frame rate. For real-time graphics, you need assembly language.

> [!TIP]
> The single biggest speed-up in BASIC graphics is to **reduce the number of statements executed per frame**, not to optimize individual statements. Replacing 10 `PLOT` statements with one `DRAW` (which the ROM implements internally as a tight Z80 loop) is often 3–5× faster than 10 separate BASIC `PLOT` calls, even though both end up calling the same pixel-set routine.

### Worked Example — A Mandelbrot at BASIC Speed

The classic Mandelbrot set, in pure Sinclair BASIC, takes ~2 hours to render a 64×48 grid on a 48K Spectrum:

```basic
10 REM Mandelbrot set (low resolution)
20 FOR PY = 0 TO 175 STEP 4
30   FOR PX = 0 TO 255 STEP 4
40     LET X = 0: LET Y = 0
50     LET CX = (PX - 128) / 64
60     LET CY = (PY - 87) / 64
70     FOR I = 0 TO 32
80       LET XT = X * X - Y * Y + CX
90       LET Y = 2 * X * Y + CY
100      LET X = XT
110      IF X * X + Y * Y > 4 THEN GO TO 150
120     NEXT I
130     PLOT PX, PY
140     GO TO 160
150     REM pixel is in the set — leave clear
160   NEXT PX
170 NEXT PY
```

This produces a recognizable Mandelbrot outline in roughly two hours. The same algorithm in Z80 assembly renders in about 30 seconds — a 240× speedup. This is the canonical illustration of why assembly language is essential for any serious Spectrum graphics work.

---

## Sound — BEEP

The 48K ZX Spectrum has a single sound source: a **1-bit beeper** driven through port `#FE` bit 4. There is no sound chip, no envelope generator, no AY-3-8912 — just a single bit that the CPU flips between 0 and 1 at audio frequencies. The 128K and later models add an AY-3-8912 (or YM2149F), but on the original machine, every sound you hear — from a one-line `BEEP` to the multi-channel music in *Chuckie Egg* — is produced by carefully timed writes to that single bit.

BASIC exposes this primitive through exactly one command:

```basic
BEEP duration, pitch
```

- **`duration`** — length in **seconds** (floating-point, e.g., `0.5` for half a second)
- **`pitch`** — semitones above (positive) or below (negative) **middle C** (integer or floating-point)

`BEEP` blocks execution for the duration of the note — there is no background music in BASIC. The CPU enters a tight loop that toggles the beeper bit at the calculated frequency, and no other code runs until the note completes.

```basic
BEEP 1, 0              : REM 1 second of middle C (~261.63 Hz)
BEEP 0.5, 0            : REM half a second of middle C
BEEP 1, 12             : REM 1 second of C one octave up (~523.25 Hz)
BEEP 1, -12            : REM 1 second of C one octave down (~130.81 Hz)
BEEP 2, 4.5            : REM 2 seconds of a note between E and F (quarter-tone)
```

The `pitch` parameter accepts **non-integer values** — this lets you produce microtonal notes that fall between standard semitones, unique to the Spectrum among home computers of the era.

### Pitch and Frequency

Sinclair BASIC uses **semitones above middle C** as its pitch unit. This is convenient for musicians because each integer step corresponds to one note on a piano keyboard:

| Pitch | Note | Frequency (Hz) |
|---|---|---|
| -12 | C3 (one octave below middle C) | 130.81 |
| 0 | **C4 (middle C)** | **261.63** |
| 4 | E4 | 329.63 |
| 7 | G4 | 392.00 |
| 9 | A4 (concert pitch reference) | 440.00 |
| 12 | C5 (one octave above middle C) | 523.25 |
| 24 | C6 (two octaves up) | 1046.50 |

The frequency is computed as:

```
frequency = 261.63 × 2^(pitch / 12)
```

So for pitch = 0, frequency = 261.63 Hz (middle C). For pitch = 12, frequency = 261.63 × 2 = 523.25 Hz. The `2^(1/12)` ratio between adjacent semitones is called an **equal-tempered** scale — the same tuning used by pianos.

> [!NOTE]
> The exact reference frequency used by the Spectrum ROM is **261.63 Hz** for middle C (pitch = 0), matching concert pitch. However, the **actual output frequency** varies slightly because the beeper is driven by a CPU delay loop, and the loop timing must be an integer number of T-states. The error is typically under 0.5% — imperceptible to most listeners, but measurable with test equipment.

### Tempo

Standard musical tempos map to durations as follows (assuming a quarter-note beat):

| Tempo | Beats per minute | Duration per quarter-note (sec) |
|---|---|---|
| Largo | 60 | 1.0 |
| Andante | 90 | 0.667 |
| Moderato | 110 | 0.545 |
| Allegro | 140 | 0.429 |
| Presto | 180 | 0.333 |

To play a melody at Allegro (140 BPM), use `BEEP 0.429, pitch` for each quarter note.

### Composing Melodies

A melody is a sequence of `(duration, pitch)` pairs. The straightforward approach uses DATA statements:

```basic
10 REM Simple melody — "Twinkle Twinkle Little Star"
20 RESTORE 100
30 FOR N = 1 TO 14
40   READ D, P
50   BEEP D, P
60 NEXT N
100 DATA 0.4, 0,  0.4, 0,  0.4, 7,  0.4, 7
110 DATA 0.4, 9,  0.4, 9,  0.8, 7
120 DATA 0.4, 5,  0.4, 5,  0.4, 4,  0.4, 4
130 DATA 0.4, 2,  0.4, 2,  0.8, 0
```

Each note is two DATA values: duration (in seconds) and pitch (in semitones from middle C). `READ` extracts the pairs one by one, and `BEEP` plays them sequentially. Using a single tempo variable lets you change the speed of an entire piece by editing one line.

### Sound Effects (Non-Musical)

The BEEP command is also useful for non-musical sound effects — clicks, blips, lasers, explosions:

```basic
BEEP 0.02, 0          : REM 20ms click — useful for key-press feedback

10 FOR P = 60 TO 0 STEP -2: BEEP 0.02, P: NEXT P
                       : REM laser / whoosh — descending pitch sweep

10 FOR P = -10 TO -30 STEP -1: BEEP 0.05, P: NEXT P
                       : REM explosion — rumble of low pitches

10 FOR I = 1 TO 20: BEEP 0.05, 12 + 5 * SIN(I): NEXT I
                       : REM warbling tone (power-up effect)

10 FOR I = 1 TO 8: BEEP 0.2, 16: BEEP 0.2, 20: NEXT I
                       : REM phone ringing (UK telephone warble)
```

### Limitations of BASIC Sound

1. **Blocking execution** — `BEEP` blocks the CPU for the entire duration of the note. You cannot play music while doing anything else. The workaround for games is to intersperse very short `BEEP`s (10–30 ms) between game updates.
2. **Single voice** — The beeper can produce only **one frequency at a time**. There is no chord support. To simulate chords, you can rapidly alternate between pitches — but this produces an arpeggio, not a true chord. The 128K's AY-3-8912 chip solves this with three independent channels (see [basic_128k.md](basic_128k.md)).
3. **Volume is fixed** — The beeper is either on or off — there is no volume control. Pulse-width modulation (very short bursts of BEEP with longer gaps) is the only workaround, and that requires cycle-exact assembly code.
4. **Pitch drift at high frequencies** — Above C7 (pitch = 36), the beeper delay loop becomes so short that quantization errors are audible.
5. **Aliased low frequencies** — Below C2 (pitch = -24), the beeper period exceeds the Spectrum's interrupt interval (20 ms), and the ROM's frame-interrupt handler disrupts the timing.

### Worked Example — Ode to Joy

A complete BASIC program that plays the opening of Beethoven's "Ode to Joy":

```basic
10 REM Ode to Joy — Beethoven, arr. for ZX Spectrum
20 LET T = 0.4           : REM quarter-note duration (Allegro)
30 RESTORE 100
40 FOR N = 1 TO 16
50   READ D, P
60   BEEP D * T, P
70 NEXT N
80 STOP
100 REM (duration multiplier, pitch)
110 DATA 1, 4, 1, 4, 1, 5, 1, 6
120 DATA 2, 7, 1, 6, 1, 5, 1, 4
130 DATA 1, 2, 1, 0, 1, 2, 1, 4
140 DATA 2, 0, 1, 0, 1, 4, 1, 4
```

> [!NOTE]
> On a Pentagon clone, the frame rate is 48.83 Hz (not 50.08 Hz), so all `BEEP` durations are about 2.5% longer than on a real Spectrum. An 8-second tune on a 48K becomes about 8.2 seconds on a Pentagon.

For full AY-3-8912 programming from assembly language, see [ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md). For multi-channel beeper music engines (Popov, Follin, etc.), see [beeper_synthesis.md](../../06_sound/synthesis/beeper_synthesis.md).

---

## PEEK, POKE, and USR — Bridging BASIC and Machine Code

Sinclair BASIC is slow — a `FOR/NEXT` loop counting to 1000 takes 10 seconds, where the equivalent Z80 machine code takes under a millisecond. The ROM gives the BASIC programmer **three escape hatches** that bypass the interpreter and let the program touch the hardware directly:

- **`PEEK(address)`** — read one byte from any memory location
- **`POKE address, value`** — write one byte to any memory location
- **`USR address`** — call a machine code subroutine at the given address

These three keywords are the **gateway from BASIC to assembly language**. Every Spectrum programmer who outgrows BASIC eventually learns them; many never write a single line of Z80 assembly but still use `PEEK`/`POKE`/`USR` to drive machine code routines loaded from tape or typed in from magazine listings.

### PEEK — Reading Memory

```basic
LET A = PEEK(address)
```

`PEEK` is a function that returns the **single byte** at the given memory address. The address must be in the range 0–65535 (the Z80's 16-bit address space). The returned value is 0–255.

| Task | Code | Notes |
|---|---|---|
| Read frame counter low byte | `LET F = PEEK 23672` | `FRAMES` is at `#5C78` (23672); this is the low byte of a 3-byte counter |
| Read keyboard state | `LET K = PEEK 23560` | `KSTATE`-derived `LAST_K` at `#5C08` returns last key pressed |
| Read attribute byte | `LET A = PEEK 22592` | Reads attribute at character cell (0, 0) — `ATTR_ADDR = 22528 + line*32 + col` |
| Test RAMTOP | `LET R = PEEK 23730 + 256 * PEEK 23731` | `RAMTOP` system variable at `#5C8A` (big-endian) |
| Read a screen pixel byte | `LET B = PEEK 16384` | Reads byte at top-left of screen memory |

The Z80 is **little-endian**: 16-bit values are stored low byte first, high byte second. To read a 16-bit value, combine two `PEEK`s:

```basic
10 DEF FN P(A) = PEEK A + 256 * PEEK (A + 1)
20 PRINT FN P(23670)   : REM prints the 16-bit value at address 23670
```

> [!NOTE]
> Sinclair BASIC's `DEF FN` allows defining single-line functions. The function is **expanded inline** at every call site — there is no call overhead. This makes `FN P(addr)` just as fast as the explicit `PEEK + 256 * PEEK` form, but far more readable.

The `FRAMES` counter at `#5C78`–`#5C7A` (23672–23674) is a **3-byte counter** incremented by the ROM's interrupt handler every video frame (~50 Hz). It is the standard way to time events in BASIC:

```basic
10 LET START = PEEK 23672 + 256 * (PEEK 23673 + 256 * PEEK 23674)
20 REM ... do something ...
30 LET END = PEEK 23672 + 256 * (PEEK 23673 + 256 * PEEK 23674)
40 LET ELAPSED_FRAMES = END - START
50 LET ELAPSED_SECONDS = ELAPSED_FRAMES / 50
60 PRINT "Elapsed: "; ELAPSED_SECONDS; " sec"
```

### POKE — Writing Memory

```basic
POKE address, value
```

`POKE` writes a single byte (`value`, 0–255) to the given memory address. It is the inverse of `PEEK`. The `address` must be writable RAM — `POKE 0, 42` writes to ROM and is silently ignored on a 48K Spectrum (the ROM is read-only).

| Task | Code | Notes |
|---|---|---|
| Set border color | `POKE 23624, 2` | `BORDCR` at `#5C48` controls border color (low 3 bits) |
| Set attribute cell | `POKE 22592, 56` | Writes attribute at cell (0, 0) — paper 7, ink 0 (white-on-black) |
| Pause-resume `PAUSE` | `POKE 23672, 0` | Reset frame counter, used to break out of `PAUSE` |
| Disable interrupts | `POKE 30000, 243: USR 30000` | (example) — poke `DI` opcode then call it |

The attribute file is at `#5800` (22528) and contains 768 bytes (32 columns × 24 rows). To set the attribute of character cell at line L, column C:

```basic
10 LET L = 10: LET C = 5
20 LET ADDR = 22528 + L * 32 + C
30 POKE ADDR, 33        : REM paper 4 (green), ink 1 (blue), no bright/flash
```

The attribute byte encodes ink (bits 0-2), paper (bits 3-5), bright (bit 6), flash (bit 7). To compute the byte for a given (ink, paper, bright, flash):

```basic
10 LET INK = 1: LET PAPER = 4: LET BRIGHT = 0: LET FLASH = 0
20 LET ATTR_BYTE = INK + 8 * PAPER + 64 * BRIGHT + 128 * FLASH
30 POKE 22528 + 10 * 32 + 5, ATTR_BYTE
```

This is the standard way to do "OUT OF BAND" color changes that are awkward or impossible with `PRINT INK ...; PAPER ...` — for example, changing a single cell's color without disturbing the text.

> [!WARNING]
> Always save your program before experimenting with `POKE` to unfamiliar addresses. A typo like `POKE 23613, 0` instead of `POKE 23612, 0` will instantly crash the machine, and any unsaved program is lost. Dangerous targets include `ERR_SP` (23670), `CH_ADD` (23613), `STACK_PT` (23698), the stack area (`#FF58`-down), and the `PROG` area itself.

### USR — Calling Machine Code

```basic
LET A = USR address
PRINT USR address
USR address                : REM legal but the return value is discarded
```

`USR address` calls a machine code subroutine at the given address. The subroutine runs with full control of the CPU — it can read and write memory, ports, the stack, everything. When the subroutine executes a `RET` instruction, control returns to BASIC, and the **return value is whatever is in the BC register pair** at that moment.

#### The Calling Convention

When `USR addr` is called:

1. The CPU jumps to `addr`
2. The **HL register pair** contains the current value of `STKEND` (a system variable pointing to the calculator stack)
3. The **BC register pair** on return becomes the function's value
4. Interrupts may or may not be enabled — typically they are, but your routine can disable them with `DI` and re-enable with `EI`

The machine code routine must end with `RET` (`#C9`) to return to BASIC. Any other exit (jumping to a ROM routine, infinite loop, crash) leaves BASIC in an undefined state.

#### Simple Example — Clear the Screen Fast

A machine code routine that clears the attribute file, much faster than `CLS`:

```
Address   Bytes          Instruction    Comment
30000     21 00 58       LD HL, #5800   ; point to start of attribute file
30003     36 38          LD (HL), #38   ; attribute byte: paper 7, ink 0
30005     11 01 58       LD DE, #5801   ; destination = source + 1
30008     01 FF 02       LD BC, #02FF   ; count = 767 bytes (one less than full)
30011     ED B0          LDIR           ; block copy of (HL) to (DE), BC bytes
30013     C9             RET            ; return to BASIC
```

To install and call this from BASIC:

```basic
10 REM Poke the routine into memory at 30000
20 FOR A = 0 TO 13
30   READ B
40   POKE 30000 + A, B
50 NEXT A
60 DATA 33, 0, 88, 54, 56, 17, 1, 88, 1, 255, 2, 237, 176, 201
70 REM Now call it
80 CLS
90 LET RESULT = USR 30000
100 PRINT "Screen cleared, return value = "; RESULT
```

Line 90 calls the routine. The return value is whatever BC holds after `RET` — in this case, BC will be 0 (because `LDIR` decrements it to 0), so `RESULT` is 0. The routine is roughly **100× faster** than `CLS` because `LDIR` is implemented as a single Z80 instruction, not a ROM loop.

#### Passing Parameters

There are several conventions for passing parameters from BASIC to a machine code routine:

| Method | Description | When to use |
|---|---|---|
| **POKE before USR** | Patch a data byte inside the routine before calling | Simple "configuration" parameters (color, address, count) |
| **System variables** | POKE to scratch system vars (`#5C80`-`#5C81`), machine code reads via `LD A,(addr)` | Small number of byte/word parameters |
| **Calculator stack** | `PRINT USR addr + 1.5` — pushes values via STKEND | Floating-point parameters (advanced) |
| **Fixed memory region** | POKE parameters to a buffer at an agreed address | Most flexible — used by most commercial BASIC programs |

Example of the fixed-region method:

```basic
10 REM Parameter area at 32000-32009
20 POKE 32000, 100      : REM parameter 1
30 POKE 32001, 200      : REM parameter 2
40 LET RESULT = USR 30000
```

```asm
        LD  HL, #7D00           ; 32000 = #7D00
        LD  A, (HL)             ; parameter 1
        INC HL
        LD  B, (HL)             ; parameter 2
        ...
```

#### Return Value Convention

The return value of `USR addr` is the **16-bit unsigned value in BC** on return. To return a specific value:

```asm
        LD  BC, #1234           ; return value = #1234 = 4660
        RET
```

> [!IMPORTANT]
> The return value is treated as **unsigned**. If you want a signed result, you must interpret values ≥ 32768 as negative in your BASIC code: `LET SIGNED = R - 256 * (R > 32767)`. Most BASIC code uses only small positive return values (0–255 or 0–65535).

A common bug is to write a routine that leaves its result in A or HL, then forget to copy to BC before RET. Always set BC explicitly before `RET` if you care about the return value.

### Loading Machine Code from Tape

Hand-typing opcodes via `POKE` is tedious. The standard way to distribute machine code is as a **code block** on tape (or .tap/.tzx file). The BASIC command to load such a block is:

```basic
LOAD "" CODE            : REM load next code block to its header address
LOAD "GAME" CODE 30000  : REM load named block to address 30000 (overrides header)
```

The block is loaded as raw bytes — no tokenization, no line numbers. A typical loader program looks like:

```basic
10 PRINT "Loading game..."
20 LOAD "" CODE 30000
30 RANDOMIZE USR 30000
```

Line 30 calls it — `RANDOMIZE USR addr` is the standard idiom for "call machine code and discard the return value". (Using just `USR addr` would work but produces a syntax error in some contexts because `USR` is technically a function, not a statement. `RANDOMIZE USR addr` is a statement that uses the function's return value as the new random seed — which we then ignore.)

To save a code block:

```basic
SAVE "GAME" CODE 30000, 4096    : REM save 4096 bytes starting at address 30000
```

> [!NOTE]
> **`RANDOMIZE USR addr` vs `LET X = USR addr`**: Both call the machine code at `addr`. The first discards the return value (uses it as the random seed, which is usually irrelevant). The second saves the return value in variable X. For one-shot calls to game/driver code, `RANDOMIZE USR addr` is the idiom. For utility routines that return meaningful values, `LET X = USR addr` is preferred.

---

## Notable Quirks and Pitfalls

### 1. GO TO vs GOTO

The Spectrum accepts **both** spellings — `GO TO 100` and `GOTO 100` are equivalent. Similarly `GO SUB` and `GOSUB`. The two-word form was used in the ZX81 manual; the one-word form was added for the Spectrum. Both are valid tokens; choose whichever you prefer.

### 2. No ELSE

There is no `ELSE` clause. To express `IF X THEN A ELSE B`, you must write:

```basic
10 IF NOT X THEN GO TO 200
20 REM THEN branch here
200 REM ELSE branch (or continuation)
```

This forces the "early return" style of control flow that BASIC programmers on the Spectrum learn to love or hate.

### 3. No DO/WHILE/UNTIL

Loops are either `FOR/NEXT` (counted) or `IF/GOTO` (conditional). A `WHILE` loop must be written:

```basic
10 REM WHILE condition
20 IF NOT (condition) THEN GO TO 60
30 REM body
40 ...
50 GO TO 10
60 REM end of loop
```

### 4. The LET Keyword Is Mandatory

In most modern BASIC dialects, `A = 5` is shorthand for `LET A = 5`. In Sinclair BASIC, `LET` is **required**:

```basic
10 LET A = 5     : REM correct
10 A = 5         : REM syntax error
```

### 5. Variable Name Length Limits

The 48K ROM accepts only the first **two characters** of a variable name, and the second character must be a digit (`0`–`9`). So `TOTAL`, `TIME`, `TEMPERATURE` all refer to the same variable `T`. The 128K ROM accepts longer names but stores them with a length prefix in the variables area.

### 6. The Single-Line Editor

You cannot move the cursor to any line on the screen and start typing — the editor is **per-line**. To edit line 100, you must:

1. Press `EDIT` (Caps Shift + 1) with the cursor on a line number, OR
2. Type `LIST 100` then move the cursor to that line and press ENTER to bring it into the edit buffer

The 128K ROM introduced a full-screen editor accessible from the menu, which is one of the major improvements of the later machines.

### 7. The Contended Memory Effect on BASIC

If your program writes to the screen during the paper area of the video frame, the ULA steals CPU cycles — and the BASIC interpreter slows down proportionally. `PRINT` statements during the bottom border are noticeably faster than during the visible screen. This is rarely a practical concern for BASIC programs (the speed difference is small compared to the interpreter's inherent slowness), but it explains why some BASIC programs feel slightly sluggish in the middle of the screen. See [contention_timing.md](../05_display_and_timing/contention_timing.md) for the underlying hardware mechanism.

### 8. IF Trap: `THEN 100` vs `THEN GO TO 100`

`10 IF X THEN 100` is **not** the same as `10 IF X THEN GO TO 100` — both work, but `THEN 100` is interpreted as `THEN GO TO 100` only because the parser allows a bare line number after THEN. However, `10 IF X THEN PRINT` (with no argument to PRINT) will produce `Nonsense in BASIC` because PRINT without an argument is not legal. Always type the full keyword.

### 9. POINT and ATTR Are Functions, Not Statements

```basic
10 POINT(100, 100)         : REM syntax error — POINT is a function
20 LET A = POINT(100, 100) : REM correct
```

`POINT` and `ATTR` return values and must appear in an expression. They cannot be used as standalone statements like `PLOT` and `DRAW`.

### 10. DRAW Arc Form Uses Semicolon, Not Comma

```basic
10 DRAW 100, 0; PI / 2     : REM correct — semicolon before arc angle
20 DRAW 100, 0, PI / 2     : REM syntax error — comma is wrong
```

---

## When to Use BASIC vs Machine Code

| Use case | Use BASIC | Use USR + machine code |
|---|---|---|
| Read/write a single byte | `PEEK`/`POKE` is fine | — |
| Read/write a 16-bit value | Two `PEEK`s/`POKE`s | — |
| Fast block fill | — | `LDIR` via `USR` |
| Pixel-level graphics | — | Direct screen writes via `USR` |
| Sound effects | — | Beeper engine via `USR` |
| Game sprite rendering | — | `USR` routine |
| Timing-sensitive code | — | Cycle-exact assembly via `USR` |
| Math (sin, cos) | Use `SIN`, `COS` | — (ROM calculator is fine) |
| String manipulation | Use `LET A$ = ...` | — (rarely worth it) |
| Simple conditionals | Use `IF`/`THEN` | — |

The general rule: if a task takes fewer than ~50 lines of BASIC, write it in BASIC. If it takes more, or if it needs to run faster than 50 Hz, write it in Z80 assembly and call it via `USR`.

---

## Cross-References

- [Sinclair BASIC 128K extensions](basic_128k.md) — extended editor, `PLAY`/`SOUND`/`MUSIC`, AY-3-8912 from BASIC, `BANK`, +2A/+3 DOS commands
- [Basic token table](../../10_references/basic_token_table.md) — the complete byte values for every keyword, function, and control code
- [Memory maps](../../10_references/memory_maps.md) — full system variable table and RAM map
- [ROM routines](../../10_references/rom_routines.md) — callable 48K ROM routines for assembly programmers
- [Error codes](../../10_references/error_codes.md) — full catalog of ROM error messages
- [Beeper synthesis](../../06_sound/synthesis/beeper_synthesis.md) — 1-bit beeper hardware, PWM engines, multi-channel beeper music (Popov, Follin, etc.)
- [AY-3-8912 PSG](../../06_sound/hardware/ay_3_8912.md) — 128K and later sound chip
- [Color system](../05_display_and_timing/color_system.md) — the 8-color attribute system, ink/paper/bright/flash
- [Video frame overview](../05_display_and_timing/video_frame_overview.md) — pixel grid, attribute grid, contended memory
- [Screen layout](../03_memory_and_io/screen_layout.md) — pixel address calculation and the ROM's `X-Y to screen address` formula
- [Screen access](../06_graphics/screen_access.md) (planned) — direct pixel and attribute writes in Z80
- [Contention timing](../05_display_and_timing/contention_timing.md) — why PRINT sometimes feels slow
- [Assembly intro](../02_assembly/assembly_intro.md) (planned) — learning Z80 assembly

---

## References

- [The Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip) — the definitive source for every routine in the 48K ROM, including the parser, tokenizer, calculator, `BEEP` at `#03F8`, and the `USR` handling code at calculator operation byte `#36`
- **Sinclair ZX Spectrum Basic Programming** (Steven Vickers, 1982) — the official manual by the ROM's co-author; chapters 1–9 cover the language, chapters 14–17 cover PLOT/DRAW/CIRCLE/POINT/ATTR, chapter 16 covers `BEEP`, chapter 26 covers `PEEK`/`POKE`/`USR`
- **The ZX Spectrum ROM** — disassembly on Wearmouth.org: https://www.wearmouth.demon.co.uk/zxsp2.htm
- [World of Spectrum — ZX BASIC Manual](https://worldofspectrum.org/) : https://worldofspectrum.org/ZXBasicManual/
- [Alessandro Grussu's Spectrumpedia](https://speccy.wiki/) — comprehensive encyclopedia of all ZX models and their BASIC dialects
- [Sinclair User Issue 29 — Helpline](https://archive.org/details/sinclair-user-magazine) : https://sinclairuser.com/029/helplne.htm — semitone-to-frequency conversion table used by the ROM
- **Soft Spectrum 48 — Timing and the Beeper**: https://softspectrum48.weebly.com/notes/timing-and-the-beeper — timing analysis of the BEEP routine
- **Your Spectrum Issue 03 — Extending BASIC**: http://www.users.globalnet.co.uk/~jg27paw4/yr03/yr03_43.htm — conventions for `USR` return values and parameter passing
