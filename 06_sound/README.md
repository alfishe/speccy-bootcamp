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
| [ay_ym_techniques.md](synthesis/ay_ym_techniques.md) | **AY/YM Synthesis Techniques** — sync-square, PWM, SID-sound, buzzer bass, note-colored noise, drum synthesis, sample playback |
| [ay_vs_ym.md](synthesis/ay_vs_ym.md) | **AY vs YM Technical Comparison** — DAC ladder differences, 5-bit envelope on YM, DC offset, SEL pin, per-unit variation, and how each major emulator models these details |
| [ay_ym_perception.md](synthesis/ay_ym_perception.md) | **The AY Sound: Perception, Emotion, and the Hardware Soul** — ABC vs ACB, AY vs YM, analog vs emulation, psychoacoustics, nostalgia, recapturing the sound |
| [beeper_synthesis.md](synthesis/beeper_synthesis.md) | 1-bit beeper synthesis: PWM engines, multi-channel tricks, timing constraints |
| [shiru_ear_shaver_analysis.md](synthesis/shiru_ear_shaver_analysis.md) | **Case Study:** Reverse engineering Shiru's *Ear Shaver* 1-bit engine via API forensics |
| [multitrack_multichip.md](synthesis/multitrack_multichip.md) | Multi-track and multi-chip synthesis: TurboSound, interleaved channels, cross-chip effects, synchronization |

### [Sound Hardware](hardware/README.md)

Hardware reference for every sound device across all three tracks.

| Article | Description |
|---------|-------------|
| [sound_overview.md](hardware/sound_overview.md) | **Sound hardware ecosystem overview + decision guide** — navigation hub for the entire subdirectory |
| [ay_3_8912.md](hardware/ay_3_8912.md) | AY-3-8912 / YM2149F PSG: pinout, register map, clock domains, DAC characteristics, per-model differences |
| [stereo_audio.md](hardware/stereo_audio.md) | Stereo audio modifications: ABC/ACB separation, BytesDelight |
| [turbosound.md](hardware/turbosound.md) | TurboSound: dual/triple AY, port decoding, programming model |
| [turbosound_fm.md](hardware/turbosound_fm.md) | TurboSound FM: YM2203 (OPN) FM synthesis, 3 FM + 3 SSG channels |
| [saa1099.md](hardware/saa1099.md) | SAA1099 PSG: Philips sound chip, 6-channel stereo |
| [covox_sounDrive.md](hardware/covox_sounDrive.md) | **Covox & SounDrive**: 8-bit DAC hardware mixing, sample playback, TLC7226CN quad DAC |
| [gs_general_sound.md](hardware/gs_general_sound.md) | General Sound: dedicated Z80-based sound card, 4-channel sample mixing |
| [moonsound.md](hardware/moonsound.md) | MoonSound (OPL4/YMF278B): 24-channel wavetable + 18-channel FM |
| [zx_next_audio.md](hardware/zx_next_audio.md) | ZX Spectrum Next audio: 3× AY + beeper + DMA sample playback |

### [Trackers, Editors & Formats](trackers_and_formats/README.md)

The software ecosystem for creating and storing AY/YM music — from the original Sound Tracker (1990) through modern cross-platform tools like Arkos Tracker 3.

| Article | Description |
|---------|-------------|
| [tracker_history.md](trackers_and_formats/tracker_history.md) | **30-year history of ZX music editors** — beeper trackers (1985), Pro Tracker lineage (Golden Disk Corp.), VTII / Arkos split, modern cross-platform tools |
| [ay_music_formats.md](trackers_and_formats/ay_music_formats.md) | **Master catalogue**: every AY/YM music file format (`.PT3`, `.PSG`, `.YM`, `.AY`, `.AKG`, etc.) — modules, dumps, containers, modern embedded |
| [sound_tracker.md](trackers_and_formats/sound_tracker.md) | **Sound Tracker 1.1** (Bzyk, 1990) — the first AY grid editor; established the pattern/sample/ornament paradigm inherited by every later tracker |
| [asc_sound_master.md](trackers_and_formats/asc_sound_master.md) | **Asc Sound Master** (Sendetskiy, 1992) — Soviet alternative with envelope-mode-per-tick instrument model; `.ASC` / `.AS0` formats |
| [protracker.md](trackers_and_formats/protracker.md) | **Pro Tracker 1/2/3** (Golden Disk Corp., 1995–1997) — the format-defining lineage that produced `.PT3`; 4 versions in 3 years |
| [vortex_tracker.md](trackers_and_formats/vortex_tracker.md) | Vortex Tracker II: the de facto PC-based PT3 editor (Bulba, 2000–present), universal import, TurboSound support |
| [arkos_tracker.md](trackers_and_formats/arkos_tracker.md) | Arkos Tracker 2/3: modern cross-platform AY/YM tracker (Targhan, 2003–present), AKG/AKM/AKY players |
| [pt3_format.md](trackers_and_formats/pt3_format.md) | PT3 module format specification: header, position table, ornaments, samples, patterns, player operation, sub-versions |
| [psg_format.md](trackers_and_formats/psg_format.md) | PSG register dump format: frame structure, skip opcode, variants (`.YM`, `.VTX`), 20-byte playback routine |

### ~~Player Routines~~ *(removed from plan)*

The planned `players/` subdirectory has been removed from the section plan. The relevant content is covered in existing articles: PT3 player operation is documented in [pt3_format.md](trackers_and_formats/pt3_format.md) § Player Routine Operation, Arkos player comparison is documented in [arkos_tracker.md](trackers_and_formats/arkos_tracker.md), and ISR/embedding considerations are touched on in [ay_ym_synthesis.md](synthesis/ay_ym_synthesis.md). Stub files remain in `players/` but are not tracked in the plan.

---

## Cross-References

- [02_hardware/original/](../02_hardware/original/) — ULA timing, contention (affects audio timing)
- [05_development/03_memory_and_io/memory_and_io_128k.md](../05_development/03_memory_and_io/memory_and_io_128k.md) — AY port decoding (#FFFD/#BFFD)
- [10_references/io_port_map.md](../10_references/io_port_map.md) — AY port addresses with decoding bitmasks
- [11_emulation/software/cycle_exact_accuracy.md](../11_emulation/software/cycle_exact_accuracy.md) — AY audio clock accuracy in emulation
