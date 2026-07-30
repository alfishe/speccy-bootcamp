[← Home](../../README.md) · [New Gen Hardware](README.md) · [ZX Evolution](zx_evo.md)

# TS-Conf — The ZX Evolution's Enhanced Video Firmware

**TS-Conf** is an alternative **firmware configuration** for the ZX Evolution, designed by **Aleksandr Zhuravlev** (`tsl`). Where the default [BaseConf](baseconf.md) focuses on Pentagon 1024 compatibility, TS-Conf focuses on **enhanced video hardware**: hardware sprites, a tilemap engine, 512 KB of dedicated VRAM, per-scanline palettes, and a turbo mode. It is the **Russian-scene equivalent of the ZX Spectrum Next's enhanced video stack** — Layer 2, sprites, and tilemap — delivered as a firmware swap rather than new hardware.

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
| **Sprites** | None (software only) | **Hardware sprites** (32 per scanline) |
| **Tilemap** | Standard Spectrum screen | **Hardware tilemap** (320×200 with 8×8 tiles) |
| **VRAM** | Shares main RAM | **512 KB dedicated VRAM** |
| **Per-scanline palettes** | No | **Yes** |
| **Turbo mode** | 3.5 / 7 / 14 MHz | **3.5 / 7 / 14 MHz** (same) |
| **Existing software** | Runs unmodified | **Requires TS-Conf-aware code** |

> [!IMPORTANT]
> TS-Conf is **not a runtime mode** — switching between BaseConf and TS-Conf requires **reflashing the CPLD bitstream** (or loading a different bitstream from SD card on later ZX Evolution revisions). It is not a software switch; the machine boots into one configuration and stays there until reboot. This is fundamentally different from the ZX Spectrum Next's runtime mode switching.

---

## TS-Conf Hardware Features

### Hardware Sprites

TS-Conf's sprite engine is more limited than the Next's but provides the same essential capability:

| Feature | TS-Conf | ZX Spectrum Next |
|---|---|---|
| **Sprite size** | 8×8 / 16×16 / 32×32 (selectable) | 16×16 (fixed) |
| **Sprites per scanline** | **32** | 64 |
| **Patterns** | 64 (typically) | 64 (4-bit) or 32 (8-bit) |
| **Color depth** | 16 colors per sprite (palette-indexed) | 4-bit or 8-bit per sprite |
| **Per-sprite features** | X/Y mirror, palette offset | Mirror, rotate 90°, palette offset, type |
| **Collision detection** | Yes | Yes |

Sprites are stored in dedicated VRAM and fetched independently of main RAM — there is **zero additional CPU contention** from the sprite engine. The base frame timing does not change (still Pentagon's 71,680 T-states, 320 lines, 48.83 Hz, no contention).

### Tilemap

TS-Conf's tilemap engine is comparable to the Next's, with slightly different specifications:

| Feature | TS-Conf | ZX Spectrum Next |
|---|---|---|
| **Grid size** | **40×25 tiles** (320×200 pixels) | 40×32 (320×256) or 80×32 (640×256) |
| **Tile size** | 8×8 pixels (fixed) | 8×8 pixels (fixed) |
| **Patterns** | 256 entries | 256 entries |
| **Color depth** | 16 colors per pixel | 4-bit or 8-bit per pixel |
| **Per-tile features** | Palette offset, mirror X/Y | Palette offset, mirror X/Y, priority bit |

The 40×25 grid (vs the Next's 40×32) reflects the Pentagon's 320-line frame, of which only ~200 lines are visible. The tilemap fits exactly within the visible area.

### Per-Scanline Palettes

TS-Conf's most distinctive feature is its **per-scanline palette** — every scanline can have its own palette, without needing a copper-like coprocessor. This is achieved by storing palettes in a dedicated scanline-indexed table in VRAM: palette for scanline N is read from a fixed address indexed by N.

This is structurally simpler than the Next's copper (which requires programming a sequence of `WAIT` + `MOVE` instructions), but less flexible — you can change palettes per scanline, but you cannot change other registers (sprite positions, layer enables, scroll offsets).

### 512 KB Dedicated VRAM

Sprites, tilemap, and palettes are stored in **512 KB of dedicated VRAM**, completely separate from main RAM. This is the same architectural pattern as the Next's sprite pattern memory — but on TS-Conf, the VRAM also holds the tilemap and palettes, making the 512 KB a unified graphics memory.

The VRAM is accessed via a **bank-switching scheme**: a 16 KB window of VRAM is paged into the Z80 address space at `#0000–#3FFF` (or another configurable window), and the programmer writes/reads sequentially. This is similar to the Next's Layer 2 banking.

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
| **Sprites per scanline** | 32 | 64 |
| **Tilemap** | 40×25 | 40×32 or 80×32 |
| **Per-scanline palettes** | Yes (dedicated table) | Yes (via copper) |
| **Copper** | No | Yes |
| **DMA** | No (CPU-driven) | Yes |
| **Documentation language** | Primarily Russian | Primarily English |
| **Software library** | Russian scene | Western scene |

TS-Conf and the Next solve the same problem (modern graphics for the Spectrum) but with different trade-offs. TS-Conf is **simpler** (no copper to program, no DMA, just sprites + tilemap + palettes), while the Next is **more powerful** (copper enables any register change per scanline, DMA enables fast block copies, runtime mode switching preserves compatibility).

---

## Cross-References

- [ZX Evolution hardware platform](zx_evo.md) — physical board that TS-Conf runs on
- [BaseConf firmware](baseconf.md) — the default Pentagon-compatible firmware
- [ZX Evolution FPGA internals](../../11_emulation/fpga/zxevo.md) — CPLD design, bitstream architecture
- [ZX Spectrum Next](zx_next.md) — the Western equivalent
- [Next sprites](zx_next_sprites.md) — comparable sprite engine (different specs)
- [Next tilemap](zx_next_tilemap.md) — comparable tilemap engine
- [Next copper](zx_next_copper.md) — the Next's per-scanline register mechanism (TS-Conf uses palette tables instead)
- [Pentagon 128](../clones/pentagon.md) — TS-Conf's compatibility baseline

---

## References

- **TS-Conf documentation** ([GitHub: ts-conv](https://github.com/ts-conv)) — official TS-Conf port and register reference
- **Aleksandr Zhuravlev's TS-Conf pages** — design notes and programming tutorials
- **NedoPC forum** — TS-Conf-specific threads, software releases
- **zx-pk.ru forum** — *TS-Conf* subforum with driver documentation and example programs
- **TS-Conf software archive** — games, demos, and utilities written specifically for TS-Conf
- **Russian demoscene archives** — TS-Conf-targeted releases from CC Chaos Constructions, diHalt, etc.
