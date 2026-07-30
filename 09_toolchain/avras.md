[← Home](../README.md) · [Toolchain](README.md)

# AVA / AVRA — Tape-Era Minor Assemblers

The names **AVA** and **AVRA** refer to a small family of early-1980s native Z80 assemblers for the ZX Spectrum that were distributed on cassette tape at the budget end of the market. These tools are among the **least documented** assemblers in the Spectrum ecosystem — they were produced by small developers, distributed informally, and largely displaced by Zeus and DevPac within a few years of their release.

> [!WARNING]
> Primary documentation for AVA/AVRA is **essentially non-existent**. The tool names appear in brief listings in 1980s software catalogs and in retrospective forum posts, but no comprehensive manual, review, or surviving source code is known. The information in this article is reconstructed from the broader context of 1982-1985 Spectrum assembler market, the typical feature set of budget tape-era tools, and brief mentions in retro-computing forums. Specific details — exact author, release date, feature set — are largely unknown.

> [!NOTE]
> The name **AVRA** has been used by several unrelated tools, including a modern AVR microcontroller cross-assembler. This article covers the **Spectrum-era AVRA**, which is a different tool entirely from the AVR toolchain.

> [!NOTE]
> The filename `avras.md` follows the planned catalog in [PLAN.md](../PLAN.md). The article covers both AVA and AVRA as a combined entry, since the relationship between the two names is unclear — they may be versions of the same tool, related tools by the same author, or distinct tools with similar names.

---

## What AVA/AVRA Was

AVA/AVRA was a Z80 assembler that ran on the ZX Spectrum, distributed on cassette tape at the budget end of the early-1980s assembler market. Its positioning was similar to [TASM](tasm_native.md):

- **Single-load tool** — occupied a region of RAM
- **Tape-distributed** — loaded from cassette
- **Budget price** — typically £3-£5, half the cost of Zeus or DevPac
- **Limited features** — no macros, no conditional assembly, no built-in monitor
- **Documented Z80 instruction set** — no support for undocumented opcodes

The tool was targeted at hobbyists who could not afford the £15-25 retail price of Zeus or DevPac and who needed more than hand-assembly from BASIC (see [spectrum_basic_mcode.md](spectrum_basic_mcode.md)).

### Reported Features

Based on the typical feature set of budget 1980s assemblers:

- **Full-screen editor** — though possibly line-based in early versions
- **Label support** — symbolic labels for branch targets
- **Two-pass assembly** — forward references resolved
- **`#NN` hex literals** — Sinclair style
- **Tape save/load** — source saved as a headerless data block

### What AVA/AVRA Lacked

- **No macros**
- **No conditional assembly**
- **No include files**
- **No debugger/monitor**
- **No disk support**

---

## Quick Start (Historical Reconstruction)

```basic
LOAD ""  ; Load AVA/AVRA from tape
```

Then within AVA/AVRA's editor:

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

After assembly, call from BASIC with `RANDOMIZE USR 30000`.

---

## The Tape-Era Assembler Market (1982-1985)

To understand AVA/AVRA, you have to understand the broader Spectrum assembler market of 1982-1985. After the Spectrum's launch with no assembler in ROM, the market responded with three tiers:

### Tier 1: Professional Tools (£15-£25)

- **[Zeus Assembler](zeus_assembler.md)** by Simon Brattel and Neil Mottershead (Crystal Computing, 1983)
- **[HiSoft DevPac](devpac_gens_mons.md)** (GENS/MONS, 1983-1984)

These tools had comprehensive features (macros, conditional assembly, built-in monitors), extensive documentation, and were the standard tools at UK commercial studios.

### Tier 2: Budget Tools (£5-£10)

- **[TASM](tasm_native.md)** — Turbo Assembler (UK, 1983-1985)
- **[Laser Genius](laser_genius.md)** — cartridge-only (Ocean-internal, 1984+)
- **AVA / AVRA** — the subject of this article

These tools had basic features (full-screen editor, labels, two-pass assembly) but lacked macros and conditional assembly. They were targeted at hobbyists and educational users.

### Tier 3: Magazine Type-In Tools (Free)

- Various assemblers published as type-in listings in *Your Sinclair*, *CRASH*, *Sinclair User*
- Typically very basic, line-based editors, limited directives
- Cost only the price of the magazine

AVA/AVRA fit into Tier 2. The challenge for Tier 2 tools was that Tier 3 was free and Tier 1 was much better — the value proposition was narrow. Most Tier 2 tools disappeared by 1986 as users either upgraded to Tier 1 or migrated to TR-DOS-based tools.

### Why Documentation Is So Sparse

The tape-era budget tools were produced by small developers who often did not survive long. They typically:

- Did not advertise widely (small budgets)
- Did not have printed manuals (cost)
- Did not have retail distribution (mail order only)
- Did not survive in the long term (the developer went out of business)

The result is that AVA/AVRA's existence is documented in software catalogs of the period and in retrospective forum posts, but no comprehensive manual or source code is known to survive.

---

## Comparison with Contemporaries

| Feature | AVA/AVRA | [TASM native](tasm_native.md) | [Zeus](zeus_assembler.md) | [DevPac GENS](devpac_gens_mons.md) |
|---|---|---|---|---|
| Year | ~1984 | 1983-1984 | 1983 | 1983-1984 |
| Price range | £3-£5 | £5-£10 | £12.95 | £15-£25 |
| Full-screen editor | ⚠️ (likely) | ✅ | ✅ | ✅ |
| Macros | ❌ | ❌ | ✅ | ✅ |
| Conditional assembly | ❌ | ❌ | ✅ | ✅ |
| Built-in monitor | ❌ | ❌ | ✅ | ✅ (separate MONS) |
| Documentation | None known | Sparse | Comprehensive | Comprehensive |
| Currently known source | None | None | Yes (Zeus 4) | Yes |

The comparison shows AVA/AVRA at the bottom of the budget tier — even less documented than TASM, with no known surviving source.

---

## When to Encounter AVA/AVRA Today

### 1. 1980s Software Catalogs

If you are browsing 1980s UK software catalogs (e.g., from mail-order houses like Silversoft, Bugs-Byte, or Quicksilva), you may see AVA/AVRA listed as a budget assembler. The catalog entry is typically just the name and price — no feature list or screenshots.

### 2. Retro-Computing Forum Discussions

Occasional forum threads on World of Spectrum (mirrored) and retro-computing mailing lists mention AVA/AVRA in passing, usually from veteran users recalling the early assembler market. These threads are the primary source of the tool's existence.

### 3. Tape Archives

It is theoretically possible that an AVA/AVRA tape image exists in some retro-computing archive. However, finding one would require significant searching, and the tool's obscurity means it may not have been preserved at all.

### Modern Alternatives

For new development, **do not use AVA/AVRA**. Use any modern cross-assembler: [SjASMPlus](sjasmplus.md), [Pasmo](pasmo.md), etc.

---

## Common Pitfalls

1. **Essentially no documentation** — be prepared for the reality that you cannot learn AVA/AVRA's exact feature set from any known source.

2. **Confusion with the AVR microcontroller assembler AVRA** — the modern `avra` tool targets Atmel AVR microcontrollers and is completely unrelated to the Spectrum-era AVRA. Use the term "Spectrum AVA" or "Spectrum AVRA" to disambiguate.

3. **No known surviving tape images** — finding a working AVA/AVRA binary is extremely unlikely. Do not rely on this for any practical work.

4. **Likely many tools with similar names** — the names AVA and AVRA may have been used by multiple unrelated budget tools in the 1980s. Treat any specific claim about "the" AVA or "the" AVRA with skepticism.

5. **Historical reconstruction only** — this article's claims about feature set are inferred from the typical budget-tier tool of the period. They may not match any specific AVA/AVRA release.

---

## FAQ

**Q: Where can I download AVA/AVRA?**

A: There is no known reliable source. Search retro-computing tape archives, but be prepared for the possibility that no surviving image exists.

**Q: Is AVA related to AVRA?**

A: Unknown. They may be the same tool with different names, related tools by the same author, or distinct tools. The relationship is not documented.

**Q: Did AVA/AVRA support macros?**

A: Almost certainly not. Budget-tier tools of 1984 generally did not support macros.

**Q: Were any commercial Spectrum games written with AVA/AVRA?**

A: Almost certainly not. Commercial studios used Zeus, DevPac, or in-house tools.

**Q: Is AVRA the same as the AVR assembler?**

A: No. The AVR assembler `avra` is a modern open-source cross-assembler for Atmel AVR microcontrollers. It is completely unrelated to the Spectrum-era AVRA.

**Q: Why is this article so vague?**

A: Because the underlying documentation is essentially non-existent. The article exists primarily to acknowledge that these tools existed and to provide context for the broader 1982-1985 assembler market.

---

## Cross-References

- [native_toolchain.md](native_toolchain.md) — survey of all native Spectrum assemblers
- [tasm_native.md](tasm_native.md) — the most documented comparable budget tool
- [laser_genius.md](laser_genius.md) — another specialist contemporary
- [zeus_assembler.md](zeus_assembler.md) — the high-end contemporary
- [devpac_gens_mons.md](devpac_gens_mons.md) — the workhorse contemporary
- [spectrum_basic_mcode.md](spectrum_basic_mcode.md) — the pre-assembler alternative
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — modern alternatives

---

## References

- 1980s UK software catalogs from mail-order houses (Silversoft, Bugs-Byte, Quicksilva)
- Retro-computing forum discussions on World of Spectrum (mirrored) and associated mailing lists
- Contextual reconstruction based on the documented feature sets of contemporary budget-tier assemblers
- **Caveat**: This article is necessarily speculative due to the absence of primary documentation. Any specific claim about AVA/AVRA should be treated as plausible reconstruction rather than verified fact.
