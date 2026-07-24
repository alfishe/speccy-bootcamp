[← Home](../../README.md) · [Peripherals](README.md)

# I/O — Peripherals

This directory covers input devices, expansion interfaces, output hardware, and the broader peripheral ecosystem around the ZX Spectrum family — original Sinclair, Soviet clones, and New Generation hardware. Sound cards live in a dedicated subdirectory ([06_sound](../../06_sound/)); mass-storage peripherals live in [03_io/storage](../storage/README.md).

---

## Articles

| # | Article | Description | Lines |
|---|---------|------------|-------|
| 1 | [interface1.md](interface1.md) | **ZX Interface 1** — Sinclair's 1983 triple-function expansion (Microdrive controller + RS-232 + ZX Net LAN). 8 KB shadow ROM paging trick (`M1` fetch at `#0008`), 3-port I/O map (`#F7`/`#EF`/`#E7`), complete hook-code API (`#1B`–`#32`), ZX Microdrive sector format (254 sectors × 543 bytes, bespoke non-CRC checksum), bit-bang RS-232 (50–9600 baud), ZX Net single-wire open-collector token bus for 64 stations, system-variable layout at `#5CB6–#5CEF`, comparison with Opus Discovery / DISCiPLE / Beta Disk / +3, full BASIC syntax extension table | 570 |
| 2 | [interface2.md](interface2.md) | **ZX Interface 2** (Sinclair, 1983) — twin-joystick + ROM-cartridge expansion. MT62001 custom IC for joystick decode (port `#EFFE` = joy 1, `#F7FE` = joy 2, with bit-order swap), 28-pin cartridge socket pinout mirroring 27128 EPROM with `/ROMCS` pulled high to disable internal ROM, A14/A15/`/MREQ` decode for #0000-#3FFF cartridge overlay, the 10 released cartridges, +2A/+3 incompatibility and two-diode fix, the homebrew cartridge ecosystem | 347 |
| 3 | [multiface.md](multiface.md) | **Multiface (One / 128 / 3)** — Romantic Robot's hardware overlay peripheral (1986–1988). 8 KB ROM + 8 KB RAM paged in via NMI vector fetch at `#0066`, three model variants with distinct port maps (`#9F`/`#1F` for MF1, `#BF`/`#3F` for MF128, `#3F`/`#BF` for MF3), `+3` paging-port back doors (`#7F3F`/`#1F3F`), stealth mode flip-flop, dump-file format (precursor to `.z80`), Genie disassembler and Lifeguard poke-finder tool ecosystem, cultural impact on cheat codes and snapshots | 411 |
| 4 | [joystick.md](joystick.md) | **Joystick Interfaces** — Kempston (`#1F`), Sinclair/Interface 2 (matrix rows `#EFFE`/`#F7FE`), Cursor/Protek/AGF, Fuller (`#7F`), Timex (TS2068 AY reg 14). Active-high vs active-low polarity, decoding variants, Beta 128 conflict, unified table-driven reader, decision guide | 399 |

See [PLAN.md](../../PLAN.md) for the full article catalog. Planned articles: keyboard, mouse, lightgun, Z-Controller, MB02, ZX Bus, printers, video output.
