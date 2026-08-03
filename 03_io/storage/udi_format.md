# .UDI Universal Disk Image Format

**Scope:** The **.UDI** (Universal Disk Image) format — a sector-level format designed to be **universal** across different disk modulation schemes (MFM, FM, GCR, etc.) and different floppy controller families (WD177x, NEC765, uPD765, etc.). The .UDI format is used by a subset of Spectrum emulators and archival tools, particularly in the Russian Spectrum community.

**Audience:** Emulator authors, archival tool authors, and demoscene coders who need a format that captures more than .TRD / .SCL but is simpler than .SCP / .UID. The .UDI format is particularly suited to disks that combine multiple sector layouts or use non-MFM encoding.

**Prerequisites:** A working understanding of the MFM signal layer (sector IDs, address marks, data marks), and ideally familiarity with .DSK / .EDSK (see [dsk_fdi_formats.md](dsk_fdi_formats.md)). The on-disk MFM format is covered in [mfm_encoding.md](mfm_encoding.md).

**Depth:** Deep. Byte-level layout of the .UDI format, including the header, the per-track descriptor table, and the per-track data blocks. Worked examples and discussion of when .UDI is preferable to .EDSK or .SCP.

---

## §1. What .UDI Is

### 1.1 Why a "universal" format?

The .DSK / .EDSK formats (see [dsk_fdi_formats.md](dsk_fdi_formats.md)) are tied to the WD177x FDC family and assume MFM encoding throughout. This is sufficient for most Spectrum and Amstrad CPC disks, but it fails for:

- **GCR-encoded disks** (used by the Commodore 64, Apple II, and some other 8-bit systems) — the .DSK / .EDSK format cannot represent GCR's 5-in-8 / 6-in-8 encoding.
- **FM-encoded disks** (single-density, used by some early CP/M systems) — the .DSK / .EDSK format assumes MFM throughout.
- **Mixed-modulation disks** that combine MFM and FM on different tracks (some protection schemes use this trick).
- **Disks written by FDC families that do not match the WD177x status-byte conventions** (e.g., the NEC765 used by the IBM PC, or the uPD765 used by MSX machines).

The .UDI format was designed to address these gaps. Its design goals are:

1. **Modulation-independent.** Each track declares its own modulation scheme (MFM, FM, GCR, or other), so a single .UDI file can contain tracks with different encodings.
2. **Controller-independent.** The format does not use WD177x status bytes; it uses its own per-sector metadata.
3. **Extensible.** The format reserves space for future extensions and uses a tagged-structure scheme for optional metadata.
4. **Simple to parse.** Despite being universal, the format is no more complex than .EDSK for the common case of an all-MFM disk.

### 1.2 .UDI vs. .EDSK vs. .SCP

| Property | .EDSK | .UDI | .SCP |
|---|---|---|---|
| **Modulation** | MFM only | MFM / FM / GCR / other | Flux-level (modulation-agnostic) |
| **Per-sector metadata** | ST1/ST2 status bytes | Custom metadata fields | Per-sector flux transitions |
| **Weak-bit support** | Per-sector weak flag | Per-sector weak flag | Native (flux-level) |
| **Multi-revolution** | No (single sample) | No (single sample) | Yes (up to 5 revolutions) |
| **Tool support** | Universal | Limited (mostly Russian) | Growing rapidly |
| **Typical file size** | 100 KB – 1 MB | 100 KB – 1 MB | 10 MB – 50 MB |

The .UDI format sits between .EDSK (which it generalises) and .SCP (which it pre-dates and which goes further). For most Spectrum archival work, .EDSK is preferred due to its wider tool support; .SCP is preferred for true preservation; .UDI is used in niche cases where the disk's non-MFM modulation must be preserved.

### 1.3 A short history

The .UDI format was developed in the late 1990s by the Russian Spectrum community (zx-pk.ru, zxevo.ru). The goal was to have a single format that could represent the disks used by the various Soviet Spectrum clones (Pentagon, Scorpion, Leningrad) — some of which used non-standard sector layouts or non-MFM modulation schemes that the original .TRD / .SCL formats could not handle.

The format is documented (in Russian) on the zx-pk.ru forum and on the zxevo.ru wiki. An English-language summary is available in the documentation for the UnrealSpeccy emulator, which supports .UDI.

### 1.4 Scope

This article covers the byte-level layout of .UDI files. The simpler .TRD / .SCL formats are covered in [trd_scl_formats.md](trd_scl_formats.md); the .DSK / .EDSK / .FDI formats are covered in [dsk_fdi_formats.md](dsk_fdi_formats.md); the .SCP flux-level format is covered in [scp_format.md](scp_format.md).


## §2. The .UDI Header and Information Block

### 2.1 Overview

A .UDI file consists of three parts:

1. **A fixed-size header** (typically 16 bytes) containing the magic string, the format version, and a small amount of geometry info.
2. **An information block** (variable length, tagged structure) containing the disk's geometry, per-track descriptions, and optional metadata.
3. **A track data block** (variable length) containing the raw sector data for every track.

The structure is similar to .FDI (header + information + data), but the .UDI information block is more focused on the per-track layout (and less on metadata tags) than .FDI's tagged-structure information block.

### 2.2 The fixed-size header

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 4 | **Magic** | ASCII: `"UDI!"` (`55 44 49 21`). Identifies the file as .UDI. |
| 4 | 1 | **Version** | Format version byte. The current documented version is `0x00`; some extensions use `0x01`. |
| 5 | 1 | **Cylinders** | Number of cylinders (typically 40 or 80). |
| 6 | 1 | **Sides** | Number of sides per cylinder (1 or 2). |
| 7 | 1 | **Default modulation** | Default modulation scheme for tracks that do not override it: `0` = MFM, `1` = FM, `2` = GCR (Commodore), `3` = Apple II GCR, `4` = other (custom). |
| 8 | 4 | **Information block length** (LE) | The size in bytes of the information block that follows the header. |
| 12 | 4 | **Track data block offset** (LE) | The byte offset in the file where the track data block starts (typically `16 + information_block_length`). |

After the 16-byte header comes the information block, then the track data block.

### 2.3 The information block: per-track descriptor table

The information block is dominated by a **per-track descriptor table**: one entry per (cylinder, side) pair, in the order:

1. Cylinder 0, side 0
2. Cylinder 0, side 1 (if 2-sided)
3. Cylinder 1, side 0
4. Cylinder 1, side 1
5. ... and so on.

The total number of entries is `cylinders * sides`. Each entry is a fixed-size descriptor (typically 8 bytes, though the exact layout varies by version):

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 1 | **Modulation scheme** | `0` = MFM, `1` = FM, `2` = GCR, etc. May override the default set in the header. |
| 1 | 1 | **Sector count** | The number of sectors on this track (e.g., 9, 10, 16). |
| 2 | 2 | **Track data length** (LE) | The size in bytes of this track's data in the track data block (including any per-sector metadata). |
| 4 | 1 | **Sector size code** | Default sector size code: 0=128, 1=256, 2=512, etc. Individual sectors can override this. |
| 5 | 1 | **Sector ID fields present** | `0` = no per-sector ID information (use default numbering 1, 2, 3, ...); `1` = per-sector ID information is present in the track data. |
| 6 | 2 | **(reserved for extensions)** | Zeros in the current version. |

A track with descriptor `0x00` for the modulation scheme uses the file's default. A track with `0x00` for the track data length is empty (i.e., unformatted).

### 2.4 Optional metadata tags

After the per-track descriptor table, the information block may contain optional metadata tags. Each tag has the form:

| Offset | Length | Field |
|---|---|---|
| 0 | 2 | Tag ID (LE) |
| 2 | 4 | Tag data length (LE) |
| 6 | N | Tag data |

The defined tags include:

| Tag ID | Name | Data content |
|---|---|---|
| `0x0000` | End of metadata | No data; signals the end of the metadata tag list. |
| `0x0001` | Disk label | A UTF-8 / CP-1251 / ASCII string (the disk's name). |
| `0x0002` | Creator tool | A string identifying the tool that wrote the file. |
| `0x0003` | Imaging date | A 4-byte Unix timestamp or an 8-byte ASCII date. |
| `0x0004` | Comment | A free-form comment string. |
| `0x0005` | Weak-bit map | A bitmap of sectors that have non-deterministic data. |
| `0x0006` | CRC errors | A list of sectors with deliberately corrupted CRCs. |

A reader that encounters an unknown tag should skip it. The metadata tag list is terminated by the `0x0000` end-of-metadata tag (or by the end of the information block, whichever comes first).

### 2.5 Validation

A reader should validate the following:

- The magic string at offset 0 is `"UDI!"`.
- The version byte at offset 4 is recognized (typically `0x00` or `0x01`).
- The cylinders and sides fields are reasonable (e.g., cylinders in 1–84, sides in 1–2).
- The information block length is consistent with `cylinders * sides * 8` plus the metadata tag list.
- The track data block offset points to a valid position within the file.

Malformed files should be reported as warnings, not errors, since real-world .UDI files in circulation often have minor format violations (especially in the metadata tags).


## §3. The Track Data Block

### 3.1 Track data layout

The track data block follows the information block. It contains, for each (cylinder, side) pair in the same order as the per-track descriptor table, a chunk of `track_data_length` bytes containing the track's data.

The track data block has no per-track header — the header information is in the per-track descriptor table in the information block. The track data block is just a concatenation of per-track data blobs, in the same order as the descriptors.

To read a specific track:

```python
# .UDI reader pseudocode
header = parse_header(data[0:16])
info_block = data[16 : 16 + header.info_length]
descriptors = parse_descriptors(info_block, header.cylinders * header.sides)

track_offset = header.track_data_offset  # = 16 + header.info_length
for i, desc in enumerate(descriptors):
    if desc.track_data_length == 0:
        continue  # empty / unformatted track
    track_data = data[track_offset : track_offset + desc.track_data_length]
    parse_track(track_data, desc)
    track_offset += desc.track_data_length
```

### 3.2 Per-track data structure

The contents of each track's data blob depend on the descriptor:

- **If the descriptor's "sector ID fields present" is 0**, the track data is just the sector payload: `sector_count * sector_size` bytes, with sectors in numerical order (1, 2, 3, ..., N).
- **If the descriptor's "sector ID fields present" is 1**, the track data begins with a per-sector ID table, followed by the sector payloads.

The per-sector ID table is one entry per sector, each entry being:

| Offset | Length | Field |
|---|---|---|
| 0 | 1 | Cylinder (as written in the sector ID field) |
| 1 | 1 | Side (as written in the sector ID field) |
| 2 | 1 | Sector ID (as written in the sector ID field) |
| 3 | 1 | Sector size code (0=128, 1=256, 2=512, etc.) |
| 4 | 1 | Flags (bit 0 = CRC error, bit 1 = data mark missing, bit 2 = weak / fuzzy data, bit 3 = deleted data mark) |

After the per-sector ID table comes the sector payload data: `sum(sector_sizes)` bytes, where each sector's size is `2^(size_code+7)`.

### 3.3 Worked example: a standard MFM track

Consider a standard TR-DOS track: cylinder 0, side 0, 10 sectors of 512 bytes each, sectors numbered 1–10, no errors. The per-track descriptor would be:

| Field | Value |
|---|---|
| Modulation | 0 (MFM, the default) |
| Sector count | 10 |
| Track data length | `40 (ID table) + 10 * 512 (sector data) = 5160` |
| Sector size code | 2 (512 bytes) |
| Sector ID fields present | 1 |

And the per-track data would be:

| Offset | Length | Content |
|---|---|---|
| 0 | 40 | 10 × 4-byte sector ID entries: each with cylinder=0, side=0, sector=N (1..10), size_code=2 |
| 40 | 5120 | 10 × 512-byte sector payloads (sectors 1, 2, 3, ..., 10 in order) |

Total track data: 5160 bytes.

### 3.4 Per-sector flags

The flags byte in the sector ID entry encodes error conditions:

| Bit | Name | Meaning |
|---|---|---|
| 0 | **CRC error** | The sector's data has a bad CRC (deliberate or due to media damage). |
| 1 | **Data mark missing** | The FDC could not find a data mark after the ID field. |
| 2 | **Weak / fuzzy data** | The sector's data is non-deterministic (different bytes per revolution). |
| 3 | **Deleted data mark** | The sector has a deleted (rather than normal) data mark. |
| 4–7 | (reserved) | Zeros. |

These flags are the .UDI equivalent of .EDSK's ST1/ST2 status bytes, but in a single byte and using a different (modulation-independent) encoding.

### 3.5 Non-MFM tracks

For tracks that use FM, GCR, or other modulation schemes, the track data layout is the same (per-sector ID table + sector payloads), but the modulation scheme byte in the descriptor determines how the data should be interpreted when written back to a real disk:

- **FM tracks** (`modulation = 1`) use single-density FM encoding (see [mfm_encoding.md](mfm_encoding.md) for the FM variant). The bit rate is half of MFM, so the same physical track holds half the data.
- **GCR tracks** (`modulation = 2` for Commodore, `modulation = 3` for Apple II) use Group Code Recording: groups of 4 data bits are encoded as 5 (or 6) bits on disk. GCR is not used on Spectrum disks (it's a Commodore / Apple thing), but the format supports it for cross-platform interchange.
- **Custom modulation** (`modulation = 4`) is reserved for non-standard schemes; the reader is expected to know the scheme out-of-band (or to treat the track as opaque).

For Spectrum disks, all tracks are MFM, so the modulation byte is always 0 (or omitted, using the default).

### 3.6 Total file size

The total file size of a .UDI file is:

```
file_size = 16 + information_block_length + sum(track_data_lengths)
```

For a standard 80-track 2-sided TR-DOS disk with 10 sectors of 512 bytes per track, all MFM:

```
per_track_descriptor_size = 8 bytes
descriptors_total = 80 * 2 * 8 = 1280 bytes
metadata_tags_minimal = 8 bytes (just the end-of-metadata tag)
information_block_length = 1280 + 8 = 1288 bytes

track_data_per_track = 40 (ID table) + 10 * 512 (data) = 5160 bytes
track_data_total = 80 * 2 * 5160 = 825,600 bytes

file_size = 16 + 1288 + 825,600 = 826,904 bytes (~808 KB)
```

This is slightly larger than the equivalent .EDSK file (which has less per-sector metadata for the all-MFM case), but the .UDI file can represent tracks with different modulations and different sector layouts in a way that .EDSK cannot.

### 3.7 Compatibility with .EDSK

There is no automatic conversion between .UDI and .EDSK, because the formats encode per-sector metadata differently. However:

- A .UDI file with all tracks being MFM and with the same sector count and sector size on every track can be losslessly converted to .EDSK (by translating the per-track descriptors and per-sector flags).
- A .UDI file with mixed-modulation tracks cannot be converted to .EDSK (which only supports MFM).
- A .UDI file with per-track sector ID overrides (bogus sector numbers) can be converted to .EDSK with the ST1/ST2 flags set appropriately, but the encoding is not one-to-one (some .UDI flag combinations have no direct .EDSK equivalent).

In practice, most tools that support .UDI also support .EDSK and provide automatic conversion in the common cases.


## §4. Tools and Converters

### 4.1 Emulators and tools that read .UDI

The .UDI format is supported by a smaller set of tools than .TRD, .SCL, .DSK, or .EDSK. The main ones are:

| Tool | Platform | Notes |
|---|---|---|
| **UnrealSpeccy** | Windows | The reference emulator for .UDI in the Russian Spectrum community. Reads and writes .UDI natively. |
| **ZEsarUX** | Linux / Win / macOS | Reads .UDI; can convert to / from .EDSK in the common cases. |
| **ZX Evolution firmware** | Real hardware | The ZX Evolution's onboard firmware reads .UDI directly from SD cards, alongside .TRD / .SCL. |
| **zxevo.ru tools** | Multiple | Various small conversion tools in the zxevo.ru community operate on .UDI files. |

The format is much less supported in the Western Spectrum community — FUSE and Spectaculator do not natively read .UDI (they support .DSK / .EDSK instead). To use a .UDI file in these emulators, convert it to .EDSK first.

### 4.2 Cross-format conversion

- **.UDI → .EDSK**: lossless if the .UDI file is all-MFM with a uniform sector layout (i.e., the per-track descriptors all specify MFM and the same sector count and sector size). Otherwise, the conversion is lossy.
- **.EDSK → .UDI**: generally lossless, since .UDI's metadata model is a superset of .EDSK's. The per-sector flags translate directly.
- **.TRD / .SCL → .UDI**: trivially lossless — the .TRD / .SCL's uniform sector layout maps cleanly to .UDI's per-track descriptors.
- **.SCP → .UDI**: lossy — the flux transitions in .SCP are decoded (using the appropriate modulation scheme) into per-sector data, which is then written to .UDI. The flux-level details (timing, multi-revolution sampling) are lost.
- **.UDI → .SCP**: not directly possible — .UDI does not contain enough information to reconstruct the flux transitions.

### 4.3 When to use .UDI

Use .UDI when:

- You are working with **Russian Spectrum clones** (Pentagon, Scorpion) that have non-standard sector layouts or use FM encoding on some tracks.
- You are working with **mixed-modulation disks** that combine MFM and FM tracks.
- You need a format that is **controller-independent** (does not assume the WD177x status byte conventions).
- Your toolchain is centered on UnrealSpeccy or the ZX Evolution.

For most other Spectrum archival work, prefer .EDSK (which is more widely supported) or .SCP (which is the gold standard for preservation).

---

## §5. Cross-references and License

### 5.1 Within the storage section

- [mfm_encoding.md](mfm_encoding.md) — the MFM signal layer that .UDI's MFM tracks refer to (and the FM variant for non-MFM tracks).
- [fdc_vg93.md](fdc_vg93.md) — the WD1793 / KR1818VG93 floppy controller chip that originally wrote the sectors.
- [beta_disk_interface.md](beta_disk_interface.md), [plus3_floppy.md](plus3_floppy.md) — the host-side hardware.
- [trd_disk_format.md](trd_disk_format.md), [trd_scl_formats.md](trd_scl_formats.md) — the simpler formats used for standard TR-DOS disks.
- [dsk_fdi_formats.md](dsk_fdi_formats.md) — the more widely supported .DSK / .EDSK / .FDI formats.

### 5.2 Adjacent format articles

- [scp_format.md](scp_format.md) — .SCP: the flux-level format that goes beyond .UDI in expressive power.
- [plus3_dos_format.md](plus3_dos_format.md), [cpm_disk_format.md](cpm_disk_format.md), [opus_discovery_format.md](opus_discovery_format.md) — the on-disk logical formats that .UDI files can contain.
- [disk_format_overview.md](disk_format_overview.md) — a comparative overview of all Spectrum floppy image formats.

### 5.3 Reverse engineering and demoscene

- (Reverse engineering / preservation) The .UDI format is occasionally used to preserve disks with mixed-modulation or non-standard sector layouts in the Russian Spectrum community. For most Western Spectrum disks, .EDSK or .SCP are preferred.
- (Demoscene) .UDI is rarely used for demoscene releases outside the Russian Spectrum community.

### 5.4 External references

- **zxevo.ru** — the canonical reference for the .UDI format, in Russian.
- **zx-pk.ru** — the Russian Spectrum community forum where the format was designed and discussed.
- **UnrealSpeccy documentation** — an English-language summary of the .UDI format is available in the UnrealSpeccy manual.
- **Sprinter / ATM Turbo documentation** — these Soviet / Russian Spectrum clones also use .UDI as one of their disk-image formats.

### 5.5 License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you give appropriate credit and distribute derivative works under the same license.

"Spectrum", "ZX Spectrum", "+3", "Pentagon", "Scorpion", "ZX Evolution", "UnrealSpeccy", and other trademarks are the property of their respective owners and are used here for identification and educational purposes only.
