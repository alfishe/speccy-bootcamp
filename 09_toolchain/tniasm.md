[← Home](../README.md) · [Toolchain](README.md)

# TNI ASM — The Late-Era Native Russian Assembler

**TNI ASM** (ТНИ АСМ, also written **TniAsm** or **tniAsm**) is a native Z80 assembler for ZX Spectrum clones, developed by **Neo** (a Russian demoscene developer from the SKR (Spectrum Klan Rostov) group) starting in 1997. It is one of the latest native Spectrum assemblers, reaching its mature form in versions 0.x → 0.54+ around 2003–2006, just as the Russian native Spectrum scene was contracting. The name "TNI" comes from the developer's group or personal branding; "ASM" is the standard abbreviation for assembler.

TNI ASM is the **second-tier** native Russian assembler after [ALASM](alasm_sts.md) and [XAS](xas_assembler.md). It never dominated the scene the way ALASM did, but it earned a devoted following for its **clean design, multi-window editor, and forward-looking feature set** (structures, namespaces, modern macro language) that anticipated cross-platform tools like SjASMPlus by several years.

> [!NOTE]
> This article is the **per-tool reference** for TNI ASM specifically. For the broader native-toolchain survey, see [native_toolchain.md](native_toolchain.md). For the dominant native Russian assembler, see [alasm_sts.md](alasm_sts.md).

---

## Quick Start

TNI ASM runs **on real Spectrum hardware or in an emulator** (Fuse, ZEsarUX, UnrealSpeccy). It is not a cross-assembler. The typical workflow:

1. Download the `TniAsm` `.trd` or `.scl` file from a Russian Spectrum archive (e.g., [trd.speccy.info](http://trd.speccy.info/)).
2. Mount it in your emulator as a TR-DOS disk.
3. Boot TR-DOS, run `LOAD"TniAsm"CODE` to load the assembler, then `RANDOMIZE USR` to the load address (usually printed by the loader).
4. Use the built-in editor to write source, then press the assemble key (typically a function key on the Pentagon keyboard layout).
5. The output binary is written to disk or to memory at the address you specify.

A typical TNI ASM source looks like:

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

This is portable to any modern cross-assembler (Pasmo, SjASMPlus, RASM) with no syntax conversion.

---

## History and Design Philosophy

Neo started TNI ASM in 1997 as a personal project to address what he saw as the limitations of ALASM 3.x and XAS 7.x — the dominant assemblers on the Russian scene at the time. His goals were:

- **Modern macro language** — proper parameterised macros with named arguments (not the `\1`, `\2` convention)
- **Structures and namespaces** — for managing complex projects with many source files
- **Multi-window editor** — with cut/paste, search/replace, and undo
- **Fast assembly** — rivaling ALASM's speed on slow clone hardware
- **TR-DOS native** — the only realistic storage system for Russian clones
- **Cyrillic comments** — for native-language source documentation

TNI ASM was released in a series of 0.x versions, reflecting Neo's perfectionism — he never declared the tool "finished". The 0.42 version (1999) was the first widely-adopted one. The 0.54 version (2003–2006) is considered the canonical mature version.

### Why TNI ASM Mattered

By 1999–2000, the Russian Spectrum scene was contracting. Many developers were transitioning to PCs and cross-platform tools (z88dk's early versions, Pasmo, etc.). Despite this, TNI ASM found a niche:

- **Developers who preferred native Spectrum workflow** — for them, switching to a PC felt like betrayal
- **Educational users** — schools and hobbyists who learned Z80 on a Pentagon and never moved to PC development
- **Demo scene purists** — who insisted on creating demos that ran on real hardware, including the assembler itself

TNI ASM's design influenced later cross-platform tools. Several SjASMPlus features (especially the modern macro language and the `MODULE` system) bear resemblance to TNI ASM conventions, though the tools are unrelated.

### Version History

| Year | Version | Highlights |
|---|---|---|
| 1997 | 0.10 | First internal release |
| 1998 | 0.20 | First public release; multi-window editor |
| 1999 | 0.42 | First widely-adopted version; structures added |
| 2000 | 0.45 | Macro language enhancements |
| 2001 | 0.50 | Namespace support (`MODULE`/`ENDMOD`) |
| 2003 | 0.54 | Mature stable version; considered canonical |
| 2006 | 0.54+ | Final patches; scene declining |

### Maintained By

TNI ASM is essentially a single-author project that ended when Neo moved on from active Spectrum development. The 0.54 version is the last widely-circulated release. Minor patches by other Russian sceners may exist, but there has been no major development since the mid-2000s.

---

## Source Language

TNI ASM's syntax closely matches the ALASM/XAS convention used across the Russian scene — `#NN` hex (also `$NN`), `db`/`dw`/`ds` directives, modern labels with `:`, and `;` for comments.

### Numbers

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `#` | `#FE`, `#4000` | **Preferred on Russian scene** |
| Hex with `$` | `$FE`, `$4000` | Zilog syntax |
| Hex with `0x` | `0xFE` | C syntax |
| Binary with `%` | `%10101010` | |
| Character | `'A'`, `"a"` | ASCII value |

### Operators

TNI ASM has a C-like expression evaluator similar to modern cross-assemblers:

- `+`, `-`, `*`, `/`, `%` — Arithmetic
- `&`, `|`, `^`, `~` — Bitwise
- `<<`, `>>` — Shifts
- `<`, `>`, `<=`, `>=`, `==`, `!=` — Comparison
- `&&`, `||`, `!` — Logical
- `?:` — Ternary

### Built-in Functions

| Function | Returns |
|---|---|
| `lo(x)` / `low(x)` | Low byte |
| `hi(x)` / `high(x)` | High byte |
| `defined(s)` | 1 if symbol is defined |
| `sizeof(s)` | Size of structure instance |

### Directives

| Directive | Use |
|---|---|
| `org address` | Set assembly address |
| `align n` | Pad to multiple of `n` |
| `db b1, b2, ...` | Define bytes |
| `dw w1, w2, ...` | Define words |
| `dd l1, l2, ...` | Define longs |
| `ds count [, fill]` | Define storage |
| `dm "text"` | Define message bytes |
| `phase addr` / `dephase` | Override ORG temporarily |
| `module name` / `endmod` | Open / close a namespaced module |
| `include "file"` | Include a source file |
| `incbin "file"` | Include a binary file |
| `if expr` / `else` / `endif` | Conditional assembly |
| `ifdef sym` / `ifndef sym` | Conditional on symbol existence |
| `define name value` | Define a symbol |
| `undef name` | Undefine a symbol |
| `rept count` / `endr` | Repeat block |
| `irp var, list` / `endm` | Iterate over list |

### Structures

TNI ASM's `struct` directive is one of its forward-looking features:

```z80
        struct game_object
            x       db
            y       db
            tile    db
            flags   db
        ends

        ; Use the struct
player:       game_object            ; one player
enemies:      game_object 16         ; 16 enemies
```

This is the same pattern later adopted by WLA-DX and other modern assemblers.

### Modules

```z80
        module drivers_screen
        public clear_screen
        extern wait_vblank

clear_screen:
        ; ... implementation
        ret

        endmod
```

From outside the module, refer to it as `drivers_screen.clear_screen`.

### Macros

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

TNI ASM macros support named parameters, local labels, recursion (with depth limits), and IRP-style iteration. This is more advanced than ALASM 3.x and matches modern cross-assemblers.

---

## Editor and Workflow

TNI ASM's editor is its **second signature feature** (after the macro language). Unlike ALASM's single-window editor or XAS's fixed multi-window layout, TNI ASM offers a fully flexible multi-window system:

- Up to 9 simultaneously open files
- Cut, copy, paste between windows
- Search and replace with optional case-insensitivity
- Block operations (indent, comment-out, etc.)
- Goto-line and goto-label navigation
- Configurable colors and key bindings
- Macro recording — record a sequence of keystrokes and replay

This was unusual for native Spectrum tools, which typically had a single-window, line-based editor inherited from the 1980s. TNI ASM's editor felt closer to Borland Pascal or Microsoft Edit on PC.

### Assembly Workflow

The typical TNI ASM workflow:

1. Open source files in multiple windows
2. Edit code
3. Press the assemble key (typically `F9` or similar)
4. TNI ASM assembles in the background, displaying errors inline
5. If successful, the binary is saved to disk or kept in memory
6. Press the test key (`F10`) to launch the assembled program in a sub-process (similar to DevPac's MONS integration)

This tight edit-assemble-test loop is what made TNI ASM feel like a modern IDE on a 7 MHz Z80.

---

## When to Encounter TNI ASM Today

TNI ASM is **historically important but not a current development tool**. Modern cross-assemblers (SjASMPlus, RASM, Pasmo) surpass it in features, documentation, and ease of use. You will encounter TNI ASM in two contexts:

### 1. Russian Scene Source Archives

Many Russian Spectrum demos, games, and utilities from the 1999–2006 period were written in TNI ASM. If you are studying or modifying these sources, you may need to:

- Run TNI ASM in an emulator to reassemble them
- Or port the source to a modern cross-assembler (usually easy — TNI ASM syntax is close to SjASMPlus)

### 2. Demoscene Preservation

The Russian Spectrum demoscene has been the subject of active preservation efforts in recent years. Archives like [trd.speccy.info](http://trd.speccy.info/), [zx-art.ru](http://zx-art.ru/), and [speccy.info](http://speccy.info/) hold TNI ASM source files alongside the binaries they produced.

### Modern Equivalents

For new development, the modern cross-assemblers that most closely resemble TNI ASM are:

- **[SjASMPlus](sjasmplus.md)** — similar macro language, similar `MODULE` system, similar overall design
- **[RASM](rasm.md)** — similar speed and modern feature set
- **[WLA-DX](wla_dx.md)** — similar `struct` and multi-window philosophy (though on PC, not native)

For new projects, **prefer SjASMPlus or RASM over TNI ASM**.

---

## Comparison with Other Native Russian Assemblers

| Feature | TNI ASM | [ALASM](alasm_sts.md) | [XAS](xas_assembler.md) |
|---|---|---|---|
| First release | 1997 | 1992 | 1993 |
| Last significant version | 0.54 (2003) | 5.x (2000s) | 9.x (2000s) |
| Scene popularity | Second-tier | **Dominant** | Strong competitor |
| Multi-window editor | ✅ (flexible, up to 9) | ⚠️ (limited) | ✅ (fixed layout) |
| Structures (`struct`) | ✅ | ❌ | ❌ |
| Modules (`module`/`endmod`) | ✅ | ✅ | ⚠️ |
| Named macro parameters | ✅ | ⚠️ (`\1`, `\2`) | ⚠️ |
| IRP / REPT | ✅ | ❌ | ⚠️ |
| Macro recording (editor) | ✅ | ❌ | ❌ |
| Cyrillic comments | ✅ | ✅ | ✅ |
| TR-DOS native | ✅ | ✅ | ✅ |
| STS debugger integration | ❌ | ✅ | ❌ |
| Influenced SjASMPlus | ✅ | ⚠️ | ⚠️ |

TNI ASM's feature set was **ahead of its time** for native tools, which is why it earned its devoted following despite ALASM's dominance.

---

## Common Pitfalls (When Porting Source)

1. **Module and endmod vs SjASMPlus's endmodule** — TNI ASM uses `endmod`; SjASMPlus accepts both `endmod` and `endmodule`. If porting source, you may need to update either directive.

2. **`STRUCT` instantiation syntax** — TNI ASM uses `name: struct_name count`; SjASMPlus uses slightly different syntax. Test after porting.

3. **Macro parameter syntax** — TNI ASM uses named parameters (preferred); SjASMPlus accepts both named and positional. Some TNI ASM source may rely on positional arguments which work in both, but check carefully.

4. **Multi-window editor key bindings** — when running TNI ASM in an emulator, the key bindings assume the original Pentagon keyboard layout. You may need to configure your emulator to map keys correctly.

5. **File encoding for Cyrillic** — TNI ASM source with Cyrillic comments uses a specific Russian encoding (typically CP866 or the Pentagon variant). Modern text editors may mangle this when you open the source on a PC.

6. **TR-DOS-specific directives** — TNI ASM has TR-DOS-aware directives (`SAVE_TRD`, etc.) that no cross-assembler supports. Replace with `INCBIN` of pre-extracted TR-DOS data or write a small wrapper.

7. **The `0.54` version confusion** — multiple builds of "0.54" exist in different archives. Some have patches from other sceners. If a source fails to assemble with one TNI ASM version, try another.

---

## FAQ

**Q: Where can I download TNI ASM?**

A: The canonical archive is [trd.speccy.info](http://trd.speccy.info/); search for "TniAsm". The 0.54 version is typically what you want.

**Q: Should I learn TNI ASM if I am starting Spectrum development today?**

A: No. Use a modern cross-assembler like [SjASMPlus](sjasmplus.md) or [RASM](rasm.md). TNI ASM is only relevant for working with historical source archives.

**Q: Why was TNI ASM never as popular as ALASM?**

A: Several reasons: (1) ALASM was already dominant when TNI ASM appeared, and switching cost was high. (2) TNI ASM's first widely-adopted version (0.42) came out in 1999, just as the scene was contracting and developers were moving to PC tools. (3) STS debugger integration gave ALASM a unique advantage that TNI ASM could not match.

**Q: Does TNI ASM work on non-Russian Spectrum clones?**

A: It runs on any TR-DOS-equipped Spectrum clone or emulator. Western 48K/128K Spectrums do not have TR-DOS by default; you need to install a TR-DOS ROM or use an emulator with TR-DOS support.

**Q: Was TNI ASM ever ported to PC as a cross-assembler?**

A: No. Neo stopped development in the mid-2000s, and no one else took up the cross-platform port. The closest spiritual successor is SjASMPlus, which adopted many similar ideas.

**Q: Does TNI ASM support ZX Spectrum Next Z80N instructions?**

A: No. TNI ASM predates the ZX Spectrum Next by 20+ years.

---

## Cross-References

- [native_toolchain.md](native_toolchain.md) — survey of all native assemblers
- [alasm_sts.md](alasm_sts.md) — the dominant native Russian assembler
- [xas_assembler.md](xas_assembler.md) — TNI ASM's other Russian competitor
- [sjasmplus.md](sjasmplus.md) — the modern cross-assembler that inherited TNI ASM's design philosophy
- [rasm.md](rasm.md) — the modern fast cross-assembler
- [pasmo.md](pasmo.md) — the simpler modern alternative
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of cross-assemblers

---

## References

- Neo (Russian demoscene developer) — TNI ASM original author
- TNI ASM downloads — [trd.speccy.info](http://trd.speccy.info/) (search for "TniAsm")
- Russian Spectrum scene archives — [zx-art.ru](http://zx-art.ru/), [speccy.info](http://speccy.info/)
- Russian demoscene party archives — CC, diHALT, CAFe, FUNtop historical releases
- SKR (Spectrum Klan Rostov) — Neo's demoscene group
