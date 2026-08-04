[← Home](../../README.md) · [New Gen Hardware](README.md) · [ZX Evolution](zx_evo.md)

# TS-Conf — The ZX Evolution's Enhanced Video Firmware

**TS-Conf** is an alternative **firmware configuration** for the ZX Evolution, designed by the **tslabs team** (Aleksandr Zhuravlev / `tsl`, hosted at [github.com/tslabs/zx-evo](https://github.com/tslabs/zx-evo)). Where the default [BaseConf](baseconf.md) focuses on Pentagon 1024 compatibility, TS-Conf focuses on **enhanced video hardware**: hardware sprites, a tilemap engine, 512 KB of dedicated VRAM, per-scanline palettes, a DMA controller, and a turbo mode. It is the **Russian-scene equivalent of the ZX Spectrum Next's enhanced video stack** — Layer 2, sprites, tilemap, copper, and DMA — delivered as a firmware swap rather than new hardware.

For software developers, TS-Conf is the target for **new Russian Spectrum software** that wants modern graphics without leaving the ZX Evolution ecosystem. It is **not binary-compatible** with Pentagon software (it adds entirely new hardware features), but it coexists with BaseConf — the same physical ZX Evolution board can run either, switched by reflashing the CPLD bitstream.

> [!NOTE]
> This article covers TS-Conf as a **programmer-visible configuration** — its sprite engine, tilemap, VRAM layout, and ports. For the underlying ZX Evolution hardware, see [zx_evo.md](zx_evo.md). For the default Pentagon-compatible firmware, see [baseconf.md](baseconf.md).

---

## Why TS-Conf Exists

By 2010, the Russian Spectrum scene faced a choice:

1. **Stay on Pentagon-class hardware** (BaseConf) and keep writing cycle-exact code with software sprites and attribute-based color — limiting what new software could achieve.
2. **Migrate to the Western ZX Spectrum Next** (released 2017) — abandoning the Russian software ecosystem and TR-DOS conventions.
3. **Add enhanced video to the ZX Evolution itself** via a new firmware configuration.

TS-Conf is path 3. It is the answer to: *"What would the Russian Spectrum look like if we added hardware sprites and a tilemap, but kept the TR-DOS / Pentagon / Russian-scene conventions?"* The result is a firmware that has inspired a small but vibrant scene of TS-Conf-targeted games and demos.

### TS-Conf vs BaseConf — At a Glance

| Feature | BaseConf | TS-Conf |
|---|---|---|
| **Compatibility target** | Pentagon 1024 | New TS-Conf-specific software |
| **Sprites** | None (software only) | **Hardware sprites — up to 85 per scanline** |
| **Sprite sizes** | N/A | **8×8 up to 64×64 pixels** (selectable) |
| **Sprite planes** | N/A | **Up to 3 sprite planes** (parallel rendering) |
| **Tilemap** | Standard Spectrum screen | **Hardware tilemap with 2 tile planes**, 8×8 tiles |
| **Pixel resolutions** | 256×192 | **256×192, 320×200, 320×240, 360×288**, up to **720×288 hi-res** |
| **Color depth** | 8 colors (attribute) | **16 or 256 indexed colors per pixel** |
| **Palette** | Hard-wired | **Programmable CRAM, RGB555, 256 entries** |
| **Per-scanline palettes** | No | **Yes** — up to 16 sprite palettes + 4 tile palettes per line |
| **VRAM** | Shares main RAM | **Dedicated graphics memory** (up to 4 MB addressing) |
| **DMA** | No | **Full DMA controller** (DRAM-to-Device, Device-to-DRAM, DRAM-to-DRAM) |
| **CPU cache** | No | **512 bytes zero-wait-state cache** (for 14 MHz mode) |
| **Interrupt sources** | Frame only | **Frame + Line + DMA** (separate IM2 vectors) |
| **Turbo mode** | 3.5 / 7 / 14 MHz | **3.5 / 7 / 14 MHz** (same) |
| **Text mode** | No | **Yes** — loadable font + hardware vertical scroll |
| **Existing software** | Runs unmodified | **Requires TS-Conf-aware code** |

> [!IMPORTANT]
> TS-Conf is **not a runtime mode** — switching between BaseConf and TS-Conf requires **reflashing the CPLD bitstream** (or loading a different bitstream from SD card on later ZX Evolution revisions). It is not a software switch; the machine boots into one configuration and stays there until reboot. This is fundamentally different from the ZX Spectrum Next's runtime mode switching.

---

## TS-Conf Hardware Features

### Hardware Sprites

TS-Conf's sprite engine is **significantly more capable than commonly documented**. The official specification (from the tslabs/zx-evo repository) lists the maximum capacity:

| Feature | TS-Conf | ZX Spectrum Next |
|---|---|---|
| **Sprite size** | **8×8 up to 64×64 pixels** (any power of 2 in between) | 16×16 (fixed) |
| **Sprites per scanline** | **Up to 85** (not 32 as often cited) | 64 |
| **Sprite planes** | **Up to 3 planes** rendered in parallel | 1 (with layer priority) |
| **Patterns** | Stored in dedicated VRAM, bank-switched | 64 (4-bit) or 32 (8-bit) |
| **Color depth** | **16 or 256 colors per pixel** (mode-dependent) | 4-bit or 8-bit per sprite |
| **Palettes per scanline** | **Up to 16** sprite palettes | Limited by NextReg palette entries |
| **Per-sprite features** | X/Y mirror, palette offset, per-plane priority | Mirror, rotate 90°, palette offset, type |
| **Collision detection** | Yes | Yes |

Sprites are stored in dedicated VRAM and fetched independently of main RAM — there is **zero additional CPU contention** from the sprite engine. The base frame timing does not change (still Pentagon's 71,680 T-states, 320 lines, 48.83 Hz, no contention).

### Tilemap and Graphic Planes

TS-Conf supports **up to 2 independent tile planes** (tile plane 0 and tile plane 1), each with its own tile patterns, scroll offset, and palette. This enables foreground/background separation without sprite usage.

| Feature | TS-Conf | ZX Spectrum Next |
|---|---|---|
| **Tile planes** | **2** (parallel rendering) | 1 |
| **Tile size** | **8×8 pixels** (fixed) | 8×8 pixels (fixed) |
| **Patterns** | 256 entries per plane | 256 entries |
| **Color depth** | **16 or 256 colors per pixel** | 4-bit or 8-bit per pixel |
| **Palettes per scanline** | **Up to 4 palettes per tile plane** | Limited by NextReg palette entries |
| **Per-tile features** | Palette offset, mirror X/Y | Palette offset, mirror X/Y, priority bit |
| **Hardware scrolling** | Yes — X and Y, per plane | Yes |

### Multiple Pixel Resolutions

Unlike BaseConf (which is locked to the standard 256×192), TS-Conf supports **four standard pixel resolutions** plus a hi-res mode, selectable via the `RRES[1:0]` bits of the `VConfig` register:

| `RRES[1:0]` | Pixel area | Border layout | Typical use |
|---|---|---|---|
| `00` | **256×192** (standard ZX) | 48 + 48 line / 52 + 52 pixel borders | Compatibility mode |
| `01` | **320×200** | 44 + 44 line / 20 + 20 pixel borders | Most TS-Conf games and demos |
| `10` | **320×240** | 24 + 24 line / 20 + 20 pixel borders | Full-resolution arcade-style games |
| `11` | **360×288** (full visible area) | 0 border | Demos with edge-to-edge graphics |
| hi-res | **Up to 720×288** | N/A | Text-heavy applications, 80-column modes |

### Four Graphic Modes

The `VM[1:0]` bits of `VConfig` select one of four pixel-rendering modes within the active area:

| `VM[1:0]` | Mode | Color depth |
|---|---|---|
| `00` | **ZX** (classic attribute mode) | 8 colors per 8×8 attribute cell |
| `01` | **16c** (16 colors per pixel) | 16 indexed colors per pixel |
| `10` | **256c** (256 colors per pixel) | 256 indexed colors per pixel |
| `11` | **Text** (loadable font) | Per-character attribute, hardware vertical scroll |

### Programmable CRAM — RGB555 Palette

The Color RAM (**CRAM**) is a dedicated 256-entry palette table, with each entry holding a **15-bit RGB555 color** (5 bits red, 5 bits green, 5 bits blue). This gives 32,768 possible colors per palette entry, with 256 entries active simultaneously. The CRAM can be modified on the fly — including **per-scanline palette swaps** — by writing to the scanline-indexed palette table in VRAM.

### DMA Controller

TS-Conf includes a **full DMA controller** — a feature often missing from Western summaries. The DMA supports three transfer modes:

- **DRAM-to-Device** — copy from main RAM to a peripheral port (e.g., streaming audio to a DAC)
- **Device-to-DRAM** — capture from a peripheral into RAM (e.g., sampling, network packets)
- **DRAM-to-DRAM** — fast block copies within main RAM (e.g., blitting graphics, double-buffer swaps)

DMA transfers run independently of the CPU. When a transfer completes, the DMA controller raises an **interrupt** (vector `#FB` in IM2 mode), allowing the CPU to start the next transfer immediately. This is critical for streaming audio and for fast screen updates.

> [!WARNING]
> DMA transfers bypass the 512-byte CPU cache. After any DRAM-to-DRAM DMA that touches cached windows, the programmer must **invalidate the cache** by writing 512 bytes to any sequential address (e.g., `LDIR` 512 bytes from `#FE00` to `#FE00`). Failure to do so returns stale cached data on subsequent reads.

### Per-Scanline Palettes

TS-Conf's most distinctive feature is its **per-scanline palette** — every scanline can have its own palette, without needing a copper-like coprocessor. This is achieved by storing palettes in a dedicated scanline-indexed table in VRAM: palette for scanline N is read from a fixed address indexed by N.

This is structurally simpler than the Next's copper (which requires programming a sequence of `WAIT` + `MOVE` instructions), but less flexible — you can change palettes per scanline, but you cannot change other registers (sprite positions, layer enables, scroll offsets).

### 4 MB RAM Addressing and Memory Mapping

TS-Conf can address up to **4096 KB (4 MB) of RAM** plus **512 KB of ROM**, far beyond BaseConf's 1024 KB. The 16-bit Z80 address space is divided into **four programmable 16 KB windows**, each with its own page register:

| CPU window | Address range | Page register | Default page | R/W |
|---|---|---|---|---|
| 0 | `#0000`–`#3FFF` | `Page0` | `#00` (ROM or RAM) | W |
| 1 | `#4000`–`#7FFF` | `Page1` | `#05` | W |
| 2 | `#8000`–`#BFFF` | `Page2` | `#02` | R/W |
| 3 | `#C000`–`#FFFF` | `Page3` | `#00` | R/W |

The Pentagon-128 standard `#7FFD` port is supported for compatibility, with four paging modes (`LCK128[1:0]` bits of `MemConfig`):

| `LCK128[1:0]` | Mode | Behavior |
|---|---|---|
| `00` | 512 KB | `Page3[4:0]` = `#7FFD[7:6]` + `#7FFD[2:0]` |
| `01` | 128 KB | `Page3[2:0]` = `#7FFD[2:0]` (standard Pentagon-128) |
| `10` | Auto | Long addressing (`out (c),a`) → 512 KB; short addressing (`out (#FD),a`) → 128 KB |
| `11` | 1024 KB | `Page3[5:0]` = `#7FFD[5]` + `#7FFD[7:6]` + `#7FFD[2:0]` (Pentagon-1024 standard) |

### Dedicated Graphics Memory

Sprites, tilemap, palettes, and tile/sprite patterns are stored in dedicated graphics memory, accessed via a memory-mapped file mechanism (`FMAddr` register). This separates graphics data from main RAM — even though both ultimately live in the same 4 MB physical RAM chip, the TS-Conf hardware arbitrates access so that the video circuit never stalls the CPU. This is conceptually similar to the Next's dedicated Layer 2 and sprite memory.

---

## TS-Conf Port Map

TS-Conf uses a **different port layout** from BaseConf — the enhanced video features require their own ports, which would conflict with Pentagon ports if placed in the standard addresses.

| Port | Function |
|---|---|
| `#00AF` | Sprite/tilemap configuration register (write) |
| `#01AF` | Sprite pattern upload |
| `#02AF` | Tile pattern upload |
| `#03AF` | Tilemap data upload |
| `#04AF` | Palette upload |
| `#05AF`–`#07AF` | Sprite attribute, position, and feature upload |
| `#XXAF` (extended) | Additional TS-Conf configuration ports |

> [!WARNING]
> TS-Conf's port layout is **not compatible** with Pentagon software — a Pentagon program that writes to `#00AF` for an unrelated reason will corrupt TS-Conf's sprite configuration. TS-Conf requires **TS-Conf-aware software**.

The exact port layout has minor variations across TS-Conf revisions; the [official TS-Conf documentation](https://github.com/ts-conv) is the canonical source.

---

## TS-Conf Programming Model

### Initialization

A TS-Conf program starts by initializing the enhanced video hardware:

```z80
ts_conf_init:
        ; 1. Enable TS-Conf mode (the firmware is already loaded — this is a runtime config)
        ld  bc, #00AF
        ld  a, #01              ; enable sprites + tilemap
        out (c), a
        
        ; 2. Upload tile patterns to VRAM
        ld  hl, tile_pattern_data
        ld  de, 16384           ; 256 patterns × 64 bytes (8-bit) = 16 KB
        call upload_tile_patterns
        
        ; 3. Upload sprite patterns to VRAM
        ld  hl, sprite_pattern_data
        ld  de, 8192            ; 64 patterns × 128 bytes (16-color) = 8 KB
        call upload_sprite_patterns
        
        ; 4. Initialize the tilemap grid
        ld  hl, level_data
        call upload_tilemap
        
        ; 5. Configure the palette (per-scanline or single)
        ld  hl, palette_data
        call upload_palette
        ret
```

### Sprite Drawing

TS-Conf sprites are configured via attribute records, similar to the Next but with a different byte layout:

```z80
; Place a 16×16 sprite at (D, E) using pattern B
place_sprite:
        ld  c, #05AF            ; sprite attribute port
        ld  a, d                ; X coordinate
        out (c), a
        ld  a, e                ; Y coordinate
        out (c), a
        ld  a, b                ; pattern number
        out (c), a
        ld  a, %00010000        ; 16×16 size, no mirror, palette 0
        out (c), a
        ret
```

The exact byte sequence varies by TS-Conf revision; see the TS-Conf reference for the authoritative layout.

### Tilemap Scrolling

The tilemap's X/Y scroll position is set via dedicated ports:

```z80
scroll_tilemap:
        ld  bc, #00AF           ; scroll X port (example)
        ld  a, scroll_x
        out (c), a
        ld  bc, #01AF           ; scroll Y port (example)
        ld  a, scroll_y
        out (c), a
        ret
```

As with the Next, scrolling is **hardware-accelerated** — writing a new offset shifts the tilemap on the next frame with zero CPU cost.

---

## TSR Drivers — The Friendly API

For developers who do not want to write directly to TS-Conf's ports, the community provides **TSR (Terminate-and-Stay-Resident) drivers** — small programs that load at boot time and expose a friendly API via RST calls or function-dispatch tables.

| Driver | Function |
|---|---|
| **TSFDRV** | File I/O on SD card (FAT16/FAT32) |
| **TSGUI** | Graphics primitives (line, rectangle, sprite blit) |
| **TSFNT** | Font rendering (8×8, 8×16 proportional) |
| **TSBDOS** | TR-DOS-compatible disk access |

Using TSR drivers makes TS-Conf code more portable (it can run on any TS-Conf machine with the driver loaded) and dramatically reduces development time. The drivers are typically loaded by the boot ROM at startup, before the user's program runs.

---

## TS-Conf Software Ecosystem

TS-Conf has a small but active software ecosystem, primarily games and demos:

- **Platformers** with smooth hardware scrolling — the tilemap and sprites make these much easier to write than on the standard Pentagon
- **Shoot-em-ups** with multiple simultaneous sprites — the hardware sprite engine eliminates the CPU cost of software sprite rendering
- **Demos** with per-scanline palette effects — the per-scanline palette feature enables gradient skies, sunset effects, and water ripples without copper programming
- **Ported games** — some Western games have been re-coded for TS-Conf, taking advantage of the enhanced hardware

The TS-Conf scene is concentrated in Russia and the Russian-speaking diaspora. Documentation is primarily in Russian; English-language resources are growing but still limited compared to the ZX Spectrum Next's ecosystem.

---

## TS-Conf vs ZX Spectrum Next

| Aspect | TS-Conf | ZX Spectrum Next |
|---|---|---|
| **Hardware base** | ZX Evolution (real Z80 + CPLD) | Dedicated FPGA board |
| **Compatibility target** | Pentagon + new TS-Conf software | 48K / 128K / Pentagon + new Next software |
| **Mode switching** | **Firmware reflash** (requires reboot) | Runtime (NextReg write) |
| **Sprites per scanline** | **Up to 85** | 64 |
| **Sprite sizes** | **8×8 up to 64×64** | 16×16 (fixed) |
| **Sprite planes** | **3** | 1 (with priority) |
| **Tilemap planes** | **2** (parallel rendering) | 1 |
| **Tilemap resolution** | Variable (256×192 up to 360×288, hi-res 720×288) | 40×32 (320×256) or 80×32 (640×256) |
| **Per-scanline palettes** | Yes (dedicated CRAM table) | Yes (via copper) |
| **Palette color depth** | **RGB555** (32,768 colors) | RGB888 (16M colors) |
| **Copper** | No | Yes |
| **DMA** | **Yes** (DRAM-to-Device, Device-to-DRAM, DRAM-to-DRAM) | Yes |
| **CPU cache** | **512 bytes** (for 14 MHz mode) | No |
| **Interrupt sources** | Frame + Line + DMA (IM2 vectors) | Frame + line + UART + DMA |
| **Text mode** | **Yes** (loadable font + vertical scroll) | Limited |
| **Documentation language** | Primarily Russian | Primarily English |
| **Software library** | Russian scene | Western scene |

TS-Conf and the Next solve the same problem (modern graphics for the Spectrum) but with different trade-offs. TS-Conf is **denser in sprite/tile capacity** (more sprites per line, more planes, larger sprites) and adds a CPU cache for 14 MHz mode, but lacks the Next's **copper coprocessor** (which can change any register on any scanline, not just palettes) and lacks runtime mode switching. The Next is more flexible overall; TS-Conf is more focused on raw 2D graphics throughput.

---

## Cross-References

- [ZX Evolution hardware platform](zx_evo.md) — physical board that TS-Conf runs on
- [BaseConf firmware](baseconf.md) — the default Pentagon-compatible firmware
- [ZX Evolution FPGA internals](../../11_emulation/fpga/zxevo.md) — CPLD design, bitstream architecture
- [ZX Spectrum Next](zx_next.md) — the Western equivalent
- [Next sprites](zx_next.md#hardware-sprites) — comparable sprite engine (different specs)
- [Next tilemap](zx_next.md#hardware-tilemap) — comparable tilemap engine
- [Next copper](zx_next.md#the-copper-coprocessor) — the Next's per-scanline register mechanism (TS-Conf uses palette tables instead)
- [Pentagon 128](../clones/pentagon.md) — TS-Conf's compatibility baseline

---

## References

- **TS-Conf official documentation** ([GitHub: tslabs/zx-evo — `pentevo/docs/TSconf/tsconf_en.md`](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/TSconf/tsconf_en.md)) — authoritative port and register reference, maintained by the tslabs team
- [Aleksandr Zhuravlev (`tsl`) TS-Conf pages](https://zxevo.ru/) — design notes and programming tutorials (Russian)
- **NedoPC forum** ([nedopc.org](http://nedopc.org/zxevo/)) — TS-Conf-specific threads, software releases, and BaseConf/TS-Conf bitstream downloads
- **[zx-pk.ru](https://zx-pk.ru) forum** — *TS-Conf* subforum with driver documentation and example programs (Russian)
- [TS-Conf software archive](https://zxevo.ru/) — games, demos, and utilities written specifically for TS-Conf
- **Russian demoscene archives** — TS-Conf-targeted releases from CC Chaos Constructions, diHalt,FUNTOP, etc.
- **[zxevo.ru](https://zxevo.ru) wiki** — ZX Evolution community wiki with TS-Conf programming guides (Russian)
- **ZEsarUX emulator** ([GitHub: chernandezba/zesarux](https://github.com/chernandezba/zesarux)) — has a TS-Conf machine mode for development testing without real hardware
- [Unreal Speccy emulator](https://sdkcad.free.fr/) — alternate TS-Conf emulation target
