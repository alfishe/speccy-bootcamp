[← Plan](../../PLAN.md) · [Assembly](README.md)

# Z80 Assembly on the ZX Spectrum — First Program, Toolchain, Memory Map, Binary Formats

The ZX Spectrum runs a **3.5 MHz Z80A** with **16 KB of ROM** and **16 to 48 KB of RAM**. A single video frame is **69,888 T-states** long on the 48K, **70,084** on the +2A/+3, and **71,111** on the Pentagon. Every effect that defines the platform — the jittery multicolor borders of a 1985 demo, the four-voice beeper music of a 1992 game, the smooth 50fps scrolling of *Zexolyth*, the 3D fill of *Famous 5* — comes from assembly code that respects those T-state budgets. Sinclair BASIC peaks at perhaps 600 fully interpreted operations per frame. Assembly peaks at roughly 10,000.

This is the entry point for programmers who already know BASIC, have read the [Z80 architecture overview](../../01_cpu/z80_architecture.md) and the [instruction-set reference](../../01_cpu/z80_instruction_set.md), and want to write a program that runs directly on the hardware — not interpreted, not abstracted, not protected. The article covers the **toolchain**, the **memory map from the programmer's point of view**, a complete annotated **Hello World**, the **build pipeline** from `.asm` source to emulator-loaded binary, and the **first debugging session** that teaches you how a Spectrum program actually behaves when it runs.

> [!NOTE]
> This article is the first in a six-article series. The complete series covers: this intro, [ROM calls](rom_calls.md), [stack and calling conventions](stack_and_rst.md), [structural design patterns](assembly_patterns.md), [performance optimization](assembly_optimization.md), and [mixed C and assembly](c_interop.md). For the full ISA reference see [z80_instruction_set.md](../../01_cpu/z80_instruction_set.md); for register-level details see [z80_architecture.md](../../01_cpu/z80_architecture.md); for a list of every ROM entry point see [rom_routines.md](../../10_references/rom_routines.md).

---

## Why Assembly on the Spectrum

The ZX Spectrum has no operating system in the modern sense. The 16 KB ROM is a BASIC interpreter with a thin set of support routines; there is no kernel, no scheduler, no device driver model, no system calls beyond what the ROM exposes for its own use. When you write a Spectrum program in assembly, you are **writing the entire user experience**: you load your code at some address in RAM, you point the CPU at it, and from that moment until the user resets the machine, **your code is the program**.

Three reasons programmers choose assembly over Sinclair BASIC:

| Reason | Quantitative impact |
|---|---|
| **Speed** | The same loop runs ~100× faster in compiled Z80 than in interpreted Sinclair BASIC. A `FOR i=1 TO 1000: NEXT i` takes about 10 seconds in BASIC; the equivalent `LD BC,1000 / DEC BC / JR NZ` loop runs in under 50 milliseconds. |
| **Hardware access** | BASIC cannot read the AY-3-8912 sound chip directly, cannot raster-synchronize with the video beam, cannot scan the keyboard at scanline granularity, cannot page 128K memory banks. Assembly can do all four. |
| **Code size** | A BASIC line like `20 PRINT "HELLO"` occupies 14 bytes tokenized; the equivalent 6-byte Z80 routine (`LD A,'H' / RST #10 / RET`) does the same work and is reusable in a 256-byte demo. |

The cost is that assembly is **unforgiving**. There is no syntax error message, no line editor, no `RUN` that catches your mistake. A bug at the wrong moment — writing to ROM, jumping into the screen memory, unbalancing the stack — will either crash the machine instantly or produce a colorful screen of garbage that takes the system down with it. This article, and the rest of the series, is about how to do it right.

### What This Article Covers (and Does Not)

This article is a **first contact** with ZX Spectrum assembly. It covers what every other article in the knowledge base takes for granted: how to install a toolchain, where to put your code in memory, what a minimal program looks like, how to turn it into something an emulator will run, and how to debug it when it breaks.

It does **not** cover:
- The Z80 instruction set itself — see [z80_instruction_set.md](../../01_cpu/z80_instruction_set.md) (1108 lines) for every opcode, T-state, and addressing mode
- Register-level architecture — see [z80_architecture.md](../../01_cpu/z80_architecture.md)
- How to call the ROM — see [rom_calls.md](rom_calls.md) in this series
- How interrupts work — see [z80_interrupts.md](../../01_cpu/z80_interrupts.md) and [interrupt_programming.md](../04_interrupts/interrupt_programming.md)
- Optimization — see [assembly_optimization.md](assembly_optimization.md) in this series

---

## Toolchain Setup

Modern ZX Spectrum development uses **cross-platform tools** running on Linux, macOS, or Windows. The "native" development environment — typing assembly into ALASM or STS on a real Spectrum or emulator — is covered in [native_toolchain.md](../../09_toolchain/native_toolchain.md) and is a historical curiosity for new projects. The modern workflow is: write `.asm` files in your editor of choice, assemble with a cross-assembler, load the resulting binary into an emulator for testing.

### The Minimum Viable Stack

| Component | Recommended choice | Alternatives |
|---|---|---|
| **Cross-assembler** | [SjASMPlus](../../09_toolchain/sjasmplus.md) (z00m128 fork, 1.23+) | [Pasmo](../../09_toolchain/pasmo.md), [RASM](../../09_toolchain/rasm.md), [z88dk-z80asm](../../09_toolchain/z88dk_z80asm.md), [vasm](../../09_toolchain/vasm.md), [WLA-DX](../../09_toolchain/wla_dx.md) |
| **Emulator** | [Fuse](https://fuse-emulator.sourceforge.io/) (universal, accurate, debugger) | [ZEsarUX](https://github.com/chernyna/zesarux), [UnrealSpeccy](https://spectrum.to/), [Klive](https://klivegfx.blogspot.com/), [CSpect](https://cspect.org/) (ZX Next focused), [SpecEmu](http://www.worldofspectrum.org/forums/discussion/52245/) |
| **Editor / IDE** | Visual Studio Code with [DeZog](https://github.com/maziac/DeZog) extension | Any text editor; full IDE setup documented in [vscode_integration.md](../../09_toolchain/vscode_integration.md) |
| **Optional: C compiler** | [z88dk](../../09_toolchain/z88dk.md) with sccz80 or zsdcc | [SDCC](../../09_toolchain/sdcc.md) standalone (without z88dk) |

The recommendation throughout this series is **SjASMPlus**, for three reasons:

1. **Device model**: SjASMPlus understands the Spectrum's paged memory. Other assemblers deal in flat 64 KB; SjASMPlus tracks which RAM page is in which slot at every address, which prevents a whole category of bugs in 128K programs.
2. **Direct output**: `SAVESNA` writes a `.sna` snapshot, `SAVETAP` writes a `.tap` tape image, `SAVETRD` writes a TR-DOS disk — all in a single assembly pass, no post-processing. For the 128K and Next, `SAVENEX` writes a `.nex` file directly.
3. **Lua scripting**: When a project grows beyond toy examples, you need code generation for lookup tables, asset conversion, conditional builds. SjASMPlus embeds Lua 5.5 for this purpose; see [sjasmplus.md § Lua Scripting](../../09_toolchain/sjasmplus.md#lua-scripting) for the deep dive.

### Installing SjASMPlus

Full installation instructions are in [sjasmplus.md § Installation](../../09_toolchain/sjasmplus.md#installation). The short version, for the three common platforms:

```bash
# Linux / macOS / FreeBSD / Raspberry Pi (build from source)
git clone https://github.com/z00m128/sjasmplus.git
cd sjasmplus
make          # produces sjasmplus binary in the source tree

# Windows: download pre-built sjasmplus.exe from
# https://github.com/z00m128/sjasmplus/releases/latest
```

Verify installation:

```bash
sjasmplus --version
# sjasmplus 1.23.1
```

### Picking an Emulator

For learning, **Fuse** is the safest choice: it is accurate, cross-platform, and has a built-in machine-code debugger that displays Z80 registers, disassembly, memory, and breakpoints in a single window. For the ZX Spectrum Next, use **CSpect**. For reverse engineering, **ZEsarUX** has the richest debug and tracing features. For pure cycle accuracy in modern demos, **SpecEmu** is the gold standard.

| Emulator | Strongest feature | Use case |
|---|---|---|
| **Fuse** | Stable, cross-platform, integrated debugger | First contact, learning, general development |
| **ZEsarUX** | Real hardware peripherals (DivMMC, ZXUNO, Next), rich tracing | Reverse engineering, hardware-specific debugging |
| **CSpect** | ZX Spectrum Next full support (Layer 2, tilemap, sprites, copper) | Next-only development |
| **UnrealSpeccy** | Russian clone accuracy, lightweight | Pentagon / Scorpion-targeted code |
| **SpecEmu** | Cycle-accurate contention and timing | Demoscene production |
| **Klive** | Integrated IDE with debugger and asset preview | Visual development workflow |

The first program in this article runs in any of them. The article uses Fuse screenshots and debugger conventions; the equivalent windows exist in every other emulator.

---

## Source File Structure

A Z80 assembly source file is plain text with one instruction or directive per line. The canonical extension is `.asm` (SjASMPlus, Pasmo, z88dk-z80asm) or `.z80s` (some native tools). The structure follows the same conventions across most modern assemblers:

```z80
    DEVICE ZXSPECTRUM48       ; SjASMPlus: declare the target hardware
    ORG    #8000              ; subsequent code emits at address #8000

start:
    LD   A, 2                 ; stream 2 = main screen
    CALL #1602                ; ROM CHAN-OPEN
    LD   HL, message
loop:
    LD   A, (HL)
    AND  A                   ; test A==0 (sets Z flag)
    JR   Z, done
    RST  #10                 ; ROM PRINT_CHAR
    INC  HL
    JR   loop

done:
    RET

message:
    DB   "Hello, World!", #0D, #00

    SAVESNA "hello.sna", start    ; emit a .sna snapshot, entry = start
    SAVETAP "hello.tap", start    ; also emit a .tap tape image
```

### Anatomy of a Source Line

Each line has at most four fields, separated by whitespace:

```
[label:]  [mnemonic [operands]]  [; comment]
```

| Field | Required? | Example | Notes |
|---|---|---|---|
| **Label** | Optional | `loop:` | Defines a symbolic name for the address of the next byte emitted. Becomes a value the assembler can use anywhere a 16-bit immediate is allowed. Labels ending in `:` are local to the file (SjASMPlus); labels ending in `::` are global across modules. |
| **Mnemonic** | Optional | `LD` | Either a CPU instruction (`LD`, `ADD`, `JR`, `RET`) or an assembler directive (`ORG`, `DEVICE`, `DB`, `EQU`, `SAVESNA`). |
| **Operands** | Depends on mnemonic | `A, (HL)` | Registers, immediates, labels, or memory references. Multiple operands separated by commas. |
| **Comment** | Optional | `; loop body` | Everything from `;` to end of line is ignored by the assembler. |

A line can be **blank** (assembler ignores it) or **comment-only** (use `;` as the first non-whitespace character).

### Essential Directives

SjASMPlus and most modern Z80 assemblers share a common set of directives. The ones you will use in every program:

| Directive | Purpose | Example |
|---|---|---|
| `ORG addr` | Set the origin address for subsequent code | `ORG #8000` |
| `DEVICE target` | (SjASMPlus) Declare target hardware; enables paged-memory tracking | `DEVICE ZXSPECTRUM48`, `DEVICE ZXSPECTRUM128`, `DEVICE NEX` |
| `label EQU value` | Define a constant | `SCREEN_ADDR EQU #4000` |
| `DB` / `DEFB` | Emit one or more bytes | `DB "Hi", 0` |
| `DW` / `DEFW` | Emit one or more 16-bit words (little-endian) | `DW #4000, #5800` |
| `DS` / `DEFS` | Reserve N bytes (filled with value or zero) | `DS 32, 0` |
| `ALIGN n` | Pad to next boundary divisible by n | `ALIGN 256` |
| `INCLUDE "file"` | Pull in another source file | `INCLUDE "macros.asm"` |
| `SAVESNA "f.sna", entry` | Emit a 48K/128K snapshot file | `SAVESNA "demo.sna", start` |
| `SAVETAP "f.tap", entry` | Emit a tape image (with optional BASIC loader) | `SAVETAP "demo.tap", start` |

### Number Syntax

Z80 assembly has no single universal convention for hex literals. SjASMPlus accepts several — all of these mean the same byte:

```
#FF        ; Z80 convention (recommended, used throughout this knowledge base)
$FF        ; common alternative (Pasmo, vasm)
0FFh       ; Intel convention
0xFF       ; C convention (works in some assemblers, ambiguous with labels in others)
```

This knowledge base standardizes on `#FF` for hexadecimal, matching the convention used in [AGENTS.md](../../AGENTS.md) and the [Complete Spectrum ROM Disassembly](https://worldofspectrum.net/). Binary literals are written `01101010b` or `%01101010` (SjASMPlus accepts both). Decimal literals have no suffix: `LD A,16` loads sixteen.

### Syntax Differences Across Assemblers

The same logical program looks slightly different in SjASMPlus, z88dk-z80asm, and Pasmo. The table below shows the directives that differ:

| Feature | SjASMPlus | z88dk-z80asm | Pasmo |
|---|---|---|---|
| Hex literal | `#FE` or `$FE` | `0FEh` or `__FEH` | `$FE` or `0FEh` |
| Device declaration | `DEVICE ZXSPECTRUM48` | (not supported; flat 64 KB model) | (not supported) |
| Emit snapshot | `SAVESNA "x.sna", entry` | (use external `appmake`) | `--snap` flag at CLI |
| Emit tape | `SAVETAP "x.tap", entry` | (use external `appmake`) | `--tap` flag at CLI |
| Local labels | `loop:` | `.loop` (module-scoped) | `loop:` (file-scoped) |
| Macros | `MACRO name ... ENDM` | `MACRO name ... ENDM` | `MACRO name ... ENDM` |

If you copy code from a tutorial written for one assembler into another, expect to spend a few minutes on syntax conversion. The instruction mnemonics (`LD`, `ADD`, `JR`, `RET`, etc.) are universal — only the directives and literal conventions differ.

---

## Memory Map for the Programmer

Before writing any code, you need to know where to put it. The ZX Spectrum's 64 KB address space is divided into fixed regions, and not all of them are available to your program.

### 48K Memory Map

```
#FFFF ┌─────────────────────────────────────┐
      │  RAM bank 0 (contended)             │
      │  Top of free RAM                     │
      │  Stack grows down from #FF60         │
      │                                      │
      │  ─── Typical code load address ───   │
      │  #8000 (recommended for beginners)   │
      │                                      │
      │  ─── Free RAM for programs ───       │
      │  ~#5CCB upward                       │
      ├─────────────────────────────────────┤
#5B00 │  Attribute file (768 bytes)          │  #5AFF
#5800 ├─────────────────────────────────────┤
      │  Display file (6912 bytes)           │
      │  Pixel data, 256×192, 1 bit/pixel    │
#4000 ├─────────────────────────────────────┤
      │  System variables (182 bytes)        │  #5CB6
#5C00 │  (channels, streams, etc.)           │
      ├─────────────────────────────────────┤
      │  Printer buffer / free RAM           │
      │  (~#5CCB to top of free RAM)         │
      │                                      │
#4000 ├─────────────────────────────────────┤ ← RAM starts here
      │  ROM (16 KB, read-only)              │
      │  BASIC interpreter, editor, etc.     │
#0000 └─────────────────────────────────────┘
```

Key addresses, in roughly the order you will use them:

| Address | What lives there | Notes |
|---|---|---|
| `#0000`–`#3FFF` | **ROM** (16 KB) | Read-only. Writes are silently ignored. See [rom_48k.md](../../04_operating_systems/rom_48k.md) for the full disassembly. |
| `#4000`–`#57FF` | **Pixel framebuffer** (6144 bytes) | 256×192×1 bit. Bit set = ink, bit clear = paper. See [screen_layout.md](../03_memory_and_io/screen_layout.md). |
| `#5800`–`#5AFF` | **Attribute file** (768 bytes) | 32×24 attribute bytes: ink/paper/blink/bright. See same article. |
| `#5B00`–`#5BFF` | **Printer buffer** (256 bytes) | Reusable for code if printer not in use. |
| `#5C00`–`#5CB6` | **System variables** (182 bytes) | ROM workspace. Do not overwrite. See [system_variables.md](../../04_operating_systems/system_variables.md). |
| `#5CB7`–`#FF57` | **Free RAM** (~40 KB) | Where your program lives. |
| `#FF58`–`#FFFF` | **ROM workspace** (~167 bytes) | Used by the ROM; safe to use only if you do not return to BASIC. |

### Where to Put Your Code

The traditional load address for Spectrum assembly programs is **`#8000`** (decimal 32768). Three reasons:

1. **It is uncontended memory** — the ULA does not steal bus cycles here during screen refresh, so timing-sensitive code runs at predictable speed. See [ula_contention.md](../../02_hardware/original/ula_contention.md).
2. **It is well above the screen** — your code cannot accidentally corrupt the display file or system variables.
3. **It is below the stack** — the Z80 stack pointer initializes to roughly `#FF60` on a 48K machine and grows downward; loading at `#8000` gives ~32 KB before code and stack collide.

For 128K programs, the load address depends on which RAM bank is paged into the top slot (`#C000`–`#FFFF`). The convention is similar (`#8000`), but you must respect that the top 16 KB can be bank-switched. See [memory_and_io_128k.md](../03_memory_and_io/memory_and_io_128k.md).

### The Stack

The Z80 stack pointer (SP) is initialized by the ROM to roughly `#FF60` on a clean 48K boot. The stack grows **downward** — each `PUSH` decrements SP by 2, then writes. Each `POP` reads, then increments SP by 2. A program that pushes more data than it pops will eventually write below the load address of the program code, corrupting it.

Convention for assembly programs that take over the machine: set SP explicitly on entry to a known-safe address.

```z80
    DI                       ; disable interrupts (we will reuse the ISR area)
    LD   SP, #FFF0           ; stack now at top of RAM, growing down
```

See [stack_and_rst.md](stack_and_rst.md) for the full treatment of stack discipline.

---

## Hello World, Annotated

The minimal ZX Spectrum assembly program does three things: opens the screen output channel, prints a string, returns to BASIC. Twenty-five bytes of code, but every line is doing something fundamental.

```z80
    DEVICE ZXSPECTRUM48
    ORG  #8000

start:
    LD   A, 2                  ; 3D 02  - select stream 2 (main screen)
    CALL #1602                ; CD 02 16 - ROM routine OPEN_CHAN
    LD   HL, msg              ; 21 1C 80 - HL = address of msg
print_loop:
    LD   A, (HL)              ; 7E      - load next byte of msg
    AND  A                   ; A7      - set Z flag if A==0
    JR   Z, print_done       ; 28 04   - if zero, we are done
    RST  #10                 ; D7      - ROM routine PRINT_CHAR
    INC  HL                  ; 23      - advance to next byte
    JR   print_loop          ; 18 F7   - loop back
print_done:
    RET                      ; C9      - return to caller (BASIC)

msg:
    DB   "Hello, World!", #0D, #00

    SAVESNA "hello.sna", start
```

Save this as `hello.asm`. Assemble and run with:

```bash
sjasmplus hello.asm
fuse hello.sna
```

The Spectrum should briefly show the `(C) 1982 Sinclair Research Ltd` banner, then clear and print `Hello, World!` in the top-left, then return you to the BASIC cursor.

### Line-by-Line Walkthrough

**`DEVICE ZXSPECTRUM48`** — SjASMPlus directive. Declares the target hardware: the 48K Spectrum with 16 KB ROM, 48 KB RAM, no memory paging. SjASMPlus now knows that `#0000`–`#3FFF` is ROM (writes are errors), `#4000`–`#FFFF` is RAM, and `#4000`–`#5AFF` is the screen. Without this directive, SjASMPlus treats memory as a flat 64 KB array and cannot emit `.sna` snapshots.

**`ORG #8000`** — Tells SjASMPlus that the next instruction should be emitted at address `#8000` in the output binary. The instruction `LD A, 2` becomes the bytes `3E 02`, written at offset `#8000`. The label `start:` is assigned the value `#8000` and can be used elsewhere in the source as an immediate.

**`LD A, 2`** — Loads the constant 2 into the A register. The ROM's `OPEN_CHAN` routine at `#1602` reads A and uses it as a stream number: stream 0 is the keyboard, stream 1 is the lower screen (the bottom two lines used for input), stream 2 is the main screen (the upper 22 lines used for output). Without this call, `RST #10` would print to whatever stream was last opened — which, immediately after BASIC hands control, is the keyboard stream, and printing to the keyboard does nothing visible.

**`CALL #1602`** — Calls the ROM routine `OPEN_CHAN`. The ROM entry point address `#1602` is documented in [rom_routines.md](../../10_references/rom_routines.md). On return, the ROM has set internal state so that subsequent `RST #10` calls print to the main screen. The `CALL` instruction takes 17 T-states and 3 bytes.

**`LD HL, msg`** — Loads the address of the `msg` label into HL. The assembler resolves `msg` to `#801C` (the address at which the message bytes start). HL is now a 16-bit pointer into memory.

**`LD A, (HL)`** — Loads the byte at the address stored in HL into A. The first time through the loop, this is the ASCII code for `H` (which is `#48`).

**`AND A`** — Performs a bitwise AND of A with itself. The result is unchanged (A AND A = A), but the operation **sets the Z flag** based on the result: Z=1 if A is zero, Z=0 otherwise. The next instruction tests this flag. This is the idiomatic Z80 way to test whether A is zero without using `CP 0` (which costs one extra byte and T-state).

**`JR Z, print_done`** — "Jump Relative if Zero." If the Z flag is set, the CPU jumps forward to `print_done`. The `JR` instruction takes 12 T-states if the jump is taken, 7 if not. The operand `print_done` is resolved by the assembler to a relative offset (here, 4 bytes forward), encoded as a single signed byte.

**`RST #10`** — Calls the ROM routine at address `#0010`. `RST` (restart) is a one-byte call instruction; `RST #10` is encoded as the single byte `#D7`. The ROM routine at `#0010` is `PRINT_CHAR`, which prints the character whose ASCII code is in A to the currently-open stream. `RST` is faster than `CALL` (11 T-states vs 17, 1 byte vs 3) — useful in tight loops.

**`INC HL`** — Increments the 16-bit value in HL by one. HL now points to the next byte of the message.

**`JR print_loop`** — Unconditional relative jump back to the start of the loop.

**`RET`** — Returns from the subroutine. Since this program was entered via `RANDOMIZE USR #8000` from BASIC, RET pops the return address off the stack and returns control to the BASIC interpreter. If you wanted the program to loop forever instead, replace `RET` with `JR print_loop` (with the loop start renamed) or `HALT` (which freezes the CPU until an interrupt).

**`DB "Hello, World!", #0D, #00`** — `DB` (Define Byte) emits literal bytes. String literals produce one byte per character; numeric literals produce one byte each. The message is 13 characters of text, a carriage return (`#0D`, used by the ROM to advance to the next line), and a null terminator (`#00`, used by our loop to detect end-of-string).

**`SAVESNA "hello.sna", start`** — SjASMPlus directive that writes a 48K snapshot file. The snapshot format is documented in [snapshots.md](../../03_io/snapshots/). The first argument is the filename; the second is the entry point — SjASMPlus patches the snapshot's PC register to this address, so the emulator begins execution at `start` instead of at the BASIC editor.

### What This Program Demonstrates

Even this minimal example touches every major theme of ZX Spectrum assembly programming:

- **Calling the ROM** — `OPEN_CHAN` and `PRINT_CHAR` are two of the dozens of ROM routines documented in [rom_calls.md](rom_calls.md).
- **Register-based pointers** — HL is used as a pointer, the standard Z80 idiom. IX and IY can also serve as pointers but cost more bytes and T-states per access.
- **Loop construction** — `label: ... JR label` is the basic Z80 loop. `DJNZ` (decrement B and jump if nonzero) is faster but only works with B as the counter.
- **Flag-based branching** — `AND A` sets flags without changing A; `JR Z`/`JR NZ`/`JR C`/`JR NC` branch on flags. There is no `JZ` or `JNZ` — branching is always flag-based.
- **Restart vectors** — `RST #10` is one of eight single-byte call instructions (`RST #00` through `RST #38`, even addresses only). They are faster and shorter than `CALL`.
- **Memory as data** — The string lives in memory right after the code. There is no separate data segment; code and data share the same address space.

---

## Building a Binary

The pipeline from `.asm` source to running program in an emulator has several stages. The first stage — assembling — is always the same. The second stage — packaging — depends on which output format you want.

### Assembling

The basic SjASMPlus invocation:

```bash
sjasmplus hello.asm
```

By default this produces no output unless the source contains `SAVESNA`, `SAVETAP`, or similar directives. To see what is being generated:

```bash
sjasmplus --msg=war hello.asm     ; warnings and errors only
sjasmplus --msg=lst hello.asm     ; full listing to stdout
sjasmplus --sld=hello.sld.txt hello.asm   ; emit Source Level Debug data for DeZog
```

Common useful flags:

| Flag | Purpose |
|---|---|
| `--lst=file.lst` | Emit a listing file showing source, bytes, and addresses side by side. Essential for debugging. |
| `--sld=file.sld.txt` | Emit Source Level Data for DeZog and ZEsarUX debuggers. See [debugging.md](../../09_toolchain/debugging.md). |
| `--sym=file.sym` | Emit a symbol table (label = address) for emulators that consume it. |
| `--raw=file.bin` | Emit a raw binary (no header). Useful when you want to manage packaging yourself. |
| `-D NAME=value` | Define a preprocessor symbol (`IFDEF NAME` will be true). |
| `-I /path/to/inc` | Add a directory to the include search path. |

### Output Formats Compared

The ZX Spectrum ecosystem uses several binary formats. Each has tradeoffs:

| Format | Extension | What it is | When to use |
|---|---|---|---|
| **Snapshot** | `.sna` | A 48 KB or 128 KB dump of the entire Spectrum memory plus CPU registers. Loads instantly in any emulator. | Quick iteration during development. Not distributable to real hardware (no real-time loading mechanism). |
| **Tape image** | `.tap` | A tape-file container: a header block + a data block, exactly as if recorded from a cassette. | Testing the loading experience; distribution to real-hardware users with tape interfaces. |
| **Tape image (extended)** | `.tzx` | Enhanced tape format supporting custom loading schemes, speed locks, turbo loaders. | Demoscene releases that use non-standard loaders; preserving original tape loading speed and visuals. |
| **TR-DOS disk** | `.trd` | A disk image for the Beta Disk Interface (the standard Soviet-dominant floppy system). | Pentagon / Scorpion / +3 distribution. |
| **Raw binary** | `.bin` | Just the bytes of your code, with no header or address information. | When you want to package the code yourself (e.g., embed in a custom loader, or BLOAD from BASIC). |
| **ZX Spectrum Next** | `.nex` | Native executable format for the Next: header + code + optional Layer 2 image + bank setup. | Next-specific development. |

For learning, use `.sna`. For distribution, use `.tap` (Spectrum community standard) or `.trd` (Russian scene standard). For Next development, use `.nex`.

### The Build Script

A practical project will have a `Makefile` or shell script that handles assembly, optional post-processing, and emulator launch. Minimum viable `build.sh`:

```bash
#!/bin/sh
set -e
sjasmplus --lst=hello.lst --sym=hello.sym hello.asm
# hello.sna and hello.tap are emitted by SAVESNA/SAVETAP directives
fuse hello.sna
```

With a `Makefile`:

```makefile
hello.sna: hello.asm
	sjasmplus --lst=hello.lst --sym=hello.sym $<

run: hello.sna
	fuse hello.sna

clean:
	rm -f *.sna *.tap *.lst *.sym

.PHONY: run clean
```

For complex projects with multiple source files, see the modular structure section in [assembly_patterns.md](assembly_patterns.md).

---

## Loading SNA vs TAP vs TZX

The first time you build a program, you will encounter the question: which file format do I distribute? The short answer depends on whether you are testing in an emulator (use `.sna`), distributing to emulator users (use `.tap` or `.tzx`), or distributing to real-hardware users with a disk interface (use `.trd`).

### Snapshot Files (.sna)

A `.sna` file is a **complete dump** of the Spectrum's state at a moment in time. The 48K format is 49,179 bytes: a 27-byte header containing CPU registers (PC, SP, AF, BC, DE, HL, IX, IY, etc.), IFF1/IFF2, interrupt mode, and other one-byte state fields, followed by 48 KB of RAM. Loading a `.sna` is instant in every emulator.

SjASMPlus's `SAVESNA "file.sna", entry` directive produces a snapshot with PC set to `entry`, all other registers cleared, interrupts disabled, and the Spectrum's BASIC environment intact (so you can `RET` back to BASIC when done).

| Pros | Cons |
|---|---|
| Instant load in emulators | Not a real "program" — cannot be loaded from tape on real hardware |
| Full CPU state in 27-byte header | Cannot trigger the loading screen / custom loader effect |
| Best for development iteration | Some emulators handle the 128K `.sna` format differently — check compatibility |

### Tape Images (.tap)

A `.tap` file is a **container of tape blocks**. Each block is a 2-byte length prefix followed by a flag byte (0 for header, 255 for data), the payload, and a checksum byte. The Spectrum ROM's standard loader reads these blocks one at a time, displaying the characteristic striped border.

SjASMPlus's `SAVETAP "file.tap", entry` directive writes:

1. A **header block** (17 bytes): flag byte + 10 bytes filename + 1 byte type (Code=3) + 2 bytes length + 2 bytes load address.
2. A **data block** (the actual program bytes).
3. An optional **BASIC loader** block: a tokenized BASIC program that does `LOAD "" CODE : RANDOMIZE USR addr`.

| Pros | Cons |
|---|---|
| Standard Spectrum distribution format | Loading takes 5–30 seconds (depends on turbo) |
| Works with all emulators and real-hardware tape interfaces | Cannot include custom loading screens without ROM hacks |
| Familiar loading stripe effect | |

### Extended Tape Images (.tzx)

The `.tzx` format extends `.tap` with new block types for turbo loaders, custom ROM routines, synthetic audio patterns, and other tricks that real Spectrum software used to make loading faster and more interesting. SjASMPlus does not natively emit `.tzx`; use external tools like [TZX Tools](http://www.worldofspectrum.org/utilities.html) or the Rust `tzx` crate.

### TR-DOS Disk Images (.trd)

The `.trd` image is the standard disk format for the Beta Disk Interface and compatible controllers (the dominant disk system in the Soviet and post-Soviet scene). SjASMPlus's `SAVETRD "file.trd", "FILENAME.C", addr, length` directive writes a single file into an 80-track disk image, creating the image if needed. Distribution to Pentagon / Scorpion / +3 users goes via `.trd`.

### Picking a Format

| Your goal | Recommended format |
|---|---|
| Quick test in Fuse / ZEsarUX | `.sna` |
| Distribution to emulator users | `.tap` (Western scene) or `.trd` (Russian scene) |
| Demoscene release with custom loader | `.tzx` (use external tools) |
| Pentagon / Scorpion distribution | `.trd` |
| ZX Spectrum Next | `.nex` |
| Real-hardware via DivMMC / SD card | `.sna` (loadable by most SD interfaces) or `.tap` |

---

## First Debugging Session

The first program you write will not work. This is normal. The Z80 has no exceptions, no `printf`, no stack trace. If you are lucky, the program does nothing visible. If you are unlucky, the screen fills with garbage and the emulator hangs. If you are very unlucky, the program appears to work but produces subtly wrong output.

The Fuse debugger (Menu → Machine → Debugger, or `F1` from within the emulator) is your primary tool. Other emulators have equivalent windows.

### The Debugger Window

The Fuse debugger shows:

- **Registers pane**: AF, BC, DE, HL, AF', BC', DE', HL', IX, IY, SP, PC, I, R, plus the flag bits
- **Disassembly pane**: instructions around the current PC, with the current instruction highlighted
- **Memory pane**: hex dump of any address range
- **Breakpoints pane**: list of active breakpoints (address-based or conditional)

### A Debugging Workflow

For a program that does nothing visible:

1. Load the `.sna` in Fuse.
2. Open the debugger. The disassembly should be at your program's entry point (PC = `start`).
3. Set a breakpoint at `start` (in the disassembly, click on the address and press `F5`).
4. Step through instructions one at a time with `F7` (step into) or `F6` (step over). Each press executes one instruction.
5. After each step, verify: are the registers what you expected? Did HL get the right pointer? Did A get the right byte from memory?

For a program that crashes:

1. Reset the emulator (Machine → Reset).
2. Open the debugger.
3. Set breakpoints at suspicious addresses — typically the start of the program and any place where you call the ROM.
4. Run (`F9`) and let it crash. Note the value of PC when the crash happens. This is the address at which the CPU tried to execute garbage.
5. Look at the disassembly around PC: is it inside your code? Inside ROM? Inside screen memory? Each tells you something different:
   - **Inside your code but at a wrong offset**: a `JR` or `JP` had a bad target.
   - **Inside ROM (usually `#0000`–`#3FFF`)**: you executed a `RET` with an unbalanced stack. The popped return address was `#0000` or some other low value, and the CPU jumped to ROM, which executes the cold boot sequence.
   - **Inside screen memory (`#4000`–`#5AFF`)**: a wild pointer dereference. HL or IX/IY had a wrong value, and the CPU executed bytes from the screen.

### Common Bugs

| Symptom | Likely cause | How to diagnose |
|---|---|---|
| Program returns to BASIC immediately without printing | `RET` executed too soon, or never reached the loop body | Set breakpoint at start; single-step |
| Screen fills with vertical stripes | Stack imbalance, `RET` popped wrong address | Check SP before/after each `CALL`/`RST` |
| Program runs forever, no output | Loop termination wrong (zero-terminator never reached) | Set breakpoint inside the loop; check A and HL |
| Emulator freezes, must be reset | `DI` followed by `HALT` with no interrupts, or infinite loop in contended memory | Set breakpoint at program start; step into |
| Output appears but is wrong characters | String has wrong bytes, or wrong stream open | Dump memory at the string address; check `CURCHL` system variable |

### DeZog: Source-Level Debugging

For projects of any real size, step through the `.asm` source, not the disassembly. The DeZog VS Code extension connects to Fuse, ZEsarUX, CSpect, MAME, and other emulators and provides source-level debugging with breakpoints, watch variables, hover-to-inspect, and call stack. Setup is documented in [debugging.md § DeZog](../../09_toolchain/debugging.md). The minimal `.sld.txt` file produced by SjASMPlus's `--sld` flag is what DeZog consumes.

---

## When to Use Assembly vs C vs BASIC

ZX Spectrum development offers three primary languages. Each has its place.

| Criterion | Sinclair BASIC | Z80 Assembly | C (z88dk / SDCC) |
|---|---|---|---|
| **Development speed** | Fast (instant feedback, no compile step) | Slow (long edit-compile-test cycle) | Medium |
| **Execution speed** | ~100× slower than asm | Baseline (fastest) | ~1.5–3× slower than hand-written asm, depending on optimization |
| **Code density** | Low (tokenized, but verbose for complex logic) | High (manual register allocation) | Medium (compiler optimizes, but emits more instructions than hand-coded) |
| **Hardware access** | Limited (PEEK/POKE/OUT/IN only) | Direct, complete | Direct via inline asm or libraries |
| **Learning curve** | Low (already known to most users) | High (ISA + memory map + ROM internals) | Medium (C knowledge + Z80-specific quirks) |
| **Best for** | One-off utilities, small demos, learning the platform, loaders | Demos, games, anything requiring 50fps or direct hardware control | Large projects, porting existing C code, projects where the speed-critical surface is small |

### When to Choose BASIC

- You are learning the Spectrum and want to experiment quickly.
- The program is small (under ~100 lines) and speed is not critical.
- You need a loader for assembly code (the standard `LOAD "" CODE : RANDOMIZE USR` pattern).
- You are writing a turn-based game or puzzle where 50fps is irrelevant.

### When to Choose Assembly

- The program needs to hit 50fps (games, real-time animation).
- You need direct hardware access (raster sync, AY programming, port-level I/O).
- The program is small enough that assembly is manageable (typically under ~5,000 lines).
- You are learning the platform for its own sake.
- You want the program to fit in 1K, 4K, or 16K for a size-coding competition.

### When to Choose C

- The project is large enough that pure assembly becomes hard to maintain (typically over ~5,000 lines).
- Speed-critical code is a small fraction of the total (e.g., a game with mostly menu and state-machine logic, plus one tight inner loop for rendering).
- You want to share code between the Spectrum and other Z80 platforms (MSX, Amstrad CPC, RC2014).
- The team includes programmers who do not know Z80 assembly.

### The Mixed Approach

Most production software uses a mix. The recommended approach for medium-to-large projects:

1. Write the main loop, state machines, and game logic in C (z88dk with sccz80 or zsdcc).
2. Identify hot spots with the emulator's T-state profiler.
3. Rewrite hot spots in assembly, calling them from C.
4. Use inline assembly for one-instruction sequences (like `DI`/`EI`).

This workflow is the subject of [c_interop.md](c_interop.md).

---

## Pitfalls and Common Mistakes

### Pitfall 1: Forgetting to Open a Stream

```z80
; BAD: prints nothing
start:
    LD   A, 'H'
    RST  #10                  ; goes to keyboard stream by default
    RET
```

```z80
; GOOD
start:
    LD   A, 2
    CALL #1602                ; OPEN_CHAN: stream 2 = main screen
    LD   A, 'H'
    RST  #10
    RET
```

**Why**: After BASIC hands control to your code, the currently-open channel is the keyboard input stream. `RST #10` to the keyboard stream does nothing visible. You must `CALL #1602` with A=2 (or A=1 for the lower screen) before any `RST #10`.

### Pitfall 2: Wrong ORG

```z80
; BAD: code overwrites the system variables
    ORG  #5C00               ; this is the system variables area!
start:
    LD   A, 2
    ...
```

```z80
; GOOD
    ORG  #8000               ; safe high-RAM address
start:
    LD   A, 2
    ...
```

**Why**: `#5C00`–`#5CB6` is the system variables area. Writing your code there corrupts the ROM workspace, and the next ROM call will fail in unpredictable ways. Always use `#8000` or higher for the load address.

### Pitfall 3: Writing to ROM

```z80
; BAD: silently ignored, but the LD takes the same T-states
    LD   (#1234), A          ; #1234 is in ROM — write is dropped
```

```z80
; GOOD
    LD   (#8000), A          ; safe RAM address
```

**Why**: ROM is `#0000`–`#3FFF`. Writes are silently ignored — the byte is not stored, and the bus cycle still happens. The error is silent but the bug is real: any later read will get the old (ROM) value, not what you thought you wrote.

### Pitfall 4: Forgetting `RET`

```z80
; BAD: control falls through into the message bytes
start:
    LD   HL, msg
    LD   A, (HL)
    RST  #10
    ; ... no RET, no jump
msg:
    DB   "Hi", 0
```

```z80
; GOOD
start:
    LD   HL, msg
    LD   A, (HL)
    RST  #10
done:
    RET                      ; explicit return
msg:
    DB   "Hi", 0
```

**Why**: Without a `RET` (or unconditional `JR`/`JP`), the CPU continues executing whatever bytes come next. In this case, the bytes of the string `Hi` are decoded as instructions: `H` (`#48`) is `LD C,C`; `i` (`#69`) is `LD L,C`; the trailing zero is `NOP`. Execution wanders into garbage, typically crashing within a few hundred T-states.

### Pitfall 5: Little-Endian Addresses

```z80
; BAD: stored as #34 #12 in memory, treating as if big-endian
    LD   A, (#1234)          ; loads from #1234 — correct
    LD   HL, #1234
    LD   (HL), #34           ; NOT what you want
```

The Z80 is **little-endian**. A 16-bit value `#1234` is stored as the byte `#34` at the lower address and `#12` at the higher address. `DW #1234` emits the bytes `34 12` (low byte first). This catches programmers coming from big-endian platforms (68000, classic ARM, IBM mainframes).

```z80
; Manual construction of a 16-bit value in memory
    LD   HL, #1234           ; HL = #1234
    LD   (addr), HL          ; stores #34 at addr, #12 at addr+1
```

### Pitfall 6: Contended Memory Timing

Any code that runs in the address range `#4000`–`#7FFF` on the 48K (or `#C000`–`#FFFF` on contended banks of the 128K) is subject to **memory contention**: the ULA stalls the CPU during screen refresh to steal bus cycles. Tight timing loops in this region will be slower than expected. The fix is either to move time-critical code to uncontended memory (`#8000`–`#BFFF` on 48K) or to count contention cycles explicitly. See [ula_contention.md](../../02_hardware/original/ula_contention.md) for the contention model.

---

## Cross-References

- **[rom_calls.md](rom_calls.md)** — full cookbook of ROM entry points used from assembly
- **[stack_and_rst.md](stack_and_rst.md)** — stack discipline, RST vectors, calling conventions
- **[assembly_patterns.md](assembly_patterns.md)** — design patterns for assembly programs at scale
- **[assembly_optimization.md](assembly_optimization.md)** — performance optimization, T-state budgeting, lookup tables
- **[c_interop.md](c_interop.md)** — mixing C and assembly, calling conventions, project structure
- **[z80_instruction_set.md](../../01_cpu/z80_instruction_set.md)** — complete ISA reference
- **[z80_architecture.md](../../01_cpu/z80_architecture.md)** — register file, ALU, internal structure
- **[z80_timing.md](../../01_cpu/z80_timing.md)** — T-states for every instruction, contention model
- **[rom_48k.md](../../04_operating_systems/rom_48k.md)** — complete 48K ROM disassembly
- **[system_variables.md](../../04_operating_systems/system_variables.md)** — system variable reference
- **[sjasmplus.md](../../09_toolchain/sjasmplus.md)** — SjASMPlus assembler deep-dive
- **[debugging.md](../../09_toolchain/debugging.md)** — full debugger landscape
- **[ula_contention.md](../../02_hardware/original/ula_contention.md)** — memory contention deep dive

## References

- *The Complete Spectrum ROM Disassembly* by Ian Logan and Frank O'Hara — the canonical 48K ROM reference
- *Programming the Z80* by Rodnay Zaks — the canonical Z80 programming tutorial
- *The ZX Spectrum ULA: How to Design a Microcomputer* by Chris Smith — definitive ULA reference
- [SjASMPlus documentation](https://github.com/z00m128/sjasmplus/wiki)
- [World of Spectrum](https://spectrumcomputing.co.uk/) — software archive, hardware reference
- [breakintoprogram.co.uk](http://www.breakintoprogram.co.uk/hardware/computers/zx-spectrum/assembly-language) — modern assembly tutorial series
