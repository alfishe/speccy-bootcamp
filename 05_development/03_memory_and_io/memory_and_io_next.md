[← Home](../../README.md) · [Memory & I/O](README.md)

# ZX Spectrum Next — Memory Map and I/O Ports

The ZX Spectrum Next is a modern FPGA-based machine with a Z80N-enhanced CPU running at up to 28 MHz, **2 MB of RAM**, and a sophisticated MMU that maps memory in **8 KB pages** across four 8 KB slots. Unlike all classic Spectrums which use 16 KB banks, the Next uses fine-grained 8 KB paging that allows much more flexible memory layouts while maintaining backward compatibility with 48K, 128K, and Pentagon modes.

The Next also adds many new I/O ports for hardware features: Layer 2 graphics, sprites, tilemap, copper, DMA, SD card, WiFi, RTC, and more.

> [!NOTE]
> This article covers the **Next memory map and I/O port architecture**. For Layer 2, sprites, tilemap, and copper details, see the dedicated articles in [02_hardware/newgen/](../../02_hardware/newgen/). For I/O port decoding concepts, see [io_port_decoding.md](io_port_decoding.md).

---

## Memory Map — Compatibility Modes

The Next can emulate the memory maps of classic machines by switching between **timing modes**. In these modes, the MMU behaves like the original hardware:

### 48K Mode

```
#0000 - #3FFF    ROM (16 KB, from flash)
#4000 - #7FFF    Bank 5 (contended if contention emulation enabled)
#8000 - #BFFF    RAM (uncontended)
#C000 - #FFFF    RAM (uncontended)
```

Port `#FE` works exactly as on the original 48K. No paging ports are active.

### 128K Mode

```
#0000 - #3FFF    ROM bank 0 or 1 (switchable)
#4000 - #7FFF    Bank 5 (fixed)
#8000 - #BFFF    Bank 2 (fixed)
#C000 - #FFFF    Banks 0–7 (switchable via #7FFD)
```

`#7FFD`, `#FFFD`/`#BFFD` work as on the Sinclair 128K. Fully compatible.

### Pentagon Mode

Same as 128K mode but with Pentagon timing (no contention, different interrupt position). `#EFF7` extended paging is supported for 512K/1024K compatibility.

---

## Memory Map — Native Next Mode (2 MB MMU)

In native mode, the Next uses a **4-slot MMU** with **8 KB pages**:

```
Slot    Address range    Size    Default page    MMU register
──────────────────────────────────────────────────────────────────
0       #0000 - #1FFF    8 KB    ROM page 0      #FFFD (slot 0)
1       #2000 - #3FFF    8 KB    ROM page 1      #DFFD (slot 1)
2       #4000 - #5FFF    8 KB    RAM page 10     #BFFD (slot 2)
3       #6000 - #7FFF    8 KB    RAM page 11     #7FFD (slot 3)
4       #8000 - #9FFF    8 KB    RAM page 4      #3FFD (slot 4)
5       #A000 - #BFFF    8 KB    RAM page 5      #1FFD (slot 5)
6       #C000 - #DFFF    8 KB    RAM page 0      #FEFD (slot 6)
7       #E000 - #FFFF    8 KB    RAM page 1      #DFFD (slot 7) *
──────────────────────────────────────────────────────────────────
```

Wait — the actual Next MMU register map is:

```
MMU Slot Selection Ports:

Port    Slot    Address range
────────────────────────────────
#50     Slot 0  #0000–#1FFF
#51     Slot 1  #2000–#3FFF
#52     Slot 2  #4000–#5FFF
#53     Slot 3  #6000–#7FFF
#54     Slot 4  #8000–#9FFF
#55     Slot 5  #A000–#BFFF
#56     Slot 6  #C000–#DFFF
#57     Slot 7  #E000–#FFFF
────────────────────────────────────────

Each port selects which 8 KB page appears in that slot.
Value written: page number 0–255 → 256 × 8 KB = 2 MB addressable.

Bit 7 of the value:  0 = RAM page,  1 = ROM page
```

### 8 KB Page Mapping

```z80
; Map RAM page 20 into slot 6 (#C000–#DFFF)
LD   BC,#56           ; Slot 6 port
LD   A,20             ; RAM page 20
OUT  (C),A

; Map ROM page 2 into slot 0 (#0000–#1FFF)
LD   BC,#50           ; Slot 0 port
LD   A,%10000010      ; Bit 7=1 (ROM), page 2
OUT  (C),A
```

### 2 MB RAM Layout

The 2 MB RAM is divided into **256 pages of 8 KB**:

```
Pages 0–9:     System use (ROM workspace, NextZXOS, etc.)
Pages 10–11:   Bank 5 screen area (#4000–#7FFF in compatibility modes)
Pages 12–13:   Bank 2 area (#8000–#BFFF in compatibility modes)
Pages 14–127:  User RAM (general purpose)
Pages 128–255: Extended memory (bank-switched via MMU)
```

### Compatibility Mapping

When the Next enters a compatibility mode (48K/128K/Pentagon), the MMU is automatically configured to map the appropriate 8 KB pages into each slot to simulate the original 16 KB bank structure. The 16 KB `#7FFD` paging still works — the Next intercepts writes to `#7FFD` and remaps two 8 KB slots accordingly.

---

## Key I/O Ports — Next-Specific

The Next adds a large number of new ports. Here are the most important categories:

### Display Control

```
Port #12 (R/W):  Layer 2 bank select
Port #15 (W):    Sprite status / system control
Port #1B (W):    Palette control
Port #40–#43:    Layer 2 access window (#0000–#1FFF mapping)
Port #50–#57:    MMU slot selection (8 KB pages)
Port #68 (R/W):  Copper control
Port #6B (W):    Layer 2 secondary mapping
```

### Sprites

```
Port #55 (W):    Sprite attribute slot select (when in sprite port mode)
Port #57 (W):    Sprite pattern upload port
Port #15:        Sprite system enable/disable
```

For complete sprite programming, see [zx_next_sprites.md](../../02_hardware/newgen/zx_next_sprites.md).

### Copper

```
Port #60 (W):    Copper data (write copper instruction)
Port #61 (W):    Copper control (reset, run, stop)
```

The copper is a simple programmable sequencer that can write to any I/O port synchronized to the raster position. See [zx_next_copper.md](../../02_hardware/newgen/zx_next_copper.md).

### DMA

```
Port #6B (W):    DMA control register
Port #6C–#6F:    DMA source/destination/length
```

For DMA programming, see [zx_next_dma.md](../../02_hardware/newgen/zx_next_dma.md).

### Storage

```
Port #B3 (R/W):  SD card SPI data
Port #B7 (R/W):  SD card control
```

### System

```
Port #09 (R):    Machine ID (reads #08 for ZX Spectrum Next)
Port #0B (R):    FPGA version
Port #2425 (W):  Turbo mode (3.5 / 7 / 14 / 28 MHz)
Port #FE:        Legacy ULA port (border, EAR, keyboard) — fully compatible
```

---

## Quick Reference — Port Summary

```
Port    Function                                     Next specific
────────────────────────────────────────────────────────────────────
#FE     Border, EAR, keyboard                       Compatible (all modes)
#7FFD   128K-compatible paging                      Compatible (128K mode)
#FFFD   AY register select                          Compatible
#BFFD   AY register data                            Compatible
#50–57  MMU slot selection (8 KB pages)             YES — Next native
#09     Machine ID detection                        YES
#12     Layer 2 bank select                         YES
#15     Sprite control / system flags               YES
#40–43  Layer 2 access window                       YES
#60–61  Copper sequencer                            YES
#6B     DMA control                                 YES
#B3/B7  SD card SPI interface                       YES
#2425   Turbo speed select                          YES
────────────────────────────────────────────────────────────────────
```

---

## Cross-References

- **128K/+2 memory and ports** (baseline paging): [memory_and_io_128k.md](memory_and_io_128k.md)
- **Pentagon memory and ports** (compatibility mode): [memory_and_io_pentagon.md](memory_and_io_pentagon.md)
- **I/O port decoding** (partial decoding, masks): [io_port_decoding.md](io_port_decoding.md)
- **ZX Spectrum Next hardware**: [zx_next.md](../../02_hardware/newgen/zx_next.md)
- **Next sprites**: [zx_next_sprites.md](../../02_hardware/newgen/zx_next_sprites.md)
- **Next Layer 2**: [zx_next_layer2.md](../../02_hardware/newgen/zx_next_layer2.md)
- **Next copper**: [zx_next_copper.md](../../02_hardware/newgen/zx_next_copper.md)
- **Next DMA**: [zx_next_dma.md](../../02_hardware/newgen/zx_next_dma.md)
- **NextZXOS**: [nextzxos.md](../../04_operating_systems/nextzxos.md)
- **Official Next documentation**: [zxnext.io](https://www.zxnext.io/)
