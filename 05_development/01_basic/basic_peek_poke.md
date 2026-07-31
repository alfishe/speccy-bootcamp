[← Home](../../README.md) · [BASIC](README.md)

# Basic PEEK, POKE, and USR — Bridging BASIC and Machine Code

Sinclair BASIC is slow — a `FOR/NEXT` loop counting to 1000 takes 10 seconds, where the equivalent Z80 machine code takes under a millisecond. The ROM gives the BASIC programmer **three escape hatches** that bypass the interpreter and let the program touch the hardware directly:

- **`PEEK(address)`** — read one byte from any memory location
- **`POKE address, value`** — write one byte to any memory location
- **`USR address`** — call a machine code subroutine at the given address

These three keywords are the **gateway from BASIC to assembly language**. Every Spectrum programmer who outgrows BASIC eventually learns them; many never write a single line of Z80 assembly but still use `PEEK`/`POKE`/`USR` to drive machine code routines loaded from tape or typed in from magazine listings. This article covers the practical use of these commands, the conventions for calling machine code, and the common pitfalls.

> [!NOTE]
> This article covers **BASIC-to-machine-code interop**. For learning Z80 assembly itself, see [assembly_intro.md](../02_assembly/assembly_intro.md) (planned). For the ROM routines callable from BASIC via `USR`, see [rom_routines.md](../../10_references/rom_routines.md).

---

## PEEK — Reading Memory

```basic
LET A = PEEK(address)
```

`PEEK` is a function that returns the **single byte** at the given memory address. The address must be in the range 0–65535 (the Z80's 16-bit address space). The returned value is 0–255.

### Common Uses

| Task | Code | Notes |
|---|---|---|
| Read frame counter low byte | `LET F = PEEK 23672` | `FRAMES` is at `#5C78` (23672); this is the low byte of a 3-byte counter |
| Read keyboard state | `LET K = PEEK 23560` | `KSTATE`-derived `LAST_K` at `#5C08` returns last key pressed |
| Read attribute byte | `LET A = PEEK 22592` | Reads attribute at character cell (0, 0) — `ATTR_ADDR = 22528 + line*32 + col` |
| Test RAMTOP | `LET R = PEEK 23730 + 256 * PEEK 23731` | `RAMTOP` system variable at `#5C8A` (big-endian) |
| Read a screen pixel byte | `LET B = PEEK 16384` | Reads byte at top-left of screen memory |

### Reading 16-bit Values

The Z80 is **little-endian**: 16-bit values are stored low byte first, high byte second. To read a 16-bit value, you must combine two `PEEK`s:

```basic
10 REM Read the 16-bit value at address ADDR
20 LET ADDR = 23670
30 LET LOW_BYTE = PEEK ADDR
40 LET HIGH_BYTE = PEEK (ADDR + 1)
50 LET VALUE = LOW_BYTE + 256 * HIGH_BYTE
```

For convenience, define a reusable function-like subroutine:

```basic
10 DEF FN P(A) = PEEK A + 256 * PEEK (A + 1)
20 PRINT FN P(23670)   : REM prints the 16-bit value at address 23670
```

> [!NOTE]
> Sinclair BASIC's `DEF FN` allows defining single-line functions. The function is **expanded inline** at every call site — there is no call overhead. This makes `FN P(addr)` just as fast as the explicit `PEEK + 256 * PEEK` form, but far more readable.

### Reading the Frame Counter

The `FRAMES` counter at `#5C78`–`#5C7A` (23672–23674) is a **3-byte counter** incremented by the ROM's interrupt handler every video frame (~50 Hz). It is the standard way to time events in BASIC:

```basic
10 LET START = PEEK 23672 + 256 * (PEEK 23673 + 256 * PEEK 23674)
20 REM ... do something ...
30 LET END = PEEK 23672 + 256 * (PEEK 23673 + 256 * PEEK 23674)
40 LET ELAPSED_FRAMES = END - START
50 LET ELAPSED_SECONDS = ELAPSED_FRAMES / 50
60 PRINT "Elapsed: "; ELAPSED_SECONDS; " sec"
```

The counter wraps around after roughly 38 hours (2^24 frames / 50 Hz). It is read atomically by reading the low byte first — the ROM has a clever trick where it re-reads the low byte if the high bytes change mid-read, ensuring a consistent 24-bit value.

---

## POKE — Writing Memory

```basic
POKE address, value
```

`POKE` writes a single byte (`value`, 0–255) to the given memory address. It is the inverse of `PEEK`. The `address` must be writable RAM — `POKE 0, 42` writes to ROM and is silently ignored on a 48K Spectrum (the ROM is read-only).

### Common Uses

| Task | Code | Notes |
|---|---|---|
| Set border color | `POKE 23624, 2` | `BORDCR` at `#5C48` controls border color (low 3 bits) |
| Set attribute cell | `POKE 22592, 56` | Writes attribute at cell (0, 0) — paper 7, ink 0 (white-on-black) |
| Pause-resume `PAUSE` | `POKE 23672, 0` | Reset frame counter, used to break out of `PAUSE` |
| Disable interrupts | `POKE 30000, 243: USR 30000` | (example) — poke `DI` opcode then call it |
| Move program area | (very careful!) — manipulating `PROG` and `VARS` pointers | Advanced technique, easy to crash the machine |

### Setting an Attribute Cell

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

### Filling a Region

To fill the entire screen with a single attribute (a "clear to color"):

```basic
10 LET ATTR_BYTE = 33      : REM paper 4 (green), ink 1 (blue)
20 FOR A = 22528 TO 23295  : REM 768 bytes from #5800 to #5AFF
30   POKE A, ATTR_BYTE
40 NEXT A
```

This is slow — about 5 seconds for the full screen — but it works. For faster fills, machine code is essential (a `LDIR` block-fill is 50× faster).

### The Perils of POKE

`POKE` will write to **any writable address** — including system variables, the BASIC program itself, the screen, and the stack. A wrong `POKE` can crash the machine instantly. Some particularly dangerous targets:

| Target | Effect of POKE |
|---|---|
| `23670` (`ERR_SP`) | Crashes on next error |
| `23613` (`CH_ADD`) | Corrupts the BASIC line pointer; next line read fails |
| `23698` (`STACK_PT`) | Stack corruption, immediate crash |
| Stack area (`#FF58`–down) | Corrupts return addresses, immediate crash |
| Screen memory (`#4000`–`#57FF`) | Visible garbage; not usually fatal |
| BASIC program text (`PROG` area) | Corrupts your own program; usually fatal on next RUN |

> [!WARNING]
> Always save your program before experimenting with `POKE` to unfamiliar addresses. A typo like `POKE 23613, 0` instead of `POKE 23612, 0` will instantly crash the machine, and any unsaved program is lost.

---

## USR — Calling Machine Code

```basic
LET A = USR address
PRINT USR address
USR address                : REM legal but the return value is discarded
```

`USR address` calls a machine code subroutine at the given address. The subroutine runs with full control of the CPU — it can read and write memory, ports, the stack, everything. When the subroutine executes a `RET` instruction, control returns to BASIC, and the **return value is whatever is in the BC register pair** at that moment.

### The Calling Convention

When `USR addr` is called:

1. The CPU jumps to `addr`
2. The **HL register pair** contains the current value of `STKEND` (a system variable pointing to the calculator stack)
3. The **BC register pair** on return becomes the function's value
4. Interrupts may or may not be enabled — typically they are, but your routine can disable them with `DI` and re-enable with `EI`

The machine code routine must end with `RET` (`#C9`) to return to BASIC. Any other exit (jumping to a ROM routine, infinite loop, crash) leaves BASIC in an undefined state.

### Simple Example — Clear the Screen Fast

A machine code routine that clears the screen, much faster than `CLS`:

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

### Passing Parameters

There are several conventions for passing parameters from BASIC to a machine code routine:

#### Method 1: POKE Before USR

```basic
10 POKE 30000, COLOR_BYTE      : REM patch the routine's data byte
20 LET RESULT = USR 30001      : REM call starting after the patched byte
```

This is simple but requires knowing where to patch. Useful for "configuration" parameters (color, address, count) that are read by the routine as data.

#### Method 2: System Variables

```basic
10 POKE 23680, 100             : REM write to a "scratch" system variable
20 LET RESULT = USR 30000      : REM the routine reads from #5C80
```

The system variables `#5C80`–`#5C81` (`SCRATCH` / unused on 48K) can be used as a parameter-passing area. The machine code reads them via `LD A, (#5C80)`.

#### Method 3: Use STKEND

Because `USR` passes `STKEND` in HL, you can use the calculator stack to pass floating-point values:

```basic
10 REM Push values via a fake PRINT expression
20 PRINT USR 30000 + 1.5, USR 30000 + 2.5
30 REM (The above calls USR 30000 twice, with the calculator stack set up)
```

This is an advanced technique that requires understanding the calculator stack format — see [assembly_intro.md](../02_assembly/assembly_intro.md) (planned).

#### Method 4: Use MEM$ or Memory Region

Poke parameters into a fixed memory region that both BASIC and machine code agree on:

```basic
10 REM Parameter area at 32000-32009
20 POKE 32000, 100      : REM parameter 1
30 POKE 32001, 200      : REM parameter 2
40 LET RESULT = USR 30000
```

The machine code reads parameters via:

```asm
        LD  HL, #7D00           ; 32000 = #7D00
        LD  A, (HL)             ; parameter 1
        INC HL
        LD  B, (HL)             ; parameter 2
        ...
```

This is the most flexible method and is used by most commercial BASIC programs that call machine code.

### Return Value Convention

The return value of `USR addr` is the **16-bit unsigned value in BC** on return. To return a specific value:

```asm
        LD  BC, #1234           ; return value = #1234 = 4660
        RET
```

Or, if you want to return a byte:

```asm
        LD  B, #0               ; high byte = 0
        LD  C, A                ; low byte = A
        RET
```

If your routine does not set BC explicitly, you will get whatever value happens to be in BC — typically garbage. Always set BC explicitly before `RET` if you care about the return value.

> [!IMPORTANT]
> The return value is treated as **unsigned**. If you want a signed result, you must interpret values ≥ 32768 as negative in your BASIC code: `LET SIGNED = R - 256 * (R > 32767)`. Most BASIC code uses only small positive return values (0–255 or 0–65535).

---

## Loading Machine Code from Tape

Hand-typing opcodes via `POKE` is tedious. The standard way to distribute machine code is as a **code block** on tape (or .tap/.tzx file). The BASIC command to load such a block is:

```basic
LOAD "" CODE
```

Or, to load to a specific address:

```basic
LOAD "GAME" CODE 30000
```

`LOAD "" CODE` reads the next code block from tape and writes it to the address specified in the tape header. `LOAD "name" CODE addr` reads a named block and writes it to `addr` (overriding the header's address). The block is loaded as raw bytes — no tokenization, no line numbers.

A typical loader program looks like:

```basic
10 PRINT "Loading game..."
20 LOAD "" CODE 30000
30 RANDOMIZE USR 30000
```

Line 20 loads the code block to address 30000. Line 30 calls it — `RANDOMIZE USR addr` is the standard idiom for "call machine code and discard the return value". (Using just `USR addr` would work but produces a syntax error in some contexts because `USR` is technically a function, not a statement. `RANDOMIZE USR addr` is a statement that uses the function's return value as the new random seed — which we then ignore.)

> [!NOTE]
> **`RANDOMIZE USR addr` vs `LET X = USR addr`**: Both call the machine code at `addr`. The first discards the return value (uses it as the random seed, which is usually irrelevant). The second saves the return value in variable X. For one-shot calls to game/driver code, `RANDOMIZE USR addr` is the idiom. For utility routines that return meaningful values, `LET X = USR addr` is preferred.

### Saving Machine Code

To save a code block:

```basic
SAVE "GAME" CODE 30000, 4096
```

This saves 4096 bytes starting at address 30000 as a code block named "GAME". The block can then be loaded with `LOAD "GAME" CODE 30000` on any Spectrum.

---

## Practical Examples

### Example 1: Fast CLS with Attribute

```basic
10 REM Fast clear-screen with attribute
20 FOR A = 0 TO 13: READ B: POKE 30000 + A, B: NEXT A
30 DATA 33, 0, 88, 54, 56, 17, 1, 88, 1, 255, 2, 237, 176, 201
40 INPUT "Attribute byte? "; AB
50 POKE 30004, AB
60 LET R = USR 30000
```

The user enters an attribute byte (e.g., 56 for white-on-black, 33 for blue-on-green) and the routine clears the screen to that attribute in roughly 1 millisecond.

### Example 2: Read a Specific Screen Pixel

```basic
10 REM Pixel reader — given (X, Y), return 0 or 1
20 FOR A = 0 TO 35: READ B: POKE 31000 + A, B: NEXT A
30 DATA 62, 0, 33, 0, 64, 94, 87, 22, 0, 22, 0, 22, 0, 22, 0, 22, 0, 22, 0, 22, 0, 22, 0, 22, 0, 126, 0, 175, 71, 0, 0, 0, 0, 0, 0
40 INPUT "X (0-255)? "; X
50 INPUT "Y (0-175)? "; Y
60 POKE 31001, X
70 POKE 31004, Y
80 LET P = USR 31000
90 IF P > 0 THEN PRINT "Pixel set" ELSE PRINT "Pixel clear"
```

(Note: the above machine code is illustrative — actual pixel-reading routines are more complex because of the Spectrum's nonlinear screen layout. See [pixel_address.md](../05_display_and_timing/pixel_address.md) (planned) for the address calculation.)

### Example 3: Print Free Memory

```basic
10 REM Print free RAM between VARS and RAMTOP
20 LET V = PEEK 23627 + 256 * PEEK 23628   : REM VARS pointer
30 LET R = PEEK 23730 + 256 * PEEK 23731   : REM RAMTOP
40 PRINT "Free RAM: "; R - V; " bytes"
```

This computes the gap between the variables area (which grows upward as you create variables) and the top of RAM (which is fixed). It is the equivalent of `FRE(0)` in Microsoft BASIC — Sinclair BASIC does not have a built-in `FRE` function, so this manual computation is required.

### Example 4: Add Two Numbers in Machine Code

A routine that takes two parameters (poked into a scratch area) and returns their sum:

```asm
        LD  HL, (#5C80)         ; load two bytes from "scratch" system var
        LD  A, L
        ADD A, H
        LD  L, A       ; result in L (low byte)
        LD  H, 0       ; high byte = 0
        LD  B, H
        LD  C, L       ; BC = result
        RET
```

In BASIC:

```basic
10 REM Install add routine
20 FOR A = 0 TO 14: READ B: POKE 32000 + A, B: NEXT A
30 DATA 42, 128, 92, 124, 132, 111, 96, 124, 237, 67, 124, 201, 0, 0, 0
40 REM Use it
50 POKE 23680, 7     : REM first number (scratch system var low byte)
60 POKE 23681, 5     : REM second number (scratch system var high byte)
70 LET SUM = USR 32000
80 PRINT "Sum = "; SUM
```

This is a contrived example (adding two numbers in BASIC is far simpler: `LET SUM = 7 + 5`), but it illustrates the parameter-passing and return-value conventions that real machine code routines use.

---

## Common Pitfalls

### 1. POKE to ROM

```basic
POKE 0, 42          : REM silently ignored — ROM is read-only
```

No error is raised. The write simply has no effect. On a 128K, this might write to paged RAM at `#0000` if a RAM page is paged into the lower 16K — be careful.

### 2. POKE That Crashes the Machine

```basic
POKE 23613, 0       : REM corrupts CH_ADD — instant crash on next line read
POKE 23730, 0       : REM corrupts RAMTOP — may crash on next variable allocation
```

Always `SAVE` your program before experimenting with `POKE` to system variables.

### 3. USR Without RET

```basic
POKE 30000, 0       : REM 0 = NOP, not RET
LET R = USR 30000   : REM hangs — routine never returns
```

The routine must end with `RET` (byte `#C9` = 201). Without it, the CPU continues executing whatever bytes happen to be in memory after your routine — typically garbage, eventually crashing or hanging.

### 4. Wrong Address Calculation

```basic
POKE 16384, 255     : REM writes to top-left of screen — visible
POKE 16384 + 32, 255 : REM writes one row down — visible
POKE 16384 + 256, 255 : REM writes 8 rows down — VISIBLE BUT COUNTERINTUITIVE
```

The screen memory layout is nonlinear — moving "down one row" is not +32 (one row is 32 bytes in attribute space, but in pixel space the rows are interleaved in 8-pixel-third blocks). See [pixel_address.md](../05_display_and_timing/pixel_address.md) (planned) for the correct formula. This is one of the most confusing aspects of the Spectrum for new programmers.

### 5. BC vs HL vs A on Return

`USR`'s return value is in **BC**, not in A or HL. A common bug is to write a routine that leaves its result in A or HL, then forget to copy to BC before RET:

```asm
        ; BAD — returns garbage
        LD  A, 42               ; result in A
        RET                     ; BASIC reads BC, which is undefined

        ; GOOD — returns 42
        LD  A, 42
        LD  BC, 0               ; high byte = 0
        LD  C, A                ; low byte = 42
        RET
```

### 6. POKEing Too Many Bytes

```basic
FOR A = 30000 TO 99999: POKE A, 0: NEXT A
```

Addresses above 65535 are out of range. The `POKE` will produce `B Integer out of range, 0:1` — but only after writing `POKE 65535, 0`. Anything between 65536 and the start of your loop will be skipped silently if the BASIC `FOR` loop wraps around (it doesn't — BASIC detects the out-of-range and stops).

### 7. USR Address as a Variable

```basic
10 LET A = 30000
20 LET R = USR A         : REM works — A is a numeric variable
30 LET R = USR (A)       : REM also works — parentheses are optional
40 LET R = USR "30000"   : REM syntax error — USR takes a numeric argument
```

The `USR` argument must be a numeric expression, not a string.

---

## When to Use PEEK/POKE/USR

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

- [Basic intro](basic_intro.md) — Sinclair BASIC foundation: tokens, syntax, variables
- [Basic graphics](basic_graphics.md) — `PLOT`, `DRAW`, `CIRCLE`, `POINT`, `ATTR`
- [Basic sound](basic_sound.md) — `BEEP` and the beeper
- [Assembly intro](../02_assembly/assembly_intro.md) (planned) — learning Z80 assembly
- [ROM routines](../../10_references/rom_routines.md) — callable ROM routines
- [Memory maps](../../10_references/memory_maps.md) — full system variable table
- [Pixel address calculation](../05_display_and_timing/pixel_address.md) (planned) — nonlinear screen layout
- [Screen access](../06_graphics/screen_access.md) (planned) — direct screen writes from Z80
- [Basic token table](../../10_references/basic_token_table.md) — byte values for `PEEK`, `POKE`, `USR` tokens

---

## References

- **Sinclair ZX Spectrum Basic Programming** (Steven Vickers, 1982) — chapter 26 covers `PEEK`, `POKE`, and `USR` in detail
- **The Complete Spectrum ROM Disassembly** (Logan & O'Hara, 1983) — the `USR` handling code is in the calculator at operation byte `#36`, with the entry sequence documented in chapter 8 of the disassembly
- **World of Spectrum — ZX BASIC Manual Chapter 26**: https://worldofspectrum.org/ZXBasicManual/zxmanchap26.html
- **Sinclair User Issue 45 — Machine Code column**: https://sinclairuser.com/045/mcode.htm — typical magazine tutorial on POKE-driven machine code installation
- **Your Spectrum Issue 03 — Extending BASIC**: http://www.users.globalnet.co.uk/~jg27paw4/yr03/yr03_43.htm — conventions for `USR` return values and parameter passing
