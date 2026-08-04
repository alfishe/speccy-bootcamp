[← Home](../README.md) · [Toolchain](README.md)

# Spectrum BASIC Machine Code Toolkit — The Pre-Assembler Era

Before cross-assemblers like [SjASMPlus](sjasmplus.md) and [Pasmo](pasmo.md) existed, ZX Spectrum programmers wrote machine code **directly from BASIC**. The Spectrum's built-in Sinclair BASIC provided several mechanisms for entering, running, and debugging machine code without leaving the BASIC environment. This was the standard workflow from 1982 through the early 1990s, when native assemblers like [ALASM](alasm_sts.md) and XAS replaced it.

This article covers the **machine code entry toolkit that ships with every ZX Spectrum**: `POKE`, `PEEK`, `USR`, `RANDOMIZE USR`, the `CODE` function, byte arrays, and the various tricks Spectrum programmers used to bootstrap machine code before loading a real assembler.

> [!NOTE]
> This article is **not** about a single tool. It documents the **built-in BASIC facilities** every Spectrum has. For third-party assemblers that run on the Spectrum itself, see [native_toolchain.md](native_toolchain.md). For modern cross-development, see [cross_platform_toolchain.md](cross_platform_toolchain.md).

---

## Quick Start

The simplest machine code program is a single-byte routine that returns to BASIC. Here is the **canonical "Hello, World"** of Spectrum machine code, entered entirely from BASIC:

```basic
10 REM The bytes 201,195,175 are "RET" then "JP (HL)" then junk
20 FOR n=30000 TO 30000
30 READ d: POKE n,d
40 NEXT n
50 DATA 201
60 RANDOMIZE USR 30000
```

Line 60 calls the address 30000 (`#7530`) as a subroutine. The byte `201` at that address is the Z80 opcode `RET`, which immediately returns control to BASIC. The `RANDOMIZE USR` mechanism is how every Spectrum program invokes machine code.

A more useful example — a routine that prints a character:

```basic
10 FOR n=30000 TO 30010
20 READ d: POKE n,d
30 NEXT n
40 DATA 62,72,211,254,201
50 REM 62,72      = LD A,72        (ASCII 'H')
60 REM 211,254    = OUT (#FE),A    (border color change)
70 REM 201        = RET
80 RANDOMIZE USR 30000
```

Running this sets the border color based on the value in A (72 = `#48`, which gives a yellow border because bits 0-2 are `%001` = blue + green = cyan — actually the border color comes from the low 3 bits, which are `%000` for 72 decimal, so it is black; see [color_system](../05_development/05_display_and_timing/color_system.md) for the color encoding).

---

## Historical Context

The ZX Spectrum shipped in 1982 with **no assembler in ROM**. The ROM contains a BASIC interpreter, a simple editor, and the character set — nothing else. Unlike the Commodore 64 (which had a built-in monitor) or the BBC Micro (which had a built-in assembler), the Spectrum programmer who wanted to write machine code had three choices:

1. **Hand-assemble** — write the bytes by hand from a Z80 reference card, using `POKE` to place them in RAM
2. **Type in a third-party assembler** — magazines like *Your Sinclair* and *ZX Computing* published assembler listings you typed in by hand
3. **Buy a commercial assembler** — Zeus, DEVPAK, Mons, ALASM (see [native_toolchain.md](native_toolchain.md))

Option 1 — hand-assembly from BASIC — was the most common path for beginners. It is painful but educational: you learn the Z80 instruction set byte by byte, and you learn exactly how memory works. Many veteran Spectrum programmers credit this process with their deep understanding of the machine.

The BASIC toolkit was so central to early Spectrum programming that **magazine type-in programs** used it routinely. Issues of *Your Sinclair*, *CRASH*, and *Sinclair User* published machine code listings as columns of decimal numbers, with a small BASIC loader program that `POKE`d the bytes into RAM.

---

## The Core BASIC Toolkit

### `POKE address, value` — Write a Byte

`POKE` writes a single byte (0-255) to an absolute memory address. It is the fundamental tool for placing machine code in RAM.

```basic
POKE 30000, 201
```

Writes the byte `201` (Z80 `RET`) to address 30000.

### `PEEK(address)` — Read a Byte

`PEEK` reads a single byte from an absolute memory address. It is used for verifying that `POKE` worked correctly, and for inspecting memory during debugging.

```basic
PRINT PEEK(30000)
```

Prints the byte at address 30000 (should be 201 if the previous `POKE` succeeded).

### `RANDOMIZE USR address` — Call Machine Code

`RANDOMIZE USR address` is the standard way to call a machine code routine from BASIC. It:

1. Sets the seed for the `RND` function to the **return value** of the machine code routine
2. Calls the routine at `address` as a subroutine
3. The routine must end with `RET` (Z80 opcode `201`) to return to BASIC

The `RANDOMIZE` part is a quirk of Sinclair BASIC. The `USR` function returns the value of the BC register pair when the routine returns. `RANDOMIZE` consumes this value as a seed. The trick is widely used but has a side effect: it resets the random number generator seed, which may be unwanted if your program uses `RND`.

### `PRINT USR address` — Call and Print Result

An alternative to `RANDOMIZE USR` that prints the return value (the BC register pair) instead of consuming it as a seed:

```basic
PRINT USR 30000
```

This calls the routine at 30000 and prints the value of BC when the routine returns.

### `LET x = USR address` — Capture Return Value

```basic
LET result = USR 30000
```

Stores the BC return value in a variable for later use.

### Which to Use?

- **`RANDOMIZE USR addr`** — most common, when the return value does not matter
- **`PRINT USR addr`** — when you want to see the return value
- **`LET x = USR addr`** — when you need the return value in a calculation

---

## Loading Bytes from `DATA` Statements

Hand-assembling a long program as a sequence of `POKE` statements is painful. The standard pattern uses `READ` and `DATA` to load a block of bytes:

```basic
10 REM Load machine code at address 30000
20 LET addr = 30000
30 FOR n = 0 TO 19
40 READ byte: POKE addr + n, byte
50 NEXT n
60 DATA 62,72,211,254,201,33,44,117,14,32
70 DATA 62,42,18,35,32,249,201,0,0,0
80 REM Now call it
90 RANDOMIZE USR 30000
```

This pattern is so common that virtually every magazine type-in program in the 1980s used it.

### Verifying the Load

After loading, you can dump memory with `PEEK` to verify:

```basic
100 FOR n = 30000 TO 30019
110 PRINT PEEK(n); " ";
120 NEXT n
```

This prints the bytes you loaded, allowing visual verification against the source.

---

## Byte Arrays as Code Storage

A more structured approach uses byte arrays to hold machine code. Sinclair BASIC supports `DIM` arrays of bytes:

```basic
10 DIM m(20) AS BYTE: REM requires 128K BASIC; on 48K use numeric arrays
```

On the 48K Spectrum, you use a numeric array (which stores each element as a 5-byte floating-point number) and `POKE` from it:

```basic
10 DIM m(20)
20 FOR n = 1 TO 20
30 READ m(n)
40 NEXT n
50 DATA 62,72,211,254,201,33,44,117,14,32
60 DATA 62,42,18,35,32,249,201,0,0,0
70 REM Copy to address 30000
80 FOR n = 1 TO 20
90 POKE 29999 + n, m(n)
100 NEXT n
110 RANDOMIZE USR 30000
```

This separates the data (in `m`) from the placement (at address 30000), which is useful if you want to move the code to a different address later.

### The `CODE` Function

The `CODE` function returns the ASCII value of the first character of a string. This lets you encode bytes as characters:

```basic
10 LET s$ = "Hello"
20 PRINT CODE(s$)
```

Prints `72` (ASCII for `H`).

This is useful for embedding small byte tables in strings:

```basic
10 LET code$ = CHR$ 62 + CHR$ 72 + CHR$ 211 + CHR$ 254 + CHR$ 201
20 REM code$ now contains the 5 bytes of our routine
30 FOR n = 1 TO LEN code$
40 POKE 29999 + n, CODE(code$(n))
50 NEXT n
60 RANDOMIZE USR 30000
```

This is more compact than `DATA` statements for small routines, but fails for bytes that conflict with BASIC string handling (notably byte 34, which is `"` and breaks string parsing).

---

## REM-Based Loaders (The Stack Trick)

One of the most famous Spectrum tricks is the **REM-based loader**. This exploits the fact that REM statements can contain arbitrary bytes:

```basic
10 REM ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

After typing this, you can `POKE` bytes into the body of the REM line. The bytes are stored in memory along with the rest of the program, but BASIC ignores them when running (it just skips the line).

### Finding the Address of a REM Line

The address of a line in memory is found via the system variable `PROG` (`#5C53`), which points to the start of the BASIC program. Each line has a 4-byte header (2 bytes for the line number, 2 bytes for the length of the line body). To find the address of line 10's REM body:

```basic
10 REM abc
20 LET addr = PEEK 23635 + 256 * PEEK 23636
30 REM addr is now PROG, pointing at line 10's header
40 LET addr = addr + 4
50 REM addr now points at line 10's first character (the 'a' of 'abc')
60 PRINT PEEK(addr), PEEK(addr + 1), PEEK(addr + 2)
```

This prints the ASCII values of `a`, `b`, `c`.

### Placing Machine Code in a REM Line

Once you know the address, you can `POKE` bytes there:

```basic
10 REM xxxxxxxxxxxxxxxxxxxx
20 LET base = PEEK 23635 + 256 * PEEK 23636 + 4
30 FOR n = 0 TO 19
40 READ byte: POKE base + n, byte
50 NEXT n
60 DATA 62,72,211,254,201,33,44,117,14,32
70 DATA 62,42,18,35,32,249,201,0,0,0
80 RANDOMIZE USR base
```

**Important caveat**: when BASIC tries to display or edit the REM line, the embedded bytes may confuse the editor. Characters corresponding to control codes (0-31) will display as ink/paper controls, which corrupts the screen. Bytes corresponding to keywords (like 195, which is `PRINT`) will display as their keyword. The REM line becomes "garbage" visually, but the bytes are intact in memory.

This trick was used by many magazine type-in programs to keep the loader short — instead of `DATA` statements with 1000 numbers, the bytes were embedded directly in a REM line and the loader just `POKE`d a small bootstrap loader to copy them to the run address.

---

## Stack-Based Loaders (The Loader Trick)

A more advanced trick uses the **return stack** to bootstrap machine code. The idea:

1. `POKE` the bytes of the routine into a region of RAM
2. Set the stack pointer to point just below the routine
3. Execute `RET` — the CPU pops the first byte of the routine as the return address

This trick is rarely used because it is fragile (any interrupt during execution corrupts the stack), but it appears in some early self-loading machine code demos.

---

## Debugging from BASIC

### Inspecting Memory

The most basic debug tool is a memory dump loop:

```basic
10 INPUT "Address: "; a
20 FOR n = 0 TO 63
30 PRINT PEEK(a + n); " ";
40 NEXT n
```

This dumps 64 bytes starting at the address you enter.

### Inspecting Registers

Sinclair BASIC's `USR` function returns BC. To inspect other registers, your routine must copy them into BC before returning:

```z80
        ; Routine that returns HL in BC (and hence to USR's return value)
        ld   b, h
        ld   c, l
        ret
```

The full register state is harder to inspect. The Spectrum's system variables at `#5C00`-`#5CB6` contain some saved register values during certain BASIC operations, but a full register dump requires a monitor program (see [native_toolchain.md](native_toolchain.md)).

### Single-Stepping

Sinclair BASIC has no single-step facility. To single-step machine code, you need a third-party monitor like **STS** (see [alasm_sts.md](alasm_sts.md)) or a hardware add-on.

---

## When to Encounter This Today

You will encounter BASIC-based machine code entry in:

### 1. Historical Source Code

Most 1980s magazine type-in programs and many commercial games of the era shipped as BASIC loaders. If you are studying these programs, you will see the `POKE` + `DATA` pattern repeatedly.

### 2. Snapshot and Tape File Headers

The header of a `.tap` file (the standard Spectrum tape format) is itself a block of bytes laid out in a specific structure. Understanding how BASIC and the ROM handle these headers helps when [reverse-engineering](../08_reverse_engineering/methodology.md) tape loaders.

### 3. Tape Loading Tricks (Speedload)

Many commercial games used custom tape loaders that bypassed the ROM's slow `LOAD`/`SAVE` routines. These loaders were machine code programs, but they had to be **loaded by the ROM first** before taking over. The standard pattern:

1. ROM loads a small BASIC program
2. BASIC `POKE`s a short machine code loader into RAM
3. BASIC calls the loader via `RANDOMIZE USR`
4. The loader takes over and loads the rest of the program at high speed

Understanding this pattern is essential for [tape loader analysis](../08_reverse_engineering/methodology.md).

### 4. Educational Exercises

Hand-assembling small routines is still an excellent way to learn the Z80. Modern cross-assemblers do all the work for you, but the act of looking up opcodes and encoding instructions by hand builds deep understanding.

---

## Common Pitfalls

1. **Byte values are decimal** — `POKE` and `DATA` use decimal bytes (0-255), not hex. Use a calculator or hex-to-decimal conversion when transcribing from assembly listings.

2. **Address ranges conflict with BASIC** — if you `POKE` into the BASIC program area (`#5C53` to `#FF57`), you corrupt your program. Use a "safe" area like `30000`-`#7FFF` for short routines. The RAM-top system variable (`RAMTOP`, `#5CB2`) tells you the highest address BASIC considers safe.

3. **`RANDOMIZE` resets the random seed** — using `RANDOMIZE USR addr` resets `RND`'s seed. If your program uses random numbers after the machine code call, you may see biased results. Use `PRINT USR addr` or `LET x = USR addr` instead.

4. **Byte 34 (`"`)** breaks REM and string-based loaders — the double quote character terminates strings in BASIC. Use `DATA` statements instead of REM-line tricks if your code contains byte 34.

5. **Interrupts can interfere** — if your routine takes more than a frame (about 1/50 second), the interrupt fires and may corrupt your routine. Disable interrupts with `DI` (byte 243) at the start of your routine and re-enable with `EI` (byte 251) before `RET` if needed.

6. **Stack location matters** — the Z80 stack lives at the top of free RAM by default. If your routine uses `CALL` or `PUSH`, make sure you have stack space. The stack pointer at routine entry is in BASIC's workspace.

7. **No assembler = no symbolic labels** — every address must be a literal number. Forward references (jumping to a label that you have not yet placed) require manual calculation.

---

## Comparison to Other Approaches

| Approach | Effort | Speed of writing | Educational value |
|---|---|---|---|
| Hand-assemble + POKE | High | Very slow | Maximum |
| Magazine type-in loader | Medium | Slow | High |
| Native assembler (ALASM, Zeus) | Medium | Fast | Medium |
| Cross-assembler (SjASMPlus) | Low | Very fast | Low (assembler does the work) |

For modern development, there is **no reason** to use the BASIC toolkit beyond education. Use [SjASMPlus](sjasmplus.md), [Pasmo](pasmo.md), or any other cross-assembler.

---

## FAQ

**Q: Why is it `RANDOMIZE USR` and not just `USR`?**

A: Sinclair BASIC's `USR` is a *function* that returns a value (BC). It cannot be used as a statement on its own — you must consume the return value somehow. `RANDOMIZE` accepts the return value as a seed (and discards the result). `PRINT` prints it. `LET` stores it. Any of these works.

**Q: What is the difference between `USR` and `USR$`?**

A: `USR address` is for numeric routines (returns BC). `USR$ address` is for string routines (returns a string pointed to by HL). `USR$` is rarely used.

**Q: Can I use `POKE` to modify BASIC program lines?**

A: Yes. The system variable `PROG` (`#5C53`) points to the start of the BASIC program in memory. You can `POKE` to change line numbers, edit line content, or even create new lines. This is dangerous — corrupting the line linkage bytes will crash BASIC.

**Q: How do I find the address of a specific BASIC line?**

A: Walk the line chain starting from `PROG`. Each line is stored as: 2 bytes line number, 2 bytes line length, then the line body. Add (line length + 4) to skip to the next line. Stop when you reach line number `#8000` (32768), which marks end-of-program.

**Q: Did professional programmers hand-assemble from BASIC?**

A: Rarely. Most professionals used commercial assemblers (Zeus, DEVPAK) or wrote their own. Hand-assembly was the path for hobbyists, magazine readers, and people learning the machine.

---

## Cross-References

- [native_toolchain.md](native_toolchain.md) — survey of native Spectrum assemblers
- [alasm_sts.md](alasm_sts.md) — STS monitor-debugger (essential companion for serious work)
- [zeus_assembler.md](zeus_assembler.md) — the canonical native assembler
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — modern cross-assemblers
- [sjasmplus.md](sjasmplus.md) — modern recommended cross-assembler
- [pasmo.md](pasmo.md) — minimalist modern alternative
- [../08_reverse_engineering/methodology.md](../08_reverse_engineering/methodology.md) — RE methodology and tape loader analysis
- [../05_development/05_display_and_timing/color_system.md](../05_development/05_display_and_timing/color_system.md) — border color encoding

---

## References

- Vickers Melson — *[ZX Spectrum BASIC Programming Manual](https://www.worldofspectrum.org/hardware.html)*, Sinclair Research, 1982
- *[Your Sinclair](https://archive.org/details/yoursinclair-magazine)*, *CRASH*, *Sinclair User* — magazine type-in program archives
- Steven Vickers — *Sinclair ZX Spectrum ROM Disassembly*, 1982-1983 (multiple revisions)
- Logan Dr — *The [Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip)*, Melbourne House, 1983
- WoS ([World of Spectrum](https://worldofspectrum.org/)) archive — machine code tutorials and historical BASIC programs
