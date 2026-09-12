[← Home](../../README.md) · [Display & Timing](README.md)

# Interlace and Flicker — Why the Spectrum Picture Stays Still, Mostly

The ZX Spectrum is unusual among 1980s home computers: its video output is **non-interlaced**. Where broadcast PAL alternates two 312½-line fields at 25 Hz each to build a 625-line frame at 50 Hz, the Spectrum outputs the **same 312-line field 50 times per second**. This single design choice shapes everything about how Spectrum graphics flicker (or don't), and why modern LCDs handle flicker-based effects differently than CRTs.

This article covers the perception physics and the practical coding implications. For the underlying frame timing, see [video_frame_overview.md](video_frame_overview.md). For GigaScreen as a video mode (alternating two attribute sets), see [clone_video_modes.md](clone_video_modes.md). For color clash and the 8×8 attribute cell, see [color_system.md](color_system.md).

---

## Why the Spectrum Is Non-Interlaced

The Ferranti ULA was designed to drive a domestic PAL television, but it cheats: instead of producing two half-fields with proper VSYNC timing for interlaced display, it produces **one field repeated at ~50 Hz**. The TV's sync circuitry locks onto this as if it were a stable broadcast signal.

```
Broadcast PAL (interlaced):
  Field A (odd lines):   1, 3, 5, ..., 625     ←──┐
  Field B (even lines):  2, 4, 6, ..., 624     ←──┤
                                                  ├── Together: 625 lines at 50 Hz
                                                  │   (each field = 25 Hz)
  
ZX Spectrum 48K (non-interlaced):
  Single field:         0, 1, 2, ..., 311       ←── Repeated 50.08 times/sec
  
Result: only 312 lines per frame (vs broadcast 625), but no interlace artifacts.
```

This was a deliberate simplification. The benefits:

- **No interlace flicker** — every scanline is drawn every frame, so there's no 25 Hz temporal component to cause the eye to perceive flicker on horizontal edges.
- **Simpler ULA logic** — only one field type to generate, no half-line offset, no field-switching logic.
- **Stable vertical detail** — a single horizontal line drawn at scanline N stays there every frame.

The cost: **half the vertical resolution** of broadcast PAL (312 vs 625 lines). For the Spectrum's 192-line paper area, this is irrelevant — there's no resolution to lose. For higher-resolution clones (ATM Turbo 640×200, Profi 512×256), it remains non-interlaced.

### Pentagon Exception

The Pentagon generates **320 lines per frame** at 48.83 Hz — still non-interlaced. The extra 8 lines (vs 48K's 312) push the frame rate slightly below broadcast PAL's 50 Hz, but most TVs and monitors tolerate the small deviation.

---

## The 50 Hz Perception Threshold

The human eye's flicker sensitivity depends on **three factors**:

1. **Refresh rate** — 50 Hz is just above the threshold for most viewers in bright ambient light, but borderline in dim rooms
2. **Brightness** — brighter images flicker more visibly (the [Ferry-Porter law](https://en.wikipedia.org/wiki/Flicker_fusion_threshold): critical flicker frequency rises ~10 Hz per decade of luminance)
3. **Display technology** — CRT phosphor decay and LCD sample-and-hold behave very differently

### Ferry-Porter and the 50 Hz Borderline

```
Critical flicker frequency (CFF) for human vision:
  Dim room, dim display:  ~25 Hz
  Normal room, normal display:  ~40-50 Hz  ← PAL Spectrum is here
  Bright room, bright display:  ~60-80 Hz
  
At normal living-room brightness, a 50 Hz CRT display is at the edge
of perception. About 5-10% of viewers can see flicker on a PAL
Spectrum picture; the rest see a stable image.
```

This is why the Spectrum's 50 Hz refresh has historically been described as "acceptable" — most viewers don't notice flicker on a CRT, but it's not invisible. NTSC Spectrums (60 Hz, slightly less flicker-prone) existed but were never widely deployed.

### Phosphor Persistence

"P22" is not one phosphor. It is the standard **set of three** coatings used in color CRTs, and they decay very differently — which is why single-number "P22 decay time" figures vary wildly between datasheets and forum posts.

| Channel | Chemistry | Decay shape | Behavior |
|---|---|---|---|
| Red | Rare-earth (Y₂O₂S:Eu / Y₂O₃:Eu) | Near-exponential | Nearly all stored energy released within **1–2 ms**; dark long before the next frame |
| Green | Zinc sulfide (ZnS:Cu,Al) | Power law ≈ `t^(-1.1)` | Fast initial drop, then a heavy tail that persists far beyond one frame |
| Blue | Zinc sulfide (ZnS:Ag) | Power law ≈ `t^(-1.1)` | Same heavy-tailed behavior as green |

The best public measurement is Markus Kuhn's [photomultiplier characterization of a P22 tube](https://www.cl.cam.ac.uk/~mgk25/ieee02-optical.pdf) (University of Cambridge, 2002), which produced closed-form impulse-response fits for all three channels. Evaluating the green-channel fit over a 50 Hz frame, expressed as a percentage of the **frame-average luminance** — the level the eye adapts to, and the only meaningful yardstick for flicker:

```
Green channel decay, % of frame-average luminance (Kuhn 2002 fit):
  T=1 ms:    ~200%   ← spike phase, beam has just passed
  T=5 ms:     ~35%
  T=10 ms:    ~17%
  T=15 ms:    ~11%
  T=20 ms:     ~8%   ← next 50 Hz refresh arrives
  T=40 ms:     ~3.6% ← one GigaScreen alternation period later
  T=100 ms:    ~1.3%
  ... the tail has no cutoff: afterglow remains visible for minutes
      in a completely dark room (scotopic vision)

Red channel: <0.1% beyond 5 ms — effectively no persistence.
```

Exact numbers vary between tube generations and beam currents (the EIA registry TEP116-C classes the sulfide channels only coarsely, "medium short" to "medium", spanning 10 µs–100 ms), but the shape is universal. Two corrections to folk wisdom follow:

- **"% of peak" is the wrong unit.** The excitation spike lasts microseconds and reaches hundreds of times the frame average — the eye never perceives the peak. Relative to the mean, the green/blue glow at the moment of the next refresh is a few percent, not the tens of percent sometimes quoted.
- **The afterglow really does outlast the frame.** The sulfide power-law tail never fully ends: at 40 ms it is still ~3.6% of the mean, and it is measurable minutes later. This is genuine physical temporal blending — but at normal viewing brightness it is a modest contribution, not a 50/50 mix.

So a 50 Hz CRT picture is **not** steady light with the phosphor "bridging" the gap between frames. Green/blue modulation depth at 50 Hz remains large, and the picture reads as stable because 50 Hz sits at the edge of the critical flicker frequency for typical living-room brightness — consistent with the market producing 100 Hz TVs for the flicker-sensitive minority. What the phosphor does provide is **partial smoothing**: it softens each refresh into a decaying pulse and leaves a few percent of residual glow that cross-blends into the following frame. LCDs are sample-and-hold displays — each pixel is held at full brightness for the entire frame with no decay — so temporal effects reach the eye at full modulation. This difference is what makes flicker-based techniques such as GigaScreen look far better on CRTs (see below).

---

## Attribute Flicker — The 8×8 Trap

The Spectrum's standard attribute cell is **8×8 pixels** with two colors (ink + paper). When software modifies the attribute byte for a cell mid-frame, the entire cell changes color for the rest of the frame.

```
Frame N:    attribute byte = INK=7 (white) on PAPER=0 (black)
Frame N+1:  attribute byte = INK=0 (black) on PAPER=7 (white)
Frame N+2:  attribute byte = INK=7 (white) on PAPER=0 (black)

Result: the entire 8×8 cell flashes black↔white at 25 Hz (every other frame)
```

This produces **visible 25 Hz flicker**, well below the CFF threshold for any viewer. The eye perceives a clearly flashing rectangle.

### When This Happens Accidentally

- **Loading screens** that update attributes one row at a time may produce visible flicker if the ISR completes mid-screen
- **Scrolling routines** that shift attributes between frames can produce flicker if the shift crosses a cell boundary
- **BASIC programs** that POKE attribute bytes in a tight loop produce flicker because each POKE is visible for one frame

### When This Is Used Intentionally

- **Highlight effects** — flashing the cursor, the EDIT prompt, error messages
- **Menu selections** — alternating attribute to indicate the highlighted item
- **Loading stripes** — the famous yellow/cyan stripes during tape loading

The ROM's standard cursor blink is **once every 32 frames (~0.64 seconds)** — far slower than the flicker threshold and easily perceived as "blinking" rather than "flickering". This is the safe convention.

---

## GigaScreen Flicker — The Math

GigaScreen ([clone_video_modes.md](clone_video_modes.md)) alternates two attribute sets on even and odd frames to extend the perceived palette through temporal color mixing. Each attribute set is displayed at 25 Hz — half the standard refresh rate.

The flicker visibility depends entirely on the **contrast between the two attribute sets**:

```
Attribute A:  INK=0 (black)   on PAPER=7 (white)
Attribute B:  INK=7 (white)   on PAPER=0 (black)

→ Luminance swing: ~100% (full black ↔ full white)
→ 25 Hz flicker at maximum contrast: SEVERE, painful to view
```

```
Attribute A:  INK=0 (black)   on PAPER=1 (blue)
Attribute B:  INK=1 (blue)    on PAPER=0 (black)

→ Luminance swing: small (both have similar perceived brightness)
→ 25 Hz flicker at low contrast: mild, often acceptable
```

### Safe GigaScreen Colour Pairs

| Pair | Luminance swing | Flicker |
|---|---|---|
| Black ↔ White | Extreme | **Unusable** |
| Black ↔ Blue | Low | Safe |
| Black ↔ Red | Medium | Borderline |
| Black ↔ Magenta | Low | Safe |
| Blue ↔ Red | Medium | Borderline |
| Green ↔ Cyan | Low | Safe |
| Red ↔ Yellow | Medium | Borderline |
| Blue ↔ Magenta | Low | Safe |

**Rule of thumb**: choose two colors with similar perceived brightness (luminance) on a monochrome display. Colours close on a Y of YUV axis flicker less.

### Why GigaScreen Looks Blended on a Real CRT

If only ~8% of the previous frame's glow survives into the next, why does a well-paired GigaScreen image on a CRT look like a stable blended picture rather than 25 Hz strobing? Because the mixing happens mostly **in the eye, not on the phosphor**:

1. **[Talbot–Plateau law](https://en.wikipedia.org/wiki/Talbot-Plateau_law)** — when an alternating light is above the viewer's flicker-fusion threshold for its modulation depth, it is perceived as a steady light of the **time-averaged** color and brightness. The blend is computed by the visual system; the screen only has to alternate fast enough.
2. **Modulation depth is the free parameter** — the designer cannot raise the 25 Hz alternation rate, but can shrink the luminance swing of the pair (the tables above). Low-swing pairs fall below the fusion threshold and blend cleanly; black↔white stays far above it and strobes.
3. **The phosphor adds a little real mixing** — each refresh lands on a screen still carrying ~8% of the previous frame's color (green/blue), and the spike-plus-decay waveform is temporally softer than an LCD's flat sample-and-hold plateau. This is why GigaScreen is reported as looking "warmer" and more integrated on a CRT than a hard digital alternation.
4. **Pentagon runs it slightly slower** — at the Pentagon's 48.83 Hz frame rate ([video_frame_pentagon.md](video_frame_pentagon.md)), each attribute set is displayed at **~24.4 Hz** instead of 25 Hz, marginally increasing visible flicker relative to a 128K.

The reason GigaScreen looks *worse* on LCDs and emulators is the mirror image: sample-and-hold delivers the alternation as a full-modulation square wave, and on a 60 Hz host display the 25 Hz color flips land irregularly (one color held two host frames, the other three), producing low-frequency beats that read as harsh strobing. Emulator "mix"/"blend" modes sidestep the problem by displaying the mathematical Talbot average — `(A + B) / 2` — as a single frame, reproducing what a CRT viewer perceives without asking the viewer's visual system to do the fusion. See [multicolor_techniques.md §8.6](../../07_demoscene/multicolor_techniques.md) for the emulator-side view.

---

## Multicolor 8×1 — Flicker from Mistimed Effects

Multicolor effects change the attribute byte **mid-frame** to produce 8×1 color resolution (vs the standard 8×8). When the timing is correct, the effect is stable. When timing drifts by even one T-state, the attribute change happens one scanline too early or too late — and the result is visible flicker.

```
Correct timing (every frame):
  Scanline N:   attribute = A
  Scanline N+1: attribute = B  ← change happens exactly here

Mistimed by 1 T-state (frame 1):
  Scanline N:   attribute = A
  Scanline N+0.99: attribute = B  ← change one T-state early
  Scanline N+1: attribute = B

Mistimed by 1 T-state (frame 2):
  Scanline N:   attribute = A
  Scanline N+1: attribute = B  ← change exactly here

Result: the attribute boundary wobbles by one scanline between frames,
producing a visible "shimmer" along the boundary.
```

This is why multicolor effects are extremely sensitive to T-state positioning. Content ([contention_timing.md](contention_timing.md)) on the 48K can vary the actual cycle count by ±6 T-states per access, so code that runs in contended memory cannot maintain stable multicolor — it must run from uncontended RAM (`#8000`+) with carefully crafted NOP-padded loops.

---

## Modern LCD Display Compatibility

When the Spectrum's video output is fed to a modern LCD (via SCART, composite-to-HDMI upscaler, or emulation on an LCD panel), the display behavior changes:

### Sample-and-Hold vs CRT Phosphor

```
CRT (impulse display):
  Pixel refreshed at T=0, decays naturally
  Eye perceives: smooth motion, mild flicker
  
LCD (sample-and-hold):
  Pixel refreshed at T=0, held at full brightness until T=20 ms
  Eye perceives: no flicker, but motion blur on moving objects
```

For static Spectrum images, LCDs are fine. For moving objects (scrolling, sprites), LCDs add motion blur that the original CRT didn't have. This is why some emulators offer a "CRT shader" or "phosphor emulation" — to recreate the CRT's temporal smoothing.

Frame pacing on a fixed-refresh panel — what a 50.08 Hz (or 48.83 Hz Pentagon) signal does when the display insists on 60 Hz: dropped and duplicated frames, judder, sync capture ranges, and the upscalers and VRR displays that solve them — is a timing topic rather than a perception one; see [cycle_exact_accuracy.md](../../11_emulation/software/cycle_exact_accuracy.md), [crt_output.md](crt_output.md), and [video_frame_pentagon.md](video_frame_pentagon.md).

---

## Mitigation Strategies for Developers

If you're writing software that targets both CRT and LCD displays:

1. **Avoid GigaScreen for moving images** — the eye's temporal averaging works best on stationary content; moving edges shimmer as they are sampled alternately in both colors, and on sample-and-hold LCDs the alternation arrives at full modulation with no phosphor softening (see § Why GigaScreen Looks Blended on a Real CRT).
2. **Don't flash attributes faster than ~3 Hz** — anything above this risks triggering photosensitive epilepsy in susceptible viewers and produces visible flicker in everyone else.
3. **Use bright/bright attribute pairs carefully** — the "bright" flag doubles luminance, which doubles flicker visibility. Bright-on-bright GigaScreen is rarely acceptable.
4. **Test on real hardware** — CRT vs LCD will look different. What looks great on an emulator may flicker unbearably on a real CRT, and vice versa.
5. **Provide a "no-flicker" mode** — for menu screens, allow the user to choose standard 8×8 attributes over GigaScreen or multicolor effects.

---

## Cross-References

- [Video frame overview](video_frame_overview.md) — PAL fundamentals, frame structure
- [Color system](color_system.md) — the 8×8 attribute cell, color clash, palette
- [Clone video modes](clone_video_modes.md) — GigaScreen, multicolor, hires modes
- [Contention timing](contention_timing.md) — why mistimed multicolor effects flicker
- [CRT output](crt_output.md) — video output hardware (RF, composite, RGB, SCART, VGA)
- [Cycle-exact accuracy](../../11_emulation/software/cycle_exact_accuracy.md) — frame pacing, drops/duplicates, and judder on modern displays
- [Border effects](border_effects.md) — timing-safe border writes
- [Raster timing](raster_timing.md) — beam position calculation
- [Video frame comparison](video_frame_comparison.md) — all models side-by-side

---

## Primary Sources

- [Chris Smith, The ZX Spectrum ULA: How to Design a Microcomputer](http://www.zxdesign.info/) — documents the ULA's non-interlaced output and its rationale.
- **IEEE Ferry-Porter law literature** — the canonical reference for human flicker perception thresholds, basis for the 50 Hz design choice.
- **Poynton, *Digital Video and HD: Algorithms and Interfaces*** — covers CRT vs LCD temporal response, sample-and-hold vs impulse display.
- [ZX Spectrum +2 / +3 Service Manual](https://www.worldofspectrum.org/hardware.html) — Amstrad documentation of the gate array's slightly non-standard sync timing.
- **[zx-pk.ru](https://zx-pk.ru) GigaScreen threads** — real-hardware reports of which GigaScreen color pairs flicker most visibly on Soviet CRT TVs.
- **Markus G. Kuhn, "Optical Time-Domain Eavesdropping Risks of CRT Displays"** ([cl.cam.ac.uk](https://www.cl.cam.ac.uk/~mgk25/ieee02-optical.pdf)) — photomultiplier-measured impulse responses of the three P22 phosphor channels; source of the decay figures in this article.
- **EIA TEP116-C, "Optical Characteristics of Cathode-Ray Tube Screens"** (1993) — the registry standard behind single-number phosphor persistence ratings.
