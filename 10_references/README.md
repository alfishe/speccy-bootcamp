[← Plan](../PLAN.md) · [References](README.md)

# References

Quick-reference tables for ZX Spectrum development: opcode matrix, I/O port map, memory maps, character set, token tables, ROM routines, color palettes, error codes, timing, and pinouts.

## Articles

| Article | Description |
|---------|-------------|
| [io_port_map.md](io_port_map.md) | Complete I/O port reference: every port across all models with decoding bitmasks, per-model differences, Black_Cat table replication with annotations |
| [z80_opcode_table.md](z80_opcode_table.md) | One-page Z80 opcode lookup: every documented instruction by group with byte count, T-states, and flag effects. Compresses [z80_instruction_set.md](../01_cpu/z80_instruction_set.md) into scan-able tables |
| [character_set.md](character_set.md) | ZX Spectrum character set: code ranges, ROM font layout at `#3D00`–`#3FFF`, UDG system, CHARS redirection for custom fonts, token encoding |
| [color_palette.md](color_palette.md) | Color reference: 15-colour standard palette (FUSE/Skoolkid/ZEsarUX variants), ULAplus 64-colour, ZX Spectrum Next 256-colour, Timex extended modes |

## Planned

- `memory_maps.md` — Consolidated memory maps for all models
- `basic_token_table.md` — Sinclair BASIC token table
- `rom_routines.md` — ROM routine addresses
- `error_codes.md` — BASIC error codes
- `timing_reference.md` — Consolidated timing tables
- `pinouts.md` — Pinout reference for edge connector, AY, joystick ports

See [PLAN.md](../PLAN.md) for the full article catalog.
