[← Home](../README.md) · [Demoscene](README.md)

# Demo Frameworks — Effect Sequencing and Music Sync

> **Status**: Stub — article not yet written

A demo framework manages the lifecycle of a demo: loading effects, timing transitions, synchronizing music, and managing memory. This article covers the architecture of ZX Spectrum demo engines.

---

## Planned Content

- Demo structure: intro → parts → credits, linear timeline
- Effect sequencing: timer-based or music-position-based transitions
- Music synchronization: reading the player's position counter for event triggers
- Resource management: loading parts from disk, decompressing on the fly
- Memory layout: where to put code, data, music, double buffers
- ISR architecture: single ISR for music + effects, or split timing
- Part transitions: crossfades, blank-frame swaps, gradual load
- Common framework patterns: event list, script-driven, hardcoded sequence
- Notable frameworks: which groups built reusable engines
- ZX Spectrum Next-specific considerations: Layer 2, tilemap, copper

---

## Cross-References

- [Effects Catalog](effects_catalog.md) — what frameworks sequence
- [Compression and Packing](compression_packing.md) — resource management
- [AY Player Routines](../06_sound/players/ay_player_routines.md) — music sync integration
- [IM2 Programming](../05_development/04_interrupts/im2_programming.md) — ISR setup
