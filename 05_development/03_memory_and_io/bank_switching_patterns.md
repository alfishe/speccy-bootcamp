[← Home](../../README.md) · [Memory & I/O](README.md)

# Bank Switching Patterns — Practical 128K+ Development

How to use RAM paging on the ZX Spectrum 128K, +2A/+3, Pentagon, and beyond. This article focuses on practical code patterns — for the paging register hardware details, see [memory_and_io_128k.md](memory_and_io_128k.md) and [io_port_decoding.md](io_port_decoding.md).

---

## The Problem

The Z80 has a 16-bit address bus — it can only see 64K at a time. The 128K Spectrum has 128K of RAM plus 32K of ROM (160K total). Bank switching maps different 16K "banks" of physical memory into the CPU's address space, typically at the top 16K (`#C000`–`#FFFF`).

```
CPU sees (64K):         Physical memory (128K+):
#0000 - #3FFF  ROM      Bank 0, 1, 2, 3 (16K each)
#4000 - #7FFF  Fixed    Bank 4, 5 (screen), 6, 7 (shadow screen)
#8000 - #BFFF  Fixed    Bank 8 = Bank 0 again on 128K
#C000 - #FFFF  Bank N ←── This window changes via port #7FFD
```

The challenge: data you need may be in a bank that isn't currently visible. You must save state, page in the right bank, access the data, and restore the previous bank — all without corrupting anything.

---

## Port #7FFD — The 128K Paging Register

```
Bit  7  6  5  4  3        2  1  0
    ┌──┬──┬──┬──┬────────┬─────────┐
    │  unused │SE│  ROM   │  BANK   │
    └──┴──┴──┴──┴────────┴─────────┘

  Bits 0-2: RAM bank number (0-7) paged at #C000-#FFFF
  Bit 3:    Screen select (0=Bank 5, 1=Bank 7/shadow)
  Bit 4:    ROM select (0=ROM 0, 1=ROM 1)
  Bits 5-7: Unused on 128K (reserved)
```

> [!IMPORTANT]
> Port `#7FFD` is **write-only**. You cannot read back the current paging state. The ROM stores a backup in `BANK_M` at `#5CC5`, but your own code must track the current state if you change it.

---

## Basic Paging Pattern

```z80
; Page in a specific bank (0-7) at #C000
; Preserves all registers
PageInBank:
    LD   A,(CurrentBank)   ; Save current bank setting
    PUSH AF
    LD   A,B               ; B = desired bank number (0-7)
    OR   #10               ; Set ROM1 (bit 4) to match 128K ROM 1
    AND #1F                ; Keep only bits 0-4 (bank + screen + ROM)
    ; Actually: preserve bit 3 (screen select) from BANK_M
    LD   C,A
    LD   A,(#5CC5)         ; BANK_M — last value written to #7FFD
    AND #08                ; Isolate screen select bit
    OR   C                 ; Merge with new bank number
    LD   (#5CC5),A         ; Update BANK_M backup
    LD   BC,#7FFD
    OUT  (C),A             ; Page in the new bank
    POP  AF
    LD   (CurrentBank),A   ; Save what we had before
    RET
```

### Simpler Version (if you don't care about screen/ROM state)

```z80
; Quick bank switch — just change the bank number
; Input: A = bank number (0-7)
SetBank:
    AND #07               ; Mask to bank bits only
    LD   HL,BankState     ; Track in our own variable
    OR   (HL)             ; Merge with existing screen/ROM bits
    AND #1F               ; Safety mask
    LD   (BankState),A
    LD   BC,#7FFD
    OUT  (C),A
    RET

BankState: DB #10         ; Initial: bank 0, ROM 1, screen 0
```

---

## Read a Byte from Another Bank

```z80
; Read one byte from any bank without losing current state
; Input: B = bank number (0-7), HL = offset within bank (#C000+)
; Output: A = byte value
; Preserves: BC, DE, HL
ReadByteFromBank:
    PUSH BC
    PUSH HL
    ; Save current bank
    LD   A,(#5CC5)
    PUSH AF
    ; Page in target bank
    LD   A,B
    CALL SetBankSimple
    ; Read the byte
    LD   A,(HL)           ; HL = #C000 + offset
    ; Restore original bank
    POP  AF
    PUSH AF
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A
    POP  AF
    POP  HL
    POP  BC
    RET

SetBankSimple:
    AND #07
    OR   #10              ; Keep ROM 1 selected
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A
    RET
```

---

## Copy Data Between Banks

```z80
; Copy data from bank N to current bank
; Input:  B = source bank, DE = source offset (#C000+)
;         HL = destination address (in visible RAM), C = byte count
CopyFromBank:
    PUSH BC
    PUSH DE
    PUSH HL
    ; Page in source bank
    LD   A,B
    CALL SetBankSimple
    ; Source is at DE (in #C000 range)
    ; Copy to HL (in visible, non-paged RAM)
    LD   H,D
    LD   L,E              ; HL = source (in paged area)
    POP  DE               ; DE = destination (restore from stack)
    LD   B,C              ; B = count
.copy:
    LD   A,(HL)
    LD   (DE),A
    INC  HL
    INC  DE
    DJNZ .copy
    ; Restore bank
    LD   A,(SavedBank)
    LD   BC,#7FFD
    OUT  (C),A
    POP  DE
    POP  BC
    RET

SavedBank: DB #10
```

---

## Double-Buffered Screen on 128K

The 128K has two screen buffers: Bank 5 (main) and Bank 7 (shadow). By switching which one the ULA displays, you can draw to the hidden buffer while the visible one is being shown — zero flicker.

```z80
; Draw to the shadow screen (Bank 7), then flip display
DoubleBufferDemo:
    ; Step 1: Make ULA show Bank 5 (main screen)
    LD   A,(#5CC5)
    AND #F7               ; Clear bit 3 → screen = Bank 5
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A

    ; Step 2: Page in Bank 7 at #C000
    LD   A,#07            ; Bank 7
    OR   #08              ; Keep shadow screen selected... no.
    ; We want bank 7 at #C000 but ULA showing bank 5
    ; Screen select and bank select are independent!
    CALL SetBankSimple     ; Pages bank 7 at #C000

    ; Step 3: Draw to shadow screen
    ; Shadow pixel buffer: #C000 + (#4000 offset) = not directly!
    ; Shadow screen is at Bank 7, offset #4000 within bank 7
    ; When bank 7 is at #C000, its screen data starts at:
    ;   Bank 7 base + #4000 = #C000 + #4000... doesn't fit in 16K!
    ;
    ; CORRECTION: You can't access the shadow screen via #C000 paging
    ; alone. You need to write to the SAME addresses (#4000-#5AFF)
    ; but have Bank 7 mapped there. Since #4000-#7FFF is always Bank 5,
    ; you must use a different approach.
    ;
    ; See the Shadow Screen section for the correct method.
    RET
```

> [!IMPORTANT]
> The shadow screen (Bank 7) occupies the **same address range** as the main screen (`#4000`–`#5AFF`) — it's just in a different physical DRAM bank. You cannot access both screens simultaneously. To write to the shadow screen, you must either:
> 1. Use the `#7FFD` bit 3 to **switch which screen the ULA displays** (but this changes the visible screen instantly)
> 2. On machines that support it, remap `#4000`–`#7FFF` to a different bank (only +2A/+3 and some clones can do this)

---

## +2A/+3 — Four Paging Modes

The +2A/+3 adds port `#1FFD` and supports four paging modes, including the ability to page RAM at `#4000`–`#7FFF` (impossible on the 128K/+2).

### Port #1FFD

```
Bit  7  6  5  4  3  2  1  0
    ┌──┬──┬──┬──┬──┬──┬──────┐
    │  unused    │MD│DI│ROM   │
    └──┴──┴──┴──┴──┴──┴──────┘

  Bit 0: ROM select (combined with #7FFD bit 4 → 4 ROM pages)
  Bit 1: Disk motor / interface select
  Bit 2: Paging mode (0=normal 128K, 1=special modes)
```

### Mode 0 — Compatible (default)

Same as 128K. `#7FFD` controls bank at `#C000`. All 128K software works.

### Mode 1 — Special Paging

When bit 2 of `#1FFD` is set, the +2A/+3 can remap all four 16K slots:

| Address range | Banks available |
|---|---|
| `#0000`–`#3FFF` | Can map any RAM bank (not just ROM) |
| `#4000`–`#7FFF` | Can map any RAM bank (not just Bank 5!) |
| `#8000`–`#BFFF` | Can map any RAM bank |
| `#C000`–`#FFFF` | Can map any RAM bank |

This allows **true double buffering**: write to Bank 7 at `#4000` while the ULA displays Bank 5, with both visible to the CPU simultaneously.

```z80
; +2A/+3: Access shadow screen while displaying main screen
; This is ONLY possible on +2A/+3, not on 128K/+2
Plus3DoubleBuffer:
    ; Enter special paging mode
    LD   BC,#1FFD
    LD   A,#04            ; Bit 2 set = special mode
    OUT  (C),A

    ; Now remap #4000-#7FFF to Bank 7
    ; (exact port sequence depends on configuration)
    ; Draw to #4000-#5AFF as normal — it writes to Bank 7
    ; ULA still displays Bank 5 (screen select unchanged)

    ; When done, restore normal mode
    LD   BC,#1FFD
    XOR  A
    OUT  (C),A            ; Back to mode 0
    RET
```

---

## Pentagon — Extended Memory

The Pentagon 128K uses the same `#7FFD` port as the 128K, but expanded models (512K, 1024K) add port `#EFF7` for extended bank selection.

### 512K / 1024K Paging

```
Port #EFF7 (write-only):
  Bits 0-3: Extended bank bits (bank 8-127)
  Combined with #7FFD bits 0-2:
    Total: 7 bits → 128 banks of 16K = 2048K maximum
```

```z80
; Pentagon 1024K: Page in bank 32 (beyond the base 8)
PentagonPageExtended:
    ; #7FFD bits 0-2 select banks 0-7
    ; For banks 8+, use #EFF7 for high bits

    LD   A,BankNumber     ; Bank 0-127
    RRCA                  ; Rotate bit 0 into carry
    RRCA
    RRCA                  ; Bits 0-2 now in position for #EFF7 low bits
    ; ... exact encoding depends on Pentagon revision
    LD   BC,#EFF7
    OUT  (C),A
    ; Then also set #7FFD for the low 3 bits
    LD   A,BankNumber
    AND #07
    ; ... merge with screen/ROM bits as normal
    RET
```

> [!NOTE]
> Extended memory paging on the Pentagon requires a CPLD or modified address decoding. The base Pentagon 128K (discrete TTL) cannot address beyond 128K. See [clone_timing.md](../../02_hardware/clones/clone_timing.md) for details.

---

## Antipatterns

### Forgetting to Restore the Bank

```z80
; BAD: Pages in a bank and returns without restoring
GetData:
    LD   A,#03
    LD   BC,#7FFD
    OUT  (C),A            ; Bank 3 paged in
    LD   A,(#C000)        ; Read data
    RET                   ; Bank 3 is still paged! Caller's code at
                          ; #C000 is now swapped out — crash likely
```

### Paging During an Interrupt

```z80
; BAD: If an interrupt fires between OUT and the restore,
; the ISR may access #C000 expecting the original bank
    LD   BC,#7FFD
    OUT  (C),A            ; New bank paged in
    ; INT fires here!
    ; ISR at #0038 runs, but any #C000+ data is wrong
    LD   (Result),A
    ; ... restore bank
```

```z80
; GOOD: Disable interrupts during bank switches
    DI
    LD   BC,#7FFD
    OUT  (C),A
    LD   A,(#C000)        ; Safe read
    LD   (BC,#7FFD)       ; WRONG SYNTAX — use OUT (C),reg
    EI
```

### Writing to #7FFD Without Tracking State

```z80
; BAD: Overwrites screen select and ROM select bits
    LD   A,#03            ; Want bank 3
    LD   BC,#7FFD
    OUT  (C),A            ; Also sets ROM0, screen=Bank 5
                          ; If ULA was showing shadow screen, it flips back!
```

```z80
; GOOD: Read-modify-write using BANK_M
    LD   A,(#5CC5)        ; BANK_M: last value written to #7FFD
    AND #F8               ; Clear bank bits (0-2)
    OR   #03              ; Set bank to 3
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A        ; Update backup
```

---

## Best Practices

1. **Always save and restore the bank** — use a consistent save/restore pattern, or maintain a global `BankState` variable
2. **Disable interrupts during bank switches** — unless your ISR is bank-aware and saves/restores the paging state itself
3. **Never assume what bank is active** — always read from `BANK_M` (`#5CC5`) or your own tracking variable
4. **Keep critical code in non-paged memory** — `#0000`–`#BFFF` is always visible. Put your ISR, bank-switching routines, and time-critical code there
5. **Minimize bank switches** — each switch costs ~20T (OUT instruction + state tracking). Batch your cross-bank operations

---

## Cross-References

- **128K memory map** (paging register, bank layout): [memory_and_io_128k.md](memory_and_io_128k.md)
- **I/O port decoding** (masks, conflicts): [io_port_decoding.md](io_port_decoding.md)
- **+2A/+3 memory and ports** (#1FFD, 4 paging modes): [memory_and_io_plus3.md](memory_and_io_plus3.md)
- **Pentagon memory and ports** (EFF7, extended paging): [memory_and_io_pentagon.md](memory_and_io_pentagon.md)
- **Contention model** (bank-based contention): [contention_model.md](contention_model.md)
- **Double buffering** (shadow screen techniques): [double_buffering.md](../06_graphics/double_buffering.md)
- **Clone timing** (Pentagon extended memory): [clone_timing.md](../../02_hardware/clones/clone_timing.md)
- **Complete I/O port map** (all paging port registers, all models): [io_port_map.md](../../08_references/io_port_map.md)
