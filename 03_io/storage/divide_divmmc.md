# The DivIDE and DivMMC: Hardware and Setup Guide

**Scope:** A **hardware and practical-setup** treatment of the **DivIDE** (Zeax, 2007) and the **DivMMC** (Zoxon, 2013) — the two expansion cards that together define modern real-hardware Spectrum mass storage. This article covers the physical boards, the firmware boot sequence, the TR-DOS virtual-floppy emulation layer, and how to prepare the storage card.

It is the **hardware companion** to [esxdos.md](../../04_operating_systems/esxdos.md), which covers the ESXDOS operating system — the DOS API, the dot-command interface, and the assembly calling conventions. The two articles are designed to be read together: this one answers "what is the box and how do I set it up?", the other answers "how do I program the DOS that runs on it?".

**Audience:** Retro-hardware buyers choosing between a DivIDE and a DivMMC, new Spectrum owners setting up their first SD card, emulator authors modeling the DivIDE boot sequence, and anyone curious what lives inside the small plastic case plugged into the back of a 2024 Spectrum.

**Prerequisites:** The [IDE interface article](ide_interface.md) covers the protocol and port map; the [overview article](hdd_overview.md) situates these cards in the storage story. No familiarity with ESXDOS itself is required — this article references it but defers the details to its own article.

**Depth:** Medium-deep. Board anatomy, boot sequence, and the virtual-floppy mechanism in detail; the DOS internals are cross-referenced rather than repeated.

---

## §1. The DivIDE and DivMMC

### 1.1 Two cards, one identity

The **DivIDE** (Dylan N. Smith, "Zeax", 2007) and the **DivMMC** (Zoxon, 2013) are the two expansion cards that together define modern real-hardware Spectrum mass storage. Both decode the same I/O ports (`#E3`–`#E7`), both page their firmware ROM into the same address window, both hook the same NMI vector, and both run the same **ESXDOS** firmware. Software written for a DivIDE runs unchanged on a DivMMC, and vice versa.

The difference is purely at the storage-medium layer: the DivIDE speaks IDE/ATA to a CompactFlash card or hard disk, while the DivMMC speaks SPI to an SD card. The ESXDOS firmware contains both drivers and auto-detects which hardware it is running on. From the user's and the programmer's perspective, the two cards are interchangeable — which is why the SD-based DivMMC has so thoroughly displaced the IDE-based DivIDE since 2013.

### 1.2 Hardware here, software elsewhere

The DivIDE and DivMMC are **hardware**; ESXDOS is the **software** that runs on them. This article covers the boards themselves, the boot sequence, the TR-DOS virtual-floppy emulation layer, and how to prepare the storage card. The ESXDOS dot-command syntax, the assembly API (`M_GETSETDRV`, `F_OPEN`, …), and the FAT internals are covered in the companion article [esxdos.md](../../04_operating_systems/esxdos.md). In short: if you are holding a physical card and asking what to plug in and where files go, read on; if you are writing Z80 code that opens a file, switch to [esxdos.md](../../04_operating_systems/esxdos.md).

## §2. The DivIDE Hardware

### 2.1 Board anatomy

The DivIDE is a single PCB roughly the size of a playing card, designed to plug into the Spectrum's rear-edge connector. Its principal components are:

- **The edge connector** — a 2×28-way finger that mates with the Spectrum's expansion bus, carrying the address, data, and control lines plus +5V and GND.
- **A 40-pin IDE header** (2×20) for a CompactFlash card via a passive adapter, or a raw IDE cable to a hard disk. Most DivIDE owners use a small CF-to-IDE adapter board.
- **A 27C512 EPROM socket** (or a 29F-series flash chip on later revisions) holding up to 64 KB of firmware. ESXDOS occupies the lower 8 KB; the rest can hold a TR-DOS compatibility image, a "fatware" file browser, or alternate firmware.
- **A paging PAL/GAL or CPLD** that implements the memory-banking logic — the most important active component on the board.
- **The NMI button** — a small tactile switch wired to the Spectrum's `/NMI` line (pin 17 of the edge connector). Pressing it invokes the ESXDOS main menu.
- **An optional RTC** (Dallas DS1307 or equivalent) soldered on later revisions, connected to the Z80 via two I/O pins bit-banging I²C. Used for file timestamps.
- **A pass-through edge connector** on the rear of the board, so further peripherals (a printer interface, a sound expander) can be daisy-chained behind the DivIDE.

### 2.2 The port block

The DivIDE responds to I/O reads and writes in the `#E3`–`#E7` block (with mirrors at `#A3`–`#A7` on some revisions), as documented in [ide_interface.md §5.1](ide_interface.md). The three primary ports are `#E3` (IDE data low), `#E5` (IDE data high), and `#E7` (the control register). The control register is the interface's nerve center: it selects the visible ROM bank, toggles the firmware write-protect, and on some revisions controls an IDE bank-switch bit.

### 2.3 Power and the CF choice

The DivIDE draws its power from the Spectrum's +5V rail through the edge connector. A spinning hard disk can pull 500 mA or more at spin-up — enough to crash an original 48K Spectrum, whose +5V rail is rated for only ~700 mA total. This is why nearly every DivIDE in practice uses a **CompactFlash card** rather than a hard disk: CF draws 30–80 mA, well within the rail's budget, and a CF card in True IDE mode is electrically identical to an IDE drive from the firmware's perspective.

A +2A or +3 Spectrum, with its more substantial power supply, can drive a small laptop hard disk through a 44-pin IDE cable — but this is rare and inadvisable. CF is the standard.

## §3. The DivMMC Hardware

### 3.1 The redesign

The **DivMMC** (Zoran "Zoxon" Mačković, 2013) is a ground-up redesign of the DivIDE that replaces the IDE/CF connector with an **SD card slot**. The motivation was practical: by 2013, CompactFlash cards were becoming hard to find and expensive, while SD cards (especially MicroSD) were commodity items. The DivMMC brings the same ESXDOS experience to a medium that is still manufactured in 2024.

The DivMMC's principal components mirror the DivIDE's, with two substitutions:

- **An SD card socket** (full-size SD on early boards, MicroSD on later ones) replaces the IDE header. The socket is wired to the same SPI interface that the firmware driver expects.
- **An SPI bridge** (a small CPLD or discrete logic) replaces the IDE buffer, translating the Z80's port writes into the SD card's SPI command protocol.

Everything else — the edge connector, the firmware ROM socket, the paging logic, the NMI button — is functionally identical to the DivIDE. The same ESXDOS firmware binary runs on both; it probes the hardware at boot and loads the appropriate driver (IDE or SPI).

### 3.2 Why the DivMMC won

The DivMMC displaced the DivIDE for four concrete reasons:

- **Medium availability.** MicroSD cards are sold in every supermarket; CompactFlash cards are specialist items. A new Spectrum user can buy a DivMMC and a MicroSD card in the same afternoon.
- **Physical size.** The DivMMC board is small enough to fit inside a 48K Spectrum case, behind the edge connector. Several "internal" DivMMC variants mount entirely inside the machine, invisible from the outside. The DivIDE with its 40-pin header and CF adapter is necessarily bulkier.
- **Power.** An SD card in SPI mode draws single-digit milliamps when idle and ~25 mA when reading — less than even a CF card. The DivMMC never stresses the Spectrum's power rail.
- **Capacity.** SDHC cards (4–32 GB) and SDXC cards (64 GB–2 TB) are routine; ESXDOS handles them transparently. Nobody fills such a card with Spectrum software, so capacity ceases to be a concern.

The DivIDE remains relevant for users who already own one, who prefer CompactFlash's physical write-protect switch, or who run DivIDE-specific software that expects IDE timing. For a new purchase in 2024, the DivMMC is the default.

### 3.3 The dual-medium future: the ZX Spectrum Next

The **ZX Spectrum Next** (2017) absorbs the DivMMC concept into the machine itself, providing **two MicroSD slots** driven by NextZXOS (an ESXDOS derivative). The primary slot holds the machine's firmware and core files; the secondary slot holds user software. No expansion card is needed. See [nextzxos.md](../../04_operating_systems/nextzxos.md) for the Next-specific extensions.

## §4. The Firmware Boot Sequence

ESXDOS is unusual among Spectrum DOSes in that it does **not** take control at power-on. The Spectrum boots its own ROM normally, shows the `(C) 1982 Sinclair Research` message, and drops into BASIC as if the DivIDE/DivMMC were not there. ESXDOS only reveals itself when the user presses the **NMI button**. This "zero footprint when idle" property is one of ESXDOS's design goals ([esxdos.md §1.2](../../04_operating_systems/esxdos.md)) and is central to understanding why the boot sequence works the way it does.

### 4.1 Power-on

At power-on, the DivIDE/DivMMC's paging logic is in its default state, in which:

- The interface's firmware ROM is **not visible** in the Spectrum's address space. The Spectrum's own ROM owns `#0000`–`#3FFF`.
- The control register's **conmem** bit (the "configuration memory" enable) is clear, so the DivIDE ROM is paged out.
- A single status bit — the **"auto-map"** flag — is set, which is what allows ESXDOS to hook back in later.

The Spectrum therefore boots normally. The DivIDE is electrically present (it decodes its I/O ports) but invisible. The only sign of its existence at this stage is that pressing the NMI button will not trigger the standard Spectrum NMI (which prints "NMI in page 1" or similar) — instead it triggers the DivIDE's firmware, because the paging logic intercepts the `/NMI` line before the Spectrum ROM sees it.

### 4.2 The NMI hook

When the user presses the NMI button, the DivIDE/DivMMC paging logic performs three actions in hardware, in a single bus cycle:

1. It **pages its firmware ROM in** at `#0000`–`#1FFF` (the low 8 KB of the address space), overriding the Spectrum ROM for that window.
2. It forces the Z80 to take the **NMI** — which vectors through `#0066`, now pointing into the freshly paged-in DivIDE ROM.
3. The DivIDE ROM's code at `#0066` is the ESXDOS NMI handler, which saves registers, switches in the rest of the firmware, and draws the main menu.

This is the crucial trick: the DivIDE does not need the Spectrum ROM's cooperation to take over. The hardware paging intercepts the NMI vector directly, so ESXDOS gains control even from the middle of running software (a game, a demo) without corrupting the machine state. When the user exits the ESXDOS menu, the firmware pages itself back out, restores registers, and returns via `RETN` — the running program never knows it was interrupted.

### 4.3 The "auto-map" mechanism for machine-code calls

After the NMI handler has run at least once, ESXDOS installs a small **hook** in RAM that allows subsequent machine-code programs to invoke ESXDOS API functions without pressing the NMI button. The mechanism is the **auto-map** flag: when a program executes an `RST 8` (or a `CALL` to a specific hook address, depending on firmware version), the paging logic briefly pages the DivIDE ROM back in, executes the requested function, and pages it back out.

This is how dot commands and application programs call `M_GETSETDRV`, `F_OPEN`, `F_READ`, and the rest of the ESXDOS API. The programmer sees a normal subroutine call; the hardware handles the ROM paging transparently. The full API catalog is in [esxdos.md §6](../../04_operating_systems/esxdos.md).

### 4.4 Why ESXDOS does not patch the BASIC ROM

Earlier Spectrum DOSes (TR-DOS, +3 DOS) integrate with BASIC by **patching the ROM** — intercepting the `LOAD`, `SAVE`, and `CAT` keywords so they redirect to the DOS. ESXDOS deliberately does not do this. Instead, it provides file access through **dot commands** typed at the BASIC prompt: `*.load "game.z80"`, `*.dir`, `*.tap2trd`.

The reason is robustness: a ROM patch must fight the Spectrum's existing ROM routines and is fragile across ROM versions (a 48K Issue 3 ROM and an Issue 6 ROM differ in the bytes a patch would overwrite). The dot-command approach works on every Spectrum variant without modification, because it never touches the ROM. The trade-off is that BASIC's native `LOAD`/`SAVE` continue to mean tape, not disk — which is why ESXDOS users always invoke file operations through `*.` commands.

## §5. TR-DOS Image Emulation

### 5.1 The problem: a huge floppy-era software library

By the time the DivIDE appeared in 2007, the Soviet and post-Soviet Spectrum scene had accumulated an enormous library of TR-DOS software — games, demos, utilities, disk magazines — all written to run on a Beta 128 floppy controller under TR-DOS. This software talks to the **TR-DOS hook codes** (the `#3D13`-family entry points documented in [trdos.md](../../04_operating_systems/trdos.md)) and, through them, to the **WD1793 floppy controller** at ports `#1F`/`#3F`/`#5F`/`#7F`/`#FF`.

A DivIDE owner who wanted to run this software faced a problem: the DivIDE has no WD1793, no floppy drive, and speaks IDE/CF, not floppy. Porting every TR-DOS program to the new interface was infeasible. The solution was to **emulate the Beta 128 in firmware**.

### 5.2 divman and divese

The DivIDE firmware includes a layer known variously as **divman** (the DIVide MANager) and **divese** (the DIVide ESEmulator). Its job is to present a `.TRD` file stored on the IDE/CF volume as if it were a physical floppy in a Beta 128 drive, complete with the WD1793 register interface.

The mechanism works at two levels:

1. **Port trapping.** When TR-DOS software reads or writes ports `#1F`, `#3F`, `#5F`, `#7F`, or `#FF` (the WD1793 register file and the floppy-system register), the DivIDE firmware intercepts the I/O cycle. Instead of letting the access reach non-existent hardware, it routes the access to an emulated WD1793 state machine maintained in firmware.

2. **Image mapping.** The emulated WD1793's "tracks" and "sectors" are mapped onto sectors of the `.TRD` file on the storage volume. When the software issues a `READ SECTOR` command, the firmware translates the (track, sector) pair into a byte offset within the `.TRD` file, issues a FAT read through ESXDOS, and returns the data as if it came from a floppy.

The result is that **a TR-DOS program runs unmodified**, reading and writing a virtual floppy that is actually a file on a CompactFlash or SD card. The user selects the `.TRD` image from the ESXDOS menu (or via a dot command like `*.eject` / `*.trd file.trd`), and the chosen image becomes "the disk in drive A" until the user ejects it.

### 5.3 Limitations

The emulation is near-perfect for software that uses the TR-DOS hook codes correctly, but it has limits:

- **Direct hardware access breaks.** Software that bypasses the hook codes and talks to the WD1793 registers directly — to use a non-standard sector size, say, or a custom interleaving — may not be emulated correctly, because divman models the standard TR-DOS geometry. Copy-protected disks and custom loaders often fall here.
- **Timing-dependent software.** Programs that rely on exact WD1793 command timing (some fast loaders do) may run at the wrong speed, because the emulated controller responds instantly rather than after real seek and settle delays.
- **Write behavior.** Writes to the virtual floppy modify the `.TRD` file on the storage volume, which is usually desired (save games work) but can corrupt a master image if the user is not careful. The dot command `*.wp` (write-protect) marks the current image read-only to prevent this.

For the vast majority of the TR-DOS library — games that load and run, demos that stream data — the emulation is transparent and perfect. The `.TRD` image format itself is documented in [trd_scl_formats.md](trd_scl_formats.md).

### 5.4 The same trick for tape

An analogous mechanism emulates the **tape interface**. A `.TAP` or `.TZX` file on the storage volume can be "inserted" as if it were a tape; the DivIDE firmware intercepts the ROM's `LD-BYTES` routine (or feeds pulses to port `#FE`) and streams the file's data into the loading routine. This lets tape-era software run from the storage card with no conversion. See [tap_format.md](tap_format.md) and [tzx_format.md](tzx_format.md) for the image formats.

## §6. Preparing the Storage Card

### 6.1 Format: FAT16 or FAT32

The card must be formatted with a **Master Boot Record (MBR)** partition table and a single **FAT16 or FAT32** volume. The choice between the two depends on capacity:

- **FAT16** for cards up to 2 GB. Faster to parse on the Z80 (smaller file-allocation table), and the only FAT variant the earliest ESXDOS versions support.
- **FAT32** for cards 4 GB and larger. Required for SDHC cards. Modern ESXDOS (0.85+) handles FAT32 correctly, including long filenames.

Cards between 2 GB and 4 GB can be either; FAT32 is the safer modern choice. A modern PC's default "format SD card" operation (right-click → Format, or `mkfs.fat`) produces a correct result in almost all cases. The one pitfall is that some PC utilities create a **GPT** partition table or an **exFAT** volume by default on large cards; ESXDOS understands neither. Always specify MBR + FAT explicitly on cards over 32 GB, where Windows in particular defaults to exFAT.

### 6.2 The partition layout

The card's first sector (LBA 0) is the **MBR**, containing the partition table at offset `0x1BE`. ESXDOS reads this table, finds the first FAT-type partition (type `0x01`, `0x04`, `0x06`, `0x0B`, `0x0C`, or `0x0E`), and mounts it. Multiple partitions are supported by later firmware versions, but a single primary partition is the standard and safest layout. See [hdd_partitioning.md](hdd_partitioning.md) for the byte-level partition table structure.

### 6.3 The SYS directory and the dot commands

ESXDOS expects a **`/SYS` directory** at the root of the volume, containing the dot-command programs. When the user types `*.dir` at the BASIC prompt, ESXDOS looks for `/SYS/DIR` (the dot command's name, uppercased, with no extension) and loads it into the dot-command RAM page.

A typical `/SYS` directory contains:

| File | Purpose |
|---|---|
| `DIR` | Lists the current directory |
| `CD` | Changes directory |
| `LOAD` | Loads a `.z80`/`.sna` snapshot and runs it |
| `TAP2TRD` | Converts a `.tap` file to a `.trd` image |
| `TRD` | Mounts a `.trd` image as the virtual floppy |
| `EJECT` | Ejects the current virtual floppy |
| `WP` | Toggles write-protect on the current image |
| `BASIC` | Returns to the BASIC prompt from a dot command |

Hundreds of additional dot commands are available from the community (file managers, media players, network tools). They all live in `/SYS` or in subdirectories that the user adds to the search path. The dot-command loading mechanism is documented in [esxdos.md §4](../../04_operating_systems/esxdos.md).

### 6.4 Where the rest of the files go

Beyond `/SYS`, the volume's structure is up to the user. Typical conventions:

- `/GAMES` — `.z80` and `.sna` snapshots of games, often organized by genre or year.
- `/TRDOS` — `.trd` images for the TR-DOS virtual floppy.
- `/TAPES` — `.tap` and `.tzx` images for the tape emulator.
- `/DEMOS` — demoscene productions.
- `/MUSIC` — `.pt3`, `.ay`, `.psc` music files for the various players.

The naming is conventional, not enforced. ESXDOS's FAT driver supports long filenames, so files can be named descriptively (`Chuckie Egg (1983).z80`) rather than forced into 8.3. The one constraint is that dot-command names themselves must be **uppercased 8.3** (`DIR`, not `dir`), because the dot dispatcher matches case-sensitively on some firmware versions.

### 6.5 A worked setup, start to finish

To set up a fresh DivMMC with a new 8 GB MicroSD card:

1. On a PC, format the card as **MBR + FAT32** (use Rufus on Windows, or `mkfs.fat -F 32` on Linux, or Disk Utility on macOS with "MS-DOS (FAT)").
2. Create a `/SYS` directory at the card's root.
3. Copy the ESXDOS dot-command binaries into `/SYS` (these ship with the firmware distribution).
4. Create `/GAMES`, `/TRDOS`, and any other directories, and copy software into them.
5. Eject the card from the PC, insert it into the DivMMC, and power on the Spectrum.
6. Press the **NMI button**. The ESXDOS main menu appears.
7. From the menu, browse to `/GAMES`, select a `.z80` file, and it loads.

The whole process takes about five minutes. The card is now a complete Spectrum software library in a space the size of a fingernail.

## §7. Hardware Revisions and Clones

### 7.1 DivIDE revisions

The original DivIDE went through several hardware revisions, the most significant being:

- **DivIDE 57c** — the most common revision, with the 27C512 ROM socket and the standard `#E3`–`#E7` port block. This is the revision most emulator authors model.
- **DivIDE+** — an enhanced variant with additional RAM and a more flexible paging CPLD, allowing larger firmware images and faster buffering.
- **ZXCF** — a related design that uses a CompactFlash socket directly on the board (no IDE adapter needed). Functionally similar to the DivIDE but with a different physical layout.

All run ESXDOS and are software-compatible at the API level.

### 7.2 DivMMC variants

The DivMMC has been cloned and re-spun many times since 2013. The principal variants are:

- **DivMMC "Future" / "FutureWas"** — the most widely manufactured 2020s variant, with a MicroSD socket, a 3D-printed or injection-molded case, and a refined power circuit. Sold ready-to-use.
- **DivMMC "Resident"** — a variant designed to mount entirely inside a 48K or 128K Spectrum, drawing power from the internal rail and presenting the SD slot at the rear. No external dongle.
- **DivMMC "Slim"** — a bare-board version for DIY enclosure, the cheapest option.
- **ZX Spectrum Next internal SD** — the Next's built-in MicroSD slots are DivMMC-compatible at the firmware level, running NextZXOS.

All of these run the same ESXDOS firmware and accept the same FAT-formatted card. The choice between them is physical (case vs bare board, external vs internal) rather than functional.

### 7.3 Emulator modeling

For emulator authors, the practical takeaway is that modeling the **DivIDE 57c port block** (`#E3`–`#E7`) and the ESXDOS NMI/menu behavior is sufficient to run the overwhelming majority of modern Spectrum software. Fuse, ZEsarUX, CSpect, and UnrealSpeccy all do this. The DivMMC needs no separate modeling — it is the same port block with an SPI driver swapped in for the IDE driver, which the firmware handles invisibly.

## §8. Cross-references and License

### 8.1 Within this sub-section

| Article | Covers |
|---|---|
| [hdd_overview.md](hdd_overview.md) | The top-level overview; where the DivIDE/DivMMC sit in the storage story |
| [ide_interface.md](ide_interface.md) | The IDE protocol and the DivIDE's port map in full detail |
| [sd_interface.md](sd_interface.md) | The SD-card interfaces, including the DivMMC's SPI driver |
| [hdd_partitioning.md](hdd_partitioning.md) | The MBR and FAT structure that the storage card uses |
| [hdf_mgt_formats.md](hdf_mgt_formats.md) | The `.HDF` emulator image format that captures a DivIDE volume |

### 8.2 Related articles elsewhere

| Article | Relationship |
|---|---|
| [esxdos.md](../../04_operating_systems/esxdos.md) | The OS companion to this hardware article — the DOS API, dot commands, assembly interface |
| [nextzxos.md](../../04_operating_systems/nextzxos.md) | The ZX Spectrum Next's ESXDOS derivative; the built-in SD slots |
| [trdos.md](../../04_operating_systems/trdos.md) | The TR-DOS whose hook codes the divman layer emulates |
| [trd_scl_formats.md](trd_scl_formats.md) | The `.TRD` image format that the virtual-floppy layer mounts |
| [beta_disk_interface.md](beta_disk_interface.md) | The Beta 128 hardware that divman emulates |
| [tap_format.md](tap_format.md) / [tzx_format.md](tzx_format.md) | The tape image formats the DivIDE's tape emulator mounts |

### 8.3 License

This article is licensed under [CC BY-SA 4.0](../../README.md). Cross-referenced articles retain their own licenses as stated in each file.
