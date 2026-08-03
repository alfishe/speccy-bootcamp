[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# I/O — Storage Media Formats

This directory covers **storage media formats** — tape, floppy disk, hard disk, and SD card. These are formats that represent data laid out on a physical (or emulated) medium, which the Spectrum loads through its tape input, floppy controller, or IDE/SD interface.

Machine-state capture formats (snapshots and replay) live in a sibling directory: [../snapshots/](../snapshots/README.md). The split reflects a real distinction: a .TAP file is a sequence of pulses that the Spectrum's tape subsystem decodes, whereas a .SNA file is a frozen image of the machine itself. See the [snapshots README](../snapshots/README.md) for that side of the I/O picture.

## Article Index

### Tape ✅ 6 articles complete

The tape subsystem — hardware interface, logical data format, and the five major tape file formats (.TAP, .TZX, .CSW, .PZX).

| File | Topic | Lines |
|------|-------|-------|
| [tape_interface.md](tape_interface.md) | **Tape interface hardware** — EAR/MIC circuits, ULA Schmitt trigger, port `#FE` bit layout (bits 0–4 keyboard, bit 6 EAR), ROM routines (SA-BYTES `#04C6`, LD-BYTES `#0556`, LD-EDGE-1/2 `#05E3`), pilot tone (8063 pulses × 2168 T-states), sync pulses (667 + 735), bit encoding (0 = 2×855, 1 = 2×1710), ~1500 baud standard rate, XOR checksum, turbo loaders (Speedlock/Alcatraz/Bleepload), 48K vs Issue 2/3 differences | 767 |
| [tape_format.md](tape_format.md) | **Tape data format (logical layer)** — two-layer model (hardware pulses + logical blocks), 17-byte header structure (block type + 10-char filename + data length + 2 params), four block types (Program/Number Array/Character Array/Code), parameter semantics (auto-run line ≥ `#8000` = no run; Code start address), XOR checksum (~99.6% detection), multi-block files, Screen$ convention | 693 |
| [tap_format.md](tap_format.md) | **.TAP file format** — Thomas Schreiber's 1996 minimal format (X128 emulator). Just sequence of blocks: 2-byte little-endian length + data, no file header, no metadata, no compression. Cannot represent turbo loaders. Warp playback (emulators inject bytes directly). Complete reader/writer C code, worked hex example for 6-byte RedBordr program (31-byte .TAP) | 889 |
| [tzx_format.md](tzx_format.md) | **.TZX file format** — Tomaz Kac's 1996 comprehensive format. 10-byte "ZXTape!" header + major/minor version. 30+ block types (0x10 standard, 0x11 turbo with 8 timing params, 0x12 pure tone, 0x13 pulse sequence, 0x14 pure data, 0x15 direct recording, 0x20 silence, 0x21/0x22 group, 0x23 jump, 0x24 loop, 0x30 text, 0x31 message, 0x32 archive info, 0x33 hardware type, 0x5A glue). Extension blocks 0x80–0xFF. Current spec v1.13 (2008). Format of choice for preservation | 1081 |
| [csw_format.md](csw_format.md) | **.CSW Compressed Square Wave** — Simon Owen's 2001 pulse-level preservation format. Stores pulse widths in samples (typically 44100 Hz), RLE compression (1–255 = single byte; 0x00 + 2-byte count + 2-byte width = RLE). v1 (small header) vs v2 (32-byte structured header with metadata extension). For analog protections and raw captures. 20–50 KB per 48K program | 551 |
| [pzx_format.md](pzx_format.md) | **.PZX chunk-based format** — Fredrik Öhrström's 2010 format (Unreal Speccy). IFF-like 8-byte file header "PZXT" + chunks (PULS/TEXT/INFO/TIME/PAUS/STOP). PULS stores 16-bit T-state pulse widths directly (cycle-exact, no sample-rate conversion). Skip-unknown-chunks rule for extensibility. ~100 KB per 48K program. Less widely supported than .TZX | 566 |

### Floppy Disk ✅ 13 articles complete

The floppy subsystem — the IBM 3740 physical layer shared by every Spectrum disk, four mutually-incompatible logical formats (TR-DOS, +3DOS, CP/M, MGT/Opus), and the eight disk-image file formats (`.TRD`, `.SCL`, `.DSK`, `.EDSK`, `.FDI`, `.MGT`, `.UDI`, `.SCP`) used to capture them.

**Physical layer (start here):**

| File | Topic | Lines |
|------|-------|-------|
| [mfm_encoding.md](mfm_encoding.md) | **MFM signal layer** — IBM 3740 sector format, MFM bit-level encoding, address/data marks, CRC16 (`0x1021`), gap structure (GAP1–GAP4), 250 kbit/s data rate, FM vs MFM, clock-bit patterns, weak bits, PLL data separator | 771 |
| [fdc_vg93.md](fdc_vg93.md) | **WD1793 / KR1818VG93 floppy controller chip** — 4-register file (Status/Cmd, Track, Sector, Data), Type I/II/III/IV commands (Type I = `T h V r1 r0`, Type II = `m S E C a0`, Type IV force-interrupt conditions per datasheet), status bits with per-type semantics and signal source (NOT READY, HEAD LOADED, SEEK ERROR/RNF, LOST DATA), INTRQ/DRQ semantics with T-state byte windows (114 MFM / 228 FM), READ ADDRESS sector length code (`128 << code`), datasheet + unreal-ng cross-verified, Soviet KR1818VG93 clone, WD179x variant table | 1074 |

**Hardware interfaces:**

| File | Topic | Lines |
|------|-------|-------|
| [beta_disk_interface.md](beta_disk_interface.md) | **Beta Disk Interface / Beta 128** hardware (Soviet standard) — WD1793 controller, port map (`#1F`/`#3F`/`#5F`/`#7F`/`#FF`), `#FF` bit layout verified across the Soviet clone matrix (Pentagon/Scorpion/Kay/ATM Turbo/Profi/Leningrad), TR-DOS ROM bank-switching mechanism (M1 + `#3D00–#3DFF` trigger, fixes the persistent banking-error myth), cable pinout, KR1818VG93 second-sourcing, TR-DOS 5.x ROM variants, custom turbo loaders, MAGIC button, modern replacements | 947 |
| [plus3_floppy.md](plus3_floppy.md) | **Spectrum +3 floppy hardware** — WD1772-PH controller, port map (`#1F`/`#3F`/`#5F`/`#7F`/`#FF`/`#7FFD`), drive geometry (80×2×9×512 = 720 KB), cable pinout, internal 3" Hitachi HFD-305S, modern replacements | 652 |

**Logical disk formats (4 mutually-incompatible formats):**

| File | Topic | Lines |
|------|-------|-------|
| [trd_disk_format.md](trd_disk_format.md) | **TR-DOS logical disk format** (Soviet standard, 800 KB DSDD-10) — 128 file entries × 16 bytes, sector-based allocation, file types (B/C/D/#), 8-byte disk descriptor | 680 |
| [plus3_dos_format.md](plus3_dos_format.md) | **+3DOS logical disk format** (CP/M 2.2 derivative, 720 KB DSDD-9) — 32-byte directory entries, 1 KB allocation blocks, extents (EX/S2/RC), DPB (SPT=36, DSM=714), "reverse side" trick | 588 |
| [cpm_disk_format.md](cpm_disk_format.md) | **CP/M 2.2 disk format** on Spectrum family — BIOS/BDOS/CCP/TPA, FCB (33-byte), DPB, BDOS system calls (`CALL 0x0005`), +3 CP/M, ATM Turbo CP/M, Sprinter CP/M | 528 |
| [opus_discovery_format.md](opus_discovery_format.md) | **Opus Discovery / MGT disk format** (UK standard, 800 KB DSDD-10) — WD1770 controller, port map (`#E3`/`#E7`/`#1F`), 256-byte directory entries, per-file sector bitmap, linked-list sector chaining, big-endian sector count | 578 |

**Disk-image file formats (8 formats, sector-level and flux-level):**

| File | Topic | Lines |
|------|-------|-------|
| [trd_scl_formats.md](trd_scl_formats.md) | **.TRD** and **.SCL** image formats — TR-DOS containers (`.TRD` = raw sector dump; `.SCL` = file-level backup) | 469 |
| [dsk_fdi_formats.md](dsk_fdi_formats.md) | **.DSK**, **.EDSK**, and **.FDI** image formats — CP/M / +3DOS / Opus containers, with worked examples | 464 |
| [udi_format.md](udi_format.md) | **.UDI** universal flux-level image format — preserves every magnetic transition | 333 |
| [scp_format.md](scp_format.md) | **.SCP** SuperCard Pro flux-level image format — gold-standard preservation format | 364 |

**Overview (read this first if you're new to floppy):**

| File | Topic | Lines |
|------|-------|-------|
| [disk_format_overview.md](disk_format_overview.md) | **Top-level comparison** — IBM 3740 physical layer, 4 logical formats side-by-side, 8 disk image formats at a glance, decision tree for choosing the right format | 472 |

### Hard Disk / SD ✅ 6 articles complete

The mass-storage subsystem — the IDE and SD interfaces that gave the Spectrum megabyte-to-gigabyte capacity, the image formats that capture them, and the FAT/IS-DOS filesystems that organize them. Three generations of hardware (IDE → SD) with a common filesystem abstraction.

**Overview (start here):**

| File | Topic | Lines |
|------|-------|-------|
| [hdd_overview.md](hdd_overview.md) | **Top-level overview** — three generations (floppy → IDE → SD), why HDD mattered for the Soviet scene, modern landscape, cross-references | 175 |

**Hardware interfaces:**

| File | Topic | Lines |
|------|-------|-------|
| [ide_interface.md](ide_interface.md) | **IDE / PATA interfaces** — generic IDE block diagram, 40-pin connector pinout, port maps compared (DivIDE/SMUC/Nemo/ZC/ATM/KAY), Z80 read loop sketch | 385 |
| [divide_divmmc.md](divide_divmmc.md) | **DivIDE / DivMMC hardware** — board architecture, NMI boot, conmem/mapram paging, divman/divese TR-DOS image emulation, card setup workflow (hardware companion to esxdos.md) | 261 |
| [sd_interface.md](sd_interface.md) | **SD card interfaces (SD-SPI)** — SPI command frame, 5-step init handshake (CMD0/CMD8/CMD55+ACMD41/CMD58), Z80 bit-bang sketch, port maps (DivMMC/ZXMMC/Next/ZC), throughput table | 295 |

**Filesystem and image formats:**

| File | Topic | Lines |
|------|-------|-------|
| [hdd_partitioning.md](hdd_partitioning.md) | **Partitioning and filesystems** — MBR + 4-entry partition table, FAT12/16/32, BPB fields, 32-byte directory entries, LFN, cluster allocation, IS-DOS alternative, multi-partition layouts | 378 |
| [hdf_mgt_formats.md](hdf_mgt_formats.md) | **Image formats** (.HDF / .IMG / .MGT / .VHD) — raw vs headered HDF, the four-names-for-same-thing problem, loopback mounting, sparse/compression, per-OS card creation commands | 217 |

---

## Status

**Tape sub-section: ✅ COMPLETE (6/6 articles).**
**Floppy sub-section: ✅ COMPLETE (13/13 articles).**
**Hard Disk / SD sub-section: ✅ COMPLETE (6/6 articles).**

All three sub-sections of the storage media directory are now complete (25 articles total). See [PLAN.md](../../PLAN.md) for the full catalog.

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

**Hard Disk / SD (overview → hardware → filesystem → image formats):**

1. [hdd_overview.md](hdd_overview.md) — start here: the evolution floppy → IDE → SD, and the unifying FAT abstraction.
2. [ide_interface.md](ide_interface.md) — the IDE protocol: 40-pin connector, port maps for every interface, Z80 read loop.
3. [divide_divmmc.md](divide_divmmc.md) — the DivIDE/DivMMC hardware: NMI boot, ESXDOS, virtual-floppy emulation.
4. [sd_interface.md](sd_interface.md) — the SD-SPI protocol: command frame, init handshake, port maps for every interface.
5. [hdd_partitioning.md](hdd_partitioning.md) — what's inside the image: MBR, FAT16/32, BPB, directory entries, LFN, IS-DOS.
6. [hdf_mgt_formats.md](hdf_mgt_formats.md) — the image formats themselves: .HDF, .IMG, .VHD, and the raw-image convention.

The tape articles cover state-over-time (the loading process). The companion [snapshots sub-section](../snapshots/README.md) covers state-at-an-instant. Together with the floppy and HDD/SD articles, this directory covers the full Spectrum storage media ecosystem.
