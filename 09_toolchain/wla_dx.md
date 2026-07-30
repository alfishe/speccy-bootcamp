[← Home](../README.md) · [Toolchain](README.md)

# WLA-DX — The Macro Assembler for Many CPU Architectures

**WLA-DX** (WLA DX — originally *Where's the Line Assembly?*, later expanded as *Workshop for Local Assembly*) is a portable macro assembler and linker system by Ville Helström, started in the late 1990s. It is unusual among Z80 cross-assemblers in that it was **designed for multi-CPU projects from day one**: the same toolchain assembles Z80, M68k, 6502, 65816 (used in the SNES), 6800, 6301, 6303, Game Boy LR35902, SPC700 (the SNES audio CPU), HUC6280 (PC Engine), and more.

For ZX Spectrum development, WLA-DX is a less obvious choice than [SjASMPlus](sjasmplus.md) or [Pasmo](pasmo.md), but it has a dedicated user base because of its clean macro language, strong linker, and consistent syntax across all its supported CPUs. If you also write Game Boy, NES, SNES, or PC Engine code, WLA-DX is the only tool you need.

> [!NOTE]
> This article is the **per-tool reference** for WLA-DX specifically. For the broader cross-assembler landscape, see [cross_platform_toolchain.md](cross_platform_toolchain.md).

---

## Quick Start

Install WLA-DX (Debian/Ubuntu: build from source per the [WLA-DX README](https://github.com/vhelin/wla-dx); macOS: `brew install wla-dx`; from source: clone the repository and run `make install`).

WLA-DX uses a two-step build: assemble to object file, then link to final binary. Write `hello.s` (note the `.s` extension — WLA-DX conventions):

```z80
        .memorymap
            defaultslot 0
            slotsize $4000
            slot 0 $0000
        .endme

        .rombankmap
            bankstotal 1
            bankssize $4000
            banks 1
            banksize $4000
            bank 0
        .endro

        .background message
        .db "Hello, World!", 0

        .org $8000
start:  ld   hl, message
        call print_string
        ret
```

Assemble and link:

```bash
wla-z80 -o hello.o hello.s
wlalink -o hello.bin hello.o
```

WLA-DX requires this `.memorymap` / `.rombankmap` preamble for every source. This is more verbose than Pasmo or SjASMPlus but it lets the linker make intelligent decisions about banked memory layouts — useful for NES, SNES, and Game Boy projects where ROM banking is fundamental.

---

## History and Design Philosophy

Ville Helström, a Finnish programmer, started WLA-DX in 1998 to support his Game Boy development work. The original target was the Game Boy's LR35902 CPU; WLA-DX's name and origin reflect this Game Boy heritage. The assembler was designed around two requirements that would shape every later CPU addition:

1. **ROM banking must be a first-class concept** — Game Boy cartridges have 32 KB of addressable space but typically 256 KB to 8 MB of physical ROM in banks. The assembler needed to track bank assignment.
2. **Linker must place code in correct banks** — code that calls into another bank needs a trampoline or a bank switch; the linker had to understand this.

These requirements are familiar to ZX Spectrum 128K developers (who deal with RAM banking, not ROM banking) and especially to those developing for the ZX Spectrum Next (which has both ROM-style banking and banked RAM).

### Supported CPUs

WLA-DX assembles one CPU per build, so you install the specific `wla-` binary for your target:

| Binary | CPU | Common targets |
|---|---|---|
| `wla-gb` | Sharp LR35902 | Game Boy, Game Boy Color |
| `wla-z80` | Zilog Z80 | ZX Spectrum, MSX, Master System, ColecoVision, SG-1000 |
| `wla-6502` | MOS 6502 | NES, Commodore 64, Atari 2600, Apple II |
| `wla-65c02` | WDC 65C02 | Modern variants of the above |
| `wla-6510` | MOS 6510 | Commodore 64 |
| `wla-65816` | WDC 65816 | SNES, Apple IIgs |
| `wla-6800` | Motorola 6800 | Old arcades, embedded |
| `wla-6801` | Motorola 6801 | Old embedded |
| `wla-6809` | Motorola 6809 | TRS-80 Color Computer, Vectrex |
| `wla-6811` | Motorola 68HC11 | Embedded |
| `wla-spc700` | Sony SPC700 | SNES audio co-processor |
| `wla-huc6280` | Hudson Soft HuC6280 | PC Engine / TurboGrafx-16 |

For ZX Spectrum development, **`wla-z80`** is the appropriate binary.

### Version History

| Year | Version | Highlights |
|---|---|---|
| 1998 | 1.0 | First public release; Game Boy only |
| 1999 | 2.0 | Z80 added; supports both GB and Spectrum |
| 2003 | 5.x | 6502, 65816 added; NES and SNES targets |
| 2010 | 9.x | All current CPUs; bug-fix focus |
| 2015 | 9.8 | Macro language improvements |
| 2020s | 10.x | Modern maintenance on GitHub |

The project moved to GitHub in the 2010s and is now actively maintained. The license is **GPL-2.0-or-later**.

---

## Source Language

WLA-DX uses dot-led directives (`.org`, `.db`, `.macro`) and C-like expressions. Comments start with `;` for line comments or `/* ... */` for block comments.

### Number Formats

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `$` | `$FE`, `$4000` | Zilog syntax — **default** |
| Hex with `0x` | `0xFE` | C syntax |
| Hex with `%` prefix | `%11110000` | Binary (also `%`-prefixed in WLA-DX) |
| Character | `'A'`, `"a"` | ASCII value |

WLA-DX accepts `$NN` and `0xNN` for hex. The `#NN` syntax used by Pasmo/SjASMPlus is **not** supported.

### Memory Map Directives

These are required at the top of every source file:

| Directive | Use |
|---|---|
| `.memorymap` ... `.endme` | Define the memory layout: slots and their addresses |
| `.rombankmap` ... `.endro` | Define the bank layout: bank sizes and count |
| `.slot N` | Assemble into slot N (from the memory map) |
| `.bank N [slot=K]` | Assemble into bank N (assigned to slot K) |
| `.org address` | Set assembly address within current bank |

### Data Definitions

| Directive | Use |
|---|---|
| `.db b1, b2, ...` | Define bytes (also: `.byte`) |
| `.dw w1, w2, ...` | Define words, little-endian (also: `.word`) |
| `.dl l1, l2, ...` | Define longs (32-bit) |
| `.dd d1, d2, ...` | Define double words (32-bit, alternative) |
| `.ds count [, fill]` | Define storage — emit `count` bytes of `fill` |
| `.asciitable` ... `.enda` | Define a character mapping |
| `.db "text"` | Define string bytes |

### Object and Section Control

| Directive | Use |
|---|---|
| `.section "name" [flags]` ... `.ends` | Define a section with optional flags (`force`, `bank N`, `align`, `overwrite`) |
| `.ramsection "name" [flags]` ... `.endram` | Like `.section` but for uninitialised RAM |
| `.export name` | Export a symbol for the linker |
| `.import name` | Import a symbol (uncommon — linker resolves by default) |
| `.background symbol` | Mark symbol as a background reference (resolved later) |

### Macros and Structured Code

WLA-DX has a powerful macro system with REPT, IRP-style expansion via `.rept`, named parameters, and conditionals:

```z80
        .macro CLEAR_N count
        ld   (hl), 0
        ld   b, \count - 1
.loop:
        inc  hl
        ld   (hl), 0
        djnz .loop
        .endm
```
#### Repeat Loops

```z80
        ; Unroll 4 iterations
        .rept 4
        sla   l
        rl    h
        .endr
```

### Conditional Assembly

```z80
        .if defined DEBUG_BUILD
        ; debug-only code
        .endif

        .ifdef TARGET_48K
        ; ...
        .else
        ; ...
        .endif
```

### Structs

WLA-DX supports `.struct` blocks for defining record types:

```z80
        .struct game_object
            x       db
            y       db
            tile    db
            flags   db
        .endst

        ; Use the struct
        .ramsection "game objects" bank 0 slot 0
            player  instanceof game_object
            enemies instanceof game_object 10
        .ends
```

This is a feature most other Z80 assemblers lack, and is the main reason some developers choose WLA-DX for larger projects.

---

## Command-Line Reference

### `wla-z80` — the assembler

| Flag | Use |
|---|---|
| `-o output.o` | Output object file |
| `-i` | Add list file information (for debugging) |
| `-q` | Quiet mode |
| `-v` | Verbose mode |
| `-t` | Output test assembly (no object file) |
| `-m` | Output makefile-style dependencies |
| `-M FILE` | Write dependencies to FILE |
| `-d` | Disable warnings |
| `-s` | Output symbol file |
| `-I DIR` | Add DIR to include path |
| `-D NAME[=VALUE]` | Define a symbol |
| `-x` | Add the WLA-DX-generated include path automatically |

### `wlalink` — the linker

| Flag | Use |
|---|---|
| `-b [type]` | Output format (`-b ROM` for ROM, `-b PRG` for Commodore, `-b BIN` for raw binary) |
| `-o output` | Output file name |
| `-r [addr]` | Set ROM address |
| `-S` | Output symbol file |
| `-d` | Disable warnings |
| `-v` | Verbose mode |
| `-i FILE` | Read link script from FILE |
| `-L DIR` | Add DIR to library search path |
| `-l LIB` | Link against library LIB |

### Typical Workflow

```bash
# Single-file project
wla-z80 -o main.o main.s
wlalink -b BIN -o program.bin main.o

# Multi-file project
wla-z80 -o main.o main.s
wla-z80 -o screen.o screen.s
wla-z80 -o input.o input.s
echo "[objects]\nmain.o\nscreen.o\ninput.o" > linkfile.ini
wlalink -b BIN -o program.bin linkfile.ini
```

The `linkfile.ini` lists object files and library paths in a simple INI-style format. This is how WLA-DX handles multi-file projects.

---

## When to Choose WLA-DX

### Strengths

- **Multi-CPU support** — one toolchain for Z80, 6502, 65816, Game Boy, SNES SPC700, PC Engine
- **Powerful linker** — proper object files, bank-aware placement, sections, and library archives
- **Structs** — `.struct` blocks are unique among Z80 assemblers and very useful for game development
- **Memory map directives** — explicit and self-documenting
- **Active maintenance** — Ville Helström still commits regularly
- **Strong documentation** — extensive examples and a working test suite

### Weaknesses

- **Verbose preamble** — the `.memorymap` / `.rombankmap` requirement adds friction for simple projects
- **No Spectrum-specific output** — no `.tap`, `.tzx`, `.sna`, `.nex` output (use a wrapper)
- **No ZX Spectrum Next Z80N support**
- **`$NN` hex only** (no `#NN`) — porting SjASMPlus source requires conversion
- **GPL license** — stricter than Pasmo's public domain or vasm's MPL

### Comparison Matrix

| Feature | WLA-DX | [vasm](vasm.md) | [Pasmo](pasmo.md) | [SjASMPlus](sjasmplus.md) | [z88dk z80asm](z88dk_z80asm.md) |
|---|---|---|---|---|---|
| Year started | 1998 | 2002 | 2001 | 2004 | 1990s |
| Multi-CPU support | ✅ (many) | ✅ (many) | ❌ | ⚠️ | ✅ |
| Hex `$NN` syntax | ✅ | ✅ | ✅ | ✅ | ✅ |
| Hex `#NN` syntax | ❌ | ❌ | ✅ | ✅ | ✅ |
| Object files + linker | ✅ | ✅ | ❌ | ❌ | ✅ |
| ROM/RAM banking model | ✅ | ⚠️ | ❌ | ⚠️ | ✅ |
| Structs | ✅ | ❌ | ❌ | ⚠️ | ⚠️ |
| Spectrum-specific output | ❌ | ❌ | ✅ | ✅ | ⚠️ (via `appmake`) |
| Z80N (Next) support | ❌ | ⚠️ | ❌ | ✅ | ✅ |
| License | GPL-2+ | MPL-2 | Public domain | BSD-2 | BSD-3 |

### Decision Guide

Choose **WLA-DX** when:
- You also develop for Game Boy, NES, SNES, or PC Engine and want one toolchain
- You want explicit memory-map declarations in your source (good documentation)
- You need `.struct` for complex game data

Choose **[vasm](vasm.md)** when:
- You want a similar feature set but with a cleaner, less verbose syntax
- You prefer the Motorola/Amiga macro dialect

Choose **[SjASMPlus](sjasmplus.md)** when:
- You target ZX Spectrum Next
- You want `.nex`, `.tap`, `.sna` output directly

---

## Common Pitfalls

1. **Forgetting `.memorymap` / `.rombankmap`** — WLA-DX will refuse to assemble without these. They are not optional.

2. **Using `#NN` hex** — WLA-DX rejects it. Use `$NN`.

3. **Expecting `.tap` output** — WLA-DX produces raw binaries, not Spectrum-specific formats. Post-process with `bin2tap` or `appmake`.

4. **Section names must be quoted strings** — `.section "code" ... .ends`, not `.section code ... .ends`. The quotes are mandatory.

5. **Bank sizes must be powers of two** — WLA-DX enforces this. A bank size of `$3000` will fail.

6. **The `.ends` directive** — different sections in WLA-DX all close with `.ends`, not `.endsection` or `.endme`. This can be confusing because `.memorymap` closes with `.endme` and `.rombankmap` closes with `.endro`.

7. **GPL-2.0 license implications** — if your project is closed-source commercial, the GPL-2.0 license of WLA-DX (which only affects the assembler, not your code) is still permissive enough to use. But consult a lawyer if you have concerns.

---

## FAQ

**Q: What does "WLA" stand for?**

A: Originally *Where's the Line Assembly?* — a joke name from the 1990s. Later retroactively expanded as *Workshop for Local Assembly*. Most users just say "WLA".

**Q: Why the long preamble for every source?**

A: Because WLA-DX was designed for banked-ROM targets (Game Boy, NES), the memory map must be declared explicitly. This is more verbose than Pasmo's "just write `ORG`" but it is also more explicit and self-documenting.

**Q: Can I produce a `.tap` file from WLA-DX output?**

A: Yes. Use a wrapper: assemble to `.bin` with `wlalink`, then convert with `bin2tap` (from fuse-utils), `appmake` (from z88dk), or a small Python script.

**Q: Does WLA-DX support ZX Spectrum Next Z80N?**

A: No. For Next development, use [SjASMPlus](sjasmplus.md).

**Q: What are `.struct` and `.ramsection` for?**

A: `.struct` lets you define record types (like C structs) — useful for game entities, screen layouts, etc. `.ramsection` lets you declare uninitialised RAM variables that the linker places in a designated memory region. Together they make WLA-DX feel more like a higher-level assembler than its competitors.

**Q: Can I use WLA-DX for a multi-target project (e.g., a game released for both Spectrum and Game Boy)?**

A: Yes, that's the original use case. You can share macros, struct definitions, and logic code via `.include`, and use `.ifdef TARGET_SPECTRUM` / `.ifdef TARGET_GAMEBOY` to switch CPU-specific instructions.

---

## Cross-References

- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [vasm.md](vasm.md) — another portable multi-CPU assembler
- [pasmo.md](pasmo.md) — simpler Z80-only alternative
- [sjasmplus.md](sjasmplus.md) — the Spectrum-focused alternative
- [z88dk_z80asm.md](z88dk_z80asm.md) — the z88dk-integrated alternative
- [zmac.md](zmac.md) — classic cross-assembler (pending)
- [rasm.md](rasm.md) — fast modern cross-assembler (pending)
- [debugging.md](debugging.md) — debugging strategies
- [vscode_integration.md](vscode_integration.md) — IDE setup

---

## References

- Ville Helström — *WLA-DX home page*, [github.com/vhelin/wla-dx](https://github.com/vhelin/wla-dx)
- WLA-DX examples directory — `examples/` in the WLA-DX repository
- WLA-DX documentation — `documentation/` in the repository
- GPL-2.0-or-later license — see `LICENSE` in the WLA-DX repository
- Homebrew formula — `brew install wla-dx` on macOS
