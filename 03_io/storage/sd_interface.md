# SD Card Interfaces on the ZX Spectrum

**Scope:** A hardware-level comparison of every significant **SD card** interface that brought Secure Digital storage to the ZX Spectrum family and its clones — the **DivMMC**, **ZXMMC**, the **ZX Spectrum Next** internal slots, and the **Z-Controller** — together with the **SPI-mode SD protocol** that all of them must implement. The IDE/ATA parallel protocol and its host adapters are covered in the sibling article [ide_interface.md](ide_interface.md); both families share the same destination (a FAT volume of Spectrum software) but speak entirely different device protocols.

**Audience:** Hardware-level emulator authors modelling the DivMMC's SPI engine, demoscene coders writing direct-to-card loaders, retro-hardware builders choosing between a DivMMC and a bare ZXMMC kit, and anyone curious how a 1982 computer reads a 32 GB MicroSD card in 2024.

**Prerequisites:** The [IDE interface article](ide_interface.md) covers the sibling protocol family; the [overview article](hdd_overview.md) situates SD in the storage story. The [DivIDE/DivMMC article](divide_divmmc.md) covers the firmware that runs on the dominant SD interface.

**Depth:** Deep. The SD-SPI command set, the bit-bang programming model, port maps, and worked read sequences. References to the OS articles where the filesystem layer takes over.

---

## §1. What an SD Interface Is

### 1.1 SD cards and their two protocols

An **SD card** (Secure Digital, 1999) is a flash-storage device with a 9-pin interface. From the factory it speaks one of two protocols with a host:

- **SD mode** — the proprietary, high-speed, 4-bit-parallel protocol used by cameras, phones, and embedded Linux. Complex to drive; requires a dedicated SD-host controller.
- **SPI mode** — a subset of the SD command set exposed through a standard **Serial Peripheral Interface** (4 wires: CS, SCK, MOSI, MISO). Much slower than SD mode, but trivial to drive from any microcontroller — or from a Z80.

Every Spectrum SD interface uses **SPI mode**. The reason is purely the host: the Z80 has no parallel SD-host controller, and bit-banging SD mode's 4-bit CRC-protected bus in software is infeasible at any useful speed. SPI mode sacrifices throughput (a typical Spectrum SD interface manages **50–200 KB/s**, versus SD mode's tens of MB/s) but gains universality — any SD, SDHC, or SDXC card ever made supports SPI mode as a fallback.

### 1.2 Why SD displaced IDE

The case for SD over IDE on the Spectrum is made in [hdd_overview.md §2.3](hdd_overview.md) and [divide_divmmc.md §3.2](divide_divmmc.md): smaller cards, lower power, a medium that is still manufactured. The protocol difference reinforces it. An IDE interface needs a 40-pin connector and a 16-bit-to-8-bit adaptation circuit; an SD-SPI interface needs only **four signal lines** plus power. The whole host adapter fits in a tiny CPLD or even discrete logic, which is why the DivMMC board is so much smaller than the DivIDE.

The trade-off is software complexity: the SD-SPI command set is larger than the IDE register file, and the init sequence is fiddly. But this complexity lives in firmware (ESXDOS) and is written once; the user never sees it.

### 1.3 SD, SDHC, SDXC — what the firmware sees

The three SD capacity families differ mainly in addressing:

| Family | Capacity | Addressing | Spectrum support |
|---|---|---|---|
| **SDSC** | up to 2 GB | Byte-limited (24-bit block) | All firmware |
| **SDHC** | 4–32 GB | Block-limited (32-bit block) | Modern ESXDOS (0.85+) |
| **SDXC** | 64 GB–2 TB | Block-limited + exFAT by default | Block access works; reformat to FAT32 |

From the SPI protocol's perspective, SDSC and SDHC differ only in whether the block-address arguments are byte offsets or block numbers — a distinction handled by one bit in the OCR (Operating Conditions Register), read during init. SDXC uses the same block addressing as SDHC but ships formatted as exFAT, which ESXDOS cannot read; the user reformats it as FAT32 on a PC first. The upshot is that **any MicroSD card works on a DivMMC**, provided it is FAT-formatted, up to the FAT32 limit of 2 TB.

The byte-vs-block distinction and the init sequence are covered in §3.

## §2. Generic Block Diagram

Every Spectrum SD interface is built from the same handful of components:

```
                      +-------------------------------------------------+
   Spectrum bus ----->| Address decoder + IOREQ/M1/+MWR/+MRD glue logic |
                      +-------------------------------------------------+
                                          |
                  +-----------------------+-----------------------+
                  |                                               |
          +---------------+                               +---------------+
          | ROM / Flash   |<-- banked into Spectrum RAM   | SPI bridge    |
          | (firmware:    |    space via paging           | (CPLD or      |
          |  ESXDOS)      |                               |  discrete)    |
          +---------------+                               +---------------+
                                                                  |
   SD card <==== 9-pin socket ====> +-----------------------------------+
                                     | CS   SCK   MOSI   MISO   (+V, GND)|
                                     | 4 signal lines + power            |
                                     +-----------------------------------+
```

The **address decoder** responds to the interface's I/O footprint (a few ports) and to the memory-mapped ROM window.

The **ROM/Flash** holds the firmware — ESXDOS on the DivMMC, NextZXOS on the Next. It is banked in exactly as on the DivIDE; see [divide_divmmc.md §4](divide_divmmc.md).

The **SPI bridge** is the SD-specific component. It exposes a small register file (typically 1–3 ports) through which the Z80 bit-bangs the four SPI lines: it writes a byte serially to MOSI by toggling SCK eight times, and simultaneously shifts in eight bits from MISO. On the DivMMC this is a dedicated CPLD; on simpler interfaces it is discrete flip-flops and a shift register. Some interfaces (the ZX Spectrum Next) include a hardware SPI engine that shifts a whole byte in one port write, removing the bit-bang loop.

The **connector** is a 9-pin SD socket (full-size SD) or an 8-pin MicroSD socket, carrying the four SPI signals plus 3.3V power and ground.

## §3. The SD-SPI Protocol

### 3.1 The four wires

SPI uses four signals:

| Signal | Direction | Purpose |
|---|---|---|
| **CS** (Chip Select) | Host → card | Active-low; asserted to select the card for a command |
| **SCK** (Serial Clock) | Host → card | Clock; the host shifts data on each edge |
| **MOSI** (Master Out, Slave In) | Host → card | Data from host to card |
| **MISO** (Master In, Slave Out) | Card → host | Data from card to host |

The host (the Z80, via the SPI bridge) is always the SPI master: it generates SCK and drives CS. The card is the slave. Every transfer is full-duplex in principle (a byte goes out on MOSI while a byte comes in on MISO), but in SD-SPI practice the host usually sends a command and then clocks dummy bytes to read the response.

### 3.2 The command frame

Every SD-SPI command is a **6-byte frame**:

| Byte | Content |
|---|---|
| 0 | `0b01CCCCCC` — the command index `CCCCCC` preceded by the bits `01` |
| 1–4 | The 32-bit big-endian argument |
| 5 | 7-bit CRC + stop bit (`1`) |

In SPI mode the CRC is **not checked** after the init handshake (CMD0 and CMD8 require a valid CRC; thereafter the card accepts CRC=0 with the stop bit set). Most drivers send a fixed CRC of `0x95` for CMD0, `0x87` for CMD8, and `0x01` (just the stop bit, CRC field zero) for everything else.

### 3.3 The init handshake

The SD-SPI init sequence is the protocol's most error-prone part. A correct init, in order:

1. **Power-up delay.** After power-on, hold CS high and clock at least 74 dummy SCK cycles (send 10 bytes of `0xFF` with CS deasserted). This lets the card's internal state machine stabilise.
2. **CMD0 (GO_IDLE_STATE)**, argument `0x00000000`, CRC `0x95`, CS asserted. The card should respond with R1 = `0x01` (idle state). This command also switches the card from SD mode to SPI mode — the card latches SPI mode the first time it sees CS low during a command.
3. **CMD8 (SEND_IF_COND)**, argument `0x000001AA` (voltage = 2.7–3.6V, check pattern `0xAA`), CRC `0x87`. An SDHC/SDXC card responds with R7 = the argument echoed back. An older SDSC card (or a MMC) responds with `0x05` (idle + illegal command), which the driver interprets as "this is an SDSC card".
4. **CMD55 + ACMD41 (SD_SEND_OP_COND)**, repeated until the idle bit clears. CMD55 (`APP_CMD`) tells the card the next command is application-specific; ACMD41 (`SD_SEND_OP_COND`, argument `0x40000000` on SDHC to request block addressing) starts the card's internal init. Loop, sending CMD55 then ACMD41 and reading R1, until R1 = `0x00` (no idle bit). This can take hundreds of milliseconds.
5. **CMD58 (READ_OCR)**, argument `0x00000000`. The response R3 is R1 (`0x00`) followed by the 32-bit OCR. Bit 30 of the OCR (`CCS`, Card Capacity Status) indicates block addressing: set means SDHC/SDXC (block-addressed), clear means SDSC (byte-addressed).

After CMD58, the card is ready for data access. The whole sequence is run by ESXDOS at boot; the programmer calling ESXDOS never sees it.

### 3.4 The response types

SD-SPI defines several response formats:

| Type | Length | Used by |
|---|---|---|
| **R1** | 1 byte | Most commands (status bits: idle, erase reset, illegal command, CRC error, etc.) |
| **R1b** | 1 byte + busy | Commands that need a card busy period (e.g. STOP_TRANSMISSION) |
| **R2** | 2 bytes | SEND_STATUS (extended status) |
| **R3** | 5 bytes (R1 + 32-bit OCR) | READ_OCR |
| **R7** | 5 bytes (R1 + 32-bit version + check pattern) | SEND_IF_COND |

The driver reads the appropriate number of bytes, clocking dummies out on MOSI, until it has the full response. The card may insert `0xFF` filler bytes before the response, so the driver polls MISO for a byte whose top bit is 0 (a real R1 response never has bit 7 set; `0xFF` means "not ready yet").

### 3.5 Data transfer: READ_SINGLE_BLOCK and WRITE_BLOCK

Once the card is initialised, all storage access goes through two commands:

- **CMD17 (READ_SINGLE_BLOCK)**, argument = block address. The card responds with R1 (`0x00`), then a **data-start token** (`0xFE`), then exactly 512 bytes of data, then a 2-byte CRC. The host clocks 512+3 bytes total after the R1.
- **CMD24 (WRITE_BLOCK)**, argument = block address. The host sends R1-expected, then a **data-start token** (`0xFE`), then 512 bytes of data, then a 2-byte CRC. The card responds with a **data-response byte** (`0x_E5`, where the middle nibble `010` means "accepted"), then holds MISO low (busy) until the write completes.

For SDSC cards, the argument is a **byte address** (so block `N` is at argument `N × 512`). For SDHC/SDXC cards, the argument is a **block number** directly. The driver checks the CCS bit from CMD58 to decide which convention to use.

Multi-block transfers (CMD18 / CMD25) read or write a stream of blocks until a STOP_TRANSMISSION command (CMD12) is sent. These are faster per block than single-block transfers because they avoid per-command overhead, but ESXDOS predominantly uses single-block access because the FAT layer reads one sector at a time.

### 3.6 A worked read (block N into a buffer)

The high-level sequence to read one 512-byte block into a Z80 buffer:

1. Assert **CS low**.
2. Send **CMD17** with the block address (byte address for SDSC, block number for SDHC), CSRC `0x01`.
3. Read bytes from MISO until one has its top bit clear — that is the **R1** response. Confirm it is `0x00`.
4. Read bytes until one equals `0xFE` — that is the **data-start token**.
5. Read **512 bytes** into the buffer.
6. Read **2 bytes** (the CRC) and discard.
7. Deassert **CS high** (and clock one dummy byte, which some cards need to release MISO).

Each "send" and "read" is an 8-bit SPI transfer: the host writes the byte to the SPI data port (which shifts it out on MOSI while shifting in MISO), then reads the port to recover the byte that came in. On a bit-bang interface this is a loop of 8 SCK toggles; on the Next's hardware SPI it is a single port write and read.

### 3.7 A Z80 bit-bang SPI byte (sketch)

On a simple SD interface, the four SPI lines are individual bits of a single I/O port — say, bit 0 = CS, bit 1 = SCK, bit 2 = MOSI, bit 7 = MISO. Sending and receiving one byte looks like:

```asm
; B = byte to send on MOSI; returns received byte in C
spi_xfer:
        ld      c, 0               ; received byte accumulator
        ld      a, 8               ; 8 bits
spi_loop:
        ; shift next MOSI bit into bit 2 of the port
        rl      b                  ; MSB out of B into carry
        ld      d, a
        ld      a, (port_shadow)   ; cached port image, CS low already set
        res     1, a               ; SCK low
        rl      a                  ; carry (MOSI bit) into bit 2  -- (simplified)
        out     (#EB), a           ; write port: CS=0, SCK=0, MOSI=bit
        set     1, a               ; SCK high -- card latches MOSI on this edge
        out     (#EB), a
        ; read MISO on the rising edge
        in      a, (#EB)
        rl      a                  ; MISO (bit 7) into carry
        rl      c                  ; shift into accumulator
        ld      a, d
        dec     a
        jr      nz, spi_loop
        ret
```

This is a sketch — the exact port bits and the polarity (which SCK edge latches) vary by interface — but it captures the essence: 8 iterations per byte, each driving one MOSI bit out and reading one MISO bit in. At ~3.5 MHz with ~20 T-states per bit, a bit-bang interface caps out around **20 KB/s** for the bit-bang itself; a hardware SPI engine (the Next) reaches the full card speed of **200+ KB/s**.

## §4. Port Maps Compared

Every SD interface exposes the SPI bridge through a small set of I/O ports. The table summarises the four families; §5 gives the per-interface detail.

| Interface | SPI footprint | Bridge type | Host clones | Native DOS |
|---|---|---|---|---|
| **DivMMC** | `#E3`–`#E7` (DivIDE-compatible) | CPLD bit-bang | DivMMC, all clones | ESXDOS |
| **ZXMMC** | `#1B`/`#3B`/`#5B`/`#7B` family | Discrete bit-bang | ZXMMC (classic ZX) | Custom / FAT |
| **ZX Spectrum Next** | NextReg + dedicated SPI port | Hardware SPI engine | Next | NextZXOS |
| **Z-Controller (SD half)** | ATM/ZC port block | CPLD bit-bang + RTC | ATM Turbo, Pentagon | FAT (firmware) |

The most important row is the first: because the DivMMC reuses the DivIDE's `#E3`–`#E7` footprint, the same ESXDOS firmware drives both. The other three interfaces each have their own port block and their own driver.

## §5. Interface-by-Interface

### 5.1 The DivMMC

The DivMMC is covered in depth in [divide_divmmc.md](divide_divmmc.md). From the SPI-protocol perspective, the key facts are:

- It reuses the DivIDE's `#E3`–`#E7` port block, so the ESXDOS firmware that already drives the DivIDE's IDE port can be extended with an SD-SPI driver at the same addresses.
- The SPI bridge is a small CPLD that presents the four SPI lines (CS, SCK, MOSI, MISO) through a data port and a control port within the `#E3`–`#E7` block. A bit-bang loop in firmware drives SCK eight times per byte.
- The card socket is a full-size SD or MicroSD socket (depending on revision), wired for SPI mode (CS, SCK, MOSI, MISO, +3.3V, GND). Level shifting between the Spectrum's 5V logic and the card's 3.3V is handled on board.

The DivMMC is the dominant SD interface and the one emulator authors must model. Fuse, ZEsarUX, CSpect, and UnrealSpeccy all implement its port block.

### 5.2 The ZXMMC

The **ZXMMC** (early 2010s, by a Polish designer) is an earlier, simpler SD interface for the classic ZX bus. It predates the DivMMC and never achieved the DivMMC's ubiquity, but it is historically important as one of the first SPI SD interfaces available.

Architecturally it is the minimal SD interface: a 9-pin SD socket, a small address decoder, and a discrete shift-register or flip-flop circuit that presents the four SPI lines as bits of an I/O port in the `#1B`/`#3B`/`#5B`/`#7B` family. There is no firmware ROM — the ZXMMC is a "dumb" SPI bridge that the host software must drive directly.

Because it has no firmware and no standard DOS, the ZXMMC appeals mainly to hardware hackers who want to write their own SD driver from scratch. Its software library is small. For a new user, the DivMMC is universally the better choice; the ZXMMC matters mainly to emulator authors modelling specific clone configurations and to owners of original ZXMMC hardware.

### 5.3 The ZX Spectrum Next SD slots

The **ZX Spectrum Next** (2017) integrates SD storage into the machine itself. It provides **two MicroSD slots** — a "primary" slot (drive `C:`) holding the firmware and core files, and a "secondary" slot (drive `D:`) for user software — driven by NextZXOS, an ESXDOS derivative.

The Next's SD interface is the most sophisticated on the Spectrum. Unlike the DivMMC's bit-bang bridge, the Next includes a **hardware SPI engine**: the programmer writes a byte to an SPI data port and the hardware shifts it out (and reads in) at full clock speed, with no Z80 bit-bang loop. This raises the throughput ceiling to **200+ KB/s**, limited mainly by the card itself rather than the host.

The two slots are independent: software can read from one while writing to the other, and the firmware can boot from the primary while the secondary is hot-swapped. See [nextzxos.md](../04_operating_systems/nextzxos.md) for the Next-specific SD API and the layer-2 / sprite / tilemap integration.

### 5.4 The Z-Controller (SD half)

The **Z-Controller** (late 2000s, ATM team) is a combined **IDE + SD + RTC** expansion for the ATM Turbo and Pentagon. Its IDE half is covered in [ide_interface.md §5.4](ide_interface.md); the SD half presents a second SPI bridge alongside the IDE port block, sharing the same address-decoding logic.

The Z-Controller's significance is that it was the first interface to offer **both** IDE and SD on a single board, letting the user choose the medium per task. Its SD driver uses the same bit-bang approach as the DivMMC, through a port within the Z-Controller's footprint. The included RTC (real-time clock) provides file timestamps, which the DivMMC achieves through an optional on-board RTC instead.

The Z-Controller is mainly relevant to owners of ATM Turbo hardware and to emulator authors modelling the ATM Turbo specifically. For everyone else, the DivMMC family covers the SD use case.

## §6. Performance and Card Compatibility

### 6.1 Throughput

Real-world SD throughput on the Spectrum is dominated by the host, not the card. The four families break down roughly as follows:

| Interface | Bit rate (SCK) | Effective read rate | Limiting factor |
|---|---|---|---|
| **ZXMMC** (discrete bit-bang) | ~100–200 kHz | ~10–20 KB/s | Z80 loop overhead |
| **DivMMC** (CPLD bit-bang) | ~250–500 kHz | ~30–80 KB/s | Z80 loop overhead |
| **Z-Controller SD** (CPLD bit-bang) | ~250–500 kHz | ~30–80 KB/s | Z80 loop overhead |
| **ZX Spectrum Next** (hardware SPI) | up to 14 MHz | ~150–250 KB/s | Card + bus contention |

The bit-bang interfaces are slow because each SPI bit costs roughly 15–25 T-states of Z80 time: read the port image, set up the MOSI bit, toggle SCK low, write, toggle SCK high, write, read MISO, shift. A 3.5 MHz Z80 executing ~20 T-states per bit does ~175 kbit/s of SPI clock, which is ~20 KB/s of payload after protocol overhead.

The Next's hardware SPI engine removes the per-bit loop: one port write clocks a full byte at up to 14 MHz, so the Z80 is free to shuttle data between RAM and the SPI port at memory speed. This is why the Next reaches an order of magnitude higher throughput.

In practice, none of these rates is a problem for Spectrum software. Even the slowest interface loads a 48 KB snapshot in under five seconds, and the dominant cost is the FAT lookup overhead, not the raw transfer.

### 6.2 The 3.3V issue

SD cards run at **3.3V**; classic Spectrum logic runs at **5V**. Driving a 3.3V card's inputs directly from 5V logic can damage the card, and reading a 3.3V MISO into a 5V input is marginal. Every well-designed SD interface therefore includes **level shifting** — either a dedicated level-shifter chip, or a simple resistor divider, or (on the DivMMC and Next) a CPLD/FPGA that runs its SD-facing I/O at 3.3V natively.

A homebrew SD interface that omits level shifting may work with some cards and destroy others. This is the single most common cause of "the card works for a week then dies" reports. Commercial interfaces (DivMMC, ZXMMC, Z-Controller, the Next) all handle this correctly.

### 6.3 Card compatibility

Modern ESXDOS is compatible with virtually every SD, SDHC, and SDXC card on the market. The known problem classes are:

- **"A1"/"A2" app-performance cards** sometimes have long busy periods after writes that exceed the DivMMC firmware's timeout. A plain "Class 10" or unbranded card is often more reliable than a premium phone card.
- **Counterfeit cards** (rebadged small chips sold as large cards) report a bogus capacity and corrupt data past their real size. Always buy from a reputable vendor and test with `h2testw` or `f3` before trusting a card with irreplaceable data.
- **Very old SDSC cards** (under 1 GB) may not negotiate SPI mode correctly with modern firmware. They are also scarce in 2024. A new 4–32 GB MicroSD is the safe default.

As a rule of thumb: a 4–32 GB MicroSD from a recognised brand (SanDisk, Kingston, Samsung), FAT32-formatted, works on every DivMMC and Next without issue.

### 6.4 Power consumption

An SD card in SPI mode draws **~1 mA idle and ~25 mA peak during reads**, with brief ~50 mA spikes during writes. This is well within the Spectrum's +5V rail budget even on the original 48K, which is why the DivMMC can be powered entirely from the edge connector with no external supply. The ZX Spectrum Next's SD slots draw from the Next's own regulated rail.

## §7. Cross-references and License

### 7.1 Within this sub-section

| Article | Covers |
|---|---|
| [hdd_overview.md](hdd_overview.md) | The top-level overview; where SD sits in the storage story |
| [ide_interface.md](ide_interface.md) | The sibling IDE/ATA protocol family and its host adapters |
| [divide_divmmc.md](divide_divmmc.md) | The DivMMC hardware in depth; the ESXDOS firmware integration |
| [hdd_partitioning.md](hdd_partitioning.md) | The MBR and FAT structure on the SD card |
| [hdf_mgt_formats.md](hdf_mgt_formats.md) | The `.IMG` image format that captures an SD volume for emulation |

### 7.2 Related articles elsewhere

| Article | Relationship |
|---|---|
| [esxdos.md](../04_operating_systems/esxdos.md) | The DOS that drives the DivMMC; the SD-SPI driver lives here |
| [nextzxos.md](../04_operating_systems/nextzxos.md) | The Next's ESXDOS derivative; the dual-slot SD API |
| [evo_os.md](../04_operating_systems/evo_os.md) | The ZX Evolution BIOS, which includes Z-Controller-compatible SD |
| [io_port_decoding.md](../05_development/03_memory_and_io/io_port_decoding.md) | How I/O ports are decoded; the foundation for the port maps here |

### 7.3 License

This article is licensed under [CC BY-SA 4.0](../LICENSE). The SD-SPI command set and response formats described in §3 are derived from the public **SD Physical Layer Simplified Specification** published by the SD Association, used here for documentation purposes.
