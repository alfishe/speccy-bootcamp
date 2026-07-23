[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# I/O — Storage Media Formats

This directory covers **storage media formats** — tape, floppy disk, hard disk, and SD card. These are formats that represent data laid out on a physical (or emulated) medium, which the Spectrum loads through its tape input, floppy controller, or IDE/SD interface.

Machine-state capture formats (snapshots and replay) live in a sibling directory: [../snapshots/](../snapshots/README.md). The split reflects a real distinction: a .TAP file is a sequence of pulses that the Spectrum's tape subsystem decodes, whereas a .SNA file is a frozen image of the machine itself. See the [snapshots README](../snapshots/README.md) for that side of the I/O picture.

## Article Index

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

### Floppy Disk ✅ 13 articles complete

The floppy subsystem — the IBM 3740 physical layer shared by every Spectrum disk, four mutually-incompatible logical formats (TR-DOS, +3DOS, CP/M, MGT/Opus), and the eight disk-image file formats (`.TRD`, `.SCL`, `.DSK`, `.EDSK`, `.FDI`, `.MGT`, `.UDI`, `.SCP`) used to capture them.

**Physical layer (start here):**

| File | Topic | Lines |
|------|-------|-------|
| [mfm_encoding.md](mfm_encoding.md) | **MFM signal layer** — IBM 3740 sector format, MFM bit-level encoding, address/data marks, CRC16 (`0x1021`), gap structure (GAP1–GAP4), 250 kbit/s data rate, FM vs MFM, clock-bit patterns, weak bits, PLL data separator | 786 |
| [fdc_vg93.md](fdc_vg93.md) | **WD1793 / KR1818VG93 floppy controller chip** — 4-register file (Status/Cmd, Track, Sector, Data), Type I/II/III/IV commands, command execution phases, status register bits, Soviet KR1818VG93 clone, undocumented features, turbo mods | 1051 |

**Hardware interfaces:**

| File | Topic | Lines |
|------|-------|-------|
| [beta_disk_interface.md](beta_disk_interface.md) | **Beta Disk Interface / Beta 128** hardware (Soviet standard) — WD1793 controller, port map (`#1F`/`#3F`/`#5F`/`#7F`/`#FF`), TR-DOS ROM bank switching, drive/motor/side control, cable pinout, variants, modern replacements | 620 |
| [plus3_floppy.md](plus3_floppy.md) | **Spectrum +3 floppy hardware** — WD1772-PH controller, port map (`#1F`/`#3F`/`#5F`/`#7F`/`#FF`/`#7FFD`), drive geometry (80×2×9×512 = 720 KB), cable pinout, internal 3" Hitachi HFD-305S, modern replacements | 671 |

**Logical disk formats (4 mutually-incompatible formats):**

| File | Topic | Lines |
|------|-------|-------|
| [trd_disk_format.md](trd_disk_format.md) | **TR-DOS logical disk format** (Soviet standard, 800 KB DSDD-10) — 128 file entries × 16 bytes, sector-based allocation, file types (B/C/D/#), 8-byte disk descriptor | 699 |
| [plus3_dos_format.md](plus3_dos_format.md) | **+3DOS logical disk format** (CP/M 2.2 derivative, 720 KB DSDD-9) — 32-byte directory entries, 1 KB allocation blocks, extents (EX/S2/RC), DPB (SPT=36, DSM=714), "reverse side" trick | 606 |
| [cpm_disk_format.md](cpm_disk_format.md) | **CP/M 2.2 disk format** on Spectrum family — BIOS/BDOS/CCP/TPA, FCB (33-byte), DPB, BDOS system calls (`CALL 0x0005`), +3 CP/M, ATM Turbo CP/M, Sprinter CP/M | 545 |
| [opus_discovery_format.md](opus_discovery_format.md) | **Opus Discovery / MGT disk format** (UK standard, 800 KB DSDD-10) — WD1770 controller, port map (`#E3`/`#E7`/`#1F`), 256-byte directory entries, per-file sector bitmap, linked-list sector chaining, big-endian sector count | 595 |

**Disk-image file formats (8 formats, sector-level and flux-level):**

| File | Topic | Lines |
|------|-------|-------|
| [trd_scl_formats.md](trd_scl_formats.md) | **.TRD** and **.SCL** image formats — TR-DOS containers (`.TRD` = raw sector dump; `.SCL` = file-level backup) | 484 |
| [dsk_fdi_formats.md](dsk_fdi_formats.md) | **.DSK**, **.EDSK**, and **.FDI** image formats — CP/M / +3DOS / Opus containers, with worked examples | 479 |
| [udi_format.md](udi_format.md) | **.UDI** universal flux-level image format — preserves every magnetic transition | 347 |
| [scp_format.md](scp_format.md) | **.SCP** SuperCard Pro flux-level image format — gold-standard preservation format | 378 |

**Overview (read this first if you're new to floppy):**

| File | Topic | Lines |
|------|-------|-------|
| [disk_format_overview.md](disk_format_overview.md) | **Top-level comparison** — IBM 3740 physical layer, 4 logical formats side-by-side, 8 disk image formats at a glance, decision tree for choosing the right format | 488 |

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

**Tape sub-section: ✅ COMPLETE (6/6 articles).**
**Floppy sub-section: ✅ COMPLETE (13/13 articles).**

The remaining sub-section (Hard Disk / SD) is planned but not yet written. See [PLAN.md](../../PLAN.md) for the full catalog and prioritisation.

## Reading Order

**Tape (signal representation, hardware to preservation):**

1. [tape_interface.md](tape_interface.md) — the hardware layer: how bits physically travel through EAR/MIC.
2. [tape_format.md](tape_format.md) — the logical layer: what the bits mean (blocks, headers, checksums).
3. [tap_format.md](tap_format.md) — the simplest file format: a direct dump of logical blocks.
4. [tzx_format.md](tzx_format.md) — the comprehensive format: block types for every tape pattern.
5. [csw_format.md](csw_format.md) — the pulse-level preservation format: analog fidelity at the cost of size.
6. [pzx_format.md](pzx_format.md) — a modern structured alternative to .CSW.

**Floppy (signal → controller → hardware → logical → image formats):**

1. [disk_format_overview.md](disk_format_overview.md) — start here: a top-level comparison of every format.
2. [mfm_encoding.md](mfm_encoding.md) — the magnetic signal layer: IBM 3740 sectors, MFM, address/data marks.
3. [fdc_vg93.md](fdc_vg93.md) — the floppy controller chip: WD1793 commands, registers, status.
4. [beta_disk_interface.md](beta_disk_interface.md) — the Soviet floppy interface (WD1793 hardware).
5. [plus3_floppy.md](plus3_floppy.md) — the Western +3 floppy interface (WD1772-PH hardware).
6. [trd_disk_format.md](trd_disk_format.md) — the Soviet logical format (TR-DOS).
7. [plus3_dos_format.md](plus3_dos_format.md) — the UK logical format (+3DOS, CP/M derivative).
8. [cpm_disk_format.md](cpm_disk_format.md) — the standard CP/M logical format.
9. [opus_discovery_format.md](opus_discovery_format.md) — the UK Opus/MGT logical format.
10. [trd_scl_formats.md](trd_scl_formats.md) — TR-DOS disk-image formats (`.TRD`, `.SCL`).
11. [dsk_fdi_formats.md](dsk_fdi_formats.md) — CP/M/+3DOS/Opus disk-image formats (`.DSK`, `.EDSK`, `.FDI`).
12. [udi_format.md](udi_format.md) — flux-level preservation format (`.UDI`).
13. [scp_format.md](scp_format.md) — flux-level preservation format (`.SCP`).

The tape articles cover state-over-time (the loading process). The companion [snapshots sub-section](../snapshots/README.md) covers state-at-an-instant. Together with the floppy and planned HDD/SD articles, this directory covers the full Spectrum storage media ecosystem.
