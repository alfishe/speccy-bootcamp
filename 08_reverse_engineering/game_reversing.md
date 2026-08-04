[← Plan](../PLAN.md) · [Reverse Engineering](README.md)

# Game Reversing — Asset Extraction, Cheats, and Engine Identification

Reversing a ZX Spectrum game is a different task from cracking protection. Cracking asks: "how do I get the unprotected code?" Game reversing asks: "how does this game work, and what can I extract from it?" The goals are varied: ripping sprites and music for a fan project, writing cheat codes (infinite lives, level skip), understanding a game engine to build a level editor, or reconstructing the original source code.

This article covers the practical techniques of game reversing. It assumes you can already produce a clean, unpacked snapshot (see [protection_cracking.md](protection_cracking.md)) and have basic disassembly skills (see [analysis_techniques.md](analysis_techniques.md)). This article does **not** duplicate those — it focuses on what you do **after** the code is disassembled and readable.

> [!NOTE]
> All techniques in this article are educational. They respect the Spectrum community's long tradition of reverse engineering for preservation, understanding, and fan projects. Commercial software on the Spectrum is decades old; the developers and publishers are long gone. The community treats RE as a form of digital archaeology.

---

## Engine Identification — The Game's Fingerprint

Before diving into a game's internals, identify its engine. Most Spectrum games were built on one of a handful of engine families. Recognizing the engine tells you where to look for sprites, maps, music, and game logic.

### The Major Engine Families

| Engine / Developer | Visual signature | Sprite format | Map format | Music format |
|---|---|---|---|---|
| **Ultimate Play the Game** | Isometric (Knight Lore, Alien8) or top-down (Jetpac) | 16x16 masked sprites, pre-shifted | Room-based, 8x8 tile grid | AY or beeper, custom |
| **Ocean (Filmation)** | Large isometric rooms (Batman, Head Over Heels) | Variable-size masked sprites | Room descriptors with object lists | AY music |
| **Graftgold** | Smooth scrolling (Uridium, Paradroid) | 8x8 or 16x16 hardware sprites or custom | Tile-based scrolling maps | AY |
| **Hewson** | Polished shoot-em-ups (Exolon, Cybernoid) | 16x16 or 32x32 sprites, masked | Static screens with enemy patterns | AY (David Whittaker, Ben Daglish) |
| **Crl / Mastertronic** | Budget games, simple engines | 8x8 sprites, basic | Simple linear scrolling | Beeper |
| **Russian/clone games** | Dizzy-style adventure (Dizzy series) | 16x16 masked sprites | Room-based, object interaction tables | AY (PSG tracker modules) |

### Engine Recognition Heuristics

**Visual identification**: The fastest way. Load the game, observe the graphics style:

- Isometric room with character walking around → Ultimate Filmation or Ocean Filmation engine
- Smooth horizontally scrolling shoot-em-up → Graftgold-style engine
- Static single-screen with enemies → Hewson-style or budget engine
- Room-based adventure with object collection → Dizzy-style engine

**Code fingerprinting**: Each engine has characteristic code patterns:

| Pattern | Engine | How to spot |
|---|---|---|
| Large lookup tables at fixed addresses | Ultimate | Sprite address tables at #9000+, game state at #5C00+ |
| Bank-switched room data | Ocean Filmation | `LD A, room_number` / `OUT (#7FFD), A` pattern |
| Parallax scroll routines | Graftgold | `LDIR` of screen rows + partial redraw |
| AY register dump at fixed address | Any AY game | 14-byte block written to `#FFFD`/`#FFFD` ports |
| Interrupt-driven music player | Most AY games | ISR at `#0038` or IM2 vector, calls music routine |

**Asset signature detection**: Look for known music format headers in the binary:

```bash
# Search for PT3 header ("PT3" ASCII) in a snapshot's RAM
# PT3 magic: bytes #50 #54 #33 ("PT3")
xxd game.sna | grep "5054 33"

# Search for AY register dump ("PSG" + #1A)
xxd game.sna | grep "5053 471a"
```

---

## Asset Extraction

### Sprite Ripping

Sprites on the Spectrum are stored as raw bitmap data: each byte represents 8 pixels (1 bit per pixel). A sprite is a block of `width_bytes * height` bytes. For masked sprites, the format interleaves mask bytes and pixel bytes.

**Step 1: Find the sprite data**

Sprites are typically located in a contiguous block of RAM, often at the end of the code section or in a dedicated asset bank (on 128K games). Look for the characteristic patterns:

```
A 8x8 sprite (8 bytes):
#3C #7E #FF #FF #FF #FF #7E #3C
(circle — narrow top, wide middle, narrow bottom)

A 16x16 sprite (32 bytes):
#03 #07 #0F #1F #3F #7F #FF #FF
#FF #FF #7F #3F #1F #0F #07 #03
(triangle — progressively wider then narrower)
```

**Step 2: Determine the sprite format**

| Format | Bytes per row | Layout | Notes |
|---|---|---|---|
| 8x8 unmasked | 1 | 8 bytes total | Simplest format |
| 8x8 masked | 2 | 16 bytes (mask + pixel interleaved per row) | Mask byte = AND, pixel byte = OR |
| 16x16 unmasked | 2 | 32 bytes (2 bytes per row) | Two bytes per row |
| 16x16 masked | 4 | 64 bytes (mask + pixel interleaved) | Most common for game characters |
| Pre-shifted | N*8 | N copies at 8-pixel shift offsets | Used in fast sprite engines |

**Step 3: Extract with a hex editor or script**

```python
# Python script: extract sprites from a snapshot
import struct

# Read snapshot RAM (skip 27-byte SNA header)
with open("game.sna", "rb") as f:
    f.seek(27)
    ram = f.read(49152)  # 48K RAM

# Base address in Spectrum memory
base = 0x4000

# Sprite table at #9000 (offset in RAM = #9000 - #4000 = #5000)
sprite_addr = 0x9000 - base
sprite_size = 32  # 16x16 unmasked (2 bytes * 16 rows)
sprite_count = 16

for i in range(sprite_count):
    offset = sprite_addr + i * sprite_size
    sprite_data = ram[offset:offset + sprite_size]
    
    # Save as .IMG file (raw bitmap)
    with open(f"sprite_{i:02d}.img", "wb") as out:
        out.write(sprite_data)
    
    # Print ASCII preview
    print(f"Sprite {i}:")
    for row in range(16):
        row_bytes = sprite_data[row*2:row*2+2]
        bits = ""
        for byte in row_bytes:
            for bit in range(7, -1, -1):
                bits += "#" if (byte >> bit) & 1 else "."
        print(f"  {bits}")
    print()
```

**Step 4: Use specialized tools**

Several tools automate sprite ripping:

- **ZX Spectrum Analyser**: GUI tool that scans RAM for sprite-like data and displays previews. You select the format and export.
- **Seka Sprite Explorer**: Another GUI sprite ripper.
- **SevenUp (7UP)**: A full sprite/graphics editor that can import raw data from snapshots.

### Map Extraction

Game maps are stored as arrays of tile indices. Each byte (or nibble) represents one tile cell in the level layout. The map dimensions depend on the game:

| Game type | Map size | Tile size | Storage |
|---|---|---|---|
| Single-screen arcade | 32x24 | 8x8 | 768 bytes (1 byte per cell) |
| Scrolling shooter | Variable width | 8x8 | Column/table-based |
| Room-based adventure | 32x24 per room | 8x8 | Multiple room data blocks |
| Isometric | 16x16 room grid | 16x16 | 3D object lists, not tiles |

**Finding the map data**: Use memory diffing (see [analysis_techniques.md](analysis_techniques.md)). Enter a room, snapshot, move to another room, snapshot, diff. The changed bytes include the screen RAM (which changes every room) and the map/tile data for the current room.

```bash
# Diff two snapshots from different rooms
dd if=room1.sna bs=1 skip=27 of=ram1.bin
dd if=room2.sna bs=1 skip=27 of=ram2.bin
cmp -l ram1.bin ram2.bin | head -30
```

The bytes that change between rooms (other than screen RAM at offset 0-6911 from #4000) are the map data for the current room.

### Music Ripping

Music data on the Spectrum comes in several formats:

| Format | Magic bytes | Tracker | Typical location |
|---|---|---|---|
| PT3 | `"PT3"` at offset 0 | Vortex Tracker II | After game code, or in banked RAM |
| STC | Specific header pattern | Sound Tracker (ST) | Embedded in game binary |
| ASC | Specific header | Advanced Sound Creator | Banked RAM |
| SQT | Specific header | SQ Tracker | Banked RAM |
| PSG | `"PSG"` + `#1A` | Register dump format | Not embedded — captured during playback |

**Finding the music data**: Set a write watchpoint on the AY register port (`#FFFD`). When the music player writes AY registers, trace back to find the data source:

1. `wp #FFFD` — break on AY register select write
2. Single-step backward from the watchpoint to find the player routine
3. The player routine reads from a fixed address — that is the music data pointer
4. Follow the pointer to find the music data

```z80
; Typical AY music player call:
PlayMusic:
        LD   HL, (MusicDataPtr)   ; pointer to PT3 module data
        CALL #9C00                ; player routine address
        RET

MusicDataPtr:  DEFW MusicModule   ; points to PT3 data
MusicModule:   DB "PT3..."        ; PT3 header starts here
```

Once you locate the music data, copy it from the snapshot and save as a `.pt3` (or `.stc`, etc.) file.

---

## Cheat Code Creation

### Infinite Lives

The most common cheat request. The technique is described in [analysis_techniques.md](analysis_techniques.md) (the "Finding the Lives Counter" worked example). Summary:

1. Use memory diffing to find the lives counter address.
2. Set a write watchpoint on that address.
3. Let the player die to trigger the watchpoint.
4. The watchpoint reveals the decrement instruction.
5. NOP out the `DEC (HL)` or change it to `INC (HL)`.

### Infinite Energy/Health

Same technique as infinite lives, but the counter decreases continuously rather than at death events:

1. Snapshot at full health.
2. Take damage.
3. Snapshot at reduced health.
4. Diff to find the health counter.
5. Either NOP the decrement, or set the counter to maximum in an infinite loop (poke).

### Level Skip

1. Set a breakpoint on the room/level transition routine.
2. Trigger a level transition (complete the level or use a built-in cheat).
3. Examine the code at the breakpoint — it typically loads a new level number into a variable and calls the level loader.
4. Patch the code to allow arbitrary level selection, or create a keyboard-triggered level skip:

```z80
; Level skip patch: check for key press, increment level, reload
CheckSkipKey:
        IN   A, (#FE)           ; read keyboard
        AND  #01                ; check specific key
        RET  NZ                 ; not pressed, return
        ; Key pressed — skip to next level
        LD   HL, (LevelNumber)
        INC  (HL)
        CALL LoadLevel
        RET
```

### POKE Format

ZX Spectrum cheats are traditionally distributed as **POKEs** — memory address/value pairs that are written before the game starts. The format:

```
POKE address, value
```

For example, a classic infinite-lives POKE for a game with the lives counter at #8B42:

```
POKE 35650, 0     ; 35650 = #8B42, value 0 = NOP the DEC instruction
```

Or, to set the lives counter to 255:

```
POKE 35650, 175   ; 175 = #AF = XOR A (sets A=0)
POKE 35651, 50    ; 50 = #32 = LD (HL), n — not exactly right, simplified
```

In practice, POKEs are more targeted. The most common types:

| POKE type | What it does | Example |
|---|---|---|
| NOP the decrement | Prevents lives from decreasing | `POKE addr, 0` (NOP) |
| Change comparison | Makes check always pass | `POKE addr, #FE → #FF` |
| Set initial value | Gives 255 lives at start | `POKE counter_addr, 255` |
| Force branch | Makes conditional jump always take | `POKE addr, #18` (JR) or `#C9` (RET) |

---

## Save Game Format Analysis

Many Spectrum games have a save/load feature that writes game state to tape or disk. Reverse engineering this format allows creating save game editors.

### Typical Save Game Structure

```z80
; Save game format (game-specific, but follows this pattern):
SaveBuffer:
        DEFB SaveVersion          ; format version byte
        DEFW LevelNumber          ; current level
        DEFB Lives                ; lives remaining
        DEFB Health               ; current health
        DEFS InventoryFlags, 8    ; 8 bytes of inventory bits
        DEFW Score                ; player score (2 bytes)
        DEFW Score+2              ; high word of score
        DEFS PositionData, 4      ; X, Y, screen, direction
        DEFW Checksum             ; simple sum of all previous bytes
```

### Analyzing the Format

1. **Find the save routine**: Set a write watchpoint on the buffer address. Trigger a save. The watchpoint reveals the routine that fills the buffer.
2. **Trace each field**: Disassemble the save routine. Each `LD (nn), A` or `LD (nn), HL` instruction writes one field.
3. **Find the load routine**: Look for a complementary routine that reads the buffer. It will have matching `LD A, (nn)` or `LD HL, (nn)` instructions.
4. **Decode the checksum**: If the last field is a checksum, verify your understanding by modifying a save game and recalculating.

---

## Decompilation — Z80 to C Reconstruction

Full decompilation — automatically converting Z80 machine code back to C source — is not practical on the Spectrum. The Z80 code was hand-written in assembly, not compiled from C (with rare exceptions like some z88dk programs). However, **manual reconstruction** of assembly into readable C-like pseudocode is a common RE practice.

### Reconstruction Workflow

```z80
; Original Z80 assembly from disassembly:
UpdateScore:
        PUSH AF
        PUSH HL
        LD   HL, (Score)
        LD   A, (ScoreBonus)
        ADD  A, L
        LD   L, A
        JR   NC, NoCarry
        INC  H
NoCarry:
        LD   (Score), HL
        POP  HL
        POP  AF
        RET
```

Reconstructed as C:

```c
void update_score(uint8_t bonus) {
    score += bonus;  // score is a 16-bit variable at "Score"
}
```

### Reassembly to Source

The most practical form of "decompilation" on the Spectrum is **reassembly**: taking the annotated disassembly and converting it back into buildable assembly source. This is what SkoolKit's `skool2asm` tool does:

```bash
# Convert annotated .skool file to buildable .asm
skool2asm game.skool > game.asm

# Re-assemble with sjasmplus
sjasmplus game.asm
```

The result is a .asm file that can be modified, extended, and re-assembled. This is how the Spectrum community maintains "source code" for games whose original source is lost.

---

## Common Pitfalls

### 1. Wrong Sprite Format Assumption

Do not assume sprites are 8x8. Spectrum games use a wide variety of sprite sizes and formats. Always verify by visually inspecting the data in a hex editor or sprite viewer before extracting.

### 2. Banked Music Data

On 128K games, music data may be in a banked memory page that is not visible in a 48K snapshot. Ensure you have a 128K snapshot and check all 8 RAM banks for music data.

### 3. Compressed Assets

Many games compress their assets (sprites, maps, music) to fit in memory. If you find compressed data instead of raw assets, see [code_crunching.md](code_crunching.md) for decompression techniques. The assets may only be decompressed at runtime — take a snapshot after the game has loaded its assets.

### 4. Checksum-Protected Save Games

If a modified save game does not load, the checksum is likely wrong. Find the checksum verification routine in the load code and either fix the checksum or NOP the verification.

### 5. Game-Specific Variable Locations

Every game stores its variables at different addresses. Techniques that work for one game (e.g., "lives is at #8B42") will not work for another. Always use memory diffing to find variables for the specific game you are reversing.

---

## Cross-References

| Topic | Reference |
|---|---|
| RE methodology overview | [methodology.md](methodology.md) |
| Analysis techniques (static/dynamic) | [analysis_techniques.md](analysis_techniques.md) |
| Protection cracking | [protection_cracking.md](protection_cracking.md) |
| Code compression and packers | [code_crunching.md](code_crunching.md) |
| Snapshot repair | [snapshot_repair.md](snapshot_repair.md) |
| Software protection catalog | [protection_techniques.md](protection_techniques.md) |
| ROM routine entry points | [rom_routines.md](../10_references/rom_routines.md) |
| System variables | [system_variables.md](../04_operating_systems/system_variables.md) |
| Character set and tokens | [character_set.md](../10_references/character_set.md) |
| File format parsing | [file_format_handling.md](../05_development/08_dos_tape/file_format_handling.md) |
| Memory and I/O (48K) | [memory_and_io_48k.md](../05_development/03_memory_and_io/memory_and_io_48k.md) |

## References

### External references

- [The Tipshop Archive](https://thetipshop.org/) — multi-decade community archive of POKE lists, infinite-lives patches, and level-skip codes for thousands of commercial Spectrum titles; the primary source for reverse-engineering the resulting memory-mod patterns.
- [`spectranet` / `divide` / `divmmc` snapshot-based debugging references](https://github.com/spectrum-pi/spectranet) — modern real-hardware debugging infrastructure that allows setting hardware breakpoints and reading machine state without affecting game timing.
- [zx-pk.ru game reversing forum](https://zx-pk.ru) — primary Russian-language venue for documented analyses of Soviet-era RPGs (*Black Crow*, *Star Legacy*) and the custom data formats they used.
- [The Speedlock Reference](https://worldofspectrum.org/forums/discussion/52570/) — the canonical English-language analysis of the Speedlock / Alkatraz families used on Western commercial titles.
- [IDA Pro / Ghidra Z80 processor modules](https://hex-rays.com/ida-pro/) — the two leading disassemblers used for game reversing; both support annotating memory maps, structuring data layouts, and identifying standard library calls.
