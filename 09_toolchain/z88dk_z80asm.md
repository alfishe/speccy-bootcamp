[← Home](../README.md) · [Toolchain](README.md)

# z88dk z80asm — The Object-File Assembler

**z80asm** is the assembler component of [z88dk](z88dk.md), the Z80 C development kit. Unlike single-file assemblers such as [Pasmo](pasmo.md) or [SjASMPlus](sjasmplus.md), z80asm is an **object-file assembler**: it compiles each source file into a relocatable `.o` object file, the linker (`z80nm` or `zcc` invoking `z80link`) resolves cross-file references, and the final output is a complete executable. This makes z80asm the natural choice when working inside the z88dk toolchain — particularly for projects that mix C and assembly.

z80asm has been part of z88dk since the project's earliest days in the late 1990s, when it was written to support Geoffrey Brownell's Small-C-derived `sccz80` compiler. It has been actively maintained ever since, gaining modern features (structures, modules, multi-CPU support) while remaining backward-compatible with the assembly sources written 25 years ago.

> [!NOTE]
> This article is the **per-tool reference** for z80asm specifically. For the broader z88dk toolchain (C compilers, libraries, `zcc` front-end, `appmake`), see [z88dk.md](z88dk.md). For the cross-assembler landscape, see [cross_platform_toolchain.md](cross_platform_toolchain.md).

---

## Quick Start

Install z88dk (Debian/Ubuntu: build from source per the [z88dk build instructions](https://github.com/z88dk/z88dk); macOS: `brew install z88dk`).

Write `add.asm` — a tiny function that adds two 16-bit integers:

```z80
        SECTION code_user

        PUBLIC add16            ; export the symbol

        EXTERN __hs_banksel     ; (just an example extern reference)

; HL = HL + DE (trivially already the case; this is a placeholder)
add16:
        add   hl, de
        ret
```

Assemble to an object file:

```bash
z80asm add.asm
```

This produces `add.o`. To link multiple objects into a final binary, use `zcc`:

```bash
zcc +zx -lndos -create-app -omyprogram main.o add.o
```

Or invoke the linker directly via `z80nm` / `z80link` for low-level control.

---

## History and Design Philosophy

z80asm predates most modern cross-assemblers. Its design philosophy reflects the era of its origin (late 1990s) and the goal it was built for: serve as the **back-end of a C compiler** rather than as a hand-assembly tool.

### Why Object Files?

A C compiler emits many separate translation units, each compiled to an object file. The linker then resolves cross-file references (variables, function calls) and combines them into a single executable. For z80asm to work as a C back-end, it had to support:

- **Object files** that can be combined later
- **Symbol tables** distinguishing `PUBLIC` (exported) from `EXTERN` (imported) symbols
- **Sections** (code, data, BSS) that the linker places independently
- **Relocation information** so addresses can be patched after final placement

These features are unfamiliar to assembly programmers used to monolithic tools like Pasmo, but they are standard in systems programming (gcc, clang, MSVC all work this way).

### Version History

| Era | z88dk version | z80asm highlights |
|---|---|---|
| 1998–2000 | z88dk 1.x (initial) | First z80asm: object-file format, linkable with sccz80 |
| 2000–2010 | z88dk 1.8–1.9 | Bug fixes; new CPU targets added |
| 2010–2015 | z88dk 1.10–1.99 | `MODULE` / `ENDMOD` namespaces; improved macros |
| 2015–2020 | z88dk 2.0+ | Modern maintenance; structured types, multiple CPUs, Z180, Z80N support for Spectrum Next |
| 2020s | ongoing | Active development; synchronised with SDCC integration; new `--cpu` flags |

The z88dk project itself has a stable release series (`1.99` for years, then `2.0` in 2017, currently `2.2+` on the development branch). z80asm tracks z88dk releases.

### Maintained By

z80asm and z88dk as a whole are maintained by a small team of volunteers on GitHub. The main contributors over the past decade include Phillip Stevens, dom (Dominic Morris), arnoldemu, and Alvin Albrecht. The project is open source under the **BSD-3-Clause license**.

---

## Source Language

z80asm uses a syntax close to the original Zilog notation, with extensions for object-file concepts.

### Numbers

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `#` | `#FE`, `#4000` | Matches Sinclair BASIC convention |
| Hex with `$` | `$FE`, `$4000` | Zilog syntax |
| Hex with `0x` | `0xFE` | C syntax |
| Hex with `H` suffix | `0FEh`, `0FFh` | Must start with a digit |
| Binary with `B` suffix | `10101010b` | |
| Binary with `%` | `%10101010` | |
| Character | `'A'`, `"a"` | ASCII value |

### Operators

z80asm has a full C-like expression evaluator, including function calls at assembly time:

| Operator | Meaning |
|---|---|
| `+`, `-`, `*`, `/`, `%` | Arithmetic (including modulo) |
| `<<`, `>>` | Bitwise shifts |
| `&`, `\|`, `^`, `~` | Bitwise AND/OR/XOR/NOT |
| `&&`, `\|\|`, `!` | Logical AND/OR/NOT |
| `==`, `!=`, `<`, `>`, `<=`, `>=` | Comparison |
| `?:` | Conditional (ternary) |

### Built-in Functions

A non-exhaustive list of useful compile-time functions:

| Function | Returns |
|---|---|
| `HIGH x` | High byte of `x` |
| `LOW x` | Low byte of `x` |
| `defined(symbol)` | 1 if symbol exists, 0 otherwise |
| `strlen("text")` | String length |
| `ASCII('A')` | ASCII value of a character |
| `BANK(symbol)` | Memory bank containing the symbol (128K targets) |
| `ORG()` | Current assembly address |

### Module System

z80asm supports `MODULE` / `ENDMOD` blocks that namespace symbols. This is critical when assembling many files into one program — two files can both define a `setup` label without conflict:

```z80
        MODULE drivers_screen

        PUBLIC clear_screen
        EXTERN wait_vblank

clear_screen:
        call wait_vblank
        ; ... implementation
        ret

        ENDMODULE
```

From outside the module, refer to it as `drivers_screen.clear_screen`. Inside the module, just `clear_screen`.

### Sections

z80asm organizes code and data into named **sections** that the linker places independently. The standard section names used in z88dk's classic library:

| Section | Contents | Placed at |
|---|---|---|
| `code_crt0` | CRT0 startup code | Start of program (e.g., `#8000`) |
| `code_user` | User-defined code | After CRT0 |
| `code_compiler` | C compiler-emitted code | Mixed with `code_user` |
| `data_user` | Initialised data | After code |
| `bss_user` | Uninitialised data | At top of memory, before stack |
| `bss_fardata` | Banked (128K) uninitialised data |
| `rodata_user` | Read-only data (tables) |
| `smc_clib` | z88dk classic library |

You can define your own sections with `SECTION myname`. The linker controls where each section goes.

### Object File Directives

| Directive | Use |
|---|---|
| `PUBLIC name` | Export this symbol for use by other objects |
| `EXTERN name` | Import a symbol from another object |
| `GLOBAL name` | Equivalent to `PUBLIC` if defined, `EXTERN` if not (handy for header files) |
| `MODULE name` / `ENDMOD` | Open / close a namespaced module block |
| `SECTION name` | Switch to a new section |
| `INCLUDE "file.asm"` | Include a source file |
| `BINARY "file.bin"` | Include a binary file as bytes |
| `ORG addr` | Override the assembly address (rarely used — let the linker decide) |
| `ALIGN n` | Pad to a multiple of `n` |

### Data Definitions

| Directive | Use |
|---|---|
| `DEFB b1, b2, ...` | Define bytes (also: `DB`, `.byte`) |
| `DEFW w1, w2, ...` | Define words, little-endian (also: `DW`, `.word`) |
| `DEFL l1, l2, ...` | Define long (32-bit) |
| `DEFQ q1, q2, ...` | Define quad (64-bit) |
| `DEFS count [, fill]` | Define storage (skip `count` bytes) |
| `DEFM "text"` | Define message (bytes of the string, no terminator) |
| `DEFC name = expr` | Define a constant |
| `DEFGROUP` | Define an enum-like group of constants |

### Macros

z80asm supports parameterised macros with `MACRO` / `ENDM`:

```z80
MACRO MUL_HL_BY_8
        sla   l
        rl    h
        sla   l
        rl    h
        sla   l
        rl    h
ENDM

; Usage
        MUL_HL_BY_8
```

Macro parameters are accessed by name (declared in the macro header), not by position number. This is more readable than the `\1`/`\2` convention used by some assemblers.

### Conditional Assembly

```z80
IFNDEF __SPECTRUM__
        ERROR "This source requires a Spectrum target"
ENDIF

IFDEF DEBUG_BUILD
        ; include verbose logging
ENDIF

IF PLATFORM_VARIANT == 48
        INCLUDE "screen_48k.asm"
ELIF PLATFORM_VARIANT == 128
        INCLUDE "screen_128k.asm"
ELSE
        ERROR "Unknown platform variant"
ENDIF
```

---

## CPU Targets

z80asm supports multiple CPU variants in the Z80 family, selected by command-line flag:

| `--cpu=` | Description |
|---|---|
| `z80` (default) | Original Zilog Z80 |
| `z80_strict` | Original Z80, reject undocumented instructions |
| `z80n` | ZX Spectrum Next Z80N (adds `LDIX`, `LDIRX`, `LDWS`, `LDPX`, `LIRF`, `PIXELDOT`, `SWAPNIB`, `MIRROR`, `ADDHL`, `ADDDE`, `ADDBC`, `BSWAP`, `LDPIRX`, `NEXTREG` instructions) |
| `z180` | Hitachi HD64180 (Z80 successor with MMU, increased addressing) |
| `rabbit2000` | Rabbit Semiconductor Rabbit 2000 |
| `rabbit3000` | Rabbit 3000 |
| `rabbit4000` | Rabbit 4000 |
| `8080` | Intel 8080 (Z80's predecessor; some instructions unsupported) |
| `gbz80` | Game Boy LR35902 (Z80 variant; missing `EXX`, alternate registers; different `LD (HL)` semantics) |

For most ZX Spectrum work, `--cpu=z80` (default) is correct. For Spectrum Next development, use `--cpu=z80n`. z80asm's Z80N support is comparable to SjASMPlus's.

---

## Command-Line Reference

z80asm has many flags. The most common for hand use:

| Flag | Use |
|---|---|
| `input.asm` | Source file (may be repeated) |
| `-o output.o` | Output object file name |
| `-x output.lib` | Create a library archive from multiple objects |
| `-i input.lib` | Link against library |
| `-d` | Emit list file (`.lis`) showing assembled output |
| `-s` | Emit symbol file (`.sym`) |
| `-g` | Emit map file (`.map`) |
| `-b` | Create a binary directly (bypass linker — for single-file use) |
| `-r addr` | With `-b`, set the ORG address |
| `--cpu=NAME` | Select CPU (see above) |
| `--IXIY` | Swap IX and IY register names (for the long-known Zilog naming bug workaround) |
| `--opt SPEED` / `--opt SIZE` | Hint the assembler to optimize for speed or size |
| `--verbose` | Print extra information |
| `--help` | Print usage and exit |

When z80asm is invoked through `zcc` (the usual case), these flags are translated automatically from `zcc` flags.

### Typical Command Lines

```bash
# Assemble to object
z80asm add.asm

# Assemble to binary directly (no linker)
z80asm -b -r #8000 standalone.asm

# Assemble and emit list + symbol + map files
z80asm -d -s -g demo.asm

# Use Z80N instructions (ZX Spectrum Next)
z80asm --cpu=z80n demo_next.asm

# Create a library archive from three objects
z80asm -x mylib.lib file1.o file2.o file3.o
```

---

## Linker Integration

The linker for z88dk is `z80nm` (the name manager) plus the integrated link step inside `zcc`. The full linker features:

- **Section placement** — assigns each section a final address based on target configuration
- **Symbol resolution** — turns `PUBLIC`/`EXTERN` declarations into actual addresses
- **Relocation patching** — patches branch offsets, `JP`, `LD`, and similar instructions that referenced symbolic addresses
- **Library archive search** — when you `-l` a library, the linker only pulls in objects that satisfy an `EXTERN` (like gcc's link-time-only-pull-in)
- **Far/banked code** — for 128K targets, supports multiple code banks and trampoline-style cross-bank calls

A typical `zcc` invocation that hides all this:

```bash
zcc +zx -clib=new -create-app -otest main.c routines.asm
```

This compiles `main.c`, assembles `routines.asm`, links both against the newlib, and emits a final `.tap` file ready for an emulator.

### Object File Format

The z80asm object file (`.o`) is a binary format containing:

- A **magic header** identifying it as z80asm output
- The **module name** (defaults to source file name)
- The **section table** with sizes and offsets
- The **code/data bytes** for each section
- The **symbol table** (`PUBLIC` declarations with local addresses)
- The **external reference table** (where each `EXTERN` was used, so the linker can patch them)
- The **relocation table** (which bytes depend on the section's final address)

You can inspect an object file with `z80nm file.o`:

```bash
$ z80nm add.o
add.o:
  code_user:        3 bytes
  symbols:
    PUBLIC  add16 @ code_user+0
```

---

## When to Choose z80asm

### Strengths

- **First-class object files** — the only major Z80 assembler with full linker support
- **Module system** — namespacing prevents collisions across large projects
- **Multi-CPU support** — Z80, Z80N, Z180, Rabbit, Game Boy, 8080 from one tool
- **C integration** — designed to interoperate with sccz80 and SDCC
- **Active maintenance** — bugs fixed regularly; tracks Spectrum Next developments
- **Cross-references and map files** — useful for understanding large projects

### Weaknesses

- **More complex to learn** than Pasmo or SjASMPlus due to object-file concepts
- **Not as fast** as Pasmo for small single-file projects (overhead of object file I/O)
- **No direct `.tap` / `.sna` / `.tzx` output** from `z80asm` itself — use `zcc` / `appmake` for those
- **Output formats target z88dk's expectations** — using z80asm standalone for non-z88dk projects is awkward

### Comparison Matrix

| Feature | z80asm | [Pasmo](pasmo.md) | [SjASMPlus](sjasmplus.md) | [vasm](vasm.md) | [WLA-DX](wla_dx.md) |
|---|---|---|---|---|---|
| Object files | ✅ | ❌ | ❌ | ⚠️ | ✅ |
| Linker | ✅ | ❌ | ❌ | ✅ | ✅ |
| Modules (namespaces) | ✅ | ❌ | ⚠️ | ❌ | ⚠️ |
| Multi-CPU support | ✅ | ❌ | ❌ | ✅ | ✅ |
| ZX Spectrum Next (Z80N) | ✅ | ❌ | ✅ | ❌ | ❌ |
| Output `.tap` directly | ❌ (use `zcc`) | ✅ | ✅ | ❌ | ❌ |
| C compiler integration | ✅ (z88dk) | ❌ | ⚠️ | ⚠️ (vasm+vbcc) | ❌ |
| License | BSD-3 | Public domain | BSD-2 | MPL-2 | GPL |

### Decision Guide

Choose **z80asm** when:
- You are inside the z88dk toolchain (writing assembly that calls or is called by C)
- You want a modular project structure with multiple object files
- You want one assembler for Z80, Z80N, and Z180 across multiple target platforms

Choose **[Pasmo](pasmo.md)** when:
- You want a tiny, simple, single-file assembler
- You want direct `.tap` output without learning `zcc`

Choose **[SjASMPlus](sjasmplus.md)** when:
- You want ZX Spectrum-specific output (`.nex`, `.trd`, `SAVESNA`) directly from the assembler
- You want Lua scripting

---

## Integration Examples

### z80asm Called from C Code (Assembly Function)

```c
// add16.c — declare an external assembly function
#include <arch/zx.h>

extern int  add16(int a, int b) __z88dk_fastcall;  // a in HL, b on stack (popped into DE)

int main(void) {
    int sum = add16(100, 200);
    zx_printf("sum = %d\n", sum);
    return 0;
}
```

```z80
; add16.asm — the assembly implementation
        SECTION code_user

        PUBLIC add16

add16:
        pop   de              ; second argument
        add   hl, de          ; first argument was in HL (fastcall)
        ret
```

Compile and link:

```bash
zcc +zx -lndos -create-app -omyprog add16.c add16.asm
```

### Mixing z80asm and SjASMPlus Objects

z80asm produces z88dk-format object files which SjASMPlus cannot consume. However, you can:

1. Assemble the z80asm portion with `z80asm` into an object, link with `zcc` to a `.bin`
2. Assemble the SjASMPlus portion separately to a `.bin`
3. Manually `BINARY "sjasmplus_part.bin"` from inside a z80asm source that the linker then includes

This is awkward; the cleaner approach is to pick one assembler per project.

### z80asm and z88dk's Classic vs newlib

z88dk ships two libraries: **classic** (the original, broad target support) and **newlib** (modern, smaller, optimized). z80asm itself does not care which you use, but the section names and CRT0 expectations differ between the two libraries. Always check the target's CRT0 documentation when writing standalone assembly meant to be linked by either library.

---

## Common Pitfalls

1. **Forgetting `PUBLIC` / `EXTERN`** — unlike Pasmo, all symbols in z80asm are local to their object by default. You must explicitly mark symbols `PUBLIC` for them to be visible to other objects, and explicitly declare them `EXTERN` to use them.

2. **Mixing sections incorrectly** — putting initialised data in `bss_user` (the uninitialised section) wastes ROM space and can corrupt the heap. Use `data_user` for initialised data.

3. **Assuming z80asm is fast** — for very small sources, the overhead of object file I/O dominates. Pasmo will be faster for a 200-line source. z80asm shines on large multi-file projects.

4. **Trying to use z80asm standalone for `.tap`** — `z80asm` does not emit `.tap` directly. Use `zcc` or post-process with `appmake`.

5. **Assuming sccz80's calling convention** — sccz80 and SDCC have different ABIs (see [sdcc.md](sdcc.md) for SDCC's stack-based ABI). If you write assembly that's called by C, you must match the compiler's ABI. z88dk provides `__z88dk_fastcall`, `__z88dk_callee`, and similar qualifiers to control this.

6. **Z80N instructions on the wrong CPU target** — if you use `LDIX` or similar without `--cpu=z80n`, the assembler will reject them.

7. **Standalone binary without linker (`-b`)** — when you bypass the linker with `-b`, you lose section placement, library archive search, and symbol resolution across files. This is fine for a single source but you are essentially using z80asm as a less convenient Pasmo.

---

## FAQ

**Q: Is z80asm the same as the z88dk project?**

A: No. z80asm is **one component** of z88dk. z88dk also includes sccz80, the patched SDCC backend, the `zcc` front-end, classic and newlib libraries, `appmake` for output formats, and several other tools. See [z88dk.md](z88dk.md) for the whole picture.

**Q: Can I use z80asm without z88dk?**

A: Yes, but it is awkward. The `-b` flag bypasses the linker and produces a raw binary from a single source, similar to Pasmo. However, you lose most of the reason to use z80asm. For standalone assembly, [Pasmo](pasmo.md) or [SjASMPlus](sjasmplus.md) are better choices.

**Q: How does z80asm compare to GNU `as` (gas)?**

A: gas supports Z80 as of the 2.40 release (2023), but the syntax is AT&T-style (different from Zilog), and there is no library ecosystem. z80asm uses Zilog syntax and integrates with the z88dk library. For pure Spectrum development, use z80asm.

**Q: What's the difference between `SECTION` and `MODULE`?**

A: A **section** is about *placement* — telling the linker which memory region to put code/data into. A **module** is about *namespacing* — keeping symbol names local to a group of code. A single module can span multiple sections, and multiple modules can contribute to the same section.

**Q: Does z80asm support ZX Spectrum Next hardware registers?**

A: Yes. With `--cpu=z80n`, the `NEXTREG` instruction (write to a Next hardware register) is available. The register names themselves (e.g., `#56` for Layer 2 transparency color) must be looked up in the Spectrum Next documentation; z80asm just treats them as numbers.

**Q: Can I produce a `.nex` file from z80asm directly?**

A: No, but `zcc +zxnext -clib=new -mhz=28 -create-app` will produce one. The `-create-app` step invokes `appmake` under the hood, which knows the `.nex` format.

**Q: Does z80asm support macros that expand to multiple instructions?**

A: Yes. The `MACRO` / `ENDM` block can contain any number of instructions, including conditional assembly, so you can build fairly complex macros. For real metaprogramming (recursive macros, IRP), Lua scripting in [SjASMPlus](sjasmplus.md) is more powerful.

---

## Cross-References

- [z88dk.md](z88dk.md) — the parent toolchain (C compilers, libraries, `zcc` front-end)
- [sdcc.md](sdcc.md) — using SDCC with z80asm (via z88dk's `-compiler=sdcc`)
- [sjasmplus.md](sjasmplus.md) — the main alternative for pure assembly projects
- [pasmo.md](pasmo.md) — the simpler alternative for single-file projects
- [vasm.md](vasm.md) — portable macro assembler (pending)
- [wla_dx.md](wla_dx.md) — cross-platform macro assembler (pending)
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [native_toolchain.md](native_toolchain.md) — survey of native assemblers
- [vscode_integration.md](vscode_integration.md) — IDE setup (z80asm `.lis` files are supported)
- [debugging.md](debugging.md) — source-level debugging with z88dk-gdb

---

## References

- z88dk Project — [github.com/z88dk/z88dk](https://github.com/z88dk/z88dk)
- z88dk Wiki — [github.com/z88dk/z88dk/wiki](https://github.com/z88dk/z88dk/wiki)
- z80asm source — `src/z80asm/` in the z88dk repository
- z88dk Classic Library — `libsrc/_DEVELOPMENT/` in the z88dk repository
- Phillip Stevens (sprack) — long-time z88dk maintainer
- BSD-3-Clause license — see `LICENSE` in the z88dk repository
