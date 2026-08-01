[← Plan](../../PLAN.md) · [DOS & Tape](README.md)

# Development — DOS and Tape Programming

This series covers every aspect of data I/O from assembly: loading and saving to tape, working with disk operating systems (TR-DOS, +3 DOS, ESXDOS, NextZXOS), parsing common file formats, and direct hardware access to mass storage.

## Reading Order

| # | Article | Description |
|---|---|---|
| 1 | [tape_programming.md](tape_programming.md) | ROM tape routines (SA-BYTES, LD-BLOCK), custom bit-banging loaders, turbo loaders (3000+ baud), custom savers, error handling |
| 2 | [trdos_programming.md](trdos_programming.md) | TR-DOS ROM paging, 9 hook codes, file operations (LOAD/SAVE/ERASE/CAT), direct WD1793 sector I/O, demoscene streaming |
| 3 | [dos_programming.md](dos_programming.md) | +3 DOS RSX calls, ESXDOS hook codes, NextZXOS extensions, dot command development, API comparison matrix, runtime DOS detection |
| 4 | [file_format_handling.md](file_format_handling.md) | Parsing .TAP/.TZX/.TRD/.SCL/.DSK/.SNA/.Z80/.SCR from assembly — magic bytes, directory traversal, decompression |
| 5 | [mass_storage_programming.md](mass_storage_programming.md) | Direct IDE/CF register access, ATA commands, SD card SPI bit-banging, read-only FAT16/32 reader, performance vs OS-mediated |

## Cross-Reference Table

| This series | Canonical reference |
|---|---|
| [tape_programming.md](tape_programming.md) | [tape_interface.md](../../03_io/storage/tape_interface.md), [tape_format.md](../../03_io/storage/tape_format.md) |
| [trdos_programming.md](trdos_programming.md) | [trdos.md](../../04_operating_systems/trdos.md), [trd_disk_format.md](../../03_io/storage/trd_disk_format.md) |
| [dos_programming.md](dos_programming.md) | [plus3dos.md](../../04_operating_systems/plus3dos.md), [esxdos.md](../../04_operating_systems/esxdos.md), [nextzxos.md](../../04_operating_systems/nextzxos.md) |
| [file_format_handling.md](file_format_handling.md) | [tap_format.md](../../03_io/storage/tap_format.md), [tzx_format.md](../../03_io/storage/tzx_format.md), [trd_scl_formats.md](../../03_io/storage/trd_scl_formats.md) |
| [mass_storage_programming.md](mass_storage_programming.md) | [ide_interface.md](../../03_io/storage/ide_interface.md), [sd_interface.md](../../03_io/storage/sd_interface.md), [divide_divmmc.md](../../03_io/storage/divide_divmmc.md) |

> **Scope note**: These articles focus on the **programmer's practical perspective** — complete working code, decision matrices, and pitfalls. The reference articles in [03_io/storage/](../../03_io/storage/README.md) and [04_operating_systems/](../../04_operating_systems/README.md) cover the byte-level specifications, hardware details, and system-level architecture in exhaustive detail. Read the tutorial first, then consult the reference when you need the full specification.
