[← Home](../../README.md) · [Peripherals](README.md)

# Mouse Interfaces — Kempston Mouse, AMX Mouse, and Modern Successors

## Overview

The ZX Spectrum has no built-in mouse. Two main third-party mouse interfaces were sold in the 1980s:

- **Kempston Mouse** (1985) — uses three I/O ports (`#FBDF`, `#FFDF`, `#FADF`) to expose 8-bit X position, 8-bit Y position, and button state. Uses quadrature encoding in hardware and exposes **absolute position counters** to software
- **AMX Mouse** (1985, by Advanced Memory Systems) — uses a Z80 PIO chip on the interface, with ports at `#1F`/`#3F`/`#5F`/`#7F` for motion (1 bit per read) and `#DF` for buttons. Came bundled with AMX Pagemaker (a desktop-publishing app)

In the 1990s and beyond, several other mouse interfaces appeared:
- **Kempston Mouse Turbo** (2008, by Velesoft) — modern PS/2 mouse version of the original Kempston protocol; uses ports `#FADF`/`#FBDF`/`#FFDF` to emulate the original plus extra ports for scroll wheel
- **K-MOUSE Turbo / K-MOUSE 2008** — community PS/2 mouse interface supporting both Kempston and AMX protocols simultaneously
- **ZX Spectrum Next** — built-in PS/2 mouse support that emulates the Kempston Mouse protocol
- **DivMMC / DivIDE with PS/2** — modern storage interfaces often include PS/2 mouse support

This article covers the two original protocols (Kempston and AMX), the modern PS/2-based successors, and how to write Spectrum software that supports mice. For the canonical port reference, see [10_references/io_port_map.md#kempston-mouse](../../10_references/io_port_map.md#kempston-mouse). For the snapshot-format representation of mouse state, see [03_io/snapshots/szx_format.md](../snapshots/szx_format.md) (`MOUS` block).

---

## Why Two Standards?

The Kempston and AMX mice launched within months of each other in 1985. They use **fundamentally different programming models**:

| Aspect | Kempston Mouse | AMX Mouse |
|--------|----------------|-----------|
| Position reporting | Absolute (8-bit X and Y counters in hardware) | Relative (1 bit per axis per read — software must poll) |
| Hardware complexity | Quadrature decoder chip + 8-bit counters | Z80 PIO chip + diode-resistor decode |
| Software complexity | Trivial — read X, read Y, read buttons | Complex — must poll motion bits at >50 Hz to track direction |
| Port addresses | `#FADF`/`#FBDF`/`#FFDF` | `#1F`/`#3F`/`#5F`/`#7F` + `#DF` |
| Conflict with joystick? | No (different ports than Kempston joystick at `#1F`) | **Yes** — `#1F` aliases the Kempston joystick port |
| Bundled software | Generic driver libraries | AMX Pagemaker, AMX Art, AMX Script |

Kempston's design philosophy was "**make software easy**": put the quadrature decoding in hardware, give software a single-byte X and Y. AMX's philosophy was "**make hardware cheap**": use a standard PIO chip, let software do the work. Kempston won; the Spectrum Next emulates the Kempston protocol natively, and most modern software that supports a mouse supports only Kempston.

---

## Quadrature Encoding (Background)

Both original mice use **quadrature encoding** for motion detection. Each axis (X and Y) has two sensors (call them A and B) that produce square waves 90° out of phase as the mouse moves. The direction of motion is determined by which signal leads the other:

```
       ┌───┐   ┌───┐   ┌───┐      Moving right:
    A: ┘   └───┘   └───┘   └──    A leads B by 90°
                                       ┌───┐   ┌───┐
    B: ────────────────────────┘   └───┘   └──
                                       └───┘   ┌───┐   ┌───┐
    A: ────────────────────────┐   ┌───┘   └──
                                   ┌───┐   ┌───┐   ┌───┐
    B: ────────────────────────┘   └───┘   └───┘   └──
       Moving left: B leads A by 90°
```

Each sensor produces ~50-200 pulses per inch of mouse motion. The interface's job is to count these pulses in the right direction:

- Kempston Mouse: a dedicated quadrature decoder chip (HP-QED or similar) counts the pulses into an 8-bit up/down counter. Software just reads the counter.
- AMX Mouse: the Z80 PIO's input pins receive the raw A/B signals. Software must poll frequently enough to track the direction itself.

If software polls too slowly on the AMX, it misses pulses — the mouse appears to "stick" or "jump backward". The Kempston has no such issue because the counting happens in hardware.

---

## Kempston Mouse (1985)

### Hardware

The Kempston Mouse interface is a small PCB containing:

- **A quadrature decoder chip** (typically an HP-QED or CMOS equivalent) that converts the mouse's two-phase signals into up/down counts
- **Two 8-bit counters** (one per axis) that hold the current X and Y position
- **A 9-pin D-sub connector** for the mouse itself (NOTE: pinout is **unique to Kempston**, not Amiga/Atari compatible)
- **A tri-state output buffer** that drives the CPU data bus when one of the three I/O ports is read

The interface passes the edge connector through, so further peripherals can stack behind it.

### ⚠️ Connector warning

The original Kempston mouse has a **unique pinout** — it is NOT compatible with Amiga, Atari ST, or Datel mice. Plugging an Amiga or Atari mouse into the Kempston interface **will fry the mouse** because the +5V pin is on a different line. Always check the mouse type before plugging in.

### Port map

| Port | Address (binary) | Direction | Function |
|------|------------------|-----------|----------|
| `#FBDF` | `xxxxx011xx0xxxxx` | Read | X position (8-bit counter) |
| `#FFDF` | `xxxxx111xx0xxxxx` | Read | Y position (8-bit counter) |
| `#FADF` | `xxxxxx10xx0xxxxx` | Read | Buttons |

**X position** (`#FBDF`): an 8-bit value representing horizontal position. The counter **rolls over** at 0/255 — moving right past 255 wraps to 0, moving left past 0 wraps to 255. Software must compute deltas between reads to track motion across multiple revolutions.

**Y position** (`#FFDF`): same as X but for vertical motion.

**Buttons** (`#FADF`):

```
Bit 7  6   5   4   3   2   1   0
 Whl whl whl whl  1   MB  MR  ML
```

- Buttons are **active-low over an `#FF` base** — a *pressed* button reads as **0**, idle reads 1 (the opposite of the "active-high" claim that circulates; verified against the port guides and the ZX Evolution FPGA, which returns `{wheel, 1'b1, buttons}`)
- **Bit 0 = Left, bit 1 = Right, bit 2 = Middle** — the assignment per Black_Cat's port guide (BC Info Guide #4) and the KB port map. Beware: two widely used emulators (ZXMAK2, zxsp's header) swap D0/D1 to right/left; software compared against them may encode the opposite order
- **Bit 3 reads as a constant 1** on the reference implementations
- **Bits 7-4 = scroll wheel counter** where a wheel exists (upper nibble of the same register — not a separate port; without a wheel they read as part of the `#FF` base)

### Reading the mouse (Kempston)

```z80
read_kempston_mouse:
        LD   BC, #FBDF
        IN   A, (C)              ; A = X position (0-255, wraps)
        LD   (MOUSE_X), A

        LD   BC, #FFDF
        IN   A, (C)              ; A = Y position (0-255, wraps)
        LD   (MOUSE_Y), A

        LD   BC, #FADF
        IN   A, (C)              ; A = #FF base: 0 bit = pressed
        CPL                      ; -> 1 = pressed, wheel nibble inverted
        AND  #07                 ; buttons only
        LD   (MOUSE_BTN), A
        RET
```

### Per-model address decoding — there is no single mask

The interface is a card; the machine is a bus, and **each machine's decoder answers a different subset of the address lines**. The canonical decode qualifies on **A9 = 1, A5 = 0**, then A8 separates buttons from axis and A10 separates X from Y — every other line is a don't-care, giving 8192 mirrors for the button port and 4096 per axis (the button register even answers at both `#FADF` and `#FEDF`, because A10 is not decoded when A8 = 0). BC Info Guide #4 documents a second flavour, the **"USSR" variant**: it drops A9 entirely, adds A7 = 1 and **A0 = 1**, and therefore answers only on odd addresses (2048 mirrors per port):

| Variant | Buttons | X | Y |
|---|---|---|---|
| Standard | A9=1, A8=0, A5=0 | A10=0, A9=1, A8=1, A5=0 | A10=1, A9=1, A8=1, A5=0 |
| USSR | A10=0, A8=0, A7=1, A5=0, **A0=1** | A10=0, A8=1, A7=1, A5=0, A0=1 | A10=1, A8=1, A7=1, A5=0, A0=1 |

> [!WARNING]
> **The ZX Evolution decodes more strictly than the original hardware**: its FPGA requires the whole low byte `#DF` (`KMOUSE = 8'hDF`), where the original decodes only A5. A program that uses a mirrored mouse port works on a Pentagon and fails on a ZX-Evo. Per BC Info Guide #4's model legend, the built-in mouse is documented for the ZX Spectrum, KAY-1024SL, Pentagon 128 and Profi; on Scorpion, ATM Turbo and Pentagon-1024SL it is an add-on card whose decode follows the card.

Two more verified bus-level behaviors:

- **The Kempston joystick collision is structural.** The joystick decodes A5 = 0 alone on original hardware — and the mouse ports (`#DF` low byte) sit inside that window. Severity is per-model: the KAY-1024SL joystick decodes **A0 alone** (it answers every odd port, mouse ports included); the Pentagon-1024SL decodes A5 = 0 + A0 = 1, which the mouse ports also satisfy. Robust joystick handlers must skip the three mouse addresses.
- **TR-DOS gating varies by machine**: ZXMAK2 suppresses the mouse while TR-DOS is paged; Xpeccy registers it non-DOS-only for Pentagon/Scorpion/ATM but DOS-agnostic for Pentevo. Software probing from inside TR-DOS may see different results per machine.

### Presence detection — there is no presence bit

Software infers the mouse from the ports themselves: the classic heuristic compares X against Y and treats **equal** values as "no mouse fitted". Consequently an implementation must reset the counters to **two different, non-zero** values (the reference emulator uses 31 and 85) — a zero-initialized mouse reads as absent.

### Tracking position (the rollover problem)

Because X and Y are 8-bit counters that wrap, software can't just store "current X" — it must compute the delta from the previous read and accumulate that into a higher-precision variable:

```z80
; Update MOUSE_X_HI:MOUSE_X_LO from the current 8-bit hardware read
update_mouse_x:
        LD   BC, #FBDF
        IN   A, (C)
        LD   E, A                 ; E = new X
        LD   A, (MOUSE_HW_X)      ; last hardware X
        LD   (MOUSE_HW_X), E      ; save new as last
        SUB  E                    ; A = old - new
        ; A is now the negative delta (signed)
        ; Add this to the 16-bit MOUSE_X
        ; If A > 127, mouse moved backward (treat as negative)
        ; If A <= 127, mouse moved forward (treat as positive)
        CP   128
        JR   C, forward
        ; backward: A is actually 256-A in the other direction
        NEG
        NEG
        ; ... (signed add to MOUSE_X_HI:MOUSE_X_LO)
        RET
forward:
        ; ... (positive add to MOUSE_X_HI:MOUSE_X_LO)
        RET
```

This is the standard idiom. Most Kempston mouse software uses 16-bit (or 32-bit) software positions and updates them from the 8-bit hardware deltas each frame.


---

## AMX Mouse (1985)

### Hardware

The AMX Mouse interface uses a **Z80 PIO chip** (a general-purpose parallel I/O chip with two 8-bit ports) plus a few diodes and pull-up resistors. The mouse itself is a 3-button bus mouse with a 20-pin TTL interface. The interface also includes a 25-pin Centronics-style parallel port passthrough.

The use of a PIO chip means the AMX interface is **a more general peripheral than just a mouse** — software can repurpose the PIO's pins for other I/O. In practice, no software ever did this; the AMX was always used as a mouse.

### Port map

The AMX interface responds to a block of addresses with `A7=0`:

| Port | Address | Decoding | Function |
|------|---------|----------|----------|
| `#1F` | `0001 1111` | A5=0, A6=0, A7=0 | Left/Right motion (bit 0 = X quadrature signal) |
| `#3F` | `0011 1111` | A5=0, A6=1, A7=0 | Up/Down motion (bit 0 = Y quadrature signal) |
| `#5F` | `0101 1111` | A5=1, A6=0, A7=0 | (used for PIO control) |
| `#7F` | `0111 1111` | A5=1, A6=1, A7=0 | (used for PIO control) |
| `#DF` | `1101 1111` | (special decode) | Buttons |

**Motion ports** (`#1F`, `#3F`): each read returns the **current state of the quadrature signal** in bit 0. The other bits are undefined. Software must poll this port at >100 Hz to detect each phase change and reconstruct the count.

**Button port** (`#DF`):

```
Bit 7  6   5   4   3   2   1   0
 LMB  MMB RMB ?   ?   ?   ?   ?
```

- Bit 7 = Left Mouse Button (**0 = pressed**, active-low)
- Bit 6 = Middle Mouse Button (0 = pressed)
- Bit 5 = Right Mouse Button (0 = pressed)
- Bits 0-4: undefined

Buttons are **active-low** — opposite convention from the Kempston Mouse.

### Reading the AMX mouse

The motion tracking requires high-frequency polling. The standard pattern is to read `#1F` and `#3F` from an interrupt service routine running at 100-200 Hz, comparing each new bit 0 to the previous bit, and reconstructing the direction via a state machine:

```z80
; AMX mouse ISR (called at ~200 Hz from a custom IM2 vector)
; Tracks X and Y motion into 16-bit software counters
amx_isr:
        ; ... save registers ...
        LD   A, (PREV_X_BIT)
        LD   B, A                 ; B = previous X bit
        LD   C, #1F
        IN   A, (C)               ; A bit 0 = new X bit
        AND  1
        LD   (PREV_X_BIT), A
        CP   B                    ; same as before?
        JR   Z, no_x_change       ; no edge
        ; Edge detected — check Y bit to determine direction
        IN   A, (#3F)
        AND  1
        ; If Y bit == X bit, mouse moved one direction; else other
        ; (Per quadrature encoding: phase relationship determines direction)
        ; ... update MOUSE_X ...
no_x_change:
        ; ... same for Y axis ...
        ; ... restore registers, EI, RETI ...
```

This is significantly more complex than the Kempston equivalent. The AMX driver library bundled with AMX Pagemaker does all this in ~1 KB of Z80 code.

### Software support

The AMX Mouse shipped with:
- **AMX Pagemaker** — a desktop publishing app (the killer app for the AMX)
- **AMX Art** — a drawing program
- **AMX Script** — a macro language
- A general driver library that other software could call

Few third-party applications supported the AMX; the Kempston Mouse had broader software support despite the AMX having a strong bundled suite.

### Conflict with Kempston joystick

The AMX Mouse's port `#1F` **aliases the Kempston joystick port**. If both devices are installed, reading `#1F` returns the OR of the joystick bits and the AMX motion bit. The Kempston joystick returns bits 0-4 as direction/fire; the AMX motion bit is bit 0. A joystick press in direction "right" (bit 0 set in Kempston joystick) would also be interpreted as "X quadrature signal high" by the AMX driver.

In practice, you can't have both the AMX Mouse and a Kempston joystick installed simultaneously. Choose one or the other.

---

## Modern PS/2-Based Successors

### Kempston Mouse Turbo (2008)

Velesoft's **Kempston Mouse Turbo 2008** is the modern de-facto standard for PS/2 mouse on the Spectrum. It:

- Accepts a standard PS/2 mouse (the kind found in every PC from 1987 to 2010)
- Translates PS/2 motion data into the Kempston Mouse protocol
- Emulates ports `#FADF`/`#FBDF`/`#FFDF` exactly, so original Kempston software works unmodified
- Adds **extra ports** for PS/2-specific features:
  - Scroll wheel: read at a fourth port (interface-specific)
  - Mouse sensitivity: configurable via a magic port write
- Is widely emulated in modern FPGA clones (Sizif, harlequin, Karabas, Next)

The original 2008 hardware is rare, but the firmware design has been cloned into many modern interfaces. The DivMMC and DivIDE interfaces often include a Kempston Mouse Turbo compatible PS/2 port.

### K-MOUSE Turbo / K-MOUSE 2008

A more advanced community design that **simultaneously emulates** the Kempston Mouse AND the AMX Mouse, so software written for either protocol works. The hardware translates PS/2 scan codes into both port-address sets. This is the gold standard for new software development.

### ZX Spectrum Next mouse

The Next's FPGA core includes a Kempston Mouse emulator that takes input from the Next's PS/2 port. Software sees the standard `#FADF`/`#FBDF`/`#FFDF` ports; no Next-specific code is needed for legacy mouse software.

For new Next software, the Next also exposes raw PS/2 mouse packets via NextReg `0x05` (PS/2 data) — but this is opt-in and rarely used.

### PS/2 mouse protocol primer

For hardware hackers building adapters, the PS/2 mouse protocol is:

- **Connector**: 6-pin mini-DIN, same as PS/2 keyboard
- **Electrical**: open-collector, idle high
- **Protocol**: 11 bits per byte (start, 8 data LSB first, parity odd, stop)
- **Mouse reporting mode**: by default, the mouse sends a 3-byte packet on every motion event:
  - Byte 1: button state (bit 0 = left, bit 1 = right, bit 2 = middle), overflow bits (3-4 X/Y), sign bits (5 X, 6 Y), always-set bit (7)
  - Byte 2: X delta (signed 8-bit)
  - Byte 3: Y delta (signed 8-bit)
- **Init sequence**: host sends `0xFF` (reset) → mouse responds `0xFA, 0xAA, 0x00`; host sends `0xF4` (enable reporting) → mouse responds `0xFA`

A microcontroller translates these PS/2 packets into the Kempston protocol by maintaining internal 8-bit X and Y counters and updating them with each packet's delta. Total parts cost: ~$5 plus a PS/2 socket.


---

## Common Pitfalls

1. **Don't plug an Amiga or Atari mouse into a Kempston interface.** The +5V pin is on a different line; you will fry the mouse. Always check the connector labeling.

2. **Kempston X/Y counters roll over at 0/255.** Software that treats the hardware X as the absolute screen position will be wrong after a few inches of motion. Always track deltas in a 16-bit (or larger) software variable.

3. **AMX motion polling requires >100 Hz.** If your code is in DI for more than 10 ms (e.g., during a disk I/O operation), the AMX driver will miss pulses and lose track of position. The Kempston has no such issue.

4. **Button polarity differs between protocols.** Kempston buttons are active-high (1 = pressed); AMX buttons are active-low (0 = pressed). Don't mix them up.

5. **AMX `#1F` aliases the Kempston joystick port.** If both devices are installed, joystick reads will be corrupted by AMX motion bits and vice versa. Choose one device.

6. **The Kempston Mouse `#FADF` button port and the Kempston joystick `#1F` port are NOT the same thing.** Don't confuse them. The joystick port is `#001F`; the mouse button port is `#FADF`. They have different addresses because A15-A5 differ.

7. **Kempston Mouse middle button is rarely supported.** The original Kempston Mouse had only 2 buttons; bit 2 of `#FADF` read as 1 (idle) on those units. The Kempston Mouse Turbo and most modern implementations support a middle button, but old software may not check it.

8. **PS/2 mouse on the Next is opt-in for new software.** Legacy software sees the Kempston Mouse ports; new software can use NextReg `0x05` for raw PS/2 access. Don't use both at once.

9. **Cursor-drawing software should use double-buffering.** A mouse cursor drawn directly to the screen will tear as the cursor moves; the standard pattern is to keep a clean copy of the screen background and XOR the cursor on each frame.

10. **Quadrature mice accumulate noise.** If the mouse is bumped or vibrated, the counters may drift. Software should provide a "recalibrate" / "warp cursor" option.

---

## When to Use a Mouse (Today)

| Use case | Recommendation |
|----------|----------------|
| Writing new GUI software for the Spectrum | Target the **Kempston Mouse** protocol — it has the widest emulator support and is the easiest to program |
| Running original AMX Pagemaker / AMX Art | Real AMX hardware, or K-MOUSE Turbo (which emulates AMX), or an emulator with AMX support |
| Modern hardware (Spectrum Next, harlequin, etc.) | Just plug in a PS/2 mouse — the hardware translates to Kempston protocol |
| Cursor-based game (e.g., point-and-click adventure) | Target Kempston Mouse; test with mouse + joystick fallback |
| Drawing application | Target Kempston Mouse for compatibility; add AMX support as a fallback if you have ROM space |

---

## Comparison Matrix

| Feature | Kempston Mouse | AMX Mouse | Kempston Mouse Turbo | K-MOUSE Turbo |
|---------|----------------|-----------|----------------------|---------------|
| Year | 1985 | 1985 | 2008 | 2008+ |
| Original/Modern | Original | Original | Modern (PS/2) | Modern (PS/2) |
| Position model | 8-bit absolute | 1-bit relative (poll) | 8-bit absolute | 8-bit absolute + 1-bit relative |
| Buttons | 2 | 3 | 3 + scroll | 3 + scroll |
| Ports | `#FBDF`/`#FFDF`/`#FADF` | `#1F`/`#3F`/`#DF` | `#FBDF`/`#FFDF`/`#FADF` + extras | All of the above |
| Conflict with joystick | No | **Yes** (`#1F`) | No | No |
| Software complexity | Trivial | Complex (ISR polling) | Trivial | Trivial |
| Bundled software | Driver libs | AMX Pagemaker, Art, Script | — | — |
| Emulator support | Universal | xFuse, ZEsarUX | Most modern emulators | Most modern emulators |
| Real hardware today | Rare | Rare | Modern clones | Modern clones |

---

## Modern Analogies

- **The Kempston Mouse ≈ a modern USB mouse with absolute positioning drivers.** Both expose a simple "current X, current Y" API; the user-space code doesn't care about the underlying motion detection.
- **The AMX Mouse ≈ a raw optical encoder.** Software gets the sensor state and has to do everything else itself — including the hard parts (debouncing, direction detection, missing-pulse recovery).
- **The Kempston Mouse Turbo ≈ a USB-to-PS/2-to-ZX Spectrum adapter chain.** Each translation layer adds overhead but lets modern hardware talk to old software transparently.
- **The 8-bit rollover counter ≈ a one-byte position counter in a game controller.** Software has to keep its own high-precision position to handle the inevitable wraps.
- **The AMX/Kempston joystick port clash ≈ the original IBM PC's IRQ conflicts.** Two peripherals claiming the same I/O resource and software having to choose one.

---

## Cross-References

- [10_references/io_port_map.md#kempston-mouse](../../10_references/io_port_map.md) — Canonical port reference
- [joystick.md](joystick.md) — Kempston joystick uses port `#1F`, conflicting with AMX Mouse
- [03_io/snapshots/szx_format.md](../snapshots/szx_format.md) — `MOUS` block records mouse state in `.szx` snapshots
- [03_io/snapshots/z80_format.md](../snapshots/z80_format.md) — Kempston Mouse state in `.z80` v3 snapshots
- [02_hardware/newgen/zx_next.md](../../02_hardware/newgen/zx_next.md#joystick-system) — Next's PS/2 mouse and joystick implementation
- [09_toolchain/cross_platform_toolchain.md](../../09_toolchain/cross_platform_toolchain.md) — Real-mouse testing in cross-platform development
- [05_development/04_interrupts/interrupt_programming.md](../../05_development/04_interrupts/interrupt_programming.md) — High-frequency ISR for AMX polling
- [keyboard.md](keyboard.md) — PS/2 protocol details shared with keyboard adapters

---

## Primary Sources

1. **Sinclair Wiki** — Kempston Mouse article. `https://sinclair.wiki.zxnet.co.uk/wiki/Kempston_Mouse`.
2. **Sinclair Wiki** — AMX Mouse article, with PCB layout, Z80 PIO decode, and button port analysis. `https://sinclair.wiki.zxnet.co.uk/wiki/AMX_Mouse`.
3. **World of Spectrum peripherals FAQ** — `worldofspectrum.org/faq/reference/peripherals.htm`.
4. **Velesoft** — Kempston Mouse Turbo 2008 documentation. `velesoft.speccy.cz/kmturbo2008-cz.htm`.
5. **Benophet Internet** — Kempston Mouse Turbo documentation, including PS/2 wiring. `benophetinternet.nl/hobby/kmt/`.
6. **k1.spdns.de** — Kempston Mouse Interface technical page. `k1.spdns.de/Vintage/Sinclair/82/Peripherals/Mouse Interfaces/Kempston Mouse Interface/`.
7. **Adam Adamowicz / Computing History** — AMX Mouse article, with photo of the AMX Pagemaker suite. `computinghistory.org.uk/det/19979/AMX-Mouse/`.
8. **ZX Spectrum Next official documentation** — `zxnext.io`, PS/2 mouse emulation.
