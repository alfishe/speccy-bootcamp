[← Home](../README.md) · [Operating Systems](README.md)

# 48K ROM — The Sinclair BASIC Operating System

The 16,384 bytes at `#0000`–`#3FFF` contain the ZX Spectrum's entire operating system. There is no separate DOS, no device driver layer, no kernel. The ROM *is* the BASIC interpreter, the line editor, the cassette tape handler, the floating-point calculator, and the I/O subsystem — all in 16K. Every Sinclair Spectrum ever made boots into this code.

The ROM was designed by Richard Altwasser (hardware) and Steve Vickers (software) at Sinclair Research in 1982. It is a direct descendant of the ZX81 ROM (by the same author), sharing much of its architecture — the channel/stream I/O model, the calculator stack, and the line-entry editor — but substantially expanded to support colour, sound, high-resolution graphics, and a more usable keyboard.

This article covers the 48K ROM as a system: its memory layout, the major subsystems, entry points useful to machine code programmers, and the design decisions that shaped it. For the per-variable workspace reference, see [system_variables.md](system_variables.md). For the 128K ROM extensions, see [rom_128k.md](rom_128k.md).

---

## ROM Map

The ROM is not a monolithic blob — it has a clear internal structure. The table below shows the major functional regions. Address ranges are approximate; some routines bleed across boundaries.

| Address range | Subsystem | Description |
|---------------|-----------|-------------|
| `#0000`–`#0008` | RST vectors | `RST #08` (error handler) and the first few bytes of `RST #10` (print character) |
| `#0010`–`#0027` | RST vectors | `RST #10` (print a character), `RST #18` (collect a character), `RST #20` (collect next character) |
| `#0028` | Calculator entry | `RST #28` — entry to the floating-point calculator |
| `#0030` | Make spaces | `RST #30` — create workspace in RAM |
| `#0038`–`#003F` | Interrupt handler | IM1 maskable interrupt routine: increments FRAMES, scans keyboard |
| `#0066`–`#0073` | NMI handler | Non-maskable interrupt: resets to `(JPN #1F05)` — warm restart |
| `#0074`–`#008F` | Error handling | Error report generation, stack recovery |
| `#0090`–`#0232` | Keyboard | Key scanning, key decoding, INKEY$ handler |
| `#0233`–`#0249` | Beeper | `BEEPER` routine — single-tone sound via ULA |
| `#024A`–`#03B5` | Tape I/O | SAVE, LOAD, VERIFY — cassette tape read/write with leader/parity |
| `#03B6`–`#04C2` | Print output | Character printing to screen channels, line wrapping |
| `#04C3`–`#0639` | Character set access | Read pixel data for a character, handle tokens |
| `#063A`–`#08FF` | Screen handling | CLS, scroll, attribute handling, plot/draw/circle support |
| `#0900`–`#0970` | Input handling | INPUT command processing |
| `#0971`–`#0CB2` | Tape data format | Block headers, data encoding, tape verify |
| `#0CB3`–`#1097` | Tape control | Motor control, tone generation for tape output |
| `#1098`–`#15DE` | Calculator | Floating-point arithmetic engine — add, subtract, multiply, divide, trig, log, and ~40 stack operations |
| `#15DF`–`#1A9B` | Tape LOAD/SAVE | High-level tape operations called from BASIC |
| `#1A9C`–`#1D9B` | Character set | 96 characters × 8 bytes = 768 bytes of pixel patterns |
| `#1D9C`–`#24FB` | BASIC interpreter | Tokeniser, line parser, expression evaluator, statement executor |
| `#24FC`–`#38FF` | BASIC runtime | Editor loop, LIST, channel/stream management, expression evaluation |
| `#3900`–`#3FFF` | BASIC commands | PRINT, INPUT, PLOT, DRAW, CIRCLE, BEEP, and remaining command implementations |

> [!TIP]
> This map is a guide, not a fence. Many routines call into other regions, and some address ranges contain utility functions used by multiple subsystems. For a detailed routine-by-routine breakdown, see *The Complete Spectrum ROM Disassembly* by Dr. Ian Logan and Dr. Frank O'Hara (Melbourne House, 1983).

---

## ROM Initialisation Sequence

When power is applied, the Z80 starts executing at address `#0000`. The ROM's first task is to bring the system from a completely unknown state to a ready-to-use BASIC environment. This process takes less than a second and proceeds through a well-defined sequence.

### Cold Start (`#0000`)

The entry point at `#0000` performs a **cold start**:

1. **Disable interrupts** (`DI`) and set the stack pointer to `#3C00` (a temporary location in ROM — the stack will move to RAM once system variables are initialised).
2. **Clear RAM** — fill the entire RAM with zeros. This is also the RAM size detection: the ROM writes to progressively higher addresses and reads back; the last address that echoes correctly determines `P_RAMT` (`#5CB4`). On a 16K machine this will be `#7FFF`; on a 48K machine, `#FFFF`.
3. **Initialise system variables** — set all 182 bytes at `#5C00`–`#5CB5` to their default values. Key defaults include `ERR_NR` = `#FF` (no error), `FLAGS` = `#F7`, and all pointer values.
4. **Set up the memory layout** — the key pointers are initialised to establish the workspace chain:

```
CHANS  → #5CB6   Channel records (K, S, P, R) — 23 bytes
         Streams 0–15 — 30 bytes
         Calculator memory (MEMBOT) — 30 bytes
PROG   → #5D56   Start of BASIC program area
VARS   → #5D56   (empty — same as PROG, no variables yet)
E_LINE → #5D56   (empty edit line)
WORKSP → #5D56   STKBOT → #5D56
UDG    → #FF58   User-defined graphics area
RAMTOP → #FF58   Top of BASIC system area
```

5. **Open channels and streams** — create the four channel records (K, S, P, R) and assign streams 0–3 to their default channels.
6. **Set up interrupt mode** — configure IM1 and enable interrupts (`IM 1; EI`). The FRAMES counter begins incrementing immediately.
7. **Display the copyright message** — print `"(c) 1982 Sinclair Research Ltd"` at the top of the screen.
8. **Enter the editor loop** — jump to the main execution loop at `MAIN_EXEC` (`#12A2`), which waits for user input.

The BASIC program area starts empty. The very first thing the user types becomes the first line in the program or is executed as a direct command.

### Warm Start (`#1F05`)

The NMI handler and several error recovery paths jump to `TEST_ROOM`/warm start at `#1F05`. This reinitialises the interpreter state **without** clearing the BASIC program:

1. Reclaim workspace (edit line, calculator stack)
2. Reset `CH_ADD`, `X_PTR`, and other cursor pointers
3. Set `ERR_NR` to `#FF` (no error)
4. Re-enter the editor loop

The `NEW` command at `#11B7` is the nuclear option — it performs the equivalent of a warm start but also **clears the entire BASIC program and all variables**, resetting `PROG` and `VARS` to their initial positions.

> [!NOTE]
> The initial RAM-clear loop is the reason a Spectrum takes a noticeable fraction of a second to "boot" — it writes zero to every single RAM address from `#5C00` to `#FFFF` (up to 41 KB of writes on a 48K machine). This is also how the machine detects its own RAM size without any hardware configuration register.

---

## RST Vectors — The ROM's Callable API

The Z80 has eight restart vectors (`RST #00` through `RST #38`), each jumping to a fixed address in a single byte. The ROM uses six of these as its public API — the primary interface between user machine code and ROM facilities:

| Vector | Address | Name | Purpose |
|--------|---------|------|----------|
| `RST #08` | `#0008` | `ERROR-1` | Report an error. A = error number. Does not return — long-jumps to the error handler via `ERR_SP` |
| `RST #10` | `#0010` | `PRINT-A` | Print the character in A to the current stream. Handles tokens, control codes, and newline |
| `RST #18` | `#0018` | `GET-CHAR` | Read the current character from the BASIC edit line into A. Uses `CH_ADD` pointer |
| `RST #20` | `#0020` | `NEXT-CHAR` | Advance `CH_ADD` and read the next character. Skips whitespace |
| `RST #28` | `#0028` | `FP-CALC` | Enter the floating-point calculator. The byte following the `RST #28` is a calculator instruction; execution continues with subsequent bytes until `+ENDCALC` (`#38`) |
| `RST #30` | `#0030` | `BC-SPACES` | Make BC bytes of workspace in RAM. HL returns the address of the new space |

### Using RST #10 to Print

The simplest and most commonly used ROM call:

```z80
; Print "HELLO" using ROM character output
    LD   A,'H'
    RST  #10
    LD   A,'E'
    RST  #10
    LD   A,'L'
    RST  #10
    LD   A,'L'
    RST  #10
    LD   A,'O'
    RST  #10
```

`RST #10` outputs to whatever stream is currently selected (stream 2 = screen by default). It handles newlines (A = `#0D`), token expansion (A >= `#A5` prints the corresponding BASIC keyword), and attribute handling.

### Using RST #28 for Floating-Point Math

The calculator is a stack-based floating-point engine. You push operands onto the calculator stack (5 bytes each, at `STKBOT`) and then invoke operations:

```z80
; Compute 2.0 + 3.0 using the ROM calculator
; Result ends up in the calculator stack
    RST  #28            ; Enter calculator
    DB   #34,#02        ; stack-2 (push 2.0 — uses a lookup table)
    DB   #34,#03        ; stack-3 (push 3.0)
    DB   #0F            ; addition
    DB   #38            ; end-calc
    ; Result (5.0) is now on the calculator stack
```

The calculator has ~40 operations: `+`, `-`, `×`, `÷`, `sin`, `cos`, `tan`, `ln`, `exp`, `√`, `abs`, `int`, and more. See *ZX Spectrum ROM Code Disassembly* by Toni Baker (Sunshine Books, 1983) for a complete operation reference.

> [!WARNING]
> `RST #28` destroys `AF`, `BC`, `DE`, `HL`. The calculator uses the system's own workspace — do not call it if you've modified `STKBOT` or `STKEND`.

### Calculator Instruction Set

The floating-point calculator entered via `RST #28` is a **bytecode virtual machine** embedded in the ROM. After the `RST #28` instruction, the bytes that follow are not Z80 opcodes — they are **calculator literals** that the calculator fetches and executes one by one. The literal `#38` (`+ENDCALC`) terminates the sequence and returns control to the Z80.

The calculator maintains its own **stack** (separate from the Z80 stack) for 5-byte floating-point values. Operations consume operands from the top of this stack and push results back.

#### Arithmetic and Comparison Operations

| Offset | Literal | Mnemonic | Stack effect | Description |
|--------|---------|----------|-------------|------------|
| `+00` | `#00` | `jump_true` | v, l → v | Conditional branch: if v ≠ 0, advance literal pointer by l |
| `+01` | `#01` | `exchange` | a, b → b, a | Swap top two stack values |
| `+02` | `#02` | `delete` | a, b → a | Remove the top value (second value becomes new top) |
| `+03` | `#03` | `subtract` | a, b → (a−b) | Subtract top from second |
| `+04` | `#04` | `multiply` | a, b → (a×b) | Multiply top two values |
| `+05` | `#05` | `division` | a, b → (a÷b) | Divide second by top |
| `+06` | `#06` | `to_power` | a, b → (a^b) | Exponentiation |
| `+07` | `#07` | `or` | a, b → (a OR b) | Logical OR |
| `+08` | `#08` | `no_and_no` | a, b → (a AND b) | Logical AND |
| `+09` | `#09` | `n≤m` | a, b → (a≤b) | Numeric comparison: ≤ |
| `+0A` | `#0A` | `n≥m` | a, b → (a≥b) | Numeric comparison: ≥ |
| `+0B` | `#0B` | `n<>m` | a, b → (a<>b) | Numeric comparison: ≠ |
| `+0C` | `#0C` | `n>m` | a, b → (a>b) | Numeric comparison: > |
| `+0D` | `#0D` | `n<m` | a, b → (a<b) | Numeric comparison: < |
| `+0E` | `#0E` | `n=m` | a, b → (a=b) | Numeric comparison: = |
| `+0F` | `#0F` | `addition` | a, b → (a+b) | Add top two values |

#### String Operations

| Offset | Literal | Mnemonic | Stack effect | Description |
|--------|---------|----------|-------------|------------|
| `+10` | `#10` | `str_to_no` | s → n | Convert string to number (VAL$ equivalent) |
| `+11` | `#11` | `s≤t` | a, b → (a≤b) | String comparison: ≤ |
| `+12` | `#12` | `s≥t` | a, b → (a≥b) | String comparison: ≥ |
| `+13` | `#13` | `s<>t` | a, b → (a<>b) | String comparison: ≠ |
| `+14` | `#14` | `s>t` | a, b → (a>b) | String comparison: > |
| `+15` | `#15` | `s<t` | a, b → (a<b) | String comparison: < |
| `+16` | `#16` | `s=t` | a, b → (a=b) | String comparison: = |
| `+17` | `#17` | `strs_add` | a, b → (a+b) | String concatenation |

#### Mathematical Functions

| Offset | Literal | Mnemonic | Stack effect | Description |
|--------|---------|----------|-------------|------------|
| `+18` | `#18` | `val$` | s → n | Evaluate string as BASIC expression |
| `+19` | `#19` | `usr_str` | s → n | USR with string argument (call machine code at address) |
| `+1A` | `#1A` | `read_in` | — → n | Read a byte from the calculator's literal stream |
| `+1B` | `#1B` | `negate` | v → (−v) | Negate top value |
| `+1C` | `#1C` | `code` | s → n | ASCII code of first character of string |
| `+1D` | `#1D` | `val` | s → n | Convert string to number (VAL equivalent) |
| `+1E` | `#1E` | `len` | s → n | Length of string |
| `+1F` | `#1F` | `sin` | v → sin(v) | Sine (v in radians) |
| `+20` | `#20` | `cos` | v → cos(v) | Cosine (v in radians) |
| `+21` | `#21` | `tan` | v → tan(v) | Tangent (v in radians) |
| `+22` | `#22` | `asn` | v → arcsin(v) | Arc sine |
| `+23` | `#23` | `acs` | v → arccos(v) | Arc cosine |
| `+24` | `#24` | `atn` | v → arctan(v) | Arc tangent |
| `+25` | `#25` | `ln` | v → ln(v) | Natural logarithm |
| `+26` | `#26` | `exp` | v → e^v | Exponential |
| `+27` | `#27` | `int` | v → ⌊v⌋ | Integer part (floor) |
| `+28` | `#28` | `sqr` | v → √v | Square root |
| `+29` | `#29` | `sgn` | v → sgn(v) | Signum (−1, 0, or +1) |
| `+2A` | `#2A` | `abs` | v → |v| | Absolute value |
| `+2B` | `#2B` | `peek` | v → n | PEEK: read byte at address v |
| `+2C` | `#2C` | `in` | v → n | IN: read port v |
| `+2D` | `#2D` | `usr_no` | v → n | USR with numeric argument |
| `+2E` | `#2E` | `str$` | n → s | Convert number to string |
| `+2F` | `#2F` | `chr$` | n → s | Character with code n |

#### Stack Manipulation and Control

| Offset | Literal | Mnemonic | Stack effect | Description |
|--------|---------|----------|-------------|------------|
| `+30` | `#30` | `not` | v → NOT v | Logical NOT (1 if v=0, 0 otherwise) |
| `+31` | `#31` | `duplicate` | v → v, v | Duplicate the top value |
| `+32` | `#32` | `n_mod_m` | n, m → (n mod m) | Modulo — used by `DRAW` for clipping |
| `+33` | `#33` | `jump` | — → — | Unconditional jump — advance literal pointer by next byte |
| `+34` | `#34` | `stk_data` | — → v | Push a constant (next 5 bytes are a FP number, or 6 bytes for a special form) |
| `+35` | `#35` | `dec_jr_nz` | — → — | Decrement `BREG` and jump back if non-zero (loop construct) |
| `+36` | `#36` | `less_0` | v → (v<0) | Test: 1 if negative, 0 otherwise |
| `+37` | `#37` | `greater_0` | v → (v>0) | Test: 1 if positive, 0 otherwise |
| `+38` | `#38` | `end_calc` | — | Terminate the calculator and return to Z80 code |

#### Internal Operations

| Offset | Literal | Mnemonic | Description |
|--------|---------|----------|------------|
| `+39` | `#39` | `get_argt` | Get arctangent approximation |
| `+3A` | `#3A` | `truncate` | Truncate to integer (toward zero) |
| `+3B` | `#3B` | `fp_calc_2` | Execute single operation whose offset is in `BREG` |
| `+3C` | `#3C` | `e_to_fp` | Convert ASCII digits at `CH_ADD` to FP (used by number parser) |
| `+3D` | `#3D` | `re_stack` | Restack a value (ensure correct format) |

#### Multi-Purpose Operations

These four operations take a **parameter** encoded in the low 5 bits of the literal byte. The upper bits determine the operation base:

| Base offset | Parameter range | Operations | Description |
|------------|----------------|------------|------------|
| `+3E` (`#80`–`#BF`) | `#06`, `#08`, `#0C` | `series-06`, `series-08`, `series-0C` | Polynomial approximation (Chebyshev) — used internally for sin, cos, tan, ln, exp, etc. |
| `+3F` (`#A0`–`#BF`) | `#00`–`#04` | `stk-zero`, `stk-one`, `stk-half`, `stk-pi/2`, `stk-ten` | Push common constants: 0, 1, 0.5, π/2, 10 |
| `+40` (`#C0`–`#DF`) | `#00`–`#05` | `st-mem-0` … `st-mem-5` | Store top of calculator stack into memory cell 0–5 |
| `+41` (`#E0`–`#FF`) | `#00`–`#05` | `get-mem-0` … `get-mem-5` | Push value from memory cell 0–5 onto calculator stack |

The six memory cells (`MEM_0` through `MEM_5`) reside in the calculator's memory area (`MEMBOT`, 30 bytes at `#5C68`). They persist between calculator invocations and are used for intermediate storage during complex calculations.

#### Practical Examples

**Compute sin(π/6) — i.e., sin(30°):**

```z80
; sin(PI/6) = 0.5
; PI/6 = PI/2 / 3, so push PI/2, push 3.0, divide, then sin
    RST  #28
    DB   #3F,#03         ; stk-pi/2 (push 1.5708)
    DB   #34             ; stk_data
    DB   #82,#40,#00,#00,#00  ; 3.0
    DB   #05             ; division → 0.5236 (PI/6 in radians)
    DB   #1F             ; sin → 0.5
    DB   #38             ; end-calc
```

**Check if a number is an integer:**

```z80
; Push 10.0 and check if integer
    RST  #28
    DB   #3F,#04         ; stk-ten (push 10.0)
    DB   #31             ; duplicate (10.0, 10.0)
    DB   #27             ; int → (10.0, 10.0)
    DB   #03             ; subtract → (0.0)
    DB   #37             ; greater_0 → 0 (not > 0, so it IS integer)
    DB   #38             ; end-calc
```

**Memory cell operations:**

```z80
; Store to and retrieve from memory cell 3
    RST  #28
    DB   #34             ; stk_data
    DB   #81,#00,#00,#00,#00  ; 1.0
    DB   #40,#03         ; st-mem-3 (store 1.0 into cell 3)
    DB   #41,#03         ; get-mem-3 (push cell 3's value back)
    DB   #38             ; end-calc
    ; Top of calculator stack is now 1.0
```

For a complete treatment of the calculator with worked examples of every operation, see Toni Baker's *Machine Code Calculator* series in ZX Computing magazine (reprinted in *Mastering Machine Code on Your ZX Spectrum*, Sunshine Books, 1983).

---

## Key ROM Routines

Beyond the RST vectors, the ROM contains dozens of useful subroutines callable with `CALL`. These are the ones most commonly used by machine code programs. Addresses are exact for the Issue 2 and Issue 3 ROMs (all official 48K Spectrums).

### Character and Screen Output

| Address | Name | Inputs | Outputs | Description |
|---------|------|--------|---------|-------------|
| `#0D4D` | `CHAN-OPEN` | A = stream number | — | Open a stream for I/O. A=0 for keyboard, A=3 for printer |
| `#09F4` | `PRINT-OUT` | A = character | — | Raw character output to current channel |
| `#0D6B` | `TEMPS` | — | — | Set temporary attributes from `ATTR_T` |
| `#0E44` | `CLS` | — | — | Clear the screen and reset attributes |
| `#0DAF` | `CL-LINE` | — | — | Clear the current edit line on screen |
| `#0C0A` | `CL-ADDR` | — | HL = attribute address | Get attribute byte address for current print position |
| `#08D5` | `P-CHAR` | — | — | Plot a character at current coordinates using current attribute |
| `#096B` | `OUT-CURS` | — | — | Output the flashing cursor |

### Keyboard Input

| Address | Name | Inputs | Outputs | Description |
|---------|------|--------|---------|-------------|
| `#028E` | `KEY-SCAN` | — | A, D, E = key data | Scan all 8 half-rows. Does not debounce |
| `#031E` | `KEYBOARD` | — | — | Full keyboard decode: scan, debounce, update `KSTATE`, set `LAST_K` |
| `#10A8` | `WAIT-KEY` | — | A = key code | Wait for a keypress. Uses `KEYBOARD` in a loop |
| `#15D6` | `TEST-KEY` | — | — | Called from BASIC WAIT command |

### Sound

| Address | Name | Inputs | Outputs | Description |
|---------|------|--------|---------|-------------|
| `#03B5` | `BEEPER` | HL = pitch, DE = duration | — | Produce a tone through the ULA beeper. HL = 437500 / freq – 30.125 |
| `#03F8` | `BEEP` | — | — | Full BEEP command handler (called from BASIC, uses calculator) |

### Cassette Tape

| Address | Name | Inputs | Outputs | Description |
|---------|------|--------|---------|-------------|
| `#04C2` | `SAVE-BYTES` | IX = start, DE = length | — | Save a block of bytes to tape |
| `#0562` | `LOAD-BYTES` | IX = destination, DE = length | F = success | Load bytes from tape. Carry flag set on success |
| `#04C6` | `SAVE-HEADER` | — | — | Write a tape header block |
| `#0556` | `VERIFY-HEADER` | — | — | Read and verify a tape header |

### Memory Management

| Address | Name | Inputs | Outputs | Description |
|---------|------|--------|---------|-------------|
| `#1601` | `LOOK-PROG` | — | — | Search BASIC program for a line number |
| `#19B8` | `E-LINE-NO` | — | BC = line number | Extract line number from current edit line |
| `#0D4D` | `CHAN-FLAG` | — | — | Check which channel is active |

> [!IMPORTANT]
> These addresses are valid for the standard 48K ROM (Issues 2 and 3). The 128K ROM 1 is binary-identical. Third-party ROMs (SE-ROM, ProfROM) may relocate routines — always check.

---

## The Channel and Stream System

The ROM implements a device-independent I/O architecture based on **channels** and **streams**. This is one of the ROM's most forward-thinking design decisions — and one that the Sinclair manual barely mentions.

### Channels

A channel represents a hardware device. Each channel record is 5 bytes:

```
Byte 0-1: Address of the output routine
Byte 2-3: Address of the input routine
Byte 4:   Single-letter channel code ('K', 'S', 'P', or 'R')
```

The ROM defines four channels:

| Code | Name | Input routine | Output routine | Purpose |
|------|------|---------------|----------------|---------|
| `K` | Keyboard | Key decode + edit | Print to lower screen | Keyboard input and command line |
| `S` | Screen | — (no input) | Print to upper screen | Display output |
| `P` | Printer | — | Output to ZX Printer | Hardcopy output |
| `R` | Edit buffer | Read from edit buffer | Write to edit buffer | Internal use by BASIC editor |

### Streams

Streams are numbered 0–15. Each stream is associated with a channel. When you `PRINT #3`, data goes to stream 3, which is attached to channel `P` (printer) by default. The standard stream assignments at boot:

| Stream | Channel | Purpose |
|--------|---------|----------|
| 0 | `K` | Keyboard input |
| 1 | `K` | Keyboard input (for commands) |
| 2 | `S` | Screen output (default for `PRINT`) |
| 3 | `P` | Printer output (default for `LPRINT`) |

### Redirecting I/O

Machine code programs can redirect streams to custom channels — this is how Interface 1 adds `M` (microdrive), `N` (network), and `T` (RS-232) channels. You can also create your own channel with custom input/output routines:

```z80
; Redirect screen output to a custom handler
; (useful for capturing text or logging to a buffer)
    ; 1. Modify channel 'S' output routine pointer
    LD   HL,(#5C4F)     ; CHANS pointer
    ; Channel 'K' is first (5 bytes), then 'S' (5 bytes)
    ; 'S' starts at CHANS + 5, output routine at offset 0-1
    INC  HL              ; Skip past 'K' channel
    INC  HL
    INC  HL
    INC  HL
    INC  HL
    ; Now at 'S' channel
    LD   (HL),my_output_routine & #FF
    INC  HL
    LD   (HL),my_output_routine >> 8
    ; Now all PRINT output goes to your routine
```

For a thorough treatment of the channel/stream system, see Chapter 6 of *Understanding Your Sinclair ZX Spectrum 48* by Roger G. Dorsay (Sigma Press, 1984), or the "Channels & Streams" section of the World of Spectrum FAQ.

---

## The BASIC Interpreter

The ROM's largest subsystem (spanning roughly `#1D9C`–`#3FFF`) is the Sinclair BASIC interpreter. It is a tokenised, line-numbered, single-pass interpreter with several noteworthy characteristics.

### Token System

BASIC keywords are stored in memory as **single-byte tokens** (values `#A5`–`#FF`), not as ASCII text. When the user types `PRINT`, the editor stores byte `#F5` in memory. This saves RAM and speeds up parsing — the interpreter never needs to match keyword strings.

The token table at `#009C` maps each token byte to its character representation. Tokens in the range `#A5`–`#C4` are statement keywords (`PRINT`, `IF`, `GOTO`, etc.); `#C5`–`#CD` are function names (`ABS`, `ACS`, `ASN`, etc.); `#CE` and above are operators and modifiers.

### Line Storage Format

BASIC lines are stored in a linked-list structure:

```
Per-line format in memory:
┌──────┬──────┬──────────────┬─────┐
│ 2B   │ 2B   │ variable     │ 1B  │
│ line │ line │ length       │     │
│ num  │ num  │ tokenised    │ #0D │
│ (MSB │ (LSB │ BASIC text   │ CR  │
│ 1st) │      │              │     │
└──────┴──────┴──────────────┴─────┘

Each line:
  Offset 0-1: line number (big-endian: MSB first, LSB second)
  Offset 2-3: length of the rest of the line (offset 2 = MSB, offset 3 = LSB)
  Offset 4+:  tokenised BASIC text
  Last byte:  #0D (carriage return = end of line marker)
```

Lines are linked by the "length" field — to find the next line, add the length to the current line's start address. There is no pointer chain; the interpreter walks forward through memory.

### Variable Storage Format

The variable area starts at the address in `VARS` (`#5C4B`) and extends to `E_LINE` (`#5C59`). Variables are stored sequentially, each prefixed by a **name** that encodes both the variable's identifier and its type.

#### Variable Name Encoding

The first character of the name has its **bit 6** set for numeric variables and clear for string variables. The **last character** of the name has its **bit 5** set. For single-character variable names, both bits are set in the same byte:

| Name stored as | BASIC variable | Type |
|---------------|---------------|------|
| `#60` (bit 6 set, bit 5 set) | `a` | Numeric (single-char) |
| `#20` (bit 6 clear, bit 5 set) | `a$` | String (single-char) |
| `#41,#7C` | `AB` | Numeric (two-char, bit 5 set on B) |
| `#41,#3C` | `AB$` | String (two-char) |

Single-letter numeric variables (like `a`) are the most common and take only 1 name byte. Long names up to the full alphabet are supported — the interpreter scans until it finds a byte with bit 5 set.

#### Numeric Variable

```
Name (1+ bytes, last char has bit 5 set, first has bit 6 set)
5-byte floating-point value
```

Total: 6 bytes for a single-character variable (1 name byte + 5 FP bytes). The 5-byte value is in the standard ROM floating-point format described above.

#### String Variable

```
Name (1+ bytes, last char has bit 5 set, first has bit 6 clear)
2-byte length (LE)
2-byte address of string data (LE)
```

The string data itself lives elsewhere in memory (typically in the string workspace area). The variable entry only stores a pointer and length. String data is moved by the garbage collector when variables are added or deleted.

#### Array Variable

```
Name (1+ bytes)
2-byte total length of array data including dimensions (LE)
For each dimension: 2-byte size (LE)
Data: elements packed sequentially
```

Numeric arrays store 5-byte FP values per element. String arrays store 3-byte descriptors (length + address) per element. Dimension sizes are stored as the total count (not the upper bound). A `DIM a(3,4)` stores dimensions as `#0003`, `#0004`, followed by `3 × 4 = 12` elements.

#### FOR/NEXT Control Variable

When a `FOR` loop is active, its control variable has an extended format:

```
Name (1 byte, bit 6 set, bit 5 set — single-char numeric)
5-byte current value
5-byte limit value
5-byte step value
2-byte referencing line number (LE)
2-byte statement number within line (LE)
2-byte loop pointer — address of the NEXT statement (LE)
```

Total: 22 bytes. When `NEXT` is executed, the interpreter searches the variable area for a control variable with a matching name and bit 7 of the name byte set (marking it as a FOR variable). This is why `FOR i = 1 TO 10` creates a 22-byte variable entry, not 6 bytes.

#### Walking the Variable Area

To enumerate all variables, start at `VARS` and examine each entry:

1. If the first byte is `#80` — this is the end-of-variables marker; stop
2. Determine the name length by scanning until a byte with bit 5 set
3. Determine the data size from the type (numeric = 5 bytes, string = 4 bytes, array = read the 2-byte length field, FOR = 22 bytes − name bytes)
4. Advance past the name + data to reach the next variable

```z80
; Walk all variables and print their names
    LD   HL,(#5C4B)       ; VARS
walk_loop:
    LD   A,(HL)
    CP   #80              ; End marker?
    JR   Z,walk_done
    ; Print first char (clear bits 5,6 for display)
    AND  %10011111        ; Keep bit 7, clear bits 6,5
    CALL print_char
    ; ... advance HL past name and data ...
    ; (depends on variable type — see above)
    JR   walk_loop
walk_done:
```

### Expression Evaluator

The expression evaluator at `#1C8C` handles operator precedence, nested parentheses, string operations, and function calls. It uses a recursive-descent approach with the following precedence (lowest to highest):

1. `OR`
2. `AND`
3. `NOT`
4. Comparisons: `=`, `<`, `>`, `<=`, `>=`, `<>`
5. `+`, `-` (addition, subtraction)
6. `*`, `/` (multiplication, division)
7. `^` (exponentiation)
8. Unary `-`, `+`
9. Functions: `SIN`, `COS`, `LEN`, etc.

The evaluator uses the calculator stack for all arithmetic — even integer operations go through the 5-byte floating-point format. This is why BASIC is slow for game logic but adequate for math-heavy calculations.

### The Floating-Point Format

Numbers in the calculator and in variables use a 5-byte binary format:

```
Byte 0: Exponent (biased by 128)
         #00 = zero (bytes 1-4 are irrelevant)
         #81 = 2^1 = 2.0
         #8E = 2^14 = 16384
Bytes 1-4: Mantissa (32-bit, normalized, MSB implicit)
         The most significant bit is implied (always 1), so byte 1
         stores bits 22-15 of the actual mantissa.

Example: 1.0 = #81 #00 #00 #00 #00
         0.5 = #80 #00 #00 #00 #00
         2.0 = #82 #00 #00 #00 #00
        -1.0 = #81 #00 #00 #00 #80  (bit 7 of byte 4 = sign)
```

Small integers (0–65535) can also be stored in a compact 2-byte form: byte 0 = `#00` (flag), bytes 1-2 = 16-bit integer (little-endian), bytes 3-4 unused. The ROM uses this optimization for line numbers and small constants.

### Command Dispatch Mechanism

When the BASIC interpreter encounters a statement, it must determine which handler to invoke and what operands to expect. This dispatch is driven by two tables in ROM: the **syntax tables** and the **command class table**. Together they form a compact, data-driven parser that handles all 50 BASIC commands.

#### The Statement Loop

The interpreter's main loop at `STMT_LOOP` (`#1B28`) reads the next token from the current BASIC line (via `CH_ADD`), looks it up in the syntax tables, validates its operands according to the command class, and then calls the command's handler routine.

The flow is:

1. Read the token at `CH_ADD` — if it's a statement keyword (`#A5`–`#C4`), proceed
2. Use the token as an index into the **offset table** at `#1A48` (50 entries, one per command)
3. The offset table entry gives a displacement into the **parameter table** starting at `#1A7A`
4. The parameter table contains a sequence of entries: **command class** byte, required **separator** characters, and finally a **handler address** (2 bytes)
5. The command class handler validates/parses the operands
6. Once all operands are processed, the handler address is called

#### Command Classes

The command class table at `#1C01` defines 12 operand classes. Each class describes what kind of data follows the command keyword:

| Class | Handler | Operand type | Example commands |
|-------|---------|-------------|------------------|
| `CLASS_00` | `#1C0D` | No operands | `STOP`, `RETURN`, `CLS`, `COPY`, `NEW`, `CONT` |
| `CLASS_01` | `#1C1F` | A variable (for LET assignment) | `LET` |
| `CLASS_02` | `#1C4E` | An expression (for LET value) | `LET` |
| `CLASS_03` | `#1C0D` | Optional numeric (default 0) | `RUN`, `RANDOMIZE`, `CLEAR`, `RESTORE` |
| `CLASS_04` | `#1C6C` | A single variable name | `FOR`, `NEXT` |
| `CLASS_05` | `#1C0D` | Items list (variable) | `PRINT`, `INPUT`, `LIST`, `DIM`, `DATA`, `READ`, `REM`, `LLIST`, `LPRINT`, `DEF FN` |
| `CLASS_06` | `#1C79` | One numeric expression | `GOTO`, `GOSUB`, `BORDER`, `PAUSE`, `CLOSE #`, `POKE` |
| `CLASS_07` | `#1C96` | Colour item (INK, PAPER, etc.) | `INK`, `PAPER`, `FLASH`, `BRIGHT`, `INVERSE`, `OVER` |
| `CLASS_08` | `#1C79` | Two numeric expressions (comma-separated) | `BEEP`, `PLOT`*, `OUT`, `POKE` |
| `CLASS_09` | `#1CBE` | Colour items + two numerics | `PLOT`, `DRAW`, `CIRCLE` |
| `CLASS_0A` | `#1CDB` | A string expression | `OPEN #`, `FORMAT`, `MOVE`, `ERASE` |
| `CLASS_0B` | `#1CDB` | Cassette I/O handling | `SAVE`, `LOAD`, `VERIFY`, `MERGE` |

#### Walk-Through: `PRINT "HELLO";A`

The token for `PRINT` is `#F5`. The offset table entry for `P_PRINT` points to the parameter table at `#1A9C`, which contains:

- `DEFB $05` — CLASS_05 (items list)
- `DEFW PRINT` — handler address `#1FCD`

The `CLASS_05` handler enters an item-parsing loop. For each item:
1. If the character at `CH_ADD` is `;` — skip it, no newline after this item
2. If `,` — skip it, advance to the next print zone (column 0, 8, 16, ...)
3. If `'` (apostrophe) — skip it, print a newline
4. If `#` — parse stream number, redirect output
5. If `AT` — parse row, column coordinates
6. If `TAB` — parse tab position
7. Otherwise — evaluate the expression (string or numeric) and print the result

The loop continues until it encounters a statement separator (`:`) or end of line (`#0D`). The `PRINT` handler itself at `#1FCD` sets up the output stream, calls the item loop, and appends a final newline if the last item did not end with `;` or `,`.

#### Walk-Through: `FOR i=1 TO 10 STEP 2`

The token for `FOR` is `#AD`. Its parameter table entry at `#1A90` is richer:

- `DEFB $04` — CLASS_04: parse a single variable name (`i`)
- `DEFB "="` — separator: expect a literal `=` character
- `DEFB $06` — CLASS_06: parse one numeric expression (the start value `1`)
- `DEFB $CC` — separator: expect the token `TO` (`#CC`)
- `DEFB $06` — CLASS_06: parse one numeric expression (the limit `10`)
- `DEFB $05` — CLASS_05: optional items (the `STEP` clause)
- `DEFW FOR` — handler address `#1D03`

This shows how a single parameter table entry can encode complex syntax: mandatory separators (`=`, `TO`), required numeric expressions, and optional trailing clauses (`STEP`). If the `STEP` clause is absent, the `FOR` handler defaults to a step of `1`.

> [!TIP]
> The syntax tables are what make Sinclair BASIC relatively easy to extend. The 128K ROM 0 adds new commands by providing its own offset table entries that intercept tokens before they reach the ROM 1 handlers. For a complete listing of all 50 parameter table entries, see Chapter 5 of *The Complete Spectrum ROM Disassembly* by Dr. Ian Logan and Dr. Frank O'Hara (Melbourne House, 1983).

---

## The Editor

The 48K Spectrum editor is a **single-line, keyword-entry** system — a stark contrast to the full-screen editors on contemporary machines like the BBC Micro or Commodore 64.

### How It Works

The screen is divided into two regions: the **upper screen** (lines 0–21) for program output, and the **lower screen** (lines 22–23) for the editor input area. The editor operates on the "edit line" — a buffer at `E_LINE` (`#5C59`) that holds whatever the user is currently typing.

Key entry uses the **keyword-on-key** system: each key produces different results depending on the current shift mode. The mode cycle is:

| Mode | Symbol | Produces |
|------|--------|----------|
| K (Keyword) | `K` | BASIC keywords (`PRINT`, `RUN`, etc.) |
| L (Letter) | `L` | Lowercase letters (no shift) or uppercase (Caps Shift) |
| E (Extended) | `E` | Extended tokens (`READ`, `DATA`, `RESTORE`) |
| G (Graphics) | `G` | Graphic characters and user-defined graphics |

The mode is indicated by the cursor shape (flashing `K`, `L`, `E`, `G`, or `C` for capital-lock mode). Mode transitions happen automatically: pressing Caps Shift + Symbol Shift cycles between modes.

### The Edit Buffer

When the user presses `ENTER` on a line:
- If it starts with a number → the line is added/replaced in the program
- If it starts with a keyword → it's executed immediately (direct command)
- If it's empty → the ROM enters edit mode for the current line

The edit buffer is part of the workspace managed by the ROM. It sits between `E_LINE` and `WORKSP` in memory.

### Limitations

The single-line editor is the most criticised aspect of the Spectrum. Users cannot see the full program while editing, cursor movement is limited to the edit line, and there is no block operations. The 128K ROM addresses most of these issues with its full-screen editor (see [rom_128k.md](rom_128k.md)).

For a detailed analysis of the editor's internal operation, see *Mastering Machine Code on Your ZX Spectrum* by Toni Baker (Sunshine Books, 1983).

---

## Character Set

The ROM contains 96 characters at `#1A9C`–`#1D9B`, each stored as 8 bytes (one byte per pixel row, 8 pixels wide). The character codes and their ROM addresses:

| Code range | Characters | Notes |
|------------|-----------|-------|
| `#20`–`#5A` | Space, punctuation, digits, uppercase A–Z | Standard ASCII subset |
| `#5B`–`#60` | `£`, `?`, `©`, `→`, `←`, `` ` `` | Spectrum-specific characters |
| `#61`–`#7A` | Lowercase a–z | |
| `#7F`–`#A4` | Token representations (inverse space, etc.) | Block graphics, inverse characters |
| `#A5`–`#FF` | BASIC keywords (tokens) | `PRINT`, `IF`, `GOTO`, etc. |

The character set pointer is stored at `CHARS` (`#5C36`), which by default points to `#19AD` (256 bytes before the actual font data — this offset simplifies address calculations). User-defined graphics (UDGs) start at `UDG` (`#5C7B`), defaulting to `#FF58`.

The font uses a classic 8×8 pixel cell with no descenders — lowercase letters like `g`, `p`, `q` sit on the baseline rather than extending below it, which keeps the implementation simple but makes text less readable than on machines with proper descender support.

---

## Interrupt Handler

The maskable interrupt handler at `#0038` is covered in detail in [interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md). In summary, the ROM ISR does two things per frame:

1. **Increments FRAMES** — the 3-byte uptime counter at `#5C78`
2. **Scans the keyboard** — reads all 8 half-rows and updates the keyboard state buffer

The handler costs approximately 700 T-states per frame (~1% of the 69,888 T-state budget on 48K). It runs in IM1 — the only interrupt mode the standard ROM supports.

---

## NMI Handler

The non-maskable interrupt handler at `#0066` performs a warm restart: it jumps to `#1F05`, which reinitialises the BASIC system without clearing the program. This is triggered by some peripheral devices (e.g., Multiface) to force the machine back to a known state.

On the standard 48K Spectrum, no hardware asserts NMI — the NMI pin is not connected to any on-board device. NMI is only used by external peripherals.

---

## Error Handling System

The ROM has a structured error-handling mechanism that allows both the BASIC interpreter and machine code programs to recover from errors gracefully. Understanding this system is essential for any program that calls ROM routines — because those routines can invoke `RST #08` (error) at any time.

### Error Reporting Chain

When an error is detected, the flow is:

1. **`RST #08`** (`#0008`) is called with `A` = error number. This does **not** return — it pushes the return address onto the stack and jumps to `ERROR-2` (`#0053`).
2. **`ERROR-2`** reads `ERR_SP` (`#5C3D`) — the address of the current error handler's recovery point on the machine stack. It sets `ERR_NR` (`#5C3A`) to `A−1` (so `#FF` means no error), then pops `ERR_SP` and jumps to the saved address.
3. The **error handler** at the recovery point typically prints the error message and returns to the editor loop.

### Report Codes

The ROM defines 22 error reports, encoded as `ERR_NR + 1`:

| Code | Report | Typical cause |
|------|--------|--------------|
| `0` | `0 NEXT without FOR` | FOR stack underflow |
| `1` | `1 Variable not found` | Undefined variable in expression |
| `2` | `2 Subscript wrong` | Array index out of range |
| `3` | `3 Wrong parameter count` | `DEF FN` argument mismatch |
| `4` | `4 Out of memory` | No room for line or variable |
| `5` | `5 No room for line` | Not enough RAM for BASIC line |
| `6` | `6 RETURN without GOSUB` | GOSUB stack underflow |
| `7` | `7 Out of DATA` | READ past end of DATA |
| `8` | `8 Invalid colour` | Colour value > 7 |
| `9` | `9 BREAK into program` | BREAK pressed during execution |
| `A` | `A Out of screen` | PRINT AT outside 0–21/0–31 |
| `B` | `B Integer out of range` | Value > 65535 for integer operation |
| `C` | `C STOP in INPUT` | STOP executed |
| `D` | `D Invalid argument` | SQR of negative, etc. |
| `E` | `E Out of DATA` (LOAD) | Tape data exhausted |
| `F` | `F Invalid filename` | Bad SAVE/LOAD filename |
| `G` | `G No room for line` | (duplicate of 5 in some contexts) |
| `H`–`K` | Various | System-level errors |
| `L`–`R` | Various | Tape, interface, and extended errors |

### Setting Up a Custom Error Handler

Machine code programs can install their own error handler by saving the current `ERR_SP` and replacing it with their own recovery point:

```z80
; Protect a ROM call with an error handler
    LD   (old_err_sp),SP   ; Save current ERR_SP value
    LD   HL,error_handler
    PUSH HL                ; Push recovery address
    LD   HL,(#5C3D)        ; Get old ERR_SP
    PUSH HL                ; Push old recovery point
    LD   (#5C3D),SP        ; Set new ERR_SP to current SP

    ; Now call ROM routines safely
    CALL #1601             ; CHAN-OPEN (example)
    ; If this triggers RST #08, control goes to error_handler

    ; Clean up on success
    POP  HL
    LD   (#5C3D),HL        ; Restore old ERR_SP
    POP  HL                ; Discard our handler address
    ; Continue normally...

error_handler:
    ; A = error code + 1
    ; SP points to old_err_sp value
    POP  HL
    LD   (#5C3D),HL        ; Restore old ERR_SP
    ; Handle the error (A = report code)
    CP   9                 ; Was it BREAK?
    JR   Z,break_pressed
    ; Handle other errors...
```

This pattern is the machine code equivalent of BASIC's `ON ERROR GOTO`. The key insight is that `ERR_SP` points to a **return address** on the Z80 machine stack — when an error occurs, `ERROR-2` simply pops that address and jumps to it.

> [!WARNING]
> Every ROM routine that can fail uses `RST #08`. If you call any ROM routine without setting up `ERR_SP`, an error will jump to whatever stale address `ERR_SP` happens to point to — usually a crash. Always protect ROM calls with your own error handler.

---

## ROM Versions

There are two official ROM versions for the 48K Spectrum:

| Version | Known as | Differences |
|---------|----------|-------------|
| Issue 2 | "Issue 2 ROM" | Original 1982 release. Has a few bugs: `SLOW`/`FAST` mode not fully implemented (no actual speed change on Spectrum), some tape loading edge cases |
| Issue 3 | "Issue 3 ROM" | 1983 bug-fix release. The most common version. Fixes include corrected tape handling and arithmetic edge cases |

Both versions are almost identical — the differences affect only a handful of bytes. The vast majority of software works identically on both. For a comprehensive list of ROM issues and third-party replacements, see [rom_versions.md](rom_versions.md) (planned).

---

## Command Handler Internals

This section describes how the major BASIC commands are implemented internally — what subroutines they call, what system variables they modify, and what a machine code programmer needs to know to invoke them directly.

### PRINT (`#1FCD`)

`PRINT` is the most complex output command. Its handler does not do the printing itself — instead it sets up the output stream and delegates to the **print items loop**.

The print items loop handles each item in the `PRINT` statement:

| Separator/keyword | Action |
|-------------------|--------|
| `;` | Suppress the trailing newline for this item |
| `,` | Move to next tab zone (columns 0, 8, 16, 24) |
| `'` (apostrophe) | Print a newline (carriage return) |
| `#` | Followed by a stream number — redirect output to that stream |
| `AT` | Followed by row, column — move cursor position |
| `TAB` | Followed by column number — move to that column |
| Expression | Evaluate and print the result |

Numeric expressions are converted from the 5-byte FP format to ASCII via `PRINT_FP` (`#2DE3`). String expressions are printed character by character via `PR_STRING` (`#203C`). After all items are processed, a trailing newline is printed unless the last item ended with `;` or `,`.

The current print position is tracked by `S_POSN` (`#5C88`, column and line). The `PRINT` handler also updates `ATTR_T` and `MASK_T` for colour handling.

### INPUT (`#2089`)

`INPUT` combines printing (for prompts) with the editor (for user input). Its behaviour depends on the syntax:

- `INPUT a` — prompt with `?`, wait for a number, assign to variable `a`
- `INPUT a$` — prompt with `?`, wait for a string, assign to variable `a$`
- `INPUT LINE a$` — same but accepts commas in the string (normally commas separate items)
- `INPUT "Prompt";a` — print the prompt string, then wait for input

Internally, `INPUT` opens the keyboard channel (`CHAN-OPEN` with A=0), prints any prompt items, then calls the `EDITOR` routine (`#0F2C`) to accept user input. The result is parsed as an expression and assigned to the target variable using the same `LET` mechanism.

### PLOT, DRAW, and CIRCLE

The three graphics commands share a common coordinate system: (0,0) is the **bottom-left** pixel, (255,175) is the top-right. Coordinates are 8-bit — the pixel grid is 256×176 but only the central 256×192 is displayed.

**PLOT** (`#22DC`):
1. Parse optional colour items (INK, PAPER, etc. that precede the coordinates)
2. Parse two numeric expressions: x-coordinate, y-coordinate
3. Convert to pixel address via `PIXEL_ADD` (`#22AA`) — returns HL = byte address, A = bit mask
4. Set the pixel in the screen buffer
5. Update `COORDS` (`#5C7D`) — the current graphics cursor position
6. Update the attribute byte at the corresponding attribute address

**DRAW** (`#2382`):
1. Parse optional colour items, then two numeric expressions (dx, dy — *relative* offsets)
2. If a third parameter is present, it's a curve (arc) — otherwise it's a straight line
3. For a straight line: uses Bresenham's algorithm (`DRAW_LINE` at `#24B7`) to draw from current `COORDS` to `COORDS + (dx, dy)`
4. For a curve: computes the curve as a series of short line segments using the `STACKER` algorithm
5. Updates `COORDS` at each pixel step

**CIRCLE** (`#2320`):
1. Parse optional colour items, then x, y (centre), and r (radius)
2. Computes 8 points around the circumference and connects them with `DRAW` arcs
3. Uses the calculator heavily for the trigonometric calculations

> [!NOTE]
> PLOT, DRAW, and CIRCLE all use the calculator stack for their parameter computations. They are among the slowest BASIC commands because every coordinate goes through 5-byte floating-point arithmetic.

### BEEP (`#03F8`)

`BEEP duration, pitch` converts musical parameters into raw hardware timing:

1. **Duration** (seconds) and **pitch** (semitones from middle C, where 0 = middle C ≈ 261.6 Hz) are evaluated as numeric expressions
2. The calculator converts pitch to frequency: `f = 440 × 2^((pitch−9)/12)` (semitone formula)
3. The frequency and duration are converted to raw parameters for `BEEPER` (`#03B5`)
4. `BEEPER` toggles the ULA beeper bit (bit 4 of port `#FE`) at the calculated rate:
   - `HL = 437500 / f − 30.125` (half-period in T-states)
   - `DE = f × duration × HL` (total number of half-cycles)
5. The beeper loop runs with interrupts disabled — `BEEP` monopolises the CPU for its entire duration

The ROM's `BEEP` command is **blocking** — the interpreter does nothing else while the note plays. For background sound, machine code must program the beeper independently (or on the 128K, use the AY chip).

### LET (`#2AFF`)

`LET` is the assignment command — it handles `LET a = 42`, `LET a$ = "hello"`, and array element assignments like `LET a(3) = 7`. Its flow:

1. **Variable lookup** via `LOOK_VARS` (`#28B2`) — searches the variable area for the given name
2. If the variable exists and the assignment changes its size (e.g., string length changes), the old variable is reclaimed
3. If the variable doesn't exist, `MAKE_ROOM` (`#1655`) creates space for it in the variable area
4. The right-hand expression is evaluated and its value stored
5. For string assignments, the old string data may trigger **garbage collection** — the ROM compacts string storage to reclaim freed memory

Garbage collection can take several hundred milliseconds on a program with many strings. This is the cause of the infamous "pause" in BASIC programs that do heavy string manipulation.

### LOAD and SAVE (`#0605`)

The tape I/O commands all funnel through a common routine:

| Command | Action | Difference from LOAD |
|---------|--------|---------------------|
| `LOAD` | Load data from tape into memory | Overwrites existing data |
| `VERIFY` | Load and compare — don't write | Data is compared byte-by-byte to existing memory |
| `MERGE` | Load and merge — add new lines/variables | Existing lines are kept; conflicting lines are replaced |
| `SAVE` | Write data to tape | Writes header + data blocks |

The tape format uses two types of blocks:

- **Header block** (17 bytes): type (PROGRAM/ARRAY/CODE), filename (10 chars), data length, and two parameters
- **Data block**: the actual bytes

Each block is preceded by a **pilot tone** (5 seconds for the first header, 2 seconds for subsequent blocks). The pilot allows the receiver to synchronise its timing. Data is encoded as a series of pulses: a `0` bit is one short pulse (~855 T-states), a `1` bit is two half-length pulses (~1710 T-states total).

For the byte-level tape format details, see [tape_format.md](../03_io/storage/tape_format.md).

### Tape Data Format

The ROM's tape I/O routines at `SA-BYTES` (`#04C2`) and `LD-BYTES` (`#0556`) implement a self-clocking serial protocol that encodes data as audio pulses on cassette tape. The format is designed for reliability over poor-quality audio connections.

#### Pulse Encoding

Each bit is encoded as a sequence of level transitions:

| Bit | Encoding | Total T-states |
|-----|----------|---------------|
| `0` | One full pulse (high → low) of ~855 T-states | ~1710 T-states |
| `1` | Two half-length pulses of ~1710 T-states each | ~3420 T-states |

A `1` bit takes twice as long as a `0` bit. The ROM measures pulse widths during loading and distinguishes `0` from `1` by comparing the pulse width to a threshold of approximately 2100 T-states.

#### Block Structure

Each saved file consists of **two blocks**: a header block and a data block.

**Header block** (17 bytes + flag byte + checksum):

| Byte offset | Size | Field |
|------------|------|-------|
| 0 | 1 | Flag = `#00` (header marker) |
| 1 | 1 | Block type: `#00` = PROGRAM, `#01` = NUMERIC ARRAY, `#02` = CHARACTER ARRAY, `#03` = CODE/BYTES |
| 2–11 | 10 | Filename (padded with spaces) |
| 12–13 | 2 | Data length (LE) |
| 14–15 | 2 | Parameter 1: for PROGRAM = autostart line number or `#8000`; for CODE = start address |
| 16–17 | 2 | Parameter 2: for PROGRAM = length of variables area; for CODE = 32768 (`#8000`) |
| 18 | 1 | Checksum (XOR of bytes 0–17) |

**Data block** (variable length + flag byte + checksum):

| Byte offset | Size | Field |
|------------|------|-------|
| 0 | 1 | Flag = `#FF` (data marker) |
| 1–N | N | Data bytes |
| N+1 | 1 | Checksum (XOR of all bytes 0–N) |

#### Loading Sequence

1. **Pilot tone** — 5 seconds of continuous short pulses (2168/2169 T-states alternating) before the first header, 2 seconds before subsequent blocks
2. **Sync pulses** — two sync bytes mark the transition from pilot to data
3. **Flag byte** — `#00` for header, `#FF` for data
4. **Data bytes** — the actual payload
5. **Checksum** — XOR of all preceding bytes (including flag)

The nominal baud rate is approximately **1,500 bits/second** (about 350 bytes/second). A full 48K RAM save takes roughly 2.5 minutes.

#### Calling SA-BYTES and LD-BYTES from Machine Code

```z80
; Save 6912 bytes (screen) to tape
    LD   IX,#4000       ; Start address
    LD   DE,#1B00       ; Length = 6912
    LD   A,#FF          ; Data block (not header)
    CALL #04C2           ; SA-BYTES

; Load 6912 bytes from tape to screen
    LD   IX,#4000       ; Destination
    LD   DE,#1B00       ; Length
    LD   A,#FF          ; Expecting data block
    CALL #0556           ; LD-BYTES
    ; Carry set = success, Carry clear = error
```

---

## Practical Use Cases

This section provides ready-to-use code patterns for common tasks that call ROM routines from machine code. All examples assume the standard 48K ROM (or ROM 1 on the 128K).

### 1. Formatted Number Output

The ROM provides two routines for printing 16-bit integers as decimal text:

```z80
; Print a number (0-9999) with no padding
    LD   BC,42           ; Number to print
    CALL #1A1B           ; OUT_NUM_1
    ; Prints "42" at current cursor position

; Print a number (0-9999) space-padded to 5 chars
    LD   HL,number_addr
    CALL #1A28           ; OUT_NUM_2
    ; Prints "   42" at current cursor position
```

`OUT_NUM_1` prints BC as a decimal number with no leading spaces. `OUT_NUM_2` reads a 2-byte number from (HL) and prints it space-padded. Both use `RST #10` internally for character output.

### 2. Reading a BASIC Numeric Variable

To read the value of a BASIC variable (e.g., `score`) from machine code:

```z80
; Find and read variable 'score' (or any single-char 's')
find_var:
    LD   HL,(#5C4B)       ; VARS — start of variable area
.next_var:
    LD   A,(HL)
    CP   #80               ; End marker?
    JR   Z,.not_found
    ; Check if this is 's' numeric (bit 6 set, bit 5 set)
    CP   #73               ; 's' with bits 5,6 set = #20+#53 = #73
    JR   Z,.found_s
    ; Not it — skip past this variable
    ; ... (advance past name + 5 bytes for numeric) ...
    INC  HL                ; Skip name byte
    INC  HL                ; Skip 5 FP bytes
    INC  HL
    INC  HL
    INC  HL
    JR   .next_var
.found_s:
    INC  HL                ; Point to FP value
    LD   DE,my_buffer
    LDI                     ; Copy 5 bytes
    LDI
    LDI
    LDI
    LDI
    ; my_buffer now holds the 5-byte FP value of 's'
.not_found:
```

For a simpler approach, use `LOOK_VARS` (`#28B2`) which does the search for you. Place the variable name in the edit line and point `CH_ADD` to it before calling.

### 3. Error-Safe ROM Calls

When calling any ROM routine that might fail (most of them), wrap the call with an error handler:

```z80
safe_chan_open:
    ; Set up error recovery point
    LD   HL,.on_error
    PUSH HL
    LD   HL,(#5C3D)        ; Old ERR_SP
    PUSH HL
    LD   (#5C3D),SP        ; Install our handler

    LD   A,2               ; Open stream 2 (screen)
    CALL #0D4D             ; CHAN-OPEN

    ; Success — clean up
    POP  HL
    LD   (#5C3D),HL        ; Restore ERR_SP
    POP  HL                ; Discard error handler
    RET

.on_error:
    ; A = error code + 1
    POP  HL
    LD   (#5C3D),HL        ; Restore ERR_SP
    ; Handle error...
    RET
```

### 4. Loading a Screen$ from Tape

To load a .SCR file (raw screen dump) directly into the display buffer:

```z80
load_screen:
    LD   IX,#4000          ; Screen pixel buffer
    LD   DE,#1B00          ; 6912 bytes (pixels + attributes)
    LD   A,#FF             ; Data block
    CALL #0556             ; LD-BYTES
    RET  C                 ; Success (Carry set)
    ; Carry clear = error, A = error code
    RET
```

This bypasses the header — the caller must have already found the right tape position. For a full load with header matching, use the ROM's high-level LOAD routine.

### 5. Walking the BASIC Program

To enumerate all lines in the current BASIC program:

```z80
walk_program:
    LD   HL,(#5C53)        ; PROG
    LD   DE,(#5C4B)        ; VARS (end of program)
.walk_loop:
    ; Check if we've reached VARS
    PUSH HL
    PUSH DE
    AND  A
    SBC  HL,DE
    POP  DE
    POP  HL
    JR   NC,.walk_done     ; HL >= DE means past program end

    ; HL points to a line: 2B line num + 2B length + data + #0D
    LD   A,(HL)            ; Line number MSB
    INC  HL
    LD   H,(HL)            ; Line number LSB
    LD   L,A
    ; HL = line number (0-9999)
    PUSH HL
    ; ... process line number ...
    POP  HL

    ; Advance to next line
    ; Go back 2 bytes to read the length field
    DEC  HL                ; Back to length LSB
    DEC  HL                ; Back to length MSB
    ; Actually need to recalculate from original position
    ; ... (see NEXT-ONE routine at #19B8 for the correct approach)
    JR   .walk_loop
.walk_done:
    RET
```

The ROM's own `NEXT-ONE` (`#19B8`) and `LINE-ADDR` (`#196E`) routines handle this correctly — they understand the variable-length line format and can find any line by number.

### 6. Frame-Accurate Timing

The 3-byte `FRAMES` counter at `#5C78` increments 50 times per second (on a PAL machine):

```z80
; Wait for exactly N frames
; Uses HALT to synchronise to the next frame interrupt
wait_frames:
    PUSH BC
    LD   B,N              ; Number of frames to wait
.wait:
    HALT                  ; Wait for next interrupt (20ms)
    DJNZ .wait
    POP  BC
    RET

; Read the current frame count (3 bytes)
    DI                    ; Atomic read
    LD   HL,(#5C78)      ; Low 2 bytes
    LD   A,(#5C7A)       ; High byte
    EI
    ; A:HL = frame count (max ~14.5 million frames = ~80 hours)
```

`HALT` puts the Z80 to sleep until the next interrupt, consuming no CPU cycles. This is the standard technique for frame-synced animation.

### 7. Keyboard Input via ROM

Two levels of keyboard access are available:

```z80
; Low-level: just read the raw key state (no debounce)
    CALL #028E             ; KEY-SCAN
    ; Returns key data in A, D, E
    ; Does not update KSTATE or LAST_K

; High-level: full keyboard decode with debounce
    CALL #02BF             ; KEYBOARD
    ; Updates KSTATE, LAST_K, FLAGS
    ; Key code in LAST_K (#5C08) if a key was pressed

; Wait for any keypress
    CALL #15D4             ; WAIT-KEY
    ; Returns with A = key code
```

The key code is a system-specific encoding (not ASCII). To convert to a character, check the key tables at `#0205`.

### 8. Custom Channel for Text Capture

Redirect all `PRINT` output to a buffer by replacing the screen channel's output routine:

```z80
capture_setup:
    LD   HL,(#5C4F)        ; CHANS pointer
    ; Skip channel K (5 bytes), arrive at channel S
    LD   BC,5
    ADD  HL,BC
    ; Bytes 0-1 of channel S = output routine address
    LD   (save_s_output),HL
    LD   (HL),my_capture & #FF
    INC  HL
    LD   (HL),my_capture >> 8
    RET

capture_restore:
    LD   HL,(#5C4F)
    LD   BC,5
    ADD  HL,BC
    LD   DE,(save_s_output)
    LD   (HL),E
    INC  HL
    LD   (HL),D
    RET

my_capture:
    ; A = character to output
    ; Instead of printing, store in buffer
    LD   (capture_buffer),A
    INC  capture_buffer+1  ; Advance pointer (simple case)
    RET
```

This technique is used by Interface 1 to add microdrive, network, and RS-232 channels, and by many games to capture text output for custom display.

### 9. Using the Cassette Routines for Data Storage

Save and load arbitrary data blocks to tape:

```z80
; Save a data block with a header
    ; First, create the header
    LD   IX,header_data
    LD   DE,17             ; Header length
    LD   A,#00             ; Header block
    CALL #04C2             ; SA-BYTES (writes header)

    ; Then write the data
    LD   IX,my_data        ; Data start
    LD   DE,my_data_len
    LD   A,#FF             ; Data block
    CALL #04C2             ; SA-BYTES (writes data)
    RET

; Load data from tape
    ; First read the header
    LD   IX,header_data
    LD   DE,17
    LD   A,#00             ; Expect header
    CALL #0556             ; LD-BYTES
    JR   NC,load_error

    ; Then read the data
    LD   IX,my_data
    LD   DE,my_data_len
    LD   A,#FF             ; Expect data
    CALL #0556             ; LD-BYTES
    JR   NC,load_error
    ; Success!
    RET
```

### 10. Floating-Point Math from Assembly

The calculator provides trigonometric and mathematical functions that would be tedious to implement in machine code:

```z80
; Compute SQR(2) = 1.414...
    RST  #28
    DB   #34               ; stk_data
    DB   #82,#00,#00,#00,#00  ; 2.0 (exponent #82 = 2^2, mantissa 0)
    DB   #28               ; sqr → 1.4142135...
    DB   #38               ; end-calc
    ; Result is on the calculator stack
    ; To retrieve: read 5 bytes at (STKBOT)
    LD   HL,(#5C63)        ; STKBOT
    LD   DE,result
    LDI : LDI : LDI : LDI : LDI

; Compute 2^10 = 1024
    RST  #28
    DB   #3F,#01           ; stk-one (push 1.0)
    DB   #01               ; exchange (reorder if needed)
    DB   #34
    DB   #82,#00,#00,#00,#00  ; 2.0
    DB   #34
    DB   #8A,#00,#00,#00,#00  ; 10.0 (exponent #8A = 2^10)
    DB   #06               ; to_power → 1024.0
    DB   #38               ; end-calc
```

For more complex examples including trigonometry and logarithms, see Toni Baker's *Machine Code Calculator* series, which dedicates an entire article to the calculator's instruction set with practical examples.

---

The Spectrum ROM reflects the constraints of its era:

- **16K is tiny**. The entire OS + BASIC interpreter fits in 16K. Compare: MS-DOS 1.0 (1981) was 4K for the BIOS + 3.5K for DOS; the BBC Micro OS was 16K plus 16K BASIC separately. Sinclair achieved this by having no file system, no driver model, and a minimal command set.
- **The channel/stream model was ahead of its time.** Device-independent I/O with redirectable streams is a Unix-like concept that very few 8-bit machines implemented. It enabled Interface 1 to add new devices without modifying the ROM.
- **BASIC is the shell.** There is no separate command processor — BASIC's direct mode *is* the command line. `LOAD`, `SAVE`, `RUN`, `COPY` are all BASIC statements.
- **The floating-point calculator is a virtual machine.** The `RST #28` entry point implements a stack-based bytecode interpreter for mathematical operations. This is an elegant design that keeps the expression evaluator simple — it just emits calculator bytecodes.

---

## Cross-References

- **System variables** (FRAMES, PROG, VARS, CHANS, FLAGS, keyboard state): [system_variables.md](system_variables.md)
- **48K memory map** (ROM region, screen, system vars): [memory_map_48k.md](../05_development/03_memory_and_io/memory_map_48k.md)
- **128K ROM** (menu system, BASIC extensions, RAM disk): [rom_128k.md](rom_128k.md)
- **Interrupt programming** (hooking #0038, ISR design): [interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md)
- **Character set** (pixel layout, token table): [screen_layout.md](../05_development/03_memory_and_io/screen_layout.md)
- **I/O ports** (#FE keyboard, beeper, border): [io_ports.md](../05_development/03_memory_and_io/io_ports.md)
