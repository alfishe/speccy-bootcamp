[← Home](../README.md) · [Demoscene](README.md)

# The Compression Mindset — Writing Code for the Compressor, Not for the Assembler

> **Scope**: This article covers a specific, counter-intuitive discipline used by size-coders who ship a **compressed** binary (ZX0/ZX1/ZX2, see [compression_packing.md](compression_packing.md)): once a compressor sits between your source and the byte budget, "smallest instruction" and "smallest compressed output" stop being the same target, and the two can actively conflict. It is a companion to [size_coding.md](size_coding.md) §5 (squeeze tricks) and §8 (compressing the final binary), and to [compression_packing.md](compression_packing.md) §13 (in-place and backward depack).
>
> The observations here are attributed to ZX Spectrum size-coder **Maxim Muchkaev**, from a discussion of practical ZX2 budgeting (personal communication, 2026). They are a working practitioner's rule of thumb, not a formally benchmarked law — treat the byte counts as illustrative, and always re-measure on your own payload (§5 below).

---

## 1. The Core Idea: The Compressor Replaces the Optimizer

[§5 of size_coding.md](size_coding.md#5-squeeze-tricks) teaches the classic size-coding discipline: for every operation, find the Z80 encoding that costs the fewest raw bytes. `XOR A` instead of `LD A,0`. `OR B` instead of `LD A,B` / `CP 0`. This discipline assumes the **assembled binary is the final binary** — every byte you emit is a byte the party counts.

Once a compressor (ZX0, ZX1, ZX2 — see [compression_packing.md](compression_packing.md) §6) sits between the assembled binary and the shipped file, that assumption breaks. The compressor is not a passive pass-through that shrinks whatever you hand it by a fixed percentage; it is an **LZ-style matcher that rewards repeated byte sequences** and is largely indifferent to how "clever" or "dense" any individual instruction is in isolation. In this world, the compressor effectively takes over the job a translator or interpreter would do in a higher-level pipeline: you stop hand-picking the shortest opcode for a single site, and instead write in whatever form gives the matcher the most to work with. As the source insight puts it: *"компрессор заменяет тебе транслятор или интерпретатор"* — the compressor substitutes for a translator/interpreter; you no longer write `ADD A,4`, you write four `INC A`.

## 2. Worked Example: `ADD A,4` vs. Four `INC A`

Take the simple task of adding 4 to the accumulator.

**Squeeze-first instinct** (§5 doctrine — fewest raw bytes, uncompressed):
```z80
    ADD  A,4        ; #C6 04 — 2 bytes, 1 unique 2-byte sequence
```

**Compression-friendly form** (deliberately "worse" by squeeze rules):
```z80
    INC  A          ; #3C — 1 byte
    INC  A          ; #3C
    INC  A          ; #3C
    INC  A          ; #3C — 4 bytes total, but all 4 bytes are IDENTICAL
```

Raw, pre-compression, the `ADD A,4` form is smaller (2 bytes vs. 4). But an LZ-style compressor doesn't grade instructions — it grades **byte patterns**. A run of four identical `#3C` bytes is exactly the kind of redundancy ZX0/ZX1/ZX2 exist to exploit: if `#3C #3C #3C #3C` (or a suffix of it) has appeared anyweher earlier in the stream, the matcher can often represent the whole run as a short back-reference token, sometimes cheaper than the two-byte literal encoding `ADD A,4` would need if `#C6 04` does **not** recur anywhere else in the binary. A unique, "already optimal" 2-byte instruction that never repeats compresses to *itself plus overhead* (a literal token); a 4-byte run of a byte that repeats throughout the binary can compress to a fraction of a byte on average, amortized across the whole file.

The lesson generalizes: **before compression, `ADD A,4` is shorter. After compression, four `INC A` can be shorter** — not always, and not by a huge margin per site, but consistently enough that it changes how a size-coder should write arithmetic, loop bodies, and repeated setup code once compression is part of the pipeline.

## 3. Why Repetition Beats Density

This is the same principle [compression_packing.md](compression_packing.md) already documents for *data* (§ on screen-format-aware traversal: laying out bytes so that spatially related pixels become byte-adjacent, because adjacency is what an LZ matcher can exploit) — this article extends it to **code**:

- A compressor's window is bytes, not semantics. It cannot tell that `ADD A,4` and `INC A ×4` are logically equivalent; it can only tell that one produces a byte pattern it has seen before and one doesn't.
- Instruction *repetition* — the same opcode, or the same short opcode sequence, appearing many times across the binary — is compression fuel. Instruction *uniqueness* — a rare, maximally-encoded opcode that appears exactly once — is compression-inert; it must be stored as a literal.
- Single-byte, no-operand instructions (`INC r`, `DEC r`, `XOR A`, `RET`, the various one-byte ALU idioms in [size_coding.md §5.7](size_coding.md#57-the-self-clear-idiom)) are the richest source of this fuel: they are short enough, and common enough elsewhere in typical Z80 code, that expanding a single "clever" instruction into several of them often *increases* the match potential rather than diluting it.
- This effect compounds when the **same expansion pattern is reused at multiple call sites**. If ten different places in your intro need "add a small constant," writing all ten as chains of `INC A` gives the matcher ten near-identical opportunities; writing them as ten distinct `ADD A,n` immediates (different `n` each time) gives it ten unrelated 2-byte literals.

The practical corollary: **§5's squeeze table is not wrong, it is scoped to the uncompressed case.** [size_coding.md §8.1](size_coding.md#81-why-compress-last) already notes that "compressors work on bytes, not on logic" as a reason to squeeze *before* compressing — this article adds the sharper point that squeezing for raw byte count and squeezing for *post-compression* byte count are different, sometimes opposite, objectives, and only measurement (§5 below) tells you which one wins for a given payload.

## 4. The Corollary: Forward vs. Backward (Self-Destructing) Depack

The same conversation that produced the `INC A` example also gives a concrete illustration of budget arithmetic changing with the *decompression direction*: for one worked payload, a normal forward depacker left **200 ZX2-effective bytes** of budget, while switching to a **backward, self-destructing depack** (decompressing into the same buffer that held the compressed data, from the end backward — see [compression_packing.md §13](compression_packing.md#13-in-place-and-backwards-depack)) freed up **210 bytes** — a ~5% swing from a decompression-direction choice alone, with no change to the effect code itself.

This is consistent with the mechanism [compression_packing.md §13.2](compression_packing.md#132-backwards-depack) already documents: backward depack lets the compressed payload and the decompressed output **overlap in the same memory**, because the depacker only ever reads from addresses *below* its current write pointer. Forward, in-place depack needs a `delta` safety margin between the end of the compressed data and the end of the destination (§13.3 of that article) to avoid the depacker overwriting bytes it hasn't consumed yet; backward depack removes that margin requirement, and the reclaimed margin is exactly the kind of few-percent swing that decides whether a 256B or 512B intro fits.

The mindset is the same as §1–§3: the depacker's *direction* is another compressor-facing decision, not a purely mechanical one — it should be chosen by measuring the resulting total (depacker + payload + margin), not by default habit.

## 5. Measure, Don't Guess

Neither §2's `INC A` trick nor §4's backward-depack trick is free — both interact with the rest of the binary in ways that are hard to predict from first principles:

1. **The `INC A`-style expansion only wins if the expanded byte pattern is genuinely more common elsewhere in the binary than the dense form would have been.** In a very short, idiosyncratic 256B intro with little internal repetition, expanding every arithmetic op this way can make the *uncompressed* binary large enough that the compressor has more raw material but no more actual redundancy to find — a net loss. This is the same caution as [size_coding.md §8.5](size_coding.md#85-when-compression-hurts): already-dense, low-redundancy code does not compress well regardless of which dense-vs-verbose form produced it.
2. **Backward depack is not universally available.** Not every compressor ships a backward depacker (ZX0 and Exomizer do; check before assuming); where one exists, the savings must be weighed against needing to pack the source data backward on the PC side and against the destination address actually being the top of usable memory (§13.2's stated use case) rather than the bottom.
3. **The only reliable test is round-trip measurement**: assemble both variants (dense vs. expanded, or forward vs. backward depack), compress both with the actual target compressor, and compare the final `depacker + compressed payload` totals. §5.8 of [size_coding.md](size_coding.md#58-squeeze-workflow) already prescribes this iterate-and-measure loop for ordinary squeezing; the compression mindset simply moves the measurement to **after** compression instead of stopping at the assembled binary.

A workable extension of the size-coding workflow in [size_coding.md §4.4](size_coding.md#44-the-stages-of-a-size-coded-intro):

1. Prototype, squeeze, reuse, and generate tables as usual (§2–§7 there).
2. Assemble and compress once, as a baseline.
3. For the hottest few call sites (loop bodies, repeated setup, anything executed or emitted many times), try the "verbose but repetitive" alternative encoding and re-compress.
4. Keep whichever total is smaller, site by site — there is no global rule that one style always wins; the winner depends on what else is already in the binary.
5. If the target compressor supports it, try both forward and backward depack layouts and keep the smaller total (§4 above).

## 6. Cross-References

- [size_coding.md](size_coding.md) §5 (Squeeze Tricks) — the pre-compression discipline this article qualifies; §8.1 (Why Compress Last) — the ordering doctrine this article sharpens; §8.5 (When Compression Hurts) — the failure mode that also bounds this technique.
- [compression_packing.md](compression_packing.md) §6 (Generation 3 — ZX0/ZX1/ZX2) — the compressors this technique targets; §13 (In-Place and Backwards Depack) — the mechanism behind §4's budget swing.
- [effects_catalog.md](effects_catalog.md) — effects whose loop bodies are natural candidates for the repetition trick in §2–§3 (anything with a tight, many-times-executed inner loop).
- [README.md](README.md) — section index.

---

## License

This article is released under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you credit the original source and license derivative works under the same terms.

The central observations are credited to Maxim Muchkaev (personal communication, 2026); the surrounding explanation, worked example, and cross-references are original to this knowledge base.
