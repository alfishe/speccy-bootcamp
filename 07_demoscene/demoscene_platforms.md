[← Home](../README.md) · [Demoscene](README.md)

# Cross-Platform Demoscene Comparison

> **Scope**: This article compares the ZX Spectrum to its principal demoscene peers — the **Commodore 64**, **Amiga**, **Atari ST**, **MSX**, and **Amstrad CPC** — to highlight each platform's unique strengths, weaknesses, and the cross-pollination between scenes. It is the technical companion to [demoscene_history.md](demoscene_history.md) (which covers the cultural narrative), [soviet_demo_scene.md](soviet_demo_scene.md) (Pentagon-centric deep-dive), and [effects_catalog.md](effects_catalog.md) (Spectrum-specific techniques).
>
> **Why a cross-platform article?** Each platform's demoscene developed techniques *that only make sense in light of what the hardware does and does not provide*. The Spectrum's multicolor tradition is incomprehensible without contrasting it with the C64's hardware-sprite model; the AY-music cross-pollination between Spectrum and ST is invisible until you notice they share the same sound chip family. This article makes those contrasts explicit.

---

## 1. Why Compare Platforms?

A demoscene is, fundamentally, a long argument with a piece of hardware about what that hardware can be made to do. The argument's character depends entirely on the hardware:

- **C64 sceners** argue with the VIC-II's hardware sprites and the SID's analogue filter — they want to *extend* capabilities the chip already provides.
- **Amiga sceners** argue with the Copper, Blitter, and Paula — they want to *combine* existing co-processors in ways the chip designers did not anticipate.
- **Spectrum sceners** argue with the absence of hardware support — they want to *build, in software, what other platforms get for free*.

These three argument-styles produce profoundly different bodies of work. A C64 effect that looks effortless (a smooth 8-pixel horizontal scroll) is impossible on the Spectrum without cycle-counted multicolor work; a Spectrum effect that looks effortless (full-frame attribute manipulation, 15-colour interlaced gigascreen) is impossible on the C64 because the VIC-II owns its colour RAM. Cross-platform comparison is the only way to understand why each scene's tradition looks the way it does.

Comparison also reveals **cross-pollination**: the AY/YM sound chip is shared (with minor variations) between Spectrum, ST, MSX, and CPC; certain demoscene effects (raster sync, copper-style per-scanline register manipulation) have analogues across multiple platforms; and tracker formats (notably PT3) crossed the East–West border. See §9 for the AY/YM bridge.

### Article Roadmap

- §2 Hardware feature matrix — the master comparison table.
- §3 ZX Spectrum vs Commodore 64 — the defining rivalry.
- §4 ZX Spectrum vs Amiga — 8-bit underdog vs 16-bit powerhouse.
- §5 ZX Spectrum vs Atari ST — the AY sibling.
- §6 ZX Spectrum vs MSX — the other Z80+PSG platform.
- §7 ZX Spectrum vs Amstrad CPC — the third Z80+AY platform.
- §8 Other peers: BBC Micro, Apple II, NES, MSX2+, TurboR.
- §9 The AY/YM bridge — how one chip family shaped four scenes.
- §10 What the Spectrum excels at — and where it loses.
- §11 Technique portability matrix — what transfers and what doesn't.
- §12 Relative scene sizes and activity levels, by year.
- §13 Cross-References and License.

---

## 2. Hardware Feature Matrix

The table below summarises the principal demoscene-relevant hardware features of each platform. All values are for the *base* configuration (e.g. C64, not C128; Amiga 500 OCS, not AGA; Spectrum 48K, not 128K unless noted). "Extensions" lists common upgrades sceners assume.

| Feature | **ZX Spectrum 48K** | **ZX Spectrum 128/+2** | **Commodore 64** | **Amiga 500 (OCS)** | **Atari ST (520ST/1040ST)** | **MSX1** | **Amstrad CPC 464/664/6128** |
|---|---|---|---|---|---|---|---|
| **CPU** | Z80A @ 3.5 MHz | Z80A @ 3.54690 MHz | MOS 6510 @ 1.023 MHz | Motorola 68000 @ 7.09 MHz (PAL) | Motorola 68000 @ 8.0 MHz | Z80A @ 3.58 MHz | Z80A @ 4.0 MHz |
| **CPU register width** | 8-bit (16-bit BC/DE/HL pairs) | same | 8-bit | 16/32-bit (32 internal) | 16/32-bit (32 internal) | 8-bit | 8-bit |
| **Base RAM** | 16K/48K | 128K (banked) | 64K | 512K (chip RAM + fast RAM) | 512K/1024K | 8K–64K (32K typical) | 64K/128K |
| **Video** | Ferranti ULA-variant: framebuffer with attribute bytes; 256×192, 32×24 attribute cells | same + extra video modes (not used by demoscene) | VIC-II: 40×25 text, 320×200 hi-res, 160×200 multicolour, 8 hardware sprites, 16-colour fixed palette, hardware smooth-scroll | OCS: bitplanes (up to 6), 320×256 / 320×512 (interlaced), 32/64/4096 colours, dual-playfield, hardware sprites | Yamaha YM701 (ST Shifter): 320×200 (16 colours) / 640×200 (mono), no sprites, no hardware scroll | TMS9918A: 16-colour 256×192, 32 hardware sprites, fixed palette of 15 | ASIC ("Gate Array"): 160×200 (16 colours) / 320×200 (4 colours) / 640×200 (2 colours), no sprites, no hardware scroll |
| **Palette (hardware colours)** | 8 colours × 2 brightness = 15 | same | 16 fixed | 4096 (12-bit RGB) | 512 (9-bit RGB), 16 on screen | 15 fixed | 27 fixed (12-bit RGB from 4096); 16/4/2 on screen depending on mode |
| **Attribute resolution** | 8×8 cells (32×24 grid) | same | Per-pixel (separate colour RAM) — *no attribute clash* | Per-pixel (bitplane-per-colour-index) | Per-pixel | Per-cell but in a different sense (colour table indirection); no clash | Per-pixel |
| **Hardware sprites** | None | None | 8 sprites, 24×21, multicolour mode, per-sprite expand | Up to 8 (in lo-res, dual playfield mode) per frame, 16-colour | None | 32 single-colour sprites, 8 per scanline | None |
| **Hardware scrolling** | None | None | Yes (VIC-II registers `XSCROLL`/`YSCROLL`) | Yes (modulo-based playfield scrolling) | No (must be done in software, like Spectrum) | Yes (TMS9918A `NAME TABLE BASE`/`PGC BASE` indirection) | No |
| **Sound chip** | None (1-bit beeper) | AY-3-8912 | MOS 6581/8580 SID (3-voice, analogue filter) | Paula (4-channel 8-bit PCM, hard-panned stereo) | Yamaha YM2149 (3-voice PSG; AY-compatible) | AY-3-8910 (3-voice PSG) | AY-3-8912 (3-voice PSG) |
| **Sound chip registers** | n/a (1-bit OUT) | 0xFFFD (address), 0xBFFD (data) | 0xD400–0xD41E (SID is 29 bytes) | Custom DMA audio ($BFxxxx) | 0xFFFF (address), 0xFF8802 (data, ST) | 0xA0–0xA1 (PSG ports) | 0xF6xx (Gate Array latches) |
| **Sample playback (4-bit)** | Manual bit-banging via beeper (~28 kHz theoretical, ~6–8 kHz usable) | Manual via AY envelope or beeper; also external interfaces | Via SID + CPU modulation (4-bit samples possible at low rate) | Hardware — Paula plays 8-bit samples via DMA at arbitrary rate | Bit-banged via YM2149 envelope; some technique | Bit-banged via AY envelope | Bit-banged via AY envelope |
| **Storage** | Cassette (~1500 baud standard, custom loaders up to ~8000 baud) | Cassette + 3" disk (+3) or TR-DOS (Soviet clones) | Cassette (C2N, ~300 baud Datasette) + 1541 floppy (5¼") | 3½" DD floppy (880 KB), internal IDE (later) | 3½" DD floppy (720 KB) + ACSI/HDD | Cassette + ROM cartridge + (later) floppy | 3" floppy (180 KB single-sided) |
| **Filesystem for scene distribution** | `.tap` (cassette image), `.z80`/`.sna` (snapshot), `.trd`/`.scl` (TR-DOS) | same + `.trd`/`.scl` (TR-DOS) | `.prg`, `.t64`, `.d64` (1541 disk image), `.tap` | `.adf` (Amiga disk file), `.lha` | `.st` (disk image), `.msa` | `.cas` (cassette), `.rom`, `.dsk` | `.dsk`, `.cdt` (cassette) |
| **Demoscene-standard extensions** | Pentagon 1024 RAM, TurboSound (dual AY), General Sound, TS-Config disk cache, DivMMC, ZXMMC | same | REU (RAM expansion), 1541 Ultimate, CMD HD, SuperCPU (rare) | Accelerator cards (030/040/060), extra RAM (Fast RAM expansions), AGA chipset (later models) | No common extensions (Atari ST demoscene targets stock 520ST) | MSX-Music (YM2413 FM), MSX-Audio, Moonsound, MegaRAM | No common extensions (CPC scene targets stock 6128) |
| **Effective CPU speed** | ~3.5 MHz minus 17% ULA contention (only on contended RAM banks) → effectively ~2.9 MHz when accessing contended RAM | same | ~1 MHz (no contention) | 7.09 MHz (no contention on Fast RAM; Chip RAM contends with custom chips) | 8 MHz (no contention) | 3.58 MHz (no contention; VDP has its own VRAM) | 4 MHz (with wait-states: ~3.3 MHz effective due to video ASIC contention) |
| **Demoscene era peak** | 1991–1996 (West), 1998–2005 (Soviet), 2015–present (revival) | 1991–1996 (West), 1998–2005 (Soviet), 2015–present (revival) | 1985–1995 (West), 2000–present (continuous) | 1987–1995 (West, peak AGA 1993–1996) | 1987–1995 (West), revival 2010–present | 1986–1992 (Japan), 1995–2005 (Brazil/Netherlands), 2010–present (revival) | 1986–1995 (UK/Europe), small revival 2010–present |

### Reading the matrix

A few patterns emerge immediately:

- **The Spectrum is the only major platform with no dedicated video co-processor**. The CPU does *everything* — every pixel write, every attribute change, every colour register poke. This is the Spectrum's defining constraint and its defining opportunity.
- **The Spectrum is the only major platform with no hardware sprites**. The C64 has 8, the Amiga has 8, the MSX has 32 (single-colour), the ST and CPC have none — but the ST and CPC compensate with bitplane/linear-framebuffer modes that make software sprites easier.
- **Three platforms share the AY/YM sound chip family**: Spectrum 128, ST (YM2149), MSX1 (AY-3-8910), CPC (AY-3-8912). This is the basis for cross-pollination of music (§9).
- **The Spectrum is the slowest** of the comparable platforms in raw CPU speed, but only by a small margin (3.5 MHz vs 3.58 MHz MSX or 4 MHz CPC). The C64's 1 MHz 6510 is *slower* per-instruction-cycle but executes 1 instruction per 2 cycles vs the Z80's typical 4–10 cycles per instruction, so per-instruction throughput is comparable.
- **The Amiga is in a different class entirely** — 16-bit CPU at 7 MHz with multiple co-processors. Spectrum-vs-Amiga is not really a fair comparison; the Amiga could do things the Spectrum simply cannot.

The matrix establishes the baseline. The next sections explore specific rivalries in depth.

---

## 3. ZX Spectrum vs Commodore 64

The ZX Spectrum and the Commodore 64 are the most compared platforms in the 8-bit demoscene world. Both launched in 1982; both have active scenes 40+ years later; both have demo traditions that depend, structurally, on what each machine did and did not provide.

### 3.1 Hardware contrast in one paragraph

The C64's VIC-II provides 8 hardware sprites, 16 fixed colours with per-pixel colour RAM, hardware horizontal and vertical scrolling, three display modes (hi-res, multicolour, extended colour), a raster-interrupt line, and a sprite-sprite collision register. The Spectrum's ULA provides *none* of these — no sprites, no scrolling, no raster interrupt, fixed attribute cells at 8×8 resolution, and a 15-colour palette. The C64's SID provides 3 synthesised voices with an analogue filter and ADSR envelopes; the Spectrum 48K has a 1-bit beeper. Even where the two platforms overlap — both are 8-bit, both have ~16-colour palettes, both have ~64K RAM — the *quality* of those features differs enormously in the C64's favour.

### 3.2 What the C64 does that the Spectrum cannot

- **Smooth hardware scrolling.** A C64 demo scrolls the playfield by writing two registers; a Spectrum demo scrolls the playfield by re-writing every visible byte of the framebuffer in real time. C64 demos can scroll arbitrarily at 50 Hz; Spectrum scrolls are partial and use clever encoding (precomputed deltas).
- **Hardware sprites.** C64 demos routinely have 8 sprites on screen per scanline, multiplexed (the raster interrupt repositions them mid-frame) to give the appearance of dozens. Spectrum demos have *no* sprites; every moving object is software-rendered pixel-by-pixel.
- **Per-pixel colour.** The C64's separate colour RAM gives every 8×1 character cell its own colour, independently of the rest of the screen. The Spectrum's 8×8 attribute grid produces the famous **attribute clash**: a horizontal stripe of 8 pixels must share a single ink and paper colour.
- **SID music.** The SID's analogue filter enables pads, sweeps, and bass lines that have no direct equivalent on the AY (or, worse, the beeper). C64 music tradition (Hubbard, Galway, Daglish) is the deepest of any 8-bit platform and the standard against which other 8-bit music is measured.
- **Raster effects without cycle counting.** The VIC-II generates a raster interrupt at any programmable scanline; the CPU can update registers between interrupts. The Spectrum's only raster tool is *cycle-counting* the CPU against the ULA's display fetches — possible but much harder.

### 3.3 What the Spectrum does that the C64 cannot

- **Per-frame attribute manipulation at zero CPU cost during display.** The VIC-II owns its colour RAM during the visible display; the C64 CPU can write to colour RAM at any time, but the *visible* per-scanline colour is fixed by what the VIC-II fetches. The Spectrum's attribute RAM is just ordinary RAM — the CPU can rewrite it mid-display if it can keep up. This is the basis of **multicolor** (see [multicolor_techniques.md](multicolor_techniques.md)).
- **Full-frame arbitrary attribute patterns.** Because colour RAM on the Spectrum is the same as display RAM, a single `LDIR` copy from a precomputed buffer can repaint every attribute cell on screen. C64 demos need to rewrite the entire 1K colour RAM to achieve the same effect.
- **Direct framebuffer access.** The Spectrum's pixel framebuffer is a simple (if weirdly-laid-out) 6144-byte linear region. The C64's framebuffer is interleaved with the VIC-II's display fetches and has more complex layout constraints.
- **1-bit music engines.** The Spectrum beeper tradition (see [1bit_music_scene.md](1bit_music_scene.md)) has no C64 equivalent, because the C64 never had a beeper — every C64 has a SID. This forced the development of software 1-bit synthesis on the Spectrum that the C64 scene never needed.

### 3.4 The attribute-clash question

The Spectrum's attribute grid is often cited as the platform's biggest weakness. It is — but it is also the basis of the Spectrum's most distinctive tradition. Soviet-scene coders (in particular) reframed attribute clash as an *aesthetic*: demos like *I am the seed* (Inward, 2005) deliberately used attribute clash as a visual style, producing blocky colour fields that read as pixel-art abstraction. A C64 demo could not produce this look even if the artist wanted it; the VIC-II's per-pixel colour defeats it.

This is a recurring pattern in cross-platform comparison: what looks like a limitation from outside becomes a tradition from inside. The Spectrum's limits *produced* its scene's identity.

### 3.5 Where the scenes align

Both scenes share:

- **Cracking-group origins** ( cassette-swapping piracy subculture of the mid-1980s).
- **Demo-party infrastructure** (The Party in Denmark, X in the Netherlands, Assembly in Finland all hosted both scenes' work).
- **Cross-platform tracker formats** (GoatTracker, SID-Wizard — the C64 equivalents of the Spectrum's PT3).
- **A continuous modern revival** driven by YouTube, Discord, and easy cross-development tools.

The two scenes rarely reference each other directly — the C64 scene is firmly Western-European-dominated; the Spectrum scene's center of gravity moved to Russia by 1998 — but they share deep structural assumptions about what a demo *is*.

### 3.6 Summary

| Question | C64 | Spectrum |
|---|---|---|
| Easier smooth scrolling? | **C64** (hardware) | Spectrum (software, hard) |
| Easier hardware sprites? | **C64** (8 sprites) | Spectrum (none) |
| Easier per-pixel colour? | **C64** (separate colour RAM) | Spectrum (8×8 attribute grid) |
| Easier music? | **C64** (SID filter) | Spectrum (beeper or AY) |
| Easier full-frame colour cycling? | Spectrum (LDIR attribute buffer) | Spectrum wins |
| Easier multicolor 8×1 / 8×2 effects? | Spectrum (CPU rewrites attributes per scanline) | Spectrum wins |
| Easier 1-bit beeper music? | n/a | **Spectrum only** |

The C64 wins on raw capability; the Spectrum wins on a narrow set of effects that depend on the ULA's permissiveness about CPU writes during display.

---
## 4. ZX Spectrum vs Amiga

The Amiga comparison is, in some sense, unfair: the Amiga is a 16-bit platform from 1985 (three years after the Spectrum) with custom co-processors (Agnus, Denise, Paula) that offload the 68000 CPU from video and audio work entirely. Where the Spectrum has *nothing* in the way of custom chips, the Amiga has *everything* — a Copper that runs register-update instructions in parallel with the CPU, a Blitter that does block copies and line draws at memory bandwidth, and Paula playing four channels of 8-bit PCM samples via DMA.

### 4.1 What the Amiga gives the scener for free

- **Hardware dual-playfield scrolling**. The Amiga's bitplanes can be configured as two independent playfields, each scrolling independently. This is the basis of dozens of standard parallax-scroll effects.
- **The Copper** — a small coprocessor that waits for a specific scanline and x-position, then writes a value to a hardware register. This enables per-scanline palette changes, mode switches, and "copper bars" — all without CPU involvement.
- **The Blitter** — a block-copy engine that can move memory regions (including bitplane-aligned data), fill patterns, draw lines, and apply minterms (logic operations) at memory bandwidth (≈3.5 MB/s on OCS).
- **Paula audio** — four 8-bit PCM channels, hard-panned (two left, two right), playing at any sample rate up to ~28 kHz. The classic Amiga "MOD" format is just four sample streams with pitch/volume info; the player reads them and feeds Paula.
- **Bitplanes** instead of attribute cells. The Amiga's 6-bitplane mode gives 64 simultaneous colours from a 4096-colour palette (or 32 in EHB mode, 4096 in HAM mode), with per-pixel colour. There is no attribute clash.

### 4.2 The Spectrum's answer

The Spectrum has none of these. What the Spectrum does have is **a CPU that can write to display RAM at any time**, and a tradition of building in software what the Amiga has in hardware:

- **Copper bars** → Spectrum **rasterbars** (rewriting the BORD register per scanline, cycle-counted against the ULA's display fetch).
- **Blitter-style block copies** → Spectrum **`LDIR`/`LDDR`-based software blits** or precomputed table lookups.
- **Paula PCM** → Spectrum **beeper-driven PWM** or AY envelope tricks.
- **Dual-playfield parallax** → Spectrum **multiple attribute layers and timing tricks**.
- **64/4096 colours** → Spectrum **15-colour fixed palette with gigascreen interlace mixing** (see [multicolor_techniques.md](multicolor_techniques.md)).

The trade-off is stark: where the Amiga achieves these effects with a few register writes, the Spectrum achieves them by spending the entire CPU budget on per-frame raster-synchronised code. The result is that **Spectrum effects are, on a strict technical comparison, much less impressive** — but the *craft* of producing them is much more intricate.

### 4.3 What the Amiga cannot do

There are a few effects where the Spectrum wins by virtue of having *less* hardware:

- **Per-frame full-screen attribute changes**. The Amiga's bitplanes are heavy (6 bitplanes × 320×256 = 60 KB per frame for 64-colour mode). The Spectrum's attribute grid is 768 bytes. An `LDIR` of 768 bytes per frame is trivial; rewriting 60 KB on Amiga per frame is harder.
- **Cycle-exact CPU-vs-raster play**. The Amiga's Copper handles this; the CPU is not normally used for it. But on the rare Amiga demos that try CPU-cycle-precision work, the result is often superior on the Spectrum simply because the Spectrum's CPU is *always* doing it.
- **Tight 1K/4K intros**. The Spectrum's smaller RAM (48K vs 512K) and simpler I/O model make very small intros tractable. Amiga 4K intros exist but are rarer; the equivalent Spectrum work is abundant.

### 4.4 Why the comparison matters

The Amiga vs Spectrum comparison is mostly interesting for what it reveals about **technique translation**:

- A **Spectrum scener moving to Amiga** finds the platform feels luxurious — everything is hardware-assisted. The challenge shifts from "can the CPU keep up?" to "can I configure the custom chips correctly?".
- An **Amiga scener moving to Spectrum** finds the platform feels brutal — nothing is hardware-assisted; every effect is hand-built. The challenge shifts from "configure hardware" to "design cycle-counted inner loops".

Both scenes produced extraordinary work, but their aesthetics differ. Amiga demos tend toward smoothness, polish, and depth (parallax, copper-bar palettes, large sprites). Spectrum demos tend toward intensity, density, and pixel-level precision (multicolor, attribute cycling, 1-bit music).

### 4.5 The 16-bit "Amiga standard"

A particular feature of the late-1980s / early-1990s demoscene was the **"Amiga standard"**: because the Amiga was the highest-profile demoscene platform from ~1987 to ~1993, demos on weaker platforms (Spectrum, C64, ST) were often measured against Amiga work. A Spectrum demo that "looked Amiga-quality" was a high compliment; a C64 demo that "rivalled Amiga parallax" was similarly praised.

This implicit standardisation pushed the Spectrum scene toward effects that, structurally, echoed Amiga work — but built entirely in software. The Soviet scene's late-1990s software-3D tradition (see [soviet_demo_scene.md](soviet_demo_scene.md) §5.4) is a direct response to the Amiga scene's 3D tradition of the early 1990s (Future Crew, Melon, Kefrens).

### 4.6 Summary

| Question | Amiga | Spectrum |
|---|---|---|
| Smooth parallax / dual-playfield? | **Amiga** (hardware) | Spectrum (software, partial) |
| Per-scanline copper bars? | **Amiga** (Copper coprocessor) | Spectrum (cycle-counted rasterbars) |
| 4-channel sample music? | **Amiga** (Paula hardware) | Spectrum (beeper PWM or AY tricks) |
| 64/4096 colours? | **Amiga** (bitplanes/HAM) | Spectrum (15 colours, gigascreen mixing) |
| 1K/4K intros? | Possible but rarer | **Spectrum** (tighter, easier) |
| Full-screen attribute swap per frame? | Possible but expensive | **Spectrum** (768-byte `LDIR`) |

The Amiga wins on essentially every objective technical measure. The Spectrum wins only where *simplicity* itself is the advantage.

---
## 5. ZX Spectrum vs Atari ST

The Atari ST is the Spectrum's closest 16-bit cousin. Both machines came from UK-origin design houses (the Spectrum from Sinclair Research in Cambridge; the ST from Atari Corp in Sunnyvale but designed largely by Shiraz Shivji's team, drawing on earlier UK/Sinclair influences); both used off-the-shelf parts rather than custom chips; both shipped without hardware sprites or hardware scrolling.

Crucially, the **Atari ST and the Spectrum 128 share the same sound chip family**: the ST's YM2149 is essentially a higher-clocked, register-compatible variant of the Spectrum's AY-3-8912. This is the foundation of cross-pollination between the two scenes (see §9).

### 5.1 Hardware contrast

The ST is much faster and more capable than the Spectrum:

- **68000 CPU at 8 MHz** vs Z80A at 3.5 MHz. The 68000 has 32-bit internal registers, 16-bit external bus, and a far richer instruction set. Per-instruction throughput is ~2–4× higher.
- **Bitplane video** (3 or 4 bitplanes for 8/16 colours at 320×200, monochrome at 640×400) instead of the Spectrum's attribute grid. The ST has no attribute clash.
- **Hardware-blankable borders**. The ST can drop the borders and run a 320×200 full-screen display. The Spectrum's border is hardware-fixed (though it can be colour-cycled).
- **512 colours** on the palette (9-bit RGB), 16 on screen simultaneously in low-res. The Spectrum has 15 colours with no palette registers.
- **No hardware sprites, no hardware scrolling, no Copper**. The ST is essentially a 16-bit Spectrum in architecture: software does everything.

### 5.2 The ST-Shifter limitation

A notable ST-specific constraint: the **Shifter video chip** outputs pixels synchronously from a FIFO that the CPU/DMA must feed. There is no per-scanline register-update coprocessor (no Copper equivalent). ST "raster effects" therefore require:

- **Cycle-counted HBL (horizontal blank) interrupts** to update the Shifter palette mid-line. This is the ST's equivalent of Spectrum rasterbars.
- **Software-synchronised "sync scrolling"** for parallax. ST demos use cycle-counted code to fake smooth scroll by rewriting the Shifter's video address.

These techniques mirror the Spectrum's cycle-counted multicolor work, but with a much faster CPU. The result is that **ST demos often look like Spectrum demos with vastly more colours and smoother motion**.

### 5.3 Why ST "feels" like a 16-bit Spectrum

Several factors make the ST/Spectrum comparison structurally similar:

1. **No custom chips.** Both platforms put the CPU in charge of everything. ST sceners and Spectrum sceners think about effects the same way.
2. **No hardware sprites.** Both scenes have robust software-sprite traditions.
3. **No hardware scrolling.** Both scenes build scrolling effects from software block-copies.
4. **Same sound chip family.** Music written for one is portable to the other (see §9).

The main differences are:

- **CPU speed**: the ST is 2–4× faster per instruction, giving it room for more sophisticated software rendering.
- **Colour depth**: the ST's 16-on-screen-512-palette gives it much more visual range than the Spectrum's 15-fixed-colours.
- **RAM**: the ST's 512K standard RAM (vs Spectrum's 48K) gives more room for precomputed tables and buffers.

### 5.4 What the ST scene gave the Spectrum scene

The ST scene pioneered several techniques that the Spectrum scene later adopted:

- **The "scroll-text" trope** (text scrolling across the bottom of the screen) was popularised by ST demos and adopted by Spectrum demos as a standard element.
- **YM-chip music composition**: ST composers developed sophisticated AY/YM techniques that Soviet composers then imported (with PT3) into the Spectrum scene.
- **Vector 3D**: the ST's faster CPU made real-time 3D easier, and ST-style vector-3D aesthetics (line-frame wireframe 3D, then filled) were adopted by the Soviet Spectrum scene.
- **The demoscene party format itself**: ST parties (especially The Computer Crossroads in Germany, the Atari ST shows in Sweden) helped establish the format that later Spectrum parties adopted.

### 5.5 What the Spectrum scene gave the ST scene

- **Tight code discipline.** The Spectrum's smaller RAM forced code compression techniques (see [compression_packing.md](compression_packing.md)) that ST coders found useful for ST 4K/64K intro categories.
- **Multicolor / attribute-cycle thinking.** ST coders experimenting with per-scanline Shifter register updates sometimes drew inspiration from Spectrum multicolor work.
- **Beeper music.** The ST has no beeper (the YM2149 is the only sound source), but Spectrum beeper-music techniques informed ST chip-music composers' approach to envelope manipulation.

### 5.6 Summary

| Question | Atari ST | ZX Spectrum |
|---|---|---|
| CPU speed for software rendering? | **ST** (8 MHz 68000) | Spectrum (3.5 MHz Z80) |
| Number of on-screen colours? | **ST** (16 from 512) | Spectrum (15 fixed) |
| Attribute clash? | **ST** (no clash, per-pixel) | Spectrum (8×8 cells) |
| AY/YM music? | Same chip family | Same chip family (cross-portable) |
| Hardware sprites? | None | None (both build in software) |
| Hardware scrolling? | None | None (both build in software) |
| 1K/4K intros? | Possible | **Spectrum** (tighter) |
| Beeper 1-bit music? | n/a (ST has no beeper) | **Spectrum only** |

The ST is a "Spectrum with steroids" — same architectural philosophy, more capable hardware. The two scenes developed parallel traditions, with substantial music cross-pollination.

---
## 6. ZX Spectrum vs MSX

The MSX is the most architecturally similar 8-bit platform to the ZX Spectrum: both use a Z80A at ~3.5 MHz and an AY-3-8910-family sound chip. The differences lie entirely in the video architecture and the peripheral model.

### 6.1 Hardware contrast

- **CPU**: Z80A at 3.58 MHz on MSX vs 3.5 MHz on Spectrum. Almost identical effective CPU speed.
- **Sound**: MSX has the AY-3-8910 (or compatible YM2149 in MSX2+) built in from the start (all MSX models). The Spectrum 48K has only a beeper; only the Spectrum 128K has an AY.
- **Video**: MSX uses the **Texas Instruments TMS9918A** (later Yamaha V9938 on MSX2, V9958 on MSX2+). The TMS9918A provides:
  - 16-colour 256×192 mode (similar resolution to the Spectrum).
  - 32 single-colour hardware sprites (4-colour mode available), 8 per scanline.
  - Hardware scroll via `NAME TABLE BASE` register indirection (not full playfield scroll, but functional).
  - **Separate VRAM** (16 KB on MSX1) — the CPU does not see VRAM directly; it writes via port-mapped I/O to the VDP. This is a critical architectural difference.
- **Palette**: MSX1 has a fixed 15-colour palette (with one extra for transparency); MSX2 has 256 colours from 512.

### 6.2 The VRAM wall

The MSX's defining constraint — and the one that made its demoscene tradition so different from the Spectrum's — is **separate VRAM accessed via port I/O**. To write a pixel on the Spectrum, the CPU does `LD (HL),A` (7 T-states, direct). To write a pixel on MSX, the CPU does:

```z80
        LD      A,(hl)           ; or write direct
        OUT     (0x98),A         ; 11 T-states to VDP data port
        ; The VDP has an internal auto-incrementing address register
```

Each VRAM write is roughly 2–3× slower than the equivalent Spectrum RAM write. Worse, the VDP's address-register setup overhead (writing low and high address bytes via port 0x99) makes scattered writes painful.

This means MSX demos have an **indirection tax** that the Spectrum does not pay. For effects that need to rewrite the entire display every frame (multicolor, copper-style raster changes), the Spectrum is dramatically faster.

### 6.3 What the MSX does better

- **Hardware sprites** (32 sprites, 8 per scanline). MSX demos have rich software-sprite-free traditions; arcade-style games are much easier than on the Spectrum.
- **Hardware scroll** (via name-table indirection on TMS9918A; full playfield scroll on V9938/V9958). Smooth scroll is essentially free.
- **Sound from day one** — every MSX has an AY; the Spectrum had to wait for the 128K model.
- **Per-pixel colour** via the VDP's pattern/colour-table architecture (different model from the Spectrum's attribute grid, but no clash).
- **Extensions**: MSX-Music (YM2413 FM), MSX-Audio (Y8950), Moonsound (YMF278B), and the MSX's cartridge slot make adding capabilities trivial. The Spectrum's expansion model is messier.

### 6.4 What the Spectrum does better

- **Direct framebuffer access** for fast full-screen writes (multicolor tradition).
- **No VDP indirection overhead** — every CPU write to display RAM is full-speed.
- **A larger and more coherent demoscene** (especially the Soviet scene). MSX demoscene is real but much smaller, with peak activity in Japan (1986–1992), Brazil and the Netherlands (1995–2005), and a modern revival.

### 6.5 MSX scene characteristics

The MSX demoscene developed in three distinct eras:

1. **Japanese MSX era (1986–1992)**: focused on games and demo-scene-precursors, with Konami's cartridges as the high-water mark. Konami's *Metal Gear*, *Knightmare*, *Parodius* etc. on MSX are essentially pre-demoscene showcases of VDP capability.
2. **Brazilian / Dutch / Scandinavian era (1995–2005)**: the *Western* MSX demoscene, focused on demos that pushed the VDP. Brazilian groups (especially the *MSX Revival* community) and Dutch groups (Dutch MSX Association) dominated.
3. **Modern revival (2010–present)**: small but active, with new demos released at MSX fairs and online compos.

Notably, the MSX scene **never developed a multicolor tradition** of the Spectrum kind. The VDP indirection tax makes per-scanline full-screen attribute changes impractical. Instead, MSX demos developed a strong tradition of **hardware-sprite multiplexing** and **scrolling tilemap effects**, both of which the VDP does natively.

### 6.6 The MSX-vs-Spectrum "feud"

There is a long-standing, mostly-friendly feud between MSX sceners and Spectrum sceners. Common positions:

- MSX sceners point out that the MSX is more capable (sprites, scroll, sound from day one).
- Spectrum sceners point out that the Spectrum scene produced more demo work, more sophisticated effects (multicolor), and a much longer continuous tradition.

Both points are correct. The MSX has more capable hardware; the Spectrum has the more impressive demoscene. This is a useful counterexample to the assumption that "more capable hardware = better demoscene" — what matters is what the scene actually does with the hardware, and the Soviet Spectrum scene in particular was exceptionally productive.

### 6.7 Note on openMSX

A frequent misconception: **openMSX is the canonical MSX emulator, not a Spectrum emulator**. Spectrum emulation is dominated by Unreal Speccy, Fuse, ZEsarUX, EightyOne, and SpecEmu. openMSX is exclusively for the MSX family. The two scenes share emulation-related discussion (VDP-on-FPGA, cycle-accurate Z80 emulation) but the emulators are separate.

### 6.8 Summary

| Question | MSX | ZX Spectrum |
|---|---|---|
| CPU speed? | Essentially identical (3.58 vs 3.5 MHz) | Essentially identical |
| Direct framebuffer access? | **MSX pays VDP indirection tax** | **Spectrum** (direct RAM writes) |
| Hardware sprites? | **MSX** (32 single-colour) | Spectrum (none) |
| Hardware scroll? | **MSX** (TMS9918A indirection) | Spectrum (none) |
| AY from base model? | **MSX** (every MSX) | Spectrum 128K only |
| Per-scanline attribute changes? | Hard (VDP indirection) | **Spectrum** (multicolor) |
| Demoscene size? | Smaller (Western-focused) | **Spectrum** (much larger, esp. Soviet) |

The MSX is more capable on paper; the Spectrum scene produced more work. The architectural difference (direct RAM vs VDP indirection) is the single biggest reason the Spectrum developed the multicolor tradition and the MSX did not.

---
## 7. ZX Spectrum vs Amstrad CPC

The Amstrad CPC (464, 664, 6128), released in 1984, is the third Z80+AY platform. Like the Spectrum, it has no custom video co-processor and no hardware sprites. Like the Spectrum 128, it has an AY-3-8912. But the CPC's video architecture — a Gate Array ASIC that produces a real linear framebuffer — is structurally different from both the Spectrum's attribute-grid framebuffer and the MSX's VDP indirection.

### 7.1 Hardware contrast

- **CPU**: Z80A at 4 MHz on CPC vs 3.5 MHz on Spectrum. CPC is ~14% faster in raw clock, but with **wait-states imposed by the Gate Array** during display fetch (the GA reads 2 bytes per μs from RAM, denying the CPU access). Effective CPU speed is ~3.3 MHz — comparable to the Spectrum with contention.
- **Sound**: AY-3-8912, same chip as the Spectrum 128/+2. Same register layout.
- **Video**: Amstrad Gate Array drives three modes:
  - **Mode 0**: 160×200, 16 colours (from 27-colour fixed palette).
  - **Mode 1**: 320×200, 4 colours (from 27).
  - **Mode 2**: 640×200, 2 colours (from 27).
- **Linear framebuffer**: CPC display RAM is a true linear framebuffer (no attribute indirection, no weird Spectrum byte interleaving). Pixel x,y → address is a simple formula. This is the CPC's biggest advantage.
- **Palette**: 27 fixed colours (3 bits R × 3 bits G × 3 bits B, with hardware hue/saturation adjustments giving 27 effective hues). Modest but more flexible than the Spectrum's 15.
- **Per-pixel colour** in all modes — no attribute clash.

### 7.2 Why the CPC didn't develop a multicolor tradition

The CPC has direct framebuffer access (like the Spectrum) and per-pixel colour (unlike the Spectrum). One might expect the CPC to have developed an even more sophisticated multicolor tradition. It did not, for two reasons:

1. **Resolution tradeoff.** To get 16 colours on the CPC, you drop to 160×200 — too low for the Spectrum-style "high-resolution overlay" effects. To get 320×200 you only have 4 colours. There is no mode that gives both high resolution and high colour count.
2. **CRTC dependency for raster effects.** The CPC's CRT controller (a Hitachi HD6845S or equivalent) *can* be reprogrammed mid-frame, but it requires more cycle-counting than the Spectrum's BORD register trick. CPC raster effects exist (*raster splits*, *CRTC tricks*) but are more delicate than Spectrum multicolor.

Instead, CPC demos developed:

- **Mode-0 16-colour artwork** (the basis of the famous CPC pixel-art tradition).
- **CRTC split-screen effects** (changing the CRTC's display address mid-frame).
- **Massive software-sprite engines** in Mode 0.
- **Pre-rendered full-screen animations** (similar to Soviet TS-Config work).

### 7.3 CPC scene characteristics

The CPC scene is small but persistent:

- **UK and France** were the primary homelands (Amstrad was a British company; the CPC sold well in France).
- **The CPC demoscene peaked later than the Spectrum's**, roughly 1990–1998, partly because the CPC's larger RAM (6128 = 128K) and cleaner architecture made it a more attractive platform for advanced work after the Spectrum scene contracted.
- **The CPC scene's modern revival (2010–present)** is small but active, with releases at Outline, Xylonium, and online compos.

### 7.4 AY music on the CPC

Because the CPC has the same AY-3-8912 as the Spectrum 128, AY-music cross-pollination is straightforward. The CPC's AY is clocked slightly differently (1 MHz vs the Spectrum 128's 1.773450 MHz on the 128K model), so playback of a `.pt3` or `.ym` file on the CPC requires tempo adjustment, but the format is otherwise portable. CPC music disks often include Spectrum-derived music.

### 7.5 Why the CPC vs Spectrum comparison is interesting

The CPC is the "cleanest" comparison to the Spectrum: same CPU family, same sound chip, both software-rendered, but with a different video architecture. Looking at the two scenes reveals how the choice of video architecture shaped everything downstream:

- The Spectrum's **attribute grid** produced attribute clash → produced multicolor (to escape the grid) → produced gigascreen (to escape the fixed palette).
- The CPC's **linear framebuffer with mode-switching** produced mode-0 artwork → produced CRTC split effects → produced pre-rendered full-frame animation.

Both scenes produced sophisticated work; neither was clearly superior. The architectural decisions made in 1982 (Spectrum) and 1984 (CPC) played out over decades of scene work.

### 7.6 Summary

| Question | Amstrad CPC | ZX Spectrum |
|---|---|---|
| CPU speed? | **CPC** (4 MHz, ~3.3 MHz effective) | Spectrum (3.5 MHz, ~2.9 MHz effective contended) |
| Sound chip? | Same (AY-3-8912) | Same |
| Linear framebuffer? | **CPC** (true linear) | Spectrum (interleaved, attribute-indirect) |
| Per-pixel colour? | **CPC** (in all modes) | Spectrum (8×8 attribute grid) |
| Hardware sprites? | None | None |
| Mode-switching mid-frame? | **CPC** (3 modes via GA) | Spectrum (single mode) |
| Multicolor 8×1 tradition? | n/a (CPC has per-pixel) | **Spectrum** (signature technique) |
| Demoscene size? | Smaller (UK/France) | **Spectrum** (much larger) |

The CPC has a cleaner framebuffer; the Spectrum has a much larger scene. Both produced distinctive work.

---
## 8. Other Peers

Beyond the C64, Amiga, ST, MSX, and CPC, several other platforms occasionally appear in cross-platform demoscene comparisons. These are not major Spectrum rivals but are mentioned here for completeness.

### 8.1 BBC Micro and Acorn Electron

The BBC Micro (1981) is a 6502-based UK platform with a custom video ULA (Teletext mode, 2/4/16-colour modes, 160×256 / 320×256 / 640×256). It has a small but persistent UK demoscene. Comparisons to the Spectrum are uncommon because the Beeb has per-pixel colour and modest hardware scrolling. The BBC scene and Spectrum scene were contemporaries in the UK but operated in parallel with minimal overlap.

### 8.2 Apple II and Apple IIGS

The Apple II (1977) is older than the Spectrum and had a small Western demoscene. The Apple IIe/IIc have 280×192 hi-res with quirky colour encoding (1-bit-per-pixel producing colours via NTSC artefacts). The Apple IIGS (1986) is a 16-bit platform with Ensoniq DOC sound. Both are essentially irrelevant to the Spectrum scene; there is no significant cross-pollination.

### 8.3 NES (Famicom)

The Nintendo Entertainment System (1983/1985) is a games console with sophisticated hardware (PPU with hardware sprites, tilemaps, scanline IRQs). The NES has a tiny modern "demo scene" but no historical demoscene (it was a closed console platform). NES coding techniques have influenced modern Spectrum coders (especially in cycle-counting discipline), but the two are not peers.

### 8.4 MSX2, MSX2+, MSX turbo R

The MSX2 (1985) adds the Yamaha V9938 VDP (80-column mode, hardware scroll, hardware multipage display, 256×212 in 16/256 colours) and a real-time clock. The MSX2+ (1988) adds the V9958 with hardware yuhaku scroll and interlaced scan. The turbo R (1990) is the final MSX model with a 16-bit R800 CPU at ~7 MHz. All three are direct descendants of MSX1 and have small but active scenes. Comparison to the Spectrum is similar to MSX1 but the MSX2+ and turbo R are substantially more capable.

### 8.5 SAM Coupé

The SAM Coupé (1989) is a UK-developed "Spectrum-compatible" platform with substantially enhanced hardware (256×192 in 16 colours, or 512×192 in 4 colours, from 128-colour palette; built-in disk; 256K RAM). It was marketed as the "Spectrum's successor". A small demoscene developed around it, including some cross-port work from the Spectrum scene. SAM Coupé demos occasionally appear in Spectrum-adjacent archives but the platform is essentially a separate ecosystem.

### 8.6 Enterprise 64/128, Memotech MTX, Tatung Einstein

Other 8-bit Z80 platforms from 1983–1985 with tiny demoscene followings. They are mentioned in cross-platform discussion but have no real impact on the Spectrum scene.

### 8.7 Modern platforms (PC, web, mobile)

Modern demos target PC (Windows, Linux), browsers (JavaScript/WebGL), and occasionally mobile. These are not comparable to the Spectrum; cross-platform discussion focuses on whether modern demos preserve demoscene values (technical showcase, aesthetic coherence, constraint-driven design) that originated on 8-bit/16-bit platforms. The Spectrum scene's influence on modern demos is mostly indirect — through technique preservation, training of coders who later moved to PC demos, and the cultural continuity of party-going.

---
## 9. The AY/YM Bridge

The single biggest piece of cross-pollination between 8-bit/16-bit demoscenes is the **AY-3-8910 / YM2149 sound chip family**. The same chip — with minor variations — appears in:

- **ZX Spectrum 128/+2/+3**: AY-3-8912 at 1.773450 MHz (clock / 2 input to chip).
- **Atari ST (all models)**: YM2149 at 2 MHz (clock / 2 input).
- **MSX1**: AY-3-8910 at 1.789773 MHz (clock / 2 input).
- **MSX2/2+/turbo R**: YM2149 or YMZ284 (compatible clones) at the same clock.
- **Amstrad CPC 464/664/6128**: AY-3-8912 at 1 MHz (clock / 4 input).
- **Mockingboard (Apple II)**: dual AY-3-8910.
- **SpecDrum, TurboSound, General Sound (Spectrum extensions)**: AY/YM-family chips.
- **Intellevision, Vectrex**: AY-3-8910 (early consoles).

This hardware-level compatibility created an unusual situation: **music written for one platform's AY could be played on another's, sometimes with only minor adjustments**. The result was a cross-platform music ecosystem that transcended individual scenes.

### 9.1 What the chips have in common

All AY/YM-family chips provide:

- **3 independent tone channels** (square wave, programmable period).
- **1 noise channel** (programmable noise period, mixable into any combination of tone channels).
- **1 envelope generator** (programmable attack/decay, shareable across channels).
- **15 volume levels per channel** (0=silent, 15=max), or envelope-driven volume.
- **28 write-only registers** organised as: 3×2 tone period (R0–R5), 1×1 noise period (R6), 1×1 mixer (R7), 3×1 channel volume (R8–R10), 1×2 envelope period (R11–R12), 1×1 envelope shape (R13), and 2× I/O ports (R14–R15, AY-8910 only).

The register layout is identical across the AY-3-8910, AY-3-8912 (one I/O port instead of two), and YM2149 (which adds a different envelope mode and slightly different analogue output).

### 9.2 Differences that matter

- **Clock speed.** Each platform clocks the chip at a different frequency, so the same register value produces a different pitch. A note table compiled for the Spectrum 128 will play back at a slightly different pitch on ST, MSX, or CPC. Players must use a per-platform note table.
- **I/O port presence.** AY-3-8910 has two 8-bit I/O ports (used for joysticks, printers, etc. on MSX); AY-3-8912 has one (used on Spectrum and CPC for the keystick port); YM2149 has two but their usage varies by platform.
- **Envelope shape.** The YM2149 has a slightly different envelope generator with one extra mode. Most music does not use the difference.
- **Output stage.** The YM2149 has a 2V DC offset on outputs; the AY-3-8910 has a 0.2V offset when the envelope is active. This affects analogue mixing on real hardware but is irrelevant for register-level cross-portability.

### 9.3 The shared music format ecosystem

Several AY-music formats became cross-platform:

- **`.ym` (YM format)**: a dump of register writes per frame, originally from Atari ST tools but readable on all AY/YM platforms. The standard archival format for AY music.
- **`.pt2` and `.pt3` (Pro Tracker)**: the Soviet-developed module formats. PT3 in particular spread from the Spectrum scene to ST, MSX, and CPC communities; it is still the de facto global AY-music module format.
- **`.ay` (AY format)**: a wrapper format that bundles a `.ym` dump with platform-specific bootstrap code, so the same file plays correctly on Spectrum, ST, MSX, or CPC.
- **`.sndh` (SNDH)**: a 68000-executable format native to the ST scene, equivalent to the Spectrum's music-disk module format.

A sophisticated cross-platform infrastructure exists for converting between these formats. The ZX Music Editor cross-development toolchain can export the same composition as `.pt3` (Spectrum/MSX/CPC) or as `.ym` (any AY platform).

### 9.4 The shared composer community

Several AY composers are recognised across multiple scenes:

- **Ben Daglish** (C64 SID primarily, but composed for AY platforms too).
- **Jochen Hippel (Mad Max)**: ST AY composer whose modules are routinely ported to Spectrum.
- **Yerzmyey**: Polish Spectrum AY composer; widely covered by ST and MSX musicians.
- **Nik-O, Ironman, MW, ASBel, Miguk**: Soviet Spectrum PT3 composers whose modules circulate in ST and MSX archives.
- **Shiru**: Russian multi-platform composer who wrote AY music for Spectrum, NES, Sega Master System, and PC.

The shared AY aesthetic (rich ornaments, sample-driven envelopes, driving noise rhythm — see [soviet_demo_scene.md](soviet_demo_scene.md) §6.5) is now a cross-scene standard, partly because of this format portability.

### 9.5 What this means for cross-platform comparison

The AY bridge means that **music is the one area where the Spectrum, ST, MSX, and CPC scenes are genuinely the same scene, not four separate scenes**. A demo's AY music is portable across platforms in a way that its graphics and code are not. This makes AY music a useful lingua franca for cross-platform contact.

It also means the Spectrum's PT3 ecosystem (see [soviet_demo_scene.md](soviet_demo_scene.md) §6) had cultural reach well beyond the Spectrum scene itself. When Soviet sceners exported PT3 modules to ST and MSX composers, they were exporting the Soviet AY aesthetic along with it.

---
## 10. What the Spectrum Excels At — and Where It Loses

After comparing the Spectrum to its peers across §3–§9, the platform's distinctive strengths and weaknesses become clear. This section summarises them.

### 10.1 Where the Spectrum excels

The Spectrum is the **best platform in the comparison set** for:

1. **Multicolor effects** (8×1 or 8×2 attribute resolution). The combination of direct RAM access + small attribute grid + cycle-countable ULA behaviour makes per-scanline attribute manipulation uniquely tractable. No other major platform can do this as effectively.
2. **Gigascreen (interlace-based colour mixing).** The 50 Hz frame rate and the Spectrum's hard 15-colour palette paradoxically enable a sophisticated 15-colour perceived-colour mixing technique that does not work the same way on per-pixel-colour platforms.
3. **1-bit beeper music.** The beeper is a unique Spectrum feature. The Soviets and the Polish scene developed the only true 1-bit music composition tradition in the demoscene world (see [1bit_music_scene.md](1bit_music_scene.md)).
4. **Tight 1K / 4K intros.** The Spectrum's small RAM and simple I/O model make very small demos tractable. The size-coding tradition on Spectrum is the deepest of any 8-bit platform (see [size_coding.md](size_coding.md)).
5. **Full-screen attribute buffer effects.** Because the attribute grid is only 768 bytes, an `LDIR` copy per frame is essentially free. This enables a class of effects that other platforms cannot match without rewriting significantly more memory.
6. **A scene size and continuity unmatched by other Z80 platforms.** The Soviet/post-Soviet scene alone produced thousands of demos from 1993 to the present. The MSX, ST, and CPC scenes are all much smaller.

### 10.2 Where the Spectrum loses

1. **Hardware sprites.** C64 has 8 multicolour sprites; MSX has 32 single-colour; Amiga has 8 dual-playfield sprites. Spectrum has zero. All moving-object work is software-rendered.
2. **Hardware scrolling.** C64, MSX, and Amiga all have hardware playfield scrolling. Spectrum has none. All scrolling is software.
3. **Per-pixel colour.** C64, MSX (pattern-table indirection), CPC, ST, Amiga — all give per-pixel colour. Spectrum's 8×8 attribute grid produces attribute clash.
4. **Music sophistication.** The SID (C64) and Paula (Amiga) are fundamentally more capable chips than the AY-3-8912. The AY is good — and the Soviet scene pushed it to its limits — but it cannot match the SID's filter or Paula's PCM.
5. **CPU throughput.** 3.5 MHz Z80 is competitive with the C64's 1 MHz 6510 (per-instruction, roughly), but the Amiga's 7 MHz 68000 and the ST's 8 MHz 68000 are 2–4× faster in effective throughput.
6. **Real-time sample playback.** Paula on Amiga plays four channels of 8-bit PCM via DMA — trivially. SID and AY require CPU bit-banging for any sample work; the Spectrum beeper's 1-bit output is the most constrained of all.

### 10.3 The paradox of constraint

The pattern from §10.1 and §10.2 is the same pattern visible across all demoscene platforms: **constraint produces tradition**. The Spectrum's lack of hardware support forced the development of distinctive traditions (multicolor, gigascreen, beeper music, size coding) that more capable platforms did not need. The C64's hardware sprites produced a strong sprite-multiplexing tradition; the Amiga's Copper produced a copper-bar tradition; the Spectrum's absence produced its own counter-traditions.

This is why cross-platform comparison matters: it reveals that what looks like a deficit ("the Spectrum has no sprites") is also an enabling condition ("the Spectrum developed software-sprite and attribute-cycle traditions that no other platform matched"). The two halves cannot be separated.

---

## 11. Technique Portability Matrix

The table below summarises which Spectrum techniques transfer to other platforms, and which ones other platforms' techniques transfer to the Spectrum.

| Technique | Originated on | Transfers to Spectrum? | Transfers from Spectrum? | Notes |
|---|---|---|---|---|
| **Hardware sprites** | C64 / Amiga / MSX | No (Spectrum has none) | n/a | Spectrum builds software sprites instead. |
| **Hardware smooth scroll** | C64 / Amiga / MSX | No (Spectrum has none) | n/a | Spectrum builds software scroll. |
| **Multicolor 8×1 / 8×2** | Spectrum | n/a | Yes (CPC: possible but rarely done) | Spectrum-exclusive refinement. |
| **Gigascreen (frame interlace colour mixing)** | Spectrum (Soviet) | n/a | Yes (any 50 Hz platform with attribute grid; but pointless on per-pixel platforms) | Works only on attribute-clash platforms. |
| **Copper bars** | Amiga | Yes (Spectrum rasterbars via BORD register) | Yes (ST has HBL version) | Universal technique. |
| **Tracker-module music** | Amiga (MOD) / ST (YM) | Yes (PT3) | Yes (Spectrum's PT3 → ST, MSX, CPC) | See §9. |
| **1-bit beeper music** | Spectrum (and Apple II) | n/a | No (no equivalent hardware on C64/Amiga/ST/MSX/CPC) | Spectrum-only tradition. |
| **Vector 3D (wireframe)** | ST / Amiga | Yes (Spectrum at lower frame rate) | Yes (ST/Amiga's richer visuals influenced Soviet Spectrum scene) | Universal but capability scales with CPU. |
| **Filled-polygon 3D** | ST / Amiga / PC | Yes (Spectrum with attribute-cell texturing) | Yes (Soviet scene's polygon work was at world-class level for late 1990s) | Soviet Spectrum scene peak. |
| **Disk-streamed multicolor video** | Spectrum (TS-Config) | n/a | No (hardware-specific extension) | Pentagon-only. |
| **Cruncher-packing for intros** | All 8-bit platforms | Yes | Yes (LZ4, LZSA, ZX0 cross-pollinated from PC to all 8-bits) | See [compression_packing.md](compression_packing.md). |
| **SID-filter sweeps** | C64 | No (no filter on AY) | n/a | C64-exclusive. |
| **Tracker-format music portability** | All platforms | Yes | Yes | Cross-platform AY (§9). |

### 11.1 What the matrix shows

The matrix reveals two categories of technique:

1. **Universal techniques** (copper bars / rasterbars, vector 3D, filled polygons, tracker music) that all platforms develop in their own way, with quality scaling with hardware capability.
2. **Platform-specific techniques** (multicolor, gigascreen, beeper music, TS-Config video) that exist only on platforms with the right combination of architectural features.

The Spectrum's distinctive techniques are mostly in the second category — which is what gives the Spectrum scene its specific identity. If you removed the Spectrum from the demoscene, these techniques would never have existed.

---
## 12. Relative Scene Sizes and Activity Levels

Different demoscene platforms have very different sizes and activity levels. The table below provides approximate, order-of-magnitude estimates for active sceners and annual demo releases at each platform's peak and today (2025). Numbers are rounded and should not be cited as authoritative — they are indicative.

| Platform | Peak era | Peak annual demos (approx) | Peak active sceners (approx) | 2025 annual demos | 2025 active sceners |
|---|---|---|---|---|---|
| **ZX Spectrum** (all regions) | 1993–2005 | ~150/year | ~1000 | ~25/year | ~80 |
| **Commodore 64** | 1985–1995 | ~120/year | ~1500 | ~40/year | ~250 |
| **Amiga** (OCS/ECS/AGA) | 1988–1995 | ~250/year | ~2000 | ~80/year | ~400 |
| **Atari ST** | 1987–1995 | ~80/year | ~600 | ~10/year | ~80 |
| **MSX** (all generations) | 1986–1992 (Japan), 1995–2005 (West) | ~40/year (Japan), ~15/year (West) | ~400 (Japan), ~150 (West) | ~15/year | ~70 |
| **Amstrad CPC** | 1986–1995 | ~30/year | ~300 | ~10/year | ~50 |

### 12.1 Reading the table

- The **Amiga scene** is the largest of all retro-platform scenes, both at peak and today. This is partly because the Amiga had the broadest commercial reach in the demoscene's formative years (1987–1995) and partly because AGA-era Amiga work (A1200/A4000) extended the platform's life.
- The **C64 scene** is the second-largest and has the longest continuous activity (1985–present, with no break).
- The **ZX Spectrum scene** is third-largest overall, but at its Soviet peak (1998–2005) it was *the largest 8-bit scene in the world*. This is the Spectrum scene's distinctive historical achievement.
- The **ST, MSX, and CPC scenes** are all much smaller. Each is real and active, but none approached the scale of the Spectrum, C64, or Amiga scenes.

### 12.2 Why size matters

Scene size affects:

- **Quality pressure**: larger scenes produce more competition, which produces higher quality at the top end.
- **Documentation**: larger scenes leave more primary-source material (demos, diskmags, source code, interviews) for future historians.
- **Continuity**: larger scenes survive generational turnover better; small scenes die when one generation of sceners retires.
- **Cross-pollination**: larger scenes are more likely to influence other scenes (the Spectrum's PT3 format influenced ST, MSX, CPC scenes; the Amiga's MOD format influenced everything).

The Spectrum scene's size — particularly its Soviet peak — is the reason it has the most distinctive body of work among 8-bit platforms. It was large enough to develop deep traditions, sustain multiple sub-scenes (Western, Soviet, modern revival), and produce work that other scenes referenced.

### 12.3 The 2025 picture

As of 2025, all major retro demoscene platforms continue to be active. The Amiga scene remains the largest (driven by Amiga-branded FPGA hardware like the A500 Mini, MNT VA2000, and the MiSTer Amiga core). The C64 scene is second-largest (with the MEGA65 and Ultimate 64 as new hardware). The ZX Spectrum scene is third (driven by the ZX Spectrum Next, ZX Uno, MiSTer Spectrum core, and the ongoing Forever party). The ST, MSX, and CPC scenes are smaller but continue to release new work.

The 2020s have seen a general revival of retro-demoscene activity, partly driven by new hardware (FPGA clones), partly by the ease of cross-development (modern PC tools targeting retro platforms), and partly by the cultural effect of the demoscene's 2021 UNESCO recognition (see [demoscene_history.md](demoscene_history.md) §10).

---

## 13. Cross-References and License

### 13.1 Articles in this section

- [demoscene_history.md](demoscene_history.md) — full cultural narrative; the comparisons here are the technical complement.
- [soviet_demo_scene.md](soviet_demo_scene.md) — deep dive on the largest ZX scene sub-tradition; the AY-bridge discussion in §9 references its §6.
- [compression_packing.md](compression_packing.md) — Soviet packer lineage; the size-coding tradition cross-pollination.
- [multicolor_techniques.md](multicolor_techniques.md) — full technical treatment of multicolor and gigascreen (referenced in §3, §4, §7, §10, §11).
- [effects_catalog.md](effects_catalog.md) — catalog of effects; cross-referenced from the technique portability matrix.
- [demo_frameworks.md](demo_frameworks.md) — Spectrum demo framework conventions.
- [notable_demos.md](notable_demos.md) — technical analysis of landmark demos.
- [1bit_music_scene.md](1bit_music_scene.md) — the Spectrum-only beeper tradition.
- [size_coding.md](size_coding.md) — the Spectrum's tight-intro tradition.

### 13.2 Hardware documentation

- [../02_hardware/original/ula_architecture.md](../02_hardware/original/ula_architecture.md) — original Spectrum ULA architecture (referenced in §3, §4).
- [../02_hardware/clones/README.md](../02_hardware/clones/README.md) — Soviet clones including the Pentagon.
- [../02_hardware/clones/clone_timing.md](../02_hardware/clones/clone_timing.md) — contention timing differences across clones.
- [../06_sound/synthesis/ay_ym_synthesis.md](../06_sound/synthesis/ay_ym_synthesis.md) — AY/YM sound synthesis (cross-platform reference).

### 13.3 External primary sources

- **Demozoo.org** — cross-platform archive; primary source for party results and demo release dates.
- **Pouët.net** — cross-platform demo archive; especially strong on C64, Amiga, ST.
- **CSDb.dk** — Commodore 64 Scene Database; the canonical C64-scene archive.
- **Hall of Light** (hol.abime.net) — Amiga game/demo archive.
- **AtariLegend**, **atarimania.com** — Atari ST archives.
- **Generation-MSX** (generation-msx.nl) — MSX database.
- **CPC-Wiki** (cpc-wiki.eu) — Amstrad CPC archive.
- **zxdemo.org**, **zxart.ee**, **zx-pk.ru**, **bbb.retroscene.org** — Spectrum archives (see [soviet_demo_scene.md](soviet_demo_scene.md) §10.3).

### 13.4 Key reference works

- **Andrew Owen / Raahir Ahmad**, "ZX Spectrum Hardware Manual" — primary reference for ULA timing.
- **Christian Bauer**, "The Secret of the Amiga Hardware" — primary reference for Amiga OCS chipset.
- **Rob nack/dKT**, "Commodore 64 Programmer's Reference Guide" — primary reference for VIC-II/SID.
- **Don French**, "Atari ST Profibuch" — primary reference for ST hardware.
- **MSX RED Book** — primary reference for MSX architecture.
- **The Unofficial Amstrad WWW Repository** — primary reference for CPC Gate Array.

---

## License

This article is released under the **Creative Commons Attribution-ShareAlike 4.0 International License** ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)). You are free to share and adapt the material, provided you credit the original source and license derivative works under the same terms.

Hardware specifications quoted in §2 are derived from the primary datasheets and hardware manuals of the respective platforms; these are factual and not subject to copyright.
