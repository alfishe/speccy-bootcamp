[← Home](../README.md) · [Demoscene](README.md)

# The Soviet / Russian ZX Spectrum Demoscene

> **Scope**: This article is the deep dive into the Soviet and post-Soviet ZX Spectrum demoscene — the parallel tradition that emerged behind the Iron Curtain, scaled to dominate the platform from the mid-1990s to mid-2000s, and developed distinctive techniques, aesthetics, group culture, and infrastructure. It complements [demoscene_history.md](demoscene_history.md) (the cross-platform narrative) and is referenced from [compression_packing.md](compression_packing.md), [multicolor_techniques.md](multicolor_techniques.md), and [notable_demos.md](notable_demos.md).
>
> **Primary source**: Konstantin Elfimov (Elfh/Inward), *Brief History of Russian Speccy Demoscene and the story of Inward* (Mustekala magazine, 2008) — the only first-hand English-language account by a founding member of a major Russian group. Other primary sources are disk magazines (*Body*, *Spectrofon*, *ZX-Format*, *Error*), FidoNet echomail archives, and the Russian-language forum archives at zx-pk.ru and nedoPC.ru.

---

## 1. Why the Soviet Scene Was Different

The Soviet ZX Spectrum demoscene is the only national demoscene tradition that emerged in near-complete isolation from the broader (Western-dominated) demoscene, scaled to a size that dwarfed any Western national scene, and produced a body of work with distinctive aesthetics and techniques that Western sceners discovered, with some surprise, only after 1997. Three structural factors made this possible:

### 1.1 Hardware independence

Soviet Spectrum users did not have original Sinclair hardware. They built their own clones from locally-sourced parts, guided by magazine schematics. The first working Soviet-built Spectrum was assembled in **August 1985 in Lvov, Ukraine** — only months after the Sinclair 128 launched in the UK. Within two years, schematics had spread to every major Soviet city; within five years, over 40 different clone models existed (Dubna, Moscow, Leningrad, Delta, Balansir, Pentagon, Scorpion, Profi, Kay, ATM, and many others).

This independence from original hardware had three consequences:

- **Specs diverged.** Each clone had slightly different memory maps, timing, sound chips, and disk interfaces. Code that worked on one clone often did not work on another.
- **The Pentagon won.** By 1995, the Pentagon 128 (and its successor Pentagon 1024) had captured the majority of the active-demo market. The Pentagon became the *de facto* Soviet standard.
- **Western software was only partially compatible.** Western demos that assumed Sinclair 128 contention timing or Sinclair +3 disk access often failed on Pentagon hardware. The Soviet scene had to write its own software.

### 1.2 Distribution independence

Soviet sceners did not have access to Western distribution channels. They built their own:

- **FidoNet** (from ~1991): Russian-language echomail conferences, most importantly `ZX.SPECTRUM` and the `SUCESSNET` echoes, became the primary real-time communication channel for the Soviet scene.
- **Disk magazines**: standalone programs containing editorial content, scene news, and embedded demos/music. The most important were *Body*, *Spectrofon*, *ZX-Format*, *Error*, and *ZX-Power*. Disk magazines were the Soviet scene's primary publication venue from 1994 to 2003.
- **BBSes**: dial-up bulletin boards in major cities (Moscow, St. Petersburg, Kyiv, Minsk, Ryazan) carried scene files. Throughput was tiny by modern standards but sufficient for a subculture.
- **Magazine distribution via radio**: as late as the early 1990s, software crossed the Iron Curtain via FM radio broadcasts — Polish and Czechoslovak stations would broadcast Spectrum software as audio during off-peak hours, and Soviet listeners would record and load it.

### 1.3 Cultural independence

The Soviet scene's cultural references were Russian-language and Russian-cultural: references to Soviet films, children's literature, science fiction, and current events that would have been opaque to most Western sceners. Music drew on Soviet rock (Kino, Alisa, Nautilus Pompilius, Grazhdanskaya Oborona) and Russian folk traditions as well as Western electronic music.

This cultural distance made Soviet demos instantly recognisable. Even without text translation, a Soviet demo's pacing, visual hierarchy, and music theory clearly differed from contemporary Western work.

### Article Roadmap

- §2 Pentagon hardware deep-dive: what made it different from a Sinclair 128, and why it mattered.
- §3 The early groups (1993–1997): Flash Inc, E-Mage, Extreme, Progress, Skrju, and the first Soviet-specific techniques.
- §4 The peak (1998–2005): CAFe, DiHAlt, CC, ENLiGHT; CyberPunks Unity; Inward; the experimental wing.
- §5 Soviet-specific techniques: gigascreen, multicolor refinement, TS-Config disk caching, the Soviet demo framework.
- §6 The Pro Tracker 3 (PT3) music ecosystem: how a single format unified AY composition across the entire scene.
- §7 Disk magazines and the FidoNet era: Soviet-specific publication and communication infrastructure.
- §8 The post-Soviet transition (2005–2015): emulators, online archives, the language gap with the West.
- §9 The modern Russian scene (2015–present): active groups, current party calendar, technical baseline.
- §10 Cross-references to detailed technique articles.

---
## 2. The Pentagon: Hardware Deep-Dive

The Pentagon 128 (and its successors) is the most important hardware platform in Soviet Spectrum history. Understanding what made it different from a Sinclair 128 is essential for understanding the demos that target it.

### 2.1 Origin and naming

The Pentagon was developed in **Moscow in 1993** by a group of hobbyists (the exact authorship is contested in scene histories, but key contributors include members of the **Nibea** group and the **ATM** firm that later commercialised boards). Its name has no connection to the US military building; it is variously explained as a play on "Penta" (five — for the five main ICs on the original board) or as a reference to the pentagonal PCB layout of some early production runs.

The Pentagon was never commercially manufactured to a consistent standard. Different production runs used different components, slightly different clocks, and sometimes different memory geometries. Each Pentagon was effectively unique; Russian demo coders learned to test on multiple machines.

### 2.2 Key technical differences from Sinclair 128

| Feature | Sinclair 128 / +2 | Pentagon 128 | Implication for demos |
|---|---|---|---|
| **CPU clock** | 3.54690 MHz | 3.5000 MHz (nominal; varied by board) | Pentagon timing assumptions are ~1.3% off from Sinclair. Pentagon demos often misbehave on Sinclair hardware. |
| **Frame rate** | 50.08 Hz (PAL) | 50.0 Hz (nominal) | Pentagon has slightly fewer scanlines per frame; timing-sensitive code (e.g. multicolor) must be re-tuned. |
| **Total scanlines per frame** | 311 (64+192+56, VBLANK split) | 320 (more VBLANK time) | Pentagon gives coders more CPU time per frame than Sinclair — a quiet advantage for cycle-counted effects. |
| **Memory contention** | ULA contends CPU during visible display | No contention | Pentagon code runs at full speed always. ~17% faster effective CPU on average for code in contended banks. |
| **Memory map** | Banks 0–7 at 0xC000–0xFFFF via 0x7FFD | Banks 0–7 at 0xC000–0xFFFF via 0x7FFD (same scheme, different numbering) | Mostly compatible, but some Pentagon demos assume Pentagon-specific banking extensions (e.g. Pentagon 1024's 0x7FFD + 0xeff7 schemes). |
| **Disk interface** | None on Sinclair 128; +3 has +3DOS (3" drive) | Beta Disk Interface (WD1793 controller, 5¼" or 3½" drives), TR-DOS filesystem | All Pentagon disk software uses TR-DOS, which is incompatible with +3DOS. Pentagon software distribution is on TR-DOS `.trd` and `.scl` images. |
| **Sound chip** | AY-3-8912 at 0xFFFD/0xBFFD | AY-3-8912 (later YM2149F) at same ports, plus optional TurboSound (dual AY) and General Sound | Pentagon has the same base AY but most serious Pentagon work assumes TurboSound (six channels) or General Sound (digital audio). |
| **ROM** | Sinclair 128 ROM (3 banks) | Usually a custom ROM with TR-DOS 5.x embedded | Pentagon ROM includes a TR-DOS boot menu; software can call TR-DOS routines directly without loading them. |

### 2.3 The contention difference — and why it mattered

On a Sinclair 128, the CPU is slowed down by ~17% during the visible display because the ULA needs to read character and attribute bytes from RAM at the same time the CPU is fetching instructions. The slowdown (called **contention**) means code in contended RAM (banks 5, 2, 0 in the original 128K layout, i.e. addresses 0x4000–0x7FFF) runs slower than code in uncontended RAM (banks 1, 3, 4, 6, 7, plus the ROM area 0x0000–0x3FFF).

The Pentagon has no contention. Code runs at full speed always. This has two practical effects:

- **Pentagon code is faster on average.** A demo that fits its inner loop in contended RAM gets a ~17% speed boost over the same code on Sinclair.
- **Pentagon timing is uniform.** Code can be cycle-counted without worrying about which scanline the CPU is on. This makes multicolor effects *dramatically* easier to write on Pentagon than on Sinclair.

The contention difference is the single biggest reason Soviet multicolor work surpassed Western multicolor work from ~1995 onwards. Soviet coders were working on hardware that was simply more forgiving.

### 2.4 The Pentagon 1024 and beyond

The original Pentagon 128 had 128 KB of RAM. Later versions expanded this:

- **Pentagon 1024**: 1024 KB (1 MB) via extended banking (additional control registers at 0x7FFD and 0xeff7).
- **ATM Turbo 1/2/3/4**: a Pentagon-compatible with turbo modes (7 MHz and 14 MHz) and CGA-like 640×200 graphics modes.
- **ZX Evolution**: a modern FPGA-based Pentagon-compatible.
- **TS-Config**: a hardware standard for caching multicolor data from disk, enabling full-screen video at 25–50 fps. See §5.4.

These extensions are *not* present on original Sinclair hardware. A modern Russian demo targeting TS-Config or Pentagon 1024 will not run on a Sinclair 128 without adaptation. This is why modern Russian demo work is often encountered first in emulators (Unreal Speccy, ZEsarUX) configured for Pentagon hardware.

### 2.5 Other Soviet clones

The Pentagon dominated from 1995 onwards, but several other clones had significant followings:

- **Scorpion ZS-256 / GMX**: a more conservatively-designed clone with better original-Sinclair compatibility. Popular with hobbyists who wanted to run UK software.
- **Profi 5.03 / 1024**: a high-end clone with extensions including a CP/M mode. Used by some developers but not a major demo platform.
- **Kay 1024**: a Soviet Spectrum with significant architectural differences.
- **Leningrad / Delta / Moscow / Dubna**: earlier DIY clones that had been superseded by the Pentagon by the mid-1990s.

A full clone census is at the [List of ZX Spectrum clones](https://en.wikipedia.org/wiki/List_of_ZX_Spectrum_clones) Wikipedia article. From a demoscene perspective, only the Pentagon matters for the modern era — everything else is historical curiosity.

---

## 3. The Early Soviet Groups (1993–1997)

The Soviet scene's first generation of demoscene groups emerged from the cracking and BBS subcultures around 1993–1994. They were not, by and large, demoscene groups in the Western sense; they were cracking/utility groups that produced demos as a side activity. The transition to "demoscene first, cracker second" happened gradually over 1994–1996.

### 3.1 The pre-scene generation (1990–1993)

Before there were "groups" in the Western sense, there were **Soviet software localisers**: individuals or informal collectives who took Western software (mostly games), translated the on-screen text to Russian, sometimes patched copy-protection, and redistributed the result on tape. Localisation was a Soviet-specific need: Soviet users did not speak English well enough to play untranslated Western games, and there was no commercial market for official translations.

The localisers set several conventions the demoscene inherited:

- **Handle-based identity** (pseudonyms, often English for international prestige).
- **Group names** that sounded international but were usually all-Soviet.
- **Greeting lists** in software releases (the precursors of cracktro greetings).
- **Disk-magazine publication of scene news** (the precursors of *Body* and *Spectrofon*).

### 3.2 Flash Inc (Ukraine, 1993–)

**Flash Inc**, founded in Kyiv by Max Iwamoto, was among the first Soviet groups to achieve Western recognition. Flash Inc's early work was on the cracking/localisation side; by 1995 they were producing original demos. The group is particularly known for:

- **Music disks**: Flash Inc produced some of the early Soviet AY music disks, establishing conventions (multi-track, menu-driven, embedded player) that would become standard.
- **Clean code**: Flash Inc's demos were technically conservative but very polished; they rarely pushed the hardware's limits but always shipped working.
- **Group longevity**: Flash Inc, in various line-ups, has been active for over 30 years.

Flash Inc's relationship to the CAFe demoparty (Kyiv, from 1998) is structural — several Flash Inc members have been CAFe organisers.

### 3.3 E-Mage (Russia)

**E-Mage** was a major Russian group active from ~1994 onwards. They are particularly important for:

- **Disk magazines**: E-Mage published and contributed to several disk magazines.
- **The Soviet demo framework** (see §5.5): the standard skeleton for loading and sequencing parts that emerged around 1999–2000 was codified by E-Mage.
- **Code quality**: E-Mage's demos were among the most technically demanding in the early Soviet scene.

### 3.4 Extreme (Russia)

**Extreme** was a major group active from ~1995, known for both technical and artistic innovation. Their work pushed the boundaries of:

- **Multicolor**: Extreme produced some of the first widely-cited Soviet multicolor demos.
- **3D rendering**: Extreme's software-rendered 3D work was, for a period in the late 1990s, the state of the art on any 8-bit platform.
- **Design coherence**: Extreme's demos had a consistent visual identity that distinguished them from contemporaries.

### 3.5 Progress (Russia) and the Pro Tracker

**Progress** (Saint Petersburg) is the single most influential group in Soviet Spectrum history, not for their demos (though those were significant) but for **Pro Tracker**. Progress developed:

- **Pro Tracker 1** (1993–1994): an early AY tracker.
- **Pro Tracker 2 (PT2)** (~1995): the format that would standardize AY composition.
- **Pro Tracker 3 (PT3)** (~1997): the refined format that became the *de facto* global AY standard for the next two decades.

PT3 is so important that §6 is dedicated to it. Without PT3, the Soviet scene would not have achieved its cultural reach.

### 3.6 Skrju (Belarus)

**Skrju**, founded in Minsk, became one of the most respected Soviet groups. Their work is characterized by:

- **Highly polished demos** with consistent design language.
- **Long-running activity**: Skrju has been active from the late 1990s through the present.
- **Strong opinions**: Skrju demos often expressed the group's views on the scene itself — most famously *Fuck You Scene* (released at an early CAFe or DiHAlt, dates vary in scene memory), a polemical demo about scene stagnation.

Skrju's members have been involved in mentoring younger Belarusian sceners; their influence extends beyond their own releases.

### 3.7 The scene at 1997

By 1997 the Soviet scene had all the infrastructure of a mature demoscene:

- Multiple active groups with distinctive identities.
- Disk magazines carrying scene news and reviews.
- A dominant music format (PT3) and a dominant hardware platform (Pentagon).
- FidoNet echomail for real-time communication.
- The first dedicated demoparties (ENLiGHT in St. Petersburg, organized by Random and others).

What it lacked was contact with the West. That would change in 1997–1999, and the resulting cross-pollination would push both scenes forward dramatically. See [demoscene_history.md](demoscene_history.md) §5–§6 for the cross-border narrative.

---

## 4. The Peak (1998–2005)

Between 1998 and 2005 the Soviet scene reached its maximum output volume, technical sophistication, and cultural self-confidence. Several converging factors drove this:

- **Demo parties regularised**: CAFe (Kyiv, 1998–), DiHAlt (Ryazan, 1998–), and CC (St. Petersburg, 1999–, descended from ENLiGHT) gave the scene annual deadlines and venues. Parties were major social events; attending CC was, for many sceners, more important than any individual demo release.
- **PT3 became standard**: by 1999 every composer was writing PT3 modules; every demo used a PT3 player. This eliminated the per-demo-player-code overhead that had fragmented the early Soviet scene.
- **FidoNet and early Internet access** became widespread, accelerating communication.
- **The Russian economy stabilised** after the 1998 collapse, giving hobbyists enough disposable income to maintain Pentagon hardware, buy blank diskettes, and attend parties.

### 4.1 The party circuit

The Soviet scene's party circuit was its primary social infrastructure. Each party had its own character:

- **CAFe (Computer Art Festival)**, Kyiv: the most internationally-oriented. CAFe accepted Western entries from early on and published bilingual results. CAFe was the venue where many first East–West contacts happened.
- **DiHAlt**, Ryazan: technically-focused, with strong compos in intro categories. Smaller attendance than CC but high-quality entries.
- **Chaos Constructions (CC)**, St. Petersburg: the largest Russian party, multi-platform. CC's ZX Spectrum compos were, at peak, the largest in the world.
- **ENLiGHT**, St. Petersburg (1997–1999): the precursor to CC. ENLiGHT was where the modern Russian party format was established.
- **Adventure**, later years: a smaller event, sometimes held jointly with other parties.

Parties served three functions:

1. **Competition**: the social pressure of being judged by peers produced quality.
2. **Physical meeting**: FidoNet friends met face-to-face for the first time. Lifelong friendships were formed.
3. **Group formation and dissolution**: parties were where new groups announced themselves, and where old groups sometimes announced their dissolution.

### 4.2 CyberPunks Unity (CPU)

**CyberPunks Unity (CPU)**, based in Rybinsk (a small Russian city), is one of the longest-running Soviet/Russian groups. CPU is known for:

- **High-quality technical work** across multiple categories (demos, intros, music disks).
- **Mentoring**: CPU has been a training ground for several generations of Russian sceners.
- **The Inward spin-off**: CPU members Elfh (Konstantin Elfimov) and Moran (Roman Skvortsov) founded Inward in 2003 as an experimental side project (see §4.4).

### 4.3 The experimental wing — Inward, Skrju, others

A distinctive feature of the Soviet scene's peak is the emergence of an **experimental/avant-garde wing**. Most demoscene work is fundamentally demonstration-of-technique; experimental work prioritises atmosphere, abstraction, and emotional effect over technical showcase.

The most influential experimental group is **Inward** (Rybinsk, founded 2003 by Elfh and Moran). Inward's work, documented by Elfh in his 2008 *Mustekala* article, includes:

- **Microcosm** (2003): a 40-minute drone piece consisting of two repeating visual patterns with randomisation, a hypnosis-inducing soundtrack, and a text describing consciousness. The work was released out-of-compo because no party would accept it; the Nomad festival (Serbia) eventually showed it in full.
- **Evenless** (2004): turned off mid-presentation at a CAFe because organisers deemed it "too minimal". The incident became legendary.
- **The Source / Inmost Sun** (2004): short experimental pieces using algorithms that displayed only part of the image per frame, producing a surreal cumulative effect.
- **Global Sensorica** (2004): a music-disk-style release with elaborate layout.
- **I am the seed** (2005): nominated for a Scene.org Award. Used noise on landscape imagery to reflect uncertainty about past and future.
- **Your song is quiet** (2007): a memorial work after multiple scene members died in 2006–2007. Premiered at Breakpoint (Germany) — Elfh's first Western party attendance, made possible by turning 28 and being released from Russian military service.
- **Give me future or give me death** (2008): a still-frame animation shot on a budget of "close to 2 euros" using found objects.

Inward's work demonstrates the breadth the Soviet scene achieved at its peak: not just technical showcase but serious artistic expression.

### 4.4 Other groups of the peak period

- **Triebkraft + 4th Dimension**: known for experimental work, often dark and atmospheric.
- **Simbols**: long-running group with consistently strong releases.
- **Milytia**: active in the late peak period.
- **BraveStorm**: known for high-quality intros.

### 4.5 Why the peak ended

By 2005 the Soviet scene was visibly contracting. Several factors:

- **Aging membership**: the core generation of 1993–1997 sceners were now in their late 20s and 30s, with careers and families. Time for the hobby decreased.
- **Hardware obsolescence**: real Pentagon hardware was aging. Replacement parts (KR580VM80A CPUs, KR580VV55 PIOs, original AY chips) were becoming scarce.
- **The PC demoscene was ascendant**: many Soviet sceners moved to PC demos, where they could reach larger audiences.
- **The Western scene contracted first**, reducing cross-border energy.

The scene did not die — it contracted and refocused. The next decade would see a transition to emulators, online archives, and a smaller but more dedicated core.

---

## 5. Soviet-Specific Techniques

The Soviet scene originated or refined to world-class levels several techniques that have no parallel in the Western Spectrum scene. These are covered in detail in the technique articles; this section explains why Soviet work in each area was distinctive.

### 5.1 Multicolor refinement

Multicolor — the technique of changing the attribute bytes synchronously with the CRT beam, achieving 8×1 or 8×2 attribute resolution instead of the hardware's 8×8 — was discovered independently in the West and the Soviet scene. What the Soviet scene did that the West did not was *scale* it: full-screen multicolor effects, persistent across frames, with timing discipline that became legendary.

The Pentagon's lack of memory contention was the enabling factor (see §2.3). Without contention, cycle-counting the timing of attribute writes is dramatically easier. Soviet coders exploited this to produce effects (full-screen multicolor plasma, multicolor texture-mapped 3D, multicolor "video" sequences) that were impossible on original Sinclair hardware without extreme effort.

A full technical treatment is in [multicolor_techniques.md](multicolor_techniques.md).

### 5.2 Gigascreen

Gigascreen (also known as **interlace** or **attr-attr**) is a flicker-based color-mixing technique: alternate two different attributes on successive frames (or successive scanlines), and the eye averages them to a perceived intermediate color. With careful pairing, gigascreen can produce 15 or more perceived colors from the Spectrum's 8-attribute palette.

Gigascreen was pioneered in the Soviet scene and reached high sophistication there. Modern emulators render gigascreen correctly (mixing the two source frames), but on real CRT hardware the effect depended heavily on phosphor persistence and could look different from monitor to monitor.

See [multicolor_techniques.md](multicolor_techniques.md) §3 (interlace/gigascreen section) for technical detail.

### 5.3 TS-Config and disk-streamed multicolor

For high-end Pentagon work, **TS-Config** is the enabling technology. The idea:

- A multicolor effect requires ~6144 bytes of attribute data per frame (64×24 cells × 4 bytes per cell with metadata).
- At 50 Hz, that is ~300 KB per second — far more than fits in 128 KB of RAM.
- TS-Config defines a hardware/software standard for caching this data on disk and streaming it into RAM in real time via the Beta Disk interface.
- The result is full-screen 15-color video at 25 fps (50 Hz fields alternating, with gigascreen mixing).

TS-Config was originally a hardware extension (a custom disk-cache card for the Pentagon); modern implementations run on FPGA clones (ZX Evolution, ATM Turbo, ZX Uno, MiSTer's Pentagon core) without requiring the original hardware. TS-Config demos are common in modern Russian party releases.

### 5.4 Software 3D and polygon rendering

The Soviet scene produced what were, for a period in the late 1990s, the most advanced real-time 3D rendering on any 8-bit platform. Achievements include:

- **Real-time filled-polygon rendering** at usable frame rates.
- **Texture-mapped surfaces** (using attribute-cell texturing).
- **Gouraud shading** approximation via attribute interpolation.
- **3D objects with thousands of vertices** at single-digit frame rates.

These achievements relied on the Pentagon's lack of contention, careful use of precomputed tables (see [precalc_trigonometry.md](precalc_trigonometry.md)), and the Soviet demo framework's discipline of part sequencing.

### 5.5 The Soviet demo framework

By 1999–2000 the Soviet scene had converged on a standard skeleton for managing a multi-part demo:

```z80
; Soviet demo framework — typical structure
        ORG     0x8000          ; standard load address on Pentagon

start:  DI                      ; interrupts off for cycle-exact code
        LD      SP, 0xC000      ; stack at top of uncontended RAM
        CALL    init_music      ; set up PT3 player
        CALL    load_part_1     ; load part 1 from disk
        CALL    run_part_1
        CALL    fade_out
        CALL    load_part_2
        CALL    run_part_2
        ...
```

The framework handled:

- **Part sequencing**: loading and running parts in order, with fades between them.
- **Music continuity**: keeping the PT3 player running across part transitions.
- **Disk access**: standardized calls into TR-DOS for loading part data.
- **Memory banking**: switching Pentagon 128 RAM banks cleanly.
- **Error handling**: what to do when a part fails to load (usually show a fixed error screen).

The framework was not a single published codebase; it was a *convention* that emerged from shared practice. Groups learned the framework by reading each other's source code, which was routinely distributed in source-code disk-magazine releases.

### 5.6 Beeper music refinement

Although AY-based music dominated the Soviet scene, the beeper (1-bit) music tradition also has Soviet roots. The Beeper music engines developed by Soviet-era coders — particularly Shiru's work — pushed 1-bit synthesis to extraordinary sophistication, producing polyphonic music, sampled drums, and software synthesis that the original Spectrum designers never imagined possible. See [1bit_music_scene.md](1bit_music_scene.md) for the full history.

---

## 6. The Pro Tracker 3 (PT3) Music Ecosystem

No single piece of software shaped the Soviet scene as deeply as **Pro Tracker 3** (PT3). Released by Progress around 1997, PT3 became the *de facto* — and effectively *only* — AY music format on the Soviet scene for nearly a decade, then went on to become the global standard for AY composition. This section explains how a Soviet tracker conquered the world.

### 6.1 What PT3 is

PT3 is a music-module format and a DOS-style tracker application for the AY-3-8910/8912/YM2149 sound chip. A `.pt3` file contains:

- **Pattern data**: 3 channels (A, B, C) of note, sample, ornament, volume, and effect commands, in a custom pattern-grid layout.
- **Sample data**: wave-like envelopes — not samples in the PCM sense, but amplitude envelopes applied to the AY's built-in tone generator. Each sample defines how the volume of a note changes over time.
- **Ornament data**: short pitch-arpeggio patterns applied on top of a note — the mechanism behind the chord-like arpeggios characteristic of AY music.
- **Header**: a fixed-layout header with pointers to patterns, samples, and ornaments, plus a fixed tempo value.

The PT3 player code is a ~600-byte Z80 routine that, given a pointer to a `.pt3` module, decodes one frame of music per call. Demos call the player once per frame from the interrupt handler (50 Hz on Pentagon, 50.08 Hz on Sinclair).

### 6.2 Why PT3 displaced earlier formats

The Soviet scene had several AY tracker formats before PT3. The most important predecessors were:

- **Pro Tracker 1 (PT1)** (Progress, ~1993): a simpler early format with limitations in sample length and ornament control.
- **Pro Tracker 2 (PT2)** (Progress, ~1995): a major refinement, but still lacked the expressivity composers wanted.
- **Sound Tracker** (ST): a parallel lineage with different conventions.
- **Sound Tracker Pro** and **ASM**: later competing formats.

PT3 won for four reasons:

1. **Longer samples and ornaments.** PT3 removed the strict length limits that had constrained PT2. Composers could build evolving textures that were impossible in earlier formats.
2. **Better player efficiency.** The PT3 player was carefully tuned for the Pentagon's uncontended RAM: a player call cost ~3000–4000 T-states on average, leaving plenty of frame budget for graphics.
3. **Cross-compatibility.** PT3 modules produced on a Pentagon ran unchanged on Sinclair hardware (with adjusted interrupt timing). This made PT3 the first format whose music crossed the East–West border without conversion.
4. **Network effect.** Once PT3 reached critical mass (around 1998–1999), every composer wanted their modules to be playable by every demo. Other formats faded for lack of players.

### 6.3 PT3 as a lingua franca

By 2000, PT3 had become so universal that the format itself became a kind of social infrastructure:

- **Music disks** — standalone programs that play a curated selection of PT3 modules with menu navigation — became a major release category. The best music disks (*Brainwave*, *Yummies*, *Chip Revolution*, *ZXM*) reached audiences far beyond the demoscene.
- **Party compos** at CC, CAFe, DiHAlt, and Forever all ran PT3-only music compos. Composers wrote directly to the format.
- **Module archives** at zx-art.ru, zx.ee, and Demozoo categorised PT3 modules by composer, year, and style — the canonical reference for the global AY music scene.
- **Conversion tools** emerged to translate between PT3 and other formats (MOD, MIDI, VGM), making PT3 a hub in a wider format graph.

### 6.4 The PT3 player as a code library

The PT3 player routine itself is a remarkable piece of code. It was reverse-engineered, optimized, and re-released by many hands over the years. Notable versions:

- **PT3P (S.../MMA)**: the canonical Soviet-era player, distributed as relocatable Z80 source.
- **EPT3 / ETracker player**: optimized for size, used in many 1K/4K intros.
- **PT3 x1000** (used by many post-2000 demos): a high-tempo variant supporting tempo multiplication for more expressive timing.
- **Modern SjAsmJ versions**: re-assembled with contemporary cross-assemblers for use in modern demos.

A typical PT3 player call site in a demo looks like:

```z80
; --- per-frame interrupt handler ---
frame_irq:
        PUSH    AF
        PUSH    BC
        PUSH    DE
        PUSH    HL
        EXX
        PUSH    BC
        PUSH    DE
        PUSH    HL
        EX     AF,AF'
        PUSH    AF

        LD      HL,(current_module)
        CALL    pt3_play           ; one frame of PT3 music

        ; ... graphics code follows ...

        POP     AF
        EX     AF,AF'
        POP     HL
        POP     DE
        POP     BC
        EXX
        POP     HL
        POP     DE
        POP     BC
        POP     AF
        EI
        RETI
```

The aggressive register preservation (saving the alternate register set, which PT3 clobbers) is a hallmark of Soviet demo code: the main-loop code uses the alternate registers for its own state, and the music player must not disturb them.

### 6.5 PT3 composers and the AY aesthetic

PT3 enabled a distinctive Soviet AY aesthetic. Soviet composers (among many others: **MW**, **Nik-O**, **Ironman**, **ASBel**, **Miguk**, **Tiboh**, **X-Trade's Yerzmyey**, **Zilogator**) developed a sound characterized by:

- **Rich ornaments** used as a substitute for chord instruments — arpeggiated 3- and 4-note chords produced from a single AY channel, since the chip has only three tone channels.
- **Sample-driven envelopes** that mimicked acoustic instruments (guitar-like plucks, drum-like percussive attacks, brass-like swells).
- **Driving rhythmic use of the AY's noise channel** for hi-hats, snares, and drum fills.
- **Bass lines on the third channel** with heavy use of pitch-bend ornaments.

This aesthetic — dense, melodic, fast — became the sound of the Soviet scene. Western AY composers who later adopted PT3 (especially after Forever's PT3 compos began accepting Western entries in the early 2000s) largely adopted this Soviet-originated aesthetic.

### 6.6 Limitations and the post-PT3 era

PT3 was not perfect. Its limitations, well-known to composers, included:

- **Fixed 3 channels.** No easy way to use TurboSound (dual AY) for 6-channel music without running two PT3 players in parallel.
- **No native digital samples.** PCM drums required workarounds (sampled data multiplexed onto the AY's envelope).
- **Integer note frequencies only.** Microtonal work required ornaments used as a hack.
- **Pattern-grid layout** that was wasteful for songs with long repeated sections.

Several post-PT3 formats attempted to address these:

- ** Chip Tracker (CHP)**, **FC**, and others: tried to add digital-sample support.
- **Vortex Tracker II (VT2)**: a modern (post-2005) tracker that reads/writes a PT3-compatible superset, addressing some ergonomic complaints.
- **Text tracks (TXT)** and direct AY-register-sequence formats: used by some later composers for finer control.

None displaced PT3. By the time the scene had the resources to build better formats, the active composer base had shrunk, and the network effect was too strong. PT3 remains the standard in 2025.

See [1bit_music_scene.md](1bit_music_scene.md) for the parallel (and earlier) beeper-music tradition, and [demoscene_history.md](demoscene_history.md) §6 for the cross-border AY narrative.

---

## 7. Disk Magazines and the FidoNet Era

The Soviet scene developed publication and communication infrastructure that had no Western equivalent. Where the Western scene relied on dial-up BBSes and (later) web archives, the Soviet scene relied on **disk magazines** for publication and **FidoNet** for real-time communication. This section explains how these worked and why they mattered.

### 7.1 Disk magazines (diskmags)

A **disk magazine** (or *diskmag*) is a standalone program — typically a single TR-DOS `.trd` or `.scl` disk image — that contains editorial content, scene news, reviews, interviews, and (importantly) embedded demo/music content. The reader boots the disk on their Pentagon, navigates a menu, and reads or watches the content.

The major Soviet diskmags were:

- **Body** (Body Corp., 1994–): one of the longest-running and most influential. *Body* published news, reviews, and embedded demos. Many Western researchers' first contact with Soviet scene writing came via archived *Body* text.
- **Spectrofon** (1995–): a higher-production-value diskmag from Moscow. *Spectrofon* included long-form articles, game reviews, and tutorials. The *Spectrofon* staff later contributed to *ZX-Format*.
- **ZX-Format** (St. Petersburg, 1996–): one of the most technically-oriented diskmags. *ZX-Format* published programming tutorials, hardware reviews, and scene interviews. Issues 1–7 (1996–1997) are particularly important as primary sources for early Soviet scene history.
- **Error** (Minsk, late 1990s–): a smaller diskmag with strong Skrju involvement. *Error* expressed strong opinions on the scene and was a venue for polemical writing.
- **ZX-Power**, **Adventurer**, **Magic**, **Polesse**: smaller diskmags with regional followings.
- **NeOS News**, **CONNEXION**: late-period diskmags focused on current scene activity.

The diskmag format solved three problems for the Soviet scene:

1. **Publication venue.** There were no commercial magazines covering the Soviet Spectrum scene; diskmags filled that role.
2. **Distributed review.** Diskmags reviewed party releases, sometimes harshly. This provided quality pressure.
3. **Embedded media.** Diskmags included playable demos and music — readers could experience the work being reviewed without swapping disks.

Diskmag editors wielded significant cultural authority. A positive *Body* or *ZX-Format* review could make a demo's reputation; a negative review could sink it.

### 7.2 FidoNet echomail

**FidoNet** was a store-and-forward dial-up networking system used widely in the Soviet bloc before HTTP internet access became common. FidoNet organized communication into **echomail conferences** (echoes), each devoted to a topic. Messages propagated node-by-node over nightly long-distance calls.

The most important FidoNet echoes for the Soviet scene were:

- **`ZX.SPECTRUM`**: the primary all-Soviet Spectrum echo. All major scene announcements, technical discussions, and flame wars happened here.
- **`SUCESSNET`** (Success Net): a wider Soviet-scene echo covering other platforms as well.
- **`RU.HACK`** and **`RU.EMULATOR`**: broader Russian-language echoes that touched on Spectrum topics.
- **`ECHO.SPECTRUM`**: an English-language echo occasionally bridged into `ZX.SPECTRUM`.

FidoNet was the Soviet scene's IRC. It was where group members coordinated, parties were organized, techniques were debated, and flame wars burned for months. The store-and-forward nature (messages took 1–3 days to propagate across the network) meant that discussions had a slower, more deliberate pace than modern chat.

FidoNet archives survive at zx-pk.ru and nedoPC.ru. They are a critical primary source for Soviet scene history, preserving day-to-day texture that no retrospective article can fully reconstruct.

### 7.3 BBSes and file distribution

In addition to FidoNet, several cities had **dial-up BBSes** that carried Spectrum files (`.trd`, `.scl`, `.tap`, `.pt3`, `.z80` snapshots). The major BBS hubs were in:

- **Moscow**: multiple BBSes, some operated by commercial software vendors.
- **St. Petersburg**: strong BBS presence, partly due to ENLiGHT/CC organisers.
- **Kyiv**: CAFe-adjacent BBSes.
- **Minsk**: Skrju-adjacent.
- **Ryazan**: DiHAlt-adjacent.
- **Rybinsk**: CPU/Inward-adjacent.

Throughput was tiny by modern standards — a single disk image (~200 KB) might take 10–20 minutes to download at 2400 baud — but sufficient for a subculture.

### 7.4 Radio distribution (the early years)

A remarkable feature of the very early Soviet scene (1989–1992) was **distribution via FM radio broadcast**. Polish and Czechoslovak state radio stations, during off-peak hours, would broadcast Spectrum software as audio (using a format similar to the Spectrum's standard tape encoding). Soviet listeners in range would record the broadcast onto cassette and load it.

This was one of the few ways software crossed the Iron Curtain before cheap diskettes became available. By 1993, diskette swapping had displaced it.

### 7.5 The HTTP internet transition

The Soviet scene's transition to the HTTP internet happened gradually between 1998 and 2005. Major milestones:

- **zx-art.ru** (~2000): the first major Russian-language HTTP archive of Spectrum demos, music, and graphics. Eventually became the canonical reference.
- **nedoPC.ru** (~2001): a Russian-language forum and file archive, still active.
- **zx-pk.ru** (~2003): the largest Russian-language Spectrum forum. Replaced FidoNet as the primary real-time discussion venue.
- **Demozoo / Pouët**: English-language archives that gradually incorporated Soviet scene releases from ~2004 onwards.
- **Scene.org**: mirrored Soviet releases from ~2002 onwards.

The HTTP transition was uneven: many older sceners stayed on FidoNet through the late 2000s. But by 2010 the move to web forums was effectively complete, and FidoNet activity had collapsed.

---

## 8. The Post-Soviet Transition (2005–2015)

The decade from 2005 to 2015 was a transitional period for the Soviet/post-Soviet scene. The peak (1998–2005) was over; the modern revival (2015–present) had not yet begun. The scene did not die, but it contracted and refocused.

### 8.1 Emulators become primary

By 2005, real Pentagon hardware was aging. Replacement parts were scarce; some critical ICs (original AY-3-8912 chips) were essentially unobtainable. Emulators became the primary platform for both development and consumption:

- **Unreal Speccy (US)**, by SMT/Max: the canonical Russian emulator. Cycle-accurate for Pentagon hardware, supports all extensions (TS-Config, TurboSound, General Sound, NeoGS).
- **ZXMAK2**: a Windows-based emulator with strong Pentagon support and an active Russian user community.
- **ZEsarUX**: a cross-platform emulator (originally Spanish, later international) that supports Pentagon hardware alongside original Sinclair.
- **SpecEmu**, **EightyOne**, **Zero**: UK-developed emulators focused on original Sinclair hardware, but increasingly including Pentagon support.

The shift to emulators had two effects:

- **Development became easier.** No more burning EPROMs, no more swapping diskettes on physical hardware.
- **Hardware fidelity concerns emerged.** Demos that worked perfectly in Unreal Speccy sometimes failed on real Pentagon hardware (and vice versa). The scene developed strong opinions about which emulator was authoritative.

### 8.2 Online archives consolidate

The HTTP transition (§7.5) reached its mature form in this period. By 2012, the canonical archives were:

- **zx-art.ru**: Russian-language, comprehensive. The de facto reference for Soviet scene releases.
- **zxart.ee**: Estonian-language, very comprehensive, well-curated.
- **Demozoo.org**: English-language, cross-platform, increasingly including Soviet scene releases.
- **bbb.retroscene.org**: Russian-curated, focused on demo releases.
- **Pouët.net**: English-language, focused on PC demos but accepting Spectrum releases.
- **Scene.org**: mirror service for major archives.

The consolidation made the Soviet scene discoverable to international researchers for the first time. Much of what is now known in the West about Soviet scene history comes from these archives.

### 8.3 Language and the East–West gap

A persistent challenge for the post-Soviet scene was the **Russian-language barrier**. Soviet scene writing — diskmag articles, FidoNet archives, group documentation, code comments — was overwhelmingly in Russian. Western researchers without Russian had to rely on:

- Occasional English-language summaries in diskmags like *Body* (which had a bilingual section).
- English-language party announcements on Forever's and Sundown's websites.
- Personal contact with bilingual sceners (Elfh/Inward, Gasman, others).
- Machine translation, which became usable for technical writing only around 2010.

This language gap is the primary reason the Soviet scene remained under-documented in the West for so long. Even today (2025), much primary-source material exists only in Russian; serious Western research into Soviet scene history requires either Russian-language skills or close collaboration with Russian-speaking sceners.

### 8.4 Party continuity and contraction

Demo parties continued through the post-Soviet transition, but attendance contracted:

- **Forever** (Slovakia) became the primary international venue for Spectrum work, with both Western and Eastern entries.
- **CC** (St. Petersburg) continued but at smaller scale; multi-platform focus shifted increasingly toward PC and modern hardware.
- **CAFe** (Kyiv) became intermittent.
- **DiHAlt** (Ryazan) continued as a small, focused event.
- **Sundown** (UK, 2004–) carried the Western-flag banner through the late 2000s.
- **Syntax** (Russia) emerged as a smaller event.

The party circuit did not collapse — it shrank and specialized. By 2012, sceners who wanted serious Spectrum compo competition went to Forever; sceners who wanted Russian-scene social reunion went to CC or DiHAlt.

### 8.5 Technical baseline at 2012

By 2012, the typical high-end Russian Spectrum demo targeted:

- **Pentagon 128** or **Pentagon 1024** (emulated or FPGA).
- **TS-Config** for disk-streamed multicolor (see §5.3).
- **TurboSound** (dual AY) or **General Sound** for audio.
- **PT3** for music composition.
- **SjAsmJ** or **SjAsmZ** as the cross-assembler.
- **Unreal Speccy** as the primary development/testing emulator.

This baseline remained essentially stable for the next decade. The hardware stopped getting better (no new Pentagon-style extensions after TS-Config achieved wide adoption), but the techniques continued to be refined. Demos from 2012 and demos from 2022 target the same nominal hardware, but the 2022 demos are dramatically more polished.

---

## 9. The Modern Russian Scene (2015–present)

From approximately 2015, the post-Soviet scene entered a modest but real renaissance. The contraction of 2005–2012 stopped; new hardware appeared; new sceners joined; the technique baseline continued to improve.

### 9.1 FPGA hardware and the new-platform effect

The single most important enabler of the modern revival was **FPGA-based hardware**. Several products gave sceners cycle-accurate, real-hardware-feeling platforms without relying on aging 1990s PCBs:

- **ZX Uno** (~2015): a modern FPGA Spectrum with onboard Pentagon compatibility, TS-Config in FPGA, and writable RTC/RAM. Became the de facto modern Russian-scene hardware.
- **MiSTer** (popular ~2018–): an FPGA platform with a high-quality Spectrum core supporting both Sinclair and Pentagon modes, including TS-Config and TurboSound. Widely adopted internationally.
- **Harlequin** (Spain/UK, ~2014–): an FPGA Spectrum with original-Sinclair focus, popular in Western scene but Pentagon-capable in later revisions.
- **ZX Evolution** (Russia, earlier but still relevant): a Russian-made FPGA board directly descended from the Pentagon lineage.
- **ATM Turbo 4+** and modern ATM boards: continued Russian-manufactured hardware for purists.
- **ZX Spectrum Next** (2020, UK-developed but Russian-supported): a new commercial Spectrum-class machine, originally targeting Western audiences but with significant Russian scene engagement.

The new hardware did three things:

1. **Eliminated the parts-availability problem.** Original AY-3-8912 chips are essentially exhausted; FPGA clones emulate them perfectly.
2. **Restored cycle-accuracy.** Modern FPGA cores are more cycle-accurate than emulators, so demos that were emulator-only can run on hardware again.
3. **Standardised extensions.** TS-Config, TurboSound, and other Pentagon extensions are now universally available across the FPGA platforms, removing the per-clone portability concerns of the 1990s.

### 9.2 The 2015–2025 release calendar

Despite the much smaller scene, releases have continued steadily:

- **Forever** (Slovakia, annual): the primary international venue. Spectrum compos at Forever are the highest-quality in the West.
- **CC** (St. Petersburg, annual): still the largest Russian party. Spectrum compos continue, with both new demos and old-style effects.
- **DiHAlt** (Ryazan, intermittent): smaller, focused, traditional.
- **CAFe** (Kyiv, intermittent): continues when circumstances permit.
- **NVScene** and **Revision** (international): occasional Spectrum entries in the "oldskool demo" compos.
- **Sundown** (UK): smaller international venue.
- **Online compos** (Yandex, ZXdev, occasional Reddit-/forum-hosted events): smaller but accessible.

The 2020–2022 period was particularly productive, with several landmark releases (full-screen TS-Config video at 25fps, 3D demos matching 1990s PC work, and intricate 1K/4K intros). The COVID-19 pandemic, by forcing parties online, paradoxically increased participation.

### 9.3 Active groups in 2025

As of 2025, the most active Russian-language groups include (in approximate order of recent release volume):

- **CyberPunks Unity (CPU)**: still active. Multi-generational; new members have joined continuously.
- **Skrju**: still active, with both veteran members and newer collaborators.
- **Inward**: still active in experimental work. Elfh continues to produce solo and collaborative pieces.
- **Simbols**: active.
- **Triebkraft + 4th Dimension**: active.
- **BraveStorm**: active in intros.
- Newer groups: small collectives forming around younger sceners.

The scene is smaller than at its 1998–2005 peak — perhaps 50–100 actively-producing sceners across all groups — but it is **not** in decline. The release rate is roughly stable; the technique baseline continues to advance.

### 9.4 Current technique baseline

A high-end 2025 Russian demo targets:

- **ZX Uno** or **MiSTer (Pentagon core)** for hardware.
- **Pentagon 1024** memory map with TS-Config streaming.
- **TurboSound (dual AY) or NeoGS** for audio.
- **PT3** for music (still — no successor has displaced it).
- **SjAsmJ** for assembly, often with C or Rust cross-development for tools.
- **ZX0, ZX1, ZX2, or LZSA2** for asset compression (see [compression_packing.md](compression_packing.md)).
- **Modern build pipelines** with Git, CI, and automated asset conversion.

This baseline has been stable since approximately 2018. The continued refinement — rather than hardware replacement — is the defining feature of the modern era. Each year's demos incrementally extend what is possible on the same nominal 1993 hardware.

### 9.5 The international context

The modern Russian scene operates in a fundamentally international context that did not exist during the Soviet era:

- **Demozoo / Pouët / Scene.org** carry releases to a global audience within hours.
- **Discord / Telegram** (replacing IRC, FidoNet, and web forums) carry real-time discussion. The primary Russian-language scene channels are Telegram-based as of 2025.
- **GitHub** hosts most modern Russian scene code (open-source releases are now standard, unlike the closed-source norm of the 1990s).
- **YouTube** carries recorded demos, demoparty streams, and tutorials — a major vector for new members joining the scene.

The language barrier (§8.3) has eased somewhat: many Russian sceners now write English-language README files for their releases, and Demozoo entries increasingly have bilingual descriptions. But primary-source Russian-language writing (zx-pk.ru forum archives, Russian-language YouTube content) remains the deepest layer of the scene's documentation.

### 9.6 Political and demographic concerns

A serious concern for the post-2022 scene is **geopolitical disruption**. The February 2022 Russian invasion of Ukraine disrupted multiple long-running scene relationships: Ukrainian sceners (particularly Kyiv-based, CAFe-adjacent) and Russian sceners (particularly St. Petersburg, Ryazan, Rybinsk) had been close colleagues since the 1990s. Travel restrictions, financial sanctions (which affected some payment processors used for scene donations), and direct personal risk made collaboration across the border difficult or impossible for some.

The scene has responded pragmatically: joint releases have continued where possible, online compos have remained open, and individual sceners have largely maintained professional-artist-to-professional-artist relationships independent of national politics. But the long-term effect on the post-Soviet scene's social cohesion is still being assessed (as of 2025).

Demographically, the modern Russian scene skews older than at its peak (most active sceners are 35–55). Younger members do join — particularly via the demoscene's presence on modern platforms (YouTube, Discord) — but the absolute number of new entrants is smaller than in the 1990s. This is the same pattern observed in all retro-computing hobbies and is not unique to the Spectrum scene.

---

## 10. Cross-References and Further Reading

### 10.1 Articles in this section

- [demoscene_history.md](demoscene_history.md) — full cross-platform narrative; the Soviet scene is treated in §5 and §6 there, complementing this article.
- [compression_packing.md](compression_packing.md) — Soviet packer lineage (LZ4/LZSA2/ZX0 family) discussed in §4 of that article.
- [multicolor_techniques.md](multicolor_techniques.md) — full technical treatment of multicolor and gigascreen (§5.1, §5.2 here).
- [effects_catalog.md](effects_catalog.md) — catalog of effects; Soviet-origin effects (gigascreen, disk-streamed multicolor) flagged.
- [demo_frameworks.md](demo_frameworks.md) — Soviet framework convention (§5.5 here) covered in depth.
- [notable_demos.md](notable_demos.md) — technical analysis of landmark Soviet demos (Evenless, I am the seed, etc.).
- [1bit_music_scene.md](1bit_music_scene.md) — beeper music tradition (§5.6 here).
- [size_coding.md](size_coding.md) — Soviet 1K/4K intro tradition.

### 10.2 Hardware documentation

- [../02_hardware/clones/README.md](../02_hardware/clones/README.md) — full clone census including Pentagon, Scorpion, Profi, Kay, ATM.
- [../02_hardware/clones/clone_timing.md](../02_hardware/clones/clone_timing.md) — contention timing differences across clones.
- [../02_hardware/original/ula_architecture.md](../02_hardware/original/ula_architecture.md) — original ULA architecture for comparison.

### 10.3 External archives and primary sources

- **zx-art.ru** — Russian-language canonical archive of demos, music, graphics.
- **zxart.ee** — Estonian comprehensive archive.
- **bbb.retroscene.org** — Russian-curated demo archive.
- **Demozoo.org** — cross-platform English-language archive.
- **zx-pk.ru** — largest Russian-language Spectrum forum; FidoNet archives also accessible.
- **nedoPC.ru** — Russian forum and file archive.
- **zxdemo.org** — Gasman's long-running archive, now powered by Demozoo.
- **Scene.org** — mirror service.
- **Mustekala magazine** (2008 article by Elfh/Inward) — primary source quoted in §3 and §4. Available at [http://mustekala.org/archive/](http://mustekala.org/archive/) (or via the Wayback Machine).

### 10.4 Key books and academic sources

- **Antti Silvast & Markku Reunanen (2014)**, *Demoskene: Sukupolvi joka pelasi tietokoneella* (in Finnish; on the broader demoscene, with Soviet-scene material).
- **Gleb Albert Ichtmann (2017)**, PhD dissertation on the demoscene (German; international scope, Soviet material in §4).
- **Marek Trescak et al.**, various papers on demoscene cultural impact.
- **UNESCO Intangible Cultural Heritage** citation (2021, Germany) — formal recognition; relevant material in [demoscene_history.md](demoscene_history.md) §10.
- **Demozoo / Pouët** party results — primary factual reference for individual demo releases and competition outcomes.

---

## License

This article is released under the **Creative Commons Attribution-ShareAlike 4.0 International License** ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)). You are free to share and adapt the material, provided you credit the original source and license derivative works under the same terms.

Quoted primary-source material (especially Elfh/Inward's 2008 *Mustekala* article) remains the copyright of its original authors and is cited under fair-dealing / fair-use conventions for scholarly commentary.
