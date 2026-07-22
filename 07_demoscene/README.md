[← Home](../README.md) · [Section Index](README.md)

# 07 — Demoscene

> The ZX Spectrum demoscene represents the **absolute apex** of what can be squeezed from a 3.5 MHz Z80, an attribute-based color system, and contended memory. This section documents the techniques, history, and culture that produced effects people still find hard to believe came from 1980s hardware.
>
> **Status**: All 11 articles are complete (CC BY-SA 4.0). Cross-references between articles are verified. The section is the deepest single-source reference on the ZX Spectrum demoscene available in English as of 2024.

---

## Why Demoscene Gets Its Own Section

Demoscene techniques transcend normal game development. They push the hardware past its specified limits using cycle-exact timing, undocumented CPU features, and a deep understanding of video timing that borders on hardware abuse. The Soviet demo scene — centered around the Pentagon clone — developed its own distinctive style and techniques that differ significantly from the Western scene. This warrants dedicated coverage separate from general development.

---

## Section Structure

### History & Culture

| Article | Description |
|---------|-------------|
| [demoscene_history.md](demoscene_history.md) | ZX Spectrum demoscene: Western origins, Soviet explosion, modern revival, cultural impact |
| [soviet_demo_scene.md](soviet_demo_scene.md) | Russian/Ukrainian scene: unique effects, Pentagon-centric development, notable groups (Eternity, Brutal, X-Trade, Progress, Skrju) |
| [demoscene_platforms.md](demoscene_platforms.md) | Cross-platform comparison: Spectrum vs C64 vs Amiga vs Atari ST vs MSX vs Amstrad CPC — what each could do that others couldn't |

### Techniques

| Article | Description |
|---------|-------------|
| [effects_catalog.md](effects_catalog.md) | Visual effects catalog: plasma, raycasting, 3D objects, multicolor, zoomers, tunnel effects, copper bars |
| [multicolor_techniques.md](multicolor_techniques.md) | Multicolor / attribute interrupt: 8×1 and 8×2 color resolution, race-the-beam timing, per-model differences |
| [precalc_trigonometry.md](precalc_trigonometry.md) | Sine tables, fixed-point math, interpolation, compression of lookup tables |
| [compression_packing.md](compression_packing.md) | 25 crunchers across 4 generations: ZX0/ZX1/ZX2/MegaLZ/Pletter/HRUM, depackers, RCS, worked example |
| [size_coding.md](size_coding.md) | 256 B / 1 K / 4 K / 16 K intro competitions: squeeze, reuse, math tricks, compression, ROM routines |

### Frameworks & Notable Works

| Article | Description |
|---------|-------------|
| [demo_frameworks.md](demo_frameworks.md) | Demo frameworks: effect sequencing, music synchronisation, memory layout, ISR architecture, part transitions |
| [notable_demos.md](notable_demos.md) | Analysis of landmark demos across four eras: Crack Intro (1986–89), Western Golden (1990–96), Soviet Peak (1996–2005), Modern Revival (2010–present) |
| [1bit_music_scene.md](1bit_music_scene.md) | 1-bit beeper music scene: hardware, techniques, engine lineage (Henry → Follin → Wham → QChan → Octode → Pusher/Squeeker), composers, community — see also [06_sound](../06_sound/README.md) |

---

## Cross-References

- [01_cpu/z80_timing.md](../01_cpu/z80_timing.md) — T-state counting is fundamental to every demo effect
- [01_cpu/z80_undocumented.md](../01_cpu/z80_undocumented.md) — Many demos rely on undocumented Z80 behavior
- [02_hardware/original/ula_timing.md](../02_hardware/original/ula_timing.md) — ULA contention windows are the canvas for multicolor effects
- [06_sound/](../06_sound/README.md) — Music is integral to demos; AY synthesis and beeper engines covered here
