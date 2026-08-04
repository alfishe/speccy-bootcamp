[← Home](../../README.md) · [Peripherals](README.md)

# Z-Controller — Russian Multi-I/O Peripheral (PS/2 + IDE + SD)

## Overview

The **Z-Controller** is a multi-function expansion board for the ZX Spectrum's ZX Bus, designed by Russian hardware engineer **Alexey Zhabin (handle: KingOfEvil)** in **2007**. It is one of a small family of "post-Soviet" peripherals built in the late-2000s Russian Speccy revival, alongside the **ZX Evolution** (TS-Conf), **Pentagon 1024 SL 2.x**, and the **ATM Turbo 3**. Where the 1980s and 1990s Soviet scene had to make do with Beta 128 floppy interfaces, custom IDE adapters (Nemo IDE, Smoker, etc.), and various ad-hoc PS/2 keyboard adapters, the Z-Controller combined all of these on a single board:

- **PS/2 keyboard input** (full IBM PC AT-style keyboard support, no Spectrum membrane needed)
- **PS/2 mouse input** (presented to software as a Kempston Mouse)
- **8-bit IDE interface** (compatible with the earlier Nemo IDE — CompactFlash, hard disk, CD-ROM)
- **SD card socket** (SPI-mode, accessible via a software-driven driver)

The Z-Controller is interesting for several reasons beyond its feature set. First, it was one of the first popular SD-card interfaces on the Russian scene, predating the more widely-known DivMMC by a couple of years and aimed at a different audience (the Russian clone ecosystem, not the Western Sinclair-original owner). Second, its **open hardware / closed firmware source** model — schematics and binary firmware images are public, but the firmware source and PCB layout files are not — was an unusual middle path between the fully-open projects (DivMMC, SMART Card) and the fully-commercial ones (MB03+ Ultimate). Third, its design was influential enough that **its functionality has been re-implemented as a hardware block inside the MB03+ Ultimate FPGA successor** (see [mb02.md](mb02.md)) and is used as the standard SD/IDE interface on the **ZX Spectrum Neo** (a modern Russian Spectrum-compatible clone).

This article covers the Z-Controller's architecture, port map (where documented), software ecosystem, and how it compares to the alternatives (DivMMC, DivIDE, SMART Card, ZXMMC). For the broader context of mass-storage peripherals, see [03_io/storage](../storage/README.md); for the ZX Bus connector it plugs into, see [zx_bus.md](zx_bus.md); for the Kempston Mouse protocol it emulates, see [mouse.md](mouse.md).

---

## Why the Z-Controller Mattered

The Russian ZX Spectrum clone scene of the late 1990s and early 2000s had reached an unusual position. The hardware was mature (Pentagon 128/512/1024, Scorpion ZS-256 Turbo+, Profi 5103, Kay 1024) and the software scene was active, but the **storage situation had stagnated**. Almost everyone was still using the Beta 128 / TR-DOS floppy interface, with its 178 KB DD disk limit and its slow PIO data path. The few owners with hard disks had Nemo IDE, Smoker IDE, or similar custom interfaces — each with its own driver software and its own per-clone quirks. Keyboard and mouse were equally fragmented: the standard 40-key Spectrum membrane was increasingly painful for serious work, and PS/2 mouse support required a separate K-Mouse Turbo or similar interface.

The Z-Controller was the **integrated solution**. A single board plugged into the ZX Bus slot gave the user:

- A **modern mass-storage option** (SD card, multi-GB capacity, FAT filesystem)
- An **upgrade path from Nemo IDE** (full backward compatibility with existing IDE drivers, but on the same board as the SD card)
- **Proper keyboard and mouse input** without needing a separate adapter

For Russian clone owners, this was the closest thing to a "modern peripheral deck" — a single board that brought the Spectrum into the 2000s. It never achieved the international popularity of the DivMMC (which is the SD card interface most Western Spectrum owners know today), but within the Russian-speaking scene it became a standard option, and its design was carried forward into the MB03+ Ultimate and the ZX Spectrum Neo.

---

## Hardware

### Block diagram

```
                  ┌──────────────────────────────────────┐
                  │           Z-Controller                │
                  │                                       │
   ZX Spectrum ───┤  56-pin ZX Bus edge connector        │
   ZX Bus slot    │  (pass-through on most revisions)    │
                  │                                       │
                  │  ┌─────────────────────────────┐     │
                  │  │ Altera EPM7128 CPLD         │     │
                  │  │  - Port decode              │     │
                  │  │  - Kempston mouse emulation │     │
                  │  │  - IDE register latch       │     │
                  │  │  - SD card clock generator  │     │
                  │  └─────────────────────────────┘     │
                  │                                       │
                  │  ┌─────────────────────────────┐     │
                  │  │ KR1878VE1 microcontroller   │     │
                  │  │  - PS/2 keyboard scan-code  │     │
                  │  │    conversion              │     │
                  │  │  - PS/2 mouse packet parse │     │
                  │  │  - Interface to CPLD       │     │
                  │  └─────────────────────────────┘     │
                  │                                       │
                  │  ┌─────────────────────────────┐     │
                  │  │ IDE 40-pin header           │     │
                  │  │  (Nemo IDE compatible)      │     │
                  │  └─────────────────────────────┘     │
                  │                                       │
                  │  ┌─────────────────────────────┐     │
                  │  │ SD card socket              │     │
                  │  │  (SPI mode, 4-wire)         │     │
                  │  └─────────────────────────────┘     │
                  │                                       │
                  │  ┌─────────────────────────────┐     │
                  │  │ PS/2 keyboard (mini-DIN 6)  │     │
                  │  └─────────────────────────────┘     │
                  │                                       │
                  │  ┌─────────────────────────────┐     │
                  │  │ PS/2 mouse (mini-DIN 6)      │     │
                  │  └─────────────────────────────┘     │
                  └──────────────────────────────────────┘
```

### Key chips

| Chip | Function | Notes |
|------|----------|-------|
| **Altera EPM7128** (CPLD) | Glue logic, port decode, mouse register emulation, IDE latch, SD clock | 128 macrocells, in-system programmable via JTAG. Configurable for the host machine's port-decoding convention (Pentagon vs Scorpion vs Profi vs original Sinclair). |
| **KR1878VE1** | PS/2 keyboard and mouse protocol microcontroller | A Russian 8-bit microcontroller from the 1878 family, programmed by KingOfEvil to convert PS/2 scan codes to the matrix form expected by Spectrum software and to convert PS/2 mouse packets to the Kempston Mouse X/Y/button register layout. Communicates with the EPM7128 via a parallel handshake. |

The split between the CPLD and the MCU is significant. The CPLD handles the high-speed, deterministic, port-decoded work — anything that has to respond within a single Z80 I/O cycle. The MCU handles the asynchronous protocol work — bit-banging the PS/2 serial clock and accumulating scan codes or mouse packets — and only reports results to the CPLD when a complete unit (one keypress, one mouse delta triple) is ready. This split is what allows the Z-Controller to claim "no CPU slowdown": the Z80 never has to wait for a scan-code to finish arriving.

### Connectors

The Z-Controller typically provides (exact layout varies by PCB revision):

- **ZX Bus edge connector** (input, from host) — see [zx_bus.md](zx_bus.md)
- **ZX Bus pass-through** (output, for further peripherals) — present on most revisions
- **40-pin IDE header** (for CompactFlash via CF-to-IDE adapter, hard disk, CD-ROM)
- **SD card socket** (full-size SD; SDHC supported via software driver; SDXC not generally supported)
- **Mini-DIN 6 PS/2 keyboard socket**
- **Mini-DIN 6 PS/2 mouse socket**
- (Some revisions) Kempston joystick port on a 9-pin D-sub

---

## I/O Port Map

The Z-Controller's port decode varies depending on the host machine it is configured for. The CPLD firmware is build-time-configurable for either the **Pentagon port layout** (the most common Russian clone convention) or the **original Sinclair port layout**. Both builds expose the same logical functions; only the port addresses differ.

### PS/2 mouse — Kempston Mouse compatible

| Port | Direction | Function |
|------|-----------|----------|
| `#FBDF` (write) | R | Mouse X position (8-bit signed delta) |
| `#FFDF` (write) | R | Mouse Y position (8-bit signed delta) |
| `#FADF` (write) | R | Mouse buttons (bit 0 = left, bit 1 = right, bit 2 = middle) |

These are the standard Kempston Mouse ports — see [mouse.md](mouse.md) for the protocol details. The Z-Controller's mouse emulation presents itself to software exactly like a real Kempston Mouse, so all existing Kempston Mouse software works without modification. There is **no scroll-wheel emulation**; the original Kempston Mouse protocol has no provision for one.

### PS/2 keyboard

The PS/2 keyboard is presented as a custom port-mapped input device. The KR1878VE1 microcontroller maintains an internal queue of converted keypress events; the Z80 reads the queue via a port. Software that supports the Z-Controller's keyboard (notably the **TR-DOS variants shipped with newer Russian clones**, and a number of Russian text editors and disk utilities) reads this port to obtain standard Spectrum row/column matrix coordinates.

Because the keyboard interface was non-standard, software had to explicitly support the Z-Controller. Most Russian clone ROMs from 2008 onward include this support; original Sinclair ROM software does not.

### IDE — Nemo IDE compatible

The IDE block is a **direct implementation of the Nemo IDE port map** — see Nemo IDE documentation (Russian: `speccy.info/Nemo_IDE`). The Nemo IDE convention places the 8-bit IDE register file at a partially-decoded port range, typically using addresses in the `#xx8B` form. The exact port decoding is:

| Port | Function (standard 8-bit IDE register mapped) |
|------|-----------------------------------------------|
| IDE data register | 16-bit wide transfers done as two 8-bit accesses via a latch |
| IDE error / features | |
| IDE sector count | |
| IDE LBA low / sector number | |
| IDE LBA mid / cylinder low | |
| IDE LBA high / cylinder high | |
| IDE head / device | |
| IDE status / command | |

The Z-Controller's IDE block accepts any CompactFlash card in 8-bit True IDE mode, which is the mode used by CF-to-IDE adapters. This makes CompactFlash the de-facto storage medium for Z-Controller users — hard disks work too, but draw too much current from the Spectrum's `+5V` rail to be practical on most clones.

### SD card

The SD card socket is wired in **SPI mode** (the simplest of the three electrical modes the SD card specification defines — see the SD card spec, "SPI Bus Topology" section). The CPLD generates the SPI clock (`SCLK`), manages the controller-out-slave-in (`MOSI`) and controller-in-slave-out (`MISO`) data lines, and asserts the per-card chip-select (`CS`). The Z80 sees this as a pair of ports: a control port (clock divider, CS level, mode bits) and a data port (write to shift out a byte, read to shift one in).

The exact port addresses for the SD card interface are **not consistently documented across sources**. Different firmware revisions and different host-machine configurations use slightly different addresses. The software-side access pattern, however, is consistent:

```z80
; Conceptual SD byte read
sd_read_byte:
        LD   A, SD_CS_ASSERT     ; pull CS low
        OUT  (SD_CTRL), A
        LD   A, #FF              ; dummy byte to shift in
        OUT  (SD_DATA), A        ; shifts out FF, shifts in next byte from card
wait_in:
        IN   A, (SD_STATUS)      ; poll for completion
        AND  SD_READY
        JR   Z, wait_in
        IN   A, (SD_DATA)        ; read the shifted-in byte
        RET
```

The SD card is **not bootable on its own** — there is no on-board BIOS ROM that pages in and reads a boot sector from SD the way the DivMMC does. To use the SD card, the user must first boot from a floppy (TR-DOS) or from IDE (where a small bootloader reads the OS), and then run a driver program. The most common driver is **Wild Disk Copier v1.21+** (by the same author), which adds SD card read/write commands to the TR-DOS environment.

---

## Software Ecosystem

The Z-Controller's software support is **almost entirely Russian-language and Russian-scene-specific**. The major pieces:

### Wild Disk Copier v1.21+

The flagship piece of Z-Controller software, written by KingOfEvil himself. Wild Disk Copier is a general-purpose disk-copy utility for the ZX Spectrum, supporting the usual floppy and hard-disk formats. Starting from version 1.21, it includes **SD card read/write commands** that operate through the Z-Controller's SD port. The utility can:

- Copy files between floppy, IDE, and SD
- Format SD cards with a FAT16 filesystem
- Browse the SD card's directory structure
- Dump and restore disk images (TRD, SCL, FDI) to and from SD

### FAT16 / FAT32 drivers

Several Russian-scene FAT16/FAT32 drivers (originally written for the Nemo IDE / SMK IDE interfaces) were patched to support the Z-Controller's SD port. These provide a POSIX-like file API similar to what esxDOS provides on the DivMMC, but with a different (and incompatible) system-call convention.

### Real-time operating systems

The Russian **iS-DOS** (a CP/M-like OS for the ZX Spectrum, originally targeting the Nemo IDE interface) was patched to support the Z-Controller. iS-DOS on a Z-Controller with a 4 GB SD card feels, charitably, like using an early 1990s Unix workstation — but it works, and a small but active user community still uses it.

The Z-Controller is **not natively supported by esxDOS**. esxDOS targets the DivMMC and DivIDE hardware specifically; the SD card protocol and port map are different on the Z-Controller. A community port called **Z-ESXDOS** was attempted around 2013 but was never completed.

### Emulator support

The Z-Controller is emulated by **Unreal Speccy** (the standard Russian-scene emulator, written by SMT) and by **ZNOS** (a less-widely-used emulator). In both cases, the SD card image is mapped to a folder or disk image on the host filesystem, and the IDE block is mapped to a separate disk image. Emulator support is what has kept Z-Controller-targeted software alive — running it on real hardware requires a physical Z-Controller board, which was produced in modest quantities and is rare today.

---

## Compatibility and Modern Use

### Host machine compatibility

The Z-Controller was designed primarily for the **Russian clone ecosystem**. It works on:

- **Pentagon 128 / 512 / 1024** — the primary target
- **Scorpion ZS-256 / ZS-256 Turbo+** — with a CPLD firmware build for Scorpion port layout
- **Profi 5103** — with a CPLD firmware build for Profi port layout
- **Kay 1024** — with appropriate firmware
- **ATM Turbo 2 / 3** — with appropriate firmware
- **ZX Evolution** — works but somewhat redundant, as the Evolution has built-in SD and IDE

On original Sinclair hardware (48K, 128K "Toastrack", +2, +2A/+3), the Z-Controller works with a Sinclair-targeted CPLD build, but the IDE and SD cards compete for port space with the +2A/+3's expanded paging registers. Most users with original Sinclair hardware are better served by a DivMMC for SD card use.

### Relationship to MB03+ Ultimate

The **MB03+ Ultimate** (see [mb02.md](mb02.md)) is a modern FPGA-based all-in-one interface designed by the Czech 8BC group (LMN128, Blazko/systems). It is not a Z-Controller clone, but its hardware spec sheet lists **"Z-Controller SD slot"** as one of the legacy peripherals it implements in FPGA. This is a software-compatible re-implementation of the Z-Controller's SD card port, allowing software written for the Z-Controller (notably Wild Disk Copier) to run unmodified on the MB03+.

The MB03+'s Z-Controller compatibility is significant because it gives MB03+ owners access to the existing library of Russian-scene SD-card software without requiring emulation layers. For Russian software that targets the Z-Controller's specific port addresses, the MB03+ is the most reliable modern hardware to run it on.

### Relationship to ZX Spectrum Neo

The **ZX Spectrum Neo** (Polish/Russian-designed modern Spectrum clone) uses the Z-Controller's SD card interface as its primary mass-storage mechanism. The Neo's documentation explicitly notes this: "SD card support is handled through the mechanisms of the Z-Controller expansion card". The Neo is essentially a modern Spectrum with a Z-Controller built in — there is no separate add-on board.

---

## Comparison with Alternatives

The Z-Controller is one of several late-2000s / early-2010s SD card interfaces for the ZX Spectrum. The most important alternatives:

| Interface | Year | Connector | Boot method | OS / Driver | Openness | Target audience |
|-----------|------|-----------|-------------|-------------|----------|-----------------|
| **Z-Controller** | 2007 | ZX Bus | Not bootable (driver loaded from floppy or IDE first) | Wild Disk Copier, iS-DOS patches | Schematics public; firmware binary public; source closed | Russian clone owners |
| **DivIDE** | 2005–2007 | ZX Bus | IDE bootable (on-board 8K EEPROM loads `COMMAND2.COM` from IDE) | FAT16 via `fatfs.lib`, esxDOS (later) | Fully open hardware and firmware | Western Sinclair owners, IDE CompactFlash focus |
| **DivMMC** | 2012 | ZX Bus | SD bootable (on-board EEPROM loads esxDOS from SD) | **esxDOS** (FAT16/FAT32, TAP loading, BASIC commands) | Fully open hardware and firmware | Modern Western Spectrum owners (de facto standard SD solution) |
| **SMART Card** | 2014+ | ZX Bus | SD bootable (on-board EEPROM + 16-bank ROM substitution) | Custom ROM manager, ESXDOS-compatible | Open hardware | 48K-only Spectrum owners who want SD + ROM replacement |
| **ZXMMC** | 2010+ | Z80 socket (or edge) | SD bootable via custom ROM | Custom | Open | +2A/+3 owners (the Z80-socket variant targets the +2A/+3 issue specifically) |
| **ZX-HD** | 2018+ | ZX Bus | SD not primary (HDMI video + SD secondary) | Custom | Open | Modern display owners wanting HDMI output |

The Z-Controller's distinctive position in this landscape:

- **Most integrated**: only one combining keyboard, mouse, IDE, and SD on a single board
- **Russian-scene focus**: works seamlessly with Pentagon/Scorpion/Profi/Kay and the TR-DOS ecosystem; does not work seamlessly with Western esxDOS
- **Not standalone bootable**: requires a floppy or IDE bootstrap, unlike the DivMMC and SMART Card
- **Mouse + keyboard included**: the others are storage-only; for input you need a separate Kempston Mouse interface and PS/2 keyboard adapter

For a modern Russian-clone owner who wants a single board covering all four functions, the Z-Controller (or its MB03+ / ZX Spectrum Neo successors) is the obvious choice. For a Western Sinclair owner who just wants SD card storage, the DivMMC is the right answer. The Z-Controller is rarely the right answer outside the Russian clone ecosystem.

---

## Common Pitfalls

| # | Pitfall | Why it happens | Fix |
|---|---------|----------------|-----|
| 1 | Z-Controller bought online doesn't fit a Sinclair 48K | The board was assembled with a Pentagon port-decode CPLD build, which clashes with the Sinclair 48K's `/IORQULA` contention scheme | Re-flash the EPM7128 CPLD with the Sinclair-targeted build (JTAG connector on board); alternatively buy a DivMMC for Sinclair use |
| 2 | SD card works in one Russian clone but not another | Pentagon, Scorpion, Profi, and Kay each have different port-decoding conventions for the SD card address | Use the CPLD build matched to your host machine |
| 3 | SDHC card (4–32 GB) not recognized | The original Wild Disk Copier v1.21 driver supports only standard-capacity SD (up to 2 GB) | Use a more recent patched driver, or use a 2 GB or smaller SD card |
| 4 | SDXC card (>32 GB) not recognized | SDXC uses exFAT by default; the Z-Controller's drivers predate exFAT | Reformat the card as FAT32 using a PC tool (will partition up to 32 GB); remainder of card is wasted |
| 5 | PS/2 mouse works in some software but not others | Software has to explicitly support the Kempston Mouse; some software checks only the Kempston Joystick port | Use software that supports the Kempston Mouse (most Russian software from 1990s onward does); see [mouse.md](mouse.md) for the compatibility table |
| 6 | PS/2 mouse buttons are swapped | The Z-Controller emulates Kempston Mouse convention: bit 0 = left, bit 1 = right. Some software expects the opposite. | Configure the software's mouse button order; or use the K-Mouse Turbo configuration utility if your board supports it |
| 7 | PS/2 keyboard gives wrong keystrokes | The KR1878VE1 firmware maps PS/2 scan codes to a Russian clone matrix layout (usually Pentagon), not the original Sinclair 40-key layout | Use a CPLD/MCU firmware build matched to your target machine's matrix; or stick with software that supports the PS/2 scan codes directly |
| 8 | CompactFlash card works in IDE but is read-only | CF cards have a "write protect" jumper on the side; some CF-to-IDE adapters do not pass through the WP signal correctly | Check the card's WP switch; try a different CF-to-IDE adapter |
| 9 | IDE hard disk works intermittently | Modern hard disks draw more current on spin-up than the Spectrum's `+5V` rail can supply; the rail sags and the machine crashes | Use a CompactFlash card instead, or use a hard disk with its own external power supply |
| 10 | Z-Controller does not appear in esxDOS's `*.dot` command list | esxDOS targets DivMMC/DivIDE hardware specifically; the Z-Controller's SD port is at a different address | Use Wild Disk Copier or a Z-Controller-aware fork; the Z-Controller is **not** a DivMMC replacement |
| 11 | Emulator does not detect the Z-Controller | Only Unreal Speccy and ZNOS have explicit Z-Controller emulation; Fuse, ZEsarUX, and most Western emulators do not | Use Unreal Speccy; or write to the emulator authors with port-decode details for support |
| 12 | Board does not fit pass-through stacking with another peripheral | The Z-Controller's PCB length and connector placement are sized for a Pentagon case; in a Sinclair or Scorpion case the pass-through may be obstructed | Use a ribbon-cable riser; or stack only below shorter peripherals |

---

## When to Use What

| You have… | You want… | Recommended solution |
|-----------|-----------|----------------------|
| Pentagon 128/512/1024 | Modern SD card mass storage | **Z-Controller** (or MB03+ Ultimate if budget allows) |
| Scorpion ZS-256 Turbo+ | Modern SD card mass storage | Z-Controller with Scorpion CPLD build |
| Original Sinclair 48K / 128K / +2 | Modern SD card mass storage | **DivMMC** (not Z-Controller — Western support is poor) |
| Original Sinclair +2A / +3 | Modern SD card mass storage | DivMMC, or SMART Card for 48K-mode-only use |
| Any Russian clone | PS/2 keyboard + PS/2 mouse | Z-Controller (only board combining both with mass storage) |
| Any Russian clone | CompactFlash via IDE | Z-Controller, or any Nemo IDE-compatible board |
| Modern hardware enthusiast | Everything (keyboard, mouse, IDE, SD, video, sound) | **MB03+ Ultimate** (FPGA successor that includes Z-Controller compatibility plus much more) |
| Modern Russian clone | All-in-one with Z-Controller built in | **ZX Spectrum Neo** |

---

## Comparison Matrix

| Property | Z-Controller | DivMMC | DivIDE | SMART Card | MB03+ Ultimate |
|----------|--------------|--------|--------|-----------|----------------|
| **Year** | 2007 | 2012 | 2005–2007 | 2014+ | 2019+ |
| **Connector** | ZX Bus | ZX Bus | ZX Bus | ZX Bus | ZX Bus |
| **SD card** | Yes | Yes | No (IDE only) | Yes | Yes (Z-Controller compatible + divMMC compatible) |
| **IDE / CompactFlash** | Yes (Nemo IDE) | No | Yes (8-bit) | No | Yes (MB-02+IDE compatible) |
| **PS/2 keyboard** | Yes | No | No | No | Yes |
| **PS/2 mouse** | Yes (Kempston emulation) | No | No | No | Yes |
| **Joystick port** | Optional (Kempston) | Optional | Optional | No | Yes |
| **On-board boot ROM** | No (must bootstrap from floppy/IDE) | Yes (loads esxDOS from SD) | Yes (loads `COMMAND2.COM` from IDE) | Yes (16-bank ROM substitution) | Yes (multi-OS boot menu) |
| **Native OS** | TR-DOS with Wild Disk Copier patches | esxDOS (FAT16/FAT32) | IDE-based FAT16 | Custom ROM manager | esxDOS, BS-DOS, ResiDOS, TR-DOS |
| **Open hardware** | Schematics public, PCB layout closed | Fully open | Fully open | Fully open | Closed (commercial) |
| **Open firmware** | Binary public, source closed | Open | Open | Open | Closed (commercial) |
| **Target audience** | Russian clone owners | Western Spectrum owners | Western Spectrum owners (IDE/CF focus) | 48K Spectrum owners | Power users wanting everything |
| **Approx. price** | Rare today; £50–£100 used | £25–£40 (new, modern clones) | £30–£50 (used) | £40 (new from retroleum.co.uk) | €300+ (new from LMN128) |

---

## Modern Analogies

- The Z-Controller is the spiritual ancestor of the **PCIe expansion card that does everything**: a single board that adds network, sound, extra USB ports, and a Wi-Fi adapter. The integration is convenient but the individual functions are not best-in-class — a dedicated DivMMC SD card interface or a dedicated K-Mouse Turbo mouse interface would do each function slightly better.
- The split between CPLD (fast deterministic logic) and MCU (slow protocol handling) is exactly the same architecture used in modern **USB-to-serial bridge chips**: the hardware serial engine handles bit timing in a CPLD or FPGA, while an embedded MCU handles the USB protocol stack. The Z-Controller was doing this kind of split in 2007, before USB-to-serial bridges were ubiquitous.
- The "open schematic, closed firmware source" licensing model is the same model used by many **modern open-hardware projects** like the Analogue Nt Mini — the schematic is published so users can verify there are no backdoors, but the FPGA bitstream is kept proprietary to protect the author's competitive advantage.
- The Z-Controller's position in the ZX Spectrum ecosystem is similar to the position of the **Russian Elbrus PC** in the broader x86 world: technically competent, designed for a specific local audience, and largely unknown outside its home market.
- The Z-Controller's re-implementation inside the MB03+ Ultimate FPGA is exactly analogous to **software emulation of legacy peripherals in modern FPGA boards** like the MiSTer — the original hardware is preserved as a "hardware description" that runs in a modern FPGA, ensuring the software library stays usable as the original components fail.

---

## Cross-References

- [zx_bus.md](zx_bus.md) — the 56-pin ZX Bus edge connector that the Z-Controller plugs into; port-decode conventions; peripheral stacking order
- [mb02.md](mb02.md) — the MB-02/+ and MB03+ Ultimate FPGA interface, which includes a Z-Controller-compatible SD block; the MB03+ is the modern successor to both the MB-02 and the Z-Controller
- [mouse.md](mouse.md) — the Kempston Mouse protocol that the Z-Controller's PS/2 mouse input emulates; standard ports `#FBDF`/`#FFDF`/`#FADF`
- [keyboard.md](keyboard.md) — Spectrum keyboard reading, including PS/2 keyboard adapters (Penguin, K-Mouse Turbo, etc.) that solve the same problem the Z-Controller does for a subset of machines
- [joystick.md](joystick.md) — the Kempston Joystick port conventions, optionally emulated by the Z-Controller
- [printers.md](printers.md) — for the Centronics printer convention used by some Russian clone disk interfaces
- [03_io/storage](../storage/README.md) — the mass-storage peripherals directory; covers Beta Disk Interface, Opus Discovery, +D, MB-02, DivIDE, DivMMC, and other disk interfaces
- [02_hardware/clones/clone_timing.md](../../02_hardware/clones/clone_timing.md) — per-clone port-decoding conventions (Pentagon, Scorpion, Profi, Kay, ATM Turbo) that the Z-Controller's CPLD must be configured for
- [Clone video modes](../../05_development/05_display_and_timing/clone_video_modes.md) — context for the Russian-clone software ecosystem the Z-Controller was designed to serve

---

## Primary Sources

- [SpeccyWiki (Russian): "Z-Controller"](https://speccy.info/Z-Controller, archived at https://web.archive.org/web/20240918071026/https://speccy.info/Z-Controller) — the canonical Russian-language reference, including authorship attribution to Alexey Zhabin (KingOfEvil), 2007 design date, and the list of supported functions (PS/2 keyboard, PS/2 mouse, IDE, SD)
- [SpeccyWiki (Russian): "Nemo IDE"](https://speccy.info/Nemo_IDE, archived at https://web.archive.org/web/20241118014803/https://speccy.info/Nemo_IDE) — original Nikolai Tyrsin 1994 IDE controller, of which the Z-Controller's IDE block is a software-compatible re-implementation
- **MB03+ Ultimate documentation** (LMN128, https://sites.google.com/view/mb03plus/home) — explicitly lists "Z-Controller SD slot" as one of the legacy peripherals implemented in the FPGA
- **MB03+ Programmer's Reference** (https://docs.google.com/document/d/13TADX_NDnTwVzgUwc03NiR2T0OVlg4SGwOctBSOVOWw/edit) — technical details of the MB03+'s Z-Controller compatibility mode
- [ZX Spectrum Neo manual](https://www.worldofspectrum.org/hardware.html) — explicitly notes that the Neo's SD card support uses Z-Controller mechanisms
- **K-Mouse Turbo and PS/2 keyboard interfaces survey** (Sam.speccy.cz, https://sam.speccy.cz/hids.html) — context for the PS/2 keyboard and mouse landscape on the ZX Spectrum, including the relationship between the Z-Controller, K-Mouse Turbo, and MB03+
- **Wild Disk Copier release notes** (KingOfEvil / Russian Speccy scene, v1.21 onward) — the first piece of software to support SD card access via the Z-Controller; required reading for Z-Controller users
- [ZX Spectrum Hardware Ports Reference](https://groups.google.com/g/comp.sys.sinclair) — definitive reference for the standard port-decode conventions (Kempston Mouse, etc.) that the Z-Controller emulates
- **BC Info Guide #4 — Guide to the ZX Spectrum ports** (Black_Cat, 2008, https://wiki.speccy.org/_media/cursos/ensamblador/zx-ports-full-table.pdf) — Russian-language ports table; documents the port-decoding conventions used by Russian clone peripherals
- **iS-DOS documentation** (Russian Speccy scene) — the CP/M-like OS that was patched to support the Z-Controller's SD and IDE interfaces
