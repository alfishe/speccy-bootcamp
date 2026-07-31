[← Home](../../README.md) · [BASIC](README.md)

# Basic Sound — BEEP, Frequency, Duration, and Music from BASIC

The 48K ZX Spectrum has a single sound source: a **1-bit beeper** driven through port `#FE` bit 4. There is no sound chip, no envelope generator, no AY-3-8912 — just a single bit that the CPU flips between 0 and 1 at audio frequencies. The 128K and later models add an AY-3-8912 (or YM2149F), but on the original machine, every sound you hear — from a one-line `BEEP` to the multi-channel music in *Chuckie Egg* — is produced by carefully timed writes to that single bit.

BASIC exposes this primitive through exactly one command: `BEEP duration, pitch`. This article covers what `BEEP` does, how the parameters map to musical notes, and how to compose simple melodies in BASIC. For the underlying hardware and assembly-level beeper programming, see [beeper.md](../../06_sound/beeper/beeper.md).

> [!NOTE]
> This article covers **BASIC-level sound only**. For AY-3-8912 programming (128K and later), see [ay_3_8912.md](../../06_sound/ay_3_8912.md). For multi-channel beeper music engines (Popov, Follin, etc.), see [beeper_engines.md](../../06_sound/beeper/beeper_engines.md).

---

## The BEEP Command

```basic
BEEP duration, pitch
```

- **`duration`** — length in **seconds** (floating-point, e.g., `0.5` for half a second)
- **`pitch`** — semitones above (positive) or below (negative) **middle C** (integer or floating-point)

`BEEP` blocks execution for the duration of the note — there is no background music in BASIC. The CPU enters a tight loop that toggles the beeper bit at the calculated frequency, and no other code runs until the note completes.

### Examples

```basic
BEEP 1, 0              : REM 1 second of middle C (~261.63 Hz)
BEEP 0.5, 0            : REM half a second of middle C
BEEP 1, 12             : REM 1 second of C one octave up (~523.25 Hz)
BEEP 1, -12            : REM 1 second of C one octave down (~130.81 Hz)
BEEP 2, 4.5            : REM 2 seconds of a note between E and F (quarter-tone)
```

The `pitch` parameter accepts **non-integer values** — this lets you produce microtonal notes that fall between standard semitones. `BEEP 1, 4.5` produces a frequency halfway between E (4 semitones above middle C) and F (5 semitones above), which is a quarter-tone not found in standard Western music.

---

## The Pitch Parameter

Sinclair BASIC uses **semitones above middle C** as its pitch unit. This is convenient for musicians because each integer step corresponds to one note on a piano keyboard:

| Pitch | Note | Frequency (Hz) |
|---|---|---|
| -12 | C3 (one octave below middle C) | 130.81 |
| -7 | F3 | 174.61 |
| -5 | G3 | 196.00 |
| -2 | A3 | 220.00 |
| 0 | **C4 (middle C)** | **261.63** |
| 2 | D4 | 293.66 |
| 4 | E4 | 329.63 |
| 5 | F4 | 349.23 |
| 7 | G4 | 392.00 |
| 9 | A4 | 440.00 (concert pitch reference) |
| 11 | B4 | 493.88 |
| 12 | C5 (one octave above middle C) | 523.25 |
| 24 | C6 (two octaves up) | 1046.50 |

### Frequency Formula

The frequency is computed as:

```
frequency = 261.63 × 2^(pitch / 12)
```

So for pitch = 0, frequency = 261.63 × 1 = 261.63 Hz (middle C). For pitch = 12, frequency = 261.63 × 2 = 523.25 Hz. The `2^(1/12)` ratio between adjacent semitones is called an **equal-tempered** scale — the same tuning used by pianos.

> [!NOTE]
> The exact reference frequency used by the Spectrum ROM is **261.63 Hz** for middle C (pitch = 0), matching concert pitch. However, the **actual output frequency** varies slightly because the beeper is driven by a CPU delay loop, and the loop timing must be an integer number of T-states. The error is typically under 0.5% — imperceptible to most listeners, but measurable with test equipment.

### Beyond the Equal-Tempered Scale

Because `pitch` accepts floating-point values, you can produce **microtonal** music:

```basic
BEEP 1, 0.5            : REM C-half-sharp (quarter-tone above middle C)
BEEP 1, 3.5            : REM D-half-sharp
BEEP 1, 12 / 7         : REM seventh of an octave (Bohlen-Pierce scale)
```

This is rarely used in practice, but it is unique to the Spectrum among home computers of the era. The MIDI standard, by contrast, uses integer semitones only.

---

## The Duration Parameter

The `duration` parameter is in **seconds** and accepts floating-point values:

```basic
BEEP 0.25, 0           : REM quarter-second middle C
BEEP 1.5, 7            : REM 1.5 seconds of G4
BEEP 0.01, 0           : REM 10 ms click (effectively a percussion sound)
```

The minimum meaningful duration is about **0.003 seconds** (3 ms) — shorter than that and the beeper loop has too few iterations to produce a recognizable pitch. Durations longer than ~30 seconds risk integer overflow in the ROM's delay counter.

### Tempo

Standard musical tempos map to durations as follows (assuming a quarter-note beat):

| Tempo | Beats per minute | Duration per beat (sec) | Duration per quarter-note |
|---|---|---|---|
| Largo | 60 | 1.0 | 1.0 |
| Andante | 90 | 0.667 | 0.667 |
| Moderato | 110 | 0.545 | 0.545 |
| Allegro | 140 | 0.429 | 0.429 |
| Presto | 180 | 0.333 | 0.333 |

To play a melody at Allegro (140 BPM), use `BEEP 0.429, pitch` for each quarter note.

---

## Composing Melodies in BASIC

A melody is a sequence of `(duration, pitch)` pairs. The straightforward approach uses DATA statements:

```basic
10 REM Simple melody — "Twinkle Twinkle Little Star"
20 RESTORE 100
30 FOR N = 1 TO 14
40   READ D, P
50   BEEP D, P
60 NEXT N
100 DATA 0.4, 0,  0.4, 0,  0.4, 7,  0.4, 7
110 DATA 0.4, 9,  0.4, 9,  0.8, 7
120 DATA 0.4, 5,  0.4, 5,  0.4, 4,  0.4, 4
130 DATA 0.4, 2,  0.4, 2,  0.8, 0
```

Each note is two DATA values: duration (in seconds) and pitch (in semitones from middle C). `READ` extracts the pairs one by one, and `BEEP` plays them sequentially.

### Note Lookup Table

For source-code readability, it is common to define note names via a lookup table:

```basic
10 REM Note table — pitch values for octave 4
20 DIM N(7)
30 LET N(1) = 0:  REM C
40 LET N(2) = 2:  REM D
50 LET N(3) = 4:  REM E
60 LET N(4) = 5:  REM F
70 LET N(5) = 7:  REM G
80 LET N(6) = 9:  REM A
90 LET N(7) = 11: REM B
100 REM Now we can write:  BEEP 0.5, N(3)
```

A more sophisticated setup includes sharps/flats and multiple octaves:

```basic
10 DIM N$(12, 2)
20 LET N$(1) = "C ":  LET N$(2) = "C#":  LET N$(3) = "D "
30 LET N$(4) = "D#":  LET N$(5) = "E ":  LET N$(6) = "F "
40 LET N$(7) = "F#":  LET N$(8) = "G ":  LET N$(9) = "G#"
50 LET N$(10) = "A ":  LET N$(11) = "A#":  LET N$(12) = "B "
```

### Tempo Control with Variables

```basic
10 LET T = 0.4         : REM base duration (Allegro)
20 BEEP T, 0           : REM quarter note middle C
30 BEEP T * 2, 7       : REM half note G
40 BEEP T / 2, 9       : REM eighth note A
```

Using a single tempo variable lets you change the speed of an entire piece by editing one line.

---

## Sound Effects (Non-Musical)

The BEEP command is also useful for non-musical sound effects — clicks, blips, lasers, explosions:

### Click

```basic
BEEP 0.02, 0
```

A 20 ms middle C click — useful for key-press feedback or menu navigation.

### Laser / Whoosh

```basic
10 FOR P = 60 TO 0 STEP -2
20   BEEP 0.02, P
30 NEXT P
```

A descending pitch sweep, 60 semitones in 60 steps of 20 ms each (total 1.2 seconds). Sounds like a laser or falling bomb.

### Explosion

```basic
10 FOR P = -10 TO -30 STEP -1
20   BEEP 0.05, P
30 NEXT P
```

A rumble of low pitches, descending into sub-bass. Combined with a few high clicks at the start, this mimics an explosion.

### Warbling Tone

```basic
10 FOR I = 1 TO 20
20   BEEP 0.05, 12 + 5 * SIN(I)
30 NEXT I
```

A warbling tone using `SIN` to modulate the pitch around the octave-above-middle-C note. Useful for "power-up" effects.

### Phone Ringing

```basic
10 FOR I = 1 TO 8
20   BEEP 0.2, 16
30   BEEP 0.2, 20
40 NEXT I
```

A two-tone warble reminiscent of a UK telephone ring.

---

## Limitations of BASIC Sound

### 1. Blocking Execution

`BEEP` blocks the CPU for the entire duration of the note. You cannot play music while doing anything else — the program is effectively frozen. This makes BASIC sound unsuitable for game soundtracks (you must choose between music and gameplay).

The workaround for games is to intersperse very short `BEEP`s (10–30 ms) between game updates, creating a "click-and-blip" soundtrack rather than continuous music. The alternative is to write an assembly-level sound engine that runs from the interrupt handler — see [beeper_engines.md](../../06_sound/beeper/beeper_engines.md).

### 2. Single Voice

The beeper can produce only **one frequency at a time**. There is no chord support, no bass-and-melody layering, no percussion alongside melody. To simulate chords, you can rapidly alternate between pitches (`BEEP 0.05, 0: BEEP 0.05, 4: BEEP 0.05, 7`) — but this produces an arpeggio, not a true chord.

The 128K's AY-3-8912 chip solves this with three independent channels — see [basic_128k.md](basic_128k.md) (planned) for the `PLAY` command.

### 3. Volume is Fixed

The beeper is either on or off — there is no volume control. You cannot fade notes in or out, you cannot balance melody against percussion. The only way to simulate volume changes is to use very short bursts of BEEP with longer gaps (pulse-width modulation), which is the technique used by advanced beeper engines — but this requires cycle-exact assembly code, not BASIC.

### 4. Pitch Drift at High Frequencies

At very high pitches (above C7, pitch = 36), the beeper delay loop becomes so short that quantization errors are audible. Notes sound slightly off-pitch. At extreme high pitches (above C8, pitch = 48), the loop has too few iterations to produce a stable tone, and the output degenerates into a buzzing square wave.

### 5. Aliased Low Frequencies

At very low pitches (below C2, pitch = -24), the beeper period exceeds the Spectrum's interrupt interval (20 ms), and the ROM's frame-interrupt handler disrupts the timing. The note may warble or click audibly. For clean sub-bass, assembly code is required (to disable interrupts during the note).

---

## PLAY on the 128K

The 128K ROM adds the `PLAY` command, which drives the AY-3-8912 sound chip and supports up to three simultaneous voices. The syntax is string-based:

```basic
PLAY "CDEFGAB"
```

This plays the seven natural notes (C-D-E-F-G-A-B) sequentially. More complex syntax allows specifying duration, articulation, and tempo per note:

```basic
PLAY "TEMPO 120; C4D4E4F4G4A4B4"   : REM each note is a quarter note at 120 BPM
```

The full `PLAY` syntax is documented in the 128K manual. It is more powerful than `BEEP` (three voices, envelopes, volume control) but also more complex. Many 128K BASIC programmers still use `BEEP` for simple sounds because it is simpler and works on both 48K and 128K Spectrums.

> [!NOTE]
> On a 128K Spectrum running in 48K mode, `BEEP` routes to the AY-3-8912 chip (rather than the beeper) for cleaner output, but the syntax and parameters are identical. This is invisible to the BASIC program.

For full AY-3-8912 programming from assembly language, see [ay_3_8912.md](../../06_sound/ay_3_8912.md).

---

## Worked Example — A Complete BASIC Tune

Here is a complete BASIC program that plays the opening of Beethoven's "Ode to Joy" with proper note lengths:

```basic
10 REM Ode to Joy — Beethoven, arr. for ZX Spectrum
20 LET T = 0.4           : REM quarter-note duration (Allegro)
30 RESTORE 100
40 FOR N = 1 TO 16
50   READ D, P
60   BEEP D * T, P
70 NEXT N
80 STOP
100 REM (duration multiplier, pitch)
110 DATA 1, 4, 1, 4, 1, 5, 1, 6
120 DATA 2, 7, 1, 6, 1, 5, 1, 4
130 DATA 1, 2, 1, 0, 1, 2, 1, 4
140 DATA 2, 0, 1, 0, 1, 4, 1, 4
```

Notes used:

- Pitch 0 = middle C (C4)
- Pitch 2 = D4
- Pitch 4 = E4
- Pitch 5 = F4
- Pitch 6 = F#4 (Beethoven uses E-F natural, but pitch 6 is closest)
- Pitch 7 = G4

The duration multiplier is 1 for quarter notes and 2 for half notes. Total runtime: roughly 8 seconds.

### Running This on a Pentagon

The Pentagon's frame rate is 48.83 Hz (not 50.08 Hz), so all `BEEP` durations are about 2.5% longer than on a real Spectrum. An 8-second tune on a 48K becomes about 8.2 seconds on a Pentagon. This is rarely noticeable, but if you are timing your music precisely, you may need to adjust.

---

## Common Pitfalls

### 1. Forgetting the Semicolon vs Comma

```basic
BEEP 1 0              : REM syntax error — missing comma
BEEP 1; 0             : REM syntax error — semicolon is wrong
BEEP 1, 0             : REM correct
```

The two parameters are separated by a **comma**, not a semicolon or space.

### 2. Confusing Pitch with Frequency

```basic
BEEP 1, 440           : REM does NOT play 440 Hz — plays an extremely high pitch
BEEP 1, 9             : REM plays 440 Hz (A4, 9 semitones above middle C)
```

The `pitch` parameter is in **semitones from middle C**, not in Hertz. If you want to play a specific frequency in Hz, you must convert:

```basic
10 REM Play a specific frequency in Hz
20 LET F = 440         : REM desired frequency
30 LET P = 12 * LN(F / 261.63) / LN(2)   : REM convert to semitones
40 BEEP 1, P
```

### 3. Using BEEP in a Loop Causes Clicking

```basic
10 FOR P = 0 TO 24
20   BEEP 0.1, P
30 NEXT P
```

Each `BEEP` turns the beeper on at the start and off at the end. The gaps between iterations produce audible clicks. To get a continuous sweep, you would need to write a custom beeper routine in assembly that does not gate the beeper between notes.

### 4. Negative Durations

```basic
BEEP -1, 0            : REM "A Invalid argument, 30:1"
```

Durations must be positive. Zero duration is accepted but produces no audible output (just a brief click from the beeper being toggled once).

### 5. Very Long BEEP Can Overflow

```basic
BEEP 100, 0           : REM probably works but ties up the machine for 100 seconds
BEEP 10000, 0         : REM may crash or produce integer overflow
```

The ROM's delay counter is 16-bit, which limits BEEP duration to about 65535 / 50 ≈ 1310 seconds (~22 minutes) in theory. In practice, durations longer than ~30 seconds are unstable because the counter interacts with the frame interrupt.

---

## Performance Notes

| Operation | Time | Notes |
|---|---|---|
| `BEEP 0.1, 0` | 100 ms + ~2 ms overhead | The 2 ms is for parameter setup; the note itself is 100 ms |
| `BEEP 1, 0` | 1000 ms + ~2 ms | Same overhead per call regardless of duration |
| `BEEP 0.001, 0` | ~3 ms total | Below this, the loop runs too few iterations to produce a tone |

The overhead per `BEEP` call is roughly 1–3 ms — significant if you are playing many very short notes (a staccato passage at 200 BPM has 6.7 notes per second, so 10–20 ms of overhead per second). For real-time music, assembly code that enters the beeper loop once and stays in it is far more efficient.

---

## Cross-References

- [Basic intro](basic_intro.md) — Sinclair BASIC foundation: tokens, syntax, variables
- [Basic graphics](basic_graphics.md) — `PLOT`, `DRAW`, `CIRCLE`, `POINT`, `ATTR`
- [Basic PEEK/POKE/USR](basic_peek_poke.md) — direct memory and port access from BASIC
- [Beeper hardware](../../06_sound/beeper/beeper.md) — how the 1-bit beeper works at the hardware level
- [Beeper music engines](../../06_sound/beeper/beeper_engines.md) — Popov, Follin, and other multi-channel beeper engines (assembly only)
- [AY-3-8912 PSG](../../06_sound/ay_3_8912.md) — 128K and later sound chip
- [128K BASIC extensions](basic_128k.md) (planned) — `PLAY`, `SOUND`, and the 128K editor
- [Basic dialects comparison](basic_dialects_comparison.md) (planned) — differences between 48K, 128K, TIMEX, and other BASIC dialects

---

## References

- **Sinclair ZX Spectrum Basic Programming** (Steven Vickers, 1982) — chapter 16 covers `BEEP` with frequency and duration details
- **Sinclair User Issue 29 — Helpline** (February 1984): https://sinclairuser.com/029/helplne.htm — semitone-to-frequency conversion table used by the ROM
- **The Complete Spectrum ROM Disassembly** (Logan & O'Hara, 1983) — chapter on the `BEEP` routine (`BEEP` at `#03F8`, frequency calculation at `#0487`)
- **World of Spectrum — ZX BASIC Manual Chapter 16**: https://worldofspectrum.org/ZXBasicManual/zxmanchap16.html
- **Soft Spectrum 48 — Timing and the Beeper**: https://softspectrum48.weebly.com/notes/timing-and-the-beeper — timing analysis of the BEEP routine
