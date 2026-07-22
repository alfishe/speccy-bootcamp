[← Home](../README.md) · [Operating Systems](README.md)

# IS-DOS — The Russian Hierarchical File System

The Soviet and post-Soviet Spectrum scene is dominated by **TR-DOS** — the flat filesystem that shipped with the Pentagon and Beta 128 interface. But TR-DOS was not the only disk OS produced in this ecosystem. **IS-DOS** (sometimes written "Iskra-DOS" or "IS-DOS") was developed in the early 1990s as a more sophisticated alternative: a **hierarchical filesystem** with subdirectories, file attributes, and a more programmer-friendly API.

IS-DOS never overthrew TR-DOS — the network effects of the established TR-DOS library were too strong — but it gained a small, dedicated user base among power users who wanted the same kind of hierarchical filesystem they saw on MS-DOS machines. IS-DOS software is rare today, but the system itself is historically important as the most advanced native Russian Spectrum DOS ever produced.

This article covers IS-DOS as a system: its origins, its hierarchical filesystem, how it integrates with BASIC, the assembly API, the hardware it runs on, and its modern status. For TR-DOS — the dominant Russian DOS — see [trdos.md](trdos.md). For ESXDOS — the modern Western alternative with similar hierarchical features — see [esxdos.md](esxdos.md).

---

## Roadmap

1. **What IS-DOS is** — history, scope, relationship to TR-DOS
2. **Why IS-DOS was created** — the limits of TR-DOS, the demand for hierarchy
3. **The hierarchical filesystem** — directories, paths, attributes
4. **Memory layout** — where IS-DOS lives in the Spectrum address space
5. **The BASIC command set** — IS-DOS keywords
6. **The assembly API** — calling IS-DOS routines from machine code
7. **Hardware requirements** — what runs IS-DOS
8. **Software library** — what was written for IS-DOS
9. **Modern status** — what survives in 2024
10. **Cross-references** — where to go next

---

## §1. What IS-DOS Is

### 1.1 Origins

IS-DOS was developed in the early 1990s — most sources date the first public version to 1992 or 1993 — by Russian Spectrum enthusiasts. The exact authorship is somewhat murky (Russian software of this era was often distributed informally, without clear attribution), but the system is associated with the **Iskra** ("Spark") brand of Spectrum clones produced in the former Soviet Union.

The name **IS-DOS** is variously explained as:

- **Iskra DOS** — after the Iskra clone hardware it was originally targeted at.
- **Information System DOS** — a backronym suggested by later users.
- **Intelligent System DOS** — another backronym.

The most likely origin is the first: IS-DOS was the disk operating system shipped with Iskra-brand Spectrums, and the name was later generalised to refer to the OS itself regardless of hardware.

### 1.2 Scope

IS-DOS is a **disk operating system** in the classic sense: it provides routines for reading and writing files on a floppy disk (or hard disk partition). It does **not** provide:

- A multi-tasking kernel (it is single-tasking, like TR-DOS).
- A command shell (it is invoked from BASIC or directly from machine code).
- A memory manager (it uses whatever RAM the host machine provides).
- A graphical user interface.

What IS-DOS provides is a **file system** and a set of **file manipulation primitives** — comparable to the file system layer of MS-DOS or the BDOS of CP/M, but with hierarchical directories.

### 1.3 Relationship to TR-DOS

TR-DOS and IS-DOS serve the same broad purpose — they let Spectrum software read and write files on disk — but they take very different approaches:

| Feature | TR-DOS | IS-DOS |
|---|---|---|
| Filesystem | Flat (single directory) | Hierarchical (subdirectories) |
| Max files per disk | 128 | Unlimited (within disk space) |
| Filename format | 8 chars + 1 char extension | 8 chars + 3 chars extension (MS-DOS-like) |
| File attributes | None | Read-only, hidden, system, archive |
| Directory listing | Linear scan of 128 slots | Tree traversal |
| Path support | None | Full paths like `/GAMES/ACTION/MYGAME` |
| Subdirectories | None | Up to 32 levels deep |
| Software support | Massive (entire Soviet scene) | Small (specific IS-DOS software only) |

IS-DOS is technically more advanced than TR-DOS in every respect. Its limitation is **software support** — most Soviet software was written for TR-DOS and will not run on IS-DOS without conversion.

### 1.4 Why IS-DOS matters

IS-DOS is important for several reasons:

1. **Historical significance.** It shows that the Russian Spectrum scene was not monolithic — there were attempts to evolve beyond the TR-DOS standard.
2. **Technical interest.** The hierarchical filesystem is well-designed and worth studying as an example of small-system file system design.
3. **Nostalgia.** For Russian Spectrum users who used IS-DOS in the 1990s, the system has historical importance.
4. **Modern emulation.** Emulators like UnrealSpeccy and ZEsarUX support IS-DOS disks, so the system is preserved.

IS-DOS is **not** a practical alternative to TR-DOS for running classic Soviet software in 2024. It is a research and nostalgia platform.

---

## §2. Why IS-DOS Was Created

### 2.1 The limits of TR-DOS

By 1990, TR-DOS was the established standard for Spectrum disks in the Soviet Union. But TR-DOS had several limitations that frustrated power users:

- **Flat filesystem**. Every file on a disk lived in a single directory. With 128 file slots per disk, organising a substantial software collection meant manually tracking which files were where.
- **No subdirectories**. You could not have `/GAMES/ACTION/` separate from `/GAMES/STRATEGY/`. Everything was in one big pile.
- **Filename limits**. 8 characters for the name, 1 character for the extension — much shorter than the MS-DOS standard of 8+3. Russian developers wanting to share files with the MS-DOS world had to abbreviate filenames.
- **No file attributes**. There was no way to mark a file as read-only, hidden, or system. Accidental overwrites were common.
- **Poor performance on large disks**. TR-DOS's directory scanning was linear; on a disk with many files, finding a specific file could take noticeable time.

These limitations were not critical for game loading (the primary use case), but they were serious obstacles for "serious" use — word processing, source code management, business applications.

### 2.2 The demand for a hierarchical filesystem

In the late 1980s and early 1990s, MS-DOS became widely available in the Soviet Union on PC clones. MS-DOS users were accustomed to:

- Hierarchical directories (subdirectories).
- 8+3 filenames.
- File attributes (read-only, hidden, system, archive).
- Paths (`C:\GAMES\ACTION\MYGAME.EXE`).

Russian Spectrum users who also used MS-DOS wanted the same convenience on their Spectrums. IS-DOS was the response.

### 2.3 The Iskra clone hardware

The **Iskra** brand of Spectrum clones was produced in the early 1990s by various factories in the former Soviet Union. The Iskra 48K and Iskra 128K clones were based on the standard Sinclair design but with some hardware enhancements:

- A built-in disk interface (Beta 128-compatible).
- A built-in parallel port.
- Higher-quality keyboards than the Pentagon.
- Often, support for hard disk partitions (in addition to floppy).

IS-DOS was designed to take advantage of these enhancements. It ran on the Iskra clones natively and could be ported to other Russian clones (Pentagon, Scorpion) with varying degrees of effort.

### 2.4 Why IS-DOS did not dominate

Despite being technically superior to TR-DOS, IS-DOS did not replace it. The reasons:

1. **Network effects.** TR-DOS had a massive software library. Users had TR-DOS disks; software was distributed on TR-DOS disks. Switching to IS-DOS meant abandoning this library.
2. **Compatibility.** TR-DOS software did not run on IS-DOS. Conversion utilities existed but were imperfect.
3. **Hardware fragmentation.** IS-DOS was originally Iskra-specific. Running it on a Pentagon required patches, and on a Scorpion required different patches. TR-DOS worked the same everywhere.
4. **Late arrival.** By the time IS-DOS was widely available (1993+), the Russian Spectrum scene had largely standardised on TR-DOS.
5. **The shift to PCs.** By the mid-1990s, the Russian market was shifting from Spectrums to inexpensive PC clones (running MS-DOS, then Windows). The "serious computing" market that IS-DOS targeted was moving away from the Spectrum entirely.

The result: IS-DOS gained a small user base among power users but never approached TR-DOS's market share.

---
## §3. The Hierarchical Filesystem

IS-DOS's defining feature is its **hierarchical filesystem**. Where TR-DOS has a single flat directory of 128 file slots, IS-DOS has a tree structure with directories, subdirectories, and full path support.

### 3.1 Disk organisation

An IS-DOS disk is divided into:

- **Boot sector** (sector 0): contains the boot code and disk identification.
- **File allocation table** (FAT): a bitmap showing which disk blocks are in use. IS-DOS uses a custom FAT format inspired by MS-DOS's FAT but simplified for the smaller disk sizes.
- **Root directory**: a fixed-size directory at a known location, holding entries for files and subdirectories directly under `/`.
- **Data area**: the bulk of the disk, containing file data and subdirectory data.

The exact geometry depends on the disk format:

| Disk format | Capacity | Sectors | Tracks | Heads |
|---|---|---|---|---|
| 5.25" DD | 800 KB | 10 | 80 | 2 |
| 5.25" HD | 1200 KB | 15 | 80 | 2 |
| 3.5" DD | 720 KB | 9 | 80 | 2 |
| 3.5" HD | 1440 KB | 18 | 80 | 2 |

IS-DOS supports all four formats, depending on the disk hardware. The 5.25" DD 800 KB format was the most common in the early 1990s; 3.5" formats became standard later.

### 3.2 Directory entries

Each file or subdirectory is represented by a **directory entry** of 32 bytes (the same size as MS-DOS's directory entries, for compatibility):

| Offset | Size | Content |
|---|---|---|
| 0 | 8 | Filename, space-padded |
| 8 | 3 | Extension, space-padded |
| 11 | 1 | Attributes (read-only, hidden, system, archive, directory) |
| 12 | 2 | Reserved |
| 14 | 2 | Last modification time |
| 16 | 2 | Last modification date |
| 18 | 2 | First data block (FAT chain head) |
| 20 | 4 | File size in bytes |
| 24 | 8 | Reserved / extension data |

This format is **byte-compatible with MS-DOS directory entries**, which made IS-DOS-to-MS-DOS file transfer straightforward. A file's name, attributes, and timestamps could be transferred between systems without conversion.

### 3.3 Filenames

IS-DOS filenames follow MS-DOS conventions:

- 1–8 characters for the name.
- 0–3 characters for the extension (after a dot).
- Case-insensitive (typically displayed in uppercase, like MS-DOS).
- Allowed characters: letters A–Z, digits 0–9, and the special characters `_`, `-`, `$`, `!`, `#`, `%`, `&`, `'`, `(`, `)`, `{`, `}`, `@`, `^`, `~`.

Examples of valid IS-DOS filenames:

- `MYPROG.BAS`
- `LEVEL01.SPR`
- `DATA`
- `README.TXT`

Examples of invalid filenames:

- `MYPROG.BASIC` (extension too long)
- `VERYLONGFILENAME.BAS` (name too long)
- `MY FILE.BAS` (space not allowed)

This is the same naming convention as MS-DOS, allowing Russian IS-DOS users to share files with PC users without renaming.

### 3.4 Paths

IS-DOS supports **full path specifications**, separated by forward slashes (Unix-like) or backslashes (MS-DOS-like):

- `/GAMES/ACTION/MYGAME` — absolute path from the root
- `MYFILE.TXT` — relative to the current directory
- `../SIBLING/FILE` — relative path with parent traversal
- `SUBDIR/` — refers to a subdirectory

The current directory is tracked by IS-DOS and persists across program invocations. This is similar to MS-DOS's `cd` command.

### 3.5 Attributes

Each file has an **attribute byte** with bit flags:

| Bit | Name | Meaning |
|---|---|---|
| 0 | Read-only | File cannot be deleted or modified |
| 1 | Hidden | File is not shown in normal directory listings |
| 2 | System | File is part of the operating system (e.g., boot code) |
| 3 | Volume label | This entry is a disk volume label, not a file |
| 4 | Directory | This entry is a subdirectory, not a file |
| 5 | Archive | File has been modified since last backup |

These are the same attribute bits as MS-DOS. Setting a file as read-only prevents accidental modification; marking a file as hidden hides it from casual directory listings.

### 3.6 Subdirectories

A subdirectory is a special file containing directory entries. The root directory is at a fixed location; subdirectories are stored in the data area like files, with their content being a sequence of 32-byte directory entries.

When IS-DOS creates a subdirectory:

1. It allocates a data block for the new directory.
2. It writes two special entries to the new directory: `.` (referring to the new directory itself) and `..` (referring to the parent).
3. It updates the parent directory with a directory entry pointing to the new subdirectory.

This is **exactly the MS-DOS subdirectory model**, and IS-DOS subdirectories can be read by MS-DOS tools (and vice versa) without conversion.

### 3.7 Performance

Hierarchical filesystems are inherently slower than flat ones for directory operations, because finding a file requires traversing a path (potentially reading multiple directory blocks). However, IS-DOS includes several optimisations:

- **Directory caching**. The most recently accessed directories are kept in RAM, reducing disk reads.
- **Hash-based file lookup**. Within a directory, files are looked up by hash rather than linear scan, speeding up the common case.
- **Lazy allocation**. New files' directory entries are not written to disk until necessary, reducing write traffic.

These optimisations make IS-DOS's directory operations reasonably fast — not as fast as TR-DOS's flat lookup, but acceptable for typical use.

---

## §4. Memory Layout

IS-DOS, like TR-DOS, occupies a portion of the Spectrum's address space when it is active. The exact layout depends on the host machine.

### 4.1 The standard IS-DOS memory map

On a typical Russian clone (Pentagon 128 or similar) running IS-DOS:

| Address range | Content |
|---|---|
| `#0000`–`#3FFF` | BASIC ROM (Sinclair 48K) or IS-DOS ROM, depending on context |
| `#4000`–`#7FFF` | Screen memory and system variables |
| `#8000`–`#BFFF` | User program area / IS-DOS work area |
| `#C000`–`#FFFF` | Banked RAM: IS-DOS buffers, file system metadata |

When IS-DOS is invoked (e.g., by a `LOAD` command in BASIC), the system:

1. Switches the bottom 16 KB to the IS-DOS ROM.
2. Performs the disk operation.
3. Switches back to the BASIC ROM.

This is similar to how TR-DOS operates. The user program is preserved across IS-DOS calls, but the IS-DOS ROM temporarily overlays the BASIC ROM.

### 4.2 IS-DOS ROM size

The IS-DOS ROM is **16 KB**, fitting in the same address space as TR-DOS. It contains:

- Disk driver (for the Beta 128-compatible FDC).
- File system code (FAT, directory, file management).
- The BASIC extension hooks.
- The assembly API entry points.

The IS-DOS ROM is typically loaded into the same ROM slot that TR-DOS would occupy, and is selected via the same port writes. A Spectrum clone running IS-DOS has IS-DOS in the "TR-DOS slot" instead of TR-DOS — they cannot both be resident at the same time.

### 4.3 Work buffers and caches

IS-DOS uses RAM for various work areas:

- **Directory cache**: ~2 KB, holds recently-accessed directory blocks.
- **FAT cache**: ~1 KB, holds portions of the FAT.
- **File transfer buffer**: ~512 bytes (one sector).
- **Path parser workspace**: ~256 bytes.

Total: ~4 KB of RAM. This is more than TR-DOS uses (TR-DOS uses essentially zero extra RAM, since it does not cache anything), but is small enough to fit comfortably in a 128 KB machine without conflicting with user programs.

### 4.4 RAM disk support

IS-DOS supports a **RAM disk** (similar to the +3's `M:` and `N:` drives) using the upper RAM banks of a 128 KB Spectrum. The IS-DOS RAM disk:

- Is formatted with the same hierarchical filesystem as a physical disk.
- Appears as drive `R:` (or `M:`, depending on configuration).
- Is much faster than a physical disk.
- Is volatile — contents are lost when the machine is powered off.

Users can copy frequently-accessed files to the RAM disk for fast access during a session.

### 4.5 Comparison with TR-DOS memory usage

| Aspect | TR-DOS | IS-DOS |
|---|---|---|
| ROM size | 16 KB | 16 KB |
| Work RAM | ~0 KB | ~4 KB (caches) |
| Bank switching | Switches bottom 16 KB to TR-DOS ROM | Same |
| Resident during normal operation | No (only when invoked) | No (only when invoked) |

The memory overhead of IS-DOS is small enough to be invisible to most users. The cost is the additional ~4 KB of work RAM, which is taken from the banked upper RAM of the host machine.

---

## §5. The BASIC Command Set

IS-DOS extends BASIC with disk commands similar to MS-DOS. The commands are activated by the IS-DOS ROM when it is banked into the bottom 16 KB.

### 5.1 Disk-related BASIC keywords

The IS-DOS BASIC extensions include:

| Keyword | Purpose |
|---|---|
| `CAT "path"` | List directory contents |
| `CD "path"` | Change current directory |
| `MD "name"` | Make (create) a directory |
| `RD "name"` | Remove a directory |
| `LOAD "path"` | Load a BASIC program from disk |
| `SAVE "path"` | Save a BASIC program to disk |
| `LOAD "path" CODE addr, len` | Load machine code |
| `SAVE "path" CODE addr, len` | Save machine code |
| `LOAD "path" DATA var()` | Load an array |
| `SAVE "path" DATA var()` | Save an array |
| `ERASE "path"` | Delete a file |
| `RENAME "old" TO "new"` | Rename a file |
| `ATTRIB "path", attrs` | Set file attributes |
| `COPY "src" TO "dst"` | Copy a file |
| `FORMAT drive, params` | Format a disk |
| `DISKCOPY src, dst` | Copy an entire disk |
| `VERIFY "path"` | Verify a file against disk |
| `RUN "path"` | Equivalent to LOAD + RUN |

The commands use MS-DOS-like syntax (e.g., `RENAME ... TO ...`, `ATTRIB`) rather than the +3 DOS-style abbreviations. The `CAT`, `FORMAT`, `ERASE` keywords are present in the original Sinclair BASIC ROM as inactive tokens; IS-DOS activates them.

### 5.2 Path interpretation

All IS-DOS commands accept full or relative paths:

- `CAT "/"` — list the root directory.
- `CAT "/GAMES"` — list the `/GAMES` subdirectory.
- `CAT ""` — list the current directory.
- `LOAD "/UTILS/EDIT.BAS"` — load a file from an absolute path.
- `LOAD "EDIT.BAS"` — load from the current directory.
- `LOAD "../SIBLING/FILE"` — load from a sibling directory.

The path parser handles forward and backslashes interchangeably. Drive prefixes (`A:`, `B:`, `R:`) can be prepended to specify a drive.

### 5.3 The `CAT` output format

`CAT` produces an MS-DOS-like directory listing:

```
Volume in drive A is WORK
Directory of A:\

GAMES        <DIR>    1993-06-15  14:32
UTILS        <DIR>    1993-06-15  14:33
README   TXT     1024  1993-06-15  14:30
MYPROG   BAS     4096  1993-06-20  10:15
DATA             512  1993-06-18  09:45

    5 file(s)    5632 bytes
                783360 bytes free
```

This format should be familiar to anyone who has used MS-DOS's `DIR` command. It shows the file name, extension, size (for files), `<DIR>` flag (for directories), and modification date/time.

### 5.4 Wildcards

IS-DOS supports **wildcard characters** in path arguments:

- `?` matches any single character.
- `*` matches any sequence of characters (including zero).

Examples:

- `CAT "*.BAS"` — list all files with the `.BAS` extension.
- `ERASE "*.TMP"` — delete all `.TMP` files in the current directory.
- `COPY "A:*.*" TO "B:"` — copy all files from drive A to drive B.

Wildcards are interpreted at the directory level — they cannot span directory boundaries. `CAT "/GAMES/*.BAS"` works; `CAT "/GAMES/*/*.BAS"` does not.

---

## §6. The Assembly API

For machine-code programs, IS-DOS exposes a set of **API routines** that can be called directly. These routines are accessed via fixed entry points in the IS-DOS ROM.

### 6.1 The IS-DOS jump table

The IS-DOS ROM contains a **jump table** at a known address (typically `#5C00` or another fixed location, depending on the IS-DOS version). Each entry in the table is a 3-byte `JP` instruction to the corresponding routine. The table allows IS-DOS to be updated internally without breaking software that calls its routines — only the jump table addresses need to remain stable.

A typical IS-DOS jump table contains:

| Offset | Routine | Purpose |
|---|---|---|
| `#00` | `INIT_DISK` | Initialise disk subsystem |
| `#03` | `READ_SECTOR` | Read one disk sector |
| `#06` | `WRITE_SECTOR` | Write one disk sector |
| `#09` | `OPEN_FILE` | Open a file by path |
| `#0C` | `CLOSE_FILE` | Close an open file |
| `#0F` | `READ_FILE` | Read bytes from an open file |
| `#12` | `WRITE_FILE` | Write bytes to an open file |
| `#15` | `SEEK_FILE` | Seek to a position in an open file |
| `#18` | `DELETE_FILE` | Delete a file by path |
| `#1B` | `RENAME_FILE` | Rename a file |
| `#1E` | `MAKE_DIR` | Create a subdirectory |
| `#21` | `CHANGE_DIR` | Change current directory |
| `#24` | `FIND_FIRST` | Start a wildcard search |
| `#27` | `FIND_NEXT` | Continue a wildcard search |
| `#2A` | `GET_ATTR` | Get file attributes |
| `#2D` | `SET_ATTR` | Set file attributes |
| ... | ... | (additional routines) |

The full jump table is documented in the IS-DOS programmer's reference (in Russian; an English translation exists in the community).

### 6.2 Calling IS-DOS routines

To call an IS-DOS routine, a machine-code program:

1. Loads the routine's address from the jump table.
2. Loads the arguments into the appropriate registers.
3. Disables interrupts.
4. Switches in the IS-DOS ROM (by writing to the appropriate port).
5. Calls the routine.
6. Switches back to the BASIC ROM.
7. Re-enables interrupts.

This is similar to calling TR-DOS hook codes, but with explicit bank switching.

Example: open a file for reading:

```z80
is_open:
        DI                          ; disable interrupts
        LD   BC,#1FFD               ; (or whichever port selects the IS-DOS ROM)
        LD   A,#01                  ; select IS-DOS ROM
        OUT  (C),A
        
        LD   HL,filename            ; HL -> "MYFILE.TXT"
        LD   DE,path_buffer         ; DE -> normalised path buffer
        CALL #5C09                  ; call OPEN_FILE via jump table
        
        ; Returns:
        ;   Carry clear = success, A = file handle (0-15)
        ;   Carry set = error, A = error code
        
        LD   BC,#1FFD
        LD   A,#00                  ; back to BASIC ROM
        OUT  (C),A
        EI
        RET
```

This pattern is verbose but works. IS-DOS provides library routines that simplify the bank switching for common cases.

### 6.3 Error codes

IS-DOS uses **MS-DOS-compatible error codes** for diagnostics:

| Code | Mnemonic | Meaning |
|---|---|---|
| 0 | OK | No error |
| 1 | INVALID_FUNC | Invalid function number |
| 2 | FILE_NOT_FOUND | File not found |
| 3 | PATH_NOT_FOUND | Directory in path not found |
| 4 | TOO_MANY_OPEN | No free file handles |
| 5 | ACCESS_DENIED | Permission denied (e.g., read-only) |
| 6 | INVALID_HANDLE | Invalid file handle |
| 7 | DISK_FULL | Disk full |
| 8 | WRITE_PROTECT | Disk is write-protected |
| 9 | DRIVE_NOT_READY | No disk in drive |
| 10 | IO_ERROR | Disk I/O error |
| 11 | INVALID_FORMAT | Bad disk format |

These error codes are returned in the A register when a routine sets the carry flag. BASIC programs see them via the standard `ON ERROR GOTO` mechanism.

---

## §7. Hardware Requirements

### 7.1 Supported machines

IS-DOS runs on most Russian Spectrum clones with a Beta 128-compatible disk interface:

| Machine | IS-DOS support | Notes |
|---|---|---|
| Iskra 48K / 128K | Full | The original target |
| Pentagon 128 / 512 / 1024 | Full | With Beta 128 interface |
| Scorpion 256 / ZS-256 | Full | With patches |
| ATM Turbo 2+ | Full | With ATM-specific patches |
| Profi | Partial | Requires specific IS-DOS build |
| Kay 1024 | Full | With Beta 128 interface |
| Leningrad 1/2/3 | Partial | Requires specific IS-DOS build |
| Original Sinclair machines | **Not supported** | Requires Beta 128-compatible hardware |

IS-DOS is essentially **Russian clone only**. It does not run on original Sinclair Spectrums because they do not have Beta 128-compatible disk hardware (unless an interface is added).

### 7.2 Disk hardware

IS-DOS works with the standard Russian disk hardware:

- **Beta 128 interface** (WD1793 FDC) — the most common.
- **ATM Turbo's built-in disk interface** — for ATM clones.
- **Profi's disk interface** — for Profi clones.
- **SMC** (SM-Centaur) interface — less common.

The disk formats are standard PC-style MFM, so IS-DOS disks can be read by PC disk drives of the appropriate physical size.

### 7.3 Disk sizes

IS-DOS supports a range of disk sizes:

- **5.25"** DD (40 tracks, 2 sides, 10 sectors/track) = 800 KB.
- **5.25"** HD (80 tracks, 2 sides, 15 sectors/track) = 1200 KB.
- **3.5"** DD (80 tracks, 2 sides, 9 sectors/track) = 720 KB.
- **3.5"** HD (80 tracks, 2 sides, 18 sectors/track) = 1440 KB.

The most common format in the early IS-DOS era was 5.25" DD (800 KB). Later, as 3.5" drives became standard, the 1.44 MB 3.5" HD format became common.

### 7.4 Hard disk support

Some IS-DOS versions support **hard disk partitions**, for clones that have hard disk interfaces (ATM Turbo, some Profi configurations). Hard disk support is similar to MS-DOS's: the disk is divided into partitions, each of which appears as a separate drive letter.

Hard disk support was uncommon but valuable for power users. A typical 1990s IS-DOS hard disk was 20–40 MB — vast compared to a floppy disk.

---

## §8. The Software Library

Software written specifically for IS-DOS is much smaller than the TR-DOS library. Most Russian software was distributed on TR-DOS disks; IS-DOS-specific releases are rare.

### 8.1 IS-DOS-specific software

The IS-DOS software library includes:

- **System software**: IS-DOS itself, plus utilities for disk copying, formatting, repair.
- **Word processors**: a Russian-language word processor called "Iskra-Text" (similar to WordStar, with Cyrillic support).
- **Spreadsheets**: a basic spreadsheet (similar in scope to Multiplan).
- **Databases**: a simple flat-file database.
- **Programming tools**: IS-DOS-specific versions of Pascal and C compilers.
- **Terminal programs**: for connecting to BBSes via modem.
- **Graphics editors**: for editing sprites and screens with file I/O via IS-DOS paths.

In total, perhaps a few hundred IS-DOS-specific programs were produced. Most are utility software rather than games.

### 8.2 TR-DOS-to-IS-DOS conversion

A common task for IS-DOS users was converting TR-DOS disks to IS-DOS format. Conversion utilities existed:

- `TRDTOIS` — reads a TR-DOS `.trd` image and writes its contents into an IS-DOS directory, preserving filenames (with adjustments for the 8+1 to 8+3 format difference).
- `ISTOTRD` — the reverse, for compatibility with TR-DOS software.

Conversion is mostly automatic but imperfect. Some TR-DOS software uses file attributes or load addresses that IS-DOS does not preserve exactly.

### 8.3 The IS-DOS shareware scene

In the mid-1990s, a small "shareware" scene emerged around IS-DOS. Authors would release software as IS-DOS disks, expecting users to send money or other software in exchange for registered versions. This scene was small (perhaps a few dozen active authors) but produced some high-quality utility software.

Most IS-DOS shareware is now abandonware, distributed freely by Russian Spectrum archives.

---

## §9. Modern Status (2024)

IS-DOS in 2024 is **historically important but practically inactive**. No new IS-DOS software has been written in years; the system is preserved for study and nostalgia.

### 9.1 Emulator support

Modern Spectrum emulators support IS-DOS to varying degrees:

- **UnrealSpeccy** (Russian emulator) — full IS-DOS support, including the hierarchical filesystem.
- **ZEsarUX** — partial IS-DOS support; can read IS-DOS disks.
- **Fuse** — limited support; can read IS-DOS disks but does not provide the full IS-DOS environment.
- **Spectaculator** — limited support.

For users wanting to explore IS-DOS in 2024, UnrealSpeccy is the recommended emulator.

### 9.2 Software archives

IS-DOS software is preserved by:

- **TR-DOS.ru** — a Russian Spectrum archive that includes some IS-DOS disks.
- **World of Spectrum** — has a small IS-DOS section.
- **Personal archives** of Russian Spectrum collectors.

IS-DOS disk images are typically distributed as `.imd` (ImageDisk format) or `.fdi` (Formatted Disk Image) files. The formats preserve the disk geometry accurately.

### 9.3 Current users

The number of active IS-DOS users in 2024 is very small — perhaps a few dozen Russian Spectrum enthusiasts. There is no active development of IS-DOS itself; the system is essentially frozen at its 1990s state.

For comparison, TR-DOS still has an active user base in the Russian Spectrum community (via the Pentagon and modern Pentagon-compatible clones). ESXDOS has a much larger user base in the Western community (via DivIDE/DivMMC). IS-DOS sits somewhere between — historically important but practically obsolete.

### 9.4 Why IS-DOS is worth knowing

Despite its current obscurity, IS-DOS is worth understanding for several reasons:

1. **As a technical achievement.** IS-DOS brought MS-DOS-like hierarchical file management to the Spectrum before any Western DOS did. The filesystem design is sound and well-implemented.
2. **As a historical lesson.** IS-DOS shows that the Russian Spectrum scene was not a TR-DOS monoculture. There were attempts to innovate and improve.
3. **As a comparison point.** Understanding IS-DOS helps clarify what TR-DOS, ESXDOS, and other Spectrum DOSes do well or poorly.
4. **As a learning tool.** IS-DOS's source code (available in Russian) is a useful reference for anyone designing small-system file systems.

---

## §10. Cross-References

- **[trdos.md](trdos.md)** — The dominant Russian DOS. IS-DOS was designed as an alternative to TR-DOS; this article's §1.3 compares the two in detail.
- **[esxdos.md](esxdos.md)** — The modern Western DOS with similar hierarchical features. IS-DOS predated ESXDOS by ~15 years but addresses many of the same problems.
- **[plus3dos.md](plus3dos.md)** — The Amstrad +3 DOS, which IS-DOS resembles in some respects (MS-DOS-like attributes, hierarchical directories).
- **[cpm.md](cpm.md)** — CP/M 2.2 on the Spectrum. CP/M's BDOS influenced both IS-DOS and +3 DOS.
- **[nextzxos.md](nextzxos.md)** — The ZX Spectrum Next OS, which (via its FAT16/32 support) provides modern hierarchical filesystem features that IS-DOS pioneered on the Spectrum.
- **[../02_hardware/clones/README.md](../02_hardware/clones/README.md)** — Russian clone hardware reference. IS-DOS runs on Iskra, Pentagon, Scorpion, ATM Turbo, and similar machines.
- **[../05_development/03_memory_and_io/memory_and_io_pentagon.md](../05_development/03_memory_and_io/memory_and_io_pentagon.md)** — The Pentagon's memory model, which IS-DOS uses for its work buffers.
- **[nedo_dos.md](nedo_dos.md)** — Another Russian DOS variant, related to IS-DOS.

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same licence.
