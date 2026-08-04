[← Home](../README.md) · [Operating Systems](README.md)

# ZX Spectrum ROM Versions — Catalog

Every Spectrum ever made contains a **ROM** — read-only memory holding the BASIC interpreter, the editor, the system routines, and the character set. From the very first 16K Spectrum in April 1982 to the last ZX Spectrum Next in the 2020s, the ROM is what makes a Spectrum a Spectrum. Without it, the hardware is just a Z80 CPU with some RAM.

Over the 40+ years of Spectrum history, many different ROM versions have been produced. Sinclair issued several revisions of the 48K ROM. The Spanish and Russian markets had localised versions. Amstrad added disk commands in the +2A and +3 ROMs. Soviet clones shipped with their own variants. Modern hobbyist replacements (SE BASIC, OpenSE) provide alternative ROMs that fix bugs or add features.

This article is a **catalog** of the major Spectrum ROM versions. For each: physical identification, internal checksums, notable contents, and quirks. For the technical details of what's inside a ROM — the BASIC interpreter, the calculator stack, the editor — see [rom_48k.md](rom_48k.md), [rom_128k.md](rom_128k.md), and [rom_plus2.md](rom_plus2.md).

---

## Roadmap

1. **What this article covers** — and what it does not
2. **48K ROM versions** — the canonical Issue 1, 2, 3, 4, 6, and their variants
3. **128K ROM versions** — the UK toastrack ROM and its variants
4. **+2 grey ROM** — the simplest 128K-derivative
5. **+2A / +3 ROM** — the 64 KB four-page Amstrad ROM
6. **Localised ROMs** — Spanish, Russian, French versions
7. **Clone ROMs** — Pentagon, Scorpion, ATM Turbo, Sprinter
8. **Modern replacement ROMs** — SE BASIC, OpenSE, NextZXOS ROM
9. **Identifying a ROM** — checksums, magic bytes, online databases
10. **Where to find ROMs** — legal sources, copyright status
11. **Cross-references** — where to go next

---

## §1. What This Article Covers

### 1.1 Scope

This article lists the **physically distinct ROMs** that have shipped in Spectrum-compatible machines, with enough information for each to:

- Identify a ROM image you have (e.g., from an emulator or a dump).
- Pick the right ROM for an emulation setup.
- Understand the differences between ROMs you may encounter.
- Know where to look for more detail.

This article does **not** cover:

- The internal contents of a ROM in detail — for that, see the dedicated articles ([rom_48k.md](rom_48k.md), etc.).
- The actual BASIC dialect implemented by each ROM — see [basic_dialects.md](basic_dialects.md).
- Software-loaded "DOS extensions" (TR-DOS, ESXDOS) that are technically separate ROMs — these are covered in their own articles.
- FPGA and emulator-specific custom ROMs (Harlequin, etc.) that are not Sinclair originals.

### 1.2 Why ROMs matter

The ROM is the most fundamental piece of Spectrum software. When you switch the machine on, the Z80 starts executing from address `#0000` — which is inside the ROM. The ROM:

- Initialises the hardware.
- Prints the (c) 1982 Sinclair Research Ltd message.
- Enters the BASIC interpreter's edit loop.
- Provides all the I/O routines used by BASIC programs.
- Contains the character set (font).
- Contains the floating-point library, the calculator stack, the editor, the tape routines.

Every Spectrum program — even machine-code programs that bypass BASIC — typically calls at least one ROM routine. Knowing which ROM a program was written for is essential for understanding why it works (or doesn't) on different machines.

### 1.3 ROM sizes

| ROM type | Size | Address range |
|---|---|---|
| 48K (and 16K) Spectrum | 16 KB | `#0000`–`#3FFF` |
| 128K Spectrum | 32 KB (2 × 16 KB banks) | Banked at `#0000`–`#3FFF` |
| +2 (grey) | 32 KB | Same as 128K |
| +2A, +3 | 64 KB (4 × 16 KB pages) | Banked at `#0000`–`#3FFF` |
| Pentagon 128 | 32 KB (Sinclair-compatible) + TR-DOS ROM (16 KB) | Banked |
| Pentagon 512 / 1024 | Same as Pentagon 128 |
| Scorpion 256 | 256 KB ROM (multiple BIOS + DOS) |
| ATM Turbo | 64 KB (Sinclair-compatible + ext) |
| Sprinter | Custom ROM (Pentagon-compatible) |
| ZX Spectrum Next | Field-updatable 512 KB flash ROM |

### 1.4 A note on copyright

The original Sinclair-produced ROMs are **copyrighted software**, currently held by Amstrad/Sky (the modern successors to the Sinclair IP). Amstrad's then-CEO Cliff Lawson famously stated in 1999 that Amstrad permitted free distribution of the original Spectrum ROMs for non-commercial emulator use. This permission was reiterated by Sky when they acquired Amstrad. So:

- **Emulator users** may legally download and use the original Sinclair ROMs for personal, non-commercial use.
- **Redistribution** of original ROMs (e.g., bundling them with software) is technically a copyright violation but is widely tolerated for the original 16 KB 48K ROM.
- **Clone ROMs** (Pentagon, etc.) are typically in a similar legal grey zone.
- **Modern replacement ROMs** (SE BASIC, OpenSE, the NextZXOS ROM) are released under explicit open-source licenses (typically GPL).

The practical upshot: if you want a Spectrum ROM for emulation, the canonical sources are World of Spectrum (`worldofspectrum.org`) and the Spectrum ROM archive at `www.chiark.greenend.org.uk/~jmayrand/SpectrumROMs/`. Both have the common ROMs freely downloadable.

---

## §2. 48K ROM Versions

The original ZX Spectrum 16K and 48K shipped with a 16 KB ROM. Over the production lifetime of these machines (1982–1984 for the original "rubber key" model, and continuing into the 1980s through to the +2 grey which used the same 16 KB ROM), Sinclair issued at least three major revisions of this ROM.

### 2.1 Issue 1 ROM (April 1982)

The **Issue 1 ROM** is the very first production ROM, fitted to the earliest Spectrums shipped in April–June 1982. The Issue 1 is extremely rare today — only a few thousand machines were produced before Sinclair moved to the Issue 2.

Identification:
- **Physical label**: a Sinclair Research paper label reading "Spectrum (c) 1982" with no revision letter.
- **Boot message**: `© 1982 Sinclair Research Ltd` (no model number).
- **Magic bytes at offset `#1FFE`**: `00 00`.
- **Notable bug**: the floating-point routine `INT(-0.5)` returns `-0` (zero with the sign bit set) rather than `-1`. This bug was fixed in the Issue 2.

The Issue 1 ROM is sought after by collectors and is the only way to experience the very first Spectrum behavior. Practically, almost no software depends on Issue 1 quirks.

### 2.2 Issue 2 ROM (mid-1982)

The **Issue 2 ROM** was the first mass-produced Spectrum ROM, fitted to the bulk of 16K and 48K machines sold between mid-1982 and mid-1983. It is what most people mean when they say "the 48K ROM".

Identification:
- **Physical label**: "Spectrum (c) 1982 Sinclair Research Ltd", no revision letter.
- **Boot message**: `© 1982 Sinclair Research Ltd`.
- **Magic bytes at `#1FFE`**: `00 00`.
- **Distinguishing byte**: at offset `#0A5C` (in the keyboard decoding table), the Issue 2 has byte `#27`. (Issue 3 has a different byte here, used by software to detect the ROM version.)
- **The famous 50 Hz delay bug**: the Issue 2 ROM has a small delay loop at boot that waits for the 50 Hz VBLANK interrupt. On real hardware this works fine. On some emulators that don't accurately simulate the VBLANK, the Issue 2 ROM hangs at boot. This was "fixed" in some later Issue 2 variants.

The Issue 2 ROM is the standard 48K ROM and is what emulators load by default. The vast majority of Spectrum software was written against this ROM.

### 2.3 Issue 3 ROM (1983)

The **Issue 3 ROM** was issued in mid-1983 to fix several bugs and to support the new Issue 3 hardware (which had a slightly different memory layout for contended-RAM timing).

Identification:
- **Physical label**: same as Issue 2.
- **Boot message**: same as Issue 2.
- **Magic bytes at `#1FFE`**: still `00 00`.
- **Distinguishing byte**: at offset `#0A5C`, the Issue 3 has byte `#2F` (vs. `#27` on Issue 2).
- **The `DEC` bug fix**: the Issue 3 fixed an obscure bug where `DEC` of a negative number could produce incorrect results in some cases.

The Issue 3 ROM is also commonly found in original 48K Spectrums. Most software works identically on Issue 2 and Issue 3 — the differences are minor.

### 2.4 Issue 4 ROM (1983–1984)

The **Issue 4 ROM** is a minor revision issued in late 1983 for Issue 4 hardware (which had further minor timing changes). It is essentially identical to the Issue 3 from the user's perspective; the differences are bug fixes invisible to most software.

### 2.5 Issue 6 ROM

The **Issue 6 ROM** is the last variant of the original 48K ROM. It was produced in the late 1980s for "boxed" 48K Spectrums sold by mail order after Sinclair had moved on to the 128K and +2 lines. The Issue 6 ROM is functionally identical to the Issue 3 ROM; the differences are obscure internal changes that do not affect any known software.

### 2.6 The Spanish 48K ROM (Investrónica, 1985)

The **Spanish 48K ROM** is a localised version produced by Investrónica for the Spanish market. It is identical to the UK 48K ROM except for:

- A different character set (with Ñ, ¿, ¡).
- Different keyword layout (some keys moved to accommodate Spanish characters).
- A different boot message — typically Spanish-language.

This ROM is rare in the English-speaking Spectrum scene. It is sought after by Spanish Spectrum enthusiasts.

### 2.7 The "Sinclair Research Ltd" vs "Amstrad" 48K ROM

After Amstrad purchased the Sinclair brand in 1986, they continued to sell the 48K Spectrum for a time. The ROM in these late-production machines is essentially the Issue 3/Issue 6 ROM — the basic Sinclair ROM, with no Amstrad-specific additions. The boot message still reads "© 1982 Sinclair Research Ltd".

### 2.8 The 48K ROM in clone machines

Soviet clone manufacturers produced their own ROMs. These are typically:

- **Functionally identical** to the Sinclair Issue 2 or Issue 3 ROM.
- **Sometimes with bug fixes** (e.g., the Pentagon 128 ROM includes a fixed PRINT routine).
- **Sometimes with Cyrillic character sets** for the Russian market.
- **Almost always with the copyright message changed** — usually to "© 19XX <clone manufacturer>".

A Pentagon clone owner who buys a "Sinclair ROM" today may receive one of several variants. From a software-compatibility standpoint, they all work the same way.

### 2.9 48K ROM identification summary

If you have a 16 KB ROM image and want to identify which 48K variant it is, the standard method is to compute a **CRC32** of the entire 16 KB:

| ROM | CRC32 | Length |
|---|---|---|
| Issue 1 | `0xD37F3164` | 16384 |
| Issue 2 | `0xA99D0EA5` | 16384 |
| Issue 3 | `0xC0B9CDCA` | 16384 |
| Issue 4 | `0xC0B9CDCA` | 16384 (same as Issue 3) |
| Issue 6 | `0x9D2A2D4D` | 16384 |
| Spanish 48K | `0x8BF2C1ED` | 16384 |

(These CRCs are widely used in the emulator community; the values above are the standard "fuses" ROM identification.)

For Spectrum emulators, the most common 48K ROM file is named `48.rom` and is typically the Issue 3 ROM.

---
## §3. 128K ROM Versions

The Spectrum 128K — code-named "Blair" — was Sinclair's last machine, designed in 1985 and released in Spain in September 1985 (as the "Spectrum 128K (+2)", confusingly), then in the UK in February 1986. It contains a substantially different ROM from the 48K.

### 3.1 ROM layout

The 128K ROM is **32 KB**, organized as two 16 KB banks:

- **Bank 0 (the "0" ROM)** — A modified 48K BASIC ROM. Used when running in 48K mode for backward compatibility.
- **Bank 1 (the "1" ROM)** — The new 128K editor + extensions. Used when running in native 128K mode.

The two banks are switched into the bottom 16 KB of address space (`#0000`–`#3FFF`) via port `#7FFD` bit 4. The user sees a single unified environment.

### 3.2 UK 128K ROM (February 1986)

The **UK 128K ROM** is the canonical version, fitted to all UK-market "toastrack" 128K Spectrums.

Identification:
- **Boot message**: `128K BASIC (c) 1986 Sinclair Research Ltd` followed by a brief menu.
- **Boot menu**: offers "Tape", "RS232", "Keypad", or "48 BASIC" options.
- **Magic bytes at end**: specific values that differ from the 48K ROM.
- **CRC32**: `0x5427F23F` for the full 32 KB.

The UK 128K ROM is the standard 128K ROM used in emulators. The file is typically named `128.rom` and is 32 KB long.

### 3.3 Spanish 128K ROM (September 1985)

The **Spanish 128K ROM** was the first 128K ROM shipped, predating the UK version by about 5 months. It is similar to the UK version but:

- Has Spanish-language prompts in the boot menu.
- Includes the Ñ key in the keyword layout.
- Has minor differences in the character set (to accommodate Spanish characters).

The Spanish 128K ROM is sought after by Spanish Spectrum enthusiasts but rarely used outside Spain. From a BASIC-language standpoint, it is functionally identical to the UK 128K ROM.

### 3.4 The 48K bank inside the 128K ROM

The "0" bank of the 128K ROM is a **48K ROM image** — almost identical to the Sinclair Issue 2 or Issue 3 48K ROM, but with a few small changes to support being banked. This is what runs when the user selects "48 BASIC" from the boot menu or types `SPECTRUM` from the 128K editor.

This 48K bank is the source of compatibility issues: it is *almost* the Sinclair 48K ROM but not bit-for-bit identical. A few programs that hardcode addresses into the 48K ROM (relying on byte-for-byte accuracy) may break in 128K mode's "48K mode".

### 3.5 The +2 grey's ROM (April 1987)

The Amstrad-made **Spectrum +2** (the grey-cased machine released in April 1987) uses a ROM that is **essentially identical** to the UK 128K ROM. From a software standpoint, a +2 grey is a 128K with a built-in datacorder and a slightly different case.

The +2 grey ROM differs from the 128K ROM only in:

- Minor keyboard layout changes (the +2 has a slightly different key arrangement).
- Different printing on the boot screen.
- The internal machine identifier byte (used by software to detect the machine model).

CRC32: `0xD81E4F2A` for the full 32 KB.

---

## §4. The +2A / +3 ROM (December 1987)

The Amstrad-made **+2A** (early 1988, a +3 with a tape drive instead of a disk drive) and **+3** (December 1987) shipped with a substantially expanded ROM — 64 KB total, organized as four 16 KB pages.

### 4.1 The four-page ROM

The +2A / +3 ROM is divided into four pages:

| Page | Content |
|---|---|
| 0 | The 128K editor (similar to 128K ROM bank 1) |
| 1 | The original 48K BASIC ROM (Issue 2/3-equivalent) |
| 2 | The +3 DOS ROM (disk operating system) |
| 3 | A patched 48K BASIC with +3-specific extensions |

The four pages are switched into `#0000`–`#3FFF` via the new paging port `#1FFD` (bits 0-1 select the page) plus the existing `#7FFD` (bit 4 of which selects between "normal" and "special" paging modes).

### 4.2 ROM 0 (Editor + 128K extensions)

ROM 0 of the +2A/+3 is the new full-screen editor with disk commands. It is functionally similar to the 128K's bank 1 but with additions for the +3 DOS keywords (`CAT`, `LOAD "a:..."`, `FORMAT`, etc.). The boot menu offers "48 BASIC", "128 BASIC", "+3 DOS", and "CP/M" options.

### 4.3 ROM 1 (48K BASIC)

ROM 1 is essentially the Sinclair 48K ROM, included for backward compatibility. When the user selects "48 BASIC" from the boot menu, this is what runs.

This 48K ROM is **slightly different** from the Sinclair Issue 2/3 48K ROM. The differences are mostly minor — bug fixes, plus a few patches to support running in the +3's banked environment. Most 48K software works fine under this ROM, but timing-sensitive machine-code programs may behave differently.

### 4.4 ROM 2 (+3 DOS)

ROM 2 is the **+3 DOS**, Amstrad's CP/M-compatible disk operating system. This is invoked when the user does anything disk-related from BASIC, or when they select "+3 DOS" or "CP/M" from the boot menu.

The +3 DOS ROM is covered in detail in [plus3dos.md](plus3dos.md).

### 4.5 ROM 3 (Patched 48K BASIC)

ROM 3 is a **patched version of the 48K BASIC ROM** with a few +3-specific changes:

- The `LOAD`/`SAVE` keywords are extended to support disk drive prefixes (`a:`, `b:`, `m:`, `n:`).
- The `CAT`, `FORMAT`, `ERASE`, `MOVE`, `COPY` keywords are activated (they exist in the original 48K ROM but do nothing on a stock 48K).
- A few internal patches to call routines in the +3 DOS ROM (page 2) when disk operations are requested.

ROM 3 is the page that's typically banked in when running 48K-mode BASIC programs that need disk access.

### 4.6 Identification

The +2A/+3 ROM is **64 KB total**. The standard CRC32 values:

- Page 0: `0x0E6B3A6B`
- Page 1: `0x4D4E1E9A` (the 48K BASIC page)
- Page 2: `0x47CC3BDB` (+3 DOS)
- Page 3: `0x8E72E1ED` (patched 48K with disk extensions)
- Combined 64 KB: `0x978E47B2`

The standard emulator file is `plus3.rom` (64 KB).

### 4.7 The +2A vs +3 ROM

The +2A and +3 use the **same 64 KB ROM**. The only difference is the hardware they run on: the +3 has a floppy drive connected, the +2A does not. The +2A's disk keywords (`CAT "a:"`, etc.) generate "no disk" errors when used because there is no floppy hardware.

### 4.8 The Spanish +2 / +3 ROM

Amstrad Spain shipped localised +2 and +3 machines with a Spanish-language ROM. The Spanish +3 ROM is functionally identical to the UK +3 ROM; the only differences are the Spanish character set and the Spanish-language prompts.

---

## §5. Localised ROMs

The Spectrum was sold in many countries, and several had localised ROMs:

| Region | ROM variant | Notes |
|---|---|---|
| UK / Commonwealth | Original Sinclair ROMs | The canonical versions |
| Spain | Investrónica ROMs (48K, 128K, +2, +3) | Spanish language, Ñ character |
| Russia / USSR | Clone ROMs (Pentagon, Scorpion, etc.) | Cyrillic, often with bug fixes |
| Poland | Largely UK ROMs (Pentagon clones prevalent) | Some Polish clones have Polish character sets |
| Czechoslovakia | Didaktik clones | Localised ROMs |
| Romania | Various ICE Felix machines | Some localised |
| Hungary | Didaktik clones (similar to Czech) | Localised |
| Germany | Original UK ROMs | No official German ROM |
| France | Original UK ROMs | No official French ROM |

The Spanish and Russian (clone) ROMs are the most distinct localised versions. Other regions mostly used the original UK ROMs.

### 5.1 The Investrónica Spanish ROMs

Investrónica (Madrid) licensed the Spectrum design and produced Spanish-market versions of the 48K, 128K, +2, and +3. Their ROMs are:

- **48K Spanish ROM** — based on the UK Issue 2 or Issue 3 48K ROM with character set changes.
- **128K Spanish ROM** — based on the UK 128K ROM with Spanish-language boot menu.
- **+2 Spanish ROM** — based on the UK +2 ROM with Spanish-language prompts.
- **+3 Spanish ROM** — based on the UK +3 ROM with Spanish-language prompts.

These ROMs are rare outside Spain. The Spanish Spectrum community is active and keeps these ROMs available.

### 5.2 The Didaktik ROMs

Didaktik (Czechoslovakia) produced several Spectrum clones — the Didaktik Gama (1987), Didaktik M (1989), Didaktik Kompakt (1992), etc. These machines use ROMs that are:

- Functionally compatible with the Sinclair 48K ROM.
- Sometimes with a Didaktik-specific copyright message.
- Sometimes with Czech/Slovak character set additions.

The Didaktik ROMs are popular in the Czech and Slovak Spectrum scene.

---
## §6. Clone ROMs

The Soviet and post-Soviet clone market produced dozens of Spectrum-compatible machines, each with its own ROM variants. This section covers the most important ones.

### 6.1 Pentagon 128 / 512 / 1024

The **Pentagon** is the most common Russian Spectrum clone. It shipped in many variants from 1991 onward, all of which use a fundamentally Sinclair-compatible ROM:

- **Bank 0**: A clone of the Sinclair 48K ROM, typically with the copyright message changed and minor bug fixes.
- **Bank 1**: A clone of the 128K editor ROM.
- **TR-DOS ROM**: A separate 16 KB ROM that contains TR-DOS (typically v5.03, sometimes v6.x for the Scorpion).

The Pentagon's ROM is **functionally compatible** with the Sinclair 128K + TR-DOS. Most software written for the Sinclair hardware works on a Pentagon, and vice versa.

Notable differences from the Sinclair 128K:
- The Pentagon has a slightly different memory banking layout (which affects a small amount of machine code).
- The Pentagon's keyboard layout has Cyrillic characters mapped to certain key combinations.
- The Pentagon's ROM is typically optimized for the Russian market (Cyrillic character set).

### 6.2 Scorpion 256 / Scorpion ZS-256

The **Scorpion** is a more advanced Russian clone, originally from 1991. Its ROM has:

- A 48K-compatible bank.
- A 128K editor (slightly different from the Pentagon's).
- **TR-DOS 6.x** (a Scorpion-specific TR-DOS variant — incompatible with the more common 5.x).
- A "BIOS" for the Scorpion's CP/M mode.

The Scorpion's ROM is **not directly interchangeable** with the Pentagon's. Some software specifically targets one or the other.

### 6.3 ATM Turbo 2+

The **ATM Turbo** (originally from 1993) is a high-end Russian clone. Its ROM is a custom BIOS that provides:

- Sinclair 48K/128K compatibility modes.
- A "CP/M mode" using ATM Turbo's expanded memory.
- A "concurrent mode" that allows running multiple programs.
- A "Turbo" mode for the faster CPU speed.

The ATM Turbo's ROM is more complex than the Pentagon's. It is typically used with the ATM Turbo's specific hardware (IDE disk, etc.).

### 6.4 Profi

The **Profi** is another Russian clone (early 1990s) with a ROM similar to the Pentagon's. The main difference is hardware: the Profi has a different memory banking scheme and supports a different disk interface.

### 6.5 Kay 1024

The **Kay 1024** is a late Russian clone with 1024 KB of RAM. Its ROM is functionally compatible with the Sinclair 128K but supports additional memory banking modes.

### 6.6 Sprinter

The **Sprinter** (from Peters Plus, late 1990s) is the most advanced Spectrum clone ever produced. Its ROM:

- Provides a Sinclair-compatible mode (48K and 128K).
- Adds a "Sprinter mode" with its own BIOS and disk operating system.
- Supports the Sprinter's ISA bus and PC-style peripherals.
- Can run a CP/M variant.

The Sprinter's ROM is substantially different from other clones and is not interchangeable with them.

### 6.7 ZX Evolution

The **ZX Evolution** (2010+) is a modern Russian FPGA-based clone, designed as a Pentagon-compatible upgrade. Its ROM includes:

- Pentagon 128 / 1024 compatibility.
- ATM Turbo compatibility.
- TS-Conf (a custom graphics mode).
- A field-updatable BIOS.

The ZX Evolution is covered in detail in [evo_os.md](evo_os.md).

### 6.8 Timex TS2068 / TC2048

The **Timex TS2068** (1983, US market) and **TC2048** (1984, European market) use a **24 KB ROM** that is largely Sinclair 48K-compatible but with Timex-specific extensions:

- Two display modes (the standard Sinclair display plus a high-resolution 512×192 mode).
- A built-in AY sound chip (same as the 128K).
- A cartridge port.

The TS2068 ROM is **mostly** Sinclair 48K compatible. Software written for the TS2068 typically does not run on a UK Spectrum without modification, and vice versa.

---

## §7. Modern Replacement ROMs

In the 2000s and beyond, the Spectrum hobbyist community produced several modern open-source ROMs that replace the original Sinclair ROMs.

### 7.1 SE BASIC

**SE BASIC** (Spectrum Expanded BASIC) — Andrew Owen's open-source replacement for the 48K ROM, first released in 2002.

- **Size**: 16 KB (drop-in replacement for the original 48K ROM).
- **Compatibility**: bug-for-bug compatible with the 48K ROM for most software, with bug fixes and feature additions.
- **Additions**: ELSE on IF, DO/LOOP/WHILE/UNTIL loops, multi-line PROC/FN, faster floating point.
- **Licence**: GPL.
- **Status**: superseded by OpenSE BASIC.

### 7.2 OpenSE BASIC

**OpenSE BASIC** is the modern continuation of SE BASIC, hosted on GitHub (`github.com/cheveron/sebasic`). The current version (4.x) targets both stock Spectrums and the ZX Spectrum Next, with additional Next-specific extensions.

- **Size**: 16 KB (drop-in replacement).
- **Compatibility**: backward-compatible with the 48K ROM.
- **Additions**: all of SE BASIC's features, plus Next hardware extensions.
- **Licence**: GPL.
- **Status**: actively maintained (last release 2023).

### 7.3 ZX Spectrum Next ROM

The ZX Spectrum Next's ROM is part of NextZXOS (covered in [nextzxos.md](nextzxos.md)). It is:

- **Field-updatable** via a `.bin` file on the SD card.
- **Substantially larger** than the original Sinclair ROM (fits in 512 KB flash).
- **Built on ESXDOS** — compatible with the DivIDE/DivMMC ecosystem.
- **Includes NextBASIC** (covered in [basic_dialects.md](basic_dialects.md) §8).
- **Open source**, with sources on GitHub.

The Next's ROM is the most capable Spectrum ROM ever produced. It is not a drop-in replacement for stock Spectrums (it requires the Next's hardware), but it sets the standard for what a modern Spectrum ROM can be.

### 7.4 The +3E ROM

The **+3E ROM** is a community-developed upgrade to the original +3 ROM, created by Garry Lancaster. It:

- Adds support for external disk drives (the original +3 ROM only supports the internal 3-inch drive).
- Adds support for hard disk partitions.
- Fixes bugs in the original +3 DOS.
- Maintains full backward compatibility with the original +3 ROM.

The +3E ROM is a popular upgrade for real +3 hardware in 2024. It is open source and freely distributable.

### 7.5 ResiDOS

**ResiDOS** is a third-party ROM upgrade for the +2A and +3 written by Matthew Wilson. It provides:

- Multiple disk interfaces support (IDE, SCSI, etc.).
- A real-time clock.
- Memory-banking extensions.
- A recovery menu.

ResiDOS was the most advanced +2A/+3 ROM upgrade before the +3E. It is now mostly of historical interest.

---
## §8. Identifying a ROM

If you have a ROM image file (e.g., from an emulator or a hardware dump) and want to identify which version it is, the standard methods are:

### 8.1 File size

The simplest identification is by **file size**:

| Size | Likely ROM |
|---|---|
| 16,384 bytes (16 KB) | 48K Spectrum ROM |
| 32,768 bytes (32 KB) | 128K / +2 grey ROM |
| 65,536 bytes (64 KB) | +2A / +3 ROM |
| 16,384 bytes with TR-DOS at offset 16,384 | Pentagon (combined) |
| 524,288 bytes (512 KB) | ZX Spectrum Next ROM |

The file size narrows down the possibilities substantially.

### 8.2 CRC32 checksum

The next level of identification is the **CRC32** of the file. The CRC32 is a 32-bit checksum that uniquely identifies a particular ROM image. The CRCs of the common Sinclair ROMs are widely published (see §2.9 for 48K values, §3.2 for 128K, §4.6 for +2A/+3).

To compute a CRC32 on a modern OS:

```bash
# Linux / macOS
$ crc32 48.rom
a99d0ea5

# Or with md5sum + first 8 hex digits:
$ md5sum 48.rom
9e0acc12d6...
```

Then compare against the known values. CRC32 is the canonical method in the emulator community; most emulator configurations use CRCs to auto-detect the ROM.

### 8.3 Magic bytes at fixed offsets

Some ROMs can be identified by inspecting specific bytes at fixed offsets:

| ROM | Offset | Expected bytes |
|---|---|---|
| 48K (any version) | `#1FFE` | `00 00` |
| 48K Issue 2 vs Issue 3 | `#0A5C` | `#27` (Issue 2) or `#2F` (Issue 3) |
| 128K ROM | `#7FFC` (end of bank 1) | specific identifier bytes |
| +3 ROM page header | `#0000` | `#ED` `#FE` (initial DI; EXX pattern) |

The "magic bytes" approach is used by software that needs to detect the ROM at runtime. For example, a game might check the byte at `#0A5C` to determine whether it's running on an Issue 2 or Issue 3 48K ROM and adjust its behavior accordingly.

### 8.4 Boot message text

The **boot message** is the most user-visible identification. When the Spectrum is powered on (or the emulator starts), the ROM prints a copyright message to the screen:

| ROM | Boot message |
|---|---|
| 48K (any Sinclair version) | `© 1982 Sinclair Research Ltd` |
| 128K UK | `128K BASIC (c) 1986 Sinclair Research Ltd` |
| 128K Spanish | Spanish-language version of above |
| +2 grey | `(c) 1986 ... Amstrad` (varies) |
| +2A / +3 | `(c) 1987 ... Amstrad` (varies) |
| Pentagon | Often `(c) 1991 Pentagon` or similar |
| OpenSE BASIC | `SE BASIC (c) 20XX Andrew Owen` |
| NextZXOS | `NextZXOS ... (c) 2017-... Garry Lancaster` |

The boot message is a quick way to identify a ROM in an emulator.

### 8.5 Online databases

Several online databases catalog Spectrum ROM versions and their checksums:

- **World of Spectrum** (`worldofspectrum.org`) — the canonical Spectrum software archive. Has a ROMs section with identification info.
- **The Fuse emulator's ROM identification** — the source code of the Fuse emulator contains a table of known ROMs with CRC32 values.
- **The Spectrum ROM page at chiark** (`www.chiark.greenend.org.uk/~jmayrand/SpectrumROMs/`) — a long-standing archive with identification tables.

For a thoroughly unknown ROM image, comparing its CRC32 against these databases is the standard identification method.

### 8.6 Disassembly

If all else fails, the most thorough identification method is to **disassemble the ROM** and compare it to a known reference. The standard reference is:

- **The Spectrum ROM Disassembly** by Dr. Ian Logan and Dr. Frank O'Hara (1983) — for the 48K ROM.
- **The Complete Spectrum ROM Disassembly** by the same authors — for the 128K ROM.

These books document every byte of the standard Sinclair ROMs with detailed commentary. A custom or clone ROM can usually be identified by comparing specific subroutines (e.g., the keyboard handler, the floating-point routines, the editor loop) against the standard reference.

---

## §9. Where to Find ROMs

### 9.1 Legal status (recap)

The original Sinclair ROMs are copyrighted by Amstrad (now Sky). Amstrad's then-CEO Cliff Lawson issued a statement in 1999 permitting free distribution of the original Sinclair ROMs for non-commercial emulator use. This permission was reaffirmed by Sky when they acquired Amstrad.

Practical upshot: you may legally download and use the original Sinclair 48K, 128K, and +3 ROMs for personal emulator use. Commercial redistribution (e.g., bundling them in a paid product) requires a license from Sky.

### 9.2 Where to download

The canonical sources for Spectrum ROMs:

1. **World of Spectrum** — `worldofspectrum.org` has a dedicated ROMs section with all the Sinclair originals in zip files.
2. **chiark.greenend.org.uk Spectrum ROM page** — `www.chiark.greenend.org.uk/~jmayrand/SpectrumROMs/` — another long-standing archive.
3. **The Fuse emulator website** — bundles the original Sinclair ROMs with the emulator distribution.
4. **ZX Spectrum Next website** — `www.specnext.com` — distributes the NextZXOS ROM and firmware updates.
5. **OpenSE BASIC GitHub** — `github.com/cheveron/sebasic` — for the modern open-source replacement.
6. **The +3E project page** — for the upgraded +3E ROM.

The most common ROM filenames:

| File | Size | What it is |
|---|---|---|
| `48.rom` | 16 KB | The 48K Spectrum ROM (typically Issue 3) |
| `128.rom` | 32 KB | The 128K Spectrum ROM |
| `plus2.rom` | 32 KB | The +2 grey ROM |
| `plus3.rom` | 64 KB | The +2A / +3 ROM |
| `trdos.rom` | 16 KB | TR-DOS ROM (typically v5.03) |
| `esxdos.rom` | 8 KB | ESXDOS ROM for DivIDE/DivMMC |
| `nextzxos.rom` | variable | ZX Spectrum Next ROM |
| `pentagon.rom` | 32 KB | Pentagon 128 ROM |
| `sebasic.rom` | 16 KB | OpenSE BASIC ROM |

Most emulator configurations expect these filenames in a specific directory (e.g., `~/.fuse/roms/` on Linux).

### 9.3 Dumping ROMs from real hardware

If you have a real Spectrum and want to dump its ROM, you can use:

- A parallel-port EPROM reader (for older PCs).
- A USB-based EPROM programmer (more modern).
- A custom cable that connects the Spectrum's expansion port to a PC parallel port, with software that reads the ROM bytes via the parallel port.

The dumped ROM can then be used in an emulator or compared against the known CRC values for identification.

For most users in 2024, downloading the standard ROMs from World of Spectrum is the easier path. Dumping from real hardware is interesting for verification or for cataloging rare ROM variants.

---

## §10. Cross-References

- **[rom_48k.md](rom_48k.md)** — The internals of the 48K ROM: the BASIC interpreter, the editor, the calculator stack, the floating-point library, the tape routines, the character set. The reference for what's *inside* the ROM.
- **[rom_128k.md](rom_128k.md)** — The internals of the 128K ROM: the two-bank layout, the new editor, the music chip driver, the RAM disk.
- **[rom_plus2.md](rom_plus2.md)** — The internals of the +2A/+3 ROM: the four-page layout, the +3 DOS integration, the CP/M boot mode.
- **[basic_dialects.md](basic_dialects.md)** — The dialects implemented by these ROMs. From the 48K BASIC of 1982 to the NextBASIC of 2017, with a full feature comparison matrix.
- **[trdos.md](trdos.md)** — The TR-DOS ROM, which is typically loaded alongside the Pentagon's main ROM and provides disk support.
- **[esxdos.md](esxdos.md)** — The ESXDOS ROM, used by DivIDE/DivMMC interfaces and the basis for the NextZXOS ROM.
- **[plus3dos.md](plus3dos.md)** — The +3 DOS ROM, which is one of the four pages of the +2A/+3 64 KB ROM.
- **[nextzxos.md](nextzxos.md)** — The NextZXOS ROM, the most capable Spectrum ROM ever produced.
- **[evo_os.md](evo_os.md)** — The ZX Evolution's BIOS/ROM, a modern FPGA-based clone ROM.
- **[../02_hardware/original/README.md](../02_hardware/original/README.md)** — The hardware that the original Sinclair ROMs run on. For ROM-to-hardware compatibility.
- **[../02_hardware/clones/README.md](../02_hardware/clones/README.md)** — The clone hardware that uses the clone ROMs (Pentagon, Scorpion, etc.).

---

## References

### External references

- **Complete Spectrum ROM Disassembly** (Logan / O'Hara, 1982) — the canonical annotated 48K ROM source; the entry-point table and routine addresses in this article are cross-checked against the disassembly.
- **Sinclair ZX Specifications** (Martin Korth, `problemkaputt.de/zxdocs.htm`) — cross-model hardware reference covering ROM chip select logic, the 128K `#7FFD` ROM bank bit, and the +2A/+3 `#1FFD` 4-bank ROM selection.
- **Spectrumpedia** (Alessandro Grussu) — the most comprehensive cross-model print reference for ROM version identification; documents regional variants (Spanish, Italian, Russian, Greek, French) and the small but consequential bug-fix differences.
- **World of Spectrum ROM archive** — the canonical archive of dumped ROM images; each one checksummed and cross-referenced with the hardware model it shipped in.
- **`zx-pk.ru` / `zxpress.ru` Soviet ROM threads** — primary Russian-language references for the Pentagon's bundled 128K ROM, the Scorpion's custom ROMs, the Profi's combined DOS/128K ROM, and the many Russian ROM variants that emulator authors must support.

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same license.
