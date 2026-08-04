[← Home](../README.md) · [Operating Systems](README.md)

# Sinclair BASIC — Dialects and Variants

On most home computers of the 1980s, BASIC was a programming language. On the ZX Spectrum, BASIC was **the operating system**. When you switched the machine on, you got a BASIC prompt. To load software, you typed BASIC keywords. To manipulate files, you typed BASIC commands. The ROM that contained the BASIC interpreter also contained the keyboard handler, the display driver, the cassette tape routines, the floating-point library, the character set, and every other piece of "system software" the Spectrum had.

The Spectrum shipped with one BASIC dialect — **Sinclair BASIC** — but over the next 40 years that dialect proliferated into a family of related but distinct BASICs. Each new Spectrum model added keywords or modified behavior. Soviet clones added their own extensions. The modern community has produced SE BASIC, OpenSE, NextBASIC, and several other rewrites. This article covers the family of BASIC dialects that have run on Spectrum-compatible hardware, from the original 48K ROM of 1982 to the modern NextBASIC of the 2020s.

For the underlying ROMs themselves — version numbers, bug lists, contents — see [rom_48k.md](rom_48k.md), [rom_128k.md](rom_128k.md), and [rom_plus2.md](rom_plus2.md). For TR-DOS's BASIC extensions, see [trdos.md](trdos.md). For NextBASIC's hardware-acceleration extensions, see [nextzxos.md](nextzxos.md).

---

## Roadmap

1. **What Sinclair BASIC is** — history, why BASIC is the Spectrum's "OS"
2. **The 48K BASIC ROM (1982)** — the canonical Sinclair BASIC
3. **The 128K BASIC (1986)** — editor, RAM disk, the second Sinclair ROM
4. **+3 BASIC (1987)** — Amstrad's DOS-aware extensions
5. **TR-DOS BASIC extensions** — the Soviet additions
6. **Sinclair QL SuperBASIC** — a brief mention of the related Sinclair dialect
7. **SE BASIC and OpenSE** — modern open replacement ROMs
8. **NextBASIC** — the ZX Spectrum Next's modern BASIC
9. **Comparison of dialects** — the full feature matrix
10. **Cross-references** — where to go next

---

## §1. What Sinclair BASIC Is

### 1.1 Origins: the ZX80 and ZX81 lineage

The Spectrum's BASIC did not appear from nowhere. It was the third iteration of a design that started at Sinclair Radionics in 1979 with the **ZX80**, continued with the **ZX81** in 1981, and matured with the **ZX Spectrum** in 1982.

The original ZX80 BASIC — written by John Grant of Nine Tiles Ltd. — was a 4 KB ROM that supported only integer arithmetic, had no PEEK/POKE, and could not even support floating-point numbers. The ZX81 upgraded this to 8 KB, added floating point (single-precision), and introduced the **single-keyword entry** system: pressing one key in the appropriate mode would type an entire BASIC keyword (`P` for PRINT, `G` for GOSUB, etc.).

The Spectrum's 48K BASIC, also by Nine Tiles, took the ZX81 design and expanded it dramatically:

- 16 KB ROM (double the ZX81's).
- Full floating-point arithmetic with the standard four trigonometric functions, LOG/EXP, SQR, and **PI** as a built-in constant.
- **Colour, ATTR, POINT, SCREEN$** — graphics and attribute manipulation functions.
- **BEEP** for sound, **POKE/PEEK** for memory access, **RANDOMIZE** for the random number seed.
- The famous (or infamous) **single-keyword entry** system retained and expanded.

The Spectrum's BASIC was, by 1982 standards, both powerful and quirky. It lacked `ELSE` on IF, lacked `DO/WHILE/UNTIL` loops, required line numbers for every statement, and used a non-standard notation for arguments. But it also gave a 1982 home user more graphics and sound capability from BASIC than almost any other machine at the price point.

### 1.2 Why BASIC is the Spectrum's operating system

The 48K Spectrum's ROM occupies the bottom 16 KB of address space (`#0000`–`#3FFF`). When you power on the machine, the Z80 starts executing at address `#0000` — inside the ROM. The ROM performs basic hardware checks, displays the (c) 1982 Sinclair Research Ltd message, and drops into BASIC.

From this point, every interaction the user has with the machine goes through BASIC:

- **Typing characters**: handled by the ROM's keyboard routine, which is called from the BASIC editor.
- **Loading from tape**: triggered by typing `LOAD ""`, parsed by the BASIC command interpreter.
- **Saving to tape**: `SAVE "name"`, same path.
- **Running programs in machine code**: `RANDOMIZE USR address` or `POKE` directly into the UDG buffer and call.
- **Displaying text or graphics**: `PRINT`, `PLOT`, `DRAW` — all built into the ROM.
- **Handling errors**: the ROM's error handler prints an error message and returns to the editor.

There is no separate OS kernel. There is no command shell. There is no file manager. The Spectrum is BASIC. This is a design that today seems hopelessly primitive — but in 1982, when the alternative was CP/M costing more than the computer itself, it was an extraordinary achievement.

Even on the 128K and +2/+3 models, which added a separate "128K editor" ROM and disk commands, the BASIC interpreter remained the user-facing interface. You booted the machine, you got BASIC. You typed BASIC. The disk loaded or saved. BASIC was the shell.

### 1.3 What is "Sinclair BASIC", formally?

The term **Sinclair BASIC** is loosely defined. For this article, it refers to:

- The BASIC dialect implemented by the **Sinclair-produced Spectrum ROMs** (16K/48K ROM, 128K ROM, +2/+2A/+3 ROMs).
- The dialect's **direct descendants** in licensed/authorised derivatives (Spanish 128K, Sinclair-branded ROMs for non-UK markets).
- The dialect's **unofficial extensions** added by add-on interfaces (ZX Microdrive, Opus Discovery, Beta 128, +D, DivIDE, etc.).
- The dialect's **clone-machine reimplementations** (Pentagon, Scorpion, ATM Turbo — mostly identical, sometimes with extras).
- The dialect's **modern open reimplementations** (SE BASIC, OpenSE, NextBASIC).

The defining features of all Sinclair BASIC variants:

- **Single-keyword entry** — pressing a key in the right mode types an entire keyword.
- **Line numbers** — every program line has a line number; lines are stored in ascending order.
- **Tokenised source** — keywords are stored as single bytes (tokens), not as ASCII text.
- **Two's-complement integers + 5-byte floats** — numbers are either 16-bit signed ints or 40-bit floats, distinguished by a flag bit.
- **No ELSE** — the IF statement has only a THEN clause; an IF that fails falls through to the next line.
- **Variable names** are case-sensitive and can be any length, but only the first letter matters for simple numeric variables (`A` and `A1` and `AB` all refer to the same variable). String variables end in `$`; for loops use integer-or-float variables.

These characteristics persist across all versions. Even NextBASIC — written from scratch in 2017 — preserves most of them.

### 1.4 The dialects this article covers

| Dialect | Year | Vendor / Author | ROM size | Notes |
|---|---|---|---|---|
| 48K BASIC | 1982 | Nine Tiles / Sinclair | 16 KB | The original |
| 128K BASIC | 1986 | Sinclair / Investrónica | 32 KB | Adds editor, RAM disk, music |
| +2/+2A/+3 BASIC | 1987 | Amstrad / LocoScript | 64 KB | Adds DOS keywords |
| Spanish 128K BASIC | 1985 | Investrónica | 32 KB | Adds Ñ-key and keyboard layout |
| TR-DOS BASIC exts | 1985+ | Various (Soviet) | (overlay) | Adds disk commands |
| SE BASIC | 2002+ | Andrew Owen | 16 KB | Modern open replacement |
| OpenSE BASIC | 2010+ | Andrew Owen et al. | 16 KB | Continued SE BASIC |
| NextBASIC | 2017+ | Garry Lancaster | (part of NextZXOS) | Modern BASIC with hardware acceleration |
| TMX BASIC | 1983 | Timex Portugal | 24 KB | For the TS2068; few changes |

This article walks through each one, focusing on what is distinctive about it.

---

## §2. The 48K BASIC ROM (1982)

The original 16 KB ROM, fitted to every ZX Spectrum 16K and 48K from April 1982 onward, defines the canonical **Sinclair BASIC**. Every later version preserves its design and adds to it.

### 2.1 The keyword set

The 48K ROM contains 88 BASIC keywords. They are entered by pressing a single key (in the appropriate keyword mode), and stored in memory as single bytes (`#A5`–`#FF`). The full list, grouped by function:

**Program structure:**
```
REM, FOR, TO, STEP, NEXT, GOTO, GOSUB, RETURN, IF, THEN,
STOP, CONTINUE, END (rarely used), DEF, FN, DIM
```

**I/O:**
```
PRINT, INPUT, LPRINT, LLIST, COPY, INVERSE, OVER, INK, PAPER,
FLASH, BRIGHT, BORDER, BEEP, CLS, PLOT, DRAW, CIRCLE, ATTR,
POINT, SCREEN$, TAB, AT
```

**File / tape:**
```
LOAD, SAVE, VERIFY, MERGE, CAT, FORMAT, MOVE, ERASE, NEW
```
(Note: `CAT`, `FORMAT`, `MOVE`, `ERASE` are defined as keywords in the 48K ROM but only do anything useful if a disk interface is attached. On a stock 48K Spectrum, they generate an error.)

**Data:**
```
DATA, READ, RESTORE, POKE, PEEK, RANDOMIZE
```

**Math:**
```
LET, +, -, *, /, ^, ABS, ACS, ASN, ATN, COS, EXP, LN, SIN, SQR, TAN, INT, PI, SGN, CODE, VAL, LEN, USR, BIN
```

**Strings:**
```
$, STR$, CHR$, TL$, (string concatenation is "+")
```

**Memory:**
```
PEEK, POKE, IN, OUT, USR (numeric: call machine code)
```

The single-keyword entry system means the user does not type `P-R-I-N-T` — they press the `P` key in keyword mode. This is efficient once learned but famously confusing to beginners.

### 2.2 Numbers: 16-bit integers and 5-byte floats

Sinclair BASIC stores numbers in two formats:

- **16-bit signed integers**: stored as 2 bytes plus a marker byte (`#00` at offset 0). Used for small whole numbers and addresses.
- **5-byte floats**: a 40-bit floating-point format (8-bit exponent + 32-bit mantissa). Used for everything else.

Internally, the ROM uses floats for almost everything. Integer arithmetic in BASIC is essentially not supported — `2 + 2` goes through the float library, not the integer ALU. This makes integer arithmetic much slower than necessary, and is one of the reasons why Spectrum BASIC programs that do a lot of counting (e.g., loop counters) run noticeably faster in machine code than in BASIC.

A numeric variable is stored as 5 bytes plus a 1-byte name character. The variable `A` lives at a specific memory location and takes 6 bytes total. A numeric array `DIM A(100)` takes 5 bytes per element plus a header.

### 2.3 The IF statement (and why no ELSE?)

The 48K IF statement is famously minimal:

```basic
10 INPUT a
20 IF a = 1 THEN PRINT "one"
30 PRINT "done"
```

There is no `ELSE`. The `THEN` keyword is followed by a single statement (which can be a colon-separated list of statements, which is a Sinclair-specific extension). If the condition is false, control falls through to the next line.

The classic workaround for missing ELSE is the IF-with-GOTO:

```basic
10 INPUT a
20 IF a = 1 THEN GO TO 100
30 PRINT "not one"
40 STOP
100 PRINT "one"
```

This is verbose and the source of many bugs. Later BASICs (and most modern dialects, including NextBASIC) added ELSE.

### 2.4 Variables and arrays

The 48K ROM supports the following variable types:

- **Numeric variables**: `A`, `B2`, `MYVAR` — all the same type (5-byte float). Only the first letter matters; `A`, `A1`, `AB` all refer to the same variable.
- **String variables**: `A$`, `B$` — variable-length strings, max 65535 chars.
- **Numeric arrays**: `DIM A(100)` — a one- or multi-dimensional array of floats.
- **String arrays**: `DIM A$(100, 10)` — a 2D "array" of fixed-length strings.
- **FOR loops**: use a numeric variable as the loop counter.

The "only the first letter matters" rule for numeric variables is unique to Sinclair BASIC and a frequent source of confusion. `MYAGE` and `MYNAME` are the same variable (`M`). String variables are distinguished by the `$` suffix, so `MYNAME$` and `MYAGE$` are different.

### 2.5 Functions and DEF FN

The 48K ROM supports user-defined functions:

```basic
10 DEF FN f(x) = x * x + 1
20 PRINT FN f(5)
```

This computes 26. The function is single-line only (no multi-line functions in 48K BASIC). Parameters are passed by value. The function body is an expression, not a sequence of statements.

This is one of the most forward-looking features of Sinclair BASIC — most home computer BASICs of the era did not have user-defined functions at all.

### 2.6 The lack of WHILE / DO / UNTIL

Sinclair BASIC has no structured-loop constructs beyond FOR. A "while" loop is implemented as:

```basic
10 LET done = 0
20 IF done = 1 THEN GO TO 60
30 ... do something ...
40 IF some_condition THEN LET done = 1
50 GO TO 20
60 REM end of loop
```

This is the same pattern every BASIC of the era used. Modern structured BASICs (QBASIC, Visual Basic, BBC BASIC) have proper WHILE/DO/UNTIL; Sinclair BASIC does not. NextBASIC (2017) finally adds them.

### 2.7 Quirks and bugs

The 48K ROM has several well-documented bugs and quirks:

- **The (c) 1982 message delay**: if you press a key during the copyright message at boot, the message is held for an extra 0.5 seconds per keypress. This is a deliberate "don't make the user think the machine has crashed" feature.
- **The INT(-1) bug**: `INT(-0.5)` correctly returns `-1`, but `INT(-1)` returns `-1` rather than the mathematically-expected `-1`. Actually, this is correct; the famous bug is `INT(x)` returning a wrong value for very large floats near the integer limit.
- **The SAVE bug**: if you type `SAVE "name" LINE 0`, the saved program auto-runs from line 0 — but line 0 doesn't exist (Sinclair BASIC conventionally starts at line 10). The behavior is that the program runs from the lowest line number, which works fine.
- **The famous "stack bug"**: a deeply recursive GOSUB chain can corrupt the calculator stack. The fix (in 128K and later) was to grow the stack downward into the GO SUB stack area.
- **Floating-point inaccuracy**: `(0.1 + 0.2) - 0.3` does not return exactly 0.0 because of binary floating-point representation. Same bug as every IEEE float system in history.

These bugs are extensively documented; see [rom_48k.md](rom_48k.md) for the full catalog.

---
## §3. The 128K BASIC (1986)

The Spectrum 128K — code-named "Blair" during development and released in September 1986 — was Sinclair's last machine before selling to Amstrad. It shipped with a substantially expanded BASIC.

### 3.1 The 32 KB ROM

The 128K ROM is 32 KB, divided into two 16 KB banks. Bank 0 contains a modified version of the 48K BASIC ROM, mostly for backward compatibility. Bank 1 contains:

- A **new full-screen editor** that replaces the old single-line editor.
- **128K-specific BASIC extensions**: PLAY, SPECTRUM, EDIT.
- A **RAM disk driver** (drives M: and N:).
- The **128K music chip** (AY-3-8910) driver.
- An **RS232 driver** for the new serial port.
- A **Keypad / Keystation** mode for the new keypad connector.

The two banks are switched into the `#0000`–`#3FFF` address range as needed. The user sees a single unified BASIC environment; the bank switching is invisible.

### 3.2 The new editor

The biggest user-facing change in 128K BASIC is the **full-screen editor**. Instead of typing one line at a time at the bottom of the screen and pressing ENTER, the user can move a cursor anywhere in the program listing and edit any line in place.

The new editor is invoked by pressing `EDIT` (Caps Shift + 1) on a line, or `ENTER` on the listing. The screen shows the program with the cursor active in the listing; the user can use arrow keys to move around, type to insert, delete, etc. Pressing ENTER commits the edit and returns to the main prompt.

This is a substantial usability improvement over the 48K's "type a whole new line to replace the old one" model. Most users prefer it, though some (especially those who grew up with the 48K) miss the speed of the old single-line editor.

### 3.3 PLAY, SPECTRUM, EDIT

The 128K adds three new keywords:

**PLAY** — plays music on the AY-3-8910 chip. The syntax is:

```basic
10 PLAY "cdefgabC"
```

The string contains note letters (`c`, `d`, `e`, `f`, `g`, `a`, `b`, `C` for upper octave), with optional octave and timing modifiers. Multiple channels are supported via semicolons:

```basic
10 PLAY "cdefgabC", "cegcegC"
```

This plays two channels simultaneously — a melody and a harmony.

**SPECTRUM** — selects 48K BASIC mode for backward compatibility. Used to switch from the 128K editor back to the 48K-style command-line editor. Rare in practice.

**EDIT** — invokes the new full-screen editor on the specified line number.

### 3.4 RAM disks

The 128K provides a **RAM disk** — a portion of banked RAM that the BASIC treats like a tape drive or disk. Two RAM disk "drives" are provided:

- `M:` — fast RAM disk in banks 4 and 5 (32 KB total).
- `N:` — slower RAM disk in banks 6 and 7 (32 KB total).

Saving to and loading from the RAM disk uses the normal SAVE/LOAD syntax with a drive prefix:

```basic
10 SAVE "M:myfile" DATA a()
20 LOAD "M:myfile" DATA a()
```

The RAM disk is much faster than tape — saving a few KB takes milliseconds instead of minutes. It's used primarily as a workspace for program development and for caching frequently-accessed data.

Note that the RAM disk is volatile: it loses its contents when the machine is powered off or reset. It is not a substitute for a real disk.

### 3.5 The AY-3-8910 music chip

The Spectrum 128K is the first Sinclair Spectrum to include a **proper sound chip**: the General Instrument AY-3-8910, the same chip used in the MSX, the Atari ST, and many arcade machines. The AY provides three independent tone channels plus a noise channel, with envelope control.

The 128K BASIC exposes the AY via the PLAY keyword (see above) and via direct register access (via `OUT` to ports `#FFFD` and `#BFFD`). Machine-code programs typically access the chip directly rather than going through PLAY.

### 3.6 The Spanish 128K

The first Spectrum 128K was actually released in Spain, by Investrónica, in September 1985 — about six months before the UK launch. The Spanish ROM is nearly identical to the UK ROM, but:

- Includes an `Ñ` key in the keyword layout.
- Adds a different character set for displaying Spanish text.
- Has minor changes to the editor to support Spanish-language prompts (mostly in the boot menu, not in BASIC itself).

The Spanish ROM is rare outside Spain. From a BASIC-language standpoint, it is functionally identical to the UK 128K ROM.

### 3.7 Backwards compatibility

The 128K ROM is designed to run 48K BASIC programs unchanged. Programs that stick to documented BASIC features work identically on both machines. Programs that fail on the 128K usually do so because they:

- Use machine code that depends on the 48K ROM being at `#0000`–`#3FFF`. On the 128K, the bottom 16 KB can be either bank 0 (mostly 48K-compatible) or bank 1 (the new editor and extensions). If the program tries to call a ROM routine at a specific address, the call may end up in the wrong bank.
- Use the screen memory layout in ways that assume the 48K's 6.9 KB screen (vs. the 128K's larger contended-RAM layout, which is the same but with extra banks for shadow screens).
- Rely on undocumented 48K ROM behavior that was changed in the 128K.

Most commercial Spectrum software works on both machines. The few that don't usually have separate 48K and 128K versions.

---

## §4. The +2/+2A/+3 BASIC (1987)

When Amstrad bought the Sinclair brand in 1986, they quickly released two new machines: the +2 (April 1987) and the +3 (December 1987). Both shipped with an expanded BASIC that included disk commands.

### 4.1 The 64 KB ROM

The +2 and +3 contain a **64 KB ROM** divided into four 16 KB pages:

- **Page 0**: The 128K editor ROM (similar to the 128K's bank 1).
- **Page 1**: The original 48K BASIC ROM (for backward compatibility).
- **Page 2**: The +3 DOS ROM (disk operating system).
- **Page 3**: A patched 48K BASIC with a few +3-specific changes.

The four pages are switched into the `#0000`–`#3FFF` address range via the new paging port `#1FFD` (in conjunction with the 128K's existing `#7FFD`). The user sees a BASIC that behaves much like the 128K's, but with disk commands available.

### 4.2 The new disk commands

The +3 BASIC adds these disk-specific keywords:

- **CAT** — list the directory of the disk in the current drive.
- **FORMAT** — format a disk in either +3 DOS format (180 KB) or CP/M format.
- **MOVE** — copy a file from one disk to another.
- **COPY** — make a backup copy of an entire disk.
- **ERASE** — delete a file from the disk.

Plus extended forms of existing keywords:

- **LOAD** "name" — load from tape (legacy form).
- **LOAD** "a:myfile" — load from disk drive A.
- **LOAD** "a:*" — load the first file from disk drive A (wildcard).
- **SAVE** "a:myfile" LINE 10 — save to disk, auto-run from line 10.
- **SAVE** "a:myfile" CODE 32768, 1000 — save 1000 bytes starting at address 32768.
- **VERIFY** "a:myfile" — verify a file against disk.

The `a:` prefix selects drive A. The `m:` and `n:` prefixes still work for the 128K RAM disk (when available).

### 4.3 The +3's "plus 3" mode and CP/M

The +3's ROM includes a special mode called **Plus 3 mode** (or `+3` mode) in which the machine boots directly into CP/M. This is invoked by:

- Typing `FORMAT "a;c"` (or similar — the exact syntax varies) to format a disk with the CP/M system tracks.
- Then `LOAD *"cpm"` to load the CP/M image from disk into RAM.
- Then `RANDOMIZE USR 25000` to jump to the CP/M entry point.

Once CP/M is running, the +3 is effectively a CP/M machine. The +3 BASIC is not used while CP/M is running. See [cpm.md](cpm.md) for the details.

### 4.4 The +2A vs the +3

The +2A (1987) is functionally a +3 with the disk drive replaced by a cassette. The ROM is the same 64 KB; only the disk keywords that depend on actual hardware (`FORMAT "a:"`, `CAT "a:"`) generate "no disk" errors. The +2A's purpose was to provide the +3's capabilities at a lower price point.

From a BASIC-language standpoint, the +2, +2A, and +3 are essentially identical.

### 4.5 Compatibility issues

The +2/+3's BASIC is mostly backward-compatible with the 128K's, which is mostly backward-compatible with the 48K's. The main compatibility issues are:

- **Tape-load timing** changed slightly. Some tape-loading software that depends on exact timing breaks.
- **The 128K RAM disk** is preserved but accessed differently (the `M:` and `N:` drives are emulated using the banked RAM).
- **Machine code that depends on the 128K's port `#7FFD` only** may break on the +3, which has the additional `#1FFD` paging port. Programs that switch banks need to write to both ports to set the right paging mode.

These issues are documented in detail in [rom_plus2.md](rom_plus2.md).

### 4.6 The +3's keyboard

The +2 (grey case, 1987) used the same keyboard as the 128K — the Sinclair "toastrack" keyboard with a slightly improved mechanism. The +2A and +3 used a new keyboard that was much more PC-like, with proper full-travel keys.

From a BASIC standpoint, the keyboards are equivalent — they all produce the same keystrokes for the same BASIC keywords. The +2A/+3 keyboard is just much more pleasant to type on.

---
## §5. TR-DOS BASIC Extensions

Soviet clone machines (Pentagon, Scorpion, ATM Turbo, etc.) and their Western Beta 128 disk interfaces add a set of TR-DOS commands directly to BASIC. The commands are not part of the ROM proper — they are loaded from the TR-DOS ROM when needed.

### 5.1 How TR-DOS commands appear in BASIC

When a Beta 128 interface is connected, typing certain keywords automatically activates TR-DOS mode. The TR-DOS ROM replaces the bottom 16 KB of address space (`#0000`–`#3FFF`) with TR-DOS code while the disk operation is performed, then swaps the BASIC ROM back in.

From the user's perspective, TR-DOS commands look like normal BASIC keywords. They are typed in the same way (using the keyword entry system), they appear in program listings the same way, and they integrate with normal BASIC variables and expressions.

### 5.2 The TR-DOS command set

TR-DOS adds the following commands to BASIC:

| Command | Purpose |
|---|---|
| `CAT` | List the disk directory |
| `FORMAT` | Format a disk in TR-DOS format |
| `LOAD "name"` | Load a BASIC program from disk |
| `SAVE "name"` | Save a BASIC program to disk |
| `LOAD "name" CODE addr, len` | Load machine code or screen |
| `SAVE "name" CODE addr, len` | Save machine code or screen |
| `LOAD "name" DATA var()` | Load an array |
| `SAVE "name" DATA var()` | Save an array |
| `LOAD "name" LINE n` | Load and auto-run from line n |
| `VERIFY "name"` | Verify a file against disk |
| `MERGE "name"` | Merge a BASIC program with current |
| `ERASE "name"` | Delete a file from disk |
| `RUN "name"` | Equivalent to LOAD + RUN |
| `COPY` | Copy entire disk |
| `MOVE` | Copy a single file between disks |

These mirror the +3 DOS commands almost exactly, but with the TR-DOS naming convention (8-char filename + 1-char extension) and the Beta 128 disk format.

### 5.3 The TR-DOS command-line mode

Pressing the special TR-DOS key combination (typically `Symbol Shift` + `Enter`, or a dedicated key on Soviet clones) drops the user into a TR-DOS command-line mode:

```
TR-DOS 5.03
> 
```

From this prompt, you can type TR-DOS commands directly without wrapping them in BASIC syntax. For example:

```
TR-DOS 5.03
> CAT
> LOAD "MYPROG"
> FORMAT
> *
```

The `*` command exits TR-DOS mode and returns to BASIC. This mode is useful for disk maintenance (formatting, copying) without writing a BASIC program to do it.

### 5.4 Programming patterns

A typical Soviet-era game or demo using TR-DOS has a small BASIC loader that loads the machine code and runs it:

```basic
10 CLEAR 24575: REM Reserve memory below 24576 for code
20 LOAD "" SCREEN$: REM Load the loading screen
30 LOAD "" CODE : REM Load the machine code (auto-loads to last loaded addr)
40 RANDOMIZE USR 24576: REM Jump to the machine code entry point
```

The `LOAD ""` syntax (with empty name) loads the first file on the disk. This is the standard "double-click to run" pattern on Soviet clones.

### 5.5 Compatibility with Western BASIC

The TR-DOS BASIC extensions are **mostly source-compatible** with the +3 DOS BASIC extensions. The same keywords do the same things. The differences are:

- Filename format: 8+1 (TR-DOS) vs. 8+3 (+3 DOS).
- Disk format: TRD vs. DSK.
- Error codes: differ in detail.
- The TR-DOS `CAT` listing uses Cyrillic by default; the +3 DOS `CAT` uses Latin.

A BASIC program that uses `LOAD "name"` for disk access works on both systems, with appropriate filename changes.

---

## §6. The Sinclair QL SuperBASIC (Brief Detour)

The **Sinclair QL** (Quantum Leap), released in January 1984, was Sinclair's "serious" machine — aimed at small businesses and power users, positioned above the Spectrum. It shipped with a Sinclair-produced BASIC called **SuperBASIC**, which was a substantial departure from the Spectrum's BASIC.

SuperBASIC is worth a brief mention here because it shows what Sinclair's BASIC thinking looked like in 1984 — and highlights how conservative the Spectrum's BASIC was even at the time.

### 6.1 SuperBASIC features

SuperBASIC added many features that the Spectrum's BASIC lacked:

- **Proper structured programming**: `IF`/`ELSE`/`END IF`, `WHILE`/`END WHILE`, `REPEAT`/`UNTIL`, `SELECT`/`END SELECT`.
- **Multi-line procedures and functions**: `DEFINE PROCEDURE Foo` ... `END DEFINE Foo`.
- **Local variables**: `LOCal a, b, c`.
- **Arrays as first-class values** — could be passed to procedures.
- **Float-only arithmetic**: no integer type distinction (everything is float).
- **A proper full-screen editor** built in.
- **Graphics windows**: multiple independent graphics contexts.
- **Microdrive support**: integrated as a normal file device (`mdv1_`, `mdv2_`).

SuperBASIC ran on a Motorola 68008 (not a Z80) and was implemented as part of the QL's QDOS operating system rather than as the OS itself. The QL did not have the Spectrum's "BASIC is the OS" design — QDOS was a real, multitasking, multi-threaded OS with SuperBASIC as one of its programming languages.

### 6.2 Why SuperBASIC matters to Spectrum users

The QL was a commercial failure (production problems, late delivery, buggy initial ROM). But SuperBASIC influenced later BASIC developments:

- The **128K BASIC**'s full-screen editor was likely inspired by SuperBASIC's editor.
- Modern open replacements for the Spectrum's BASIC (SE BASIC, NextBASIC) adopt many SuperBASIC-like features.

If you want to know what Sinclair was *really* thinking about BASIC design in the 1980s, SuperBASIC is the answer — not the Spectrum's intentionally-minimalist BASIC.

### 6.3 Compatibility with Spectrum BASIC

None. SuperBASIC is a different language on different hardware. Spectrum BASIC programs do not run on the QL, and vice versa.

---

## §7. SE BASIC and OpenSE (Modern Replacement ROMs)

The Spectrum hobbyist community in the 2000s and 2010s produced several modern open-source replacement BASIC ROMs. The most prominent are **SE BASIC** and its successor **OpenSE BASIC**, both primarily by **Andrew Owen**.

### 7.1 What SE BASIC is

SE BASIC ("Spectrum Expanded BASIC") is a from-scratch reimplementation of the Spectrum BASIC ROM that:

- Fits in the same 16 KB address space.
- Is **bug-for-bug compatible** with the 48K ROM for most programs.
- Adds new keywords and features where the original ROM had errors or limitations.
- Is **open source** (GPL), allowing users to study and modify it.

The project started in 2002 with the goal of providing a "fixed and extended" BASIC ROM for the Spectrum community. Andrew Owen and a small team of contributors rebuilt the ROM from disassemblies of the original, replacing the floating-point library, fixing known bugs, and adding new features.

### 7.2 SE BASIC's extensions

SE BASIC adds several features missing from the original 48K BASIC:

- **`ELSE`** clause on IF statements: `IF a = 1 THEN PRINT "one" ELSE PRINT "not one"`.
- **`DO` / `LOOP` / `WHILE` / `UNTIL`** structured loops.
- **`REPEAT` / `UNTIL`** loops (BBC BASIC style).
- **`PROC` and `FN` for multi-line procedures and functions** (BBC BASIC style).
- **`ENDIF` and `ENDPROC`** block delimiters.
- **Native floating-point speed improvements** — typically 2-3x faster than the original ROM.
- **A cleaner editor** that supports both 48K-style and 128K-style editing.

The result is a BASIC that feels much more modern than the 1982 original, while still fitting in a standard 16 KB ROM and running on a stock 48K Spectrum.

### 7.3 OpenSE BASIC

OpenSE BASIC (also known as SE BASIC Next) is the modern continuation of SE BASIC, hosted on GitHub. It:

- Targets the ZX Spectrum Next as well as stock Spectrums.
- Adds more keywords for hardware-acceleration (`SPRITE`, `TILEMAP`, `LAYER2` — these mirror NextBASIC's features).
- Has an actively-maintained source tree.
- Is the recommended "open BASIC ROM" for hobbyist projects in 2024.

For Spectrum owners who want a "better BASIC" than the original Sinclair ROM, OpenSE BASIC is the standard choice.

### 7.4 Compatibility

SE BASIC / OpenSE BASIC are designed to be backward-compatible with the original 48K ROM. Programs that stick to standard Sinclair BASIC run unchanged. The new features are opt-in — old programs do not use them.

The main compatibility issue is that SE BASIC is faster than the original ROM, which can break timing-sensitive machine-code programs that hook into ROM routines. For pure BASIC programs, this is rarely an issue.

---

## §8. NextBASIC (2017)

The ZX Spectrum Next ships with **NextBASIC** — a substantially extended BASIC written by Garry Lancaster as part of NextZXOS. NextBASIC is the most capable Spectrum BASIC ever produced, with full access to the Next's hardware features (Layer 2 graphics, hardware sprites, tilemap, copper, DMA).

### 8.1 NextBASIC's design goals

NextBASIC was designed to:

1. Be **source-compatible with the original 48K/128K BASIC** for backward compatibility.
2. Add **structured programming constructs** (proper IF/ELSE, DO/LOOP, multi-line procedures).
3. Provide **direct access to the Next's hardware** from BASIC, without dropping to machine code.
4. Be **extensible** — new keywords can be added by NextBASIC extensions loaded from SD card.

The result is a BASIC that can write smooth-scrolling hardware-sprite games without ever calling a machine-code routine.

### 8.2 The `#` syntax

NextBASIC's distinguishing feature is the **`#` syntax** for hardware extensions. A statement starting with `#` invokes a hardware-acceleration subsystem:

```basic
# L2 POKE 100, 50, 255
```

This writes a single pixel (color 255) at position (100, 50) on the Layer 2 (256-color) framebuffer. The equivalent machine code would be dozens of instructions involving bank switching and port writes.

The major `#` subsystems are:

- **`#L2`** — Layer 2 (256-color framebuffer): pixel plotting, line drawing, copying, clearing.
- **`#SPRITE`** — hardware sprites: define, move, hit-test, animate.
- **`#TILEMAP`** — hardware tilemap: define tiles, draw, scroll.
- **`#COPPER`** — copper (programmable raster effects): load, run, stop.
- **`#DMA`** — DMA controller: bulk memory or I/O transfers.
- **`#MMU`** — memory management unit: bank switching.
- **`#ESP`** — ESP32 module: WiFi, accelerator control.

A simple NextBASIC program that draws a moving sprite might look like:

```basic
10 # SPRITE 0, 1, SETUP, 16, 16, 0     ; Set up sprite 0 with 16x16 pattern from bank 0
20 # SPRITE 0, 1, MOVE, 100, 100       ; Move sprite 0 to (100, 100)
30 FOR x = 0 TO 200
40   # SPRITE 0, 1, MOVE, x, 100       ; Move sprite 0 along x
50   PAUSE 2                            ; Wait 2 frames
60 NEXT x
70 # SPRITE 0, 1, REMOVE                ; Remove sprite 0
```

This produces smooth 50-Hz hardware-sprite motion with zero machine code.

### 8.3 Structured programming

NextBASIC adds proper structured-programming constructs:

```basic
10 PROC main
20 STOP
30 DEF PROC main
40   LOCAL x
50   FOR x = 1 TO 10
60     IF x MOD 2 = 0 THEN
70       PRINT x; " is even"
80     ELSE
90       PRINT x; " is odd"
100    END IF
110  NEXT x
120 END PROC
```

This is BBC BASIC-style multi-line procedures with local variables, real IF/ELSE/END IF blocks, and proper scoping. The code is dramatically more readable than the original Sinclair BASIC style.

### 8.4 NextBASIC extensions

NextBASIC supports loadable **extensions**: small modules (typically written in C with the Fuzix C compiler, or in assembly) that add new keywords to BASIC. An extension is loaded with:

```basic
10 # LOAD "MYEXT"
```

After this, the keywords `MYEXT` defined in the extension become available. This makes NextBASIC open-ended — the Next team and community have added many extensions over the years for networking, file formats, media playback, and so on.

### 8.5 Compatibility with original BASIC

NextBASIC runs original 48K and 128K BASIC programs unchanged. The original keywords are all there with their original behavior. The new features are purely additive — they do not change the meaning of existing keywords.

The one notable exception is performance: NextBASIC runs on the Next's turbo mode (28 MHz Z80) by default, which is roughly 7x faster than a stock Spectrum. Timing-sensitive programs may need to be throttled with `PAUSE` statements.

---
## §9. Comparison of Dialects

This section pulls together the dialects discussed above into a single feature matrix. The intent is to help you pick the right BASIC for a given task, or to understand what changes when moving code from one dialect to another.

### 9.1 Feature matrix

| Feature | 48K | 128K | +2/+2A/+3 | TR-DOS ext | SE BASIC | NextBASIC |
|---|---|---|---|---|---|---|
| Line numbers | Yes | Yes | Yes | Yes | Yes | Yes (optional) |
| Single-keyword entry | Yes | Yes | Yes | Yes | Yes | Yes |
| Tokenised source | Yes | Yes | Yes | Yes | Yes | Yes |
| Floats | Yes (5-byte) | Yes | Yes | Yes | Yes (fast) | Yes |
| Integers | Slow | Slow | Slow | Slow | Slow | Slow (or none) |
| ELSE on IF | **No** | No | No | No | **Yes** | **Yes** |
| DO/WHILE loops | **No** | No | No | No | **Yes** | **Yes** |
| Multi-line procedures | **No** | No | No | No | **Yes** | **Yes** |
| Full-screen editor | **No** | Yes | Yes | Yes | Optional | Yes |
| Tape I/O | Yes | Yes | Yes | Yes | Yes | Yes (DMA-fast) |
| Disk I/O | **No** | RAM only | **Yes** (+3 DOS) | **Yes** (TR-DOS) | Via extensions | **Yes** (FAT/SD) |
| Sound | Beep | Beep + AY | Beep + AY | Beep + AY | Beep + AY | Beep + AY + DMA |
| Hardware sprites | **No** | No | No | No | **No** | **Yes** |
| Tilemap | **No** | No | No | No | **No** | **Yes** |
| Layer 2 (256-color) | **No** | No | No | No | **No** | **Yes** |
| Copper | **No** | No | No | No | **No** | **Yes** |
| Networking | **No** | No | No | No | **No** | **Yes** (ESP32) |
| Year | 1982 | 1986 | 1987 | 1985+ | 2002 | 2017 |
| Vendor | Sinclair | Sinclair | Amstrad | Soviet (various) | Andrew Owen | Garry Lancaster |

### 9.2 What does "Sinclair BASIC" mean in 2024?

If you say "Sinclair BASIC" today, you might mean:

1. **The 48K BASIC ROM** — the canonical version, used in almost all "learn Spectrum programming" tutorials.
2. **The 128K BASIC ROM** — used by anyone running original 128K hardware or most emulators' default 128K profile.
3. **The +2/+2A/+3 BASIC** — used by anyone running original +3 hardware or working with +3 disk software.
4. **TR-DOS BASIC** — used by anyone running Soviet clones (most of the Russian demoscene).
5. **SE BASIC / OpenSE** — used by hobbyists who want a "modernised" BASIC on stock hardware.
6. **NextBASIC** — used by anyone on the ZX Spectrum Next, the only modern Spectrum being actively sold in 2024.

The features most users associate with "Sinclair BASIC" — single-keyword entry, tokenised source, line numbers, two-character variable names, no ELSE — come from the 48K ROM. The later dialects preserve these but add more. NextBASIC is the only dialect that materially changes the programming experience.

### 9.3 Which BASIC should I use?

For a 2024 hobbyist:

- **Learning Spectrum history**: use the **48K ROM** (in an emulator like Fuse or ZEsarUX, or on real 48K hardware). This is the canonical Sinclair experience.
- **Writing modern Spectrum software**: use **NextBASIC** on the ZX Spectrum Next. It is the only dialect that gives you access to hardware-accelerated graphics without dropping to assembly.
- **Hacking on real 128K/+3 hardware**: use the machine's native ROM. The +3's built-in disk support is the most convenient for real hardware.
- **Running Soviet-era demos and games**: use **TR-DOS BASIC** on a Pentagon clone (or an emulated Pentagon). Most Soviet software targets this exact configuration.
- **Building a "better BASIC" experiment**: use **OpenSE BASIC**. It is open source, modern, and runs on stock hardware.

### 9.4 Resources

- [The Official Sinclair BASIC Manual](https://worldofspectrum.org/) — the canonical reference. Available as a free PDF from World of Spectrum.
- [The Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip) — the famous full disassembly of the 48K ROM with commentary. The standard reference for ROM hackers.
- [The Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip) — covers the 128K ROM as well.
- **NextBASIC Manual** — the Next team's official documentation, available as a free PDF from the ZX Spectrum Next website.
- [SE BASIC documentation](https://github.com/cheveron/sebasic) — in the OpenSE BASIC GitHub repository.

---

## §10. Cross-References

- **[rom_48k.md](rom_48k.md)** — The 48K ROM internals. The actual binary that contains the BASIC interpreter, the editor, the calculator stack, the floating-point library, and all the rest of the 48K's "OS".
- **[rom_128k.md](rom_128k.md)** — The 128K ROM internals. The two-bank layout, the new editor, the music chip driver.
- **[rom_plus2.md](rom_plus2.md)** — The +2/+2A/+3 ROM variants. The 64 KB four-page layout, the +3 DOS integration, the CP/M boot mode.
- **[trdos.md](trdos.md)** — TR-DOS's BASIC extensions in detail (§5 of this article is a brief summary).
- **[plus3dos.md](plus3dos.md)** — +3 DOS's BASIC commands in detail (§4 of this article is a brief summary).
- **[nextzxos.md](nextzxos.md)** — NextBASIC and the Next's OS in detail (§8 of this article is a brief summary).
- **[../05_development/01_basic/README.md](../05_development/01_basic/README.md)** — Spectrum BASIC programming in depth. BASIC is one option; assembly is the other major one.
- **[../07_demoscene/demo_frameworks.md](../07_demoscene/demo_frameworks.md)** — How BASIC is used in modern Spectrum demo development. (Mostly it isn't — modern demos are written in assembly — but classic-style BASIC demos exist.)

---

## References

### External references

- [Complete Spectrum ROM Disassembly (Logan & O'Hara, 1983)](https://worldofspectrum.org/ROMdisassembly.zip) — the canonical annotated source of the 48K BASIC interpreter; documents every keyword, every syntax rule, and every error code referenced throughout this article.
- [Sinclair ZX Spectrum 48K BASIC Manual (Vickers, 1982)](https://worldofspectrum.org/faq/reference/basicreference.htm) — the primary-source reference for the original Sinclair BASIC keyword set, syntax, and error handling.
- [Andrew Owen — SE BASIC / OpenSE BASIC](https://github.com/cheveron/sebasic) — the modern open-source replacement ROM; reference implementation for the extended BASIC dialects covered in §7.
- [Boriel — ZX BASIC Compiler](https://www.boriel.com/wiki/en/index.php/ZX_BASIC:Documentation) — modern cross-platform BASIC compiler that extends Sinclair BASIC syntax with structured-programming constructs.
- [Spectrumpedia (Alessandro Grussu)](https://www.alessandrogrussu.it/zx/) — encyclopedic reference for the divergent BASIC dialects shipped with Soviet clones (ATM Turbo's `BASIC 128`, Profi's extended editor, Pentagon's Russian-localized ROM variants).
- [zx-pk.ru — BASIC dialects and ROM extensions subforum](https://zx-pk.ru/) — primary Russian-language community archive for clone-specific BASIC extensions, Russian-language keyword sets, and homebrew replacement ROMs.

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same license.
