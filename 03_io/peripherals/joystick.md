[← Home](../../README.md) · [Peripherals](README.md)

# Joystick Interfaces — Kempston, Sinclair/Interface 2, Cursor/Protek/AGF, Fuller, and the Clone-Era Standards

## Overview

The ZX Spectrum shipped without a joystick port — and without a joystick *standard*. Into that vacuum stepped at least four incompatible third-party interfaces, and every action game of the 1980s paid the price: the familiar menu litany **"KEMPSTON / SINCLAIR / CURSOR / REDEFINE KEYS"** is the direct consequence of Sinclair leaving input to the aftermarket.

The split was fundamental. One camp — Sinclair's own Interface 2, and the Cursor-style interfaces from Protek and AGF — wired the joystick into the **keyboard matrix**, making a stick indistinguishable from five specific keys. The other camp — Kempston, and the rarer Fuller box — gave the stick its own **hardware port**, which software had to support explicitly. Each approach had real merits: matrix joysticks worked even in games that only knew the keyboard; port joysticks freed the keyboard entirely, read in a single instruction, and never ghosted. Kempston won the 48K era so thoroughly that Soviet clones later soldered it directly onto the motherboard, Amstrad's +2/+3 went the Sinclair matrix route with a hostile pinout, and modern interfaces routinely speak three or four standards at once.

This article catalogs the protocols as programming targets: ports, bit layouts, polarity, decoding variants, conflicts, and a unified reader that speaks the big three. For the matrix side of the Sinclair/Cursor standards (rows, ghosting, two-player rows) see [Keyboard Matrix](../../02_hardware/original/keyboard_matrix.md); for port decoding minutiae see [I/O Port Map](../../10_references/io_port_map.md#joystick-ports-world-of-spectrum-reference).

---

## The Interface Landscape

| Standard | Port | Polarity | Hardware type | Era / status |
|---|---|---|---|---|
| **Kempston** | `#1F` | Active-high | Dedicated port, one stick | Won the 48K era; built into most Soviet clones; still the default in emulators |
| **Sinclair 1 / 2** (Interface 2) | `#EFFE` / `#F7FE` (keyboard rows) | Active-low | Passive — shorts matrix lines, two sticks | Sinclair's own, 1983; built into +2/+3 (SJS1 pinout) |
| **Cursor / Protek / AGF** | `#F7FE` + `#EFFE` (keyboard rows) | Active-low | Matrix interface, one stick | Early; survived via "redefine keys" compatibility |
| **Fuller** | `#7F` | Active-low | Dedicated port inside the Fuller Audio Box | Rare; mostly bought for its AY sound chip |
| **Timex (TS2068)** | `#F6` via AY register 14 | Active-low | Built-in, two sticks | Timex machines only; TC2048 used Kempston instead |

Two physical details span all of them:

- **The plug is (almost) always the Atari-standard DE-9** — up/down/left/right/fire with a common ground. The exceptions are the Amstrad-era SJS1 ports, which rearranged the pins to sell Sinclair's own sticks.
- **Everything is digital.** There is no analog standard in the Spectrum world worth supporting; the few analog experiments (Mikro-Gen's A/D board) are historical curiosities.

---

## Kempston — The Standard That Won

The Kempston interface (Kempston Micro Electronics) is a minimal piece of logic: a port decode, a buffer, and a DE-9 socket. One read returns the whole stick:

```z80
        in      a, (#1F)        ; Kempston state — active HIGH (bit set = pressed)
        bit     4, a
        jr      nz, fire_pressed
```

| Port | Decoding | R/W | Description |
|---|---|---|---|
| `#1F` | Varies — see below | R | Kempston joystick state |

**Read byte — the canonical `000FUDLR` layout:**

| Bit | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|---|
| Meaning | 0 | 0 | 0 | **F**ire | **U**p | **D**own | **L**eft | **R**ight |

Active **high** — the opposite polarity of everything on the keyboard matrix. Bits 5–7 read as 0 on classic interfaces; some modern multi-button variants use them for extra fire buttons (see [ZX Next Joystick](../../02_hardware/newgen/zx_next.md#joystick-system)).

> [!NOTE]
> Some reference tables (including the Black_Cat port table that [I/O Port Map](../../10_references/io_port_map.md#kempston-joystick--1f) reproduces) print the bits in a different order, with fire on bit 0. The layout above is what emulators (Fuse, ZEsarUX, UnrealSpeccy) implement and what the surviving software base expects — treat it as canonical, and if in doubt, verify against a known game.

### Decoding variants — the wild west

There was never one Kempston circuit. The documented decode variants:

| Variant | Address lines checked |
|---|---|
| Kempston(7) | A0=1 only — answers on `#1F`, `#FF`, thousands of aliases |
| Kempston(D) | A5=0, A0=1 |
| Kempston(6) | A7=0, A5=0, A1=1, A0=1 |
| Kempston+Printer(6) | A7=0, A3=1, A2=1, A0=1 |

Software impact: **always use the canonical `#1F`** — every variant responds to it. Hardware impact: a loosely-decoded Kempston answers on ports belonging to other devices, which is the root of the conflicts below.

### The Beta 128 / TR-DOS conflict

The Beta 128 disk interface's WD1793 FDC occupies ports `#1F`–`#FF` — the Kempston `#1F` lands exactly on the FDC's command/status register. On a machine with both:

- A well-behaved clone-era Kempston decodes additional address lines to stay out of the FDC's way.
- A cheap one doesn't, and **reading `#1F` during disk activity returns FDC status**, not joystick state — or worse, two devices drive the bus at once.

Soviet machines solved this by policy: TR-DOS games read the joystick before/after disk access, and clone motherboards integrated a properly-decoded Kempston. Details in [I/O Port Map — Beta 128](../../10_references/io_port_map.md#beta-128-disk-interface).

### Why it won

- **One instruction, 11 T-states** — the cheapest input read on the machine; the keyboard matrix costs 12 T-states per half-row and you need at least three rows for directions + fire.
- **No ghosting, ever** — it's not a matrix.
- **Active-high reads naturally** — `bit 4,a / jr nz, fire` with no `CPL` gymnastics.
- **The keyboard stays free** — critical for two-player games (one on Kempston, one on keys) and for games using the full keyboard for secondary functions.

---

## Sinclair / Interface 2 — The Matrix Standard

Sinclair's Interface 2 (September 1983, £19.95) combined a 16K ROM cartridge slot with two DE-9 joystick ports wired **passively into the keyboard matrix** — no electronics, just switches across matrix intersections. Port 1 lands on keys 6–0, port 2 on keys 1–5:

| Menu label | Row (port) | Left | Right | Down | Up | Fire |
|---|---|---|---|---|---|---|
| **Sinclair 1** (port 1) | A12 (`#EFFE`) | 6 | 7 | 8 | 9 | 0 |
| **Sinclair 2** (port 2) | A11 (`#F7FE`) | 1 | 2 | 3 | 4 | 5 |

Active **low**, exactly like the keyboard — because it *is* the keyboard. Reading, two-player use, the mirrored bit order between the two rows, and ghosting behavior are covered in [Keyboard Matrix — Joysticks on the Matrix](../../02_hardware/original/keyboard_matrix.md#joysticks-on-the-matrix) and not repeated here.

Naming traps to keep straight:

- **Interface 1 ≠ joysticks.** Interface 1 is the Microdrive/RS-232/network unit. The joystick unit is Interface 2; menu labels "SINCLAIR 1 / SINCLAIR 2" number its *ports*.
- **Interface 2's pass-through edge connector was cut down** — officially only a ZX Printer could daisy-chain off it.
- The ROM cartridge slot was a commercial failure (10 titles, 16K vs 48K games); the joystick ports were the lasting legacy.

### The Amstrad era: +2/+3 built-in ports and the SJS1 trap

The grey +2 and the +2A/+3 integrated two joystick ports following the **same Sinclair matrix mapping** (6–0 and 1–5 rows) — but with a **proprietary pinout** that is *not* Atari-compatible. Amstrad sold the matching **SJS1** stick (often bundled, not highly regarded); plugging a standard Atari-style stick into the rearranged pins at best doesn't work and at worst shorts +5V through the stick's switches. Third-party **passive pin adapters** appeared immediately and remain the correct solution. Software-wise nothing changed: the sticks still read as keyboard rows `#EFFE`/`#F7FE`.

---

## Cursor / Protek / AGF — The Redefine-Compatible Standard

The Cursor standard maps the stick onto the Spectrum's own **cursor keys**: 5, 6, 7, 8 plus 0 for fire:

| Direction | Key | Row, bit |
|---|---|---|
| Left | 5 | A11 (`#F7FE`), bit 4 |
| Down | 6 | A12 (`#EFFE`), bit 0 |
| Up | 7 | A12 (`#EFFE`), bit 1 |
| Right | 8 | A12 (`#EFFE`), bit 2 |
| Fire | 0 | A12 (`#EFFE`), bit 4 |

Protek and AGF sold the interfaces (AGF's was "programmable" — its second-stick mapping landed on T-Y-U-I-P — and included a keyboard/joystick switch). The standard's killer feature: **it worked with games that had no joystick support at all**, as long as they offered redefinable keys — the stick simply *became* the cursor keys. The same property made the electronics costlier (the interface must drive the matrix in half-row groups), and once joystick support became a checkbox feature in games, the Cursor interface faded. It survives as a menu option to this day — and it's the reason "cursor keys" as a keyboard control scheme (5/6/7/8/0) appears in hundreds of games.

---

## Fuller — The Sound Box With a Joystick

The Fuller Audio Box (1983, £29.95) was bought primarily for its **AY-3-8912 sound chip** (ports `#3F` control / `#5F` data — years before the 128K made AY sound standard) with an optional speech chip; the joystick port rode along:

| Port | Decoding | R/W | Description |
|---|---|---|---|
| `#7F` | Low byte `#7F` | R | Fuller joystick — active **low** |

The returned byte is conventionally written `F--RLDU` — fire on bit 7, right/left/down/up on bits 4–1, bit clear = triggered. Fuller boxes sold in small numbers (they are genuinely rare now), but a meaningful slice of 1983–84 software supports the standard, and emulators still implement it.

---

## Timex — The AY Register Joysticks

The Timex Sinclair TS2068 (and TC2068) built joysticks in, but routed them through the **AY-3-8912's I/O port A** (register 14) rather than a dedicated port or the matrix:

| Port | Select | Returns |
|---|---|---|
| `#01F6` | A8=1, A9=0 | Joystick 1 |
| `#02F6` | A8=0, A9=1 | Joystick 2 |
| `#F6` (A8=0,A9=0) | — | Both OR'd together |

Active low. The later **TC2048 dropped this and went Kempston-compatible** instead — an early sign of which way the market had settled. Timex support matters if you target the TS2068 software library or the Portuguese/Polish Timex clones; otherwise it's a footnote.

---

## Track Applicability

This article covers the **original-track** aftermarket standards as they existed on Sinclair/Amstrad hardware. The other two tracks get their own articles:

- **Soviet clones** moved Kempston onto the motherboard and settled the standards war in hardware — see [Clone Joysticks](../../02_hardware/clones/clone_joysticks.md).
- **ZX Spectrum Next** implements every standard above per-port, plus Mega Drive pads — see [ZX Next Joystick](../../02_hardware/newgen/zx_next.md#joystick-system).

Modern multi-standard interfaces serve the original-hardware market where nothing is built in. A representative example (Lotharek's Kempston MAX 2) shows how complete the coverage has become — one device, mode switch: Kempston on `#1F` (second stick on `#5F`), Sinclair 1/2 on the keyboard rows, Fuller on `#7F` (second stick as Kempston on `#37`), and Cursor/Protek modes. On original 48K hardware such an interface is the practical way to cover every game ever written.

---

## A Unified Reader — Kempston + Sinclair 1 + Cursor

Games historically solved the multi-standard mess the same way: a menu, and one small reader per standard, all normalizing to a single bitfield. This complete example does exactly that — output layout matches the Kempston byte (`F U D L R` in bits 4–0, bit set = active), so the game logic below it never knows which standard is in use.

```z80
; joystick_read.asm — unified reader for the big three standards
; sjasmplus. Output: A = FUDLR (bit 0=RIGHT 1=LEFT 2=DOWN 3=UP 4=FIRE)

JOY_KEMPSTON  equ 0
JOY_SINCLAIR1 equ 1
JOY_CURSOR    equ 2

; read_joystick — in: A = standard (0-2). Out: A = normalized state.
; Clobbers AF, BC, DE, HL.
read_joystick:
        ld      hl, joy_vectors
        add     a, a            ; 2 bytes per vector
        ld      e, a
        ld      d, 0
        add     hl, de
        ld      e, (hl)
        inc     hl
        ld      d, (hl)
        ex      de, hl
        jp      (hl)

joy_vectors:
        dw      read_joy_kempston
        dw      read_joy_sinclair1
        dw      read_joy_cursor

; --- Kempston: already in FUDLR format, active-high. Nothing to do. ---
read_joy_kempston:
        in      a, (#1F)
        and     #1F             ; drop undefined bits 5-7
        ret

; --- Sinclair 1: row 6 7 8 9 0, active low. ---
; src bits (active-high after CPL): b4=L b3=R b2=D b1=U b0=F
read_joy_sinclair1:
        ld      bc, #EFFE
        in      a, (c)
        cpl
        and     #1F
        ld      h, >joy_lut_s1  ; permute L R D U F → F U D L R
        ld      l, a
        ld      a, (hl)
        ret

; --- Cursor: 5/6/7/8/0 across two rows, active low. ---
read_joy_cursor:
        ld      bc, #EFFE       ; 6=down(b0) 7=up(b1) 8=right(b2) 0=fire(b4)
        in      a, (c)
        cpl
        and     #17             ; keep b0,b1,b2,b4 — ignore key 9 (b3)
        ld      h, >joy_lut_cursor
        ld      l, a
        ld      e, (hl)         ; R/D/U/F placed; left comes from the other row
        ld      bc, #F7FE       ; key 5 = left (b4), active low
        in      a, (c)
        and     #10
        jr      nz, .no_left
        set     1, e            ; L → bit 1
.no_left:
        ld      a, e
        ret

        align 256
; index: b4..b0 = L R D U F (active-high) → FUDLR
joy_lut_s1:
        db  0,16,8,24,4,20,12,28,1,17,9,25,5,21,13,29
        db  2,18,10,26,6,22,14,30,3,19,11,27,7,23,15,31
; index: b4..b0 = F 0 R U D (active-high, b3=0) → FUDLR with L=0
joy_lut_cursor:
        db  0,4,8,12,1,5,9,13,0,4,8,12,1,5,9,13
        db  16,20,24,28,17,21,25,29,16,20,24,28,17,21,25,29
```

Design notes:

- **The Kempston byte is the normalization target** for a reason: active-high, single byte, and the layout most post-1985 software was written against. Sinclair and Cursor readers convert into it; the game consumes one format.
- **Both LUTs fit in one 256-byte page**, so the `ld h, >table` / `ld l, a` trick costs 4 T-states per lookup instead of a chain of `BIT`/`JR` tests. Sinclair 2 support is a third LUT (same shape, different permutation) — left as an exercise the table format makes trivial.
- **Merge, don't switch:** many games OR the joystick result with the keyboard bitfield every frame so both work simultaneously. With this reader that is literally one `or` instruction.
- **Add fire-button edge detection above this layer**, exactly as in the [keyboard game-input example](../../02_hardware/original/keyboard_matrix.md#game-input-patterns--a-complete-example) — the bitfield layout is deliberately identical.

> [!WARNING]
> **You cannot reliably autodetect these interfaces.** Reading `#1F` with no Kempston attached returns whatever floats on the bus (often `#00`, `#FF`, or screen data); a Matrix stick is invisible until pressed. Every classic solution is social, not technical: ask the player in a menu. See Pitfall 2.

---

## Which Standards to Support — Decision Guide

For new software in this ecosystem, the support matrix writes itself:

| Standard | Support? | Why |
|---|---|---|
| **Kempston** | **Mandatory** | Built into every clone, every emulator default, every modern interface. If you support exactly one standard, it's this one |
| **Keyboard (redefinable)** | **Mandatory** | The only input guaranteed on every machine ever made; QAOP+SPACE default + redefine covers all players and all regional habits (see [Keyboard Matrix — keysets](../../02_hardware/original/keyboard_matrix.md#how-games-use-the-keyboard--typical-keysets)) |
| **Sinclair 1/2** | **Recommended** | Free to add (one LUT each), covers Interface 2, +2/+3 built-in ports, and two-player-on-one-keyboard |
| **Cursor** | **Recommended** | One more LUT; doubles as support for the cursor-key control scheme many players still use |
| **Fuller** | Optional | Rare hardware; add it if your reader is table-driven and it costs nothing |
| **Timex** | Only if targeting TS2068 | Different mechanism (AY register), not a port read |

**When NOT to bother with joystick code at all:** text adventures, strategy, anything menu-driven — the ROM keyboard path is better suited, and joystick support adds nothing.

**When joystick support is non-negotiable:** action games, and especially two-player simultaneous games — where the standard loadout is Kempston for player 1 and Sinclair rows (or keys) for player 2.

## Historical Context — The Standard That Wasn't

The Spectrum's joystick chaos was a direct consequence of Sinclair's minimalism: the machine shipped with no port, no connector, and no opinion. Compare what everyone else did:

| Platform | Built-in joystick? | Standard |
|---|---|---|
| **ZX Spectrum** | No — aftermarket vacuum | Four+ incompatible standards; software absorbs the complexity |
| **Commodore 64** | Yes — 2× DE-9 on the motherboard | One standard (CIA ports), every game uses it |
| **Atari 8-bit** | Yes — 4× DE-9 | The original Atari standard everyone else's plugs copied |
| **Amstrad CPC** | Yes — 1× DE-9 | One standard (AY I/O port) |
| **MSX** | Yes — 2× DE-9 | One standard (PSG I/O ports), codified in the MSX spec |
| **BBC Micro** | Yes — analog port | One (analog) standard |

Every competitor answered the question in hardware; the Spectrum answered it in **game menus**. The cost was real — every action game carried 3–4 input drivers, and players needed to know what hardware they owned — but so was the upside: the aftermarket competed, Kempston emerged as a genuine market-chosen standard rather than a corporate one, and the keyboard-matrix designs meant even a game from 1982 with no joystick code could be played with a stick via redefine. Amstrad closed the loop in 1987 by building ports in — and immediately repeated Sinclair's mistake by changing the pinout.

The Soviet chapter inverted everything again: clones standardized on Kempston in hardware because the software library had already standardized on it, and the "menu quartet" became a formality — the full story is in [Clone Joysticks](../../02_hardware/clones/clone_joysticks.md).

## Modern Analogies

| Spectrum joystick concept | Modern equivalent |
|---|---|
| Four competing hardware standards | Pre-USB game peripherals: game port vs Sidewinder vs Gravis protocols |
| "KEMPSTON / SINCLAIR / CURSOR" menu | Controller API selection: XInput vs DirectInput vs raw HID |
| Keyboard-matrix joysticks | Remapping a gamepad to emit keyboard events (Steam Input) |
| Kempston single-byte port read | Reading a HID gamepad report — one struct, active-high bits |
| No autodetection; ask the user | Emulator controller configuration screens |
| Next's Mega Drive pad on upper bits | Extended buttons in a backward-compatible report descriptor |

---

## Pitfalls & Common Mistakes

### Pitfall 1 — Mixing Polarities in Merged Input

```z80
        in      a, (#1F)        ; Kempston: bit SET = pressed
        ld      b, a
        ld      c, #FE
        in      a, (c)          ; keyboard row: bit CLEAR = pressed
        or      b               ; BAD: OR of opposite polarities is garbage
        ld      (input), a
```

**Why it fails:** Kempston is active-high, everything on the matrix is active-low. OR-ing them raw produces a byte that means nothing — pressed keys mask real joystick bits, idle keys fake joystick presses.

**Correct:** normalize each source to one polarity/layout *first* (as the unified reader does), then merge:

```z80
        call    read_joystick   ; A = FUDLR, active-high
        ld      b, a
        call    read_keys_norm  ; your keyboard scan, also active-high FUDLR
        or      b
        ld      (input_state), a
```

### Pitfall 2 — Trying to Autodetect the Interface

```z80
        in      a, (#1F)
        or      a
        jr      nz, kempston_present   ; BAD: nz proves nothing
```

**Why it fails:** with no Kempston attached, `#1F` reads the floating bus — which may be `#00`, `#FF`, or bytes of the currently displayed screen, changing every frame. A zero read doesn't prove absence (the stick might just be centered), and a nonzero read doesn't prove presence. There is no handshake, no ID register, no reliable probe.

**Correct:** ask the player. Every classic game did; the menu *is* the detection mechanism.

### Pitfall 3 — Reading `#1F` While the Disk Is Active

On Beta 128 / TR-DOS systems the FDC lives on `#1F`–`#FF`. Reading the "joystick" during a disk operation returns WD1793 status bits or fights the FDC for the bus. **Correct:** read input before invoking TR-DOS calls, and never poll the stick inside a disk routine. On well-decoded clone hardware this is handled for you; on original 48K + Beta 128 it is not.

### Pitfall 4 — Trusting Kempston Bits 5–7

```z80
        in      a, (#1F)
        bit     7, a            ; BAD: undefined on classic hardware
```

Classic interfaces drive only bits 0–4; bits 5–7 may read as 0, 1, or float depending on the buffer. Modern devices (Next, multi-button interfaces) *do* use bits 5–6 for extra fire buttons — deliberately. **Correct:** `and #1F` unless you have explicitly identified multi-button hardware, and offer the extra buttons as an enhancement, never a requirement.

### Pitfall 5 — The SJS1 Pinout Assumption

Hardware-side, not software: the +2/+3 joystick ports are **not Atari-wired**. Building a cable or adapter from the Atari DE-9 standard and plugging it into a +2/+3 connects +5V to the wrong pin. **Correct:** use or build the documented SJS1-to-Atari adapter; the pinout difference is precisely why third-party adapters exist.

---

## Impact on Emulation and FPGA

- **Default to Kempston.** It's the emulator default everywhere (Fuse, ZEsarUX, UnrealSpeccy all map host gamepads to Kempston first), so emulator-tested homebrew that only supports Kempston still reaches most players — but see the decision guide before shipping that.
- **Model the floating read.** Emulators differ on what `#1F` returns with no joystick attached (`#00` vs `#FF` vs floating bus); software relying on any specific value is emulator-locked — another reason Pitfall 2's "just ask" policy survives.
- **Matrix standards must ghost.** Sinclair/Cursor emulation belongs in the keyboard-matrix model, including rectangle ghosting — see [Keyboard Matrix — Impact on Emulation](../../02_hardware/original/keyboard_matrix.md#impact-on-emulation-and-fpga).
- **FPGA cores** (Next, ZX-Uno, MiSTer) typically implement per-port standard selection and Mega Drive pad decoding; match the Next's upper-bit convention for extra buttons rather than inventing a new one.

---

## FAQ

**If I support only one joystick standard, which one?**
Kempston. Clones have it on the motherboard, emulators default to it, modern interfaces speak it. Add keyboard-with-redefine and you're done for 95% of players; add Sinclair/Cursor LUTs for the rest.

**Why is it called "Kempston"?**
After Kempston Micro Electronics, the company that made the interface — named in turn after Kempston, Bedfordshire. It has no relationship to the keyboard or to Sinclair.

**Can two players use joysticks at once?**
Yes, in three ways: two Interface 2 sticks (Sinclair 1 + 2 rows), Kempston + one Sinclair row, or — on modern multi-interfaces — two Kempston-style ports (`#1F` + `#5F`). Two *classic* Kempston interfaces on one machine collide at `#1F`.

**Do any games use analog joysticks?**
Effectively no. A handful of Mikro-Gen titles supported an analog A/D board (memory-mapped at `#3E80`) in the ZX81/early Spectrum era — a curiosity, not a standard. Spectrum gaming is digital-only.

**Why does my Kempston read fine in an emulator but erratically on a real 48K + Beta 128?**
The FDC conflict — Pitfall 3. Your reads are landing on WD1793 registers during disk activity, or your interface decodes too loosely and both devices respond.

---

## References

- [Retro Isle — Sinclair ZX Spectrum Joysticks Explained](https://www.retroisle.com/general/spectrum_joysticks.php) — interface history, Fuller `F--RLDU` format, Timex register-14 joysticks, +2/+3 SJS1
- [Sinclair ZX Specifications (no$zx docs)](https://problemkaputt.de/zxdocs.htm) — exhaustive joystick port/bit tables including AGF second-stick mappings
- [I/O Port Map](../../10_references/io_port_map.md#joystick-ports-world-of-spectrum-reference) — Black_Cat decode variants, Beta 128 conflict, mouse ports
- [World of Spectrum](https://worldofspectrum.org/) (spectrumcomputing.co.uk) — interface hardware archive, game support lists

### Cross-References

- [Keyboard Matrix](../../02_hardware/original/keyboard_matrix.md) — Sinclair/Cursor mechanics, ghosting, two-player rows, game keysets by genre and region
- [ULA Architecture](../../02_hardware/original/ula_architecture.md) — the `#FE` port the matrix standards live on
- [Contention Model](../../05_development/03_memory_and_io/contention_model.md) — I/O contention costs of port reads
- [Next Memory & I/O](../../05_development/03_memory_and_io/memory_and_io_next.md) — NextReg joystick modes, Mega Drive pads
- [48K Memory & I/O](../../05_development/03_memory_and_io/memory_and_io_48k.md) — port-level context for `#1F` and `#FE`
