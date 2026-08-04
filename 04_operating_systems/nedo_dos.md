[← Home](../README.md) · [Operating Systems](README.md)

# NedoDOS — Modern DOS for the ZX Evolution

The Western Spectrum scene has **ESXDOS** (for DivIDE/DivMMC hardware) and **NextZXOS** (for the ZX Spectrum Next). The Russian scene has its own modern DOS: **NedoDOS**, the disk operating system designed for the **ZX Evolution** FPGA-based clone and the broader NedoPC ecosystem. NedoDOS brings modern FAT16/FAT32 filesystem support, long filenames, SD/IDE hardware compatibility, and a clean assembly API to the Russian Spectrum world.

NedoDOS occupies a similar niche in the Russian scene to what ESXDOS occupies in the Western scene: it is the modern alternative to the classic DOSes (TR-DOS, IS-DOS), designed to work with current-generation mass storage (SD cards, CompactFlash, IDE hard disks) rather than the 5.25" floppies of the 1980s. But unlike ESXDOS, NedoDOS was designed from the start for Russian clone hardware — its conventions, defaults, and integrations assume a Pentagon-like or ZX Evolution-like machine.

This article covers NedoDOS as a system: its place in the NedoPC ecosystem, its hardware support, its filesystem, its BASIC integration, its assembly API, and its modern status. For ESXDOS — the Western equivalent — see [esxdos.md](esxdos.md). For the ZX Evolution hardware itself — NedoDOS's primary platform — see [evo_os.md](evo_os.md).

---

## Roadmap

1. **What NedoDOS is** — history, scope, the NedoPC connection
2. **The NedoPC ecosystem** — context: ZX Evolution, NedoPC boards, modern Russian clones
3. **Hardware support** — SD, IDE/CF, Beta 128, and other interfaces
4. **The filesystem** — FAT16/FAT32, long filenames, paths
5. **Memory layout** — where NedoDOS lives in the address space
6. **BASIC integration** — NedoDOS keywords
7. **The assembly API** — calling NedoDOS from machine code
8. **Comparison with ESXDOS, TR-DOS, IS-DOS** — what each does well
9. **Modern status** — NedoDOS in 2024, the active community
10. **Cross-references** — where to go next

---

## §1. What NedoDOS Is

### 1.1 Origins

NedoDOS was developed in the late 2000s and early 2010s by the **NedoPC team** — a group of Russian hardware and software developers centered around **Aleksandr (Alex) Zhuravlev** (also known as `tsl` in the Russian Spectrum community) and other contributors. The NedoPC team is best known for designing the **ZX Evolution** — an FPGA-based Spectrum clone that is the most popular modern Russian Spectrum hardware.

The original motivation for NedoDOS was practical: the ZX Evolution ships with a CompactFlash card slot and an SD card slot, and the existing DOSes (TR-DOS, IS-DOS) could not make good use of these. TR-DOS is too primitive (flat filesystem, no long filenames). IS-DOS is essentially abandoned. The team needed a modern DOS that could:

- Read and write FAT16/FAT32 partitions on CompactFlash and SD cards.
- Support long filenames for compatibility with PC-side file management.
- Provide a clean assembly API for new software.
- Maintain backward compatibility with classic TR-DOS software where possible.

NedoDOS was the answer. It was designed from scratch to be the "modern DOS" for the Russian Spectrum world, in the same way that ESXDOS is the modern DOS for the Western world.

### 1.2 Scope

NedoDOS is a **disk operating system** in the modern sense: it provides:

- A **file system driver** for FAT16 and FAT32 partitions.
- **Hardware drivers** for SD cards, CompactFlash (via IDE), and traditional Beta 128 floppy interfaces.
- A **BASIC extension** that adds disk commands to the host machine's BASIC.
- An **assembly API** for machine-code programs.
- **Long filename support** for full PC compatibility.

NedoDOS does **not** provide:

- A multi-tasking kernel (it is single-tasking, like all other Spectrum DOSes).
- A command shell (though one exists as a separate utility, the NedoDOS Commander).
- A memory manager (it uses the host machine's banked RAM).
- A network stack (though the ZX Evolution's hardware can support networking via separate software).

### 1.3 Relationship to ESXDOS

NedoDOS and ESXDOS serve similar roles in their respective ecosystems:

| Feature | ESXDOS | NedoDOS |
|---|---|---|
| Target hardware | DivIDE / DivMMC (Western) | ZX Evolution, Pentagon, ATM Turbo (Russian) |
| Filesystem | FAT16/FAT32 | FAT16/FAT32 |
| Long filenames | Yes | Yes |
| API style | Hook codes via `CALL #0084` | Jump table at fixed addresses |
| Dot commands | Yes (8 KB overlays) | Yes (similar mechanism) |
| Software library | Large (Western hobbyist scene) | Smaller (Russian scene) |
| Active development | Yes (continued) | Yes (continued) |

The two systems are conceptually similar but not API-compatible. Software written for ESXDOS does not run under NedoDOS without porting, and vice versa. The choice between them is determined by the hardware: DivIDE/DivMMC users use ESXDOS; ZX Evolution and modern Russian clone users use NedoDOS.

### 1.4 Relationship to TR-DOS

NedoDOS does **not** replace TR-DOS — it coexists with it. A typical ZX Evolution setup has:

- **TR-DOS** for running classic Soviet-era software (which expects the TR-DOS API and flat filesystem).
- **NedoDOS** for modern software and for accessing files on CF/SD cards.

The two are loaded as separate ROM images and switched in as needed. This dual-DOS approach is normal for modern Russian clone hardware.

### 1.5 Why NedoDOS matters

NedoDOS matters for several reasons:

1. **It is the modern DOS for the Russian Spectrum scene.** If you have a ZX Evolution or a modern Pentagon clone, NedoDOS is the recommended DOS for accessing your SD card.
2. **It is technically sophisticated.** FAT32 with long filenames on a Z80 is a non-trivial achievement.
3. **It is actively maintained.** The NedoPC team continues to fix bugs and add features.
4. **It preserves compatibility.** NedoDOS allows classic TR-DOS software to coexist with modern file management.

For Russian Spectrum enthusiasts in 2024, NedoDOS is the standard modern DOS.

---

## §2. The NedoPC Ecosystem

### 2.1 The NedoPC team

**NedoPC** is a loose collective of Russian Spectrum hardware and software developers who have been active since the late 1990s. The team's name is a play on "Nedo" (Russian: "Недо-", meaning "quasi-" or "would-be") and "PC" — a self-deprecating reference to the fact that the Spectrum is not really a PC.

Key figures in the NedoPC team include:

- **Aleksandr Zhuravlev** (`tsl`) — the lead hardware designer of the ZX Evolution.
- **Vladimir Kladov** (`Clover`) — software developer, contributor to NedoDOS.
- **Oleg Nesterov** (`nester`) — software developer.
- Various other contributors from the Russian Spectrum scene.

The NedoPC team operates primarily in Russian, with documentation and software releases in Russian. Some English translations exist for the wider community.

### 2.2 The ZX Evolution

The **ZX Evolution** (sometimes "ZX Evo" or "Evo") is the flagship product of the NedoPC team. It is an FPGA-based Spectrum clone, originally released around 2010, with the following key features:

- **Pentagon 128 / 1024 compatibility** (the standard for Russian Spectrum clones).
- **ATM Turbo compatibility** (another popular Russian clone).
- **512 KB or 1024 KB of RAM** (configurable).
- **CompactFlash slot** (IDE interface).
- **SD card slot** (SPI interface).
- **PS/2 keyboard and mouse ports**.
- **VGA and composite video output**.
- **Built-in Turbo modes** (7 MHz, 14 MHz).
- **FPGA-based hardware** — fully reconfigurable, can be updated to fix bugs or add features.

The ZX Evolution is the most popular modern Russian Spectrum hardware in 2024. It is the primary target for NedoDOS.

For more on the ZX Evolution's hardware, see [evo_os.md](evo_os.md).

### 2.3 Other NedoPC hardware

Beyond the ZX Evolution, the NedoPC team has produced or supported several other hardware platforms:

- **NedoPC boards** — bare PCBs for hobbyists to build their own Spectrum clones.
- **Pentagon-compatible upgrades** — kits to upgrade existing Pentagon clones with modern features (CF slots, SD slots, turbo modes).
- **BaseConf** — the FPGA "base configuration" for the ZX Evolution, which implements the Spectrum hardware and can be updated.

NedoDOS runs on all of these platforms, provided they have the necessary storage hardware (CF or SD slot).

### 2.4 The NedoPC software ecosystem

Beyond NedoDOS, the NedoPC ecosystem includes:

- **BaseConf** — the FPGA hardware configuration for the ZX Evolution.
- **TS-Conf** — an alternative FPGA configuration with extended graphics and memory.
- **NeoGS** — a sound card expansion.
- **GMX** — a memory extension.
- **Various utilities** for disk management, file conversion, and hardware configuration.

NedoDOS is the disk operating system layer in this stack — it sits between the hardware and the user-facing software (BASIC, applications, games).

---
## §3. Hardware Support

NedoDOS supports a range of storage hardware, reflecting the diversity of modern Russian clone configurations.

### 3.1 SD card (SPI)

The primary storage for modern Russian clones is the **SD card via SPI** interface:

- **Standard SD** (up to 2 GB): formatted as FAT16.
- **SDHC** (4 GB to 32 GB): formatted as FAT32.
- **SDXC** (64 GB+): supported in newer NedoDOS versions, formatted as FAT32 (requiring PC-side reformatting from exFAT).

The SPI interface is bit-banged by the NedoDOS driver. Speed is approximately 100–200 KB/s in turbo mode, which is fast enough for most operations.

### 3.2 CompactFlash / IDE

The ZX Evolution has a **CompactFlash slot** connected via an IDE interface. CF cards appear to the host as IDE drives, with the standard ATA protocol:

- **CF Type I and Type II** cards: both supported.
- **Microdrives** (CF-sized micro-hard disks): supported as IDE devices.
- **IDE hard disks** (via adapter): supported.
- **IDE-to-SD adapters**: allow using SD cards via the IDE interface.

The IDE interface is faster than SPI SD — typical speeds are 500–800 KB/s in turbo mode.

### 3.3 Beta 128 floppy interface

NedoDOS includes a **Beta 128-compatible floppy driver** for legacy 5.25" and 3.5" floppy drives. This allows NedoDOS to read traditional TR-DOS-formatted floppies — useful for archiving old software.

The Beta 128 driver supports:

- **5.25" DD** (800 KB) — the classic Soviet format.
- **5.25" HD** (1200 KB).
- **3.5" DD** (720 KB).
- **3.5" HD** (1440 KB).

Floppy access is slow (~30 KB/s) compared to CF/SD, but it works.

### 3.4 Partitioning

For CF and IDE drives larger than 2 GB, NedoDOS supports **multiple partitions**:

- Up to 4 primary partitions per drive.
- Each partition can be FAT16 or FAT32.
- Partitions appear as separate drive letters in NedoDOS (`C:`, `D:`, `E:`, `F:`).

A typical ZX Evolution setup might have:

- Partition 1 (FAT32, 8 GB): the main file store.
- Partition 2 (FAT16, 512 MB): TR-DOS-format software images.
- Partition 3 (FAT32, rest): backup and bulk storage.

### 3.5 Hot-plug support

NedoDOS supports **hot-plugging** SD cards (and to a lesser extent CF cards). The user can remove and reinsert an SD card without rebooting, and NedoDOS will automatically detect the change.

This is useful for transferring files between the Spectrum and a modern PC: insert the SD card in the PC, copy files, eject, insert in the Spectrum, and they appear in NedoDOS.

### 3.6 Write protection

NedoDOS respects the **write-protect tab** on SD cards (when present) and the read-only attribute on individual files. Attempting to write to a protected card or file generates a clear error message.

### 3.7 Performance summary

Typical NedoDOS performance on a ZX Evolution (turbo mode):

| Operation | Speed |
|---|---|
| SD card read | ~150 KB/s |
| SD card write | ~80 KB/s |
| CF card read | ~700 KB/s |
| CF card write | ~400 KB/s |
| Floppy read | ~30 KB/s |
| Floppy write | ~30 KB/s |

These speeds make NedoDOS feel responsive for interactive use. Loading a typical 48 KB game image from CF takes about 70 ms — fast enough that the user perceives it as instant.

---

## §4. The Filesystem

NedoDOS's filesystem is **FAT16 or FAT32 with long filename support** — the standard PC filesystem. This makes file transfer between the Spectrum and a modern PC trivial.

### 4.1 FAT16 vs FAT32

NedoDOS chooses between FAT16 and FAT32 based on partition size:

- **FAT16**: used for partitions up to 2 GB. Simpler data structures, slightly faster access.
- **FAT32**: used for partitions larger than 2 GB. More complex but supports the larger sizes.

For typical use (a 2 GB or 4 GB SD card formatted as a single partition), FAT16 is fine. Users with very large CF cards (8 GB+) use FAT32.

### 4.2 Long filenames (LFN)

NedoDOS fully supports **VFAT long filenames** — the same long-filename extension used by every version of Windows since Windows 95. This means files on a NedoDOS disk can have names like:

- `My Game Snapshot.sna`
- `Demos from 1995.z80`
- `Source Code for Project X.txt`

These names are stored in the FAT as additional directory entries (with the "volume label" attribute), alongside the standard 8.3 short-name entry. This is exactly the way Windows stores long filenames, so files moved between the Spectrum and a PC retain their long names.

Without LFN support, files would be limited to 8.3 names like `MYGAME~1.SNA`. NedoDOS eliminates this limitation.

### 4.3 Directory hierarchy

Like all FAT filesystems, NedoDOS supports an arbitrary hierarchy of subdirectories:

- `/` is the root directory.
- `/GAMES/` is a subdirectory of root.
- `/GAMES/ACTION/` is a sub-subdirectory.
- And so on, up to the FAT limit (typically unlimited in practice).

Paths can be specified with forward or backward slashes:

- `/GAMES/ACTION/INVADERS.SNA`
- `\GAMES\ACTION\INVADERS.SNA`

NedoDOS treats both as equivalent.

### 4.4 Filename character set

FAT filenames (both short and long) support a range of characters. NedoDOS uses the standard FAT character set:

- Letters A–Z (case-insensitive; case is preserved in LFN).
- Digits 0–9.
- Special characters: `_`, `-`, `$`, `!`, `#`, `%`, `&`, `'`, `(`, `)`, `@`, `^`, `~`, `.`.
- Spaces (in LFN only).
- Unicode characters via UTF-16 in LFN (NedoDOS displays Cyrillic characters correctly).

The standard 8.3 short name restricts the character set more tightly (no spaces, restricted punctuation). LFN removes these restrictions.

### 4.5 File attributes

NedoDOS supports the standard FAT file attributes:

- **Read-only**: file cannot be deleted or modified.
- **Hidden**: file is not shown in normal directory listings.
- **System**: file is treated as part of the OS.
- **Archive**: file has been modified since last backup.
- **Directory**: entry is a subdirectory.

These attributes can be set and queried via NedoDOS commands.

### 4.6 File sizes

NedoDOS supports files up to 4 GB (the FAT32 limit). In practice, of course, files are limited by the partition size — but the OS itself handles large files correctly.

### 4.7 Timestamps

NedoDOS reads and writes file timestamps:

- **Creation time and date**.
- **Last modification time and date**.
- **Last access date** (FAT32 only).

The timestamps are stored in the standard FAT format. When a NedoDOS disk is moved to a PC, the timestamps appear correctly in Windows Explorer.

If the host machine has a real-time clock (the ZX Evolution has one), NedoDOS uses it to set timestamps. Otherwise, timestamps may default to a fixed date (often the date of the NedoDOS build).

---

## §5. Memory Layout

NedoDOS, like other Spectrum DOSes, occupies a portion of the address space when active.

### 5.1 The NedoDOS ROM

The NedoDOS ROM is **16 KB** (sometimes 32 KB in newer versions), loaded into the standard DOS ROM slot of the host machine. On the ZX Evolution, this slot is configurable — the user can choose which DOS ROM to load at boot.

When NedoDOS is invoked (e.g., by a `LOAD` command in BASIC), the system:

1. Switches the bottom 16 KB of address space to the NedoDOS ROM.
2. Performs the requested operation.
3. Switches back to the BASIC ROM.

This is the same bank-switching pattern used by TR-DOS, IS-DOS, and other Spectrum DOSes.

### 5.2 Work buffers

NedoDOS uses RAM for various work areas:

- **FAT cache**: 2–4 KB, holds portions of the FAT for fast access.
- **Directory cache**: 2 KB, holds recently-accessed directory blocks.
- **File transfer buffer**: 512 bytes (one sector).
- **Path parser workspace**: 512 bytes.
- **LFN buffer**: 512 bytes, holds long filename data during directory operations.

Total: ~6 KB of work RAM. This is taken from the host machine's banked RAM.

### 5.3 RAM disk

NedoDOS supports a **RAM disk** using the host machine's upper RAM banks. The RAM disk appears as a separate drive (`R:`) and is formatted with the same FAT16 filesystem as a physical disk.

The RAM disk is much faster than any physical disk — file operations complete in milliseconds. The trade-off is volatility: the RAM disk loses its contents when the machine is powered off.

### 5.4 Concurrent DOSes

On a ZX Evolution with both NedoDOS and TR-DOS loaded, the two DOSes can coexist:

- **NedoDOS** is loaded into one DOS ROM slot.
- **TR-DOS** is loaded into another DOS ROM slot.
- The user (or software) selects which DOS is active via port writes.

This allows a single machine to run both modern NedoDOS-aware software and classic TR-DOS software. The cost is that the two cannot be active at the same time — switching between them is a bank-switching operation.

### 5.5 Comparison with ESXDOS memory

| Aspect | ESXDOS | NedoDOS |
|---|---|---|
| ROM size | 8 KB | 16 KB |
| Work RAM | ~4 KB | ~6 KB |
| Resident during normal operation | Yes (overlay) | No (banked in on demand) |
| Concurrent with other DOSes | Yes (via dot commands) | Yes (via separate ROM slot) |

ESXDOS uses an overlay model: it is always resident in the `#2000`–`#3FFF` address range and is invoked via function calls. NedoDOS uses the classic TR-DOS-style banked model: it is banked into the bottom 16 KB only when invoked. The two approaches have different trade-offs, but both work.

---

## §6. BASIC Integration

NedoDOS extends the host machine's BASIC with disk commands similar to TR-DOS and ESXDOS.

### 6.1 The NedoDOS command set

The NedoDOS BASIC extensions include:

| Keyword | Purpose |
|---|---|
| `CAT "path"` | List directory contents (with long filenames) |
| `CD "path"` | Change current directory |
| `MD "name"` | Make (create) a directory |
| `RD "name"` | Remove a directory |
| `LOAD "path"` | Load a BASIC program |
| `SAVE "path"` | Save a BASIC program |
| `LOAD "path" CODE addr, len` | Load machine code |
| `SAVE "path" CODE addr, len` | Save machine code |
| `LOAD "path" DATA var()` | Load an array |
| `SAVE "path" DATA var()` | Save an array |
| `ERASE "path"` | Delete a file |
| `RENAME "old" TO "new"` | Rename a file |
| `ATTRIB "path", attrs` | Set file attributes |
| `COPY "src" TO "dst"` | Copy a file |
| `FORMAT drive, params` | Format a disk partition |
| `VERIFY "path"` | Verify a file |
| `RUN "path"` | Equivalent to LOAD + RUN |
| `MOUNT "dev" TO "dir"` | Mount a partition (advanced) |
| `UMOUNT "dir"` | Unmount a partition |

The command set is a superset of TR-DOS's commands, with the addition of directory management (`CD`, `MD`, `RD`) and modern file operations (`MOUNT`, `UMOUNT`).

### 6.2 Path interpretation

NedoDOS paths follow standard FAT conventions:

- `LOAD "/GAMES/MYGAME.SNA"` — absolute path from the root.
- `LOAD "MYGAME.SNA"` — relative to the current directory.
- `LOAD "../SIBLING/FILE.BIN"` — relative path with parent traversal.
- `LOAD "C:/GAMES/MYGAME.SNA"` — explicitly on drive `C:`.
- `LOAD "R:TEMPFILE"` — on the RAM disk.

The drive prefix is optional. When omitted, NedoDOS uses the current default drive.

### 6.3 Long filenames in BASIC

Long filenames can be used directly in BASIC commands:

```basic
10 LOAD "/Games/My Game Snapshot.sna"
20 SAVE "/Saves/My Progress.z80"
30 CAT "/Demos from 1995"
```

The BASIC interpreter handles the long filenames transparently. The only restriction is that the entire command must fit within the BASIC line length limit (typically 128 characters on the host machine).

### 6.4 Wildcards

NedoDOS supports `?` and `*` wildcards in CAT and ERASE:

- `CAT "*.SNA"` — list all `.SNA` snapshot files in the current directory.
- `CAT "/GAMES/A*"` — list all files starting with `A` in `/GAMES`.
- `ERASE "*.TMP"` — delete all `.TMP` files in the current directory.

Wildcards work the same way as in MS-DOS or Windows.

### 6.5 The NedoDOS Commander

For interactive use, NedoDOS provides a **Norton Commander-style file manager** called the **NedoDOS Commander**. This is a separate program (not a BASIC extension) that provides a two-pane file browser:

- Left pane: source directory.
- Right pane: destination directory.
- Function keys for copy, move, delete, etc.
- Long filename display.
- Mouse support (on hardware with a mouse).

The NedoDOS Commander is the standard way to manage files on a ZX Evolution. It is invoked by typing its name at the BASIC prompt:

```basic
LOAD "C:/UTILS/NDC" CODE
RANDOMIZE USR 32768
```

Or by pressing a hotkey if the user has configured one.

---

## §7. The Assembly API

For machine-code programs, NedoDOS exposes a clean assembly API via a jump table.

### 7.1 The NedoDOS jump table

NedoDOS provides a jump table at a fixed address (typically `#5C00` or another documented location). Each entry is a 3-byte `JP` instruction to the corresponding routine.

A representative subset of the API:

| Offset | Routine | Purpose |
|---|---|---|
| `#00` | `INIT` | Initialise NedoDOS |
| `#03` | `OPEN_FILE` | Open a file (returns handle) |
| `#06` | `CLOSE_FILE` | Close an open file |
| `#09` | `READ_FILE` | Read bytes from an open file |
| `#0C` | `WRITE_FILE` | Write bytes to an open file |
| `#0F` | `SEEK_FILE` | Seek to a position |
| `#12` | `DELETE_FILE` | Delete a file |
| `#15` | `RENAME_FILE` | Rename a file |
| `#18` | `MAKE_DIR` | Create a directory |
| `#1B` | `CHANGE_DIR` | Change current directory |
| `#1E` | `FIND_FIRST` | Start a wildcard search |
| `#21` | `FIND_NEXT` | Continue a wildcard search |
| `#24` | `GET_FILE_INFO` | Get file size, attributes, timestamps |
| `#27` | `SET_FILE_INFO` | Set file attributes, timestamps |
| `#2A` | `OPEN_DIR` | Open a directory for listing |
| `#2D` | `READ_DIR` | Read next directory entry |
| `#30` | `CLOSE_DIR` | Close a directory |
| `#33` | `MOUNT` | Mount a partition |
| `#36` | `UMOUNT` | Unmount a partition |
| `#39` | `GET_FREE_SPACE` | Get free space on a drive |
| `#3C` | `GET_CWD` | Get the current working directory path |

The full API is documented in the NedoDOS programmer's reference.

### 7.2 Calling NedoDOS routines

A typical call pattern:

```z80
; Open a file for reading
n_open:
        DI                          ; disable interrupts
        LD   BC,#XXXX               ; NedoDOS ROM select port
        LD   A,#01                  ; select NedoDOS ROM
        OUT  (C),A
        
        LD   HL,filename            ; HL -> path string
        LD   A,#00                  ; mode: read
        CALL #5C03                  ; call OPEN_FILE
        
        ; Returns: carry clear = success, A = handle
        ;         carry set = error, A = error code
        
        LD   BC,#XXXX
        LD   A,#00                  ; back to BASIC ROM
        OUT  (C),A
        EI
        RET
```

The DI/EI pair prevents interrupt handlers from executing with the wrong ROM banked in.

### 7.3 Error codes

NedoDOS uses error codes compatible with MS-DOS:

| Code | Meaning |
|---|---|
| 0 | No error |
| 1 | Invalid function |
| 2 | File not found |
| 3 | Path not found |
| 4 | Too many open files |
| 5 | Access denied |
| 6 | Invalid handle |
| 7 | Disk full |
| 8 | Write protect |
| 9 | Drive not ready |
| 10 | I/O error |
| 11 | Invalid format |

These match IS-DOS and MS-DOS conventions, making NedoDOS easy to learn for programmers familiar with either.

### 7.4 Concurrency and re-entrancy

NedoDOS routines are not re-entrant. A program that calls a NedoDOS routine must wait for it to complete before calling another. This is rarely a problem in practice — single-tasking BASIC programs and machine-code utilities do not need concurrency.

The NedoDOS ROM itself can be called from interrupt handlers, but this is delicate and not recommended for casual use.

---

## §8. Comparison with ESXDOS, TR-DOS, IS-DOS

| Feature | TR-DOS | IS-DOS | ESXDOS | NedoDOS |
|---|---|---|---|---|
| Origin | Soviet (1980s) | Russian (1990s) | Western (2008+) | Russian (2010s) |
| Target hardware | Beta 128 | Iskra | DivIDE/DivMMC | ZX Evolution |
| Filesystem | Custom flat | Hierarchical | FAT16/32 | FAT16/32 |
| Long filenames | No | No | Yes | Yes |
| Max file size | Disk-limited | Disk-limited | 4 GB | 4 GB |
| API style | Hook codes | Jump table | Hook codes | Jump table |
| Resident model | Banked | Banked | Overlay | Banked |
| Active development | Inactive | Inactive | Active | Active |
| Software library | Massive (Soviet) | Small | Large (Western) | Medium (Russian) |

NedoDOS is conceptually closest to ESXDOS: both are modern FAT16/32 DOSes for modern Spectrum hardware. The choice between them is determined by the hardware (DivIDE/DivMMC vs. ZX Evolution).

---

## §9. Modern Status (2024)

NedoDOS is **actively developed** in 2024 by the NedoPC team and contributors.

### 9.1 Where to get NedoDOS

- **NedoPC website**: `nedopc.com` — the official source for NedoDOS binaries and source code.
- **ZX Evolution community forums**: Russian-language discussions and updates.
- **GitHub mirrors**: some community-maintained mirrors exist.
- **Emulator distributions**: UnrealSpeccy and ZEsarUX include NedoDOS for testing.

To install NedoDOS on a ZX Evolution:

1. Download the latest NedoDOS ROM image from the NedoPC website.
2. Copy it to the SD card.
3. Use the ZX Evolution's boot menu to load the NedoDOS ROM into the DOS ROM slot.
4. Reboot — NedoDOS is now active.

### 9.2 Recent development

Active areas of NedoDOS development in 2024:

- **SDXC support**: cards larger than 32 GB.
- **Performance improvements**: faster SPI and IDE drivers.
- **Bug fixes**: continued maintenance of the FAT filesystem code.
- **New hardware support**: compatibility with new Russian clone boards.

The current stable version (mid-2024) is well-tested. Development snapshots are usually usable.

### 9.3 Community

The NedoDOS community is centered on Russian-language forums and the NedoPC team's IRC/Discord channels. English-language support is limited but available via the wider Spectrum community.

For Russian Spectrum enthusiasts, NedoDOS is the standard modern DOS in 2024. It is what TR-DOS was in the 1990s: the default way to manage files on a Spectrum.

### 9.4 Limitations

NedoDOS's main limitations:

- **Hardware-specific**: requires ZX Evolution or compatible hardware. Does not run on Western Spectrums.
- **Russian documentation**: most documentation is in Russian; English translations lag behind.
- **Software library**: smaller than TR-DOS or ESXDOS libraries.
- **No networking**: NedoDOS does not provide TCP/IP; that requires separate software.

For users of ZX Evolution hardware, these limitations are minor. For users of other hardware, ESXDOS or TR-DOS may be more appropriate.

---

## §10. Cross-References

- **[evo_os.md](evo_os.md)** — The ZX Evolution BIOS/OS, the platform NedoDOS was designed for. Covers the hardware, the BaseConf FPGA configuration, and the boot process.
- **[esxdos.md](esxdos.md)** — The Western equivalent. ESXDOS serves the same role for DivIDE/DivMMC hardware that NedoDOS serves for ZX Evolution.
- **[trdos.md](trdos.md)** — The classic Russian DOS. NedoDOS coexists with TR-DOS on modern Russian hardware.
- **[is_dos.md](is_dos.md)** — The earlier Russian attempt at a hierarchical DOS. NedoDOS addresses many of the same problems that IS-DOS tried to solve.
- **[nextzxos.md](nextzxos.md)** — The ZX Spectrum Next's OS, the Western equivalent of NedoDOS + evo_os combined.
- **[../02_hardware/clones/README.md](../02_hardware/clones/README.md)** — Russian clone hardware reference, including the ZX Evolution.
- **[../05_development/03_memory_and_io/memory_and_io_pentagon.md](../05_development/03_memory_and_io/memory_and_io_pentagon.md)** — The Pentagon's memory model, which NedoDOS uses.

---

## References

### External references

- **NedoDOS documentation** (`nedopc.com`, Russian and English) — the canonical reference for NedoDOS as shipped with the Sprinter computer and the NedoPC team's later projects; covers the API, the dot-command system, and the FAT16 implementation.
- **Sprinter 2000 documentation** (`sprinter.com`, archived) — the Sprinter's hardware reference; documents the ISA bus and PC-style peripheral layout that NedoDOS was designed to drive.
- [zx-pk.ru / `nedopc.com` forum threads](https://zx-pk.ru) — primary discussion venue for NedoDOS extensions, the Z-Controller's FAT implementation, and the modern cross-platform ports of NedoDOS to DivIDE-class hardware.
- [ESXDOS documentation](https://github.com/joneiricon/ESXDOS) — for direct comparison; NedoDOS and ESXDOS target similar use cases (hierarchical filesystem on Z80-class hardware) but evolved independently.
- **`cpmtools` documentation** — Unix reference for working with the CP/M-style directory entries that influenced both NedoDOS and +3 DOS.

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same license.
