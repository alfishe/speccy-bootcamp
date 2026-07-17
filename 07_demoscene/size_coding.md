[← Home](../README.md) · [Demoscene](README.md)

# Size Coding — 1K / 4K / 16K Intro Competitions

> **Status**: Stub — article not yet written

Size-limited intro competitions challenge programmers to create visual effects and music in as little as 1024 bytes. This article covers the extreme optimization techniques that make this possible.

---

## Planned Content

- Competition categories: 256 bytes, 1K, 4K, 16K — rules and traditions
- Self-modifying code: code that rewrites itself for multi-use
- Code-as-data: overlapping tables, instructions serving double duty
- Register tricks: using AF, IX/IY halves for storage, shadow register set
- SMC patterns: load-modify-execute loops, runtime code generation
- Boot sector tricks: getting the most from the first byte
- Minimal music: AKM player, hand-crafted beeper loops, table-driven sound
- Compression for size coding: ZX0 + self-extracting depacker
- Well-known size coding techniques: XOR textures, SMC generators, ROM call abuse
- Famous 1K/4K intros and what they achieved
- Z80 vs other architectures for size coding (6502, 68000, x86)

---

## Cross-References

- [Compression and Packing](compression_packing.md) — ZX0 and depackers
- [Effects Catalog](effects_catalog.md) — which effects fit in tight size limits
- [Z80 Undocumented](../01_cpu/z80_undocumented.md) — tricks used in size coding
- [Z80 Coding Practices](../01_cpu/z80_coding_practices.md) — general optimization
