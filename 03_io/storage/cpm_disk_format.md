# CP/M 2.2 Disk Format on the Spectrum

**Scope:** The **CP/M 2.2** disk format as used on the ZX Spectrum family and its clones — including the Spectrum +3 (with its bundled CP/M mode), the ATM Turbo (a Soviet clone with native CP/M support), and the Sprinter (a more modern Russian Spectrum-compatible PC). This article covers the **on-disk** format: the File Control Block (FCB), the disk directory, the Disk Parameter Block (DPB), and the differences between each machine's CP/M variant.

**Audience:** Emulator authors who need to read or write CP/M disks for any of the Spectrum-compatible machines, archival tool authors, and software preservationists. The article assumes you already understand the simpler +3DOS format (see [plus3_dos_format.md](plus3_dos_format.md)) — CP/M is the "parent" format that +3DOS is derived from, so many concepts are shared.

**Prerequisites:** A working understanding of CP/M 2.2 concepts (BDOS, BIOS, FCB, allocation blocks, extents) helps but is not strictly required — this article introduces the CP/M 2.2 architecture from scratch. Familiarity with the MFM signal layer (see [mfm_encoding.md](mfm_encoding.md)) and the disk-image formats (see [dsk_fdi_formats.md](dsk_fdi_formats.md)) is also useful.

**Depth:** Deep. Byte-level layout of the CP/M 2.2 FCB, the DPB, and the directory; coverage of the three main Spectrum-compatible CP/M variants (+3 CP/M, ATM Turbo CP/M, Sprinter CP/M); worked examples for each.

---

## §1. What CP/M Is

### 1.1 Why CP/M matters

**CP/M** (Control Program for Microcomputers) was, from 1974 until about 1985, the dominant operating system for 8-bit microcomputers. Written by **Gary Kildall** at Digital Research Inc. (DRI), CP/M ran on the Intel 8080, the Zilog Z80, and compatible CPUs (the 8085, the NSC800, the Z180, etc.).

CP/M was the OS of choice for business microcomputers throughout the late 1970s and early 1980s. Thousands of application programs — word processors (WordStar), spreadsheets (SuperCalc), databases (dBase II), assemblers, compilers (Microsoft BASIC, Microsoft FORTRAN, Microsoft COBOL) — were written for CP/M, and CP/M-compatible disk formats were standardised across hundreds of machines.

When the IBM PC launched in 1981, it ran PC-DOS (a CP/M-like clone by Microsoft) rather than CP/M itself, primarily because DRI's pricing negotiations with IBM fell through. The PC's eventual domination of the market killed CP/M as a commercial platform by 1985, but CP/M remained in use on embedded systems, niche computers, and retrocomputing platforms for decades afterwards.

For the Spectrum family, CP/M matters because:

- **It was the standard "business" OS** for 8-bit machines — anyone who wanted to run business software on a Spectrum needed CP/M.
- **The Spectrum +3 was bundled with CP/M 2.2** as a boot option. The +3's +3DOS file format (see [plus3_dos_format.md](plus3_dos_format.md)) is a CP/M derivative, so understanding CP/M is essential for understanding +3DOS.
- **Soviet Spectrum clones** (the ATM Turbo, the Sprinter, and others) had native CP/M support, often with customised file-system layouts.
- **The +3's CP/M disks are interchangeable** with CP/M disks from Amstrad CPC, Amstrad PCW, and many other 8-bit business machines.

### 1.2 CP/M 2.2 vs other CP/M versions

The version of CP/M used on the Spectrum family is almost always **CP/M 2.2** (released by DRI in 1979). This is the "classic" CP/M — the most widely deployed version, and the version to which the +3DOS file format directly corresponds.

Other CP/M versions exist but are not covered in detail here:

- **CP/M 1.4** (1977) — the predecessor of 2.2; uses a slightly different directory entry format.
- **CP/M 3.0** (1983, also called "CP/M Plus") — adds date stamps, larger file support, password protection; used on the Amstrad CPC and PCW. Not used on the Spectrum +3.
- **MP/M** (1981) — multi-user CP/M; rare on Spectrum-compatible hardware.

Throughout this article, "CP/M" refers to CP/M 2.2 unless otherwise stated.

### 1.3 CP/M on the Spectrum family

The following Spectrum-compatible machines shipped with CP/M support:

| Machine | Year | CP/M version | Disk format |
|---|---|---|---|
| **Spectrum +3** | 1987 | CP/M 2.2 (bundled) | +3DOS-compatible (see §5) |
| **Spectrum +2A** | 1987 | CP/M 2.2 (bundled, as +3) | Same as +3 |
| **ATM Turbo 1/2** | 1991–1993 | CP/M 2.2 variant | Custom DPB (see §6) |
| **Sprinter (SpecNext predecessor)** | 1999 | CP/M 2.2 variant | Custom DPB (see §6) |
| **Pentagon 1024SL** | 1990s | Some custom CP/M support | Rare |

The Spectrum +3 is by far the most important of these — it was a major commercial product (in the UK and Europe), and the vast majority of Spectrum CP/M disks in circulation today were written on a +3.

### 1.4 Scope

This article covers the **on-disk format** of CP/M 2.2 disks as used on the Spectrum family. The related **+3DOS** format (a customised CP/M derivative) is covered in [plus3_dos_format.md](plus3_dos_format.md); the **TR-DOS** format (a non-CP/M alternative used by Soviet machines) is covered in [trd_disk_format.md](trd_disk_format.md); the **disk-image** file formats (`.DSK`, `.EDSK`, `.FDI`) used to store CP/M images on modern systems are covered in [dsk_fdi_formats.md](dsk_fdi_formats.md).

## §2. CP/M 2.2 Architecture

### 2.1 The four components of CP/M

A running CP/M 2.2 system is divided into four memory regions, each with a specific role:

| Region | Address range | Role |
|---|---|---|
| **BIOS** (Basic I/O System) | Top of RAM | Hardware-specific I/O routines (read sector, write sector, console in, console out, etc.). The BIOS is the only CP/M component that varies between machines — every machine needs its own BIOS. |
| **BDOS** (Basic Disk Operating System) | Just below BIOS | Hardware-independent file-system and command-dispatch routines. Provides the standard CP/M `CALL 0x0005` system-call interface. The BDOS is identical across all CP/M 2.2 machines. |
| **CCP** (Console Command Processor) | Just below BDOS | The command-line shell. Reads user commands (like `DIR`, `ERA`, `TYPE`, or external `.COM` file names) and executes them. The CCP is the same across all CP/M 2.2 machines. |
| **TPA** (Transient Program Area) | `0x0100` up to CCP | The area where user programs (`COM` files) are loaded and executed. The program is loaded at `0x0100` and execution starts at `0x0100`. |

The very bottom of memory (`0x0000`–`0x00FF`) is the **system parameter area**, containing the jump vectors to the BIOS, BDOS, and CCP, plus various system state bytes (current disk, current user, DMA address, etc.).

This layered design is what makes CP/M portable: the BDOS, CCP, and TPA conventions are the same on every CP/M machine; only the BIOS needs to be rewritten for new hardware.

### 2.2 The CP/M system-call interface

User programs (and the CCP itself) interact with the BDOS via the **system-call interface** at `CALL 0x0005`. The calling convention is:

- **Register C:** function number (1–40 for CP/M 2.2).
- **Register DE:** argument (often a pointer to an FCB, or a byte value for character I/O).
- **Returns:** result in register A (and sometimes in register pair BA or HL).

The most important BDOS functions are:

| Function | Name | Description |
|---|---|---|
| 1 | `CONIN` | Read a character from the console |
| 2 | `CONOUT` | Write a character to the console |
| 9 | `PRINTSTR` | Write a `$`-terminated string |
| 10 (`0x0A`) | `READBUF` | Read a console line into a buffer |
| 12 (`0x0C`) | `VERSION` | Return CP/M version number |
| 13 (`0x0D`) | `RESET` | Reset disk system |
| 14 (`0x0E`) | `SELDSK` | Select disk drive |
| 15 (`0x0F`) | `OPEN` | Open a file (FCB → directory) |
| 16 (`0x10`) | `CLOSE` | Close a file |
| 17 (`0x11`) | `SEARCHF` | Search for first directory match |
| 18 (`0x12`) | `SEARCHN` | Search for next match |
| 19 (`0x13`) | `DELETE` | Delete a file |
| 20 (`0x14`) | `READSEQ` | Read sequentially (FCB advances) |
| 21 (`0x15`) | `WRITESEQ` | Write sequentially |
| 22 (`0x16`) | `MAKE` | Create a file |
| 23 (`0x17`) | `RENAME` | Rename a file |
| 25 (`0x19`) | `CURDSK` | Get current disk |
| 26 (`0x1A`) | `SETDMA` | Set DMA address (default `0x0080`) |
| 31 (`0x1F`) | `DISKMAP` | Get disk-map pointer |
| 33 (`0x21`) | `READRAND` | Read random record (FCB) |
| 34 (`0x22`) | `WRITERAND` | Write random record |
| 40 (`0x28`) | `WRITEZF` | Write zero-filled random record |

Every file operation works through an **FCB** (File Control Block), described in §4. The FCB format is what unifies the CP/M file-system interface across machines.

### 2.3 DMA and the 128-byte record

CP/M 2.2 reads and writes data in units of **128-byte records** (the standard CP/M sector size). When a program calls `READSEQ` (function 20), the BDOS reads the next 128-byte record from the file into the **DMA address** — a memory location set by the program (default `0x0080`, right after the system parameter area).

The 128-byte record is a CP/M-level abstraction: it does **not** correspond to the disk's physical sector size. The BIOS is responsible for translating 128-byte record requests into 512-byte physical sector reads, using whatever buffering scheme the machine uses.

For example, on the Spectrum +3 (which has 512-byte physical sectors), the BIOS reads a full 512-byte sector into a buffer and then hands the BDOS the appropriate 128-byte quarter on each call. This is invisible to the BDOS and to user programs.

### 2.4 The user-area concept

CP/M 2.2 supports a primitive form of "directory" via the **user area** — a number from 0 to 15. Every disk file has a user-area number (stored implicitly in its directory entry), and the BDOS only shows files in the current user area. The user area is set with the `USER n` CCP command.

In practice, most Spectrum CP/M disks use only user area 0, but the user-area concept is preserved in the on-disk format and in the BDOS interface.

### 2.5 Memory map on the Spectrum +3 in CP/M mode

When the Spectrum +3 boots into CP/M mode, the memory is laid out as follows (approximate addresses — the exact layout depends on the +3's memory banking):

| Address | Contents |
|---|---|
| `0x0000` | BIOS / BDOS jump vectors |
| `0x005C` | Default FCB 1 (32 bytes) |
| `0x007C` | Default FCB 2 (16 bytes) |
| `0x0080` | Default DMA buffer (128 bytes); also holds the command tail from CCP |
| `0x0100` | Start of TPA (loaded `COM` file) |
| `0xC000` or so | CCP and BDOS (banked in when needed) |
| `0xFE00` or so | BIOS |

The TPA size on the +3 is around 56 KB, which is more than most other CP/M-capable 8-bit machines (typical TPA is 48–58 KB).
## §3. The Disk Parameter Block (DPB)

### 3.1 What the DPB describes

Every CP/M disk format is described by a **Disk Parameter Block (DPB)** — a 15- or 16-byte data structure that tells the BDOS how the disk is laid out. The DPB is part of the BIOS, not the disk itself: when the BDOS selects a disk drive, it asks the BIOS for the DPB, and then uses the DPB to translate logical file-system operations into physical sector reads and writes.

The DPB is what makes CP/M portable across disk formats: the BDOS code is the same on every machine, and only the DPB (and the underlying sector-read/write routines in the BIOS) change to accommodate different disk geometries.

For an emulator author, knowing the DPB for a particular disk is essential — without it, you cannot interpret the disk's directory or allocation pointers.

### 3.2 The DPB fields

The standard CP/M 2.2 DPB has the following fields (offsets given in bytes, with all multi-byte fields little-endian):

| Offset | Field | Length | Notes |
|---|---|---|---|
| 0 | **SPT** (sectors per track) | 2 | Counted in 128-byte records. For a disk with 9 physical sectors of 512 bytes per track, SPT = 9 × 4 = 36. |
| 2 | **BSH** (block shift) | 1 | The shift used to convert a byte offset to a block number: `block = byte_offset >> (BSH + 7)`. BSH = 3 → 1 KB blocks; BSH = 4 → 2 KB blocks; BSH = 5 → 4 KB blocks. |
| 3 | **BLM** (block mask) | 1 | `BLM = (1 << BSH) - 1`. Used for masking the low bits of a byte offset within a block. |
| 4 | **EXM** (extent mask) | 1 | The number of 16 KB extents per directory entry, minus 1. EXM = 0 → 16 KB per entry; EXM = 1 → 32 KB per entry (only when DSM < 256). |
| 5 | **DSM** (max data-block number) | 2 | The highest block number on the disk. Total blocks = DSM + 1. |
| 7 | **DRM** (max directory entry number) | 2 | The highest directory-entry number. Total entries = DRM + 1. |
| 9 | **AL0** (allocation bitmap byte 0) | 1 | The first byte of a 16-bit bitmap indicating which of the first 16 blocks are reserved for the directory. |
| 10 | **AL1** (allocation bitmap byte 1) | 1 | The second byte of the bitmap. |
| 11 | **CKS** (directory check vector size) | 2 | The size in bytes of the directory check vector, used to detect changed disks. Typically `(DRM + 1) / 4`. |
| 13 | **OFF** (reserved tracks offset) | 2 | The number of reserved tracks at the start of the disk (for boot sectors). The BDOS skips this many tracks before the directory begins. |
| 15 | (padding) | 0–2 | Optional padding for alignment; not used by CP/M 2.2. |

### 3.3 Common DPB values

The following table lists some commonly-encountered CP/M DPB values. The +3 DPB is also shown (it is essentially the same as a 720 KB CP/M DPB with the +3's "reverse side" hardware trick applied).

| Disk type | SPT | BSH | BLM | EXM | DSM | DRM | AL0/AL1 | CKS | OFF |
|---|---|---|---|---|---|---|---|---|---|
| **8" SD (243 KB)** | 26 | 3 | 7 | 0 | 242 | 63 | `0xC0/00` | 16 | 2 |
| **8" DD (1 MB)** | 52 | 4 | 15 | 1 | 254 | 255 | `0xFF/00` | 64 | 2 |
| **5.25" SD (160 KB)** | 18 | 3 | 7 | 0 | 158 | 63 | `0xC0/00` | 16 | 0 |
| **5.25" DD (360 KB)** | 36 | 3 | 7 | 0 | 354 | 63 | `0xC0/00` | 16 | 0 |
| **3" DSDD (180 KB) — Amstrad CPC** | 36 | 3 | 7 | 0 | 178 | 63 | `0xC0/00` | 16 | 0 |
| **3" DSDD (720 KB) — Amstrad PCW / Spectrum +3** | 36 | 3 | 7 | 0 | 714 | 63 | `0xC0/00` | 16 | 0 |
| **3.5" HD (1.44 MB)** | 72 | 4 | 15 | 1 | 1422 | 255 | `0xF0/00` | 64 | 0 |

These values are typical but not universal — different BIOSes used slightly different values (especially for DSM, which varies with how the BIOS reserves boot and directory space).

### 3.4 Worked example: the standard +3 CP/M DPB

For the standard +3 720 KB DSDD disk, the DPB in the +3's CP/M BIOS is (all values little-endian):

```
24 00       SPT  = 36 (= 9 sectors × 4 records)
03          BSH  = 3
07          BLM  = 7
00          EXM  = 0
CA 02       DSM  = 0x02CA = 714
3F 00       DRM  = 0x003F = 63
C0 00       AL0  = 0xC0, AL1 = 0x00
10 00       CKS  = 16
00 00       OFF  = 0
```

What this means:
- 1 KB allocation blocks (BSH = 3, BLM = 7).
- 715 blocks total (DSM + 1 = 715).
- 2 blocks reserved for the directory (AL0 = `0xC0`), giving 64 directory entries.
- 64 entries × 32 bytes = 2048 bytes = 2 blocks. ✓
- No reserved system tracks (OFF = 0) — the directory starts at logical track 0.
- 36 128-byte records per track = 9 × 512-byte sectors per track. ✓
- CKS = 16 → the directory check vector is 16 bytes.

This DPB is identical to the +3DOS DPB (see [plus3_dos_format.md §3.2](plus3_dos_format.md)) — which is expected, since +3DOS uses the CP/M 2.2 directory format with the +3's geometry.

### 3.5 Variations across machines

The DPB differs across Spectrum-compatible machines because the underlying disk geometry differs:

- **Spectrum +3:** 720 KB DSDD, standard DPB as above.
- **ATM Turbo:** 800 KB DSDD (10 sectors per track instead of 9), so SPT = 40, DSM ≈ 794. The ATM Turbo BIOS uses a slightly modified DPB to accommodate the extra sector per track.
- **Sprinter:** Variable geometry — the Sprinter can read 1.44 MB HD disks, so its DPB can have SPT = 72 and DSM ≈ 1422. Multiple DPBs are supported simultaneously.
- **Pentagon 1024SL:** 720 KB DSDD (same as +3) or 800 KB DD with non-standard sectoring.

An emulator should consult the relevant machine's BIOS disassembly to determine the exact DPB it uses. For most archival work, however, the standard +3 / PCW DPB is sufficient.
## §4. The File Control Block (FCB)

### 4.1 What the FCB is

In CP/M 2.2, every file operation (open, close, read, write, search, delete) is performed by passing a **File Control Block (FCB)** to the BDOS. The FCB is a 33-byte (sequential) or 35-byte (random) in-memory structure that identifies the file, tracks the current read/write position, and records the file's allocation.

When a user program calls `BDOS_OPEN` (function 15), it fills in the filename fields of the FCB and passes the FCB's address to the BDOS. The BDOS searches the disk directory for the file, copies the directory entry's allocation info into the FCB, and returns. Subsequent `BDOS_READSEQ` (function 20) and `BDOS_WRITESEQ` (function 21) calls use the FCB to track the current position in the file.

The FCB is **both a program-level structure** (used by user programs) **and a disk-level structure** — the first 32 bytes of the FCB are the same as the 32-byte directory entry, so reading the disk's directory is equivalent to reading a sequence of FCB-like records.

### 4.2 The 33-byte sequential FCB layout

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 1 | **Drive** | `0` = default drive, `1` = drive A, `2` = drive B, ..., `16` = drive P. (The drive byte is set by the user program; the BDOS rewrites it with the actual drive number when the file is opened.) |
| 1 | 11 | **Filename + file-type** | 11 bytes: 8 chars of name, 3 chars of type, space-padded, uppercase. Same encoding as the directory entry (see [plus3_dos_format.md §4.3](plus3_dos_format.md)). |
| 12 | 1 | **EX** (extent number low) | Current extent number. |
| 13 | 1 | **S1** (reserved) | Reserved by BDOS; usually 0. |
| 14 | 1 | **S2** (extent number high) | High bits of extent number. |
| 15 | 1 | **RC** (record count) | Number of 128-byte records used in this extent. |
| 16 | 16 | **Allocation pointers** | 16 × 1-byte block pointers (each pointing to a 1 KB block). |
| 32 | 1 | **CR** (current record) | The current record number within the extent (0–127). Used by `READSEQ` / `WRITESEQ`. |

The first 32 bytes (offset 0–31) match the on-disk directory entry format exactly. The 33rd byte (CR, the "current record") is the BDOS's bookmark for sequential I/O.

### 4.3 The 35-byte random FCB layout

For random-access I/O (`BDOS_READRAND` function 33, `BDOS_WRITERAND` function 34), the FCB is extended with two more bytes:

| Offset | Length | Field | Notes |
|---|---|---|---|
| 33 | 2 | **R0, R1** (random record low) | The low 16 bits of the random record number. The random record number identifies a specific 128-byte record within the file. |
| 35 | 1 | **R2** (random record high) | The high 8 bits of the random record number. |

The random record number is a 24-bit value, allowing files of up to 2^24 × 128 = 2 GB. In practice, CP/M files are limited by the disk size (typical max ~700 KB on a +3 disk).

### 4.4 Filename specification

The filename field in the FCB can contain **wildcard characters** (`?` = match any single character; `*` = match all characters from this point to the end of the field). Wildcards are expanded by the BDOS when searching the directory.

For example, to search for all `*.COM` files in user area 0:

```z80
; Z80 code to list all .COM files
        LD    DE, FCB
        LD    C, 17        ; BDOS function 17 = SEARCHF
        CALL  5
        ; ... process matches ...
FCB:    DB    0            ; drive 0 = default
        DB    "???????????" ; 11 question marks = any name
        DB    "COM"        ; extension COM
        ; ... remaining FCB fields are zero ...
```

This searches the directory for all entries matching the pattern and returns the address of the first match in the DMA buffer. The BDOS then iterates with function 18 (`SEARCHN`) to find subsequent matches.

### 4.5 FCB usage in the +3's BASIC

When the +3's BASIC (in +3DOS mode) executes a `LOAD "name" CODE` or similar command that reads a disk file, it constructs an FCB at a fixed location in memory and calls the BDOS to open and read the file. The FCB construction and BDOS calling are hidden from the BASIC user, but they are visible to anyone disassembling the +3's ROM.

For more details on the +3DOS-specific use of the FCB, see [plus3_dos_format.md §4](plus3_dos_format.md).
## §5. CP/M on the Spectrum +3

### 5.1 The bundled CP/M

The Spectrum +3 shipped with **CP/M 2.2** as a built-in boot option. The CP/M kernel, BDOS, CCP, and BIOS are stored in the +3's built-in ROM, alongside the +3DOS ROM and the BASIC ROM. To boot CP/M, the user selects the CP/M boot option from the +3's boot menu (or types a specific key combination at power-on).

Once booted, the +3's CP/M behaves like any other CP/M 2.2 implementation. It presents the standard `A>` prompt and accepts standard CCP commands (`DIR`, `ERA`, `TYPE`, `REN`, etc.) plus the standard `COM`-file execution convention.

### 5.2 The +3's CP/M hardware

The +3's CP/M uses the following hardware:

- **Z80 CPU** at 3.54689 MHz (the +3's standard clock). This is the same speed used by the +3's BASIC mode.
- **Floppy controller:** the WD1772-PH (see [plus3_floppy.md §4](plus3_floppy.md)). The +3's CP/M BIOS translates 128-byte record requests into WD1772-PH sector reads.
- **Memory banking:** the +3 has 128 KB of RAM organised into 4 banks of 32 KB. The CP/M BIOS uses banking to fit the BIOS, BDOS, and CCP into the upper half of the address space while leaving the lower half for the TPA.
- **Console I/O:** keyboard input is via the standard Spectrum keyboard matrix; output is to the +3's display (in 32-column or 80-column mode, depending on the +3's video mode).
- **Disk drives:** A: and B: are the +3's two internal 3.5" floppy drives (or the +3's single drive, on the +2A which has only one).

### 5.3 Booting CP/M

To boot CP/M on the +3:

1. Insert a CP/M boot disk into drive A:. (The +3's CP/M requires a boot disk — it does not boot directly from ROM.)
2. Power on the +3 (or press the reset button).
3. From the boot menu, select "CP/M".

The boot disk's **boot sector** (cylinder 0, side 0, sector 1) contains a small bootstrap loader. The +3's ROM reads this sector, executes it, and the bootstrap loader in turn reads the rest of the CP/M kernel into the TPA and jumps to the CCP.

A standard +3 CP/M boot disk contains:

- Boot sector (cylinder 0, side 0, sector 1).
- CCP, BDOS, and BIOS images, stored as separate files (`CCP.COM`, `BDOS.COM`, `BIOS.COM`) or as a single `CPM.SYS` file.
- Standard CP/M utility programs: `STAT.COM`, `PIP.COM`, `ED.COM`, `SUBMIT.COM`, `XSUB.COM`, `DDT.COM`, etc.

### 5.4 Disk compatibility

The +3's CP/M uses the **same on-disk format** as +3DOS:

- Same geometry: 80-track DSDD, 9 sectors per track, 512 bytes per sector, 720 KB.
- Same directory entry format (32 bytes, CP/M 2.2 standard).
- Same DPB (see §3.4).
- Same "reverse side" trick (side 1 cylinder numbering is reversed).

This means a +3DOS disk and a +3 CP/M disk are **format-compatible** — the same disk can be read in either mode. The only difference is which CCP / BDOS / BIOS is loaded at boot time.

### 5.5 CP/M software available for the +3

A wide range of CP/M software was made available for the +3, including:

- **Microsoft MBASIC** (CP/M BASIC interpreter).
- **HiSoft BASIC** (a Z80-native BASIC compiler for CP/M).
- **HiSoft DevPac** (Z80 / 8080 assembler and disassembler).
- **Borland Turbo Pascal 3** (a fast Pascal compiler for CP/M).
- **WordStar** (the dominant CP/M word processor).
- **SuperCalc** (the dominant CP/M spreadsheet).
- **dBase II** (the dominant CP/M database).
- **Perfect Writer, Perfect Calc, Perfect Filer** (the "Perfect" suite).
- Various Z80 assemblers (ZSM, M80, MAC, RMAC).

Most of this software was originally written for other CP/M machines (Osborne, Kaypro, Epson QX-10, etc.) and was made available on +3 CP/M disks by third-party distributors.

### 5.6 Limitations of +3 CP/M

The +3's CP/M has a few limitations compared to a "real" CP/M machine:

- **No hard-disk support.** The +3's CP/M only supports floppy disks.
- **No native networking.** The +3 did not include a CP/M network stack (unlike, say, CP/NET).
- **No native printer support** beyond the +3's built-in Centronics port.
- **No graphics support.** CP/M on the +3 runs in text mode only; there are no CP/M-aware graphics libraries.
- **Small TPA.** The TPA on the +3 is around 56 KB, smaller than some other CP/M machines (the Kaypro II had 62 KB TPA, for example). This limits the size of programs that can run.

These limitations were not unique to the +3 — most consumer CP/M machines had similar restrictions. The +3's CP/M was aimed at home users who wanted to run business software at home, not at competing with full business microcomputers.
## §6. CP/M on Other Spectrum Clones

### 6.1 ATM Turbo

The **ATM Turbo** (also known as the ATM Turbo 1, ATM Turbo 2, or simply "ATM") is a Russian Spectrum-compatible computer produced from 1991 onwards by NEMO (a Russian computer company). The ATM Turbo is one of the more powerful Soviet Spectrum clones, with:

- Z80 CPU at 7 MHz (turbo mode) or 3.5 MHz (compatibility mode).
- 512 KB or 1024 KB of RAM with sophisticated banking.
- Two floppy-disk interfaces: TR-DOS (Beta 128-compatible) and CP/M.
- Custom video hardware with multiple text and graphics modes.
- Optional IBM PC keyboard.

The ATM Turbo's CP/M support is provided by a custom CP/M 2.2 BIOS that uses the ATM's second floppy interface (a WD1772 variant similar to the +3's). The CP/M BIOS provides:

- Standard CP/M 2.2 BDOS interface.
- Custom BIOS routines for the ATM's hardware (video, keyboard, floppy).
- Support for two disk drives (A: and B:).

The ATM Turbo's CP/M disk format uses **80-track double-density 5.25" or 3.5" floppies with 10 sectors per track of 512 bytes each** (giving 800 KB total), rather than the +3's 9 sectors per track. This results in a DPB with:

- SPT = 40 (= 10 × 4)
- DSM = 794 (= 800 KB − 1 KB directory reservation)
- All other fields identical to the +3's DPB.

ATM Turbo CP/M disks are **format-incompatible** with +3 CP/M disks: the +3 cannot read an ATM disk directly (different sector count per track). However, an emulator that supports both machines can convert between the two formats using a sector-by-sector read-and-rewrite tool.

### 6.2 Sprinter

The **Sprinter** (sometimes called the "ZXP-2" or "Sprinter 2000") is a Russian Spectrum-compatible computer produced from 1999 onwards by Peters Plus Ltd. The Sprinter is one of the most advanced Spectrum-compatible machines ever produced:

- Z80 CPU at 7 MHz (turbo) or 3.5 MHz (compatibility).
- Up to 4 MB of RAM with advanced banking.
- ISA bus for IBM PC-compatible expansion cards.
- 1.44 MB floppy disk support (the Sprinter uses PC-compatible HD disks).
- VGA-compatible video output (with custom Spectrum-compatible modes).

The Sprinter's CP/M support is provided by a custom CP/M 2.2 BIOS that uses the Sprinter's standard PC-compatible floppy interface. The CP/M BIOS supports:

- 720 KB DSDD disks (3.5" 80-track 2-sided 9-sector) — same as the +3.
- 1.44 MB HD disks (3.5" 80-track 2-sided 18-sector) — Sprinter-specific.
- Two floppy drives, plus optional hard-disk emulation via the ISA bus.

The Sprinter's CP/M DPB for the 1.44 MB HD format is:

- SPT = 72 (= 18 × 4)
- BSH = 4 (2 KB blocks)
- BLM = 15
- EXM = 1
- DSM = 1422 (= 1440 KB − 4 KB directory reservation)
- DRM = 511 (512 directory entries × 32 bytes = 16 KB = 8 blocks)
- AL0/AL1 = `0xF0/0x00` (first 4 blocks reserved)
- CKS = 128
- OFF = 0

The Sprinter is one of the few Spectrum-compatible machines that can read **standard IBM PC 1.44 MB floppies** with CP/M format — making it useful for transferring CP/M data between modern PCs and the Spectrum world.

### 6.3 Pentagon 1024SL and others

The **Pentagon 1024SL** (a Soviet Spectrum clone from the late 1990s) supports a custom CP/M variant, but it is rarely used — most Pentagon users stick with TR-DOS. The Pentagon's CP/M uses the same TR-DOS floppy hardware (a Beta 128-compatible interface with the VG93 / WD1793 controller) but with a custom CP/M BIOS, resulting in yet another DPB.

Other Spectrum-compatible machines with CP/M support include:

- **Kay 102** (Russian clone, 1990s) — CP/M 2.2 support, custom DPB.
- **Scorpion ZS-256** (Russian clone, 1990s) — CP/M 2.2 support via an expansion board, custom DPB.
- **Profi 5.03** (Russian clone, 1990s) — CP/M 2.2 support, custom DPB.

For each of these machines, the on-disk CP/M format follows the standard CP/M 2.2 conventions described in this article, but the DPB and the underlying sector translation differ. Emulator authors should consult the relevant machine's BIOS disassembly for the exact DPB.

### 6.4 Cross-machine disk compatibility

| Source machine → Reader | +3 | ATM Turbo | Sprinter (1.44 MB) |
|---|---|---|---|
| **+3 disk** | — | Read OK with `*FORMAT` conversion | Read OK (DSDD mode) |
| **ATM Turbo disk** | Read OK with conversion | — | Read OK |
| **Sprinter 1.44 MB disk** | Not supported | Not supported | — |
| **PC (DOS) disk** | Not supported | Not supported | Read OK at sector level |

In practice, the +3's 720 KB format is the most widely supported Spectrum-CP/M format, and most modern Spectrum CP/M disk images in the World of Spectrum archive are in +3 format.
## §7. Tools and Editors

### 7.1 cpmtools

The standard tool for working with CP/M disks on a modern Unix-like system is **`cpmtools`** (open-source, available on Linux, macOS, and Windows via Cygwin). It provides:

- **`cpmls`** — list files on a CP/M disk.
- **`cpmcp`** — copy files to / from a CP/M disk.
- **`cpmrm`** — remove files from a CP/M disk.
- **`cpmformat`** — format a CP/M disk.
- **`cpmchattr`** — change file attributes (RO, SYS, ARCH).
- **`fsck.cpm`** — check the file system for errors.

`cpmtools` works with `.DSK` and `.EDSK` images (see [dsk_fdi_formats.md](dsk_fdi_formats.md)) via the appropriate **disk definition**. The standard disk definition for a +3 720 KB disk is:

```
diskdef plus3
  seclen 512
  tracks 160
  sectrk 9
  blocksize 1024
  maxdir 64
  boottrk 0
  skew 0
  offset 0
end
```

For the ATM Turbo 800 KB disk:

```
diskdef atm
  seclen 512
  tracks 160
  sectrk 10
  blocksize 1024
  maxdir 64
  boottrk 0
  skew 0
  offset 0
end
```

### 7.2 Emulators that support CP/M

All the major Spectrum emulators support +3 CP/M disks (since +3DOS and CP/M use the same disk format):

- **Fuse**, **UnrealSpeccy**, **Zero**, **SpecEmu**, **EightyOne** — all support +3 CP/M mode.
- **UnrealSpeccy** and **emu80** also support ATM Turbo CP/M mode.
- **Sprinter emulator** (`sprinteremu`) supports Sprinter CP/M.

### 7.3 Reading a CP/M disk programmatically

A minimal Python reader for the directory of a +3 / CP/M disk is essentially the same as for a +3DOS disk (see [plus3_dos_format.md §8.3](plus3_dos_format.md) for the code). The directory format is identical — the only difference is which DPB you use for block-to-sector translation.

### 7.4 Conversion tools

| Conversion | Tool | Notes |
|---|---|---|
| CP/M disk → files on host | `cpmcp` | Loses CP/M user-area info |
| Files on host → CP/M disk | `cpmcp` (with `-p` for user-area) | |
| CP/M `.DSK` ↔ +3DOS `.DSK` | No conversion needed (same format) | The same `.DSK` file can be read in either mode |
| CP/M `.DSK` ↔ TR-DOS `.TRD` | `zxmak` or custom script | Involves file-system conversion |
| CP/M `.COM` → Spectrum Z80 binary | Manual | The `.COM` file is loaded at `0x0100` and starts at `0x0100`; just prepend 256 bytes of zeros to get a flat binary |

## §8. Cross-references and License

### 8.1 Related articles in this Knowledge base

- [plus3_dos_format.md](plus3_dos_format.md) — the **+3DOS** logical disk format, a customised CP/M 2.2 derivative used by the Spectrum +3 in BASIC mode. This article and that one are companions: this one covers the CP/M "parent", that one covers the +3-specific child.
- [plus3_floppy.md](plus3_floppy.md) — the **physical** layer of the +3's floppy subsystem (the WD1772-PH controller, the port map, the cable pinout).
- [mfm_encoding.md](mfm_encoding.md) — the MFM signal layer underlying all floppy-disk formats.
- [trd_disk_format.md](trd_disk_format.md) — the **TR-DOS** logical disk format (a non-CP/M alternative used by the Beta Disk Interface and Soviet machines).
- [opus_discovery_format.md](opus_discovery_format.md) — the Opus Discovery disk format (another Western alternative).
- [disk_format_overview.md](disk_format_overview.md) — a high-level comparison of all Spectrum disk formats.
- [dsk_fdi_formats.md](dsk_fdi_formats.md) — the disk-image file formats (`.DSK`, `.EDSK`, `.FDI`) used to store CP/M images on modern systems.
- [trd_scl_formats.md](trd_scl_formats.md) — the `.TRD` and `.SCL` disk-image file formats (the TR-DOS equivalents of `.DSK` / `.EDSK`).

### 8.2 External references

- **"CP/M 2.2 Interface Guide"** (Digital Research, 1979) — the canonical CP/M BDOS / BIOS specification.
- **"The CP/M Handbook with MP/M"** by Rodney Zaks (Sybex, 1980) — a comprehensive CP/M programmer's guide.
- **"Programming the Z80"** by Rodnay Zaks (Sybex, 1979) — the canonical Z80 reference, with extensive CP/M examples.
- **The `cpmtools` documentation** — Unix man pages and disk definitions for working with CP/M disks on modern systems.
- **The Unofficial CP/M Web Site** (www.cpm.z80.de) — archives of CP/M software, documentation, and utilities.
- **The Spectrum +3 Manual Set** (Sinclair / Amstrad, 1987) — the original +3 hardware and CP/M reference.

### 8.3 Trademarks

"ZX Spectrum", "+3", "Amstrad", "Sinclair", "CP/M", "WordStar", "SuperCalc", "dBase II", "Microsoft BASIC", "HiSoft", "Borland Turbo Pascal", "ATM Turbo", "Sprinter", and other trademarks are the property of their respective owners and are used here for identification and educational purposes only.

### 8.4 License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you give appropriate credit and distribute derivative works under the same license.
