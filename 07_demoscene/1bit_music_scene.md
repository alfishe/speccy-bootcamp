[← Home](../README.md) · [Demoscene](README.md)

# 1-Bit Music Scene — Beeper Synthesis as a Subculture

> **Scope**: This article covers the **ZX Spectrum 1-bit "beeper" music subculture**: the composers, engines, techniques, and community that turned a single bit of output hardware into one of the most distinctive soundscapes in 8-bit computing. The technical synthesis details are covered in [../06_sound/synthesis/beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md); this article is the scene-and-people companion, covering who made the music, what tools they built, and how the community evolved from 1982 to the present.
>
> The 1-bit scene is unusual in the demoscene because it is **partly orthogonal to the demo scene**: many of its most important figures are game soundtrack composers (Tim Follin, Ben Daglish) rather than demosceners, and many of its modern engines are developed by hobbyists who do not make demos at all. The article therefore includes substantial coverage of game music and of standalone engine development, alongside the demoscene side.

---

## Article Roadmap

- §1 — Why 1-bit?: the hardware constraint as a creative challenge.
- §2 — Beeper hardware: port #FE, the ROM `BEEP` driver, contention, timing.
- §3 — Synthesis techniques: from single-voice to multi-voice to PCM.
- §4 — Engine lineage: Henry → Follin → Wham → QChan → Octode → Pusher/Squeeker.
- §5 — Key composers: Follin, Daglish, utz, irrlicht project, Mr. BEEP, Rotter.
- §6 — Beeper music in games: the legendary 48K soundtracks.
- §7 — The 1-Bit Forum and the modern community.
- §8 — Cross-platform beeper: PC speaker, SAM Coupé, Atari POKEY, etc.
- §9 — Compos and the modern scene.
- §10 — Cross-references.

---

## 1. Why 1-Bit?

The unexpanded 16K/48K ZX Spectrum has a **single bit** of audio output: a 1-bit register at I/O port `#FE`, bit 4, connected through an amplifier to an internal speaker (or, on later models, to the TV's speaker via the ULA). Setting the bit toggles the speaker cone between two positions; clearing it toggles it back. That is the entire audio hardware.

By any normal engineering judgment, this is the **worst possible sound hardware**. It cannot produce volume levels (only on/off), it cannot produce different wave shapes (only square), it cannot play multiple notes at once (only one frequency at a time), and its maximum frequency is limited by how fast the CPU can toggle the bit. The Commodore 64's SID, the Amiga's Paula, the Atari ST's Yamaha YM chip — all of them vastly outclass the Spectrum's beeper.

What makes the 1-bit scene remarkable is that sceners and game musicians refused to accept this judgment. Over the course of forty years, they built up a body of techniques that extracts from the single bit:

- **Multi-voice music**: 2, 3, 4, 5, 6, 7 or even more simultaneous notes.
- **Percussion**: kick drums, hi-hats, snares, and cymbals.
- **Timbre**: distinct instrument voices (organ, bass, lead, arpeggiated pads).
- **Sample playback**: short PCM recordings of speech or sound effects.
- **Effects**: vibrato, tremolo, portamento, slide.

None of this was intended by the hardware's designers. All of it is the result of careful cycle-exact programming that exploits the **integration behavior** of the speaker cone, the amplifier, and the ear itself.

### 1.1 The Allure of the Impossible

The 1-bit scene's appeal is partly the **impossibility allure**: this hardware should not be able to do what it demonstrably does. Each new engine that adds another voice, another effect, or another percussive sound is met with the same delighted surprise by listeners who know what the hardware is. The 1-bit scene is, in this sense, the purest expression of the demoscene ethos: take the worst possible platform, and make it do the impossible.

### 1.2 The affordability factor

There is also a practical reason why 1-bit music mattered: **the 48K Spectrum was cheap**. In 1982, a 48K Spectrum cost £175 in the UK; a Commodore 64 cost £329. The price gap was even wider in Eastern Europe, where the Spectrum and its clones dominated the home computer market throughout the 1980s and early 1990s. Millions of families had a Spectrum and nothing else. If you wanted to make music on a home computer in 1985, in most of the world, the 1-bit speaker was what you had.

### 1.3 Aesthetics

The 1-bit sound has its own aesthetic. The harsh, ringing timbre of fast pulse-width modulation, the buzzing of multi-voice chords, the characteristic "pin-ball" sound of two-voice counterpoint — these are immediately recognisable. Many 1-bit composers consider the aesthetic not a compromise but a **choice**, and resist attempts to make 1-bit music sound "smoother" or "more realistic". The point is what the hardware sounds like; the art is in working with that sound, not around it.

---

## 2. Beeper Hardware

This section covers the hardware at the level needed to understand the music scene. The full synthesis-level details are in [../06_sound/synthesis/beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md).

### 2.1 Port #FE

The Spectrum's beeper is controlled by a single I/O port:

- **Port address**: `#FE` (i.e., any address with `A0 = 0` and `A1..A7 = 1`, but conventionally `#FE`).
- **Output bit 4**: the speaker (1 = cone pushed out, 0 = cone pulled back).
- **Output bits 0–2**: the border color (the same port sets the border).
- **Output bit 3**: the MIC/EAR cassette output (early models).
- **Output bits 5–7**: unused.

To toggle the speaker, code writes to `#FE` with bit 4 alternating between 0 and 1. The border color comes along for the ride — every music routine that toggles the speaker also changes the border, which is why classic 1-bit music on the Spectrum has the characteristic **"music also paints the border"** side effect.

### 2.2 The ROM `BEEP` Driver

The 48K ROM provides a `BEEP` routine at address `#03B5` that plays a single note. The interface is:

- **Entry**: pitch in HL (cycles per second, ×2), duration in DE (seconds ×10).
- **Effect**: a single square-wave note plays for the given duration; the routine blocks until done.

The ROM driver is **single-voice** and **blocking**: it cannot play music in the background, and it cannot play two notes at once. From a music-making perspective, this is essentially useless except for jingles and sound effects. Every 1-bit music engine from the 1980s onward bypasses the ROM and writes to port `#FE` directly.

`BEEP` is also useful as a **size-coding trick**: in a 256-byte intro, calling `BEEP` lets the demo play a note in 3 bytes of code (CALL + RET), where implementing a custom routine would cost 50–100 bytes. See [size_coding.md](size_coding.md) §6.

### 2.3 Timing and Contention

The hard part of 1-bit music is **timing**. The speaker cone is moved by an electromagnet that integrates the bit pattern over time. To produce a clean tone at frequency `f`, the code must toggle the bit at frequency `2f`, and each toggle must occur at a precise moment relative to the previous one. Any jitter (variation in toggle-to-toggle time) produces audible distortion.

The Z80's instruction timing is deterministic, so cycle-counting the toggle loop is the standard approach. However, the Spectrum has **memory contention**: the CPU and the ULA (which is reading the screen) share the lower 16K of RAM, and during active display the ULA gets priority. The CPU is paused ("contended") on certain cycles. The contention pattern depends on the scanline position, so a tight inner loop that runs at full speed during the border area runs slower during the screen area.

A 1-bit music engine must either:

1. **Run only during the border area** (vertical blanking) — limits the maximum frequency and timing precision.
2. **Run continuously and account for contention** — the engine's inner loop must include the contention pattern in its cycle count.

The second approach is used by all serious engines; the first is used only by very simple melodies. See [../06_sound/synthesis/beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md) for the contention tables.

### 2.4 Per-Model Differences

The 48K, 128K, +2, +2A, +3, and Pentagon all have slightly different contention patterns. An engine that produces clean music on a 48K may produce buzzing or detuning on a +2A. This is a recurring problem for the 1-bit scene: an engine must be **per-model** to sound right on all Spectrums.

The Pentagon, which has a slightly different ULA from any Sinclair-produced model, has its own contention pattern; Soviet-era 1-bit music is rare (most Soviet sceners used the AY chip), but the modern Russian scene does produce Pentagon-targeted beeper music.

---

## 3. Synthesis Techniques

This section is an overview; the full technical details are in [../06_sound/synthesis/beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md).

### 3.1 Single-Voice

The simplest 1-bit music is a **single square-wave voice**. The engine toggles bit 4 of port `#FE` at twice the desired frequency, holding each value for a half-period. Code structure:

```z80
play_note:
    LD   B,period_hi
    LD   C,period_lo
loop:
    XOR  A                  ; speaker off
    OUT  (#FE),A
    CALL delay              ; wait half-period
    LD   A,#10              ; bit 4 set, speaker on
    OUT  (#FE),A
    CALL delay              ; wait half-period
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,loop
    RET
```

This is the technique used by every Spectrum game's title-screen jingle from 1982 to about 1985, and by every crack intro of that era. It is audibly limited: no chords, no percussion, no timbre variation. The ROM `BEEP` routine is essentially a more polished version of this technique, with floating-point pitch handling.

### 3.2 Multi-Voice via "Pin-Balling"

The breakthrough to multi-voice music came in the mid-1980s with the **"pin-ball" technique**, attributed to **Keith "Henry" Murdoch** (1985, working at Softek). The technique interleaves multiple voices' toggles in the same inner loop:

```z80
loop:
    ; toggle voice 1 if its period has elapsed
    ; toggle voice 2 if its period has elapsed
    ; toggle voice 3 if its period has elapsed
    JR   loop
```

Each voice has its own **period counter**, decremented every iteration of the loop. When a voice's counter reaches zero, the speaker is toggled (XOR'd with that voice's "current state" bit) and the counter is reset.

The catch: only one physical speaker exists. When voice 1 wants the speaker "up" and voice 2 wants it "down", the engine must choose. The standard approach is to **XOR the voices together**: each voice contributes a bit, the engine outputs the XOR of all current bits. This produces the characteristic "ringing" interference sound of multi-voice 1-bit music — sometimes called **"amplitude modulation"** or **"sum-and-difference"** tones.

The audible result is that the listener hears not only the two intended notes, but also their **sum frequency** and **difference frequency**, plus various harmonics. With skill, the spurious tones become part of the music's texture rather than noise.

### 3.3 Phase-Reset Technique

A refinement of pin-balling is the **phase-reset** technique. Each voice has a fixed, short period (e.g., 100 iterations); when the counter reaches zero, the engine toggles the speaker and resets the counter. Because each voice runs at its own frequency independently, the voices' phases drift continuously, producing the rich, evolving texture characteristic of 2-channel and 3-channel 1-bit engines.

Phase-reset is the technique used by most pre-2008 beeper engines (Wham, Music Studio, the Special FX engine used in Tim Follin's soundtracks). It is also the technique that the modern engines (QChan, Octode, Pusher) build on, with refinements.

### 3.4 Pulse-Width Modulation (PWM)

To produce **volume variation** or **timbre variation**, an engine can vary the **duty cycle** of the square wave: instead of spending half the period "on" and half "off", the engine might spend 25% on and 75% off (a "narrow" pulse), or 75% on and 25% off (a "wide" pulse).

The listener perceives a narrow pulse as **quieter** than a 50% pulse, because the speaker cone moves less air on average. The listener also perceives a different **timbre**: narrow pulses have more energy in their upper harmonics, sounding brighter and thinner; wide pulses sound rounder.

PWM is used heavily in modern engines to give each voice a distinct character (bass = narrow pulse, lead = wide pulse, percussion = very narrow pulse). The CPU cost is moderate: each voice needs a duty-cycle counter in addition to its period counter.

### 3.5 PCM Sample Playback

A separate branch of the 1-bit scene is **sample playback**: rendering digitised audio through the speaker. The technique pre-dates multi-voice music — it was used in 1982 by **Bug-Byte's** "Manic Miner" loading screen, and was standard for Spectrum speech throughout the 1980s.

The engine stores a sequence of 1-bit samples (or, for higher fidelity, a sequence of deltas that the engine integrates). It toggles the speaker at a fixed sample rate (often 8–16 kHz on the Spectrum, with elite engines reaching 22 kHz or higher). The result is recognisable speech, drums, or short musical clips.

**Delta modulation** is a refinement: instead of storing absolute 1-bit values, the engine stores the **sign of the change** in the audio waveform. An integrator in the engine reconstructs an approximation of the original waveform. The result is significantly better fidelity than raw 1-bit samples for the same bit rate.

Notable Spectrum PCM playback engines include the **"Robin of the Wood"** speech, the **"Chronos"** voice, and the modern **"1-bit music and speech"** engines that combine multi-voice music with PCM samples.

### 3.6 Trade-Offs

Every 1-bit engine makes trade-offs along three axes:

| Trade-off | Description |
|---|---|
| **Channel count vs CPU cost** | Each additional voice consumes CPU cycles in the inner loop, limiting the maximum toggle frequency and therefore the highest note playable. |
| **Frequency range vs jitter** | Faster inner loops allow higher notes but produce more timing jitter, causing detuning and noise. |
| **Voice richness vs frequency range** | PWM, vibrato, and per-voice envelopes add code in the inner loop, slowing it down. |

The "ideal" engine therefore depends on the music: a chiptune-style piece with 5 short voices needs a different engine than a melodic piece with 2 rich voices. This is why the 1-bit scene has dozens of engines, each optimized for a different point on the trade-off surface. See §4 for the engine lineage.

---

## 4. The Engine Lineage

The 1-bit engine lineage is a forty-year chain of borrowing, refinement, and reinvention. Each engine builds on (or reacts against) the one before it. The earliest engines are lost to time — Spectrum game developers in 1982–1984 typically wrote their own ad-hoc beep routines, and only a few names survive. From the mid-1980s onward, the engines are better documented.

### 4.1 The Henry Engine (1985, Softek)

The first documented multi-voice beeper engine is **Keith "Henry" Murdoch's**, written in 1985 for Softek (a UK games publisher). The engine produced **two simultaneous voices** by interleaving their toggles in the inner loop, with each voice having its own period counter. This is the original "pin-ball" engine that all later multi-voice beeper engines descend from.

Henry's engine was used in several Softek games and quickly spread to other publishers via the typical 1980s mechanism of programmers changing employers. By 1987, the two-voice beeper engine was standard for any Spectrum game that wanted music.

### 4.2 The Follin Engine (1987–1990)

**Tim Follin** (born 1970, UK) is widely considered the greatest 48K Spectrum soundtrack composer. Starting at age 16, Follin wrote music for several Spectrum games using a custom engine that pushed the pin-ball technique further:

- **Three voices** instead of two.
- **Software envelopes** on each voice (attack, decay, sustain, release).
- **Percussion** via short noise bursts on a fourth "drum" channel.
- **Pitch slides, vibrato, and arpeggios**.

The result was unlike anything else on the Spectrum. Follin's soundtracks for *Agent X* (1986, Mastertronic), *Agent X II* (1987), *Chronos* (1987), *Bionic Commando* (1988), *Black Lamp* (1988), and *Ghouls 'n Ghosts* (CPC/Spectrum, 1989) are still considered the peak of 48K Spectrum game music.

Follin's engine was never publicly released, but the techniques were reverse-engineered in the late 1990s and have influenced every modern beeper engine.

### 4.3 Wham Music Editor (1989, Jason Brookes)

The first widely-used **general-purpose beeper music editor** was **Wham**, written by Jason Brookes in 1989. Wham let a musician compose 2- or 3-voice beeper music in a tracker-like interface, then exported a binary that any game or demo could play. This was a generational change: previously every game's music engine was bespoke; with Wham, the music engine became a shared platform.

Wham's engine was based on the pin-ball technique with phase-reset voices, similar to Follin's but without the envelopes or percussion. It was less capable than Follin's engine, but it was **accessible** — any musician could write music in it, not just Follin.

Wham was widely used in early 1990s Spectrum demos and games. See [notable_demos.md](notable_demos.md) §4.3 for its role in the Western Golden Age.

### 4.4 Music Studio (1991, JSL/ROM)

**Music Studio** (also known as **Roman's Music Editor**, but distinct from other editors of that name) was a more sophisticated beeper editor from the early 1990s. It supported:

- Three voices (versus Wham's two).
- A fourth "noise" channel for percussion.
- Per-voice volume (via PWM).
- Pattern-based composition (similar to PT1/PT2/PT3, but for the beeper).

Music Studio was used in a number of Western megademos in the early 1990s. By the mid-1990s, however, the AY chip had become standard for the demoscene, and beeper music retreated to the size-coding and game-music niches.

### 4.5 The 1995–2008 Gap

From roughly 1995 to 2008, there was **little new development** in beeper engines. The demoscene had moved to the AY (128K and Pentagon), and game development for the Spectrum had effectively ended. The surviving beeper engines (Wham, Music Studio) continued to be used in size-coding intros, but no major new engines appeared.

The one exception was the **Soviet-era "MIDI" engine** used in a few Russian games, which attempted to combine beeper music with PCM percussion. This engine never became standard in the Soviet scene (which preferred the AY from 1996 onward), and is mostly forgotten today.

### 4.6 QChan (2008, utz)

The modern revival of beeper music began with **QChan** (also spelled **Q-Chan** or **Q-chan**), written by **utz** (an Austrian scener) in 2008. QChan was a **4-voice engine** with per-voice PWM, designed to push the beeper as far as it could go using only the basic pin-ball technique.

QChan's breakthrough was not a new technique — the techniques were those Follin had used 20 years earlier — but its **availability**: utz released the source on the 1-Bit Forum (§7), with per-model variants for 48K, 128K, +2A, +3, and Pentagon. This made it easy for any modern musician to write 4-voice beeper music that ran on real hardware.

QChan triggered the modern beeper revival: within a year, several new engines had appeared.

### 4.7 Octode (2010, utz)

**Octode** (utz, 2010) pushed the voice count to **8**. This was widely considered impossible: with eight voices, the inner loop has so many toggles to check that the maximum toggle frequency drops below the highest audible frequencies. Octode solved this by using a **fixed** inner loop where every voice is always checked, and by accepting a slightly lower maximum note frequency in exchange for the channel count.

Octode music sounds very different from Follin-style 3-voice music: it is busier, buzzier, more chiptune-like. The technique is now standard for "wall of sound" beeper compositions where the goal is maximum channel density rather than melodic clarity.

### 4.8 Huby, ZX Polyphony, and Shiru's Engines

In parallel with utz's work, several other modern engine authors contributed:

- **Huby** (Patrik "Rak" Rak, ~2010) — a 2-voice engine optimized for **maximum frequency range**, sacrificing channel count for clean high notes. Used for melodic music where Follin-style clarity is the goal.
- **ZX Polyphony** (irrlicht project, 2009–2012) — an experimental engine attempting **real polyphonic synthesis** with per-voice timbre.
- **Shiru's beeper engines** (Shiru, ~2010) — a family of small engines optimized for size-coding intros, sometimes only 100–200 bytes of player code. Used in many modern 1K/256B intros (see [size_coding.md](size_coding.md) §9).

These engines cover different points on the trade-off surface (§3.6), so a modern musician chooses the engine that best fits the piece.

### 4.9 Pusher, Squeeker, Sq1, Phaser1 (2013–present)

The most recent wave of beeper engines, developed by **utz**, **irrlicht project**, **Mr. BEEP**, and others, includes:

- **Pusher** — a high-channel-count engine using per-voice "push-pull" (driving the speaker both up and down on each cycle, instead of just up).
- **Squeeker** — a compact engine with squeaky, high-treble timbre.
- **Sq1** — a single-voice engine with very rich timbre, optimized for solo melodic pieces.
- **Phaser1** — a phase-modulation engine that produces evolving, phasing textures.
- **Savage** — a modern 5+ channel engine with per-voice envelopes.

These engines are typically **open-source**, distributed on Github and the 1-Bit Forum (§7), and continually refined by their authors and contributors. The state of the art advances year by year, with new engines appearing regularly.

### 4.10 Engine Comparison Table

The major engine families summarised:

| Engine | Year | Voices | Author | Use case |
|---|---|---|---|---|
| Henry | 1985 | 2 | Henry Murdoch | First multi-voice; vintage games |
| Follin | 1987–1990 | 3 + drums | Tim Follin | Peak 48K game soundtracks |
| Wham | 1989 | 2–3 | Jason Brookes | Demoscene standard 1989–1994 |
| Music Studio | 1991 | 3 + noise | JSL/ROM | Western megademos 1991–1995 |
| QChan | 2008 | 4 | utz | Modern revival starter |
| Octode | 2010 | 8 | utz | Maximum channel count |
| Huby | 2010 | 2 | Patrik Rak | Maximum frequency range |
| ZX Polyphony | 2009–2012 | polyphonic | irrlicht project | Experimental synthesis |
| Shiru beeper | ~2010 | varies | Shiru | Size-coding intros |
| Pusher | 2013+ | varies | utz et al. | Modern "wall of sound" |
| Phaser1 | 2013+ | 2–3 | irrlicht project | Phasing textures |

The demoscene canon for modern 1-bit music includes engines from all of these families; the choice is per-piece.

---

## 5. Key Composers

The 1-bit scene's composers fall into three broad traditions: **game soundtrack composers** (the 1980s and early 1990s tradition), **the size-coding tradition** (composers who wrote for 1K/256B intros), and **the modern revival composers** (post-2008, working in the new engines).

### 5.1 Tim Follin (1969–present)

**Tim Follin** is the single most celebrated 1-bit composer. Born in the UK in 1969, he began writing Spectrum music at age 14–15 (1983–1984) and produced his most acclaimed work between 1986 and 1990, while still a teenager. Follin's day job was writing music for commercial Spectrum games; he later moved to the C64, Amiga, and consoles (NES, Game Boy, PC) before retiring from game music in the late 1990s.

Follin's signature pieces for the Spectrum include:

- *Agent X* (1986, Mastertronic) — three-voice beeper music with envelopes and percussion, at a time when most games had one-voice jingles.
- *Agent X II: The Mad Prof's Return* (1987, Mastertronic) — further refinement of his three-voice engine.
- *Chronos* (1987, Mastertronic) — atmospheric, evolving music that used the beeper for both melodic and ambient textures.
- *Bionic Commando* (1988, GO!/US Gold) — fast arpeggios and percussion.
- *Black Lamp* (1988, Firebird) — long-form melodic pieces.
- *Ghouls 'n Ghosts* (1989, US Gold) — Follin's last great Spectrum soundtrack, a cover of the arcade original.

Follin's Spectrum work has been called "the greatest music ever produced on the worst sound chip" — an overstatement, but a revealing one. His engine was the technical peak of pre-AY Spectrum music, and his pieces remain the standard against which modern beeper composers measure themselves.

### 5.2 Ben Daglish (1966–2018)

**Ben Daglish** was a contemporary of Follin's, working across the C64, Amiga, and Spectrum in the 1980s. His Spectrum output was smaller than Follin's but technically distinctive: Daglish preferred **cleaner, more melodic** soundtracks with explicit counterpoint, where Follin preferred richer, more textured soundscapes.

Daglish's best-known Spectrum soundtracks include *The Last Ninja* (1987, vs the more famous C64 version) and *Crosswize* (1987, Gremlin Graphics). He remained active in the retro scene until his death in 2018 and was a vocal advocate for 1-bit music as a serious art form.

### 5.3 Martin Galway (1966–present)

**Martin Galway** is best known for his C64 soundtracks (the canonical *Comic Bakery*, *Green Beret*, *Wizball*), but he also produced a few Spectrum pieces. Galway's Spectrum work is less influential than his C64 work but is admired for its tight melodic construction. He remains an important bridge between the C64 and Spectrum 1-bit scenes.

### 5.4 Fred Gray and Jonathan Dunn

**Fred Gray** (*Out Run*, *Power Drift*) and **Jonathan Dunn** (*RoboCop*, * Target: Renegade*) are among the other named Spectrum game soundtrack composers whose work is still admired. Their style is generally more conservative than Follin's (closer to the Wham/Music Studio two- and three-voice baseline), but their melodies are well-loved.

### 5.5 The Size-Coding Tradition

The size-coding 1-bit tradition (composers writing for 256B and 1K intros) is anonymous or pseudonymous by custom: most size-coded intros credit the musician only by handle. Notable figures include:

- **Shiru** — Russian composer and engine author, contributed many 1-bit pieces for size-coded intros.
- **Mr. BEEP** — Belgian composer and engine author, specialises in pieces that maximize musical interest per byte of music data.
- **Rotter** — Polish composer, several notable 1-bit pieces in the late 2000s.

These composers often write music that is **as much a technical achievement as a musical one**: a melodic 1-bit piece in 200 bytes of music data is as much a size-coding feat as a 256-byte intro is.

### 5.6 utz (Modern revival)

**utz** (Austrian, real name not public) is the central figure of the modern 1-bit revival. As an **engine author**, utz created QChan, Octode, Pusher, Squeeker, and Savage — five of the most-used modern beeper engines. As a **composer**, utz's work demonstrates each engine's capabilities and is widely referenced as the canonical modern 1-bit style.

utz is also a **technical writer**: the [1-Bit Forum](http://randomflux.tv/1bit) (§7) and the associated documentation are largely utz's work, and many modern 1-bit composers learned the technique from utz's writeups and source code releases.

### 5.7 irrlicht project

**irrlicht project** (real name not consistently public; the handle is the German word for "will-o'-the-wisp") is the other central modern 1-bit figure. irrlicht is responsible for ZX Polyphony, Phaser1, and several experimental engines, as well as a substantial body of compositions in those engines. irrlicht's music tends toward **atmospheric, evolving textures** rather than the high-density arpeggios favored by utz.

### 5.8 Other Modern Composers

The modern 1-bit scene has a healthy cohort of composers releasing music at Forever, AY Compo, and other compos. Names change year by year; the canonical sources are the [1-Bit Forum](http://randomflux.tv/1bit) and the ZXArt.ee 1-bit music section.

---

## 6. Beeper Music in Games

The 1-bit beeper's primary commercial application was **game soundtracks** for the 48K Spectrum. From 1982 to roughly 1992, almost every Spectrum game that shipped with in-game music used the beeper; the 128K's AY chip did not become standard for game soundtracks until the late 1980s, and even then only for games explicitly targeted at the 128K (a smaller market than the 48K).

### 6.1 The Golden Age of 48K Spectrum Game Music (1985–1990)

The period 1985–1990 is the **golden age of beeper game music**. The form was established, the engine techniques had matured (with Follin as the leading figure), and the 48K Spectrum was still a viable commercial platform. Notable 48K soundtracks include:

- **Agent X / Agent X II / Chronos** (1986–1987, Mastertronic, Follin) — the peak of the era.
- **Bionic Commando, Black Lamp, Ghouls 'n Ghosts** (1988–1989, Follin).
- **Raw Recruits** (1987, Ocean, composed by Martin Galway) — short, punchy, melodic.
- **Target: Renegade** (1987, Imagine, Jonathan Dunn) — title theme widely admired.
- **RoboCop** (1988, Ocean, Jonathan Dunn) — atmospheric, multi-section piece.
- **Crosswize** (1987, Gremlin, Ben Daglish).
- **Star Paws** (1987, Follin, Mastertronic).

By 1990, the commercial quality of beeper music had reached its peak; after that, the publishers moved to AY or to abandoning the Spectrum entirely.

### 6.2 Loading Music

A separate 1-bit tradition is **loading music**: music that played during the several-minute tape-loading sequence of a Spectrum game. Because the loader had to run alongside the actual tape-handling code (which was timing-critical), loading music was technically simpler than in-game music — usually single-voice, with carefully crafted timing. Notable loading music includes the **Speedlock** and **Alcatraz** loaders, both of which became signature sounds of the Spectrum loading experience.

### 6.3 Speech and PCM Effects

Many Spectrum games used the beeper for **speech playback** — typically a short spoken phrase at the title screen or after certain in-game events. Notable examples:

- **"Get out of my way!"** in *Ghost 'n Goblins* (1986).
- **"Welcome to Chronos"** in *Chronos* (1987).
- **"Robin of the Wood"** in *Robin of the Wood* (1985).
- **"Wizard's Lair"** in various titles.

These PCM clips were usually 1-bit samples at ~6–10 kHz, sounding harsh but recognisable. The technique was an offshoot of the broader 1-bit PCM tradition (§3.5).

### 6.4 The AY Transition (1989–1992)

From 1989 onward, major publishers increasingly targeted the 128K Spectrum (and its AY chip) for their flagship releases. The 48K beeper soundtrack became the secondary product, often a port or adaptation of the AY original. By 1992, beeper music was largely confined to budget titles and to games that explicitly targeted the 48K base.

The demoscene, however, continued to use the beeper through the 1990s, particularly in size-coding intros where the beeper was the only option (the AY was only on 128K machines, and a 1K intro had to work on 48K).

### 6.5 Modern Beeper in Games

In the modern revival (§7), the beeper has reappeared in **new Spectrum-targeted indie games**, particularly those made for the ZX Spectrum Next or distributed as .tap files via itch.io. Modern beeper game soundtracks use the new engines (QChan, Octode, Pusher) and demonstrate the gulf between 1987's three-voice Follin style and today's five-to-eight voice modern style. Specific modern titles are easier to track via Pouet.net, itch.io, and the Forever party archive than via Western-archives' outdated filters.

---

## 7. The 1-Bit Forum and the Modern Community

The modern revival of 1-bit music is organized around a single web forum: the **1-Bit Forum** at [randomflux.tv/1bit](http://randomflux.tv/1bit). The forum was founded in the late 2000s (most cited year: 2008, alongside utz's QChan release) and has been the central meeting place for the international 1-bit community since.

### 7.1 What the Forum Does

The 1-Bit Forum serves several functions simultaneously:

- **Engine releases** — new engines (QChan, Octode, Pusher, Phaser1, Squeeker, Sq1, Savage, etc.) are announced and discussed here first.
- **Composition compos** — periodic compos with themes ("write a piece in 4 weeks using only 2 voices", "write a piece that fits in 256 bytes of music data") produce a steady stream of new work.
- **Technical discussion** — timing tables, contention patterns, per-model differences, and per-engine tricks are documented in forum threads.
- **Help for newcomers** — "how do I get my engine to sound right on a +2A?" threads walk new musicians through the per-model calibration process.
- **Cross-platform discussion** — the forum covers PC speaker, SAM Coupé, and other 1-bit platforms alongside the Spectrum (§8).

The forum is small (a few hundred active members at any time) but disproportionately productive. Most modern 1-bit engines and most modern 1-bit composers have a thread there.

### 7.2 Key Figures

The forum's most prolific contributors overlap with the modern composers named in §5: utz, irrlicht project, Mr. BEEP, and several others who post under handles rather than real names. The community is international (Austria, Germany, Belgium, Poland, Russia, UK, US) and works in English as a lingua franca.

Tim Follin and other 1980s composers are **not** forum regulars, but they are referenced often; the modern community regards itself as building on the 1980s tradition, even when the original tradition's figures are no longer active.

### 7.3 Github and Modern Distribution

In parallel with the forum, modern 1-bit engines and compositions are increasingly distributed via **Github**. Engine authors release source with permissive licenses; composers release their `.mus` data files alongside the player code, so that a future scener can replay the music with the original engine. This is a generational change from the Soviet-era practice of binary-only distribution, and it means that modern 1-bit music is more durable than Soviet-era music: if the forum disappears, the Github releases survive.

### 7.4 Tutorials and Documentation

The 1-bit community has produced substantial **written documentation** for newcomers, including:

- **Pin-ball technique tutorials** — step-by-step construction of a 2-voice engine from scratch.
- **Contention tables** — the precise cycle-by-cycle timing for each Spectrum model.
- **Per-engine writeups** — design notes from the authors of each engine.
- **Reference compositions** — small, well-documented pieces that demonstrate each engine's idioms.

The documentation is scattered across the forum, Github READMEs, and a few standalone web pages. The [../06_sound/synthesis/beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md) article in this knowledge base is intended as a single-entry-point reference that consolidates the technical parts of this documentation.

---

## 8. Cross-Platform Beeper

The ZX Spectrum is not the only 1-bit platform. Several other computers and consoles have similar 1-bit output hardware and analogous 1-bit music traditions. The Spectrum scene has historically cross-pollinated with these scenes, sharing techniques and sometimes even composers.

### 8.1 The IBM PC Speaker

The original IBM PC (1981) and its clones shipped with a **single-bit speaker** connected to an Intel 8255 PPI. The hardware is conceptually identical to the Spectrum's beeper: a single bit toggles the speaker cone. The 1-bit music tradition on the PC includes the legendary *Space Hulk* (1993) intro, the *Impossible Mission* port, and many 1990s shareware games.

The PC-speaker 1-bit scene is smaller than the Spectrum's, but it has produced notable engines (notably the work of **Ken Silverman** of *Duke Nukem 3D* fame, who wrote PC-speaker music drivers) and continues today in the demoscene (PC-spearer category at certain parties). Techniques cross-pollinate freely between the two scenes.

### 8.2 The SAM Coupé

The SAM Coupé (1989, Miles Gordon Technology) is an ~8-bit Spectrum-compatible machine with substantial extensions, including an SAA1099 sound chip (similar to but more capable than the AY). The SAM Coupé also has a beeper-compatible port, so 1-bit Spectrum music runs on it with minor adaptation. The SAM Coupé scene is small but maintained 1-bit music activity into the 2000s.

### 8.3 The Atari 2600 / TIA

The Atari 2600 (1977) has a **TIA** chip with two audio channels, each producing square or asymmetric waves from a small palette of preset patterns. The TIA is not literally 1-bit (it has separate volume registers per channel), but the techniques for producing rich music on it overlap heavily with 1-bit techniques: tight cycle counting, multi-voice arpeggios, and percussion via noise bursts. The 2600 music scene is well-developed, with several modern engines (notably *Silly Venture*'s Atari 2600 music category).

### 8.4 The Atari POKEY

The Atari 400/800 (1979) and Atari 5200 console use the **POKEY** chip, which has four square-wave voices with a small amount of timbre control. POKEY is not 1-bit but, like the TIA, has inspired 1-bit-style engines that squeeze polyphony and timbre out of limited hardware. The modern Atari 8-bit music scene is closely tied to the 1-bit scene via shared composers and shared compos.

### 8.5 Other 1-Bit Platforms

Other platforms with 1-bit or near-1-bit audio include:

- **The BBC Micro** (1981) — single-channel sound chip, but with a simpler interface than the Spectrum.
- **The Cambridge Z88** (1987) — a single-bit piezo speaker.
- **The original Game Boy** — has 4 voices but one of them is a 1-bit-style square wave, leading to a similar aesthetic.
- **Many early Texas Instruments calculators** — single-bit piezo speakers, with active 1-bit music scenes among calculator hobbyists.

These scenes are smaller than the Spectrum's but produce distinctive work. The Spectrum scene's central position in 1-bit music is partly historical (the Spectrum was the most widely owned 1-bit-only machine) and partly current (the 1-Bit Forum and the demoscene still treat the Spectrum as the canonical 1-bit platform).

---

## 9. Compos and the Modern Scene

1-bit music has its own **competition circuit**, separate from (but overlapping with) the main demoscene party circuit.

### 9.1 The 1-Bit Compo at Forever

The **Forever party** (Slovakia, since 1996 — see [demoscene_history.md](demoscene_history.md) §9) is the most important annual event for the Spectrum demoscene, and it has a **dedicated 1-bit music compo**. Entries are 1-bit music files played on real hardware at the party; voters rank them on musical quality and technical sophistication. The 1-bit compo at Forever is the closest thing the 1-bit scene has to a "world championship".

### 9.2 The AY Compo

The AY Compo (Russian-language, online) is primarily for AY chip music, but it has occasionally run a 1-bit category. The AY Compo is more Russian-language-focussed than the 1-Bit Forum; it complements rather than competes with the forum.

### 9.3 The 1-Bit Forum Compos

The 1-Bit Forum runs periodic compos with rotating themes. Past compos have included:

- "Two-voice only" — write a piece using exactly two voices.
- "256 bytes" — write a piece where the music data must fit in 256 bytes (the player can be any size).
- "Engine fork" — take an existing engine and modify it; the piece must use a feature the original did not have.
- "Cross-platform" — write a piece that runs (with the same music data) on two 1-bit platforms.

These compos produce a steady stream of new work and are the main venue for composers who do not attend in-person parties.

### 9.4 ZXArt.ee and Pouet.net

ZXArt.ee has a 1-bit music section with thousands of entries spanning 1985 to the present. Pouet.net's 1-bit coverage is thinner (because Pouet is demo-focussed, not music-focussed). For archival purposes, ZXArt.ee is the canonical 1-bit music archive; for current releases, the Forever party archive and the 1-Bit Forum are equally important.

### 9.5 The Modern Scene's Health

The 1-bit scene is small but **healthy**. New engines appear every year or two; new compositions appear monthly; new composers join the forum regularly. The community is friendly and tutorial-focussed, and the technical barrier to entry has been substantially lowered by open-source engines and clear documentation. The 1-bit scene is one of the few Spectrum subcultures that is **growing rather than shrinking** in the 2020s, partly because the 1-bit constraint is appealing to musicians coming from other platforms (the Game Boy scene, the chipmusic scene generally) who want a new challenge.

---

## 10. Cross-References

### 10.1 Within the Demoscene Section

- [README.md](README.md) — section overview.
- [demoscene_history.md](demoscene_history.md) — the full cultural and historical narrative, including the beeper-to-AY transition (§§4–5 of that article).
- [soviet_demo_scene.md](soviet_demo_scene.md) — the Soviet scene used the AY (PT3) almost exclusively; the beeper was a Western-affiliated tradition. See §6 of that article for PT3.
- [demoscene_platforms.md](demoscene_platforms.md) — the AY/YM bridge (§9 of that article) explains why the Spectrum has two distinct music scenes (beeper and AY).
- [size_coding.md](size_coding.md) — beeper music is the only option for size-coded intros on the 48K (§§6 and 9 of that article).
- [demo_frameworks.md](demo_frameworks.md) — frameworks that schedule beeper music alongside effects (§§4 and 6 of that article).
- [notable_demos.md](notable_demos.md) — demos featuring beeper soundtracks (§§3–4 of that article, the crack intro and early megademo eras).

### 10.2 Outside the Demoscene Section

- [../06_sound/synthesis/beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md) — the technical synthesis deep-dive. This article is the scene-and-people companion; that article is the engineering reference.
- [../06_sound/README.md](../06_sound/README.md) — the broader audio section, covering the AY chip, beeper, and PCM traditions together.
- [../02_hardware/original/](../02_hardware/original/) — the original 48K Spectrum hardware (the only model with beeper-only audio).
- [../01_cpu/README.md](../01_cpu/README.md) — the Z80 CPU, whose cycle-exact timing is the foundation of every 1-bit engine.

### 10.3 External References

- **[1-Bit Forum](http://randomflux.tv/1bit)** — the central community hub.
- **[ZXArt.ee 1-bit music section](https://zxart.ee)** — the canonical music archive.
- **[Forever party archive](https://forever.zeroteam.sk)** — annual 1-bit compo entries.
- **[Pouet.net](https://www.pouet.net)** — 1-bit-tagged entries (demo-focussed).
- **[utz's Github](https://github.com/utz0r)** — modern engines source code (the most authoritative source for QChan, Octode, Pusher, Squeeker).

---

## License

This article is released under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share and adapt the material for any purpose, provided you attribute the source and license derivative works under the same terms. The full license text is at [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/).

Specific composer names, engine names, game titles, and other identifying details are drawn from publicly accessible archives (ZXArt.ee, Pouet.net, the Forever party archive, the 1-Bit Forum) as of 2024. Composer handles are the composers' own; real names are given only where they are already widely published in the demoscene or game-music literature. Trademarks, where they apply to specific games or engines, belong to their respective holders; their use here is for documentary and educational purposes only.
