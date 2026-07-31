[← Plan](../../PLAN.md) · [New Generation](README.md)

# Hardware — New Generation

This directory covers modern ZX Spectrum hardware: ZX Spectrum Next, Sprinter, ZX Evolution, ZX-Uno, and the Karabas family.

---

## Articles

| # | Article | Description |
|---|---------|------------|
| 1 | [zx_next.md](zx_next.md) | ZX Spectrum Next complete hardware reference: history/revisions, physical architecture, layer stack, NextReg system, Layer 2 framebuffer (256-color, banking, shadow, scrolling), hardware sprites (64/scanline, 4-/8-bit, collision), tilemap (40×32/80×32, attributes, scrolling), copper coprocessor (WAIT/MOVE/STOP, raster effects), DMA controller (memory/I/O, burst/continuous, pattern match), joystick system (dual Kempston, Mega Drive pads), Z80N CPU extensions, compatibility modes (48K/128K/+3/Pentagon) |
| 2 | [sprinter.md](sprinter.md) | Peters Plus Sprinter (1996): Z80 @ 21 MHz, 4 MB RAM, Altera PLD-based video (320×256×256 / 640×256×16), IDE, ISA, PS/2 — different path from FPGA-based machines |
| 3 | [zx_evo.md](zx_evo.md) | ZX Evolution (2007): hybrid Z80 + Altera FPGA + ATmega MCU, Pentagon 1024 hardware compatibility, modern extensions (turbo/IDE/SD/PS-2) |
| 4 | [baseconf.md](baseconf.md) | BaseConf (ZX Evolution default firmware, by CHRV/LVD at NedoPC): Pentagon 1024 profile, `#7FFD`/`#DFFD`/`#EFF7` paging, turbo/IDE/SD/RTC extensions, ROM configuration, hardware revisions A/B/C, 7 alternative firmware configurations (TS-Conf, ScorpEvo, EVO RESET/DOS/PROF, etc.) |
| 5 | [ts_conf.md](ts_conf.md) | TS-Conf enhanced firmware (tslabs team): hardware sprites (**up to 85/scanline**, 8×8 to 64×64, 3 planes), **2 tile planes**, **4 pixel resolutions** (256×192/320×200/320×240/360×288 + 720×288 hi-res), **4 graphic modes** (ZX/16c/256c/Text), **programmable RGB555 CRAM** (256 entries), **full DMA controller** (3 transfer modes), **512-byte CPU cache** for 14 MHz mode, **4 MB RAM addressing**, dedicated graphics memory |
| 6 | [zx_uno.md](zx_uno.md) | ZX-Uno (2016, AZXUNO, crowdfunded on Verkami): open-source FPGA Spectrum (Xilinx Spartan-6 XC6SLX9-2TQG144C + 512 KB SRAM + 4 MB SPI flash), 5-person team (Villena/Bayó/Baselga/Rodríguez Jódar/Superfo), ULAplus palette, multi-machine framework (up to 9 cores incl. SAM Coupé, Jupiter ACE, ColecoVision), optional ESP-12 WiFi |
| 7 | [karabas.md](karabas.md) | Karabas family (2018+): three open-source Z80 + Altera MAX II CPLD clones — Karabas 128 (EPM240, Sinclair 128K exact), Karabas Pro (EPM570, Pentagon 128 + turbo/SD/VGA), Peridot (EPM1270, Karabas Pro + WiFi/RTC/GPIO) |

See [PLAN.md](../../PLAN.md) for the full article catalog.
