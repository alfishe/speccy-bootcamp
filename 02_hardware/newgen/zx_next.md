[← Home](../../README.md) · [New Gen Hardware](README.md)

# ZX Spectrum Next — The Modern FPGA Spectrum

The **ZX Spectrum Next** (2017–2020) is a modern FPGA-based Spectrum-compatible home computer, designed by a UK-Brazilian team led by **Jim Bagley**, **Victor Trucco**, **Henrique Oliviéri**, and **Fabio Belavenuto**, with the ROM/OS work by **Garry Lancaster**. It is the most commercially successful modern Spectrum: a desktop machine in a Spectrum-style case with a real keyboard, FPGA core, and a stack of hardware features — Layer 2 256-color graphics, hardware sprites, tilemap, copper coprocessor, DMA, 28 MHz CPU, 2 MB RAM — none of which existed on any 1980s Spectrum.

For software developers, the Next is **the only Spectrum where a BASIC programmer can write a smooth-scrolling hardware-sprite game without dropping to assembly**. It is also fully binary-compatible with the entire 48K/128K/Pentagon software library: classic software runs without modification, with optional contention emulation so even cycle-exact demos work.

> [!NOTE]
> This article is the **hardware platform overview** — what the Next is, its physical hardware, its layer stack, and the NextReg mechanism. For deep dives:
> - Memory map and I/O port architecture → [memory_and_io_next.md](../../05_development/03_memory_and_io/memory_and_io_next.md)
> - Frame timing, contention modes, copper timing → [video_frame_next.md](../../05_development/05_display_and_timing/video_frame_next.md)
> - NextZXOS operating system, NextBASIC, dot commands → [nextzxos.md](../../04_operating_systems/nextzxos.md)
> - Joystick system (dual Kempston, Mega Drive pads) → [zx_next_joystick.md](zx_next_joystick.md)
> - Layer 2, sprites, tilemap, copper, DMA programmers' references → linked articles below

---

## History and Hardware Revisions

The Next was funded via **Kickstarter** in 2016 (campaign by the "SpecNext" team). Two major hardware revisions shipped:

| Revision | Year | FPGA | Notes |
|---|---|---|---|
| **Issue 2 / 2A / 2B** (KS1) | 2017–2019 | **Xilinx Spartan-6** (XC6SLX16) | First backer shipment; the "black case" |
| **Issue 3** (KS2) | 2020 | **Xilinx Spartan-6** (XC6SLX16) | Minor PCB revision; the "white case" |
| **Issue 4 / 4A** (Accelerated) | 2022+ | **Artix-7** (XC7A15T) | Latest; faster FPGA, accommodates core 3.x firmware |

All revisions are **binary-compatible at the software level** — software written for KS1 runs unchanged on KS2/4. The only differences are analog (HDMI output quality) and the firmware version supported. Today (2024), the **Issue 4** is the only revision still in production, available from **Pin Solutions** (UK) and various retro-computing retailers.

---

## Physical Architecture

| Component | Specification |
|---|---|
| **Case** | Spectrum-style desktop case with built-in rubber-key or membrane keyboard (issue-dependent) |
| **CPU** | **Z80N** — an FPGA soft-core with the standard Z80 instruction set **plus** Next-specific extensions (`LDPIR`, `SWAPNIB`, `MIRROR`, `PIXELDAT`, `NEXTREG` access instructions) |
| **CPU clock** | **3.5 / 7 / 14 / 28 MHz** — runtime-switchable via NextReg `0x07` |
| **RAM** | **2 MB** static RAM (vs. 48K–128K on classic Spectrums) |
| **ROM** | **512 KB** flash, holds NextZXOS + 48K/128K editor ROMs + TR-DOS-compatible routines |
| **Video output** | **HDMI** + VGA + composite (all simultaneously) |
| **Storage** | **MicroSD card slot** (SPI-mode, FAT32) |
| **Audio** | **Internal speaker** + AY-3-8912 (two chips, 6 channels) + 8-channel DMA-driven PCM + beeper |
| **Joystick** | **Two DE-9 ports** — individually mode-switchable per port (Kempston ×2, Sinclair, Cursor, Mega Drive) |
| **Expansion** | **Raspberry Pi Zero** slot (accelerator), **ESP-12 WiFi** module, **2×20-pin GPIO header** |
| **Accelerator** | **Pi Zero** (optional) — runs a faster Z80 emulator at >100 MHz effective clock |

The case is designed to evoke the original Sinclair 48K rubber-key form factor (Issue 2) or the Spectrum+ membrane-key form factor (Issue 3+). The keyboard matrix is **Sinclair-compatible** so original software reads it correctly.

---

## The Layer Stack

The Next's video hardware presents a **stack of independent layers** that are composited in a fixed priority order:

| # | Layer | Resolution | Colors | Priority |
|---|---|---|---|---|
| 1 | **ULA screen** (standard Spectrum) | 256×192 | 8×2 (attribute-based) | Lowest |
| 2 | **LoRes** (320×192, optional) | 320×192 | 8×8 attribute blocks | Above ULA |
| 3 | **Layer 2** (256-color framebuffer) | 256×192 / 320×256 | 256 from 24-bit RGB palette | Above LoRes |
| 4 | **Tilemap** (hardware tiles) | 40×32 or 80×32 tiles | 256 from palette | Above Layer 2 |
| 5 | **Hardware sprites** (up to 64 per scanline) | 16×16 each | 256 from palette | Above tilemap |
| 6 | **Border** (programmable) | Frame border | 256 from palette | Highest (covers everything) |

Each layer can be **enabled, disabled, and prioritized** via NextReg registers. The compositor runs entirely in the FPGA in parallel with CPU execution — there is **zero CPU cost** for layer compositing (beyond the initial memory writes to set up each layer).

### The Layer-Selection NextReg

The most fundamental video NextReg is `0x15` (**Layer 2 shadow, LoRes, tilemap, sprites, layer priority**). It contains one-bit enable flags for each layer and the priority between Layer 2 and the tilemap:

| Bit | Function |
|---|---|
| 0 | Enable Layer 2 (1 = on) |
| 1 | Enable tilemap (1 = on) |
| 2 | Enable sprites (1 = on) |
| 3 | Select LoRes mode (1 = on) |
| 4 | Layer 2 / tilemap priority bit (1 = tilemap over Layer 2) |
| 5–7 | Reserved |

> [!TIP]
> For a first graphics program, enable **only Layer 2** (`NextReg 0x15 = 0x01`). This gives you a 256-color framebuffer with no attribute constraints and no need to understand sprites or tilemaps. See [zx_next_layer2.md](zx_next_layer2.md) for the programming guide.

Each layer has its own dedicated article:

- [**Layer 2**](zx_next_layer2.md) — 256-color 8bpp framebuffer, bank-switching, palette
- [**Sprites**](zx_next_sprites.md) — up to 64 sprites/scanline, pattern/attribute upload, collision
- [**Tilemap**](zx_next_tilemap.md) — 40×32 or 80×32 hardware tiles, scrolling
- [**Copper**](zx_next_copper.md) — programmable scanline coprocessor for raster effects

---

## The NextReg System

The Next's hardware features are configured via **NextReg registers** — a flat 256-register address space accessed through a two-port I/O protocol. This is the **single most important programmer interface** on the machine: nearly every hardware feature is enabled, tuned, or queried through a NextReg.

### NextReg Access Ports

| Port | Direction | Function |
|---|---|---|
| `#243B` | Write | **Register select** — write the register number (0x00–0xFF) here |
| `#253B` | Read/Write | **Register data** — read or write the selected register's value |

Example — write the value `0x01` to NextReg `0x15` (enable Layer 2):

```z80
        ld  bc, #243B
        ld  a, #15          ; NextReg 0x15 = Layer 2 / sprites / tilemap config
        out (c), a
        ld  bc, #253B
        ld  a, #01          ; enable Layer 2, disable others
        out (c), a
```

The Z80N instruction set also has dedicated `NEXTREG` instructions that combine the two-port sequence into a single instruction — see [memory_and_io_next.md](../../05_development/03_memory_and_io/memory_and_io_next.md) for the full Z80N extension set.

### Most-Used NextReg Quick Reference

| Reg | Name | Function |
|---|---|---|
| `0x00` | Machine ID | Read-only — returns hardware revision (e.g. `0x0A` = Issue 4) |
| `0x05` | Peripheral 1 | Joystick 1/2 mode, 50/60 Hz, scandoubler — see [zx_next_joystick.md](zx_next_joystick.md) |
| `0x06` | Peripheral 2 | Kempston mouse, Multiface, divMMC, scan doubler |
| `0x07` | Turbo mode | CPU speed: `0` = 3.5 MHz, `1` = 7 MHz, `2` = 14 MHz, `3` = 28 MHz |
| `0x08` | Peripheral 3 | DAC A/B/C/D enables, SpecDrum, Timex modes |
| `0x0A` | Layer 2 RAM page | Selects which 16 KB bank is paged at `#0000–#3FFF` for Layer 2 writes |
| `0x12` | Layer 2 offset X | Layer 2 horizontal scroll offset |
| `0x13` | Layer 2 offset Y | Layer 2 vertical scroll offset |
| `0x15` | Layer 2 / sprites / tilemap enable | See table above |
| `0x40` | Palette index | Write-only — select palette entry for write |
| `0x41` | Palette value | Write the 8-bit palette value (in palette write mode) |
| `0x42` | Palette value (16-bit, RGB565) | Write the upper 8 bits of a 16-bit palette entry |
| `0x50` | Sprite system | Sprite enable, pattern/attribute upload protocol |
| `0x6B` | DMA port | Direct DMA register access (legacy; main DMA port is `#6B`/`#7B`) |
| `0x70` | Tilemap base address | High byte of tilemap RAM base |
| `0x71` | Tilemap attribute base | High byte of attribute RAM base |

For the full 256-register list, see the [official Next documentation](https://www.specnext.com/tbblue-io-port-system/) or [io_port_map.md](../../10_references/io_port_map.md).

---

## I/O Port Summary

Beyond the NextReg system, the Next exposes hardware features through traditional I/O ports. The complete port map is in [memory_and_io_next.md](../../05_development/03_memory_and_io/memory_and_io_next.md); the most important ports:

| Port | Function |
|---|---|
| `#FE` | Standard Spectrum ULA port — border, beeper, MIC, keyboard (compatibility) |
| `#1F` / `#37` | Kempston joystick 1 / 2 (see [zx_next_joystick.md](zx_next_joystick.md)) |
| `#FFFD` / `#BFFD` | AY-3-8912 register select / data (first AY) |
| `#1FFD` | +2A/+3 paging compatibility port |
| `#7FFD` | 128K paging compatibility port |
| `#123B` | Layer 2 bank select (16 KB bank at `#0000–#3FFF`) |
| `#243B` / `#253B` | NextReg select / data |
| `#303B` / `#55` / `#57` | Sprite pattern/attribute upload (see [zx_next_sprites.md](zx_next_sprites.md)) |
| `#6B` / `#7B` | DMA register select / data (see [zx_next_dma.md](zx_next_dma.md)) |
| `#60` / `#61` | Copper instruction write (low/high byte) (see [zx_next_copper.md](zx_next_copper.md)) |

The Next's port decoding is deliberately **complex** to support all the classic modes — for the precise port decoding logic (full vs partial, address mask conventions), see [memory_and_io_next.md](../../05_development/03_memory_and_io/memory_and_io_next.md).

---

## Compatibility Modes

The Next can impersonate four classic machines via the **timing-mode NextReg `0x22`** (and its associated memory-map NextRegs). Switching modes at runtime lets a single binary support multiple Spectrums:

| Mode | Memory map | Contention | Frame |
|---|---|---|---|
| **48K** | ROM + 16K contended + 32K uncontended | Yes (`#4000`–`#7FFF`) | 69,888 T-states, 312 lines, 50.08 Hz |
| **128K / +2** | `#7FFD` paging | Yes (banks 1/3/5/7) | 70,908 T-states, 311 lines, 50.02 Hz |
| **+2A / +3** | `#7FFD` + `#1FFD` paging | Yes (split banks) | 70,908 T-states, 311 lines, 50.02 Hz |
| **Pentagon** | `#7FFD` + `#DFFD`/`#EFF7` paging | **No** | 71,680 T-states, 320 lines, 48.83 Hz |

Classic software that runs on any of these machines will run on the Next. **Contention is emulated** in 48K/128K/+3 modes — even cycle-exact demos work.

> [!WARNING]
> The Pentagon mode is **not binary-compatible** with original Sinclair 128K software that depends on contention timing. Software must be specifically compiled for Pentagon (or written to handle the difference). See [video_frame_next.md](../../05_development/05_display_and_timing/video_frame_next.md) for the full timing comparison.

---

## The Z80N CPU

The Next's CPU is not a standard Z80 — it is a **Z80N**, an FPGA soft-core with the standard Z80 instruction set **plus** Next-specific extensions. The most important extensions:

| Instruction | Mnemonic | Function |
|---|---|---|
| `ED 30 nn` | `NEXTREG nn` | Write accumulator to NextReg `nn` (single instruction, vs 2-port sequence) |
| `ED 31 nn mm` | `NEXTREG nn, mm` | Write immediate `mm` to NextReg `nn` |
| `ED 23` | `SWAPNIB` | Swap high/low nibbles of A |
| `ED 24` | `MIRROR` | Mirror (bit-reverse) the bits of A |
| `ED 8A` | `PIXELDAT` | Read a Layer 2 pixel at DE into A |
| `ED 90` | `LDIX` | Like `LDIR`, but skips bytes equal to A (transparency-aware copy) |
| `ED 91` | `LDWX` | Like `LDIX`, but copies with a byte mask from another register |
| `ED 92` | `LDPIR` | Pixel-aware LDIR for fast block fill with transparency |
| `ED 93` | `JP (C)` | Jump to address held at `(HL)` if C matches — useful for jump tables |

The Z80N extensions are **upward-compatible** — code assembled for a standard Z80 runs on the Next unchanged. The extensions are an opt-in convenience for fast graphics and NextReg access. See [memory_and_io_next.md](../../05_development/03_memory_and_io/memory_and_io_next.md) for the full opcode table and cycle timings.

---

## Software Development Entry Points

The Next offers three primary ways to develop software, in increasing order of capability:

### 1. NextBASIC (high-level, beginner)

NextBASIC is the Next's enhanced BASIC dialect, integrated with NextZXOS. It can drive Layer 2, sprites, tilemap, copper, and DMA directly from BASIC commands. Best for: educational programs, simple games, demos, and prototypes. See [nextzxos.md](../../04_operating_systems/nextzxos.md) for the NextBASIC command reference.

### 2. C with z88dk (medium-level, productivity)

The **z88dk** C compiler targets the Next natively, with library functions wrapping Layer 2, sprites, tilemap, copper, and DMA. Best for: games that need C-level structure, larger projects, cross-platform code. See [z88dk.md](../../09_toolchain/z88dk.md) for the toolchain.

### 3. Assembly with sjasmplus (low-level, performance)

The **sjasmplus** assembler is the canonical Next assembler. It supports the Z80N extension instructions and the Next's memory model directly. Best for: demoscene productions, cycle-exact code, performance-critical games. See the assembler's documentation at [z00m128/sjasmplus on GitHub](https://github.com/z00m128/sjasmplus).

### The Developer's Typical Workflow

1. **Code** in z80 assembly (sjasmplus) or C (z88dk), using the [NextReg access pattern](#the-nextreg-system) for hardware features.
2. **Test** in the [CSpect](../../11_emulation/software/cspect.md) emulator — Mike Dailly's reference emulator, fast iteration.
3. **Verify** on real hardware via SD card — for cycle-exact behavior, floating-bus quirks, and HDMI signal fidelity.
4. **Cross-reference** the official Next documentation at [zxnext.io](https://www.zxnext.io/) and [specnext.com](https://www.specnext.com/tbblue-io-port-system/) for the canonical register reference.

---

## Cross-References

### Layer/feature deep dives (in this directory)

- [Layer 2](zx_next_layer2.md) — 256-color 8bpp framebuffer, bank-switching, palette, shadow layer
- [Sprites](zx_next_sprites.md) — up to 64 sprites/scanline, pattern/attribute upload, priority, collision
- [Tilemap](zx_next_tilemap.md) — 40×32 or 80×32 hardware tiles, tile patterns, scrolling
- [Copper](zx_next_copper.md) — programmable scanline coprocessor for raster effects
- [DMA](zx_next_dma.md) — memory-to-memory, memory-to-I/O, I/O-to-I/O transfers
- [Joystick system](zx_next_joystick.md) — per-port mode selection, dual Kempston, Mega Drive pads

### Programming reference (in 05_development)

- [Next memory map and I/O ports](../../05_development/03_memory_and_io/memory_and_io_next.md) — full MMU, 8 KB paging, port decoding
- [Next video frame](../../05_development/05_display_and_timing/video_frame_next.md) — frame timing, contention modes, copper timing
- [z88dk toolchain](../../09_toolchain/z88dk.md) — C compiler targeting the Next

### OS and emulator coverage

- [NextZXOS](../../04_operating_systems/nextzxos.md) — operating system, NextBASIC, dot commands, function dispatch
- [CSpect emulator](../../11_emulation/software/cspect.md) — reference emulator for Next development
- [ZEsarUX emulator](../../11_emulation/software/zesarux.md) — alternative emulator with better WiFi simulation

### Hardware context

- [ZX Evolution](zx_evo.md) — the Russian equivalent (Pentagon-compatible FPGA Spectrum)
- [TS-Conf](ts_conf.md) — the Russian enhanced video mode (sprites/tilemap/512K VRAM)
- [ZX-Uno](zx_uno.md) — open-source FPGA Spectrum (smaller feature set than Next)
- [Original 48K](../original/zx_spectrum_16k_48k.md) — the Next's binary-compatibility target

---

## References

- **Official Next documentation** ([specnext.com](https://www.specnext.com/tbblue-io-port-system/)) — canonical NextReg and port reference
- **ZX Spectrum Next community site** ([zxnext.io](https://www.zxnext.io/)) — tutorials, software library, community forums
- **TBBlue I/O Port System documentation** — the NextReg register table maintained by the development team
- **NextZXOS source** ([GitHub](https://github.com/z00m128/NextZXOS)) — open-source firmware
- **The ZX Spectrum Next Register Reference** (community-maintained PDF) — printable NextReg quick reference
- **"ZX Spectrum Next Programming"** (various community tutorials at speccy.xyz/next) — beginner-friendly programming guides
- **sjasmplus assembler** ([GitHub: z00m128/sjasmplus](https://github.com/z00m128/sjasmplus)) — canonical Next assembler
- **Pin Solutions store** (pinsolutions.co.uk) — current Next hardware vendor (Issue 4)

