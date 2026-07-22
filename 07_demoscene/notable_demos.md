[← Home](../README.md) · [Demoscene](README.md)

# Notable Demos — Analysis of Landmark Works

> **Scope**: This article catalogues **specific ZX Spectrum demos that pushed the platform past its perceived limits**, with analysis of what each achieved and why it mattered. It is the empirical companion to the technique-focussed articles ([effects_catalog.md](effects_catalog.md), [multicolor_techniques.md](multicolor_techniques.md), [precalc_trigonometry.md](precalc_trigonometry.md)) and the historical articles ([demoscene_history.md](demoscene_history.md), [soviet_demo_scene.md](soviet_demo_scene.md)).
>
> The article is deliberately selective: rather than list every demo ever released (Pouet.net and ZXArt.ee do that), it covers the **landmark works** that defined genres, introduced techniques, or represented the state of the art at their moment of release. Each entry includes the year, group, target platform, the techniques it pioneered or perfected, and where to find more detail.

---

## Article Roadmap

- §1 — Selection criteria: what makes a demo "notable"?
- §2 — Era categorisation: a timeline of landmark demos.
- §3 — The Crack Intro Era (1986–1989): the first generation.
- §4 — The Western Golden Age (1990–1996): demos emerge as standalone art.
- §5 — The Soviet Peak (1996–2005): the Pentagon-driven renaissance.
- §6 — The Modern Revival (2010–present): open source, Next, and cross-platform.
- §7 — Source releases, archives, and study material.
- §8 — Cross-references.

---

## 1. Selection Criteria

A demo is "notable" if it meets one or more of the following criteria. Most landmark demos meet several.

### 1.1 The Criteria

1. **Technical first** — the demo introduced a technique that had never been done before on the Spectrum: first 8×1 multicolor, first true 3D filled polygon, first per-pixel texture mapping, first TS-Config disk-streamed video.
2. **State of the art at release** — at the moment it was shown, the demo represented the best-ever implementation of a known technique: the fastest plasma, the smoothest 3D, the most multicolor cells per frame.
3. **Scene influence** — the demo shaped subsequent work: its framework was reused, its techniques were copied, its aesthetic was referenced by other groups.
4. **Party recognition** — the demo won or placed highly at a major party (Forever, Chaos Constructions, DiHalt, Outline, Nova, MSX/ZX devcon).
5. **Cross-platform impact** — the demo was known outside the Spectrum scene and influenced C64, Amiga, or PC demosceners.
6. **Source availability** — the demo's source was released, making it a teaching resource for later sceners.

A demo need not be universally admired to be notable. A technically brilliant demo with mediocre art direction still meets criterion 1 or 2. A party-winning demo with conservative technique still meets criterion 4.

### 1.2 What This Article Is Not

This article is **not**:
- A complete list of every Spectrum demo (Pouet.net and ZXArt.ee have ~5,000 entries each).
- A "top 10" ranking (the demoscene does not rank demos hierarchically).
- A critical review (opinions on art direction are subjective and out of scope).
- A tutorial (working source code is out of scope; see [size_coding.md](size_coding.md) for tutorials).

The article is a curated selection, intended to give a reader a map of the Spectrum demoscene's landmark works and a starting point for further study.

### 1.3 Caveat on Specific Titles

Specific demo titles and group names are listed where they are well-documented in public archives (Pouet.net, ZXArt.ee, scene Wikipedia articles). In a few cases, the article refers to demos by category rather than by name — this is deliberate, either because the demo's authorship is disputed, because multiple demos share the same technique, or because the article's author cannot verify details. Readers seeking complete lists should consult the archives directly (§7).

---

## 2. Era Categorisation

The Spectrum demoscene has four distinguishable eras, each with its own technological baseline and aesthetic conventions. The landmark demos of each era pushed against the baseline of their day; what was groundbreaking in 1989 was routine by 1996.

### 2.1 The Four Eras

| Era | Years | Hardware baseline | Musical baseline | Defining innovation |
|---|---|---|---|---|
| **Crack Intro** | 1986–1989 | 48K | Beeper | The demo as standalone artefact (separate from the cracked game) |
| **Western Golden** | 1990–1996 | 48K, +2A/+3 | AY (PT1/PT2) | The multi-part "megademo" with effect transitions |
| **Soviet Peak** | 1996–2005 | Pentagon 128K | AY (PT3) | 8×1 multicolor, event-list frameworks, FidoNet distribution |
| **Modern Revival** | 2010–present | 128K, Pentagon, TS-Config, Next | AY + beeper + PCM | Open-source frameworks, cross-platform binaries, ZX Spectrum Next |

A demo's significance is judged against its era. A 1991 demo that achieved two-effect sequencing was groundbreaking; a 2005 demo with the same technique was retro. This article treats each era on its own terms.

### 2.2 The Timeline at a Glance

A non-exhaustive timeline of landmark demos, with more detail in the era-specific sections (§3–§6):

```
1986-1987: First crack intros with beeper music and basic scrollers
1989:      First "demo" separate from cracked software (Western Europe)
1991:      First multi-part demos (3-5 parts with hard cuts)
1993:      Soviet scene emerges; first Russian-language demos
1996:      First PT3-driven demos; first event-list frameworks
1997-1998: 8×1 multicolor perfected on the Pentagon
2000:      First TS-Config demos; disk-streamed multicolor
2003:      "Peak" Pentagon era — most complex stock-Spectrum demos
2005-2010: Transition era; many sceners move to other platforms
2010:      Modern revival begins; first Github-hosted frameworks
2017:      ZX Spectrum Next Kickstarter hardware shipped
2020-2024: Next-targeted demos; cross-platform frameworks mature
```

### 2.3 Geographic Distribution

Landmark demos are not evenly distributed geographically. The vast majority of post-1996 landmark demos come from the **post-Soviet space** (Russia, Ukraine, Belarus, Kazakhstan, the Baltic states), reflecting the Soviet scene's scale and continuity. Western Europe (UK, Germany, Finland, Poland, Czech Republic, Slovakia) produced most of the pre-1996 landmarks and a smaller but steady stream afterwards. The North American and Asian scenes have produced few Spectrum-specific landmarks.

The geographic split matters because the two traditions developed **different aesthetic priorities**: Western demos tend to emphasise coding tricks and effect variety; Soviet demos tend to emphasise multicolor richness and musical sophistication. The landmark works of each tradition are not directly comparable.

### 2.4 The Article's Scope Limits

Specific titles listed in §§3–6 are limited to those that meet at least one of the criteria in §1.1 *and* that are documented in publicly accessible archives as of 2024. Demos that exist only in private collections, demos with disputed authorship, and demos that were never publicly released are excluded. The result is inevitably incomplete — the Spectrum demoscene has produced thousands of demos, and many worthy titles are omitted simply for space.

---

## 3. The Crack Intro Era (1986–1989)

The first generation of Spectrum demos were **crack intros** — small pieces of code prepended to pirated games by cracking groups. The intro played before the game loaded, displaying the group's name, the names of the cracker and supplier, a few greetings, and occasionally a simple visual effect or piece of music.

### 3.1 The Form of an Early Crack Intro

A typical 1987 crack intro contained:

- A **title screen** with the group's logo (often hand-drawn pixel art, sometimes a converted font).
- A **scroll text** — a horizontally moving text line at the bottom of the screen, typically 40 characters wide, with the group's "news" and greetings to other groups.
- A **simple visual effect** behind the scroll text: animated colour bars (border-only), a bouncing sprite, or a static image.
- **Beeper music**: a single-voice melody played by toggling the speaker at a fixed rate. The music had no envelopes, no chords, no percussion — just a sequence of pitched beeps.

Total code size: typically 2–8 KB. Total music data: typically 200–500 bytes.

### 3.2 Why Crack Intros Matter

The crack intro is the **origin of the demoscene** as a distinct cultural form. Three things made it significant:

1. **It separated the demo from the game**. Before crack intros, the only "demos" were the game's own attract mode. The crack intro was the first time a Spectrum user saw original code that wasn't part of a commercial product.
2. **It established the competition**. Crackers competed on intro quality because intro quality was a proxy for cracker skill. The groups with the best intros (The Surge, Flash, Ikari, MAD, Lord Blagger's tools) attracted the best suppliers.
3. **It built the techniques**. The scroll text, the bouncing sprite, the colour bars, the beeper melody — these were the building blocks that the demoscene later refined into plasma, tunnel, and multicolor. Every later technique has an ancestor in a 1987 crack intro.

### 3.3 The Hardware Baseline

The crack intro era was almost entirely **48K Spectrum**. The 128K and +2 were available from 1986 but were expensive and rare; most crackers worked on the 48K they already owned. This meant:

- **No AY chip** — music was beeper-only.
- **No banked memory** — all code and data lived in the 48K address space.
- **No disk** — everything loaded from tape, so intros had to be small enough to fit in the load buffer alongside the cracked game.

These constraints shaped the aesthetic of the era: small, tight, focused on what the 48K could do well.

### 3.4 Notable Groups of the Era

Specific demo titles from this era are difficult to verify today — most crack intros were unsigned or attributed only by rumour. Well-documented groups active in this period include:

- **The Surge** (UK) — early beeper-music pioneers.
- **Ikari** (European, multi-national) — prolific crackers with distinctive intro style.
- **MAD** — early Hungarian group, part of the Eastern European tradition that later fed into the Soviet scene.
- **Lord Blagger** (UK) — produced well-known cracking tools and accompanying intros.

The intros themselves are mostly anonymous — viewers in 1987 knew them by group, not by title. ZXArt.ee and Pouet.net catalogue many of these as "intro" or "cracktro" without specific titles.

### 3.5 The Transition to Standalone Demos

Around 1988–1989, groups began releasing **intros without an accompanying cracked game** — standalone demos whose only purpose was to show off. This was a critical shift: it removed the size constraint (the demo no longer had to fit alongside a game) and the thematic constraint (the demo no longer had to advertise cracking services).

The first standalone Spectrum demos (1989) were essentially crack intros repackaged: scroll text, beeper music, simple effect, ~4 KB total. Within a year (1990–1991), they had grown into multi-part "megademos" with effect transitions, AY music, and the structure that would dominate the next era.

### 3.6 What a 1989 Viewer Saw

To convey the leap from crack intro to early standalone demo, here is what a typical 1989 Spectrum demo looked like:

- **Load**: tape-loading screen with the group's name in large font.
- **Part 1 (20 seconds)**: scroll text over a colour-bar effect, beeper music playing.
- **Part 2 (15 seconds)**: a single rotating wireframe cube (16-bit fixed-point), no music.
- **Part 3 (10 seconds)**: a static "greet screen" with the names of 20+ other groups.
- **End**: blank screen, music fades, demo halts.

Total: ~45 seconds, ~6 KB. By 1989 standards, this was impressive; by 1992, it would be considered a learning exercise.

---

## 4. The Western Golden Age (1990–1996)

The seven years from 1990 to 1996 are the **Western Golden Age**: the period in which the Spectrum demoscene defined itself as an art form distinct from cracking, established the multi-part "megademo" structure that would dominate for the next decade, and developed most of the techniques that later eras would refine. The era is "Western" because almost all of its landmark works came from Western and Central Europe (UK, Germany, Czechoslovakia, Poland, Hungary, Finland); the Soviet scene was just emerging in this period and produced its first landmark works only at the very end (§5).

### 4.1 The Megademo Form

The defining innovation of the era was the **megademo**: a multi-part production in which several distinct visual effects were sequenced into a single continuous presentation, originally with hard cuts between parts and later with fades and other transitions. The form was borrowed from the Commodore 64 and Amiga demoscenes of the late 1980s, but adapted to the Spectrum's much tighter resources.

A typical 1993 megademo contained:

- An **intro part** with the demo's title, the group's logo, and a scroll text.
- Three to six **effect parts** — plasma, raster bars, a 3D wireframe object, a starfield, a zoomer, or a rotazer (see [effects_catalog.md](effects_catalog.md)).
- A **greet part** listing 30+ other groups, sometimes with mini-logos.
- A **credits part** listing the coder(s), musician(s), and graphician(s).

Each part lasted 15–45 seconds. Total runtime: 2–5 minutes. Total size: 20–60 KB. Music: continuous, with one piece per part or a single piece covering the whole demo.

The megademo form is described in detail in [demo_frameworks.md](demo_frameworks.md) §2; the frameworks that implemented it are covered in §8 of the same article.

### 4.2 The AY Revolution

The single most important technical change of the era was the **adoption of the AY-3-8912 sound chip** as the standard music platform. The 128K Spectrum (1986) and +2/+3 (1986/1987) shipped with the AY, but the chip did not become standard in the demoscene until 1990–1991, when the 128K machines became affordable enough for most sceners to own one.

The AY was a generational leap over the beeper:

- **Three-voice polyphony** instead of a single voice.
- **Hardware envelopes** for amplitude, allowing percussion-like effects without CPU cost.
- **Noise generator** for percussive and textural sounds.
- **Frequency precision** (12-bit period registers) — beeper music was limited by interrupt rate, AY music was not.

This enabled proper soundtrack-style music: melodies with bass lines, drum patterns, and arpeggios. By 1992, every serious megademo had an AY soundtrack.

### 4.3 The Music Editors

The AY revolution was driven by **music editors** — programs that let a musician compose AY music by entering notes into a tracker-like interface and then exported a binary that a demo could play. The major editors of the era were:

- **Wham Music Editor** (Jason Brookes, 1989–1991) — one of the earliest AY trackers, used in early 1990s Western demos. Limited pattern length and few effects, but established the tracker paradigm on the Spectrum.
- **Music Studio** (JSL/ROM, 1991–1993) — popular in the Western scene, with a more sophisticated pattern system and support for samples (short PCM waveforms uploaded to the AY's envelope generator).
- **Sound Tracker** (early port of the Atari ST format, ~1992) — first attempt to bring the Amiga/Atari tracker format to the Spectrum; not widely adopted but influenced later editors.
- **PT1 (Pro Tracker 1)** (Sasha Vinsent/Plz, ~1993) and **PT2** (~1994) — the editors that became standard in the Soviet scene and would dominate from 1995 onward. PT3 (1996) was the final form; see [soviet_demo_scene.md](soviet_demo_scene.md) §6.

The player code for each editor's exported binary was typically 1–2 KB; the music data for a 3-minute piece was typically 5–15 KB. Both had to fit alongside the demo code, which constrained megademo length.

### 4.4 First Effect Transitions

The first megademos (1990–1991) used **hard cuts** between parts: the screen went blank for one frame, and the next effect appeared. Hard cuts cost zero code bytes and were the only practical option for a 48K demo with limited space.

By 1992–1993, **fade to black** transitions appeared: the framework would multiply the attribute buffer by a decreasing value over 16–32 frames, then load the next effect, then ramp back up. This cost ~50 bytes of code and one frame buffer — acceptable on 128K, tight on 48K. See [demo_frameworks.md](demo_frameworks.md) §7 for the cost matrix.

**Crossfades** (mixing two effects pixel by pixel over the transition) appeared around 1994–1995, but were rare because they required two frame buffers (one for the outgoing effect, one for the incoming) and ~200 bytes of mixer code. Only the largest 128K megademos used crossfades.

### 4.5 The Czech/Slovak Scene

The most active Western-adjacent scene of the era was **Czechoslovakia** (and after 1993, the Czech Republic and Slovakia). The Czech and Slovak sceners benefited from low-cost hardware and a strong home-computer culture, and they produced a disproportionate share of the era's landmark demos.

Notable Czech/Slovak groups of the era included:

- **Liquid** (Czech, early 1990s) — among the most prolific early megademo groups. Members included Jeff Smart and others who would influence the entire scene's aesthetic.
- **Blackmail / CsL** (Czech, mid-1990s) — produced technically advanced work. The "Yes, Not No" demo (1996) is frequently cited as one of the era's peak achievements on stock hardware.
- **Contraz** (Czech) — contributed to the megademo form.
- **JUMI** and individual sceners known by handles rather than group names.

The Czech/Slovak scene hosted the first major Spectrum-specific demoparty, **Forever** (founded 1996 in Slovakia). Forever became the spiritual home of the Spectrum demoscene and remains the most important annual party for the platform. See [demoscene_history.md](demoscene_history.md) §9 for party history.

### 4.6 The Polish Scene

Poland was the other major Western-adjacent centre. Polish groups tended to bridge the Western and Soviet scenes, both geographically and culturally:

- **X-Trade Syndicate** (mid-1990s onward) — Polish group that bridged into the post-Soviet era; known for technically ambitious demos that competed directly with the Russian scene's output.
- **LANACS** and other Polish groups — participated in early megademo development.

The Polish scene also developed strong ties to the Atari and Commodore scenes, leading to cross-platform releases that ran (with different code) on the Spectrum, Atari 8-bit, and C64.

### 4.7 The Western European and Nordic Scene

In parallel with Central Europe, a smaller but significant Western scene existed in **the United Kingdom, Germany, Finland, and the Netherlands**. Western European groups tended to favour effect variety and coding tricks over multicolor richness (which required timing-precise Pentagon-style hardware that was less common in the West). Notable activity included:

- **UK groups** — direct inheritors of the crack intro tradition, producing demos that emphasised scroll-text culture and visual humour.
- **Finnish groups** — a small but technically accomplished scene, with cross-pollination to the C64 and Amiga scenes.
- **German groups** — bridges to the strong German C64 and PC scenes.

### 4.8 The Late-Period Peak (1995–1996)

By 1995, the megademo form had been refined to a high degree. The peak Western demos of 1995–1996 typically featured:

- Six to ten effect parts with fade transitions.
- PT2 or early PT3 soundtracks (3 voices + percussion).
- 40–60 KB total code + data on 128K hardware.
- Smooth 3D wireframe objects (rotating cubes, pyramids, ships).
- Plasma, raster bars, starfields, zoomers, and rotazers in the same demo.
- Sometimes a first attempt at simple multicolor (8×2 cells) — though the technique was not yet mature.

The late-period peak is also where the **Soviet scene's output began to overtake the West's**. By 1996, Russian and Ukrainian demos were matching or exceeding Western megademos in technical sophistication, and within two years they would dominate. See §5 for the Soviet peak.

### 4.9 What a 1995 Viewer Saw

To convey the state of the art in the Western Golden Age, here is what a typical 1995 Spectrum megademo looked like:

- **Load (1–2 minutes)**: tape or disk load, with a static title screen.
- **Intro (15 seconds)**: animated logo, scroll text, AY music starts.
- **Part 1 — plasma (30 seconds)**: smooth XOR plasma in attribute cells, music continues.
- **Part 2 — 3D wireframe (20 seconds)**: rotating cube or star, hidden-line removal, fades out.
- **Part 3 — raster bars (25 seconds)**: horizontal colour bars in the border, synced to the music beat.
- **Part 4 — starfield (20 seconds)**: 3D starfield with perspective.
- **Part 5 — greet screen (30 seconds)**: scrolling list of 40+ group names, music shifts to a different pattern.
- **Credits (15 seconds)**: names of coder, musician, graphician; demo halts.

Total: ~3 minutes, ~50 KB on 128K hardware. By 1995 standards, this was state of the art; by 1998, the Soviet scene's multicolor-rich demos would make it look dated.

---

## 5. The Soviet Peak (1996–2005)

Between 1996 and 2005, the centre of gravity of the Spectrum demoscene shifted decisively to the **post-Soviet space** (Russia, Ukraine, Belarus, Kazakhstan, the Baltic states). The Soviet scene had been active since 1993, but from 1996 onward it produced the bulk of the platform's landmark demos and effectively defined the form for the next decade. This section is the demos-and-groups view of the era; the cultural, hardware, and music-industry aspects are covered in [soviet_demo_scene.md](soviet_demo_scene.md).

### 5.1 Why the Soviet Scene Took Over

Three factors converged in 1995–1997 to make the post-Soviet scene dominant:

1. **The Pentagon clone** became widely available in the former USSR from ~1993 onward. By 1996, it was effectively the standard Spectrum-compatible machine in the region. Its timing determinism made 8×1 multicolor practical, which was impossible on the original Sinclair hardware. See [multicolor_techniques.md](multicolor_techniques.md) §6 for per-model differences.
2. **PT3** (Sergey Bulba, 1996) made sophisticated AY music universally portable across Soviet demos. One editor and one player binary ran everywhere; musicians could publish music that any demo could use.
3. **FidoNet** gave the geographically dispersed scene a distribution network. Demos, music, and disk magazines moved between Russian, Ukrainian, and Baltic BBSes within days of release. See [soviet_demo_scene.md](soviet_demo_scene.md) §7.

By contrast, the Western scene was fragmenting: many Western sceners had moved on to the PC, Amiga, or PlayStation by 1996, leaving the Spectrum to a smaller group of hobbyists. The Soviet scene had no comparable "next platform" to migrate to in the same period.

### 5.2 The Pentagon Hardware Baseline

The standard Soviet-era production target was the **Pentagon 128K**, often expanded to Pentagon 256K or 512K with a TR-DOS disk interface and a CRT monitor. Key specifications relevant to demo-making:

- **Z80A at 3.5 MHz** — slightly faster than the original Spectrum's 3.546 MHz, with deterministic timing.
- **128K RAM** banked in 16K pages at #C000–#FFFF; the screen was in bank 7 by default but could be swapped out.
- **AY-3-8912** at a known clock, with the player code counting cycles rather than relying on a separate interrupt.
- **TR-DOS disk** (720 KB 5.25" or 3.5") for loading data on demand — this is what enabled the multi-megabyte demos that defined the era.
- **Deterministic ULA timing** — every scanline, every contention cycle was identical from machine to machine. This is what made 8×1 multicolor reliable.

See [soviet_demo_scene.md](soviet_demo_scene.md) §2 for the full Pentagon hardware deep-dive.

### 5.3 The 8×1 Multicolor Revolution

The defining technical first of the Soviet peak was **8×1 multicolor** — also called "true multicolor" — which overrode the Spectrum's 8×8 attribute grid with a new attribute every 8 pixels (every 4 T-states during paper scan). The result: up to 32 colours per scanline, or 6,144 attribute cells per frame instead of 768.

The technique was known in theory in the early 1990s, but it was perfected on the Pentagon between 1997 and 1999. The breakthrough was realising that:

- The ULA reads the attribute byte at a **fixed, predictable cycle** in each character row.
- The CPU can change the attribute byte at `#5800 + row*32 + col` **just before** the ULA reads it, then change it again immediately afterwards.
- The result is that each 8-pixel-wide cell can have its own INK and PAPER, eliminating colour clash for any effect that respects the 8-pixel column boundary.

The cost was enormous: ~150,000 T-states per frame for a full 8×1 multicolor picture, leaving only ~34,000 T-states for everything else (music, effect, framework). Full details are in [multicolor_techniques.md](multicolor_techniques.md) §4.

The 8×1 multicolor revolution made possible:

- **Photorealistic images** in Spectrum "screens" — converted from JPEG with 32 colours per line.
- **Smooth colour gradients** that the original hardware could not produce.
- **Multicolor animations** — 50 Hz motion pictures with per-line colour.

It became the visual signature of the Soviet peak: a 2003 Pentagon demo that did *not* use 8×1 multicolor was considered retrograde.

### 5.4 The PT3 Ecosystem

**Pro Tracker 3** (PT3, Sergey Bulba, 1996) became the standard AY music format for the entire Soviet scene. By 2000, virtually every Soviet demo's soundtrack was a PT3 file. The format is documented in [soviet_demo_scene.md](soviet_demo_scene.md) §6.

PT3's importance to landmark demos was structural: because every musician used the same editor and every coder used the same player binary, music became **interchangeable**. A musician could compose a track, release it on a disk magazine, and have it appear in three different demos by three different groups within a year. This created a shared musical vocabulary that tied the whole scene together.

Notable PT3 musicians whose work appears in many landmark demos include **Sergey Bulba** (Co-Founder of Eternity, composer of the editor's bundled tracks), **Andy Man**, **TBC** (Roman Shiryaev), **Freez**, **Keygee**, and many others. Their tracks were often as recognisable as the demos they appeared in.

### 5.5 The Event-List Framework Standard

By 1998–1999, the Soviet scene had converged on a **standard demo framework pattern**: the event-list driven framework. This is documented in [demo_frameworks.md](demo_frameworks.md) §3 and §8. The pattern:

1. A timeline table lists the parts: `start_frame, init_routine, frame_routine, exit_routine, end_frame`.
2. The framework's ISR reads the current music position counter (a 16-bit value in the PT3 player) on every frame.
3. The current position counter is matched against the table; when it crosses a `start_frame`, the framework calls `init_routine`; while it is in the part's range, it calls `frame_routine` every frame.
4. Transitions between parts are hardcoded as fade routines.

This pattern was small (~1.5–2 KB), reusable across demos, and tight enough to leave room for the 8×1 multicolor engine and the effect code. It was the framework pattern that the entire Soviet scene used for the next decade, with minor per-group variations.

### 5.6 TS-Config and Disk Streaming

Around 2000–2001, the Soviet scene developed **TS-Config** (and the related Beta Disk / TR-DOS streaming pattern) to load data from floppy disk during the demo. This broke the "everything must fit in RAM" constraint and enabled multi-megabyte productions.

The technique worked by:

1. **Banking out** the screen and low memory during disk reads, so the visible screen remained stable while data loaded into a high bank.
2. **Pre-loading** the next part's data into a hidden bank while the current part was still playing.
3. **Swapping banks** at the transition, so the new part's data was visible instantly.

Combined with 8×1 multicolor, this enabled the so-called **"video demos"** — productions that streamed a sequence of pre-rendered multicolor frames from disk, producing what looked like a 50 Hz full-motion video. These were technically extraordinary and unique to the Soviet scene.

The TS-Config concept is covered in [demo_frameworks.md](demo_frameworks.md) §5 (Pentagon memory layout) and [soviet_demo_scene.md](soviet_demo_scene.md) §5.

### 5.7 Notable Soviet Groups

The Soviet peak produced dozens of significant groups. Some of the best-documented include:

- **Eternity** (Sergey Bulba's group) — pioneered the PT3 + 8×1 multicolor combination.
- **X-Trade Syndicate** (Polish, but with strong ties to the Soviet scene) — produced ambitious megademos that competed directly with the Soviet output.
- **Brutal** — known for visual polish and multicolor work.
- **Wecrew**, **Proxima**, **Phantasy**, **Sinclair Club**, **Mindflow**, **Sage**, **Antares**, **Digital Reality**, **Infinite** — all active in the late 1990s / early 2000s peak.
- **SkrewJack**, **Eremine**, **C-jump** — individual sceners whose work appeared across multiple group productions.

Specific demo titles from this era are harder to verify from Western archives; ZXArt.ee and Pouet.net catalogue several hundred Soviet-era productions, but attributions and release years are sometimes uncertain. The safest reference for any specific title is the disk-magazine archive at [zxpress.ru](https://zxpress.ru) (§7).

### 5.8 The 2003 Peak

The Soviet peak's technical high point is usually dated to **2002–2004**. By 2003, the standard "best-in-class" Pentagon demo included:

- A PT3 soundtrack by a known composer.
- Multiple 8×1 multicolor parts — often 4–6 distinct scenes.
- Disk-streamed transitions between parts (no perceptible load delay).
- At least one "video" part — a sequence of multicolor frames playing at 25 or 50 Hz.
- A 3D part (wireframe or filled) demonstrating the platform's mathematical capability.
- Greets, credits, and a final logo screen.
- Total runtime: 5–8 minutes.
- Total size on disk: 200 KB – 1 MB.

The peak did not last long. By 2004–2005, many Soviet sceners had moved to the PC demoscene (which had matured by that point) or had stopped producing demos entirely. The late Soviet-era demos (2004–2005) are often a recapitulation of techniques already perfected rather than a step forward.

### 5.9 What a 2003 Viewer Saw

To convey the state of the art at the Soviet peak, here is what a typical 2003 Pentagon demo looked like:

- **Load (10–30 seconds)**: TR-DOS disk load, with a static title screen showing the group logo.
- **Intro (20 seconds)**: animated logo, PT3 music starts, fade-in.
- **Part 1 — multicolor image (30 seconds)**: a photograph or painted image, rendered in 8×1 multicolor with 32 colours per line.
- **Part 2 — multicolor video (30 seconds)**: a short clip of pre-rendered animation (a face, a landscape, an abstract shape), streamed from disk at 25 Hz.
- **Part 3 — 3D object (20 seconds)**: a rotating filled-polygon object (cube, ship, or abstract shape) with hidden-surface removal.
- **Part 4 — plasma or twister (25 seconds)**: a classic demoscene effect, but in 8×1 multicolor (smooth gradients).
- **Part 5 — greets (40 seconds)**: scrolling list of 50+ group names, with each name in a different multicolor font.
- **Credits (15 seconds)**: names of coder, musician, graphician; PT3 music reaches final pattern; demo halts.

Total: ~5 minutes, ~500 KB on disk. By 2003 Pentagon standards, this was state of the art; no comparable production was being made on the original Sinclair hardware anywhere in the world.

---

## 6. The Modern Revival (2010–present)

From roughly 2010 onward, the Spectrum demoscene has experienced a sustained **revival**. The revival is smaller in volume than the Soviet peak — far fewer demos per year, smaller parties, fewer active groups — but it is technically healthy and has produced its own landmark works. The defining features of the modern era are: **open-source development** (frameworks and demos hosted on Github), **cross-platform toolchains** (z88dk, sjasmplus, modern emulators), and the **ZX Spectrum Next** as a new target hardware. The era is covered in cultural and historical detail in [demoscene_history.md](demoscene_history.md) §8.

### 6.1 The Starting Point

The modern revival is generally dated to **2009–2011**, when several things happened in quick succession:

1. **Modern emulators matured**. Spectaculator, Fuse, and (later) ZEsarUX became accurate enough that a demo developed and tested in an emulator would run on real hardware. This removed the "you must own a real Spectrum" barrier that had limited the Western scene's growth.
2. **The Russian scene restructured**. The post-Soviet scene had largely moved to the PC by 2008, but a small group of dedicated sceners continued to produce Pentagon demos for Forever and DiHalt. They were joined by a new generation of sceners who had grown up with emulation.
3. **Github and modern version control** became normal for hobbyist code. Spectrum demos started appearing on Github with full source, build scripts, and licenses, where the Soviet-era demos had been distributed only as binaries through FidoNet and disk magazines.
4. **The Forever party** in Slovakia (continuously held since 1996) became the spiritual home of the revival. Forever consistently attracts 30–50 new Spectrum demos per year and is where most landmark works of the modern era have premiered.

### 6.2 Open-Source Frameworks and Tools

The single most important technical change of the revival is **open-source frameworks**. Where Soviet-era frameworks were private to each group, modern frameworks are shared, forked, and improved collectively. Notable examples:

- **sjasmplus** (open Z80 assembler) — the de facto modern assembler for Spectrum development. Actively maintained, supports all modern Spectrum hardware variants, and is the assembler most often used in Github-hosted demos.
- **z88dk** (small C compiler targeting Z80) — used for parts of demos that don't need cycle-counted assembly, and for entire demos by sceners more comfortable in C. The compiler's output is good enough for many purposes, though tight loops still require hand-written assembly.
- **ZX0 / ZX1 / ZX2** (Einar Saukas, 2017–2018) — the modern standard for Spectrum-side data compression. See [compression_packing.md](compression_packing.md) §4 for full details.
- **Multipattern / modern PT3 players** — cleaned-up versions of the original Soviet player with per-platform variants (48K, 128K, Pentagon, Next).
- **z88dk/zxnext** — a Next-specific toolkit for Layer 2, tilemap, sprites, and copper.

Open-source frameworks mean that a modern scener can start from a working skeleton (assembler + player + framework + makefile) rather than building one from scratch. This has significantly lowered the entry barrier and is one reason the revival has produced more new sceners than the late Soviet era.

### 6.3 Cross-Platform Development

The modern era is also the **cross-platform** era. A typical modern demo is:

- **Developed on Linux, macOS, or Windows** in a text editor or VS Code.
- **Assembled with sjasmplus** (or z88dk for C-heavy demos).
- **Tested in an emulator** (Fuse, Spectaculator, ZEsarUX) — usually several, to catch emulator-specific quirks.
- **Optionally tested on real hardware** by sending the binary to a fellow scener who owns a Spectrum, Pentagon, or Next.
- **Distributed as a .tap, .sna, .szx, or .trd file** via Pouet.net, ZXArt.ee, the Forever party archive, and (often) Github.

This is in stark contrast to the Soviet era, where a demo was developed on a single Pentagon, tested only on that Pentagon, and distributed only through FidoNet. Cross-platform development has made the modern scene more accessible but has also introduced emulator-vs-hardware bugs: occasionally a demo that works perfectly in Fuse will fail on a real Pentagon because of timing edge cases.

### 6.4 The ZX Spectrum Next

The most important hardware development of the modern era is the **ZX Spectrum Next** (Kickstarter 2017, shipped 2017–2020). The Next is a modern FPGA-based Spectrum-compatible machine with substantial extensions:

- **Layer 2**: a 256-colour framebuffer at 320×256, in addition to the classic Spectrum display.
- **Tilemap**: a hardware tilemap engine, like the C64's character mode but with 256-colour tiles.
- **Hardware sprites**: up to 64 independent sprites per frame, with 256-colour palettes.
- **Copper unit**: a programmable display-list processor similar to the Amiga's copper.
- **28 MHz Z80** (in turbo mode), in addition to the original 3.5 MHz.
- **2 MB RAM**, expanded via the esxDOS interface.
- **Two AY chips** (six voices), in addition to the original beeper.
- **PCM playback** through the DMA engine.

The Next is described in detail in [demo_frameworks.md](demo_frameworks.md) §9. From a landmark-demos perspective, the Next matters because it allowed Spectrum sceners to write demos in a new register: 256-colour visuals, hardware-accelerated sprites, and Amiga-level sound. The Next-targeted demos are the only modern demos that compete on equal terms with the C64 and Atari ST demoscenes for visual richness on stock "8-bit-class" hardware.

Notable Next-targeted demos have premiered at the Next-directed parties and at Forever; the Next-specific party circuit is still forming as of 2024.

### 6.5 The Modern Party Circuit

The revival-era party circuit includes:

- **Forever** (Slovakia, since 1996, annual) — the spiritual home. Spectrum-only competition categories, with separate compos for stock 48K, stock 128K, Pentagon, and Next demos.
- **DiHalt** (Russia, since 1997, annual) — Russian-language party, continues the Soviet-era tradition.
- **Outline** (Netherlands, since 2003) — multi-platform, has a small but consistent Spectrum competition.
- **Nova** (UK, occasional) — smaller party, but has been important for UK scene revival.
- **ZX / MSX devcon** (occasional) — combined Spectrum-MSX developer conference, celebrating the AY/YM bridge (see [demoscene_platforms.md](demoscene_platforms.md) §9).
- **MSXdev** and similar parties occasionally accept Spectrum-targeted entries when the format permits.

Forever remains the most important; a Spectrum demo that wins at Forever has achieved the modern scene's highest recognition.

### 6.6 Notable Modern Groups and Demos

Modern-era landmark demos are easier to verify than Soviet-era ones because they are documented on Github, Pouet.net, and the Forever party archive. Some well-known groups of the era include:

- **Booze Design** — active in the modern era, known for visual polish.
- **Oxygen** — Next-focused group, contributed to the Next-targeted library of demos.
- **Einar Saukas** — individual scener best known for ZX0 and for size-coding landmark 1K and 256B intros.
- **Critical Impact**, **Mindflow** (continuing from the Soviet peak), **Spice Connection**, **X-Trade** (continuing from the Polish scene) — groups that bridge the Soviet and modern eras.
- **Vision / Vision-Club** — modern Russian-language scene with Pentagon-targeted work.

Specific landmark titles of the modern era include: notable Forever-winning demos (the safest citation is the [Forever party archive](https://forever.zeroteam.sk)), notable 1K and 256B intros (see [size_coding.md](size_coding.md) §9 for the size-coding canon), and notable Next-targeted premiers. Specific titles are deliberately not listed here because the modern scene is still active and the canon is still forming; readers should consult the archives in §7.

### 6.7 What a 2023 Viewer Saw

To convey the modern era's state of the art, here is what a typical 2023 Next-targeted demo looked like:

- **Load (instant)**: the demo loads from SD card via esxDOS, no perceptible delay.
- **Intro (15 seconds)**: animated logo on Layer 2, PCM soundtrack starts, copper bars in the border.
- **Part 1 — Layer 2 video (30 seconds)**: full 256-colour animation, equivalent to an Amiga AGA demo.
- **Part 2 — hardware sprites (25 seconds)**: dozens of moving sprites with rotation and scaling.
- **Part 3 — tilemap (20 seconds)**: a scrolling level reminiscent of a Nintendo game, but rendered as a demo effect.
- **Part 4 — classic 8×1 multicolor (30 seconds)**: a callback to the Soviet peak, rendered on the legacy ULA layer.
- **Part 5 — 3D raycasting (30 seconds)**: a Wolfenstein-style first-person view at 25–50 Hz.
- **Greets + credits (20 seconds)**: scrolling list, two-AY-chip music, demo halts.

Total: ~3 minutes, ~2 MB on SD card. By modern Next standards, this is state of the art; by the standards of the original 1982 hardware, it would have been inconceivable.

For comparison, a 2023 stock-Pentagon demo at Forever would be visually similar to the 2003 peak described in §5.9, with perhaps one or two new techniques (a more efficient multicolor engine, a new raycasting variant). The Pentagon-targeted modern scene is conservative — it values continuity with the Soviet peak over novelty for its own sake.

---

## 7. Source Releases, Archives, and Study Material

This section lists the **publicly accessible archives** where landmark demos can be found, the source releases that are most useful for study, and a recommended path for new sceners who want to learn from landmark works.

### 7.1 Primary Archives

The four most important archives for Spectrum demoscene research are:

- **[Pouet.net](https://www.pouet.net)** — the multi-platform demoscene archive. Searchable by platform (ZX Spectrum), group, year, and party. Includes screenshots, votes, and comment threads. ~5,000 Spectrum entries.
- **[ZXArt.ee](https://zxart.ee)** — the most comprehensive Spectrum-specific archive. Includes demos, music (PT3), graphics, and text files. Stronger coverage of the Soviet-era output than Pouet. ~5,000 Spectrum demo entries plus extensive music and graphics collections.
- **[Forever party archive](https://forever.zeroteam.sk)** — the official archive of the Forever party, with downloadable entries for every year since 1996. The most authoritative source for modern-era Spectrum demos.
- **[zxpress.ru](http://zxpress.ru)** — the Russian-language disk-magazine archive. Contains scanned/extracted text from dozens of Soviet-era disk magazines (Body, Futuris, Echo, Sinclair Classic, and many others). The primary source for Soviet-era group history and demo attribution.

A fifth important source is **[Speccy.Live](https://speccy.live)** and similar streaming archives, which record live demo runs on real hardware. These are essential for understanding the timing-dependent effects (especially 8×1 multicolor) that emulators sometimes misrender.

### 7.2 Github-Hosted Source Releases

Modern Spectrum demos are increasingly released with full source on Github. Notable categories of source-available material include:

- **Modern Forever entries** — many of the 2015-onward Forever winners are released with source. Search Github for "zx spectrum demo" or "Forever" plus the year.
- **Size-coded intros** — the size-coding canon (1K, 256B) is heavily source-released, because the whole point is for other sceners to learn the tricks. See [size_coding.md](size_coding.md) §9.
- **Tooling source** — `sjasmplus`, `z88dk`, `ZX0`/`ZX1`/`ZX2`, modern PT3 players, and the ZX Spectrum Next SDK are all open-source.
- **Tutorial code** — a small but growing body of Github repos provides working skeletons for newcomers: "first effect on the Spectrum", "first multicolor demo", "first ISR-driven framework".

Source releases for Soviet-era demos are rare, because the original source code was typically lost or kept private by the groups. Some source has been recovered via [reverse engineering](../08_reverse_engineering/README.md) of binary demos; the reversing section's README lists the relevant techniques and tools.

### 7.3 The Disk Magazine Archive

A distinctive resource for the Spectrum scene is the **disk magazine archive**. Disk magazines ("diskmags") were FidoNet-distributed Spectrum programs containing news, interviews, demo reviews, music, and sometimes bundled demos. The peak era of diskmags was 1995–2005 (the Soviet peak); they declined with the rise of the World Wide Web.

Important diskmags included:

- **Body** (Russia) — one of the longest-running and most influential.
- **Futuris** (Russia) — known for high-quality writing and demo reviews.
- **Echo** (Russia) — important early diskmag.
- **Sinclair Classic**, **Subzero**, **Visual Spectrum**, **Kanydel** — others of note.
- **Newsflash** (Western) — bridged Western and Eastern readers.

The full text of most diskmags is available at [zxpress.ru](http://zxpress.ru). They are essential primary sources for understanding how the Soviet scene saw itself.

### 7.4 Recommended Study Order

For a new scener who wants to study landmark demos in a structured way, the recommended path is:

1. **Start with the size-coding canon** ([size_coding.md](size_coding.md) §9) — these are small, well-documented, and source-available. They teach the basic building blocks.
2. **Watch modern Forever winners** — the [Forever party archive](https://forever.zeroteam.sk) has 25+ years of entries, and the modern ones are accessible to contemporary viewers.
3. **Read the relevant technique articles** — for each effect you see, look up the implementation in [effects_catalog.md](effects_catalog.md), [multicolor_techniques.md](multicolor_techniques.md), or [precalc_trigonometry.md](precalc_trigonometry.md).
4. **Read the framework article** — [demo_frameworks.md](demo_frameworks.md) explains how effects are sequenced into a multi-part production.
5. **Watch the Soviet peak demos** — once you understand the techniques, the 2003-era Pentagon demos become legible. Browse ZXArt.ee for "Eternity", "Brutal", or specific years.
6. **Read the diskmags** — for cultural context and group history, the zxpress.ru archive is unmatched.

### 7.5 Caveats on Attribution

Specific demo titles, group names, release years, and authorship attributions in this article are drawn from publicly accessible archives as of 2024. Attribution disputes are common in the demoscene, especially for the Soviet era:

- A demo released under one group's name may have had contributions from members of other groups.
- "Stolen" demos (re-released without permission) exist in the archive.
- Some demos were released without any group attribution at all.
- Release years are sometimes the year of party premiere, sometimes the year of public release, and sometimes the year the demo was finished — these can differ.

Where this article is uncertain, it says so explicitly. For definitive attribution, consult the disk-magazine primary sources at zxpress.ru and the comments on ZXArt.ee and Pouet.net.

---

## 8. Cross-References

### 8.1 Within the Demoscene Section

- [README.md](README.md) — section overview.
- [demoscene_history.md](demoscene_history.md) — the full cultural and historical narrative. §§3–6 of this article correspond to §§3–8 of the history article.
- [soviet_demo_scene.md](soviet_demo_scene.md) — the dedicated article on the post-Soviet scene. §5 of this article depends heavily on §§2–6 of that article.
- [demoscene_platforms.md](demoscene_platforms.md) — the Spectrum vs C64/Amiga/Atari ST/MSX comparison that contextualises "what made the Spectrum demos unique".
- [effects_catalog.md](effects_catalog.md) — the techniques themselves. Every demo discussed in §§3–6 is built from effects catalogued there.
- [multicolor_techniques.md](multicolor_techniques.md) — the 8×1 multicolor technique that defines the Soviet peak (§5.3 of this article).
- [precalc_trigonometry.md](precalc_trigonometry.md) — the precomputed-table foundation underlying most 3D and plasma effects.
- [compression_packing.md](compression_packing.md) — the depackers and compressors that make size-coding possible.
- [size_coding.md](size_coding.md) — the 256-byte and 1K intro tradition. §6 of this article references §9 of size_coding.md for the size-coding canon.
- [demo_frameworks.md](demo_frameworks.md) — the runtime architecture. §§4–6 of this article reference §§2, 3, 5, 7, 8, 9 of demo_frameworks.md.

### 8.2 Outside the Demoscene Section

- [../08_reverse_engineering/README.md](../08_reverse_engineering/README.md) — the reversing section. Reverse engineering is the standard tool for recovering source from Soviet-era demos that were released only as binaries (§7.2 above).
- [../05_development/02_assembly/README.md](../05_development/02_assembly/README.md) — the assembler / toolchain entry point, including sjasmplus and z88dk that made the modern revival possible (§6.2).
- [../01_cpu/README.md](../01_cpu/README.md) — the Z80 CPU section, essential background for understanding every technique cited in this article.
- [../02_hardware/clones/README.md](../02_hardware/clones/README.md) — the hardware clones entry point (Pentagon and others), the machine that defined the Soviet peak (§5.2). The ZX Spectrum Next is covered separately under [../02_hardware/newgen/README.md](../02_hardware/newgen/README.md) (§6.4).
- [../04_operating_systems/README.md](../04_operating_systems/README.md) — for TR-DOS and esxDOS, which underlie the disk-streaming (§5.6) and Next's instant-load (§6.7) respectively.

### 8.3 External References

- **[Pouet.net](https://www.pouet.net)** — multi-platform demoscene archive.
- **[ZXArt.ee](https://zxart.ee)** — Spectrum-specific archive.
- **[Forever party archive](https://forever.zeroteam.sk)** — annual party archive.
- **[zxpress.ru](http://zxpress.ru)** — Russian-language disk magazine archive.
- **[Speccy.Live](https://speccy.live)** — live hardware demo recordings.
- **[Demoscene.info](https://demoscene.info)** — UNESCO 2021 demoscene research portal.

---

## License

This article is released under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share and adapt the material for any purpose, provided you attribute the source and license derivative works under the same terms. The full license text is at [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/).

Specific demo titles, group names, and other identifying details are drawn from publicly accessible archives (Pouet.net, ZXArt.ee, zxpress.ru, the Forever party archive) as of 2024. Trademarks, where they apply to specific demos or groups, belong to their respective holders; their use here is for documentary and educational purposes only.
