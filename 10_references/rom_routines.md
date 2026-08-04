[← Home](../README.md) · [References](README.md)

# ROM Routines — ZX Spectrum ROM Entry Points

Every useful ROM entry point for the 48K and 128K/+2 ROMs: restart vectors, system routines, tape routines, character output, math routines, and editor helpers. The 48K ROM is documented in detail in Logan and O'Hara's *Complete Spectrum ROM Disassembly*; this article is the **lookup table** — you come here to find the address and calling convention for a specific routine.

> [!NOTE]
> For the *internals* of the ROM (how it parses BASIC, manages streams, runs the editor), see [rom_48k.md](../04_operating_systems/rom_48k.md). This article is the **calling-convention reference** for assembly programmers who want to invoke ROM functionality.

---

## Restart Vectors (RST #08–#38)

The Z80 reserves 8 bytes at the bottom of address space for **restart vectors** — short `RST n` instructions that act like fast calls. The 48K ROM uses five of them:

| Address | Instruction | Purpose |
|---|---|---|
| `#0000` | (reset) | Cold/warm reset — clears RAM and enters the editor |
| `#0008` | `RST #08` | Error handler — prints error message and exits to editor; HL = error code (negated) |
| `#0010` | `RST #10` | `PRINT_CHAR` — print character in A to current stream |
| `#0018` | `RST #18` | `COLLECT_CHAR` — fetch next character from current stream into A |
| `#0020` | `RST #20` | `KEY_SCAN` — scan keyboard, return key info |
| `#0028` | `RST #28` | Floating-point calculator — HL = opcode list |
| `#0030` | `RST #30` | Unused (reserved for BCPL-style call in 128K) |
| `#0038` | `RST #38` | Maskable INT service routine (IM 1) — also reached by JP for non-IM1 setups |

`RST` instructions are single-byte and take 11 T-states — much faster than `CALL` (17 T-states, 3 bytes).

> [!WARNING]
> `RST #08` does not return. It goes through `ERR_SP` to the error handler, which clears the stack and exits to the editor. Only call it when you actually want to abort the program.

---

## Character Output Routines

| Address | Name | Entry | Exit | Modifies |
|---|---|---|---|---|
| `#0010` | `RST #10` PRINT_CHAR | A = character | Char printed | AF, HL, BC, DE |
| `#0D4D` | CHAN_OPEN | A = channel number | Channel opened | AF, BC, DE, HL |
| `#0E44` | CHAN_OPEN_SUB | A = channel number | Channel opened (subroutine) | AF, BC, DE, HL |
| `#15EF` | PRINT_OUT | A = character, BC = coordinates | Char printed | All |
| `#1A1B` | BEEP | HL = pitch, DE = duration | Beep played | All |
| `#0F2C` | TEMPO_PAUSE | HL = ms delay | Delay executed | All |
| `#22B5` | PRINT_FLOAT | STKBOT = float | Float printed | All |

### `RST #10` PRINT_CHAR

Prints the character in A to the currently-open channel. Recognises control codes (`#06` AT, `#11` INK, `#0D` newline, etc.) and acts on them. Useful for both raw text output and formatted printing.

```z80
        LD   A,'H'           ; Print 'H'
        RST  #10
        LD   A,'i'
        RST  #10
```

To open a stream first, use `CHAN_OPEN`:

```z80
        LD   A,2              ; Stream 2 = main screen
        CALL #0E44            ; CHAN_OPEN
        LD   A,'*'
        RST  #10
```

### BEEP Routine at `#1A1B`

Generates a tone on the beeper. Entry parameters:

- HL = pitch in **semitones × 256** above middle C (negative for below)
- DE = duration in frames (50 Hz units)

Example: middle C for 1 second:

```z80
        LD   HL,0              ; Middle C (pitch 0)
        LD   DE,50             ; 50 frames = 1 second
        CALL #1A1B             ; BEEP
```

For semitone `n` above middle C, pitch = `n * 256`. For semitones below, pitch = `65536 - (|n| * 256)`. The BEEP routine is accurate but takes a long time — it disables interrupts while playing.

---

## Keyboard Routines

| Address | Name | Entry | Exit | Modifies |
|---|---|---|---|---|
| `#028E` | KEY_LINE | — | Line edited | All |
| `#031E` | KEY_INPUT | — | A = key code, C flag set if no key | All |
| `#1E5A` | INPUT_AD | — | A = character input | All |
| `#0202` | BREAK_KEY | — | Zero flag set if BREAK pressed | AF |
| `#10A8` | FLOAT_TO_INT | STKEND = float | HL = integer | All |
| `#0D6D` | CLS | — | Screen cleared | All |

### `KEY_INPUT` at `#031E`

Scans the keyboard once. On exit:

- If a key is pressed: A = key code, carry flag clear
- If no key: carry flag set

The key code is in the same format as the BASIC `INKEY$` function:

| Key code range | Meaning |
|---|---|
| `#20`–`#7F` | Standard ASCII (letters, digits, punctuation) |
| `#80`–`#A4` | User-defined graphics |
| `#A5`–`#FF` | BASIC keywords (token codes) |
| `#0D` | ENTER |

If the user presses BREAK, the routine calls the error handler instead of returning.

### `BREAK_KEY` at `#0202`

Returns zero flag set if BREAK (CAPS SHIFT + SPACE) is currently pressed. Use this in tight loops to allow user interruption:

```z80
LOOP:   ; ...do work...
        CALL #0202            ; BREAK_KEY
        JR   Z,EXIT_LOOP      ; Break pressed, exit
        JR   LOOP
```

### `CLS` at `#0D6D`

Clears the screen (paper + border) and resets the cursor to the top-left. Sets attributes to default (INK black, PAPER white, no FLASH/BRIGHT/INVERSE/OVER).

```z80
        CALL #0D6D            ; CLS
```

---

## Tape Routines

| Address | Name | Entry | Exit | Modifies |
|---|---|---|---|---|
| `#04C2` | SA_BYTES | HL = data, DE = length, A = flag | Byte saved | All |
| `#0556` | SA_BYTE_RET | — | (subroutine exit) | — |
| `#0564` | SA_LD_RET | — | (subroutine exit) | — |
| `#07EE` | LD_BYTES | A = flag, carry set for header | A = byte, carry clear on success | All |
| `#08C0` | LD_BLOCK | — | Block loaded | All |
| `#0801` | LD_EDGE_1 | — | One edge read | All |
| `#0875` | LD_EDGE_2 | — | Two edges read | All |
| `#20CC` | SAVE | (via stream) | Block saved | All |
| `#21CC` | LOAD | (via stream) | Block loaded | All |

### `SAVE` at `#20CC`

Saves a block to tape. Entry parameters via system variables:

- `T_ADDR` (`#5C74`) = start address of data
- `SEED` (`#5C76`) = length in bytes
- A register = block type flag (0 = header, 255 = data)

Example: save a 6912-byte screen starting at `#4000`:

```z80
        LD   A,#FF             ; Data block (not header)
        LD   HL,SAVERET        ; Return address
        PUSH HL
        LD   IX,#4000          ; Start address
        LD   DE,6912           ; Length
        JP   #04C2             ; SA_BYTES (entry point)
SAVERET:
        ; ... continues here
```

The `SAVE` routine is **not** re-entrant and disables interrupts. For Turbo load routines, see the deep-dive in [tape_programming.md](../05_development/08_dos_tape/tape_programming.md).

### `LOAD` at `#21CC`

Loads a block from tape. Same calling convention as SAVE.

---

## Math and Floating-Point Routines

The Spectrum has a built-in floating-point math system based on a 5-byte number format and a stack-based calculator. The calculator's opcodes are invoked via `RST #28` with a list of operations.

### Number Format

A Spectrum floating-point number is 5 bytes:

- Byte 0: exponent (biased by `#80`; `#00` = zero)
- Bytes 1–4: mantissa (32 bits, high bit always 1 for normalized numbers; bit 7 of byte 1 stores the sign)

Integer small enough to fit in 16 bits can also be stored as `#0F` followed by 2 bytes (see [basic_token_table.md](basic_token_table.md) for the inline-number encoding).

### Math Routine Entry Points

| Address | Name | Entry | Exit | Modifies |
|---|---|---|---|---|
| `#2BF1` | FP_TO_BC | STKEND = float | BC = integer | All |
| `#2D1B` | INT_TO_FP | HL = integer | STKEND = float | All |
| `#2D2B` | STACK_NUMBER | HL = literal address | STKEND = float | All |
| `#303A` | SIN | STKEND = angle (radians) | STKEND = sin | All |
| `#30D2` | COS | STKEND = angle (radians) | STKEND = cos | All |
| `#3310` | TAN | STKEND = angle (radians) | STKEND = tan | All |
| `#3485` | ASN | STKEND = value | STKEND = arcsin | All |
| `#35C6` | ACS | STKEND = value | STKEND = arccos | All |
| `#36C5` | ATN | STKEND = value | STKEND = arctan | All |
| `#3871` | LN | STKEND = value | STKEND = ln | All |
| `#3C9D` | EXP | STKEND = value | STKEND = exp | All |
| `#3C98` | SQR | STKEND = value | STKEND = sqrt | All |
| `#3CD0` | SGN | STKEND = value | STKEND = sign | All |
| `#3DA0` | ABS | STKEND = value | STKEND = absolute value | All |
| `#3DA5` | NEGATE | STKEND = value | STKEND = negated value | All |
| `#1F05` | COPY | — | Screen copied to ZX Printer | All |

### The Stack Calculator (`RST #28`)

The floating-point calculator uses a separate stack (the **calculator stack**) distinct from the Z80 stack. Operations are written as a list of single-byte opcodes terminated by `#38` (end). `RST #28` with HL pointing to the opcode list runs them in sequence.

| Opcode | Operation | Stack effect |
|---|---|---|
| `#0F` | ADD | `a b` → `a+b` |
| `#03` | SUBTRACT | `a b` → `a-b` |
| `#04` | MULTIPLY | `a b` → `a*b` |
| `#05` | DIVIDE | `a b` → `a/b` |
| `#38` | END_CALC | (terminates) |

Example: calculate `3 * 4 + 5`:

```z80
        LD   HL,CALC_LIST
        RST  #28              ; Run calculator
        ; Result on calc stack at STKEND
CALC_LIST:
        DEFB #2D              ; STACK_CONST (literal: 3)
        DEFB #00,#00,#00,#40  ; 3.0 in FP
        DEFB #2D              ; STACK_CONST
        DEFB #00,#00,#00,#80  ; 4.0
        DEFB #04              ; MULTIPLY (3*4)
        DEFB #2D              ; STACK_CONST
        DEFB #00,#00,#A0,#40  ; 5.0
        DEFB #0F              ; ADD (3*4 + 5)
        DEFB #38              ; END_CALC
```

This is the same mechanism the BASIC ROM uses internally to evaluate expressions. The full opcode list (over 50 operations) is in the ROM disassembly.

---

## 128K-Specific Routines

The 128K ROM adds routines for AY-3-8912 sound, RAM banking, and the menu system. These are **not** at the same addresses as 48K routines — the 128K ROM is a completely different codebase.

### 128K Sound Routines

| Address (ROM 0) | Name | Use |
|---|---|---|
| `#1100` | MUSIC (entry) | MUSIC command handler |
| `#11AB` | PLAY | PLAY command handler |
| `#1A29` | TEMPO | TEMPO command handler |

### 128K Banking Routines

| Address (ROM 0) | Name | Use |
|---|---|---|
| `#1B17` | MEM_COPY | Copy data between banks |
| `#2300` | PAGE_BANK | Page a specific bank at `#C000` |
| `#2335` | RESTORE_BANK | Restore previous banking state |

> [!WARNING]
> 128K ROM addresses above assume ROM 0 is paged in. If you call from ROM 1, addresses are different. Always check which ROM is currently paged before calling these routines.

---

## Cross-References

- [memory_maps.md](memory_maps.md) — system variable addresses (`#5C00` range)
- [io_port_map.md](io_port_map.md) — ports for hardware access (when ROM routines are insufficient)
- [basic_token_table.md](basic_token_table.md) — keyword tokens referenced in some ROM routines
- [error_codes.md](error_codes.md) — error codes used by `RST #08`
- [timing_reference.md](timing_reference.md) — T-state counts for ROM routines
- [rom_48k.md](../04_operating_systems/rom_48k.md) — 48K ROM deep dive
- [rom_128k.md](../04_operating_systems/rom_128k.md) — 128K ROM deep dive
- [rom_plus2.md](../04_operating_systems/rom_plus2.md) — +2 grey ROM deep dive
- [tape_programming.md](../05_development/08_dos_tape/tape_programming.md) — custom tape routines (load and save)
- [assembly_patterns.md](../05_development/02_assembly/assembly_patterns.md) — calling ROM routines from machine code

---

## References

- Ian Logan, Frank O'Hara — *The [Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip)*, Melbourne House, 1983 — canonical disassembly with all entry points and calling conventions
- Dr. Ian [Logan — *ZX Spectrum 128 ROM Disassembly*, 1986 — 128K ROM](https://worldofspectrum.org/ROMdisassembly.zip) reference
- Geoff Wearmouth — *48K ROM Disassembly*, [wearmouth.demon.co.uk](https://www.wearmouth.demon.co.uk/zxsp2.htm) — online hypertext disassembly
- Steven Vickers — *ZX Spectrum BASIC Programming*, Sinclair Research, 1982 — official documentation of `BEEP`, `SAVE`, `LOAD` and other statements
- Toni Baker — *Mastering Machine Code on Your ZX Spectrum*, 1983 — practical examples of ROM routine usage
- World of Spectrum — [ROM routines FAQ](https://worldofspectrum.org/faq/reference/romreference.htm)
