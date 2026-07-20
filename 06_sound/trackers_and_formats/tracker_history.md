[← Home](../../README.md) · [Sound](../README.md) · [Trackers & Formats](README.md)

# Tracker History — From Sound Tracker (1990) to Arkos Tracker 3

> **Applies to**: All tracks. The ZX music tooling ecosystem is unusual in that it was born on the Spectrum itself (1990), migrated to the PC (2002+), and is still actively developed today (Arkos Tracker 3, Vortex Tracker II). No other 8-bit platform has a comparable continuous lineage of music editing software spanning 35 years.

---

## Overview

The ZX Spectrum's music software is a story of **born-on-host, migrated-to-PC**. The first generation of music trackers (1985–2002) ran **on the Spectrum itself** — the composer edited notes directly in a Spectrum program, saved `.STC`/`.STP`/`.PT3` modules to tape or disk, and used a small player routine to play them back. The second generation (2000–present) moved editing to the PC but kept producing Spectrum-compatible module formats, because the audience was still Spectrum owners and the playback hardware was still the AY.

This continuity is the defining feature of the ecosystem. A `.PT3` module written on a real Pentagon in 1997 loads unchanged in Vortex Tracker II on Windows 11 in 2025, plays through the same register-write sequence, and sounds identical on the same AY chip. No other 8-bit platform preserves its music tooling lineage this intact.

The article is organized into three eras plus the modern PC generation:

1. **Era 1 (1985–2002): On-Spectrum trackers** — beeper trackers, AY trackers, the Pro Tracker lineage, and digital (Covox/GS) trackers.
2. **Era 2 (2000–present): PC-based AY editors** — Vortex Tracker II (Sergey Bulba) and Arkos Tracker (Julien Nevo).
3. **Era 3 (2010s–present): Multi-platform and modern** — Vortex Tracker 3 (open-source C# port), Arkos Tracker 3, and web-based tools.

### Naming Convention

| Term | Meaning |
|---|---|
| **Tracker** | A music editor patterned after early demoscene tools — patterns, channels, notes entered in a grid (not piano roll) |
| **Module / Mod** | A self-contained music file containing note patterns + instrument definitions + effects |
| **Player routine** | The small Z80 routine embedded in a game/demo that reads a module and writes AY registers each frame |
| **STC / STP / PT3 / PT2** | The four major module formats, named after the trackers that produced them |
| **Sample / Instrument** | In AY tracker parlance, an "instrument" is an envelope-and-volume waveform definition, not a PCM sample |
| **Ornament** | A PT3-specific term for an arpeggio pattern — a list of pitch offsets applied to a note over time |
| **Golden Disk Corp.** | St. Petersburg software house (sometimes spelled "Golden Disc") — authors of Pro Tracker 1.x/2.x/3.x |
| **Bzyk** | Jarek Burczynski (Poland) — author of the original Sound Tracker (1990), the earliest AY grid tracker |
| **Bulba (S.V.)** | Sergey Bulba — author of Vortex Tracker II (PC, 2000+), the standard PC-based PT3 editor. |

---

## Era 1: On-Spectrum Trackers (1985–2002)

The first generation of ZX music tooling happened entirely **on the ZX Spectrum itself**. The composer bootstrapped into a tracker program, edited notes using the Spectrum keyboard, previewed through the machine's own sound hardware (beeper or AY), and saved the result as a module file. The catalog below is taken from the authoritative [zxtunes.com software list](https://zxtunes.com/software_list.php), which preserves 30 distinct Spectrum-native editors.

### Pre-AY Era: Beeper Trackers (1985–1990)

The earliest Spectrum music software predates the AY chip entirely — these editors targeted the 48K beeper:

| Tracker | Author | Year | Format |
|---|---|---|---|
| **Wham! The Music Box** | Mark Time Ltd. (Mark Alexander) | 1985 | proprietary |
| **The Mark Time Music Box** | Mark Time Ltd. (Mark Alexander) | 1986 | proprietary |
| **Music Synth 48K** | Simon Tillson | 1989 | proprietary |
| **Orfeus Music Assembler** | Proxima | 1990 | proprietary |

These early tools established the editing paradigm (note grid, instrument definitions, song position table) but had no AY to address. The Wham! family from Mark Time is the **earliest Spectrum-native music editor** in the historical record.

### The AY Generation: Sound Tracker and Contemporaries (1990–1993)

With the 128K's AY-3-8912 now widespread, a first generation of AY-targeting trackers emerged. The most influential was **Sound Tracker 1.1** by **Jarek Burczynski (Bzyk)** — a Polish author, often incorrectly credited to Sergey Bulba in Western sources. Bulba's role began later, with Vortex Tracker II on the PC.

| Tracker | Author | Year | Format |
|---|---|---|---|
| **Sound Tracker 1.1** | Jarek Burczynski (Bzyk) | 1990 | `.STC` |
| **A.Y. Tracker 1.0** | Jonathan Cauldwell | 1992 | proprietary |
| **Asc Sound Master 0.12** | Andrew Sendetskiy (ASC) | 1992 | `.ASC` / `.AS0` |
| **Sample Tracker 2.0** | CBM | 1992 | digital |
| **SQ-Tracker** | George K. | 1993 | `.SQT` |
| **Super Sonic 1.20** | Klav | 1993 | proprietary |

Sound Tracker 1.1 established the foundational pattern that every later AY tracker would inherit: a pattern grid of 3 channels (one per AY voice), notes entered by name (C-4, D-4, etc.), per-note instrument selection, and simple effects columns. The composer assembled patterns into a **position table** (a list specifying which pattern plays in which order) to build a complete song.

In parallel, **Jonathan Cauldwell**'s A.Y. Tracker (1992) took a different approach aimed at game developers. **Asc Sound Master** (Andrew Sendetskiy, 1992) produced the `.ASC` format that Vortex Tracker II can still import today. **SQ-Tracker** (George K., 1993) introduced the `.SQT` format later used by the digital-only SQ Tracker 1.0 (1997, Sham Software — a different author despite the similar name).

### Pro Tracker Lineage (1995–1997)

The Pro Tracker family is the most consequential series of AY trackers in the platform's history. All four major versions were produced by **Golden Disk Corp.** (sometimes spelled "Golden Disc"), a St. Petersburg software house — not by any single individual.

| Tracker | Year | Module Format |
|---|---|---|
| **Pro Tracker 1.1** | 1995 | `.PT1` / `.STP` |
| **Pro Tracker 2.1** | 1995 | `.PT2` |
| **Pro Tracker 3.1** | 1996 | `.PT3` |
| **Pro Tracker 3.31** | 1997 | `.PT3` (final on-Spectrum revision) |

Each version refined the editing model and tightened the module format. Pro Tracker 3.x introduced two innovations that would define the platform for the next 30 years:

1. **The PT3 module format** — a compact, self-contained file containing patterns, instruments (called "samples"), arpeggio patterns (called "ornaments"), and a position table. The format is documented in detail in [PT3 Format](pt3_format.md).
2. **The separate player routine** — a small (~300–700 byte) Z80 routine that reads a PT3 module and writes AY registers each frame. This routine could be embedded in any game or demo, decoupling music playback from the editor.

PT3's compactness and the player's small size made it the dominant format of the late-Soviet-clone era and beyond. Thousands of PT3 modules were composed between 1996 and the early 2000s, and the format remains in active use today.

### Late On-Spectrum AY Trackers (1995–1999)

The period 1995–1999 saw a final flowering of on-Spectrum AY trackers as the Soviet clone scene reached peak activity:

| Tracker | Author | Year | Format |
|---|---|---|---|
| **Sound Tracker Pro** | KSA | 1996 | `.STP`-family |
| **Cacofony Professional System 0.10** | S.T.A.S. | 1995 | proprietary |
| **Pro Sound Maker (demo)** | Team V | 1995 | `.PSM` |
| **Fast Tracker 1.0** | Digital Reality | 1997 | `.FTC` |
| **Global Tracker 1.1** | Global Corp. | 1998 | `.GTR` |
| **Pro Sound Creator 1.07** | E-mage Group | 1999 | `.PSC` |

None of these displaced PT3 as the dominant interchange format, but each accumulated its own library of modules. Vortex Tracker II's import menu today reads all of these formats (`.PSM`, `.FTC`, `.GTR`, `.PSC`, `.ASC`, `.AS0`, `.SQT`, etc.) — a testament to the fragmentation of the era.

### Digital Trackers (1994–2004, Covox / General Sound)

A parallel lineage targeted digital sound hardware (Covox, SounDrive, General Sound) rather than the AY. These editors produce sample-based modules — the Soviet equivalent of PC MOD files:

| Tracker | Author | Year | Target |
|---|---|---|---|
| **Instrument 4.01** | Vadim Eremeev | 1994 | Covox / SD |
| **Digital Music Maker 2.0** | Lave Software | 1995 | Covox / SD |
| **Digital Studio 1.12** | Uderground Systems | 1995 | Covox / SD |
| **Global Digital Music Editor 1.0** | Global Corporation | 1996 | General Sound |
| **Riff Tracker 2.9 / 4.19** | STS / Volga Soft | 1997–1998 | Covox / SD |
| **SQ Tracker 1.0** | Sham Software | 1997 | Covox / SD |
| **Extreme's Tracker 2.10** | Alexey Porfiryev / RLDG | 1999 | Covox / SD |
| **ZX Chip 1.4** | Alone Coder | 2004 | Covox / SD |

The **Global Digital Music Editor** is the canonical tracker for the **General Sound** coprocessor card — its modules target the GS's 14 MHz Z80 rather than the main CPU. The others target the simpler Covox/SounDrive hardware-mixed DACs. See [Sound Hardware Ecosystem Overview](../hardware/sound_overview.md) for the hardware side of this split.

---

## Era 2: PC-Based AY Editors (2000–2017)

By 2000, the Soviet clone scene was in decline and the practical reality of composing on a real Spectrum had become limiting — slow input, limited memory, no undo history. Two PC-based editors emerged to replace the on-Spectrum workflow while preserving the AY module ecosystem:

### Vortex Tracker II (2000–present)

**Author:** Sergey V. Bulba. **Native format:** `.PT3` (re-exports to `.SNDH`, `.AY`, `.PSG`, `.WAV`, `.HOBETA`, `.SCL`, `.TAP`).

Vortex Tracker II (VTII) is a Windows editor that reproduces and extends the Pro Tracker 3 editing experience on PC. Its key contributions:

- **Universal import** — reads PT1, PT2, PT3, ST1, STC, ST3, STF, STP, SQT, AS0, ASC, PSC, PSM, FLS, GTR, FTC, FXM, and AY dump formats. Every major on-Spectrum tracker format is supported.
- **PT3 as native output** — VTII saves only to `.PT3`, consolidating the format-fragmented 1990s ecosystem onto one standard.
- **TurboSound support** — two modules can be edited simultaneously and synced, producing a single 6-channel TurboSound module.
- **The standard PT3 player routine** — Bulba's player is the de facto embedding routine used by virtually every game/demo that plays PT3 on real hardware.

VTII is the bridge that made the on-Spectrum module ecosystem accessible to composers who had moved to PC. It is documented in detail in [Vortex Tracker II](vortex_tracker.md).

### Arkos Tracker 1 (2003)

**Author:** Julien Nevo (Targhan, France). **Native format:** `.AKS` (source) + `.AKG` / `.AKM` / `.AKY` (player formats).

Arkos Tracker 1 took a different approach from Vortex Tracker II. Instead of extending the PT3 model, it defined an entirely new format family designed from the ground up for **embedded use in games**:

- **`.AKG`** — the high-quality player, ~600–900 bytes, full instrument fidelity.
- **`.AKM`** — the minimal player, ~400 bytes, reduced instrument features for tight space budgets.
- **`.AKY`** — a compact precompiled binary format for sound effects.

Arkos Tracker 1 did not import PT3 — it was a fresh start. Its contribution is the **game-optimized player**: smaller, faster, and with better sound effect integration than the PT3 player. Arkos-targeted music became common in Western Spectrum homebrew from 2003 onward.

---

## Era 3: Modern Cross-Platform Tools (2017–present)

The third era brought two big changes: (1) trackers became cross-platform (Windows + macOS + Linux), and (2) source code went open. The result is that ZX music composing today is no longer gated by Windows-only freeware.

### Arkos Tracker 2 (2017) and 3 (2020–present)

**Author:** Julien Nevo (Targhan). **Native format:** `.aks` (XML-like source) + `.akg` / `.aky` / `.skm` / `.skzx` players.

Arkos Tracker 2 was a complete rewrite of AT1 in C++/JUCE, making it cross-platform (Windows, macOS, Linux). Arkos Tracker 3 (2020–present) is the current actively-developed version, adding:

- **Multi-PSG support** — direct editing of TurboSound (6-channel) and even triple-AY configurations.
- **Unlimited channels** via multiple PSG instances.
- **Modern UI** — piano roll alongside the traditional tracker grid, undo/redo, full MIDI support.
- **Open source (MIT licence)** on [GitHub](https://github.com/ArkosTracker/arkestracker).

AT3 is the recommended tracker for new composers in 2025. It cannot import PT3 natively — composers migrating from the PT3 ecosystem must re-export via Vortex Tracker II tools or convert by hand.

### Vortex Tracker 3 (2024–present)

**Author:** Ben Baker (RustyPixelsUK), based on the original VT II by S.V. Bulba, Ivan Pirog, and Dexus. **Source:** [GitHub](https://github.com/RustyPixelsUK/VortexTracker3) (MIT licence).

VT3 is a C#/OpenGL/OpenAL port of VT II, fixing long-standing UI limitations of the original Windows MDI interface. It uses the same PT3 module format and the same player routine, so existing modules load without conversion. VT3 development is actively coordinated with the ZX Spectrum Next community.

### Web-Based and Minor Tools

- **WUDSN Music Editor** — Java-based, multi-format.
- Various browser-based AY experimenters — useful for quick prototyping but not for production module work.

The practical landscape in 2025: **Arkos Tracker 3 for new composers**, **Vortex Tracker II/3 for the PT3 back-catalogue**, and the original on-Spectrum trackers for historical research only.

---

## Format Lineage — How Module Formats Evolved

The module format timeline tells a story of consolidation by attrition:

| Year | Format | Origin Tracker | Fate |
|---|---|---|---|
| 1985–1989 | (proprietary) | Wham!, Music Synth 48K | Dead — no modern importer |
| 1990 | `.STC` | Sound Tracker 1.1 | Dead as output; importable by VTII |
| 1992 | `.ASC` / `.AS0` | Asc Sound Master | Importable by VTII |
| 1993 | `.SQT` | SQ-Tracker | Importable by VTII; later reused by SQ Tracker 1.0 (digital) |
| 1995 | `.PT1` / `.STP` | Pro Tracker 1.x | Superseded by PT2/PT3; VTII imports |
| 1995 | `.PT2` | Pro Tracker 2.x | Superseded by PT3; VTII imports |
| 1995 | `.PSM` | Pro Sound Maker | Importable by VTII |
| 1996 | `.PT3` | Pro Tracker 3.x | **The surviving standard.** VTII/VT3 native, thousands of modules |
| 1997 | `.FTC` | Fast Tracker | Importable by VTII |
| 1998 | `.GTR` | Global Tracker | Importable by VTII |
| 1999 | `.PSC` | Pro Sound Creator | Importable by VTII |
| 2003 | `.AKS` / `.AKG` / `.AKM` / `.AKY` | Arkos Tracker 1 | Living format, AT2/3 native |
| 2007 | `.aks` / `.akg` / `.aky` / `.skm` | Arkos Tracker 2/3 | Current — game-embedded format family |

Two formats dominate today: **PT3** (the on-Spectrum legacy, kept alive by VTII/VT3) and **`.akg`** (the modern game-embedded format, kept alive by Arkos Tracker 3). All other on-Spectrum formats are read-only — VTII imports them but writes PT3.

---

## Cross-References

- [Vortex Tracker II](vortex_tracker.md) — the dominant PC-based PT3 editor
- [Arkos Tracker](arkos_tracker.md) — modern cross-platform alternative
- [PT3 Format](pt3_format.md) — the format Pro Tracker 3 established
- [PSG Format](psg_format.md) — register dump format (alternative to module formats)
- [AY Music Formats](ay_music_formats.md) — comprehensive format catalogue
- [Sound Hardware Ecosystem Overview](../hardware/sound_overview.md) — the hardware these trackers target
- [AY-3-8912 PSG Silicon](../hardware/ay_3_8912.md) — the chip whose register map every tracker drives

## References

- [zxtunes.com software list](https://zxtunes.com/software_list.php) — authoritative catalogue of 30 Spectrum-native editors (Russian)
- [Bulba's Vortex Project](https://bulba.untergrund.net/) — Vortex Tracker II home, with the full import format list
- [Arkos Tracker 3 on GitHub](https://github.com/ArkosTracker/arkestracker) — actively maintained source
- [Vortex Tracker 3 on GitHub](https://github.com/RustyPixelsUK/VortexTracker3) — open-source VT II port
- [zxart.ee](https://zxart.ee/) — largest archive of Spectrum music, indexed by tracker format
- [zxpress.ru Deja Vu archive](https://zxpress.ru/) — historical Spectrum press, including Golden Disk Corp. announcements
