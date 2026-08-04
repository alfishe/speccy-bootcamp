[← Home](../README.md) · [Operating Systems](README.md)

# CP/M on the Spectrum

CP/M was the most important microcomputer operating system of the late 1970s and early 1980s — the operating system that made Microsoft possible (their first products were CP/M language ports), the operating system that the IBM PC almost used instead of MS-DOS, and the operating system that dominated business computing until the rise of the IBM PC clone market in 1983–1985.

The ZX Spectrum — originally a games machine — was never a primary CP/M platform. But several Spectrum-compatible machines could boot CP/M, and a surprisingly rich library of CP/M software was available to Spectrum owners who wanted to use their machine for "serious" work. This article covers CP/M as an operating system, its architecture, how it was ported to the Spectrum, and the software ecosystem that resulted.

For the +3's CP/M compatibility (the most common Spectrum CP/M path), see [plus3dos.md](plus3dos.md) §7. For FUZIX — the modern Unix-like alternative — see [fuzix.md](fuzix.md).

---

## Roadmap

1. **What CP/M is** — history, scope, why the Spectrum had it
2. **CP/M architecture** — BIOS, BDOS, CCP, the three layers
3. **Memory layout** — TPA, FCB, DMA, where everything lives
4. **The file system** — FCB-based access, user numbers, .COM files
5. **The BDOS API** — the function-call interface, with examples
6. **CP/M on the Spectrum** — +3, ATM Turbo, Sprinter, the various ports
7. **The software library** — WordStar, dBase, Turbo Pascal, and friends
8. **Modern status** — what survives in 2024
9. **Cross-references** — where to go next

---

## §1. What CP/M Is

### 1.1 Origins

CP/M was created in 1974 by **Gary Kildall**, a computer science professor at the Naval Postgraduate School in Monterey, California. Working with an Intel Intellec-8 development system built around the Intel 8080 CPU, Kildall wrote a simple operating system to manage floppy disk storage. He called it **CP/M** — Control Program for Microcomputers.

The first versions of CP/M were tightly tied to the Intel Intellec-8 hardware. In 1977, Kildall and his company **Digital Research** (DRI) restructured CP/M into a layered architecture: a hardware-independent BDOS (the bulk of the OS) sitting on top of a hardware-specific BIOS (the I/O layer). This restructuring meant that CP/M could be ported to any 8080- or Z80-based computer by writing a custom BIOS — typically a few hundred lines of assembly.

The result was explosive growth. Within a few years, CP/M was running on hundreds of different microcomputers from manufacturers as diverse as Osborne, Kaypro, Cromemco, North Star, and Radio Shack. By 1980, CP/M had approximately 90% market share in business microcomputing.

### 1.2 The IBM PC story

In 1980, IBM was developing its Personal Computer and needed an operating system. The natural choice was CP/M-86, a port of CP/M to the new Intel 8086 CPU. But negotiations between IBM and Digital Research broke down, reportedly over IBM's demand for a non-disclosure agreement that Kildall refused to sign. IBM instead turned to a small company called Microsoft, which bought a CP/M clone called QDOS (Quick and Dirty Operating System) from Seattle Computer Products, renamed it MS-DOS, and licensed it to IBM.

The IBM PC shipped in August 1981 with three operating system options: CP/M-86 (at $240, the most expensive), PC-DOS (at $40, the Microsoft option), and the UCSD p-System. The price difference and Microsoft's aggressive marketing tipped the market decisively toward MS-DOS. By 1983, CP/M was in retreat; by 1985, it was a niche product.

CP/M's last significant version was **CP/M 2.2** (1980), which became the canonical 8-bit CP/M release. Later versions (CP/M 3.0, CP/M Plus, MP/M) added features but never matched 2.2's market presence. All Spectrum CP/M implementations are based on 2.2.

### 1.3 Why CP/M matters to the Spectrum

The Spectrum is a Z80 machine, and CP/M 2.2 is fundamentally a Z80 operating system (it runs on both 8080 and Z80, but Z80 is the better fit). Porting CP/M to a Z80-based Spectrum requires only:

- 56 KB or more of RAM.
- A disk drive (real or emulated).
- A keyboard and a text-mode screen.
- A custom BIOS (a few hundred lines of code).

The hardware requirements are minimal. The bigger challenge is **memory layout**: CP/M expects a flat 64 KB address space with the OS at the top, which conflicts with the Spectrum's ROM-at-the-bottom layout. Spectrum CP/M ports solve this by either:

- Running CP/M in a "shadow RAM" configuration (using RAM banked in to overlay the ROM).
- Using a machine that has RAM at `#0000`-`#FFFF` (no ROM, or RAM-disk-booted).

Either way, when CP/M is running, the Spectrum's normal BASIC ROM is invisible. The user is in a different world.

### 1.4 What CP/M gave the Spectrum

A Spectrum running CP/M becomes a **serious business computer**. The CP/M software library — thousands of programs, mostly from 1978–1984 — includes:

- WordStar: the dominant word processor of the CP/M era.
- SuperCalc: the dominant spreadsheet.
- dBase II: the first widely-used relational database.
- Microsoft BASIC-80: the CP/M version of Microsoft's BASIC.
- Turbo Pascal: Borland's revolutionary Pascal IDE.
- Microsoft FORTRAN-80, COBOL-80, M80: other languages.
- Perfect Writer, Perfect Speller, Perfect Calc: an office suite.
- Magic Wand: a popular word processor.
- PIE: an early spreadsheet.
- MuMath, MuLisp: symbolic math and Lisp.
- Hundreds of smaller utilities: text editors, archive tools, terminal programs.

For a Spectrum owner in 1988 who wanted to do "real" work — write a dissertation, balance a budget, learn Pascal — CP/M was the answer. The Spectrum was suddenly a viable second computer for a household that already had a "real" machine.

---

## §2. CP/M Architecture

CP/M is a layered operating system. The architecture is one of the most important design decisions in computing history and is worth understanding in detail.

### 2.1 The three layers

CP/M is divided into three layers, each occupying a different region of memory:

```
FFFF +------------------+
     |        BDOS      |  ~3.5 KB: Basic Disk Operating System
     |                  |  (file I/O, command processing)
F400 +------------------+
     |        CCP       |  ~2 KB: Console Command Processor
     |                  |  (the user's command shell)
EC00 +------------------+
     |     BIOS +       |  ~1 KB: Basic I/O System
     |   buffers        |  (hardware-specific I/O routines)
E600 +------------------+
     |                  |
     |    Free TPA      |  ~58 KB: Transient Program Area
     |                  |  (where application programs run)
     |                  |
0100 +------------------+
     | Program header   |  256 bytes: jump to BDOS, etc.
0000 +------------------+
```

The exact addresses depend on the BIOS size; the values above are typical for a 56 KB CP/M system.

### 2.2 The CCP (Console Command Processor)

The CCP is CP/M's user interface — the equivalent of a Unix shell or the MS-DOS `COMMAND.COM`. When CP/M boots, the CCP runs and displays the `A>` prompt (where `A` is the current drive). The user types commands; the CCP parses them and either:

- **Built-in commands**: executed by the CCP itself. CP/M 2.2 has very few built-ins — just `DIR` (list directory), `ERA` (erase), `REN` (rename), `TYPE` (display file), `SAVE` (save memory to file), and `USER` (switch user number).
- **External commands**: executed by loading a `.COM` file from disk into the TPA and jumping to it. Almost all CP/M commands are external.

The CCP source code is small (about 600 lines of 8080 assembly) and well-documented. Some CP/M ports (the +3's included) include a slightly modified CCP with a few extra built-in commands.

### 2.3 The BDOS (Basic Disk Operating System)

The BDOS is CP/M's file system and I/O layer. It exposes a small set of function calls (about 40 in CP/M 2.2) that programs use to:

- Open, close, read, write, and delete files.
- Read and change directories.
- Get console input and output.
- Print to a printer.
- Send and receive via a serial port.
- Get and set the date (in versions that support it).

The BDOS is hardware-independent: every CP/M system has the same BDOS, with the same function numbers, calling conventions, and behavior. This is what makes CP/M software portable — a program written against the BDOS will run on any CP/M system that provides the BIOS routines the BDOS calls.

### 2.4 The BIOS (Basic I/O System)

The BIOS is the only hardware-specific part of CP/M. It is a small set of routines (about 17 in CP/M 2.2) that the BDOS calls to perform actual hardware operations:

- `BOOT`: cold boot the system.
- `WBOOT`: warm boot (return to CCP).
- `CONST`: console status (is a key waiting?).
- `CONIN`: read a character from the console.
- `CONOUT`: write a character to the console.
- `LIST`: write a character to the printer.
- `PUNCH`: write to the punch device (paper tape, historically).
- `READER`: read from the reader device.
- `HOME`: seek to track 0.
- `SELDSK`: select a disk drive.
- `SETTRK`: set the current track.
- `SETSEC`: set the current sector.
- `SETDMA`: set the DMA address.
- `READ`: read a sector.
- `WRITE`: write a sector.
- `PRSTAT`: printer status.
- `SECTRN`: sector translation (for skewing).

To port CP/M to a new machine, the implementer writes implementations of these 17 routines for the target hardware. The rest of CP/M (CCP and BDOS) is unchanged. This separation of concerns — hardware-specific BIOS over hardware-independent BDOS/CCP — was Kildall's most influential design contribution. The same architecture appears in MS-DOS (with `IO.SYS` and `MSDOS.SYS`), in Linux (with kernel modules over a hardware-specific bootloader), and in many other systems.

### 2.5 The system parameter block

The BIOS includes a small data structure at its base — the **system parameter block** — that tells the rest of CP/M how this particular machine is configured. It contains:

- The base address of the BIOS (so the BDOS can find the routines).
- The base address of the BDOS (so user programs can find the function entry point).
- The I/O byte (which devices are configured).
- The drive byte (how many drives are available).
- The user number (the default user area).

When CP/M is loaded into memory, this parameter block is read first; the BDOS uses it to discover the BIOS's entry point and call into it.
---

## §3. Memory Layout

CP/M's memory model is fundamentally different from the Spectrum's. Where the Spectrum has ROM at the bottom of the address space and RAM above, CP/M expects **RAM everywhere**.

### 3.1 The flat 64 KB model

CP/M assumes the entire 64 KB Z80 address space is RAM, with the OS at the top and the user's program at the bottom. There is no ROM visible during CP/M operation.

| Address range | Content |
|---|---|
| `#0000`–`#00FF` | System parameter block, jump vectors |
| `#0100`–`xxxx` | TPA (Transient Program Area) — where application programs load |
| `xxxx`–`#EBFF` | BDOS (top of TPA varies based on BIOS size) |
| `#EC00`–`#F3FF` | CCP (Console Command Processor) |
| `#F400`–`#FFFF` | BIOS and buffers |

The address `xxxx` (top of TPA) varies between CP/M ports. On a 56 KB system it's `#DFFF`; on a 62 KB system it's `#F7FF`. The bigger the TPA, the more RAM available to applications.

### 3.2 The `#0005` jump vector

CP/M exposes its BDOS function-call interface via a single address: `#0005`. A program calls a BDOS function by:

1. Loading the function number into the C register.
2. Loading the function argument (if any) into the DE register pair.
3. Calling `#0005`.

The byte sequence at `#0005` is a `JMP <BDOS>` instruction that the BIOS initialises at boot time. This indirection allows different CP/M ports to place the BDOS at different addresses without breaking application compatibility.

A typical BDOS call (function 2: write a character to console):

```z80
LD   E,'A'                ; character to print
LD   C,2                  ; function 2: CONOUT
CALL #0005                ; dispatch
```

### 3.3 The FCB and DMA

Two regions of memory are essential for CP/M file I/O:

**The default FCB (File Control Block)** lives at `#005C`–`#007F` (36 bytes). When the CCP loads an external command, it parses the command's first two arguments into the default FCB. A program that wants to operate on a file passed on the command line uses this FCB directly.

**The default DMA (Direct Memory Access) buffer** lives at `#0080`–`#00FF` (128 bytes). All disk I/O goes through this buffer by default: a `READ` BDOS call reads a 128-byte sector into the DMA buffer; a `WRITE` call writes from it.

Programs that need more sophisticated file handling allocate their own FCBs (typically 36 bytes each) in their TPA. Multiple FCBs allow multiple simultaneously-open files.

### 3.4 The 128-byte record

CP/M file I/O is **record-based**: every read or write transfers exactly 128 bytes. A program that wants to read a 1024-byte file makes 8 sequential `READ` calls. A program that wants to read a 100-byte file reads one full 128-byte record and uses only the first 100 bytes.

This is a constraint of CP/M 2.2. CP/M 3.0 and MS-DOS later relaxed it to support arbitrary block sizes, but the 128-byte record is a fixed feature of CP/M 2.2 file I/O.

---

## §4. The File System

CP/M's file system is the direct ancestor of MS-DOS's file system and, indirectly, of every FAT-based filesystem in use today. Understanding CP/M files means understanding where MS-DOS came from.

### 4.1 Filename format

CP/M filenames have the form:

```
[<user>:]<name>.<type>
```

Where:

- `<user>` is a user number 0–15 (or a drive letter A–P for drive specification).
- `<name>` is 1–8 characters of name (letters, digits, and some symbols).
- `<type>` is 0–3 characters of type (e.g., `COM` for command, `BAS` for BASIC, `TXT` for text).

Examples:

- `A:MYPROG.COM`: file `MYPROG.COM` on drive A.
- `B:DATA.TXT`: file `DATA.TXT` on drive B.
- `MYPROG.COM`: file on the current drive and current user area.

The user-number prefix (`0:`, `1:`, etc.) is rarely used in file specifications; it is set globally via the `USER` command.

### 4.2 File types

Standard CP/M file types include:

| Extension | Meaning |
|---|---|
| `.COM` | Command (executable program) |
| `.BAS` | BASIC source file |
| `.INT` | BASIC intermediate (tokenised) |
| `.REL` | Relocatable object file |
| `.HEX` | Intel HEX format (alternative to .COM) |
| `.TXT` | Plain text |
| `.DOC` | Document (WordStar or other) |
| `.BAK` | Backup file (auto-created by editors) |
| `.SUB` | Submit (batch) file |
| `.ASM` | Assembly source |
| `.PRN` | Print file (assembly listing output) |
| `.LIB` | Library file |
| `$$$` | Temporary file |

The convention is informal — programs can use any 3-letter extension — but most CP/M software follows these conventions.

### 4.3 File allocation

CP/M files are stored in **allocation blocks**, with each block being 1 KB, 2 KB, 4 KB, 8 KB, or 16 KB depending on disk capacity. A directory entry (extent) tracks up to 16 blocks; files larger than 16 × (block size) span multiple extents.

The directory itself is stored in reserved tracks at the beginning of the disk. Each entry is **32 bytes**:

| Offset | Size | Field |
|---|---|---|
| `+0` | 1 | User number (0–15) |
| `+1` | 8 | Filename |
| `+9` | 3 | Type |
| `+12` | 1 | Extent number (high byte) |
| `+13` | 1 | Reserved |
| `+14` | 1 | Extent number (low byte) |
| `+15` | 1 | Records in last block (1–128) |
| `+16` | 16 | Allocation block map |
| `+28` | 4 | Reserved |

This format is shared by TR-DOS's directory entries (with some modifications), the +3 DOS file system, and MS-DOS's early versions.

### 4.4 User numbers

The first byte of every directory entry is a **user number** (0–15). Files in different user areas are invisible to each other. A program in user 0 sees only user-0 files; switching to user 1 reveals a different set.

The `USER` command switches user areas: `USER 5`. This is CP/M's primitive form of file isolation — what we would today call "directories" or "folders". The mechanism was inherited by MS-DOS as directories in version 2.0 (1983).

### 4.5 Read-only and system attributes

Each directory entry has two attribute bits:

- **Read-only** (`R/O`): the file cannot be deleted, renamed, or modified.
- **System** (`SYS`): the file is hidden from normal `DIR` listings (visible with `DIR S`).

These attributes are set with the `STAT` command. They are rarely used in practice.

---

## §5. The BDOS API

The BDOS exposes about 40 function calls (CP/M 2.2). All are called via the `#0005` dispatch address with the function number in C and the argument in DE.

### 5.1 The function table

The most important BDOS functions:

| Function | Name | Purpose |
|---|---|---|
| 0 | `BOOT` | Reset / warm boot |
| 1 | `CONIN` | Read console character |
| 2 | `CONOUT` | Write console character |
| 3 | `READER` | Read reader device |
| 4 | `PUNCH` | Write punch device |
| 5 | `LIST` | Write list (printer) device |
| 6 | `DIRECT_IO` | Direct console I/O |
| 7 | `GET_IOBYTE` | Get I/O byte |
| 8 | `SET_IOBYTE` | Set I/O byte |
| 9 | `PRINT$` | Print `$`-terminated string |
| 10 | `READLINE` | Read buffered line |
| 11 | `CONST` | Console status |
| 12 | `VERSION` | Get CP/M version |
| 13 | `RESET` | Reset disk system |
| 14 | `SELDSK` | Select disk drive |
| 15 | `OPEN` | Open file |
| 16 | `CLOSE` | Close file |
| 17 | `SEARCH` | Search for first match |
| 18 | `SEARCHN` | Search for next match |
| 19 | `DELETE` | Delete file |
| 20 | `READ` | Read next record (128 bytes) |
| 21 | `WRITE` | Write next record |
| 22 | `MAKE` | Create file |
| 23 | `RENAME` | Rename file |
| 24 | `LOGINV` | Get login vector |
| 25 | `CURDSK` | Get current disk |
| 26 | `SETDMA` | Set DMA address |
| 27 | `ALLVEC` | Get allocation vector |
| 28 | `WPDSK` | Write-protect disk |
| 29 | `ROVEC` | Get read-only vector |
| 30 | `FATTR` | Set file attributes |
| 31 | `GETDPB` | Get disk parameter block |
| 32 | `GETSETU` | Get/set user number |
| 33 | `READR` | Read random record |
| 34 | `WRITER` | Write random record |
| 35 | `COMPSIZE` | Compute file size |
| 36 | `SETRAN` | Set random record |

Functions 33 and 34 are particularly important: they allow random access to any 128-byte record in a file, not just sequential reads. Random access is essential for databases (dBase II uses it heavily).

### 5.2 Worked example: print a string

```z80
LD   DE,msg
LD   C,9                  ; function 9: PRINT$ (string)
CALL #0005
RET

msg:    DB   'Hello, CP/M!$'    ; $-terminated
```

The `$` terminator is unusual (Unix strings are null-terminated, MS-DOS uses `$` for some functions and null for others). The convention is a CP/M artefact.

### 5.3 Worked example: open and read a file

```z80
; Open a file and read its first record.
LD   DE,fcb               ; pointer to a 36-byte FCB
LD   C,15                 ; function 15: OPEN
CALL #0005
OR   A
JR   NZ,open_failed       ; A = #FF means file not found

; Read the first 128-byte record (into default DMA buffer at #0080)
LD   DE,fcb
LD   C,20                 ; function 20: READ
CALL #0005
OR   A
JR   NZ,read_failed       ; A = 1 means end of file

; The first 128 bytes of the file are now at #0080-#00FF
RET

fcb:    DB   0,'MYFILE  TXT'    ; user 0, filename, type (11 bytes total)
        DS   25                  ; rest of the 36-byte FCB (filled by OPEN)
```

This pattern — open, read, process, repeat — is the universal CP/M file-access idiom. Programs that need random access use functions 33/34 instead.

### 5.4 Worked example: create a file and write

```z80
; Create a new file and write one record.
LD   DE,fcb
LD   C,22                 ; function 22: MAKE (create)
CALL #0005
OR   A
JR   NZ,create_failed

; The DMA buffer (#0080) currently has data we want to write
LD   DE,fcb
LD   C,21                 ; function 21: WRITE
CALL #0005
OR   A
JR   NZ,write_failed

; Close the file (otherwise the record may not be flushed to disk)
LD   DE,fcb
LD   C,16                 ; function 16: CLOSE
CALL #0005
RET

fcb:    DB   0,'NEWFILE TXT'
        DS   25
```

Note that the `CLOSE` call is mandatory: CP/M buffers writes and may not flush them to disk until close. Forgetting to close means losing data — a common beginner's mistake.
---

## §6. CP/M on the Spectrum

Several Spectrum-compatible machines could run CP/M. This section covers the major ports.

### 6.1 The +3 and +2A

The most common Spectrum CP/M path is the **+3 (and +2A with a disk drive attached)**. The +3 shipped with a custom CP/M 2.2 port in its ROM, accessible by booting a CP/M system disk. See [plus3dos.md](plus3dos.md) §7 for the full story.

The +3's CP/M provides:

- A TPA of approximately 56 KB.
- A 51-column text mode using the +3's standard display hardware.
- Support for the +3's built-in disk drive and most parallel printers.
- Compatibility with the Amstrad CPC's CP/M software library (which is substantial).

The +3's CP/M is not 100% bug-compatible with the Amstrad CPC's CP/M, but the differences are minor and most software works on both.

### 6.2 The ATM Turbo

The **ATM Turbo** (1991–1993) is a Soviet Spectrum clone with significantly enhanced hardware, including a CPU that can run at 7 MHz (twice the Spectrum's standard 3.5 MHz) and a hardware text mode. The ATM Turbo can run CP/M via a custom BIOS that takes advantage of its hardware.

The ATM Turbo's CP/M provides:

- A TPA of approximately 60 KB.
- A 64-column or 80-column text mode (using the ATM's hardware text mode).
- Support for hard disks via the ATM's IDE interface.
- Significant speed advantage over the +3 (the 7 MHz CPU runs CP/M at roughly PC-XT speeds).

The ATM Turbo CP/M was popular in the early Russian hobbyist scene but is rare today. Few non-Russian users have ever encountered it.

### 6.3 The Sprinter

The **Sprinter** (SPRINTER 2000, by Peters Plus Ltd.) is a late-1990s Russian Spectrum clone with an even more enhanced architecture: it includes a 21 MHz Z80-compatible CPU, a Super VGA video controller, IDE hard disk support, and PS/2 keyboard and mouse ports. The Sprinter can run CP/M via a custom BIOS that takes advantage of its powerful hardware.

The Sprinter's CP/M provides:

- A TPA of approximately 62 KB (the largest of any Spectrum CP/M port).
- An 80-column text mode at VGA resolution.
- Support for FAT-formatted hard disks (a major step up from floppy-only CP/M).
- CPU speeds high enough that CP/M software feels "modern" rather than "1980s".

The Sprinter CP/M is the most capable Spectrum CP/M port ever produced. However, the Sprinter itself is extremely rare — only a few thousand units were ever produced — so its CP/M is largely a curiosity today.

### 6.4 Other ports

Several other Spectrum clones and expansions can run CP/M:

- **The Peters Plus Pentagon Turbo+** had a CP/M-compatible mode via custom software.
- **The KAY-1024** could run CP/M via a third-party BIOS.
- **Some Pentagon configurations** with the right expansion cards could boot a Pentagon-specific CP/M.

None of these are widely used. The +3 remains the de facto reference for Spectrum CP/M, with the ATM Turbo and Sprinter as exotic alternatives.

### 6.5 Emulated CP/M

For modern users, the easiest way to run CP/M on a Spectrum-compatible machine is **emulation**. Most Spectrum emulators (Fuse, ZEsarUX, Spectaculator) can boot CP/M disks on emulated +3 hardware. The user inserts a CP/M `.DSK` image, types the boot commands, and is in CP/M within seconds.

There is also a modern CP/M emulator that runs under NextZXOS on the ZX Spectrum Next: it boots CP/M `.COM` files directly, without requiring a full CP/M system disk. This makes the Next a particularly convenient platform for exploring the CP/M software library.

### 6.6 What about Pentagon / Scorpion?

A common question: can a Pentagon or Scorpion (the standard Soviet clones) run CP/M? The answer is **generally no**, for two reasons:

1. **Memory layout.** The Pentagon's ROM-at-the-bottom layout is incompatible with CP/M's RAM-everywhere expectation. Converting the Pentagon to a flat-RAM machine requires significant hardware modification.
2. **No market demand.** The Soviet scene standardized on TR-DOS for disk I/O and never developed a strong CP/M ecosystem. Soviet users who needed "serious" computing typically used a Soviet-built PC clone (the Electronika, Poisk, or ES-1840) rather than a Spectrum running CP/M.

The result is that CP/M is primarily a Western-Spectrum phenomenon, with the +3 as its main vehicle.

---

## §7. The Software Library

The CP/M software library is enormous — well over 10,000 programs were commercially released, and many more were distributed as shareware, freeware, or public domain. This section covers the most important categories.

### 7.1 Word processors

- **WordStar** (MicroPro International): the dominant CP/M word processor. Versions 3.0 and 4.0 are the canonical releases. WordStar's keyboard commands (Control-K for block operations, Control-Q for quick movements) influenced every later word processor — including WordPerfect and Microsoft Word's "compatibility mode".
- **Magic Wand**: a popular alternative, particularly for legal documents.
- **Perfect Writer**: part of the Perfect Software suite.
- **NewWord**: an improved WordStar clone.

### 7.2 Spreadsheets

- **SuperCalc** (Sorcim): the dominant CP/M spreadsheet. Originally bundled with the Osborne 1; later sold separately.
- **MultiPlan** (Microsoft): Microsoft's pre-Excel spreadsheet, available on CP/M.
- **Lucid 1-2-3**: a Lotus 1-2-3 predecessor that ran on CP/M.

### 7.3 Databases

- **dBase II** (Ashton-Tate): the first widely-used personal database management system. Originally written in assembly for CP/M; later ported to MS-DOS and evolved into xBase (FoxPro, Clipper, etc.).
- **Condor**: an early CP/M database.

### 7.4 Programming languages

- **Microsoft BASIC-80** (Microsoft): the canonical CP/M BASIC. Versions 5.x added structured programming features.
- **BASCOM** (Microsoft): a BASIC compiler, generating .COM files from BASIC source.
- **CBASIC** (Compiler Systems): another popular BASIC compiler.
- **Turbo Pascal** (Borland, 1983+): the revolutionary Pascal IDE that made Borland famous. Versions 1.x, 2.x, and 3.x ran on CP/M.
- **Microsoft FORTRAN-80, COBOL-80, BASIC-80**: the Microsoft language series.
- **MultiMat** and **MUMATH**: symbolic math and Lisp.
- **SMALL-C**: a small C compiler that produced 8080 assembly as output.
- **Aztec C** (Manx Software): a more complete C compiler for CP/M.

### 7.5 Utilities

- **WordStar's non-document mode**: a general-purpose text editor.
- **VEDIT**: a programmer's editor.
- **SED**: a screen editor (a precursor to Unix `vi`).
- **PIP** (Peripheral Interchange Program): the standard CP/M file copy utility.
- **STAT**: shows disk and file statistics.
- **SUBMIT**: runs batch files of CP/M commands.
- **XSUB**: allows nested batch processing.
- **DDT** (Dynamic Debugging Tool): the standard CP/M debugger.
- **SID** and **ZSID**: alternative debuggers.
- **ASM**: the standard CP/M assembler (8080 source).
- **MAC** (Digital Research): a more powerful macro assembler.
- **LINK-80**: a linker for combining `.REL` object files.
- **LOAD**: converts `.HEX` files to `.COM` executables.

### 7.6 Games

CP/M is not primarily a games platform, but there are notable games:

- **Colossal Cave Adventure** (the original "ADVENT", 1977): the canonical text adventure.
- **Zork I, II, III** (Infocom): released on CP/M as well as every other platform.
- **Empire**: a multiplayer conquest game.
- **Eliza**: the classic conversational simulation.
- **Hamurabi**: the resource-management classic.
- **Lunar Lander** variants.
- Various board games (chess, checkers, etc.).

Most CP/M games are text-based; the few graphics-based ones are tied to specific terminals or machines.

### 7.7 Where to find CP/M software today

The CP/M software library is preserved by:

- **The CP/M Museum** (cpm80.net): a comprehensive archive of CP/M software.
- **The Walnut Creek CD-ROM archive**: a 1990s CD-ROM archive that has been preserved online.
- **The Simtel archive**: another 1990s CP/M software archive.
- **The comp.os.cpm newsgroup**: still active, with regular posts from CP/M enthusiasts.
- **The Retro Computing community**: active discussion of CP/M on Retro Computing forums and Reddit.

Almost the entire CP/M commercial catalog is now abandonware and freely downloadable.

---

## §8. Modern Status

CP/M is a "dead" operating system in the sense that no commercial development happens for it. But it is very much "alive" in the retro-computing community.

### 8.1 Why CP/M still matters

- **Historical significance.** CP/M is the direct ancestor of MS-DOS, Windows, and every modern PC operating system. Understanding CP/M is understanding where PCs came from.
- **The software library.** The 1980s CP/M software library is a unique cultural artefact. Programs like WordStar and dBase II defined what "office software" meant for a generation.
- **Simplicity.** CP/M is small enough to understand completely — a single person can read the entire BDOS source in a day. It is a great teaching tool for operating-system concepts.
- **The Z80 connection.** For Spectrum enthusiasts, CP/M is the natural "serious" OS — it runs on the same CPU as the Spectrum, just in a different mode.

### 8.2 CP/M in modern emulators

Every major Z80 emulator can run CP/M. Beyond the Spectrum-specific emulators:

- **MyZ80** (1990s): an MS-DOS program that emulates a Z80 running CP/M. The classic CP/M emulator.
- **z80pack** (cross-platform): a modern CP/M emulator.
- **RunCPM** (cross-platform): a CP/M 2.2 implementation that runs as a regular application on modern operating systems.
- **Various JavaScript CP/M emulators**: in-browser CP/M experiences.

These emulators let users explore the CP/M software library without any 1980s hardware.

### 8.3 The Spectrum CP/M community

The Spectrum-specific CP/M community is small but dedicated. It centers on:

- **Owners of real +3 hardware**: a few hundred active users worldwide, mostly in the UK and Eastern Europe.
- **Spectrum emulator users**: a much larger group, primarily running +3 CP/M via Fuse, ZEsarUX, or Spectaculator.
- **The World of Spectrum archive**: hosts a large collection of +3 CP/M `.DSK` images.
- **The comp.sys.sinclair and comp.os.cpm newsgroups**: discussion forums (low traffic but still active).
- **Modern Spectrum events** (Centre for Computing History, Spectrum 50th celebrations, etc.): occasionally feature CP/M demos on real +3 hardware.

For Spectrum enthusiasts, CP/M is a side trip — interesting, historically important, but secondary to the main Spectrum experience of BASIC programming, games, and demos.

---

## §9. Cross-References

### 9.1 Within the Operating Systems section

- [README.md](README.md) — section index
- [plus3dos.md](plus3dos.md) §7 — the +3's CP/M compatibility (the most common Spectrum CP/M path)
- [fuzix.md](fuzix.md) — the modern Unix-like alternative for the Spectrum
- [trdos.md](trdos.md) — TR-DOS, the Soviet alternative; did not use CP/M

### 9.2 Outside the section

- [../01_cpu/README.md](../01_cpu/README.md) — the Z80 CPU, which CP/M is built around
- [../02_hardware/original/README.md](../02_hardware/original/README.md) — original Sinclair hardware (+3 and +2A)

### 9.3 External resources

- **The CP/M Museum**: https://cpm80.net/
- **The CP/M Wiki**: https://www.cpm.z80.de/
- **RunCPM**: https://github.com/MockbaTheBorg/RunCPM
- **z80pack**: https://www.unix4fun.net/z80pack/
- **Digital Research source archives**: Garry Kildall's original CP/M source code is preserved at the Computer History Museum
- **"CP/M: An Oral History"** by David Craig, a comprehensive history of CP/M
- **The comp.os.cpm newsgroup**: still active, archived on Google Groups
- **[World of Spectrum](https://worldofspectrum.org/)'s +3 CP/M archive**: https://worldofspectrum.org/+3/cpm/

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/). Attribute as "CP/M on the Spectrum, from the ZX Spectrum Knowledge Base".
