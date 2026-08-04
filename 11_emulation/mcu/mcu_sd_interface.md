[← Home](../../README.md) · [Emulation](../README.md) · [MCU Emulation](README.md)

# SD Card Interface on a Microcontroller

Mass storage is one of the most useful upgrades for a Spectrum. Original storage — **cassette tape** (slow, unreliable) and **floppy disk** (the Beta 128 / TR-DOS system, requiring 30-year-old media and drives) — is increasingly impractical. Modern **SD card** storage offers gigabytes of capacity in a tiny form factor, loading software in milliseconds instead of minutes.

An **SD card interface on an MCU** connects an SD card to the Spectrum, presenting the storage either as a **TR-DOS disk image** (compatible with all Beta 128 software), as a **Tape Interface** (loading `.tap`/`.tzx` files), or as a **generic mass storage device** accessed via custom software.

This article covers SD card protocols, the design of SD interfaces on MCU, file system support, image loading, and existing projects such as **DivMMC**, **ZXMMC**, and **ZX Div Future OS**. For background on Beta 128 and TR-DOS, see [the FDC documentation](mcu_fdc_vg93.md). For SD cards used with the [VG93 emulator](mcu_fdc_vg93.md), that article covers the storage side; here we cover the SD interface itself.

---

## Why SD Cards?

### Capacity

A single SD card holds thousands of Spectrum programs:

- **Spectrum software archive** — the entire archive of Spectrum software (World of Spectrum, etc.) is a few gigabytes
- **Disk image collections** — thousands of `.trd` (TR-DOS) images fit easily on a 1 GB card
- **Tape images** — tens of thousands of `.tap`/`.tzx` files fit on a small card

For comparison, a single floppy diskette holds 640 KB (`0.5 MB`) — a 1 GB SD card holds the equivalent of 1,500 floppies.

### Speed

SD card access is much faster than floppy:

- **SD card** — read speeds of 10-25 MB/s via SPI
- **Floppy disk** — read speed of ~62 KB/s (300 RPM × 16 sectors/track × 256 bytes/sector = ~62 KB/s)

A Spectrum program that takes 30 seconds to load from floppy loads in less than a second from SD.

### Reliability

SD cards are solid-state — no moving parts, no magnetic media to degrade. They have write endurance of 100,000+ writes per sector, which is effectively unlimited for retro computing use.

### Cost

A small SD card (4 GB or 8 GB) costs ~£2-3. MicroSD cards are even cheaper. The SD card reader hardware is similarly cheap — the SD card slot is a simple PCB-mounted connector.

---

## SD Card Basics

### SD Card Families

Several SD card families exist:

- **SDSC** (Standard Capacity) — up to 2 GB, original SD spec
- **SDHC** (High Capacity) — 4 GB to 32 GB, most common today
- **SDXC** (Extended Capacity) — 64 GB to 2 TB, requires exFAT file system
- **SDUC** (Ultra Capacity) — 2 TB to 128 TB, very new, rare

For Spectrum use, **SDHC** is the sweet spot — 4 GB to 32 GB, FAT32 file system, cheap, widely available.

### Form Factors

Three form factors are common:

- **Standard SD** (32 × 24 mm) — the original, used in most adapters
- **miniSD** (21.5 × 20 mm) — rare, mostly obsolete
- **microSD** (15 × 11 mm) — the most common today, used in phones and most consumer electronics

Most retro-computing SD adapters use **microSD** due to its small size. A full-size SD slot is sometimes preferred for durability (microSD cards are small and easy to lose).

### SD Card Protocols

SD cards support two protocols:

- **SPI mode** — uses 4 signals (CS, SCK, MOSI, MISO), slower but simpler. Supported by virtually all MCUs.
- **SDIO mode** — uses 4 or 8 data lines, faster but more complex. Requires MCU hardware support (STM32, ESP32, some others).

For retro-computing use, **SPI mode** is preferred — it's slower but easier to implement and works with any MCU. Speeds of 12-25 MHz are typical in SPI mode, giving 1.5-3 MB/s effective throughput, which is more than enough for Spectrum use.

---

## Hardware Connection

### SPI Mode Pinout

In SPI mode, the SD card uses 4 signals:

| SD Card Pin | SPI Function | Typical MCU Pin |
|---|---|---|
| DAT2 | (unused in SPI mode) | (often pulled high with 10K) |
| CD/DAT3 | CS (Chip Select) | Any GPIO |
| CMD | MOSI (Master Out, Slave In) | SPI MOSI |
| VDD | +3.3V power | +3.3V supply |
| CLK | SCK (Serial Clock) | SPI SCK |
| VSS | Ground | Ground |
| DAT0 | MISO (Master In, Slave Out) | SPI MISO |
| DAT1 | (unused in SPI mode) | (often pulled high with 10K) |

The MCU's SPI peripheral drives CS, SCK, MOSI and reads MISO. All signals are 3.3V logic level — the SD card is **not 5V tolerant**.

### Level Shifting

If the host MCU is 5V (like an Arduino), level shifting is required between the MCU and the 3.3V SD card. A simple resistor divider on MOSI/SCK/CS (5V → 3.3V) and a buffer or direct connection on MISO (3.3V is high enough for 5V TTL logic) is often sufficient.

For 3.3V MCUs (RP2040, ESP32, STM32), no level shifting is needed — the SD card connects directly.

### Power Supply

The SD card requires **3.3V at up to 100 mA** during write operations. Most MCU boards have a 3.3V regulator that can supply this — but check the regulator's current rating. Some cheap Arduino clones have weak 3.3V regulators that cannot drive an SD card reliably.

### Card Detection

Most SD card sockets include a **card detect (CD)** switch — a mechanical switch that closes when a card is inserted. This can be connected to a GPIO to detect card insertion/removal, allowing the firmware to remount the file system.

A **write protect (WP)** switch is also present on full-size SD cards (but not microSD). Most retro adapters ignore WP.


---

## SD Card SPI Protocol

The SD card SPI protocol is documented in the SD Physical Layer Specification. Key aspects:

### Initialization Sequence

SD cards power up in a "native" (SDIO) mode and must be switched to SPI mode:

1. **Power up** — apply 3.3V, wait 1 ms for the card to power up
2. **Clock at 100-400 kHz** — slow clock for initialisation
3. **Send 80 dummy clocks** — with CS high and MOSI high, to wake the card
4. **Send CMD0 (RESET) with CS low** — switches the card to SPI mode. The card responds with the R1 response byte `#01` (idle state)
5. **Send CMD8 (SEND_IF_COND)** — checks the card's voltage range. SDHC/SDXC cards respond with the voltage window in R7 response
6. **Send CMD55 + ACMD41 (SD_SEND_OP_COND)** repeatedly — initializes the card. Send ACMD41 with HCS bit (bit 30) set to indicate SDHC support. The card responds with `#00` (ready) when initialisation completes
7. **Send CMD58 (READ_OCR)** — reads the Operating Conditions Register, which includes the CCS bit indicating if the card is SDHC (block-addressed) or SDSC (byte-addressed)
8. **Switch to high-speed clock** — increase SPI clock to 12-25 MHz for normal operation

After initialisation, the card is ready for read/write operations.

### Read/Write Commands

Once initialized, the card uses these commands:

- **CMD17 (READ_SINGLE_BLOCK)** — reads one 512-byte block at a given address. The card responds with a start token, 512 bytes of data, and a 2-byte CRC
- **CMD24 (WRITE_BLOCK)** — writes one 512-byte block. The host sends a start token, 512 bytes of data, and a 2-byte CRC. The card responds with a data response token
- **CMD18 (READ_MULTI_BLOCK)** — reads multiple consecutive blocks until CMD12 (STOP_TRANSMISSION) is sent
- **CMD25 (WRITE_MULTI_BLOCK)** — writes multiple consecutive blocks until STOP is sent
- **CMD13 (SEND_STATUS)** — reads the card's status register

For SDHC/SDXC cards, addresses are **block numbers** (each block is 512 bytes). For SDSC cards, addresses are **byte addresses**. This is why CMD58 (READ_OCR) is important — it tells the host which addressing scheme to use.

### Pseudocode

```c
// Initialize SD card in SPI mode
int sd_init(spi_t *spi) {
    // 1. Power-up delay
    delay_ms(1);
    
    // 2. Set slow SPI clock (400 kHz)
    spi_set_clock(spi, 400000);
    
    // 3. Send 80 dummy clocks (10 bytes of 0xFF with CS high)
    sd_cs_high();
    for (int i = 0; i < 10; i++) spi_transfer(spi, 0xFF);
    
    // 4. Send CMD0 (RESET) — switch to SPI mode
    sd_cs_low();
    uint8_t r1 = sd_send_command(spi, 0, 0, 0x95);
    if (r1 != 0x01) return SD_ERROR;  // Expected idle state
    
    // 5. Send CMD8 (SEND_IF_COND)
    uint8_t r7[4];
    r1 = sd_send_command_r7(spi, 8, 0x000001AA, r7);
    // Check voltage range in r7
    
    // 6. Send ACMD41 until initialised
    int timeout = 1000;
    do {
        sd_send_command(spi, 55, 0, 0);  // CMD55 (app command prefix)
        r1 = sd_send_command(spi, 41, 0x40000000, 0);  // ACMD41 with HCS bit
        if (--timeout == 0) return SD_ERROR;
        delay_ms(1);
    } while (r1 != 0x00);  // Loop until not idle
    
    // 7. Read OCR to check SDHC
    uint8_t ocr[4];
    sd_send_command_r3(spi, 58, 0, ocr);
    int is_sdhc = (ocr[0] & 0x40) != 0;  // CCS bit
    
    // 8. Switch to high-speed clock (25 MHz)
    spi_set_clock(spi, 25000000);
    
    return is_sdhc ? SD_SDHC : SD_SDSC;
}

// Read a 512-byte block
int sd_read_block(spi_t *spi, uint32_t block_num, uint8_t *buffer) {
    uint32_t addr = is_sdhc ? block_num : (block_num * 512);
    uint8_t r1 = sd_send_command(spi, 17, addr, 0);
    if (r1 != 0x00) return SD_ERROR;
    
    // Wait for start token (0xFE)
    int timeout = 1000;
    uint8_t token;
    do {
        token = spi_transfer(spi, 0xFF);
    } while (token == 0xFF && --timeout > 0);
    if (token != 0xFE) return SD_ERROR;
    
    // Read 512 bytes + 2 CRC bytes
    for (int i = 0; i < 512; i++) buffer[i] = spi_transfer(spi, 0xFF);
    spi_transfer(spi, 0xFF);  // CRC byte 1
    spi_transfer(spi, 0xFF);  // CRC byte 2
    
    return SD_OK;
}
```

---

## File System Support

Most SD adapters present a **FAT16 or FAT32 file system** to the host computer, allowing the SD card to be loaded with files from any PC. The MCU implements a FAT file system driver to read these files.

### FAT16 vs FAT32

- **FAT16** — used for SDSC cards (up to 2 GB), supports up to 2 GB per partition
- **FAT32** — used for SDHC cards (4 GB to 32 GB), supports up to 32 GB per partition (in practice, larger is possible but unusual)
- **exFAT** — used for SDXC cards (64 GB+), requires licensing from Microsoft, rarely implemented in MCU projects

For Spectrum use, **FAT32 on SDHC** is the standard choice.

### FAT File System Implementation

A FAT file system driver for MCU includes:

- **Boot sector parsing** — read the BIOS Parameter Block (BPB) to determine cluster size, FAT location, root directory location
- **FAT table access** — follow cluster chains to read a file's data
- **Directory listing** — read directory entries (8.3 filenames or LFN for long filenames)
- **File open/read/write** — high-level file operations

Open-source FAT libraries for MCU:

- **FatFs by Elm-Chan** — the de facto standard FAT library for MCU, well-documented, portable, supports FAT12/16/32, LFN, multiple partitions
- **Petit FatFs** — a smaller version of FatFs, read-only, for MCUs with limited RAM
- **Arduino SD library** — based on an older version of FatFs, simplified API

Using FatFs with an RP2040 or STM32 is straightforward — the library handles all the FAT details, the user just calls `f_open`, `f_read`, `f_write`, etc.

---
## Spectrum Integration

An SD interface can be integrated with the Spectrum in several ways:

### DivMMC / DivMMC EnJon

**DivMMC** is the most popular SD interface standard for the Spectrum, designed as a modern successor to the original **DivIDE** (which used IDE hard drives). A DivMMC interface:

- Plugs into the Spectrum's **expansion port**
- Contains an MCU (often an ATmega or RP2040) and an SD card slot
- Presents a **memory-mapped interface** to the Spectrum — a 16 KB "DivMMC ROM" is paged into the Spectrum's address space when accessed
- The ROM contains a file browser (often **ESXOS** or **DIVI**) that the user navigates to load software
- Loads `.tap`, `.tzx`, `.z80`, `.sna`, `.scr`, and other formats

When the user selects a `.tap` file in the browser, the DivMMC plays it through the Spectrum's EAR input — loading it as if from a tape, but at much higher speed.

The **DivMMC EnJon** is a specific commercial implementation — a small expansion port device that includes DivMMC functionality, plus a Kempston joystick port.

### ZXMMC

**ZXMMC** is another SD interface standard, similar to DivMMC. Originally designed by **Zaxos** and later developed by the community. Uses SPI to talk to the SD card directly from the Spectrum's Z80 — no MCU involved (the Z80 bit-bangs SPI via I/O ports).

This is a different approach from DivMMC — the Z80 directly accesses the SD card, rather than going through an MCU. This requires a small CPLD or GAL for address decoding, but no MCU firmware.

### ZXM DivMMC

The **ZX Div Future OS** and related projects provide a complete operating environment for SD-connected Spectrums, with file management, text editor, assembler, and more.

### Tape Emulation

A simpler approach is **tape emulation** — the MCU plays a `.tap` or `.tzx` file through the Spectrum's EAR input. This works with any Spectrum (no expansion port needed) and requires no special software on the Spectrum side. The Spectrum just thinks it's loading from a tape.

The disadvantage is that loading is at tape speed (or slightly faster) — not the near-instant loading of DivMMC. But for compatibility with all Spectrum models, tape emulation is the simplest option.

### Generic Mass Storage

For software that expects a file system (e.g., **TR-DOS**, **+3 DOS**), the SD interface can present itself as the appropriate storage device:

- For TR-DOS, the SD interface maps a `.trd` disk image to the Beta 128's I/O ports, as described in [mcu_fdc_vg93.md](mcu_fdc_vg93.md)
- For +3 DOS, the SD interface maps a `.dsk` image to the +3's FDC (a different chip, the uPD765)

This gives full compatibility with disk-based software.

---

## Image File Formats

The SD interface must understand various image formats to load them:

### Tape Formats

- **`.tap`** — the simplest tape format, containing raw blocks of data with headers. Each block has a sync pulse sequence, a header/data flag, the data bytes, and a checksum
- **`.tzx`** — a more comprehensive format, supporting all the variations of tape loading (custom speed loaders, copy protection tricks). Has a detailed header structure with different block types for pilot tones, data blocks, pure tones, etc.
- **`.csw`** — Compressed Square Wave, a sample-based format
- **`.wav`** — raw audio, played as if from a real tape

### Snapshot Formats

- **`.sna`** — a 48K snapshot, containing the contents of RAM plus CPU registers (PC, SP, AF, BC, DE, HL, IX, IY, etc.). Loading a `.sna` restores the Spectrum to the exact state when the snapshot was taken
- **`.z80`** — a more flexible snapshot format, supporting 48K and 128K Spectrums, with various extensions for hardware state
- **`.sp`**, **`.szx`**, **`.rzx`** — other snapshot formats, less common

### Disk Image Formats

- **`.trd`** — TR-DOS disk image, as covered in [FDC documentation](mcu_fdc_vg93.md)
- **`.dsk`** — a generic disk image format used by various emulators
- **`.fdi`** — raw MFM disk image, preserves copy protection

### Screen Formats

- **`.scr`** — a 6912-byte file containing the Spectrum's video memory (6144 bytes of pixel data + 768 bytes of attributes). Loading a `.scr` displays a still image instantly

### Loading and Converting

Some formats are simple enough to load directly (`.scr`, basic `.tap` blocks). Others require the MCU to perform conversion:

- **`.tzx`** — the MCU parses the block structure and plays each block through the EAR input in sequence
- **`.sna`/`.z80`** — the MCU writes the snapshot data to the Spectrum's RAM (via the expansion port bus), then jumps to the saved PC

For DivMMC and similar, the host Spectrum software typically handles most of the loading — the MCU just provides file access.

---
## Existing Projects

### DivMMC EnJon

The **DivMMC EnJon** is a popular commercial SD interface. It plugs into the Spectrum's expansion port and provides:

- microSD card slot
- DivMMC-compatible firmware (ESXOS)
- Kempston joystick port
- Tape input passthrough

The EnJon is widely available and supports most SD card formats.

### ZXMMC by Zaxos

**ZXMMC** is an open-source SD interface that uses direct SPI (no MCU). The Z80 bit-bangs SPI via I/O ports. This is a minimalist design — just a few logic chips for address decoding and the SD card slot.

### ZX-Uno (Integrated SD)

The [ZX-Uno FPGA Spectrum](../fpga/zx_uno_core.md) includes a built-in SD card interface, accessed via the same DivMMC protocol. This is the integrated approach — no separate adapter needed.

### MiSTer (Integrated SD)

The [MiSTer](../fpga/mist_mister_core.md) Spectrum core uses the MiSTer framework's SD card infrastructure, presenting disk and tape images via a menu system.

### Simple DIY Adapters

For hobbyists, building a simple SD adapter is straightforward:

- **Arduino** + SD card shield + a few wires to the Spectrum's expansion port or EAR input
- **RP2040** Pico + SD card breakout + custom firmware
- **ESP32** with built-in SD card slot on some boards

### Tape-only Emulators

For users who just want to load `.tap` files without modifying the Spectrum, **tape-only emulators** exist:

- A small device that connects to the Spectrum's EAR input
- An MCU plays a `.tap` or `.tzx` file from SD through the EAR input
- The Spectrum loads as if from a real tape

These are the simplest devices — they require no expansion port and no modifications to the Spectrum.

---

## Comparison of Approaches

| Approach | Cost | Difficulty | Compatibility | Best For |
|---|---|---|---|---|
| Tape emulator (EAR input) | ~£2 (Arduino + SD) | Easy | All Spectrums | Simple loading |
| DivMMC (expansion port) | ~£10-20 | Medium | All except +3 (mostly) | Best all-rounder |
| ZXMMC (expansion port) | ~£5 (DIY) | Hard (DIY PCB) | Same as DivMMC | Minimalist DIY |
| TR-DOS emulation (VG93) | ~£3 (STM32) | Medium | Beta 128/TR-DOS software | Pentagon/Scorpion owners |
| Integrated (ZX-Uno/MiSTer) | ~£50-150 | N/A | All | FPGA Spectrum owners |

For most users, a DivMMC adapter (commercial or DIY) is the best choice — it gives the widest compatibility with software and supports the most image formats.

---

## FAQ

### What's the maximum SD card size I can use?

Most SD adapters support SDHC cards (up to 32 GB) with FAT32. SDXC cards (64 GB+) require exFAT, which is rarely supported.

In practice, 32 GB is more than enough — the entire Spectrum software archive is a few GB.

### Why is my SD card not recognized?

Common causes:

- **Card not SDHC** — some adapters only support SDHC, not SDSC
- **Card formatted as NTFS or exFAT** — most adapters require FAT16 or FAT32
- **Wrong partition type** — the SD card must have a primary partition, not an extended partition
- **Card too large** — some adapters cannot address cards larger than 32 GB
- **Counterfeit card** — some cheap SD cards are counterfeit and have incorrect capacity

Format the card as FAT32 with a single primary partition and try again.

### Can I hot-swap the SD card?

Most adapters support hot-swapping — the MCU detects the card removal (via the CD pin) and unmounts the file system. When a new card is inserted, the MCU mounts it.

However, hot-swapping during a write can corrupt the file system. It's safer to "eject" the card via software (if the firmware supports it) or to power off before swapping.

### How fast is loading from SD?

Loading speed depends on the protocol:

- **Tape emulation** — at tape speed (~1500 baud = ~190 bytes/s) or faster if accelerated
- **DivMMC** — much faster, near-instant for snapshots, a few seconds for tape files via the "turbo" loading
- **Direct SD access (ZXMMC)** — depends on the Z80's SPI bit-bang speed, typically 50-200 KB/s

### Can I save to SD?

Yes — DivMMC and similar support writing back to SD. The user can save snapshots, save game progress, or save data files.

SD cards have write endurance of ~100,000 writes per sector. For typical retro use, this is effectively unlimited — saving a few snapshots per session is fine.

### Do I need a special ROM in the Spectrum?

For DivMMC, the DivMMC ROM itself is provided by the adapter (paged in when needed). The Spectrum's original ROM is unchanged.

For ZXMMC, the Z80 directly accesses the SD card, so no ROM is needed — but a small loader must be present in the Spectrum's RAM to bootstrap the process (often loaded from a small EEPROM or via tape).

### What about +3 DOS compatibility?

The +3 uses a different FDC (the uPD765) than the Beta 128 (the WD1793). Some SD interfaces can emulate the uPD765 as well, presenting `.dsk` images as +3 disks. This is less common than Beta 128 emulation.

---

## Summary

An SD card interface for the Spectrum performs these functions:

1. **Connects an SD card** via SPI to an MCU (or directly to the Z80 via bit-banged SPI)
2. **Implements a FAT file system** (typically FAT32) so the card can be loaded with files from any PC
3. **Loads various image formats** — `.tap`/`.tzx` (tape), `.sna`/`.z80` (snapshots), `.trd`/`.dsk` (disk images), `.scr` (screens)
4. **Presents the storage** to the Spectrum as a file browser (DivMMC), as a TR-DOS disk (FDC emulation), or as a tape (EAR input emulation)
5. **Provides fast loading** — seconds instead of minutes for software

The most popular approach is **DivMMC** — an expansion port adapter with microSD slot, presenting a file browser that loads any image format. For minimalists, **ZXMMC** gives direct Z80-to-SD access. For full Beta 128 compatibility, an [MCU-based FDC emulator](mcu_fdc_vg93.md) on SD storage is the answer.

---

## References

- [SD Physical Layer Simplified Specification](https://www.sdcard.org/downloads/) — SD Association, free download
- [FatFs by Elm-Chan](https://elm-chan.org/fsw/ff/00index_e.html) — the standard FAT library for MCU (elm-chan.org)
- [DivMMC documentation](https://github.com/westonrf/divide-ide) — community wiki and ESXOS documentation
- [ZXMMC project](https://github.com/Zaxos/ZXMMC) — Zaxos's original design and community developments
- [TAP file format specification](https://worldofspectrum.org/) — on the World of Spectrum archive
- **TZX file format specification** — by Tomaz Kac, comprehensive
- **SNA and Z80 file format specifications** — widely documented
- [RP2040 SPI examples](https://www.raspberrypi.com/documentation/microcontrollers/) — in the RP2040 SDK
- **Arduino SD library** — for simpler projects

## Cross-References

- [FDC on MCU](mcu_fdc_vg93.md) — using SD cards with the VG93 emulator for TR-DOS compatibility
- [Video adapter on MCU](mcu_video_adapter.md) — for screenshot capture to SD
- [Keyboard on MCU](mcu_keyboard.md) — often combined with SD in a multi-function adapter
- [N-Go](n_go.md) — a complete MCU-based Spectrum including SD storage
- [ZX-Uno](../fpga/zx_uno_core.md) — FPGA Spectrum with integrated DivMMC
- [MiSTer](../fpga/mist_mister_core.md) — FPGA framework with integrated SD support
- [MCU design patterns](mcu_design_patterns.md) — general SPI and bus interfacing techniques
