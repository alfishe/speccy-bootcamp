# Keyboard Reading — Cross-Model Programming Patterns

## Overview

The ZX Spectrum's keyboard is unusual in that it has **no controller chip**: it is a passive 8×5 switch matrix wired directly into the CPU bus, and the CPU itself must do all the work of scanning. This article is the **programming-side** companion to [02_hardware/original/keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md) (the hardware reference) and covers:

- **Scanning algorithms**: from the simplest one-key-poll to the full 40-key scan
- **Multi-key detection and ghosting**: what the matrix physically allows, and what code patterns avoid phantom keypresses
- **Per-model differences**: 48K ULA port reads, 128K/+2 AY chip reads, +2A/+3 special keyboard row extensions
- **Alternative keyboards on modern hardware**: PS/2 via ZX Spectrum Next, DivMMC, harlequin, etc.
- **Game input conventions**: QAOP, CS, redefine-keys menus, debouncing, repeats
- **Common pitfalls**: the `IN A,(n)` trap, the half-row bit order, contended I/O timing, race with the ROM's INT handler

For the **hardware matrix layout** (the 8 rows × 5 columns, the address-line decode, the diode placement), see [keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md). For the ROM's own keyboard routines (KEY-SCAN, KEY-TEST, KEY-INPUT), see [04_operating_systems/rom_48k.md](../../04_operating_systems/rom_48k.md#keyboard-input). For joystick interfaces (which piggyback on the matrix), see [joystick.md](joystick.md).

---

## Why This Article Is Separate from the Hardware Reference

[02_hardware/original/keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md) is a **hardware article**: it explains the membrane, the ULA's column multiplexer, the address-line row decode, the diodes on A8-A15, ghosting as an electrical phenomenon, and the cable/connector mechanicals. That's the right place to look up "which physical key closes which intersection" and "why does pressing three keys invent a fourth".

This article is a **programming article**: it's the right place to look up "how do I scan all 40 keys in a single frame", "what's the difference between `IN A,(#FE)` and `IN A,(C)` when scanning row 4", "how does the 128K's AY chip change keyboard reading", and "what's the modern PS/2 keyboard protocol for a Spectrum replacement". Cross-references between the two articles are explicit.

---

## The Basic 48K Scan

The simplest possible scan reads a single half-row:

```z80
; Read keys 1-5 (row A11 low)
        LD   BC, #F7FE       ; B = #F7 → A11=0, all other A8-A15 high
                             ; C = #FE → A0=0 selects ULA
        IN   A, (C)          ; bits 0-4 → keys 1, 2, 3, 4, 5
                             ; bit clear = pressed, bit set = released
        AND  #1F             ; mask the 5 keyboard bits
        CPL                  ; now bit set = pressed (easier for code)
        RET
```

That's the complete primitive. The returned byte has bits 0-4 set according to which of keys 1-5 are pressed. (CPL converts from active-low hardware convention to active-high "set = pressed" software convention, which is easier to reason about in game logic.)

### Full 40-key scan

To scan all 8 half-rows in one frame, loop through the eight high bytes:

```z80
; Full 40-key scan.  Returns a 40-bit bitmap in KEYSTATE (5 bytes).
scan_all:
        LD   HL, KEYSTATE         ; 5 bytes = 40 bits
        LD   B, #FE               ; B = high byte for first row (A8=0)
        LD   C, #FE               ; C = low byte (#FE selects ULA)
scan_loop:
        IN   A, (C)               ; read row selected by B
        AND  #1F                  ; bits 0-4 only
        CPL                       ; active-high now
        ; Pack 5 bits into KEYSTATE
        ; ... (bit-packing code, see below)
        ; Advance B: rotate the low bit left through A8-A15
        LD   A, B
        RLCA                      ; next row address bit
        LD   B, A
        CP   #FE                  ; back to first row (after 8 rotates)?
        JR   NZ, scan_loop
        RET
```

The eight high bytes for the rows are `#FE, #FD, #FB, #F7, #EF, #DF, #BF, #7F`. These are just the 8-bit one's-complement of the row number: `#FF & ~(1 << row)`.

### Packing the bits

Forty bits is awkward — it doesn't fit a register pair. The standard game pattern is to pack the 40 bits into 5 bytes (40 bits exactly), one per half-row. The first 5 bits of each byte are used; the upper 3 bits are garbage or repurposed as flags:

```z80
; One half-row read into (HL), then HL advances
read_halfrow:
        IN   A, (C)
        AND  #1F
        CPL
        LD   (HL), A
        INC  HL
        ; advance B to next row
        ...
```

A game's input handler then tests individual bits via `BIT 0, (HL)` after pointing HL at the right byte.

### The "any key pressed" probe

To detect "any key" — useful for "PRESS ANY KEY TO CONTINUE" prompts — read all rows at once by setting every row line low:

```z80
        LD   BC, #FEFE      ; B = #FE means A8=0, but other rows still high
                             ; Wait — we want ALL rows low
```

Actually that won't work; setting B=#FE only makes A8 low. To make **all** row lines low simultaneously, you need B such that A8-A15 are all low — i.e. B=`#00`. The standard idiom:

```z80
any_key:
        LD   BC, #00FE      ; B = #00 → all of A8-A15 low
                             ; C = #FE → ULA selected
        IN   A, (C)          ; bits 0-4 = OR of every pressed key's column
        AND  #1F
        RET  NZ              ; any bit set = at least one key pressed
        ; A == 0 means no keys pressed at all
```

This is fast (5 T-states for the `IN`) and is what the ROM uses for the BREAK-detect during tape load ([rom_48k.md](../../04_operating_systems/rom_48k.md)).

---

## Multi-Key Detection, Ghosting, and Anti-Ghosting

The 48K Spectrum's matrix has **no anti-ghosting diodes**. The diodes you see on the schematic (D15-D22) are on the **row drivers**, not on the individual switches. This means the matrix can produce **phantom keypresses** when three or more keys are pressed simultaneously.

### How ghosting works

If keys at matrix positions (row R1, col C1), (row R1, col C2), and (row R2, col C1) are all pressed simultaneously, then the switch at (row R2, col C2) **also reads as pressed**, even though it isn't. The closed switches form an electrical circuit: R1 → C1 → R2 → C2 → R1, completing the loop.

```
       C1       C2
R1 ----[X]------[X]----   (both keys pressed)
       |        |
R2 ----[X]      ?       (R2,C1 pressed; R2,C2 reads as pressed)
```

The matrix can't tell the difference between "three keys pressed" and "four keys pressed forming a rectangle". This is why some three-key chords work on the Spectrum and others don't — it depends on whether the three keys form a rectangle corner in the matrix.

### Game-design implications

This is why classic Spectrum games converged on the **QAOP-Space** control scheme:

- Q (row A10, col 0), A (row A9, col 0), O (row A13, col 1), P (row A13, col 0), Space (row A15, col 0)
- These keys are positioned in the matrix such that no three of them form a rectangle corner
- They also happen to be naturally positioned for left-hand play (Q/A/O/P form a comfortable diamond, with Space under the thumb)

Other popular schemes:
- **CS (CAPS SHIFT + Symbol)**: CAPS is at (R0, C0), Symbol Shift is at (R7, C1) — no ghosting risk because they're in different rows and columns from the typical action keys
- **12345 / 67890**: all on rows A11 and A12; pressing two keys on the same row is fine, but pressing two on each row simultaneously can ghost
- **OPQA** (variant): O (R13, C1), P (R13, C0), Q (R10, C0), A (R9, C0) — same matrix positions as QAOP, no ghosting

### What software can do

You can't fix ghosting in software — the matrix is what it is. You can only:

1. **Pick keysets that don't form rectangle corners** (what the games did)
2. **Detect three-key chords and reject them** (some games do this for "impossible" combinations)
3. **Use joystick input instead** ( Kempston joystick interfaces are not affected by ghosting — see [joystick.md](joystick.md))
4. **Use the SHIFT keys as modifiers**: CAPS SHIFT (R0, C0) and SYMBOL SHIFT (R7, C1) are in opposite corners of the matrix, so any combination of SHIFT + one other key is ghost-free

For a full ghosting analysis of every popular keyset, see the dedicated section in [keyboard_matrix.md#ghosting](../../02_hardware/original/keyboard_matrix.md#ghosting).

---

## Per-Model Differences

### 48K Spectrum (16K, 48K, +, Spanish 48K)

Read keyboard via ULA port `#FE`:

- **Port `#FE`** (any address with A0=0): bits 0-4 = columns of the row(s) selected by A8-A15
- Bit 5: always reads as 1 (not connected)
- Bit 6: EAR input (tape signal)
- Bit 7: always reads as 1 (not connected)

The ULA does the column multiplexing in hardware — software just reads the port. No special timing needed beyond contended-I/O awareness.

### 128K / +2 (grey)

The 128K and +2 (grey) add an **AY-3-8912 sound chip** with two 8-bit I/O ports (port A and port B). The 128K's keyboard is still scanned through the ULA port `#FE`, but two additional hardware features use AY port B:

- **Keypad port**: the 128K's rear keypad connector is wired to AY port B. Reading AY register 14 (port B data) returns the keypad state. Few games used this; the keypad was primarily for the bundled 128K BASIC editor.
- **`#7FFD` paging port**: this isn't keyboard-related, but it shares the I/O space — be careful when scanning the keyboard with A15=0, which can also affect the paging register.

The keyboard itself works identically to the 48K: same matrix, same port `#FE`, same address-line row select.

### +2A / +3

Amstrad changed the keyboard hardware on the +2A and +3. The ULA is replaced by an Amstrad gate array (the "ASIC"), which decodes things differently:

- **Row select still goes through `#FE`** with A8-A15 choosing the row, BUT
- **The +2A/+3 has additional keyboard rows** because the keyboard layout is slightly different (extra keys for the editor, etc.)
- The keyboard scan is therefore a **multi-step process**: read `#FE` for the basic 40 keys, then read a second register for the extended keys
- Software written for the 48K still works because the basic 40-key scan is backward-compatible; only software that needs the extended keys has to know about the difference

For full details see [02_hardware/original/README.md](../../02_hardware/original/README.md).

### Russian clones (Pentagon, Scorpion, etc.)

Most Russian clones keep the 48K-compatible matrix and `#FE` port. Some add extensions:

- **Pentagon 128/512/1024**: same 40-key matrix, scanned via `#FE`. The Pentagon's keyboard is sometimes physically larger (PC-style AT/XT keyboard) but emulates the Spectrum matrix in hardware.
- **Scorpion ZS-256**: includes a ProfROM that adds keyboard shortcuts, but the underlying matrix is standard.
- **Profi**: same.
- **ATM Turbo**: has a PC-style keyboard controller chip that emulates the Spectrum matrix.

The clone convention is that software written for the 48K keyboard Just Works.

### ZX Spectrum Next

The Next emulates the original 48K keyboard matrix in its FPGA, so old software works unmodified. **PS/2 and USB keyboards** are supported via the Next's keyboard controller, which translates PS/2 scan codes into Spectrum matrix reads:

- A PS/2 keyboard plugged into the Next's PS/2 port produces the same `#FE` reads as the membrane keyboard
- The Next also supports **scan-code-based input** for new software via NextReg `0x05` (PS/2 key code register) — but this is opt-in
- For full coverage see [02_hardware/newgen/zx_next_joystick.md](../../02_hardware/newgen/zx_next_joystick.md)


---

## Modern PS/2 Keyboard Adapters

Beyond the Next, several modern hardware platforms add PS/2 keyboard support to the original Spectrum:

### DivMMC / DivIDE with PS/2

The DivMMC and DivIDE storage interfaces include an optional PS/2 keyboard adapter. The keyboard controller is on the interface itself, and writes the scanned key state into a memory-mapped register. Software has to opt in — legacy software still sees the membrane keyboard via `#FE`.

### Harlequin / Sizif / Karabas (modern Spectrum rebuilds)

These FPGA and CPLD-based hardware clones typically include PS/2 keyboard support natively. The PS/2 scan codes are translated to Spectrum matrix reads in hardware, so unmodified software works.

### Standalone PS/2 adapters

Several third-party adapters plug into the Spectrum's expansion port and provide a PS/2 socket. Examples include the **ZX Keyboard Adapter** and various community projects on zx-pk.ru. These typically work by translating PS/2 scan codes to matrix reads and driving the same ULA port (`#FE`) — so software sees no difference.

### PS/2 protocol primer (for hardware hackers)

If you're building your own adapter, the PS/2 protocol is straightforward:

- **Connector**: 6-pin mini-DIN (PS/2); only 4 pins used: +5V, GND, DATA, CLK
- **Electrical**: open-collector, idle high, both ends can pull low
- **Protocol**: 11 bits per scan code — 1 start bit (0), 8 data bits (LSB first), 1 parity (odd), 1 stop (1)
- **Direction**: device-to-host by default; host can also send commands to the device (e.g., reset, set LEDs)
- **Scan codes**: set 2 (the standard set used by all PS/2 keyboards). Make code on key press, break code (`F0` prefix) on key release
- **Timing**: CLK frequency 10-16.7 kHz; one scan code takes about 1 ms

An AVR/PIC/STM32 microcontroller reads the PS/2 codes, looks up the corresponding Spectrum matrix intersection in a lookup table, and pulls the appropriate column line low via open-collector outputs when the corresponding row is selected by A8-A15. Total parts cost: ~$5.

For a worked example with code, see the **retro-cia-spectrum-ps2** project on GitHub (or similar community projects on zx-pk.ru).

---

## Common Game Input Patterns

### Debouncing

Mechanical keys bounce — they make and break contact several times over ~5 ms before settling. Without debouncing, a single keypress can register as 5-10 presses. The standard pattern is to scan the keyboard once per frame (50 Hz on PAL, so 20 ms between scans) and accept a keypress only if it persists across two consecutive scans:

```z80
; Pseudo-code: debounced key read
; KEYSTATE holds the current scan, PREV holds the previous scan
; A key is "registered" only when it goes from 0->1 in PREV->KEYSTATE
scan_debounced:
        ; ...scan the keyboard into KEYSTATE...
        LD   HL, KEYSTATE
        LD   DE, PREV
        LD   B, 5                ; 5 bytes = 40 keys
debounce_loop:
        LD   A, (DE)             ; previous state
        AND  A                   ; bit was set?
        JR   NZ, was_pressed     ; yes, skip (waiting for release)
        LD   A, (HL)             ; current state
        AND  A                   ; bit set now?
        JR   NZ, register_press  ; transition from released to pressed
was_pressed:
        ; ... copy KEYSTATE to PREV ...
        DJNZ debounce_loop
        RET
register_press:
        ; ... handle key press ...
```

The exact debounce scheme depends on the game. Some games accept any press (no debounce), some require a 2-frame settle, some require the key to be held for 3+ frames before accepting (avoids accidental taps).

### Auto-repeat

For text input, auto-repeat is desirable. The standard pattern:

1. Key is pressed: register immediately, start a "repeat delay" counter (e.g., 30 frames = 600 ms)
2. Counter expires and key still pressed: register another press, start a faster "repeat rate" counter (e.g., 4 frames = 80 ms)
3. Key released: reset all counters

The ROM's editor uses essentially this scheme — see [rom_48k.md#editor](../../04_operating_systems/rom_48k.md).

### Redefine-keys menus

The 1980s convention: present the user with a list of "actions" (UP, DOWN, LEFT, RIGHT, FIRE) and ask them to press a key for each. The pressed key's matrix position is then stored in a lookup table. Modern alternative: just support all the standard schemes (QAOP, CS, Kempston, Cursor) and let the user pick from a menu.

### Multi-input games

For two-player games with one keyboard, the convention is **Player 1 = left half (Q-T, A-G)**, **Player 2 = right half (Y-P, H-L)**, with each player's keys chosen to avoid ghosting within their own set. Two-player keyboard games became rare once joysticks became standard.

---

## Common Pitfalls

1. **`IN A,(n)` vs `IN A,(C)`**: `IN A,(n)` puts A on A8-A15, not B. If you use `IN A,(#FE)` thinking it reads row 0, it actually reads the row selected by the current accumulator value. Always use `IN A,(C)` with B set to the desired row select. (Both forms work for "any key" scans because the row doesn't matter — but the bad habit will bite you on row-specific scans.)

2. **The half-row bit order**: digits 1-5 are on row A11 with bit 0 = "1" (so `#F7FE` returns bit 0 = key 1). Digits 6-0 are on row A12 with bit 0 = "0" (so `#EFFE` returns bit 0 = key 0). The bit order is **reversed** between the two digit rows. If your code assumes "bit 0 is the leftmost digit", it'll be wrong on one of the two rows.

3. **Contended I/O timing**: port `#FE` lives on the ULA, and reads to it during the screen-draw period take longer than during vertical blank. Code that scans the keyboard in tight loops can desync if it doesn't account for contention. See [05_development/03_memory_and_io/contention_model.md](../../05_development/03_memory_and_io/contention_model.md).

4. **Race with the ROM's INT handler**: the 48K ROM's interrupt handler reads the keyboard on every frame (50 Hz). If your code is in IM1, the ROM's KEY-SCAN runs every frame and consumes key presses from the system variable `LASTK` at `#5C08`. If your code is in IM2 or has DI enabled, the ROM's KEY-SCAN doesn't run, and you have to read the keyboard yourself. See [05_development/04_interrupts/interrupt_programming.md](../../05_development/04_interrupts/interrupt_programming.md).

5. **Keyboard reading from timing-critical loops**: if you scan the keyboard inside a cycle-counted effect (raster racing, multicolor), the contended-I/O delay can vary by ~2 T-states depending on the raster position, breaking your timing. Either scan outside the effect or compensate.

6. **The CAPS SHIFT and SYMBOL SHIFT are just keys**: many programmers think of them as special modifier inputs. They're not — they're matrix positions like any other. You can read them with `BIT 0, A` after `IN A,(#FEFE)` (CAPS) or `BIT 1, A` after `IN A,(#7FFE)` (SYMBOL). Many games use CAPS SHIFT as a fire button.

7. **EAR bit interference**: bit 6 of port `#FE` returns the EAR (tape input) signal, not a keyboard column. If you forget to mask with `AND #1F`, you'll see random bits set from the tape input even when no keys are pressed. Always mask.

8. **Don't read port `#FE` with all of A8-A15 low** if you have a joystick interface installed (Kempston at `#1F`, Cursor at the matrix rows). With A8-A15 all low, you might activate the joystick's address decode as well as the ULA's, causing bus contention.

9. **128K paging port aliasing**: on the 128K, writing to port `#7FFD` pages RAM banks. Reading from `#FE` with A15=0 also aliases to the paging register in some configurations — be careful when writing keyboard scan code that the high byte of BC doesn't accidentally match a paging register pattern.

10. **PS/2 keyboards on the Next can produce different scan codes**: if your Next software uses NextReg `0x05` (PS/2 raw scan code), you need a Set 2 scan code table. If you read via `#FE` (the legacy matrix port), no translation needed.

---

## Cross-References

- [02_hardware/original/keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md) — Hardware matrix reference (the companion article)
- [04_operating_systems/rom_48k.md](../../04_operating_systems/rom_48k.md) — ROM KEY-SCAN, KEY-TEST, KEY-INPUT routines
- [joystick.md](joystick.md) — Joystick interfaces piggyback on the matrix
- [02_hardware/original/ula_architecture.md](../../02_hardware/original/ula_architecture.md) — Port `#FE` decode and column multiplexer
- [02_hardware/original/README.md](../../02_hardware/original/README.md) — Per-model hardware overview (including +2A/+3 keyboard changes)
- [02_hardware/newgen/zx_next_joystick.md](../../02_hardware/newgen/zx_next_joystick.md) — Next keyboard/joystick implementation
- [05_development/03_memory_and_io/memory_and_io_48k.md](../../05_development/03_memory_and_io/memory_and_io_48k.md) — Port-level usage in context
- [05_development/03_memory_and_io/contention_model.md](../../05_development/03_memory_and_io/contention_model.md) — Why `#FE` reads take variable time
- [05_development/04_interrupts/interrupt_programming.md](../../05_development/04_interrupts/interrupt_programming.md) — Race between ROM KEY-SCAN and your ISR
- [10_references/io_port_map.md](../../10_references/io_port_map.md) — Canonical port reference

---

## Primary Sources

1. **Chris Smith** — *The ZX Spectrum ULA: An Anatomical Guide* (2010). The definitive reference for port `#FE` internals, column multiplexing, and the address-line row select mechanism.
2. **Sinclair Research** — *ZX Spectrum BASIC Programming* (1982), chapter on the keyboard. Reproduced widely.
3. **The Complete Spectrum ROM Disassembly** — KEY-SCAN, KEY-TEST, KEY-INPUT, KEY-DONE routines documented at `#02BB`-`#031E` in the 48K ROM.
4. **Ian Logan & Frank O'Hara** — *The Spectrum ROM Disassembly* (1983). Dr. Ian Logan's annotated ROM listing.
5. **Geoff Wearmouth** — ROM disassembly pages. `http://www.wearmouth.demon.co.uk/`.
6. **zx-pk.ru** threads on PS/2 adapters — community-developed hardware projects with schematics and AVR/STM32 firmware.
7. **ZX Spectrum Next official documentation** — `zxnext.io`, especially the NextReg `0x05` and `0x08` documentation for PS/2 keyboard.
