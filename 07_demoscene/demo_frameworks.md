[← Home](../README.md) · [Demoscene](README.md)

# Demo Frameworks — Effect Sequencing and Music Sync

> **Scope**: This article covers the **runtime architecture of a ZX Spectrum demo** — the code that decides which effect runs when, how transitions between effects are handled, how music is kept in sync with visuals, and how memory is managed across a multi-part production. It is the practical companion to [effects_catalog.md](effects_catalog.md) (which catalogs the effects themselves), [compression_packing.md](compression_packing.md) (which provides the depackers frameworks call), [multicolor_techniques.md](multicolor_techniques.md) (whose engines a framework must schedule around the ISR), and [notable_demos.md](notable_demos.md) (which catalogs the demos built on these frameworks).
>
> The article is descriptive rather than tutorial: it explains what a framework is responsible for, what design choices exist, and what trade-offs each choice implies. Working source code for specific frameworks is out of scope; refer to the source releases of the demos cited in [notable_demos.md](notable_demos.md).

---

## Article Roadmap

- §1 — What a framework does: the five core responsibilities.
- §2 — Demo structure: intro → parts → credits, the linear timeline.
- §3 — Effect sequencing: event-list, script-driven, hardcoded.
- §4 — Music synchronisation: reading the player's position counter.
- §5 — Memory layout: 48K flat, 128K banked, Pentagon with RAM-disc.
- §6 — ISR architecture: single ISR, split timing, multi-rate scheduling.
- §7 — Part transitions: crossfades, blank-frame swaps, gradual load.
- §8 — Notable frameworks: Soviet, Western, and modern engines.
- §9 — ZX Spectrum Next and modern hardware considerations.
- §10 — Cross-references.

---

## 1. What a Framework Does

A **demo framework** is the orchestration layer that sits between the hardware and the individual effects. A single effect — plasma, tunnel, raster bars — runs in isolation and produces visuals. A framework lets the demoscener **sequence multiple effects into a multi-minute production** with music, transitions, and resource management.

Without a framework, a demo is a single effect running forever (the 256-byte intro model — see [size_coding.md](size_coding.md)). With a framework, a demo is a **narrative**: an intro, a sequence of distinct parts, and a credits screen, all set to a piece of music that drives the timing.

### 1.1 The Five Core Responsibilities

Every non-trivial Spectrum demo framework handles five things:

1. **Effect sequencing** — deciding which effect runs at time *T*, when it ends, and which effect runs next. §3.
2. **Music synchronisation** — ensuring visual events (transitions, palette changes, effect swaps) happen at specific points in the music. §4.
3. **Memory management** — loading effect code and data from disk or banked ROM, decompressing on the fly, and freeing memory when an effect ends. §5.
4. **Interrupt architecture** — running the music player, the effect's per-frame code, and (for multicolor) the raster-synchronous rewrite from a single interrupt service routine or a small set of cooperating routines. §6.
5. **Part transitions** — moving from one effect to the next without visible glitches: crossfades, blank-frame swaps, gradual loads. §7.

A small Spectrum demo (e.g. a 4K intro) may handle all five in as little as 200 bytes of code. A large megademo (e.g. a 32K Pentagon demo with TS-Config streaming) may have a 4 KB framework that handles disk streaming, banked memory, software sprites, and per-frame scripting.

### 1.2 The Audience for This Article

Three groups benefit from understanding demo frameworks:

- **Demo authors**: anyone planning to build a multi-part demo needs a framework, even if they write it themselves from scratch.
- **Demo reverse-engineers**: when reading a disassembly of a demo, the framework is the first thing to identify — once the framework is understood, individual effects are easy to extract and study.
- **Effect authors**: an effect that cannot be plugged into a framework (e.g. one that hogs all RAM, or that doesn't follow the per-frame contract) is much less useful than one that fits.

The article does not assume the reader is writing a framework from scratch — most demo authors reuse an existing framework. But the conceptual model is needed to choose a framework, extend one, or debug a demo that uses one.

### 1.3 Frameworks vs Effect Libraries

There is a clear separation between **frameworks** (this article) and **effect libraries** ([effects_catalog.md](effects_catalog.md)):

| Aspect | Framework | Effect library |
|---|---|---|
| Responsibility | Sequencing, sync, memory, transitions | Single visual effect per file |
| Lifetime | Runs for the entire demo | Runs for one part, then exits |
| Memory ownership | Manages all RAM | Borrows RAM from framework |
| Calls into player | Yes (per-frame) | No (called by framework) |
| Visible to viewer | No (invisible orchestration) | Yes (the actual visuals) |

A well-designed framework treats effects as **plugins**: each effect exposes a small interface (init, per-frame, exit) and the framework calls them in order. Effects that don't follow the contract are hard to integrate.

---

## 2. Demo Structure — The Linear Timeline

Almost every ZX Spectrum demo follows the same **linear timeline**:

```
[intro screen] → [part 1] → [part 2] → ... → [part N] → [credits] → [greet screen]
```

There are rare exceptions — interactive demos, branched demos, "choose-your-own" demos — but these are curiosities. The linear timeline dominates because it matches the linear nature of music: a 3-minute PT3 module plays from start to finish, and the visuals must synchronize to it.

### 2.1 The Intro Screen

The intro screen is the **first thing the viewer sees** when the demo runs. It typically contains:

- The demo's title (large font, often with effect-overlay).
- The group's logo or name.
- A "press space to start" prompt or a short delay timer.
- Optional: hardware requirements (e.g. "128K ONLY"), greeting text, or a copyright line.

The intro screen is the only part of the demo that is **explicitly user-paced**: most demos wait for a key press before starting the music and the parts sequence. Some demos auto-start after a fixed delay (typically 5–10 seconds) to allow unattended playback at parties.

### 2.2 Parts

A **part** is a single effect (or a tightly-coupled set of effects) running for a defined duration. A typical part lasts:

- **8–20 seconds** for a fast-paced megademo.
- **30–60 seconds** for a "cinematic" demo with long fades.
- **60–120 seconds** for a music-driven demo where each part corresponds to a section of the music.

A part is defined by:

- **Effect code**: the actual visuals — plasma, tunnel, 3D scene, multicolor rewrite, etc.
- **Effect data**: precomputed tables, palette definitions, screen layout.
- **Music position range**: the part starts at music-position *M_start* and ends at *M_end*.
- **Transition in**: how the part appears (fade from black, hard cut, scroll in).
- **Transition out**: how the part exits (fade to black, hard cut to next part).

The framework's job is to call the effect's init routine at *M_start*, run its per-frame routine every frame until *M_end*, then call its exit routine and start the next part.

### 2.3 The Credits and Greet Screens

The credits screen lists:

- Code, graphics, music credits for each contributor.
- The group's name and any sub-groups.
- Greetings to other groups (the "greet list").
- Hardware used, tools used, party thanks.

The greet screen is often the **last thing** the viewer sees — a static screen that lingers indefinitely, or a scroll that runs until the viewer resets the machine. Some demos loop back to the intro screen after a delay; most do not.

### 2.4 The Timeline Table

A framework typically encodes the timeline as a **static table**:

```
PART_TABLE:
    DEFW plasma_init, plasma_frame, plasma_exit, 0x0000, 0x0100  ; part 1: positions 0-256
    DEFW tunnel_init, tunnel_frame, tunnel_exit, 0x0100, 0x0240  ; part 2: positions 256-576
    DEFW cube3d_init, cube3d_frame, cube3d_exit,   0x0240, 0x03C0  ; part 3: positions 576-960
    ...
    DEFW 0,0,0,0xFFFF,0xFFFF  ; end-of-demo marker
```

Each row contains:
- A pointer to the part's `init` routine.
- A pointer to the part's `frame` routine (called per video frame).
- A pointer to the part's `exit` routine.
- The music position at which the part starts.
- The music position at which the part ends.

The framework's main loop walks this table, advancing to the next row when the music position counter reaches the end of the current part. This is the **simplest possible** framework; most production frameworks add scripting, conditional branches, and per-frame event triggers on top.

### 2.5 Total Demo Duration

Spectrum demos are typically **3–10 minutes** long:

- **3 minutes**: the lower bound for a party-quality demo. Shorter feels incomplete.
- **5 minutes**: the sweet spot. Long enough to show 6–10 distinct parts with transitions; short enough to keep the viewer's attention.
- **10 minutes**: the upper bound. Demos this long risk boring the viewer unless the parts are exceptionally varied.
- **15+ minutes**: rare, and usually only seen in megademos where each part is essentially a self-contained mini-demo.

The duration is determined primarily by the **music**: the demo ends when the music ends. A framework typically runs the parts table to completion and then idles on the credits screen while the music's final note fades.

---

## 3. Effect Sequencing Patterns

The simplest sequencing decision in a framework is **"when does this part start, and when does it end?"**. The answer can be encoded in three main ways, each with different trade-offs in code size, flexibility, and authoring effort.

### 3.1 Hardcoded Sequence

The simplest framework has **no table at all** — the sequence of effects is hardcoded into the main loop:

```z80
main_loop:
    CALL wait_for_key
    CALL music_start
    CALL plasma_init
    CALL run_plasma_until_music_pos_256
    CALL plasma_exit
    CALL tunnel_init
    CALL run_tunnel_until_music_pos_576
    CALL tunnel_exit
    CALL cube3d_init
    CALL run_cube3d_until_end
    CALL cube3d_exit
    CALL credits_screen
    RET
```

This is the **only** sequencing style used in 4K intros and below — there is no room for a table parser. The "until music position X" wrappers each contain a tight loop comparing the music position counter to the end position.

Advantages:
- **Smallest code** — no table parser, no indirect calls.
- **Fastest** — direct `CALL` is faster than table dispatch.
- **Easiest to debug** — the entire sequence is visible in the source.

Disadvantages:
- **No runtime flexibility** — to change the sequence, you must reassemble.
- **No scripting** — adding a palette change at music position 240 requires hand-editing the relevant `run_*_until` routine.
- **No reordering** — swapping two parts means moving code blocks, which can break address-dependent calculations.

This style dominates below 16K. It is rare in larger demos.

### 3.2 The Event List (Table-Driven)

A table-driven framework stores the timeline as a static list of events. Each event has a **trigger condition** (a music position, a frame count, or a key press) and an **action** (call an init routine, change a palette, start a transition, etc.).

```
EVENT_LIST:
    DEFW 0x0000, EVENT_START_MUSIC      ; position 0
    DEFW 0x0000, EVENT_CALL_PART_PLASMA  ; position 0
    DEFW 0x0100, EVENT_END_PART          ; position 256
    DEFW 0x0100, EVENT_CALL_PART_TUNNEL  ; position 256
    DEFW 0x0180, EVENT_FADE_TO_BLACK     ; position 384
    DEFW 0x0240, EVENT_END_PART          ; position 576
    DEFW 0x0240, EVENT_CALL_PART_CUBE3D  ; position 576
    ...
    DEFW 0xFFFF, EVENT_END_DEMO          ; sentinel
```

The framework's main loop scans this table each frame and fires any event whose trigger condition is met. Each event handler is a small routine that performs its action and returns.

Advantages:
- **Reorderable**: the table can be edited without touching code.
- **Multiple simultaneous events**: two events at the same music position both fire — useful for "start music AND start effect" at position 0.
- **Trivial to author**: writing the table is much faster than writing the equivalent hardcoded sequence.

Disadvantages:
- **Larger code** than hardcoded: the table parser adds ~50–100 bytes.
- **Slower per frame**: the parser must scan the table every frame, even when no events fire.
- **No conditionals**: events fire when their position is reached, full stop. Branching requires multiple tables or extended event types.

This style dominates 16K–48K demos.

### 3.3 Script-Driven (Bytecode Interpreter)

The most sophisticated framework style uses a small **bytecode interpreter** that executes a "demo script" stored in RAM. The script language has commands like `CALL_EFFECT`, `WAIT_MUSIC_POS`, `FADE`, `LOAD_BANK`, `SET_PALETTE`, etc.

```
script:
    BYTE CMD_START_MUSIC, 0             ; start music at position 0
    BYTE CMD_CALL_EFFECT, EFFECT_PLASMA
    BYTE CMD_WAIT_MUSIC_POS, 0x00, 0x01 ; wait for position 256
    BYTE CMD_FADE_OUT, 30               ; fade out over 30 frames
    BYTE CMD_CALL_EFFECT, EFFECT_TUNNEL
    BYTE CMD_FADE_IN, 30
    ...
    BYTE CMD_END
```

The interpreter walks the script byte by byte, executing each command and advancing. Some commands block (e.g. `CMD_WAIT_MUSIC_POS`); others return immediately (e.g. `CMD_CALL_EFFECT`).

Advantages:
- **Maximum flexibility** — complex sequences with branches, loops, and conditionals are possible.
- **Compact storage** — the script is smaller than the equivalent event list because each command is one or two bytes.
- **Author-friendly** — scripts can be edited without recompiling the framework, allowing rapid iteration.

Disadvantages:
- **Largest framework code** — the interpreter itself is ~500–1000 bytes.
- **Slowest per command** — each command goes through a dispatch table.
- **Hardest to debug** — a script bug can crash the interpreter in ways that are not obvious from the script source.

This style is found in large Pentagon/TS-Config demos (1998–present) and in most post-2010 Western demos.

### 3.4 Sequencing Triggers — Music vs Frame vs Wall-Clock

Independently of the encoding (hardcoded, table, script), a framework must choose what **trigger** advances the sequence. Three options:

| Trigger | Source | Resolution | Used for |
|---|---|---|---|
| **Music position** | PT3 player's `Pos` counter | 1/50s at 50 Hz | Most demos — best sync |
| **Frame counter** | incremented per VBLANK INT | 1/50s or 1/60s | Demos with no music; pinball-style demos |
| **Wall-clock** | RTC or keyboard scan timing | seconds | Demos with user-paced sections |

The **music position** is the dominant choice for Spectrum demos because the music is the master clock. The PT3 player maintains a 16-bit `Pos` counter that increments once per "row" of music (typically 1/50s of a second at the default tempo). The framework reads this counter and uses it as the trigger for all events.

The downside: if the music's tempo changes mid-song, the timing of visual events relative to wall-clock time drifts. This is usually acceptable — demos are authored around the music, not the wall-clock — but it can confuse reverse-engineers who expect consistent time intervals.

### 3.5 Multi-Stream Sequencing

A modern framework may run **multiple parallel streams**:

- The **parts stream**: which effect is currently active.
- The **palette stream**: palette changes that occur independently of part changes.
- The **overlay stream**: text overlays, greetings, and logos that appear on top of the current effect.
- The **transition stream**: crossfades and effect swaps that may overlap with the next effect's init.

Each stream has its own event list or script, and the framework dispatches all of them per frame. This is the model used by the most sophisticated Western and post-2010 Russian demos.

### 3.6 Sequencing Failure Modes

Common sequencing bugs:

- **Off-by-one music positions** — the part starts one row too early or too late, causing a visible glitch.
- **Effect init during paper area** — the init routine runs while the raster is in the display area, breaking multicolor timing for the first frame of the new part.
- **Stack overflow** — the framework's nested `CALL`s accumulate on the stack, eventually overwriting data.
- **Event-list scan lag** — the framework's table scan takes too long and the music player misses a frame.
- **Race condition between init and ISR** — the new effect's init routine runs while the ISR is still calling the old effect's per-frame routine.

These are framework-author concerns, but effect authors should be aware that their init and exit routines run in a sensitive context where timing and stack usage matter.

---

## 4. Music Synchronisation

Music is the master clock of nearly every ZX Spectrum demo. Visual events are timed relative to the music's position counter, not to wall-clock time, and the framework's primary job during a part is to **keep visuals in lock-step with the audio**.

### 4.1 The PT3 Position Counter

The dominant AY music format on the Spectrum is **Pro Tracker 3** (PT3), played by the standard PT3 player routine. See [soviet_demo_scene.md](soviet_demo_scene.md) §6 for the history of the format and [../06_sound/players/ay_player_routines.md](../06_sound/players/ay_player_routines.md) for player internals.

The PT3 player maintains several public counters that the framework can read:

| Variable | Size | Purpose |
|---|---|---|
| `Pos` | 16-bit | Current "position" (row counter) in the module, 0..N |
| `Pattern` | 8-bit | Current pattern number being played |
| `Row` | 8-bit | Current row within the pattern (0–63 typically) |
| `Tick` | 8-bit | Sub-row counter (0–Tempo-1) |

The most useful for sync is **`Pos`**, which is a 16-bit running counter that increments by 1 each time the player advances one row. At the default tempo of 6 ticks per row and 50 Hz interrupt rate, `Pos` increments roughly every 1/8.3 seconds (faster at higher tempos).

### 4.2 Reading the Position Counter

The framework reads `Pos` from a known address in the player's data area. The address depends on the player build but is typically a fixed location after the player code.

```z80
; Get current music position into HL
get_music_pos:
    LD   HL,(MUSIC_POS)       ; 3 bytes — read the player's Pos counter
    RET
```

The framework then compares this against the trigger positions stored in the event list:

```z80
; Check if event at position DE should fire
check_event:
    LD   HL,(MUSIC_POS)       ; current position
    AND  A                    ; clear carry
    SBC  HL,DE                ; HL = current - target
    RET  C                    ; not yet
    ; HL >= 0, event fires
    ; ...
```

A subtle issue: reading a 16-bit counter is not atomic on the Z80 — the interrupt can fire between the two byte reads, giving an inconsistent value. The framework must either:
1. **Disable interrupts briefly** around the read (`DI`/`EI`), costing ~3 T-states of interrupt latency.
2. **Read twice and retry** if the two reads disagree.

Most frameworks use option 1, as the latency is negligible compared to the 50 Hz frame budget.

### 4.3 Coarse Sync — Part-Level Triggers

The coarsest level of sync is **part-level**: the framework uses the music position to decide when to start and end parts. The event list (§3.2) or script (§3.3) contains entries like `WAIT_MUSIC_POS 0x0100`, which block the framework until `Pos` reaches the target.

This gives **sub-second** accuracy — at default tempo, one music row is ~120 ms. Two effects that swap at a part boundary will be visually aligned to the music within one row, which is acceptable for almost all transitions.

### 4.4 Fine Sync — Note-Level Triggers

For tighter sync — e.g. firing a flash effect on every bass-drum hit — the framework can read the **`Row` counter** or the AY envelope state. This is more invasive: the framework must know the music's pattern structure or sample the AY chip's register state.

A simpler approach uses **hand-crafted markers** in the music itself. The composer places a specific note or effect in a channel at the moment the visual event should fire; the framework watches for that note. PT3 supports "sample changes" and "ornament changes" that can serve as out-of-band signals.

The most robust fine-sync technique is **direct AY register polling**: the framework reads AY register 0–7 (the channel periods and envelopes) and triggers visual events when the values cross thresholds. This requires no cooperation from the music data but is fragile — changes to the music's mix can break the triggers.

### 4.5 Visual Events Triggered by Music

Common visual events tied to music:

- **Bass-drum flash** — when the AY envelope's period crosses a threshold, the framework briefly brightens the screen.
- **Snare/tick jitter** — a small offset is added to all rotating objects, producing a "shake" effect on each beat.
- **Pattern change palette swap** — when `Pattern` increments, the framework swaps the active palette.
- **Tempo-based effect rate** — a plasma's `time` variable is incremented in step with the music, not the frame counter, so the effect speeds up and slows down with the music.

### 4.6 Synchronisation Pitfalls

#### Variable Tempo

PT3 modules can change tempo mid-song (using the `Tempo` ornament). The framework's event list, if expressed in music positions, is unaffected — but if expressed in frames or wall-clock, will drift. **Always use music positions for triggers** when the music has variable tempo.

#### Player Jitter

The PT3 player runs once per frame from the ISR. If the framework disables interrupts for longer than one frame (e.g. during a disk load), the player skips calls and the music falls behind. The framework must either:
1. **Avoid long interrupt-disabled sections** during music playback.
2. **Use a separate ISR** for disk I/O that yields to the music ISR periodically.

See §6.5 for split-ISR architectures that solve this.

#### First-Frame Lag

When a part starts at music position *M*, the framework calls the effect's init routine and then runs the per-frame routine. The first frame's per-frame runs at the *next* interrupt, ~20 ms after the init. This means the visual effect lags the music by one frame — usually invisible but sometimes noticeable for sharp transitions.

The fix is to call the per-frame routine **immediately after init**, before returning to the main loop. This costs ~20 ms of CPU time during the transition but eliminates the first-frame lag.

### 4.7 Music as Master Clock

A useful mental model: the **music is the only clock that matters**. Wall-clock time, frame counters, and CPU cycle counts are irrelevant — the viewer perceives the demo through the music's tempo. A demo that drifts relative to wall-clock but stays locked to the music feels correct; a demo that stays locked to wall-clock but drifts from the music feels broken.

This is why music sync is the framework's first priority (§1.1) and why every other timing decision flows from it.

---

## 5. Memory Layout

Spectrum demos run on three distinct memory architectures — the 48K flat model, the 128K banked model, and the Pentagon/TR-DOS model with RAM-disc — and a framework must understand all three if the demo is to be portable across them.

### 5.1 The 48K Memory Map

The 48K Spectrum has 16 KB of ROM at `#0000`–`#3FFF` and 48 KB of RAM at `#4000`–`#FFFF`. The RAM is split into two regions with different performance characteristics:

| Region | Address | Size | Contended? | Use |
|---|---|---|---|---|
| Screen pixel data | `#4000`–`#57FF` | 6 KB | **Yes** (during paper area) | Display file |
| Screen attributes | `#5800`–`#5AFF` | 768 B | **Yes** | Attribute file |
| Printer buffer | `#5B00`–`#5BFF` | 256 B | **Yes** | Reused by framework |
| System variables | `#5C00`–`#5CBF` | 192 B | **Yes** | ROM state (mostly unused by demo) |
| Free RAM (lower) | `#5CC0`–`#7FFF` | ~9 KB | **Yes** | Effect data, small tables |
| Free RAM (upper) | `#8000`–`#FFFF` | 32 KB | **No** | Framework, effect code, large tables |

The "contended" regions are slowed by ULA memory accesses during the paper area (see [contention_model.md](../05_development/03_memory_and_io/contention_model.md)). Code executing from contended memory runs ~5–15% slower than code in uncontended memory. Framework code, the music player, and the per-frame effect code should always live in the upper 32 KB if possible.

#### Typical 48K Demo Layout

```
#4000-#5AFF  Screen (always)
#5B00-#5BFF  Framework scratch (1 page)
#5C00-#5CBF  (system variables — left alone)
#5CC0-#7FFF  Effect data (contended) — tables, screen-offset lists, sine samples
#8000-#9FFF  Music player + module (~8 KB)
#A000-#BFFF  Current effect's code (~8 KB)
#C000-#DFFF  Framework code (~8 KB)
#E000-#FDFF  Large tables (sine, projection, font) (~8 KB)
#FE00-#FEFF  Stack (256 bytes — plenty)
#FF00-#FFFF  (top of stack, VARS space)
```

This is tight: a 48K demo has roughly **~24 KB of usable code/data space** after the screen and system overhead. Large effects (3D scenes with many vertices, or multicolor engines with precomputed rewrite sequences) often do not fit and must be split across parts.

### 5.2 The 128K Banked Memory Map

The 128K Spectrum and its descendants add **bank switching** via port `#7FFD`. The lower 16 KB (`#0000`–`#3FFF`) is either ROM 0 (128K BASIC), ROM 1 (48K BASIC), or — on the +2A/+3 — one of four "extra" ROMs. The middle 16 KB (`#4000`–`#7FFF`) is always bank 5 (containing the screen). The upper 16 KB (`#8000`–`#BFFF`) is always bank 2. The top 16 KB (`#C000`–`#FFFF`) is **swappable**: one of banks 0, 1, 3, 4, 6, 7 can be visible there.

The swappable bank at `#C000` is the key to 128K demos. A framework can:

- Load effect code into banks 0, 1, 3, 4, 6, 7 (each 16 KB) without affecting the running demo.
- Swap the visible bank at `#C000` instantly via a single `LD A,bank` / `OUT (#FD),A`.
- Pre-load multiple effects into different banks and switch between them with one instruction.

This gives a 128K demo **~96 KB of usable code/data** (6 swappable banks × 16 KB) vs. 24 KB on the 48K — a 4× improvement.

#### Typical 128K Demo Layout

```
#0000-#3FFF  ROM 0 (128K BASIC) — left alone unless used for ROM calls
#4000-#5AFF  Screen (bank 5) — always visible
#5B00-#7FFF  Bank 5 free area — small framework data, effect state
#8000-#BFFF  Bank 2 — music player + module + framework core (~16 KB)
#C000-#FFFF  Swappable bank — current effect's code (~16 KB)

Banks 0, 1, 3, 4, 6, 7: pre-loaded with other effects' code
```

The framework's main loop executes from bank 2 and calls into the swappable bank at `#C000` for effect-specific code. When a part ends, the framework swaps the next part's bank into `#C000` and calls its init routine.

### 5.3 The Pentagon/TR-DOS Model

The Pentagon 128K (and its successors) follow the 128K banking model but add a **TR-DOS disk interface** with its own ROM at `#0000`–`#3FFF` (paged in via port `#7FFD` bit 4). TR-DOS provides:

- Block I/O to a 720 KB floppy (80 tracks × 16 sectors × 512 bytes on a double-density drive).
- A built-in disk cache in the RAM-disc area (banks 0, 1, 3, 4, 6, 7 are sometimes used as a disk cache).
- File-based loading via the `TR-DOS` BASIC extensions.

A Pentagon demo can either:
1. **Load all effects upfront** into RAM-disc banks, then run the demo from RAM (no disk access during demo).
2. **Stream effects from disk on demand**, loading each effect's code and data just before it is needed.

The streaming approach is more flexible but risks audio dropouts during loads (the music ISR must be paused while TR-DOS accesses the disk). See §6.5 for split-ISR techniques that work around this.

### 5.4 Stack and Framework Locations

The stack is typically placed at the **top of RAM** (`#FF00`–`#FFFF` on the 48K, or in bank 2's top on the 128K). This area is uncontended and not banked, so the stack is always accessible regardless of which bank is visible at `#C000`.

The framework code itself lives in **bank 2** (always visible on 128K) or in the upper 16 KB of the 48K (`#C000`–`#FF00`), leaving the top of RAM for the stack. This means the framework can always be called without swapping.

### 5.5 Loading Strategies

Three patterns for getting effect code and data into RAM:

#### Preload All

At demo start, before the music begins, the framework loads every effect's code and data into RAM. On the 48K this is impossible (24 KB total); on the 128K with TR-DOS it is feasible for ~6 effects (6 × 16 KB = 96 KB, fits in 6 swappable banks).

Advantages: no disk activity during the demo; no audio dropouts.
Disadvantages: limited effect count; long initial load time.

#### Stream Per-Part

At each part transition, the framework loads the next part's code/data from disk. On the 128K, this means swapping banks and calling TR-DOS to load. On the 48K, this means loading into a fixed buffer and overwriting the previous effect's code.

Advantages: unlimited effect count; can use the full 96 KB of banked RAM at each part.
Disadvantages: brief disk activity during transitions; audio may stutter during loads unless a split ISR is used.

#### Disk-Streamed Frames (TS-Config)

The TS-Config extension (see [multicolor_techniques.md](multicolor_techniques.md) §7.4) streams **full-frame multicolor data** from disk during the demo, with the disk's own DMA handling the timing. This allows 25 fps full-screen multicolor with no CPU cost per frame — but the entire demo is essentially a video playback, with no per-frame computation.

### 5.6 Memory Failure Modes

Common memory-related bugs:

- **Bank swap during ISR** — swapping the bank at `#C000` while the ISR is executing code in that bank causes a crash. The framework must swap banks only with interrupts disabled, and the ISR must not access the swappable bank.
- **Stack overflow into tables** — a deep `CALL` chain (e.g. framework → effect → sub-routine) can overflow the 256-byte stack into the table area. The framework must limit call depth or move the stack.
- **Contended memory for time-critical code** — placing the music player in contended memory (`#4000`–`#7FFF`) slows it by ~10%, which may break the player's tight timing assumptions.
- **Screen overwrite** — an effect that writes to `#4000`–`#5AFF` for scratch storage corrupts the display. Effects must treat the screen area as read-only except for the actual pixel writes.

---

## 6. ISR Architecture

Every Spectrum demo is driven by a **VBLANK interrupt service routine** (ISR) that fires 50 (or 60) times per second. The ISR is the framework's heartbeat: it advances the music player, calls the effect's per-frame routine, and (for multicolor) performs the raster-synchronous attribute rewrite. Getting the ISR architecture right is the framework's most critical design decision.

### 6.1 The Single-ISR Model

The simplest model is a single ISR that does **everything**:

```z80
isr:
    PUSH AF,BC,DE,HL            ; save registers
    PUSH IX,IY                  ; save index regs
    CALL music_player           ; advance PT3 player
    CALL effect_frame           ; run current effect's per-frame
    ; (for multicolor demos: CALL multicolor_rewrite goes here,
    ; but only when the raster is in the right position)
    POP IX,IY
    POP HL,DE,BC,AF
    EI
    RETI
```

This is the model used by most 48K demos and by 128K demos that don't stream from disk. The ISR runs once per frame, executes its three calls, and returns. Total ISR cost: ~10,000–20,000 T-states for music + effect, well within the 70,000 T-state frame budget.

### 6.2 IM2 vs IM1

The Z80 supports two interrupt modes relevant to Spectrum demos:

- **IM1** — the ISR is always at address `#0038` (in the ROM). The ROM's default ISR reads the keyboard and returns. To take over, the demo writes a `JP <my_isr>` to `#0038` (technically to the RAM underneath, which requires disabling the ROM paging).
- **IM2** — the ISR address is read from a 256-byte vector table at `I*256 + byte_on_bus`. This gives full control over the ISR address without modifying the ROM area.

Most frameworks use **IM2** because it is portable (works on 48K and 128K without ROM paging tricks) and flexible (the ISR address can be changed at runtime by editing the vector table). See [interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md) for the full setup.

### 6.3 Multi-Rate Scheduling

Not all framework work needs to happen at 50 Hz. A common pattern:

- **Music player**: 50 Hz (every frame).
- **Effect per-frame**: 50 Hz for fluid effects; 25 Hz for expensive effects (every other frame).
- **Framework event-list scan**: 50 Hz on simple frameworks; 12.5 Hz (every 4th frame) on frameworks with expensive scans.
- **Disk I/O check**: 1–5 Hz (only when a load is in progress).

The ISR implements this with a **frame counter** that masks calls:

```z80
isr:
    PUSH ...
    CALL music_player              ; every frame
    
    LD   A,(frame_counter)
    INC  A
    LD   (frame_counter),A
    BIT  0,A                       ; odd or even frame?
    JR   Z,every_other
    CALL effect_frame              ; only on odd frames → 25 Hz
every_other:
    
    AND  #03                       ; check bits 0-1
    JR   NZ,no_scan
    CALL framework_scan            ; every 4th frame → 12.5 Hz
no_scan:
    
    POP ...
    EI
    RETI
```

Multi-rate scheduling lets a framework run expensive effects (which need more than one frame's worth of CPU) without dropping the music's frame rate.

### 6.4 The Multicolor Constraint

For demos that use 8×1 or 8×2 multicolor, the ISR must do its work **at the exact raster position** required for the attribute rewrite. This is fundamentally different from the single-ISR model above — the multicolor rewrite happens during the paper scan, not at VBLANK.

The standard pattern (see [multicolor_techniques.md](multicolor_techniques.md) §5) is:

1. VBLANK INT fires at the top of the frame.
2. The ISR runs the music player and the effect's per-frame computation, then **waits for the raster to reach the paper area** (via floating bus).
3. The ISR executes the multicolor rewrite synchronously with the raster, scanline by scanline.
4. The ISR returns after the last paper scanline.

This is the most demanding ISR architecture on the Spectrum: the ISR is active for **almost the entire frame** and must produce attribute writes at exact T-state offsets. Frameworks targeting multicolor demos are built around this constraint from the start.

### 6.5 Split ISR for Disk Streaming

When a demo streams effect code from disk during the demo (§5.5), the disk I/O can take 100+ ms per block — long enough that the music player would miss frames if interrupts were disabled. The solution is a **split ISR**:

- The TR-DOS ROM has its own ISR that runs while disk I/O is in progress.
- This ISR **does not call the music player** (TR-DOS doesn't know about the demo's player).
- The demo installs a wrapper that intercepts the TR-DOS ISR and calls the music player on each frame, even during disk I/O.

This is tricky to implement correctly — it requires patching TR-DOS's ISR vector and being careful about stack state — but it allows **gapless music during disk loads**, which is essential for streamed demos.

### 6.6 What Goes in the ISR

A summary of what an ISR might do, by demo complexity:

| Demo type | ISR work |
|---|---|
| **1K intro** | Music player (beeper); effect per-frame. |
| **48K demo (no multicolor)** | Music player (PT3); effect per-frame; event-list scan. |
| **48K demo (multicolor)** | Music player; effect per-frame; raster-synchronous multicolor rewrite. |
| **128K demo** | Music player; effect per-frame; bank-swap bookkeeping; event-list scan. |
| **Pentagon/TS-Config (streaming)** | Music player; effect per-frame; split ISR for disk I/O; optional raster rewrite. |
| **ZX Spectrum Next** | Music player; effect per-frame; Layer 2 / tilemap / copper updates; layer swapping. |

---

## 7. Part Transitions

A **part transition** is the visual moment when one effect ends and another begins. Good transitions hide the technical work of loading/swapping code and data; bad transitions expose a visible glitch (frozen frame, garbage pixels, palette flash).

### 7.1 Hard Cut

The simplest transition: **no transition**. At the music position for the next part, the framework:

1. Calls the current effect's `exit` routine (clears the screen, frees state).
2. Swaps the next effect's bank in (128K) or loads its code (48K).
3. Calls the next effect's `init` routine.
4. Calls the next effect's per-frame routine for the first frame.

Total time: ~1 frame (20 ms), invisible to the viewer if done at VBLANK.

Hard cuts are jarring visually but appropriate for fast-paced demos where each part is short. They are also the only option for 4K and smaller intros where there is no room for fade code.

### 7.2 Fade to Black / Fade In

A two-step transition:

1. **Fade out**: over *N* frames (typically 8–30), reduce the screen brightness by modifying all attribute bytes — paper becomes black, ink becomes a darker shade.
2. **Swap**: while the screen is black, perform the hard cut (§7.1).
3. **Fade in**: over *N* frames, restore the new effect's attributes to full brightness.

The fade can be **attribute-only** (cheap, ~200 T-states per frame) or **pixel-level** (expensive, ~5000 T-states per frame, requires re-drawing the effect at each brightness level).

### 7.3 Crossfade

The most visually impressive transition: the outgoing effect's frame dissolves into the incoming effect's frame over *N* frames. This requires:

- Both effects' current frames in memory simultaneously.
- A blend routine that mixes the two framebuffers per pixel or per attribute.

On the 48K, a crossfade is impractical (no room for two framebuffers). On the 128K, a crossfade can be done by:
1. Rendering the outgoing effect's final frame to bank 5 (screen).
2. Rendering the incoming effect's first frame to bank 7 (off-screen).
3. Per frame, blending bank 7 into bank 5 with decreasing opacity.

Crossfades are rare on the Spectrum due to the cost; they are more common on the C64 (which has hardware-assisted crossfades via the VIC-II's sprite priority bit).

### 7.4 Blank-Frame Swap

A compromise between hard cut and fade:

1. Clear the screen to a single color (typically black) — 1 frame.
2. While the screen is blank, perform the swap (1–2 frames).
3. Reveal the new effect — 1 frame.

Total: 3–4 frames (~80 ms), invisible to the viewer. The blank frames hide the loading latency.

### 7.5 Gradual Load

For demos that stream from disk (§5.5), the new effect's code and data may arrive in pieces over several seconds. The framework can hide this by:

1. Running the outgoing effect with reduced CPU (e.g. at 25 Hz instead of 50).
2. Loading the new effect's code in the background during the freed frames.
3. Once the load is complete, performing a hard cut or fade.

This requires a split ISR (§6.5) to keep music running during the load.

### 7.6 Transition Choice

| Transition | Cost (bytes) | Cost (frames) | Use when |
|---|---|---|---|
| Hard cut | 0 | 1 | Fast demos; intros ≤ 4K |
| Fade to black | ~50 | 16–60 | Most demos; mid-budget |
| Crossfade | ~200 + buffer | 16–30 | High-end 128K demos |
| Blank-frame swap | ~20 | 3–4 | Streamed demos; tight budgets |
| Gradual load | ~100 + split ISR | varies | Disk-streamed Pentagon demos |

The choice is driven by demo style, memory budget, and party expectations. The Forever party's size-coding compos require hard cuts (no room for fades); the Chaos Constructions megademo compos expect at least fade-to-black transitions.

---
## 8. Notable Frameworks

Rather than enumerate specific framework names — most Spectrum frameworks are private to their group and never receive an official name or public release — this section describes the **framework traditions** by region and era. Specific demos built on each tradition are cataloged in [notable_demos.md](notable_demos.md).

### 8.1 The First Generation (1991–1996)

The earliest Spectrum demo frameworks (1991–1994) were essentially **hardcoded sequences** (§3.1) with no abstraction. Each "part" was a self-contained routine that ran to completion and returned; the framework was just a list of `CALL` instructions in `main_loop`. Music was typically beeper-based (since AY music required a more sophisticated player than the early frameworks could host) or used a single fixed PT2 module with no position tracking.

Characteristics:
- No event lists, no scripts — pure code.
- Hard cuts only — no transitions.
- No banked memory use (most early demos targeted the 48K).
- Music was either beeper or played from a single PT2 module with no sync to visuals.
- Total framework code: ~200–500 bytes.

These frameworks were rarely reusable: each demo had its own, written from scratch. The concept of a "reusable engine" had not yet emerged on the Spectrum.

### 8.2 The Soviet School (1996–2005)

The Soviet/Russian scene developed the **first widely-reused Spectrum framework architecture**. The key innovations:

- **PT3 player integration**: the framework shipped with a PT3 player at a fixed address, and the music position counter was a public symbol that effects could read for sync.
- **Event-list sequencing**: a static table of (music_position, action) pairs drove the demo. This is the model described in §3.2.
- **Banked memory support**: the framework handled bank swaps at `#C000` automatically; each effect's init/exit routines could request a specific bank.
- **Fade-to-black transitions**: a standard ~50-byte fade routine was built into the framework and called between parts.

The Soviet framework tradition was codified by groups like **X-Trade**, **Eternity**, **Machinists Of Toy Sceners**, and **Brutal** — each had its own variant, but the overall architecture was remarkably consistent. By 2000, a "standard" Pentagon framework was ~1.5–2 KB of code, including the PT3 player.

A typical Soviet framework of this era:

```
[bank 2, persistent]
  framework_core:      ~600 bytes (event-list scan, transitions, bank mgmt)
  music_player:        ~700 bytes (PT3 player + 1 module)
  fade_routine:        ~50 bytes
  text_renderer:       ~150 bytes
  greet_scroller:      ~150 bytes

[bank at #C000, swappable per part]
  effect_init, effect_frame, effect_exit, effect_data
```

This architecture was published, discussed in disk magazines (see [soviet_demo_scene.md](soviet_demo_scene.md) §7), and effectively became the de facto standard for Pentagon demos by 2003.

### 8.3 The Western School (1995–2010)

The Western European scene (UK, Germany, Finland, Poland) developed a parallel framework tradition with different priorities:

- **Less standardisation**: each group wrote its own framework from scratch, often for a single demo. There was no equivalent of the Soviet "de facto standard".
- **More variety in sequencing**: Western frameworks experimented with script-driven interpreters (§3.3) earlier than the Soviet scene.
- **More emphasis on 48K demos**: Western sceners targeted the 48K well into the 2000s, when the Soviet scene had largely moved to the Pentagon 128K.
- **Less reliance on PT3**: Western groups used a wider variety of players (Wham Music Editor, Music Studio, MSM, etc.), so framework sync logic was less standardized.

Western frameworks tended to be **smaller** (48K target) and **more bespoke** than Soviet ones. The lack of standardisation made cross-group collaboration rare but also encouraged experimentation.

### 8.4 Modern Frameworks (2010–present)

The post-2010 scene has seen renewed framework development driven by:

- **Cross-platform targets**: a modern framework may need to run on 48K, 128K, Pentagon, TS-Config, DivMMC, and ZX Spectrum Next, with feature detection at startup.
- **Open-source culture**: Github has made it possible to publish frameworks, accept patches, and build on others' work — something the Soviet scene never had.
- **The Next's hardware**: Layer 2 (256-color framebuffer), tilemap, hardware sprites, and the copper unit require new framework abstractions.

Several open-source frameworks have appeared since 2015, providing reusable effect sequencing, music sync, and hardware abstraction. These frameworks tend to be **much larger** than the Soviet 2 KB standard — 4–8 KB is typical, with extensive feature sets.

### 8.5 The "Reusable Engine" Pattern

The most significant shift in modern Spectrum framework development is the **reusable engine**: a single framework that is maintained independently of any specific demo, with effects plugged in as modules. This pattern, borrowed from the C64 and PC demoscene, has produced frameworks that:

- Are versioned (1.0, 1.1, 2.0) and announced in scene news.
- Support multiple demos from the same group.
- Accept effects from external authors as "plug-in" modules.
- Document their public API (init/exit contracts, register conventions, available memory regions).

This is a major cultural change from the early 1990s, when every demo's framework was bespoke. As of 2024, a group starting a new Spectrum demo is more likely to adopt an existing open-source framework than to write its own from scratch.

### 8.6 Framework Identification

When reverse-engineering a Spectrum demo (see [../08_reverse_engineering/README.md](../08_reverse_engineering/README.md)), the framework is the **first thing to identify**. Key signatures:

- **ISR vector table**: the IM2 vector table's address reveals the framework's interrupt architecture.
- **Music player address**: most frameworks include the PT3 player at a fixed address; identifying the player identifies the framework's music sync point.
- **Bank swap sequence**: the sequence of `OUT (#FD),A` instructions reveals the bank layout.
- **Event-list format**: the table format (rows of 5 bytes vs 6 bytes vs 8 bytes) is framework-specific.
- **Greeting strings**: framework authors often embed a credit string like "Framework by X-Trade, 1999" in the binary.

Once the framework is identified, the rest of the disassembly falls into place: the effect code is in known banks, the music player is at a known address, and the event list is at a known offset.

---

## 9. The ZX Spectrum Next and Modern Hardware

The **ZX Spectrum Next** (released 2020, designed 2017) is a modern reimplementation of the Spectrum with significant hardware additions. Its capabilities change the framework design space substantially, and a modern framework may target the Next either exclusively or as one of several platforms.

### 9.1 The Next's Hardware Additions

The Next is binary-compatible with the 48K and 128K Spectrum but adds:

- **Layer 2**: a 256-color framebuffer at 320×256 resolution, occupying a 16 KB bank that can be paged into `#0000`–`#3FFF` for writing. This eliminates the 8×8 attribute constraint (see [multicolor_techniques.md](multicolor_techniques.md) §10.3) and allows full-color effects at 50 Hz with no raster synchronisation.
- **Tilemap**: a hardware tile-based display mode (40×32 tiles of 8×8 pixels, with per-tile attributes and a 256-entry palette). Useful for scrolling backgrounds and HUDs without per-pixel CPU cost.
- **Hardware sprites**: up to 256 sprites (16×16 pixels each), 64 visible per scanline, with per-sprite attributes (palette, mirror, rotation). This is the Spectrum's first hardware sprite engine.
- **Copper unit**: a programmable raster co-processor similar to the Amiga's copper. The copper can change hardware registers at specific scanlines without CPU intervention — enabling "raster bars" and palette swaps for free.
- **Faster CPU**: 28 MHz Z80 (vs. 3.5 MHz on the original). Demos that target the Next's 28 MHz mode can run ~8× more code per frame.
- **More memory**: 2 MB RAM (vs. 128 KB), paged in 16 KB banks. The banked memory model is generalized to many more banks.
- **Extended AY**: two AY chips (6 channels total), plus 8-channel DMA-driven PCM playback.
- **Hardware acceleration**: hardware line draw, hardware fill, hardware blit.

See [../02_hardware/newgen/README.md](../02_hardware/newgen/README.md) for the Next hardware reference.

### 9.2 Framework Implications

The Next's hardware changes framework design in three ways:

#### Layer 2 vs Screen Rewrite

A 48K/128K framework spends much of its time in the multicolor rewrite — the raster-synchronous attribute writes. On the Next, **Layer 2 replaces this entirely**: the framework writes pixels to Layer 2 memory and the hardware displays them. No raster synchronisation is needed; no multicolor engine runs. The ISR can be much simpler (§6.4's "multicolor constraint" disappears).

#### Copper-Driven Effects

The copper unit handles effects that previously required per-scanline CPU work: raster bars, palette changes, split-screen modes. A framework targeting the Next can offload these to the copper and free the CPU for effect computation.

#### Banked Memory Simplification

With 2 MB of RAM and a more flexible banking scheme, a Next framework does not need the careful bank-budgeting of a 128K framework. Effect code and data can live in dedicated banks, swapped at part boundaries, with much less risk of running out.

### 9.3 A Modern Next Framework

A Next-targeting framework might look like:

```
[bank 7, persistent]
  framework_core:        ~2 KB (event-list scan, copper programming, layer mgmt)
  music_player:          ~1 KB (AY or 8-channel PCM player)
  text_renderer:         ~500 bytes (Layer 2 text)
  greet_scroller:        ~500 bytes

[bank 5, persistent]
  Layer 2 framebuffer:   16 KB (the actual display)

[swappable banks]
  effect_init, effect_frame, effect_exit, effect_data
  copper_lists (per-effect raster programs)
```

Total framework overhead: ~4 KB. Effect code can be much larger than on a 128K Spectrum — a single effect might use 32 KB or more of code and data, with multiple effects pre-loaded into different banks.

### 9.4 Cross-Platform Frameworks

Many modern frameworks target **both stock Spectrum and Next**, with feature detection at start-up. The framework queries the hardware (via the Next's `next-reg` ports) and configures itself accordingly:

- On stock 48K/128K: use the standard screen, multicolor rewrite, single AY.
- On Next: use Layer 2, copper, two AYs, sprites.

This requires the framework to support two distinct rendering paths per effect — a substantial authoring cost — but allows a single demo binary to run on both platforms.

### 9.5 Other Modern Hardware

Beyond the Next, several other modern Spectrum-compatible platforms affect framework design:

- **TS-Config**: disk-streaming of multicolor frames (see [multicolor_techniques.md](multicolor_techniques.md) §7.4). Frameworks targeting TS-Config are built around the disk DMA and have a distinctive "video player" architecture.
- **DivMMC, DivIDE**: IDE/SD storage. Replaces TR-DOS floppy with faster I/O, allowing streaming without split ISR tricks.
- **ZX Evo (Pentagon 1024)**: 1 MB RAM, faster CPU, more banks. Frameworks targeting it have generous memory but must support the Pentagon's banking quirks.
- **ZX Spectrum 48K/+2 with ULAplus**: 64-color palette extension. Allows nicer color palettes without raster sync.

Each platform has its own framework conventions; the cross-platform framework that targets all of them is the holy grail of modern Spectrum development.

---

## 10. Cross-References

This article sits within the ZX Spectrum demoscene knowledge base and connects to the following related articles:

### 10.1 Within the Demoscene Section

- [demoscene_history.md](demoscene_history.md) — when frameworks emerged and how they evolved.
- [soviet_demo_scene.md](soviet_demo_scene.md) — §6 (PT3 ecosystem), §7 (disk magazines), §8 (Soviet framework tradition).
- [demoscene_platforms.md](demoscene_platforms.md) — how frameworks differ across Spectrum models and peer platforms.
- [precalc_trigonometry.md](precalc_trigonometry.md) — the tables a framework precomputes at startup.
- [multicolor_techniques.md](multicolor_techniques.md) — §6 (per-model timing constraints on ISR), §7 (multicolor engines that frameworks schedule), §10 (ULAplus / Next alternatives).
- [effects_catalog.md](effects_catalog.md) — what frameworks sequence (the effect interface contract).
- [compression_packing.md](compression_packing.md) — the depackers frameworks call at part transitions.
- [size_coding.md](size_coding.md) — the smallest frameworks (hardcoded sequences).
- [notable_demos.md](notable_demos.md) — specific demos built on each framework tradition.
- [1bit_music_scene.md](1bit_music_scene.md) — beeper music players used in 1K intro frameworks.
- [README.md](README.md) — index of all demoscene articles.

### 10.2 Within the Hardware and Development Sections

- [../02_hardware/newgen/README.md](../02_hardware/newgen/README.md) — ZX Spectrum Next and modern clones.
- [../05_development/03_memory_and_io/contention_model.md](../05_development/03_memory_and_io/contention_model.md) — the contended memory that framework code must avoid.
- [../05_development/04_interrupts/interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md) — IM2 setup and ISR construction.
- [../05_development/05_display_and_timing/video_frame_48k.md](../05_development/05_display_and_timing/video_frame_48k.md) — the VBLANK timing that drives the ISR.
- [../06_sound/players/ay_player_routines.md](../06_sound/players/ay_player_routines.md) — PT3 and other AY players that frameworks host.
- [../08_reverse_engineering/README.md](../08_reverse_engineering/README.md) — how to identify a framework when reversing a demo binary.

### 10.3 External Resources

- **"How to Write a ZX Spectrum Demo"** (various community tutorials) — beginner-level introductions to framework construction.
- **Pouet.net** — searchable archive of Next and stock-Spectrum demos with sources.
- **ZX Spectrum Next Register Reference** — official documentation of the `next-reg` ports.
- **Github** — modern open-source Spectrum frameworks are typically published here.

---

## License

This article is released under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you credit the original source and license derivative works under the same terms.

The framework architecture descriptions here draw on the published work of dozens of Spectrum demo groups over three decades. Specific attributions for individual framework designs are impractical, but the community's collective contribution is acknowledged.
