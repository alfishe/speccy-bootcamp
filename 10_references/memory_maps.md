[← Home](../README.md) · [References](README.md)

# Memory Maps — ZX Spectrum Memory Layouts

Consolidated memory layout reference for every ZX Spectrum model and major clone: 16K/48K, 128K/+2 (grey), +2A/+3, Pentagon, Scorpion, ATM Turbo, and the ZX Spectrum Next. Each model has its own deep-dive article covering bank switching, contention nuances, and programming patterns — this page is the **lookup table** that puts all the maps side-by-side for cross-model comparison.

> [!NOTE]
> For the *concepts* behind bank switching, partial decoding, and contention, see [bank_switching_patterns.md](../05_development/03_memory_and_io/bank_switching_patterns.md), [contention_model.md](../05_development/03_memory_and_io/contention_model.md), and [io_port_decoding.md](../05_development/03_memory_and_io/io_port_decoding.md). This article is the **reference card** — you come here to see exact addresses at a glance.

---

## How the Z80 Sees Memory

The Z80 CPU has a 16-bit address bus, so it can address **65,536 bytes (64 KB)** of memory at any one instant. The address space is always divided the same way at the top level:

| Region | 48K | 128K / +2 | +2A / +3 |
|---|---|---|---|
| `#0000–#3FFF` (16 KB low) | ROM (one bank) | ROM bank 0 or 1, or DOS ROM | ROM bank 0/1/2/3, or DOS ROM, or all-RAM mode |
| `#4000–#7FFF` (16 KB mid) | RAM (fixed) | RAM bank 5 (fixed) | RAM, configurable |
| `#8000–#BFFF` (16 KB high-mid) | RAM (fixed) | RAM, bank 2 fixed | RAM, configurable |
| `#C000–#FFFF` (16 KB top) | RAM (fixed) | RAM, paged bank | RAM, configurable |

The 48K is **static** — the layout never changes. Everything else **pages** one or more 16 KB banks in or out of the address space via an I/O port. The +2A/+3 is the most flexible: all four 16 KB slots can be independently remapped to one of eight RAM banks.

---

## 48K / 16K Memory Map

The Sinclair ZX Spectrum 16K and 48K use a **fixed, non-paged** memory map. The 16K is identical except RAM stops at `#7FFF` and the upper 32 KB (`#8000–#FFFF`) is unmapped — reads return `#FF` and writes are lost.

### Full 48K Address Space

| Range | Size | Contents | Contended? |
|---|---|---|---|
| `#0000–#3FFF` | 16384 | **ROM** — Sinclair BASIC interpreter, editor, tape routines, character set | No (ROM) |
| `#4000–#57FF` | 6144 | **Screen pixel buffer (PIX)** — 256×192 pixels, 1 bpp, nonlinear layout | **Yes** (ULA reads for display) |
| `#5800–#5AFF` | 768 | **Attribute file (ATTR)** — 32×24 cells, 1 byte per cell (INK/PAPER/BRIGHT/FLASH) | **Yes** |
| `#5B00–#5BFF` | 256 | **Printer buffer** — output buffer for the ZX Printer | No |
| `#5C00–#5CB5` | 182 | **System variables** — ROM workspace, flags, cursor position, etc. | No |
| `#5CB6–` | varies | **Channel information area** — definitions for streams `K`, `S`, `P`, `R` | No |
| (after channels) | varies | **Stream data** — 16 streams × 2 bytes | No |
| `#5D00` ↑ | free | **BASIC program text** — tokenised program, grows upward | No |
| (above program) | free | **Variables area** — numeric and string variables | No |
| `#FF58` ↓ | free | **UDG area** — User-Defined Graphics, grows downward from RAMTOP | No |
| `#FF58` | — | **RAMTOP** — top of usable RAM, default `#FF57` on 48K, `#7F57` on 16K | No |
| `#FF59`–`#FFFF` | ~150 | **Z80 machine stack** — grows downward from `#FFFF` | No |

> [!WARNING]
> Memory above `#FF58` is **stack space**. Storing data there is safe *only* if you move the stack with `LD SP,...` first; otherwise any `CALL`, `RST`, or interrupt will overwrite your data.

### 16K Model Differences

| Item | 48K | 16K |
|---|---|---|
| RAM size | 48 KB (`#4000–`#FFFF`) | 16 KB (`#4000–#7FFF`) |
| RAMTOP | `#FF57` | `#7F57` |
| Reads from `#8000–#FFFF` | Returns RAM contents | Returns `#FF` (floating bus) |
| Writes to `#8000–#FFFF` | Stored | Lost |

The 16K and 48K ROMs are **identical** — the ROM checks `#7FFF` at startup to detect which model it is running on and adjusts RAMTOP accordingly.

### Standard System Variables (48K)

The most-used system variables live in the `#5C00` range. Full list in the Sinclair ROM manual; the most useful ones for assembly programmers are:

| Address | Name | Purpose |
|---|---|---|
| `#5C3C` | `MODE` | 0 = K (keywords), 1 = L (lowercase), 2 = G (graphics), 3 = E (extended) |
| `#5C3D` | `VARS` | Address of variables area (word) |
| `#5C44` | `E_PPC` | Current line number for EDIT (word) |
| `#5C45` | `WORKSP` | Address of workspace (word) |
| `#5C49` | `STKBOT` | Bottom of machine stack (word) |
| `#5C4B` | `CURCHL` | Current channel (word) |
| `#5C51` | `ATTR_P` | Permanent attributes (INK/PAPER/etc.) |
| `#5C53` | `ATTR_T` | Temporary attributes |
| `#5C5B` | `BORDCR` | Border color × 8 (mirrors port `#FE`) |
| `#5C7B` | `FRAMES` | 3-byte frame counter, incremented every 20 ms by INT — the canonical "time" reference |
| `#5C8D` | `TADDR` | Pointer used by `PLAY` command (128K only) |
| `#5CB6` | `CHANS` | Channel information table address |

For the complete list with one-line semantics, see [rom_routines.md](rom_routines.md) and the Sinclair *ZX Spectrum BASIC Programming* manual.

---

## 128K / +2 (Grey) Memory Map

The 128K (1986, the "Toastrack") and the Amstrad +2 (grey, 1987) use the **same memory architecture**. They expose 128 KB of RAM split into **8 banks of 16 KB** plus two 16 KB ROM banks, with **one paging port** at `#7FFD`.

### Default Memory Layout

| Range | Bank | Contents | Contended? |
|---|---|---|---|
| `#0000–#3FFF` | ROM 0 | 128K BASIC editor and menu | No |
| `#4000–#7FFF` | RAM 5 | Screen pixel buffer + attributes (main screen) | **Yes** |
| `#8000–#BFFF` | RAM 2 | General-purpose RAM | No |
| `#C000–#FFFF` | RAM 0 | Default paged bank — general-purpose RAM | No |

### All 8 RAM Banks

| Bank | Address when paged into `#C000` | Typical use | Contended? |
|---|---|---|---|
| 0 | `#C000` (default) | Main RAM | No |
| 1 | `#C000` | General use | No |
| 2 | `#8000` (fixed) | General use | No |
| 3 | `#C000` | General use | No |
| 4 | `#C000` | General use | No |
| 5 | `#4000` (fixed) | **Main screen** (PIX + ATTR) | **Yes** |
| 6 | `#C000` | General use | No |
| 7 | `#C000` | **Shadow screen** (PIX + ATTR) — bank-switchable display | **Yes** |

### ROM Banks

| ROM bank | Mapped at | Purpose |
|---|---|---|
| 0 | `#0000–#3FFF` | 128K BASIC editor + menu + 48K BASIC |
| 1 | `#0000–#3FFF` | 128K BASIC runtime (help, error messages, etc.) |
| (TR-DOS) | `#0000–#3FFF` | Russian-clones only: Beta 128 TR-DOS ROM, paged by reading port `#7FFD` |

### Paging Register — Port `#7FFD`

| Bit | Purpose |
|---|---|
| 0–2 | RAM bank paged into `#C000–#FFFF` (banks 0–7) |
| 3 | Screen select: 0 = main (bank 5), 1 = shadow (bank 7) |
| 4 | ROM bank select: 0 = ROM 0, 1 = ROM 1 |
| 5 | Disable further paging — once set to 1, this bit is **sticky** until reset (prevents runaway programs from breaking the memory map) |
| 6–7 | Unused |

> [!WARNING]
> Bit 5 is **write-once**. Once you set it, the paging register is locked until the next reset. Test for `BIT 5,(HL)` before assuming you can re-page.

### Fixed vs Switchable Slots

| Slot | Range | Switchable? |
|---|---|---|
| ROM | `#0000–#3FFF` | Only ROM 0/1 toggle (bit 4 of `#7FFD`) |
| Bank 5 | `#4000–#7FFF` | **Fixed** — always RAM bank 5, never moved |
| Bank 2 | `#8000–#BFFF` | **Fixed** — always RAM bank 2, never moved |
| Paged bank | `#C000–#FFFF` | Any of banks 0/1/2/3/4/5/6/7 via bits 0–2 of `#7FFD` |

The choice of which banks are "fixed" is intentional: it guarantees that the screen is always at `#4000–#7AFF` and the interrupt vector / common workspace is always in bank 2 — software can rely on these being where they are regardless of paging state.

For the full programming model including shadow screen, contention patterns, and how to access data in paged-out banks, see [memory_and_io_128k.md](../05_development/03_memory_and_io/memory_and_io_128k.md).

---

## +2A / +3 Memory Map

The Amstrad +2A (black, 1987) and +3 (1987, with built-in floppy disk) replace the simple 128K paging scheme with a more flexible one. Port `#7FFD` is retained for compatibility, but a **new port `#1FFD`** adds four "special modes" that can remap **all four 16 KB slots** independently.

### Default Configuration (Compatibility Mode)

Same as 128K/+2 above — port `#1FFD` bits 0 and 1 are 0, putting the machine in "configuration 0" which mimics the original 128K.

### Port `#7FFD` (Same as 128K, with Caveat)

On the +2A/+3, the `#7FFD` register has 3 bits of paging plus the screen and ROM select bits — same bit assignments as 128K. However, bits 0 and 1 are also affected by port `#1FFD` (see below), so the actual RAM bank is a combination.

### Port `#1FFD` — Special Configuration

| Bit | Purpose |
|---|---|
| 0 | ROM 0 / ROM 1 select (overrides `#7FFD` bit 4 in special modes) |
| 1 | ROM / RAM at `#0000–#3FFF`: 0 = ROM, 1 = RAM |
| 2 | Disk motor control (+3 only) |
| 3 | Printer strobe (parallel port) |
| 4–6 | Unused |
| 7 | Special paging mode: 0 = compatibility (128K mode), 1 = special mode |

When bit 7 of `#1FFD` is 0, the machine behaves like a 128K. When bit 7 is 1, **special paging mode** is enabled and bits 0–1 of `#1FFD` plus bits 0–2 of `#7FFD` select one of 16 configurations.

### The Four Special Modes (All-RAM Configurations)

| Mode | `#0000–#3FFF` | `#4000–#7FFF` | `#8000–#BFFF` | `#C000–#FFFF` |
|---|---|---|---|---|
| Config 0 | RAM 0 | RAM 1 | RAM 2 | RAM 3 |
| Config 1 | RAM 4 | RAM 5 | RAM 6 | RAM 7 |
| Config 2 | RAM 6 | RAM 0 | RAM 1 | RAM 2 |
| Config 3 | RAM 4 | RAM 5 | RAM 6 | RAM 3 |

Configurations 0 and 1 are "all RAM" — useful when the +2A/+3 must read or write the whole 128 KB without ROM being present (e.g., to dump the whole memory to disk). Configurations 2 and 3 are mixed and rarely used outside specific DOS routines.

The full breakdown with examples is in [memory_and_io_plus3.md](../05_development/03_memory_and_io/memory_and_io_plus3.md).

---

## Pentagon 128K Memory Map

The Pentagon is a Russian unofficial clone (see [pentagon.md](../02_hardware/clones/pentagon.md)) that closely follows the 128K/+2 architecture but with two important differences: **different contention** and **different port decoding** for compatibility.

### Pentagon-Specific Behaviour

| Item | 128K/+2 (Sinclair/Amstrad) | Pentagon |
|---|---|---|
| Contended banks | 0, 1, 3, 4, 5, 7 (slow access during display) | 1, 3, 5, 7 (only the "odd" banks) |
| Uncontended banks | 2, 6 | 0, 2, 4, 6 (only the "even" banks) |
| Display | ULA reads bank 5 (or 7 if shadow selected) | Same — ULA reads bank 5 (or 7) |
| Port `#7FFD` paging | Bits 0–2 select any of 8 banks | Same |
| Port `#1FFD` | Not implemented | Not implemented (only `#7FFD` is used) |
| TR-DOS ROM | Not present | **Present** — paged when accessing Beta 128 ports |

### Pentagon Extended Memory (Pentagon 512 / 1024)

Larger Pentagon variants extend the paging register to add more banks:

| Variant | Total RAM | Banks available | Paging port |
|---|---|---|---|
| Pentagon 128 | 128 KB | 0–7 (3-bit select) | `#7FFD` bits 0–2 |
| Pentagon 512 | 512 KB | 0–31 (5-bit select) | `#7FFD` bits 0–2 + `#EFF7` bits 0–1 |
| Pentagon 1024 | 1024 KB | 0–63 (6-bit select) | `#7FFD` bits 0–2 + `#DFF7` bits 0–2 |

The extended paging ports are write-only and their exact decoding varies between Pentagon revisions — see [memory_and_io_pentagon.md](../05_development/03_memory_and_io/memory_and_io_pentagon.md) for details.

---

## Scorpion 256K / 1024 Memory Map

The Scorpion ZS-256 is a more sophisticated Russian clone with its own paging scheme — see [scorpion.md](../02_hardware/clones/scorpion.md). The default "Sinclair 128K compatibility" mode mimics the 128K, but a "Scorpion" mode adds more banks.

| Range | Sinclair mode | Scorpion mode |
|---|---|---|
| `#0000–#3FFF` | ROM 0 / ROM 1 | ROM 0 / ROM 1 / TR-DOS ROM / Service ROM |
| `#4000–#7FFF` | RAM bank 5 (fixed) | Configurable — any of 64 banks |
| `#8000–#BFFF` | RAM bank 2 (fixed) | Configurable — any of 64 banks |
| `#C000–#FFFF` | Paged RAM | Configurable — any of 64 banks |

Scorpion uses two ports: `#1FFD` (mode + memory layout) and `#7FFD` (bank selection). See [scorpion.md](../02_hardware/clones/scorpion.md) for the full decoding table.

---

## ATM Turbo Memory Map

The ATM Turbo is a Russian clone with Turbo mode and a hard disk option. It uses port `#FFFD` (not `#7FFD`) for paging and supports up to 1 MB of RAM. See [atm_turbo.md](../02_hardware/clones/atm_turbo.md).

| Mode | Use |
|---|---|
| Sinclair 128K | Compatibility — same as 128K/+2 |
| ATM (Turbo) | CP/M-style memory map, 4 banks of 16 KB paged into `#C000–#FFFF`, with extended ports for the disk and IDE |

---

## ZX Spectrum Next Memory Map

The ZX Spectrum Next (2017+, see [zx_next.md](../02_hardware/newgen/zx_next.md) for hardware overview) extends the architecture dramatically:

- **8 KB ROM banks** (vs 16 KB on 128K) — 256 ROM bank slots
- **8 KB RAM pages** (vs 16 KB) — 16,384 RAM pages = 128 MB maximum (only 1–2 MB on shipping hardware)
- **Layer 2** — 256×192×8bpp framebuffer paged into `#0000–#3FFF` in 16 KB chunks
- **MMU** — 8 mapping slots, each can map any 8 KB RAM/ROM page into the Z80 address space
- **Hardware sprites, tilemap, copper** — all addressed separately from main memory

The Next can run in several compatibility modes:

| Mode | What it does |
|---|---|
| 48K | Maps ROM + RAM to mimic a 48K |
| 128K | Maps ROM + RAM to mimic a 128K/+2 |
| +3 | Maps ROM + RAM to mimic a +2A/+3 |
| Next (native) | Full MMU active, all Next features available |

Programming details in [memory_and_io_next.md](../05_development/03_memory_and_io/memory_and_io_next.md).

---

## Screen Address Quick Reference

The screen is always 6912 bytes (6144 pixels + 768 attributes) regardless of model. The address of the visible screen depends on the model and the shadow-screen bit:

| Model | Default screen | Shadow screen | Bit to toggle |
|---|---|---|---|
| 48K / 16K | `#4000` | n/a | n/a |
| 128K / +2 | `#4000` (bank 5) | `#C000` (bank 7) | `#7FFD` bit 3 |
| +2A / +3 | `#4000` (bank 5) | `#C000` (bank 7) | `#7FFD` bit 3 |
| Pentagon 128 | `#4000` (bank 5) | `#C000` (bank 7) | `#7FFD` bit 3 |
| Scorpion | `#4000` (bank 5) | `#C000` (bank 7) | `#7FFD` bit 3 |
| ZX Spectrum Next | `#4000` (bank 5) | `#C000` (bank 7) | `#7FFD` bit 3 (or Next register) |

The pixel buffer is always at **offset 0** of the screen, attributes at **offset 6144** (`#4000 + #1800 = #5800` on the default screen).

For pixel address calculation (the nonlinear layout: line `Y` → byte address `#4000 + (Y & #C0) << 5 + (Y & #07) << 8 + (Y & #38) << 2 + X >> 3`), see [screen_layout.md](../05_development/03_memory_and_io/screen_layout.md).

---

## Contended Memory Regions

When the ULA is reading the screen for display, it stalls the CPU with `WAIT_n` for short windows of time. The "contended" regions are the RAM areas the ULA touches. Accessing a contended address during display time adds extra T-states — the exact number depends on the model and the contention pattern.

| Model | Contended addresses (display-time) | Contention pattern |
|---|---|---|
| **48K** | `#4000–#7FFF` (banks always present) | Late timing — `+1` T-state per access inside contention window |
| **128K / +2** | Banks 0, 1, 3, 4, 5, 7 when paged in | Late timing — `+1` to `+6` T-states, varies by cycle |
| **+2A / +3** | Banks 4, 5, 6, 7 when paged in | Late timing, similar to 128K |
| **Pentagon** | Banks 1, 3, 5, 7 when paged in | Early timing — `+1` T-state per access |
| **Scorpion** | Banks 1, 3, 5, 7 (Sinclair mode) | Pentagon-compatible |
| **ATM Turbo** | Varies by mode | N/A for non-Sinclair modes |
| **ZX Spectrum Next** | Banks 5, 7 (compatibility mode) | Configurable; can be disabled |

For exact contention delay tables per cycle and per model, see [timing_reference.md](timing_reference.md) and the deep-dive [contention_model.md](../05_development/03_memory_and_io/contention_model.md).

---

## ROM Locations Quick Reference

All models keep the Sinclair ROM (or a Sinclair-compatible ROM) in the low 16 KB at `#0000–#3FFF`. Common ROM entry points used by assembly programmers:

| Address | Routine | Use |
|---|---|---|
| `#0000` | Reset | Cold/warm reset — clears RAM and restarts |
| `#0008` | Error handler | Print error and reset stack; HL = error code |
| `#0010` | PRINT_CHAR | Print character in A to current channel |
| `#0018` | COLLECT_CHAR | Get next character from current channel |
| `#0020` | KEY_SCAN | Scan keyboard, return result in DE |
| `#0028` | KEY_INPUT | Wait for and return key in A |
| `#0038` | Maskable INT | INT service routine (IM 1) |
| `#0066` | NMI | NMI service routine |
| `#0D6D` | CLS | Clear screen and reset attributes |
| `#0E44` | CHAN_OPEN | Open channel A to current stream |
| `#10A8` | FLOAT_TO_INT | Convert FP accumulator to integer |
| `#1A1B` | BEEP | BEEP command routine |
| `#1F05` | COPY | Copy screen to ZX Printer |
| `#20CC` | SAVE | SAVE to tape |
| `#21CC` | LOAD | LOAD from tape |

Full table in [rom_routines.md](rom_routines.md).

> [!WARNING]
> Calling 48K ROM routines from 128K/+2A/+3 code is **only safe in 48K mode** — the ROM entry points differ between ROMs. Always check the active ROM bank before calling.

---

## RAMTOP and Stack Defaults

| Model | Default RAMTOP | Default stack pointer |
|---|---|---|
| 16K | `#7F57` | `#7F58` |
| 48K | `#FF57` | `#FF58` |
| 128K / +2 | `#FF57` | `#FF58` |
| +2A / +3 | `#FF57` | `#FF58` |
| Pentagon | `#FF57` | `#FF58` |
| Scorpion | `#FF57` | `#FF58` |

RAMTOP is the highest address the BASIC system uses. The stack sits **just above** RAMTOP and grows upward toward `#FFFF`. Programs that need machine-code space typically call `CLEAR <addr>` (which sets RAMTOP) before loading the code, so BASIC will not overwrite it.

---

## Cross-Model Compatibility Cheat Sheet

When writing code that must run on multiple models:

| Concern | Solution |
|---|---|
| Detect 48K vs 128K | Read system variable `LASTSL` at `#5C02` — bit pattern reveals ROM version; or check `#7FFF` (returns `#FF` on 16K, RAM on 48K+) |
| Detect +2A/+3 vs 128K/+2 | Try writing to port `#1FFD` and reading back — if the value sticks, it's a +2A/+3 |
| Detect Pentagon vs 128K | Time the contention pattern at a known contended address — Pentagon uses "early" timing, 128K uses "late" |
| Detect ZX Spectrum Next | Read the `NEXTREG` registers via port `#243B` — if it responds, it's a Next |
| Safe screen writes | Always write to bank 5 at `#4000–#5AFF` and set `#7FFD` bit 3 = 0 first; restore previous paging afterward |
| Safe RAM access | Avoid banks 0, 1, 3, 4, 5, 7 for cycle-critical code; bank 2 at `#8000–#BFFF` is uncontended on every model |
| Safe INT handler | IM 1 vectors through `#0038` — the ROM is always paged during INT, so this is safe; IM 2 requires the vector table to be in uncontended RAM |

---

## Cross-References

- [io_port_map.md](io_port_map.md) — I/O port reference (companion lookup table)
- [timing_reference.md](timing_reference.md) — cycle-exact timing tables including contention delays
- [rom_routines.md](rom_routines.md) — full ROM routine entry point list
- [memory_and_io_48k.md](../05_development/03_memory_and_io/memory_and_io_48k.md) — 48K deep dive
- [memory_and_io_128k.md](../05_development/03_memory_and_io/memory_and_io_128k.md) — 128K/+2 deep dive
- [memory_and_io_plus3.md](../05_development/03_memory_and_io/memory_and_io_plus3.md) — +2A/+3 deep dive
- [memory_and_io_pentagon.md](../05_development/03_memory_and_io/memory_and_io_pentagon.md) — Pentagon deep dive
- [memory_and_io_next.md](../05_development/03_memory_and_io/memory_and_io_next.md) — ZX Spectrum Next deep dive
- [bank_switching_patterns.md](../05_development/03_memory_and_io/bank_switching_patterns.md) — programming patterns
- [contention_model.md](../05_development/03_memory_and_io/contention_model.md) — contention deep dive
- [screen_layout.md](../05_development/03_memory_and_io/screen_layout.md) — screen address calculation

---

## References

- Ian Logan, Frank O'Hara — *The [Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip)*, Melbourne House, 1983 — canonical ROM listing with system variable addresses
- Sinclair Research — *ZX Spectrum BASIC Programming* by Steven Vickers, 1982 — original 16K/48K manual with memory map and system variables
- Amstrad — *[ZX Spectrum +2 Manual*, 1987 and *+3 Manual](https://www.worldofspectrum.org/hardware.html)*, 1987 — original 128K/+2/+2A/+3 documentation
- [Chris Smith — *The ZX Spectrum ULA](http://www.zxdesign.info/)*, 2010 — definitive ULA reverse-engineering, explains contention
- Black_Cat — *BC Info Guide #4*, 2008 — port and memory map tables for clones ([github mirror](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt))
- World of Spectrum — [memory maps FAQ](https://worldofspectrum.org/faq/reference/memorymap.htm) and [128K memory map](https://worldofspectrum.org/faq/reference/128kmemorymap.htm)
- ZX Spectrum Next — *ZX Spectrum Next Hardware Register Reference*, [official spec](https://gitlab.com/thesmog358/tbblue/-/blob/master/docs/NextRegisterReference.pdf)
