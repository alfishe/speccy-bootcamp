[← Plan](../../PLAN.md) · [Assembly](README.md)

# ROM Calls — Cookbook for 48K and 128K ROM Routines in Assembly

The ZX Spectrum's 16 KB ROM is the closest thing the platform has to an operating system, and it is a remarkably complete one. Written by Nine Tiles Ltd over 1980–1981 and refined by Sinclair's in-house team through 1982, the ROM contains **a BASIC interpreter, a screen editor, a floating-point math package, a tape I/O subsystem, a keyboard scanner, and roughly three hundred callable subroutines** — all in 16,384 bytes of code. Every routine is reachable from your assembly program by a `CALL #xxxx` or a single-byte `RST` instruction.

The question is not *can* you call the ROM — you can, and you should. The question is *when* to call the ROM versus writing the equivalent code yourself. The ROM routines are tested, debugged, and dense (some are marvels of compact code). They are also slow by assembly standards, they trash registers liberally, and they assume the entire BASIC environment is intact. This article is a **practical cookbook**: which routine does what, how to call it without crashing, and how to wrap routine sequences in macros that handle the bookkeeping automatically.

> [!NOTE]
> This article is the second in the six-article [Assembly series](README.md). It assumes you have read [assembly_intro.md](assembly_intro.md) and can build and run a basic Z80 program. For the **lookup table** of every ROM entry point (address, name, parameters), see [rom_routines.md](../../10_references/rom_routines.md) — this article is the tutorial, that one is the reference. For the **internals** of how the ROM parses BASIC, manages streams, and runs the editor, see [rom_48k.md](../../04_operating_systems/rom_48k.md).

---

## The ROM Entry-Point Landscape

The 48K ROM exposes its functionality in three tiers, in roughly increasing order of complexity:

### Tier 1 — Restart Vectors (1-byte calls)

The Z80 has eight hardware restart vectors: addresses `#0000`, `#0008`, `#0010`, `#0018`, `#0020`, `#0028`, `#0030`, `#0038`. Each is reachable by a single-byte instruction `RST n` (encoded as `#C7` for `RST #00`, `#CF` for `RST #08`, etc., incrementing by 8). The instruction takes 11 T-states; an equivalent `CALL` takes 17 T-states and 3 bytes.

The 48K ROM uses five of the eight restart vectors:

| Address | Instruction | Purpose |
|---|---|---|
| `#0008` | `RST #08` | **Error handler.** Prints an error message and exits to the editor. HL = error code (negated). **Does not return.** |
| `#0010` | `RST #10` | **PRINT_CHAR.** Prints the character in A to the currently-open stream. |
| `#0018` | `RST #18` | **COLLECT_CHAR.** Fetches the next character from the current stream into A. |
| `#0020` | `RST #20` | **KEY_SCAN.** Scans the keyboard and returns key info. |
| `#0028` | `RST #28` | **FP_CALC.** Runs the floating-point calculator. HL = opcode list. |

`RST #30` is unused in the 48K ROM (reserved for the 128K's BCPL-style call mechanism). `RST #38` is the maskable interrupt service routine in IM1 mode — calling it directly from your own ISR is unusual but legal.

### Tier 2 — System Routines (3-byte `CALL`)

These are the workhorse routines you will use most often. They take parameters in registers (typically A for a byte value, HL for a pointer, DE for a destination or length) and return results in registers and flags.

| Address | Name | What it does |
|---|---|---|
| `#0D6D` | `CLS` | Clear screen, reset attributes, cursor to top-left |
| `#0E44` | `CHAN_OPEN` | Open a stream (A = stream number) |
| `#0DAF` | `CL_ALL` | Close all streams, reset channels |
| `#1602` | `OPEN_CHAN` | Open channel (alias of CHAN_OPEN via a wrapper) |
| `#1A1B` | `BEEP` | Play a tone on the beeper (HL = pitch, DE = duration) |
| `#0202` | `BREAK_KEY` | Check if BREAK is pressed (sets Z flag) |
| `#028E` | `KEY_LINE` | Invoke the BASIC line editor |
| `#031E` | `KEY_INPUT` | Scan keyboard, A = key code or carry set |
| `#04C2` | `SA_BYTES` | Save bytes to tape (HL = data, DE = length, A = flag) |
| `#07EE` | `LD_BYTES` | Load bytes from tape (A = flag, carry = header/data) |
| `#1F05` | `COPY` | Copy screen to ZX Printer |
| `#22B5` | `PRINT_FLOAT` | Print a floating-point number from the calc stack |
| `#2D28` | `STACK_NUM` | Push a literal number onto the calc stack |
| `#2D1B` | `INT_TO_FP` | Convert HL to floating-point on calc stack |

Full table (with calling conventions, exit state, and register usage) is in [rom_routines.md](../../10_references/rom_routines.md).

### Tier 3 — Low-Level Helpers

These routines are useful only in narrow circumstances — they typically do one tiny piece of work that is part of a larger ROM flow. Examples: `LD_EDGE_1` (`#0801`, reads one tape edge), `KEY_TEST` (returns the half-row scan result for a specific half-row), `BC_SPACES` (allocates N bytes on the BASIC workspace). Reach for these only when you need to do something the higher-level routines do not expose.

---

## Saving and Restoring State — The Non-Negotiable Rule

The single most important thing to know about calling the ROM: **the ROM uses IY as a base register for all system variable access, and trashes AF, BC, DE, and HL freely**. If you have data in any of those registers that you need after the call, you must save it first.

### The IY Register — Always `#5C3A`

The ROM initializes IY to `#5C3A` on boot. Every access to a system variable is encoded as `IY+offset` — for example, `ERR_NR` is at `#5C3A` (offset 0), `FLAGS` is at `#5C3B` (offset +1), `FRAMES` is at `#5C78` (offset +62, accessed as `IY+62` or in code as `L (IY+62)`).

This has three consequences for assembly code:

1. **You cannot use IY freely.** Any time you want to use IY for your own purposes (e.g., as a base pointer for a data structure), you must either disable interrupts (because the IM1 ISR uses IY) or save and restore IY around interrupt-enabled code.

2. **ROM calls assume IY = `#5C3A`.** If you have changed IY for your own purposes, you must restore it before calling any ROM routine.

3. **IX is similar but less constrained.** The ROM uses IX occasionally but not as a base register. You can usually use IX freely, but check the routine's documentation.

### The Standard Prologue and Epilogue

The safe pattern for calling a ROM routine that might trash registers you need:

```z80
    PUSH AF                 ; save what you need
    PUSH BC
    PUSH DE
    PUSH HL
    PUSH IX                 ; only if the routine might trash IX
    ; ... possibly PUSH IY if you have changed it

    LD   A, 2               ; set up parameters
    CALL #1602              ; CHAN_OPEN — trashes AF, BC, DE, HL

    ; ... possibly more ROM calls

    POP  IX                 ; restore in reverse order
    POP  HL
    POP  DE
    POP  BC
    POP  AF
```

The order matters: POP in the reverse order of PUSH. Stack imbalance here is one of the most common assembly bugs.

### The Minimal Set

For most ROM calls, you only need to save what you actually need later. If a routine trashes AF and HL but you only care about BC, save only BC. The minimum pattern for a single ROM call:

```z80
    LD   A, 2               ; argument
    PUSH BC                 ; BC is the only register I need across this call
    CALL #1602              ; CHAN_OPEN trashes AF, BC, DE, HL
    POP  BC                 ; restore
```

### The IY Problem in ISRs

If your program installs a custom interrupt service routine (ISR) at `#0038` (IM1) or via a vector table (IM2), and that ISR uses IY, the ROM routines called outside the ISR will see a corrupted IY. Two solutions:

1. **Save and restore IY inside the ISR**:
   ```z80
   isr:
       PUSH IY
       LD   IY, #5C3A       ; restore IY for any ROM calls the ISR might make
       ; ... ISR body ...
       POP  IY
       EI
       RETI
   ```

2. **Disable interrupts during ROM calls** and accept that the frame counter `FRAMES` (`#5C78`) will not advance during the call:
   ```z80
   DI
   CALL #1602
   EI
   ```

The first approach is correct; the second loses frame-counter accuracy and breaks any time-critical code that relies on interrupts.

### The ERR_SP Trick — Try/Catch Around ROM Calls

The system variable `ERR_SP` at `#5C3D` (IY+3) holds the address of the error handler. When `RST #08` is invoked (error), the ROM jumps to the address at `ERR_SP`. By pushing your own address onto ERR_SP before a ROM call, you can intercept errors:

```z80
    ; Set up try/catch around a ROM call
    LD   HL, catch_addr
    PUSH HL
    LD   (#5C3D), SP        ; ERR_SP now points to our handler

    LD   A, #FF             ; some risky operation
    CALL #21CC              ; LOAD — might error if no tape
    ; ... success path ...
    POP  HL                 ; pop our handler off the stack
    JR   continue

catch_addr:
    ; ROM jumps here if RST #08 fires during the call
    ; A = error code (negated)
    ; ... handle the error ...
```

This is an advanced pattern. The stack discipline is delicate — see [stack_and_rst.md](stack_and_rst.md) for a full treatment of `ERR_SP` and the recovery mechanism.

---

## Cookbook — Character Output

### The Minimal Print Routine

The smallest useful print routine prints a single character to the main screen. Two ROM calls are required: `CHAN_OPEN` to direct output to stream 2, then `RST #10` to print the character.

```z80
print_a:
    ; Entry: A = ASCII code to print
    ; Modifies: AF, BC, DE, HL (all trashed by ROM)
    PUSH AF
    LD   A, 2               ; stream 2 = main screen
    CALL #0E44              ; CHAN_OPEN
    POP  AF
    RST  #10                ; PRINT_CHAR
    RET
```

The same routine can be inlined where needed; the function overhead is only useful if you call it from multiple places.

### Printing a String

The standard string-print loop, used by nearly every assembly tutorial, is identical to the Hello World example in [assembly_intro.md](assembly_intro.md):

```z80
print_string:
    ; Entry: HL = address of null-terminated string
    ; Exit: HL points one past the null terminator
    ; Modifies: AF, HL
print_loop:
    LD   A, (HL)
    AND  A                  ; test for zero (sets Z flag)
    RET  Z                  ; done
    RST  #10                ; PRINT_CHAR
    INC  HL
    JR   print_loop
```

This assumes stream 2 is already open. If your program prints strings at multiple points, open the stream once at startup and never close it.

### Printing a Number

Printing an integer in decimal is a common need. The ROM has `PRINT_FLOAT` at `#22B5` which prints a value from the calculator stack, but going through the calc stack for an integer is overkill. A direct approach:

```z80
print_decimal:
    ; Entry: BC = 16-bit unsigned integer to print
    ; Exit: number printed, BC trashed
    LD   A, B               ; check for zero
    OR   C
    JR   Z, .zero           ; special case: 0
    LD   DE, 0              ; digit count
.div_loop:
    ; Divide BC by 10, push remainder as digit
    XOR  A
    LD   L, C
    LD   H, B
    LD   BC, #10
.div_inner:
    SBC  HL, BC             ; HL -= 10
    JR   C, .div_done
    INC  A
    JR   .div_inner
.div_done:
    ADD  HL, BC             ; add back the over-subtracted 10
    PUSH AF                 ; push the digit (in A)
    INC  DE                 ; increment digit count
    LD   C, L               ; HL is now the quotient
    LD   B, H
    LD   A, B
    OR   C
    JR   NZ, .div_loop
    ; Print all digits
    LD   A, '0'
.print_loop:
    POP  AF                 ; digit value
    ADD  A, '0'             ; convert to ASCII
    RST  #10                ; PRINT_CHAR
    DEC  DE
    LD   A, D
    OR   E
    JR   NZ, .print_loop
    RET
.zero:
    LD   A, '0'
    RST  #10
    RET
```

This routine is ~35 bytes and runs in roughly 1500 T-states for a 5-digit number. It is slower than a table-driven approach but small enough for general use.

### Print Positioning

To print at a specific row and column, write the control codes `AT` (`#16`) followed by row and column before the text:

```z80
print_at:
    ; Entry: B = row (0-23), C = column (0-31), HL = string
    LD   A, #16             ; AT control code
    RST  #10
    LD   A, B               ; row
    RST  #10
    LD   A, C               ; column
    RST  #10
    JR   print_string       ; tail call
```

The full set of control codes (`INK`, `PAPER`, `BRIGHT`, `FLASH`, `OVER`, `INVERSE`, `TAB`) work the same way: write the code, then the parameters. See [rom_48k.md § Print Routines](../../04_operating_systems/rom_48k.md) for the complete list.

---

## Cookbook — Keyboard Input

The ROM offers three increasingly high-level keyboard routines. Pick the one that matches your need.

### Direct Keyboard Scan — `KEY_INPUT` at `#031E`

`KEY_INPUT` scans the keyboard once and returns a key code in A. If no key is pressed, the carry flag is set. If a key is pressed, carry is clear and A holds the code.

```z80
wait_for_key:
    CALL #031E              ; KEY_INPUT
    JR   C, wait_for_key    ; loop until a key is pressed
    ; A now holds the key code
    RET
```

The key code follows the BASIC `INKEY$` convention:

| Range | Meaning |
|---|---|
| `#20`–`#7F` | Standard ASCII (letters, digits, punctuation) |
| `#80`–`#A4` | User-defined graphics characters |
| `#A5`–`#FF` | BASIC keyword tokens (tokens `PRINT`, `FOR`, etc.) |
| `#0D` | ENTER |

Note that `KEY_INPUT` returns the **current** key state, not a key-down event. Holding a key returns the same code on every call. For debounce, you must implement your own logic:

```z80
wait_press_release:
    ; Wait for keypress, then release, return code in A
    CALL #031E              ; wait for press
    JR   C, wait_press_release
    LD   B, A               ; save key code
.wait_release:
    CALL #031E
    JR   NC, .wait_release  ; loop while key still held
    LD   A, B               ; restore code
    RET
```

### BREAK Detection — `BREAK_KEY` at `#0202`

`BREAK_KEY` returns zero flag set if BREAK (CAPS SHIFT + SPACE) is currently pressed. Useful inside long loops to allow user interruption:

```z80
long_loop:
    ; ... do work ...
    CALL #0202              ; BREAK_KEY
    JR   Z, aborted         ; BREAK pressed
    JR   long_loop
aborted:
    ; ... clean up ...
    RET
```

### Direct Hardware Scan (Bypassing the ROM)

For games that need to read multiple keys simultaneously (e.g., for diagonal movement), the ROM routines are insufficient. They return only one key at a time. The direct approach reads the keyboard matrix via port `#FE`:

```z80
read_full_keyboard:
    ; Returns a 8-byte bitmap of all 40 keys in a buffer at (HL)
    LD   B, #FE             ; starting port (high byte)
    LD   C, #FE             ; starting port (low byte) — fully decoded by ULA
    LD   D, 8               ; 8 half-rows
.scan_loop:
    IN   A, (C)             ; read half-row at port BC
    CPL                     ; invert: bit set = key pressed
    LD   (HL), A
    INC  HL
    INC  C                  ; next half-row (port #FE, #FD, #FB, ...)
    DEC  D
    JR   NZ, .scan_loop
    RET
```

This bypasses the ROM entirely and reads the hardware directly. It is much faster (one IN per half-row, no debounce, no key-code conversion) and gives you the raw state of every key. The downside is that you must interpret the bitmap yourself. See [keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md) for the bit layout of each half-row.

---

## Cookbook — Screen Management

### CLS — Clear Screen at `#0D6D`

`CLS` clears the screen, resets all attributes to default (INK black on PAPER white, no FLASH/BRIGHT/INVERSE/OVER), resets the cursor to the top-left, and sets the border to the current `BORDCR` value. It takes about 16,000 T-states — slow, but acceptable for a startup routine.

```z80
    CALL #0D6D              ; CLS
```

If you only need to clear the pixel area (not the attributes), or only the attributes, you can do it faster with `LDIR`:

```z80
; Clear only pixel area (6144 bytes at #4000)
clear_pixels:
    LD   HL, #4000
    LD   (HL), 0
    LD   DE, #4001
    LD   BC, 6143
    LDIR
    RET

; Clear only attribute area (768 bytes at #5800)
clear_attrs:
    LD   HL, #5800
    LD   (HL), #38          ; default: ink 0, paper 7
    LD   DE, #5801
    LD   BC, 767
    LDIR
    RET
```

`LDIR` takes 16 T-states per byte plus 21 for setup — about 98,000 T-states for the full pixel clear. Faster approaches (unrolled `LDI`, SMC fill) are covered in [assembly_optimization.md](assembly_optimization.md).

### Border Color — `OUT (#FE), A`

The border color is set by writing to port `#FE`. The low 3 bits of the byte are the border color (0-7); other bits affect speaker/MIC/EAR. There is no ROM routine for this — it is a direct hardware operation.

```z80
set_border:
    ; Entry: A = color (0-7)
    AND  7                  ; mask to color bits
    OUT  (#FE), A           ; ULA port
    RET
```

This sets the border but also mutes the speaker and disables MIC output. To preserve the other bits:

```z80
set_border_safe:
    ; Entry: A = color (0-7)
    LD   E, A
    LD   A, (BORDCR)        ; system variable at #5C48
    AND  #F8                ; keep high bits
    OR   E                  ; combine with new border color
    OUT  (#FE), A
    RET
```

### Attribute Manipulation

To set the attribute for a single character cell (row 0-23, column 0-31):

```z80
set_attr:
    ; Entry: B = row (0-23), C = column (0-31), A = attribute byte
    LD   H, 0
    LD   L, B
    ADD  HL, HL             ; HL = row * 2
    ADD  HL, HL             ; row * 4
    ADD  HL, HL             ; row * 8
    ADD  HL, HL             ; row * 16
    ADD  HL, HL             ; row * 32
    LD   D, 0
    LD   E, C
    ADD  HL, DE             ; HL = row*32 + column
    LD   DE, #5800
    ADD  HL, DE             ; HL = address in attribute file
    LD   (HL), A
    RET
```

The attribute byte format:

```
Bit  7  6  5  4  3  2  1  0
     F  B  P2 P1 P0 I2 I1 I0

F  = Flash (1 = blink)
B  = Bright (1 = bright colors)
P2 P1 P0 = Paper color (background, 0-7)
I2 I1 I0 = Ink color (foreground, 0-7)
```

For example, attribute `#38` is bright white paper (`111`), ink 0 (black): the default. `#42` is red ink on green paper.

### Plotting a Pixel via the ROM

The ROM provides `PLOT` at `#22B5` (which prints the calc-stack float, not the graphics command — common confusion). The actual pixel-plot routine is `PLOT_SUB` at `#22DC`. The BASIC `PLOT x, y` command goes through `PLOT_SUB`.

```z80
plot_pixel:
    ; Entry: B = y coordinate (0-175), C = x coordinate (0-255)
    ; Modifies: AF, BC, DE, HL
    LD   A, B
    CP   175
    RET  NC                 ; out of range, ignore
    LD   A, C
    CP   255
    RET  NC
    LD   A, 0               ; screen mode (0 = plot, 1 = unplot via PLOT_MODE)
    LD   (#5C8D), A         ; actually `SCREEN_ADDR` — placeholder for direct access
    CALL #22DC              ; PLOT_SUB
    RET
```

The ROM's PLOT is slow (~300 T-states per pixel) because it handles all the address arithmetic generically. A direct screen-access routine is ~10× faster. See [screen_access.md](../06_graphics/screen_access.md) (planned) for the direct approach.

---

## Cookbook — Sound (Beeper)

The 48K ROM's only sound routine is `BEEP` at `#1A1B`. It takes a pitch (in semitones relative to middle C, multiplied by 256) and a duration (in frames at 50 Hz).

```z80
play_beep:
    ; Middle C for half a second
    LD   HL, 0              ; pitch 0 = middle C (semitone offset)
    LD   DE, 25             ; 25 frames = 0.5 seconds
    CALL #1A1B              ; BEEP
    RET
```

For a higher pitch, use positive HL. For lower, use negative (HL is signed 16-bit):

```z80
    LD   HL, 256            ; one octave up (12 semitones × 256)
    LD   DE, 25
    CALL #1A1B

    LD   HL, -512           ; two octaves down
    LD   DE, 50
    CALL #1A1B
```

### Limitations of ROM BEEP

`BEEP` is **not suitable for game sound effects or music** because:

1. **It disables interrupts** during the entire beep. `FRAMES` stops advancing; the keyboard is not scanned.
2. **It is single-tasking.** No other code runs while the beep plays.
3. **Pitch resolution is coarse** at short durations due to integer rounding in the loop counter.
4. **It is monophonic** — only one tone at a time on the 1-bit beeper.

For game sound, you must write your own beeper routine that runs from an ISR, mixing multiple voices via PWM. See [beeper_synthesis.md](../../06_sound/synthesis/beeper_synthesis.md) for the deep dive. For 128K machines with the AY-3-8912, see the section below on 128K-specific routines.

---

## Cookbook — Math via the Floating-Point Calculator

The ROM contains a complete floating-point math package. It is exposed via `RST #28` (the calculator) and a set of helper routines. The calculator uses its own stack (the **calculator stack**, growing upward from `STKEND` at `#5C65`) and a list of single-byte opcodes.

### When to Use the ROM Math

| Use ROM math for... | Use direct asm for... |
|---|---|
| Trigonometric functions (sin, cos, tan) | Integer add/subtract |
| Square root, logarithms, exponentials | Integer multiply (small operands) |
| Floating-point arithmetic | Bit operations |
| Display formatting (decimal output) | Comparisons |
| Anything where the math is not the bottleneck | Anything in a 50fps hot loop |

The ROM's `SIN` (`#303A`) takes about 6,000 T-states. A 256-entry lookup table takes about 30 T-states. Pick accordingly.

### The Calculator Invocation Pattern

`RST #28` runs the calculator. HL points to a list of single-byte opcodes; the list ends with `#38` (end). The calculator maintains its own stack at `STKEND` (`#5C65`).

```z80
    ; Compute 2 + 3 and leave result on calc stack
    LD   HL, calc_2_plus_3
    RST  #28
    ; Result is now at top of calc stack
calc_2_plus_3:
    DEFB #2D               ; STACK_CONST opcode
    DEFB #00, #00, #00, #40  ; 2.0 in FP format (exponent #00 + 4-byte mantissa)
    DEFB #2D               ; STACK_CONST
    DEFB #00, #00, #40     ; 3.0 (compact form)
    DEFB #0F               ; ADD
    DEFB #38               ; END_CALC
```

The full opcode table (over 50 operations: ADD, SUBTRACT, MULTIPLY, DIVIDE, SIN, COS, TAN, LN, EXP, SQR, ABS, NEGATE, etc.) is in [rom_routines.md § FP_CALC Opcodes](../../10_references/rom_routines.md#the-stack-calculator-rst-28) and the [Complete Spectrum ROM Disassembly](https://worldofspectrum.net/).

### 16-Bit Multiply via the Calculator

For one-off multiplications where speed does not matter, the calculator is fine:

```z80
multiply_de_by_bc:
    ; Entry: DE = first factor, BC = second factor
    ; Exit: result on calc stack; pull with FP_TO_BC
    PUSH BC
    PUSH DE
    ; Stack DE as float
    POP  HL                 ; HL = first factor
    CALL #2D1B              ; INT_TO_FP: HL → calc stack
    PUSH BC
    POP  HL                 ; HL = second factor
    CALL #2D28              ; STACK_NUM: HL → calc stack (without conversion)
    ; Now multiply
    LD   HL, mul_opcodes
    RST  #28
    ; Result is on calc stack; convert back to BC
    CALL #2BF1              ; FP_TO_BC: STKEND → BC
    RET
mul_opcodes:
    DEFB #04               ; MULTIPLY
    DEFB #38               ; END_CALC
```

This works but takes ~3,000 T-states. A direct shift-and-add multiply (covered in [assembly_optimization.md](assembly_optimization.md)) takes ~400 T-states for 8×8 or ~1,500 for 16×16. Use the calculator when you genuinely need floating-point (trigonometry, square roots) or when speed is irrelevant.

### Sine via Lookup vs ROM

For 50fps animation that needs trigonometry, the calculator is too slow. The standard approach is a 256-entry sine table:

```z80
    ; 256-entry sine table, values in range -128 to +127
    ; Input: A = angle (0-255, where 0 = 0°, 64 = 90°, 128 = 180°, 192 = 270°)
    ; Output: A = sin(angle) * 127
sin_a:
    LD   HL, sin_table
    LD   B, 0
    LD   C, A
    ADD  HL, BC
    LD   A, (HL)
    RET

sin_table:
    DB $00, $03, $06, $09, $0C, $10, $13, $16
    DB $19, $1C, $1F, $22, $25, $28, $2B, $2E
    DB $31, $33, $36, $39, $3B, $3E, $40, $43
    ; ... 256 entries total
```

This is ~30 T-states vs ~6,000 for the ROM `SIN`. The table costs 256 bytes. For most games and demos, the trade-off is worth it.

---

## 128K-Specific ROM Routines

The 128K, +2, +2A, and +3 have a **completely different 32 KB ROM** split across two 16 KB pages (ROM 0 and ROM 1). The 48K ROM is also present as ROM 1 in these machines, and they switch between ROM 0 (128K-specific features) and ROM 1 (48K compatibility) at runtime.

### ROM Banking Essentials

The port `#7FFD` controls memory banking on all 128K machines:

```
Bit  Meaning
0-2  RAM bank paged at #C000 (0-6 for 128K, 0-7 for +2A/+3)
3    Screen select (0 = normal at #4000, 1 = second screen at #C000 in bank 7)
4    ROM select (0 = ROM 0 = 128K, 1 = ROM 1 = 48K compatibility)
5    Disable paging (set once to lock the configuration)
7    ( +2A/+3 only ) special paging modes
```

To call a 128K-specific routine, you must:

1. Save current banking state
2. Page in ROM 0 (if not already paged)
3. Set up your routine to live in RAM that is NOT in the `#C000`-`#FFFF` bank (because paging the ROM does not affect lower memory)
4. Make the call
5. Restore banking state

The 128K ROM has its own copy of certain 48K routines at different addresses, plus new routines:

| Address (ROM 0) | Name | Use |
|---|---|---|
| `#1100` | MUSIC handler | MUSIC command (play AY-3-8912 melody via note syntax) |
| `#11AB` | PLAY handler | PLAY command (full PLAY mini-language) |
| `#1A29` | TEMPO handler | TEMPO command (set PLAY tempo) |
| `#1B17` | MEM_COPY | Copy data between memory banks |
| `#2300` | PAGE_BANK | Page a specific bank at `#C000` |
| `#2335` | RESTORE_BANK | Restore previous banking state |

### PLAY from Assembly

The PLAY command's mini-language is documented in [basic_128k.md § PLAY Mini-Language](../01_basic/basic_128k.md). From assembly, calling PLAY requires building the three channel strings in memory, pointing system variables at them, and invoking the handler.

```z80
play_music:
    ; Entry: HL, DE, BC = pointers to channel A, B, C strings (null-terminated)
    ; Modifies: all registers, plus banking state
    LD   (chan_a_ptr), HL
    LD   (chan_b_ptr), DE
    LD   (chan_c_ptr), BC
    
    ; Ensure ROM 0 is paged
    LD   A, (#5B5C)         ; current paging state (sysvar BANK_M)
    BIT  4, A               ; is ROM 0 paged?
    JR   NZ, .rom0_ok       ; yes, skip swap
    XOR  #10                ; toggle ROM bit
    LD   BC, #7FFD
    OUT  (C), A             ; page in ROM 0
    LD   (#5B5C), A
.rom0_ok:
    ; Call the PLAY handler
    LD   HL, (chan_a_ptr)
    LD   DE, (chan_b_ptr)
    LD   BC, (chan_c_ptr)
    CALL #11AB              ; PLAY handler
    
    ; (Caller must restore banking if needed)
    RET

chan_a_ptr: DEFW 0
chan_b_ptr: DEFW 0
chan_c_ptr: DEFW 0
```

In practice, **calling PLAY from assembly is rare**. The PLAY command is invoked from BASIC, which handles banking automatically. If you need background music in an assembly program, the standard approach is to use a dedicated AY-3-8912 player routine that reads a tracked music format (PT3, ASC, etc.). See [06_sound/](../../06_sound/) for player routines.

### Direct AY-3-8912 Access (Bypassing the ROM)

For direct AY-3-8912 control, you write to two ports: `#FFFD` (register select) and `#BFFD` (data write). This bypasses the ROM entirely.

```z80
ay_write:
    ; Entry: B = register number (0-13), A = value
    ; Modifies: AF, BC
    LD   C, A               ; save value in C
    LD   A, B
    OUT  (#FFFD), A         ; select register
    LD   A, C
    OUT  (#BFFD), A         ; write value
    RET

ay_read:
    ; Entry: B = register number
    ; Exit: A = value
    LD   A, B
    OUT  (#FFFD), A         ; select register
    IN   A, (#FFFD)         ; read value (only registers 0-14 readable)
    RET
```

The full AY-3-8912 register reference is in [ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md). The standard music tracker players (PT3, ASC, PLY) all use direct port access rather than the ROM.

---

## Wrapping ROM Calls in Helper Macros

Once you write the same prologue/epilogue pattern three times, it is time to factor it into a macro. SjASMPlus macros look like this:

```z80
    MACRO PRINT_CHAR_M char
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL
    LD   A, char
    RST  #10
    POP  HL
    POP  DE
    POP  BC
    POP  AF
    ENDM
```

After this definition, `PRINT_CHAR_M 'H'` expands to the eight instructions inline. A more useful macro library:

```z80
; --- macros.asm ---

    MACRO OPEN_STREAM stream
    PUSH AF
    LD   A, stream
    CALL #0E44              ; CHAN_OPEN
    POP  AF
    ENDM

    MACRO PRINT_STRING_M addr
    PUSH AF
    PUSH HL
    LD   HL, addr
.ps_loop:
    LD   A, (HL)
    AND  A
    JR   Z, .ps_done
    RST  #10
    INC  HL
    JR   .ps_loop
.ps_done:
    POP  HL
    POP  AF
    ENDM

    MACRO CLS_M
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL
    CALL #0D6D              ; CLS
    POP  HL
    POP  DE
    POP  BC
    POP  AF
    ENDM

    MACRO SET_BORDER_M color
    PUSH AF
    LD   A, color
    AND  7
    OUT  (#FE), A
    POP  AF
    ENDM

    MACRO BEEP_M pitch, duration
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL
    LD   HL, pitch
    LD   DE, duration
    CALL #1A1B              ; BEEP
    POP  HL
    POP  DE
    POP  BC
    POP  AF
    ENDM
```

Usage:

```z80
    INCLUDE "macros.asm"

    OPEN_STREAM 2
    CLS_M
    PRINT_STRING_M hello_msg
    SET_BORDER_M 2          ; red border
    BEEP_M 0, 25            ; middle C, half a second
    RET

hello_msg:
    DB "Hello, World!", #0D, #00
```

### Cost of Macros

Macros expand inline, so each use costs the full prologue/epilogue. If you call the macro in a tight loop, you are paying for PUSH/POP on every iteration. In hot loops, manually inline only what you need.

### Alternative: Subroutine Library

If you call a routine from many places, factor it into a subroutine rather than a macro to save code size:

```z80
; --- subs.asm ---
open_stream:
    ; Entry: A = stream number
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL
    CALL #0E44
    POP  HL
    POP  DE
    POP  BC
    POP  AF
    RET

cls:
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL
    CALL #0D6D
    POP  HL
    POP  DE
    POP  BC
    POP  AF
    RET
```

Each call costs a `CALL` (3 bytes, 17 T-states) plus the prologue/epilogue inside the subroutine, but only one copy of the prologue exists in the binary. For a routine called 20 times, the subroutine version saves ~400 bytes versus the macro version.

---

## When NOT to Use ROM Calls

ROM calls are a tool, not a religion. There are situations where bypassing the ROM is the right answer.

### When Performance Matters

The ROM routines are written for compactness, not speed. `BEEP` disables interrupts and uses long floating-point loops. `CLS` does ~16,000 T-states of work. The math routines use the calculator stack, which has 16-bit overhead per operation. For anything in a 50fps hot loop, write the equivalent code yourself:

| Operation | ROM routine | T-states | Direct asm | T-states |
|---|---|---|---|---|
| Clear pixel area | (no direct ROM call) | n/a | `LDIR` over 6144 bytes | ~98,000 |
| Clear entire screen | `CLS` (#0D6D) | ~16,000 | SMC fill | ~50,000 |
| Sine of angle | `SIN` (#303A) | ~6,000 | Table lookup | ~30 |
| 16-bit multiply | (via calculator) | ~3,000 | Shift-and-add | ~400 |
| 16-bit divide | (via calculator) | ~4,000 | Shift-subtract | ~600 |
| Print 5-digit number | `PRINT_FLOAT` + FP | ~5,000 | Direct integer routine | ~1,500 |

### When You Need Deterministic Timing

The ROM routines have variable timing depending on the input. `BEEP` with a long duration does proportionally more work; `CLS` clears more bytes if the screen is full. If you are writing code that must finish within a specific number of T-states (e.g., a race-the-beam effect), do not call the ROM. Write the operation directly.

### When You Have Taken Over the Machine

If your program has done `DI`, taken over the interrupt vector, and is running as a self-contained game or demo, the ROM environment may be partially broken. `FRAMES` is not advancing (interrupts are off), `CURCHL` may point to garbage, the calculator stack may be invalid. In this state, ROM calls may behave unpredictably. The safe approach is to either:

- **Initialize the environment before going off-grid**: set up `CURCHL`, leave `STKEND` valid, ensure `ERR_SP` points somewhere safe.
- **Bypass the ROM entirely**: write your own screen, keyboard, and sound routines. This is what every commercial game and demo does.

### When You Need Cross-Model Portability

The ROM routines are at different addresses on the 48K, 128K, +2A/+3, Pentagon, and Scorpion ROMs. The 48K ROM at `#0D6D` (CLS) is consistent across all of them because they all include a 48K-compatible ROM. But the 128K-specific routines (PLAY, banking helpers) are at addresses that vary by ROM version. If your code must run on multiple models, either stick to 48K-compatible routines or write the operation directly in assembly.

### When the ROM Does Not Provide What You Need

The ROM does not provide routines for:

- AY-3-8912 sound programming (only beeper)
- Memory bank copying (beyond the basic 128K MEM_COPY)
- Multicolor effects (raster synchronization)
- Sprite rendering
- Tape turbo loading
- Disk I/O (TR-DOS or +3 DOS have their own ROMs)
- Keyboard matrix scanning (only single-key via `KEY_INPUT`)
- Joystick reading
- Mouse reading
- Real-time clock

For these, you must write the code yourself or use a library. The rest of the [Assembly series](README.md) and the [Sound](../../06_sound/) section cover these topics.

---

## Pitfalls and Common Mistakes

### Pitfall 1: Forgetting to Restore IY

```z80
; BAD: IY corrupted, subsequent ROM calls crash
my_isr:
    LD   IY, my_data_ptr   ; use IY for my own purposes
    ; ... do stuff ...
    EI
    RETI
main:
    ; ... some time later, an interrupt fires ...
    ; ISR ran, set IY = my_data_ptr
    LD   A, 'H'
    RST  #10               ; PRINT_CHAR assumes IY = #5C3A
    ; output is garbage or crashes
```

```z80
; GOOD
my_isr:
    PUSH IY
    LD   IY, my_data_ptr
    ; ... do stuff ...
    POP  IY                ; restore before returning
    EI
    RETI
```

**Why**: Every ROM routine uses IY as a base register for system variables. If IY is wrong, the routine reads and writes the wrong addresses. The classic symptom is a corrupted screen, weird attribute changes, or an apparent crash in a routine that worked before.

### Pitfall 2: Stack Imbalance from ERR_SP Abuse

```z80
; BAD: error during the call leaves ERR_SP pointing at our handler,
; but the stack itself is unwound to the wrong place
    LD   HL, err_handler
    PUSH HL
    LD   (#5C3D), SP
    CALL #21CC              ; LOAD — might error
    POP  HL                 ; only pops if LOAD succeeded
    ; ... continues ...
```

If `LOAD` errors, the ROM calls `RST #08`, which jumps to `ERR_SP`. The stack state at that point is whatever the ROM left it as — not necessarily where you `PUSH`ed `HL`. Recovery requires careful stack manipulation. The safest pattern is to never rely on the stack across a risky ROM call; instead, use a flag byte.

### Pitfall 3: Calling 48K Routines from 128K Mode

The 128K ROM has its own copies of many routines at **different addresses**. If your code is running with ROM 0 paged in, calling `#0D6D` does NOT call `CLS` — it calls whatever is at that address in the 128K ROM 0, which may be unrelated.

```z80
; WRONG: assumes 48K ROM is paged
    CALL #0D6D              ; CLS — works on 48K, may NOT on 128K!
```

```z80
; CORRECT: explicitly page in ROM 1 (48K) first
    LD   A, (#5B5C)         ; BANK_M sysvar
    SET  4, A               ; ROM 1 = 48K compatibility
    LD   BC, #7FFD
    OUT  (C), A
    LD   (#5B5C), A
    CALL #0D6D              ; now in 48K ROM, CLS works
```

For routines that exist identically in both ROMs (the 128K ROM 1 is a near-copy of the 48K ROM), the addresses are typically the same. But for safety, always check which ROM is paged before calling.

### Pitfall 4: RST #08 Does Not Return

`RST #08` is the error handler. Calling it deliberately is fine if you actually want to abort the program:

```z80
abort_with_error:
    LD   HL, #011A          ; error code #0A = "Out of Memory" (negated)
    ; Actually: HL = negative of error code per ROM convention
    RST  #08
    DEFB #0A                ; literal error code follows the RST
```

But many beginners treat `RST #08` as a printf, expecting it to return. It does not. It clears the stack, restores the editor, and exits to BASIC. Code after `RST #08` is unreachable.

### Pitfall 5: Calculator Stack Corruption

The calculator stack at `STKEND` (`#5C65`) is shared between your assembly code (if you use `RST #28`) and the BASIC environment. If you call `RST #28` and leave values on the stack without popping them, the next call into the BASIC interpreter (via `RET` to BASIC) will misinterpret the stale values.

```z80
; BAD: leaks values on the calc stack
    LD   HL, two_plus_two
    RST  #28                ; result on calc stack
    RET                     ; return to BASIC, leaving 4.0 on calc stack
two_plus_two:
    DEFB #34, 64            ; STACK_CONST 2.0
    DEFB #34, 64            ; STACK_CONST 2.0
    DEFB #04               ; MULTIPLY
    DEFB #38               ; END_CALC
```

To clean up, pop the value explicitly with a `DELETE` opcode (`#22`) at the end of your calculator list, or use `STK_TO_BC` / `FP_TO_BC` to remove it into a register.

### Pitfall 6: Race Conditions Around FRAMES

The `FRAMES` system variable at `#5C78` is a 3-byte counter incremented by the ISR every 20ms (50 Hz). Reading it is racy: if an interrupt fires between reading the low byte and the high byte, you get an inconsistent value.

```z80
; BAD: racy read
    LD   A, (#5C78)
    LD   L, A
    LD   A, (#5C79)         ; interrupt could fire here
    LD   H, A
```

```z80
; CORRECT: disable interrupts during the read
    DI
    LD   A, (#5C78)
    LD   L, A
    LD   A, (#5C79)
    LD   H, A
    EI
```

Or read it twice and check for consistency:

```z80
    LD   A, (#5C79)         ; high byte first
    LD   H, A
    LD   A, (#5C78)         ; low byte
    LD   L, A
    LD   A, (#5C79)         ; high byte again
    CP   H
    JR   NZ, .try_again     ; if changed, retry
```

---

## Cross-References

- **[assembly_intro.md](assembly_intro.md)** — first contact with assembly, including a minimal Hello World that uses `CHAN_OPEN` and `RST #10`
- **[stack_and_rst.md](stack_and_rst.md)** — stack discipline and `ERR_SP` deep dive
- **[assembly_patterns.md](assembly_patterns.md)** — larger-scale patterns for assembly programs
- **[rom_routines.md](../../10_references/rom_routines.md)** — lookup table of every ROM entry point
- **[system_variables.md](../../04_operating_systems/system_variables.md)** — every system variable the ROM routines use
- **[rom_48k.md](../../04_operating_systems/rom_48k.md)** — complete 48K ROM disassembly and internals
- **[rom_128k.md](../../04_operating_systems/rom_128k.md)** — complete 128K ROM disassembly
- **[basic_48k.md](../01_basic/basic_48k.md)** — Sinclair BASIC reference; documents the BASIC commands that wrap these routines
- **[basic_128k.md](../01_basic/basic_128k.md)** — PLAY command reference; covers the same AY-3-8912 access from BASIC
- **[beeper_synthesis.md](../../06_sound/synthesis/beeper_synthesis.md)** — write your own beeper routine instead of using ROM `BEEP`
- **[ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md)** — full AY-3-8912 register reference (128K machines)
- **[keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md)** — direct keyboard scan via port `#FE`
- **[screen_layout.md](../03_memory_and_io/screen_layout.md)** — pixel and attribute file layout for direct screen access
- **[memory_and_io_128k.md](../03_memory_and_io/memory_and_io_128k.md)** — 128K banking details

## References

- Ian Logan, Frank O'Hara — *The [Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip)*, Melbourne House, 1983 — canonical reference for every routine
- Dr. Ian Logan — *ZX Spectrum 128 ROM Disassembly*, 1986 — the 128K ROM equivalent
- Geoff Wearmouth — [*Gosh Wonderful ROM*](http://www.wearmouth.demon.co.uk/gw03.htm) — a community-improved 48K ROM with extensive annotations of every routine
- Toni Baker — *Mastering Machine Code on Your ZX Spectrum*, 1983 — practical ROM routine usage from assembly
- World of Spectrum — [ROM routines reference](https://worldofspectrum.org/faq/reference/romreference.htm)
