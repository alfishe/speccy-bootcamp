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

### Tape *(planned — not yet written)*

| File | Topic |
|------|-------|
| `tape_interface.md` | EAR/MIC hardware: pilot tone, sync pulses, data encoding, Turbo LOAD speed-ups |
| `tape_format.md` | Tape data format: blocks (header + data), checksums, baud rates (1500–3600 baud) |
| `tap_format.md` | .TAP file format: pulse-level encoding, block structure |
| `tzx_format.md` | .TZX file format: complete specification, all block types, turbo loading, custom loaders |
| `csw_format.md` | .CSW (Compressed Square Wave): tape format for preservation |
| `pzx_format.md` | .PZX: alternative tape format |

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

The remaining three sub-sections (Tape, Floppy Disk, Hard Disk/SD) are planned but not yet written. See [PLAN.md](../../PLAN.md) for the full catalog and prioritisation.

## Reading Order

If you are new to Spectrum snapshots, read in this order:

1. [sna_format.md](sna_format.md) — the simplest format, foundational concepts (header layout, PC restoration, limitations).
2. [z80_format.md](z80_format.md) — the most widely-used "rich" format; builds on .SNA concepts.
3. [szx_format.md](szx_format.md) — the modern chunk-based approach; introduces IFF-like extensibility.
4. [rzx_format.md](rzx_format.md) — a different paradigm: recording input over time rather than state at an instant.

The four formats together cover the full design space of Spectrum state capture and reproduction.
