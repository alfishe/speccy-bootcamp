[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# Spectrum Hard Disk and SD Storage: An Overview

**Scope:** A high-level introduction to **mass storage beyond the floppy disk** on the ZX Spectrum family and its clones — the **three generations** of storage technology (floppy, IDE hard disk, SD card), the **interface hardware** that brought each to the Spectrum, and the **file systems** (FAT16, FAT32, IS-DOS) that organized the data.

This article is the **top-level index** into the hard-disk / SD documentation. It does not duplicate the byte-level port maps or filesystem layouts covered in the dedicated articles; instead it places every interface side-by-side so the reader can see at a glance what each does, when it appeared, and why it mattered.

**Audience:** Anyone trying to understand the Spectrum's mass-storage ecosystem — emulator authors deciding which interfaces to model, demoscene coders choosing a storage target for a large release, retro-hardware buyers deciding between a DivIDE and a DivMMC, or new Spectrum users wondering why a 1982 computer has an SD card slot in 2024.

**Prerequisites:** A general familiarity with the Spectrum and its floppy subsystem helps. If the four floppy logical formats (TR-DOS, +3DOS, CP/M, MGT) are unfamiliar, read [disk_format_overview.md](disk_format_overview.md) first.

**Depth:** Medium. Comparison matrices, summary tables, and references to the deep articles. No port-level hardware details here — follow the cross-references.

---

## §1. Introduction

### 1.1 What "hard disk on a Spectrum" means

The unexpanded ZX Spectrum has no mass storage at all — only a cassette tape interface running at roughly 1500 baud. Adding a floppy controller gave the machine access to ~720–800 KB per disk, which was enormous by 1985 standards but cramped by the early 1990s. Software was growing: multi-disk games, demoscene megabytes, operating systems with GUIs, and the Russian *FidoNet* file-swapping culture all pushed against the floppy's ceiling.

"Hard disk on a Spectrum" therefore means **any interface that lets the machine address a storage device larger than a single floppy** — whether that device is a parallel-ATA spinning hard disk, a CompactFlash card, an SD card, or (in a few unusual clones) an ISA-bus PC peripheral. The Spectrum never shipped with such an interface built in; every hard-disk or SD solution is a **third-party expansion** that plugs into the rear-edge connector or a clone's internal bus.

Three distinct generations of mass storage reached the Spectrum, each defined by the physical medium it used:

1. **The floppy era (1984–1995)** — the baseline. Covered fully in the [floppy sub-section](disk_format_overview.md); this article treats it only as the starting point.

2. **The IDE era (2001–2013)** — hobbyist interfaces that wired a 40-pin PATA IDE connector (or a CompactFlash socket, which speaks the same protocol) to the Spectrum's I/O bus. The breakthrough product was the **DivIDE** (2007), but it was preceded by a decade of experimental IDE cards.

3. **The SD era (2013–present)** — interfaces that replaced the bulky IDE connector with a tiny SD-card slot using SPI mode. The **DivMMC** (2013) is the dominant product; nearly every real-hardware Spectrum user in 2024 owns one.

### 1.2 The unifying abstraction: FAT

Across all three generations, one thing converges: **the FAT file system**. Early IDE interfaces used ad-hoc formats or raw block access, but every modern interface — DivIDE with ESXDOS, DivMMC, ZXMMC, the ZX Spectrum Next's SD card — speaks **FAT16 or FAT32**. This is not a coincidence: FAT is simple enough to implement in a few kilobytes of Z80 code, universal enough that a modern PC can read the same card, and robust enough for daily use.

The practical consequence is that a single SD card, prepared on a modern PC, can be moved between a DivMMC, a ZXMMC, and a ZX Spectrum Next with no conversion. The same was never true of floppies, where TR-DOS, +3DOS, and MGT disks could not be read by each other's DOS.

The details of the FAT implementation, partition tables, and long-filename support are covered in [hdd_partitioning.md](hdd_partitioning.md).

## §2. Three Generations

### 2.1 Generation 1 — The floppy ceiling (1984–1995)

The floppy subsystem gave the Spectrum a fixed ceiling of **720 KB** (+3DOS, 9 sectors/track) or **800 KB** (TR-DOS, 10 sectors/track) per disk. For most of the 1980s this was ample: a typical game was 40–48 KB, a demoscene production perhaps 100 KB. The floppy's real limitation was not capacity but **swapping** — a multi-disk game required the user to physically exchange media, and a demoscene megademo spread across four disks was awkward to distribute.

Two pressures eroded the floppy's adequacy in the early 1990s:

- **Software size.** Russian RPGs and adventure games (the *Star Legacy* / *Black Crow* lineage) routinely exceeded a single TR-DOS disk. A 1 MB production needed two disks and a swap midway.
- **The demoscene.** By 1996 the top Pentagon demoscene works — *Echo*, *Yummy* — pushed 2–4 MB of graphics, music, and code. Distributing these on floppies meant 3–5 disks and a fragile multi-load sequence.

The floppy also imposed a **speed ceiling**. TR-DOS reads at roughly 30–60 KB/s depending on the controller; loading a 1 MB production took 20–30 seconds of disk thrashing. Random access (seeking to a specific file) was slower still.

### 2.2 Generation 2 — IDE and CompactFlash (2001–2013)

The first hobbyist IDE interfaces appeared around **2001**, but the format did not reach maturity until the **DivIDE** in 2007. IDE (Integrated Drive Electronics, also called PATA or ATA) is a 16-bit parallel protocol originally designed for PC hard disks; a CompactFlash card in "true IDE" mode speaks the same protocol through a 50-pin CF socket, which is how most Spectrum IDE interfaces actually connect storage.

The appeal of IDE was capacity and speed:

- A typical IDE hard disk of the mid-2000s held **2–40 GB** — effectively infinite by Spectrum standards.
- A CompactFlash card held **32 MB–4 GB** and drew little power, important because the Spectrum's +5V rail is weak.
- IDE transfer rates reached **200–800 KB/s** on a well-designed interface, an order of magnitude above floppy.

The difficulty was the protocol. IDE is a 16-bit bus with a register file (Error, Features, Sector Count, LBA Low/Mid/High, Drive/Head, Status, Command) and a pio transfer mode. Driving it from an 8-bit Z80 requires two reads or writes per 16-bit word, plus polling the Status register's DRQ bit. This is tedious but not hard, and every IDE interface article in this sub-section documents the exact sequence.

The IDE era's signature DOS was **ESXDOS** (Dylan Smith, 2008), which brought FAT16/FAT32 to the DivIDE. See [divide_divmmc.md](divide_divmmc.md) for the full treatment.

### 2.3 Generation 3 — SD cards (2013–present)

The **DivMMC** (Zoran "Zoxon" Mačković, 2013) replaced the IDE connector with an SD-card slot. SD cards talk to a host using one of two protocols: the proprietary SD high-speed mode, or the simpler **SPI mode** that any microcontroller (or Z80) can drive. Every Spectrum SD interface uses SPI mode.

SD's advantages over IDE are physical and economic rather than performance:

- **Size.** A MicroSD card is smaller than a fingernail; the socket is tiny. The whole DivMMC board fits inside a 48K Spectrum case.
- **Power.** SD cards draw milliamps, not the hundreds of milliamps an old IDE drive needs. No external power supply is required.
- **Availability.** In 2024, IDE drives and even CompactFlash cards are scarce; SD cards are commodity items in any supermarket.
- **Capacity.** Even a modest 8 GB MicroSD card holds the entire documented Spectrum software library with room to spare.

The trade-off is that SPI mode is slower than parallel IDE — typically **50–200 KB/s** on a Spectrum — but this is still far above floppy and imperceptible for most software. SD became the default, and IDE is now a specialist's format. See [sd_interface.md](sd_interface.md) for the hardware details.

## §3. The Interfaces at a Glance

The table below lists every significant mass-storage interface that reached the Spectrum. The dedicated articles cover each in depth; this is the navigation map.

| Interface | Year | Medium | Connector | Native DOS | Typical use |
|---|---|---|---|---|---|
| **DivIDE** | 2007 | IDE / CF | 40-pin PATA + 27C512 ROM | ESXDOS | General-purpose IDE; TR-DOS image emulation |
| **DivMMC** | 2013 | SD / SDHC | MicroSD slot (SPI) | ESXDOS | The 2024 default; pocket-sized SD storage |
| **ZXMMC** | 2011 | SD / SDHC | SD slot (SPI) | Custom / FAT | Early SD interface; SPI on classic ZX bus |
| **ZX Spectrum Next** | 2017 | SD / SDHC | MicroSD ×2 (SPI) | NextZXOS | Built-in dual SD; layer-2 / ROM slots |
| **Z-Controller** | 2008 | SD / CF | SD slot + IDE | FAT (firmware) | ATM Turbo / Pentagon add-on; RTC included |
| **SMUC** | 2007 | ISA peripherals | ISA slot | Custom | ZX Evolution ISA bridge (NIC, IDE, RTC) |
| **Nemo IDE** | 2004 | IDE / CF | 40-pin PATA | Raw / FAT | Early Pentagon IDE; predecessor of DivIDE |
| **KAY IDE** | 2004 | IDE / CF | 40-pin PATA | Raw / FAT | KAY-1024 built-in IDE |

A few observations on this table:

**The DivIDE family dominates.** The DivIDE (2007) and its SD-card sibling the DivMMC (2013) account for the overwhelming majority of real-hardware Spectrum mass storage in 2024. They share a port layout (`#E3`–`#E7`), a firmware lineage (ESXDOS), and an API, so software written for one runs on the other. The other interfaces are either older experiments (Nemo IDE, KAY IDE), specialist hardware (SMUC's ISA bridge for the ZX Evolution), or built into specific clones (Z-Controller on the ATM Turbo, dual SD on the Next).

**Two protocols, one bus.** Every interface in the table speaks one of two device protocols — IDE/ATA (the DivIDE, Nemo IDE, KAY IDE, Z-Controller's IDE half, SMUC's IDE cards) or SD-SPI (the DivMMC, ZXMMC, Next, Z-Controller's SD half). The [ide_interface.md](ide_interface.md) and [sd_interface.md](sd_interface.md) articles cover each protocol family respectively.

**The DOS matters more than the hardware.** A naked IDE interface with no DOS is just a block device; what makes it useful is the filesystem layer. ESXDOS (FAT16/32), NextZXOS (FAT + Next extensions), and the older IS-DOS (hierarchical, MS-DOS-like) are the three DOSes that matter. The hardware articles therefore lean heavily on the OS articles: [esxdos.md](../../04_operating_systems/esxdos.md), [nextzxos.md](../../04_operating_systems/nextzxos.md), and [is_dos.md](../../04_operating_systems/is_dos.md).

### 3.1 Choosing an interface in 2024

For a new real-hardware Spectrum user, the decision is almost always the **DivMMC**: it is cheap, tiny, SD-based, and runs the same ESXDOS firmware as the DivIDE. The DivIDE remains relevant for users who want CompactFlash storage (some prefer CF's write-protect switch) or who own DivIDE-specific software.

For the ZX Spectrum Next, the built-in **dual MicroSD slots** need no expansion at all — the primary slot holds the machine's firmware and core files, the secondary slot holds user software.

For emulator authors, modeling the **DivIDE/DivMMC port layout** (`#E3`–`#E7`) and ESXDOS is sufficient to run the vast majority of modern Spectrum software. Fuse, ZEsarUX, CSpect, and UnrealSpeccy all implement this.

## §4. Why HDD Mattered for the Soviet Scene

The Western Spectrum story could almost end at the floppy: by 1987 the +3 had a built-in disk drive, and most UK users moved to 16-bit machines before mass storage became a real limitation. The Soviet and post-Soviet story is the opposite: the **Pentagon** and its clones dominated Russian computing well into the late 1990s, and software for them grew without the safety valve of a platform upgrade.

### 4.1 The Pentagon's longevity

The Pentagon (1991) and its successors — the Pentagon 1024, Scorpion ZS-256, Profi, ATM Turbo, and the late ZX Evolution (2010) — were the primary home computers for hundreds of thousands of users across Russia, Ukraine, and Belarus throughout the 1990s. A 16-bit PC was unaffordable for most families; a Pentagon kit cost roughly a month's wages and could be upgraded incrementally.

The consequence was that **Spectrum software kept growing on a platform that never officially supported hard disk**. By 1996 the major Russian demoscene groups (Brainwave, Eternity Industry, Extreme, X-Trade) were producing megabytes of content. By 2000, the Russian game scene had produced RPGs and strategies that dwarfed anything the Western Spectrum ever saw.

### 4.2 FidoNet and the software river

The other driver was **FidoNet**. From roughly 1994 to 2005, FidoNet was the dominant electronic communication network in the post-Soviet world — a store-and-forward BBS system running over dial-up modems. Spectrum users had their own FidoNet echoes (notably `ZX.SPECTRUM` and `RU.SPECTRUM.ZX`), and software flowed through them constantly: new demos, tracker modules, disk magazines (*Spectrofon*, *Adventurer*, *ZX-Format*), and cracked games.

A user who wanted to keep up needed somewhere to **store** this river of software. A 800 KB TR-DOS disk held perhaps two demos; a serious collector had stacks of floppies. The appeal of a hard disk that could hold the entire incoming FidoNet batch in one place was enormous. This is the direct motivation behind the **Nemo IDE** (2004) and the **DivIDE** (2007): give the Spectrum a single large volume instead of a hundred floppies.

### 4.3 IS-DOS: the Russian hierarchical filesystem

Western interfaces standardized on FAT, but the Soviet scene produced its own filesystem: **IS-DOS** (Дымиров / Aleksey Dmyrov, 1993). IS-DOS is a hierarchical, MS-DOS-compatible filesystem with 32-byte directory entries, subdirectories, file attributes, and a jump-table API. It predates FAT-on-Spectrum by over a decade and shipped with its own GUI file manager.

IS-DOS never achieved the ubiquity of FAT (it was tied to specific hardware and had a smaller software library), but it is historically important as the **first** attempt to give the Spectrum a PC-like filesystem. It is covered in [is_dos.md](../../04_operating_systems/is_dos.md) and [hdd_partitioning.md](hdd_partitioning.md).

### 4.4 The convergence

By 2010 the Soviet and Western stories had converged. The DivIDE (a Western design) was adopted enthusiastically by Russian users; ESXDOS (a Western DOS) became the standard on Pentagon and Scorpion machines; and the ZX Evolution (a Russian clone) shipped with DivIDE-compatible ports. The cultural split that characterized the floppy era — TR-DOS in the East, +3DOS/CP/M/MGT in the West — dissolved at the hard-disk layer, where a single FAT volume serves both worlds.

## §5. The Modern Landscape (2024)

In 2024, real-hardware Spectrum mass storage is a solved problem. The **DivMMC** (or one of its clones — the "Resident" version, the "FutureOS" version, the integrated ZX Spectrum Next SD slot) is the default; a new user buys one for the equivalent of $20–40, plugs in a MicroSD card prepared on a PC, and has access to the entire documented software library.

The professional retro-hardware stack in 2024 is typically:

- A **ZX Spectrum Next** (FPGA reimplementation) with its dual MicroSD slots and NextZXOS, **or**
- A refurbished 48K/128K/+2A/+3 with a **DivMMC** and ESXDOS, plus
- A **Beta 128 / TR-DOS** interface for original floppy software (still common among demoscene coders), and
- Optionally an **inner-side** SD interface on clone hardware (ZX Evolution, ATM Turbo, Pentagon with Z-Controller).

For software distribution, the **FAT-formatted SD card** has completely replaced the floppy disk. New demoscene releases in 2024 ship as a `.zip` on a web archive, are unpacked onto an SD card, and run from a DivMMC via a dot command (`*.run`, `*.load`). The `.TRD` floppy image remains in use for Beta 128 compatibility, but it is now a virtual image on an SD card rather than a physical disk.

## §6. Cross-references and License

### 6.1 Within this sub-section

| Article | Covers |
|---|---|
| [ide_interface.md](ide_interface.md) | Every IDE interface compared: DivIDE, Nemo IDE, KAY IDE, Z-Controller, SMUC — port maps, pinouts, banking |
| [divide_divmmc.md](divide_divmmc.md) | The DivIDE and DivMMC in depth: hardware, ESXDOS firmware, memory paging, dot commands, FAT access |
| [sd_interface.md](sd_interface.md) | Every SD interface compared: DivMMC, ZXMMC, ZX Spectrum Next, Z-Controller — SPI protocol, port maps |
| [hdf_mgt_formats.md](hdf_mgt_formats.md) | The `.HDF`, `.MGT`, and `.IMG` hard-disk and disk-image file formats used by emulators |
| [hdd_partitioning.md](hdd_partitioning.md) | Partition tables, FAT16/FAT32 on DivIDE, IS-DOS partitions, how the SD card is laid out |

### 6.2 Related articles elsewhere

| Article | Relationship |
|---|---|
| [disk_format_overview.md](disk_format_overview.md) | The floppy sub-section this article extends; the starting point for the whole storage story |
| [trd_disk_format.md](trd_disk_format.md) | TR-DOS, the floppy format that hard disk originally supplemented and now emulates |
| [esxdos.md](../../04_operating_systems/esxdos.md) | The DOS that defined the IDE/SD era — FAT16/32, dot commands, the assembly API |
| [nextzxos.md](../../04_operating_systems/nextzxos.md) | The ZX Spectrum Next's ESXDOS derivative; dual SD, layer-2 / sprite / tilemap integration |
| [is_dos.md](../../04_operating_systems/is_dos.md) | The Russian hierarchical filesystem alternative; covered here as historical context |
| [evo_os.md](../../04_operating_systems/evo_os.md) | The ZX Evolution's BIOS/OS stack, which uses DivIDE-compatible ports for its IDE |
| [io_port_decoding.md](../../05_development/03_memory_and_io/io_port_decoding.md) | How I/O ports like `#E3`–`#E7` are decoded; the foundation for the port maps in this sub-section |

### 6.3 External references

- **World of Spectrum** (`worldofspectrum.org`) — the central Western Spectrum archive; scans of the original DivIDE/DivMMC documentation and the ESXDOS manual.
- **Spectrumpedia (Alessandro Grussu)** — English/Italian encyclopedia covering the Sinclair/Amstrad line and the Russian clone ecosystem; the most authoritative cross-track print reference.
- **zx-pk.ru** — the Russian-language Spectrum forum; the origin of most Pentagon/Scorpion mass-storage modifications and the primary discussion venue for Nemo IDE, SMUC, and Z-Controller.
- **ZX Spectrum Next official docs** (`zxnext.io`) — the layer-2 / expansion-bus reference that defines the Next's dual SD slot and the NextZXOS FAT access API.
- **The ESXDOS documentation** (Dylan Smith, 2008 and later) — the canonical reference for the FAT16/32 API, dot command system, and `#E3`–`#E7` port layout that defined the DivIDE era.

### 6.4 License

This article is licensed under [CC BY-SA 4.0](../../README.md). Cross-referenced articles retain their own licenses as stated in each file.
