[← Home](../README.md) · [Operating Systems](README.md)

# ESXDOS — The Modern Spectrum Disk OS

If TR-DOS is the Soviet disk standard of the 1980s, ESXDOS is the Western disk standard of the 2010s. Designed by **Dylan Smith** (UK) starting in 2008 for the DivIDE IDE interface, ESXDOS brings FAT16/FAT32 file access, a Unix-flavoured API, and a modern dot-command interface to the unexpanded Spectrum. Anyone using a DivMMC SD-card interface on a real Spectrum today is running ESXDOS or one of its derivatives (residos, NextZXOS).

ESXDOS is a "soft-OS" in a specific sense: it does not replace the BASIC ROM and does not require a custom machine. It is a small (typically 8 KB) piece of firmware that lives on the interface's own ROM, hooks into the Spectrum's NMI button, and provides file I/O services to any machine-code program that cares to call them. From BASIC, the user invokes ESXDOS via `.dot` commands — small programs loaded into RAM and executed — typed directly at the `>` prompt: `*.dir`, `*.load`, `*.tap2trd`, and so on.

This article covers ESXDOS as a system: the DivIDE and DivMMC hardware it sits on, its memory layout, the dot-command interface, the file system, the assembly API, common programming patterns, and the quirks that come with running a modern OS on 1982 hardware. For TR-DOS — the older Soviet disk OS — see [trdos.md](trdos.md). For the ZX Spectrum Next's derivative, see [nextzxos.md](nextzxos.md).

---

## Roadmap

1. **What ESXDOS is** — origins, design goals, why it supplanted earlier attempts
2. **The DivIDE and DivMMC hardware** — IDE / SD interfaces that host ESXDOS
3. **Memory layout** — where the firmware lives, where dot commands run
4. **Dot commands** — the BASIC-level interface, syntax, common commands
5. **Filesystem** — FAT16/FAT32, long filenames, directory layout
6. **The assembly API** — function dispatch, file I/O calls, error model
7. **Programming patterns** — loading files, NMI handlers, snapshotting
8. **Quirks and traps** — what catches newcomers
9. **Modern status and derivatives** — residos, NextZXOS, the ESXDOS ecosystem in 2024
10. **Cross-references** — where to go next

---

## §1. What ESXDOS Is

### 1.1 The pre-ESXDOS world

Before 2008, real-hardware Spectrum users who wanted disk storage had two options:

- **A +3 with its 3-inch drive** running +3 DOS — see [plus3dos.md](plus3dos.md). Reliable, but the 3-inch disks are now scarce, the drives are failing, and +3 DOS is incompatible with anything Soviet.
- **A Soviet clone with a Beta 128 interface** running TR-DOS — see [trdos.md](trdos.md). Reliable on 5.25" floppies, but the clones are ageing and the floppies are scarce.

A modern user in 2007 with a real 48K or 128K Spectrum had no good way to attach mass storage. Several hobbyist IDE interfaces existed (ZXCF, simple IDE), but each had its own incompatible DOS — there was no standard.

The DivIDE hardware, designed by **Zeax** in 2007, was the breakthrough. It was a single expansion card that provided:

- An IDE connector for a 40-pin IDE hard disk or CompactFlash card.
- A ROM slot holding firmware that could page into the Spectrum's address space.
- A button wired to the Spectrum's NMI line, allowing user-invoked firmware interaction.
- An optional RTC (real-time clock) for file timestamps.
- Compatibility with the Beta 128 port layout, so existing TR-DOS software could run via a `.TRD` image on the IDE disk.

What the DivIDE lacked was an OS to drive all this. Early firmware was crude: a basic menu that let the user pick a `.TRD` or `.TAP` image and "insert" it. There was no proper file system access.

### 1.2 ESXDOS's design goals

Dylan Smith started ESXDOS in 2008 to fill this gap. His stated goals:

1. **Standard filesystem.** Use FAT16 or FAT32 — the file system every PC, camera, and phone understands — so Spectrum files can be read and written directly from a modern computer with no conversion.
2. **Long filenames.** No more 8.3 limits. Spectrum files can have names like `mysong.pt3` or even `My Song (final mix).pt3`.
3. **BASIC-level access.** Users should be able to do file operations without dropping to machine code. This drove the dot-command design.
4. **A clean assembly API.** Machine-code programs should be able to open, read, write, seek, and close files through a uniform interface, similar to POSIX or BDOS.
5. **Backwards compatibility.** The system should still boot TR-DOS `.TRD` images and run existing software, when the user wants it to.
6. **Zero footprint when not in use.** ESXDOS should not consume RAM or interfere with running software unless explicitly invoked.

ESXDOS achieved all six goals. By 2010 it was the de facto firmware for every DivIDE owner. The later **DivMMC** hardware — a SD-card version of the DivIDE, designed by Zoran "Zoxon" Mačković — shipped with ESXDOS as its standard firmware from 2013 onward.

### 1.3 The dot-command concept

The most innovative aspect of ESXDOS is the **dot command**. Instead of patching the BASIC ROM to add new keywords (the way TR-DOS adds `*LOAD`, `*SAVE`, etc.), ESXDOS provides a tiny dispatcher that watches for input beginning with `*` followed by a filename. When it sees such input, it:

1. Looks for a file named `<name>.dot` in the `SYS` directory of the storage card.
2. Loads that file into a fixed RAM page.
3. Executes it.

The dot file is a regular Z80 machine-code program, typically 1–4 KB, that does its work (lists a directory, loads a game, mounts a tape image) and returns to BASIC. The user sees this as if BASIC had a rich new command set, but the implementation is much simpler and more extensible than patching the ROM.

Want a new command? Write a new `.dot` file. No ROM changes, no firmware updates. Hundreds of dot commands have been written by the community, covering everything from file management to network access to MOD music playback.

### 1.4 Versions

ESXDOS version history:

| Version | Year | Notable change |
|---|---|---|
| 0.1–0.5 | 2008–2010 | Initial development, DivIDE-only |
| 0.6 | 2011 | First widely-used version |
| 0.7 | 2012 | DivMMC support added |
| 0.8 | 2013 | Bug fixes; improved FAT32 support |
| 0.85 | 2014 | Dot command path resolution improved |
| 0.86 | 2015 | Last "stable" version for several years |
| 0.87–0.90 | 2018–2022 | Continued development after hiatus |
| 1.0 (dev) | 2023+ | Ongoing work toward a 1.0 release |

The version most commonly seen on real hardware today is **0.86**, but newer betas are circulating. The API surface has been stable since 0.7; software written against 0.7 will run on 0.90 with no changes.

---

## §2. The DivIDE and DivMMC Hardware

ESXDOS is meaningless without understanding the interface it runs on. This section covers the two pieces of hardware that host ESXDOS in 2024.

### 2.1 The DivIDE

The **DivIDE** (pronounced "divide", as in the mathematical operation) is a Spectrum expansion card designed by Zeax in 2007. It provides:

- A **40-pin IDE connector** compatible with standard PATA/IDE hard disks and CompactFlash cards (via a passive adapter).
- A **27C512 ROM socket** (64 KB EPROM) holding the firmware. ESXDOS occupies the lower 8–16 KB; the remainder can hold alternative firmware (e.g., a TR-DOS compatibility layer).
- An **NMI button**, which triggers the Spectrum's `#0066` NMI vector. ESXDOS hooks this vector to provide its main menu.
- An **RTC chip** (Dallas DS1307 or equivalent) for file timestamps, connected via I²C bit-banged from the Spectrum side.
- A **pass-through edge connector** so other peripherals (printer interfaces, audio expanders) can be daisy-chained.

The DivIDE occupies a small block of I/O ports, conventionally decoded at `#E3`–`#E7`:

| Port | Function |
|---|---|
| `#E3` | IDE register select / data (16-bit IDE access) |
| `#E5` | IDE register select / data |
| `#E7` | Control: ROM page, IDE bank, write-protect |
| `#A3`–`#A7` | Bank switching (alternative decode on some DivIDE clones) |

The DivIDE uses **memory paging**: its 64 KB ROM and the IDE data buffer are banked into the Spectrum's address space in 8 KB or 16 KB chunks. The exact paging scheme is documented in §3.

The DivIDE's most important feature, however, is **DivIDE-compatible TR-DOS emulation**. A small firmware layer (called "divese") can present any `.TRD` file on the IDE disk as if it were a real floppy in a Beta 128 drive. This means existing Soviet software runs unmodified — provided the software only uses the standard hook codes and does not talk directly to the WD1793.

### 2.2 The DivMMC

The **DivMMC** is a redesign of the DivIDE by Zoran Mačković (Zoxon), released in 2013. It replaces the IDE connector with an **SD card slot** (SPI-mode, compatible with all standard SD, SDHC, and SDXC cards) and removes the RTC and the pass-through connector, in exchange for a much smaller physical footprint and lower power consumption. The DivMMC:

- Uses the same I/O port layout as the DivIDE (`#E3`–`#E7`), so existing firmware works.
- Replaces the IDE register protocol with an SPI protocol for talking to the SD card. The firmware hides this difference; the user-visible API is identical.
- Comes in several physical variants: a bare PCB for DIY enclosure, a 3D-printed case version, and a "trimmed" version that fits inside the Spectrum 48K case.

The DivMMC is by far the most common modern Spectrum storage interface. A new Spectrum user in 2024 will almost certainly buy a DivMMC before any other peripheral. Its ubiquity makes ESXDOS effectively the default real-hardware Spectrum disk OS today.

### 2.3 Variants and successors

Several other interfaces provide ESXDOS-compatible APIs:

- **ZX Spectrum Next (internal)**: The Next has a built-in SD card slot and runs NextZXOS, an ESXDOS derivative. See [nextzxos.md](nextzxos.md).
- **ZX-Uno**: An FPGA Spectrum clone that includes a DivMMC-compatible SD interface.
- **ZX Evolution**: A Soviet/Russian FPGA Spectrum with both TR-DOS compatibility and a DivMMC-compatible SD interface.
- **MB02+**: An older IDE interface (ZebRoc Systems) that gained an ESXDOS-compatible firmware port.
- **zx-divmmc (FPGA)**: Various FPGA cores implement DivMMC-compatible interfaces.

Code that targets ESXDOS via the standard assembly API will run on all of these. The only variation is in the underlying hardware protocol, which is hidden by the firmware.

### 2.4 Hardware feature comparison

| Feature | DivIDE | DivMMC | NextZXOS |
|---|---|---|---|
| Storage | IDE / CF | SD | SD |
| Max card size | 137 GB (LBA28) | 2 TB (SDHC) | 2 TB |
| TR-DOS compatibility | Yes (via divese) | Yes | Yes (built-in) |
| RTC | Yes (DS1307) | No (some clones have one) | Yes |
| NMI button | Yes | Yes | Yes (via reset combo) |
| Pass-through | Yes | Most variants: No | N/A (built into Next) |
| Power consumption | ~200 mA | ~80 mA | N/A |

The trend is clear: DivMMC is the present, the Next is the future, and original DivIDE hardware is increasingly a collector's item.
---

## §3. Memory Layout

ESXDOS is unusual among Spectrum disk OSes in that it **does not consume RAM when not in use**. The entire firmware lives in the interface's own ROM, which is normally invisible to the CPU. RAM is allocated only when a dot command is loaded or an assembly program calls an ESXDOS function.

### 3.1 The firmware ROM window

The DivIDE/DivMMC firmware ROM is 64 KB on the original DivIDE, 128 KB or larger on some newer boards. This ROM is banked into the Spectrum's address space via a single control port at `#E7`. The banking scheme divides the firmware into **8 KB pages** and presents them at `#0000`–`#1FFF` (overlapping the BASIC ROM) when enabled:

| Bit pattern in port `#E7` | Effect on `#0000`–`#1FFF` |
|---|---|
| ROM disabled | BASIC ROM visible (default) |
| ROM enabled, page N | DivIDE/DivMMC firmware page N visible |

The currently-active page can be switched with a single `OUT` instruction. The first three pages (`0`, `1`, `2`) typically hold ESXDOS proper; pages `3`–`7` hold divese (the TR-DOS compatibility layer) and optional utilities.

### 3.2 Where dot commands run

When the user types `*.foo` at the BASIC prompt, the dispatcher:

1. Pages ESXDOS into the ROM window.
2. Allocates a 8 KB region of RAM at `#2000`–`#3FFF` (the "dot command slot").
3. Loads the file `SYS/foo.dot` into the dot command slot.
4. Calls the dot command's entry point at `#2000`.

The dot command runs with ESXDOS paged in, so it can call any ESXDOS API function. It has access to:

- `#2000`–`#3FFF`: its own code and data (8 KB).
- `#4000`–`#5AFF`: the screen (it can read and write the display).
- `#5B00`–`#5CB5`: the system variables.
- The upper RAM (`#5CB6`-up), used as scratch / heap.

The dot command **must not** return to BASIC without restoring the ROM window to its default state (BASIC ROM visible). The convention is to call the ESXDOS "exit" function, which performs the restore.

### 3.3 What ESXDOS uses when called from machine code

Machine code that calls ESXDOS functions (see §6) does not need to load a dot command. The caller:

1. Saves the current state of port `#E7`.
2. Pages ESXDOS into the ROM window.
3. Sets up registers per the function's calling convention.
4. Calls the ESXDOS dispatch routine.
5. Restores port `#E7`.

This sequence is short and well-defined. The key insight is that **ESXDOS does not need any persistent RAM** when called this way. The whole ESXDOS state lives in the firmware ROM and in two scratch bytes that the caller is expected to preserve.

### 3.4 Compatibility with running software

Because ESXDOS occupies no RAM by default, it is compatible with essentially all existing Spectrum software. A game loaded from a `.TAP` via a dot command will run identically to the same game loaded from a real cassette — the game does not know or care that ESXDOS exists.

The exceptions are:

- Software that uses the `#E3`–`#E7` I/O port range for some other purpose. This is rare but exists; some older clone-specific interfaces decoded other peripherals in this range.
- Software that hooks the NMI vector for its own purposes. Since ESXDOS also hooks NMI, conflicts are possible. The user can disable ESXDOS's NMI hook in firmware settings.
- Software that insists on direct WD1793 FDC access. The DivIDE/DivMMC emulates the WD1793 via divese, but only if the user has enabled TR-DOS compatibility mode. Software that writes raw FDC commands will not work outside this mode.

---

## §4. Dot Commands

The dot command interface is the user-facing heart of ESXDOS. This section documents the syntax, the standard commands shipped with the system, and the conventions for writing new ones.

### 4.1 Syntax

A dot command is invoked from the BASIC prompt by typing `*` followed by the command name (without the `.dot` extension) and any arguments:

```
*.dir /games/*.tap
*.load game.z80
*.tap load mygame.tap
*.cp file1.z80 /backup/
```

The leading `.` is implicit. ESXDOS looks for a file named `dir.dot`, `load.dot`, `tap.dot`, `cp.dot` in the `SYS` directory of the storage card. If found, it loads and runs that file.

Arguments are passed to the dot command as a string in a known RAM location. The dot command parses them itself — there is no enforced argument convention. Most commands accept space-separated arguments and forward-slash-style paths.

### 4.2 Standard commands

ESXDOS ships with a baseline set of dot commands:

| Command | Purpose |
|---|---|
| `*.dir` or `*.ls` | List the contents of a directory |
| `*.cd` | Change current directory |
| `*.md` | Make a new directory |
| `*.rd` | Remove a directory |
| `*.cp` | Copy a file |
| `*.mv` | Move/rename a file |
| `*.rm` | Delete a file |
| `*.type` | Display a text file |
| `*.load` | Load a file into memory (raw bytes) |
| `*.save` | Save memory to a file (raw bytes) |
| `*.tap` | Tape image commands (load, save, list, convert) |
| `*.trd` | TR-DOS image commands |
| `*.sna` | Snapshot load/save |
| `*.z80` | `.z80` snapshot load/save |
| `*.scr` | Screen image load/save |
| `*.rom` | ROM image loading (for custom ROM banks) |
| `*.exit` | Exit a dot command |
| `*.help` | Built-in help |

These cover the basics of file management. Beyond them, the community has contributed hundreds of additional dot commands:

- **`*.if2`**: Interface 2 ROM cartridge loading.
- **`*.dsk`**: +3 DOS `.DSK` image manipulation.
- **`*.zip`**: ZIP archive extraction.
- **`*.mod`**: Amiga MOD module playback.
- **`*.ay`**: AY music module playback (PT3, ASC, AKG, etc.).
- **`*.sid`**: SID music playback (via a SID-on-Spectrum hardware expansion).
- **`*.net`**: Network access (via a Spectranet or modem).
- **`*.up`**: Update ESXDOS firmware from a file on the card.

A typical Spectrum user's SD card has the standard set plus perhaps 20-30 additional community dot commands, covering most file and media types in the Spectrum ecosystem.

### 4.3 Path conventions

ESXDOS paths use forward slashes (`/`) and follow Unix-like conventions:

| Path | Meaning |
|---|---|
| `/games/foo.tap` | Absolute path, from card root |
| `games/foo.tap` | Relative path, from current directory |
| `./foo.tap` | Explicit relative path |
| `../foo.tap` | Parent directory |
| `/` | Card root |

The current directory is stored in a single-byte pointer in firmware state; it persists across BASIC sessions (until the Spectrum is reset). The default current directory at boot is `/`.

Filenames are case-insensitive on most filesystems (FAT16/FAT32 is case-insensitive by convention), but ESXDOS preserves case when listing directories. Long filenames (up to 255 characters) are fully supported.

### 4.4 Wildcards

Several commands — notably `*.dir` and `*.cp` — support wildcards in their arguments:

- `*` matches zero or more characters.
- `?` matches exactly one character.

Examples:

```
*.dir /games/*.tap         ; list all .tap files in /games
*.dir /?i*                 ; list entries starting with any char + "i"
*.cp /games/*.tap /backup/ ; copy all .tap files
```

Wildcard expansion is performed by the dot command itself, not by ESXDOS. Each dot command implements its own glob logic; conventions are mostly consistent but not universal.

### 4.5 The NMI menu

When the user presses the NMI button (the small button on the DivIDE/DivMMC), ESXDOS displays a menu in a small popup over the current screen. The menu offers:

- **Browser**: a full-screen file browser that can navigate the SD card and load files directly.
- **Commands**: a text entry field where any dot command can be typed.
- **Configuration**: settings for TR-DOS compatibility mode, autostart, RTC, etc.
- **Exit**: return to whatever was running before NMI was pressed.

The NMI menu is the primary user interface for ESXDOS. Many users never type dot commands at the BASIC prompt; they use the NMI browser exclusively.

### 4.6 Writing a dot command

A dot command is simply a Z80 machine-code program with:

- Entry point at offset `0` of the file.
- An ESXDOS header byte at offset `0` indicating version and features (most dot commands use a simple header).
- A return-to-BASIC sequence at the end, typically `JP #0084` or a call to an ESXDOS exit function.

A minimal dot command skeleton:

```z80
        ; --- ESXDOS header (single byte at offset 0) ---
        DB   $DD                   ; magic byte indicating ESXDOS dot command
        
        ; --- entry point at offset 1 ---
entry:  DI
        ; ... dot command body ...
        ; ... call ESXDOS functions as needed ...
        EI
        RET                        ; return to BASIC
```

In practice, dot commands are written in C (using z88dk, which has an ESXDOS target), in assembly (using sjasmplus), or in a mix of the two. The z88dk ESXDOS dot-command template handles the header, the entry point, and the argument parsing; the developer writes only the body.

### 4.7 Worked example: a "hello world" dot command

The following complete dot command (in sjasmplus assembly) prints "Hello, ESXDOS!" to the screen and returns to BASIC:

```z80
        DEVICE ZXSPECTRUM48
        ORG  $2000                ; dot commands load at $2000
        
        DB   $DD                  ; ESXDOS dot-command magic
        
        ; --- entry ---
        LD   HL,msg
loop:   LD   A,(HL)
        OR   A
        RET  Z                    ; null terminator: return to BASIC
        RST $10                   ; print character (using BASIC ROM RST #10)
        INC  HL
        JR   loop
        
msg:    DB   "Hello, ESXDOS!",13,0
        
        ; file padding to a 256-byte boundary (ESXDOS loads dot
        ; commands in 256-byte chunks)
        DEFS $-($2000),0
```

Assemble with `sjasmplus hello.asm`, copy `hello.bin` to `SYS/hello.dot` on the SD card, and type `*.hello` at the BASIC prompt. The string prints. This is the smallest meaningful ESXDOS dot command.
---

## §5. Filesystem

ESXDOS uses the **FAT** filesystem — the same filesystem used by MS-DOS, Windows, digital cameras, and embedded devices worldwide. This section documents the FAT variants supported, the directory layout conventions, and the differences from TR-DOS's custom format.

### 5.1 FAT16 and FAT32

ESXDOS supports both **FAT16** and **FAT32**. FAT12 is not supported (the smallest cards in use today are well above FAT12's 32 MB ceiling).

| Filesystem | Card size range | Cluster size | Notes |
|---|---|---|---|
| FAT16 | 16 MB to 2 GB | 2 KB to 32 KB | Recommended for older hardware; slightly faster |
| FAT32 | 512 MB to 2 TB | 4 KB to 32 KB | Required for cards > 2 GB; default on modern SD cards |

Cards larger than 2 TB are not currently supported; the SD card standard itself has only recently reached this size, and FAT32 becomes inefficient above 32 TB anyway.

The choice between FAT16 and FAT32 does not affect the user-visible API. ESXDOS abstracts the differences internally. A file written on a FAT16 card reads correctly on a FAT32 card and vice versa.

### 5.2 Long filenames

VFAT long filenames (LFN) are fully supported. Files can have names up to 255 characters, with mixed case, spaces, and most punctuation. The only forbidden characters are the same as on Windows: `\`, `/`, `:`, `*`, `?`, `"`, `<`, `>`, `|`.

This is a significant step up from TR-DOS's 8+1 character names. A typical ESXDOS card might contain files named:

- `Eternal_Dead_City.pt3`
- `My Demo (final).z80`
- `BASIC programs/math/prime sieve.b`

LFN support does cost some performance: a directory listing has to read twice as many directory entries (the LFN entries plus the 8.3 alias). For most use cases the difference is imperceptible.

### 5.3 Recommended directory layout

ESXDOS itself does not impose any particular directory structure on the card. The community has, however, converged on a de facto convention:

```
/
├── SYS/                     ; dot commands (loaded automatically)
│   ├── dir.dot
│   ├── load.dot
│   └── ...
├── BIN/                     ; utility programs
├── GAMES/                   ; games (typically as .z80 or .tap)
│   ├── Manic Miner.z80
│   └── ...
├── DEMOS/                   ; demo scene productions
│   ├── Ecstasy.trd
│   └── ...
├── MUSIC/                   ; AY/beeper music modules
│   ├── songs/
│   │   └── mysong.pt3
│   └── players/
├── SNAPSHOTS/               ; .z80 / .sna snapshots
└── MISC/                    ; anything else
```

The only directory ESXDOS itself looks in is `SYS/` — for dot commands. All other directories are convention. A card with no `SYS/` directory will boot but the user will have no dot commands until they create it and copy the standard set.

### 5.4 File types

ESXDOS does not enforce file types — every file is just a stream of bytes — but the community uses extensions to indicate content:

| Extension | Meaning |
|---|---|
| `.dot` | ESXDOS dot command |
| `.z80` | Spectrum snapshot (`.z80` format) |
| `.sna` | Spectrum snapshot (`.sna` format) |
| `.tap` | Tape image |
| `.tzx` | Tape image (TZX format, advanced) |
| `.trd` | TR-DOS disk image |
| `.dsk` | +3 DOS disk image |
| `.mdr` | Microdrive image |
| `.scr` | Screen dump (6912 bytes raw) |
| `.rom` | ROM image |
| `.pt3`, `.asc`, `.akg` | AY music modules |
| `.ay` | AY music module container |
| `.mod` | Amiga MOD module |
| `.txt` | Plain text |
| `.bin` | Raw binary (loaded to a fixed address) |

The `.dot` extension is the only one ESXDOS itself checks. Everything else is convention enforced by dot commands (e.g., `*.sna load foo.sna` knows how to handle a snapshot file).

### 5.5 Comparison with TR-DOS

| Feature | TR-DOS | ESXDOS |
|---|---|---|
| Filesystem | Custom (80×16 sectors) | FAT16/FAT32 |
| Filename length | 8+1 | 255 characters |
| Directory structure | Flat (no subdirectories) | Hierarchical |
| Max files per volume | 128 | Effectively unlimited |
| Max volume size | 640 KB | 2 TB |
| Snapshot/tape support | Via separate tools | Built-in via dot commands |
| Cross-platform (PC) read | Requires `.TRD` tools | Native FAT support |
| Bootable | Yes (boot.B) | Yes (auto-run from a configured file) |

For modern use, ESXDOS wins on every axis except nostalgia and authenticity. A Soviet clone owner running original 1995 hardware will use TR-DOS; everyone else uses ESXDOS or NextZXOS.

---

## §6. The Assembly API

ESXDOS exposes its file I/O services to machine-code programs through a small, well-defined API. This section documents the dispatch mechanism, the function catalog, and the calling conventions.

### 6.1 Dispatch mechanism

All ESXDOS functions are called via the same dispatch routine at address `#0084` (in the ROM window — the caller must have ESXDOS paged in). The function number is loaded into the `B` register before the call. The dispatcher reads `B` and jumps to the corresponding internal routine.

The standard call sequence:

```z80
DI                      ; interrupts off
LD   B,function_number  ; ESXDOS function (e.g. $9A for M_OPENFILE)
LD   HL,filename        ; function-specific parameter
; ... set up other registers per function ...
CALL #0084              ; dispatch
; ... carry set on success, reset on error ...
EI
```

If the function succeeds, ESXDOS returns with the **carry flag set**. On error, the carry flag is reset and the A register holds the error code (see §6.6).

### 6.2 The function catalog

The core ESXDOS function set, stable since version 0.7:

| `B` | Name | Purpose |
|---|---|---|
| `#80` | M_GETSETDRIVE | Get/set current drive |
| `#81` | M_DRIVESTATUS | Check drive status |
| `#82` | M_TAPIN | Read a byte from tape |
| `#83` | M_TAPOUT | Write a byte to tape |
| `#84` | M_TAPEIO | General tape I/O |
| `#86` | M_SETRAM | Set RAM bank |
| `#87` | M_SETRAMBACK | Restore RAM bank |
| `#88` | M_GETHANDLE | Allocate a file handle |
| `#89` | M_FINDHANDLE | Find a free handle |
| `#8A` | M_GETDATE | Get current date/time |
| `#8B` | M_SETDATE | Set current date/time |
| `#8C` | M_DBALLOC | Database allocation |
| `#94` | F_MOUNT | Mount a filesystem |
| `#95` | F_OPEN | Open a file |
| `#96` | F_CLOSE | Close a file |
| `#97` | F_SYNC | Sync file system |
| `#98` | F_READ | Read bytes from a file |
| `#99` | F_WRITE | Write bytes to a file |
| `#9A` | F_SEEK | Seek in a file |
| `#9B` | F_FGETPOS | Get current position |
| `#9C` | F_FSTAT | Get file info |
| `#9D` | F_FOPENDIR | Open a directory |
| `#9E` | F_FREADDIR | Read directory entry |
| `#9F` | F_FCLOSEDIR | Close a directory |
| `#A0` | F_FSTAT_FREE | Get free space info |
| `#A1` | F_FTRUNCATE | Truncate a file |
| `#A2` | F_FMKDIR | Make a directory |
| `#A3` | F_FRMDIR | Remove a directory |
| `#A4` | F_FRENAME | Rename a file |
| `#A5` | F_FREMOVE | Delete a file |
| `#A6` | F_FATTRIB | Change file attributes |
| `#A7` | F_FCD | Change current directory |
| `#A8` | F_FGETCWD | Get current directory path |

This is a much richer API than TR-DOS's nine hook codes. The function names follow a Unix/POSIX flavor: `F_OPEN`/`F_CLOSE`/`F_READ`/`F_WRITE` are obvious analogs of POSIX `open`/`close`/`read`/`write`, and `F_FMKDIR`/`F_FRMDIR` mirror `mkdir`/`rmdir`.

### 6.3 File handles

ESXDOS uses **file handles** — small integers (1–255) that identify an open file. A handle is returned by `F_OPEN` and passed to `F_READ`, `F_WRITE`, `F_SEEK`, and `F_CLOSE`. Up to 255 files can be open simultaneously (in practice, the limit is lower — the firmware reserves a fixed-size handle table).

This is conceptually different from TR-DOS, where every file operation is independent and there is no concept of an open file. The handle model is more powerful: it supports seeking, partial reads, and overlapping access to multiple files. The cost is the handle table.

### 6.4 Worked example: open and read a file

```z80
; Open "/etc/foo.bin" for reading, read 256 bytes into #8000, close.

DI
LD   B,#95              ; F_OPEN
LD   HL,fn              ; pointer to filename string
LD   A,1                ; mode: read
; (ESXDOS will allocate a handle and return it in A)
CALL #0084
JR   C,open_ok          ; carry set = success
; ... handle error (A = error code) ...
JP   error_exit

open_ok:
LD   (handle),A         ; save the handle

LD   B,A                ; B = handle
LD   B,#98              ; F_READ
LD   HL,#8000           ; destination address
LD   DE,256             ; byte count
CALL #0084
JR   C,read_ok
; ... handle read error ...
JP   error_exit_close

read_ok:
LD   B,(handle)
LD   B,#96              ; F_CLOSE
CALL #0084

error_exit_close:
LD   B,(handle)
LD   B,#96              ; F_CLOSE
CALL #0084

error_exit:
EI
RET

fn:     DB   "/etc/foo.bin",0
handle: DB   0
```

This pattern — open, read, close — is the universal file-loading idiom in ESXDOS. Note that the filename string is null-terminated (TR-DOS uses 9-byte fixed-length strings; ESXDOS uses null-terminated C-style strings).

### 6.5 Worked example: write a file

```z80
; Save 6912 bytes from #4000 (the screen) to "/snaps/screen.scr"

DI
LD   B,#95              ; F_OPEN
LD   HL,fn
LD   A,2                ; mode: write (create/truncate)
CALL #0084
JR   C,open_ok
JP   error_exit
open_ok:
LD   (handle),A

LD   B,A
LD   B,#99              ; F_WRITE
LD   HL,#4000           ; source address
LD   DE,6912            ; byte count
CALL #0084

LD   B,(handle)
LD   B,#96              ; F_CLOSE
CALL #0084
EI
RET

fn:     DB   "/snaps/screen.scr",0
handle: DB   0
```

### 6.6 Error codes

ESXDOS uses a single-byte error code returned in the A register on failure (carry flag reset). The codes overlap with but are not identical to TR-DOS:

| Code | Meaning |
|---|---|
| `#01` | OK (no error) |
| `#02` | No file |
| `#03` | Bad parameter |
| `#04` | Out of memory |
| `#05` | Drive not present |
| `#06` | Invalid drive |
| `#07` | Sector not found (FAT corruption or hardware error) |
| `#08` | Read error |
| `#09` | Write error / write-protected |
| `#0A` | Out of space |
| `#0B` | Bad filesystem / not FAT |
| `#0C` | File not found |
| `#0D` | Invalid filename |
| `#0E` | Already exists |
| `#0F` | Out of file handles |
| `#10` | Path not found |
| `#11` | Bad mode |
| `#12` | Drive busy |
| `#FF` | Timeout / no response |

A robust ESXDOS-aware program should handle at least `#0A`, `#0C`, `#0E`, and `#0F` — these are the errors a normal user can remedy.
---

## §7. Programming Patterns

Real-world ESXDOS programming shows clear recurring patterns. This section documents the three most important ones.

### 7.1 The NMI handler

Many ESXDOS-aware programs hook the NMI button to provide in-game or in-demo file access (save state, screenshot, return to browser). The pattern:

```z80
install_nmi:
        LD   HL,nmi_handler
        LD   (#0066),JP_ptr      ; write JP nmi_handler at #0066
        LD   (#0066+1),HL
        RET

nmi_handler:
        ; --- NMI was pressed; save state and call ESXDOS ---
        DI
        EXX
        EX   AF,AF'              ; save alternate registers
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        PUSH IX
        PUSH IY
        
        ; ... do ESXDOS work here (save snapshot, list files, etc.) ...
        
        ; --- restore state ---
        POP  IY
        POP  IX
        POP  HL
        POP  DE
        POP  BC
        POP  AF
        EX   AF,AF'
        EXX
        EI
        RETN                     ; NMI return (not RET)
```

The key points:

- Use `EXX` / `EX AF,AF'` to swap in the alternate register set before saving anything. This leaves the main registers untouched when control returns to the running program.
- Restore the alternate set on exit.
- Use `RETN` (retrieves IFF2 into IFF1, restoring interrupt state) rather than `RET`.

The NMI handler can call ESXDOS functions freely. ESXDOS itself uses the same pattern for its built-in NMI menu.

### 7.2 The snapshot loader

A common task: load a `.z80` or `.sna` snapshot from the SD card and resume execution in that snapshot. The pattern:

1. Open the snapshot file with `F_OPEN`.
2. Read its header with `F_READ` (the first 30 bytes for `.sna`, or variable for `.z80`).
3. Restore the CPU registers from the header.
4. Restore the RAM contents (via bulk `F_READ`).
5. Restore the paging state.
6. `JP` to the snapshot's stored PC.

ESXDOS itself provides this functionality via the `*.sna` and `*.z80` dot commands, but if you want to embed it in your own program (e.g., a "continue from last save" feature in a game), the pattern is the same — just inlined.

### 7.3 The TR-DOS compatibility bridge

A program that needs to load a TR-DOS `.TRD` disk image and read a file from it has two options:

**Option A: Use divese.** Mount the `.TRD` as a virtual floppy in the Beta 128 emulator, then issue standard TR-DOS hook codes (see [trdos.md](trdos.md) §6). This is the simplest approach — the divese layer handles everything. The catch is that the user must have enabled TR-DOS compatibility mode in the ESXDOS NMI menu.

**Option B: Parse the .TRD file directly.** Open the `.TRD` file as a regular ESXDOS file, seek to offset 0 (the catalog), read the catalog entries, locate the file by name, and bulk-read the file's sectors. This is more code, but works without TR-DOS mode enabled and is more portable.

Most modern loaders use Option A because it requires less code. Option B is used by cross-platform tools (e.g., `.TRD`-to-`.TAP` converters) that run on non-Spectrum hosts.

### 7.4 The autoplay-on-boot

To make a program auto-run when the Spectrum boots with a particular card inserted, the user places a file named `autorun.bas` (or any other configured name) at the root of the card. ESXDOS, on detecting this file, loads and runs it before dropping to the BASIC prompt.

The implementation is trivial: a small NextBASIC program that contains a single `LOAD "..." : RUN` line pointing at the desired program. This is the modern equivalent of TR-DOS's `boot.B`.

---

## §8. Quirks and Traps

ESXDOS is generally well-behaved, but it has accumulated its own folklore of footguns. The most important ones:

### 8.1 The 8 KB dot command limit

The dot command slot is **exactly 8 KB** (`#2000`–`#3FFF`). Dot commands larger than this cannot be loaded by the standard dispatcher. Workarounds include:

- Storing data in a separate file on the card and loading it on demand.
- Using the upper RAM (`#8000`-up) for overflow, paging out the dot command's lower 8 KB once initialised.
- Writing the command as two halves: a small dot command loader that calls into a larger secondary program.

Most dot commands fit comfortably in 8 KB. The ones that don't (typically text editors and tape format converters) use the secondary-program pattern.

### 8.2 The boot-time delay

When the Spectrum is first powered on with a DivMMC attached, ESXDOS performs an SD card initialisation that takes **1–3 seconds**. During this time, the BASIC ROM is in control but the SD card is not yet ready. Calls to ESXDOS functions during this window will fail with `#FF` (timeout).

The cure: poll the drive status (`M_DRIVESTATUS` function `#81`) until it returns "ready" before doing any other ESXDOS call. Most well-behaved programs do this at startup.

### 8.3 Long filenames and DOS 8.3 names

Each file on a FAT card has two directory entries: the LFN (long filename) entries and the underlying 8.3 alias. When a card is written from a modern OS, both are present. When a card is written from ESXDOS, only the LFN entry is created if the filename doesn't fit in 8.3 — and the 8.3 alias is auto-generated.

This is mostly invisible, but causes problems if the card is later moved to a system that only reads 8.3 names (older DOS, some embedded devices). Files with names like `My Demo (final).z80` will appear as `MYDEM~1.Z80`.

### 8.4 SD card class matters

The SD card class (Class 4, Class 10, UHS-I, etc.) affects read performance. A Class 4 card can deliver sustained reads of about 100 KB/s — fast enough for most Spectrum uses (the entire 48K RAM loads in well under a second). A Class 10 or UHS-I card is several times faster, which matters for video demos and snapshot-heavy workflows.

Counterintuitively, **some very old or very small cards work poorly with the DivMMC**. The DivMMC's SPI implementation assumes certain timing characteristics of the SD protocol; cards that violate these can produce read errors. As a rule, any SD card from a major manufacturer made after 2010 will work fine.

### 8.5 The NMI button is shared

Pressing the NMI button on a DivMMC triggers ESXDOS's NMI handler — but only if no running program has hooked NMI for its own use. Games that use NMI for music playback or in-game debug will see their NMI handler invoked instead of ESXDOS's menu.

The cure is to press-and-hold the NMI button for >2 seconds, which is interpreted as a "force ESXDOS menu" gesture by the firmware.

### 8.6 Compatibility with Soviet software

Soviet software written for TR-DOS generally works under ESXDOS via the divese compatibility layer, with these caveats:

- Software that uses the hook codes for sector I/O (e.g., custom disk protection) may fail if the divese emulation is incomplete. divese has been refined over the years and is now very complete, but edge cases remain.
- Software that expects the 128K BASIC editor to be patched with `*` commands (TR-DOS-style) will not see those commands. ESXDOS uses `.` commands instead, and there is no compatibility shim.
- Software that directly accesses the WD1793 FDC ports (`#1F`-range) bypasses divese and will not work. Use of the hook codes is required.

### 8.7 The firmware update process

Updating ESXDOS firmware requires:

1. Putting the new firmware file (typically `esxdos.rom`) on the SD card.
2. Booting the Spectrum with the SD card inserted.
3. Typing `*.up esxdos.rom` (or running the `*.up` dot command from the NMI menu).
4. Waiting 10–30 seconds for the flashing process to complete.
5. Rebooting.

The flashing process writes to the interface's EEPROM. A power loss during flashing will brick the interface — there is no recovery without an external EEPROM programmer. Always use a stable power supply when updating firmware.
---

## §9. Modern Status and Derivatives

ESXDOS in 2024 is the foundation of a small but active ecosystem. This section documents the current state and the major derivative projects.

### 9.1 Active development

ESXDOS development continues, primarily driven by Dylan Smith and a small group of contributors. The current development branch (which has not yet been tagged as a stable release) includes:

- Improved SDHC and SDXC card support (cards up to 2 TB).
- Faster SPI timing for Class 10/UHS-I cards.
- Expanded dot-command set.
- Better divese compatibility (more complete TR-DOS hook code coverage).
- A cleaner, more POSIX-like API for some functions.

The official distribution channel is the ESXDOS site (esxdos.org, occasionally mirrored elsewhere) and the World of Spectrum forums. Development builds are circulated among beta testers; stable releases appear roughly once a year.

### 9.2 ResiDOS

**ResiDOS** is an older derivative of ESXDOS by Matthew Wilson, dating from around 2011–2013. It adds:

- Multiple RAM bank management (for 128K and expanded machines).
- A more sophisticated dot-command shell.
- Some additional filesystem features.

ResiDOS is largely historical today — its features have been absorbed into mainstream ESXDOS — but it remains in use on some older DivIDE hardware where newer ESXDOS versions are too heavy.

### 9.3 NextZXOS

**NextZXOS** is the ZX Spectrum Next's built-in OS, an ESXDOS derivative maintained by the Next team. It preserves the ESXDOS API almost intact while adding:

- Support for the Next's hardware (Layer 2, tilemap, sprites, copper).
- NextBASIC integration (NextBASIC can call ESXDOS functions directly via `#` syntax).
- Larger dot commands (the Next has 2 MB RAM, so the 8 KB limit is lifted).
- The Next's `.dot` system uses the same syntax and conventions as ESXDOS, so most dot commands port with minimal changes.

NextZXOS is the most widely-used ESXDOS derivative today, thanks to the commercial success of the ZX Spectrum Next (10,000+ units shipped). See [nextzxos.md](nextzxos.md) for the full Next-specific picture.

### 9.4 Cross-platform tooling

Several tools on modern operating systems produce or consume ESXDOS-format files:

- **z88dk** has a complete ESXDOS dot-command template (`zcc +esxdot ...`).
- **SJASMPlus** has ESXDOS-aware features (the `DEVICE ZXSPECTRUM48` directive respects ESXDOS dot-command layout).
- **Fuse**, **ZEsarUX**, and other emulators implement ESXDOS-compatible APIs for testing.
- **zxpaint**, **zarch**, and other cross-platform tools can target ESXDOS output.

A modern developer writing for real Spectrum hardware can write code in C or assembly on a Mac/Linux/Windows machine, cross-compile, drop the resulting `.dot` file onto an SD card, and test it on the real Spectrum in seconds. This workflow did not exist before ESXDOS.

### 9.5 The community

The ESXDOS community lives primarily on:

- **The World of Spectrum forums** (worldofspectrum.org/forums): the historical home; most dot commands are announced here.
- **The ZX Spectrum Next forum** (spectrum-next.net): for NextZXOS-specific discussion.
- **The Russian Spectrum forums** (zx-pk.ru, speccy.info): for Soviet hardware integration issues.
- **The "ESXDOS and DivMMC" Facebook group**: smaller but active.
- **GitHub**: many modern dot commands are open-sourced there.

The community has been remarkably stable over the past 15 years, with the same names appearing throughout. New contributors are welcomed; the barrier to writing a first dot command is low (a working z88dk install and 50 lines of C is sufficient).

### 9.6 Why ESXDOS succeeded

Like TR-DOS before it, ESXDOS succeeded for a mix of technical and circumstantial reasons:

1. **Right hardware at the right time.** The DivIDE (2007) and DivMMC (2013) solved the "how do I attach storage to a real Spectrum" problem just as the retro-computing revival was beginning.
2. **FAT compatibility.** Making the Spectrum speak the same filesystem as every PC was a masterstroke. No conversion, no special software — drop the SD card in your laptop and copy files.
3. **The dot command model.** A simple, extensible, community-friendly way to add commands without ROM patching. Hundreds of dot commands exist because writing one is easy.
4. **Backwards compatibility.** Existing Soviet software kept working via divese. Users did not have to choose between old and new.
5. **Active maintenance.** Dylan Smith has continued developing ESXDOS for over 15 years. The API has stayed stable while the implementation has improved.

The result is that ESXDOS — or one of its derivatives — is what runs on essentially every real-hardware Spectrum in active use today.

---

## §10. Cross-References

### 10.1 Within the Operating Systems section

- [README.md](README.md) — section index
- [trdos.md](trdos.md) — the older Soviet disk OS; ESXDOS provides TR-DOS compatibility via divese
- [nextzxos.md](nextzxos.md) — the ZX Spectrum Next's derivative of ESXDOS
- [plus3dos.md](plus3dos.md) — the Amstrad +3 DOS, the other Western Spectrum disk OS
- [rom_48k.md](rom_48k.md) — the 48K BASIC ROM that ESXDOS coexists with
- [rom_128k.md](rom_128k.md) — the 128K editor ROM

### 10.2 Outside the section

- [../02_hardware/original/README.md](../02_hardware/original/README.md) — original Sinclair hardware that hosts DivIDE/DivMMC
- [../02_hardware/newgen/README.md](../02_hardware/newgen/README.md) — the ZX Spectrum Next and other modern FPGA hardware that runs ESXDOS derivatives
- [../05_development/03_memory_and_io/memory_and_io_next.md](../05_development/03_memory_and_io/memory_and_io_next.md) — ZX Spectrum Next memory and I/O (NextZXOS context)
- [../07_demoscene/demo_frameworks.md](../07_demoscene/demo_frameworks.md) — modern demo frameworks, which assume ESXDOS or NextZXOS as the runtime

### 10.3 External resources

- **Official ESXDOS site**: https://www.esxdos.org/
- **DivMMC project page**: https://divmmc.com/
- **z88dk ESXDOS documentation**: https://github.com/z88dk/z88dk/wiki/ESXDOS
- **SJASMPlus**: https://github.com/z00m128/sjasmplus
- **ZX Spectrum Next documentation** (NextZXOS): https://specnext.dev/
- **World of Spectrum forums**: https://worldofspectrum.org/forums/
- **ZX-PK.ru (Russian)**: https://zx-pk.ru/
- **ZX Spectrum Wiki on ESXDOS**: https://sinclair.wiki.zx/esxdos

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/). Attribute as "ESXDOS — The Modern Spectrum Disk OS, from the ZX Spectrum Knowledge Base".
