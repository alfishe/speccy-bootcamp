[← Home](../../README.md) · [Interrupts](README.md)

# Non-Maskable Interrupts — Multiface, Magic Buttons, and Safe NMI Handlers

The ZX Spectrum has one interrupt line (`INT`, maskable) and one non-maskable interrupt line (`NMI`). The standard ULA drives only `INT`, once per video frame. Nothing in the stock machine generates an NMI. NMI exists purely as a hook for **external hardware** — the Multiface series of cheat/snapshot cartridges, the DivIDE "magic button", ESXDOS NMI hooks, and various custom interfaces.

This article covers what NMI is on the Z80, how the Multiface hardware exploits it to seize control of a running program, what code is safe to run inside an NMI handler, and the failure modes that make NMI dangerous during tape or disk I/O.

> [!NOTE]
> This article assumes you understand the basics of maskable interrupts from [interrupt_programming.md](interrupt_programming.md). The Z80 CPU-level interrupt architecture (IFF1/IFF2, bus cycles, acknowledge timing for both INT and NMI) is in [z80_interrupts.md](../../01_cpu/z80_interrupts.md).

---

## NMI vs INT on the Z80

| Property | INT (maskable) | NMI (non-maskable) |
|---|---|---|
| Triggered by | ULA, peripherals | External hardware (Multiface, DivIDE) |
| Disabled by `DI`? | Yes | No |
| Vector mechanism | IM1 fixed to `#0038`, IM2 vector table | Always fixed to `#0066` |
| Acknowledge cycle | Variable (12-19 T-states) | Fixed (11 T-states) |
| Saves IFF1 to IFF2? | No | Yes — `IFF2 := IFF1` before clearing IFF1 |
| Stack usage | Pushes PC (2 bytes) | Pushes PC (2 bytes) |
| Return instruction | `RET` (with manual `EI`) or `RETI` | `RETN` (restores IFF1 from IFF2) |

### The Acknowledge Cycle

When the NMI line is asserted (pulled low), the Z80 finishes the current instruction, performs an 11-T-state acknowledge sequence, pushes the return address onto the stack, and jumps to `#0066`. There is no vector lookup — the target address is hardwired.

```text
NMI assertion
    ↓
[finish current instruction]
    ↓
[11-T acknowledge cycle: M1 + WAIT + refresh]
    ↓
[SP -= 2; (SP) := PC; PC := #0066]
    ↓
[IFF2 := IFF1; IFF1 := 0]  ← maskable interrupts now disabled
    ↓
First instruction at #0066 executes
```

### Why IFF2 Matters

NMI clears `IFF1` (so the NMI handler is not interrupted by an INT mid-execution), but saves the previous value in `IFF2`. The handler must use `RETN` (not `RET` or `RETI`) to restore `IFF1` from `IFF2`. If you use `RET`, the previous interrupt-enable state is lost and `IFF1` stays at 0 — your maskable interrupts are gone forever.

```z80
; Correct NMI handler exit
nmi_handler:
    ; ... do work ...
    RETN                   ; Restores IFF1 from IFF2

; WRONG — loses interrupt state
nmi_handler_bad:
    ; ... do work ...
    RET                    ; IFF1 stays at 0, maskable interrupts dead
```

---

## Multiface Hardware

The Multiface series by Romantic Robot (Multiface I, Multiface 128, Multiface 3) is the most iconic NMI-generating hardware for the Spectrum. Pressing the red button on a Multiface freezes the running program, pages in the Multiface's own ROM and RAM, and presents a menu for saving memory snapshots, poking values, or examining the game state.

### Hardware Implementation

The Multiface I contains:

- 8 KB ROM paged in at `#0000`–`#1FFF`
- 8 KB RAM paged in at `#2000`–`#3FFF`
- Kempston-compatible joystick port (decoded at `#1F`)
- A single 74LS74 dual flip-flop IC storing two state bits

The two flip-flops are the entire control logic:

| Flip-flop | Name | Purpose |
|---|---|---|
| `FF_PAGED_IN` | "Memory is mapped" | When set, MF ROM/RAM override the Spectrum's normal `#0000`–`#3FFF` |
| `FF_NMI_PENDING` | "Button was pressed" | When set, drives the NMI line low; cleared by `OUT (#1F),A` |

### Boot Sequence

1. User presses the NMI button
2. The NAND gate on the button input checks `FF_NMI_PENDING`; if clear, sets it
3. `FF_NMI_PENDING` output drives the Z80's NMI pin low
4. `FF_NMI_PENDING` output also arms detection of address `#0066` (decoded together with `MREQ` and `M1`)
5. Z80 finishes current instruction, pushes PC, jumps to `#0066`
6. **When the Z80 fetches the first byte at `#0066`**, the Multiface detects this address and **sets `FF_PAGED_IN`**
7. `FF_PAGED_IN` immediately pages in MF ROM at `#0000` and MF RAM at `#2000`
8. The very next fetch (which the Z80 thinks is the second byte at `#0067`) is now from MF ROM — the NMI handler takes over

This is a brilliant piece of minimal logic: the Multiface waits until the Z80 has committed to the NMI, then transparently replaces the ROM before the second instruction of the handler executes. The MF ROM at `#0066` contains a `JP` to the actual menu code.

### Reset

The MF is paged out and `FF_NMI_PENDING` is cleared by `OUT (#1F),A` from the MF ROM's menu code. The output decode is:

```text
OUT port: %----.----.-001.--1-
```

Any `OUT` to a port matching this mask (e.g. `#1F`, `#3F`, ...) clears `FF_NMI_PENDING`. Once cleared, the NAND gate on the button input is re-enabled, allowing another button press.

### Joystick Port Decode

The same port is used for joystick reads:

```text
IN port: %----.----.-001.--1-
```

- `IN A,(#1F)` returns joystick bits `D0`–`D4` (Kempston layout)
- The `A7` bit in the address determines `FF_PAGED_IN` state:
  - `A7=0` (e.g. `IN A,(#1F)`): pages MF memory **out**
  - `A7=1` (e.g. `IN A,(#9F)`): pages MF memory **in**

This is how the MF menu reads the joystick (page in to read Kempston port, page out to release machine back to the game).

### The Multiface I Design Flaw

The button signal is gated through a NAND that immediately disables the button as soon as `FF_NMI_PENDING` is set. The intention was to prevent the NMI line from staying low while the button is held. But the design is flawed: as soon as the MF software clears `FF_NMI_PENDING`, the NAND re-enables the button, which immediately sets `FF_NMI_PENDING` again if the user is still holding it. The result is a brief "NMI off" pulse that can recursively re-trigger.

In practice this means: **the user must release the NMI button before the MF menu code returns from the handler**, or another NMI fires immediately on `RETN`.

---

## NMI-Safe Code Constraints

If you are writing an NMI handler — either for a Multiface-like device of your own design, or for the DivIDE magic button, or for any custom hardware — there are hard rules about what the handler can and cannot do.

### Rule 1: Preserve the I Register

If the program was running in IM2 mode when NMI fired, the `I` register holds the high byte of the vector table. Your NMI handler **must not change `I`** without restoring it.

```z80
; BAD: corrupts I, breaks IM2 on return
nmi_bad:
    LD   A,#FE
    LD   I,A              ; Now I is wrong
    ; ... NMI work ...
    RETN                   ; Program returns to IM2 with wrong table address
```

```z80
; GOOD: save and restore I
nmi_good:
    PUSH AF
    LD   A,I              ; Read I (also sets parity flag for IFF2)
    LD   (saved_i),A
    LD   A,#FE
    LD   I,A              ; Use our own table while in NMI
    ; ... NMI work ...
    LD   A,(saved_i)
    LD   I,A
    POP  AF
    RETN

saved_i:  DB  0
```

Actually, the simpler discipline is **never change `I` in an NMI handler**. There is rarely a reason to.

### Rule 2: Save and Restore IY

The 48K ROM ISR at `#0038` uses `IY` as a base register pointing to system variables at `#5C3A`. Many commercial games also assume `IY` is preserved across interrupts. If your NMI handler changes `IY` and an INT fires (impossible, since NMI clears IFF1) — wait, that is actually safe. But if the interrupted code expects `IY` to remain stable across function calls, your NMI must restore it.

```z80
nmi_handler:
    PUSH IY               ; 15T — always save
    ; ... work that may trash IY ...
    POP  IY               ; 14T
    RETN
```

### Rule 3: Save and Restore #7FFD Bank State on 128K

On the 128K, `#7FFD` controls which RAM bank is paged at `#C000`. If the interrupted code has bank 3 paged and your NMI handler switches to bank 0 to access the menu data, you must restore bank 3 before `RETN`.

The port is write-only — you cannot read back the current state. Track it in a shadow variable that the main program updates whenever it changes banks.

```z80
nmi_handler:
    PUSH AF
    PUSH BC
    LD   A,(current_bank) ; Save desired bank
    LD   (saved_bank),A
    LD   A,#10             ; Switch to bank 0 for MF menu
    LD   BC,#7FFD
    OUT  (C),A
    ; ... NMI menu work ...
    LD   A,(saved_bank)   ; Restore
    OUT  (C),A
    POP  BC
    POP  AF
    RETN

current_bank:  DB  #10
saved_bank:    DB  0
```

This is the Hudson Hawk pattern generalized — see [im2_effects.md](im2_effects.md) for the same technique applied to maskable interrupts.

### Rule 4: Stack Discipline

The NMI acknowledge pushes the return address (2 bytes) onto whatever stack `SP` is currently pointing to. If the interrupted code had `SP` pointing at a 1-byte buffer or at the top of memory (`#FFFF`), the push will corrupt adjacent data or wrap into ROM.

NMI handlers must assume the worst about `SP`:

- Save the current `SP` to a fixed location
- Point `SP` at a dedicated NMI stack in safe RAM (e.g. `#FD00`–`#FD7F`)
- Do the handler's work
- Restore `SP`
- `RETN`

```z80
nmi_handler:
    LD   (saved_sp),SP    ; 20T — save current SP
    LD   SP,#FD40         ; 10T — switch to NMI stack
    ; ... work using stack freely ...
    LD   SP,(saved_sp)    ; 20T — restore
    RETN

saved_sp:  DW  0
```

The cost is 50 T-states of overhead, but the safety is essential — without this, NMI during stack-fragile code (like the Spectrum ROM's floating-point routines) will crash.

---

## NMI During Common Operations

The hardware asserts NMI asynchronously. It can fire at any point in the running program. Different operations have different tolerance for NMI:

| Operation | NMI safety | Reason |
|---|---|---|
| `HALT` | **Safe** | `HALT` finishes cleanly; NMI handler runs; `RETN` returns to `HALT` (or to the instruction after it) |
| Main loop in IM2 | **Safe** | Standard case; follow the rules above |
| Tape loading (ROM) | **Safe** | The ROM tape routine disables interrupts but checks for NMI; Multiface explicitly supports snapshotting during tape load |
| TR-DOS hook codes | **Catastrophic** | The WD1793 FDC is in the middle of a multi-byte DRQ stream; NMI fires, the FDC's DRQ is not serviced, bytes are lost, sector read fails silently and corrupts data |
| Direct WD1793 programming | **Catastrophic** | Same as TR-DOS but worse — there is no automatic retry logic to recover |
| +3 DOS RSX calls | **Mostly safe** | +3 DOS uses the UPD765 FDC which has deeper internal buffering (16 bytes vs WD1793's 1 byte), but long NMI handlers still cause data loss |
| ESXDOS `dma_read` | **Mostly safe** | ESXDOS uses IDE/SD which is block-buffered; NMI during a 512-byte sector read is tolerated if the handler is fast |
| Music player ISR | **Safe** | The music player is just code; NMI during it works fine (the player is paused while NMI runs) |
| Race-the-beam multicolor loop | **Disastrous** | The cycle-counted PUSH sequence is broken by NMI's 11-T acknowledge + handler time; visible tearing |

### Why NMI During Disk I/O Is Catastrophic

The WD1793 reads a sector one byte at a time, asserting DRQ (data request) for each byte. The CPU has approximately **32 T-states per byte** to read the byte from the FDC data register before the next byte arrives. If the CPU is late, the FDC sets the lost-data bit and the rest of the sector is garbage.

An NMI during this window consumes:

- 11 T-states: NMI acknowledge
- 2 × 11 T-states: minimum PUSH/POP for AF
- 10 T-states: minimum handler body (just `RETN`)
- 14 T-states: `RETN`
- **Total minimum: 57 T-states** — already over the 32-T-state budget

The result is silent data corruption. No error is raised by TR-DOS — the CRC check at the end of the sector will fail and TR-DOS will retry, but if your NMI fires repeatedly, you get stuck in a retry loop forever.

**Mitigation**: the DivIDE and DivMMC devices disable their magic button during ESXDOS disk operations via a software-controlled gate. The Multiface cannot do this — there is no software way to disable its button.

---

## Worked NMI Handler

A minimal NMI handler suitable for a custom interface (e.g. a homebrew cartridge with an NMI button) — follows all the rules:

```z80
    ORG  #0066             ; Z80 NMI vector

nmi_entry:
    ; --- Stack discipline ---
    LD   (nmi_saved_sp),SP
    LD   SP,nmi_stack_top

    ; --- Save everything ---
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL
    PUSH IX
    PUSH IY
    EX   AF,AF'
    EXX
    PUSH AF
    PUSH BC
    PUSH DE
    PUSH HL

    ; --- Save banking (128K) ---
    LD   A,(main_bank)
    LD   (nmi_saved_bank),A
    LD   A,#10             ; ROM 0, bank 0, screen 5
    LD   BC,#7FFD
    OUT  (C),A

    ; --- Do NMI work here ---
    CALL nmi_menu          ; Show menu, wait for key, etc.

    ; --- Restore banking ---
    LD   A,(nmi_saved_bank)
    OUT  (C),A

    ; --- Restore registers ---
    POP  HL
    POP  DE
    POP  BC
    POP  AF
    EXX
    EX   AF,AF'
    POP  IY
    POP  IX
    POP  HL
    POP  DE
    POP  BC
    POP  AF

    ; --- Restore SP ---
    LD   SP,(nmi_saved_sp)

    ; --- Acknowledge any NMI-source hardware ---
    ; (Multiface: OUT (#1F),A; custom hardware: as appropriate)

    RETN                   ; Restore IFF1 from IFF2

; --- Variables ---
nmi_saved_sp:    DW  0
nmi_saved_bank:  DB  0
main_bank:       DB  #10

; --- NMI stack (128 bytes, top-down) ---
    ORG  #FD80
nmi_stack_top:
```

This handler:

1. Saves `SP` and switches to a dedicated NMI stack in safe RAM
2. Saves all registers including shadow set
3. Saves the 128K bank state and switches to a known bank
4. Calls the user-facing NMI menu (which can freely use registers, stack, etc.)
5. Restores bank, registers, and stack
6. Returns with `RETN` to atomically restore IFF1

The total overhead is ~120 T-states plus the menu work. Acceptable for any non-disk-I/O context.

---

## Other NMI Sources

### DivIDE / DivMMC Magic Button

The DivIDE interface (and its modern successor, DivMMC) includes an NMI button used to invoke the ESXDOS NMI hook. Unlike the Multiface, the ESXDOS NMI handler is software-defined — the ESXDOS ROM is paged in via the interface's normal banking mechanism, and the handler reads the button press as a command to enter the ESXDOS dot-command selector.

The DivIDE/DivMMC hardware includes a software-controlled NMI gate: when ESXDOS is performing disk I/O, it disables the NMI button to prevent the catastrophic data corruption described above. This is why the DivIDE magic button is safer than the Multiface button during disk operations.

### Custom Hardware

Homebrew NMI sources include:

- **Real-time clock add-ons** that assert NMI at programmable intervals
- **Parallel port interfaces** that assert NMI on data-ready
- **Network interfaces** (Spectranet, ZXUNO) that assert NMI on packet reception

All of these share the same design requirement: the NMI handler must follow the rules above, and the NMI source must be acknowledged by the handler (typically via an `OUT` to a control port that clears the pending-interrupt flip-flop on the device).

---

## Cross-References

- **[interrupt_programming.md](interrupt_programming.md)** — Maskable interrupts (IM1/IM2), the foundation
- **[z80_interrupts.md](../../01_cpu/z80_interrupts.md)** — Z80 CPU-level interrupt architecture (IFF1/IFF2, NMI acknowledge cycle, RETN semantics)
- **[im2_effects.md](im2_effects.md)** — Maskable IM2 demoscene patterns; same register preservation rules apply
- **[im2_disk_music.md](im2_disk_music.md)** — Why disk operations cannot tolerate even short interrupts
- **[trdos_programming.md](../08_dos_tape/trdos_programming.md)** — TR-DOS pitfalls include NMI-safety warnings
- **[fdc_vg93.md](../../03_io/storage/fdc_vg93.md)** — WD1793 datasheet reference for DRQ timing

## Sources

- *Multiface 1, 128 and 3 — Technical Information* (kio, 2015) — circuit-level analysis of the 74LS74 flip-flop design
- *Multiface 128 Manual* (Romantic Robot) — official usage and NMI reliability notes
- *ZX Spectrum interrupt handling: maskable and NMI* (retrocomputing.stackexchange.com) — community Q&A on NMI skeleton handlers
- *Did any ZX Spectrum clones use the Z80's interrupt mode 0?* (retrocomputing.stackexchange.com) — context on which interrupt modes see real use
- *ESXDOS manual* (Garry Lancaster et al.) — DivIDE/DivMMC NMI behavior during disk I/O
