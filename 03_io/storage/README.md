[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# I/O — Storage

This directory covers tape, floppy disk, hard disk, SD card, and snapshot/replay formats — every form of persistent state and input/output storage used by the ZX Spectrum ecosystem from 1982 to the present day.

## Article Index

### Snapshots & Replay ✅ 4 articles complete

The snapshot/replay formats — how Spectrum machine state is saved, shared, and reproduced.

| File | Topic | Lines |
|------|-------|-------|
| [sna_format.md](sna_format.md) | **.SNA snapshot format** — the original 1992 format by Arnt Gulbrandsen (JPP emulator). 48K (49179 bytes) and 128K (131103 bytes) variants, the 27-byte header, the PC-on-the-stack trick, extension header for 128K, loader implementation, limitations (no AY, no clone state) | 548 |
| [z80_format.md](z80_format.md) | **.Z80 snapshot format** — the 1994 "rich" format by Glen Lleston (Z80 emulator). Three versions: v1 (48K only, 30-byte header), v2 (128K, 23-byte extension), v3 (clones/AY/peripherals, 54-byte extension). Hardware ID system (0–26+), RLE compression via 0xED 0xED marker, per-page storage | 670 |
| [szx_format.md](szx_format.md) | **.SZX snapshot format** — the modern chunk-based (IFF-like) format by César Hernández Bauset (ZEsarUX, ~2005). 8-byte file header ("ZXST" + version), standard chunks (Z80R, RAM, AY16, CFGR, BETA, PLSB, ZXRG, COPR, DMA, etc.), extensibility via skip-unknown-chunks rule, hardware IDs 0–28+ including Next and TS-Conf | 639 |
| [rzx_format.md](rzx_format.md) | **.RZX replay format** — the 2001 input-recording format by the RZX Working Group (Andrew Broad, Phillip Kendall, et al.). Block-based (Creator/Snapshot/Input/Sign), records IN port reads rather than key presses (hardware-independent), embedded initial snapshot, cryptographic signing for the RZX Archive, T-states-per-frame for cycle-accurate replay | 628 |

### Tape ✅ 6 articles complete

The tape subsystem — hardware interface, logical data format, and the five major tape file formats (.TAP, .TZX, .CSW, .PZX).

| File | Topic | Lines |
|------|-------|-------|
| [tape_interface.md](tape_interface.md) | **Tape interface hardware** — EAR/MIC circuits, ULA Schmitt trigger, port `#FE` bit layout (bits 0–4 keyboard, bit 6 EAR), ROM routines (SA-BYTES `#04C6`, LD-BYTES `#0556`, LD-EDGE-1/2 `#05E3`), pilot tone (8063 pulses × 2168 T-states), sync pulses (667 + 735), bit encoding (0 = 2×855, 1 = 2×1710), ~1500 baud standard rate, XOR checksum, turbo loaders (Speedlock/Alcatraz/Bleepload), 48K vs Issue 2/3 differences | 782 |
| [tape_format.md](tape_format.md) | **Tape data format (logical layer)** — two-layer model (hardware pulses + logical blocks), 17-byte header structure (block type + 10-char filename + data length + 2 params), four block types (Program/Number Array/Character Array/Code), parameter semantics (auto-run line ≥ `#8000` = no run; Code start address), XOR checksum (~99.6% detection), multi-block files, Screen$ convention | 706 |
| [tap_format.md](tap_format.md) | **.TAP file format** — Thomas Schreiber's 1996 minimal format (X128 emulator). Just sequence of blocks: 2-byte little-endian length + data, no file header, no metadata, no compression. Cannot represent turbo loaders. Warp playback (emulators inject bytes directly). Complete reader/writer C code, worked hex example for 6-byte RedBordr program (31-byte .TAP) | 902 |
| [tzx_format.md](tzx_format.md) | **.TZX file format** — Tomaz Kac's 1996 comprehensive format. 10-byte "ZXTape!" header + major/minor version. 30+ block types (0x10 standard, 0x11 turbo with 8 timing params, 0x12 pure tone, 0x13 pulse sequence, 0x14 pure data, 0x15 direct recording, 0x20 silence, 0x21/0x22 group, 0x23 jump, 0x24 loop, 0x30 text, 0x31 message, 0x32 archive info, 0x33 hardware type, 0x5A glue). Extension blocks 0x80–0xFF. Current spec v1.13 (2008). Format of choice for preservation | 1094 |
| [csw_format.md](csw_format.md) | **.CSW Compressed Square Wave** — Simon Owen's 2001 pulse-level preservation format. Stores pulse widths in samples (typically 44100 Hz), RLE compression (1–255 = single byte; 0x00 + 2-byte count + 2-byte width = RLE). v1 (small header) vs v2 (32-byte structured header with metadata extension). For analog protections and raw captures. 20–50 KB per 48K program | 564 |
| [pzx_format.md](pzx_format.md) | **.PZX chunk-based format** — Fredrik Öhrström's 2010 format (Unreal Speccy). IFF-like 8-byte file header "PZXT" + chunks (PULS/TEXT/INFO/TIME/PAUS/STOP). PULS stores 16-bit T-state pulse widths directly (cycle-exact, no sample-rate conversion). Skip-unknown-chunks rule for extensibility. ~100 KB per 48K program. Less widely supported than .TZX | 579 |

### Floppy Disk *(planned — not yet written)*

| File | Topic |
|------|-------|
| `beta_disk_interface.md` | Beta Disk Interface: WD1793 / KR1818VG93 FDC, TR-DOS integration, disk format |
| `fdc_vg93.md` | KR1818VG93 / WD1793 FDC deep dive: registers, commands, timing, undocumented features, turbo mods |
| `plus3_floppy.md` | +3 internal floppy: WD1772-based, +3 DOS format, drive geometry |
| `trd_disk_format.md` | TR-DOS disk format: directory structure, file types (B, C, D, M, #), disk parameters (80 tracks × 10 sectors) |
| `trd_scl_formats.md` | .TRD / .SCL disk image formats |
| `dsk_fdi_formats.md` | .DSK / .EDSK / .FDI disk image formats (preservation-level) |
| `udi_format.md` | .UDI universal disk image format |
| `scp_format.md` | .SCP (SuperCard Pro) flux-level preservation format |
| `mfm_encoding.md` | MFM encoding: how data is recorded on floppy, sync marks, address marks |

### Hard Disk / SD *(planned — not yet written)*

| File | Topic |
|------|-------|
| `hdd_overview.md` | HDD on Spectrum: evolution from floppy to IDE to SD card, why HDD mattered for the Soviet scene |
| `ide_interface.md` | IDE interfaces: DivIDE, SMUC, Nemo IDE, Z-Controller, KAY IDE — hardware comparison, port maps, pinouts |
| `divide_divmmc.md` | DivIDE / DivMMC: IDE hard disk + ESXDOS, FAT file system, pocket-level storage |
| `sd_interface.md` | SD card interfaces: DivMMC, ZXMMC, Next SD card, Z-Controller SD |
| `hdf_mgt_formats.md` | .HDF / .MGT / .IMG hard disk and disk image formats |
| `hdd_partitioning.md` | HDD partitioning and filesystems: FAT16/FAT32 on DivIDE, IS-DOS partitions, partition tables |

---

## Status

**Snapshots & Replay sub-section: ✅ COMPLETE (4/4 articles).**
**Tape sub-section: ✅ COMPLETE (6/6 articles).**

The remaining two sub-sections (Floppy Disk, Hard Disk/SD) are planned but not yet written. See [PLAN.md](../../PLAN.md) for the full catalog and prioritisation.

## Reading Order

**Snapshots & Replay (state at an instant):**

1. [sna_format.md](sna_format.md) — the simplest format, foundational concepts (header layout, PC restoration, limitations).
2. [z80_format.md](z80_format.md) — the most widely-used "rich" format; builds on .SNA concepts.
3. [szx_format.md](szx_format.md) — the modern chunk-based approach; introduces IFF-like extensibility.
4. [rzx_format.md](rzx_format.md) — a different paradigm: recording input over time rather than state at an instant.

**Tape (signal representation, hardware to preservation):**

1. [tape_interface.md](tape_interface.md) — the hardware layer: how bits physically travel through EAR/MIC.
2. [tape_format.md](tape_format.md) — the logical layer: what the bits mean (blocks, headers, checksums).
3. [tap_format.md](tap_format.md) — the simplest file format: a direct dump of logical blocks.
4. [tzx_format.md](tzx_format.md) — the comprehensive format: block types for every tape pattern.
5. [csw_format.md](csw_format.md) — the pulse-level preservation format: analog fidelity at the cost of size.
6. [pzx_format.md](pzx_format.md) — a modern structured alternative to .CSW.

The snapshots cover state-at-an-instant; the tape articles cover state-over-time (the loading process). Together with the planned floppy and HDD/SD articles, they will cover the full Spectrum storage ecosystem.
