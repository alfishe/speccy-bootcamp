[← Home](../../README.md) · [Sound](../README.md) · [Hardware](README.md)

# General Sound — Dedicated Z80 Sound Card

> **Status**: Stub — article not yet written

General Sound (GS) is a dedicated sound card with its own Z80 CPU and 4-channel 8-bit sample mixing hardware. It offloads all audio processing from the main CPU.

---

## Planned Content

- Hardware: independent Z80 at higher clock, RAM/ROM, 4-channel DAC
- Architecture: main CPU sends commands via shared memory or FIFO
- Programming model: command protocol, sample uploading, real-time control
- Sample format and storage
- Music software support (GS-specific modules)
- Comparison with Covox (CPU-driven) and AY (synthesized)
- NeoGS: modern redesign

---

## Cross-References

- [Covox / SounDrive](covox_sounDrive.md) — simpler DAC playback
- [Sound Overview](sound_overview.md) — ecosystem comparison
- [I/O Port Map](../../10_references/io_port_map.md) — GS port addresses
