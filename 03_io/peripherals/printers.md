[← Home](../../README.md) · [Peripherals](README.md)

# Printers — ZX Printer, Centronics Adapters, and Soviet SM640/SM646

## Overview

The ZX Spectrum's printer ecosystem divides into three eras:

1. **Sinclair's own ZX Printer** (1981, originally for the ZX81 but compatible with the Spectrum) — a spark printer using metallized paper, decoded at any I/O port with `A2=0`
2. **Third-party Centronics/parallel port adapters** (1983-1988) — Kempston, DK'Tronics, and others sold interfaces that connected the Spectrum to standard parallel-port printers (Epson FX-80, Seikosha SP-1000, etc.)
3. **Soviet SM640/SM646 printers** (late 1980s-1990s) — Soviet parallel-port dot-matrix printers used with the Beta 128 interface, requiring driver software

In the modern era, the **Retro-Printer** (a Pi-based emulation system) and various Next-based Centronics drivers preserve the ability to print from Spectrum software to modern printers.

This article covers the ZX Printer's hardware and protocol, the Centronics adapter conventions, the Soviet SM640/SM646 ecosystem, and modern options for printer output. For the BASIC `COPY`/`LPRINT`/`LLIST` commands, see [04_operating_systems/rom_48k.md](../../04_operating_systems/rom_48k.md#printing). For the +2A/+3's removal of the +9V line that broke ZX Printer compatibility, see [interface2.md](interface2.md).

---

## The ZX Printer (1981)

### What it is

The ZX Printer is a **spark printer** (sometimes called an "electro-erosion" printer). It uses special paper with a thin aluminum coating over a black underlayer. A moving stylus passes a brief electric current through the aluminum, vaporizing it at that point to expose the black underneath. The result is a monochrome (black on silver) image built up pixel by pixel as a rotating drum pulls the paper past the stylus.

This technology is unique to Sinclair's peripherals (also used in the ZX81 printer) — no other home computer manufacturer used it. The advantages:

- **No ink, no ribbon, no toner** — only electricity and special paper
- **Cheap mechanism** — just a motor, a stylus, and a paper-feed drum
- **Fast for text** — about 1 line per second
- **Compact** — fits in a 22 cm × 11 cm × 5 cm case

The disadvantages:

- **Special paper** — the metallized paper was only sold by Sinclair (and later third parties); you couldn't use plain paper
- **Smelly** — the vaporized aluminum produced a characteristic ozone-and-metal odor
- **Low resolution** — about 256×256 pixels per page, equivalent to a 9-pin dot-matrix
- **Not archival** — the paper degraded over decades; many surviving prints are now faded
- **Stylus wear** — the stylus slowly eroded with use, requiring periodic replacement
- **No gray levels** — pure black/white only, no halftones (the stylus can't modulate current)

### Hardware

The ZX Printer contains:

- **A 9V DC motor** (powered from the Spectrum's +9V line on the edge connector — see Pitfall 1 below)
- **A rotating drum** that pulls the paper past the stylus
- **A stylus on a slider** that moves radially across the drum as the drum rotates
- **A small PCB** with port-decode logic and a transistor to switch the stylus current
- **A 34-way edge connector** at the back that plugs directly into the Spectrum's expansion port

The decode logic is simple: respond to any I/O cycle where **A2=0** (so port addresses `#FB`, `#F7`, `#F3`, `#EF`, etc. all work). This intentionally overlaps with the ULA's keyboard port at `#FE`, but with A2=0 instead of A0=0, so the two devices coexist.

### Port layout

Reading and writing the printer use the **same port address** (any address with A2=0), but with **different bit meanings** for read vs. write:

**Read port** (e.g. `IN A,(#FB)`):

| Bit | Meaning |
|-----|---------|
| 7 | **Paper start latch** — set when the stylus reaches the start-of-line position, or when stylus power is turned on. Cleared by any write to the printer port. |
| 6, 5, 4, 3, 2, 1 | Always read as 1 (not connected) |
| 0 | **Next pixel latch** — pulsed when the stylus has advanced one pixel position (~every 250 T-states in fast mode) |

**Write port** (e.g. `OUT (#FB),A`):

| Bit | Meaning |
|-----|---------|
| 7 | **Stylus power** (1 = on, 0 = off) |
| 4 | **Motor power** (0 = run, 1 = stop) |
| 2 | **Motor speed** (0 = fast, 1 = slow; no effect if motor stopped) |
| 1, 0, 3, 5, 6 | Not connected |

**Important**: any write to the printer port **resets both latches** (bit 7 and bit 0 of the read register go to 0). This is how the software acknowledges a latch event.

### The print cycle

The standard print loop, in pseudocode:

```
1. Write bit 4 = 0 (motor run) and bit 2 = 0 (fast mode)
2. Wait for read bit 7 (paper start latch) to go high
3. For each pixel column of the line:
   a. Wait for read bit 0 (next pixel latch) to go high
   b. If the pixel should be black, write bit 7 = 1 (stylus on); else bit 7 = 0 (off)
   c. The write also resets the latch for the next pixel
4. After the last pixel, write bit 4 = 1 (motor stop)
```

The ROM routine `COPY` (called by the BASIC `COPY` command, token code `Z`) implements exactly this loop. The full `COPY` routine is at `#0EAC` in the 48K ROM and is documented in [04_operating_systems/rom_48k.md#printing](../../04_operating_systems/rom_48k.md).

### Software driving code

A minimal Spectrum-side driver to print one line of pixels (256 pixels = 32 bytes) from address `HL`:

```z80
print_256_pixels:
        ; 1. Start the motor in fast mode
        LD   A, #00             ; bit 4=0 (run), bit 2=0 (fast)
        OUT  (#FB), A
        ; 2. Wait for paper start
wait_start:
        IN   A, (#FB)
        RLCA                     ; bit 7 → carry
        JR   NC, wait_start
        ; 3. Print 256 pixels
        LD   B, 32               ; 32 bytes = 256 pixels
print_loop:
        LD   A, (HL)             ; 8 pixels in this byte
        LD   C, 8                ; process each bit
bit_loop:
        RLCA                     ; bit 7 → carry
        PUSH AF
        ; Wait for next-pixel latch
wait_pixel:
        IN   A, (#FB)
        RRCA                     ; bit 0 → carry
        JR   NC, wait_pixel
        ; Write stylus based on the pixel bit
        POP  AF
        LD   A, #80              ; stylus ON
        JR   C, pixel_set
        LD   A, #00              ; stylus OFF
pixel_set:
        OUT  (#FB), A            ; also resets latches
        DEC  C
        JR   NZ, bit_loop
        INC  HL
        DJNZ print_loop
        ; 4. Stop the motor
        LD   A, #10              ; bit 4=1 (stop)
        OUT  (#FB), A
        RET
```

This is essentially what the ROM's COPY routine does, but the ROM also handles screen addressing (extracting pixel bytes from the screen memory in the right order), border color, and pagination. See [04_operating_systems/rom_48k.md#printing](../../04_operating_systems/rom_48k.md).

### BASIC commands

The 48K ROM provides three printing commands:

| Command | Token | Action |
|---------|-------|--------|
| `COPY` | `Z` (extended-SHIFT + Z) | Print the current screen image (pixel data only; attributes are ignored) |
| `LPRINT` | extended-SHIFT + C | Print a line of text (like PRINT but to stream 3, the printer) |
| `LLIST` | extended-SHIFT + V | List the current BASIC program to the printer |

These commands work because the ROM has a "printer" stream (stream 3) hooked into the channel system. See [04_operating_systems/rom_48k.md#channels](../../04_operating_systems/rom_48k.md) for the channel/stream mechanism.

### The Alphacom 32

The **Alphacom 32** is a third-party printer compatible with ZX Printer software (responds to the same port `#FB` protocol, uses the same BASIC commands) but uses **thermal paper** instead of metallized paper. The thermal paper is more pleasant to handle, doesn't smell, and produces slightly higher contrast. The Alphacom 32 also has its own power supply (no reliance on the Spectrum's +9V line), which means it works on the +2A/+3 (where the +9V line was removed).

### Compatibility

| Spectrum model | ZX Printer | Alphacom 32 |
|----------------|------------|-------------|
| 16K, 48K, 48K+ | ✅ Direct | ✅ Direct |
| 128K (toastrack) | ✅ Direct | ✅ Direct |
| +2 (grey) | ✅ Direct | ✅ Direct |
| +2A, +2B | ❌ No +9V line | ✅ (self-powered) |
| +3, +3B | ❌ No +9V line | ✅ (self-powered) |
| Pentagon, Scorpion | ❌ | ❌ (no ZX Printer protocol) |

For the +2A/+3, an external +9V power supply wired into the edge connector can revive the original ZX Printer, but most users simply bought an Alphacom 32 or a Centronics adapter.

---

## Centronics / Parallel Port Adapters

By 1984-85, the limitations of the ZX Printer (special paper, low resolution, slow speed) led most serious users to standard parallel-port printers like the Epson FX-80, Seikosha SP-1000, Mannesmann Tally, and Star LC-10. These printers use the **Centronics parallel interface** — an industry standard since the 1970s, with a 36-pin Amphenol connector on the printer side and a 25-pin D-sub on the host side.

The Spectrum has no built-in parallel port, so a third-party adapter is required. Several companies sold these:

| Adapter | Year | Port addresses | Notes |
|---------|------|----------------|-------|
| **Kempston Centronics Interface** | 1984 | `#0F` (data), `#1F` (status) | Includes a pass-through edge connector; widely supported |
| **DK'Tronics Printer Interface** | 1985 | `#0F` (data), `#1F` (status) | Software-compatible with the Kempston interface |
| **Romantic Robot Multiprint** | 1984 | Various | Predecessor to the Multiface; supports screen-print and text modes |
| **ZX Spectrum+ 2 (grey) built-in** | 1987 | `#0F` data, RS-232 via AY | Amstrad added Centronics support in firmware |
| **Beta 128 with printer adapter** | 1985+ | `#0F` data, `#1F` status | Soviet convention; works with SM640/SM646 |

### Standard Centronics protocol

The Centronics protocol has been stable since 1970 and works the same on every printer:

- **Data lines**: 8 parallel data bits (D0-D7), set up by the host
- **`/STROBE`**: host pulses this low for >0.5 µs to indicate "data is valid, please read"
- **`/ACK`**: printer pulses low to acknowledge receipt of the byte
- **BUSY**: printer holds high while not ready to accept another byte (paper-out, buffer full, etc.)
- **PE (Paper Empty)**: high when the printer is out of paper
- **SELECT**: high when the printer is online (selected)

The host-side algorithm:

```
1. Read BUSY.  If BUSY=1, wait.
2. Place byte on data lines D0-D7.
3. Pulse /STROBE low for at least 0.5 µs, then high.
4. Wait for /ACK (or just rely on BUSY for next byte).
```

On the Spectrum, the 8 data bits are written to the adapter's data port (typically `#0F`). The `/STROBE` is either:
- Automatically pulsed by the hardware on each write to the data port (simpler adapters), OR
- Manually pulsed by writing to a separate control port (more flexible adapters)

The Spectrum-side code is correspondingly simple:

```z80
; Send byte in A to the Centronics printer
; Assumes Kempston/DK'Tronics-style interface at #0F/#1F
print_byte:
        PUSH AF
wait_ready:
        IN   A, (#1F)            ; read status
        AND  #80                 ; bit 7 = BUSY
        JR   NZ, wait_ready      ; wait until not busy
        POP  AF
        OUT  (#0F), A            ; write byte (also pulses /STROBE on Kempston)
        RET
```

For software compatibility, the **Kempston and DK'Tronics conventions are the same**: data at `#0F`, status at `#1F`, hardware-strobe on write. Most Centronics-using software (word processors, document editors, drawing apps) is written to this convention.

### Software ecosystem

The major applications that supported Centronics printers from the Spectrum:

- **Tasword II** — the dominant word processor; supported Kempston and DK'Tronics adapters
- **The Advanced Word Processor (TAWP)** — later alternative
- **VU-3D, VU-File, VU-Calc** — the VU suite supported parallel printers
- **Pendown** — educational word processor
- **Microdraft** — CAD program; supported screen dumps to Centronics printers
- **The Artist, The Art Studio** — drawing programs; screen dumps

For Soviet software, the **Breeze** editor and many other applications supported the Beta 128 + Centronics convention.

---

## Soviet Printers: SM640, SM646

The Soviet Spectrum clone ecosystem had its own printers, designed for compatibility with the wider Soviet/Eastern-bloc computer market:

### SM640

The **SM640** (СМ640) is a Soviet dot-matrix printer using the **IEEE 488 / IEC 625** interface (a parallel bus standard used in Soviet instrumentation). It was used with various Soviet computer families (Agat, Korvet, UKNC) and adapted to the Spectrum via a Centronics-like interface on the Beta 128.

- **Print method**: 9-pin dot matrix
- **Print speed**: ~120 cps
- **Paper**: Continuous tractor-fed, 80-column fanfold
- **Character set**: GOST 19768-74 (Soviet character set with Cyrillic + Latin)
- **Driver**: requires a custom Spectrum-side driver that translates Spectrum character codes to the SM640's character set and handles the IEC 625 protocol (different from standard Centronics)

### SM646

The **SM646** (СМ646) is the Centronics-interface successor to the SM640. It uses the standard Centronics protocol and works directly with the Beta 128 + Centronics adapter (or any Kempston-style adapter).

- **Print method**: 9-pin dot matrix
- **Print speed**: ~150 cps
- **Paper**: Continuous tractor-fed, 80-column fanfold
- **Character set**: Same GOST 19768-74
- **Driver**: standard Spectrum Centronics driver works, but character set translation is needed for Cyrillic

### Soviet software support

The Russian Spectrum scene developed several utilities for printing on SM640/SM646 and other Soviet printers:

- **Breeze** (Бриз) — text editor with built-in printer support
- **ASC Sound Master** — early Russian music tracker with screen-dump-to-printer
- **Driver libraries** in ProfROM (Scorpion), ATM Turbo ROM, etc.

For source material on Soviet printer support, **zx-pk.ru** is the primary archive — most Russian-language printer driver code and SM640/SM646 documentation is there.

### Modern Russian/Cyrillic printers

For modern Russian users, the SM640/SM646 are obsolete; the convention now is the same as for Western users: emulators and Centronics-to-USB adapters, or modern dot-matrix printers that natively support Cyrillic.


---

## Common Pitfalls

1. **The +2A/+3 dropped the +9V line on the edge connector.** The original ZX Printer is powered from this line. Plugging a ZX Printer into a +2A/+3 will not work — the motor will not spin and no printing will occur. Use an Alphacom 32 (self-powered), a Centronics adapter, or supply +9V externally. See [interface2.md](interface2.md) for the same issue affecting Interface 2 cartridges.

2. **The ZX Printer port overlaps the keyboard port.** The printer responds to any address with `A2=0`; the ULA's keyboard port responds to any address with `A0=0`. Reading `#FA` (both A0 and A2 low) hits both devices simultaneously. Use `#FB` (A0=1, A2=0) for the printer to avoid keyboard interference.

3. **The `OUT (#FB),A` instruction resets both latches on every write.** Code that reads the printer status AFTER writing will see bit 7 (paper start) and bit 0 (next pixel) cleared, regardless of the printer's actual state. Always wait for the latches to re-trigger before reading again.

4. **The ZX Printer's port decode is `A2=0`, not full decode.** This means the printer responds to a large number of port addresses (`#FB`, `#F7`, `#F3`, `#EF`, `#EB`, …). Software that does `OUT` to a broad mask of addresses (e.g., a RAM-refresh loop or `OUT (C),A` with `B` non-FF) may inadvertently trip the printer.

5. **The stylus heats up over time.** Holding the stylus on for too long (e.g., during a paused print) burns the paper through to the backing and damages the stylus tip. Always turn the stylus off (bit 7 = 0) when not actively printing a pixel.

6. **The 8-bit Centronics status read at `#1F` conflicts with the Kempston joystick port.** Software that polls both `#1F` (printer status) and `#1F` (joystick) will get the OR of both devices. The Kempston Centronics Interface typically decodes more address lines to avoid this, but cheap clones may not. See [joystick.md](joystick.md) for the Kempston joystick decode variants.

7. **Centronics BUSY polarity varies between adapters.** The Kempston convention is bit 7 of `#1F` = BUSY (1 = busy). The DK'Tronics convention is the same. Some Soviet and homebrew adapters use bit 5 or bit 6. Always check the adapter's documentation.

8. **`LPRINT`/`LLIST`/`COPY` only work when stream 3 is open.** On the 48K ROM, stream 3 is opened to the printer channel at boot. On the 128K/+2/+3 with the +3DOS ROM, stream 3 may be redirected. If `LPRINT` produces no output, check that stream 3 is bound to the printer channel.

9. **Soviet SM640 uses IEEE 488 (IEC 625), not Centronics.** Don't try to drive an SM640 with a Kempston adapter — the protocols are completely different (handshake-driven bus vs. strobe-driven interface). Use the SM646 (Centronics) instead.

10. **Character set translation is required for Cyrillic.** Soviet printers (SM640, SM646) use GOST 19768-74, which is incompatible with the Spectrum's native character codes. Russian-language software includes a translation table; Western software printing to a Soviet printer will print gibberish for any non-ASCII character.

---

## When to Use a Printer (Today)

| Use case | Recommendation |
|----------|----------------|
| Running original Spectrum software that uses `COPY` / `LPRINT` / `LLIST` | Real ZX Printer (for 16K-+2) or Alphacom 32 (any model); emulators that emulate the ZX Printer also work |
| Word processing (Tasword II, etc.) on original hardware | Kempston or DK'Tronics Centronics adapter + a real Epson FX-80 / Star LC-100 (or modern dot-matrix) |
| Modern hardware (Next, harlequin, etc.) | Most have a Centronics-compatible output via GPIO or expansion; the ZX Spectrum Next has a specific Retro-Printer interface |
| Emulator users | Modern emulators can redirect `COPY`/`LPRINT` to a PDF or PNG — no hardware needed |
| New software with print capability | Target the Kempston Centronics convention (`#0F` data, `#1F` status) — it has the broadest emulator support |
| Preserving ZX Printer output | Scan surviving prints at 600 dpi or higher; the metallized paper degrades over decades |

---

## Comparison Matrix

| Feature | ZX Printer | Alphacom 32 | Kempston Centronics | DK'Tronics | SM640 (Soviet) | SM646 (Soviet) |
|---------|------------|-------------|---------------------|------------|----------------|----------------|
| Year | 1981 | 1984 | 1984 | 1985 | late 1980s | early 1990s |
| Technology | Spark (electro-erosion) | Thermal | n/a (just adapter) | n/a (just adapter) | 9-pin dot matrix | 9-pin dot matrix |
| Paper | Metallized aluminized | Thermal | Standard fanfold | Standard fanfold | Tractor fanfold | Tractor fanfold |
| Resolution | ~256×256 | ~256×256 | printer-dependent | printer-dependent | 240 dpi | 240 dpi |
| Speed (text) | ~50 cps | ~80 cps | printer-dependent | printer-dependent | ~120 cps | ~150 cps |
| Power | Spectrum +9V line | Self-powered | Spectrum edge | Spectrum edge | External | External |
| Host interface | Port `#FB` (any `A2=0`) | Port `#FB` (compatible) | `#0F`/`#1F` | `#0F`/`#1F` | IEEE 488 | Centronics |
| Works on +2A/+3 | ❌ (no +9V) | ✅ | ✅ | ✅ | n/a | n/a |
| Works on Pentagon/Scorpion | ❌ | ❌ | ✅ | ✅ | via Beta 128 adapter | ✅ (Centronics) |
| Bundled software | `COPY`/`LPRINT`/`LLIST` (ROM) | Same | Tasword, VU suite | Tasword, VU suite | Breeze editor | Breeze editor |

---

## Modern Analogies

- **The ZX Printer's spark technology ≈ a tattoo machine.** A needle (the stylus) punctures a surface (the aluminized paper), with the puncture controlled by an electric current. The mechanics are nearly identical.
- **The ZX Printer's pixel-by-pixel protocol ≈ a thermal print head in a modern receipt printer.** Both iterate pixel-by-pixel, with a "stylus ready" signal gating each pixel. Modern thermal printers do this in hardware; the ZX Printer made the Spectrum's CPU do it.
- **The ZX Printer's reliance on +9V ≈ USB devices exceeding the 500 mA spec.** Both pull more power than the host bus is designed to supply, leading to compatibility issues with later host revisions.
- **The Centronics adapter ecosystem ≈ USB-to-parallel printer adapters today.** A small dongle translates the host's interface (Centronics parallel) into the printer's interface (modern USB), so legacy software can drive modern printers.
- **The SM640's IEEE 488 ≈ HP-IB / GPIB instrument control.** The same protocol used by Soviet printers was the standard for laboratory instrumentation; both use a 24-pin Amphenol connector with a hardware handshake bus.
- **The "LPRINT goes to stream 3" convention ≈ Unix's `/dev/lp0` device.** Both expose a printer as a named stream that any program can write to; the host OS (or ROM) handles the device-specific protocol.

---

## Cross-References

- [04_operating_systems/rom_48k.md#printing](../../04_operating_systems/rom_48k.md) — 48K ROM's `COPY` routine, `LPRINT`/`LLIST` tokens, stream 3 / channel mechanism
- [interface2.md](interface2.md) — +2A/+3 dropped the +9V line on the edge connector (also broke ZX Printer)
- [10_references/io_port_map.md](../../10_references/io_port_map.md) — Canonical I/O port reference (printer at `A2=0`)
- [joystick.md](joystick.md) — Kempston joystick port `#1F` conflict with Centronics status read
- [03_io/storage/beta_disk_interface.md](../storage/beta_disk_interface.md) — Beta 128 + Centronics adapter convention used in Soviet clones
- [04_operating_systems/system_variables.md](../../04_operating_systems/system_variables.md) — `STREAM` / `CHANNEL` system variables
- [02_hardware/original/README.md](../../02_hardware/original/README.md) — Original Spectrum hardware models (power supply, edge connector pinout)

---

## Primary Sources

1. **Sinclair ZX Printer Owner's Manual** — Sinclair Research, 1981. Original protocol description, BASIC commands, paper specification.
2. **The ZX Spectrum ROM Disassembly** — Logan & O'Hara, 1983. The `COPY` routine at `#0EAC`, the `PO-FETCH` and `PO-MSG` print-stream routines.
3. **World of Spectrum — Peripherals FAQ** — `worldofspectrum.org/faq/reference/peripherals.htm`. Adapter port assignments and compatibility tables.
4. **Sinclair Wiki — ZX Printer** — `sinclair.wiki.zxnet.co.uk/wiki/ZX_Printer`. Hardware photographs, schematic, port-decode analysis.
5. **Sinclair Wiki — Alphacom 32** — `sinclair.wiki.zxnet.co.uk/wiki/Alphacom_32`. Thermal-paper variant details.
6. **Kempston Centronics Interface documentation** — Kempston Micro Electronics, 1984. Port assignment, status bit definitions.
7. **ZX Spectrum +2 / +3 Service Manual** — Amstrad, 1987-1988. Documents the removal of the +9V line and the resulting ZX Printer incompatibility.
8. **zx-pk.ru (Russian)** — Soviet SM640/SM646 printer discussions, Breeze editor driver source code, Beta 128 Centronics adapter schematics.
9. **Retro-Printer project** — `retroprinter.com`. Modern Pi-based emulation of ZX Printer and Centronics protocols; reference for new software targeting the same conventions.

