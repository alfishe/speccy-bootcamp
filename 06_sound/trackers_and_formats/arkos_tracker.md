[← Home](../../README.md) · [Sound](../README.md) · [Trackers & Formats](README.md)

# Arkos Tracker 2/3 — The Modern Cross-Platform Alternative

> **Applies to**: All tracks. Arkos Tracker (AT) is a cross-platform AY/YM music editor by Julien Nevo (Targhan, France). It is the recommended tracker for new ZX Spectrum composers in 2025. Active 2003–present, open source under MIT since AT2.

---

## Overview

Arkos Tracker is the alternative lineage to the Pro Tracker / Vortex Tracker II family. Where VTII preserves and consolidates the 1990s Soviet-clone format ecosystem, Arkos started fresh in 2003 with a format designed for **embedded use in games** — small player routines, fast execution, native sound-effect support, and multi-platform export. The current version (AT3, actively developed 2020–present) is a C++/JUCE application running on Windows, macOS, and Linux.

The key trade-off versus VTII: Arkos cannot import or export PT3. A composer with an existing PT3 catalogue must either stay in VTII or convert modules manually. The payoff for new music is a more capable editor and a family of player routines (AKG, AKM, AKY, MOD) optimized for different use cases — game soundtracks, size-limited demos, multi-PSG music, even sample playback.

### Naming Convention

| Term | Meaning |
|---|---|
| **AT1 / AT2 / AT3** | Arkos Tracker versions 1 (2003), 2 (2017), 3 (2020–present) |
| **AKG** | "Arkos Tracker Game" — the general-purpose player, balanced speed/size |
| **AKM** | "Arkos Tracker Minimal" — memory-optimized player for size-limited demos |
| **AKY** | "Arkos Tracker Y" — fast player for demos, supports digidrums and samples |
| **FAP** | Fast And Powerful player — CPC only, NOT available for ZX |
| **SE** | Sound Effect player — for SFX-only projects |
| **MOD** | Full-sample player — 100% PCM, no PSG synthesis |
| **Targhan** | Julien Nevo's scene handle — author of all Arkos Tracker versions |
| **.aks** | Arkos Tracker 2/3 native source format (XML-like) |

---

## History and Versions

Arkos Tracker has been developed continuously by Julien Nevo (Targhan) since 2003. The version history tracks three major architecture eras.

### Arkos Tracker 1 (2003–2017, Delphi/Windows)

The original version, written in Delphi and Windows-only. Native format: `.AKS` (binary). Player formats: AKG, AKM, AKY. AT1 was the first major AY tracker not descended from the Sound Tracker lineage — it defined its own module format and its own player routine family. AT1 had no PT3 import.

### Arkos Tracker 2 (2017–2020, C++/JUCE)

A complete rewrite in C++ using the [JUCE](https://juce.com/) framework, making AT cross-platform (Windows, macOS, Linux). Native format: `.aks` (XML-like, distinct from AT1's binary `.AKS`). AT2 added modern UI conventions (multiple panels, undo/redo, full MIDI input), VST plugin support for export, and the first official TurboSound editing in the Arkos lineage.

### Arkos Tracker 3 (2020–present, C++/JUCE, open source)

The current version, actively developed on [GitHub](https://github.com/ArkosTracker/arkestracker) under the MIT licence. Major additions over AT2:

- **Multi-PSG composition** — songs can target 1, 2, 3, or more PSG chips simultaneously, with each PSG's clock independently configurable. This is true 6/9/12-channel editing, not the two-parallel-modules approach of VTII.
- **Sample (digidrum) support** — digidrum samples can be embedded in the song and triggered via the AKY player.
- **Modern player formats** — AKY (fast, digidrum-capable), FAP (CPC-only, but AT3 generates it for cross-platform composers), MOD (full-sample songs).
- **Piano-roll editor** alongside the traditional tracker grid.
- **Cross-platform builds** — official Windows, macOS, Linux binaries released in sync.

### Future Directions

AT3's roadmap (per [Julien Nevo's site](https://www.julien-nevo.com/arkostracker/)) includes additional player ports (Amstrad Plus, Atari ST), improved sample support, and tighter integration with hardware targets like the ZX Spectrum Next's TBBlue registers.

---

## Player Formats — Which One to Use

The Arkos ecosystem produces several player routines, each optimized for a different use case. AT3 generates the player source code (Z80 assembly) directly from the editor; the composer embeds it alongside the binary song data in their game or demo.

### Player Decision Matrix

| Player | Use Case | ZX Available? | Size | Speed |
|---|---|---|---|---|
| **AKG** | Game soundtracks — general purpose, balanced | ✅ | Medium (~600–900 bytes) | Baseline |
| **AKM** | Size-limited demos (1K/4K intros) | ✅ | Small (~400 bytes) | Baseline |
| **AKY** | Demos — fast, digidrum-capable, multi-PSG | ✅ | Larger | Fast |
| **FAP** | CPC demos — fastest with great compression | ❌ CPC only | — | — |
| **SE** | Sound effects only — no music | ✅ | Small | Fast |
| **MOD** | 100% sample songs — no PSG synthesis | ✅ | Depends on samples | Depends |

### Decision Guide (per Targhan's official recommendations)

- **Working on a game?** → AKG (or AKM if size is very tight).
- **Working on a demo?** → AKY (multi-platform) — FAP is CPC-only, so ZX composers use AKY instead.
- **Size-limited demo (1K/4K)?** → AKM.
- **Need more than 3 channels?** → AKY (multi-PSG support).
- **Need digidrums (sample drums alongside PSG music)?** → AKY.
- **Need pitched samples alongside PSG?** → AKY.
- **Full-sample song, no PSG?** → MOD.
- **Only sound effects, no music?** → SE.

### RAM vs ROM Players

Each Arkos player comes in two variants:

- **RAM player** — uses self-modifying code as an optimization. Smaller and faster, but only works when the player+song is in writable RAM.
- **ROM player** — uses a small buffer instead of self-modification, allowing the player to live in ROM. Slightly larger and slower, but required for cartridge-based distributions.

The ZX Spectrum itself runs from RAM (the ROM is the BASIC interpreter), so most ZX projects use RAM players. ROM players matter for cartridge-based systems (MSX, C64 cartridge) or for Spectrum +3 software distributed on ROM.

### Platform Interoperability

Arkos songs target a specific PSG clock (ZX 1.7734 MHz, CPC 1 MHz, MSX 1.789 MHz, Atari ST 2 MHz). When moving a song between platforms:

- **AKY songs encode absolute periods**, so the song sounds different on a different PSG clock. Re-export targeting the new platform.
- **AKG and AKM songs encode notes**, not periods, so the song is theoretically portable. However, pitch effects (slides) are period-based and will sound wrong. Manually verify.

The practical rule: **always re-export for each target platform** and listen on real hardware or an accurate emulator.

---

## Multi-PSG Composition

AT3's headline feature is true multi-PSG editing. Where VTII's TurboSound mode runs two parallel 3-channel songs, AT3 treats all PSG voices as a single unified song:

- **Per-PSG clock configuration** — each PSG can have its own clock, allowing hybrid songs (e.g. one ZX AY at 1.7734 MHz + one Atari ST YM at 2 MHz).
- **Per-PSG channel count** — most songs use 3 channels per PSG, but the model allows arbitrary configurations.
- **Channel-spanning effects** — a single instrument or arpeggio can target voices across multiple PSGs.
- **Single song file** — the multi-PSG arrangement is one `.aks` file, not two synchronized files as in VTII.

For ZX-specific TurboSound (2× AY at the same clock), AT3 exports a single song that drives both AYs via the standard `#FFFD`/`#BFFD` ports plus the `#FF` bank-select port. See [TurboSound](../hardware/turbosound.md) for the hardware side.

### Multi-PSG Player Outputs

| Configuration | Total Voices | Player |
|---|---|---|
| 1 PSG (3 voices) | 3 | AKG / AKM / AKY |
| 2 PSG TurboSound (6 voices) | 6 | AKY (recommended) |
| 3 PSG TurboSound Next (9 voices) | 9 | AKY |
| Custom (e.g. 1 ZX + 1 Atari ST) | varies | AKY |

---

## Comparison with Vortex Tracker II

Arkos and VTII serve overlapping but distinct needs. The choice is rarely "which is better" — it's "which fits the project."

| Criterion | Vortex Tracker II | Arkos Tracker 3 |
|---|---|---|
| **Native format** | PT3 (binary) | .aks (XML) |
| **PT3 import** | ✅ Native | ❌ |
| **PT3 export** | ✅ Native | ❌ |
| **AKG/AKM/AKY export** | ❌ | ✅ Native |
| **TurboSound editing** | Two parallel modules | Single unified song |
| **Multi-PSG (>2)** | ❌ Max 2 PSGs | ✅ Unlimited |
| **Cross-platform** | ❌ Windows only (VT3 port exists separately) | ✅ Windows/macOS/Linux |
| **Open source** | ❌ (VTII proper; VT3 is open) | ✅ MIT licence |
| **Digidrum / sample support** | ❌ PSG only | ✅ AKY + MOD |
| **Sound effects support** | Limited | ✅ SE player |
| **Piano roll** | ❌ | ✅ |
| **Active development** | Maintenance only | ✅ Actively developed |
| **Universal import** | ✅ 15+ legacy formats | ❌ .aks only |

### When to Use Which

**Use VTII when:**
- You have an existing PT3 catalogue to maintain.
- You need to import 1990s tracker formats (STC, STP, ASC, SQT, etc.).
- You are working with Soviet-clone-scene musicians who use PT3.
- You only need 3 or 6 (TurboSound) channels.

**Use Arkos Tracker 3 when:**
- You are starting new music with no PT3 legacy.
- You need multi-PSG (>2 chips) or digidrum samples.
- You need sound-effect integration alongside music.
- You are on macOS or Linux.
- You want modern UI (piano roll, undo/redo).
- You need very small or very fast player routines (AKM, AKY).

---

## Pitfalls and Best Practices

### Pitfall 1: Choosing FAP for a ZX Project

The FAP player is the most attractive on paper (fastest, best compression) but is **CPC-only**. ZX composers who select FAP will produce code that cannot be assembled for the ZX target. **Fix:** use AKY for ZX demos instead.

### Pitfall 2: Assuming AKG Songs Are Portable Across PSG Clocks

While AKG encodes notes (not periods), pitch effects like slides encode period values. A slide composed for a ZX PSG will sound wrong on a CPC or Atari ST PSG. **Fix:** re-export for each target and verify by ear.

### Pitfall 3: Forgetting to Specify the Target PSG Clock

AT3 supports arbitrary PSG clocks, but the default may not match the ZX. A song composed without verifying the PSG clock will play out of tune on real hardware. **Fix:** in Song Properties, set the PSG frequency to **1.7734 MHz** for ZX targets (or 1.75 MHz if targeting specific Soviet clones).

### Pitfall 4: Expecting PT3 Compatibility

AT3 cannot read or write PT3. Composers migrating from VTII must either stay in VTII for legacy modules or rewrite the music in AT3 from scratch. **Fix:** for legacy PT3 maintenance, keep VTII installed; for new music, use AT3.

### Best Practices

- **Set the PSG clock before composing** — ZX 1.7734 MHz is the default for ZX targets.
- **Use AKG by default** — switch to AKM only for size-limited intros, AKY only for demos requiring digidrums or multi-PSG.
- **Generate the player source from the latest AT3 build** — bug fixes and optimizations are released frequently.
- **Test on real hardware or ZEsarUX** — AT3's preview uses internal AY emulation which is excellent but not bit-exact.
- **Commit the `.aks` source to version control** — it's XML-like, diffs cleanly, and is the canonical source for all player exports.

---

## Cross-References

- [Tracker History](tracker_history.md) — the full lineage, including AT's place in it
- [Vortex Tracker II](vortex_tracker.md) — the alternative ecosystem (PT3 lineage)
- [AY Music Formats](ay_music_formats.md) — comprehensive format catalogue
- [Player Comparison](../players/player_comparison.md) — Arkos players vs PT3 player benchmarks
- [AY Player Routines](../players/ay_player_routines.md) — embedding Arkos players in a game
- [TurboSound](../hardware/turbosound.md) — the multi-PSG hardware AT3 targets
- [ZX Spectrum Next Audio](../hardware/zx_next_audio.md) — 3-PSG target for AT3
- [AY-3-8912 PSG Silicon](../hardware/ay_3_8912.md) — the chip family all Arkos players drive

## References

- [Arkos Tracker official site](https://www.julien-nevo.com/arkostracker/) — Targhan's home page
- [Arkos Tracker 3 on GitHub](https://github.com/ArkosTracker/arkestracker) — source code and issue tracker
- [Players Overview](https://www.julien-nevo.com/arkostracker/index.php/players-overview/) — official player decision guide
- [Arkos Tracker 2 ST (Atari ST port by ggnkua)](https://github.com/ggnkua/Arkos-Tracker-2-ST) — community port for Atari ST workflow
- [ym2149_arkos_replayer (Rust crate)](https://docs.rs/ym2149-arkos-replayer) — programmatic song playback for tooling
