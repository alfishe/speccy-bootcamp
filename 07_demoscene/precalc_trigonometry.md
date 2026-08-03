[← Home](../README.md) · [Demoscene](README.md)

# Precalculated Trigonometry and Lookup Tables

> **Scope**: This article covers the technique that makes almost every "advanced" Spectrum demo effect tractable: **precomputing trigonometric and arithmetic tables offline and storing them in RAM**, rather than computing values in real time. The Z80 has no hardware multiply or divide, no floating-point unit, and a 3.5 MHz clock; without precomputed tables, real-time 3D, plasma effects, tunnels, and rotation would be impossible. With them, the Spectrum scene produced some of the most ambitious 8-bit demoscene work ever achieved.
>
> The article is paired with [effects_catalog.md](effects_catalog.md) (which shows how these tables are used in practice) and [size_coding.md](size_coding.md) (which covers the special case of tables in 1K/4K intros where memory budget is critical).

---

## 1. Why Precalculation Is Necessary

The Z80's arithmetic capabilities are minimal:

- **No `MUL` or `DIV` instruction**. Multiplying two 8-bit values requires a software loop (~100–300 T-states depending on algorithm). Dividing is even worse.
- **No floating-point support**. All FP work must be done in software; a single FP multiply costs thousands of T-states.
- **Only 8-bit `ADD A,E` and 16-bit `ADD HL,DE`**. There is no 32-bit add, no 16-bit multiply, and the 16-bit `ADD HL,DE` itself is 11 T-states.
- **3.5 MHz clock** (~3.5 million T-states per second). At a 50 Hz frame rate, you have ~70000 T-states per frame *total* — and that includes graphics rendering, music, and the main loop overhead.

A single software `sin()` call via CORDIC or Taylor series costs 1000–5000 T-states on Z80. Computing 192 sine values per frame (one per scanline for a multicolor effect) would consume the entire frame budget — leaving nothing for graphics. **Real-time trigonometry is structurally impossible at this clock speed.**

Precalculation sidesteps the problem entirely:

1. **Precompute the table offline** — on a PC, in Python/C, or via a small BASIC program — and store it in the demo as data.
2. **Look up values at runtime** — a single `LD A,(HL)` (7 T-states) or `LD E,(HL):INC HL:LD D,(HL)` (14 T-states for 16-bit) returns a sine value.
3. **Pay for storage, not computation** — the trade-off is RAM, not CPU cycles.

This trade-off defines Spectrum demo engineering. Every demo decides, for each effect, what to precompute, how to compress it, and how to look it up.

### 1.1 What gets precomputed

- **Sine and cosine tables** (the most common; basis of plasma, tunnels, rotation, wobblers).
- **Multiplication tables** (for fixed-point multiply: precompute `a*b` for all valid `(a,b)` or use indexed lookup).
- **Division / reciprocal tables** (for projection in 3D: `1/z` lookup).
- **Square root tables** (for distance shading and vector normalisation).
- **Arctangent tables** (for rotation effects and "look-at" computation).
- **Precomputed rotation matrices** (for object rotation: store all six or nine matrix entries for the few rotation angles the demo uses).
- **Precomputed object geometry** (3D vertices rotated on PC to a fixed orientation, then re-projected at runtime).
- **Precomputed pixel-coordinate tables** (the Spectrum's weird framebuffer layout means pixel `(x,y)` → address calculation is non-trivial; many demos precompute the address table).

### Article Roadmap

- §2 Fixed-point arithmetic: Q-formats, scaling, signedness.
- §3 Sine and cosine tables: formats, sizes, accuracy tradeoffs.
- §4 Table compression: quarter-wave storage, symmetries, differences between tables.
- §5 Multiplication and division tables: the `MUL8` lookup trick.
- §6 3D rotation matrices: when to precompute, when to compute at runtime.
- §7 Memory budget: how much RAM does a typical demo spend on tables?
- §8 Self-modifying code: tables that double as code, code that doubles as tables.
- §9 Practical examples: plasma, tunnel, 3D rotation, vector shading.
- §10 Cross-References and License.

---

## 2. Fixed-Point Arithmetic

Real numbers must be represented as integers with an implied scaling. The Z80 has only 8-bit `A` and 16-bit `HL/BC/DE` registers, so fixed-point formats are chosen to fit these widths.

### 2.1 Q-notation

A **Qm.n** format is an integer where the bottom `n` bits are the fractional part and the top `m` bits (plus a sign bit if signed) are the integer part. The integer is stored as a 2^n-scaled version of the real value.

Common Q-formats on Z80:

- **Q8.8** (16-bit signed): range [−128, +127.996], step 1/256 ≈ 0.0039. Used for general-purpose math.
- **Q7.8** (16-bit signed): range [−128, +127], step 1/256. The signed variant of Q8.8.
- **Q4.4** (8-bit signed): range [−8, +7.9375], step 1/16. Used for unit-range values (sine/cosine, normalized vectors) where 16-bit storage is too expensive.
- **Q0.8** (8-bit unsigned): range [0, 0.9961], step 1/256. Used for sub-entity fractional positions or table indices.
- **Q0.7** (8-bit signed): range [−1, +0.992], step 1/128. Common for unit-circle sines.

A typical choice for a Spectrum demo is:

- **Q4.4 for sine/cosine tables** (8-bit values, range −1 to +1, accuracy ~0.016 per step).
- **Q7.8 for general-purpose fixed-point math** (16-bit values, range −128 to +127, accuracy ~0.004 per step).
- **Q8.8 (unsigned) for screen coordinates** (range 0–255.996, accuracy ~0.004).

### 2.2 Sine table in Q4.4

A standard Q4.4 sine table covering one full period (256 entries, one per 360°/256 ≈ 1.41°) is:

```z80
; 256-entry sine table, Q4.4 signed: range -128..127 representing -8.0..+7.9375
; Actual sine range is -1..+1, so values are -16..+16 in Q4.4
SIN_TABLE:
    DB 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
    DB 16, 16, 16, 16, 16, 16, 15, 15, 14, 14, 13, 12, 11, 10, 9, 8
    DB 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6, -7, -8
    DB -9, -10, -11, -12, -13, -14, -15, -16, -16, -16, -16, -16, -16, -15, -15, -14
    ; ... (256 entries total, mirroring the above for the negative half)
```

Lookup is trivial:

```z80
        LD      HL,SIN_TABLE
        LD      A,(angle)        ; 0..255 representing 0..360°
        LD      L,A              ; offset into table
        LD      A,(HL)           ; A = sin(angle) in Q4.4, 7 T-states
```

A 256-byte table gives a sine value in 7 T-states (1.9 μs at 3.5 MHz) — **about 1000× faster** than a software `sin()`.

### 2.3 Multiply in Q-format

Multiplying two Q-values requires shifting to remove the duplicated fractional bits. For Q8.8 × Q8.8 → Q8.8:

```z80
; Multiply HL (Q8.8) by DE (Q8.8) → HL (Q8.8)
; Naive: 16x16 → 32-bit multiply, then take bits 8..23.
; Cost: ~200-300 T-states without tables.
```

The cost of unassisted 16-bit multiply on Z80 is high — about 200 T-states for a tight loop. This is why **multiplication tables** (§5) are sometimes precomputed.

### 2.4 When to use 8-bit vs 16-bit

A demo's choice of fixed-point width depends on:

- **Accuracy required**: a plasma effect looks fine with 8-bit Q4.4 sines; a 3D rotation needs Q7.8 to avoid drift over multiple frames.
- **Memory budget**: 8-bit tables are half the size of 16-bit tables.
- **Speed**: 8-bit lookups are faster (no `INC HL:LD D,(HL)` second byte).
- **Code size**: 8-bit multiply code is shorter than 16-bit.

A typical demo uses both — 8-bit for plasma/wobbler effects, 16-bit for 3D work.

### 2.5 Signedness

The Z80's `ADD` and `SUB` are agnostic to signedness; only the flags differ. But comparison and right-shift need signed handling. For Q-format values:

- **Right-shift (divide-by-2)**: use `SRA A` (arithmetic shift, preserves sign) instead of `SRL A` (logical, fills with zero).
- **Comparison**: signed comparison is done by checking sign after subtraction, with a careful flags interpretation.

Many Spectrum demos avoid signedness entirely by using **biased values**: a sine is stored as `0..255` (representing −1 to +1 mapped to 0 to 255), with offset added at lookup. This makes all arithmetic unsigned, simplifying code at the cost of one extra `SUB 128` to convert back.

---
## 3. Sine and Cosine Tables

The sine table is the most fundamental and most-used precomputed table in demoscene work. It is the basis of:

- **Plasma** (sines of x and y coordinates produce a smooth color field).
- **Wobblers / distorters** (sines offset bitmap rows or attributes).
- **Tunnels** (sines and cosines of an angle produce the tunnel's polar coordinates).
- **3D rotation** (sines and cosines of the rotation angle build the rotation matrix).
- **Lissajous figures** (independent sines on x and y).
- **Raster effects** (sine drives the BORD register for wavy borders).

### 3.1 Standard layout

The most common layout is a **256-entry, full-period** sine table stored in a single byte per entry. The 256 entries cover one full 360° rotation, giving ~1.41° per entry. The amplitude is scaled to fit the byte's range.

Two encoding choices are common:

1. **Signed Q4.4** (range −16..+16 in the byte, representing sine −1..+1 in Q4.4 real). Used for math where the result feeds further computation.
2. **Unsigned 0..255** (offset 128 = sine 0; range −128..+127 representing sine −1..+1). Used for direct screen-coordinate writes where the value will be added to a center coordinate.

A complete generation script in Python:

```python
import math
table_signed = [int(round(16 * math.sin(2 * math.pi * i / 256))) for i in range(256)]
table_offset = [(int(round(128 * math.sin(2 * math.pi * i / 256)))) & 0xFF for i in range(256)]
```

### 3.2 Cosine as a sine offset

A cosine is the same data shifted by 90°:

```z80
        ; A = sin(angle) at SIN_TABLE
        ; A = cos(angle) at SIN_TABLE + 64  (90° = 64 entries on a 256-entry period)
```

So a single 256-entry table gives both sine and cosine. This saves 256 bytes vs storing two separate tables.

```z80
; Lookup both sin and cos in one table
SINCOS:
        LD      A,(angle)
        LD      L,A
        LD      H,HIGH(SIN_TABLE)
        LD      A,(HL)            ; A = sin(angle)
        LD      (sin_result),A
        LD      A,(angle)
        ADD     A,64              ; cos = sin + 90°
        LD      L,A
        LD      A,(HL)            ; A = cos(angle)
        LD      (cos_result),A
```

### 3.3 16-bit precision (when 8-bit is not enough)

For 3D rotation that runs over many frames, accumulated 8-bit error produces drift. A 16-bit sine table (Q7.8 or Q8.8 unsigned) doubles the storage to 512 bytes but eliminates drift for hundreds of frames.

A 16-bit lookup is two bytes:

```z80
        LD      A,(angle)
        ADD     A,A               ; 2 bytes per entry
        LD      L,A
        LD      H,0
        LD      BC,SIN_TABLE_16
        ADD     HL,BC
        LD      E,(HL)            ; low byte
        INC     HL
        LD      D,(HL)            ; high byte
        ; DE = sin(angle) in Q7.8
```

Cost: ~30 T-states for the lookup itself — still far faster than software `sin()`.

### 3.4 Choosing the table resolution

The "right" number of entries depends on the effect:

- **32 entries** (full period): low resolution, useful only for slow-changing values (e.g. color cycling). Step ~11°.
- **64 entries** (full period): medium resolution, useful for wobblers and slow plasmas. Step ~5.6°.
- **128 entries** (full period): good general-purpose resolution. Step ~2.8°.
- **256 entries** (full period): the **standard** demoscene resolution. Step ~1.41°.
- **512 entries** (full period): high resolution, used for smooth 3D work.
- **1024 entries** (full period): rare; only used when ultra-smooth rotation is needed and RAM is plentiful.

The trade-off is **memory vs angular resolution**. A 256-entry table at 1 byte per entry is 256 bytes — affordable. A 1024-entry table at 2 bytes per entry is 2048 bytes — significant.

### 3.5 Interpolation for sub-table resolution

Sometimes a 256-entry table is not enough, but a 1024-entry table is too expensive. Linear interpolation between table entries gives sub-table resolution:

```z80
; A = angle (0..1023) into a 256-entry table
; Want result in HL = interpolated sin(angle/4)
        ; high 8 bits are table index
        ; low 2 bits are interpolation fraction
        LD      C,A              ; save
        SRL     A
        SRL     A                ; A = index (0..255)
        LD      L,A
        LD      H,HIGH(SIN_TABLE)
        LD      E,(HL)           ; E = sin(lo)
        INC     HL
        LD      D,(HL)           ; D = sin(hi)
        ; difference = hi - lo
        LD      A,D
        SUB     E                ; A = delta
        ; multiply by fraction (0..3) and add 1 (for 4-quadrant linear interp)
        ; ... (a few more instructions)
```

Linear interpolation on sines has a small error (~0.005 at full amplitude) that is usually invisible in graphics. For audio or precise 3D, **linear interpolation is not enough** and you must either store more samples or use a polynomial.

### 3.6 Tradeoffs summary

| Choice | Bytes | Speed (T-states) | Accuracy |
|---|---|---|---|
| 8-bit sine, 256 entries, no interp | 256 | 7 | 1.4° |
| 16-bit sine, 256 entries, no interp | 512 | 14 | 1.4° |
| 8-bit sine, 256 entries, linear interp | 256 | ~50 | sub-degree |
| 16-bit sine, 1024 entries, no interp | 2048 | 14 | 0.35° |
| Software `sin()` call | 0 | ~2000 | perfect |

The 256-entry 8-bit table is the **universal default**: it fits comfortably in RAM, it is fast enough for any effect, and its accuracy is acceptable for almost all graphics. The other choices are specialisations.

---
## 4. Table Compression: Symmetries and Differences

A full sine table is 256 entries covering 0° to 360°. But a sine has **four-fold symmetry**: the four quadrants are reflections of each other. A quarter-wave table (64 entries, 0° to 90°) is sufficient to reconstruct the full sine.

This section covers the symmetry tricks and the more advanced **difference table** technique used when memory is critical (e.g. in 1K intros).

### 4.1 Four-fold symmetry

A sine has the following symmetries:

- `sin(θ + 90°) = sin(180° − θ)` (mirror around 90°)
- `sin(θ + 180°) = −sin(θ)` (negate)
- `sin(θ + 270°) = −sin(180° − θ)` (mirror + negate)

A 64-entry quarter-wave table covering 0° to 90° (entries 0..63) can be used to look up any angle in 0°..360° (entries 0..255):

```z80
; A = angle 0..255 (full period)
; Quarter-wave table covers 0..63
        CP      64              ; quadrant 0 (0°..90°)?
        JR      C,q0
        CP      128             ; quadrant 1 (90°..180°)?
        JR      C,q1
        CP      192             ; quadrant 2 (180°..270°)?
        JR      C,q2
                              ; else quadrant 3 (270°..360°)
q3:
        SUB     192
        LD      C,A
        LD      B,0
        LD      HL,SIN_QUARTER
        ADD     HL,BC
        LD      A,(HL)
        NEG                     ; negate for q3
        RET
q2:
        SUB     128
        ; q2 is mirror of q0 around 0°..90°
        LD      C,A
        NEG
        ADD     64             ; A = 64 - (A - 128) = 192 - A
        ; ... compute address, negate
        RET
q1:
        SUB     64
        ; q1 = q0 mirrored: index 64 - A
        NEG
        ADD     64
        LD      C,A
        LD      B,0
        LD      HL,SIN_QUARTER
        ADD     HL,BC
        LD      A,(HL)
        RET                     ; positive
q0:
        LD      C,A
        LD      B,0
        LD      HL,SIN_QUARTER
        ADD     HL,BC
        LD      A,(HL)
        RET
```

This costs ~30–40 T-states per lookup (vs 7 for the full table) but saves **192 bytes of RAM** (64 vs 256). For demos tight on memory, the trade is often worthwhile.

### 4.2 Tradeoffs of compression

| Approach | Bytes | Lookup speed | Code complexity |
|---|---|---|---|
| Full 256-entry table | 256 | 7 T | Trivial (1 instruction) |
| Quarter-wave (64 entries) + symmetry | 64 | 30–40 T | Moderate (quadrant logic) |
| Quarter-wave + zero-trim (32 entries) | 32 | 40–50 T | High (zero-suppression) |
| Difference table (§4.3) | 16–32 | 60–80 T | High |

The full table is the right choice for ~95% of demos. Compression is for **size-limited intros** (1K, 4K) and **extremely tight multicolor loops** where every byte matters. See [size_coding.md](size_coding.md) for the size-coding perspective.

### 4.3 Difference tables

A more aggressive compression stores **differences between consecutive sine values** rather than the values themselves. Since adjacent sine values differ by small amounts (max ±2 in Q4.4), the difference sequence is highly compressible.

A typical difference-encoded sine table stores 2-bit codes (00 = no change, 01 = +1, 10 = −1, 11 = +2 or special-case escape). The full 256-entry sine table compresses to 64 bytes (4 entries per byte). Decoding requires reading the byte, masking, shifting, and accumulating — slower but very compact.

Difference tables are the basis of many 1K-intro sine implementations, where 64 bytes for the sine table is affordable but 256 bytes is not.

### 4.4 Differences between sines

If you need **two sines at different frequencies** (common in plasma: `sin(x) + sin(y*2)`), you have two options:

1. **Two full tables** (512 bytes) — fast but expensive.
2. **One full table + different step sizes** — `sin(x)` uses step 1, `sin(x*2)` uses step 2. Only 256 bytes needed. The second option is the **demoscene standard**.

```z80
        LD      A,(angle_x)
        LD      L,A
        LD      H,HIGH(SIN_TABLE)
        LD      A,(HL)            ; sin(angle_x)

        LD      A,(angle_x)
        ADD     A,A               ; *2 step
        LD      L,A
        LD      A,(HL)            ; sin(2*angle_x)
```

This generalises: one table can serve any integer-multiple frequency. Sub-integer frequencies (e.g. `sin(angle*0.7)`) need either a second table or a 16-bit accumulator stepping through the table.

### 4.5 Self-modifying tables

A advanced trick: the **sine table itself can be modified at runtime** to produce different waveforms. For example:

- **Phase-shifted sines**: add a constant to all table entries to bias the sine.
- **Asymmetric sines**: half-wave rectified (set negative half to zero).
- **Distorted sines**: square the entries via lookup against another table.

This is used in advanced effects where the demo wants a "wave" that is not a pure sine but a related shape.

### 4.6 Compression summary

For a typical demo, the rule of thumb is:

- **256-entry 8-bit table is the default** (256 bytes, full symmetry, fast).
- **Quarter-wave** is for medium-tight memory budgets (64 bytes, ~5× slower lookup).
- **Difference encoding** is for 1K intros only (16–32 bytes, very slow lookup, complex code).

Most demos use the full table for everything except the very tightest effects.

---
## 5. Multiplication and Division Tables

After sines, multiplication is the second-most-needed precomputed operation. The Z80's lack of `MUL` means a software 8×8 multiply costs ~100 T-states; a 16×16 multiply ~300–400 T. For effects that need dozens of multiplies per frame (3D projection, texture mapping, vector scaling), this is prohibitive.

The classic solution is the **`MUL8` lookup table**: a 64 KB table indexed by `(a,b)` returning `a*b`. This is too large for the Spectrum's address space, but a **square table** gets the same effect in 512 bytes.

### 5.1 The squaring trick

Use the algebraic identity:

```
a*b = ((a+b)² − (a−b)²) / 4
```

So if we precompute `square(n)` for all `n` in 0..510 (the range of `a+b` and `a−b` after biasing), we can compute any `a*b` in two table lookups and one subtract.

The square table is 511 bytes (for `n` in 0..510, `n²` fits in 16 bits but the high byte is rarely needed; for demo work where products are bounded, an 8-bit `n²/4` table is often enough).

```z80
; Compute A * E, both 0..15 (small range example)
; SQR_TABLE: 32 entries, 0..31 squared / 4
MUL4:
        ; bias to make sum and difference both non-negative
        ADD     A,16              ; A in 16..31
        LD      C,A
        LD      A,E
        ADD     A,16              ; E in 16..31
        ; sum: A + E in 32..62
        LD      L,A
        LD      H,0
        ADD     HL,BC             ; C still has biased A
        ; HL = (A + E) biased
        ; ... lookup (A+E)^2
        ; difference: |A - E|
        ; ... lookup (A-E)^2
        ; subtract, shift
        RET
```

Total cost: ~30 T-states. This is **3–10× faster** than a software multiply loop.

### 5.2 Limited-range multiplication

For many demo effects, the multiplication range is bounded:

- **Sprite scaling**: scale factor 0..16, sprite coordinates 0..255.
- **3D vertex projection**: vertices in range −127..+127, perspective factor in range 1..32.
- **Multicolor cell addressing**: row 0..23, cell 0..31.

For bounded ranges, the table is small. A 16×16 multiply table is just 256 bytes (16 entries × 16 entries, indexed by `(a<<4)|b`).

### 5.3 The full 8-bit `MUL8` table

If you really need full 8×8 → 16-bit multiplication, you can build a 64 KB table — but this is impractical on the Spectrum. Instead, **shift-and-add** is used for full-range multiplies:

```z80
; 8x8 unsigned multiply: HL = H * L (both inputs in H and L; result in HL)
MUL8:
        LD      B,L              ; B = multiplier
        LD      HL,0             ; HL = accumulator
        LD      C,8              ; 8 iterations
loop:   ADD     HL,HL            ; shift accumulator left
        RL      B                ; bring next bit of multiplier into carry
        JR      NC,skip          ; if bit was 0, skip the add
        ADD     HL,DE            ; add multiplicand (held in DE)
skip:   DEC     C
        JR      NZ,loop
        RET
```

Cost: ~250 T-states typical (worst case 8 adds, best case 0 adds). For occasional multiplies this is fine; for hundreds per frame, precomputed tables are better.

### 5.4 Division and reciprocals

Division is harder than multiplication on Z80 (no shift-and-add trick; it requires restoring or non-restoring division with careful bit manipulation). For real-time work, **reciprocal tables** are the answer.

A reciprocal table stores `1/n` for some range of `n`:

```z80
; RECIP_TABLE: 256 entries, each entry = 256/n (Q0.8 approximation of 1/n)
; Look up: instead of dividing X by N, multiply X by RECIP_TABLE[N]
        LD      A,(divisor)
        LD      L,A
        LD      H,HIGH(RECIP_TABLE)
        LD      A,(HL)            ; A = 256/divisor (approx)
        ; Now multiply X by A using MUL8 (§5.3)
```

This converts division into multiplication at the cost of one table lookup. The result is approximate (1/x is irrational for most x) but the error is acceptable for graphics.

### 5.5 Perspective projection: the killer app

The single biggest consumer of division in Spectrum demos is **3D perspective projection**. To project a 3D point `(x, y, z)` to 2D:

```
sx = x * fov / z
sy = y * fov / z
```

Each projected vertex needs two divisions by `z`. A typical 3D object has 50–200 vertices, projected at 10–20 fps. This means 1000–8000 divisions per second.

A software division costs ~300 T-states. 8000 divisions would consume 2.4 million T-states — almost the entire 3.5 MHz CPU budget. With a reciprocal table, each "division" becomes a table lookup (~30 T) plus a multiply (~30 T) — about 60 T-states. 8000 divisions now cost 480000 T-states — about 14% of the CPU budget. The effect becomes tractable.

This is why **virtually every Spectrum 3D demo uses a reciprocal table** for perspective projection. It is the enabling optimisation.

### 5.6 Square root tables

Square root is rarely needed directly, but it appears in:

- **Distance computation** (`sqrt(x² + y²)`) for radial effects.
- **Vector normalisation** for shading.
- **Sphere mapping** in pseudo-3D.

A 256-byte square root table gives `sqrt(n)` for `n` in 0..255, accurate to 0.1. The lookup is one `LD A,(HL)` — fast enough for any effect.

---
## 6. 3D Rotation Matrices

3D rotation is the most demanding consumer of trigonometry in demoscene work. A single 3D rotation about one axis needs 4 sine/cosine lookups and 4 multiplies per vertex; full 3-axis rotation needs 9 lookups and 9 multiplies per vertex. For a 100-vertex object at 20 fps, that is 18000 lookups and 18000 multiplies per second — barely tractable even with tables.

The standard demoscene approach is to **precompute the rotation matrix** once per frame, then apply it to every vertex. This collapses the per-vertex work to 9 multiplies (no trig).

### 6.1 The standard rotation matrix

For rotation about the X axis by angle θ:

```
| x' |   | 1    0       0    |   | x |
| y' | = | 0   cos θ  −sin θ | · | y |
| z' |   | 0   sin θ   cos θ |   | z |
```

The Y and Z rotations are similar (permutations of the same structure). A combined 3-axis rotation is the product of three such matrices, giving a 3×3 matrix with 9 entries.

### 6.2 Precomputing the matrix

At the start of each frame, the demo:

1. Reads three angles `(θx, θy, θz)` from the animation timers.
2. Looks up 6 sines/cosines (3 axes × 2 trig functions each).
3. Computes the 9 entries of the combined matrix via ~10 multiplies.
4. Stores the matrix in 9 bytes (or 9 words for 16-bit precision).

Then for every vertex in the 3D object, the demo applies the precomputed matrix:

```z80
; Vertex: (vx, vy, vz) in Q7.8 fixed-point
; Matrix: m00..m22 in Q7.8 fixed-point
; Result: (rx, ry, rz) in Q7.8 fixed-point
ROTATE_VERTEX:
        ; rx = m00*vx + m01*vy + m02*vz
        LD      L,(vx+0):LD      H,(vx+1)         ; HL = vx
        LD      E,(m00+0):LD     D,(m00+1)        ; DE = m00
        CALL    MUL16                             ; HL = m00*vx
        ; ... add m01*vy, m02*vz
        ; Repeat for ry and rz
```

Per-vertex cost: 9 multiplies + 6 adds ≈ 9×200 + 6×20 = ~2000 T-states. For a 100-vertex object, that is 200000 T-states per frame — about 3 frames' worth of CPU. To get 20 fps, the demo needs 6× as much work — which is why Soviet 3D demos use a smaller vertex count, smaller fixed-point (Q4.4), and aggressive culling.

### 6.3 When to precompute the matrix

Precompute the matrix once per frame (or once per object per frame). Do **not** re-look-up sines per vertex — that doubles the per-vertex cost.

If the object rotates only around one axis (common for "spinning cube" or "spinning logo" effects), precompute the 2D rotation matrix in just 2 entries (`cos θ, sin θ`) and apply only a 2×2 rotation per vertex.

### 6.4 Pre-storing common rotations

If a demo uses only a small set of rotation angles (e.g. 0°, 30°, 45°, 60°, 90°, 120°, 135°, 150°, 180° for a "tumbling" effect), the matrices can be **precomputed entirely on PC and stored in the demo binary**. The runtime just selects which matrix to apply per frame.

This is common for "logo-on-cube" effects where the cube spins on a fixed set of angles.

### 6.5 Per-vertex precision

For 3D vertex coordinates, 16-bit fixed-point (Q7.8 or Q8.8) is the standard choice. 8-bit is too coarse (jitter becomes visible at the projected screen position); 32-bit is too slow.

Some advanced Soviet work uses **mixed precision**: 16-bit for object-space coordinates, 8-bit for the rotation matrix entries (the matrix is bounded to −1..+1 in Q4.4). This saves a multiply of 16×16 by using 16×8 instead, cutting the cost roughly in half.

### 6.6 Normal vectors for shading

For shaded 3D (Gouraud, flat, or Lambert), the demo needs to compute the normal vector of each face after rotation. This is another matrix-vector multiply per face — but since faces are fewer than vertices (typically 1.5–2× fewer), the cost is acceptable.

The shading computation itself (dot product of normal with light direction) is one multiply per face — also tractable.

---

## 7. Memory Budget: How Much RAM for Tables?

A typical high-end Spectrum 3D demo spends the following on tables:

| Table | Bytes | Purpose |
|---|---|---|
| Sine table (8-bit, 256 entries) | 256 | Plasma, wobblers, raster effects |
| Sine table (16-bit, 256 entries) | 512 | 3D rotation |
| Multiplication table (square, 511 bytes) | 511 | `MUL8` via squaring |
| Reciprocal table (256 entries) | 256 | Perspective projection |
| Square root table (256 entries) | 256 | Distance / shading |
| Pixel-address table (192 entries × 2 bytes) | 384 | Spectrum framebuffer layout |
| **Total** | **~2175 bytes** | Out of ~41 KB usable RAM |

So tables consume ~5% of available RAM — a worthwhile investment given that they enable 3D effects at all.

For tight demos (1K intros), the budget is radically different. A 1K intro has **less than 1024 bytes total** for code + data + stack. Tables are compressed to the bare minimum:

- Quarter-wave sine: 32–64 bytes
- Difference-encoded sine: 16–32 bytes
- No multiplication or reciprocal tables (use shift-and-add inline)

See [size_coding.md](size_coding.md) for the size-coding approach.

### 7.1 When tables are swapped in/out

For multi-part demos, tables can be **loaded per-part** from disk. Part 1 might need only a sine table; part 2 might need sine + multiplication + reciprocal. Loading tables per-part keeps each part's RAM budget low.

The Soviet demo framework (see [soviet_demo_scene.md](soviet_demo_scene.md) §5.5) is built around this: each part is essentially a standalone program, loaded fresh from disk with its own tables.

---
## 8. Self-Modifying Code and Code-as-Table

A advanced technique: when both code and table memory are tight, the demo can use **the same bytes as both code and data**. This is sometimes called "code-as-data" or "data-as-code".

### 8.1 The RST trick

The Z80's `RST` instructions (1-byte calls to fixed low memory addresses) can be used as both a code sequence and as the first byte of a small data table:

```z80
        ORG     0x8000
start:  RST     0x10           ; 0xD7 byte
        DB      data_bytes...
```

If `RST 0x10` is set up to do useful work (return, increment a counter, etc.), the byte `0xD7` is both a called instruction and a marker in a data stream.

This is rare outside 1K intros. See [size_coding.md](size_coding.md) for details.

### 8.2 The table-is-code trick

A sine table can sometimes be designed so its bytes are also valid Z80 instructions. For example, the values `0x00` (`NOP`), `0x40` (`LD B,B`), `0x48` (`LD C,C`), `0x50` (`LD D,D`), `0x58` (`LD E,E`), `0x60` (`LD H,H`), `0x68` (`LD L,L`) are all effectively no-ops and form a smooth sine wave when scaled appropriately.

By designing the table to be a valid (if bizarre) code sequence, the demo can run the table as code and use its existence as data — saving the bytes that would otherwise be separate.

### 8.3 Self-modifying address pointers

A more practical SMC pattern: the demo loads a fresh address into a `LD A,(nnnn)` instruction's `nnnn` field each frame:

```z80
        LD      HL,(frame_addr)   ; address updated per frame
        LD      (smc_load+1),HL   ; patch the next LD's address field
smc_load:
        LD      A,(0x0000)         ; the address is rewritten each frame
```

This is how most multicolor effects index into per-frame attribute buffers. The buffer pointer is updated by writing to the instruction's operand bytes.

### 8.4 Tradeoffs of SMC

Self-modifying code is:

- **Faster** than reloading pointers through registers in some cases.
- **Harder to debug** because the code changes at runtime.
- **Forbidden in ROM** (obviously — the Spectrum's lower 16K is ROM, but the upper RAM is writable).

Most demos use SMC only where it has clear value (the address-pointer trick above), not as a general technique.

---

## 9. Practical Examples

This section walks through how precomputed tables enable four classic Spectrum effects.

### 9.1 Plasma

A plasma is a smoothly-varying color field. The classic formula:

```
colour(x, y, t) = sin(x/16 + t) + sin(y/24 + t) + sin((x+y)/32 + 2t)
```

Implementation on Spectrum:

- Precompute a 256-entry 8-bit sine table (256 bytes).
- Per frame, for each attribute cell (768 cells = 32×24):
  - Compute three sine lookups (different step sizes).
  - Sum the sines, scale, and use as an index into a color palette.
- Cost per cell: ~40 T-states × 768 cells = ~30000 T-states. Tractable at 50 Hz.

The plasma is **the canonical demonstration of precomputed sines**: without the table, this effect would be impossible.

### 9.2 Tunnel / wormhole

A tunnel renders a 2D image of receding rings. Each pixel `(x, y)` is mapped to:

```
distance = constant / sqrt(x² + y²)
angle = atan2(y, x) + t
```

Then `(distance, angle)` indexes into a texture pattern.

Implementation:

- Precompute `sqrt(x² + y²)` table indexed by radius (256 bytes).
- Precompute `atan2` table indexed by angle (256 bytes).
- Per frame, per pixel: two lookups + texture index lookup.
- Cost per pixel: ~30 T-states × 6144 framebuffer pixels = ~180000 T-states. Tractable.

### 9.3 3D rotation (single object)

A 3D object (e.g. a cube, pyramid, or icosahedron) with N vertices:

- Per frame: compute the rotation matrix (6 sine lookups + ~10 multiplies).
- Per vertex: 9 multiplies + 6 adds.
- Per face: 3 multiplies for normal + 1 for shading.
- Project: 1 reciprocal lookup + 2 multiplies.

For a 100-vertex object: ~100 × 20 = 2000 multiplies per frame ≈ 600000 T-states. This is achievable at ~5–10 fps on a 3.5 MHz Spectrum.

### 9.4 Vector shading (Gouraud-style)

For each face of the 3D object, compute the dot product of the rotated face normal with a fixed light direction. Use the dot product to select an attribute color for the face.

Precompute:

- Sine/cosine tables for the rotation.
- A 16-entry "brightness → color" table.

Per face per frame:

1. Rotate the face normal (matrix-vector multiply, 9 multiplies).
2. Dot product with light direction (3 multiplies + 2 adds).
3. Look up color in brightness table.
4. Fill the face's pixels with that color (or fill the face's attribute cell for fast shading).

This gives the "rotating shaded 3D object" effect that Soviet demos (Extreme, E-Mage) pioneered on the Spectrum in the late 1990s.

### 9.5 Summary of table-driven effects

| Effect | Tables needed | Per-frame cost (T-states) |
|---|---|---|
| Plasma | 8-bit sine | ~30000 |
| Wobbler | 8-bit sine | ~20000 |
| Tunnel | sqrt + atan2 + sine | ~180000 |
| Rasterbars | 8-bit sine | ~10000 |
| 3D rotation | 16-bit sine + square + recip | ~600000 |
| Vector shading | 3D rotation + color LUT | ~700000 |

The most expensive (vector shading) is on the edge of tractability. The cheapest (rasterbars) is essentially free. Every effect above relies on precomputed tables to fit in the frame budget.

---
## 10. Cross-References and License

### 10.1 Articles in this section

- [effects_catalog.md](effects_catalog.md) — full catalog of effects using the tables documented here (plasma, tunnel, 3D rotation, etc.).
- [size_coding.md](size_coding.md) — table compression for 1K/4K intros, where the techniques in §4 are essential.
- [multicolor_techniques.md](multicolor_techniques.md) — multicolor effects use SMC address pointers (§8.3) heavily.
- [demo_frameworks.md](demo_frameworks.md) — typical demo framework loads tables per part (§7.1).
- [demoscene_platforms.md](demoscene_platforms.md) — comparison of how other 8-bit scenes handle trigonometry (most do the same thing; the MSX's VDP indirection makes table-driven effects harder).
- [soviet_demo_scene.md](soviet_demo_scene.md) — the Soviet 3D tradition relies on the techniques in §5–§6.
- [compression_packing.md](compression_packing.md) — tables can be packed (e.g. quarter-wave sines are themselves a form of compression).
- [notable_demos.md](notable_demos.md) — landmark demos that pushed table-driven effects.

### 10.2 CPU documentation

- [../01_cpu/z80_instruction_set.md](../01_cpu/z80_instruction_set.md) — full Z80 instruction set reference.
- [../01_cpu/README.md](../01_cpu/README.md) — Z80 architecture overview, including register usage conventions relevant to table-driven code.

### 10.3 Hardware context

- [../02_hardware/original/ula_timing.md](../02_hardware/original/ula_timing.md) — ULA timing details, relevant to cycle-counted multicolor lookups.
- [../02_hardware/clones/clone_timing.md](../02_hardware/clones/clone_timing.md) — Pentagon vs Sinclair timing differences affect table-driven raster effects.

### 10.4 External references

- **Helmar Hartmann**, "Tables and fixed-point on Z80" — series of articles in *ZX-Format* and *Spectrofon* diskmags (1997–1999). Primary Soviet-era reference.
- **John Metcalf**, "Z80 fixed-point routines" — published code library.
- **Shiru**, "Programming ZX Spectrum" — modern Russian-language tutorial covering table-driven effects extensively.
- **z80-heaven** (GitHub) — open-source Z80 demo code collection with extensive table-driven routines.
- **SXBJ (Spectrum X BJ)**, "8-bit multiply routines" — benchmark comparisons of various `MUL8` implementations.

### 10.5 The math behind the choices

For readers who want to understand *why* a 256-entry sine table gives 1.41° resolution (360° / 256), or *why* Q4.4 has step 1/16, the standard references are:

- **Knuth, TAOCP vol. 2** — fixed-point arithmetic fundamentals.
- **Hacker's Delight (Henry S. Warren, Jr.)** — bit-level arithmetic tricks applicable to Z80.
- **IEEE 754** — for understanding why fixed-point is preferred on 8-bit CPUs (no FPU, no instruction-level support for normalisation).

---

## License

This article is released under the **Creative Commons Attribution-ShareAlike 4.0 International License** ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)). You are free to share and adapt the material, provided you credit the original source and license derivative works under the same terms.

The Z80 instruction-cycle counts cited in the article are derived from the official Zilog Z80 CPU Product Specification (datasheet) and Christian Bauer's "Zilog Z80 CPU" reference; these are factual.
