[← Home](../../README.md) · [New Gen Hardware](README.md) · [ZX Evolution](zx_evo.md)

# BaseConf — The ZX Evolution's Default Firmware

**BaseConf** is the default **firmware configuration** for the ZX Evolution — the bitstream loaded into the board's Altera MAX CPLDs that defines what hardware the Z80 sees. Designed by **Vladimir "vslav" Kladov** as the ZX Evolution's launch configuration, BaseConf implements the full **Pentagon 1024** specification plus a set of well-documented extensions: turbo mode, IDE storage, PS/2 keyboard, SD card, RTC, and SVGA output.

For software developers, BaseConf is the **"known-good target"** for ZX Evolution software. If your program runs under BaseConf, it runs on the vast majority of ZX Evolution boards in the field. This article covers BaseConf as a programmer-visible configuration: what hardware it presents, how the memory map differs from a bare Pentagon 1024, what extra ports it exposes, and what compatibility pitfalls exist.

> [!NOTE]
> This article covers the **firmware configuration** (what the Z80 sees). For the underlying hardware platform (real Z80 + CPLD + ATmega), see [zx_evo.md](zx_evo.md). For the **OS-level details** (boot ROM, dot commands, file system), see [evo_os.md](../../04_operating_systems/evo_os.md). For the enhanced firmware alternative (sprites, tilemap, 512K VRAM), see [ts_conf.md](ts_conf.md).

---

## What BaseConf Defines

A BaseConf is a **complete hardware definition** — changing it changes everything the Z80 sees:

| Aspect | Defined by BaseConf |
|---|---|
| **CPU core** | T80 (Z80-compatible soft-core) running at the configured speed |
| **Memory map** | Which RAM banks are mapped where, how paging works |
| **Video modes** | Standard Spectrum, ATM Turbo, text mode — and their address layouts |
| **Sound chips** | Which AY chips are present, at which addresses |
| **I/O ports** | Which ports respond to which devices |
| **Timing** | CPU clock speeds, video timing, interrupt frequency |
| **Disk interfaces** | Beta 128 + IDE + SD + Gluk RTC support |

In short, BaseConf is the **hardware definition of the ZX Evolution as the Z80 sees it**. Changing the BaseConf changes what hardware the Z80 sees.

---

## The Default Profile — Pentagon 1024

The default BaseConf implements the **Pentagon 1024** standard — the most widely-supported Russian Spectrum configuration. Most Russian software is tested against it.

| Feature | Pentagon 1024 BaseConf | Notes |
|---|---|---|
| **RAM** | **1024 KB**, 64 banks of 16 KB | Paged via `#7FFD` + extended port |
| **Video** | Standard Spectrum 256×192 | Plus multicolor and text modes via port `#FF` and ATM Turbo ports |
| **Sound** | AY-3-8910 at `#FFFD`/`#BFFD` | Standard Pentagon clock |
| **Disk** | Beta 128 at standard Pentagon ports | Optional secondary FDC |
| **I/O layout** | Standard Pentagon + extensions | See port summary below |

This is the **compatibility configuration** — it runs the vast majority of Russian Spectrum software. Most users keep their ZX Evolution in this configuration most of the time.

---

## Memory Map — The Three Paging Ports

BaseConf implements three paging ports, providing flexibility beyond a bare Pentagon 128:

### Port `#7FFD` — 128K Paging (Standard)

The standard Sinclair 128K paging port. Works identically to a Pentagon 128 — selects among the first 8 RAM banks (0–7), toggles the screen between banks 5 and 7, and selects ROM 0 / ROM 1.

### Port `#DFFD` — Pentagon Extended Paging

Provides access to banks beyond the first 8. The bit layout differs slightly from other clones:

| Bit | Function |
|---|---|
| 0–2 | **Extended bank bits** — combined with `#7FFD` bits 0–2 to form a 6-bit bank number |
| 3 | Reserved |
| 4 | (varies by BaseConf version) |
| 5 | Reserved |
| 6 | (varies by BaseConf version) |
| 7 | Reserved |

The full bank number is `(#DFFD & 0x07) × 8 + (#7FFD & 0x07)`, giving 64 banks = 1024 KB. This is identical to the Pentagon 1024 formula.

### Port `#EFF7` — Pentagon 1024 Extended Paging

The "true" Pentagon 1024 extension port — uses a full 8-bit identity decode (zero aliases). On BaseConf, this port provides the same 6-bit bank number as `#DFFD`, but with **full address decoding** — writes to other addresses do not affect the bank register. Software targeting the original Pentagon 1024 hardware should use `#EFF7`.

> [!WARNING]
> **Do not mix `#DFFD` and `#EFF7` writes.** Both ports affect the same bank register on BaseConf, but with different decode masks. Mixing them produces inconsistent behavior across BaseConf revisions. Pick one and stick with it.

---

## BaseConf Extensions Beyond Pentagon

BaseConf adds several features the original Pentagon 1024 lacked. These extensions are presented through additional I/O ports that do not conflict with the Pentagon port layout.

### Turbo Mode

BaseConf supports CPU speeds of **3.5 MHz, 7 MHz, and 14 MHz** — switchable at runtime via a port write. Turbo mode accelerates all CPU-bound code but does not affect video timing (the frame rate stays at 48.83 Hz).

| Port | Bits | Function |
|---|---|---|
| `#DFFD` (in some BaseConf versions) | 6 | Turbo enable (1 = 14 MHz) |
| `#1FFD` (Scorpion-style, in some versions) | 5–6 | Turbo speed select |

> [!WARNING]
> Turbo mode accelerates access to **all** peripherals, including the Beta 128 FDC and the AY chip — which expect 3.5 MHz timing. Always restore 3.5 MHz before accessing these peripherals, or use the BIOS wrappers that handle it automatically.

### IDE Interface

BaseConf provides an **8-bit IDE interface** for CompactFlash cards and hard disks. The IDE controller is mapped to ports in the `#A0`–`#B7` range (Kay-compatible):

| Port | Function |
|---|---|
| `#A0` | IDE data (read/write 8 bits at a time) |
| `#A1`–`#A7` | IDE register select (error, features, sector count, LBA low/mid/high, device/head) |
| `#B0`–`#B7` | IDE status / command / control |

The IDE interface is **8-bit** (not 16-bit) — each 16-bit word from the drive requires two port reads. This is the same limitation as the Kay's IDE; software written for the Kay IDE works on BaseConf with minor adjustments.

### SD Card via SPI

BaseConf exposes an SD card interface via the ATmega's SPI controller, accessible through a port pair (typically `#57` and `#77`). This is a software-driven SPI — the ATmega handles the bit-banging, the Z80 just reads/writes bytes. SD cards up to 32 GB are supported (FAT16/FAT32).

### PS/2 Keyboard and Mouse

The ATmega handles the PS/2 protocol for both keyboard and mouse, presenting a simplified byte-stream interface to the Z80. Keyboard scan codes are read from a port (typically `#FE` for compatibility, with extended keys available at a secondary port); mouse movement is read from a separate port pair.

### Real-Time Clock (RTC)

A battery-backed RTC (typically DS12887 or similar) is accessible via a port pair, providing date and time. The BIOS uses this for filesystem timestamps.

---

## ROM Configuration

BaseConf supports **multiple ROM images** stored in flash memory, selectable at boot time. The standard ROM set:

| ROM slot | Contents |
|---|---|
| `0` | **TR-DOS ROM** — Russian disk operating system (used for disk operations) |
| `1` | **128K BASIC ROM** — standard 128K BASIC editor |
| `2` | **48K BASIC ROM** — for 48K software compatibility |
| `3` | **Service ROM** — diagnostic and configuration menus |
| `4`–`7` | **Custom ROMs** — user-flashed ROM images (e.g., alternative DOS, BIOS extensions) |

The boot menu (accessible via a key combination at power-on) lets the user select which ROM to boot from, configure turbo mode, and set other options.

### ROM Banking and TR-DOS Coexistence

The TR-DOS ROM is **banked into the memory map on demand** — when software calls the TR-DOS entry point at `#3D13`, the BIOS pages the TR-DOS ROM into `#0000`–`#3FFF` and transfers control. When TR-DOS returns, the original ROM is paged back in. This is the same mechanism the Pentagon 128 uses; existing TR-DOS software works unchanged.

---

## Compatibility Profiles

Beyond the default Pentagon 1024 profile, BaseConf implements several **alternative compatibility profiles** — each presents a different classic machine to the Z80:

| Profile | What it does |
|---|---|
| **Pentagon 1024** (default) | Most Russian software; default daily use |
| **Pentagon 128** | Older Pentagon-128 software with compatibility issues |
| **ATM Turbo** | ATM Turbo-specific software (alternative Russian clone with its own video modes) |
| **48K** | Original Sinclair software that misbehaves on clones |
| **128K** | Original 128K/+2 software |
| **TS-Conf** | Modern TS-Conf-aware software (requires TS-Conf BaseConf — see [ts_conf.md](ts_conf.md)) |

Switching profiles is a **reboot operation** — the user selects the new BaseConf in the boot menu, and the CPLD is reprogrammed on the next power cycle. This is fundamentally different from the ZX Spectrum Next's runtime mode switching.

---

## Updating BaseConf

Updating BaseConf is similar to updating the boot ROM:

1. **Load a new bitstream** from the SD/CF card
2. **Use the boot ROM's BaseConf update utility** to reflash the CPLD's configuration flash
3. **Reboot** — the CPLD is reconfigured at the next power-on

Because BaseConf is the lowest layer of the system (it defines the hardware itself), a corrupt BaseConf is a more serious problem than a corrupt boot ROM. If BaseConf is corrupted, the CPLD will not be configured, and the board will be completely non-functional until the bitstream is rewritten via JTAG.

The community therefore recommends **keeping a known-good BaseConf image on a separate SD card** for emergencies.

---

## Cross-References

- [ZX Evolution hardware platform](zx_evo.md) — physical board, real Z80 + CPLD + ATmega
- [TS-Conf firmware](ts_conf.md) — the enhanced firmware (sprites, tilemap, 512K VRAM)
- [ZX Evolution FPGA internals](../../11_emulation/fpga/zxevo.md) — CPLD design, bitstream architecture
- [Evo OS](../../04_operating_systems/evo_os.md) — OS-level details, dot commands, file system
- [Pentagon 128](../clones/pentagon.md) — the BaseConf's primary compatibility target
- [Pentagon 1024](../clones/pentagon_1024.md) — the maximum Pentagon configuration
- [Kay 1024](../clones/kay.md) — Kay's IDE interface (BaseConf's IDE is Kay-compatible)
- [ATM Turbo](../clones/atm_turbo.md) — alternative Russian clone (BaseConf has an ATM Turbo profile)

---

## References

- **BaseConf source code** ([nedopc.org](http://nedopc.org/zxevo/)) — official BaseConf bitstream source
- **ZX Evolution documentation** (Russian) — BaseConf port map and extension reference
- **NedoPC forum** — BaseConf-specific threads, bug reports, feature requests
- **zx-pk.ru forum** — *ZX Evolution* subforum with BaseConf programming guides
- **TS-Conf documentation** — comparison reference for the enhanced firmware alternative
- **Pentagon 1024 specification** (1989, Russian) — the original hardware specification that BaseConf implements
