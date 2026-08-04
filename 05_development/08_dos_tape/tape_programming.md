[← Plan](../../PLAN.md) · [DOS & Tape](README.md)

# Tape Programming — ROM Load/Save, Custom Loaders, Turbo Loaders

The ZX Spectrum's tape interface is the most iconic loading mechanism in home computer history. The colored border stripes, the screeching audio, the tense wait — every Spectrum programmer experienced this, and every serious Spectrum programmer eventually wanted to control it. Writing your own tape routine was a rite of passage: it taught you bit-banging, timing precision, and the art of squeezing performance from a 3.5 MHz CPU with no hardware support.

This article covers tape programming from the assembly perspective. It is the first article in the [DOS and Tape series](README.md) and assumes you have read the [Assembly series](../02_assembly/README.md), particularly [rom_calls.md](../02_assembly/rom_calls.md) and [stack_and_rst.md](../02_assembly/stack_and_rst.md). It does **not** duplicate the [tape hardware reference](../../03_io/storage/tape_interface.md) or the [tape data format reference](../../03_io/storage/tape_format.md) — those cover the hardware circuit and logical block structure in detail. This article is the **programmer's tutorial**: how to call the ROM routines, how to write your own loader, and how to push the baud rate beyond the standard 1500.

> [!NOTE]
> If you are coming from a modern platform, the idea of spending CPU cycles to read individual bits from a storage device may seem primitive. It is — but it is also the foundation of all software-defined I/O. The techniques in this article (edge detection, timing measurement, bit assembly) apply directly to software serial, software SPI, and any other bit-banging scenario you will encounter on microcontrollers and retro hardware.

---

## ROM Tape Routines

The 48K ROM contains a complete set of tape routines that handle loading and saving at the standard 1500 baud rate. These are the same routines that BASIC's `LOAD` and `SAVE` commands use. Calling them from machine code gives you the standard speed and reliability without needing to write any bit-banging logic.

### The Routine Map

| Address | Name | Function |
|---|---|---|
| `#04C2` | SA-BYTES | Save a block of bytes to tape |
| `#0556` | SA-BYTE-RET | Internal: exit from save byte loop |
| `#07EE` | LD-BYTES | Load a block of bytes from tape |
| `#0801` | LD-EDGE-1 | Internal: detect one tape edge |
| `#0775` | LD-EDGE-2 | Internal: detect two edges (one full pulse) |
| `#08C0` | LD-BLOCK | High-level: load a complete block (header + data) |
| `#20CC` | SAVE | High-level save entry via stream mechanism |
| `#21CC` | LOAD | High-level load entry via stream mechanism |

The routines form a hierarchy: `SAVE`/`LOAD` are the top-level entry points (called by BASIC), which set up system variables and then call `SA-BYTES`/`LD-BYTES` for the actual block transfer. `LD-EDGE-1` and `LD-EDGE-2` are the low-level edge detectors used by `LD-BYTES`.

For a full entry-point reference with parameter details, see [rom_routines.md](../../10_references/rom_routines.md). This article covers the practical usage patterns.

### Saving with SA-BYTES

`SA-BYTES` at `#04C2` writes a single block to tape. Parameters:

| Parameter | Register | Description |
|---|---|---|
| Data address | IX | Start of the data to save |
| Data length | DE | Number of bytes to save |
| Block type | A | `#00` = header block, `#FF` = data block |

The routine outputs a pilot tone (~5 seconds for header, ~2 seconds for data), a sync pulse, the data bytes, and a checksum. It disables interrupts for the duration.

```z80
; Save a 6912-byte screen dump to tape
save_screen:
    LD   A, #FF              ; block type: data (#FF)
    LD   IX, #4000           ; start address: screen memory
    LD   DE, 6912            ; length: 6912 bytes (full display)
    CALL #04C2               ; SA-BYTES
    RET
```

This is the simplest way to save data. The ROM handles all the timing, pilot tones, and checksums.

### Saving with a Header

A proper tape file consists of a **header block** followed by one or more **data blocks**. The header carries the filename, data type, and length. The ROM routine to save a complete file with header is:

```z80
; Save a CODE file with header
save_code_file:
    ; First, build the header in a 17-byte buffer
    LD   HL, header_buf
    LD   (HL), #03           ; type 3 = CODE file
    INC  HL
    LD   DE, filename        ; copy 10-char filename
    LD   B, 10
.copy_name:
    LD   A, (DE)
    LD   (HL), A
    INC  HL
    INC  DE
    DJNZ .copy_name
    ; Data length (2 bytes, little-endian)
    LD   DE, 4096            ; code length
    LD   (HL), E
    INC  HL
    LD   (HL), D
    INC  HL
    ; Parameter 1: load address
    LD   DE, #8000           ; load address
    LD   (HL), E
    INC  HL
    LD   (HL), D
    INC  HL
    ; Parameter 2: 32768 (unused for CODE, = auto-run address for BASIC)
    XOR  A
    LD   (HL), A
    INC  HL
    LD   (HL), A

    ; Save the header block
    LD   A, #00              ; block type: header
    LD   IX, header_buf
    LD   DE, 17              ; header is always 17 bytes
    CALL #04C2               ; SA-BYTES (header)

    ; Save the data block
    LD   A, #FF              ; block type: data
    LD   IX, #8000           ; start of code
    LD   DE, 4096            ; code length
    CALL #04C2               ; SA-BYTES (data)
    RET

header_buf:
    DEFS 17                  ; 17-byte header buffer
filename:
    DB   "MyProgram "        ; exactly 10 characters, padded with spaces
```

For the complete header structure and block types (Program, Number Array, Character Array, Code), see [tape_format.md](../../03_io/storage/tape_format.md).

### Loading with LD-BYTES

`LD-BYTES` at `#07EE` loads a single block from tape. Parameters:

| Parameter | Register | Description |
|---|---|---|
| Block type | A | `#00` = expecting header, `#FF` = expecting data |
| Carry flag | C | Set = looking for header, clear = looking for data |

The routine waits for the pilot tone, synchronizes, reads the data bytes into memory at IX, and verifies the checksum.

```z80
; Load a data block from tape into memory at #8000
load_data_block:
    SCF                      ; carry set = looking for data block
    CCF                      ; invert carry: SCF then CCF = carry clear
    ; Actually, the convention is:
    ;   carry SET = header block expected
    ;   carry CLEAR = data block expected
    ; For data block loading:
    OR   A                   ; clear carry (data block)
    LD   A, #FF              ; expecting data block flag
    LD   IX, #8000           ; destination address
    CALL #07EE               ; LD-BYTES
    JR   C, load_error       ; carry set on exit = error
    ; Data loaded successfully
    RET
load_error:
    ; Handle tape error
    RET
```

> [!WARNING]
> The carry flag convention for LD-BYTES is subtle: on **entry**, carry set means "header block expected" and carry clear means "data block expected." On **exit**, carry set means "error" and carry clear means "success." This dual use of the carry flag is a common source of bugs.

### Using the High-Level LOAD and SAVE

The `LOAD` and `SAVE` entry points at `#21CC` and `#20CC` are higher-level routines that handle the complete header-plus-data sequence. They use system variables for parameter passing:

| System variable | Address | Purpose |
|---|---|---|
| `T_ADDR` | `#5C74` | Start address of data |
| `SEED` | `#5C76` | Length in bytes |

```z80
; High-level load: equivalent to LOAD "" CODE
load_code_rom:
    LD   HL, #8000           ; load address
    LD   (#5C74), HL         ; T_ADDR = load address
    LD   HL, 4096            ; length
    LD   (#5C76), HL         ; SEED = length
    CALL #21CC               ; LOAD
    RET
```

The advantage of using the high-level routines is that they handle the header parsing automatically — the filename, length, and load address are read from the tape header and applied. The disadvantage is that they are slower and less flexible than direct block-level loading.

---

## Custom Loaders

Why would you write a custom tape loader when the ROM already handles loading? Three reasons:

| Reason | Explanation |
|---|---|
| **Speed** | The ROM loader runs at 1500 baud. A custom loader can reach 3000-3600 baud (2x-2.4x faster), cutting load time from 4 minutes to under 2 minutes for a 48K game. |
| **Visual effects** | Custom loaders can display loading screens, animated effects, or music while loading. The ROM loader only shows border stripes. |
| **Compression** | Custom loaders can decompress data on the fly, fitting more data into a shorter load time. |

The vast majority of commercial Spectrum games used custom loaders. The famous Speedlock, Alkatraz, and Bleepload protections were all custom loaders with added anti-piracy features.

### Reading the EAR Bit

All custom tape routines read data from the EAR jack via port `#FE`. The byte returned by `IN A, (#FE)` has the EAR signal in bit 6:

```z80
    IN   A, (#FE)            ; read port #FE
    AND  #40                 ; isolate bit 6 (EAR)
    JR   Z, .ear_low         ; bit 6 clear = EAR is low
    ; bit 6 set = EAR is high
```

The hardware behind this is covered in [tape_interface.md](../../03_io/storage/tape_interface.md). For programming purposes, you only need to know: **bit 6 of port `#FE` reflects the current state of the tape input signal.**

### Edge Detection

Tape data is encoded not as absolute voltage levels but as **transitions** (edges) between high and low. A pulse consists of a rising edge followed by a falling edge (or vice versa). The time between edges determines whether the pulse represents a 0 bit or a 1 bit.

The standard ROM encoding:

| Bit | Pulse width |
|---|---|
| 0 | Two pulses of 855 T-states each |
| 1 | Two pulses of 1710 T-states each |
| Pilot tone | Many pulses of 2168 T-states each |
| Sync pulse 1 | 667 T-states |
| Sync pulse 2 | 735 T-states |

To detect an edge, you poll the EAR bit and wait for it to change. The key is **measuring the time** between edges to distinguish 0-bits from 1-bits.

### A Minimal Edge Detector

Here is the fundamental edge-detection loop. It waits for a transition on the EAR bit and returns the elapsed T-state count in the B register:

```z80
; ----------------------------------------------------------
; Wait for an edge on the EAR input
; Returns: B = approximate T-state count since call
;          C = previous EAR state (#40 or #00)
; Modifies: AF, B, C
; ----------------------------------------------------------
edge_detect:
    LD   B, #FF              ; maximum timeout counter
    LD   C, A                ; save current port value
    AND  #40                 ; isolate EAR bit
    LD   C, A                ; C = current EAR state (#40 or #00)
.wait_loop:
    DEC  B                   ; count down (4T per iteration core)
    JR   Z, .timeout         ; B wrapped to 0 = no edge within timeout
    IN   A, (#FE)            ; read EAR (11T)
    AND  #40                 ; isolate bit 6 (7T)
    CP   C                   ; same as before? (4T)
    JR   Z, .wait_loop       ; yes, keep waiting (12T taken)
    ; Edge detected! B = remaining counter = timing measurement
    RET
.timeout:
    SCF                      ; carry set = timeout error
    RET
```

Each iteration of `.wait_loop` takes approximately 38 T-states (4 + 12 + 11 + 7 + 4). The counter B starts at 255 and decrements, so the maximum wait is about `255 x 38 = 9,690` T-states — enough to detect even the slowest pilot pulses (2168T each).

The value of B when the edge is detected is inversely proportional to the pulse width: a small B means a long wait (wide pulse), a large B means a short wait (narrow pulse). The ROM loader uses this to distinguish 0-bits from 1-bits.

### A Complete Custom Loader

Here is a minimal custom loader (~60 bytes) that reads data at the ROM's standard timing but using its own edge-detection code. This is the starting point for any custom loader:

```z80
; ============================================================
; Minimal custom tape loader
; Loads BC bytes from tape to address HL
; Uses standard ROM timing (1500 baud)
; ============================================================

    ORG  #8000

custom_load:
    DI                       ; disable interrupts (timing-critical)
    LD   (save_sp), SP        ; save stack pointer
    LD   SP, #FFF0            ; temporary stack

    ; Phase 1: Wait for pilot tone
    ; Pilot tone is many pulses of ~2168 T-states each
    LD   B, 0                ; pulse counter
.wait_pilot:
    CALL read_pulse           ; measure one pulse
    ; If pulse width > ~1500T, it is a pilot pulse
    LD   A, B
    CP   #D0                 ; threshold (approximate)
    JR   NC, .got_pilot       ; B high enough = pilot pulse
    ; Not a pilot pulse, reset counter and try again
    LD   B, 0
    JR   .wait_pilot
.got_pilot:
    INC  B                   ; count consecutive pilot pulses
    LD   A, B
    CP   20                  ; need at least ~20 consecutive pilots
    JR   C, .wait_pilot       ; not enough yet
    ; Keep reading pilot pulses until we see the sync
.wait_sync:
    CALL read_pulse
    LD   A, B
    CP   #D0
    JR   NC, .wait_sync       ; still pilot, keep going
    ; B < #D0 means this is the sync pulse — fall through

    ; Phase 2: Read data bytes
    LD   B, 8                ; bits per byte (MSB first)
.read_byte_loop:
    ; Read two pulses (one full bit)
    CALL read_pulse           ; first half of pulse
    CALL read_pulse           ; second half
    ; B now holds the timing of the second pulse
    ; Determine if it was a 0 or 1 bit
    LD   A, B
    CP   #E0                 ; threshold between 0-bit and 1-bit
    ; (This threshold is approximate; tune for your tape recorder)
    CCF                      ; invert carry: wide pulse = carry clear = 0
    RL   C                   ; shift bit into C (MSB first)
    DJNZ .read_byte_loop
    ; C now holds the complete byte
    LD   (HL), C             ; store the byte
    INC  HL                  ; advance pointer
    DEC  DE                  ; decrement byte counter
    LD   A, D
    OR   E
    JR   NZ, .read_byte_loop ; more bytes to read

    ; Phase 3: Read and verify checksum
    CALL read_byte           ; read the checksum byte
    ; (Checksum verification omitted for brevity)

    ; Done — restore and return
    LD   SP, (save_sp)
    EI
    RET

; ----------------------------------------------------------
; read_pulse: wait for two edges, return timing in B
; ----------------------------------------------------------
read_pulse:
    IN   A, (#FE)
    AND  #40
    LD   B, A                ; B = initial state
.edge1:
    IN   A, (#FE)
    AND  #40
    CP   B
    JR   Z, .edge1           ; wait for first edge
    ; First edge detected
    LD   C, #FF              ; timing counter
.edge2:
    DEC  C
    JR   Z, .timeout
    IN   A, (#FE)
    AND  #40
    CP   B
    JR   NZ, .edge2          ; wait for second edge
    ; B = timing value (inverse of pulse width)
    LD   B, C                ; B = pulse width measurement
    RET
.timeout:
    SCF
    RET

read_byte:
    ; (simplified — calls read_pulse 8 times)
    RET

save_sp:   DEFW 0
```

This loader is deliberately simplified. A production loader would add:
- Checksum verification
- Error recovery (retry on bad block)
- Border stripe effects
- A decompression pass for compressed data

> [!TIP]
> The threshold values (`#D0`, `#E0`) are approximate and depend on the tape recorder, tape quality, and volume level. Real-world loaders include calibration logic that measures the pilot tone to derive thresholds dynamically.

---

## Turbo Loaders

A turbo loader is a custom loader that uses **shorter pulse widths** than the ROM standard, allowing data to be read faster. The ROM loader uses 855 T-states for a 0-bit and 1710 T-states for a 1-bit (1500 baud). A turbo loader might use 428T for a 0-bit and 855T for a 1-bit (3000 baud), or even shorter.

### Speed Comparison

| Loader type | 0-bit pulse | 1-bit pulse | Effective baud | Time to load 40K |
|---|---|---|---|---|
| ROM standard | 855T | 1710T | ~1500 baud | ~22 seconds |
| Turbo 2000 | 640T | 1280T | ~2000 baud | ~16 seconds |
| Turbo 3000 | 428T | 855T | ~3000 baud | ~11 seconds |
| Turbo 3600 | 356T | 712T | ~3600 baud | ~9 seconds |
| Extreme turbo | 200T | 400T | ~6400 baud | ~5 seconds |

The practical limit is about 3600 baud on a real tape recorder with consumer-grade tape. Faster speeds require high-quality tape decks, clean heads, and carefully adjusted volume levels. Emulators can handle arbitrarily fast speeds.

### Turbo Loader Design

A turbo loader is structurally identical to the custom loader above — the only difference is the timing thresholds. To convert the standard custom loader to a 3000-baud turbo loader:

1. **Shorten the pilot tone**: Use 1000T pulses instead of 2168T. The pilot tone is just a synchronization aid; it does not need to be as long as the ROM's.
2. **Adjust the thresholds**: The pulse-width comparison thresholds change because the turbo pulses are narrower.
3. **Reduce timeout values**: The maximum wait per edge is shorter, so the timeout counter can be smaller.

```z80
; Turbo loader threshold values for 3000 baud
; Pilot pulse: ~1000T each
; 0-bit: 2 x 428T = 856T total
; 1-bit: 2 x 855T = 1710T total
;
; In the edge detector, each loop iteration is ~38T.
; For a 428T pulse, the counter B decrements by about 428/38 = 11 iterations.
; For an 855T pulse, about 22 iterations.
; Threshold between 0 and 1: ~16 iterations.

TURBO_PILOT_THRESHOLD    EQU  #E8    ; ~17 iterations = ~646T (pilot > this)
TURBO_BIT_THRESHOLD      EQU  #F0    ; ~16 iterations = ~608T (0-bit < this < 1-bit)
```

### The Calibration Problem

Real tape recorders vary in speed by 5-10%. A turbo loader designed for exactly 3000 baud may fail on a tape recorder running at 2800 baud. The solution is **calibration**: measure the actual pulse widths from the pilot tone and derive thresholds dynamically.

```z80
; Calibration: measure average pilot pulse width
; Returns: A = average pilot pulse width (in loop iterations)
calibrate:
    LD   B, 0               ; accumulator
    LD   C, 16              ; measure 16 pilot pulses
.cal_loop:
    PUSH BC
    CALL read_pulse          ; measure one pulse (B = width)
    POP  BC
    ADD  A, B                ; accumulate
    DEC  C
    JR   NZ, .cal_loop
    ; A = sum of 16 widths. Divide by 16: shift right 4 times
    SRL  A
    SRL  A
    SRL  A
    SRL  A
    ; A = average pilot width. Use this to compute thresholds.
    ; Typical: threshold_0 = A/2, threshold_1 = A
    LD   (pilot_avg), A
    SRL  A                  ; A = pilot_avg / 2 = 0-bit threshold
    LD   (bit0_threshold), A
    LD   A, (pilot_avg)
    LD   (bit1_threshold), A ; 1-bit threshold = pilot width
    RET

pilot_avg:       DEFB 0
bit0_threshold:  DEFB 0
bit1_threshold:  DEFB 0
```

With calibration, the loader adapts to any tape recorder speed within its operating range. This is why the best commercial turbo loaders worked across a wide variety of hardware.

---

## Border Stripe Effects

The iconic loading border stripes are a side effect of the ROM loader writing the EAR bit state to the border color during loading. You can replicate this in custom loaders for visual appeal:

```z80
; Write EAR state to border during loading
border_stripe:
    IN   A, (#FE)            ; read EAR bit
    AND  #40                 ; isolate bit 6
    ; Shift to border bit (bit 3 of output byte)
    ; The border color is in bits 0-2 of the output to port #FE
    ; We want: EAR high = one color, EAR low = another
    ; Simple: blue border on high, yellow on low
    RRCA                     ; rotate bit 6 to bit 3
    RRCA
    RRCA
    AND  #08                 ; isolate bit 3
    OR   #02                 ; set blue base (bit 1)
    OUT  (#FE), A            ; write border color
    RET
```

During turbo loading, the alternating blue/yellow stripes flash rapidly, creating the classic effect. More sophisticated loaders use the border as a progress indicator or display a loading screen simultaneously.

### Displaying a Loading Screen

A popular technique is to load a screen image first, display it, then continue loading the game code while the player admires the artwork. The key trick: the screen memory (`#4000`-`#57FF`) is loaded during the first block, and the loading stripes appear in the border while the game code loads in the second block.

```z80
; Two-phase loading: screen first, then code
load_game:
    ; Phase 1: Load screen (6912 bytes to #4000)
    LD   HL, #4000           ; destination
    LD   DE, 6912            ; length
    CALL turbo_load_block    ; custom turbo loader

    ; Phase 2: Display screen + border message
    ; (Screen is now visible at #4000)
    ; Set border to show loading is in progress
    LD   A, #02              ; red border
    OUT  (#FE), A

    ; Phase 3: Load game code (contended memory!)
    LD   HL, #8000           ; destination (uncontended)
    LD   DE, 32768           ; length
    CALL turbo_load_block    ; continue loading
    ; Border effect during load is handled inside turbo_load_block
    RET
```

---

## Custom Savers

Writing data to tape is the mirror image of reading it. The MIC bit (bit 3 of port `#FE` output) controls the tape output signal. To write a pulse, you toggle the MIC bit with precise timing:

```z80
; Write a pulse of specified width to tape (MIC output)
; Entry: DE = pulse width in T-states (approximate)
write_pulse:
    LD   A, (mic_state)      ; current MIC state
    XOR  #10                 ; toggle MIC bit (bit 3)
    LD   (mic_state), A
    AND  #F7                 ; clear MIC bit temporarily
    OR   (mic_state)         ; apply toggled state
    OUT  (#FE), A            ; write to port
    ; Delay for DE T-states
    LD   B, D
    LD   C, E
.delay:
    DEC  BC
    LD   A, B
    OR   C
    JR   NZ, .delay
    RET

mic_state:   DEFB #0F        ; initial port state (MIC off)
```

A complete turbo saver writes pilot tone, sync pulses, data bytes, and checksum — all with precise timing. The structure is straightforward but the timing must be exact. For the standard ROM save, use `SA-BYTES` at `#04C2` instead — it is easier and handles all timing internally.

### Verification (Read-Back Check)

After saving a block, you can verify it by reading it back:

```z80
save_and_verify:
    ; Save the block
    LD   A, #FF
    LD   IX, #8000
    LD   DE, 4096
    CALL #04C2               ; SA-BYTES

    ; Prompt user to rewind tape
    LD   A, 2
    CALL #1601               ; ROM PRINT (channel 2)
    LD   HL, rewind_msg
    CALL print_string

    ; Load the block back into a temp buffer
    LD   IX, verify_buf
    LD   DE, 4096
    CALL #07EE               ; LD-BYTES
    JR   C, verify_error

    ; Compare original and loaded data
    LD   HL, #8000
    LD   DE, verify_buf
    LD   BC, 4096
.compare:
    LD   A, (DE)
    CPI                      ; compare (HL) with A, HL++, BC--
    JR   NZ, mismatch        ; data differs!
    JP   PE, .compare        ; BC not zero yet
    ; Data matches — save verified
    RET

rewind_msg:   DB "Rewind tape, press PLAY", #0D, 0
```

---

## Error Handling

Tape errors are common. Real tapes have dropouts, wow and flutter, and volume inconsistencies. A robust loader must handle errors gracefully.

### Common Error Types

| Error | Cause | Handling |
|---|---|---|
| Checksum mismatch | Noise, dropout, speed variation | Retry the block load |
| No pilot tone | Wrong tape, wrong side, volume too low | Display message, wait for user |
| Edge timeout | No signal for extended period | Abort with error message |
| Data garbled | Intermittent signal, contention | Retry or abort |

### Retry Logic

```z80
load_with_retry:
    LD   B, 3               ; max retries
.retry:
    PUSH BC
    LD   A, #FF
    LD   IX, #8000
    LD   DE, 4096
    CALL #07EE               ; LD-BYTES
    POP  BC
    JR   NC, .success         ; carry clear = success
    DJNZ .retry               ; retry up to 3 times
    ; All retries failed
    LD   A, 2                 ; red border = error
    OUT  (#FE), A
    LD   HL, error_msg
    CALL print_string
    RET
.success:
    LD   A, 4                 ; green border = success
    OUT  (#FE), A
    RET

error_msg:   DB "Tape loading error", #0D, 0
```

### Border Color Conventions

| Color | Meaning |
|---|---|
| Blue/cyan stripes | Normal loading in progress |
| Red | Error (checksum failure, no signal) |
| Green | Successful load |
| Yellow | Turbo loading (custom loaders) |
| White | Pilot tone detection |

---

## When to Use ROM vs Custom Loader

| Criterion | ROM routine | Custom loader |
|---|---|---|
| Development effort | Minimal (one CALL) | High (write + debug timing code) |
| Load speed | 1500 baud | 3000-3600 baud |
| Visual effects | Border stripes only | Loading screen, custom effects, music |
| Reliability | High (well-tested ROM code) | Depends on implementation |
| Compatibility | All Spectrum models | May need tuning per tape deck |
| Compression | No | Yes (on-the-fly decompression) |
| Code size | 0 (ROM code) | 50-200 bytes |
| Use case | Simple programs, utilities | Games, demos, commercial software |

### Recommendation

- **For utilities and simple programs**: Use the ROM routines (`SA-BYTES`, `LD-BYTES`). The standard 1500 baud is adequate and the ROM code is thoroughly tested.
- **For games**: Use a custom turbo loader. The 2x speed improvement is worth the development effort, and the ability to show a loading screen enhances the user experience.
- **For demos**: Custom loaders are mandatory for multi-part streaming and compressed data.

---

## Pitfalls

### 1 — Interrupts Disrupt Timing

The IM1 interrupt service routine fires every 20 ms and takes ~4,000-6,000 T-states. If an interrupt fires during a custom loader's timing loop, the measured pulse width is wrong and the loader fails.

**Fix**: Always disable interrupts (`DI`) before entering the timing-critical section of a custom loader. Re-enable with `EI` after loading is complete.

### 2 — Contended Memory During Loading

If you load data into the contended memory range (`#4000`-`#7FFF`), the ULA steals CPU cycles during the screen draw period. This corrupts the timing of custom loaders.

**Fix**: Load into uncontended memory (`#8000`-`#FFFF`) if possible. If you must load into contended memory (e.g., a screen at `#4000`), account for contention in the timing loops or load during the vertical blank period.

### 3 — Volume Level Sensitivity

Real tape recorders require careful volume adjustment. Too low and edges are missed; too high and clipping distorts the signal. The ROM loader is somewhat tolerant; custom turbo loaders are more sensitive.

**Fix**: Include a calibration phase in the loader that measures pilot pulse widths and adapts thresholds. Include user-facing instructions ("set volume to 7").

### 4 — Real Tape vs Emulator Differences

Emulators generate perfectly clean signals; real tapes have noise, dropouts, and speed variation. A loader that works perfectly in an emulator may fail on real hardware.

**Fix**: Always test on real hardware if targeting real-tape users. Emulator-only loaders (popular in the modern demoscene) can skip error handling entirely.

### 5 — Stack Pointer Corruption

Custom loaders often relocate SP to a temporary location. If the loader crashes before restoring SP, the system becomes unstable.

**Fix**: Always save the original SP before changing it, and restore it on every exit path (including error paths). Use a known-safe SP value like `#FFF0`.

### 6 — The Two-Edge Pulse Model

Each data pulse on tape consists of **two edges** (one rising, one falling). If your edge detector only waits for one edge per pulse, it reads garbage. The ROM loader waits for two edges per pulse via `LD-EDGE-2`.

**Fix**: Always read two edges per pulse. The timing measurement is the interval between the first edge of one pulse and the first edge of the next pulse.

---

## Cross-References

- **[tape_interface.md](../../03_io/storage/tape_interface.md)** — EAR/MIC hardware, Schmitt trigger, port #FE bit layout
- **[tape_format.md](../../03_io/storage/tape_format.md)** — block structure, header types, checksum algorithm
- **[tap_format.md](../../03_io/storage/tap_format.md)** — .TAP file format (tape image for emulators)
- **[tzx_format.md](../../03_io/storage/tzx_format.md)** — .TZX file format (preserves turbo loader timing)
- **[rom_routines.md](../../10_references/rom_routines.md)** — ROM tape routine addresses and calling conventions
- **[rom_48k.md](../../04_operating_systems/rom_48k.md)** — ROM disassembly (LD-BYTES, SA-BYTES internals)
- **[assembly_intro.md](../02_assembly/assembly_intro.md)** — first article in Assembly series
- **[rom_calls.md](../02_assembly/rom_calls.md)** — calling ROM routines from assembly
- **[trdos_programming.md](trdos_programming.md)** — disk loading (faster alternative to tape)

## References

- *The [Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip)* by Dr. Ian Logan and Dr. Frank O'Hara — LD-BYTES and SA-BYTES internals
- [smloader](http://sebastianmihai.com/smloader-minimalist-ZX-Spectrum-custom-tape-loader.html) — minimalist 161-byte custom loader (source code)
- [zqloader](https://github.com/oxidaan/zqloader) — modern turbo loader for 48K games
- [How Tape Loading Works](https://lemmings.info/how-tape-loading-works/) — visual explanation of pulse timing
- [ZX Spectrum Custom Tape Loaders](https://www.youtube.com/watch?v=8e_IkqfMeD4) — collection of commercial loader effects
