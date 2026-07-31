[← Home](../../README.md) · [New Gen Hardware](README.md)

# Sprinter — Peters Plus's Z80 PC with Reprogrammable Logic

The **Sprinter** (Russian: **Спринтер**) is a late-era Russian Spectrum-family computer produced by **Peters Plus, Ltd.** of St. Petersburg, with the **Sp2000** motherboard launching around 1999–2001. It takes a different path from the FPGA-based machines (Next, ZX Evolution, ZX-Uno) covered elsewhere in this section. Where those machines use FPGAs to recreate classic Spectrum hardware, the Sprinter is a **Z80-based personal computer** built around an **Altera reprogrammable logic device (PLD)**, paired with a real Zilog Z84C15 CPU, 4 MB of RAM, 256 KB of ROM, a hardware disk controller, IDE/AT hard disk support, two ISA-8 expansion slots, and a 16-bit Philips TDA1543 DAC for digital audio.

Designed primarily by **Alex Goryachev** and the Peters Plus team, the Sprinter is binary-compatible with the Spectrum 128K and Pentagon (for the existing Russian software library) but provides enough PC-style hardware that **new software could be written for it that had nothing to do with the Spectrum** — word processors, file managers, BBS clients, CD-ROM audio players, and even a port of Doom.

This article covers the Sprinter as a hardware platform: its architecture, memory map, video modes, ports, and programming model. For the demoscene context, see [Soviet demo scene](../../07_demoscene/soviet_demo_scene.md). For the Sprinter's place in the clone-timing landscape, see [clone_timing.md](../clones/clone_timing.md).

> [!IMPORTANT]
> The Sprinter's defining feature is its **reprogrammable logic**. The hardware's behavior is defined by a bitstream stored in **EEPROM**, loaded into the Altera PLD at power-on. This means the Sprinter can be **upgraded in software** — running a flash utility on the Sprinter itself rewrites the EEPROM in approximately three minutes, changing the computer's hardware architecture without any component replacement.

---

## Why the Sprinter Is Different

By the late 1990s, the Russian Spectrum scene had a problem: the hardware was old. The Pentagon 128 was a 1989 design built around discrete TTL logic, with a slow 3.5 MHz CPU and tape-based software distribution. The scene wanted modern features — fast CPU, disk storage, VGA-compatible output, PS/2 keyboard, mouse — without abandoning the thousands of existing Spectrum programs.

Two solutions emerged:

1. **The ZX Evolution** (Vladimir Kladov's later design, 2007+) — use an FPGA to recreate the Pentagon while adding modern peripherals (see [zx_evo.md](zx_evo.md)).
2. **The Sprinter** (Alex Goryachev / Peters Plus, ~1999) — build a **new Z80-based computer** around a reprogrammable logic device, with a 128K/Pentagon compatibility mode implemented as one of two firmware configurations.

The Sprinter is the "more radical" approach: it does not try to clone the Pentagon's video timing or contention behavior at the hardware level. Instead, it provides a modern PC-style architecture with a Spectrum compatibility layer. The result is a machine that is **binary-compatible with Pentagon software at the API level** (TR-DOS calls, BIOS calls, video memory layout) but has **completely different underlying hardware**.

| Criterion | Sprinter (Sp2000) | ZX Evolution | ZX Spectrum Next |
|---|---|---|---|
| **Year** | ~1999–2001 | 2007 | 2017 |
| **Architecture** | Z80 + Altera PLD | Z80 + Altera FPGA + ATmega MCU | FPGA soft-core (Z80N) |
| **CPU** | Real Z84C15 @ 21 MHz / 3.5 MHz | Real Z80 @ 3.5 / 7 / 14 MHz | Z80N @ 3.5 / 7 / 14 / 28 MHz |
| **RAM** | **4 MB** (SIMM, expandable to 64 MB hardware limit) | 4 MB | 2 MB |
| **Video** | PLD-based (320×256×256, 640×256×16) | Pentagon-style + extensions | Layer 2 / sprites / tilemap / copper |
| **Storage** | IDE/AT + Kr1818VG93 FDC + 3.5"/5.25" FDD | IDE + SD card + Beta 128 | SD card |
| **Keyboard** | **101-key AT PC keyboard** | PS/2 | Built-in + PS/2 |
| **Mouse** | **MS Mouse** (serial) | PS/2 | PS/2 |
| **Audio** | **AY-3-8910** (in PLD) + **16-bit DAC (Philips TDA1543)** | AY-3-8912 + beeper | Dual AY + DMA-driven PCM |
| **Expansion** | **Two ISA-8 slots** | Pentagon edge connector | Edge connector + expansion |
| **RTC** | Dallas DS12887A (CMOS clock) | Battery-backed via ATmega | Software |
| **Compatibility target** | Pentagon (software-level) | Pentagon (cycle-level) | 48K/128K/Pentagon (cycle-level) |

---

## Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | **Zilog Z84C15** at 21 MHz (turbo) or 3.5 MHz (compatibility) — a full Z80 CPU with integrated peripherals (CTC, PIO, SIO, watchdog) |
| **Logic** | **Altera reprogrammable PLD (PPLM)** — loaded from EEPROM at every power-on, rewritable in 3 minutes via software utility |
| **RAM** | **4 MB SIMM** (installed standard) — hardware supports up to 64 MB but no PLD bitstream exists for >4 MB |
| **Fast RAM** | **64 KB dedicated fast RAM** (zero wait-state access) |
| **ROM** | **256 KB flash** (EEPROM) — holds the BIOS, 128K BASIC, Pentagon ROMs, and DOS |
| **Video RAM** | **256 KB** (or 512 KB on upgraded units) — dedicated VideoOZU |
| **FDC** | **Kr1818VG93** (Soviet WD1793 clone) — supports 3.5" (1.44 MB / 720 KB) and 5.25" (720 KB) drives |
| **HDD controller** | **IDE / AT** — 8-bit transfers, MS-DOS FAT-16 formatted, up to 2 GB partitions |
| **Clock** | **Dallas DS12887A** or ODIN OED12C887 — battery-backed CMOS real-time clock |
| **Keyboard** | **101-key AT PC keyboard** controller |
| **Mouse** | **MS Mouse** serial controller |
| **Audio output** | **AY-3-8910** (implemented in PLD, Pentagon-compatible) + **16-bit stereo DAC Philips TDA1543** (sample rates up to 110 kHz) + beeper |
| **Video output** | **CGA monitor** (15 kHz horizontal sync) + **RGB** (via DIN) + **TV via SCART** |
| **Joystick** | **Kempston** at port `#1F` (Sinclair joysticks duplicated on keyboard) |
| **Parallel port** | **Centronics** — for printer connection |
| **Serial ports** | **Two non-RS-232 serial ports** — one for mouse, one for keyboard (not standard PC COM ports) |
| **Expansion** | **Two standard ISA-8 slots** — for ISA modems and other 8-bit ISA cards |
| **Graphics modes** | **320×256×256** (PC-style 256-color) and **640×256×16** (PC-style 16-color) |
| **Power** | Standard PC AT power supply (+5 V, −5 V, +12 V, −12 V) |
| **Case** | Desktop case resembling a PC/XT (or ATX — but ATX PSU connectors incompatible) |

### Why an Altera PLD, not an FPGA?

The Sprinter was designed in the late 1990s, when FPGA technology was expensive and hard to source in Russia. Altera's **MAX 7000 series PLDs** (complex programmable logic devices) were more affordable and adequate for the glue-logic task — address decoding, memory banking, video generation, and I/O port mapping. The PLD does **not** contain a CPU; the real Z84C15 handles all Z80 execution.

The crucial innovation is the PLD's **reprogrammability**: the bitstream is stored in a separate EEPROM chip, and rewriting the EEPROM changes the hardware architecture without any component replacement. The Sprinter is one of the earliest examples of a Russian home computer with **field-upgradable hardware logic**.

---

## Memory Architecture

The Sprinter's memory is organized as **256 banks of 16 KB** (4 MB total), paged through a Pentium-style bank-switching scheme. The system operates in two configurations:

### Native Sprinter Mode

In **native mode**, the Sprinter provides independent banking for all four 16 KB slots in the Z80 address space:

| Port | Function |
|---|---|
| `#1FFD` | Bank switch for `#0000–#3FFF` (lower 16 KB) |
| `#EFF7` | Bank switch for `#4000–#7FFF` |
| `#DFFD` | Bank switch for `#8000–#BFFF` |
| `#7FFD` | Bank switch for `#C000–#FFFF` |

In native mode, all four 16 KB slots are independently banked — giving the programmer full control over which 4 of the 256 banks are visible at any time. This is more flexible than the Pentagon's model (where `#4000–#7FFF` is bank 5 and `#8000–#BFFF` is bank 2, both fixed).

### Spectrum Compatibility Mode (Sprinter-ZX)

In **Sprinter-ZX mode** (selected at boot via the configuration menu), the banking is restricted to mimic the Pentagon 128:

- `#7FFD` controls `#C000–#FFFF` as a single 16 KB bank
- `#4000–#7FFF` is bank 5 (fixed)
- `#8000–#BFFF` is bank 2 (fixed)

This allows existing Pentagon software to run, provided it does not depend on cycle-exact contention timing or floating-bus behavior. Different clone sub-modes (Pentagon, Scorpion) can be selected to handle software written for specific Russian clone timing.

> [!NOTE]
> The Sprinter's Pentagon compatibility is "good enough" for **most** Pentagon software — roughly 80–90% of games and demos run correctly. The 10–20% that fail are typically cycle-exact demos that depend on contention timing. See [clone_timing.md](../clones/clone_timing.md) for the timing comparison.

---

## Video Modes

The Sprinter's PLD-based video generator produces the machine's signature feature — **multiple video modes** selectable at runtime:

| Mode | Resolution | Colors | Use case |
|---|---|---|---|
| **Spectrum (text)** | 256×192 | 8×2 (attribute) | Pentagon-compatible display |
| **Sprinter 320×256×256** | **320×256** | **256** | PC-style 256-color graphics (games, image viewers) |
| **Sprinter 640×256×16** | **640×256** | **16** | PC-style 16-color graphics (spreadsheets, text editors) |

The Spectrum mode is binary-compatible with the Pentagon — software that writes to `#4000` (bank 5) sees the standard attribute-based screen. The Sprinter native modes are accessed through the PLD's video register set, which uses dedicated I/O ports.

### Video Output

Unlike PC-style machines with VGA output, the Sprinter targets **15 kHz horizontal sync** monitors:

- **CGA-style analog monitor** with RGB input (e.g., Elektronika, WTC, Commodore 1084)
- **TV via SCART** — the Sprinter ships with a SCART video cable for direct TV connection
- **RGB via DIN connector** — for RGB monitors

The Sprinter does **not** produce a standard VGA signal. To use a VGA monitor, you need a 15 kHz-capable model (most early 1990s VGA monitors support this; modern VGA monitors typically do not).

---

## Software Ecosystem

The Sprinter shipped with a substantial **bundled software package**, distributed free of charge with the Sp2000 board:

### Operating Systems and System Software

| Software | Function |
|---|---|
| **Estex OS** | Disk subsystem OS compatible with MS-DOS FAT-16 — supports IDE hard disks up to 2 GB partitions |
| **Sprinter-ZX configuration** | Spectrum compatibility mode (Pentagon/Scorpion selectable) |
| **BIOS** | Boot ROM with hardware initialization and PLD loading |

### Applications

| Software | Function |
|---|---|
| **Flex Navigator** | Graphical file manager (similar to Norton Commander) |
| **Black Cat Modem Terminal** | Terminal program — supports X-modem, Y-modem, Z-modem protocols |
| **GFX-viewer** | Image viewer for BMP, PCX, and ZX Spectrum formats |
| **CD-Player** | Audio CD playback via connected CD-ROM drive |
| **CD-Browser** | CD-ROM data reader (file browser for CD-ROMs) |
| **DOS Commander** | Text-mode dual-panel file manager |
| **TASM** | Multi-text editor and assembler (Sprinter-native) |
| **2D-Studio** | Graphics editor for BMP format (320×256, 256 colors) — working version with minimum functions |
| **FORTH** | Forth programming language core |

### Games and Demos

| Software | Function |
|---|---|
| **Doom (Sprinter port)** | First-person shooter demonstrating the Sprinter's hardware graphics capabilities |

The Sprinter's software ecosystem went beyond Spectrum compatibility, embracing PC-style productivity applications. The bundled IDE hard disk support and FAT-16 file system made the Sprinter a credible **general-purpose 8-bit PC**, not just a gaming machine.

---

## Hardware Self-Upgrade — Reprogramming the PLD

The Sprinter's most innovative feature is its **field-upgradable hardware logic**. The Altera PLD's bitstream is stored in a separate EEPROM chip on the Sp2000 board. The bitstream is **not** baked into the PLD itself — it is loaded from EEPROM into the PLD at every power-on.

This means **upgrading the Sprinter's hardware is a software operation**:

1. Download or write a new EEPROM image (containing updated PLD bitstream)
2. Run the EEPROM flashing utility on the Sprinter (an `.EXE` file)
3. The utility rewrites the EEPROM contents in approximately **3 minutes**
4. Reboot — the new hardware architecture is loaded into the PLD at next power-on

The Sprinter can **rewrite its own EEPROM** — no external JTAG programmer is required. This is a remarkable capability for a 1999 home computer, predating the in-field firmware updates of modern FPGA platforms (ZX Evolution, MiSTer, etc.) by several years.

### Hardware Upgrade Roadmap

Peters Plus had plans to extend the Sprinter's hardware architecture via PLD updates:

- **Support for >4 MB RAM** — the Sp2000 board has hardware contacts laid out for up to **64 MB of memory**, but the memory-distribution scheme in the PLD bitstream was never finalized for configurations beyond 4 MB
- **New video modes** — additional graphics modes were planned
- **Bus support** — possible PCI bus support was discussed but never implemented

Peters Plus explicitly committed to **never releasing a new Sp2000 board revision** — all hardware improvements would be delivered as PLD bitstream updates, free for existing owners.

---

## Sprinter Community and Distribution

### Distribution

The Sprinter Sp2000 board was sold by Peters Plus directly, either from their St. Petersburg office or by mail order after full prepayment:

> **Peters Plus, Ltd.**  
> Russia, 191014 St. Petersburg  
> st. Uprising 35-31  
> Tel: +7 (812) 327-3531  
> E-mail: sprinter@petersplus.ru  
> Web: petersplus.ru / petersplus.com  
> FidoNet: 2:5030/529.56

**Price** (circa 2001): **3,255 Russian rubles** for the assembled Sp2000 board with installed 4 MB SIMM and 256 KB video RAM. Delivery within Russia was approximately 7% of the order cost. Bare boards and component kits were **not** sold — only fully assembled and tested units.

### International Adoption

By late 2001, Peters Plus reported **over 50 Sprinter owners** across multiple countries, reflecting a small but international user base:

| Country | Region |
|---|---|
| Russia | Primary market |
| Belarus | Post-Soviet neighbor |
| Hungary | Eastern Europe |
| Poland | Eastern Europe |
| Austria | Western Europe |
| Italy | Western Europe |
| Denmark | Western Europe |
| USA | North America |
| Argentina | South America |

Many international users were programmers interested in developing Sprinter software. The English-language documentation was limited; international users relied heavily on machine-translated Russian docs.

### Warranty and Support

Peters Plus provided:

- **1-year warranty** against manufacturing defects
- **Free technical support** via e-mail and FidoNet
- **BIOS updates** and **PLD bitstream updates** (free for all owners)
- **Software consultations** for programmers writing Sprinter-native software

---

## Programming the Sprinter

### Detecting a Sprinter

The Sprinter can be detected by reading its BIOS signature or by probing for unique ports. A typical detection routine checks for the presence of the Sprinter's bank-switching behavior:

```z80
detect_sprinter:
        ; 1. Save current bank state
        ld  bc, #1FFD
        in  a, (c)
        ld  (saved_bank), a
        
        ; 2. Try to switch to a high bank (only Sprinter has >1 MB)
        ld  a, #80                 ; bank 128 (way beyond 128K clone range)
        out (c), a
        
        ; 3. Verify the switch took effect
        in  a, (c)
        cp  #80
        jr  nz, .not_sprinter
        
        ; 4. Restore original bank
        ld  a, (saved_bank)
        out (c), a
        scf                        ; carry set = Sprinter detected
        ret
.not_sprinter:
        ld  a, (saved_bank)
        out (c), a
        or  a                      ; carry clear = not Sprinter
        ret
```

For authoritative detection, consult the Sprinter technical manual for the specific BIOS signature bytes and their addresses.

### Switching Between Modes

The Sprinter's mode (native vs. Sprinter-ZX) is selected at boot time via the configuration menu, not at runtime. Once the machine boots into a configuration, it stays there until the next reboot. This is fundamentally different from the ZX Spectrum Next's runtime mode switching via NextReg writes.

### Using the 16-bit DAC

The Sprinter's Philips TDA1543 DAC provides **16-bit stereo output at sample rates up to 110 kHz** — the highest-quality digital audio of any Spectrum-family machine. To play digital audio through the DAC:

```z80
; Simplified DAC output routine (mono, 8-bit samples scaled to 16-bit)
play_dac_sample:
        ld  a, (hl)                ; load 8-bit sample
        ; ... scale to 16-bit and write to DAC register pair ...
        ; (exact ports vary by PLD bitstream version)
        ret
```

The DAC was used by the Sprinter's bundled software (especially the CD-Player for Audio CD playback) and by demoscene productions. It is significantly higher fidelity than the 8-bit Covox-style DACs found on other Spectrum clones.

---

## Historical Significance

The Sprinter occupies an important transitional position in the Russian Spectrum ecosystem:

1. **Late-era Z80 PC** — along with the ATM Turbo, it represents the "Spectrum as a real computer" approach: fast Z80, large RAM, hard disk, modern peripherals
2. **First mass-produced Russian computer with field-upgradable hardware logic** — the EEPROM-backed PLD architecture predates similar capabilities in Western retro hardware by years
3. **Bridge between the clone era and the FPGA era** — the Sprinter's design philosophy directly influenced Vladimir Kladov's later ZX Evolution (2007+), which moved the reprogrammable logic from a PLD to a full FPGA
4. **Small but international community** — the Sprinter found users across Europe and the Americas, demonstrating that the Russian Spectrum scene had global reach by the early 2000s

The Sprinter was largely superseded by the ZX Evolution after 2007, which had better Pentagon compatibility via its FPGA approach. The Sprinter is now a niche historical platform — small but dedicated community, primarily Russian-language documentation, with active preservation efforts on the **nedopc.org** archive.

---

## Cross-References

- [ZX Evolution](zx_evo.md) — the later, FPGA-based successor concept from a different designer (Kladov, NedoPC)
- [Pentagon 128](../clones/pentagon.md) — the Sprinter's compatibility target
- [Pentagon 1024](../clones/pentagon_1024.md) — the Sprinter's competitor at the time
- [ATM Turbo](../clones/atm_turbo.md) — another late-era Russian "Z80 PC" with extended graphics
- [Profi](../clones/profi.md) — earlier Ukrainian clone with VGA output (similar concept)
- [Clone timing](../clones/clone_timing.md) — Sprinter's relationship to other clone timings
- [Soviet demo scene](../../07_demoscene/soviet_demo_scene.md) — cultural context

---

## References

- **Sprinter FAQ** by Alex Goryachev / Peters Plus, Ltd. (created 17 December 2001) — the canonical hardware, software, and support reference; reprinted via ZXPRESS as "Iron — Sprinter? Questions and answers!" in Sinclair Club #05
- **Sprinter technical manual** (Peters Plus, ~1999–2001, Russian) — original hardware reference with port maps and BIOS entry points
- **Peters Plus archive** ([nedopc.org](http://nedopc.org)) — Sprinter schematics, BIOS source, software archive
- **ZX-Format magazine** issues covering the Sprinter launch and ongoing development
- **ZX-Forum #2** (ZXF02.pdf) — interview with Alex Goryachev on the Sprinter's design and goals
- **zx-pk.ru forum** — *Sprinter* subforum with BIOS documentation and repair threads
- **SpeccyWiki (speccy.info)** — Sprinter article with photos and specification tables
- **World of Spectrum** — Sprinter file archive with software, documentation, and interviews
