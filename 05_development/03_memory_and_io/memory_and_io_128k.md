[← Home](../../README.md) · [Memory & I/O](README.md)

# ZX Spectrum 128K / +2 — Memory Map and I/O Ports

The 128K Spectrum (and the grey +2) has **128 KB of RAM** plus **32 KB of ROM** (two 16 KB ROM banks), but the Z80 can still only address **64 KB** at a time. The solution is **bank switching**: a paging register at port `#7FFD` maps different 16 KB RAM banks into the upper address range (`#C000`–`#FFFF`), and selects between two ROM banks at `#0000`–`#3FFF`.

The 128K/+2 adds three important ports beyond the 48K's `#FE`: `#7FFD` (paging), `#FFFD`/`#BFFD` (AY sound chip), and uses the AY's I/O port for keypad reading.

> [!NOTE]
> This article covers the **128K and +2 (grey) memory map and I/O ports**. For the 48K (no paging, no AY), see [memory_and_io_48k.md](memory_and_io_48k.md). For the +2A/+3 with additional paging modes, see [memory_and_io_plus3.md](memory_and_io_plus3.md). For I/O port decoding concepts, see [io_port_decoding.md](io_port_decoding.md).

---

## Memory Map Overview

```
Address range    48K equivalent    128K contents
──────────────────────────────────────────────────────────────────
#0000 - #3FFF    ROM (16 KB)       ROM bank 0 or ROM bank 1 (switchable)
#4000 - #7FFF    Screen + attrs    Bank 5 (fixed) — always mapped here
#8000 - #BFFF    BASIC + free RAM  Bank 2 (fixed)
#C000 - #FFFF    BASIC + free RAM  Bank 0,1,3,4,6,7 (switchable via #7FFD)
──────────────────────────────────────────────────────────────────
```

The key difference from 48K: the upper 16 KB (`#C000`–`#FFFF`) can be **dynamically switched** between 8 different RAM banks by writing to port `#7FFD`.

> [!IMPORTANT]
> **CPU view vs ULA view**: Bank 5 is always mapped at `#4000`–`#7FFF` from the CPU's perspective — that never changes. But the **ULA can render from either Bank 5 or Bank 7**, regardless of where Bank 7 is currently paged. The CPU address mapping and the ULA's display source are **independent**. See [Shadow Screen](#shadow-screen-double-buffering) below.

---

## The 8 RAM Banks

The 128K has **8 banks** of 16 KB each, numbered 0–7:

```
Bank    Address when paged    Physical RAM     Contended
──────────────────────────────────────────────────────────
0       #C000–#FFFF           16 KB           No
1       #C000–#FFFF           16 KB           Yes (odd bank)
2       #8000–#BFFF (fixed)   16 KB           No
3       #C000–#FFFF           16 KB           Yes (odd bank)
4       #C000–#FFFF           16 KB           No
5       #4000–#7FFF (fixed)   16 KB           Yes (screen bank)
6       #C000–#FFFF           16 KB           No
7       #C000–#FFFF           16 KB           Yes (odd bank, shadow screen)
──────────────────────────────────────────────────────────
```

### Contention on 128K

On the 128K/+2, **odd-numbered banks** (1, 3, 5, 7) are contended — the ULA may delay CPU access during screen display. This is because these banks share the same physical DRAM chips as the screen bank.

- **Bank 5** (always at `#4000`–`#7FFF`): contended because it contains the screen
- **Banks 1, 3, 7**: contended even when paged into `#C000`–`#FFFF`
- **Banks 0, 2, 4, 6**: never contended

> [!WARNING]
> On the 128K/+2, contention applies to the **bank number**, not the address range. Code in bank 3 paged at `#C000` WILL be contended, even though `#C000` is not contended on the 48K. This is a common source of timing bugs when porting 48K software. See [contention_model.md](contention_model.md) for details.

---

## I/O Port — #7FFD (Memory Paging)

Port `#7FFD` is the **single control point** for memory configuration on the 128K:

```
OUT (#7FFD), A — 128K paging register (write-only):

  Bit   7  6  5  4  3  2  1  0
      ┌────┬────┬────┬────┬────┬────┬────┬────┐
      │DIS │ x  │ x  │ROM │SCR │B2  │B1  │B0  │
      └────┴────┴────┴────┴────┴────┴────┴────┘

  Bits 0–2 (B0–B2): RAM bank to page into #C000–#FFFF (0–7)
  Bit  3    (SCR):   Screen select (0 = bank 5, 1 = bank 7 shadow)
  Bit  4    (ROM):   ROM select (0 = 128K editor ROM, 1 = 48K BASIC ROM)
  Bit  5:            Unused
  Bit  6:            Unused
  Bit  7    (DIS):   Disable paging (1 = lock #7FFD until next reset)
```

### Decoding

Port `#7FFD` checks 6 address lines (relatively well-decoded for the Spectrum): A15=0, A14–A11=`0111`, A1=0. This gives 64 mirror addresses. Always use the canonical `#7FFD`. See [io_port_decoding.md](io_port_decoding.md) for the full decoding mask.

### Paging Examples

```z80
; Page bank 3 into #C000–#FFFF
LD   A,%00000011     ; Bank 3, ROM 0, screen 0
OUT  (#7FFD),A

; Switch to shadow screen (bank 7) — double buffering
LD   A,%00001000     ; Screen = bank 7, bank = 0
OUT  (#7FFD),A

; Switch to 48K BASIC ROM
LD   A,%00010000     ; ROM 1 (48K), bank 0
OUT  (#7FFD),A

; Page bank 7 and lock paging
LD   A,%10000111     ; DIS=1, bank 7
OUT  (#7FFD),A
; Now #7FFD is locked! No more paging until reset.
```

### Write-Only Warning

Port `#7FFD` is **write-only**. Reading it returns floating bus garbage. Track the current state yourself:

```z80
; The ROM stores a backup in BANK_M at #5CC5
; Your code should update this after every OUT (#7FFD)
CurrentBank: DB 0

SetBank:
    LD   (CurrentBank),A  ; Save
    LD   (#5CC5),A        ; Update BANK_M
    LD   BC,#7FFD
    OUT  (C),A            ; Apply
    RET
```

For practical bank-switching patterns, see [bank_switching_patterns.md](bank_switching_patterns.md).

---

## ROM Banks

The 128K has **two 16 KB ROM banks**:

| ROM | Contents | Selected by |
|-----|----------|-------------|
| ROM 0 | 128K editor, menu system, 128K BASIC extensions, RAM disk commands | Bit 4 of `#7FFD` = 0 |
| ROM 1 | 48K BASIC ROM (identical to original 48K Spectrum) | Bit 4 of `#7FFD` = 1 |

For how ROM 0 delegates to ROM 1 via the RAM bridge, see [rom_128k.md](../../04_operating_systems/rom_128k.md).

### TR-DOS ROM (on clones)

On the Pentagon, Scorpion, and other clones with the Beta 128 disk interface, a **third ROM** is present — the TR-DOS ROM. It is paged in via the Beta 128's port, overriding the standard ROM at `#0000`–`#3FFF`. See [memory_and_io_pentagon.md](memory_and_io_pentagon.md) for details.

---

## I/O Ports — #FFFD / #BFFD (AY Sound Chip)

The AY-3-8912 PSG (Programmable Sound Generator) is present on the 128K, +2, +2A, +3, and all clones. It connects through two ports:

```
OUT (#FFFD), A — Select AY register (register address port)
OUT (#BFFD), A — Write to selected AY register (register data port)
IN  A, (#FFFD) — Read from selected AY register
```

### Decoding

```
#FFFD:  A1=0, A0=1    → Register select
#BFFD:  A1=1, A0=1    → Register data
```

Both ports have many mirrors due to minimal decoding. Always use canonical addresses.

### Programming Example

```z80
; Set AY channel A tone to 440 Hz (approximately)
; AY clock = 1.7734 MHz on 128K, divider = 16
; Tone period = clock / (16 × frequency) = 1773400 / (16 × 440) ≈ 252

LD   BC,#FFFD
LD   A,#00           ; Register 0 = Channel A tone period fine
OUT  (C),A
LD   B,#BF           ; BC = #BFFD
LD   A,#252 & #FF    ; Fine = #FC
OUT  (C),A

LD   BC,#FFFD
LD   A,#01           ; Register 1 = Channel A tone period coarse
OUT  (C),A
LD   B,#BF
LD   A,#252 >> 8     ; Coarse = 0
OUT  (C),A
```

### AY I/O Port — Keypad

The AY-3-8912 has a built-in **8-bit I/O port** (register 14). On the 128K, this port is wired to the **external keypad connector** on the rear of the machine. On the +2, it's unused. The 128K editor ROM reads the keypad through this port.

For complete AY programming, see [ay_programming.md](../../06_sound/hardware/ay_3_8912.md).

---

## Shadow Screen (Double Buffering)

One of the most important features of the 128K is the **shadow screen** in bank 7. By setting bit 3 of `#7FFD`, the ULA displays bank 7's pixel and attribute data instead of bank 5's.

### How the ULA Switches Display Source

The 128K has 128 KB of RAM built from **two sets of 64 KB DRAM**:

```
128K DRAM organization:

  DRAM set A (64 KB):  Banks 0, 2, 4, 6  (even banks)
  DRAM set B (64 KB):  Banks 1, 3, 5, 7  (odd banks)

  The ULA always fetches from DRAM set B (where the screen banks live).
  The screen select bit chooses WHICH bank within set B:

  Screen select = 0 → ULA reads Bank 5 pixel/attribute data
  Screen select = 1 → ULA reads Bank 7 pixel/attribute data
```

Key points:

1. **The ULA has its own DRAM address counter** — it generates sequential addresses for pixel and attribute fetches during each scanline, hard-wired into the DRAM (not the Z80 bus).
2. **The screen select bit controls a multiplexer** — changing bit 3 of `#7FFD` switches which bank the ULA's address counter points to within DRAM set B.
3. **The switch takes effect on the next scanline** — the ULA reads the screen select latch at the start of each scanline.

### CPU and ULA Do Not Compete for the Same Bus

The CPU and ULA share the same physical DRAM chips, but access them on **alternating clock phases** within each T-state:

```
Phase 1 (first half):  ULA reads DRAM for video → CPU blocked from contended banks
Phase 2 (second half): CPU reads/writes DRAM → ULA idle (not fetching)
```

This is WHY contention exists — but only for ODD banks (DRAM set B). Even banks (set A) use different physical chips → no collision. This is true **regardless of which screen is active**.

### Addressing the Shadow Screen

Bank 7's screen data occupies the **same offsets** within the bank as Bank 5's:

```
Within any bank, screen data is at:
  Pixels:      offset #0000–#17FF  (6144 bytes)
  Attributes:  offset #1800–#1AFF  (768 bytes)

CPU access (must page Bank 7 into #C000–#FFFF):
  Bank 7 pixels:      #C000 + #0000 = #C000–#D7FF
  Bank 7 attributes:  #C000 + #1800 = #D800–#DAFF
```

> [!TIP]
> The offset from a Bank 5 address to its Bank 7 equivalent is **#8000**. Add `#8000` to any 48K screen address to get the Bank 7 address when it's paged at `#C000`: `#4000` → `#C000`, `#5800` → `#D800`.

---

## Fixed vs Switchable Regions

```
Address range    Contents               Fixed/Switchable
─────────────────────────────────────────────────────────
#0000 - #3FFF   ROM 0 or ROM 1         Switchable (bit 4 of #7FFD)
#4000 - #7FFF   Bank 5 (always)        FIXED — never changes
#8000 - #BFFF   Bank 2 (always)        FIXED — never changes
#C000 - #FFFF   Banks 0,1,3,4,6,7     Switchable (bits 0-2 of #7FFD)
─────────────────────────────────────────────────────────
```

- **Bank 5** is always accessible at `#4000`–`#7FFF` — the main screen is always here
- **Bank 2** is always accessible at `#8000`–`#BFFF` — good place for frequently used code/data
- Only the **upper 16 KB** can be switched — you can only access one additional bank at a time

---

## Default Configuration

On boot (after the 128K menu), the default configuration is:

```
#0000 - #3FFF   ROM 0 (128K editor)
#4000 - #7FFF   Bank 5 (screen + system vars + attributes)
#8000 - #BFFF   Bank 2 (BASIC program area)
#C000 - #FFFF   Bank 0 (free for BASIC / user programs)
```

### Reserved Banks

- **Bank 5**: Screen, system variables, attributes (always at `#4000`–`#7FFF`)
- **Bank 2**: BASIC program, variables (always at `#8000`–`#BFFF`)
- **Banks 4, 6**: RAM disk and cache (used by 128K ROM)
- **Bank 0**: Default paged bank at `#C000`
- **Banks 1, 3, 7**: Available for user programs (7 = shadow screen)

---

## Accessing Data in Other Banks

```z80
; Read a byte from bank 6, address #C000+16
ReadFromBank6:
    ; Save current bank
    LD   A,(#5CC5)
    PUSH AF
    ; Page in bank 6
    LD   A,6
    CALL SetBank
    ; Read the byte
    LD   HL,#C010
    LD   A,(HL)
    LD   (result),A
    ; Restore original bank
    POP  AF
    CALL SetBank
    RET

SetBank:
    AND  #07
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A
    RET
```

For complete bank-switching patterns, see [bank_switching_patterns.md](bank_switching_patterns.md).

---

## Comparison with 48K

| Feature | 48K | 128K/+2 |
|---------|-----|---------|
| Total RAM | 48 KB | 128 KB (8 × 16 KB banks) |
| Total ROM | 16 KB | 32 KB (2 × 16 KB) |
| Address space | 64 KB, static | 64 KB, paged |
| Paging register | None | `#7FFD` (write-only) |
| Screen buffer | 1 (at `#4000`) | 2 (bank 5 + bank 7 shadow) |
| Sound | Beeper only (#FE bit 0) | Beeper + AY-3-8912 (#FFFD/#BFFD) |
| Contended banks | `#4000`–`#7FFF` | Banks 1, 3, 5, 7 (odd banks) |
| Non-contended RAM | `#8000`–`#FFFF` | Banks 0, 2, 4, 6 |
| Keypad | None | AY I/O port (register 14) |

---

## Cross-References

- **48K memory and ports** (#FE, keyboard, beeper, no paging): [memory_and_io_48k.md](memory_and_io_48k.md)
- **+2A/+3 memory and ports** (#1FFD, 4 paging modes): [memory_and_io_plus3.md](memory_and_io_plus3.md)
- **Pentagon memory and ports** (EFF7, TR-DOS, extended paging): [memory_and_io_pentagon.md](memory_and_io_pentagon.md)
- **I/O port decoding** (partial decoding, masks, conflicts): [io_port_decoding.md](io_port_decoding.md)
- **Bank switching patterns** (practical techniques): [bank_switching_patterns.md](bank_switching_patterns.md)
- **Screen layout** (pixel addressing): [screen_layout.md](screen_layout.md)
- **Contention model** (bank-based contention): [contention_model.md](contention_model.md)
- **128K ROM internals** (dual-ROM, RAM bridge): [rom_128k.md](../../04_operating_systems/rom_128k.md)
- **AY programming** (register map, effects): [ay_programming.md](../../06_sound/hardware/ay_3_8912.md)
- **Complete I/O port map** (all ports, all models, decoding bitmasks): [io_port_map.md](../../10_references/io_port_map.md)

## References

### External references

- [Chris Smith — The ZX Spectrum ULA](http://www.zxdesign.info/) — definitive reference for the 128K's modified gate array / ASIC and the `#7FFD` paging port that selects ROM bank, RAM bank, and shadow screen.
- [Sinclair ZX Specifications](http://problemkaputt.de/zxdocs.htm) — the canonical 128K / +2 / +2A / +3 hardware reference; documents the partial address decoding on `#7FFD`, `#1FFD` (on +2A/+3), and the AY-3-8912 ports `#FFFD` / `#BFFD`.
- **Amstrad +2 / +3 Service Manuals** — full schematics including the gate array's address-decode equations and the DRAM control signals.
- [Spectrumpedia](https://speccy.wiki/) — cross-model reference covering the Soviet clones' divergent paging ports (Pentagon's `#7FFD` plus `#DFFD`/`#DFFF` for extended banks, ATM Turbo's `#FDF2`/`#FDF6`, etc.).
- **`tslabs/zx-evo` repository on GitHub** — the ZX Evolution's FPGA implementation; the most authoritative reference for how modern hardware replicates the 128K paging behavior and extends it.
