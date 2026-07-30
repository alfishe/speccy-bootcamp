[← Home](../README.md) · [Toolchain](README.md)

# PikAsm — Soviet-Era Specialist Assembler for the VAST Toolchain

**PikAsm** (also written **PikASM** or **PIK Assembler**) is a Russian-developed native Z80 assembler associated with the **VAST** toolchain — a professional Soviet-era software development environment used in commercial clone game productions in the late 1980s and early 1990s. PikAsm was narrower in distribution than [ALASM](alasm_sts.md) or [XAS](xas_assembler.md), with a reputation for clean macro handling, and was used internally by several studios producing games for the Russian clone market.

> [!WARNING]
> Primary documentation for PikAsm is extremely scarce. The tool was used internally at studios and was not widely distributed through the public demoscene channels that documented ALASM and XAS. The details in this article are reconstructed from brief mentions in Russian-scene archives and recollections from developers of the period. Some specifics — exact author, version dates, feature set details — may be incomplete or approximate.

> [!NOTE]
> PikAsm is **not** the same as **PikFub** (a Russian floppy utility), **Piksi** (a Russian disk tool), or any other Russian-scene tool starting with "Pik". The name appears to be derived from a personal name or abbreviation, not an acronym.

---

## What PikAsm Was

PikAsm was a native Z80 assembler that ran on ZX Spectrum clones (Pentagon, Scorpion, and similar) under TR-DOS. It was part of the broader **VAST toolchain** — a professional development environment used at studios producing commercial software for the Russian-speaking Spectrum clone market in the late 1980s through mid-1990s.

### The VAST Toolchain

VAST was a vertically-integrated development environment that combined:

- **PikAsm** — the assembler
- A text editor (PikAsm's built-in editor)
- A debugger / monitor
- Asset conversion utilities (graphics, music)
- Build orchestration tools

This integration was unusual for the Russian scene, where most developers assembled their own toolchain from individual tools (ALASM + STS + a music editor + an art tool). VAST studios used the whole package as a unit, which gave them tighter workflow integration but made it harder to share tooling with the broader community.

### Key Features

PikAsm's reported feature set included:

- **Clean macro handling** — the tool's most praised feature
- **Two-pass assembly** with forward references
- **TR-DOS native** — disk-based source and output
- **Documented Z80 instruction set** (status of undocumented opcodes unclear)
- **Multi-file projects** via the VAST orchestration layer
- **Sinclair-style hex** (`#NN`)

### What Distinguished PikAsm

Compared to ALASM and XAS:

- **Cleaner macro syntax** — based on developer testimonials
- **Tighter tool integration** — via the VAST environment
- **Narrower distribution** — used by professional studios, not the demoscene
- **Fewer known bugs** — likely because the user base was smaller and the tool was tested in production workflows

---

## Quick Start (Historical Reconstruction)

The exact PikAsm workflow is not documented in any single authoritative source. The following is a reconstruction based on the typical Russian-scene native assembler workflow:

```basic
LOAD *"m";1;"pikasm"
```

Then within PikAsm:

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

PikAsm would assemble to a specified address, with the macro preprocessor running first to expand any macros, then the main two-pass assembler producing machine code.

---

## Historical Context

PikAsm and the VAST toolchain belong to the **commercial Soviet-era software industry** that produced games and applications for the Russian clone market. This industry was distinct from the later Russian demoscene in several ways:

- **Time period**: commercial studios operated from the late 1980s through the mid-1990s, peaking around 1992-1994. The demoscene flourished later, roughly 1995-2005.
- **Distribution**: commercial studios sold software on tape and disk through retail channels. Demoscene productions were freely distributed at parties and via BBSes.
- **Toolchain**: commercial studios often used proprietary or semi-proprietary tools (like VAST). Demoscene coders used publicly-distributed tools (ALASM, XAS).
- **Authorship**: commercial software was typically credited to a studio (e.g., **Step Creative Group**, **Sinclair Labs**, **Nemo**). Demoscene works were credited to individual handles and crews.

### Studios That Used VAST

Several Russian studios are reported to have used VAST internally, including studios that produced ported and original games for the clone market. Specific titles produced with VAST are hard to identify because Soviet and Russian commercial software of this period rarely credited the toolchain in the published work.

### Why PikAsm Did Not Spread

Despite its technical merits, PikAsm never gained the wider adoption of ALASM or XAS. Reasons:

1. **Proprietary distribution** — VAST was a studio tool, not a public release
2. **Late documentation** — by the time the demoscene started documenting tools, VAST had been superseded
3. **Hardware requirements** — VAST assumed specific studio setups, including large RAM and disk configurations
4. **Scene shift to cross-development** — by the late 1990s, Russian developers were increasingly using PC-based cross-assemblers, making native tools like PikAsm obsolete

---

## Source Language

PikAsm's source language is largely undocumented. Based on the conventions of the era and the tool's positioning alongside ALASM/XAS, it likely supported:

### Number Formats (Reconstructed)

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `#` | `#FE`, `#4000` | **Sinclair style** — likely preferred |
| Hex with `H` suffix | `0FEh` | Also accepted |
| Character | `'A'` | ASCII value |

### Directives (Reconstructed)

A typical Russian-scene directive set, likely close to ALASM:

| Directive | Use |
|---|---|
| `ORG address` | Set assembly address |
| `DEFB` / `DB` | Define bytes |
| `DEFW` / `DW` | Define words |
| `DEFS` / `DS` | Define storage |
| `EQU` / `=` | Define a constant |
| `INCLUDE "file"` | Include source file |
| `INCBIN "file"` | Include binary file |
| `IF` / `ELSE` / `ENDIF` | Conditional assembly |
| `MACRO` / `ENDM` | Define a macro |
| `END [label]` | End of source |

### Macros — The Praised Feature

Multiple Russian-scene developers, when asked about PikAsm in retrospectives, highlighted its macro handling as cleaner than ALASM's or XAS's. The exact syntax is not preserved in any known archive, but it was reported to be more readable and less error-prone than the alternatives.

Without source samples, it is not possible to give a definitive macro example. See [xas_assembler.md](xas_assembler.md) and [alasm_sts.md](alasm_sts.md) for the macro syntax of comparable contemporary tools.

---

## Comparison with Contemporaries

| Feature | PikAsm | [ALASM](alasm_sts.md) | [XAS](xas_assembler.md) | [ZXASM](zxasm_native.md) |
|---|---|---|---|---|
| Time period | Late 1980s - mid 1990s | 1992-2005 | 1993-2000s | 1994-2000s |
| Distribution | Internal (studio use) | Public (scene) | Public (scene) | Public (scene) |
| Toolchain integration | Part of VAST | Standalone + STS | Standalone | Standalone + STS |
| Macro syntax | Reported clean | Standard | Elaborate 3-layer | Standard |
| Multi-file projects | Via VAST orchestration | Via INCLUDE | Via INCLUDE | Via INCLUDE |
| Public documentation | Extremely sparse | Extensive | Moderate | Sparse |

### Why PikAsm Mattered

Despite its narrow distribution, PikAsm is historically important because it documents the **professional software production industry** that existed in the Soviet Union and post-Soviet Russia in the late 1980s and early 1990s. This industry has been less documented than the demoscene that followed it, in part because commercial studios of the period were less inclined to publish their tools and methods.

PikAsm is a reminder that the Russian Spectrum scene had **two parallel toolchain cultures**:

1. **Studio toolchains** (VAST, in-house tools at Step, Nemo, etc.) — vertically integrated, proprietary, used for commercial production
2. **Public toolchains** (ALASM, XAS, ZXASM, STS) — distributed through demoscene channels, used by hobbyists and indie developers

The studio toolchains died with the commercial industry in the mid-1990s. The public toolchains lived on through the demoscene into the 2000s.

---

## When to Encounter PikAsm Today

### 1. Reverse-Engineering Soviet-Era Commercial Games

If you are reverse-engineering or studying commercial Soviet-era Spectrum games (especially those from studios like Step Creative Group), the original source may have been written in PikAsm. However, the published binaries do not typically identify the assembler used. You would only know from internal documentation or developer interviews.

### 2. Historical Research

Researchers studying the Soviet/Russian commercial software industry may encounter PikAsm in interviews with veteran developers from studios of that period. Russian-language retro-computing forums (zx-pk.ru) occasionally have threads where former studio developers discuss their tools.

### 3. TR-DOS Disk Archives

Some TR-DOS disk archives include PikAsm alongside other Russian-scene development tools. Finding a working PikAsm image today requires searching these archives — the tool is rarer than ALASM or XAS.

### Modern Alternatives

For new development, **do not use PikAsm**. Use [SjASMPlus](sjasmplus.md), [Pasmo](pasmo.md), or any other modern cross-assembler.

---

## Common Pitfalls

1. **Extremely sparse documentation** — PikAsm is one of the most poorly documented tools in the Russian Spectrum scene. Most information comes from second-hand recollections.

2. **Confusion with other "Pik" tools** — several unrelated Russian-scene utilities start with "Pik". Confirm you are looking at PikAsm the VAST toolchain assembler.

3. **No known public binary** — unlike ALASM and XAS, PikAsm binaries are not widely distributed. Finding one requires deep searching of Russian TR-DOS archives.

4. **Historical reconstruction required** — the tool's exact feature set, syntax, and version history are not preserved in any single canonical source.

5. **Studio-specific extensions** — different studios may have customized VAST/PikAsm for their own needs. There may not have been a single "canonical" PikAsm.

---

## FAQ

**Q: Where can I download PikAsm?**

A: There is no canonical download. Search Russian retro-computing archives (zx-pk.ru, TR-DOS software collections) for VAST or PikAsm. Be prepared for a long search — the tool is much rarer than ALASM or XAS.

**Q: Was PikAsm used in any well-known games?**

A: Specific titles are not widely documented. Soviet/Russian commercial software of the late 1980s and early 1990s rarely credited its toolchain.

**Q: Can I assemble PikAsm source with a modern cross-assembler?**

A: Probably yes, assuming the directive set is close to the reconstructed table above. The lack of macros in modern source means there is nothing exotic to port.

**Q: Is PikAsm related to ALASM?**

A: No direct relationship. They are distinct tools with different authors and different distribution models. They target the same hardware and roughly the same time period.

**Q: Why is PikAsm so poorly documented?**

A: Because it was a studio tool used in commercial production, not a public release. Documentation was internal to the studios that used it.

---

## Cross-References

- [native_toolchain.md](native_toolchain.md) — survey of all native Spectrum assemblers
- [alasm_sts.md](alasm_sts.md) — the dominant public Russian-scene assembler
- [xas_assembler.md](xas_assembler.md) — the Russian macro specialist
- [zxasm_native.md](zxasm_native.md) — another Russian native assembler with STS integration
- [tniasm.md](tniasm.md) — another Russian native assembler
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — modern alternatives

---

## References

- Russian Spectrum scene archives — zx-pk.ru forum and TR-DOS software collections
- Developer interviews and retrospectives on Soviet-era studios (Step Creative Group, Nemo, etc.)
- Comparisons with contemporaries based on the documented feature sets of ALASM and XAS
- Caveat: most information about PikAsm is second-hand, reconstructed from recollections rather than primary documentation
