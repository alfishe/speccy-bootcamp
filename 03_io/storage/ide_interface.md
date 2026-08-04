[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# IDE Interfaces on the ZX Spectrum

**Scope:** A hardware-level comparison of every significant **IDE (Integrated Drive Electronics)** interface that brought parallel-ATA hard disks and CompactFlash cards to the ZX Spectrum family and its clones — the **DivIDE**, **Nemo IDE**, **KAY IDE**, the **ATM Turbo / Z-Controller IDE**, and the **SMUC** ISA bridge.

This article is the **hardware reference** for the IDE era: port maps, banking schemes, cable pinouts, and the register-level protocol the Z80 uses to talk to an IDE device. It does not cover the SD-card interfaces (those are in [sd_interface.md](sd_interface.md)), nor the DOS firmware in depth (that is in [divide_divmmc.md](divide_divmmc.md) and [esxdos.md](../../04_operating_systems/esxdos.md)).

**Audience:** Hardware-level emulator authors modeling the DivIDE or SMUC port blocks, demoscene coders writing direct-to-disk loaders that bypass ESXDOS, retro-hardware builders adapting CompactFlash to a clone, and anyone curious why the Spectrum speaks a 16-bit PC protocol through an 8-bit 1982 bus.

**Prerequisites:** Familiarity with [I/O port decoding](../../05_development/03_memory_and_io/io_port_decoding.md) and the general [memory-and-I/O model](../../05_development/03_memory_and_io/memory_and_io_48k.md) of the Spectrum. The [overview article](hdd_overview.md) situates the IDE era in the wider storage story.

**Depth:** Deep. Port maps, banking registers, the ATA command set, and worked read/write sequences. References to the OS articles where the filesystem layer takes over.

---

## §1. What an IDE Interface Is

### 1.1 IDE, ATA, PATA — three names for one protocol

**IDE** (Integrated Drive Electronics), **ATA** (AT Attachment), and **PATA** (Parallel ATA, a retronym coined after Serial ATA appeared) refer to the same thing: the 16-bit parallel storage bus that IBM introduced with the PC/AT in 1984 and that dominated PC storage from the late 1980s until SATA displaced it around 2005. On the Spectrum, the terms are used interchangeably; this article uses "IDE" because that is the word the Spectrum community settled on.

The defining property of IDE is that **the controller lives on the drive itself**, not on a host bus. A "host adapter" for IDE is therefore almost trivial — it is little more than a buffer and an address decoder that maps the IDE register file into the host's I/O space. This is exactly why IDE reached the Spectrum at all: a WD1793 floppy controller is a complex state machine that needs careful timing, but an IDE interface is just a window onto a register file that any 8-bit CPU can drive.

### 1.2 The 16-bit-on-8-bit problem

The Z80 is an 8-bit processor; IDE is a 16-bit bus. Every IDE interface on the Spectrum solves this mismatch in one of two ways:

- **Paired 8-bit ports.** The interface exposes two host ports per IDE register — one for the low byte, one for the high byte. Reading or writing a 16-bit IDE word costs two I/O cycles. The ATM Turbo IDE and most clone interfaces use this scheme.
- **A single 8-bit port with a high/low latch.** One port holds a byte; a second access to the same or a neighbouring port commits the pair as a 16-bit word. The DivIDE uses a variant of this.

Either way, the throughput ceiling is set by the Z80's I/O bandwidth, not by the IDE device. A well-coded loop reading the IDE data register on a 3.5 MHz Z80 manages roughly **200–400 KB/s**; with contention and firmware overhead this drops to **100–250 KB/s** in practice. That is still an order of magnitude faster than a floppy.

### 1.3 CompactFlash as a drop-in

Most Spectrum "IDE" interfaces in practice never touch a spinning hard disk. A **CompactFlash** card, from CF-I onwards, implements a "True IDE" mode in which its 50-pin socket behaves exactly like a 40-pin IDE device. A passive adapter (a small PCB that reroutes the CF pinout to a 40-pin header) turns any CF card into an IDE drive. CF draws far less power than a hard disk, fits the Spectrum's weak +5V rail, and offers a write-protect switch — which is why CF became the storage medium of choice for the DivIDE and its contemporaries.

The protocol layer does not know or care whether the device behind the connector is a hard disk or a CF card. This article therefore uses "IDE device" to mean either.

## §2. Generic Block Diagram

Despite their differences, every Spectrum IDE interface is built from the same five components. Understanding the generic diagram makes the per-interface variations in §5 easy to follow.

```
                      +-------------------------------------------------+
   Spectrum bus ----->| Address decoder + IOREQ/M1/+MWR/+MRD glue logic |
                      +-------------------------------------------------+
                                          |
                  +-----------------------+-----------------------+
                  |                                               |
          +---------------+                               +---------------+
          | ROM / Flash   |<-- banked into Spectrum RAM   | Control reg   |
          | (firmware:    |    space via paging (8/16 KB) | (ROM page,    |
          |  ESXDOS, etc.)|                               |  write-protect|
          +---------------+                               |  IDE reset)   |
                                                          +---------------+
                                                                  |
   IDE device <==== 40-pin cable ====> +-----------------------------------+
                                        | IDE register file window         |
                                        | (Data, Error, Features, SecCnt,  |
                                        |  LBA/Cyl, Head, Status, Command) |
                                        | 16-bit bus with 8/16-bit adapter |
                                        +-----------------------------------+
```

**The address decoder** responds to a small block of I/O ports (the interface's "footprint") and, on some interfaces, to a memory-mapped window for the ROM. Partial decoding is normal: the DivIDE checks only a handful of address lines, so its ports have many mirrors.

**The ROM/Flash** holds the firmware — ESXDOS on the DivIDE, the ATM Turbo's system ROM, the SMUC's monitor. It is banked into the Spectrum's address space because the firmware (16–64 KB) is larger than the 8–16 KB window the Spectrum can spare. The banking register is part of the control register, below.

**The control register** selects the active ROM page, toggles write-protect (so a careless `OUT` cannot corrupt the firmware), and asserts the IDE `RESET` line. On the DivIDE this is port `#E7`.

**The IDE register window** is the heart of the interface. It maps a subset of the IDE device's register file (typically the eight "Command Block" registers) into a few host ports. The 8-bit/16-bit adaptation described in §1.2 happens here.

**The connector** is a standard 40-pin IDE header (or a 44-pin laptop IDE header that includes power, or a 50-pin CompactFlash socket). §4 covers the pinout.

## §3. Port Maps Compared

Every IDE interface occupies a distinct I/O footprint. The table below summarises the five families covered in this article; §5 gives the per-register breakdown for each.

| Interface | Primary footprint | Width | Host clones | Native DOS |
|---|---|---|---|---|
| **DivIDE** | `#E3`–`#E7` (+ `#A3`–`#A7` mirror) | 8-bit windowed | DivIDE, DivIDE clones, ZX Evolution (compat) | ESXDOS |
| **Nemo IDE** | Pentagon-specific (port-mapped) | 8-bit paired | Pentagon, Profi | Raw / IS-DOS |
| **KAY IDE** | KAY-1024 internal (`#08`–`#0F` family) | 8-bit paired | KAY-1024 | Raw / FAT |
| **ATM Turbo / Z-Controller IDE** | `#FF0F`–`#FFEF` (8 regs) | 8-bit paired | ATM Turbo, Sprinter, Z-Controller | ATM ROM / FAT |
| **SMUC** | `#D8BE` + `#F8BE`–`#FFBE` | 16-bit ISA | Scorpion, ZX Evolution | Custom / FAT |

### 3.1 Why the footprints differ

The footprints differ because each interface was designed independently, for different host machines, before any standardisation. The DivIDE chose `#E3`–`#E7` because those ports were largely unused on a 48K/128K Spectrum. The ATM Turbo used `#FF0F`–`#FFEF` to fit its existing port map. SMUC inherited the PC's `0x1F0`/`0x3F6` register layout because it bridges a real PC ISA bus.

The practical consequence is that **software written for one IDE interface does not run on another** without a driver abstraction. ESXDOS is that abstraction for the DivIDE family; the ATM Turbo and SMUC each have their own. Only the DivIDE family gained a large enough software library that emulator authors bother to model it.

### 3.2 The DivIDE port block in detail

The DivIDE is the most important interface, so its port block is documented here in full. The other interfaces' port blocks appear in §5.

| Port | Read | Write | Notes |
|---|---|---|---|
| `#E3` | IDE data (low byte) | IDE data (low byte) | 16-bit access via `#E3`/`#E5` pair |
| `#E5` | IDE data (high byte) | IDE data (high byte) | High half of 16-bit word |
| `#E7` | — (or status on some clones) | Control: ROM page, write-protect, IDE bank | Bit 0 = ROM page bit 0, etc. |

Bit 4 of `#E7` (on most firmware) controls the **write-protect** flag for the flash ROM; bit 5 selects between the two 16 KB "banks" of the IDE data buffer on some DivIDE revisions. The exact bit assignment varies by firmware version; consult the ESXDOS source for the authoritative mapping.

The remaining IDE registers (Error, Features, Sector Count, LBA, Status, Command) are accessed by first writing a 3-bit register-select value to a control sub-port, then reading or writing `#E3`/`#E5`. This is the "windowed" scheme described in §1.2.

## §4. The 40-pin IDE Connector Pinout

Every Spectrum IDE interface terminates in the same 40-pin (2×20) header defined by the ATA standard. This is the same connector found on every PC motherboard from the late 1980s to the mid-2000s, and the same pinout a passive CF adapter presents. A standard 40-wire ribbon cable (or, for higher speeds, an 80-wire cable with interleaved grounds) connects the interface to the device.

### 4.1 The signal set

The 40 pins break down as follows: 16 data lines (DD0–DD15), 3 address lines (DA0–DA2) that select an IDE register, the chip-select pair (`CS0`/`CS1`), the read/write strobes (`DIOR`/`DIOW`), a reset line, an interrupt line, a few status lines (IORDY, DMACK, DASP, PDIAG), two power-related pins, and grounds. Only the data, address, chip-select, and strobe lines matter to a Spectrum host adapter; the DMA and interrupt lines are unused because the Z80 drives everything in PIO mode.

### 4.2 Pin table (key signals)

| Pin | Signal | Pin | Signal | Notes |
|---|---|---|---|---|
| 1 | `/RESET` | 2 | GND | Reset is active-low |
| 3 | DD7 | 4 | DD8 | Data bus, high byte = pins 4,6,8,10,12,14,16,18 |
| 5 | DD6 | 6 | DD9 | Data bus, low byte = pins 3,5,7,9,11,13,15,17 |
| 7 | DD5 | 8 | DD10 | |
| 9 | DD4 | 10 | DD11 | |
| 11 | DD3 | 12 | DD12 | |
| 13 | DD2 | 14 | DD13 | |
| 15 | DD1 | 16 | DD14 | |
| 17 | DD0 | 18 | DD15 | |
| 23 | `/DIOW` | 25 | `/DIOR` | Write/Read strobes (active-low) |
| 27 | IORDY | 28 | `CSEL` | Cable select (usually tied to GND or NC) |
| 31 | `/INTRQ` | 33 | DA1 | Register address bit 1 |
| 35 | DA0 | 36 | DA2 | Register address bits 0 and 2 |
| 37 | `/CS0` | 38 | `/CS1` | Chip selects (Command vs Control block) |
| 39 | `/DASP` | 40 | GND | Device activity / slave present |

Pins 19, 22, 24, 26, 30, 40, and others are GND. Pin 20 is the **key pin** — it is often removed from the header and blocked on the cable to prevent reversed insertion. Pin 34 (`PDIAG`) and pin 32 (`DMACK`) are used only for master/slave negotiation and DMA, both irrelevant on the Spectrum.

### 4.3 Register selection

The IDE register file is selected by the combination of `CS0`, `CS1`, and `DA2:DA0`. The "Command Block" registers (the ones a PIO driver actually uses) live at `CS0=0, CS1=1`; the "Control Block" (alternate status and device control) lives at `CS0=1, CS1=0`. The host adapter's address decoder translates host I/O port addresses into these chip-select and DA-line combinations.

For example, on the ATM Turbo, host port `#FFEF` maps to `CS0=0, DA=111` — the Command/Status register. The full mapping is given in §5.4.

### 4.4 The 44-pin and CompactFlash variants

Two variants appear on Spectrum hardware:

- **44-pin laptop IDE** (2×22) adds four power pins and four reserved pins, eliminating the separate power connector. Some compact DivIDE clones use this to save space.
- **50-pin CompactFlash** in True IDE mode. The CF socket is physically different but the active signals are a superset of the 40-pin IDE pinout. A passive adapter maps CF to the 40-pin header; no active electronics are needed.

A Spectrum builder almost always ends up with a CF socket rather than a true hard-disk connector, because CF cards are still manufactured and draw little power.

## §5. Interface-by-Interface

### 5.1 The DivIDE

The **DivIDE** (Zeax, 2007) is the most widely used IDE interface on the Spectrum. It is a rear-edge expansion card containing:

- A 40-pin IDE header for a hard disk or CompactFlash (via passive adapter).
- A 27C512 EPROM socket holding up to 64 KB of firmware (ESXDOS occupies 8–16 KB; the rest holds optional TR-DOS compatibility firmware).
- A paging register that banks the ROM and an 8 KB data buffer into the Spectrum's address space.
- An **NMI button** wired to the Spectrum's `/NMI` line, which ESXDOS hooks to summon its main menu.
- An optional RTC (Dallas DS1307, I²C via bit-bang) for file timestamps.
- A pass-through edge connector for daisy-chaining further peripherals.

**Port map** (`#E3`–`#E7`, partially decoded):

| Port | Function |
|---|---|
| `#E3` | IDE data, low byte |
| `#E5` | IDE data, high byte |
| `#E7` | Control register (ROM page, write-protect, IDE bank) |

A mirror at `#A3`–`#A7` appears on some revisions. The non-data IDE registers (Error, Features, Sector Count, LBA, Status, Command) are reached by writing a register-select value into a sub-field of the control register, then strobing `#E3`/`#E5`.

**Memory paging.** The DivIDE banks its 64 KB ROM into the Spectrum in 16 KB slices mapped at `#0000`–`#3FFF` (overriding the Spectrum ROM). A "conmem" bit in the control register gates whether the DivIDE ROM is visible at all; a "mapram" bit swaps the ROM out for a RAM page after the firmware has booted, so that ESXDOS can keep resident data in the banked window. The paging scheme is the single most confusing aspect of DivIDE programming; see [divide_divmmc.md](divide_divmmc.md) for the worked sequence.

**TR-DOS image emulation.** The DivIDE's killer feature is **divman / divese**, a firmware layer that presents a `.TRD` file on the IDE/CF volume as if it were a floppy in a Beta 128 drive. Existing Soviet software that uses the standard TR-DOS hook codes runs unmodified, reading and writing a virtual floppy on the hard disk. This is the bridge that let the IDE era inherit the floppy era's software library wholesale.

### 5.2 The Nemo IDE

The **Nemo IDE** (early 2000s, named after Nemo / Eugene Shcherbakov, the Pentagon's designer) is the earliest mass-produced Spectrum IDE interface. It was designed for the Pentagon and Profi clones and predates the DivIDE by several years.

Architecturally it is simpler than the DivIDE: a 40-pin IDE header, a small PAL/GAL for address decoding, and no firmware ROM of its own. The host accesses the IDE registers through a set of port-mapped 8-bit registers using the **paired-port** scheme — two host ports per 16-bit IDE word, one for the low byte and one for the high byte.

The Nemo IDE was driven initially by raw block-access routines and later by **IS-DOS** (the Russian hierarchical filesystem), which was adapted to use it as its backing store. It never gained a FAT implementation or a large Western software library; its significance is historical — it proved that IDE was viable on the Spectrum and it seeded the Russian hard-disk culture that the DivIDE later inherited.

Because the Nemo IDE has no firmware ROM, it does not hook the NMI vector or provide a menu. The user boots IS-DOS (or a custom loader) from floppy and then addresses the hard disk through that software's driver.

### 5.3 The KAY IDE

The **KAY IDE** is the IDE controller built into the **KAY-1024** clone (a Russian Spectrum derivative with 1024 KB of RAM). It is functionally similar to the Nemo IDE — a port-mapped paired-byte IDE interface — but integrated onto the KAY's own motherboard rather than supplied as a separate expansion card.

The KAY IDE occupies a port footprint in the `#08`–`#0F` family, sharing the address-decoding logic with the KAY's other on-board peripherals. It is driven by the KAY's system ROM and by IS-DOS / custom loaders, in the same way the Nemo IDE is driven on the Pentagon.

The KAY IDE matters mainly to owners of original KAY hardware and to emulator authors modeling the KAY-1024 specifically. For everyone else, the DivIDE's port layout is the relevant one, because the KAY's software library is small and largely inaccessible outside the Russian scene.

### 5.4 The ATM Turbo / Z-Controller IDE

The **ATM Turbo** (1991, and its successors the ATM Turbo 2+ and the Sprinter) include an on-board IDE controller. The same controller design is also the IDE half of the **Z-Controller** — a combined IDE + SD + RTC expansion for the ATM Turbo and Pentagon designed by the ATM team in the late 2000s.

Unlike the DivIDE, the ATM IDE uses the **paired-port** scheme directly, mapping each IDE register to its own host port. The mapping is documented in the Black_Cat port table and reproduced here from [io_port_map.md](../../10_references/io_port_map.md):

| Host port | Read | Write | IDE register |
|---|---|---|---|
| `#FE0F` / `#FF0F` | IDEdata-Lo/Hi | IDEdata-Lo/Hi | Data register (bit `A` selects low/high byte) |
| `#FF2F` | IDEerror | IDEparam (Features) | Error / Features |
| `#FF4F` | IDEsect | IDEsect | Sector Count |
| `#FF6F` | IDEstartsect | IDEstartsect | Sector Number / LBA low |
| `#FF8F` | IDEcyl-Lo | IDEcyl-Lo | Cylinder Low / LBA mid |
| `#FFAF` | IDEcyl-Hi | IDEcyl-Hi | Cylinder High / LBA high |
| `#FFCF` | IDEdevice | IDEhead | Drive/Head / LBA high + LBA bit |
| `#FFEF` | IDEstatus | IDEcomnd | Status (R) / Command (W) |

The address bit `A` in `#FE0F`/`#FF0F` selects which half of the 16-bit data word is transferred, giving the same two-cycle 8-bit-paired access as the other interfaces.

The ATM IDE is driven by the ATM Turbo's system ROM and by the ATM's native DOS (an ATM-specific variant). It supports both CHS (Cylinder/Head/Sector) and LBA addressing; modern CF cards are addressed in LBA. The Z-Controller adds an SD-card slot on the same board, covered in [sd_interface.md](sd_interface.md).

### 5.5 The SMUC

The **SMUC** (Scorpion & MOA Universal Controller, 2007) is a different kind of interface entirely. Rather than presenting a custom IDE port block, it **bridges a real PC ISA bus** onto the Scorpion (and later the ZX Evolution), letting the Spectrum drive actual PC ISA expansion cards — including ISA IDE controllers, ISA network cards (NE2000), and ISA RTC chips.

Because the SMUC exposes the PC's ISA IDE register layout directly, its IDE ports follow the PC convention. From [io_port_map.md](../../10_references/io_port_map.md):

| Host port | Function | Notes |
|---|---|---|
| `#D8BE` | IDE-Hi | High byte of 16-bit IDE data |
| `#F8BE`–`#FFBE` | IDE `#1Fx` / `#3F6` | The standard PC IDE register block |
| `#DFBA` | DS1685 RTC | Real-time clock |
| `#FFBA` | SYS | System control register |

The `#F8BE`–`#FFBE` range maps the PC's primary IDE controller registers (`0x1F0`–`0x1F7` data/error/count/sector/cyl-lo/cyl-hi/head/status, plus `0x3F6` device control) into the Spectrum's I/O space, with bits `CBA` of the address selecting the exact register. This is the same register layout a PC DOS driver would use, which is why SMUC firmware could reuse PC-style driver code with minimal adaptation.

The SMUC's significance is that it brought **PC peripherals** to the Spectrum world — most importantly the NE2000-compatible ISA network card, which enabled the ZX Evolution to speak TCP/IP. For pure storage, however, the SMUC's IDE is no faster than the DivIDE's, and its software library is smaller. Most users who wanted mass storage chose a DivIDE; the SMUC was the enthusiast's choice for networking.

The ZX Evolution (2010) includes a SMUC-compatible ISA bridge as part of its standard I/O, so ZX Evolution owners have SMUC IDE available without a separate expansion.

## §6. The IDE Programming Model

### 6.1 The Command Block register file

Every IDE device exposes eight "Command Block" registers, selected by `CS0=0, CS1=1` and `DA2:DA0`:

| DA2:DA0 | Read | Write | Name | Purpose |
|---|---|---|---|---|
| `000` | Data | Data | Data | 16-bit data FIFO; read/written 256 times per sector |
| `001` | Error | Features | Error/Features | Last error code (R) / command-specific parameter (W) |
| `010` | Sector Count | Sector Count | SecCnt | Number of sectors for the next command |
| `011` | Sector Number | Sector Number | LBAlo | CHS sector / LBA bits 0–7 |
| `100` | Cylinder Low | Cylinder Low | LBAmid | CHS cylinder low / LBA bits 8–15 |
| `101` | Cylinder High | Cylinder High | LBAhi | CHS cylinder high / LBA bits 16–23 |
| `110` | Drive/Head | Drive/Head | Head | Drive select + head / LBA bits 24–27 + LBA bit |
| `111` | Status | Command | Status/Cmd | Device status (R) / command opcode (W) |

An eighth "Control Block" register (`CS0=1, CS1=0`, `DA=110`) gives the **Alternate Status** (read) and **Device Control** (write) — most importantly a bit that issues a **software reset** and a bit that enables/disables interrupts. On the Spectrum interrupts from IDE are ignored, but the reset bit is used during initialisation.

### 6.2 The Status register

The Status register (DA=111, read) is polled before and during every transfer:

| Bit | Name | Meaning when set |
|---|---|---|
| 7 | BSY | Busy — device is executing a command; ignore all other bits |
| 6 | DRDY | Drive ready |
| 5 | DF | Device fault |
| 4 | DSC | Seek complete |
| 3 | DRQ | Data request — the data register is ready for a transfer |
| 2 | CORR | Correctable data error (data is still valid) |
| 1 | IDX | Index pulse (once per revolution) |
| 0 | ERR | Error — see the Error register |

The cardinal rule of IDE polling is: **wait until BSY clears, then check DRQ (or DRDY, depending on the command phase)**. A driver that polls DRQ without first confirming BSY=0 will read garbage.

### 6.3 LBA setup and the `READ SECTORS` command

Modern CF cards are addressed in **28-bit LBA** (Logical Block Addressing), which numbers sectors from 0 across the whole device. To read one sector at LBA `N`:

1. Poll the Status register until `BSY` clears.
2. Write the **Drive/Head** register: `0xE0 | ((N >> 24) & 0x0F)` — this selects drive 0, sets the LBA mode bit, and loads LBA bits 24–27.
3. Write **Sector Count** = 1.
4. Write **LBAlo** = `N & 0xFF`.
5. Write **LBAmid** = `(N >> 8) & 0xFF`.
6. Write **LBAhi** = `(N >> 16) & 0xFF`.
7. Write **Command** = `0x20` (`READ SECTORS`).
8. Poll Status until `BSY` clears and `DRQ` sets.
9. Read the **Data** register **256 times** (each read yields one 16-bit word, two 8-bit reads on the Spectrum), delivering a 512-byte sector into memory.
10. Poll Status once more to confirm `ERR` is clear.

The write path is identical but writes `0x30` (`WRITE SECTORS`) at step 7 and writes the 256 words into the Data register at step 9.

### 6.4 A worked DivIDE read loop (sketch)

The following Z80 sketch reads one sector from a DivIDE into a buffer, ignoring the register-select windowing for clarity:

```asm
;  HL = buffer address, DE:BC = 28-bit LBA (DE = high word)
;  Uses the DivIDE #E3/#E5 data pair and a hypothetical register-select port
read_sector:
        call    wait_not_busy      ; poll Status until BSY=0
        ld      a, 0xE0            ; LBA mode, drive 0
        or      d                  ; fold in LBA bits 24-27 (assume D=0)
        call    write_head         ; -> Drive/Head register
        ld      a, 1
        call    write_seccnt        ; Sector Count = 1
        ld      a, c
        call    write_lbalo        ; LBAlo = BC low byte
        ld      a, b
        call    write_lbamid       ; LBAmid
        ld      a, e
        call    write_lbahi        ; LBAhi
        ld      a, 0x20            ; READ SECTORS
        call    write_cmd
wait_drq:
        call    read_status
        and     0x88               ; BSY | DRQ
        jr      z, wait_drq        ; spin until DRQ
        bit     3, a
        jr      z, wait_drq
        ; transfer 256 words = 512 bytes
        ld      b, 0               ; 256 iterations
read_loop:
        in      a, (#E3)           ; low byte
        ld      (hl), a
        inc     hl
        in      a, (#E5)           ; high byte
        ld      (hl), a
        inc     hl
        djnz    read_loop
        ret
```

The `write_head`, `write_seccnt`, etc. helpers each push the register-select value and then the data byte through the control port. On the ATM Turbo these helpers collapse to a single `OUT (n), A` because each IDE register has its own host port. This is the chief programming difference between the windowed DivIDE and the paired-port interfaces.

In practice, every ESXDOS storage call goes through this sequence internally; application code calls `ESXDOS_OPEN` / `ESXDOS_READ` instead. The raw sequence matters only to firmware authors and demoscene coders who bypass the DOS for speed.

## §7. Common Issues and Modern SD Replacements

### 7.1 The 8.4 GB and 128 GB ceilings

Original ATA-1 defined a 28-bit LBA, capping addressable storage at **2²⁸ × 512 = 128 GB**. In practice, older CF cards and older IDE firmwares hit walls far earlier: many pre-2005 CF cards misbehave above **2 GB** (where FAT16 runs out), and the DivIDE firmware historically had bugs above **512 MB**. Modern ESXDOS versions handle large cards correctly, but a builder should test the specific CF card rather than assume.

ATA-6 introduced 48-bit LBA, but no Spectrum IDE interface or firmware supports it; the 28-bit ceiling is the practical limit, and it is never approached because nobody fills a CF card with Spectrum software.

### 7.2 Power and the weak +5V rail

The original 48K Spectrum's +5V rail is rated for roughly 700 mA, of which the machine itself consumes ~500 mA. A spinning IDE hard disk needs 500–1000 mA at spin-up — enough to crash the Spectrum. This is why real spinning hard disks were rare on the Spectrum and **CompactFlash became the norm**: a CF card draws 30–80 mA, well within budget. A +2A/+3 with its heftier power supply can drive a small laptop hard disk, but it is still inadvisable.

The lesson: use CompactFlash (or, on SD interfaces, SD cards), not spinning disks.

### 7.3 Cable and master/slave issues

A 40-wire IDE cable longer than ~45 cm suffers signal integrity problems. The Spectrum's expansion bus is slow enough that this is rarely an issue, but a flaky cable produces intermittent read errors that look like firmware bugs. Always use the shortest cable that reaches.

IDE devices have a master/slave jumper. A single device on the cable must be jumpered **Master** (or **Single**, if the device distinguishes). A CF card in True IDE mode is always a single device; if a second device is on the cable, the CF card may need to be Master and the other device Slave. Getting this wrong produces a "drive not present" error.

### 7.4 The modern replacement: SD

In 2024 the practical answer to "which IDE interface should I use?" is **none** — use an SD interface instead. The **DivMMC** ([sd_interface.md](sd_interface.md)) provides the same ESXDOS API and port layout as the DivIDE but with an SD card in place of the IDE/CF connector, drawing less power and using a medium that is still manufactured. DivIDE hardware is now mainly of interest to emulator authors (who must model its ports) and to owners of original DivIDE cards who prefer CompactFlash.

The one scenario that still favours IDE is the **ZX Evolution** and **Scorpion** with a SMUC bridge, where an ISA IDE card is part of a broader ISA peripheral stack. But even there, an SD card on the same machine is usually present and preferred.

## §8. Cross-references and License

### 8.1 Within this sub-section

| Article | Covers |
|---|---|
| [hdd_overview.md](hdd_overview.md) | The top-level overview this article drills into; the three storage generations |
| [divide_divmmc.md](divide_divmmc.md) | The DivIDE and DivMMC firmware side: ESXDOS, paging, dot commands, FAT |
| [sd_interface.md](sd_interface.md) | The SD-card interfaces that have largely replaced IDE in 2024 |
| [hdd_partitioning.md](hdd_partitioning.md) | How the IDE/SD volume is partitioned and formatted (FAT16/32, IS-DOS) |
| [hdf_mgt_formats.md](hdf_mgt_formats.md) | The `.HDF` and `.IMG` hard-disk image formats used by emulators |

### 8.2 Related articles elsewhere

| Article | Relationship |
|---|---|
| [io_port_map.md](../../10_references/io_port_map.md) | The master port table; the ATM IDE and SMUC port blocks are reproduced from here |
| [esxdos.md](../../04_operating_systems/esxdos.md) | The DOS that drives the DivIDE family; the firmware side of this hardware |
| [beta_disk_interface.md](beta_disk_interface.md) | The floppy interface whose `.TRD` images the DivIDE emulates |
| [trd_disk_format.md](trd_disk_format.md) | The TR-DOS logical format, as seen through the DivIDE's virtual-floppy layer |
| [evo_os.md](../../04_operating_systems/evo_os.md) | The ZX Evolution's BIOS, which includes a SMUC-compatible IDE bridge |
| [io_port_decoding.md](../../05_development/03_memory_and_io/io_port_decoding.md) | The partial-decoding theory behind the `#E3`–`#E7` footprints |

### 8.3 External references

- [ATA/ATAPI Command Set-2 (ACS-2)](https://www.t13.org/standards) — ANSI INCITS 482-2012, the successor to the original ATA/ATAPI-7 standard. Documents the IDE register file, `READ SECTORS`/`WRITE SECTORS` commands, and the LBA addressing scheme used by every Spectrum IDE interface.
- **CompactFlash Association CF Specification** — the public CF specification covering "True IDE Mode" that most Spectrum IDE interfaces actually use via a CF socket.
- [DivIDE documentation](https://github.com/westonrf/divide-ide) — the canonical hardware and firmware reference for the `#E3`–`#E7` port block and 8 KB RAM/ROM banking.
- [ZEsarUX source code](https://github.com/chernandezba/zesarux) — emulator implementation of the DivIDE port layout; useful for verifying edge cases in banking and interrupt behavior.
- **[zx-pk.ru](https://zx-pk.ru) DivIDE / Nemo IDE threads** — the primary discussion venue for Russian-language IDE hardware mods (KAY IDE, ATM Turbo IDE, SMUC ISA bridge).

### 8.4 License

This article is licensed under [CC BY-SA 4.0](../../README.md). The port-map data in §5.4 and §5.5 is derived from **Black_Cat's ZX Ports Full Table** (BC Info Guide #4, 2008), preserved in the [tslabs/zx-evo repository](https://github.com/tslabs/zx-evo), and used here for documentation purposes.
