[← Plan](../../PLAN.md) · [New Generation](README.md)

# Hardware — New Generation

This directory covers modern ZX Spectrum hardware: ZX Spectrum Next, Sprinter, ZX Evolution, ZX-Uno, and the Karabas family.

---

## Articles

| # | Article | Description |
|---|---------|------------|
| 1 | [zx_next.md](zx_next.md) | ZX Spectrum Next complete hardware reference: history/revisions, physical architecture, layer stack, NextReg system, Layer 2 framebuffer (256-color, banking, shadow, scrolling), hardware sprites (64/scanline, 4-/8-bit, collision), tilemap (40×32/80×32, attributes, scrolling), copper coprocessor (WAIT/MOVE/STOP, raster effects), DMA controller (memory/I/O, burst/continuous, pattern match), joystick system (dual Kempston, Mega Drive pads), Z80N CPU extensions, compatibility modes (48K/128K/+3/Pentagon) |
| 2 | [sprinter.md](sprinter.md) | Peters Plus Sprinter (2000): Z84C15 @ 21 MHz, 4 MB RAM, Altera ACEX EP1K30 (reconfigurable from flash), per-cell video modes (320×256×256 / 640×256×16, mixed per 8×8 cell), RAM-based soft port map, IDE, ISA-8, AY in FPGA + 16-bit Covox — different path from FPGA-recreation machines |
| 3 | [sprinter_firmware.md](sprinter_firmware.md) | Sprinter firmware & sources: PLD configuration concept and bitstream loading, the six configurations (Sprinter-1/2, ZX+AY, Game-1, DooM, Video), RAM copy accelerator (`LD r,r` opcodes, `#C7` scale register), BIOS flash layout and versions 2.02→3.07 (Peters Plus → community), Estex DSS 1.52→1.71, board history sp97→sp2016s, full source-repository catalog (GitLab/zxgit/GitHub, verified) |
| 4 | [zx_evo.md](zx_evo.md) | ZX Evolution (2007): hybrid Z80 + Altera FPGA + ATmega MCU, Pentagon 1024 hardware compatibility, modern extensions (turbo/IDE/SD/PS-2) |
| 5 | [baseconf.md](baseconf.md) | BaseConf (ZX Evolution default firmware, by CHRV/LVD at NedoPC): Pentagon 1024 profile, `#7FFD`/`#DFFD`/`#EFF7` paging, **Nemo IDE with 16-bit words in both byte orders**, turbo + emulated 48K/128K contention, AVR-managed PS/2/SD/RS-232/RTC, hardware revisions A/B/C, 7 alternative firmware configurations |
| 6 | [ts_conf.md](ts_conf.md) | TS-Conf enhanced firmware (tslabs / A. Zhuravlev): **`#xxAF` register space** (256 registers, only 4 readable), 4 windows × 16 KB into shared 4 MB (no separate VRAM), 2 tile layers 64×64 + **85 sprites/frame** in 3 layers (8–64 px, LEAP split, X/Y flip), 4 pixel modes × 4 geometries (256×192 → 360×288, TXT hires 720×288), RGB555 CRAM with immediate writes, **9-task DMA** (copy/BLT1/BLT2/FILL/SPI/IDE/CRAM/SFILE), 512-byte CPU cache, 4 INT vectors, 71,680 T frame |
| 7 | [vdac2.md](vdac2.md) | VDAC2 (TS-Labs, 2025–2026): FT812 EVE2 GPU card for the ZX Evolution IDE slot — display lists, coprocessor, 1 MB RAM_G, 640×480/800×600/1024×768 @ 57–85 Hz, hardware scaling/rotation; SPI via TS-Conf ports `#57`/`#77` (CS[1]) + DMA, msel = `V_CONFIG[2]`, VDAC_VER lineage (VDAC1→2→3/ESP32), DXT texture trick, VDAC2 games (R-Type, Zuma, HoMM2 — MIT), emulation state |
| 8 | [zx_uno.md](zx_uno.md) | ZX-Uno (2016, AZXUNO, crowdfunded on Verkami): open-source FPGA Spectrum (Xilinx Spartan-6 XC6SLX9-2TQG144C + 512 KB SRAM + 4 MB SPI flash), 5-person team (Villena/Bayó/Baselga/Rodríguez Jódar/Superfo), ULAplus palette, multi-machine framework (up to 9 cores incl. SAM Coupé, Jupiter ACE, ColecoVision), optional ESP-12 WiFi |
| 9 | [karabas.md](karabas.md) | Karabas family (2018+): three open-source Z80 + Altera MAX II CPLD clones — Karabas 128 (EPM240, Sinclair 128K exact), Karabas Pro (EPM570, Pentagon 128 + turbo/SD/VGA), Peridot (EPM1270, Karabas Pro + WiFi/RTC/GPIO) |

See [PLAN.md](../../PLAN.md) for the full article catalog.
