[← Home](../../README.md) · [Sound](../README.md) · [Hardware](README.md)

# ZX Spectrum Next Audio

> **Status**: Stub — article not yet written

The ZX Spectrum Next has the most powerful audio subsystem of any Spectrum: 3 AY chips (9 channels), a 1-bit beeper, and hardware DMA-driven sample playback — all controllable independently.

---

## Planned Content

- Three AY chips at programmable clock (default 1.7734 MHz)
- DMA audio: hardware sample playback via DMA controller, independent of CPU
- Beeper: 1-bit output for legacy compatibility
- Register interface: AY bank-select, DMA configuration ports
- Programming model: combining AY synthesis with DMA samples
- Sample rates and format for DMA playback
- Music software support on Next

---

## Cross-References

- [AY/YM Sound Generation](../synthesis/ay_ym_synthesis.md) — PSG programming
- [TurboSound](turbosound.md) — multi-AY techniques
- [ZX Spectrum Next Memory and I/O](../../05_development/03_memory_and_io/memory_and_io_next.md) — Next port map
