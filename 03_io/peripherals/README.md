[← Home](../../README.md) · [Peripherals](README.md)

# I/O — Peripherals

This directory covers input devices, expansion interfaces, output hardware, and the broader peripheral ecosystem around the ZX Spectrum family — original Sinclair, Soviet clones, and New Generation hardware. Sound cards live in a dedicated subdirectory ([06_sound](../../06_sound/)); mass-storage peripherals live in [03_io/storage](../storage/README.md).

---

## Articles

| # | Article | Description | Lines |
|---|---------|------------|-------|
| 1 | [interface1.md](interface1.md) | **ZX Interface 1** — Sinclair's 1983 triple-function expansion (Microdrive controller + RS-232 + ZX Net LAN). 8 KB shadow ROM paging trick (`M1` fetch at `#0008`), 3-port I/O map (`#F7`/`#EF`/`#E7`), complete hook-code API (`#1B`–`#32`), ZX Microdrive sector format (254 sectors × 543 bytes, bespoke non-CRC checksum), bit-bang RS-232 (50–9600 baud), ZX Net single-wire open-collector token bus for 64 stations, system-variable layout at `#5CB6–#5CEF`, comparison with Opus Discovery / DISCiPLE / Beta Disk / +3, full BASIC syntax extension table | 570 |
| 2 | [joystick.md](joystick.md) | **Joystick Interfaces** — Kempston (`#1F`), Sinclair/Interface 2 (matrix rows `#EFFE`/`#F7FE`), Cursor/Protek/AGF, Fuller (`#7F`), Timex (TS2068 AY reg 14). Active-high vs active-low polarity, decoding variants, Beta 128 conflict, unified table-driven reader, decision guide | 399 |

See [PLAN.md](../../PLAN.md) for the full article catalog. Planned articles: keyboard, mouse, lightgun, Interface 2, Multiface, Z-Controller, MB02, ZX Bus, printers, video output.
