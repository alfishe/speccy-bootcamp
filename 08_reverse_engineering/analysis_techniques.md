[← Plan](../PLAN.md) · [Reverse Engineering](README.md)

# Analysis Techniques — Static and Dynamic RE Workflows

Reverse engineering a ZX Spectrum program is a two-phase process: **static analysis** (reading the code without running it) and **dynamic analysis** (running the code under a debugger and observing its behavior). The two phases alternate — you disassemble statically, form hypotheses, then test them dynamically. You set breakpoints dynamically, discover code paths, then go back to the disassembly to annotate them. This cycle continues until you understand the program.

This article is the practical deep-dive companion to [methodology.md](methodology.md). The methodology article covers the workflow at a high level — this article provides complete worked examples, toolchain setup guides, and the specific keystroke-level procedures for each analysis technique. It does **not** duplicate the methodology article; it expands sections 3-4 into full tutorials.

> [!NOTE]
> This article assumes you have read [methodology.md](methodology.md) sections 1-2 (starting points and the standard workflow) and have a working understanding of Z80 assembly (see the [Assembly series](../05_development/02_assembly/README.md)).

---

## Toolchain Setup

Before you can analyze a Spectrum program, you need the right tools. Here is the complete setup for a modern RE workflow.

### Tool Summary

| Tool | Purpose | Platform | Cost |
|---|---|---|---|
| ZEsarUX | Emulator with best-in-class debugger | Cross-platform | Free |
| Fuse | Lightweight emulator, quick testing | Cross-platform | Free |
| DeZog | VS Code debugger extension for ZEsarUX/CSpect | VS Code | Free |
| SkoolKit | Annotated disassembly toolkit | Python, cross-platform | Free |
| z80dasm | Command-line disassembler | Cross-platform | Free |
| Spectrum Analyser | GUI disassembler + emulator hybrid | Windows | Free |
| xxd / hexyl | Hex viewers | Cross-platform | Free |
| vbindiff | Binary diff tool | Cross-platform | Free |

### ZEsarUX Setup

ZEsarUX has the most complete Spectrum debugger of any emulator. It supports every Spectrum model (16K through Next), every clone (Pentagon, Scorpion, etc.), and every peripheral (DivIDE, Multiface, Beta 128). Its debug monitor provides disassembly, breakpoints, watchpoints, trace logging, reverse execution, and memory editing.

```bash
# Linux/macOS build from source
git clone https://github.com/chernandezba/zesarux.git
cd zesarux
./configure
make
./zesarux

# Key startup flags for RE work:
./zesarux --enablemapperstatus --enabletimings --machine 48k
```

Key ZEsarUX debugger commands (press F5 to open the debugger):

| Command | Action |
|---|---|
| `bp <addr>` | Set breakpoint at address |
| `bp <addr> if <cond>` | Conditional breakpoint (e.g., `bp #8000 if A=#42`) |
| `wp <addr>` | Set write watchpoint |
| `rp <addr>` | Set read watchpoint |
| `s` | Single-step (into calls) |
| `n` | Step over (skip calls) |
| `finish` | Run until current function returns |
| `ri` | Reverse-step (undo last instruction) |
| `trace on` | Begin trace logging |
| `trace off` | Stop trace logging |
| `mem <addr>` | Inspect memory |
| `regs` | Show all registers |
| `set <reg>=<val>` | Modify a register |

### DeZog — VS Code Integration

DeZog brings the modern IDE debugging experience to Spectrum RE. It connects VS Code to ZEsarUX (or CSpect or MAME) via a debug protocol, giving you source-level debugging, watch expressions, conditional breakpoints, and memory views — all inside VS Code.

```json
// .vscode/launch.json — DeZog configuration for ZEsarUX
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "ZEsarUX Debug",
            "type": "dezog",
            "request": "launch",
            "zrcp": {
                "hostname": "localhost",
                "port": 10000
            },
            "sjasmplus": {
                "listFile": "build/game.lst"
            },
            "load": "build/game.sna",
            "program": "build/game.sna"
        }
    ]
}
```

Start ZEsarUX with remote debugging enabled:

```bash
zesarux --remotedbg 10000 --machine 48k
```

Then press F5 in VS Code. DeZog connects, loads the snapshot, and you get:

- **Disassembly view** with inline annotations from `.lst`/`.sym` files
- **Watch expressions** (e.g., `HL`, `(HL)`, `(#5C3C)`)
- **Conditional breakpoints** (e.g., break at `#8000` only when `B == 0`)
- **Memory view** with hex/ASCII
- **Call stack** when stepping through nested calls
- **Reverse debugging** — step backward through execution history

For full DeZog setup details, see [debugging.md](../09_toolchain/debugging.md).

### SkoolKit Setup

SkoolKit is the gold standard for publishing annotated Spectrum disassemblies. It produces HTML disassemblies with cross-references, comments, and data type annotations — the format used by every major Spectrum RE project (e.g., the complete ROM disassembly at skoolkit.ca).

```bash
# Install SkoolKit (Python 3 required)
pip install skoolkit

# Convert a snapshot to a .skool file (annotated disassembly source)
sna2skool game.sna > game.skool

# After annotating the .skool file, render to HTML
skool2html.py game.skool

# Or render back to assembly source
skool2asm.py game.skool > game.asm
```

SkoolKit's `.skool` format uses special directives to mark code vs. data:

```
; @label PrintString
; @comment Prints a null-terminated string at HL
c8000 PUSH AF
       PUSH BC
       LD   A,(HL)
       AND  A
       JR   Z,$800B
       RST  #10
       INC  HL
       JR   $8000
$800B POP  BC
       POP  AF
       RET

; @label SpriteData
; @type b
b8010 DEFB #00,#3C,#7E,#FF,#FF,#7E,#3C,#00
```

The `c` prefix marks a code block, `b` marks a byte data block, `w` marks a word data block, `t` marks a text block, and `s` marks a subroutine entry point.

### z80dasm Setup

For quick-and-dirty disassembly without SkoolKit's annotation overhead:

```bash
# Install z80dasm
# macOS: brew install z80dasm
# Linux: apt install z80dasm

# Disassemble a binary at origin #8000
z80dasm --origin=0x8000 --sym=labels.sym game.bin > game.asm

# Disassemble a snapshot (skip the 27-byte SNA header)
dd if=game.sna bs=1 skip=27 of=game.bin
z80dasm --origin=0x8000 game.bin > game.asm
```

---

## Static Analysis — Reading the Code

Static analysis is what you do before running the program. The goal is to produce an annotated disassembly that identifies code regions, data regions, subroutine boundaries, and ROM call sites.

### The Initial Disassembly Pass

Start with a raw disassembly of the entire code region. For a 48K snapshot loaded at `#8000`, the code typically occupies `#8000`-`#FFFF` (32 KB). For a snapshot of a game that uses the full RAM, code may be anywhere from `#5C00` (above system variables) to `#FFFF`.

```bash
# Generate raw disassembly with z80dasm
z80dasm --origin=0x8000 --sym=symbols.sym game.bin > game_raw.asm

# Or with SkoolKit for a richer starting point
sna2skool game.sna > game.skool
```

The raw disassembly is mostly garbage — data regions disassembled as instructions, jump tables mistaken for code, and no labels or comments. The goal of static analysis is to transform this into something readable.

### Code vs. Data Separation

The fundamental problem of Z80 disassembly: the CPU cannot distinguish code from data, and neither can a disassembler. A byte like `#C9` could be a `RET` instruction or part of a sprite. You must manually identify and mark data regions.

**Heuristic 1: Trace from known entry points.**

The CPU's PC (program counter) in a snapshot is always a code address. ROM routine addresses (`#0E9B`, `#03B5`, `#1605`, etc.) are code. Interrupt service routines (at `#0038` for IM1 or anywhere in the IM2 vector table) are code. Start from these points and trace linearly, marking each instruction as code.

**Heuristic 2: Identify function prologues and epilogues.**

```z80
; Typical function prologue (save registers):
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        ; or
        PUSH IX
        PUSH IY

; Typical function epilogue (restore and return):
        POP  HL
        POP  DE
        POP  BC
        POP  AF
        RET
```

A `PUSH` sequence followed by a `POP` sequence and `RET` marks a clean subroutine boundary.

**Heuristic 3: Detect data by byte patterns.**

| Pattern | Likely content |
|---|---|
| Long runs of `#00` | Zero-filled RAM, blank screen areas |
| Long runs of `#FF` | Unused ROM space, or inverted data |
| Alternating `#55 #AA` | Bitmap data (checkerboard pattern) |
| Repeating 8-byte blocks | Sprite data (each byte = one pixel row) |
| ASCII range `#20`-`#7E` in long runs | Text strings |
| `#18` or `#20` followed by small signed offset | Relative jump table (code, not data) |
| `#C3` (JP) followed by an address in code range | Jump table (code, not data) |
| `#CD` (CALL) followed by an address in code range | Call table (code, not data) |

**Heuristic 4: Use SkoolKit directives to mark data.**

Once you identify a data region, mark it in the `.skool` file:

```
; Sprite data: 16 sprites × 8 bytes each
; @type b
bA000 DEFB #3C,#7E,#FF,#FF,#FF,#FF,#7E,#3C
       DEFB #00,#FF,#00,#FF,#00,#FF,#00,#FF
       ...
```

SkoolKit will skip this region during disassembly and display it as hex data.

### ROM Call Recognition

Commercial Spectrum software calls ROM routines extensively for I/O, printing, tape operations, and floating-point math. Labeling these calls is the single fastest way to make a disassembly readable.

The 48K ROM has well-known entry points (see [rom_routines.md](../10_references/rom_routines.md) for the complete list). The most common:

| Address | Name | Function |
|---|---|---|
| `#1605` | PRINT-A | Print character in A via current channel |
| `#15EF` | PRINT-OUT | Output to S-channel (main screen) |
| `#10A8` | CL-CH-ADD | Skip spaces in channel buffer |
| `#0E9B` | CL-ALL | Close all streams |
| `#03B5` | BEEPER | Produce a tone (HL = pitch, DE = duration) |
| `#1F05` | COPY | Copy screen to ZX Printer |
| `#20CC` | SAVE | Save data to tape |
| `#21CC` | LOAD | Load data from tape |
| `#0D6D` | KEY-SCAN | Scan keyboard |
| `#028E` | KEY-INPUT | Wait for keypress |
| `#22B5` | BP-GET-MEM | Allocate BASIC workspace |

```z80
; Before labeling (raw disassembly):
L8A23  CD0516    CALL #1605
L8A26  3A3C5C    LD   A,(#5C3C)
L8A29  FE41      CP   #41
L8A2B  2806      JR   Z,#8A33

; After labeling ROM calls:
PrintChar   CALL #1605          ; PRINT-A — print character in A
            LD   A,(ATTR_P)     ; ATTR_P = #5C3C — permanent attribute
            CP   'A'            ; compare to 'A'?
            JR   Z,IsAlpha
```

This single technique — recognizing and labeling ROM calls and system variables — can cut the apparent complexity of a disassembly by 50% on the first pass.

### String and Asset Detection

Spectrum software stores assets in recognizable patterns:

**Text strings**: Long runs of bytes in the `#20`-`#7E` range. In a hex editor, these jump out as readable ASCII. Note: BASIC programs store tokens (like `PRINT`) as single bytes in the `#A5`-`#FF` range, not as ASCII text — see [character_set.md](../10_references/character_set.md) for the token table.

**Sprite data**: 8-byte aligned blocks where each byte represents one row of 8 pixels. A sprite table is typically `n * 8` bytes. For masked sprites, the format is 16 bytes per row (8 bytes mask + 8 bytes pixel data). Look for the characteristic "U-shape" patterns in hex — sprites often start with a narrow top row (`#18`, `#3C`) and widen downward.

**Music data**: Different trackers have different magic bytes:
- PT3 modules: start with `"PT3..."` (ASCII at offset 0)
- STC modules: start with specific header bytes
- PSG register dumps: start with `"PSG"` + `#1A`
- AY song format: start with `"AYSONG"` or `"AY EMUL"`

**Screen data**: If you see 6,144 bytes of data that would make sense when loaded at `#4000`, it is a screen image. The `.SCR` format is exactly this — see [file_format_handling.md](../05_development/08_dos_tape/file_format_handling.md).

**Map data**: Game maps are often stored as tile indices (1 byte per tile cell) or as room descriptors (pointer tables to room data). Look for repeating structures: a map that is 32×24 tiles would be 768 bytes, matching the attribute grid size.

### Cross-Reference Analysis

Once you have a partially annotated disassembly, build a cross-reference map: which routines call which. This reveals the program's call graph and helps identify utility routines.

**Heuristic**: A `CALL` or `JP` target that appears many times across the program is a utility routine (print, draw, sprite blit, music player). A target called only once is often a state transition or initialization routine. A target never called is either data mistaken for code or a routine entered via indirect jump (`JP (HL)`).

SkoolKit generates cross-references automatically. With z80dasm, grep the symbol file:

```bash
# Find all CALL targets, sorted by frequency
grep -oE 'CALL #[0-9A-F]{4}' game.asm | sort | uniq -c | sort -rn | head -20

# Find all JP targets
grep -oE 'JP #[0-9A-F]{4}' game.asm | sort | uniq -c | sort -rn | head -20
```

The most frequently called address is often the main screen update or sprite drawing routine.

---

## Dynamic Analysis — Running the Code

Static analysis tells you what the code *says*. Dynamic analysis tells you what the code *does*. The two phases alternate throughout an RE project: you form a hypothesis from the static disassembly, then verify or refute it by running the code under a debugger.

### The Debugging Cycle

```
1. Spot something interesting in the disassembly (a routine, a branch, a data access)
2. Set a breakpoint at that address in the emulator
3. Run the program until the breakpoint triggers
4. Examine registers and memory at the breakpoint
5. Single-step through the routine, watching how state changes
6. Update the disassembly with what you learned
7. Resume execution; repeat
```

This cycle is the heart of ZX Spectrum RE. Each iteration through the cycle adds understanding.

### ZEsarUX Debugger Walkthrough

ZEsarUX has the most powerful Spectrum debugger available. Press **F5** during emulation to open the debug monitor. The main views:

**Disassembly view**: Shows the current PC location with surrounding instructions. Registers are displayed at the top (AF, BC, DE, HL, IX, IY, SP, PC, I, R, IFF1, IFF2, IM). You can navigate with arrow keys, and pressing Enter on an instruction toggles a breakpoint.

**Memory view**: Press `M` to open. Shows a hex dump of any address range. You can switch between hex, ASCII, and decimal display modes. Press `E` to edit bytes directly.

**Stack view**: Shows the current stack contents, updated as SP changes.

**Register editor**: Click any register value and type a new one. This is invaluable for testing hypotheses — e.g., force a comparison result and see if the code path changes.

### Setting Breakpoints

Breakpoints are the primary dynamic analysis tool. ZEsarUX supports several types:

| Type | Command | Purpose |
|---|---|---|
| PC breakpoint | `bp #8000` | Break when PC reaches address |
| Conditional | `bp #8000 if A=#42` | Break only when condition is true |
| Write watchpoint | `wp #5C3C` | Break when a memory address is written |
| Read watchpoint | `rp #5800` | Break when a memory address is read |
| Port breakpoint | `pio #FE` | Break on I/O port access |

Conditional breakpoints are extremely powerful. Common patterns:

```
; Break when the game writes to the lives counter
bp #8A23 if A=#00      ; break at this address only when A=0

; Break when a specific memory location changes
wp #8B00               ; break on any write to lives counter

; Break when the screen is modified
wp #4000               ; break on pixel RAM write
wp #5800               ; break on attribute RAM write
```

### Worked Example: Finding the Lives Counter

A common RE task: find where the game stores the player's lives, so you can create an infinite-lives cheat. Here is the step-by-step procedure:

**Step 1**: Load the game. Play until the player dies. Note the moment the lives counter decrements.

**Step 2**: Set a write watchpoint on the system variable area (`#5C00`-`#5CB5`). Many games store game state in unused system variables.

```
wp #5C00
```

**Step 3**: Let the player die again. The watchpoint triggers, showing the instruction that modified the lives counter.

**Step 4**: If no hit in the system variable area, try a broader search. Use ZEsarUX's memory snapshot feature:

1. At the start of a life: `snapshot save life1.sna`
2. Lose a life.
3. At the start of the next life: `snapshot save life2.sna`
4. Binary-diff the two snapshots to find what changed:

```bash
# Compare the two snapshots to find changed bytes
vbindiff life1.sna life2.sna

# Or extract RAM and compare:
dd if=life1.sna bs=1 skip=27 of=ram1.bin
dd if=life2.sna bs=1 skip=27 of=ram2.bin
cmp -l ram1.bin ram2.bin
```

The changed bytes are candidates for the lives counter. Usually only a few bytes differ between consecutive lives.

**Step 5**: Once you have a candidate address, set a write watchpoint on it:

```
wp #8B42              ; candidate lives counter address
```

**Step 6**: Lose a life. The watchpoint triggers at the instruction that decrements the counter. This is typically a `DEC (HL)` or `LD (HL),A` instruction.

```z80
; Typical lives decrement:
DecLives:   LD   HL,(LivesPtr)    ; HL -> lives counter
            DEC  (HL)             ; decrement
            RET
```

**Step 7**: To create an infinite-lives patch, NOP out the `DEC (HL)` instruction:

```z80
; Original: DEC (HL)  = #35
; Patched:  NOP       = #00
; Write #00 at the address of the DEC instruction
```

Or, even simpler, change the DEC to an INC — the lives counter goes up instead of down.

### DeZog — Source-Level Debugging

When you have an annotated disassembly or a re-assembled source file, DeZog provides a dramatically better debugging experience. Instead of navigating raw addresses, you debug using labels and source lines.

**Setup**:

1. Re-assemble the target with sjasmplus, generating a `.lst` file:
```bash
sjasmplus --lst=game.lst game.asm
```

2. Configure DeZog in VS Code's `launch.json` (see [toolchain setup above](#dezog--vs-code-integration)).

3. Start ZEsarUX with remote debugging:
```bash
zesarux --remotedbg 10000
```

4. Press F5 in VS Code. DeZog connects, loads the program, and shows your source with the current PC highlighted.

**Benefits over raw emulator debugging**:

- You see source code, not raw disassembly
- Labels appear as variable names in watch expressions
- Step through source lines, not individual instructions
- Hover over a label to see its value
- Set breakpoints by clicking in the source margin
- The call stack shows function names, not addresses

### Trace Logging

For non-deterministic bugs, timing-sensitive protection schemes, or code that detects debugger presence, **trace logging** is the technique of last resort. ZEsarUX can log every executed instruction in order, with full register state.

```
; In ZEsarUX debugger:
trace on /tmp/trace.log
; ... let the program run for a few seconds ...
trace off
```

The trace log contains lines like:

```
#8000  CD 05 16    CALL #1605     AF=0041 BC=0000 DE=5C3C HL=8000 IX=5C3A IY=5C3A SP=FF40
#8003  3A 3C 5C    LD A,(#5C3C)   AF=0041 BC=0000 DE=5C3C HL=8000 IX=5C3A IY=5C3A SP=FF3E
```

The log is enormous — a single second of game time can produce millions of lines. Analysis techniques:

```bash
# Find every write to port #FE (border/beeper)
grep 'OUT (#FE)' /tmp/trace.log

# Find every CALL to a specific address
grep 'CALL #1605' /tmp/trace.log

# Find all memory writes to system variables (#5C00-#5CB5)
grep -E 'WRITE .*#5C[0-9A-F][0-9A-F]' /tmp/trace.log

# Count how many times each routine is called
grep -oE 'CALL #[0-9A-F]{4}' /tmp/trace.log | sort | uniq -c | sort -rn | head -20
```

Trace logging works even on self-modifying code, encrypted code (after decryption), and code that actively resists disassembly. It is the ultimate fallback when all other techniques fail.

### Reverse Debugging

ZEsarUX supports **reverse execution** — the ability to step backward through previously executed code. This is invaluable for answering the question "how did the program get into this state?"

The typical workflow:

1. Set a breakpoint at a crash or interesting behavior.
2. When it triggers, examine the state.
3. Step **backward** to find the instruction that set the bad value.
4. Set a breakpoint at that instruction, run forward, and watch the bug develop.

In ZEsarUX, press `ri` (reverse instruction) in the debugger to undo the last executed instruction. You can also use `rb` (reverse breakpoint) to run backward until a specific address is reached.

> [!WARNING]
> Reverse debugging requires significant memory — the entire execution history is kept in RAM. For long sessions, this can consume gigabytes. Use sparingly: capture the interesting moment with a breakpoint, then use reverse-stepping only in the immediate vicinity.

---

## Memory Diffing

One of the most powerful analysis techniques is **memory diffing**: comparing two snapshots taken at different points to find what changed. This reveals game state, asset loading, and code decryption.

### Snapshot Diff Workflow

```bash
# Step 1: Take snapshot before an event (e.g., before collecting an item)
# In ZEsarUX: File > Save snapshot > before_item.sna

# Step 2: Trigger the event (collect the item)

# Step 3: Take snapshot after the event
# In ZEsarUX: File > Save snapshot > after_item.sna

# Step 4: Extract RAM from both snapshots (skip 27-byte SNA header)
dd if=before_item.sna bs=1 skip=27 of=ram_before.bin
dd if=after_item.sna bs=1 skip=27 of=ram_after.bin

# Step 5: Compare
cmp -l ram_before.bin ram_after.bin
# Output: byte_offset old_byte new_byte
# Each differing byte is a candidate for the game state change
```

For 128K snapshots, you need to diff each bank separately. Take snapshots with the same bank paged in at `#C000` to make the comparison meaningful.

### Practical Diff Scenarios

| Scenario | What changes |
|---|---|
| Player moves | Sprite attribute bytes, player position variables |
| Player dies | Lives counter, game state flag, screen update |
| Collect item | Inventory flag, score variable |
| Enter new room | Screen RAM (6144+768 bytes), room data pointers |
| Music changes | AY register writes, music data pointer |
| Code unpacks | Large regions of RAM change (decompression) |

The last scenario — code unpacking — is particularly important. If you take a snapshot before and after a packer/decryptor runs, the diff shows exactly which memory regions were written. This reveals the unpacked code location and size.

---

## Common Pitfalls

### 1. Disassembling Data as Code

The most common static analysis error. A raw disassembly will happily convert a sprite table into nonsensical instructions. Always verify that a region contains real code by checking for coherent control flow (sequential instructions with valid opcodes, sensible call targets, proper function boundaries).

### 2. Missing Indirect Jumps

Functions called via `JP (HL)`, `JP (IX)`, or computed jump tables are invisible to static cross-reference analysis. The disassembly shows the indirect jump instruction, but not its targets. Use dynamic analysis (breakpoints) to discover the actual jump targets at runtime.

### 3. Self-Modifying Code

If the program modifies its own code (e.g., changing the operand of an `LD A,(nnnn)` instruction), the static disassembly shows the *original* operand, not the one used at runtime. This is especially common in tight inner loops where an address is patched for each iteration. Trace logging reveals the actual values used.

### 4. Bank-Switched Code

On 128K machines, code in banked memory (`#C000`-`#FFFF`) changes when the bank register (`#7FFD`) is written. A disassembly of a 128K snapshot only shows the currently-paged bank. To analyze code in other banks, either page each bank in and snapshot separately, or use SkoolKit's 128K support to process all banks.

### 5. Interrupt-Driven Code Paths

Code that runs in an interrupt service routine (ISR) is invisible to normal stepping — it fires asynchronously between instructions. If the program uses IM1, the ISR runs at `#0038` every frame. If it uses IM2, the ISR address is in the vector table. Always check for active ISRs when analyzing timing-sensitive behavior. See [interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md) for ISR patterns.

---

## Cross-References

| Topic | Reference |
|---|---|
| RE methodology overview | [methodology.md](methodology.md) |
| Software protection catalog | [protection_techniques.md](protection_techniques.md) |
| Protection cracking deep-dive | [protection_cracking.md](protection_cracking.md) |
| Game reversing case studies | [game_reversing.md](game_reversing.md) |
| Code compression and packers | [code_crunching.md](code_crunching.md) |
| Snapshot repair | [snapshot_repair.md](snapshot_repair.md) |
| Debugging toolchain setup | [debugging.md](../09_toolchain/debugging.md) |
| Cross-platform toolchain | [cross_platform_toolchain.md](../09_toolchain/cross_platform_toolchain.md) |
| ROM routine entry points | [rom_routines.md](../10_references/rom_routines.md) |
| System variables | [system_variables.md](../04_operating_systems/system_variables.md) |
| Assembly series | [assembly series](../05_development/02_assembly/README.md) |
| Interrupt programming | [interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md) |

## References

### External references

- [IDA Pro and Ghidra documentation](https://hex-rays.com/ida-pro/) — the two leading disassemblers used for ZX Spectrum reverse engineering; both support Z80 mode and the ZX Spectrum Next's Z80N extended ISA.
- [`z88dk-appmake`](https://github.com/z88dk/z88dk/wiki/appmake) — the z88dk tool for unpacking and repacking ZX Spectrum binary formats (`.tap`, `.tzx`, `.z80`, `.sna`); essential for splitting a release into analyzable code + data sections.
- [Complete Spectrum ROM Disassembly](https://worldofspectrum.org/ROMdisassembly.zip) — the canonical worked example of reverse-engineering a complex Spectrum binary; every routine annotated and cross-referenced.
- [zx-pk.ru reversing forum](https://zx-pk.ru) — primary Russian-language venue for Soviet-era game intros / loaders / protections; the source of most documented custom-loader analyses.
- [chibiakumas.com (Keith S. of CPU shack)](https://chibiakumas.com) — English-language archive of translated Russian reversing articles, magazine scans, and disassembly listings for famous Soviet-era intros.
