[← Home](../../README.md) · [Graphics](README.md)

# 3D Graphics on the ZX Spectrum

Three-dimensional graphics on a 3.5 MHz Z80 with no floating-point unit, no hardware multiply, and a frame buffer organized as a non-linear 8×8 attribute grid is one of the tightest engineering problems in 8-bit game development. Yet the Spectrum shipped a steady stream of 3D titles: *Elite* (1985), *Star Glider* (1986), *Driller* (1987, the first real-time filled-polygon 3D on any home computer), *Carrier Command* (1988), *Star Glider 2* (1989), *Freescape* titles, the *3D Construction Kit* (1991), plus a separate lineage of isometric adventures starting with *Knight Lore* (1984) and culminating in *Head Over Heels* (1987).

This article covers the techniques those games used, organized by visual style:

- **Wireframe 3D** — *Elite*, *Star Glider*: lines only, no fills, fast enough for real-time at 10-20 Hz
- **Filled-polygon 3D** — *Driller*, *3D Construction Kit*: solid-shaded polygons, frame update at 1-4 Hz
- **Isometric 3D** — *Knight Lore*, *Head Over Heels*: pre-rendered sprites projected isometrically, looks 3D but is fundamentally a 2D engine
- **Raycasting** — pseudo-3D first-person column rendering, late-period Russian and modern homebrew

The math foundation (fixed-point arithmetic, rotation matrices, table-driven multiplication) is shared across all four. The article starts with that foundation, then walks each visual style in turn.

> [!NOTE]
> This article assumes you have read [screen_access.md](screen_access.md) (line drawing requires the address tables described there) and understand the Z80's register set. Code examples are in Z80 assembly. Some math routines use the `RST 0x28` floating-point ROM entry points — those are covered in [c_interop.md](../02_assembly/c_interop.md).

---

## The Z80's Math Problem

The Z80 has no hardware multiply, divide, or floating-point. The core arithmetic instructions are `ADD`, `SUB`, `ADC`, `SBC`, `INC`, `DEC`, and the bitwise operations. Any multiplication, division, or trigonometric function must be implemented in software.

This shapes everything about Spectrum 3D. The CPU can add and subtract in 4 T-states; multiplying two 8-bit values takes ~200 T-states in software; computing a sine takes ~400 T-states. A typical 3D frame on the Spectrum is **dominated by multiplication**, not by line drawing or polygon filling.

The standard solutions:

### 1. Precomputed lookup tables

Sine and cosine values are precomputed at assembly time and stored as 256-byte tables (one full period, 256 entries, each a signed 8-bit value scaled to ±127). A sine lookup is then a single `LD A,(HL)` — 7 T-states instead of ~400.

```z80
; SIN(A) where A is angle in [0, 255] mapping to [0, 360°)
; Returns signed result in A, scaled to ±127
sine_table:
        DEFB 0, 3, 6, 9, ... (256 entries) ..., -3

sine_a:
        LD   L,A
        LD   H,HIGH(sine_table)
        LD   A,(HL)
        RET
```

A cosine table is the same as the sine table, offset by 90° (64 entries in the 256-entry table).

### 2. Table-driven 8×8 multiply

The fastest 8-bit × 8-bit → 16-bit multiply on the Z80 is a **256-byte table lookup followed by an addition**. The table stores partial products. The technique is sometimes called *quarter-square multiplication* because it exploits the identity:

```
a * b = ((a + b)² - (a - b)²) / 4
```

With a precomputed 510-byte square table, multiplication becomes three table lookups and a subtract — about **100 T-states** for an 8×8 → 16-bit result, twice as fast as the shift-and-add algorithm.

```z80
; HL = A * B (unsigned 8x8 -> 16)
; Uses square_table (510 bytes, indexed from -255 to +255)
multiply_8x8:
        LD   C,A
        LD   A,B
        SUB  C              ; A = B - A (signed)
        ; ... handle as signed index into square_table ...
        LD   L,A
        LD   H,HIGH(square_table_base)
        LD   E,(HL)         ; (B-A)² low byte
        INC  H              ; high page of square table
        LD   D,(HL)         ; (B-A)² high byte
        ; Similarly for (B+A)²
        ; result = ((B+A)² - (B-A)²) / 4
        ; ... arithmetic ...
        RET
```

For 3D work, where a frame may require hundreds of multiplications (vertex transformation × 3 coordinates × 3 rotation matrix entries × N vertices), the table-driven multiply is essential.

### 3. Fixed-point arithmetic

Floating-point is too expensive. Spectrum 3D uses **fixed-point**: a 16-bit signed value where the high byte is the integer part and the low byte is the fractional part. This format is called **8.8 fixed-point** (8 bits integer, 8 bits fraction).

```
Value   Memory layout (big-endian for clarity)
+1.0    01 00
+1.5    01 80
+0.25   00 40
-1.0    FF 00
-0.5    FF 80
```

Addition and subtraction work directly on the 16-bit value with `ADD HL,DE` or `SBC HL,DE` (with sign-extension handling). Multiplication of two 8.8 values produces a 16.16 result; the high 16 bits are the answer in 8.8 format.

```z80
; HL = HL * DE (8.8 fixed-point multiply, result in 8.8)
; Uses 16-bit multiply subroutine, then shifts right by 8
fixed_mul_88:
        CALL multiply_16x16     ; HL:DE = HL * DE (32-bit result)
        ; The 8.8 result is in the high 16 bits of the 32-bit product
        ; ... rearrange registers ...
        RET
```

---

## Line Drawing: Bresenham's Algorithm

All wireframe 3D reduces to drawing lines between projected vertices. The Spectrum needs a line-drawing routine that is:

- **Fast** — a typical frame may draw 50-200 lines
- **Integer-only** — no floating-point in the inner loop
- **Single-pixel-wide** — antialiasing is out of the question at 3.5 MHz

**Bresenham's algorithm** satisfies all three. The version below is the standard integer-only implementation, adapted to the Spectrum's non-linear screen layout.

### The algorithm

Given two endpoints `(x0, y0)` and `(x1, y1)`:

1. Compute `dx = |x1 - x0|`, `dy = |y1 - y0|`
2. Initialize error term `err = dx - dy`
3. Loop:
   - Plot `(x, y)`
   - If `(x, y) == (x1, y1)`, done
   - Compute `e2 = 2 * err`
   - If `e2 > -dy`: `err -= dy`, advance `x` toward `x1`
   - If `e2 < dx`: `err += dx`, advance `y` toward `y1`

The clever part is that all decisions are made with integer comparisons against zero — no division, no multiplication, no square roots in the inner loop.

### Spectrum implementation

The line routine below uses precomputed address tables (see [screen_access.md](screen_access.md)) to convert `(x, y)` to a screen address, then walks the Bresenham loop. The inner loop is ~30 T-states per pixel, plotting a 100-pixel line in ~3,000 T-states.

```z80
; Draw line from (D,E) to (H,L) — pixel coordinates 0..255, 0..191
; Destroys all main registers
draw_line:
        ; Compute dx = |x1 - x0|
        LD   A,H
        SUB  D
        JR   NC,.dx_pos
        NEG
.dx_pos
        LD   (dx),A            ; dx = |x1 - x0|

        ; Compute dy = |y1 - y0|
        LD   A,L
        SUB  E
        JR   NC,.dy_pos
        NEG
.dy_pos
        LD   (dy),A            ; dy = |y1 - y0|

        ; Determine step directions
        LD   A,H
        SUB  D
        JR   NC,.sx_pos
        LD   A,-1
        JR   .sx_done
.sx_pos LD   A,1
.sx_done
        LD   (sx),A

        LD   A,L
        SUB  E
        JR   NC,.sy_pos
        LD   A,-1
        JR   .sy_done
.sy_pos LD   A,1
.sy_done
        LD   (sy),A

        ; Initialize err = dx - dy
        LD   A,(dx)
        SUB  (dy)
        LD   (err),A

.line_loop
        ; Plot pixel at (D, E)
        LD   A,E               ; y
        LD   L,A
        LD   H,HIGH(pixel_addr_y) ; y -> screen address low byte
        LD   C,(HL)
        INC  H                 ; pixel_addr_y + 256 -> high byte
        LD   B,(HL)            ; BC = screen row address
        LD   A,D               ; x
        RRCA : RRCA : RRCA     ; x / 8
        AND  31                ; column index 0..31
        ADD  A,C
        LD   C,A               ; BC = byte address
        LD   A,D
        AND  7                 ; bit within byte (0=MSB, 7=LSB)
        LD   L,A
        LD   A,%10000000
        JR   Z,.bit_done
.bit_shift
        RRCA
        DEC  L
        JR   NZ,.bit_shift
.bit_done
        OR   (BC)
        LD   (BC),A            ; plot pixel

        ; Check endpoint
        LD   A,D
        CP   H
        JR   NZ,.continue
        LD   A,E
        CP   L
        JR   Z,.done
.continue
        ; err *= 2
        LD   A,(err)
        ADD  A,A
        LD   (e2),A
        ; if e2 > -dy: err += dy; x += sx
        LD   A,(dy)
        NEG
        CP   (e2)              ; compare -dy vs e2
        JR   NC,.skip_x
        LD   A,(dy)
        ADD  A,(err)
        LD   (err),A
        LD   A,(sx)
        ADD  A,D
        LD   D,A
.skip_x
        ; if e2 < dx: err += dx; y += sy
        LD   A,(e2)
        CP   (dx)
        JR   NC,.skip_y
        LD   A,(dx)
        ADD  A,(err)
        LD   (err),A
        LD   A,(sy)
        ADD  A,E
        LD   E,A
.skip_y
        JR   .line_loop

.done   RET
```

For performance-critical code (e.g., *Elite*'s ship rendering), this routine is further optimized:

- **Unrolled inner loop** for the common case of horizontal lines (`dx > 0, dy = 0`)
- **Separate routines** for `dx > dy` and `dy > dx` to avoid one branch per pixel
- **Direct screen address computation** rather than table lookup (saves the `LD H,HIGH(...)` and double `LD C,(HL)`)

These optimizations bring the inner loop down to ~20 T-states per pixel, or ~2,000 T-states for a 100-pixel line.

---

## 3D Math: Rotation and Projection

A wireframe 3D frame consists of:

1. **Model coordinates**: each vertex of the object stored as `(x, y, z)` in model space
2. **Rotation**: multiply each vertex by a 3×3 rotation matrix (yaw, pitch, roll) to get world coordinates
3. **Translation**: add the object's position to get camera-relative coordinates
4. **Projection**: divide by `z` (perspective) to get 2D screen coordinates
5. **Line drawing**: connect projected vertices with lines

Each step has a Z80-specific implementation.

### Rotation matrices

The standard rotation matrices are (for rotation about each axis):

```
Yaw (Y-axis):     Pitch (X-axis):     Roll (Z-axis):
[ cosY   0  sinY]   [1    0      0  ]   [cosR  -sinR  0]
[   0    1    0  ]   [0  cosP  -sinP]   [sinR   cosR  0]
[-sinY   0  cosY]   [0  sinP   cosP]   [  0      0    1]
```

The combined rotation matrix is the product of all three. For a frame, the matrix is computed once (9 sine/cosine lookups + 27 multiplies to combine them), then applied to every vertex.

Applying the matrix to a single vertex requires **9 multiplies and 6 adds**:

```
x' = m[0][0]*x + m[0][1]*y + m[0][2]*z
y' = m[1][0]*x + m[1][1]*y + m[1][2]*z
z' = m[2][0]*x + m[2][1]*y + m[2][2]*z
```

At ~100 T-states per table-driven multiply, this is ~900 T-states per vertex. For a 32-vertex ship (typical *Elite* count), vertex transformation alone is ~29,000 T-states — a significant chunk of the ~71,000 T-state frame budget.

### Perspective projection

Projecting a 3D point `(x, y, z)` to 2D screen coordinates:

```
screen_x = origin_x + (x * focal_length) / z
screen_y = origin_y - (y * focal_length) / z
```

The division by `z` is the expensive part. The standard Z80 approach is **table-driven reciprocal**: a precomputed table of `focal_length / z` values, indexed by `z`. With a 256-entry table covering `z` from 1 to 256, projection becomes:

```z80
; HL = projected x coordinate
; A = x (signed 8-bit), C = z (unsigned 8-bit, 1..255)
project_x:
        LD   L,C
        LD   H,HIGH(reciprocal_table)  ; HL -> focal/z
        LD   E,(HL)                     ; E = focal_length / z (8-bit)
        ; multiply A * E -> 16-bit result
        LD   L,A
        CALL multiply_8x8_signed        ; HL = A * E
        LD   A,H                        ; take high byte (8.0 result)
        ADD  A,SCREEN_CENTER_X
        LD   L,A
        LD   H,0
        RET
```

With this routine, projecting a vertex is ~200 T-states — much cheaper than the rotation. Total per vertex: ~900 (rotation) + ~400 (two projections) = **~1,300 T-states**. For a 32-vertex ship: ~42,000 T-states.

### Near-plane clipping

Vertices with `z <= 0` are behind the camera and must not be projected (the division produces garbage). Real games clip each edge against the near plane: if one endpoint has `z > 0` and the other has `z <= 0`, the line is split at the plane.

The math is straightforward: linearly interpolate the `(x, y, z)` along the edge to find the intersection point.

```
t = (z_near - z0) / (z1 - z0)
x_clip = x0 + t * (x1 - x0)
y_clip = y0 + t * (y1 - y0)
z_clip = z_near
```

The division `(z_near - z0) / (z1 - z0)` is the expensive step, but it happens only once per clipped edge (not per vertex).

---

## Case Study: *Elite* (1985)

*Elite*, written by David Braben and Ian Bell and ported to the Spectrum by Torus Systems, is the canonical wireframe 3D game on the platform. The Spectrum version shipped in 1985 and was a technical showcase — wireframe ships rotating in real time, with up to 16 ships visible at once, at a usable frame rate.

### Architecture

*Elite*'s 3D engine runs at **variable frame rate** depending on how many ships are on screen. With one or two ships visible, the frame rate is around 15-20 Hz; with eight or more, it drops to 4-6 Hz. The engine is interruptible: the player's input is read every frame, but rendering ships is batched.

Key techniques:

- **All math in 16-bit signed fixed-point** (1.15 format, where the high bit is the sign and the low 15 bits are the fractional part). This gives enough precision for vertex coordinates without overflowing the Z80's 16-bit registers.
- **Precomputed trig tables** for sin/cos, 256 entries each.
- **Table-driven multiply** for the rotation matrix multiply.
- **Back-face culling**: faces whose normal points away from the camera are skipped. This roughly halves the number of lines drawn for typical convex ships.
- **Edge list deduplication**: each face's edges are stored once, with a flag indicating whether they have been drawn this frame. Drawing face 1 stores its edges; drawing the adjacent face 2 finds the shared edge already flagged and skips it.

### Ship data format

Each ship is stored as:

- **Vertex list**: `(x, y, z)` coordinates, 1 byte each (signed). A Cobra Mk III has 26 vertices; a Python has 30; a small fighter has 12-16.
- **Face list**: each face is a list of vertex indices, plus a normal vector. The normal is used for back-face culling.
- **Edge list**: each edge is a pair of vertex indices plus a flag byte. The flag indicates visibility (some edges are always drawn, some only if both adjacent faces are visible).

The data is tightly packed — a typical ship is 80-150 bytes total. The Spectrum version of *Elite* ships with about 32 ship definitions, plus the space station and the sun.

### Frame budget

For a typical scene with 3 ships visible, the per-frame work is:

- Rotation matrix computation: ~5,000 T-states (once)
- Vertex transformation: 3 ships × 20 vertices × 1,300 T-states = ~78,000 T-states
- Edge drawing (after culling): ~30 lines × 2,000 T-states = ~60,000 T-states
- Total: ~143,000 T-states, or **~2 frames** at 50 Hz

The result is that *Elite*'s frame rate settles around 10-15 Hz in typical play — fast enough for dogfights, slow enough that the player sees individual frames as the ship rotates.

### Other wireframe titles

- **Star Glider** (Argonaut, 1986) — similar approach to *Elite*, with ground texture and a larger playfield
- **Sentinel** (Firebird, 1986) — first-person wireframe, 10,000 landscapes procedurally generated
- **Ace of Aces** (US Gold, 1986) — cockpit view with limited wireframe objects
- **Echelon** (Access, 1987) — wireframe space combat with palette-cycled text panels

The wireframe approach dominated 3D on the Spectrum from 1985 to 1987. After *Driller* demonstrated that filled-polygon 3D was feasible, the focus shifted.

---

## Filled-Polygon 3D

Drawing solid-shaded polygons is fundamentally harder than wireframe. Each polygon must be filled, hidden surfaces must be removed, and the result must look correct at frame rates the player can interact with.

The Spectrum's filled-polygon era begins with **Driller** (Incentive Software, 1987), the first real-time solid-3D game on any home computer. *Driller*'s engine, called **Freescape**, was developed by Chris Y. Gray, Stephen Northcott, and David A. Y. Broadhurst at Incentive. It was later productized as the **3D Construction Kit** (1991) and **3D Construction Kit II** (1992), which are essentially the Freescape engine exposed as a game-authoring system.

### The hidden-surface problem

For a closed convex object, **back-face culling** suffices: each face has an outward normal, and faces whose normal points away from the camera are invisible. The check is a single dot product per face:

```
visible = (normal · view_vector) < 0
```

For non-convex objects, or for multiple objects in a scene, back-face culling is insufficient. Two additional techniques are used:

1. **Painter's algorithm**: sort all faces by their average z-coordinate (farthest first), draw them in that order. Closer faces paint over farther faces. Cost: O(N log N) sort per frame, plus the fill cost. Failure mode: when faces interpenetrate, the sort produces visible artifacts.
2. **Binary space partitioning (BSP)**: precompute a tree that, for any camera position, yields a correct drawing order in O(N) time. Cost: complex precomputation; the tree is fixed at level-design time and cannot be modified for moving objects. Used by *Doom* (1993) and later; rare on the Spectrum due to memory cost.

*Driller* uses painter's algorithm with back-face culling. The same approach is used by the *3D Construction Kit* and by *Star Glider 2*.

### Polygon filling

Once a polygon's vertices are projected to screen coordinates, the fill routine walks each scanline of the polygon's bounding box, computes the left and right edges at that scanline, and fills the span.

The standard Spectrum routine is **edge-table scanline fill**:

1. **Build edge table**: for each edge of the polygon, store `(y_min, y_max, x_at_y_min, dx_per_scanline)`. The `dx_per_scanline` is `1/slope` of the edge.
2. **For each scanline** in the polygon's y-range:
   - Find all edges that intersect this scanline
   - Sort their x-intersections (typically 2 for a convex polygon, more for concave)
   - Fill the span between consecutive pairs

For an 8×8 attribute screen, the fill is byte-aligned: each fill span starts at a byte boundary, fills complete bytes with `0xFF`, and handles partial bytes at the ends with masks.

```z80
; Fill horizontal span from (D, B) to (D, C) — row D, columns B..C
fill_span:
        ; Convert (D, B) to screen address
        ; ... (see screen_access.md) ...
        ; BC now points to byte containing column B
        ; Compute mask for left edge (high bits set)
        ; Compute mask for right edge (low bits set)
        ; Fill complete bytes in between with 0xFF
        ; Apply edge masks at both ends
        RET
```

A typical polygon fill (say, a 40×40 pixel quad) takes **~10,000 T-states**. For a scene with 20 visible polygons, that's ~200,000 T-states — already 2.5 frames at 50 Hz, before any rotation or projection work.

This is why filled 3D on the Spectrum runs at **1-4 Hz**, not 10-15 Hz. The frame rate is acceptable for slow-paced games (exploration, puzzle-adventure) but not for action games.

### Case study: *Driller* (1987)

*Driller* (released in the US as *Space Station Oblivion*) is the canonical Freescape title. The game takes place on an abandoned mining moon, where the player walks around a 3D environment in first-person perspective, drilling gas pockets to prevent the moon from exploding.

The Spectrum version achieves roughly **2-3 Hz frame rate** when the player is moving (the screen redraws every 0.4-0.5 seconds). When the player stands still, the screen is not redrawn at all — saving the CPU for input polling and the in-game status display.

Key engineering choices:

- **Solid-shaded polygons, no textures**. Each polygon has one INK and one PAPER (typically a single attribute cell covers the whole polygon).
- **Pre-shaded faces**: each face's brightness is precomputed based on the assumed light direction, so the engine does not need to do per-frame lighting calculations.
- **Fixed grid world**: the playfield is divided into a 16×16 grid of sectors, each 256×256 units. The player's position within a sector is `(x, y, z)` in 8-bit; sector coordinates are also 8-bit. This keeps all math in 8-bit where possible.
- **Limited object count**: typically 8-16 visible objects per scene.
- **Precomputed view**: the engine precomputes which sectors are visible from each sector (a visibility set), avoiding the need to test every sector every frame.

### Freescape's data format

A Freescape scene (called an *area*) consists of:

- **Vertex list**: `(x, y, z)` coordinates, 1 byte each
- **Polygon list**: each polygon is a list of vertex indices plus a color/shading byte
- **Object list**: groups of polygons that move or rotate together
- **Entrance/exit points**: special positions for player movement between areas
- **Hotspots**: clickable regions that trigger actions

This data structure was exposed in the *3D Construction Kit* as the user-facing scene format, allowing non-programmers to build Freescape-style games.

### Other filled-3D titles

- **Total Eclipse** (Incentive, 1988) — Freescape engine, Egyptian tomb exploration
- **Castle Master** (Incentive, 1989) — Freescape engine, larger environments
- **Star Glider 2** (Argonaut, 1989) — filled-3D space flight, hybrid with wireframe for distant objects
- **Carrier Command** (Realtime Games, 1988) — filled-3D carrier simulation, faster than Freescape
- **3D Construction Kit** / **3D Construction Kit II** (Incentive, 1991/1992) — Freescape engine as authoring tool
- **Micro Machines** (Codemasters, 1991) — top-down pseudo-3D using sprite scaling, not polygon

The Freescape engine was the high-water mark of Spectrum filled 3D. After the *3D Construction Kit* in 1991, no major publisher invested in further Spectrum 3D engine development — the focus shifted to the 16-bit platforms (Atari ST, Amiga) which had hardware multiply and bitplane graphics.

---

## Isometric 3D (Filmation)

A separate 3D tradition on the Spectrum is the **isometric adventure**, pioneered by Ultimate Play the Game with *Knight Lore* (1984) and developed through *Alien 8* (1985), *Pentagram* (1986), *Gunfright* (1986), and — most famously — Ocean's *Batman* (1986) and *Head Over Heels* (1987). These games look 3D but are technically **2D sprite engines** with pre-rendered isometric graphics.

The technique is sometimes called **Filmation** (after Ultimate's internal engine name for *Knight Lore*) or **isometric projection**. It produces the characteristic "3D room" look of late-period Spectrum adventures, with the player able to walk around objects and view them from four rotational perspectives.

### Why isometric?

True filled 3D (Freescape) at 1-3 Hz is too slow for action games. Wireframe 3D (*Elite*) does not convey solid objects well enough for adventure gameplay. Isometric projection gives the **appearance of 3D** (objects have visible depth, the player can walk around them) while running at the **full 50 Hz** of a 2D sprite engine.

The tradeoff: the player cannot rotate the camera freely. The view is fixed at one of four rotational angles (typically 0°, 90°, 180°, 270°), and the game's rooms are designed around this constraint. Most isometric adventures allow the player to flip the room 90° left or right, cycling through four fixed views.

### The projection math

Isometric projection maps 3D world coordinates `(x, y, z)` to 2D screen coordinates `(sx, sy)`:

```
sx = screen_origin_x + (x - y)
sy = screen_origin_y + (x + y) / 2 - z
```

The x-axis goes one way on screen, the y-axis goes the other way, and the z-axis (height) goes straight up. The factor of 2 in `(x + y) / 2` is what produces the characteristic 2:1 pixel ratio of isometric graphics (the screen tiles are twice as wide as they are tall).

A worked example: object at world `(0, 0, 0)` projects to screen `(origin_x, origin_y)`. Object at `(8, 0, 0)` projects to `(origin_x + 8, origin_y + 4)`. Object at `(8, 8, 0)` projects to `(origin_x, origin_y + 8)`. Object at `(0, 0, 8)` projects to `(origin_x, origin_y - 8)` — directly above.

```z80
; Project world (x, y, z) to screen (sx, sy)
; Inputs: B = x, C = y, D = z
; Outputs: L = sx, E = sy
; Uses: origin_x, origin_y (screen origin constants)
isometric_project:
        ; sx = (x - y) + origin_x
        LD   A,B
        SUB  C                  ; A = x - y
        ADD  A,(origin_x)
        LD   L,A                ; L = sx
        ; sy = ((x + y) / 2) - z + origin_y
        LD   A,B
        ADD  A,C                ; A = x + y
        SRA  A                  ; A = (x + y) / 2  (arithmetic shift right)
        SUB  D                  ; A = (x + y) / 2 - z
        ADD  A,(origin_y)
        LD   E,A                ; E = sy
        RET
```

The math is **purely integer** and takes ~50 T-states per projection — three orders of magnitude faster than a true 3D perspective projection.

### Z-sorting (the painter's algorithm for sprites)

For correct occlusion, sprites must be drawn in **back-to-front order** — the artist farther from the camera is drawn first, the closer artist overpaints it. In an isometric view, "closer to the camera" means **larger (x + y) in world coordinates** (the bottom-right of the room is closest; the top-left is farthest).

The engine maintains a list of objects in the room, each tagged with its `(x, y)` position. Each frame, the list is sorted by `(x + y)` and drawn in that order. For a typical room with 8-15 objects, the sort is cheap (~2,000 T-states).

Static scenery (walls, floor tiles) is drawn first, sorted by `(x + y)`. Moving sprites (player, enemies) are inserted into the sort order each frame.

### Sprite storage: pre-rendered isometric views

Each object needs **4 pre-rendered views** (one per room rotation) plus multiple animation frames per view. A typical player character has 4 views × 4 walk frames = 16 sprites, each 16×16 or 16×24 pixels. At ~64 bytes per masked sprite, that's ~1 KB per character.

A room typically has 6-10 distinct objects, each with 4 views, plus floor and wall tiles. Total sprite data per room: ~4-8 KB. This is why isometric adventures are usually **room-based** — each room is a separate ~16 KB load, with sprite data shared across rooms where possible.

### The Filmation engine lineage

- **Knight Lore** (Ultimate, 1984) — the first isometric adventure on the Spectrum. Player controls Sabreman, transforming between human and werewolf, navigating a castle of 19 rooms. The engine was originally developed for *Knight Lore* but was so far ahead of its time that Ultimate held the game back to avoid undermining their earlier title *Sabre Wulf*.
- **Alien 8** (Ultimate, 1985) — refined Filmation, larger rooms, more objects
- **Pentagram** (Ultimate, 1986) — isometric with magic-combat gameplay
- **Nightshade** (Ultimate, 1985) — simplified isometric, smaller scale
- **Batman** (Ocean, 1986) — Ocean's Filmation-style engine, 8 directional views instead of 4
- **Head Over Heels** (Ocean, 1987) — the peak of the genre: two characters with different abilities, larger rooms, refined sprite compositing

### Reverse-engineering notes

The Ultimate Filmation engine has a recognizable fingerprint in disassembly: a characteristic 32-bit fixed-point sprite blit routine, predictable tile-grid offsets, and a filmstrip attribute system where each row of cells has its own attribute byte in a separate table. See [game_reversing.md § Ultimate Play the Game](../../08_reverse_engineering/game_reversing.md) for technique guidance.

---

## Raycasting (Pseudo-3D)

Raycasting is a technique for rendering a first-person view of a 2D grid-based world without true polygon 3D. The canonical example is *Wolfenstein 3D* (1992) and *Doom* (1993) on the PC. On the Spectrum, the technique appears late and rarely — it is more associated with Russian and Czech demoscene productions of the late 1990s and with modern homebrew.

### How raycasting works

The world is a 2D grid of cells (walls and floor). For each column of the screen, the engine casts a ray from the player's position in the player's facing direction, and finds where it hits a wall. The distance to the wall determines the height of the wall slice drawn in that column.

```
For each screen column c (0..255):
    angle = player_facing - field_of_view/2 + (c / 256) * field_of_view
    step along (cos(angle), sin(angle)) until hitting a wall
    distance = steps taken
    wall_height = SCREEN_HEIGHT / distance
    draw a vertical strip of wall_height pixels in column c
```

The result is a convincing first-person 3D view of a maze of rectangular rooms. The technique is much faster than polygon 3D because each column requires only a ray walk (a few dozen steps), not a full polygon transformation.

### Spectrum implementation

The expensive step is the per-column trigonometry (`cos(angle)`, `sin(angle)`). The standard optimization is a precomputed **fishbowl table** that, for each screen column, stores the cosine correction factor that converts the ray distance to a perpendicular distance (without which the walls appear curved).

```z80
; For each column (0..255):
;   - Cast a ray through the 2D grid
;   - Find the wall cell hit and the distance
;   - Look up wall texture column (which texel to draw)
;   - Draw the vertical strip
raycast_column:
        ; ... angle and ray direction calculation ...
        ; ... DDA (Digital Differential Analyzer) grid walk ...
        ; ... finds (wall_cell, distance, texel_x) ...
        ; Apply fishbowl correction
        LD   A,(current_column)
        LD   L,A
        LD   H,HIGH(fishbowl_table)
        LD   C,(HL)             ; C = cos(angle_from_center)
        ; Multiply distance by C (using table-driven multiply)
        CALL multiply_8x8_signed
        ; Now A holds the perpendicular distance
        ; Compute wall_height = (SCREEN_H * focal) / perpendicular_distance
        ; ... (table-driven reciprocal again) ...
        ; Draw the vertical strip
        RET
```

A typical raycaster on the Spectrum can render a full frame in **~100,000 T-states** (one column at ~400 T-states × 256 columns), achieving roughly **8-12 Hz** at the upper end. Texture-mapped walls are within reach at this speed; flat-shaded walls are noticeably faster.

### Spectrum raycasting titles

- **Legendary** (Sony Imagesoft, 1991) — uses a raycasting-style renderer for the dungeon sections
- **Tomb of Cairo** (homebrew) — Spectrum raycasting demo
- **Russian demoscene** productions from the late 1990s onward frequently include raycasting effects as technical showpieces
- Modern homebrew raycasting engines on the Spectrum Next routinely hit 25-50 Hz thanks to the Layer 2 framebuffer and hardware sprites

Raycasting is rare in commercial Spectrum games because the technique became well-known only after *Wolfenstein 3D* (1992), by which point the commercial Spectrum market was in steep decline. Most Spectrum raycasters are demoscene or modern homebrew.

---

## Performance Budgets

Spectrum 3D is dominated by the same arithmetic-cost tradeoffs at every level. The numbers below are approximate but representative of real implementations.

### Per-operation T-state costs

| Operation | Cost (T-states) | Notes |
|---|---|---|
| 8-bit add/sub | 4 | `ADD A,r`, `SUB r` |
| 16-bit add/sub | 11 | `ADD HL,rr`, `SBC HL,rr` |
| 8×8 → 16 multiply (shift-add) | ~200 | Standard shift-and-add loop |
| 8×8 → 16 multiply (quarter-square) | ~100 | Table-driven, 510-byte table |
| 16×16 → 32 multiply | ~600 | Four 8×8 multiplies plus partial-product adds |
| 8÷8 divide | ~250 | Restoring division loop |
| Sine / cosine (table lookup) | 7 | `LD A,(HL)` into a 256-byte table |
| Reciprocal (1/x, table lookup) | 7 | 256-entry table of precomputed reciprocals |
| Perspective projection (one axis) | ~200 | Reciprocal lookup + multiply |
| Bresenham line plot (per pixel) | ~25 | Plot, advance, decide |
| Polygon fill (per scanline of span) | ~250 | Edge-table lookup + span fill |

### Per-frame budgets at 50 Hz

The Spectrum's 50 Hz frame is **~71,000 T-states** (3.5 MHz ÷ 50). Subtracting interrupt overhead and the typical music player (~3,000-8,000 T-states), the engine has roughly **~60,000 T-states** of useful work per frame.

What fits in 60,000 T-states:

- **Wireframe**: 1-3 ships of 20-30 vertices each, full rotation and projection, 30-50 lines drawn. Frame rate: 10-20 Hz.
- **Filled polygons**: 5-15 small polygons, sorted and filled. Frame rate: 1-4 Hz.
- **Isometric**: full room redraw with 10-15 sprites. Frame rate: 50 Hz.
- **Raycasting**: full screen, 256 columns. Frame rate: 8-12 Hz.

### Optimization patterns

The classic 3D optimization patterns, ranked by payoff on the Z80:

1. **Table-driven math** — sine, cosine, reciprocal, and (with quarter-square) multiply. This is the single biggest win: it converts 200-400 T-state operations into 7-100 T-state operations.
2. **Back-face culling** — eliminate invisible polygons before transforming or filling them. Each culled polygon saves its full transform + fill cost.
3. **Coarse Z-sort** (integer, not fixed-point) — sort by `(x + y)` or by an 8-bit z-bin. Avoids 16-bit compares in the sort loop.
4. **Edge deduplication** — for wireframe, draw each edge once even if shared by two faces.
5. **Fixed grid** — constrain world coordinates to 8-bit per axis. Keeps multiplies in the 8×8 fast range.
6. **Pre-rendered views** (isometric) — trade memory for CPU. Avoids per-frame projection entirely.
7. **Variable frame rate** — draw at the rate the scene allows; never stall the input loop. *Elite* and *Driller* both do this.

---

## Common Pitfalls

### 1. Overflowing 16-bit fixed-point

8.8 fixed-point has a range of ±127.9961. A vertex at world position `(200, 0, 0)` overflows the 8.8 representation. Either constrain the world to ±127 units, or use a smaller fractional part (e.g., 6.10 fixed-point gives ±32 with 4× the resolution).

*Elite* uses 1.15 fixed-point (range ±1) with implicit scaling constants: the vertex coordinates are pre-scaled so that the model fits in [-1, +1] and the projection matrix scales them up at draw time.

### 2. Forgetting to clip against the near plane

A vertex with `z = 0` produces a divide-by-zero in perspective projection (or a wild table lookup if using reciprocal tables). A vertex with `z < 0` is behind the camera and produces nonsense screen coordinates. Always clip edges against the near plane before projecting.

### 3. Painter's algorithm with interpenetrating faces

Painter's algorithm assumes no two faces interpenetrate. If they do (e.g., a sword passing through a wall), the sort will produce visible artifacts: parts of the closer face will be hidden by the farther face. The fix is BSP, or splitting the interpenetrating faces manually at design time, or accepting the artifact in non-critical scenes.

### 4. Using floating-point ROM calls in the inner loop

The Spectrum's ROM floating-point routines (`RST 0x28` and the calculator stack) are general-purpose and correct, but **slow** — a single sine via the ROM takes ~2,000 T-states. They are fine for setup (computing the rotation matrix once per frame) but never in the per-vertex inner loop. Always use table lookups there.

### 5. Confusing camera-relative and world coordinates

The rotation matrix transforms model coordinates to camera-relative coordinates. Adding the object's world position must happen *before* the rotation (for the camera looking around the object) or *after* (for the camera looking at the world), depending on the design. Mixing the two produces objects that rotate around the wrong origin — a common bug that is hard to spot visually until the camera moves.

### 6. Isometric z-sort assuming all objects are at the same height

The standard isometric sort uses `(x + y)` as the sort key, which is correct when all objects sit on the same floor. When objects are at different heights (e.g., a character standing on a platform), the sort must use `(x + y + z_offset)` or another depth measure. A character on a high platform should always be drawn after (i.e., on top of) the platform, regardless of x and y.

### 7. Forgetting that raycasting requires rectangular walls

Raycasting works because the ray-wall intersection is cheap for axis-aligned rectangular walls. If the level design includes diagonal walls, circular columns, or non-grid-aligned geometry, the per-column ray walk has to handle arbitrary intersections — which destroys the performance advantage. Most raycasting engines restrict the level to grid-aligned rectangular walls and approximate other shapes with multiple cells.

---

## Cross-References

- [screen_access.md](screen_access.md) — address tables and fast byte writes used by line drawing and polygon fill
- [sprites_and_masking.md](sprites_and_masking.md) — masked sprite compositing used by isometric engines
- [c_interop.md](../02_assembly/c_interop.md) — Z80 fixed-point arithmetic routines in detail (§ Fixed-Point Instead of Floating Point)
- [game_reversing.md](../../08_reverse_engineering/game_reversing.md) — reversing Ultimate's Filmation engine and other 3D engines
- [effects_catalog.md](../../07_demoscene/effects_catalog.md) — demoscene 3D objects, vector/plasma tunnel effects
- [next_graphics.md](next_graphics.md) — the Spectrum Next's hardware acceleration, which makes filled 3D at 50 Hz feasible

---

## References

- David Braben and Ian Bell, *Elite* source code and documentation — [Elite Wiki](http://www.elitehomepage.org/)
- Chris Y. Gray, Stephen Northcott, David Broadhurst, *Freescape engine* — Incentive Software, internal documentation excerpts archived at [Wikipedia](https://en.wikipedia.org/wiki/Freescape)
- *3D Construction Kit* user manual (Incentive, 1991) — complete Freescape data format reference
- bannalia.blogspot.com, *Filmation math* posts — derivation of the isometric projection used by *Knight Lore* and *Head Over Heels*
- L. Spiro, *[Ultimate Play the Game](https://archive.org/) disassembly notes* — *Knight Lore* and *Alien 8* reverse-engineering writeups
- *Head Over Heels* source reconstruction project (Graham Goring) — commented Z80 source
- *Star Glider* disassembly writeups — Argonaut's wireframe-with-ground engine
- Russian demoscene raycasting source code — late-1990s productions archived at [zx-art.ru](http://zx-art.ru)
- *Wolfenstein 3D* engine documentation — original id Software source release, useful as a reference for the raycasting technique even though it was never ported to the Spectrum
