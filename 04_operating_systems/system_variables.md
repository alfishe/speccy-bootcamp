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

## Complete System Variables Table

### I/O and Keyboard

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5C00` | `KSTATE` | 8 | Keyboard state: 8 bytes for the debounce buffer. Bytes 0-3 = main key buffer, bytes 4-7 = extended key buffer |
| `#5C08` | `LAST_K` | 1 | Last key pressed (key code). Reset to `#FF` after reading by the ROM |
| `#5C09` | `REPDEL` | 1 | Delay before auto-repeat starts (in frames, default 35) |
| `#5C0A` | `REPPER` | 1 | Auto-repeat period (in frames between repeats, default 5) |
| `#5C0B` | `DEFADD` | 2 | Address of current `DEFINE` key definition, or `#0000` |
| `#5C0D` | `KDATA` | 1 | Keyboard data being built into a token |
| `#5C0E` | `TVDATA` | 2 | TV scan position data for tape loading |
| `#5C10` | `STRMS` | 30 | Stream data: 15 streams × 2 bytes each. Stream 0 = keyboard, 1 = screen, 2 = printer |

### Channel Information Pointers

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5C0F` | `CHANS` | 2 | Address of channel data area (points just after `#5CB6`) |
| `#5C4F` | `CHANS` | 2 | **Duplicate reference**: Address of channel information area |

> **Note**: `CHANS` at `#5C4F` is the canonical pointer. The ROM uses it to locate channel definitions (K, S, P, R channels).

### Display and Color

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5C28` | `ATTR_T` | 1 | Temporary attribute: current INK/PAPER/BRIGHT/FLASH for printing |
| `#5C29` | `MASK_T` | 1 | Temporary attribute mask |
| `#5C2A` | `ATTR_P` | 1 | Permanent attribute: used by `PRINT`, `PLOT`, `DRAW` |
| `#5C2B` | `MASK_P` | 1 | Permanent attribute mask |
| `#5C2C` | `TADDR` | 2 | Temporary attribute address (pointing into the attribute file) |
| `#5C2E` | `MEM` | 2 | Base address of calculator's memory area (used by `STR$`, etc.) |
| `#5C30` | `FLAGS2` | 1 | More system flags (bit 0 = caps lock, bit 6 = printer output) |
| `#5C48` | `BORDCR` | 1 | Border color (bits 1-3) combined with screen attributes |

### Error Handling

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5C3A` | `ERR_NR` | 1 | One less than error report number. `#FF` = no error. `#00` = error 1 ("NEXT without FOR"), etc. |
| `#5C3C` | `FLAGS` | 1 | System flags: bit 0 = printer output, bit 1 = syntax check mode, bit 6 = numeric result, bit 7 = syntax OK |
| `#5C3D` | `ERR_SP` | 2 | Machine stack pointer for error recovery (points to the `RST 08h` handler's return address) |
| `#5C3F` | `LIST_SP` | 2 | Return address for LIST command continuation |

### BASIC Program and Variables

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5C42` | `MODE` | 1 | Cursor mode: 'K' (keyword), 'L' (lowercase), 'E' (extended), 'G' (graphics) |
| `#5C44` | `NEWPPC` | 2 | Line number for `GO TO` / `GO SUB` |
| `#5C46` | `NSPPC` | 1 | Statement number within line for continuation |
| `#5C4B` | `VARS` | 2 | Address of the start of the variables area (grows upward) |
| `#5C4D` | `DEST` | 2 | Destination address for `GO TO`/`GO SUB` line lookup |
| `#5C53` | `PROG` | 2 | Address of the start of the BASIC program (first line) |
| `#5C55` | `NXTLIN` | 2 | Address of the next BASIC line to execute |
| `#5C57` | `DATADD` | 2 | Address of current DATA item (for `READ`/`RESTORE`) |
| `#5C59` | `E_LINE` | 2 | Address of the edit line (command being typed) |
| `#5C5B` | `K_CUR` | 2 | Address of the cursor position in the edit line |
| `#5C5D` | `CH_ADD` | 2 | Address of next character to interpret (syntax analyzer pointer) |
| `#5C5F` | `X_PTR` | 2 | Address of the syntax error marker (or `#0000`) |
| `#5C61` | `WORKSP` | 2 | Address of the start of workspace (input buffer area) |
| `#5C63` | `STKBOT` | 2 | Address of the bottom of the calculator stack |
| `#5C65` | `STKEND` | 2 | Address of the end of the calculator stack |
| `#5C67` | `BREG` | 1 | Calculator's B register (saved during floating-point operations) |
| `#5C68` | `MEMBOT` | 30 | Calculator's memory area: 6 × 5-byte floating-point numbers |
| `#5C86` | `FLAGS2` → see `#5C30` | | (overlaps, earlier entry is correct) |
| `#5C88` | `D_STR` | 2 | Drawing string end address |
| `#5C8A` | `G_COL` | 1 | Graphics color |
| `#5C8B` | `CO_ORDS` | 2 | Current graphics coordinates (x, y) for `PLOT`/`DRAW` |
| `#5C8D` | `P_POSN` | 2 | Print column/row position |
| `#5C8F` | `PR_CC` | 2 | Print cursor column (for 32-column mode) |

### Timing and Frame

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5C78` | `FRAMES` | 3 | **Frame counter**: 3-byte counter incremented every 20ms interrupt (every frame). LSB first. Wraps around after 16,777,216 frames (~4.6 days). **Not zeroed by `NEW`** — only by reset. |

### Character Set and UDG

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5C36` | `CHARS` | 2 | Address minus 256 of the character set. Default points to ROM character set at `#153C` (stored as `#15D6`, which is `#153C` + `#0100`). Change this to point to a custom font |
| `#5C7B` | `UDG` | 2 | Address of the first user-defined graphic character (UDG 'A' at codes 144-164). Default: `RAMTOP` - 168 (`#FF58` on 48K) |

### Memory Boundaries

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5CB2` | `RAMTOP` | 2 | Address of the last byte of the BASIC system area. `CLEAR` sets this. Default `#FF57` on 48K |
| `#5CB4` | `P_RAMT` | 2 | Address of the last byte of physical RAM. `#FFFF` on 48K, `#7FFF` on 16K |
| `#5CB6` | Channel info start | — | Start of the channel definitions area |

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

## 128K Extensions

The 128K uses the same `#5C00`–`#5CB5` system variables, with additional variables:

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `#5CC5` | `BANK_M` | 1 | Backup of the last value written to port `#7FFD` (128K paging register) |
| `#5CC6` | `RAMRST` | 1 | Reset flag for RAM disk |
| `#5CC7` | `RAMERR` | 1 | RAM disk error status |
| Additional 128K variables | | | RAM disk parameters, bank allocation flags |

The 128K ROM also uses banks 4 and 6 for workspace (RAM disk cache, editor buffers). These are not mapped into the system variables area — they are accessed by paging the banks in as needed.

---

## Memory Allocation Map (from ROM's perspective)

```
#5C00      System variables (182 bytes, fixed)
#5CB6      Channel definitions
           ↓ grows
           Stream data (30 bytes for 15 streams)
           ↓
#5D00      BASIC program area (grows upward with LIST)
           ↓
           BASIC variables area (grows upward)
           ↓
           Free RAM
           ↓
           ↓
           ↓
           User-defined graphics (UDG) — grows downward from RAMTOP
#FF58      Default UDG area start (48K)
RAMTOP     Top of BASIC system area
#FFFF      End of physical RAM (48K)
```

### Key Pointers for Navigation

| From | To | Purpose |
|------|----|---------|
| `PROG` (`#5C53`) | `VARS` (`#5C4B`) | BASIC program text |
| `VARS` (`#5C4B`) | `E_LINE` (`#5C59`) | BASIC variables |
| `E_LINE` (`#5C59`) | `WORKSP` | Edit line buffer |
| `WORKSP` | `STKBOT` | Workspace |
| `STKEND` | `UDG` (`#5C7B`) | Free RAM (calc stack to UDG) |

---

## Cross-References

- **48K memory map** (address ranges, contended regions): [memory_map_48k.md](../05_development/03_memory_and_io/memory_map_48k.md)
- **128K memory map** (banking, 128K extensions): [memory_map_128k.md](../05_development/03_memory_and_io/memory_map_128k.md)
- **Interrupt programming** (hooking into the frame counter): [im1_programming.md](../05_development/04_interrupts/im1_programming.md)
- **ROM disassembly** (complete system variable reference): [skoolkid ROM sysvars](https://skoolkid.github.io/rom/buffers/sysvars.html)
- **I/O ports** (#FE keyboard reading): [io_ports.md](../05_development/03_memory_and_io/io_ports.md)
