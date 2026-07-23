[← Home](../../README.md) · [I/O](../) · [Snapshots](README.md)

# I/O — Snapshots & Replay

This directory covers **machine-state capture** formats — snapshots (which record the Spectrum's state at a single instant) and replay (which records input over time). These are conceptually distinct from [storage media formats](../storage/README.md) (tape, floppy, HDD, SD): a snapshot is a frozen image of the machine itself, not data laid out on a physical medium.

The split reflects how these formats are used. A .SNA or .Z80 file is the typical distribution format for Spectrum software today — load it into any emulator and you are instantly inside the program. A .TAP or .TRD file, by contrast, represents data that must be loaded *through* the Spectrum's tape or floppy subsystem. Snapshot and replay formats sit alongside storage formats in the broader I/O picture, but they answer a different question: not "what is on the disk?" but "what is the machine doing?".

## Article Index ✅ 4 articles complete

| File | Topic | Lines |
|------|-------|-------|
| [sna_format.md](sna_format.md) | **.SNA snapshot format** — the original 1992 format by Arnt Gulbrandsen (JPP emulator). 48K (49179 bytes) and 128K (131103 bytes) variants, the 27-byte header, the PC-on-the-stack trick, extension header for 128K, loader implementation, limitations (no AY, no clone state) | 549 |
| [z80_format.md](z80_format.md) | **.Z80 snapshot format** — the 1994 "rich" format by Glen Lleston (Z80 emulator). Three versions: v1 (48K only, 30-byte header), v2 (128K, 23-byte extension), v3 (clones/AY/peripherals, 54-byte extension). Hardware ID system (0–26+), RLE compression via 0xED 0xED marker, per-page storage | 671 |
| [szx_format.md](szx_format.md) | **.SZX snapshot format** — the modern chunk-based (IFF-like) format by César Hernández Bauset (ZEsarUX, ~2005). 8-byte file header ("ZXST" + version), standard chunks (Z80R, RAM, AY16, CFGR, BETA, PLSB, ZXRG, COPR, DMA, etc.), extensibility via skip-unknown-chunks rule, hardware IDs 0–28+ including Next and TS-Conf | 640 |
| [rzx_format.md](rzx_format.md) | **.RZX replay format** — the 2001 input-recording format by the RZX Working Group (Andrew Broad, Phillip Kendall, et al.). Block-based (Creator/Snapshot/Input/Sign), records IN port reads rather than key presses (hardware-independent), embedded initial snapshot, cryptographic signing for the RZX Archive, T-states-per-frame for cycle-accurate replay | 629 |

## Status

**Snapshots & Replay sub-section: ✅ COMPLETE (4/4 articles).**

## Reading Order

**From simplest to most capable, then to the alternative paradigm:**

1. [sna_format.md](sna_format.md) — the simplest format, foundational concepts (header layout, PC restoration via stack, limitations). Start here.
2. [z80_format.md](z80_format.md) — the most widely-used "rich" format; builds on .SNA concepts, adds compression and 128K/clone support.
3. [szx_format.md](szx_format.md) — the modern chunk-based approach; introduces IFF-like extensibility and per-peripheral chunks.
4. [rzx_format.md](rzx_format.md) — a different paradigm: recording input over time rather than state at an instant.

## Companion Sub-sections

- **[../storage/](../storage/README.md)** — tape, floppy disk, hard disk, and SD card formats. These are the *media* formats that snapshots sidestep: instead of representing a tape or disk that the Spectrum must load through its tape/floppy subsystem, a snapshot captures the result *after* loading.
- **[../peripherals/](../peripherals/README.md)** — input devices (joysticks, etc.) whose state .RZX recordings capture as IN port reads.
- **[../../08_reverse_engineering/](../../08_reverse_engineering/)** — snapshot files are commonly analysed during reverse engineering; the planned `snapshot_repair.md` article covers fixing corrupted .SNA/.Z80 files.
