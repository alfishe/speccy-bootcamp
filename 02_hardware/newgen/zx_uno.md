[← Home](../../README.md) · [New Gen Hardware](README.md)

# ZX-Uno — The Open-Source FPGA Spectrum

The **ZX-Uno** is an open-source, community-designed FPGA-based ZX Spectrum, crowdfunded on **Verkami in March 2016** by the **AZXUNO non-profit association** — a five-person Spanish-led team. The project was born in **2012** on the Spanish retro-computing forum **zonadepruebas.com**, evolved through **four board revisions and approximately 40 hand-soldered prototypes** over three years, and shipped its first production boards in 2016. The latest public board revision is **v4.1**.

Where the ZX Spectrum Next is a finished commercial product aimed at the broader retro-computing market, the ZX-Uno is a **hacker-friendly platform** aimed at developers who want to **modify the FPGA core itself**. The bitstream is fully open source (Verilog), the schematic is open (Creative Commons Share-Alike), and the firmware is field-updatable from SD card. The ZX-Uno has become the de facto **experimental platform** for the Spanish-speaking and wider retro Spectrum community — new features (ZXCortex, DIVMMC, layer 2 prototypes) are often tried on the ZX-Uno first.

### The AZXUNO Team

The ZX-Uno was designed by five people, four based in Spain (Málaga, Zaragoza, Barcelona, Sevilla) and one in California, USA. To support the project legally, they constituted themselves as the **ZX-UNO Developer Association (AZXUNO)** — a Spanish non-profit association with fiscal identification:

| Member | Handle | Role | Location |
|---|---|---|---|
| **Antonio José Villena Godoy** | `avillena` | **President of AZXUNO**; author and maintainer of the ZX-Uno BIOS; day job at **IMAGINA Artificial Intelligence, S.L.** | Málaga, Spain |
| **Jordi Bayó** | `Hark0` | **Secretary**; graphic designer; corporate image and package design; keyboard stickers | Zaragoza, Spain |
| **Samuel Baselga López** | `Quest` | **Core porter and framework author** — wrote the multi-core framework that allows storing up to **9 cores in the same FPGA** without a JTAG programmer; joined the team in **September 2015** | Barcelona, Spain |
| **Miguel Angel Rodríguez Jódar** | `mcleod_ideafix` | **Treasurer**; full-time lecturer at the **Dept. of Architecture and Computing Technology, University of Seville**; author and maintainer of the **ZX Spectrum, SAM Coupé, and Jupiter ACE cores** | Sevilla, Spain |
| **Don "Superfo"** | `Superfo` | **PCB designer** — design, layout, and routing for the **first three board versions** (v1, v2, v3) | California, USA |

The crowdfunding campaign raised money to manufacture and distribute a limited run of **250 units** — explicitly positioned as "not a product for the masses, but rather for original machine lovers and microelectronic hobbyists."

> [!NOTE]
> This article covers the **hardware platform** — what the ZX-Uno is, its physical architecture, and its programming model. For the **FPGA internals** (the soft-core CPU, the ULA recreation, the memory arbitration), see [zx_uno_core.md](../../11_emulation/fpga/zx_uno_core.md) in the emulation section.

---

## Why ZX-Uno?

The ZX-Uno was created to fill a gap that existed before the ZX Spectrum Next shipped:

1. **Open-source bitstream** — anyone could modify the FPGA core, add features, fix bugs
2. **Affordable hardware** — significantly cheaper than a real Spectrum or even a Harlequin kit
3. **Multi-machine** — a single FPGA can emulate 48K, 128K, +2A, +3, Pentagon, Scorpion, and other variants via core swaps
4. **Modern peripherals** — SD card storage, PS/2 keyboard, VGA output, audio jack
5. **Expansion bus** — a standard Spectrum edge connector for original peripherals

The ZX Spectrum Next (released 2017) addressed some of these needs commercially, but the ZX-Uno remains popular because it is **fully open** — no proprietary firmware, no locked-down features, no commercial vendor dependency.

---

## Hardware Architecture

| Component | Specification |
|---|---|
| **FPGA** | **Xilinx Spartan-6 XC6SLX9-2TQG144C** (TQFP-144 package) — same family as the ZX Spectrum Next KS1 |
| **SRAM** | **512 KB AS7C34096A-10TIN** (static, single +5V rail, 10 ns access time) — used as the Spectrum's main RAM |
| **Oscillator** | **50 MHz** master clock (divided down by the FPGA for Z80 and video timings) |
| **SPI flash** | **4 MB (32 Mbit)** writable SPI flash — holds the FPGA bitstream + multiple ROM images + multiple machine cores |
| **Video output** | **Composite via AD724 encoder** (with switchable **4.43 MHz PAL / 3.58 MHz NTSC** crystal) + **RGB/VGA via Molex 1.25 mm header** (cable available separately) |
| **Audio output** | **3.5 mm stereo jack** — AY left, AY right, beeper mixed |
| **Keyboard** | **PS/2 connector for keyboard and mouse** (no built-in keyboard) |
| **Joystick** | **Sinclair / Kempston** via the expansion edge connector (adapter required) |
| **Expansion port** | **Standard Spectrum edge connector** — accepts original Spectrum peripherals |
| **EAR input** | **Mono 3.5 mm jack** for tape loading (uses **Superfo's 1-transistor EAR circuit**) + alternative mobile-phone / MP3 input |
| **SD/MMC** | **Full-size SD/MMC socket** (microSD also possible with adapter) |
| **JTAG** | **Molex 1.25 mm JTAG header** — for hardware programming (rarely needed; the multi-core framework can reflash from SD) |
| **Power** | **5 V DC via micro-USB connector** (also usable from a TV/monitor USB port) |
| **WiFi** (optional) | **ESP-12 module** (Espressif ESP8266) — connected via SPI header |
| **Form factor** | **Single-board, 86 × 56 mm PCB** — compatible with **Raspberry Pi 1 cases** (some machining required); distributed bare-board (case available separately as a reward) |

The ZX-Uno is **significantly smaller** than the ZX Spectrum Next — it is a bare PCB roughly the size of a Raspberry Pi, designed to be plugged into a TV or monitor via composite video and used with an external PS/2 keyboard. RGB-SCART and VGA cables are available separately for higher-quality video.

### Boot Configuration Utility (PC-BIOS-like)

Out of the box, the ZX-Uno ships with the ZX Spectrum core and **OpenSE** (Andrew Owen's open-source ROM) as the default boot ROM. The boot-time setup program (similar in appearance to a PC BIOS setup screen) lets the user configure:

- **Memory testing, EAR signal level, keyboard testing**
- **Silent Boot** (no ZX-Uno logo at boot)
- **Spectrum keyboard implementation** (Issue 2 or Issue 3)
- **Machine timings** (48K, 128K, etc.)
- **Enable/disable contended memory**
- **Enable/disable DivMMC** and DivMMC NMI trap
- **Choose default ZX Spectrum ROM** to boot from, or choose **default core** for non-Spectrum machines
- **ZX Spectrum ROM manager** — add, delete, update ROMs from SD
- **Core manager** — add other machines' cores, up to **9 cores** total, without needing an external JTAG programmer

---

## Software Compatibility

The ZX-Uno's default bitstream implements a **Spectrum 128K / +2A** with the following extensions:

| Feature | ZX-Uno (default core) | Notes |
|---|---|---|
| **CPU** | Z80 at 3.5 MHz (default), with optional 7 / 14 / 28 MHz turbo | Turbo is switchable via a port write |
| **Memory** | 128 KB standard, up to 1 MB via extended paging | Pentagon-style `#EFF7` paging |
| **Video** | Standard Spectrum 256×192 + **ULAplus** (256-color palette extension) | ULAplus is described below |
| **Audio** | AY-3-8912 (single) + beeper | Standard 128K sound chip |
| **Storage** | **DivMMC** (SD card via SPI) | Emulates the DivMMC interface — modern disk replacement |
| **Keyboard** | PS/2 PC keyboard | Mapped to the Spectrum matrix |
| **Disk interface** | DivMMC + **Beta 128** (emulated) | TR-DOS-compatible |

For most software, the ZX-Uno behaves like a **128K Spectrum with turbo mode and ULAplus palette** — software that runs on a 128K runs unchanged, with optional turbo acceleration and richer colors.

### ULAplus — 256-Color Palette Extension

**ULAplus** is a community-developed extension to the Spectrum's video hardware that replaces the standard 8×2 attribute color model with a **256-color palette** (each pixel attribute selects one of 256 palette entries, each entry programmable to any of 4096 colors via 12-bit RGB). The ZX-Uno implements ULAplus natively in its FPGA core.

ULAplus is **software-transparent** — software that does not use ULAplus sees the standard attribute display. Software that initializes ULAplus via its configuration port (`#BF3B` / `#FF3B`) gains access to the full 256-color palette.

| Port | Function |
|---|---|
| `#BF3B` | ULAplus register select (write) |
| `#FF3B` | ULAplus register data (read/write) |
| ULAplus register 0 | Mode (0 = standard, 1 = ULAplus palette) |
| ULAplus registers 64–191 | Palette entries (one per register, RGB444 in 2 writes) |

ULAplus is also implemented in several emulators (EightyOne, ZEsarUX) and is supported by some modern 48K software. It is **not** as powerful as the ZX Spectrum Next's Layer 2 — ULAplus still uses 8×8 attribute cells, just with more colors per cell — but it is **binary-compatible with all existing Spectrum software**.

---

## Multi-Machine Capability

The ZX-Uno can run **multiple cores** — different bitstreams that implement different machines. Cores are loaded from the SD card at boot time, selectable via a configuration menu:

| Core | What it implements | Author |
|---|---|---|
| **Spectrum 48K** | Original Sinclair 48K — exact timing, contention, floating bus | Antonio Villena (`avillena`) |
| **Spectrum 128K / +2** | Sinclair 128K with `#7FFD` paging | Antonio Villena (`avillena`) |
| **Spectrum +2A / +3** | +2A/+3 with `#7FFD` + `#1FFD` paging | Antonio Villena (`avillena`) |
| **Pentagon 128** | Russian Pentagon 128 — different timing, no contention | Antonio Villena (`avillena`) |
| **Pentagon 1024** | Pentagon with extended paging | Antonio Villena (`avillena`) |
| **Scorpion ZS-256** | Scorpion with its specific timing and ports | Antonio Villena (`avillena`) |
| **Jupiter ACE** | The 1981 Forth-based machine (different CPU is still Z80-compatible) | Miguel Angel Rodríguez Jódar (`mcleod_ideafix`) |
| **SAM Coupé** | The 1989 SAM Coupé — the Spectrum's spiritual successor by MGT | Miguel Angel Rodríguez Jódar (`mcleod_ideafix`) |
| **ColecoVision** | The ColecoVision console (TI SN76489 sound, Z80-based) | Community port |
| **TS-Conf** | The Russian enhanced video configuration from the ZX Evolution | Community port |
| **MSX** | Several MSX variants (also TMS9918-based, Z80-based) | Community port |
| **Galaksija** | The Yugoslavian 8-bit home computer by Voja Antonić | Community port |

The ability to run **non-Spectrum cores** (Jupiter ACE, SAM Coupé, ColecoVision, Galaksija) is a unique strength of the ZX-Uno's FPGA approach — the same hardware can impersonate any machine that fits in its FPGA. Up to **9 cores** can be stored simultaneously in the SPI flash, selectable at boot via the Core Manager without a JTAG programmer (thanks to Samuel Baselga's multi-core framework).

---

## Programming the ZX-Uno

### Detecting the Hardware

The ZX-Uno can be detected by probing for its configuration port:

```z80
detect_zxuno:
        ; Read the ZX-Uno machine ID via its scan-doubler register
        ld  bc, #4053           ; (example — exact port varies)
        in  a, (c)
        cp  #01                 ; ZX-Uno ID
        jr  z, .is_zxuno
        ; Not a ZX-Uno
        ret
.is_zxuno:
        ; Use ZX-Uno extensions (turbo, ULAplus)
        ret
```

### Enabling Turbo Mode

The ZX-Uno's turbo modes (7 / 14 / 28 MHz) are enabled via a port write:

```z80
enable_turbo_14:
        ld  bc, #0BDF           ; (example port — exact value depends on core)
        in  a, (c)
        or  #20                 ; bit 5 = 14 MHz turbo
        out (c), a
        ret
```

As with the ZX Evolution's turbo mode, **always restore 3.5 MHz before accessing slow peripherals** (Beta 128, AY chip).

### Programming ULAplus

To enable ULAplus and set a custom palette:

```z80
enable_ulaplus:
        ; 1. Enable ULAplus mode
        ld  bc, #BF3B           ; register select port
        ld  a, 0                ; register 0 = mode
        out (c), a
        ld  b, >#FF3B           ; BC = #FF3B
        ld  a, 1                ; mode 1 = ULAplus palette active
        out (c), a
        
        ; 2. Set palette entry 0 to bright red (R=15, G=0, B=0 in RGB444)
        ld  bc, #BF3B
        ld  a, 64               ; register 64 = palette entry 0
        out (c), a
        ld  b, >#FF3B
        ld  a, #0F              ; R = 15, G-B = 0
        out (c), a
        ret
```

After this, any attribute byte 0 in the screen displays as bright red instead of the standard black. Software can build custom palettes for striking visual effects while remaining **binary-compatible** with non-ULAplus Spectrums (where the palette port writes are simply ignored).

---

## WiFi via ESP-12

The ZX-Uno includes a header for an **ESP-12 WiFi module** (Espressif ESP8266 derivative), connected via SPI. When installed, the ESP-12 provides:

- **WiFi connectivity** via AT commands (sent over SPI)
- **TCP/UDP sockets** accessible from Z80 code
- **HTTP client** capability (for downloading files from the internet)
- **NTP time sync** for the ZX-Uno's RTC

The WiFi capability is supported by community firmware (the "ZX-Uno WiFi Edition"), and several Spectrum programs (BBS clients, weather widgets, file downloaders) have been written to use it. This makes the ZX-Uno **one of the few WiFi-capable Spectrums** alongside the ZX Spectrum Next.

---

## ZX-Uno vs ZX Spectrum Next

| Aspect | ZX-Uno | ZX Spectrum Next |
|---|---|---|
| **Year** | **2016** (Verkami campaign) | 2017 (Kickstarter campaign) |
| **Origin** | **Spain** (AZXUNO non-profit) | UK (SpecNext Ltd, Rick Dickinson design) |
| **FPGA** | **Xilinx Spartan-6 XC6SLX9-2TQG144C** | Xilinx Spartan-6 (KS1) or Artix-7 (KS2) |
| **RAM** | **512 KB AS7C34096A** (single chip) | 2 MB |
| **Flash** | **4 MB SPI** (bitstream + ROMs + cores) | 4 MB SPI |
| **Video** | **Composite via AD724 (PAL/NTSC switchable) + RGB/VGA via Molex header** | HDMI + VGA + composite |
| **Audio** | AY-3-8912 stereo + beeper (3.5 mm jack) | Dual AY + DMA-driven PCM + beeper |
| **Keyboard** | PS/2 only (external, no built-in) | Built-in + PS/2 |
| **Case** | **Bare board, 86 × 56 mm** (fits Raspberry Pi 1 case) | Desktop case with keyboard |
| **Open-source bitstream** | **Yes** (Verilog, GPL) | No (proprietary core) |
| **Open-source schematic** | **Yes** (Creative Commons Share-Alike) | Hardware specs published, but closed |
| **Enhanced graphics** | **ULAplus** (256-color palette on 8×8 cells) | Layer 2 + sprites + tilemap + copper |
| **Multi-machine** | **Up to 9 cores in same FPGA** (no JTAG needed) | Yes (mode switching at runtime) |
| **Non-Spectrum cores** | **Yes** (Jupiter ACE, ColecoVision, SAM Coupé, MSX, etc.) | No |
| **Crowdfunding** | **Verkami** (250 units, hobbyist-targeted) | **Kickstarter** (thousands of units, mass market) |
| **Production volume** | ~250 units (limited run) | ~5,000+ units |
| **WiFi** | Optional ESP-12 module | Optional ESP-12 module |
| **Price (at launch)** | ~€50–€60 (bare board) | ~£175–£225 (assembled) |

The ZX-Uno and the ZX Spectrum Next are **complementary** — the Next is the more powerful machine for game development, while the ZX-Uno is the more open platform for hardware experimentation. Many enthusiasts own both. The ZX-Uno predates the Next by about a year and pioneered several ideas (open Verilog core, SD-card core swapping, ESP-12 WiFi) that influenced the Next's design.

---

## Cross-References

- [ZX-Uno FPGA core internals](../../11_emulation/fpga/zx_uno_core.md) — the bitstream architecture and ULA recreation
- [ZX Spectrum Next](zx_next.md) — the more powerful commercial equivalent
- [ZX Evolution](zx_evo.md) — the Russian equivalent (different community)
- [Sizif-512 / Harlequin](../clones/sizif_harlequin.md) — other modern recreations (different approaches)
- [Spectrum 128K](../original/zx_spectrum_128.md) — the ZX-Uno's primary compatibility target
- [ULAplus documentation](https://github.com/charliernew/ULAplus) — community-developed palette extension
- [zxdivmmc project](https://github.com/zxdos/zxdivmmc) — the DivMMC interface the ZX-Uno emulates

---

## References

### Project History and Official Sources

- **Verkami crowdfunding campaign** ([verkami.com/zx-uno](https://verkami.com/projects/15202-zx-uno)) — the original March 2016 campaign page, with full project description, reward tiers, and donor list
- **ZX-Uno project page** ([zxuno.speccy.org](http://zxuno.speccy.org/)) — official project page with schematics, bitstreams, manuals, and forum links (primarily Spanish)
- **Antonio Villena's ZX-Uno pages** ([antoniovillena.es](https://antoniovillena.es/)) — design notes, hardware revisions, expansion modules by the project's President and BIOS author
- **zonadepruebas.com retro-computing forum** — the Spanish-language forum where the ZX-Uno project was conceived in 2012 and developed over four years
- [AZXUNO (Asociación de Desarrolladores de ZX-UNO)](https://github.com/zxdos/zx-uno) — the Spanish non-profit association legally constituted to manage the project

### Hardware and Bitstream

- **ZX-Uno bitstream source** ([GitHub: zxdos](https://github.com/zxdos)) — Verilog source for the FPGA core (GPL-licensed)
- [ZX-Uno schematic and PCB](https://github.com/zxdos/zx-uno) — published alongside the bitstream for hardware hackers
- **ZX-Uno Wiki** ([github.com/zxdos/zxuno/wiki](https://github.com/zxdos/zxuno/wiki)) — community-maintained documentation (English and Spanish)
- **Multi-core framework by Samuel Baselga (Quest)** — the framework that allows loading up to 9 cores into the FPGA without a JTAG programmer

### Software and Emulation

- **ULAplus specification** ([GitHub: charliernew/ULAplus](https://github.com/charliernew/ULAplus)) — community-developed palette extension's programmer reference
- **EightyOne emulator** ([SourceForge](http://www.aptuning.com/EightyOne-DS/)) — implements ULAplus and ZX-Uno extensions for development testing
- **ZEsarUX emulator** ([GitHub: chernandezba/zesarux](https://github.com/chernandezba/zesarux)) — full-featured emulator with strong ZX-Uno support, including WiFi simulation
- **esxDOS** ([github.com/zxdos/esxDOS](https://github.com/zxdos/esxDOS)) — the firmware used by the ZX-Uno's DivMMC implementation

### Community

- **Speccy.santo forum** — primary Spanish-language ZX-Uno community hub
- [World of Spectrum forum threads](https://worldofspectrum.org/) — English-language discussion of the ZX-Uno
- **Retro Wiki ES** ([retrowiki.es](https://retrowiki.es/)) — broader Spanish retro-computing community
