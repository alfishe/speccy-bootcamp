[← Home](../README.md) · [Toolchain](README.md)

# ZXASM 3.0 — Russian-Scene Native Assembler with STS Integration

**ZXASM** (also written **ZX-ASM** or **ZX Assembler**) is a Russian-developed native Z80 assembler for ZX Spectrum clones, with version 3.0 being the most widely known release. It was created in the mid-to-late 1990s by developers in the Russian Spectrum scene, where it served as an alternative to the dominant [ALASM](alasm_sts.md). ZXASM's distinguishing feature was its **tight integration with the [STS](alasm_sts.md) debugger** — the same STS paired with ALASM — giving developers a choice of editor while keeping the same debugging tool.

ZXASM occupies a position in the Russian Spectrum scene analogous to a "second-tier" native assembler: less universally adopted than ALASM or [XAS](xas_assembler.md), but with a loyal following among developers who preferred its editor and workflow.

> [!NOTE]
> This article covers **ZXASM** the Russian-scene native assembler. The name has been used by several unrelated tools over the years (including some cross-assemblers). When researching, look for version 3.0+ and STS integration to confirm you have the Russian-scene native tool.

> [!WARNING]
> Primary documentation for ZXASM is sparse and primarily in Russian. The historical details in this article are reconstructed from Russian-scene archives, forum discussions, and the tool's relationship with STS. Some specific details (exact release dates, author names) may be incomplete or approximate.

---

## Quick Start

ZXASM runs on ZX Spectrum clones (Pentagon, Scorpion, Kay, etc.) with TR-DOS. To bootstrap, you typically load ZXASM from a TR-DOS disk:

```basic
LOAD *"m";1;"zxasm30"
```

Then within ZXASM, you write Z80 source in the editor:

```z80
        ORG  #8000

START:  LD   HL, MESSAGE
        CALL PRINT_STRING
        RET

MESSAGE:
        DEFB "Hello, World!", 13, 0

PRINT_STRING:
        LD   A, (HL)
        OR   A
        RET  Z
        RST  16
        INC  HL
        JR   PRINT_STRING

        END  START
```

Press the assemble key, and ZXASM produces machine code at the address specified by `ORG`. To debug, you can hot-swap to STS (the same STS that pairs with ALASM) and step through the code.

---

## History and the STS Ecosystem

ZXASM appeared in the mid-1990s, during the peak of the Russian Spectrum clone era (1993-2000). This period saw a flourishing of native development tools aimed at the Pentagon, Scorpion, and Kay clones that dominated the Russian-speaking market. The dominant native assembler of this period was [ALASM](alasm_sts.md) (versions 3.0 through 5.x), paired with the **STS** monitor-debugger.

ZXASM entered this market as an **alternative editor** — same backend concepts (two-pass assembly, TR-DOS-native, STS debugging) but a different front-end. The Russian scene had a strong culture of editor wars: developers who preferred ALASM's macro style stayed with ALASM; those who preferred ZXASM's editor and key bindings switched. Both shared STS as the common debugger.

### The STS Pairing

STS (Step Trace System) is a hardware-assisted monitor-debugger developed for the Russian clone scene. Its key features include:

- **Cycle-exact single-stepping** via custom hardware on Pentagon/Scorpion
- **Reverse debugging** (rollback to any prior state)
- **Conditional tracing** (break when an address is read or written)
- **Full register and memory inspection**

STS was paired primarily with ALASM but also integrated with ZXASM and **TASM 128** (the Russian TASM variant, distinct from both the UK native TASM and the MS-DOS TASM covered in [tasm_cross.md](tasm_cross.md)). See [native_toolchain.md](native_toolchain.md) for the broader STS ecosystem.

The integration worked by sharing a common memory layout and bank-switching protocol. The user could be editing in ZXASM, press a hot-key, and instantly be in STS looking at the same code with breakpoints set. This tight loop (edit → assemble → debug → edit) was the core productivity advantage of the Russian scene's native development stack.

### Version History

ZXASM's version history is not as well documented as ALASM's. Known versions:

| Version | Approximate Year | Notes |
|---|---|---|
| 1.x | 1994-1995 | Early versions, limited features |
| 2.x | 1996-1997 | Improved editor, STS integration refined |
| 3.0 | 1998-1999 | The widely-adopted version |
| 4.x+ | 2000s | Continued development; less widely used as the Russian scene declined |

ZXASM 3.0 was the canonical version that appears in most archives. Later versions added features but were less widely adopted as the Russian Spectrum scene contracted.

### Place in the Russian Scene

ZXASM was used by several demoscene crews and individual developers. It did not dominate any particular sub-niche the way ALASM dominated the St. Petersburg scene or XAS dominated the Moscow scene. Its user base was distributed and loyal but not concentrated enough to make ZXASM a "scene standard".

Concrete commercial or demoscene works produced with ZXASM are harder to identify than ALASM-produced works, because ZXASM was less likely to be mentioned in production credits. The Russian scene tradition was to credit the demo or game, not the toolchain.

---

## Source Language

ZXASM's source language is close to ALASM and uses standard Russian-scene conventions. Sinclair-style hex (`#NN`) is preferred.

### Number Formats

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `#` | `#FE`, `#4000` | **Sinclair style** — preferred |
| Hex with `H` suffix | `0FEh` | Also accepted |
| Binary with `%` | `%10101010` | |
| Character | `'A'` | ASCII value |

### Operators

Full expression evaluator with arithmetic, bitwise, and comparison operators — comparable to ALASM and modern cross-assemblers.

### Directives

ZXASM's directive set is similar to ALASM's, with `DEFB`/`DEFW`/`DEFS`/`DEFM` and `ORG`/`END`:

| Directive | Use |
|---|---|
| `ORG address` | Set assembly address |
| `DEFB b1, b2, ...` | Define bytes (also: `DB`) |
| `DEFW w1, w2, ...` | Define words (also: `DW`) |
| `DEFS count [, fill]` | Define storage |
| `DEFM "text"` | Define message bytes |
| `EQU` or `=` | Define a constant |
| `INCLUDE "file"` | Include source file (TR-DOS) |
| `INCBIN "file"` | Include binary file (TR-DOS) |
| `IF expr` / `ELSE` / `ENDIF` | Conditional assembly |
| `MACRO name(params)` ... `ENDM` | Define a macro |
| `REPT count` ... `ENDR` | Repeat block |
| `MODULE name` | Set module/namespace prefix |
| `ENDMOD` | End module |
| `END [label]` | End of source |

### Module / Namespace Support

Like ALASM, ZXASM supports a module prefix system for organizing large projects. Labels declared within a `MODULE` block are prefixed with the module name, allowing multi-file projects without label collisions. This is one of the features that distinguishes the Russian-scene assemblers (ALASM, ZXASM, XAS) from the simpler Western tools of the same era.

### Macros

ZXASM supports named-parameter macros and `REPT` for repeat blocks, comparable to ALASM. The macro language is not as elaborate as XAS's (no IRP or string-manipulation built-ins), but covers the common cases:

```z80
        MACRO CLEAR_N(addr, count)
        LD   HL, addr
        LD   (HL), 0
        LD   DE, addr + 1
        LD   BC, count - 1
        LDIR
        ENDM

        ; Usage
        CLEAR_N(#4000, 6144)   ; Clear screen memory
        CLEAR_N(#5800, 768)    ; Clear attribute memory
```

---

## Editor and Workflow

ZXASM's editor is a full-screen text editor with multi-window support on the larger Russian clone hardware. Key features:

- **Multi-file editing** — work on several source files simultaneously (subject to RAM)
- **Block operations** — copy/move/delete blocks of lines
- **Search and replace** — including across multiple files
- **TR-DOS file operations** — load/save source files directly from disk
- **Configurable key bindings** — Russian vs Latin keyboard layout switching (important for Cyrillic comments)
- **Syntax highlighting** — limited; mostly distinguishing labels, mnemonics, and comments by attribute

### Cyrillic Comment Support

A distinctive feature of Russian-scene tools is full **Cyrillic comment support**. Russian developers could write comments in their native language using either the Soviet GOST cipher (a latin-character transliteration of Cyrillic) or actual Cyrillic characters when the hardware supported it. ZXASM, like ALASM and XAS, handled both gracefully.

### Cyrillic in Modern Cross-Assemblers

Modern cross-assemblers (SjASMPlus, Pasmo) handle UTF-8 Cyrillic directly. If you are porting ZXASM source with Cyrillic comments to a modern tool, ensure your editor is set to UTF-8 and that you use the appropriate encoding when saving.

---

## Comparison with Contemporaries

| Feature | ZXASM 3.0 | [ALASM 4/5](alasm_sts.md) | [XAS 7-9](xas_assembler.md) | [TNI ASM](tniasm.md) |
|---|---|---|---|---|
| Year (main version) | 1998-1999 | 1995-2000 | 1996-2000 | 1997-2006 |
| Editor style | Full-screen, multi-window | Full-screen, multi-window | Multi-window IDE-like | Multi-window IDE-like |
| STS integration | ✅ | ✅ | ⚠️ | ❌ (own debugger) |
| Macros | ✅ (named params, REPT) | ✅ (similar) | ✅ (3-layer system) | ✅ (named params) |
| Conditional assembly | ✅ | ✅ | ✅ | ✅ |
| Module / namespace | ✅ | ✅ | ❌ | ✅ |
| IRP / IRPC | ❌ | ⚠️ | ✅ | ❌ |
| TR-DOS native | ✅ | ✅ | ✅ | ✅ |
| Cyrillic comments | ✅ | ✅ | ✅ | ✅ |

### ZXASM vs ALASM

The choice between ZXASM and ALASM was largely a matter of editor preference. Both supported the same workflow (STS debugging, TR-DOS, multi-file projects). ALASM had a larger user base, more documentation, and was more widely taught in Russian-scene tutorials. ZXASM had a smaller but loyal user base.

### ZXASM vs XAS

XAS focused on **elaborate macro processing** for code generation. ZXASM had solid macros but not the same three-layer system. If you needed algorithmic code generation (sine tables, unrolled blits, complex data transformations), XAS was the better choice. If you wanted a more conventional editor with solid macro support, ZXASM (or ALASM) was better.

---

## When to Encounter ZXASM Today

### 1. Russian Scene Source Archives

If you are studying source code from the Russian Spectrum scene (1995-2005), there is a moderate chance it was written in ZXASM, particularly if the author was not part of the St. Petersburg ALASM-centric community. The source syntax is similar enough to ALASM that you may not be able to distinguish them without checking the assembler's identity in comments or file headers.

### 2. TR-DOS Disk Image Archives

Russian-scene TR-DOS disk images (`.trd` files) in retro-computing archives often include ZXASM as one of the bundled development tools. These images are typically bootable in emulators like UnrealSpeccy, ZXMAK2, or [ZEsarUX](../11_emulation/).

### Modern Alternatives

For new development targeting ZX Spectrum or Spectrum clones, **do not use ZXASM**. Use:

- **[SjASMPlus](sjasmplus.md)** — modern cross-assembler with all of ZXASM's features and more
- **[Pasmo](pasmo.md)** — minimalist modern alternative
- **[z88dk z80asm](z88dk_z80asm.md)** — if you need object-file linking

---

## Common Pitfalls

1. **Confusion with other ZXASM tools** — search for "ZXASM 3.0" or "ZXASM STS" to find the Russian-scene native assembler.

2. **Russian-language documentation** — ZXASM's manual and most tutorials are in Russian. English documentation is sparse.

3. **TRS-DOS disk images required** — ZXASM runs on TR-DOS, which means you need a TR-DOS disk image and a Beta Disk Interface (or emulator equivalent) to use it.

4. **Russian keyboard layout** — Cyrillic comment support assumes a Russian keyboard layout. On modern systems, you may need to configure your emulator's keyboard mapping.

5. **STS hardware features** — some STS features (cycle-exact single-step, reverse debugging) require Russian clone hardware (Pentagon, Scorpion). On a 48K/128K Spectrum or emulator without STS support, these features are unavailable.

6. **Single-platform** — ZXASM is a native tool and does not run on modern operating systems. Use an emulator (UnrealSpeccy, ZXMAK2, ZEsarUX).

---

## FAQ

**Q: Was ZXASM 3.0 the latest version?**

A: Probably not — there were later versions in the 2000s. But version 3.0 is the most widely archived and the one most modern retro developers encounter.

**Q: Can I assemble ZXASM source with a modern cross-assembler?**

A: Usually yes. The directive set (`ORG`, `DEFB`, `DEFW`, `EQU`, `INCLUDE`, `MACRO`, `REPT`, `MODULE`) is largely compatible with SjASMPlus and z88dk z80asm. Module prefix syntax may need adjustment (different assemblers use different separators). Hex literals (`#NN`) work directly.

**Q: Did ZXASM support ZX Spectrum Next (Z80N)?**

A: No. ZXASM is a 1990s native tool that predates the Spectrum Next by 20 years. Use [SjASMPlus](sjasmplus.md) for Z80N.

**Q: Where can I download ZXASM?**

A: Search Russian retro-computing archives for TR-DOS disk images that include ZXASM 3.0. Specific sites include zx-pk.ru (the largest Russian Spectrum forum) and various TR-DOS software collections.

**Q: Was ZXASM better than ALASM?**

A: Neither was strictly better. They had similar feature sets and similar performance. The choice was largely about editor preference and what your local community used.

---

## Cross-References

- [native_toolchain.md](native_toolchain.md) — survey of all native Spectrum assemblers
- [alasm_sts.md](alasm_sts.md) — the dominant Russian-scene native assembler and STS debugger
- [xas_assembler.md](xas_assembler.md) — the Russian macro specialist
- [tniasm.md](tniasm.md) — another Russian native assembler
- [tasm_native.md](tasm_native.md) — the Russian-scene TASM 128 (different from this ZXASM)
- [tasm_cross.md](tasm_cross.md) — unrelated MS-DOS cross-assembler sharing the TASM name
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — modern alternatives

---

## References

- Russian Spectrum scene archives — zx-pk.ru forum and TR-DOS software collections
- ALASM and STS documentation (ZXASM's primary integration partners)
- Discussions on Russian retro-computing forums clarifying the relationship between ZXASM, ALASM, and XAS
- Comparison with contemporaries based on the documented feature sets of ALASM, XAS, and TNI ASM
