[← Home](../../README.md) · [Original Hardware](README.md)

# Keyboard Matrix — The 8×5 Membrane, Half-Row Scanning, Ghosting, and Game Input Patterns

## Overview

The ZX Spectrum keyboard has **no controller, no encoder chip, no interrupt, and no buffer in hardware**. It is a passive grid of 40 membrane switches — 8 rows by 5 columns — wired so that the rows hang off the CPU's own address bus and the columns feed five inputs on the ULA. Every key press ever registered on a Spectrum was detected by software asking, one half-row at a time: "is anything connected right now?"

This arrangement is the keyboard equivalent of the beeper: Sinclair moved an entire subsystem into software to save a few dollars of silicon. The consequences shape every Spectrum program that takes input. Reading the keyboard costs CPU time on every frame. Pressing certain three-key combinations **invents a phantom fourth key**, because the matrix has no anti-ghosting diodes — which is why a generation of games converged on the same QAOP-and-Space control schemes. And because the row select lives on address lines A8–A15, a keyboard read is just an `IN` from a carefully chosen port — fast, simple, and dangerously easy to get subtly wrong.

This article covers the matrix as hardware and as a programming target: the electrical structure, the scanning algorithms, ghosting mechanics, joystick adapters that piggyback on the matrix, and the clone-era extensions. For the ULA-side view (column inputs, internal pull-ups, port `#FE` bit layout) see [ULA Architecture](ula_architecture.md); for the ROM's keyboard routines see [48K ROM](../../04_operating_systems/rom_48k.md#keyboard-input); for port-level usage in context see [48K Memory & I/O](../../05_development/03_memory_and_io/memory_and_io_48k.md#keyboard-reading).

---

## The Physical Matrix

The keyboard is two layers of printed membrane separated by a spacer with holes at each switch position. Pressing a key pushes the top layer's contact through the hole onto the bottom layer's contact, closing one intersection of the grid. Two ribbon tails leave the membrane:

| Connector | Width | Carries | Destination |
|---|---|---|---|
| Rows | 8-way | Row selects KRA0–KRA7 | Address lines A8–A15 (through diodes) |
| Columns | 5-way | Column returns KRC0–KRC4 | ULA keyboard inputs (internal pull-ups) |

Each intersection is one switch:

```
        A8 ───[D]───┬────────●────────●─── ...   (row 0: CAPS..V)
                    |        |        |
        A9 ───[D]───┼────────●────────●─── ...   (row 1: A S D F G)
                    |        |        |
                   ...      (40 intersections total)
                    |        |        |
        A15 ──[D]───┴────────●────────●─── ...   (row 7: SPACE..B)
                             |        |
                          KRC0     KRC1 ... KRC4  → ULA bits D0..D4
```

Three electrical facts explain everything the software sees:

1. **The rows are driven by address lines.** During `IN A,(C)`, the Z80 puts BC on A0–A15. Making A8 low drives row 0 low; the other rows stay high. The diodes (D15–D22 on the schematic) prevent two simultaneously-low address lines from shorting each other through the matrix.
2. **The columns idle high.** The ULA's five keyboard inputs have internal pull-ups. An open switch reads as 1; a closed switch connects the column to the low row and reads as **0**. Keyboard data is active-low — `0 = pressed`.
3. **There are no diodes per key.** The only diodes are on the row drivers. This is what makes ghosting possible — see the dedicated section below.

The membrane tails are the machine's most fragile component: they crack at the connector fold with age, killing whole rows or columns. A dead row in hardware looks exactly like keys that never respond in software — worth remembering before blaming your scanning code on real machines.

---

## How a Read Works

A keyboard read is an I/O read where the **high byte of the port address selects the row** and **A0=0 selects the ULA**:

```z80
        ld      bc, #F7FE       ; B = #F7 → A11 low = row 3 (1 2 3 4 5)
                                ; C = #FE → A0 low = ULA port
        in      a, (c)          ; A8-A15 drive rows; columns return in bits 0-4
        bit     0, a            ; key "1" pressed? (bit clear = yes)
        jr      z, pressed_one
```

During the `IN`, three things happen in one bus cycle: the address bus drives exactly the rows whose address bits are low, each closed switch pulls its column down to its row's level, and the ULA's input mux places the five column levels on data bits D0–D4 (with EAR on D6 and fixed 1s on D5/D7). The mechanics of the port itself — decoding, bit layout, contended I/O timing — are documented in [ULA Architecture](ula_architecture.md#port-fe-internals--one-register-five-jobs).

Two addressing subtleties:

- **`IN A,(C)` is the only correct form for row selection.** `IN A,(n)` ignores B entirely and puts the *accumulator* on A8–A15 — see Pitfall 2.
- **More than one row line may be low.** `IN` from `#00FE` pulls all eight rows low, and the columns read the **AND of all rows** — any pressed key anywhere pulls its column to 0. This is the standard "any key pressed?" probe, but it also drives every other device that decodes any of those address lines — see Pitfall 4.

---

## The Full Matrix Map

All 40 intersections, by port high byte and returned bit. Remember: **bit clear = pressed**.

| Port | Row line | Bit 0 | Bit 1 | Bit 2 | Bit 3 | Bit 4 |
|---|---|---|---|---|---|---|
| `#FEFE` | A8 | CAPS SHIFT | Z | X | C | V |
| `#FDFE` | A9 | A | S | D | F | G |
| `#FBFE` | A10 | Q | W | E | R | T |
| `#F7FE` | A11 | 1 | 2 | 3 | 4 | 5 |
| `#EFFE` | A12 | 0 | 9 | 8 | 7 | 6 |
| `#DFFE` | A13 | P | O | I | U | Y |
| `#BFFE` | A14 | ENTER | L | K | J | H |
| `#7FFE` | A15 | SPACE | SYMBOL SHIFT | M | N | B |

Structural observations that matter for input code:

- **CAPS SHIFT and SYMBOL SHIFT are just keys** — row 0 bit 0 and row 7 bit 1. The ROM interprets them; hardware treats them identically to any other key. Your own scanner can use them as two free extra buttons (many games use CAPS SHIFT as fire).
- **The digit row is split across two half-rows**: 1–5 on A11, 6–0 on A12, mirrored in order (bit 0 = 1 vs bit 0 = 0). Converting a pressed digit to its value requires knowing which half-row it came from.
- **The matrix favors the left hand.** QAOP spans rows A10–A13 in one neat column (bit 0 of each); that is why it became the default direction cluster — see the ghosting section for the electrical reason it works so well.

### What the shifts produce (ROM-level)

The matrix knows nothing about these — the ROM's keyboard routine builds them from simultaneous key detection. Useful for reference when writing your own text input:

| Combination | Result |
|---|---|
| CAPS + letter | Uppercase letter |
| CAPS + 1 / 2 / 3 / 4 | EDIT / CAPS LOCK / TRUE VIDEO / INV VIDEO |
| CAPS + 5 / 6 / 7 / 8 | Cursor left / down / up / right |
| CAPS + 9 / 0 | GRAPHICS / DELETE |
| CAPS + SPACE | **BREAK** (also triggers the ROM's break check during tape ops) |
| SYM + 1..0 | `! @ # $ % & ' ( ) _` |
| SYM + P / O / I / U / Y | `" ;` ... (punctuation set) |
| SYM + letter | Extended graphics/symbol characters |

### ROM Keyboard Modes and Tokenization

The matrix itself is completely dumb, but the ROM builds a complex state machine on top of it to handle Sinclair BASIC's famous single-key tokenization. The current input state is indicated by a flashing cursor letter, which dictates how the ROM interprets the next keypress:

- **K (Keywords)**: The default mode at the start of a line or after `THEN` / `:`. Unshifted letter keys produce whole BASIC keywords (e.g., `P` produces `PRINT`).
- **L (Letters)**: Active inside strings or when the ROM expects a variable name. Unshifted letters produce lowercase characters.
- **C (Capitals)**: A variant of L mode where letters default to uppercase. Toggled by pressing CAPS LOCK (CAPS SHIFT + 2).
- **E (Extended)**: Entered by pressing both CAPS SHIFT and SYMBOL SHIFT together. The cursor changes to E, and the next keypress produces an extended keyword (green text above the keys on the 48K) or symbol (red text below).
- **G (Graphics)**: Toggled by GRAPHICS (CAPS SHIFT + 9). Letter keys produce user-defined graphics (UDGs), and digits 1–8 produce block mosaic characters.

These modes are strictly a software construct of the `KEYBOARD` routine (`#02BF`); games bypassing the ROM ignore them entirely. See [48K ROM — Keyboard Input](../../04_operating_systems/rom_48k.md#keyboard-input) for implementation details.

---

## Scanning Algorithms

### Full-matrix scan

The canonical full scan: iterate all eight half-rows, collect each row's five bits into an 8-byte buffer. Called once per frame from the interrupt handler or the main loop.

```z80
; scan_keyboard — fill key_buf[8] with raw matrix state
; In:  nothing          Out: key_buf[0..7] = rows A8..A15 (bit clear = pressed)
; Clobbers: AF, BC, DE, HL. ~160 T-states + contention.
scan_keyboard:
        ld      hl, key_buf
        ld      b, #FE          ; first row select: A8 low
.next_row:
        ld      c, #FE          ; A0 low → ULA
        in      a, (c)          ; 12 T — read half-row
        and     #1F             ; keep key bits, drop EAR/unused (Pitfall 1)
        ld      (hl), a
        inc     hl
        rlc     b               ; next row: #FE→#FD→#FB→#F7→#EF→#DF→#BF→#7F
        jr      c, .next_row    ; bit 0 fell off after 8 iterations → done
        ret

key_buf: defs 8
```

The `RLC B` trick generates the row sequence `#FE #FD #FB #F7 #EF #DF #BF #7F` in order and terminates via carry after eight rows — no counter needed.

### The "any key" probe

Pull all rows low at once and test the AND of the whole matrix:

```z80
        ld      bc, #00FE       ; ALL row lines low
        in      a, (c)
        and     #1F
        cp      #1F             ; Z = nothing pressed anywhere
        jr      z, no_key
```

Seven T-states of setup for a whole-keyboard answer. Use it for "press any key" screens and to skip the full scan on idle frames. Note the port arithmetic that makes this safe: the low byte `#FE` keeps A1–A7 high, so no other peripheral (Kempston decodes A5=0, 128K paging decodes A1=0, AY decodes A1=0 with A15=1) is selected — only the ULA sees A0=0, and the zero *high* byte is what pulls all eight rows low. The dangerous variant is probing with a low byte other than `#FE` (say `#0000`): that asserts A1–A7 as well and can put the Kempston interface and the ULA on the data bus at the same time. See Pitfall 4.

### Debounce and repeat — hardware gives you nothing

The membrane bounces for a frame or two; the ROM hides this with its `KSTATE` state machine (see [System Variables](../../04_operating_systems/system_variables.md)). For your own scanner, the standard frame-synchronous approach:

- **Edge detection** — keep the previous frame's buffer; `pressed = ~prev AND cur`. One event per physical press, immune to bounce longer than a frame.
- **Repeat delay** — for menus/text: act on press immediately, then again after N held frames (N≈25 for first repeat, 3–5 for subsequent). Track a per-key hold counter or a single "last key + timer" pair.

### ROM scanner vs direct reads

| Criterion | ROM (`LAST_K` / `KEYBOARD` #02BF) | Own scanner |
|---|---|---|
| Setup cost | Zero — IM 1 handler updates `LAST_K` every frame | Write and debug the scan |
| Multi-key simultaneous | **No** — one key + shifts at a time | Yes — full 40-key state |
| Repeat/debounce | Built in (KSTATE, REPDEL/REPPER) | You implement it |
| Overhead per frame | ROM does work you may not need (click, decoding) | Pay only for what you read (~160 T) |
| Break key handling | Automatic CAPS+SPACE → error | You must handle/ignore deliberately |
| Suitable for | Menus, text entry, BASIC coexistence | Games, demos, anything real-time |

**Rule of thumb:** text and menus — let the ROM do it. Anything where two keys can be down at once (which is every action game ever) — scan the matrix yourself. Reading `LAST_K` from machine code is documented in [System Variables](../../04_operating_systems/system_variables.md) with a ready-made snippet.

---

## Ghosting — The Phantom Fourth Key

The matrix has diodes on the row drivers only — the switches themselves are naked intersections. Press **three keys that form three corners of a rectangle** in the grid, and current finds a sneaker path through them that makes the **fourth corner read as pressed**:

```
              KRC1 (bit1)      KRC2 (bit2)
A9 row  ──────■ A(S pressed)─────● D ──────
                  │                │
A10 row ──────■ Q(pressed)─────■ W(pressed)
                  │
                 A11 row low during scan...
```

With Q, W, and S held, scanning row A9 finds column 2 pulled low *through W → row A10 → Q → column 1 → S* — the machine reports **D** as pressed even though nobody touched it. (The exact columns/rows above are illustrative; any rectangle in the grid behaves this way.)

Practical consequences:

- **Two-key combos are always safe.** Ghosting needs three simultaneous keys. Menus and typing never see it; action games live in it.
- **Keys in the same row or same column never ghost.** A rectangle needs two rows *and* two columns.
- This is why the classic control clusters look the way they do. **Q/A/O/P + M/Space**: A and Q share column 0; O and P share one row; M and Space share another. Pick any three — they never complete a rectangle, so no phantom direction or fire appears mid-game. Joystick-to-keyboard adapters (below) were designed to the same rule.

Design guidance for your own control schemes:

| Rule | Reason |
|---|---|
| Keep directions in one column + one row pair (QA/OP) | No rectangle with fire keys |
| Put fire on SPACE row or CAPS row | Column 0 of A15/A8 rows rectangles only with keys games rarely combine |
| If you allow 3+ simultaneous arbitrary keys, accept ghosts | Or reject the third key: if a full-column-and-row pattern appears, drop the newest input |

## Joysticks on the Matrix

Most Spectrum joysticks are not devices at all — they are **five switches wired to look like key presses**, either literally (Sinclair's joystick interface shorts matrix lines directly) or by convention (Cursor interfaces map onto specific keys). Games read them with the same `IN` code as the keyboard. For the port-based standards (Kempston, Fuller, Timex) and a unified multi-standard reader, see [Joystick Interfaces](../../03_io/peripherals/joystick.md).

### Naming: Interface 2, not Interface 1

A persistent source of confusion, worth settling explicitly:

- **Sinclair Interface 1** = Microdrive, RS-232, and ZX Network unit. **No joystick ports.**
- **Sinclair Interface 2** = ROM cartridge slot + **two DE-9 joystick ports**, wired passively into the keyboard matrix.
- Game menus offering **"SINCLAIR 1" and "SINCLAIR 2"** mean *Interface 2, port 1* and *Interface 2, port 2* — the numbering refers to the joystick port, not the interface model.

### The Sinclair key mappings

Interface 2 connects each joystick line straight across a matrix intersection — no electronics, just switches. Port 1 lands on the 6–0 row, port 2 on the 1–5 row:

| Standard | Row (port) | Left | Right | Down | Up | Fire |
|---|---|---|---|---|---|---|
| **Sinclair 1** (Interface 2, port 1) | A12 (`#EFFE`) | 6 (bit 4) | 7 (bit 3) | 8 (bit 2) | 9 (bit 1) | 0 (bit 0) |
| **Sinclair 2** (Interface 2, port 2) | A11 (`#F7FE`) | 1 (bit 0) | 2 (bit 1) | 3 (bit 2) | 4 (bit 3) | 5 (bit 4) |
| **Cursor / Protek / AGF** | A11+A12 | 5 | 8 | 6 | 7 | 0 |

Because the "keys" are ordinary matrix intersections, **any keyboard becomes a dual Sinclair joystick for free** — pressing 6–0 and 1–5 rows with fingers is indistinguishable from two Interface 2 sticks.

### The dual-joystick setup: 6–0 and 1–5

The two Sinclair rows are **adjacent half-rows**, which made them the standard answer for two-player simultaneous play:

- **Two players, one Interface 2** — stick 1 on 6–0, stick 2 on 1–5.
- **Two players, one keyboard** — player 1 on 6 7 8 9 0, player 2 on 1 2 3 4 5, no hardware at all.
- **Single-player dual-stick** — a few games read both rows for one player (move + aim independently).

The code is trivially symmetric — two `IN`s, one per player:

```z80
        ld      bc, #EFFE       ; player 1: row 6 7 8 9 0
        in      a, (c)          ; bit 4=left .. bit 0=fire
        ld      (p1_raw), a
        ld      bc, #F7FE       ; player 2: row 1 2 3 4 5
        in      a, (c)          ; bit 0=left .. bit 4=fire (mirrored!)
        ld      (p2_raw), a
```

Note the **mirrored bit order**: player 1's directions run bit 4→bit 0, player 2's run bit 0→bit 4. Table-driven decoding (like the redefinable-keys example below) absorbs this for free; hardcoded bit tests must not assume both sticks look alike. The rows also ghost against each other — 6, 1, and 2 pressed simultaneously phantoms 7 — which two-joystick games simply lived with.

### Conventions vs hardware

- **Sinclair 1 fits in a single half-row** (`#EFFE`) — one `IN` reads the whole stick, which is part of why it was popular with developers.
- The Cursor layout deliberately straddles the two digit rows; combined with keyboard directions it avoids rectangles for the common 3-key cases.
- **Kempston is the odd one out**: a real hardware port (`#1F`, active-high bits — the polarity opposite of the matrix) with no CPU-side row driving at all. It costs an interface but frees the keyboard entirely. Full coverage in [Joystick Interfaces](../../03_io/peripherals/joystick.md) and [I/O Port Map](../../10_references/io_port_map.md).
- Because these are conventions, **always offer redefinable keys** — there is no way to probe which adapter is attached, and players still argue about which Sinclair mapping is "correct."

---

## How Games Use the Keyboard — Typical Keysets

Decades of Spectrum software converged on a small set of conventions. These are **tendencies, not rules** — individual games deviate constantly, which is exactly why redefinable keys became the norm — but the patterns below cover the vast majority of titles.

### Common patterns across all games

- **One direction cluster + one fire key**, scanned as 4–6 individual keys, not the ROM's single-key `LAST_K`.
- **Keyboard and joystick active simultaneously** — no mode switching; both are just matrix reads merged into the same bitfield.
- **Secondary functions on memorable keys**: H = pause/hold, M = music on/off, ENTER = start/confirm, SPACE = select. Symbol Shift occasionally serves as a second fire.
- **"Redefine keys" menu** storing (row, mask) pairs — the table-driven pattern in the example below.

### By game type

| Genre | Typical keyset | Notes |
|---|---|---|
| Platform / run-and-gun | **QAOP + SPACE or M** (fire) | The canonical layout; CAPS SHIFT often a second action |
| Isometric adventure (Filmation-style) | 5 keys: rotate L / rotate R / forward / jump / pick-up | Directions rotate the character rather than move it; keys chosen adjacent (e.g. ZXAS + SPACE variants) |
| Racing | Z/X or QA steer + accelerate/brake (P/ENTER or bottom row) | Two hands on the bottom rows; fire rarely needed |
| Shoot-'em-up (vertical/horizontal) | QAOP + fire; R-Type-likes add a second key for charge/force | Auto-fire common, so fire reads `state` not `edge` |
| Beat-'em-up | QAOP + 2–3 attack keys on nearby bottom-row keys | Attacks on M/N/B/SYMBOL SHIFT keep one hand on QAOP |
| Twin-stick / multi-direction fire | Move cluster + second cluster for fire direction | Often Sinclair 1 + Sinclair 2 rows, or QAOP + bottom row |
| Flight / vehicle sim | Wide spread: throttle, flaps, gear on digit rows; stick on QAOP | Full keyboard use, closest thing to "simulator UI" on the machine |
| Text / graphic adventure | Full 40-key input via ROM (`LAST_K`) | The ROM scanner's home turf; multi-key irrelevant |
| Sports (multi-event) | "Waggling": alternate two keys rapidly (Z/X or N/M) | Decathlon-likes measure alternation rate per frame |

### By country / scene

Regional habits grew out of which hardware was common and which publishers dominated. Treat these as folklore-grade generalizations — useful for defaults in a "redefine keys" menu, not as laws.

| Scene | Dominant input culture | Typical defaults |
|---|---|---|
| **UK** | QAOP+SPACE canonized early by major publishers; Kempston the most popular add-on; Interface 2 pricier and rarer | QAOP+SPACE, redefine common |
| **Spain** | Strongly keyboard-centric; Dinamic/Topo/Erbe titles shipped keyboard-first with joystick as an option | OPQA + SPACE or M; "teclado redefinible" frequent; cursor-key defaults not unusual |
| **USSR / post-Soviet** | Early clones often had **no joystick port at all** — keyboard was the only input; later Pentagon/Scorpion boards built Kempston in, making it the clone-era standard | QAOP+SPACE defaults, redefinable keys near-universal; Sinclair-row two-player common on shared keyboards |
| **Poland / Czechoslovakia** | Mixed UK/Soviet influence; Kempston widespread on local hardware | QAOP+SPACE, Kempston, redefine |

The practical lesson for a new game: ship **QAOP+SPACE as the default**, support **Kempston + both Sinclair rows + Cursor** as presets, and make redefinition a first-class menu item — that combination satisfies every scene above.

---

## Game Input Patterns — A Complete Example

Real games don't scan all 40 keys per frame — they read only the half-rows their controls live on, pack the results into a bitfield, and edge-detect the fire button. This complete example implements QAOP + Space with **redefinable keys** (the industry-standard table-driven approach) and runs in ~200 T-states per frame.

```z80
; game_input.asm — redefinable multi-key input for games
; Controls default to Q/A/O/P/Space. Assemble: sjasmplus game_input.asm

        org     #8000

; ---- Key definition table: 5 entries × 2 bytes ----
; Byte 0 = port high byte (row select), byte 1 = bit mask (1 = the key's bit)
key_up:     db  #FB, %00001     ; Q   (row A10, bit 0)
key_down:   db  #FD, %00001     ; A   (row A9,  bit 0)
key_left:   db  #DF, %00010     ; O   (row A13, bit 1)
key_right:  db  #DF, %00001     ; P   (row A13, bit 0)
key_fire:   db  #7F, %00001     ; SPC (row A15, bit 0)

; ---- Result bitfield (1 = active this frame) ----
IN_UP    equ 0
IN_DOWN  equ 1
IN_LEFT  equ 2
IN_RIGHT equ 3
IN_FIRE  equ 4
input_state:  db 0              ; current frame
input_edge:   db 0              ; newly pressed this frame
input_prev:   db 0

; ---- read_input: scan the 5 defined keys, build bitfield + edges ----
; Clobbers AF, BC, DE, HL. ~200 T + contention.
read_input:
        ld      hl, key_up      ; walk the definition table
        ld      de, 1           ; E = running result-bit mask, D = 0 (state)
        ld      b, 5            ; 5 keys
.next_key:
        ld      a, (hl)         ; row-select high byte
        inc     hl              ; HL now points at the bit mask
        ld      c, #FE
        push    bc              ; save DJNZ counter
        ld      b, a
        in      a, (c)          ; read half-row — bit CLEAR = pressed
        pop     bc
        and     (hl)            ; isolate this key's bit → Z if pressed
        inc     hl
        jr      nz, .not_pressed
        ld      a, d
        or      e
        ld      d, a            ; set this key's result bit
.not_pressed:
        rlc     e               ; next result bit: 1,2,4,8,16
        djnz    .next_key
        ; D = state bitfield. Edges: pressed now AND not pressed last frame.
        ld      a, (input_prev)
        cpl
        and     d
        ld      (input_edge), a
        ld      a, d
        ld      (input_state), a
        ld      (input_prev), a
        ret
```

Usage in the game loop:

```z80
        call    read_input
        ld      a, (input_state)
        bit     IN_LEFT, a
        call    nz, move_left
        bit     IN_RIGHT, a
        call    nz, move_right
        ld      a, (input_edge)
        bit     IN_FIRE, a
        call    nz, fire_weapon     ; exactly once per press
```

What this pattern buys you:

1. **Redefinition for free** — the "redefine keys" menu just rewrites five (port, mask) pairs. Sinclair/Cursor joystick support is a different five-byte table, not different code.
2. **Simultaneous multi-key** — diagonal movement + fire works because every key is tested independently. The ROM scanner cannot do this at all.
3. **Edge detection separates held directions from single-shot fire** — the standard split: movement reads `input_state`, triggers read `input_edge`.
4. **Predictable cost** — five `IN`s ≈ 200 T-states including loop overhead, versus ~160 for a full scan of rows you don't use. Read only what you test.

> [!WARNING]
> **Requires contended I/O awareness.** These `IN`s hit the ULA and stretch on real 48K hardware during the paper area. For a game loop this only adds harmless per-frame jitter; for a raster-timed effect, never poll the keyboard mid-effect — scan during the vertical blank and reuse the result. See [Contention Model](../../05_development/03_memory_and_io/contention_model.md).

---

## The Spectrum+ and 128K Extended Keyboard

When Sinclair released the ZX Spectrum+ (and subsequently the 128K "Toastrack" and Amstrad's +2 / +3 models), the rubber keys were replaced with a hard-plastic cap QWERTY keyboard featuring dedicated keys for `DELETE`, `EDIT`, cursor arrows, and punctuation (like `"` and `;`). 

However, the ULA and the ROM's scanning routine were **not changed**. The 8×5 matrix remained exactly the same. To support the new keys without breaking backward compatibility, Sinclair used a clever hardware hack: the new membrane featured a multi-layer trace design. When you press the dedicated `DELETE` key on a Spectrum+, the physical membrane mechanically shorts **two separate matrix intersections at once** — CAPS SHIFT (Row A8, Bit 0) and 0 (Row A12, Bit 0). 

The ROM simply sees two keys being held down, exactly as if a user on a rubber-key 48K had pressed them simultaneously. This macro-injection applies to all the extended keys:
- `DELETE` = CAPS SHIFT + 0
- `EDIT` = CAPS SHIFT + 1
- `"` (Quote) = SYMBOL SHIFT + P
- `TRUE VIDEO` = CAPS SHIFT + 3
- **Cursor Arrows** = CAPS SHIFT + 5, 6, 7, 8

Because this extension is entirely mechanical, scanning algorithms that rely on the classic 8×5 matrix work perfectly on every 8-bit Sinclair model. The only downside is that pressing these macro keys during a game that scans multiple rows can trigger unexpected ghosting if other keys are also held.

---

## Track Applicability

The 8×5 matrix survived every clone and every modern reimplementation, because all software depends on it: **write to the 8×5 matrix and you run everywhere**. The physical side, however, diverged — Soviet clones extended the matrix (8×6/8×7), replaced the membrane with full-travel keyboards, and eventually injected PS/2 input into the matrix lines; the ZX Spectrum Next decodes PS/2/USB keyboards onto the standard matrix in FPGA. The programming model in *this* article applies unchanged on all three tracks.

## Historical Context

| Platform | Keyboard hardware | Scanning done by |
|---|---|---|
| **ZX Spectrum** | Passive 8×5 membrane on CPU address bus + ULA | The Z80, in software, every frame |
| **Commodore 64** | 8×8 matrix on CIA#1 ports | 6510 via CIA, KERNAL IRQ routine |
| **BBC Micro** | Matrix with 74LS163/7445 + system VIA, semi-autonomous | Hardware scans; 6502 reads results |
| **MSX** | Matrix on PPI (8255) | Z80 via PPI, BIOS interrupt routine |
| **Amstrad CPC** | Matrix on AY-3-8912's I/O port | Z80 via PSG registers |

Sinclair's approach was the cheapest of the generation: everyone else at least bolted the matrix to a parallel-port chip; the Spectrum wired it straight to the address bus and billed the Z80 for everything. The hidden cost — CPU time per frame, ghosting pushed onto game designers — was real but small, and it bought the £125 price point. In the Soviet Union it had a second virtue: the membrane and two connectors were trivially reproducible, and when membranes wore out, entire workshops manufactured replacements.

## Modern Analogies

| Spectrum keyboard concept | Modern equivalent |
|---|---|
| 8×5 matrix on the address bus | GPIO matrix scanning on a microcontroller (exactly how mechanical-keyboard firmware like QMK works) |
| Half-row `IN` read | Driving row GPIOs low and reading column GPIOs |
| Active-low, bit-clear = pressed | Pull-ups + short-to-ground switches — the standard MCU pattern |
| Ghosting, no per-key diodes | The reason modern mechanical keyboards advertise "NKRO" and per-key diodes |
| ROM `LAST_K` + debounce | USB HID report with boot-protocol state |
| Redefinable (port, mask) table | Keymap layers in keyboard firmware |

---

## Pitfalls & Common Mistakes

### Pitfall 1 — Forgetting to Mask Off Non-Keyboard Bits

```z80
        in      a, (#FE)
        cp      #FF             ; BAD: bit 6 is EAR, bits 5/7 are unused
        jr      z, no_key
```

**Why it fails:** only bits 0–4 are keys. Bit 6 follows the EAR input, whose idle state differs between ULA revisions (see [ULA Architecture — Pitfalls](ula_architecture.md#pitfall-1--the-unmasked-keyboard-read)); bits 5 and 7 read as 1. Whole-byte comparisons break on real machines.

**Correct:** `and #1F` after every read, compare against `#1F`.

### Pitfall 2 — `IN A,(n)` When You Meant `IN A,(C)`

```z80
        ld      b, #7F          ; want SPACE row
        in      a, (#FE)        ; BAD: B is ignored; A goes on A8-A15
```

**Why it fails:** the immediate-port form of `IN` puts the *accumulator* on the high address byte. Your row select in B never reaches the bus; the rows actually driven depend on leftover A contents — often reading an unintended AND of rows that changes with program state. It assembles fine and "mostly works" in emulators where A happens to be benign, which makes it a vicious bug to find.

**Correct:** `ld bc, #7FFE` / `in a, (c)`.

### Pitfall 3 — Testing for Bit Set = Pressed

```z80
        in      a, (c)
        bit     0, a
        call    nz, jump        ; BAD: matrix is active-low
```

**Why it fails:** the ULA's pull-ups make idle columns read 1; a pressed key pulls its column to the low row and reads **0**. Code written "bit set = pressed" fires continuously and stops when the key is actually hit.

**Correct:** `bit 0,a` / `call z, ...` — or invert once after the read (`cpl; and mask`) if set-bits-pressed reads better in the rest of the code, as the game example does.

### Pitfall 4 — The Sloppy "Any Key" Probe

```z80
        ld      bc, #0000       ; BAD: A0-A7 all low as well
        in      a, (c)
```

**Why it fails:** the low byte `#00` asserts A1–A7, which also selects the Kempston interface (decodes A5=0) and other peripherals — two devices driving the data bus at once, reading as garbage on some setups and stressing drivers on real hardware.

**Correct:** `#00FE` — zero *high* byte pulls all eight rows low; the low byte `#FE` keeps A1–A7 high so only the ULA responds. Details in the any-key section above.

### Pitfall 5 — Polling the Keyboard Inside a Raster Effect

Timing-critical border/multicolor code that pauses to scan the keyboard inherits **contended-I/O stretch** in the middle of the effect and tears. **Correct:** scan during the vertical blank, store the bitfield, and let the effect read memory. See [Raster Timing](../../05_development/05_display_and_timing/raster_timing.md).

---

## Impact on Emulation and FPGA

- **Emulators** must model the matrix as wired: row = address line low, columns pulled low through closed switches, including **ghosting** (rectangle phantoms) — test ROMs and a few demos detect emulators via multi-key behavior. The EAR bit's idle state (bit 6) should match the emulated ULA revision.
- **Host keyboard mapping** is a policy decision: positional (host key position → matrix position, good for games) vs symbolic (host label → Spectrum key, good for typing). Most emulators offer both; symbol-mode needs the shift keys synthesized as matrix presses.
- **FPGA/MCU adapters** should emulate the matrix electrically (per-intersection closures) rather than asserting row/column lines directly, or 3+ key combinations will behave differently from a real membrane.

---

## FAQ

**How many keys can be detected simultaneously?**
Electrically, all 40 — the scan reads each row independently. The limit is ghosting: any three keys forming a grid rectangle phantom a fourth. Two-key combos are always safe; well-chosen three-key clusters (QA+Space, OP+M) are too.

**Why do some games read the keyboard faster than others?**
They read fewer half-rows. A game using QAOP+Space touches three rows (A9, A10, A13) plus the A15 fire row — four `IN`s instead of eight, and no ROM overhead.

**Can I use CAPS SHIFT as a game button?**
Yes — it's row A8 bit 0, an ordinary key. Many games use it as a second fire. Just remember the ROM also acts on it if you leave the IM 1 handler active.

**What's the difference between "Sinclair 1" and "Sinclair 2" in game menus?**
Interface 2's two joystick ports: port 1 maps to keys 6–0 (row A12), port 2 to keys 1–5 (row A11). Neither has anything to do with Interface 1, which is the Microdrive/network unit and has no joystick ports. A plain keyboard can emulate both at once — that's the standard two-player setup.

**My code works in an emulator but not on real hardware — why?**
The three usual suspects, in order: unmasked EAR bit (Pitfall 1), `IN A,(n)` instead of `IN A,(C)` (Pitfall 2), and a cracked membrane tail on the real machine killing a whole row — verify with the ROM's own editor first.

**Is there a keyboard interrupt?**
No. The only interrupt is the ULA's frame `/INT`; keyboard state must be polled. The ROM polls it inside its IM 1 handler each frame, which is why `LAST_K` looks "interrupt-driven."

---

## References

- Sinclair ZX Spectrum Service Manual — keyboard connector pinouts, membrane replacement procedure
- Dr. Ian Logan & Dr. Frank O'Hara, [*The Complete Spectrum ROM Disassembly*](https://archive.org/details/CompleteSpectrumROMDisassemblyThe) — the `KEYBOARD` routine at `#02BF` and its key tables (also available as a [modern HTML adaptation via SkoolKit](https://skoolkid.github.io/rom/index.html))
- [I/O Port Map](../../10_references/io_port_map.md) — `#FE` decoding, Scorpion `#7E`, Kempston `#1F`
- [ZX Spectrum clone identification (atw.hu)](http://users.atw.hu/zxspectrum/zx_clone_identification_en.htm) — extended 8×6/8×7 matrix circuits, EPROM key encoders

### Cross-References

- [ULA Architecture](ula_architecture.md) — the chip side: column inputs, pull-ups, `#FE` internals
- [48K Memory & I/O](../../05_development/03_memory_and_io/memory_and_io_48k.md#keyboard-reading) — port-level keyboard usage in context
- [48K ROM — Keyboard Input](../../04_operating_systems/rom_48k.md#keyboard-input) — the ROM scanner and decoding
- [System Variables](../../04_operating_systems/system_variables.md) — `LAST_K`, `KSTATE`, reading keys from machine code via ROM state
- [Raster Timing](../../05_development/05_display_and_timing/raster_timing.md) — when *not* to touch the keyboard
- [Contention Model](../../05_development/03_memory_and_io/contention_model.md) — contended I/O costs of `IN`
