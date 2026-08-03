[← Home](../../README.md) · [Interrupts](README.md)

# Demoscene IM2 Effects — Survey, Patterns, and Real Game Disassembly

Interrupt Mode 2 is the demoscene's swiss army knife. Where the ROM uses IM1 because it has one job (count frames and scan the keyboard), demo and game authors use IM2 because they need to drive multiple independent systems — music, raster effects, screen updates, input, level streaming — from a single 50 Hz heartbeat. This article catalogs the IM2 patterns observed in real software, from commercial 128K games of the late 1980s through modern demoscene releases.

> [!NOTE]
> This article assumes you already understand IM2 mechanics from [interrupt_programming.md](interrupt_programming.md) (the 257-byte vector table, the floating-bus problem, why all vectors point to the same address). Here we focus on **how real software uses IM2**, not how IM2 works.

---

## Vector Table Placement Rules

### Where the Table Goes

The IM2 vector table is 257 bytes, located at `I × 256`. The `I` register determines the table address. The choice of `I` is constrained by Spectrum hardware:

| `I` value range | Table location | Behavior on real hardware | Notes |
|---|---|---|---|
| `#00`–`#3F` | `#0000`–`#3FFF` | **ROM area** — table reads return ROM bytes, not your table | Cannot use |
| `#40`–`#7F` | `#4000`–`#7FFF` | **Contended memory** — crashes on real Spectrums | See Gasman's letter below |
| `#80`–`#BE` | `#8000`–`#BEFF` | **Uncontended RAM** — safe | Recommended |
| `#BF` | `#BF00` | Crosses `#BFFF`/`#C000` bank boundary on 128K | Avoid |
| `#C0`–`#FE` | `#C000`–`#FEFF` | **Bank-switchable region** — works if your ISR is in the same bank as the table | Plan carefully |
| `#FF` | `#FF00` | Overlaps system variables (UDG at `#FF58`) | Avoid |

### Why #4000-#7FFF Crashes Real Spectrums

Gasman's open letter to the Russian demoscene (Subliminal Extacy #3, 2002) makes the canonical statement:

> "When the I register is set between 40 and 7F, the computer crashes. Please think of this while you're coding, and arrange your code so that there's space to put it higher in memory."

The crash is caused by **memory contention timing violations** during the Z80's interrupt acknowledge cycle. The Z80 reads two bytes from the vector table in `I × 256 + vector_byte`, and during these reads the ULA is also fetching screen bytes from the same DRAM chip range. On real 48K Spectrums the contention pattern corrupts the vector table lookup, causing the Z80 to jump to a garbage address.

### Recommended Safe Range

**Always place the vector table at `#8000`–`#BEFF`**, and fill all 257 bytes with the same value (e.g. `#80`, `#90`, `#B0`). The handler address becomes the doubled fill byte (e.g. `#8080`, `#9090`, `#B0B0`).

```z80
; Safe IM2 setup — table at #FE00-#FF00, handler at #9090
    DI
    LD   A,#FE             ; I := #FE (table at #FE00)
    LD   I,A
    LD   HL,#FE00
    LD   (HL),#90          ; All vectors → #9090
    LD   DE,#FE01
    LD   BC,#0100          ; 256 more bytes (257 total)
    LDIR
    IM   2
    EI
```

The handler at `#9090` lives in uncontended RAM and runs at full speed during paper display.

---

## 256-Byte vs 257-Byte Tables — A Real-World Survey

The canonical rule is **257 bytes**: a 256-byte table fails when the vector byte is `#FF`, because the second read at `I × 256 + #FF + 1` crosses into the next page. In theory every IM2 program needs all 257 bytes.

In practice, a survey of 13 commercial Spectrum 128K games shows the rule is routinely ignored. The data below was collected via SpecEmu's "Debug > Run until > Opcode > IM2" feature.

| Game | IM2 entry | I reg | Table range | Table size | Fill value | Handler |
|---|---|---|---|---|---|---|
| Where Time Stood Still | `#8529` | `#84` | `#8400`–`#8500` | **256** | `#BE` | `#BEBE` |
| 7th Reality Demo | `#6DD8` | `#63` | `#6300`–`#6400` | **256** | `#64` | `#6464` → JP `#624D` |
| La Abadia Del Crimen | `#A253` | `#BE` | `#BE00`–`#BF00` | **256** | `#BF` | `#BFBF` |
| Grand Prix Circuit | `#950C` | `#82` | `#8200`–`#8301` | **257** | `#63` | `#6363` → JP `#A07A` |
| The Addams Family | `#97D8` | `#9B` | `#9B00`–`#9BFF` | **256** | `#FD` | `#FDFD` → JP `#BA6E` |
| Chase HQ 2 | `#97D8` | `#9B` | `#9B00`–`#9BFF` | **256** | `#FD` | `#FDFD` → JP `#BA6E` |
| Robocop 2 | `#8805` | `#A4` | `#A400`–`#A500` | **256** | `#5B` | `#5B5B` → JP `#9CB4` |
| Robocop 3 | `#8221` | `#77` | `#7700`–`#7800` | **256** | `#76` | `#7676` → JP `#8225` |
| Spacegun | `#62DA` | `#BE` | `#BE00`–`#BF00` | **256** | `#BF` | `#BFBF` → JP `#64FD` |
| Total Recall | `#C008` | `#91` | `#9100`–`#9200` | **256** | `#5D` | `#5D5D` → JP `#71FF` |
| Carrier Command | `#84E2` | `#83` | `#8300`–`#8400` | **256** | `#85` | `#8585` |
| Hudson Hawk | `#D0F9` | `#80` | `#8000`–`#8100` | **256** | `#81` | `#8181` |
| NARC | `#DE21` | `#BE` | `#BE00`–`#BF00` | **256** | `#BF` | `#BFBF` → JP `#DE38` |
| Navy Seals | `#D878` | `#91` | `#9100`–`#9200` | **256** | `#5D` | `#5D5D` → JP `#6DFD` |
| Pang | `#5D69` | `#80` | `#8100`–`#8101` | **257** | `#81` | `#8181` → JP `#6286` |

### Patterns Observed

- **Only 2 of 15** entries (Pang, Grand Prix Circuit) use the correct 257-byte table
- **All 13 others** use 256 bytes
- The Addams Family and Chase HQ 2 are **identical** down to every address — Jonathan Dunn is credited in both, and clearly wrote a shared IM2 manager
- 8 of 15 use a `JP` trampoline at the handler address (e.g. `#FDFD: JP #BA6E`)
- 7 of 15 jump directly to the manager at the handler address
- All games place the table at `#80` or higher (avoiding the `#40`–`#7F` crash range)

### Why 256 Bytes "Works" on Most Hardware

The 256-byte table fails only when the floating bus returns a vector byte of `#FF`. The handler address would then be formed from `(byte at I × 256 + #FF) and (byte at I × 256 + #00)`, the second byte being outside the table.

On most emulators and on the Pentagon, the floating bus value during interrupt acknowledge is deterministic:
- **Pentagon**: always `#FF` (clean design)
- **SpecEmu, FUSE, ZEsarUX (default)**: hardcode `#FF`
- **Real 128K / +2**: usually `#FF` due to bus pull-up resistors

So the failure mode (`V = #FF` reading the wrong byte for the high half of the handler address) actually works in the programmer's favor on these machines — because the missing byte happens to be `#FF`, the handler address becomes `#FDFF` or similar, which often contains a `JP` to the real handler.

**On real 48K Spectrums**, the floating bus is less predictable. The vector byte can be the residual of the last memory or I/O cycle. A program that worked perfectly on a Pentagon may crash on a 48K Spectrum after specific instruction sequences. This is why the **257-byte table rule** is non-negotiable for portable code.

---

## Real-Game IM2 Manager Patterns

Three distinct patterns are observed in commercial IM2 code. They differ in how the handler is reached and in how much state they preserve.

### Pattern A — Direct Handler

The handler address is formed by doubling the fill byte. Code begins executing directly at that address with no indirection. Used by: Where Time Stood Still, La Abadia Del Crimen, Carrier Command, Hudson Hawk.

```z80
; I=#BE, table filled with #BF, handler at #BFBF
    ORG  #BFBF
im2_handler:
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL
    ; ... handler body ...
    POP  HL
    POP  DE
    POP  BC
    POP  AF
    EI
    RETI
```

**Pros**: fastest acknowledge, no `JP` overhead.
**Cons**: handler must be at an address where high byte = low byte.

### Pattern B — JP Trampoline

The handler address contains a 3-byte `JP` instruction that jumps to the real manager. Used by: Addams Family, Chase HQ 2, Robocop 2/3, Spacegun, Total Recall, NARC, Navy Seals, Pang, Grand Prix Circuit, 7th Reality Demo.

```z80
; I=#9B, table filled with #FD, handler at #FDFD
    ORG  #FDFD
im2_trampoline:
    JP   real_handler    ; 10T for the JP

    ORG  #BA6E           ; Anywhere in RAM
real_handler:
    PUSH AF
    ; ... body ...
    EI
    RETI
```

**Pros**: handler body can live anywhere in RAM — no high-byte=low-byte constraint.
**Cons**: costs 10 T-states per frame for the `JP`.

### Pattern C — Bank-Switching Aware (Hudson Hawk)

The most sophisticated pattern in the survey. Used by Hudson Hawk (programmer Jim Bagley). The handler saves the current RAM bank at `#C000`, switches to a known bank for the ISR's work, plays music, then restores the original bank.

Jim Bagley's description of the technique, from a comment on the disassembly survey:

> "After pushing [the registers], as this is a 128K game, we get a byte from a location in RAM `#70D4`, which is the value that the main program writes to before it changes the 16K bank at `#C000`. That way, no matter where it gets interrupted, `#70D4` will hold the 16K RAM bank that the code wants in place. [...] After it's pushed the registers, and the current 16K bank, it then sets the 16K bank at `#C000` to be bank 3, then calls a routine which handles the audio, then pops the bank and registers and returns to the main code."

The crucial insight: the main program writes the desired bank to `#70D4` **before** it issues the actual `OUT (#7FFD)` to switch banks. If an NMI or maskable interrupt fires between the write to `#70D4` and the `OUT`, the ISR can still read `#70D4` to know which bank the main program will need next.

```z80
; Simplified Hudson Hawk pattern
; Main program bank-switching routine
set_bank:
    PUSH BC
    LD   BC,#7FFD
    LD   A,(desired_bank)
    AND  #07              ; Mask to valid bank bits
    LD   C,A              ; C := new bank bits
    LD   A,(current_out)  ; Previous value written to #7FFD
    AND  #38              ; Clear bank bits
    OR   C                ; OR in new bank
    OR   #10              ; Bit 4 = ROM 0 select
    LD   (#70D4),A        ; *** Save desired value FIRST ***
    LD   (current_out),A
    OUT  (C),A            ; Then actually switch
    POP  BC
    RET

; IM2 handler
im2_handler:
    PUSH AF : PUSH BC : PUSH DE : PUSH HL
    PUSH IX : PUSH IY
    LD   A,(#70D4)        ; What bank does main want?
    PUSH AF               ; Save it
    AND  #07              ; Switch to bank 3 for audio work
    OR   #10
    OR   #08              ; Screen 1 (or whatever)
    LD   BC,#7FFD
    OUT  (C),A
    CALL play_music       ; Audio lives in bank 3
    POP  AF               ; Restore desired bank
    LD   BC,#7FFD
    OUT  (C),A
    POP  IY : POP  IX
    POP  HL : POP  DE : POP  BC : POP  AF
    EI
    RETI
```

This pattern is the canonical way to write 128K-aware interrupt handlers. The general rule:

1. Main program maintains a shadow variable containing the next desired `#7FFD` value
2. The shadow is updated **before** the `OUT` that switches banks
3. ISR reads the shadow on entry, restores it on exit
4. Because `#7FFD` is write-only, this is the only way to track bank state across interrupts

---

## Common ISR Effect Catalog

Five effect classes appear repeatedly in IM2-driven Spectrum software. Each has a typical T-state budget and constraint profile.

### Effect 1 — Per-Frame Music Player

The simplest and most universal IM2 use case. The ISR calls the music player's `PLAY` routine once per frame. The main loop is free for game logic or demo effects.

```z80
; Arkos / PT3 player pattern
im2_handler:
    PUSH AF : PUSH BC : PUSH DE : PUSH HL
    PUSH IX : PUSH IY
    EX   AF,AF'
    EXX
    PUSH AF : PUSH BC : PUSH DE : PUSH HL

    CALL PLY_AKG_PLAY      ; Advance music one frame

    POP  HL : POP  DE : POP  BC : POP  AF
    EXX
    EX   AF,AF'
    POP  IY : POP  IX
    POP  HL : POP  DE : POP  BC : POP  AF
    EI
    RETI
```

The aggressive register preservation is required because tracker players (Arkos AKG/AKM, PT3) freely use **every** register including shadow set and `IX`/`IY`. The save/restore overhead is roughly **150 T-states** before any music work happens.

For the full pattern with init, stop, and IM2 setup code, see [ay_player_routines.md](../../06_sound/players/ay_player_routines.md).

### Effect 2 — Per-Scanline Attribute Update

The ISR rewrites one attribute row per scanline, producing 8×1 multicolor. This requires cycle-counted code that finishes within the 224-T-state scanline budget. See [race_the_beam.md](race_the_beam.md) for the full technique. Here is the IM2-side framing:

```z80
im2_handler:
    PUSH AF
    ; ISR fires at scanline 0 (top border)
    ; Wait until scanline 64 (first paper line) using floating bus
.fb_wait:
    IN   A,(#FF)
    CP   #07               ; Detect specific attribute byte
    JR   NZ,.fb_wait
    ; Now beam is at scanline 64 — begin cycle-counted PUSH loop
    CALL multicolor_push_loop   ; See race_the_beam.md
    POP  AF
    EI
    RETI
```

**Critical constraint**: the entire PUSH loop runs **inside the ISR**, which means the ISR cannot return until the entire effect completes (typically 192 scanlines = ~43,000 T-states). The main loop effectively never runs. This is fine for pure demo effects but not for games.

### Effect 3 — Palette Cycling (ULAplus on FPGA Clones)

On FPGA-based clones (ZX-Uno, Sizif, Next in compatibility mode), ULAplus provides a 64-color palette. The ISR can change palette entries per frame for cycling effects:

```z80
im2_handler:
    PUSH AF
    PUSH BC
    LD   A,(pal_index)
    INC  A
    AND  #3F
    LD   (pal_index),A
    LD   B,A
    LD   A,#55             ; ULAplus palette register port
    OUT  (C),A             ; Write palette index
    LD   BC,#BF3B
    LD   A,(pal_data_offset)
    INC  A
    LD   (pal_data_offset),A
    LD   HL,palette_data
    LD   L,A
    LD   A,(HL)
    OUT  (C),A             ; Write color
    POP  BC
    POP  AF
    EI
    RETI
```

This costs ~80 T-states per frame — negligible compared to the 70,000 T-state budget.

### Effect 4 — Per-Line Border Effects

Changing border color at specific scanlines produces raster bars. Cheaper than full multicolor because border writes use only `OUT (#FE),A` and have no contention:

```z80
im2_handler:
    PUSH AF
    LD   A,#02             ; Red border
    OUT  (#FE),A
    LD   B,80              ; ~12 scanlines
.d1: NOP : NOP : NOP : NOP : NOP : NOP
    DJNZ .d1
    LD   A,#06             ; Yellow border
    OUT  (#FE),A
    LD   B,80
.d2: NOP : NOP : NOP : NOP : NOP : NOP
    DJNZ .d2
    LD   A,#04             ; Green border
    OUT  (#FE),A
    POP  AF
    EI
    RETI
```

See [border_effects.md](../05_display_and_timing/border_effects.md) for the full technique.

### Effect 5 — Multi-Effect Dispatcher

A single ISR can run different effects on different frames by modulating on a frame counter:

```z80
frame_cnt:    DW  0
im2_handler:
    PUSH AF
    PUSH HL

    ; Always: increment frame counter
    LD   HL,(frame_cnt)
    INC  HL
    LD   (frame_cnt),HL

    ; Always: music
    CALL play_music

    ; Frame-mod dispatch
    LD   A,L
    AND  #07               ; 8-frame cycle
    JP   Z,do_palette
    CP   1
    JP   Z,do_sprite_update
    CP   2
    JP   Z,do_border
    ; ... frames 3-7 fall through
.default:
    POP  HL
    POP  AF
    EI
    RETI
```

This pattern spreads heavy work across multiple frames so each ISR invocation stays within budget.

---

## Demo Framework Patterns

Demos are organized as a sequence of effects. The IM2 ISR plays multiple roles: timing the effect transitions, advancing music, and driving per-effect raster work.

### Effect Sequencer

```z80
effect_table:
    DW   effect1_init, effect1_frame, 500    ; Effect 1: 500 frames (~10s)
    DW   effect2_init, effect2_frame, 250    ; Effect 2: 250 frames (~5s)
    DW   effect3_init, effect3_frame, 1000   ; Effect 3: 1000 frames (~20s)
    DW   0                                  ; End

current_effect:  DW effect_table
frame_in_effect: DW 0

main_loop:
    LD   HL,(current_effect)
    LD   A,(HL)            ; Check for end marker
    OR   A
    JR   Z,demo_done

    ; Init effect if at frame 0
    LD   DE,(frame_in_effect)
    LD   A,D
    OR   E
    JR   NZ,.skip_init
    INC  HL               ; HL now points at init routine address
    LD   E,(HL) : INC  HL
    LD   D,(HL) : INC  HL  ; DE = init routine
    PUSH DE
    RET                   ; Call init
.skip_init:
    INC  HL : INC  HL      ; Skip past init address

    ; Call frame routine
    LD   E,(HL) : INC  HL
    LD   D,(HL) : INC  HL
    PUSH DE
    RET

    ; HALT and wait for next frame
    HALT

    ; Increment frame counter
    LD   HL,(frame_in_effect)
    INC  HL
    LD   (frame_in_effect),HL

    ; Check duration
    LD   E,(HL) : INC  HL
    LD   D,(HL) : INC  HL  ; DE = duration
    PUSH HL
    LD   HL,(frame_in_effect)
    OR   A
    SBC  HL,DE
    POP  HL
    JR   C,.same_effect

    ; Advance to next effect
    LD   (current_effect),HL
    LD   HL,0
    LD   (frame_in_effect),HL
.same_effect:
    JR   main_loop

demo_done:
    RET
```

The ISR is responsible only for advancing the music. All effect work happens in the main loop, which `HALT`s once per frame to sync with the ISR.

### Transition Techniques

| Transition | T-state cost | Visual effect |
|---|---|---|
| Hard cut (no transition) | 0 | Instant swap |
| Fade to black | ~2000 per frame × 16 frames | Gradual dim |
| Wipe (left-to-right) | ~5000 per frame × 32 frames | Sliding reveal |
| Crossfade (needs 128K) | ~3000 per frame × 16 frames | Smooth blend via bank switch |

See [race_the_beam.md](race_the_beam.md) for raster-effect-specific transitions.

---

## IM2 Setup Code Generators

The setup is identical across projects: pick a fill byte, fill 257 bytes, set I, set IM 2. The macros below parameterize this for the two most common assemblers.

### SjASMPlus Macro

```text
; im2_setup.asm — SjASMPlus
; Usage:  IM2_SETUP #FE, #90
;        (table at #FE00-#FF00, handler at #9090)

    MACRO IM2_SETUP table_page, handler_byte
        DI
        LD   A, table_page
        LD   I, A
        LD   HL, table_page * 256
        LD   (HL), handler_byte
        LD   DE, table_page * 256 + 1
        LD   BC, #0100
        LDIR
        IM   2
        EI
    ENDM
```

### z88dk / sccz80 Assembly (z88dk-z80asm)

```text
; im2_setup.z80asm — z88dk-z80asm syntax
; Usage: pass table_page and handler_byte as DEFC

    MACRO IM2_SETUP table_page, handler_byte
        di
        ld   a, table_page
        ld   i, a
        ld   hl, table_page * 256
        ld   (hl), handler_byte
        ld   de, table_page * 256 + 1
        ld   bc, 256
        ldir
        im   2
        ei
    ENDM
```

### Verification Snippet

After IM2 setup, verify the table by reading two adjacent bytes:

```z80
    LD   A,(#FE00)         ; Should equal fill byte
    CP   #90
    JR   NZ,.bad_table
    LD   A,(#FF00)          ; 257th byte (handles V=#FF case)
    CP   #90
    JR   NZ,.bad_table
    ; Table is correct
```

If the 257th byte is wrong, the program will crash the first time the floating bus returns `#FF` as the vector byte.

---

## Cross-References

- **[interrupt_programming.md](interrupt_programming.md)** — Foundational IM2 mechanics, 257-byte table rule, floating-bus problem
- **[race_the_beam.md](race_the_beam.md)** — Per-scanline multicolor technique in depth
- **[nmi.md](nmi.md)** — NMI handler patterns; same register-preservation rules
- **[im2_advanced.md](im2_advanced.md)** — Next/TS-Conf hardware IM2 multi-vector mode, bank-switching deep dive
- **[ay_player_routines.md](../../06_sound/players/ay_player_routines.md)** — Music player ISR integration, Arkos / PT3 patterns
- **[border_effects.md](../05_display_and_timing/border_effects.md)** — Per-line border effects from ISR
- **[contention_model.md](../03_memory_and_io/contention_model.md)** — Why #4000-#7FFF crashes for vector tables
- **[bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md)** — 128K paging in ISR context

## Sources

- *Disassemble Interrupt Mode on some popular ZX Spectrum 128k Games* (andydansby, zxspectrumcoding.wordpress.com, 2021) — 13-game IM2 disassembly survey with addresses, I register values, and table sizes
- *Compatibility: An open letter to the Russian scene* (Gasman, Subliminal Extacy #3, zxpress.ru) — canonical statement on `#40`–`#7F` IM2 table crash and the cross-platform portability plea
- *Jim Bagley comment on Hudson Hawk IM2 manager* (via zxspectrumcoding.wordpress.com, 2021) — first-person description of the `#70D4` bank-shadow technique
- *Interrupts - SpecNext Wiki* (wiki.specnext.dev) — Next hardware IM2 mode reference
- *Arkos Tracker — Using interruption player on ZX Spectrum* (julien-nevo.com) — Arkos AKG IM2 setup code by Gusman
