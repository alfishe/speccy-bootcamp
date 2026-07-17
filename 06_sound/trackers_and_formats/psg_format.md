[← Home](../../README.md) · [Sound](../README.md) · [Trackers & Formats](README.md)

# PSG Register Dump Format

> **Status**: Stub — article not yet written

The .PSG format is a simple frame-by-frame register dump of AY/YM chip state. It is the most portable format for pre-rendered AY music playback.

---

## Planned Content

- File header: magic bytes, clock frequency, chip type, song info
- Frame structure: 14 register values per frame, skip/compression via escape byte #FF
- Special bytes: #FF (skip), #FE (end of frame)
- Interleaved vs non-interleaved layouts
- Per-frame vs per-register encoding
- Clock specification: how the format encodes ZX vs Atari ST vs Pentagon timing
- Advantages: simplicity, exact playback, no player code needed
- Disadvantages: large file size, not editable, format-specific
- Comparison with .YM format (LZSS-compressed PSG variant)

---

## Cross-References

- [AY Music Formats](ay_music_formats.md) — all formats compared
- [AY/YM PSG](../hardware/ay_3_8912.md) — the chip being dumped
- [AY Player Routines](../players/ay_player_routines.md) — playing PSG dumps
