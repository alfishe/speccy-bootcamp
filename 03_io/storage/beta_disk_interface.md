# Beta Disk Interface

**Scope:** Hardware and host-glue aspects of the Beta Disk Interface — the address decoder, port map, TR-DOS ROM bank switching, drive/motor/side control, cable, variants, and common issues. The floppy controller chip itself (WD1793 / KR1818VG93) is covered in the sibling article [fdc_vg93.md](fdc_vg93.md); the TR-DOS logical disk format (directory, file types, disk parameters) is covered in [trd_disk_format.md](trd_disk_format.md).

**Audience:** Emulator authors, hardware reverse-engineers, modern Spectrum-clone designers, and demoscene coders who need to know exactly how the original 1985 Beta Disk Interface exposed the WD1793 to the Z80 — what ports to hit, in what order, with what side effects.

**Prerequisites:** A working knowledge of the Z80 CPU and a basic familiarity with floppy drive signals (step / dir / motor / index). It is strongly recommended to read [fdc_vg93.md](fdc_vg93.md) first or in parallel, because most of the Beta Disk Interface's host-visible behaviour is a thin wrapper around the FDC's register file.

**Depth:** Deep. Pin-level and byte-level detail, including the exact port addresses, the address decoder that produces them, the WAIT-state logic used to slow down the Z80's I/O cycles, and the Soviet clones that introduced subtle incompatibilities.

---

## Roadmap

| Section | Topic | Length |
|---|---|---|
| §1 | What the Beta Disk Interface Is — history, UK pricing, ex-USSR replication | long |
| §2 | Hardware Block Diagram — the chips and their connections | medium |
| §3 | Port Map — the 4 I/O ports and how they are decoded | medium |
| §4 | TR-DOS ROM Bank Switching — how the disk ROM takes over the Z80 | medium |
| §5 | Drive Select, Motor, and Side Control — what each port bit does | medium |
| §6 | Cable Pinout and Drive Compatibility — Shugart 34-pin, drives A–D | medium |
| §7 | Variants — Beta 48, Beta 128, Soviet clones, Pentagon integration | medium |
| §8 | Common Issues and Maintenance — what fails and how to fix it | short |
| §9 | Modern Replacements — onboard FDC on ZX Evo / ZX Next / clones | short |
| §10 | Cross-references — related articles and external references | short |

Reading order: §1 → §2 → §3 (the core) → §4 → §5 → §6, with §7–§9 as reference material.

---

## §1. What the Beta Disk Interface Is — History, Pricing, and the ex-USSR Replication

### 1.1 A short history

The Beta Disk Interface was released in 1985 by **Technology Research Ltd (Technology Research UK / TR Ltd.)**, a small British company founded by Andrew Owen. It was the first affordable **true floppy-disk** storage system for the ZX Spectrum — a distinction it holds over Sinclair's earlier **ZX Interface 1 + Microdrive** (1983), which was a tape-loop stringy-floppy rather than a real disk. The Beta Disk Interface predated Sinclair's first true floppy machine, the +3 with its internal 3" drive, by two years.

The interface shipped with two products:

- **The hardware**: a black plastic cartridge-style module that plugs onto the rear edge connector of the Spectrum (16/48 / 48+ / 128 / +2 / +3 — mechanically compatible with all Toastrack/Amstrad-era machines through adapter cables). It exposes a single **Shugart 34-pin** floppy connector and supports up to four drives (A, B, C, D).
- **The software**: a 16 KB **TR-DOS ROM** (versions 5.0, 5.1, 5.2, 5.3, 5.4 — the canonical version is 5.03 / 5.04) that occupies memory at `#3D00–#3FFF` (when paged in) and adds BASIC keywords (`CAT`, `LOAD`, `SAVE`, `MERGE`, `ERASE`, `FORMAT`, `COPY`, `MOVE`) plus a `*` command-line interface for disk operations.

The original 1985 hardware used a Western Digital **WD1793** floppy controller (single-sided, single-density). The revised **Beta 128** model (1986) used double-density-capable WD2793 or the Soviet KR1818VG93 clone; the host interface is identical in all cases. The Beta 128 is the canonical model that dominated ex-USSR computing.

### 1.2 UK launch pricing and competitive landscape

Contemporary UK retail prices for the Beta Disk Interface and its direct competitors:

| Product | Year | Price | Storage type |
|---|---|---|---|
| ZX Interface 1 + Microdrive + 4 carts (bundle) | 1983 | £99.95 | Tape-loop ("stringy floppy") |
| Opus Discovery, single 3" drive | 1984 | £199.95 | True floppy, 178 KB/disk |
| Opus Discovery, dual drive | 1984 | £329.95 | True floppy |
| **Beta Disk Interface** (interface only) | 1985 | **£109.25** | True floppy |
| **Beta Disk Interface + one drive** | 1985 | **£249.75** | True floppy |
| **Beta 128** (revised interface) | 1986 | comparable | True floppy |
| Sinclair +3 (whole computer, drive included) | 1987 | £199.99 | True floppy, 178 KB/disk |

The Beta Disk Interface sat between the cheap-but-limited Microdrive bundle and the more expensive Opus Discovery. Its UK market position was ultimately eroded by the +3 (1987), which included a drive in the base machine for less than the cost of a Beta Disk + standalone drive. In the West, the Beta Disk Interface was a niche product by 1988.

### 1.3 Why it mattered: the ex-USSR replication

In 1985, the Spectrum's only storage was cassette tape. Loading a 48 KB program from tape took 3–5 minutes (more for protected loaders); loading the same program from a TR-DOS floppy took 1–3 seconds. In the West, that speed-up was a convenience; in the Soviet bloc, it became the foundation of an entire software market that lasted until the early 2000s.

The Beta Disk Interface's UK commercial life was short. After 1987, the +3 (with its integrated drive and +3DOS) and cheaper tape-based loaders eroded its Western market share. The opposite happened in the USSR and Eastern Bloc: the Beta Disk Interface (and its locally-made clones) became the **de facto** disk standard, and TR-DOS remained the dominant disk operating system for the Spectrum until the platform's commercial death.

#### 1.3.1 The replication timeline

The Beta 128's migration into Soviet computing followed a four-year chain of reverse-engineering and cloning:

| Year | Event |
|---|---|
| **1986** | Beta 128 released in UK by Technology Research Ltd. |
| **1987** | Beta 128 imported to USSR at approximately £70 per unit — cheap enough to enter the country in quantity. The 128K Spectrum's ULA is "completely cracked" the same year, enabling local 128K clones. |
| **mid-1988** | Circuit diagram of the Beta 128 is reverse-engineered, adapted to Soviet-made logic ICs, and **published**. The **KR1818VG93** (Soviet clone of WD1793) becomes the standard FDC chip. The design is now free to copy. |
| **1989** | **Pentagon 48K** released in Moscow — the first Soviet clone with a Beta 128 controller **built into the motherboard** rather than as a separate cartridge. Named "Pentagon" after the pentagonal ground-plane layout of its PCB. |
| **1990** | **Pentagon 128K** (with AY sound and ZX-Lprint printer interface added). |
| **1991–1996** | Pentagon PCB is "copied all over the ex-USSR". Mass production runs through state electronics plants, frequently assembled after-hours on programmable soldering stations. |
| **1992** | Approximately 3 million Spectrum users in the ex-USSR (per Pentagon FAQ). **Scorpion ZS-256** (Sergey Zonov, St. Petersburg) launches as a high-end, also Beta-compatible, alternative. |

#### 1.3.2 Why Beta Disk locked in (three reinforcing reasons)

Three factors compounded to make Beta 128 effectively unchallengeable in the ex-USSR market:

1. **It was cracked first.** The Beta 128 circuit was reverse-engineered and publicized in mid-1988, before any competing Western disk interface reached the Soviet Union. Once the schematic and the KR1818VG93 chip were in the wild, copying was free — state fabs stamped the FDC by the thousand, and any competing interface would have had to overcome Beta 128's head start.

2. **TR-DOS lived in EPROM.** Because the OS was burned into a 16 KB ROM, not loaded from disk, every clone "just worked" with the same DOS — no driver fragmentation, no chicken-and-egg boot problem, no version skew. A user could swap disks between a Pentagon, a Scorpion, and a Profi without thinking about it.

3. **Pentagon integrated it onboard.** By soldering the Beta 128 controller directly onto the motherboard (rather than as a separate cartridge), the Pentagon made every Pentagon machine a Beta Disk machine by default. The Pentagon was the cheapest and most-copied Soviet clone, so its design choice became the de facto standard. Buyers did not choose Beta Disk; they got it whether they wanted it or not.

The lock-in was total. An often-quoted observation from the era: by 1992, "every new program (game or system one) released in ExUSSR will be Beta 128 only." Tape effectively vanished from the Soviet scene years before it did from the Western one — the inverse of the conventional history, where the West kept tape dominant for games until the late 1980s.

#### 1.3.3 Modern hardware inheritance

Modern Spectrum-clone and FPGA hardware still implements the Beta Disk port map for backward compatibility with the TR-DOS software catalogue:

- **ZX Evolution** (Pentagon-based FPGA redesign) — full Beta 128 compatibility.
- **ZX Spectrum Next** — Beta 128 port map implemented in the FPGA, in addition to the newer DivMMC/SD storage.
- **Karabas** (open-hardware Pentagon successor) — same.
- **DivMMC/DivIDE boot path** — emulates a Beta 128 floppy during the ESXDOS boot sequence, so TR-DOS software can launch from SD card.

The Beta Disk Interface is, as a result, the longest-lived storage interface in the Spectrum ecosystem: designed in 1985, locked in by 1990, and still emulated in 2024 — a forty-year run driven almost entirely by its ex-USSR adoption.

---

## §2. Hardware Block Diagram

### 2.1 The major components

A real Beta Disk Interface cartridge contains the following components:

| Component | Purpose | Notes |
|---|---|---|
| **Edge connector** | Plugs onto the Spectrum's rear expansion bus | All 86 pins of the ZX Spectrum edge connector are passed through to a second connector on the back of the cartridge, allowing further peripherals to be daisy-chained. |
| **Address decoder** | Decodes I/O ports `#1F`, `#3F`, `#5F`, `#7F`, `#FF` and memory window `#3D00–#3FFF` | Implemented as a small PAL or as discrete 74LS-series logic depending on the board revision. |
| **TR-DOS ROM** | 16 KB EPROM (27128 or equivalent) holding the TR-DOS 5.x code | Mapped into the Spectrum's `#0000–#3FFF` slot when paged in. |
| **WD1793 / KR1818VG93 FDC** | The floppy controller chip itself | See [fdc_vg93.md](fdc_vg93.md) for full details. |
| **Control latch (74LS273 or equivalent)** | 8-bit latch holding drive-select / motor / side bits | Written via port `#FF`. |
| **Clock oscillator** | 8 MHz crystal or RC oscillator | Drives the WD1793's CLK pin (8 MHz → 6/12/20/30 ms step rates, 250 kbit/s MFM data rate). |
| **WAIT-state generator** | Small monostable or RC delay that holds the Z80's `/WAIT` line low for ~2 µs on every I/O access to ports `#1F`–`#7F` | Necessary because the WD1793 needs ≥1 µs of address-setup time before `/RD` or `/WR` is asserted, but the Z80's I/O cycle is too fast for that at 3.5 MHz. |
| **Data bus buffer (74LS245)** | Bidirectional buffer between the Spectrum's data bus and the WD1793 / latch / ROM | Used to drive the WD1793's data lines strongly enough to survive the long cable runs of a daisy-chained Spectrum. |
| **Shugart 34-pin header** | Connects to the floppy drive cable | Carries the WD1793's step/dir/wg/wd signals plus the latched drive/motor/side signals. |

### 2.2 Signal flow

```
                  ┌─────────────────────────────┐
                  │        ZX Spectrum          │
                  │  Z80 @ 3.5 MHz              │
                  └──────┬──────────────────────┘
                         │ A0..A15, D0..D7, /IORQ, /RD, /WR,
                         │ /MREQ, /M1, /RFSH, /WAIT, /RESET,
                         │ /ROMCS
                         ▼
            ┌────────────────────────────────────────┐
            │   Beta Disk Interface cartridge        │
            │                                        │
            │   ┌────────────┐                       │
            │   │   Address  │ ─── /CS, A0, A1 ──▶   │
            │   │  decoder   │ ─── /ROMCS ───────▶   │
            │   └─────┬──────┘                       │
            │         │                              │
            │   ┌─────▼────────────┐                 │
            │   │  WAIT generator  │ ─── /WAIT ◀──── │
            │   └──────────────────┘                 │
            │                                        │
            │   ┌──────────────────┐  D0..D7         │
            │   │   WD1793 /       │ ◀──────────────▶│
            │   │   KR1818VG93     │                 │
            │   │   FDC            │                 │
            │   └─────────┬────────┘                 │
            │             │                          │
            │             │   step / dir / wd / wg / │
            │             │   tr00 / idx / wp / dso..3
            │             ▼                          │
            │   ┌──────────────────┐                 │
            │   │  Control latch   │ ◀── port #FF ── │
            │   │  (drive/motor/   │ ─── ds0..3, mtr,│
            │   │   side)          │     side ─────▶ │
            │   └─────────┬────────┘                 │
            │             │                          │
            │   ┌─────────▼────────┐                 │
            │   │  34-pin Shugart  │ ─── to drives   │
            │   │     header       │                 │
            │   └──────────────────┘                 │
            │                                        │
            │   ┌──────────────────┐                 │
            │   │   TR-DOS ROM     │ ◀── paged into  │
            │   │   (16 KB)        │     #0000-#3FFF │
            │   └──────────────────┘                 │
            └────────────────────────────────────────┘
```

The key thing to notice in this diagram is that **all host-visible control flows through three places**: the WD1793 register file (ports `#1F`, `#3F`, `#5F`, `#7F`), the control latch (port `#FF`), and the TR-DOS ROM paged into memory. There is no other software-visible state in the cartridge.

### 2.3 Why a WAIT-state generator is needed

The WD1793's `/CS`, `A0`, `A1` inputs require ≥150 ns of address-setup time before `/RE` or `/WE` is asserted, and the read-data output needs ~150 ns after `/RE` is de-asserted before the bus can be released. At the Spectrum's 3.5 MHz Z80 clock, an I/O cycle is 4 T-states = ~1.14 µs, of which `/IORQ` is low for only 2 T-states (~570 ns). That's plenty of time for the address setup, but the WD1793 also requires the address to be stable for a full read or write — and the WD1793's output drivers are not strong enough to drive the long, capacitive Spectrum expansion bus at full speed.

The WAIT-state generator inserts ~2 µs of wait time at the start of every I/O cycle to ports `#1F`, `#3F`, `#5F`, `#7F`, `#FF`. This guarantees the WD1793 sees stable addresses and the data bus has time to settle. The cost is that I/O operations to the Beta Disk Interface take roughly 5–6 µs each (vs. ~2 µs for an unthrottled Z80 I/O cycle). The TR-DOS ROM code is written with this assumption in mind.

This is also why a Beta Disk Interface clone built with a fast modern microcontroller or FPGA can be **much** faster than the original: the WAIT state is no longer needed if the FDC replacement is fast enough to keep up with the Z80.

---

## §3. Port Map

### 3.1 The five host-visible ports

The Beta Disk Interface occupies five ports in the Z80's I/O address space:

| Port | Read (`IN`) | Write (`OUT`) | Action |
|---|---|---|---|
| `#1F` | Status register | Command register | Selects WD1793 register 0 (A0=0, A1=0). |
| `#3F` | Track register | Track register | Selects WD1793 register 1 (A0=1, A1=0). |
| `#5F` | Sector register | Sector register | Selects WD1793 register 2 (A0=0, A1=1). |
| `#7F` | Data register | Data register | Selects WD1793 register 3 (A0=1, A1=1). |
| `#FF` | (system variable read, see §3.4) | Control latch | Drive select, motor, side, ROM-page control. |

Note the pattern: bits 5 and 6 of the port number are `01` (this is what the address decoder recognises as "the Beta Disk Interface range"); bits 0, 1, and 2 select which WD1793 register to access (`00` = status/command, `01` = track, `10` = sector, `11` = data); bits 3, 4, and 7 are **don't-care** in the original hardware. This is why the Beta Disk Interface aliases across `#1F`, `#3F`, `#5F`, `#7F`, `#9F`, `#BF`, `#DF`, `#FF` — only bits 5 and 6 are actually decoded as 01 for the FDC.

Modern emulators and FPGA clones should decode bits 5 and 6 only (treating the FDC ports as a "select /CS low if bits 5,6 = 01"), and the control latch as a separate decode ("select /CS low if A0=1 and A1=1 and bits 5,6 = 11" — i.e. ports `#FF`, `#DF`, `#BF`, `#9F` all alias to the latch). Pentagon and Scorpion hardware does exactly this.

### 3.2 The WD1793 ports `#1F`, `#3F`, `#5F`, `#7F`

These four ports pass straight through to the WD1793's register-select pins, with `/CS` asserted. See [fdc_vg93.md §3](fdc_vg93.md) for the full description of what each register contains; for reference:

```
| Port | A1 | A0 | /RE=0 (read)  | /WE=0 (write) |
| #1F  | 0  | 0  | Status        | Command        |
| #3F  | 0  | 1  | Track         | Track          |
| #5F  | 1  | 0  | Sector        | Sector         |
| #7F  | 1  | 1  | Data          | Data           |
```

There is no wait between successive accesses — the TR-DOS ROM code is written with the assumption that every `IN` / `OUT` to these ports takes at least 5 µs (because of the WAIT-state generator in §2.3). Code that polls the status register in a tight loop will hit the WAIT state on every iteration.

### 3.3 The control latch port `#FF`

Writing to port `#FF` latches a byte into the 8-bit control register. The bit assignment is:

```
| Bit | When set to 1                  | When cleared to 0                 |
|  7  | TR-DOS ROM paged into memory   | TR-DOS ROM paged out (normal ROM) |
|  6  | (unused; should be 0)          | (unused)                          |
|  5  | (unused; should be 0)          | (unused)                          |
|  4  | (unused; should be 0)          | (unused)                          |
|  3  | Drive D selected               | Drive D not selected              |
|  2  | Drive C selected               | Drive C not selected              |
|  1  | Drive B selected               | Drive B not selected              |
|  0  | Drive A selected               | Drive A not selected              |
```

Note that bits 0–3 are **active-high** drive-select lines. Most real hardware selects only one drive at a time (writing `#01` for A, `#02` for B, `#04` for C, `#08` for D), but it is technically possible to select multiple drives simultaneously — this is sometimes used to spin up two drives before a `COPY` operation.

**Important:** the original Beta Disk Interface does **not** have a side-select bit on port `#FF`. Side selection is done **inside the WD1793** via the side-select flag in the Type II command byte (the `s` bit). Soviet clones (Pentagon, Scorpion, etc.) added a separate side-select bit on a different port — see §7 for details.

**Motor control** is also **not** on port `#FF` in the original interface. The motor is controlled via the WD1793's head-load flag (the `h` bit in Type I commands), which controls the `/HDLD` pin and — through external glue — turns on the spindle motor for the currently-selected drive. Again, Soviet clones differ and added an explicit motor bit.

### 3.4 Reading port `#FF`

Reading port `#FF` is unusual. On the original Beta Disk Interface, port `#FF` is **write-only** — reading it returns an undefined value (typically floating bus data). However, TR-DOS 5.x uses the address `#5C3C` (the BASIC system variable `STRMS`) and other system variables to track which drive is currently active, so software rarely needs to read port `#FF`.

Later Soviet clones sometimes made port `#FF` readable, returning the last value written. Code written for these clones should not assume this works on the original hardware.

### 3.5 Memory-mapped ports

In addition to the five I/O ports above, the Beta Disk Interface responds to a write at memory address `#3D00–#3DFF` as a "page the TR-DOS ROM in" trigger. Any write to this 256-byte window flips the Beta Disk Interface's page latch, swapping the Spectrum's `#0000–#3FFF` ROM window to point to the TR-DOS ROM instead of the BASIC ROM. See §4 for the full mechanism.

---

## §4. TR-DOS ROM Bank Switching

### 4.1 Why a separate ROM is needed

The ZX Spectrum's ROM (`#0000–#3FFF`, 16 KB) contains the BASIC interpreter and the cassette LOAD/SAVE routines. It cannot be modified in place, and the cassette routines are far too primitive to handle floppy disk. The TR-DOS is therefore supplied as a separate 16 KB ROM that takes over the `#0000–#3FFF` window whenever disk operations are needed.

When TR-DOS is paged in, the BASIC interpreter is gone — there is no BASIC, no syntax checking, no editor. The TR-DOS ROM is a self-contained piece of code that handles disk operations and then returns control to the original ROM. This is conceptually similar to how the +3 uses its `+3DOS` calls (the `DOS` hook at `#0008`), but the mechanism is different.

### 4.2 The paging mechanism

The Beta Disk Interface uses a **simple flip-flop page latch**: writing to any address in the `#3D00–#3DFF` range toggles the latch. The latch controls a multiplexer between the Spectrum's on-board ROM and the TR-DOS ROM. When the latch is set, the TR-DOS ROM responds to memory accesses at `#0000–#3FFF`; when cleared, the on-board ROM does.

Once paged in, the TR-DOS ROM stays in place until it explicitly pages itself out (by writing to a "page out" address that the Beta Disk Interface's address decoder recognises — typically `#3D00` for page-in and a different address in `#3D00–#3DFF` for page-out, depending on the board revision). The TR-DOS ROM code at the end of every command sequence writes to the page-out address to return control to the BASIC ROM.

The actual addresses used for page-in and page-out vary slightly across revisions. The canonical values, used by TR-DOS 5.03 and most emulators:

| Address | Action |
|---|---|
| `#3D00` | Page TR-DOS ROM **out** (BASIC ROM active) |
| `#3D02` | Page TR-DOS ROM **in** (TR-DOS ROM active, edge-triggered) |
| `#3D03` | Some clones use this as an alternative page-in address |

Writing to **any** address in `#3D00–#3DFF` is sufficient to page the ROM in on real hardware, because the address decoder ignores the low bits. TR-DOS itself uses `#3D02` as a convention.

### 4.3 How the TR-DOS ROM hooks BASIC

When the TR-DOS ROM is paged in, it copies a small set of hooks into the Spectrum's RAM (specifically, it patches the BASIC command table and the channel definitions). After this, the BASIC keywords `LOAD`, `SAVE`, `MERGE`, `VERIFY`, etc. are redefined to call TR-DOS routines instead of the cassette routines. The `*` (star) command is also installed, allowing direct access to TR-DOS commands like `*CAT`, `*FORMAT`, `*COPY`.

The hook installation is performed by entering TR-DOS via its entry point at `#3D03` (which the user does by typing `RANDOMIZE USR 15616` in BASIC, or by pressing a special key combination on machines where TR-DOS is pre-installed in ROM space). From this point, all disk operations go through TR-DOS without any explicit "page in" calls from user code.

### 4.4 The 4-byte entry stub

When the user calls `RANDOMIZE USR 15616` (decimal) — or, equivalently, executes `RST #08 DW hook` — the Spectrum's CPU eventually ends up executing a tiny stub at `#3D00` (or `#3D02`). This stub is **always** present in the Spectrum's memory map, even when TR-DOS is not paged in, because the Beta Disk Interface's address decoder forces the stub bytes onto the data bus when the CPU reads addresses `#3D00–#3D03`.

The stub is 4 bytes long and looks like:

```
#3D00:  LD BC, #0101   ; placeholder; really: jump to TR-DOS entry
#3D03:  ...
```

The exact bytes vary by Beta Disk Interface revision, but the effect is: "page TR-DOS in and jump to the TR-DOS entry point." This is how TR-DOS is bootstrapped into existence from the BASIC environment.

### 4.5 What happens during TR-DOS execution

Once TR-DOS is paged in, the spectrum's `#0000–#3FFF` window contains TR-DOS code. The interrupt vector table at `#0000–#00FF` is replaced, so RST instructions go to TR-DOS handlers. The TR-DOS code uses the WD1793 ports (`#1F`, `#3F`, `#5F`, `#7F`) and the control latch (`#FF`) to perform disk I/O, and it uses the Spectrum's normal RAM (`#4000–#FFFF`) for buffers and state.

When TR-DOS is done with a command, it writes to `#3D00` to page the BASIC ROM back in, restores the BASIC command hooks (so the BASIC interpreter's next `LOAD` will still go through TR-DOS), and returns to the caller. From the user's point of view, TR-DOS is "always there" once activated.

### 4.6 Compatibility with the 128K / +2 / +3

The 128K, +2, and +3 Spectra have a more sophisticated memory management system than the 48K: they can page 16 KB RAM banks into the `#0000–#3FFF` window, and they have a separate "ROM 0 / ROM 1" selection mechanism for the BASIC ROMs. The Beta Disk Interface's paging logic interferes with these mechanisms in a few subtle ways:

- On the 128K / +2 (Toastrack / Grey +2), TR-DOS works as on the 48K: paging the TR-DOS ROM in simply replaces the BASIC ROM. The 128K's `+3DOS` calls (which use the `DOS` hook at `#0008`) are not used.
- On the +2A / +3 (Black +2 / +3), the paging mechanism is different (the `+3` uses a custom MMU). The Beta Disk Interface works, but TR-DOS coexists awkwardly with the +3's own `+3DOS` ROM — usually TR-DOS takes over and the +3's floppy controller is disabled via software.
- On the Soviet clones (Pentagon, Scorpion), TR-DOS is the default and only disk operating system; there is no conflict.

See §7 for a full discussion of variants.

---

## §5. Drive Select, Motor, and Side Control

### 5.1 Drive selection: bits 0–3 of port `#FF`

The Beta Disk Interface supports up to four floppy drives, labelled **A**, **B**, **C**, **D**. Drive selection is done by writing a single bit set in bits 0–3 of port `#FF`:

| Bit | Drive | Write value |
|---|---|---|
| 0 | A | `#01` |
| 1 | B | `#02` |
| 2 | C | `#04` |
| 3 | D | `#08` |
| 0+1 | A and B (both selected) | `#03` |

Each bit corresponds to one of the four Shugart `/DS0`–`/DS3` lines on the 34-pin floppy cable (active-low on the cable, but latched active-high on port `#FF`, with the inversion done in hardware between the latch and the cable connector). When a drive's `/DSn` line is asserted, that drive responds to step/dir/read/write signals; all other drives ignore them.

Selecting multiple drives simultaneously is electrically valid (and sometimes useful — e.g., to spin up two drives for a `COPY`), but reads and writes can only target one drive at a time (the WD1793's read/write signals go to whichever drive has `/DSn` asserted). In practice, TR-DOS software always selects exactly one drive.

When no drive is selected (write `#00` to port `#FF`), the floppy cable is electrically isolated — no step pulses, no read/write signals, no motor. This is the default state after a reset.

### 5.2 Motor control: implicit via the WD1793

The original Beta Disk Interface has **no explicit motor-on port bit**. Instead, the spindle motor is started indirectly via the WD1793's **head-load** mechanism:

1. Software issues a Type I command (RESTORE / SEEK / STEP) with the **head-load flag** (`h`) set.
2. The WD1793 asserts its `/HDLD` output.
3. External glue in the Beta Disk Interface cartridge translates `/HDLD` into a spindle-motor-on signal for the currently-selected drive.

This means: on real Beta Disk Interface hardware, the motor spins up automatically the first time you do any head-positioning command, and stays spinning as long as the WD1793 keeps `/HDLD` asserted. The WD1793 will drop `/HDLD` after a configurable delay (15 index pulses, or ~1.5 seconds of disk rotation) if no further commands are issued.

**Side effect:** software that wants to read sector 0 of a track must first do a Type I command with `h=1` to ensure the motor is up to speed. If the software does a Type II READ SECTOR without first issuing a Type I command with `h=1`, the WD1793 may attempt to read from a stationary disk and return `RECORD NOT FOUND`.

Modern Soviet clones (Pentagon, Scorpion, etc.) and emulators typically add an **explicit motor-on bit** to a separate port. See §7 for details. TR-DOS software written for these clones may set this bit directly, but TR-DOS software written for the original Beta Disk Interface uses only the head-load mechanism.

### 5.3 Side selection: implicit via the WD1793

Like motor control, **side selection** on the original Beta Disk Interface is **not** on port `#FF`. It is done inside the WD1793, via the **side-select flag** (`s`) in the Type II command byte:

- `s = 0` → side 0 of the disk.
- `s = 1` → side 1 of the disk.

The WD1793's `/SIDE` output pin is wired to the floppy cable's side-select line (pin 32 on the Shugart connector). When a Type II command is issued with `s=1`, the WD1793 asserts `/SIDE` and the drive uses its upper head; when `s=0`, `/SIDE` is de-asserted and the drive uses its lower head.

This is sufficient for most software because the WD1793 sets `/SIDE` **before** it starts reading or writing, ensuring the drive head is on the right side when the data transfer begins.

**Side effect:** software cannot change side without issuing a Type II command. If the software needs to read from both sides of a disk in quick succession (e.g., to read a 2-sided file spanning both sides), it must issue Type II commands with the appropriate `s` bit set each time — it cannot simply flip a side-select port bit between sectors.

Soviet clones added an **explicit side-select bit** to port `#FF` (typically bit 4), allowing software to change side without re-issuing a Type II command. This is a common source of incompatibility: software written for these clones may flip bit 4 of port `#FF` and expect the side to change, which has no effect on original Beta Disk Interface hardware (where bit 4 is unused and the WD1793's `/SIDE` pin is driven solely by the `s` bit in the command byte).

### 5.4 Drive spin-up timing

After the spindle motor starts, the floppy disk takes time to reach its operating speed (300 RPM for a 5.25" drive, 300 RPM for a 3.5" drive). The WD1793 has a built-in **spin-up timer** that requires 6 index pulses (≈1.2 seconds at 300 RPM) of disk rotation before it will accept a Type II or Type III command. This is implemented by the WD1793's internal state machine, which waits for the index pulse counter to reach 6 after the head is loaded.

The first Type I command after a motor start therefore takes ~1.2 seconds; subsequent commands are fast (a few milliseconds per track step). TR-DOS software is written with this in mind: the initial `RESTORE` command on startup takes 1–2 seconds, and then disk operations are quick.

Software that needs to access the disk as fast as possible can disable the spin-up timer by writing the Type I command with the **head-load flag cleared** (`h=0`), then waiting for the user to indicate the disk is spinning. This is rarely done because it requires knowing how long the motor has been running.

### 5.5 Reset state

On power-up or after a `/RESET`, the Beta Disk Interface's control latch is reset to `#00` — no drives selected, motor off, side 0. The WD1793 is held in a `/MR` (master reset) state until the host writes a `RESTORE` command.

After a reset, the Spectrum's `#0000–#3FFF` window contains the BASIC ROM (the TR-DOS ROM is not paged in). The 4-byte stub at `#3D00–#3D03` is present but inactive until written to.

Software that needs to use the disk must:
1. Page TR-DOS in by writing to `#3D00–#3DFF` (or via the entry point at `RANDOMIZE USR 15616`).
2. Select the desired drive via port `#FF`.
3. Issue a `RESTORE` command to the WD1793 to home the head and start the motor.
4. Wait for the spin-up timer to expire (≈1.2 seconds).
5. Issue Type II / III commands to access the disk.

TR-DOS does all of this automatically when the user types `*CAT`, `LOAD "x"`, etc.

---

## §6. Cable Pinout and Drive Compatibility

### 6.1 The Shugart 34-pin connector

The Beta Disk Interface uses the industry-standard **Shugart 34-pin** floppy connector. This is the same connector used by 5.25" and 3.5" floppy drives on the IBM PC and almost every other home computer of the era, with one important difference: **the Shugart bus uses drive-select jumpers, while the IBM PC bus uses a twisted cable.**

The pinout of the 34-pin header on the Beta Disk Interface:

| Pin | Signal | Direction | Notes |
|---|---|---|---|
| 2  | `/REDWC` (reduced write current) | out | Usually unused on the Beta Disk Interface. |
| 4  | (reserved, head load) | — | Often unused. |
| 6  | `/DS3` (drive select 3) | out | Drives D when bit 3 of port `#FF` is set. |
| 8  | `/INDEX` | in | From the currently-selected drive. |
| 10 | `/DS0` (drive select 0) | out | Drives A when bit 0 of port `#FF` is set. |
| 12 | `/DS1` (drive select 1) | out | Drives B when bit 1 of port `#FF` is set. |
| 14 | `/DS2` (drive select 2) | out | Drives C when bit 2 of port `#FF` is set. |
| 16 | `/MOTOR ON` | out | On the original Beta Disk Interface, this is driven by external glue from the WD1793's `/HDLD` pin. |
| 18 | `/DIR` (direction select) | out | From the WD1793. |
| 20 | `/STEP` | out | From the WD1793. |
| 22 | `/WDATE` (write data) | out | From the WD1793. |
| 24 | `/WGATE` (write enable) | out | From the WD1793. |
| 26 | `/TRK00` (track 0) | in | To the WD1793. |
| 28 | `/WPT` (write protect) | in | To the WD1793. |
| 30 | `/RDATE` (read data) | in | To the WD1793. |
| 32 | `/SIDE1` (side select) | out | From the WD1793's `/SIDE` output. |
| 34 | `/READY` | in | Often unused; the WD1793 uses index pulses for spin-up detection instead. |
| Odd pins (1, 3, 5, ..., 33) | GND | — | Ground; all odd pins are tied to ground. |

### 6.2 Drive compatibility

The Beta Disk Interface works with **any** Shugart-bus floppy drive: 5.25" 40-track (40 tracks × 1 side, 40 tracks × 2 sides), 5.25" 80-track (80 tracks × 2 sides, "quad density"), 3.5" 80-track (standard PC floppy drive), and 3" drives (used by the Amstrad CPC / +3 — though the +3 uses its own internal interface, an external Beta Disk Interface connected to a 3" drive works fine).

To use a drive with the Beta Disk Interface:

1. **Set the drive-select jumper** on the drive to match the cable position. Shugart-bus drives have a small DIP switch or solder jumper that selects `/DS0`, `/DS1`, `/DS2`, or `/DS3`. The first drive on the cable should be set to `/DS0` (drive A); the second to `/DS1` (drive B); etc.
2. **Terminate the last drive on the cable**. The last drive in the chain should have its termination resistor pack installed (or the terminating jumper set). Intermediate drives should have their termination removed to avoid bus contention.
3. **Set the proper drive-ready configuration**. Some drives have a `/READY` jumper; the Beta Disk Interface does not use `/READY`, so it does not matter, but if the drive requires `/READY` to be pulled low before it responds, this jumper should be set to "always ready" or tied to ground.

### 6.3 IBM PC drives: the twist problem

Standard IBM PC floppy drives use a **twisted cable** instead of drive-select jumpers: the cable has a 7-wire twist between the connectors for drive A and drive B, so that drive A responds to `/DS1` (because the twist routes `/DS0` from the controller to the drive's `/DS1` pin), and drive B responds to `/DS0`. This means an unmodified IBM PC drive connected to a Beta Disk Interface (which does not have the twist) will be on the wrong drive-select line.

To use an IBM PC 3.5" drive on a Beta Disk Interface, you must either:
- Use a cable with the IBM twist (and live with the fact that drive A responds to port `#FF` bit 1, not bit 0), or
- Modify the drive (often a small solder jumper on the drive's PCB) to change it from `/DS1` to `/DS0`, then use a straight cable.

Soviet clones often shipped with IBM-twist cables for compatibility with cheap surplus IBM PC drives, so Soviet software does not assume a specific mapping of port `#FF` bits to cable positions.

### 6.4 Drive geometry and TR-DOS

TR-DOS 5.x assumes **80 tracks × 2 sides × 10 sectors/track × 512 bytes/sector** by default (the standard TR-DOS 80-track format, see [trd_disk_format.md](trd_disk_format.md)). However, the underlying hardware supports any reasonable geometry:

- 40-track 5.25" drives (single-sided or double-sided) — TR-DOS 5.0 / 5.1 supports these via the `*FORMAT` command with reduced track count.
- 80-track 5.25" drives — standard TR-DOS format.
- 80-track 3.5" drives — standard TR-DOS format; the most common configuration on Soviet hardware.
- 80-track 3" drives (as used by the Amstrad CPC and the +3) — supported by TR-DOS, though rarely used because of the +3's separate internal controller.

The WD1793's step rate must match the drive's track-to-track step time. TR-DOS uses a 6 ms step rate (clock bit pattern `00` in the Type I command), which works for all standard 5.25" and 3.5" drives. Faster drives (e.g., 3 ms on some 3.5" drives) are supported by changing the step rate bits in the Type I command byte.

### 6.5 Cable length and signal integrity

The Shugart bus is rated for a maximum cable length of about 1 metre (≈3 feet). The Beta Disk Interface itself is at the end of the Spectrum's expansion bus, which adds another ~30 cm of bus length before the cable even starts. Long cables (more than 1.5 metres total) cause signal reflections and timing problems — particularly on the high-impedance `/RDATE` line, where reflections can produce phantom data transitions that the WD1793's PLL will misinterpret.

In practice, Soviet Beta Disk Interface clones used short cables (typically 30–50 cm) and a single drive per cable, with no signal-integrity problems. Multi-drive setups with long cables often required termination resistors at both ends of the cable to absorb reflections.

---

## §7. Variants: Beta 48, Beta 128, Soviet Clones, Pentagon Integration

### 7.1 The original Beta 128 vs. Beta 48

The original Beta Disk Interface shipped in two main revisions:

- **Beta 48** (1985) — for the 16K / 48K Spectrum. Provides ports `#1F`–`#7F` and the control latch on port `#FF`. The TR-DOS ROM is a 16 KB EPROM that pages into the Spectrum's `#0000–#3FFF` window. Supports up to 4 drives. Uses a WD1793 FDC.
- **Beta 128** (1986) — for the 128K, +2, and +3. Functionally identical to the Beta 48, but with revised address-decoding logic that works correctly with the 128K's more complex memory management. Some Beta 128 revisions used the WD2793 (double-density-capable) FDC, though TR-DOS never officially used double-density mode.

The host-visible port map and the control-latch bit assignment are **identical** on both revisions, so TR-DOS software runs on either without modification.

### 7.2 Soviet clones

After the Beta Disk Interface's hardware was reverse-engineered in the late 1980s, dozens of Soviet companies and hobbyists produced clones. The most common ones are:

- **Moscow Beta Disk clones** (various, 1989–1992) — direct PCB-level clones of the Beta 128, using the KR1818VG93 Soviet WD1793 clone. Compatible with TR-DOS 5.x.
- **Pentagon onboard FDC** (Pentagon 48, Pentagon 128, Pentagon 512, 1991–1996) — the Pentagon home-brew computer has the Beta Disk Interface port map built into its motherboard. Uses the KR1818VG93. The control latch on port `#FF` has the same bit assignment as the original Beta Disk Interface, plus an **explicit motor bit on bit 7** (bit 7 of port `#FF` is `MOTOR ON` on Pentagon, overriding the original's TR-DOS-ROM-page bit — which the Pentagon does not need because it has no BASIC ROM in the original sense).
- **Scorpion ZS-256 onboard FDC** (Scorpion, 1992) — similar to Pentagon, with the Beta Disk Interface port map built in. Adds a separate **side-select bit on port `#FF` bit 4** (bit 4 is `SIDE` on Scorpion, unused on original Beta Disk). The Scorpion also has a motor bit on bit 7.
- **Kay 1024, Profi, ATM Turbo** — all include Beta Disk-compatible FDCs with similar port maps, though the exact bit assignments for motor and side vary between models.

### 7.3 The port `#FF` bit-assignment chaos

Because Soviet clones added motor and side bits to port `#FF` without standardising on a single bit assignment, TR-DOS software that targets Soviet clones must handle **multiple incompatible port `#FF` conventions**. The most common variants:

| Bit | Original Beta | Pentagon | Scorpion |
|---|---|---|---|
| 7 | TR-DOS ROM page | Motor on/off | Motor on/off |
| 6 | (unused) | (unused) | (unused) |
| 5 | (unused) | (unused) | (unused) |
| 4 | (unused) | (unused) | Side select (1=side 1) |
| 3 | Drive D | Drive D | Drive D |
| 2 | Drive C | Drive C | Drive C |
| 1 | Drive B | Drive B | Drive B |
| 0 | Drive A | Drive A | Drive A |

To maintain compatibility, modern TR-DOS versions (TR-DOS 6.x, ETR-DOS, Mr Gluk Reset Service) probe the hardware at boot time by writing known patterns to port `#FF` and reading them back, or by querying a model-detection port, and then use the correct bit assignment for the detected hardware. Emulators usually emulate the Pentagon variant by default, since that's the most common Soviet Spectrum model in use today.

### 7.4 Pentagon / Scorpion specifics

On Pentagon and Scorpion hardware, the Beta Disk Interface port map is **wired directly to the motherboard** — there is no external cartridge. The port addresses are the same (`#1F`–`#7F`, `#FF`), but the WAIT-state generator is implemented as part of the motherboard's Z80 I/O logic, not as a separate monostable.

Both machines also have an **onboard TR-DOS ROM** (typically version 5.03 or 5.04) paged in the same way as the original Beta Disk Interface — writing to `#3D00–#3DFF` toggles the page latch. The ROM is soldered to the motherboard (often as part of a larger "BIOS" / system ROM that also contains a BASIC ROM and CP/M loader).

### 7.5 Western variants and uncommon drives

A few Western companies produced Beta Disk Interface variants:

- **Technology Research Beta 128 with WD2793** — Western Digital's WD2793 is a double-density-capable upgrade of the WD1793. Some Beta 128 boards shipped with this chip and offered a `*DD` (double-density) TR-DOS command. The format was not officially TR-DOS-compatible, but some software supported it.
- **Opus Discovery** — a different interface entirely, using its own FDC (WD1770) and disk format. Not Beta Disk-compatible; see [opus_discovery_format.md](opus_discovery_format.md).
- **Rotronics Wafadrive** — not Beta Disk-compatible; uses its own tape-loop storage.

For software that needs to detect which interface is present, the standard trick is to write to port `#FF` and read back the value. On a real Beta Disk Interface, the read is undefined (the latch is write-only); on Soviet clones, the latch may or may not be readable. Detecting a Pentagon vs. a Scorpion vs. an original Beta Disk requires more elaborate probing that is beyond the scope of this article.

### 7.6 Emulator assumptions

Modern emulators (UnrealSpeccy, ZEsarUX, FUSE, SpecEmu, etc.) typically emulate the **Pentagon variant** of the Beta Disk Interface by default, because:
- The Pentagon is the most common Soviet Spectrum clone, and most active TR-DOS software targets the Pentagon.
- The Pentagon variant includes the motor bit on port `#FF` bit 7 and supports reading port `#FF` back, which makes software that targets it simpler.
- The Pentagon variant does not need the WAIT-state generator (the emulator does not have a physical Z80), so I/O cycles are fast.

Emulators usually have a configuration option to switch between Pentagon, Scorpion, and "original Beta Disk" modes for accurate testing. For 100% accurate original-Beta-Disk emulation, the emulator should make port `#FF` write-only and force the motor to be controlled via the WD1793's head-load mechanism.

---

## §8. Common Issues and Maintenance

### 8.1 Edge-connector contact oxidation

The most common hardware failure on a real Beta Disk Interface is **oxidation of the Spectrum's edge-connector contacts**. The contacts are gold-flashed copper, and over 30+ years the gold flash wears off and the copper underneath corrodes. Symptoms include intermittent disk errors, the TR-DOS ROM not paging in reliably, and the Spectrum crashing when the cartridge is plugged in.

The fix is mechanical: clean the edge-connector contacts on both the Spectrum and the Beta Disk Interface with isopropyl alcohol and a soft cloth, or use a specialised contact cleaner. Inserting and removing the cartridge several times can also break through the oxide layer.

### 8.2 Drive belt failure (5.25" drives)

Older 5.25" floppy drives use a rubber belt to drive the spindle. Over decades, the belt perishes — it either snaps, stretches, or turns into a sticky goo. Symptoms include the disk not spinning at the correct speed (read errors), the motor running but the disk not moving (snapped belt), or a grinding noise and a stuck disk (gooey belt jamming the mechanism).

Replacement belts are still available from specialty suppliers. The belt size is typically a "square belt" of about 50–80 mm length; the exact size depends on the drive model.

3.5" drives do not have a belt — they use a direct-drive motor — so this problem does not affect them.

### 8.3 Head alignment drift

After years of use, the read/write head on a floppy drive can drift out of alignment with the track positions. Symptoms include a disk that was formatted and written on the drive reading fine, but failing to read on a different drive (or vice versa). The standard fix is to write a "calibration disk" on a known-good drive and adjust the head-positioner stepper motor until the calibration disk reads correctly.

TR-DOS does not have a built-in head-alignment utility. The closest thing is `*COPY`, which copies a disk track-by-track; if `*COPY` succeeds for tracks 0–39 but fails for tracks 40–79, the head is likely misaligned.

### 8.4 Disk media failure

Magnetic media degrade over time. The most common failure mode is **magnetic domain decay**: the recorded bits gradually lose their magnetic orientation, and after 20–30 years the disk becomes unreadable. There is no fix for this — once the data is gone, it is gone. The only mitigation is to copy data off old disks onto newer media (or into disk image files like .TRD or .SCL) before they degrade.

A second failure mode is **mould growth on the disk surface**, particularly common for disks stored in damp conditions. Mould physically damages the oxide layer and contaminates the drive head. Cleaning mould-contaminated disks is a delicate process involving isopropyl alcohol and Q-tips, and the drive head must also be cleaned afterwards.

### 8.5 Software incompatibilities

Software written for Soviet clones (Pentagon, Scorpion) may not work correctly on an original Beta Disk Interface, because:

- It expects port `#FF` to be readable (returns last value written).
- It expects a motor bit on port `#FF` bit 7 and flips this bit to start the motor.
- It expects a side bit on port `#FF` bit 4 (Scorpion variant).
- It assumes a faster I/O cycle (no WAIT-state generator).
- It assumes the WD1793's spin-up timer has already expired (because the Soviet clone keeps the motor running continuously).

To run such software on an original Beta Disk Interface, you need either:
- A TR-DOS version patched for original-Beta-Disk hardware (some "TR-DOS 5.04 patches" exist that fix the motor-bit assumption).
- A hardware adapter that emulates the Pentagon's port `#FF` behaviour.
- An emulator that lets you choose which hardware to emulate.

### 8.6 Power supply considerations

The Beta Disk Interface draws its power from the Spectrum's +5 V and +12 V lines (via the edge connector). The +12 V is used for the floppy drive's spindle motor; the +5 V is used for the interface's logic. A weak or aged Spectrum power supply may not deliver enough current for both the Spectrum and a power-hungry 5.25" drive, leading to crashes when the drive spins up.

A separate +12 V power supply for the floppy drive (or a modern switched-mode replacement for the Spectrum's original linear supply) is the standard fix.

---

## §9. Modern Replacements

### 9.1 Onboard FDC on modern Spectrum clones

Most modern FPGA-based Spectrum clones include the Beta Disk Interface port map in their HDL, so software written for the Beta Disk Interface runs without modification. Notable examples:

- **ZX Spectrum Next** (2017+) — implements the Beta Disk Interface port map in its FPGA, but does **not** include a physical floppy connector. A "Layer 2" (video layer) widget called the **Pi-zero interface** or a layer-3 expansion can add a real floppy port. By default, the Next reads disk images from the SD card and presents them to TR-DOS via an emulated FDC.
- **ZX Evolution** (2010+) — Russian FPGA-based clone with a real 34-pin floppy connector and an onboard WD1793 (or KR1818VG93) chip. The Beta Disk Interface port map is bit-for-bit compatible with the original, including the WAIT-state generator. Supports both real floppy drives and disk images on SD card.
- **Karabas Pro / Karabas 128** (2018+) — modern Z80-based hardware with a CPLD that implements the Beta Disk Interface port map. Real floppy connector included.
- **ZX-Uno** (2016+) — small FPGA-based Spectrum with an optional floppy expansion that implements the Beta Disk Interface port map.

All of these clones can run original TR-DOS 5.x ROMs and original TR-DOS disk software. The port map is identical; only the underlying hardware (real WD1793 vs. FPGA emulation vs. microcontroller emulation) differs.

### 9.2 Gotek / HxC floppy emulators

The most popular modern replacement for a real floppy drive is the **Gotek** floppy emulator: a small device with a 34-pin Shugart connector that emulates a floppy drive, but reads disk images from a USB stick instead of a physical disk. With the **FlashFloppy** or **HxC** firmware, the Gotek can read .TRD, .SCL, .DSK, and other disk image formats directly.

The Gotek connects to the Beta Disk Interface exactly like a real floppy drive: drive-select jumpers, termination, and the 34-pin cable all work the same way. From the TR-DOS software's point of view, the Gotek is indistinguishable from a real drive (except that it is much faster, more reliable, and never suffers from media degradation).

The original Gotek firmware (the "factory" firmware) reads a proprietary image format (.img with a strict sector layout). The FlashFloppy firmware is recommended because it supports the standard .TRD / .SCL formats and the standard IBM-sector DSK format.

### 9.3 SD-card emulators: DivMMC / Smuc / Nemo IDE

For Spectrum users who want to abandon floppy entirely, the **DivMMC**, **SMUC**, and **Nemo IDE** interfaces provide IDE / SD-card storage that is many orders of magnitude faster than any floppy system. These interfaces use modern mass-storage formats (FAT16, FAT32) and bypass TR-DOS entirely.

However, even these modern interfaces often **emulate the Beta Disk Interface port map** at the software level, so TR-DOS software can run unmodified. The DivMMC, for example, includes an "ESXDOS" ROM that hooks TR-DOS system calls and redirects them to the SD card. The user can still type `LOAD "x"` in BASIC and the file is loaded from SD card instead of floppy.

See [divide_divmmc.md](divide_divmmc.md) and [hdd_overview.md](hdd_overview.md) for details.

### 9.4 Cycle-exact FDC emulation for software preservation

For emulator authors, the gold standard is **cycle-exact** emulation of the original Beta Disk Interface hardware, including:
- The WAIT-state generator (every I/O cycle takes 5–6 µs).
- The WD1793's command state machine (see [fdc_vg93.md](fdc_vg93.md)).
- The exact timing of the TR-DOS ROM's polling loops.
- The implicit motor control via `/HDLD`.
- The implicit side control via the Type II `s` bit.

This level of accuracy is necessary to run protected loaders, custom-format disk software, and demoscene productions that abuse the WD1793's undocumented features. ZEsarUX, UnrealSpeccy, and FUSE all implement approximately cycle-exact Beta Disk Interface emulation; the ZX Spectrum Next's onboard emulator is bit-exact for the original hardware.

The .SCP flux-level format (see [scp_format.md](scp_format.md)) is the gold standard for preserving Beta Disk Interface disks at the flux level, allowing cycle-exact re-emulation of even the most heavily protected loaders.

---

## 10. Cross-references

### 10.1 Within the storage section

- [fdc_vg93.md](fdc_vg93.md) — the companion article to this one. Covers the WD1793 / KR1818VG93 chip in depth: register file, command set, execution phases, status bits, undocumented quirks, and turbo modifications. Read this first to understand what the Beta Disk Interface's ports actually do.
- [trd_disk_format.md](trd_disk_format.md) — the logical disk format used by TR-DOS on a Beta Disk Interface disk. Covers the directory structure, file types (B, C, D, M, #), and disk parameters (80 tracks × 10 sectors × 512 bytes × 2 sides).
- [plus3_floppy.md](plus3_floppy.md) — the +3's internal floppy hardware, which uses the WD1772-PH controller instead of the WD1793. Different port map (single port `#1F` plus side/motor on a system port), but same Shugart 34-pin cable and same disk mechanics.
- [mfm_encoding.md](mfm_encoding.md) — the signal layer recorded on the floppy disk by the Beta Disk Interface's WD1793.
- [disk_format_overview.md](disk_format_overview.md) — the IBM 3740 physical sector layout shared by TR-DOS, +3 DOS, CP/M, and Opus formats.
- [trd_scl_formats.md](trd_scl_formats.md), [dsk_fdi_formats.md](dsk_fdi_formats.md), [udi_format.md](udi_format.md), [scp_format.md](scp_format.md) — disk image formats used to preserve and emulate Beta Disk Interface disks.
- [hdd_overview.md](hdd_overview.md), [ide_interface.md](ide_interface.md), [divide_divmmc.md](divide_divmmc.md) — the modern IDE/SD storage interfaces that displaced the Beta Disk Interface.

### 10.2 Adjacent hardware references

- [plus3_floppy.md](plus3_floppy.md) — for comparison: the +3's integrated WD1772-PH controller and its (different) port map.
- For Spectrum clone onboard FDCs (Pentagon, Scorpion, ATM Turbo, Profi, Kay, ZX Evolution, Karabas): see §7 above, and the [02_hardware/](../../02_hardware/) section.

### 10.3 Reverse engineering and demoscene angles

- For custom loaders, protection schemes, and disk-based DRM that run on a Beta Disk Interface: see [05_reversing/](../../05_reversing/) and in particular [custom_loaders_and_drm.md](../../05_reversing/custom_loaders_and_drm.md).
- For cycle-exact Beta Disk Interface emulation in modern emulators: see [11_emulation/](../../11_emulation/).
- For TR-DOS extensions and modern disk operating systems that build on the Beta Disk Interface (ESXDOS, FatFS, etc.): see [04_operating_systems/](../../04_operating_systems/).

### 10.4 External references

- **The TR-DOS 5.03 ROM source code** — disassemblies are widely available (e.g. on the WoS archive and zxevo.ru). Reading the TR-DOS source is the best way to understand how the Beta Disk Interface ports are used in practice.
- **The Beta Disk Interface schematic** — original schematics are rare, but several reverse-engineered schematics circulate in the Spectrum community. The Pentagon and Scorpion motherboard schematics are also useful because they include the onboard FDC circuitry.
- **Andrew Owen's "ZX Spectrum Hardware" pages** — original documentation on the Beta Disk Interface, with pinouts and address-decoder details.
- **The comp.sys.sinclair FAQ** — historical context on the Beta Disk Interface and its competitors (Opus Discovery, Plus D, Rotronics Wafadrive, Microdrive).
- **The "Beta 128 Disk Interface" entry on the World of Spectrum archive** — software compatibility lists and historical information.

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

You are free to:

- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

- **Attribution** — you must give appropriate credit (a link to this article is sufficient), indicate if changes were made, and indicate the license under which the original is released.
- **ShareAlike** — if you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

The full legal text is available at the link above.

The trademarks **Beta Disk Interface**, **Beta 48**, **Beta 128**, **TR-DOS**, **ETR-DOS**, **ESXDOS**, **WD1793**, **WD1772**, **WD1770**, **WD2793**, **KR1818VG93**, **ZX Spectrum**, **ZX Spectrum Next**, **ZX Evolution**, **ZX-Uno**, **Karabas Pro**, **Karabas 128**, **Peridot**, **Pentagon**, **Scorpion**, **ATM Turbo**, **Profi**, **Kay**, **DivIDE**, **DivMMC**, **Nemo IDE**, **SMUC**, **Gotek**, **FlashFloppy**, **HxC**, **Western Digital**, **Shugart**, **IBM PC**, and others mentioned in this document are the property of their respective owners and are used here for identification and educational purposes only. No endorsement by, or affiliation with, any of these trademark holders is implied.
