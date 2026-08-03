[← Home](../../README.md) · [Sound](../README.md) · [Trackers & Formats](README.md)

# Vortex Tracker II — The PC-Based PT3 Editor

> **Applies to**: All tracks. Vortex Tracker II (VTII) is a Windows editor for AY/YM music. It is the de facto standard for producing `.PT3` modules on the PC, and the bridge that moved the Soviet-clone on-Spectrum music ecosystem to desktop composition. Active 2000–present, written by Sergey V. Bulba.

---

## Overview

Vortex Tracker II is the editor that made it possible to compose Spectrum AY music on a PC without losing compatibility with the on-Spectrum module ecosystem. Released in 2000 by Sergey Bulba and developed continuously through 1.0 (2009) and beyond, VTII reproduces the Pro Tracker 3 editing model on Windows while adding two crucial features the on-Spectrum PT3 lacked: **universal format import** (every major 1990s AY tracker format can be loaded) and **TurboSound editing** (two AY modules edited and played in sync, producing one 6-channel TurboSound module).

VTII's role in the ecosystem is best understood as **the consolidation point**. The 1990s Soviet clone scene produced at least 15 distinct module formats (STC, STP, ASC, AS0, SQT, PSM, PSC, GTR, FTC, FXM, PT1, PT2, PT3, FLS, and several more) — each tied to its own tracker. VTII can read all of them but writes only PT3. By the late 2000s, the practical effect was that PT3 became the single interchange format for AY music on the platform, and every other format became read-only historical data.

### Naming Convention

| Term | Meaning |
|---|---|
| **VTII** | Vortex Tracker II — the standard abbreviation |
| **PT3** | Pro Tracker 3 module format — VTII's native output |
| **VTII TXT** | VTII's temporary text save format (used for work-in-progress, not for playback) |
| **Sample** | In PT3/VTII parlance, an instrument definition (envelope + volume shape) — not a PCM sample |
| **Ornament** | A PT3 arpeggio pattern — a list of pitch offsets applied to a note over time |
| **Position table** | The list of pattern numbers defining song order |
| **TS-module** | TurboSound module — two PT3 modules packed together for 6-channel playback |

---

## History and Versions

Vortex Tracker II was conceived in 2000 by Sergey Bulba as the successor to the unfinished **Vortex Tracker** — an abandoned on-Spectrum project from the late 1990s. The "II" in the name preserves this lineage. VTII was developed continuously from 2000 through the 1.0 release in 2009, with the last beta (1.0 beta 28) being the final widely-distributed version before the stable release.

### Version Timeline

| Version | Year | Milestone |
|---|---|---|
| 1.0 beta 1 | 2000 | Initial Windows release, basic PT3 editing |
| 1.0 beta 17 | 2007 | Catalogued by [zxtunes.com](https://zxtunes.com/software_list.php) as the version in widespread scene use |
| 1.0 beta 19 | 2009 | Last version supporting Windows 98; widely redistributed |
| 1.0 beta 19+ | 2009 | Community-maintained extension |
| 1.0 beta 28 | 2010s | Last version using the classic MDI interface |
| **1.0 (stable)** | 2009–present | The standard release; 32-bit and 64-bit Windows builds |

The version freeze at 1.0 is misleading: VTII has been updated incrementally since 2009, with the 1.0 label kept because Bulba considered the editor "finished" once all major planned features were implemented. The current build remains the standard PT3 editor in 2025.

### The Open-Source Continuation: Vortex Tracker 3

In 2024, Ben Baker (RustyPixelsUK) released [Vortex Tracker 3](https://github.com/RustyPixelsUK/VortexTracker3), a C#/OpenGL/OpenAL port of VTII licensed under MIT. VT3 preserves the PT3 module format and the player routine exactly, so existing modules load without conversion. The port's primary contribution is a modern UI: the original VTII used Windows' Multiple Document Interface (MDI), which is awkward on modern high-DPI displays.

---

## Interface and Editing Model

VTII inherits the Pro Tracker 3 editing model: a multi-window interface with each major concept in its own window. The MDI shell lets all windows be tiled, cascaded, or maximized independently.

### Main Windows

| Window | Purpose |
|---|---|
| **Pattern Editor** | The note grid — 3 or 6 channels (TS-mode), columns for note, sample/instrument number, ornament, volume, and effect |
| **Position Table** | The song sequence — a list of pattern numbers (e.g. `0,0,1,1,2,3,2,3`), defining which pattern plays at each song position |
| **Sample Editor** | Instrument definitions — each "sample" is a list of (volume, envelope-flag, noise-flag, tone-flag) tuples stepped through at the AY's envelope frequency |
| **Ornament Editor** | Arpeggio patterns — lists of signed pitch offsets cycled per tick, used for chord arpeggios and vibrato effects |
| **Frequency Table Selector** | Chooses the tuning table (ZX 1.7734 MHz, ZX 1.75 MHz, Atari ST 2 MHz, YM custom, etc.) |
| **Module Properties** | Title, author, song speed (ticks per row), and other globals |

The composer works by switching between windows: define samples and ornaments first, then enter notes into patterns, then arrange patterns into a song via the position table. This pattern→position separation allows reusing a single pattern (e.g. a drum loop) at multiple points in the song without duplicating data.

---

## Format Import and Export — The Universal Translator

VTII's defining feature is its import breadth. No other AY tool reads as many historical formats.

### Import (Read)

| Format Family | Extensions | Origin Tracker |
|---|---|---|
| **Pro Tracker** | `.PT1`, `.PT2`, `.PT3` | Golden Disk Corp. Pro Tracker 1.x/2.x/3.x |
| **Sound Tracker** | `.STC`, `.ST1`, `.ST3`, `.STF`, `.STP` | Bzyk's Sound Tracker 1.1, KSA's Sound Tracker Pro |
| **SQ-Tracker** | `.SQT` | George K. SQ-Tracker (1993) |
| **ASC Sound Master** | `.ASC`, `.AS0` | Andrew Sendetskiy (1992) |
| **Pro Sound Maker/Creator** | `.PSM`, `.PSC` | Team V (1995), E-mage Group (1999) |
| **Fast Tracker** | `.FTC` | Digital Reality (1997) |
| **Global Tracker** | `.GTR` | Global Corp. (1998) |
| **Fast Tracker Extended** | `.FXM` | Variant of FTC |
| **Flash Tracker** | `.FLS` | Late-1990s Soviet tracker |
| **AY dump (ZXAYEMUL)** | `.AY` | AY-emulator project snapshot format |
| **AY dump (ZXAYST11)** | `.AY` | Earlier AY dump variant |
| **PT 3.6/3.7 TurboSound** | (PT3 with TS extension) | Pro Tracker TurboSound modules |

On import, VTII normalizes the module to its internal PT3 representation, losing any format-specific quirks but preserving the audible music. Some very obscure formats (Cacofony, Super Sonic) are not directly importable and require conversion via third-party tools.

### Export (Write)

| Format | Use |
|---|---|
| **`.PT3`** | Native — the canonical output, embeddable in any ZX game/demo with Bulba's player |
| **`.PT3 + TS-player`** | TurboSound — two modules packed together for 6-channel clones |
| **VTII TXT** | Temporary work-in-progress text format (NOT for playback) |
| **`.HOBETA` (with player)** |ZX Spectrum executable — drop-in `.B` / `.C` file that runs and plays the song on real hardware |
| **`.HOBETA` (data only)** | HOBETA file containing just the module data |
| **`.SCL`** | TR-DOS disk image containing the module |
| **`.TAP`** | Spectrum tape image — loadable from real tape or emulator |
| **`.AY`** | AY-emulator snapshot — playable by AY-emulator, ayfly, and many ZEsarUX configurations |
| **`.PSG`** | Register dump — playable by PSG players, useful for non-ZX AY hosts |
| **`.WAV`** | Rendered audio — for distribution to non-Spectrum audiences |
| **`.SNDH`** | Atari ST SNDH format — for cross-platform AY/YM music archives |

The HOBETA-with-player export is particularly useful: it produces a single file that boots on a real Spectrum (or any emulator) and plays the song, no other software required. This is how most PT3 modules are distributed for on-hardware listening.

---

## Samples and Ornaments — How AY Timbres Are Defined

The AY-3-8912 has no built-in instrument memory — every "instrument" in a piece of AY music is a software construction built from the chip's register primitives. VTII exposes this construction through two parallel editors.

### Samples (Instruments)

A VTII **sample** is a list of steps, each step containing:

- **Volume** (0–15) — the AY channel volume for that step
- **Envelope flag** — if set, the volume is replaced by the AY hardware envelope generator output
- **Noise flag** — if set, the channel's noise generator is enabled
- **Tone flag** — if set, the channel's tone generator is enabled (off for pure noise/percussion)
- **Envelope frequency** — when envelope flag is set, the period of the hardware envelope

The sample is stepped through at the song's tick rate (typically 50 Hz), producing a time-varying timbre. A violin-like sustain might be a 1-step sample with envelope flag set; a plucked string might be a 32-step sample with volume decaying from 15 to 0. Drums are typically short samples with tone off and noise on.

### Ornaments (Arpeggios)

A VTII **ornament** is a list of signed pitch offsets, cycled per tick. Each note in the pattern editor can be paired with an ornament, allowing:

- **Chord arpeggios** — cycle through `[0, +4, +7]` (major) or `[0, +3, +7]` (minor) to fake polyphony on a single channel
- **Vibrato** — small repeating offsets like `[0, +1, +2, +1, 0, -1, -2, -1]`
- **Slide effects** — long ascending or descending offset sequences

Ornaments are what allow 3-channel AY music to sound fuller than 3-voice polyphony would suggest — a single channel with an arpeggio ornament effectively plays a chord.

### Frequency Tables

VTII lets the composer choose the **frequency table** — the lookup that maps note names (C-4, D-4, etc.) to AY tone period values. The table must match the target hardware's clock:

| Table | Clock | Target Hardware |
|---|---|---|
| **ZX (1.7734 MHz)** | Standard ZX AY clock | Original 128K / +2 / +2A / +3, most Soviet clones |
| **ZX (1.75 MHz)** | Common approximation | Some Soviet clones, certain emulators |
| **Atari ST (2 MHz)** | Atari ST's YM2149 | Cross-platform music for Atari ST |
| **Custom** | User-defined | Exotic hardware, modern FPGA cores |

Choosing the wrong table makes every note play at the wrong pitch — a common mistake when playing modules authored for one machine on another. See [AY-3-8912 PSG Silicon](../hardware/ay_3_8912.md) for the clock-derivation details.

---

## TurboSound Editing — Two Modules in Sync

VTII supports TurboSound (TS) editing: two PT3 modules are opened in two VTII instances and played in tight synchronization, then exported as a single TS-module for 6-channel clones (Pentagon, Scorpion GMX, ATM Turbo, etc.). The mechanism is described in detail in [TurboSound](../hardware/turbosound.md); the editing-side considerations are:

- **Two VTII windows** — both run simultaneously, sharing transport controls (start/stop/tempo) when TS-sync is enabled.
- **Pattern-level sync** — patterns in module A and module B with matching indices play together. The composer must align the pattern boundaries.
- **Saving a TS-module** — VTII packs both PT3 modules plus the TS-player routine into a single file, loadable on TS-equipped hardware.
- **PT 3.6 / 3.7 import** — VTII can import TurboSound modules created by the rare on-Spectrum Pro Tracker 3.6/3.7 revisions.

TS-editing is not multi-tracking in the DAW sense — it is two parallel 3-channel songs, not one 6-channel song. The composer treats them as left/right or foreground/background rather than as 6 independent voices.

---

## Player Integration — Embedding PT3 in a Game or Demo

VTII's export pipeline produces files ready for embedding, but the embedding itself is the developer's job. The standard workflow:

1. Compose and edit the music in VTII; export as `.PT3`.
2. Include the PT3 module as binary data in the game/demo's resource file.
3. Include the **PT3 player routine** (Bulba's standard, ~600–900 bytes) as Z80 code.
4. From the game's main loop or vertical-blank interrupt, call the player once per frame.

The player routine reads the module and writes 14 bytes to AY registers `#0`–`#13` via the standard `#FFFD` (register index) and `#BFFD` (register data) ports. The exact integration pattern is documented in [AY Player Routines](../players/ay_player_routines.md).

### The Player Routine Options

Several PT3 player routines exist, each with different trade-offs:

| Routine | Author | Size | Speed | Notes |
|---|---|---|---|---|
| **PT3P (standard)** | S.V. Bulba | ~700 bytes | Baseline | The reference implementation shipped with VTII |
| **RSM PT3 player** | Lion / RSM | ~600 bytes | Faster | Optimized for speed, slight reorder of register writes |
| **Ayalong's PT3 player** | Ayalong | ~550 bytes | Faster still | Aggressively optimized; some compatibility trade-offs |
| **PT3P (Y Patreon)** | Various | Varies | Various | Modern forks with bug fixes |

The choice rarely matters for new compositions — Bulba's standard player is fine. It matters when CPU budget is extremely tight (e.g. inside a 1K intro) and every T-state counts. See [Player Comparison](../players/player_comparison.md) for the full benchmark table.

---

## Pitfalls and Best Practices

### Pitfall 1: Wrong Frequency Table for the Target Hardware

A module composed with the ZX 1.7734 MHz table will play out of tune on hardware running at a different AY clock. Soviet clones are mostly fine (same clock), but Atari ST YM2149 modules and some FPGA cores use different clocks. **Fix:** verify the target hardware clock before exporting, and set the Frequency Table selector accordingly.

### Pitfall 2: Forgetting that "Sample" ≠ PCM Sample

VTII's "samples" are instrument definitions (envelope + volume + noise/tone flags), not PCM data. A composer expecting to import a `.wav` drum sample will be confused — there is no sample-import feature. **Fix:** for PCM drums, use a Covox/GS-targeted tracker (see [Tracker History](tracker_history.md#digital-trackers-19942004-covox--general-sound)).

### Pitfall 3: Module Too Long for Target Memory

A long PT3 module with many patterns and ornaments can exceed a 48K Spectrum's available RAM. **Fix:** keep the module under ~16 KB for 48K targets, or use 128K paging for larger modules. VTII shows the module size in the status bar.

### Pitfall 4: TS-Module Played on Non-TS Hardware

A TurboSound module played on a single-AY machine will play only one of the two embedded modules (typically the first), silently losing the other. **Fix:** always include a single-AY fallback module when targeting mixed hardware.

### Best Practices

- **Compose in `.PT3`** — it's the universal interchange format and survives the longest.
- **Use Bulba's standard player** unless CPU budget forces optimization.
- **Set the correct frequency table** before exporting — the table is part of the module, not the player.
- **Test on real hardware** (or an accurate emulator like ZEsarUX) before publishing. The VTII preview uses Bulba's AY emulation, which is excellent but not bit-exact.
- **Save often in VTII TXT format** — it preserves ornaments/samples even when not used in any pattern, allowing later experimentation.

---

## Cross-References

- [Tracker History](tracker_history.md) — the full lineage, including PT3's place in it
- [Arkos Tracker](arkos_tracker.md) — modern alternative, different format family
- [PT3 Format](pt3_format.md) — the binary format specification
- [AY Music Formats](ay_music_formats.md) — all ZX music formats cataloged
- [TurboSound](../hardware/turbosound.md) — the hardware TS-module editing produces
- [AY-3-8912 PSG Silicon](../hardware/ay_3_8912.md) — the chip the player routine drives
- [AY Player Routines](../players/ay_player_routines.md) — embedding PT3 in a game

## References

- [Bulba's Vortex Project](https://bulba.untergrund.net/vortex_e.htm) — official VTII home
- [Vortex Tracker 3 on GitHub](https://github.com/RustyPixelsUK/VortexTracker3) — open-source continuation
- [VTII source code](https://bulba.untergrund.net/programmer_e.htm) — Bulba's release of the VTII source
- [zxtunes.com](https://zxtunes.com/) — largest archive of VTII-produced music
- [zxart.ee](https://zxart.ee/) — second-largest archive, indexed by tracker format
- [VTII tutorial by chechu_rolemusic (YouTube)](https://www.youtube.com/watch?v=6ZYjzqUOnpM) — practical walkthrough
