[← Home](../../README.md) · [Display & Timing](README.md)

# Other Soviet Clone Video Frames — Kay, ATM Turbo, Profi, Byte, Quorum, Leningrad, LEC

Beyond the two dominant Soviet clones — [Pentagon](video_frame_pentagon.md) (320 lines, 48.83 Hz, no contention) and [Scorpion](video_frame_scorpion.md) (312 lines, 50.08 Hz, revision-dependent contention) — there is a long tail of less common clones with their own timing quirks. Most match the 48K at the macro level (312 lines, 224 T-states, 69,888 T-states/frame), but differ in horizontal phase, contention behavior, and turbo modes.

> [!NOTE]
> This article covers the **video frame timing** of the long tail of Soviet clones. For hardware details (RAM, ROM, I/O ports, expansions), see [atm_turbo.md](../../02_hardware/clones/atm_turbo.md) and the planned [kay.md](../../02_hardware/clones/README.md), [profi.md](../../02_hardware/clones/README.md). The big-picture comparison across all clones lives in [clone_timing.md](../../02_hardware/clones/clone_timing.md).

---

## Quick Comparison

| Clone | Year | T/frame | Lines | Turbo | Contention | Notable |
|---|---|---|---|---|---|---|
| Pentagon 128 | 1989 | **71,680** | **320** | — | None | Most popular, weird 48.83 Hz |
| Scorpion ZS-256 | 1996 | 69,888 | 312 | 7 MHz | Revision-dep. | +9 T horizontal shift |
| Kay 1024 | 1998 | 69,888 | 312 | 7 MHz | None | GigaScreen on Kay 2006 |
| ATM Turbo 2+ | 1994 | ~69,888 | ~312 | **7 MHz** | Minimal | 640×200 text mode for CP/M |
| Profi 5.03 | 1991 | 69,888 | 312 | 5–7 MHz | None | **Paper offset +245 T-states** |
| Byte | 1991 | 69,888 | 312 | — | None | Ukrainian clone, compact |
| Quorum 64/256 | 1990 | 69,888 | 312 | — | None | Lower-cost Soviet |
| Leningrad 1/2 | 1988 | **71,680** | **320** | — | None | Pentagon precursor |
| LEC 48/528 | 1991 | 69,888 | 312 | — | None | Belarus clone |

Sources: Unreal Speccy `unreal.ini` presets, ZXMAK2 model list, emulator timing tables, real-hardware measurements on zx-pk.ru.

---

## Kay 1024 / Kay 2006 NB

The Kay 1024 (Кэй, NEMO company, St. Petersburg, 1998) is a high-end clone with 1024K of RAM and a 7 MHz turbo mode. Built from discrete logic (КР1533 series). The Kay 2006 NB revision adds an Altera EPM7064 CPLD for enhanced video.

### Frame Timing

| Parameter | Value | vs 48K |
|---|---|---|
| T-states/frame | 69,888 | Same |
| Scanlines | 312 | Same |
| T-states/scanline | 224 | Same |
| Frame rate | 50.08 Hz | Same |
| Paper offset | T=14,336 | ~Same |
| Contention | **None** | Differs |
| Turbo | Optional 7 MHz | New |

The Kay is **the cleanest Soviet clone to target** if you want 48K-compatible timing without contention headaches. It matches 48K timing exactly at the macro level and has no contention, so timing-sensitive code that breaks on Pentagon (due to 320-line frame) and on Scorpion (due to +9 T horizontal shift) runs cleanly.

### Kay 2006 NB Enhanced Modes

The 2006 revision's CPLD adds three video modes that **don't change base timing** but affect how the video circuit reads RAM:

- **Multicolor mode** — per-scanline attribute changes via a shadow attribute buffer in alternate RAM bank; no CPU contention because the video circuit reads from a separate buffer
- **GigaScreen** — alternates two attribute sets on even/odd frames to simulate 8×1 color resolution via PAL chroma bleed; works on stock CRTs but produces visible flicker
- **512×192 pixel mode** — double horizontal resolution in 2 colors, useful for static title screens

These modes are Kay-specific and not portable. See [clone_video_modes.md](clone_video_modes.md) for the cross-clone survey.

---

## ATM Turbo

The ATM Turbo (АТМ Турбо, designed by Alexander Kuzmin and Viktor Shcherbakov, 1994) is the most divergent popular clone. It supports ZX Spectrum and CP/M modes with several video subsystems.

### Frame Timing

| Parameter | Standard mode | Turbo mode |
|---|---|---|
| CPU clock | 3.500000 MHz | **7.000000 MHz** |
| T-states/frame | ~69,888 | ~139,776 |
| Scanlines | ~312 | ~312 (same) |
| Frame rate | 50.08 Hz | 50.08 Hz |
| Contention | Minimal / none | Minimal / none |

### The 7 MHz Turbo Anomaly

ATM Turbo's 7 MHz mode is unusual because it **doesn't merely double the CPU clock** — it also slightly alters memory access patterns. The reported frame T-state count at 7 MHz is approximately **99,880** in some sources rather than the expected 139,776 (2 × 69,888). This number comes from emulator presets (Unreal Speccy `ATM7MHz=99880`) and reflects that the memory bus runs at a divided clock between 3.5 and 7 MHz, so the CPU is sometimes stalled waiting for RAM slots.

```
ATM Turbo 7 MHz frame:
  Expected if pure 2× clock:  69,888 × 2 = 139,776 T-states
  Actual reported:           ~99,880 T-states
  Effective speedup:         ~1.43× (not 2×)
  
  The CPU gets more cycles per frame than at 3.5 MHz,
  but not twice as many — RAM access can't keep up.
```

> [!WARNING]
> If you port timing-critical code to ATM Turbo 7 MHz, you cannot simply divide all your T-state budgets by 2. The effective speedup is closer to **1.43×**, and the exact value depends on the mix of memory access in your inner loop. Profile on real hardware or emulator.

### CP/M and Text Modes

The ATM Turbo's CP/M mode uses a 640×200 monochrome video mode that generates timing independently of the ZX Spectrum mode. When CP/M is active:

- The visible area is different (640 pixels wide vs 256)
- The frame timing may be 70 Hz or 60 Hz to match VGA-style output on some revisions
- INT may be repositioned for the CP/M BIOS

These modes are documented in the ATM Turbo manual and rarely encountered in modern demoscene work, but they exist.

---

## Profi 5.03 / 5.04

The Profi (Профі, designed in Lviv, Ukraine, 1991) is a Russian/Ukrainian professional clone with ISA-like expansion and VGA output on later revisions.

### Frame Timing

| Parameter | Value | vs 48K |
|---|---|---|
| T-states/frame | 69,888 | Same |
| Scanlines | 312 | Same |
| Frame rate | 50.08 Hz | Same |
| Paper offset | **T=12,580** | **Off by −1,755 T-states!** |
| Contention | None | Differs |
| Turbo | Optional 5 MHz or 7 MHz | New |

The Profi's most distinctive quirk is its **paper offset**: the paper area starts at T=12,580 instead of T=14,335 (48K) — that's **1,755 T-states earlier** in the frame, equivalent to about 7.8 scanlines earlier. This is a consequence of the Profi's revised video counter logic.

```
48K frame:    INT → 14,335 T → Paper starts at scanline 64
Profi frame:  INT → 12,580 T → Paper starts at scanline ~56

Profi has ~12% LESS time after INT before paper area starts.
ISRs that assume 14,336 T-states of uncontended setup time
may still be running when paper begins.
```

> [!WARNING]
> Code that uses `HALT` to wait for INT and then assumes 14,336 T-states of free time before paper will **race the beam** on Profi and may write pixels into the visible area before the paper fetch cycle has started. Test specifically on Profi or skip Profi support if your effects depend on tight timing.

### VGA Output

Profi 5.04 added a VGA output option that runs from a separate pixel clock. The base frame rate remains 50.08 Hz (CGA-style 640×200 at 50 Hz, doubled scanlines to 400 visible). On modern VGA monitors this works but may require a VRR-capable display for clean sync.

---

## Byte, Quorum, Leningrad, LEC

These are the smaller-volume Soviet clones. Their timing is well-documented in emulator sources (Unreal Speccy, ZXMAK2) because each was distinct enough to require its own model preset.

### Byte

- **Manufacturer**: Ukraine, ~1991
- **Frame**: 69,888 T-states, 312 lines, 50.08 Hz (48K-compatible)
- **Contention**: None
- **Notes**: Compact design, moderate popularity in Ukraine. Standard timing — most 48K software works.

### Quorum 64 / Quorum 256

- **Manufacturer**: USSR, ~1990
- **Frame**: 69,888 T-states, 312 lines (48K-compatible)
- **Contention**: None
- **Notes**: Lower-cost Soviet alternative to the Scorpion. Limited expansion, no turbo mode.

### Leningrad 1 / Leningrad 2

- **Manufacturer**: USSR, 1988
- **Frame**: **71,680 T-states, 320 lines** (Pentagon precursor!)
- **Contention**: None
- **Notes**: The Leningrad predates the Pentagon and uses the same 320-line counter. The Pentagon inherited its timing model. If you write code for Pentagon, it works on Leningrad with no changes.

### LEC 48 / LEC 528

- **Manufacturer**: Belarus, ~1991
- **Frame**: 69,888 T-states, 312 lines (48K-compatible)
- **Contention**: None
- **Notes**: Linear-frame, 48K-timing. Modest expansion (up to 528K). Standard timing.

---

## General Rules for Soviet Clones

### What Soviet Clones Almost Always Have in Common

1. **No Ferranti ULA** — built from discrete TTL (early) or CPLD (late). Bus arbitration differs fundamentally from the original.

2. **No contention, or contention-limited** — discrete logic rarely implements the precise CPU-stall pattern of the ULA. The conservative assumption is **zero contention**.

3. **312 or 320 scanlines, no in-between** — Soviet designers chose one of two binary counter patterns. 312 matches 48K (50.08 Hz); 320 matches Pentagon/Leningrad (48.83 Hz).

4. **224 T-states per scanline** — universally matches 48K because the pixel clock derives from the same 14 MHz / 4 divider.

5. **INT at line 0, T=0** — universally aligned with 48K so that 48K ISRs fire at the right time.

6. **Optional turbo mode** — almost every late-90s clone has a 7 MHz option. Some (ATM Turbo, Scorpion, Kay, Profi) have it as standard.

### What Differs Wildly

1. **Horizontal phase** — the position of paper-start within each line varies by ±10 T-states between clones. Pixel-precise multicolor effects cannot be ported without re-timing.

2. **Paper vertical offset** — the Profi starts paper 1,755 T-states earlier than 48K. Other clones match 48K exactly.

3. **Turbo speedup factor** — pure 2× for Scorpion/Kay, ~1.43× for ATM Turbo (memory-bus-limited), 1.4–2.0× for Profi depending on revision.

4. **Video output standard** — composite, RGB, or VGA, all of which may affect visible picture geometry.

---

## Detecting Which Clone You're On

There is no universal detection routine. The most reliable heuristic combines:

1. **Measure T-states per frame** by counting loop iterations between INTs.
   - 69,888 → 312-line machine (48K, Scorpion, Kay, Profi, Byte, Quorum, LEC)
   - 71,680 → 320-line machine (Pentagon, Leningrad)
   - ~99,880 → ATM Turbo at 7 MHz

2. **Probe the contention pattern** by writing to screen RAM and measuring read-back time.
   - No slowdown → Pentagon-class (no contention)
   - 6-5-4-3-2-1-0-0 pattern → 48K-class
   - Inconsistent → Scorpion (revision-dependent)

3. **Probe paper offset** by reading `[number]` floating bus values at specific T-states.
   - Floating bus starts at T=14,335 → 48K-class
   - Floating bus starts at T=14,344 → Scorpion
   - Floating bus starts at T=12,580 → Profi

4. **Probe specific I/O ports** for the clone's banking extension registers.

The canonical decision tree is in [clone_timing.md § Clone Detection](../../02_hardware/clones/clone_timing.md#clone-detection).

---

## Cross-References

- [Clone timing overview](../../02_hardware/clones/clone_timing.md) — the master cross-clone comparison and detection decision tree
- [ATM Turbo hardware](../../02_hardware/clones/atm_turbo.md) — full hardware reference (CP/M, turbo, video modes)
- [Video frame Pentagon](video_frame_pentagon.md) — 320-line / 48.83 Hz clone reference
- [Video frame Scorpion](video_frame_scorpion.md) — 312-line / 50.08 Hz / 7 MHz clone reference
- [Video frame 48K](video_frame_48k.md) — the base reference
- [Video frame comparison](video_frame_comparison.md) — all models side-by-side
- [Clone video modes](clone_video_modes.md) — non-standard video modes (GigaScreen, hires, multicolor)
- [Contention model](../03_memory_and_io/contention_model.md) — what contention is, why clones lack it
- [Contention timing](contention_timing.md) — per-model contention patterns deep dive

---

## Primary Sources

- **Unreal Speccy emulator** ([github.com/mkoloberdin/unrealspeccy](https://github.com/mkoloberdin/unrealspeccy)) — `unreal.ini` defines the per-model frame timings: `FRAME=69888` (48K/Scorpion/Kay/ATM 3.5MHz/Profi), `FRAME=71680` (Pentagon/Leningrad), `FRAME=99880` (ATM 7MHz), `PAPER=14364` (Scorpion), `PAPER=12580` (Profi). These presets are the de facto timing reference for all emulators.
- **ZXMAK2 emulator** ([github.com/zxmak/zxmak2](https://github.com/zxmak/zxmak2)) — 16+ clone models with separate contention profiles. Source code documents per-revision Scorpion contention and the ATM Turbo speedup anomaly.
- **zx-pk.ru forum threads** — Russian-language real-hardware measurements and clone-specific discussions. Notable threads: "Timing measurements on Profi 5.03", "ATM Turbo 7MHz real speed", "Kay 2006 GigaScreen details".
- **SpeccyWiki (speccy.info)** — Russian-language clone encyclopaedia with per-clone hardware specifications.
- **spectrum-computing.co.uk hardware catalog** — clone hardware profiles with original documentation links.
