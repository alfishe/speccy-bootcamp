[← Home](../../README.md) · [Clone Hardware](README.md)

# Kay 1024 — The Professional Soviet Spectrum: Nemo Bus, IDE, and the Cleanest Timing

The **Kay 1024** (Кэй, NEMO company, St. Petersburg, 1991–1998) is the Soviet Spectrum's **professional tier** — a high-end clone built for users who wanted more than the Pentagon's bare-bones hobbyist design could offer. Where the Pentagon was a minimal DIY machine, the Kay was a **factory-assembled computer** with a proper case, integrated disk drive, hard-disk support, and the cleanest video timing of any Soviet clone.

The Kay's defining characteristics — from a programmer's perspective — are: **48K-compatible timing** (69,888 T-states/frame, 312 scanlines, 50.08 Hz), **zero memory contention**, **1024K of RAM** with a different extended paging scheme than the Pentagon, and the **Nemo bus** — a proprietary expansion bus that became the foundation for an entire ecosystem of Russian peripherals.

> [!NOTE]
> This article covers the **hardware platform**. For the Kay's frame timing and how it compares to other clones, see [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md). For the broader clone timing landscape, see [clone_timing.md](clone_timing.md).

---

## The Nemo Bus — Kay's Expansion Foundation

The Kay's most important architectural feature is the **Nemo bus** — a 60-pin expansion bus that exposes the full Z80 bus plus additional signals for DMA-style peripherals and paged memory. The Nemo bus was designed by the Kay team (NEMO company) specifically for the Kay, but it became a **de facto standard** for high-end Soviet peripherals and was later adopted (with variations) by the Scorpion and ATM Turbo.

### Nemo Bus vs Spectrum Edge Connector

| Feature | Spectrum 48K edge connector | Kay Nemo bus |
|---|---|---|
| **Pin count** | 56 (2 × 28 PCB edge) | 60 (2 × 30 pin header) |
| **Bus signals** | Z80 A0–A15, D0–D7, control | Same + additional paging signals |
| **Power** | +5V, +9V, ±12V (issue-dependent) | +5V, +12V, −12V (regulated on-board) |
| **Video** | Analog Y/U/V to modulator | Digital RGB (TTL-level) + composite sync |
| **DMA support** | `/BUSRQ`, `/BUSACK` only | Full DMA handshake + wait-state generator |
| **Connector** | PCB edge (gold fingers) | Pin header (IDC connector) |

The Nemo bus's **digital RGB output** was a major advantage over the Spectrum's analog YUV. Peripherals could tap into the RGB signal directly (for genlocks, overlay graphics, or RGB-to-VGA converters) without decoding the analog video. This made the Kay the preferred platform for video overlay hardware and SVGA adapters.

### Nemo Bus Peripherals

The Nemo bus hosted a substantial peripheral ecosystem:

| Peripheral | Function | Notes |
|---|---|---|
| **Kay IDE controller** | ATA/IDE hard disk interface | Allowed connecting PC AT-style hard drives (typically 40–200 MB). Used the SM1840 or custom gate array for address decode. |
| **Kay SVGA adapter** | 640×480 VGA output | Digital RGB → analog VGA converter. Some versions supported hardware scrolling in the VGA output. |
| **Kay sound expansion** | TurboSound (dual AY) | Two AY-3-8912 chips for 12-channel sound; later versions added a MIDI port. |
| **Kay modem board** | 2400/9600 baud modem | Connected to the Nemo bus; used by FidoNet nodes across Russia. |
| **CMC/SMUC ISA bridge** | PC AT ISA bus bridge | Allowed using PC ISA cards (VGA, Ethernet, SoundBlaster) on the Kay. Later adopted by Scorpion. |
| **Kay scanner interface** | Hand scanner input | For digitizing graphics — widely used by demoscene artists. |

The IDE controller was the most important peripheral for software development — it enabled **hard-disk storage** of the entire Russian software library on a single machine, eliminating the constant disk-swapping that plagued TR-DOS-based systems.

---

## Memory Architecture and Paging

The Kay 1024 uses a **different extended paging scheme** from the Pentagon. While both use `#7FFD` for the base 128K paging, the Kay adds extended banking via port `#7FFD` bit 7 (which is the paging-disable bit on Sinclair hardware) combined with additional ports.

### Kay Memory Map

```
Address range    Contents               Control
──────────────────────────────────────────────────────────
#0000 - #3FFF   ROM 0 / ROM 1 / TR-DOS  #7FFD bit 4 + Beta port
                                              + extended ROM bits
#4000 - #7FFF   Bank 5 (fixed)         Always Bank 5
#8000 - #BFFF   Bank 2 (fixed)         Always Bank 2
#C000 - #FFFF   Banks 0-7 (standard)   #7FFD bits 0–2
                Banks 8-63 (extended)  #DFFD bits 0–2 (high bits)
──────────────────────────────────────────────────────────
```

### Port #DFFD — Kay Extended Paging

The Kay uses port `#DFFD` (not `#EFF7` like the Pentagon) for extended bank selection:

```
Port #DFFD (Kay extended paging, write-only):
  Bits 0–2: Extended bank bits (high bits of bank number)
  Combined with #7FFD bits 0–2:
    Total bank = (#DFFD & 0x07) × 8 + (#7FFD & 0x07)
    Range: 0..63 (64 banks × 16 KB = 1024 KB)
```

> [!WARNING]
> Port `#DFFD` on the Kay is **not the same** as `#DFFD` on the Pentagon (which is an alternative paging port on some Pentagon configs) or `#1FFD` on the +2A/+3. Always verify the target machine before writing to extended paging ports.

### ROM Banking

The Kay supports **multiple ROM banks** — typically 4 ROM banks of 16 KB, selectable via a combination of `#7FFD` bit 4 and an additional register:

| ROM bank | Contents | Selected by |
|---|---|---|
| Bank 0 | 128K editor ROM (Russian) | `#7FFD` bit 4 = 0, extended ROM bit = 0 |
| Bank 1 | 48K BASIC ROM | `#7FFD` bit 4 = 1, extended ROM bit = 0 |
| Bank 2 | TR-DOS ROM | Beta 128 FDC port |
| Bank 3 | Service ROM / debug monitor | Extended ROM bit = 1 |

The service ROM (bank 3) contains a low-level debug monitor — similar to the Scorpion's Shadow Service Monitor — that allows memory inspection, register display, and single-stepping without requiring external hardware.

---

## The Kay 2006 NB — CPLD Enhanced Video

The **Kay 2006 NB** is a late revision (2006) that adds an **Altera EPM7064 CPLD** for enhanced video modes. The CPLD replaces several discrete TTL chips in the video circuit and adds three new display modes that are not available on earlier Kay revisions or on any other Soviet clone.

### CPLD Video Modes

| Mode | Resolution | Colors | Use case |
|---|---|---|---|
| **Standard** | 256×192 | 15 (attribute) | Sinclair-compatible — default mode |
| **Multicolor** | 256×192 ×2 | 15 (8×1 attribute) | Shadow attribute buffer in alternate RAM bank — per-scanline attribute changes without CPU contention |
| **GigaScreen** | 256×192 interlaced | ~102 (simulated) | Alternates two attribute sets on even/odd frames; exploits PAL chroma bleed to simulate higher color resolution |
| **512×192** | 512×192 | 2 (monochrome) | Double horizontal resolution for static title screens and high-res artwork |

> [!NOTE]
> These modes are **Kay 2006 NB-specific** and not portable to other clones. The GigaScreen effect depends on PAL encoding artifacts and does not reproduce correctly on VGA monitors or in emulators that skip the PAL simulation. See [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md) for details.

### Programming the CPLD Modes

Mode selection is via a write to port `#DFFD` (the extended paging port, repurposed on the 2006 NB):

```z80
; Kay 2006 NB video mode selection
; Port #DFFD bits 4-5 select video mode (in addition to bits 0-2 for banking)

    LD   A,%0000_0000    ; Mode 0: Standard (256×192, 15 color)
    LD   BC,#DFFD
    OUT  (C),A
    
    LD   A,%0001_0000    ; Mode 1: Multicolor (shadow attribute buffer)
    OUT  (C),A
    
    LD   A,%0010_0000    ; Mode 2: GigaScreen (interlaced attribute)
    OUT  (C),A
    
    LD   A,%0011_0000    ; Mode 3: 512×192 monochrome
    OUT  (C),A
```

> [!WARNING]
> Port `#DFFD` is **overloaded** on the Kay 2006 NB — it controls both extended banking (bits 0–2) and video mode (bits 4–5). Software that writes to `#DFFD` for banking must preserve the video mode bits (and vice versa). Always read-modify-write if possible, or maintain a shadow register.

---

## Kay IDE Programming

The Kay IDE controller maps ATA/IDE register access to Z80 I/O ports. The interface is **8-bit** (not 16-bit like PC ATA) — each 16-bit IDE transfer requires two Z80 I/O reads.

### IDE Port Map

| Port | IDE register | Function |
|---|---|---|
| `#A0`–`#A7` | Data (low byte) | Read/write 8-bit data (low byte of 16-bit word) |
| `#A8`–`#AF` | Data (high byte) | Read/write 8-bit data (high byte of 16-bit word) |
| `#B0` | Error / Features | Read: error status; Write: feature enable |
| `#B2` | Sector count | Number of sectors to transfer |
| `#B3` | LBA low | LBA bits 0–7 |
| `#B4` | LBA mid | LBA bits 8–15 |
| `#B5` | LBA high | LBA bits 16–23 |
| `#B6` | Device / Head | LBA bit 24 + master/slave select |
| `#B7` | Status / Command | Read: status; Write: issue command |

### Reading a Sector (8-bit mode)

```z80
; Kay IDE — read one sector (512 bytes) into memory at HL
; Assumes: IDE drive is in LBA mode, 8-bit transfers enabled
; Destroys: AF, BC, DE, HL

ReadSector:
    ; Wait for drive not busy (status bit 7 = 0)
.wait_busy:
    LD   BC,#B7
    IN   A,(C)
    AND  #80
    JR   NZ,.wait_busy
    
    ; Select LBA mode, master drive, LBA bit 24 = 0
    LD   A,#E0           ; LBA mode | master | LBA[24:27] = 0
    LD   BC,#B6
    OUT  (C),A
    
    ; Set sector count = 1
    LD   A,#01
    LD   BC,#B2
    OUT  (C),A
    
    ; Issue READ SECTORS command (0x20)
    LD   A,#20
    LD   BC,#B7
    OUT  (C),A
    
    ; Wait for data ready (status bit 3 = 1, i.e., DRQ)
.wait_drq:
    IN   A,(C)
    AND  #08
    JR   Z,.wait_drq
    
    ; Read 512 bytes (256 × 2 bytes, 8-bit reads)
    LD   B,#00           ; 256 iterations
    LD   C,#A0           ; Low-byte data port
.read_loop:
    IN   A,(C)           ; Read low byte
    LD   (HL),A
    INC  HL
    INC  C               ; High-byte data port (#A1)
    IN   A,(C)           ; Read high byte
    LD   (HL),A
    INC  HL
    DEC  C               ; Back to low-byte port
    DJNZ .read_loop
    
    RET
```

This is the basic pattern; production code adds error handling (check the error register after status), timeouts (don't wait forever for DRQ), and retry logic for bad sectors. The [iDE interface article](../../03_io/storage/ide_interface.md) covers these patterns in depth.

---

## Kay vs Pentagon — When to Target Each

| Criterion | Kay 1024 | Pentagon 1024 |
|---|---|---|
| **Timing compatibility** | 48K-exact (69,888 T/frame, 312 lines) | Non-standard (71,680 T/frame, 320 lines) |
| **Contention** | None | None |
| **Extended paging port** | `#DFFD` | `#EFF7` |
| **Expansion bus** | Nemo bus (60-pin) | Standard edge connector (56-pin) |
| **Hard disk support** | Built-in IDE controller | Requires expansion |
| **Video modes** | Standard + GigaScreen (2006 NB) | Standard only |
| **Popularity** | Professional market (1995–2002) | Hobbyist / demoscene (1993–present) |
| **Software library** | Smaller (professional tools) | Larger (all Russian demoscene) |

**Target the Kay** if you want 48K-exact timing with zero contention — code written for the 48K runs cleanly on the Kay with only timing-specific adjustments (remove contention delays). The Kay is the best choice for cross-platform software that must run on both Western and Russian hardware.

**Target the Pentagon** if you want maximum audience — the Pentagon was far more popular than the Kay, and Russian demoscene software overwhelmingly targets Pentagon timing. But be prepared for your code to break on 48K hardware due to the 320-line frame.

---

## Cross-References

- [Pentagon 128K](pentagon.md) — the dominant Soviet clone, with different timing and `#EFF7` paging
- [Pentagon 1024](pentagon_1024.md) — the Pentagon's 1 MB variant, Kay's main competitor
- [Scorpion](scorpion.md) — another high-end clone with Nemo bus compatibility (SMUC)
- [ATM Turbo](atm_turbo.md) — CP/M-capable clone with extended graphics
- [Profi](profi.md) — Ukrainian professional clone with VGA output
- [Clone timing](clone_timing.md) — Kay vs Pentagon vs Scorpion timing comparison
- [Kay video frame](../../05_development/05_display_and_timing/video_frame_other_soviet.md) — detailed Kay frame timing and 2006 NB modes
- [IDE interface](../../03_io/storage/ide_interface.md) — general IDE/ATA programming (Kay-specific patterns above)
- [Beta 128 FDC](../../03_io/storage/beta_disk_interface.md) — disk interface used on the Kay
- [TR-DOS](../../04_operating_systems/trdos.md) — disk operating system
- [Soviet demoscene](../../07_demoscene/soviet_demo_scene.md) — cultural context

---

## References

- **NEMO company documentation** (1991–1998) — original Kay 1024 schematics and Nemo bus specification
- **zx-pk.ru forum** — *Кэй 1024* subforum contains hardware variants, IDE controller schematics, and repair threads
- **SpeccyWiki (speccy.info)** — Kay 1024 and Kay 2006 NB articles with CPLD programming details
- **Kay 2006 NB documentation** (zx-pk.ru) — GigaScreen and multicolor mode specifications
- **Unreal Speccy emulator** — reference implementation of Kay `#DFFD` paging and 2006 NB video modes
- **FidoNet ZX.SPECTRUM echoes** (1995–2002) — contemporary discussions of Kay IDE programming and Nemo bus peripherals
