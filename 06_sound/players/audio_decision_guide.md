[← Home](../../README.md) · [Sound](../README.md) · [Players](README.md)

# Audio Decision Guide — Which Hardware, Format, and Player

> **Status**: Stub — article not yet written

A practical decision guide for choosing the right sound hardware, music format, and player routine for your ZX Spectrum project.

---

## Planned Content

- Decision tree: target hardware → available sound chips → format → player
- Compatibility matrix: which combinations work on which machines
- Common scenarios:
  - 48K-only game: beeper or no sound
  - 128K game: single AY, PT3 or Arkos
  - Pentagon demo: AY + TurboSound
  - Next demo: 3× AY + DMA
  - 1K/4K intro: AKM minimal player or hand-crafted beeper
- Tradeoffs: code size vs quality vs compatibility vs ease of composition
- Recommendation: sensible defaults for common cases

---

## Cross-References

- [Sound Hardware Overview](../hardware/sound_overview.md) — hardware catalog
- [Player Comparison](player_comparison.md) — player benchmarks
- [AY Music Formats](../trackers_and_formats/ay_music_formats.md) — format reference
