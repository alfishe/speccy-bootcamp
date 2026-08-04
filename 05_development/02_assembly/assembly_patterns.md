[← Plan](../../PLAN.md) · [Assembly](README.md)

# Assembly Design Patterns — State Machines, Dispatch Tables, Table-Driven Code

A persistent myth about assembly language is that it produces "unstructured goto soup." The truth is the opposite: 1980s and 1990s ZX Spectrum software — commercial games, demoscene productions, productivity tools — was often **more disciplined than contemporary C**. Programmers had no compiler to enforce structure, so the good ones invented their own. The result was a body of reusable patterns: state machines encoded as switch tables, dispatch tables for plugin architectures, table-driven level data, coroutine-style stack swapping for background tasks, self-modifying code for hot loops.

This article catalogs the structural patterns that turn a pile of instructions into a maintainable program. It is the fourth article in the [Assembly series](README.md) and assumes you have read [assembly_intro.md](assembly_intro.md), [rom_calls.md](rom_calls.md), and [stack_and_rst.md](stack_and_rst.md). It is **not** a rehash of [z80_coding_practices.md](../../01_cpu/z80_coding_practices.md) — that article covers micro-level instruction selection (register allocation, loop construction, instruction timing). This article covers **macro-level structure**: how to organize a 5,000-line program so it does not collapse under its own weight.

> [!NOTE]
> The patterns in this article are language-agnostic — the same patterns appear in C, Rust, and Python programs. What makes them distinctive in assembly is that **the programmer enforces them by convention**, not by language support. There is no `enum class` for state values, no `interface` for plugins, no `struct` for data layouts. There are only labels, bytes, and your discipline.

---

## Why Patterns Matter in Assembly

Every assembly program of meaningful size faces the same problems:

| Problem | Symptom when ignored |
|---|---|
| **State management** | Many unrelated flags and counters; impossible to reason about program flow |
| **Extensibility** | Adding a new feature requires editing 20 different places |
| **Data vs code** | Levels, enemies, and dialogs end up hard-coded as instruction sequences |
| **Hot path vs cold path** | Everything runs at the same speed; no budget for the 50fps loop |
| **Modularity** | Changing one subsystem breaks three others; cross-cutting concerns everywhere |
| **Reentrancy** | ISRs and main code corrupt each other's state |

The patterns in this article are time-tested answers to these problems. Each one has a name, a typical structure, and a clear "when to use" guidance.

### Cost-Benefit Mindset

Every pattern has a cost. A dispatch table costs N×2 bytes for the table plus the dispatch code. A state machine costs the state variable plus the per-state handlers. Self-modifying code costs the patching logic. The benefit is **maintainability and extensibility** — features you only appreciate when the program grows.

For a 256-byte demo, none of these patterns matter. For a 32 KB game or a 16 KB demo engine, they are the difference between shipping and giving up.

---

## State Machines

A state machine is the most common structural pattern in assembly programs. It models the program (or a subsystem) as a finite set of **states** and **transitions** between them.

### Moore vs Mealy

| Type | Output depends on | In assembly terms |
|---|---|---|
| **Moore** | Current state only | Per-state handler returns the next state |
| **Mealy** | Current state + input | Per-state handler reads input and computes the next state |

Most assembly state machines are Mealy-style: the handler reads input (keyboard, timer, sprite collision) and decides the next state based on both state and input.

### The Pattern

```z80
; State variable — a single byte holding the current state index
state:   DEFB 0              ; 0 = title, 1 = playing, 2 = paused, 3 = game_over

; State handler table — addresses of per-state routines
state_table:
    DEFW state_title
    DEFW state_playing
    DEFW state_paused
    DEFW state_game_over

; Main loop — call the current state's handler once per frame
main_loop:
    HALT                     ; wait for vertical blank
    LD   A, (state)          ; get current state
    ADD  A, A                ; * 2 (each entry is 2 bytes)
    LD   L, A
    LD   H, 0
    LD   DE, state_table
    ADD  HL, DE              ; HL = address of state entry
    LD   E, (HL)
    INC  HL
    LD   D, (HL)             ; DE = address of handler
    EX   DE, HL              ; HL = handler address
    JP   (HL)                ; tail call to handler
```

Each state handler follows a convention: do its work, possibly change the state variable, return.

```z80
state_title:
    ; Display title, wait for any key to start the game
    CALL draw_title_screen
    CALL #031E               ; KEY_INPUT
    JR   C, .no_key          ; no key, stay in title
    LD   A, 1                ; transition to playing
    LD   (state), A
.no_key:
    JP   main_loop           ; return to top of loop

state_playing:
    CALL read_input
    CALL update_player
    CALL update_enemies
    CALL draw_frame
    ; Check for game-over condition
    LD   A, (player_lives)
    AND  A
    JR   NZ, .still_alive
    LD   A, 3                ; transition to game_over
    LD   (state), A
.still_alive:
    JP   main_loop

; ... state_paused and state_game_over follow the same pattern ...
```

### Hierarchical State Machines

When the state space gets large, group states hierarchically. The top level has "phases" (menu, game, ending). Within "game," there are sub-states (playing, paused, inventory). The top-level dispatcher calls a per-phase dispatcher, which in turn dispatches to per-substate handlers.

```z80
phase_table:
    DEFW phase_menu
    DEFW phase_game
    DEFW phase_ending

phase_game:
    ; Sub-dispatcher for the game phase
    LD   A, (game_substate)
    ADD  A, A
    LD   L, A
    LD   H, 0
    LD   DE, game_substate_table
    ADD  HL, DE
    LD   E, (HL)
    INC  HL
    LD   D, (HL)
    EX   DE, HL
    JP   (HL)

game_substate_table:
    DEFW substate_playing
    DEFW substate_paused
    DEFW substate_inventory
```

This avoids the combinatorial explosion that comes from flattening everything into one state variable.

### When to Use a State Machine

| Situation | Recommendation |
|---|---|
| Game flow (title → game → game over) | Yes — classic state machine |
| Menu navigation (sub-menu, parent menu, modal) | Yes |
| Animation phases (intro, loop, outro) | Yes |
| Player status (alive, dying, respawn) | Yes |
| Simple if/else logic | No — just use branches |
| Linear code with no phases | No — no states to manage |

---

## Jump Tables / Dispatch Tables

A jump table (also called a dispatch table or function pointer table) is an array of addresses, indexed by some value to determine which routine to call. The state machine in the previous section uses a jump table internally; here we treat the pattern in its own right.

### Basic Structure

```z80
; A table of N function addresses
handlers:
    DEFW handler_0
    DEFW handler_1
    DEFW handler_2
    DEFW handler_3
    ; ... as many as needed

; Dispatch: A = index, calls handler at that index
dispatch:
    ADD  A, A                ; A *= 2 (each entry is 2 bytes)
    LD   L, A
    LD   H, 0
    LD   DE, handlers
    ADD  HL, DE              ; HL = address of table entry
    LD   A, (HL)
    INC  HL
    LD   H, (HL)
    LD   L, A                ; HL = handler address
    JP   (HL)                ; tail call
```

This is the **primitive operation** of every C `switch` statement, every Python `dispatch` decorator, every Lua table-of-functions. The cost is 6 bytes for the dispatch code plus 2 bytes per entry. The benefit is **O(1) dispatch** with no conditional branches.

### Variant — Indexed CALL (Returns)

If the handlers need to return to the caller of `dispatch`, use a computed CALL pattern instead of `JP (HL)`:

```z80
dispatch_call:
    ; Entry: A = index
    ; Effect: CALL handler at that index, returns to caller of dispatch_call
    ADD  A, A
    LD   L, A
    LD   H, 0
    LD   DE, handlers
    ADD  HL, DE
    LD   E, (HL)
    INC  HL
    LD   D, (HL)             ; DE = handler
    PUSH DE                  ; push handler address
    RET                      ; "return" to handler — when handler RETs, returns to dispatch_call's caller
```

This is the "computed CALL via PUSH + RET" trick. It is slightly less efficient than a direct `CALL (HL)` would be (if such an instruction existed), but it works.

### Bounds Checking

Production code should bounds-check the index before indexing into the table. Otherwise, an out-of-range index reads garbage and jumps to a random address — usually a crash.

```z80
dispatch_safe:
    ; Entry: A = index, B = table size
    CP   B
    JR   NC, .out_of_range
    ADD  A, A
    LD   L, A
    LD   H, 0
    LD   DE, handlers
    ADD  HL, DE
    LD   A, (HL)
    INC  HL
    LD   H, (HL)
    LD   L, A
    JP   (HL)
.out_of_range:
    ; ... handle error ...
    RET
```

### Example — Command Processor

A text command processor maps command names to handler routines. The pattern:

```z80
command_table:
    ; Each entry: 3 bytes pointer to name, 2 bytes pointer to handler
    DEFW cmd_help_name
    DEFW cmd_help
    DEFW cmd_load_name
    DEFW cmd_load
    DEFW cmd_save_name
    DEFW cmd_save
    DEFW 0                   ; sentinel — end of table

cmd_help_name:   DB "help", 0
cmd_load_name:   DB "load", 0
cmd_save_name:   DB "save", 0

process_command:
    ; Entry: HL = command string (null-terminated)
    ; Modifies: AF, BC, DE, HL
    LD   DE, command_table
.search_loop:
    LD   A, (DE)
    OR   A
    JR   Z, .not_found       ; sentinel — end of table
    ; Save DE and HL for the string compare
    PUSH DE
    PUSH HL
    ; Get the name pointer
    LD   A, (DE)
    INC  DE
    LD   L, A
    LD   A, (DE)
    LD   H, A                ; HL = name
    INC  DE                  ; DE now points at handler
    PUSH DE                  ; save handler pointer
    EX   DE, HL              ; DE = name, HL = handler slot
    CALL strcmp
    POP  HL                  ; restore handler slot
    POP  HL                  ; restore input string
    POP  DE                  ; restore table pointer
    JR   Z, .found
    ; Advance DE past the handler (2 bytes)
    INC  DE
    INC  DE
    INC  DE                  ; next entry (4 bytes per entry)
    JR   .search_loop
.found:
    ; DE points at handler; call it
    INC  DE
    LD   A, (DE)
    INC  DE
    LD   L, A
    LD   A, (DE)
    LD   H, A
    EX   DE, HL              ; DE = handler
    ; (use PUSH DE + RET to call)
    PUSH DE
    RET
.not_found:
    SCF                      ; carry = not found
    RET
```

This is the same pattern used by every text-adventure parser and every BASIC interpreter.

---

## Table-Driven Code — Data-Oriented Design

Before "data-oriented design" was a 2010s game-dev buzzword, assembly programmers were doing it. The pattern: store levels, enemies, dialogs, and other content as **binary data tables**, then write generic iteration code that processes any table.

### Enemy Spawn Table

Instead of hard-coding enemy waves:

```z80
; BAD — hard-coded
spawn_wave_1:
    LD   A, 10
    LD   (enemy_x), A
    LD   A, 20
    LD   (enemy_y), A
    LD   A, ENEMY_GOBLIN
    LD   (enemy_type), A
    CALL spawn_enemy
    LD   A, 50
    LD   (enemy_x), A
    LD   A, 30
    LD   (enemy_y), A
    LD   A, ENEMY_ORC
    LD   (enemy_type), A
    CALL spawn_enemy
    RET
```

Use a data table:

```z80
; GOOD — table-driven
wave_1:
    DEFB 10, 20, ENEMY_GOBLIN
    DEFB 50, 30, ENEMY_ORC
    DEFB 0                   ; sentinel — end of wave

spawn_wave:
    ; Entry: HL = wave table address
.spawn_loop:
    LD   A, (HL)
    AND  A
    RET  Z                   ; sentinel
    LD   (enemy_x), A
    INC  HL
    LD   A, (HL)
    LD   (enemy_y), A
    INC  HL
    LD   A, (HL)
    LD   (enemy_type), A
    INC  HL
    PUSH HL
    CALL spawn_enemy
    POP  HL
    JR   .spawn_loop

; Caller
    LD   HL, wave_1
    CALL spawn_wave
```

### Benefits

- **Same code, many waves.** Add a new wave by adding new data; no new code.
- **Data-driven balancing.** Designers can tune enemy placement without touching code.
- **Compressed representation.** A wave of 50 enemies is 150 bytes of data, not 50×8 = 400 bytes of instructions.
- **Separable asset pipeline.** Wave data can be generated by a level editor, exported as `.bin`, and included via `INCBIN`.

### Tradeoffs

- **Fixed format.** Every entry must use the same byte layout. Special cases need a flag byte or a separate "unusual spawn" table.
- **Indirection cost.** Each table entry requires a load, a write, and an increment. Hard-coded `LD` instructions are faster (no table read overhead).
- **Harder to debug.** Wrong byte in a table produces a subtle bug; wrong instruction produces a loud crash.

For most game and application code, the benefits outweigh the costs. Use the table-driven approach for anything with more than 5-10 instances.

### Level Data as Binary Tables

A complete level is typically a sequence of enemy waves, scripted events, and tile data. One representation:

```z80
level_1:
    ; Header: length, music track, starting position
    DEFW level_1_end - $
    DEFB MUSIC_TRACK_3
    DEFW #4000              ; start address
    
    ; Wave 1: 5 goblins in a row
    DEFB EVENT_WAVE
    DEFW wave_1
    
    ; Pause for 60 frames (1.2 seconds)
    DEFB EVENT_PAUSE
    DEFW 60
    
    ; Dialog
    DEFB EVENT_DIALOG
    DEFW dialog_boss_intro
    
    ; Wave 2: boss fight
    DEFB EVENT_WAVE
    DEFW wave_boss
    
    ; End
    DEFB EVENT_END
level_1_end:
```

The level player is a small loop that reads events and dispatches:

```z80
play_level:
    ; Entry: HL = level data address
    LD   E, (HL)
    INC  HL
    LD   D, (HL)             ; DE = level length
    INC  HL
    ; (Skip header — music, start)
    INC  HL
    INC  HL
    INC  HL
.event_loop:
    LD   A, (HL)
    CP   EVENT_END
    RET  Z
    ; Dispatch on event type
    ; ... switch on A, handle each event type ...
    JR   .event_loop
```

This is the architecture of every JRPG, every platformer, every shoot-em-up. The same engine plays any level by pointing it at different data.

---

## Function Pointer Tables — Plugin Architectures

A function pointer table is a jump table with a twist: the table is **populated at runtime**, allowing different code to be plugged in. This is the foundation of plugin architectures and polymorphism.

### Use Case — Sound Driver Abstraction

Suppose your game supports both 48K (beeper) and 128K (AY-3-8912) machines. The sound API is the same (`play_effect`, `play_music`, `stop_sound`), but the implementation differs. Use a function table:

```z80
; Sound driver interface — three function pointers
sound_driver:
sd_init:    DEFW 0           ; filled in at boot
sd_play:    DEFW 0
sd_stop:    DEFW 0

; Boot-time detection — install the right driver
install_sound_driver:
    ; Detect machine type (check sysvar or port)
    LD   A, (#5C7A)         ; MARGIN or similar sysvar
    ; (simplified — real detection is more involved)
    CP   48                 ; 48K?
    JR   Z, .beeper
    ; 128K
    LD   HL, ay_init
    LD   (sd_init), HL
    LD   HL, ay_play
    LD   (sd_play), HL
    LD   HL, ay_stop
    LD   (sd_stop), HL
    RET
.beeper:
    LD   HL, beep_init
    LD   (sd_init), HL
    LD   HL, beep_play
    LD   (sd_play), HL
    LD   HL, beep_stop
    LD   (sd_stop), HL
    RET

; Game code calls the driver through the function pointers
play_sound_effect:
    ; Entry: A = effect number
    LD   HL, (sd_play)
    JP   (HL)               ; tail call into the driver
```

This pattern lets you swap implementations without changing call sites. It is exactly how C++ vtables work.

---

## Coroutine Patterns — Stack Swapping for Concurrent Tasks

A coroutine is a routine that can be paused and resumed. On a single-threaded Z80, coroutines provide concurrency without an OS scheduler. The trick: save the current stack pointer, switch to another stack, return. When the other coroutine pauses, swap back.

### The Basic Swap

```z80
task_a_sp:   DEFW 0          ; saved SP for task A
task_b_sp:   DEFW 0          ; saved SP for task B

task_switch_to_a:
    LD   HL, (task_b_sp)     ; save current SP (we are B)
    LD   (HL_save_temp), SP
    ; (simplified — real impl needs more care)
    LD   SP, (task_a_sp)     ; load A's SP
    RET                      ; "return" into A's code
```

The full pattern is more involved because you must save and restore SP correctly. Here is a working example:

```z80
; Two tasks, each with their own stack region
task_a_stack: DEFS 64        ; 64 bytes for task A
task_b_stack: DEFS 64        ; 64 bytes for task B
task_a_sp:    DEFW 0         ; saved SP for A
task_b_sp:    DEFW 0         ; saved SP for B

; Initialize both tasks
init_tasks:
    LD   HL, task_a_stack + 64 - 2  ; top of A's stack (minus 2 for the return address we'll push)
    LD   (HL), LOW task_a_entry
    DEC  HL
    LD   (HL), HIGH task_a_entry
    LD   (task_a_sp), HL
    
    LD   HL, task_b_stack + 64 - 2
    LD   (HL), LOW task_b_entry
    DEC  HL
    LD   (HL), HIGH task_b_entry
    LD   (task_b_sp), HL
    RET

; Switch from A to B
yield_from_a:
    LD   (task_a_sp), SP     ; save A's SP
    LD   SP, (task_b_sp)     ; load B's SP
    RET                      ; resume B

; Switch from B to A
yield_from_b:
    LD   (task_b_sp), SP     ; save B's SP
    LD   SP, (task_a_sp)     ; load A's SP
    RET                      ; resume A

task_a_entry:
    ; Task A's main loop
.a_loop:
    CALL do_a_work
    CALL yield_from_a        ; give B a turn
    JR   .a_loop

task_b_entry:
    ; Task B's main loop
.b_loop:
    CALL do_b_work
    CALL yield_from_b        ; give A a turn
    JR   .b_loop
```

### When to Use Coroutines

| Situation | Recommendation |
|---|---|
| Background music + foreground game | Yes — music in one coroutine, game in another |
| Loading screen with animation | Yes — load in one coroutine, animate in another |
| Multi-pass rendering (e.g., 3-frame multicolor) | Maybe — often simpler to inline |
| Simple sequential code | No — adds complexity for no benefit |

The cost of coroutines is moderate: 64 bytes of stack per task, plus ~50 bytes of switching code. For two tasks (background music + main game), the cost is worth it. For more than four tasks, you have outgrown the pattern and should consider a real scheduler.

---

## Self-Modifying Code Patterns

Self-modifying code (SMC) is code that writes to itself at runtime. The Z80 makes this easy: code and data share the same address space, and writes to RAM are immediate. (Writes to ROM are silently ignored — important constraint.)

### Pattern 1 — Variable Immediate

The classic SMC pattern: patch an immediate operand at runtime to inject a value into the next instruction.

```z80
fast_clear_row:
    ; Clear one row (32 bytes) starting at HL
    LD   A, 32               ; count
    LD   (patch+1), A        ; patch the LD B,imm below
patch:
    LD   B, 0                ; B is now 32
.clear_loop:
    LD   (HL), 0
    INC  HL
    DJNZ .clear_loop
    RET
```

Without SMC, this would be `LD B, A` (one extra byte, one extra T-state per call). The SMC version is faster on subsequent calls because the patching can be done once outside the inner loop.

### Pattern 2 — Patching an Address

```z80
; Generic blit: copy bytes from (src) to (dst), count in BC
generic_blit:
    LD   A, (src_low)        ; read low byte of src
    LD   (patch_src+1), A    ; patch LD HL, imm
    LD   A, (src_high)
    LD   (patch_src+2), A
patch_src:
    LD   HL, #0000           ; patched to actual src
    ; ... similar patching for dst and count ...
```

### When SMC Wins

SMC shines when:

- The patched value changes rarely (e.g., once per frame)
- The patched instruction is in a tight inner loop
- Code size matters more than readability

### When SMC Loses

SMC is problematic when:

- The code lives in ROM (cannot be patched — silently ignored)
- The code is bank-switched (patches disappear when the bank changes)
- Multiple threads execute the same code (race conditions on the patch)
- Code readability matters (SMC is opaque; reviewers miss it)

For modern development, prefer non-SMC unless you are writing tight demoscene code. The cycle-count benefits are typically 1-2 T-states per loop iteration, which adds up to 5-10% in extreme cases but is invisible in most code.

---

## Macro Systems

SjASMPlus and most modern assemblers support macros: parameterized code templates expanded inline at assembly time. Macros are the assembly answer to C++ templates and Rust macros.

### Basic Macro

```z80
    MACRO PRINTLN string_addr
    PUSH AF
    PUSH HL
    LD   HL, string_addr
.ps_loop:
    LD   A, (HL)
    AND  A
    JR   Z, .ps_done
    RST  #10
    INC  HL
    JR   .ps_loop
.ps_done:
    LD   A, #0D              ; newline
    RST  #10
    POP  HL
    POP  AF
    ENDM
```

Usage:

```z80
    PRINTLN hello_msg
    PRINTLN goodbye_msg
```

Each use expands to the full inline code. Local labels (starting with `.`) are unique per expansion.

### Macros vs Subroutines

| Criterion | Macro | Subroutine |
|---|---|---|
| Code size | One copy per use | One copy total |
| Speed | Inline (no CALL/RET overhead) | CALL/RET per use |
| Readability | High (named operation) | High |
| Parameterization | Assembly-time constants | Runtime values |
| Use case | Short, hot code | Long, cold code |

For a routine called 20 times that is 10 instructions long, the macro version costs 200 bytes; the subroutine version costs 10 bytes plus 60 bytes of CALL sites = 70 bytes. The subroutine wins. For a routine called 20 times that is 2 instructions, the macro costs 40 bytes; the subroutine costs 2 bytes plus 60 bytes of CALL = 62 bytes. The macro wins.

### Advanced Macro Patterns

SjASMPlus macros support repetition (`REPT`), conditional assembly (`IF`/`ENDIF`), and Lua scripting. These allow generating repetitive code (unrolled loops, lookup tables) at assembly time. See [sjasmplus.md § Macros](../../09_toolchain/sjasmplus.md#macros-and-conditional-assembly) for the full syntax.

---

## Modular File Organization

A 5000-line program in a single `.asm` file is unmaintainable. The standard solution is to split into multiple files and use the assembler's `INCLUDE` directive to combine them.

### Project Structure

A typical project layout:

```
my_project/
├── main.asm              ; main loop, state machine
├── player/
│   ├── player.asm        ; player update/draw
│   └── player_data.asm   ; player tables
├── enemies/
│   ├── enemies.asm
│   └── enemy_types.asm
├── graphics/
│   ├── sprites.asm       ; sprite definitions
│   └── screen.asm        ; screen routines
├── audio/
│   └── music.asm
├── lib/
│   ├── macros.asm        ; shared macros
│   ├── math.asm          ; multiply, divide
│   └── string.asm        ; print routines
├── data/
│   ├── levels.asm
│   └── dialogs.asm
└── build.sh
```

### Public/Private Symbols

By default, every label in every file is local to that file. To make a label visible from other files, use `PUBLIC` (or `GLOBAL`, depending on the assembler). To reference a label from another file, use `EXTERN` (or `EXTERN`).

```z80
; player.asm
    PUBLIC update_player, draw_player
    EXTERN sprite_data, screen_addr

update_player:
    ; ...
    RET

draw_player:
    ; ...
    RET
```

```z80
; main.asm
    EXTERN update_player, draw_player

main:
    CALL update_player
    CALL draw_player
```

SjASMPlus handles this differently: by default, labels ending in `:` are local; labels ending in `::` are global. See [sjasmplus.md](../../09_toolchain/sjasmplus.md).

### Linker Directives

For projects with multiple source files, the linker (which is often the same tool as the assembler) needs to know:

- Which sections go where in memory (code, data, BSS)
- The entry point address
- Whether to emit a snapshot, tape, or disk image

SjASMPlus uses `DEVICE` + `ORG` + `SAVESNA`/`SAVETAP` to handle this. For complex projects, multiple `ORG` directives can place code at specific addresses:

```z80
    DEVICE ZXSPECTRUM48
    ORG  #8000              ; main code
    INCLUDE "main.asm"
    INCLUDE "player/player.asm"
    INCLUDE "enemies/enemies.asm"
    
    ORG  #C000              ; data in upper RAM
    INCLUDE "data/levels.asm"
    
    SAVESNA "mygame.sna", main
```

---

## Memory Banking Patterns

On the 128K and later machines, the top 16 KB of address space (`#C000`-`#FFFF`) can be switched between multiple RAM banks. This expands total addressable memory at the cost of complexity.

### Pattern — Common Code in Low RAM

The trick to bank-switched code: **always keep your common code in the fixed low-RAM region** (`#8000`-`#BFFF`). The banked region can hold data and per-bank code, but the dispatcher and the banking routines themselves must be in low RAM.

```z80
; Low RAM (always paged in)
    ORG  #8000
switch_bank:
    ; Entry: A = bank number (0-6)
    LD   BC, #7FFD
    AND  7
    OUT  (C), A             ; page in bank
    RET

; Per-bank code (bank 5, for example)
    ORG  #C000
bank5_init:
    ; ... runs only when bank 5 is paged ...
    RET
```

### Pattern — Bank-Switched Data

For large data (music, graphics, level data), keep a single accessor routine in low RAM and the data in banks:

```z80
; Read a byte from banked address
; Entry: HL = address (within banked region), B = bank
; Exit: A = byte
read_banked:
    PUSH HL
    PUSH BC
    LD   A, B
    CALL switch_bank
    POP  BC
    POP  HL
    LD   A, (HL)            ; read from banked memory
    PUSH HL
    PUSH BC
    LD   A, (current_bank)  ; restore
    CALL switch_bank
    POP  BC
    POP  HL
    RET
```

This is verbose but works. For bulk transfer (e.g., loading a screen from banked memory), the inner loop is faster because you switch once and read many bytes.

Full treatment of 128K+ banking patterns is in [bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md).

---

## Error Handling Patterns

Assembly has no exception system. Errors are communicated by return values, flags, and global status codes. Pick a convention and stick with it across the project.

### Convention 1 — Carry Flag for Success/Failure

The most common convention: **carry clear = success, carry set = failure**. The C flag is set or cleared by many arithmetic instructions, making it cheap to use.

```z80
load_file:
    ; Entry: HL = filename
    ; Exit: carry set = error (A = code), carry clear = success
    ; ...
    ; (success path)
    OR   A                  ; clear carry
    RET
.error:
    SCF                     ; set carry
    RET

; Caller
    LD   HL, filename
    CALL load_file
    JR   C, handle_error
    ; ... use loaded file ...
```

### Convention 2 — Zero Flag for Not-Found

For search and lookup routines: **Z flag set = found, Z flag clear = not found**.

```z80
find_item:
    ; Entry: HL = item list, A = key
    ; Exit: Z = found (HL = address), NZ = not found
.search_loop:
    CP   (HL)
    JR   Z, .found
    INC  HL
    LD   A, (HL)
    AND  A
    JR   NZ, .search_loop
    ; Not found — ensure Z is clear
    OR   #FF                ; any nonzero value
    RET
.found:
    ; Z already set by CP
    RET
```

### Convention 3 — Error Code in A

For routines that can fail in many ways: **A = error code on failure, A = 0 (or value) on success**.

```z80
open_file:
    ; Exit: A = 0 (success) or error code (1=file not found, 2=disk error, etc.)
    ; ...
    RET

; Caller
    CALL open_file
    AND  A
    JR   NZ, handle_error
    ; ... A == 0, success ...
```

### Convention 4 — Error Handler Hook (ERR_SP)

The ROM uses `RST #08` with `ERR_SP` for fatal errors. User code can hook into this for try/catch semantics. See [stack_and_rst.md § ERR_SP Trick](stack_and_rst.md#the-err_sp-trick--trycatch-around-rom-calls) for the full pattern.

### Pick One and Document It

Every project should pick one convention (typically carry flag) and document it. Mixed conventions within one project are a common source of bugs.

---

## Pitfalls and Common Mistakes

### Pitfall 1: Out-of-Bounds Dispatch

```z80
; BAD: no bounds check on state index
    LD   A, (state)
    ADD  A, A
    LD   L, A
    LD   H, 0
    LD   DE, state_table
    ADD  HL, DE
    ; (reads handler address — if A >= state count, reads garbage)
    LD   A, (HL)
    INC  HL
    LD   H, (HL)
    LD   L, A
    JP   (HL)               ; might jump anywhere!
```

Always bounds-check before indexing:

```z80
    LD   A, (state)
    CP   STATE_COUNT
    JR   NC, .invalid_state
    ; ... proceed with dispatch ...
.invalid_state:
    LD   A, 0                ; reset to default state
    LD   (state), A
    JR   main_loop
```

### Pitfall 2: Self-Modifying Code in ROM

```z80
; BAD: tries to patch code that lives in ROM (0x0000-0x3FFF)
    LD   A, #FF
    LD   (#0D6D + 1), A     ; try to patch ROM CLS — silently ignored!
```

Writes to ROM are silently ignored on the ZX Spectrum. The patch appears to work in the listing (no error from the assembler), but at runtime the code is unchanged. Always verify your SMC code is in RAM (`#8000`+).

### Pitfall 3: Coroutine Stack Overflow

If two coroutines each have a 64-byte stack, and one calls a routine that uses 80 bytes of stack, the stack pointer walks out of the 64-byte region and into the other coroutine's state. The symptom is intermittent corruption that depends on call timing.

Solution: size each stack generously (256 bytes minimum), and use the emulator's debugger to verify SP never leaves its region.

### Pitfall 4: Macro Local Label Conflicts

```z80
    MACRO LOOP_INIT counter
    LD   B, counter
init:
    RET
    ENDM
```

If the macro is expanded twice, the label `init` appears twice, which is an error. SjASMPlus and most modern assemblers support **local labels** (starting with `.`) that are unique per expansion:

```z80
    MACRO LOOP_INIT counter
    LD   B, counter
.init:
    RET
    ENDM
```

Always use local labels in macros.

### Pitfall 5: Symbol Visibility Mismanagement

```z80
; file_a.asm
    PUBLIC some_function
some_function:
    ; ...

; file_b.asm
some_function:               ; local label, same name — collision!
    ; ...
```

Two files defining the same label name, one as PUBLIC, causes a link error. The fix is to use unique prefixes (e.g., `player_update` and `enemy_update`) or use SjASMPlus's module system (`MODULE player; update:` defines `player.update`).

### Pitfall 6: Data Tables Embedded in Code Path

```z80
subroutine:
    CALL helper
    DEFW 0x1234              ; data
    DEFB "hello", 0
    RET
```

If `subroutine` is called and `helper` returns normally, execution falls through into the data — `0x1234` is decoded as `LD (nn), HL` and reads further bytes. Always put data tables **after** the final `RET` of a subroutine, or branch around them with `JR`.

---

## Cross-References

- **[assembly_intro.md](assembly_intro.md)** — first contact; uses simple state machine pattern in the Hello World example
- **[rom_calls.md](rom_calls.md)** — uses error handler pattern (RST #08 + ERR_SP)
- **[stack_and_rst.md](stack_and_rst.md)** — `JP (HL)` and computed call patterns
- **[assembly_optimization.md](assembly_optimization.md)** — when SMC and unrolled loops are worth the cost
- **[c_interop.md](c_interop.md)** — C compilers use these patterns internally (vtables, stack frames)
- **[z80_coding_practices.md](../../01_cpu/z80_coding_practices.md)** — micro-level patterns (instruction selection, register allocation)
- **[bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md)** — 128K+ memory banking patterns in depth
- **[interrupt_programming.md](../04_interrupts/interrupt_programming.md)** — ISR patterns build on these structural patterns
- **[sjasmplus.md](../../09_toolchain/sjasmplus.md)** — assembler-specific macro and modular features

## References

- *Game Programming Patterns* by Robert Nystrom — the patterns in this article are language-agnostic; this book covers them in a higher-level context
- *Programming the Z80* by [Rodnay Zaks](https://en.wikipedia.org/wiki/Rodnay_Zaks) — practical examples of state machines and tables in Z80 assembly
- *The [Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip)* — the ROM itself uses dispatch tables extensively; studying it is a masterclass in assembly patterns
- [chibiakumas.com Z80 tutorials](https://www.chibiakumas.com/z80/) — modern assembly tutorials covering patterns
- [breakintoprogram.co.uk](http://www.breakintoprogram.co.uk/hardware/computers/zx-spectrum/assembly-language) — assembly routine library
