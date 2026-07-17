[← Home](../../README.md) · [Sound](../README.md) · [Hardware](README.md)

# TurboSound — Dual/Triple AY

> **Status**: Stub — article not yet written

TurboSound is a Soviet-clone-era expansion that adds a second (and sometimes third) AY chip, providing 6 or 9 tone channels. This article covers the hardware interface, port decoding, bank-select mechanism, and programming model.

---

## Planned Content

- History: origin in the Soviet clone scene, adoption across Pentagon/Scorpion/ATM
- Hardware: how the second AY is wired, bank-select port
- Port decoding: primary AY at #FFFD/#BFFD, bank-select register, secondary AY access
- Programming model: selecting active chip, writing registers, ISR integration
- Per-clone differences: Pentagon TurboSound vs Scorpion vs ATM Turbo
- Triple AY: TurboSound Next (ZX Spectrum Next) — 3 chips, 9 channels
- Detection: how software identifies TurboSound presence

---

## Cross-References

- [AY/YM Sound Generation](../synthesis/ay_ym_synthesis.md) — single-chip programming (prerequisite)
- [Multi-Track and Multi-Chip Synthesis](../synthesis/multitrack_multichip.md) — multi-chip composition techniques
- [TurboSound FM](turbosound_fm.md) — FM expansion variant
