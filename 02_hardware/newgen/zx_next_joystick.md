[← Home](../../README.md) · [New Gen Hardware](README.md)

# ZX Next Joystick — Per-Port Standards, Two Kempston Ports, and Mega Drive Pads

## Overview

The ZX Spectrum Next ends the joystick standards war by simply implementing **all of it**. Its two DE-9 ports are not wired to any fixed protocol — each port is individually switchable between Sinclair-row, Cursor, Kempston, and Mega Drive modes through a NextReg, and the FPGA presents the stick to software as whichever standard was selected. A 1984 game expecting a Cursor joystick and a 1994 demo expecting Kempston can both work, on the same machine, one port each.

Two further upgrades matter for new software: the Next is one of the few Spectrum-family machines with **two Kempston-style ports** (`#1F` and `#37`), making dual-stick games practical; and its Mega Drive pad support brings **three or six fire buttons** to a platform that spent four decades with one. This article covers the mode register, the port map, the Mega Drive extension, and the conflicts to avoid. For the underlying protocols (Kempston byte format, Sinclair/Cursor matrix mappings) see [Joystick Interfaces](../../03_io/peripherals/joystick.md); for the NextReg mechanism itself see [Next Memory & I/O](../../05_development/03_memory_and_io/memory_and_io_next.md).

---

## The Two Ports

Both DB9 connectors use the **Atari-standard pinout** — no SJS1-style trap, any classic stick works. What each port *is* depends on NextReg `0x05` (Peripheral 1 setting), which holds a 3-bit mode for each joystick:

| NextReg `0x05` bits | Field |
|---|---|
| 7–6 + 3 | Joystick 1 mode (bits 7–6 = low two bits, bit 3 = high bit) |
| 5–4 + 1 | Joystick 2 mode (bits 5–4 = low two bits, bit 1 = high bit) |
| 2 | 50/60 Hz mode — unrelated, preserve on write |
| 0 | Scandoubler enable — unrelated, preserve on write |

**Mode values** (from the official TBBlue I/O documentation):

| Mode | Standard | Read via |
|---|---|---|
| `000` | Sinclair 2 (keys 67890) | keyboard row `#EFFE` |
| `001` | Kempston 1 | port `#1F` |
| `010` | Cursor (keys 56780) | keyboard rows `#F7FE`/`#EFFE` |
| `011` | Sinclair 1 (keys 12345) | keyboard row `#F7FE` |
| `100` | Kempston 2 | port `#37` |
| `101` | MD 1 — Mega Drive pad, 3 or 6 button | port `#1F` |
| `110` | MD 2 — Mega Drive pad, 3 or 6 button | port `#37` |

In the matrix modes the FPGA injects the stick state into the emulated keyboard rows — the game's ordinary keyboard-scan code sees keypresses, exactly like a real Interface 2. In Kempston/MD modes the port returns an active-high byte.

> [!WARNING]
> **The Sinclair numbering trap.** The official Next documentation labels the 67890 mapping "Sinclair 2" and 12345 "Sinclair 1" — the *opposite* of the Interface 2-era convention used by most games and by [Joystick Interfaces](../../03_io/peripherals/joystick.md) (Sinclair 1 = 6–0, Sinclair 2 = 1–5). The numbering was never consistent across the ecosystem; when configuring or documenting, specify the **keys**, not the number.

---

## Configuring and Reading — Complete Example

Mode selection is a read-modify-write on NextReg `0x05` via the standard NextReg ports (`#243B` select, `#253B` data). This example puts port 1 into Kempston 1 mode and port 2 into Kempston 2 mode, then reads both sticks into a two-player bitfield:

```z80
; next_joystick.asm — dual Kempston setup on the ZX Spectrum Next
; sjasmplus. NextReg access: #243B = register select, #253B = data.

NR_SEL      equ #243B
NR_DAT      equ #253B
NR_PERIPH1  equ #05

; --- Configure: joy1 = Kempston 1 (mode 001), joy2 = Kempston 2 (mode 100) ---
setup_joysticks:
        ld      bc, NR_SEL
        ld      a, NR_PERIPH1
        out     (c), a          ; select NextReg 0x05
        ld      b, >NR_DAT      ; BC = #253B
        in      a, (c)          ; read current Peripheral 1 value
        and     %00000101       ; clear joy1 bits (7,6,3) and joy2 bits (5,4,1),
                                ; preserve 50/60Hz (bit 2) and scandoubler (bit 0)
        or      %01000010       ; joy1 mode 001 (bit 6) | joy2 mode 100 (bit 1)
        out     (c), a
        ret

; --- Read both sticks: returns B = player 1, C = player 2 ---
; Format: FUDLR active-high (bit 0=R 1=L 2=D 3=U 4=F) — same as classic Kempston
read_both:
        in      a, (#1F)        ; Kempston joy 1
        and     #1F
        ld      b, a
        in      a, (#37)        ; Kempston joy 2 — a port classic machines don't have
        and     #1F
        ld      c, a
        ret
```

Notes:

- **Always read-modify-write NextReg `0x05`** — it also carries the 50/60 Hz flag and the scandoubler enable; clobbering them changes the video mode.
- The mask `%00000101` clears the six joystick-mode bits while preserving bits 2 and 0.
- The returned byte is the classic Kempston `000FUDLR` layout — every [unified reader](../../03_io/peripherals/joystick.md#a-unified-reader--kempston--sinclair-1--cursor) already written for 1980s hardware works unchanged.

## Mega Drive Pads — More Than One Fire Button

Modes `101`/`110` decode Sega Mega Drive/Genesis pads (3- and 6-button) through the same `#1F`/`#37` ports: directions and the primary fire button occupy the standard Kempston bits, and **the additional buttons appear on the upper bits (5–7)** of the port byte. For software this is the first sanctioned use of those bits in the platform's history — everywhere else they are undefined (see [Joystick Interfaces — Pitfall 4](../../03_io/peripherals/joystick.md#pitfall-4--trusting-kempston-bits-5-7)).

Recommended practice:

1. Detect the Next first (Machine ID NextReg `0x00`), then check the configured mode — never probe upper bits on unknown hardware.
2. Treat extra buttons as **progressive enhancement**: the game must remain fully playable with fire on bit 4 alone, so the same binary runs on clones and original hardware.
3. Offer the mapping in your redefine menu like any other key.

## Port Conflicts to Know

- **`#1F` is also Multiface 1's disable port and DAC B** — with SpecDrum/Covox enabled (NextReg `0x08` bit 3), writes/reads on `#1F` hit the audio DAC; the Multiface enable/disable ports (`#1F`, `#9F`, `#3F`, `#BF`) share the same low addresses. When the Multiface is disabled (NextReg `0x06` bit 3 = 0) and Covox is off, `#1F` is purely the joystick.
- **Kempston mouse** lives at `#FBDF`/`#FFDF`/`#FADF` — different addresses, no conflict with either joystick port.
- Mode changes are **global, not per-process**: if your program switches modes, restore the user's configuration on exit (read `0x05` at startup, keep it, write it back).

---

## FAQ

**Do I need to configure modes before reading?**
For Kempston modes, the factory default already maps port 1 to Kempston on most setups — but never rely on it: set the mode explicitly or read and respect the existing configuration.

**Can a game use both ports as Kempston simultaneously?**
Yes — this is the Next's signature input upgrade. Configure joy1 = `001`, joy2 = `100`, read `#1F` and `#37`. Two-player games no longer need to exile player 2 to the keyboard.

**How do I detect a Mega Drive pad vs a normal stick?**
You generally don't — the user selects the mode in the Next's configuration (or your program sets it). MD pads without mode switching read as ordinary Kempston sticks on their main button.

**Does the Sinclair/Cursor mode work with *any* old game?**
With any game that reads the keyboard matrix normally — which is nearly all of them. The injection happens below software, in the emulated matrix.

---

## References

- [ZX Spectrum Next I/O Port System and Registers (official)](https://www.specnext.com/tbblue-io-port-system/) — NextReg `0x05` layout, joystick mode table, peripheral port map
- [Next Memory & I/O](../../05_development/03_memory_and_io/memory_and_io_next.md) — the NextReg mechanism (`#243B`/`#253B`), MMU context
- [Joystick Interfaces](../../03_io/peripherals/joystick.md) — the protocols the Next emulates

### Cross-References

- [Clone Joysticks](../clones/clone_joysticks.md) — the single-standard ecosystem the Next is a superset of
- [Keyboard Matrix](../original/keyboard_matrix.md) — the matrix that Sinclair/Cursor modes inject into
- [ULA Architecture](../original/ula_architecture.md) — where the original `#FE`-centric design came from
