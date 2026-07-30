[← Home](../README.md) · [Toolchain](README.md)

# RASM — The Fast Modern Z80 Cross-Assembler

**RASM** (Rasm Assembler) is a fast, modern Z80 cross-assembler by Roudoudou (a French demoscene developer), first released in 2016. Its primary design goals are **raw assembly speed** and **comfortable modern syntax**. RASM is reportedly the fastest Z80 assembler available — capable of assembling large multi-bank projects (hundreds of KB of source) in well under a second.

For ZX Spectrum work, RASM is most popular with the **French demoscene** and with developers building large multi-bank projects (128K demos, RPGs, movie-players). It is less well-known in the English-speaking Spectrum community than SjASMPlus or Pasmo, but its speed, modern macro language, and built-in ZX Spectrum output formats make it a credible alternative.

> [!NOTE]
> This article is the **per-tool reference** for RASM specifically. For the broader cross-assembler landscape, see [cross_platform_toolchain.md](cross_platform_toolchain.md).

---

## Quick Start

Install RASM (build from source per the [RASM repository](https://github.com/eduardommu/rasm); pre-built binaries are also available from [Roudoudou's site](http://www.logiciels-cepe.com/rasm/rasm.html)).

Write `hello.asm`:

```z80
        org  #8000

start:  ld   hl, message
        call print_string
        ret

message:
        db   "Hello, World!", #0D, 0

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
rasm hello.asm
```

Or to a Spectrum snapshot:

```bash
rasm hello.asm -o hello -sna
```

RASM is fast: even a 10000-line source will assemble in under 200ms on modern hardware.

---

## History and Design Philosophy

Roudoudou (real name not widely publicised; he is well-known in the French Spectrum and Amstrad CPC demoscenes) started RASM in 2016 to address two frustrations with existing cross-assemblers:

1. **SjASMPlus was too slow** for his large multi-bank projects (especially CPC demos with megabytes of asset data).
2. **Macro languages were too primitive** for the code-generation patterns he needed (procedural tile generation, audio sample tables, etc.).

RASM was designed from the start for **speed**. It uses a hand-written recursive-descent parser, careful memory layout, and aggressive caching of intermediate results. The result is dramatic: RASM can assemble the same source in tens of milliseconds that takes SjASMPlus a second or more.

RASM is also designed for **French Spectrum and Amstrad CPC conventions**, including:

- Output formats specific to the CPC and Plus machines (in addition to Spectrum formats)
- Default `#NN` hex syntax (matches French retro conventions)
- Strong support for banked-memory targets

### Version History

| Year | Version | Highlights |
|---|---|---|
| 2016 | 1.0 | First release; raw binary + Spectrum snapshot output |
| 2017 | 1.1 | CPC support; macro language enhancements |
| 2018 | 1.2 | TZX, TAP output; bug fixes |
| 2020 | 2.0 | Major rewrite; multi-section support; faster |
| 2022 | 2.x | Continuous improvement; ZX Spectrum Next Z80N partial support |
| 2020s | ongoing | Active maintenance by Roudoudou and community |

### Maintained By

RASM is primarily a single-author project (Roudoudou) with community contributions. It is hosted on GitHub at **github.com/eduardommu/rasm** (a mirror) and on Roudoudou's personal site. The license is **MIT** — very permissive.

---

## Source Language

RASM's syntax is close to SjASMPlus (modern, dot-optional directives, `#NN` hex). This is intentional — easy migration between the two tools.

### Number Formats

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `#` | `#FE`, `#4000` | **Preferred** |
| Hex with `$` | `$FE` | Zilog syntax |
| Hex with `0x` | `0xFE` | C syntax |
| Hex with `H` suffix | `0FEh` | |
| Binary with `%` | `%10101010` | |
| Character | `'A'`, `"a"` | ASCII value |

### Operators and Built-in Functions

RASM has a complete expression evaluator with C-like operators (`+`, `-`, `*`, `/`, `%`, `<<`, `>>`, `&`, `|`, `^`, `~`, `<`, `>`, `<=`, `>=`, `==`, `!=`, `&&`, `||`, `!`, `?:`). Built-in functions include:

| Function | Returns |
|---|---|
| `lo(x)` / `low(x)` | Low byte of `x` |
| `hi(x)` / `high(x)` | High byte of `x` |
| `defined(name)` | 1 if symbol exists |
| `sizeof(name)` | Size of a section or struct |
| `addr(name)` | Address of a symbol |

### Directives

RASM uses non-dot directive names by default (`org`, `db`, `if`); dot forms (`.org`, `.db`, `.if`) are also accepted.

| Directive | Use |
|---|---|
| `org address` | Set assembly address |
| `align n` | Pad to multiple of `n` bytes |
| `limit address` | Set a maximum assembly address (warn if exceeded) |
| `db b1, b2, ...` | Define bytes |
| `dw w1, w2, ...` | Define words, little-endian |
| `dd l1, l2, ...` | Define longs (32-bit) |
| `ds count [, fill]` | Define storage |
| `dm "text"` | Define message bytes |
| `str "text"` | Define string with length prefix |
| `phase address` / `dephase` | Override ORG temporarily |
| `section name` | Switch to a new section |
| `include "file.asm"` | Include a source file |
| `incbin "file.bin"` | Include a binary file |
| `binary "file.bin"` | Same as `incbin` |
| `if expr` / `else` / `endif` | Conditional assembly |
| `ifdef sym` / `ifndef sym` | Conditional on symbol existence |
| `for var, start, end [, step]` / `next` | C-style for loop in assembly-time |
| `rept count` / `endr` | Repeat block |
| `irp var, list` / `endm` | Iterate over list |
| `define name value` | Define a symbol |
| `undef name` | Undefine a symbol |

### Macros

RASM's macro language is its strongest feature. It supports parameterised macros, local labels, recursion (with depth limits), and named parameters:

```z80
        macro CLEAR_N count
        ld   (hl), 0
        ld   b, \count - 1
.clear_loop:
        inc  hl
        ld   (hl), 0
        djnz .clear_loop
        endm
```

#### For Loops at Assembly Time

```z80
        ; Generate a sine table
        for  angle, 0, 255
        db   (sin(angle * 2 * 3.14 / 256) + 1) * 127
        next
```

This kind of assembly-time computation is unusual among Z80 assemblers and is one of RASM's standout features.

### Sections and Multi-Bank Projects

RASM supports named sections and bank-aware assembly:

```z80
        bank 0, #c000
        section code
main:   ; ... code in bank 0

        bank 1, #c000
        section data
sprites: ; ... data in bank 1
```

This makes RASM particularly well-suited for 128K demos, RPGs, and any project with multiple RAM banks.

### ZX Spectrum Next (Z80N) Support

RASM supports the Z80N instruction set partially. As of the current version, the major Z80N instructions (`LDIX`, `LDIRX`, `LDWS`, `LDPX`, `LIRF`, `NEXTREG`, `SWAPNIB`, `MIRROR`, `BSWAP`) are accepted. Full coverage is a work in progress.

---

## Command-Line Reference

| Flag | Use |
|---|---|
| `input.asm` | Source file |
| `-o output` | Output file base name |
| `-sna` | Output 48K `.sna` snapshot |
| `-sna128` | Output 128K `.sna` snapshot |
| `-tap` | Output `.tap` file |
| `-tzx` | Output `.tzx` file |
| `-cpr` | Output Amstrad Plus cartridge |
| `-cpc` | Output Amstrad CPC disk image |
| `-bin` | Output raw binary (default) |
| `-lb` | Output library object file |
| `-po addr` | Set the ORG address |
| `-sl` | Emit symbol/label file (for DeZog etc.) |
| `-ls` | Emit listing file |
| `-erro` | Emit error file |
| `-eq name=value` | Define a symbol |
| `-screen "file.scr"` | Include a loading screen in the output |
| `-no-standard-rom-rst` | Disable automatic ROM-resident RST handler insertion |
| `-rasm2pass` | Force two-pass mode (faster, but no forward-reference optimization) |
| `-speed-optimization` | Hint RASM to optimize output for CPU speed (no-op in many cases) |
| `-verbose` | Print extra information |
| `-version` | Print version and exit |

### Typical Command Lines

```bash
# Simple binary
rasm hello.asm

# 48K snapshot
rasm hello.asm -o hello -sna

# 128K snapshot
rasm hello.asm -o hello -sna128

# TAP with auto-start
rasm hello.asm -o hello -tap

# Assemble part of a project
rasm -po #8000 src/main.asm -o build/main
```

RASM is one of the few assemblers that produces `.sna` (both 48K and 128K) directly, making it convenient for emulator testing.

---

## When to Choose RASM

### Strengths

- **The fastest Z80 assembler** — tens of milliseconds for large sources
- **Direct `.sna` output** (both 48K and 128K) — no wrapper tool needed
- **Direct `.tap`, `.tzx`, and CPC `.cpr` / disk output**
- **Powerful macro language** with `for` loops, recursion, IRP
- **Bank-aware assembly** for 128K and multi-bank projects
- **Partial Z80N support** for ZX Spectrum Next
- **MIT license** — most permissive license available
- **Active maintenance** — Roudoudou and community are responsive

### Weaknesses

- **Less documentation** than SjASMPlus (the manual is in French primarily)
- **No formal object-file linker** — multi-file projects use `include`
- **No full Z80N support** yet (some Next instructions missing)
- **Smaller community** than SjASMPlus, especially outside French-speaking regions
- **Single-author bus factor** — if Roudoudou stops, maintenance may stall

### Comparison Matrix

| Feature | RASM | [SjASMPlus](sjasmplus.md) | [Pasmo](pasmo.md) | [vasm](vasm.md) | [zmac](zmac.md) |
|---|---|---|---|---|---|
| Assembly speed | **Fastest** | Fast | Fast | Fast | Fast |
| Hex `#NN` syntax | ✅ | ✅ | ✅ | ❌ | ✅ |
| Direct `.sna` output | ✅ (48K + 128K) | ✅ | ✅ | ❌ | ❌ |
| Direct `.tap` / `.tzx` | ✅ | ✅ | ✅ | ❌ | ✅ |
| Z80N (Next) | ⚠️ | ✅ | ❌ | ⚠️ | ❌ |
| Multi-CPU | ❌ | ❌ | ❌ | ✅ | ⚠️ (8080) |
| For loops at assembly time | ✅ | ❌ | ❌ | ⚠️ | ❌ |
| Lua scripting | ❌ | ✅ | ❌ | ❌ | ❌ |
| License | MIT | BSD-2 | Public domain | MPL-2 | GPL-2+ |

### Decision Guide

Choose **RASM** when:
- You need maximum assembly speed (large projects, CI builds, iterative testing)
- You work with 128K or multi-bank projects
- You want modern macros (for loops, recursion) without Lua's complexity
- You prefer MIT license

Choose **[SjASMPlus](sjasmplus.md)** when:
- You target ZX Spectrum Next (full Z80N support)
- You want Lua scripting
- You need the larger community / more documentation

Choose **[Pasmo](pasmo.md)** when:
- You want the simplest possible tool for a small project

---

## Integration Examples

### RASM + DeZog (Source-Level Debugging)

RASM emits a symbol/label file with the `-sl` flag, compatible with DeZog:

```bash
rasm hello.asm -o hello -tap -sl
```

This produces `hello.tap`, `hello.sym` (RASM symbol file), and `hello.lbl` (DeZog-compatible label file). Load the `.tap` in ZEsarUX or Fuse, then connect DeZog.

### RASM in CI

```yaml
# GitHub Actions
- name: Download RASM
  run: wget http://www.logiciels-cepe.com/rasm/rasm_linux64.zip && unzip rasm_linux64.zip
- name: Assemble
  run: ./rasm src/main.asm -o build/main -sna128 -sl
- name: Upload artifact
  uses: actions/upload-artifact@v3
  with:
    name: spectrum-sna
    path: build/main.sna
```

### RASM + Loading Screen

The `-screen` flag embeds a loading screen in the output:

```bash
rasm demo.asm -o demo -sna -screen loading.scr
```

This is convenient for demos — the snapshot starts with the loading screen already on display.

---

## Common Pitfalls

1. **Documentation primarily in French** — RASM's official documentation is in French first, with community-translated fragments. English-only developers may struggle.

2. **Forgetting `-sl` for debugging** — without the symbol/label file, source-level debugging in DeZog is impossible. Always add `-sl` for development builds.

3. **The `-po` vs `org` confusion** — `-po` is the command-line ORG override. If you also have `org` in the source, `-po` wins. Use only one.

4. **Z80N partial support** — most Z80N instructions work, but a few obscure ones may not. Test before committing to RASM for a Next-only project.

5. **Single-file output** — RASM produces one binary or snapshot. Multi-bank projects produce a single 128K snapshot with the right contents in each bank; you cannot split into separate bank files.

6. **The `-screen` flag has specific screen format requirements** — must be exactly 6912 bytes (48K `.scr`). Other sizes are rejected.

7. **Bank addresses must match hardware** — for 128K snapshots, the `bank` directive must point to the banked RAM region (`#c000-#ffff` on Spectrum 128K).

---

## FAQ

**Q: Where can I find the latest RASM build?**

A: From Roudoudou's site at [logiciels-cepe.com/rasm/rasm.html](http://www.logiciels-cepe.com/rasm/rasm.html) or the GitHub mirror at [github.com/eduardommu/rasm](https://github.com/eduardommu/rasm).

**Q: Is RASM faster than SjASMPlus?**

A: Yes, significantly. On large multi-bank projects, RASM is typically 5-10x faster than SjASMPlus. For small single-file projects, the difference is negligible (both assemble in tens of milliseconds).

**Q: Can RASM produce a `.nex` file for ZX Spectrum Next?**

A: Not directly. Use SjASMPlus for `.nex` output, or post-process RASM's `.bin` with a separate tool.

**Q: Does RASM support the Amstrad CPC?**

A: Yes. RASM supports both Spectrum and Amstrad CPC output formats. The `-cpr` flag produces a CPC Plus cartridge; the `-cpc` flag produces a CPC disk image. This makes RASM popular with French developers who work on both platforms.

**Q: Is the documentation available in English?**

A: Partially. The reference manual is in French; community translations exist but may lag the latest version. The error messages are also French by default.

**Q: Can RASM link multiple object files?**

A: No. RASM is single-pass with `include` for multi-file projects. If you need a real linker, use [z88dk z80asm](z88dk_z80asm.md) or [WLA-DX](wla_dx.md).

**Q: Does RASM support undocumented Z80 instructions?**

A: Yes. `SLI` (also `SLL`), `LD IXh`, etc. are accepted.

---

## Cross-References

- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [sjasmplus.md](sjasmplus.md) — the main alternative
- [pasmo.md](pasmo.md) — the simpler alternative
- [z88dk_z80asm.md](z88dk_z80asm.md) — the z88dk-integrated alternative
- [vasm.md](vasm.md) — the portable multi-CPU alternative
- [wla_dx.md](wla_dx.md) — the linker-aware alternative
- [zmac.md](zmac.md) — the classic alternative
- [tniasm.md](tniasm.md) — the late-era native Russian alternative (pending)
- [debugging.md](debugging.md) — debugging strategies
- [vscode_integration.md](vscode_integration.md) — IDE setup

---

## References

- Roudoudou — *RASM home page*, [logiciels-cepe.com/rasm/rasm.html](http://www.logiciels-cepe.com/rasm/rasm.html)
- RASM GitHub mirror — [github.com/eduardommu/rasm](https://github.com/eduardommu/rasm)
- Demoscene releases built with RASM — demos on [Pouet.net](https://www.pouet.net/) by various French scene groups
- MIT License — very permissive
- French Spectrum scene — [cpcscene.net](https://cpcscene.net/) and other French retro resources
