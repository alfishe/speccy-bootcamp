[← Plan](../../PLAN.md) · [DOS & Tape](README.md)

# Western DOS Programming — +3 DOS, ESXDOS, NextZXOS from Assembly

TR-DOS won the Soviet market. In the West, three different disk operating systems competed for the Spectrum user's floppy drive: **+3 DOS** (Amstrad's CP/M-derived system, built into the +2A/+3), **ESXDOS** (Dylan Smith's modern firmware for the DivIDE/DivMMC IDE interfaces), and **NextZXOS** (Garry Lancaster's ESXDOS derivative for the ZX Spectrum Next). None of them dominate the way TR-DOS dominated the East — but each has a loyal user base, and each presents a different assembly API.

This article covers all three Western DOSes from the assembly programmer's perspective, side by side. It is the third article in the [DOS and Tape series](README.md) and assumes you have read [trdos_programming.md](trdos_programming.md). It does **not** duplicate the system references — [+3 DOS](../../04_operating_systems/plus3dos.md), [ESXDOS](../../04_operating_systems/esxdos.md), [NextZXOS](../../04_operating_systems/nextzxos.md) — those cover the history, hardware, and complete API catalog. This article provides the practical code patterns and the side-by-side comparison that helps you choose the right approach.

> [!NOTE]
> If you are writing software for real hardware in 2024, the most common Western target is **ESXDOS on DivMMC** — nearly every real-hardware Spectrum owner has a DivMMC SD-card interface. NextZXOS is relevant if you target the ZX Spectrum Next specifically. +3 DOS is the least common target today but matters for historical compatibility and +2A/+3 owners.

---

## Why Three DOSes?

### History Summary

| DOS | Year | Author | Target Hardware | Storage Medium |
|---|---|---|---|---|
| +3 DOS | 1987 | Amstrad | ZX Spectrum +2A/+3 | 3-inch floppy |
| ESXDOS | 2008-2018 | Dylan Smith | DivIDE / DivMMC | IDE HDD / CF / SD |
| NextZXOS | 2017+ | Garry Lancaster | ZX Spectrum Next | SD card |

Each DOS fills a different niche:

- **+3 DOS** was the only factory-installed DOS on a Sinclair-branded Spectrum. It uses a CP/M-compatible filesystem and provides the RSX (Resident System Extension) mechanism for assembly calls. Its limitation: proprietary 3-inch disk format, rare today.

- **ESXDOS** is the modern hobbyist standard. It runs on DivIDE (IDE/CF) and DivMMC (SD) interfaces, supports FAT16/FAT32 filesystems, and provides a Unix-flavored hook code API at address `#0084`. If you have a real Spectrum with mass storage in 2024, you are probably running ESXDOS.

- **NextZXOS** extends ESXDOS with Next-specific features (hardware acceleration, Layer 2, sprites, copper). The API is ESXDOS-compatible with additions. If you target the Next, NextZXOS is your OS.

### API Style Comparison

| Feature | +3 DOS | ESXDOS | NextZXOS |
|---|---|---|---|
| **Call mechanism** | RSX via `JP #000C` | Hook codes at `#0084` | ESXDOS-compatible + extensions |
| **Dispatch** | Name string lookup | Function number in register | Same as ESXDOS |
| **Filename format** | 8.3 (CP/M style) | 8.3 or LFN (FAT) | 8.3 or LFN (FAT32) |
| **Filesystem** | CP/M (flat, user numbers) | FAT16/FAT32 | FAT32 |
| **Max file size** | 16 MB (CP/M) | 2 GB (FAT16) / 4 GB (FAT32) | Same as FAT32 |
| **Memory model** | Bank 7 = DOS ROM, bank 3 = DOS RAM | DivMMC ROM paged at #2000 | ESXDOS overlay at #2000 |
| **Error model** | A = error code, carry set | A = error code, carry set | Same as ESXDOS |

For the full history and system architecture of each, see the linked OS reference articles. The rest of this article focuses on the practical assembly code.

---

## +3 DOS Programming

+3 DOS provides its services through the **Resident System Extension (RSX)** mechanism. RSX calls are dispatched through the system variable at `#000C` (the `RST #08` extension hook), which looks up the RSX name string and calls the matching function.

### The RSX Call Mechanism

To call a +3 DOS function from assembly:

1. Set up registers with parameters
2. Load HL with the address of the RSX name string (null-terminated)
3. Call the DOS dispatch at `#000C`

```z80
; +3 DOS RSX dispatch
; Entry: HL = address of null-terminated RSX name
;        Other registers = parameters (function-specific)
; Exit:  A = error code (if carry set = error)

plus3_dos_call:
    PUSH IX                  ; save IX (DOS uses it)
    PUSH IY                  ; save IY
    CALL #000C               ; DOS dispatch via RST extension
    POP  IY
    POP  IX
    RET
```

### The Key +3 DOS Functions

| RSX Name | Function | Parameters |
|---|---|---|
| `DOS_OPEN` | Open a file | HL = filename, A = mode (0=read, 1=write, 2=read+write) |
| `DOS_CLOSE` | Close a file | A = file handle (from DOS_OPEN) |
| `DOS_READ` | Read from file | A = handle, HL = buffer, BC = byte count |
| `DOS_WRITE` | Write to file | A = handle, HL = buffer, BC = byte count |
| `DOS_ABANDON` | Close without flushing | A = handle |
| `DOS_SEEK` | Seek to position | A = handle, DEHL = byte offset |
| `DOS_DELETE` | Delete a file | HL = filename |
| `DOS_RENAME` | Rename a file | HL = old name, DE = new name |
| `DOS_FREE_SPACE` | Get free disk space | Returns free space in BC/DE/HL |

### Loading a File via +3 DOS

```z80
; ============================================================
; Load a file using +3 DOS
;
; Entry: HL = filename (null-terminated, "a:filename.ext")
;        DE = load address
; ============================================================

p3_load_file:
    ; Step 1: Open the file
    LD   (load_dest), DE     ; save destination for later

    LD   HL, open_name       ; "DOS_OPEN" + null
    LD   A, 0                ; mode 0 = read
    ; Need filename in HL... actually, +3 DOS uses IX for filename
    LD   IX, p3_filename     ; filename string
    LD   B, 0                ; drive B: (0=A, 1=B)
    CALL #0100               ; DOS_OPEN entry (simplified)
    JR   C, p3_error         ; carry = error
    LD   (file_handle), A    ; save file handle

    ; Step 2: Read the file
    LD   A, (file_handle)
    LD   HL, (load_dest)     ; destination
    LD   BC, 32768           ; max bytes to read
    LD   DE, read_name       ; "DOS_READ" + null
    CALL #0100
    JR   C, p3_error

    ; Step 3: Close the file
    LD   A, (file_handle)
    LD   HL, close_name      ; "DOS_CLOSE" + null
    CALL #0100
    RET

p3_error:
    ; A = error code
    LD   HL, p3_err_msg
    CALL print_string
    RET

p3_filename:    DB "a:gamefile.dat", 0
open_name:      DB "DOS_OPEN", 0
read_name:      DB "DOS_READ", 0
close_name:     DB "DOS_CLOSE", 0
file_handle:    DEFB 0
load_dest:      DEFW 0
p3_err_msg:     DB "+3 DOS error", #0D, 0
```

> [!WARNING]
> The exact entry point for +3 DOS RSX dispatch varies depending on the ROM version and machine model. The example above uses simplified entry addresses. For the definitive API reference, see the [+3 Manual Chapter 8](https://worldofspectrum.net/ZXSpectrum128+3Manual/chapter8pt26.html) and [plus3dos.md](../../04_operating_systems/plus3dos.md).

### +3 DOS Memory Considerations

+3 DOS uses a separate memory bank for its workspace. When calling DOS functions, the machine pages in the DOS ROM (bank 7) and DOS RAM (bank 3) temporarily. Your code in the main RAM banks (`#8000`-`#BFFF`) is unaffected, but anything in bank 3 (`#C000`-`#FFFF`) is overwritten during DOS calls.

**Fix**: Do not keep critical data in the `#C000`-`#FFFF` range when calling +3 DOS. If you must use that range, save your data to a different bank before the call.

---

## ESXDOS Programming

ESXDOS is the most relevant Western DOS for modern real-hardware development. It runs on DivIDE (CompactFlash) and DivMMC (SD card) interfaces, both of which are widely available and affordable. The API is accessed via hook codes dispatched at address `#0084`.

### The Hook Code Dispatch

ESXDOS functions are called via a hook code dispatch at `#0084`. The function number goes in the B register, and parameters go in other registers:

```z80
; ESXDOS dispatch
; Entry: B = function number
;        Other registers = parameters
; Exit:  A = error code (carry set = error)

esxdos_call:
    PUSH IX                  ; ESXDOS may use IX/IY
    PUSH IY
    CALL #0084               ; ESXDOS dispatch
    POP  IY
    POP  IX
    JR   C, esxdos_error      ; carry set = error
    ; Success — results in registers
    RET
esxdos_error:
    ; A = error code
    RET
```

### The Key ESXDOS Functions

| B | Function | Name | Parameters |
|---|---|---|---|
| `#01` | Open file | M_OPENFILE | HL = filename (null-terminated), returns A = handle |
| `#02` | Close file | M_CLOSE | A = handle |
| `#03` | Read file | M_READ | A = handle, DE = buffer, BC = byte count |
| `#04` | Write file | M_WRITE | A = handle, DE = buffer, BC = byte count |
| `#05` | Seek | M_SEEK | A = handle, DEHL = byte offset, C = seek mode |
| `#06` | Get file pos | M_GETPOS | A = handle |
| `#07` | Get status | M_STAT | (device-specific) |
| `#09` | Delete file | M_DELETE | HL = filename |
| `#0A` | Rename file | M_RENAME | HL = old name, DE = new name |
| `#0B` | Make directory | M_MKDIR | HL = path |
| `#0C` | Remove directory | M_RMDIR | HL = path |
| `#0D` | Change directory | M_CHDIR | HL = path |
| `#13` | Open directory | M_OPENDIR | HL = path |
| `#14` | Read directory | M_READDIR | (returns entries) |
| `#16` | Get free space | M_GETFREE | A = drive, returns free space |

### Loading a File via ESXDOS

```z80
; ============================================================
; Load a file using ESXDOS
;
; Entry: HL = filename (null-terminated, e.g. "/games/data.bin")
;        DE = load address
; ============================================================

esxdos_load_file:
    LD   (load_dest), DE     ; save destination

    ; Open the file
    LD   B, #01              ; M_OPENFILE
    PUSH HL                  ; ESXDOS uses HL for filename
    CALL #0084
    POP  HL
    JR   C, esx_error
    LD   (file_handle), A    ; save file handle

    ; Read the file
    LD   A, (file_handle)
    LD   DE, (load_dest)
    LD   BC, #7FFF           ; read up to 32767 bytes
    LD   B, #03              ; M_READ
    CALL #0084
    JR   C, esx_error
    ; BC = bytes actually read

    ; Close the file
    LD   A, (file_handle)
    LD   B, #02              ; M_CLOSE
    CALL #0084
    RET

esx_error:
    ; A = ESXDOS error code
    LD   HL, esx_err_msg
    CALL print_string
    LD   A, (err_code)
    CALL print_hex_byte
    RET

esx_err_msg:   DB "ESXDOS error: ", 0
err_code:      DEFB 0
```

### ESXDOS Filenames

ESXDOS uses standard FAT filenames with forward-slash path separators:

```
/                       Root directory
/games/                 Games subdirectory
/games/game.bin         Specific file
```

Filenames can be up to 255 characters (LFN support). The old 8.3 format also works. Paths are relative to the current directory unless they start with `/`.

### Dot Commands

ESXDOS introduces the **dot command** concept: small programs loaded from the SD card and executed as BASIC extensions. A dot command is invoked by typing `.` followed by the command name at the BASIC prompt:

```
.dir              ; list directory contents
.load game        ; load a file
.tap2trd file     ; convert .TAP to .TRD
```

Dot commands are stored as `.dot` files on the SD card and run as 8 KB overlays. When a dot command executes, it is loaded at address `#2000` and given control. The dot command can call ESXDOS functions to perform file I/O.

#### Dot Command Skeleton

```z80
; ============================================================
; Minimal ESXDOS dot command
; Compiled as: z88dk-z80asm -d -o mycmd.dot mycmd.asm
; Installed: copy mycmd.dot to SD card, type .mycmd at BASIC
; ============================================================

    ORG  #2000               ; dot commands load at #2000

    ; Entry: HL = address of command tail string (arguments)
    ;        (null-terminated, may be empty)

dot_entry:
    ; Save the argument string pointer
    LD   (dot_args), HL

    ; Print a message
    LD   HL, hello_msg
    CALL print_string_z

    ; Parse arguments (if any)
    LD   HL, (dot_args)
    LD   A, (HL)
    AND  A                   ; null? (no arguments)
    JR   Z, .no_args
    ; Print the arguments
    LD   HL, arg_msg
    CALL print_string_z
    LD   HL, (dot_args)
    CALL print_string_z
.no_args:
    LD   A, #0D              ; newline
    CALL print_char_a

    ; Exit — return to BASIC
    ; ESXDOS expects dot commands to return with A=0 for success
    XOR  A
    RET

hello_msg:   DB "My Dot Command v1.0", #0D, 0
arg_msg:     DB "Arguments: ", 0
dot_args:    DEFW 0

; --- Print null-terminated string ---
print_string_z:
    LD   A, (HL)
    AND  A
    RET  Z
    CALL print_char_a
    INC  HL
    JR   print_string_z
```

The 8 KB overlay limit means your dot command (code + data) must fit in addresses `#2000`-`#3FFF`. For larger commands, split into multiple files and chain them.

For the full ESXDOS API including the complete function catalog, memory model, and NMI handling, see [esxdos.md](../../04_operating_systems/esxdos.md).

---

## NextZXOS Programming

NextZXOS is the operating system for the ZX Spectrum Next. It is an ESXDOS derivative — all ESXDOS API calls work on NextZXOS, plus Next-specific extensions.

### ESXDOS Compatibility

Any code written for ESXDOS will run on NextZXOS without modification. The hook code dispatch at `#0084` works identically. The function numbers, parameter passing, and error codes are the same.

The differences are:

| Feature | ESXDOS | NextZXOS |
|---|---|---|
| Overlay limit | 8 KB | Unlimited (can page in more memory) |
| Bank count | 128K max | 2 MB (Next MMU) |
| Hardware | DivIDE/DivMMC IDE | Next SD + DMA |
| File hooks | M_OPENFILE etc. | Same + M_GETHANDLE |
| NextBASIC | Not supported | Full integration |

### Next-Specific Extensions

NextZXOS adds several hooks beyond the ESXDOS set:

| Hook | Name | Purpose |
|---|---|---|
| `M_GETHANDLE` | Get file handle | Get handle for currently running dot command |
| `M_P3DOS` | +3 DOS emulation | Call +3 DOS RSX functions from NextZXOS |
| `M_GETSETDRV` | Drive management | Get/set current drive |
| `M_TRDOS` | TR-DOS emulation | Call TR-DOS hook codes from NextZXOS |

### Loading a .SCR File (NextZXOS Example)

```z80
; ============================================================
; Load and display a .SCR file using NextZXOS
; A .SCR file is 6912 bytes: 6144 pixel data + 768 attributes
; ============================================================

load_scr:
    ; Open the file
    LD   B, #01              ; M_OPENFILE
    LD   HL, scr_filename
    CALL #0084
    JR   C, scr_error
    LD   (scr_handle), A

    ; Read into screen memory
    LD   A, (scr_handle)
    LD   DE, #4000           ; screen memory
    LD   BC, 6912            ; 6144 + 768 bytes
    LD   B, #03              ; M_READ
    CALL #0084
    JR   C, scr_error

    ; Close file
    LD   A, (scr_handle)
    LD   B, #02              ; M_CLOSE
    CALL #0084
    RET

scr_error:
    LD   HL, scr_err_msg
    CALL print_string
    RET

scr_filename:   DB "/art/title.scr", 0
scr_handle:     DEFB 0
scr_err_msg:    DB "Cannot load .SCR file", #0D, 0
```

### NextBASIC Integration

NextZXOS allows NextBASIC to call ESXDOS functions directly using the `%` prefix syntax. From assembly, you can invoke NextBASIC commands, but this is rarely needed — the ESXDOS API is more direct.

For the full NextZXOS API, see [nextzxos.md](../../04_operating_systems/nextzxos.md) and the [NextZXOS API PDF](https://sarah.speccy.cz/sarah/nextzxos_api.pdf).

---

## API Comparison Matrix

The same basic operations performed across all three DOSes, side by side. Use this table to port code between platforms or to write portable wrappers.

### Opening a File

| DOS | Call | Entry |
|---|---|---|
| +3 DOS | `DOS_OPEN` RSX | IX = filename, A = mode, B = drive |
| ESXDOS | `M_OPENFILE` (#01) | HL = filename (null-terminated) |
| NextZXOS | `M_OPENFILE` (#01) | HL = filename (null-terminated) |
| TR-DOS | `READ-FILE` (#04) | HL = 9-byte filename, DE = load address |

### Reading Data

| DOS | Call | Entry |
|---|---|---|
| +3 DOS | `DOS_READ` RSX | A = handle, HL = buffer, BC = count |
| ESXDOS | `M_READ` (#03) | A = handle, DE = buffer, BC = count |
| NextZXOS | `M_READ` (#03) | A = handle, DE = buffer, BC = count |
| TR-DOS | No equivalent (loads entire file) | — |

### Writing Data

| DOS | Call | Entry |
|---|---|---|
| +3 DOS | `DOS_WRITE` RSX | A = handle, HL = buffer, BC = count |
| ESXDOS | `M_WRITE` (#04) | A = handle, DE = buffer, BC = count |
| NextZXOS | `M_WRITE` (#04) | A = handle, DE = buffer, BC = count |
| TR-DOS | `WRITE-FILE` (#05) | HL = filename, DE = source, BC = length |

### Closing

| DOS | Call | Entry |
|---|---|---|
| +3 DOS | `DOS_CLOSE` RSX | A = handle |
| ESXDOS | `M_CLOSE` (#02) | A = handle |
| NextZXOS | `M_CLOSE` (#02) | A = handle |
| TR-DOS | No explicit close | File loaded in one operation |

### Seeking

| DOS | Call | Entry |
|---|---|---|
| +3 DOS | `DOS_SEEK` RSX | A = handle, DEHL = offset |
| ESXDOS | `M_SEEK` (#05) | A = handle, DEHL = offset, C = mode |
| NextZXOS | `M_SEEK` (#05) | A = handle, DEHL = offset, C = mode |
| TR-DOS | Not available (use sector reads) | — |

### Deleting

| DOS | Call | Entry |
|---|---|---|
| +3 DOS | `DOS_DELETE` RSX | HL = filename |
| ESXDOS | `M_DELETE` (#09) | HL = filename |
| NextZXOS | `M_DELETE` (#09) | HL = filename |
| TR-DOS | `DELETE-FILE` (#08) | HL = 9-byte filename |

### Getting Free Space

| DOS | Call | Entry |
|---|---|---|
| +3 DOS | `DOS_FREE_SPACE` RSX | (returns in BC/DE/HL) |
| ESXDOS | `M_GETFREE` (#16) | A = drive, returns in BC/DE/HL |
| NextZXOS | `M_GETFREE` (#16) | A = drive, returns in BC/DE/HL |
| TR-DOS | Not available via hook code | Read catalog sector and count |

---

## Portable Code Strategy

If you want your program to run on multiple DOSes, you need a runtime detection layer and per-DOS function wrappers.

### Runtime DOS Detection

```z80
; ============================================================
; Detect which DOS is available
; Returns: A = DOS type (0=none, 1=TR-DOS, 2=+3DOS, 3=ESXDOS, 4=NextZXOS)
; ============================================================

detect_dos:
    ; Check for ESXDOS first (most common on modern hardware)
    ; ESXDOS hooks at #0084 — test by calling M_GETSETDRV safely
    ; If it returns a valid drive number, ESXDOS is present

    ; Check for NextZXOS by looking for Next hardware signature
    LD   BC, #243B           ; Next register port
    LD   A, #80              ; peripheral 4 register (unique to Next)
    OUT  (C), A
    LD   B, #253             ; Next data port (#233B)
    IN   A, (C)              ; read register
    CP   #FF                 ; on non-Next hardware, reads floating bus
    JR   Z, .not_next
    ; This is a Next — NextZXOS is available
    LD   A, 4                ; NextZXOS
    RET
.not_next:

    ; Check for ESXDOS at #0084
    ; The ESXDOS ROM has a signature string at a known offset
    ; Simpler approach: call M_GETSETDRV and check for valid return
    LD   B, #16              ; M_GETSETDRV
    LD   A, #FF              ; invalid drive (get current)
    CALL #0084
    JR   C, .no_esxdos       ; carry set = ESXDOS not present
    ; A = current drive number (0+)
    LD   A, 3                ; ESXDOS
    RET
.no_esxdos:

    ; Check for TR-DOS by looking for the "TRDOS" signature
    ; in the ROM at #0000 when paged in
    ; (TR-DOS detection requires paging the ROM, which is risky
    ; if no Beta 128 is present. Use a safe check.)
    ; For simplicity, check if port #FF is writable and TR-DOS responds
    ; This is a simplified check — production code should be more careful
    LD   A, 1                ; TR-DOS (assume for now)
    ; Full detection omitted for brevity
    RET
```

### Wrapper Functions

Once the DOS type is known, use a jump table to dispatch to the right routine:

```z80
; DOS function jump table
dos_jumptable:
    DEFW dos_none_open       ; 0 = none
    DEFW trdos_open          ; 1 = TR-DOS
    DEFW plus3_open          ; 2 = +3 DOS
    DEFW esxdos_open         ; 3 = ESXDOS
    DEFW nextzxos_open       ; 4 = NextZXOS

; Generic open file
dos_open_file:
    LD   A, (dos_type)       ; which DOS?
    ADD  A, A                ; * 2 (each entry is 2 bytes)
    LD   L, A
    LD   H, 0
    LD   DE, dos_jumptable
    ADD  HL, DE
    LD   E, (HL)
    INC  HL
    LD   D, (HL)
    EX   DE, HL
    JP   (HL)                ; jump to the right open function

dos_type:   DEFB 3           ; detected at startup
```

### Conditional Compilation with z88dk

If you are using z88dk, you can use C preprocessor directives to compile per-DOS versions:

```c
/* Portable file loader using z88dk */
#include <stdlib.h>

#ifdef TARGET_ESXDOS
#include <arch/zx/esxdos.h>

void *load_file(const char *filename, void *dest)
{
    int fd = esxdos_f_open(filename, ESXDOS_MODE_READ);
    if (fd < 0) return NULL;
    esxdos_f_read(fd, dest, 32768);
    esxdos_f_close(fd);
    return dest;
}

#elif defined TARGET_PLUS3

void *load_file(const char *filename, void *dest)
{
    /* +3 DOS implementation using RSX calls */
    /* ... */
    return dest;
}

#elif defined TARGET_TRDOS

void *load_file(const char *filename, void *dest)
{
    /* TR-DOS implementation using hook codes */
    /* ... */
    return dest;
}

#endif
```

Compile with `-DTARGET_ESXDOS` or `-DTARGET_TRDOS` to select the DOS.

---

## Error Handling

### Error Code Ranges

| DOS | Error encoding |
|---|---|
| +3 DOS | Carry set on error, A = code (#00-#FF) |
| ESXDOS | Carry set on error, A = code |
| NextZXOS | Same as ESXDOS |
| TR-DOS | Carry clear on error, A = code (note: reversed!) |

> [!WARNING]
| TR-DOS has carry **clear** on error, while +3 DOS/ESXDOS have carry **set** on error. This is the most common source of bugs when porting between DOSes. Always check the carry flag convention for each DOS.

### Common Error Codes

| Meaning | +3 DOS | ESXDOS | TR-DOS |
|---|---|---|---|
| File not found | varies | `#05` | `#05` |
| Disk full | varies | `#08` | `#04` |
| Bad filename | varies | `#0A` | — |
| Read-only / write-protect | varies | `#0F` | `#01` |
| No disk | varies | `#10` | `#02` |

The exact error code numbers differ across DOSes. For production code, map each DOS's codes to a common error enum.

---

## Pitfalls

### 1 — Wrong Carry Flag Convention

TR-DOS sets carry on **success** (clear on error). +3 DOS and ESXDOS set carry on **error** (clear on success). Code ported from one to the other without adjusting the carry check will always take the wrong branch.

**Fix**: Abstract the error check behind a wrapper function that normalizes the convention.

### 2 — Bank Switching Conflicts

All three DOSes page in their own ROM and/or RAM during calls. The specific bank and address range differs:

| DOS | ROM/RAM used |
|---|---|
| +3 DOS | Bank 7 (DOS ROM) at #0000-#3FFF, bank 3 (DOS RAM) at #C000-#FFFF |
| ESXDOS | 8 KB overlay at #2000-#3FFF, uses some workspace in main RAM |
| NextZXOS | Same as ESXDOS, plus MMU pages for Next-specific features |

**Fix**: Do not keep critical data in the ranges that get overwritten. Check each DOS's memory map before relying on data in `#C000`-`#FFFF` or `#2000`-`#3FFF`.

### 3 — IY/IX Corruption

None of the three DOSes guarantee preservation of IX or IY. The ROM ISR uses IY. If a DOS call trashes IY and an interrupt fires, the system crashes.

**Fix**: Always save and restore IX and IY around DOS calls. Or disable interrupts (`DI`) during the call.

### 4 — Filename Case Sensitivity

+3 DOS filenames are case-insensitive (CP/M convention). ESXDOS on FAT is also case-insensitive for 8.3 names but case-sensitive for long filenames depending on the SD card format. NextZXOS is similar.

**Fix**: Normalize filenames to uppercase for maximum compatibility.

### 5 — 8 KB Dot Command Limit (ESXDOS)

ESXDOS dot commands must fit in 8 KB (`#2000`-`#3FFF`). If your code exceeds this, there is no way to extend it within ESXDOS. NextZXOS lifts this limit via the Next's MMU.

**Fix**: Split large dot commands into multiple files. Use the first file to load the second into a different memory bank.

### 6 — FAT Endianness on Z80

FAT structures are little-endian, and the Z80 is also little-endian. This means you can read FAT fields directly without byte-swapping — unlike big-endian systems (68000, SPARC). This is a feature, not a bug, but it surprises programmers who expect to need endianness conversion.

---

## Cross-References

- **[esxdos.md](../../04_operating_systems/esxdos.md)** — ESXDOS system reference (history, architecture, complete API)
- **[plus3dos.md](../../04_operating_systems/plus3dos.md)** — +3 DOS system reference (RSX, CP/M compatibility)
- **[nextzxos.md](../../04_operating_systems/nextzxos.md)** — NextZXOS system reference (Next integration, API)
- **[trdos.md](../../04_operating_systems/trdos.md)** — TR-DOS system reference (for comparison)
- **[divide_divmmc.md](../../03_io/storage/divide_divmmc.md)** — DivIDE/DivMMC hardware reference
- **[tape_programming.md](tape_programming.md)** — tape loading (fallback when no disk available)
- **[trdos_programming.md](trdos_programming.md)** — TR-DOS programming tutorial
- **[file_format_handling.md](file_format_handling.md)** — parsing disk image files from code
- **[mass_storage_programming.md](mass_storage_programming.md)** — direct IDE/SD access bypassing all DOSes

## References

- [ESXDOS Manual](https://www.benophetinternet.nl/hobby/vanmezelf/ESXDOS%20manual.pdf) — official ESXDOS API documentation
- [NextZXOS API PDF](https://sarah.speccy.cz/sarah/nextzxos_api.pdf) — NextZXOS function reference
- [+3 Manual Chapter 8](https://worldofspectrum.net/ZXSpectrum128+3Manual/chapter8pt26.html) — +3 DOS machine-code API
- [+3 DOS System Reference](../../04_operating_systems/plus3dos.md) — in-repo canonical reference
- [[ESXDOS](https://github.com/joneiricon/ESXDOS) System Reference](../../04_operating_systems/esxdos.md) — in-repo canonical reference
- [[NextZXOS](https://gitlab.com/thesmog358/tbblue) System Reference](../../04_operating_systems/nextzxos.md) — in-repo canonical reference
- [ESXDOS forums](http://board.esxdos.org/) — community support and API discussions
- [The Fossil Record](http://www.thefossilrecord.co.uk/tag/esxdos/) — ESXDOS development articles
