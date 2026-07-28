[← Home](../../README.md) · [Emulation](../README.md) · [MCU Emulation](README.md)

# Video Adapter on a Microcontroller

The Spectrum's video output — **composite PAL** on the 48K toastrack, **RGB** on the 128K/+2/+3 — was designed for 1980s CRT televisions and monitors. Modern displays (LCD, OLED, plasma) do not handle these signals well: composite is blurry, RGB-on-SCART is increasingly rare on TVs, and the 50 Hz refresh rate of the Spectrum conflicts with the 60 Hz native rate of many modern monitors.

A **video adapter** based on an MCU takes the Spectrum's video output (or its video memory contents) and converts it to a modern format: **VGA**, **HDMI**, or **DVI**. The adapter may also perform **upscaling** (since the Spectrum's 256×192 resolution is tiny on a 1920×1080 display) and add visual enhancements like **scanlines** (to mimic the CRT look).

This article covers the design of video adapters on RP2040 and other MCUs, including VGA output, HDMI via Pico DVI, scanline generation, and upscaling algorithms. For the Spectrum's original video output, see [the video documentation](../../08_graphics/). For background on MCU video generation, see [ULA on MCU](mcu_ula.md).

---

## Why Need a Video Adapter?

### Modern Displays Don't Like Spectrum Signals

The Spectrum's video output presents several problems for modern displays:

- **Composite PAL** — the 48K Spectrum outputs composite PAL via a TV modulator. Modern displays either have no composite input or downscale it poorly (comb filters introduce artifacts, interlace is mangled, the 50 Hz refresh may not be supported)
- **RGB on SCART** — the 128K, +2, and +3 output RGB via the edge connector or a SCART cable. Modern TVs increasingly lack SCART inputs, and those that have one often treat it as composite-only
- **50 Hz refresh** — many modern monitors (especially in the US) only support 60 Hz, causing frame skipping or refusal to sync to the Spectrum's 50 Hz signal
- **Low resolution** — the Spectrum's 256×192 active pixels look tiny on a modern 1920×1080 or 4K display, requiring upscaling that the display's internal scaler may not handle well
- **CRT artifacts lost** — the characteristic CRT look (scanlines, phosphor glow, slight bloom) is lost on modern flat-panel displays

### The Adapter's Role

A video adapter solves these problems by:

1. **Receiving the Spectrum's video** — either by intercepting the video signal directly, by reading video memory (when the adapter is integrated with an [MCU-based ULA replacement](mcu_ula.md)), or by emulating the video output from scratch (in a full software emulator)
2. **Converting to a modern format** — VGA (analog RGB + TTL sync), HDMI/DVI (digital), or even DisplayPort
3. **Upscaling** the 256×192 (or 512×192 with multicolour) image to a resolution the modern display can show natively
4. **Adding optional CRT effects** — scanlines, phosphor mask, bloom, to recreate the original CRT look

---

## Video Output Options

An MCU video adapter can produce several output formats:

### Composite PAL (Recreated)

The simplest option — the MCU recreates the composite PAL signal that the Spectrum originally produced. This is what the [ULA emulation on RP2040](mcu_ula.md) does via the PIO and a resistor DAC. It works with any display that accepts composite (or with an RF modulator for true retro CRT use), but inherits all the problems of composite.

This is the "authentic but low-quality" option — useful for original CRT televisions.

### VGA

**VGA** is the most accessible modern video format. A VGA signal consists of:

- **Analog RGB** — three analog signals (R, G, B), each 0–0.7V
- **HSYNC** and **VSYNC** — TTL digital pulses (0 or 5V, ~5V active)
- **Refresh rate** — typically 60 Hz, but VGA supports 50 Hz and other rates

VGA monitors accept a wide range of resolutions and refresh rates, making it ideal for retro computing. The Spectrum's 50 Hz refresh can be supported by most VGA monitors (though some only accept 60 Hz).

The RP2040 can drive VGA output directly via its PIO — see the [PicoVGA](https://github.com/PandaHood/PicoVGA) and similar projects. A simple resistor DAC (3 resistors per colour, for 3-bit colour depth) provides the analog RGB signals, and the PIO generates HSYNC and VSYNC.

### HDMI/DVI

**HDMI** and **DVI** (which share the same video signal format, just different connectors) are the modern standard. The signal is fully digital — the video frame is encoded as a stream of pixels with explicit sync signals in the data stream.

Generating HDMI/DVI from an MCU is harder than VGA because of the high data rate (even at 640×480, the pixel clock is 25 MHz, requiring 250 Mbps per colour channel). Two approaches:

- **Bit-banged DVI** via the RP2040's PIO — demonstrated by the [Pico DVI](https://github.com/Wren6991/pico-dvi) project. The PIO shifts out DVI data at high speed, encoding TMDS via PIO state machines. This works for low resolutions (640×480, 800×600) but is at the edge of the RP2040's capabilities.
- **External HDMI encoder** — an IC like the **ADV7513** or **TFP410** takes digital pixel data (parallel or serial) and produces the HDMI signal. This offloads the high-speed encoding from the MCU.

### DisplayPort

DisplayPort is rare in MCU projects — its encoding is more complex than HDMI, and the connector licensing is different. Most MCU adapters target HDMI instead.

---
## VGA Output on RP2040

### Hardware

A simple VGA output from RP2040 requires:

- **3-bit colour per channel** (3 resistors per R/G/B = 9 resistors total) — for 512 colours (8×8×8)
- **HSYNC** and **VSYNC** — driven directly from GPIO (5V TTL, no level shifting needed for VGA)
- **VGA connector** — a standard 15-pin DSUB connector

For higher colour depth, an external DAC like the **ADV7125** (3-channel 8-bit video DAC) provides 24-bit colour (16.7M colours).

### PIO Program for VGA

The PIO program generates the video signal cycle-precisely:

1. **Pixel loop** — shifts out one pixel per clock cycle (or per two cycles for 50 Hz / 25 MHz pixel clock)
2. **HSYNC** — at end of scanline, drives HSYNC low for the sync period, then returns to blanking level
3. **VSYNC** — at end of frame, drives VSYNC low for the appropriate number of scanlines (VGA VSYNC is two lines)
4. **Pixel data** — read from a frame buffer in RAM via DMA

The PIO handles the timing precisely — the CPU only needs to keep the frame buffer updated with the latest video memory contents.

### PicoVGA Library

The [PicoVGA](https://github.com/PandaHood/PicoVGA) library by Miroslav Nemecek (and similar libraries) provides a ready-made VGA output driver for RP2040. The library:

- Defines standard VGA modes (320×240, 640×480, 800×600, etc.)
- Provides a frame buffer in RP2040 RAM
- Handles the PIO programming and DMA setup
- Supports 8-bit palettised colour (256 colours) or 4-bit (16 colours)
- Includes primitives for drawing pixels, lines, rectangles, text

Using PicoVGA, a video adapter is straightforward:

1. Initialise the library with the desired VGA mode (e.g., 640×480 at 60 Hz)
2. In the main loop, read the Spectrum's video memory (or receive it via SPI/UART)
3. Convert each Spectrum pixel to the palette
4. Update the PicoVGA frame buffer
5. The library handles output

### VGA Timing

VGA uses specific timing per mode. For 640×480 at 60 Hz:

- **Pixel clock** — 25.175 MHz (often approximated as 25 MHz)
- **HSYNC** — 96 pixels low (3.8 µs), then 16 pixels back porch, 480 pixels active, 16 pixels front porch = 640 total
- **Total scanline** — 800 pixels (31.77 µs)
- **VSYNC** — 2 lines low, then 33 lines back porch, 480 lines active, 10 lines front porch = 525 total
- **Frame rate** — exactly 59.94 Hz (close to 60 Hz)

For 50 Hz operation (matching the Spectrum), a custom VGA mode is needed — e.g., 800×600 at 56 Hz or a custom mode like 640×480 at 50 Hz. Most VGA monitors accept these custom modes.

---

## HDMI Output via Pico DVI

### The Pico DVI Project

The [Pico DVI](https://github.com/Wren6991/pico-dvi) project by Luke Wren demonstrates that the RP2040 can generate DVI signals via its PIO. The approach:

1. **Three TMDS channels** — DVI/HDMI uses three Transition Minimised Differential Signalling (TMDS) channels for R, G, B (plus a fourth for clock)
2. **PIO shifts out TMDS** — three PIO state machines, one per TMDS channel, shift out the 10-bit TMDS symbols at the pixel clock rate (typically 25 MHz for 640×480)
3. **External circuit** — three pairs of GPIO pins (differential), with a simple resistor network to provide the 100-ohm differential impedance

The Pico DVI library provides a frame buffer and handles the TMDS encoding (which is non-trivial — each 8-bit pixel value is mapped to a 10-bit TMDS symbol that minimises transitions).

### Limitations

The Pico DVI approach has limits:

- **Maximum resolution** — about 640×480 at 60 Hz or 800×600 at 60 Hz. Higher resolutions require too much bandwidth for the RP2040's PIO.
- **Memory bandwidth** — the RP2040's RAM is small (264 KB), and the frame buffer plus the Z80 emulator's working memory can be tight at higher resolutions.
- **Audio** — HDMI supports audio, but Pico DVI typically does not (the PIO is fully occupied with video). An external HDMI encoder (ADV7513) would add audio.

### External HDMI Encoder

For higher resolutions or audio support, an external HDMI encoder like the **ADV7513** is used. The MCU provides parallel pixel data (16-bit or 24-bit) and the encoder produces the HDMI signal. This offloads the high-speed encoding from the MCU.

The ADV7513 is more expensive (~£10) than the RP2040 (~£1), but provides:

- Up to 1920×1080 at 60 Hz (1080p)
- Audio support (I2S from the MCU)
- HDCP support (not useful for retro computing, but included)
- Standard HDMI connector

---
## Upscaling

The Spectrum's video memory produces a 256×192 image (or 512×192 in multicolour effects). Modern displays want at least 640×480, and often 1280×720 or 1920×1080. The adapter must upscale the Spectrum's image.

### Nearest Neighbour (Integer Scaling)

The simplest upscaling is **integer scaling** — each Spectrum pixel becomes a 2×2, 3×3, or 4×4 block in the output. For example, scaling 256×192 to 768×576 is a 3× scale (each pixel becomes a 3×3 block).

Advantages:

- **Fast** — no calculation, just memory copy with stride
- **Sharp pixels** — preserves the pixel-art look
- **No artefacts** — pixels remain crisp, no smoothing

Disadvantages:

- **Blocky** — the pixels are very visible at high scale factors
- **May not fit standard resolutions** — 256×192 × 3 = 768×576, which doesn't fit 640×480 or 1280×720 exactly

Integer scaling is the most common approach in retro computing — it preserves the original pixel art without distortion.

### Bilinear Filtering

**Bilinear filtering** smooths the upscaled image by blending neighbouring pixels. This produces a softer, less pixelated look, but destroys the sharp pixel art aesthetic.

Bilinear filtering is rarely used for retro video adapters — it makes the image look blurry rather than enhanced.

### Scanline Interpolation (CRT Emulation)

A more authentic upscaling keeps the pixel art but adds **scanlines** — dark horizontal lines between pixel rows, mimicking the CRT phosphor mask. The result is a 256×384 image (alternating pixel rows and scanline rows), then scaled to the final resolution.

### Integer Scaling with Aspect Ratio Correction

The Spectrum's pixels are not square — they are wider than they are tall (a 256×192 image has an aspect ratio of 4:3, not 16:9). To preserve the correct aspect ratio, the adapter should scale non-uniformly:

- **Horizontal scale** — 256 × N pixels (e.g., 256 × 3 = 768)
- **Vertical scale** — 192 × M pixels, where M is chosen to maintain 4:3 (e.g., 192 × 2.25 = 432, which means non-integer scaling is needed)

Integer scaling often cannot preserve the exact 4:3 aspect ratio. The adapter must choose between:

- **Square pixels at wrong aspect ratio** (e.g., 256×192 scaled 3×3 = 768×576, aspect ratio 4:3)
- **Non-integer vertical scaling** to maintain aspect ratio
- **Letterboxing** (black bars top and bottom) to preserve both

Most retro adapters use the first approach — slight aspect ratio distortion is acceptable for most software.

---

## Scanline Generation

The classic CRT look includes **scanlines** — dark horizontal lines between the visible pixel rows. This is a side effect of how CRTs work (the electron beam scans horizontally, leaving a gap between scans).

### Scanline Effect

A scanline effect darkens every other (or every third) row of pixels:

```c
// Pseudocode for scanline generation
void apply_scanlines(uint16_t *framebuffer, int width, int height) {
    for (int y = 0; y < height; y += 2) {
        for (int x = 0; x < width; x++) {
            // Darken every other line by 50%
            uint16_t pixel = framebuffer[y * width + x];
            uint8_t r = (pixel >> 11) & 0x1F;
            uint8_t g = (pixel >> 5) & 0x3F;
            uint8_t b = pixel & 0x1F;
            framebuffer[y * width + x] = 
                ((r / 2) << 11) | ((g / 2) << 5) | (b / 2);
        }
    }
}
```

The strength of the scanline effect can be configured — 50% darkening is strong, 25% is subtle.

### Phosphor Mask

A more advanced CRT effect adds a **phosphor mask** — vertical stripes of colour subpixels, mimicking the shadow mask of a colour CRT. This is more computationally intensive and is rarely implemented in MCU video adapters (more common in software emulators).

### Bloom and Glow

Real CRTs have slight **bloom** — bright pixels "glow" and bleed into neighbouring pixels. This is simulated with a small blur filter (e.g., 3×3 box blur) applied selectively to bright pixels. This is rarely implemented in MCU adapters due to the computational cost.

---

## Receiving the Spectrum's Video

The adapter must get the video data from the Spectrum. Several methods:

### Intercepting the Video Signal

For an adapter connected to the Spectrum's video output (composite or RGB), the adapter digitises the analog signal:

- An **ADC** (analog-to-digital converter) samples the video signal at the pixel rate
- The MCU processes the samples, reconstructing the digital pixel data
- The data is then upscaled and output in the modern format

This is essentially a **scan converter** and is complex. Few MCU projects take this approach — most use the alternatives below.

### Reading Video Memory

For an adapter integrated with an [MCU-based ULA replacement](mcu_ula.md), the video memory is already in the MCU's RAM. The adapter just reads it directly and renders it. This is the simplest approach and is how most "Pico Spectrum" projects work.

### Frame Grabber

For an adapter connected via a fast interface (SPI, parallel), the host Spectrum sends its video memory contents to the adapter periodically. The adapter buffers the data and renders it.

### Software Emulation

For a [software emulator](../software/) running on the MCU (e.g., a Pico running a Z80 emulator plus ULA emulator), the video memory is in the emulator's RAM. The video output is generated from this internal memory.

---
## Existing Projects

### PicoVGA

The **PicoVGA** library by Miroslav Nemecek is a comprehensive VGA output library for RP2040. While not Spectrum-specific, it is the basis for many Spectrum-on-Pico projects. It provides a frame buffer, multiple video modes, and an easy API.

### Pico DVI

The **Pico DVI** project by Luke Wren demonstrates DVI output from RP2040. Combined with a Spectrum emulator (or ULA emulator), this gives HDMI output from a £1 MCU.

### RGB-to-HDMI

The **RGB-to-HDMI** project (by Ian Stocks and David Banks) is a different approach — it uses a Raspberry Pi Zero (not RP2040) to digitise the analog RGB output from a retro computer and re-emit it as HDMI. While not RP2040-based, the same concept applies: the Pi acts as a scan converter.

A version using RP2040 has also been developed — the **Pi Pico RGB-to-HDMI** project uses the RP2040's PIO to sample the digital video signal and re-emit it as HDMI.

### Spectrum-Specific Video Adapters

Several Spectrum-specific video adapters exist, both commercial and open-source:

- **Retroleum SMARTi** — an expansion port adapter that provides VGA output from a 48K Spectrum
- **ZX-HD** — HDMI output adapter for the 48K and 128K Spectrum
- **Spectra** — video interface providing RGB and other outputs

These typically use a small FPGA or fast MCU to sample the video and re-emit it in a modern format.

---

## Comparison of Output Formats

| Format | Cost | Difficulty | Quality | Best For |
|---|---|---|---|---|
| Composite PAL (recreated) | ~£1 (RP2040 + resistors) | Medium | Low (blurry) | Original CRT TVs |
| VGA (resistor DAC) | ~£1 (RP2040 + 9 resistors) | Easy | Good (sharp pixels) | VGA monitors, modern displays with VGA |
| VGA (ADV7125 DAC) | ~£5 (RP2040 + ADV7125) | Medium | High (24-bit colour) | High-quality VGA |
| HDMI (Pico DVI) | ~£2 (RP2040 + resistors) | Hard | High | Modern HDMI displays |
| HDMI (ADV7513) | ~£12 (RP2040 + ADV7513) | Medium | High | Modern HDMI displays with audio |
| RGB-to-HDMI (Pi Zero) | ~£15 (Pi Zero + addon) | Medium | Very high | Best quality conversion |

For most hobbyists, VGA via resistor DAC is the simplest and cheapest option that produces good results. HDMI via Pico DVI is the modern choice for displays without VGA inputs.

---

## Integration with Original Hardware

### External Adapter

The most common integration is an **external adapter** — a small box that takes the Spectrum's video output (composite or RGB) and converts it to VGA or HDMI. The adapter connects via:

- **Composite video cable** — simple but lowest quality
- **RGB cable** (from the edge connector) — better quality, requires a custom cable
- **Edge connector** — direct digital access to video memory (no analog stage)

The external adapter is non-invasive and works with any Spectrum.

### Integrated Adapter

For an MCU-based Spectrum (Pico Spectrum, Harlequin, etc.), the video output is generated by the MCU and there is no need for an external adapter. The video output circuit (resistor DAC for VGA, or Pico DVI circuit for HDMI) is built into the main board.

This is the most elegant solution but requires the whole Spectrum to be implemented on the MCU.

---

## FAQ

### What's the minimum resolution I should target?

For a usable Spectrum display, **640×480** is the minimum. This allows a 2× scale of the Spectrum's 256×192 (with some letterboxing). 800×600 or 1024×768 is preferred for a more comfortable display.

For pixel-perfect integer scaling, **768×576** (3× scale) is ideal — but this is a non-standard VGA mode that some monitors may not support.

### Can I add audio to HDMI?

Yes, but only with an external HDMI encoder like the ADV7513. The Pico DVI approach uses all available PIO for video, leaving no bandwidth for audio.

The ADV7513 accepts I2S audio from the MCU (or from the [AY-3-8912 emulator](mcu_psg_ay.md)) and embeds it in the HDMI signal.

### Why does my monitor refuse to sync at 50 Hz?

Many modern monitors (especially in the US) are designed for 60 Hz minimum and do not support 50 Hz. Solutions:

- Use a monitor that supports 50 Hz (most European monitors do)
- Output at 60 Hz and accept a slight speedup (games run 20% faster)
- Output at 60 Hz with frame interpolation (the MCU generates 60 frames per second, duplicating every 5th frame from the Spectrum's 50 Hz output)

### How do I handle attribute clash?

The Spectrum's attribute clash (where two colours in the same 8×8 attribute block conflict) is a fundamental property of the original hardware. The video adapter should preserve it — attempting to "fix" attribute clash would make the image non-authentic.

If the user wants to reduce attribute clash, they should use Spectrum software designed for hi-res modes (like the **Timex HiColor** mode or software-specific enhancements).

### Can I capture video frames for screenshots?

Yes — the MCU can write the frame buffer to an SD card ([SD interface on MCU](mcu_sd_interface.md)) as a PNG or BMP file. This is useful for documentation, demos, and sharing.

### How fast is the video output?

The RP2040 generates video in real time, with no perceptible latency. The frame buffer is updated as the Spectrum writes to video memory, and the PIO outputs pixels at the pixel clock rate.

For external HDMI encoders, there may be 1-2 frames of latency due to the encoder's internal buffering. This is usually not noticeable but can be problematic for time-critical applications.

---

## Summary

An MCU video adapter for the Spectrum performs these functions:

1. **Receives the Spectrum's video** — from video memory (integrated adapter), from the video signal (scan converter), or from an emulator's internal state
2. **Upscales** the 256×192 (or higher) image to a modern resolution (640×480, 800×600, 1280×720, etc.)
3. **Generates the output signal** — VGA via resistor DAC, HDMI via Pico DVI or external encoder, or composite PAL for CRT use
4. **Optionally adds CRT effects** — scanlines, phosphor mask, bloom
5. **Handles aspect ratio** — preserves the 4:3 aspect ratio (with possible letterboxing) or accepts slight distortion

The RP2040 is again the optimal MCU choice, due to its PIO for cycle-precise video generation and its ability to drive VGA, DVI, or external encoders. The PicoVGA library provides a ready-made VGA output, and the Pico DVI project provides HDMI.

For most users, VGA via resistor DAC is the cheapest option (~£1) and works with any VGA monitor. HDMI via Pico DVI is the modern choice, costing ~£2 and working with any HDMI display.

---

## References

- **PicoVGA** by Miroslav Nemecek — VGA output library for RP2040 (GitHub)
- **Pico DVI** by Luke Wren — DVI output from RP2040 via PIO (GitHub)
- **RGB-to-HDMI** project — scan converter using Raspberry Pi (project wiki)
- **ADV7513 datasheet** — Analog Devices HDMI encoder
- **ADV7125 datasheet** — Analog Devices triple video DAC
- **VGA timing documentation** — widely available, e.g., TinyVGA
- **DVI specification** — for TMDS encoding details
- **RP2040 datasheet** — for PIO programming
- **Retroleum SMARTi, ZX-HD, Spectra** — Spectrum-specific video adapters
- **Chris Smith's *The ZX Spectrum ULA*** — for the Spectrum's video timing

## Cross-References

- [ULA on MCU](mcu_ula.md) — the ULA emulator generates the video memory that this adapter outputs
- [Keyboard on MCU](mcu_keyboard.md) — often combined with video adapter in a multi-function expansion port device
- [SD interface on MCU](mcu_sd_interface.md) — for screenshot capture and disk images
- [N-Go](n_go.md) — a complete MCU-based Spectrum including video output
- [MCU design patterns](mcu_design_patterns.md) — general techniques for high-speed I/O
- [FPGA implementation](../fpga/fpga_implementation.md) — alternative approach using FPGA for video generation
