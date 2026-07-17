[← Home](../README.md) · [Demoscene](README.md)

# Precalculated Trigonometry and Lookup Tables

> **Status**: Stub — article not yet written

The Z80 has no hardware multiply or divide, making real-time trigonometric calculations impractical. The demoscene solves this with precomputed lookup tables — sine, cosine, fixed-point multiplication, and interpolation.

---

## Planned Content

- Fixed-point arithmetic: Q8.8 and Q4.4 formats, when to use each
- Sine table generation: offline precomputation, symmetries (4-fold, 8-fold)
- Table compression: storing only a quarter-wave, mirror symmetry tricks
- Sine interpolation: linear interpolation between table entries for finer resolution
- 3D rotation matrices: precomputed rotation tables for demo effects
- Fast multiply: using lookup tables instead of Z80's slow multiply loop
- Division tables: reciprocal lookups
- Memory budget: table sizes vs accuracy tradeoffs
- Self-modifying code: tables that double as code
- Practical examples: plasma effect, 3D rotation, tunnel renderer

---

## Cross-References

- [Effects Catalog](effects_catalog.md) — effects that use these tables
- [Size Coding](size_coding.md) — table compression in size-limited intros
- [Z80 Instruction Set](../01_cpu/z80_instruction_set.md) — available math instructions
