[← Home](../README.md) · [Toolchain](README.md)

# vasm — The Portable Modular Retargetable Assembler

**vasm** is a portable, modular, multi-CPU assembler written in C by Volker Barthelmann. Started in 2002 as part of the **vbcc** C compiler project, vasm has grown into one of the most general-purpose cross-assemblers available — it supports an unusually large set of CPU architectures (M68k, PowerPC, ARM, x86, Z80, 6502, 6809, H8/300, Jaguar DSP, Motorola DSP56k, Trimedia, Videocore, QNCE, RISC-V, and more) with a single executable. For ZX Spectrum development, the relevant CPU module is `z80` (and, to a lesser extent, the related `z84010`, `gameboy`, and `Rabbit` modules).

Whereas [Pasmo](pasmo.md) is intentionally minimal, and [SjASMPlus](sjasmplus.md) is highly Spectrum-specific, vasm takes the middle ground: a **clean, portable, syntax-driven macro assembler** that works the same way on all CPUs it supports. You give up some Spectrum-specific conveniences (no built-in `.tap` / `.tzx` / `.sna` output) in exchange for a tool you can reuse across many other retro platforms.

> [!NOTE]
> This article is the **per-tool reference** for vasm specifically. For the broader cross-assembler landscape, see [cross_platform_toolchain.md](cross_platform_toolchain.md).

---

## Quick Start

Install vasm (Debian/Ubuntu: `sudo apt install vasm` or build from source; macOS: `brew install vasm`; from source: clone the [vasm repository](http://sun.hasenbraten.de/vasm/) and run `make CPU=z80`).

Write `hello.asm`:

```z80
        org   $8000

start:  ld    hl, message
        call  print_string
        ret

message:
        dc.b  "Hello, World!", $0D, 0

print_string:
        ld    a, (hl)
        or    a
        ret   z
        rst   $10
        inc   hl
        jr    print_string
```

Assemble to a raw binary:

```bash
vasmz80 -Fbin -o hello.bin hello.asm
```

> [!IMPORTANT]
> vasm uses `$NN` for hexadecimal (Zilog style). The `#NN` syntax used by Pasmo and SjASMPlus is **not** accepted by vasm by default. See the [Number Formats](#number-formats) section for details.

---

## History and Design Philosophy

Volker Barthelmann, a German mathematician and Amiga scene veteran, started vasm in 2002 as the back-end of vbcc (his portable C compiler). The motivation was that existing C compiler back-ends for Z80 and M68k had idiosyncratic inline-assembly syntax, and there was no portable macro assembler that could serve both. vasm was designed to be:

- **Modular** — a single syntax module (e.g., Motorola syntax, Zilog syntax, standard syntax) plugs into a single CPU module (e.g., M68k, Z80, 6502)
- **Portable** — pure ANSI C, builds on any platform with a C89 compiler
- **No external dependencies** — single executable, no runtime libraries
- **Open source** — MPL 2.0 license (free for any use, including commercial)

### Architecture

vasm is structured as a three-layer stack:

1. **CPU modules** — one per architecture (`cpu_m68k.c`, `cpu_z80.c`, `cpu_6502.c`, etc.). These know the binary encodings.
2. **Syntax modules** — one per input syntax style (`syntax_mot.c` for Motorola-style, `syntax_std.c` for standard macro assembler style, `syntax_oldstyle.c` for the original Devpac-compatible dialect).
3. **Output modules** — one per output format (`output_bin.c` for raw binary, `output_aout.c`, `output_elf.c`, `output_hunk.c`, `output_tos.c`, etc.).

You choose these at compile time, which is why vasm ships as separate binaries: `vasmm68k`, `vasmz80`, `vasm6502`, etc. Each is a small executable optimized for its CPU.

### Version History

| Year | Version | Highlights |
|---|---|---|
| 2002 | 0.1 | First public release; M68k + Z80 CPUs, Motorola + standard syntax |
| 2006 | 1.0 | Stable; more CPUs (PowerPC, ARM); ELF output |
| 2010 | 1.2 | Rabbit, Jaguar DSP; improved macros |
| 2015 | 1.5 | RISC-V CPU module; bug-fix focus |
| 2020 | 1.8 | Modern maintenance; Z80N partial support |
| 2020s | ongoing | Active maintenance by Volker Barthelmann and Frank Wille |

vasm's release model is conservative — features are added carefully, and bug-fix-only releases are frequent.

### Maintained By

vasm is primarily maintained by **Volker Barthelmann** with significant contributions by **Frank Wille**. Both are long-time Amiga/M68k scene developers. The project is hosted on Barthelmann's personal website at [sun.hasenbraten.de/vasm/](http://sun.hasenbraten.de/vasm/) with mirrors on GitHub.

---

## Source Language

vasm supports two syntax modules of interest for Z80 development:

- **`syntax_std`** (standard macro assembler syntax) — the default for vasmz80; resembles WLA-DX and other modern macro assemblers
- **`syntax_mot`** (Motorola syntax) — useful when porting Amiga M68k macros, but rarely used for Z80
- **`syntax_oldstyle`** — Devpac-compatible, mainly for retro M68k code

For Z80 Spectrum work, `syntax_std` (the default) is the right choice.

### Number Formats

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `$` | `$FE`, `$4000` | Zilog syntax — **default and preferred** |
| Hex with `0x` | `0xFE` | C syntax |
| Hex with `H` suffix | `0FEh`, `0FFh` | Must start with a digit |
| Binary with `B` suffix | `10101010b` | |
| Binary with `%` | `%10101010` | |
| Character | `'A'`, `"a"` | ASCII value |

> [!WARNING]
> vasm does **not** accept `#FE` (Pasmo/SjASMPlus style) for hexadecimal. `#` is instead used for **immediate addressing** in some syntax modules, and for **comments** in others. Always use `$FE` in vasm Z80 source.

### Comments

| Style | Syntax | Use |
|---|---|---|
| Line comment (standard) | `;` | Default — to end of line |
| Line comment (alternative) | `*` in column 1 | Devpac-style |
| Block comment | `/* ... */` | Multi-line; standard syntax only |

### Operators

vasm has a full C-like expression evaluator:

| Operator | Meaning |
|---|---|
| `+`, `-`, `*`, `/`, `%` | Arithmetic |
| `<<`, `>>` | Bitwise shifts |
| `&`, `\|`, `^`, `~` | Bitwise AND/OR/XOR/NOT |
| `<`, `>`, `<=`, `>=`, `==`, `!=` | Comparison (returns 0 or 1) |
| `&&`, `\|\|`, `!` | Logical AND/OR/NOT |
| `?:` | Conditional (ternary) |

### Built-in Functions

| Function | Returns |
|---|---|
| `lo(x)` | Low byte of `x` |
| `hi(x)` | High byte of `x` |
| `defined(name)` | 1 if symbol is defined, 0 otherwise |
| `strlen("text")` | String length |
| `sizeof(name)` | Size of a section or structure |

### Sections

vasm supports named sections that the linker (`vlink`) assigns final addresses:

```z80
        section code, align=256
clear_screen:
        ; ... implementation

        section data
screen_buffer:
        ds    6912

        section bss
scratch_var:
        ds    1
```

When you assemble to a single binary (`-Fbin`), sections are concatenated in declaration order. When you emit object files (`-Fobj`) and link with `vlink`, sections can be placed independently.

### Directives

vasm directives are case-insensitive and dot-led (`.org`) or non-dot (`org`) — both accepted.

#### Code Placement

| Directive | Use |
|---|---|
| `org address` | Set assembly address |
| `align n` | Pad to multiple of `n` bytes |
| `phase address` | Assemble as if at `address`, real cursor unchanged (for overlays) |
| `dephase` | End a `phase` block |

#### Data Definitions

| Directive | Use |
|---|---|
| `dc.b value [, value ...]` | Define constant bytes (also: `dc`, `db`) |
| `dc.w value [, value ...]` | Define constant words |
| `dc.l value [, value ...]` | Define constant long (32-bit) |
| `dc.d value [, value ...]` | Define constant double (64-bit) |
| `dcb.b count, fill` | Define constant block — emit `fill` byte `count` times (also: `ds`, `fill`) |
| `dc.b "text"` | Define string — bytes of the string, no terminator |

vasm uses the **Motorola-flavoured** directive names (`dc.b` for "define constant.byte"). This is one of the most obvious differences from Pasmo, which uses `db`.

#### Includes

| Directive | Use |
|---|---|
| `include "file.asm"` | Include a source file inline |
| `incbin "file.bin" [, offset, count]` | Include a binary file as bytes; optionally skip `offset` bytes and include only `count` |

#### Conditional Assembly

```z80
        ifd  DEBUG_BUILD
        ; debug-only code
        endc

        ifnd TARGET_48K
        fail "This source requires the 48K target"
        endc
```

### Macros

vasm's macro system is powerful and supports recursive expansion, IRP/IRPC/REPT, named parameters, local labels, and macro-time conditionals:

```z80
        macro CLEAR_N count
        ld    (hl), 0
        ld    b, \count - 1
.loop:
        inc   hl
        ld    (hl), 0
        djnz  .loop
        endm
```

#### Repeat and Iterate

```z80
        ; Unroll a 4-iteration loop
        rept  4
        sla   l
        rl    h
        endr

        ; Iterate over a comma-separated list of values
        irp   reg, <a, b, c, d>
        ld    \reg, 0
        endm

        ; Iterate over the characters of a string
        irpc  ch, ABCD
        dc.b  '\ch' - 'A'
        endm
```

This is the **same macro language** used by Amiga M68k assemblers, which is a strength if you write cross-platform code or port routines between Z80 and 68000.

---

## Output Formats and Command-Line Reference

vasm uses the `-F` flag to select the output format. The format names depend on the build configuration, but the commonly available ones for Z80 work:

| Flag | Output | Use |
|---|---|---|
| `-Fbin` | Raw binary | Most common for Spectrum — produce a `.bin` to load or wrap in a `.tap` |
| `-Fobj` | vasm object file | For linking with `vlink` |
| `-Fhunk` | Amiga Hunk format | Useful only if you are working with Amiga tools |
| `-Faout` | a.out | Legacy Unix object format |
| `-Felf` | ELF | Modern Unix object format |
| `-Ftos` | Atari TOS | Atari ST executable |
| `-Fieee` | IEEE-695 | Old standard object format |

For Spectrum development, **`-Fbin` is essentially the only output format you will use** from `vasmz80`. There is no built-in `.tap`, `.tzx`, or `.sna` output — for those, post-process with a separate tool (e.g., `bin2tap`, `appmake` from z88dk, or write a small Python script).

### Common Command-Line Flags

| Flag | Use |
|---|---|
| `input.asm` | Source file (only one per invocation by default) |
| `-o output` | Output file name |
| `-Fbin` / `-Fobj` / etc. | Select output format |
| `-I dir` | Add `dir` to the include search path |
| `-D name[=value]` | Define a symbol at the command line |
| `-U name` | Undefine a symbol |
| `-no-macro-override` | Disallow macros from overriding instructions |
| `-align` | Enable section alignment (off by default) |
| `-no-opt` | Disable all assembly-time optimizations |
| `-werror` | Treat warnings as errors |
| `-nowarn=NNN` | Suppress warning number NNN |
| `-quiet` | Suppress informational output |
| `-verbose` | Print extra debugging information |
| `-version` | Print version and exit |

### Typical Command Lines

```bash
# Assemble to raw binary
vasmz80 -Fbin -o hello.bin hello.asm

# Assemble with a define
vasmz80 -Fbin -D DEBUG_BUILD -o hello.bin hello.asm

# Assemble to object file (then link with vlink)
vasmz80 -Fobj -o hello.o hello.asm

# Include a search path for headers
vasmz80 -Fbin -I include/ -o hello.bin hello.asm
```

### vlink: The Companion Linker

For multi-file projects, vasm pairs with **vlink**, another Volker Barthelmann tool. vlink understands vasm object files (`-Fobj`) and links them with section placement and symbol resolution:

```bash
# Assemble multiple objects
vasmz80 -Fobj -o main.o main.asm
vasmz80 -Fobj -o screen.o screen.asm

# Link
vlink -b rawbin1 -o program.bin main.o screen.o
```

vlink supports many output formats: raw binary, ELF, Amiga Hunk, Atari TOS, MS-DOS COM, and more. The linker script can specify section placement at specific addresses.

---

## When to Choose vasm

### Strengths

- **Portable** — pure ANSI C, builds on any system with a C89 compiler
- **Multi-CPU** — single toolchain for Z80, M68k, 6502, ARM, RISC-V, and many more
- **Powerful macro system** — recursive, IRP, IRPC, REPT, named parameters
- **Devpac-compatible Motorola syntax** — porting Amiga M68k macros is straightforward
- **Object-file output with vlink** — multi-file projects with section placement
- **MPL 2.0 license** — free for any use, including commercial
- **Active maintenance** — Volker Barthelmann and Frank Wille are still improving it

### Weaknesses

- **No native `.tap` / `.tzx` / `.sna` output** — must post-process with another tool
- **`$NN` hex only** (no `#NN`) — friction when porting SjASMPlus or Pasmo source
- **No ZX Spectrum Next Z80N support** (or only partial, depending on version)
- **Steeper learning curve** than Pasmo or SjASMPlus due to abstract module system
- **Z80 CPU module lags M68k in features** — the M68k module is the canonical one, Z80 is secondary

### Comparison Matrix

| Feature | vasm | [Pasmo](pasmo.md) | [SjASMPlus](sjasmplus.md) | [z88dk z80asm](z88dk_z80asm.md) | [WLA-DX](wla_dx.md) |
|---|---|---|---|---|---|
| Year started | 2002 | 2001 | 2004 | 1990s | 1990s |
| Multi-CPU support | ✅ (many) | ❌ | ⚠️ (Z80N) | ✅ | ✅ |
| Hex `$NN` syntax | ✅ (preferred) | ✅ | ✅ | ✅ | ✅ |
| Hex `#NN` syntax | ❌ | ✅ | ✅ | ✅ | ❌ |
| Recursive macros | ✅ | ❌ | ✅ | ⚠️ | ✅ |
| IRP / REPT / IRPC | ✅ | ❌ | ✅ | ✅ | ✅ |
| Spectrum-specific output (`.tap`/`.tzx`/`.sna`) | ❌ | ✅ | ✅ | ⚠️ (via `appmake`) | ❌ |
| Z80N (Next) support | ⚠️ | ❌ | ✅ | ✅ | ❌ |
| Standalone linker (`vlink`) | ✅ | ❌ | ❌ | ✅ | ✅ |
| License | MPL-2 | Public domain | BSD-2 | BSD-3 | GPL |

### Decision Guide

Choose **vasm** when:
- You work on multiple CPU platforms and want one toolchain
- You need powerful macros with recursion, IRP, REPT
- You are porting Amiga M68k code (the Motorola syntax module makes this easy)
- You need a clean, portable, license-friendly assembler for a commercial project

Choose **[Pasmo](pasmo.md)** when:
- You want `.tap` output directly
- You want minimal dependencies
- You use `#NN` hex syntax

Choose **[SjASMPlus](sjasmplus.md)** when:
- You target ZX Spectrum Next (`Z80N`)
- You want Spectrum-specific output (`.nex`, `.trd`)
- You want Lua scripting

---

## Spectrum-Specific Workflow

Since vasm does not emit `.tap` directly, Spectrum developers usually pair it with a small wrapper script. Here is a typical Makefile:

```make
all: hello.tap

hello.bin: hello.asm
        vasmz80 -Fbin -I include/ -o $@ $<

hello.tap: hello.bin
        bin2tap -org #8000 -start #8000 $< $@

clean:
        rm -f *.bin *.tap
```

Where `bin2tap` is a small utility that wraps a raw binary into a Spectrum `.tap` with a basic-loader block. Several implementations exist; the most common is part of the **fuse-utils** package (`fuse-emulator-utils` on Debian/Ubuntu, `brew install fuse-utils` on macOS).

Alternatively, you can use z88dk's `appmake`:

```bash
vasmz80 -Fbin -o hello.bin hello.asm
appmake +zx -b hello.bin -o hello.tap --org 32768
```

---

## Common Pitfalls

1. **Using `#NN` hex syntax** — vasm rejects this. Always use `$NN` (or `0FEh`). If you are porting SjASMPlus source, you must convert all hex literals.

2. **Using `db` directive** — vasm uses `dc.b`. If you write `db 1, 2, 3`, vasm will treat `db` as a label name and fail. This is a common gotcha when porting Pasmo source.

3. **Forgetting `-Fbin`** — without an output format flag, vasm may default to a strange format on some builds. Always specify `-Fbin` explicitly for raw binary output.

4. **Comments starting with `#`** — in vasm standard syntax, `#` is not a comment character (it is sometimes used for immediate addressing in M68k context). Use `;` for comments.

5. **No `.tap` output** — vasm users new to Spectrum development often expect to find a `-tap` flag. There isn't one. Pair vasm with `bin2tap`, `appmake`, or a custom Python script.

6. **Single source file per invocation** — by default, vasm processes one source file. To combine multiple files, use `include` inside the source or link multiple object files with `vlink`.

7. **Section ordering in `-Fbin`** — sections are emitted in the order they are first declared, not in the order of code appearance. If you need a specific layout, either declare sections in the desired order or use `vlink` with a linker script.

---

## FAQ

**Q: Is vasm the same as vasm68k?**

A: `vasm` is the project name. `vasm68k` and `vasmz80` are different builds of the same source, compiled with different CPU modules. Once installed, you invoke the specific build for your target CPU.

**Q: Can vasm produce a Spectrum `.sna` snapshot directly?**

A: No. Use a separate tool like `bin2sna` (Python) or z88dk's `appmake +zx -b file.bin --sna`.

**Q: Does vasm support undocumented Z80 instructions (`SLI`, `LD IXh`, etc.)?**

A: Yes, vasm supports the well-known undocumented instructions (`SLI` is a documented alias for `SLL`). They are accepted with a warning by default.

**Q: Why doesn't vasm have a `.tap` output format like Pasmo does?**

A: vasm is CPU-agnostic and platform-agnostic. The `.tap` format is Spectrum-specific. vasm's philosophy is to produce a portable binary and let platform-specific tools handle platform-specific formats. This is consistent with the Unix philosophy.

**Q: Can I use vasm with z88dk?**

A: Yes, indirectly. vasm can produce `.bin` files that z88dk's `appmake` can wrap into `.tap`. However, z88dk's own z80asm is the better choice inside the z88dk toolchain (it produces object files compatible with z88dk's linker).

**Q: Is there a VS Code extension for vasm?**

A: Not specifically. The Z80 Macro Assembler extension (designed for SjASMPlus-like syntax) will provide some highlighting but may not handle vasm-specific directives perfectly. For best results, define your own syntax file or accept generic Z80 highlighting.

**Q: How do I debug vasm output at source level?**

A: vasm does not emit a symbol file in DeZog-compatible format directly. Use a script to convert vasm's symbol file to DeZog's `.labels` format, or use an emulator's built-in disassembler. See [debugging.md](debugging.md) for general strategies.

---

## Cross-References

- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [pasmo.md](pasmo.md) — the simpler Z80-only alternative
- [sjasmplus.md](sjasmplus.md) — the Spectrum-focused alternative with `.tap` output
- [z88dk_z80asm.md](z88dk_z80asm.md) — the z88dk-integrated alternative
- [wla_dx.md](wla_dx.md) — another portable cross-platform assembler (pending)
- [zmac.md](zmac.md) — classic cross-assembler (pending)
- [debugging.md](debugging.md) — source-level debugging workflows
- [vscode_integration.md](vscode_integration.md) — IDE setup

---

## References

- Volker Barthelmann — *vasm home page*, [sun.hasenbraten.de/vasm/](http://sun.hasenbraten.de/vasm/)
- vlink home page — [sun.hasenbraten.de/vlink/](http://sun.hasenbraten.de/vlink/)
- vbcc C compiler — [www.compilers.de/vbcc.html](https://www.compilers.de/vbcc.html)
- vasm GitHub mirror — [github.com/AmigaLemos/vasm](https://github.com/AmigaLemos/vasm)
- fuse-utils (for `bin2tap`) — [fuse-emulator.sourceforge.net](https://fuse-emulator.sourceforge.net/)
