# +3DOS Logical Disk Format

**Scope:** The **+3DOS** logical disk format used by the Sinclair ZX Spectrum +3 and +2A (the "Plus" range). +3DOS is the file system that the +3's built-in DOS uses to organize files on floppy disks — it defines the on-disk directory, the file allocation table (in the form of CP/M-style block pointers), the file type bytes, and the conventions for naming and addressing files. This article covers the **logical** layer; the **physical** layer (sector IDs, MFM encoding, the WD1772-PH controller) is covered in [plus3_floppy.md](plus3_floppy.md), and the MFM signal layer is covered in [mfm_encoding.md](mfm_encoding.md).

**Audience:** Emulator authors who need to read or write +3 disk images (.DSK / .EDSK files of +3 disks), archival tool authors, and Spectrum +3 software preservationists. The article assumes you already understand the difference between the physical sector layer (covered in [plus3_floppy.md](plus3_floppy.md)) and the file-system layer that sits on top of it.

**Prerequisites:** A working understanding of CP/M 2.2 directory structure (since +3DOS is a direct derivative — see [cpm_disk_format.md](cpm_disk_format.md) for the related CP/M format). Familiarity with the simpler TR-DOS logical format (see [trd_disk_format.md](trd_disk_format.md)) helps for comparison, but is not strictly required.

**Depth:** Deep. Byte-level layout of the +3DOS directory, the disk parameter block (DPB), the 32-byte directory entry, the block-pointer allocation scheme, the file-type byte, and the attribute-byte conventions. Worked examples for a typical +3 disk.

---

## §1. What +3DOS Is

### 1.1 Why a separate format?

The TR-DOS file system used by the Beta Disk Interface and TR-DOS ROM (see [trd_disk_format.md](trd_disk_format.md)) was designed in the Soviet Union in the mid-1980s and is essentially a flat directory of file entries with byte-level addressing. It works well for the kinds of disks that TR-DOS users had — typically 80-track double-sided disks with 10 sectors per track and a simple file layout — but it has a number of limitations:

- **No native subdirectories.** All files live in the root directory.
- **File names limited to 8 characters, single-letter extensions.** The TR-DOS directory entry does not have room for longer names.
- **No native file attributes.** There is no read-only or system flag — TR-DOS files can be modified or deleted by any command.
- **No CP/M compatibility.** TR-DOS cannot read CP/M disks (which were in wide use in the West by 1985) without a separate CP/M utility.

When Amstrad bought Sinclair in 1986 and developed the +3 (released 1987), they decided to base the +3's DOS on **CP/M 2.2** rather than on TR-DOS. This was a deliberate choice:

- CP/M 2.2 was already a well-established industry standard by 1987.
- CP/M's directory and allocation scheme was already widely understood by software developers.
- Amstrad had previously used CP/M-style DOSes on its CPC and PCW ranges.
- Using CP/M as the base meant that existing CP/M software could (in principle) be ported to the +3 with minimal effort.

The result was **+3DOS**: a CP/M-compatible disk format with some minor extensions for the +3's specific hardware (notably the +3's "reverse side" trick and the +3's 720 KB DSDD disk geometry). +3DOS is **not** a full CP/M implementation — the +3 ships with a separate CP/M emulator — but the **disk format** is essentially CP/M-compatible, which means that +3DOS disks can be read by any standard CP/M tool.

### 1.2 +3DOS vs TR-DOS

| Property | TR-DOS 5.x | +3DOS |
|---|---|---|
| **Origin** | Soviet Union, ~1985 | Amstrad / LocoScript, 1987 |
| **Based on** | Custom | CP/M 2.2 |
| **Disk size** | 80 tr × 2 sd × 10 sec × 512 B = 800 KB | 80 tr × 2 sd × 9 sec × 512 B = 720 KB |
| **Block size** | Sectors directly (no allocation blocks) | 1 KB (2 sectors per block) |
| **Directory entries** | 128 max | 64 max |
| **Filename length** | 8 + 1-char ext | 8 + 3-char ext |
| **File attributes** | None | RO, SYS, ARCH |
| **Subdirectories** | None | None (flat directory) |
| **Date stamps** | No | Optional (rarely used) |
| **Read by +3?** | No (requires +3 utility) | Yes (native) |
| **Read by Pentagon/Scorpion?** | Yes (native) | No (requires +3 emulator) |

The key observation is that **TR-DOS and +3DOS are mutually incompatible at the disk-format level**: a TR-DOS disk cannot be read by a +3, and a +3DOS disk cannot be read by a TR-DOS machine, without a conversion utility. This is a frequent source of confusion for modern users.

### 1.3 +3DOS vs CP/M 2.2

The +3DOS disk format is essentially CP/M 2.2 with a custom Disk Parameter Block (DPB) tailored to the +3's hardware. The differences are minor at the format level:

- **Block size:** 1 KB (same as many CP/M 2.2 configurations).
- **Directory entry format:** 32 bytes, identical to CP/M 2.2.
- **Allocation pointers:** 16 × 1-byte block pointers per directory entry (same as CP/M 2.2 with 1 KB blocks).
- **Extent counter:** EX (byte 11) and S2 (byte 13) used the same way as CP/M 2.2.
- **Record count (RC):** byte 14, counts 128-byte records, same as CP/M 2.2.
- **Empty-entry marker:** `0xE5` (same as CP/M 2.2).

The differences are at the **logical file-system** layer, not the on-disk format:

- +3DOS adds a custom BIOS and BDOS, accessed via the +3's RAM-based DOS workspace.
- +3DOS uses the +3's "reverse side" hardware trick (see §2.2), which means the **cylinder numbering on side 1 is reversed** relative to a normal CP/M disk.
- +3DOS adds a custom boot-sector format (see §2.3) for booting the +3's DOS.
- +3DOS uses a slightly different DPB (see §3.2) for the +3's specific geometry.

For archival and emulation purposes, a +3DOS disk image is essentially a CP/M 2.2 disk image, and standard CP/M tools can read the directory. The complications only arise when writing or booting the disk, which require the +3-specific extensions.

### 1.4 A short history

The +3 was designed at Amstrad in 1986–1987, drawing heavily on the technology of Amstrad's CPC and PCW ranges. The +3DOS was developed by **LocoScript** (the company that wrote the LocoScript word processor for the PCW) under contract to Amstrad.

The +3DOS ROM was shipped with the +3 from launch in late 1987. It provides a subset of CP/M 2.2 functionality plus Spectrum-specific extensions for the +3's graphics and sound hardware.

The +3DOS disk format was based on the LocoScript / PCW CF2 disk format, adapted for the +3's 720 KB DSDD geometry. The format remained stable throughout the +3's commercial lifetime (1987–1992) and is still in use today in the Spectrum demoscene and emulator communities.

### 1.5 Scope

This article covers the **on-disk logical format** of +3DOS: the directory layout, the allocation scheme, the file-type bytes, and the attribute bytes. The **physical** layer is covered in [plus3_floppy.md](plus3_floppy.md); the related CP/M format is covered in [cpm_disk_format.md](cpm_disk_format.md); the disk-image file formats (.DSK, .EDSK, .FDI) used to store +3DOS images are covered in [dsk_fdi_formats.md](dsk_fdi_formats.md).

## §2. The Physical Disk Layout

### 2.1 Standard +3 disk geometry

The standard +3DOS disk is a 3.5-inch **double-sided, double-density** (DSDD) disk with the following physical geometry:

| Parameter | Value | Notes |
|---|---|---|
| **Cylinders (tracks per side)** | 80 | Standard 3.5" DSDD |
| **Sides (heads)** | 2 | |
| **Sectors per track** | 9 | Standard CP/M-style density |
| **Sector size** | 512 bytes | Standard 2 KB format sector |
| **Total formatted capacity** | 80 × 2 × 9 × 512 = **720 KB** | Standard +3 capacity |
| **Encoding** | MFM | Double density |
| **Bit rate** | 250 kbps | Standard DSDD rate |
| **Rotation speed** | 300 RPM | Standard 3.5" rate |

This is the same physical geometry used by almost every other 8-bit / 16-bit machine of the era (Amstrad CPC, Amstrad PCW, IBM PC 720 KB, Atari ST 720 KB, etc.), which means +3 disks are physically compatible with disks written by those systems. The +3 cannot read those disks at the file-system level (different logical formats), but the raw sector data can be read by any 720 KB-capable drive.

The total number of sectors on a +3 disk is **1440** (80 × 2 × 9), numbered by the +3's DOS as **logical sectors 0 through 1439**. The mapping from (cylinder, side, sector-within-track) to logical sector is described below.

### 2.2 The +3's "reverse side" trick

A normal CP/M 2.2 disk uses the **side-first** sector ordering: side 0 of all cylinders is written first, followed by side 1 of all cylinders. So a 2-sided 80-track disk has its logical sectors laid out as:

- Sectors 0–719: side 0, cylinder 0 (sectors 1–9), side 0 cylinder 1 (sectors 1–9), ..., side 0 cylinder 79 (sectors 1–9).
- Sectors 720–1439: side 1, cylinder 0 (sectors 1–9), side 1 cylinder 1 (sectors 1–9), ..., side 1 cylinder 79 (sectors 1–9).

The +3 does **not** use this ordering. Instead, the +3 uses a **"reverse side" trick**: side 0 is read in normal cylinder order (cylinder 0 → 79), but **side 1 is read in reverse cylinder order** (cylinder 79 → 0). The reason for this is hardware-related (the +3's floppy controller, the WD1772-PH, has a side-select quirk — see [plus3_floppy.md §4](plus3_floppy.md) for details).

The result is that the +3's logical sector ordering looks like:

- Sectors 0–719: side 0, cylinder 0 (sectors 1–9), side 0 cylinder 1 (sectors 1–9), ..., side 0 cylinder 79 (sectors 1–9).
- Sectors 720–1439: side 1, cylinder **79** (sectors 1–9), side 1 cylinder **78** (sectors 1–9), ..., side 1 cylinder **0** (sectors 1–9).

This is sometimes called the **"backward second side"** layout, and it is identical to the layout used by the Amstrad CPC and PCW. (The PCW CF2 disks that inspired +3DOS used the same trick.)

**Practical consequence for emulator authors:** When a +3 disk is stored in a .DSK or .EDSK file (see [dsk_fdi_formats.md](dsk_fdi_formats.md)), the sectors are stored in their physical (cylinder, side) order: cylinder 0 side 0, cylinder 0 side 1, cylinder 1 side 0, cylinder 1 side 1, and so on. The +3's "reverse side" trick is implemented at the **logical-to-physical** translation layer in the +3's BIOS, not at the disk-image layer. So a .DSK image of a +3 disk looks just like a .DSK image of a CPC disk — the difference is only visible when you actually try to read a +3DOS file system from it.

### 2.3 The boot sector

The first sector of a +3DOS disk (logical sector 0, = cylinder 0 side 0 sector 1) is the **boot sector**. On a bootable +3 disk, this sector contains code that the +3's ROM executes to bootstrap the +3DOS.

The structure of the boot sector is loosely inspired by the IBM PC boot sector format, but it is not identical. The first three bytes are a jump instruction to the bootstrap code, followed by a 50-byte header containing the disk identification, the format version, and the geometry parameters. After the header comes the bootstrap code itself, which is responsible for loading the rest of the +3DOS kernel from sectors 1–7 (or thereabouts) and entering it.

On non-bootable +3 disks (i.e., most data disks), the boot sector contains only zeros or a simple "this disk is not bootable" message. The +3's boot ROM silently ignores non-bootable disks.

For archival purposes, the boot sector is part of the disk image and is preserved as-is in .DSK / .EDSK images. It does not need to be interpreted by the emulator unless the user is actually booting from the disk; for read-only access to the file system, the boot sector can be ignored.

### 2.4 Logical-to-physical sector mapping

The +3's DOS presents the disk to user programs as a flat sequence of **logical sectors**, numbered 0 through 1439. The mapping from a logical sector to a (cylinder, side, sector-within-track) tuple is:

```python
# +3DOS logical-to-physical sector mapping (side 0 normal, side 1 reversed)

def logical_to_physical(logical_sector):
    if logical_sector < 720:
        # Side 0: cylinders 0..79, normal order
        side = 0
        cylinder = logical_sector // 9
        sector_in_track = (logical_sector % 9) + 1   # sectors numbered 1..9
    else:
        # Side 1: cylinders 79..0, reversed
        side = 1
        offset = logical_sector - 720
        cylinder = 79 - (offset // 9)
        sector_in_track = (offset % 9) + 1
    return (cylinder, side, sector_in_track)
```

This mapping is identical to the mapping used by the Amstrad CPC and PCW (which is why +3DOS disks are sometimes described as "PCW CF2 format" disks).

When the +3's BIOS needs to read a particular logical sector, it converts the logical sector number to a (cylinder, side, sector) tuple using this mapping, then issues a WD1772-PH `READ SECTOR` command (see [plus3_floppy.md §3](plus3_floppy.md)).

## §3. The Disk Parameter Block (DPB)

### 3.1 What the DPB is

Every CP/M-compatible disk format is described by a **Disk Parameter Block (DPB)** — a 15- or 16-byte data structure that tells the BDOS how the disk is laid out: how many sectors per track, how big each block is, how many directory entries there are, and so on. The +3DOS is no exception: every +3 disk has an associated DPB, and the +3's BIOS consults the DPB to translate logical file-system operations into physical sector reads and writes.

On a real +3, the DPB is **not** stored on the disk itself (unlike, say, the FAT BIOS Parameter Block on an MS-DOS disk). Instead, the DPB is part of the +3's ROM, and the BIOS selects the correct DPB based on the disk's geometry (which it determines by issuing a `READ ADDRESS` command to the WD1772-PH and inspecting the returned sector IDs). For non-standard geometries, the user can supply a custom DPB via the `*FORMAT` command.

For archival and emulator-author purposes, however, it is useful to know the **standard +3 DPB** so that you can interpret a +3 disk image without consulting the +3's ROM.

### 3.2 The standard +3DOS DPB

The standard +3 DPB (for a 720 KB DSDD disk) has the following fields. The field names follow the standard CP/M 2.2 DPB convention (see [cpm_disk_format.md §3](cpm_disk_format.md)).

In CP/M 2.2, the **DSM** field is the **highest** block number (not the count) — so the total number of blocks on the disk is `DSM + 1`. The **AL0/AL1** fields form a 16-bit bitmap indicating which of the first 16 blocks are reserved for the directory; for +3DOS, AL0 = `0xC0` and AL1 = `0x00`, so blocks 0 and 1 are reserved (2 × 1 KB = 2 KB = 64 directory entries × 32 bytes).

| Offset | Field | Value | Notes |
|---|---|---|---|
| 0 | **SPT** (sectors per track) | `0x0024` = 36 | Counted in 128-byte records, so 9 sectors × 4 records = 36 |
| 2 | **BSH** (block shift) | `0x03` | Block size = `2^(BSH+7)` = 2^10 = 1024 bytes |
| 3 | **BLM** (block mask) | `0x07` | `2^BSH - 1` = 7 |
| 4 | **EXM** (extent mask) | `0x00` | With BLM = 0x07 and DSM < 256, EXM = 0 (16 blocks per entry) |
| 5 | **DSM** (max data block number) | `0x02CA` = 714 | Highest block number; total blocks = 715 × 1 KB = 715 KB |
| 7 | **DRM** (max directory entry number) | `0x003F` = 63 | Number of directory entries minus 1 (so 64 entries) |
| 9 | **AL0** (alloc. bitmap byte 0) | `0xC0` | First 2 blocks reserved for directory (2 × 1 KB = 2 KB) |
| 10 | **AL1** (alloc. bitmap byte 1) | `0x00` | |
| 11 | **CKS** (dir-check vector size) | `0x0010` = 16 | `(DRM+1) / 4`, rounded up |
| 13 | **OFF** (reserved tracks offset) | `0x0000` = 0 | No reserved system tracks |
| 15 | (padding / unused) | `0x0000` | Some CP/M variants use this for sector-size or other flags |

The DPB defines the following important parameters:

- **Block size:** 1024 bytes (1 KB). This is the unit of allocation for files.
- **Sectors per block:** 2 (1024 / 512).
- **Total blocks on disk:** 715 (DSM + 1).
- **Directory blocks:** 2 (blocks 0 and 1, reserved via AL0 = `0xC0`).
- **Data blocks:** 715 − 2 = 713 (= ~713 KB available for file data).
- **Directory size:** 2 × 1024 = 2048 bytes = 64 directory entries × 32 bytes.

**Notes on the DSM value.** The exact DSM value varies slightly between sources: some references cite DSM = 710, others 714, others 719. The differences arise from how each source accounts for the boot sector and the directory reservation. The value 714 (= 0x02CA) is the most commonly cited and is used by the standard +3 ROM; with BSH = 3 (1 KB blocks), this gives 715 KB of total file-system space, leaving the remaining ~5 KB unused on the 720 KB physical disk. Most +3 software does not depend on the exact DSM value, since few disks fill more than ~700 blocks.

The reason the DPB counts in **128-byte records** (note SPT = 36 = 9 × 4, not 9) is a CP/M convention: every BDOS-level file operation works in units of 128-byte records, so all DPB fields are scaled accordingly.

### 3.3 DPB variants

The standard +3 DPB described above applies to the standard 720 KB DSDD disk. Other geometries have different DPBs:

- **Single-sided 40-track disk (180 KB):** SPT = 36, BSH = 3, BLM = 7, EXM = 0, DSM = 178, DRM = 31, AL0 = 0xC0, AL1 = 0x00, CKS = 8, OFF = 0.
- **Single-sided 80-track disk (360 KB):** SPT = 36, BSH = 3, BLM = 7, EXM = 0, DSM = 358, DRM = 63, AL0 = 0xC0, AL1 = 0x00, CKS = 16, OFF = 0.
- **High-density 80-track 2-sided disk (1.44 MB):** This was not commonly used on the +3 (the +3's controller only supported DSDD), but some third-party interfaces supported it. The DPB would have SPT = 72, DSM = ~1430.

Custom DPBs can be supplied to the `*FORMAT` command for non-standard layouts. The DPB is stored in the +3's DOS workspace and is consulted by every file-system operation.
## §4. The Directory Structure

### 4.1 Directory layout

The +3DOS directory occupies the **first 2 KB** of the disk (blocks 0 and 1, as reserved by `AL0 = 0xC0` in the DPB). This is 4 sectors of 512 bytes, or 2048 bytes total, divided into **64 directory entries** of 32 bytes each.

The directory is a flat array of 32-byte entries — there are no subdirectories, no tree structure, and no separate allocation table. Each directory entry either describes one "extent" of a file (see §4.4) or is marked as unused.

To enumerate all files on a +3DOS disk, an emulator reads the directory entries sequentially (entries 0–63) and groups them by filename — all entries with the same (filename, file-type) tuple describe the same logical file, with each entry describing one "extent" of that file's data.

### 4.2 The 32-byte directory entry

The format of a 32-byte +3DOS directory entry is identical to CP/M 2.2:

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 8 | **Filename** | 8 ASCII characters, space-padded, uppercase. High bit of byte 0 = "read-only" flag (see §6). High bit of byte 1 = "system" flag. |
| 8 | 3 | **File type (extension)** | 3 ASCII characters, space-padded, uppercase. High bit of byte 10 = "archive" / "modified" flag. |
| 11 | 1 | **EX** (extent number low) | Extent number, low byte. With EXM = 0, EX ranges 0–31 within a single S2 group. |
| 12 | 1 | **S1** (reserved) | Reserved (always 0 in standard +3DOS). Some CP/M implementations use this for the "file position" indicator. |
| 13 | 1 | **S2** (extent number high) | Extent number, high bits 0–4. `0x80` bit set indicates an unused extent. The full extent number is `(S2 & 0x1F) * 32 + EX`. |
| 14 | 1 | **RC** (record count) | Number of 128-byte records used in this extent. Max is 128 (= 16 KB). |
| 15 | 16 | **Allocation pointers** | 16 × 1-byte block pointers. Each non-zero byte is the number of a 1 KB block on the disk. A zero byte = "no block here". |

**Empty entries** are marked by byte 0 = `0xE5` (the CP/M "deleted" marker). An emulator scanning the directory should skip any entry with byte 0 = `0xE5`.

### 4.3 Filename encoding

Filenames in +3DOS are stored as **uppercase ASCII, space-padded**:

- Filename field (bytes 0–7): the 8 characters of the "base" name. Shorter names are padded on the right with spaces (`0x20`). All characters must be uppercase ASCII in the range `0x20`–`0x7E` (excluding the high bit; high bits are used for attributes).
- File type field (bytes 8–10): the 3 characters of the "extension". Same encoding.

Examples:

| File on disk | Filename field | File-type field |
|---|---|---|
| `GAME.BAS` | `GAME    ` (4 + 4 spaces) | `BAS` |
| `LEVELS.DAT` | `LEVELS  ` (6 + 2 spaces) | `DAT` |
| `BOOT` | `BOOT    ` (4 + 4 spaces) | `   ` (3 spaces) |
| `README.TXT` | `README  ` (6 + 2 spaces) | `TXT` |

The `*CAT` (catalog) command on the +3 displays filenames as `BASE.EXT` (inserting a period between the base name and the extension), or just `BASE` if the extension is all spaces.

### 4.4 Allocation pointers (the DM/AL field)

Bytes 15–30 of a directory entry are 16 **allocation pointers**, each one byte. Each non-zero pointer is the **block number** of a 1 KB block on the disk that holds part of this file's data. A zero byte means "no block at this position".

For a typical 720 KB disk, the block numbers range from 0 to 714 (= DSM). Blocks 0 and 1 are reserved for the directory itself (per the `AL0 = 0xC0` bitmap), so user-file data starts at block 2.

When reading a file, the emulator concatenates the data from the blocks in the order they appear in the allocation-pointer list:

```python
# +3DOS file-read pseudocode
def read_extent_data(disk, dir_entry):
    data = b""
    for ptr in dir_entry.alloc_pointers:   # bytes 15..30
        if ptr != 0:
            block_offset = ptr * 1024      # 1 KB blocks
            data += disk[block_offset : block_offset + 1024]
    # The last extent may not be full — only the first RC × 128 bytes are valid
    valid_bytes = dir_entry.RC * 128
    return data[:valid_bytes] if len(data) > valid_bytes else data
```

A single directory entry can address up to **16 KB** of file data (16 blocks × 1 KB). Files larger than 16 KB require multiple directory entries (multiple "extents"), described next.

### 4.5 Extents and the EX/S2/RC fields

For files larger than 16 KB, +3DOS uses **multiple directory entries** (called "extents" in CP/M terminology) to describe the file's allocation. Each extent covers up to 16 KB of contiguous file data.

The three fields that govern extents are:

- **EX** (byte 11): the extent number within the current S2 group. With `EXM = 0` (the +3 standard), EX ranges 0–31, so an S2 group of extents can cover up to 32 × 16 KB = 512 KB.
- **S2** (byte 13): the S2 group number (bits 0–4). With S2 = 0, EX can be 0–31. With S2 = 1, EX can again be 0–31, addressing extents 32–63, and so on. In practice, S2 is almost always 0 for files under 512 KB.
- **RC** (byte 14): the **record count** — the number of 128-byte records of valid data in this extent. The maximum is 128 records (= 16 KB); a smaller value indicates a partial extent (e.g., the last extent of a file that is not a multiple of 16 KB).

The **full extent number** for an entry is computed as `(S2 & 0x1F) × 32 + EX`. Extents for the same file have the same (filename, file-type) tuple but different extent numbers.

**Worked example.** Consider a file `BIGFILE.DAT` of 38 KB. Its directory entries would look like:

| Entry | Filename | Type | EX | S2 | RC | Alloc pointers |
|---|---|---|---|---|---|---|
| 0 | `BIGFILE ` | `DAT` | `0x00` | `0x00` | `0x80` (= 128) | blocks 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 (16 KB) |
| 1 | `BIGFILE ` | `DAT` | `0x01` | `0x00` | `0x80` (= 128) | blocks 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36 (16 KB) |
| 2 | `BIGFILE ` | `DAT` | `0x02` | `0x00` | `0x30` (= 48) | blocks 37, 38, 39 (3 KB) |

Total: 16 + 16 + 6 = 38 KB. ✓

To read the full file, the emulator reads entries 0, 1, and 2 in order of (EX, S2), concatenates the block data for each entry, and stops when the total bytes equal the sum of `(RC × 128)` for each entry.

### 4.6 Empty and deleted entries

A directory entry with **byte 0 = `0xE5`** is treated as **empty** (no file). When a file is deleted, the +3's DOS simply writes `0xE5` to byte 0 of every extent of that file; the block pointers and the actual file data remain on disk until overwritten. This is the same as CP/M 2.2's behavior, and the same recovery technique (writing back the first character of the filename) works for undeletion.
## §5. File Types and Extensions

### 5.1 The +3DOS file-type byte

+3DOS, like CP/M 2.2, has **no separate file-type byte** — the file type is encoded entirely in the **3-character extension** stored in bytes 8–10 of the directory entry. There is no separate "type" field like TR-DOS has (compare [trd_disk_format.md §5](trd_disk_format.md)).

Instead, the +3's DOS (and the +3's `LOAD`, `SAVE`, `MERGE`, etc. BASIC commands) use **convention** to interpret the contents of files based on their extension:

| Extension | Convention | Notes |
|---|---|---|
| (none) or `   ` | Generic data file | |
| `BAS` | Spectrum BASIC program | Saved by `SAVE "name" LINE n` |
| `BIN` | Spectrum binary (machine code) | Saved by `SAVE "name" CODE start, length` |
| `SCR` | Screen snapshot | Saved by `SAVE "name" SCREEN$` (6912 bytes) |
| `DAT` | Generic data file | |
| `TXT` | Plain text file | |
| `CHP` | Cheat file (for use with game cheat utilities) | |
| `MUS` | Music data file | |
| `COM` | CP/M transient command | (For use under CP/M mode only) |
| `SUB` | CP/M submit file | (For use under CP/M mode only) |
| `REL` | CP/M random-access data file | (For use under CP/M mode only) |
| `OVR` | CP/M overlay file | (For use under CP/M mode only) |
| `LIB` | CP/M library | (For use under CP/M mode only) |
| `   ` | CP/M `$$$` intermediate | Produced by `SUBMIT.COM` |

The `BAS`, `BIN`, and `SCR` extensions are Spectrum-specific (the +3's BASIC uses them by default). The `COM`, `SUB`, `REL`, `OVR`, and `LIB` extensions are CP/M 2.2 conventions and are only meaningful when running CP/M mode on the +3.

### 5.2 The Spectrum BASIC file header

When the +3's BASIC saves a file with `SAVE "name"`, `SAVE "name" LINE n`, or `SAVE "name" CODE`, the file's data on disk begins with a **9-byte header** that encodes the file's type and length:

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 1 | **File type** | `0x00` = BASIC program, `0x01` = number array, `0x02` = character array, `0x03` = binary code |
| 1 | 2 | **Data length** (LE) | Length of the data block following this header |
| 3 | 2 | **Parameter 1** (LE) | For BASIC: the autostart line number (or 0x8000 for no autostart). For code: the start address. |
| 5 | 2 | **Parameter 2** (LE) | Length of BASIC program (excluding variables). For code: always equals the data length. |
| 7 | 2 | **(reserved / unused)** | |
| 9+ | N | **File data** | The actual file data |

This is the same 9-byte header format used by the Spectrum tape system (see the TAP format documentation in [03_io/snapshots/tap_format.md](../snapshots/README.md)) — the +3 reuses the tape header format for its disk files.

When the +3's BASIC loads a file with `LOAD "name"` or `LOAD "name" CODE`, it reads the 9-byte header, determines the file type from byte 0, and dispatches accordingly.

### 5.3 Raw data files

Files saved with no BASIC header (i.e., raw data written directly to the disk via DOS calls) have no header — the file's data on disk is exactly the bytes the program wrote. Files with extensions like `DAT`, `TXT`, `MUS`, and `BIN` (when not produced by BASIC) are typically raw data files.

An emulator reading a +3DOS disk cannot distinguish between BASIC files (which have a 9-byte header) and raw data files (which do not) without inspecting the file's contents — there is no flag in the directory entry. The `*CAT` command displays the extension, which is the only hint the user has about the file's contents.

### 5.4 CP/M-mode files

When running under CP/M mode (a separate boot option on the +3), the file types are interpreted according to CP/M 2.2 conventions:

- `COM` files are executable programs (loaded at `0x0100` and executed).
- `SUB` files are submit scripts for the CP/M `SUBMIT.COM` utility.
- `REL` files are relocatable object files (used by Microsoft's MAC and RMAC assemblers).
- `OVR` files are overlay files loaded by parent programs on demand.
- `LIB` files are library files for the linker.
- `BAS` files (in CP/M mode) are MBASIC / HiSoft BASIC source files (not the same format as the +3's `SAVE "name" LINE` BASIC files).

This dual interpretation of file types is one of the reasons +3DOS disks can be confusing to emulator authors: a file with extension `BAS` could be either a Spectrum BASIC program (with a 9-byte header) or a CP/M MBASIC source file (plain text source code), depending on which mode the +3 was in when it was saved.
## §6. Attribute Bytes

### 6.1 Where the attributes are stored

+3DOS has **no dedicated attribute byte** in the directory entry — unlike, say, MS-DOS (which has a dedicated byte of file attributes) or FAT32. Instead, the file attributes are encoded in the **high bits of the filename and file-type bytes**:

| Bit position | Attribute | Notes |
|---|---|---|
| Byte 0, bit 7 (`0x80`) | **Read-only (RO)** | File cannot be modified or deleted by BDOS calls. |
| Byte 1, bit 7 (`0x80`) | **System (SYS)** | File is hidden from directory listings (the `*CAT` command skips SYS files unless explicitly requested). |
| Byte 10, bit 7 (`0x80`) | **Archive (ARCH)** | File has been modified since the last backup (set automatically on write, cleared by backup tools). |

This is the same encoding used by CP/M 2.2 — the high bits of the filename and file-type fields are reserved for attributes, while the low 7 bits contain the ASCII character.

### 6.2 Read-only (RO)

Setting the read-only attribute on a file marks it as "do not modify". The +3's BDOS will refuse to open the file for writing, refuse to delete the file, and refuse to rename the file. (Other read operations, such as `LOAD` and `MERGE`, are still permitted.)

Read-only is set by `*SET` (the +3's attribute-setting command) and can be cleared the same way. The attribute is stored in the directory entry (byte 0, high bit) and persists across disk changes.

### 6.3 System (SYS)

Setting the system attribute on a file marks it as "hidden" — the `*CAT` command skips SYS files by default. The file is still present on disk and can be opened explicitly by name; it just doesn't appear in directory listings.

The system attribute was used in CP/M 2.2 for the operating system itself (which was stored in reserved system tracks and should not appear in directory listings). On the +3, the attribute is rarely used for its original purpose, but some software (notably copy-protection schemes) uses the SYS attribute to hide configuration files or save files.

### 6.4 Archive (ARCH)

Setting the archive attribute on a file indicates that the file has been modified since the last backup. The attribute is **set automatically** by the BDOS whenever the file is written to, and **cleared** by backup tools (after copying the file to the backup disk).

The archive attribute is the only one of the three that is set automatically — RO and SYS are always set explicitly by the user (or by software).

### 6.5 The empty-entry marker (`0xE5`)

A separate convention applies to **empty** directory entries: byte 0 is set to `0xE5`, which has the high bit set (`0x80`) and is therefore not a valid ASCII character. An emulator scanning the directory should test byte 0 against `0xE5` **before** interpreting byte 0 as a filename character with a possible RO attribute — otherwise, an empty entry will be incorrectly reported as a file whose name starts with `u` (the `0xE5 & 0x7F = 0x65` ASCII value).

This is the standard CP/M 2.2 convention and is followed by every +3DOS implementation.

## §7. +3DOS vs CP/M 2.2 — Differences

### 7.1 What stayed the same

The following parts of +3DOS are **identical** to CP/M 2.2:

- The **disk directory entry format** (32 bytes: filename, file-type, EX, S1, S2, RC, 16 allocation pointers).
- The **allocation scheme** (1 KB blocks, 16 block pointers per extent).
- The **extent-counter semantics** (EX for low byte, S2 for high bits, RC for record count).
- The **empty-entry marker** (`0xE5`).
- The **attribute-bit encoding** (high bits of filename and file-type bytes for RO, SYS, ARCH).
- The **BDOS calling convention** (entry via `CALL 0x0005` in TPA).
- The **DMA convention** (default DMA address is `0x0080`).
- The **FCB (File Control Block) format** (33 bytes for sequential, 35+ bytes for random).

A program written for CP/M 2.2 that does not depend on hardware-specific I/O can be ported to the +3 with very little modification (the +3's CP/M mode does exactly this).

### 7.2 What changed

The +3DOS extends CP/M 2.2 in several ways:

- **Custom DPB** for the +3's 720 KB DSDD geometry (see §3). The DPB is tailored to the +3's specific sector layout and "reverse side" trick.
- **Custom BIOS** for the +3's hardware (the WD1772-PH floppy controller, the +3's memory banking, the +3's screen and keyboard). The BIOS presents a CP/M-style interface to the BDOS, but the underlying operations are very different from a "real" CP/M machine.
- **Custom BDOS extensions** for Spectrum-specific operations (graphics, sound, file-system operations on the +3's two disk drives). These extensions are accessed via additional `CALL` addresses beyond the standard CP/M `CALL 0x0005`.
- **Spectrum BASIC integration** — the +3's BASIC can call +3DOS directly (via RST routines and the `STREAM` system), allowing BASIC programs to use disk files seamlessly. This is not part of standard CP/M.
- **No CCP (Console Command Processor)** — the +3's +3DOS does not provide a CP/M-style `CCP.COM` command shell; instead, the user interacts via the +3's BASIC editor and the `*` commands (`*CAT`, `*FORMAT`, `*COPY`, etc.).

### 7.3 Compatibility summary

| Aspect | Compatible? | Notes |
|---|---|---|
| **Reading +3DOS directory from CP/M** | Yes | The directory format is identical; any CP/M directory tool can read +3DOS directories. |
| **Reading +3DOS files from CP/M** | Yes | File data is stored in standard CP/M blocks. |
| **Booting CP/M from a +3DOS disk** | Requires +3-specific CP/M boot track | The standard +3DOS boot sector is for +3DOS, not CP/M; a CP/M boot requires a separate boot disk. |
| **Running CP/M `.COM` files on +3DOS** | Requires CP/M mode | The +3 must be in CP/M mode to execute `.COM` files. In Spectrum BASIC mode, `.COM` files are not executable. |
| **Writing to a +3DOS disk from CP/M** | Yes, with caveats | The CP/M BDOS will write the file correctly, but the +3's "reverse side" trick may confuse CP/M tools that assume a "normal" side-1 layout. |

### 7.4 Practical implications for emulator authors

For an emulator that only needs to **read** +3DOS disks (the common case), the implementation is essentially identical to reading a CP/M 2.2 disk:

1. Read the directory blocks (blocks 0 and 1, = first 2 KB).
2. Parse each 32-byte entry per the standard CP/M format.
3. For each file, traverse the extents in order of (EX, S2), read the 16 block pointers, and concatenate the block data.
4. Trim the last extent to `RC × 128` bytes.

The only +3-specific consideration is the "reverse side" mapping when translating logical blocks to physical sectors — this is handled at the disk-image layer (see [dsk_fdi_formats.md](dsk_fdi_formats.md)) and is transparent to the directory parser.

For an emulator that needs to **write** +3DOS disks, the situation is more complex: the emulator must implement the +3's specific BDOS extension calls and the "reverse side" mapping when writing. This is rarely necessary for archival or read-only emulator use cases.
## §8. Tools and Editors

### 8.1 Emulators that support +3DOS

The following Spectrum emulators fully support +3DOS disks (read and write):

- **UnrealSpeccy** (and its fork **UnrealSpeccy Portable**) — supports +3 disks in `.DSK` and `.EDSK` format.
- **Zero** — full +3 support.
- **Fuse** (Free Unix Spectrum Emulator) — full +3 support; the de facto standard for Unix-like systems.
- **SpecEmu** — full +3 support; popular Windows emulator.
- **ZXSP, Spin, ZX-Spectrum 4.7** — Windows emulators with +3 support.
- **EightyOne** — supports +3 and many other Spectrum variants.

All of these emulators accept `.DSK` / `.EDSK` images of +3 disks and interpret the +3DOS file system natively.

### 8.2 Disk image manipulation tools

For working with +3DOS disk images outside an emulator:

- **DiskImage (by Simon Owen)** — Windows / Linux command-line tool for reading and writing `.DSK` / `.EDSK` images, including +3DOS, CP/M, and Amstrad formats.
- **CPMTools (`cpmtools`)** — open-source Unix tool for reading and writing CP/M file systems; works on +3DOS disks with the correct DPB.
- **zxmak** — cross-platform tool for working with `.TRD`, `.SCL`, `.DSK`, and `.EDSK` images.
- **SAMdisk** — modern open-source tool for reading and writing many floppy-disk formats, including +3DOS.

To read a +3DOS image with `cpmtools`, you need to supply the correct DPB. The following `cpmtools` definition works for the standard 720 KB +3 disk:

```
# /etc/cpmtools/diskdefs entry for the ZX Spectrum +3 (720 KB DSDD)
diskdef plus3
  seclen 512
  tracks 160
  sectrk 9
  blocksize 1024
  maxdir 64
  boottrk 0
  skew 0
  offset 0
end
```

With this definition, you can list files on a +3DOS disk with:

```bash
cpmls -f plus3 disk.dsk
```

…and extract files with:

```bash
cpmcp -f plus3 disk.dsk FILENAME.EXT output.bin
```

### 8.3 Editor scripts

For emulator authors who want to inspect a +3DOS directory programmatically, a minimal Python reader looks like:

```python
def parse_plus3_directory(disk_bytes):
    """Parse a +3DOS directory from the first 2048 bytes of a disk image."""
    directory = []
    for i in range(64):
        entry = disk_bytes[i * 32 : (i + 1) * 32]
        if entry[0] == 0xE5:
            continue   # empty entry
        # Mask off attribute bits
        name = bytes(b & 0x7F for b in entry[0:8]).decode("ascii", "replace")
        ext  = bytes(b & 0x7F for b in entry[8:11]).decode("ascii", "replace")
        EX  = entry[11]
        S1  = entry[12]
        S2  = entry[13] & 0x1F
        RC  = entry[14]
        alloc = list(entry[15:31])
        attrs = []
        if entry[0] & 0x80: attrs.append("RO")
        if entry[1] & 0x80: attrs.append("SYS")
        if entry[10] & 0x80: attrs.append("ARCH")
        extent = S2 * 32 + EX
        directory.append({
            "name":    name.strip() + "." + ext.strip(),
            "extent":  extent,
            "rc":      RC,
            "blocks":  [b for b in alloc if b != 0],
            "attrs":   attrs,
        })
    return directory
```

### 8.4 Conversion tools

The following conversions are commonly needed when working with +3 disks:

| Conversion | Tool | Notes |
|---|---|---|
| +3 disk → `.DSK` / `.EDSK` | Any +3 emulator's "save disk image" function | |
| `.DSK` / `.EDSK` → +3 disk | Any +3 emulator's "load disk image" function (requires real floppy drive) |
| `.DSK` → files on host | `cpmcp -f plus3 image.dsk FILE.OUT out.bin` | Loses +3 BASIC header info |
| Files on host → `.DSK` | `cpmcp -f plus3 image.dsk in.bin FILE.NEW` | |
| `.TRD` ↔ `.DSK` (+3DOS) | `zxmak` (interactive) or custom script | Involves file-system conversion |

### 8.5 Reverse-engineering +3DOS disks

For reverse-engineering +3 software distributed on +3DOS disks (see [05_reversing/methodology.md](../../08_reverse_engineering/README.md) for general methodology):

1. **Extract the files** using `cpmcp` or an emulator.
2. **Inspect the BASIC headers** of `.BAS` files to determine the autostart line and length.
3. **Disassemble `.BIN` files** with a Z80 disassembler, starting at the address from the BASIC header.
4. **Look for copy-protection tricks** that examine the +3DOS directory directly (e.g., reading the directory to check for "extra" files that should not be present).

## §9. Cross-references and License

### 9.1 Related articles in this Knowledge base

- [plus3_floppy.md](plus3_floppy.md) — the **physical** layer of the +3's floppy subsystem (the WD1772-PH controller, the port map, the cable pinout). This article and that one are companions: this one covers the file system, that one covers the hardware.
- [mfm_encoding.md](mfm_encoding.md) — the MFM signal layer (sectors, address marks, data marks) that underlies all floppy-disk formats on the Spectrum.
- [trd_disk_format.md](trd_disk_format.md) — the **TR-DOS** logical disk format (a parallel format used by the Beta Disk Interface and Soviet Spectrum clones). This article and that one are the two main Spectrum disk formats.
- [cpm_disk_format.md](cpm_disk_format.md) — the **CP/M 2.2** disk format on the Spectrum (used by +3 CP/M mode, ATM Turbo, Sprinter). +3DOS is essentially a customized CP/M, so this article is the natural companion.
- [opus_discovery_format.md](opus_discovery_format.md) — the Opus Discovery disk format (a Western alternative to TR-DOS and +3DOS).
- [disk_format_overview.md](disk_format_overview.md) — a high-level comparison of all Spectrum disk formats.
- [dsk_fdi_formats.md](dsk_fdi_formats.md) — the disk-image file formats (`.DSK`, `.EDSK`, `.FDI`) used to store +3DOS images on modern systems.
- [trd_scl_formats.md](trd_scl_formats.md) — the `.TRD` and `.SCL` disk-image file formats (the TR-DOS equivalents of `.DSK` / `.EDSK`).

### 9.2 External references

- **The +3 Manual Set** (Sinclair / Amstrad, 1987) — the original hardware and DOS reference, including the +3DOS ROM disassembly.
- **"Spectrum +3 DOS"** — the canonical +3DOS reference in the World of Spectrum archive (originally published as part of the +3 user manual).
- **"CP/M 2.2 Interface Guide"** (Digital Research) — the original CP/M BDOS / BIOS specification that +3DOS is based on.
- **"LocoScript PCW disk format"** (LocoScript Software) — the Amstrad PCW CF2 disk format that inspired +3DOS.
- **The `cpmtools` documentation** — Unix manual pages and disk definitions for working with CP/M-compatible disks.

### 9.3 Trademarks

"ZX Spectrum", "+3", "+2A", "Amstrad", "Sinclair", "LocoScript", "CP/M", and other trademarks are the property of their respective owners and are used here for identification and educational purposes only.

### 9.4 License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you give appropriate credit and distribute derivative works under the same license.
