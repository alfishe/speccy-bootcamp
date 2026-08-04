[← Home](../README.md) · [Toolchain](README.md)

# SARCASM — A Rare Cross-Assembler for ZX Spectrum

**SARCASM** is a relatively obscure Z80 cross-assembler that appears in some retro-computing software catalogs and download archives but has limited public documentation. The name suggests an acronym (possibly **S**imple **A**nd **R**eliable **C**ross **AS**e**M**bler or similar), but the original meaning is not preserved in any known source.

SARCASM sits in the long tail of Z80 cross-assemblers that were developed in the late 1990s and early 2000s to fill niches not served by the dominant tools ([Pasmo](pasmo.md), [z88dk z80asm](z88dk_z80asm.md), [SjASMPlus](sjasmplus.md)). It is most commonly encountered as a downloadable binary or source archive on retro-computing mirror sites, often without comprehensive documentation.

> [!WARNING]
> Primary documentation for SARCASM is extremely sparse. The tool does not appear to have a canonical home page, manual, or active maintainer in 2025. The details in this article are reconstructed from archive file listings, README fragments, and comparisons with contemporary cross-assemblers.

> [!NOTE]
> This article exists primarily to acknowledge SARCASM as a known data point in the cross-assembler landscape. For practical work, prefer [SjASMPlus](sjasmplus.md) or [Pasmo](pasmo.md), which have comprehensive documentation and active communities.

---

## Quick Start (Based on Archive Reconstruction)

SARCASM is typically distributed as source code or a Linux binary. To build from source:

```bash
tar xzf sarcasm.tar.gz
cd sarcasm
make
sudo make install
```

A typical usage:

```bash
sarcasm hello.asm -o hello.bin
```

The exact CLI flags vary by version. Check `sarcasm --help` (if the version you have supports it) for the specific options.

---

## History and Context

The history of SARCASM is not well documented. Based on archive metadata and code style, SARCASM appears to be a personal project from the late 1990s or early 2000s — the same period that produced [Pasmo](pasmo.md) (2001), [z88dk z80asm](z88dk_z80asm.md) (late 1990s), and the early versions of SjASMPlus (2004). Many Z80 cross-assemblers from this period were one-developer projects motivated by:

- Frustration with [TASM](tasm_cross.md)'s MS-DOS-only limitation
- Desire for a simpler alternative to z88dk's multi-tool pipeline
- Specific feature needs (e.g., direct `.tap` output) not met by mainstream tools
- Educational exercises in compiler/assembler construction

SARCASM was likely one of these personal projects. Without comprehensive documentation, it is hard to know its distinguishing features or intended niche. The fact that it appears in retro-computing archives but did not gain a significant user base suggests it was either:

- A niche tool with specific use cases that did not appeal broadly
- A personal project that the developer did not actively promote
- A victim of timing (released alongside more polished alternatives like Pasmo)

### Why SARCASM Did Not Spread

The cross-assembler market of the late 1990s and early 2000s consolidated quickly around a few tools:

- **[Pasmo](pasmo.md)** for minimalist cross-platform work
- **[z88dk z80asm](z88dk_z80asm.md)** for z88dk-integrated projects
- **[SjASMPlus](sjasmplus.md)** (from 2004) for the most features
- **[vasm](vasm.md)** (from 2002) for multi-CPU coverage

SARCASM competed in this space but did not differentiate sufficiently to attract users away from these alternatives.

---

## Reconstructed Feature Set

Based on the typical feature set of late-1990s/early-2000s Z80 cross-assemblers and brief archive README fragments:

### Number Formats (Likely)

| Format | Example | Notes |
|---|---|---|
| Decimal | `42`, `255` | Default base |
| Hex with `0x` | `0xFE` | C syntax (likely) |
| Hex with `$` | `$FE` | Zilog syntax (likely) |
| Hex with `H` suffix | `0FEh` | Possible |
| Character | `'A'` | ASCII value |

### Directives (Likely)

| Directive | Use |
|---|---|
| `ORG address` / `.org` | Set assembly address |
| `DB` / `.db` / `DEFB` | Define bytes |
| `DW` / `.dw` / `DEFW` | Define words |
| `DS` / `.ds` / `DEFS` | Define storage |
| `EQU` / `=` | Define a constant |
| `INCLUDE "file"` | Include source file |
| `INCBIN "file"` | Include binary file |
| `IF` / `ELSE` / `ENDIF` | Conditional assembly |
| `MACRO` / `ENDM` | Define a macro |
| `END` | End of source |

### Output Formats

SARCASM likely produces raw binary output (`.bin`) by default. Direct `.tap` or `.sna` output, if supported, is undocumented.

---

## Comparison with Contemporaries

| Feature | SARCASM | [Pasmo](pasmo.md) | [z88dk z80asm](z88dk_z80asm.md) | [SjASMPlus](sjasmplus.md) | [vasm](vasm.md) |
|---|---|---|---|---|---|
| Year (approx) | Late 1990s - early 2000s | 2001 | Late 1990s | 2004 | 2002 |
| Direct `.tap` output | Unknown | ✅ | ❌ (use appmake) | ✅ | ❌ |
| Direct `.sna` output | Unknown | ✅ | ❌ | ✅ | ❌ |
| Object files | Unknown | ❌ | ✅ | ❌ | ✅ |
| Multi-CPU | ❌ (Z80 only) | ❌ | ⚠️ (Z80 family) | ⚠️ (Z80N) | ✅ (many) |
| Documentation | Sparse | Comprehensive | Comprehensive | Comprehensive | Comprehensive |
| Active maintenance | ❌ | ✅ | ✅ | ✅ | ✅ |
| Community size | Minimal | Large | Large (via z88dk) | Large | Medium |

### Why SARCASM Is Largely Forgotten

The cross-assembler landscape rewards **active maintenance** and **community building**. Tools that stop receiving updates and do not build a user community tend to fade, regardless of their technical merits. SARCASM appears to fit this pattern — a one-developer project that did not transition to a community-maintained codebase.

---

## When to Encounter SARCASM Today

### 1. Retro-Computing Software Archives

You may find SARCASM on retro-computing download sites, often in a directory of "assorted Z80 assemblers" or "retro Spectrum tools". The archive is typically a tarball with source code and possibly a README.

### 2. Build Script References

Occasionally, you may find an old Spectrum project whose build script invokes `sarcasm` rather than a more common assembler. This is rare but possible for projects from the late 1990s or early 2000s.

### 3. Forum Discussions

SARCASM occasionally appears in forum threads comparing Z80 cross-assemblers, usually as a historical mention rather than an active recommendation.

### Modern Alternatives

For any new development, **do not use SARCASM**. Use:

- [[SjASMPlus]([sjasmplus](https://github.com/z00m128/sjasmplus).md)](https://github.com/z00m128/sjasmplus) — the modern de facto standard
- [[[Pasmo](https://www.naslag.info/pasmo/)](pasmo.md)](https://www.naslag.info/pasmo/) — minimalist alternative
- [[[z88dk](https://github.com/z88dk/z88dk) z80asm](z88dk_z80asm.md)](https://github.com/z88dk/z88dk) — for z88dk-integrated work

---

## Common Pitfalls

1. **Essentially no documentation** — SARCASM is one of the most poorly documented cross-assemblers. Be prepared for trial and error.

2. **No active maintenance** — bugs from years ago are unlikely to be fixed. The tool may not compile cleanly on modern systems without source patches.

3. **No community support** — finding help online is very difficult. There is no active forum, mailing list, or Discord server for SARCASM.

4. **Uncertain feature set** — without documentation, the exact syntax, directives, and output formats are uncertain.

5. **Easily confused with similar names** — "sarcasm" is a common English word, making web searches for the tool difficult. Use specific search terms like "sarcasm z80 assembler" or "sarcasm spectrum".

6. **Old build environment** — if building from source, expect C/C++ code that may not compile cleanly on modern compilers without warnings or errors.

---

## FAQ

**Q: Where can I download SARCASM?**

A: Search retro-computing download archives for "sarcasm z80" or "sarcasm spectrum". There is no canonical home page.

**Q: Is SARCASM worth using for new projects?**

A: No. Use [SjASMPlus](sjasmplus.md), [Pasmo](pasmo.md), or any other actively maintained cross-assembler.

**Q: What does SARCASM stand for?**

A: The acronym expansion is not documented. It may stand for "Simple And Reliable Cross Assembler" or similar, but this is speculative.

**Q: Is SARCASM still being developed?**

A: No sign of active development. The last updates to known archives appear to be from the early 2000s.

**Q: Did SARCASM support ZX Spectrum Next (Z80N)?**

A: Almost certainly not. The tool predates the Spectrum Next by over a decade.

---

## Cross-References

- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of all cross-assemblers
- [pasmo.md](pasmo.md) — the closest comparable minimalist tool
- [sjasmplus.md](sjasmplus.md) — the modern recommended alternative
- [z88dk_z80asm.md](z88dk_z80asm.md) — the z88dk-integrated alternative
- [vasm.md](vasm.md) — the multi-CPU alternative
- [zasm_kio.md](zasm_kio.md) — another niche modern cross-assembler

---

## References

- Retro-computing software download archives (file listings and README fragments)
- Historical comparison with Pasmo, [z88dk](https://github.com/z88dk/z88dk) z80asm, and SjASMPlus
- **Caveat**: This article is necessarily speculative due to the absence of comprehensive documentation. Specific feature claims should be verified against any SARCASM distribution you may find before relying on them.
