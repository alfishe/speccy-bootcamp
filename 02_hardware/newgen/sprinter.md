[← Home](../../README.md) · [New Gen Hardware](README.md)

# Sprinter — Peters Plus's 1996 Z80 PC

The **Sprinter** (Спринтер, produced by **Peters Plus**, Moscow, 1996–2000) is a late-era Russian Spectrum-family computer that takes a different path from the FPGA-based machines (Next, ZX Evolution, ZX-Uno) covered elsewhere in this section. Where those machines use FPGAs to recreate classic Spectrum hardware, the Sprinter is a **discrete-component Z80 PC** — a single-board computer with a real Z80 CPU running at 20 MHz, 1 MB of RAM, an SVGA-compatible video controller, IDE storage, and a PC-style keyboard and mouse.

The Sprinter was designed by **Vladimir "vslav" Kladov** (later the lead designer of the ZX Evolution) and was Peters Plus's flagship product — aimed at the **post-clone professional market** of the late 1990s. It is binary-compatible with the Spectrum 128K and Pentagon (for the existing Russian software library) but adds enough PC-style hardware that **new software could be written for it that had nothing to do with the Spectrum** — word processors, spreadsheets, BBS clients, etc.

This article covers the Sprinter as a hardware platform: its architecture, memory map, video modes, ports, and programming model. For the demoscene context, see [Soviet demo scene](../../07_demoscene/soviet_demo_scene.md). For the Sprinter's place in the clone-timing landscape, see [clone_timing.md](../clones/clone_timing.md).

---

## Why the Sprinter Is Different

By 1996, the Russian Spectrum scene had a problem: the hardware was old. The Pentagon 128 was a 1989 design built around discrete TTL logic, with a slow 3.5 MHz CPU and tape-based software distribution. The scene wanted modern features — fast CPU, disk storage, VGA output, PS/2 keyboard — without abandoning the thousands of existing Spectrum programs.

Two solutions emerged:

1. **The ZX Evolution** (Kladov's later design, 2007+) — use an FPGA to recreate the Pentagon while adding modern peripherals (see [zx_evo.md](zx_evo.md)).
2. **The Sprinter** (Kladov's earlier design, 1996) — build a **new Z80-based computer** from discrete components, with a 128K/Pentagon compatibility mode implemented in firmware.

The Sprinter is the "more radical" approach: it does not try to clone the Pentagon's video timing or contention behavior at the hardware level. Instead, it provides a modern PC-style architecture with a Spectrum compatibility layer. The result is a machine that is **binary-compatible with Pentagon software at the API level** (DOS calls, BIOS calls, video memory layout) but has **completely different underlying hardware**.

| Criterion | Sprinter | ZX Evolution | ZX Spectrum Next |
|---|---|---|---|
| **Year** | 1996 | 2007 | 2017 |
| **Architecture** | Discrete Z80 PC | Z80 + CPLD glue | FPGA soft-core |
| **CPU** | Real Z80 @ 20 MHz | Real Z80 @ 3.5/7/14 MHz | Z80N soft-core @ 3.5/7/14/28 MHz |
| **RAM** | 1 MB | 4 MB | 2 MB |
| **Video** | **Produce SVGA chip** (PC-style) | Pentagon-style + extensions | Layer 2 / sprites / tilemap / copper |
| **Storage** | **IDE hard disk** | IDE + SD card | SD card |
| **Keyboard** | **PS/2 PC keyboard** | PS/2 | Built-in + PS/2 |
| **Compatibility target** | Pentagon (software-level) | Pentagon (cycle-level) | 48K/128K/Pentagon (cycle-level) |

---

## Hardware Architecture

| Component | Specification |
|---|---|
| **CPU** | **Z80 at 20 MHz** (some revisions: 14 MHz), CMOS Z84C0020 |
| **RAM** | **1 MB** static or pseudo-static RAM, organized as 64 banks of 16 KB |
| **ROM** | **256 KB or 512 KB flash**, holds the BIOS + 128K BASIC + Pentagon ROMs + DOS |
| **Video controller** | **Produce** (a Russian SVGA-compatible ASIC), produces 320×200 256-color and 640×480 16-color SVGA output |
| **Storage** | **IDE interface** (8-bit, single drive), CompactFlash via IDE adapter |
| **Floppy** | **PC-style 3.5" floppy** at standard PC formats (1.44 MB, 720 KB) — not Beta 128 |
| **Keyboard** | **PS/2 PC keyboard** (full-travel, AT-compatible) |
| **Mouse** | **PS/2 mouse** |
| **Audio** | **AY-3-8912** (Pentagon-compatible) + beeper + Covox-style 8-bit DAC |
| **Joystick** | **Kempston** at port `#1F` |
| **Expansion** | **ISA-compatible slots** (8-bit, PC-style) |
| **Case** | Desktop case resembling a PC/XT |
| **Power** | Standard PC AT power supply |

The Sprinter's defining hardware choice is the **Produce video ASIC** — a Russian-made SVGA-compatible chip that provides video modes that no other Spectrum-family machine has. Where the Pentagon's video is the standard 256×192 attribute-based display, the Sprinter can drive a real SVGA monitor at PC-standard resolutions.

---

## Memory Architecture

The Sprinter's memory is organized as **64 banks of 16 KB** (1 MB total), paged through a Pentium-style bank-switching scheme that is **not compatible with the Pentagon's `#7FFD`/`#EFF7` paging**:

| Port | Function |
|---|---|
| `#1FFD` | Bank switch for `#0000–#3FFF` (lower 16 KB) |
| `#EFF7` | Bank switch for `#4000–#7FFF` |
| `#DFFD` | Bank switch for `#8000–#BFFF` |
| `#7FFD` | Bank switch for `#C000–#FFFF` (compatibility with Pentagon 128) |

In **Sprinter native mode**, all four 16 KB slots are independently banked — giving the programmer full control over which 4 of the 64 banks are visible at any time. This is more flexible than the Pentagon's model (where `#4000–#7FFF` and `#8000–#BFFF` are fixed).

In **Pentagon compatibility mode**, the banking is restricted to mimic the Pentagon 128 — `#7FFD` controls `#C000–#FFFF` as a single 16 KB bank, while `#4000–#7FFF` is bank 5 and `#8000–#BFFF` is bank 2 (fixed). This allows existing Pentagon software to run.

### The Pentagon Compatibility Layer

The Sprinter's Pentagon compatibility is implemented in **firmware**, not hardware. The BIOS exposes Pentagon-compatible entry points for:

- **TR-DOS calls** — the standard `#3D13` entry points for disk operations
- **BASIC ROM** — the 128K BASIC editor is banked in on demand
- **Video memory** — the standard Pentagon screen at `#4000` (bank 5) is mapped to the Produce ASIC's framebuffer

Software that uses these entry points runs identically to a Pentagon. Software that hits hardware directly (e.g., reads the floating bus, or assumes contention timing) may fail — the Sprinter does not emulate the Pentagon's contention pattern or floating-bus behavior.

> [!NOTE]
> The Sprinter's compatibility is "good enough" for **most** Pentagon software — roughly 80–90% of games and demos run correctly. The 10–20% that fail are typically cycle-exact demos that depend on contention timing. See [clone_timing.md](../clones/clone_timing.md) for the timing comparison.

---

## Video Modes

The Produce ASIC provides the Sprinter's signature feature — **multiple video modes** selectable at runtime:

| Mode | Resolution | Colors | Notes |
|---|---|---|---|
| **Spectrum text** | 256×192 | 8×2 (attribute) | Pentagon-compatible |
| **Produce 320×200×256** | 320×200 | 256 | PC-style, like VGA mode 13h |
| **Produce 640×480×16** | 640×480 | 16 | PC-style, like VGA mode 12h |
| **Produce 640×200×16** | 640×200 | 16 | PC-style, useful for spreadsheets |
| **Text mode** | 80×25 (text) | 16 | Standard PC text mode |

The Spectrum text mode is binary-compatible with the Pentagon — software that writes to `#4000` (bank 5) sees the standard attribute-based screen. The Produce modes are accessed through the Produce ASIC's register set (separate I/O ports).

### Produce Register Programming

The Produce ASIC is configured through a set of register ports similar to a standard VGA controller:

| Port | Function |
|---|---|
| `#3CE` / `#3CF` | Graphics Controller register select / data (VGA-compatible) |
| `#3D4` / `#3D5` | CRT Controller register select / data (VGA-compatible) |
| `#3DA` | Input Status #1 (VGA-compatible — vsync, hsync) |

Programming the Produce is essentially programming a standard VGA — the same algorithms used for PC demoscene VGA effects (mode 13h "un chained", palette cycling, raster interrupts via vsync) work on the Sprinter.

> [!TIP]
> For developers coming from the PC demoscene, the Sprinter is the most comfortable Russian Spectrum — you can write code that's structurally identical to a 1990s VGA demo, just targeting a Z80 instead of an x86.

---

## Software Ecosystem

The Sprinter had a brief but active software ecosystem (1996–2000):

- **New software** — word processors, terminal programs, file managers written specifically for the Sprinter's VGA modes
- **Ported software** — many Pentagon games and demos were adapted to run under the Sprinter's compatibility layer
- **IS-DOS** — a Russian DOS clone that ran on the Sprinter, providing a CP/M-like environment with full file system and process management
- **BBS software** — the Sprinter's PS/2 keyboard and SVGA made it a popular platform for Russian BBS systems in the late 1990s

After 2000, the Sprinter was largely superseded by the ZX Evolution (which had better Pentagon compatibility via its FPGA approach). The Sprinter is now a niche historical platform — small but dedicated community, mostly Russian-language documentation.

---

## Programming the Sprinter

### Detecting a Sprinter

The Sprinter can be detected by checking for its BIOS signature. The BIOS exposes a **machine ID byte** at a known location:

```z80
detect_sprinter:
        ld  a, (#FFFF)           ; Read machine ID
        cp  #10                  ; Sprinter ID is #10 (example value — check docs)
        jr  z, .is_sprinter
        ; Not a Sprinter — fall back to Pentagon behavior
        ret
.is_sprinter:
        ; Use Sprinter-specific features
        ret
```

The exact ID byte and location varies by BIOS revision; see the Sprinter technical manual for the authoritative values.

### Switching to Produce Mode

To enable the 320×200×256 Produce mode (the most useful for new software):

```z80
enable_produce_320x200:
        ; 1. Disable the Spectrum text mode
        ld  bc, #1FFD
        in  a, (c)
        or  #10                  ; bit 4 = switch to Produce
        out (c), a
        
        ; 2. Configure the Produce ASIC for mode 13h-like 320×200×256
        ld  bc, #3CE             ; Graphics Controller
        ld  a, 5                 ; GDC mode register
        out (c), a
        inc b                    ; BC = #3CF
        ld  a, #40               ; Mode 2 (256-color), no chain
        out (c), a
        
        ; 3. Set the palette to a default 256-color gradient
        call init_produce_palette
        
        ; 4. The framebuffer is now at #A0000 (banked into Z80 space in 16 KB chunks)
        ; Use the Sprinter's bank-switching to write to it
        ret
```

The exact register values follow the standard VGA programming conventions — see any VGA reference (e.g., [the VGA tutorial by Fabian](https://files.lyhus.com/VGA/vga.html)) for the canonical sequences.

---

## Cross-References

- [ZX Evolution](zx_evo.md) — Kladov's later, FPGA-based successor to the Sprinter
- [Pentagon 128](../clones/pentagon.md) — the Sprinter's compatibility target
- [Pentagon 1024](../clones/pentagon_1024.md) — the Sprinter's competitor at the time
- [ATM Turbo](../clones/atm_turbo.md) — another late-era Russian "Z80 PC" with VGA-style video
- [Profi](../clones/profi.md) — earlier Ukrainian clone with VGA output (similar concept)
- [Clone timing](../clones/clone_timing.md) — Sprinter's relationship to other clone timings
- [Soviet demo scene](../../07_demoscene/soviet_demo_scene.md) — cultural context

---

## References

- **Sprinter technical manual** (Peters Plus, 1996, Russian) — original hardware reference
- **Peters Plus archive** (nedopc.org) — Sprinter schematics, BIOS source, software archive
- **ZX-Review magazine** (1996–1999) — Sprinter construction articles and programming guides
- **zx-pk.ru forum** — *Sprinter* subforum with BIOS documentation and repair threads
- **SpeccyWiki (speccy.info)** — Sprinter article with photos and specification tables
- **VGA programming references** — the Sprinter's Produce ASIC follows VGA conventions; any VGA reference is applicable
