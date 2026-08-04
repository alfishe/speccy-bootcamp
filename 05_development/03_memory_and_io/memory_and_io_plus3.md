[← Home](../../README.md) · [Memory & I/O](README.md)

# ZX Spectrum +2A / +3 — Memory Map and I/O Ports

The +2A and +3 use an **Amstrad gate array** instead of the Ferranti ULA, which changes everything about memory paging. While the 128K/+2 has one paging register (`#7FFD`) that can only switch the upper 16 KB, the +2A/+3 adds a second register (`#1FFD`) that enables **four paging modes** — including the ability to remap ALL four 16 KB slots, page RAM at `#0000` (replacing ROM), and access the shadow screen without displacing the visible one.

The +3 also adds an internal floppy drive controlled through additional FDC ports.

> [!NOTE]
> This article covers the **+2A and +3 memory map and I/O ports**. The +2A and +3 have identical memory architectures (the +3 just adds a floppy drive). For the 128K/+2, see [memory_and_io_128k.md](memory_and_io_128k.md). For I/O port decoding concepts, see [io_port_decoding.md](io_port_decoding.md).

---

## Memory Map — Mode 0 (Compatible, Default)

In the default mode, the +2A/+3 is fully compatible with the 128K:

```
Address range    Contents               Control
──────────────────────────────────────────────────────────
#0000 - #3FFF   ROM 0 or ROM 1         #7FFD bit 4
#4000 - #7FFF   Bank 5 (fixed)         Always Bank 5
#8000 - #BFFF   Bank 2 (fixed)         Always Bank 2
#C000 - #FFFF   Banks 0–7 (switchable) #7FFD bits 0–2
──────────────────────────────────────────────────────────
```

Identical to the 128K/+2. All 128K software works without modification.

---

## The Two Paging Registers

### Port #7FFD — Primary Paging (Same as 128K)

```
OUT (#7FFD), A — primary paging register (write-only):

  Bits 0–2: RAM bank paged at #C000 (0–7)  [in mode 0]
  Bit  3:   Screen select (0=Bank 5, 1=Bank 7)
  Bit  4:   ROM select (combined with #1FFD bit 0 → 4 ROM pages)
  Bit  7:   Disable paging (1 = lock both registers until reset)
```

Functionally identical to the 128K version, except:
- **Bit 4 combines with #1FFD bit 0** to select from 4 ROM pages instead of 2
- **Bit 7 locks BOTH #7FFD and #1FFD** when set to 1

### Port #1FFD — Extended Control (+2A/+3 Only)

```
OUT (#1FFD), A — +2A/+3 extended control register (write-only):

  Bit 0:   ROM bank select (combined with #7FFD bit 4 → 4 ROM pages)
  Bit 1:   Disk motor control (+3 only)
  Bit 2:   Paging mode (0 = compatible mode 0, 1 = special modes 1–3)
  Bit 3:   Printer strobe
  Bits 4–7: Unused

Decoding: A15=0, A14–A12=001, A1=0 — checks 5 lines → 128 mirrors
```

### ROM Bank Selection (4 Pages)

The +2A/+3 has **four 16 KB ROM pages**, selected by combining bit 4 of `#7FFD` and bit 0 of `#1FFD`:

| #7FFD bit 4 | #1FFD bit 0 | ROM page | Contents |
|---|---|---|---|
| 0 | 0 | 0 | 128K editor ROM (same as 128K ROM 0) |
| 1 | 0 | 1 | 48K BASIC ROM (same as 128K ROM 1) |
| 0 | 1 | 2 | +3 DOS / character set ROM |
| 1 | 1 | 3 | (duplicate of ROM 1 on most machines) |

---

## The Four Paging Modes

When bit 2 of `#1FFD` is set, the +2A/+3 can remap **all four 16 KB slots** independently. The mode is selected by bits 2–3 of `#7FFD` (repurposed in special mode):

### Mode 0 — Compatible (Default)

`#1FFD` bit 2 = 0. Same as 128K. `#7FFD` controls bank at `#C000` only. `#4000` and `#8000` are fixed to Banks 5 and 2.

### Mode 1 — Special Paging: RAM at #0000

`#1FFD` bit 2 = 1, `#7FFD` bits 2–3 = `00`.

```
Address range    Contents               Control
──────────────────────────────────────────────────────────
#0000 - #3FFF   RAM bank (not ROM!)     Bank 4
#4000 - #7FFF   Bank 5 (fixed)         Always Bank 5
#8000 - #BFFF   Bank 2 (fixed)         Always Bank 2
#C000 - #FFFF   RAM bank (switchable)  #7FFD bits 0–1 → banks 0,1,3,4,6,7
──────────────────────────────────────────────────────────
```

ROM is completely replaced by **Bank 4 at `#0000`**. The 128K ROM's RAM bridge routines at `#5B00` are no longer needed — code runs directly from RAM.

Use case: CP/M compatibility — the operating system loads into Bank 4 at `#0000` and takes over the machine.

### Mode 2 — Special Paging: Full Remap

`#1FFD` bit 2 = 1, `#7FFD` bits 2–3 = `01`.

```
Address range    Contents               Control
──────────────────────────────────────────────────────────
#0000 - #3FFF   RAM bank               Bank 0
#4000 - #7FFF   RAM bank (not Bank 5!) Bank 1
#8000 - #BFFF   RAM bank               Bank 2
#C000 - #FFFF   RAM bank               Bank 3
──────────────────────────────────────────────────────────
```

All four 16 KB slots map to **consecutive banks 0–3**. This means `#4000`–`#7FFF` is **Bank 1**, not Bank 5 — the screen is effectively disconnected from its normal position.

> [!IMPORTANT]
> This is the mode that enables **true double buffering**: you can map Bank 7 at `#4000` (for writing) while the ULA still displays Bank 5. But note that Mode 2 maps banks 0–3, not arbitrary banks. See Mode 3 for more flexible remapping.

### Mode 3 — Special Paging: Flexible Remap

`#1FFD` bit 2 = 1, `#7FFD` bits 2–3 = `10` or `11`.

```
Address range    Contents               Control
──────────────────────────────────────────────────────────
#0000 - #3FFF   RAM bank (switchable)  #7FFD bits 0–2 select bank
#4000 - #7FFF   RAM bank (not Bank 5!) Determined by internal logic
#8000 - #BFFF   Bank 2 (fixed)         Always Bank 2
#C000 - #FFFF   RAM bank (switchable)  Related to #0000 bank selection
──────────────────────────────────────────────────────────
```

The most flexible mode. You can page **any RAM bank at `#0000`** (replacing ROM) and independently control `#4000` and `#C000`.

> [!WARNING]
> The exact bank mapping in Modes 2 and 3 varies by source. The gate array's internal logic is not fully documented in the original Amstrad datasheets. When targeting +2A/+3, test on real hardware or a verified emulator (Fuse, ZEsarUX).

---

## True Double Buffering on +2A/+3

Unlike the 128K/+2 where accessing the shadow screen requires paging Bank 7 at `#C000` (displacing any code/data there), the +2A/+3 can map Bank 7 at `#4000` while the ULA displays Bank 5:

```z80
; +2A/+3: Write to shadow screen while displaying main screen
; This is ONLY possible on +2A/+3, not on 128K/+2

; Enter special paging mode (Mode 3)
LD   BC,#1FFD
LD   A,%00000100      ; Bit 2 = 1 → special mode
OUT  (C),A

; Now configure #7FFD for the desired bank layout
; Bank 7 at #4000 → write to #4000-#5AFF as normal → shadow screen
; ULA still displays Bank 5 (screen select unchanged)

; ... draw to shadow screen at #4000-#5AFF ...

; When done, flip display to show Bank 7
LD   BC,#7FFD
LD   A,(#5CC5)
SET  3,A              ; Screen select = Bank 7
OUT  (C),A

; Restore normal mode
LD   BC,#1FFD
XOR  A
OUT  (C),A            ; Back to mode 0
RET
```

---

## Contention — Amstrad Gate Array

The +2A/+3 has a **completely different contention model** from the 128K/+2:

| Property | 128K/+2 (Ferranti) | +2A/+3 (Gate Array) |
|---|---|---|
| Contended banks | 1, 3, 5, 7 (odd) | **4, 5, 6, 7** (high banks) |
| Delay pattern | 6-5-4-3-2-1-0-0 | **1-0-7-6-5-4-3-2** |
| I/O contention | Yes (A0=0 ports) | **No** (MREQ only) |
| Peak delay | 6T | **7T** |

> [!WARNING]
> Code that relies on the exact Ferranti contention pattern (6-5-4-3-2-1-0-0) for timing will break on the +2A/+3. The peak delay is 7T at a different T-state offset. See [contention_model.md](contention_model.md) for details.

Key differences:
- **I/O is never contended** — `OUT (#FE), A` takes the same time during paper as during border
- **Banks 4, 5, 6, 7** are contended (not 1, 3, 5, 7)
- **No early/late timing drift** — the gate array doesn't have the thermal drift of the Ferranti ULA

---

## I/O Port — +3 Floppy Disk Controller

The +3 has an internal **WD1772 FDC** (Floppy Disk Controller) connected through the gate array. The FDC is accessed via ports decoded by the gate array:

```
Port #1FFD:  Bit 1 = disk motor on/off (+3 only)
Port #3FFD:  FDC data register (read/write)
Port #2FFD:  FDC status/register select
```

For complete +3 floppy programming, see [plus3_floppy.md](../../03_io/storage/plus3_floppy.md) and [plus3dos.md](../../04_operating_systems/plus3dos.md).

---

## Quick Reference — Port Summary

```
Port    Function                                     +2A/+3 specific
────────────────────────────────────────────────────────────────────
#FE     ULA/gate array: border, EAR, keyboard       No (same as all models)
#7FFD   Primary paging: bank, ROM, screen, lock     Extended ROM select (4 pages)
#1FFD   Extended control: mode, disk motor, ROM      YES — +2A/+3 only
#FFFD   AY register select                           No
#BFFD   AY register data                             No
#2FFD   +3 FDC status/register select                +3 only
#3FFD   +3 FDC data                                  +3 only
#1F     Kempston joystick (if interface present)     No
────────────────────────────────────────────────────────────────────
```

---

## Cross-References

- **128K/+2 memory and ports** (#7FFD, AY, shadow screen): [memory_and_io_128k.md](memory_and_io_128k.md)
- **Pentagon memory and ports** (EFF7, TR-DOS): [memory_and_io_pentagon.md](memory_and_io_pentagon.md)
- **I/O port decoding** (partial decoding, masks): [io_port_decoding.md](io_port_decoding.md)
- **Bank switching patterns** (practical techniques): [bank_switching_patterns.md](bank_switching_patterns.md)
- **Contention model** (gate array contention): [contention_model.md](contention_model.md)
- **+3 DOS** (floppy file system): [plus3dos.md](../../04_operating_systems/plus3dos.md)
- **+3 floppy hardware**: [plus3_floppy.md](../../03_io/storage/plus3_floppy.md)
- **AY programming**: [ay_programming.md](../../06_sound/hardware/ay_3_8912.md)
- **Complete I/O port map** (all ports, all models, decoding bitmasks): [io_port_map.md](../../10_references/io_port_map.md)

---

## References

### External references

- [Sinclair ZX Specifications (Martin Korth)](http://problemkaputt.de/zxdocs.htm) — canonical hardware reference for the +2A / +3 ASIC's 4 paging modes (`#1FFD` bits 0–1 combined with `#7FFD`), the gate array's address decode, and the special ROM configuration that exposes CP/M.
- [Amstrad +2A / +3 Service Manuals](https://zxfaq.eu/extra/amstrad_plus3_service_manual.pdf) — full schematics for the custom gate array that replaced the 128K's discrete paging logic, including the DRAM control signals and the address-decode equations that produce the 4 paging modes.
- [World of Spectrum — +3 DOS Programmer Guide](https://worldofspectrum.org/faq/reference/plus3dosreference.htm) — reference for the +3's floppy disk subsystem integration, including how `#1FFD` switches between the +3 DOS ROM, the 48K BASIC ROM, and the external CP/M boot ROM.
- [Spectrumpedia (Alessandro Grussu)](https://www.alessandrogrussu.it/zx/) — encyclopedic reference for the +2A / +3 lineage, including the Spanish +2 variant differences and the late Amstrad mainboard revisions that changed the gate array's contention behavior.
- [Complete Spectrum ROM Disassembly (Logan & O'Hara, 1983)](https://worldofspectrum.org/ROMdisassembly.zip) — primary-source reference for the 48K ROM routines that the +3 still exposes in compatibility mode, including the channel-I/O hooks that `#1FFD` redirects into the +3 DOS ROM.
