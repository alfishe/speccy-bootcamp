[← Home](../../README.md) · [Sound](../README.md) · [Hardware](README.md)

# Sound Hardware

> Hardware reference for every sound device across all three tracks — Original, Soviet clones, and New Gen. From the built-in 1-bit beeper to 24-channel OPL4 wavetable synthesis.

---

## Quick Reference

| If you want... | Read this |
|----------------|-----------|
| Which hardware fits my project | [sound_overview.md](sound_overview.md) |
| Standard AY/YM programming | [ay_3_8912.md](ay_3_8912.md) |
| Multi-chip AY setup | [turbosound.md](turbosound.md) |
| FM synthesis on ZX | [turbosound_fm.md](turbosound_fm.md) or [moonsound.md](moonsound.md) |
| Sample playback | [covox_sounDrive.md](covox_sounDrive.md) or [gs_general_sound.md](gs_general_sound.md) |
| Modern/Next audio | [zx_next_audio.md](zx_next_audio.md) |

---

## Articles

### Overview & Decision Guide

| Article | Description |
|---------|-------------|
| [sound_overview.md](sound_overview.md) | **Sound hardware ecosystem overview + decision guide** — taxonomy, chronology, compatibility matrix, which hardware for which use case |

### PSG Chips (Programmable Sound Generators)

| Article | Description |
|---------|-------------|
| [ay_3_8912.md](ay_3_8912.md) | **AY-3-8912 / YM2149F** — The standard ZX sound chip. Pinout, register map, clock domains, DAC ladder, per-model differences, tone/noise/envelope |
| [stereo_audio.md](stereo_audio.md) | **Stereo modifications** — ABC/ACB channel separation, hardware mixing circuits, BytesDelight, mono-to-stereo upgrades |
| [turbosound.md](turbosound.md) | **TurboSound** — Dual/triple AY expansion. Port #FF chip select, programming model, 6/9 channels |
| [saa1099.md](saa1099.md) | **SAA1099** — Philips 6-channel stereo PSG. SAM Coupe's sound chip, ZX adaptations, register map |

### FM Synthesis

| Article | Description |
|---------|-------------|
| [turbosound_fm.md](turbosound_fm.md) | **TurboSound FM (TSFM)** — YM2203 OPN FM synthesis. 3 FM + 3 SSG channels per chip, register map, Soviet clone standard |
| [moonsound.md](moonsound.md) | **MoonSound (OPL4)** — YMF278B wavetable + FM. 24-channel PCM + 18-channel OPL3 FM, 1MB wave ROM, rare ZX adaptation |

### Sample Playback / DAC

| Article | Description |
|---------|-------------|
| [covox_sounDrive.md](covox_sounDrive.md) | **Covox & SounDrive** — 8-bit DAC direct playback. Single-channel Covox, 4-channel SounDrive (TLC7226CN), port mapping, stereo panning |
| [gs_general_sound.md](gs_general_sound.md) | **General Sound / NeoGS** — Dedicated Z80-based sound coprocessor. 4-channel sample mixing, command protocol, 64KB/128KB RAM, zero CPU cost |
| [dma_usc.md](dma_usc.md) | **DMA USC** — Intel 8237 DMA-based autonomous sample playback. Zero CPU cost during playback |

### Modern / FPGA

| Article | Description |
|---------|-------------|
| [zx_next_audio.md](zx_next_audio.md) | **ZX Spectrum Next Audio** — 3× FPGA AY (TurboSound Next), DMA-driven 8-bit sample playback, stereo DAC, beeper compatibility |

---

## Cross-References

### Related Sound Topics

- [Synthesis Techniques](../synthesis/README.md) — How to program these chips: PWM, SID-sound, buzzer bass, sample playback
- [Trackers & Formats](../trackers_and_formats/README.md) — Music editors and file formats for these chips
- [Player Routines](../players/README.md) — Integrating music playback into your code

### Port Reference

- [I/O Port Map](../../10_references/io_port_map.md) — Complete port addresses with 16-bit decoding masks
- [ZX Ports Full Table](../../10_references/zx_ports_full_table.md) — Black_Cat's comprehensive port table

### Hardware Context

- [Clone Hardware](../../02_hardware/clones/) — Soviet machines with TurboSound/GS built-in
- [Memory & I/O](../../05_development/03_memory_and_io/) — AY port decoding (#FFFD/#BFFD)
