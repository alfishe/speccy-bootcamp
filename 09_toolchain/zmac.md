[← Home](../README.md) · [Toolchain](README.md)

# zmac — The Classic Z80 Cross-Assembler

**zmac** is one of the oldest Z80 cross-assemblers still in regular use. Originally written in the late 1980s or early 1990s (sources differ on the exact date) for MS-DOS, zmac has since been ported to virtually every modern operating system. Its enduring appeal is its **simplicity, portability, and authenticity**: zmac source looks exactly like the assembly examples in 1980s Z80 documentation, and the tool is small enough to read in an afternoon.

For ZX Spectrum work, zmac is most commonly used to assemble **source recovered from disassemblies of classic 1980s games**. Many of the disassembly listings on GitHub ( Ultimate Play the Game, Ocean, Hewson Consultants, etc.) are written in zmac syntax because it closely matches the syntax those original programmers used with DevPac and GENS in the 1980s.

> [!NOTE]
> This article is the **per-tool reference** for zmac specifically. For the broader cross-assembler landscape, see [cross_platform_toolchain.md](cross_platform_toolchain.md).

---

## Quick Start

Install zmac (Debian/Ubuntu: `sudo apt install zmac`; macOS: build from source; from source: clone the [zmac repository](https://github.com/agz-zx/zmac) and run `make`).

Write `hello.z80`:

```z80
        org  #8000

start:  ld   hl, message
        call print_string
        ret

message:
        defm "Hello, World!"
        defb 0

print_string:
        ld   a, (hl)
        or   a
        ret  z
        rst  #10
        inc  hl
        jr   print_string
```

Assemble to a raw binary:

```bash
zmac hello.z80
```

Or with explicit output and binary:

```bash
zmac -o hello.bin --oo bin hello.z80
```

zmac's default output is a `.CIM` file (raw binary). The `--oo` flag selects the output format.

---

## History and Design Philosophy

zmac's origins are not entirely clear. The original MS-DOS version was circulating in the early 1990s, written by an author whose name is lost to history. The earliest widely-circulated version is 1.2 from around 1992. Russell Wallace released a major rewrite in 1998 (version 2.0), and Colin Douglas Howell maintained the modern branch from 2004 onward, adding the modern output formats and improving 8080 support.

zmac was designed for a different era:

- **Single-file source** — no linker, no object files
- **8080 + Z80 dual support** — useful for CP/M software
- **No macros** in the original, simple parameterised macros added later
- **No sections** — just one linear binary blob
- **No ZX Spectrum-specific features** — just an assembler

This makes zmac the **most conservative** of the major cross-assemblers. If you want a tool that works exactly like an assembler from 1992, zmac is it.

### Version History

| Year | Version | Author | Highlights |
|---|---|---|---|
| ~1992 | 1.0–1.2 | Unknown | Original MS-DOS release; 8080 + Z80 |
| 1998 | 2.0 | Russell Wallace | Major rewrite, portable C, multi-platform |
| 2004 | 2.5+ | Colin Douglas Howell | Modern maintenance; new output formats (`.tap`, `.tzx`) |
| 2010s | 2.7–2.9 | Colin Douglas Howell + community | Bug fixes; Z80N partial support added then removed |
| 2020s | 3.x | community (github.com/agz-zx/zmac) | Modern fork with new features |

### Maintained By

The current canonical home is **github.com/agz-zx/zmac** — a fork maintained by the AGZ (Another Game for ZX) community, which keeps the tool running on modern systems and adds small features as needed. The license is **GPL-2.0-or-later**, inherited from Russell Wallace's 1998 rewrite.

---

## Source Language

zmac uses a classic 1980s-era syntax that closely resembles the original Zilog notation. It supports both Z80 and Intel 8080 mnemonics.

### Number Formats

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `#` | `#FE`, `#4000` | Sinclair BASIC convention — **preferred for Spectrum work** |
| Hex with `$` | `$FE`, `$4000` | Zilog syntax |
| Hex with `0x` | `0xFE` | C syntax |
| Hex with `H` suffix | `0FEh`, `0FFh` | Must start with a digit |
| Binary with `B` suffix | `10101010b` | |
| Character | `'A'`, `"a"` | ASCII value |

All four hex syntaxes are accepted. zmac is unusual in that it accepts `#NN` (Sinclair style) by default, which makes porting Pasmo/SjASMPlus source easy.

### Comments and Identifiers

Comments start with `;`. Identifiers are case-sensitive by default (uppercase is traditional). Labels may be on their own line or share a line with an instruction.

### Operators

zmac has a minimal expression evaluator:

| Operator | Meaning |
|---|---|
| `+`, `-`, `*`, `/`, `%` | Arithmetic |
| `&`, `\|`, `^`, `~` | Bitwise AND/OR/XOR/NOT |
| `<<`, `>>` | Bitwise shifts |
| `<`, `>` | Low / high byte of expression (prefix) |
| `==`, `!=` | Equality (returns 0 or 1) |

Note the special `<` and `>` prefix operators — these return the low and high byte of an expression respectively. They are an old Zilog convention that pre-dates the `LOW()` / `HIGH()` function syntax used by modern assemblers.

### Directives

| Directive | Use |
|---|---|
| `ORG address` | Set assembly address |
| `EQU` | Define a constant: `BORDER_RED equ 2` |
| `= ` | Define a reassignable symbol |
| `DEFB b1, b2, ...` | Define bytes (also: `DB`) |
| `DEFW w1, w2, ...` | Define words, little-endian (also: `DW`) |
| `DEFL l1, l2, ...` | Define longs (32-bit) |
| `DEFS count [, fill]` | Define storage — emit `count` bytes of `fill` (also: `DS`) |
| `DEFM "text"` | Define message — bytes of the string (also: `DM`) |
| `TEXT "text"` | Same as `DEFM` |
| `ALIGN n` | Pad to multiple of `n` bytes |
| `PHASE address` / `DEPHASE` | Assemble as if at `address`, real cursor unchanged |
| `INCLUDE "file.asm"` | Include a source file |
| `INCBIN "file.bin" [, offset, count]` | Include a binary file |
| `IF expr` / `ELSE` / `ENDIF` | Conditional assembly |
| `IFDEF sym` / `IFNDEF sym` | Conditional assembly based on symbol definition |
| `phase` / `dephase` | Override ORG temporarily |

### Macros (Modern zmac)

Modern zmac (2.0+) supports parameterised macros:

```z80
        macro MUL_HL_BY_8
        sla   l
        rl    h
        sla   l
        rl    h
        sla   l
        rl    h
        endm

        ; Usage
        MUL_HL_BY_8
```

Parameterised macros are supported with `\1`, `\2`, etc., similar to Pasmo. zmac does **not** support IRP, REPT, recursive macros, or Lua scripting.

### 8080 Mode

With `--8080`, zmac accepts Intel 8080 mnemonics (`MVI A, 0` instead of `LD A, 0`, etc.). This is useful for working with CP/M source code or porting 8080 routines to Z80.

### Undocumented Z80 Instructions

zmac has long supported the well-known undocumented Z80 instructions: `SLI` (also `SLL`), `LD IXh`, `LD IXl`, `LD IYh`, `LD IYl`, `LD A, IXh`, `LD BC, (nn)` variants, etc. These are accepted silently by default. Use `--strict` to reject them.

---

## Command-Line Reference

| Flag | Use |
|---|---|
| `input.z80` | Source file |
| `-o output` | Output file name |
| `--oo FORMAT` | Output format: `bin` (raw), `cim` (raw, default), `tap`, `tzx`, `cdt`, `hex`, `obj`, `sln` (zmac object file) |
| `--8080` | Assemble 8080 instructions |
| `--z80` | Assemble Z80 instructions (default) |
| `--strict` | Reject undocumented Z80 instructions |
| `-P address` | Override the ORG address |
| `-n NAME` | Set the program name (for `.tap` headers) |
| `-D name[=value]` | Define a symbol |
| `-I dir` | Add `dir` to the include search path |
| `-z` | Disable warning messages |
| `--label ADDRESS` | Set the autostart address for `.tap` files |
| `--version` | Print version and exit |
| `--help` | Print usage and exit |

### Typical Command Lines

```bash
# Assemble to raw binary
zmac -o hello.cim hello.z80

# Assemble to Spectrum .tap with autostart
zmac --oo tap --label #8000 -o hello.tap hello.z80

# Assemble to TZX
zmac --oo tzx --label #8000 -o hello.tzx hello.z80

# Define a symbol at command line
zmac -D DEBUG=true -o hello.cim hello.z80
```

zmac is one of the few assemblers that produces `.tap` and `.tzx` directly, making it convenient for Spectrum development without additional tooling.

---

## When to Choose zmac

### Strengths

- **Direct `.tap` / `.tzx` output** — no need for `bin2tap` or `appmake` post-processing
- **All four hex syntaxes accepted** — easiest assembler for porting 1980s source
- **Undocumented Z80 instruction support** — works well with code recovered from disassembly
- **8080 mode** — useful for CP/M and cross-platform 8080/Z80 work
- **Tiny, fast, no dependencies** — single executable, builds in seconds
- **Authentic 1980s syntax** — matches what you see in old books and magazines

### Weaknesses

- **No multi-CPU support** (only Z80 + 8080)
- **No ZX Spectrum Next Z80N support**
- **No linker / object files** — single source file only
- **Limited macro language** — no IRP, REPT, recursion, or Lua scripting
- **GPL-2.0 license** — slightly less permissive than public-domain alternatives
- **The `--oo` interface is awkward** — the name `--oo` (output options) is unintuitive

### Comparison Matrix

| Feature | zmac | [Pasmo](pasmo.md) | [SjASMPlus](sjasmplus.md) | [z88dk z80asm](z88dk_z80asm.md) | [vasm](vasm.md) |
|---|---|---|---|---|---|
| Year started | 1990s | 2001 | 2004 | 1990s | 2002 |
| Hex `#NN` syntax | ✅ | ✅ | ✅ | ✅ | ❌ |
| Direct `.tap` / `.tzx` output | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| ZX Spectrum Next (Z80N) | ❌ | ❌ | ✅ | ✅ | ⚠️ |
| Undocumented Z80 (default) | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| 8080 mode | ✅ | ⚠️ | ❌ | ✅ | ✅ |
| Object files / linker | ⚠️ (`.sln`) | ❌ | ❌ | ✅ | ✅ |
| Macros (IRP, REPT) | ❌ | ❌ | ✅ | ✅ | ✅ |
| License | GPL-2+ | Public domain | BSD-2 | BSD-3 | MPL-2 |

### Decision Guide

Choose **zmac** when:
- You are assembling a disassembly of a 1980s game and want the syntax to match the original
- You want `.tap` / `.tzx` output directly
- You want to work with 8080 / CP/M source
- You want a minimal, no-frills, classic Z80 assembler

Choose **[Pasmo](pasmo.md)** when:
- You want the same minimal feel but slightly more modern features

Choose **[SjASMPlus](sjasmplus.md)** when:
- You need ZX Spectrum Next support
- You want powerful macros or Lua scripting

---

## Common Pitfalls

1. **Forgetting `--oo` for `.tap`** — without `--oo tap`, zmac produces a `.CIM` raw binary which most emulators will not load directly.

2. **`--label` for autostart** — when emitting `.tap`, you must specify the autostart address with `--label #8000`. Otherwise the loader has no `RANDOMIZE USR` line.

3. **Uppercase vs lowercase** — zmac is case-sensitive for labels by default. If you `ld a, (SomeLabel)` but defined `somelabel:`, you will get an undefined-symbol error.

4. **`<` and `>` prefix operators** — these return the low and high byte of an expression. They are NOT comparison operators in zmac. This is a frequent source of confusion when porting modern source.

5. **No multi-file support** — zmac cannot link multiple object files together. If you need multi-file projects, use `INCLUDE` to combine sources into one big file, or pick a different assembler.

6. **The default extension `.z80`** — zmac source often has the `.z80` extension, which conflicts with the `.z80` snapshot format. Pay attention to the file type when sharing files.

7. **`SLI` vs `SLL`** — zmac accepts both as the same undocumented instruction. Some other assemblers only accept one or the other.

---

## FAQ

**Q: What is a `.CIM` file?**

A: It's zmac's default output format — a raw binary with no header. The name comes from "core image". Load it into an emulator at the ORG address (e.g., `#8000`) or convert it to `.tap`.

**Q: Is zmac actively maintained?**

A: Conservatively. The community fork on GitHub (github.com/agz-zx/zmac) gets occasional updates. For most Spectrum work, the current version is fine.

**Q: Can zmac produce a 128K `.sna`?**

A: Not directly. Use `bin2sna` or `appmake` to convert zmac's raw binary into a snapshot.

**Q: Why does zmac use `.z80` as a source extension?**

A: Convention from the 1990s. The conflict with the `.z80` snapshot format is unfortunate but historical.

**Q: Does zmac support ZX Spectrum Next Z80N?**

A: No. For Next development, use [SjASMPlus](sjasmplus.md).

**Q: Can I use zmac for Game Boy development?**

A: No. zmac is Z80 + 8080 only. The Game Boy's LR35902 has different instructions; use WLA-DX's `wla-gb` or RGBDS.

---

## Cross-References

- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [pasmo.md](pasmo.md) — the closest modern alternative
- [sjasmplus.md](sjasmplus.md) — the Spectrum-focused alternative
- [z88dk_z80asm.md](z88dk_z80asm.md) — the z88dk-integrated alternative
- [vasm.md](vasm.md) — the portable multi-CPU alternative
- [wla_dx.md](wla_dx.md) — the linker-aware multi-CPU alternative
- [rasm.md](rasm.md) — the fast modern alternative (pending)
- [native_toolchain.md](native_toolchain.md) — native assemblers (whose syntax zmac mimics)

---

## References

- Russell Wallace — *zmac 2.0* original release (1998)
- Colin Douglas Howell — *zmac 2.x* maintenance releases
- AGZ community fork — [github.com/agz-zx/zmac](https://github.com/agz-zx/zmac)
- Linux distribution packages — `zmac` in Debian, Ubuntu
- GPL-2.0-or-later license — see `gpl.txt` in the zmac distribution
- World of Spectrum — disassembly listings that commonly use zmac syntax
