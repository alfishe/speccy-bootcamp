[← Home](../../README.md) · [Memory & I/O](README.md)

# Pentagon 128K / 512K / 1024K — Memory Map and I/O Ports

The Pentagon is the **most popular Soviet ZX Spectrum clone**, designed in 1989 by enthusiasts in Moscow. It uses discrete TTL logic instead of a ULA, which changes several key behaviors: **zero memory contention**, different interrupt timing, and extended memory paging via additional ports.

The base Pentagon 128K is register-compatible with the Sinclair 128K at port `#7FFD`, making most 128K software work out of the box. Expanded models (512K, 1024K) keep the same port and add **extension bank bits in `#7FFD` bits 5-7**, gated by the Pentagon-specific `#EFF7` control register — one `OUT` selects any of the 64 banks on a 1024K machine. Most Pentagons also include a **Beta 128 disk interface** with TR-DOS ROM, which pages into `#0000`–`#3FFF` via its own port.

> [!NOTE]
> This article covers the **Pentagon memory map and I/O ports**. For Pentagon video timing differences (different scanline count, different INT position), see [video_frame_pentagon.md](../05_display_and_timing/video_frame_pentagon.md). For the Sinclair 128K baseline, see [memory_and_io_128k.md](memory_and_io_128k.md).

---

## Memory Map — Base 128K (Compatible Mode)

In default configuration, the Pentagon is identical to the Sinclair 128K:

```
Address range    Contents               Control
──────────────────────────────────────────────────────────
#0000 - #3FFF   ROM 0 or ROM 1         #7FFD bit 4
                (or TR-DOS ROM)         Beta 128 port
#4000 - #7FFF   Bank 5 (fixed)         Always Bank 5
#8000 - #BFFF   Bank 2 (fixed)         Always Bank 2
#C000 - #FFFF   Banks 0–7 (switchable) #7FFD bits 0–2
──────────────────────────────────────────────────────────
```

The Pentagon's `#7FFD` implementation is **fully compatible** with the Sinclair 128K. All 128K software that uses standard paging works without modification.

### ROM Configuration

The Pentagon typically has **three ROM images** available:

| ROM | Contents | Selected by |
|-----|----------|-------------|
| ROM 0 | 128K editor (Russian or English version) | `#7FFD` bit 4 = 0 |
| ROM 1 | 48K BASIC ROM (Sinclair-compatible) | `#7FFD` bit 4 = 1 |
| TR-DOS | TR-DOS disk operating system | Beta 128 FDC port |

The TR-DOS ROM is paged in via the Beta 128 interface's port `#1FFD` (different function from the +2A/+3 `#1FFD`!). When TR-DOS is active, it overrides the normal ROM at `#0000`–`#3FFF` regardless of `#7FFD` bit 4.

---

## I/O Port — #7FFD (Standard + Extended Paging)

Identical to the Sinclair 128K in the base configuration:

```
OUT (#7FFD), A — paging register (write-only):

  Bits 0–2: RAM bank at #C000 (0–7)
  Bit  3:   Screen select (0=Bank 5, 1=Bank 7)
  Bit  4:   ROM select (0=ROM 0, 1=ROM 1)
  Bit  5:   Disable paging (1 = lock until reset)
```

The lock bit (bit 5) is respected on the Pentagon, just like the Sinclair 128K. Some Soviet software relies on this.

### Extended Bits on 512K/1024K Machines

On expanded machines the **unused high bits become bank-select bits**, giving up to 64 banks in the single port:

```
  Bit  6:   Bank bit 3  (banks 8–15, 256 KB step)
  Bit  7:   Bank bit 4  (banks 16–31, 512 KB step)
  Bit  5:   Bank bit 5  (banks 32–63) — ONLY while extended RAM
            is enabled via #EFF7 bit 2 = 0; otherwise it is the
            standard 48K lock (see above)

  Effective bank = (#7FFD & 7) | ((#7FFD & 0xC0) >> 3) | (#7FFD & 0x20)
```

The dual role of bit 5 is the key compatibility mechanism: with extended memory gated off, the machine is electronically a plain 128K and bit 5 locks paging the Sinclair way. Emulators (ZEsarUX, UnrealSpeccy, ZXMAK2) implement exactly this model. See [pentagon_1024.md](../../02_hardware/clones/pentagon_1024.md) for the full hardware story.

> [!WARNING]
> Writing bit 5 while extended memory is disabled engages the 48K lock irreversibly until RESET. Clear `#EFF7` bit 2 (enable extended RAM) before any bit-5 banking, and never assume the `#EFF7` state at program start — the Gluk Reset Service ROM manipulates it.

---

## I/O Port — #EFF7 (Control Register: Gate, Video, Turbo)

`#EFF7` is **not a bank-select port** — it is the Pentagon extended-feature register (Black_Cat's port guide calls it `PagVidTrbReg`). Its paging-relevant bit is the **extended-memory gate**:

```
OUT (#EFF7), A — Pentagon control register (write-only):

  Bit  2:   Extended RAM gate: 0 = memory above 128K enabled
            (bits 5-7 of #7FFD = bank bits), 1 = disabled
            (plain 128K, #7FFD bit 5 = 48K lock)
  Bit  3:   1 = RAM page 0 at #0000-#3FFF instead of ROM (1024SL)
  Bit  4:   Turbo: 0 = 7 MHz ON, 1 = OFF (1024SL v2.x; inverted!)
  Bit  0:   Video: 16 colour (1024SL) / a4b multicolor (hand-built)
  Bit  1:   Video: 512×192 (hand-built standard; unused on 1024SL)
  Bit  6:   Video: 384×304 borderless mode
  Bit  7:   Gluk CMOS real-time clock enable (hand-built standard)
```

The bit layout differs between the 1990s hand-built standard (Born Dead #10) and the factory Pentagon-1024SL v2.x — see [pentagon_1024.md](../../02_hardware/clones/pentagon_1024.md) for both tables and the decode masks.

### Paging Extended Banks

```z80
; Pentagon 1024K: page in bank 20 (beyond the base 8) — ONE write
; Bank 20 = 16 + 4  ->  bank bit 4 (bit 7 of #7FFD) + bits 0-2 = 4

    LD   A,#00
    LD   BC,#EFF7
    OUT  (C),A           ; extended RAM ON: bit 5 of #7FFD = bank bit

    LD   A,(#5CC5)        ; current #7FFD shadow (BANK_M)
    AND  #18             ; keep screen (#08) + ROM (#10) bits from shadow
    OR   #84             ; %10000100: bank bit 4 + low bank bits = 4
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A
```

> [!NOTE]
> The `AND #18` / `OR #84` merge keeps the screen and ROM selections from the shadow while replacing all six bank bits — and can never leak a stale bit 5 as an accidental lock. Extended memory paging requires the `#EFF7` gate (bit 2 = 0) beforehand. The base Pentagon 128K (discrete TTL only, no `#EFF7` circuit) cannot address beyond 128K.

---

## I/O Port — Beta 128 FDC (TR-DOS)

The Beta 128 disk interface is present on almost all Pentagons. It has its own port decoding that pages the TR-DOS ROM:

```
Port #1FFD (Beta 128 FDC — NOT the same as +2A/+3 #1FFD):
  Write: Bit 0 = TR-DOS ROM page enable (1 = TR-DOS active at #0000-#3FFF)
         Other bits control FDC functions

Port #3FFD: WD1793 / KR1818VG93 FDC data register
Port #FFFD: FDC status/command register (aliases with AY — careful!)
Port #5FFD: FDC track register
Port #7FFD: FDC sector register (aliases with paging — conflict!)
```

> [!WARNING]
> The Beta 128's port decoding **overlaps** with `#7FFD` (paging) and `#FFFD` (AY register select). The TR-DOS ROM contains code that carefully sequences port accesses to avoid conflicts. Do not access the FDC directly from user code without understanding the overlap — use TR-DOS hook codes instead. See [trdos.md](../../04_operating_systems/trdos.md) and [fdc_vg93.md](../../03_io/storage/fdc_vg93.md).

---

## I/O Port — What About Port #77?

Older articles sometimes credit the Pentagon with a "shadow port" `#77` (turbo, cache, wait states). **It does not have one** — the `#77` family (`xxxxxxxx0xx10111`) is the ATM Turbo's video/turbo register (`VidTrbReg`, model A in Black_Cat's table; the ATM Turbo 2+ programs it via `#FF77`). On a stock Pentagon a write to `#77` is simply not decoded. Pentagon turbo modes live in `#EFF7` bit 4 on the 1024SL (see above); older hand-built turbo boards used ad-hoc ports that were never standardized.

---

## Port Decoding Circuits

The Pentagon uses **two separate decoding circuits** — one for the standard 128K-compatible paging, and one for extended memory:

<img src="./assets/pentagon_port_decoding.svg" width="720" alt="Pentagon #7FFD + #EFF7 decoding schematic" />

| Circuit | Chip | Port | Lines Checked | Mirrors |
|---------|------|------|---------------|--------|
| 128K paging (Pentagon 128) | 74HC138 / KR1533ID7 | `#7FFD` | 2 (A15=0, A1=0) | 16K-wide |
| Paging (Pentagon 1024 / 1024SL) | same latch | `#7FFD` | 3 (+A14=1) | 8K-wide |
| Control register | 74HC688 / KR1533SP1 | `#EFF7` | 5 (A15-A12=`1110`, A3=0) + WR | 2048 |

The paging latch works identically to the Sinclair 128K (see [memory_and_io_128k.md](memory_and_io_128k.md)). The `#EFF7` decode is **partial, not exact**: five address lines are compared (A15-A12 = `1110`, A3 = 0), the rest are ignored — yielding 2048 mirror addresses. Hand-built 1990s machines decoded even less (minimum: A3=0, A12=0, IOWR, reset by RESET). The decoded lines were chosen so canonical `#7FFD` writes (A3=1, A12=1) can never strobe the `#EFF7` latch. Full decoding details and Verilog equivalents: [io_port_decoding.md](io_port_decoding.md); both bit layouts: [pentagon_1024.md](../../02_hardware/clones/pentagon_1024.md).

---

## Contention — None

The Pentagon has **zero memory contention**. Video address generation uses discrete counter chips that run independently of the CPU bus. Code runs at full speed regardless of address or display position.

This means:
- **All code runs at the same speed** — whether in screen area, ROM, or upper RAM
- **Multicolor effects that depend on contention delays will not work** without adaptation
- **Floating bus behavior is absent or different** — reading contended memory during screen display does NOT return the byte the ULA is fetching (unlike 48K/128K)
- **I/O timing is deterministic** — `IN` and `OUT` take exactly the documented number of T-states

> [!TIP]
> Code that works perfectly on a Pentagon but breaks on a 48K almost certainly has a contention-related timing bug that the Pentagon's lack of contention masks. Always test on both.

See [contention_model.md](contention_model.md) for cross-model contention comparison.

---

## Memory Map — 512K Configuration

```
Bank    Address when paged    Physical RAM     Notes
──────────────────────────────────────────────────────────
0       #C000–#FFFF           16 KB           Base bank
1       #C000–#FFFF           16 KB           Base bank
2       #8000–#BFFF (fixed)   16 KB           Fixed
3       #C000–#FFFF           16 KB           Base bank
4       #C000–#FFFF           16 KB           Base bank
5       #4000–#7FFF (fixed)   16 KB           Screen bank (fixed)
6       #C000–#FFFF           16 KB           Base bank
7       #C000–#FFFF           16 KB           Shadow screen
8–31    #C000–#FFFF           16 KB each      Extended banks via #7FFD bits 6–7
──────────────────────────────────────────────────────────

Total: 32 banks × 16 KB = 512 KB
```

### Memory Map — 1024K Configuration

Same structure but 64 banks (0–63): the third extension bit is `#7FFD` bit 5 (active only while `#EFF7` bit 2 = 0), giving 1024 KB total. Banks 0–7 use `#7FFD` bits 0–2 alone; banks 8–63 use bits 6, 7 and 5 respectively — still a single port.

---

## Quick Reference — Port Summary

```
Port    Function                                     Pentagon specific
────────────────────────────────────────────────────────────────────
#FE     Border, EAR, keyboard                       No (same as all models)
#7FFD   Paging: bank, ROM, screen, lock — plus       Compatible with 128K;
        extension bank bits 6-7 (and 5) on 512K/1024K  extended bits YES
#EFF7   Control register: ext-RAM gate, video,        YES — Pentagon family
        turbo (NOT a bank-select port)
#DFFD   Profi-compatible extension (wired parallel    Hand-built 1024K
        to #7FFD bits 7/6/5); Kay uses it independently
#1FFD   Beta 128 FDC / TR-DOS ROM page              YES — different from +3!
#77     Not a Pentagon port (ATM Turbo register)  No — undecoded on Pentagon
#FFFD   AY register select / FDC status              Overlaps with Beta 128!
#BFFD   AY register data                             No
#1F     Kempston joystick (built-in)                 No (but always present)
────────────────────────────────────────────────────────────────────
```

---

## Cross-References

- **128K/+2 memory and ports** (#7FFD, AY, shadow screen baseline): [memory_and_io_128k.md](memory_and_io_128k.md)
- **+2A/+3 memory and ports** (#1FFD, 4 paging modes): [memory_and_io_plus3.md](memory_and_io_plus3.md)
- **I/O port decoding** (partial decoding, masks, conflicts): [io_port_decoding.md](io_port_decoding.md)
- **Contention model** (Pentagon: no contention): [contention_model.md](contention_model.md)
- **Pentagon video frame** (timing differences): [video_frame_pentagon.md](../05_display_and_timing/video_frame_pentagon.md)
- **Clone timing** (all Soviet clone differences): [clone_timing.md](../../02_hardware/clones/clone_timing.md)
- **TR-DOS** (disk operating system): [trdos.md](../../04_operating_systems/trdos.md)
- **Beta 128 FDC** (WD1793/VG93): [fdc_vg93.md](../../03_io/storage/fdc_vg93.md)
- **Pentagon hardware**: [pentagon.md](../../02_hardware/clones/pentagon.md); 1 MB maximum configuration: [pentagon_1024.md](../../02_hardware/clones/pentagon_1024.md)
- **Complete I/O port map** (all ports, all models, decoding bitmasks): [io_port_map.md](../../10_references/io_port_map.md)

---

## References

### External references

- [Alone Coder — Born Dead #10 (zxpress.ru)](https://zxpress.ru/ru/ezines/born-dead/10/tehnicheskie-podrobnosti-kompyuterov-semeystva-pentagon-osobennosti-pentagon-1024-upravlenie) — primary source for the Pentagon 512/1024 paging standard: `#7FFD` extension bits, `#EFF7` gate, `#DFFD` parallel wiring, lock behavior
- [Pentagon-1024SL v2.2 official documentation (ver22.pdf)](https://github.com/koe1234/pentagon_2.2/blob/main/ver22.pdf) — factory register tables for `#7FFD` / `#EFF7` and decode masks
- [zx-pk.ru — Pentagon hardware subforum](https://zx-pk.ru/) — the primary Russian-language knowledge base for the Pentagon 128/512/1024, including schematics for the `#7FFD` / `#DFFD` / `#EFF7` ports and the various memory extensions (1 MB, 4 MB "shadow RAM").
- [SpeccyWiki — Pentagon (speccy.info)](https://speccy.info/) — Russian-language wiki article covering the Pentagon's architectural deviations from the 128K, including the absence of contention and the divergent TR-DOS banking.
- [Black_Cat — *ZX Port Map* (tslabs/zx-evo)](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt) — comprehensive port-decoding reference covering Pentagon-specific ports (`#7FFD`, `#DFFD`, `#EFF7`, `#BFF7`) and their partial-decode mirrors.
- [Pentagon Schematics Archive — Pentagon 128 / 512 / 1024 SL V2 (zx-pk.ru)](https://zx-pk.ru/) — community-verified schematic scans documenting the discrete logic that implements the `#7FFD` banking and the `#DFFD` extended bank selector on the 512 KB variants.
- [ZXM-Phoenix / Pentagon hardware reference (chibiakumas.com)](https://chibiakumas.com/) — English-language translations of Russian hardware articles covering the Pentagon's design lineage from the Leningrad and the design choices that led to its de facto standard status in the post-Soviet scene.
