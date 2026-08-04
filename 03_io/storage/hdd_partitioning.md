[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# Hard Disk Partitioning and Filesystems on the ZX Spectrum

**Scope:** The **partition table** and **filesystem layers** that sit between the raw sectors of a Spectrum mass-storage device (CompactFlash, SD card, hard disk) and the files that ESXDOS, NextZXOS, and IS-DOS present to the user. This article covers the **Master Boot Record**, the **BIOS Parameter Block**, the **FAT16 and FAT32** filesystems, the **Long File Name** extension, and the Russian **IS-DOS** alternative.

This is the **filesystem companion** to the hardware articles: [ide_interface.md](ide_interface.md) and [sd_interface.md](sd_interface.md) explain how a sector reaches the device; this article explains how those sectors are organized into directories and files. The image-format article [hdf_mgt_formats.md](hdf_mgt_formats.md) explains how a modern PC captures the whole structure.

**Audience:** Emulator authors implementing a FAT driver, ESXDOS application programmers who need to understand cluster sizes and LFN quirks, archival tool authors building conversion utilities, and curious users who want to know what lives inside their SD card.

**Prerequisites:** The [overview article](hdd_overview.md) situates partitioning in the storage story; [esxdos.md](../../04_operating_systems/esxdos.md) covers the DOS that reads these filesystems.

**Depth:** Deep. Byte-level layout of the MBR, BPB, FAT, and directory entries; the FAT16/FAT32 differences; the LFN encoding; and the IS-DOS on-disk structure. References to the OS articles where the API layer takes over.

---

## §1. Introduction

### 1.1 Why the Spectrum needs a partition table

A floppy disk has a single filesystem that starts at sector 0 — there is no partition table, no choice of filesystem, and no ambiguity. A mass-storage device (CompactFlash, SD card, hard disk) is different: it is large enough to hold **multiple filesystems side by side**, and the device must tell the host where each one begins and ends. The structure that does this is the **partition table**, stored in the first sector of the device.

The Spectrum inherited the PC's partitioning scheme wholesale: the **Master Boot Record (MBR)** at sector 0, containing a four-entry partition table, each entry pointing at a contiguous run of sectors that holds a single filesystem (a "volume" or "partition"). This was not inevitable — the Spectrum could have used a custom scheme — but adopting the PC standard meant a Spectrum SD card is readable by any modern computer with no conversion. This interchangeability is one of ESXDOS's key design wins.

### 1.2 The two filesystems that matter

Two filesystems have been used on Spectrum mass storage:

- **FAT** (File Allocation Table, in its FAT16 and FAT32 variants) — the PC standard, used by ESXDOS, NextZXOS, and every modern interface. This is what 99% of Spectrum mass-storage volumes use in 2024.
- **IS-DOS** — a Russian hierarchical filesystem, MS-DOS-compatible at the directory-entry level but with its own allocation scheme. Used mainly on Nemo IDE and KAY hardware in the 1990s; rare today.

This article covers both, but FAT dominates because it is what the DivIDE, DivMMC, ZXMMC, Next, and Z-Controller all use. IS-DOS is covered in §6 as historical context and cross-referenced to its own OS article.

## §2. The Master Boot Record and Partition Table

### 2.1 The boot sector layout

Sector 0 of every Spectrum mass-storage device is the **Master Boot Record** (MBR), a 512-byte sector with this structure:

| Offset | Size | Field | Purpose |
|---|---|---|---|
| `0x000` | 446 | Bootstrap code | On a PC this is boot loader code; on a Spectrum volume it is usually empty or a stub |
| `0x1BE` | 16 | Partition entry 1 | First partition descriptor |
| `0x1CE` | 16 | Partition entry 2 | Second partition descriptor |
| `0x1DE` | 16 | Partition entry 3 | Third partition descriptor |
| `0x1EE` | 16 | Partition entry 4 | Fourth partition descriptor |
| `0x1FE` | 2 | Signature | `0x55 0xAA` — marks a valid boot sector |

The signature `0x55AA` at offset `0x1FE` is the universal marker that distinguishes a boot sector from random data. ESXDOS checks it before reading the partition table; an image without it is rejected.

### 2.2 The 16-byte partition entry

Each of the four partition entries is 16 bytes:

| Offset | Size | Field | Meaning |
|---|---|---|---|
| `0x00` | 1 | Status | `0x80` = bootable, `0x00` = not bootable (other values invalid) |
| `0x01` | 3 | CHS start | Starting cylinder/head/sector (legacy; usually ignored) |
| `0x04` | 1 | Type | Filesystem type code (see below) |
| `0x05` | 3 | CHS end | Ending cylinder/head/sector (legacy; usually ignored) |
| `0x08` | 4 | LBA start | Starting sector, in 32-bit LBA (little-endian) — **the field ESXDOS uses** |
| `0x0C` | 4 | LBA size | Number of sectors in the partition (little-endian) |

The **CHS fields** (cylinder/head/sector) are a legacy of pre-LBA hard disks and are almost always wrong on modern media. ESXDOS, like every modern OS, ignores them and uses the **LBA start** and **LBA size** fields exclusively. This is why an SD card prepared on a PC works on a Spectrum: both read the LBA fields and ignore the CHS fields.

### 2.3 Partition type codes

The type byte at offset `0x04` tells the host what filesystem the partition contains. The codes ESXDOS recognizes:

| Code | Filesystem |
|---|---|
| `0x01` | FAT12 (small volumes, under ~16 MB) |
| `0x04` | FAT16 (small, under 32 MB) |
| `0x06` | FAT16 (large, 32 MB – 2 GB) |
| `0x0B` | FAT32 |
| `0x0C` | FAT32 with LBA |
| `0x0E` | FAT16 with LBA |

ESXDOS mounts the first partition whose type matches one of these. A partition of any other type (Linux `0x83`, NTFS `0x07`, etc.) is skipped. For a single-FAT-volume card, the first partition entry is FAT and the other three are zeroed (type `0x00` = unused).

### 2.4 The typical single-partition layout

A typical Spectrum SD card has a single FAT partition starting at LBA 2048 (1 MB into the card, leaving room for the MBR and alignment). The partition table looks like:

```
Entry 1:  status=0x80  type=0x0C  LBA_start=0x0800  LBA_size=(card_sectors - 0x0800)
Entry 2:  all zero (unused)
Entry 3:  all zero (unused)
Entry 4:  all zero (unused)
```

The 1 MB offset (LBA 2048) is a modern convention for **4 KB alignment**: flash media (SD cards, SSDs) erase in 4 KB blocks, and aligning the partition start to a 4 KB boundary (LBA 2048 × 512 = 1 MB) avoids write amplification. ESXDOS does not require this alignment, but it improves card longevity, so modern formatting tools produce it by default.

## §3. FAT: The Common Filesystem

### 3.1 The volume layout

A FAT volume (the region inside one partition) is laid out as four contiguous regions:

```
+-----------------+  <- partition start (LBA = partition_LBA_start)
| Reserved region |  <- boot sector + (usually) a few backup sectors
+-----------------+
| FAT #1          |  <- the File Allocation Table
+-----------------+
| FAT #2          |  <- a second copy (usually identical to #1)
+-----------------+
| Root directory  |  <- FAT12/16 only; FAT32 puts this in the data region
+-----------------+
| Data region     |  <- files and subdirectories, organised into clusters
|                 |
+-----------------+  <- partition end
```

The sizes and start offsets of each region are computed from the **BIOS Parameter Block (BPB)** in the boot sector (§3.2). The two FAT copies are kept in sync by the DOS: every allocation change is written to both, so that a bad sector in one FAT does not lose the whole volume. ESXDOS reads FAT #1 by default and falls back to FAT #2 only if #1 is corrupt.

### 3.2 The BIOS Parameter Block (BPB)

The first sector of the partition (the **boot sector** or **VBR**, Volume Boot Record) contains the **BPB** at offset `0x0B` (immediately after the 11-byte jump instruction and OEM name). The fields a FAT driver must read:

| Offset | Size | Field | Meaning |
|---|---|---|---|
| `0x00B` | 2 | `BytsPerSec` | Bytes per sector — always 512 on Spectrum media |
| `0x00D` | 1 | `SecPerClus` | Sectors per cluster (1, 2, 4, 8, 16, 32, 64) |
| `0x00E` | 2 | `RsvdSecCnt` | Reserved sectors before FAT #1 (usually 1 on FAT16, 32 on FAT32) |
| `0x010` | 1 | `NumFATs` | Number of FAT copies (almost always 2) |
| `0x011` | 2 | `RootEntCnt` | Root directory entries (FAT12/16 only; 0 on FAT32) |
| `0x013` | 2 | `TotSec16` | Total sectors, 16-bit (0 if the volume is > 65535 sectors) |
| `0x015` | 1 | `Media` | Media descriptor (`0xF8` = hard disk) |
| `0x016` | 2 | `FATSz16` | Sectors per FAT (FAT12/16; 0 on FAT32) |
| `0x020` | 4 | `TotSec32` | Total sectors, 32-bit (used when TotSec16 is 0) |
| `0x024` | 1 | `DrvNum` | Physical drive number (unused on Spectrum) |
| `0x036` | 1 | `BootSig` | Extended boot signature (`0x29` if the next fields are present) |
| `0x037` | 4 | `VolID` | Volume serial number |
| `0x03B` | 11 | `VolLab` | Volume label |
| `0x042` | 8 | `FilSysType` | `FAT16   ` or `FAT32   ` (informational) |

For FAT32, additional fields appear at higher offsets (`FATSz32`, `RootClus`, `FSInfo`), documented in §4.

From the BPB, the driver computes the key offsets:

- **FAT #1 start** = `partition_start + RsvdSecCnt`
- **FAT #2 start** = `FAT #1 start + FATSz16` (or `FATSz32` on FAT32)
- **Root directory start** = `FAT #2 start + FATSz16` (FAT16 only)
- **Data region start** = `root dir start + (RootEntCnt × 32) / BytsPerSec` (FAT16)
- **Data region start** = `FAT #2 start + FATSz32` (FAT32, no fixed root dir)

These four offsets are everything the DOS needs to navigate the volume. The rest of FAT access is reading and writing clusters in the data region and following the allocation chain in the FAT.

### 3.3 The File Allocation Table

The **FAT** is an array of cluster-link entries. Each entry describes one cluster in the data region:

- The entry is **0** if the cluster is free.
- The entry is a **cluster number** (pointing at the next cluster in the file) if the cluster is part of a file and is not the last cluster.
- The entry is an **end-of-chain marker** (`>= 0xFFF8` for FAT16, `>= 0x0FFFFFF8` for FAT32) if the cluster is the last in a file.
- The entry is a **bad-cluster marker** (`0xFFF7` / `0x0FFFFFF7`) if the cluster is unusable.

To read a file, the DOS starts at the file's **first cluster** (stored in its directory entry), reads that cluster's data, then looks up that cluster's FAT entry to find the next cluster, and repeats until it hits an end-of-chain marker. This linked-list structure is what gives FAT its name: the table is a map of how clusters chain together into files.

The entry width depends on the FAT variant:

| Variant | Entry width | Max clusters | Typical volume size |
|---|---|---|---|
| FAT12 | 12 bits | 4,078 | under ~16 MB (floppies) |
| FAT16 | 16 bits | 65,524 | 16 MB – 2 GB |
| FAT32 | 28 bits | 268,435,444 | 512 MB – 2 TB |

The first two FAT entries (clusters 0 and 1) are reserved: cluster 0 holds the media descriptor byte, and cluster 1 holds a end-of-chain marker. Real data clusters start at cluster 2, which corresponds to the first cluster in the data region. This off-by-two is a perennial source of bugs in FAT drivers: cluster number `N` maps to data-region offset `(N - 2) × SecPerClus × BytsPerSec`.

### 3.4 Directory entries

Every directory — the root and every subdirectory — is a sequence of **32-byte directory entries**. In a FAT12/16 volume the root directory has a fixed size (set by `RootEntCnt` in the BPB, usually 512 entries = 16 KB); subdirectories are files full of directory entries, stored in the data region and growable. In FAT32 the root directory is also a growable cluster chain (its first cluster is in the `RootClus` BPB field).

The 32-byte directory entry format:

| Offset | Size | Field | Meaning |
|---|---|---|---|
| `0x00` | 11 | `Name` | 8-byte name + 3-byte extension, space-padded, uppercased |
| `0x0B` | 1 | `Attr` | Attributes (see below) |
| `0x0C` | 1 | `NTRes` | Windows NT reserved (lowercase flags) |
| `0x0D` | 1 | `CrtTimeTenth` | Creation time, tenths of a second |
| `0x0E` | 2 | `CrtTime` | Creation time |
| `0x10` | 2 | `CrtDate` | Creation date |
| `0x12` | 2 | `LstAccDate` | Last access date |
| `0x14` | 2 | `FstClusHI` | First cluster, high 16 bits (FAT32 only; 0 on FAT16) |
| `0x16` | 2 | `WrtTime` | Last write time |
| `0x18` | 2 | `WrtDate` | Last write date |
| `0x1A` | 2 | `FstClusLO` | First cluster, low 16 bits |
| `0x1C` | 4 | `FileSize` | File size in bytes (32-bit) |

The attribute byte encodes:

| Bit | Name | Meaning |
|---|---|---|
| 0 | Read-only | File cannot be written or deleted |
| 1 | Hidden | Hidden from normal directory listing |
| 2 | System | System file |
| 3 | Volume label | Entry is the volume label, not a file |
| 4 | Directory | Entry is a subdirectory, not a file |
| 5 | Archive | File has changed since last backup |
| 6 | — | Reserved |
| 7 | — | Reserved |

A first byte of `0x00` means "this and all following entries are free" (the directory ends here). A first byte of `0xE5` means "this entry is deleted" (the slot is reusable but the directory continues). Any other first byte is the first character of a live entry's name.

## §4. FAT16 vs FAT32

### 4.1 The variant chosen by the formatter

A formatting tool chooses FAT12, FAT16, or FAT32 based on the volume size and the cluster count. The Microsoft conventions (which every formatter follows):

| Volume size | Variant | Typical `SecPerClus` |
|---|---|---|
| Under ~16 MB | FAT12 | 1–4 |
| 16 MB – 128 MB | FAT16 | 2 |
| 128 MB – 256 MB | FAT16 | 4 |
| 256 MB – 512 MB | FAT16 | 8 |
| 512 MB – 1 GB | FAT16 | 16 |
| 1 GB – 2 GB | FAT16 | 32 |
| 2 GB – 8 GB | FAT32 | 1 |
| 8 GB – 16 GB | FAT32 | 8 |
| 16 GB – 32 GB | FAT32 | 16 |
| Over 32 GB | FAT32 | 32 (but Windows defaults to exFAT here) |

The variant is **not stored explicitly** in the BPB. Instead, the driver computes it from the cluster count: under 4,084 clusters is FAT12; under 65,524 is FAT16; otherwise FAT32. This is why a formatter must pick a cluster size that produces the right cluster count for the intended variant — a mismatched volume will be misread.

For Spectrum use, FAT16 covers cards up to 2 GB, and FAT32 covers everything larger. The choice is usually made automatically by the formatting tool.

### 4.2 The FAT32 extensions

FAT32 adds three things over FAT16:

- **Larger FAT entries** (32 bits, of which 28 are used), allowing far more clusters.
- **A growable root directory.** The root is no longer a fixed region after the FATs; it is a cluster chain (starting at `RootClus`, usually cluster 2) stored in the data region. This removes the 512-entry root-directory limit.
- **An FSInfo sector** and a backup boot sector, providing the DOS with a hint of the next free cluster and a redundant copy of the BPB.

The FAT32 BPB extends the FAT16 BPB with these fields at offset `0x024`:

| Offset | Size | Field | Meaning |
|---|---|---|---|
| `0x024` | 4 | `FATSz32` | Sectors per FAT (FAT32; replaces `FATSz16`, which is 0) |
| `0x02C` | 4 | `RootClus` | Root directory's first cluster (usually 2) |
| `0x030` | 2 | `FSInfo` | Sector number of the FSInfo structure (usually 1) |
| `0x032` | 2 | `BkBootSec` | Backup boot sector (usually 6) |

The cluster-chain-following logic is otherwise identical to FAT16; only the entry width and the root-directory location differ.

### 4.3 Long File Names (LFN)

Plain FAT directory entries store only an 8.3 name (8 characters, dot, 3 characters), uppercased and space-padded. This is adequate for the floppy era but cramped for a modern software library where files have names like `Chuckie Egg (1983).z80`.

**VFAT Long File Names** solve this by prepending one or more **LFN entries** before the 8.3 entry. Each LFN entry is a 32-byte structure with the special attribute byte `0x0F` (read-only + hidden + system + volume — a combination that never occurs naturally, so the DOS recognizes it as an LFN marker). The LFN entry holds 13 UTF-16 characters of the long name; multiple LFN entries chain together to spell a name of any length up to 255 characters.

The LFN entry layout:

| Offset | Size | Field | Meaning |
|---|---|---|---|
| `0x00` | 1 | `Ord` | Sequence number (with `0x40` bit set on the last entry) |
| `0x01` | 10 | `Name1` | Characters 1–5 (UTF-16, 2 bytes each) |
| `0x0B` | 1 | `Attr` | Always `0x0F` (the LFN marker) |
| `0x0C` | 1 | `Type` | Always 0 |
| `0x0D` | 1 | `Chksum` | Checksum of the 8.3 name |
| `0x0E` | 12 | `Name2` | Characters 6–11 |
| `0x1A` | 2 | `FstClusLO` | Always 0 |
| `0x1C` | 4 | `Name3` | Characters 12–13 |

The LFN entries appear in **reverse order** (the last entry's name fragment comes first on disk), terminated by the regular 8.3 entry that holds the file's actual cluster pointer and size. Reading a directory therefore requires the DOS to accumulate LFN entries until it hits the 8.3 entry, then concatenate the name fragments in forward order.

ESXDOS (version 0.85+) supports LFN fully: files can have long names, and the `*.dir` command displays them. Earlier versions and some older DOSes show only the 8.3 "short name" that the formatter generated as a fallback. The short name is a mangled uppercase version with a numeric tail (`CHUCKI~1.Z80`), guaranteed unique within a directory.

## §5. The Cluster and Allocation Strategy

### 5.1 Why clusters exist

The FAT indexes the data region in **clusters**, not sectors. A cluster is `SecPerClus` sectors (always a power of 2). The reason for clustering is FAT size: if the FAT indexed every sector directly, a 2 GB volume with 512-byte sectors would need a 4-million-entry FAT — 8 MB of metadata, in addition to the data. Clustering at 32 sectors per cluster (16 KB) reduces the FAT to 128 KB, a 60× saving.

The cost is **internal fragmentation**: a file that is one byte larger than a whole number of clusters wastes the remainder of its last cluster. On a 16 KB cluster volume, the average waste per file is 8 KB. For a library of small Spectrum files (snapshots, music modules), this adds up — thousands of 40 KB snapshots on a 16 KB cluster volume waste 8 KB each, totalling tens of megabytes of slack.

### 5.2 Choosing `SecPerClus` for Spectrum use

For Spectrum mass storage, the formatter's default cluster size is usually fine, but the trade-offs are worth knowing:

| `SecPerClus` | Cluster size | FAT overhead | Slack per file | Good for |
|---|---|---|---|---|
| 1 | 512 B | Large | Tiny | Floppy-sized volumes only |
| 2 | 1 KB | Moderate | ~512 B | Small FAT16 volumes (under 128 MB) |
| 4 | 2 KB | Moderate | ~1 KB | Medium FAT16 volumes |
| 8 | 4 KB | Small | ~2 KB | Good default for small cards |
| 16 | 8 KB | Small | ~4 KB | Larger cards; aligns with SD erase blocks |
| 32 | 16 KB | Tiny | ~8 KB | Default on 1–2 GB FAT16 |
| 64 | 32 KB | Tiny | ~16 KB | Large FAT32 cards |

For a 512 MB card full of small files, **4 KB clusters** (`SecPerClus = 8`) minimize slack. For an 8 GB card, **8 KB or 16 KB clusters** are the modern default and the slack is negligible given the card's size. The formatter's automatic choice is rarely wrong.

### 5.3 How the DOS allocates a new file

When ESXDOS creates a file, it:

1. Scans the FAT for the first **free cluster** (an entry equal to 0). The FSInfo sector (FAT32) caches a hint of this, but the DOS can always fall back to a linear scan.
2. Writes the file's data into that cluster.
3. If the file is larger than one cluster, finds the next free cluster, writes the file's data there, and updates the FAT to chain the two clusters.
4. Repeats until the file is fully written, then marks the last cluster's FAT entry as end-of-chain.
5. Writes the directory entry (name, attributes, first cluster, size).

This linear "first-fit" allocation is simple and fast but can fragment files over time as the volume fills and old files are deleted. ESXDOS does not defragment; on a flash medium, fragmentation has no seek-time penalty, so the practical impact is negligible.

## §6. IS-DOS and Alternative Filesystems

### 6.1 IS-DOS: the Russian hierarchical filesystem

**IS-DOS** (Aleksey Dmyrov, 1993) is a hierarchical filesystem and DOS that predates FAT-on-Spectrum by over a decade. It was designed for the Nemo IDE and KAY IDE hardware (§5.2–5.3 of [ide_interface.md](ide_interface.md)) and shipped with its own GUI file manager. IS-DOS is historically important as the **first** attempt to give the Spectrum a PC-like filesystem.

At the directory-entry level, IS-DOS is **MS-DOS-compatible**: it uses 32-byte directory entries with an 8.3 name, attributes, a first-cluster field, and a size field, laid out almost identically to FAT. This was a deliberate design choice to allow file interchange with MS-DOS PCs.

The differences from FAT are:

- **Hierarchical from the start.** IS-DOS has true subdirectories with `.` and `..` entries, like MS-DOS — unlike the floppy-era TR-DOS, which is flat.
- **A different allocation scheme.** IS-DOS does not use the FAT linked-list structure; it uses a per-file cluster bitmap. This is more compact than a FAT for small volumes but does not scale to gigabyte media.
- **A jump-table API.** IS-DOS exposes its functions through a fixed jump table (like the Amiga's `exec` library), rather than the BDOS `CALL 5` convention of CP/M or the hook-code convention of TR-DOS.

The full IS-DOS API, on-disk structure, and history are covered in [is_dos.md](../../04_operating_systems/is_dos.md). For partitioning purposes, the key point is that an IS-DOS volume is **not interchangeable** with a FAT volume: a PC cannot read it, and ESXDOS cannot mount it. IS-DOS volumes exist only on period-correct Nemo IDE and KAY hardware and are now rare.

### 6.2 Why FAT won

FAT displaced IS-DOS for three reasons:

- **PC interchange.** A FAT volume is readable by every PC; an IS-DOS volume is not. The convenience of preparing a card on a modern computer outweighed any technical advantage IS-DOS might have had.
- **Hardware convergence.** When the DivIDE (a Western design) became the standard interface, it shipped with ESXDOS (which speaks FAT), not IS-DOS. The hardware and the DOS standardized together.
- **Scale.** IS-DOS's allocation scheme does not scale to gigabyte media; FAT32 does. As SD cards grew, only FAT could follow.

IS-DOS survives as a historical curiosity, documented for completeness but no longer in active use. Every modern Spectrum mass-storage volume is FAT.

## §7. Multi-Partition Layouts

### 7.1 Why more than one partition

Most Spectrum SD cards have a single FAT partition, but the MBR supports up to four. Two scenarios use multiple partitions:

- **A TR-DOS partition and a FAT partition.** Some DivMMC setups partition the card so that the first partition is a small (~800 KB) TR-DOS volume (mounted as a virtual floppy by `divman` or `divese` — see [divide_divmmc.md §5](divide_divmmc.md)) and the second is the larger FAT volume for ESXDOS. This lets one card serve both as a TR-DOS floppy and an ESXDOS hard disk.
- **A FAT16 and a FAT32 partition.** Some old interfaces (early DivIDE firmware) only read FAT16, which caps at 2 GB. To use a larger card, the user partitions it: a 2 GB FAT16 volume for the DivIDE, and the remainder as FAT32 (ignored by the DivIDE but usable when the card is in a PC).

ESXDOS mounts only the **first FAT partition** it finds in the MBR. Secondary partitions are not auto-mounted. To access a second FAT volume, the user must repartition so that volume is first, or use a DOS extension that walks the whole table.

### 7.2 The extended partition chain

For more than four partitions, the MBR uses an **extended partition** (type `0x05` or `0x0F`) that points at a linked list of **extended boot records (EBRs)**, each holding one logical partition and a pointer to the next EBR. This is the same scheme a PC uses.

ESXDOS does **not** walk the extended partition chain. Only the four primary entries in the MBR are examined. A card with logical partitions in an extended partition will appear empty to ESXDOS unless at least one of the four primary entries is FAT. In practice this rarely matters — Spectrum cards are small enough that four primary partitions are plenty.

### 7.3 Alignment and the 1 MB offset

Modern formatters start the first partition at LBA 2048 (1 MB into the card). This is not an accident — it aligns the partition start to a 4 KB boundary, which matches the erase-block size of modern SD cards and SSDs. Misaligned partitions cause **write amplification**: every write to a 4 KB logical block forces the card to erase and rewrite two 4 KB physical blocks, halving the card's lifespan.

ESXDOS does not require alignment, but a card formatted on a modern OS will be aligned by default. A card formatted on the Spectrum itself (via `*format` or a DivMMC formatter) may not be aligned — these tools usually start the partition at LBA 1 or 2, saving a megabyte but writing misaligned. For flash media, prefer to format on a PC.

## §8. Cross-references and License

### 8.1 Within this sub-section

| Article | Covers |
|---|---|
| [hdd_overview.md](hdd_overview.md) | The top-level overview; where partitioning sits in the storage story |
| [ide_interface.md](ide_interface.md) | The IDE protocol that delivers sectors to the partition layer |
| [sd_interface.md](sd_interface.md) | The SD-SPI protocol that delivers sectors to the partition layer |
| [divide_divmmc.md](divide_divmmc.md) | The DivIDE/DivMMC hardware and the card-formatting workflow |
| [hdf_mgt_formats.md](hdf_mgt_formats.md) | The image formats that capture the partitioned volume in a file |

### 8.2 Related articles elsewhere

| Article | Relationship |
|---|---|
| [esxdos.md](../../04_operating_systems/esxdos.md) | The DOS that reads the FAT volumes this article describes |
| [is_dos.md](../../04_operating_systems/is_dos.md) | The Russian alternative filesystem covered in §6 |
| [nextzxos.md](../../04_operating_systems/nextzxos.md) | The Next's DOS, which uses the same FAT structure as ESXDOS |
| [beta_disk_interface.md](beta_disk_interface.md) / [trd_disk_format.md](trd_disk_format.md) | The floppy-only predecessors that had no partition table |

### 8.3 External references

- [Microsoft Extensible Firmware Initiative FAT32 File System Specification](https://learn.microsoft.com/en-us/windows/win32/fileio/exfat-specification) — the canonical reference for the FAT16/FAT32 boot sector, FSINFO structure, and directory entry layout used by every DivIDE/DivMMC card.
- [SD Association — SD Simplified Specification](https://www.sdcard.org/downloads/) — the public specification for SD card physical layer, SPI mode command set, and CSR/CSD register layout.
- [ESXDOS documentation](https://github.com/joneiricon/ESXDOS) — the canonical DOS reference for the DivIDE/DivMMC; documents the partition-detection heuristics and FAT mount sequence.
- **`cpmtools` documentation** — Unix manual pages and disk definitions for working with CP/M-style partitions on +3 and ATM Turbo disks.
- **[zx-pk.ru](https://zx-pk.ru)** — Russian Spectrum forum; the origin of IS-DOS partitioning and the discussion venue for Pentagon/Scorpion partition compatibility issues.

### 8.4 License

This article is licensed under [CC BY-SA 4.0](../../README.md). The FAT specification referenced in §3 is published by Microsoft in the Extensible Firmware Initiative FAT File System Specification; the SD card physical layer referenced in §7.3 is published by the SD Association. Both are used here for documentation purposes.
