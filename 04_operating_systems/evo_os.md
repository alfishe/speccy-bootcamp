[← Home](../README.md) · [Operating Systems](README.md)

# The ZX Evolution — BIOS, BaseConf, and the Boot Process

The Russian Spectrum clone scene reached its technical peak with the **ZX Evolution** — an FPGA-based reimplementation of the Spectrum, designed by the NedoPC team and first released around 2010. Unlike the earlier Russian clones (Pentagon, Scorpion, ATM Turbo), which were built from discrete TTL logic and the original Sinclair custom chips, the ZX Evolution implements the entire Spectrum in a single FPGA. This makes it the most flexible, most powerful, and most modern Russian Spectrum hardware ever produced — and the platform that the modern Russian Spectrum scene is built around.

The ZX Evolution is not just hardware. It is a complete system with three distinct software layers: the **boot ROM** (firmware that initialises the hardware and presents a boot menu), the **BaseConf** (the FPGA "hardware configuration" that defines what hardware the FPGA presents to the CPU), and the **OS layer** (typically NedoDOS or TR-DOS, loaded as a DOS ROM). Together these three layers make a ZX Evolution behave like a Spectrum — and selecting between configurations is what makes it possible to use the same physical board for Pentagon-128 software, ATM Turbo software, or new TS-Conf-extended software.

This article covers the ZX Evolution as a system, with emphasis on the firmware and OS layers. For the ZX Spectrum Next — the Western equivalent FPGA-Spectrum — see [nextzxos.md](nextzxos.md). For NedoDOS — the DOS that runs on the ZX Evolution — see [nedo_dos.md](nedo_dos.md). For Russian clone hardware more broadly, see [../02_hardware/clones/README.md](../02_hardware/clones/README.md).

---

## Roadmap

1. **What the ZX Evolution is** — origins, scope, design goals
2. **Hardware architecture** — FPGA, RAM, storage, video, audio, I/O
3. **The boot ROM / firmware** — the BIOS chip and its responsibilities
4. **BaseConf — the FPGA configuration** — the hardware definition layer
5. **TS-Conf and other configurations** — alternative FPGA images
6. **The boot process** — from power-on to the BASIC prompt
7. **The OS layer** — NedoDOS, TR-DOS, and ROM slot management
8. **Configuration and the user interface** — boot menu, hotkeys, settings
9. **Modern status** — the ZX Evolution in 2024 and the active community
10. **Cross-references** — where to go next

---

## §1. What the ZX Evolution Is

### 1.1 Origins

The ZX Evolution project began in the late 2000s as a collaboration within the **NedoPC team**, a loose collective of Russian Spectrum hardware and software developers. The lead hardware designer was **Aleksandr Zhuravlev** (`tsl`), with contributions from **Vladimir Kladov** (`Clover`), **Oleg Nesterov** (`nester`), and others.

The motivation was the slow death of the classic Russian clones. The Pentagon, Scorpion, and ATM Turbo were all built from discrete logic — a mixture of 7400-series TTL chips, the original ULA (or a Russian clone of it), and a great deal of hand-wired PCB layout. By the late 1990s:

- The original Sinclair ULA was out of production.
- Russian ULA clones (the `T34` and similar) were becoming hard to source.
- PCB manufacture for complex discrete-logic designs was expensive.
- Maintaining and repairing 15-year-old homebrew clones was increasingly impractical.

At the same time, **FPGAs** (Field-Programmable Gate Arrays) had become affordable. An FPGA can implement any digital circuit by loading a "bitstream" — and a Spectrum is, fundamentally, just a digital circuit. Implementing the Spectrum in an FPGA offered several advantages:

- **No obsolete parts.** An FPGA is generic; you do not need any 1980s silicon.
- **Bug-fixable in software.** Hardware bugs can be patched by reprogramming the FPGA.
- **Configurable.** The same physical board can be reconfigured to behave as different clones.
- **Mass-producible.** Once the FPGA design is stable, manufacturing is straightforward.

The ZX Evolution was the result: a single-board Spectrum, implemented entirely in an FPGA, designed to be the modern standard for the Russian scene.

### 1.2 Scope

The ZX Evolution is **hardware**: a PCB with an FPGA, RAM, storage interfaces, video output, and I/O. But it ships with a complete software stack that includes:

- **The boot ROM** — firmware that runs at power-on, initialises the hardware, and presents a boot menu.
- **The BaseConf** — an FPGA bitstream that defines what hardware the board presents (memory map, video modes, sound chips, etc.).
- **A bundled DOS** — typically NedoDOS, loaded into a DOS ROM slot.
- **A bundled BASIC** — the standard 128K BASIC ROM, often with extensions.

So while the ZX Evolution is *primarily* hardware, this article covers the software layers — the BIOS, the BaseConf, and how they fit together. The hardware itself is covered briefly in §2 and in more detail in [../02_hardware/clones/README.md](../02_hardware/clones/README.md).

### 1.3 What the ZX Evolution is not

It is important to be clear about what the ZX Evolution is *not*:

- **It is not a software emulator.** The CPU is real (a Z80 or Z80-compatible core in the FPGA), not emulated on a host processor.
- **It is not a single Spectrum model.** It can impersonate several Russian clones (Pentagon, Scorpion, ATM Turbo) and the original 48K/128K Spectrums, depending on the BaseConf in use.
- **It is not a closed system.** The FPGA bitstream is open and the hardware design is documented. Users can and do modify both.
- **It is not the same as the ZX Spectrum Next.** The Next is a Western product, designed by a different team, with different goals. The two share the "FPGA Spectrum" concept but are not software- or hardware-compatible at the firmware level.

### 1.4 Why the ZX Evolution matters

The ZX Evolution matters because it is the **modern Russian Spectrum**. In 2024, if you want to buy new Russian Spectrum hardware, the ZX Evolution (or a derivative board) is essentially your only realistic option. The classic clones (Pentagon, Scorpion, ATM Turbo) are no longer manufactured; the ZX Evolution is.

It also matters because of its **flexibility**. The FPGA approach means that the same physical board can run:

- Classic 48K software (using a 48K-compatible BaseConf).
- Pentagon software (the dominant Russian Spectrum standard).
- ATM Turbo software (an alternative Russian clone).
- TS-Conf-extended software (a modern Russian graphics/memory extension).
- Original NedoDOS software (modern Russian DOS-aware software).

No other hardware in the Spectrum ecosystem offers this level of flexibility in a single device. The closest Western equivalent is the ZX Spectrum Next, which targets the Western scene and is not API-compatible at the firmware level.

### 1.5 Relationship to NedoDOS

NedoDOS and the ZX Evolution are designed together but are separate components:

- **NedoDOS** is a disk operating system — software that provides file I/O over SD/CF/IDE.
- **The ZX Evolution** is hardware — the physical machine, with its BIOS and FPGA configuration.

NedoDOS runs *on* the ZX Evolution. You can run the ZX Evolution without NedoDOS (using TR-DOS instead, for example), and you can run NedoDOS on other hardware (Pentagon, ATM Turbo). But the ZX Evolution is NedoDOS's primary platform, and the two are usually used together.

For details on NedoDOS itself, see [nedo_dos.md](nedo_dos.md).

---

## §2. Hardware Architecture

The ZX Evolution is a single-board computer built around an FPGA. The hardware architecture determines what the firmware and OS layers have to work with.

### 2.1 The FPGA

The heart of the ZX Evolution is an **Altera Cyclone** FPGA (specifically the EP1C6 or EP1C12, depending on the board revision). The FPGA implements:

- The **CPU core** (a Z80-compatible processor, typically the T80 open-source core).
- The **memory controller** (managing the board's static and dynamic RAM).
- The **video controller** (generating the video signal).
- The **sound chips** (the AY-3-8910, the beeper, and optionally the Covox).
- The **I/O controllers** (keyboard, joystick, mouse, SD, IDE, etc.).

The FPGA is configured at power-on by loading a bitstream from a serial Flash chip. This bitstream is the **BaseConf** (see §4).

### 2.2 Memory

The ZX Evolution ships with **512 KB or 1024 KB of RAM**, depending on the configuration. This memory is used for:

- The standard Spectrum 128 KB (the lower 128 KB of the address space).
- **Extended memory banks** — additional 16 KB pages that can be banked into the address space.
- **Video memory** — separate regions for the various video modes.
- **RAM disk** — memory set aside to act as a virtual disk drive.

The memory layout is configurable via the BaseConf. The default layout matches the Pentagon 1024 (the de facto Russian Spectrum standard).

### 2.3 Storage

The ZX Evolution includes several storage interfaces:

- **CompactFlash slot** (via IDE) — the primary mass storage for most users. CF cards from 8 MB to 64 GB are supported.
- **SD card slot** (via SPI) — a secondary storage interface, useful for transferring files to/from modern PCs.
- **Beta 128 floppy interface** — for reading and writing traditional TR-DOS-formatted floppies (5.25" DD/HD, 3.5" DD/HD).

These interfaces are managed by NedoDOS (or TR-DOS, depending on the loaded DOS). The boot ROM knows how to access them at a low level for boot purposes.

### 2.4 Video

The video output supports several modes, depending on the BaseConf:

- **Standard Spectrum modes** — 256×192 with attributes, in all variants (standard, multicolour, GIGASCREEN, etc.).
- **ATM Turbo modes** — 320×200 and 640×200 text and graphics modes.
- **TS-Conf extended modes** — 16-color and 256-color modes with hardware tiles and sprites (in TS-Conf configurations).
- **Text modes** — 80×25 and 64×28 character modes for CP/M, IS-DOS, and NedoDOS Commander use.

The video output is **VGA** (in addition to composite and RGB). This makes the ZX Evolution directly usable with modern monitors — a significant practical advantage over the older Russian clones, which typically only output composite video.

### 2.5 Audio

The ZX Evolution includes:

- The **Spectrum beeper** (1-bit sound, as on the original 48K).
- The **AY-3-8910 sound chip** (or a YM2149 in newer configurations).
- Optionally, a **Covox** (8-bit DAC for sample playback).
- Optionally, a **TurboSound** extension (two or three AY chips, for richer sound).

For users with the NeoGS sound card expansion (a daughter-board), additional sound hardware (Sound Blaster-compatible, MIDI, and others) is available.

### 2.6 Input/Output

The ZX Evolution includes:

- **PS/2 keyboard** port — most ZX Evolution users use a PS/2 (or USB-to-PS/2) keyboard instead of the original Spectrum membrane.
- **PS/2 mouse** port.
- Two **joystick ports** (Sinclair and Kempston protocols).
- **Serial port** (rarely used).
- **Parallel port** (Centronics, for printers).

The PS/2 keyboard is a major quality-of-life improvement over the original Spectrum membrane — and over the typically-poor keyboards on Russian clones.

### 2.7 Turbo modes

The ZX Evolution supports several CPU clock speeds:

- **3.5 MHz** — standard Spectrum speed.
- **7 MHz** — "turbo" mode (the standard Russian turbo speed).
- **14 MHz** — "double turbo" mode (used for the most demanding software).

The turbo modes are selected via a hotkey or programmatically. Most classic software runs in 3.5 MHz mode; modern Russian software often takes advantage of 7 MHz or 14 MHz.
---

## §3. The Boot ROM / Firmware

The boot ROM is the **firmware** — the small piece of software that runs at power-on, before the OS is loaded. On the ZX Evolution, the boot ROM is responsible for hardware initialisation, presenting the boot menu, and loading the chosen OS.

### 3.1 Physical form

The boot ROM lives in a small **serial Flash chip** on the ZX Evolution board, separate from the FPGA's main configuration Flash. This separation is deliberate:

- The **FPGA configuration Flash** holds the BaseConf bitstream. It is loaded into the FPGA at power-on by the FPGA's hardware configuration controller.
- The **boot ROM Flash** holds the firmware code. It is mapped into the Z80's address space at `#0000`–`#3FFF` after the FPGA is configured.

Both Flash chips can be reprogrammed in-circuit, allowing both the firmware and the BaseConf to be updated without removing any chips.

### 3.2 What the boot ROM does

At power-on, after the FPGA has been configured with the BaseConf, the Z80 is reset and begins executing at address `#0000` — which is the start of the boot ROM. The boot ROM then:

1. **Initialises the hardware** — sets up the memory controller, configures the video mode, calibrates the SD/IDE interfaces, etc.
2. **Detects the storage devices** — scans for SD cards, CF cards, and floppy drives, and identifies them.
3. **Loads the configuration** — reads a settings file from the SD/CF card (if present), which specifies the user's preferred defaults: which DOS to load, which BaseConf to use, the boot video mode, etc.
4. **Presents the boot menu** — displays a menu allowing the user to choose what to boot (the default DOS, an alternative DOS, BASIC, or a specific file).
5. **Loads and runs the chosen OS** — reads the selected DOS ROM image from the storage device and maps it into the appropriate ROM slot.
6. **Transfers control** — jumps to the start of the loaded OS, which takes over the machine.

This is a more complex boot sequence than the original Spectrum (which just ran the BASIC ROM) or the Pentagon (which ran the 128K ROM). The complexity is necessary because the ZX Evolution has more options: multiple storage devices, multiple DOSes, multiple BaseConfs.

### 3.3 The boot menu

The boot menu is a simple text-mode interface presented on screen after power-on. A typical boot menu offers:

- **Boot DOS** — load the default DOS (typically NedoDOS) and present its prompt.
- **Boot BASIC 128K** — load the 128K BASIC ROM, ignoring the DOS.
- **Boot BASIC 48K** — load the original 48K BASIC ROM.
- **Boot from floppy** — boot from a TR-DOS-formatted floppy in the Beta 128 drive.
- **Run file** — load and run a specific file from the SD/CF card.
- **Configure** — enter the configuration editor.

The user navigates with the arrow keys and selects with Enter. There is also a hotkey shortcut to bypass the menu and boot straight to the default.

### 3.4 The configuration editor

The configuration editor allows the user to change persistent settings without modifying files on the SD card. Typical settings include:

- **Default boot device** — SD or CF or floppy.
- **Default DOS** — NedoDOS, TR-DOS, or another ROM image.
- **Default BaseConf** — which FPGA configuration to use at power-on.
- **Default video mode** — standard, ATM Turbo, text mode.
- **Default CPU speed** — 3.5 MHz, 7 MHz, 14 MHz.
- **Keyboard layout** — Russian, English, or mixed.
- **Mouse protocol** — Kempston, Mouse Systems, or Microsoft.
- **Sound configuration** — which sound chips are enabled.

Settings are stored in a small Flash partition or in a file on the SD card. The boot ROM reads them at startup and applies them before presenting the boot menu.

### 3.5 ROM slot management

The ZX Evolution provides multiple **ROM slots** — independent 16 KB regions of address space, each of which can hold a different ROM image. The boot ROM manages these slots:

- **Slot 0** — the boot ROM itself (always present).
- **Slots 1–N** — available for DOS ROMs, BASIC ROMs, or other system ROMs.

At boot, the user (or the configuration) selects which slot to map into the active ROM region. Switching between slots during operation is possible via port writes, allowing software to access multiple ROMs (e.g., TR-DOS and NedoDOS) without rebooting.

This is conceptually similar to the +3's paging mechanism (see [rom_plus2.md](rom_plus2.md) §5) but more flexible — the slots are software-configurable, not hardwired to specific ROM pages.

### 3.6 Updating the boot ROM

The boot ROM can be updated by:

1. **Loading a new ROM image** from the SD/CF card.
2. **Using the in-boot-ROM update utility** to reflash the boot ROM chip.
3. **Power-cycling** to load the new boot ROM.

This is generally safe — the update utility verifies the image before flashing, and a recovery mechanism exists if the update fails. But it is a delicate operation: if the boot ROM is corrupted, the machine will not boot. The recovery mechanism involves reprogramming the serial Flash via a JTAG adapter, which requires additional hardware.

---

## §4. BaseConf — The FPGA Configuration

The BaseConf is the **FPGA bitstream** — the binary file that defines what hardware the FPGA implements. Without the BaseConf, the ZX Evolution is just a board with an FPGA and RAM. With the BaseConf, it becomes a Spectrum.

### 4.1 What the BaseConf defines

The BaseConf defines:

- The **CPU core** (typically the T80 Z80-compatible core).
- The **memory map** (which RAM banks are mapped where, how paging works, what ports control it).
- The **video modes** (standard Spectrum, ATM Turbo, text mode, etc.) and their address layouts.
- The **sound chips** (which AY chips are present, where they are addressed, what extensions exist).
- The **I/O ports** (which ports respond to which devices — keyboard, joystick, mouse, SD, IDE, etc.).
- The **timing** (CPU clock speeds, video timing, interrupt frequency).

In short, the BaseConf is the **hardware definition** of the ZX Evolution as the Z80 sees it. Changing the BaseConf changes what hardware the Z80 sees.

### 4.2 The default BaseConf: Pentagon 1024

The default BaseConf implements the **Pentagon 1024** standard. The Pentagon 1024 is the most widely-supported Russian Spectrum configuration — most Russian software is tested against it. Key features of the Pentagon 1024 BaseConf:

- **Memory**: 1024 KB, organized as 64 banks of 16 KB, paged via port `#7FFD` (and the extension port `#DFFD`).
- **Video**: standard Spectrum 256×192 mode, with additional multicolour and text modes via port `#FF` and the ATM Turbo ports.
- **Sound**: standard AY-3-8910 at address `#FFFD`/`#BFFD`.
- **I/O**: standard Spectrum layout plus Pentagon-specific ports (Beta 128 disk interface at `#1F`/`#3F`/`#5F`/`#7F`).

This is the "compatibility" configuration — it runs the vast majority of Russian Spectrum software. Most users keep their ZX Evolution in this configuration most of the time.

### 4.3 The Pentagon 128 variant

A simplified variant — the **Pentagon 128** — is also available. This configuration has only 128 KB of RAM (no extended banks) and matches the original Pentagon specification. It is useful for running older Pentagon-128-specific software that may behave oddly on a Pentagon 1024.

### 4.4 The ATM Turbo variant

The **ATM Turbo** BaseConf implements the ATM Turbo clone — a different Russian Spectrum with its own video modes (320×200 and 640×200), its own memory paging (via ports `#BF` and `#7F`), and its own conventions. Software written for the ATM Turbo requires the ATM Turbo BaseConf to run correctly.

### 4.5 The original 48K and 128K variants

For maximum compatibility with original Sinclair software, BaseConfs implementing the plain 48K and 128K Spectrums are available. These are useful for:

- Running software that misbehaves on Russian clones.
- Testing software that should run on original Sinclair hardware.
- Avoiding any Pentagon-specific features (e.g., the additional Beta 128 disk port).

### 4.6 Updating the BaseConf

Updating the BaseConf is similar to updating the boot ROM:

1. **Load a new bitstream** from the SD/CF card.
2. **Use the boot ROM's BaseConf update utility** to reflash the FPGA's configuration Flash.
3. **Reboot** — the FPGA is reconfigured at the next power-on.

Because the BaseConf is the lowest layer of the system (it defines the hardware itself), a corrupt BaseConf is a more serious problem than a corrupt boot ROM. If the BaseConf is corrupted, the FPGA will not be configured, and the board will be completely non-functional until the bitstream is rewritten via JTAG.

The community therefore recommends keeping a known-good BaseConf image on a separate SD card for emergencies.

### 4.7 The relationship between boot ROM and BaseConf

The boot ROM and the BaseConf are independent but cooperating:

- The **BaseConf** is loaded first (by the FPGA's hardware configuration controller, at power-on).
- The **boot ROM** is loaded second (by the Z80, which executes from the boot ROM after the FPGA is configured).

The boot ROM is written to match the BaseConf — i.e., the boot ROM knows which I/O ports are available, what memory layout is in use, and what features are exposed. If you change the BaseConf without changing the boot ROM (or vice versa), the system may not boot correctly.

In practice, BaseConf and boot ROM updates are released together as a "package" by the NedoPC team. Users update both at the same time.
---

## §5. TS-Conf and Other Configurations

Beyond the Pentagon, ATM, and original-Sinclair BaseConfs, there are extended configurations that exploit the FPGA's flexibility to provide features no classic Spectrum had.

### 5.1 TS-Conf — the modern Russian graphics configuration

**TS-Conf** is the most important alternative configuration. Designed by the NedoPC team and contributors, TS-Conf is an extended Spectrum configuration that includes:

- **16-color and 256-color graphics modes** — far beyond the standard Spectrum's attribute-based color.
- **Hardware tiles** — a tile-based background layer, similar to console graphics (NES, SMS, etc.).
- **Hardware sprites** — up to 96 independent sprites with per-pixel transparency.
- **Multiple graphics layers** — a Layer 2-style full-color overlay on top of the Spectrum display.
- **Extended memory** — a flat memory model with up to 4 MB addressable.
- **DMA** — a hardware DMA controller for fast memory-to-memory and memory-to-video copies.
- **Copper** — a programmable video sequencer (similar to the Amiga copper).

TS-Conf is, in effect, the **Russian answer to the ZX Spectrum Next's extended graphics**: a modern Spectrum configuration designed for new software that goes beyond the original hardware's capabilities.

Software written for TS-Conf does not run on a Pentagon or ATM Turbo. It requires the TS-Conf BaseConf. The ZX Evolution's ability to switch BaseConfs means that the same physical board can run both TS-Conf software (in the TS-Conf configuration) and Pentagon software (in the Pentagon configuration).

### 5.2 When to use which configuration

A typical ZX Evolution user has several BaseConfs available on the SD card and switches between them as needed:

| Configuration | When to use it |
|---|---|
| Pentagon 1024 (default) | Most classic Russian software; default daily use |
| Pentagon 128 | Older Pentagon-128 software with compatibility issues |
| ATM Turbo | ATM Turbo-specific software |
| 48K | Original Sinclair software that misbehaves on clones |
| 128K | Original 128K/+2 software |
| TS-Conf | Modern TS-Conf-aware software (new games, demos, applications) |

Switching configurations is a reboot operation — the user selects the new BaseConf in the boot menu, and the FPGA is reprogrammed on the next power cycle.

### 5.3 The future of TS-Conf

TS-Conf is under active development. The configuration continues to receive new features (more sprites, more layers, more memory, etc.) and is increasingly the target for new Russian Spectrum software. Some commentators believe TS-Conf will eventually replace the Pentagon as the de facto Russian Spectrum standard — but the Pentagon's software library is so large that Pentagon compatibility will remain important for the foreseeable future.

The ZX Evolution's FPGA approach means that the hardware can evolve without requiring new physical boards — users simply install a newer BaseConf.

### 5.4 Other community configurations

Beyond TS-Conf, the community has produced:

- **GMX configurations** — for the GMX memory extension (a daughter-board providing additional RAM and features).
- **NeoGS configurations** — for the NeoGS sound card extension (with multiple AY chips, sample playback, MIDI).
- **Custom configurations** — enthusiasts have written BaseConfs for experimental hardware features (e.g., 1024-color video modes, hardware 3D acceleration).

This openness — the ability for anyone with FPGA expertise to add features to the platform — is one of the ZX Evolution's great strengths.

---

## §6. The Boot Process

The boot process of the ZX Evolution is more complex than that of a classic Spectrum, because of the multiple layers (FPGA, BaseConf, boot ROM, OS) and the multiple options (which BaseConf, which DOS, which video mode).

### 6.1 Power-on

When power is applied:

1. **The FPGA's configuration controller starts.** This is hardware-level logic that reads the BaseConf bitstream from the configuration Flash and programs the FPGA.
2. **The FPGA is configured.** The FPGA now implements the hardware defined by the BaseConf — the CPU core, memory controller, video controller, etc.
3. **The Z80 is held in reset.** Until the FPGA is fully configured and stable, the Z80 is not running.
4. **The Z80 is released from reset.** The Z80 begins executing at address `#0000`, which is the start of the boot ROM.

This process takes a fraction of a second — typically under 100 ms from power-on to the Z80 starting to execute the boot ROM.

### 6.2 Boot ROM execution

Once the Z80 starts executing the boot ROM, the boot ROM performs the steps described in §3.2: hardware initialisation, device detection, configuration loading, boot menu presentation, OS loading.

In detail:

```
+----------+   +-------------+   +---------------+
| Power-on |-->| FPGA        |-->| Z80 reset     |
|          |   | configured  |   | released      |
+----------+   +-------------+   +---------------+
                                       |
                                       v
                            +-----------------------+
                            | Boot ROM starts at    |
                            | #0000                 |
                            +-----------------------+
                                       |
                                       v
                            +-----------------------+
                            | Hardware init         |
                            | (memory, video, I/O)  |
                            +-----------------------+
                                       |
                                       v
                            +-----------------------+
                            | Detect storage        |
                            | (SD, CF, floppy)      |
                            +-----------------------+
                                       |
                                       v
                            +-----------------------+
                            | Load config file      |
                            | (if present on SD/CF) |
                            +-----------------------+
                                       |
                                       v
                            +-----------------------+
                            | Present boot menu     |
                            | (or auto-boot)        |
                            +-----------------------+
                                       |
                                       v
                            +-----------------------+
                            | Load selected OS ROM |
                            | into ROM slot        |
                            +-----------------------+
                                       |
                                       v
                            +-----------------------+
                            | Jump to OS entry     |
                            | (typically #0000)    |
                            +-----------------------+
```

### 6.3 OS loading

Loading the selected OS involves:

1. **Locating the OS ROM image** — typically a 16 KB or 32 KB file on the SD/CF card (e.g., `NEDODOS.ROM`).
2. **Reading the file** into a temporary RAM buffer.
3. **Mapping the buffer to a ROM slot** — the boot ROM copies the OS image into the appropriate ROM slot via a Flash programming routine.
4. **Switching the active ROM slot** — the boot ROM changes the active ROM slot to the one containing the newly-loaded OS.
5. **Jumping to the OS entry point** — the boot ROM jumps to `#0000`, which is now the start of the loaded OS.

This is fast — a typical NedoDOS load takes under a second from CF or SD. Floppy boots are slower, of course.

### 6.4 OS takeover

Once the OS (e.g., NedoDOS) is loaded and control has been transferred, the boot ROM is no longer in the active address space — the OS has full control of the machine. The OS:

- Sets up its own work RAM.
- Initialises its filesystem driver.
- Loads any BASIC extension ROMs that are configured.
- Eventually presents the BASIC prompt (or its own command interface).

The boot ROM remains in its ROM slot and can be re-entered (e.g., via a soft reboot) if needed. But during normal operation, the OS is in control.

### 6.5 Soft reboot

A **soft reboot** — rebooting without power-cycling — is supported via a hotkey combination (typically `Ctrl+Alt+Del` or a similar PS/2-keyboard combination). The soft reboot:

1. Triggers a non-maskable interrupt (NMI) or a software reset.
2. The boot ROM regains control.
3. The boot ROM re-initialises the hardware and re-presents the boot menu.

Soft reboot is useful for switching between DOSes, between configurations, or recovering from software crashes without physically cycling power.

### 6.6 Comparison with the original Spectrum boot process

The original 48K Spectrum's boot process was trivial: power-on → Z80 reset → execute ROM at `#0000` → initialise hardware → present BASIC prompt. The whole process took less than a second.

The ZX Evolution's boot process is more complex because it has more options. But the result is the same: within a few seconds of power-on, the user is at a BASIC prompt (or a DOS prompt) and ready to use the machine.

---

## §7. The OS Layer

The OS layer is what runs after the boot ROM has finished — the DOS (NedoDOS or TR-DOS) and the BASIC that runs on top of it.

### 7.1 The DOS ROM

The primary OS component is the **DOS ROM** — a 16 KB or 32 KB image that provides file I/O and disk management. On the ZX Evolution, this is typically:

- **NedoDOS** — the modern Russian DOS, designed for the ZX Evolution. Provides FAT16/32 with long filenames, SD/CF/IDE support, and a clean assembly API. (See [nedo_dos.md](nedo_dos.md).)
- **TR-DOS** — the classic Russian DOS, provided for backward compatibility. Used to run classic Soviet-era software.
- **ESXDOS** — occasionally used, though primarily a Western DOS for DivIDE/DivMMC hardware.
- **IS-DOS** — the older Russian hierarchical DOS, rarely used but supported. (See [is_dos.md](is_dos.md).)

The DOS ROM is loaded into a ROM slot by the boot ROM and remains resident for the duration of the session.

### 7.2 The BASIC ROM

On top of (or alongside) the DOS, the **BASIC ROM** provides the BASIC interpreter. The default BASIC ROM on the ZX Evolution is typically:

- **128K BASIC** — the standard Amstrad-era Spectrum BASIC, with the full-screen editor, AY-3-8910 driver, and 128K extensions.
- **48K BASIC** — the original Sinclair 48K BASIC, available for compatibility.
- **TR-DOS BASIC** — the 128K BASIC extended with TR-DOS disk commands.
- **NedoDOS BASIC** — the 128K BASIC extended with NedoDOS disk commands.

The choice of BASIC ROM depends on what software the user intends to run. Classic 48K software requires the 48K BASIC ROM; modern Russian software typically uses the NedoDOS BASIC.

### 7.3 ROM slot layout

A typical ZX Evolution memory map during normal operation looks like:

```
#0000-#3FFF  Active ROM slot (BASIC or DOS, switchable)
#4000-#7FFF  RAM (Spectrum screen and work area)
#8000-#BFFF  RAM (program area)
#C000-#FFFF  RAM (banked — page switched via #7FFD)
```

The active ROM slot at `#0000`–`#3FFF` can be switched between BASIC and DOS via port writes, allowing software to call DOS routines from BASIC and vice versa. This is the same basic mechanism as the +3's paging (see [rom_plus2.md](rom_plus2.md)) but with more flexibility.

### 7.4 Application software

Above the BASIC/DOS layer, **application software** runs as machine code in the RAM regions. Applications can be:

- **BASIC programs** — interpreted, loaded via `LOAD "name"`.
- **Machine code programs** — loaded via `LOAD "name" CODE`, then executed via `RANDOMIZE USR addr`.
- **Snapshot files** — complete machine state snapshots (`.sna`, `.z80`), loaded by NedoDOS and executed directly.

NedoDOS supports all three. Classic TR-DOS software is typically distributed as snapshots or as raw machine-code files.
---

## §8. Configuration and the User Interface

The ZX Evolution provides several user-facing interfaces for changing settings and controlling the machine.

### 8.1 The boot menu

As described in §3.3, the boot menu is a text-based menu presented at power-on. It allows the user to select:

- The DOS to load.
- Whether to boot straight to BASIC.
- Which BaseConf to use.
- Which file to run (for direct-loading snapshots or programs).

The boot menu is navigated with the PS/2 keyboard. Settings selected in the boot menu apply only for the current session — they are not persisted unless explicitly saved.

### 8.2 Hotkeys

During operation, the ZX Evolution provides several hotkeys that can be pressed at any time:

| Hotkey | Action |
|---|---|
| `Ctrl+Alt+Del` | Soft reboot — return to the boot menu |
| `Ctrl+Alt+Backspace` | Hard reset — full hardware reset (also reboots) |
| `Magic` + F1 | Help screen (lists all hotkeys) |
| `Magic` + F2 | Toggle turbo mode (3.5 MHz ↔ 7 MHz) |
| `Magic` + F3 | Toggle 14 MHz turbo mode |
| `Magic` + F4 | Switch video mode (standard / ATM / text) |
| `Magic` + F5 | Take a screenshot (saved to SD/CF) |
| `Magic` + F6 | Toggle mouse capture (PS/2 ↔ Spectrum) |
| `Magic` + F10 | Enter configuration editor |

(The "Magic" key is typically the left Windows key on a PS/2 keyboard, or a configurable alternative.)

These hotkeys are handled by the boot ROM (or by a small resident driver that the boot ROM installs) and work in any application — even in 48K BASIC.

### 8.3 The configuration editor

The configuration editor (entered via `Magic+F10` or the boot menu) is a text-mode screen that allows the user to change persistent settings:

- Default boot device.
- Default DOS.
- Default BaseConf.
- Default video mode.
- Default CPU speed.
- Keyboard layout (Russian/English/mixed).
- Mouse protocol.
- Sound chip configuration.
- Hotkey assignments.

Changes are saved to a settings file on the SD card (or to a dedicated Flash partition) and take effect at the next reboot.

### 8.4 The NedoDOS Commander

Although not strictly part of the firmware, the **NedoDOS Commander** (a Norton Commander-style file manager) is the primary user interface for file management on the ZX Evolution. It is described in more detail in [nedo_dos.md](nedo_dos.md) §6.5.

The NedoDOS Commander provides:

- Two-pane file browsing.
- Copy, move, delete, rename operations.
- File attributes and timestamps.
- Long filename support.
- Mouse support.
- Built-in viewer for text files and snapshot files.

Most ZX Evolution users spend a significant fraction of their interactive time in the NedoDOS Commander, rather than at the BASIC prompt.

### 8.5 The BASIC prompt

Despite the modern conveniences, the **BASIC prompt** remains the primary interactive environment for many users. From the BASIC prompt, the user can:

- Load and run programs via `LOAD "name"`.
- Issue NedoDOS commands via the NedoDOS BASIC extension.
- Switch between DOSes (via port writes, for advanced users).
- Type in BASIC programs directly (as on the original Spectrum).

For users who grew up with the Spectrum, the BASIC prompt is still the most familiar interface — and the ZX Evolution's NedoDOS extension makes it capable of accessing all the modern hardware features.

---

## §9. Modern Status (2024)

The ZX Evolution remains the **flagship Russian Spectrum hardware** in 2024. Its status is healthy, with active development and a vibrant user community.

### 9.1 Hardware availability

The ZX Evolution is no longer in mass production, but it is still manufactured in small batches by the NedoPC team and various community members. Boards are sold via Russian-language forums and online stores. A typical ZX Evolution setup costs around 200–300 USD (board only) or 400–500 USD (with case, power supply, and accessories).

For users who want a more affordable option, several **derivative boards** exist:

- **Sprinter** — an earlier FPGA-Spectrum, less capable but cheaper.
- **ZX-Uno** — a Spanish-designed FPGA-Spectrum board, similar in concept but smaller and cheaper.
- **Mister-style boards** (with the right Spectrum core) — offer a more modern alternative, though without native Pentagon compatibility.

But for users specifically wanting a Russian-style Spectrum experience, the ZX Evolution remains the gold standard.

### 9.2 Active development

The NedoPC team and the wider community continue to develop the ZX Evolution's software stack:

- **BaseConf updates** are released periodically, adding features (more video modes, more memory, more I/O options) and fixing bugs.
- **NedoDOS** is under active development, with new versions supporting larger SD cards, faster transfer rates, and additional file formats.
- **TS-Conf** continues to evolve, with new graphics features added regularly.
- **Applications and games** are still being written for the platform, including new demos, games, and utilities.

The development is primarily Russian-language, with English translations available for major releases.

### 9.3 Documentation and community

The ZX Evolution is well-documented (in Russian) on the **nedopc.com** website and in the Russian Spectrum community forums. English documentation is more sparse but available for the major features.

The community is active — new users are welcomed, questions are answered, and the culture is one of experimentation and improvement. For an English-speaking user willing to use translation tools, the Russian community is accessible.

### 9.4 Comparison with the ZX Spectrum Next

The ZX Evolution is sometimes compared to the **ZX Spectrum Next** — the Western equivalent FPGA-Spectrum. The two share the FPGA approach but differ in important ways:

| Aspect | ZX Evolution | ZX Spectrum Next |
|---|---|---|
| Origin | Russia (NedoPC team) | UK (SpecNext team) |
| Primary compatibility | Pentagon 1024 (Russian) | Original 48K/128K (Sinclair) |
| Extended graphics | TS-Conf | Layer 2, hardware sprites, tilemap |
| Storage | CF + SD (SPI) | SD + IDE |
| Output | VGA, composite | HDMI, VGA, composite |
| Keyboard | PS/2 (external) | Built-in + PS/2 |
| Case | Usually sold bare-board | Available with case |
| Community language | Primarily Russian | Primarily English |
| Software library | Russian scene (Pentagon) | Western scene (Sinclair) |
| Price | ~300-500 USD | ~250-400 USD (kickstarter pricing) |

Neither is "better" — they target different communities and different software libraries. The ZX Evolution is the right choice for users interested in the Russian Spectrum scene; the ZX Spectrum Next is the right choice for users interested in the Western scene. (See [nextzxos.md](nextzxos.md) for the Next's OS.)

### 9.5 Future directions

The ZX Evolution's future is tied to the health of the Russian Spectrum scene. As long as that scene continues to produce new software and engage new users, the ZX Evolution will continue to be developed and supported. The FPGA approach means the hardware can continue to evolve without new physical boards — new BaseConfs and new TS-Conf features can be downloaded and installed indefinitely.

The biggest risk to the platform is **component availability** — the Altera Cyclone FPGA used in the ZX Evolution is no longer in current production (Altera was acquired by Intel, and the Cyclone series has been superseded). If stocks of the specific FPGA run out, future production runs may need to be redesigned around a newer FPGA, which would require porting the BaseConf.

For now (2024), the platform is healthy, and the community is active. New users are still joining, and the platform continues to evolve.

---

## §10. Cross-References

### 10.1 Within the Operating Systems section

- **[nedo_dos.md](nedo_dos.md)** — The primary DOS for the ZX Evolution. This article and nedo_dos.md are designed to be read together: this article covers the hardware/firmware layer, nedo_dos.md covers the DOS layer.
- **[trdos.md](trdos.md)** — The classic Russian DOS. The ZX Evolution supports TR-DOS for backward compatibility.
- **[is_dos.md](is_dos.md)** — An older Russian hierarchical DOS, occasionally used on the ZX Evolution.
- **[nextzxos.md](nextzxos.md)** — The Western equivalent: the OS for the ZX Spectrum Next. Useful for comparison.
- **[esxdos.md](esxdos.md)** — A modern Western DOS, conceptually similar to NedoDOS but for different hardware.
- **[rom_versions.md](rom_versions.md)** — Catalogue of original Sinclair ROM versions, for understanding what the ZX Evolution emulates.
- **[rom_plus2.md](rom_plus2.md)** — Internals of the +2A/+3 ROM. The ZX Evolution's ROM slot management is conceptually similar.

### 10.2 Outside the section

- **[../02_hardware/clones/README.md](../02_hardware/clones/README.md)** — Russian clone hardware reference, including the Pentagon, Scorpion, and ATM Turbo that the ZX Evolution impersonates.
- **[../02_hardware/clones/clone_timing.md](../02_hardware/clones/clone_timing.md)** — How Russian clone timing differs from original Sinclair timing.
- **[../05_development/03_memory_and_io/memory_and_io_pentagon.md](../05_development/03_memory_and_io/memory_and_io_pentagon.md)** — The Pentagon memory model, which the ZX Evolution's default BaseConf implements.

### 10.3 External resources

- **[nedopc.com](https://nedopc.com)** — The NedoPC team's website, with hardware documentation, BaseConf downloads, and NedoDOS releases.
- **speccy.info** — A Russian-language Spectrum wiki with detailed ZX Evolution information.
- **[zx-pk.ru](https://zx-pk.ru)** — The main Russian Spectrum community forum.

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same license.
