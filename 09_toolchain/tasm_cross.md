[← Home](../README.md) · [Toolchain](README.md)

# TASM — The Table-Driven Cross-Assembler

**TASM** (Turbo Assembler) is a table-driven cross-assembler by **Thomas N. Anderson** (Squakvalley Software), first released in 1990 for MS-DOS. Unlike most Z80 assemblers that hard-code the instruction encoding, TASM is **table-driven**: the CPU's instruction set is defined in an external table file (`.TAB`), and the assembler reads the table to know which mnemonics are valid and how to encode them. This design lets TASM support many CPUs (Z80, 6502, 68000, 8051, 8085, and more) from the same executable, just by loading the appropriate table.

TASM was the dominant cross-assembler for MS-DOS throughout the 1990s and early 2000s. It was used extensively for Game Boy, NES, and ZX Spectrum development before modern cross-platform tools like SjASMPlus and z88dk became available. Although development stopped around 2003 (version 3.2 being the final release), TASM source files are still found in many archived projects, and the tool runs cleanly under DOSBox on modern systems.

> [!NOTE]
> This article covers **TASM the cross-assembler** (Anderson's MS-DOS tool). For native Spectrum assemblers, see [native_toolchain.md](native_toolchain.md). TASM is **not** related to Borland Turbo Assembler (also called TASM), which targets x86.

---

## Quick Start

Download TASM from the [Squakvalley Software archive](http://www.tni.de/old/tasm.html) or a retro-computing mirror. It runs under MS-DOS, DOSBox, or any DOS-compatible environment.

Write `hello.asm`:

```z80
        .org  8000h

start:  ld    hl,message
        call  print_string
        ret

message:
        .db   "Hello, World!",0Dh,0

print_string:
        ld    a,(hl)
        or    a
        ret   z
        rst   10h
        inc   hl
        jr    print_string

        .end
```

Assemble using the Z80 table:

```bash
tasm -80 hello.asm hello.bin
```

The `-80` flag tells TASM to use the Z80 instruction table (`TASM80.TAB`). Other flags include `-65` for 6502, `-48` for 8048, `-51` for 8051, and `-85` for 8085.

---

## History and Design Philosophy

Thomas N. Anderson started TASM in 1990 to support his embedded systems consulting work, which spanned multiple CPU families. Rather than writing a separate assembler for each CPU, he designed TASM as a **generic assembler engine** driven by external instruction tables. This was a well-known technique in the 1980s (used by AVOCET, 2500AD, and other professional cross-assembler suites), but Anderson's TASM brought it to the shareware market at an affordable price.

### The Table-Driven Architecture

The core TASM executable (`TASM.EXE`) contains:

- A **lexical analyzer** that reads source text
- An **expression evaluator** for assembly-time computation
- A **two-pass assembler engine** that resolves labels and produces object code
- A **table parser** that reads `.TAB` files

The `.TAB` file for each CPU defines:

- Valid mnemonics (e.g., `LD`, `JP`, `CALL`)
- Operand syntax patterns (e.g., `A,(HL)`, `A,nn`)
- Binary encoding templates
- Addressing mode selection rules

This separation means adding a new CPU is just a matter of writing a new `.TAB` file — no recompilation needed. Anderson shipped tables for Z80, 6502, 68000, 8048, 8051, 8085, 68HC11, and several others.

### Version History

| Year | Version | Highlights |
|---|---|---|
| 1990 | 1.0 | First public release; Z80, 6502, 8085 tables |
| 1993 | 2.0 | 68000 and 8051 tables; improved macro support |
| 1997 | 3.0 | Label table improvements; bug fixes |
| 2001 | 3.1 | Final shareware release; final documentation update |
| 2003 | 3.2 | Last known version; development stops |

TASM was distributed as **shareware** with a nominal registration fee. After Anderson stopped development, the tool entered the retro-computing community's standard toolkit. The license is still shareware — technically you should register, but the author is no longer accepting registrations.

### Why TASM Mattered

Before SjASMPlus (2004), z88dk (late 1990s but not widely known until the 2010s), and Pasmo (2001), TASM was often the only practical cross-assembler available on PC. It was particularly important for:

- **Game Boy homebrew** in the late 1990s (before WLA-DX and RGBDS became standard)
- **ZX Spectrum** developers who had moved from native tools to PCs
- **Embedded systems** work using 8051, 8048, and Z80 derivatives
- **NES** development in the early homebrew scene

---

## Source Language

TASM uses dot-led directives (`.org`, `.db`, `.byte`) and a straightforward expression evaluator. The syntax is close to 1980s Zilog notation.

### Number Formats

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `H` suffix | `0FEh`, `8000h` | **Default hex format** — must start with a digit |
| Hex with `$` | `$FE` | Zilog syntax |
| Hex with `0x` | `0xFE` | C syntax |
| Binary with `B` suffix | `10101010b` | Must start with 0 or 1 |
| Binary with `%` | `%10101010` | |
| Character | `'A'`, `"a"` | ASCII value |

TASM does **not** accept `#NN` (Sinclair style) for hexadecimal. Use `H` suffix or `$` prefix.

### Operators

| Operator | Meaning |
|---|---|
| `+`, `-`, `*`, `/`, `%` | Arithmetic |
| `&`, `\|`, `^`, `~` | Bitwise AND/OR/XOR/NOT |
| `<<`, `>>` | Bitwise shifts |
| `$` | Current address counter |

TASM's expression evaluator is more limited than modern cross-assemblers. There are no comparison operators, ternary, or logical operators at assembly time. Use conditional assembly directives for branching.

### Directives

| Directive | Use |
|---|---|
| `.org address` | Set assembly address |
| `.align n` | Pad to multiple of `n` bytes |
| `.db b1, b2, ...` | Define bytes (also: `.byte`) |
| `.dw w1, w2, ...` | Define words, little-endian (also: `.word`) |
| `.dl l1, l2, ...` | Define longs (32-bit) |
| `.byte "text"` | Define string bytes |
| `.block size` | Define storage (emit `size` zero bytes) |
| `.word label` | Define a word pointing to `label` |
| `.equ name, value` | Define a constant (also: `label .equ value`) |
| `.include "file"` | Include a source file |
| `.incbin "file"` | Include a binary file |
| `.if expr` / `.else` / `.endif` | Conditional assembly |
| `.ifdef name` / `.ifndef name` | Conditional on symbol definition |
| `.define name value` | Define a text substitution macro |
| `.module name` | Set a module prefix for labels (not full namespacing) |
| `.end` | End of source (required) |

### Macros

TASM supports two kinds of macros:

**Text substitution macros** via `.define`:

```z80
        .define SCREEN_ATTR 5C8Dh
        ld    a,(SCREEN_ATTR)
```

**Block macros** via `.macro` / `.endm`:

```z80
        .macro MUL_HL_BY_8
        sla   l
        rl    h
        sla   l
        rl    h
        sla   l
        rl    h
        .endm

        ; Usage
        MUL_HL_BY_8
```

Parameterised macros use `\1`, `\2`, etc. for positional arguments:

```z80
        .macro CLEAR_N
        ld    (hl),0
        ld    b,\1 - 1
.loop:  inc   hl
        ld    (hl),0
        djnz  .loop
        .endm
```

TASM does not support IRP, REPT, or recursive macros. For complex code generation, pre-process the source with a separate tool.

### Label Module Prefixing

TASM's `.module` directive sets a prefix for subsequent labels:

```z80
        .module driver
init:   ; This label becomes "driver.init"
        ret
```

This is simpler than full namespacing (as in [z88dk z80asm](z88dk_z80asm.md)) but useful for avoiding collisions in multi-file projects that are concatenated via `.include`.

---

## Command-Line Reference

| Flag | Use |
|---|---|
| `-80` | Use Z80 table (`TASM80.TAB`) |
| `-65` | Use 6502 table |
| `-48` | Use 8048 table |
| `-51` | Use 8051 table |
| `-85` | Use 8085 table |
| `-b` | Produce raw binary output (no header) |
| `-f` | Output format selection (see below) |
| `-s` | Produce symbol file |
| `-l` | Produce list file (`.lst`) |
| `-t TABFILE` | Use custom table file |
| `-p PASS` | Number of passes (default 2; can increase for complex forward references) |
| `-h` | Produce hex output file (Intel HEX format) |
| `-d` | Debug output |
| `-c` | Case-insensitive label matching |
| `-q` | Quiet mode |
| `-a LABEL` | Auto-set assembly address from label |

### Output Formats

TASM can produce several output formats, selected by the `-f` flag:

| `-f` | Format | Description |
|---|---|---|
| `1` (default) | Raw binary | No header, just bytes |
| `2` | Intel HEX | Standard `.hex` format with address info |
| `3` | Motorola S-record | `.s19` / `.s28` / `.s37` formats |
| `4` | TASM object format | TASM's proprietary object format |

For ZX Spectrum work, use the default (`-f1`) raw binary. To produce a `.tap` file, post-process with a separate tool.

### Typical Command Lines

```bash
# Assemble Z80 source to raw binary
tasm -80 -b hello.asm hello.bin

# Assemble 6502 source (for NES)
tasm -65 -b game.asm game.bin

# Assemble with list and symbol files
tasm -80 -b -l -s hello.asm hello.bin

# Increase passes for complex forward references
tasm -80 -b -p 3 complex.asm complex.bin
```

---

## When to Encounter TASM Today

TASM is **legacy software**. It has not been updated since 2003, and modern alternatives are strictly better for new projects. You will encounter TASM in two contexts:

### 1. Historical Source Archives

Many ZX Spectrum, Game Boy, and NES homebrew projects from the 1990s and early 2000s were written in TASM syntax. If you are studying or modifying these sources, you can either:

- Run TASM under DOSBox to reassemble them
- Or port the source to a modern cross-assembler (usually easy — TASM's syntax is close to SjASMPlus with minor directive renaming)

### 2. Educational Resources

Some older tutorials (especially for Game Boy and NES development) use TASM. If you are following such a tutorial, TASM under DOSBox works fine.

### Modern Equivalents

For new development, prefer:

- [[SjASMPlus]([sjasmplus](https://github.com/z00m128/sjasmplus).md)](https://github.com/z00m128/sjasmplus) — for ZX Spectrum and ZX Spectrum Next
- **[WLA-DX](wla_dx.md)** — for Game Boy, NES, SNES, and multi-CPU work
- **[vasm](vasm.md)** — for portable multi-CPU work
- **RGBDS** — for Game Boy specifically (the modern standard)

---

## Comparison Matrix

| Feature | TASM | [SjASMPlus](sjasmplus.md) | [WLA-DX](wla_dx.md) | [vasm](vasm.md) | [Pasmo](pasmo.md) |
|---|---|---|---|---|---|
| Year started | 1990 | 2004 | 1998 | 2002 | 2001 |
| Last release | 3.2 (2003) | Active | Active | Active | Active |
| Multi-CPU | ✅ (table-driven) | ⚠️ (Z80N) | ✅ (12 CPUs) | ✅ (many) | ❌ |
| Hex `#NN` syntax | ❌ | ✅ | ❌ | ❌ | ✅ |
| Hex `H` suffix | ✅ (preferred) | ✅ | ✅ | ✅ | ✅ |
| Direct `.tap` output | ❌ | ✅ | ❌ | ❌ | ✅ |
| Macros (IRP, REPT) | ❌ | ✅ | ✅ | ✅ | ❌ |
| Object files | ❌ | ❌ | ✅ | ✅ | ❌ |
| Native OS support | MS-DOS only | All | All | All | All |
| License | Shareware | BSD-2 | GPL-2+ | MPL-2 | Public domain |

---

## Common Pitfalls

1. **Requires DOSBox on modern OSes** — TASM is a 16-bit DOS program. On 64-bit Windows, macOS, and Linux, you need DOSBox or a similar emulator to run it.

2. **Table file must be in the same directory** — TASM looks for `TASM80.TAB` (or the relevant CPU table) in the current directory or the TASM installation directory. If the table is not found, assembly fails.

3. **`.end` is required** — without `.end` at the end of source, TASM may produce errors or truncate the output.

4. **`.org` vs ORG** — TASM uses dot-led directives (`.org`). The non-dot form (`org`) is accepted in some versions but not all.

5. **Hex format** — TASM prefers `H` suffix (`0FEh`). The `#NN` Sinclair style is **not** accepted.

6. **Limited expression evaluator** — no comparison operators, ternary, or logical operators at assembly time.

7. **No multi-file linking** — TASM is single-source only. Use `.include` for multi-file projects.

8. **Undocumented instruction support varies** — some `.TAB` files support undocumented Z80 instructions, others do not. Check the table you are using.

---

## FAQ

**Q: Is TASM related to Borland Turbo Assembler?**

A: No. Borland's TASM targets x86 and uses different syntax. Anderson's TASM targets embedded and retro CPUs. The name collision is unfortunate.

**Q: Can TASM produce a `.tap` file?**

A: No. TASM produces raw binary, Intel HEX, or Motorola S-record. To produce a `.tap`, post-process with `bin2tap` or `appmake`.

**Q: Where can I download TASM?**

A: From [the Squakvalley Software archive](http://www.tni.de/old/tasm.html) or various retro-computing mirrors. The shareware package includes all CPU tables.

**Q: Should I learn TASM for new projects?**

A: No. Use [SjASMPlus](sjasmplus.md) for ZX Spectrum, [WLA-DX](wla_dx.md) for Game Boy/NES, or [vasm](vasm.md) for portable multi-CPU work. TASM is only relevant for historical source.

**Q: Can I modify the `.TAB` file to add custom instructions?**

A: Yes. The `.TAB` file format is documented in TASM's manual. You can add support for undocumented Z80 instructions, custom addressing modes, or even fictional CPUs. This is TASM's most unique feature.

---

## Cross-References

- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [sjasmplus.md](sjasmplus.md) — modern Spectrum-focused alternative
- [pasmo.md](pasmo.md) — modern minimalist alternative
- [wla_dx.md](wla_dx.md) — modern multi-CPU alternative
- [vasm.md](vasm.md) — modern portable multi-CPU alternative
- [z88dk_z80asm.md](z88dk_z80asm.md) — modern object-file alternative
- [native_toolchain.md](native_toolchain.md) — survey of native assemblers

---

## References

- Thomas N. Anderson — *TASM User's Manual*, Squakvalley Software
- TASM archive — [tni.de/old/tasm.html](http://www.tni.de/old/tasm.html)
- TASM CPU table documentation — included in the TASM distribution
- Game Boy homebrew history — TASM's role documented on various retro-computing wikis
- Shareware license — see `LICENSE.TXT` in the TASM distribution
