[← Plan](../../PLAN.md) · [New Generation](README.md)

# Hardware — New Generation

This directory covers modern ZX Spectrum hardware: ZX Spectrum Next, Sprinter, ZX Evolution, ZX-Uno, Karabas family, and Peridot.

---

## Articles

| # | Article | Description |
|---|---------|------------|
| 1 | [zx_next_joystick.md](zx_next_joystick.md) | ZX Next joystick system: per-port mode selection (NextReg 0x05), dual Kempston ports #1F/#37, Mega Drive pads, Sinclair numbering trap, port conflicts |
| 2 | [zx_next.md](zx_next.md) | ZX Spectrum Next platform overview: history/revisions, physical hardware, layer stack, NextReg access system, I/O port summary, compatibility modes (48K/128K/+3/Pentagon), Z80N CPU extensions |
| 3 | [zx_next_sprites.md](zx_next_sprites.md) | Next sprites: 64 sprites/scanline, 4-/8-bit types, pattern/attribute upload protocol, priority/transparency, collision detection, per-scanline limit |
| 4 | [zx_next_layer2.md](zx_next_layer2.md) | Next Layer 2: 256-color 8bpp framebuffer, three-window banking (#123B), 256-entry palette, 320×256 extended mode, shadow framebuffer (double-buffering), hardware scrolling |
| 5 | [zx_next_tilemap.md](zx_next_tilemap.md) | Next tilemap: 40×32 (or 80×32) hardware tiles, 256-entry pattern table, per-tile attributes (mirror/palette offset/priority), X/Y scroll NextRegs |
| 6 | [zx_next_copper.md](zx_next_copper.md) | Next copper: WAIT/MOVE/STOP instruction set, instruction encoding, upload protocol, raster bars, mid-frame mode switches, sprite multiplexing |
| 7 | [zx_next_dma.md](zx_next_dma.md) | Next DMA: Z80 DMA-derived, memory/I/O transfers, byte/burst/continuous modes, pattern matching, sample playback pattern |
| 8 | [sprinter.md](sprinter.md) | Peters Plus Sprinter (1996): Z80 @ 20 MHz, 1 MB RAM, Produce SVGA ASIC (PC-style video modes), IDE, PS/2, ISA — different path from FPGA-based machines |
| 9 | [zx_evo.md](zx_evo.md) | ZX Evolution (2007): hybrid Z80 + Altera MAX CPLDs + ATmega MCU, Pentagon 1024 hardware compatibility, modern extensions (turbo/IDE/SD/PS-2) |
| 10 | [baseconf.md](baseconf.md) | ZX Evolution default firmware: Pentagon 1024 profile, #7FFD/#DFFD/#EFF7 paging, turbo/IDE/SD/RTC extensions, ROM configuration, profile switching |
| 11 | [ts_conf.md](ts_conf.md) | TS-Conf enhanced firmware: hardware sprites (32/scanline), tilemap (40×25), 512 KB dedicated VRAM, per-scanline palettes, TSR driver API |
| 12 | [zx_uno.md](zx_uno.md) | ZX-Uno (2015): open-source FPGA Spectrum (Xilinx Spartan-6), ULAplus palette extension, multi-machine cores, optional ESP-12 WiFi |
| 13 | [karabas_pro.md](karabas_pro.md) | Karabas Pro: compact modern Z80 + Altera MAX II EPM570, Pentagon 128 compatibility, 512 KB RAM, turbo (3.5/7/14 MHz), SD card, VGA |
| 14 | [karabas_128.md](karabas_128.md) | Karabas 128: minimalist modern Z80 + MAX II EPM240, Sinclair 128K exact compatibility (with contention), entry-level build |
| 15 | [peridot.md](peridot.md) | Peridot: expandable Karabas-compatible platform, MAX II EPM1270, built-in WiFi (ESP-12)/RTC/GPIO header, hardware experimenter's machine |

See [PLAN.md](../../PLAN.md) for the full article catalog.
