[← Home](../../README.md) · [New Gen Hardware](README.md)

# ZX-Uno — The Open-Source FPGA Spectrum

The **ZX-Uno** is an open-source, community-designed FPGA-based ZX Spectrum, first released in 2015 by a Spanish-led team including **Antonio Villena**, **Zeledriver**, and others. It occupies a middle ground between the **ZX Spectrum Next** (a full commercial product with case and keyboard) and the **bare-board clones** (Harlequin, Sizif) — a small single-board computer with an FPGA at its heart, designed to be **built at home** from a kit or pre-assembled, running a free and open bitstream.

Where the ZX Spectrum Next is a finished product aimed at the broader retro-computing market, the ZX-Uno is a **hacker-friendly platform** aimed at developers who want to **modify the FPGA core itself**. The bitstream is fully open source (Verilog), the schematic is open, and the firmware is field-updatable from SD card. The ZX-Uno has become the de facto **experimental platform** for the Spanish-speaking and wider retro Spectrum community — new features (ZXCortex, DIVMMC, layer 2 prototypes) are often tried on the ZX-Uno first.

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
| **FPGA** | **Xilinx Spartan-6 XC6SLX9** (early revisions) or **XC6SLX16** (later revisions) — the same family as the ZX Spectrum Next KS1 |
| **RAM** | **512 KB or 1 MB SRAM** (static, single +5V rail) |
| **Flash** | **512 KB or 1 MB SPI flash** — holds the FPGA bitstream + multiple ROM images |
| **SD card slot** | **MicroSD** (SPI-mode), FAT16/FAT32 filesystem |
| **Video output** | **VGA** (RGB) — directly driven by the FPGA, no scan doubler needed |
| **Audio output** | **3.5 mm stereo jack** — AY left, AY right, beeper mixed |
| **Keyboard** | **PS/2 keyboard port** (no built-in keyboard) |
| **Joystick** | **Sinclair / Kempston** via the expansion edge connector (adapter required) |
| **Expansion** | **Standard Spectrum edge connector** — accepts original Spectrum peripherals |
| **WiFi** (optional) | **ESP-12 module** (Espressif ESP8266) — connected via SPI header |
| **Form factor** | **Single-board**, ~10 cm × 6 cm PCB, bare-board (no case) |
| **Power** | **5V DC** via mini-USB or barrel jack |

The ZX-Uno is **significantly smaller** than the ZX Spectrum Next — it is a bare PCB roughly the size of a Raspberry Pi, designed to be plugged into a TV or monitor via VGA and used with an external PS/2 keyboard.

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

| Core | What it implements |
|---|---|
| **Spectrum 48K** | Original Sinclair 48K — exact timing, contention, floating bus |
| **Spectrum 128K / +2** | Sinclair 128K with `#7FFD` paging |
| **Spectrum +2A / +3** | +2A/+3 with `#7FFD` + `#1FFD` paging |
| **Pentagon 128** | Russian Pentagon 128 — different timing, no contention |
| **Pentagon 1024** | Pentagon with extended paging |
| **Scorpion ZS-256** | Scorpion with its specific timing and ports |
| **Jupiter ACE** | (community port) The Jupiter ACE — a different 1980s machine |
| **ColecoVision** | (community port) The ColecoVision console |
| **TS-Conf** | (community port) The Russian enhanced video configuration |

The ability to run **non-Spectrum cores** (Jupiter ACE, ColecoVision) is a unique strength of the ZX-Uno's FPGA approach — the same hardware can impersonate any machine that fits in its FPGA.

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
| **Year** | 2015 | 2017 |
| **FPGA** | Xilinx Spartan-6 (XC6SLX9/16) | Xilinx Spartan-6 (KS1) or Artix-7 (KS2) |
| **RAM** | 512 KB – 1 MB | 2 MB |
| **Video** | VGA only | HDMI + VGA + composite |
| **Audio** | Stereo AY + beeper | Dual AY + DMA-driven PCM + beeper |
| **Keyboard** | PS/2 only (external) | Built-in + PS/2 |
| **Case** | Bare board | Desktop case with keyboard |
| **Open-source bitstream** | **Yes** (Verilog) | No (proprietary core) |
| **Enhanced graphics** | ULAplus (256-color palette) | Layer 2 + sprites + tilemap + copper |
| **Multi-machine** | Yes (multiple cores) | Yes (mode switching at runtime) |
| **Non-Spectrum cores** | Yes (Jupiter ACE, ColecoVision, etc.) | No |
| **Price** | ~$50–$80 (kit) | ~$250–$400 (assembled) |

The ZX-Uno and the ZX Spectrum Next are **complementary** — the Next is the more powerful machine for game development, while the ZX-Uno is the more open platform for hardware experimentation. Many enthusiasts own both.

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

- **ZX-Uno project page** ([zxuno.speccy.org](http://zxuno.speccy.org/)) — official project page with schematics, bitstreams, and forums (primarily Spanish)
- **ZX-Uno bitstream source** ([GitHub: zxdos](https://github.com/zxdos)) — Verilog source for the FPGA core
- **ZX-Uno forum** ( speccy.santo) — primary community hub (Spanish-language)
- **Antonio Villena's ZX-Uno pages** — design notes, hardware revisions, expansion modules
- **ULAplus specification** (community-developed) — the palette extension's programmer reference
- **EightyOne emulator** ([SourceForge](http://www.aptuning.com/EightyOne-DS/)) — implements ULAplus and ZX-Uno extensions for development testing
- **ZEsarUX emulator** ([GitHub: chernandezba](https://github.com/chernandezba/zesarux)) — another emulator with strong ZX-Uno support
