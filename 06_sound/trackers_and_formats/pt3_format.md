[← Home](../../README.md) · [Sound](../README.md) · [Trackers & Formats](README.md)

# PT3 Module Format

> **Status**: Stub — article not yet written

The PT3 format is the most widely used AY/YM music module format on the ZX Spectrum. This article documents its complete binary structure.

---

## Planned Content

- File structure: header, frequency table pointer, patterns, samples, ornaments
- Header layout: version byte, tempo, delay, positions table
- Frequency tables: selectable tuning (ZX, Atari ST, custom), note-to-period mapping
- Pattern format: note/note-off/sample-change/effect columns, packing
- Sample format: volume envelope, tone variation (arpeggio/noise), loop points
- Ornament format: pitch offset sequences, note-to-note transitions
- Player routine: how the PT3 player interprets this data at runtime
- Version differences: PT3.0 through PT3.7
- How to parse a .pt3 file programmatically

---

## Cross-References

- [Vortex Tracker II](vortex_tracker.md) — the editor that produces PT3
- [Tracker History](tracker_history.md) — PT3's place in the lineage
- [AY Music Formats](ay_music_formats.md) — all formats compared
