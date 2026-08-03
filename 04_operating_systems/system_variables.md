[← Home](../README.md) · [Operating Systems](README.md)

# System Variables — ROM Workspace Reference

The ZX Spectrum's ROM defines a fixed area of RAM starting at `#5C00` as its workspace: interpreter flags, I/O buffers, channel pointers, and the frame counter. These variables are the **ROM's API surface** — the contract between the ROM operating system and machine code programs. Understanding them is essential for any assembly program that interacts with the ROM, hooks interrupts, or reads system state.

This article provides a complete reference for the 48K ROM system variables, plus notes on 128K ROM extensions.

---

## Memory Layout

```
#5C00 - #5CB5    System variables (182 bytes, fixed by ROM)
#5CB6 - #5CCF    Channel information (variable, depends on open channels)
                   Stream data follows (16 streams × 2 bytes)
```

The system variables area is in **contended memory** on all models. Access during the paper display area is subject to contention delays.

---

## Complete 48K ROM System Variables

The ROM accesses all system variables through the IY register (`IY = #5C3A`, so `IY+0 = ERR_NR`, etc.). This is why the ROM pushes `IY` on entry and pops it on exit — any assembly code that uses IY for other purposes must save and restore it around ROM calls.

| Address | IY Offset | Name | Size | Description |
|---------|-----------|------|------|-------------|
| `#5C00` | IY-58 | `KSTATE` | 8 | Keyboard debounce buffer: bytes 0-3 = main key buffer, bytes 4-7 = extended key buffer |
| `#5C08` | IY-50 | `LAST_K` | 1 | Last key pressed (key code). Reset to `#FF` after reading by the ROM |
| `#5C09` | IY-49 | `REPDEL` | 1 | Delay before auto-repeat starts (in frames, default 35) |
| `#5C0A` | IY-48 | `REPPER` | 1 | Auto-repeat period (in frames between repeats, default 5) |
| `#5C0B` | IY-47 | `DEFADD` | 2 | Address of arguments of user-defined function, or `#0000` |
| `#5C0D` | IY-45 | `K_DATA` | 1 | 2nd byte of color controls entered from keyboard |
| `#5C0E` | IY-44 | `TVDATA` | 2 | Bytes of color, AT and TAB controls going to TV |
| `#5C10` | IY-42 | `STRMS` | 30 | Stream data: 15 streams × 2 bytes. Stream 0 = keyboard, 1 = screen, 2 = printer |
| `#5C36` | IY-4 | `CHARS` | 2 | Address minus 256 of the character set (96 chars × 8 bytes = 768 bytes). Default: `#3C00` (= `#3D00 − #0100`, pointing to ROM character set at `#3D00`–`#3FFF`). See [character_set.md](../10_references/character_set.md) for details. |
| `#5C38` | IY-2 | `RASP` | 1 | Length of warning buzz |
| `#5C39` | IY-1 | `PIP` | 1 | Length of keyboard click |
| `#5C3A` | IY+0 | `ERR_NR` | 1 | One less than error report number. `#FF` = no error. `#00` = error 1 ("NEXT without FOR") |
| `#5C3B` | IY+1 | `FLAGS` | 1 | System flags (see bit-level table below) |
| `#5C3C` | IY+2 | `TVFLAG` | 1 | TV flags (see bit-level table below) |
| `#5C3D` | IY+3 | `ERR_SP` | 2 | Machine stack pointer for error recovery |
| `#5C3F` | IY+5 | `LIST_SP` | 2 | Return address for LIST command continuation |
| `#5C41` | IY+7 | `MODE` | 1 | Cursor mode: 'K' (keyword), 'L' (lowercase), 'E' (extended), 'G' (graphics) |
| `#5C42` | IY+8 | `NEWPPC` | 2 | Line number for `GO TO` / `GO SUB` |
| `#5C44` | IY+10 | `NSPPC` | 1 | Statement number within line for continuation |
| `#5C45` | IY+11 | `PPC` | 2 | Line number of statement currently being executed |
| `#5C47` | IY+13 | `SUBPPC` | 1 | Statement number within line currently being executed |
| `#5C48` | IY+14 | `BORDCR` | 1 | Border color × 8; also lower screen attributes |
| `#5C49` | IY+15 | `E_PPC` | 2 | Number of current line (with program cursor) |
| `#5C4B` | IY+17 | `VARS` | 2 | Address of the start of the variables area (grows upward) |
| `#5C4D` | IY+19 | `DEST` | 2 | Destination address for `GO TO`/`GO SUB` line lookup |
| `#5C4F` | IY+21 | `CHANS` | 2 | Address of channel information area |
| `#5C51` | IY+23 | `CURCHL` | 2 | Address of channel currently being used for I/O |
| `#5C53` | IY+25 | `PROG` | 2 | Address of the start of the BASIC program (first line) |
| `#5C55` | IY+27 | `NXTLIN` | 2 | Address of the next BASIC line to execute |
| `#5C57` | IY+29 | `DATADD` | 2 | Address of current DATA item (for `READ`/`RESTORE`) |
| `#5C59` | IY+31 | `E_LINE` | 2 | Address of the edit line (command being typed) |
| `#5C5B` | IY+33 | `K_CUR` | 2 | Address of the cursor position in the edit line |
| `#5C5D` | IY+35 | `CH_ADD` | 2 | Address of next character to interpret (syntax analyzer pointer) |
| `#5C5F` | IY+37 | `X_PTR` | 2 | Address of the syntax error marker (or `#0000`) |
| `#5C61` | IY+39 | `WORKSP` | 2 | Address of the start of workspace (input buffer area) |
| `#5C63` | IY+41 | `STKBOT` | 2 | Address of the bottom of the calculator stack |
| `#5C65` | IY+43 | `STKEND` | 2 | Address of the end of the calculator stack |
| `#5C67` | IY+45 | `BREG` | 1 | Calculator's B register (saved during floating-point operations) |
| `#5C68` | IY+46 | `MEM` | 2 | Base address of calculator's memory area (usually `MEMBOT`) |
| `#5C6A` | IY+48 | `FLAGS2` | 1 | More system flags (see bit-level table below) |
| `#5C6B` | IY+49 | `DFSZ` | 1 | Number of lines in lower part of screen |
| `#5C6C` | IY+50 | `S_TOP` | 2 | Top program line number in automatic listings |
| `#5C6E` | IY+52 | `OLDPPC` | 2 | Line number to which `CONTINUE` jumps |
| `#5C70` | IY+54 | `OSPPC` | 1 | Statement number within line for `CONTINUE` |
| `#5C71` | IY+55 | `FLAGX` | 1 | Input/assignment flags |
| `#5C72` | IY+56 | `STRLEN` | 2 | Length of string-type destination in assignment |
| `#5C74` | IY+58 | `T_ADDR` | 2 | Address of next item in syntax table; file ops: 0=SAVE, 1=LOAD, 2=VERIFY, 3=MERGE |
| `#5C76` | IY+60 | `SEED` | 2 | Seed for `RND`. Set by `RANDOMIZE` |
| `#5C78` | IY+62 | `FRAMES` | 3 | **Frame counter**: 3-byte counter incremented every 20ms interrupt. LSB first. Wraps after ~4.6 days. **Not zeroed by `NEW`** |
| `#5C7B` | IY+65 | `UDG` | 2 | Address of the first user-defined graphic character. Default: `#FF58` on 48K |
| `#5C7D` | IY+67 | `COORDS` | 2 | Current graphics coordinates: X in low byte, Y in high byte (for `PLOT`/`DRAW`) |
| `#5C7F` | IY+69 | `P_POSN` | 1 | 33-column number of printer position |
| `#5C80` | IY+70 | `PR_CC` | 2 | Full address of next LPRINT position (ZX printer buffer `#5B00`–`#5B1F`) |
| `#5C82` | IY+72 | `ECHO_E` | 2 | 33-column and 24-line number (lower half, end of input buffer) |
| `#5C84` | IY+74 | `DFCC` | 2 | Address in display file of PRINT position |
| `#5C86` | IY+76 | `DFCCL` | 2 | Like `DFCC` but for lower part of screen |
| `#5C88` | IY+78 | `S_POSN` | 2 | PRINT position: column in low byte, line in high byte |
| `#5C8A` | IY+80 | `SPOSNL` | 2 | Like `S_POSN` but for lower part of screen |
| `#5C8C` | IY+82 | `SCRCT` | 1 | Scroll counter before "scroll?" prompt. POKE >1 to disable |
| `#5C8D` | IY+83 | `ATTR_P` | 1 | Permanent attribute: used by `PRINT`, `PLOT`, `DRAW` |
| `#5C8E` | IY+84 | `MASK_P` | 1 | Permanent transparency mask |
| `#5C8F` | IY+85 | `ATTR_T` | 1 | Temporary attribute: current INK/PAPER/BRIGHT/FLASH for printing |
| `#5C90` | IY+86 | `MASK_T` | 1 | Temporary transparency mask |
| `#5C91` | IY+87 | `PFLAG` | 1 | Print flags: bit 7=Paper9Perm, 6=Paper9Curr, 5=Ink9Perm, 4=Ink9Curr, 3=InvPerm, 2=InvCurr, 1=OverPerm, 0=OverCurr |
| `#5C92` | IY+88 | `MEMBOT` | 30 | Calculator's memory area: 6 × 5-byte floating-point numbers |
| `#5CB0` | IY+118 | `NMIADD` | 2 | User's NMI service routine address. Write `#0000` to disable custom NMI |
| `#5CB2` | IY+120 | `RAMTOP` | 2 | Address of the last byte of the BASIC system area. `CLEAR` sets this. Default `#FF57` on 48K |
| `#5CB4` | IY+122 | `P_RAMT` | 2 | Address of the last byte of physical RAM. `#FFFF` on 48K, `#7FFF` on 16K |

---

## Flag Register Bit-Level Reference

### FLAGS (`#5C3B`, IY+1)

| Bit | Name | Meaning when set (1) |
|-----|------|---------------------|
| 7 | — | (unused) |
| 6 | Str/Num | 1 = string result, 0 = numeric result |
| 5 | NewKey | New key pressed |
| 4 | 128KMode | Running in 128K mode |
| 3 | K/L In | Keyboard input mode |
| 2 | K/L Prn | Printer output mode |
| 1 | PrnTxt/Raw | 1 = printer text mode, 0 = raw |
| 0 | LeadSpace | Leading space required |

### FLAGS2 (`#5C6A`, IY+48)

| Bit | Name | Meaning when set (1) |
|-----|------|---------------------|
| 7 | DefTokIgnoreCase | Token definition ignore case |
| 6 | DefTokNoAbbrev | No abbreviation in token definition |
| 5 | DefTokSep | Token separator |
| 4 | OutChanK | Output channel is 'K' |
| 3 | CapsLock | Caps lock active |
| 2 | ParseInQuote | Parser is inside quoted string |
| 1 | PrnBufNotEmpty | Printer buffer has data |
| 0 | ScreenClear | Screen has been cleared |

### TVFLAG (`#5C3C`, IY+2)

| Bit | Name | Meaning when set (1) |
|-----|------|---------------------|
| 7 | — | (unused) |
| 6 | — | (unused) |
| 5 | ClrLwKey | Clear lower key |
| 4 | AutoList | Automatic listing mode |
| 3 | ModeChg | Mode has changed |
| 2 | — | (unused) |
| 1 | — | (unused) |
| 0 | — | (unused) |

---

## Common Use Patterns

### Reading the Frame Counter

The 3-byte `FRAMES` counter at `#5C78` is the most reliable timing source:

```z80
; Read the full 24-bit frame counter
ReadFrames:
    LD   A,R            ; Disable interrupts briefly for atomic read
    DI
    LD   HL,(#5C78)     ; Low 16 bits
    LD   A,(#5C7A)      ; High byte
    EI
    RET
```

> [!WARNING]
> The ROM interrupt handler increments `FRAMES` non-atomically (it's 3 bytes). If you read it with interrupts enabled, you may catch it mid-increment. Use `DI`/`EI` around reads for a consistent snapshot.

### Waiting for a Specific Number of Frames

```z80
; Wait for N frames (N in B)
WaitFrames:
    PUSH BC
    HALT               ; Wait for next frame interrupt
    POP  BC
    DJNZ WaitFrames
    RET
```

### Getting the BASIC Program Area

```z80
; Find the start and end of the BASIC program
    LD   HL,(#5C53)    ; PROG = start of BASIC program
    ; HL now points to the first line's line number (2 bytes)
    ; followed by line length (2 bytes), then line data

    LD   DE,(#5C4B)    ; VARS = start of variables area
    ; BASIC program ends just before VARS
    ; Program length = VARS - PROG
```

### Setting Custom Font

```z80
; Point to a custom character set at #8000
; Each character is 8 bytes, 96 characters = 768 bytes
SetFont:
    LD   HL,#8000 - 256   ; CHARS stores address minus 256
    LD   (#5C36),HL        ; Update CHARS
    RET
```

### Checking for Key Press (ROM Method)

```z80
; Check if a key was pressed since last check
CheckKey:
    LD   A,(#5C08)         ; LAST_K
    CP   #FF               ; #FF = no key
    JR   Z,.no_key
    LD   (#5C08),#FF       ; Reset LAST_K to mark as read
    ; A = key code of the pressed key
    RET
.no_key:
    ; No key pressed
    RET
```

---

## 128K ROM Extensions

The 128K ROMs (ROM 0 and ROM 3) use the same `#5C00`–`#5CB4` system variables, but add a dedicated workspace area at `#5B00`–`#5BFF` for ROM paging, RS232 I/O, renumber, and disk interface state.

### 128K Workspace (`#5B00`–`#5BFF`)

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5B00` | `SWAP` | 16 | Paging subroutine (ROM switch routine entry) |
| `#5B10` | `STOO` | 17 | Paging subroutine (entered with interrupts disabled, AF/BC on stack) |
| `#5B21` | `YOUNGER` | 9 | Paging subroutine (ROM switch) |
| `#5B2A` | `REGNUOY` | 16 | Paging subroutine (ROM switch) |
| `#5B3A` | `ONERR` | 24 | Paging subroutine (error handler) |
| `#5B52` | `OLDHL` | 2 | Temporary HL store while switching ROMs |
| `#5B54` | `OLDBC` | 2 | Temporary BC store while switching ROMs |
| `#5B56` | `OLDAF` | 2 | Temporary AF store while switching ROMs |
| `#5B58` | `TARGET` | 2 | Subroutine address in ROM 3 |
| `#5B5A` | `RETADDR` | 2 | Return address in ROM 1 |
| `#5B5C` | `BANK_M` | 1 | **Copy of port `#7FFD`** — RAM paging, ROM switch, screen selection. Must be kept up to date if interrupts are enabled |
| `#5B5D` | `RAMRST` | 1 | `RST 8` instruction byte (used by ROM 1 to report errors to ROM 3) |
| `#5B5E` | `RAMERR` | 1 | Error number passed from ROM 1 to ROM 3. Also used as temp drive store during SAVE/LOAD |
| `#5B5F` | `BAUD` | 2 | RS232 bit period in T-states/26. Set by `FORMAT LINE` |
| `#5B61` | `SERFL` | 2 | Second-character-received flag and data |
| `#5B63` | `COL` | 1 | Current column (1 to width) |
| `#5B64` | `WIDTH` | 1 | Paper column width. Default 80 |
| `#5B65` | `TVPARS` | 1 | Number of inline parameters expected by RS232 |
| `#5B66` | `FLAGS3` | 1 | Flags: bit 2=expand tokens, bit 3=RS232 print, bit 4=disk interface present, bit 5=drive B: present |
| `#5B67` | `BANK678` | 1 | **Copy of port `#1FFD`** — +2A/+3 RAM/ROM switching, disk motor, Centronics strobe. Must be kept up to date |
| `#5B68` | `XLOC` | 1 | X location for `COPY` command |
| `#5B69` | `YLOC` | 1 | Y location for `COPY` command |
| `#5B6A` | `OLDSP` | 2 | Old stack pointer when `TSTACK` is in use |
| `#5B6C` | `SYNRET` | 2 | Return address for `ONERR` |
| `#5B6E` | `LASTV` | 5 | Last value printed by calculator |
| `#5B73` | `RCLINE` | 2 | Current line being renumbered |
| `#5B75` | `RCSTART` | 2 | Starting line number for renumbering. Default 10 |
| `#5B77` | `RCSTEP` | 2 | Increment value for renumbering. Default 10 |
| `#5B79` | `LODDRV` | 1 | `'T'` if LOAD/VERIFY/MERGE from tape, else `'A'`, `'B'`, `'M'` |
| `#5B7A` | `SAVDRV` | 1 | `'T'` if SAVE to tape, else `'A'`, `'B'`, `'M'` |
| `#5B7B` | `DUMPLF` | 1 | Line feed in 1/216ths for `COPY EXP`. Default 9. POKE with 8 for smaller dump |
| `#5B7C` | `STRIP1` | 8 | Stripe one bitmap (for `COPY`) |
| `#5B84` | `STRIP2` | 8 | Stripe two bitmap (for `COPY`) |
| `#5BFF` | `TSTACK` | 115 | Temporary stack (grows downward). Used when RAM page 7 is paged in |

### 128K Standard Variables

The 128K also adds a few variables adjacent to the 48K set:

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5CC5` | `BANK_M` | 1 | Backup of the last value written to port `#7FFD` (128K paging register) |
| `#5CC6` | `RAMRST` | 1 | Reset flag for RAM disk |
| `#5CC7` | `RAMERR` | 1 | RAM disk error status |
| Additional 128K variables | | | RAM disk parameters, bank allocation flags |

> [!NOTE]
> The 128K ROM also uses banks 4 and 6 for workspace (RAM disk cache, editor buffers). These are not mapped into the system variables area — they are accessed by paging the banks in as needed.

---

## Memory Allocation Map (from ROM's perspective)

| Address | Region | Direction | Notes |
|---------|--------|-----------|-------|
| `#5C00` | System variables | Fixed | 182 bytes, IY-relative addressed |
| `#5CB6` | Channel definitions | ↓ grows | Stream data follows (30 bytes for 15 streams) |
| `#5D00` | BASIC program area | ↓ grows | Grows upward with LIST |
| | BASIC variables area | ↓ grows | Grows upward |
| | Free RAM | | Available to machine code |
| `#FF58` | User-defined graphics (UDG) | ↑ grows | Grows downward from RAMTOP |
| RAMTOP | Top of BASIC system area | | Set by CLEAR command |
| `#FFFF` | End of physical RAM | | 48K machines |

### Key Pointers for Navigation

| From | To | Purpose |
|------|----|---------|
| `PROG` (`#5C53`) | `VARS` (`#5C4B`) | BASIC program text |
| `VARS` (`#5C4B`) | `E_LINE` (`#5C59`) | BASIC variables |
| `E_LINE` (`#5C59`) | `WORKSP` | Edit line buffer |
| `WORKSP` | `STKBOT` | Workspace |
| `STKEND` | `UDG` (`#5C7B`) | Free RAM (calc stack to UDG) |

---

## Interface 1 Variables (`#5CB6`–`#5CEF`)

When Sinclair Interface 1 is connected, the area from `#5CB6` to `#5CEF` is used for Microdrive, RS232, and network state. **When Interface 1 is NOT present**, this area is the standard CHANS data (K, S, R, P channel definitions).

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5CB6` | `FLAGS3` | 1 | Flags: bit 7=VERIFY, 6=MERGE, 5=SAVE, 4=LOAD/MOVE, 3=NetUse, 2=MainROMError, 1=CLEAR#/ShadowEntry, 0=NewCmd |
| `#5CB7` | `VECTOR` | 2 | Command extension vector. Normally points to `#01F0` (`ERR_6`) |
| `#5CB9` | `SBRT` | 10 | ROM paging routine workspace |
| `#5CC3` | `BAUD` | 2 | RS232 timing constant: `(3500000 / (26 × baudrate)) - 2` |
| `#5CC5` | `NTSTAT` | 1 | Network station number |
| `#5CC6` | `IOBORD` | 1 | Border color during I/O. Default 0 (black) |
| `#5CC7` | `SER_FL` | 1 | Number of buffered serial characters (0 or 1) |
| `#5CC8` | `SER_BF` | 1 | One-byte serial input buffer |
| `#5CC9` | `SECTOR` | 2 | Counter of sectors examined during Microdrive ops |
| `#5CCB` | `CHADD_` | 2 | Temporary store for `CH_ADD` |
| `#5CCD` | `NTRESP` | 1 | Network response code + 1 |
| `#5CCE` | `NTDEST` | 1 | Destination station for current packet |
| `#5CCF` | `NTSRCE` | 1 | Station number of sending machine |
| `#5CD0` | `NTNUMB` | 2 | Current packet block number |
| `#5CD2` | `NTTYPE` | 1 | Packet type: 0=normal, 1=EOF |
| `#5CD3` | `NTLEN` | 1 | Length of data block (1–255) |
| `#5CD4` | `NTDCS` | 1 | Current data block checksum |
| `#5CD5` | `NTCHS` | 1 | Current header block checksum |

### File Specifiers

Interface 1 uses two 8-byte file specifier blocks:

| Address | Name | Description |
|---------|------|-------------|
| `#5CD6`–`#5CDD` | File specifier 1 | Drive (2), stream (1), device 'M'/'N'/'T'/'B' (1), filename length (2), filename start |
| `#5CDE`–`#5CE5` | File specifier 2 | Same format, used by LOAD and MOVE |

### File Header Workspace

| Address | Name | Description |
|---------|------|-------------|
| `#5CE6` | `HD_00` | File type |
| `#5CE7` | `HD_0B` | Data block length (2 bytes) |
| `#5CE9` | `HD_0D` | Data block start address (2 bytes) |
| `#5CEB` | `HD_0F` | Program length without variables, or array name (2 bytes) |
| `#5CED` | `HD_11` | Autostart line number / execute address (2 bytes) |
| `#5CEF` | `COPIES` | Number of copies for SAVE. Reset to 1 after SAVE |

> [!NOTE]
> When Interface 1 is active, CHANS starts at `#5CF0` instead of `#5CB6`. This shifts the entire channel data area upward by 58 bytes, reducing available BASIC RAM.

---

## TR-DOS Variables (`#5C96`–`#5CE3`)

TR-DOS (Technology Research DOS) is the disk operating system used by the Beta 128 Disk Interface. When activated, it occupies 112 bytes of RAM from `#5C96` (`23734`) to `#5CE3` for its own workspace, reducing BASIC program area. The entry points are at `#5CC6` (BASIC extension), `#5CF4` (hook code), and `#3D13` (machine code call).

### Drive Configuration

| Address | Size | Description |
|---------|------|-------------|
| `#5C96` | 1 | Interface 1 detection flag. `#F4` = sysvars not moved, `#00` = check `#5C98` |
| `#5CA2` | 1 | Drive A mode: bit 7 = 80-track, bit 6 = double-sided |
| `#5CA3` | 1 | Drive B mode: same bit layout |
| `#5CA4` | 1 | Drive C mode: same bit layout |
| `#5CA5` | 1 | Drive D mode: same bit layout |
| `#5CB0` | 1 | Stepping rate for drive A |
| `#5CB1` | 1 | Stepping rate for drive B |
| `#5CB2` | 1 | Stepping rate for drive C |
| `#5CB3` | 1 | Stepping rate for drive D |

### File Operations

| Address | Size | Description |
|---------|------|-------------|
| `#5CA6` | 1 | Current sector number during catalog reading |
| `#5CA7` | 1 | `#80` = disk drive ready |
| `#5CA8` | 1 | `#00` = sector reading, `#FF` = sector writing |
| `#5CAD` | 8 | File name in ASCII |
| `#5CB5` | 1 | File type: `B`, `C`, `D`, `#`, etc. |
| `#5CB6` | 2 | Start address for `C` files; BASIC program size for `B` files |
| `#5CB8` | 2 | File length in bytes |
| `#5CBA` | 1 | File size in 256-byte sectors |
| `#5CBB` | 1 | First sector number of current file (0–15) |
| `#5CBC` | 1 | First track number of current file (0–160) |
| `#5CC0` | 1 | Current sector number |
| `#5CC1` | 1 | Current track number |
| `#5CC2` | 1 | Drive number for temporary operations |
| `#5CC4` | 1 | Drive number for two-file operations; `#FF` if stream open |
| `#5CC5` | 1 | Drive number for two-file ops; READ/VERIFY flag |

### System State

| Address | Size | Description |
|---------|------|-------------|
| `#5CBE` | 1 | Last FDC command code |
| `#5CBF` | 1 | Sector number for sector read/write functions |
| `#5CC6` | 1 | Command mode: `#FF` = BASIC, other = TR-DOS |
| `#5CC7` | 1 | TR-DOS error code (return value in BC). `#00` = no error |
| `#5CC8` | 1 | MSB of error code, cleared on `#3D00` call |
| `#5CC9` | 2 | Address of command line. On `#3D00` call = `E_LINE`; on `#3D03` = `CH_ADD` |
| `#5CCB` | 2 | Copy of `ERR_SP`. If MSB = `#AA`, `RUN "boot"` executes on reset |
| `#5CCD` | 1 | If `#00` then show TR-DOS screen |
| `#5CCE` | 1 | Copy of system register (555TM9 latch) |
| `#5CCF` | 1 | Default disk drive number (0–3) |
| `#5CD1` | 1 | File number from `#0A` find-file function |
| `#5CD3` | 1 | Number of 256-byte blocks for MOVE command (4K minimum) |

### TR-DOS Channel Data

TR-DOS replaces the standard CHANS area with its own channel definitions:

| Address | Size | Channel |
|---------|------|---------|
| `#5CD6` | 5 | Channel 'K' (keyboard) |
| `#5CDB` | 5 | Channel 'S' (screen) |
| `#5CE0` | 5 | Channel 'R' (RS232) — TR-DOS provides its own |
| `#5CE5` | 5 | Channel 'P' (printer) |
| `#5CEA` | — | Start of BASIC program if no files opened |

> [!WARNING]
> TR-DOS variables occupy the same address range as Interface 1 variables (`#5CB6`–`#5CEF`). These two interfaces are mutually exclusive — you cannot have both active simultaneously.

---

## Cross-References

- **48K memory map** (address ranges, contended regions): [memory_and_io_48k.md](../05_development/03_memory_and_io/memory_and_io_48k.md)
- **128K memory map** (banking, 128K extensions): [memory_and_io_128k.md](../05_development/03_memory_and_io/memory_and_io_128k.md)
- **Interrupt programming** (hooking #0038, ISR design): [interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md)
- **ROM disassembly** (complete system variable reference): [skoolkid ROM sysvars](https://skoolkid.github.io/rom/buffers/sysvars.html)
- **I/O ports** (#FE keyboard reading): [memory_and_io_48k.md](../05_development/03_memory_and_io/memory_and_io_48k.md)
