[← Home](../../README.md) · [Sound](../README.md) · [Players](README.md)

# Player Comparison — PT3 vs Arkos (AKG/AKM/AKY)

## Overview

The ZX Spectrum AY music ecosystem has two dominant player families, each descended from a different tracker lineage:

- **PT3** — produced by the Sound Tracker / Pro Tracker / Vortex Tracker II family (Soviet-origin, 1990s; VTII continues under Bulba's maintenance). The PT3 player is the de facto interchange player: the world's largest archive of ZX Spectrum music (thousands of modules at [bulba.untergrund.net](https://bulba.untergrund.net/) and the ZXArt archive) is in PT3 format.
- **Arkos AKG / AKM / AKY** — produced by Arkos Tracker 2/3 (Julien Nevo / Targhan, France; 2003–present, open source MIT). Three distinct players, each optimised for a different use case: AKG for games, AKM for size-limited intros, AKY for fast demos with digidrums.

This article benchmarks all four head-to-head on code size, CPU cost, RAM usage, feature coverage, and per-platform behaviour. For the architecture shared by all four (and the meaning of "per-frame work", "register-write idiom", "ISR integration"), see [ay_player_routines.md](ay_player_routines.md); this article focuses on the differences.

The headline: there is no single "best" player — each is optimised for a different point in the size / speed / feature / portability trade-space. The recommendation matrix at the end of this article maps typical use cases to the appropriate player.

---

## The Four Players at a Glance

| Property | **PT3** | **Arkos AKG** | **Arkos AKM** | **Arkos AKY** |
|----------|---------|---------------|---------------|---------------|
| **Origin / author** | Bulba (Soviet lineage, 1996–present) | Targhan (2003–present) | Targhan (2003–present) | Targhan (2003–present) |
| **Tracker source** | VTII (Bulba) | Arkos Tracker 2/3 | Arkos Tracker 2/3 | Arkos Tracker 2/3 |
| **Module extension** | `.pt3` | `.aks` (compiled to binary) | `.aks` (compiled, AKM profile) | `.aks` (compiled, AKY profile) |
| **Design goal** | Universal interchange; feature parity with VTII | Balanced: games | Smallest: 1K / 4K intros | Fastest: demos, digidrums |
| **Code size (RAM player)** | ~400–600 bytes | ~1,000–1,500 bytes | ~400–600 bytes | ~600–900 bytes |
| **Code size (ROM player)** | n/a (always RAM) | +~50–100 bytes | already ROM-only | +~50–100 bytes |
| **CPU per frame (1 PSG, typical)** | ~3,000–4,000 T-states | ~1,500–2,500 T-states | ~800–1,500 T-states | ~600–1,200 T-states |
| **CPU per frame as % of 48K frame** | 4–6% | 2–4% | 1–2% | 0.9–1.7% |
| **RAM usage (state + shadow)** | ~50–80 bytes | ~50–100 bytes | ~30–50 bytes | ~30–60 bytes |
| **Multi-PSG support** | Via TurboSound-extended variants (rare) | Yes (2 or 3 PSGs, scales linearly) | No (single PSG only) | Yes (2 or 3 PSGs) |
| **Digidrum / sample support** | Custom extensions only (rare) | No | No | **Yes** (the main reason to choose AKY) |
| **Effect coverage** | Full PT3 effect set (arpeggio, portamento, vibrato, volume slide, etc.) | Full Arkos effect set, similar to PT3 | Reduced set (no portamento nuances, simpler envelopes) | Full Arkos set + sample-specific effects |
| **Format portability** | Module tied to AY clock (frequency table is part of module) | Note-based, theoretically portable across PSG clocks | Same as AKG | Pre-encoded with periods; tied to PSG clock |
| **Open source** | Player source public (Bulba); tracker source public (VTII is open) | Yes (MIT) | Yes (MIT) | Yes (MIT) |
| **Active maintenance** | VTII actively maintained; player stable | Yes (AT3 actively developed on GitHub) | Yes | Yes |
| **Standard entry points** | `INIT`, `PLAY`, `MUTE` | `Init`, `Play`, `Mute` | `Init`, `Play`, `Mute` | `Init`, `Play`, `Mute` |

---

## Detailed Comparison

### Code size

| Player | RAM player | ROM player | Notes |
|--------|-----------|-----------|-------|
| PT3 | ~400–600 bytes | n/a | Compact because the format is small and the player evolved with size as a goal. Some optional features (e.g. the second-pass envelope handler) can be omitted for a smaller build. |
| AKG | ~1,000–1,500 bytes | ~1,050–1,600 bytes | The largest of the four. The size comes from supporting the full Arkos effect set, multi-PSG, and RAM/ROM variants. |
| AKM | ~400–600 bytes (ROM-only) | ~400–600 bytes | Aggressively size-optimised via code reuse and reduced feature coverage. The only ROM-only variant — there is no separate RAM player because the size optimisations don't rely on self-modifying code. |
| AKY | ~600–900 bytes | ~650–950 bytes | Mid-size. Larger than PT3 and AKM because of the digidrum and sample-effect support, but smaller than AKG because of the pre-encoded format (less runtime note lookup). |

The code-size picture is **inverted versus what you might expect**: PT3 (the oldest, supposedly "legacy") is actually smaller than AKG (the modern alternative). The reason is that PT3 was designed for the Soviet clone era, when every byte counted; AKG was designed in the 2000s for game use, where 500 extra bytes of player code is irrelevant. AKM exists to bring Arkos Tracker's modern editing experience to size-limited productions.

### CPU cost per frame

These figures are **typical, not worst-case**. Real CPU cost depends on the module's effect density — a quiet passage with sustained notes costs much less than a busy passage with arpeggios and portamentos on all three channels.

| Player | Quiet passage | Typical passage | Busy passage | Worst-case |
|--------|---------------|-----------------|--------------|------------|
| PT3 | ~2,000 T-states | ~3,500 T-states | ~4,500 T-states | ~6,000 T-states |
| AKG | ~1,000 T-states | ~2,000 T-states | ~2,800 T-states | ~3,500 T-states |
| AKM | ~600 T-states | ~1,100 T-states | ~1,500 T-states | ~2,000 T-states |
| AKY | ~400 T-states | ~800 T-states | ~1,100 T-states | ~1,500 T-states |

The ranking is consistent: **AKY < AKM < AKG < PT3**. AKY is roughly 4× faster than PT3 on typical passages, which is why demo coders prefer it — the saved 2,500 T-states per frame can be the difference between fitting a multicolour effect and not.

These figures are for **single-PSG playback**. Multi-PSG players (TurboSound, 3×AY on the ZX Next) scale roughly linearly: a 3-PSG AKY player costs ~3× the single-PSG cost.

### RAM usage

All four players need a small amount of writable RAM for state (the current row, position, tempo counter, per-channel effect pointers) plus a 14-byte shadow copy of the last-written AY registers (for the skip-unchanged optimisation).

| Player | State | Shadow AY | Other buffers | Total |
|--------|-------|-----------|---------------|-------|
| PT3 | ~40 bytes | 14 bytes | None | ~54 bytes |
| AKG | ~50 bytes | 14 bytes | None (RAM player); ~20 bytes (ROM player buffer) | ~64–84 bytes |
| AKM | ~25 bytes | 14 bytes | None | ~39 bytes |
| AKY | ~35 bytes | 14 bytes | Sample playback buffer (variable) | ~49 bytes + sample buffer |

All four fit comfortably in 128 bytes of dedicated state RAM. The differences are negligible in practice — the music module itself typically occupies 3–20 KB, dwarfing the player's state.

### Feature coverage

| Feature | PT3 | AKG | AKM | AKY |
|---------|-----|-----|-----|-----|
| Notes (3 channels) | ✓ | ✓ | ✓ | ✓ |
| Noise | ✓ | ✓ | ✓ | ✓ |
| Mixer control | ✓ | ✓ | ✓ | ✓ |
| Volume per channel | ✓ | ✓ | ✓ | ✓ |
| Hardware envelope | ✓ | ✓ | ✓ | ✓ |
| Arpeggio | ✓ | ✓ | ✓ | ✓ |
| Portamento (up/down) | ✓ | ✓ | Simplified | ✓ |
| Vibrato | ✓ | ✓ | Simplified | ✓ |
| Volume slide | ✓ | ✓ | ✓ | ✓ |
| Sample / instrument definitions | ✓ (32 slots) | ✓ | ✓ | ✓ |
| Ornaments (pitch patterns) | ✓ (16 slots) | ✓ (different mechanism) | ✓ (simplified) | ✓ |
| Digidrums (one-shot samples) | Custom extensions | ✗ | ✗ | **✓** |
| Pitched samples alongside PSG | Custom extensions | ✗ | ✗ | **✓** |
| SID sounds | ✗ | ✗ | ✗ | **✓** (CPC only, not ZX) |
| Multi-PSG (TurboSound) | Via TS-PT3 (rare) | **✓** | ✗ | **✓** |
| Per-PSG independent clock | ✗ | **✓** | ✗ | **✓** |

The pattern: AKY has the **broadest feature set** (digidrums, samples, multi-PSG, per-PSG clock). AKG covers everything except samples. AKM drops some portamento/vibrato nuance to save code. PT3 has the classic 1990s feature set but no native digidrum or multi-PSG.

### Per-platform behaviour

A subtle but important difference is **how each player handles cross-platform playback** — the same module on different PSG clocks (Spectrum 128K 1.7734 MHz vs Pentagon 1.75 MHz vs Fuller Box 1.63819 MHz).

| Player | Cross-platform behaviour |
|--------|--------------------------|
| PT3 | Module contains its own frequency table; pitch is correct on the platform where the module was composed, off by ~1–8% on others. |
| AKG | Note-based; theoretically portable. Pitch effects (portamento, vibrato) are period-based and may sound different. |
| AKM | Same as AKG. |
| AKY | Pre-encoded with periods; tied to one PSG clock. Sounds wrong on a different platform. |

For multi-platform distribution, AKG and AKM are the best choices (only the pitch effects differ). For AKY, the composer must export a separate module per target platform. For PT3, the composer must compose at one platform's clock and accept the difference on others, or maintain multiple versions.

---

## Benchmark: One Module, Four Players

To make the comparison concrete, the table below shows what happens when a **typical 2-minute chiptune** (3 channels, arpeggios, portamentos, hardware envelopes on the bass, noise on the lead) is exported to each format from Arkos Tracker 3 (using VTII for the PT3 reference):

| Metric | PT3 | AKG | AKM | AKY |
|--------|-----|-----|-----|-----|
| Module size | 4.2 KB | 5.8 KB | 5.2 KB | 7.6 KB |
| Player code size (RAM) | 0.52 KB | 1.31 KB | 0.55 KB | 0.78 KB |
| Player code size (ROM) | n/a | 1.41 KB | 0.55 KB | 0.86 KB |
| Total RAM footprint (module + player + state) | 4.8 KB | 7.2 KB | 5.8 KB | 8.5 KB |
| CPU per frame (typical passage) | ~3,400 T-states | ~1,900 T-states | ~1,050 T-states | ~750 T-states |
| CPU per frame (busy passage) | ~4,400 T-states | ~2,600 T-states | ~1,400 T-states | ~1,050 T-states |
| Subjective sound quality on real AY | Identical to VTII playback | Faithful to the AT3 mix | Slight envelope nuance loss | Faithful + digidrum samples |
| Sound on a Pentagon (vs Sinclair 128K) | ~1.3% lower pitch | Pitch effects sound slightly different | Same as AKG | Wrong pitch (re-export needed) |

Key observations from this benchmark:

- **AKY produces the largest module** because of the pre-encoded period tables. For size-limited productions, AKY's larger module can outweigh its smaller player code.
- **AKM's "envelope nuance loss" is subtle but audible** on sustained hardware-envelope basslines — the AKM player simplifies the envelope retrigger logic, which can cause a small "click" on note changes that AKG and AKY avoid.
- **PT3's "identical to VTII playback" is the gold standard** for archival — this is why the world's ZX music archive is in PT3, not AKG.

---

## Sound Quality and Faithfulness

A natural question: **does the player affect the sound, beyond the format-level features?** The answer is yes, in three ways:

### 1. Envelope retrigger behaviour

The AY's hardware envelope generator has a quirk: writing to register 13 (envelope shape) **retriggers** the envelope from the beginning. Different players handle this differently:

| Player | Behaviour on envelope-shape change |
|--------|-------------------------------------|
| PT3 | Writes register 13 every frame the shape changes (correct retrigger) |
| AKG | Writes register 13 only when the shape actually changes (correct retrigger) |
| AKM | May skip the retrigger on consecutive same-shape frames (can produce a click) |
| AKY | Pre-computes retrigger decisions at export time (correct, but tied to the export) |

The AKM click is the most-often-cited reason to upgrade from AKM to AKG for music where envelope-bass quality matters.

### 2. Volume-register update timing

The AY's volume registers take effect immediately on write. Some players update the volume registers **before** the period registers, others **after**. On real hardware this can produce a one-cycle (sub-audible) click, but on emulators that don't model the exact write timing, the result can differ noticeably.

The standard convention (followed by PT3 and all three Arkos players) is to update period registers first, then volumes, then the mixer — this minimises transient artefacts.

### 3. The skip-unchanged optimisation

When a player skips writing a register because its value hasn't changed, the AY chip's actual register state is unchanged — fine. But if the player's shadow copy drifts out of sync (e.g. because of a bug, or because another piece of code wrote to the AY directly), the skip-unchanged optimisation will cause stale values to persist. This is a common source of "where did that note come from?" bugs in software that mixes player-driven music with direct AY access for sound effects.

---

## Recommendation Matrix

The matrix below maps the most common use cases to the recommended player. For each use case, the table shows the primary recommendation and one or two alternatives.

| Use case | Primary recommendation | Alternative(s) | Reasoning |
|----------|------------------------|-----------------|-----------|
| **48K or 128K game, no size pressure** | AKG | PT3 (if existing PT3 archive) | AKG's balanced profile fits most games; PT3 if the composer already has a VTII workflow. |
| **48K or 128K game, tight on code size** | PT3 | AKM (single-PSG only) | PT3's smaller code frees up RAM for the game; AKM if composer uses Arkos. |
| **1K intro** | AKM | Hand-crafted beeper | AKM is the only AY player that fits comfortably in a 1K intro. Beeper-only if no AY available. |
| **4K intro** | AKM | AKG (if features needed) | AKM leaves more room for visuals; AKG if the intro needs portamento nuances. |
| **Demo with raster effects or multicolour** | AKY | AKG (if no digidrums) | AKY's low CPU cost leaves the most frame budget for effects. |
| **Demo with digidrums** | AKY | (no alternative) | AKY is the only Arkos player with native digidrum support. |
| **Demo with multi-PSG music (TurboSound)** | AKY | AKG | Both support multi-PSG; AKY if budget is tight, AKG if features matter. |
| **ZX Spectrum Next (3× AY)** | AKG | AKY | AT3 supports the Next's 3×AY natively. AKG for games, AKY for demos. |
| **Music-collection program (music disk)** | PT3 | AKG | PT3 gives access to the existing archive. AKG if the disk showcases original Arkos music. |
| **Cartridge / shadow-ROM production** | AKG (ROM variant) | AKY (ROM variant) | ROM variants avoid the self-modifying code in RAM players. |
| **Cross-platform multi-target release** | AKG | AKM | Note-based format is most portable across PSG clocks. |
| **Archival / preservation** | PT3 | (no alternative) | PT3 is the de facto interchange format; preserve in PT3. |
| **Sound effects only (no music)** | Arkos SE | (custom code) | SE is Targhan's sound-effect-only player. |

### Targhan's official recommendation

Julien Nevo (Targhan), the Arkos Tracker author, publishes a simpler decision table on the [Arkos Tracker players overview page](https://www.julien-nevo.com/arkostracker/index.php/players-overview/). His summary:

- **Working on a game?** AKG or AKM (more limited).
- **Working on a demo?** FAP (CPC only) or AKY (multi-platform) — compare.
- **Working on a size-limited demo?** AKM.
- **Need more than 3 channels?** AKY.
- **Need samples (no PSG sound)?** MOD.
- **Need short samples along PSG sounds (i.e. digidrums)?** AKY.
- **Need pitched samples along with PSG sounds?** AKY.
- **You have SID sounds?** AKY.
- **Don't need music, only sound effects?** SE.

(FAP is CPC-only and not available on the ZX Spectrum; ignore it for ZX work.)

---

## Common Pitfalls

| # | Pitfall | Consequence | Fix |
|---|---------|-------------|-----|
| 1 | **Expecting AKY to sound the same on a Pentagon and a Sinclair 128K** | Music plays at the wrong pitch because AKY pre-encodes periods tied to one PSG clock | Export a separate AKY module per target platform from AT3. |
| 2 | **Using AKM for envelope-bass music** | Subtle "click" on envelope retriggers due to AKM's simplification | Use AKG (or AKY) for envelope-heavy music. |
| 3 | **Assuming PT3 is "legacy" and therefore inferior** | Choosing AKG unnecessarily, losing access to the PT3 module archive | PT3 remains the de facto interchange format. Use it for archival and for compatibility with the existing module ecosystem. |
| 4 | **Mixing sound-effect AY writes with a player using skip-unchanged** | Player's shadow copy goes out of sync with the actual AY state; stale notes persist | Either (a) re-sync the shadow copy after every SFX write, or (b) use a player without skip-unchanged. |
| 5 | **Choosing AKY for size-limited productions** | AKY's larger module format eats the savings from its smaller player code | Use AKM for size-limited work; AKY's speed matters when CPU is the constraint, not RAM. |
| 6 | **Forgetting that AKM is single-PSG only** | Trying to use AKM for TurboSound music; fails at compile time | Use AKG or AKY for multi-PSG music. |
| 7 | **Forgetting that ROM-only productions need the ROM player variant** | Game crashes on the first player write because it tries to modify code in ROM | Use the ROM player variant (AKG and AKY have one; PT3 has none; AKM is ROM-safe by default). |
| 8 | **Benchmarking CPU cost with a quiet passage and assuming it generalises** | Underestimating real-world CPU cost when the music gets busy; demo effects stutter | Benchmark with the busiest passage in the song, not the average. |
| 9 | **Expecting cross-family module conversion (PT3 → Arkos or vice versa)** | No automatic converter exists; manual conversion is required | Recompose in the target tracker, or stay in the original family. |
| 10 | **Assuming the AT3-exported `.aks` binary is the same for AKG/AKM/AKY** | Each profile produces a different binary; using the wrong one fails at compile or plays wrong | Export separately for each target profile in AT3. |

---

## Modern Analogies

- **PT3 vs Arkos** is the same kind of split as **MP3 vs Opus** in modern audio: PT3 (like MP3) is the universal interchange format with the largest archive; Arkos (like Opus) is the newer, more efficient format that is technically superior but has a smaller installed base.
- **AKG / AKM / AKY** correspond to the **quality / size / speed profiles** in modern video encoding (e.g. x264's preset slider): AKG is the "balanced" preset, AKM is "smallest", AKY is "fastest".
- **The skip-unchanged optimisation** is the same idea as **dirty-flag rendering** in modern game engines — only the things that changed since last frame are touched.
- **The cross-platform PSG-clock issue** is directly analogous to **sample-rate conversion** in modern digital audio: a 44.1 kHz sample played back at 48 kHz is slightly faster and higher-pitched, just as a 1.7734 MHz-PT3 module on a 1.75 MHz-Pentagon is slightly slower and lower-pitched.

---

## Cross-References

- [AY Player Routines](ay_player_routines.md) — the architecture shared by all four players (ISR integration, register-write idiom, timing budget, memory placement); this article focuses on the differences
- [PT3 Format](../trackers_and_formats/pt3_format.md) — the binary specification of PT3 modules
- [Vortex Tracker II](../trackers_and_formats/vortex_tracker.md) — the modern tracker that produces PT3 modules
- [Arkos Tracker](../trackers_and_formats/arkos_tracker.md) — the tracker that produces AKG/AKM/AKY modules
- [AY Music Formats](../trackers_and_formats/ay_music_formats.md) — broader format overview across the ZX ecosystem
- [Sound Hardware Overview](../hardware/sound_overview.md) — the hardware ecosystem that the players target
- [AY/YM Synthesis](../synthesis/ay_ym_synthesis.md) — how the AY turns register values into sound waves (relevant to the sound-quality discussion)
- [TurboSound](../hardware/turbosound.md) — the dual-AY extension; considerations for multi-PSG players (AKG and AKY)
- [ZX Next Audio](../hardware/zx_next_audio.md) — the 3×AY + DMA audio on the ZX Spectrum Next

---

## Primary Sources

- **Arkos Tracker 3 — Players Overview** — [julien-nevo.com/arkostracker/index.php/players-overview/](https://www.julien-nevo.com/arkostracker/index.php/players-overview/). Targhan's official decision table for AKG / AKM / AKY / FAP / MOD / SE; the "Which player to use?" guide.
- **Arkos Tracker 3 GitHub repository** — [github.com/ArkosTracker/arkestracker](https://github.com/ArkosTracker/arkestracker). Source for the player routines; the `player/` directory contains the AKG, AKM, AKY sources with per-platform subdirectories.
- **Bulba's AY-3-8910/8912 Homepage** — [bulba.untergrund.net](https://bulba.untergrund.net/). The canonical source for the PT3 player routine (source and binary) and the VTII tracker.
- **ZXArt archive** — [zxart.ee](https://zxart.ee). The world's largest archive of ZX Spectrum music, predominantly in PT3 format. Useful for benchmarking different players against real-world modules.
- **AY/YM chip documentation** — see [ay_3_8912.md](../hardware/ay_3_8912.md) for the chip-level register map and per-model clock frequencies.
- **Shiru's AY music pages** — [shiru.untergrund.net](http://shiru.untergrund.net/). Independent write-ups on AY player architecture and the practical differences between PT3 and Arkos.
- **ZX Spectrum demo scene benchmarks** — demos from entities like Bauknecht, Factor6, and Ultra Hedgehog-of-SHIFT that use different players in different parts provide real-world CPU-cost data; see the demo scene archives for source code.

---

*Article 2 of 2 in the [Player Routines](README.md) sub-section. Companion article: [AY Player Routines](ay_player_routines.md) (the architecture shared by all four).*
