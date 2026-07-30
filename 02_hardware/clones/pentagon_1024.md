[← Home](../../README.md) · [Clone Hardware](README.md)

# Pentagon 1024 / 1024SL — The Maximum Pentagon: 1 MB of RAM and the Soviet Demoscene's Workhorse

The **Pentagon 1024** is the maximum configuration of the Pentagon family — a 1024 KB (1 MB) RAM expansion of the base Pentagon 128K, achieved through the `#EFF7` extended paging port. Where the base Pentagon 128K was the *default* Russian Spectrum of the early 1990s, the Pentagon 1024 became the **demoscene and power-user machine** of the late 1990s and 2000s — the platform that ran the most ambitious Russian productions, hosted the most advanced trackers (Pro Tracker 3.x), and stored the largest software collections on a single machine.

The Pentagon 1024 is **not a different computer** from the Pentagon 128K — it is the same discrete-TTL design with additional DRAM and an `#EFF7` decode circuit added. The result is a machine with 64 banks of 16 KB (vs the 128K's 8 banks), all accessible from software via two write-only paging ports. This article covers the hardware evolution from 128K to 1024K, the 1024SL variant, modern recreations, and the programming model.

> [!NOTE]
> This article covers the **hardware platform** — the physical machine, its expansions, and its variants. For the register-level paging details (port `#7FFD` and `#EFF7` bit layout, code examples), see [memory_and_io_pentagon.md](../../05_development/03_memory_and_io/memory_and_io_pentagon.md). For the frame timing (320 scanlines, 48.83 Hz, zero contention), see [video_frame_pentagon.md](../../05_development/05_display_and_timing/video_frame_pentagon.md). For the base Pentagon 128K history and architecture, see [pentagon.md](pentagon.md).

---

## Why 1024 KB?

The base Pentagon 128K has 8 banks of 16 KB — enough for the standard 128K memory map plus the screen buffer and TR-DOS workspace. But by 1993–1995, Russian software had outgrown 128 KB:

| Use case | RAM needed | Why |
|---|---|---|
| **TR-DOS disk caching** | 256–512 KB | Loading demos/games from disk was slow (5.25" drives at 300 KB/disk). Caching the entire disk in RAM eliminated reloads. |
| **Pro Tracker 3.x samples** | 256–1024 KB | PT3 modules with high-quality digitized samples could exceed 128 KB per song. The 1024K machine could hold an entire album in RAM. |
| **Multicolor double-buffering** | 256 KB | Two full-screen multicolor buffers (one being displayed, one being rendered) require 2 × 6912 bytes per bank — easily exceeding 128 KB with code and data. |
| **Russian RPGs and adventures** | 256–512 KB | Games like *Black Raven* (Черный Ворон) and *Nord and Bert* used banked data sets far larger than 128 KB. |
| **Demo megablocks** | 512–1024 KB | Multi-part demos (e.g., *Eternity* by XBazing) loaded all parts into RAM at startup and switched between them via paging, avoiding disk access during the demo. |

The Pentagon community's answer was the `#EFF7` extension — a second paging port that added high bank-select bits, allowing the existing `#7FFD`-based banking to address up to 64 banks (1024 KB).

---

## Hardware Architecture — The EFF7 Modification

The 1024K upgrade is a **minimal hardware change** to the base Pentagon 128K. The modification consists of three additions:

### 1. Additional DRAM

The base Pentagon uses 8 × `К565РУ5` (4164-equivalent, 64 Kbit × 1) DRAM chips for the lower 16 KB, plus 8 more for the upper 32 KB — totaling 48 KB on the base 48K layout. The 128K adds another 80 KB (5 banks × 16 KB) of `К565РУ5` or `4164` DRAM.

The 1024K upgrade adds the remaining banks by populating the expansion RAM area with higher-density chips:

| Configuration | RAM chips | Total banks | Total RAM |
|---|---|---|---|
| Pentagon 48K | 16 × 4164 (64 Kbit × 1) | 3 | 48 KB |
| Pentagon 128K | 16 × 4164 + expansion | 8 | 128 KB |
| Pentagon 256K | + 8 × 41256 (256 Kbit × 1) | 16 | 256 KB |
| Pentagon 512K | + 16 × 41256 | 32 | 512 KB |
| Pentagon 1024K | + 32 × 41256 or 4464 (64 Kbit × 4) | 64 | 1024 KB |

The `К565РУ6` (256 Kbit × 1, equivalent to 41256) was the workhorse DRAM for Pentagon expansions. A 1024K machine uses 32 of these chips for the paged banks, plus the original 4164s for the fixed banks.

### 2. The #EFF7 Decode Circuit

The base Pentagon 128K decodes only `#7FFD` for paging — 3 bank-select bits, giving 8 banks. The 1024K upgrade adds a second decoder for `#EFF7`:

```
#EFF7 decode (Pentagon 1024K extension):

  74HC688 (КР1533СП1) — 8-bit identity comparator
  ┌─────────────────────────────────┐
  │  P0–P7 ← Z80 A0–A7             │
  │  Q0–Q7 ← hardwired #F7 (11110111)│
  │  /G    ← A15 (gate)            │
  │  /P=Q → pulse to latch         │
  └─────────────────────────────────┘
  Result: exact match on low byte, A15 must be 0
  → only #EFF7 (and no aliases) triggers the latch
```

The `74HC688` provides a **full decode** — unlike the `74HC138` used for `#7FFD` (which has 64 mirror addresses), the `#EFF7` decode has **zero aliases**. This was a deliberate design choice: extended paging was added later, when the community had learned the cost of partial decoding (the `#7FFD` mirrors cause software compatibility problems across clones).

The latch itself is a `74HC273` (КР1533ИР23) — an 8-bit register clocked by the `#EFF7` decode pulse. Its outputs feed the high address bits of the expansion DRAM.

### 3. Bank Address Merging

The final piece is the address-merge logic that combines `#7FFD` and `#EFF7` outputs into a complete bank number:

```
  Total bank number (6 bits for 1024K):
  
  #EFF7 bits 0–2 → bank bits 3–5  (high bits, group selector)
  #7FFD bits 0–2 → bank bits 0–2  (low bits, within-group selector)
  
  Bank = (#EFF7 & 0x07) × 8 + (#7FFD & 0x07)
       = 0..63
```

This means the `#7FFD` port continues to work exactly as on a 128K — software that only knows about `#7FFD` runs unchanged. The `#EFF7` port transparently extends the address space without breaking compatibility.

> [!NOTE]
> The `#EFF7` port is **write-only**. There is no way to read back the current extended bank selection. Software that needs to preserve the state must shadow it in a system variable (typically at `#5CC5` or a custom location). See [memory_and_io_pentagon.md](../../05_development/03_memory_and_io/memory_and_io_pentagon.md) for the standard shadow-variable pattern.

---

## The Pentagon 1024SL

The **Pentagon 1024SL** (СЛ = "Самостоятельная Логика", literally "Self-Contained Logic") is a late-1990s redesign of the Pentagon 1024 that integrates the entire machine onto a single, professionally-manufactured PCB. Where the original Pentagon 1024 was a hobbyist-built machine (hand-soldered, point-to-point wiring on prototyping board), the 1024SL was a **factory-produced** machine with:

- **Four-layer PCB** (vs the original's two-layer) — better power distribution, lower noise
- **Integrated Beta 128 FDC** on the motherboard (no expansion card needed)
- **Integrated Kempston joystick port** (no external interface)
- **Integrated Turbo 7 MHz** with a switching circuit (original Pentagon required a mod)
- **PS/2 keyboard adapter header** (the original Pentagon used the standard Spectrum membrane keyboard; the SL could accept a full PC AT keyboard via an adapter board)
- **SVGA output option** (via an add-on board that generated 50 Hz SVGA from the Pentagon's video signal)

The 1024SL was produced from roughly 1997 to 2002 by several small Russian firms (notably *MicroArt* and *Дельта-Софт*). It became the standard machine for Russian demoscene parties in the late 1990s — most entries at the *Funtop* and *Paradox* parties were developed and shown on 1024SL machines.

### SL-Specific Programming Considerations

The 1024SL's integrated features add a few programming considerations:

| Feature | Port | Notes |
|---|---|---|
| Turbo 7 MHz enable/disable | `#77` bit 0 | Write `1` to enable, `0` to disable. The CPU clock switches between 3.5 MHz and 7 MHz. Timing-sensitive code must account for this. |
| SVGA mode (if fitted) | `#77` bit 1 | Toggles between composite/SVGA output. Some demos check this bit to enable SVGA-specific timing. |
| PS/2 keyboard (if fitted) | `#FADF` | Read for scancode. Not standard — depends on the specific adapter board. |

> [!WARNING]
> Port `#77` is **not standardized** across all Pentagon revisions. The 1024SL uses it for turbo/SVGA control, but other Pentagons use it for different functions or not at all. Software that targets port `#77` should detect the machine type first (via timing or port probing) or provide a fallback.

---

## Modern Recreations

The original Pentagon 1024 and 1024SL are long out of production, but several modern projects recreate or emulate the platform:

| Project | Type | Pentagon 1024 support |
|---|---|---|
| **Pentagon 2.666 Lite** | FPGA core (Cyclone IV) | Full — implements `#7FFD` + `#EFF7`, 1024K RAM, Beta 128 FDC, Turbo mode |
| **ZX Evolution (TS-Conf)** | Real Z80 + CPLD | Full — Pentagon-compatible with extensions; see [zx_evo.md](../newgen/zx_evo.md) and [ts_conf.md](../newgen/ts_conf.md) |
| **MIST / MiSTer (Pentagon core)** | FPGA (Altera) | Full — cycle-accurate Pentagon 1024 core; see [mist_mister_core.md](../../11_emulation/fpga/mist_mister_core.md) |
| **Unreal Speccy / ZXMAK2 / ZEsarUX** | Software emulator | Full — all three implement the `#EFF7` port and 1024K RAM |
| **ZX-Uno** | FPGA (Cyclone IV) | Full — Pentagon 1024 core included; see [zx_uno.md](../newgen/zx_uno.md) |

For software development, the Pentagon 1024 is one of the best-documented Soviet clones — every major emulator and FPGA platform supports it. Code that runs on one Pentagon 1024 implementation will run on all of them.

---

## Programming Model — Detecting and Using 1024K

### Detecting a Pentagon 1024

There is no standard ROM routine to query the amount of RAM. The canonical detection method is **write-and-verify**: page in a bank beyond the 128K range, write a unique byte, page it back, and check that the byte survived.

```z80
; Pentagon 1024 detection — write/verify across extended banks
; Returns: A=1 if 1024K detected, A=0 if not
; Destroys: AF, BC, HL
; Requires: interrupts disabled, stack in safe bank

Detect1024K:
    DI                  ; Paging must not be interrupted
    
    ; Save current paging state
    LD   HL,(BANK_M)    ; Shadow copy of #7FFD at system variable #5CC5
    PUSH HL             ; Save it
    
    ; Select extended group 7 (banks 56-63) via #EFF7
    LD   A,#07
    LD   BC,#EFF7
    OUT  (C),A
    
    ; Select bank 63 (within group 7) via #7FFD
    ; (preserve ROM/screen bits from BANK_M)
    LD   A,L
    OR   #07            ; Set low bank bits to 7
    AND  #1F            ; Preserve ROM/screen
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A      ; Update shadow
    
    ; Write a signature byte to #C000 in bank 63
    LD   A,#A5          ; Arbitrary test byte (01010101 pattern)
    LD   (#C000),A
    
    ; Switch to a different bank (bank 0) to force a page-out
    LD   A,#00
    LD   BC,#EFF7
    OUT  (C),A          ; Group 0
    LD   A,L
    AND  #1F            ; Clear low bank bits
    OR   #00
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A
    
    ; Read back from #C000 (now bank 0) — should be different
    LD   A,(#C000)
    CP   #A5            ; If still #A5, paging didn't work
    JR   Z,.no_1024     ; → not a 1024K machine
    
    ; Page bank 63 back and verify
    LD   A,#07
    LD   BC,#EFF7
    OUT  (C),A
    LD   A,L
    OR   #07
    AND  #1F
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A
    
    LD   A,(#C000)
    CP   #A5            ; Should be our signature
    JR   NZ,.no_1024
    
    ; Success: 1024K detected
    LD   A,#01
    JR   .done
    
.no_1024:
    XOR  A              ; A=0
    
.done:
    ; Restore original paging
    POP  HL
    LD   A,L
    LD   BC,#7FFD
    OUT  (C),A
    LD   (#5CC5),A
    
    ; Reset #EFF7 to group 0
    XOR  A
    LD   BC,#EFF7
    OUT  (C),A
    
    EI
    RET
```

> [!WARNING]
> This detection routine assumes Pentagon-style `#EFF7` paging. On non-Pentagon machines, `#EFF7` may be decoded differently or not at all, and this routine could corrupt state. Always run a broader machine-detection routine first (see [clone_timing.md](clone_timing.md) for detection techniques).

### Bank Allocation Strategy

The 64 banks are typically allocated as follows by demoscene and game code:

```
Banks 0-7    → Standard 128K bank space (via #7FFD alone)
                Bank 0,1,3,4,6: general code/data
                Bank 2: fixed at #8000 (ROM-compatible)
                Bank 5: fixed at #4000 (screen bank)
                Bank 7: shadow screen
Banks 8-31   → Extended data (samples, graphics, level data)
Banks 32-63  → Disk cache / unused / reserved
```

The split between `#7FFD` (3-bit, within-group) and `#EFF7` (3-bit, group-select) means code typically sets `#EFF7` once per data region, then cycles `#7FFD` to scan within that group. This minimizes port writes — each bank switch costs only one `OUT` instruction instead of two.

---

## Pentagon 1024 vs Other Large-RAM Clones

| Clone | Max RAM | Extended port | Notes |
|---|---|---|---|
| **Pentagon 1024 / 1024SL** | 1024 KB | `#EFF7` | Most popular 1 MB clone; de-facto Russian demoscene standard |
| **Kay 1024** | 1024 KB | `#7FFD` + custom | Nemo-bus expansion; see [kay.md](kay.md) |
| **Scorpion ZS-1024** | 1024 KB | `#1FFD` + ProfROM | GMX expansion adds 2 MB; see [scorpion.md](scorpion.md) |
| **ATM Turbo 2+** | 1024 KB | `#7FFD` + `#EFF7` + `#BFFD` | Has its own paging model for CP/M modes; see [atm_turbo.md](atm_turbo.md) |
| **Profi 1024** | 1024 KB | `#7FFD` + `#DFFD` | Different extended paging port; see [profi.md](profi.md) |

The Pentagon's `#EFF7` paging is the most widely supported extended paging scheme in the Russian software ecosystem — software targeting "Pentagon 1024" typically works on all five clones above (with minor port adjustments for Profi and ATM).

---

## Cross-References

- [Pentagon 128K (base)](pentagon.md) — the original 1989 design, history, architecture, video timing
- [Pentagon memory & I/O ports](../../05_development/03_memory_and_io/memory_and_io_pentagon.md) — register-level `#7FFD` / `#EFF7` reference, code examples
- [Pentagon video frame](../../05_development/05_display_and_timing/video_frame_pentagon.md) — 320-line frame, 48.83 Hz, zero contention
- [Clone timing](clone_timing.md) — cross-clone timing comparison and machine detection
- [Kay 1024](kay.md) — alternative 1 MB clone with Nemo bus
- [Profi](profi.md) — Ukrainian professional clone with VGA and ISA expansion
- [ATM Turbo](atm_turbo.md) — CP/M-capable clone with extended graphics
- [Scorpion](scorpion.md) — true-48K-timing alternative with GMX expansion
- [ZX Evolution](../newgen/zx_evo.md) — modern FPGA-based Pentagon successor
- [TR-DOS](../../04_operating_systems/trdos.md) — the disk OS standard on Pentagon 1024
- [Beta 128 FDC](../../03_io/storage/beta_disk_interface.md) — disk interface integrated into Pentagon 1024SL
- [Pro Tracker 3](../../06_sound/trackers_and_formats/pt3_format.md) — AY music format that benefits from 1024K RAM
- [Soviet demoscene](../../07_demoscene/soviet_demo_scene.md) — cultural context for Pentagon 1024's dominance

---

## References

- **ZX-Review magazine** (1993–1998) — primary source for Pentagon 1024 modification schematics and the original `#EFF7` specification
- **zx-pk.ru forum** — *Пентагон 1024* subforum contains hardware variants, repair threads, and modern reproduction PCB files
- **SpeccyWiki (speccy.info)** — Pentagon 1024SL article with PCB photos and schematic scans
- **Unreal Speccy emulator source** — reference implementation of `#EFF7` paging in `machine_pentagon.cpp`
- **Pentagon 2.666 Lite project** (zx-pk.ru) — modern FPGA recreation with open Verilog source, documents the exact `#EFF7` decode logic
- **Demoscene productions** — *Eternity* (XBazing, 1999), *Eclipse* (MGS, 1998), and other 1024K-targeted demos demonstrate real-world `#EFF7` usage patterns
