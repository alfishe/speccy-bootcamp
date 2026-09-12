[← Home](../../README.md) · [Sound](../README.md) · [Trackers & Formats](README.md)

# Trackers, Editors & Formats

> The software ecosystem for creating and storing AY/YM music — from the original Sound Tracker (1990) through modern cross-platform tools like Arkos Tracker 3. 35 years of chiptune tooling.

---

## Quick Reference

| If you want... | Read this |
|----------------|-----------|
| Understand the tracker timeline | [tracker_history.md](tracker_history.md) |
| Know all file formats | [ay_music_formats.md](ay_music_formats.md) |
| Use Vortex Tracker II | [vortex_tracker.md](vortex_tracker.md) |
| Use Arkos Tracker | [arkos_tracker.md](arkos_tracker.md) |
| Parse PT3 files | [pt3_format.md](pt3_format.md) |

---

## Articles

The nine articles are best read in chronological order: history first for context, then the format catalog, then the foundational on-Spectrum editors, then the PC-generation tools, then the binary format references.

### History & Catalog

| Article | Description |
|---------|-------------|
| [tracker_history.md](tracker_history.md) | **30-year history** — beeper trackers (1985), Sound Tracker (1990), Pro Tracker lineage, VTII/Arkos split, modern cross-platform tools |
| [ay_music_formats.md](ay_music_formats.md) | **Master format catalog** — every AY/YM file format (`.PT3`, `.PSG`, `.YM`, `.AY`, `.AKG`, etc.): modules, dumps, containers, modern embedded |

### On-Spectrum Editors (1990–1997)

| Article | Description |
|---------|-------------|
| [sound_tracker.md](sound_tracker.md) | **Sound Tracker 1.1** (Bzyk, 1990) — the first AY grid editor, established the pattern/sample/ornament paradigm |
| [asc_sound_master.md](asc_sound_master.md) | **ASC Sound Master** (Sendetskiy, 1992) — Soviet alternative with envelope-mode-per-tick instruments |
| [protracker.md](protracker.md) | **Pro Tracker 1/2/3** (Golden Disk Corp., 1995–1997) — the format-defining lineage that produced `.PT3` |

### PC-Based Editors (2000–present)

| Article | Description |
|---------|-------------|
| [vortex_tracker.md](vortex_tracker.md) | **Vortex Tracker II** (Bulba, 2000+) — de facto PC-based PT3 editor, universal import, TurboSound support |
| [arkos_tracker.md](arkos_tracker.md) | **Arkos Tracker 2/3** (Targhan, 2003+) — modern cross-platform tracker, AKG/AKM/AKY players, digidrum support |

### Binary Format Specifications

| Article | Description |
|---------|-------------|
| [pt3_format.md](pt3_format.md) | **PT3 module format** — byte-level binary specification: header, position table, ornaments, samples, patterns |
| [psg_format.md](psg_format.md) | **PSG register dump** — universal pre-rendered format, frame structure, variants (`.YM`, `.VTX`) |

---

## Quick Format Reference

| Extension | Type | Editor | Use case |
|-----------|------|--------|----------|
| `.PT3` | Module | Vortex Tracker II | Soviet scene, most ZX games/demos |
| `.AKG` | Module | Arkos Tracker 3 | Modern Western homebrew |
| `.AKM` | Module | Arkos Tracker 3 | Size-optimized intros |
| `.AKY` | Module | Arkos Tracker 3 | Speed-optimized demos |
| `.PSG` | Dump | Any | Cross-platform playback |
| `.YM` | Dump | Any | Atari ST scene, compressed |
| `.AY` | Container | Any | Universal archive with player |

For new composers:
- **`.PT3`** via [Vortex Tracker II](vortex_tracker.md) — standard for Soviet scene compatibility
- **`.AKG`** via [Arkos Tracker 3](arkos_tracker.md) — standard for modern Western homebrew

---

## Cross-References

### Related Sound Topics

- [Sound Hardware](../hardware/README.md) — The chips these formats drive (AY-3-8912, TurboSound)
- [Player Routines](../players/README.md) — How modules become register writes at runtime
- [Synthesis Techniques](../synthesis/README.md) — The underlying sound generation methods

### External Resources

- [Vortex Tracker II](http://vtii.seban.ru/) — Official download
- [Arkos Tracker 2](https://www.julien-nevo.com/arkostracker/) — Official site
- [zxart.ee](https://zxart.ee/eng/music/) — Largest ZX music database
- [ZXTUNES](https://zxtunes.com/) — Online PT3/AY player and archive
