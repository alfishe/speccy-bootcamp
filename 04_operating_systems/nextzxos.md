[← Home](../README.md) · [Operating Systems](README.md)

# NextZXOS — The ZX Spectrum Next Operating System

The ZX Spectrum Next, released in 2017 after a successful Kickstarter campaign, needed an operating system that did something no Spectrum OS had done before: bridge 1982-era compatibility with 21st-century hardware features like 2 MB of RAM, a Layer 2 256-color framebuffer, hardware sprites, a tilemap, a programmable copper unit, and a DMA controller. The result is **NextZXOS** — an ESXDOS derivative that has become the most powerful native Spectrum OS ever written.

NextZXOS was authored primarily by **Garry Lancaster** with contributions from the wider Next team (Jim Bagley, Victor Trucco, Fabio Belavenuto, Henrique Oliviéri). It preserves the ESXDOS API almost intact, so existing ESXDOS software and dot commands run with minimal modification. On top of this base, NextZXOS adds NextBASIC integration (NextBASIC can call ESXDOS functions directly), an expanded dot-command system (no 8 KB limit), and hardware-acceleration hooks for Layer 2, sprites, and the copper.

This article covers NextZXOS as a system: the Next hardware it runs on, its memory model, the NextBASIC integration, the dot-command system, the filesystem, the assembly API, common programming patterns, and the current state of the Next ecosystem. For ESXDOS — the parent OS — see [esxdos.md](esxdos.md). For the Next's hardware, see [../02_hardware/newgen/README.md](../02_hardware/newgen/README.md).

---

## Roadmap

1. **What NextZXOS is** — origins, design goals, relationship to ESXDOS
2. **Next hardware context** — what NextZXOS exposes (Layer 2, sprites, tilemap, copper, DMA, ESP)
3. **Memory model** — the 2 MB MMU, banking, ESXDOS overlays
4. **NextBASIC integration** — how NextBASIC calls NextZXOS functions
5. **Dot commands** — the expanded dot-command system
6. **Filesystem** — FAT32 on the Next's SD card, Next-specific conventions
7. **The assembly API** — ESXDOS-compatible functions, Next-specific extensions
8. **Programming patterns** — NMI handler, hardware-accelerated effects, snapshotting
9. **Modern status** — version history, the Next ecosystem, where to get help
10. **Cross-references** — where to go next

---

## §1. What NextZXOS Is

### 1.1 Origins

The ZX Spectrum Next project began in 2016 as a collaboration between Rick Dickinson (Sinclair's industrial designer) and a team of veteran Spectrum developers. The hardware was ambitious: an FPGA-based Spectrum clone with 2 MB of RAM, hardware acceleration for graphics, an integrated ESP32 for WiFi, and full backward compatibility with every model of original Spectrum hardware.

The OS choice was contentious. Three options were on the table:

1. **Ship a plain ESXDOS port.** This would work, but would not expose any of the Next's new hardware. Users would have to write machine code to access Layer 2, sprites, etc.
2. **Write an entirely new OS.** This would maximize the Next's potential but would break compatibility with the existing ESXDOS dot-command ecosystem.
3. **Extend ESXDOS.** Keep the ESXDOS API stable, add Next-specific functions and a NextBASIC integration layer on top.

The team chose option 3. Garry Lancaster, already the author of the popular "+3DOS" extension libraries for the original Spectrum, took on the task of adapting the ESXDOS source to the Next's hardware and adding the integration layer. The result — **NextZXOS** — was first released as version 1.0 in 2017 alongside the initial Next hardware shipments.

### 1.2 Relationship to ESXDOS

NextZXOS is **API-compatible with ESXDOS**. The core function catalog (F_OPEN, F_CLOSE, F_READ, F_WRITE, F_SEEK, F_OPENDIR, F_READDIR, etc.) is identical; the calling convention (`LD B,function; CALL #0084`) is the same; the error codes are the same. Code written for ESXDOS on a DivMMC runs on the Next with no changes (assuming it does not use the DivMMC's specific I/O ports directly).

On top of the ESXDOS base, NextZXOS adds:

- **Next-specific functions** for hardware acceleration (`F_VIDEO`, `F_LAYER2`, `F_SPRITE`, `F_TILEMAP`, `F_COPPER`, `F_DMA`).
- **NextBASIC extensions** that expose these functions to BASIC programs via the `#` syntax (e.g., `#L2`, `#SPRITE`, `#TILEMAP`).
- **An expanded dot-command system** that lifts the 8 KB limit (the Next's 2 MB RAM allows arbitrary-size dot commands) and adds Next-specific environment information.
- **Hardware-accelerated tape loading** via the DMA controller — `.TAP` files load at much higher speeds than the original hardware allowed.

The result is an OS that feels familiar to any ESXDOS user but exposes far more capability.

### 1.3 Design goals

NextZXOS's stated design goals, in approximate priority order:

1. **Zero surprises for ESXDOS users.** A DivMMC user picking up a Next should feel immediately at home.
2. **Full Next hardware access from BASIC.** No machine code required for Layer 2 graphics, sprite plotting, copper programming, or DMA transfers.
3. **Maximum backward compatibility.** Original Spectrum software, both 48K and 128K, runs without modification.
4. **Extensibility.** New dot commands and NextBASIC extensions should be addable without firmware updates.
5. **Open source.** All NextZXOS source code is on GitHub under a permissive license.

NextZXOS has met all five goals. The Next is the only Spectrum-compatible machine on which a BASIC programmer can write a smooth-scrolling hardware-sprite game without dropping to assembly.

### 1.4 Versions

NextZXOS version history (showing the major stable releases):

| Version | Year | Notable change |
|---|---|---|
| 1.0 | 2017 | Initial release alongside first Next shipments |
| 1.93 | 2018 | Bug fixes; improved NextBASIC integration |
| 1.98 | 2019 | The "first good" version; widely deployed |
| 2.00 | 2020 | Major release; tilemap and copper extensions |
| 2.05 | 2021 | DMA support; ESP32 WiFi integration |
| 2.06 | 2022 | Bug fixes; performance improvements |
| 2.06b–e | 2023 | Iterative fixes; latest stable is 2.06e |

The version most commonly seen on real Nexts today is **2.06e**. The Next's firmware is field-updatable: a new version can be installed by dropping a single `.bin` file on the SD card and choosing "Update Firmware" from the boot menu.

---

## §2. Next Hardware Context

NextZXOS exists to expose the Next's hardware. This section briefly summarises the hardware features and how NextZXOS presents each one. Detailed hardware documentation is in [../02_hardware/newgen/README.md](../02_hardware/newgen/README.md).

### 2.1 Memory: 2 MB RAM

The Next's defining feature is **2 MB of RAM**, organized as 224 eight-kilobyte banks (`#00`–`#DF`) plus the original 16K/48K/128K memory models. The MMU (Memory Management Unit) maps any 8 KB bank into any of the eight 8 KB slots in the Z80's 64 KB address space.

NextZXOS exposes this via:
- NextBASIC `BANK` commands (`BANK 5 LAYER2`, `BANK 10 LOAD "filename"`).
- Assembly `M_SETRAM` and `M_GETRAM` ESXDOS-compatible functions.
- Next-specific `M_GETSETDRVIVE`-like functions for the bank allocator.

The 2 MB is enough to hold a Layer 2 framebuffer (32 KB), a tilemap (32 KB), a sprite pattern table (16 KB), and still have 1.9 MB left for program code, data, and asset loading. This is roughly 30× the memory available to any original Spectrum programmer.

### 2.2 Layer 2

**Layer 2** is a 256-color framebuffer displayed on top of the standard Spectrum display. It occupies 48 KB of RAM (one 8 KB bank per 1/6 of the screen — six banks total for a 320×256 pixel image at 8 bits per pixel). NextZXOS exposes it via:

- NextBASIC: `#L2 POKE x,y,colour`, `#L2 COPY`, `#L2 CLS`, etc.
- Assembly: Direct memory writes to the Layer 2 banks, with the active bank selected via port `#123B`.
- DMA: Hardware DMA can transfer pixel data into Layer 2 at up to 8 MB/s.

Layer 2 is what makes the Next feel like a different machine: 256-color graphics, software-rendered, with no attribute clash, no timing tricks, and no sacrifice of CPU time to the display.

### 2.3 Tilemap

The **tilemap** is a hardware-accelerated 2D tile-based renderer. It can display 40×32 or 80×32 tiles (each 8×8 or 16×16 pixels) from a tile pattern table in RAM. Scrolling is hardware-supported; the entire tilemap can be panned by writing to two ports.

NextZXOS exposes it via:
- NextBASIC: `#TILEMAP DEFINE`, `#TILEMAP DRAW`, `#TILEMAP SCROLL`.
- Assembly: Direct writes to the tilemap ports (`#6B11`–`#6B1F`).

The tilemap is the basis for most Next games. It allows smooth-scrolling arcade-style action at 50 Hz without the CPU cost of software scrolling.

### 2.4 Hardware sprites

The Next supports up to **64 hardware sprites**, each up to 16×16 pixels in 4-bit or 8-bit color, with rotation, scaling, and per-sprite clipping. The sprite pattern table lives in dedicated RAM banks.

NextZXOS exposes sprites via:
- NextBASIC: `#SPRITE DEFINE`, `#SPRITE MOVE`, `#SPRITE HIT` (collision detection).
- Assembly: Direct writes to the sprite attribute ports.

Hardware sprites eliminate the single biggest headache of original Spectrum game development: software sprite drawing.

### 2.5 The copper

The **copper** is a programmable raster effects unit — inspired by the Amiga copper, hence the name. It runs a tiny instruction set (WRITE, WAIT, SKIP, STOP) and can change any of the Next's I/O ports at any raster position during the frame.

NextZXOS exposes the copper via:
- NextBASIC: `#COPPER LOAD "filename.cop"`, `#COPPER RUN`, `#COPPER STOP`.
- Assembly: Direct writes to the copper data port.

The copper is what makes the Next capable of effects that no original Spectrum could achieve: per-scanline palette changes, hardware horizontal splits, mid-frame mode switches between Layer 2 and tilemap.

### 2.6 DMA

The **DMA controller** can transfer memory-to-memory, memory-to-I/O, or I/O-to-I/O at the Z80's full bus speed (or higher, with the turbo mode engaged). It is used for fast tape loading, sample playback, and bulk graphics copies.

NextZXOS exposes DMA via:
- NextBASIC: `#DMA COPY`, `#DMA SOURCE`, `#DMA DEST`, `#DMA RUN`.
- Assembly: Direct writes to the DMA ports, or via the `F_DMA` NextZXOS function.

A DMA-based tape load of a 48 KB `.TAP` takes less than 1 second — compared to ~3 minutes on the original hardware.

### 2.7 ESP32 (accelerator and WiFi)

The Next includes an **ESP32 module** that serves two purposes:

- **Accelerator**: the ESP32 can run a Z80 emulator at >100 MHz effective clock speed, making it possible to run CPU-intensive software (e.g., complex 3D) at much higher framerates than the native Z80 core.
- **WiFi**: the ESP32 can connect to a WiFi network and provide internet access via a socket-style API.

NextZXOS exposes the ESP32 via dot commands (`*.esp`, `*.wifi`) and via NextBASIC socket functions. ESP32 support is the most actively-developed area of NextZXOS in 2024.

### 2.8 SD card

The Next has a built-in **SD card slot** (SPI-mode, like the DivMMC). The card holds the Next's filesystem (FAT32) with the NextZXOS firmware, dot commands, NextBASIC programs, snapshots, and any user files. Cards up to 2 TB are supported.

The SD card is also where firmware updates live. Updating the Next's firmware is as simple as copying a `.bin` file to the card and choosing "Update" from the boot menu.
---

## §3. Memory Model

The Next's memory model is the most complex of any Spectrum-compatible machine. NextZXOS presents this complexity in a way that hides most of it from casual users while exposing the full power to advanced programmers.

### 3.1 The 8 KB slot model

The Z80 has a 16-bit address bus — 64 KB of addressable memory. The Next's MMU divides this 64 KB into **eight 8 KB slots**:

| Slot | Address range |
|---|---|
| 0 | `#0000`–`#1FFF` |
| 1 | `#2000`–`#3FFF` |
| 2 | `#4000`–`#5FFF` |
| 3 | `#6000`–`#7FFF` |
| 4 | `#8000`–`#9FFF` |
| 5 | `#A000`–`#BFFF` |
| 6 | `#C000`–`#DFFF` |
| 7 | `#E000`–`#FFFF` |

Each slot can be independently mapped to any of the 224 eight-kilobyte RAM banks (`#00`–`#DF`), or to the ROM. The mapping is controlled via the MMU ports at `#50`–`#57` (one port per slot, write-only).

### 3.2 Compatibility modes

The Next can present itself in any of the original Spectrum memory configurations:

- **48K mode**: slot 0–1 = ROM, slot 2–7 = contiguous RAM. This is the standard 48K layout.
- **128K mode**: slot 0–1 = ROM (switchable between ROM 0 and ROM 1), slot 2–4 = RAM bank 5, slot 5 = RAM bank 2, slot 6–7 = switchable between RAM banks 0, 1, 3, 4, 6, 7.
- **Pentagon mode**: similar to 128K but with Pentagon-specific timing and paging.

When running original Spectrum software, NextZXOS sets the appropriate compatibility mode and the software runs unchanged. The MMU slots are simply mapped to the appropriate RAM banks.

### 3.3 Next-native mode

For Next-specific software, the full 2 MB is accessible. A typical Next-native memory layout:

| Slot | Content |
|---|---|
| 0 | ROM (NextZXOS) or user code |
| 1 | User code / NextBASIC workspace |
| 2–3 | Layer 2 bank 0–1 (top of screen) |
| 4–5 | Layer 2 bank 2–3 (middle of screen) |
| 6 | Layer 2 bank 4 (bottom of screen) or sprite patterns |
| 7 | Stack, dot command slot, or Layer 2 bank 5 |

The remaining 217 RAM banks (out of 224 total) are available for the user's data — typically sprite patterns, tile patterns, sample data, and large asset files.

### 3.4 Bank management

NextZXOS exposes bank management through both NextBASIC and the assembly API:

**NextBASIC**:
```
BANK 10 LOAD "sprites.bin"        ; Load file into bank 10
BANK 10 LAYER2 0                  ; Use bank 10 as Layer 2 bank 0
BANK 10 ERASE                     ; Free the bank
```

**Assembly**:
```z80
LD   B,#86              ; M_SETRAM
LD   A,10               ; bank number
LD   (bank_state),A
CALL #0084
```

A small set of Next-specific ESXDOS functions also handles bank allocation and deallocation dynamically — useful for programs that need to allocate banks at runtime rather than hard-coding bank numbers.

### 3.5 The dot command slot

In NextZXOS, the dot command slot is **not limited to 8 KB** as in ESXDOS. A Next dot command can be any size — it is loaded into the upper RAM (typically starting at `#8000`), with banks paged in as needed. This allows Next dot commands to be much more sophisticated than their ESXDOS counterparts: full-screen applications, text editors, even games.

The trade-off is that Next dot commands need to be more careful about memory cleanup. The convention is to use only banks allocated via the NextZXOS bank allocator, and to free them on exit. Code that writes to arbitrary banks will clobber other parts of the system.

### 3.6 ROM footprint

NextZXOS occupies **32 KB of the Next's ROM** (out of 512 KB total ROM). The ROM is banked into the lower slots on demand; it is normally invisible to running software. The 32 KB is divided as:

- `0 KB – 8 KB`: ESXDOS-compatible core (the API surface).
- `8 KB – 16 KB`: Next-specific functions (Layer 2, tilemap, sprites, copper, DMA).
- `16 KB – 24 KB`: NextBASIC interpreter extensions.
- `24 KB – 32 KB`: Boot code, NMI menu, dot-command dispatcher.

The remaining 480 KB of ROM holds the full NextBASIC interpreter, the 128K editor ROM, and various compatibility ROMs (48K BASIC, TR-DOS-compatible routines). All of this is banked in on demand.

---

## §4. NextBASIC Integration

NextBASIC is the ZX Spectrum Next's enhanced BASIC dialect. It is built on the 128K BASIC ROM but adds dozens of new commands and a structured-programming syntax. This section documents how NextBASIC exposes NextZXOS functionality.

### 4.1 The `#` syntax

NextBASIC introduces the `#` prefix for hardware-specific functions. A `#`-prefixed keyword is dispatched to a NextZXOS routine that handles the hardware interaction. Examples:

```
#L2 POKE 100,50,255              ; Plot a pixel at (100,50) in 255-colour
#SPRITE 0,1,SETUP,16,16,0        ; Set up sprite 0 with pattern 1, 16×16 pixels
#TILEMAP SETUP,40,32,8,8         ; Configure tilemap as 40×32 tiles of 8×8 pixels
#COPPER LOAD "rainbow.cop"       ; Load a copper program
#COPPER RUN                      ; Start the copper
```

The full keyword list runs to dozens of commands. They are documented in the NextBASIC manual and exposed via the `*.help` dot command.

### 4.2 File I/O from NextBASIC

NextBASIC inherits ESXDOS's file I/O model via the `#` syntax. A program can open, read, write, and close files directly:

```
10 REM Load a 32 KB data file into bank 10
20 BANK 10 LOAD "level1.bin"
30 REM Open a file for writing
40 HANDLER = #FCREATE "highscore.txt"
50 REM Write a string
60 #FWRITE HANDLER, "SCORE=",SCORE
70 REM Close
80 #FCLOSE HANDLER
```

The file handles are integers (0–255), like file descriptors in POSIX. Up to 16 files can be open simultaneously (the firmware reserves a 16-entry handle table for NextBASIC).

### 4.3 Hardware access from NextBASIC

The hardware-specific NextBASIC commands are designed so that a BASIC programmer can write complete games and demos without ever dropping to assembly. A minimal Layer 2 animation in NextBASIC:

```
10 REM Clear Layer 2 with colour 0
20 #L2 CLS 0
30 REM Draw a moving pixel
40 FOR X = 0 TO 319
50   #L2 POKE X,128,255
60   PAUSE 1
70   #L2 POKE X,128,0
80 NEXT X
```

This program would have taken several pages of assembly on an original Spectrum. On the Next, it fits in 5 lines of BASIC.

### 4.4 Calling ESXDOS functions directly

For operations that NextBASIC does not have a built-in keyword for, NextZXOS exposes the full ESXDOS function catalog via the `#FN` syntax:

```
10 REM Call ESXDOS function #95 (F_OPEN) directly
20 HANDLE = #FN #95, "myfile.bin", 1, 0, 0
30 REM Handle is in A register after the call
```

This is a low-level escape hatch: it lets NextBASIC call any ESXDOS function, including those not wrapped by a friendlier keyword. It is rarely needed but occasionally invaluable.

### 4.5 NextBASIC structured programming

Beyond hardware access, NextBASIC adds structured programming constructs to the original BASIC:

```
10 REM A modern-style IF/THEN/ELSE/END IF
20 IF X > 10 THEN
30   PRINT "Big"
40 ELSE
50   PRINT "Small"
60 END IF

70 REM A WHILE/WEND loop
80 WHILE NOT INKEY$=""
90   PAUSE 1
100 WEND

110 REM A PROCEDURE
120 DEFPROC DRAW_CIRCLE(X, Y, R)
130   #CIRCLE X, Y, R
140 ENDPROC

150 REM A function
160 DEFFN SQUARE(N) = N * N
```

These additions bring NextBASIC roughly in line with later 8-bit BASICs (BBC BASIC, Amstrad Locomotive BASIC). The result is that NextBASIC programs can be considerably more readable than the original Sinclair BASIC.

### 4.6 NextBASIC and dot commands

A NextBASIC program can invoke a dot command via the `SHELL` statement:

```
10 SHELL "*.zip extract archive.zip /tmp/"
```

The dot command runs, completes, and control returns to the NextBASIC program. This makes NextBASIC a scripting language for orchestrating dot commands — a powerful pattern for utility programs.

### 4.7 Limitations

NextBASIC is not without limitations:

- **Single-threaded.** No background tasks; the BASIC program runs alone.
- **No real-time.** The PAUSE statement is the only timing primitive; precise timing requires assembly.
- **No direct sprite pattern access.** Sprite patterns must be defined in a separate file and loaded.
- **No callback from copper.** The copper runs asynchronously, but NextBASIC cannot directly receive interrupts from it (assembly is required for that).

For maximum performance or precise timing, machine code is still the answer. NextBASIC is the right tool for prototyping, scripting, and many games; assembly is required for the highest-performance demoscene work.
---

## §5. Dot Commands

NextZXOS inherits the ESXDOS dot-command system and extends it with Next-specific features. This section documents the differences and the most useful Next-specific dot commands.

### 5.1 Differences from ESXDOS dot commands

The core concept is identical: a `*`-prefixed filename is looked up in the `SYS` directory, loaded into RAM, and executed. The differences from plain ESXDOS:

- **No 8 KB size limit.** A Next dot command can be tens of kilobytes. The 8 KB limit in plain ESXDOS was driven by the DivMMC's small RAM footprint; the Next's 2 MB RAM removes this constraint.
- **Bank awareness.** Next dot commands can use the full bank allocation API. A complex dot command (e.g., a file manager with a graphical UI) can allocate dozens of banks for its workspace.
- **Hardware access.** Next dot commands can directly access Layer 2, sprites, tilemap, and copper. Many do — the Next's graphical dot commands (file browsers, image viewers) use Layer 2 for their UI.
- **Argument parsing helpers.** NextZXOS provides a small library of argument-parsing routines that dot commands can call, simplifying command-line handling.

The result is that Next dot commands are richer and more capable than their ESXDOS counterparts. Some Next dot commands are entire applications in their own right.

### 5.2 Standard NextZXOS dot commands

The NextZXOS distribution ships with a baseline set of dot commands:

| Command | Purpose |
|---|---|
| `*.dot` (built-in) | The dot command dispatcher itself |
| `*.help` | Display dot command help system |
| `*.dir` / `*.ls` | List directory contents |
| `*.cp` / `*.mv` / `*.rm` | File copy / move / delete |
| `*.md` / `*.rd` | Directory make / remove |
| `*.cd` | Change current directory |
| `*.load` / `*.save` | Raw file load/save |
| `*.tap` | Tape image operations (with DMA acceleration) |
| `*.trd` | TR-DOS image operations |
| `*.dsk` | +3 DOS image operations |
| `*.sna` / `*.z80` | Snapshot load/save |
| `*.scr` | Screen image load/save |
| `*.l2` | Layer 2 image load/save (`.nxi` format) |
| `*.spt` | Sprite pattern table load/save |
| `*.cop` | Copper program load/run |
| `*.esp` | ESP32 control (boot, firmware update) |
| `*.wifi` | WiFi scan / connect |
| `*.up` | Firmware update |
| `*.exit` | Exit current dot command |
| `*.sys` | System information |
| `*.bank` | Bank allocation debugging |

### 5.3 Community dot commands

The Next community has contributed hundreds of additional dot commands. Notable examples:

- **`*.nextimg`**: image viewer supporting PNG, JPG, GIF, BMP, and various retro formats.
- **`*.modplayer`**: ProTracker MOD module playback.
- **`*.ymplayer`**: YM music module playback (Atari ST / Spectrum AY format).
- **`*.esppload`**: ESP32 program loader.
- **`*.ftp`**: FTP client via the ESP32.
- **`*.httpget`**: HTTP client via the ESP32.
- **`*.modem`**: TCP modem emulator for connecting to BBSes via the ESP32.
- **`*.terminal`**: VT100 terminal emulator.
- **`*.zxpaint`**: full-screen Layer 2 paint program.
- **`*.nextor`**: disk image editor.

A typical Next user's SD card has 50+ dot commands installed.

### 5.4 Writing a Next dot command

The skeleton for a Next dot command is similar to an ESXDOS dot command but uses Next-specific entry conventions. A minimal Next dot command (in NextBASIC):

```
1 REM *.hello.dot
10 PRINT "Hello, Next!"
20 REM Return to the calling program (or BASIC prompt)
30 STOP
```

Save this as `hello.dot` on the SD card (via the Next's SD card slot directly, or via a PC if the card is removed). Type `*.hello` at the NextBASIC prompt and the message prints.

A Next dot command in machine code (sjasmplus assembly):

```z80
        DEVICE NEX                ; Next target
        ORG  $8000                ; Next dot commands load at #8000
        
        DB   $DD                  ; dot command magic byte
        
        ; --- entry ---
        LD   HL,msg
loop:   LD   A,(HL)
        OR   A
        RET  Z                    ; null terminator: return
        RST  $10                  ; print character
        INC  HL
        JR   loop
        
msg:    DB   "Hello, Next!",13,0
```

The z88dk C compiler provides a `+nextdot` target that handles all the boilerplate, so dot commands can be written in C with full access to the Next hardware via a library.

---

## §6. Filesystem

NextZXOS uses **FAT32** as its filesystem, identical to ESXDOS in concept but with Next-specific directory conventions.

### 6.1 Card layout

A typical Next SD card is laid out as:

```
/
├── SYS/                    ; NextZXOS system files
│   ├── nextzxos.bin        ; the firmware itself
│   ├── esxdos.rom          ; ESXDOS compatibility layer
│   ├── *.dot files         ; built-in and user-installed dot commands
│   └── ...
├── BASIC/                  ; NextBASIC programs
│   ├── mygame.bas
│   └── libs/               ; NextBASIC library files
├── GAMES/                  ; games (typically as .z80 or .nex)
│   ├── ManicMiner.z80
│   └── ...
├── MUSIC/                  ; AY music modules
├── DEMOS/                  ; Next-specific demos
├── SNAPSHOTS/              ; .z80 / .sna snapshots
├── IMG/                    ; image files (.nxi, .scr, .png)
├── ESP/                    ; ESP32 firmware and programs
└── MISC/                   ; anything else
```

The `SYS/` directory is mandatory — NextZXOS looks there for its dot commands. Other directories are convention.

### 6.2 The `.nex` format

The Next has its own native executable format, `.nex`. A `.nex` file is a complete program package containing:

- A header with the program's name, author, and version.
- The memory banks the program uses, with their contents.
- The CPU register state to start with.
- Optional Layer 2, tilemap, sprite, and copper initialisation data.
- Optional NextBASIC program code.

Loading a `.nex` file is a single dot command: `*.nexload mygame.nex`. NextZXOS reads the header, allocates the required banks, populates them, sets the register state, and jumps to the entry point. The program runs immediately.

The `.nex` format is what most modern Next-native software ships as. It is to the Next what `.TRD` is to the Pentagon — the canonical distribution format.

### 6.3 Long filenames

FAT32 long filenames are fully supported, identical to ESXDOS. Files can have names up to 255 characters with mixed case, spaces, and most punctuation.

### 6.4 Compatibility with ESXDOS filesystem

A SD card from a DivMMC can be inserted directly into a Next. The Next will read the existing filesystem and dot commands without modification. ESXDOS dot commands that do not use the DivMMC's specific hardware ports will run on the Next unchanged.

The reverse is not always true: Next-specific dot commands and `.nex` files will not run on a DivMMC. The Next's filesystem is a superset.

---

## §7. The Assembly API

NextZXOS's assembly API is **ESXDOS-compatible** plus Next-specific extensions. This section documents the extensions.

### 7.1 ESXDOS-compatible core

The entire ESXDOS function catalog (see [esxdos.md](esxdos.md) §6.2) is supported, with the same dispatch mechanism:

```z80
LD   B,function        ; ESXDOS function number
; ... set up registers per function table ...
CALL #0084             ; dispatch
```

Code that worked against ESXDOS 0.86 will run against NextZXOS 2.06e with no changes. The only differences are subtle:

- **Faster SPI.** The Next's SD card interface is faster than the DivMMC's, so file I/O is several times quicker.
- **More file handles.** NextZXOS allows up to 16 simultaneously-open files (the DivMMC limits to 8 in most firmware versions).
- **No 8 KB dot command limit.** Assembly code can be loaded into the larger Next dot command slot.

### 7.2 Next-specific functions

NextZXOS adds Next-specific functions to the dispatch table. These use function numbers in the `#C0`-range, distinct from the ESXDOS `#80`-`#A8` range:

| `B` | Name | Purpose |
|---|---|---|
| `#C0` | M_GETNEXTREG | Read a Next register |
| `#C1` | M_SETNEXTREG | Write a Next register |
| `#C2` | M_LAYER2 | Layer 2 control (bank select, palette) |
| `#C3` | M_TILEMAP | Tilemap control |
| `#C4` | M_SPRITE | Sprite control |
| `#C5` | M_COPPER | Copper control (load, run, stop) |
| `#C6` | M_DMA | DMA control |
| `#C7` | M_PALETTTE | Palette manipulation |
| `#C8` | M_VIDEO mode | Video mode switch |
| `#C9` | M_BANKALLOC | Allocate a RAM bank |
| `#CA` | M_BANKFREE | Free a RAM bank |
| `#CB` | M_BANKREAD | Read from a specific bank |
| `#CC` | M_BANKWRITE | Write to a specific bank |

These functions handle the most common Next hardware interactions. For low-level hardware access, programs typically write directly to the Next's I/O ports rather than going through the NextZXOS API — this is faster and gives finer control.

### 7.3 Worked example: load and display a Layer 2 image

```z80
; Load "image.nxi" and display it on Layer 2
DI
LD   B,#95              ; F_OPEN
LD   HL,fn
LD   A,1                ; mode: read
CALL #0084
JR   C,open_ok
JP   error

open_ok:
LD   (handle),A

; Read the .nxi header (16 bytes)
LD   B,A
LD   B,#98              ; F_READ
LD   HL,header
LD   DE,16
CALL #0084

; For each of 6 Layer 2 banks, read 8 KB
LD   B,6
load_loop:
PUSH BC
;   - select Layer 2 bank via port #123B
;   - read 8 KB from file via F_READ
;   - increment Layer 2 bank
POP  AF
POP  BC
DJNZ load_loop

; Close the file
LD   B,(handle)
LD   B,#96              ; F_CLOSE
CALL #0084
EI
RET

fn:     DB   "image.nxi",0
handle: DB   0
header: DS   16
```

This pattern — open, loop over banks, close — is the universal NextZXOS file-loading idiom.

### 7.4 Direct hardware access

For maximum performance, Next programmers usually bypass the NextZXOS API and access hardware directly:

```z80
; Set Layer 2 bank 0
LD   BC,#123B
LD   A,0
OUT  (C),A

; Write a pixel at the top-left of the screen
LD   A,255             ; colour index
LD   (#0000),A
```

This is faster (no API call overhead) and gives the programmer complete control. The NextZXOS API exists as a convenience and a portability layer; for demoscene work, direct hardware access is standard.
---

## §8. Programming Patterns

NextZXOS programming shows clear recurring patterns. This section documents the three most important ones.

### 8.1 The copper-based effect

A common Next pattern: use the copper for raster effects (per-scanline palette changes, mid-frame mode switches) while the main program runs in the foreground.

A minimal copper program (in NextBASIC):

```
10 REM Load a copper program that cycles the border colour per scanline
20 #COPPER LOAD "rainbow.cop"
30 REM Run the copper
40 #COPPER RUN
50 REM The copper runs autonomously now; do other work
60 FOR X = 1 TO 1000
70   REM Some main-program work
80 NEXT X
90 REM Stop the copper
100 #COPPER STOP
```

The copper program `rainbow.cop` is a series of `WAIT` and `WRITE` instructions in the copper's tiny ISA. The copper runs in parallel with the Z80 — it does not consume CPU cycles — making it possible to do per-scanline effects that no original Spectrum could match.

### 8.2 The sprite-based game loop

The canonical Next game loop uses the tilemap for the background, sprites for moving objects, and a single frame-synchronized main loop:

```
10 REM Setup tilemap and sprites
20 #TILEMAP SETUP 40,32,8,8
30 #TILEMAP LOAD "level1.til"
40 #SPRITE 0,1,SETUP,16,16,0       ; Player sprite

100 REM Main loop
110 REM Wait for vblank
120 WAIT 1
130 REM Read input
140 K$ = INKEY$
150 REM Update player position
160 IF K$ = "8" THEN PX = PX - 2
170 IF K$ = "9" THEN PX = PX + 2
180 REM Move sprite
190 #SPRITE 0,PX,PY
200 REM Check collisions
210 IF #SPRITE HIT(0,1) THEN GOSUB 1000
220 GOTO 110
```

This pattern — wait for vblank, read input, update state, draw sprites, repeat — is the universal 2D game loop on the Next. It runs at a stable 50 Hz.

### 8.3 The Next-native file format

Programs that need to save state — high scores, save games, etc. — typically use a simple binary format loaded via `*.load`:

```
10 REM Save high score
20 HANDLE = #FCREATE "score.dat"
30 #FWRITE HANDLE, SCORE
40 #FCLOSE HANDLE

100 REM Load high score
110 HANDLE = #FOPEN "score.dat"
120 IF HANDLE = -1 THEN SCORE = 0: GOTO 200
130 SCORE = #FREAD HANDLE
140 #FCLOSE HANDLE
```

This is essentially the same pattern as on ESXDOS, just expressed in NextBASIC rather than assembly.

---

## §9. Modern Status

NextZXOS in 2024 is the most actively-developed Spectrum-compatible OS. This section documents the current state.

### 9.1 Active development

NextZXOS development is led by Garry Lancaster with contributions from the Next community. Development is open and public on GitHub. The current focus areas:

- **ESP32 integration.** Making the ESP32's accelerator and WiFi capabilities more accessible from NextBASIC and machine code.
- **Hardware bug workarounds.** The Next FPGA has a few known issues (specifically around sprites and DMA in some configurations); NextZXOS provides workarounds.
- **Performance tuning.** The NextZXOS file I/O has been measured at 800+ KB/s on fast SD cards — about 8× what was possible on the DivMMC.
- **Documentation.** The NextZXOS manual is a living document, regularly updated to reflect new features.

New firmware releases appear roughly every 3–6 months. The Next's firmware is field-updatable via an SD card file, so adopting new versions is trivial.

### 9.2 The Next ecosystem

The NextZXOS ecosystem extends well beyond the Next itself:

- **Next-compatible clones.** Several FPGA projects (SpecNext, MiSTer Spectrum Next core, etc.) run NextZXOS or a compatible OS.
- **Cross-development tools.** z88dk, sjasmplus, and various modern IDEs target the Next directly. Code can be cross-compiled on a PC and dropped onto the Next's SD card.
- **Community software.** Hundreds of Next-specific games, demos, and utilities have been released since 2017. The Next has its own demoscene (centered on the Outline and Nova parties).
- **Documentation.** The Next has more English-language documentation than any other Spectrum platform. The official manual (`specnext.dev`) is comprehensive.

### 9.3 Where to get help

The NextZXOS and Next community lives on:

- **specnext.dev**: the official documentation site.
- **The ZX Spectrum Next forum** (spectrum-next.net): the primary community hub.
- **The "ZX Spectrum Next" Facebook group**: smaller but very active.
- **The Next's GitHub organisation**: source code, issue tracking, community contributions.
- **Outline party** (Netherlands, annual): the primary Next demoscene event.
- **Nova party** (UK, annual): another major Next event.

For anyone starting Spectrum development in 2024 with a focus on modern hardware, the Next is the natural choice. It is the only modern Spectrum-compatible machine with active commercial production, an active software scene, and active OS development.

### 9.4 The future

The Next team has stated that NextZXOS will continue to evolve as long as the Next hardware is in production (which is open-ended; the Next is currently manufactured by SpecNext Ltd. in batches of several thousand units per year). Planned future work includes:

- Better NextBASIC compiler (a separate tool that compiles NextBASIC to native machine code for speed).
- More complete ESP32 integration (TCP/IP stack, HTTP server, etc.).
- Improvements to the copper (more instructions, more registers).
- Possible hardware floating-point support via a future FPGA update.

The Next is not a static platform. It continues to grow.

---

## §10. Cross-References

### 10.1 Within the Operating Systems section

- [README.md](README.md) — section index
- [esxdos.md](esxdos.md) — the parent OS; NextZXOS extends the ESXDOS API
- [trdos.md](trdos.md) — TR-DOS compatibility is preserved in NextZXOS
- [plus3dos.md](plus3dos.md) — +3 DOS compatibility is also preserved
- [rom_128k.md](rom_128k.md) — NextZXOS uses the 128K editor ROM as its base
- [basic_dialects.md](basic_dialects.md) — NextBASIC is one of the BASIC dialects covered there

### 10.2 Outside the section

- [../02_hardware/newgen/README.md](../02_hardware/newgen/README.md) — the Next hardware itself
- [../05_development/03_memory_and_io/memory_and_io_next.md](../05_development/03_memory_and_io/memory_and_io_next.md) — Next memory map and I/O ports
- [../07_demoscene/demo_frameworks.md](../07_demoscene/demo_frameworks.md) — modern demo frameworks target the Next
- [../07_demoscene/notable_demos.md](../07_demoscene/notable_demos.md) §6 — modern revival demos on the Next

### 10.3 External resources

- **Official [NextZXOS](https://gitlab.com/thesmog358/tbblue) documentation**: https://specnext.dev/
- **[NextZXOS](https://gitlab.com/thesmog358/tbblue) source code (GitHub)**: https://github.com/Threetwosevensix/NextZXOS
- **[ZX Spectrum Next forum](https://specnext.org/)**: https://spectrum-next.net/
- **The Next's official site**: https://www.specnext.com/
- **Outline party**: https://outline-party.org/
- **[z88dk](https://github.com/z88dk/z88dk) Next target**: https://github.com/z88dk/z88dk/wiki/Platform-ZX-Next
- **SJASMPlus Next support**: https://github.com/z00m128/[sjasmplus](https://github.com/z00m128/sjasmplus)/blob/master/docs/Next.htm

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/). Attribute as "NextZXOS — The ZX Spectrum Next Operating System, from the ZX Spectrum Knowledge Base".
