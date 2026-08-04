[← Home](../../README.md) · [Display & Timing](README.md)

# +2A / +3 Video Frame — Amstrad Gate Array Timing

The ZX Spectrum +2A and +3 replace the Ferranti ULA with an **Amstrad gate array**. While the frame structure is similar to the 128K, the contention model is completely different. Code that relies on exact Ferranti ULA contention timing will break on these machines.

---

## Frame Parameters

```
┌──────────────────────────────────────────────────┐
│  ZX Spectrum +2A / +3 — Frame Parameters         │
│                                                  │
│  T-states per frame:     70,908                  │
│  T-states per scanline:  228                     │
│  Total scanlines:        311                     │
│  Frame rate:             ~50.02 Hz               │
│                                                  │
│  Top border:             63 lines   (14,364 T)   │
│  Paper area:             192 lines  (43,776 T)   │
│  Bottom border:          56 lines   (12,768 T)   │
│  VBlank:                 included in border      │
│                                                  │
│  Contention:             Banks 4, 5, 6, 7        │
│  Contention type:        Amstrad gate array      │
│  Pattern:                1-0-7-6-5-4-3-2         │
│  I/O contended:          NO (MREQ only)          │
│                                                  │
│  INT position:           T=0, scanline 0         │
│  INT duration:           36 T-states             │
│  Early/late timing:      NOT present             │
└──────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> The frame T-state count (70,908) and scanline count (311) are the **same** as the 128K/+2. However, the **contention pattern and contended banks are different**.

---

## Amstrad Gate Array vs Ferranti ULA

### Contention Pattern Comparison

```
Ferranti ULA (48K, 128K, +2):
T-state offset:  0  1  2  3  4  5  6  7
Contention delay: 6  5  4  3  2  1  0  0
                 ↑↑                    ↑↑
            Peak delay            No delay

Amstrad gate array (+2A, +3):
T-state offset:  0  1  2  3  4  5  6  7
Contention delay: 1  0  7  6  5  4  3  2
                 ↑     ↑↑
              Minimal  Peak delay (7T!)
```

Key differences:

1. **Peak delay is 7T, not 6T** — the Amstrad gate array can stall the CPU for one additional T-state compared to the Ferranti ULA
2. **Peak is at offset 2, not offset 0** — the entire pattern is shifted and inverted
3. **Minimum delay at offset 0 is 1T** — even at the start of the window, there's a 1T delay (vs 6T on Ferranti)

### Contended Banks

| Model | Contended banks |
|-------|----------------|
| 128K / +2 | Banks **1, 3, 5, 7** (odd banks / DRAM set B) |
| +2A / +3 | Banks **4, 5, 6, 7** (high banks) |

This is a significant difference. On the 128K, bank 0 is uncontended. On the +2A/+3, **bank 4 and 6 are contended** even though they were safe on the 128K.

### I/O Contention

| Model | I/O contention | Root cause |
|-------|---------------|------------|
| Ferranti ULA | **Yes** — any port with A0=0 is contended during paper | ULA cannot distinguish memory vs I/O bus cycles |
| Amstrad gate array | **No** — only `MREQ` (memory) is contended | Gate array keys off `MREQ` line; I/O accesses activate `IORQ` instead |

This means `OUT (#FE),A` (border color), `OUT (#7FFD),A` (paging), and `OUT (#BFFD),A` (AY) all run at the **same speed during paper as during border** on +2A/+3. On the Ferranti ULA (48K/128K/+2), each of these pays up to 6T of contention delay per call during the paper area. This asymmetry is the most common cause of multicolor border effects running too fast when ported from +2A/+3 back to earlier machines — pad with NOPs to compensate.

For the full per-T-state delay tables (both Ferranti and Amstrad), see [contention_timing.md](contention_timing.md).

---

## Scanline Map

| Scanline | T-state start | Region | Content | Contention |
|----------|--------------|--------|---------|------------|
| 0 | 0 | Top border | Border | None |
| 1–62 | 228–14,363 | Top border | Border | None |
| 63 | 14,364 | Paper start | First display line | **Active** |
| 63–254 | 14,364–58,139 | Paper area | 192 display lines | **Active** |
| 255 | 58,140 | Bottom border | Border | None |
| 255–310 | 58,140–70,907 | Bottom border + VBlank | Border | None |
| → 0 | 70,908 | Next frame | INT fires | — |

### Paper Area Timing

```
Per scanline during paper (228T total):
  48T left border (no pixel fetch, contention may start)
  128T pixel + attribute fetch (contention window)
  52T right border + blanking (no contention)
```

---

## Impact on Existing Code

### What Breaks

1. **Cycle-exact multicolor effects** — The different contention pattern (1-0-7-6-5-4-3-2 vs 6-5-4-3-2-1-0-0) means T-state budgets calculated for the 48K/128K are wrong. Effects appear shifted or misaligned.

2. **Floating bus raster sync** — The gate array's floating bus behavior is unreliable. Many T-states return `#FF` instead of pixel/attribute data. Code that uses `IN A,(#FF)` for raster position detection will not work.

3. **Contention-based timing tricks** — Any code that uses the exact Ferranti contention delay as part of its timing (e.g., relying on 6T worst-case delay) will have different timing on the +2A/+3.

4. **Bank-sensitive code** — Code that puts timing-critical data in "uncontended" bank 4 or 6 (safe on 128K/+2) will be contended on the +2A/+3.

### What Still Works

1. **HALT-based synchronization** — `HALT` works the same way. The INT fires at T=0 of the frame. Frame-locked code (effects that update once per frame) is unaffected.

2. **Code in uncontended banks** — Banks 0, 1, 2, 3 are uncontended on the +2A/+3. Place timing-critical code there.

3. **Attribute and pixel writes** — The screen is at the same address (`#4000`–`#5AFF`). Writes work the same; only timing is different.

4. **Border effects** — Since I/O is not contended, `OUT (#FE),A` timing is predictable. This makes border effects **easier** to code on the +2A/+3 than on the 48K/128K.

### Porting Checklist

```
48K/128K → +2A/+3 porting:
  [ ] Replace floating bus sync with HALT + delay
  [ ] Recalculate T-state budgets for contention pattern 1-0-7-6-5-4-3-2
  [ ] Move timing-critical code from banks 4/6 to banks 0-3
  [ ] Verify multicolor effects align correctly
  [ ] Test border effects (may be easier due to no I/O contention)
  [ ] Check #1FFD paging (4 modes available)
```

---

## The #1FFD Port and Paging Modes

The +2A/+3 adds port `#1FFD` which, combined with `#7FFD`, provides four paging modes:

| Mode | #1FFD bit 2 | Description |
|------|-------------|-------------|
| 0 | 0 | **Compatible mode** — same as 128K/+2 |
| 1 | 1 | **Special mode** — all 4 slots remappable |
| 2 | 1 | **RAM disk mode** — special configurations |
| 3 | 1 | **ROM paging mode** — 4 ROM pages accessible |

In compatible mode (0), all 128K software should work (with the contention differences noted above). Special mode allows mapping any RAM bank to any 16K slot — enabling true double buffering where the shadow screen is accessible at `#4000` while the main screen is displayed.

See [bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md) for code patterns.

---

## Cross-References

- **128K video frame** (Ferranti ULA timing): [video_frame_128k.md](video_frame_128k.md)
- **48K video frame** (base reference): [video_frame_48k.md](video_frame_48k.md)
- **ULA timing** (contention patterns, gate array details): [ula_timing.md](../../02_hardware/original/ula_timing.md)
- **Contention model** (per-model comparison): [contention_model.md](../03_memory_and_io/contention_model.md)
- **Bank switching** (+2A/+3 special modes): [bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md)
- **Floating bus** (why it's unreliable on +2A/+3): [floating_bus.md](floating_bus.md)

## References

### External references

- [Amstrad +2A / +3 Service Manual](https://www.worldofspectrum.org/hardware.html) — the canonical hardware reference for the +2A/+3's gate array (the "AMSTRAD 40040" or "40058" ASIC); documents the modified contention scanline range and the absence of floating-bus reads.
- [Chris Smith — The ZX Spectrum ULA](http://www.zxdesign.info/) — while the book focuses on the Ferranti ULA, it also documents the gate array evolution in the 128K lineage and explains why the +2A/+3 breaks compatibility with 48K timing-sensitive code.
- [Sinclair ZX Specifications](http://problemkaputt.de/zxdocs.htm) — the cross-model hardware reference covering the +2A/+3's paging port (`#1FFD`, the special MMU modes), the contention scanline range (64–255 vs the 128K's 64–191), and the 4-bank ROM layout.
- [Spectrumpedia](https://speccy.wiki/) — cross-model print reference for the +2A/+3's special modes (ROM 0/1/2/3 selection, special RAM config, all-RAM mode for development).
- [SpecEmu / ZEsarUX source code](https://sourceforge.net/projects/specemu/) — emulator references for the +2A/+3's exact scanline timing and the differences from the earlier +2 (grey) Z70830 mainboard.
