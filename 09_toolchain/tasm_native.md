[← Home](../README.md) · [Toolchain](README.md)

# TASM (Native Spectrum Version) — Early-Era Tape-Loaded Assembler

The native **TASM** (sometimes called **TASMFORTH** or simply "Turbo Assembler" in 1980s UK magazines, though unrelated to Borland's later x86 product of the same name) was a simple Z80 assembler that ran on the ZX Spectrum itself, distributed on cassette tape in the 1983-1985 period. It was one of several early native assemblers (alongside HiSoft DEVPAK, Zeus, and a wave of magazine type-in tools) competing for the early hobbyist market before commercial studios standardized on DevPac or Zeus.

> [!WARNING]
> **Three different products share the "TASM" name** and are routinely confused in modern retro-computing discussions:
>
> 1. **Native Spectrum TASM** — this article. A tape-era Z80 assembler that runs on the Spectrum (1983-1985)
> 2. **Telemark / Squakvalley TASM** — Thomas Anderson's MS-DOS table-driven cross-assembler (1990-2003). See [tasm_cross.md](tasm_cross.md)
> 3. **Borland Turbo Assembler** — Borland's x86 assembler for DOS (1989-2007). Unrelated to either of the above
>
> When reading 1980s magazine listings or modern forum posts, use the surrounding context (Spectrum vs DOS vs x86) to disambiguate.

> [!NOTE]
> This article covers TASM as a **historical reference**. Primary documentation is scarce. None of the major commercial Spectrum studios used TASM as their primary assembler — they standardized on Zeus, DEVPAK, or in-house tools. TASM is mostly relevant today for understanding the early Spectrum tool landscape before DEVPAK and Zeus became standard.

---

## What TASM Was

The native Spectrum TASM was a single-load assembler that occupied a region of RAM (typically the upper portion, above BASIC's workspace) and let the user type Z80 assembly source using a basic full-screen editor. After assembling, the resulting machine code was placed in a separate region of RAM, ready to be tested, saved to tape, or merged with a loader program.

### Key Features (Relative to 1983 Alternatives)

- **Full-screen editor** — a step up from Sinclair BASIC's line editor
- **Label support** — symbolic labels for branch targets (no more hand-calculating offsets)
- **Two-pass assembly** — forward references resolved
- **Documented Z80 instruction set** — no support for undocumented opcodes
- **Tape save/load** — source could be saved as a headerless data block to tape
- **`#NN` hex literals** — Sinclair BASIC style, familiar to Spectrum users

### What TASM Lacked

- **No macros** — repetitive code had to be typed by hand or generated with `READ`/`DATA` tricks
- **No conditional assembly** — no `IF`/`ELSE`/`ENDIF`
- **No structured include files** — single-source only
- **No built-in monitor/debugger** — pair with a separate tool (like MONS) for debugging
- **No disk support** — tape only (TR-DOS interfaces existed but TASM predates widespread TR-DOS adoption)

---

## Quick Start (Historical Reconstruction)

The following is a reconstruction of the typical TASM workflow, based on magazine reviews of the period. Exact commands and keystrokes varied between versions and are not documented in any single authoritative source.

```z80
        ORG  30000

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

The user typed this source in TASM's editor, pressed a key to assemble, and (if no errors) called the resulting code from BASIC with `RANDOMIZE USR 30000`. See [spectrum_basic_mcode.md](spectrum_basic_mcode.md) for the BASIC-side calling convention.

---

## Historical Context and the 1983-1985 Assembler Boom

The native Spectrum TASM appeared during a brief but intense period (1983-1985) that can be called the **Spectrum assembler boom**. After the Spectrum's 1982 launch with no assembler in ROM, the market responded rapidly:

- **1982-1983**: Hobbyists hand-assembled from BASIC (see [spectrum_basic_mcode.md](spectrum_basic_mcode.md)). Magazine type-in listings were the main path to learning machine code.
- **1983**: **Zeus Assembler** by Simon Brattel and Neil Mottershead launched at £12.95, establishing the high end. See [zeus_assembler.md](zeus_assembler.md).
- **1983-1984**: **HiSoft DEVPAK** (GENS/MONS) launched, establishing the workhorse standard for UK commercial studios. See [devpac_gens_mons.md](devpac_gens_mons.md).
- **1983-1985**: A wave of cheaper, simpler alternatives appeared — **TASM**, **AVA**, **AVRA** (see [avras.md](avras.md)), **Laser Genius** (see [laser_genius.md](laser_genius.md)), and various magazine type-in assemblers.
- **1985-1986**: DEVPAK and Zeus consolidated the market. The simpler alternatives either disappeared or were absorbed into the demoscene's informal toolkit.

### Where TASM Fit

TASM targeted the **budget end** of the assembler market — typically priced around £5-10, about half the cost of Zeus or DevPac. It appealed to:

- **Hobbyists on a budget** who could not justify £15-20 for Zeus or DevPac
- **Beginners** who wanted a simpler tool with fewer features to learn
- **Educational users** — schools and computing clubs that needed an assembler without commercial features

The trade-off was feature set. TASM's lack of macros and conditional assembly made it unsuitable for the large-scale projects (full games, professional demos) that DevPac and Zeus users were building. By 1986, TASM had largely disappeared from the commercial market.

### Pricing and Distribution

Specific pricing for TASM varies between sources. Tape-based assemblers in 1984 typically retailed for £4.99-£9.99 in the UK. TASM was at the lower end of this range. Distribution was through:

- Mail order from small software houses
- Computing magazine cover disks (rebranded or licensed versions)
- Type-in listings in magazines like *Your Sinclair*, *CRASH*, and *Sinclair User*

Because TASM lacked the institutional backing of HiSoft or Crystal Computing (Zeus), its distribution was less reliable. Many users encountered TASM through informal swapping rather than retail purchase.

---

## Source Language

TASM used standard 1980s Z80 notation with Sinclair-style hex literals. The directives were close to HiSoft GENS but with some simplifications.

### Number Formats

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `#` | `#FE`, `#4000` | **Sinclair style** — preferred |
| Hex with `H` suffix | `0FEh` | Also accepted |
| Character | `'A'` | ASCII value |

TASM did not accept `$NN` (Zilog style) or `0xNN` (C style). It was a Spectrum-native tool and used Spectrum conventions.

### Operators

Basic arithmetic only: `+`, `-`, `*`, `/`. No bitwise operators, no comparison operators. Complex expressions had to be pre-computed.

### Directives

| Directive | Use |
|---|---|
| `ORG address` | Set assembly address |
| `DEFB b1, b2, ...` | Define bytes (also: `DB`) |
| `DEFW w1, w2, ...` | Define words (also: `DW`) |
| `DEFS count` | Define storage (also: `DS`) |
| `DEFM "text"` | Define message bytes |
| `EQU` or `=` | Define a constant |
| `END [label]` | End of source (optional entry point) |

Note the absence of `INCLUDE`, `IF`, `MACRO`, or any conditional/repeat directives — all confirmed limitations consistent with TASM's positioning as a simple budget tool.

### Labels

Labels are alphanumeric identifiers starting with a letter, followed by a colon (`:`):

```z80
START:  LD HL, MESSAGE
        ...
MESSAGE:
        DEFB "Hello", 0
```

Local labels (with `.` prefix or other scoping) are not supported. All labels are global within the source file.

---

## Comparison with Contemporaries

| Feature | TASM (native) | [Zeus](zeus_assembler.md) | [DevPac GENS](devpac_gens_mons.md) | [AVA](avras.md) |
|---|---|---|---|---|
| Year launched | 1983-1984 | 1983 | 1983-1984 | 1984 |
| Price range | £5-£10 | £12.95 | £15-£25 | £3-£5 |
| Full-screen editor | ✅ | ✅ | ✅ (from v3) | ⚠️ (line-based) |
| Macros | ❌ | ✅ | ✅ | ❌ |
| Conditional assembly | ❌ | ✅ | ✅ | ❌ |
| Built-in monitor | ❌ | ✅ | ✅ (separate MONS) | ❌ |
| Tape save/load | ✅ | ✅ | ✅ | ✅ |
| Disk (TR-DOS) | ❌ | ⚠️ (later) | ✅ | ❌ |
| Documented Z80 only | ✅ | ⚠️ | ⚠️ (later added undoc) | ✅ |

The comparison shows TASM positioned between the bare-bones magazine type-in assemblers and the professional Zeus/DevPac offerings. It was capable enough for small projects but quickly outgrown.

---

## When to Encounter TASM Today

### 1. Historical Source Archives

If you are studying a 1983-1985 hobbyist Spectrum program with assembly source attached, there is a small chance it was written in TASM. The giveaway is the directive set: `DEFB`/`DEFW`/`DEFM` and `EQU` with no macro usage and no `IF`/`ENDIF`. However, this same directive set was used by GENS and several other assemblers, so you cannot conclusively identify TASM from source alone — you need the assembler's identity in any accompanying documentation.

### 2. Magazine Reviews and Advertisements

Reviews and advertisements in *Your Sinclair*, *CRASH*, and *Sinclair User* from 1983-1985 contain references to TASM and similar budget assemblers. These are the primary historical sources for the tool.

### 3. Emulator Bundles

Some retro-computing archives and emulator bundles include TASM as part of a "period software" collection. Running TASM in [ZX Spin](zx_spin.md), [Fuse](../11_emulation/), or [ZEsarUX](../11_emulation/) requires a snapshot or tape image of the assembler.

### Modern Alternatives

For new Spectrum development, **do not use TASM**. Use:

- **[SjASMPlus](sjasmplus.md)** — the modern de facto standard
- **[Pasmo](pasmo.md)** — minimalist alternative with similar scope but more features
- **[Zeus 4](zeus_assembler.md)** — modern revival of the canonical native tool

---

## Common Pitfalls (For Modern Users)

1. **Confusion with other TASM tools** — see the warning at the top of this article. The native Spectrum TASM is **not** the MS-DOS cross-assembler (see [tasm_cross.md](tasm_cross.md)) and **not** Borland's x86 tool.

2. **Limited feature set** — coming from a modern cross-assembler, TASM's lack of macros, conditional assembly, and include files is a significant limitation.

3. **Single-source projects only** — multi-file projects require manual concatenation.

4. **No debugger** — pair with a separate monitor like STS or MONS for debugging.

5. **Tape-only distribution** — finding a working TASM image today requires searching retro-computing archives. There is no canonical website.

6. **Limited documentation** — unlike Zeus and DevPac, TASM did not have a comprehensive printed manual. Users learned from magazine tutorials and word-of-mouth.

---

## FAQ

**Q: I have a TASM source file from the 1980s. Can I assemble it with a modern cross-assembler?**

A: Usually yes. The directive set (`ORG`, `DEFB`, `DEFW`, `EQU`, `END`) is compatible with [Pasmo](pasmo.md), [SjASMPlus](sjasmplus.md), and most modern Z80 cross-assemblers with minor adjustments. Hex literals (`#NN`) work directly. The lack of macros means there is nothing exotic to port.

**Q: Was TASM related to Borland Turbo Assembler?**

A: No. Borland's TASM is an x86 tool from a different company. The name collision is coincidental and confusing.

**Q: Why was TASM not more successful?**

A: Combination of factors: limited features compared to Zeus/DevPac, lack of institutional backing for distribution and support, and the rapid consolidation of the market around 1985-1986 as commercial studios standardized on DevPac.

**Q: Did any commercial Spectrum games use TASM?**

A: Not that has been documented. Commercial studios used Zeus, DevPac, or in-house tools. TASM was a hobbyist tool.

**Q: Where can I download TASM?**

A: There is no canonical download site. Search retro-computing archives like World of Spectrum (now offline, but mirrored) for snapshot or tape images. Search specifically for "TASM Spectrum assembler" to disambiguate from the MS-DOS and Borland tools.

---

## Cross-References

- [tasm_cross.md](tasm_cross.md) — the unrelated MS-DOS TASM (Telemark Assembler)
- [native_toolchain.md](native_toolchain.md) — survey of all native Spectrum assemblers
- [zeus_assembler.md](zeus_assembler.md) — the high-end contemporary
- [devpac_gens_mons.md](devpac_gens_mons.md) — the workhorse contemporary
- [avras.md](avras.md) — AVA/AVRA, similar minor tape-era assemblers
- [laser_genius.md](laser_genius.md) — another minor contemporary
- [spectrum_basic_mcode.md](spectrum_basic_mcode.md) — what TASM replaced for hobbyists
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — modern alternatives

---

## References

- *[Your Sinclair](https://archive.org/details/yoursinclair-magazine)*, *CRASH*, *Sinclair User* — magazine reviews and advertisements from 1983-1985
- [World of Spectrum](https://worldofspectrum.org/) software archive (mirrored) — TASM tape images and documentation
- Discussions on retro-computing forums ([World of Spectrum](https://worldofspectrum.org/) forums, retro-martyrship mailing lists) clarifying the multiple "TASM" tools
- Comparison with contemporaries based on the documented feature sets of Zeus, DevPac, and magazine type-in assemblers of the period
