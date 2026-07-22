[← Home](../README.md) · [Operating Systems](README.md)

# +3 DOS — The Amstrad Disk Standard

The third Western attempt at giving the Spectrum disk storage — after Sinclair's aborted microdrive interface and the read-only ZX Interface 2 ROM cartridges — was the **+3 DOS**, shipped with the Amstrad-manufactured ZX Spectrum +3 in December 1987. Built on technology Amstrad had developed for its CPC range, +3 DOS was a CP/M-compatible operating system with a BASIC-level command set and a robust assembly API.

+3 DOS is significant for several reasons. It was the **only DOS ever shipped as standard on a Sinclair-branded Spectrum** — the +3 was the first model to include a disk drive from the factory. It was the first Spectrum OS to support a hierarchical filesystem. And it provided the formal **Resident System Extension (RSX)** mechanism that allowed BASIC and machine code to be extended in a structured way — a mechanism later borrowed by other Spectrum DOSes.

But +3 DOS is also significant for what it did *not* achieve. Its drives used the proprietary Hitachi 3-inch disk format, which never achieved the ubiquity of 5.25" or 3.5" media. It was incompatible with the Beta 128 / TR-DOS ecosystem that was about to dominate the Soviet market. And it was widely perceived as slow compared to cassette turbo loaders. By 1990, the +3 had been discontinued in the West, and +3 DOS survived primarily as a hobbyist curiosity.

This article covers +3 DOS as a system: the +3 hardware it sits on, its memory model, the BASIC command set, the file system, the RSX-based assembly API, the CP/M compatibility, and the quirks and modern status. For TR-DOS — the Soviet alternative that won the market — see [trdos.md](trdos.md). For ESXDOS — the modern alternative — see [esxdos.md](esxdos.md).

---

## Roadmap

1. **What +3 DOS is** — history, scope, why it both succeeded and failed
2. **The +3 disk subsystem** — Hitachi 3-inch drive, UPD765 FDC, gate array
3. **Memory layout** — the four paging modes, where DOS lives
4. **The BASIC command set** — the DOS-specific keywords added to +3 BASIC
5. **The file system** — CP/M-style user numbers, directories, allocation
6. **The RSX assembly API** — Resident System Extensions, function catalogue
7. **CP/M compatibility** — booting CP/M 2.2 from a +3
8. **Quirks, traps, and modern status** — what survives today
9. **Cross-references** — where to go next

---

## §1. What +3 DOS Is

### 1.1 Origins

When Amstrad purchased the rights to the Sinclair Spectrum range from Sinclair Research in 1986, the company immediately began modernising it. The first Amstrad-produced machine was the +2 (April 1987): a +2 (grey case) machine with a built-in cassette drive, essentially a 128K Spectrum in a CPC-style case. The +3 (December 1987) went further: it replaced the cassette drive with a 3-inch floppy disk drive, added 64 KB of ROM (taking the total to 128 KB), and shipped a disk operating system based on Amstrad's CPC +3 DOS code.

Amstrad had been making CP/M-compatible microcomputers since the CPC 464 in 1984. The CPC's disk operating system — also called +3 DOS or AMSDOS depending on context — was a derivative of the CP/M BDOS (Basic Disk Operating System), the file-handling layer of Digital Research's CP/M operating system. When Amstrad needed a DOS for the Spectrum +3, porting this code was the obvious path: it was proven, it was small enough to fit in the +3's extra ROM, and it preserved compatibility with the existing Amstrad software ecosystem.

The result was a DOS that was sophisticated by Spectrum standards — a hierarchical filesystem, a structured file handle model, and the ability to run actual CP/M programs — but tied to hardware that would prove increasingly exotic.

### 1.2 What +3 DOS actually was

+3 DOS is a 16 KB ROM image that occupies one half of the +3's 64 KB total ROM. The ROM is banked into the Z80's address space on demand, replacing either the BASIC ROM or the editor ROM depending on the operation. From the user's perspective, +3 DOS appears as:

- **A set of BASIC keywords** added to the +3's BASIC dialect (`CAT`, `LOAD`, `SAVE`, `ERASE`, `MOVE`, `FORMAT`, `COPY`, etc.).
- **An assembly-level API** accessed via the Resident System Extension (RSX) mechanism.
- **A CP/M compatibility layer** that can boot actual CP/M 2.2 programs.
- **A file system** stored on 3-inch floppy disks in a CP/M-derived format.

From the perspective of anyone using a +2A or +3 in the late 1980s, +3 DOS was simply "what the disk drive runs". From the perspective of a modern emulator, +3 DOS is the contents of the `.DSK` disk images that hold +3 software.

### 1.3 Why +3 DOS did not dominate

Three reasons:

1. **The +3 itself was a commercial disappointment.** Sales were modest, the price was high, and the disk format was non-standard. By 1990, Amstrad had discontinued the +3 in favour of the +2A (a +3 with the disk drive removed and the price halved).

2. **The 3-inch disk format was orphaned.** Hitachi's 3-inch floppy — distinct from the 3.5-inch floppy that won the market — was used only by Amstrad, some MSX machines, and a few obscure home computers. By 1990, blank 3-inch disks were expensive and hard to find.

3. **The Soviet scene chose TR-DOS.** While Western users were booting +3 DOS, the Soviet scene was building the Pentagon + Beta 128 + TR-DOS ecosystem that would dominate by 1990. TR-DOS used standard 5.25" floppies and was substantially faster. The two ecosystems never really intersected.

The result is that +3 DOS is the **standard DOS for a small slice of original Western Spectrum hardware** but is essentially absent from the demoscene, the Soviet world, or modern hardware. It is a respected curiosity — important for historical reasons, but no longer a platform for active development.

### 1.4 Where +3 DOS is still relevant

Despite its niche status, +3 DOS matters for:

- **Owners of real +3 or +2A hardware** in 2024. +3 DOS is the only way to use the built-in disk drive on these machines.
- **Emulator users running +3 software.** Many commercial Spectrum games from 1987–1990 shipped on +3 disks. Emulators load `.DSK` images.
- **Students of Spectrum OS history.** +3 DOS is the only "professional" Spectrum DOS from the original era — its RSX mechanism is more sophisticated than anything in TR-DOS or ESXDOS.
- **CP/M enthusiasts.** The +3 is one of the cheapest and easiest ways to run actual CP/M 2.2 software on real Z80 hardware.

---

## §2. The +3 Disk Subsystem

+3 DOS exists to drive the +3's disk hardware. Understanding the hardware is essential for anyone using +3 DOS, debugging it, or implementing an emulator.

### 2.1 The Hitachi 3-inch drive

The +3 contains a single **Hitachi 3-inch floppy disk drive** — a unit almost unique in microcomputing history. The 3-inch disk (sometimes called a "compact floppy") was developed by Hitachi in the early 1980s as a smaller alternative to the 5.25-inch floppy. It was used in:

- The Amstrad CPC 664 and 6128 (1985–1986).
- The Amstrad PCW 8256, 8512, 9512, and their successors.
- The Sinclair Spectrum +3 (1987) and +2A/+3 ROM variants.
- A few obscure MSX models.

It was *not* used in IBM PCs, Apple IIs, or the dominant home computers of the era. By 1990, the 3.5-inch floppy had won the format war, and the Hitachi 3-inch was on its way to obsolescence.

The 3-inch disk physical specifications:

| Parameter | Value |
|---|---|
| Disk diameter | 3 inches (76 mm) |
| Cartridge size | 90 mm × 94 mm × 3.3 mm |
| Recording mode | MFM (double density) |
| Tracks per side | 40 |
| Sectors per track | 9 |
| Bytes per sector | 512 |
| Sides | 1 (single-sided, +3 default) or 2 (double-sided, CPC-style) |
| Total capacity | 180 KB (single-sided) or 720 KB (double-sided) |

The +3 supports both single-sided 180 KB and double-sided 720 KB disks, although the bundled drive mechanism is single-sided. Users wanting 720 KB capacity had to either fit a third-party double-sided drive or modify the +3's drive cable — neither was common.

### 2.2 The UPD765 floppy disk controller

The +3's floppy disk controller is a **NEC UPD765** (or its many equivalents — Intel 8272A, Siemens SAB1797, etc.). The UPD765 is a more sophisticated chip than the WD1793 used in the Beta 128: it supports multiple density modes, DMA-driven transfers, and a richer command set.

Key UPD765 features used by the +3:

- **Data rates**: 250 kbit/s (double density, the only mode +3 DOS uses).
- **Track register**: automatically maintained by the FDC, not the host CPU.
- **DMA mode**: the FDC can transfer data directly to/from RAM via an external DMA controller. The +3 uses pseudo-DMA — the gate array polls the FDC's data register and reads/writes bytes one at a time, achieving approximately the same effect.
- **Multi-sector transfers**: a single command can read or write multiple consecutive sectors, reducing CPU overhead.

The UPD765 is accessed via four I/O ports:

| Port | Read | Write | Purpose |
|---|---|---|---|
| `#FB` | — | FDC command byte | Send a command to the FDC |
| `#FB` | Main status | — | Read FDC status (busy, data ready, etc.) |
| `#F9` | Data register | Data register | Read/write data bytes during transfers |
| `#FF` | — | Drive control | Drive select, motor, side, density |

A complete FDC command sequence involves sending a command byte (`#FB`), followed by 1–8 parameter bytes, then waiting for the FDC to assert an interrupt. The result phase reads 0–7 status bytes back. This is significantly more complex than the WD1793's simple register model, but it allows for more sophisticated operations.

### 2.3 The Amstrad gate array

The disk subsystem is glued together by a custom **Amstrad gate array** — an ASIC that handles bank switching, the pseudo-DMA for the FDC, the disk motor control, and the +3's other hardware-specific features. The gate array is not documented in as much detail as the original Ferranti ULA, but it is the reason the +3's memory model is so different from earlier Spectrums.

From the +3 DOS's perspective, the gate array is invisible: it accesses the disk only through the FDC ports. But from the perspective of anyone implementing a +3 emulator or repairing a real +3, the gate array is the single most important and least-understood component.

### 2.4 Disk image formats

Modern emulators represent +3 disks as `.DSK` images. The `.DSK` format is the **Amstrad disk image format**, originally used by the Amstrad CPC emulators and adopted by the Spectrum community for +3 support. A `.DSK` file contains:

- A 256-byte header identifying the format.
- Per-track headers describing the track geometry.
- The actual sector data, in the order it appears on the disk.

The `.DSK` format is more sophisticated than TR-DOS's `.TRD` (which is just a raw sector dump): it can represent non-standard track geometries, weak sectors, and other copy-protection tricks. Most commercial +3 disks use the standard format and are accurately preserved as `.DSK` images.

The +3 disk drives, despite using the orphaned 3-inch format, are well-supported by modern emulators (Fuse, ZEsarUX, Spectaculator, etc.). A user with real +3 hardware in 2024 typically transfers disks to/from a modern PC by either:

- Removing the 3-inch drive and replacing it with a Gotek or HxC floppy emulator that mounts `.DSK` images from a USB stick.
- Using a special cable to read 3-inch disks directly on a PC with appropriate hardware.

Both approaches are common; the Gotek mod has largely replaced the original drive in surviving +3 hardware.
---

## §3. Memory Layout

The +3's memory model is the most complex of any original Sinclair Spectrum — substantially more so than the 128K. This is because the +3 has 128 KB of ROM (vs. the 128K's 32 KB) and uses a different paging scheme with four distinct modes.

### 3.1 The four paging modes

The +3 uses a port at `#1FFD` to select between four **paging modes**. Combined with the standard 128K `#7FFD` port, this gives the +3 its distinctive memory architecture:

| Mode | `#1FFD` bits 4–3 | `#0000`–`#3FFF` | `#4000`–`#7FFF` | `#8000`–`#BFFF` | `#C000`–`#FFFF` |
|---|---|---|---|---|---|
| 0 (128K mode) | `00` | ROM 0 (128K editor) or ROM 1 (48K) | RAM bank 5 | RAM bank 2 | RAM bank 0–7 (via `#7FFD`) |
| 1 (special) | `01` | RAM bank 0 | RAM bank 1 | RAM bank 2 | RAM bank 3 |
| 2 (RAM disk) | `10` | RAM bank 4 (page 4 of RAM disk) | RAM bank 5 | RAM bank 6 | RAM bank 7 |
| 3 (Plus 3 mode) | `11` | RAM bank 4 | RAM bank 5 | RAM bank 6 | RAM bank 7 |

- **Mode 0** is the standard 128K-compatible mode. This is what most software uses.
- **Mode 1** is a special mode used to access the four "extra" RAM banks (0–3) simultaneously. Used for cross-bank data transfers.
- **Mode 2** is the RAM disk mode, used by +3 DOS itself for its workspace.
- **Mode 3** is the "Plus 3 mode" used by some special-purpose software; it puts the same banks in all four slots.

The +3's extra ROM — containing the +3 DOS code and the +3's enhanced editor — is banked into the `#0000`–`#3FFF` slot via a separate mechanism. There are effectively **four ROM pages**:

- ROM 0: the 128K editor ROM (modified for +3 hardware).
- ROM 1: the original 48K BASIC ROM (for backwards compatibility).
- ROM 2: the +3's DOS and disk routines.
- ROM 3: the 48K BASIC ROM with patches for +2A/+3 hardware differences.

A fifth "ROM" page is actually the RAM disk — when bank 4 is paged in via `#1FFD`, the address space behaves as if it were ROM but actually contains RAM.

### 3.2 Where +3 DOS lives

+3 DOS occupies **ROM pages 2 and 3** (the third 16 KB and the fourth 16 KB of the +3's 64 KB ROM total). It is paged into the address space on demand:

- When a +3 DOS BASIC command is executed (`CAT`, `LOAD`, etc.), the editor ROM temporarily pages in ROM 2 to handle the call.
- When a CP/M program is booted, ROM 3 (the patched 48K ROM) takes over as the boot environment.
- When assembly code calls a +3 DOS routine directly, the caller must page in ROM 2 explicitly via the `#1FFD`/`#7FFD` ports.

The DOS workspace lives in **RAM bank 0** (in the +3's RAM disk mode, mode 2). This bank is normally invisible to user programs — it is accessed only when the +3 pages itself into mode 2 during DOS operations.

### 3.3 Backwards compatibility

Despite its complexity, the +3's memory model is designed to be backwards-compatible with the 128K and 48K:

- A program that uses only 128K-compatible `#7FFD` paging will work on the +3 unchanged, as long as it doesn't try to write to `#1FFD`.
- A program that uses only the 48K memory layout (no paging at all) will work on the +3 unchanged.

The catch is that +3 DOS itself uses the more complex modes. A program that wants to call +3 DOS functions must understand and respect the four-mode paging — a non-trivial requirement.

### 3.4 The RAM disk

The +3's 128 KB of RAM is normally split between the visible 128 KB (banks 0–7) and the RAM disk (banks 0–3 in mode 2). The RAM disk appears to the user as a high-speed storage device, accessed via the `*` and `MOVE` BASIC commands. Files can be copied from floppy to RAM disk for fast repeated access, or stored on RAM disk for the duration of a session.

The RAM disk's contents are lost when the +3 is reset or powered off. It is essentially a 64 KB scratch space for transient files — useful, but not a substitute for the floppy disk.

---

## §4. The BASIC Command Set

+3 DOS adds a set of BASIC keywords to the +3's BASIC dialect. Unlike TR-DOS's `*`-prefixed commands, +3 DOS keywords are full tokens in the BASIC language, parsed by the editor ROM.

### 4.1 File operations

| Command | Purpose | Example |
|---|---|---|
| `FORMAT` | Initialise a blank disk | `FORMAT "A:"` |
| `CAT` | Display the disk catalog | `CAT` |
| `LOAD` | Load any file by name | `LOAD *"game" CODE` |
| `SAVE` | Save a memory block to disk | `SAVE *"game" CODE 16384,6912` |
| `VERIFY` | Verify a file against memory | `VERIFY *"game" CODE 16384,6912` |
| `MERGE` | Merge a BASIC file | `MERGE *"lib"` |
| `ERASE` | Delete a file | `ERASE "game"` |
| `MOVE` | Copy or move a file | `MOVE "old" TO "new"` |
| `COPY` | Copy entire disk (single-drive) | `COPY` |

The `*` after the command indicates a disk operation (rather than a cassette one). Without the `*`, the same commands operate on cassette tape.

### 4.2 Filename syntax

+3 DOS filenames are:

- **8 characters of name** + **1 character of type** (no extension separator). Example: `MYFILE  C` (the space and `C` form the type).
- Or, with an explicit type separator: `MYFILE:C`.
- Optionally preceded by a drive letter: `A:MYFILE:C`.

Standard types:

| Type letter | Meaning |
|---|---|
| (space) | BASIC program |
| `B` | BASIC program (alternative) |
| `C` | Code (raw memory block) |
| `D` | Data array |
| `M` | Mixed (rarely used) |
| `P` | Code marked as a program |
| `S` | Screen dump (`#4000`–`#5AFF`, 6912 bytes) |

### 4.3 Example session

A complete +3 BASIC session that loads and runs a game:

```
LOAD *"game" CODE
RANDOMIZE USR 25000
```

Or to view the disk catalog:

```
CAT
```

The disk catalog is displayed as a numbered list:

```
1 GAME     C  32768
2 LOADER   C   1024
3 PIC      S   6912
```

Files are referenced either by name (`"game"`) or by catalog number (`1`).

### 4.4 Stream I/O

+3 DOS also adds **stream I/O** to BASIC. A program can open a file as a stream and read/write characters one at a time:

```
10 OPEN #4, "A:DATA", INPUT
20 LINE INPUT #4, A$
30 CLOSE #4
```

This is a significant step up from TR-DOS, which only supports whole-file operations. With +3 DOS, a program can read a text file line by line without loading it all into memory at once.

Stream I/O is the foundation of the RSX-based assembly API (see §6): every file is fundamentally a stream of bytes that can be read or written one at a time.

---

## §5. The File System

+3 DOS uses a **CP/M-derived filesystem** with a hierarchical structure — a significant step up from TR-DOS's flat directory.

### 5.1 Disk geometry

The standard +3 disk (single-sided, 80-track, double-density) is laid out as:

- **40 tracks per side** (numbered 0 to 39).
- **9 sectors per track** (numbered 1 to 9).
- **1 side** (the +3's standard drive is single-sided).
- **512 bytes per sector.**

Total: 40 × 9 × 1 × 512 = **180 KB**.

The first two tracks (tracks 0 and 1) hold the **directory** and the **file allocation table** (a bitmap of free sectors). The remaining 38 tracks (tracks 2–39) hold file data. Each file occupies a linked list of 1 KB allocation blocks (two sectors each).

### 5.2 Directory entries

A directory entry is **32 bytes**:

| Offset | Size | Field |
|---|---|---|
| `+0` | 1 | User number (0–15) |
| `+1` | 8 | Filename (space-padded) |
| `+9` | 3 | Filetype (3 characters, space-padded) |
| `+12` | 1 | Extent number (high) |
| `+13` | 2 | Reserved |
| `+15` | 1 | Extent number (low) |
| `+16` | 16 | Block allocation map (16 × 1-byte block numbers) |
| `+28` | 1 | Records in this extent (1 record = 128 bytes) |
| `+29` | 3 | Reserved |

This is the standard CP/M directory entry format. Files larger than 16 KB occupy multiple directory entries (called **extents**), each pointing to up to 16 KB of file data.

### 5.3 User numbers

The first byte of each directory entry is a **user number** (0–15). This is a CP/M feature: the disk is logically divided into 16 user areas, and files in different user areas are invisible to each other. A program operating in user area 0 sees only user-0 files; switching to user area 1 reveals a different set.

The +3 BASIC `CAT` command always shows the current user area (default 0). The `USER` keyword can switch user areas: `USER 5`. This is a primitive form of hierarchical directory support, borrowed directly from CP/M.

Modern CP/M-compatible disks typically use only user area 0; the multi-user feature is rarely exercised.

### 5.4 File types

CP/M filenames use an 8+3 convention (8 characters of name, 3 of extension). The +3 DOS simplifies this to 8+1 — only one character of type — because the BASIC convention is a single type letter (see §4.2). Internally, however, the on-disk format supports full CP/M 8+3 names.

When a +3 DOS disk is read by an actual CP/M program (e.g., booted CP/M 2.2), files appear with full 8+3 names. The +3 BASIC convention is a UI simplification layered on top of the CP/M format.

### 5.5 Free space and fragmentation

The disk's free space is tracked in a **bitmap** in the directory tracks. Each bit represents one 1 KB allocation block; set bits are free, cleared bits are allocated. The +3 DOS scan for free space is linear over this bitmap.

Files are stored in allocation blocks that need not be contiguous — CP/M's directory entry format links them together via the block map. This means +3 DOS does not suffer from TR-DOS's "consecutive sectors required" limitation. A heavily-used +3 disk can have heavily-fragmented files without any problem, although read performance suffers as the FDC must seek between non-adjacent tracks.

### 5.6 Read-only and system attributes

Each directory entry can have **read-only** and **system** attribute flags set. Read-only files cannot be deleted or modified; system files are hidden from the standard `CAT` listing (but visible with `CAT EXT`).

These attributes are inherited from CP/M. They are rarely used in practice; most +3 disks have all files marked as normal.
---

## §6. The RSX Assembly API

For machine-code programs, +3 DOS provides a structured API via the **Resident System Extension (RSX)** mechanism. RSX is an Amstrad/CPC invention that was carried over to the +3 and remains one of +3 DOS's most distinctive features.

### 6.1 What an RSX is

An RSX is a named, callable subroutine that +3 DOS makes available to other programs. Each RSX has:

- A **name** (1–7 characters, upper-case, no extension).
- An **entry point** in the +3 DOS ROM.
- A **calling convention** (what registers / parameters it expects).

The collection of all RSXs forms +3 DOS's assembly-level API. To call an RSX, a program uses a dispatch routine that resolves the name to an entry point and jumps to it.

This is conceptually similar to ESXDOS's function-dispatch mechanism, but more sophisticated: ESXDOS uses numeric function IDs, while +3 DOS uses **names**. The advantage of names is self-documentation; the disadvantage is slower dispatch (string comparison vs. integer lookup).

### 6.2 Calling an RSX

The standard way to call an RSX is via the **+3 DOS jump table** at the fixed address `#DOS` (literally `#0000` of ROM page 2, which is paged in via `#1FFD` for the call). The most common entry points:

| Address | Function | Purpose |
|---|---|---|
| `#DOS_OPEN` | `DOS_OPEN` | Open a file |
| `#DOS_CLOSE` | `DOS_CLOSE` | Close a file |
| `#DOS_READ` | `DOS_READ` | Read bytes from a file |
| `#DOS_WRITE` | `DOS_WRITE` | Write bytes to a file |
| `#DOS_ABANDON` | `DOS_ABANDON` | Abandon file operation |
| `#DOS_CATALOG` | `DOS_CATALOG` | Read catalog entry |
| `#DOS_DELETE` | `DOS_DELETE` | Delete a file |
| `#DOS_RENAME` | `DOS_RENAME` | Rename a file |
| `#DOS_FREE_SPACE` | `DOS_FREE_SPACE` | Get free disk space |
| `#DOS_FORMAT` | `DOS_FORMAT` | Format a disk |

There are roughly 50 RSXs in the standard +3 DOS API. The +3 DOS manual documents all of them.

### 6.3 Worked example: open and read a file

```z80
; Open "A:DATA" for reading, then read 256 bytes into #8000.

DI
; --- Page in +3 DOS ROM (page 2) at #0000-#3FFF ---
LD   BC,#1FFD
LD   A,(#1FFD_save)         ; save current paging
LD   (save_1FFD),A
LD   A,(ROM_2_paging_byte)  ; the byte that pages in ROM 2
OUT  (C),A

; --- Call DOS_OPEN ---
LD   B,255                   ; open mode: read
LD   HL,fn                   ; pointer to filename string
LD   DE,fileref              ; pointer to a 256-byte "file reference" buffer
CALL #DOS_OPEN
JR   NC,open_error           ; carry set = success

; --- Call DOS_READ ---
LD   IX,(fileref)            ; IX = file reference (handle)
LD   DE,#8000                ; destination address
LD   BC,256                  ; byte count
CALL #DOS_READ
JR   NC,read_error

; --- Call DOS_CLOSE ---
LD   IX,(fileref)
CALL #DOS_CLOSE

; --- Restore paging ---
LD   BC,#1FFD
LD   A,(save_1FFD)
OUT  (C),A
EI
RET

fn:        DB   "A:DATA",0
fileref:   DS   256
save_1FFD: DB   0
```

This pattern — page DOS in, open/read/close, page DOS out — is the universal +3 DOS file-loading idiom.

### 6.4 The file reference

Note the **256-byte "file reference" buffer**. +3 DOS uses a substantial per-open-file state — much more than ESXDOS's 1-byte handle or TR-DOS's bare catalog index. The file reference contains:

- The full filename.
- The current position in the file (in records and bytes).
- The file's catalog entry.
- Buffer space for partial sector reads.
- Status flags.

This is closer to the CP/M `FCB` (File Control Block) model than to modern file descriptors. It is more verbose but gives the caller more control.

The size of the file reference is the reason +3 DOS limits the number of simultaneously-open files to a small number (typically 4–8) — each consumes 256 bytes of RAM.

### 6.5 Stream I/O

Beyond file I/O, +3 DOS exposes the same RSX interface for **streams** — including the screen, keyboard, and printer. The `STREAM_OUT` RSX writes a character to a stream; `STREAM_IN` reads from one. Streams are identified by small integers (`0` = keyboard, `1` = screen, `2` = printer, `3`-up = open files).

This stream abstraction is borrowed directly from CP/M and the Amstrad CPC. It is the foundation of +3 BASIC's `OPEN #4, ...; PRINT #4, ...` syntax.

---

## §7. CP/M Compatibility

One of +3 DOS's most distinctive features is its **CP/M 2.2 compatibility**. The +3 can boot actual CP/M programs from disk, making it a viable CP/M system.

### 7.1 What CP/M is

CP/M (Control Program for Microcomputers) was Digital Research's Z80/8080 operating system, dominant in business microcomputing from 1975 to 1985. CP/M provides:

- A command-line interface (CCP — Console Command Processor).
- A file system (BDOS — Basic Disk Operating System).
- Hardware abstraction via the BIOS (Basic I/O System — note: not the IBM PC BIOS).
- A standard API for application programs.

Thousands of business applications — word processors (WordStar), spreadsheets (SuperCalc), databases (dBase II), programming languages (Microsoft BASIC, Turbo Pascal, MPM) — ran on CP/M.

### 7.2 How the +3 boots CP/M

To boot CP/M on a +3, the user inserts a CP/M system disk and types:

```
LOAD *"CPM",CODE
RANDOMIZE USR 25000
```

This loads the CP/M CCP/BDOS code (typically ~12 KB) into memory and jumps to it. From that point, the +3 is running CP/M, not +3 BASIC. The user sees the CP/M `A>` prompt and can run any CP/M program that fits in the available RAM.

The +3's CP/M BIOS is a custom implementation that translates CP/M BDOS calls into +3 hardware operations. It includes:

- Disk I/O via the +3's UPD765 FDC (treated as a CP/M-compatible disk).
- Keyboard input via the +3's keyboard hardware.
- Screen output to the +3's screen (in a 51-column text mode).
- Printer output via the parallel port.

### 7.3 CP/M programs on the +3

Many CP/M programs run on the +3 with no modification. The +3's CP/M is approximately equivalent to a slightly-older CP/M machine with 56 KB of TPA (Transient Program Area — the RAM available to applications) and a single 180 KB floppy drive.

Compatible CP/M programs include:

- **WordStar 3.0**: the dominant CP/M word processor.
- **SuperCalc**: the dominant CP/M spreadsheet.
- **dBase II**: the original relational-style database.
- **Microsoft BASIC-80**: CP/M Microsoft BASIC (compiler and interpreter).
- **Turbo Pascal 1.x–2.x**: Borland's revolutionary Pascal IDE.
- **Microsoft FORTRAN-80, COBOL-80, etc.**: other CP/M languages.
- **MuLISP, MuSTAR**: AI language implementations for CP/M.
- **Thousands of smaller utilities**: archive tools, terminal programs, editors.

Incompatibilities are mainly:

- Programs that require more than 56 KB of TPA. The +3's RAM is divided between CP/M and the +3's ROM workspace.
- Programs that use non-standard video hardware or terminals.
- Programs that require hard-disk access.

### 7.4 Why this mattered (and matters)

CP/M compatibility was a significant selling point for the +3 in 1987. It positioned the machine as a serious small-business computer — a Spectrum that could run real business software — at a fraction of the price of an IBM PC.

In 2024, CP/M compatibility is primarily of historical interest. A handful of enthusiasts still run CP/M software on real +3 hardware; many more do so under emulation. The +3 remains one of the easiest ways to experience actual 1980s CP/M software without dedicated CP/M hardware.

For more on CP/M as a system — including how it compares to TR-DOS and ESXDOS — see [cpm.md](cpm.md).

### 7.5 The +3 CP/M community

The CP/M-on-Spectrum community is small but persistent. Notable projects:

- **The "+3 CP/M User Group"**: a loose community sharing CP/M software and hardware tips.
- **CP/M emulators for the +3**: modern alternatives that run within +3 DOS rather than replacing it, providing CP/M compatibility without losing +3 BASIC access.
- **The `.DSK` archive of +3 CP/M software**: large collections of bootable CP/M disks for emulators and real hardware.

CP/M is the +3's secret superpower — a capability that no other original Spectrum possesses.
---

## §8. Quirks, Traps, and Modern Status

+3 DOS has accumulated its own folklore of footguns. The most important ones, plus a snapshot of the current state.

### 8.1 The "must not be in mode 2" rule

Many +3 DOS functions assume the machine is in paging mode 0 (standard 128K mode). Calling a +3 DOS function while in mode 2 (RAM disk mode) will corrupt the RAM disk and may crash the machine. Always switch back to mode 0 before calling +3 DOS.

### 8.2 The slow disk

The +3's disk subsystem is **slower than the Beta 128** by a significant margin. Typical transfer rates:

| Operation | +3 DOS | TR-DOS |
|---|---|---|
| Read 1 KB block | 50 ms | 25 ms |
| Seek to new track | 60 ms | 40 ms |
| Full disk catalog read | 800 ms | 200 ms |

The reason is partly the 3-inch drive's slower spin rate (300 RPM vs. 360 RPM on the 5.25"), partly the UPD765's higher per-command overhead, and partly +3 DOS's more elaborate file reference model.

In practice this means a 32 KB game loads from +3 disk in about 1.5 seconds — about three times what a Pentagon/TR-DOS setup would take. Not unusable, but noticeably slower.

### 8.3 The RAM disk reset behaviour

The RAM disk (the +3's 64 KB of "extra" RAM, banks 0–3 in mode 2) is cleared on every reset. A program that stores data on the RAM disk and then triggers a `RANDOMIZE USR 0` (reset) will lose all of it. The cure is to use the RAM disk only for transient data, never for state the user cares about.

### 8.4 The Gotek upgrade

Real +3 hardware in 2024 typically has a **Gotek floppy emulator** replacing the original Hitachi 3-inch drive. The Gotek is a small device that mounts `.DSK` images from a USB stick and presents them to the +3 as if they were real floppies. This is by far the most common +3 hardware modification.

The Gotek requires a small cable modification (the +3's floppy connector is non-standard) and a Gotek firmware that supports `.DSK` format (the most popular is "FlashFloppy" by Keir Fraser, which supports `.DSK`, `.TRD`, `.OPB`, and many other formats).

With a Gotek, a +3 owner can run any of the thousands of preserved +3 disks without ever touching a real 3-inch floppy.

### 8.5 Compatibility with TR-DOS

A common question: can a +3 read TR-DOS disks? The answer is **no, not directly** — the disk formats are physically incompatible (180 KB single-sided vs. 640 KB double-sided), and the file systems are completely different.

However, several software bridges exist:

- **`.DSK` to `.TRD` converters**: cross-platform tools that extract files from one format and write them to the other. These run on a PC.
- **Emulator support**: most emulators can mount both `.DSK` and `.TRD` images, so a user can switch between them at will.
- **Community-migrated archives**: many Soviet demos have been re-released as `.DSK` images for +3 users, and many Western games have been re-released as `.TRD` for Pentagon users.

The two formats serve different communities today; the bridges are convenient but rarely used in earnest.

### 8.6 Modern status

+3 DOS is a frozen system. No new versions have been released since the +3 was discontinued in 1990. The ROM image is what it is. However, the ecosystem around it is alive:

- **The World of Spectrum archive** has thousands of `.DSK` images of +3 software.
- **Modern emulators** (Fuse, ZEsarUX, Spectaculator) all support +3 DOS via `.DSK` images with high fidelity.
- **Real +3 hardware** remains in active use, typically with Gotek upgrades.
- **New software is occasionally released** for the +3, though this is rare compared to the Pentagon/TR-DOS scene.

For new Spectrum software development, +3 DOS is rarely the target of choice. The combination of slow disk access, exotic hardware, and limited audience makes TR-DOS or ESXDOS the more natural platforms.

### 8.7 Where +3 DOS is unmatched

Despite its niche status, +3 DOS has three things no other Spectrum DOS has:

1. **Real CP/M compatibility.** No other original Spectrum can run actual CP/M 2.2 software without significant additional hardware.
2. **The RSX mechanism.** The structured, named-subroutine API is more sophisticated than anything else in the Spectrum DOS world.
3. **A hierarchical filesystem.** The user-number system, primitive as it is, allows multiple "directories" on the same disk — something TR-DOS never offered.

These are historical curiosities today, but they were important design choices in 1987.

---

## §9. Cross-References

### 9.1 Within the Operating Systems section

- [README.md](README.md) — section index
- [trdos.md](trdos.md) — the Soviet alternative; faster, simpler, won the market
- [esxdos.md](esxdos.md) — the modern alternative; compatible with current hardware
- [nextzxos.md](nextzxos.md) — the most powerful modern Spectrum OS
- [cpm.md](cpm.md) — CP/M 2.2 as an OS, with +3 CP/M as one specific port
- [rom_128k.md](rom_128k.md) — the +3's editor ROM is a derivative of the 128K's
- [basic_dialects.md](basic_dialects.md) — +3 BASIC is one of the BASIC dialects documented there

### 9.2 Outside the section

- [../02_hardware/original/README.md](../02_hardware/original/README.md) — original Sinclair hardware including the +3
- [../05_development/03_memory_and_io/memory_and_io_plus3.md](../05_development/03_memory_and_io/memory_and_io_plus3.md) — +3 memory map and I/O ports

### 9.3 External resources

- **The +3 manual**: included as a PDF in most emulator distributions.
- **World of Spectrum archive**: https://worldofspectrum.org/
- **The +3 DOS reference (comp.sys.sinclair FAQ)**: archived at https://worldofspectrum.org/faq/
- **Fuse emulator**: https://fuse-emulator.sourceforge.net/
- **ZEsarUX**: https://github.com/chernandezba/zesarux
- **FlashFloppy (Gotek firmware)**: https://github.com/keirf/FlashFloppy
- **ZX Spectrum Wiki on +3 DOS**: https://sinclair.wiki.zx/+3-dos

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/). Attribute as "+3 DOS — The Amstrad Disk Standard, from the ZX Spectrum Knowledge Base".
