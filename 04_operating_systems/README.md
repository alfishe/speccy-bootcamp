[← Home](../README.md) · [Operating Systems](README.md)

# Operating Systems

ZX Spectrum ROM variants, DOS systems, and ROM-defined workspace. The Spectrum has no traditional OS — the ROM BASIC interpreter IS the operating system. Disk-based DOSes (TR-DOS, +3 DOS, ESXDOS) layer on top.

The articles in this section are grouped into four thematic areas:

- **ROM internals** — dissection of the original Sinclair ROM variants (48K, 128K, +2A/+3) and the system variables that the ROM defines.
- **Disk operating systems** — the DOSes that brought file I/O to the Spectrum: TR-DOS, +3 DOS, ESXDOS, IS-DOS, NedoDOS, and the ZX Evolution BIOS that hosts them.
- **Alternative operating systems** — non-DOS OSes that ran on Spectrum-compatible hardware: CP/M 2.2 and FUZIX.
- **BASIC dialects and ROM identification** — survey of all Sinclair BASIC variants, plus the catalog of ROM versions for identification.

## ROM Internals

| Article | Description |
|---------|-------------|
| [rom_48k.md](rom_48k.md) | 48K ROM: initialisation, RST vectors, command dispatch mechanism, calculator instruction set (66 ops), error handling, variable storage, command handler internals (PRINT/INPUT/PLOT/BEEP/LET/LOAD), tape format, 10 practical use cases |
| [rom_128k.md](rom_128k.md) | 128K ROM 0: dual-ROM architecture, ROM call bridge (how ROM 0 delegates to ROM 1 via RAM paging routines), ROM swap calling convention with mermaid flow diagrams, start-up sequence, PLAY/SOUND/BANK/SPECTRUM handlers, AY-3-8912 register map and programming, RAM disk data structures, editor internals, +2A/+3 deep dive, 6 use cases |
| [rom_plus2.md](rom_plus2.md) | +2A/+3 ROM internals: the 64 KB four-page ROM layout (128K editor, original 48K BASIC, +3 DOS, patched 48K with disk extensions), paging ports `#7FFD` and `#1FFD`, four paging modes (128K compat / all-RAM 0-3 / all-RAM 4-7 / Plus 3), CP/M boot support, bugs and quirks |
| [system_variables.md](system_variables.md) | ROM-defined system variables: FRAMES counter, PROG/VARS pointers, keyboard state, display color, error handling, memory boundaries, 128K workspace — the ROM's API surface |
| [rom_versions.md](rom_versions.md) | ROM version catalog: 48K Issues 1-6 with CRC32 values, 128K ROM, +2 grey, +2A/+3 four-page ROM, localised ROMs (Spanish, Russian), clone ROMs (Pentagon, Scorpion, ATM Turbo, Sprinter, ZX Evolution, Timex), modern replacements (SE BASIC, OpenSE BASIC, +3E ROM, NextZXOS ROM), identification guide |

## Disk Operating Systems

| Article | Description |
|---------|-------------|
| [trdos.md](trdos.md) | TR-DOS: the Soviet-era standard floppy disk OS, shipped with the Pentagon and Beta 128 interface. Flat filesystem with 128 file slots, 8+1 filename format, hook codes API, ROM structure, why it dominated the Russian scene |
| [plus3dos.md](plus3dos.md) | +3 DOS: Amstrad's CP/M-compatible DOS for the +2A/+3 hardware. Built on the CP/M BDOS layer, RSX-based BASIC integration (`LOAD "a:..."`, `CAT`, `FORMAT`), file system, comparison with TR-DOS |
| [esxdos.md](esxdos.md) | ESXDOS: the modern Western DOS for DivIDE/DivMMC hardware. FAT16/32 support, 8 KB dot-command overlays, hook codes API at `#0084`, the standard for Western hobbyist SD-card storage |
| [is_dos.md](is_dos.md) | IS-DOS: the 1990s Russian hierarchical filesystem alternative to TR-DOS. MS-DOS-compatible 32-byte directory entries, subdirectories up to 32 levels deep, file attributes, jump-table assembly API. Why it failed to displace TR-DOS |
| [nedo_dos.md](nedo_dos.md) | NedoDOS: the modern DOS for the ZX Evolution and broader NedoPC ecosystem. FAT16/32 with VFAT long filenames, SD/CF/IDE hardware support, multiple partitions, jump-table API, NedoDOS Commander |
| [nextzxos.md](nextzxos.md) | NextZXOS: the ZX Spectrum Next's OS, the Western equivalent of NedoDOS + evo_os combined. ESXDOS-derived API with Next hardware extensions, dot commands, SD card, layer 2 / sprite / tilemap integration |
| [evo_os.md](evo_os.md) | ZX Evolution BIOS/OS: the three-layer software stack (boot ROM firmware, BaseConf FPGA bitstream, OS layer) for the flagship Russian FPGA-Spectrum. Pentagon 1024 / ATM Turbo / TS-Conf configurations, boot process, ROM slot management, hotkeys |

## Alternative Operating Systems

| Article | Description |
|---------|-------------|
| [cpm.md](cpm.md) | CP/M 2.2 on the Spectrum: Amstrad +3 bootable CP/M, ATM Turbo CP/M, Sprinter CP/M mode. The CP/M BIOS/BDOS layer, file control blocks, CCP, the CP/M software library, why CP/M mattered on the Spectrum |
| [fuzix.md](fuzix.md) | FUZIX: Alan Cox's Unix-like OS for Z80 systems, including the Spectrum 128K/+2/+2A/+3, Pentagon, ATM Turbo, Sprinter, ZX Evolution, and ZX Spectrum Next. ~24 KB kernel, ~70 Unix V7-style syscalls, pre-emptive multitasking, FCC C compiler |

## BASIC Dialects

| Article | Description |
|---------|-------------|
| [basic_dialects.md](basic_dialects.md) | Sinclair BASIC variants: 48K BASIC (1982), 128K BASIC (1986), +2/+2A/+3 BASIC (1987), TR-DOS extensions, QL SuperBASIC (1984), SE BASIC / OpenSE BASIC (2002-2023), NextBASIC (2017). 17-feature comparison matrix across the dialects |

## Cross-References

See [PLAN.md](../PLAN.md) for the full article catalog and progress tracking.
