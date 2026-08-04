[← Home](../../README.md) · [New Gen Hardware](README.md)

# ZX Evolution — The Modern Russian Z80 + CPLD Spectrum

The **ZX Evolution** (also known as **ZX Evo**, **Pentagon Evo**, or **PentEvo**) is a modern Russian Spectrum-family computer designed by **Vladimir "vslav" Kladov** and the NedoPC team (2007–2010). It is a **hybrid architecture**: a real Z80 CPU and real SRAM paired with **three Altera programmable logic devices** — a main **EP1K50 FPGA** (an ACEX 1K family chip), an **EPM7128 CPLD** for glue logic, and an **EPM3032A CPLD** for auxiliary decoding — plus an **Atmel ATmega128 microcontroller** for peripheral management (PS/2 keyboard and mouse, SD card via SPI, real-time clock). This distinguishes it from the pure-FPGA recreations (Next, ZX-Uno) and the older discrete-logic clones (Pentagon, Scorpion).

The ZX Evolution is the **spiritual successor to the Pentagon** — the most popular Russian Spectrum clone of the 1990s. It preserves the Pentagon's memory map, TR-DOS disk interface, and software library while adding modern features: PS/2 keyboard and mouse, IDE storage, SVGA output at multiple resolutions, 4 MB of paged RAM, an SD card interface, and the **NeoGS** General Sound-compatible audio expansion. For the Russian-scene developer, the ZX Evolution is **the modern Pentagon** — the same software base, but with hardware that does not suffer from 30-year-old capacitor rot.

> [!NOTE]
> This article covers the **hardware platform** — what the ZX Evolution is, its physical architecture, its programming model, and its firmware configurations. For the **FPGA internals** (CPLD design, the T80 soft-core, BaseConf bitstream architecture, verification methodology), see [11_emulation/fpga/zxevo.md](../../11_emulation/fpga/zxevo.md). For the OS-level details (NextZXOS-like dot commands, file system, dot-command dispatch), see [evo_os.md](../../04_operating_systems/evo_os.md). For BaseConf and TS-Conf firmware configurations, see [baseconf.md](baseconf.md) and [ts_conf.md](ts_conf.md) respectively.

---

## Why a "Hybrid" Architecture?

By 2007, the Russian Spectrum scene had two paths forward:

1. **Pure FPGA** — like the Western ZX Spectrum Next, replace the entire machine with an FPGA soft-core. Pro: perfect timing fidelity, easy to extend. Con: requires FPGA development tools, not "real hardware".
2. **Modern discrete components** — keep the real Z80 CPU, but use a combination of FPGA + CPLDs (instead of hundreds of discrete TTL chips) for glue logic and video generation. Pro: feels like classic hardware, easy to debug with a logic analyzer. Con: more complex than a single FPGA, but far more capable than discrete TTL alone.

Kladov chose path 2 for the ZX Evolution. The result is a machine that:

- Has a **real Z80 CPU** at its heart (no soft-core approximation)
- Uses a **3-chip Altera programmable logic solution**: the **EP1K50 FPGA** (main video/memory/peripheral logic), the **EPM7128 CPLD** (address decoding and paging), and the **EPM3032A CPLD** (auxiliary I/O decoding)
- Includes an **Atmel ATmega128 microcontroller** for peripheral management (PS/2 keyboard/mouse, SD card via SPI, RTC, USB-style connectors)
- Is **binary-compatible with the Pentagon 1024** at the hardware level (memory banking, video timing, I/O ports)

For Russian-scene software — which targets the Pentagon and expects exact Pentagon behavior — the ZX Evolution is the most authentic modern platform. It is **not** a Next competitor: the Next targets the Western software library, while the ZX Evolution targets the Russian one.

---

## Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | **Real Z80** (Zilog Z84C00 or Russian KR1858VM1), 3.5/7/14 MHz |
| **Main FPGA** | **Altera EP1K50** (ACEX 1K family, 50,000 gates) — video generation, memory arbitration, extended peripherals |
| **Glue CPLD** | **Altera EPM7128S** — address decoding and memory paging |
| **Auxiliary CPLD** | **Altera EPM3032A** — secondary I/O decoding |
| **Peripheral controller** | **Atmel ATmega128** MCU — handles PS/2 keyboard/mouse, SD card via SPI, RTC, USB-style connectors |
| **RAM** | **4 MB** paged SRAM (vs. Pentagon's 128 KB / 512 KB / 1 MB) |
| **ROM** | **512 KB flash** — holds multiple ROM images (TR-DOS, 128K BASIC, 48K BASIC, service) |
| **Video output** | **SVGA** at multiple resolutions — 48K VGA, 128K VGA, Pentagon VGA, 60 Hz VGA modes (selectable via Scroll Lock at runtime) |
| **Storage** | **IDE** (for CF cards and hard disks) + **SD card via ATmega SPI** + **Beta 128 disk interface** |
| **Keyboard** | **PS/2** PC keyboard (via ATmega) |
| **Mouse** | **PS/2** mouse (via ATmega) |
| **Audio** | **AY-3-8910** at Pentagon clock + beeper |
| **Joystick** | **Kempston** at `#1F` |
| **RTC** | Battery-backed, accessible via ATmega |
| **Gluk socket** | For connecting a real-time clock / NVRAM module |
| **Expansion** | **ZXBUS** edge connector (Pentagon / Russian standard) — accepts Pentagon peripherals including the **NeoGS** General Sound-compatible sound card |
| **Case** | Usually sold as bare board (users provide their own case — typically a PC ATX case with custom PSU wiring) |

The defining hardware choice is the **3-chip Altera programmable logic solution**. Where the Pentagon uses ~50 discrete 74LS-series TTL chips for address decoding and memory paging, the ZX Evolution uses an **EP1K50 FPGA + EPM7128 CPLD + EPM3032A CPLD**. This dramatically reduces chip count, increases reliability, and — crucially — makes the design **reprogrammable**: new firmware (a "BaseConf") can redefine the memory map and port layout without hardware changes. The EP1K50 FPGA is the most important of the three — it holds the video generation logic, memory arbitration, and the extended peripheral interfaces that go beyond what discrete TTL could provide.

---

## Pentagon 1024 Compatibility

The ZX Evolution's primary design goal is **exact Pentagon 1024 compatibility**. Software that runs on a real Pentagon 1024 (which is most Russian Spectrum software from the 1990s onward) should run identically on the ZX Evolution. This includes:

| Feature | Pentagon 1024 | ZX Evolution | Compatible? |
|---|---|---|---|
| **Memory banking** | `#7FFD` + `#EFF7` (extended paging) | Identical | Yes |
| **Video timing** | 71,680 T-states, 320 lines, 48.83 Hz, no contention | Identical | Yes |
| **I/O port layout** | Standard Pentagon ports | Identical | Yes |
| **Beta 128 disk interface** | VG93 (FD1793) at standard port addresses | Identical | Yes |
| **AY-3-8910 sound** | At Pentagon port addresses and clock rate | Identical | Yes |
| **Floating bus** | Returns `#FF` (no ULA contention) | Identical | Yes |
| **INT timing** | At line 304, T=0 (Pentagon-standard position) | Identical | Yes |

The result: Russian-scene demos, games, and system software written for the Pentagon run on the ZX Evolution **without modification**. This is the machine's core value proposition.

---

## Extensions Beyond Standard Pentagon

Beyond Pentagon compatibility, the ZX Evolution adds several features the original Pentagon lacked:

| Extension | Pentagon | ZX Evolution |
|---|---|---|
| **CPU speed** | 3.5 MHz only | **3.5 / 7 / 14 MHz** (turbo modes) |
| **RAM** | 128K / 512K / 1 MB | **4 MB** paged |
| **Keyboard** | Sinclair matrix (rubber-key) | **PS/2 PC keyboard** |
| **Mouse** | Kempston mouse (rare) | **PS/2 mouse** |
| **Storage** | Beta 128 floppy only | **IDE** + **SD card** + Beta 128 |
| **Video output** | Composite / RF | **SVGA** (multiple resolutions) |
| **RTC** | None | **Battery-backed RTC** (Dallas CMOS, configurable) |
| **NVRAM** | None | **Gluk socket** for NVRAM module |

These extensions are presented to software via additional I/O ports that do not conflict with the original Pentagon port layout. Software that does not use the extensions simply ignores them.

### Video Output and Timing Modes

The ZX Evolution's video subsystem supports **multiple timing configurations**, switchable at runtime via the **Scroll Lock** key (via the EVO Reset Service boot menu). The available modes are:

| Timing mode | Use case |
|---|---|
| **48K VGA** | Original Sinclair 48K timing (69,888 T-states, 312 scanlines) |
| **128K VGA** | Sinclair 128K timing |
| **PENT VGA** | Pentagon timing (71,680 T-states, 320 scanlines) |
| **60 Hz VGA** | NTSC-compatible timing for non-PAL displays |

Choosing the right timing mode is critical for **pixel-perfect output** with multicolor effects and cycle-exact code. A common benchmark is the **Shock Megademo part II** — a multicolor scroll in paper and border that requires precise Pentagon timing. The ZX Evolution displays this demo correctly, but only if the correct timing mode is selected.

### Boot Menu — EVO Reset Service

The ZX Evolution boots into the **EVO Reset Service** menu after a reset (or via the F12 key). This menu provides:

- **File browsing** of the SD card — load `*.TAP` files, snapshots (`.SNA`, `.Z80`), TR-DOS images (`.TRD`, `.SCL`)
- **CMOS editor** — modify real-time clock and NVRAM settings (BCD format)
- **ROM management** — add, delete, update ROM images in the flash
- **Firmware update** — flash new BaseConf or TS-Conf bitstreams
- **Keyboard testing tool**
- **Mode switching** — between EVO Reset Service and Wild Commander (TS-Conf's file manager)

The EVO Reset Service is updated independently from the firmware; users should keep it current to avoid boot errors (later versions like `zxevo.rom v0.58.16` fix issues found in earlier releases like `v0.58.09`).

### Turbo Mode Programming

The ZX Evolution's turbo modes (7 MHz and 14 MHz) are controlled via a port:

```z80
enable_turbo_14:
        ld  bc, #DFFD            ; (or #1FFD, depending on BaseConf)
        in  a, (c)
        or  #20                  ; bit 5 = turbo 14 MHz
        out (c), a
        ; CPU now runs at 14 MHz
        ; ... do work ...
        ; Restore 3.5 MHz before accessing slow peripherals (Beta 128, AY)
        and  %10011111           ; clear turbo bits
        out (c), a
        ret
```

> [!WARNING]
> Turbo mode affects **all** timing — including the Beta 128 floppy controller and the AY sound chip, which expect 3.5 MHz access rates. Always restore 3.5 MHz before accessing these peripherals. The ZX Evolution's BIOS handles this automatically; direct hardware access code must do so explicitly.

---

## Firmware Configurations — BaseConf and TS-Conf

The ZX Evolution's hardware is defined by its **firmware** — the bitstream loaded into the CPLDs and the boot ROM in flash. Two major firmware configurations exist:

| Firmware | Purpose | See |
|---|---|---|
| **BaseConf** | The default — Pentagon 1024 compatibility with extensions | [baseconf.md](baseconf.md) |
| **TS-Conf** | Enhanced video — sprites, tilemap, 512K VRAM, turbo | [ts_conf.md](ts_conf.md) |

Switching between configurations requires **reflashing the CPLD bitstream** (or loading a different bitstream from SD card on later revisions). It is not a runtime switch — the machine boots into one configuration and stays there until reboot. This is fundamentally different from the ZX Spectrum Next's runtime mode switching.

For the full details of each firmware configuration, see their dedicated articles: [baseconf.md](baseconf.md) and [ts_conf.md](ts_conf.md).

---

## I/O Port Summary

The ZX Evolution's port map is **superset of the Pentagon's**:

| Port | Function | Pentagon? |
|---|---|---|
| `#FE` | Border, EAR, MIC, keyboard | Yes (48K-compatible) |
| `#1F` | Kempston joystick | Yes |
| `#FADF` / `#FBDF` / `#FFDF` | Kempston mouse | Yes (optional) |
| `#1FFD` | Scorpion-style turbo + extended paging | Yes (Scorpion) |
| `#7FFD` | 128K paging | Yes |
| `#BFFD` / `#FFFD` | AY register data / select | Yes |
| `#DFFD` | Extended paging (Pentagon 1024) | Yes |
| `#EFF7` | Pentagon 1024 extended paging | Yes |
| **#xx** (TS-Conf specific) | Sprite/tilemap/VRAM control | No — TS-Conf only |
| **IDE ports** | CompactFlash / hard disk access | No — ZX Evo extension |
| **SPI ports** (via ATmega) | SD card access | No — ZX Evo extension |
| **RTC ports** (via ATmega) | Real-time clock read/write | No — ZX Evo extension |

For the BaseConf-specific ports, see [baseconf.md](baseconf.md). For TS-Conf-specific ports, see [ts_conf.md](ts_conf.md).

---

## Software Ecosystem

The ZX Evolution has a thriving Russian-scene software ecosystem that goes well beyond running legacy Pentagon software. Major components:

### NedoOS — Multitasking Operating System

**NedoOS** is a multitasking operating system for the ZX Evolution, actively developed since 2018 by Aleksey Morozov (Moroz). It is the most ambitious modern OS for any Spectrum-family machine. Features:

- **Command prompt** with VT100 terminal output
- **Dual-panel file navigator** (NedoVigator)
- **Networking stack** — HTTP downloading, IRC client, FTP, Telnet (client and servers)
- **Multitasking** — multiple applications can run concurrently
- **TCP/IP** over Ethernet or Wi-Fi (via Zifi)

NedoOS is the closest any Spectrum-family machine has come to feeling like a modern networked computer. It runs on BaseConf and TS-Conf configurations.

### Wild Commander — TS-Conf File Manager

When the ZX Evolution is flashed with TS-Conf, it boots into **Wild Commander** — a dual-panel file manager with extensive plugins:

- Music player (multiple module formats)
- Image viewers (BMP, PCX, SCR)
- TAP/TRD/SCL image loader
- Built-in text editor

Wild Commander is the de facto standard launcher for TS-Conf-targeted software and is the entry point for most TS-Conf games and demos.

### NeoGS — General Sound Expansion

The **NeoGS** is a hardware sound card that plugs into the ZX Evolution's ZXBUS expansion slot. It is compatible with the legendary **General Sound** specification (a Russian 12-bit sampling synthesizer with its own Z80 subsystem) and adds:

- **MP3 playback** (decoded by an on-board decoder chip)
- **Module playback** (MOD, XM, S3M formats)
- **Sampled instruments** for game soundtracks
- **Second SD card slot** (independent storage)

NeoGS is supported by many Russian games and demos. It is the modern successor to the original General Sound card from the 1990s.

### Zifi — Wi-Fi Connectivity

**Zifi** is an ESP8266-based Wi-Fi module that connects to the ZX Evolution via the ZXBUS or a dedicated header. With the appropriate firmware and drivers, Zifi enables:

- **Wi-Fi connectivity** via AT commands over serial
- **TCP/UDP sockets** accessible from Z80 code
- **HTTP client** for downloading files
- **NTP time sync** for the RTC

Zifi support is built into NedoOS and several other modern programs. It makes the ZX Evolution one of the few WiFi-capable Spectrums alongside the ZX Spectrum Next and the ZX-Uno (with its ESP-12 module).

### VideoDAC — Enhanced Color Output

In TS-Conf configurations, an optional **VideoDAC** add-on provides enhanced color depth for IDE video playback and graphics editors. This enables smoother color gradients and more accurate video playback than the standard TS-Conf palette can provide.

### Notable Software Ports

The ZX Evolution (with TS-Conf) has received several high-profile ports of games from other platforms:

- **Sonic the Hedgehog** — ported from the Sega Master System, demonstrating TS-Conf's sprite and tilemap capabilities
- **Multiple Sega Master System games** — ported by Russian developers using TS-Conf's enhanced video hardware

These ports are technically impressive demonstrations of what TS-Conf can achieve, often looking closer to the original Master System versions than to traditional Spectrum software.

---

## Hardware Production and Community

### Production

ZX Evolution boards are produced by **Vitaliy "Tetroid"** in Novosibirsk, Russia, and sold through **tetroid.nedopc.com**. International buyers can communicate in English with Tetroid directly. Payment is typically via PayPal (Friends and Family), and shipping from Novosibirsk takes 2–3 weeks to most international destinations.

The board ships with antistatic packaging and includes:

- The ZX Evolution mainboard (assembled and tested)
- Peripheral cards (if ordered separately): NeoGS, ZXUSBNET
- RGB-to-CVBS/S-video converter (for composite video output)
- Keyboard stickers for Russian/Cyrillic layout
- Rear cover of peripherals for PC-style case mounting

### Firmware Flashing Procedure

Updating the ZX Evolution's FPGA bitstream (BaseConf or TS-Conf) is a two-stage process using the board's hardware reset buttons:

1. **Copy `zxevo_fw.bin`** (the firmware bundle, ~1 MB) to the root of the SD card
2. **Copy `ts-bios.rom`** and Wild Commander files to the SD card root
3. **Flash the FPGA**: hold down **SOFT RESET (J6)** and momentarily press **HARD RESET (J9)** while keeping soft reset depressed. The power LED will flash rapidly during upload; error beeps indicate a problem
4. **Flash the TS BIOS** via BaseConf menu: R. Service → U. Update custom ROM → select `ts-bios.rom`
5. **Configure NVRAM**: press `RShift+F2` to enter NVRAM options, set boot device as SD-Z Controller and "Reset to" as `BD boot.$c`
6. **Verify**: press F12 for reset, `LShift+F2` to switch between EVO Reset Service and Wild Commander

> [!WARNING]
> A failed firmware upgrade can **brick the ZX Evolution**. Always use a known-good SD card and verified firmware images. There is an alternative flashing method via serial port using XMODEM protocol for emergency recovery.

### Community Hubs

The ZX Evolution has a dedicated Russian-language community:

- **NedoPC forum** ([nedopc.org](http://nedopc.org)) — primary development hub
- **zx-pk.ru forum** — broader Russian Spectrum community
- **forum.tslabs.info** — TS-Conf-specific discussions
- **tetroid.nedopc.com** — official hardware vendor
- **Pouet.net** — ZX Enhanced and TS-Conf demo releases
- **Retroscene.org** — TS-Conf demo archive

Most documentation is in Russian; international users rely on machine translation. The ZX Evolution team and community are active and welcoming to non-Russian-speaking developers willing to engage.

---

## Hardware vs. Next — Decision Matrix

| Aspect | ZX Evolution | ZX Spectrum Next |
|---|---|---|
| **Origin** | Russia (NedoPC team) | UK (SpecNext team) |
| **Primary compatibility** | **Pentagon 1024** (Russian) | Original 48K/128K (Sinclair) |
| **Architecture** | Real Z80 + CPLD glue | FPGA soft-core (Z80N) |
| **Extended graphics** | TS-Conf (sprites/tilemap, via firmware swap) | Layer 2 / sprites / tilemap / copper (always available) |
| **Storage** | CF + SD (SPI) + Beta 128 floppy | SD + IDE |
| **Output** | VGA, composite | HDMI, VGA, composite |
| **Keyboard** | PS/2 (external) | Built-in + PS/2 |
| **Case** | Bare-board (usually) | Available with case |
| **Community language** | Primarily Russian | Primarily English |
| **Software library** | Russian scene (Pentagon) | Western scene (Sinclair) |

Neither is "better" — they target different communities and different software libraries. The ZX Evolution is the right choice for users interested in the Russian Spectrum scene; the ZX Spectrum Next is the right choice for users interested in the Western scene.

---

## Cross-References

### Companion articles

- [BaseConf firmware](baseconf.md) — the default Pentagon-compatible configuration
- [TS-Conf firmware](ts_conf.md) — the enhanced video configuration (sprites/tilemap/512K VRAM)
- [ZX Evolution FPGA internals](../../11_emulation/fpga/zxevo.md) — CPLD design, T80 soft-core, bitstream architecture
- [Evo OS](../../04_operating_systems/evo_os.md) — OS-level details, dot commands, file system

### Related hardware

- [Pentagon 128](../clones/pentagon.md) — the ZX Evolution's compatibility target
- [Pentagon 1024](../clones/pentagon_1024.md) — the maximum Pentagon configuration (the Evo's default profile)
- [Sprinter](sprinter.md) — Kladov's earlier, more radical Z80 PC design
- [ZX Spectrum Next](zx_next.md) — the Western equivalent
- [ZX-Uno](zx_uno.md) — open-source FPGA Spectrum (smaller feature set)
- [Clone timing](../clones/clone_timing.md) — ZX Evolution's place in the cross-clone timing landscape

---

## References

- **ZX Evolution project** ([nedopc.org](http://nedopc.org/zxevo/)) — official project page with schematics, PCB layouts, and BaseConf downloads
- **ZX Evolution SVN/GitHub** — open-source CPLD and ATmega firmware
- **NedoPC forum** (nedopc.org) — primary community hub, Russian-language
- **[zx-pk.ru](https://zx-pk.ru) forum** — *ZX Evolution* subforum with build guides, repair threads, and software announcements
- [TS-Conf documentation](https://zxevo.ru/) — the enhanced firmware's programmer reference
- [Vladimir Kladov's personal pages](https://zx-pk.ru/) — design notes, history of the project
- **Russian demoscene archives** (CC Chaos Constructions, diHalt, CAFe, FunTop, AXAC, ZX-Dev parties) — ZX Evolution-targeted demos and intros
