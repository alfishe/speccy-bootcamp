[← Home](../README.md) · [Operating Systems](README.md)

# TR-DOS — The Soviet Disk Standard

Where Western Spectrum owners booted a +3 DOS disk or copied files to cassette, the entire Soviet and post-Soviet demoscene standardized on a single disk operating system: **TR-DOS**. Bundled with every Pentagon, Scorpion, and Kay clone from 1987 onwards, TR-DOS is the file system on which the Russian-language demo scene's megademos, disk magazines, and party entries were distributed for almost two decades. A modern emulator loading a `.TRD` image is mounting a TR-DOS disk.

TR-DOS is the work of two engineers, neither of them Sinclair: **Evgeny Samarsky** (Евгений Самарский, Leningrad) and **Charles Ingman** (Moscow). Samarsky wrote the original version for the Beta 128 disk interface around 1985–1987; the result is a 16 KB ROM that pages into the Spectrum address space and exposes a BASIC extension (the `*` commands such as `*CAT`, `*LOAD`, `*SAVE`) plus a small assembly-level API called the **hook codes**. The file system is a custom 80-track, 16-sector layout with a flat directory — simple, fast for sequential access, and uniquely tolerant of poorly-floppy media of the late-Soviet era.

This article covers TR-DOS as a system: the Beta 128 hardware it sits on, its memory layout, the BASIC command set, the on-disk file system, the assembly hook codes, common programming patterns, and the quirks that anyone writing a TR-DOS-aware demo or game must know. For the wider Pentagon hardware picture, see [../02_hardware/clones/README.md](../02_hardware/clones/README.md). For how demos use TR-DOS to stream parts from disk, see [../07_demoscene/demo_frameworks.md](../07_demoscene/demo_frameworks.md) §5.

---

## Roadmap

1. **What TR-DOS is** — history, scope, why it became the Soviet standard
2. **The Beta 128 hardware** — WD1793 FDC, port layout, ROM slot
3. **Memory layout under TR-DOS** — what the 16 KB ROM replaces, where it lives
4. **The BASIC command set** — `*`-prefixed commands, syntax, examples
5. **The TR-DOS disk format** — geometry, directory, file types, free space bitmap
6. **Hook codes** — assembly-level file I/O, the nine standard calls
7. **Programming patterns** — loading, saving, catalog access, custom loaders
8. **Quirks, traps, and compatibility** — what bites the unwary programmer
9. **Modern status and tools** — `.TRD` images, emulators, cross-platform tooling
10. **Cross-references** — where to go next

---

## §1. What TR-DOS Is

### 1.1 Why a separate DOS at all

The Sinclair Spectrum was not designed with a disk drive in mind. Cassette tape was the official mass-storage medium from the original 16K model in 1982 through the +2A in 1987. When Sinclair finally shipped a disk-equipped machine — the +3 in 1987 — it ran Amstrad's +3 DOS, a CP/M-derived file system that talked to the built-in 3-inch drive through an Amstrad-designed gate array and a UPD765 FDC.

This path was closed to Soviet users. The +3 was never officially sold in the USSR, and Amstrad's custom disk controller was effectively uncloneable in late-Soviet conditions. What Soviet engineers could clone, cheaply and reliably, was the Western Digital **WD1793** floppy disk controller — an off-the-shelf part with comprehensive datasheets, widely used in 8-bit personal computers from TRS-80 to MSX. By the mid-1980s, Soviet semiconductor fabs were producing a direct equivalent, the **KR1818VG93** (КР1818ВГ93), and several hobbyist disk interfaces for the Spectrum had appeared using it.

TR-DOS is the operating system that sat on top of one such interface: the **Beta 128**, designed by the same Leningrad team (VLK — *Voenno-lyubitelny klub*, "Military-Hobbyist Club") that produced the Pentagon. The combination — a Pentagon clone, a Beta 128 card, a 5.25-inch floppy drive, and TR-DOS — became the default Soviet Spectrum setup from approximately 1989 and remained so until the late 1990s.

### 1.2 History

The development of TR-DOS is conventionally attributed to **Evgeny Samarsky** (the file system, disk routines, and most of the ROM) and **Charles Ingman** (the BASIC extension layer and command parser). Working from their respective Soviet cities, they delivered the first widely-circulated TR-DOS version, **TR-DOS 5.00**, around 1986. Minor revisions followed through the late 1980s:

| Version | Year | Notable change |
|---|---|---|
| 4.00 | ~1985 | Early pre-release; buggy, limited distribution |
| 5.00 | ~1986 | First widely distributed; canonical file format |
| 5.01 | ~1987 | Bug fixes; improved `*FORMAT` reliability |
| 5.03 | ~1988 | The most commonly seen version on real hardware |
| 5.04 | ~1990 | Minor changes; rarely seen on Pentagon |
| 6.00+ | ~1991 | Scorpion-specific extensions by Scratchy (Scorpion ZS-256 Turbo version only) |

For all practical purposes, **TR-DOS 5.03** is "TR-DOS": it is what every emulator defaults to, what every Pentagon owner booted, and what every `.TRD` disk image in circulation assumes. The differences between 5.00 and 5.03 are small enough that most software written for one runs on the other; 6.00 and later are Scorpion-specific and outside the scope of this article.

### 1.3 Why it succeeded

TR-DOS became the Soviet standard for a combination of technical and circumstantial reasons:

- **Hardware ubiquity.** Every Pentagon shipped with a Beta 128 (or a Beta 128-compatible integrated controller) and a 5.25" floppy drive. There was no alternative DOS in widespread use.
- **Tape was already obsolete.** By the time the Pentagon reached volume production in 1989–1990, Soviet hobbyists had been transferring software via cassette for years and were heartily sick of the unreliability. Floppy was the upgrade everyone wanted.
- **The file format was simple and forgiving.** TR-DOS's flat directory and 8.3-ish filename scheme made it easy to write the simplest possible tools, and the geometry (80 tracks × 16 sectors × 256 bytes) survived a lot of marginal media.
- **The BASIC extension was unobtrusive.** TR-DOS did not interfere with the 48K BASIC ROM or the 128K editor; it added commands prefixed with `*`, so existing software continued to work.
- **Piracy.** TR-DOS made copying a disk a one-command operation (`*COPY`). In a scene where distribution was entirely user-to-user, this mattered.

By 1992, every significant Soviet demoscene group was shipping on TR-DOS. By 1996, every party entry required a `.TRD` submission. The format's dominance is the reason `.TRD` images remain the de facto archive format for Soviet Spectrum software to this day.
---

## §2. The Beta 128 Hardware

TR-DOS is meaningless without the disk controller it talks to. Understanding the hardware is essential for anyone writing custom disk code, repairing real Pentagon hardware, or implementing a TR-DOS emulator.

### 2.1 The WD1793 floppy disk controller

At the heart of the Beta 128 is a single chip: the **Western Digital WD1793** (or its Soviet clone, the **KR1818VG93**). The WD1793 is an LSI floppy disk controller that handles the low-level timing of MFM/ FM data separation, CRC generation, and address-mark detection. To the host CPU it presents a 4-register interface:

| Register offset | Read | Write |
|---|---|---|
| `+0` | Status | Command |
| `+1` | Track register | Track register |
| `+2` | Sector register | Sector register |
| `+3` | Data register | Data register |

The Beta 128 decodes these four registers onto four consecutive I/O ports. The WD1793 generates an interrupt (`INTRQ`) on command completion and a data request (`DRQ`) on every byte transfer — the host CPU polls these via an additional status port.

Key parameters supported by the WD1793 in Beta 128 use:

- **Recording mode**: MFM (modified frequency modulation) at 250 kbit/s on double-density disks, the only mode TR-DOS uses.
- **Sector size**: 256 bytes (the WD1793's `#x01` sector length code, configured per command).
- **Step rate**: 6 ms — a compromise between speed and reliability on Soviet-made 5.25" mechanisms.
- **Settling time**: 30 ms.

These timings plus the 300 RPM spin rate of a 5.25" drive give the well-known per-sector access time of roughly 100 ms (seek) + 12.5 ms (one-revolution average rotational latency) + 8 ms (256-byte read at 250 kbit/s) = **~120 ms** per random sector access. Sequential reads within a track are dramatically faster — about 6 sectors per revolution, so ~50 ms for a 6-sector file.

### 2.2 Port layout

The Beta 128 occupies **8 consecutive I/O ports** starting at `#1F`. The exact port mask varies slightly between clones, but the canonical Pentagon layout is:

| Port | Read | Write | Purpose |
|---|---|---|---|
| `#1F` | Status | Command | WD1793 register 0: FDC command/status |
| `#3F` | Track | Track | WD1793 register 1: current track number |
| `#5F` | Sector | Sector | WD1793 register 2: desired sector number |
| `#7F` | Data | Data | WD1793 register 3: data byte for read/write |
| `#FF` | System status | System control | Drive select, side, density, motor, ROM page |
| `#BF` | — | (write-only) | Memory page selection on some clones (Scorpion) |
| `#9F` | — | — | Reserved (used on ATM Turbo for IDE) |
| `#DF` | — | — | Reserved (used on Scorpion for additional paging) |

The **system control port at `#FF`** is the one that matters most. Its bit layout:

| Bit | Function |
|---|---|
| 0 | Drive select A (1 = active) |
| 1 | Drive select B (1 = active) |
| 2 | Reserved |
| 3 | Side select (0 = side 0, 1 = side 1) |
| 4 | Density (0 = FM single, 1 = MFM double) |
| 5 | ROM page bit 0 (TR-DOS ROM on/off) |
| 6 | ROM page bit 1 |
| 7 | System ROM off (1 = disable BASIC ROM) |

The motor-on signal is implicit: the Beta 128 turns the drive motor on whenever any drive-select bit is set, and leaves it on for a few seconds after the last operation. There is no separate "motor on" bit.

### 2.3 The ROM slot

The Beta 128 card carries a 16 KB ROM (actually a 27128 or 2764 EPROM) holding the TR-DOS code. The Spectrum's address space normally cannot see this ROM — the BASIC ROM at `#0000–#3FFF` is permanently enabled on a 48K machine. The Beta 128 therefore includes a small piece of glue logic that, when activated via the system control port, **disables the BASIC ROM and enables the TR-DOS ROM in its place**.

The switch is performed by setting bit 7 of port `#FF`. After this write, all reads in the range `#0000–#3FFF` come from the TR-DOS ROM rather than the BASIC ROM. The RAM from `#4000` upward is unchanged. This is the same mechanism the 128K machine uses for its own ROM 0 / ROM 1 switching — the Beta 128 simply co-opts it.

The switch is **bidirectional and instant**: a single `OUT (#FF),A` instruction flips the active ROM. This is why TR-DOS routines can be called from machine code without any complex banking scheme — the caller pages TR-DOS in, calls the routine, pages it back out, and returns. See §6 for the standard calling sequence.

### 2.4 Drive geometry

TR-DOS supports three disk geometries, although only the first is common in practice:

| Geometry | Tracks | Sectors/track | Sides | Total size | Notes |
|---|---|---|---|---|---|
| 80-track DSDD | 80 | 16 | 2 | 640 KB | The canonical Pentagon disk; standard for all Soviet demos |
| 40-track SSDD | 40 | 16 | 1 | 160 KB | Early format, rare after 1990 |
| 80-track SSDD | 80 | 16 | 1 | 320 KB | Used on single-drive systems; seen in early diskmags |

The first track of side 0 (track 0, sectors 1–8) holds the **disk catalog** (see §5.2). The remaining 79 tracks of side 0 plus all 80 tracks of side 1 hold file data. Sectors are numbered 1 through 16 within each track; this 1-based convention is a WD1793 feature, not a TR-DOS choice.

The 640 KB double-sided disk became so canonical that the `.TRD` image format used by modern emulators is exactly 655,360 bytes — 80 × 16 × 256 × 2 — with no header, no footer, no metadata. A `.TRD` file is a raw sector-by-sector dump of an entire TR-DOS disk.

### 2.5 Hardware variants and clones

The Beta 128 design was widely copied, with minor variations:

- **Beta 128 original** (VLK, 1987): the reference design, on a separate expansion card.
- **Beta 128 integrated** (Pentagon-128 and later): the same logic integrated onto the Pentagon motherboard, occupying the same port addresses.
- **Beta 128 Scorpion variant** (Scorpion ZS-256): additional paging registers, slightly different port decoding.
- **SMUC** (Spectrum Magistral Universal Controller): Beta 128-compatible plus IDE hard disk interface on the same card.
- **DivIDE / DivMMC**: modern interfaces that implement Beta 128 *compatibility* in addition to their primary IDE/SD function. Useful for running real TR-DOS software on a real Spectrum today.

For machine code that needs to talk directly to the FDC, the Pentagon port layout (`#1F` base, `#FF` system) is the safest target: it works on every Beta-compatible interface and every emulator. The Scorpion-specific ports should be avoided unless you know your audience.
---

## §3. Memory Layout Under TR-DOS

When TR-DOS is paged in, the Spectrum's memory map changes in a small but critical way. Programmers writing code that calls TR-DOS hook codes (§6) or that needs to coexist with the DOS must understand exactly what overlaps what.

### 3.1 The 48K machine

On a 48K (or Pentagon-48K) machine, the memory map under TR-DOS is:

| Address range | Without TR-DOS | With TR-DOS paged in |
|---|---|---|
| `#0000`–`#3FFF` | BASIC ROM | **TR-DOS ROM** |
| `#4000`–`#5AFF` | Screen RAM | Screen RAM (unchanged) |
| `#5B00`–`#5CB5` | System variables | System variables (unchanged) |
| `#5CB6`–`#FF57` | BASIC program / free RAM | BASIC program / free RAM (unchanged) |
| `#FF58`–`#FFFF` | TR-DOS workspace (only when paged) | TR-DOS workspace |

The TR-DOS ROM occupies exactly the same address range as the BASIC ROM. When TR-DOS is paged in, the BASIC ROM is invisible — calling a ROM routine such as `RST #10` (print a character) will instead call whatever is at the corresponding offset in the TR-DOS ROM, which is *not* a print-a-character routine.

This is the single biggest trap for new TR-DOS programmers. **If you page TR-DOS in, you cannot use the BASIC ROM.** The TR-DOS ROM does include its own routines for many common operations (printing, keyboard scanning, etc.) at different addresses, but they must be called by their TR-DOS addresses, not by the familiar `RST` codes.

### 3.2 The 128K and Pentagon-128

On a 128K or Pentagon-128, the same physical layout applies, with one addition: TR-DOS uses the standard `#7FFD` paging port to switch the active 16 KB RAM bank at `#C000`–`#FFFF`. The TR-DOS workspace (its own variables, buffers, and stack) lives in **RAM bank 0**, which is mapped to `#C000`–`#FFFF` during TR-DOS operations.

The 128K TR-DOS memory map:

| Address range | Content |
|---|---|
| `#0000`–`#3FFF` | TR-DOS ROM (when paged in) |
| `#4000`–`#7FFF` | RAM bank 5 — screen |
| `#8000`–`#BFFF` | RAM bank 2 — usually BASIC program / free |
| `#C000`–`#FFFF` | RAM bank 0 — TR-DOS workspace during DOS calls |

This is why TR-DOS calls clobber memory at `#C000` and above: the workspace lives there. If your program is using the upper 16 KB of the active bank for data, that data will be overwritten by any TR-DOS call.

### 3.3 Stack considerations

TR-DOS uses the main Z80 stack (the `SP` register), not a separate stack. The TR-DOS routines are stack-safe in the sense that they preserve `IX`, `IY`, and the alternate register set, but they do use the stack for their own internal calls. Ensure the stack pointer is in valid RAM (typically `#FF40`–`#FF57` on a 48K machine, `#5E00`-ish on a 128K machine) before calling any TR-DOS hook code.

A typical pre-call setup:

```z80
DI                      ; interrupts off — TR-DOS uses IM1 with its own ISR
LD   HL,#FF40           ; safe stack location
LD   SP,HL
LD   B,0                ; filename length (will be set per call)
; ... set up registers per hook code table ...
CALL #3D13              ; the TR-DOS entry point (see §6.1)
```

### 3.4 What TR-DOS does not touch

Reassuringly, TR-DOS does **not** touch:

- The screen RAM (`#4000`–`#57FF`) — your display is safe.
- The attribute file (`#5800`–`#5AFF`) — your colors are safe.
- The system variables area (`#5B00`–`#5CB5`) — except for the specific bytes TR-DOS uses as its own workspace (see below).
- RAM banks other than the one currently paged in at `#C000` — useful for keeping data safe across DOS calls.

The TR-DOS-specific system variable bytes (in the otherwise-reserved area at `#5CB6`–`#5CCF`) hold the drive select state, the current directory position, and temporary scratch. Programmers should treat this range as owned by TR-DOS and never write to it directly.

---

## §4. The BASIC Command Set

TR-DOS exposes its BASIC-level functionality via commands prefixed with `*`. To type a TR-DOS command, the user enters the BASIC editor, types `*`, and then the command word. The `*` is itself a single keypress (typically Symbol Shift + H on the 48K keyboard) and is parsed by the 128K editor as the start of a TR-DOS directive.

### 4.1 Disk and file management

| Command | Purpose | Example |
|---|---|---|
| `*FORMAT` | Initialise a blank disk; write the empty catalog | `*FORMAT` (then answer prompts) |
| `*CAT` | Display the disk catalog (file list) | `*CAT` |
| `*DIR` | Same as `*CAT` on some versions | `*DIR` |
| `*ERASE` | Delete a file | `*ERASE "demo.C"` |
| `*REN` | Rename a file | `*REN "old.B" TO "new.B"` |
| `*COPY` | Copy an entire disk (drive A → drive B) | `*COPY` (requires two drives) |
| `*BACKUP` | Make a bootable copy of the system disk | `*BACKUP` |

### 4.2 File loading and saving

| Command | Purpose | Example |
|---|---|---|
| `*LOAD` | Load any file by name into a given address | `*LOAD "demo.C" CODE 25000` |
| `*SAVE` | Save a block of memory to a named file | `*SAVE "screen.#" CODE 16384,6912` |
| `*VERIFY` | Verify a file on disk against memory | `*VERIFY "demo.C" CODE 25000` |
| `*MERGE` | Merge a BASIC file with the current program | `*MERGE "lib.B"` |
| `*RUN` | Load and execute a `.B` (BASIC) file | `*RUN "game.B"` |

### 4.3 Filename syntax

TR-DOS filenames are **8 characters of name + 1 character of extension**, case-insensitive:

```
NAME1234.X
└─┬──┘ └┬┘
  │    └── extension: 1 character
  └─────── name: up to 8 characters
```

The extension character is not optional — every file has exactly one. The standard extensions are:

| Extension | Meaning |
|---|---|
| `B` | BASIC program |
| `C` | Code (raw memory block) |
| `D` | Data array (numeric or string) |
| `#` | Screen dump (`#4000`–`#5AFF`, 6912 bytes) |
| `P` | Code file marked as a program (some authors use this for "executable") |
| `M` | Music data (PT3, ASC, etc.) |
| `S` | Sprite data (informal convention) |

These conventions are not enforced by TR-DOS — it stores all files as raw byte streams — but tools and demos generally follow them.

### 4.4 Booting from TR-DOS

TR-DOS disks are bootable: when a Pentagon is powered on with a TR-DOS disk in drive A, the machine boots directly into TR-DOS rather than BASIC. The boot sequence is:

1. Power-on reset → BASIC ROM at `#0000`.
2. BASIC ROM initialises RAM, prints the (c) 1982 message, then checks for a disk ROM by paging it in and looking for the magic bytes `"TRDOS"` at a specific offset.
3. If found, the BASIC ROM jumps to the TR-DOS entry point.
4. TR-DOS prints its startup banner (typically `TR-DOS 5.03`), loads the `boot.B` file from the disk if present, and runs it.

A bootable demo disk therefore contains a `boot.B` that loads the demo's first part. This is why a Soviet demo disk runs automatically when inserted at power-on — no commands needed.

### 4.5 Examples

A complete BASIC session loading and running a demo:

```
*CAT
GAME     B   1234
LOADER   C  16384
PIC      #   6912

*RUN "GAME"
```

The same operation, performed entirely from machine code (using the hook codes from §6), is what a `boot.B` would do — typically just a few `LOAD` and `CALL` instructions chained together.
---

## §5. The TR-DOS Disk Format

The on-disk layout of a TR-DOS disk is simple, well-documented, and stable across all versions. Anyone writing a TR-DOS tool — a catalog browser, a defragmenter, a disk image inspector — needs to know this format.

### 5.1 Disk geometry recap

A canonical 640 KB TR-DOS disk:

- **80 tracks per side** (numbered 0 to 79).
- **16 sectors per track** (numbered 1 to 16 — note the 1-based convention).
- **2 sides** (side 0 and side 1).
- **256 bytes per sector.**

Total: 80 × 16 × 2 × 256 = **655,360 bytes**.

Sectors are interleaved on a single track in physical order 1, 2, 3, ..., 16 (no skew factor). Files written sequentially within a track can therefore be read back at the maximum sustained rate of one sector per ~5 ms.

### 5.2 The catalog (track 0)

The first 8 sectors of **track 0, side 0** (sectors 1–8, 2048 bytes total) hold the disk catalog. This region is organized as:

- **8 file descriptors** (each 16 bytes) in sectors 1–4: 4 descriptors × 16 bytes × 4 sectors = 256 bytes per sector. Total: 128 file slots.
- **Free-space and disk metadata** in sectors 5–8.

#### The 16-byte file descriptor

Each file slot occupies 16 bytes laid out as:

| Offset | Size | Field | Description |
|---|---|---|---|
| `+0` | 1 | Status | `#00` = empty slot, `#01`–`#FE` = deleted file (kept for undelete), `#FF` = file present |
| `+1` | 8 | Filename | 8 ASCII characters, space-padded |
| `+9` | 1 | Extension | 1 ASCII character (`B`, `C`, `D`, `#`, etc.) |
| `+10` | 2 | Length | File length in bytes (little-endian) |
| `+12` | 2 | Length in sectors | Number of 256-byte sectors the file occupies (little-endian) |
| `+14` | 1 | Start sector | Sector number within the start track (1-based) |
| `+15` | 1 | Start track | Track number of the first sector (0-based) |

A directory with no files has all 128 slots set to `#00` in the status byte. TR-DOS scans the directory linearly to find a free slot, so adding the 129th file to a disk is impossible — even if free space on disk remains.

#### The free-space and metadata sectors

Sector 5 of track 0 holds the **free-sector bitmap**: a 256-byte array in which each bit represents one sector on the disk (bit set = free, bit clear = allocated). With 80 × 16 × 2 = 2560 sectors per disk, the bitmap uses 320 bytes — slightly more than one sector. TR-DOS therefore spills the bitmap into the first 64 bytes of sector 6.

The remainder of sector 6 plus sectors 7–8 hold:

- The disk label (8 ASCII characters).
- The number of free sectors (2 bytes, little-endian).
- The disk format code (1 byte: `#16` for 80-track DSDD, `#17` for 80-track SSDD, `#18` for 40-track SSDD).
- The position of the first free sector (used as a hint for the next allocation).
- Reserved bytes (TR-DOS 6.x uses some of these for additional features; 5.x leaves them as `#00`).

### 5.3 File placement strategy

When TR-DOS writes a new file, it:

1. Scans the catalog for a free slot (`#00` status byte).
2. Reads the free-sector bitmap, locates `N` consecutive free sectors starting from the first-free hint.
3. Allocates the sectors by clearing the corresponding bits.
4. Writes the file data to the allocated sectors.
5. Updates the catalog slot with the filename, length, sector count, and start position.

The "consecutive free sectors" requirement is the reason TR-DOS disks benefit from periodic defragmentation: a heavily-used disk accumulates gaps that TR-DOS will not span with a single file, even when total free space is sufficient.

Files do **not** cross track boundaries by default — TR-DOS attempts to keep each file within a single track whenever possible, for read performance. Files larger than 16 sectors (4096 bytes) automatically span multiple tracks.

### 5.4 The `.TRD` image format

The `.TRD` image format used by every modern Spectrum emulator is a literal byte-for-byte dump of a TR-DOS disk. The image file is:

- **Exactly 655,360 bytes** for an 80-track DSDD disk (the most common case).
- **Exactly 327,680 bytes** for an 80-track SSDD disk.
- **Exactly 163,840 bytes** for a 40-track SSDD disk.
- **No header, no footer, no metadata.**

Byte offset `N` in the image corresponds to physical (track, sector, side, offset-within-sector) computed as:

```
byte_offset = ((side * 80 + track) * 16 + (sector - 1)) * 256 + offset_within_sector
```

The first 2048 bytes of any `.TRD` image are the catalog (track 0, side 0, sectors 1–8). The next 4096 bytes (sectors 9–16 of track 0 side 0) are the first data sectors. Track 1 begins at offset 16 × 256 = 4096.

### 5.5 Reading a catalog programmatically

Given a `.TRD` image, extracting the file list is a straightforward operation in any language:

```python
import struct
with open("disk.trd", "rb") as f:
    data = f.read()

# Catalog is the first 8 sectors of the image (offset 0..2048)
catalog = data[0:2048]

for slot_idx in range(128):
    slot = catalog[slot_idx * 16:(slot_idx + 1) * 16]
    status = slot[0]
    if status != 0xFF:
        continue
    filename = slot[1:9].decode('ascii', errors='replace')
    extension = chr(slot[9])
    length = struct.unpack('<H', slot[10:12])[0]
    sectors = struct.unpack('<H', slot[12:14])[0]
    start_sector = slot[14]
    start_track = slot[15]
    print(f"{filename}.{extension}  {length} bytes  {sectors} sectors  @T{start_track}S{start_sector}")
```

This pattern — read 2048 bytes, walk 128 16-byte slots, decode the active ones — is universal to TR-DOS tools. Every emulator, every catalog viewer, every disk-editor implements this exact algorithm.

### 5.6 Deleted files and undelete

When a file is erased with `*ERASE`, TR-DOS does not zero out its catalog slot. It writes the value `#01` to the status byte and leaves the rest of the slot intact. The file's data on disk is also untouched — only the free-sector bitmap is updated to mark the file's sectors as available.

This means **deleted files can be undeleted** simply by changing the status byte back to `#FF` (assuming no other file has been written in the meantime). Several Soviet utilities exploited this; modern tooling such as `trdtool.py` exposes it as a command-line option.

The status byte values `#02` through `#FE` are reserved for various markers used by utility software. TR-DOS itself only generates `#00`, `#01`, and `#FF`.
---

## §6. Hook Codes — The Assembly API

For machine-code programs — every game, every demo, every disk magazine — TR-DOS provides a small but complete API called the **hook codes**. These are entry points in the TR-DOS ROM, called via a single dispatch routine at `#3D13`, that perform file I/O without going through the BASIC command parser.

### 6.1 The dispatch mechanism

All hook codes are called through the same address: **`#3D13`**. The hook code itself is loaded into the `B` register before the call. TR-DOS inspects `B` and dispatches to the appropriate internal routine.

The standard call sequence is:

```z80
DI                      ; interrupts off
LD   B,hook_code        ; e.g. #07 for "read directory entry"
LD   HL,filename        ; address of 9-byte filename (8 + extension) for some calls
LD   DE,address         ; load/save address for some calls
LD   IX,parameter_block ; address of parameter block for some calls
CALL #3D13              ; dispatch to TR-DOS
; ... returns with carry flag set on success, reset on error ...
EI                      ; interrupts back on (caller responsibility)
```

If TR-DOS returns with the **carry flag set**, the call succeeded. If the carry flag is reset, an error occurred; the A register holds the error code (see §8.1).

### 6.2 The nine standard hook codes

The canonical set of hook codes supported by every TR-DOS version from 5.00 onward:

| `B` value | Name | Purpose | Parameters |
|---|---|---|---|
| `#00` | `INIT` | Re-initialise TR-DOS state, select drive A | None |
| `#01` | `SEEK` | Seek to a specific track | `A` = track number |
| `#02` | `READ_SECTOR` | Read one sector into memory | `A` = track, `C` = sector (1-based), `DE` = destination address |
| `#03` | `WRITE_SECTOR` | Write one sector from memory | `A` = track, `C` = sector (1-based), `DE` = source address |
| `#04` | `READ_FILE` | Read a file by name into memory | `HL` → 9-byte filename, `DE` → load address |
| `#05` | `WRITE_FILE` | Write memory to a new file | `HL` → 9-byte filename, `DE` → start address, `BC` → length |
| `#06` | `READ_CAT_ENTRY` | Read the Nth catalog entry | `C` = entry index (0..127), `IX` → 16-byte buffer |
| `#07` | `SCAN_CAT` | Scan catalog for a file by name | `HL` → 9-byte filename, returns entry in `C` |
| `#08` | `DELETE_FILE` | Delete a file by name | `HL` → 9-byte filename |

These nine operations cover the vast majority of disk I/O needs. Additional hook codes exist for things like file renaming, disk formatting, and direct FDC access, but they are version-specific and not portable.

### 6.3 Worked example: load a file

The single most common TR-DOS operation is "load a file by name into a known address". Here is the canonical implementation:

```z80
; -----------------------------------------------------------
; trdos_load — load a file from disk via TR-DOS hook code #04
;
; Input:  HL = address of 9-byte filename string ("NAME    C")
;         DE = destination address in memory
; Output: carry flag set on success, reset on error
;         A = error code on failure
; Destroys: AF, BC, DE, HL, IX, IY (TR-DOS preserves none)
; -----------------------------------------------------------
trdos_load:
        DI
        PUSH DE               ; save destination
        LD   B,#04            ; hook code: READ_FILE
        CALL #3D13            ; dispatch
        POP  DE               ; restore destination
        RET
```

The filename is a 9-byte string: 8 characters of name (space-padded if shorter) followed by 1 character of extension. There is no null terminator. If the file is not found, TR-DOS returns with carry reset and `A = #05` ("file not found").

### 6.4 Worked example: save a file

```z80
; -----------------------------------------------------------
; trdos_save — save a memory block to a file via TR-DOS #05
;
; Input:  HL = address of 9-byte filename string
;         DE = source address
;         BC = byte length
; Output: carry set on success, reset on error
; -----------------------------------------------------------
trdos_save:
        DI
        LD   B,#05            ; hook code: WRITE_FILE
        CALL #3D13
        RET
```

Note that TR-DOS will refuse to overwrite an existing file with the same name — `WRITE_FILE` always creates a new catalog slot. To replace a file, you must `DELETE_FILE` first, then `WRITE_FILE`.

### 6.5 Worked example: scan the catalog

To find a file by name without loading it (for example, to check if a file exists before loading):

```z80
; -----------------------------------------------------------
; trdos_find — locate a file in the catalog
;
; Input:  HL = address of 9-byte filename string
; Output: carry set on found, C = catalog index (0..127)
;         carry reset on not found
; -----------------------------------------------------------
trdos_find:
        DI
        LD   B,#07            ; hook code: SCAN_CAT
        CALL #3D13
        RET
```

Once you have the catalog index, you can call `READ_CAT_ENTRY` (`B = #06`) to retrieve the file's full 16-byte descriptor — its length, sector count, and start position. This is how a demo loader knows how many bytes to expect before issuing the `READ_FILE` call.

### 6.6 The full pre-call boilerplate

Most production code wraps every TR-DOS call in a standard prologue/epilogue to handle ROM paging. The complete sequence is:

```z80
trdos_call:
        ; --- prologue ---
        DI                      ; TR-DOS routines are not interrupt-safe
        LD   (save_sp),SP       ; save stack pointer
        LD   SP,#FF40           ; TR-DOS-friendly stack location
        LD   (save_7ffd),A      ; save current #7FFD paging byte
        PUSH AF
        LD   A,#10              ; RAM bank 0 in #C000-#FFFF (TR-DOS workspace)
        LD   BC,#7FFD
        LD   (BC),A
        ; (TR-DOS ROM is now visible at #0000-#3FFF via the call to #3D13 itself)
        
        ; --- the actual call ---
        LD   B,hook_code        ; specific to your operation
        CALL #3D13
        
        ; --- epilogue ---
        PUSH AF                 ; save TR-DOS result
        POP  AF
        LD   A,(save_7ffd)      ; restore original paging
        LD   BC,#7FFD
        LD   (BC),A
        LD   SP,(save_sp)       ; restore stack
        EI
        RET
```

This pattern appears, with minor variations, in essentially every Soviet demo and game that uses TR-DOS. It is one of the most copy-pasted snippets in the entire Spectrum codebase.

### 6.7 Direct sector I/O

For specialized uses — boot sectors, copy protection, disk editors, custom file systems — TR-DOS exposes the `READ_SECTOR` and `WRITE_SECTOR` hook codes (#02 and #03). These bypass the catalog entirely and let you read or write any sector by its physical coordinates.

```z80
; Read track 5, sector 3, into address #8000
DI
LD   B,#02              ; hook code: READ_SECTOR
LD   A,5                ; track
LD   C,3                ; sector (1-based)
LD   DE,#8000           ; destination
CALL #3D13
```

This is how the famous Soviet copy-protection schemes worked: they would write custom-formatted sectors that `*COPY` could not reproduce, then check for those sectors at runtime to verify an original disk. The corresponding western techniques (Speedlock, Alkatraz) used cassette-tape tricks instead — see [../08_reverse_engineering/README.md](../08_reverse_engineering/README.md) for the protection landscape.

### 6.8 Errors and error codes

When a TR-DOS hook code returns with the carry flag reset, the `A` register contains one of these standard error codes:

| Code | Meaning |
|---|---|
| `#01` | Operation in progress / retry needed |
| `#02` | Disk write protected |
| `#03` | Disk not present / drive door open |
| `#04` | Data error (CRC mismatch) |
| `#05` | File not found |
| `#06` | Disk full |
| `#07` | Catalog full (128 files already) |
| `#08` | Directory entry invalid |
| `#09` | Wrong disk (TR-DOS signature not found) |
| `#0A` | File already exists (when saving) |
| `#0B` | Seek error / track 0 not found |
| `#0C` | Drive not ready (timeout) |
| `#0D` | FDC hardware error |
| `#0E` | Read-only file (rare) |
| `#0F` | General error |

A robust TR-DOS-aware program will handle at least `#04`, `#05`, `#06`, and `#07` — these are the errors that can occur during normal operation and which the user might be able to remedy (reinserting the disk, freeing space, etc.).
---

## §7. Programming Patterns

TR-DOS programming shows clear recurring patterns across the Soviet and post-Soviet demoscene. This section documents the three most common ones.

### 7.1 The chained demo loader

The classic Soviet megademo loader is a tight loop that:

1. Reads the next filename from a fixed table.
2. Calls `trdos_load` to bring the part into a swap area.
3. Jumps to the part's entry point.
4. The part runs, eventually returns to the loader.
5. Repeat.

A minimal implementation:

```z80
        ORG #6000

file_table:
        DB  "PART1   C", 0        ; filename + terminator
        DW  part_swap_area         ; load address
        DW  part_entry
        DB  "PART2   C", 0
        DW  part_swap_area
        DW  part_entry
        DB  0                     ; end of table

loader_loop:
        LD   HL,file_table
loader_next:
        LD   A,(HL)
        OR   A
        JR   Z,loader_done        ; end of table
        ; copy filename into our 9-byte buffer
        LD   DE,fname_buf
        LD   BC,9
        LDIR
        ; advance the table pointer past filename, terminator, two DWs
        ; ... (omitted for brevity) ...
        ; call TR-DOS
        LD   HL,fname_buf
        LD   DE,(load_addr)
        CALL trdos_load
        JR   NC,load_error
        ; jump to the part
        LD   HL,(entry_addr)
        JP   (HL)
        ; the part returns here when it's done
        JR   loader_next

loader_done:
        RET
```

This pattern, or something very like it, is the loader for essentially every Soviet megademo from 1994 onward. The `trdos_load` routine is the one from §6.3. Modern frameworks (see [../07_demoscene/demo_frameworks.md](../07_demoscene/demo_frameworks.md)) wrap this in a much more sophisticated shell that handles music synchronization, effect transitions, and memory bank switching.

### 7.2 The streaming part

For demos with parts larger than available RAM (notably the "video demos" of 2001–2005, see [../07_demoscene/notable_demos.md](../07_demoscene/notable_demos.md) §5), the loader streams data from disk directly into the active effect's working memory. A typical sequence:

1. The effect initialises itself in the upper RAM.
2. The framework sets up an interrupt that fires on every other video frame (25 Hz).
3. On each interrupt tick, the framework calls `READ_SECTOR` to load one new sector of streaming data into a buffer.
4. The effect consumes the data from the buffer at its own pace.

This pattern requires careful timing. `READ_SECTOR` takes about 120 ms when seeking, which is more than two video frames (40 ms each at 50 Hz). The framework must overlap the seek with effect work, or pre-seek to the right track during a quiet moment.

The "TS-Config" disk-streaming system on the ZX Evolution hardware was the apotheosis of this pattern, achieving effective data rates of 30+ KB/s by combining hardware-assisted bank switching with TR-DOS reads.

### 7.3 The save-on-exit pattern

Disk magazines and interactive programs need to save user state — high scores, settings, partial work — back to disk. The save pattern:

```z80
save_state:
        ; Build the filename in our buffer
        LD   HL,state_name         ; "STATE   C" — 9 bytes
        LD   DE,fname_buf
        LD   BC,9
        LDIR
        
        ; If a previous state file exists, delete it first
        LD   HL,fname_buf
        CALL trdos_find            ; §6.5
        JR   NC,do_save            ; not found: safe to write
        LD   HL,fname_buf
        CALL trdos_delete          ; found: delete old version first
        
do_save:
        LD   HL,fname_buf
        LD   DE,state_area         ; source address
        LD   BC,state_length       ; byte length
        LD   B,#05                  ; hook code: WRITE_FILE
        ; ... standard pre-call boilerplate ...
        CALL #3D13
        ; ... post-call cleanup ...
        RET
```

The `delete-then-write` sequence is mandatory: TR-DOS's `WRITE_FILE` will fail with error `#0A` ("file already exists") if you try to save over an existing file without first deleting it.

### 7.4 Cross-bank loading

On a 128K or Pentagon-128, loading data into a non-active RAM bank requires an extra step. The caller must:

1. Disable interrupts.
2. Page the target bank into `#C000`–`#FFFF`.
3. Issue the TR-DOS load with `DE` pointing into `#C000`-range.
4. Restore the original bank.
5. Re-enable interrupts.

The catch: TR-DOS uses `#C000`-range as its own workspace during the call. So **you cannot load data directly into bank 0** (TR-DOS's workspace bank). To populate bank 0 with data, you must load into a temporary buffer in another bank first, then memcpy the data into bank 0 after restoring the TR-DOS workspace.

This sounds more complicated than it is — the pattern is well-rehearsed and appears in countless demos. But it is a footgun that has wasted many an hour of demoscene debugging.

---

## §8. Quirks, Traps, and Compatibility

TR-DOS is generally well-behaved, but it has accumulated a folklore of "gotchas" over its decades of use. This section collects the most important ones.

### 8.1 TR-DOS clobbers the screen on error

When TR-DOS encounters an error during a hook-code call, it does not simply return with the carry flag reset. In versions 5.00–5.03, **it prints an error message to the screen at the current cursor position** before returning. This is a legacy of TR-DOS's BASIC-level origins: errors during `*LOAD` are supposed to be visible to the user.

For machine-code programs that hold the screen in a known state (a running demo, a game), this is a disaster. The cure is to **suppress error printing** by setting a specific byte in TR-DOS's workspace area before the call:

```z80
LD   HL,#5CF6           ; TR-DOS error-suppression byte
LD   (HL),#FF           ; #FF = suppress printing, #00 = print (default)
```

With this byte set to `#FF`, TR-DOS will silently return the error code in A without printing anything. Every serious TR-DOS-aware program sets this byte once at startup.

### 8.2 The 9th filename byte is mandatory

The TR-DOS filename is **exactly 9 bytes**: 8 characters of name plus 1 character of extension. There is no null terminator. If you build a filename buffer that is only 8 bytes long (forgetting the extension), TR-DOS will read the 9th byte from whatever memory happens to follow, with unpredictable results.

The cure: always declare filename buffers as 9 bytes, and always LDIR exactly 9 bytes from your source string. The Soviet convention is to use space characters (`#20`) for padding inside the 8-character name portion.

### 8.3 Interrupts must be off during calls

TR-DOS routines use the Z80's IM1 interrupt for internal timing (specifically, the motor-on timeout). If your program has set up its own IM2 vector table, or if your IM1 ISR does anything other than the standard ROM keyboard scan, **TR-DOS calls will fail unpredictably**.

The cure is the standard `DI`/`EI` pattern shown in §6.6. Always.

### 8.4 TR-DOS uses some of your system variables

TR-DOS uses a handful of bytes in the system variables area for its own state. The most important ones:

| Address | Name | Used by TR-DOS for |
|---|---|---|
| `#5CF6` | (no standard name) | Error printing suppression flag |
| `#5CF7`–`#5CF8` | `TRDOS_DRV` | Current drive selection |
| `#5CF9` | `TRDOS_PTR` | Current catalog scan pointer |
| `#5CFA`–`#5CFB` | `TRDOS_LEN` | Remaining bytes in current operation |

These are in the otherwise-reserved range `#5CB6`–`#5CCF`. If your program writes to these bytes for its own purposes, TR-DOS will malfunction. The cure is simply to leave them alone.

### 8.5 Cross-version compatibility

Code written against TR-DOS 5.03 will, with two exceptions, run on every other TR-DOS version:

- **TR-DOS 5.00**: the `READ_CAT_ENTRY` hook code returns slightly different field offsets. Code that walks the catalog should use `SCAN_CAT` instead, which is stable.
- **TR-DOS 6.x (Scorpion only)**: hook codes `#09`-`#0F` exist for Scorpion-specific features. Code that uses them will fail on a Pentagon.

The reverse — code written for 5.00 running on 5.03 — is universally safe. If you target TR-DOS 5.03, you have effectively targeted every Beta-compatible Soviet machine.

### 8.6 TR-DOS and 128K BASIC

A subtle point: when TR-DOS is installed, the 128K editor ROM is patched to recognize the `*` prefix and dispatch to TR-DOS commands. This patch is applied by TR-DOS at boot time and is invisible to the user. However, if you boot a 128K Spectrum without a TR-DOS disk in the drive, the patch is not applied — and `*` commands will not work in the editor.

This is rarely a problem in practice (a Pentagon without TR-DOS is like a fish without water), but it confuses users of modern emulators who boot a 128K machine, type `*CAT`, and see an error.

### 8.7 Disk image quirks in emulators

Modern emulators (Unreal Speccy, ZEsarUX, Fuse, etc.) implement TR-DOS via `.TRD` images. A few quirks to be aware of:

- Some `.TRD` images in circulation are smaller than the canonical 655,360 bytes — they are truncated dumps of single-sided disks, or partial dumps. Emulators generally handle this gracefully by zero-padding.
- Some `.TRD` images were created from disks with non-standard geometries (40 tracks, single-sided, 9 sectors per track). TR-DOS 5.03 will report errors when accessing such disks, but the catalog will still read.
- The `.TRD` format has no formal specification; the de facto standard is "whatever Unreal Speccy writes". A few variants exist (`.FDI`, a more flexible container with embedded geometry metadata) but `.TRD` is by far the most common.

For new software, write to standard 640 KB `.TRD` images and you will not go wrong.
---

## §9. Modern Status and Tools

TR-DOS is not a dead format. The Soviet Spectrum scene still produces new software, and the global emulation scene relies on TR-DOS as the canonical archive format for Soviet-era software. The tools and workflows of 2024 are quite different from those of 1991, but the underlying format is unchanged.

### 9.1 Cross-platform command-line tools

The most widely-used modern TR-DOS tool is **`trdtool`**, a small command-line utility available for Linux, macOS, and Windows. It can:

- Create, read, and write `.TRD` images.
- List catalogs, extract files, inject files.
- Format empty images and check geometry.

Typical usage:

```bash
$ trdtool ls demo.trd
 NAME     EXT    SIZE SECT T  S
 LOADER   B      1234    5  0  9
 PART1    C     16384   64  1  1
 PART2    C     32768  128  5  1
 PIC      #      6912   27 16  1

$ trdtool extract demo.trd PART1.C
$ ls -l PART1.C
-rw-r--r--  1 user  staff  16384 Jul 17 16:00 PART1.C
```

Equivalent tools exist in Python (`trd.py`, embedded in many disk-image libraries), in Rust, and in JavaScript (for browser-based viewers). The format is simple enough that a complete reader is a 50-line program in any modern language.

### 9.2 Emulator support

Every major Spectrum emulator implements TR-DOS via `.TRD` images:

- **Unreal Speccy** (Russian, Windows): the canonical Soviet-era emulator. Its `.TRD` writer is the de facto format standard.
- **ZEsarUX** (Spanish, cross-platform): full TR-DOS support, including custom hook-code interception for debugging.
- **Fuse** (cross-platform, GTK/Qt): TR-DOS supported via the "Beta 128" interface option, enabled by default when a `.TRD` is inserted.
- **Speccy** (Marat Fayzullin, multi-platform): TR-DOS support, though less commonly used than Fuse or ZEsarUX.
- **ESXESP / DivESP** (DivMMC firmware emulators): TR-DOS compatibility via DivIDE emulation.

When writing TR-DOS-aware code, test in **Unreal Speccy** for compatibility with Soviet software conventions and in **ZEsarUX** for debugging (its hook-code call logging is invaluable).

### 9.3 Real-hardware options

Running TR-DOS on real Spectrum hardware in 2024 requires one of:

- **A real Pentagon or Scorpion** with a working 5.25" floppy drive. Increasingly rare; the drives themselves are the failure point.
- **A modern interface that emulates the Beta 128**: the DivIDE, DivMMC, or ZXMAX. These use CF/SD cards formatted as `.TRD` images and present them to the Spectrum as if they were real floppy disks.
- **A modern FPGA clone** (Turbo Chameleon, MiST, MiSTer, ZX Spectrum Next): these typically include Beta 128 emulation in their Spectrum core, with `.TRD` images loaded directly from SD card.

The `.TRD`-on-SD-card workflow has largely replaced real floppy disks in the modern scene. A party entry shipped on `.TRD` will run on a real Pentagon with a floppy, on a real Pentagon with a DivMMC, on an FPGA clone, or in any emulator.

### 9.4 The format's longevity

Why does TR-DOS remain current almost 40 years after its creation? Three reasons:

1. **Installed base.** Thousands of Soviet demos, diskmags, and games are archived in `.TRD` form. Any new format would orphan this corpus.
2. **Simplicity.** The `.TRD` format has no metadata, no header, no compression. It can be inspected with a hex editor, parsed in 50 lines of any language, and produced by a trivial tool.
3. **Demoscene continuity.** The modern Russian scene — Forever party, DiHalt, Chaos Constructions — still runs on TR-DOS-compatible setups. New productions continue to ship as `.TRD`.

This continuity is a rare thing in computing. Most 8-bit disk formats (Commodore 1541, Atari 810, Apple DOS 3.3) survive only as emulator-only artifacts. TR-DOS, by contrast, is still a "live" format with active production.

---

## §10. Cross-References

### 10.1 Within the Operating Systems section

- [README.md](README.md) — section index
- [rom_48k.md](rom_48k.md) — the 48K BASIC ROM, which TR-DOS displaces at `#0000`–`#3FFF` when paged in
- [rom_128k.md](rom_128k.md) — the 128K editor ROM, which TR-DOS patches to recognize `*` commands
- [system_variables.md](system_variables.md) — the system variable area at `#5C00`-range; TR-DOS uses some of the reserved bytes
- [plus3dos.md](plus3dos.md) — the Western alternative to TR-DOS, used on the Amstrad +3
- [esxdos.md](esxdos.md) — the modern DivIDE/DivMMC OS that coexists with TR-DOS compatibility
- [nextzxos.md](nextzxos.md) — the ZX Spectrum Next's OS, which provides its own disk access
- [is_dos.md](is_dos.md), [nedo_dos.md](nedo_dos.md) — Soviet/Russian alternatives to TR-DOS

### 10.2 Outside the section

- [../02_hardware/clones/README.md](../02_hardware/clones/README.md) — Pentagon and other Soviet clones (hardware context)
- [../05_development/03_memory_and_io/memory_and_io_pentagon.md](../05_development/03_memory_and_io/memory_and_io_pentagon.md) — Pentagon memory map and I/O ports, including Beta 128
- [../07_demoscene/demo_frameworks.md](../07_demoscene/demo_frameworks.md) §5 — how megademos use TR-DOS for part loading and disk streaming
- [../07_demoscene/notable_demos.md](../07_demoscene/notable_demos.md) §5.6 — TS-Config disk streaming on the ZX Evolution
- [../07_demoscene/soviet_demo_scene.md](../07_demoscene/soviet_demo_scene.md) — the Soviet scene that standardized on TR-DOS
- [../08_reverse_engineering/README.md](../08_reverse_engineering/README.md) — disk-based copy protection schemes (which used TR-DOS direct sector I/O)

### 10.3 External resources

- **`trdtool` source**: https://github.com/sprinter98/trdtool
- **[Unreal Speccy](https://sdkcad.free.fr/) emulator**: https://spectrum.lovelyish.com/
- **[ZEsarUX](https://github.com/chernandezba/zesarux)**: https://github.com/chernandezba/zesarux
- **ZX Spectrum Wiki on TR-DOS**: https://sinclair.wiki.zx/tr-dos
- **`trd.py` (Python TR-DOS library)**: bundled in many disk image tools; a clean reference implementation lives in the [ZEsarUX](https://github.com/chernandezba/zesarux) source tree
- **The Pentagon hardware reference** (Russian): various docs in the `zx-pk.ru` and `speccy.info` archives
- **Forever party archive** (live `.TRD` submissions from 1996 onwards): https://forever.zeroteam.sk

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/). Attribute as "TR-DOS — The Soviet Disk Standard, from the ZX Spectrum Knowledge Base".
