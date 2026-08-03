[← Home](../README.md) · [Operating Systems](README.md)

# The +2A / +3 ROM Internals

The original Sinclair 48K ROM was 16 KB. The 128K ROM was 32 KB. The **+2A / +3 ROM** — Amstrad's third-generation Spectrum ROM, shipped from December 1987 — was **64 KB**: a four-page ROM containing a 128K-compatible editor, an original 48K BASIC ROM, the +3 DOS disk operating system, and a patched 48K BASIC with disk extensions.

This ROM is the most complex piece of system software ever shipped in a Sinclair-branded Spectrum. It introduces a new paging port (`#1FFD`), four paging modes, a CP/M compatibility layer, and a substantially different memory model from any prior Spectrum. Understanding it is essential for anyone working with +2A or +3 hardware, writing emulator code, or trying to make 48K software run on a +3.

This article covers the +2A / +3 ROM at the technical level: its physical layout, its paging mechanism, the four paging modes, what each of the four ROM pages does, the bugs and quirks, and how it differs from the 128K ROM that preceded it. For the catalog of ROM versions and identification, see [rom_versions.md](rom_versions.md). For the +3 DOS disk operating system (one of the four pages), see [plus3dos.md](plus3dos.md).

---

## Roadmap

1. **What the +2A/+3 ROM is** — physical and logical overview
2. **Why Amstrad rewrote the ROM** — design goals, historical context
3. **The 64 KB physical ROM** — chip layout, address decoding
4. **The four ROM pages** — what each one does
5. **The paging mechanism** — ports `#7FFD` and `#1FFD` in detail
6. **The four paging modes** — the memory model complexity
7. **Page-by-page breakdown** — internals of each page
8. **Compatibility and quirks** — what works, what breaks
9. **Bugs and gotchas** — known issues with the ROM
10. **Cross-references** — where to go next

---

## §1. What the +2A / +3 ROM Is

### 1.1 Physical layout

The +2A and +3 contain a single **64 KB ROM chip** (or, in some hardware variants, two 32 KB chips) soldered to the motherboard. The chip holds four 16 KB "pages" of read-only memory:

```
Physical ROM chip (64 KB total):
+------------------------------------+
| Page 0: 16 KB                      |  Offset 0x0000 - 0x3FFF
|   128K editor + extensions         |
+------------------------------------+
| Page 1: 16 KB                      |  Offset 0x4000 - 0x7FFF
|   Original 48K BASIC ROM           |
+------------------------------------+
| Page 2: 16 KB                      |  Offset 0x8000 - 0xBFFF
|   +3 DOS                           |
+------------------------------------+
| Page 3: 16 KB                      |  Offset 0xC000 - 0xFFFF
|   Patched 48K BASIC with disk exts |
+------------------------------------+
```

These four pages occupy the same logical address range (`#0000`–`#3FFF`) in the Z80's address space at different times, depending on the state of the paging ports.

### 1.2 Logical vs physical addresses

It is critical to understand the difference between **physical ROM addresses** (offsets within the 64 KB chip) and **logical addresses** (the Z80's view of memory at any given moment):

- The 64 KB ROM chip has physical offsets `0x0000`–`0xFFFF`.
- The Z80 sees only 16 KB at a time at logical addresses `#0000`–`#3FFF`.
- A "page" is a 16 KB slice of the physical ROM that can be switched into the logical `#0000`–`#3FFF` window.

When software writes a value to port `#1FFD` to select "Page 2", the hardware physically reconnects the address lines so that logical address `#0000` now reads from physical offset `0x8000` (the start of Page 2). The other 48 KB of logical address space (`#4000`–`#FFFF`) is unaffected.

This is bank switching — the same basic mechanism used by the 128K ROM, just with more pages and an additional control port.

### 1.3 Why four pages?

The +2A / +3 ROM is four pages because it has to provide:

1. **Backwards compatibility with 128K software** — needs the 128K editor (Page 0).
2. **Backwards compatibility with 48K software** — needs the original 48K BASIC ROM (Page 1).
3. **Disk access** — needs the +3 DOS ROM (Page 2), which is itself a substantial 16 KB operating system.
4. **48K BASIC with disk commands** — needs a slightly patched 48K ROM that activates the `LOAD "a:..."` syntax (Page 3).

Pages 1 and 3 are similar but not identical: Page 1 is the pristine original 48K BASIC, used for maximum 48K compatibility; Page 3 is a modified version that supports +3 DOS keywords.

The Amstrad engineers could have merged Pages 1 and 3, but chose not to — both for safety (preserving an unmodified 48K ROM for compatibility) and because the patch was simpler to implement as a separate ROM.

### 1.4 Versions

The +2A / +3 ROM has been issued in two main variants:

| Variant | Year | Notable change |
|---|---|---|
| Original | 1987 | First release with the +3 |
| Spanish | 1988 | Spanish-language prompts |
| +3E (community) | 1999+ | Garry Lancaster's open upgrade with hard disk support |

The "original" ROM is what's in every stock +2A and +3. The +3E is a modern community-developed upgrade that adds IDE hard disk support, fixed bugs, and other improvements. See [rom_versions.md](rom_versions.md) §7.4 for details.

---

## §2. Why Amstrad Rewrote the ROM

### 2.1 Historical context

When Amstrad purchased the Sinclair computer range in 1986, they inherited:

- The 48K Spectrum (with the 1982 16 KB ROM).
- The 128K Spectrum ("toastrack", with the 1986 32 KB ROM).
- The QL (with its own ROM — Amstrad discontinued this).
- The ZX Interface 1, Interface 2, Microdrives, and various peripherals.

Amstrad immediately moved to consolidate the product line. The +2 (April 1987) was essentially a 128K in a CPC-style case with a built-in datacorder — same 32 KB ROM as the 128K. The +3 (December 1987) added a floppy disk drive and required a more sophisticated ROM to support it.

### 2.2 Design goals

Amstrad's design goals for the +2A / +3 ROM, in approximate priority:

1. **Full backward compatibility.** Software that ran on the 48K or 128K Spectrums must run unchanged on the +2A / +3. This meant keeping the original 48K BASIC ROM available (Page 1) and the 128K editor available (Page 0).
2. **Built-in disk support.** The +3's floppy drive had to be accessible from BASIC without additional software. This required extending BASIC with disk keywords (`CAT`, `LOAD "a:..."`, etc.) and including a disk operating system ROM (+3 DOS, Page 2).
3. **CP/M compatibility.** Amstrad had a long history with CP/M (the CPC and PCW both ran it). The +3 should be able to boot CP/M 2.2 to give access to the business software library.
4. **RAM disk support.** To keep cassette-era software usable, the +2A / +3 should support a RAM disk mode where banked RAM acts as a virtual disk.
5. **Minimal hardware changes.** The +2A / +3 motherboard should be a modest evolution of the 128K / +2 design, not a complete redesign.

The four-page ROM, the second paging port, and the four paging modes are all consequences of these goals.

### 2.3 What changed from the 128K ROM

Compared to the 128K ROM, the +2A / +3 ROM adds:

- **Two more ROM pages** (Page 2 = +3 DOS, Page 3 = patched 48K with disk extensions).
- **A new paging port** (`#1FFD`) that selects the page and the paging mode.
- **Four paging modes** (vs. the 128K's single mode).
- **CP/M boot support** (the boot menu has a CP/M option).
- **Disk-specific BASIC keywords** (`CAT`, `FORMAT`, `MOVE`, `ERASE`, `COPY`).
- **Disk-aware `LOAD`/`SAVE`** (with `a:` and `m:` drive prefixes).

The +2A / +3 ROM is essentially the 128K ROM **with disk support bolted on**. The 128K editor is preserved in Page 0; the original 48K BASIC is preserved in Page 1. What's new is the disk infrastructure (Pages 2 and 3) and the more flexible paging.

### 2.4 What did not change

Things that the +2A / +3 ROM **kept the same** as the 128K:

- The BASIC interpreter's core (the floating-point library, the calculator stack, the tokenizer, the program editor).
- The AY-3-8910 sound chip driver.
- The keyboard matrix layout (mostly — the +2A / +3 has a different physical keyboard but produces the same keystrokes).
- The 128K's `#7FFD` paging port (still present, still works the same way).
- The 128K's "Tape" and "48 BASIC" boot menu options.

A 128K Spectrum program that does not use disk I/O will run identically on a +2A / +3.

### 2.5 Why not just use the 128K ROM + an external DOS ROM?

A reasonable question: why didn't Amstrad just ship the +3 with the 128K ROM and put +3 DOS on an external cartridge (like the original Interface 1 with the microdrive ROM)?

The answer is partly historical (Amstrad's design philosophy favored integrated solutions) and partly technical:

- **Cartridge ROMs** were available on the Spectrum's rear expansion port, but they required careful timing with the banked 128K ROM and could conflict with each other.
- **An integrated +3 DOS** is faster (always available, no bank switching to invoke) and simpler for users (no external hardware required).
- **CP/M boot** requires a tight integration between the boot ROM and the disk driver; this is much easier if both are in the same physical chip.

The four-page integrated ROM was the cleanest solution, even though it required the new paging port and the more complex memory model.

---
## §3. The 64 KB Physical ROM

### 3.1 Chip variants

The +2A and +3 were manufactured over several years (1987–1990) and used different physical ROM chip configurations:

- **Original +3 (December 1987)**: A single 64 KB ROM chip (often a 27C512 EPROM or mask ROM).
- **Later +3 and +2A**: Sometimes two 32 KB ROM chips (often 27C256 EPROMs) for ease of manufacture.
- **+2A (1988+)**: Single 64 KB ROM, identical to the +3 ROM.

From the software's perspective, all variants are identical — they all present a 64 KB address space divided into four 16 KB pages. The chip variant matters only for hardware repair and ROM dumping.

### 3.2 Address decoding

The +2A / +3 motherboard has a custom gate array (the "Amstrad gate array" or "40084" chip) that handles:

- Decoding the Z80's address bus.
- Selecting between RAM banks and ROM pages.
- Implementing the paging ports (`#7FFD` and `#1FFD`).
- Controlling the floppy disk controller and its DMA-style interface.

When the Z80 reads from address `#0000`–`#3FFF` with MREQ asserted, the gate array determines which ROM page to expose based on:

- The current value of port `#1FFD` bits 0–1 (selects the ROM page).
- The current value of port `#7FFD` bit 4 (controls special paging modes).
- The DISRom signal (set when an external ROM is in use, e.g., from a cartridge).

This is more complex than the 128K's paging (which only had one port and one page select bit), but the principle is the same.

### 3.3 ROM access timing

ROM access on the +2A / +3 is the same as RAM access: the gate array decodes the address and returns the byte at the corresponding physical ROM offset. There is no contended-RAM timing issue for ROM reads (unlike the 128K's contended-RAM banks 4–7).

The ROM is always available — it does not need to be "enabled" in any sense other than the appropriate page being selected. This is important for interrupt handling: the Z80's mode 1 interrupt vector is at `#0038`, which is always in the currently-selected ROM page.

### 3.4 Reading the ROM from software

Software that wants to inspect the ROM can read it like any other memory:

```z80
LD   A,(#0000)              ; Read first byte of currently-selected ROM page
LD   A,(#1FFE)              ; Read the magic byte that identifies the ROM
```

To read a different ROM page, software must:

1. Disable interrupts (DI).
2. Write the appropriate value to port `#1FFD` to select the page.
3. Read the desired bytes.
4. Restore the original paging.
5. Re-enable interrupts (EI).

This pattern is fragile because interrupt handlers can run between DI and EI; if an interrupt occurs during the paging window, the interrupt handler will execute from the wrong ROM page. The DI/EI pair prevents this.

---

## §4. The Four ROM Pages

### 4.1 Page 0: The 128K editor + extensions

Page 0 is the +2A / +3's "default" page — it is what is banked in when the machine boots and when the user is in 128 BASIC mode. It contains:

- The full-screen editor (similar to the 128K's bank 1, with minor enhancements).
- The boot menu (Tape / RS232 / 48 BASIC / 128 BASIC / +3 DOS / CP/M).
- The keyboard matrix decoder.
- The display driver (text rendering, attribute handling).
- The AY-3-8910 music chip driver.
- The RS232 driver.
- The RAM disk driver (for the M: and N: drives).
- The extensions to support the +3's disk-aware keywords (when invoked, these extensions call into +3 DOS in Page 2).

Page 0 is essentially the 128K ROM's bank 1 with additions for disk awareness. From the user's perspective, it's "the 128K editor with extra disk stuff".

### 4.2 Page 1: The original 48K BASIC ROM

Page 1 is the **original Sinclair 48K BASIC ROM**, byte-for-byte identical (or nearly so) to the Issue 2 or Issue 3 ROM that shipped in the original 48K Spectrums. This page is used when:

- The user selects "48 BASIC" from the boot menu.
- Software explicitly switches to 48K mode via port `#7FFD`.

Page 1's role is **backward compatibility**. Software that was written for the 48K Spectrum and that hardcodes ROM routines (e.g., `CALL #0D4B` for the keyboard scanner) will work on the +2A / +3 because Page 1 has the original 48K ROM at the expected addresses.

Page 1 is *almost* byte-identical to the original Sinclair 48K ROM. A small number of patches were applied to make it work correctly in the banked environment (e.g., the keyboard scanner must be aware that the top 16 KB of RAM can be different banks). But the vast majority of the ROM is unchanged.

### 4.3 Page 2: +3 DOS

Page 2 is the **+3 DOS ROM** — Amstrad's CP/M-derived disk operating system. This is invoked when:

- The user does anything disk-related from BASIC (`CAT`, `LOAD "a:..."`, etc.).
- The user selects "+3 DOS" or "CP/M" from the boot menu.
- Software explicitly banks in Page 2 to access +3 DOS routines.

Page 2 contains:

- The +3 DOS file system driver (CP/M-style directory and allocation).
- The floppy disk driver (for the +3's built-in 3-inch drive).
- The +3 DOS RSX (Resident System Extension) mechanism, which extends BASIC.
- The CP/M boot loader.
- Disk utility routines (format, copy, verify).

Page 2 is itself a substantial piece of software — roughly 16 KB of dense code, comparable in size to the entire 48K BASIC ROM. It is covered in detail in [plus3dos.md](plus3dos.md).

### 4.4 Page 3: Patched 48K BASIC with disk extensions

Page 3 is a **modified version of the 48K BASIC ROM** (Page 1) with patches to enable disk-aware keywords. The differences from Page 1:

- The `LOAD` and `SAVE` keyword handlers are extended to recognize the `a:` and `m:` drive prefixes.
- The `CAT`, `FORMAT`, `ERASE`, `MOVE`, `COPY` keywords (which exist as tokens in the original 48K ROM but do nothing) are connected to +3 DOS routines.
- A few internal routines are patched to call into +3 DOS when disk operations are requested.

Page 3 is used when the user is running in "48 BASIC" mode but wants disk access. It is essentially the "best of both worlds" page: 48K compatibility plus disk support.

Most users do not explicitly select Page 3 — the +3 DOS ROM does it transparently when needed. But software that needs to manipulate the paging directly can bank in Page 3 to get disk-aware 48K BASIC.

### 4.5 Why three pages of "BASIC"?

The reason the +2A / +3 ROM has three pages of BASIC (Pages 0, 1, and 3) is historical:

- **Page 0** is needed for 128 BASIC mode (with the new editor and PLAY keyword).
- **Page 1** is needed for maximum 48K compatibility (where software expects the pristine 48K ROM at specific addresses).
- **Page 3** is needed for 48 BASIC mode with disk access.

Pages 1 and 3 are similar enough that they could in principle be merged, but the Amstrad engineers chose to keep them separate for safety. The cost of this redundancy is 16 KB of ROM — which in 1987 was a non-trivial expense, but Amstrad evidently decided that the compatibility benefit was worth it.

---

## §5. The Paging Mechanism

The +2A / +3 has two paging ports: `#7FFD` (inherited from the 128K) and `#1FFD` (new to the +2A / +3). Together, these ports control which ROM page and which RAM banks are visible.

### 5.1 Port `#7FFD` (the 128K paging port)

This port was introduced on the 128K Spectrum and is preserved on the +2A / +3. Its bit layout:

| Bit | Function |
|---|---|
| 0–2 | Selects which 16 KB RAM bank is visible at `#C000`–`#FFFF` (banks 0–7) |
| 3 | Selects the visible screen (bank 5 = normal, bank 7 = shadow) |
| 4 | Selects which ROM is visible at `#0000`–`#3FFF` (0 = "normal" ROM, 1 = "special" ROM) |
| 5 | Disable paging (write 1 to lock further writes to this port) |
| 6–7 | Unused |

On the 128K, bit 4 selects between the two ROM banks (bank 0 = 48K BASIC, bank 1 = 128K editor). On the +2A / +3, bit 4 has a more nuanced meaning that depends on the current value of port `#1FFD`.

### 5.2 Port `#1FFD` (the +2A / +3 paging port)

This port is **new to the +2A / +3**. Its bit layout:

| Bit | Function |
|---|---|
| 0–1 | Selects the paging mode (0–3) |
| 2 | Disable the +3's disk motor (or in some clones, used for other purposes) |
| 3 | Selects between disk and tape on some hardware configurations |
| 4 | Selects the active disk drive (A or B) |
| 5–7 | Unused |

The most important bits are 0–1, which select the paging mode. See §6 for details.

### 5.3 The paging port interaction

The two ports interact in non-obvious ways. The full state of memory mapping on a +2A / +3 depends on:

- The current value of port `#1FFD` bits 0–1 (the paging mode).
- The current value of port `#7FFD` bit 4 (which ROM page is selected in some modes).
- The current value of port `#7FFD` bits 0–2 (which RAM bank is at `#C000`).

The result is a memory model that is dramatically more complex than the 128K's. Software that assumes the 128K's simpler model can break on the +2A / +3.

### 5.4 The paging port write protocol

To change the memory mapping on a +2A / +3, software writes a byte to port `#7FFD` or `#1FFD`:

```z80
LD   BC,#7FFD              ; the 128K paging port
LD   A,#18                 ; bit 4 = 1 (special ROM), bits 0-2 = 0 (bank 0)
OUT  (C),A                 ; remap memory
```

After this OUT, the memory layout changes immediately. Code execution continues from the new memory layout — which can be a problem if the code that issued the OUT is now in different memory. The standard pattern is to issue the OUT from a known location (typically a routine in RAM at `#5C00` or similar) that is unaffected by the paging.

### 5.5 Locking the paging port

Port `#7FFD` bit 5 is a "lock" bit. Once set to 1, no further writes to port `#7FFD` have any effect until the machine is reset. This is used by software that wants to prevent the paging from being changed (e.g., a game that needs a specific memory layout).

Port `#1FFD` does not have a lock bit. To prevent changes to `#1FFD`, software typically just remembers not to write to it.

### 5.6 Detecting the +2A / +3 from software

Software that wants to know whether it's running on a 128K or a +2A / +3 can:

1. Try to write to port `#1FFD`. On a 128K / +2 (grey), this port does not exist — writes go nowhere. On a +2A / +3, the write succeeds.
2. Read back port `#1FFD` (or its effects on memory) to confirm.

A common detection routine:

```z80
LD   BC,#1FFD
LD   A,#04                 ; try to set "RAM disk mode"
OUT  (C),A
IN   A,(C)                 ; try to read back
CP   #04                   ; did the write stick?
JR   Z,is_plus3
; otherwise, this is a 128K or +2 (grey)
```

This is not perfectly reliable (some clones emulate the +2A / +3 paging without being one), but it works for distinguishing the main Sinclair/Amstrad models.

---
## §6. The Four Paging Modes

Port `#1FFD` bits 0–1 select one of four paging modes. Each mode presents a different memory layout. This is the single most important (and most complex) feature of the +2A / +3 ROM.

### 6.1 Mode 0: 128K compatibility mode

`#1FFD` bits 0–1 = `00` — **Mode 0** is the default mode and the most backward-compatible. The memory layout in this mode is:

| Address range | Content |
|---|---|
| `#0000`–`#3FFF` | ROM page (selected by `#7FFD` bit 4: 0 = Page 0/1, 1 = Page 2/3) |
| `#4000`–`#7FFF` | RAM bank 5 (always) |
| `#8000`–`#BFFF` | RAM bank 2 (always) |
| `#C000`–`#FFFF` | RAM bank selected by `#7FFD` bits 0–2 (banks 0–7) |

This is **the same memory model as the 128K Spectrum**. Software written for the 128K runs in this mode without modification.

In Mode 0, port `#7FFD` bit 4 selects between "Page 0" (or Page 1, depending on which "default" ROM is configured) and "Page 2" (or Page 3). Specifically:

- Bit 4 = 0: ROM page 0 (128K editor) or ROM page 1 (48K BASIC), depending on a secondary state.
- Bit 4 = 1: ROM page 2 (+3 DOS) or ROM page 3 (patched 48K), depending on a secondary state.

The "secondary state" is determined by other bits in port `#1FFD`. Most software doesn't need to worry about this — the +3 DOS ROM handles the page selection automatically.

### 6.2 Mode 1: Special paging mode

`#1FFD` bits 0–1 = `01` — **Mode 1** is a "special" mode that exposes RAM banks 0–3 at the lower address ranges. The memory layout:

| Address range | Content |
|---|---|
| `#0000`–`#3FFF` | RAM bank 0 |
| `#4000`–`#7FFF` | RAM bank 1 |
| `#8000`–`#BFFF` | RAM bank 2 |
| `#C000`–`#FFFF` | RAM bank 3 |

In this mode, **all of the lower 64 KB is RAM** — no ROM is visible. The machine is essentially a CP/M-compatible flat-memory machine. This is used for:

- Running CP/M (which expects a flat 64 KB address space).
- Running machine-code programs that need to read from addresses that the ROM normally occupies (e.g., to disassemble the ROM).
- Certain types of copy protection that expect RAM at low addresses.

Mode 1 is the most "non-Spectrum" of the four modes. When in this mode, BASIC cannot run (because the ROM is not visible). Software in this mode is typically self-contained machine code that has been loaded into RAM.

### 6.3 Mode 2: RAM disk mode

`#1FFD` bits 0–1 = `10` — **Mode 2** is a "RAM disk" mode that exposes RAM banks 4, 5, 6, 7 at the lower address ranges. The memory layout:

| Address range | Content |
|---|---|
| `#0000`–`#3FFF` | RAM bank 4 |
| `#4000`–`#7FFF` | RAM bank 5 |
| `#8000`–`#BFFF` | RAM bank 6 |
| `#C000`–`#FFFF` | RAM bank 7 |

In this mode, **all of the lower 64 KB is RAM**, but it's the *upper* four banks (4, 5, 6, 7) rather than the *lower* four (0, 1, 2, 3).

Mode 2 is used for:

- The +3's RAM disk M: and N: drives (which are stored in RAM banks 4–7).
- Self-contained machine-code programs that want maximum RAM without ROM overhead.

Like Mode 1, Mode 2 cannot run BASIC (the ROM is not visible). The difference is which four RAM banks are exposed.

### 6.4 Mode 3: Plus 3 mode

`#1FFD` bits 0–1 = `11` — **Mode 3** is similar to Mode 0 (the 128K compatibility mode), with subtle differences in how the ROM pages are selected. It is rarely used directly by software; it exists primarily for compatibility with software that expects a specific paging behavior.

### 6.5 Comparison of the four modes

| Mode | Bits 0-1 of `#1FFD` | Memory layout | Typical use |
|---|---|---|---|
| 0 | 00 | 128K-like (ROM at bottom, RAM banks at top) | Default; 128K software |
| 1 | 01 | All RAM, banks 0-3 | CP/M; some special software |
| 2 | 10 | All RAM, banks 4-7 | RAM disk; some special software |
| 3 | 11 | Similar to Mode 0 with different ROM paging | Compatibility |

Mode 0 is by far the most common. Most +2A / +3 software runs in Mode 0. Modes 1 and 2 are used by specialized software (CP/M, RAM-disk-intensive programs).

### 6.6 Mode switching

Software can switch modes at any time by writing to port `#1FFD`. The transition is instantaneous — the memory layout changes immediately, and code execution continues from the new layout.

The standard pattern for switching modes:

```z80
DI                        ; disable interrupts
LD   BC,#1FFD             ; paging port
LD   A,#XX                ; desired mode + other bits
OUT  (C),A                ; switch mode
; ... do stuff in the new mode ...
LD   A,#00                ; back to mode 0
OUT  (C),A
EI                        ; re-enable interrupts
```

The DI/EI pair is critical because interrupt handlers (which run every 20 ms during VBLANK) would otherwise execute from the wrong memory layout.

---

## §7. Page-by-Page Breakdown

### 7.1 Page 0 internal structure

Page 0 (the 128K editor + extensions) is internally structured like the 128K ROM's bank 1:

| Address range | Content |
|---|---|
| `#0000`–`#0FFF` | Reset vector, RST handlers, NMI handler |
| `#1000`–`#1FFF` | Boot menu, keyboard scanner |
| `#2000`–`#2FFF` | Editor (full-screen), display routines |
| `#3000`–`#3BFF` | AY-3-8910 driver, RS232 driver, RAM disk driver |
| `#3C00`–`#3FFF` | Disk extension hooks, configuration data |

Page 0 is the most "user-visible" page — it's what runs when the user is interacting with the BASIC editor in 128 mode.

### 7.2 Page 1 internal structure

Page 1 (the original 48K BASIC ROM) is internally identical to the Sinclair 48K ROM. See [rom_48k.md](rom_48k.md) for the detailed structure. In brief:

| Address range | Content |
|---|---|
| `#0000`–`#0FFF` | Reset, RST handlers, NMI, error handlers |
| `#1000`–`#1FFF` | Keyboard scanner, display routines |
| `#2000`–`#2FFF` | Editor, calculator stack, floating-point library |
| `#3000`–`#3BFF` | BASIC interpreter, tape routines |
| `#3C00`–`#3FFF` | Character set (font), sprites for UDGs |

### 7.3 Page 2 internal structure

Page 2 (+3 DOS) is itself a substantial 16 KB operating system. See [plus3dos.md](plus3dos.md) for the detailed structure. In brief:

| Address range | Content |
|---|---|
| `#0000`–`#0FFF` | +3 DOS entry points, boot code |
| `#1000`–`#1FFF` | File system driver (CP/M-style) |
| `#2000`–`#2FFF` | Floppy disk driver (UPD765 FDC) |
| `#3000`–`#3BFF` | RSX mechanism, DOS utilities |
| `#3C00`–`#3FFF` | Disk parameter tables, error messages |

### 7.4 Page 3 internal structure

Page 3 (patched 48K BASIC with disk extensions) is mostly identical to Page 1, with patches at specific locations. The patches:

- Modify the `LOAD` keyword handler to recognize the `a:`, `b:`, `m:`, `n:` drive prefixes.
- Modify the `SAVE` keyword handler similarly.
- Connect the `CAT`, `FORMAT`, `ERASE`, `MOVE`, `COPY` keywords (which exist as tokens in Page 1 but do nothing) to the corresponding +3 DOS routines in Page 2.
- Add a small amount of glue code that performs the page switch to Page 2 when a disk operation is invoked.

The total size of the patches is a few hundred bytes. The bulk of Page 3 is identical to Page 1.

### 7.5 How the pages interact

The four pages are not independent — they call into each other. The typical flow for a disk operation:

1. User types `LOAD "a:myfile"` in the BASIC editor (Page 0).
2. Page 0's `LOAD` handler recognizes the `a:` prefix and calls into Page 3's patched `LOAD` handler.
3. Page 3's patched `LOAD` handler calls into Page 2's +3 DOS file routines.
4. Page 2's file routines read the disk and return the loaded data to Page 3.
5. Page 3 returns to Page 0, which continues the BASIC program.

Each of these calls requires a page switch (write to `#1FFD` or `#7FFD`). The transitions are managed carefully to ensure that the return address (on the Z80 stack) is always in a valid memory location.

### 7.6 How CP/M interacts

When the user selects "CP/M" from the boot menu:

1. Page 0 loads the CP/M image (typically from a file named `cpm` on the +3 disk) into RAM.
2. Page 0 sets up the +3's CP/M BIOS routines.
3. Page 0 switches the machine to Mode 1 (all-RAM mode with banks 0–3 at low addresses).
4. Page 0 jumps to the CP/M entry point in RAM.

Once CP/M is running, the +2A / +3 ROM is **not visible** — the entire 64 KB address space is RAM, as CP/M expects. The ROM is banked back in only when the machine is reset or when CP/M makes a specific BIOS call that requires it.

This is the cleanest way to make a Spectrum run CP/M: hide the ROM entirely and present a flat 64 KB RAM space, which is what CP/M was designed for.

---
## §8. Compatibility and Quirks

The +2A / +3 ROM is designed to be backward-compatible with software written for the 48K and 128K Spectrums. In practice, most software works, but there are gotchas.

### 8.1 48K compatibility

Software written for the 48K Spectrum runs on the +2A / +3 in two ways:

1. **From the boot menu, select "48 BASIC"** — this runs Page 1 (the original 48K BASIC ROM) and switches the machine into a 48K-compatible memory layout. The +3 essentially becomes a 48K Spectrum.
2. **From 128 BASIC, type `SPECTRUM` or `USING 48`** — same effect, but invoked from within 128 mode.

Most 48K software works correctly under this mode. Compatibility issues arise with software that:

- **Hardcodes timing-critical machine code** that depends on the 48K's exact contended-RAM timing. The +2A / +3 has slightly different timing from the original 48K, and software that uses tight timing loops (e.g., loading screens with custom tape loaders) may break.
- **Reads the ROM at specific addresses**. Page 1 of the +2A / +3 ROM is *almost* identical to the original 48K ROM, but a few bytes are different. Software that does byte-for-byte ROM checksums will fail.
- **Assumes the absence of the second paging port**. Software that writes to port `#1FFD` (intending to write to some other device) will accidentally change the +2A / +3's memory layout.
- **Uses the parallel port or other hardware** that differs between the 48K and the +2A / +3.

These compatibility issues are well-known and have workarounds. The +3 community has produced lists of incompatible software and patches for the most popular titles.

### 8.2 128K compatibility

Software written for the 128K Spectrum runs on the +2A / +3 in Mode 0 (the default mode), which is essentially identical to the 128K's memory model. Compatibility is very high — most 128K software works without modification.

The main issues are similar to the 48K case: timing-sensitive software, software that reads the ROM at specific addresses, and software that does unexpected things with the paging ports.

### 8.3 The shadow screen

The 128K Spectrum introduced the concept of a **shadow screen** — a second display buffer in RAM bank 7 that can be used for double-buffering. The +2A / +3 preserves this functionality.

Software that uses the shadow screen (e.g., fast-action games that render to bank 7 then swap it to bank 5 at VBLANK) works correctly on the +2A / +3.

### 8.4 Disk-aware BASIC from 48K mode

In Page 1 (48K BASIC), the disk keywords `CAT`, `FORMAT`, `LOAD "a:..."` etc. do **not** work — they are stubs in the 48K ROM that just produce an error. To get disk support in 48K mode, you need Page 3 (the patched 48K BASIC).

The +2A / +3 ROM handles this automatically when running in 128 mode: it banks in Page 3 when disk operations are needed and banks in Page 1 when not. But software that explicitly switches to Page 1 (e.g., for maximum compatibility) loses disk access.

### 8.5 CP/M compatibility quirks

When CP/M is running on the +2A / +3:

- The CP/M "TPA" (Transient Program Area) is about 56 KB — slightly less than the 60 KB available on dedicated CP/M machines like the Amstrad CPC.
- The CP/M BIOS must be specifically written for the +2A / +3 hardware (it differs from the CPC's BIOS).
- The +3's 3-inch disk format is supported; 3.5" or 5.25" formats require additional hardware.

Most CP/M software written for the Amstrad CPC, PCW, or other Z80 CP/M machines can be made to run on the +2A / +3 with minor adjustments. See [cpm.md](cpm.md) §6 for details.

### 8.6 The "tape to disk" workflow

A common task on a +3 is converting cassette-era software to disk. The standard workflow is:

1. Boot the +3 in 128 BASIC mode.
2. `LOAD ""` from tape — loads the original cassette-based program into RAM.
3. `SAVE "a:converted"` — saves the loaded program to the +3's disk.

This works for most 48K-era software that uses standard tape formats. For software with non-standard loaders (custom turbo loaders, copy-protected loaders), the conversion is more complex and may require machine-code intervention.

---

## §9. Bugs and Gotchas

The +2A / +3 ROM is generally well-designed but has several known bugs and quirks.

### 9.1 The `RANDOMIZE USR 0` crash

On a 48K Spectrum, `RANDOMIZE USR 0` jumps to address `#0000`, which is the start of the ROM — the machine resets. On the +2A / +3, this can have different effects depending on the current paging mode, and may crash rather than reset cleanly. Software that uses this as a "reset" trick may not work as expected.

The fix is to use a proper reset mechanism (e.g., the reset button on the +3 case, or `OUT (C), 0` to a specific port that triggers reset).

### 9.2 The `INKEY$` keyboard timing

The +2A / +3's keyboard scanner is slightly slower than the 48K's, because it has to handle the more complex memory layout. Software that uses tight `INKEY$` loops for input may miss keystrokes on the +2A / +3 that work on the 48K.

The fix is to insert a small delay in the input loop, or to use the proper `INKEY$` keyword (which is interrupt-driven and handles the timing correctly).

### 9.3 The disk "no disk in drive" error

If the +3 is asked to access the disk drive with no disk inserted, it returns an error. The exact error code depends on the operation and the disk format. Some software does not handle these errors gracefully and may hang or crash.

The fix is to always insert a disk before invoking disk operations, or to add proper error handling.

### 9.4 The 64 KB ROM banking gotcha

Software that does direct memory paging (writing to ports `#7FFD` and `#1FFD`) without following the documented protocols can leave the machine in an inconsistent state. For example, if software writes to `#1FFD` to switch to Mode 1 (all-RAM) without first preparing the RAM banks, the machine may crash when the next interrupt fires.

The fix is to always follow the documented mode-switching protocol: disable interrupts, set up the desired state, re-enable interrupts.

### 9.5 The Spanish +3 ROM

The Spanish +3 ROM has the same bugs as the UK +3 ROM, plus a few Spanish-specific issues (e.g., the Ñ character sometimes displays incorrectly in certain fonts). These are minor and rarely affect software behavior.

### 9.6 Compatibility with +2 (grey) software

Software written for the +2 (grey) — which has the 128K ROM, not the +2A / +3 ROM — generally works on the +2A / +3. Compatibility issues arise with software that:

- Uses the +2's specific tape-loading timing (the +2A / +3 has slightly different tape timing).
- Reads the ROM at specific addresses and expects the 128K ROM, not the +2A / +3 ROM.
- Writes to port `#1FFD` for some other purpose (which is interpreted as a +2A / +3 paging command).

### 9.7 The `+3` keyword issue

The +2A / +3 ROM adds a few new tokens (`FORMAT`, `MOVE`, etc.) that did not exist as active keywords in the 48K or 128K ROMs. Software that uses these tokens for other purposes (e.g., as UDG characters) may have unexpected behavior on the +2A / +3.

### 9.8 The +3E ROM fixes

The community-developed +3E ROM (see [rom_versions.md](rom_versions.md) §7.4) fixes many of these bugs. It is the recommended ROM for serious +3 users in 2024. The +3E is a drop-in replacement for the original +3 ROM and preserves backward compatibility while fixing bugs and adding new features (notably IDE hard disk support).

---

## §10. Cross-References

- **[rom_versions.md](rom_versions.md)** — The catalog of all Spectrum ROM versions, including the +2A / +3. This article covers the technical internals; the catalog article covers identification and history.
- **[plus3dos.md](plus3dos.md)** — The +3 DOS disk operating system, which is Page 2 of the +2A / +3 ROM. Detailed coverage of the disk file system, FDC driver, and RSX mechanism.
- **[cpm.md](cpm.md)** — CP/M 2.2 on the Spectrum, which runs on the +2A / +3 in Mode 1 (all-RAM mode). Covers the CP/M boot process, BIOS, and software library.
- **[basic_dialects.md](basic_dialects.md)** — The dialect of BASIC implemented by the +2A / +3 ROM. Includes the disk-aware keywords (`CAT`, `LOAD "a:..."`, etc.).
- **[rom_48k.md](rom_48k.md)** — The 48K ROM internals. The +2A / +3's Page 1 is essentially the Sinclair 48K ROM; this article covers its internals in detail.
- **[rom_128k.md](rom_128k.md)** — The 128K ROM internals. The +2A / +3's Page 0 is essentially the 128K ROM's bank 1 with extensions.
- **[../05_development/03_memory_and_io/memory_and_io_plus3.md](../05_development/03_memory_and_io/memory_and_io_plus3.md)** — The +3's memory and I/O model from the development section. Detailed programming reference.
- **[../02_hardware/original/README.md](../02_hardware/original/README.md)** — Original Sinclair hardware. The +3 is the last machine in this lineage.
- **[esxdos.md](esxdos.md)** — A modern alternative to the +3 DOS. ESXDOS provides similar functionality but for the DivIDE/DivMMC ecosystem rather than the +3's built-in floppy.

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same license.
