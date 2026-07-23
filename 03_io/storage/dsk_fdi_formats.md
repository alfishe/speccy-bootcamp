# .DSK / .EDSK / .FDI Disk Image Formats

**Scope:** The three preservation-level disk image formats that can capture **non-standard** sector layouts: **.DSK** (the original CPCEMU "MV - CPC" format), **.EDSK** (the extended CPC DSK format), and **.FDI** (Vincent Joguin's "Full Disk Image"). These are the formats used by archivists to preserve disks that .TRD and .SCL cannot represent — disks with non-standard sector sizes, non-standard sector IDs, deliberate corruption, or copy-protection tricks.

**Audience:** Emulator authors, archival tool authors, copy-protection researchers, and demoscene coders who need to image non-standard disks or run disk software that depends on non-standard sector layouts.

**Prerequisites:** A working understanding of the MFM signal layer (sector IDs, address marks, data marks), and ideally familiarity with the simpler .TRD / .SCL formats (see [trd_scl_formats.md](trd_scl_formats.md)). The on-disk MFM format is covered in [mfm_encoding.md](mfm_encoding.md).

**Depth:** Deep. Byte-level layout of all three formats, with worked examples and detailed discussion of the trade-offs between them. Particular attention to .EDSK, which is the de facto standard for non-TR-DOS Spectrum disk imaging (CP/M disks, +3DOS disks, Opus Discovery disks, copy-protected originals).

---

## Roadmap

| Section | Topic | Length |
|---|---|---|
| §1 | What .DSK / .EDSK / .FDI Are — purpose, history, when to use each | short |
| §2 | The .DSK Format — the original "MV - CPC" sector-level image | medium |
| §3 | The .EDSK Format — extended format with per-track size tables | medium |
| §4 | The .FDI Format — Vincent Joguin's Full Disk Image | medium |
| §5 | Tools and Converters — emulators, editors, format converters | short |
| §6 | Cross-references and License | short |

Reading order: §1 → §2 → §3 → §4 → §5, with §6 as supplementary material.

---

## §1. What .DSK / .EDSK / .FDI Are

### 1.1 Why preservation-level formats?

The simpler .TRD and .SCL formats (see [trd_scl_formats.md](trd_scl_formats.md)) assume a "well-behaved" TR-DOS disk: every track has exactly 10 sectors of 512 bytes each, every sector is numbered 1–10, every sector has the standard data mark, and the directory layout follows the TR-DOS 5.03 conventions. This is sufficient for 95% of TR-DOS software, but it fails for:

- **CP/M disks** on the Spectrum +3, which use a different sector layout (typically 9 sectors of 512 bytes per track on side 0, and 5 sectors of 1024 bytes on side 1, due to the +3's "reverse side" hardware trick).
- **+3DOS disks** with non-standard geometry (e.g., third-party formatters that used 10-sector / 512-byte layouts instead of the +3's standard 9-sector layout).
- **Opus Discovery disks** (a Western alternative to TR-DOS), which use yet another sector layout.
- **Copy-protected disks** that use non-standard sector IDs (e.g., sector 0xA1 on cylinder 5 side 0), non-standard sector sizes (e.g., 128-byte, 1024-byte, or 4096-byte sectors), weak bits, or deliberately corrupted CRCs to defeat naive disk-copy programs.

For all of these cases, **a sector-level format that preserves the per-track layout is needed**. The .DSK / .EDSK / .FDI formats are the answer: they store the disk at the **per-sector** level (with sector IDs, sizes, data marks, and — in some cases — error flags), rather than at the per-byte level of .TRD / .SCL.

Note that .DSK / .EDSK / .FDI are **not** flux-level formats — they cannot capture every magnetic transition. For true flux-level preservation (the gold standard for archival work), see [scp_format.md](scp_format.md) and [udi_format.md](udi_format.md).

### 1.2 The three formats at a glance

| Format | Origin | Year | Magic string | Captures non-standard sector IDs? | Captures weak/CRC errors? |
|---|---|---|---|---|---|
| **.DSK** | CPCEMU emulator (Amstrad CPC) | 1993 | `"MV - CPC"` | No (assumes uniform layout) | No |
| **.EDSK** | Extended CPC DSK format (community extension) | 1996 | `"EXTENDED CPC DSK File Format"` | Yes (per-track tables) | Yes (per-sector flags) |
| **.FDI** | Vincent Joguin (Caprice emulator) | 1997 | `"FDI"` magic + version | Yes (per-sector metadata) | Yes (information-encoding scheme) |

The .DSK format was the first, but its limitations (it could only represent uniform-sector disks) quickly led to the .EDSK extension. .FDI is an alternative format with similar expressive power to .EDSK but a more general (and more complex) information model.

In the Spectrum community:

- **.DSK** is rarely used directly, because most non-TR-DOS Spectrum disks (CP/M, +3DOS) have non-uniform layouts that .DSK cannot represent.
- **.EDSK** is the de facto standard for non-TR-DOS Spectrum disk imaging. Almost every +3 disk image in the World of Spectrum archive is in .EDSK format.
- **.FDI** is less common but still in use, particularly in tools that originated in the Amstrad CPC community.

### 1.3 A short history

The **.DSK** format was created in 1993 by the authors of the **CPCEMU** Amstrad CPC emulator (Marco Casteleijn and Ulrich von Hassel). The format was designed to capture the simple, uniform-sector layout of standard Amstrad CPC data disks. The CPCEMU header format (`"MV - CPC"` magic) was simple, contained a single track-count and a single sector-count, and assumed that every track had the same layout.

The **.EDSK** extension was developed in 1996 by the Amstrad CPC demoscene community (the "CPC emulators" mailing list). The extension introduced a new magic string (`"EXTENDED CPC DSK File Format"`) and a per-track size table, allowing different tracks to have different sizes. Later additions introduced per-sector flags for errors, bad CRCs, and weak bits, making the format suitable for representing copy-protected disks.

The **.FDI** format was created in 1997 by **Vincent Joguin** (author of the Caprice CPC emulator and the Disk2FDI imaging tool). Joguin designed .FDI as a more general and more rigorously-specified alternative to .EDSK. The .FDI format uses a single information block (containing the disk's geometry, the locations of weak-bit regions, and other metadata) plus a raw sector-data block, in a structure that is independent of any particular FDC's quirks.

All three formats are still in active use today, and most Spectrum and CPC emulators can read all three. For archival work, .EDSK is preferred over .DSK (since .DSK cannot represent non-uniform layouts) and over .FDI (since .EDSK is more widely supported).

### 1.4 Scope

This article covers the byte-level layout of .DSK, .EDSK, and .FDI files. The on-disk logical formats that these files capture (CP/M, +3DOS, Opus Discovery) are covered in their own articles: [cpm_disk_format.md](cpm_disk_format.md), [plus3_dos_format.md](plus3_dos_format.md), [opus_discovery_format.md](opus_discovery_format.md). The flux-level formats that go beyond what these formats can capture are covered in [scp_format.md](scp_format.md) and [udi_format.md](udi_format.md).


## §2. The .DSK Format

### 2.1 Overview

A **.DSK file** is a sector-level image of a floppy disk, with a 256-byte header followed by the raw bytes of every track and every sector on the disk. The format was designed for uniform-sector disks: every track has the same number of sectors, the same sector sizes, and the same sector IDs.

The .DSK file consists of:

1. **A 256-byte disk information block (DIB)** containing the magic string `"MV - CPC"`, the disk's track count, side count, sector count, sector size, and other parameters.
2. **One track information block (TIB) per track**, each containing a per-track header with the sector IDs followed by the sector data.

The .DSK format does **not** support per-track variation in sector count or sector size — those are stored once in the DIB and assumed to apply uniformly to every track. This is the key limitation that .EDSK (§3) was designed to fix.

### 2.2 The 256-byte disk information block (DIB)

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 34 | **Magic string** | ASCII: `"MV - CPC"` followed by zeros. Identifies the file as a "plain" .DSK. |
| 34 | 1 | **Creator** (start of a 14-byte field) | A 14-byte ASCII string identifying the tool that wrote the file (e.g., `"Caprice    "`). Padded with spaces. |
| 48 | 1 | **Tracks** | Number of tracks (cylinders × sides, since each "track" in .DSK terminology is one head pass). For an 80-track 2-sided disk, this is 160 (80 × 2). For a 40-track 1-sided disk, this is 40. |
| 49 | 1 | **Sides raw** | Number of heads: 1 or 2. (Sometimes 0 or 128 for legacy reasons.) |
| 50 | 2 | **Track size** | The size in bytes of each track's TIB (track information block), including the TIB header. For a 9-sector × 512-byte track with the standard 0x100 TIB header, this would be `0x100 + 9 × 0x200 = 0x1300`. **All tracks must have the same size** — this is the .DSK limitation. |
| 52 | 2 | **Number of sectors per track** | The same value for every track. |
| 54 | 2 | **Sector size** | The size in bytes of every sector (typically 512). |
| 56 | 2 | **Gap 3 length** | The formatted gap-3 value used by the WD1772 / WD1773 when writing this disk (see [fdc_vg93.md](fdc_vg93.md)). |
| 58 | 2 | **Gap 5 length** | The formatted gap-5 (post-index) value. |
| 60 | 1 | **Filler byte** | The byte value written to every sector on `*FORMAT` (typically `0xE5` for CP/M, `0x00` for TR-DOS). |
| 61 | 195 | **(unused, reserved)** | Zeros. |

The 256-byte DIB is **always** at offset 0 in the .DSK file. The remaining bytes of the file (offset 256 onward) are the track information blocks.

### 2.3 The track information block (TIB)

Each track information block consists of a per-track header followed by the per-sector data. The per-track header is 0x100 bytes (256 bytes):

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 12 | **Track-header magic** | ASCII: `"Track-Info\r\n"`. Always exactly these 12 bytes. |
| 12 | 1 | **(reserved)** | Zeros. |
| 13 | 1 | **(reserved)** | Zeros. |
| 14 | 1 | **Track number** | The cylinder number (0–79 for an 80-track disk). |
| 15 | 1 | **Side number** | 0 or 1. |
| 16 | 2 | **(reserved)** | Zeros. |
| 18 | 1 | **Sector size code** | 0=128, 1=256, 2=512, 3=1024, ..., 6=8192 (encoded as `2^(code+7)`). |
| 19 | 1 | **Number of sectors** | Should match the DIB's "sectors per track" field. |
| 20 | 1 | **Gap 3 length** | Formatted gap-3 value. |
| 21 | 1 | **Filler byte** | Formatted filler value. |
| 22 | 2 | **(reserved)** | Zeros. |
| 24 | 8 × N | **Sector info list** | N entries (one per sector), each 8 bytes. See §2.4 below. |

After the per-track header comes the sector data: N sectors × `sector_size` bytes, concatenated in the order specified by the sector info list.

### 2.4 The 8-byte sector info entry

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 1 | **Track (cylinder)** | The sector's cylinder number as written in the sector ID field on disk. May differ from the TIB's track number for protection tricks (e.g., sector IDs that say "track 5" on a track-6 cylinder). |
| 1 | 1 | **Side (head)** | The sector's head number as written in the sector ID field. May differ from the TIB's side number. |
| 2 | 1 | **Sector ID** | The sector number as written in the sector ID field. Typically 1–N, but can be any byte value for protection tricks. |
| 3 | 1 | **Sector size code** | 0=128, 1=256, 2=512, ..., 6=8192. Should match the TIB's sector size code, but in some non-standard disks different sectors on the same track have different sizes. |
| 4 | 1 | **FDC status byte 1** (ST1) | The WD1772/NEC765 status byte 1 for this sector. Bit 7 = end-of-cylinder, bit 5 = CRC error in data, bit 4 = data mark not found, bit 2 = no data, bit 1 = write-protect. For a clean disk, this is `0x00`. |
| 5 | 1 | **FDC status byte 2** (ST2) | The WD1772/NEC765 status byte 2 for this sector. Bit 5 = CRC error in ID field, bit 2 = sector not found, bit 1 = bad cylinder, bit 0 = data mark type. For a clean disk, this is `0x00`. |
| 6 | 2 | **(unused)** | Zeros. |

The ST1 and ST2 bytes are how .DSK (and .EDSK) record per-sector error information: a non-zero value indicates a sector that the FDC could not read cleanly, which is the basic mechanism for representing copy-protected or damaged sectors.

### 2.5 Total file size

The total file size of a .DSK is:

```
file_size = 256 + tracks * track_size
```

For a standard 80-track 2-sided disk with 10 sectors of 512 bytes per track:

```
track_size = 256 (TIB header) + 10 * 512 (sector data) = 5376 bytes
file_size = 256 + 160 * 5376 = 860,416 bytes
```

For a 40-track 1-sided disk with 9 sectors of 512 bytes:

```
track_size = 256 + 9 * 512 = 4864 bytes
file_size = 256 + 40 * 4864 = 194,816 bytes
```

Note that the per-track TIB header adds 256 bytes of overhead per track — a small but non-negligible overhead compared to the corresponding .TRD file (which has no per-track headers).

### 2.6 Limitations of .DSK

The .DSK format has several limitations:

1. **All tracks must have the same size.** This means disks with mixed-sector layouts (common in copy-protected disks) cannot be represented.
2. **The DIB's "track size" field is a single 16-bit value.** If a disk has tracks with very different layouts, the writer must choose the largest track's size, padding the smaller tracks — this is wasteful and fragile.
3. **No support for weak-bit patterns** that vary between reads. The .DSK format assumes that a sector's data is deterministic; a real-world weak sector (which reads as different bytes on each revolution) cannot be represented.
4. **No support for missing sectors** (a track with fewer than the nominal number of readable sectors). The writer must either omit the missing sector (which breaks the per-track size invariant) or pad with zero data (which is indistinguishable from a real all-zero sector).

These limitations were the motivation for the .EDSK extension.

### 2.7 When .DSK is still useful

Despite its limitations, the .DSK format remains useful for:

- **Standard +3DOS disks** that have a uniform 9-sector × 512-byte layout on every track. Such disks can be losslessly stored as .DSK files.
- **Cross-platform interchange** with Amstrad CPC emulators, where .DSK is still the native format.
- **Disk-image manipulation** that requires per-sector addressing (e.g., reading sector 3 of track 5 side 1) without parsing a directory structure.

For any disk that does not fit the "uniform layout" assumption, .EDSK is required.


## §3. The .EDSK Format

### 3.1 Overview

The **.EDSK** (Extended DSK) format is a strict superset of the .DSK format. It uses a different magic string in the DIB and replaces the single "track size" field with a **per-track size table**, allowing each track to have its own size. All other aspects of the format — the 256-byte DIB, the per-track TIB, the 8-byte sector info entries — are identical to .DSK.

A .EDSK file can represent:

- Disks with mixed sector sizes per track.
- Disks with mixed sector counts per track.
- Disks with deleted / unreadable sectors (via the ST1/ST2 status bytes).
- Disks with weak / fuzzy data (via the special `0xFF` size code, see §3.5).
- Disks with deliberately bogus sector IDs (used by some copy-protection schemes).

The .EDSK format is backwards-compatible: a .DSK reader that only looks at the DIB's "track size" field can still read an .EDSK file, but it will get incorrect results for non-uniform tracks. Modern readers always check the magic string to distinguish .DSK from .EDSK.

### 3.2 The .EDSK disk information block (DIB)

The DIB layout is identical to .DSK, except for two changes:

| Offset | Length | Field | .DSK value | .EDSK value |
|---|---|---|---|---|
| 0 | 34 | Magic | `"MV - CPC"` (8 chars + zeros) | `"EXTENDED CPC DSK File Format"` (exactly 34 chars) |
| 50 | 2 | Track size | Single 16-bit track size value | **High byte = 0, low byte = 0** (per-track sizes are in the per-track size table) |

In .DSK, the "track size" field at offset 50 of the DIB is a single 16-bit value that applies to every track. In .EDSK, this field is set to zero, signalling that the file contains a separate **per-track size table**.

### 3.3 The per-track size table

The per-track size table starts at offset 256 in the .EDSK file (immediately after the 256-byte DIB) and contains N × 1-byte entries (one per track), where each entry is the size of the track's TIB in **256-byte units**. The full track size is therefore `entry * 256` bytes.

- Per-track size byte `0x13` → track size = `0x13 * 0x100` = `0x1300` = 4864 bytes.
- Per-track size byte `0x00` → track size = 0 (i.e., the track is missing or unformatted).

Because each entry is a single byte (and the size unit is 256 bytes), the maximum TIB size is `0xFF * 0x100` = 65,280 bytes, which is more than enough for any real floppy track (the largest common track is ~12 KB).

The per-track TIBs follow immediately after the per-track size table. The TIB for track 0 starts at offset `256 + N`, the TIB for track 1 starts at `256 + N + size[0]`, and so on.

To read the disk in order:

```python
# .EDSK reader pseudocode
dib = data[0:256]
magic = dib[0:34].rstrip(b"\x00 ")  # "EXTENDED CPC DSK File Format"
n_tracks = dib[48]
track_size_bytes = dib[50]  # should be 0x00 in .EDSK

track_sizes = [data[256 + i] * 256 for i in range(n_tracks)]  # one byte per track
tib_offset = 256 + n_tracks

for i, size in enumerate(track_sizes):
    if size == 0:
        continue  # missing / unformatted track
    tib = data[tib_offset : tib_offset + size]
    parse_tib(tib)
    tib_offset += size
```

### 3.4 The .EDSK track information block (TIB)

The TIB layout is identical to .DSK (§2.3). The TIB starts with the 12-byte `"Track-Info\r\n"` magic, followed by the track's metadata, followed by the sector info list (8 bytes per sector), followed by the sector data.

The difference in .EDSK is that the TIB may have **fewer** sectors than the DIB's "sectors per track" field (the DIB field is now only a default), and the sector data block may be **shorter** than `sectors_per_track * sector_size` if some sectors are missing or weak.

### 3.5 Per-sector error flags

The .EDSK format defines two special patterns in the 8-byte sector info entry to encode error conditions:

| ST1 byte | ST2 byte | Meaning |
|---|---|---|
| `0x00` | `0x00` | Clean sector — data is valid. |
| `0x20` | `0x20` | **CRC error** in the data field. The sector's data is read but is flagged as having a bad CRC; the data may still be usable. |
| `0x20` | `0x20` (with size code = `0xFF`) | **Weak / fuzzy sector**. The sector's data is non-deterministic — different bytes are read on each revolution. The data block in the .EDSK file contains a "representative" sample. |
| `0x04` | `0x01` | **Sector not found**. The FDC could not find a sector with the requested ID. The sector's data block is empty. |
| `0x04` | `0x02` | **Bad cylinder** — the cylinder field in the sector ID did not match the expected value. |
| `0x01` | `0x00` | **Missing address mark** — the FDC found the sector ID but no data mark. |
| `0x80` | `0x00` | **End-of-cylinder** — the FDC tried to read past the last sector on the track. |

These flags allow .EDSK to represent copy-protected disks: a protection scheme that, say, deliberately corrupts the CRC on cylinder 12 side 0 sector 5 would be encoded as ST1=`0x20`, ST2=`0x20` for that sector in the .EDSK file.

### 3.6 The "weak sector" extension

A weak sector (sometimes called a "fuzzy" sector) is one whose data is non-deterministic: each time the FDC reads it, it gets different bytes. This is a common copy-protection technique, achieved on real disks by writing two valid MFM streams that overlap (so the read amplifier sees a different one each revolution) or by writing deliberately weak flux transitions.

The .EDSK format's convention for weak sectors is:

- The sector's data size in the TIB is **the full nominal size** (e.g., 512 bytes for a sector size code of 2).
- The sector's data in the .EDSK file contains **a representative sample** of the data (typically the bytes from the first read).
- The ST1/ST2 flags are set to `0x20 / 0x20` (CRC error).
- The sector size code in the sector info entry may be set to `0xFF` (special "weak" marker) in some implementations, though this is non-standard.

A sophisticated .EDSK reader that detects this pattern should **emulate the non-determinism**: each time the sector is read, return slightly different bytes (e.g., randomly toggle one bit per read), so that the protection scheme in the original software still works. Less sophisticated readers simply return the same data every time, which may defeat the protection scheme or simply cause the software to misbehave.

### 3.7 When .EDSK is the right choice

Use .EDSK when:

- The disk has **non-uniform tracks** (different sector counts, different sector sizes per track) — common in CP/M and +3DOS disks.
- The disk has **deliberate corruption** (CRC errors, missing sectors, bogus sector IDs) for copy protection.
- The disk has **weak / fuzzy sectors** that you want to preserve (with the understanding that the .EDSK file will only contain a single representative sample, not the full flux pattern).
- You need **maximum emulator compatibility** for archival purposes — .EDSK is the de facto standard for Spectrum +3 disk imaging in the World of Spectrum archive.

The .EDSK format is preferred over .DSK for almost all Spectrum disk imaging tasks, because .EDSK is a strict superset of .DSK and the cost (one extra byte per track in the size table) is negligible.

### 3.8 When .EDSK is not enough

The .EDSK format still has some limitations:

1. **No true flux representation.** The .EDSK format captures the sector data and the per-sector status flags, but it cannot represent the raw flux transitions on the disk surface. If a protection scheme depends on a specific bit pattern at the flux level (rather than at the sector level), .EDSK cannot capture it.
2. **No multi-revolution sampling for weak sectors.** The .EDSK format stores only one representative sample for weak sectors. A more rigorous preservation would store several revolutions' worth of data to characterize the non-determinism.
3. **No timing information.** The .EDSK format discards all timing information (bit-cell widths, spindle-speed variation, jitter). For most software this is fine, but for software that uses unusual bit timings as part of a protection scheme, this is a loss.

For true flux-level preservation, use .SCP (see [scp_format.md](scp_format.md)) or .UDI (see [udi_format.md](udi_format.md)).


## §4. The .FDI Format

### 4.1 Overview

The **.FDI** (Full Disk Image) format was created in 1997 by **Vincent Joguin** as a more rigorous and general alternative to .DSK / .EDSK. The .FDI format separates the disk's geometry and metadata (stored in an "information block" at the start of the file) from the raw sector data (stored in a separate "data block" at the end of the file). This separation makes the format more extensible and more independent of any particular FDC's quirks.

A .FDI file consists of:

1. **A 14-byte header** containing the magic string `"FDI"` plus a version number and the offsets to the information block and the data block.
2. **An information block** (variable length) containing the disk's geometry and a per-track description table.
3. **A data block** (variable length) containing the raw sector data for every track.

The .FDI format's key design feature is the **information block**, which uses a tagged-structure encoding (similar to a TIFF IFD or a MIDI chunk) to describe the disk's geometry, weak-bit patterns, and other metadata in a self-describing way. New information tags can be added without breaking old readers.

### 4.2 The 14-byte header

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 3 | **Magic** | ASCII `"FDI"`. |
| 3 | 1 | **Reserved / padding** | Typically `0x00`. |
| 4 | 4 | **Information block offset** (LE) | The byte offset in the file where the information block starts (typically 14). |
| 8 | 4 | **Data block offset** (LE) | The byte offset in the file where the data block starts. |
| 12 | 2 | **Information block length** (LE) | The size in bytes of the information block. |

The header is followed immediately by the information block (at offset 14, unless the writer chose to put it elsewhere), and the data block is at the offset given by the data-block offset field. The two blocks are independent and may be in either order.

### 4.3 The information block

The information block is a sequence of tagged entries. Each tagged entry has the form:

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 1 | **Tag ID** | An integer that identifies the type of information. |
| 1 | 4 | **Tag length** (LE) | The length of the tag's data in bytes. |
| 5 | N | **Tag data** | The tag's data, format depends on the tag ID. |

The most important tag IDs are:

| Tag ID | Name | Data content |
|---|---|---|
| `0x00` | **End of information block** | No data; signals the end of the tag list. |
| `0x01` | **Cylinders** | 4 bytes (LE): number of cylinders on the disk. |
| `0x02` | **Sides** | 4 bytes (LE): number of sides per cylinder (1 or 2). |
| `0x03` | **Disk geometry** | A description of the per-cylinder, per-side sector layout. |
| `0x04` | **Weak-bit pattern** | A list of (track, side, sector, offset, length) tuples describing regions of the disk where the data is non-deterministic. |
| `0x05` | **Comment** | A free-form ASCII string (e.g., the disk's label, the imaging tool's name, the date of imaging). |
| `0x06` | **Creator** | A 4-byte magic identifying the imaging tool that wrote the file. |
| `0x07` | **CRC errors** | A list of sectors with deliberately corrupted CRCs (for copy-protected disks). |
| `0x08` | **Bogus sector IDs** | A list of sectors whose sector-ID field on disk does not match the cylinder/side they are physically on. |
| `0x09` | **Track sizes** | The per-track size table (analogous to .EDSK's per-track size table). |

A reader that encounters an unknown tag should **skip it** (using the length field) rather than reject the file. This makes the format extensible without breaking compatibility.

### 4.4 The data block

The data block contains the raw sector data for every track on the disk, in order:

1. Cylinder 0, side 0: all sectors concatenated.
2. Cylinder 0, side 1: all sectors concatenated.
3. Cylinder 1, side 0: all sectors concatenated.
4. ... and so on.

Within each track, sectors are stored in the order they appear on the physical track (typically by sector ID, but the order is determined by the information block's per-track sector description).

The data block does **not** contain the sector ID headers, address marks, or CRCs — only the data payload of each sector. The IDs and other metadata are stored in the information block.

### 4.5 What .FDI preserves that .EDSK doesn't

The .FDI format's main advantages over .EDSK are:

1. **Multi-region weak-bit support.** The .FDI format can describe weak regions at arbitrary offsets within sectors (not just "weak sector" as a whole), via the `0x04` tag's (offset, length) tuples. This is more precise than .EDSK's per-sector weak flag.
2. **Free-form metadata.** The `0x05` (Comment) and `0x06` (Creator) tags allow arbitrary text to be stored with the disk image, which is useful for archival provenance.
3. **Extensibility.** Unknown tags are skipped, so the format can grow without breaking old readers. .EDSK, by contrast, requires new conventions to be encoded in the ST1/ST2 status bytes, which is more fragile.
4. **Independent of any FDC.** The .FDI format does not use the WD1772 or NEC765 status byte conventions; it has its own per-sector metadata model. This makes the format more portable across different FDC families.

### 4.6 What .FDI does NOT preserve

Despite these advantages, .FDI still has limitations:

1. **No flux representation.** Like .EDSK, .FDI stores sector data, not raw flux transitions. For flux-level preservation, use .SCP or .UDI.
2. **Less tool support.** The .FDI format is less widely supported in the Spectrum community than .EDSK. Most Spectrum emulators that read .FDI also read .EDSK, but not vice versa.
3. **More complex to parse.** The tagged-structure information block is more complex than .EDSK's fixed-size per-track headers. Some simple readers prefer .EDSK's simpler format.

### 4.7 When .FDI is the right choice

Use .FDI when:

- You need the more precise weak-region description that .FDI's `0x04` tag provides.
- You are working with Amstrad CPC disk images and need cross-platform compatibility with CPC tools (which historically favored .FDI).
- You need to store metadata about the imaging process (date, tool, comment) alongside the image data.

For most Spectrum-specific archival work, .EDSK is preferred due to its wider tool support. For flux-level preservation, use .SCP or .UDI.


## §5. Tools and Converters

### 5.1 Emulators that read .DSK / .EDSK / .FDI

| Emulator | Platform | .DSK | .EDSK | .FDI | Notes |
|---|---|---|---|---|---|
| **FUSE** | Linux / Win / macOS | Yes | Yes | Yes | The standard open-source emulator for the Spectrum +3; reads .DSK and .EDSK natively. |
| **ZEsarUX** | Linux / Win / macOS | Yes | Yes | Yes | Full-featured; supports all three formats and conversion between them. |
| **Spectaculator** | Windows | Yes | Yes | Yes | Commercial, well-maintained. |
| **UnrealSpeccy** | Windows | Yes | Yes | No | TR-DOS-focused; reads .DSK and .EDSK for non-TR-DOS disks. |
| **Caprice** (CPC emulator) | Multiple | Yes | Yes | Yes | The reference emulator for the Amstrad CPC; .FDI is one of Caprice's native formats. |
| **CPCE** / **WinAPE** (CPC) | Multiple | Yes | Yes | Yes | Other major CPC emulators, all read the three formats. |

The CPC community uses .DSK / .EDSK / .FDI as its primary formats; the Spectrum community borrows them for +3DOS / CP/M disk imaging, where .TRD / .SCL are not applicable.

### 5.2 Standalone .DSK / .EDSK / .FDI tools

- **ZX-Blockeditor** (Simon Owen) — supports .DSK, .EDSK, and (to a limited extent) .FDI, plus .TRD, .SCL, and many other formats. The de facto standard for archival work.
- **Disk2FDI** (Vincent Joguin) — the original .FDI imaging tool, designed to run from MS-DOS and image real floppy disks via a PC's onboard FDC.
- **HxCFloppyEmulatorTool** — reads and writes .DSK / .EDSK / .FDI, and can write any of them to a Gotek / HxC USB-floppy emulator.
- **libdsk** (a Unix library) — supports .DSK and .EDSK via plugins; can read non-standard CPC and Spectrum +3 disks from real PC floppy drives.
- **cwtool** (raw flux tool) — can produce .DSK / .EDSK files from raw flux captured by KryoFlux or SuperCard Pro hardware.

### 5.3 Cross-format conversion

- **.EDSK ↔ .FDI**: ZX-Blockeditor and HxCFloppyEmulatorTool can convert between these formats, but the conversion may lose information (e.g., .FDI's per-offset weak regions become per-sector weak flags in .EDSK).
- **.DSK → .EDSK**: trivial, since .EDSK is a strict superset of .DSK. Every .DSK reader can read .EDSK files that happen to have a uniform per-track size table.
- **.EDSK → .DSK**: only possible if the .EDSK file has uniform track sizes; otherwise, the conversion is lossy or impossible.
- **.SCP / .UDI → .DSK / .EDSK**: the upstream flux format is parsed to extract the per-sector data and ID fields, which are then written to the sector-level format. See [scp_format.md](scp_format.md) for details on the flux-level workflow.

### 5.4 Format validation

A reader should validate the following:

- For **.DSK**: the magic string at offset 0 is `"MV - CPC"`, and the file size is `256 + tracks * track_size`.
- For **.EDSK**: the magic string at offset 0 is `"EXTENDED CPC DSK File Format"` (exactly 34 bytes), and the file size matches the sum of the per-track size table.
- For **.FDI**: the magic string at offset 0 is `"FDI"`, the information block offset and data block offset point to valid positions within the file, and the information block's tags are well-formed.

Most modern readers emit warnings for malformed files but rarely hard-error.

### 5.5 The "ST1/ST2 trick" in .EDSK

A common hack in .EDSK-land is to set ST1=`0x20` and ST2=`0x20` on sectors whose data is known to be CRC-corrupted but should be readable. The emulator should emulate the WD1772's behavior: read the data but set the CRC-error bit in the status register. Software that reads the sector via `READ SECTOR` will see the data and the CRC-error bit; software that does its own MFM decoding will see the actual corrupted bytes.

This is the mechanism by which .EDSK preserves disks with deliberately corrupted CRCs (a common copy-protection technique).

---

## §6. Cross-references and License

### 6.1 Within the storage section

- [mfm_encoding.md](mfm_encoding.md) — the MFM signal layer that the .DSK / .EDSK / .FDI sector IDs refer to.
- [fdc_vg93.md](fdc_vg93.md) — the WD1793 / KR1818VG93 floppy controller chip that originally wrote the sectors preserved in .DSK / .EDSK / .FDI files.
- [beta_disk_interface.md](beta_disk_interface.md) — the host-side hardware for TR-DOS disks (whose non-protected disks are typically stored as .TRD / .SCL, not .DSK).
- [plus3_floppy.md](plus3_floppy.md) — the +3's floppy hardware; +3 disks are typically stored as .DSK / .EDSK.
- [trd_disk_format.md](trd_disk_format.md), [trd_scl_formats.md](trd_scl_formats.md) — the simpler formats used for TR-DOS disks.

### 6.2 Adjacent format articles

- [udi_format.md](udi_format.md) — .UDI: a universal disk image format that goes beyond sector-level to capture more details.
- [scp_format.md](scp_format.md) — .SCP: a true flux-level format, the gold standard for archival preservation.
- [plus3_dos_format.md](plus3_dos_format.md) — the +3DOS logical format that .DSK / .EDSK files containing +3 disks capture.
- [cpm_disk_format.md](cpm_disk_format.md) — the CP/M logical format that .DSK / .EDSK files containing CP/M disks capture.
- [opus_discovery_format.md](opus_discovery_format.md) — the Opus Discovery logical format (Western alternative to TR-DOS / +3DOS).
- [disk_format_overview.md](disk_format_overview.md) — a comparative overview of all Spectrum floppy formats.

### 6.3 Reverse engineering and demoscene

- (Reverse engineering / copy-protection) The .EDSK weak-sector extension is the standard way to preserve copy-protected disks at the sector level. For deeper analysis (flux-level patterns, multi-revolution sampling), see [scp_format.md](scp_format.md). The 05_reversing section covers the techniques used to bypass such protection in software.
- (Demoscene) .DSK / .EDSK are rarely used for TR-DOS demoscene releases (which prefer .TRD / .SCL), but they are common for +3 / CP/M demoscene releases.

### 6.4 External references

- **Marat Fayzullin's .DSK documentation** — the canonical reference for the .DSK / .EDSK format, including the per-track size table and the ST1/ST2 conventions.
- **Vincent Joguin's .FDI specification** — the canonical reference for the .FDI format, available at the Disk2FDI website.
- **Simon Owen's ZX-Blockeditor** — the de facto cross-format disk-image editor, supporting .DSK / .EDSK / .FDI / .TRD / .SCL and many other formats.
- **libdsk** — a Unix library for reading non-standard floppy formats; useful for converting between .DSK / .EDSK and other formats.
- **"CPC Wiki"** (the Amstrad CPC community wiki) — extensive documentation on .DSK / .EDSK / .FDI, including the history of each format and the various extensions in use.

### 6.5 License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you give appropriate credit and distribute derivative works under the same license.

"Spectrum", "+3", "ZX Spectrum", "Amstrad", "CPC", "TR-DOS", "+3DOS", "CP/M", and other trademarks are the property of their respective owners and are used here for identification and educational purposes only.
