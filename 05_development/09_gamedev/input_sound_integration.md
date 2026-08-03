[← Game Dev](README.md) · [Input and Sound Integration](input_sound_integration.md)

# Player Input and Audio Integration — Game-Specific Layers

> **Scope**: This article covers the two integration concerns that sit between the game engine and the player: how input is read, normalized, and dispatched; and how music and SFX are wired into the game loop without breaking its timing budget.

For *what hardware exists* and *what ports it uses*, see [joystick.md](../../03_io/peripherals/joystick.md) (Kempston, Sinclair, Cursor, Fuller), [clone_joysticks.md](../../02_hardware/clones/clone_joysticks.md) (Pentagon/Scorpion defaults), and [keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md) (the Spectrum keyboard). For *how a music player works*, see [ay_player_routines.md](../../06_sound/players/ay_player_routines.md) — player architecture, ISR integration mechanics, PT3/AKG benchmarks.

This article covers **what the game adds on top**: input edge detection, key-redefine UIs, the SFX-vs-music channel-stealing arbitration, and memory budgets that fit a real cartridge or tape.

---

## Article Roadmap

- §1 — Input normalization: producing one bitfield from many devices
- §2 — Edge detection, debouncing, repeat handling
- §3 — The "redefine keys" UI pattern
- §4 — Audio integration: the four places music can live
- §5 — SFX: channel stealing, channel priority, interrupt-driven vs inline
- §6 — Memory budgets: music RAM, SFX RAM, AY register file
- §7 — Cross-references and pitfalls

---

## 1. Input Normalization — One Bitfield From Many Devices

The ZX Spectrum has four major joystick standards (Kempston, Sinclair 1, Sinclair 2, Cursor/Protek), the keyboard matrix (which is its own "joystick" via the 6-0 and 1-5 rows), the Kempston mouse, and on the Next, a second Kempston port plus a Mega-Drive-style extended pad. A game cannot assume any particular device is connected; it must ask the player, then read the chosen device once per frame.

### The normalized bitfield

The standard convention is to produce a single byte every frame where the bits mean the same thing regardless of source device:

```
Bit 7  6  5  4    3    2    1    0
     unused       FIRE RIGHT LEFT DOWN UP
```

This is the **Kempston byte layout**, used as the normalization target because it is active-high (bit set = pressed) and matches the most common hardware standard. The keyboard and other joysticks are read once per frame and converted into this format; the game logic then reads the single byte and dispatches on bits.

```z80
read_input:
        LD    A,(input_device)
        CP    DEV_KEMPSTON
        JR    Z,.read_kempston
        CP    DEV_KEYBOARD
        JR    Z,.read_keyboard
        CP    DEV_SINCLAIR1
        JR    Z,.read_sinclair1
        ; ... etc
        RET

.read_kempston:
        IN    A,(#1F)                ; Kempston is already in normalized form
        LD    (input_state),A
        RET

.read_keyboard:
        ; Read keyboard rows for QWERTY-as-joystick
        ; ... convert to normalized bitfield ...
        LD    (input_state),A
        RET

.read_sinclair1:
        ; Read keyboard row for keys 6-0, convert
        ; ... bit-shuffling ...
        LD    (input_state),A
        RET
```

For detailed port addresses and bit layouts, see [joystick.md](../../03_io/peripherals/joystick.md) and [keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md). This article assumes the device readers are already implemented; what matters here is the **integration contract**: every device reader produces the same byte format, and the game logic consumes only that byte.

### The "merge keyboard and joystick" trick

Many games allow the player to use either device without re-selecting. The merge is a single `OR`:

```z80
read_merged_input:
        CALL  read_kempston           ; Returns Kempston byte in A (or 0 if absent)
        LD    B,A
        CALL  read_keyboard           ; Returns keyboard-derived joystick byte in A
        OR    B                       ; Merge: any device can press any direction
        LD    (input_state),A
        RET
```

The merge is correct as long as both readers use the same bitfield layout. Polarity must match — Kempston is active-high, but the keyboard matrix is active-low. The keyboard reader must invert the polarity before merging; otherwise a "no key pressed" keyboard read merges as `#FF` (all directions pressed).

> [!WARNING]
> The classic input bug: reading Kempston on a 48K Spectrum with no interface attached returns whatever floats on the bus — usually `#FF`, occasionally `#00`, sometimes garbage from the floating bus. If your game's default is "Kempston" and the player has no interface, every direction appears pressed simultaneously. Always show a menu; never assume a default device.

### Detecting the device at runtime

There is **no reliable autodetection**. The closest heuristic: read Kempston; if the result is `#FF` or `#00` (all bits set or all clear), the player has probably not touched the stick but the interface may or may not be present. The honest approach is to ask the player via a menu, with the keyboard as a universal fallback. See [joystick.md](../../03_io/peripherals/joystick.md) §Pitfalls for the technical details.

---

## 2. Edge Detection, Debouncing, and Repeat

The `input_state` byte tells you what is **currently held down**. Game logic usually needs to know what was **newly pressed this frame** (for one-shot actions like jump or fire) or what was **held for N frames** (for charged actions). This requires comparing the current state to the previous state.

### Edge detection

```z80
; Compute edge-detected input: bits set only on the frame a key was newly pressed
compute_edges:
        LD    A,(input_state)          ; Current frame's state
        LD    B,A
        LD    A,(input_prev)           ; Previous frame's state
        CPL                             ; Invert previous
        AND   B                         ; Newly pressed = (current) AND NOT (previous)
        LD    (input_edges),A
        ; Save current as previous for next frame
        LD    A,(input_state)
        LD    (input_prev),A
        RET
```

Game logic then uses `input_edges` for one-shot actions (jump, fire) and `input_state` for continuous actions (move, walk). This is the universal pattern.

```z80
player_input:
        ; Check for jump (edge-triggered)
        LD    A,(input_edges)
        BIT   4,A                      ; FIRE bit
        JR    Z,.no_jump
        ; Initiate jump
        CALL  player_jump
.no_jump:
        ; Check for movement (level-triggered)
        LD    A,(input_state)
        BIT   0,A                      ; RIGHT bit
        JR    Z,.no_right
        LD    A,(player_vx)
        ADD   A,PLAYER_ACCEL
        LD    (player_vx),A
.no_right:
        ; ... etc ...
        RET
```

### Debouncing for menus

In a menu, edge detection is not enough: if the player holds DOWN, the cursor should not advance every frame (50 Hz is far too fast). The standard solution is a **repeat timer**: the first press advances the cursor instantly; if the key is still held after N frames (typically 20–30), the cursor advances every M frames (typically 4–6).

```z80
menu_input:
        LD    A,(input_edges)
        BIT   3,A                      ; DOWN edge
        JR    Z,.no_first_down
        ; First press: advance immediately
        CALL  menu_cursor_down
        LD    A,MENU_REPEAT_DELAY      ; e.g., 25
        LD    (menu_repeat_timer),A
        RET
.no_first_down:
        LD    A,(input_state)
        BIT   3,A                      ; DOWN held
        JR    Z,.no_down_held
        ; Key is held: count down timer
        LD    A,(menu_repeat_timer)
        DEC   A
        LD    (menu_repeat_timer),A
        RET   NZ
        ; Timer expired: advance and reset to faster repeat rate
        CALL  menu_cursor_down
        LD    A,MENU_REPEAT_RATE       ; e.g., 5
        LD    (menu_repeat_timer),A
        RET
.no_down_held:
        ; Key released: reset timer
        LD    A,MENU_REPEAT_DELAY
        LD    (menu_repeat_timer),A
        RET
```

This pattern produces the familiar feel of a PC BIOS menu or a modern game's settings screen: instant first response, then a short pause, then fast repeat.

### Diagonal movement

The normalized bitfield naturally supports diagonals: pressing UP+RIGHT sets both bits. Game logic that checks each direction independently and applies orthogonal velocity vectors will produce diagonal motion automatically. The catch is **diagonal speed boost**: if UP gives velocity (-1, 0) and RIGHT gives (0, +1), then UP+RIGHT gives (-1, +1), which is √2 ≈ 1.41× faster than pure horizontal. Some games accept this (the player gets a slight speed bonus for diagonal movement); others normalize by reducing both components to ~0.7 when both are active. The latter requires sub-pixel arithmetic.

---

## 3. The "Redefine Keys" UI Pattern

Every Western 1980s Spectrum game offers a "Redefine Keys" option in its menu. The pattern is so universal that the player expects it; omitting it is considered rude. The implementation is straightforward:

```z80
redefine_keys:
        LD    HL,key_table              ; 5 entries: right, left, down, up, fire
        LD    B,5
.red_loop:
        ; Prompt "Press key for <action>"
        LD    A,(HL+action_name_offset)
        CALL  print_action_name
        CALL  wait_for_keypress         ; Returns the (row, mask) pair
        LD    (HL+key_row),A
        LD    (HL+key_mask),B
        INC   HL
        DJNZ  .red_loop
        RET
```

The `key_table` stores, for each of the 5 joystick-equivalent actions, the keyboard matrix row and bitmask that triggers it. The keyboard reader then iterates this table instead of testing hardcoded rows.

For multi-device games, the redefine UI typically has three layers:

1. **Joystick selection**: KEMPSTON / SINCLAIR 1 / SINCLAIR 2 / CURSOR / KEYBOARD ONLY
2. **Keyboard redefine** (only if "KEYBOARD ONLY" or always): pick keys for each direction
3. **Per-action fire mode** (rare): some games distinguish "fire" from "jump" and let the player assign different keys

The Western menu litany "KEMPSTON / SINCLAIR / CURSOR / REDEFINE KEYS" is the direct consequence of Sinclair not shipping a standard joystick port with the machine. See [joystick.md](../../03_io/peripherals/joystick.md) for the full historical story.

### Post-Soviet convention

The Russian/Ukrainian software market standardized on Kempston-as-default because every clone machine has it on the motherboard. The menu is correspondingly simpler: **"KEMPSTON / KEYBOARD / REDEFINE"** — three options, with Kempston assumed by default. This is described in [clone_joysticks.md](../../02_hardware/clones/clone_joysticks.md).

---

## 4. Audio Integration — Where the Player Lives

The AY music player is described in detail in [ay_player_routines.md](../../06_sound/players/ay_player_routines.md) — its construction, ISR integration patterns, per-model frame budgets, and per-format structure. This article does not duplicate that. What it covers instead is the **integration decision**: where in the engine and where in memory the player lives, and how the game orchestrates music and SFX.

### Four places the player can live

| Location | Pros | Cons | When to use |
|---|---|---|---|
| **Foreground (called from main loop)** | Simple; no ISR coordination | Music pauses if main loop stalls; burns foreground budget | Only for short SFX; not used for music |
| **ISR (called every frame)** | Music never pauses; isolated from foreground | Must save/restore bank on 128K; ISR cost must fit | The dominant pattern for commercial games |
| **Separate ISR (music at 100 Hz, gameplay at 50 Hz)** | Smoother music; allows Tempo FX | Complex timing; double the per-frame cost | Rare; used by a few Ocean titles for arpeggio-rich music |
| **Dedicated hardware (GS, MoonSound, Covox)** | Free CPU for game; no arbitration | Requires the hardware to be present; non-portable | Only when targeting that hardware specifically |

The ISR-based pattern is the universal default. The next section explains what goes in the ISR and what stays in the foreground.

### What goes in the ISR

```z80
isr:
        ; Save Z80 state
        EX    AF,AF'
        EXX
        PUSH  IX
        PUSH   IY
        ; (On 128K) save current bank, page in music bank
        ; ... bank-switch code (see game_loop.md §4) ...
        ; Tick music player
        CALL  music_tick                ; ~600 T-states for PT3 single AY
        ; Tick any streaming SFX (e.g., sample playback via AY volume register)
        CALL  sfx_stream_tick           ; ~0 if no SFX playing
        ; (On 128K) restore bank
        ; ... bank-restore code ...
        ; Restore Z80 state
        POP   IY
        POP   IX
        EXX
        EX    AF,AF'
        EI
        RETI
```

The total ISR cost is typically 800–1,500 T-states (including save/restore). This is ~2% of the frame budget.

### What stays in the foreground

- **Reading input** — the keyboard matrix and joystick ports are I/O ports, not interrupt-driven. Read once per frame, after `HALT`.
- **Updating entity state** — too expensive for the ISR; belongs in the foreground.
- **Triggering SFX** — when a collision happens, the foreground code sets a flag (`sfx_pending = SFX_EXPLOSION`). The ISR's `sfx_stream_tick` then checks the flag, picks an AY channel for the SFX, and starts playing it.

The contract is: **the foreground triggers, the ISR delivers**. The foreground never writes directly to the AY chip — that would race with the music player's writes.

---

## 5. SFX — Channel Priority and Channel Stealing

The AY has three channels (A, B, C) plus the noise generator. A typical game allocates these:

- **Channel A**: music melody
- **Channel B**: music bass (or harmony)
- **Channel C**: reserved for SFX (with music's Channel C temporarily silenced while SFX plays)

This is the **dedicated-SFX-channel** model. When an SFX fires, the engine:

1. Saves the music's current Channel C state (period, volume, envelope).
2. Writes the SFX's period and envelope to Channel C.
3. Sets a frame counter for how long the SFX plays.
4. On each frame while the counter is non-zero, the music player's Channel C writes are skipped (or routed to a scratch buffer).
5. When the counter reaches zero, the saved Channel C state is restored and the music resumes.

The audible effect: the music's third channel ducks out for the duration of the SFX. This is the standard pattern for 128K games from *RoboCop* onward.

### Channel priority

Some games (typically action games where SFX are more important than music) use a **priority-based** scheme instead of a dedicated SFX channel. Each SFX has a priority byte; if a higher-priority SFX is requested while a lower-priority one is playing, the lower-priority one is interrupted. Critical SFX (player death, boss explosion) get priority 3; medium SFX (enemy hit) get priority 2; ambient SFX (footsteps) get priority 1.

```z80
trigger_sfx:
        ; A = SFX index
        ; Look up priority
        LD    HL,sfx_priority_table
        ADD   A,L
        LD    L,A
        LD    A,(HL)
        LD    B,A
        ; Compare against currently-playing SFX priority
        LD    A,(current_sfx_priority)
        CP    B
        JR    NC,.skip                  ; Current priority >= new: ignore new SFX
        ; New SFX has higher priority: replace
        LD    A,B
        LD    (current_sfx_priority),A
        ; ... initialize SFX playback ...
.skip:
        RET
```

This pattern was popularized by *Ocean* in the late 1980s and is now standard for action games.

### One-shot vs streaming SFX

The simplest SFX are **one-shot register writes**: the engine writes a fixed set of AY register values to produce a click, a tone, or a short noise burst. Cost: ~100 T-states.

More sophisticated SFX are **streaming**: the engine plays a sequence of register values over multiple frames, typically from a small data table. Cost: ~50 T-states per frame while the SFX plays.

The most expensive SFX are **sampled**: the engine plays a 4-bit PCM sample through the AY volume register at ~7 kHz. Cost: ~48 T-states per sample × 140 samples/frame = ~6,700 T-states per frame. This is too expensive for the foreground; sampled SFX are always ISR-driven.

For full coverage of SFX techniques (one-shot, streaming, sampled), see [ay_ym_techniques.md](../../06_sound/synthesis/ay_ym_techniques.md). This article covers only the **arbitration layer** that decides when and how to play them.

---

## 6. Memory Budgets — Music, SFX, and the Rest

The music subsystem consumes memory in three blocks:

| Block | Size | Notes |
|---|---|---|
| Player code | 600–1,500 bytes | PT3 player ~600 bytes; AKG ~900 bytes; ASM ~1,100 bytes |
| Module data | 4–15 KB | A 3-minute song is ~8 KB in PT3 format |
| SFX data | 1–4 KB | 16–64 short SFX, each 60–250 bytes |
| **Total** | **5–20 KB** | A significant fraction of the 48K budget |

On 48K, the engine must fit alongside the music subsystem in 24 KB. *Manic Miner* has no AY music (beeper only) for this reason; the 9 KB engine + 20 KB level data leaves no room. The first AY-music 48K games appeared after *Manic Miner* but typically used the AY only for short tunes between levels, not for in-game music.

On 128K, music lives in its own dedicated bank. The 16 KB bank holds player + module + SFX with room to spare. Multiple songs can be pre-loaded (one per level) by paging between banks.

### The beeper alternative

The 48K's beeper can play music during gameplay via the **beeper engine** pattern (see [beeper_synthesis.md](../../06_sound/synthesis/beeper_synthesis.md)). The cost is much higher than AY: ~10,000–20,000 T-states per frame for a 2-channel beeper engine, leaving little headroom for the game itself. Most commercial 48K games used beeper music only on the title screen, not in-game.

### Music size vs music length

The relationship between module size and song length is non-linear. A 30-second loop is ~2 KB; a 3-minute song is ~8 KB; a 10-minute epic is ~20 KB. The cost grows with the number of patterns × pattern length, not with playback duration. A short loop played for 5 minutes is still 2 KB.

For games with many short loops (one per level), the total cost is `level_count × per_level_module_size`. *Dizzy* series uses ~10 levels × ~3 KB/level = ~30 KB of music, requiring 128K banking to fit. Games with one continuous soundtrack (*Chase H.Q.*) use one ~8 KB module across all levels.

---

## 7. Cross-References

- [game_loop.md](game_loop.md) — The main loop's structure determines when input is read and when the music player is ticked. This article covers what happens inside those calls.
- [entities_collision_ai.md](entities_collision_ai.md) — Entity collision events trigger SFX. The trigger fires from the entity update; the SFX playback happens later in the ISR.
- [interrupt_programming.md](../04_interrupts/interrupt_programming.md) — ISR construction for the music player. The bank-switch pattern documented there is essential for 128K music integration.
- [joystick.md](../../03_io/peripherals/joystick.md) — Joystick hardware reference: ports, bit layouts, polarity conventions, and the historical reason for the four competing standards.
- [clone_joysticks.md](../../02_hardware/clones/clone_joysticks.md) — Why Soviet clones default to Kempston, and why the post-Soviet menu convention differs from the Western one.
- [keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md) — The keyboard matrix as an input device. Section "Game Input Patterns" shows a complete keyboard-derived joystick reader.
- [mouse.md](../../03_io/peripherals/mouse.md) — Kempston mouse support; relevant for UI-heavy games and point-and-click adventures.
- [ay_player_routines.md](../../06_sound/players/ay_player_routines.md) — Player architecture, ISR integration, per-model frame budgets. This article assumes that material; it covers the game-side integration.
- [player_comparison.md](../../06_sound/players/player_comparison.md) — PT3 vs AKG vs ASM head-to-head. The choice of player affects the integration budget (Section 6).
- [ay_ym_techniques.md](../../06_sound/synthesis/ay_ym_techniques.md) — SFX synthesis techniques (one-shot register writes, streaming SFX, sampled PCM). This article covers the arbitration layer; that article covers the synthesis.
- [beeper_synthesis.md](../../06_sound/synthesis/beeper_synthesis.md) — 1-bit beeper music engines (the only option on 48K, alternative on 128K).
- [ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md) — AY hardware reference: register map, port addresses, signal path.
- [zx_next_audio.md](../../06_sound/hardware/zx_next_audio.md) — Next audio: 3× AY + DMA sample playback, and why the integration budget is fundamentally different.
- [asset_tools.md](../../09_toolchain/asset_tools.md) — Authoring tools for music and SFX (Vortex Tracker II, Arkos Tracker, Beepola).
- [game_case_studies.md](game_case_studies.md) — How *Manic Miner*, *Ocean*, and *Rare* wired music and SFX into their engines.

---

## 8. Common Pitfalls

### Pitfall 1 — Polarity mismatch in merged input

Kempston is active-high (bit set = pressed). Keyboard matrix is active-low (bit clear = pressed). The naive merge `OR` produces garbage. The keyboard reader must **invert** the matrix read before merging. This is described in [joystick.md](../../03_io/peripherals/joystick.md) §Pitfalls.

### Pitfall 2 — Edge detection computed too early

If `input_edges` is computed before the new `input_state` is read, the edges reflect last frame's state vs. two frames ago. Always read the new state first, then compute edges against the stored previous.

### Pitfall 3 — Reading input inside the ISR

Reading the keyboard matrix or Kempston port inside the ISR seems efficient (zero cost in foreground) but causes two bugs: (a) the input byte can change mid-frame if the player releases a key, producing phantom presses in the simulation; (b) the ISR becomes longer. **Read input once, in the foreground, after `HALT`.** See [game_loop.md](game_loop.md) §Pitfalls.

### Pitfall 4 — Triggering SFX from the foreground by writing AY registers directly

```z80
; BAD: races with the music player in the ISR
play_explosion:
        LD    BC,#FFFD
        LD    A,8                       ; Channel A volume register
        OUT   (C),A
        LD    BC,#BFFD
        LD    A,#10                     ; Full volume
        OUT   (C),A
        RET
```

This writes to the AY chip while the music player in the ISR is mid-write-sequence. The result is unpredictable: sometimes the music's Channel A note is overwritten, sometimes the explosion is overwritten by the music, sometimes both. **Always set a flag** (`sfx_pending`) and let the ISR handle the AY writes from a single, synchronized code path.

### Pitfall 5 — Music module too large for 48K

A 12 KB PT3 module leaves only 12 KB for the engine + level data + sprite tables. Most 48K games cannot afford this. Either reduce the module (fewer patterns, shorter instruments) or target the 128K with banking.

### Pitfall 6 — Bank-switch races in the music ISR

On 128K, the ISR switches to the music bank, calls the player, switches back. If the foreground code happens to be reading data from a paged bank when the ISR fires, the ISR's bank-switch makes the foreground read garbage. Solution: the ISR must save the current bank value (from `#7FFD`) and restore it exactly. See [game_loop.md](game_loop.md) §4 for the canonical pattern.

### Pitfall 7 — Frame-flag ignored when CPU is in turbo mode

On the Next at 7/14/28 MHz, the ISR fires at the same rate (50 Hz, tied to video), but the foreground loop runs much faster. If the loop polls `frame_flag` in a tight `while` loop, it will busy-wait for most of the frame even at 28 MHz — useful only if you want the CPU free for other work. The standard pattern: `HALT` once per frame to yield, then do per-frame work.

---

## 9. References

- **Richard Dymond (SkoolKit)**, [*Jet Set Willy* RAM disassembly](https://skoolkit.ca/disassemblies/jet_set_willy/) — The JSW input handling and beeper-music integration are documented in the disassembly's commentary.
- **Chris Wild**, [*Ocean Software: A Technical Retrospective*](https://web.archive.org/) — Discussion of Ocean's 128K music engine and the bank-switching ISR pattern.
- **Jonathan Cauldwell**, *How to Write ZX Spectrum Games* (2008) — Practical input handling and SFX integration for modern Spectrum homebrew.
- **Bulba**, [Vortex Tracker II documentation](https://bulba.untergrund.net/) — Authoring guidance for the most widely used PT3 editor.
- **Targhan**, [Arkos Tracker 2 documentation](https://www.julien-neumetaler.com/arkos-tracker-2) — Authoring guidance for AKG/AKM/AKY players; covers the SFX-channel-stealing arbitration in detail.
- **shiru**, [*AY Music Programming*](https://shiru.untergrund.net/software.shtml) — Practical guide to writing AY players and SFX systems.
- **Einar Saukas**, [World of Spectrum forums](https://worldofspectrum.org/forums/) — Numerous posts on player optimization and integration patterns.

---

## License

This article is released under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you credit the original source and license derivative works under the same terms.
