[← Home](../../README.md) · [Display & Timing](README.md)

# Interlace and Flicker — Why the Spectrum Picture Stays Still, Mostly

The ZX Spectrum is unusual among 1980s home computers: its video output is **non-interlaced**. Where broadcast PAL alternates two 312½-line fields at 25 Hz each to build a 625-line frame at 50 Hz, the Spectrum outputs the **same 312-line field 50 times per second**. This single design choice shapes everything about how Spectrum graphics flicker (or don't), how monitors react, and why modern LCD displays require special handling.

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
2. **Brightness** — brighter images flicker more visibly (the Ferry-Porter law: critical flicker frequency rises ~10 Hz per decade of luminance)
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

The P22 phosphor used in most European color CRTs has a decay time of approximately 5–15 ms to 10% brightness. At a 20 ms frame period (50 Hz), this means each scanline is still glowing at **~30–50% of its peak brightness** when the next refresh arrives — the eye perceives a continuous image.

```
CRT phosphor decay (typical P22 green channel):
  T=0 ms:   100% brightness (just refreshed)
  T=5 ms:    50% brightness
  T=10 ms:   20% brightness
  T=15 ms:    8% brightness
  T=20 ms:    3% brightness  ← next refresh arrives
  
Average perceived brightness: ~35% of peak
Flicker: visible only to sensitive viewers
```

This is why **CRT displays hide flicker that LCDs reveal**: the CRT's phosphor decay provides natural temporal smoothing. LCDs use sample-and-hold, where each pixel is held at full brightness for the entire frame period — this eliminates phosphor decay but introduces motion blur and makes flicker effects look different.

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

GigaScreen ([clone_video_modes.md](clone_video_modes.md)) alternates two attribute sets on even and odd frames to simulate 8×1 color resolution via temporal mixing. Each attribute set is displayed at 25 Hz — half the standard refresh rate.

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

### Frame-Rate Mismatch

Most modern LCDs run at **60 Hz** (or 120 Hz, 144 Hz). The Spectrum's 50.08 Hz output requires the display to either:

1. **Drop frames** — every 6th frame is dropped, producing visible judder on motion
2. **Duplicate frames** — every 5th frame is shown twice, producing visible stutter
3. **Adaptive sync (G-Sync/FreeSync)** — the display matches the source rate; requires a VRR-capable monitor

For 48.83 Hz Pentagon output on a 60 Hz LCD, the mismatch is worse: ~16.7% of frames must be dropped or duplicated.

### Modern Solutions

- **OSSC (Open Source Scan Converter)** — line-multiplies the Spectrum's signal to a higher resolution and feeds it to a VGA/HDMI display at the original refresh rate
- **RetroTINK upscalers** — similar function with additional frame-rate conversion options
- **GigaDEF / CRT emulation shaders** — software filters in emulators that simulate phosphor decay
- **FreeSync/G-Sync over HDMI** — modern monitors with VRR can lock to the Spectrum's 50.08 Hz natively

---

## VSYNC and HSYNC Tolerances

The Spectrum's sync signals are within broadcast PAL tolerances, but barely:

```
Standard PAL:
  HSYNC frequency:    15,625 Hz  (64.000 µs per line)
  VSYNC frequency:     50.000 Hz  (20.000 ms per frame)
  
ZX Spectrum 48K:
  HSYNC frequency:    15,625 Hz  (64.000 µs per line)  ← matches
  VSYNC frequency:     50.080 Hz  (19.968 ms per frame) ← 0.16% off

ZX Spectrum 128K / +2 / +2A:
  HSYNC frequency:    15,652 Hz  (~63.89 µs per line)
  VSYNC frequency:     50.020 Hz  (~19.99 ms per frame)

Pentagon:
  HSYNC frequency:    15,625 Hz  (matches 48K)
  VSYNC frequency:     48.830 Hz  (20.478 ms per frame) ← 2.3% off, marginal
```

Most CRTs tolerate ±2% deviation without issue. Some modern LCDs are stricter and may refuse to sync to the Pentagon's 48.83 Hz output entirely, requiring an upscaler.

---

## Mitigation Strategies for Developers

If you're writing software that targets both CRT and LCD displays:

1. **Avoid GigaScreen for moving images** — temporal mixing only works on impulse displays; on sample-and-hold LCDs it produces visible strobing without the smoothing benefit.
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
- [Border effects](border_effects.md) — timing-safe border writes
- [Raster timing](raster_timing.md) — beam position calculation
- [Video frame comparison](video_frame_comparison.md) — all models side-by-side

---

## Primary Sources

- [Chris Smith, The ZX Spectrum ULA: How to Design a Microcomputer](http://www.zxdesign.info/) — documents the ULA's non-interlaced output and its rationale.
- **IEEE Ferry-Porter law literature** — the canonical reference for human flicker perception thresholds, basis for the 50 Hz design choice.
- **Poynton, *Digital Video and HD: Algorithms and Interfaces*** — covers CRT vs LCD temporal response, sample-and-hold vs impulse display.
- **OSSC documentation** ([github.com/marqs85/ossc](https://github.com/marqs85/ossc)) — documents the frame-rate mismatch issues between 50.08 Hz Spectrum output and 60 Hz LCD displays.
- **RetroGFX CRT Shader documentation** — software emulation of phosphor decay for modern displays.
- [ZX Spectrum +2 / +3 Service Manual](https://www.worldofspectrum.org/hardware.html) — Amstrad documentation of the gate array's slightly non-standard sync timing.
- **[zx-pk.ru](https://zx-pk.ru) GigaScreen threads** — real-hardware reports of which GigaScreen color pairs flicker most visibly on Soviet CRT TVs.
