# .TRD and .SCL Disk Image Formats

**Scope:** The two file-image formats used to store TR-DOS disks as files on modern computers: **.TRD** (a sector-by-sector disk image) and **.SCL** (a file-by-file logical image). The on-disk TR-DOS format itself is covered in [trd_disk_format.md](trd_disk_format.md); the floppy hardware that reads TR-DOS disks is covered in [beta_disk_interface.md](beta_disk_interface.md).

**Audience:** Emulator authors, archival tool authors, demoscene coders, and anyone who needs to read, write, convert, or manipulate TR-DOS disk images on modern hardware.

**Prerequisites:** A working understanding of the TR-DOS logical disk format (the 16-byte directory entry, the disk descriptor, the sector layout). Strongly recommended to read [trd_disk_format.md](trd_disk_format.md) first; this article assumes familiarity with its terminology.

**Depth:** Deep. Byte-level layout of both file-image formats, including the .TRD headerless format, the .SCL header with file table, the checksumming scheme, the file-table layout, and the many compatibility quirks of real-world .TRD and .SCL files in circulation.

---

## §1. What .TRD and .SCL Are

### 1.1 Why disk images?

A TR-DOS disk is a physical object (a 3" or 3.5" floppy) that contains both:

- **Logical structure** (the directory, files, disk descriptor) — see [trd_disk_format.md](trd_disk_format.md).
- **Physical structure** (the MFM-encoded sectors, gaps, sync marks, address marks) — see [mfm_encoding.md](mfm_encoding.md).

A **disk image** is a file on a modern computer that captures some subset of this structure, in a format that emulators and other tools can read. TR-DOS disks are preserved via two main image formats:

- **.TRD** (TR-Dos Read) — a **sector-by-sector** image: every sector on the disk is stored in the file as a 512-byte block. The result is essentially a raw dump of the disk's logical contents, with no metadata beyond what TR-DOS itself stores in the disk descriptor.
- **.SCL** (Sinclair Logical Image / SCL) — a **file-by-file** image: only the TR-DOS files (their names, types, and data) are stored in the file, plus a small header. The disk's directory structure is reconstructed from the file table when the image is loaded.

Both formats are widely used by Spectrum emulators (UnrealSpeccy, ZEsarUX, FUSE, etc.) and by archival tools.

### 1.2 When .TRD vs. .SCL?

The two formats have different trade-offs:

| Aspect | .TRD | .SCL |
|---|---|---|
| **Fidelity** | Captures the entire disk (every sector, including free sectors and the disk descriptor). | Captures only the files; the directory and free-space layout are reconstructed. |
| **Size** | Always the same size for a given geometry (typically 800 KB for 80-track 2-sided). | Proportional to the total file data on the disk (much smaller for disks with few files). |
| **Preservation** | Good — captures deleted entries, gaps, custom boot sectors, etc. | Poor — only preserves the live files; deleted files, custom loaders, and non-standard sectors are lost. |
| **Compatibility** | Universal — every TR-DOS-aware emulator reads .TRD. | Universal — every TR-DOS-aware emulator reads .SCL. |
| **Editability** | Difficult — editing a .TRD requires modifying the sector bytes directly. | Easy — adding or removing files is a simple matter of updating the file table. |

In practice:

- **.TRD** is used for archival preservation of original disks, where fidelity matters.
- **SCL** is used for software distribution and emulator loading, where size matters.

Most commercial software from the TR-DOS era is distributed today as .SCL files (small, easy to download). Original disks preserved by archivists are typically stored as .TRD (or, increasingly, as .SCP flux-level images — see [scp_format.md](scp_format.md)).

### 1.3 A short history

The **.TRD** format originated in the early 1990s with the first PC-based Spectrum emulators. The format was standardized by the Russian Spectrum community (zxevo.ru, zx-pk.ru) in the late 1990s.

The **.SCL** format was created around the same time, originally as a "compressed" alternative to .TRD for software distribution. The format was designed by the authors of the X128 emulator and was quickly adopted by other emulators.

Both formats have remained essentially unchanged since the late 1990s. Modern emulators and tools maintain backward compatibility with .TRD and .SCL files created decades ago.

### 1.4 Scope

This article covers the byte-level layout of .TRD and .SCL files. The .DSK, .EDSK, .FDI, .UDI, and .SCP formats (which can also store TR-DOS disks, with varying levels of fidelity) are covered in their own articles: [dsk_fdi_formats.md](dsk_fdi_formats.md), [udi_format.md](udi_format.md), [scp_format.md](scp_format.md).

---

## §2. The .TRD Format

### 2.1 Overview

A **.TRD file** is a sector-by-sector image of a TR-DOS disk. It contains **no file header**: the file is simply a concatenation of the disk's sectors, in physical (cylinder, side, sector) order.

For a standard 80-track 2-sided TR-DOS disk (80 cylinders × 2 sides × 10 sectors × 512 bytes = 819,200 bytes), the .TRD file is **819,200 bytes long**. Smaller geometries produce smaller files:

| Disk geometry | .TRD file size |
|---|---|
| 80 × 2 × 10 × 512 (standard) | 819,200 bytes (800 KB) |
| 80 × 1 × 10 × 512 | 409,600 bytes (400 KB) |
| 40 × 2 × 10 × 512 | 409,600 bytes (400 KB) |
| 40 × 1 × 10 × 512 | 204,800 bytes (200 KB) |
| 80 × 2 × 16 × 256 (TR-DOS 5.0) | 655,360 bytes (640 KB) |

A real .TRD file may be slightly smaller than the disk's full capacity if the imaging tool stopped at the last non-free sector. The "missing" sectors at the end are assumed to be all-zero when the file is loaded into an emulator.

### 2.2 Sector ordering

The sectors in a .TRD file are stored in the order in which they would be read by sequential READ SECTOR commands. The order is:

1. Cylinder 0, side 0, sectors 1 through 10 (in numerical order).
2. Cylinder 0, side 1, sectors 1 through 10.
3. Cylinder 1, side 0, sectors 1 through 10.
4. Cylinder 1, side 1, sectors 1 through 10.
5. ...
6. Cylinder 79, side 1, sectors 1 through 10.

This is the **side-first** ordering (within each cylinder, side 0 is read first, then side 1, then the next cylinder). It is sometimes called "Apple / Commodore" ordering, as opposed to the "side-last" ordering used by IBM PC floppy images.

The byte offset of a given (cylinder, side, sector) within a .TRD file is:

```
offset = (cylinder * 2 + side) * 10 * 512 + (sector - 1) * 512
```

For example:
- Cylinder 0, side 0, sector 1 → offset 0 (the start of the file).
- Cylinder 0, side 0, sector 8 → offset 3584 (the disk descriptor — see [trd_disk_format.md §7](trd_disk_format.md)).
- Cylinder 0, side 1, sector 1 → offset 5120.
- Cylinder 1, side 0, sector 1 → offset 10240.
- Cylinder 79, side 1, sector 10 → offset 819200 - 512 = 818688 (the last sector of the disk).

### 2.3 The disk descriptor's role

Because the .TRD file has no header of its own, the **disk descriptor** (sector 8 of cylinder 0 side 0, at offset 3584 in the .TRD file) is the source of all metadata about the disk's geometry. A .TRD-reading tool must:

1. Read the disk descriptor at offset 3584.
2. Check the format code at offset 3584 + `#FB` = `#87F` (decimal 2175 within the sector, or 3584 + 251 = 3835 within the .TRD file).
3. Use the format code to determine the disk's cylinder count, side count, and sector count.
4. Validate that the .TRD file's actual length matches the expected capacity for that geometry.

If the .TRD file's length does not match the disk descriptor's geometry, the file is either truncated or padded. Tools usually pad with zeros up to the expected capacity.

### 2.4 The catalog in a .TRD file

The TR-DOS catalog (directory) is at offsets 0–2047 in the .TRD file (sectors 1–4 of cylinder 0 side 0). Each of the 128 directory entries occupies 16 bytes (see [trd_disk_format.md §6](trd_disk_format.md) for the entry layout).

A tool that wants to enumerate the files on a .TRD disk should iterate over the 128 directory entries starting at offset 0, skipping entries whose first byte is `#00` (free) or `#01` (deleted), and stopping at the first free entry.

### 2.5 Reading a file's data

To read the data of a file from a .TRD file:

1. Find the directory entry for the file (by iterating the catalog as above).
2. Extract the file's first-sector address from bytes 14–15 of the directory entry: `track_byte` (byte 14) and `sector_byte` (byte 15). The cylinder is `track_byte & 0x7F`; the side is `(track_byte >> 7) & 0x01`; the sector is `sector_byte` (assumed 1–10).
3. Compute the byte offset in the .TRD file: `offset = (cylinder * 2 + side) * 5120 + (sector - 1) * 512`.
4. Read `sector_count` sectors (from bytes 12–13 of the directory entry) starting at that offset.
5. Truncate to the file's byte length (from bytes 10–11) — the last sector may be only partially used.

This is a straightforward process once you have the directory entry and the disk geometry. No additional metadata is needed.

### 2.6 Truncated .TRD files

Some .TRD files in circulation are **truncated** — they are shorter than the disk's full capacity, ending at the last sector that contained non-zero data. This is a common optimisation for distribution: a 200 KB disk stored as a 200 KB .TRD file rather than a 800 KB one.

A tool reading a truncated .TRD file should:

1. Read the disk descriptor to determine the disk's full geometry.
2. Compute the expected file size for that geometry.
3. If the actual file size is smaller, pad the missing sectors with zeros in memory.

Most modern emulators handle truncated .TRD files transparently. Some older tools may fail on them, so a common fix is to "untruncate" the file by appending zeros up to the expected capacity.

### 2.7 .TRD file extensions and variants

The `.TRD` file extension is the standard, but other extensions are sometimes seen:

- `.trd` (lowercase) — the same format, used on case-sensitive file systems.
- `.TR` — an early variant, identical to .TRD.
- `.FDI` — sometimes used for TR-DOS images (confusingly; .FDI is more commonly a different format — see [dsk_fdi_formats.md](dsk_fdi_formats.md)).

The content of the file is the same regardless of the extension. The .TRD extension is preferred for clarity.

### 2.8 Worked example: a minimal .TRD file

A minimal .TRD file containing a single 1000-byte CODE file named `GAME`:

- Offset 0 (catalog entry 0): the directory entry for `GAME    C`, as described in [trd_disk_format.md §6.5](trd_disk_format.md).
- Offsets 16–2047 (catalog entries 1–127): all zeros (free entries).
- Offsets 2048–3583 (sectors 5–7 of cylinder 0 side 0): all zeros (unused).
- Offset 3584 (sector 8 of cylinder 0 side 0): the disk descriptor, with:
  - First free sector: cylinder 0 side 1 sector 3 (after the 2 sectors used by GAME).
  - Free sector count: 1598 (1600 total sectors minus 2 used).
  - Disk label: "TESTDISK".
  - Format code: `#16` (80-track 2-sided).
- Offset 4096 (sector 9 of cylinder 0 side 0): backup copy of the disk descriptor.
- Offset 4608 (sector 10 of cylinder 0 side 0): all zeros (unused).
- Offset 5120 (sector 1 of cylinder 0 side 1): the first 512 bytes of GAME (a 4-byte `load_addr + length` header followed by 508 bytes of code).
- Offset 5632 (sector 2 of cylinder 0 side 1): the next 488 bytes of GAME, followed by 24 bytes of zeros (padding to fill the sector).

The rest of the .TRD file (offsets 6144 through 819199) is all zeros. A truncated .TRD file would end at offset 6144 (the last non-zero byte); a full .TRD file would be 819200 bytes long.


## §3. The .SCL Format

### 3.1 Overview

A **.SCL file** is a **file-by-file logical image** of a TR-DOS disk. Instead of storing every sector on the disk (like .TRD), the .SCL format stores only the **TR-DOS files**: their names, types, lengths, and contents. The disk's directory structure and free-space layout are **reconstructed** when the .SCL is loaded by an emulator.

A .SCL file is composed of three parts, in this order:

1. **A 9-byte header** containing the magic string `"SINCLAIR"` and a file count.
2. **A file table** of N entries (one per file on the disk), each 14 bytes.
3. **The file data**: the contents of every file, concatenated in the same order as the file table.

Optionally, a single-byte **checksum** at the very end of the file.

The total size of a .SCL file is therefore:

```
file_size = 9 + N * 14 + sum(file_lengths) [+ 1 if checksum present]
```

where N is the file count and `sum(file_lengths)` is the total of every file's data length in bytes. Because the file table contains no information about sector placement or free space, the file is significantly smaller than the corresponding .TRD file (typically 100–600 KB for a 800 KB disk, depending on how much free space the original disk had).

### 3.2 The 9-byte header

| Offset | Length | Content |
|---|---|---|
| 0 | 8 | **Magic string**: `53 49 4E 43 4C 41 49 52` (ASCII `"SINCLAIR"`) |
| 8 | 1 | **File count** (N): the number of file-table entries that follow, in the range 0–127. |

The `"SINCLAIR"` magic identifies the file as a .SCL image. Some readers also accept `"SCL"` (3 bytes) followed by 5 bytes of additional magic, but `"SINCLAIR"` is the canonical form.

The file count at offset 8 is a single byte. The maximum value is 127, matching TR-DOS's 128-entry catalog (the difference is that the disk descriptor's catalog can hold up to 128 files; the .SCL header byte uses 0–127, with the convention that 0 means "128 files" in some historical readers, but the modern convention is that the count is literal).

### 3.3 The 14-byte file-table entry

The file table contains N entries, each 14 bytes long. The layout of each entry is:

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 8 | **Filename** | 8 ASCII characters, space-padded (`0x20`). Same format as a TR-DOS directory entry's name field (see [trd_disk_format.md §6.1](trd_disk_format.md)). |
| 8 | 1 | **File type** | ASCII letter: `'B'` (`0x42`, Basic), `'C'` (`0x43`, Code), `'D'` (`0x44`, Data / screen), `'#'` (`0x23`, Print), `'M'` (`0x4D`, Master / M-drive). Same encoding as the TR-DOS directory entry's type byte. |
| 9 | 2 | **File length** (LE) | The file's data length in bytes (little-endian). |
| 11 | 2 | **Parameter** (LE) | For `B` and `C` files: the start address in memory (the LINE parameter for Basic, the LOAD address for Code). For `D` files: typically the start address of the screen. For `#` files: a driver-specific parameter. Little-endian. |
| 13 | 1 | **High byte of length** | The high byte (bits 16–23) of the file's length, allowing files larger than 65535 bytes (rare). For files under 64 KB, this byte is `0x00`. |

This 14-byte format closely mirrors the 16-byte TR-DOS directory entry, but **omits** the 2-byte "sector count" field (since the .SCL format does not preserve sector placement) and **adds** the high-byte-of-length extension to support files >64 KB.

### 3.4 The file data

After the file table comes the **file data**: the raw bytes of every file on the disk, concatenated in the same order as the file-table entries. There is **no padding** between files — file N's data immediately follows file N-1's data.

For example, if a disk contains 3 files of lengths 1000, 500, and 20000 bytes:

| Offset | Length | Content |
|---|---|---|
| 0 | 9 | Header (`"SINCLAIR"` + file count `0x03`) |
| 9 | 14 × 3 = 42 | File table |
| 51 | 1000 | File 0's data |
| 1051 | 500 | File 1's data |
| 1551 | 20000 | File 2's data |
| 21551 | (optional) 1 | Checksum byte |

The total file size would be 21551 bytes (or 21552 with the checksum), versus 819200 bytes for the equivalent .TRD image. This compression is why .SCL became the dominant format for software distribution.

### 3.5 The optional checksum

Some .SCL files include a single-byte **checksum** at the very end of the file. The checksum is computed as the **8-bit XOR** (or in some variants, the 8-bit addition modulo 256) of every byte in the file from the header onward (the file data and the file table).

| Checksum scheme | Formula | Used by |
|---|---|---|
| XOR | `csum = 0; for byte in file: csum ^= byte` | Older .SCL readers |
| Sum mod 256 | `csum = (sum of all bytes) & 0xFF` | Most modern .SCL writers |
| None | No checksum byte; file ends after the last file's data | Some readers tolerate either |

A reader should check whether the file size matches `9 + N * 14 + sum(file_lengths)` (no checksum) or `9 + N * 14 + sum(file_lengths) + 1` (checksum present). In the latter case, the last byte is the checksum and should be validated.

In practice, most modern emulators tolerate both forms and validate the checksum only as a warning, not a hard error. Many .SCL files in circulation have an incorrect checksum (the writer's checksum implementation was buggy), and tools usually accept them silently.

### 3.6 What .SCL does NOT preserve

Because the .SCL format stores only the file's name, type, length, and data, it **loses** the following information that is present on the original TR-DOS disk:

- **The disk descriptor** (disk label, format code, position of first free sector, free-space count). A loader reconstructs plausible defaults when generating a fresh directory.
- **The exact sector placement** of each file. The original disk may have had file A on cylinder 5 side 0 and file B on cylinder 7 side 1; the .SCL discards this and lets the loader re-pack the files when the image is loaded.
- **Deleted files** and their (potentially still-recoverable) sector data. Once a file is removed from the file table, its data is gone from the .SCL.
- **Custom boot sectors** or non-standard directory entries. Any non-TR-DOS-standard structure on the disk (e.g., copy-protection tricks, custom loaders in the disk descriptor) is lost.
- **The 128-entry directory structure**. The .SCL format does not preserve which slot in the directory each file occupied.

In particular, .SCL files **cannot represent copy-protected disks**. Any disk that uses non-standard sector layouts, deliberately corrupted sectors, or sector-placement-dependent protection (the common techniques used by 1980s commercial software) cannot be faithfully stored in a .SCL file. For such disks, use .TRD (which at least preserves the sector-by-sector layout) or — better — a flux-level format like .SCP (see [scp_format.md](scp_format.md)).

### 3.7 Loader behavior

When an emulator loads a .SCL file into its virtual floppy drive, it does the following:

1. Reads the 9-byte header and verifies the `"SINCLAIR"` magic.
2. Reads N (the file count) from byte 8.
3. Reads the N × 14-byte file table into memory.
4. Optionally validates the checksum byte.
5. **Builds a fresh TR-DOS disk image in memory**: it formats a blank disk (819,200 bytes for the standard 80-track 2-sided geometry), writes the disk descriptor at sector 8 of cylinder 0 side 0 with default values, then iterates the file table and writes a synthetic 16-byte directory entry for each file in catalog slots 0, 1, 2, ..., N-1.
6. Writes the file data, in order, to the disk starting at the first sector after the catalog (cylinder 0 side 1 sector 1, conventionally).
7. Updates the disk descriptor's first-free-sector and free-space-count fields to reflect the post-load free space.

The result is an in-memory disk image that is byte-equivalent to a freshly formatted TR-DOS disk onto which the files have been copied in their .SCL-table order. Software running in the emulator sees the disk as a normal TR-DOS disk and can `LOAD`, `SAVE`, and `*CAT` it normally.

### 3.8 Worked example: a minimal .SCL file

A .SCL file containing a single 1000-byte CODE file named `GAME`:

- Offset 0 (8 bytes): `"SINCLAIR"` magic (`53 49 4E 43 4C 41 49 52`).
- Offset 8 (1 byte): file count `0x01`.
- Offset 9 (14 bytes): the file-table entry for `GAME    C`:
  - Bytes 0–7: `47 41 4D 45 20 20 20 20` ("GAME    ").
  - Byte 8: `0x43` ('C').
  - Bytes 9–10: `E8 03` (1000 LE).
  - Bytes 11–12: `00 80` (start address `#8000` LE).
  - Byte 13: `0x00` (high byte of length, 0 for a <64 KB file).
- Offset 23 (1000 bytes): the file's data.
- Offset 1023 (optional, 1 byte): the checksum.

Total file size: 1023 bytes without checksum, or 1024 with. This is far smaller than the corresponding .TRD file (819200 bytes for the full disk, or at least 6144 bytes for a truncated one).

### 3.9 .SCL file extensions

The `.SCL` extension is the canonical form. Some tools accept lowercase `.scl`. There are no common variant extensions (unlike .TRD's `.TR` and `.FDI` variants).


## §4. .TRD vs. .SCL: Comparison and Use Cases

### 4.1 The trade-off matrix

| Criterion | .TRD | .SCL |
|---|---|---|
| **Fidelity** | High — every sector on the disk is captured, including the disk descriptor, the catalog layout, free sectors, and any deleted-but-recoverable data. | Low — only the live files are captured; the disk descriptor, catalog layout, and free-space arrangement are reconstructed by the loader. |
| **File size** | Fixed by geometry (typically 819,200 bytes / 800 KB for an 80-track 2-sided disk). Truncated .TRD files are common and smaller. | Proportional to total file data; typically 100–600 KB for a fully-loaded disk, and trivially small for a near-empty disk. |
| **Round-trip integrity** | A `.TRD → disk → .TRD` round-trip is byte-exact (assuming the disk drive is functional). | A `.SCL → disk → .SCL` round-trip preserves file data but loses sector placement (the new .SCL may differ from the original). |
| **Load speed** | Slower in emulators that load the full disk image into memory at boot (an 800 KB read on every disk insert). | Faster — only the file table and file data are loaded, often <50 KB total. |
| **Editability** | Difficult — adding or removing files requires updating the directory, the free-space pointer, and the disk descriptor by hand. | Easy — the file table is a fixed-position array, and the file data is simply concatenated. Most .SCL editors let you drag-and-drop files. |
| **Compatibility** | Universal across TR-DOS-aware emulators. | Universal across TR-DOS-aware emulators. |
| **Copy protection** | Can represent some non-standard sector layouts (if the emulator supports the variant). Cannot represent weak/strong bits or sector placement at the flux level. | Cannot represent any copy protection. A .SCL of a protected disk will generally not boot. |
| **Disk geometry variants** | Geometry must be inferred from the disk descriptor or the file size. Non-standard geometries (e.g., 80×2×16×256) require reader support. | Geometry is implicit (always the standard 80-track 2-sided) — a .SCL of a 40-track disk is loaded onto a synthetic 80-track disk by the emulator. |

### 4.2 When to use .TRD

Use .TRD when:

- **Archiving original media** for long-term preservation. The .TRD format captures the disk's directory layout, free-space arrangement, and (if the imaging tool preserves them) any non-standard sectors on the disk. This makes it the appropriate choice for archival projects such as the World of Spectrum archive or the Russian `trd.speccy.info` collection.
- **Running disk software that depends on the disk's physical structure**. Some software uses hardcoded (cylinder, side, sector) addresses to read its data, bypassing the directory. Such software will only work correctly if the disk image preserves the original sector placement, which only .TRD does.
- **Editing a disk's directory in place** (e.g., recovering a deleted file, fixing a corrupted disk descriptor, examining the disk's structure). A .TRD file is a byte-for-byte representation of the disk, so a hex editor can navigate the structure directly using the offsets documented in [trd_disk_format.md](trd_disk_format.md).

### 4.3 When to use .SCL

Use .SCL when:

- **Distributing disk software** for download. The size advantage is decisive — a typical .SCL is 5–10× smaller than the equivalent .TRD, and most downloaders do not care about the disk's free-space layout.
- **Loading disk software into an emulator quickly**. The smaller file size translates directly into faster load times, especially when loading from slow media (e.g., SD cards on a real-hardware Spectrum with an SD-card interface).
- **Building a "best-of" compilation disk** from files scattered across many original disks. The .SCL format makes it trivial to drag files from multiple sources into a single new image.
- **Sharing a disk that uses only standard TR-DOS file operations**. If the software does not care about its sector placement (and most disk-based Spectrum software does not), .SCL is the right choice.

### 4.4 When to use neither

Neither .TRD nor .SCL is suitable for:

- **Copy-protected disks** that use non-standard sector layouts, weak bits, or flux-level tricks. For such disks, use **.SCP** (a flux-level image — see [scp_format.md](scp_format.md)) or **.EDSK** (extended DSK, which can capture non-standard sector layouts at the sector level — see [dsk_fdi_formats.md](dsk_fdi_formats.md)).
- **Non-TR-DOS disks** (e.g., +3DOS disks, CP/M disks, Opus Discovery disks). These require their own image formats: see [plus3_dos_format.md](plus3_dos_format.md), [cpm_disk_format.md](cpm_disk_format.md), [opus_discovery_format.md](opus_discovery_format.md).
- **Archival preservation of media that may have bit-rot**. For long-term preservation, flux-level imaging (.SCP, .UID/.UDI) is the gold standard, because it captures the disk at the lowest possible level (the raw MFM flux transitions) and can be re-imaged if the magnetic media degrades.

### 4.5 Converting between .TRD and .SCL

Conversion between .TRD and .SCL is straightforward in one direction and lossy in the other:

- **.TRD → .SCL** (lossless within .SCL's expressive power): read the directory from the .TRD, iterate the live file entries, and write each file's name/type/length/data into the .SCL. Information about the disk descriptor, free-space layout, and deleted entries is lost — but this is unavoidable in the .SCL format.
- **.SCL → .TRD** (lossless with respect to file data): create a fresh blank .TRD image, write a default disk descriptor at sector 8 of cylinder 0 side 0, write a synthetic directory from the .SCL file table at catalog slots 0 through N-1, and write the file data starting at the first sector after the catalog. The resulting .TRD file has the same files as the original .SCL, but the disk descriptor's label and the file sector placement will differ from any "original" disk.

Most Spectrum emulator suites (e.g., UnrealSpeccy, ZEsarUX, FUSE, spectaculator) and standalone tools (e.g., **ZX-Blockeditor**, **TRD-Tool**, **SCL2TRD**) perform these conversions via a menu option. The conversion is purely a software operation — no real floppy drive is needed.


## §5. Tools and Converters

### 5.1 Emulators that read .TRD and .SCL

Every Spectrum emulator with TR-DOS support reads both .TRD and .SCL files. The major ones:

| Emulator | Platform | .TRD | .SCL | Notes |
|---|---|---|---|---|
| **UnrealSpeccy / Unreal Speccy** | Windows | Yes | Yes | The de facto reference emulator for TR-DOS in the Russian community. Origin of many .SCL conventions. |
| **ZEsarUX** | Linux / Windows / macOS | Yes | Yes | Full-featured, supports all major Spectrum disk formats and conversions between them. |
| **FUSE** (Free Unix Spectrum Emulator) | Linux / Windows / macOS | Yes | Yes | The standard open-source emulator; .TRD/.SCL support is via the "Disk" menu. |
| **Spectaculator** | Windows | Yes | Yes | Commercial, well-maintained, with strong disk-image handling. |
| **Speccy** (by Marat Fayzullin) | Multiple | Yes | Yes | Bundled with many other Fayzullin emulators; .TRD/.SCL support is included. |
| **Klive** / **Kudos** | Web / JS | Yes | Yes | Browser-based; can load .TRD/.SCL via drag-and-drop. |
| **ZX Evolution** (real hardware) | FPGA Spectrum | Yes | Yes | Reads .TRD/.SCL directly from SD card. |

When loading a .SCL file, these emulators reconstruct the in-memory disk as described in §3.7. When loading a .TRD file, they typically memory-map or stream the file directly into the emulator's virtual floppy buffer.

### 5.2 Standalone .TRD/.SCL editors

For editing disk images without running an emulator, several dedicated tools exist:

- **ZX-Blockeditor** (Windows, by Simon Owen) — a comprehensive editor for .TRD, .SCL, and many other Spectrum disk/tape formats. Supports drag-and-drop file management, hex viewing of individual sectors, format conversion, and disk descriptor editing. The de facto standard for archival work.
- **TRD-Tool** (Windows, command-line) — a small utility for inspecting and modifying .TRD files. Useful in batch scripts.
- **SCL2TRD / TRD2SCL** (DOS, by various Russian authors) — simple format converters. The original 1990s tools are still distributed by the ZX Spectrum community.
- **disk-image-editor** (Python) — a cross-platform open-source tool with .TRD/.SCL support, available on GitHub.

### 5.3 Cross-format converters

The following tools convert .TRD/.SCL to and from other disk-image formats:

- **ZX-Blockeditor** converts .TRD ↔ .SCL ↔ .DSK (single-sided, for +3-formatted .TRD disks).
- **HxCFloppyEmulatorTool** can write a .TRD or .SCL file directly to a Gotek / HxC USB-floppy emulator, formatted for use in a real Spectrum.
- **libdsk** (a Unix library for reading non-standard floppy formats) supports .TRD via a plugin, allowing command-line conversion to .DSK and other formats.
- **cwtool** (raw flux tool, used with KryoFlux and SuperCard Pro hardware) can produce .TRD files from real floppy disks; see [scp_format.md](scp_format.md) and [dsk_fdi_formats.md](dsk_fdi_formats.md) for the upstream flux-level workflows.

### 5.4 Format validation tools

To check whether a .TRD or .SCL file is well-formed:

- For **.TRD**: validate that the file size matches the disk descriptor's geometry, and that the disk descriptor's first-free-sector pointer and free-space count are consistent with the directory.
- For **.SCL**: validate that the file size matches `9 + N*14 + sum(file_lengths) [+ 1 for checksum]`, and that the file-table entries have valid type letters (`B`/`C`/`D`/`M`/`#`) and reasonable length values (≤ 65536, unless the high-byte extension is used).

ZX-Blockeditor and most modern emulators perform these checks on load and emit warnings (but rarely hard errors) for malformed files.

### 5.5 A minimal .TRD/.SCL reader in pseudocode

A minimal .SCL reader, written in pseudocode:

```python
def read_scl(filename):
    with open(filename, "rb") as f:
        data = f.read()

    # Verify magic
    if data[0:8] != b"SINCLAIR":
        raise ValueError("Not a .SCL file")

    n = data[8]
    file_table = []
    offset = 9
    for i in range(n):
        entry = data[offset : offset + 14]
        name  = entry[0:8].decode("ascii", "replace").rstrip()
        type_ = chr(entry[8])
        length = entry[9] | (entry[10] << 8) | (entry[13] << 16)
        param  = entry[11] | (entry[12] << 8)
        file_table.append((name, type_, length, param))
        offset += 14

    files = {}
    for (name, type_, length, param) in file_table:
        files[name + "." + type_] = data[offset : offset + length]
        offset += length

    # offset should now be at the optional checksum byte (or at EOF)
    return files
```

The corresponding .TRD reader is slightly more complex because it must parse the directory, decode the (cylinder, side, sector) tuples, and translate them into file offsets using the formula in §2.2. Refer to [trd_disk_format.md §6](trd_disk_format.md) for the directory-entry layout.

---

## §6. Cross-references and License

### 6.1 Within the storage section

- [mfm_encoding.md](mfm_encoding.md) — the MFM signal layer that physically underlies every TR-DOS sector.
- [fdc_vg93.md](fdc_vg93.md) — the WD1793 / KR1818VG93 floppy controller chip that reads and writes TR-DOS disks.
- [beta_disk_interface.md](beta_disk_interface.md) — the host-side hardware that connects the WD1793 to the Spectrum.
- [trd_disk_format.md](trd_disk_format.md) — the on-disk logical format that .TRD and .SCL files capture.

### 6.2 Adjacent format articles

- [dsk_fdi_formats.md](dsk_fdi_formats.md) — .DSK / .EDSK / .FDI: preservation-level formats that can capture non-standard sector layouts and (in .EDSK's case) some weak-bit patterns.
- [udi_format.md](udi_format.md) — .UDI: a universal disk image format with strong preservation properties.
- [scp_format.md](scp_format.md) — .SCP: a flux-level format from the SuperCard Pro hardware, capable of capturing every magnetic transition on the disk surface.
- [plus3_dos_format.md](plus3_dos_format.md), [cpm_disk_format.md](cpm_disk_format.md), [opus_discovery_format.md](opus_discovery_format.md) — the on-disk formats used by non-TR-DOS Spectrum disk systems.

### 6.3 Demoscene and reverse engineering

- (Reverse engineering / unpacking) Disk-based intros and demos that use custom loaders: see the 05_reversing section for techniques. A .SCL of such a demo will work only if the loader reads via standard TR-DOS calls; demos that do raw sector I/O require a .TRD (or .EDSK / .SCP) image to boot.
- (Demoscene) Software releases that were originally distributed on TR-DOS disks: see the 07_demoscene section for the history of disk-based demoscene releases.

### 6.4 External references

- **`trd.speccy.info`** — a large online archive of TR-DOS disk software, distributed as .TRD and .SCL files.
- **World of Spectrum (`worldofspectrum.org`)** — the canonical Western Spectrum archive; many disk titles are available as .TRD files.
- **`zx-pk.ru`** — the Russian Spectrum community forum; the origin of many .TRD / .SCL conventions and tools.
- **`zxevo.ru`** — the ZX Evolution community; documentation for the .TRD / .SCL formats and their extensions.
- **ZX-Blockeditor** (Simon Owen) — the de facto .TRD/.SCL editor; useful for examining the byte-level structure of any .TRD or .SCL file.

### 6.5 License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you give appropriate credit and distribute derivative works under the same license.

"Spectrum", "TR-DOS", "ZX Spectrum", "+3", and other trademarks are the property of their respective owners and are used here for identification and educational purposes only.
