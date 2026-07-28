[← Home](../../README.md) · [Emulation](../README.md) · [MCU Emulation](README.md)

# KR1818VG93 / WD1793 FDC on a Microcontroller

The **Beta 128** disk interface and its associated floppy disk controller (FDC) — the Western Digital **WD1793** or its Russian equivalent **KR1818VG93** (often just called the **VG93**) — were the standard mass-storage interface for Russian Spectrum clones (Pentagon, Scorpion, ATM Turbo) and many Western upgrades. Original FDC chips are now 30+ years old and frequently failing, and floppy diskettes themselves are degrading rapidly. Replacing the FDC with a modern MCU that emulates its behaviour — while loading disk images from SD card instead of physical floppies — is one of the most practical retro-computing upgrades.

The **VG93Em-STM32** project is the canonical open-source implementation: an STM32 microcontroller programmed to behave exactly like a VG93/WD1793, presenting the same register interface to the host computer while internally serving "tracks" from SD-card-stored disk images. This article covers the FDC's behaviour, the replacement approach, and the implementation details.

For background on the Beta 128 interface and TR-DOS, see [the disk interface documentation](../../02_hardware/). For SD-card-based storage more generally, see [mcu_sd_interface.md](mcu_sd_interface.md).

---

## The Beta 128 and VG93/WD1793

### The WD1793 Floppy Disk Controller

The **Western Digital WD1793** (and its variants WD1791, WD1792, WD1795, WD1797) is a single-chip floppy disk controller introduced in the late 1970s. It handles the low-level protocol of reading and writing floppy diskettes:

- **MFM/FM encoding/decoding** — converts the raw magnetic flux transitions on the disk into data bytes (MFM = Modified Frequency Modulation, used by double-density disks; FM = Frequency Modulation, used by single-density)
- **Track seeking** — moves the read/write head to the correct cylinder
- **Sector reading** — locates a specific sector by ID and reads its data
- **Sector writing** — locates a sector and writes new data
- **CRC generation/checking** — ensures data integrity
- **Index pulse detection** — synchronises to the physical disk rotation

The WD1793 presents a simple register interface to the host:

| Register | Function |
|---|---|
| Command | Write a command (restore, seek, step, step-in, step-out, read sector, write sector, read address, read track, write track, force interrupt) |
| Status | Read the current command's status (busy, index, track 0, CRC error, seek error, write protect, record not found, lost data, data request) |
| Track | Current track register |
| Sector | Desired sector register |
| Data | Data byte (for read/write) |

The host (in the Spectrum's case, the TR-DOS ROM) issues commands by writing to the Command register, then polls the Status register until the command completes, reading or writing data bytes via the Data register as needed.

### The KR1818VG93

The **KR1818VG93** is the Russian clone of the WD1793. Produced through the 1980s and 1990s, it is pin-compatible and register-compatible with the WD1793. Software written for one runs identically on the other. Russian Spectrum clones (Pentagon, Scorpion, ATM Turbo) all use the KR1818VG93.

### The Beta 128 Disk Interface

The **Beta 128** is a disk interface add-on for the Spectrum, designed in Russia (and used by Western clones like the Scorpion and ATM Turbo). It consists of:

- The FDC chip (WD1793 or KR1818VG93)
- A **ROM** containing the TR-DOS operating system (paged into the Spectrum's address space when accessed)
- An **interface connector** for the floppy disk drive cable (34-pin IDC, standard PC floppy drive)
- **Address decoding logic** — selecting the FDC's registers and the TR-DOS ROM based on I/O port addresses

The Beta 128 occupies I/O ports `0x1F`, `0x3F`, `0x5F`, `0x7F` for the FDC's four registers, and `0xFF`/`0x7FFD` interactions for memory banking.

### TR-DOS

**TR-DOS** is the disk operating system that runs on the Beta 128. Developed by **Mikhail "Misha" Shumakov** in the late 1980s, TR-DOS provides:

- File operations (load, save, catalog, delete, rename)
- Disk formatting
- A BASIC extension (commands like `CAT`, `LOAD *"file"`, `SAVE *"file"`)
- A binary loader for executable files

TR-DOS is essentially a thin layer over the Beta 128 hardware — it issues FDC commands to read/write sectors, then assembles them into files.

---

## Why Replace the FDC with an MCU?

Several motivations drive FDC-on-MCU projects:

### Failing Original Chips

The WD1793 and KR1818VG93 are 30+ years old and increasingly unreliable. Common failures include:

- **Read errors** — the FDC reports CRC errors on disks that are actually fine
- **Write failures** — data written to disk is corrupted
- **Seek failures** — the FDC cannot move the head to the requested track
- **Complete failure** — the chip does not respond at all

A modern MCU replacement eliminates the failing silicon.

### Media Degradation

5.25" and 3.5" floppy diskettes are degrading rapidly due to:

- **Magnetic domain decay** — the recorded signal weakens over time
- **Physical deterioration** — the magnetic coating flakes off the disk substrate
- **Fungal growth** — organic contaminants grow on the disk surface
- **Mechanical wear** — each read/write cycle damages the disk slightly

By moving to SD-card-stored disk images (`.trd`, `.scl`, `.fdi` formats), the media becomes effectively permanent.

### Convenience

Loading software from SD card is faster than from floppy, and the catalog of available software is much larger (the entire Russian Spectrum software archive fits easily on a small SD card).

### Authentic Form Factor Preservation

For owners of original Pentagon / Scorpion / ATM Turbo hardware, an MCU-based FDC replacement allows the original machine to keep running without modification to the rest of the system. The MCU presents the same register interface as a real FDC, so TR-DOS and all software continue to work unchanged.

---
## VG93Em-STM32 — The Reference Implementation

The **VG93Em-STM32** project is the canonical open-source FDC-on-MCU implementation. Designed by Russian retro-computing enthusiasts, it uses an STM32 microcontroller (typically an STM32F103 or STM32F407) to emulate the VG93 chip and serve disk images from an SD card.

### Hardware

The VG93Em-STM32 hardware consists of:

- **STM32F103C8T6** (the "Blue Pill" board) or **STM32F407** (more capable)
- **MicroSD card slot** — connected via SPI
- **40-pin connector** — to plug into the Beta 128 socket on the host motherboard (replacing the original VG93 chip)
- **Optional status LEDs** — showing read/write activity
- **Optional configuration jumpers** — selecting drive number, disk image, etc.

The MCU runs at 72 MHz (STM32F103) or 168 MHz (STM32F407), providing ample performance for FDC emulation. The SD card interface uses SPI at 12–25 MHz, allowing fast disk image access.

### Firmware

The firmware implements the VG93 register interface and the command set:

```c
// Pseudocode for the VG93 emulator
typedef struct {
    uint8_t command;   // Current command
    uint8_t status;    // Status register
    uint8_t track;     // Track register
    uint8_t sector;    // Sector register
    uint8_t data;      // Data register
    // Internal state
    int current_track;
    int current_sector;
    int data_index;
    uint8_t sector_buffer[256];  // One sector of data
    // Disk image info
    FILE *disk_image;
    int disk_tracks;
    int disk_sectors_per_track;
} vg93_state_t;

// Handle a write to the command register
void vg93_write_command(vg93_state_t *state, uint8_t cmd) {
    state->command = cmd;
    switch (cmd & 0xF0) {
        case 0x00:  // Restore (seek to track 0)
            vg93_restore(state);
            break;
        case 0x10:  // Seek to a specific track
            vg93_seek(state, state->data);
            break;
        case 0x20:  // Step (no update)
        case 0x30:  // Step (with update)
            vg93_step(state, cmd);
            break;
        case 0x40:  // Step in (no update)
        case 0x50:  // Step in (with update)
            vg93_step_in(state, cmd);
            break;
        case 0x60:  // Step out (no update)
        case 0x70:  // Step out (with update)
            vg93_step_out(state, cmd);
            break;
        case 0x80:  // Read sector
        case 0x90:  // Read sector (multi-record)
            vg93_read_sector(state, cmd);
            break;
        case 0xA0:  // Write sector
        case 0xB0:  // Write sector (multi-record)
            vg93_write_sector(state, cmd);
            break;
        case 0xC0:  // Read address
            vg93_read_address(state);
            break;
        case 0xE0:  // Read track
            vg93_read_track(state);
            break;
        case 0xF0:  // Write track
            vg93_write_track(state);
            break;
        case 0xD0:  // Force interrupt
            vg93_force_interrupt(state, cmd);
            break;
    }
}

// Handle a read of the status register
uint8_t vg93_read_status(vg93_state_t *state) {
    return state->status;
}

// Handle a read of the data register
uint8_t vg93_read_data(vg93_state_t *state) {
    return state->data;
}
```

The firmware's main loop waits for I/O writes from the host, decodes the command, performs the necessary SD card reads/writes, and updates the status register appropriately.

### Disk Image Formats

The VG93Em-STM32 supports several disk image formats:

- **`.trd`** — the standard TR-DOS disk image, 640 KB (80 tracks × 16 sectors × 256 bytes) for 5.25" DS/DD disks
- **`.scl`** — a sector-based image, similar to `.trd` but with different header
- **`.fdi`** — a full disk image including raw MFM data (preserves copy protection)
- **`.imd`** — ImageDisk format, also preserves raw MFM data
- **`.opd` / `.dsk`** — other emulator formats

The firmware loads the appropriate track from the SD card when the host seeks to a new track, and reads/writes individual sectors within that track.

### Seek Emulation

When the host writes to the Track register or issues a Seek/Step command, the emulator updates its internal track pointer and loads the corresponding track data from the SD card. The seek operation takes some time (a few milliseconds for SD card access), which is reflected in the status register's BUSY bit.

A real FDC also has a "settle time" — a delay after reaching the target track before reading can begin. The emulator reproduces this delay to match the real chip's timing.

### Sector Read/Write Emulation

When the host issues a Read Sector command:

1. The emulator locates the requested sector in the current track's data
2. Sets the status register's DRQ (Data Request) bit
3. The host reads the Data register to get each byte
4. After 256 bytes (one sector), the status register shows completion

Write Sector is the reverse: the host writes each byte to the Data register, and the emulator stores them in the sector buffer, writing to the SD card when the sector is complete.

### Status Register Emulation

The status register bits must be set correctly:

| Bit | Meaning |
|---|---|
| 7 | Motor On |
| 6 | Write Protect |
| 5 | Spin-Up/Ready |
| 4 | Record Not Found / Seek Error |
| 3 | CRC Error |
| 2 | Track 0 |
| 1 | Index Pulse |
| 0 | Busy |

The host polls these bits to determine command completion and error conditions. Correct emulation is critical for TR-DOS compatibility.

### Timing Considerations

A real FDC operates at the floppy disk's rotational speed (300 RPM for most 5.25" drives = 200 ms per revolution, so 12.5 ms per sector at 16 sectors/track). The emulator does not have a real disk, but it must respect these timings:

- **Command completion** — read/write commands should complete in roughly the time it would take a real disk
- **DRQ timing** — the DRQ bit must be asserted at the right intervals (every 31 µs for a 256-byte sector at standard density)
- **Index pulse** — must be generated periodically

If the emulator responds too fast, some software (especially copy protection that measures disk timing) may behave incorrectly. If too slow, the host may time out.

---
## Alternative Implementations

Beyond the VG93Em-STM32, several other projects offer MCU-based FDC replacement:

### ESP32-Based Emulators

ESP32 microcontrollers can also emulate the VG93, leveraging their faster CPU (240 MHz) and additional features (Wi-Fi for network-based disk image serving). Some projects allow loading `.trd` files over Wi-Fi from a server, eliminating the SD card entirely.

### RP2040-Based Emulators

The RP2040 is increasingly used for FDC emulation. Its PIO blocks can drive the FDC interface with precise timing, and its dual CPU cores can handle both the FDC logic and the SD card I/O concurrently.

### FPGA Implementations

For users preferring the FPGA route, the [MiSTer](../fpga/mist_mister_core.md) and [ZX-Uno](../fpga/zx_uno_core.md) cores include VG93 implementations in HDL. These offer cycle-exact timing but require an FPGA platform.

### Comparison

| Implementation | Cost | Difficulty | Timing Accuracy | Best For |
|---|---|---|---|---|
| **VG93Em-STM32** | ~£5 | Moderate | Good | Drop-in replacement for original Beta 128 |
| **ESP32-based** | ~£5 | Moderate | Good | Wi-Fi-enabled, network disk serving |
| **RP2040-based** | ~£2 | Moderate | Good | Lower cost, hobbyist builds |
| **FPGA (MiSTer)** | ~£130 | Hard | Excellent | Full-system recreation |
| **Real FDC + Gotek** | ~£30 | Easy | Authentic | Modifying original hardware |

### Gotek Floppy Emulators

A related but different approach: instead of replacing the FDC chip, **Gotek** floppy emulators replace the physical floppy drive with an MCU-based device that presents itself as a floppy drive to the existing FDC. The Gotek reads `.trd` files from USB stick and feeds them to the host's existing FDC. This requires no modification to the Spectrum/Beta 128 hardware.

The HxC firmware for Gotek supports many disk image formats and is widely used in retro-computing.

---

## Integration with Real Hardware

To integrate an MCU-based FDC replacement with original hardware:

### Drop-in Chip Replacement

The MCU is mounted on a small PCB with the same pinout as the original VG93 (40-pin DIP). The PCB plugs directly into the VG93 socket on the host motherboard. The SD card slot is mounted on a flexible extension cable to be accessible from outside the case.

This approach requires:

- **Pinout adapter** — mapping the MCU's GPIO pins to the 40-pin DIP layout of the VG93
- **Level shifters** — the host system uses 5V logic; the MCU is 3.3V
- **SD card slot** — external, accessible without opening the case
- **Configuration interface** — buttons or jumpers to select the active disk image

### External Module

Alternatively, the MCU module can be external, connected to the host via a cable. This allows the original VG93 to remain in place (for authenticity) while routing the disk interface to the MCU module.

### Software Compatibility

A well-implemented FDC replacement is transparent to the host software. TR-DOS, all games and demos that use TR-DOS, and all Beta 128 utilities should work unchanged. Copy protection that depends on specific FDC timing or behaviour may fail — for these, a real FDC with a Gotek may be preferable.

---

## Copy Protection Considerations

Some Spectrum disk software includes copy protection that probes FDC behaviour in unusual ways:

- **Non-standard sector sizes** — 128, 1024, or 2048 bytes per sector instead of the standard 256
- **Non-standard sector IDs** — sector numbers outside the usual 1–16
- **Hidden tracks** — tracks beyond the standard 80 (e.g., track 81, 82)
- **Weak bits / fuzzy bits** — areas of the disk where the magnetic signal is intentionally ambiguous, producing different read results each time
- **Timing-based protection** — measures the time between specific FDC events

The VG93Em-STM32 and similar projects handle the standard cases well but may fail on advanced copy protection. The `.fdi` and `.imd` formats (which preserve raw MFM data) can sometimes help, but weak bits and timing-based protection remain difficult to emulate.

For most software (games, demos, system software), the MCU-based FDC works perfectly. For copy-protected titles, the user may need to find a "cracked" version (with the protection removed) or use a different approach.

---

## FAQ

**Q: Can I use any STM32 for the FDC replacement?**

A: An STM32F103 (Blue Pill) works but is at the lower end of performance. STM32F407 (Black Pill / Discovery) provides more headroom and is recommended for serious builds. RP2040 and ESP32 are also viable.

**Q: Does the emulator work with all TR-DOS software?**

A: Yes, for 95%+ of TR-DOS software. The exceptions are games/demos with advanced copy protection or those that use non-standard FDC commands. The standard TR-DOS command set (read sector, write sector, seek, restore) is fully supported.

**Q: How do I select which disk image is loaded?**

A: Most implementations provide either: physical buttons on the MCU module that cycle through images on the SD card, a small OLED display with a menu, or a configuration file (`config.ini` or similar) on the SD card. Some advanced versions allow image switching via a host-side utility.

**Q: Can I write back to the disk images?**

A: Yes — write operations to the SD card are supported, allowing the host to save files, modify disks, etc. The SD card's limited write endurance (100k writes per sector) is not a concern for typical retro use.

**Q: Do I need to preserve the original Beta 128 ROM?**

A: Yes — the Beta 128's TR-DOS ROM must still be present (or emulated). The MCU only replaces the FDC chip, not the ROM. Some integrated designs include the TR-DOS ROM in the MCU's flash, but this is less common.

**Q: Why is the SD card accessed via SPI rather than SDIO?**

A: SPI is simpler, widely supported, and fast enough for floppy emulation (which requires ~500 kbps for double-density MFM). SDIO offers higher speed but requires more pins and a more complex driver.

**Q: How accurate is the timing of the emulator?**

A: For most operations, within a few microseconds of a real FDC. This is accurate enough for TR-DOS but may not satisfy software that measures sub-microsecond timing. The `.fdi`/`.imd` formats and higher-performance MCUs (STM32F407) improve accuracy.

---

## Summary

Replacing the WD1793 or KR1818VG93 FDC with a modern MCU is a practical and popular upgrade for owners of Pentagon, Scorpion, and other Russian Spectrum clones. The **VG93Em-STM32** project demonstrates the approach:

1. **Drop-in chip replacement** — MCU presents the same 40-pin DIP interface as the original FDC
2. **SD-card-based storage** — disk images (`.trd`, `.scl`, `.fdi`) replace physical floppies
3. **Register-accurate emulation** — the host software (TR-DOS) sees no difference
4. **Timing-aware** — DRQ and status bits are set with realistic timing

With these elements in place, the original hardware continues to work with all its software, while benefiting from the reliability and convenience of SD-card storage. Copy protection remains the main limitation, but for most software the emulator is transparent.

---

## References

- **Western Digital WD1793 datasheet** — register interface, command set, timing
- **KR1818VG93 datasheet** (Russian) — pinout and behaviour
- **VG93Em-STM32 project** — GitHub repository with schematics and firmware
- **TR-DOS documentation** — file format, BASIC extension, command reference
- **Beta 128 documentation** — interface specification, port addresses
- **HxC Gotek firmware** — alternative approach using a physical floppy drive emulator
- **`.trd` / `.scl` / `.fdi` format specifications** — disk image layouts

## Cross-references

- [SD card interface on MCU](mcu_sd_interface.md) — broader SD-card storage topics
- [Z80 on MCU](mcu_z80.md) — companion article on CPU replacement
- [ULA on MCU](mcu_ula.md) — companion article on ULA replacement
- [PSG/AY on MCU](mcu_psg_ay.md) — sound chip replacement
- [MiSTer](../fpga/mist_mister_core.md) / [ZX-Uno](../fpga/zx_uno_core.md) / [ZX Evolution](../fpga/zxevo.md) — FPGA alternatives with built-in VG93 emulation
- [MCU design patterns](mcu_design_patterns.md) — general bus interfacing techniques
