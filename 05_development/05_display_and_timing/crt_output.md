[← Home](../../README.md) · [Display & Timing](README.md)

# CRT Output — What the Viewer Actually Sees

The Spectrum generates a 256×192-pixel image inside a 312-scanline PAL video frame, but what reaches the viewer's eye is shaped by three layers of analog processing: the ULA's video pipeline, the modulator or RGB encoder stage, and the display device itself. Two Spectrums running the same software can produce wildly different pictures depending on what monitor they are connected to.

This article is the **software developer's view** of the CRT output: what reaches the eye, what gets lost, and how to write code that looks correct across the range of displays a Spectrum might drive. For the hardware output stage (modulators, encoders, connectors, cables), see [video_output.md](../../03_io/peripherals/video_output.md). For the perception physics of flicker, see [interlace_and_flicker.md](interlace_and_flicker.md).

---

## The Visible Picture — What's Actually Shown

### The Spectrum's Native Image

The ULA generates a picture with the following regions:

```
┌────────────────────────────────────────────────────┐
│                                                    │  Border area
│                                                    │  (variable colour,
│   ┌────────────────────────────────────────┐       │   set by port #FE)
│   │                                        │       │
│   │         256 × 192 paper area           │       │
│   │         (pixel + attribute data)       │       │
│   │                                        │       │
│   └────────────────────────────────────────┘       │
│                                                    │
│                                                    │  Border continues
└────────────────────────────────────────────────────┘  around all four sides
```

- **Paper area**: 256×192 pixels = 32×24 attribute cells, displayed at the center of the frame
- **Border area**: a single color surrounding the paper, set by bits 3-5 of port `#FE`
- **Total video frame**: 312 scanlines × ~448 T-states worth of horizontal time (48K)

The ULA generates 256 pixels horizontally within a 224-T-state scanline. Each pixel is displayed for **approximately 0.9787 µs** (1/3.5 MHz × ~3.43 T-states).

### What the Monitor Actually Shows

Different display types show different amounts of the Spectrum's frame:

| Display type | Visible border | Visible paper | Aspect ratio (paper) |
|---|---|---|---|
| 1980s domestic PAL TV (CRT) | Crop to ~70-80% of frame | Full paper visible | Stretched to 4:3 |
| 1990s PAL CRT via SCART RGB | Crop to ~85% of frame | Full paper visible | Stretched to 4:3 |
| Sony PVM / Commodore 1084 (RGB CRT) | Variable (underscan mode available) | Full paper visible | Calibrated 4:3 |
| Modern LCD via OSSC | Frame-multiplied, no crop | Full paper visible | Configurable (1:1 or 4:3) |
| Modern LCD via composite input | Heavy overscan crop | May lose 1-2 cells of border | Stretched to 16:9 |
| Emulator on PC | Pixel-exact | Exact 256×192 visible | Configurable |

The domestic TV's heavy overscan crop means **2-3 attribute cells of border around the paper may be invisible** on the original target hardware. Code that draws important information in the outermost border region risks being cut off on real hardware.

---

## Pixel Aspect Ratio — Pixels Are NOT Square

The Spectrum's pixel aspect ratio is **not 1:1**. The paper area is 256 pixels wide × 192 scanlines tall, but the displayed picture on a 4:3 CRT is **320×256 effective pixels** (because the CRT's pixels are taller than they are wide).

```
CRT pixel aspect ratio for ZX Spectrum (PAL):
  
  Horizontal pixels: 256 in the paper area
  Vertical pixels:   192 scanlines
  
  Displayed aspect:  4:3 (1.333)
  
  Pixel aspect:      (256/192) × (3/4) = 1.0
                     ... wait, that's 1.0?
  
  Actually: each Spectrum pixel is wider than it is tall.
  Correct math:
    Display width:  256 pixels × pixel_width = 4 units
    Display height: 192 pixels × pixel_height = 3 units
    Pixel_width / pixel_height = (4/256) / (3/192) = 0.015625 / 0.015625 = 1.0
  
  But: PAL pixels are not square to begin with.
  PAL pixel aspect ratio (CCIR-601): 12:11 (1.0909)
  
  Combined Spectrum pixel aspect on PAL CRT:
    pixel_width / pixel_height ≈ 1.0 (after PAL compensation)
    "Looks square on a correctly-adjusted PAL CRT"
```

### Practical Implications

- **Circles look round** when the CRT is correctly adjusted
- **Diagonal lines** have a 45° angle visually (matches mathematical expectation)
- On a modern LCD with 1:1 pixel mapping (no aspect correction), circles look **slightly tall** — the picture is being squeezed horizontally

### Emulator Aspect Correction

Modern emulators offer an "aspect correction" option that rescales the 256×192 buffer to display at the correct 4:3 ratio. Without this correction, the picture looks squeezed; with it, the picture matches what the original CRT would show.

Some emulators also offer a "pixel-perfect" mode that displays each Spectrum pixel as exactly one modern pixel — useful for examining artwork but not historically accurate.

---

## Composite Video Artifacts

When the Spectrum is connected via composite video (RF modulator on 48K, composite output on 128K, or any Soviet clone's composite output), several analog artifacts alter the picture:

### Dot Crawl

The PAL color encoding alternates the phase of the V (R-Y) component on each scanline. This causes the chroma information to appear to "crawl" vertically across multiple frames — visible as a wavy pattern along edges between saturated colors.

```
Frame N:   pixel X on scanline Y shows colour A
Frame N+1: same pixel shows slightly shifted colour due to phase alternation
Frame N+2: back to original

Result: horizontal edges between bright colours show visible "crawl"
```

**Mitigation**: use RGB output (SCART) instead of composite, or run on an emulator that does not emulate chroma artifacts.

### Colour Bleed (Chroma Crosstalk)

Adjacent bright colors on the same scanline may bleed into each other because the chroma bandwidth of composite PAL (~1 MHz) is much lower than the luminance bandwidth (~5 MHz). This is why a single pixel of red surrounded by blue may appear purple on composite but red on RGB.

### Luminance Smearing

The luminance bandwidth on a domestic CRT is also limited — typically to about 4-4.5 MHz. A single-pixel-wide horizontal line (one pixel on, next pixel off) produces a barely-visible smear rather than a sharp edge.

```
Pixel pattern:   ████░░░░░░░░████████
On RGB CRT:      sharp transitions
On composite:    visible smearing, edges are soft
On modern LCD via composite: smearing + dot crawl
On emulator (no artifact emulation): pixel-exact sharpness
```

### Y/C Separation (S-Video)

The S-Video modification for the 48K ([video_output.md § S-Video alternative](../../03_io/peripherals/video_output.md)) separates luminance and chroma into two signals, eliminating crosstalk. The result is significantly sharper than composite but still analog.

---

## Per-Display Behaviour Reference

### Domestic PAL CRT (1980s-1990s)

The original target hardware. Properties:

- **Refresh**: 50 Hz interlaced (when receiving broadcast) or 50.08 Hz progressive (when receiving Spectrum signal)
- **Visible area**: ~85-90% of the transmitted frame, with substantial overscan crop
- **Pixel aspect**: 1:1 after PAL compensation
- **Colour reproduction**: accurate within PAL gamut; bright/dim distinction visible
- **Border color**: visible around paper, but the outermost 1-2 cm may be cropped
- **Phosphor decay**: ~5-15 ms, providing natural motion smoothing
- **Flicker**: minimal at 50 Hz, mild at 25 Hz (GigaScreen)

This is what Spectrum software was designed for. If it looks right on a 1985-era PAL CRT, it looks "correct".

### RGB Monitor (Sony PVM, Commodore 1084)

These are professional-grade CRTs that bypass composite encoding entirely and accept TTL or analog RGB directly:

- **Visible area**: configurable (underscan mode shows full frame including border)
- **Pixel aspect**: 1:1 (these monitors don't apply PAL aspect correction)
- **Colour reproduction**: extremely accurate; bright/dim distinction crisp
- **Sharpness**: pixel-exact — every pixel boundary is visible
- **Phosphor decay**: P22 (similar to domestic CRTs)

These monitors are the **preferred display** for Spectrum software today because they preserve all the original detail without composite artifacts. But circles will look slightly **taller than wide** because they don't apply PAL aspect correction.

### Modern LCD via OSSC

The OSSC line-multiplies the Spectrum's signal to drive a modern HDMI/VGA display:

- **Refresh**: original 50.08 Hz (preserved exactly)
- **Visible area**: full frame, no overscan crop
- **Pixel aspect**: configurable (1:1, 4:3, or custom)
- **Colour reproduction**: 8-bit RGB, accurate
- **Sharpness**: pixel-exact, possibly with scanline simulation
- **Phosphor decay**: none (LCD sample-and-hold); motion looks different from CRT
- **Flicker**: none on the LCD (50 Hz signal is held, not refreshed at 50 Hz)

### Modern LCD via Composite Input

Many modern TVs still accept composite video, but the result is poor:

- **Refresh**: usually converted to 60 Hz with frame dropping/duplication
- **Visible area**: heavy overscan crop (TV assumes broadcast framing)
- **Colour reproduction**: shifted by NTSC/PAL conversion if TV is NTSC-region
- **Sharpness**: degraded by analog-to-digital conversion
- **Flicker**: any 25 Hz effect (GigaScreen) becomes painful strobing

**Not recommended** for serious Spectrum use.

### Emulator on PC

The most variable case. Emulators offer many options:

- **Refresh**: typically 60 Hz (matches host display), or original 50.08 Hz if VRR
- **Pixel aspect**: configurable (pixel-perfect vs 4:3 vs stretched)
- **Colour reproduction**: accurate (digital)
- **Sharpness**: pixel-exact
- **CRT shader effects**: optional (scanlines, phosphor decay, aperture grille)
- **Flicker**: depends on shader — CRT shaders can recreate flicker; pixel-perfect modes do not

---

## Writing Code That Looks Right Everywhere

### Border Region

- **Don't draw critical information in the outer border** — it may be cropped on domestic CRTs
- **Use the border for ambient effects** (raster bars, frame indicators) but not for primary gameplay
- **The "safe" border area** is approximately 2 attribute cells (16 pixels) wider/taller than the paper — anything beyond that may be cut

### Aspect Ratio

- **Design artwork as 256×192** — the ULA's native resolution
- **Test on a CRT or with aspect correction enabled** — if circles look round, you're correct
- **Don't use single-pixel diagonal lines as critical detail** — they smear on composite, look stair-stepped on pixel-perfect LCDs

### Colour Choice

- **Avoid pure saturated primaries adjacent to each other** (red next to blue, magenta next to cyan) — they bleed on composite
- **Use the BRIGHT attribute to double your palette** but be aware that bright variants may wash out on poorly-adjusted CRTs
- **For GigaScreen ([clone_video_modes.md](clone_video_modes.md))**: choose color pairs with similar luminance to minimize 25 Hz flicker (see [interlace_and_flicker.md](interlace_and_flicker.md))

### Pixel-Level Detail

- **Single-pixel-wide horizontal features** are unreliable on composite video — they smear
- **Single-pixel-wide vertical features** are sharp on RGB but may strobe on interlace-capable displays (though the Spectrum's progressive output makes this rare)
- **For text and small detail, use 2-pixel-wide strokes** for guaranteed visibility on all display types

### Border Colour Effects

- **Border raster bars** (`OUT (#FE),A` timing tricks) work on every display type, but their visibility depends on how much border the display shows
- **Domestic CRTs**: shows the outer ~2 cm of border, raster bars visible
- **Modern LCD via OSSC**: shows the entire border area, raster bars extremely visible
- **Modern LCD via composite**: shows minimal border, raster bars may be cut

---

## Diagnosing Display Problems

| Symptom | Likely cause | Fix |
|---|---|---|
| Picture squeezed horizontally on LCD | Pixel aspect not corrected | Enable 4:3 aspect ratio in emulator/upscaler |
| Circles look like ellipses on LCD | Pixel aspect correction off | Enable PAL aspect correction |
| Circles look like tall ellipses on PVM | RGB monitor not applying PAL correction | This is correct behavior — design artwork for it |
| Diagonal lines look jagged on LCD | No scanline simulation | Enable CRT shader |
| Saturated colors bleed on composite | Composite chroma crosstalk | Switch to RGB (SCART) output |
| Border looks "cropped" on emulator | Emulator is showing full frame (no overscan) | This is correct — real CRTs cropped this |
| Image rolls or won't sync | Refresh rate mismatch (50 Hz source, 60 Hz display) | Use OSSC with proper line multiplication, or VRR display |
| Flicker visible on GigaScreen | 25 Hz attribute alternation | Use lower-contrast color pairs; see [interlace_and_flicker.md](interlace_and_flicker.md) |

---

## The "Correct" Display

For historically accurate Spectrum graphics, the reference display is a **1980s domestic PAL CRT** connected via the Spectrum's RF modulator (48K) or RGB SCART cable (128K onwards). On this display:

- The picture has the expected aspect ratio
- Colours are within PAL gamut
- Border is visible but partially cropped (overscan)
- Phosphor decay provides natural motion smoothing
- 50 Hz refresh is at the edge of flicker perception but acceptable

All other display types introduce some deviation from this reference. Emulators with CRT shaders come closest; pixel-perfect modern LCDs are the most accurate in pixel terms but the least accurate in motion behavior.

---

## Cross-References

- [Video output hardware](../../03_io/peripherals/video_output.md) — connectors, cables, modulators, encoders
- [Interlace and flicker](interlace_and_flicker.md) — perception physics, CRT vs LCD
- [Video frame overview](video_frame_overview.md) — PAL fundamentals and ULA frame cycle
- [Color system](color_system.md) — the 15-color palette, BRIGHT, FLASH, color clash
- [Border effects](border_effects.md) — practical raster bar and timing code
- [Clone video modes](clone_video_modes.md) — GigaScreen, hires, multicolor
- [Video frame comparison](video_frame_comparison.md) — per-model timing comparison

---

## Primary Sources

- [Chris Smith, The ZX Spectrum ULA: How to Design a Microcomputer](http://www.zxdesign.info/) — documents the ULA's pixel pipeline and the analog output stages.
- **ZX Spectrum 128K / +2 / +2A / +3 Service Manuals** (Amstrad/Sinclair, 1986-1990) — official documentation of the video output stages, signal levels, and recommended monitor types.
- **Poynton, *Digital Video and HD: Algorithms and Interfaces*** — pixel aspect ratio mathematics for PAL and other broadcast standards.
- **OSSC documentation** ([videogameperfection.com](https://www.videogameperfection.com)) — line multiplication modes and display compatibility.
- **RGB-to-HDMI project** ([github.com/hoglet67/RGBtoHDMI](https://github.com/hoglet67/RGBtoHDMI)) — documents Spectrum-specific display handling, including aspect ratio correction and scanline simulation.
- [World of Spectrum forums — "Monitor recommendations" threads](https://worldofspectrum.org/) — community-collected data on which CRT models work best with Spectrums, including visible-area measurements.
- **RetroGFX / CRT emulation shader documentation** — software recreation of CRT visual properties for modern displays.
