[← Plan](../PLAN.md) · [Reverse Engineering](README.md)

# Protection Cracking — Defeating Speedlock, Alkatraz, and Disk Schemes

ZX Spectrum commercial software was protected by a layered system of custom loaders, encryption, timing checks, and anti-debugging tricks. This article is the practical companion to [protection_techniques.md](protection_techniques.md) — that article catalogs **what** the protections are; this article shows **how to crack them**. Every major protection system on the Spectrum has been defeated, and the techniques are well-documented. This article collects them in one place, with worked examples and byte-level analysis.

> [!NOTE]
> This article assumes you have read [protection_techniques.md](protection_techniques.md) (the protection catalog) and [analysis_techniques.md](analysis_techniques.md) (the disassembly and debugging toolchain). It expands protection_techniques.md sections 1-3 with practical cracking procedures.

---

## The Cracking Workflow

Every tape-based protection system on the Spectrum follows the same general pattern:

```
1. Standard ROM header block (loading screen + name)
2. Custom loader code (loaded at turbo speed)
3. Encrypted/compressed payload
4. Decryption stub (runs after loading, decrypts payload in RAM)
5. Execution transfers to decrypted code
```

The cracker's goal is to extract the decrypted payload **after step 4 but before step 5** — producing a clean snapshot that contains the unprotected game code with no custom loader, no encryption, and no timing checks.

### The Universal Approach: Snapshot at the Right Moment

The single most powerful cracking technique is **timing the snapshot**. The decryption stub must decrypt the code into RAM before executing it. If you can interrupt execution at exactly the right moment — after decryption, before the game starts — you capture the unprotected code.

**Procedure**:

1. Load the protected tape in ZEsarUX.
2. Set a breakpoint at the address where execution transfers from the loader to the decrypted game (usually a `JP nn` or `CALL nn` to the game's entry point).
3. Let the tape load. The breakpoint triggers after decryption.
4. Save a snapshot. This snapshot contains the fully decrypted game code.

The challenge is finding the right breakpoint address. The following sections show how to find it for each protection system.

---

## Speedlock Deep-Dive

Speedlock was the most widely used commercial tape protection system, appearing in hundreds of titles from 1985-1990. It used a multi-stage loading sequence with XOR encryption and a timing-based verification loop.

### Speedlock Loading Sequence

A typical Speedlock-protected tape has this structure:

| Block | ROM/Custom | Content | Purpose |
|---|---|---|---|
| 1 | ROM standard | Header (17 bytes) | Loading screen, program name |
| 2 | ROM standard | Loading screen data | Displays while loading |
| 3 | Custom turbo | Loader code (~512 bytes) | Speedlock decryption engine |
| 4 | Custom turbo | Encrypted payload (~40K) | XOR-encrypted game code |

Block 3 is the Speedlock engine. It is loaded at a known address (typically `#5E00` or `#8500`) and executes immediately upon loading. The engine then loads block 4 (the encrypted payload) and decrypts it in place.

### Identifying Speedlock

Speedlock loaders have recognizable signatures. The pilot tone for the custom blocks uses a distinctive pattern:

```
Speedlock pilot: ~10000+ pulses at custom timing
Bit 0: 600 T-states (vs ROM 855)
Bit 1: 1200 T-states (vs ROM 1710)
```

In a .TZX file, Speedlock blocks use block type `#11` (turbo speed data) with these specific timing values. You can identify a Speedlock tape by examining the .TZX block structure:

```bash
# SkoolKit's tzxlist shows block details
tzxlist game.tzx
# Look for: block type #11 with pilot=2168, sync1=600, sync2=1200
```

### Speedlock Decryption Analysis

The Speedlock decryption engine typically works as follows:

```z80
; Simplified Speedlock decryption engine
; (Actual implementations vary by version — v1, v2, v3 differ)

SpeedlockInit:
        LD   HL, EncryptedStart     ; #8000 typically
        LD   BC, EncryptedLength    ; ~40000 bytes
        LD   A, (DecryptionKey)     ; XOR key byte

DecryptLoop:
        XOR  (HL)                   ; decrypt byte
        LD   (HL), A                ; write back decrypted byte
        INC  HL                     ; next byte
        DEC  BC                     ; decrement counter
        LD   A, B
        OR   C
        JR   Z, DecryptDone
        LD   A, (DecryptionKey)     ; reload key (some versions rotate it)
        JR   DecryptLoop

DecryptDone:
        ; Timing verification check
        LD   BC, #0000              ; counter
TimingLoop:
        DEC  BC                     ; tight loop
        JR   NZ, TimingLoop
        ; Check if BC reached expected value
        ; If tape motor speed was wrong (copy), timing differs
        LD   HL, (ExpectedTiming)
        AND  A
        SBC  HL, BC
        JR   NZ, TimingFail         ; timing mismatch = copy detected
        ; Timing OK — execute decrypted game
        JP   GameEntryPoint

TimingFail:
        ; Crash, reset, or display error
        RST  #08
        DB   #0A                    ; error code
```

### Cracking Speedlock

**Method 1: Snapshot at decryption completion**

1. Load the tape in ZEsarUX.
2. Open the debugger (F5).
3. Set a breakpoint on the `JP GameEntryPoint` instruction (the one after `DecryptDone`).
4. Let the tape load and decrypt. The breakpoint triggers.
5. Save the snapshot. The game code is now fully decrypted in RAM.

**Finding the JP address**: The Speedlock engine is typically at `#5E00` or `#8500`. Disassemble from there to find the `JP nn` at the end of the decryption phase. Look for the pattern: XOR loop → timing check → JP to game entry.

**Method 2: Patch the timing check**

If you cannot find the JP address, you can instead patch the timing check to always pass:

1. Disassemble the loader.
2. Find the `JR NZ, TimingFail` instruction after the timing check.
3. Change it to `JR DecryptDone` (or `NOP` it out).

```z80
; Original: JR NZ, TimingFail   = #20 nn
; Patched:  NOP + NOP           = #00 #00
; Or:       JR DecryptDone      = #18 nn (always pass)
```

**Method 3: Brute-force snapshot**

If all else fails, take snapshots at regular intervals during loading and diff them:

1. Set ZEsarUX to auto-snapshot every frame.
2. Load the tape.
3. After loading, examine the sequence of snapshots.
4. The snapshot where memory stabilizes (stops changing between frames) is the decrypted state.

---

## Alkatraz Deep-Dive

Alkatraz was a later, more aggressive protection system used primarily by Hewson Consultants. It combined turbo loading with self-decrypting code and stack-based integrity checks.

### Alkatraz Structure

| Feature | Implementation |
|---|---|
| Variable timing | Each data block uses slightly different pulse lengths |
| Self-decrypting code | Loaded code contains decryption stub that overwrites itself |
| Stack canary | Places known values on stack; checks them after loading |
| Multi-pass decryption | Code is encrypted in layers; each pass decrypts the next |

### Cracking Alkatraz

The self-decrypting nature of Alkatraz makes static analysis difficult — the code you see in the disassembly is encrypted, not the final code. The solution is dynamic:

1. Set a breakpoint at the **final transfer of control** — the `JP` or `RET` that jumps to the decrypted game entry point.
2. Let the entire loading and decryption sequence run.
3. The breakpoint triggers with all layers decrypted.
4. Save the snapshot.

The challenge: finding the final transfer point. Alkatraz uses multiple decryption passes, each ending with a jump to the next. The last jump goes to the game entry. Technique:

1. Set breakpoints on every `JP nn` instruction in the loader region.
2. The first few hits are intermediate decryption passes.
3. The last hit (after which memory stops changing) is the final transfer.

### Stack Canary Bypass

Alkatraz places canary values on the stack and checks them after loading. If a debugger or NMI tool pushed extra data, the canary check fails. To bypass:

1. Note the stack pointer value when the canary check runs.
2. Set a breakpoint at the canary comparison instruction.
3. When it triggers, modify the comparison result (set the Zero flag) to make the check pass.
4. Continue execution.

```z80
; Typical canary check:
        POP  DE              ; retrieve canary
        LD   HL, CanaryValue ; expected value
        AND  A               ; clear carry
        SBC  HL, DE          ; compare
        JR   NZ, CanaryFail  ; mismatch = debugger detected

; Bypass: set Z flag before the JR NZ
; In ZEsarUX debugger, press F to flip the Zero flag, then continue
```

---

## Disk Protection Bypass

TR-DOS-based disk protection schemes exploit the WD1793 FDC's low-level behavior. See [protection_techniques.md](protection_techniques.md) section 2 for the full catalog. Here is how to bypass each:

### Weak-Bit Protection

**How it works**: A track is written at a marginal flux level. Each read produces different bit patterns. The loader reads the track twice and compares — copies produce deterministic bits (always the same), so they match and the check fails.

**How to bypass**: Patch the comparison check. Find the `JR Z, Match` or `CP` instruction that compares the two reads, and force it to always report a match:

```z80
; Original: compare two reads
        LD   HL, ReadBuffer1
        LD   DE, ReadBuffer2
        LD   BC, 256
CompareLoop:
        LD   A, (DE)
        CPI                  ; compare (HL) with A, HL++, BC--
        JR   NZ, WeakBitOK   ; mismatch = original (weak bits differ)
        JP   PE, CompareLoop
        JR   WeakBitFail     ; all match = copy (deterministic)

; Patch: force mismatch path
; Change the JR NZ target or NOP the JR WeakBitFail
```

### Non-Standard Sector IDs

**How it works**: Sectors are numbered non-sequentially (e.g., `#01, #02, #80, #81` instead of `1, 2, 3, 4`). Standard copiers expect sequential numbering and cannot read the disk.

**How to bypass**: Patch the sector ID table in the loader to use standard sequential IDs, or patch the READ SECTOR call to accept the actual IDs. See [trdos_programming.md](../05_development/08_dos_tape/trdos_programming.md) for TR-DOS sector I/O.

---

## NMI Countermeasure Defeat

Copy-protected software developed techniques to detect and resist NMI-based hardware debugging. See [protection_techniques.md](protection_techniques.md) section 3 for the full catalog. Here is how to defeat each:

### R-Register Checking

**How it works**: The program reads the R (refresh) register at two points in a timing loop. If a debugger single-stepped between them, R will have advanced more than expected.

```z80
; R-register check
        DI
        LD   A, R            ; read R at point A
        LD   B, A            ; save
        LD   C, #FF          ; tight loop counter
TimingLoop:
        DEC  C
        JR   NZ, TimingLoop
        LD   A, R            ; read R at point B
        SUB  B               ; A = R advancement
        CP   #10             ; expected advancement (calibrated)
        JR   NC, DebuggerDetected  ; too much = single-stepping
```

**How to defeat**: Use a hardware debugger that preserves R exactly (like the Scorpion Shadow Monitor), or patch the comparison:

```z80
; Patch: change CP #10 to CP #FF (accept any R advancement)
; Original: FE 10    CP #10
; Patched:  FE FF    CP #FF
```

Or, more robustly, NOP out the entire check:

```z80
; NOP from the CP instruction through the JR NC
; Original: FE 10 30 nn
; Patched:  00 00 00 00
```

### Stack Canary Checking

**How it works**: The program places known values on the stack before protected code. If NMI fires, the Z80 pushes 2 bytes (return address) onto the stack, corrupting the canary.

**How to defeat**: This is the hardest countermeasure, because the 2 bytes pushed by NMI are permanently overwritten. Options:

1. **Use a hardware monitor with a shadow stack** (Scorpion Shadow Monitor) — it switches to its own stack immediately, never touching the user's SP.
2. **Patch the canary check** to always pass.
3. **Avoid NMI during protected sections** — use breakpoints (which do not push to the stack) instead of NMI.

### Timing-Window Checking

**How it works**: A tight raster loop is calibrated to frame timing. NMI injects 11+ T-states, causing a missed timing window. This is the one check that **cannot be fully defeated** — the Z80 NMI architecture guarantees minimum latency.

**Mitigation**: Minimize NMI usage during timing-critical sections. Use PC breakpoints instead. If you must debug timing-critical code, accept that the timing window will break and focus on understanding the code structure rather than running it in real-time.

---

## The Clean Snapshot Technique

The end goal of most cracking work is a **clean snapshot** — a .SNA or .Z80 file that contains the unprotected game code, loads directly in any emulator, and runs without the original protection. Here is the universal procedure:

### Step-by-Step: From Protected .TAP to Clean Snapshot

```
1. Load the protected .TAP in ZEsarUX
2. Open debugger, set breakpoint at the game entry point
   (disassemble loader to find the JP to game code)
3. Let the tape load completely
4. Breakpoint triggers — game code is decrypted in RAM
5. Note: the game's entry point address (PC)
6. Note: the stack pointer (SP) — should be in upper RAM
7. Check that RAM #8000-#FFFF contains valid code
8. Clear any protection variables:
   - Zero out timing check flags
   - Reset any "loader active" flags
9. Save as .SNA (48K) or .Z80 (128K)
10. Test: load the snapshot in a fresh ZEsarUX instance
11. If the game runs correctly, the snapshot is clean
```

### Common Issues with Clean Snapshots

| Problem | Cause | Fix |
|---|---|---|
| Game crashes immediately | PC not at real entry point | Find the actual JP target |
| Game runs but crashes after intro | Initialization code missed | Set earlier breakpoint |
| Game resets to BASIC | Protection check still active | Find and NOP the check |
| Graphics corrupted | Screen RAM not fully loaded | Let tape play a bit longer |
| 128K game loses sound | Wrong machine model | Save as 128K snapshot, not 48K |
| Game works in ZEsarUX but not Fuse | Snapshot format quirk | Try .Z80 format instead of .SNA |

---

## Decision Matrix: Which Cracking Approach?

| Your situation | Recommended approach |
|---|---|
| Speedlock-protected tape | Snapshot at decryption completion |
| Alkatraz-protected tape | Snapshot at final control transfer |
| Unknown custom loader | Auto-snapshot + memory diffing |
| Disk-based protection (weak bits) | Patch the comparison check |
| Anti-NMI protection (R check) | Patch the R comparison or use Scorpion Shadow Monitor |
| Anti-NMI protection (stack canary) | Use PC breakpoints, avoid NMI; or patch canary check |
| Timing-window protection | Accept limitation; use static analysis for timing-critical sections |
| Need to distribute clean copy | Produce clean snapshot after all protections defeated |
| Need to modify game code | Apply patches to clean snapshot, re-save |

---

## Cross-References

| Topic | Reference |
|---|---|
| Protection techniques catalog | [protection_techniques.md](protection_techniques.md) |
| RE methodology | [methodology.md](methodology.md) |
| Static/dynamic analysis tools | [analysis_techniques.md](analysis_techniques.md) |
| Game reversing case studies | [game_reversing.md](game_reversing.md) |
| Code compression and packers | [code_crunching.md](code_crunching.md) |
| Snapshot repair | [snapshot_repair.md](snapshot_repair.md) |
| TR-DOS file operations | [trdos_programming.md](../05_development/08_dos_tape/trdos_programming.md) |
| Tape format details | [tape_interface.md](../03_io/storage/tape_interface.md) |
| TZX format (turbo block timings) | [tzx_format.md](../03_io/storage/tzx_format.md) |
| Z80 NMI mechanics | [z80_interrupts.md](../01_cpu/z80_interrupts.md) |
| Scorpion Shadow Monitor | [scorpion.md](../02_hardware/clones/scorpion.md) |
| Debugging toolchain | [debugging.md](../09_toolchain/debugging.md) |

## References

### External references

- **Speedlock / Alkatraz / Power Load documentation** — community-maintained analyses of the three most widespread Western Spectrum protection schemes; Speedlock alone was used on over 300 commercial titles.
- **`zx-pk.ru` protection cracking forum** — primary Russian-language venue for documented analyses of Soviet-era custom loaders (Star Sky, 5B Group, Mafia Corporation); the source of most published decryption tables.
- **UnrealSpeccy / ZEsarUX source code** — emulator-side references for the exact timing / pulse patterns used by Speedlock and Laserload; emulators must reproduce these bit-for-bit to load protected images.
- **Magazine archives on `zxpress.ru`** — primary-source articles from *Spectrofon*, *ZX-Format*, *Adventurer*, and *ZX-Review* on disk protection schemes and the Russian custom-loader ecosystem.
- **Andrew Broad's *Speedlock Disassembly* (WoS archive)** — the canonical English-language worked example of cracking a Speedlock-protected title, originally distributed as a commented .z80 disassembly.
