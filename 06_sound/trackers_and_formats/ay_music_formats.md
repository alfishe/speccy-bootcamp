[← Home](../../README.md) · [Sound](../README.md) · [Trackers & Formats](README.md)

# AY Music Formats — Complete Reference

> **Status**: Stub — article not yet written

The ZX Spectrum AY music scene uses dozens of file formats. This article is a comprehensive reference covering module formats, register dumps, and memory snapshots.

---

## Planned Content

- **Module formats** (composable, editable): .PT3, .ASC, .STC, .STP, .AKS, .SKM
- **Register dump formats** (pre-rendered): .PSG, .YM, .VTX, .AY
- **Memory dump format**: .AY (ZX Spectrum memory snapshot with embedded player)
- PSG format: frame-based register dumps, escape bytes, interleaved vs non-interleaved
- YM format: LZSS-compressed register dumps, Atari ST clock assumption
- VTX format: variable-length compressed dumps for multiple chips
- AY format: full memory snapshot, header format, player location
- When to use each format: composition vs playback vs archival
- Software support: which players/editors handle which formats
- Clock frequency specification in each format

---

## Cross-References

- [PT3 Format](pt3_format.md) — the dominant module format (deep dive)
- [PSG Format](psg_format.md) — register dump format (deep dive)
- [Tracker History](tracker_history.md) — which trackers produced which formats
