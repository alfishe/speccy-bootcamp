[← Home](../README.md) · [References](README.md)

# Error Codes — ZX Spectrum Error Reference

Every error code reported by Sinclair BASIC, 128K BASIC, +3 DOS, TR-DOS, ESXDOS, IS-DOS, and NextZXOS, with the message text, the conditions that trigger each one, and recovery patterns for assembly programmers. The ROM encodes errors as a single byte in the system variable `ERR_NR` at `#5C3A` — most negative as a twos-complement byte — and a matching message string in the ROM.

> [!NOTE]
> For the *mechanism* of error reporting in Sinclair BASIC (the `RST #08` call, `ERR_NR`, `ERR_SP`, error handler chains), see [system_variables.md](../04_operating_systems/system_variables.md) for the full system variable reference and [rom_routines.md](rom_routines.md) for the `RST #08` entry point. This article is the **lookup table** — you come here to find out what a specific code means.

---

## How Sinclair BASIC Reports Errors

When a BASIC error occurs, the ROM does three things:

1. Writes the error code (negated, so code `9` becomes `#F7`) into `ERR_NR` at `#5C3A`.
2. Sets `ERR_SP` (system variable at `#5C3D`, but really a structure holding the error-handler stack pointer) so that subsequent `RETURN` calls land in the error routine.
3. Calls `RST #08` which prints the message and exits to the editor.

Assembly programs can intercept by replacing `ERR_SP` with their own address — `RST #08` will then land there with `ERR_NR` already set.

---

## 48K / 128K / +2 / +2A / +3 BASIC Errors

These are the **standard 10 Sinclair BASIC error codes**. They apply to every Sinclair and Amstrad model (16K, 48K, 128K, +2 grey, +2A, +3) and are byte-for-byte identical across the ROMs (though some are unreachable in 48K mode without specific commands).

| Code | Letter | Message | Cause |
|---|---|---|---|
| 0 | **R** | `0 NEXT without FOR, xx/yy` | `NEXT` encountered without a matching `FOR` on the call stack. Also: variable name in `NEXT` does not match the one in `FOR`. |
| 1 | **C** | `1 Control variable doesn't exist, xx/yy` | `FOR` loop variable not in scope, or the loop was exited early and the runtime can no longer find it. |
| 2 | **N** | `2 No program to run, xx/yy` | `RUN` or `GO SUB` called from an empty program (no lines in memory). |
| 3 | **B** | `3 End of file, xx/yy` | `INPUT`/`READ`/`INKEY$`/`LOAD` reached end of available data; or `EOF` on a stream. |
| 4 | **A** | `4 Bad parameter, xx/yy` | Function argument out of range: e.g. `SQR(-1)`, `LN(0)`, `CHR$(256)`, `POKE addr,value` with `addr > #FFFF`. |
| 5 | **O** | `5 Out of memory, xx/yy` | RAM exhausted — program too large, variable area overflowed into stack, recursion too deep, or `DIM` array exceeds available RAM. |
| 6 | **F** | `6 Number too big, xx/yy` | Floating-point overflow: a calculation produced a result with magnitude > ~`1.7E38`. |
| 7 | **K** | `7 BREAK — CONT repeats, xx/yy` | `BREAK` (CAPS SHIFT + SPACE) pressed during program execution or `STOP` statement. `CONT` resumes from the next line. |
| 8 | **K** | `8 BREAK into program, xx/yy` | `BREAK` pressed *during* a `RUN`ning program (different from code 7 — `CONT` resumes at the same line, not the next one). |
| 9 | **K** | `9 STOP statement, xx/yy` | `STOP` statement executed (deliberate pause for inspection). |

The `xx/yy` suffix is the line:statement at which the error occurred (`xx` = line number, `yy` = statement number within that line, 0-indexed). The error message format is consistent across all Sinclair and Amstrad ROMs.

### Sub-codes and Variants

- Code **K** (codes 7, 8, 9) is overloaded — the same letter covers three different "interactive" errors. The actual code byte in `ERR_NR` differs (`#F9`, `#F8`, `#F7`) but the displayed letter is always **K**.
- Some sources call these "keyboard" errors because they relate to the user pressing keys; the message "BREAK" confirms this.
- **Code 0 (R)** is reported when `NEXT` is executed outside its `FOR`. The most common cause is `GO TO` jumping into the middle of a loop body — the FOR-frame is no longer on the calculator stack.

---

## +3 DOS Errors (Codes 20+)

The +2A/+3 add floppy disk support via the +3 DOS ROM. The DOS extends the error table with codes starting at 20:

| Code | Message | Cause |
|---|---|---|
| 20 | `Invalid device` | Stream name (e.g. `"d:data"` with bad drive letter) |
| 21 | `File not found` | `LOAD`, `OPEN`, `CAT "file"` etc. with a non-existent file |
| 22 | File exists | `SAVE` to a filename already on the disk |
| 23 | `Disk full` | No free blocks on the disk |
| 24 | `Disk is write-protected` | Write attempted to a disk with the write-protect tab closed |
| 25 | `Bad disk` | Sector CRC error, drive not ready, etc. |
| 26 | `Disk error` | Generic I/O error — usually drive door open or no disk |
| 27 | `Wrong disk` | The disk in the drive does not match the one DOS expects |
| 28 | `Path not found` | Subdirectory does not exist (only on CP/M disks) |
| 29 | `Read-only` | `SAVE`/`ERASE` attempted on a read-only file |
| 30 | `No room` | Disk directory is full (max 64 entries per disk) |
| 31 | `Disk not ready` | Drive door open or no disk inserted |

Plus 3 DOS integrates with BASIC via `ERROR #k,n` (raise code `n`) and the `GO SUB`-based `ON ERROR` extension.

---

## TR-DOS Errors (Russian Clones)

The TR-DOS ROM by Mikhail Shumakov runs on the Beta 128 disk interface used in the Pentagon, Scorpion, and other clones. TR-DOS uses its own error reporting separate from BASIC, with codes typically displayed in the form `TR-DOS Error: n`.

| Code | Message (Russian) | English translation | Cause |
|---|---|---|---|
| 0 | `OK` | OK | Success — no error |
| 1 | `Oshibka zapisi` | Write error | Disk write failed |
| 2 | `Oshibka chteniya` | Read error | Disk read failed |
| 3 | `Net diska` | No disk | Drive door open, no disk, or drive not responding |
| 4 | `Disk zashchishchyen` | Disk write-protected | Write attempted to a protected disk |
| 5 | `Net fayla` | File not found | File does not exist on disk |
| 6 | `Disk polon` | Disk full | No free blocks |
| 7 | `Oshibka ustroystva` | Device error | Hardware fault — drive, FDC, cable |
| 8 | `Failovaya sistema razrushena` | File system corrupted | TR-DOS catalog damaged |
| 9 | `Oshibka diskety` | Disk error | Generic disk I/O failure |
| 10 | `Nomer dorozhki` | Track number error | Disk geometry mismatch |
| 16 | `Oshibka pri zapisi fayla` | File write error | Specific write failure during `SAVE` |
| 17 | `Disk ne otsortirovan` | Disk not sorted | Catalog sort pending |

TR-DOS prints the Russian text directly to the screen — it does **not** go through BASIC's error handler. Assembly programs intercept by reading the TR-DOS status byte at a fixed RAM location (varies by ROM version).

For the TR-DOS interface, see [trdos.md](../04_operating_systems/trdos.md) and [trdos_programming.md](../05_development/08_dos_tape/trdos_programming.md).

---

## ESXDOS Errors

ESXDOS (the SD-card DOS used by DivMMC and the original ESX interface) uses its own numeric codes:

| Code | Constant | Meaning |
|---|---|---|
| 1 | `EOK` (also written 0 in some APIs) | Success — no error |
| 1 | `EINVAL` | Invalid parameter |
| 2 | `ENOENT` | No such file or directory |
| 3 | `EIO` | I/O error |
| 4 | `ENOSPC` | No space left on device |
| 5 | `EROFS` | Read-only filesystem |
| 6 | `ENOTDIR` | Not a directory |
| 7 | `EEXIST` | File already exists |
| 8 | `ENOTEMPTY` | Directory not empty |
| 9 | `EBUSY` | Device busy |
| 16 | `ETIMEOUT` | Timeout |
| 17 | `ENOMEDIUM` | No medium (SD card not present) |
| 18 | `ECRC` | CRC error |
| 19 | `EBADIMAGE` | Bad disk image |

ESXDOS follows the POSIX convention more closely than the older DOSes. See [esxdos.md](../04_operating_systems/esxdos.md) and [esxdos_programming.md](../05_development/08_dos_tape/esxdos_programming.md).

---

## IS-DOS Errors

IS-DOS (Romanenco's DOS for the Scorpion and other clones, with CP/M-like features) uses yet another error scheme, mostly text-based:

| Code | Message | Cause |
|---|---|---|
| `#00` | `OK` | Success |
| `#01` | `Bad command` | Unknown command or argument |
| `#02` | `File not found` | File does not exist |
| `#03` | `Disk error` | Generic I/O error |
| `#04` | `Disk full` | No space |
| `#05` | `Bad file` | File format invalid or file corrupted |
| `#06` | `Read only` | Write attempted to a read-only file |
| `#07` | `No disk` | No disk in drive |

IS-DOS's `ERROR` system variable is in its system area at `#5D00+` — exact location varies by version.

---

## NextZXOS Errors

The ZX Spectrum Next's NextZXOS extends ESXDOS and adds Next-specific errors:

| Code | Message | Cause |
|---|---|---|
| 0 | `OK` | Success |
| 1 | `Bad command` | Syntax error in command |
| 2 | `File not found` | File missing |
| 3 | `Bad disk` | Disk I/O error |
| 4 | `Disk full` | No space |
| 5 | `Bad mode` | Display / hardware mode not supported |
| 6 | `Bad type` | File type wrong (e.g. tried to LOAD a `.TAP` as `.SCR`) |
| 7 | `Bad name` | Invalid filename (illegal characters, length, etc.) |
| 8 | `Bad RAM` | Memory test failed |
| 9 | `DivMMC busy` | DivMMC interface in use by another process |
| 16 | `Layer 2 busy` | Layer 2 in use |
| 17 | `Sprite busy` | Sprites being accessed by hardware |
| 18 | `Tilemap busy` | Tilemap being accessed |

See [nextzxos.md](../04_operating_systems/nextzxos.md) and [nextzxos_programming.md](../05_development/08_dos_tape/nextzxos_programming.md).

---

## System Variables for Error Handling

| Address | Name | Purpose |
|---|---|---|
| `#5C3A` | `ERR_NR` | Current error code, stored negated (0 = no error, `#F7` = code 9 etc.) |
| `#5C3D` | `FLAGS` | General flags — bit 5 set on error |
| `#5C3F` | `ERR_SP` | Pointer to error-handler stack — `RST #08` returns here |
| `#5C8B` | `NEWPPC` | Line to jump to after error (set by `ON ERROR GO TO`) |
| `#5C8D` | `NSPPC` | Statement number after error |
| `#5C4D` | `NXTLIN` | Next line to execute — current line on error |

Assembly programs typically read `ERR_NR` to detect errors, or replace `ERR_SP` with the address of their own error handler before calling ROM routines that may fail.

---

## Handling Errors in BASIC

Sinclair BASIC does **not** have an `ON ERROR` statement — that came later in some clone ROMs. Error handling is done via:

### Method 1: Pre-Check Arguments

The most common pattern is to validate input before doing the operation:

```basic
10 INPUT "Value? "; V
20 IF V < 0 THEN PRINT "Must be positive": GO TO 10
30 PRINT "Square root is "; SQR(V)
```

### Method 2: `IF` after the Call

Test for the error condition immediately after the call:

```basic
10 INPUT "Filename? ": LINE F$
20 LOAD F$
30 REM If we get here, LOAD succeeded
```

If `LOAD` fails, the program exits to the editor with code 2 (N).

### Method 3: Patch `ERR_SP` (Assembly)

For machine-code programs, install an error handler:

```z80
        ; Set up error handler
        LD   HL,ERR_HANDLER
        LD   (#5C3F),HL         ; ERR_SP
        ; ... do risky operation ...
        RET

ERR_HANDLER:
        ; On entry, ERR_NR holds the code (negated)
        LD   A,(#5C3A)          ; Get ERR_NR
        INC  A                  ; Negate it back
        ; A now holds the actual error code
        CP   2                  ; Is it "No program"?
        JR   Z,NO_PROGRAM
        CP   3                  ; Is it "End of file"?
        JR  Z,EOF
        ; ... etc ...
```

### Method 4: `ON ERROR` (Clone ROMs)

Some clone ROMs (e.g., ATM Turbo, Sprinter) add an `ON ERROR GO TO line` extension that emulates other BASIC dialects. This is **not portable** across models — only clones that document the extension support it.

---

## Common Error Scenarios and Fixes

### "Out of memory" (Code O / 5)

The most common error. Causes and fixes:

| Cause | Fix |
|---|---|
| BASIC program too long | Split into modules loaded separately; use machine code for tight loops |
| `DIM` array too big | Reduce array size, or move to paged RAM (128K only) |
| Recursion too deep | Convert to iteration; reduce stack depth |
| Variables overflow into stack | `CLEAR addr` to give variables more space; delete unused variables |
| Machine code overrunning BASIC | `CLEAR addr` to set RAMTOP lower |

### "Bad parameter" (Code A / 4)

| Common trigger | Range |
|---|---|
| `POKE addr,v` | `addr` 0–65535, `v` 0–255 |
| `PEEK(addr)` | `addr` 0–65535 |
| `CHR$(n)` | `n` 0–255 |
| `STR$(n)` | always valid |
| `CODE(s)` | always valid |
| `SIN/COS/TAN` | valid for any number — but value > 2^32 raises code F |
| `LN(x)` | `x > 0` |
| `SQR(x)` | `x >= 0` |
| `SGN(x)` | always valid |
| `PEEK(addr)` | `addr` 0–65535 |
| `POKE` to ROM range | No error — but writes lost |
| `BORDER c` | `c` 0–7 |
| `INK c`/`PAPER c` | `c` 0–9 (0–7 = colors, 8 = transparent, 9 = contrast) |
| `PLOT x,y` | `x` 0–255, `y` 0–175 |
| `DRAW x,y` | `x,y` valid: -65535 to 65535 |
| `PLAY string` (128K) | string must match the PLAY syntax |

### "BREAK" (Code K / 7, 8, 9)

User-interrupt errors are *expected* — they are how the user stops a running program. Codes 7 and 8 are caused by the user pressing BREAK (CAPS SHIFT + SPACE); code 9 is the `STOP` statement.

| Code | When to `CONT` |
|---|---|
| 7 (NEXT) | Yes — `CONT` resumes from the next line |
| 8 (INTO) | Yes — `CONT` resumes from the *same* line (re-executes it) |
| 9 (STOP) | Yes — `CONT` resumes from the next line |

If your program enters an infinite loop without `INPUT`/`PAUSE`, the only way out is `BREAK` — the user expects this. Always document any "press BREAK to exit" behavior in your program's help.

---

## Assembly Quick-Reference: Detecting Error After ROM Calls

After calling any ROM routine that can fail (tape routines, `BEEP`, `PRINT` with bad attribute, etc.):

```z80
        CALL    #20CC           ; SAVE routine
        LD      A,(#5C3A)       ; ERR_NR
        INC     A               ; Negate: 0 means no error
        JR      NZ,SAVE_ERROR
        ; ... save succeeded ...
```

For the inverse — raising an error from machine code:

```z80
        LD      A,#0F7          ; Code 9 (STOP), negated = #F7
        LD      (#5C3A),A       ; Set ERR_NR
        RST     #08             ; Trigger error handler
        ; RST #08 does not return; it goes through ERR_SP
```

---

## Cross-References

- [basic_token_table.md](basic_token_table.md) — token encoding for keywords like `STOP`, `CONT`, `ON ERROR`
- [rom_routines.md](rom_routines.md) — `RST #08` error entry point and related routines
- [memory_maps.md](memory_maps.md) — system variable addresses
- [system_variables.md](../04_operating_systems/system_variables.md) — system variable addresses including `ERR_NR` and `ERR_SP`
- [trdos.md](../04_operating_systems/trdos.md) — TR-DOS internals
- [plus3dos.md](../04_operating_systems/plus3dos.md) — +3 DOS internals
- [esxdos.md](../04_operating_systems/esxdos.md) — ESXDOS internals
- [nextzxos.md](../04_operating_systems/nextzxos.md) — NextZXOS internals

---

## References

- Steven Vickers — *ZX Spectrum BASIC Programming*, Sinclair Research, 1982 — original list of 10 Sinclair BASIC error codes
- Ian Logan, Frank O'Hara — *The Complete Spectrum ROM Disassembly*, Melbourne House, 1983 — error reporting mechanism with disassembly
- Amstrad — *ZX Spectrum +3 DOS Manual*, 1987 — +3 DOS error table
- Mikhail Shumakov — *TR-DOS User Manual*, original Russian documentation
- ESXDOS Documentation, Espter Software, [community-maintained mirror](https://github.com/z-esxdos/esxdos-manual)
- NextZXOS Manual, ZX Spectrum Next team, [gitlab mirror](https://gitlab.com/thesmog358/tbblue/-/tree/master/docs/nextos)
