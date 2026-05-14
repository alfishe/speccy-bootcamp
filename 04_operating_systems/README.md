[← Home](../README.md) · [Operating Systems](README.md)

# Operating Systems

ZX Spectrum ROM variants, DOS systems, and ROM-defined workspace. The Spectrum has no traditional OS — the ROM BASIC interpreter IS the operating system. Disk-based DOSes (TR-DOS, +3 DOS, ESXDOS) layer on top.

| Article | Description |
|---------|------------|
| [rom_48k.md](rom_48k.md) | 48K ROM: initialisation, RST vectors, command dispatch mechanism, calculator instruction set (66 ops), error handling, variable storage, command handler internals (PRINT/INPUT/PLOT/BEEP/LET/LOAD), tape format, 10 practical use cases |
| [rom_128k.md](rom_128k.md) | 128K ROM 0: dual-ROM architecture, ROM call bridge (how ROM 0 delegates to ROM 1 via RAM paging routines), ROM swap calling convention with mermaid flow diagrams, start-up sequence, PLAY/SOUND/BANK/SPECTRUM handlers, AY-3-8912 register map and programming, RAM disk data structures, editor internals, +2A/+3 deep dive, 6 use cases |
| [system_variables.md](system_variables.md) | ROM-defined system variables: FRAMES counter, PROG/VARS pointers, keyboard state, display color, error handling, memory boundaries, 128K workspace — the ROM's API surface |

See [PLAN.md](../PLAN.md) for the full article catalog (ROM dissection, TR-DOS, +3 DOS, ESXDOS, NextZXOS, CP/M, FUZIX, BASIC dialects).
