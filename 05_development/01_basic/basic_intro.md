[← Home](../../README.md) · [BASIC](README.md)

# Sinclair BASIC — Syntax, Tokens, Variables, and the ROM Interpreter

The ZX Spectrum boots straight into BASIC. There is no operating system, no shell, no `COMMAND.COM` — the moment the ROM finishes its power-on self-test, the user is staring at a `(C) 1982 Sinclair Research Ltd` banner and a flashing K cursor, ready to type a BASIC line. On a 16K machine with nothing loaded, BASIC is the entire user-facing environment; on a 128K it sits behind a menu, but it is still there, still in ROM, still interpreting every keystroke.

Sinclair BASIC is **not a fast language**. A simple `FOR/NEXT` loop counting to 1000 takes roughly 10 seconds — about a hundredth the speed of the same loop in compiled Z80 machine code. What it is, however, is **the universal entry point** to the machine: every Spectrum programmer starts here, every demo and game ultimately boots through some ROM interaction, and every article on assembly development on this site assumes the reader has internalized BASIC's quirks. This article covers those quirks — the token system, the variable model, the memory layout, the floating-point format, and the parser that turns typed text into runnable code.

> [!NOTE]
> This article covers **the language as the ROM implements it**. For the byte-level token table (every keyword's numeric code), see [basic_token_table.md](../../10_references/basic_token_table.md). For graphics commands (`PLOT`, `DRAW`, `CIRCLE`), see [basic_graphics.md](basic_graphics.md). For sound (`BEEP`), see [basic_sound.md](basic_sound.md). For mixing BASIC with machine code (`PEEK`, `POKE`, `USR`), see [basic_peek_poke.md](basic_peek_poke.md).

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

The 128K ROM's different token table is a frequent source of confusion. Loading a 48K program saved with `SAVE "X" LINE 0` into a 128K Spectrum running in 128K mode will work — the 128K ROM detects the old token set and re-tokenizes. But inspecting the bytes in memory will show **different byte values** for the same keywords.

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

For machine-code programmers, these are the variables you read or write to integrate with the BASIC environment. For BASIC programmers, they mostly matter when you start using `PEEK` and `POKE` — see [basic_peek_poke.md](basic_peek_poke.md).

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
20 LET NAME$ = "WORLD"     ! Wait — this is actually invalid
```

Actually that second line fails — `NAME$` is interpreted as variable `N$` (with trailing `AME` ignored on 48K), and the only legal string names are `A$`–`Z$`. So `LET N$ = "WORLD"` works:

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

Array storage format:

- **Numeric array**: 1 byte type marker (`#85`), name letter, then dimensions (2 bytes each, big-endian), then values (5 bytes each, in row-major order)
- **String array**: 1 byte type marker (`#C0` + name letter offset), name, dimensions, then for each element a length-prefixed string

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

This is the **inline integer form** — it is 3 bytes instead of the 6 bytes (`#0E` + 5-byte float) that the full floating-point form would take. The ROM's expression evaluator knows how to read either form. See [basic_token_table.md](../../10_references/basic_token_table.md) for the full details on `#0E` and `#0F`.

---

## The Expression Evaluator (Calculator Stack)

When the BASIC interpreter encounters an expression like `2 + 3 * SIN(0.5)`, it does **not** generate a parse tree and walk it. Instead, it uses a **stack-based calculator** — the same kind of architecture as a Hewlett-Packard HP-15C or a Java VM. The ROM has a "calculator" routine at address `#30CB` (`STACK-COMMON`) that takes a single byte operand specifying the operation, performs it on the top one or two values of the calculator stack, and pushes the result.

The calculator stack lives just below the main program work area, growing downward from `STKEND` (system variable `#5C59`). Each stack slot is 5 bytes — one floating-point value.

### Operations

The ROM calculator has 44 built-in operations, each identified by a single byte:

| Byte | Operation | Effect |
|---|---|---|
| `#00` | `JFALSE` | Jump if top of stack is zero (control flow) |
| `#02` | `JTRUE` | Jump if top of stack is non-zero |
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
| `#38` | `STR$` | Push string representation of arg |
| `#3A` | `CHRS` | Push single-character string with ASCII arg |

For BASIC programmers, this is mostly invisible — you write `2 + 3 * SIN(0.5)` and get the answer. For assembly programmers, the calculator stack is **the bridge between BASIC and machine code**: you can call the same routines (`STACK-NUM` at `#2DE3` to push, `FP-TO-A` at `#2DD9` to pop, etc.) from your own code. See [basic_peek_poke.md](basic_peek_poke.md) for the routine-level interface.

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

### Syntax Checking Quirks

The ROM's syntax check is strict about **statement structure** but loose about **expression validity**. For example:

- `10 LET A = ` followed by nothing produces `Nonsense in BASIC` at ENTER time (missing expression)
- `10 LET A = B +` produces the same error (`+` needs a right operand)
- `10 LET A = B / 0` is **accepted** at ENTER time (division by zero is a runtime error, not a syntax error)
- `10 PRINT "missing quote` is **accepted** at ENTER time (the parser is lenient about unterminated strings — it implicitly closes them)

The runtime-vs-syntax distinction matters because syntax errors are reported immediately at line entry, while runtime errors are reported when the offending line is executed. `10 LET A = 1/0` will type fine but produce `6 Number too big, 0:1` at RUN time.

---

## Notable Quirks and Pitfalls

### 1. GO TO vs GOTO

The Spectrum accepts **both** spellings — `GO TO 100` and `GOTO 100` are equivalent. Similarly `GO SUB` and `GOSUB`. The two-word form was used in the ZX81 manual; the one-word form was added for the Spectrum. Both are valid tokens; choose whichever you prefer.

### 2. No ELSE

There is no `ELSE` clause. To express `IF X THEN A ELSE B`, you must write:

```basic
10 IF X THEN GO TO 100
20 REM This is the ELSE branch
30 GO TO 200
100 REM This is the THEN branch
200 REM Continue
```

Or, more idiomatically:

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

### 4. IF Takes a Line Number or Statement

`IF` can be followed by either a `GO TO` (or `GOTO`) directly, or any other statement. If `IF X THEN PRINT "YES"` is the line, the PRINT only executes if X is non-zero. If you want multiple statements under IF, you must use GOTO:

```basic
10 IF X THEN GO TO 100
20 PRINT "X is zero"     : REM only runs if X = 0
30 ...
100 PRINT "X is non-zero"
110 LET Y = Y + 1
120 ...
```

### 5. The IF Trap: Empty Branches

`10 IF X THEN 100` is **not** the same as `10 IF X THEN GO TO 100` — both work, but `THEN 100` is interpreted as `THEN GO TO 100` only because the parser allows a bare line number after THEN. However, `10 IF X THEN PRINT` (with no argument to PRINT) will produce `Nonsense in BASIC` because PRINT without an argument is not legal. Always type the full keyword.

### 6. The LET Keyword Is Mandatory

In most modern BASIC dialects, `A = 5` is shorthand for `LET A = 5`. In Sinclair BASIC, `LET` is **required**:

```basic
10 LET A = 5     : REM correct
10 A = 5         : REM syntax error
```

### 7. The Contended Memory Effect on BASIC

If your program writes to the screen during the paper area of the video frame, the ULA steals CPU cycles — and the BASIC interpreter slows down proportionally. `PRINT` statements during the bottom border are noticeably faster than during the visible screen. This is rarely a practical concern for BASIC programs (the speed difference is small compared to the interpreter's inherent slowness), but it explains why some BASIC programs feel slightly sluggish in the middle of the screen.

See [contention_timing.md](../05_display_and_timing/contention_timing.md) for the underlying hardware mechanism.

### 8. Variable Name Length Limits

The 48K ROM accepts only the first **two characters** of a variable name, and the second character must be a digit (`0`–`9`). So `TOTAL`, `TIME`, `TEMPERATURE` all refer to the same variable `T`. The 128K ROM accepts longer names but stores them with a length prefix in the variables area.

### 9. The Single-Line Editor

You cannot move the cursor to any line on the screen and start typing — the editor is **per-line**. To edit line 100, you must:

1. Press `EDIT` (Caps Shift + 1) with the cursor on a line number, OR
2. Type `LIST 100` then move the cursor to that line and press ENTER to bring it into the edit buffer

The 128K ROM introduced a full-screen editor accessible from the menu, which is one of the major improvements of the later machines.

---

## Running Your First Program

A complete worked example — the canonical "guess the number" game in Sinclair BASIC:

```basic
10 REM Guess the number
20 LET TARGET = INT (RND * 100) + 1
30 LET TRIES = 0
40 INPUT "Your guess? "; G
50 LET TRIES = TRIES + 1
60 IF G = TARGET THEN GO TO 100
70 IF G < TARGET THEN PRINT "Too low"
80 IF G > TARGET THEN PRINT "Too high"
90 GO TO 40
100 PRINT "You got it in "; TRIES; " tries"
```

Key things this example demonstrates:

- **`REM`** is the comment keyword — anything after it on the line is ignored
- **`INT (RND * 100) + 1`** generates a random integer from 1 to 100 (RND returns 0 ≤ RND < 1, multiply by 100 to get 0 ≤ x < 100, INT truncates to integer, +1 shifts to 1–101)
- **`INPUT`** reads from the keyboard — the prompt string is optional, and `;` after the prompt means "insert a ? after the prompt"
- **`IF ... THEN GO TO`** is the conditional branch — note the lack of ELSE
- **`PRINT`** with `;` between expressions means "concatenate without space" (use `,` for tab-separated output)

> [!TIP]
> The above program is around 250 bytes of tokenized BASIC and runs the entire game in roughly 50 lines of interaction. The same game in Z80 machine code would be about 80 bytes of code but require several hundred lines of source. BASIC's trade-off is clear: it is verbose in source but compact in storage, and slow at runtime but fast to develop.

---

## Cross-References

- [Basic token table](../../10_references/basic_token_table.md) — the complete byte values for every keyword, function, and control code
- [Basic graphics](basic_graphics.md) — `PLOT`, `DRAW`, `CIRCLE`, `POINT`, `ATTR` and the screen coordinate system
- [Basic sound](basic_sound.md) — `BEEP`, the beeper, frequency/duration parameters
- [Basic file I/O](basic_file_io.md) (pending) — `SAVE`, `LOAD`, `VERIFY`, `MERGE`, tape operations
- [Basic PEEK/POKE/USR](basic_peek_poke.md) — mixing BASIC with machine code
- [Memory maps](../../10_references/memory_maps.md) — full system variable table and RAM map
- [ROM routines](../../10_references/rom_routines.md) — callable 48K ROM routines for assembly programmers
- [Floating-point calculator](../02_assembly/float_calc.md) (planned) — using the ROM calculator stack from Z80
- [Contention timing](../05_display_and_timing/contention_timing.md) — why PRINT sometimes feels slow

---

## References

- **The Complete Spectrum ROM Disassembly** (Dr. Ian Logan & Dr. Frank O'Hara, 1983) — the definitive source for every routine in the 48K ROM, including the parser, tokenizer, and calculator
- **Sinclair ZX Spectrum Basic Programming** (Steven Vickers, 1982) — the official manual by the ROM's co-author; chapters 1–9 cover the language, chapters 10–25 cover graphics, sound, and the system
- **The ZX Spectrum ROM** — disassembly on Wearmouth.org: https://www.wearmouth.demon.co.uk/zxsp2.htm
- **World of Spectrum — ZX BASIC Manual** (chapters online): https://worldofspectrum.org/ZXBasicManual/
- **Alessandro Grussu's Spectrumpedia** — comprehensive encyclopedia of all ZX models and their BASIC dialects
