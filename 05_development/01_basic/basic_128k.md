[← Home](../../README.md) · [BASIC](README.md)

# Sinclair BASIC 128K Extensions — Editor, PLAY, and the AY-3-8912

The 128K ZX Spectrum (1986) and its successors — the +2 (grey, 1986), the +2A (black, 1987), and the +3 (1987) — introduced a new 32 KB ROM that adds exactly one fundamentally new BASIC statement, **`PLAY`**, along with a substantially upgraded editor and a token table that is **not byte-compatible** with the 48K ROM. The +2A/+3 ROM further extends the language with disk operating system commands (`CAT`, `FORMAT`, `ERASE`, `MOVE`, `OPEN #`).

This article covers only the **delta from 48K BASIC**: the new editor, the `PLAY` mini-language, AY-3-8912 access patterns from BASIC, the `+2A`/`+3` DOS commands, and the compatibility pitfalls that arise from the different token tables. The full 48K language reference is in [basic_48k.md](basic_48k.md) — everything documented there (variable types, floating-point format, calculator stack, parser pipeline, PEEK/POKE/USR semantics, GO TO vs GOTO, mandatory LET, no ELSE, no DO/WHILE) applies unchanged on the 128K.

> [!NOTE]
> This article focuses on **language-level** extensions. For the hardware — the AY-3-8912 PSG, the #7FFD paging port, the eight RAM banks — see [ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md) and [memory_and_io_128k.md](../03_memory_and_io/memory_and_io_128k.md). For 128K-specific timing, see [video_frame_128k.md](../05_display_and_timing/video_frame_128k.md).

---

## The 128K Architecture in Brief

The 128K Spectrum is a substantially redesigned machine. From a BASIC programmer's perspective, the relevant changes are:

| Feature | 48K | 128K / +2 (grey) | +2A (black) / +3 |
|---|---|---|---|
| RAM | 48 KB (one bank) | 128 KB (8 banks of 16 KB) | 128 KB (8 banks of 16 KB) |
| Sound | 1-bit beeper only | Beeper + **AY-3-8912 PSG** | Beeper + AY-3-8912 PSG |
| ROM | 16 KB | 32 KB (two 16 KB pages) | 64 KB (four 16 KB pages) |
| Boot | Direct to BASIC cursor | **Menu-driven** (128 BASIC / 48 BASIC / Tape Loader / Calculator / Tape Tester) | Menu-driven with disk options |
| Editor | Per-line, single line at a time | **Full-screen editor** in a 4-line window at the bottom of the screen | Full-screen editor |
| Storage | Tape only | Tape + RS-232 (optional) | **3" floppy disk** + tape |
| New BASIC statements | — | `PLAY` | `PLAY` + DOS commands |

The 128K ROM pages between two 16 KB ROM pages (ROM 0 and ROM 1) on the fly. ROM 0 contains the editor, menu, and `PLAY` handler. ROM 1 is essentially the 48K ROM, used when running 48K-mode software. The page swap is invisible to the BASIC programmer except insofar as the boot menu and `PLAY` are concerned.

The AY-3-8912 is a **3-channel PSG** (Programmable Sound Generator) with a built-in envelope generator and a noise generator. It is dramatically more capable than the 1-bit beeper of the 48K: three independent voices, volume control per channel, frequency control per channel, white-noise percussion, and an envelope generator for tremolo/decay effects. From assembly language, it is programmed by writing to two I/O ports (`#FFFD` to select a register, `#BFFFD` to write a value). From BASIC, it is programmed **only** through the `PLAY` command — there is no direct chip-register access from BASIC.

---

## The New Editor

The most user-visible change in 128K BASIC is the editor. The 48K editor is per-line: you type a line, press ENTER, and it is committed to the program. Editing an existing line requires bringing it into the edit buffer with `EDIT` (Caps Shift + 1) and re-typing portions of it. The 128K editor is **full-screen** — you can move the cursor anywhere on the visible screen and edit any line in place.

### The 4-Line Edit Buffer

When the 128K boots into 128 BASIC mode, the screen shows the standard `(C) 1986 Sinclair Research Ltd` banner, the current line counter, and a flashing K cursor — but **below** the main screen area, there is a 4-line edit buffer at the bottom (the bottom two lines of the screen, just above the cursor). This buffer is where the user types and edits BASIC lines.

The buffer supports:

- **Cursor movement** — arrow keys move the cursor within the buffer
- **Insert/overwrite** — press `Caps Shift` + `0` to toggle insert mode (a flashing cursor appears)
- **Line editing** — modify any portion of the line in the buffer
- **ENTER** commits the buffer as a new line or as an edit of an existing line

This is a substantial improvement over the 48K editor, which has no concept of an "edit buffer" beyond the single line currently being typed.

### The Boot Menu

When the 128K is reset (or powered on), instead of going directly to the BASIC cursor, the ROM displays a menu:

| Option | Function |
|---|---|
| **128 BASIC** | Enter 128K BASIC mode (with `PLAY`, full-screen editor) |
| **48 BASIC** | Enter 48K BASIC compatibility mode (no `PLAY`, per-line editor) |
| **Tape Loader** | Load a program from tape with no further user interaction |
| **Calculator** | A simple calculator mode (executes single BASIC expressions immediately) |
| **Tape Tester** | Play a tape to verify its quality (level meter) |

The +2A/+3 adds a "64 BASIC" option (for +2A/+3-specific 64 KB banked mode) and disk options.

The Calculator mode is a curious addition: it allows the user to type a single BASIC expression like `2 + 2 * SIN(0.5)` and get the result immediately, without typing a line number or pressing ENTER to commit a program line. It is the spiritual ancestor of the modern calculator app.

### Compatibility With 48K Programs

When the user selects **48 BASIC** from the menu, the 128K pages in ROM 1 (which is essentially the 48K ROM) and runs in a strict 48K-compatible mode: `PLAY` is not available, the editor is per-line, and the AY-3-8912 is not directly accessible. This is how the 128K runs the vast majority of existing Spectrum software, which was written for the 48K.

The 128K mode can also load and run most 48K programs — the token table is auto-converted on load. However, programs that peek at the BASIC area or rely on the 48K token byte values will not work correctly in 128K mode (see [Token Table Differences](#token-table-differences) below).

---

## The PLAY Command

`PLAY` is the headline new feature of 128K BASIC. It drives the AY-3-8912 PSG and supports up to **three simultaneous voices** plus a noise channel, all controlled through a string-based mini-language.

```basic
PLAY a$                        : REM play one string on channel A
PLAY a$, b$                    : REM play two strings on channels A and B
PLAY a$, b$, c$                : REM play three strings on channels A, B, and C
```

Each argument is a string variable (or string literal) that contains a **music program** — a sequence of single-character commands that specify notes, durations, octaves, volumes, effects, tempo, repeats, and channel modes. All three strings execute **simultaneously**, allowing chords, bass-and-melody layering, and percussion alongside music.

`PLAY` is **non-blocking**: it sets up the music and returns control to BASIC. The ROM's interrupt handler (running at ~50 Hz) continues to update the AY registers in the background while the BASIC program does other work. This is the inverse of `BEEP`, which blocks the CPU for the entire note duration.

### Note Names

Within a PLAY string, individual notes are specified with letters:

| Letter | Note |
|---|---|
| `c`, `d`, `e`, `f`, `g`, `a`, `b` | C, D, E, F, G, A, B in the **current octave** |
| `C`, `D`, `E`, `F`, `G`, `A`, `B` | C, D, E, F, G, A, B in the **octave above** the current one |

So the ascending C-major scale across two octaves is:

```basic
PLAY "cdefgabC"
```

This plays seven notes in the current octave (lowercase `c` through `b`), then a high C (uppercase `C` = one octave up). To extend into higher octaves, use the `O` command (below) to change the current octave.

### Accidentals (Sharps and Flats)

Sharps and flats are written **before** the affected note:

- `#c` — C sharp
- `$b` — B flat
- `##c` — C double sharp (equivalent to D natural)
- `$$c` — C double flat (equivalent to B natural — same octave)

To play a descending C-minor scale:

```basic
PLAY "cd$efg$a$bC"
```

(Here `$e`, `$a`, `$b` flatten the E, A, and B to produce the minor third, minor sixth, and minor seventh.)

### Octave (`O`)

The current octave is set with `O` followed by a number from 0 to 8. The default is `O5` (roughly the octave containing middle C). Octave changes affect all subsequent notes until the next `O` command.

```basic
PLAY "O4cdeO5cdeO6cde"     : REM ascending scale across three octaves
```

The uppercase note letters (`C`, `D`, etc.) always refer to **one octave above** the current `O` setting — they do not change the current octave.

### Note Length

The duration of a note is set by a digit from 1 to 9 placed **before** the note. The duration applies to all subsequent notes and rests until changed. The default is `5` (quarter note).

| Digit | Note length |
|---|---|
| 1 | Whole note |
| 2 | Half note |
| 3 | Quarter-note triplet (1/3 of a beat) |
| 4 | Quarter note |
| 5 | Default (same as 4 — quarter note) |
| 6 | Eighth note |
| 8 | Sixteenth note |
| 9 | Thirty-second note |
| 10–12 | Triplets (special — see below) |

For triplet timings, use digits 10, 11, or 12. These set the length of the immediately following notes to triplet values without affecting the established duration of subsequent notes.

```basic
PLAY "5cde4fgab"            : REM quarter notes C-D-E, then eighth notes... wait, 4 is shorter
PLAY "3fed&11fed&fed"       : REM triplets interleaved with regular notes
```

The `&` character denotes a **rest** (silence for the current note duration). So `5c&d` plays C for a quarter note, rests for a quarter note, then plays D for a quarter note.

### Volume (`V`)

Per-channel volume is set with `V` followed by a number from 0 (silence) to 15 (maximum). The default is 15.

```basic
PLAY "V8cdeV15fgab"         : REM play at half volume, then full volume
```

Volume changes affect only the channel they appear in. The three channels are independent.

### Volume Effects (`W`, `U`, `X`)

The AY-3-8912 has a built-in **envelope generator** that can produce volume sweeps — decay, attack, sawtooth waves, etc. This is controlled in PLAY strings with three commands:

| Command | Function |
|---|---|
| `W` | Select envelope waveform (0–7). Default is 0 (no envelope). |
| `U` | Enable the envelope effect on subsequent notes in this string. |
| `X` | Set envelope duration (0–65535, in 1/50ths of a second). |

The eight envelope shapes (W0–W7):

| W | Shape |
|---|---|
| 0 | Envelope off (fixed volume) |
| 1 | Single decay (sawtooth down) |
| 2 | Single attack (sawtooth up) |
| 3 | Single decay then attack (triangle) |
| 4 | Repeating decay (multiple sawtooth down) |
| 5 | Repeating attack (multiple sawtooth up) |
| 6 | Repeating decay-attack (triangle wave) |
| 7 | Repeating attack-decay (inverted triangle) |

```basic
10 LET a$ = "UW1X1000cdefgabC"   : REM ascending scale with decay envelope
20 PLAY a$
```

This plays each note with a 1-second decay envelope (the note starts at full volume and fades to silence over ~1 second). The `U` command enables the envelope; `W1` selects single-decay shape; `X1000` sets the envelope duration to 1000/50 = 20 seconds (the envelope period).

> [!IMPORTANT]
> The AY-3-8912 has only **one envelope generator**, shared across all three channels. If you set an envelope in channel A, it also affects channels B and C if they have `U` enabled. To use different envelope shapes per channel, you must sequence them (change the envelope between phrases) or use machine code.

### Tempo (`T`)

Tempo applies to the whole PLAY statement, not to individual channels. It is set with `T` followed by a number from 60 (slow) to 240 (fast), in beats per minute. The default is `T120`. The `T` command is **only honored in channel A** — putting it in channel B or C has no effect.

```basic
PLAY "T180cdefgabC"         : REM fast tempo (180 BPM) ascending scale
```

### Channel Mode (`M`)

Each channel can produce either a **tone** ( pitched sound) or **noise** (white noise, used for percussion). The `M` command configures the channel modes with a number from 1 to 63, formed by adding mode codes for each channel:

| Code | Effect |
|---|---|
| 1 | Channel A: tone |
| 2 | Channel A: noise |
| 4 | Channel B: tone |
| 8 | Channel B: noise |
| 16 | Channel C: tone |
| 32 | Channel C: noise |

The default is `M7` (channels A, B, and C all tone: 1 + 4 + 16 = 21... wait, that's wrong). Actually, the binary representation makes more sense:

| Bit | Effect if set |
|---|---|
| 0 (value 1) | Channel A tone enabled |
| 1 (value 2) | Channel B tone enabled |
| 2 (value 4) | Channel C tone enabled |
| 3 (value 8) | Channel A noise enabled |
| 4 (value 16) | Channel B noise enabled |
| 5 (value 32) | Channel C noise enabled |

So `M7` = 1+2+4 = all three channels producing tone. `M56` = 8+16+32 = all three channels producing noise. `M17` = 1+16 = channels A and C producing tone, channel B silent.

To mix tone and noise on the same channel (for snare-drum or gunshot effects), set both bits for that channel. For example, `M9` = 1+8 = channel A producing both tone and noise simultaneously.

> [!NOTE]
> The AY-3-8912 has only **one noise generator**, shared across all channels. So while you can route noise to multiple channels, they all share the same noise frequency. To change the noise frequency, use machine code (the noise period is in register 6 of the AY).

### Repeats (`(` `)`)

A phrase enclosed in parentheses is played **twice**:

```basic
PLAY "(cde)fgh"             : REM plays c-d-e twice, then f-g-h once
```

Parentheses can be nested up to 4 levels deep:

```basic
PLAY "((cd)ef)g"            : REM plays c-d-c-d-e-f-c-d-c-d-e-f-g (the inner repeats, then the outer repeats with the inner repeated again)
```

A closing parenthesis without a matching opening parenthesis causes the entire string to **repeat forever**. This is the standard idiom for a bass line that loops throughout a song:

```basic
10 LET bass$ = "O3cgcg)"      : REM loops c-g-c-g-c-g-... forever
20 LET melody$ = "O5cdefgabCH" : REM plays the melody once, then H stops everything
30 PLAY melody$, bass$
```

The `H` command in the melody string stops the entire PLAY statement (all channels) — without it, the bass would loop forever.

### Comments (`!` `!`)

Text enclosed in `!` characters is ignored:

```basic
PLAY "!Ascending scale:! cdefgabC"
```

If the comment runs to the end of the string, the closing `!` is optional.

### MIDI Support (Channels D–H)

PLAY accepts up to 8 string arguments, but only the first 3 (channels A, B, C) drive the AY-3-8912. Channels D through H are routed to a **MIDI interface** (if one is connected). The `Y` command selects a MIDI channel (1–16) and `Z` sends a raw MIDI byte (0–255). This feature is rarely used — the Spectrum 128 did not ship with MIDI hardware — but the syntax is reserved.

### Worked Example — A Three-Voice Tune

```basic
10 REM Three-voice tune — melody, harmony, bass
20 LET melody$ = "T120 O5 cdefgabC O4 bagfedc H"
30 LET harmony$ = "          O4 egabCDEg fedcbafe H"
40 LET bass$    = "          O3 cgcgcgcg )"          : REM loop bass
50 PLAY melody$, harmony$, bass$
```

The `H` in the melody and harmony strings stops the entire PLAY when both finish. The bass loops (`)`) until then.

### Limitations of PLAY

1. **Single envelope generator** — All three channels share one envelope. If channel A has a decay envelope, channels B and C cannot simultaneously have an attack envelope. To get different effects per channel, you must time-share or use machine code.
2. **Single noise generator** — All channels share one noise source with a fixed frequency. Multiple "drum" sounds must be approximated by toggling the noise enable bit.
3. **Background execution is interrupt-driven** — If your BASIC program disables interrupts (`DI` via USR) or takes too long in a single statement, the music stutters. The interrupt handler needs ~1 ms every 20 ms frame to update the AY registers.
4. **String length limit** — PLAY strings are limited by the maximum string length (roughly 32 KB). For very long pieces, use the repeat feature (`)`) or split into multiple PLAY calls.
5. **No direct register access** — PLAY provides a high-level musical interface but no way to set AY registers directly from BASIC. For sample playback, custom envelopes, or specialized effects, you must use machine code (see [ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md)).

---

## AY-3-8912 Access From BASIC

The AY-3-8912 has 16 internal registers, each controlling one aspect of the sound (tone period, volume, envelope shape, noise period, I/O port). To read or write a register from machine code:

```
OUT (#FFFD), register_number   ; select register (port #FFFD = 65533)
OUT (#BFFFD), value             ; write value (port #BFFFD = 49149)
LET A = IN (#FFFD)              ; read currently selected register
```

Sinclair BASIC **does** have `OUT` and `IN` keywords (statements/functions for I/O port access), so you can write directly to the AY registers from BASIC:

```basic
10 OUT 65533, 7    : REM select AY register 7 (channel enable / I/O port)
20 OUT 49149, 62   : REM write 62 = binary 00111110 (channels A,B,C tone enabled, noise disabled)
30 OUT 65533, 0    : REM select register 0 (channel A tone period, low byte)
40 OUT 49149, 100  : REM set channel A period to 100 (high byte assumed 0)
50 OUT 65533, 8    : REM select register 8 (channel A volume)
60 OUT 49149, 15   : REM set channel A volume to maximum (15)
```

This produces a steady tone on channel A. The frequency is determined by the formula:

```
frequency = clock_hz / (16 × period)
```

Where `clock_hz` is the AY-3-8912's clock (1.7734 MHz on the 128K Spectrum, derived from the CPU clock divided by 16). A period of 100 gives a frequency of approximately 1108 Hz.

> [!WARNING]
> Direct register access from BASIC is **slow** — each `OUT` takes ~5 ms (the BASIC interpreter overhead). To change 14 registers (a full envelope update), that's ~70 ms, far too slow for real-time music. For real-time AY control, use machine code via `USR`. Direct register writes from BASIC are useful for **static setups** (configuring the chip once at program start) but not for live music.

For the complete AY-3-8912 register map, see [ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md).

---

## +2A and +3 Disk Commands

The +2A and +3 models ship with a 64 KB ROM organized as four 16 KB pages. The added disk commands extend the existing `LOAD`, `SAVE`, and `VERIFY` keywords and add new RSX-style commands (technically typed with a `#` prefix or as extensions to existing keywords):

| Command | Function |
|---|---|
| `CAT` | Display the directory of the disk in drive M: |
| `FORMAT` | Format a disk (interactive prompts for disk name and options) |
| `ERASE "filename"` | Delete a file |
| `MOVE "src", "dst"` | Rename a file |
| `OPEN #stream, "filename"` | Open a file stream for sequential I/O |
| `CLOSE #stream` | Close a file stream |
| `LOAD "filename" CODE addr, len` | Load a code block from disk |
| `SAVE "filename" CODE addr, len` | Save a code block to disk |
| `MERGE "filename"` | Merge a BASIC program from disk |
| `VERIFY "filename"` | Verify a saved block against memory |

### Loading From Disk

```basic
LOAD "game"            : REM loads BASIC program "game" from disk
LOAD "game" CODE 30000 : REM loads code block "game" to address 30000
CAT                    : REM lists the disk directory
```

The disk interface is via +3DOS, which is built on top of CP/M's BDOS layer. Disks are 3" floppy disks (178 KB per side, single-sided by default). The +3 could read +D, DID, and Opus Discovery disk formats with appropriate software.

### Compatibility Notes

- The +2A/+3 cannot run some 48K software that uses the #FFFD port or assumes specific contention patterns. The +2A/+3 has different memory contention than the 128K/+2 (grey) — see [contention_model.md](../03_memory_and_io/contention_model.md).
- Programs that page ROM 1 in via #7FFD must use the correct paging sequence (the #1FFD port also exists on +2A/+3 and controls the 4 paging modes).
- The +3's disk operating system uses the same hook codes as the +2A but adds disk-specific RSX commands.

For more on the +2A/+3 paging modes (128K compat, all-RAM 0–3, all-RAM 4–7, Plus 3), see [memory_and_io_plus3.md](../03_memory_and_io/memory_and_io_plus3.md).

---

## Token Table Differences

The 128K ROM uses a **different token table** from the 48K ROM. The single-byte codes for keywords are mostly the same, but `PLAY` is a new token, and several other tokens are shifted to accommodate it. This means that a BASIC program saved on a 48K Spectrum and loaded into a 128K Spectrum in 128K mode will be **re-tokenized on load** — the ROM detects the old token set and converts it.

This is normally transparent to the user — the program runs identically. But it matters when:

1. **Inspecting the PROG area in memory** — the byte values for keywords will differ between a 48K-saved and a 128K-saved version of the same program.
2. **POKE-driven line manipulation** — code that uses `POKE` to modify the token bytes of a program line will produce different results on 48K vs 128K.
3. **Machine code that calls ROM routines** — the addresses of the parser, tokenizer, and command dispatch routines are different in the 128K ROM. Programs that hardcode ROM addresses (e.g., `RST #10` for PRINT) will work because the RST vectors are the same, but programs that call subroutines by absolute address (e.g., `CALL #0C0A`) may break.

The +2A/+3 token table is yet another variation — it adds tokens for the disk commands. Programs written for the 48K that include disk operations on the +3 will have different byte values for `LOAD`, `SAVE`, etc.

For the full byte-level token table for all three ROMs (48K, 128K, +2A/+3), see [basic_token_table.md](../../10_references/basic_token_table.md).

---

## Memory Paging and BANK

The 128K has 128 KB of RAM organized as 8 banks of 16 KB. The bottom 16 KB (`#0000`–`#3FFF`) is always bank 0 (or the ROM). The top 16 KB (`#C000`–`#FFFF`) can be paged to any of the 8 banks via the `#7FFD` port.

From BASIC, there is **no direct paging command** in the 128K ROM. The paging port is written from machine code:

```asm
LD  A, bank_number     ; 0-7
OR  banking_bits       ; bit 3 = screen (0=normal, 1=shadow), bit 4 = ROM (0=1, 1=0)
LD  BC, #7FFD
OUT (C), A
```

However, some later BASIC dialects (notably SE BASIC, OpenSE, and NextBASIC) add a `BANK` keyword for explicit paging. The 128K ROM's only concession to banking is the **RAM disk** — a portion of the upper banks is reserved for storing code blocks that can be quickly paged in and out.

### The RAM Disk

The 128K ROM provides a RAM disk that uses banks 5, 2, and 0 of RAM (the banks not used by the screen, system variables, or the lower RAM). This gives roughly 48 KB of high-speed "disk" storage. The RAM disk is accessed via the standard `LOAD`/`SAVE` commands with the device prefix `M:`:

```basic
SAVE *"m"; CODE 30000, 1000     : REM save 1000 bytes to RAM disk
LOAD *"m"; CODE 30000           : REM load from RAM disk back to address 30000
```

The RAM disk is volatile — its contents are lost when the machine is reset or powered off. It is primarily used for fast loading during gameplay (e.g., loading the next level while the player is still playing the current one) and for holding frequently-accessed data tables.

For the complete 128K memory map and paging details, see [memory_and_io_128k.md](../03_memory_and_io/memory_and_io_128k.md).

---

## Worked Example — Background Music and Foreground Action

Here is a complete 128K BASIC program that plays background music while displaying a moving pattern on the screen. This is impossible on a 48K (where `BEEP` blocks execution), but trivial with `PLAY`'s non-blocking design:

```basic
10 REM Background music + foreground animation
20 LET melody$ = "T120 O5 (cdef)gbfedc H"
30 LET bass$ = "O3 (cgcg)"
40 PLAY melody$, bass$       : REM starts music in background
50 REM Animation loop — runs while music plays
60 FOR X = 0 TO 255
70   PLOT X, 87 + 50 * SIN (X / 20)
80   PLOT OVER 1; X - 1, 87 + 50 * SIN ((X - 1) / 20)
90 NEXT X
100 GO TO 60                   : REM loop animation until music ends
```

When the `H` in the melody string executes, the entire PLAY statement stops. The animation loop continues until the user presses BREAK.

> [!NOTE]
> The music's quality depends on the BASIC program not blocking the CPU for too long. Long-running statements (like the inner loop above) are fine because they yield to the interrupt handler between iterations. But a single long-running machine code call (via USR) that disables interrupts will cause the music to stutter.

---

## Common Pitfalls

### 1. PLAY Token Not Recognized in 48K Mode

If the user selects **48 BASIC** from the 128K boot menu, `PLAY` is not available — attempting to use it produces `Nonsense in BASIC` or a similar error. To use `PLAY`, you must be in **128 BASIC** mode.

### 2. Different Token Tables Break Binary Inspection

A 48K BASIC program saved with `SAVE "X" LINE 0` and loaded into a 128K Spectrum in 128K mode will have its tokens re-encoded. Code that relies on specific token byte values (e.g., for copy protection or self-modifying line editing) will not work.

### 3. Envelope Generator Is Shared

The single envelope generator on the AY-3-8912 cannot produce different envelope shapes simultaneously on different channels. Setting `W1` (decay) on channel A affects channels B and C if they have `U` enabled. To get independent envelopes, sequence them or use machine code.

### 4. Background Music Requires Interrupts

PLAY's non-blocking behavior depends on the 50 Hz interrupt handler. If your program disables interrupts (`DI` via USR) for more than ~20 ms, the music will skip or stop. Always re-enable interrupts (`EI`) before returning to BASIC.

### 5. OUT to AY Registers Is Slow

Each `OUT` from BASIC takes ~5 ms. A full AY register update (14 registers) takes ~70 ms — too slow for real-time music. Use machine code (`LDIR` to a register table, then a tight `OTIR` loop) for real-time control.

### 6. Shadow Screen vs Main Screen

Paging bank 7 into the screen area (`#4000`–`#7FFF`) via #7FFD bit 3 selects the **shadow screen**. PRINT writes go to whichever screen is currently paged; the ULA displays whichever screen the #7FFD bit 3 selects. This enables double-buffered animation (write to shadow, flip, repeat) but is invisible to a BASIC program unless it explicitly pages.

---

## Cross-References

- [Sinclair BASIC 48K comprehensive reference](basic_48k.md) — tokens, syntax, variables, floating-point format, calculator stack, parser, PLOT/DRAW/CIRCLE, BEEP, PEEK/POKE/USR
- [AY-3-8912 PSG](../../06_sound/hardware/ay_3_8912.md) — complete sound chip register map, programming model, envelope generator, noise generator
- [Beeper synthesis](../../06_sound/synthesis/beeper_synthesis.md) — the 1-bit beeper hardware (still available on 128K for compatibility)
- [Memory maps 128K](../03_memory_and_io/memory_and_io_128k.md) — 8-bank RAM layout, #7FFD paging port, shadow screen
- [Memory maps +2A/+3](../03_memory_and_io/memory_and_io_plus3.md) — #1FFD port, 4 paging modes, +3 FDC
- [Contention model](../03_memory_and_io/contention_model.md) — per-model timing differences (48K vs 128K vs +2A/+3 vs Pentagon)
- [Video frame 128K](../05_display_and_timing/video_frame_128k.md) — odd-bank contention, shadow screen, floating bus differences
- [Basic token table](../../10_references/basic_token_table.md) — byte-level token values for 48K, 128K, and +2A/+3 ROMs
- [ROM 128K internals](../../04_operating_systems/rom_128k.md) — dual-ROM architecture, ROM call bridge, ROM swap calling convention
- [ROM +2A/+3 internals](../../04_operating_systems/rom_plus2.md) — four-page ROM, paging modes, CP/M boot, +3 DOS integration
- [Basic dialects comparison](../../04_operating_systems/basic_dialects.md) — variants: 48K, 128K, +2/+2A/+3, QL SuperBASIC, SE BASIC, NextBASIC

---

## References

- **Sinclair ZX Spectrum 128 Introduction** (1986) — the official manual covering the boot menu, 128 BASIC editor, and PLAY command syntax
- **Sinclair ZX Spectrum +2 Manual** (1986) — same content as the 128 manual with +2-specific hardware notes
- **Sinclair ZX Spectrum +3 Manual** (1987) — adds the +3 DOS commands and disk operation details. Available online: https://zxspectrumvault.github.io/Manuals/Hardware/SpectrumPlus3Manual.html
- **The Complete SPECTRUM 128 ROM Disassembly** (Matthew Wilson) — the definitive reference for the 128K ROM 0 internals, including the PLAY handler routines. Available online: http://www.matthew-wilson.net/spectrum/rom/128_ROM0.pdf
- **ZX Forum #04 — "World of Sound: The PLAY operator for AY-3-8910"** — detailed coverage of the PLAY mini-language with worked examples. Available online: https://www.zxpress.ru/eng/ezines/zx-forum/04/play-operator-for-ay-3-8910-sound-processor-in-zx-spectrum-128-syntax-commands-for-note-playback
- **World of Spectrum — ZX Spectrum 128 Manual Page 10** — the canonical PLAY command summary table. Available online: https://worldofspectrum.org/ZXSpectrum128Manual/sp128p10.html
- **Alessandro Grussu's Spectrumpedia** — comprehensive coverage of all 128K-family BASIC dialects and their differences
