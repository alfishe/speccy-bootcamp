[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# Spectrum Floppy Disk Formats: A Comparative Overview

**Scope:** A high-level comparison of every floppy disk format used on the ZX Spectrum family and its clones — the **physical** sector layer they all share, the **four logical** file-system formats they use (TR-DOS, +3DOS, CP/M, MGT/Opus), and the **eight disk-image** file formats used to capture them today (`.TRD`, `.SCL`, `.DSK`, `.EDSK`, `.FDI`, `.MGT`, `.UDI`, `.SCP`).

This article is the **top-level index** into the floppy documentation: it does not duplicate the byte-level details covered in the dedicated articles, but instead places them side-by-side so the reader can see at a glance what each format does, where they overlap, and where they diverge.

**Audience:** Anyone trying to choose a format for a specific task — emulator authors deciding which image formats to support, demoscene coders choosing a disk for a new release, archival tool authors planning a preservation pipeline, or new Spectrum users wondering why there are so many incompatible floppy formats.

**Prerequisites:** None, beyond a general familiarity with the Spectrum. This article is intended as the **entry point** to the floppy documentation; subsequent articles drill into specific topics in depth.

**Depth:** Medium. Comparison matrices, summary tables, and references to the deep articles. No byte-level layouts here — follow the cross-references.

---

## §1. Introduction

### 1.1 Why there are so many formats

The ZX Spectrum was manufactured from 1982 to 1992 by three different companies (Sinclair, Amstrad, and the various Soviet and Russian clone makers) and supported by hundreds of third-party peripherals. Floppy-disk storage arrived on the Spectrum through at least **five independent routes**, each bringing its own controller chip, its own DOS ROM, and its own on-disk file system:

1. **The Beta Disk Interface** (Technology Research, UK; ~1984) and its Soviet clone, the **Beta 128** — used the **WD1793** controller and shipped with **TR-DOS**. This route dominated the Soviet Union and post-Soviet Russia; the standard TR-DOS disk is 800 KB DSDD with 10 sectors per track.

2. **The Opus Discovery** (Opus Supplies, UK; 1984) — used the **WD1770** controller and an 8 KB DOS ROM. It introduced the **MGT format** (named after Miles Gordon Technology, who later adopted it for the Disciple and +D interfaces and for the SAM Coupé).

3. **The MGT DISCiPLE** (1985) and **+D** (1987) — both built on the Opus Discovery's MGT format, with extended DOSes (GDOS, G+DOS). These were the standard Western Spectrum disk systems until the +3.

4. **The Spectrum +3** (Amstrad, 1987) — built-in floppy using the **WD1772-PH** controller and shipped with **+3DOS** (a CP/M 2.2 derivative by LocoScript). The standard +3 disk is 720 KB DSDD with 9 sectors per track.

5. **The Spectrum +3's CP/M mode** (Amstrad, 1987) — bundled with the +3; ran standard **CP/M 2.2** disks (interchangeable with Amstrad CPC and PCW disks).

Later Soviet clones added further variations: the **ATM Turbo** (1991) with native CP/M support and 800 KB disks; the **Sprinter** (1999) with 1.44 MB HD support; and various Pentagon/Scorpion variants with custom geometry.

The result is **four mutually incompatible logical disk formats** (TR-DOS, +3DOS, CP/M, MGT) sharing **three near-identical physical geometries** (720 KB DSDD-9sec, 800 KB DSDD-10sec, and 1.44 MB HD), captured by **eight different disk-image file formats** for archival.

### 1.2 What unifies them: the IBM 3740 standard

Despite the bewildering variety at the file-system level, **every Spectrum floppy ever made** uses the same underlying **IBM 3740 sector format** at the magnetic layer. This means:

- The same **MFM** (Modified Frequency Modulation) bit-level encoding.
- The same **address mark / data mark** sync pattern.
- The same **5-byte address field** (CHRN) and **variable data field** (128–16384 bytes, but almost always 512).
- The same **CRC16** polynomial (`0x1021`).
- The same **gap structure** (GAP1, GAP2, GAP3, GAP4).

This common physical layer is the reason a single `.SCP` flux-level image can capture any Spectrum disk, and the reason modern tools like **samdisk** can convert between disk-image formats without losing information.

The full details of the IBM 3740 / MFM physical layer are covered in [mfm_encoding.md](mfm_encoding.md).

### 1.3 Three categories of formats

This overview is organized around three categories:

| Category | Articles | What it describes |
|---|---|---|
| **Physical layer** | [mfm_encoding.md](mfm_encoding.md), [fdc_vg93.md](fdc_vg93.md) | The MFM signal, the controller chip, the sector structure. |
| **Logical layer** (4 formats) | [trd_disk_format.md](trd_disk_format.md), [plus3_dos_format.md](plus3_dos_format.md), [cpm_disk_format.md](cpm_disk_format.md), [opus_discovery_format.md](opus_discovery_format.md) | The on-disk directory, allocation scheme, file headers. |
| **Disk image layer** (8 formats) | [trd_scl_formats.md](trd_scl_formats.md), [dsk_fdi_formats.md](dsk_fdi_formats.md), [udi_format.md](udi_format.md), [scp_format.md](scp_format.md) | The file formats used on modern systems to capture and store disks. |

The reader should pick one article from each category depending on their need: physical (always [mfm_encoding.md](mfm_encoding.md)), logical (whichever DOS they're targeting), image (whichever format their emulator uses).

### 1.4 Scope of this article

This article **does not** duplicate the byte-level coverage of the dedicated articles. Instead, it provides:

- A summary of what each format is and does (§3).
- Side-by-side comparison matrices (§3.5, §5).
- A decision tree for picking the right format (§6).
- Cross-references to the dedicated articles (§7).

For the byte-level layout of any specific format, follow the corresponding link.

## §2. The Shared Physical Layer

### 2.1 The IBM 3740 sector format

Every Spectrum disk, regardless of file system, is built on the same sector structure defined by the IBM 3740 floppy standard (1973). A track is laid out as:

```
GAP4a | INDEX AM | GAP1 | sector 1 | GAP2 | sector 2 | GAP2 | ... | sector N | GAP4b
```

Each sector (`SECTn`) consists of:

- **12 bytes of `0x00`** — preamble for the PLL to lock onto.
- **3-byte sync** (`0xA1 0xA1 0xA1` in MFM, missing clock bit on each) — start of address mark.
- **1-byte address mark** (`0xFE` for sector header).
- **4-byte CHRN** — Cylinder, Head, Record (sector), Number (size code).
- **2-byte CRC16** (`0x1021` polynomial).
- **22-byte GAP** — inter-field gap.
- **12 bytes of `0x00`** — data preamble.
- **3-byte sync** — start of data mark.
- **1-byte data mark** (`0xFB` for normal data, `0xF8` for deleted).
- **N bytes of data** — 128, 256, 512, 1024, ... (size code 0–5).
- **2-byte CRC16**.
- **22-byte GAP** — post-data gap.

The size code in the CHRN determines the data field size:

| Size code | Bytes |
|---|---|
| 0 | 128 |
| 1 | 256 |
| 2 | **512** (standard for all Spectrum formats) |
| 3 | 1024 |
| 4 | 2048 |
| 5 | 4096 |
| 6 | 8192 |

Spectrum formats almost universally use size code 2 (512 bytes). The full structure of the MFM signal, including preambles, address marks, and clock-bit patterns, is covered in [mfm_encoding.md](mfm_encoding.md).

### 2.2 The three geometries

While the **sector structure** is identical across all formats, the **disk geometry** varies. Three geometries cover ~99% of Spectrum disks:

| Geometry | Cylinders | Sides | Sectors/track | Sector size | Capacity | Used by |
|---|---|---|---|---|---|---|
| **800 KB DSDD-10** | 80 | 2 | 10 | 512 | 819 200 B | TR-DOS, MGT/Opus, ATM Turbo |
| **720 KB DSDD-9** | 80 | 2 | 9 | 512 | 737 280 B | +3DOS, +3 CP/M |
| **1.44 MB HD** | 80 | 2 | 18 | 512 | 1 474 560 B | Sprinter, modern clones |

The 200 KB SSDD-10 (single-sided) was the original Opus Discovery geometry and is rarely seen today. Single-sided 40-track formats exist for early Beta Disk Interface and Opus systems but are uncommon.

### 2.3 The three controllers

Three Western Digital floppy controller (FDC) chips cover every Spectrum floppy system:

| Controller | Used by | Year | Features |
|---|---|---|---|
| **WD1793** (and its Soviet clone, KR1818VG93) | Beta Disk Interface, Beta 128, Pentagon, Scorpion | 1977 | External data separator required; +12 V / −5 V supplies. |
| **WD1770** | Opus Discovery, DISCiPLE, +D | 1983 | Internal PLL, single 5 V supply, simpler design. |
| **WD1772-PH** | Spectrum +3, +2A | 1985 | Same as WD1770 with 2 ms turbo step rate; compatible with WD1770 register-wise. |

All three chips share the **Type I/II/III/IV command structure** (see [fdc_vg93.md §4](fdc_vg93.md)) and have the same 4-register file (Status/Command, Track, Sector, Data). Code written for one controller can often be ported to another with minimal changes — the main differences are in step rate, data separator, and supply voltage.

### 2.4 Encoding density

All Spectrum floppies use **double-density MFM** at 250 kbit/s:

- **FM** (single-density) is supported by the controllers but never used for Spectrum disks.
- **MFM** (double-density) is the only encoding ever used in practice.
- **GCR** (group-coded recording, used by the Commodore 1541) is **not** used by any Spectrum format.

The data rate of 250 kbit/s gives ~6250 bytes of raw data per track (300 RPM rotation = 200 ms per revolution, 250 000 bits/s × 0.2 s = 50 000 bits = 6250 bytes). After MFM overhead (clock bits, gaps, address marks), the usable data is 5120 bytes (= 10 × 512) for a 10-sector track or 4608 bytes (= 9 × 512) for a 9-sector track.

---

## §3. The Four Logical Formats Compared

### 3.1 TR-DOS (Beta Disk Interface)

**Origin:** USSR, ~1985. **Hardware:** Beta Disk Interface / Beta 128 with WD1793 (or KR1818VG93 Soviet clone). **Disk:** 800 KB DSDD-10 (80 tracks × 2 sides × 10 sectors × 512 bytes). **Full article:** [trd_disk_format.md](trd_disk_format.md).

TR-DOS is the **Soviet standard** for Spectrum floppies. Its directory is a flat array of up to 128 file entries, each 16 bytes. Allocation is **sector-based** (each file is identified by its starting sector and length) — there is no FAT, no block abstraction, and no extents.

Key features:

- **Filename:** 8 ASCII characters + 1-character extension (1 byte encodes the file type).
- **Directory entry:** 16 bytes, with a leading "mark" byte (`0x00` = empty, `0x01` = used).
- **Allocation:** contiguous sectors starting at a fixed sector; files cannot be fragmented.
- **Disk descriptor:** sector 8 of track 0 holds an 8-byte disk descriptor (free sector count, disk label, etc.).
- **File header:** 9-byte Spectrum BASIC header stored in the first sector of BASIC/code files.
- **Variants:** TR-DOS 5.0, 5.1, 5.2, 5.3, 6.0 (the last only on Scorpion). Mostly compatible.

TR-DOS is simple, fast, and well-suited to the kind of software the Soviet Spectrum scene produced (BASIC programs, snapshots, demoscene demos). It lacks attributes, dates, and subdirectories.

### 3.2 +3DOS (Spectrum +3 / +2A)

**Origin:** UK / Amstrad, 1987 (LocoScript). **Hardware:** Spectrum +3 with WD1772-PH controller. **Disk:** 720 KB DSDD-9 (80 tracks × 2 sides × 9 sectors × 512 bytes). **Full article:** [plus3_dos_format.md](plus3_dos_format.md).

+3DOS is a **CP/M 2.2 derivative** — it uses the same 32-byte directory entry, the same allocation-block abstraction (1 KB blocks with 16 block pointers per entry), and the same extents (EX/S2/RC) as standard CP/M. The "reverse side" trick (side 1 cylinder numbering is reversed) is the +3's hardware-specific quirk.

Key features:

- **Filename:** 8 + 3 (CP/M-style), with attributes encoded in the high bits of filename and extension.
- **Directory entry:** 32 bytes, identical to CP/M 2.2.
- **Allocation:** 1 KB blocks, addressed by 16 one-byte block pointers per directory entry.
- **DPB:** standard CP/M DPB with SPT=36, DSM=714, DRM=63.
- **Empty marker:** byte 0 = `0xE5`.
- **Variants:** natively supported on +3, +2A; read-only on Sprinter.

+3DOS is interoperable with CP/M tools — a +3DOS disk can be read by any CP/M-aware utility, and vice versa for data files.

### 3.3 CP/M 2.2 (Spectrum +3 / ATM Turbo / Sprinter)

**Origin:** USA / Digital Research, 1979. **Hardware:** any Spectrum with a CP/M-capable BIOS (+3, ATM Turbo, Sprinter). **Disk:** 720 KB DSDD-9 on +3; 800 KB DSDD-10 on ATM Turbo; 1.44 MB HD on Sprinter. **Full article:** [cpm_disk_format.md](cpm_disk_format.md).

CP/M 2.2 is the **industry-standard 8-bit business OS**. The +3's CP/M mode boots from disk and provides the standard CP/M BDOS interface (`CALL 0x0005`), CCP shell, and TPA program area. The on-disk format is essentially identical to +3DOS (same DPB, same directory entry), but the running OS is full CP/M, not the +3DOS variant.

Key features:

- **FCB (File Control Block):** 33 bytes sequential, 35 bytes random. First 32 bytes mirror the directory entry format.
- **User areas 0–15:** primitive directory separation.
- **Wildcards:** `?` matches any single character; `*` matches all remaining characters.
- **System calls:** 40 BDOS functions via `CALL 0x0005`.
- **128-byte record abstraction:** CP/M I/O always works in 128-byte records, regardless of physical sector size.
- **Variants:** +3 CP/M (720 KB); ATM Turbo CP/M (800 KB); Sprinter CP/M (1.44 MB HD).

CP/M matters because it was the dominant 8-bit OS of the early 1980s — running CP/M on a Spectrum means access to thousands of business applications written for CP/M (WordStar, SuperCalc, dBase II, Microsoft BASIC, etc.).

### 3.4 MGT (Opus Discovery / DISCiPLE / +D / SAM Coupé)

**Origin:** UK / Opus Supplies (1984), MGT (1985–1989). **Hardware:** Opus Discovery with WD1770 (1984), DISCiPLE (1985), +D (1987), SAM Coupé (1989). **Disk:** 800 KB DSDD-10 (or 200/400 KB SSDD on early Opus). **Full article:** [opus_discovery_format.md](opus_discovery_format.md).

MGT is the **Western UK standard** for Spectrum floppies. It is neither CP/M-like (no FCB) nor TR-DOS-like (no flat sector list). Instead, it uses **256-byte directory entries** with a per-file **sector bitmap** and a **linked-list sector chain** (the last 2 bytes of every file sector point to the next sector).

Key features:

- **Filename:** 10 ASCII characters (no separate extension — type byte separate).
- **Directory entry:** 256 bytes, including a 195-byte per-file sector bitmap.
- **Allocation:** linked-list sectors (each sector holds 510 bytes of data + 2 bytes pointer).
- **Track encoding:** side bit encoded in MSB of track number (0–79 = side 0; 128–207 = side 1).
- **Big-endian sector count:** unusual (almost every other Spectrum format is little-endian).
- **Variants:** GDOS (DISCiPLE), G+DOS (+D), SAMDOS 2 (SAM Coupé), MasterDOS, B-DOS, UNI-DOS.

MGT is the most sophisticated of the four formats — it supports random access via the bitmap and resilient sequential access via the linked list, and it can hold files up to 800 KB (filling an entire disk).

### 3.5 Comparison matrix

| Property | TR-DOS | +3DOS | CP/M 2.2 | MGT |
|---|---|---|---|---|
| **Origin** | USSR ~1985 | UK 1987 | USA 1979 | UK 1984 |
| **Hardware** | WD1793 / Beta 128 | WD1772-PH (+3) | any (any BIOS) | WD1770 |
| **Disk capacity** | 800 KB | 720 KB | 720 KB (+3) / varies | 800 KB |
| **Sectors per track** | 10 | 9 | 9 / 10 / 18 | 10 |
| **Filename length** | 8 + 1 ext | 8 + 3 ext | 8 + 3 ext | 10 (no ext) |
| **Directory entry size** | 16 bytes | 32 bytes | 32 bytes (FCB) | 256 bytes |
| **Max directory entries** | 128 | 64 | 64 (+3) / 128+ | 80 (up to 780 with MasterDOS) |
| **Allocation unit** | sectors (1 per file location) | 1 KB blocks | 1 KB blocks | sectors with linked list |
| **File attributes** | None | RO, SYS, ARCH | RO, SYS | RO, HIDDEN |
| **Date stamps** | No | Optional | No | Optional (MasterDOS) |
| **Subdirectories** | No | No | User areas (0–15) | Yes (MasterDOS only) |
| **Max file size** | ~720 KB (single extent) | 16 KB per entry, 8 MB across entries | 16 KB per entry, 8 MB across entries | 800 KB (full disk) |
| **Interoperable with...** | itself only | CP/M tools | +3DOS tools, CPC/PCW disks | SAM Coupé disks |

**Key observations:**

- **TR-DOS is the odd one out** — it does not derive from any other format.
- **+3DOS and CP/M are essentially the same** at the disk-format level (both are CP/M 2.2 with the +3 DPB).
- **MGT is unique** in its linked-list allocation scheme — no other Spectrum format uses this.
- **None of the four formats are mutually interchangeable** — each requires its own reader.

---

## §4. File Header Conventions

### 4.1 The shared 9-byte Spectrum BASIC header

A surprising feature of three of the four logical formats (TR-DOS, +3DOS, MGT) is that they all store Spectrum BASIC, code, and array files with the same **9-byte file header**. This header is identical to the one used in the TAP tape format (see [tap_format.md](tap_format.md)) and is structured as:

| Offset | Length | Field |
|---|---|---|
| 0 | 1 | File type: 0=BASIC, 1=number array, 2=char array, 3=code/binary |
| 1 | 2 | Data length (LE) |
| 3 | 2 | Parameter 1 (autostart line for BASIC; load address for code) (LE) |
| 5 | 2 | Parameter 2 (LE) |
| 7 | 2 | Reserved |

The reason for this shared convention is that the 9-byte header is the format the Spectrum ROM's tape-load routines use (`LD-BYTES`, `SA-BYTES`, etc. at `0x0556`, `0x04C6`, etc.). All three formats adopted it for compatibility with the ROM's loader — a BASIC program saved to tape can be saved to disk with the same header, byte-for-byte.

CP/M disks do **not** use this header — CP/M files are pure data, with no metadata at the file level (any metadata is application-specific, e.g. WordStar's formatting directives).

### 4.2 Snapshot files

Both TR-DOS and MGT support **snapshot files** (type 5 in MGT, `C` extension in TR-DOS). These contain a complete Z80 register dump plus the 48 KB or 128 KB RAM contents, allowing the machine state to be saved and restored.

The TR-DOS snapshot format is identical to the **.SNA format** (see [sna_format.md](../snapshots/sna_format.md) for details). The MGT snapshot format stores the register dump in the directory entry (bytes 210–241), not in the file data — the file data is just the raw RAM contents.

### 4.3 Code/binary files

A Spectrum "code file" (also called a "binary file") is a contiguous block of memory saved to disk. The 9-byte header for code files contains:

- Type byte (#03).
- Length in bytes (LE 16-bit).
- Start address (LE 16-bit) — where the file should be loaded in memory.
- 32768 (#8000) as parameter 2 — unused for code files.

To load a code file at address X and length L, a Spectrum DOS reads the 9-byte header, then reads L bytes from the file into address X. Code files are the standard way to distribute machine-code programs, demoscene effects, and games.

---

## §5. Disk Image File Formats

### 5.1 The eight formats

Modern systems store Spectrum disks as **disk-image files**. Eight image formats are in active use, falling into three categories:

| Format | Layer | Captures | Article |
|---|---|---|---|
| `.TRD` | sector | TR-DOS disks (standard geometry only) | [trd_scl_formats.md](trd_scl_formats.md) |
| `.SCL` | sector | TR-DOS disks (file-level backup, no sector layout) | [trd_scl_formats.md](trd_scl_formats.md) |
| `.MGT` | sector | MGT/Opus disks (any geometry) | [opus_discovery_format.md](opus_discovery_format.md) |
| `.DSK` | sector | any CP/M/+3DOS disk (standard geometry) | [dsk_fdi_formats.md](dsk_fdi_formats.md) |
| `.EDSK` | sector | any disk, including non-standard sectors, copy-protected disks | [dsk_fdi_formats.md](dsk_fdi_formats.md) |
| `.FDI` | sector | any disk (similar capability to .EDSK, different format) | [dsk_fdi_formats.md](dsk_fdi_formats.md) |
| `.UDI` | flux | any disk at the flux-transition level (best archival fidelity) | [udi_format.md](udi_format.md) |
| `.SCP` | flux | any disk at the flux-transition level (SuperCard Pro hardware) | [scp_format.md](scp_format.md) |

### 5.2 Sector-level vs flux-level

The eight formats split into two categories:

- **Sector-level formats** (`.TRD`, `.SCL`, `.MGT`, `.DSK`, `.EDSK`, `.FDI`) store the 512-byte sector data, plus optionally the sector header (CHRN). They cannot capture non-standard sectors, weak bits, or flux-level copy protection.
- **Flux-level formats** (`.UDI`, `.SCP`) store every magnetic transition on the disk surface, exactly as the read head sees it. They can capture any disk, including copy-protected originals.

For archival use, flux-level formats are **always preferred** — they preserve every bit of information. Sector-level formats are sufficient for most non-copy-protected disks and are smaller and easier to work with.

### 5.3 When to use which

- **`.TRD`** — for distributing TR-DOS software (demoscene demos, Russian games). The smallest format, supported by every Russian-oriented emulator.
- **`.SCL`** — for file-level backups of TR-DOS disks (no sector-level layout, just the file contents). Smaller than `.TRD` for sparsely-populated disks.
- **`.MGT`** — for distributing Opus Discovery / +D / DISCiPLE / SAM Coupé software. Simple raw-sector format.
- **`.DSK`** — for distributing +3DOS / CP/M software with standard geometry. Smaller than `.EDSK`.
- **`.EDSK`** — the de-facto Western standard for +3DOS / CP/M disks, including those with non-standard geometry. Supported by Fuse, Spectaculator, SimCoupé, and most modern emulators.
- **`.FDI`** — an alternative to `.EDSK` with similar capabilities; used by some older emulators.
- **`.UDI`** — for archival preservation of any disk at the flux level.
- **`.SCP`** — for archival preservation using the SuperCard Pro hardware; the gold standard for long-term preservation.

### 5.4 Comparison matrix

| Format | Layer | Header | Variable geometry | Non-standard sectors | Weak bits / copy protection | Relative size |
|---|---|---|---|---|---|---|
| `.TRD` | sector | minimal | no | no | no | 1.0× |
| `.SCL` | sector | minimal | n/a (no sector layout) | no | no | 0.5–1.0× |
| `.MGT` | sector | none | yes (by file size) | no | no | 1.0× |
| `.DSK` | sector | yes | no | no | no | 1.0× |
| `.EDSK` | sector | yes | yes | yes | no | 1.1–1.5× |
| `.FDI` | sector | yes | yes | yes | no | 1.1–1.5× |
| `.UDI` | flux | yes | yes | yes | yes | 5–10× |
| `.SCP` | flux | yes | yes | yes | yes | 5–20× |

The relative size is approximate, based on an 800 KB DSDD source disk. Flux-level formats are much larger because they capture multiple revolutions per track and store every MFM transition.

---

## §6. Choosing the Right Format

### 6.1 Decision tree: which logical format?

If you are **writing or distributing Spectrum software**, choose the logical format that matches your target audience:

```
Is the software targeting Soviet / Russian / Eastern European users?
├── Yes → TR-DOS  (.TRD or .SCL disk image)
│         - Works on Pentagon, Scorpion, ATM Turbo, all Russian clones
│         - Most Russian-language demoscene releases use this
│
└── No
    ├── Is it for the Spectrum +3 / +2A?
    │   ├── Yes → +3DOS  (.DSK or .EDSK disk image)
    │   │           - Standard format for +3 software
    │   │           - Interoperable with CP/M tools
    │   │
    │   └── No
    │       ├── Is it for the Opus Discovery / DISCiPLE / +D / SAM Coupé?
    │       │   └── Yes → MGT  (.MGT disk image)
    │       │
    │       └── Is it CP/M business software?
    │           └── Yes → CP/M  (.DSK or .EDSK disk image)
    │                       - Boots into CP/M mode on the +3
    │                       - Interchangeable with Amstrad CPC/PCW disks
```

### 6.2 Decision tree: which disk image format?

If you are **archiving or distributing disk images**, choose the image format that matches your fidelity needs:

```
Is the disk copy-protected or uses non-standard sector IDs?
├── Yes → .SCP  (flux level — preserves everything)
│         - Requires SuperCard Pro or GreaseWeazle hardware to image
│         - 5–20× larger than sector-level images
│
└── No
    ├── Is long-term archival preservation the goal?
    │   └── Yes → .UDI  (flux level, no special hardware required)
    │                - 5–10× larger than sector-level images
    │
    └── No (daily use / distribution)
        ├── TR-DOS disk? → .TRD  (simplest, smallest)
        ├── MGT disk?    → .MGT  (raw sector dump)
        └── +3DOS / CP/M disk? → .EDSK  (handles non-standard geometry)
```

### 6.3 Emulator support matrix

For emulator authors, the following formats are typically required:

| Emulator target | Required formats | Recommended additions |
|---|---|---|
| **Russian Spectrum** (Pentagon, Scorpion) | `.TRD`, `.SCL` | `.FDI` for non-standard disks |
| **Western Spectrum +3** | `.DSK`, `.EDSK` | `.TRD` for cross-compatibility |
| **Opus / DISCiPLE / +D / SAM Coupé** | `.MGT` | `.DSK` for +3 compatibility |
| **General Spectrum emulator** (Fuse, Spectaculator, ZX Spin) | all of the above | `.UDI`, `.SCP` for archival |
| **CP/M emulator** (zxcc, MYZ80) | `.DSK` | `.EDSK` for non-standard geometry |

### 6.4 Conversion tips

The modern tool **`samdisk`** (open source, by Owen Dunn) can convert between most of these formats:

```
samdisk input.trd output.edsk     # TR-DOS sector dump → EDSK
samdisk input.scp output.dsk      # SuperCard flux → DSK
samdisk input.mgt output.edsk     # MGT raw → EDSK
```

When converting from a flux-level format (`.SCP`, `.UDI`) to a sector-level format (`.DSK`, `.EDSK`), information about weak bits, copy protection, and non-standard sectors is **lost**. Always keep the flux-level original for archival.

When converting from `.TRD` to `.EDSK` or vice versa, the **logical format is preserved** (a TR-DOS disk remains a TR-DOS disk) — only the container format changes. This is safe and lossless.

**Conversion between logical formats is not possible** by simple image conversion — a TR-DOS disk cannot be turned into a +3DOS disk without re-creating the directory structure. Tools like **`trd2plus3`** and **`mgtscl`** can do this for specific format pairs, but the results are not always perfect (file attributes, dates, and other metadata may be lost).

---

## §7. Cross-references and License

### 7.1 The complete floppy documentation set

This overview is one of 13 articles covering the Spectrum's floppy-disk storage. The full set, in reading order:

**Physical layer (2 articles):**

1. [mfm_encoding.md](mfm_encoding.md) — the **MFM signal layer**: bit-level encoding, address marks, CRC16, gap structure.
2. [fdc_vg93.md](fdc_vg93.md) — the **WD1793 / KR1818VG93 floppy controller chip**: register file, Type I/II/III/IV commands, status register.

**Hardware interfaces (2 articles):**

3. [beta_disk_interface.md](beta_disk_interface.md) — the **Beta Disk Interface / Beta 128** hardware (Soviet standard).
4. [plus3_floppy.md](plus3_floppy.md) — the **Spectrum +3's floppy hardware** (WD1772-PH controller, internal 3" drive).

**Logical disk formats (4 articles):**

5. [trd_disk_format.md](trd_disk_format.md) — **TR-DOS** logical disk format (Soviet standard, 800 KB DSDD).
6. [plus3_dos_format.md](plus3_dos_format.md) — **+3DOS** logical disk format (CP/M 2.2 derivative, 720 KB DSDD).
7. [cpm_disk_format.md](cpm_disk_format.md) — **CP/M 2.2** disk format on the Spectrum family (+3, ATM Turbo, Sprinter).
8. [opus_discovery_format.md](opus_discovery_format.md) — **Opus Discovery / MGT** disk format (UK standard, 800 KB DSDD with linked-list allocation).

**Disk-image file formats (4 articles):**

9. [trd_scl_formats.md](trd_scl_formats.md) — **`.TRD`** and **`.SCL`** image formats (TR-DOS containers).
10. [dsk_fdi_formats.md](dsk_fdi_formats.md) — **`.DSK`**, **`.EDSK`**, and **`.FDI`** image formats (CP/M / +3DOS / Opus containers).
11. [udi_format.md](udi_format.md) — **`.UDI`** flux-level image format.
12. [scp_format.md](scp_format.md) — **`.SCP`** flux-level image format (SuperCard Pro).

**Overview (this article):**

13. [disk_format_overview.md](disk_format_overview.md) — this article.

### 7.2 External references

- [World of Spectrum](https://worldofspectrum.org/) — the central Spectrum software archive; many disk images in all formats.
- [The Sinclair Wiki](https://sinclair.wiki.zxnet.co.uk/) — authoritative reference for MGT, TR-DOS, and CP/M formats.
- [Speccy Wiki](https://speccy.info/) — Russian-language wiki with extensive TR-DOS documentation.
- [samdisk](https://simcoupe.org/samdisk/) — modern open-source multi-format disk-image converter.
- [SuperCard Pro](http://www.cbmstuff.com/proddetail.php?prod=SCP) — hardware for flux-level disk imaging.

### 7.3 License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)** — see `https://creativecommons.org/licenses/by-sa/4.0/`.

You are free to:

- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

- **Attribution** — You must give appropriate credit (attribution to the Knowledge base project), provide a link to the license, and indicate if changes were made.
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

The full legal text is available at the link above.

The trademarks **ZX Spectrum**, **ZX Spectrum +2**, **ZX Spectrum +2A**, **ZX Spectrum +3**, **Sinclair Research**, **Amstrad**, **Opus Supplies**, **Miles Gordon Technology**, **MGT**, **DISCiPLE**, **+D**, **SAM Coupé**, **SAMDOS**, **MasterDOS**, **Beta Disk Interface**, **Beta 128**, **TR-DOS**, **+3DOS**, **CP/M**, **Digital Research**, **ATM Turbo**, **Sprinter**, **Pentagon**, **Scorpion**, **Western Digital**, **WD1793**, **WD1770**, **WD1772**, **WD1772-PH**, **KR1818VG93**, **IBM 3740**, **Hitachi HFD-305S**, **Gotek**, **FlashFloppy**, **HxC**, **SuperCard Pro**, **GreaseWeazle**, **samdisk**, and others mentioned in this document are the property of their respective owners and are used here for identification and educational purposes only. No endorsement by, or affiliation with, any of these trademark holders is implied.
