[← Home](../README.md) · [Toolchain](README.md)

# ZASM (by Kio) — Small, Clean, Modern Cross-Assembler

**ZASM** by **Kio** (a German ZX Spectrum developer, active under the handle "Kio") is a small, modern, single-executable Z80 cross-assembler. First released around 2010, ZASM targets Linux and macOS (and Windows under WSL or Cygwin). It is a niche tool used primarily by the German retro-computing scene and by developers who appreciate its clean, minimal syntax and direct `.sna` output.

Unlike larger projects like [z88dk z80asm](z88dk_z80asm.md) or [SjASMPlus](sjasmplus.md), ZASM is a small project with a single developer. It is not as feature-rich as its bigger siblings, but it covers the common Z80 development workflow cleanly and produces snapshots directly.

> [!NOTE]
> This article covers **ZASM by Kio**. There are several other tools named "ZASM" — including an earlier MS-DOS Z80 cross-assembler and the ZASM emulator/IDE. Kio's ZASM is the most commonly encountered modern version.

---

## Quick Start

Install from source (clone from Kio's repository; build with `make`). Pre-built Linux/macOS binaries are sometimes available.

Write `hello.asm`:

```z80
        org  #8000

start:  ld   hl, message
        call print_string
        ret

message:
        db   "Hello, World!", 13, 0

print_string:
        ld   a, (hl)
        or   a
        ret  z
        rst  16
        inc  hl
        jr   print_string

        end  start
```

Assemble to a 48K snapshot:

```bash
zasm hello.asm -o hello.sna
```

Or to raw binary:

```bash
zasm hello.asm -o hello.bin
```

ZASM accepts both `#NN` (Sinclair style) and `0xNN` (C style) for hexadecimal.

---

## History and Design Philosophy

ZASM by Kio started around 2010 as a personal project. The author needed a small, clean Z80 assembler for Linux that could produce `.sna` snapshots directly without requiring a separate wrapping step. The result is a minimal tool that focuses on:

- **Small size** — single executable, no runtime dependencies
- **Direct snapshot output** — `.sna` from one command
- **Sinclair-friendly hex** — accepts `#NN` like Sinclair BASIC
- **Modern Unix build** — runs natively on Linux and macOS

ZASM is a **single-developer project**. It has a smaller feature set than [SjASMPlus](sjasmplus.md) and a smaller user base than [Pasmo](pasmo.md). It is most often encountered in:

- German-language ZX Spectrum tutorials
- Small homebrew projects that need direct `.sna` output on Linux
- As a reference implementation for clean Z80 assembler design

### Relationship to Other Z80 Assemblers

ZASM is sometimes confused with other tools sharing the name:

- **ZASM (DOS, 1990s)** — an older MS-DOS Z80 assembler, unrelated to Kio's
- **ZASM (IDE)** — a Z80 IDE/debugger, unrelated
- **Z80ASM** (without the A) — various tools including z88dk's [z80asm](z88dk_z80asm.md)

To disambiguate, this article uses "ZASM by Kio" or just "ZASM" where context is clear.

---

## Source Language

ZASM uses a minimal, clean syntax. Directives are dot-less (`org`, `db`, `dw`, `end`) but dot-led forms are also accepted.

### Number Formats

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `#` | `#FE`, `#4000` | **Sinclair style** |
| Hex with `0x` | `0xFE` | C syntax |
| Hex with `$` | `$FE` | Zilog syntax |
| Hex with `H` suffix | `0FEh` | |
| Binary with `%` | `%10101010` | |
| Character | `'A'`, `"a"` | ASCII value |

The wide hex support is a notable feature — most assemblers pick one or two formats, but ZASM accepts all common ones.

### Operators

ZASM has the standard set: arithmetic, bitwise, shifts. Comparison and ternary operators are supported.

### Directives

| Directive | Use |
|---|---|
| `org address` | Set assembly address |
| `db b1, b2, ...` | Define bytes (also: `.db`, `defb`) |
| `dw w1, w2, ...` | Define words (also: `.dw`, `defw`) |
| `ds count [, fill]` | Define storage |
| `dm "text"` | Define message (no terminator) |
| `equ` or `=` | Define a constant |
| `include "file"` | Include a source file |
| `incbin "file"` | Include a binary file |
| `if expr` / `else` / `endif` | Conditional assembly |
| `macro name(params)` ... `endm` | Define a macro |
| `rept count` ... `endr` | Repeat block |
| `end [label]` | End of source |

### Macros

ZASM supports named-parameter macros with `rept` for repeat blocks:

```z80
        macro clear_block(addr, count)
        ld   hl, addr
        ld   (hl), 0
        ld   de, addr + 1
        ld   bc, count - 1
        ldir
        endm

        ; Usage
        clear_block(#4000, 6144)   ; Clear screen memory
        clear_block(#5800, 768)    ; Clear attribute memory
```

The macro language is similar to SjASMPlus but with fewer advanced features (no Lua scripting, no IRP).

---

## Command-Line and Output Formats

### Common Flags

| Flag | Use |
|---|---|
| `-o FILE` | Output file (extension decides format) |
| `-l FILE` | Produce listing file |
| `-s FILE` | Produce symbol file |
| `-D name=value` | Define a symbol |
| `-I dir` | Add include search path |
| `-v` | Verbose output |
| `-w` | Show warnings |

### Output Formats

ZASM decides the output format from the file extension:

| Extension | Format |
|---|---|
| `.bin` | Raw binary |
| `.sna` | ZX Spectrum 48K snapshot |
| `.z80` | ZX Spectrum .z80 snapshot |
| `.tap` | ZX Spectrum tape file (with auto-run) |
| `.hex` | Intel HEX |

This is similar to [Pasmo](pasmo.md)'s approach — the extension controls the output format, simplifying the command line.

### Typical Workflow

```bash
# Assemble to 48K snapshot
zasm hello.asm -o hello.sna

# Assemble to .tap (auto-run)
zasm hello.asm -o hello.tap

# With listing and symbols
zasm hello.asm -o hello.bin -l hello.lst -s hello.sym
```

---

## When to Choose ZASM

### Strengths

- **Direct `.sna` and `.tap` output** — no post-processing required
- **Accepts all common hex formats** including `#NN` Sinclair style
- **Small, single executable** — easy to install and bundle
- **Clean, minimal syntax** — easy to learn
- **Native Linux/macOS support** — no DOSBox needed

### Weaknesses

- **Small user community** — fewer tutorials, examples, and Stack Overflow answers
- **Limited documentation** — primarily in German
- **No object-file linking** — single-source only (use `.include` for multi-file projects)
- **No Z80N (Spectrum Next) support** — stick to vanilla Z80
- **Less feature-rich than SjASMPlus or Pasmo** — fewer directives, fewer macros, fewer output options
- **Single-developer project** — maintenance depends on one person's availability

### Comparison Matrix

| Feature | ZASM (Kio) | [Pasmo](pasmo.md) | [SjASMPlus](sjasmplus.md) | [RASM](rasm.md) | [z88dk z80asm](z88dk_z80asm.md) |
|---|---|---|---|---|---|
| Year started | ~2010 | 2001 | 2004 | 2016 | 1990s |
| Direct `.sna` output | ✅ | ✅ | ✅ | ✅ | ❌ |
| Direct `.tap` output | ✅ | ✅ | ✅ | ✅ | ❌ (use appmake) |
| Hex `#NN` syntax | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Object files | ❌ | ❌ | ❌ | ❌ | ✅ |
| Z80N (Spectrum Next) | ❌ | ❌ | ✅ | ✅ | ✅ |
| Lua scripting | ❌ | ❌ | ✅ | ❌ | ❌ |
| Multi-CPU | ❌ | ❌ | ❌ | ⚠️ (CPC too) | ❌ |
| License | Open source | Public domain | BSD-2 | MIT | GPL |

### Decision Guide

Choose **ZASM** when:
- You want the simplest possible workflow on Linux/macOS
- You want direct `.sna` or `.tap` output
- You like Sinclair `#NN` hex syntax
- You are in the German retro scene and following local tutorials

Choose **[Pasmo](pasmo.md)** when:
- You want a similar minimal tool with broader community support
- You want documented, public-domain code

Choose **[SjASMPlus](sjasmplus.md)** when:
- You target ZX Spectrum Next (Z80N)
- You want Lua scripting
- You want the most active development and community

---

## Common Pitfalls

1. **Limited documentation** — ZASM's docs are sparse. Expect to read the source code or ask the author.

2. **No Z80N support** — ZASM targets vanilla Z80 only. For Spectrum Next work, use [SjASMPlus](sjasmplus.md) or [RASM](rasm.md).

3. **Single-source projects** — ZASM does not support object files or linker. Use `.include` for multi-file projects.

4. **Niche community** — finding help online is harder than for SjASMPlus or Pasmo.

5. **Build from source** — pre-built binaries are not always available for all platforms. Building from source requires a C++ compiler and `make`.

6. **Confusion with other "ZASM" tools** — make sure you are using Kio's ZASM, not one of the several other tools with the same name.

---

## FAQ

**Q: Where can I download ZASM by Kio?**

A: From Kio's personal repository or a German retro-computing mirror. Search for "zasm kio" to disambiguate from other tools.

**Q: Does ZASM support ZX Spectrum Next?**

A: No. ZASM targets vanilla Z80 only. Use [SjASMPlus](sjasmplus.md) for Z80N.

**Q: Can ZASM produce a `.tap` file with auto-run?**

A: Yes. Use `-o file.tap` and ZASM sets the auto-run address from the `org` directive.

**Q: Is ZASM better than Pasmo?**

A: They are similar tools with similar feature sets. Pasmo has broader documentation and community. ZASM has slightly cleaner syntax and native `.sna` output on Linux. Either works for most projects.

**Q: Does ZASM have an IDE or debugger?**

A: No. ZASM is a command-line assembler only. Pair with [vscode_integration.md](vscode_integration.md) for editing and a Spectrum emulator for debugging.

---

## Cross-References

- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [pasmo.md](pasmo.md) — similar minimalist cross-assembler
- [sjasmplus.md](sjasmplus.md) — more featureful modern alternative
- [rasm.md](rasm.md) — another modern Z80 cross-assembler
- [z88dk_z80asm.md](z88dk_z80asm.md) — object-file assembler from z88dk
- [vasm.md](vasm.md) — multi-CPU alternative
- [native_toolchain.md](native_toolchain.md) — survey of native assemblers

---

## References

- Kio's ZASM repository (search for "zasm kio spectrum")
- German ZX Spectrum community forums and tutorials
- Comparison with other modern Z80 assemblers in various retro-computing wikis
