[← Home](../../README.md) · [Display & Timing](README.md)

# ZX Evolution Video Frame — Pentagon Base, CPLD Glue, Two Configurations

The ZX Evolution (Резидент / PentEvo, NedoPC team, 2008–2011) is the most recent Russian-designed Spectrum-class machine still built around a **real Z80 CPU**. Where the [ZX Spectrum Next](video_frame_next.md) implements the entire machine in an FPGA, the Evolution keeps a physical Z80 and physical RAM, with two **Altera MAX CPLDs** (EPM7128S + EPM3032A) acting only as programmable glue logic — address decoding, memory paging, I/O mapping, and video counter generation.

The result is a machine whose **base video timing is identical to the Pentagon** (71,680 T-states/frame, 320 scanlines, 48.83 Hz, no contention), but which can be reconfigured at the CPLD level into very different hardware personalities.

> [!NOTE]
> This article covers the **video frame timing** of the ZX Evolution. For the OS/firmware stack (boot ROM, BaseConf, NedoDOS), see [evo_os.md](../../04_operating_systems/evo_os.md). For hardware details (PCB, RAM, IDE, PS/2), see the planned [zx_evo.md](../../02_hardware/newgen/README.md). For how the Evolution fits the broader clone landscape, see [clone_timing.md § ZX Evolution](../../02_hardware/clones/clone_timing.md).

---

## Frame Parameters (ZX Evolution, BaseConf)

```
┌──────────────────────────────────────────────────────────┐
│  ZX Evolution Frame Timing (BaseConf = Pentagon 1024)    │
├──────────────────────────────────────────────────────────┤
│  Hardware:                PCB with real Z80 + CPLDs      │
│  CPLDs:                   Altera EPM7128S + EPM3032A     │
│  CPU core:                Z80 (real chip, not FPGA)      │
│                                                          │
│  CPU clock (base):        3.500000 MHz                   │
│  CPU clock (turbo):       7.000 or 14.000 MHz            │
│                                                          │
│  T-states per frame:      71,680 (Pentagon base)         │
│  Scanlines:               320                            │
│  T-states per scanline:   224                            │
│  Frame rate:              48.83 Hz                       │
│                                                          │
│  INT position:            Line 304, T=0 (Pentagon-style) │
│  Paper starts at:         Line 80 (T=17,920)             │
│  Contention:              None                           │
│                                                          │
│  Configurations:          BaseConf, TS-Conf              │
└──────────────────────────────────────────────────────────┘
```

The Evolution was designed for **maximum compatibility with the existing Russian software library**, which overwhelmingly targets the Pentagon. Every timing parameter matches the Pentagon — same 320-line frame, same INT position near the end of the visible area, same lack of memory contention. Code that runs on a Pentagon runs on the Evolution unchanged.

---

## Why "Pentagon Evolution" (PentEvo)

The name **PentEvo** is literal: the machine was designed as a hardware-level successor to the **Pentagon 1024 SL 2.x**. The design goals were:

1. **Recreate the Pentagon** — same timing, same memory map, same no-contention behavior.
2. **Replace aging discrete logic with CPLDs** — the Pentagon's hundreds of 74-series chips were failing by the late 2000s; two CPLDs replace them all.
3. **Add modern peripherals** — IDE, PS/2 keyboard, PS/2 mouse, SD card via expansion.
4. **Stay binary-compatible** — every existing Pentagon demo, game, and OS should boot unmodified.

The result is sometimes called the **"Pentagon in CPLD clothing"**. From the CPU's perspective, it is indistinguishable from a well-built Pentagon 1024.

---

## Configurations: BaseConf vs TS-Conf

The Evolution's defining feature is its **two CPLD configurations**, which are essentially different "hardware personalities" the same board can present:

### BaseConf — The Pentagon-Compatible Mode

- Default configuration shipped with the board
- Implements a Pentagon 1024 with the standard memory map and timing
- INT at line 304, T=0 (Pentagon-standard position)
- VGA output via a separate scan-doubler circuit; base frame rate unchanged
- No enhanced video modes — what you see is what a Pentagon would show
- All classic Pentagon software runs unmodified

### TS-Conf — The Enhanced Video Mode

- Designed by Aleksandr Zhuravlev (`tsl`)
- Adds **hardware sprites** (32 sprites × 64 patterns), **tilemap** (320×200 with 8×8 tiles), and **per-scanline palette** (like the Next's copper but simpler)
- Adds **512 KB of dedicated VRAM** — sprites and tiles are fetched independently of main RAM, so there is **zero additional CPU contention**
- Base frame timing **does not change** — still 71,680 T-states, 320 lines, 48.83 Hz, no contention on main RAM
- TSR (Terminate-and-Stay-Resident) drivers provide a friendly API for the enhanced modes
- Software must be **specifically written for TS-Conf** — classic Pentagon software does not see the enhancements

> [!IMPORTANT]
> Switching between BaseConf and TS-Conf requires **reflashing the CPLD bitstream** (or loading a different bitstream from SD card on later revisions). It is not a runtime switch — the machine boots into one configuration and stays there until reboot. This is fundamentally different from the [Next's runtime mode switching](video_frame_next.md).

---

## Turbo Modes

The Evolution supports two turbo speeds via a port write:

| Speed | T-states/frame | Effective speedup | Use case |
|---|---|---|---|
| 3.5 MHz (default) | 71,680 | 1.0× | Pentagon compatibility |
| 7 MHz | 143,360 | 2.0× | Demos with heavy precalc |
| 14 MHz | 286,720 | 4.0× | TS-Conf software, demoscene work |

Unlike the ATM Turbo (whose 7 MHz mode is bottlenecked by the memory bus to ~1.43× effective speedup), the Evolution's turbo modes deliver **close to the theoretical maximum speedup** because the SRAM used in the Evolution supports the higher clock without inserted wait states.

```
ATM Turbo 7 MHz:    99,880 T-states/frame (1.43× effective)
ZX Evolution 7 MHz: 143,360 T-states/frame (2.00× effective)  ← clean 2×
ZX Evolution 14 MHz: 286,720 T-states/frame (4.00× effective)  ← clean 4×
```

Turbo can be enabled and disabled at runtime — typical Evolution software enables turbo during precalculation or decompression, then drops back to 3.5 MHz for timing-sensitive rendering.

---

## INT Position and ISR Design

The INT position matches the Pentagon — asserted at **line 304, near the end of the frame** (not at the start like the 48K). This means ISRs fire **after** the visible paper area has been drawn, giving the CPU uncontended time to update the screen for the *next* frame.

```
Pentagon / ZX Evolution frame layout:

  Line 0 ──────────  Top border (no paper)
  ...
  Line 80 ─────────  Paper starts (T=17,920 from frame start)
  ...
  Line 256 ─────────  Paper ends
  ...
  Line 304 ─────────  INT asserted here  ←─────────────
  ...
  Line 319 ─────────  End of frame
  Line 0 ──────────  New frame begins

ISR runs during lines 304-319 (16 lines = 3,584 T-states of uncontended
time at end of frame) plus lines 0-79 (80 lines = 17,920 T-states of
uncontended time before paper). Total ISR budget: ~21,500 T-states at 3.5 MHz.
```

### ISR Pattern (Pentagon/Evolution)

```z80
; Standard ISR for ZX Evolution (and Pentagon)
isr:
    EX   AF,AF'             ; 4T  — minimal context save
    EXX                      ; 4T  — alternate register set
    ; ...do ISR work...
    ; At 3.5 MHz: ~21,500 T-states available before paper
    ; At 7 MHz:   ~43,000 T-states available
    ; At 14 MHz:  ~86,000 T-states available
    EXX                      ; 4T
    EX   AF,AF'             ; 4T
    EI                       ; 4T
    RET                      ; 10T  — total ISR overhead: ~30T
```

The Pentagon-style ISR pattern is slightly different from the 48K pattern because INT fires at the *end* of the frame rather than the start. Code that does work in the ISR is preparing the **next** frame's screen, not reacting to the just-finished frame.

---

## VGA Output

The Evolution outputs **VGA** rather than composite video. The VGA signal is generated by a scan-doubler circuit that takes the original 50 Hz / 320-line Pentagon frame and doubles each scanline to produce a 640-line signal at the same 50 Hz refresh rate.

- **Base frame rate**: 48.83 Hz (unchanged from Pentagon)
- **Visible resolution**: doubled vertically, typically 640×480 within a 60 Hz or 50 Hz VGA frame depending on monitor compatibility
- **Colour depth**: 8-bit RGB per pixel (256 colors) — the original Spectrum palette is mapped into a larger TS-Conf palette space

> [!WARNING]
> Modern VGA monitors may refuse to sync to a 48.83 Hz signal — the standard VGA minimum is 56 Hz. The Evolution works best on CRT monitors, multisync LCDs, or via an OSSC/upscaler. Some TS-Conf software includes a "60 Hz mode" that adjusts the frame counter to 65,000 T-states for monitor compatibility, at the cost of breaking Pentagon-compatibility.

---

## Detecting the Evolution at Runtime

```z80
; Detect ZX Evolution
; Method: probe the Evolution's config port
DetectEvo:
    LD   BC,#F8              ; Configuration port (model-specific)
    IN   A,(C)
    AND  #F0
    CP   #E0                 ; Evolution responds with #Ex pattern
    JR   Z,isEvo
    
    ; Alternative: check for TS-Conf extensions
    LD   BC,#BF              ; TS-Conf sprite/tile control port
    IN   A,(C)
    CP   #TS_MAGIC           ; TS-Conf-specific signature
    JR   Z,isTSConf
    
    ; Fall through to standard Pentagon code
    RET
```

Most Russian demoscene software that targets the Evolution simply assumes Pentagon timing and uses the Evolution's extra speed as an invisible speed boost — detection is only necessary if the software needs to use TS-Conf's sprites or tilemap.

---

## Software Compatibility Matrix

| Software type | Compatibility on Evolution |
|---|---|
| **Pentagon 128/1024 software** | **Excellent** — runs identically, no changes needed |
| **48K software (assuming 50 Hz)** | **Good** — runs ~2.4% slower due to 48.83 Hz (same as on Pentagon) |
| **48K multicolor effects** | **Broken on Pentagon/Evo** — no contention pattern to ride |
| **TS-Conf-native software** | **Excellent on TS-Conf, broken on BaseConf** |
| **ATM Turbo software** | Runs via "ATM-mode" CPLD configuration on some revisions |
| **Music (AY)** | Runs at correct tempo (48.83 Hz, like Pentagon) |
| **Race-the-beam effects** | Possible but require Pentagon-timed code, not 48K-timed |

The Evolution is, in effect, **the modern reference Pentagon**. If your software runs on the Evolution, it runs on every other Pentagon-class machine.

---

## Cross-References

- [ZX Evolution OS / firmware stack](../../04_operating_systems/evo_os.md) — boot ROM, BaseConf, TS-Conf, NedoDOS boot process
- [Video frame Pentagon](video_frame_pentagon.md) — the base timing model the Evolution inherits
- [Video frame Next](video_frame_next.md) — the Western FPGA equivalent, with configurable timing
- [Clone timing overview](../../02_hardware/clones/clone_timing.md) — full per-clone comparison table
- [Video frame comparison](video_frame_comparison.md) — all models side-by-side, including the Evolution
- [NedoDOS](../../04_operating_systems/nedo_dos.md) — the primary DOS for ZX Evolution
- [Cycle-exact accuracy](../../11_emulation/software/cycle_exact_accuracy.md) — why Pentagon/Evolution timing differs from 48K

---

## Primary Sources

- **NedoPC team documentation** — original hardware specifications and BaseConf/TS-Conf reference manuals, archived at [nedopc.com](https://nedopc.com) and the [SpeccyWiki ZX Evolution page](https://speccy.info).
- **Unreal Speccy emulator** ([github.com/mkoloberdin/unrealspeccy](https://github.com/mkoloberdin/unrealspeccy)) — `Pentagon 1024 SL v2` and `PentEvo` model presets document the 71,680 T-state frame and INT-at-line-304 position.
- **ZXMAK2 emulator** ([github.com/zxmak/zxmak2](https://github.com/zxmak2)) — Implements both BaseConf and TS-Conf personalities; source code documents the 7/14 MHz turbo mode timing.
- **UnrealTSConf / Xevord emulator forks** — community forks that specifically test TS-Conf sprite/tile/palette timing.
- **TS-Conf Programming Reference** (Russian, archived at nedopc.org) — official documentation for the sprite, tilemap, and palette API.
- **zx-pk.ru forum threads** — Real-hardware measurements of the Evolution's VGA output, turbo-mode effectiveness, and TS-Conf quirks. Notable threads: "TS-Conf sprite timing", "PentEvo vs Pentagon timing comparison", "Evo 14MHz speed test".
