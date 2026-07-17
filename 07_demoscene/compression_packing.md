[← Home](../README.md) · [Demoscene](README.md)

# Compression and Packing — MegaLZ, HRUM, Z80 Crunchers

> **Status**: Stub — article not yet written

Compression is essential on the ZX Spectrum — every byte counts. This article covers the major compression algorithms used in the demoscene, their decompression routines, and practical memory-constrained deployment.

---

## Planned Content

- Why compression matters: 48K RAM, slow tape loading, floppy space limits
- MegaLZ: fast and efficient, the standard Z80 cruncher for demos
- HRUM / HRUST: popular Soviet compression format
- Z80 cruncher: classic compressor, low ratio but tiny depacker
- Pletter: modern LZ-based compressor, configurable effort levels
- ZX0: modern (2021) compressor by Einar Saukas, excellent ratio + tiny depacker
- Algorithm comparison: ratio, depacker size, decompression speed
- In-place decompression: constraints and techniques
- Decompression during loading screens / effects: streaming depack
- Self-extracting code: compressed code that decompresses itself on entry
- When NOT to compress: timing-critical code, executable that must run immediately

---

## Cross-References

- [Size Coding](size_coding.md) — extreme compression for 1K/4K intros
- [Demo Frameworks](demo_frameworks.md) — how demos manage packed resources
- [Tape Format](../03_io/storage/tape_format.md) — loading compressed data from tape
