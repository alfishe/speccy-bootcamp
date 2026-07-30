[← Home](../../README.md) · [New Gen Hardware](README.md)

# ZX Evolution — The Modern Russian Z80 + CPLD Spectrum

The **ZX Evolution** (also known as **ZX Evo**, **Pentagon Evo**, or **PentEvo**) is a modern Russian Spectrum-family computer designed by **Vladimir "vslav" Kladov** and the NedoPC team (2007–2010). It is a **hybrid architecture**: a real Z80 CPU and real SRAM/DRAM paired with **Altera MAX CPLDs** that handle address decoding, memory paging, and I/O port mapping. This distinguishes it from the pure-FPGA recreations (Next, ZX-Uno) and the older discrete-logic clones (Pentagon, Scorpion).

The ZX Evolution is the **spiritual successor to the Pentagon** — the most popular Russian Spectrum clone of the 1990s. It preserves the Pentagon's memory map, TR-DOS disk interface, and software library while adding modern features: PS/2 keyboard and mouse, IDE storage, SVGA output at multiple resolutions, 4 MB of paged RAM, and an SD card interface. For the Russian-scene developer, the ZX Evolution is **the modern Pentagon** — the same software base, but with hardware that does not suffer from 30-year-old capacitor rot.

> [!NOTE]
> This article covers the **hardware platform** — what the ZX Evolution is, its physical architecture, its programming model, and its firmware configurations. For the **FPGA internals** (CPLD design, the T80 soft-core, BaseConf bitstream architecture, verification methodology), see [11_emulation/fpga/zxevo.md](../../11_emulation/fpga/zxevo.md). For the OS-level details (NextZXOS-like dot commands, file system, dot-command dispatch), see [evo_os.md](../../04_operating_systems/evo_os.md). For BaseConf and TS-Conf firmware configurations, see [baseconf.md](baseconf.md) and [ts_conf.md](ts_conf.md) respectively.

---

## Why a "Hybrid" Architecture?

By 2007, the Russian Spectrum scene had two paths forward:

1. **Pure FPGA** — like the Western ZX Spectrum Next, replace the entire machine with an FPGA soft-core. Pro: perfect timing fidelity, easy to extend. Con: requires FPGA development tools, not "real hardware".
2. **Modern discrete components** — keep the real Z80 CPU, but use CPLDs (instead of hundreds of discrete TTL chips) for glue logic. Pro: feels like classic hardware, easy to debug with a logic analyzer. Con: less flexible than a full FPGA, no Layer 2 / sprites / tilemap.

Kladov chose path 2 for the ZX Evolution. The result is a machine that:

- Has a **real Z80 CPU** at its heart (no soft-core approximation)
- Uses **two Altera MAX CPLDs** (EPM7128S + EPM3032A) for glue logic — far fewer chips than the Pentagon's ~50 discrete TTLs
- Includes an **Atmel ATmega microcontroller** for peripheral management (PS/2, SD card, RTC)
- Is **binary-compatible with the Pentagon 1024** at the hardware level (memory banking, video timing, I/O ports)

For Russian-scene software — which targets the Pentagon and expects exact Pentagon behavior — the ZX Evolution is the most authentic modern platform. It is **not** a Next competitor: the Next targets the Western software library, while the ZX Evolution targets the Russian one.

---

## Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | **Real Z80** (Zilog Z84C00 or Russian KR1858VM1), 3.5/7/14 MHz |
| **Glue logic** | **Altera MAX CPLDs** — EPM7128S (main) + EPM3032A (auxiliary decoding) |
| **Peripheral controller** | **Atmel ATmega8515** MCU — handles PS/2 keyboard/mouse, SD card via SPI, RTC |
| **RAM** | **4 MB** paged SRAM (vs. Pentagon's 128 KB / 512 KB / 1 MB) |
| **ROM** | **512 KB flash** — holds multiple ROM images (TR-DOS, 128K BASIC, 48K BASIC, service) |
| **Video output** | **SVGA** at multiple resolutions — 256×192, 384×304 (Pentagon extended), 16/256-color extended modes |
| **Storage** | **IDE** (for CF cards and hard disks) + **SD card via ATmega SPI** + **Beta 128 disk interface** |
| **Keyboard** | **PS/2** PC keyboard (via ATmega) |
| **Mouse** | **PS/2** mouse (via ATmega) |
| **Audio** | **AY-3-8912** at Pentagon clock + beeper |
| **Joystick** | **Kempston** at `#1F` |
| **RTC** | Battery-backed, accessible via ATmega |
| **Gluk socket** | For connecting a real-time clock / NVRAM module |
| **Expansion** | **Pentagon / Russian edge connector** standard |
| **Case** | Usually sold as bare board (users provide their own case) |

The defining hardware choice is the **CPLD glue logic**. Where the Pentagon uses ~50 discrete 74LS-series TTL chips for address decoding and memory paging, the ZX Evolution uses a single Altera EPM7128S CPLD. This dramatically reduces chip count, increases reliability, and — crucially — makes the design **reprogrammable**: new firmware (a "BaseConf") can redefine the memory map and port layout without hardware changes.

---

## Pentagon 1024 Compatibility

The ZX Evolution's primary design goal is **exact Pentagon 1024 compatibility**. Software that runs on a real Pentagon 1024 (which is most Russian Spectrum software from the 1990s onward) should run identically on the ZX Evolution. This includes:

| Feature | Pentagon 1024 | ZX Evolution | Compatible? |
|---|---|---|---|
| **Memory banking** | `#7FFD` + `#EFF7` (extended paging) | Identical | Yes |
| **Video timing** | 71,680 T-states, 320 lines, 48.83 Hz, no contention | Identical | Yes |
| **I/O port layout** | Standard Pentagon ports | Identical | Yes |
| **Beta 128 disk interface** | VG93 (FD1793) at standard port addresses | Identical | Yes |
| **AY-3-8912 sound** | At Pentagon port addresses and clock rate | Identical | Yes |
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
| **RTC** | None | **Battery-backed RTC** |
| **NVRAM** | None | **Gluk socket** for NVRAM module |

These extensions are presented to software via additional I/O ports that do not conflict with the original Pentagon port layout. Software that does not use the extensions simply ignores them.

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
- **zx-pk.ru forum** — *ZX Evolution* subforum with build guides, repair threads, and software announcements
- **TS-Conf documentation** (tsl / Aleksandr Zhuravlev) — the enhanced firmware's programmer reference
- **Vladimir Kladov's personal pages** — design notes, history of the project
- **Russian demoscene archives** (CC Chaos Constructions, diHalt, CAFe, FunTop, AXAC, ZX-Dev parties) — ZX Evolution-targeted demos and intros
