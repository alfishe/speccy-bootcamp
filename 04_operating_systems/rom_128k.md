[← Home](../README.md) · [Operating Systems](README.md)

# 128K ROM — Menu System, BASIC Extensions, and RAM Disk

The ZX Spectrum 128K (1986) and its Amstrad successors (+2, +2A, +3) ship with two ROM chips: **ROM 0** (the 128K-specific menu system and extended BASIC) and **ROM 1** (the original 48K ROM, retained for backward compatibility). This article covers the 128K ROM 0 features that distinguish it from the 48K ROM.

> **Status**: Stub — content in progress.

---

## ROM Layout

| ROM | Address range | Content |
|-----|--------------|---------|
| ROM 0 | `#0000`–`#3FFF` (when selected) | 128K menu system, BASIC extensions, AY sound driver, RAM disk, editor |
| ROM 1 | `#0000`–`#3FFF` (when selected) | Standard 48K ROM — full backward compatibility |

ROM selection is controlled by bit 4 of port `#7FFD`. At reset, ROM 0 is paged in and displays the start-up menu.

---

## Start-Up Menu

When the 128K powers on, ROM 0 presents a menu:

```
  128K BASIC
  Calculator
  Tape Loader
  128K BASIC (extended)
```

Selecting "128K BASIC" enters the extended editor. The menu itself is driven by a simple polling loop — it does not use interrupts beyond the standard IM1 ROM handler.

---

## 128K BASIC Extensions

The 128K ROM 0 adds several commands beyond the 48K BASIC set:

| Command | Description |
|---------|-------------|
| `PLAY` | AY-3-8912 music — plays note sequences through the sound chip. **Synchronous** execution: the ROM busy-waits for note duration, it does not use interrupt-driven playback |
| `SOUND` | Direct AY register access from BASIC |
| `BANK` | Memory bank management — examine and manage RAM banks |
| `SPECTRUM` | Switch to 48K BASIC mode (pages in ROM 1) |

### AY Sound from BASIC

`PLAY` and `BEEP` on the 128K output through the AY-3-8912 rather than the ULA beeper. However, this is done **synchronously** — the ROM programs the AY tone registers and then busy-waits (via the FRAMES counter) for the note duration to elapse. The AY chip's interrupt output pin is **never enabled** by the standard ROM. For interrupt-driven audio, assembly language and IM2 are required.

---

## RAM Disk

The 128K ROM implements a software RAM disk using banks 4 and 6 as storage. BASIC can save/load data to the RAM disk as if it were tape, but at RAM speed. The RAM disk parameters are tracked in system variables at `#5CC5`–`#5CFF`.

---

## Editor Differences

The 128K editor is significantly improved over the 48K keyword-entry system:

- **Full-screen editor** with cursor movement (arrow keys)
- **Keyword spelling**: Type keywords letter-by-letter instead of using key combinations
- **Extended error messages**: More descriptive than the 48K's single-character reports
- **BASIC renumber**: Built-in renumber utility (not available on 48K)

---

## Cross-References

- **System variables** (FRAMES, BANK_M, RAM disk state): [system_variables.md](system_variables.md)
- **128K memory map** (bank layout, paging): [memory_map_128k.md](../05_development/03_memory_and_io/memory_map_128k.md)
- **Bank switching patterns**: [bank_switching_patterns.md](../05_development/03_memory_and_io/bank_switching_patterns.md)
- **Interrupt programming** (AY interrupt, IM2): [interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md)
- **48K ROM** (baseline ROM reference): [rom_48k.md](rom_48k.md) (planned)
