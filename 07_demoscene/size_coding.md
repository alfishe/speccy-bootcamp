[← Home](../README.md) · [Demoscene](README.md)

# Size Coding — 1K / 4K / 16K Intro Competitions

> **Scope**: This article covers **size-limited intro competitions** — the demoscene tradition of building a complete audiovisual production in 256 bytes, 1 kilobyte, 4 kilobytes, or 16 kilobytes. It is the practical companion to [compression_packing.md](compression_packing.md) (the compressors used in the final squeeze), [effects_catalog.md](effects_catalog.md) (which effects fit in tight limits), and [z80_undocumented.md](../01_cpu/z80_undocumented.md) (the alternative encodings size-coders exploit).
>
> The article is descriptive rather than tutorial: it explains what techniques exist, why they work, and how much they save. Full working source for each trick is out of scope; refer to the source releases of the intros cited in [notable_demos.md](notable_demos.md).

---

## Article Roadmap

- §1 — Why size coding matters: the philosophy and history.
- §2 — Competition categories: 256B, 1K, 4K, 16K rules and traditions.
- §3 — The 256-byte barrier: what is and isn't possible at the extreme.
- §4 — Sub-1K techniques: the toolkit for 256B and 1K intros.
- §5 — Squeeze tricks: overlapping registers, RET tricks, ALU dual-use.
- §6 — Reuse tricks: the BASIC ROM as a free library.
- §7 — Math tricks: 8-bit LUTs, parallax, SMC generators.
- §8 — Compressing code: when and how to apply ZX0 + depacker.
- §9 — Notable 1K/256B Spectrum intros.
- §10 — Cross-references.

---

## 1. Why Size Coding Matters

Size-limited intros are one of the demoscene's oldest and most respected disciplines. Where a megademo might be 32 KB or more of densely-packed code, a 1K intro must fit the same kind of effects — plasma, tunnel, rotozoom, music — into **1,024 bytes**, less than the size of this article's header.

### 1.1 The Appeal

Three reasons size coding endures as a competition category:

1. **Purity of craft**. With no room for wasted bytes, every instruction earns its place. There is no padding, no redundancy, no "good enough." The code is stripped to its essential form.
2. **Reproducibility**. A 256-byte intro fits in a tweet, on a business card, in a QR code. The full binary can be read and understood in an afternoon.
3. **Cross-platform comparability**. Because the rules are byte-count based, a 1K intro on the ZX Spectrum can be compared directly to a 1K intro on the C64, Atari ST, or PC. The discipline transfers across architectures.

### 1.2 A Brief History

The size-coding tradition predates the demoscene itself. Early crack intros (1985–1987) had to fit in the few bytes between the disk bootloader and the game's load address — typically 100–200 bytes for the intro code. When groups started competing on intro quality rather than cracking speed, the **256-byte intro** became a natural category: it was the smallest unit that still allowed a recognisable visual effect.

The **1K intro** emerged on the 8-bit platforms around 1988 and became a standard party category by 1990. The **4K intro** came later (1993–1994) as 16-bit platforms (Amiga, Atari ST) needed more room for graphics data; the ZX Spectrum never had a strong 4K tradition because the platform's 16K base model already felt like a "small" target. The **16K intro** is essentially a "small megademo" — common on the Pentagon 128K and TS-Config, less common on stock 48K hardware.

### 1.3 What Fits in Each Size

A rough budget for what each category enables on the ZX Spectrum:

| Size | What fits | Famous examples |
|---|---|---|
| **256 bytes** | One static effect (plasma, raster bars, simple zoom), no music | various 256B party entries |
| **1K** | One or two effects, beeper music or silent, no precomputed tables | many 1K entries 1990–present |
| **4K** | Several effects, full AY music, some precomputed tables | mid-tier party intros |
| **16K** | Multi-part intro, full PT3 music, multiple effects with transitions | "small megademos" |

The 16K category is rare on stock Spectrum hardware because it overlaps with the 48K "demo" category. Where 16K competitions appear on the Spectrum they typically target the **128K/+2** models and allow banked memory.

---

## 2. Competition Categories

### 2.1 256 Bytes

The 256-byte intro is the **most constrained** recognized category. On the Z80, 256 bytes is roughly:

- 50–80 instructions of "naive" code, or
- 100–150 instructions of carefully size-optimized code, or
- 30–50 instructions plus a small data table.

What 256 bytes can achieve:
- A **plasma** effect using `AND`/`XOR` arithmetic on screen addresses.
- A **raster bar** sequence (border-only, port `#FE` writes per scanline).
- A **text scroll** using the ROM font (loaded from `#3D00` on the 48K).
- A **rotating cube** wireframe with vertices hardcoded.

What 256 bytes cannot easily achieve:
- Any form of multicolor (the engine alone is too large — see [multicolor_techniques.md](multicolor_techniques.md)).
- AY music (the smallest AY players are ~200 bytes, leaving no room for the player data).
- More than one effect (no room for a transition or sequencer).

#### Rules Traditions

Most parties follow the **"true 256 bytes"** convention:
- The final binary must be ≤256 bytes including any header, depacker, and data.
- Self-extracting compression is allowed: the compressed file is 256 bytes; it may expand to any size in RAM.
- BASIC loaders are allowed but their size is **counted** in the 256-byte budget.
- The intro must be loadable on stock hardware (typically the 48K or 128K, depending on the party).

### 2.2 1 Kilobyte

The **1K intro** is the canonical size-coding category. 1,024 bytes is roughly 4× the budget of a 256B intro, enough to:

- Run two or three effects with a simple sequencer (~50 bytes for the sequencer).
- Include a beeper music loop (~150 bytes for the smallest beeper players — Roman Borisenko's `beeperfx`, `pti`, or Shiru's `qxplayer`).
- Use small precomputed tables (a 64-byte sine table, an 80-byte screen-offset table).
- Apply mild self-modifying code to share instructions between effects.

What still doesn't fit comfortably:
- Full AY music (the smallest PT3 player is ~700 bytes; only ~300 remain for the visual).
- Multicolor effects (the rewrite engine alone is ~400 bytes; only ~600 remain).
- A complete compressed payload that decompresses into multiple parts (compression helps but depackers cost 50–100 bytes).

#### Standard Party Rules

1K rules are largely standardized across parties:
- The final binary must be ≤1,024 bytes.
- The intro must run on the platform it is submitted for (ZX Spectrum 48K, 128K, or Pentagon, depending on the party).
- Self-extracting compression (typically [ZX0](compression_packing.md)) is allowed.
- A BASIC loader is allowed and is **not** counted against the budget on most parties (it is a separate file on the disk/tape).

The Spectrum-specific tradition is that 1K intros are typically **silent** or use beeper sound, because AY player overhead would consume most of the budget. AY-based 1K intros exist but are rare and use custom mini-players rather than the full PT3 engine.

### 2.3 4 Kilobytes

The **4K intro** is the bridge category between intros and demos. 4,096 bytes is enough for:

- A small AY player (~700 bytes for a stripped PT3, ~300 bytes for a custom minimal player).
- A 1–2 KB module of music data.
- Multiple effects with proper sequencing and fade transitions.
- Small precomputed tables (sine, screen offsets, multiplication).

The 4K category is **less common on the ZX Spectrum** than on the Amiga or PC, because:
- The 48K Spectrum's "small demo" tradition uses the full 16K–40K range — 4K feels artificially constrained.
- The Pentagon 128K's banking makes 4K an awkward size (smaller than one RAM bank).
- Most sceners either go "all the way down" to 1K or up to the unlimited category.

When 4K Spectrum intros do appear, they typically target the **Pentagon 128K** and use banked memory to get more than 4K of usable space across the lifetime of the intro. Loading data from a bank that isn't counted in the 4K limit is sometimes permitted, sometimes not — party-specific.

### 2.4 16 Kilobytes

The **16K intro** is essentially the "small megademo" category. 16,384 bytes is enough for:

- Full PT3 music with player (~1.5 KB) plus a sizable module (~3–5 KB).
- 5–10 minutes of sequenced visual effects.
- Precomputed tables for all standard effects (sine, projection, screen offsets).
- A proper multi-part framework with text overlays and transitions.

On the **48K Spectrum**, 16K is a meaningful constraint because the screen memory consumes 6.9 KB of the 16 KB lower RAM — leaving only ~9 KB for code, music, and data. This makes 16K a genuine "tight" category on the 48K, where every byte competes with the screen.

On the **128K/+2/Pentagon**, 16K intros are common because the banking hardware makes it trivial to swap code in and out of the 16K window at `#C000`. The 16K limit then refers to the "main code" size, with banked data loaded on demand.

#### The 16K/48K Historical Note

The original ZX Spectrum 16K model (1982–1984) was the **first mass-market 16K computer** in the UK. Early Spectrum software (1982–1983) was constrained to 16K and developed the techniques that 16K intro competitions later canonised: small AY-less music, table-driven animation, self-modifying code. When 48K Spectrums became standard in 1984, the 16K techniques were largely forgotten — only to be revived by the demoscene in the 1990s as a deliberate art form.

---

## 3. The 256-Byte Barrier

The 256-byte intro is small enough that the entire binary fits in the same address space as a single Z80 register pair indexed by `L` or `H`. There is no room for abstractions — no functions, no structures, no commenting convention. Every byte is either an instruction, a data literal, or a self-modifying target.

### 3.1 The Instruction Budget

A "typical" 256-byte intro contains, after compression:

- ~80–100 bytes of effect code (one effect).
- ~30–50 bytes of player/setup (set stack pointer, clear screen, set up ports, install ISR if needed).
- ~20–40 bytes of inlined data (sine samples, screen offsets, palette bytes).
- ~30–80 bytes of compression overhead (a ZX0 depacker is 65–90 bytes depending on variant).

That leaves **no room for a sequencer**, no room for transitions, and no room for music unless the music is generated algorithmically (e.g. a one-line `OUT (#FE),A` driven by a counter).

### 3.2 The Canonical 256-Byte Skeleton

Most 256-byte Spectrum intros reduce to the following skeleton:

```z80
                ORG  #5E00           ; anywhere above the screen
    start:
                DI                   ; 1 byte
                LD   SP,#FF00        ; 3 bytes — stack at top of RAM
                LD   HL,#4000        ; 3 bytes — screen base
                LD   DE,#4001        ; 3 bytes
                LD   BC,#1800        ; 3 bytes — 6144 bytes
                LD   (HL),L          ; 1 byte — clear to zero (L=0)
                LDIR                 ; 2 bytes
                ; ... effect loop ...
    loop:
                ; <~60-100 bytes of effect code>
                JR   loop            ; 2 bytes
```

That is **~18 bytes** for the prologue, leaving ~238 bytes for the effect itself. With a 65-byte ZX0 depacker at the front, the available effect code drops to **~170 bytes**. Working within that budget is the entire art of the 256-byte intro.

### 3.3 What 256 Bytes Can Express

A non-exhaustive list of effects that have been demonstrated in ≤256 bytes on the Spectrum:

- **Mandelbrot plot** (fixed-point integer arithmetic, 16-bit fixed, 64×48 cells).
- **Plasma** (XOR-based, no sine table — see §7).
- **Raster bars** (border-only, port `#FE` writes synchronized to INT).
- **Sierpinski triangle** (chaos-game: 3 fixed points, random walk).
- **Text scroll** using the 48K ROM font at `#3D00`.
- **Rotating wireframe cube** (vertices hardcoded, projection in 16-bit).
- **1-bit beeper tone** (a counter-driven `OUT (#FE),A` loop, no envelope, no music).

What 256 bytes has **never** achieved on stock Spectrum hardware, as of 2024:

- Any **multicolor** effect (the rewrite engine is ~400 bytes minimum).
- Any **AY music** (the smallest working AY loop is ~180 bytes, leaving no room for visual).
- Any **3D filled-polygon** renderer (the polygon scan converter alone is ~300 bytes).
- A **two-effect** intro with a transition (no room for the transition code).

### 3.4 The 256B Aesthetic

The 256-byte intro has developed its own aesthetic, distinct from larger intros:

- **Static single effect**, no narrative arc.
- **Repetition as feature**: because no time is left for variation, the effect is whatever the loop produces, run forever.
- **Algorithmic music**: rather than store notes, the music is generated by a counter or LFSR — see [1bit_music_scene.md](1bit_music_scene.md).
- **Heavy reliance on initialised RAM state**: many 256B intros start with the screen memory in its power-on state (garbage) and treat that garbage as a feature.

The result is an art form that values **density of idea over polish of presentation**. A 256-byte intro that produces a recognisable Mandelbrot set is considered impressive; a 1K intro that does the same is considered routine.

---

## 4. Sub-1K Techniques

The techniques used in 256-byte and 1K intros form a distinct toolkit, separate from "ordinary" Spectrum optimisation. This section introduces the toolkit; the next four sections (§5–§8) develop each family in detail.

### 4.1 The Toolkit Overview

| Family | Idea | Typical saving | Where covered |
|---|---|---|---|
| **Squeeze** | Replace multi-byte instructions with shorter alternatives; reuse registers as both data and control. | 1–3 bytes per site | §5 |
| **Reuse** | Call into the 16K BASIC ROM as a free library of arithmetic, string, and screen routines. | 20–200 bytes total | §6 |
| **Math** | Generate tables at runtime; use small LUTs; trade time for space. | 50–300 bytes | §7 |
| **Compression** | Run ZX0 on the assembled binary; ship the depacker + compressed payload. | 30–60% of binary | §8 |

These families are not orthogonal. A good 256-byte intro typically combines all four: the source is squeezed, the code calls ROM routines, tables are generated at runtime, and the final binary is compressed.

### 4.2 The Mental Model

Size-coding requires a different mental model from ordinary Z80 programming:

1. **Every instruction is costed in bytes, not T-states.** Speed matters only secondarily; many 256B intros run at 5–10 Hz and that is acceptable.
2. **RAM state is free; ROM code is free; only the loaded binary is budgeted.** Anything that can be computed from RAM or called from ROM is free.
3. **Side effects are features.** An instruction that destroys a register or sets a flag may be useful later. The "natural" choice of instruction is often the one that leaves the right side effect for the next consumer.
4. **Self-modifying code is the default, not the exception.** A loop that rewrites its own operand each iteration is smaller than a loop with indexed addressing.

### 4.3 Trade-offs vs Ordinary Optimisation

Ordinary Z80 optimisation (see [z80_coding_practices.md](../01_cpu/z80_coding_practices.md)) prioritises **speed** — replacing slow instructions with faster equivalents, unrolling loops, using tables. Size coding inverts the priority:

| Ordinary optimisation | Size-coding equivalent |
|---|---|
| Unroll loops for speed | Loop with `DJNZ`, even if slower |
| Precompute tables in RAM | Compute on-the-fly with `RRA`/`ADD A,A` |
| Use direct screen addressing via `LD HL,(addr)` | Self-modify the address literal in-place |
| Inline common subroutines | `RST #10`/`CALL` into a shared routine, even at speed cost |
| Use `LD A,(HL)`/`INC HL` pairs | Use `LD A,(HL+)` (HL auto-increments, 1 byte saved) |
| Avoid undocumented opcodes | Embrace `LD F,A`/`LD A,F`, `LD (HL),r` aliases, SLL |

The size coder's maxim: **"Bytes first, T-states second, RAM third."** Time is the one resource that 256 bytes can afford to spend.

### 4.4 The Stages of a Size-Coded Intro

A typical 1K intro development cycle, in order:

1. **Prototype** the effect in unconstrained code (~2–4 KB). Verify it works.
2. **Squeeze**: replace naive sequences with shorter alternatives (§5). Target: ~1.5 KB.
3. **Refactor to ROM reuse**: identify calls into the BASIC ROM and replace custom routines (§6). Target: ~1.2 KB.
4. **Table removal**: replace precomputed tables with runtime generation (§7). Target: ~1.05 KB.
5. **Compress**: assemble, run ZX0 on the binary, prepend the depacker (§8). Final: typically 600–900 bytes, well within the 1K budget.

For a 256-byte intro, the same cycle targets ~400 bytes pre-compression, ~250 bytes post-compression.

---

## 5. Squeeze Tricks

**Squeezing** is the process of replacing multi-byte instruction sequences with byte-equivalent or byte-smaller alternatives that achieve the same effect. The Z80's instruction set is dense enough that almost every common operation has at least two encodings, and size-coding exploits this density systematically.

### 5.1 The Shorter-Alternative Table

A reference of the most common substitutions:

| Naive (longer) | Squeezed (shorter) | Saved | Notes |
|---|---|---|---|
| `LD A,0` (2 bytes) | `XOR A` (1 byte) | 1 | Also clears carry |
| `LD A,#FF` (2 bytes) | `OR A`/`CPL` after `XOR A` (2 bytes) | 0 | Same size but different side effects |
| `LD A,(nn)` (3 bytes) | `LD A,(HL)` (1 byte) | 2 | Requires HL pointing at address |
| `LD (nn),A` (3 bytes) | `LD (HL),A` (1 byte) | 2 | Requires HL pointing at address |
| `LD HL,nn` (3 bytes) | `LD H,n`/`LD L,n` (4 bytes) | -1 | Avoid — always longer |
| `LD HL,(nn)` (3 bytes) | `LD H,(HL)`/`INC HL`/`LD L,(HL)` (3 bytes) | 0 | Same size but uses HL |
| `INC HL` (1 byte) | `INC H`/`INC L` (2 bytes) | -1 | Avoid |
| `ADD HL,HL` (1 byte) | SLA H/RL L (4 bytes) | -3 | Always use `ADD HL,HL` |
| `LD A,B` then `CP 0` (3 bytes) | `OR B` (1 byte) | 2 | `OR B` sets Z flag if B=0 |
| `LD A,B`/`AND A` (2 bytes) | `LD A,B`/`OR A` (2 bytes) | 0 | Equivalent; OR A is more idiomatic |
| `JP nn` (3 bytes) | `JR` (2 bytes) | 1 | ±127 byte range only |
| `JP (HL)` (1 byte) | — | — | Already 1 byte; useful for computed jumps |
| `CALL nn`/`RET` (5 bytes) | `RST n`/`RET` (2 bytes) | 3 | Limited to 8 vectors |

A size-coder develops fluency in this table through practice; after a few months, the shorter alternative becomes the "default" form in muscle memory.

### 5.2 The RET Trick — Push Address, Then Return

The Z80's `RET` instruction pops a 16-bit value from the stack and jumps to it. This means a sequence:

```z80
    LD   HL,target
    PUSH HL
    RET
```

performs an unconditional jump to `target` in 6 bytes — not impressive. But the equivalent for a function call:

```z80
    LD   HL,function
    PUSH HL
```

schedules a "call" to `function` that will happen when the current routine returns. This is the basis of the **RET trick**: a single `RET` at the bottom of a routine can dispatch to an arbitrary address pushed earlier. The trick saves bytes when:

- A function needs to return to one of several addresses depending on flags.
- Two routines share a common epilogue.
- A jump table is implemented by pushing entries.

Worked example — a routine that either increments or decrements HL based on carry, then jumps to a fixed continuation:

```z80
; Naive (7 bytes):
process:
    JR   NC,dec_case
    INC  HL
    JR   done
dec_case:
    DEC  HL
done:
    JP   continuation

; Squeezed with RET trick (5 bytes):
process:
    PUSH HL              ; schedule "continuation" via stack
    LD   HL,continuation
    EX   (SP),HL         ; HL now has old HL, stack has continuation
    JR   NC,dec_case
    INC  HL
    RET                  ; pops continuation, jumps there
dec_case:
    DEC  HL
    RET                  ; pops continuation, jumps there
```

The RET trick shines when a routine is called from many sites that each want their own continuation: each caller pushes its own continuation before calling, and the routine just `RET`s.

### 5.3 Register Dual-Use

In ordinary code, registers are typed: `A` is the accumulator, `B`/`C` are counters, `HL` is a pointer. In size-coded code, **all registers are interchangeable storage**, and the more you can do with a single register, the fewer `LD` instructions you need.

#### AF as 16-bit storage

The flags register `F` is normally read-only, but the **undocumented** `LD F,A` (opcode `#ED+reg`) and `LD A,F` opcodes let you use `AF` as a 16-bit pair. This is most useful when:

- `F` can hold a packed byte of state across a `CALL`.
- `A` needs to be saved cheaply: `EX AF,AF'` (1 byte) swaps the entire `AF` with the shadow `AF'`, much cheaper than `PUSH AF`/`POP AF` (3 bytes total).

See [z80_undocumented.md](../01_cpu/z80_undocumented.md) for the full list of undocumented instructions.

#### IX/IY as 8-bit pairs

The index registers `IX` and `IY` can be split into high and low 8-bit halves via undocumented opcodes (`#DD`/`#FD` prefixes on `LD r,r'` instructions). This effectively gives the programmer **four extra 8-bit registers** (`IXH`, `IXL`, `IYH`, `IYL`) at the cost of one prefix byte per access.

```z80
; Using IX as two 8-bit counters:
    LD   IXH,8           ; 3 bytes (#DD prefix + 2-byte instruction)
    LD   IXL,16          ; 3 bytes
loop_outer:
    ; ... outer loop body ...
loop_inner:
    ; ... inner loop body ...
    DEC  IXL             ; 2 bytes
    JR   NZ,loop_inner   ; 2 bytes
    DEC  IXH             ; 2 bytes
    JR   NZ,loop_outer   ; 2 bytes
```

This is **2 bytes per counter access** vs 1 byte for `B` or `C`, but it provides counters that don't conflict with `BC` or `DE`.

### 5.4 ALU Dual-Use

The 8-bit ALU instructions (`AND`, `OR`, `XOR`, `ADD`, `SUB`, `ADC`, `SBC`) each produce **two outputs simultaneously**: the arithmetic result in `A`, and the flags in `F`. In ordinary code, the programmer typically uses one and ignores the other. In size-coded code, both outputs are consumed.

Worked example — read a byte from `(HL)`, mask off the high nibble, AND branch if the result is zero, all in 2 bytes:

```z80
; Naive (4 bytes):
    LD   A,(HL)
    AND  #0F
    JR   Z,zero_case

; Squeezed (4 bytes but the AND reads (HL) directly):
    AND  #0F             ; assumes A = (HL) already, or use:
    ; Actually the classic squeeze:
    LD   A,(HL)          ; 1 byte
    AND  A               ; 1 byte — redundant if AND #0F already set flags
    ; The real trick:
    AND  (HL)            ; 1 byte — A = A AND (HL), sets Z flag
    JR   Z,zero_case     ; 2 bytes
```

The classic dual-use: `AND A` (1 byte) does not change `A` but **sets flags based on A**, useful for testing A without `CP 0`. Similarly `OR A` clears carry without changing A — handy before `SBC` operations.

### 5.5 Drop the High Byte

When an address has a known high byte (e.g. all screen addresses start with `#40`–`#5A`), the high byte can be a constant loaded once, with only the low byte updated per access:

```z80
; Naive (3 bytes per access):
    LD   HL,#5800        ; 3 bytes — attribute row 0
    LD   (HL),A
    LD   HL,#5820        ; 3 bytes — attribute row 1
    LD   (HL),A

; Squeezed (1 byte per access after first):
    LD   H,#58           ; 2 bytes — high byte constant
    LD   L,#00           ; 2 bytes
    LD   (HL),A          ; 1 byte
    LD   L,#20           ; 2 bytes
    LD   (HL),A          ; 1 byte
```

Savings compound across hundreds of screen accesses.

### 5.6 Overlapping Instructions

The most aggressive squeeze: arrange the binary so that the operand byte of one instruction is the opcode of another. The Z80 has no alignment requirement, so jumping into the middle of a multi-byte instruction reinterprets the operand bytes as code.

Classic example — the `LD BC,nn` (3 bytes, `#01 nn nn`) and `LD C,n` (2 bytes, `#0E n`) share the `nn` operand. If `LD BC,#0E01` is followed by code that `JP`s into the second byte, the CPU sees `LD C,#01` instead.

```z80
table_or_code:
    LD   BC,#0E01        ; bytes: 01 0E 01
    ; if we JP to table_or_code+1, we execute:
    ;   #0E 01 = LD C,01   (2 bytes, then continues)
```

This trick is fragile — any change to the surrounding bytes shifts the alignment — and is usually applied last, after all other optimisations. It can save 1–5 bytes in a tight intro but is rarely worth the debugging cost. **Document any overlap extensively**, as the next reader will not see the dual interpretation.

### 5.7 The Self-Clear Idiom

A family of one-byte idioms that achieve common effects:

| Instruction | Bytes | Effect |
|---|---|---|
| `XOR A` | 1 | `A = 0`, carry = 0, sets flags |
| `OR A` | 1 | `A` unchanged, carry = 0, sets flags |
| `AND A` | 1 | `A` unchanged, carry = 0, sets flags |
| `CPL` | 1 | `A = ~A` |
| `NEG` | 2 | `A = -A` |
| `SCF` | 1 | carry = 1 |
| `CCF` | 1 | carry = !carry |

`XOR A` is the most-used: it replaces the 2-byte `LD A,0` while also clearing carry, which is often what the surrounding code wants. A size-coder's instinct is to reach for `XOR A` any time a zero is needed.

### 5.8 Squeeze Workflow

The squeeze stage is iterative. A typical workflow:

1. Assemble the source. Note the binary size.
2. Scan for any 2-byte `LD A,n` where `n` could be produced by a 1-byte ALU op (`XOR A`, `CPL`, etc.).
3. Scan for any 3-byte `LD A,(nn)` where `HL` is already pointing at `nn` (or could be made to).
4. Scan for any 3-byte `JP nn` within ±127 bytes — replace with `JR`.
5. Scan for any `PUSH`/`POP AF` pair that could be `EX AF,AF'` (saves 1 byte).
6. Re-assemble, repeat until the savings per pass drop below 1 byte.

A skilled squeezer typically achieves a **20–30% reduction** at this stage before moving on to ROM reuse (§6) and table generation (§7).

---

## 6. Reuse Tricks — The BASIC ROM as a Library

Every ZX Spectrum ships with a **16 KB BASIC ROM** at `#0000`–`#3FFF` containing the entire Sinclair BASIC interpreter: tokeniser, editor, screen driver, floating-point calculator, keyboard scanner, cassette I/O, and more. From a size-coder's perspective this is **16 KB of free code** — pre-installed, pre-tested, and accessible via `CALL` or `RST`. Replacing custom routines with ROM calls can save hundreds of bytes in a 1K intro.

### 6.1 ROM Routine Categories

The ROM contains roughly four categories of useful routines:

1. **Screen routines** — clear screen, print character, scroll, set attribute.
2. **Keyboard routines** — read key, decode key, wait for key.
3. **Calculator routines** — 5-byte floating-point arithmetic, including sine, cosine, square root.
4. **Cassette routines** — block loader, byte loader, header parser.

For size coding, categories 1–3 are the most useful. Category 4 is occasionally used to load compressed data blocks from tape after the intro has started — a way to "cheat" the size limit on parties that allow tape/disk data outside the binary.

### 6.2 The Most-Used ROM Routines

A short list of routines that appear in nearly every size-coded Spectrum intro:

| Address | Name | Function | Bytes saved vs custom |
|---|---|---|---|
| `#0DAF` | `CL-ALL` | Clear screen + attributes + set defaults | ~30 |
| `#0E44` | `CL-CHAN` | Close all channels (setup helper) | ~10 |
| `#09F4` | `PRINT-A-1` | Print the character in A at current cursor | ~80 |
| `#0C0A` | `SET-DE` | Copy 8 bytes from `(HL)` to `(DE)` | ~10 |
| `#03B5` | `BEEPER` | Make a sound: B=pitch, C+D duration | ~50 |
| `#028E` | `KEY-SCAN` | Scan keyboard into `LAST-K` system variable | ~30 |
| `#10E1` | `TOKENS` | Print a tokenised string | ~30 |
| `#1A1B` | `BC-SPACES` | Reserve BC bytes on workspace | ~15 |
| `#15DE` | `FP-TC-2` | Push a constant onto FP calculator stack | ~20 |
| `#0333` | `KEY-TEST` | Test if a specific key is pressed | ~30 |

A single `CALL #0DAF` (3 bytes) replaces ~30 bytes of custom screen-clearing code. A `CALL #03B5` (3 bytes) replaces a 50-byte beeper routine. Compounded across an intro, ROM reuse can shave 200+ bytes — a fifth of the 1K budget.

### 6.3 Print-Char Pattern

The most-quoted size-coding pattern: print the ROM font directly using `PRINT-A-1`:

```z80
; Print the byte in A at the current cursor position
print_char:
    CALL #09F4             ; PRINT-A-1
    RET
```

Combined with cursor system variables `S-POSN` (`#5C88`) for positioning, this gives a size-coder a complete text output system in ~10 bytes, vs. ~250 bytes for a custom font renderer. The trade-off: the ROM font uses fixed 8×8 cells with the standard attribute model — no multicolor, no proportional width.

### 6.4 Clear-Screen Pattern

```z80
clear_screen:
    CALL #0DAF             ; CL-ALL — clears display file and attributes
    RET
```

`CL-ALL` performs:
1. Clears the display file (`#4000`–`#57FF`) to zero.
2. Clears the attribute file (`#5800`–`#5AFF`) to the current `ATTR-P` value (default: black ink on white paper).
3. Resets the cursor position to top-left.

This is **23 bytes of useful work for a 3-byte call**. For a 256-byte intro, replacing custom clear code with `CL-ALL` is the single biggest optimisation available.

### 6.5 Beeper Pattern

The 48K ROM contains a working 1-bit beeper routine at `#03B5` (`BEEPER`):

```z80
; Sound: HL = pitch (smaller = higher), DE = duration
play_beep:
    LD   HL,#0100          ; pitch
    LD   DE,#0100          ; duration
    CALL #03B5             ; BEEPER
    RET
```

This is **50 bytes of sound code for a 9-byte call sequence**. The catch: `BEEPER` is a blocking routine — it does not return until the sound completes. For continuous music, the size-coder must either use `BEEPER` once for a single tone or replace it with a custom interrupt-driven beeper player (which costs ~150 bytes, see [1bit_music_scene.md](1bit_music_scene.md)).

### 6.6 The Floating-Point Calculator

The 48K ROM contains a complete 5-byte floating-point calculator at the calculator stack (`STKEND` system variable, `#5C65`). The interface is the `FP-CALC` routine at `#1C9A`, which takes a "calculator literal" byte that selects an operation: `add`, `subtract`, `multiply`, `divide`, `sin`, `cos`, `tan`, `atn`, `ln`, `exp`, `sqr`, and more.

```z80
; Compute sin(x) where x is on the FP stack
    RST  #28               ; FP-CALC literal (1 byte)
    DEFB #A4               ; literal: sin
    DEFB #38               ; literal: end-calc
```

This is **8 bytes for a complete sine function** — vs. ~150 bytes for a custom fixed-point sine using a Taylor series or table lookup. The trade-off is **speed**: the FP calculator uses 5-byte floats with multi-byte arithmetic, and a single sine call takes ~10,000 T-states. For a 256-byte Mandelbrot that runs at 1 Hz, this is fine; for a 50 Hz effect, the FP calculator is unusable.

### 6.7 ROM Caveats

The 48K and 128K ROMs are **not binary-compatible** at every address. Sinclair rewrote large portions of the 128K ROM for the new banking hardware, and many routines moved:

| Routine | 48K address | 128K address | Notes |
|---|---|---|---|
| `CL-ALL` | `#0DAF` | `#10DAF` (banked) | 128K uses banked ROM page 0 |
| `PRINT-A-1` | `#09F4` | `#109F4` | Same |
| `BEEPER` | `#03B5` | `#103B5` | Same |
| `KEY-SCAN` | `#028E` | `#1028E` | Same |
| `FP-CALC` | `#1C9A` / `RST #28` | `RST #28` | Identical (RST entry) |

The Pentagon ROM is **derived from the 48K ROM** and most routines work at the same address. However, the Pentagon has no `BEEPER` contention behavior, so timing-dependent calls to `BEEPER` produce slightly different pitch.

#### The `RST #18`/`RST #28` Idiom

Two RST vectors are stable across all ROM variants:
- `RST #18` (= `CALL #0018`) — fetch the next byte from `CH-ADD` system variable. Useful for tokenising.
- `RST #28` (= `CALL #0028`) — enter the FP calculator with the literal byte after the call site.

RSTs are **1-byte calls** — the cheapest form of subroutine invocation on the Z80. Using `RST #28` to invoke the calculator saves 2 bytes over `CALL #1C9A` per invocation, which compounds quickly.

### 6.8 ROM Reuse Workflow

The reuse stage of size-coding is more analytical than the squeeze stage:

1. **Inventory the intro's needs**: screen clear, print, beep, sine, multiply, divide, key-read.
2. **Map each need to a ROM routine** using a reference table (e.g. the well-known "ROM Disassembly" by Dr. Ian Logan and Dr. Frank O'Hara).
3. **Delete the custom routine** from the source.
4. **Insert the `CALL` or `RST`** at the call sites.
5. **Verify the routine's preconditions** (registers, system variables) are met.
6. **Re-assemble and test**.

A typical 1K intro that aggressively reuses the ROM can shed **200–400 bytes** at this stage. The result is often a binary that no longer contains any "infrastructure" code — only the effect logic and a few `CALL`s into the ROM.

### 6.9 When Not to Use the ROM

The ROM is not always the right answer. Common reasons to avoid a ROM call:

- **Speed**: ROM routines are slower than hand-rolled code tuned for the specific case.
- **Side effects**: a ROM call often changes system variables, registers, and the FP stack in ways that are expensive to undo.
- **Model dependence**: if the intro must run on 48K, 128K, and Pentagon, ROM addresses diverge and a single binary can't reuse them portably.
- **Contended timing**: on the 48K, ROM calls executed during paper area contend with the ULA and may break raster sync. (See [contention_model.md](../05_development/03_memory_and_io/contention_model.md).)

The 256-byte intro typically leans **hard** on the ROM. The 1K intro balances ROM calls with custom code. The 4K intro has enough room for hand-rolled everything, and ROM calls are rare.

---

## 7. Math Tricks

Math is the most expensive part of any size-coded intro. A 256-byte Mandelbrot needs multiplication, square, and absolute value; a 1K plasma needs sine; a 1K tunnel needs `atan2` and `1/sqrt(x²+y²)`. The naive implementation of these is far too large — sines from Taylor series run to 200+ bytes, fixed-point multipliers to 80+. The size-coder's alternative is **algorithmic math**: generate the values cheaply at runtime, use the cheapest approximation that looks right.

### 7.1 The XOR Plasma — No Sine Needed

The classic 256-byte plasma uses no sine table and no multiplication. The effect is generated by XOR-ing screen coordinates:

```z80
; For each screen address (HL), compute plasma value in A
    LD   A,H              ; high byte of address
    XOR  L                ; XOR with low byte
    ; A now contains a "plasma" pattern that depends on row and column
    LD   (HL),A           ; write back as pixel data
    INC  HL               ; next byte
    DJNZ loop
```

Why it works: XOR is symmetric around bit boundaries, producing a repeating but irregular pattern that **looks like** a sine-based plasma. Different XOR combinations (`H XOR L`, `H XOR L XOR t`, `H XOR L XOR (H+L) XOR t`) produce different plasma textures, all from 1-byte operations.

The XOR plasma is the canonical **"256-byte effect"** — it needs no tables, no multiplication, no division. It runs at full frame rate, fills the screen, and recognisably "does something". Many first-time size-coders cut their teeth on the XOR plasma.

### 7.2 Small Sine Tables

When the effect needs actual sine values, a size-coder uses the **smallest table that produces a usable result**. The standard sizes:

| Table size | Resolution | Useful range | Cost |
|---|---|---|---|
| 32 bytes | 11.25° per entry | 0°–360° | Crude — blocky curves |
| 64 bytes | 5.625° per entry | 0°–360° | Acceptable — recognisable shapes |
| 128 bytes | 2.8° per entry | 0°–360° | Good — smooth animations |
| 256 bytes | 1.4° per entry | 0°–360° | Excellent — full quality |

For a 256-byte intro, **32 bytes** is the maximum affordable sine. For 1K, **64 bytes** is the sweet spot. 128 and 256-byte tables appear only in 4K+ intros where memory is not the binding constraint.

#### Quarter-Wave Storage

A sine wave has fourfold symmetry: `sin(90+x) = sin(90-x)`, `sin(180+x) = -sin(x)`, `sin(270+x) = sin(270-x)`. Storing only the first quarter (0°–90°) and reflecting for the other three quarters reduces storage by 4×. A 64-byte full sine becomes a 16-byte quarter sine.

```z80
; Look up sin(x) in 0..255 (one full revolution) using a 64-byte quarter table
sin_lookup:
    LD   A,(angle)        ; 0..255
    CP   128              ; check second half
    JR   NC,neg_half
    CP   64               ; check second quarter
    JR   NC,second_q
    LD   L,A              ; first quarter: direct lookup
    LD   H,HIGH(sintab)
    LD   A,(HL)
    RET
second_q:
    ; reflect: index = 128 - A
    NEG
    ADD  A,128
    LD   L,A
    LD   H,HIGH(sintab)
    LD   A,(HL)
    RET
neg_half:
    SUB  128              ; reduce to 0..127
    ; ... mirror the first half logic, but negate the result ...
```

The look-up logic costs ~25 bytes but saves 48 bytes of table — net win of 23 bytes vs. a full 64-byte sine. See [precalc_trigonometry.md](precalc_trigonometry.md) §4.2 for the full pattern.

### 7.3 Runtime Table Generation

If a table cannot be afforded even at quarter-wave size, generate it at runtime. A sine table can be computed in ~40 bytes of code using a second-order difference equation:

```z80
; Generate a 64-byte sine in 0..255 using the recurrence:
;   y[n+1] = 2*cos(theta)*y[n] - y[n-1]
; where theta = 2*pi/64

gen_sine:
    LD   HL,sin_table
    LD   DE,#007F         ; initial value (mid-scale)
    LD   (HL),E
    INC  HL
    LD   B,63             ; 63 more values
    LD   C,#FD            ; y[n-1] initial = -3 (tuned)
gen_loop:
    ; compute new = (2*cos(theta)*y[n] - y[n-1]) / 256
    ; ... (about 15 bytes of arithmetic) ...
    DJNZ gen_loop
    RET
```

This **40-byte generator replaces a 64-byte table** — a 24-byte net saving. The trade-off is start-up time: the table is computed once at intro start, costing ~5,000 T-states. For an intro that runs for minutes, this is invisible.

### 7.4 Bit-Shift Multiplication

The Z80 has no hardware multiply — `MUL` does not exist. Multiplication must be implemented in software, but for size-coding the **shift-and-add** algorithm is sufficient and tiny:

```z80
; Multiply H * C, result in HL (8-bit inputs, 16-bit result)
mul8x8:
    XOR  A                ; A = 0, also clears carry
    LD   L,A              ; L = 0
    LD   B,8              ; 8 bits to process
mul_loop:
    ADD  HL,HL            ; shift HL left (1 byte)
    JR   NC,no_add
    ADD  HL,BC            ; add multiplicand if carry (2 bytes)
no_add:
    DJNZ mul_loop         ; (2 bytes)
    RET
```

This is **~10 bytes for a complete 8×8 multiply** — far cheaper than a 256-byte multiplication table (see [precalc_trigonometry.md](precalc_trigonometry.md) §5 for the table approach). The cost is **~250 T-states per multiply** vs. ~20 for a table lookup.

#### Constant Multiplication

For multiplications by a known constant (e.g. `* 6`, `* 10`, `* 12`), the binary decomposition is even cheaper:

```z80
; Compute HL = HL * 6 = HL * 4 + HL * 2 = (HL << 2) + (HL << 1)
mul_by_6:
    LD   D,H              ; save HL in DE
    LD   E,L              ; (2 bytes)
    ADD  HL,HL            ; HL = HL * 2  (1 byte)
    ADD  HL,DE            ; HL = HL * 3  (1 byte)
    ADD  HL,HL            ; HL = HL * 6  (1 byte)
    RET                   ; 5 bytes total
```

A size-coder keeps a mental list of which constants are cheap: powers of 2 (single shift), 3 (`x + x<<1`), 5 (`x + x<<2`), 6, 9, 10, 12, 15, 17. Each can be computed in 5–10 bytes.

### 7.5 Parallax from a Single Table

A parallax scroll shows several layers of background scrolling at different speeds. The naive implementation uses one table per layer. The size-coder uses **a single table, indexed by `(layer + time)`**:

```z80
; For each layer L (0, 1, 2, ...) and time T, look up:
;   offset[L][T] = table[(L * speed_L + T) mod table_size]
    LD   A,(time)
    ADD  A,L              ; add layer offset
    LD   L,A
    LD   H,HIGH(parallax_table)
    LD   A,(HL)           ; pixel offset for this layer
```

The single table can be 64 or 128 bytes and serves **N layers simultaneously**. This compresses a 3-layer parallax from ~600 bytes (per-layer tables) to ~80 bytes (one shared table + lookup code).

### 7.6 SMC Generators — Code That Writes Code

Self-modifying code at its most extreme: a small loop that **writes the body of another loop**, then jumps into the generated code. This is how size-coded intros perform operations that would otherwise need unrolled loops:

```z80
; Generate an unrolled "PUSH" sequence to fill a screen row
gen_pushes:
    LD   HL,push_target   ; address where code will be generated
    LD   DE,#C5C5         ; two PUSH BC bytes
    LD   B,16             ; generate 16 PUSHes
gen_loop:
    LD   (HL),D           ; write PUSH BC opcode
    INC  HL
    LD   (HL),E
    INC  HL
    DJNZ gen_loop
    LD   (HL),#C9         ; write RET at the end
    JP   push_target      ; jump to the generated code
```

The generator is ~15 bytes; the generated code is ~33 bytes. By generating rather than embedding, the intro pays only 15 bytes for the 33-byte payload — an 18-byte saving. The trade-off is RAM: the generated code must be written to writeable memory, and the intro cannot easily re-execute the generator if the generated code is overwritten.

### 7.7 Fast Atan2 and 1/Sqrt

The tunnel effect (see [effects_catalog.md](effects_catalog.md) §8) needs `atan2(dy, dx)` and `1/sqrt(dx² + dy²)` for each screen cell. Both are expensive — naive `atan2` is ~150 bytes, naive `1/sqrt` requires Newton-Raphson iteration at ~50 bytes.

Size-coded alternatives:

- **Atan2 approximation**: a 6-line binary-search or linear approximation. Cheapest is `A = (dy > dx) ? (dy + dx/2) : (dx + dy/2)` — produces a coarse octant-angle that is "good enough" for visual tunnels.
- **1/sqrt via shift-subtract**: a 15-byte iterative refinement. Result has ~4 bits of accuracy, sufficient for a tunnel texture lookup.

Both tricks are well-documented in the demoscene literature (see [notable_demos.md](notable_demos.md) for source releases that include tunnels).

### 7.8 Mandelbrot in 256 Bytes

The 256-byte Mandelbrot is a milestone: it demonstrates that even an iterative escape-time fractal can fit. The trick is to use **8-bit fixed-point arithmetic** throughout (no 16-bit multiply), accept a coarse 32×24 cell grid, and iterate at most 16 times per cell. The core loop fits in ~80 bytes:

```z80
mandel_loop:
    ; given cx, cy in 8-bit signed fixed-point
    ; zx = 0, zy = 0
    ; iterate: zx' = zx² - zy² + cx ; zy' = 2*zx*zy + cy
    ; escape when |zx|² + |zy|² > 4

    LD   B,16             ; max iterations
m_iter:
    ; compute zx² and zy² via 8x8 multiply (§7.4)
    ; ... ~20 bytes of arithmetic ...
    ; check escape condition
    ; ... ~5 bytes ...
    DJNZ m_iter
```

The 256-byte Mandelbrot is often the **benchmark** for size-coders — anyone who has written one is considered fluent.

---

## 8. Compressing the Final Binary

After squeezing, ROM reuse, and table generation, the size-coder reaches the **final stage**: running a byte-level compressor on the assembled binary and shipping a self-extracting payload. This is the technique that turns a 600-byte intro into a 350-byte intro, and a 1,100-byte intro into a 700-byte intro.

### 8.1 Why Compress Last

Compression is always applied **last**, after all manual optimisations, for three reasons:

1. **Compressors work on bytes, not on logic.** A compressor cannot squeeze out a redundant `LD A,0` — it can only squeeze out redundant byte patterns. Manual squeeze (§5) removes logic redundancy; compression removes byte redundancy.
2. **Compression is invisible at the source level.** Once compressed, the binary cannot be edited; the source must be edited, reassembled, and recompressed. Iterating on source-after-compression is wasteful.
3. **Compression has a fixed depacker cost.** A ZX0 depacker is ~65–90 bytes; this is a fixed overhead that must be paid before any compressed byte is decompressed. Below a certain binary size, the depacker cost exceeds the savings.

The order of operations is therefore: **squeeze → reuse → table-generate → assemble → compress**.

### 8.2 ZX0 — The Current Standard

**ZX0** (by Einar Saukas, 2017) is the de facto Spectrum size-coding compressor as of 2024. Its key properties:

- **Optimal** — provably finds the smallest compressed output for a given input.
- **Asymmetric** — slow to compress (~seconds), fast to decompress (~5,000 T-states for 1 KB).
- **Tiny depacker** — three depacker variants:
  - **Standard** (`dzx0_standard.asm`): ~69 bytes, full speed.
  - **Turbo** (`dzx0_turbo.asm`): ~88 bytes, ~25% faster.
  - **Mega** (`dzx0_mega.asm`): ~117 bytes, ~40% faster.
- **Typical ratio** — 30–50% reduction on Spectrum binary code; 60–80% on data-heavy binaries.

For size coding, the **standard depacker** is almost always the right choice — it is the smallest, and decompression speed is rarely critical (it runs once at start-up).

See [compression_packing.md](compression_packing.md) for full algorithm details, alternative compressors (ZX1, ZX2, MegaLZ, Pletter), and benchmark comparisons.

### 8.3 The Self-Extracting Pattern

A self-extracting intro is laid out as:

```
[ BASIC loader | depacker | compressed payload ]
```

When loaded:
1. The BASIC loader `LOAD "" CODE` reads the entire block into RAM at a chosen address.
2. The loader then `RANDOMIZE USR <depacker_start>` to execute the depacker.
3. The depacker reads the compressed payload, writes the decompressed code to its target address, and `JP`s to the entry point.
4. The decompressed intro runs as if it had been loaded uncompressed.

A typical BASIC loader:

```basic
10 CLEAR 24575 : REM reserve space below #6000
20 LOAD "" CODE
30 RANDOMIZE USR 24576 : REM run depacker at #6000
```

The CLEAR reserves space, LOAD reads the depacker + payload into the reserved area, and RANDOMIZE USR runs the depacker. The depacker's first instruction is typically a `LD HL,<compressed_start>` / `LD DE,<target_start>` / `CALL dzx0_standard`.

### 8.4 The Depacker Budget

The depacker is **counted against the size limit** at most parties. For a 256-byte intro with a 69-byte ZX0 depacker, only **187 bytes** are available for the compressed payload. Since the typical compression ratio is 50%, the original pre-compression budget is ~370 bytes — generous enough for a complex single effect, but not for two effects.

Some parties (notably the Spectrum-specific Chaos Construct and Forever parties) **do not count the depacker** against the budget, on the grounds that the depacker is a "runtime utility" rather than "demo content". The rules are party-specific and must be checked before submission.

### 8.5 When Compression Hurts

Compression is not always a win:

- **Already-dense code**: a binary with no repeated byte sequences (e.g. a 256-byte Mandelbrot with extensive SMC) may compress to only 240 bytes — a 5% saving that doesn't justify the depacker cost.
- **Tiny payloads**: compressing a 100-byte payload with a 69-byte depacker gives a final binary of ~180 bytes, larger than the original.
- **Start-up latency**: decompression of a 2 KB payload takes ~10,000 T-states (3 ms on a 3.5 MHz Z80). For most intros this is invisible, but a few parties require "instant start" and prohibit depackers.
- **Decompressed-vs-RAM overlap**: if the compressed payload overlaps the decompression target, the depacker must run from a different memory area (typically a high RAM page) to avoid overwriting itself. This adds complexity.

For 256-byte intros, the size-coder typically tries compression, measures the result, and **keeps the smaller of the two**. For 1K intros, compression is almost always a win and is applied automatically.

### 8.6 Alternative Compressors

Although ZX0 is the modern default, several alternatives remain in use:

| Compressor | Year | Typical ratio | Depacker size | Notes |
|---|---|---|---|---|
| **MegaLZ** | 2007 | ~5% worse than ZX0 | ~70 bytes | Predates ZX0; still seen in old sources |
| **Pletter 0.5** | 2008 | ~8% worse than ZX0 | ~100 bytes | Fast decompression; uses bit-stream |
| **ZX1** (Saukas) | 2018 | ~2% worse than ZX0 | ~67 bytes | Slightly faster than ZX0 |
| **ZX2** (Saukas) | 2018 | ~6% worse than ZX0 | ~58 bytes | Smallest depacker; aggressive trade-off |
| **LZ4** (port) | 2016 | ~15% worse than ZX0 | ~40 bytes | Cross-platform; very fast |

For pure size coding (256B / 1K), **ZX0** is the right answer. For 4K+ intros where decompression speed matters (e.g. streaming compressed chunks from a banked ROM), **ZX1** or **ZX2** may be preferable.

### 8.7 Aggressive Payload Compression

Some size-coders push compression further by **compressing the payload twice** (a "second pass" with a different algorithm), or by **compressing data and code separately** with different algorithms tuned to each. The savings are typically 2–5% over single-pass ZX0, at the cost of two depackers in the binary. This is a niche technique, used mainly in the 256-byte category where every byte counts.

### 8.8 The Final Stage Workflow

1. **Assemble** the source to a raw binary.
2. **Measure** the binary size; if it's already under budget, ship without compression.
3. **Run ZX0** (standard depacker) on the binary.
4. **Prepend** the depacker to the compressed payload.
5. **Measure** the total size; if still over budget, go back to §5–§7 and optimize the source further.
6. **Write** the BASIC loader.
7. **Test** on real hardware (or accurate emulator) — ZX0 depackers are well-tested, but every party has stories of submissions that worked in `sz80` but failed on real Spectrums due to timing differences.

The size-coder's final check before submission: **the binary, the depacker, and the BASIC loader together must be ≤ the party's byte limit.** No exceptions; off-by-one submissions are disqualified.

---

## 9. Notable Size-Coded Intros

Rather than enumerate specific titles — the size-coding scene releases dozens of 256B and 1K intros every year, and individual titles age quickly — this section describes the **achievements** of the size-coding scene and the **effects** that have been demonstrated in tight limits. For specific titles with sources, see [notable_demos.md](notable_demos.md).

### 9.1 The 256-Byte Achievements

The 256-byte Spectrum category has, as of 2024, demonstrated:

- **Mandelbrot fractals** with up to 16 levels of escape-time shading, using 8-bit fixed-point arithmetic.
- **Plasma effects** (XOR-based and sine-based) at full frame rate.
- **Border-only raster bars** with up to 8 simultaneous colors.
- **Sierpinski triangles** via the chaos-game algorithm.
- **Wireframe cube rotation** in 16-bit fixed-point.
- **Beeper tones** (single pitch, no music) generated by counter loops.
- **Text scrolls** using the 48K ROM font at `#3D00`.
- **Animated fire effects** (low-resolution, attribute-only).

What 256 bytes has **not** achieved, and likely never will on stock hardware:
- Multicolor effects (8×2 or 8×1).
- Full AY music.
- 3D filled polygons.
- Two effects with a transition.

### 9.2 The 1K Achievements

The 1K category has demonstrated:

- **Two-effect intros** with simple fades — typically plasma → tunnel, or raster bars → wireframe cube.
- **Beeper music** with simple envelopes (Roman Borisenko's `beeperfx` style — see [1bit_music_scene.md](1bit_music_scene.md)).
- **Tunnels and rotozooms** at attribute resolution, using precomputed quarter-wave sines.
- **3D wireframe scenes** with multiple objects (cube, pyramid, star) and rotation in two axes.
- **Vector text scroll** using hand-coded 8×8 fonts.
- **TS-Config disk-streamed frames** (in 1K-of-code, with frames loaded from disk outside the budget — party-specific).

### 9.3 The 4K and 16K Achievements

The 4K and 16K categories are sparser on the Spectrum than on the Amiga or PC, but have produced:

- **Full PT3 music** with a stripped player, accompanied by 2–3 minutes of visual effects.
- **8×2 multicolor** effects with proper raster synchronisation.
- **Raycasting** at 32-cell resolution, with simple texture mapping.
- **Multi-part demos** with text overlays, fades, and effect transitions.

### 9.4 The Active Competition Platforms

The Spectrum size-coding tradition is kept alive by several annual parties:

| Party | Country | Categories | Notes |
|---|---|---|---|
| **Forever** | Slovakia | 256B, 1K, 4K | Spectrum-focused; longest-running size-coding party |
| **Chaos Constructions** | Russia | 256B, 1K | Cross-platform; strong Spectrum presence |
| **DiHalt** | Russia | 256B, 1K | ZX Spectrum-centric |
| **CAFe** | Russia | 256B, 1K | Annual; smaller field but high quality |
| **Nova** | Portugal | 256B, 1K | Cross-platform; growing Spectrum presence |
| **Outline** | Netherlands | (historically) 1K, 4K | Mostly Atari/MSX but accepts Spectrum |
| **Revision** | Germany | (no Spectrum category) | PC-focused; mentioned for context |

The **Forever** party is the spiritual home of Spectrum size coding — its 1K and 256B competitions have produced the most-submitted and most-studied Spectrum size-coded binaries.

### 9.5 Source Releases and Study Material

Most size-coded Spectrum intros are released with full source code, typically in Z80 assembly with the `pasmo`, `sjasmplus`, or `z88dk` assembler syntax. The standard repositories are:

- **Pouet.net** — the demoscene archive; tag-filterable by platform and size.
- **ZXArt.ee** — the ZX Spectrum-specific archive, with intros categorised by size.
- **Github** — many size-coders publish their sources in public repositories.

For learning size-coding, the standard path is:
1. Read the source of a published 256-byte Mandelbrot or plasma.
2. Re-implement it from scratch, without looking at the original.
3. Compare byte counts and identify where the original is shorter.
4. Move to a 1K intro source and repeat.

The size-coding community is small, generous with feedback, and explicitly welcoming to newcomers. The `sxzx` Slack channel (Spectrum size-coding) and the `zx-pk.ru` Russian forum are the main discussion venues.

### 9.6 Cross-Platform Comparisons

A 1K intro on the ZX Spectrum can be compared directly to a 1K intro on the Commodore 64, Atari 800, BBC Micro, or MSX. The comparison reveals interesting architectural differences:

| Platform | CPU | Clock | Advantages for size coding | Disadvantages |
|---|---|---|---|---|
| **ZX Spectrum** | Z80A | 3.5 MHz | Dense instruction set; 16K free ROM library; LDIR for block ops | No hardware multiply; contended memory |
| **Commodore 64** | 6510 | 1.0 MHz | Hardware sprites; VIC-II raster IRQs; SID sound | Sparse 6502 encoding; no LDIR equivalent |
| **Atari 800** | 6502 | 1.8 MHz | ANTIC/GTIA hardware; display lists; POKEY sound | Sparse encoding; smaller installed scene |
| **MSX** | Z80A | 3.5 MHz | Same CPU; TMS9918A VDP with sprites; AY sound | VDP access is slow (port-mapped, not memory-mapped) |
| **Amstrad CPC** | Z80A | 4.0 MHz | Same CPU; slightly faster; GA hardware for raster sync | Smaller scene; less shared code |

The Z80's **dense instruction set** and the Spectrum's **16K free ROM** give the Spectrum an edge in pure code density. The C64's **hardware sprites and raster interrupts** give it an edge in visual quality at a given byte budget. The two scenes have influenced each other heavily, with C64 size-coders adopting ZX0 and Spectrum size-coders adopting C64-style IRQ-driven effects.

---

## 10. Cross-References

This article sits within the ZX Spectrum demoscene knowledge base and connects to the following related articles:

### 10.1 Within the Demoscene Section

- [demoscene_history.md](demoscene_history.md) — where size coding fits in the broader timeline (size competitions emerged around 1988).
- [soviet_demo_scene.md](soviet_demo_scene.md) — Soviet/Russian size-coding tradition (DiHalt, Chaos Constructions).
- [demoscene_platforms.md](demoscene_platforms.md) — cross-platform size-coding comparisons (§9.6 of this article).
- [precalc_trigonometry.md](precalc_trigonometry.md) — §3 sine tables, §4 quarter-wave storage, §5 multiplication tables (alternatives to runtime generation in §7 of this article).
- [multicolor_techniques.md](multicolor_techniques.md) — why multicolor is impractical at 256 bytes (§3.3 of this article).
- [effects_catalog.md](effects_catalog.md) — which effects fit in size-coding budgets (cross-referenced from §3.3, §7.1, §7.7).
- [compression_packing.md](compression_packing.md) — full treatment of ZX0, ZX1, ZX2, MegaLZ, Pletter (referenced extensively in §8).
- [demo_frameworks.md](demo_frameworks.md) — how larger demos sequence effects; 16K intros use a stripped-down framework.
- [notable_demos.md](notable_demos.md) — specific size-coded intros with sources (cross-referenced from §9.5).
- [1bit_music_scene.md](1bit_music_scene.md) — the beeper music tradition used in 256B and 1K intros (cross-referenced from §6.5 and §9.2).
- [README.md](README.md) — index of all demoscene articles.

### 10.2 Within the Development Section

- [../01_cpu/z80_undocumented.md](../01_cpu/z80_undocumented.md) — `LD F,A`, `LD A,F`, IX/IY halves, SLL — used in §5.3.
- [../01_cpu/z80_coding_practices.md](../01_cpu/z80_coding_practices.md) — general Z80 optimisation, contrasted with size coding in §4.3.
- [../05_development/03_memory_and_io/contention_model.md](../05_development/03_memory_and_io/contention_model.md) — ROM-call timing caveats (§6.9).
- [../05_development/04_interrupts/interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md) — ISR-driven beeper music in 1K intros.
- [../05_development/06_graphics/README.md](../05_development/06_graphics/README.md) — screen layout for size-coded effects.

### 10.3 External Resources

- [Logan & O'Hara, "The Spectrum ROM Disassembly"](https://worldofspectrum.org/ROMdisassembly.zip) — the canonical reference for ROM routine addresses.
- [Pouet.net](https://www.pouet.net/) — searchable archive of size-coded Spectrum productions.
- **ZXArt.ee** — Spectrum-specific archive with size categorisation.
- **Einar Saukas's ZX0 release** (2017) — the modern standard Spectrum compressor.
- **ZX Size Coding wiki** (community-maintained) — techniques and tutorials.

---

## License

This article is released under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you credit the original source and license derivative works under the same terms.

The techniques described here are part of the demoscene's shared heritage. The article draws on the published work of hundreds of size-coders over four decades; specific attributions for individual tricks are impractical, but the community's collective contribution is acknowledged.
