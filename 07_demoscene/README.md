[← Home](../README.md) · [Section Index](README.md)

# 07 — Demoscene

> The ZX Spectrum demoscene represents the **absolute apex** of what can be squeezed from a 3.5 MHz Z80, an attribute-based color system, and contended memory. This section documents the techniques, history, and culture that produced effects people still find hard to believe came from 1980s hardware.

---

## Why Demoscene Gets Its Own Section

Demoscene techniques transcend normal game development. They push the hardware past its specified limits using cycle-exact timing, undocumented CPU features, and a deep understanding of video timing that borders on hardware abuse. The Soviet demo scene — centered around the Pentagon clone — developed its own distinctive style and techniques that differ significantly from the Western scene. This warrants dedicated coverage separate from general development.

---

## Section Structure

### History & Culture

| Article | Description |
|---------|-------------|
| `demoscene_history.md` *(planned)* | ZX Spectrum demoscene: Western origins, Soviet explosion, modern revival, cultural impact |
| `soviet_demo_scene.md` *(planned)* | Russian/Ukrainian scene: unique effects, Pentagon-centric development, notable groups (E-Mage, Extreme, Progress, Skrju) |
| `demoscene_platforms.md` *(planned)* | Cross-platform comparison: Spectrum vs C64 vs Amiga vs Atari ST — what each could do that others couldn't |

### Techniques

| Article | Description |
|---------|-------------|
| `effects_catalog.md` *(planned)* | Visual effects catalog: plasma, raycasting, 3D objects, multicolor, zoomers, tunnel effects, copper bars |
| `multicolor_techniques.md` *(planned)* | Multicolor / attribute interrupt: 8×1 and 8×2 color resolution, race-the-beam timing, per-model differences |
| `precalc_trigonometry.md` *(planned)* | Sine tables, fixed-point math, interpolation, compression of lookup tables |
| `compression_packing.md` *(planned)* | MegaLZ, HRUM, Z80 crunchers, depackers, memory-constrained decompression |
| `size_coding.md` *(planned)* | 1K/4K/16K intro competitions: self-modifying code, code-as-data, extreme optimization |

### Frameworks & Notable Works

| Article | Description |
|---------|-------------|
| `demo_frameworks.md` *(planned)* | Demo frameworks: effect sequencing, timing management, resource loading, music sync |
| `notable_demos.md` *(planned)* | Analysis of landmark demos: techniques used, how they work, what made them groundbreaking |
| `1bit_music_scene.md` *(planned)* | 1-bit music scene: beeper engine evolution from 1982 to present — see also [06_sound](../06_sound/README.md) |

---

## Cross-References

- [01_cpu/z80_timing.md](../01_cpu/z80_timing.md) — T-state counting is fundamental to every demo effect
- [01_cpu/z80_undocumented.md](../01_cpu/z80_undocumented.md) — Many demos rely on undocumented Z80 behavior
- [02_hardware/original/ula_timing.md](../02_hardware/original/ula_timing.md) — ULA contention windows are the canvas for multicolor effects
- [06_sound/](../06_sound/README.md) — Music is integral to demos; AY synthesis and beeper engines covered here
