[← Home](../README.md) · [Demoscene](README.md)

# Multicolor Techniques — 8×1 and 8×2 Color Resolution

> **Scope**: This article covers the most technically demanding technique in the ZX Spectrum's demoscene repertoire: **changing the attribute bytes synchronously with the CRT beam** to achieve a per-pixel or per-scanline color resolution that the hardware was never designed to provide. Multicolor work is what separates casual Spectrum coders from elite ones; it requires cycle-exact timing, deep knowledge of the ULA's behavior, and a willingness to fight the hardware for every last T-state.
>
> The article is paired with [precalc_trigonometry.md](precalc_trigonometry.md) (which supplies the table-driven math that most multicolor effects consume), [effects_catalog.md](effects_catalog.md) (which shows finished effects built on multicolor), and [soviet_demo_scene.md](soviet_demo_scene.md) §5.1 (the cultural context for why Soviet sceners pushed multicolor further than anyone else).

---

## 1. The Constraint: 8×8 Attributes and Color Clash

To understand why multicolor exists, you must first understand what it is reacting against. The Spectrum's video hardware was designed for **low cost**, not for graphical flexibility. Sinclair's engineers made one decision in particular that defines every graphical challenge on the platform:

### 1.1 The attribute cell

The Spectrum's display is organized as a **256×192 pixel framebuffer** stored in two parallel regions of RAM:

- **Pixel RAM** at `#4000`–`#57FF` (6144 bytes): one bit per pixel, eight pixels per byte. A `1` bit is *ink* (foreground); a `0` bit is *paper* (background). The pixel grid is monochrome by itself.
- **Attribute RAM** at `#5800`–`#5AFF` (768 bytes): one byte per **8×8 pixel cell**, encoding the cell's `INK` color (bits 0–2), `PAPER` color (bits 3–5), `BRIGHT` flag (bit 6), and `FLASH` flag (bit 7).

There are `32 × 24 = 768` attribute cells covering the screen — one byte each. The display hardware (the Ferranti ULA on the 48K, the gate array on the +2A/+3) reads one attribute byte and **uses it for eight consecutive scanlines × eight horizontal pixels** = 64 pixels total.

This means the **minimum addressable unit of color is the 8×8 cell**, not the individual pixel. You cannot draw a red dot on a blue background at coordinates (12, 17); you can only color the entire 8×8 cell containing (12, 17) red on blue. Any pixel pattern within that cell shares the same two colors (ink and paper).

### 1.2 Why the attribute system exists

The 8×8 cell is a **memory compromise**. A true per-pixel color framebuffer on a 256×192 display would need, at minimum, 256×192 = 49,152 bytes (one bit per pixel for one bit-plane of color), and realistically 4 bits per pixel for a usable palette = 24,576 bytes. In 1982, RAM was expensive; the Spectrum shipped with 16 KB (later 48 KB) total, of which only 6.5 KB could be spared for the display.

The attribute scheme compresses the color information by a factor of 64: one byte covers 64 pixels. The total display memory is 6144 + 768 = **6912 bytes** — under 7 KB. This was the design constraint that made the Spectrum affordable.

### 1.3 Color clash

The 8×8 cell constraint produces the Spectrum's most famous (and most mocked) graphical artefact: **color clash**. When an image contains two differently-colored objects that happen to share an 8×8 cell, the cell's single INK/PAPER pair must accommodate both — and the result is usually wrong.

The classic example is a yellow face on a black background. If the face occupies some but not all pixels in a cell, the cell's INK must be yellow (for the face pixels) and the PAPER must be black (for the background pixels). That works. But if a blue shirt now crosses into the same cell, the cell can only have one INK color — so the shirt pixels must become yellow, or the face pixels must become blue. Either way, the image is corrupted.

Color clash is why:
- Most Spectrum games use **monochrome graphics with color highlights** — black-and-white sprites with carefully placed color attributes underneath.
- The Spectrum's most iconic games (*Manic Miner*, *Jet Set Willy*, *Chuckie Egg*) have flat black backgrounds with characters drawn in single-ink cells.
- Artists developed a distinct aesthetic of **carefully chosen 2-color palettes per cell** rather than fighting for true color.

### 1.4 The demoscene's response

The demoscene's response to color clash was to attack its root cause: the 8×8 cell granularity. If the hardware only reads one attribute byte per cell *because the ULA fetches one attribute byte per cell*, then **changing the attribute byte mid-cell** would let you change the color mid-cell. The ULA does not cache attributes — it fetches them from RAM on every scanline. So if you overwrite the attribute byte *while* the ULA is fetching it for the next scanline, the next scanline gets the new color.

This is multicolor. It is, in essence, **a race against the CRT beam**: rewrite the attribute bytes just before the ULA reads them, every scanline, for 192 scanlines per frame, at 50 Hz. The window per write is ~16 T-states. The penalty for being late is one or more scanlines of wrong color.

The rest of this article is about how to win that race.

---

## 2. What Multicolor Is — and How It Was Discovered

### 2.1 The basic principle

The Spectrum's display hardware walks through attribute RAM in a predictable pattern, fetching one attribute byte per cell per scanline. **The ULA does not cache attributes.** Each scanline, for each of the 32 cells across the screen, the ULA reads the cell's attribute byte fresh from RAM and feeds it to the video output for that 8-pixel-wide slice.

That means: if you change the attribute byte in RAM *between* the ULA's read of it on scanline *N* and the ULA's read of it on scanline *N+1*, the two scanlines will be displayed with different colors. The cell is no longer 8×8 with one color pair — it is 8×1 with one color pair per scanline. Eight scanlines of one cell can now have **eight different INK/PAPER combinations**.

This is the fundamental trick. Everything else in multicolor engineering is about *how to do this for many cells simultaneously, in real time, without missing the deadline*.

### 2.2 Why this is hard

The hard part is the timing. The ULA walks attribute RAM in lockstep with the CRT beam — about every **16 T-states**, it advances to the next attribute byte (one cell). At the Z80's 3.5 MHz clock, that gives you roughly **4.5 microseconds** per cell. To rewrite an attribute byte in that window, you must:

1. **Compute the new attribute value** (or fetch it from a precomputed table — see [precalc_trigonometry.md](precalc_trigonometry.md) §3 for table-driven approaches).
2. **Write it to the correct address in attribute RAM** (`#5800`–`#5AFF`) **before the ULA reads that address**.
3. **Move to the next attribute byte** and do it again, 32 times per scanline.

If you are even a few T-states late on any one write, the color on that cell will be wrong for one scanline — visible as a **color fringing** artefact. If you are systematically late, the entire effect falls apart. There is no margin for error.

### 2.3 The first discovery (1985–1986)

The discovery of multicolor is usually credited to **independent realisations** by several early Spectrum hackers around 1985–1986, working on games rather than demos. The technique was originally called **"interrupt-driven color"** or **"raster color"**; the term **"multicolor"** (sometimes written "multicolour") became standard in the early 1990s and is now universal in the demoscene.

The earliest widely-cited commercial use was in the game **Zynaps** (Hewson Consultants, 1987), which used per-scanline color changes in the border area and limited interior cells to produce ground/sky gradients. However, the technique was understood in the Spectrum hacking community before then — it appears in several 1986 tape-traded demos and in the boundaries of certain copy-protection schemes.

### 2.4 Why demos pushed it further than games

Commercial game developers had little incentive to use multicolor extensively:

- **Timing-sensitive code is fragile** across the Spectrum's hardware variants. Code timed for the 48K ULA breaks on the 128K, the +2A/+3, and the Pentagon. A commercial game had to run on every Spectrum in the market, which made aggressive multicolor commercially risky.
- **Multicolor consumes almost all CPU time** during the display area, leaving little for gameplay logic. The few commercial games that used it (e.g. *Zynaps*, *Cobra*, *Dragon's Lair*) restricted it to specific scenes or backgrounds.
- **The aesthetic payoff was unclear** at the low resolutions achievable on a CRT television. A perfect 8×1 attribute grid is barely visible on a 1980s TV because the phosphor bleeding masks the scanline boundaries.

The demoscene, by contrast, valued **technical achievement for its own sake** and ran demos on specific hardware configurations (often the Pentagon, where multicolor is significantly easier — see §6.4). Demos also displayed on monitors rather than TVs, which made the scanline detail visible. The combination pushed multicolor from a niche game trick to a defining demoscene art form.

### 2.5 Vocabulary

The vocabulary around multicolor is unfortunately inconsistent. This article uses the following conventions, which match modern Russian and English scene usage:

| Term | Meaning |
|---|---|
| **8×8 attribute** | The hardware default: one INK/PAPER pair per 8×8 cell. |
| **8×2 multicolor** | Attribute change every **2 scanlines** within a cell, giving 4 color pairs per cell. Easier than 8×1; commonly used for static images. |
| **8×1 multicolor** ("true multicolor", "chrominance") | Attribute change **every scanline**, giving 8 color pairs per cell. The hardest common variant; the visual standard for high-end demos since ~1996. |
| **8×1 ×2 interlace** (gigascreen) | Alternating two 8×1 frames on successive video frames; the eye averages them to ~15 perceived colors. See §8. |
| **Pixel-resolution multicolor** (also "8×1 with pixel tricks", "real multicolor" in some sources) | Combining 8×1 attribute changes with carefully chosen pixel patterns to push color resolution below 8 pixels horizontally. Rare and fragile. |
| **Static multicolor image** | A picture prepared offline with 8×1 or 8×2 color detail, displayed without animation. The simplest multicolor use; the test case for new engines. |
| **Multicolor video / animation** | A sequence of multicolor frames played back at 25 or 50 Hz, requiring streaming from disk or RAM-bank switching. The hardest application; modern Russian demos routinely do this via TS-Config (see §7.5). |

---

## 3. 8×2 Multicolor — Fundamentals

8×2 multicolor is the **entry-level technique**: it gives you four distinct color pairs per cell (one per pair of scanlines) and is achievable with hand-written Z80 in a few hundred bytes of code. It is the standard technique for **static multicolor images** and is the foundation for understanding 8×1.

### 3.1 The geometry

An 8×8 cell contains 8 scanlines. With 8×2 multicolor, you change the attribute byte **every 2 scanlines**:

```
Cell scanlines:    0  1  2  3  4  5  6  7
Attribute index:   0  0  1  1  2  2  3  3
                  └─pair 0─┘ └─pair 1─┘ └─pair 2─┘ └─pair 3─┘
```

You get 4 attribute values per cell instead of 1 — a 4× color-detail improvement. The cost is that you must rewrite each cell's attribute byte 4 times per frame (once every 2 scanlines), instead of leaving it alone.

### 3.2 The timing budget

Each scanline is **224 T-states** on the 48K (228 on the 128K, 224 on the Pentagon). The visible paper area is 192 scanlines. The ULA fetches attributes only during the paper area; the border and VBLANK are free CPU time.

For 8×2 multicolor, your code must:

1. Wait for the start of the paper area (scanline 64 on the 48K; see [video_frame_48k.md](../05_development/05_display_and_timing/video_frame_48k.md)).
2. For each pair of scanlines (96 pairs total):
   - Rewrite **all 32 attribute bytes** across the top of the screen before the ULA advances past the first scanline of the pair.
   - Spend the second scanline doing... nothing on the attributes, but you can use it for music playback, joystick reads, or computation for the next pair.

The budget per "rewrite pass" is **224 T-states** (one scanline). In that scanline you must write 32 bytes to attribute RAM. The minimum-cost Z80 instruction for "write byte from a register to an address in HL" is:

```z80
    LD   (HL),A    ; 7 T-states
    INC  HL        ; 6 T-states
```

That is 13 T-states per cell. For 32 cells: `32 × 13 = 416 T-states`. **You cannot do this in one scanline.**

This is the fundamental problem with multicolor: there is **not enough time** in a single scanline to rewrite the whole screen's attributes naively.

### 3.3 The solution: unrolled writes

The standard solution is to **unroll the write loop** and use faster instructions. The fastest Z80 byte-write is `LD (nn),A` (13 T-states) where `nn` is a literal address; but `LD (HL),A` (7 T-states) + `INC HL` (6 T-states) is equally fast at 13 T-states per write — so the unrolling has to find a different speed-up.

The actual trick is to **read the new attribute values from a precomputed table** and write them in a tight unrolled loop:

```z80
; 8x2 multicolor — single scanline rewrite pass
; On entry: HL = address in attribute table for first cell
;           DE = address in precomputed attribute buffer for this pair
;           B  = 0 (32 iterations via DJNZ)
; Note: total cost must be ≤ 224 T-states for the whole pass.

REPT 32
    LD   A,(DE)    ; 7 T-states
    LD   (HL),A    ; 7 T-states
    INC  DE        ; 6 T-states
    INC  L         ; 4 T-states (L only — attribute row is 32 bytes, fits in low byte)
ENDM
                ; Total per cell: 24 T-states
                ; 32 cells: 32 × 24 = 768 T-states — STILL too slow!
```

This is still too slow. 768 T-states vs 224 available = **3.4 scanlines** of CPU time for one rewrite pass.

### 3.4 The real solution: accept partial rewrites

Real 8×2 multicolor engines do **not rewrite every cell every pair of scanlines**. They exploit three observations:

1. **Most cells do not change color between adjacent scanline pairs.** A typical multicolor image has regions of solid color. If cell (5, 3) has the same color on scanline pair 0 and pair 1, there is no need to rewrite it.
2. **The visible artefact for one missed rewrite is small.** A single scanline of wrong color is barely visible at TV resolution.
3. **Only the cells where the color changes between scanline pairs need rewriting.** For a typical image, this is 20–40% of cells, not 100%.

So the engine stores, for each scanline pair, **only the cells whose color differs from the previous pair**. The rewrite code walks a list of `(address, new_colour)` pairs and writes only those. This typically brings the rewrite pass down to ~150–250 T-states per pair — within the scanline budget.

### 3.5 The precomputed attribute stream

For a static multicolor image, the list of `(address, new_colour)` writes is computed **offline** (by a Python script, or by a tool like *BMP2SCR* or *XVD*). The tool takes a 256×192 RGB image, downsamples it to the Spectrum palette, and emits:

- A fixed pixel buffer (6144 bytes) loaded into `#4000`.
- A fixed attribute baseline (768 bytes) loaded into `#5800`.
- A precomputed sequence of writes that the engine plays back during display.

The engine's main loop is just:

```z80
display_loop:
    CALL  wait_for_paper_start
    LD    IX, write_stream        ; precomputed (address, byte) pairs
next_pair:
    ; Play back writes for scanline pair N
    LD    B,(IX+)                 ; count of writes for this pair
    JR    Z, done_pair
write_loop:
    LD    A,(IX+)                 ; new colour
    LD    L,(IX+)                 ; low byte of attribute address
    LD    H,(IX+)                 ; high byte
    LD    (HL),A                  ; apply the write
    DJNZ  write_loop
done_pair:
    CALL  waste_one_scanline      ; burn 224 T-states (the "second" scanline)
    JR    next_pair
```

For a static image, the entire `write_stream` is computed once at load time and played back every frame. For an animated effect (plasma, tunnel), the write stream is regenerated each frame by the effect's math code — which is where the table-driven math from [precalc_trigonometry.md](precalc_trigonometry.md) becomes essential.

### 3.6 What 8×2 buys you

A well-executed 8×2 multicolor image is recognisably "better" than an 8×8 image but still visibly coarse: 8×2-pixel color blocks produce a noticeable **venetian-blind effect** on diagonals and curves. For static art (title screens, loading pictures), 8×2 is usually good enough and the engine cost is modest. For animation and effects, sceners almost always push to 8×1.

---

## 4. 8×1 Multicolor — True Per-Scanline Colour

8×1 multicolor is the **visual gold standard** for non-interlaced multicolor work. It gives you eight distinct color pairs per cell — one per scanline — and the visible result is, on a good monitor, indistinguishable from a true per-scanline-color display. It is also where the timing budget becomes truly murderous.

### 4.1 The geometry

With 8×1 multicolor, every scanline of an 8×8 cell can have its own color pair:

```
Cell scanlines:    0  1  2  3  4  5  6  7
Attribute index:   0  1  2  3  4  5  6  7
                  └─8 distinct INK/PAPER pairs─┘
```

You rewrite every cell's attribute byte **every scanline** — 192 rewrites per cell per frame, instead of the cell's original single value.

### 4.2 The timing wall

The arithmetic of §3.3 returns with a vengeance. For 8×1 you must rewrite each cell on **every** scanline, not every other scanline. There is no "second scanline to do other work in". And critically, the partial-rewrite trick of §3.4 helps less, because for a typical image the color changes between *adjacent* scanlines are more numerous than between *pair* boundaries.

Roughly: a high-detail 8×1 image has 60–90% of cells changing color between scanlines in busy regions (faces, textures). The naive 32-cell rewrite at 24 T-states/cell = 768 T-states per scanline, but you only have **224 T-states per scanline**. You need to be **3.4× faster than naive**.

### 4.3 The stack-push trick

The fastest known way to write a contiguous run of bytes to memory on the Z80 is the **stack-push trick**: use `PUSH` to write two bytes at a time. `PUSH HL` writes HL to `(SP)`, decrements SP by 2, and costs **11 T-states for 2 bytes** — that is 5.5 T-states per byte, vs 13 for `LD (HL),A;INC HL`.

To use this for attribute writes, you set SP to point *downward* into attribute RAM, pre-load your attribute values into pairs of registers, and execute a sequence of `PUSH` instructions:

```z80
; 8x1 multicolor — single scanline rewrite using stack pushes
; On entry: SP = address of LAST cell in this row's attribute bytes + 1
;           (we PUSH downward, so SP starts high)
;
; Register allocation:
;   H = high byte of attribute address (#58 always for attribute RAM)
;   L = attribute byte for one cell
;   We need 32 different attribute bytes per scanline.
;   Trick: pre-load pairs of attribute bytes into BC, DE, HL and
;   alternate PUSHes with stack offset adjustments.

    LD   SP,#5AC0          ; end of attribute row + padding
    ; (this is set up before the scanline begins)

    ; Sequence of 16 PUSHes writes 32 bytes in 16 × 11 = 176 T-states.
    ; That's 5.5 T-states per byte — within the 224-T-state scanline budget!

    PUSH DE                ; 11 T  (cells 30-31)
    PUSH HL                ; 11 T  (cells 28-29)
    PUSH BC                ; 11 T  (cells 26-27)
    PUSH DE                ; 11 T  (cells 24-25)
    PUSH HL                ; 11 T  (cells 22-23)
    PUSH BC                ; 11 T  (cells 20-21)
    PUSH DE                ; 11 T  (cells 18-19)
    PUSH HL                ; 11 T  (cells 16-17)
    PUSH BC                ; 11 T  (cells 14-15)
    PUSH DE                ; 11 T  (cells 12-13)
    PUSH HL                ; 11 T  (cells 10-11)
    PUSH BC                ; 11 T  (cells 8-9)
    PUSH DE                ; 11 T  (cells 6-7)
    PUSH HL                ; 11 T  (cells 4-5)
    PUSH BC                ; 11 T  (cells 2-3)
    PUSH DE                ; 11 T  (cells 0-1)
                          ; Total: 176 T-states
                          ; Within budget: 224 - 176 = 48 T-states slack.
```

There is a problem: `PUSH` writes **the same register pair repeatedly**. You cannot push 32 different values with 16 `PUSH` instructions if each register pair holds only one fixed value. The trick above works only if cells come in pairs of equal color.

### 4.4 The fully general solution: precomputed unrolled code

For arbitrary 8×1 multicolor, the standard solution is **fully unrolled, precomputed code**. For each scanline, the engine emits a sequence of instructions that hard-codes the attribute address and value as immediates:

```z80
; Emitted by the engine for scanline N of an animated effect:

    LD   (#5800),A         ; cell (0, N)  -- 13 T-states
    LD   A,(some_table_0)
    LD   (#5801),A         ; cell (1, N)
    LD   A,(some_table_1)
    LD   (#5802),A         ; cell (2, N)
    ...                    ; 32 such writes per scanline
```

But 32 × 13 = 416 T-states per scanline — **still too slow**.

The actual technique combines several ideas:

1. **Pre-decode the attribute stream into a tightly-packed format** that the engine can read with `LDIR` or stack-push patterns.
2. **Use self-modifying code** (SMC): the engine patches immediate values into a sequence of `LD (nn),A` instructions during the "spare" scanlines or vertical blank.
3. **Use the **`LD (HL),A;INC L`** sequence at 11 T-states/cell** (4 T-states for `INC L` instead of 6 for `INC HL` because the attribute row fits in one page), giving `32 × 11 = 352 T-states` — closer but still over budget.
4. **Skip writes that don't change**: maintain a per-scanline mask of which cells need rewriting, and use conditional branches to skip the unchanged cells.

### 4.5 The "exomizer" approach: per-scanline code generation

The most advanced 8×1 engines (developed in the Soviet scene in the late 1990s) generate **a unique sequence of Z80 instructions per scanline** by combining SMC with a small library of write "templates":

- *Template "solid color"* (1 cell, 11 T): `LD (HL),A:INC L`
- *Template "two-color pair"* (2 cells, 22 T): two `LD (HL),A:INC L` with `A` reloaded between
- *Template "stack run"* (8 cells of varying color, ~70 T): one `PUSH` sequence with setup

The engine, in vertical blank or in a low-activity scanline, walks the per-scanline color data and emits the cheapest template sequence that covers each cell. The result is **per-scanline generated machine code** that is exactly as long as it needs to be — no wasted writes, no wasted T-states.

This is hard. It is essentially a JIT compiler running in real time on a 3.5 MHz Z80. Soviet sceners (Extreme, E-Mage, Skrju, and especially the Inward collective) developed this approach to its limits between 1998 and 2005; modern engines (BMP2SCR's `mc1` mode, the `MSU` engine) use the same ideas with cleaner implementations.

### 4.6 What 8×1 looks like

A well-executed 8×1 multicolor image, on a CRT monitor with reasonable phosphor persistence, looks like a **genuine per-scanline-color display** — comparable to the C64's per-pixel color in *character* detail, though not in pixel detail. Static 8×1 art (portraits, landscapes, recreations of classical paintings) is the standard showcase format for new multicolor engines; modern Russian demos (2005–present) routinely display 8×1 images and animations as one part of a multi-part demo.

---

## 5. Raster Synchronisation — The Floating Bus

All of the timing in §3 and §4 presumes you **know which scanline the ULA is currently generating**. Without that knowledge, you cannot know when to begin the rewrite pass. The Spectrum provides **no hardware raster register** — there is no port you can read that tells you "the beam is currently on scanline 127". The demoscene's solution is a side-effect of the ULA's design called the **floating bus**.

This section is a summary; the full technical reference is [floating_bus.md](../05_development/05_display_and_timing/floating_bus.md).

### 5.1 What the floating bus is

During the paper area, the ULA continuously fetches bytes from screen RAM to feed the video shift register. Its fetch pattern is **2 bytes every 8 T-states**: one pixel byte, then one attribute byte. When the CPU simultaneously tries to read from the contended range (`#4000`–`#7FFF`), the bus arbitration sometimes lets the CPU latch **the byte the ULA just placed on the data bus** — not the actual memory value.

So a read from `#4000`–`#7FFF` during the paper area may return:
- A pixel byte (whatever the ULA is currently reading for the pixel layer)
- An attribute byte (whatever the ULA is currently reading for the attribute layer)
- Or a stale/previous bus value, in some edge cases

Reading via the I/O space — `IN A,(#FF)` — picks up the same floating value without needing to set up an address.

### 5.2 Why this synchronizes raster

Each scanline has a **unique** sequence of pixel and attribute bytes (because the pixel and attribute bytes differ by screen position). If you set up a known pattern in screen RAM and then read the floating bus in a tight loop, the value you read tells you **exactly which scanline and column the ULA is currently generating**.

The classic use is the **"wait for scanline 0"** routine used at the top of a multicolor effect:

```z80
; Wait for the start of the paper area (scanline 64) by polling the floating bus.
; Precondition: the top-left 8x8 cell of the screen contains a unique attribute
; value (e.g. #47 = white ink, red paper) that does NOT appear anywhere else
; in the top row.

wait_for_paper:
    IN   A,(#FF)         ; read the floating bus
    CP   #47             ; is this the unique attribute we planted?
    JR   NZ, wait_for_paper
    ; We are now somewhere in scanline 64 (the first paper scanline).
    ; From here, we count T-states precisely to stay in lockstep.
```

### 5.3 The drift problem

The floating bus gives you a **single-point sync**: one known scanline. From there, you must count T-states to track your position. But counting T-states perfectly for 192 scanlines (43000+ T-states) is hard:

- **Interrupt jitter**: if the AY chip or any other device fires an interrupt during your display code, you lose sync.
- **Contention uncertainty**: code in contended RAM (§6) has variable timing depending on which scanline it's on. A `LD A,(HL)` in contended RAM can take anywhere from 7 to 13 T-states.
- **Branch timing variance**: conditional branches (`JR NZ, ...`) take 7 T-states if taken, 12 if not. Predicting which branch is taken per iteration is hard.

The standard solution is to put all timing-critical code in **uncontended RAM** (`#8000`–`#FFFF`), disable interrupts (`DI`) during the display area, and write the inner loops with **constant-time branches** (e.g. use `AND`/`OR` tricks instead of `JR NZ`).

### 5.4 The re-sync technique

Even with careful coding, multicolor engines occasionally lose sync — typically due to a missed floating-bus read or an unexpected contention delay. The fix is to **re-sync every few scanlines**:

```z80
; Re-sync after every 8 scanlines by polling for a known attribute pattern
; that occurs once every 8 scanlines (i.e. once per character row).

resync_every_8:
    ; ... rewrite 8 scanlines of attributes ...
    ; ... then re-sync before continuing:
wait_next_row:
    IN   A,(#FF)
    CP   ROW_SYNC_BYTE
    JR   NZ, wait_next_row
    JR   resync_every_8
```

This costs a few T-states per re-sync (the wait loop runs 0–N times), but it bounds the worst-case drift to one character row. The visible artefact of a missed sync is a single character row of glitched color, not the entire screen.

### 5.5 Why the Pentagon doesn't need this

On the Pentagon, there is no ULA — and therefore **no floating bus**. This sounds like a problem, but it's actually an advantage: the Pentagon also has **no contention** and a deterministic clock, so timing-based raster sync works perfectly without floating bus polling. You wait a fixed number of T-states after the interrupt and you're guaranteed to be at scanline 64.

This is one reason Soviet multicolor work surpassed Western work from 1995 onward (see [soviet_demo_scene.md](soviet_demo_scene.md) §2.3): Pentagon coders never had to deal with the floating bus's quirks.

---

## 6. Per-Model Differences

Multicolor code that works on one Spectrum variant frequently breaks on another. The four common target platforms (48K, 128K/+2, +2A/+3, Pentagon) differ in three timing-critical dimensions:

1. **Scanline length** in T-states (224 / 228 / 228 / 224)
2. **Contention pattern** (Ferranti ULA 6,5,4,3,2,1,0,0 / same / Amstrad gate array 1,0,7,6,5,4,3,2 / none)
3. **Floating-bus presence** (yes / yes / yes on different banks / no)

A serious multicolor engine targets one model and is **ported** to the others; "write once, run anywhere" is not achievable for high-detail multicolor. This section summarises what each model demands. The full timing references are [ula_timing.md](../02_hardware/original/ula_timing.md) and [contention_model.md](../05_development/03_memory_and_io/contention_model.md).

### 6.1 ZX Spectrum 48K — the canonical target

| Parameter | Value |
|---|---|
| T-states per scanline | 224 |
| T-states per frame | 69,888 |
| Contention | Ferranti ULA pattern 6,5,4,3,2,1,0,0 in `#4000`–`#7FFF` during paper area |
| Floating bus | Yes, on `#4000`–`#7FFF` and `IN A,(#FF)` |
| Interrupt | INT at T-state 0, asserted for 32 T-states |

The 48K is the **reference platform** for Western multicolor work. Code written for the 48K uses the floating bus for raster sync, places timing-critical code in uncontended RAM (`#8000`–`#FFFF`), and reads attribute / pixel data from contended RAM with full awareness that those reads cost extra T-states.

The 48K's ULA has one further quirk: **early/late timing drift**. Different 48K ULA revisions (issue 2, issue 3, issue 4, issue 6) start the frame at slightly different T-states relative to the CPU clock, by up to ±2 T-states. This is invisible to most software but matters for cycle-exact multicolor; well-written engines re-sync mid-frame to compensate.

### 6.2 ZX Spectrum 128K / +2 (grey) — longer scanlines

| Parameter | Value | Difference from 48K |
|---|---|---|
| T-states per scanline | 228 | +4 T-states |
| T-states per frame | 70,908 | +1,020 |
| Scanlines per frame | 311 | −1 |
| Contention | Ferranti ULA pattern (same shape, bank-based) | Banks 1, 3, 5, 7 contended instead of address range |
| Floating bus | Yes, on contended banks | Same behavior, different addresses |
| Interrupt | INT at T-state 0, asserted for 32 T-states | Same |

The 128K and grey +2 use a Ferranti ULA derived from the 48K design, but with **4 extra T-states per scanline**. Multicolor code written for the 48K's 224-T-state scanline **breaks** on the 128K because the rewrite pass finishes 4 T-states "early" each scanline, drifting relative to the beam.

Porting from 48K to 128K requires inserting **4 T-states of padding** into each scanline's rewrite loop. The fix is mechanical but tedious: every `REPT 32` block or unrolled sequence must be re-tuned.

The 128K's bank-based contention is a separate complication: code in `#C000`–`#FFFF` is in the *current* RAM bank, which may or may not be a contended bank depending on the value written to `#7FFD`. Multicolor engines typically place code in uncontended banks (0, 2, 4, 6) and use banks 1, 3, 5, 7 only for attribute data.

### 6.3 ZX Spectrum +2A / +3 (black) — incompatible contention

| Parameter | Value | Difference from 128K |
|---|---|---|
| T-states per scanline | 228 | Same |
| Contention | **Amstrad gate array**, pattern 1,0,7,6,5,4,3,2 | **Completely different** |
| Contended banks | 4, 5, 6, 7 | Different from 128K's 1, 3, 5, 7 |
| Floating bus | Different behavior (much less useful) | Engine rewrites needed |
| Early/late drift | None | Deterministic |

The +2A/+3 are the **most painful multicolor target**. The contention pattern is shifted relative to the 128K/48K, so code that compensates for one pattern gets the wrong delays on the other. Worse, the floating bus behaves differently — it returns attribute values only on specific T-state boundaries, and the technique of §5 (polling for a known attribute) is much less reliable.

Practical result: most multicolor demos **explicitly refuse to run** on the +2A/+3, or ship separate builds. The +2A/+3 are commonly used for *playing* demos via the +3DOS disk interface, but the demos themselves target the 48K or 128K timing.

### 6.4 Pentagon — the easy mode

| Parameter | Value | Difference from 48K |
|---|---|---|
| T-states per scanline | 224 | Same |
| T-states per frame | 69,888 | Same |
| Scanlines per frame | 312 | Same |
| Contention | **None** | Code always runs at full speed |
| Floating bus | None | Different sync technique needed |
| Interrupt | INT at T-state 0 | Same |

The Pentagon is the **easiest multicolor target**. With no contention, code runs at full speed regardless of which bank it's in. With no floating bus, sync is done by **pure T-state counting** from the interrupt — and because the Pentagon has no contention, this counting is exact.

Soviet multicolor work targeted the Pentagon almost exclusively from 1995 onward. Western multicolor work targeting the 48K is often ported *to* the Pentagon but the reverse is rare: Pentagon-targeted demos expect the lack of contention and would run ~17% slow on a real Sinclair.

### 6.5 Compatibility matrix

| Demo targets | Runs on 48K? | Runs on 128K? | Runs on +2A/+3? | Runs on Pentagon? |
|---|---|---|---|---|
| **48K** | Yes | Usually misaligned (4T drift per line) | No (contention differs) | No (no contention, runs fast) |
| **128K** | Misaligned (4T drift) | Yes | No (contention differs) | No (no contention) |
| **+2A/+3** | No (contention differs) | No (contention differs) | Yes | No (no contention) |
| **Pentagon** | Misaligned & 17% fast | Misaligned & 17% fast | Misaligned & 17% fast | Yes |

Most modern multicolor demos ship **separate binaries per target**, often packed into a single TRD or TAP image with a model-detection routine at the start that picks the right one.

---

## 7. Multicolor Engines — Practical Architecture

A **multicolor engine** is the software infrastructure that takes per-scanline color data and plays it back in lockstep with the CRT beam, frame after frame. Beyond the raw timing tricks of §3–§5, real engines must also handle: **memory banking** (128K machines), **double buffering** (for animation), and **per-frame regeneration** of attribute streams (for effects like plasma). This section covers the common architecture patterns.

### 7.1 Static-image engines (the simplest case)

For a **static multicolor image**, the engine is little more than:

1. A load-time setup that places pixel data in `#4000` and the attribute baseline in `#5800`.
2. A precomputed `write_stream` (per §3.5) — the sequence of `(address, byte)` writes that turns the baseline into the final 8×1 or 8×2 image.
3. A display loop that calls `wait_for_paper`, then walks `write_stream` writing bytes in lockstep with the beam.

There is no banking, no animation, no per-frame computation. The total code is typically 200–500 bytes. This is the format every multicolor tutorial starts with.

### 7.2 Banked engines on 128K machines

On the 128K, +2, +2A, +3, and Pentagon-128, the upper 16 KB of address space (`#C000`–`#FFFF`) is a **bank window**: it can be remapped to any of 8 RAM banks by writing a control byte to port `#7FFD`. This is essential for multicolor work because:

- A single 8×1 frame's attribute stream for one part might be **4–6 KB** (compressed: ~1 KB per scanline of attribute data, 192 scanlines = 24 KB raw, ~5 KB compressed).
- The visible screen memory (`#4000`–`#5AFF`) is **6.9 KB** and must remain in place during display.
- The code that runs during display must be in **uncontended RAM**.
- You therefore need additional RAM banks to hold the per-frame attribute data, swapped into a working bank during vertical blank for processing and out again before display.

A typical 128K engine layout:

| Bank | Contents |
|---|---|
| 5 (visible at `#4000`–`#7FFF` always) | Pixel data + attribute baseline |
| 2 (visible at `#8000`–`#BFFF` always) | Engine code, tables, stack |
| 0 (visible at `#C000`–`#FFFF` always) | Engine code, ISR, music player |
| 1 (swappable at `#C000`) | Frame data: write_stream for current frame |
| 3 (swappable at `#C000`) | Frame data: write_stream for next frame |
| 4, 6, 7 (swappable at `#C000`) | Music data, fonts, additional frame buffers |

The engine swaps banks **only during vertical blank**, never during display — bank switches take ~12 T-states and the resulting memory accesses have unpredictable contention on 128K machines, which would desync the rewrite passes.

### 7.3 Double buffering for animation

For animated multicolor (plasma, rotators, tunnels), the engine must **regenerate the write_stream every frame**. The regeneration runs during vertical blank and any "spare" scanlines, and writes to a *back buffer* — bank 3 in the layout above. During display, the engine reads from the *front buffer* (bank 1) for the current frame's writes. At the next vertical blank, the buffers swap roles.

This is **double buffering**, and it is mandatory for any animated multicolor effect at 50 Hz. Without it, the regeneration would have to happen in the same bank the display loop is reading from — which would mean visible tearing (half-finished frames being shown) or a 25 Hz frame rate (every other frame spent regenerating).

The cost: each frame's `write_stream` takes 4–6 KB, so two buffers cost 8–12 KB of banked RAM. On a 128K machine (with ~80 KB usable), this is affordable.

### 7.4 Precomputed stream compression

Storing 50 Hz of unique frame data for a 10-second effect is **5 KB × 500 frames = 2.5 MB** — far beyond what fits in any Spectrum's RAM. Two solutions are common:

1. **Algorithmic generation**: the per-frame `write_stream` is computed from a small algorithm (e.g. plasma: `colour(x,y,t) = sin(x+t) + sin(y+t) + sin((x+y)/2)`). The math runs during vertical blank. This is what most "real-time" multicolor effects do. The constraint is that the algorithm must run in <14 ms (one frame at 50 Hz minus the display time).
2. **Disk streaming via TS-Config**: the per-frame data is precomputed on a PC, compressed (often with ZX0 or LZSA; see [compression_packing.md](compression_packing.md)), and streamed from disk in real time. This is how modern Russian demos achieve full-screen 25 Hz multicolor video. See §7.5.

### 7.5 TS-Config and disk-streamed multicolor

**TS-Config** is a hardware/software standard developed for the Pentagon and its descendants (Pentagon 1024, ATM Turbo, ZX Evolution, ZX Uno, and the MiSTer Pentagon core). It defines:

- A disk-cache controller that streams data from the Beta Disk Interface (WD1793) directly into a configurable RAM region.
- A standard API for "load next frame from disk into bank N", callable during vertical blank.
- A standard frame-packing format: each frame is compressed (typically with ZX0), and frames are concatenated into a single file on disk.

The result: **full-screen 8×1 multicolor video at 25 fps** (50 Hz fields alternating, with gigascreen mixing — see §8). This is the technique behind the most visually impressive Russian demos of the last 15 years.

TS-Config is **not available on original Sinclair hardware**. To run a TS-Config demo, you need:
- A Pentagon 1024 or later Soviet/Russian clone, OR
- An FPGA-based clone (ZX Evolution, ZX Uno, MiSTer with the Pentagon core), OR
- An emulator configured for Pentagon + TS-Config (Unreal Speccy, ZEsarUX).

The cultural significance: TS-Config made it possible to put **full-motion video** on the Spectrum, with the limitation that it must be pre-rendered on a PC. This is the modern pinnacle of Spectrum multicolor work. See [soviet_demo_scene.md](soviet_demo_scene.md) §5.3 for the cultural context.

### 7.6 Engine taxonomies

Engines can be classified along several axes:

| Axis | Values | Notes |
|---|---|---|
| **Target resolution** | 8×2 / 8×1 / interlaced 8×1 ×2 | Higher resolution = harder |
| **Target model** | 48K / 128K / Pentagon / multi | Multi-model engines are rare |
| **Source of frame data** | Precomputed static / Algorithmic / Disk-streamed | Disk-streamed needs TS-Config |
| **Animation rate** | Static / 50 Hz / 25 Hz / 12.5 Hz | Disk-streamed is typically 25 Hz |
| **Number of cells updated per scanline** | Partial (e.g. 30–60%) / Full (100%) | Partial uses the §3.4 trick |

Modern Russian demos typically use: **8×1 interlaced, Pentagon target, disk-streamed via TS-Config, 25 Hz, full-screen updates**. This is the high-end configuration; everything below it is easier.

---

## 8. Gigascreen — Interlace as a Colour-Mixing Technique

Multicolor (§3, §4) achieves high color resolution by **changing attributes faster than the hardware expects**. **Gigascreen** (also called *interlace*, *flicker*, or *attr-attr*) achieves higher **color depth** by exploiting the CRT's phosphor persistence: alternate two attribute values on successive frames (or successive scanlines), and the eye averages them to a perceived intermediate color. The two techniques are independent and frequently combined.

### 8.1 The palette limitation

The Spectrum's standard palette has 8 colors (15 if you count the `BRIGHT` variants separately). With 8×1 multicolor, each cell can display any 8 of these 15 colors per scanline — but no more. There is no way to display **brown**, **orange**, **pink**, **grey**, or **dark yellow**, because those colors are not in the hardware palette.

Gigascreen breaks this limit. By alternating two of the 15 hardware colors at 50 Hz (or 25 Hz with two-frame cycles), the eye perceives a **temporal dither** that approximates their average. The result depends on phosphor persistence, screen brightness, and viewing distance — but for a typical CRT, the perceived colors are quite stable and the effective palette grows from 15 to roughly **60–100** distinguishable colors.

### 8.2 Pairings and perceived results

Some common gigascreen pairings (frame N / frame N+1):

| Frame A | Frame B | Perceived color |
|---|---|---|
| Black (`#00`) | White (`#07`) | Grey |
| Blue (`#01`) | Yellow (`#06`) | Grey (slightly warmer) |
| Red (`#02`) | Cyan (`#05`) | Grey (slightly cooler) |
| Red (`#02`) | Yellow (`#06`) | Orange |
| Blue (`#01`) | Red (`#02`) | Purple / magenta |
| Black (`#00`) | Red (`#02`) | Dark red |
| Black (`#00`) | Blue (`#01`) | Dark blue / navy |
| White (`#07`) | Red (`#02`) | Pink |
| Green (`#04`) | Red (`#02`) | Brown |

These pairings are the foundation of Soviet "gigascreen" art. With careful choice of pairs, an image can simulate photographic color — though always with some flicker on real CRTs (and total flicker on modern LCDs unless the emulator mixes the two frames).

### 8.3 Frame-based gigascreen

The simplest gigascreen alternates **two complete frames**:

```
Frame 0:  display image A (with its own 8×1 multicolor attributes)
Frame 1:  display image B (different 8×1 attributes)
Frame 2:  display image A again
Frame 3:  display image B again
...
```

Each individual frame's effective resolution is 8×1; the gigascreen averaging happens in the viewer's eye. This technique works well on CRTs with short phosphor persistence (where the previous frame has just faded when the next is drawn) and is the standard gigascreen format in modern Russian demos.

The cost: you must compute **two** attribute streams per frame instead of one. With algorithmic generation, this is twice the math cost; with disk streaming, this is twice the disk bandwidth.

### 8.4 Scanline gigascreen (4-pixel interlace)

A more aggressive variant alternates two attribute values **every scanline** instead of every frame. Because the eye averages vertically, this produces finer detail than frame-based gigascreen but with **more visible flicker** — the eye is sensitive to scanline-level alternation in a way it isn't to frame-level alternation.

Scanline gigascreen was used in some 1990s Soviet demos but is now rare; frame-based gigascreen (§8.3) is preferred because it has the same effective color depth with less flicker.

### 8.5 Gigascreen combined with 8×1 multicolor

The two techniques combine naturally: each of the two gigascreen frames is itself an 8×1 multicolor image. The result is **8×1 color resolution with ~60–100 perceived colors**, which is the visual gold standard for modern Russian Spectrum art. A well-executed gigascreen multicolor still image can resemble a low-resolution photograph in a way that no other 8-bit technique can match.

### 8.6 Gigascreen on modern displays

Gigascreen was designed for **CRT phosphor persistence**. On a modern LCD or OLED display (which has near-instant pixel response), the alternating frames are perceived as harsh flicker rather than averaged color — completely breaking the effect.

Emulators solve this by offering a **"mix" mode**: instead of displaying frame A then frame B alternately, the emulator computes a mathematical blend (e.g. `(A + B) / 2`) and displays the blended image as a single frame. This produces the perceived colors without flicker, and is the standard way gigascreen content is consumed in 2025. Real CRTs and FPGA clones with CRT output preserve the original behavior.

### 8.7 Why this is "Soviet"

Gigascreen was pioneered in the Soviet scene around 1994–1996 (multiple groups claim priority; Extreme and E-Mage are the most-cited) and reached its highest sophistication in Soviet/Russian work through the 2000s. Western Spectrum work used gigascreen sparingly until the 2010s, partly because the Western scene was smaller and partly because Western sceners favored crisp 8×1 color over flicker-based color.

Today, gigascreen is universal — every modern multicolor engine supports it — but the dense, ornamental aesthetic of high-end Soviet gigascreen art remains distinctive. See [soviet_demo_scene.md](soviet_demo_scene.md) §5.2 for the cultural context.

---

## 9. Performance Budget and Limitations

This section consolidates the cost numbers for multicolor work and lists the hard limits that no amount of clever coding can break.

### 9.1 The frame-time budget

At 50.08 Hz (48K) the total frame is **69,888 T-states = 19.968 ms**. The breakdown:

| Region | T-states | Time | Available for |
|---|---|---|---|
| Vertical blank + bottom border | ~12,500 | 3.57 ms | Per-frame math, music, bank swaps |
| Top border | ~14,335 | 4.10 ms | Setup, pre-computation, double-buffer swaps |
| Paper area (192 scanlines × 224T) | 43,008 | 12.30 ms | Multicolor rewrite passes — **almost entirely consumed** |
| **Total** | **69,888** | **19.97 ms** | |

In a "naive" 8×1 multicolor engine, the paper-area time is **completely spent** rewriting attribute bytes. There is essentially zero CPU time available *during display* for anything else (music, joystick, math). All non-display work must happen in the **~7.7 ms of border + VBLANK time** per frame.

### 9.2 Music during multicolor

A standard PT3 music player costs **~5,000–8,000 T-states** per frame (see [soviet_demo_scene.md](soviet_demo_scene.md) §6.4). This must run during the border/VBLANK region; ~7,700 T-states of free time leaves room for music + a small amount of bookkeeping. **Music does not run during the paper area.**

This is fine for simple parts but becomes a constraint for demos that want to do per-frame math (e.g. plasma regeneration) AND play music AND do multicolor. The solution is usually to do the math at 25 Hz (every other frame) so it has more time per pass.

### 9.3 The "real" cost of an 8×1 rewrite pass

Per scanline, for a full 32-cell rewrite using the techniques of §4:

| Technique | Cost per scanline | Cells covered |
|---|---|---|
| Naive `LD (HL),A; INC HL` | 13 T × 32 = **416 T** | 32 |
| `LD (HL),A; INC L` | 11 T × 32 = **352 T** | 32 |
| Stack-push (8 cells per PUSH run, 4 runs of varying setup) | ~250–300 T | 32 |
| Per-scanline generated code (§4.5) | ~150–220 T | 32 (with skips for unchanged cells) |

The state of the art in 2025 is ~150 T-states per scanline for full-screen 8×1, leaving ~75 T-states of headroom per scanline for sync re-anchoring and minor per-scanline computation.

### 9.4 Memory costs

| Item | Bytes | Notes |
|---|---|---|
| Pixel RAM (one screen) | 6,144 | Mandatory, lives at `#4000` |
| Attribute RAM (one screen) | 768 | Mandatory, lives at `#5800` |
| 8×2 attribute stream (full) | 768 × 4 = 3,072 | Per frame |
| 8×1 attribute stream (full) | 768 × 8 = 6,144 | Per frame |
| 8×1 attribute stream (compressed, only-changed) | ~1,000–2,500 | Per frame |
| Double-buffered (×2) | 2,000–5,000 | For animation |
| Engine code | 1,000–3,000 | Per-variant: 48K, 128K, Pentagon separate |
| Sine / math tables | 256–2,000 | For algorithmic effects (see [precalc_trigonometry.md](precalc_trigonometry.md)) |
| Music module (PT3) | ~10,000–30,000 | Per part |

A modern Russian multicolor demo part typically fits in 40–60 KB of banked RAM with disk streaming for asset overflow.

### 9.5 Hard limits — what multicolor cannot do

Despite 30+ years of development, multicolor has hard limits that no technique can break:

1. **No pixel-resolution color.** The 8-pixel horizontal granularity of the attribute byte is a hardware fact. Even "pixel-resolution multicolor" tricks (§2.5) work only for specific patterns, not general images.
2. **No multicolor on +2A/+3 (without rewriting the engine).** The contention model is too different; even with porting, the floating bus is unreliable.
3. **No multicolor + sampled audio at full quality.** Sampled audio (e.g. via the AY's envelope or General Sound) needs predictable CPU time, which multicolor denies during display. Music must be PT3-style (cheap, scheduled).
4. **No mid-frame disk access.** Disk access via TR-DOS takes ~1 frame of CPU time per sector; this would desync the rewrite passes. TS-Config (§7.5) avoids this by doing the disk access during vertical blank using dedicated hardware.
5. **No multicolor above 50 Hz.** The frame rate is fixed by the ULA's video signal generation. Faster-than-50Hz multicolor would require faster-than-Spectrum hardware.
6. **No 8×1 multicolor with arbitrary content at full frame rate on a 48K.** The 48K's contention makes the budget too tight for the most aggressive engines; only Pentagon-class machines (without contention) can sustain true 8×1 at 50 Hz for arbitrary content.

### 9.6 Performance-vs-quality tradeoffs

Engine authors choose along a Pareto frontier:

| Choice | What you get | What you give up |
|---|---|---|
| Static 8×2 | Simplest code; runs on 48K | Detail; animation |
| Static 8×1 | Photorealistic stills | Animation |
| Animated 8×1 (algorithmic) | Real-time plasma etc. | Per-frame compute time |
| Animated 8×1 + gigascreen (algorithmic) | 100-color video | Even less compute time |
| Disk-streamed 8×1 + gigascreen | Full-motion video | Pentagon/TS-Config requirement |

For a demo, each part typically picks one point on this frontier and stays there for the part's duration.

---

## 10. Modern Alternatives — Hardware Extensions

Multicolor is a software technique for getting more color out of stock Spectrum hardware. Several hardware extensions, original and modern, provide alternative paths to higher color depth and resolution.

### 10.1 ULAplus

**ULAplus** is a modern hardware replacement for the Ferranti ULA, available as an upgrade board for original Spectrums and as a standard feature on several modern clones (Harlequin, ZX Uno, ZX Spectrum Next). It provides:

- A **64-color palette** (6 bits per pixel, 2 each for R/G/B), replacing the original 15-color palette.
- A **palette register** at port `#BF3B` (write) / `#FF3B` (select), allowing any of the 64 colors to be assigned to any of the 8 INK and 8 PAPER values.
- Backwards compatibility with original timing — ULAplus does not change scanline length or contention.

ULAplus **does not eliminate the 8×8 attribute constraint**, but it dramatically expands the palette available *within* that constraint. Combined with multicolor, ULAplus makes 8×1 multicolor far more visually effective: instead of choosing between 15 hardware colors per scanline, you choose between 64.

Many modern demos detect ULAplus at startup and use it if available; otherwise they fall back to standard multicolor. The detection routine is a simple port read with checksum.

### 10.2 ZX Spectrum Next — Layer 2 and tilemap modes

The **ZX Spectrum Next** (a modern FPGA-based Spectrum clone) provides two enhanced video modes that obsolete multicolor for new development:

- **Layer 2**: a 256×192, 8-bits-per-pixel (256-color) framebuffer overlaying the standard display. No attribute cells, no multicolor tricks needed — the framebuffer is true per-pixel color.
- **Tilemap**: a hardware-accelerated tile-based mode (similar to the C64's character mode), with per-tile palette and hardware scrolling.

The Next also supports the standard Spectrum display (with multicolor) for backward compatibility. Most Next demos use Layer 2 or tilemap for new effects and standard display for nostalgia.

### 10.3 16-color "timex" modes

The **Timex TC2048** and **TS2068** (Spectrum-compatible machines sold in the US and Portugal in the 1980s) added two extra video modes:

- **HiColor**: 8×1 attribute cells (effectively, hardware multicolor — no timing tricks needed).
- **HiRes**: 512×192 monochrome with per-byte color attributes.

These modes were never widely available in the Soviet scene and had limited Western adoption, but they are supported by modern emulators and by the ZX Spectrum Next. A demo targeting HiColor mode can achieve "8×1 multicolor" trivially, without the timing engineering of this article — at the cost of working only on Timex-class hardware or its emulators.

### 10.4 Why multicolor still matters

Given that ULAplus, the Next's Layer 2, and Timex HiColor all provide higher color resolution with much less effort, why does multicolor remain a vibrant technique in 2025?

1. **Stock-hardware purity.** Many sceners consider stock 48K / 128K / Pentagon hardware the "real" Spectrum, and view hardware extensions as moving the goalposts. Multicolor on stock hardware is a *demonstration of skill*; the same effect on a Next is just a feature.
2. **Compo categories.** Most demoparties have separate compos for "stock Spectrum" and "enhanced Spectrum" demos. The stock-Spectrum compos are where multicolor work competes.
3. **The technical challenge itself.** For a certain kind of scener, the multicolor timing puzzle is the appeal. Writing a 150-T-state-per-scanline engine is its own reward; the visual result is secondary.
4. **Backwards compatibility.** A multicolor demo runs on every Spectrum ever made (with the §6 caveats); a Next-specific demo runs only on a Next.

The likely future: multicolor will continue to be developed for as long as there is a Spectrum demoscene at all, which (based on the past 40 years) is likely to be many more decades. New engines, new compression techniques, and new visual styles continue to appear.

---
## 11. Cross-References

- [soviet_demo_scene.md](soviet_demo_scene.md) §5.1 — cultural context for Soviet multicolor dominance.
- [soviet_demo_scene.md](soviet_demo_scene.md) §5.2 — gigascreen history.
- [soviet_demo_scene.md](soviet_demo_scene.md) §5.3 — TS-Config and disk-streamed multicolor.
- [precalc_trigonometry.md](precalc_trigonometry.md) — table-driven math that feeds algorithmic multicolor effects.
- [effects_catalog.md](effects_catalog.md) — finished multicolor effects cataloged (plasma, tunnel, rotators).
- [compression_packing.md](compression_packing.md) — ZX0 and LZSA, used to compress disk-streamed multicolor frames.
- [demoscene_platforms.md](demoscene_platforms.md) §3 — why the C64's per-pixel color RAM makes multicolor unnecessary on that platform.
- [../02_hardware/original/ula_timing.md](../02_hardware/original/ula_timing.md) — full ULA timing reference; the foundation for all multicolor engineering.
- [../05_development/05_display_and_timing/video_frame_48k.md](../05_development/05_display_and_timing/video_frame_48k.md) — the 48K frame T-state map.
- [../05_development/05_display_and_timing/floating_bus.md](../05_development/05_display_and_timing/floating_bus.md) — full floating-bus reference (raster sync).
- [../05_development/03_memory_and_io/contention_model.md](../05_development/03_memory_and_io/contention_model.md) — contention patterns per model, the root cause of §6.
- [../05_development/05_display_and_timing/video_frame_128k.md](../05_development/05_display_and_timing/video_frame_128k.md) — 128K frame timing.
- [../05_development/05_display_and_timing/video_frame_pentagon.md](../05_development/05_display_and_timing/video_frame_pentagon.md) — Pentagon frame timing.
- [../05_development/04_interrupts/interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md) — ISR programming (used at the start of every multicolor frame).

---

## References

### External references

- **`zx-pk.ru` multicolor / multitekst threads** — primary Russian-language forum for multicolor technique discussions; documents the Pentagon-specific scanline counts and the demoscene idioms for synchronizing to the raster without floating-bus reads.
- **ZXArt (`zxart.ee`)** — the canonical archive of Spectrum demos; search for "multicolor" to find the canonical reference demos (e.g., *Extasy*, *Epic 128*, *Reanimation*, *Shock*, *Crystal Dream*).
- **Gerton Lunter's *Multicolor demonstration* routines** — early worked examples of the timing-safe inner loops that make `8x8` and `8x4` color modes possible at 50 Hz on the 48K.
- **Andrew Owen's *Multicolor Tutorial*** (community-maintained, on WoS archive) — the canonical English-language introduction to multicolor timing for newcomers.
- **`z88dk` and `sjasmplus` documentation** — modern toolchain references for assembling multicolor code with macros that generate the timing tables automatically.

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/) (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit and distribute any derivative works under the same license.
