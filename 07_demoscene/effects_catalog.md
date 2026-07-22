[← Home](../README.md) · [Demoscene](README.md)

# Visual Effects Catalog

> **Scope**: This article is a comprehensive technical catalog of the **visual effects** used in ZX Spectrum demoscene work, with implementation notes, T-state cost estimates, and known limitations for each. It is the practical companion to [multicolor_techniques.md](multicolor_techniques.md) (the raster-timing foundation most effects rely on), [precalc_trigonometry.md](precalc_trigonometry.md) (the math tables most effects consume), and [demo_frameworks.md](demo_frameworks.md) (how effects are sequenced into a multi-part demo).
>
> The catalog is descriptive rather than tutorial-style: each effect gets a section explaining what it looks like, how it works at the algorithmic level, what the per-frame cost is on stock Spectrum hardware, and what the variant forms are. Source code for each effect is not included; refer to the source releases of the demos cited in [notable_demos.md](notable_demos.md) for working implementations.

---

## 1. Why a Catalog

Spectrum demos, like demos on any platform, are built from a relatively small set of **reusable visual effects**: plasma, tunnel, raster bars, starfield, twister, and so on. New demos combine these effects in new sequences, with new palettes and new music — but the underlying techniques are shared. A scener who has implemented plasma once can implement it again, in any demo, in a few hundred lines of code.

This catalog exists because:

1. **Each effect has a known cost** in CPU time, memory, and development effort. Knowing the cost helps a designer decide what to put in a demo with a fixed time budget.
2. **Each effect has a "state of the art"** — a specific implementation technique that is currently the fastest, the highest-quality, or the most flexible version. Knowing the state of the art prevents sceners from reinventing inferior versions.
3. **Each effect has a history** — a first appearance, a peak sophistication, and (sometimes) a decline as sceners move on to other techniques. Knowing the history places a demo in context.
4. **Cross-references between effects matter**: plasma and tunnel share math, twister and 3D wireframe share projection, raster bars and copper bars share timing tricks. The catalog makes these connections visible.

### Article Roadmap

- §2 — Effect taxonomy: how to classify effects along axes (per-frame cost, attribute use, dimension).
- §3 — Plasma: the canonical "first effect" every scener implements.
- §4 — Zoomers and rotazers: scaling and rotating a static image.
- §5 — Starfields: 2D and 3D star projections.
- §6 — Raster bars and copper bars: border timing tricks.
- §7 — Twisters: perspective tricks with rotating rectangles.
- §8 — Tunnels: polar-coordinate texture mapping.
- §9 — Raycasting and voxel: pseudo-3D environments.
- §10 — 3D wireframe and filled polygons.
- §11 — Particles, fire, wobblers, vector scroll, demoscene texts.
- §12 — Cost matrix: a single table comparing all effects.
- §13 — Cross-references.

---

## 2. Effect Taxonomy

Spectrum demoscene effects can be classified along several axes. Each axis affects the implementation strategy:

### 2.1 By output dimensionality

| Class | Examples | Cost |
|---|---|---|
| **2D pure** | Plasma, raster bars, zoomers, twisters, copper bars | Low–moderate |
| **2.5D (pseudo-3D)** | Tunnel, raycasting, voxel landscape, mode-7-style floor | Moderate–high |
| **3D true** | Wireframe objects, filled polygons, gouraud shading | High–very high |

True 3D is the most expensive category because every vertex must be transformed through a rotation matrix (see [precalc_trigonometry.md](precalc_trigonometry.md) §6) before projection. 2.5D effects fake 3D using precomputed tables.

### 2.2 By attribute strategy

| Strategy | Examples | Notes |
|---|---|---|
| **Static attributes** | Twisters (mostly), starfields, simple 3D wireframe | Colours set once at start, only pixel data updates |
| **Per-frame attribute writes (no multicolor)** | Plasma (some), copper bars | Whole cells change colour between frames but not within a frame |
| **8×2 multicolor** | Zoomers, simple plasma, basic twisters | Cell colour changes every 2 scanlines |
| **8×1 multicolor** | Tunnel, high-end plasma, raycasting | Cell colour changes every scanline |
| **8×1 gigascreen** | Static art, disk-streamed "video" | Alternates two 8×1 frames for ~100 perceived colours |

Higher-resolution attribute strategies cost more CPU time but produce visibly better images. The progression from "static attributes" to "8×1 gigascreen" roughly tracks the historical development of Spectrum demoscene art (see [demoscene_history.md](demoscene_history.md)).

### 2.3 By per-frame cost

Cost categories at 50 Hz on a stock 128K Pentagon:

| Category | T-states per frame | CPU % | Examples |
|---|---|---|---|
| **Trivial** | < 5,000 | < 7% | Static screens, scroll text |
| **Cheap** | 5,000–20,000 | 7%–28% | Raster bars, simple starfield, simple plasma |
| **Moderate** | 20,000–50,000 | 28%–71% | Zoomers, twisters, basic 3D wireframe, multicolor plasma |
| **Expensive** | 50,000–69,000 | 71%–98% | Tunnel, raycasting, 3D filled polygons |
| **Frame-bound** | 69,000+ | 100%+ (needs 25 Hz or precompute) | Full-screen 8×1 multicolor plasma, complex voxel landscape |

The cost is dominated by **memory writes** (pixel or attribute bytes) and **multiplication** (8×8 → 16-bit via the shift-and-add loop of [precalc_trigonometry.md](precalc_trigonometry.md) §5.3). Effects that minimise both — raster bars, scroll text — are cheap; effects that maximise both — full-screen multicolor with per-pixel perspective texturing — are frame-bound.

### 2.4 By memory footprint

| Category | Bytes of tables/data | Examples |
|---|---|---|
| **Tiny** (< 1 KB) | Sine table, reciprocal table | Raster bars, scroll text |
| **Small** (1–4 KB) | Sine + multiplication + reciprocal | Plasma, twister, starfield |
| **Medium** (4–16 KB) | Above + rotation matrices + bitmap font | Zoomer, raycasting |
| **Large** (16–48 KB) | Above + texture maps / precomputed distance fields | Tunnel, voxel landscape |
| **Huge** (48 KB+) | Above + multiple texture frames | Disk-streamed TS-Config video |

Memory footprint determines which effects fit in 48K, which need 128K, and which need Pentagon 1024 + disk streaming.

---

## 3. Plasma

**Plasma** is the canonical "first demoscene effect": every scener implements a plasma at some point, and almost every demo has at least one plasma part. It produces smoothly morphing colour fields that look like clouds, waves, or interference patterns. On the Spectrum, plasma is almost always implemented as a **per-cell attribute animation**, optionally enhanced with 8×1 or 8×2 multicolor for higher detail.

### 3.1 What it looks like

A plasma displays smoothly-varying colours across the screen, with the colour pattern morphing over time. The colour of each cell is a function `f(x, y, t)` of the cell's position `(x, y)` and the time parameter `t`. The function is designed to produce **smooth, organic-looking** variations rather than sharp edges.

### 3.2 The basic algorithm

The classic plasma function is a sum of sine waves:

```
f(x, y, t) = sin(x / a + t)        // horizontal wave
           + sin(y / b + t * 1.3)   // vertical wave
           + sin((x + y) / c + t * 0.7)   // diagonal
           + sin(sqrt(x² + y²) / d + t * 2.0)   // radial
```

The output `f` is mapped to an attribute byte via a **colour lookup table** (`LUT`). The LUT is chosen by the artist to produce a pleasing palette cycle — typically a smooth ramp through several colours.

### 3.3 The Spectrum implementation

On the Spectrum, the plasma function is evaluated **per cell** (768 cells), not per pixel. Each frame:

1. For each cell `(x, y)` in the 32×24 grid, compute `f(x, y, t)`.
2. Look up `f` in the LUT to get an attribute byte.
3. Write the attribute byte to `#5800 + (y << 5) + x`.

The arithmetic is dominated by sine lookups: each cell needs 4 sine evaluations. With 768 cells × 4 sines = 3072 lookups per frame, at 7 T-states per `LD A,(HL)` lookup = ~21,000 T-states just for the sine reads. Add additions, the LUT lookup, and the attribute write, and the per-frame cost is **~35,000–50,000 T-states**.

### 3.4 Optimisation: precomputed (x,y)→sine-index

The x- and y-dependent parts of the plasma function don't change from frame to frame (only `t` does). A common optimisation is to **precompute** a table of `sin(x / a)` for each column, `sin(y / b)` for each row, and combine them at runtime. This reduces the per-cell work to ~3 additions plus one sine-of-distance lookup, dropping the cost to **~20,000–30,000 T-states per frame** — comfortably within the 50 Hz frame budget.

### 3.5 Multicolor plasma

For higher detail, the plasma can be evaluated at 8×2 or 8×1 resolution. This multiplies the cell count by 4 or 8 respectively. Multicolor plasma is the most demanding common plasma variant; full-screen 8×1 plasma typically requires running at 25 Hz (every other frame) on a 128K Spectrum, or fits in 50 Hz only on a contention-free Pentagon.

### 3.6 Variants

- **Interference plasma**: f is the sum of two radial sines whose centres drift over time, producing characteristic two-centre interference patterns.
- **Distance plasma**: f depends only on `sqrt(x² + y²)` from a moving centre, producing expanding/contracting rings.
- **Mandeltunnel-adjacent plasma**: f is computed from a precomputed distance-to-Mandelbrot-boundary table, producing fractal-adjacent patterns.
- **Pixel-level plasma**: rare and very expensive; plasma computed per pixel rather than per cell. Uses a precomputed full-screen 6 KB LUT.

### 3.7 Cost summary

| Variant | Per-frame cost | Resolution | Notes |
|---|---|---|---|
| 8×8 attribute plasma | ~30,000 T | 32×24 colour cells | The "default" plasma; runs on any Spectrum |
| 8×2 multicolor plasma | ~80,000 T | 32×96 colour cells | Needs Pentagon or 25 Hz frame rate |
| 8×1 multicolor plasma | ~150,000 T | 32×192 colour cells | 25 Hz, Pentagon-class hardware |
| Pixel-level plasma | ~250,000 T | 256×192 | 12.5 Hz, requires precomputed LUT |

### 3.8 History

Plasma was among the first demoscene effects on the Spectrum, appearing in early demos around 1991–1993. The "modern" multicolor plasma emerged in Soviet work around 1996–1998 (Extreme, E-Mage) and has been a staple ever since. By 2025, plasma is a "warm-up" effect — sceners implement it first when building a new engine, then move on to more demanding effects.

---

## 4. Zoomers and Rotazers

A **zoomer** continuously scales an image up or down; a **rotaazer** (rotazer, rotator) continuously rotates it. The two are often combined into a **zoomer-rotaazer** that scales and rotates simultaneously. On the Spectrum, these effects display a static piece of art (typically a multicolor image) and transform it in real time.

### 4.1 What it looks like

A zoomer appears as the camera "flying into" or "pulling back from" the image; a rotaazer spins the image around its centre. The image is usually a multicolor still, so the effect is one of the most common ways to display a scener's pixel art in motion.

### 4.2 The algorithm

The transform is inverse-mapped: for each output pixel (or cell) on the screen, compute the corresponding **source coordinate** in the original image:

```
Zoom only:
    sx = (ox - cx) / zoom + cx
    sy = (oy - cy) / zoom + cy

Zoom + rotate:
    dx = ox - cx
    dy = oy - cy
    sx = cx + (dx * cos(theta) + dy * sin(theta)) / zoom
    sy = cy + (-dx * sin(theta) + dy * cos(theta)) / zoom
```

Here `(ox, oy)` is the output coordinate, `(sx, sy)` is the source coordinate, `(cx, cy)` is the centre of transformation, `zoom` is the scale factor, and `theta` is the rotation angle. The source coordinate is then looked up in the original image to get the output pixel.

### 4.3 The Spectrum implementation

On the Spectrum, zoomers/rotaazers are computed **per cell** (32×24 cells), not per pixel, with the attribute byte for each cell looked up from a pre-multicolored source image. The per-cell work is:

- One sine and one cosine lookup (for rotaazer)
- Two multiplications (the rotation, using the 8×8 multiply from [precalc_trigonometry.md](precalc_trigonometry.md) §5.3)
- One division by `zoom` (via a reciprocal table)
- One address calculation in the source image
- One attribute write

Per-cell cost: ~150–250 T-states. Per frame: 768 cells × ~200 T = **~150,000 T-states**. This is at the upper limit of 50 Hz; most zoomer-rotaazers run at 25 Hz (alternate frames).

### 4.4 Pixel-level zooming

Pixel-level (true per-pixel) zooming is much rarer because the per-pixel cost is ~6 KB of source lookups per frame, plus the same transform math applied 6144 times instead of 768. Pixel-level zooming exists in a handful of demos and usually sacrifices frame rate (10 Hz or slower) for visual quality.

### 4.5 Cost summary

| Variant | Per-frame cost | Resolution | Notes |
|---|---|---|---|
| Cell-level zoom | ~80,000 T | 32×24 cells | Cheap; runs at 50 Hz easily |
| Cell-level zoom+rotate | ~150,000 T | 32×24 cells | 25–50 Hz depending on optimisation |
| Pixel-level zoom | ~250,000 T | 256×192 | 12.5 Hz; rare |

---

## 5. Starfields

A **starfield** displays a moving field of point sources ("stars"), giving the impression of flying through space. Starfields are typically 2D (stars scroll sideways or fly outward from a centre point) or 3D (stars have depth and project to the screen as the camera moves).

### 5.1 What it looks like

A 2D starfield has stars moving in a single direction (typically left-to-right or outward from centre). A 3D starfield has stars with varying depths; closer stars appear to move faster (parallax), and stars ahead of the camera appear to fly outward from the vanishing point.

### 5.2 2D starfield

Each star has `(x, y, speed)`. Each frame:

- `x -= speed` (or `x += speed` for outward motion).
- If `x` goes off-screen, respawn at the opposite edge with a new random `y`.
- Plot the star at `(x, y)`.

Per-frame cost: ~50 stars × ~30 T per star (clear old pixel, plot new pixel, update x) = ~1,500 T-states. **Trivial.** 2D starfields are commonly used as filler between more expensive parts.

### 5.3 3D starfield

Each star has `(x, y, z)`. The camera looks down the +z axis. Each frame:

- `z -= speed` (move star closer).
- If `z <= 0`, respawn the star at large `z` with new random `(x, y)`.
- Project to screen: `screen_x = x * focal / z + screen_cx`, `screen_y = y * focal / z + screen_cy`.
- Plot at `(screen_x, screen_y)`.

Per-frame cost: ~100 stars × ~200 T per star (clear old, compute new x/y/z, project with one multiplication and one division, plot new) = ~20,000 T-states. **Cheap.** 3D starfields are a standard demoscene effect and combine well with 3D wireframe objects in "spaceship" sequences.

### 5.4 Variants

- **Hyperspace**: stars leave brief trails behind them as they fly outward, simulating faster-than-light travel. Adds ~30 T per star for the trail plot.
- **Streak starfield**: stars are drawn as short lines (one end at the previous position, other end at the new position) instead of single pixels. Adds ~50 T per star for the line draw.
- **Tunnel starfield**: stars fly outward from a single centre point rather than from a vanishing point at infinity. Visually similar to a tunnel effect (§8) but cheaper.

### 5.5 Cost summary

| Variant | Per-frame cost | Notes |
|---|---|---|
| 2D starfield (50 stars) | ~1,500 T | Trivial; used as filler |
| 3D starfield (100 stars) | ~20,000 T | Standard |
| 3D hyperspace (100 stars, trails) | ~30,000 T | Still cheap; very common |
| 3D streak (100 stars, line plots) | ~40,000 T | More expensive; visually striking |

### 5.6 History

Starfields are one of the oldest demoscene effects, predating the Spectrum itself (they appear in 1980s C64 and Atari demos). On the Spectrum, 2D starfields were common from 1990; 3D starfields became standard from ~1993. By 2025, starfields are considered a beginner effect — included for nostalgia but rarely the highlight of a demo.

---

## 6. Raster Bars and Copper Bars

**Raster bars** are horizontal stripes of colour drawn synchronously with the CRT beam, traditionally in the **border area** (which has no attribute RAM and can only be coloured by writing to port `#FE` mid-scanline). On the Amiga, the equivalent effect (using the Copper co-processor) is called **copper bars**; the term has been borrowed by the Spectrum scene even though no co-processor is involved.

### 6.1 What it looks like

A raster-bar effect fills the screen (and usually the border) with smoothly-coloured horizontal stripes — typically gradients from one colour to another and back, animated to scroll vertically or "wave" across the screen. The classic look is multiple coloured bars scrolling past each other, producing an effect similar to a lava lamp or aurora.

### 6.2 The border-colour register

The Spectrum's only way to colour the border is port `#FE` (the same port that controls the speaker and the Mic/Ear edge). Bits 0–2 of the value written set the border colour (8 colours; no `BRIGHT` bit). To produce per-scanline border colour changes, the code must write a new value to `#FE` on every scanline.

```z80
; Raster-bar scanline loop (simplified)
    LD   A,(HL)         ; new colour from table
    OUT  (#FE),A        ; set border colour
    INC  HL
    ; ... waste time until next scanline ...
    ; ... repeat for 311 scanlines ...
```

### 6.3 Spectrum raster bars in the paper area

Beyond the border, raster-bar effects often colour the paper area too. There are two approaches:

- **Attribute-only raster bars**: write one attribute byte per scanline to a fixed column (e.g. cell (0, current_scanline)), with the rest of the screen black. The visible effect is a vertical stripe of changing colours.
- **Full-screen attribute bars**: write attribute bytes for a whole row of cells at a specific scanline, colouring that row's cells with the same colour as the border. This requires multicolor-style timing discipline (see [multicolor_techniques.md](multicolor_techniques.md) §3–§4).

### 6.4 Cost

Raster bars are one of the **cheapest** demoscene effects:

- Border-only bars: ~50 T per scanline × 311 scanlines = ~15,500 T-states per frame. Runs at 50 Hz on any Spectrum.
- Full-screen bars (attribute writes for one row per scanline): ~150 T per scanline × 192 paper scanlines = ~28,800 T-states. Still cheap.

The hard part is not the cost but the **timing precision** — every `OUT (#FE),A` must be at the same offset within the scanline, or the bars wobble. See [multicolor_techniques.md](multicolor_techniques.md) §5 for raster sync.

### 6.5 Variants

- **Moving copper bars**: the colour gradient is shifted up or down each frame, producing the illusion of motion.
- **Waving bars**: the gradient's phase varies sinusoidally across columns, producing bars that undulate horizontally.
- **Attr-attr bars**: bars drawn by alternating attributes (gigascreen) instead of solid colours, doubling perceived colour depth.
- **Combined bars + image**: a static image (logo, greeting) is drawn in the centre of the screen with raster bars surrounding it.

### 6.6 History

Raster bars are another ancient demoscene effect, originating on the C64 (which has a hardware raster interrupt). On the Spectrum, they were a staple of the 1987–1992 cracktro/demoscene era and remain a nostalgic favourite. They are commonly the *first* effect a new Spectrum scener implements because the basic version is achievable in under 100 lines of code.

---

## 7. Twisters

A **twister** is an effect that displays a rotating bar or column with a 3D-rotating appearance, achieved through 2D tricks. The classic twister shows a vertical bar whose horizontal width and texture vary sinusoidally down its length, producing the illusion of a bar twisting around its vertical axis.

### 7.1 What it looks like

A twister is a vertical or horizontal "bar" that appears to rotate. The bar's width at each scanline is determined by a sine wave, and the bar's colour/texture shifts as it rotates. Multiple parallel bars may rotate in synchronisation, producing a striped column.

### 7.2 The algorithm

The twister does not actually rotate anything in 3D. Instead, for each scanline, the **width of the bar** is computed from a sine:

```
width(y, t) = max_width * |sin(y * frequency + t * speed)|
```

The bar is drawn at horizontal positions `[cx - width/2, cx + width/2]` where `cx` is the bar's centre. As `width` varies down the screen, the bar appears to twist.

To enhance the 3D illusion, the bar is often split into a **front half** and **back half**, with the back half dimmer (or with `BRIGHT=0`) to simulate depth. When `width` is near zero, only a thin line shows; when `width` is maximal, the full bar fills its slot.

### 7.3 Spectrum implementation

On the Spectrum, a twister is typically drawn as **attribute cells** rather than pixels. For each scanline (or each pair of scanlines), the engine:

1. Computes `width(y, t)` from a sine lookup.
2. Determines which cells fall within `[cx - width/2, cx + width/2]`.
3. Writes attribute bytes for those cells (front colour for front half, back colour for back half).
4. Writes background colour for cells outside the bar.

Per-scanline cost: ~100 T. Per frame (192 scanlines): ~20,000 T-states. **Cheap.**

### 7.4 Pixel-level twisters

Pixel-level twisters compute the bar edges at per-pixel resolution. This produces smoother edges but costs ~6 KB of pixel writes per frame. With careful coding, a pixel-level twister can run at 25 Hz on a 128K Spectrum.

### 7.5 Variants

- **Horizontal twisters**: same idea but rotated 90°, so the bar is horizontal and twists around its horizontal axis.
- **Multiple parallel twisters**: 2–4 bars side by side, rotating with phase offsets.
- **Tunnel-twister hybrid**: the bar edges follow a tunnel-like curve instead of a simple sine.
- **Twisted-rectangle twisters**: the bar has a rectangular cross-section instead of circular, producing harder-edged twisting.

### 7.6 Cost summary

| Variant | Per-frame cost | Notes |
|---|---|---|
| Attribute-only twister | ~20,000 T | Cheap; standard |
| Multicolor (8×1) twister | ~80,000 T | Smoother edges; common in modern demos |
| Pixel-level twister | ~150,000 T | 25 Hz; rare |

### 7.7 History

Twisters originated on the Amiga (which has hardware support for horizontal bar positioning via the Copper) and were ported to the Spectrum in the early 1990s. They became a standard "second-tier" effect (more impressive than starfields, less impressive than 3D) and remain common in modern demos as visually-pleasing transitions between more demanding parts.

---

## 8. Tunnels

A **tunnel** is a 2.5D effect that simulates flying through a textured tube or corridor. The viewer appears to be inside a cylindrical tunnel whose walls are covered with a repeating texture; the camera moves forward continuously, producing an effect of relentless forward motion.

### 8.1 What it looks like

The screen fills with a rectangular texture pattern that has been **polar-warped** so that the centre of the screen corresponds to "infinitely far ahead" and the edges correspond to "the walls right next to me". As the texture shifts, the viewer appears to fly forward through the tunnel. Different tunnel effects use different textures (circuit-board patterns, brick walls, organic shapes) and different camera motions (straightforward forward motion, swaying, rotating).

### 8.2 The algorithm

For each pixel (or cell) on the screen, the tunnel is rendered by computing its **polar coordinates** relative to the screen centre:

```
dx = screen_x - centre_x
dy = screen_y - centre_y
distance = sqrt(dx*dx + dy*dy)   // distance from centre
angle = atan2(dy, dx)             // angle from centre
```

These are then mapped to a **texture coordinate** in a wrapping texture:

```
u = angle * texture_width / (2 * PI)   // angle wraps horizontally
v = reciprocal(distance) * scale + time_offset   // 1/distance gives forward motion
```

The texture is read at `(u, v)` to get the output pixel.

### 8.3 The trick: precomputed distance and angle

The expensive part of the algorithm is `sqrt` and `atan2`, both of which are intractable on Z80 (no hardware divide, let alone transcendental functions). The trick is to **precompute both** as full-screen tables:

- `DISTANCE_TABLE[screen_y][screen_x]` = `reciprocal(sqrt(dx² + dy²))` for each pixel. (6144 bytes for pixel resolution; 768 bytes for cell resolution.)
- `ANGLE_TABLE[screen_y][screen_x]` = `atan2(dy, dx)` for each pixel. (Same size.)

With these tables, the per-pixel inner loop becomes:

```z80
    LD   A,(DISTANCE_TABLE_OFFSET)   ; get low byte of distance
    ADD  A, time_offset              ; add forward-motion offset
    LD   L,A
    LD   H,HIGH(TEXTURE)             ; H is constant for the texture page
    LD   A,(HL)                      ; A = texture byte
    LD   (screen_addr),A             ; plot
```

Per-pixel cost: ~30 T. Per-cell cost (using cell-resolution tables): ~60 T (including the angle computation).

### 8.4 Spectrum implementation

On the Spectrum, tunnels are usually rendered at **cell resolution** (32×24 = 768 cells), not pixel resolution, because per-pixel rendering of a 6144-byte framebuffer with table lookups is too expensive (~180,000 T-states per frame, achievable only at 25 Hz on a Pentagon). Cell-resolution tunnels cost ~30,000–50,000 T-states per frame and run at 50 Hz on stock 128K hardware.

The texture is typically an attribute-cell pattern (32×24 attribute bytes), and the tunnel maps `(distance, angle)` into this pattern. With multicolor enhancement (§3.5 of [multicolor_techniques.md](multicolor_techniques.md)), the resolution can be pushed to 8×1 (32×192 cells) at 25 Hz.

### 8.5 Variants

- **Tunnel + rotation**: the angle offset is animated, making the tunnel appear to spin around its forward axis.
- **Tunnel + swaying camera**: the centre point `(centre_x, centre_y)` moves sinusoidally over time, making the tunnel sway.
- **Two-layer tunnel**: two textures are interleaved (one in the foreground, one in the background) using distance thresholds.
- **Reflections**: a second, mirrored tunnel is composited on top of the first, simulating a wet floor or mirror.
- **Pixel-level tunnel (rare)**: full per-pixel rendering with a 6144-byte texture. Visually stunning but very expensive.

### 8.6 Cost summary

| Variant | Per-frame cost | Resolution | Notes |
|---|---|---|---|
| Cell-resolution tunnel | ~30,000 T | 32×24 cells | Standard |
| Cell-resolution tunnel + rotation/swaying | ~40,000 T | 32×24 cells | Common |
| 8×1 multicolor tunnel | ~150,000 T | 32×192 cells | 25 Hz; modern Russian style |
| Pixel-level tunnel | ~180,000 T | 256×192 | 25 Hz; rare |

### 8.7 History

The tunnel effect originated on the Amiga (Future Crew's *Second Reality* (1993) made it famous) and was ported to the Spectrum in the mid-1990s. The precomputed-table approach is universal; the only improvements over time have been in (a) the resolution (cell → 8×1 multicolor) and (b) the texture quality. Modern Russian tunnels (post-2010) are typically 8×1 multicolor with rich gigascreen palettes.

---

## 9. Raycasting and Voxel Landscapes

**Raycasting** renders a 3D-ish view from a 2D map by casting one ray per screen column and finding the wall it hits first. **Voxel landscapes** render a 3D-ish terrain by sampling a height-map along columns. Both are 2.5D techniques popularised by 1990s PC games (*Wolfenstein 3D*, *Comanche*) and adapted to the Spectrum by ambitious sceners.

### 9.1 What raycasting looks like

A Spectrum raycaster typically renders a maze of rectangular rooms from a first-person perspective. The walls are at right angles to each other (the "grid maze" constraint), and the player can move forward, backward, and turn. Each frame shows a different view of the maze; the screen is divided into a textured "wall" area (top 60–70% of the screen) and a floor/ceiling area (bottom 30–40%, often untextured for performance).

### 9.2 The algorithm

For each screen column `x` (256 columns pixel-wide, or 32 cells attribute-wide), cast a ray from the player's position in the player's facing direction plus an angular offset based on `x`:

```
ray_angle = player_angle + (x - screen_width/2) * fov / screen_width
step through the maze grid in ray_angle direction until a wall cell is hit
distance = grid distance to the wall hit
wall_height = screen_height / distance   // perspective projection
draw the wall as a vertical strip of height wall_height at column x
```

The wall's texture is sampled based on where in the wall cell the ray hit (giving a horizontal texture coordinate) and the row within the wall (giving a vertical texture coordinate).

### 9.3 The Spectrum implementation

A 32-column raycaster (one column per attribute cell) is feasible at 50 Hz on a stock 128K Spectrum. A 256-column raycaster (per-pixel horizontal resolution) is frame-bound and rare.

The per-column work:

1. Compute `ray_angle` from `player_angle` and `x` offset (~30 T).
2. Step through the maze grid using DDA (Digital Differential Analyzer) until a wall is hit (~200–500 T depending on maze).
3. Compute `distance` and `wall_height` (~50 T, with a reciprocal table).
4. Draw the wall as a vertical strip of attribute cells (~100 T).

Per-column total: ~400–700 T. Per frame: 32 columns × ~500 T = **~16,000 T-states** for the casting alone. Add the wall drawing (which scales with `wall_height`): total ~30,000 T-states per frame. **Cheap enough to run at 50 Hz.**

### 9.4 Voxel landscapes

A voxel landscape replaces the grid maze with a **height-map** (a 2D array of terrain elevations). For each screen column, cast a ray from the camera position outward, sampling the height-map at intervals. The first point on the ray whose height-map value exceeds the ray's height determines a visible terrain column; draw it as a vertical strip.

Voxel landscapes are significantly more expensive than grid-maze raycasting because the ray must step through the height-map (rather than jumping cell-by-cell through a grid). The cost is roughly **~5× higher** per column, putting voxel rendering at 25 Hz on a 128K Spectrum and 50 Hz only on a contention-free Pentagon.

### 9.5 Cost summary

| Variant | Per-frame cost | Frame rate | Notes |
|---|---|---|---|
| 32-cell grid raycaster (no texture) | ~25,000 T | 50 Hz | Simple raycaster |
| 32-cell grid raycaster (textured) | ~45,000 T | 50 Hz | Most common |
| 256-column raycaster (textured, pixel-level) | ~250,000 T | 12.5 Hz | Showpiece; rare |
| 32-cell voxel landscape | ~120,000 T | 25 Hz | Demanding |
| 256-column voxel landscape | ~500,000 T | 5–10 Hz | Showcase; very rare |

### 9.6 Variants

- **Floor and ceiling texturing**: extending the raycast to texture the floor and ceiling (not just walls). Adds ~50% to per-frame cost.
- **Sprites (enemies, items)**: drawing 2D billboards at appropriate distances in the maze. Each sprite costs ~2,000 T to draw; budget 5–10 sprites.
- **Curved walls**: abandoning the grid-maze constraint; the raycaster handles arbitrary wall angles. ~2× cost; very rare on Spectrum.
- **Reflections**: compositing a mirrored version of the view, simulating wet floors.

### 9.7 History

Raycasting came to the Spectrum in the mid-1990s, motivated by the popularity of *Wolfenstein 3D* and *Doom* on PC. Several commercial Spectrum games used it (*Wally*, *Driven*, *Rescate en el Golfo*), and the demoscene adopted it as a showpiece effect from ~1995. Voxel landscapes followed in the late 1990s, motivated by *Comanche* and *Outcast*. Both remain showpiece effects in modern demos.

---

## 10. 3D Wireframe and Filled Polygons

True **3D rendering** — transforming vertices through a rotation matrix, projecting them to 2D, and drawing lines or filled polygons between them — is one of the most demanding demoscene effects on the Spectrum. The Spectrum has no hardware multiply, no floating point, and a 3.5 MHz CPU; 3D rendering is therefore a software tour-de-force.

### 10.1 What it looks like

3D wireframe shows a rotating geometric object (cube, pyramid, icosahedron, more complex shapes) drawn as connected lines. 3D filled polygons show the same object but with each face filled with a solid colour (or an attribute cell pattern), producing a "solid" appearance. High-end filled-polygon work uses **gouraud shading** — interpolating brightness across each face to simulate a light source.

### 10.2 The pipeline

A 3D object is defined by:

- A list of **vertices** (3D coordinates in object space).
- A list of **edges** (pairs of vertex indices, for wireframe).
- A list of **faces** (closed polygons of vertex indices, for filled rendering).

Each frame:

1. **Rotate** each vertex by the current rotation angles `(ax, ay, az)` using a precomputed rotation matrix (see [precalc_trigonometry.md](precalc_trigonometry.md) §6). Cost: ~9 multiplications + 6 additions per vertex = ~200 T per vertex.
2. **Project** each rotated vertex to 2D screen coordinates using perspective projection. Cost: ~2 multiplications + 1 division = ~80 T per vertex.
3. **Wireframe**: draw lines between connected vertices using Bresenham's algorithm. Cost: ~10–30 T per pixel; a typical object has ~500–2000 visible pixels per frame.
4. **Filled**: sort faces by depth (painter's algorithm), fill each face using a scanline-fill algorithm. Cost: ~1000–3000 T per face depending on size.

### 10.3 The cost

| Object | Vertices | Faces | Per-frame cost (wireframe) | Per-frame cost (filled) |
|---|---|---|---|---|
| Cube | 8 | 6 | ~10,000 T | ~30,000 T |
| Icosahedron | 12 | 20 | ~15,000 T | ~60,000 T |
| Space shuttle (typical) | 50 | 60 | ~50,000 T | ~150,000 T |
| Complex scene (multiple objects) | 200+ | 300+ | ~200,000 T | ~500,000 T |

Wireframe runs at 50 Hz for simple objects and 25 Hz for complex ones. Filled-polygon rendering is 25 Hz for simple objects and 12.5 Hz or slower for complex ones. Modern Russian demos often combine 3D with multicolor shading, pushing the cost into the "frame-bound" category.

### 10.4 Hidden-surface removal

For filled rendering, you must hide the back-facing polygons. Two common approaches:

- **Back-face culling**: compute the normal of each face; if it points away from the camera, skip the face. Costs ~50 T per face but eliminates ~50% of the rendering work on average.
- **Painter's algorithm**: sort faces by depth (Z-coordinate of their centre) and draw them back-to-front, so nearer faces overwrite farther ones. Costs ~30 T per face for the sort, plus the cost of drawing occluded faces (wasted work).

Most engines use both: back-face culling first, then painter's algorithm on the remaining faces.

### 10.5 Gouraud shading

Gouraud shading computes a brightness value for each vertex (based on the angle between the vertex's normal and the light direction) and interpolates brightness across the face. On the Spectrum, the result is typically quantised to the 2 brightness levels (`BRIGHT=0` or `BRIGHT=1`) per attribute cell, producing a faceted look. Higher-quality gouraud uses per-cell attribute interpolation across the face, achieving ~4–6 brightness levels.

Gouraud shading adds ~50% to the per-face cost. It is the visual standard for high-end Spectrum 3D work.

### 10.6 Texture mapping

Texture mapping (UV-mapping a texture onto a face) is **extremely rare** on the Spectrum because the per-pixel cost is enormous (~50 T per pixel for perspective-correct texturing). The handful of textured 3D demos on the Spectrum use either:

- **Affine texture mapping** (no perspective correction): cheap but visually distorted.
- **Per-cell attribute texturing**: the texture is sampled at the centre of each attribute cell, giving 32×24 resolution. Cheap and acceptable for distant objects.
- **Multicolor texture mapping**: per-scanline attribute sampling, giving 32×192 resolution. Expensive but visually impressive; rare.

### 10.7 Variants

- **Vector objects** with thousands of vertices: modern Russian work (post-2005) has demonstrated objects with 1000+ vertices at single-digit frame rates.
- **3D scenes** with multiple objects and a 3D environment: extremely demanding; only a handful of demos attempt it.
- **Real-time morphing**: vertices are interpolated between two object definitions, producing a morphing animation. Adds ~30 T per vertex.
- **Particle 3D**: 3D positions of thousands of particles are projected and drawn as single pixels. Cheap per particle; the standard "energy field" effect.

### 10.8 History

3D wireframe was a flex from the earliest days of the Spectrum demoscene (~1990); simple rotating cubes were among the first "showcase" effects. Filled polygons appeared in the mid-1990s, driven by Soviet groups (Extreme, E-Mage). Gouraud shading and texture mapping came in the late 1990s and reached their peak sophistication in the 2000s. Modern Spectrum 3D work rivals the C64's best 3D and approaches the Amiga's early work.

---

## 11. Other Effects — Particles, Fire, Wobblers, Vector Scroll, Demoscene Texts

This section catalogues the remaining common effects that don't fit into the larger categories above. They are typically **cheap** and used as transitions, atmospherics, or filler between more ambitious parts.

### 11.1 Particle systems

A particle system tracks many small "particles", each with `(x, y, vx, vy, life)`. Each frame, the particle's position is updated by its velocity, the velocity may be updated by gravity or attractors, and the particle is plotted. When `life` reaches zero, the particle is removed.

```
new_x = x + vx
new_y = y + vy
new_vy = vy + gravity
new_life = life - 1
```

Per-particle cost: ~30 T. Per frame with 500 particles: ~15,000 T-states. **Cheap.** Particle systems are commonly used for fireworks, sparks, snow, rain, and explosions.

### 11.2 Fire

Fire is a specific particle-like effect using a **diffusion-and-decay** algorithm:

1. The bottom row of the screen is set to "maximum heat" (white attribute).
2. Each frame, every cell's heat is updated as the average of the cells immediately below it, with a small random decay.
3. The heat value is mapped to a colour via a LUT (black → red → yellow → white).

Per-cell cost: ~30 T. Per frame: 768 cells × 30 T = ~23,000 T-states. **Cheap.** The result is a flickering flame rising up the screen. Variants include "fire + image" (where the heat source is a static image rather than a bottom row) and "cold fire" (a downward-burning variant).

### 11.3 Wobblers

A wobbler takes a static image (typically a logo or font) and **shifts each scanline horizontally by a sinusoidal offset**:

```
For each scanline y:
    offset = amplitude * sin(y * frequency + t)
    shift the scanline left or right by `offset` pixels
```

The result is that the image appears to wave or ripple. Per-scanline cost: ~50 T (for pixel shifting) or ~20 T (for attribute shifting only). Per frame: ~10,000–15,000 T-states. **Cheap.** Wobblers are commonly used on logos and greeting screens.

### 11.4 Vector scroll

Vector scroll (also called "hardware-impossible scroll") displays a long horizontal sequence of text that scrolls smoothly left or right. The Spectrum has no hardware horizontal scroll, so the entire scrolling region must be redrawn each frame.

The trick is to draw the text into a **virtual framebuffer** wider than the screen, then blit only the visible portion to actual screen RAM. With careful per-byte shifting (using the carry flag and `RRA`/`RLA`), a smooth 1-pixel-per-frame scroll is achievable at 50 Hz for a single-line text banner.

Per-frame cost: ~5,000–10,000 T-states for a one-line banner. **Cheap.** Vector scroll text is a staple of cracktros and demo greetings.

### 11.5 Demoscene texts and "demoshell" intros

Beyond the visual effects, most demos include:

- **Greeting texts**: scrolling lists of group names ("Greetings to: Flash Inc, Extreme, Skrju, ...").
- **Effect labels**: "PLASMA ENGINE v3.2 by Random/Group".
- **Effect transitions**: fade-in / fade-out, wipes, "scrollers" that move the text in interesting patterns.

These are not visually demanding but require careful design. A typical demo spends 20–40% of its duration on text/transitions and 60–80% on visual effects.

### 11.6 Bouncing logos

A **bouncing logo** is a sprite (typically 16×16 or 32×32 pixels) that bounces around the screen, sometimes off the edges of the displayed area. The Spectrum has no hardware sprites, so the logo must be redrawn each frame, with the previous position restored.

Per-frame cost: ~5,000 T-states for a 32×32 logo with XOR plotting. **Trivial.** Bouncing logos are a nostalgic reference to the C64 and Amiga demoscene and appear frequently in "old-school" Spectrum demos.

### 11.7 Picture morphing

A morph between two static images, computed as a per-pixel weighted average. Per-pixel cost: ~10 T. Per frame: 6144 pixels × 10 T = ~60,000 T-states. Achievable at 25 Hz on a 128K Spectrum. Morphing is rare but visually striking.

---

## 12. Effect Cost Matrix

A single-table summary of all effects, sorted from cheapest to most expensive.

| Effect | T-states per frame | Frame rate (Pentagon 128K) | Memory cost | Cost class |
|---|---|---|---|---|
| Bouncing logo | ~5,000 | 50 Hz | < 1 KB | Trivial |
| Vector scroll (1-line banner) | ~10,000 | 50 Hz | < 1 KB | Trivial |
| 2D starfield (50 stars) | ~15,000 | 50 Hz | < 1 KB | Cheap |
| Border raster bars | ~15,500 | 50 Hz | < 1 KB | Cheap |
| 32-cell raycaster (no texture) | ~25,000 | 50 Hz | 2–4 KB (map) | Cheap |
| Simple plasma (per-cell) | ~30,000 | 50 Hz | 1–4 KB | Cheap |
| Cell-resolution tunnel | ~30,000 | 50 Hz | 4–8 KB | Cheap |
| Cube wireframe | ~10,000 | 50 Hz | < 1 KB | Cheap |
| Full-screen raster bars | ~28,800 | 50 Hz | < 1 KB | Cheap |
| 3D starfield (100 stars) | ~20,000 | 50 Hz | < 1 KB | Cheap |
| Particle system (500 particles) | ~15,000 | 50 Hz | 1–2 KB | Cheap |
| Fire | ~23,000 | 50 Hz | < 1 KB | Cheap |
| Wobbler | ~15,000 | 50 Hz | < 1 KB (image lives in screen RAM) | Cheap |
| Twister (attribute) | ~20,000 | 50 Hz | < 1 KB | Cheap |
| 32-cell raycaster (textured) | ~45,000 | 50 Hz | 4–8 KB | Moderate |
| Icosahedron wireframe | ~15,000 | 50 Hz | < 1 KB | Moderate |
| Plasma (8×2 multicolor) | ~80,000 | 25 Hz | 2–4 KB | Moderate |
| Twister (8×1 multicolor) | ~80,000 | 25 Hz | 1–2 KB | Moderate |
| Cube filled polygons | ~30,000 | 50 Hz | < 1 KB | Moderate |
| Zoomer (cell-level) | ~80,000 | 50 Hz | 6 KB (image) | Moderate |
| Zoomer + rotaazer | ~150,000 | 25 Hz | 6 KB | Expensive |
| 32-cell voxel landscape | ~120,000 | 25 Hz | 4–8 KB (heightmap) | Expensive |
| Plasma (8×1 multicolor) | ~150,000 | 25 Hz | 4–8 KB | Expensive |
| Tunnel (8×1 multicolor) | ~150,000 | 25 Hz | 8–16 KB | Expensive |
| Space-shuttle 3D filled | ~150,000 | 25 Hz | 2–4 KB (object) | Expensive |
| 256-column raycaster | ~250,000 | 12.5 Hz | 4–8 KB | Frame-bound |
| Pixel-level tunnel | ~180,000 | 25 Hz | 16 KB | Frame-bound |
| Pixel-level plasma | ~250,000 | 12.5 Hz | 16 KB | Frame-bound |
| 3D scene (200+ vertices) | ~500,000 | 5–10 Hz | 8–16 KB | Frame-bound |
| TS-Config video | n/a (disk-streamed) | 25 Hz | 100+ KB (on disk) | Hardware-assisted |

### 12.1 How to use the matrix

When designing a demo:

1. **Pick a target frame rate** (50 Hz for fast action, 25 Hz for showpiece, 12.5 Hz for "look what we did").
2. **Compute the available T-states** per frame: 69,888 T at 50 Hz, 139,776 T at 25 Hz, 279,552 T at 12.5 Hz.
3. **Subtract mandatory overhead**: music player (~5–8K T), bank swaps (~2K T), framework (~3K T). This leaves the **per-frame budget for effects**.
4. **Select effects** whose total cost fits within the budget. A typical demo part uses 1 main effect + 1 secondary effect + scrolltext greetings.

---

## 13. Cross-References

- [multicolor_techniques.md](multicolor_techniques.md) — the raster-timing foundation that most effects rely on for 8×1/8×2 colour detail.
- [precalc_trigonometry.md](precalc_trigonometry.md) — the sine, multiplication, and reciprocal tables that plasma, tunnel, zoomer, and 3D effects all depend on.
- [compression_packing.md](compression_packing.md) — ZX0, ZX1, ZX2, LZSA; used to compress pre-rendered effect frames for TS-Config disk streaming.
- [demo_frameworks.md](demo_frameworks.md) — how effects are sequenced into a multi-part demo, with fades between them.
- [soviet_demo_scene.md](soviet_demo_scene.md) §5 — the cultural context for Soviet refinement of multicolor-based effects (plasma, tunnel, gigascreen video).
- [demoscene_platforms.md](demoscene_platforms.md) §3 — why the C64's hardware sprites and per-pixel colour RAM make some of these effects trivial on that platform (and others impossible).
- [notable_demos.md](notable_demos.md) — specific demos that pushed each effect to new heights; cited per-effect in §3.8, §4.7, §5.6, §6.6, §7.7, §8.7, §9.7, §10.8.
- [../02_hardware/original/ula_timing.md](../02_hardware/original/ula_timing.md) — the ULA's frame timing; the foundation for all "50 Hz at 69,888 T-states" claims in this article.
- [../02_hardware/original/ula_architecture.md](../02_hardware/original/ula_architecture.md) — why the ULA's video generation behaves as it does.
- [../05_development/05_display_and_timing/video_frame_48k.md](../05_development/05_display_and_timing/video_frame_48k.md) — the 48K T-state map (used for raster-bar and twister timing).
- [../05_development/05_display_and_timing/floating_bus.md](../05_development/05_display_and_timing/floating_bus.md) — raster sync technique; required for any per-scanline effect.
- [../05_development/05_display_and_timing/raster_timing.md](../05_development/05_display_and_timing/raster_timing.md) — general raster-timing reference.
- [../05_development/06_graphics/README.md](../05_development/06_graphics/README.md) — pixel and attribute plotting primitives; the building blocks of effects.
- [../05_development/04_interrupts/interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md) — ISR programming; how a 50 Hz effect's main loop is structured.

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/) (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit and distribute any derivative works under the same licence.
