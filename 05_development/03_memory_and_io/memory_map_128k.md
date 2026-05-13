[← Home](../../README.md) · [Memory & I/O](README.md)

# ZX Spectrum 128K / +2 Memory Map — Paging, Shadow Screen, and Bank Switching

The 128K Spectrum (and the grey +2) has **128 KB of RAM** plus **32 KB of ROM** (two 16 KB ROM banks), but the Z80 can still only address **64 KB** at a time. The solution is **bank switching**: a paging register at port `#7FFD` maps different 16 KB RAM banks into the upper address range (`#C000`–`#FFFF`), and selects between two ROM banks at `#0000`–`#3FFF`.

> [!NOTE]
> This article covers the **128K and +2 (grey) memory map**. For the 48K memory map (no paging), see [memory_map_48k.md](memory_map_48k.md). For the +2A/+3 which has additional paging modes, see [memory_map_plus3.md](memory_map_plus3.md). For Pentagon memory expansions (512K/1024K), see [memory_map_pentagon.md](memory_map_pentagon.md).

---

## Overview

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
> **CPU view vs ULA view**: Bank 5 is always mapped at `#4000`–`#7FFF` from the CPU's perspective — that never changes. But the **ULA can render from either Bank 5 or Bank 7**, regardless of where Bank 7 is currently paged. When the screen select bit (bit 3 of `#7FFD`) is set to 1, the ULA fetches pixel and attribute data from Bank 7's screen area — even if Bank 7 is paged into `#C000`–`#FFFF` at that moment, or not paged at all. The CPU address mapping and the ULA's display source are **independent**. See [Shadow Screen (Double Buffering)](#shadow-screen-double-buffering) below.

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

On the 128K/+2, **odd-numbered banks** (1, 3, 5, 7) are contended — the ULA may delay CPU access during screen display, just like the `#4000`–`#7FFF` range on the 48K. This is because these banks share the same physical DRAM chips as the screen bank.

- **Bank 5** (always at `#4000`–`#7FFF`): contended because it contains the screen
- **Banks 1, 3, 7**: contended even when paged into `#C000`–`#FFFF`
- **Banks 0, 2, 4, 6**: never contended

> [!WARNING]
> On the 128K/+2, contention applies to the **bank number**, not the address range. Code in bank 3 paged at `#C000` WILL be contended, even though `#C000` is not contended on the 48K. This is a common source of timing bugs when porting 48K software.

---

## The Paging Register (#7FFD)

Port `#7FFD` is the **single control point** for memory configuration:

```
OUT (#7FFD), A — 128K paging register:

  Bit    Function
  ─────  ─────────────────────────────────────────
  0-2    RAM bank paged into #C000–#FFFF (0–7)
  3      Screen select: 0 = bank 5, 1 = bank 7 (shadow screen)
  4      ROM select: 0 = ROM 0 (128K editor), 1 = ROM 1 (48K BASIC)
  5      Unused
  6      Unused
  7      Disable paging: 1 = lock #7FFD until next reset
  ─────  ─────────────────────────────────────────
```

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

Port `#7FFD` is **write-only**. You cannot read back the current paging state. If your program needs to know which bank is currently paged, you must **track it yourself**:

```z80
; Common pattern: save current paging state
CurrentBank: DB 0       ; Track which bank is at #C000

SetBank:
    LD   (CurrentBank),A  ; Save
    OUT  (#7FFD),A        ; Apply
    RET

GetBank:
    LD   A,(CurrentBank)
    RET
```

---

## ROM Banks

The 128K has **two 16 KB ROM banks**:

| ROM | Contents | Selected by |
|-----|----------|-------------|
| ROM 0 | 128K editor, menu system, 128K BASIC extensions, RAM disk commands | Bit 4 of `#7FFD` = 0 |
| ROM 1 | 48K BASIC ROM (identical to original 48K Spectrum) | Bit 4 of `#7FFD` = 1 |

```z80
; Switch to 48K ROM (ROM 1)
LD   A,%00010000     ; ROM=1, bank=0
OUT  (#7FFD),A
; Now #0000–#3FFF contains the 48K BASIC ROM
; All 48K ROM routines are accessible at their standard addresses
```

### TR-DOS ROM (on clones)

On the Pentagon, Scorpion, and other clones with the Beta 128 disk interface, a **third ROM** is present — the TR-DOS ROM. It is paged in via the Beta 128's port `#1FFD`, overriding the standard ROM at `#0000`–`#3FFF`. See [trdos.md](../../04_operating_systems/trdos.md) for details.

---

## Shadow Screen (Double Buffering)

One of the most important features of the 128K is the **shadow screen** in bank 7. By setting bit 3 of `#7FFD`, the ULA displays bank 7's pixel and attribute data instead of bank 5's.

### How the ULA Switches Display Source

The 128K has 128 KB of RAM built from **two sets of 64 KB DRAM**. The ULA has a dedicated address path into this DRAM that is **completely independent** of the CPU's address bus:

```
128K DRAM organization:

  DRAM set A (64 KB):  Banks 0, 2, 4, 6  (even banks)
  DRAM set B (64 KB):  Banks 1, 3, 5, 7  (odd banks)

  The ULA always fetches from DRAM set B (where the screen banks live).
  The screen select bit chooses WHICH bank within set B:

  Screen select = 0 → ULA reads Bank 5 pixel/attribute data
  Screen select = 1 → ULA reads Bank 7 pixel/attribute data

  The ULA generates its own 14-bit video address:
    - Bits 13–0 select pixel byte within the chosen bank
    - This is the SAME offset as #4000–#5AFF on Bank 5
    - But the ULA doesn't go through the CPU address bus at all
```

Key mechanism:

1. **The ULA has its own DRAM address counter** — it generates sequential addresses for pixel and attribute fetches during each scanline. This counter is hard-wired into the DRAM, not the Z80 bus.

2. **The screen select bit controls a multiplexer** — when you write `#7FFD`, bit 3 is latched into a flip-flop that controls which bank the ULA's address counter points to within DRAM set B. The ULA switches banks by changing the high-order address bits it presents to the DRAM — it does not go through the Z80's memory paging logic.

3. **The switch takes effect on the next scanline** — the ULA reads the screen select latch at the start of each scanline. Changing bit 3 mid-frame causes the ULA to start fetching from the new bank on the very next scanline.

### CPU and ULA Do Not Compete for the Same Bus

The CPU and ULA **do** share the same physical DRAM chips, but they access them on **alternating clock phases** within each T-state:

```
T-state clock phases (simplified):

  Phase 1 (first half of T-state):
    ULA reads DRAM for video (if during paper area)
    CPU is blocked from accessing contended banks

  Phase 2 (second half of T-state):
    CPU reads/writes DRAM
    ULA is idle (not fetching)

This is WHY contention exists — but only for ODD banks:
  - CPU accesses Bank 5 or 7 (DRAM set B) → may collide with ULA → contention
  - CPU accesses Bank 0, 2, 4, 6 (DRAM set A) → different chip set → no collision
```

The critical point: **the ULA always reads from DRAM set B** (odd banks). Whether it reads Bank 5 or Bank 7, it accesses the same physical DRAM chips. The CPU's access pattern is:

- Accessing **any odd bank** (1, 3, 5, 7) during paper area → contends with ULA → delayed
- Accessing **any even bank** (0, 2, 4, 6) during paper area → different DRAM chips → no delay
- Accessing anything during **border/blank** → ULA not fetching → no delay

This is true **regardless of which screen is active**. Switching to the shadow screen (Bank 7) does NOT change which DRAM set the ULA reads from — it's always set B. So contention behavior is the same whether displaying Bank 5 or Bank 7.

### Addressing the Shadow Screen

Bank 7's pixel and attribute data occupies the **same offsets** within the bank as Bank 5's:

```
Within any bank, the screen data is at these offsets:
  Pixels:      offset #0000–#17FF  (6144 bytes)
  Attributes:  offset #1800–#1AFF  (768 bytes)

CPU access (must page Bank 7 into #C000–#FFFF):
  Bank 7 pixels:      #C000 + #0000 = #C000–#D7FF
  Bank 7 attributes:  #C000 + #1800 = #D800–#DAFF

ULA access (independent of CPU paging):
  ULA always uses offset #0000–#1AFF within the selected bank
  It doesn't know or care about #C000 — that's a CPU address concept
```

This is why you write to `#C000`–`#D7FF` when Bank 7 is paged at `#C000` — the CPU sees it at that address, but the ULA reads the same bytes at their physical offset within the DRAM chip.

> [!TIP]
> When writing to Bank 7's screen area, the offset from a Bank 5 address is **#8000**. Add `#8000` to any 48K screen address to get the Bank 7 equivalent when it's paged at `#C000`: `#4000` → `#C000`, `#5800` → `#D800`.

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

The fixed regions mean:
- **Bank 5** is always accessible at `#4000`–`#7FFF` — the main screen is always here
- **Bank 2** is always accessible at `#8000`–`#BFFF` — good place for frequently used code/data
- Only the **upper 16 KB** can be switched — you can only access one additional bank at a time

---

## Memory Map — Default Configuration

On boot (after the 128K menu), the default configuration is:

```
#0000 - #3FFF   ROM 0 (128K editor)
#4000 - #7FFF   Bank 5 (screen + system vars + attributes)
#8000 - #BFFF   Bank 2 (BASIC program area)
#C000 - #FFFF   Bank 0 (free for BASIC / user programs)
```

### System Variables and Workspace

The 128K uses the same system variable area as the 48K (`#5C00`–`#5CB6`), plus additional variables:

| Address | Name | Purpose |
|---------|------|---------|
| `#5B00`–`#5BFF` | Printer buffer | Same as 48K |
| `#5C00`–`#5CB6` | System variables | Same as 48K |
| `#5CB6`–`#5CFF` | Channels + streams | Same as 48K |
| `#5CC5` | `BANK_M` | Backup of last value written to `#7FFD` |
| Additional 128K variables | | RAM disk parameters, bank allocation |

The 128K ROM also uses banks 4 and 6 for workspace (RAM disk cache, editor buffers). These are not available for user programs unless you override them.

### Reserved Banks

On the 128K, the ROM reserves:
- **Bank 5**: Screen, system variables, attributes (always at `#4000`–`#7FFF`)
- **Bank 2**: BASIC program, variables (always at `#8000`–`#BFFF`)
- **Banks 4, 6**: RAM disk and cache (used by 128K ROM)
- **Bank 0**: Default paged bank at `#C000`
- **Banks 1, 3, 7**: Available for user programs (7 = shadow screen)

---

## Accessing Data in Other Banks

To read or write data in a bank that's not currently paged in:

```z80
; Read a byte from bank 6, address #C000+16
; (which is offset 16 within bank 6's #C000 range)
ReadFromBank6:
    ; Save current bank
    LD   A,(CurrentBank)
    PUSH AF
    
    ; Page in bank 6
    LD   A,6
    CALL SetBank
    
    ; Read the byte
    LD   HL,#C010       ; Address in bank 6
    LD   A,(HL)         ; Read it
    LD   (result),A     ; Save result
    
    ; Restore original bank
    POP  AF
    CALL SetBank
    RET
```

### Fast Bank-Switching Pattern

For performance-critical code (games, demos), minimize bank switches:

```z80
; Copy 256 bytes from bank 3 to bank 0 (both at #C000 range)
CopyBetweenBanks:
    ; Page in source bank (3)
    LD   A,3
    OUT  (#7FFD),A
    
    ; Copy source to a buffer in fixed bank (bank 2 at #8000)
    LD   HL,#C000       ; Source (bank 3)
    LD   DE,#8000       ; Temp buffer (bank 2, always accessible)
    LD   BC,256
    LDIR
    
    ; Page in destination bank (0)
    LD   A,0
    OUT  (#7FFD),A
    
    ; Copy from buffer to destination
    LD   HL,#8000       ; Temp buffer
    LD   DE,#C000       ; Destination (bank 0)
    LD   BC,256
    LDIR
    RET
```

---

## Comparison with 48K

| Feature | 48K | 128K/+2 |
|---------|-----|---------|
| Total RAM | 48 KB | 128 KB (8 × 16 KB banks) |
| Total ROM | 16 KB | 32 KB (2 × 16 KB) |
| Address space | 64 KB, static | 64 KB, paged |
| Paging register | None | `#7FFD` (write-only) |
| Screen buffer | 1 (at `#4000`) | 2 (bank 5 + bank 7 shadow) |
| Contended banks | `#4000`–`#7FFF` | Banks 1, 3, 5, 7 (odd banks) |
| Non-contended RAM | `#8000`–`#FFFF` | Banks 0, 2, 4, 6 |

---

## Cross-References

- **48K memory map** (no paging): [memory_map_48k.md](memory_map_48k.md)
- **+2A/+3 memory map** (4 paging modes): [memory_map_plus3.md](memory_map_plus3.md)
- **Pentagon memory** (512K/1024K): [memory_map_pentagon.md](memory_map_pentagon.md)
- **I/O ports** (#7FFD, #1FFD, #FE): [io_ports.md](io_ports.md)
- **Bank switching patterns** (practical techniques): [bank_switching_patterns.md](bank_switching_patterns.md)
- **Screen layout** (pixel addressing): [screen_layout.md](screen_layout.md)
- **ULA timing** (contention details): [ula_timing.md](../../02_hardware/original/ula_timing.md)
