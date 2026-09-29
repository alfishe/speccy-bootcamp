[← Home](../../README.md) · [Display & Timing](README.md)

# Scorpion Video Frame — 312 Scanlines Like 48K, but Shifted 9 T-states and Optionally 7 MHz

The Scorpion ZS-256 (Скорпион, designed by Sergey Zonov, St. Petersburg, 1996) is the second-most-important Soviet clone after the Pentagon. Unlike the Pentagon, its frame timing **matches the 48K exactly at the macro level** — 312 scanlines × 224 T-states = 69,888 T-states at 50.08 Hz — but the **horizontal phase within each line is shifted**, and the machine optionally doubles its CPU clock to 7 MHz. Code that "feels like 48K" mostly works, but timing-critical effects may be subtly off.

> [!NOTE]
> This article covers **only the Scorpion's video frame timing**. For hardware design (discrete logic, Zonov's glue logic), see [scorpion.md](../../02_hardware/clones/scorpion.md). For the broader clone-timing landscape (Pentagon, Kay, ATM Turbo, Profi), see [clone_timing.md](../../02_hardware/clones/clone_timing.md).

---

## Frame Parameters (Scorpion)

```
┌────────────────────────────────────────────────────────┐
│  Scorpion ZS-256 Frame Timing                          │
├────────────────────────────────────────────────────────┤
│  CPU clock (standard):   3.500000 MHz (same as 48K)    │
│  CPU clock (turbo):      7.000000 MHz (optional)       │
│  T-states per scanline:  224 (same as 48K)             │
│  Total scanlines:        312 (same as 48K)             │
│  Total T-states/frame:   69,888 (same as 48K)          │
│  Frame rate:             50.08 Hz (same as 48K)        │
│                                                        │
│  Paper starts at:        T=14,344 (vs T=14,335 on 48K) │
│  Horizontal offset:      +9 T-states vs 48K            │
│                                                        │
│  INT position:           T=0, line 0 (same as 48K)     │
│  INT duration:           32 T-states (same as 48K)     │
│                                                        │
│  Contention:             None (any board)              │
│  Even M1:                +0/+1 T on opcode fetches     │
│                          from RAM (not ROM)            │
└────────────────────────────────────────────────────────┘
```

The frame totals are identical to the 48K, which makes Scorpion **the only Soviet clone that runs unmodified PAL-timed software**. What changes is the *phase* of the visible area within each line.

---

## Why Scorpion Looks Like 48K — and Isn't

The Scorpion was designed in 1996, seven years after the Pentagon. By then the Russian demoscene had a substantial library of 48K-targeted software that authors wanted to run unmodified. Zonov's design goal was **binary compatibility with the 48K at the frame level**, while extending memory and adding turbo mode. He achieved this by:

1. **Using the same vertical counter maths** — 312 scanlines per frame, 224 T-states per scanline, 69,888 T-states per frame.
2. **Keeping INT at line 0, T=0** — so ISRs fire at the same logical position as 48K.
3. **Preserving the standard `#7FFD` paging port** — so 128K-style RAM banking works.

But the **horizontal sync and blanking phases within each scanline are shifted**, because the discrete logic generates them from a different divider chain than the 48K's ULA:

```
48K horizontal phase per scanline (224 T-states total):
  16T  HSYNC                | 48T left border | 128T paper | 32T right border
                          ← paper starts at T=14,335 within frame

Scorpion horizontal phase (224 T-states total):
  40T  off-screen (sync + back porch) | 24T left border | 128T paper | 32T right border
                                       ← paper starts at T=14,344 within frame (+9T)
```

The 9 T-state offset is small but visible: border bars that align with paper edges on 48K appear shifted one pixel left on Scorpion. For most software this is invisible; for race-the-beam multicolor demos it matters.

---

## Frame Structure

```
Scorpion frame layout (312 scanlines = 69,888 T-states):

┌──────────────────────────────────────────────────┐ Line 0, T=0
│  INTERRUPT (INT asserted for 32 T-states)        │
│  Top border: 64 lines, 14,336 T-states           │
│  (matches 48K vertical timing)                   │
├──────────────────────────────────────────────────┤ Line 64, T=14,344 ← +9T vs 48K
│  Paper area: 192 lines, 43,008 T-states          │
│  256×192 pixel display                           │
│  Contention: none (Even M1 on RAM fetches)       │
├──────────────────────────────────────────────────┤ Line 256, T=57,352
│  Bottom border: 56 lines, 12,544 T-states        │
└──────────────────────────────────────────────────┘ Line 312 = 0

64 + 192 + 56 = 312 scanlines ✓
312 × 224 = 69,888 T-states ✓
```

---

## Contention — None, but Even M1

Unlike the 48K (strict 6-5-4-3-2-1-0-0 contention, by ULA design), the Scorpion has **no memory contention and no I/O contention on any board**. Its video logic and the CPU share the DRAM in fixed slots on a 7 MHz phase counter, like the Pentagon, so an access to screen memory during the paper never waits.

What the Scorpion has instead is **"Even M1"**: an opcode fetch (M1) from **RAM** that would start on an odd T-state gets one WAIT, so every fetch from RAM starts on an even T-state. Fetches from ROM, data reads and writes, I/O and interrupt acknowledge never wait. The rule comes from the turbo board's SC15.1 EPLD equations (ZS Company, 1996) and matches programmers' reports from real machines — full details in [scorpion.md](../../02_hardware/clones/scorpion.md#contention-and-the-even-m1-wait); the generic explanation of why only fetches from shared DRAM are affected is in [contention_model.md](../03_memory_and_io/contention_model.md#why-memory-slows-the-cpu--shared-dram-slots-and-who-waits).

| Board | Even M1 at 3.5 MHz | 7 MHz turbo |
|---|---|---|
| Yellow (1991–92) | Yes (probable) | — (no turbo without the upgrade) |
| Green / Turbo+ upgrade (SC15.1 EPLD) | Yes | Every RAM access waits for a free slot; fewer CPU slots during the paper |
| 2007 GAL re-creation ("TURBO 15.3") | No | Per its own GAL |
| Early RC-delay boards | Unknown | — |

For raster code this means:

- **Paper and border cost the same** at 3.5 MHz — there is no contention window to model.
- **Code in RAM runs each instruction at its Pentagon length rounded up to an even number** (`LD A,n` 7 → 8, `DJNZ` taken 13 → 14, `OUT (n),A` 11 → 12). A 224-T line loop built from odd-length instructions tuned on a Pentagon will be longer on a Scorpion.
- **Exit from `HALT` is always on an even T-state** ("на скорпионе … всегда получается чётный такт на выходе из halt" — introspec, [zx-pk.ru](https://zx-pk.ru/threads/21212-tajmingi-pentagon-128/page3.html)), so a `HALT`-synchronized effect can only start on an even phase.
- **Code in ROM is unaffected.**

> [!WARNING]
> **Requires contended memory timing** — on the Scorpion, the fetch alignment. Multicolor or border code that needs 1-T resolution cannot get it from RAM: odd delays round up to even. Use even-length timed paths, or detect the Scorpion and use a separately tuned path. At 7 MHz the Turbo+ slot waits make the timing paper-dependent.

---

## 7 MHz Turbo Mode

The Scorpion was the first widely-available Soviet clone with a hardware turbo mode. Besides the front-panel button and the Shadow Monitor's `RST 8` calls, a port access doubles the CPU clock. MAME and Xpeccy model the switch as read-triggered — an `IN` from the `#7FFD` decode turns turbo on, an `IN` from `#1FFD` (or a reset) turns it off, and the byte read is meaningless:

```z80
; Turbo on/off as modeled by MAME and Xpeccy (read-triggered).
TurboOn:
        LD   BC,#7FFD
        IN   A,(C)            ; any read of the #7FFD decode: 7 MHz
        RET
TurboOff:
        LD   BC,#1FFD
        IN   A,(C)            ; any read of the #1FFD decode: 3.5 MHz
        RET
```

The Scorpion ROM leaves turbo **on**, so code that needs 3.5 MHz timing must switch it off itself.

### What Changes at 7 MHz

| Quantity | 3.5 MHz | 7 MHz |
|---|---|---|
| CPU clock | 3.500000 MHz | 7.000000 MHz |
| T-states per frame (CPU's view) | 69,888 | **139,776** |
| Frame rate | 50.08 Hz | 50.08 Hz (unchanged — video still 312 lines × 224T at the original pixel clock) |
| Effective CPU speed | 100% | **~180-200%** (RAM accesses wait for free DRAM slots, more during the paper) |
| I/O port access | Normal timing | Faster (fewer T-states per OUT/IN) |

### What Doesn't Change

- **Frame duration** — 19.97 ms either way; the video subsystem runs from the same 14 MHz master clock divided down.
- **INT position** — still fires at line 0, T=0 (in CPU T-states: T=0 at 3.5 MHz, T=0 at 7 MHz).
- **DRAM slot schedule** — the DRAM is still divided between video and CPU by the same 7 MHz phase counter. At 7 MHz the CPU often arrives outside its slot and waits for it; per the SC15.1 equations it gets twice as many slots during the border as during the paper, so the turbo Scorpion is **screen-contended in its own way** (medium confidence — no timing measurement found).

### Compatibility Implications

- **Interrupt handlers**: code that does N T-states of work in the ISR now has 2N T-states available — but only if you re-time everything for 7 MHz. A naive port will run the ISR twice as fast and exit early.
- **Multicolor / race-the-beam**: the doubled T-state density per scanline (448 T-states per line at 7 MHz vs 224 at 3.5 MHz) means you can write to ATTR registers twice per line — but the timing must be completely re-derived.
- **Music players**: tempo is unaffected (still 50 Hz) but the player routine has twice the CPU budget per frame.
- **I/O loops**: tape loaders, disk routines, and any code with cycle-counted I/O **breaks** at 7 MHz unless it explicitly gates itself back to 3.5 MHz.

Most production code toggles turbo on for compute-heavy sections (decrunching, 3D math, screen rebuilds) and off for timing-critical sections (ISR, I/O).

---

## INT Timing and ISR Implications

INT timing matches 48K:

```
INT asserted at:    Line 0, T=0
INT duration:       32 T-states (then auto-cleared)
INT acknowledged:   by the CPU's IM1/IM2 ISR entry

After INT, before paper area:
  Top border:       64 lines = 14,336 T-states
                    (vs 10,752 on Pentagon — Scorpion has 29% more setup time)
```

The Scorpion has the **same generous pre-paper window as 48K**, which means 48K-style ISRs work without modification. There is no need to shorten ISR setup code like on the Pentagon.

---

## Scorpion vs 48K vs Pentagon

```
                          48K           Scorpion         Pentagon
Scanlines:                312           312              320
T-states/frame:           69,888        69,888           71,680
Frame rate:               50.08 Hz      50.08 Hz         48.83 Hz
Paper starts at:          T=14,335      T=14,344 (+9T)   T=10,752
Top border:               64 lines      64 lines         48 lines
Bottom border:            56 lines      56 lines         48 lines
Contention:               Strict        None (Even M1)   None
Turbo mode:               No            7 MHz optional   Rare
Binary compat with 48K:   (is 48K)      High             Medium
```

The Scorpion occupies a useful middle ground: it runs 48K software with high fidelity (unlike Pentagon, which shifts timing significantly), but offers optional turbo and expanded memory.

---

## Detecting Scorpion at Runtime

```z80
; Scorpion detection via the #1FFD port
; The Scorpion responds to port #1FFD with a memory banking register.
; A safe detection: write a pattern, read it back, check the banking effect.

DetectScorpion:
    ; ... standard 48K vs 128K detection first ...
    
    ; On Scorpion: port #1FFD is the turbo + ROM bank register
    ; Try toggling turbo mode and measuring frame T-states
    ; (139,776 at 7 MHz vs 69,888 at 3.5 MHz)
    
    ; A more practical detection uses the Scorpion's ProfROM signature
    ; or checks for the presence of the Beta 128 interface at #1F-#3F
    RET
```

> Detection routines are fragile because the Scorpion's I/O layout overlaps with other clones. The most reliable method is **measuring the frame T-state count** (which distinguishes 312-line from 320-line machines) and then probing Scorpion-specific ports. See [clone_timing.md](../../02_hardware/clones/clone_timing.md#detection-techniques) for the canonical decision tree.

---

## What Breaks When Porting 48K → Scorpion

1. **Pixel-precise multicolor**: effects appear shifted 9 T-states (about 1 pixel) left of their 48K position. Realign by inserting a 9 T-state `NOP` slide before the timed loop.

2. **Contention-dependent timing loops**: there is no contention, so a loop that relied on contention delays runs faster than on a 48K — but a loop in RAM with odd-length instructions runs slower than on a Pentagon, because each opcode fetch from RAM is aligned to an even T-state.

3. **I/O port conflicts**: the Scorpion maps additional ports (`#1FFD`, Beta 128 registers) that may collide with hardware you assumed was 48K-only.

4. **ROM routine behavior**: Scorpion's custom ROM (or ProfROM upgrade) replaces some entry points — code that calls specific 48K ROM addresses may behave differently.

### What Gets Better

1. **Optional 2× speed**: compute-intensive sections can run at 7 MHz with a single port access.
2. **256K RAM**: 4 banks of 64K available without external expansion.
3. **Built-in disk + joystick**: no need for external Beta 128 or Kempston interfaces.
4. **Predictable 50.08 Hz**: music plays at correct tempo (unlike Pentagon's 2.3% slowdown).

---

## Cross-References

- [Scorpion hardware](../../02_hardware/clones/scorpion.md) — full hardware reference (discrete logic, Zonov design, RAM banking)
- [Clone timing overview](../../02_hardware/clones/clone_timing.md) — all Soviet clones compared, decision tree
- [Video frame 48K](video_frame_48k.md) — base reference for the timing the Scorpion matches
- [Video frame Pentagon](video_frame_pentagon.md) — the *other* major Soviet clone, with very different timing
- [Video frame comparison](video_frame_comparison.md) — all models side-by-side
- [Contention model](../03_memory_and_io/contention_model.md) — what contention is, why the Scorpion has none but aligns RAM fetches (Even M1)
- [Z80 timing](../../01_cpu/z80_timing.md#where-the-cpu-samples-the-bus--fetch-vs-read) — when the Z80 latches data in a fetch vs a read
- [Clone video modes](clone_video_modes.md) — non-standard video modes (hires, GigaScreen) on clones

---

## Primary Sources

- **Scorpion ZS-256 Programmer's Reference** — ZXPress magazine articles (1996–1998), Scorpion ROM documentation. Reproduced at [zx-pk.ru](https://zx-pk.ru).
- **Unreal Speccy emulator** ([github.com/mkoloberdin/unrealspeccy](https://github.com/mkoloberdin/unrealspeccy)) — `unreal.ini` Scorpion preset: `FRAME=69888`, `PAPER=14364`, `LINE=224`, `INT=32`. Definitive timing values used by every other emulator.
- **ZXMAK2 emulator** ([github.com/zxmak/zxmak2](https://github.com/zxmak/zxmak2)) — two Scorpion models: the yellow board with Even M1 on fetches at `#4000`–`#FFFF` (`UlaScorpionYellow.cs`), and the green board with no Even M1 and a 70,784 T frame (`UlaScorpionGreen.cs`). Neither models contention.
- **SC15.1 EPLD equations** — [zx-pk.ru thread 940, post #40](https://zx-pk.ru/threads/940-scorpion-zs-256-turbo-(skhema)/page4.html): the Scorpion turbo board's WAIT and clock logic (ZS Company, 1996).
- **Sergey Zonov's original Scorpion documentation** — hardware schematics and I/O port tables, circulated on FidoNet in 1996-97 and archived at [Spectrum-computing.co.uk](https://spectrum-computing.co.uk).
