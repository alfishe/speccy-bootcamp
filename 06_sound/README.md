[← Home](../README.md) · [Section Index](README.md)

# 06 — Sound

> Sound on the ZX Spectrum spans an extraordinary range — from the 1-bit beeper of the original 48K, through the AY-3-8912/YM2149 PSG on the 128K and clones, to multi-chip expansions (TurboSound, General Sound, MoonSound) and modern hardware (ZX Spectrum Next with 3× AY + DMA). This section covers the **entire sound ecosystem**: hardware, synthesis techniques, music software (trackers, editors, players), and file formats.

---

## Why Sound Gets Its Own Section

The ZX Spectrum's audio subsystem is not a minor peripheral — it is a **vast technical domain** that touches hardware design, real-time programming, digital signal processing concepts, and an extraordinarily rich software ecosystem. The demoscene's most celebrated works are often musical. The Soviet clone scene built entire sound card ecosystems around the AY chip. Understanding sound generation on the Spectrum requires grasping:

- **Hardware**: PSG architecture, DAC behavior, clock domains, analog mixing circuits
- **Synthesis**: Square wave generation, envelope shaping, noise synthesis, phase manipulation, sample playback
- **Software**: A 35-year lineage of music trackers (Sound Tracker → Pro Tracker 3 → Vortex Tracker II → Arkos Tracker), player routines that run inside ISRs, and dozens of file formats
- **Multi-chip**: TurboSound (dual/triple AY), General Sound (dedicated Z80 sound card), FM synthesis (YM2203), wavetable (OPL4)

---

## Section Structure

### [Synthesis Techniques](synthesis/README.md)

Sound generation theory and practice — how to make the chips produce the sounds you want.

| Article | Description |
|---------|-------------|
| [ay_ym_synthesis.md](synthesis/ay_ym_synthesis.md) | **Comprehensive AY/YM sound generation**: internal counter model, register mechanics, phase reset, sync-square, PWM, envelope exploitation, SID-sound, sample playback |
| [ay_ym_perception.md](synthesis/ay_ym_perception.md) | **The AY Sound: Perception, Emotion, and the Hardware Soul** — ABC vs ACB, AY vs YM, analog vs emulation, psychoacoustics, nostalgia, recapturing the sound |
| [beeper_synthesis.md](synthesis/beeper_synthesis.md) | 1-bit beeper synthesis: PWM engines, multi-channel tricks, timing constraints |
| [shiru_ear_shaver_analysis.md](synthesis/shiru_ear_shaver_analysis.md) | **Case Study:** Reverse engineering Shiru's *Ear Shaver* 1-bit engine via API forensics |
| [multitrack_multichip.md](synthesis/multitrack_multichip.md) | Multi-track and multi-chip synthesis: TurboSound, interleaved channels, cross-chip effects, synchronization |

### [Sound Hardware](hardware/README.md) *(planned)*

Hardware reference for every sound device across all three tracks.

| Article | Description |
|---------|-------------|
| `ay_3_8912.md` | AY-3-8912 / YM2149F PSG: pinout, register map, clock domains, DAC characteristics, per-model differences |
| `turbosound.md` | TurboSound: dual/triple AY, port decoding, programming model |
| `turbosound_fm.md` | TurboSound FM: YM2203 (OPN) FM synthesis, 3 FM + 3 SSG channels |
| `covox_sounDrive.md` | Covox (8-bit DAC), SounDrive (4×8-bit DAC): direct sample playback |
| `gs_general_sound.md` | General Sound: dedicated Z80-based sound card, 4-channel sample mixing |
| `moonsound.md` | MoonSound (OPL4/YMF278B): 24-channel wavetable + 18-channel FM |
| `saa1099.md` | SAA1099 PSG: Philips sound chip, 6-channel stereo |
| `zx_next_audio.md` | ZX Spectrum Next audio: 3× AY + beeper + DMA sample playback |
| `stereo_audio.md` | Stereo audio modifications: ABC/ACB separation, BytesDelight |
| `sound_overview.md` | Sound hardware ecosystem overview + decision guide |

### [Trackers, Editors & Formats](trackers_and_formats/README.md) *(planned)*

The software ecosystem for creating and storing AY/YM music.

| Article | Description |
|---------|-------------|
| `tracker_history.md` | Chronological history: Sound Tracker (1990) → Pro Tracker 3 → Vortex Tracker II → Arkos Tracker |
| `vortex_tracker.md` | Vortex Tracker II: the de facto PC-based PT3 editor, format import/export |
| `arkos_tracker.md` | Arkos Tracker 2/3: modern cross-platform AY/YM tracker with multi-PSG support |
| `pt3_format.md` | PT3 module format specification: header, patterns, ornaments, instruments |
| `ay_music_formats.md` | All AY music formats: module formats (.PT3/.ASC/.STC/.STP), register dumps (.PSG/.YM/.VTX), memory dumps (.AY) |
| `psg_format.md` | PSG register dump format: frame structure, escape bytes, clock specification |

### [Player Routines](players/README.md) *(planned)*

How music data becomes sound on real hardware.

| Article | Description |
|---------|-------------|
| `ay_player_routines.md` | Player routine architecture: ISR integration, register write sequences, stack manipulation, timing budgets |
| `player_comparison.md` | PT3 player vs Arkos players (AKG/AKM/AKY): speed, size, features comparison |
| `audio_decision_guide.md` | Decision guide: which sound hardware + format + player to target for your project |

---

## Cross-References

- [02_hardware/original/](../02_hardware/original/) — ULA timing, contention (affects audio timing)
- [05_development/03_memory_and_io/memory_and_io_128k.md](../05_development/03_memory_and_io/memory_and_io_128k.md) — AY port decoding (#FFFD/#BFFD)
- [10_references/io_port_map.md](../10_references/io_port_map.md) — AY port addresses with decoding bitmasks
- [11_emulation/software/cycle_exact_accuracy.md](../11_emulation/software/cycle_exact_accuracy.md) — AY audio clock accuracy in emulation
