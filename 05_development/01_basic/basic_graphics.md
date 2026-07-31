[← Home](../../README.md) · [BASIC](README.md)

# Basic Graphics — PLOT, DRAW, CIRCLE, POINT, ATTR

The Sinclair BASIC ROM includes five graphics statements that map directly to the Spectrum's pixel-based display: `PLOT` (set one pixel), `DRAW` (line and arc), `CIRCLE` (circle outline), `POINT` (test one pixel), and `ATTR` (read an attribute cell). These are not library calls — they are wired into the ROM's interpreter and execute via the same calculator stack used for arithmetic. They are also the **only high-level graphics commands a 48K BASIC programmer has** — there is no `LINE` statement, no `BOX`, no `PAINT`, no `SPRITE`. Anything more sophisticated requires either assembly language or layered use of these five primitives.

This article covers the **commands, their coordinate systems, their quirks, and how they interact with the attribute system**. For the underlying display hardware (the 256×192 pixel grid, the 32×24 attribute grid, contended memory), see [video_frame_overview.md](../05_display_and_timing/video_frame_overview.md) and [color_system.md](../05_display_and_timing/color_system.md).

> [!NOTE]
> This article covers **BASIC-level graphics**. For Z80-level pixel pushing (direct screen writes, attribute tricks, multicolor effects), see [screen_access.md](../06_graphics/screen_access.md) (planned) and [raster_timing.md](../05_display_and_timing/raster_timing.md).

---

## Coordinate System

Sinclair BASIC uses a **mathematical** coordinate system, not a screen-memory coordinate system:

- **Origin (0, 0)** is at the **bottom-left** of the paper area
- **X increases to the right** — range 0 to 255
- **Y increases upward** — range 0 to 175
- Coordinates outside these ranges produce `B Integer out of range, 0:1`

```
(0,175) ──────────────────────────── (255,175)
   │                                     │
   │      Y increases upward             │
   │      (mathematical convention)      │
   │                                     │
   │                                     │
(0, 0) ───────────────────────────── (255, 0)
   ▲
   Origin
```

This is the opposite of the screen memory layout, where address `#4000` is the top-left pixel and addresses increase downward and rightward. The ROM's graphics routines internally translate `(x, y)` to the correct screen address every call — see [pixel_address.md](../05_display_and_timing/pixel_address.md) for the formula.

> [!WARNING]
> The coordinate system is **relative to the paper area**, not the full screen. The border (controlled via `BORDER n`) is outside the coordinate space — you cannot `PLOT` into the border. Border color is set via `OUT #FE` in machine code or `BORDER n` in BASIC.

### The PLOT Position

All drawing commands maintain a shared **current plot position** (CPP), which is the (x, y) coordinate where the last graphics command left off. `PLOT` updates the CPP, `DRAW` extends from the CPP to a new point and updates the CPP, `CIRCLE` draws around the CPP and leaves it unchanged (or updates it to the last point drawn, depending on ROM version).

Commands that reset the CPP to (0, 0):

- `CLS` — clear screen
- `RUN` — start program execution
- `CLEAR` — clear all variables
- `NEW` — wipe program

The CPP persists across `PRINT` statements — you can `PLOT` at one point, print some text, then `DRAW` from the original PLOT position.

---

## PLOT — Set One Pixel

```basic
PLOT x, y
PLOT INK color; x, y
PLOT PAPER color; x, y
PLOT INVERSE 1; x, y
PLOT OVER 1; x, y
```

`PLOT` sets a single pixel at coordinate (x, y) and updates the current plot position. The pixel takes its color from the **attribute cell** at that location — you do not specify a color directly with PLOT. To control color, either set the attribute cell first (via `PRINT` with embedded INK/PAPER codes, or `POKE` the attribute byte directly), or use `PLOT INK n; x, y` to set a temporary color for the duration of the PLOT.

### Variants

| Form | Effect |
|---|---|
| `PLOT x, y` | Set pixel at (x, y), using current attribute state |
| `PLOT INK 2; x, y` | Use red ink for this pixel only (does not change the attribute cell permanently) |
| `PLOT OVER 1; x, y` | Toggle pixel (set if clear, clear if set) — useful for erasing |
| `PLOT INVERSE 1; x, y` | Invert pixel (rarely useful — `OVER 1` is preferred) |
| `PLOT PAPER 6; x, y` | Use yellow paper for this pixel only |

> [!IMPORTANT]
> `PLOT INK n;` sets the color **temporarily** for the single PLOT operation. It does not modify the underlying attribute byte at that screen cell — only the pixel bit. To make the color permanent, you must write directly to the attribute byte (`POKE ATTR_ADDR, attr_byte`) or use PRINT with attribute codes. This is a common source of confusion.

### Worked Example

```basic
10 PLOT 0, 0              : REM bottom-left corner
20 PLOT 255, 175          : REM top-right corner
30 PLOT 128, 87           : REM approximate center
40 PLOT INK 2; 0, 87      : REM red pixel at left edge, middle
50 PLOT INK 6; 255, 87    : REM yellow pixel at right edge, middle
```

The result is four points marking the corners and the horizontal middle of the screen, with colored points on the left and right.

---

## DRAW — Line and Arc

```basic
DRAW x, y                : REM line from CPP to (CPP.x + x, CPP.y + y)
DRAW x, y; a             : REM arc turning through angle a radians
DRAW INK n; x, y
```

`DRAW` has two forms:

1. **Straight line**: `DRAW dx, dy` draws a line from the current plot position to a point offset by (dx, dy). The offsets can be negative.
2. **Arc**: `DRAW dx, dy; angle` draws a curve from the CPP to the offset point, where the curve turns through `angle` radians. `angle = 0` is a straight line; positive angles curve to the left (counterclockwise); negative angles curve to the right.

### Straight Line

```basic
10 PLOT 0, 0              : REM start at bottom-left
20 DRAW 255, 175          : REM diagonal line to top-right
```

This draws a diagonal across the screen. The line is drawn using Bresenham's algorithm (or rather, the Spectrum's slightly different variant — see the ROM disassembly for details).

### Negative Offsets

```basic
10 PLOT 128, 87           : REM center
20 DRAW -50, 0            : REM 50 pixels left
30 DRAW 0, 50             : REM 50 pixels up
40 DRAW 50, 0             : REM 50 pixels right
50 DRAW 0, -50            : REM 50 pixels down
```

This draws a 50×50 square centered on the screen, going counterclockwise.

### Arc Form

The arc form is unusual — it takes a third parameter (after a semicolon, not a comma) that specifies the angle through which the line curves:

```basic
10 PLOT 50, 87
20 DRAW 150, 0; PI        : REM semicircle curving upward
```

The angle is in **radians** (like all of Sinclair BASIC's trigonometry). `PI` is a built-in constant equal to approximately 3.14159. An angle of `PI` (180 degrees) draws a semicircle, `PI/2` draws a quarter circle, and `2 * PI` would draw a full circle but produces `B Integer out of range` because the curve math divides by zero at 360 degrees.

> [!NOTE]
> The arc form is rarely used in practice — most BASIC programmers use `CIRCLE` for circles and `DRAW` for straight lines. The arc form is useful for **curved arrows** and **partial curves**, but it is awkward to control for general shapes.

### Drawing Modes

`DRAW` accepts the same `INK`, `PAPER`, `INVERSE`, and `OVER` modifiers as `PLOT`:

- `DRAW OVER 1; x, y` — toggle pixels along the line (useful for erasing)
- `DRAW INK 4; x, y` — draw in green
- `DRAW INVERSE 1; x, y` — draw inverted (rare)

A common idiom for **erasing** a previously drawn line:

```basic
10 PLOT 0, 0
20 DRAW 255, 175          : REM draw visible line
30 PAUSE 50
40 PLOT 0, 0
50 DRAW OVER 1; 255, 175  : REM erase by toggling pixels back
```

---

## CIRCLE — Circle Outline

```basic
CIRCLE x, y, radius
CIRCLE INK n; x, y, radius
```

`CIRCLE` draws the outline of a circle centered at (x, y) with the specified radius. The circle is drawn using the same algorithm internally as `DRAW` with an arc form — `CIRCLE 100, 100, 50` is approximately equivalent to `PLOT 150, 100: DRAW 0, 0; 2 * PI` (with appropriate handling to avoid the divide-by-zero).

```basic
10 CIRCLE 128, 87, 50     : REM circle in the center
20 CIRCLE INK 2; 128, 87, 80   : REM larger red circle
30 CIRCLE 128, 87, 30     : REM smaller circle inside
```

> [!WARNING]
> `CIRCLE` does **not** fill the circle — it draws only the outline. To fill a circle, you must use a loop of `DRAW` statements or `PLOT` individual pixels. BASIC does not have a `PAINT` or `FILL` command.

### Filling a Circle (Workaround)

```basic
10 FOR R = 50 TO 0 STEP -1
20   CIRCLE 128, 87, R
30 NEXT R
```

This draws concentric circles of decreasing radius, effectively filling the area. It is slow (about 2 seconds for a 50-pixel-radius circle) and leaves "holes" if the algorithm misses pixels, but it works.

---

## POINT — Test a Pixel

```basic
LET A = POINT(x, y)
```

`POINT` is a **function**, not a statement — it returns 1 if the pixel at (x, y) is set, 0 if it is clear. This is the inverse of `PLOT`: where `PLOT` sets a pixel, `POINT` reads it.

```basic
10 PLOT 50, 50
20 PRINT POINT(50, 50)    : REM prints 1
30 PRINT POINT(51, 50)    : REM prints 0
```

`POINT` is used for **collision detection** in BASIC games — typically by testing the pixel at the leading edge of a moving object:

```basic
10 REM Simple collision detection
20 LET X = 100: LET Y = 100
30 LET DX = 1: LET DY = 0
40 IF POINT(X + DX, Y + DY) THEN PRINT "BLOCKED": STOP
50 PLOT INK 6; X, Y
60 LET X = X + DX: LET Y = Y + DY
70 GO TO 40
```

> [!IMPORTANT]
> `POINT` is **slow** — about 200 T-states per call when running interpreted. For real-time games, assembly-language pixel reads (via direct attribute-byte or screen-byte inspection) are preferred. See [screen_access.md](../06_graphics/screen_access.md) (planned).

---

## ATTR — Read an Attribute Cell

```basic
LET A = ATTR(line, column)
```

`ATTR` is a function that returns the **attribute byte** (color settings) for a specific character cell. The arguments are not pixel coordinates — they are **character cell coordinates**, where line ranges 0–23 and column ranges 0–31, with (0, 0) at the **top-left** of the paper area.

This is the opposite of `POINT`/`PLOT`/`DRAW`/`CIRCLE`, which all use pixel coordinates with origin at the bottom-left. The two coordinate systems coexist because they reflect two different aspects of the screen:

- **Pixel coordinates** (0–255 × 0–175, origin bottom-left): the 256×192 pixel grid
- **Character coordinates** (0–31 × 0–23, origin top-left): the 32×24 attribute grid

The attribute byte encodes ink, paper, bright, and flash:

| Bits | Meaning |
|---|---|
| 0–2 | **Ink** color (0–7) |
| 3–5 | **Paper** color (0–7) |
| 6 | **Bright** (0 = normal, 1 = bright) |
| 7 | **Flash** (0 = steady, 1 = flashing) |

So `ATTR(0, 0)` returns 56 (`#38`) on a freshly-booted Spectrum — paper 7 (white), ink 0 (black), no bright, no flash:

```
binary: 00111000
        │││││││└─ bit 0: ink bit 0 = 0
        ││││││└── bit 1: ink bit 1 = 0
        │││││└─── bit 2: ink bit 2 = 0    → ink = 0 (black)
        ││││└──── bit 3: paper bit 0 = 1
        │││└───── bit 4: paper bit 1 = 1
        ││└────── bit 5: paper bit 2 = 1  → paper = 7 (white)
        │└─────── bit 6: bright = 0
        └──────── bit 7: flash = 0
```

To extract the ink color from an attribute byte in BASIC:

```basic
10 LET A = ATTR(10, 5)         : REM read attribute of cell at line 10, col 5
20 LET INK_COLOR = A - INT (A / 8) * 8    : REM ink = A mod 8
30 LET PAPER_COLOR = INT (A / 8) - INT (A / 64) * 8   : REM paper = (A / 8) mod 8
40 LET BRIGHT_FLAG = INT (A / 64) - INT (A / 128) * 2  : REM bright = bit 6
```

> [!NOTE]
> Sinclair BASIC has no bitwise AND operator — `8 mod 8` etc. must be computed via `A - INT (A / N) * N`. This is one of the most painful omissions for programmers coming from other BASICs. The 128K ROM does not fix this. To do bitwise operations efficiently, you must call machine code via `USR` — see [basic_peek_poke.md](basic_peek_poke.md).

---

## Screen Access Patterns

### Drawing a Line of Pixels (Manual)

For cases where `DRAW` is too restrictive (e.g., drawing with attribute changes per pixel), use a loop:

```basic
10 FOR X = 0 TO 255
20   PLOT INK X / 32; X, 87
30 NEXT X
```

This draws a horizontal line across the middle of the screen with ink color changing as a function of X. Each pixel takes its own color from the local attribute cell.

### Combining PRINT and PLOT

`PRINT` writes text and updates the attribute cells as it goes; `PLOT`/`DRAW` write pixels but use the existing attribute cells. This means you can combine them: `PRINT` to set up the background colors, then `PLOT` to draw pixels over them:

```basic
10 PRINT AT 10, 5; INK 2; "         "    : REM 9 spaces with red ink → red band
20 PLOT 100, 100                              : REM pixel takes red ink from attribute
```

The pixel at (100, 100) lands in the attribute cell whose ink was just set to red by PRINT, so it appears red.

### Animating with OVER

The classic BASIC animation technique uses `OVER 1` (toggle mode):

```basic
10 FOR X = 0 TO 255
20   PLOT INK 6; X, 87 + 50 * SIN (X / 20)
30   PLOT OVER 1; INK 6; X - 1, 87 + 50 * SIN ((X - 1) / 20)   : REM erase previous
40 NEXT X
```

This draws a sine wave by plotting one pixel and erasing the previous one each frame. The `OVER 1` modifier toggles the pixel off without affecting other pixels in the same cell.

> [!WARNING]
> `OVER 1` toggles pixels — it does not "clear" them. If you call `PLOT OVER 1; x, y` twice on the same pixel, it ends up in its original state. To guarantee a pixel is cleared, use `PLOT INVERSE 1; x, y` (which always clears regardless of starting state — but is also slower because it reads the pixel first).

---

## Performance Notes

Sinclair BASIC graphics are **slow** by machine-code standards. Approximate timings on a 48K Spectrum:

| Operation | Time | Notes |
|---|---|---|
| `PLOT x, y` | ~3.5 ms (~12,000 T-states) | Includes coordinate translation + pixel write + attribute update |
| `DRAW 100, 0` (horizontal line) | ~15 ms (~52,000 T-states) | 100 pixels at ~150 µs/pixel |
| `DRAW 100, 100` (diagonal) | ~20 ms (~70,000 T-states) | Slightly slower due to non-trivial Bresenham |
| `CIRCLE 100, 100, 50` | ~50 ms (~175,000 T-states) | 50 pixels of radius, ~1 ms per degree |
| `POINT(x, y)` | ~3 ms (~10,000 T-states) | Comparable to PLOT |
| `ATTR(line, col)` | ~2 ms (~7,000 T-states) | Just reads the attribute byte |

A frame is 19.97 ms (50.08 Hz) on a 48K. So:

- A single `PLOT` consumes about 17% of a frame
- A `DRAW` across the screen consumes an entire frame
- A `CIRCLE` consumes 2–3 frames

This is why BASIC animation typically uses small moves (10–20 pixels per frame) and why "racing the beam" effects are **impossible in BASIC** — the interpreter simply cannot keep up with the 50 Hz frame rate. For real-time graphics, you need assembly language.

> [!TIP]
> The single biggest speed-up in BASIC graphics is to **reduce the number of statements executed per frame**, not to optimize individual statements. Replacing 10 `PLOT` statements with one `DRAW` (which the ROM implements internally as a tight Z80 loop) is often 3–5× faster than 10 separate BASIC `PLOT` calls, even though both end up calling the same pixel-set routine.

---

## Common Pitfalls

### 1. PLOT Does Not Change Attribute

```basic
10 PLOT INK 2; 100, 100
20 PLOT 102, 100          : REM ink from attribute cell, not the previous INK 2!
```

The first `PLOT INK 2` sets the pixel using a temporary ink color. The second `PLOT` (without the INK clause) uses the attribute cell's ink — which may be different. To make all pixels in a region use the same color, set the attribute cell first (via PRINT or POKE).

### 2. Coordinate System Mismatch

```basic
10 PRINT AT 0, 0; "TOP-LEFT"
20 PLOT 0, 0
```

`PRINT AT 0, 0` writes text at the **top-left** of the screen (character coordinates, origin top-left). `PLOT 0, 0` sets a pixel at the **bottom-left** (pixel coordinates, origin bottom-left). These are different points and easily confused.

### 3. Out-of-Range Coordinates

```basic
10 PLOT 256, 100          : REM "B Integer out of range, 0:1"
20 PLOT 100, 176          : REM same error
```

Coordinates must be 0–255 (X) and 0–175 (Y). Bounds checking is performed at runtime — there is no way to "turn it off" in BASIC. For machine-code pixel pushing, you can write directly to screen memory and bypass the check.

### 4. CIRCLE Does Not Fill

```basic
10 CIRCLE 100, 100, 50
```

This draws only the outline. To fill, use concentric circles (slow) or write a manual fill routine in machine code.

### 5. DRAW Arc Form Uses Semicolon, Not Comma

```basic
10 DRAW 100, 0; PI / 2     : REM correct — semicolon before arc angle
20 DRAW 100, 0, PI / 2     : REM syntax error — comma is wrong
```

The arc form takes two parameters separated by a comma, then the angle separated by a semicolon. This is the only place in Sinclair BASIC where a semicolon separates parameters.

### 6. POINT Cannot Be Used as a Statement

```basic
10 POINT(100, 100)         : REM syntax error — POINT is a function
20 LET A = POINT(100, 100) : REM correct
```

`POINT` and `ATTR` are **functions** — they return a value and must appear in an expression. They cannot be used as standalone statements like `PLOT` and `DRAW`.

---

## Worked Example — A Mandelbrot at BASIC Speed

The classic Mandelbrot set, in pure Sinclair BASIC, takes ~2 hours to render a 64×48 grid on a 48K Spectrum:

```basic
10 REM Mandelbrot set (low resolution)
20 FOR PY = 0 TO 175 STEP 4
30   FOR PX = 0 TO 255 STEP 4
40     LET X = 0: LET Y = 0
50     LET CX = (PX - 128) / 64
60     LET CY = (PY - 87) / 64
70     FOR I = 0 TO 32
80       LET XT = X * X - Y * Y + CX
90       LET Y = 2 * X * Y + CY
100      LET X = XT
110      IF X * X + Y * Y > 4 THEN GO TO 150
120     NEXT I
130     PLOT PX, PY
140     GO TO 160
150     REM pixel is in the set — leave clear
160   NEXT PX
170 NEXT PY
```

This produces a recognizable Mandelbrot outline in roughly two hours. The same algorithm in Z80 assembly renders in about 30 seconds — a 240× speedup. This is the canonical illustration of why assembly language is essential for any serious Spectrum graphics work.

For more Mandelbrot details and faster versions, see the demoscene references in [demoscene_overview.md](../10_demoscene/demoscene_overview.md) (planned).

---

## Cross-References

- [Basic intro](basic_intro.md) — Sinclair BASIC foundation: tokens, syntax, variables
- [Basic sound](basic_sound.md) — `BEEP` and the beeper
- [Basic PEEK/POKE/USR](basic_peek_poke.md) — direct memory access from BASIC
- [Color system](../05_display_and_timing/color_system.md) — the 8-color attribute system, ink/paper/bright/flash
- [Video frame overview](../05_display_and_timing/video_frame_overview.md) — pixel grid, attribute grid, contended memory
- [Pixel address calculation](../05_display_and_timing/pixel_address.md) (planned) — the ROM's `X-Y to screen address` formula
- [Screen access](../06_graphics/screen_access.md) (planned) — direct pixel and attribute writes in Z80
- [Raster timing](../05_display_and_timing/raster_timing.md) — cycle-exact beam racing (assembly only)
- [Basic token table](../../10_references/basic_token_table.md) — byte values for `PLOT`, `DRAW`, `CIRCLE`, `POINT`, `ATTR` tokens

---

## References

- **Sinclair ZX Spectrum Basic Programming** (Steven Vickers, 1982) — chapters 14–17 cover PLOT, DRAW, CIRCLE, POINT, ATTR with worked examples
- **The Complete Spectrum ROM Disassembly** (Logan & O'Hara, 1983) — chapters on the `PLOT`, `DRAW`, and `CIRCLE` routines (`POINT` and `ATTR` are handled by the calculator stack)
- **World of Spectrum — ZX BASIC Manual Chapter 17**: https://worldofspectrum.org/ZXBasicManual/zxmanchap17.html
- **Pixel address calculation reference** — see [pixel_address.md](../05_display_and_timing/pixel_address.md) for the formula used by the ROM
