[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# Hard Disk and SD Image Formats: .HDF, .IMG, .MGT

**Scope:** The **disk-image file formats** that emulator authors use to capture **mass-storage volumes** — the CompactFlash, SD-card, and hard-disk partitions that the DivIDE, DivMMC, ZXMMC, and ZX Spectrum Next read and write. This article covers the **`.HDF`** hard-disk image, the **`.IMG`** raw image, and recaps the **`.MGT`** floppy image (covered in depth in [opus_discovery_format.md](opus_discovery_format.md)) for completeness.

This is the **image-format companion** to the hardware articles [ide_interface.md](ide_interface.md) and [sd_interface.md](sd_interface.md): those cover how the Spectrum talks to a physical device; this covers how a modern computer captures that device's contents in a file.

**Audience:** Emulator authors deciding which image formats to support, archival tool authors building conversion utilities, and retro-hardware users who want to back up their CompactFlash or SD card to a file on a PC.

**Prerequisites:** The [overview article](hdd_overview.md) situates these formats in the storage story; [hdd_partitioning.md](hdd_partitioning.md) covers the MBR and FAT structure that lives inside every image.

**Depth:** Medium. The image formats themselves are simple — most are raw byte-for-byte dumps — so the depth is in explaining when each is used, how emulators mount them, and how they relate to the floppy image formats.

---

## §1. Introduction

### 1.1 Why mass-storage images differ from floppy images

The floppy disk-image formats (`.TRD`, `.SCL`, `.DSK`, `.EDSK`, `.FDI`, `.UDI`, `.SCP`) capture a single floppy disk — at most ~800 KB of data, with a well-known geometry. They are small, simple, and often include metadata (track layout, weak bits, flux transitions) that goes beyond the raw bytes.

A mass-storage image captures something much larger and more structured: a **whole CompactFlash card, SD card, or hard-disk partition**, typically 32 MB to 32 GB, containing a **Master Boot Record, a partition table, one or more FAT volumes, and a directory tree of thousands of files**. The image is not a single file-system snapshot but a **byte-for-byte copy of the storage medium**, including the empty space.

This difference has two consequences. First, mass-storage images are **large**: a 2 GB SD card produces a 2 GB image file, uncompressed. Second, they are **boring**: because the on-medium structure is just FAT (a universally understood filesystem), the image format itself is usually trivial — a raw dump with no header, no metadata, and no per-track structure. The interesting work happens inside the image, where the FAT and partition layers live, and that is covered in [hdd_partitioning.md](hdd_partitioning.md).

### 1.2 The four names for the same thing

The Spectrum community uses four file extensions for mass-storage images, almost interchangeably:

| Extension | Typical origin | Content |
|---|---|---|
| `.HDF` | SpecEmu, Zero, EightyOne (hard-disk emulation) | Raw bytes, optionally with a small header |
| `.IMG` | Fuse, Spectaculator, generic PC tools | Raw bytes, no header |
| `.VHD` | Spectaculator, modern virtualisation tools | Microsoft VHD format (has a footer) |
| `.RAW` / no extension | `dd`, low-level tools | Raw bytes, no header |

In most cases the file's **content is identical** — a byte-for-byte copy of the storage medium. The extension is a hint to the emulator about what to expect, not a guarantee of a different format. §3 and §4 explain the nuances.

## §2. The Raw Image Concept

### 2.1 What "raw" means

A **raw image** is a file whose bytes are an exact copy of the storage medium's sectors, in order, starting at sector 0. If the medium is a 512 MB CompactFlash card organized into 512-byte sectors, the raw image is a 536,870,912-byte file in which byte offset `N × 512` is the first byte of sector `N`. There is no header, no footer, no metadata, and no compression. The file size equals the medium size.

This is the same concept as a `dd if=/dev/sdX of=image.img` dump on Unix, or a "Read Device to Image File" operation in Win32 Disk Imager. The result is universally readable: any tool that understands FAT can mount the image (usually via a loopback device) and browse its files, because the image's internal structure is exactly what a real medium's structure would be.

### 2.2 The MBR at offset 0

The first 512 bytes of a raw Spectrum mass-storage image are the **Master Boot Record** — the same structure a PC's boot sector uses. It contains:

- Bootstrap code (446 bytes) — on a Spectrum volume this is usually empty or a stub, because the Spectrum does not boot from the MBR the way a PC does.
- The **partition table** (64 bytes, at offset `0x1BE`) — up to four 16-byte partition entries.
- The **signature** `0x55 0xAA` at offset `0x1FE`.

ESXDOS reads this partition table, finds the first FAT partition, and mounts it. The full partition-table layout is documented in [hdd_partitioning.md](hdd_partitioning.md). For image-format purposes, the key point is that **every raw image starts with a valid MBR** — this is how an emulator (or a PC) knows the image contains a filesystem rather than arbitrary data.

### 2.3 Why raw dominates

Raw images dominate mass-storage emulation for three reasons:

1. **Simplicity.** No parser is needed; the emulator just maps LBA offsets in the image to LBA offsets on the (virtual) device. This is a one-line address calculation.
2. **Interchange with real hardware.** A raw image can be written directly back to a CompactFlash or SD card with `dd` or Win32 Disk Imager, and the card will work in a real DivIDE/DivMMC. Conversely, a real card can be dumped to a raw image that an emulator will mount. The image and the physical medium are interchangeable.
3. **Tools already exist.** Every operating system can already mount, read, and write FAT filesystems. An emulator that mounts a raw image as a loopback device gets FAT support "for free" from the host OS.

The cost is **size**: a raw image of an 8 GB SD card is 8 GB, even if the card is mostly empty. §7 covers sparse-file and compression techniques that mitigate this.

## §3. `.HDF` — the Hard-Disk Image Format

### 3.1 The two `.HDF` sub-variants

The `.HDF` extension is used by several ZX Spectrum emulators (notably **SpecEmu**, **Zero**, and **EightyOne**) for hard-disk images. There are two sub-variants in the wild:

- **Raw `.HDF`** — identical in content to a `.IMG` (§4). The file is a byte-for-byte dump of the storage medium, starting with the MBR. This is the most common variant in modern use.
- **Headered `.HDF`** — a small header prepended to the raw data, describing the geometry (cylinders, heads, sectors, sector size). This variant is used by older SpecEmu versions and a few other emulators that needed to know the geometry without assuming it.

The two are distinguished by **file size and magic number**. A raw `.HDF` whose size is an exact multiple of 512 bytes (and whose first two bytes at offset `0x1FE` are `0x55 0xAA`) is almost certainly a raw image. A headered `.HDF` begins with a geometry descriptor that is not a valid MBR.

### 3.2 The headered `.HDF` structure (older SpecEmu)

The headered variant used by older SpecEmu revisions begins with a small structure (the exact layout varies by emulator version) containing:

- A **magic number** identifying the format.
- The **geometry**: cylinder count, head count, sectors-per-track, bytes-per-sector.
- The **total sector count** (cylinders × heads × sectors-per-track).
- Optionally, the **interface type** (DivIDE, ZXCF, etc.).

After the header, the file continues as a raw sector dump. An emulator reading the header learns the geometry; an emulator that does not understand the header can often still read the file by skipping a fixed number of bytes (if it knows the header size) or by treating the file as raw and ignoring the header's geometry hint.

### 3.3 Which variant to use

For new images, **use the raw variant**. It is universally compatible, interchangeable with `.IMG`, and writes directly back to real hardware. The headered variant is a historical artifact of emulators that predated the standardisation on raw images.

If you encounter a headered `.HDF` from an old archive, the conversion tools in §7 can strip the header and produce a raw image. Conversely, if an old emulator requires a headered `.HDF`, the same tools can prepend one — but you are better off upgrading to a modern emulator that accepts raw images.

## §4. `.IMG` — the Generic Raw Image

### 4.1 `.IMG` as the universal default

The `.IMG` extension is the **generic raw image**: a byte-for-byte dump of a storage medium with no header, no footer, and no metadata. It is the format that `dd`, Win32 Disk Imager, balenaEtcher, and every other low-level imaging tool produce by default. A `.IMG` file whose size is 512 MB is a 512 MB dump; an emulator mounts it as a 512 MB virtual device.

For Spectrum mass storage, `.IMG` is the **preferred extension** for new images because it carries no format-specific baggage. Fuse, Spectaculator, ZEsarUX, and CSpect all accept `.IMG` files for DivIDE/DivMMC emulation. A `.IMG` is also directly writable to a real SD card or CompactFlash card, and a real card dumped with `dd` produces a `.IMG` that any emulator will mount.

### 4.2 The relationship to `.HDF`

A raw `.HDF` and a `.IMG` are **the same file with different extensions**. The byte content is identical — both start with the MBR at offset 0 and continue as a flat sector dump. An emulator that accepts one will usually accept the other; the extension is a hint, not a hard requirement. If you have a `.HDF` that an emulator refuses, renaming it to `.IMG` (or vice versa) often works.

The only exception is the **headered `.HDF`** variant (§3.2), which is not a raw image and cannot be renamed to `.IMG` without first stripping the header.

### 4.3 `.IMG` and the loopback mount

The great advantage of `.IMG` is that every modern operating system can **loopback-mount** it as a filesystem. On Linux, `mount -o loop image.img /mnt` exposes the FAT volume; on macOS, `hdiutil attach image.img` does the same; on Windows, tools like OSFMount mount `.IMG` files as drive letters. Once mounted, the image is browsable with a normal file manager, and files can be copied in and out exactly as if the image were a real card.

This makes `.IMG` the natural format for **building a DivIDE/DivMMC card on a PC**: create a FAT-formatted `.IMG` of the desired size, loopback-mount it, copy the `/SYS` directory and software into it, unmount, and point the emulator at the file. The same `.IMG` can then be written to a real SD card for use on real hardware. The workflow is detailed in §7.

## §5. `.MGT` — the Floppy Image (Recap)

The `.MGT` extension denotes a **raw sector dump of an MGT-format floppy disk** — the 800 KB DSDD-10 disks used by the Opus Discovery, the MGT Disciple, the MGT +D, and the SAM Coupé. It is covered in full in [opus_discovery_format.md §5](opus_discovery_format.md).

For mass-storage purposes, `.MGT` is included here only to distinguish it from the hard-disk image formats. The key differences:

- A `.MGT` is a **floppy** image (~800 KB), not a hard-disk image. It has no MBR and no partition table — the FAT-like MGT filesystem starts at sector 0 directly.
- A `.MGT` is geometry-fixed (80 cylinders × 2 heads × 10 sectors × 512 bytes = 819,200 bytes). The reader assumes this geometry; there is no header.
- A `.MGT` is **not** interchangeable with a `.IMG` or `.HDF`, because the latter start with an MBR and the former do not.

The `.MGT` is the floppy counterpart of `.TRD` (TR-DOS) and `.DSK` (+3DOS/CP/M). For the byte-level MGT layout, see [opus_discovery_format.md §5](opus_discovery_format.md).

## §6. Other Variants

### 6.1 `.VHD` — Microsoft Virtual Hard Disk

`.VHD` is the **Microsoft Virtual Hard Disk** format, used by Virtual PC, Hyper-V, and (for Spectrum purposes) by Spectaculator. Unlike a raw image, a `.VHD` has a **footer** at the end of the file describing the disk's geometry and format. The footer lets the format support **sparse/dynamic disks** (where the file is smaller than the nominal disk size), which a raw image cannot.

For Spectrum use, a `.VHD` is usually a **fixed-size** disk — a raw image with a 512-byte footer appended. The footer is documented in the Microsoft VHD Image Format Specification; tools like `qemu-img` convert between `.VHD` and raw `.IMG` losslessly. The advantage of `.VHD` is that Spectaculator understands it natively; the disadvantage is that the footer confuses tools that expect a raw image.

### 6.2 `.VFD`, `.DCK`, `.DSQ` — minor floppy variants

These are floppy-disk image extensions, not hard-disk formats:

- **`.VFD`** (Virtual Floppy Disk) — a generic floppy image format used by some emulators; usually a raw 720 KB or 800 KB dump.
- **`.DCK`** and **`.DSQ`** — Disciple and +D-specific floppy image variants, related to `.MGT` but with interface-specific extensions. See [opus_discovery_format.md §5.4](opus_discovery_format.md). These are floppy-only formats, not used for mass-storage emulation.

### 6.3 Compressed variants: `.HZF`, `.gz`, `.zip`

Some emulators accept **compressed** images: a raw `.IMG` or `.HDF` compressed with gzip (`.img.gz`) or stored inside a `.zip`. The emulator decompresses on the fly. The `.HZF` extension (used by HZX Spectrum emulator) is a gzipped raw image with a magic header. These are conveniences, not distinct formats — the uncompressed content is a standard raw image.

## §7. Creating and Mounting Images

### 7.1 Creating a blank `.IMG` on each OS

| OS | Command | Result |
|---|---|---|
| **Linux** | `truncate -s 512M card.img` then `mkfs.fat -F 16 card.img` | A 512 MB FAT16 image |
| **macOS** | `hdiutil create -size 512m -fs MS-DOS -volname ZX card.img` | A 512 MB FAT image |
| **Windows** | Use `diskpart` or a tool like Minitool Partition Wizard on a `.IMG` mounted by OSFMount | A FAT image of chosen size |

The choice of FAT16 vs FAT32 follows §6.1 of [divide_divmmc.md](divide_divmmc.md): FAT16 for images up to 2 GB, FAT32 for larger. For an emulator-only image, 256–512 MB is ample for a large software library.

### 7.2 Populating the image

Once the `.IMG` exists, loopback-mount it and copy files in:

- **Linux:** `sudo mount -o loop card.img /mnt`, then `cp -r /path/to/software /mnt/`, then `sudo umount /mnt`.
- **macOS:** `hdiutil attach card.img` mounts it (usually at `/Volumes/ZX`), copy files in, `hdiutil detach /dev/diskN`.
- **Windows:** OSFMount assigns a drive letter; copy files via Explorer; detach in OSFMount.

Create the `/SYS` directory and copy the ESXDOS dot commands into it, as described in [divide_divmmc.md §6.3](divide_divmmc.md). Add `/GAMES`, `/TRDOS`, and any other directories with software. Unmount when done.

### 7.3 Using the image in an emulator

Point the emulator at the `.IMG` (or renamed `.HDF`) file. In Fuse, this is the "DivIDE" or "DivMMC" settings panel; in ZEsarUX, the "Storage" menu; in CSpect, a command-line option. The emulator presents the image as the DivIDE/DivMMC's storage device, and ESXDOS boots from it exactly as it would from a real card.

### 7.4 Writing the image to a real card

The same `.IMG` can be written to a physical SD card or CompactFlash card for use on real hardware:

- **Linux:** `sudo dd if=card.img of=/dev/sdX bs=4M` (where `/dev/sdX` is the card device — be very careful to identify the correct device).
- **macOS:** `sudo dd if=card.img of=/dev/rdiskN bs=1m` (where `N` is the disk number from `diskutil list`).
- **Windows:** Win32 Disk Imager or balenaEtcher, selecting the `.IMG` and the card drive.

The card is now a byte-for-byte copy of the image, formatted and populated identically. Insert it into a DivMMC and it works.

### 7.5 Backing up a real card to an image

The reverse operation backs up an existing card: `dd if=/dev/sdX of=card.img bs=4M` on Linux, or the "Read" operation in Win32 Disk Imager on Windows. The resulting `.IMG` is a complete archival copy of the card, including the MBR, partitions, and all files. Store it (compressed with `gzip` or `xz` to save space — a mostly-empty card compresses extremely well) as a backup.

### 7.6 Sparse files and deduplication

A raw image of an 8 GB card is 8 GB on disk, which is wasteful when the card is mostly empty. Two mitigations exist:

- **Sparse files.** On Linux and macOS, `truncate` creates a sparse file that reports 8 GB but consumes only the space actually written. `dd conv=sparse` preserves sparseness. The emulator reads it as a full 8 GB image but the host filesystem stores only the non-zero blocks.
- **Compression.** A gzipped `.IMG` of a mostly-empty card compresses by 90–99%. The trade-off is that the emulator must decompress on the fly (or the user decompresses before mounting). Some emulators (Fuse, ZEsarUX) accept `.img.gz` directly.

For archival, **gzip the `.IMG`**; for active emulator use, use a **sparse file** or a smaller image (256–512 MB is plenty).

## §8. Cross-references and License

### 8.1 Within this sub-section

| Article | Covers |
|---|---|
| [hdd_overview.md](hdd_overview.md) | The top-level overview; where image formats sit in the storage story |
| [ide_interface.md](ide_interface.md) | The IDE protocol that the `.HDF`/`.IMG` captures |
| [sd_interface.md](sd_interface.md) | The SD-SPI protocol that the same images capture |
| [divide_divmmc.md](divide_divmmc.md) | The DivIDE/DivMMC hardware and the card-formatting guide (§6) |
| [hdd_partitioning.md](hdd_partitioning.md) | The MBR and FAT structure that lives inside every image |

### 8.2 Related articles elsewhere

| Article | Relationship |
|---|---|
| [opus_discovery_format.md](opus_discovery_format.md) | The full `.MGT` floppy image format, covered in §5 of that article |
| [esxdos.md](../../04_operating_systems/esxdos.md) | The DOS that reads the FAT volume inside the image |
| [trd_scl_formats.md](trd_scl_formats.md) / [dsk_fdi_formats.md](dsk_fdi_formats.md) | The floppy image formats, for comparison |
| [udi_format.md](udi_format.md) / [scp_format.md](scp_format.md) | The flux-level floppy image formats, which capture far more detail but only for floppies |

### 8.3 External references

- **Microsoft Virtual Hard Disk Image Format Specification** (public, 2006) — the canonical reference for the `.VHD` format cited in §6.1; defines the 512-byte footer structure used by `.HDF` files.
- [ESXDOS `.HDF` documentation](https://github.com/joneiricon/ESXDOS) — community-maintained documentation for the sparse `.HDF` format used by the DivIDE/DivMMC emulator workflows.
- [`samdisk`](https://github.com/samdisk71/samdisk) — modern open-source multi-format disk-image converter; the reference implementation for reading/writing `.IMG`, `.HDF`, `.TRD`, `.DSK` interchangeably.
- [ZX-Blockeditor](https://www.raxoft.de/) — the de facto cross-format disk-image editor; supports direct inspection of `.HDF` and `.IMG` partition tables and FAT structures.
- [`libdsk`](https://www.danceswithferrets.org/gnu/libdsk/) — Unix library for reading non-standard floppy and hard-disk image formats; documents the on-disk layout conventions used by Spectrum emulators.

### 8.4 License

This article is licensed under [CC BY-SA 4.0](../../README.md). The Microsoft VHD format referenced in §6.1 is documented in the public Microsoft VHD Image Format Specification; the SD and FAT specifications referenced throughout are published by the SD Association and Microsoft respectively. All are used here for documentation purposes.
