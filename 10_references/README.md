[← Home](../README.md) · [References](README.md)

# References ✅ COMPLETE (11 articles)

Quick-reference tables for ZX Spectrum development: opcode matrix, I/O port map, memory maps, character set, token tables, ROM routines, color palettes, error codes, timing, and pinouts — plus the complete English translation of Black_Cat's full ports table.

## Articles

| Article | Description |
|---------|-------------|
| [io_port_map.md](io_port_map.md) | Complete I/O port reference: every port across all models with decoding bitmasks, per-model differences, Black_Cat table replication with annotations |
| [zx_ports_full_table.md](zx_ports_full_table.md) | Complete English translation of Black_Cat's ZX Ports Full Table (BC Info Guide #4, 2008) — all 32 sections verbatim: system/peripheral/shadow ports, disk interfaces, IDE adapters, sound cards, mice, COM ports, RTCs, with the original's model-code and function-code legends |
| [z80_opcode_table.md](z80_opcode_table.md) | One-page Z80 opcode lookup: every documented instruction by group with byte count, T-states, and flag effects. Compresses [z80_instruction_set.md](../01_cpu/z80_instruction_set.md) into scan-able tables |
| [character_set.md](character_set.md) | ZX Spectrum character set: code ranges, ROM font layout at `#3D00`–`#3FFF`, UDG system, CHARS redirection for custom fonts, token encoding |
| [color_palette.md](color_palette.md) | Color reference: 15-color standard palette (FUSE/Skoolkid/ZEsarUX variants), ULAplus 64-color, ZX Spectrum Next 256-color, Timex extended modes |
| [memory_maps.md](memory_maps.md) | Consolidated memory maps for every model (16K/48K, 128K/+2, +2A/+3, Pentagon, Scorpion, ATM Turbo, Next) — contended regions, banking registers, RAMTOP defaults, cross-model compatibility cheat sheet |
| [basic_token_table.md](basic_token_table.md) | Sinclair BASIC token table: byte values, mnemonics, and tokenisation rules for 48K/128K/+2/+2A/+3 ROMs — control codes, function tokens, UDGs, block graphics, detokenising and tokenising routines |
| [error_codes.md](error_codes.md) | All BASIC/DOS error codes — 10 Sinclair BASIC codes, +3 DOS (12 codes), TR-DOS (Russian), ESXDOS (POSIX-style), IS-DOS, NextZXOS — system variables, recovery patterns, common scenarios |
| [timing_reference.md](timing_reference.md) | Cycle-exact timing tables — CPU clocks per model, video frame timings (48K/128K/Pentagon), contention delay tables (late/early), INT/NMI timing, common instruction T-state counts, useful constants |
| [pinouts.md](pinouts.md) | Pin-by-pin reference — 48K/128K/+2 expansion edge connector (A and B side), Z80 CPU 40-pin DIP, AY-3-8912 28-pin DIP, joystick ports (Kempston/Sinclair 1/2/Fuller), Kempston mouse, EAR/MIC jacks, power connectors |
| [rom_routines.md](rom_routines.md) | ROM entry points — restart vectors (`RST #08–#38`), character output, keyboard, tape, math/calculator, 128K-specific routines, calling conventions with examples |

See [PLAN.md](../PLAN.md) for the full article catalog.
