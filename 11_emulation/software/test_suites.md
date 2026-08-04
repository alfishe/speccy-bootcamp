[← Home](../../README.md) · [Software Emulators](README.md)

# Test Suites — Validating ZX Spectrum Emulator Accuracy

A **test suite** is a piece of software designed to verify that an emulator (or real hardware) behaves correctly. For ZX Spectrum emulators, test suites check three main things:

1. **Z80 CPU correctness** — every documented and undocumented instruction, every flag, every register combination
2. **Memory and timing behavior** — contended memory timing, ULA video timing, interrupt timing
3. **Peripherals** — AY-3-8912 sound chip, Kempston joystick, Interface 1 microdrives, etc.

A modern emulator that passes all the major test suites will run essentially all original Spectrum software correctly. Conversely, an emulator that fails tests will produce visible glitches on specific software — particularly demoscene productions, which often rely on precise hardware behavior.

This article covers the **major test suites** used by the Spectrum emulator community, what they test, how they're used, and the limitations of testing. For the broader context of why accuracy matters and the technical challenges of cycle-exact emulation, see [cycle_exact_accuracy.md](cycle_exact_accuracy.md). For which emulators pass which tests, see [emulator_comparison.md](emulator_comparison.md).

---

## Why Test Suites Matter

### The Complexity of Correct Emulation

A working Z80 emulator that handles the documented instruction set is straightforward — the Z80 has roughly 700 documented opcodes, and a basic interpreter can be written in a few hundred lines of code. But producing an emulator that runs *every Spectrum program* correctly is much harder:

- **Undocumented instructions** — the Z80 has dozens of undocumented opcodes (e.g., `SLI`, `SLL`, the half-carry flag behavior on `BIT n, (HL)`). Real Spectrum software uses them, particularly games from Eastern Europe.
- **Undocumented flags** — the YF and XF flags (bits 5 and 3 of F) are set in undocumented ways by various instructions; some software inspects them.
- **Memory access timing** — the ULA slows CPU access to contended memory (the upper 16K of RAM on 48K machines) at specific times in the video frame. Getting this wrong causes subtle graphics corruption.
- **Interrupt timing** — the Z80's interrupt response time depends on what the CPU is doing when the interrupt is asserted; the ULA's INT signal must be modeled cycle-accurately.
- **Peripheral interactions** — the AY-3-8912 has precise read/write timing; the Kempston joystick has a specific read latency; etc.

For each of these, an emulator can be "wrong" in subtle ways that don't show up in casual testing but do break specific software. Test suites exist to catch these errors systematically.

### The Validation Workflow

Emulator authors use test suites in two main ways:

1. **Regression testing** — running the test suites after every change to the emulator, to catch newly-introduced bugs. Many emulators have automated test harnesses that run the full test suite and report any regressions.
2. **Targeted validation** — when adding support for a new piece of hardware (e.g., a new Russian clone), the author runs the relevant test suites to confirm the new hardware is correctly modeled.

Real hardware is also tested with these suites — the same test program that fails on emulator X may also fail (or behave subtlyly differently) on a real Pentagon vs a real 48K Spectrum. The test suites thus serve a dual purpose: validating emulators *and* documenting hardware behavior.

---

## The Major Test Suites

### ZEXALL and ZEXDOC — The Z80 Instruction Exercisers

The most famous Z80 test programs are **ZEXALL** and **ZEXDOC**, written by **Frank D. Cringle** in 1997 for the **YZ80** CP/M emulator. These programs exhaustively test the Z80 instruction set:

- **ZEXDOC** tests the documented behavior of every instruction — every register combination, every flag, every addressing mode
- **ZEXALL** extends ZEXDOC to test the undocumented instructions (the ones that real Z80s execute but Zilog didn't document)

Each test program loads test patterns into registers and memory, executes an instruction, and checks the result against an internal table of expected results. Failures are reported as a list of discrepancies. A typical ZEXALL run takes 5–10 minutes on a real Z80 (or emulated equivalent).

The ZEXALL/ZEXDOC test programs were originally written for CP/M but have been adapted for many platforms including the ZX Spectrum. The Spectrum versions are typically loaded as a `.tap` or `.sna` file and produce a textual report on the Spectrum screen.

**What they catch**:

- Incorrect opcode decoding (e.g., treating `CB 30` as a different instruction)
- Wrong flag behavior (the Z80 has subtle flag-setting rules that are easy to get wrong)
- Wrong undocumented instruction behavior
- Wrong register pair behavior (e.g., `LD (HL), r` not properly handling the `(HL)` addressing mode)

**What they don't catch**:

- Timing errors (ZEXALL doesn't measure cycle counts)
- Memory access pattern errors
- Interrupt handling
- Peripheral behavior

For these reasons, ZEXALL is necessary but not sufficient — emulators that pass ZEXALL can still have serious timing bugs that break specific software.

### The FUSE Test Suite

The **FUSE test suite** is a collection of test programs developed alongside the **Fuse emulator** (see [fuse.md](fuse.md)) by Philip Kendall and contributors. It's hosted on the Fuse project's source repository and is used by Fuse developers for regression testing.

The FUSE test suite includes:

- **Z80 instruction tests** — similar to ZEXALL but more focused on Spectrum-specific edge cases
- **Contended memory timing tests** — verify that the ULA's contention pattern is correctly modeled
- **Interrupt timing tests** — verify INT signal timing and response
- **Video timing tests** — verify that the ULA generates the correct video signal
- **Audio tests** — verify AY-3-8912 register behavior and timing
- **Peripheral tests** — Kempston, Interface 1, microdrive, etc.

The FUSE test suite is the standard reference for Spectrum emulator authors. Many other emulators (ZEsarUX, CSpect) run the FUSE suite as part of their own validation.

---


### The Pentagon Diag ROM

For Russian-clone emulation, the **Pentagon Diag ROM** is a key test. This is a custom ROM image that runs at power-on and performs a series of diagnostic checks specific to the Pentagon architecture:

- RAM banking (Pentagon has different banking from standard 128K Spectrums)
- Video timing (Pentagon's 320×200 mode with non-standard timing)
- Keyboard scan
- Disk interface (Beta 128)
- Sound (AY-3-8912 on different port addresses than Sinclair)

Emulators targeting the Pentagon must pass this diagnostic to be considered accurate. The Diag ROM is often distributed with Pentagon ROM sets and is the standard "smoke test" for new Pentagon emulators.

### Timing-Specific Tests

Several test programs focus specifically on **cycle-exact timing behavior**:

#### Sensible Software Tests

- **"Sensible" tests** — a series of small programs written by **Andrew Owen** that demonstrate specific timing-sensitive effects (ULA Plus palette switching, multicolor effects, raster interrupts). Emulators that get the timing wrong produce visible glitches on these tests.
- **"Float Spell"** — a popular multicolor test/demo that requires cycle-accurate ULA timing
- **"Sixteen colors" / "128-color" demos** — push the limits of the Spectrum's color capabilities, requiring cycle-accurate contention modeling

#### Contended Memory Tests

The classic contended memory test:

```z80
LD HL, 0x4000      ; start of contended memory
LD B, 0            ; counter
loop:
INC HL             ; access contended memory
DJNZ loop          ; repeat
```

On a real 48K Spectrum, the loop runs slower than expected because the ULA delays contended memory accesses during the active video portion of the frame. An emulator that doesn't model this contention will report a different cycle count.

#### INT Timing Tests

The ULA asserts INT (the Z80's maskable interrupt) for 32 T-states at the start of each vertical blank. Emulators must:

- Assert INT at the correct cycle
- Hold INT for exactly 32 T-states
- Deassert INT cleanly

Test programs measure the precise cycle counts around `HALT` instructions and interrupt response.

### Peripheral Tests

#### AY-3-8912 Tests

The AY-3-8912 sound chip has its own subtle behaviors that test programs verify:

- **Register write order** — writing to the AY involves a 2-step process (register select, then data); the timing matters
- **Envelope generator behavior** — the AY's envelope generator has specific reset conditions
- **Noise generator** — pseudo-random sequence that must match real hardware

Test programs produce known audio patterns that can be compared against the output of a real AY chip.

#### Kempston Joystick Tests

The Kempston joystick interface is read at I/O address `#1F`. Test programs verify:

- The joystick bits are correctly mapped (bit 0 = right, bit 1 = left, etc.)
- Reading from `#1F` doesn't affect other hardware
- Multiple simultaneous directions are correctly reported

#### Interface 1 / Microdrive Tests

The Interface 1's microdrive system has notoriously complex timing. Test programs verify:

- Microdrive cartridge read/write
- RS-232 port behavior
- ZX Net network primitives

These tests are particularly important for emulators claiming Interface 1 support — getting microdrive timing right is difficult.

### Diagnostic ROMs

Several **diagnostic ROMs** exist that run at power-on (replacing the Spectrum ROM) and produce a screen report of hardware status. These are commonly used by Spectrum repair technicians but are equally useful for emulator validation:

- **ZX Diag** — comprehensive hardware diagnostic with on-screen reports
- **Burnt ROM diagnostics** — various community-developed diagnostic programs
- **Ramtest** — memory test ROMs

These are particularly useful for catching subtle memory banking bugs.

---

## How to Use the Test Suites

### For Emulator Users

If you're choosing an emulator or evaluating its accuracy:

1. **Download the test suites** — ZEXALL, ZEXDOC, the FUSE test suite, and the relevant clone diagnostic ROMs (e.g., Pentagon Diag if you care about Pentagon emulation)
2. **Run each test in the emulator** — most tests are distributed as `.tap`, `.tzx`, or `.sna` files that load and run like any Spectrum program
3. **Compare output to known-good results** — most test suites document what a passing result looks like; many emulator authors publish their test results
4. **Test the specific behavior you care about** — if you're developing for a 128K +2A, run the tests on a +2A emulated configuration, not the default 48K

### For Emulator Authors

If you're writing or maintaining an emulator:

1. **Run the test suites as part of your CI pipeline** — automate test execution so every code change is validated
2. **Test on multiple hardware configurations** — 16K, 48K, 128K, +2, +2A, +3, Pentagon, Scorpion, etc. — each has different timing
3. **Compare results against real hardware** — when in doubt, run the same test on a real Spectrum and compare. Video output can be compared frame-by-frame.
4. **Publish your test results** — this helps users understand which emulators handle which tests correctly

### The Limitations of Testing

Test suites are essential but have limits:

- **They test what's known** — a test suite only catches bugs that its authors anticipated. New edge cases are regularly discovered by demoscene productions.
- **They don't model hardware variability** — real Z80s from different manufacturers (Zilog, SGS, Russian clones) have subtle differences. A test that passes on one real Spectrum might fail on another.
- **They can be wrong** — test suite authors occasionally make mistakes. A "failing" test might indicate a bug in the test rather than the emulator.
- **They don't cover everything** — some hardware behaviors (CRT screen phosphor decay, RF interference, power supply sag) are not testable in software.

For these reasons, even emulators that pass all known test suites should be considered "asymptotically correct" rather than perfect. Real hardware remains the ultimate reference for any specific software behavior.

---


## FAQ

**Q: My emulator passes ZEXALL — am I done?**

A: No. ZEXALL only tests Z80 instruction correctness — it says nothing about timing, interrupts, peripherals, or ULA behavior. An emulator that passes ZEXALL but has timing bugs will still fail on most demoscene productions.

**Q: Where can I download the test suites?**

A: The **FUSE test suite** is hosted on the Fuse project's SourceForge repository. **ZEXALL** and **ZEXDOC** are widely available on Spectrum archive sites (World of Spectrum, zxaaa.net, etc.) as `.tap` files. The Pentagon Diag ROM is distributed with Pentagon ROM sets on Russian Spectrum archives.

**Q: How do I know what a "pass" looks like?**

A: Most test suites include documentation describing expected output. For ZEXALL, a passing run reports "Z80 CCP/M exerciser stopped" with no error counts. For the FUSE test suite, each test has a documented expected output that emulator authors compare against.

**Q: Can I write my own test suite?**

A: Yes — and the community welcomes new test programs. If you discover a hardware behavior that no existing test covers (e.g., a subtle interaction between two peripherals), write a small test program and contribute it. The FUSE test suite accepts community submissions via the project's source repository.

**Q: Do real Spectrums pass all the tests?**

A: Almost all — but with **hardware-specific variations**. A real 48K issue 2 Spectrum behaves subtly differently from an issue 6A, and both differ from a Pentagon or Russian clone. Some tests deliberately document these variations (e.g., the contended memory pattern differs between Sinclair and Russian hardware). Emulators that aim to model a specific hardware variant must pass the tests for that variant.

**Q: What's the hardest behavior to test?**

A: **Audio timing**. The AY-3-8912 produces continuous analog output, and verifying that an emulator's audio exactly matches a real chip's output requires capturing audio from real hardware and comparing sample-by-sample. Test programs exist that produce specific audio patterns, but full verification is labor-intensive.

**Q: Why does my emulator fail the contended memory test only on specific cycles?**

A: Contended memory timing has several subtleties — different memory banks have different contention patterns, contention starts and stops at specific cycles in the video frame, and the contention delay itself depends on what the ULA is doing. A bug in any of these details will cause failures on specific cycle counts but not others. Debugging typically requires comparing the emulator's cycle-by-cycle behavior against a known-good implementation.

---

## Summary

Test suites are the cornerstone of Spectrum emulator validation. Without them, emulator development would be ad-hoc and unreliable — authors would test the software they happen to have and miss the edge cases that break specific programs. With them, emulator authors can systematically verify that their work matches real hardware behavior.

The standard test suite stack includes:

- **ZEXALL / ZEXDOC** for Z80 instruction correctness
- **The FUSE test suite** for comprehensive Spectrum-specific behavior
- **Pentagon Diag ROM** for Russian clone emulation
- Various timing-specific tests for contended memory, interrupts, and video

Modern emulators like **Fuse**, **ZEsarUX**, and **CSpect** all run these suites as part of their development process, and passing them is the baseline for being considered a serious emulator. The remaining gaps — undocumented clone quirks, audio waveform precision, analog hardware behavior — are gradually being closed by ongoing community research.

For users, the test suites provide a way to evaluate emulator claims. An emulator that says it "supports the Pentagon" should pass the Pentagon Diag ROM; an emulator that claims "100% compatibility with original software" should pass ZEXALL and the FUSE suite. If it doesn't, the claims are overstated.

---

## References

### Primary Sources

- **Frank D. Cringle's ZEXALL/ZEXDOC** — original source and documentation, available from various CP/M archives
- **The FUSE test suite** — hosted at the Fuse project's source repository on SourceForge
- **Pentagon Diag ROM** — distributed with Pentagon ROM images on Russian Spectrum archive sites
- **ZX Diag** — community diagnostic ROM, various versions circulating in the Spectrum community

### Emulator Documentation

- **Fuse release notes** — document which tests pass in each version
- [ZEsarUX documentation](https://github.com/chernandezba/zesarux) — describes the test results for various clone emulations
- **CSpect release notes** — describes test results for ZX Spectrum Next emulation

### Community Resources

- [World of Spectrum forums](https://worldofspectrum.org/) — discussions of test suite results for various emulators
- **ZX Spectrum Discord / Telegram groups** — community knowledge about specific test failures and their causes
- [comp.sys.sinclair](https://groups.google.com/g/comp.sys.sinclair) Usenet archives — historical discussions of test suite development (1990s–2000s)

### Cross-References

- [Emulator Comparison](emulator_comparison.md) — which emulators pass which tests
- [Cycle-Exact Accuracy](cycle_exact_accuracy.md) — the technical challenges test suites try to catch
- [[Fuse](fuse.md) — the reference emulator](https://fuse-emulator.sourceforge.net/) and test suite source
- [[ZEsarUX](https://github.com/chernandezba/zesarux)](zesarux.md) — broadest test coverage for clones
- [CSpect](cspect.md) — Next-specific test programs
