[← Home](../../README.md) · [I/O](../../README.md) · [Snapshots](README.md)

# The .RZX Replay Format

The three snapshot formats covered so far — [.SNA](sna_format.md), [.Z80](z80_format.md), [.SZX](szx_format.md) — all capture a single instant in time: the machine state at one moment. But there is another way to "save" Spectrum software: instead of recording the state, **record the input**. If you start from a known machine state and feed the same inputs in the same order, the emulator will deterministically reproduce the same execution — and the same on-screen action.

The **.RZX format** (created in 2001 by the **RZX Working Group** — Andrew Broad, Phillip G. Kendall, and other Spectrum community members) is the standard format for **input recordings**. It captures the keyboard and joystick inputs over time, allowing a "movie" of Spectrum software to be recorded, shared, and replayed. .RZX is used for verified game completions (the RZX Archive on World of Spectrum), speedruns, bug reproductions, and tutorial distribution.

This article covers the .RZX format: its history, the file structure, how input is encoded, the snapshot-embedding mechanism, the cryptographic signing used for verified recordings, how to write a recorder and player, and the gotchas. For the snapshot formats that .RZX recordings build upon, see the previous articles in this section.

---

## Roadmap

1. **What the .RZX format is** — history, scope, use cases
2. **The file structure** — blocks: header, creator, snapshot, input
3. **The input recording blocks** — how input is encoded frame by frame
4. **Snapshot embedding** — how the initial state is captured or referenced
5. **Cryptographic signing** — verified recordings and the RZX Archive
6. **Writing an .RZX recorder** — capturing input from an emulator
7. **Writing an .RZX player** — replaying a recording deterministically
8. **Compatibility and quirks** — emulator support, validation, common issues
9. **Comparison with snapshots** — when to use .RZX vs .SNA/.Z80/.SZX
10. **Cross-references** — where to go next

---

## §1. What the .RZX Format Is

### 1.1 Origins

The .RZX format was created in 2001 by the **RZX Working Group**, an informal collective of Spectrum community members including **Andrew Broad**, **Phillip G. Kendall**, **Darren J. N. Scales**, **Marek Januszewski**, and others. The motivation was the **RZX Archive** — a project to create a verified, peer-reviewed library of "completed" Spectrum games.

The problem the RZX Archive was solving: how do you prove that you actually completed a game? Anyone can claim to have reached the end screen, but a screenshot is trivially fakeable. The RZX Archive's solution was to require an **input recording** — a file that, when replayed against the game's snapshot, deterministically reproduces the entire playthrough. The recording can be inspected, validated, and verified by the community.

The .RZX format was designed to be that recording file. It was based on earlier "demo" formats used by various emulators (notably X128's `.dem` format and Spectrum+ALF's `.piolet` format), but standardized into a single open format supported by every major emulator.

### 1.2 Scope

An .RZX file contains:

- A **header** identifying the file as .RZX and specifying the version.
- A **creator block** identifying the emulator that created the recording, plus version and timing info.
- An optional **embedded snapshot** — a .SNA or .Z80 file representing the initial machine state.
- A sequence of **input blocks** — each recording the keyboard/joystick state for a number of video frames.
- An optional **cryptographic signature** — proving that the recording is authentic and unmodified.

Unlike a snapshot, an .RZX file does **not** contain RAM contents or register values (beyond the optional initial snapshot). It is purely a recording of inputs over time. To play it back, the emulator loads the snapshot and then "plays" the inputs in sequence, producing the same machine state as the original recording.

### 1.3 Use cases

The .RZX format supports several use cases:

- **Verified game completions**: the RZX Archive (now hosted by World of Spectrum) uses .RZX files as proof that a game has been completed. The files are cryptographically signed and peer-reviewed.
- **Speedruns**: speedrunners use .RZX files to share their playthroughs. The format records the inputs, allowing anyone to replay the run on their own emulator.
- **Bug reproductions**: developers use .RZX files to reproduce and share bugs. A 10-second .RZX recording can show exactly what inputs triggered a bug.
- **Tutorial distribution**: .RZX files can serve as interactive tutorials — a player can watch the inputs and the resulting action, learning how to play a game.
- **Tool-assisted speedruns (TAS)**: TAS enthusiasts use .RZX files to share their frame-perfect playthroughs.

### 1.4 Why .RZX matters

.RZX matters because it enables **deterministic sharing of gameplay**. Unlike video recordings (which are large and not interactive), an .RZX file is small (typically a few KB to a few hundred KB) and can be inspected, paused, rewound, and modified. This makes it invaluable for:

- **Game preservation**: the RZX Archive contains thousands of .RZX files documenting how Spectrum games are played and completed.
- **Emulator development**: .RZX files are used as regression tests for emulator accuracy — if an emulator correctly replays an .RZX file, the emulator is producing the same machine state as the original recording.
- **Speedrun verification**: speedrun.com and other communities accept .RZX recordings as evidence of speedrun claims.

---

## §2. The File Structure

The .RZX file uses a **block-based** structure similar to .SZX. Each block has an ID, length, and data. Unlike .SZX, however, .RZX blocks have a more constrained set of types.

### 2.1 The file header (10 bytes)

Every .RZX file begins with a 10-byte header:

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 4 | Magic | "RZX!" (#52 #5A #58 #21) — identifies this as an .RZX file |
| 4 | 4 | Version (32-bit, little-endian) | The .RZX format version. Currently 1 (#01 #00 #00 #00) |
| 8 | 2 | Flags | Bit 0: embedded snapshot present; other bits reserved |

If the first 4 bytes are not "RZX!", the file is not an .RZX file. Loaders should reject it.

### 2.2 The blocks

After the 10-byte header, the file consists of a sequence of blocks. Each block has the following structure:

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID |
| 1 | 4 | Block data length (32-bit, little-endian) — includes the 5-byte block header |
| 5 | (length - 5) | Block data |

The block ID identifies the block type. The block data length gives the total size of the block, including the 5-byte block header.

### 2.3 The standard block types

| Block ID | Name | Content |
|---|---|---|
| #01 | Creator | The emulator that created the recording, plus version and timing info |
| #02 | Snapshot | An embedded initial snapshot (`.SNA`, `.Z80`, or `.SZX`) |
| #03 | Input | A chunk of input recording (one or more frames of input data) |
| #04 | Sign | A cryptographic signature for verified recordings |
| #10 | Creator info extension | Additional creator metadata (rare) |
| #80+ | (Reserved for custom blocks) | Custom block IDs for private extensions |

A typical .RZX file has the following block order:

1. **Creator block** (mandatory, comes first)
2. **Snapshot block** (optional, but typically present for self-contained recordings)
3. **Input blocks** (one or more, containing the actual recording)
4. **Sign block** (optional, for verified recordings)

Some emulators concatenate many input blocks (one per minute of recording, for example) to allow efficient seeking. Others use a single input block for the entire recording.

### 2.4 Hex view

A visual layout of a small .RZX file:

```
Offset 0x00: 52 5A 58 21 01 00 00 00 01 00    <- File header: "RZX!" v1, flag = embedded snapshot
Offset 0x0A: 01 21 00 00 00                    <- Block: ID=0x01 (Creator), length=33
Offset 0x0F: 46 75 73 65 ...                   <- Block data: "Fuse" emulator info
...
Offset 0x2A: 02 39 40 00 00                    <- Block: ID=0x02 (Snapshot), length=16473
Offset 0x2F: 53 4E 41 ...                      <- Block data: "SNA" snapshot data
...
Offset 0x4039: 03 30 75 00 00                  <- Block: ID=0x03 (Input), length=30000
Offset 0x403E: C0 27 09 00 ...                 <- Block data: 500 frames of input
...
Offset 0xB647: 04 81 00 00 00                  <- Block: ID=0x04 (Sign), length=129
Offset 0xB64C: 30 82 01 20 ...                 <- Block data: cryptographic signature
```

This layout — header followed by heterogeneous blocks — is typical of replay formats.
---

## §3. The Input Recording Blocks

The input blocks (block ID `0x03`) are the heart of an .RZX file. They contain the actual recorded input — the sequence of keyboard and joystick states over time.

### 3.1 The input block header

Each input block begins with a header:

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | Number of frames | The number of video frames this block records (each frame is 1/50 second on PAL) |
| 4 | 4 | T-states per frame | The number of CPU T-states in each frame (used for cycle-accurate replay) |

For the 48K Spectrum, T-states per frame is 69888 (the standard PAL timing). For the 128K, it's 70908. For the Pentagon, it's 71680. This value is critical for cycle-accurate replay.

### 3.2 The frame entry format

After the 8-byte block header, the input block contains a sequence of **frame entries**. Each frame entry is variable-length and uses a run-length encoding scheme: one entry can describe the input for one frame or for many consecutive frames at once.

The frame entry header is 8 bytes:

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | Frame count | The number of consecutive frames this entry applies to (1 = just this frame; 60 = the next 60 frames) |
| 4 | 4 | Number of IN reads | How many IN port reads were performed during these frames |

If the number of IN reads is 0, no further data follows for this entry — the frame's inputs are simply "no IN reads happened" (which means the program did not poll any input during this frame, common in title screens or attract modes).

If the number of IN reads is N, then N×4 bytes of IN read data follow:

| Offset (within IN read data) | Size | Field |
|---|---|---|
| 0 | 2 | Port address (the value placed on the address bus during the IN) |
| 2 | 2 | Value read from the port (the byte that the program received) |

### 3.3 Why this format?

The .RZX input format is unusual in that it records **what the program read**, not what the user pressed. This is a deliberate design choice:

- **Hardware independence**: The format does not need to model the Spectrum's keyboard matrix or any specific joystick interface. It just records "the program did `IN A, (#FE)` and got `0xDF`".
- **Compression efficiency**: If the program polls the same port with the same input multiple times in a row, the recording can use a single frame entry with `count > 1`.
- **Robustness**: The format captures the actual machine behavior, not the user's intention. This means the recording will replay correctly even on an emulator with slightly different input handling.

The downside is that the format is tied to the emulator's IN-port handling — if the emulator's keyboard/joystick handling changes, old recordings may not replay correctly. This is why .RZX recordings are tied to a specific emulator version (recorded in the creator block).

### 3.4 The frame count field

The `frame count` field is the primary compression mechanism. A long stretch of "no input" (e.g., the title screen of a game waiting for a key press) can be recorded as a single frame entry with `count = 1000` (meaning "the next 1000 frames have no IN reads"). This compresses 20 seconds of inactivity into 8 bytes.

For active gameplay, frame counts are typically 1 (each frame has its own input data).

### 3.5 Worked example

Consider a simple recording of a 3-second Spectrum session:

- Frame 0: Game shows title screen, no input.
- Frames 1–149: Still no input (3 seconds of waiting).
- Frame 150: Player presses SPACE to start the game. `IN A, (#FE)` returns `0xFE` (space pressed).
- Frames 151–199: Player plays the game, polling keyboard each frame.

The input block would contain:

```
[Block header: frames = 200, T-states per frame = 69888]

[Frame entry 1]
  count = 150          <- "no input for the first 150 frames"
  num_IN_reads = 0

[Frame entry 2]
  count = 1            <- "1 frame with the following input"
  num_IN_reads = 1
  IN read 1: port=#FE, value=0xFE

[Frame entry 3]
  count = 49           <- "next 49 frames with the following input each"
  num_IN_reads = 1
  IN read 1: port=#FE, value=0xEF
  ...
```

This encoding is very compact for typical gameplay recordings.

---

## §4. Snapshot Embedding

The snapshot block (block ID `0x02`) is optional but commonly present. It contains the initial machine state that the recording should be played against.

### 4.1 The snapshot block format

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | Snapshot flags | Bit 0: snapshot is compressed (.gz); Bits 1–7: reserved |
| 4 | 4 | Snapshot length | The size of the snapshot data that follows |
| 8 | 32 | Snapshot MD5 hash | MD5 hash of the snapshot data (for verification) |
| 40 | varies | Snapshot data | The actual snapshot file contents (.SNA, .Z80, or .SZX) |

The snapshot data is a complete, standard snapshot file in one of the three formats (.SNA, .Z80, or .SZX). The MD5 hash is used by the player to verify that the snapshot has not been corrupted.

### 4.2 Why embed a snapshot?

Embedding the snapshot makes the .RZX file **self-contained** — the player can load the recording and replay it without needing any external files. This is essential for sharing recordings (e.g., via the RZX Archive, where each recording must work independently).

The downside is file size: an .RZX file with an embedded snapshot is at least as large as the snapshot itself (49 KB for a 48K .SNA, plus the recording data). For long recordings, this overhead is negligible.

### 4.3 External snapshot references

Some .RZX recordings use an **external** snapshot instead of an embedded one. In this case, the snapshot block contains only the snapshot's MD5 hash and a hint (typically the filename). The player must locate the snapshot in its own library and load it before playing the recording.

External snapshot references are less common but useful for:

- **Reducing file size**: When many recordings use the same starting snapshot (e.g., the title-screen snapshot of a popular game).
- **Encouraging standard snapshots**: The RZX Archive has a standard set of "title-screen snapshots" for each game, which recordings can reference by hash.

### 4.4 Snapshot format choice

The .RZX format does not mandate a particular snapshot format. For maximum compatibility, recordings typically use .SNA (since every emulator can load it). For complex recordings (e.g., 128K software, +3 software, or software with peripheral state), .Z80 or .SZX is used.

---

## §5. Cryptographic Signing

The sign block (block ID `0x04`) contains a cryptographic signature proving that the recording is authentic and unmodified. This is the foundation of the RZX Archive's verification system.

### 5.1 The sign block format

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | Signature organisation ID | Identifies who signed the recording (e.g., the RZX Archive) |
| 4 | 4 | Signature length | The size of the signature data that follows |
| 8 | varies | Signature data | The actual cryptographic signature (typically RSA or DSA) |

The signature is computed over the entire .RZX file contents up to (but not including) the sign block. This means the creator block, snapshot block, and all input blocks are covered by the signature.

### 5.2 How signing works

1. The recorder plays through the game in an emulator that supports .RZX recording (e.g., Fuse, ZEsarUX).
2. The emulator produces an .RZX file with the recording.
3. The recorder (or a third-party validator) computes the cryptographic signature of the .RZX file using the signing organisation's private key.
4. The signature is appended as the sign block.
5. The signed .RZX file is distributed.

To verify a signed recording:

1. The player reads the signature from the sign block.
2. The player recomputes the signature of the .RZX file (everything before the sign block).
3. The player compares the recomputed signature against the stored one, using the signing organisation's public key.
4. If they match, the recording is authentic and unmodified.

### 5.3 Why signing matters

Without signing, an .RZX recording could be modified (e.g., to fake a high score) without detection. The signature makes modification detectable — any change to the recording invalidates the signature.

This is what makes the RZX Archive trustworthy. When the Archive lists a recording as "verified", it means the recording has a valid signature from a trusted source (the Archive's own signing key). Players can be confident that the recording is genuine.

### 5.4 The RZX Archive's signing process

The RZX Archive uses a multi-step verification process:

1. **Initial recording**: The recorder plays through the game and produces an .RZX file.
2. **Self-validation**: The recorder replays their own .RZX file to verify it produces the expected result.
3. **Submission**: The .RZX file is submitted to the RZX Archive.
4. **Peer review**: Other community members replay the .RZX file in their own emulators. If they see the same result, the recording is considered valid.
5. **Signing**: The Archive's maintainer signs the .RZX file with the Archive's private key and adds it to the public library.

This multi-step process ensures that recordings are not only cryptographically authentic but also verified to produce the claimed result.

---

## §6. Writing an .RZX Recorder

This section covers the practical implementation of an .RZX recorder — the code that runs inside an emulator, watches every IN instruction the program executes, and writes the recording to a file.

### 6.1 The recording loop

The recorder integrates with the emulator's main CPU execution loop. For each emulated video frame:

1. Initialise a per-frame buffer of IN reads (empty at frame start).
2. Run the Z80 for `T_states_per_frame` T-states.
3. Whenever the program executes an `IN r, (C)` or `IN A, (n)` instruction, record the port address and the value returned in the per-frame buffer.
4. At the end of the frame, emit a frame entry: `count`, `num_IN_reads`, and the IN read data.

The pseudo-code:

```c
void rzx_record_frame(EmulatorState *emu, RzxFile *rzx) {
    InRead frame_buffer[MAX_IN_READS_PER_FRAME];
    int n_reads = 0;

    // Hook IN instructions to call rzx_capture_in() below
    g_current_frame_buffer = frame_buffer;
    g_current_n_reads = &n_reads;

    // Run one frame
    z80_run_tstates(emu->cpu, emu->t_states_per_frame);

    // Check if this frame's input is identical to the previous frame's
    // (for run-length compression)
    if (n_reads == rzx->last_entry_n_reads &&
        memcmp(frame_buffer, rzx->last_entry_reads,
               n_reads * sizeof(InRead)) == 0) {
        // Identical input: extend the previous entry's frame count
        rzx->last_entry->count++;
    } else {
        // New input: emit a new frame entry
        rzx_emit_frame_entry(rzx, 1, n_reads, frame_buffer);
        rzx->last_entry = rzx->current_entry;
        rzx->last_entry_n_reads = n_reads;
        memcpy(rzx->last_entry_reads, frame_buffer,
               n_reads * sizeof(InRead));
    }
}

// Hook called from the CPU core on every IN instruction
void rzx_capture_in(uint16_t port, uint8_t value) {
    if (*g_current_n_reads < MAX_IN_READS_PER_FRAME) {
        g_current_frame_buffer[*g_current_n_reads].port = port;
        g_current_frame_buffer[*g_current_n_reads].value = value;
        (*g_current_n_reads)++;
    }
}
```

### 6.2 Run-length compression

The example above includes the most important optimisation: **run-length compression of identical frames**. If the program polls the same port with the same value for 50 frames in a row (typical of a "press any key" prompt), the recorder produces a single frame entry with `count = 50` instead of 50 separate entries. This typically reduces the recording size by an order of magnitude.

Some emulators take this further by **coalescing non-adjacent but identical frames** (e.g., frames 100–149 and 150–199 with identical input). However, this is non-standard and risks subtly altering replay semantics if the program's behavior depends on the exact frame count.

### 6.3 Capturing the initial snapshot

At the start of recording, the recorder writes a snapshot block containing the current machine state. The recorder must:

1. Generate the snapshot (typically `.SNA` for 48K software, `.Z80` for 128K software, or `.SZX` for complex state).
2. Compute the MD5 hash of the snapshot data.
3. Write the snapshot block (flags, length, MD5, snapshot data).

```c
void rzx_write_initial_snapshot(RzxFile *rzx, EmulatorState *emu) {
    uint8_t snap[65536];
    size_t snap_len = write_sna_to_buffer(emu, snap, sizeof(snap));

    uint8_t md5[16];
    md5_compute(snap, snap_len, md5);

    RzxBlockSnap hdr = {
        .flags = 0,
        .length = snap_len
    };
    memcpy(hdr.md5, md5, 16);

    rzx_write_block_header(rzx, 0x02, sizeof(hdr) + snap_len);
    rzx_write(rzx, &hdr, sizeof(hdr));
    rzx_write(rzx, snap, snap_len);
}
```

### 6.4 The creator block

The creator block identifies the emulator that produced the recording. This is important for compatibility: if a recording only replays correctly on one emulator (due to quirks in that emulator's IN-port handling), the creator block lets the user know which emulator to use.

```c
typedef struct {
    char     emulator_name[32];   // Null-terminated: "Fuse", "ZEsarUX", "SpecEmu", etc.
    uint32_t emulator_version;    // Major/minor/patch packed into 32 bits
    uint32_t t_states_per_frame;  // 69888 for 48K, 70908 for 128K, etc.
    uint32_t flags;               // Bit 0: competition mode; other bits reserved
    // ... additional creator metadata
} RzxCreatorBlock;
```

The `competition mode` flag (bit 0 of flags) indicates that the recording was made under "competition conditions" — no save states, no slow-motion, no pausing. Competition recordings are sometimes marked separately in speedrun leaderboards.

### 6.5 Closing the recording

When the user stops recording (or the emulator exits), the recorder:

1. Flushes any pending input block data.
2. Optionally computes and writes the cryptographic signature (if the recorder has access to a signing key — typically not; signing is done by the RZX Archive maintainer).
3. Closes the file.

The resulting `.rzx` file is ready for replay on any .RZX-aware emulator.

---

## §7. Writing an .RZX Player

The player is the inverse of the recorder: it loads the snapshot, replays the input, and reproduces the original machine state and on-screen action.

### 7.1 The replay loop

```c
int rzx_play(RzxFile *rzx, EmulatorState *emu) {
    // Step 1: Load the embedded snapshot
    if (rzx->snapshot_data) {
        uint8_t computed_md5[16];
        md5_compute(rzx->snapshot_data, rzx->snapshot_len, computed_md5);
        if (memcmp(computed_md5, rzx->snapshot_md5, 16) != 0) {
            fprintf(stderr, "Snapshot MD5 mismatch — file may be corrupt\n");
            return -1;
        }
        load_sna_from_buffer(emu, rzx->snapshot_data, rzx->snapshot_len);
    }

    // Step 2: Replay each frame entry
    g_replay_active = true;
    for (int i = 0; i < rzx->n_input_blocks; i++) {
        RzxInputBlock *block = &rzx->input_blocks[i];
        g_t_states_per_frame = block->t_states_per_frame;

        for (int j = 0; j < block->n_entries; j++) {
            RzxFrameEntry *entry = &block->entries[j];

            // Install the IN-read overrides for this entry
            g_overrides = entry->reads;
            g_n_overrides = entry->n_reads;
            g_override_index = 0;

            // Run 'count' frames with these overrides
            for (int f = 0; f < entry->count; f++) {
                g_override_index = 0;  // Reset at start of each frame
                z80_run_tstates(emu->cpu, g_t_states_per_frame);
            }
        }
    }
    g_replay_active = false;
    return 0;
}

// Hook called from the CPU core on every IN instruction during replay
uint8_t rzx_replay_in(uint16_t port) {
    if (g_replay_active) {
        if (g_override_index < g_n_overrides &&
            g_overrides[g_override_index].port == port) {
            return g_overrides[g_override_index++].value;
        }
        // Port read not in recording: emulator bug or non-determinism
        fprintf(stderr, "Unexpected IN port %04X during replay\n", port);
        return 0xFF;
    }
    return normal_in_port_read(port);
}
```

### 7.2 Determinism

Replay is only correct if the emulator's execution is **deterministic** — that is, given the same snapshot and the same inputs, the emulator produces exactly the same machine state at every point. This requires:

- **Cycle-accurate Z80 emulation**: every instruction must take the same number of T-states as on real hardware. Contended memory timing (the "slow RAM" delay when accessing the upper 16K of the 48K Spectrum) must be modeled correctly.
- **Deterministic peripheral behavior**: the AY chip, the beeper, the floating bus, and the keyboard matrix must all produce the same output for the same inputs.
- **No real-time dependencies**: the emulator must not sample the host's clock, host's keyboard, or host's random number generator during replay. All randomness in the emulated machine must come from the snapshot or the input.

If determinism is violated (e.g., the emulator reads the host's clock during replay), the replay will diverge from the original recording. The first sign of divergence is usually an unexpected IN port read — the player's `rzx_replay_in()` will hit the "unexpected IN port" branch.

### 7.3 Validation

After replay, the player should validate that the replay was successful. The most common validation is to compute a hash of the final machine state (or a portion of it, such as the screen memory) and compare it against an expected hash recorded alongside the .RZX file. Some emulators also display the final frame to the user and let them visually verify the result.

For RZX Archive recordings, the validation is even stricter: the recording is considered valid only if the final screen shows the expected "game completed" message. This is typically verified by visual inspection during peer review (see §5.4).

### 7.4 Seeking

For long recordings, the player may want to support seeking — jumping to a specific frame in the recording. This is done by:

1. Loading the initial snapshot.
2. Replaying all frames up to (but not including) the target frame.
3. Pausing replay at the target frame.

Because replay is fast (typically much faster than real-time on modern hardware), seeking is usually implemented as "fast-forward replay". Some .RZX files include periodic embedded snapshots (every N frames) to make seeking faster, but this is non-standard and bloats the file.

---

## §8. Compatibility and Quirks

### 8.1 Emulator support

| Emulator | Record | Replay | Sign | Verify | Notes |
|---|---|---|---|---|---|
| **Fuse** | ✅ | ✅ | ✅ | ✅ | Reference implementation; produces the canonical .RZX format |
| **ZEsarUX** | ✅ | ✅ | ❌ | ✅ | Full record/replay support; relies on external signing |
| **SpecEmu** | ✅ | ✅ | ❌ | ✅ | Competition-mode recording for speedrun leaderboards |
| **EightyOne** | ✅ | ✅ | ❌ | ❌ | Supports .RZX for the Spectrum and several clones |
| **SPIN** | ✅ | ✅ | ❌ | ❌ | Older but still used; some quirks with 128K recordings |
| **Klive** | ✅ | ✅ | ❌ | ✅ | Modern emulator with strong .RZX support |
| **Qaop** | ❌ | ✅ | ❌ | ❌ | Replay-only (browser-based) |

The RZX Archive accepts recordings from any emulator, but recommends Fuse for compatibility.

### 8.2 Common quirks

- **Non-deterministic games**: Some games use the R register or the floating bus as a source of randomness. If the emulator's R-register emulation or floating-bus emulation differs from the original recording's emulator, the replay will diverge. This is rare but does happen.
- **Contention-sensitive code**: Code that depends on exact memory contention timing (e.g., some effects in demos) may not replay correctly if the player's contention model differs from the recorder's. For demo recordings, .SZX snapshots at each effect are sometimes preferred over .RZX.
- **Multiple input blocks**: Some emulators write a single input block for the entire recording; others write many input blocks (one per minute, or one per save-state boundary). Players must handle both.
- **Empty recordings**: An .RZX file with zero frames is technically valid (a "recording" of nothing) and players should handle it gracefully.
- **Truncated recordings**: If an emulator crashes during recording, the resulting .RZX file may be truncated. Players should detect this and warn the user.

### 8.3 The competition mode flag

The creator block's `competition mode` flag (bit 0 of flags) indicates that the recording was made under strict conditions:

- No save states used.
- No slow-motion or fast-forward during recording.
- No pausing.
- The recording started from a clean boot (or a standard starting snapshot).

Speedrun leaderboards that accept .RZX recordings typically require this flag to be set. Some emulators enforce these conditions when recording in competition mode (e.g., by disabling the save-state hotkeys).

### 8.4 Version compatibility

The .RZX format has remained at version 1 since its introduction in 2001. There are no known compatibility issues between .RZX files produced by different emulators, provided both emulators correctly implement the specification. The format's simplicity (a flat sequence of blocks) has proven sufficient for all use cases to date.

A proposed version 2 (with support for cycle-exact recording — capturing not just the port and value of each IN read, but the exact T-state at which it occurred) has been discussed but not implemented. For cycle-exact use cases, .SZX snapshots at each interesting moment remain the preferred approach.

---

## §9. Comparison with Snapshots

How does .RZX compare with the snapshot formats (.SNA, .Z80, .SZX)?

| Feature | .RZX | .SNA | .Z80 | .SZX |
|---|---|---|---|---|
| **What it captures** | Input over time | Single state | Single state | Single state |
| **File size (typical)** | 50–500 KB | 49–131 KB | 50–200 KB | 50–500 KB |
| **Self-contained** | ✅ (with snapshot) | ✅ | ✅ | ✅ |
| **Captures AY state** | ✅ (via snapshot) | ❌ | ✅ | ✅ |
| **Captures clone state** | ✅ (via snapshot) | ❌ | ✅ (v3) | ✅ |
| **Cryptographic signing** | ✅ | ❌ | ❌ | ❌ |
| **Reproducible across emulators** | Usually | N/A | N/A | N/A |
| **Best for** | Playthroughs, speedruns, validation | Quick 48K saves | Rich 128K saves | Complex state, modern hardware |

### 9.1 When to use .RZX

- You want to record a **playthrough** of a game (e.g., for the RZX Archive).
- You want to share a **speedrun** with verifiable proof.
- You want to **reproduce a bug** in a piece of Spectrum software.
- You want to create a **tutorial** showing how to play a game.

### 9.2 When to use a snapshot

- You want to **save your progress** at a specific point in a game.
- You want to **distribute** a piece of Spectrum software (snapshots are commonly used for cracked or modified versions).
- You want to capture a **specific visual state** (e.g., a title screen) for archival purposes.
- You are working with **Russian clone software** or **Next software** with complex peripheral state.

### 9.3 Combining .RZX with snapshots

Many workflows combine both: a starting snapshot captures the initial state, and an .RZX recording captures the input from there. This is exactly what .RZX's snapshot-embedding feature is for. The result is a self-contained file that can be replayed anywhere.

For very long playthroughs, some archivists insert "checkpoint snapshots" at intervals (e.g., every 5 minutes) to allow fast seeking. This is non-standard but supported by some emulators as a custom block type.

---

## §10. Cross-References

### 10.1 Other snapshot formats

- [sna_format.md](sna_format.md) — the simplest snapshot format, 48K and 128K variants. The historical default.
- [z80_format.md](z80_format.md) — the most widely-supported "rich" snapshot format, with three versions covering 48K, 128K, and clones.
- [szx_format.md](szx_format.md) — the chunk-based modern snapshot format used by ZEsarUX, capable of capturing essentially any Spectrum state.

### 10.2 Related I/O articles

- Keyboard interface — how the Spectrum's keyboard matrix is read via IN port `#FE`. The .RZX format records the bytes returned by these IN reads, not the keys themselves.
- Joystick interfaces (Kempston, Sinclair, Fuller) — how joysticks are read. These are also captured as IN reads in .RZX.
- Tape and disk loading — these are not directly recorded in .RZX (they happen during the embedded snapshot loading, before the recording starts).

### 10.3 External resources

- [RZX Archive](https://worldofspectrum.org/) on World of Spectrum — the canonical library of verified .RZX recordings.
- **RZX format specification** — the original specification document by the RZX Working Group (2001).
- [Fuse emulator](https://fuse-emulator.sourceforge.net/) — the reference implementation of .RZX recording and playback.
- **speedrun.net** and other speedrun communities — accept .RZX recordings as proof of completion.

### 10.4 Where to go next

After understanding .RZX, the natural next steps are:

- **Reverse engineering** — .RZX recordings are useful for reproducing bugs and analysing game logic. See [reverse_engineering/](../../08_reverse_engineering/) for the broader topic.
- **Demoscene analysis** — .RZX recordings of demos can help understand how visual effects are produced. See [demoscene/](../../07_demoscene/).
- **Emulator development** — implementing .RZX record/replay is a useful exercise in emulator determinism. See [emulation/](../../11_emulation/).

---

## License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share and adapt this material, provided you credit the original source and license your contributions under the same terms.

For the canonical text of the license, see https://creativecommons.org/licenses/by-sa/4.0/.
