[← Home](../README.md) · [Toolchain](README.md)

# AS (Alfred Arnold's Macro Assembler) — The Comprehensive Multi-CPU Toolkit

**AS** is a powerful multi-CPU cross-assembler by **Alfred Arnold**, first released in 1990. Alongside [vasm](vasm.md) and [WLA-DX](wla_dx.md), AS is one of the "big three" portable multi-CPU assemblers. Its distinguishing feature is the **sheer breadth of CPU coverage**: AS supports over 30 CPU architectures, including Z80, Z80N, 6502, 65816, 6800, 6809, 68000, 68HC11, 8048, 8051, 8085, ARM, AVR, DS/PIC, COP8, 1802, H8/300, H8/500, Mitsubishi 740, Mitsubishi 7700, National HPC, SC/MP, SCC2692, STM8, SuperH, TLCS-90, TLCS-870, and more.

For ZX Spectrum development, AS is a niche choice — less common than [SjASMPlus](sjasmplus.md) or [Pasmo](pasmo.md), but with a loyal following in the **German retro-computing scene** (where Arnold is from) and among developers who work across many CPU architectures. AS also has a companion C compiler (`ASC`) and linker (`P2HEX`), making it a complete toolchain for embedded development.

> [!NOTE]
> This article covers **AS the macro assembler** (Alfred Arnold's tool). For the broader cross-assembler landscape, see [cross_platform_toolchain.md](cross_platform_toolchain.md).

---

## Quick Start

Install AS (Debian/Ubuntu: build from source per the [AS repository](https://github.com/alfredarnold/asn-aux); Windows: download from [the AS home page](http://john.ccac.rwth-aachen.de:8000/as/); macOS: build from source).

Write `hello.asm`:

```z80
        cpu z80
        org  $8000

start:  ld   hl, message
        call print_string
        ret

message:
        db   "Hello, World!", $0D, 0

print_string:
        ld   a, (hl)
        or   a
        ret  z
        rst  $10
        inc  hl
        jr   print_string

        end  start
```

Assemble:

```bash
asl -cpu z80 -L hello.asm
p2hex -r $8000-$FFFF hello.p hello.hex
```

AS uses a two-step process: `asl` assembles to a `.p` file, then `p2hex` converts to the final output format. For raw binary output, use `p2bin` instead of `p2hex`.

---

## History and Design Philosophy

Alfred Arnold started AS in 1990 while at the RWTH Aachen University of Technology. His original goal was to have a single assembler for the wide variety of CPUs he encountered in embedded systems consulting. AS's design principles:

- **One assembler, many CPUs** — add a CPU by writing a new table, not a new executable
- **Portable** — originally C for Amiga, later ported to DOS, Unix, macOS, and Windows
- **No dependencies** — single self-contained executable
- **Companion tools** — ASC (C compiler) and P2HEX/P2BIN (format converters) form a complete toolchain
- **Free for non-commercial use** — shareware-style license, registration required for commercial use

### Supported CPUs

AS supports an exceptionally wide range of CPU families. The most relevant for retro-computing:

| Family | Specific CPUs |
|---|---|
| Z80 family | Z80, Z80N (Spectrum Next), Z180/HD64180, Z380 |
| 6502 family | 6502, 65C02, 65816, 65EL02 |
| Motorola 6800 | 6800, 6801, 6809, 68HC11 |
| Motorola 68000 | 68000, 68020, 68030, 68040, 68060, ColdFire |
| Intel 8-bit | 8048, 8051, 8080, 8085 |
| ARM | ARM7, ARM9 |
| Atmel AVR | ATtiny, ATmega |
| Toshiba TLCS | TLCS-90, TLCS-870, TLCS-900 |
| Others | H8/300, H8/500, SC/MP, STM8, SuperH, Mitsubishi 740/7700, COP8, RCA 1802 |

For ZX Spectrum development, use `cpu z80` (standard) or `cpu z80n` (Spectrum Next).

### Version History

| Year | Version | Highlights |
|---|---|---|
| 1990 | 1.0 | First release; Z80, 6502, 68000, 8051 |
| 1995 | 1.40 | More CPUs; improved macro language |
| 2000 | 1.42 | P2HEX/P2BIN companions; Linux native build |
| 2010 | 1.42r3 | Z80N partial support; bug fixes |
| 2015 | 2.0 | Major rewrite; ASC companion C compiler |
| 2020s | 2.x | Active maintenance on GitHub |

### Maintained By

AS is primarily maintained by Alfred Arnold himself, now hosted on GitHub at **github.com/alfredarnold/asn-aux** and his university page at **john.ccac.rwth-aachen.de:8000/as/**. The license is free for non-commercial use; commercial users must register.

---

## Source Language

AS uses a clean, modern syntax with dot-led directives (`.org`, `.db`) and C-like expressions. The syntax is closer to WLA-DX and vasm than to Pasmo or SjASMPlus.

### Number Formats

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `$` | `$FE`, `$4000` | **Preferred** |
| Hex with `0x` | `0xFE` | C syntax |
| Hex with `H` suffix | `0FEh` | |
| Binary with `%` | `%10101010` | |
| Character | `'A'`, `"a"` | ASCII value |

AS does **not** accept `#NN` (Sinclair style). Use `$NN`.

### Operators

AS has a full C-like expression evaluator, including the same operator set as modern cross-assemblers: arithmetic, bitwise, comparison, logical, ternary (`?:`).

### Directives

| Directive | Use |
|---|---|
| `cpu NAME` | Select CPU (e.g., `cpu z80`) |
| `org address` | Set assembly address |
| `align n` | Pad to multiple of `n` bytes |
| `db b1, b2, ...` | Define bytes (also: `.byte`) |
| `dw w1, w2, ...` | Define words (also: `.word`) |
| `dl l1, l2, ...` | Define longs (32-bit) |
| `dc.b "text"` | Define string bytes |
| `ds count [, fill]` | Define storage |
| `section name` | Switch to a new section |
| `include "file"` | Include a source file |
| `incbin "file"` | Include a binary file |
| `if expr` / `else` / `endif` | Conditional assembly |
| `ifdef name` / `ifndef name` | Conditional on symbol definition |
| `function name(params)` ... `endfunction` | Assembly-time function |
| `macro name(params)` ... `endmacro` | Define a macro |
| `rept count` ... `endr` | Repeat block |
| `irp var, list` ... `endm` | Iterate over list |
| `end [label]` | End of source (optional label for entry point) |

### Macros

AS has a powerful macro language with named parameters, recursion, and assembly-time functions:

```z80
        macro mul_hl_by_8()
        sla   l
        rl    h
        sla   l
        rl    h
        sla   l
        rl    h
        endmacro

        ; Usage
        mul_hl_by_8()
```

#### Assembly-Time Functions

AS is unusual in supporting **assembly-time functions** — reusable code blocks that can return values:

```z80
        function is_even(n)
        return (n & 1) == 0
        endfunction

        if is_even(counter)
        ; even case
        else
        ; odd case
        endif
```

This feature goes beyond what most Z80 assemblers offer and approaches the power of Lua scripting in SjASMPlus.

### Structs and Sections

AS supports `struct` blocks and named sections for organized, multi-file projects. The syntax is close to WLA-DX.

### Sections

AS supports multiple named sections that the linker (P2HEX/P2BIN) can place independently. This is useful for 128K Spectrum projects where code lives in banked RAM:

```z80
        section code
main:   ; code here

        section bank1
sprites: ; data in bank 1

        section bank2
levels:  ; data in bank 2
```

---

## Command-Line and Workflow

AS uses a two-step build process:

1. **Assemble** with `asl` to produce a `.p` (code) file and optionally `.lst` (listing) and `.sym` (symbols)
2. **Convert** with `p2hex` (Intel HEX), `p2bin` (raw binary), or `p2file` (human-readable)

### `asl` Flags

| Flag | Use |
|---|---|
| `-cpu NAME` | Select CPU |
| `-L` | Include list file in output |
| `-S` | Include symbol file |
| `-D name=value` | Define a symbol |
| `-I dir` | Add include search path |
| `-i` | Case-insensitive labels |
| `-w N` | Set maximum warning count |
| `-shareware` | Acknowledge non-commercial use |
| `-verbose` | Print extra information |

### `p2hex` / `p2bin` Flags

| Flag | Use |
|---|---|
| `-r START-END` | Output range (which addresses to include) |
| `-o FILE` | Output file name |
| `-b OFFSET` | Add a fixed offset to all addresses |

### Typical Workflow

```bash
# Assemble
asl -cpu z80 -L -S hello.asm

# Convert to raw binary
p2bin -r $8000-$FFFF hello.p hello.bin

# Or convert to Intel HEX
p2hex -r $8000-$FFFF hello.p hello.hex

# Wrap into .tap for Spectrum
appmake +zx -b hello.bin -o hello.tap --org 32768
```

The two-step process (assemble then convert) is more verbose than SjASMPlus's single-step `--tap` output but gives fine-grained control over which address ranges to include in the output.

---

## When to Choose AS

### Strengths

- **Widest CPU coverage** — over 30 architectures from a single executable
- **Assembly-time functions** — a unique feature for compile-time computation
- **Companion C compiler (ASC)** — full embedded toolchain in one package
- **Active maintenance** — Alfred Arnold still maintains AS
- **Section-based multi-region output** — useful for banked targets
- **Free for non-commercial use**

### Weaknesses

- **No direct `.tap` / `.tzx` / `.sna` output** — must post-process with `appmake` or a custom script
- **`$NN` hex only** (no `#NN`)
- **Two-step build** — more complex workflow than single-step assemblers
- **Less known in the English-speaking Spectrum scene** — documentation is primarily in German
- **Non-commercial license** — commercial users must register

### Comparison Matrix

| Feature | AS | [vasm](vasm.md) | [WLA-DX](wla_dx.md) | [SjASMPlus](sjasmplus.md) | [Pasmo](pasmo.md) |
|---|---|---|---|---|---|
| Year started | 1990 | 2002 | 1998 | 2004 | 2001 |
| CPUs supported | 30+ | many | 12 | 1 (Z80N) | 1 |
| Assembly-time functions | ✅ | ❌ | ❌ | ✅ (Lua) | ❌ |
| Sections / multi-region | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| Direct `.tap` output | ❌ | ❌ | ❌ | ✅ | ✅ |
| Companion C compiler | ✅ (ASC) | ⚠️ (vbcc) | ❌ | ❌ | ❌ |
| License | Non-commercial free | MPL-2 | GPL-2+ | BSD-2 | Public domain |

### Decision Guide

Choose **AS** when:
- You work across many CPU architectures and want the widest coverage
- You need assembly-time functions for compile-time computation
- You want a companion C compiler (ASC)
- You work in embedded systems alongside retro computing

Choose **[vasm](vasm.md)** when:
- You want similar multi-CPU coverage with a cleaner license
- You prefer a single-step build process

Choose **[SjASMPlus](sjasmplus.md)** when:
- You target ZX Spectrum only
- You want `.tap` / `.sna` output directly

---

## Common Pitfalls

1. **Two-step build required** — you cannot get a `.bin` or `.tap` directly from `asl`. You must run `p2bin` or `p2hex` afterward.

2. **Hex syntax** — AS uses `$NN` only, not `#NN`.

3. **The `cpu` directive is mandatory** — without `cpu z80`, AS defaults to the last-used CPU (from a previous file) or fails.

4. **`-shareware` flag for non-commercial use** — some builds of AS require you to acknowledge the license with this flag. Without it, you get a nag message.

5. **Section placement is manual** — unlike WLA-DX's linker scripts, AS sections are placed in the order they are first declared. For complex layouts, use the `-r` flag in `p2bin`/`p2hex` to specify which ranges to output.

6. **No ZX Spectrum-specific output formats** — no `.tap`, `.tzx`, `.sna`, `.nex`. Pair with `appmake` from z88dk or a custom script.

7. **Z80N support is partial** — the major Spectrum Next instructions work, but some obscure ones may be missing. Check the latest release notes.

---

## FAQ

**Q: Is AS the same as GNU `as` (gas)?**

A: No. They are completely different tools. GNU `as` is the GNU Binutils assembler; AS is Alfred Arnold's macro assembler. They have different syntax, different feature sets, and different target audiences.

**Q: Where can I download AS?**

A: From [john.ccac.rwth-aachen.de:8000/as/](http://john.ccac.rwth-aachen.de:8000/as/) or the GitHub mirror at [github.com/alfredarnold/asn-aux](https://github.com/alfredarnold/asn-aux).

**Q: Can AS produce a `.tap` file directly?**

A: No. AS produces a `.p` code file that you convert with `p2bin` to raw binary. Then use `appmake` or `bin2tap` to wrap it in a `.tap`.

**Q: Is the ASC C compiler usable for Spectrum development?**

A: Yes, but it is less capable than z88dk for Spectrum-specific work. ASC targets embedded systems generally; z88dk has a much richer Spectrum library.

**Q: How does AS compare to vasm?**

A: Both are portable multi-CPU assemblers. AS supports more CPUs and has assembly-time functions. vasm has a cleaner license (MPL-2 vs. non-commercial) and is slightly faster. For ZX Spectrum-only work, neither is the best choice — use SjASMPlus.

**Q: Does AS support ZX Spectrum Next Z80N?**

A: Yes, with `cpu z80n`. The major Z80N instructions are supported.

---

## Cross-References

- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [vasm.md](vasm.md) — the closest comparable multi-CPU assembler
- [wla_dx.md](wla_dx.md) — another multi-CPU assembler with linker
- [sjasmplus.md](sjasmplus.md) — the Spectrum-focused alternative
- [pasmo.md](pasmo.md) — the simpler Z80-only alternative
- [z88dk_z80asm.md](z88dk_z80asm.md) — the z88dk-integrated alternative
- [tasm_cross.md](tasm_cross.md) — the legacy MS-DOS table-driven alternative
- [debugging.md](debugging.md) — debugging strategies

---

## References

- Alfred Arnold — *AS User's Manual*, [john.ccac.rwth-aachen.de:8000/as/](http://john.ccac.rwth-aachen.de:8000/as/)
- AS GitHub mirror — [github.com/alfredarnold/asn-aux](https://github.com/alfredarnold/asn-aux)
- ASC C compiler — included in the AS distribution
- P2HEX / P2BIN documentation — included in the AS distribution
- Non-commercial license — see `license.txt` in the AS distribution
