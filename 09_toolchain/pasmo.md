[← Home](../README.md) · [Toolchain](README.md)

# Pasmo — The Minimalist Z80 Cross-Assembler

**Pasmo** is a small, fast, single-file Z80 cross-assembler written in C++ by Julián Albo Santiago. First released around 2001, it has become the **de facto "first cross-assembler"** for new Spectrum developers — the tool you reach for when SjASMPlus feels too feature-laden and you just want a quick binary from a `.asm` source.

Pasmo's design philosophy is **minimalism**: a single executable, no dependencies, no project files, no macro language beyond the basics. It assembles a single source file into a raw binary, a `.tap` tape file, or a `.tzx` tape file. This simplicity has made it the standard tool for tutorials, small demos, and the first port of call for hobbyists.

> [!NOTE]
> For the *full* cross-assembler landscape (SjASMPlus, z88dk z80asm, vasm, WLA-DX, zmac, RASM and where Pasmo fits), see [cross_platform_toolchain.md](cross_platform_toolchain.md). This article is the **per-tool reference** for Pasmo specifically.

---

## Quick Start

Install Pasmo (Debian/Ubuntu: `sudo apt install pasmo`; macOS: `brew install pasmo`; from source: download from the [official site](http://www.arrakis.es/~ninsesabe/pasmo/) and run `make`).

Write `hello.asm`:

```z80
        org #8000

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
pasmo hello.asm hello.bin
```

Or to a `.tap` tape file ready to load into Fuse, ZEsarUX, or any other emulator:

```bash
pasmo --tap hello.asm hello.tap
```

Load `hello.tap` in an emulator and `RANDOMIZE USR 32768` (which is `#8000` in decimal) to run.

---

## History and Design Philosophy

Julián Albo Santiago, a Spanish mathematician and programmer, started Pasmo in 2001 to fill a gap: existing cross-assemblers of the era (zmac, tasm) were either MS-DOS tools showing their age or commercial packages. Pasmo was deliberately written to be:

- **Single-source-file** in C++ — easy to compile on any platform with any C++ compiler
- **Public domain** (no license restrictions at all)
- **Fast** — two-pass assembly, no macroexplosion overhead
- **Deterministic** — same source always produces the same bytes
- **Small** — the executable is under 200 KB

The design reflects the Unix philosophy: "do one thing well". Pasmo does not include a disassembler, debugger, emulator, IDE, or library manager. It assembles Z80 source to binary and stops there. Other tools (Fuse, ZEsarUX, DeZog, hex editors) handle the rest of the workflow.

### Version History

| Version | Year | Highlights |
|---|---|---|
| 0.1 | 2001 | First public release; basic two-pass assembly |
| 0.3 | 2002 | `.tap` output format |
| 0.4 | 2003 | `.tzx` output, `--name` for tape block naming |
| 0.5 | 2005 | Spectrum 128K snapshot (`.sna`/`.z80`) output |
| 0.6 | 2010 | Improved macro support, bug fixes |
| 0.7 | 2017 | Modern maintenance branch (latest versions on SourceForge) |
| 0.7.x | 2020s | Ongoing community maintenance |

Pasmo's development has always been slow and conservative — new features arrive rarely. This is a feature, not a bug: programs written for Pasmo 0.3 in 2002 still assemble unchanged under Pasmo 0.7 today.

---

## Source Language

Pasmo supports a **simple, generic Z80 syntax** that closely matches what you would find in 1980s documentation like the Zilog manual or the Rodnay Zaks book. There are no exotic dialect features.

### Numbers

| Format | Example | Base |
|---|---|---|
| Decimal | `42`, `255` | 10 |
| Hex with `#` | `#FE`, `#4000` | 16 |
| Hex with `$` | `$FE`, `$4000` | 16 |
| Hex with `0x` | `0xFE`, `0x4000` | 16 |
| Hex with `H` suffix | `0FEh`, `4000h` | 16 (must start with digit) |
| Binary with `B` suffix | `10101010b` | 2 (must start with 0 or 1) |
| Binary with `%` | `%10101010` | 2 |
| Character | `'A'`, `"a"` | ASCII value |

All four hex syntaxes are interchangeable — Pasmo accepts all of them. The choice is a style preference; the Spectrum community typically uses `#FE` (matching the original Sinclair BASIC convention) while the broader Z80 community uses `$FE` or `0FEh`.

### Identifiers

Labels and symbols follow standard rules:

- Start with a letter or underscore (`[A-Za-z_]`)
- Continue with letters, digits, or underscores
- Case-sensitive by default (use `--case-insensitive` to override)
- May contain `.` for namespacing (e.g., `loop.start`, `loop.end`)
- Maximum length: implementation-defined but practically unlimited

Local labels (starting with `.`) are scoped to the last non-local label. This is useful inside macro expansions:

```z80
CopyBytes:
        ld   a, b
        or   a
        ret  z
.loop:  ldir              ; local label
        ret
```

### Operators

Pasmo supports a standard set of expression operators, evaluated at assembly time:

| Operator | Meaning | Precedence |
|---|---|---|
| `+`, `-`, `*`, `/` | Arithmetic | Standard |
| `%` | Modulo | Standard |
| `&`, `\|`, `^`, `~` | Bitwise AND, OR, XOR, NOT | Lower than arithmetic |
| `<<`, `>>` | Bitwise shifts | Same as `*`/`/` |
| `==`, `!=`, `<`, `>`, `<=`, `>=` | Comparison (returns 0 or 1) | Lower than bitwise |
| `&&`, `\|\|` | Logical AND, OR | Lowest |
| `!` | Logical NOT | Highest unary |
| `'` (prefix) | Low byte of next value | (special) |
| `<>` | High byte (also: `>` suffix) | (special) |

### Built-in Functions

Pasmo's function set is small but useful:

| Function | Returns |
|---|---|
| `HIGH x` | High byte of `x` |
| `LOW x` | Low byte of `x` |
| `defined(symbol)` | 1 if symbol exists, 0 otherwise |
| `addr(label)` | Address of label (same as just `label`) |

The function set is intentionally minimal — for complex compile-time computation, use macros or pre-process the source with another tool.

---

## Directives

Pasmo supports the standard set of Z80 assembler directives, with both the **dot-led form** (`.org`, `.db`) and the **non-dot form** (`org`, `db`) accepted interchangeably.

### Origin and Code Placement

| Directive | Use |
|---|---|
| `ORG address` | Set the assembly address (where the next bytes will go when loaded) |
| `ALIGN n` | Pad with zeros until the address is a multiple of `n` (typical: `ALIGN #100` for 256-byte alignment) |
| `PHASE address` | Assemble as if at `address`, without moving the real output cursor — useful for overlays |
| `DEPHASE` | End a `PHASE` block |

### Data Definitions

| Directive | Use |
|---|---|
| `DB value [, value ...]` | Define bytes (also: `DEFB`, `BYTE`, `.byte`) |
| `DW value [, value ...]` | Define words (16-bit, little-endian) (also: `DEFW`, `WORD`, `.word`) |
| `DD value [, value ...]` | Define double words (32-bit) — rarely needed on Z80 |
| `DS count [, fill]` | Define storage — emit `count` bytes of `fill` (default 0). Useful for reserving BSS-like regions |
| `DM "text"` | Define message — like `DB` but for text (some dialects) |
| `TEXT "text"` | Same as `DM` |

Example: define a 16-entry lookup table with `DS`:

```z80
SineTable:
        ds   16               ; reserve 16 bytes (zero-filled)
```

### Symbols and Constants

| Directive | Use |
|---|---|
| `EQU` | Define a constant: `BORDER_RED equ 2` (note reverse order vs `=`) |
| `=` | Define a reassignable symbol: `LOOP_COUNT = 0` |
| `LABEL` | Define a label at current address (implicit when using `name:` syntax) |

### Includes and Conditional Assembly

| Directive | Use |
|---|---|
| `INCLUDE "file.asm"` | Include a source file inline at this point (also: `#include "file.asm"`) |
| `INCBIN "file.bin"` | Include a binary file as-is |
| `IF expression` ... `ELSE` ... `ENDIF` | Conditional assembly |
| `IFDEF symbol` ... `ENDIF` | Assemble only if symbol is defined |
| `IFNDEF symbol` ... `ENDIF` | Assemble only if symbol is not defined |

Example: include different sources based on a target define:

```z80
IFDEF TARGET_48K
        INCLUDE "screen_48k.asm"
ELSE
        INCLUDE "screen_128k.asm"
ENDIF
```

### Macros

Pasmo supports **single-line text macros** via `DEFINE` and **parameterised macros** via the standard `MACRO` / `ENDM` block:

```z80
; Parameterised macro: zero-fill N bytes starting at HL
MACRO CLEAR_N count
        ld   (hl), 0
        ld   b, count - 1
        inc  hl
.clear_loop:
        ld   (hl), 0
        inc  hl
        djnz .clear_loop
ENDM

; Usage
        ld   hl, ScreenBuffer
        CLEAR_N 256
```

Macro arguments are referenced by number: `\1` is the first argument, `\2` the second, etc. Local labels inside macros (starting with `.`) get a unique suffix per expansion to avoid name conflicts.

> [!NOTE]
> Pasmo's macro support is **limited** compared to [SjASMPlus](sjasmplus.md) or [WLA-DX](wla_dx.md). For complex metaprogramming (variadic macros, recursive macros, IRP), use a more powerful assembler.

---

## Output Formats and Command-Line Reference

The output format is selected by command-line flag. Without a flag, Pasmo emits a raw binary.

### Common Output Formats

| Flag | Output | Notes |
|---|---|---|
| (none) | Raw binary (`.bin`) | Loadable to any address — usually paired with `ORG #8000` for Spectrum use |
| `--tap` | `.tap` file | Standard Spectrum `.tap` with one header block and one data block. Load with `LOAD ""` |
| `--tapbas` | `.tap` file with BASIC loader | Adds an auto-`LOAD`/`RANDOMIZE USR` block so the user just types `LOAD""` |
| `--tzx` | `.tzx` file | TZX format with same block structure as `.tap` |
| `--tzxbas` | `.tzx` with BASIC loader | Same as `--tapbas` but TZX |
| `--cdt` | `.cdt` file | Amstrad CPC tape format (rarely used for Spectrum) |
| `--bin` | Explicit raw binary (same as default) |

### Snapshot Formats

| Flag | Output |
|---|---|
| `--sna` | 48K `.sna` snapshot — loadable directly into any emulator that supports SNA |
| `--z80` | `.z80` snapshot (version 2, 48K or 128K depending on `--128`) |
| `--128` | Combine with `--sna` or `--z80` to produce 128K versions |

### Command-Line Flags

| Flag | Purpose |
|---|---|
| `--name NAME` | Set the tape block name (default: filename) |
| `--org ADDR` | Override the `ORG` directive in the source |
| `--autostart ADDR` | Set the auto-start address for snapshot files |
| `--public` (default) | Include all symbols in the symbol file |
| `--local` | Treat symbols starting with `_` as local |
| `--case-insensitive` | Treat identifiers as case-insensitive |
| `--ascii` | Convert strings to ASCII (default — same as Sinclair ROM) |
| `--zx80` / `--zx81` | Target ZX80 / ZX81 character encoding |
| `--tabbed-symbols` | Symbol file uses tab-separated columns |
| `--symbols-file FILE` | Write symbols to FILE (Pasmo format) |
| `--labels` | Write labels to `<source>.labels` (DeZog-compatible) |
| `--err` | Print error messages in a standard parser-friendly format |
| `--verbose` | Print extra debugging information |
| `--version` | Print Pasmo version and exit |
| `--help` | Print usage and exit |

### Typical Command Lines

```bash
# Plain binary
pasmo hello.asm hello.bin

# Tape file with auto-run
pasmo --tapbas --autostart #8000 hello.asm hello.tap

# 48K snapshot
pasmo --sna --autostart #8000 hello.asm hello.sna

# 128K snapshot
pasmo --sna --128 --autostart #8000 hello.asm hello.sna

# Emit a DeZog-compatible label file alongside
pasmo --tap --labels hello.asm hello.tap
```

---

## When to Choose Pasmo

### Strengths

- **Zero-friction start** — `apt install pasmo` and you are done
- **Tiny, fast, deterministic** — sub-second assembly on any modern machine
- **All four hex syntaxes accepted** — useful when adapting code from various sources
- **All major output formats supported** — `.bin`, `.tap`, `.tzx`, `.sna`, `.z80`
- **DeZog-compatible label file** via `--labels` for source-level debugging
- **Public domain** — no license restrictions

### Weaknesses

- **No macro metaprogramming** beyond simple parameterised macros
- **No structured programming constructs** (no `STRUCT`, `UNION`)
- **No Spectrum-specific hardware awareness** — you must manually use `OUT (#FD),A` etc.; no built-in `MMU` or `BANK` directives
- **No ZX Spectrum Next support** — Z80N instructions are unknown
- **No multi-section output** — you get exactly one binary blob
- **Project is in maintenance mode** — bugs may go unfixed for years

### Comparison Matrix

| Feature | Pasmo | [SjASMPlus](sjasmplus.md) | [z88dk z80asm](z88dk_z80asm.md) | [vasm](vasm.md) | [WLA-DX](wla_dx.md) | [zmac](zmac.md) |
|---|---|---|---|---|---|---|
| Year started | 2001 | 2004 | 1990s (origin) | 2002 | 1990s | 1990s |
| Hex `#NN` syntax | ✅ | ✅ | ✅ | ⚠️ (`$NN` only) | ⚠️ (`$NN` only) | ✅ |
| Parameterised macros | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Structured macros (IRP, REPT) | ❌ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Z80N (ZX Spectrum Next) | ❌ | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| `.tap` / `.tzx` output | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `.sna` / `.z80` output | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| DeZog label file | ✅ | ✅ (`--sld`) | ⚠️ | ❌ | ❌ | ⚠️ |
| Multiple CPUs | ❌ (Z80 only) | ⚠️ (Z80 + Z80N) | ✅ | ✅ (many) | ✅ | ⚠️ (Z80 + 8080) |
| Snapshot format output | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Maintenance level | Conservative | Active | Active | Active | Active | Sporadic |

### Decision Guide

Choose **Pasmo** when:
- You want to assemble a single-file demo or tutorial quickly
- You are learning Z80 assembly and do not need advanced features
- You want minimum dependencies and smallest possible toolchain
- You are working from the Rodnay Zaks book or similar 1980s reference

Choose **[SjASMPlus](sjasmplus.md)** when:
- You need ZX Spectrum Next Z80N instructions
- You want Lua scripting for metaprogramming
- You need ZX Spectrum-specific output formats (`.nex`, `.trd`)

Choose **[z88dk z80asm](z88dk_z80asm.md)** when:
- You are inside the z88dk toolchain
- You need object files that link with C code
- You want multi-CPU support (Z180, Rabbit, etc.)

---

## Integration with Other Tools

### Pasmo + DeZog + ZEsarUX (Source-Level Debugging)

The recommended workflow for source-level debugging of Pasmo-assembled code:

```bash
# 1. Assemble with label file
pasmo --tap --labels --name myprogram myprogram.asm myprogram.tap

# 2. Open myprogram.tap in ZEsarUX (File > Tape > Insert Tape)

# 3. In ZEsarUX: enable remote debugging (Settings > Debug > Open Debug Port)

# 4. Open VS Code with the DeZog extension, configured for ZEsarUX backend

# 5. DeZog reads myprogram.labels for symbol information
```

For full setup details see [vscode_integration.md](vscode_integration.md) and [debugging.md](debugging.md).

### Pasmo + Make

A typical Makefile rule:

```make
all: myprogram.tap

myprogram.tap: myprogram.asm
        pasmo --tapbas --autostart #8000 $< $@

clean:
        rm -f *.tap *.bin *.labels
```

For a complete asset pipeline (graphics, music, levels), see [asset_tools.md](asset_tools.md).

### Pasmo in CI

Because Pasmo is small, deterministic, and CLI-only, it integrates cleanly with CI/CD:

```yaml
# GitHub Actions example
- name: Install Pasmo
  run: sudo apt-get install -y pasmo
- name: Assemble
  run: pasmo --tapbas --autostart #8000 src/main.asm build/main.tap
- name: Upload artifact
  uses: actions/upload-artifact@v3
  with:
    name: spectrum-tap
    path: build/main.tap
```

---

## Common Pitfalls

1. **Forgetting `ORG`** — without an `ORG` directive, Pasmo assembles as if at address `#0000`, which produces a binary that conflicts with the ROM. Always add `ORG #8000` (or your chosen load address) at the top.

2. **Mismatch between `ORG` and load address** — when emitting a `.tap` file with `--tapbas`, the auto-loader will `LOAD` the binary and `RANDOMIZE USR` the autostart address. If `ORG` and `--autostart` differ, the binary is loaded to the wrong place and crashes.

3. **`LD A,(nn)` vs `LD (nn),A`** — Z80 has both `LD A,(addr)` and `LD (addr),A` which are different instructions. Pasmo accepts both; just be sure you used the right one.

4. **Hexadecimal syntax mix** — `#FF`, `$FF`, `0xFF`, and `0FFh` are all accepted but you must be consistent. Mixing them in one source is legal but ugly.

5. **Snapshot of banked code** — `--sna --128` will assemble and write a 128K snapshot, but Pasmo does not understand the 128K paging port. If your code uses paged RAM, you must manually compute the bank contents and place them with `ORG`.

6. **No ZX Spectrum Next support** — Pasmo does not recognize `LDIX`, `LDIRX`, `LDWS`, `LDPX`, `LIRF`, or any other Z80N instruction. For Next development use [SjASMPlus](sjasmplus.md).

7. **Macros cannot recurse** — Pasmo's macro expansion is not recursive. A macro that expands into another macro call will not expand the inner macro. For metaprogramming, pre-process the source.

---

## FAQ

**Q: Why is it called "Pasmo"?**

A: The name is Julián Albo's choice. "Pasmo" is Spanish for "amazement" or "stupor". The connection to assembly is unclear — possibly a self-deprecating comment on how assemblers feel.

**Q: Is Pasmo still maintained?**

A: Conservatively. The last major feature release was 0.7 in 2017. Bug fixes and minor patches are applied occasionally. The current version on SourceForge and Linux package managers is generally 0.7.x. For most uses, this is plenty.

**Q: Can Pasmo produce a `.nex` file for the ZX Spectrum Next?**

A: No. Use [SjASMPlus](sjasmplus.md) for `.nex` output.

**Q: Does Pasmo support Game Boy Z80 variants?**

A: No. The Game Boy CPU (LR35902) is Z80-like but not strictly Z80. Use a Game Boy-specific assembler like [WLA-DX](wla_dx.md) (which supports Game Boy) or RGBDS.

**Q: Can I use Pasmo with z88dk's library?**

A: No. z88dk produces object files in its own format, which Pasmo cannot read. Use z88dk's bundled assembler `z80asm` instead (see [z88dk_z80asm.md](z88dk_z80asm.md)).

**Q: How do I debug Pasmo output at source level?**

A: Use the `--labels` flag to emit a DeZog-compatible symbol file, then open the `.tap` in ZEsarUX or Fuse and connect via DeZog. See [vscode_integration.md](vscode_integration.md) for the full setup.

**Q: Why does Pasmo report an error on `LD A,(IX+5)`?**

A: Pasmo accepts this syntax. If you see an error, check that `IX` is correctly cased (case-insensitive mode may be needed) and that you have not used `IX` as a label name elsewhere.

---

## Cross-References

- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [native_toolchain.md](native_toolchain.md) — survey of native assemblers (Zeus, DevPac, ALASM, XAS)
- [sjasmplus.md](sjasmplus.md) — the more powerful alternative
- [z88dk_z80asm.md](z88dk_z80asm.md) — z88dk's bundled assembler
- [vasm.md](vasm.md) — portable macro assembler (pending)
- [wla_dx.md](wla_dx.md) — cross-platform macro assembler (pending)
- [zmac.md](zmac.md) — classic cross-assembler (pending)
- [vscode_integration.md](vscode_integration.md) — IDE setup with DeZog
- [debugging.md](debugging.md) — source-level debugging workflows
- [asset_tools.md](asset_tools.md) — asset pipeline that often accompanies assembly code

---

## References

- Julián Albo Santiago — *Pasmo Z80 Cross-Assembler*, [official site](http://www.arrakis.es/~ninsesabe/pasmo/) (archived; current versions on SourceForge)
- Pasmo SourceForge project — [sourceforge.net/projects/pasmo](https://sourceforge.net/projects/pasmo/)
- Linux distribution packages — `pasmo` in Debian, Ubuntu, Fedora, Arch AUR
- Homebrew formula — `brew install pasmo` on macOS
