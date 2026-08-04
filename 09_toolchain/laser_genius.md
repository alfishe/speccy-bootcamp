[← Home](../README.md) · [Toolchain](README.md)

# Laser Genius — Cartridge-Based Assembler for the Interface 2

**Laser Genius** is a Z80 assembler/editor for the ZX Spectrum that shipped on a **ROM cartridge** for the Interface 2 ROM cartridge port. It was developed by **Nick Hampshire** and was one of the few commercial Spectrum development tools distributed in cartridge form rather than on cassette tape. The cartridge format gave Laser Genius an unusual advantage: **instant load**, compared to the several minutes required to load a tape-based assembler.

Laser Genius was positioned as a premium professional tool, used internally at studios that valued fast turnaround (particularly **Ocean Software**, which had a close relationship with the cartridge format) and licensed to a small number of partner studios. Its closed distribution model limited its broader influence on the Spectrum toolchain ecosystem.

> [!WARNING]
> Primary documentation for Laser Genius is scarce. The tool was used in a small number of studios and was not widely reviewed in the major Spectrum magazines. The details in this article are reconstructed from Interface 2 cartridge archives, brief mentions in Ocean-era developer interviews, and the tool's relationship with the Interface 2 hardware.

> [!NOTE]
> This article covers **Laser Genius** the Spectrum assembler. There is also a more famous **Laser Genius** brand of chess computer (Laser Chess / Laser Genius Chess) from the same era — completely unrelated.

---

## Quick Start (Historical Reconstruction)

To use Laser Genius, you needed:

1. A ZX Spectrum (48K or later — most Interface 2 owners had 48K or 128K machines)
2. An **Interface 2** cartridge peripheral
3. The **Laser Genius cartridge**

Plug the cartridge into the Interface 2 slot. The Spectrum's ROM detects the cartridge on reset and offers to boot from it. Within seconds, you are in the Laser Genius editor:

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

The exact editor commands are not preserved in modern archives. The workflow would have been similar to other 1984-era assemblers: full-screen editor, assembly with error messages, run the resulting code from BASIC with `RANDOMIZE USR`.

---

## The Interface 2 Cartridge Format

To understand Laser Genius's market position, you have to understand the **ZX Spectrum Interface 2**. Released by Sinclair Research in 1984, the Interface 2 was a peripheral that plugged into the Spectrum's edge connector and provided:

- A **ROM cartridge slot** — for instant-load software
- A **joystick port** (Sinclair's proprietary SJS standard, later supplemented by Kempston-compatible versions)
- An **RS-232 port** (rarely used)
- A **network interface** (rarely used)

The cartridge slot was the key feature. Cartridges contained a 16 KB ROM mapped into the Spectrum's memory space at boot time, allowing software to run instantly without tape loading. This was an enormous productivity advantage in 1984, when tape loading could take 5+ minutes for a large assembler.

### Limitations of the Cartridge Format

The Interface 2 was not a commercial success for Sinclair. Reasons:

1. **Cartridge cost** — ROM cartridges were significantly more expensive to manufacture than cassette tapes
2. **16 KB limit** — cartridges could hold at most 16 KB, limiting software complexity
3. **Closed ecosystem** — Sinclair controlled cartridge production, limiting third-party developers
4. **Tape was good enough for most users** — the 5-minute load time was tolerable for occasional use

Despite these limitations, the Interface 2 found a niche in **professional development environments** where the instant-load advantage justified the cost. Studios that bought Interface 2s for development also got a Laser Genius cartridge to use with them.

---

## Nick Hampshire and Laser Genius

**Nick Hampshire** was a British computer journalist and developer who wrote for several Spectrum-era publications, including *Sinclair User* and *Personal Computer World*. He developed Laser Genius as a commercial product in the early 1980s, leveraging his knowledge of professional development workflows.

Hampshire's design philosophy for Laser Genius appears to have been:

- **Cartridge-native** — exploit the instant-load advantage
- **Professional feature set** — macros, conditional assembly, multi-file support
- **Closed distribution** — sell direct to studios, not through retail

The result was a tool that was capable but narrowly distributed. Compared to Zeus and DevPac, which sold thousands of units through retail, Laser Genius sold perhaps a few dozen cartridges direct to studios.

### Laser Genius's Reported Feature Set

Reconstructed from brief mentions in contemporary sources:

- **Full-screen editor** — comparable to Zeus
- **Z80 instruction set** — documented instructions (status of undocumented opcodes unclear)
- **Label support** — symbolic labels
- **Macros** — present in some form (specifics not documented)
- **Conditional assembly** — present in some form
- **Output to RAM** — assembled code placed at `ORG` address, ready to call from BASIC
- **Cartridge-native** — instant boot, no tape

The exact directive set and macro syntax are not preserved in modern archives.

---

## Ocean Software and Laser Genius

**Ocean Software** was the most prominent UK studio associated with Laser Genius. Ocean's use of the tool grew out of two factors:

1. **Ocean's volume** — Ocean produced dozens of Spectrum games per year in the mid-1980s, requiring fast turnaround
2. **Ocean's hardware investments** — Ocean invested in Interface 2 cartridges for development, both for instant-loading assemblers and for prototyping cartridge-format games

Ocean used Laser Genius internally for some of its 1984-1987 Spectrum titles. The exact list of games produced with Laser Genius is not documented — Ocean did not publicly credit the tool. Other studios that reportedly used Laser Genius include:

- **Imagine Studios** (before its absorption into Ocean)
- A small number of UK studios that valued instant load

By the late 1980s, Ocean and other studios had moved to disk-based development (TR-DOS on +3, Opus Discovery on 48K) and cross-development on PC. Laser Genius became obsolete along with the Interface 2 itself.

---

## Comparison with Contemporaries

| Feature | Laser Genius | [Zeus](zeus_assembler.md) | [DevPac GENS](devpac_gens_mons.md) | [TASM native](tasm_native.md) |
|---|---|---|---|---|
| Year launched | ~1984 | 1983 | 1983-1984 | 1983-1984 |
| Distribution | Cartridge (Interface 2) | Tape | Tape | Tape |
| Load time | Seconds | 5+ minutes | 5+ minutes | 5+ minutes |
| Full-screen editor | ✅ | ✅ | ✅ | ✅ |
| Macros | ✅ (reported) | ✅ | ✅ | ❌ |
| Built-in monitor | ❌ | ✅ | ✅ (separate MONS) | ❌ |
| Public availability | Limited (studio tool) | Wide retail | Wide retail | Limited (mail order) |
| Documentation | Sparse | Comprehensive | Comprehensive | Sparse |

Laser Genius's distinguishing feature was the **cartridge format**, not its feature set. As an assembler, it was comparable to Zeus or DevPac, but its distribution model was unique.

---

## When to Encounter Laser Genius Today

### 1. Interface 2 Cartridge Archives

If you are studying Interface 2 cartridges, you may encounter a Laser Genius ROM dump. These are rarer than game cartridge dumps because Laser Genius was not widely distributed.

### 2. Ocean-Era Developer Interviews

Interviews with Ocean-era developers (1984-1987) occasionally mention Laser Genius. These interviews are the primary source of information about the tool's actual use.

### 3. Emulator Support

Modern Spectrum emulators support Interface 2 cartridges. To run a Laser Genius ROM dump:

- Use [Fuse](../11_emulation/), [ZEsarUX](../11_emulation/), or [ZX Spin](zx_spin.md)
- Configure the emulator to attach an Interface 2
- Load the Laser Genius ROM as a cartridge image
- Reset the Spectrum

The emulator will boot Laser Genius as if a real cartridge had been plugged in.

### Modern Alternatives

For new development, **do not use Laser Genius**. Use [SjASMPlus](sjasmplus.md), [Pasmo](pasmo.md), or any other modern cross-assembler.

---

## Common Pitfalls

1. **Confusion with Laser Chess / Laser Genius Chess** — the chess computer brand is unrelated.

2. **Cartridge required** — Laser Genius cannot be loaded from tape or disk. You need an Interface 2 (or emulator equivalent) and the cartridge ROM.

3. **16 KB limit** — the cartridge could only hold 16 KB. Some Laser Genius features may have been cut to fit. This is one reason the tool's feature set is hard to document precisely.

4. **Studio-specific customizations** — different studios may have had their own customized versions. There may not be a single canonical Laser Genius.

5. **Emulator configuration** — getting Laser Genius to run in an emulator requires correctly configuring the Interface 2 peripheral.

6. **No surviving source code** — the Laser Genius source is not in any known archive. The tool is only known from ROM dumps and second-hand accounts.

---

## FAQ

**Q: Where can I download Laser Genius?**

A: Search Interface 2 cartridge archives for a Laser Genius ROM dump. Retro-computing archives that focus on Spectrum cartridges are the best source.

**Q: Did Laser Genius support macros?**

A: Reportedly yes, but the exact macro syntax is not documented.

**Q: Why is Laser Genius so poorly documented?**

A: Combination of factors: closed distribution (studio tool, not retail), small user base, the 16 KB cartridge limit (likely cut documentation), and the rapid obsolescence of the Interface 2 format.

**Q: Did any commercial Spectrum games use Laser Genius?**

A: Some Ocean titles from 1984-1987 reportedly used it, but specific titles are not publicly credited.

**Q: Was Laser Genius better than Zeus?**

A: As an assembler, probably comparable. The cartridge format was the differentiator — instant load versus tape load. For studios with Interface 2 hardware, Laser Genius was a productivity advantage. For everyone else, Zeus was the better choice.

**Q: Is the Interface 2 worth collecting today?**

A: Only for completeness. The Interface 2 is rare and expensive. Emulator support is the practical alternative for running Laser Genius and other cartridge software.

---

## Cross-References

- [native_toolchain.md](native_toolchain.md) — survey of all native Spectrum assemblers
- [zeus_assembler.md](zeus_assembler.md) — the dominant contemporary
- [devpac_gens_mons.md](devpac_gens_mons.md) — the other dominant contemporary
- [tasm_native.md](tasm_native.md) — the budget contemporary
- [avras.md](avras.md) — other minor tape-era assemblers
- [zx_spin.md](zx_spin.md) — emulator with Interface 2 support
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — modern alternatives

---

## References

- Interface 2 cartridge archives — ROM dumps of Laser Genius
- *[Sinclair User](https://archive.org/details/sinclair-user-magazine)*, *CRASH* — occasional mentions of Laser Genius in Ocean-era developer interviews
- Nick Hampshire's writings in *Personal Computer World* and *[Sinclair User](https://archive.org/details/sinclair-user-magazine)*
- Comparisons with Zeus and DevPac based on their documented feature sets
- Caveat: most information about Laser Genius is second-hand, reconstructed from cartridge ROM dumps and brief mentions in magazine interviews
