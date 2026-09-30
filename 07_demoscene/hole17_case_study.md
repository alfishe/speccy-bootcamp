[← Home](../README.md) · [Demoscene](README.md)

# Case Study: "Hole 17 enigma" — A 256-Byte Intro Where Code, Data, Music, and Picture Are One Object

> **Type**: case_study
>
> **Scope**: A line-by-line technical dissection of **"Hole 17 enigma"** (RMDA, LoveByte'2021, ZX Spectrum 48K+AY, 256 bytes; code by `.ded^RMDA`) — [ZXArt.ee entry](https://zxart.ee/prod/359194), [source + binaries](https://emulate.su/rmda/hole17.zip). It is referenced from [size_coding.md §9.1](size_coding.md#91-the-256-byte-achievements) as the named example behind the "self-generating decruncher" and "static AY chord" claims there; this article is where the mechanism is actually worked out.
>
> The point of this case study is **not** the byte count. Plenty of 256-byte intros hit that target with a static effect and a squeeze table (see [size_coding.md](size_coding.md) §5). What makes Hole17 worth a dedicated article is that it has almost no "effect code" and no "data" in the conventional sense at all — the picture, the sound, the randomness, and the program are the **same bytes and the same CPU registers**, reinterpreted depending on when and how they're touched. All source quotes below are from `hole17.asm` as released by the author.

---

## 1. What You Actually See and Hear

Run the binary and this is the experience, with no separate "scenes" or timeline:

1. **A flickering, drifting field of color** fills the screen from the first frame — not a designed plasma or gradient, but genuine byte-level chaos (§3 explains exactly where it comes from).
2. **A static vertical object** is stamped into the bitmap once at start-up and stays fixed while the color chaos churns around it — the closest thing the intro has to a "logo."
3. **Nothing else happens until you press SPACE** ("*In SPACE no one can hear your CALL...*" — the NFO's pun is literal: the intro is built almost entirely out of the Z80 `CALL` instruction). On SPACE, an asymmetric hole-shaped silhouette is punched into the bitmap by OR-ing a fixed bit pattern into whatever chaotic noise already occupies that screen region — the "hole" is carved out of the noise, not drawn over it.
4. **The sound is a single static AY chord** — not a tune, not a sequencer, not even a beeper envelope. The AY registers are written once at boot and never touched again; whatever timbre results holds (or repeats, per the chip's own internal counters) for the entire run.

Every one of these four things is a side effect of the same underlying engine, described next.

## 2. The Single Generative Engine: A Self-Built, Self-Executing `CALL` Chain

At start-up (`newrnd`/`rernd` in the source), the program does not decompress or load an effect — it **writes its own program**:

- It walks through free RAM (`#5B00`–end of usable memory) and lays down a chain of `complexity` (`#EB` = 235) linked `CALL nnnn` instructions. Each one's target is chosen by a compact **CMWC pseudo-random generator** (credited in the source to Patrik Rak), reseeded from a 10-byte table placed immediately after the intro's own code (`table: equ $+17`).
- Every candidate target is checked against three bytes of RAM that must currently read as zero (`or a` / `jr nz,rernd`) before it's accepted — this guarantees the generator never overwrites a `CALL` it (or the setup code) already placed, and never lands inside its own code or the screen's "protected" start.
- The last node in the chain is patched to `CALL #5B00`, closing it into a **235-node loop**.

The result is a single closed loop of `CALL` instructions scattered pseudo-randomly across free memory — no data section, no display list, just executable opcodes chaining into each other forever. This loop is the *entire* runtime engine: there is no separate "main loop" that calls into it once per frame. It **is** the frame loop.

## 3. Rendering Is a Side Effect: the Stack Pointer as the Plotter

This is the article's central finding, and it is stated almost in passing by the author's own comment.

Every time the interrupt handler (`int:`) finishes, it re-enters the chain via:

```z80
im2exit:
    ei
    ld   sp,start_scr   ; SP = #5800 — the exact boundary between
                         ; the bitmap (#4000-#57FF) and the attributes
    jp   (hl)            ; jump into the CALL chain
```

`SP` is deliberately reset to `#5800` — the byte immediately above the last row of the screen bitmap — **every single frame**, right before the chaotic `CALL` chain resumes. Because every node in the chain is a `CALL` and none of them ever `RET`s, each executed `CALL` does the one thing a `CALL` always does regardless of programmer intent: it pushes a 2-byte return address onto the stack and decrements `SP` by 2. With `SP` parked at the top of the bitmap and no `RET` anywhere in the loop, that push has nowhere else to land but **straight into video memory**, and the next push lands two bytes below that, and so on — `SP` walks down through the bitmap, and the two-byte "return addresses" it deposits (themselves just Z80 addresses in the `#5B–#FD` range, chosen by the PRNG when the chain was built) *are* the pixel data the viewer sees.

Nothing in the program ever explicitly writes to the bitmap during normal execution. The picture is a byte-for-byte record of how far the CPU's own call-return bookkeeping mechanism got before the next 1/50s interrupt arrived. This is confirmed directly by the author's comment sitting right at the entry point of the interrupt handler:

```z80
int:    ;check SP value with debugger at this point
        ;to understand how fast/slow your hardware
```

`SP`'s value at that instant is a direct, cycle-accurate readout of how many `CALL`s executed since the frame began — i.e., of the host's real clock speed and contention behavior. A faster machine (or a less-contended memory model) walks further down the bitmap per frame and repaints more of it; a slower one repaints less. The demo has no explicit frame-rate-adaptive code, no speed detection routine — the rendering mechanism *is* the speed detector, and the author is inviting the viewer to read one register to see it.

**Where the color noise comes from.** The interrupt can land at any point in that 235-node walk, so at the moment it fires, `HL` (the chain's "current position" register) holds a genuinely hardware-timing-determined value — not a value produced by a separate PRNG call. The handler exploits this directly:

```z80
enigma2:
    ld   h,#58      ; force the high byte into the attribute page
    ld   b,d        ; B = 3 (three attribute thirds of the screen)
    ex   af,af'
attr2:  ld   (hl),a
    rlc  l          ; L is random from last IM2
    inc  l
    ld   (hl),a
    inc  h
    djnz attr2
```

Only the high byte of `HL` is forced (to `#58`, the attribute page); the **low byte is left exactly as the interrupt found it** — leftover state from wherever in memory the chaotic chain happened to be executing. That leftover low byte becomes the effective "random seed" for which attribute cells get repainted this frame. No table, no LFSR, no extra PRNG call: the entropy is free, borrowed from the same register the rendering engine was already using for something else.

**Why the picture drifts instead of just flickering in place.** At the end of the handler:

```z80
    ld   hl,(start_scr-fx_shift)
    dec  hl
    jr   im2exit
```

`HL` is reloaded from a fixed memory location offset by `fx_shift` (`equ 24`, and per the source comment must stay even — `2` = no shift, `4` = shift 2 bytes, `34` = shift 32 bytes, and so on) before the chain resumes. Because the content of that memory location keeps changing as the chaotic engine runs, this reentry point — and hence where the "brush" starts painting each frame — creeps by a controlled amount every frame, producing the slow drift/scroll in the noise pattern rather than pure static.

## 4. Sound: One Chord, Baked Directly Out of the Program's Own Bytes

The AY setup runs once, before anything else, and never runs again:

```z80
    ld   de,#fe0d      ; D = #FE (IM2 table page), E = 13 (last AY register)
    ld   hl,begin+73   ; source pointer INTO THE INTRO'S OWN CODE
ayl:
    ld   bc,#fffd
    out  (c),e         ; select AY register E
    ld   b,#bf
    outi                ; write (HL) to the AY data port, HL++, then E--
    jr   nz,ayl
```

Thirteen AY registers (R13 down to R1 — the loop stops before R0) are written from thirteen consecutive bytes starting at `begin+73` — that is, from a span of **the intro's own already-assembled instruction bytes**, reinterpreted as tone, volume, and mixer values. There is no dedicated data table for the chord; the author picked an offset into the code whose incidental byte values happen to produce a usable chord when poured into the AY. The source comment beside the loop (`;+3,+10,+32,+37,+45,+68,+78`) records specific code offsets the author cross-checked as contributing usable register bytes this way.

The consequence: the AY chip is configured once and left alone. There is no player, no interrupt-driven note table, no envelope sequencing — what you hear is whatever static chord those thirteen bytes decode to, for as long as the demo runs. This is the concrete example behind the "a static AY chord fits in 256 bytes; a sequenced tune does not" distinction drawn in [size_coding.md §3.3](size_coding.md#33-what-256-bytes-can-express).

## 5. The Squeeze Tricks, Mapped to the General Taxonomy

Everything above is the *conceptual* engine; fitting its setup code into the remaining byte budget still required the standard size-coding toolkit from [size_coding.md §5](size_coding.md#5-squeeze-tricks), applied unusually aggressively:

- **Overlapping instructions (§5.6).** The clear/attribute-fill loop's exit is engineered so that jumping to `attr-1` — one byte before the `attr:` label, inside what would otherwise be read as the tail of the preceding `jr nz,clear` — lands on a byte that decodes as a fresh `LD SP,HL` opcode. The author's own comment calls this out twice: *"hidden free LD SP,HL is here!"* and *"jr attr-1 give us free LD SP,HL"*. This is what sets up `SP` for the generation phase (§2 above) without spending a single dedicated byte on the instruction — the commented-out alternative (`ld sp,hl` / `inc sp`) is left in the source specifically so the reader can see what was eliminated, corrected afterward with a single `pop af` that both advances `SP` by 2 and discards two already-zeroed bytes.
- **Register dual-use via `AF'` (§5.3).** `ex af,af'` is used purely to stash the attribute value (`#06`, later `xor`'d with `#36`) across the setup code, described in the source as *"4 bytes offset here for right colors in decrunch attribute"* — the shadow register pair is free storage, cheaper than any memory location.
- **Leftover-register reuse.** After the AY loop ends, `E` is guaranteed to be `0` (the loop counts down to zero to terminate). The very next stage reuses that fact — `ld l,e` — to zero `L` for free, commented explicitly as *"for relocation code"*, instead of spending 2 bytes on `ld l,0`.
- **The IM2 filled-page trick.** `#FE00`–`#FF00` is filled entirely with the byte `#FD`, and `I` is set so that the IM2 vector fetch lands inside that page. Because *every* byte in the fetch window is `#FD`, the interrupt vector always resolves to `#FDFD` — `jp int` — regardless of which byte the ULA's floating data bus happens to return during the fetch. This sidesteps the need to predict or control the exact refresh-register value, which would otherwise cost extra bytes of hardware-specific handling; the extra byte written at `#FF00` after the fill loop exists purely to cover the one edge case where the refresh byte is `#FF`.
- **"Fake" omitted re-reads for the hole shape (§5.4-adjacent ALU dual-use).** The hole-punching code at the end (`-1` through `-8` per side, per the source's own numbered comments) deliberately skips re-loading `A` from `(HL)` at several steps, reusing the value already sitting in `A` from the previous `OR`. The source labels these skipped steps `fake#1`/`fake#2`/`fake#3` and states plainly that this trades a **visually asymmetric hole** for up to 8 saved bytes — an explicit, acknowledged trade of aesthetic symmetry for byte count, not an accident.
- **Data-as-code reuse (§7's self-modifying-code family, taken to its limit).** As covered in §4 above, the AY chord's thirteen data bytes are not data at all — they are a slice of the program's own opcodes, read as if they were a table. This is the same family of trick as [size_coding.md §7.6](size_coding.md#76-smc-generators--code-that-writes-code), inverted: instead of code that writes data, this is data that *is* code, simply pointed at by a second, unrelated instruction stream (the AY loop) that never executes those bytes as instructions at all.

## 6. How It Is All Fused Into One Blob

The reason Hole17 resists being described as "a program plus some data plus a picture plus a tune" is that almost nothing in it has a single, fixed role. The same bytes and the same CPU registers are doing two, three, or four jobs simultaneously, depending only on *when* and *how* something touches them:

| Byte range / register | Role #1 | Role #2 | Role #3 |
|---|---|---|---|
| Code bytes at `begin+73..` | Executable instructions (part of the intro's own setup code) | AY register data (§4) — read once via `outi`, never executed as opcodes from that access path | — |
| `#FE00`–`#FF00` | The IM2 interrupt vector table | Disposable filler — its only functional requirement is "every byte equals `#FD`," so it needs no real content, only a uniform value | — |
| The screen bitmap `#4000`–`#57FF` | The picture the viewer sees | The live memory the self-built `CALL` chain executes through and pushes return addresses into (§3) — there is no separate off-screen buffer; the chain's working memory *is* the framebuffer | The one place the "hole" shape gets OR'd into whatever chaos already occupies it, rather than into a clean layer |
| `HL` | The chain's "current instruction pointer" during execution | This frame's color-noise seed, taken from wherever the chain happened to be interrupted (§3) | The reentry point for the next frame, after the `fx_shift` adjustment |
| `SP` | The CPU's ordinary call/return bookkeeping register | The rendering engine's pixel-plotting cursor (§3) — repurposed with zero modification to its normal hardware behavior | An implicit hardware-speed sensor, readable by a debugger at the interrupt entry point |
| The `#CD` (`CALL`) opcode, repeated 235 times | The single instruction that drives the entire runtime | (via the PRNG-chosen, constrained address range `#5B`–`#FD`) the source of every "pixel" value pushed to the bitmap, since the pushed bytes are literally these addresses | — |

No layer of this intro is "just" code, "just" data, "just" the picture, or "just" the tune. The AY chord *is* a fragment of the boot code, reread as data. The picture *is* the stack's ordinary bookkeeping, redirected into visible memory. The color randomness *is* interrupt jitter, borrowed from a register that was already busy doing something else. The 256-byte budget doesn't force this fusion by itself — a size-coder could hit 256 bytes with cleanly separated (if minimal) code/data/effect sections, as the more conventional entries in [size_coding.md §9.1](size_coding.md#91-the-256-byte-achievements) do. Hole17's specific achievement is collapsing "renderer," "asset," "randomness source," and "program" into the *same* bytes and the *same* registers, so that the finished 256-byte object has no internal seams at all.

## 7. Cross-References

- [size_coding.md](size_coding.md) §3.3 (What 256 Bytes Can Express), §5 (Squeeze Tricks), §9.1 (The 256-Byte Achievements) — the general taxonomy this case study's tricks are drawn from and feed back into.
- [compression_mindset.md](compression_mindset.md) — a related but distinct discipline (writing code for a *compressor's* benefit); Hole17 ships uncompressed, so it is a pure demonstration of the squeeze/fusion side of size-coding rather than the compression side.
- [1bit_music_scene.md](1bit_music_scene.md) — for contrast, the beeper-music tradition that 1K+ intros use when a static AY chord isn't the target sound.
- [effects_catalog.md](effects_catalog.md) — conventional plasma/noise effects, for contrast with §3's stack-driven rendering.
- [README.md](README.md) — section index.

---

## License

This article is released under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you credit the original source and license derivative works under the same terms.

The analysis draws directly on the source comments and code of "Hole 17 enigma" by `.ded^RMDA` / RMDA (2021), released with the production itself; the surrounding explanation, taxonomy mapping, and cross-references are original to this knowledge base.
