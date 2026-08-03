[← Home](../../README.md) · [Original Hardware](README.md)

# ZX Spectrum +2A / +3 — Amstrad's ASIC Redesign

The **ZX Spectrum +2A** (black case, launched April 1987, £149.99) and the **ZX Spectrum +3** (black case with built-in 3-inch floppy drive, launched December 1987, £199.99) are **the most internally-divergent models** in the Sinclair Spectrum lineage. Despite using the same case, keyboard, and most of the I/O as the +2 grey, the +2A and +3 are **not software-compatible with the 128K/+2** at the cycle-precise level — they use a **completely different gate array** (the Amstrad **40084** and **40085** ASICs, replacing Sinclair's 8K5/7K0), a **different contention model** (per-bank, MREQ-gated, on banks 4/5/6/7 instead of 1/3/5/7), an **additional paging register** (`#1FFD` for special paging modes and disk control), and an **enlarged ROM** (64 KB, four switchable 16 KB banks, adding the +3 DOS disk operating system).

The +2A was Amstrad's cost-reduction exercise on the +2 grey: replace the discrete logic and Sinclair gate array with a single custom ASIC, reduce the PCB complexity, and replace the 32 KB ROM with a 64 KB ROM to incorporate +3 DOS without requiring a separate floppy interface. The +3 is the same machine with the addition of an **internal 3-inch floppy drive** (using the same Hitachi HFD-305S mechanism as the Amstrad CPC 6128 and PCW 8256) and the **uPD765A** floppy disk controller chip.

The +2A and +3 are the **most technically interesting** Spectrum models from a hardware-engineering perspective: they represent Amstrad's only significant redesign of the Spectrum's core logic. Their differences from the earlier Sinclair-designed models cause subtle incompatibilities that have been the subject of decades of demoscene discussion.

> [!NOTE]
> This article covers what is **new and different** in the +2A/+3: the Amstrad ASIC, the new contention model, the `#1FFD` register, the +3 disk subsystem, and the ROM layout. For aspects that are identical to the +2 (case, keyboard, ports, AY chip), see [zx_spectrum_plus2.md](zx_spectrum_plus2.md).

---

## History

### The +2A (April 1987)

Six months after launching the +2 grey, Amstrad released the **+2A** (the "A" stands for "Amstrad ASIC", reflecting the new gate array design). The +2A was produced in parallel with the +2 grey for about a year (mid-1987 to mid-1988), then entirely replaced the +2 grey in production. By 1989, only the +2A and +3 remained in Amstrad's Spectrum line.

The +2A's external appearance is nearly identical to the +2 grey, except:
- **Black case** instead of grey (this is the easiest way to distinguish a +2A from a +2)
- **Same keyboard** (64-key full-travel, same layout)
- **Same connectors** (with one addition: a disk drive connector at the rear, present even on machines without the internal disk drive)
- **Same power supply** (9V DC external adapter)

### The +3 (December 1987)

The +3 is a +2A with an internal floppy disk drive. Launched in December 1987 at £199.99, the +3 was Amstrad's attempt to extend the Spectrum's commercial life by adding disk-based software distribution, competing with the Amstrad CPC 6128 and Commodore 64C with 1541 drive.

The +3 uses the **Hitachi HFD-305S** 3-inch floppy drive mechanism — the same drive used in the Amstrad CPC 6128, Amstrad PCW 8256/8512, and several other Amstrad products. This is a single-sided, double-density, 40-track drive formatted to **175 KB** per disk in the +3's own DOS format. The 3-inch disk format was obsolete by the late 1980s (3.5-inch had won the format war), but Amstrad had invested heavily in 3-inch drives for the CPC line and used them across their products.

The +3 was **commercially unsuccessful** compared to the +2A. Software publishers were reluctant to release games on 3-inch disk when most Spectrum owners had tape-based +2s, and the £50 price premium over the +2A was not justified for most consumers. The +3 sold only about 125,000 units over its production life (1987–1990), versus the +2A's estimated 750,000 units.

### Why the +2A/+3 Matter

The +2A and +3 introduced three architectural changes that affected all later Spectrum hardware:

1. **The Amstrad ASIC (40084/40085)** — a full custom chip replacing the Sinclair 8K5/7K0 gate array, with different contention timing
2. **The `#1FFD` paging register** — extends memory paging beyond the 128K's `#7FFD` with special paging modes and disk drive control
3. **The +3 DOS** — a real disk operating system built into the ROM, derived from the Amstrad CPC's AMSDOS / PCW's CP/M loader

---

## The Amstrad ASIC (40084 / 40085)

The +2A and +3 replace Sinclair's 8K5/7K0 gate array with two Amstrad-designed ASICs:

- **40084** — gate array (similar role to Sinclair 8K5: video, banking, contention, `#FE` and `#7FFD` registers)
- **40085** — disk interface and additional paging logic (handles `#1FFD` register, disk FDC, and the special paging modes)

The two ASICs are paired: 40084 alone is sufficient for a +2A, and 40085 is added on the +3 (and on +2A machines fitted with the optional external disk drive). The 40085 is what provides the +2A/+3 with their distinctive special paging modes and disk support.

### Why Replace the Sinclair Gate Array?

Amstrad's motivation for replacing the Sinclair gate array was primarily **cost reduction**:

- The Sinclair 8K5/7K0 was sourced from a specific foundry at a fixed price; Amstrad wanted to use their own foundry relationships
- The Sinclair gate array required several external 74LS-series chips for address decoding and paging logic; integrating these into the ASIC reduced chip count
- The 32 KB ROM was insufficient for +3 DOS; adding a 64 KB ROM required additional banking logic, which was free if the ASIC was being redesigned anyway
- Amstrad's existing CPC and PCW product lines used custom ASICs; designing a similar ASIC for the Spectrum gave economies of scale

### What the ASIC Changes

The new ASIC's most consequential changes are:

| Parameter | Sinclair 8K5/7K0 (128K/+2) | Amstrad 40084/40085 (+2A/+3) |
|---|---|---|
| **Contended banks** | 1, 3, 5, 7 (odd banks) | 4, 5, 6, 7 (high banks) |
| **Contention gating** | On all bus cycles | **MREQ-gated** — only on real memory accesses |
| **Delay pattern** | `(6, 5, 4, 3, 2, 1, 0, 0)` | `(1, 0, 7, 6, 5, 4, 3, 2)` (same values, rotated) |
| **Pattern start T-state** | 14361 | 14361 |
| **Free gap before resumption** | — | 100 T-states, resumes at T=14589 |
| **`#7FFD` bit 1 (DIS)** | Disables further `#7FFD` writes | Same behavior, preserved for compatibility |
| **Additional paging register** | — | `#1FFD` (special modes, disk motor, ROM bank) |

The most important change is **MREQ gating**. On the Sinclair gate array (128K/+2), the ULA contends **any access to a contended bank**, regardless of whether it is a memory access (MREQ) or an I/O access (IORQ). This means that on the 128K/+2, `OUT (#FE), A` or `OUT (#7FFD), A` will trigger contention if the address falls in a contended bank's range — even though no memory is being accessed.

On the +2A/+3, the ASIC only contends memory accesses (when MREQ is asserted). I/O accesses (IORQ) **never trigger contention**, even when the address bits match a contended bank. This means:

- `OUT (#FE), A` is uncontended on the +2A/+3, but contended on the 128K/+2
- `OUT (#7FFD), A` is uncontended on the +2A/+3, but contended on the 128K/+2
- `OUT (#BFFD), A` (AY register writes) are uncontended on the +2A/+3, but contended on the 128K/+2

This is the source of many timing-sensitive incompatibilities. Demoscene productions that rely on the precise cycle count of `OUT (#FE), A` for multicolor effects will behave differently on the +2A/+3 vs the 128K/+2.

---

## Memory Contention on the +2A/+3

The +2A/+3's contention model uses different contended banks than the 128K/+2:

- **128K/+2**: banks 1, 3, 5, 7 are contended (the odd-numbered banks)
- **+2A/+3**: banks 4, 5, 6, 7 are contended (the high banks)

The reason for the change is in the ASIC's memory-decoder redesign: the Amstrad ASIC organizes the 128 KB of RAM as **two 64 KB blocks** (banks 0–3 and banks 4–7), with the high block sharing DRAM with the video circuitry. On the Sinclair gate array, the contended banks were interleaved with the screen banks for electrical reasons; on the Amstrad ASIC, the contended banks are grouped together for simpler decoding.

### Contention Timing Comparison

| Parameter | 48K | 128K / +2 | **+2A / +3** |
|---|---|---|---|
| **Scanline** | 224 T-states | 228 T-states | **228 T-states** |
| **Contention cell** | 8 T-states | 8 T-states (same as 48K) | **8 T-states** |
| **Delay pattern** | `(6,5,4,3,2,1,0,0)` | `(6,5,4,3,2,1,0,0)` | **`(1,0,7,6,5,4,3,2)`** |
| **Contended banks** | `#4000–#7FFF` (address) | 1, 3, 5, 7 (bank number) | **4, 5, 6, 7 (bank number)** |
| **MREQ gating** | No (contends any cycle) | No (contends any cycle) | **Yes (only memory accesses)** |
| **Pattern starts** | T=14335 | T=14361 | **T=14361** |
| **Free gap** | — | — | **100 T-states, resumes at T=14589** |
| **Frame rate** | 50.08 Hz | 49.89 Hz | **49.89 Hz** |

### Practical Implications for Software

The +2A/+3's contention differences mean:

1. **Software written for the 128K/+2 timing may glitch on the +2A/+3** if it depends on cycle-exact timing of `OUT` instructions in the contended region. This affects some multicolor effects and tape-loading routines.

2. **Software that runs entirely from uncontended banks is unaffected**. Code in bank 0 (at `#C000`) runs at the same speed on the 128K/+2 and the +2A/+3.

3. **The +2A/+3's contention is more predictable for non-memory I/O** — `OUT (#FE), A` always runs in the same number of cycles on the +2A/+3, regardless of where the CPU is executing from. This is why some modern demoscene productions explicitly target the +2A/+3.

4. **Detecting a +2A/+3 from software** is possible by timing `OUT (#FE), A` from a contended bank and observing whether the cycle count matches the 128K/+2's contended pattern or the +2A/+3's uncontended pattern. The ROM does this on boot to detect the machine type.

For the programmer-facing view of contention with per-T-state tables, see [contention_model.md](../../05_development/03_memory_and_io/contention_model.md) and [contention_timing.md](../../05_development/05_display_and_timing/contention_timing.md).

---

## The `#1FFD` Paging Register

The +2A/+3 adds a second paging register at I/O port **`#1FFD`** (write-only). This register provides the new features that the `#7FFD` cannot fit:

```
OUT (#1FFD), A — +2A/+3 extension paging register (write-only):

  Bit   7  6  5  4  3  2  1  0
      ┌────┬────┬────┬────┬────┬────┬────┬────┐
      │ x  │ x  │ x  │ x  │ x  │ROM │PAG │DISK|
      └────┴────┴────┴────┴────┴────┴────┴────┘

  Bit  0 (DISK):  Disk motor control (0 = motor off, 1 = motor on)
  Bit  1 (PAG):   Paging mode (0 = normal 128K mode, 1 = special paging mode)
  Bit  2 (ROM):   ROM bank select within the selected ROM page
  Bits 3–7:       Unused
```

### Paging Modes (Bit 1)

The +2A/+3 has **two distinct paging modes**, switched via bit 1 of `#1FFD`:

#### Normal 128K Mode (bit 1 = 0)

This is the default mode at power-on. The +2A/+3 behaves like a 128K/+2: `#7FFD` controls bank selection, ROM select (between two banks), and shadow screen. This mode exists for **backward compatibility** with software that does not know about the `#1FFD` register.

In this mode, the 64 KB ROM is treated as **two 32 KB halves**: ROM page 0 (banks 0+1 of the physical ROM) is selected by `#7FFD` bit 4 = 0, ROM page 1 (banks 2+3 of the physical ROM) is selected by `#7FFD` bit 4 = 1. The exact 16 KB bank within each half is selected by `#1FFD` bit 2.

#### Special Paging Mode (bit 1 = 1)

This is the new mode enabled by setting `#1FFD` bit 1. It changes the memory map completely:

- **`#0000–#1FFF`**: RAM (the low 8 KB of the currently-paged RAM bank, exposed at the bottom of the address space — **the ROM is disabled**)
- **`#2000–#3FFF`**: RAM (the next 8 KB)
- **`#4000–#7FFF`**: RAM bank 5 (fixed, contains the screen)
- **`#8000–#BFFF`**: RAM bank 2 (fixed)
- **`#C000–#FFFF`**: RAM bank 0–7 (switchable via `#7FFD` bits 0–2)

The key feature of special paging mode is the **first 16 KB (`#0000–#3FFF`)** is now RAM, not ROM. This allows software to:

- Run with no ROM active (full RAM-based execution)
- Provide a custom interrupt vector table at `#0000–#01FF` (instead of the ROM's hardcoded IM 1 vector at `#0038`)
- Implement custom RST handlers at `#0000`, `#0008`, `#0010`, etc.
- Use IM 2 with the vector table starting at `#0000`

The cost: software in special paging mode **cannot call any ROM routine**, because the ROM is not mapped. All ROM functionality must be replaced by equivalent code in RAM.

This mode is **rarely used** outside of demoscene productions and tape-loaders that need precise control over interrupts. Commercial software typically stays in normal 128K mode for compatibility.

### ROM Banking (Bit 2)

Bit 2 of `#1FFD` selects between two 16 KB banks within the currently-selected ROM page:

- In **normal 128K mode** with `#7FFD` bit 4 = 0: bit 2 selects between ROM bank 0 (the 128K editor ROM, default) and ROM bank 2 (an alternate bank, rarely used)
- In **normal 128K mode** with `#7FFD` bit 4 = 1: bit 2 selects between ROM bank 1 (the 48K BASIC ROM, default) and ROM bank 3 (the +3 DOS ROM)

To access the +3 DOS ROM from BASIC, software writes `#7FFD` bit 4 = 1 (selecting ROM page 1) and `#1FFD` bit 2 = 1 (selecting bank 3 within that page). The ROM's `CAT`, `LOAD *`, and `SAVE *` commands do this automatically.

---

## The +3 Disk Subsystem

The +3's floppy disk subsystem consists of:

- **Hitachi HFD-305S** 3-inch floppy drive mechanism (single-sided, double-density, 40 tracks)
- **uPD765A** floppy disk controller (FDC) chip
- **ROM bank 3** — the +3 DOS ROM (16 KB) containing the disk operating system

> [!NOTE]
> The +3 has **128 KB of total RAM**, identical to the +2A — not 256 KB. The disk subsystem uses a portion of the existing RAM (typically in bank 0) as a sector buffer; no extra RAM is fitted.

The disk subsystem is accessed via two new I/O ports:

- **`#3FFD`** — FDC status register (read) / command register (write)
- **`#2FFD`** — FDC track register
- **`#1FFD`** — FDC data register (also handles paging mode, motor control)

(The exact port map varies between sources. See [plus3_floppy.md](../../03_io/storage/plus3_floppy.md) for the canonical reference.)

### +3 DOS

The +3 DOS is a **disk operating system** built into ROM bank 3. It provides:

- **Disk file operations**: `CAT`, `LOAD *"filename"`, `SAVE *"filename"`, `ERASE`, `FORMAT`, `COPY`
- **Drive control**: motor on/off, disk change detection, write protection
- **BASIC extensions**: the `*` syntax (as in `LOAD *"GAME"`) indicates a disk operation rather than a tape operation
- **File system**: CP/M-compatible directory format, 175 KB formatted capacity per disk

The +3 DOS is **derived from Amstrad's AMSDOS** (used on the Amstrad CPC), which is itself derived from CP/M 2.2. The directory format is compatible with the CP/M format used on Amstrad PCW machines, allowing disk interchange with those systems.

For more on the +3's floppy subsystem and the +3 DOS, see [plus3_floppy.md](../../03_io/storage/plus3_floppy.md) and [plus3_dos_format.md](../../03_io/storage/plus3_dos_format.md).

---

## ROM Contents

The +2A/+3 contains a **64 KB mask ROM** organized as four switchable 16 KB banks. Only one bank is visible at `#0000–#3FFF` at any time. The bank selection logic combines `#7FFD` bit 4 (ROM page) and `#1FFD` bit 2 (bank within page):

| `#7FFD` bit 4 | `#1FFD` bit 2 | **Active ROM bank** | Contents |
|---|---|---|---|
| 0 | 0 | **Bank 0** | 128K editor ROM (identical to the 128K/+2 bank 0 — the 128K BASIC, editor, and tape-load/save routines) |
| 0 | 1 | **Bank 2** | 128K editor ROM variant (used by some +2A/+3 firmware paths; on early ROMs, this is the Spanish-localised 128K editor; on later ROMs, effectively a duplicate of bank 0) |
| 1 | 0 | **Bank 1** | 48K BASIC ROM (the original 48K ROM image, for 48K-mode compatibility — selected by `USR 0` and the 48K BASIC menu option) |
| 1 | 1 | **Bank 3** | **+3 DOS** ROM (the disk operating system, accessible only on the +3; on the +2A without a disk drive, this bank contains a stub that prints `DISK ERROR`) |

At power-on, the ROM is in **normal 128K mode**, `#7FFD` bit 4 = 0, `#1FFD` bit 2 = 0 — i.e. ROM bank 0 (the 128K editor) is visible at `#0000–#3FFF`. The +3's boot sequence then jumps through the editor ROM to perform a cold-start check, and if a disk is present in drive A:, it attempts to boot from it via bank 3.

> [!NOTE]
> The **+2A's** ROM is also 64 KB / 4-bank, but bank 3 contains a placeholder DOS stub rather than the full +3 DOS. The +2A and +3 share the same ROM image otherwise. Some +2A machines can be upgraded to +3 DOS by simply replacing the ROM chip (provided the FDC and drive are fitted).

For the canonical ROM dump reference and disassembly notes, see [rom_versions.md](../../04_operating_systems/rom_versions.md) (catalog of all ROM versions) and [plus3dos.md](../../04_operating_systems/plus3dos.md) (+3 DOS internals).

---

## Comparison Across All Spectrum Models

| Feature | 16K/48K | 128K | +2 grey | **+2A** | **+3** |
|---|---|---|---|---|---|
| **RAM** | 16/48 KB | 128 KB | 128 KB | 128 KB | 128 KB |
| **ROM** | 16 KB | 32 KB (2 banks) | 32 KB (2 banks) | 64 KB (4 banks) | 64 KB (4 banks) |
| **Gate array** | Ferranti ULA | Sinclair 8K5/7K0 | Sinclair 8K5/7K0 | **Amstrad 40084/40085** | **Amstrad 40084/40085** |
| **Sound** | Beeper only | Beeper + AY-3-8912 | Beeper + AY-3-8912 | Beeper + AY-3-8912 | Beeper + AY-3-8912 |
| **Scanline** | 224 T-states | 228 T-states | 228 T-states | 228 T-states | 228 T-states |
| **Frame rate** | 50.08 Hz | 49.89 Hz | 49.89 Hz | 49.89 Hz | 49.89 Hz |
| **Contended banks** | `#4000–#7FFF` | 1, 3, 5, 7 | 1, 3, 5, 7 | **4, 5, 6, 7** | **4, 5, 6, 7** |
| **MREQ-gated contention** | No | No | No | **Yes** | **Yes** |
| **Paging registers** | none | `#7FFD` | `#7FFD` | `#7FFD` + `#1FFD` | `#7FFD` + `#1FFD` |
| **Special paging mode** | — | — | — | **Yes** | **Yes** |
| **Disk drive** | External only | External only | External only | External connector | **Internal 3-inch** |
| **RS-232 / MIDI** | No | Yes | No | No | No |
| **Keypad** | No | Yes | No | No | No |
| **Keyboard** | 40-key rubber | 65-key chiclet + keypad | 64-key full-travel | 64-key full-travel | 64-key full-travel |
| **Launch price** | £125/£175 | £179.95 | £149.99 | £149.99 | £199.99 |

---

## Common Issues and Repairs

### DRAM Failures

The +2A/+3's 16 DRAM chips (same `8464` family as the 128K/+2) are now over 35 years old and are the most common cause of failure. Symptoms include:

- **Random characters / colored blocks** on the boot screen — indicates DRAM in bank 5 (the screen bank) is faulty
- **Machine boots to a black screen** — DRAM in bank 0 (the boot bank) or the low RAM (`#4000–#7FFF`) is faulty
- **Random crashes after a few minutes of running** — a DRAM chip is intermittent; heat-related failures are common

Repair: desolder the faulty chip(s). Identifying the specific chip requires a DRAM tester or the diagnostic ROM available from the retro-computing community. Replacement `8464` chips are still available from surplus suppliers.

### ASIC (40084/40085) Failures

The Amstrad ASICs are generally reliable, but failures do occur — especially on machines that have been subjected to voltage spikes from a faulty power supply. Symptoms include:

- **No video output** (blank screen, but the CPU is running) — 40084 video generation failed
- **Memory paging broken** (bank switching doesn't work, software crashes when accessing banked RAM) — 40084 or 40085 paging logic failed
- **Disk subsystem non-functional** (drive doesn't respond to motor on/off) — 40085 disk interface failed

Replacement ASICs are not manufactured and must be salvaged from donor boards. There is no modern FPGA/CPLD drop-in replacement for the 40084/40085 pair (unlike the Sinclair gate array, which has the Harlequin project).

### Disk Drive Maintenance (+3 only)

The Hitachi HFD-305S 3-inch drive is the most failure-prone component of the +3. Common issues:

- **Drive motor belt perished** — the rubber belt driving the disk spindle stretches and snaps with age. Replacement belts are available from retro suppliers.
- **Read/write head dirty** — cleaning requires dismantling the drive and using isopropyl alcohol on the head. 3-inch disk shells are hard-sealed, so contamination is less common than with 5.25-inch drives.
- **Head alignment drifted** — the drive's stepper alignment drifts over time, causing disks formatted on the same drive to read fine but disks from other drives to fail. Realignment requires a calibration disk and an oscilloscope.
- **No new 3-inch media** — blank 3-inch disks are no longer manufactured. Existing stock is finite and degrading. The +3 community has developed a hardware mod to fit a 3.5-inch drive (which requires modifying the +3's drive cable and the +3 DOS's geometry assumptions).

For details on the +3's floppy subsystem and the HFD-305S, see [plus3_floppy.md](../../03_io/storage/plus3_floppy.md).

### ROM Corruption

The +2A/+3's mask ROM is a 27C256-class EPROM (or mask ROM in early units). Rare failures manifest as:
- **Garbage characters at boot** — ROM bank 0 partially corrupted
- **48K mode broken** (`USR 0` crashes) — ROM bank 1 corrupted
- **+3 DOS commands fail with `DISK ERROR` on the +3** — ROM bank 3 corrupted

The ROM can be replaced with a 27C256 EPROM programmed with the canonical +2A or +3 ROM dump. Several community-maintained ROM images exist with bug fixes (e.g. the well-known `+3E` ROM patch which fixes RAM-disc support and adds an NMI diagnostic menu).

---

## Cross-References

- [zx_spectrum_16k_48k.md](zx_spectrum_16k_48k.md) — the original Sinclair 16K/48K hardware (the design the +2A/+3 still partially emulates)
- [zx_spectrum_128.md](zx_spectrum_128.md) — the 128K "Toast Rack" (architecture the +2A/+3 nominally extends)
- [zx_spectrum_plus2.md](zx_spectrum_plus2.md) — the +2 grey (same case/keyboard; predecessor with Sinclair gate array)
- [ula_architecture.md](ula_architecture.md) — internal architecture of the Sinclair gate array (for contrast with the Amstrad ASIC)
- [rom_versions.md](../../04_operating_systems/rom_versions.md) — catalog of all Spectrum ROM versions including +2A/+3 four-bank ROM
- [plus3dos.md](../../04_operating_systems/plus3dos.md) — +3 DOS internals and ROM bank 3 disassembly
- [memory_and_io_plus3.md](../../05_development/03_memory_and_io/memory_and_io_plus3.md) — programmer-facing view of +2A/+3 memory and I/O ports
- [contention_model.md](../../05_development/03_memory_and_io/contention_model.md) — per-T-state contention tables for all models
- [io_port_decoding.md](../../05_development/03_memory_and_io/io_port_decoding.md) — port decoding for the `#1FFD` / `#2FFD` / `#3FFD` range
- [plus3_floppy.md](../../03_io/storage/plus3_floppy.md) — the +3's floppy disk subsystem in depth
- [plus3_dos_format.md](../../03_io/storage/plus3_dos_format.md) — +3 DOS disk format and CP/M compatibility

---

## References

- Amstrad +2A User Manual (Amstrad Consumer Electronics plc, 1987)
- Amstrad +3 User Manual and +3 DOS Guide (Amstrad Consumer Electronics plc, 1987)
- Ian Colquhoun's "The Hardware Book" — Spectrums +2A and +3 chapters
- Christopher Lampton, *The Spectrum +2A/+3 Hardware Reference* (comp.sys.sinclair archive)
- The "World of Spectrum" hardware registry — +2A and +3 entries (mirror at the Internet Archive)
- +3E ROM project by Andrew Owen (community-maintained bug-fixed +3 ROM)
- Zircon 2000 issue on Amstrad ASIC reverse-engineering (Russian hardware zine, English translation available)
- Sinclair/Amstrad service manuals for the +2A (part 40084) and +3 (parts 40084/40085) — circuit diagrams and ASIC pinouts

