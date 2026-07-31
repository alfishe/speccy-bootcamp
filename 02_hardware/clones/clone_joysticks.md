[← Home](../../README.md) · [Clone Hardware](README.md)

# Clone Joysticks — Built-In Kempston, Beta 128 Coexistence, and the Single-Standard Ecosystem

## Overview

In the West, the joystick standards war was fought in game menus. In the Soviet Union, it was settled with a soldering iron: by the early 1990s, **Kempston was on the motherboard**. Pentagon, Scorpion, ATM Turbo, and most of their siblings shipped with an integrated Kempston-compatible port, decoded properly to live alongside the Beta 128 disk interface that the same machines also carried as standard equipment.

The reasons were structural, not sentimental. The Soviet scene bootstrapped itself on the existing software library — which had already chosen Kempston as the dominant port-based standard — and clones had no installed base of Interface 2 or Cursor hardware to honor. Adding a Kempston decoder to a TTL design cost a handful of gates; adding *four* standards cost menus, code, and confusion. So the clone ecosystem standardized completely: in post-Soviet software, "joystick" simply means Kempston, and the Sinclair/Cursor options that Western games carried as menu items survive only as keyboard control schemes.

This article covers the clone-side specifics: how the built-in ports are implemented, the Beta 128 coexistence engineering, two-player realities, and the software conventions that resulted. For the Kempston protocol itself (byte format, decode variants, why it won in the West) see [Joystick Interfaces](../../03_io/peripherals/joystick.md); for keyboard-based control schemes see [Keyboard Matrix](../original/keyboard_matrix.md).

---

## On-Board Implementations

| Machine | Joystick hardware | Notes |
|---|---|---|
| **Pentagon** (all variants) | Built-in Kempston, DE-9 on board | Decoded to avoid the Beta 128 FDC range; present from early versions onward |
| **Scorpion ZS 256** | Built-in Kempston | Coexists with on-board Beta 128; Kempston effectively always available |
| **ATM Turbo** | Built-in Kempston | Alongside its extended keyboard and turbo modes |
| **Profi, Kay, Byte, others** | Kempston standard | Either on-board or the expected expansion; software assumes it |

The practical programming contract across all of them:

- **Port `#1F`, canonical `000FUDLR` layout, active-high** — identical to the Western standard documented in [Joystick Interfaces](../../03_io/peripherals/joystick.md#kempston--the-standard-that-won). Code written for a 1985 Kempston interface runs unchanged on a 1994 Pentagon.
- **The decode is tighter than the cheapest Western interfaces** precisely because every clone also hosts a disk system — see below.
- **One port is the norm.** A second Kempston-style port exists only on some modern multi-interfaces and the ZX Spectrum Next; do not assume it.

## The Beta 128 Coexistence Problem

Every mainstream clone paired its joystick port with a **Beta 128 disk interface** (the TR-DOS standard), whose WD1793 floppy controller occupies ports `#1F`–`#FF` — with the command/status register sitting exactly on the Kempston address `#1F`. On original Western hardware this collision was a genuine hazard (details and bus-fight mechanics in [I/O Port Map — Beta 128](../../10_references/io_port_map.md#beta-128-disk-interface)). Clone designers treated it as a solved problem:

- **Hardware side:** the on-board Kempston decodes additional address lines beyond the FDC's, so the two devices never answer simultaneously. The loose "A0-only" Western Kempston variants simply weren't replicated.
- **Software side:** the convention survived anyway — **don't poll the joystick inside TR-DOS calls**. Disk routines on clones run with interrupts tightly managed and the FDC on the bus; input is read before and after disk activity, never during.

A safe input pattern on TR-DOS machines:

```z80
; Standard TR-DOS-era game loop structure
frame_loop:
        ei
        halt                    ; frame sync
        di
        in      a, (#1F)        ; read Kempston NOW — disk is idle
        ld      (joy_state), a
        call    game_logic
        ; ... any TR-DOS calls happen here, with input already buffered ...
        call    draw_frame
        jr      frame_loop

joy_state:  db  0
```

## Two Players, One Standard

The single-port reality shaped multiplayer conventions:

- **Player 1 on Kempston, player 2 on keyboard rows** — the dominant arrangement. The Sinclair-row mappings (6–0 and 1–5) work on every clone because the keyboard matrix is electrically identical, even on full-travel clone keyboards.
- **Two players sharing the keyboard** via the 6–0 / 1–5 rows — equally common, zero hardware.
- **Two Kempston ports** — essentially nonexistent in the classic era; two loosely-decoded interfaces on one machine collide at `#1F`. Modern dual-port interfaces and the Next's `#1F` + `#37` pair are the exceptions, not the rule.

## Software Culture

The single-standard ecosystem shows in the software:

- Post-Soviet games frequently offer **"KEMPSTON / KEYBOARD / REDEFINE"** — three options instead of the Western quartet.
- Joystick = Kempston is assumed so thoroughly that much scene software (demos included) reads `#1F` directly with no menu at all.
- **Autofire** was a beloved clone-era joystick feature (hardware toggle on the stick itself); games never implemented it in software.

> [!NOTE]
> When porting Western software to clones — or writing new cross-platform titles — the rule of thumb inverts the Western one: on clones you may assume Kempston is present; you may **not** assume the player has ever seen a Cursor interface. Keep keyboard redefine as the universal fallback and every scene is served.

---

## Pitfalls

### Pitfall 1 — Assuming a Second Kempston Port

```z80
        in      a, (#5F)        ; second stick? BAD on classic clones
```

Only specific modern multi-interfaces and the ZX Spectrum Next (`#37`) provide a second Kempston-style port. On a classic Pentagon or Scorpion, `#5F` reads nothing meaningful — or something else's register. **Correct:** player 2 goes on the keyboard rows, or detect the Next explicitly ([ZX Next Joystick](../newgen/zx_next.md#joystick-system)).

### Pitfall 2 — Polling the Stick Inside TR-DOS Calls

Even though clone hardware decodes properly, a joystick read issued while your code has the FDC mid-command is asking for status bytes, not stick state. **Correct:** buffer input at frame top, before any disk activity (pattern above).

### Pitfall 3 — Assuming Western Menu Options Exist

Post-Soviet players expect KEMPSTON/KEYBOARD/REDEFINE and little else; conversely, Western players on original hardware may have *no* Kempston. **Correct:** ship both sensibilities — default Kempston, default keyboard cluster, redefine — as laid out in [Joystick Interfaces — Decision Guide](../../03_io/peripherals/joystick.md#which-standards-to-support--decision-guide).

---

## References

- [I/O Port Map — Beta 128 Disk Interface](../../10_references/io_port_map.md#beta-128-disk-interface) — the `#1F`–`#FF` collision in detail
- zx-pk.ru — clone schematics (Pentagon, Scorpion) showing the on-board Kempston decode

### Cross-References

- [Joystick Interfaces](../../03_io/peripherals/joystick.md) — the Kempston protocol and Western standards this article assumes

- [Clone Timing](clone_timing.md) — per-clone detection if your input code needs to know the host
- [Keyboard Matrix — keysets by scene](../original/keyboard_matrix.md#how-games-use-the-keyboard--typical-keysets) — regional input conventions
