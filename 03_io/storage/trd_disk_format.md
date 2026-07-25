# TR-DOS Disk Format

**Scope:** The **logical** disk format used by TR-DOS — the directory structure, file types, file headers, disk descriptor, free-space bookkeeping, and boot process. The hardware that reads and writes this format (the WD1793 controller chip and the Beta Disk Interface) is covered in [fdc_vg93.md](fdc_vg93.md) and [beta_disk_interface.md](beta_disk_interface.md); the file-image formats used to preserve TR-DOS disks (.TRD, .SCL) are covered in [trd_scl_formats.md](trd_scl_formats.md).

**Audience:** TR-DOS software developers, emulator authors, disk-image tool authors, and demoscene coders who need to read or write TR-DOS disks directly (bypassing the TR-DOS ROM).

**Prerequisites:** A working knowledge of the WD1793 sector model (cylinder/head/sector) and of the MFM signal layer that underlies it. Strongly recommended to read [mfm_encoding.md](mfm_encoding.md) and [beta_disk_interface.md](beta_disk_interface.md) first, since this article assumes you know what a "sector" and a "track" are at the physical level.

**Depth:** Deep. Byte-level layout of every structure on a TR-DOS disk, including the on-disk catalog format, the file-type encoding, the disk descriptor (with its many compatibility extensions), and the messy real-world details of how TR-DOS 5.03/5.04 actually boots.

---

## §1. What TR-DOS Disk Format Is

### 1.1 The logical / physical boundary

A TR-DOS disk has two layers:

- **Physical layer**: the MFM-encoded magnetic flux transitions on the disk surface, organised into 80 cylinders × 2 sides × 10 sectors × 512 bytes (the standard TR-DOS 80-track format). This is what the WD1793's READ SECTOR and WRITE SECTOR commands see. See [mfm_encoding.md](mfm_encoding.md) and [fdc_vg93.md](fdc_vg93.md).
- **Logical layer**: the directory structure, file types, and bookkeeping that TR-DOS imposes on top of the raw sectors. This is what `LOAD "x"`, `SAVE "x"`, and `*CAT` operate on. **This article is about the logical layer.**

The logical layer does not care about the physical layer beyond the (cylinder, side, sector) addressing. A TR-DOS disk written on an 80-track 3.5" drive is logically identical to one written on an 80-track 5.25" drive — the bytes in the directory are the same, the file contents are the same, the disk descriptor is the same.

### 1.2 TR-DOS as a CP/M-influenced DOS

TR-DOS was designed in 1985 by Andrew Owen at Technology Research Ltd. The directory structure is **loosely derived from CP/M** (in turn derived from earlier DEC operating systems):

- Files are addressed by **name + extension**, like CP/M (e.g., `GAME    C` for a CODE file).
- Files are stored as **a sequence of 512-byte sectors** chained by a simple "next sector" pointer in the directory entry, like CP/M extents.
- There is **no separate FAT** (file allocation table) — free space is tracked implicitly by scanning the directory for unused sectors, and free-space queries scan the entire directory.

This is in contrast to MS-DOS (which uses a FAT) and to +3DOS (which uses extents but with a different bookkeeping scheme — see [plus3_dos_format.md](plus3_dos_format.md)).

### 1.3 TR-DOS versions

This article describes the **TR-DOS 5.03 / 5.04** disk format, which is the canonical version used by the overwhelming majority of TR-DOS software. Earlier versions (5.0, 5.1, 5.2 — note that TR-DOS version numbering is not monotonic) used slightly different formats that are not compatible. Later versions (5.4, TR-DOS 6.x, ETR-DOS) added extensions but remained backward-compatible with 5.03 / 5.04.

Specifically:

| Version | Year | Notes |
|---|---|---|
| 5.0 | 1985 | Initial release. Some early-format disks use this; modern emulators can usually read it. |
| 5.1, 5.2 | 1985–86 | Bug fixes. |
| 5.3 | 1986 | The canonical version; almost all TR-DOS software targets 5.03 specifically. |
| 5.4 | 1988 | Adds 80-track support as default; some extensions to the disk descriptor. |
| 6.x / ETR-DOS / Mr Gluk | 1990s+ | Soviet/post-Soviet extensions; add double-density, larger directories, long filenames. |

Unless otherwise noted, all references to "TR-DOS" in this article mean TR-DOS 5.03 / 5.04.

### 1.4 Scope

This article covers the **on-disk layout** of a TR-DOS disk: where the directory is, what the directory entries look like, how file types are encoded, and how free space is tracked. The .TRD and .SCL file-image formats (which are byte-for-byte images of a TR-DOS disk, plus a small header) are covered in [trd_scl_formats.md](trd_scl_formats.md).

---

## §2. Disk Parameters

### 2.1 Standard TR-DOS 80-track geometry

The standard TR-DOS disk has the following geometry:

| Parameter | Value |
|---|---|
| Cylinders (tracks per side) | 80 |
| Sides | 2 |
| Sectors per track | 16 (in some early formats) or 10 (the modern standard) — **see note below** |
| Bytes per sector | 256 (in some early formats) or 512 (the modern standard) |
| Encoding | MFM (double-density equivalent at the data rate, but called "single density" because it is 250 kbit/s) |
| Data rate | 250 kbit/s |
| Rotation speed | 300 RPM |
| Total capacity (80 × 2 × 10 × 512) | 819,200 bytes = **800 KB** |
| Usable capacity (after directory + boot) | ~798 KB |

**Note on sector count:** The "modern" TR-DOS 5.03 / 5.04 format uses **10 sectors of 512 bytes per track**. Earlier TR-DOS 5.0 / 5.1 used **16 sectors of 256 bytes per track**; both layouts give the same track capacity (5120 bytes per track = 2560 bytes per side = 5120 bytes per cylinder), and the directory entry format is identical, but the WD1793's READ SECTOR / WRITE SECTOR commands take a different sector number for the same byte offset.

Most modern emulators and disk tools assume the **10 sectors × 512 bytes** format. This article follows that convention.

### 2.2 Cylinder / side / sector numbering

TR-DOS uses **physical** cylinder / side / sector numbering, not the **logical** sector numbering used by some other DOSes (e.g., MS-DOS). The numbering is:

- **Cylinder**: 0–79 (cylinder 0 is the outermost track; cylinder 79 is the innermost).
- **Side**: 0 or 1 (side 0 is the lower head; side 1 is the upper head).
- **Sector**: 1–10 (sectors are numbered starting from 1, not 0).

The WD1793's READ SECTOR and WRITE SECTOR commands take a cylinder number, side bit, and sector number, and the controller chip handles the rest. TR-DOS software typically accesses sectors by their (cylinder, side, sector) tuple directly, rather than via a "logical sector number" abstraction.

### 2.3 Sector interleaving

TR-DOS does **not** use sector interleaving on a normally-formatted disk. Sectors are written in physical order: 1, 2, 3, ..., 10 around the track. This means that a multi-sector READ SECTOR command (which reads sectors 1, 2, 3, ..., n in sequence) is slower than it could be — the WD1793 finishes reading sector N, then has to wait for sector N+1 to come around, which means a full disk revolution between sectors.

Some disk-copy tools (e.g., the famous **DISCOPY**) interleave sectors when copying disks, e.g., writing them in the order 1, 6, 2, 7, 3, 8, 4, 9, 5, 10. This gives the WD1793 time to process sector N before sector N+1 arrives, **halving the multi-sector read time**. However, software that reads sectors in their physical order (which is most TR-DOS software) does not benefit from interleaving.

TR-DOS's `*COPY` command preserves sector order; it does not interleave. Disks formatted by `*FORMAT` use physical order.

### 2.4 Disk-side selection

Because the WD1793 supports double-sided disks via the `s` bit in the Type II command byte, TR-DOS files can span both sides of a disk. The directory itself spans both sides: the catalog (sectors 1 and 2 of cylinder 0) is on side 0; the disk descriptor (sector 8 of cylinder 0) is on side 0; but file data can be on either side.

When TR-DOS reads a file, it follows the chain of "next sector" pointers in the directory entry, which can cross from side 0 to side 1 (and back). Software that does raw sector access (e.g., custom loaders) must handle the side bit explicitly.

---

## §3. Sector Layout

### 3.1 What lives where on a TR-DOS disk

The on-disk layout of a TR-DOS disk is:

| Cylinder | Side | Sector(s) | Content |
|---|---|---|---|
| 0 | 0 | 1 | **Sector 0 of the catalog** (first 32 directory entries, 16 bytes each) |
| 0 | 0 | 2 | **Sector 1 of the catalog** (next 32 directory entries) |
| 0 | 0 | 3 | **Sector 2 of the catalog** (next 32 directory entries) |
| 0 | 0 | 4 | **Sector 3 of the catalog** (next 32 directory entries) |
| 0 | 0 | 5–7 | (typically free for user data; rarely used for catalog) |
| 0 | 0 | 8 | **Disk descriptor** ("system info" sector) — see §7 |
| 0 | 0 | 9 | **Backup copy of the disk descriptor** (optional; usually a duplicate of sector 8) |
| 0 | 0 | 10 | (typically free) |
| 0 | 1 | 1–10 | File data (sectors allocated to user files) |
| 1–79 | 0/1 | 1–10 | File data (sectors allocated to user files) |

### 3.2 Catalog layout

The TR-DOS catalog (the "directory" in modern DOS terminology) is stored in **sectors 1, 2, 3, and 4 of cylinder 0, side 0**. Each sector holds **32 directory entries** (each 16 bytes long, so 32 × 16 = 512 bytes per sector). The total catalog capacity is therefore **4 × 32 = 128 entries**.

This is the hard limit on the number of files a TR-DOS disk can hold: **128 files**, regardless of how much free space is available on the disk. If a disk has 128 files, you cannot add another file even if there are 500 KB free.

Some TR-DOS extensions (TR-DOS 6.x, ETR-DOS) increase the catalog capacity by using additional catalog sectors, but the base TR-DOS 5.03 / 5.04 format is limited to 128 entries.

### 3.3 Disk descriptor location

The **disk descriptor** is a single sector (512 bytes) at **cylinder 0, side 0, sector 8** that describes the disk as a whole: the disk's TR-DOS version, the disk's geometry (80-track vs. 40-track, 2-sided vs. 1-sided), the position of the first free sector, the disk's free-space count, the disk's label, and other bookkeeping fields.

Sector 9 is a backup copy of the disk descriptor, written by some TR-DOS versions as a safety measure. If sector 8 is corrupted, the `*RECOVER` command can copy sector 9 back to sector 8 to restore the disk.

The full byte layout of the disk descriptor is in §7 below.

### 3.4 Boot sector

Unlike MS-DOS or CP/M, **TR-DOS has no boot sector in the usual sense**. There is no "boot loader" code on the disk that the BIOS executes on startup. Instead, the TR-DOS ROM itself contains the boot logic: when the user types `*CAT` or any other disk command, the TR-DOS ROM reads the disk descriptor (sector 8) to determine the disk's geometry, then reads the catalog (sectors 1–4) to build an in-memory file table.

This means a TR-DOS disk is "bootable" if and only if the user has TR-DOS paged into the Spectrum's ROM window. A TR-DOS disk inserted into a non-TR-DOS machine (e.g., a +3 without Beta Disk Interface hardware) cannot be booted.

Some commercial disks include a small "auto-loader" program in sector 0 of cylinder 0, but this is a software convention, not a TR-DOS format requirement. The TR-DOS ROM does not auto-execute any sector on insertion.

### 3.5 User-data sector allocation

Sectors 5, 6, 7, and 10 of cylinder 0 side 0, plus all sectors on cylinder 0 side 1 and all subsequent cylinders, are available for user data. TR-DOS allocates sectors to files on a **first-fit basis**, scanning the catalog for the first free sector after the last used sector.

Files do **not** have to be contiguous on the disk — TR-DOS files can have arbitrary sector chains (like MS-DOS, unlike CP/M which uses contiguous extents). However, the TR-DOS `SAVE` command always writes files contiguously (in consecutive sectors), so fragmented files are rare unless the disk has been heavily edited.

---

## §4. Directory Structure

### 4.1 The 128-entry catalog

The TR-DOS directory (catalog) consists of **128 entries**, each 16 bytes long, occupying sectors 1–4 of cylinder 0 side 0. Entries are stored in entry-number order: entry 0 occupies bytes 0–15 of sector 1; entry 1 occupies bytes 16–31 of sector 1; entry 31 occupies bytes 496–511 of sector 1; entry 32 occupies bytes 0–15 of sector 2; and so on.

A directory entry can be in one of three states:

- **Free (unused)**: the first byte (byte 0) of the entry is `#00`. The entry is available for a new file.
- **Used (file)**: the first byte is a non-zero file-type code (`#42` for B, `#43` for C, etc. — see §5). The remaining 15 bytes describe the file.
- **Deleted**: the first byte is `#01`. The entry was used but the file was deleted with `*ERASE`; the entry is marked as deleted but the directory slot is not freed. The `*RECOVER` command can sometimes undelete such files.

### 4.2 Catalog iteration algorithm

To iterate over the directory, TR-DOS (and disk-image tools) typically do:

```pseudo
for entry = 0 to 127:
    read the 16-byte entry from catalog sector
    if byte[0] == 0: stop iterating (free entry marks end of catalog)
    if byte[0] == 1: skip (deleted entry, not shown in *CAT)
    else: process the file (byte[0] is the file type, bytes 1–14 are the file spec)
```

The convention is that the catalog has no "holes" — once a free entry (byte 0 == 0) is encountered, all subsequent entries are also free. This is a **soft convention**: TR-DOS itself always packs the catalog, but custom tools can leave holes, in which case `*CAT` stops at the first free entry.

### 4.3 The catalog as a TR-DOS "file"

From TR-DOS's point of view, the catalog is not a regular file — it cannot be read or written with `LOAD` or `SAVE`. Instead, the TR-DOS ROM has dedicated routines for reading and writing catalog entries. User software that wants to read the catalog directly (e.g., a custom disk-catalog utility) must access the catalog sectors via raw WD1793 READ SECTOR commands.

In the .TRD file-image format (see [trd_scl_formats.md](trd_scl_formats.md)), the catalog is stored at byte offset 0 of the file (since sector 1 of cylinder 0 side 0 is the first sector of the image).

### 4.4 The `*CAT` listing

When the user types `*CAT` (or just `CAT`), TR-DOS reads the catalog sectors, iterates over the entries, and prints a listing like:

```
GAME       C  32768
LEVELS     D  16384
MUSIC      M  8192
HISCORES   #  512
```

The listing shows:

- The **filename** (8 characters, padded with spaces).
- The **file-type letter** (B, C, D, M, or #).
- The **file length in bytes**.

The TR-DOS catalog is sorted alphabetically by filename by default, but the on-disk order is the order in which files were created (with deleted entries skipped). The in-memory sort happens during the `*CAT` listing.

### 4.5 Filenames

TR-DOS filenames follow the CP/M convention:

- **8 characters** maximum, padded with spaces if shorter.
- Characters allowed: uppercase letters `A–Z`, digits `0–9`, and (in some implementations) the symbols `$ % ' - @ { } ~ ! ( ) & _ ^` (this set varies by TR-DOS version and by Soviet clone).
- Filenames are case-sensitive at the byte level but TR-DOS uppercases input filenames before lookup, so in practice filenames are all uppercase.
- No directory hierarchy — TR-DOS has no subdirectories.

The file extension is a **single letter** (not three characters as in MS-DOS): `B` for BASIC, `C` for CODE, `D` for DATA, `M` for Microdrive/MEMORY, `#` for stream/print. The extension is stored in byte 0 of the directory entry (see §5) and is **part of the filename** — you cannot have two files with the same name and different extensions, unlike MS-DOS.

### 4.6 Deleted entries and undeletion

When the user types `*ERASE "FILE"`, TR-DOS:

1. Finds the directory entry for `FILE`.
2. Marks the first byte as `#01` (deleted).
3. Does **not** clear the rest of the entry — the filename, length, and sector chain are still there.
4. Does **not** free the disk sectors — they are still marked as "used" by the directory's free-space accounting (see §8).

The `*RECOVER` command can undelete such files: it scans for entries with byte 0 == `#01`, sets byte 0 back to the file type, and the file becomes accessible again. **But** if any sectors have been re-used for new files between the `*ERASE` and the `*RECOVER`, the recovered file will contain garbage.

### 4.7 Catalog corruption

Because the catalog is only 4 sectors (2048 bytes), corruption of any of these sectors is catastrophic. TR-DOS has no catalog-redundancy mechanism beyond the sector-9 backup of the disk descriptor. If a catalog sector goes bad (magnetic media failure, head crash), the disk is unusable.

The standard recovery procedure is to use a sector-editor (e.g., **DISCED** by Aleksander Kuznetsov) to manually inspect and repair catalog sectors. This requires deep knowledge of the TR-DOS format — which is one reason this article exists.

---

## §5. File Types

### 5.1 The five file types

TR-DOS recognises **five file types**, identified by a single ASCII letter stored in the directory entry:

| Letter | Type code | Byte value | Description |
|---|---|---|---|
| **B** | BASIC | `#42` | A Spectrum BASIC program. Starts at the start of the program area (`PROG`), with the system variables set up. |
| **C** | CODE | `#43` | Machine-code (binary) data. Has an explicit load address; the `LOAD "x" CODE` command loads the bytes at that address. |
| **D** | DATA array | `#44` | A `DIM`-declared array (numeric or string) saved with `SAVE "x" DATA`. Contains the array name and dimensions in a header. |
| **M** | MEMORY / Microdrive | `#4D` | A "memory block" — equivalent to CODE in modern usage. Originally distinct (for Microdrive compatibility) but functionally equivalent to CODE. |
| **#** | PRINT stream | `#23` | Output captured from a `STREAM` or print redirect. Rarely used; treated as a sequence of bytes for printing. |

The byte values are simply the ASCII codes of the letters (`B` = `#42`, `C` = `#43`, etc.), with `#` = `#23`. This makes the file type easy to identify in a hex dump of the catalog.

### 5.2 BASIC files (type B)

A **BASIC file** contains:

- The Spectrum BASIC program text (the tokenised BASIC source).
- The system variables that describe the program (specifically, the values of `PROG`, `NXTLIN`, and `VARS`).
- Optionally, the variable area (the values of all `LET`-assigned variables and `DIM`-declared arrays).

The file is loaded by typing `LOAD "filename"` (without `CODE`, `DATA`, etc.). TR-DOS reads the file into memory starting at the Spectrum's BASIC program area (`#5C53` system variable), updates the system variables, and returns control to BASIC. The user can then `RUN` the program or `LIST` it.

### 5.3 CODE files (type C)

A **CODE file** contains:

- Raw binary data (machine code, screen memory, etc.).
- A 4-byte **header** at the start of the file: `load_addr (2 bytes LE), length (2 bytes LE)`.
- The binary data itself.

The file is loaded by typing `LOAD "filename" CODE` (or `LOAD "filename" CODE addr, length` to override the header). TR-DOS reads the header to determine the load address and length, then reads the binary data into the specified address.

The header is **separate from the directory entry** — the directory entry's length and sector-chain fields describe the entire file (header + data), but the load address is stored only in the header inside the file. The directory entry itself does not know the load address.

### 5.4 DATA files (type D)

A **DATA file** contains:

- A **3-byte header** at the start of the file: the first byte identifies whether the data is numeric (`#00`) or string (`#01`); the next two bytes form the array name (the letter of the array, e.g., `A` for `DIM A(...)`, plus a flag).
- The array contents.

The file is loaded by typing `LOAD "filename" DATA A()` (the array name must match the saved array). TR-DOS reads the header to determine the array type and name, then reads the data into the named array's storage in the variable area.

DATA files are rarely used on disk; most disk-based software uses CODE files for binary data instead.

### 5.5 MEMORY files (type M)

**MEMORY files** are functionally identical to CODE files. The distinction is historical: in the original TR-DOS 5.0 design, type M was used for files saved with `SAVE "x" MEMORY` (an early name for the `CODE` save), and type C was reserved for "compiled" code. In TR-DOS 5.03 / 5.04, both types are loaded the same way (`LOAD "x" CODE`), and software can save either type interchangeably.

In practice, most Soviet software uses type C for code files. Type M is occasionally seen on disks from the very early TR-DOS era (1985–1986).

### 5.6 PRINT stream files (type #)

**PRINT files** are the rarest type. They are created by redirecting the `LPRINT` or `STREAM` output to disk, e.g., `OPEN #4, "d", "FILENAME"` followed by `PRINT #4, "Hello"`. The output is captured byte-by-byte into the file.

The file has no header — it is pure ASCII (or tokenised BASIC, depending on what was printed). The file can be loaded into memory like any other file, but TR-DOS has no built-in command to "execute" a PRINT file; the user must `LOAD` it into a specific address and then process it programmatically.

PRINT files are essentially unused on real TR-DOS disks. Most software that needs to write ASCII data uses CODE files instead.

### 5.7 The file-type byte vs. the Spectrum header byte

The Spectrum's tape system uses a similar file-type classification: a tape file starts with a 17-byte header whose first byte is the file type (`#00` for BASIC, `#01` for DATA, `#03` for CODE). The TR-DOS file-type letter is **separate** from this tape header byte — the letter is in the directory entry; the tape-style header (if present) is in the file's data.

For BASIC files (type B), TR-DOS stores the file with a 17-byte Spectrum-style header at the start of the file data, then the BASIC program text. For CODE files (type C), TR-DOS stores a 4-byte header (`addr + length`); the Spectrum-style 17-byte header is not used.

This is one of the reasons that you cannot simply copy a file from tape to disk and expect it to work — the file format is different. The `*COPY` command (with the `T` option) handles the conversion between tape and disk formats.

---

## §6. Directory Entry Format

### 6.1 The 16-byte entry layout

Each TR-DOS directory entry is **exactly 16 bytes**. The layout is:

| Byte | Length | Field | Notes |
|---|---|---|---|
| 0 | 1 | **File type** | ASCII letter: `B`, `C`, `D`, `M`, `#`. `#00` = free entry; `#01` = deleted entry. |
| 1 | 8 | **Filename** | 8 characters, padded with spaces (`#20`). |
| 9 | 1 | **Extension letter** | The file-type letter again (`B`, `C`, `D`, `M`, `#`); redundant with byte 0. Some TR-DOS versions allow this to differ from byte 0 for compatibility with non-standard file types. |
| 10 | 2 | **File length in bytes** (LE) | The actual file length. The number of sectors used is `ceil(length / 512)`. |
| 12 | 2 | **Sector count** (LE) | The number of 512-byte sectors the file occupies. Equals `ceil(length / 512)` in most cases. |
| 14 | 1 | **First sector track** | The cylinder number (0–79) of the first sector of the file. |
| 15 | 1 | **First sector** | The sector number (1–10) of the first sector of the file. The side bit is **implicit**: track numbers `#00–#7F` mean side 0; track numbers `#80–#FF` mean side 1, with the actual cylinder being `track - #80`. |

So a file is described by its **type letter**, its **8-character filename**, its **byte length**, its **sector count**, and the **(cylinder, side, sector) of its first sector**. The remaining sectors are accessed by **reading consecutive sectors** from the first sector — TR-DOS files are always stored contiguously, even though the format technically supports non-contiguous storage.

### 6.2 The first-sector encoding

The encoding of the first sector is a bit subtle:

- **Byte 14 (track)**: cylinder 0–79 for side 0, cylinder 0–79 + 128 (`#80`–`#FF`) for side 1. So a value of `#83` means cylinder 3 of side 1.
- **Byte 15 (sector)**: sector number 1–10 (sectors are numbered starting from 1, not 0).

To compute the **physical** (cylinder, side, sector) of the first sector:

```
cylinder = (track_byte & 0x7F)
side = (track_byte >> 7) & 0x01
sector = sector_byte  (assumed 1–10)
```

This encoding allows the entire first-sector address to fit in two bytes (16 bits), with the side bit packed into the high bit of the track byte. It is one of TR-DOS's more elegant design choices.

### 6.3 File-data sector chaining

After the first sector, the file's remaining sectors are accessed by reading consecutive physical sectors. The order is:

- Sector 1 of the first cylinder/side.
- Sector 2 of the first cylinder/side.
- ...
- Sector 10 of the first cylinder/side.
- Sector 1 of the next cylinder/same side.
- ...
- When the side is exhausted (cylinder 79), switch to cylinder 0 of the other side and continue.
- When both sides are exhausted, the file is at end-of-disk (out of space).

This is a **linear** layout: the file occupies consecutive physical sectors, with side 0 cylinder N followed by side 1 cylinder N, not side 0 cylinder N followed by side 0 cylinder N+1. (This is sometimes called "cylinder interleaving" or "side-first ordering".)

The first sector's address (in the directory entry) plus the file's sector count (also in the directory entry) fully determines the file's location on disk. No further chaining information is needed.

### 6.4 Why TR-DOS does not have a chain

The TR-DOS directory entry stores **only the first sector's address** and the **sector count**. It does not store a chain of next-sector pointers (as MS-DOS does in the FAT, or as CP/M does in extent blocks).

This works because TR-DOS files are **always contiguous**: when `SAVE` writes a file, it allocates a contiguous run of sectors and stores the first sector + count in the directory. There is no fragmentation, no chained allocation.

The downside is that **fragmenting a TR-DOS file requires manual intervention** (e.g., using a sector editor). The upside is that the directory entry is simple (16 bytes per file) and the directory fits in a small number of sectors.

### 6.5 Worked example: a small file

Suppose we have a file `GAME    C` with length 1000 bytes (so it occupies 2 sectors: `ceil(1000/512) = 2`). The 16-byte directory entry would look like:

```
Byte    Value (hex)   Meaning
 0      43            File type 'C'
 1      47            'G'
 2      41            'A'
 3      4D            'M'
 4      45            'E'
 5      20            ' '
 6      20            ' '
 7      20            ' '
 8      20            ' '
 9      43            Extension 'C'
10      E8            Low byte of length (1000 = 0x03E8)
11      03            High byte of length
12      02            Low byte of sector count
13      00            High byte of sector count
14      00            First sector track (cylinder 0, side 0)
15      09            First sector number (sector 9)
```

This file occupies sectors 9 and 10 of cylinder 0 side 0. To read the file, TR-DOS issues two WD1793 READ SECTOR commands: one for sector 9 (full 512 bytes copied to memory), one for sector 10 (only 488 of 512 bytes copied, since the file is 1000 bytes total).

### 6.6 Length vs. sector count

The directory entry stores **both** the byte length (bytes 10–11) and the sector count (bytes 12–13). These are related by `sector_count = ceil(length / 512)`, but TR-DOS stores both for convenience — the byte length is needed when reading the file (to know how many bytes to copy to memory), and the sector count is needed when iterating over the directory (to know how many sectors to skip to find the next file's first sector).

A subtle point: the **last sector of a file may be only partially filled**. If a file is 1000 bytes long, the last 24 bytes of the second 512-byte sector are unused. TR-DOS reads the entire sector and copies only the first 1000 bytes to memory. The trailing 24 bytes are typically zero-filled when the file is saved (TR-DOS zeroes the unused portion of the last sector), but this is not guaranteed for files modified by non-TR-DOS tools.

### 6.7 Reserved and unused fields

All 16 bytes of the directory entry are used. There are no reserved or "for future use" fields. This means TR-DOS extensions (TR-DOS 6.x, ETR-DOS) that want to add long filenames, file dates, or other metadata must use a different directory format — they cannot extend the existing 16-byte entry without breaking TR-DOS 5.03 compatibility.

---

## §7. Disk Descriptor

### 7.1 The "system info" sector

The **disk descriptor** is a single 512-byte sector at **cylinder 0, side 0, sector 8** that describes the disk as a whole. It is the equivalent of an MS-DOS boot sector's BPB (BIOS Parameter Block) or a CP/M DPB (Disk Parameter Block), but in TR-DOS's own format.

The descriptor is read by the TR-DOS ROM on every disk operation (or cached in memory after the first read). It tells the ROM:

- What kind of disk this is (40-track or 80-track, 1-sided or 2-sided).
- Where the next free sector is (so `SAVE` knows where to write a new file).
- How many free sectors remain (so `*CAT` can display the free space).
- The disk's label / title.
- The disk's TR-DOS version (so the ROM knows which features are supported).

A backup copy of the disk descriptor is at sector 9, written by TR-DOS 5.03+ as a safety measure.

### 7.2 The descriptor byte layout

The disk descriptor's important fields (TR-DOS 5.03 / 5.04 layout):

| Offset | Length | Field | Notes |
|---|---|---|---|
| `#E5` | 1 | **Disk end-of-file marker** | Always `#00` for a non-write-protected disk; `#01` if the disk is "soft" write-protected (TR-DOS will refuse to write). |
| `#E6` | 1 | **First free sector's cylinder** | Cylinder number of the first free sector (where the next `SAVE` will write). |
| `#E7` | 1 | **First free sector's side bit + sector** | The high bit (bit 7) is the side bit (0 = side 0, 1 = side 1); bits 6–0 are the sector number (1–10). |
| `#E8` | 2 | **Free sector count** (LE) | The total number of free sectors remaining on the disk. |
| `#EA` | 1 | **Disk ID** | A non-zero value indicating a TR-DOS disk. Often `#01`. |
| `#EB` | 1 | **Number of used catalog sectors** | Always 4 in TR-DOS 5.03 / 5.04 (the catalog occupies sectors 1–4). |
| `#EC` | 2 | **Disk label / ID string** (continued) | Often a numeric ID like `#00A1`. |
| `#F0` | 8 | **Disk label** | Up to 8 ASCII characters of user-settable disk label. Padded with spaces. |
| `#F8` | 1 | **Number of files** | The count of non-deleted entries in the catalog (0–128). |
| `#F9` | 1 | **Free sectors (low byte)** | Redundant copy of the low byte of the free sector count. |
| `#FA` | 1 | **TR-DOS ID byte** | Always `#10` for TR-DOS-format disks. |
| `#FB` | 1 | **Disk format code** | `#16` for 80-track 2-sided, `#17` for 80-track 1-sided, `#18` for 40-track 2-sided, `#19` for 40-track 1-sided. |
| `#FC` | 1 | **Sides** | Number of sides (1 or 2). |
| `#FD` | 1 | **Tracks per side** | Number of tracks per side (40 or 80). |

(Note: the byte offsets are given in hex; the descriptor is 512 bytes long but most of the early bytes are unused — the important fields are at the end, in bytes `#E5`–`#FF`.)

### 7.3 The format-code field

The **disk format code** at offset `#FB` is the key field that identifies the disk's geometry:

| Code | Geometry |
|---|---|
| `#16` | 80 tracks × 2 sides × 10 sectors × 512 bytes (the standard TR-DOS 80-track format) |
| `#17` | 80 tracks × 1 side × 10 sectors × 512 bytes |
| `#18` | 40 tracks × 2 sides × 10 sectors × 512 bytes |
| `#19` | 40 tracks × 1 side × 10 sectors × 512 bytes |
| `#1A` | 80 tracks × 2 sides × 16 sectors × 256 bytes (the old TR-DOS 5.0 format) |
| `#1B` | 80 tracks × 1 side × 16 sectors × 256 bytes |

The TR-DOS ROM reads this byte on first access to a disk and configures its sector-reading routines accordingly. If the byte is unrecognised (e.g., a non-TR-DOS disk inserted by mistake), TR-DOS reports a "Disk not recognised" error.

### 7.4 The free-sector pointer

The **first-free-sector pointer** (bytes `#E6`–`#E7`) is critical to TR-DOS's free-space accounting. After every `SAVE`, TR-DOS:

1. Reads the first-free-sector pointer from the descriptor.
2. Writes the new file starting at that sector.
3. Updates the pointer to point to the next free sector (after the newly-written file).
4. Decrements the free-sector count by the number of sectors used.

This is a "high-water mark" allocation strategy: files are always written to the end of the used space, never into gaps left by deleted files. The result is that the disk can become "fragmented" in the sense that deleted files leave gaps that are not re-used, even though TR-DOS files themselves are always contiguous.

The `*MOVE` command (or similar disk-optimizer tools) can compact the disk by reading all files and rewriting them in a packed order, resetting the free-sector pointer to the end of the packed files.

### 7.5 The disk label

The **disk label** at offset `#F0` is 8 bytes of user-settable ASCII text. It is set by the `*FORMAT` command (with the `L=` option) or by the `*LABEL` command. The label is displayed by some catalog utilities but is not used by TR-DOS for any file-system purpose.

The label is padded with spaces (`#20`) if shorter than 8 characters, like the filename in a directory entry.

### 7.6 Extensions in TR-DOS 5.4 and later

TR-DOS 5.4 and later (including TR-DOS 6.x and ETR-DOS) use the unused bytes (`#00`–`#E4` and parts of `#E5`–`#FF`) to store additional information:

- **Long disk label** (up to 16 or 32 characters).
- **Disk creation date** (in CP/M format: 16-bit days-since-1978).
- **Owner / author string**.
- **TR-DOS version that created the disk**.
- **Custom geometry parameters** (for non-standard disks).

TR-DOS 5.03 ignores these fields; TR-DOS 5.4+ reads them but works fine without them. The result is that TR-DOS 5.03 disks work fine in TR-DOS 5.4+ (the new fields are simply absent), and TR-DOS 5.4+ disks work in TR-DOS 5.03 (the new fields are ignored).

### 7.7 Disk descriptor and `.TRD` image files

In the .TRD file-image format (see [trd_scl_formats.md](trd_scl_formats.md)), the disk descriptor is at byte offset `(8 - 1) * 512 = 3584` of the file (since it is the 8th sector of cylinder 0 side 0, and TR-DOS image files are stored as a linear sequence of sectors). Tools that read .TRD files typically parse the descriptor first to determine the disk's geometry before reading the catalog or file data.

---

## §8. Free-Space Tracking

### 8.1 No FAT, no bitmap

TR-DOS does **not** use a File Allocation Table (FAT) or a free-sector bitmap. Instead, free space is tracked by two fields in the disk descriptor (see §7):

1. **First free sector** (bytes `#E6`–`#E7`): the location of the next sector that will be allocated when `SAVE` writes a new file.
2. **Free sector count** (bytes `#E8`–`#E9`): the total number of free sectors remaining on the disk.

Together, these two fields describe free space as a single contiguous run from the first free sector to the end of the disk. There is no concept of "scattered free space" — TR-DOS assumes all free space is contiguous, located at the end of the disk, after all the existing files.

### 8.2 How `SAVE` allocates sectors

When the user types `SAVE "filename" CODE addr, length`, TR-DOS:

1. Reads the disk descriptor to find the first free sector and the free sector count.
2. Computes the number of sectors needed: `needed = ceil(length / 512)`.
3. Checks that `needed <= free_sector_count`; if not, returns a "Disk full" error.
4. Writes the file's data starting at the first free sector.
5. Updates the first-free-sector pointer to point past the end of the newly-written file.
6. Decrements the free sector count by `needed`.
7. Adds a directory entry for the new file, pointing to the (former) first free sector.

This is a **high-water mark** allocation strategy: each new file is appended to the end of the used space. There is no search for a "best fit" or "first fit" gap among existing files — those gaps are not re-used.

### 8.3 How `*ERASE` "frees" sectors

When the user types `*ERASE "filename"`, TR-DOS:

1. Finds the directory entry for the file.
2. Marks the entry as deleted (byte 0 = `#01`).
3. **Does not** update the first-free-sector pointer.
4. **Does not** increment the free sector count.

The freed sectors are **not** actually added back to the free-space pool. They remain "lost" until either:

- The disk is reformatted (`*FORMAT`), which resets the first-free-sector pointer to the beginning and the free-sector count to the disk capacity.
- The disk is compacted (`*MOVE` or a similar tool), which reads all the live files, writes them back in a packed order, and resets the first-free-sector pointer.
- The deleted file is undeleted (`*RECOVER`), which restores the directory entry and "uses" the sectors again.

This is a deliberate design choice: TR-DOS does not have a FAT because the high-water-mark strategy means files always append to the end of the disk, so the "free space" is always a single contiguous run.

### 8.4 Worked example

Suppose a freshly-formatted disk has 1600 free sectors (80 × 2 × 10 = 1600 sectors total). The first-free-sector pointer is at cylinder 0, side 0, sector 1 (the start of the disk after the reserved catalog/descriptor sectors — actually, after cylinder 0 side 0, sectors 1–10 are reserved, so the first free sector is at cylinder 0 side 0 sector 1 according to TR-DOS, but in practice it's at cylinder 0 side 1 sector 1, since sectors 1–10 of side 0 are reserved for the catalog and descriptor).

The user saves three files:

| Step | File size | Sectors used | Free count after | First free sector after |
|---|---|---|---|---|
| Initial | — | — | 1600 | cyl 0 side 1 sec 1 |
| Save A | 1500 B | 3 | 1597 | cyl 0 side 1 sec 4 |
| Save B | 800 B | 2 | 1595 | cyl 0 side 1 sec 6 |
| Save C | 2000 B | 4 | 1591 | cyl 0 side 1 sec 10 |
| Erase A | — | — | 1591 (no change!) | cyl 0 side 1 sec 10 (no change!) |
| Save D | 500 B | 1 | 1590 | cyl 1 side 0 sec 1 (skipping over the now-dead sectors of A) |

After erasing file A, the 3 sectors it occupied (cyl 0 side 1 sec 1–3) are "dead" — not in the free-space pool. TR-DOS does not re-use them. File D is written starting at the current first-free-sector (cyl 0 side 1 sec 10), which means 3 sectors of capacity are wasted.

This is the cost of TR-DOS's simple free-space accounting: deleted-file sectors are not reclaimed until a `*MOVE` operation.

### 8.5 The `*MOVE` compaction command

The `*MOVE` command (or the more sophisticated **DISCOPY**, **DISKCOPY**, or **ADVANCED MOVE** tools) compacts the disk:

1. Read all live files into memory (in TR-DOS's `#5000`–`#FF00` buffer area).
2. Reformat the destination disk.
3. Write the live files back, in directory order, packing them at the start of the disk.
4. Re-create the directory entries on the destination disk.

The result is a disk with no dead sectors: all free space is contiguous, at the end of the disk. This is the TR-DOS equivalent of an MS-DOS defragmenter.

`*MOVE` typically requires two drives (source and destination), since TR-DOS cannot easily hold an entire disk in memory. With a single drive, the operation requires swapping disks repeatedly.

---

## §9. Boot Process

### 9.1 What "booting a TR-DOS disk" means

Unlike MS-DOS or modern operating systems, a TR-DOS disk does not "boot" in the sense of running an autonomous bootloader. Instead, the user types a command (`*CAT`, `LOAD "x"`, etc.) and the TR-DOS ROM performs the requested operation.

The closest thing to "booting" is the user typing `*CAT` on a freshly-inserted disk: TR-DOS reads the disk descriptor and catalog, displays the file listing, and returns control to the user. From there, the user types `LOAD "x"` to load a program.

### 9.2 The boot sequence

When the user types `*CAT`:

1. **Page TR-DOS in** (via the `#3D00–#3DFF` write — see [beta_disk_interface.md](beta_disk_interface.md) §4).
2. **Select the drive** (write the drive-select byte to port `#FF`).
3. **Issue a RESTORE command** to the WD1793 (homing the head to cylinder 0 and starting the motor via `/HDLD`).
4. **Wait for spin-up** (6 index pulses, ~1.2 seconds).
5. **Read the disk descriptor** (sector 8 of cylinder 0 side 0). TR-DOS checks the format code at offset `#FB` to verify this is a TR-DOS disk and to determine the geometry.
6. **Read the catalog** (sectors 1, 2, 3, 4 of cylinder 0 side 0). TR-DOS builds an in-memory table of all files (sorted alphabetically).
7. **Display the catalog** (the `*CAT` listing: filename, type, length).
8. **Page TR-DOS out** and return to BASIC.

This sequence takes about 1.5 seconds (mostly motor spin-up), assuming the disk is already spinning. If the motor was off, the first `*CAT` takes 1.5–2 seconds; subsequent `*CAT`s are faster (the motor stays on for ~3 seconds after the last command).

### 9.3 The `LOAD "x"` command

When the user types `LOAD "filename"`:

1. Page TR-DOS in.
2. Read the catalog (as above) and find the entry for `filename`.
3. Compute the (cylinder, side, sector) of the file's first sector (using the entry's first-sector field, with side bit packed in the high bit of the track byte — see §6.2).
4. Issue a SEEK command to position the head at the file's first cylinder.
5. Issue READ SECTOR commands for each of the file's sectors, reading them into memory.
6. For a BASIC file, update the BASIC system variables (`PROG`, `NXTLIN`, etc.).
7. For a CODE file, the first 4 bytes of the file (the load address + length header) are processed to determine the load destination; the remaining bytes are loaded at that destination.
8. Page TR-DOS out and return to BASIC.

This sequence is much faster than tape loading: a 30 KB file loads in 0.5–1 second on a TR-DOS disk, vs. 2–3 minutes on tape.

### 9.4 The "auto-boot" disk convention

Many commercial TR-DOS disks include a small BASIC program called `boot` (or `BOOT`, `loader`, etc.) that contains a `LOAD "main" CODE : RANDOMIZE USR addr` sequence. The user types `LOAD "boot"` and the boot program loads and runs the main program automatically.

Some disks go further and include a **boot loader** in the catalog itself: a directory entry with a special name (often `boot` or `*`) that TR-DOS auto-executes on disk insertion. This is a **software convention**, not a TR-DOS format requirement — the TR-DOS ROM does not auto-execute any sector on insertion. The user must type a `LOAD` command.

The reason this works is that TR-DOS BASIC allows programs to call TR-DOS commands programmatically. A "boot" program can include `LOAD "main" CODE` and `RANDOMIZE USR main_addr` as BASIC statements, and when the user types `LOAD "boot" : RUN`, the main program is loaded and executed.

### 9.5 Custom boot sectors

A few TR-DOS disks use **custom boot sectors** that bypass the TR-DOS ROM entirely. The disk's sector 0 of cylinder 0 contains a small machine-code program that the user loads with `LOAD "" CODE 16384, 512 : RANDOMIZE USR 16384` (or similar). This program then reads the rest of the disk directly via the WD1793 ports, bypassing TR-DOS.

This is used by:

- **Protected loaders**: games that use non-standard sector layouts or DRM, which TR-DOS cannot read.
- **Custom-format disks**: disks that use double-density, non-standard sector sizes, or unusual geometries.
- **Demoscene productions**: demos that need cycle-exact control over disk access for visual effects.

For these disks, the TR-DOS catalog may be empty or may contain only the loader file. The rest of the disk is read via raw WD1793 commands from the loader code. See [05_reversing/](../../08_reverse_engineering/README.md) for more on custom loaders.

---

## 10. Cross-references

### 10.1 Within the storage section

- [beta_disk_interface.md](beta_disk_interface.md) — the hardware interface that TR-DOS uses to read and write this format. The port map, the address decoder, and the ROM-paging mechanism are all covered there.
- [fdc_vg93.md](fdc_vg93.md) — the WD1793 / KR1818VG93 chip that physically reads and writes the sectors. The Type II READ SECTOR / WRITE SECTOR commands are how TR-DOS accesses individual sectors of a TR-DOS disk.
- [mfm_encoding.md](mfm_encoding.md) — the signal layer recorded on the magnetic media. TR-DOS files are organised into 512-byte MFM sectors, which are organised into tracks, which are organised into cylinders.
- [disk_format_overview.md](disk_format_overview.md) — a comparison of TR-DOS with the other Spectrum disk formats (+3 DOS, CP/M, Opus). Useful for understanding the trade-offs between the formats.
- [plus3_dos_format.md](plus3_dos_format.md) — the +3's logical disk format, which is the direct competitor to TR-DOS. The two are not compatible, but they share some CP/M-derived ideas.
- [cpm_disk_format.md](cpm_disk_format.md) — the CP/M disk format, which heavily influenced TR-DOS's directory structure (CP/M-style filenames, contiguous extents).
- [opus_discovery_format.md](opus_discovery_format.md) — the Opus Discovery format, an alternative Western disk system that coexisted with TR-DOS.
- [trd_scl_formats.md](trd_scl_formats.md) — the .TRD and .SCL file-image formats used to preserve TR-DOS disks. A .TRD file is a byte-for-byte image of a TR-DOS disk (per the layout described in this article), plus a small header.
- [dsk_fdi_formats.md](dsk_fdi_formats.md), [udi_format.md](udi_format.md), [scp_format.md](scp_format.md) — other disk-image formats that can also store TR-DOS disks at various preservation levels.

### 10.2 Adjacent topics

- [04_operating_systems/](../../04_operating_systems/) — for the TR-DOS ROM itself, its command set, and its interaction with the BASIC ROM.
- [05_reversing/](../../08_reverse_engineering/README.md) — for protection schemes that exploit TR-DOS format quirks (deleted entries, custom boot sectors, non-standard sector layouts).
- [11_emulation/](../../11_emulation/) — for cycle-exact TR-DOS disk emulation in modern emulators.

### 10.3 External references

- **The TR-DOS 5.03 ROM source code** — disassemblies are widely available (zxevo.ru, WoS archive). Reading the source is the best way to understand the on-disk format; the format is defined by what the ROM code reads and writes.
- **"TR-DOS File Format Specification" by Andrew Owen** — the original designer's notes, occasionally available on Spectrum community sites.
- **The TRDOS.LST file in the UnrealSpeccy emulator distribution** — a detailed format specification maintained by the emulator community.
- **The comp.sys.sinclair FAQ and the Russian-language zx-pk.ru forum** — community-maintained documentation on TR-DOS variants and extensions.
- **The "ESXDOS" documentation** — for the modern TR-DOS-compatible system used by DivMMC and similar peripherals. ESXDOS extends TR-DOS with long filenames, subdirectories, and FAT compatibility.

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

You are free to:

- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

- **Attribution** — you must give appropriate credit (a link to this article is sufficient), indicate if changes were made, and indicate the license under which the original is released.
- **ShareAlike** — if you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

The full legal text is available at the link above.

The trademarks **TR-DOS**, **TR-DOS 5.03**, **TR-DOS 5.04**, **TR-DOS 6.x**, **ETR-DOS**, **Mr Gluk Reset Service**, **ESXDOS**, **Technology Research Ltd**, **Beta Disk Interface**, **WD1793**, **KR1818VG93**, **ZX Spectrum**, **ZX Spectrum Next**, **ZX Evolution**, **Pentagon**, **Scorpion**, **CP/M**, **Digital Research**, **DISCOPY**, **DISKCOPY**, **DISCED**, **DivMMC**, and others mentioned in this document are the property of their respective owners and are used here for identification and educational purposes only. No endorsement by, or affiliation with, any of these trademark holders is implied.
