[← Plan](../../PLAN.md) · [Assembly](README.md)

# Stack, RST Vectors, and Calling Conventions — Z80 Function Call Discipline

Every non-trivial Z80 program is a stack discipline problem. The CPU has no parameter-passing convention, no calling convention, no language runtime — the stack is whatever you make of it. Push more than you pop, your program crashes. Pop in the wrong order, your program reads garbage. Trust a register that a subroutine trashed, your program computes wrong answers. There is no compiler to catch these mistakes; there is only the moment when the screen fills with vertical stripes and you realize that the return address you popped was actually the high byte of a pixel coordinate.

This article covers the **stack**, the **RST vectors**, and the **calling conventions** that bind them together. It is the third article in the [Assembly series](README.md) and assumes you have read [assembly_intro.md](assembly_intro.md) and the basics of [rom_calls.md](rom_calls.md). It does not duplicate the [Z80 architecture reference](../../01_cpu/z80_architecture.md) or the [interrupt programming article](../04_interrupts/interrupt_programming.md) — both of which touch stack mechanics for their own purposes.

> [!NOTE]
> If you are coming from C, Rust, or Go, the stack is a familiar concept but the Z80's stack is **manual**. There is no calling convention enforced by hardware. Every subroutine is free to use whatever registers it wants, push whatever it wants onto the stack, and pop in whatever order it wants. The contract between caller and callee is whatever you choose to write down in a comment.

---

## Stack Mechanics

The Z80 stack lives in main memory, not in a separate stack memory. The stack pointer (SP) is a 16-bit register that holds the address of the most recently pushed byte. The stack grows **downward** — PUSH decrements SP first, then writes; POP reads first, then increments SP.

```
                      Before PUSH BC:          After PUSH BC:
                      
#FF00 ┌──────────┐                          #FF00 ┌──────────┐
      │  ??      │                                │  ??      │
#FEFF │          │                          #FEFF │  ??      │
      │  ??      │                          #FEFE │  B       │ ← SP now points here
      │  ??      │                          #FEFD │  C       │
      │  ??      │                                │  ??      │
      │  ??      │                          #FEFD │  ??      │
      SP → #FEFE                                SP → #FEFC
```

### Stack Operations

| Instruction | Encoding | T-states | Effect |
|---|---|---|---|
| `PUSH BC` | `#C5` | 15 | SP -= 2; (SP) = C, (SP+1) = B |
| `PUSH DE` | `#D5` | 15 | SP -= 2; (SP) = E, (SP+1) = D |
| `PUSH HL` | `#E5` | 15 | SP -= 2; (SP) = L, (SP+1) = H |
| `PUSH AF` | `#F5` | 15 | SP -= 2; (SP) = F, (SP+1) = A |
| `PUSH IX` | `#DD #E5` | 15+4 = 19 | SP -= 2; write IX low, high |
| `PUSH IY` | `#FD #E5` | 15+4 = 19 | SP -= 2; write IY low, high |
| `POP BC` | `#C1` | 10 | B = (SP+1); C = (SP); SP += 2 |
| `POP DE` | `#D1` | 10 | (symmetric) |
| `POP HL` | `#E1` | 10 | (symmetric) |
| `POP AF` | `#F1` | 10 | (symmetric) |
| `POP IX` | `#DD #E1` | 14+4 = 18 | (symmetric, with prefix) |
| `POP IY` | `#FD #E1` | 14+4 = 18 | (symmetric, with prefix) |
| `CALL nn` | `#CD n n` | 17 | SP -= 2; (SP) = return-PC low; PC = nn |
| `RET` | `#C9` | 10 | PC = (SP); SP += 2 |
| `RST n` | `#C7`+n | 11 | SP -= 2; PC = n (n ∈ {0,8,16,24,32,40,48,56}) |
| `RETI` | `#ED #4D` | 14 | Like RET, plus signals end of interrupt to peripheral |
| `RETN` | `#ED #45` | 14 | Like RET, plus restores IFF1 from IFF2 |
| `EX (SP), HL` | `#E3` | 19 | Swap L ↔ (SP), H ↔ (SP+1) |
| `EX (SP), IX` | `#DD #E3` | 23 | Same for IX |

Note the T-state cost of IX/IY operations: every IX/IY instruction has a 4-T-state prefix overhead. `PUSH IX` is 19 T-states versus 15 for `PUSH HL`. In hot loops, prefer HL over IX/IY for register pushes.

### The SP Register and Where to Put It

The SP register is initialized by the ROM at boot to roughly `#FF60` on a 48K machine. From the programmer's perspective:

| SP location | Use case | Notes |
|---|---|---|
| `#FF60` (default, ROM-set) | Returning to BASIC after your code | ROM uses `#FF58`-`#FFFF` for its workspace; collision possible with deep BASIC programs |
| `#FFF0` (top of RAM) | Take-over program (game/demo) | Avoids ROM workspace; max 32 entries before hitting `#FF60` |
| `#8000` boundary (top of code) | Programs that need lots of stack | Risk: stack can grow into your code |
| Below `#4000` (in ROM) | Never | Reads return garbage; writes are ignored |
| `#4000`-`#5AFF` (screen) | Never | Stack operations would corrupt the display |
| `#5C00`-`#5CB6` (sysvars) | Never | Stack operations would corrupt ROM state |

For programs that take over the machine, set SP explicitly on entry:

```z80
start:
    DI                       ; we are about to change SP; disable interrupts
    LD   SP, #FFF0           ; stack now at top of RAM
    ; ... program body ...
```

The convention `#FFF0` (instead of `#FFFF`) leaves 16 bytes of safety margin. The ROM uses the area above `#FF60` for its own workspace; starting below that means our stack will not collide with the ROM if we briefly call back into it.

### Contended Memory and the Stack

On the 48K, the entire RAM is "contended" with the ULA during screen refresh — but contention is strongest in the `#4000`-`#7FFF` range. If the stack pointer is in this range, every PUSH/POP costs extra T-states during the screen-draw period (192 of the 311 scanlines per frame).

| Stack location | Contention |
|---|---|
| `#FF60` (default) | None (above `#8000`) |
| `#8000`-`#FFFF` | None |
| `#4000`-`#7FFF` | Contended — ULA steals cycles |
| Below `#4000` | ROM — pushes succeed but reads return ROM bytes |

For time-critical code, keep SP above `#8000`. The default ROM-set `#FF60` is fine for almost all programs.

---

## The Balanced Stack Rule

The single most important rule of Z80 assembly: **every `PUSH` must have a matching `POP`, every `CALL` must have a matching `RET`**. Stack imbalance is the most common cause of "my program worked once, then crashed on the second call."

### The Symmetric Pattern

```z80
my_routine:
    PUSH AF                 ; save what we trash
    PUSH BC
    PUSH DE
    PUSH HL
    ; ... body of routine ...
    POP  HL                 ; restore in reverse order
    POP  DE
    POP  BC
    POP  AF
    RET
```

Note the symmetry: PUSH order AF, BC, DE, HL becomes POP order HL, DE, BC, AF. **Last in, first out.**

### Stack Imbalance Symptoms

| Symptom | Likely cause |
|---|---|
| Program crashes on `RET` | Pushed more than popped; RET popped a wrong return address |
| Program returns to wrong place | Popped more than pushed; same effect |
| Screen fills with garbage | RET popped a low address (e.g., #0000), executing ROM as code |
| Program runs correctly once, crashes second time | Conditional PUSH/POP that fires only sometimes |
| Crash deep in ROM call | Interrupt fired during stack manipulation, ISR saw unbalanced stack |

### Conditional Pushes Need Discipline

```z80
; BAD: conditional push, unconditional pop
risky_routine:
    CP   #20
    JR   C, .skip_push      ; if A < 0x20, skip the push
    PUSH AF
.skip_push:
    ; ... do stuff ...
    POP  AF                 ; pops WRONG value if we skipped the push!
    RET
```

The fix is either to push unconditionally or to use a different control flow:

```z80
; GOOD option 1: unconditional push
risky_routine:
    PUSH AF
    CP   #20
    JR   C, .skip_work
    ; ... do stuff ...
.skip_work:
    POP  AF
    RET

; GOOD option 2: jump around the pop
risky_routine:
    CP   #20
    JR   C, .return_early
    PUSH AF
    ; ... do stuff ...
    POP  AF
.return_early:
    RET
```

### Early Returns

Every `RET` in a subroutine must pop the same number of bytes that were pushed since the subroutine entry. Multiple `RET` paths are fine as long as each one balances its own pushes:

```z80
; GOOD: every RET path balances its pushes
search_array:
    ; Entry: HL = array address, B = length, A = target
    PUSH BC
.search_loop:
    CP   (HL)
    JR   Z, .found          ; jump with one PUSH active
    INC  HL
    DJNZ .search_loop
    ; Not found
    POP  BC
    OR   A                  ; clear Z (A is the target, which is nonzero for our search)
    RET
.found:
    POP  BC
    SCF                     ; set carry = "found"
    RET
```

---

## RST Vectors — Single-Byte Calls

The Z80 provides eight **restart instructions**: `RST #00`, `RST #08`, `RST #10`, ..., `RST #38`. Each is encoded as a single byte (`#C7` for `#00`, `#CF` for `#08`, `#D7` for `#10`, incrementing by 8 in the encoding). Each restart is a `CALL` to its corresponding fixed address — 11 T-states, 1 byte, no operand.

Compared to `CALL nn` (3 bytes, 17 T-states), `RST` is **6 T-states faster and 2 bytes smaller**. In tight loops, this matters. The cost is that the target address must be one of the eight fixed vectors.

### The Eight Vectors

| Instruction | Encoding | Target | 48K ROM use |
|---|---|---|---|
| `RST #00` | `#C7` | `#0000` | Reset / cold boot. Calling `RST #00` reboots the Spectrum. |
| `RST #08` | `#CF` | `#0008` | Error handler. Does not return. HL = error code (negated). |
| `RST #10` | `#D7` | `#0010` | `PRINT_CHAR`. Prints A to current stream. |
| `RST #18` | `#DF` | `#0018` | `COLLECT_CHAR`. Fetches next char from current stream into A. |
| `RST #20` | `#E7` | `#0020` | `KEY_SCAN`. Scans keyboard. |
| `RST #28` | `#EF` | `#0028` | `FP_CALC`. Runs the floating-point calculator. HL = opcode list. |
| `RST #30` | `#F7` | `#0030` | Unused on 48K (used by 128K ROM for BCPL call). |
| `RST #38` | `#FF` | `#0038` | IM1 maskable interrupt service routine. Also called directly to invoke the ISR. |

### When to Use RST vs CALL

- **Use `RST`** when calling one of the eight fixed vectors. It is always faster and smaller.
- **Use `CALL`** for everything else. Any address, any time.

The 48K ROM was designed around RST heavily. `PRINT_CHAR` is invoked from dozens of places in the ROM via `RST #10` precisely because the single-byte encoding saves significant space when the routine is called many times. Your assembly programs should follow the same convention: prefer `RST #10` over `CALL #0010`.

### Custom RST Handlers

If your program is self-contained (e.g., a game that takes over the machine), you can replace the RST vectors in RAM. But the first 64 bytes of memory are in ROM — you cannot overwrite them on a standard Spectrum. The vectors are only redefinable on machines with RAM at low addresses (some Soviet clones, the Spectrum Next with custom configurations).

What you **can** do on any Spectrum is define your own restart-like conventions. Reserve a single byte in your code as a trampoline:

```z80
; Define a "custom RST" — a single-byte dispatch
fast_dispatch:
    JP   (HL)               ; jump to address in HL
```

Then `CALL fast_dispatch` is 3 bytes; if you have many call sites, this can save space.

### RST #08 — The Error Handler (Does Not Return)

`RST #08` is a special case. It is the ROM's error handler. The error code is in HL (negated; e.g., HL = `#FFDA` means error 38). The routine prints the error message, clears the stack, and exits to the editor. **Code after `RST #08` is unreachable.**

```z80
abort_program:
    LD   HL, #FFF2          ; error #0E = "Out of Data" (negated: -14 = #FFF2)
    RST  #08
    ; code here is unreachable
    RET
```

The byte following `RST #08` is sometimes used as an inline literal error code (read by the error handler). Different assemblers handle this differently. SjASMPlus treats the byte as a regular instruction; Pasmo may flag it. The safe pattern is to declare the byte explicitly:

```z80
    RST  #08
    DEFB #0E               ; error code byte
```

### RST #38 — The IM1 Interrupt Vector

On a 48K Spectrum with interrupts enabled and IM1 mode active (the default after BASIC hands control), the CPU calls `RST #38` 50 times per second (60 times on a US-spec machine). The routine at `#0038` increments `FRAMES`, scans the keyboard, and handles tape I/O.

Calling `RST #38` directly from your code is unusual but legal. It invokes the ISR immediately, which is useful for testing or for forcing a frame-tick. After `RST #38` returns, interrupts are still disabled (the routine does not end with EI); you must EI to re-enable.

---

## Calling Conventions

A calling convention is the contract between caller and callee: which registers are preserved, which are trashed, where parameters go, where the return value comes back. The Z80 has no enforced convention. Every project, every library, every compiler picks its own.

This section documents the conventions in common use, organized from simplest to most complex.

### Convention 1 — Caller-Saved (Default)

The simplest convention: the callee can trash any register. The caller saves anything it needs.

```z80
; Callee — trashes AF, BC, DE, HL freely
multiply:
    ; Entry: D, E = factors
    ; Exit: A = product (low byte)
    PUSH BC
    LD   B, 0
    LD   C, D
    LD   A, 0
.mul_loop:
    ADD  A, C
    DEC  E
    JR   NZ, .mul_loop
    POP  BC
    RET

; Caller — saves what it needs across the call
    PUSH HL                 ; I need HL after the call
    LD   D, 7
    LD   E, 6
    CALL multiply
    LD   (result), A        ; A = 42
    POP  HL
```

**Pros**: simple to understand, caller pays only for what it needs.
**Cons**: caller must know which registers the callee trashes. Without documentation, the caller must defensively save everything.

### Convention 2 — Callee-Saved (Symmetric)

The callee saves everything it touches. The caller can call without worrying about its registers.

```z80
multiply:
    ; Entry: D, E = factors
    ; Exit: A = product
    PUSH AF                 ; save everything I might trash
    PUSH BC
    PUSH DE
    PUSH HL
    LD   H, 0
    LD   L, D
    LD   B, E
    LD   A, 0
.mul_loop:
    ADD  A, L
    DJNZ .mul_loop
    POP  HL
    POP  DE
    POP  BC
    POP  AF
    RET
```

**Pros**: caller does not need to know what the callee trashes.
**Cons**: callee always pays full PUSH/POP cost, even if the caller did not need those registers. Wasteful for short routines.

### Convention 3 — Register Parameters

Pass parameters in registers. The standard mapping:

| Parameter type | Register convention |
|---|---|
| First 8-bit value | A |
| Second 8-bit value | B (or C) |
| First 16-bit value (pointer) | HL |
| Second 16-bit value | DE |
| Third 16-bit value | BC |
| Index/offset | IX or IY |

This is the convention used by virtually every ROM routine and most assembly libraries.

```z80
memset:
    ; Entry: HL = address, A = value, BC = count
    ; Exit: HL points one past the end of the filled region
    LD   (HL), A
    LD   D, H
    LD   E, L
    INC  DE
    DEC  BC
    RET  Z                  ; if BC was 1, done
    LDIR
    RET

; Caller
    LD   HL, screen_buffer
    LD   A, #FF
    LD   BC, 6144
    CALL memset
```

### Convention 4 — Stack Parameters

When there are too many parameters to fit in registers, push them onto the stack before the call. The callee reads them via indexed addressing.

```z80
; Caller — push parameters right-to-left (C-style)
    LD   HL, format_string
    PUSH HL                 ; first parameter
    LD   A, 42
    PUSH AF                 ; second parameter
    CALL printf
    POP  AF                 ; clean up stack (caller cleans)
    POP  HL

; Callee — read parameters from stack
printf:
    ; Stack layout (top to bottom):
    ;   return address (2 bytes) ← SP
    ;   second parameter (2 bytes)
    ;   first parameter (2 bytes)
    PUSH AF
    PUSH HL
    LD   HL, 6              ; offset to first parameter
    ADD  HL, SP
    ; HL now points at first parameter
    LD   E, (HL)            ; low byte of format_string
    INC  HL
    LD   D, (HL)            ; high byte
    ; ... do work ...
    POP  HL
    POP  AF
    RET
```

The tricky part is calculating the stack offset. After two PUSHes inside the callee (4 bytes) plus the return address pushed by CALL (2 bytes), the first parameter is at SP+6. With more or fewer PUSHes, the offset changes.

### Convention 5 — Return Value in A or HL

Standard return value conventions:

| Return type | Register |
|---|---|
| 8-bit value | A |
| 16-bit value | HL |
| 32-bit value | DE:HL (high:low) |
| Boolean (true/false) | Z flag (Z = false, NZ = true) or carry (C = true) |
| Pointer | HL |
| Error/success | Carry flag (C = error, NC = success) |

Pick one and stick with it across your project. Mixing conventions within one project is a frequent source of bugs.

### Convention Combinations

In practice, most projects use a hybrid: register parameters for the common case (1-3 params), stack parameters when there are many, callee-saved for the most-called routines, and caller-saved for everything else. Document the convention in a comment header for each routine.

---

## Shadow Registers — Two Banks for the Price of One

The Z80 has two complete sets of general-purpose registers: the **primary** set (AF, BC, DE, HL) and the **shadow** set (AF', BC', DE', HL'). Only one set is active at a time. Two instructions swap them:

| Instruction | Encoding | T-states | Effect |
|---|---|---|---|
| `EX AF, AF'` | `#08` | 4 | Swap AF with AF' (F and flags too) |
| `EXX` | `#D9` | 4 | Swap BC, DE, HL with their shadows |

The swap is **instantaneous** — a flip-flop toggles which bank is active. No data is copied. After `EXX`, what was BC' is now BC; the old BC is hidden in the shadow set. Swap back with another `EXX`.

### Use Case 1 — Interrupt-Safe Context Switch

The classic use of shadow registers is inside an ISR. The ISR swaps to shadow registers on entry, does its work, swaps back on exit:

```z80
isr:
    EX   AF, AF'            ; swap to shadow AF
    EXX                     ; swap to shadow BC/DE/HL
    ; ... ISR body uses primary registers, but they're really shadows from main's perspective ...
    EXX                     ; swap back
    EX   AF, AF'
    EI
    RETI
```

This pattern leaves the main program's registers completely untouched. The cost is 16 T-states of swap overhead per interrupt — far cheaper than 8 PUSH/POP pairs (240+ T-states).

### Use Case 2 — Inner-Loop Acceleration

If you have a tight inner loop that needs many registers, swap to shadows at the top of the loop and swap back at the bottom:

```z80
fast_copy:
    EXX                     ; shadow BC/DE/HL are now primary
    ; The original BC, DE, HL are hidden
    LD   B, 32              ; this uses shadow B
.copy_loop:
    LD   A, (HL)            ; this uses shadow HL
    LD   (DE), A            ; this uses shadow DE
    INC  HL
    INC  DE
    DJNZ .copy_loop
    EXX                     ; swap back — original BC/DE/HL restored
    RET
```

The caller's BC, DE, HL are preserved for free, no PUSH/POP.

### When NOT to Use Shadow Registers

Shadow registers are dangerous in two situations:

1. **Reentrant code**: if a routine uses `EXX` and is interrupted during the swap, the ISR's own `EXX` (if any) will collide. Solution: ISRs should always save and restore shadow state if main code uses them.
2. **Recursive routines**: each recursion level needs its own copy of the shadow state. There are only two banks; recursion deeper than 2 levels cannot use shadow registers.

---

## Stack as Temporary Storage

PUSH/POP is the cheapest way to save a register for a few instructions. The pattern:

```z80
    PUSH AF                 ; save A
    LD   A, (some_var)      ; clobber A
    CALL some_routine
    LD   (some_var), A
    POP  AF                 ; restore A
```

This works for short-lived saves (a few instructions). For longer-lived saves, use a memory variable instead — the stack pointer is too easy to forget about.

### The Self-Adjusting Stack (INC SP / DEC SP)

You can manually adjust SP to discard pushed values:

```z80
    PUSH AF
    PUSH BC
    PUSH DE
    ; ... do work that does not need these values ...
    LD   HL, 6              ; bytes to discard
    ADD  HL, SP
    LD   SP, HL             ; SP += 6
```

Or use `INC SP` twice to discard one register (2 bytes):

```z80
    INC  SP
    INC  SP                 ; effectively "POP and discard"
```

This is rare in modern assembly but appears in some compact code and in compiler-emitted code (especially SDCC).

### EX (SP), HL — Swap Top of Stack

`EX (SP), HL` swaps HL with the top two bytes of the stack. Useful for:

- Modifying a return address (rare; usually a sign of trampoline tricks)
- Reading the top of the stack without popping
- Implementing a peek-and-modify

```z80
    ; Change the return address to return to a different location
    LD   HL, alt_return
    EX   (SP), HL           ; HL now = old return address, stack now = alt_return
    RET                     ; returns to alt_return
```

---

## Computed Calls — JP (HL) and the Fake CALL

The Z80 has `JP (HL)`, `JP (IX)`, and `JP (IY)` — indirect jumps through a register. But it has **no `CALL (HL)`** instruction. The workaround is a trampoline: push the target address onto the stack, then `RET`:

```z80
; Computed CALL — invoke the address in HL
call_hl:
    JP   (HL)               ; the simplest version: jump, not call

; True computed CALL — return address is pushed first
call_hl_with_return:
    ; Entry: HL = address to call
    ; Effect: CALL (HL)
    EX   (SP), HL           ; swap HL with return address of THIS function
    JP   (HL)               ; jump to HL (which is now the caller's return-1 address)
```

This is a classic trick. The pattern is sometimes called "the RST trick" or "the JP (HL) idiom".

### Dispatch Tables

The most common use of computed calls is the **dispatch table** — an array of addresses, indexed by some value:

```z80
command_table:
    DEFW cmd_help           ; index 0
    DEFW cmd_load           ; index 1
    DEFW cmd_save           ; index 2
    DEFW cmd_quit           ; index 3

dispatch:
    ; Entry: A = command index (0-3)
    ; Modifies: AF, HL
    ADD  A, A               ; A *= 2 (each entry is 2 bytes)
    LD   L, A
    LD   H, 0
    LD   DE, command_table
    ADD  HL, DE             ; HL = address of command entry
    LD   E, (HL)
    INC  HL
    LD   D, (HL)            ; DE = address of command
    EX   DE, HL             ; HL = command address
    JP   (HL)               ; tail call (no return expected)
```

Dispatch tables are the foundation of state machines and command processors. See [assembly_patterns.md](assembly_patterns.md) for the full treatment.

---

## Stack Frame Layout for Local Variables

For larger subroutines with many local variables, a **stack frame** gives each invocation its own private storage. The pattern is borrowed from C compilers:

```z80
my_function:
    ; Entry: parameter1 in A, parameter2 in HL
    ; Locals: local1 (2 bytes), local2 (2 bytes), local3 (1 byte) = 5 bytes
    PUSH IX
    LD   IX, 0
    ADD  IX, SP             ; IX = original SP
    LD   HL, -5
    ADD  HL, SP
    LD   SP, HL             ; allocate 5 bytes for locals
    
    ; Now locals are accessed as IX-2, IX-4, IX-5 (offsets from saved SP)
    ; (IX-1) = local1 high, (IX-2) = local1 low
    ; (IX-3) = local2 high, (IX-4) = local2 low
    ; (IX-5) = local3
    
    LD   (IX-1), B          ; store B as local1 high
    LD   (IX-5), A          ; store A as local3
    
    ; ... function body ...
    
    ; Cleanup
    LD   SP, IX             ; restore SP
    POP  IX                 ; restore caller's IX
    RET
```

This is verbose but gives you true local variables. The C compiler (z88dk/sccz80 and z88dk/zsdcc) uses this pattern internally — see [c_interop.md](c_interop.md).

### When to Use Stack Frames

| Situation | Recommendation |
|---|---|
| Few locals, non-recursive | Use static memory addresses (variables in the .bss section) |
| Many locals, non-recursive | Static memory is fine; reserve a block per routine |
| Recursive | Stack frame required |
| Reentrant (called from ISR and main) | Stack frame required |
| Compiler-emitted code | Stack frame is automatic |

For most hand-written assembly, static memory is simpler and faster. Use stack frames only when recursion or reentrancy is required.

---

## The ERR_SP Trick — Try/Catch Around ROM Calls

The system variable `ERR_SP` at `#5C3D` (IY+3) holds the address of the error handler. When `RST #08` is invoked, the ROM jumps to the address at `ERR_SP`. By pushing your own address onto ERR_SP before a ROM call, you can intercept errors.

This pattern, mentioned briefly in [rom_calls.md](rom_calls.md), deserves a fuller treatment here because it is a stack trick.

```z80
try_catch:
    ; Set up the try/catch
    ; Push the catch address onto the stack first
    LD   HL, catch_handler
    PUSH HL
    
    ; Update ERR_SP to point at our pushed address
    ; ERR_SP should be #5C3D
    LD   (#5C3D), SP        ; ERR_SP = current SP
    
    ; Now call the risky routine
    LD   A, #FF
    CALL #21CC              ; LOAD — might error
    
    ; Success path: clean up our pushed handler
    POP  HL                 ; discard the catch_handler address
    JR   success

catch_handler:
    ; Error path: ROM jumped here via ERR_SP
    ; A = error code (already negated)
    ; ... handle the error ...
    RET
```

The pattern is delicate. Key facts:

1. **ERR_SP must point to a stack location**, not a fixed address. The ROM uses `RET` semantics to pop the next handler.
2. **Nested try/catch** requires pushing multiple handler addresses.
3. **The stack at error time is unpredictable** — the ROM has cleared it as part of the error recovery.

For most programs, the simpler approach is to check return codes from ROM routines (when they have them) and avoid `RST #08`.

---

## Recursion and Reentrancy

The Z80 stack supports recursion naturally — each `CALL` pushes a return address, and recursive routines simply allocate their own stack frames for locals. The limit is stack depth: on a 48K Spectrum with SP at `#FFF0`, you have roughly 32 KB of stack, allowing ~1000 levels of recursion for a routine with a 32-byte stack frame.

### Classic Example: Recursive Factorial

```z80
factorial:
    ; Entry: A = n (0-5 for 8-bit result, 0-7 for reasonable)
    ; Exit: A = n!
    ; Modifies: AF, BC
    CP   0
    JR   Z, .base_case
    PUSH AF                 ; save n
    DEC  A
    CALL factorial          ; recurse with n-1
    POP  BC                 ; restore n into B
    LD   C, A               ; C = (n-1)!
    LD   A, 0
.mul_loop:
    ADD  A, C               ; accumulate
    DJNZ .mul_loop          ; multiply B times
    RET
.base_case:
    LD   A, 1
    RET
```

This works but is wasteful — recursion on the Z80 should be reserved for genuinely recursive data structures (tree traversal, parsing). For most problems, iteration is faster and smaller.

### Reentrancy Requirements

A subroutine is **reentrant** if it can be called from multiple contexts (e.g., main code and an ISR) without conflicts. The requirements:

1. **No static memory writes** — all locals must be on the stack or in registers
2. **No global state mutation** — the routine must not modify any global variables
3. **No self-modifying code** — code that patches itself is not reentrant

Most assembly routines are not reentrant by default. Making them reentrant requires either discipline (stack-only locals) or disabling interrupts during the call.

---

## Pitfalls and Common Mistakes

### Pitfall 1: POP Order Mismatch

```z80
; BAD: pushed BC, DE, HL but popped in wrong order
    PUSH BC
    PUSH DE
    PUSH HL
    ; ... do work ...
    POP  BC                 ; was HL
    POP  HL                 ; was DE
    POP  DE                 ; was BC
```

The compiler/assembler does not check this. The result is silent register corruption: BC has what HL had, HL has what DE had, and DE has what BC had. Always POP in **reverse order of PUSH**.

### Pitfall 2: Forgetting that PUSH IX Costs More

`PUSH IX` is 19 T-states (4 prefix + 15). `PUSH HL` is 15 T-states. In a tight inner loop with frequent PUSH/POP, IX is meaningfully slower than HL. Reserve IX/IY for cases where you genuinely need indexed addressing (stack frame access, table walks).

### Pitfall 3: Shadow Registers in ISR Without Swap

```z80
; BAD: ISR uses primary BC but does not swap to shadows
isr:
    ; ... modifies BC ...
    EI
    RETI
main:
    LD   B, 10
    LD   C, 0
.loop:
    HALT                    ; wait for interrupt
    ; ... but the ISR trashed BC!
    DJNZ .loop
```

Either swap to shadows on ISR entry/exit, or save the registers the ISR uses:

```z80
isr:
    PUSH BC
    ; ... modifies BC ...
    POP  BC
    EI
    RETI
```

### Pitfall 4: CALL Without RET (or Vice Versa)

```z80
; BAD: used JP to enter a subroutine, will RET to wrong place
    JP   some_routine
some_routine:
    ; ... work ...
    RET                     ; pops garbage from stack
```

If you `JP` to a routine that ends with `RET`, the RET pops whatever is at the top of the stack — typically a return address from a previous CALL or a stale value. Always use `CALL` to enter a routine that ends with `RET`, or use `JP` for both (tail-call optimization).

### Pitfall 5: Stack Pointer in Contended Memory

```z80
; BAD: SP set inside the contended range
    LD   SP, #5000          ; right in the pixel framebuffer!
```

The framebuffer is at `#4000`-`#5AFF`. Stack writes here corrupt the display. Stack reads here return pixel data. Always set SP to uncontended RAM (`#8000`-`#FFFF`).

### Pitfall 6: DI Without EI

```z80
; BAD: DI around a routine that never returns
    DI
    CALL some_routine
    ; if some_routine crashes, interrupts stay off forever
```

If `some_routine` might crash, you want interrupts on so the user can recover with BREAK. Use a try/catch pattern or accept that crashing with interrupts off requires a reset.

---

## Cross-References

- **[assembly_intro.md](assembly_intro.md)** — first contact; mentions stack basics
- **[rom_calls.md](rom_calls.md)** — uses ERR_SP and discusses IY preservation around ROM calls
- **[assembly_patterns.md](assembly_patterns.md)** — dispatch tables, state machines, and coroutine patterns build on the stack discipline here
- **[c_interop.md](c_interop.md)** — C compilers' calling conventions are stack frames in action
- **[z80_architecture.md](../../01_cpu/z80_architecture.md)** — register file internals, shadow register hardware
- **[z80_interrupts.md](../../01_cpu/z80_interrupts.md)** — RETI, RETN, and the IFF1/IFF2 flip-flops
- **[interrupt_programming.md](../04_interrupts/interrupt_programming.md)** — ISR design patterns, including shadow register use
- **[z80_coding_practices.md](../../01_cpu/z80_coding_practices.md)** — register discipline and instruction selection

## References

- *Z80 CPU User Manual* by Zilog — official reference for stack operations and instruction timings
- *Programming the Z80* by Rodnay Zaks — calling conventions and stack discipline
- *The Complete Spectrum ROM Disassembly* by Ian Logan and Frank O'Hara — shows the ROM's calling convention in action
