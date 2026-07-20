[← Home](../../README.md) · [Sound](../README.md) · [Trackers & Formats](README.md)

# Trackers, Editors & Formats

> The software ecosystem for creating and storing AY/YM music — from the original Sound Tracker (1990) through modern cross-platform tools like Arkos Tracker 3.

---

## Articles

The nine articles are best read in chronological order: history first for context, then the format catalogue, then the three foundational on-Spectrum editors in chronological order, then the PC-generation tools, then the binary format references.

| # | Article | Description |
|---|---|---|
| 1 | [tracker_history.md](tracker_history.md) | The 30-year history of ZX music editors — beeper trackers, the Pro Tracker lineage, the VTII / Arkos split, modern cross-platform tools |
| 2 | [ay_music_formats.md](ay_music_formats.md) | **Master catalogue**: every AY/YM music file format (`.PT3`, `.PSG`, `.YM`, `.AY`, `.AKG`, etc.) — modules, dumps, containers, modern embedded |
| 3 | [sound_tracker.md](sound_tracker.md) | **Sound Tracker 1.1** (Bzyk, 1990) — the first AY grid editor; established the pattern/sample/ornament paradigm |
| 4 | [asc_sound_master.md](asc_sound_master.md) | **Asc Sound Master** (Sendetskiy, 1992) — Soviet alternative with envelope-mode-per-tick instrument model |
| 5 | [protracker.md](protracker.md) | **Pro Tracker 1/2/3** (Golden Disk Corp., 1995–1997) — the format-defining lineage that produced `.PT3` |
| 6 | [vortex_tracker.md](vortex_tracker.md) | **Vortex Tracker II** (Bulba, 2000+) — the de facto PC-based PT3 editor |
| 7 | [arkos_tracker.md](arkos_tracker.md) | **Arkos Tracker 2/3** (Targhan, 2003+) — modern cross-platform AY tracker |
| 8 | [pt3_format.md](pt3_format.md) | **PT3 module format** — byte-level binary specification |
| 9 | [psg_format.md](psg_format.md) | **PSG register dump format** — the universal pre-rendered dump |

---

## Quick Format Reference

The two dominant file extensions a new composer will encounter:

- **`.PT3`** — the module format produced by Vortex Tracker II. Used by virtually every ZX game/demo that has music. See [PT3 Format](pt3_format.md).
- **`.AKG`** — the player-coupled format produced by Arkos Tracker 3. Used by most modern Western homebrew. See [Arkos Tracker](arkos_tracker.md).

For archival: `.AY` (universal container including the player routine). For cross-platform playback: `.PSG` or `.YM`. See [AY Music Formats](ay_music_formats.md) for the full family.

---

## Cross-References

- [Sound Hardware](../hardware/README.md) — the chips these formats drive (AY-3-8912, TurboSound, etc.)
- [Player Routines](../players/README.md) — how modules are converted to register writes at runtime
- [Synthesis Techniques](../synthesis/README.md) — the underlying sound generation methods
- [Sound Section Index](../README.md) — full sound catalog
