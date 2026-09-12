[← Home](../README.md) · [Section Index](README.md)

# 06 — Sound

> Sound on the ZX Spectrum spans an extraordinary range — from the 1-bit beeper of the original 48K, through the AY-3-8912/YM2149 PSG on the 128K and clones, to multi-chip expansions (TurboSound, General Sound, MoonSound) and modern hardware (ZX Spectrum Next with 3× AY + DMA). This section covers the **entire sound ecosystem**: hardware, synthesis techniques, music software (trackers, editors, players), and file formats.

---

## Quick Navigation

| If you want to... | Start here |
|-------------------|------------|
| Understand the ZX sound hardware landscape | [sound_overview.md](hardware/sound_overview.md) |
| Program the AY-3-8912 / YM2149 | [ay_3_8912.md](hardware/ay_3_8912.md) |
| Learn synthesis techniques | [ay_ym_synthesis.md](synthesis/ay_ym_synthesis.md) |
| Compare trackers and formats | [ay_music_formats.md](trackers_and_formats/ay_music_formats.md) |
| Integrate a player routine | [ay_player_routines.md](players/ay_player_routines.md) |

---

## Why Sound Gets Its Own Section

The ZX Spectrum's audio subsystem is not a minor peripheral — it is a **vast technical domain** that touches hardware design, real-time programming, digital signal processing concepts, and an extraordinarily rich software ecosystem. The demoscene's most celebrated works are often musical. The Soviet clone scene built entire sound card ecosystems around the AY chip. Understanding sound generation on the Spectrum requires grasping:

- **Hardware**: PSG architecture, DAC behavior, clock domains, analog mixing circuits
- **Synthesis**: Square wave generation, envelope shaping, noise synthesis, phase manipulation, sample playback
- **Software**: A 35-year lineage of music trackers (Sound Tracker → Pro Tracker 3 → Vortex Tracker II → Arkos Tracker), player routines that run inside ISRs, and dozens of file formats
- **Multi-chip**: TurboSound (dual/triple AY), General Sound (dedicated Z80 sound card), FM synthesis (YM2203), wavetable (OPL4)

---

## Section Structure

### [Sound Hardware](hardware/README.md)

Hardware reference for every sound device across all three tracks (Original, Soviet Clone, New Gen).

| Article | Description |
|---------|-------------|
| [sound_overview.md](hardware/sound_overview.md) | **Sound hardware ecosystem overview + decision guide** — navigation hub, taxonomy, chronology, decision matrix |
| [ay_3_8912.md](hardware/ay_3_8912.md) | AY-3-8912 / YM2149F PSG: pinout, register map, clock domains, DAC characteristics, per-model differences |
| [stereo_audio.md](hardware/stereo_audio.md) | Stereo audio modifications: ABC/ACB separation, mixing circuits, BytesDelight |
| [turbosound.md](hardware/turbosound.md) | TurboSound: dual/triple AY, port decoding, chip selection, programming model |
| [turbosound_fm.md](hardware/turbosound_fm.md) | TurboSound FM: YM2203 (OPN) FM synthesis, 3 FM + 3 SSG channels, register map |
| [saa1099.md](hardware/saa1099.md) | SAA1099 PSG: Philips 6-channel stereo sound chip, SAM Coupe and ZX adaptations |
| [covox_sounDrive.md](hardware/covox_sounDrive.md) | Covox & SounDrive: 8-bit DAC direct sample playback, 4-channel hardware mixing |
| [gs_general_sound.md](hardware/gs_general_sound.md) | General Sound / NeoGS: dedicated Z80-based sound card, 4-channel sample mixing, command protocol |
| [dma_usc.md](hardware/dma_usc.md) | DMA USC: Intel 8237 DMA-based autonomous sample playback, zero CPU cost |
| [moonsound.md](hardware/moonsound.md) | MoonSound (OPL4/YMF278B): 24-channel wavetable + 18-channel FM synthesis |
| [zx_next_audio.md](hardware/zx_next_audio.md) | ZX Spectrum Next audio: 3× FPGA AY + beeper + DMA sample playback |

### [Synthesis Techniques](synthesis/README.md)

Sound generation theory and practice — how to make the chips produce the sounds you want.

| Article | Description |
|---------|-------------|
| [ay_ym_synthesis.md](synthesis/ay_ym_synthesis.md) | **Comprehensive AY/YM sound generation**: internal counter model, register mechanics, phase reset, envelope exploitation, sample playback |
| [ay_ym_techniques.md](synthesis/ay_ym_techniques.md) | AY/YM synthesis techniques: sync-square, PWM, SID-sound, buzzer bass, note-colored noise, drum synthesis |
| [ay_vs_ym.md](synthesis/ay_vs_ym.md) | AY vs YM technical comparison: DAC ladder differences, 5-bit envelope on YM, DC offset, per-unit variation |
| [ay_ym_perception.md](synthesis/ay_ym_perception.md) | The AY sound: perception, emotion, ABC vs ACB, AY vs YM, analog vs emulation, psychoacoustics |
| [beeper_synthesis.md](synthesis/beeper_synthesis.md) | 1-bit beeper synthesis: PWM engines, multi-channel tricks, timing constraints, Phaser/Tritone/QChan |
| [shiru_ear_shaver_analysis.md](synthesis/shiru_ear_shaver_analysis.md) | Case study: reverse engineering Shiru's *Ear Shaver* 1-bit engine via API forensics |
| [multitrack_multichip.md](synthesis/multitrack_multichip.md) | Multi-track and multi-chip synthesis: TurboSound, interleaved channels, cross-chip synchronization |

### [Trackers, Editors & Formats](trackers_and_formats/README.md)

The software ecosystem for creating and storing AY/YM music — from the original Sound Tracker (1990) through modern cross-platform tools.

| Article | Description |
|---------|-------------|
| [tracker_history.md](trackers_and_formats/tracker_history.md) | 30-year history of ZX music editors: beeper trackers, Pro Tracker lineage, VTII/Arkos split |
| [ay_music_formats.md](trackers_and_formats/ay_music_formats.md) | **Master catalog**: every AY/YM music file format (`.PT3`, `.PSG`, `.YM`, `.AY`, `.AKG`, etc.) |
| [sound_tracker.md](trackers_and_formats/sound_tracker.md) | Sound Tracker 1.1 (Bzyk, 1990): the first AY grid editor, pattern/sample/ornament paradigm |
| [asc_sound_master.md](trackers_and_formats/asc_sound_master.md) | ASC Sound Master (Sendetskiy, 1992): Soviet alternative, envelope-mode-per-tick instruments |
| [protracker.md](trackers_and_formats/protracker.md) | Pro Tracker 1/2/3 (Golden Disk Corp., 1995–1997): the format-defining `.PT3` lineage |
| [vortex_tracker.md](trackers_and_formats/vortex_tracker.md) | Vortex Tracker II: de facto PC-based PT3 editor (Bulba, 2000–present), TurboSound support |
| [arkos_tracker.md](trackers_and_formats/arkos_tracker.md) | Arkos Tracker 2/3: modern cross-platform tracker (Targhan), AKG/AKM/AKY players |
| [pt3_format.md](trackers_and_formats/pt3_format.md) | PT3 module format specification: header, position table, ornaments, samples, patterns |
| [psg_format.md](trackers_and_formats/psg_format.md) | PSG register dump format: frame structure, variants (`.YM`, `.VTX`), 20-byte playback routine |

### [Player Routines](players/README.md)

Integration of music playback into games and demos — from minimal ISR players to optimized replayers.

| Article | Description |
|---------|-------------|
| [ay_player_routines.md](players/ay_player_routines.md) | AY player routines: ISR integration, PT3/Arkos/Vortex players, memory footprint, CPU cost |
| [player_comparison.md](players/player_comparison.md) | Player comparison matrix: size, speed, features, format support |

---

## Cross-References

### Related Sections

- [02_hardware/](../02_hardware/) — ULA timing, contention (affects audio timing), clone hardware
- [05_development/03_memory_and_io/](../05_development/03_memory_and_io/) — AY port decoding (#FFFD/#BFFD), interrupt timing
- [10_references/io_port_map.md](../10_references/io_port_map.md) — Complete I/O port addresses with 16-bit decoding masks
- [11_emulation/](../11_emulation/) — AY emulation accuracy, cycle-exact audio

### External Resources

- [Vortex Tracker II](http://vtii.seban.ru/) — the standard PC-based PT3 editor
- [Arkos Tracker 2](https://www.julien-nevo.com/arkostracker/) — modern cross-platform tracker
- [AY Emulator](https://bulba.untergrund.net/emulator.htm) — Bulba's cycle-accurate AY emulator core
- [zxart.ee Music Archive](https://zxart.ee/eng/music/) — largest ZX Spectrum music database
