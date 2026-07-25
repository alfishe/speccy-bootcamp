[← Home](../../README.md) · [Sound](../README.md) · [Players](README.md)

# AY Player Routines — Architecture and Timing

> **Status**: Stub — article not yet written

A player routine is the Z80 code that reads a music module and writes AY registers each frame. This article covers the architecture, ISR integration, timing budgets, and practical implementation patterns.

---

## Planned Content

- ISR integration: hooking IM2, saving/restoring registers, re-entrancy
- Register write sequence: address latch + data write pairs, optimal ordering
- Timing budget: how many T-states a player consumes per frame
- PT3 player routine: structure, size (~400-600 bytes), cycle count
- Arkos AKG/AKM/AKY players: structure, size comparison, cycle count
- Interrupt frequency: 50 Hz (standard) vs higher (smooth effects)
- Contended vs uncontended memory placement for player code
- Combining music playback with game/demo code
- Common pitfalls: stack corruption, contention interaction, ISR jitter

---

## Cross-References

- [PT3 Format](../trackers_and_formats/pt3_format.md) — the data the PT3 player reads
- [Player Comparison](player_comparison.md) — PT3 vs Arkos benchmark
- [IM2 Programming](../../05_development/04_interrupts/interrupt_programming.md) — interrupt mode setup
