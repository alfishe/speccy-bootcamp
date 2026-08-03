[← Overview](README.md) · [Glossary](glossary.md)

# ZX Spectrum Glossary — Platform-Specific Terminology

> **Scope**: This article is the **term reference** for the ZX Spectrum ecosystem: the platform-specific jargon, abbreviations, and proper nouns that appear throughout this knowledge base and across the wider Spectrum literature. Each entry defines the term in one short paragraph and links to the per-topic deep-dive article where the full story lives.

For the **historical narrative**, see [history.md](history.md). For the **per-model technical details** of the hardware mentioned here, see [hardware_models.md](hardware_models.md) and the cross-references from the per-track README files. For the **canonical reference data** (port addresses, opcode tables, memory maps), see [10_references/](../10_references/README.md).

---

## Article Roadmap

- §1 — Hardware terms (ULA, AY, contention, gate array, FPGA, Z80N, …)
- §2 — Display terms (ATTR, INK, PAPER, color clash, multicolor, scanline, …)
- §3 — Memory terms (bank, page, `#7FFD`, contention pattern, shadow screen, …)
- §4 — Storage terms (TR-DOS, ESXDOS, `.TAP`, `.TRD`, `.SNA`, …)
- §5 — Software and system terms (ROM routine, RST, IM2, ISR, beeper engine, tracker, …)
- §6 — Cultural and demoscene terms (Scene, 1-bit music, group, party, disk-mag, …)
- §7 — Track-specific terms (Pentagon timing, TS-Conf, BaseConf, Layer 2, copper, …)

---

## How to Use This Glossary

Entries are grouped by category and alphabetised within each category. Each entry follows the same format:

- **Term** — definition (2–4 sentences). *See `[target-article.md]` for the full article.*

Where a term has multiple meanings or is used differently across the three tracks (Original / Soviet Clones / New Gen), each variant is noted. Abbreviations are listed both under their short form (e.g., **ULA**) and spelled out at their full form (e.g., **Uncommitted Logic Array**) with a cross-reference.

---

## 1. Hardware Terms

- **Amstrad ASIC** — The custom gate-array chip (Amstrad part numbers 40084 and 40085) used in the ZX Spectrum +2A and +3. Replaced the discrete logic of the 128K/+2, changed the memory contention pattern from `6-5-4-3-2-1-0-0` to `1-0-7-6-5-4-3-2`, and added the `#1FFD` paging register with CP/M-compatible 64 KB mode. *See [zx_spectrum_plus2a_plus3.md](../02_hardware/original/zx_spectrum_plus2a_plus3.md).*

- **AY-3-8912** — The General Instruments (later Microchip) sound chip used in every ZX Spectrum from the 128K onward, in every Soviet clone with sound, and synthesized in essentially every FPGA Spectrum. Three-voice PSG (Programmable Sound Generator) with a noise generator and envelope. The Soviet clone is the Т34ВГ1; Yamaha's YM2149 is software-compatible and was used in some clones. *See [ay_3_8912.md](../06_sound/hardware/ay_3_8912.md).*

- **Beeper** — The 1-bit speaker driven directly by bit 4 of the `#FE` ULA port on every original Spectrum. No dedicated sound chip on the 48K — only the beeper. The demoscene's "1-bit music" genre is entirely beeper-driven. *See [beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md) and [1bit_music_scene.md](../07_demoscene/1bit_music_scene.md).*

- **Beta 128** — The standard Soviet-era disk interface, designed by Dmitry Mikhalchenko for the Pentagon. Based on the Western Beta interface but using the VG-93 (WD1793-compatible) FDC. The TR-DOS disk operating system runs on top of it. Built into nearly every Soviet clone. *See [beta_disk_interface.md](../03_io/storage/beta_disk_interface.md) and [trdos.md](../04_operating_systems/trdos.md).*

- **Copper** — The raster coprocessor in the ZX Spectrum Next, inspired by the Amiga copper. Executes a program of `WAIT` and `MOVE` instructions synchronized to the video beam, allowing per-scanline register changes for effects like raster bars, mid-scanline palette swaps, and dynamic layer mixing. *See [zx_next.md](../02_hardware/newgen/zx_next.md).*

- **Covox** — A simple resistor-ladder DAC attached to a Z80 parallel port, providing 8-bit sampled audio without a dedicated sound chip. Common on Soviet clones as an upgrade; also seen as the "SounDrive" interface. *See [covox_sounDrive.md](../06_sound/hardware/covox_sounDrive.md).*

- **Contention** — The CPU-cycle-stealing behavior introduced by the ULA's simultaneous memory access for video generation. During the upper-RAM area (and contended I/O), the Z80 is stalled for variable numbers of T-states. The dominant performance constraint on original Spectrums. *See [ula_contention.md](../02_hardware/original/ula_contention.md) and [contention_timing.md](../05_development/05_display_and_timing/contention_timing.md).*

- **DivIDE / DivMMC** — Two popular modern interfaces providing IDE/SD storage, typically with a `+3DOS`-like or `ESXDOS`-style resident ROM. The DivIDE was designed for the original Spectrum edge connector; the DivMMC uses the same protocol but runs at higher speeds. *See [divide_divmmc.md](../03_io/storage/divide_divmmc.md) and [esxdos.md](../04_operating_systems/esxdos.md).*

- **Ferranti ULA** — The original custom chip family (5C112, 6C001, 6C011, 7K010) used in the 16K/48K/128K Spectrums. Designed by Richard Altwasser and manufactured by Ferranti Semiconductors. Integrated video generation, memory arbitration, and I/O glue into a single 40-pin package. Chris Smith's *The ZX Spectrum ULA* book is the definitive reference. *See [ula_architecture.md](../02_hardware/original/ula_architecture.md).*

- **FPGA** — Field-Programmable Gate Array. The hardware basis of every modern Spectrum-compatible machine (ZX Uno, ZX Evolution, Karabas, ZX Spectrum Next) and every accurate emulator core (MiSTer, MiST, Antiriad's FPGA core). Allows cycle-exact reimplementation of ULA timing and CPU behavior. *See [zx_uno.md](../02_hardware/newgen/zx_uno.md), [zx_evo.md](../02_hardware/newgen/zx_evo.md), and [zx_next.md](../02_hardware/newgen/zx_next.md).*

- **Floating bus** — The phenomenon where reading an uncontended I/O port returns the byte currently being read by the ULA's video fetch (the pixel or ATTR byte being fetched for display). Used by some games and demos as a deterministic source of entropy or to detect vertical beam position. Behaviour differs significantly between original Spectrums (deterministic) and the +2A/+3 (effectively zero). *See [ula_architecture.md](../02_hardware/original/ula_architecture.md).*

- **Gate array** — A semi-custom integrated circuit with fixed macrocells that the customer configures with a final metal layer. The Amstrad ASIC is a gate array; the original ULA is technically a different technology (Uncommitted Logic Array). The terms are sometimes used loosely. *See [zx_spectrum_plus2a_plus3.md](../02_hardware/original/zx_spectrum_plus2a_plus3.md).*

- **General Sound (GS)** — A Soviet/Russian sound expansion card with a Z80 + 4× AY chips at its core, providing multi-channel sampled and PSG audio independently of the main CPU. Released by Khelson Ltd. in 1995. *See [gs_general_sound.md](../06_sound/hardware/gs_general_sound.md).*

- **Harlequin** — A modern discrete-logic recreation of the 48K Spectrum, designed by Chris Smith (author of *The ZX Spectrum ULA* book). Proves the ULA's exact behavior can be reconstructed in 74-series logic. *See [sizif_harlequin.md](../02_hardware/clones/sizif_harlequin.md).*

- **Kempston joystick** — The de facto joystick interface on Soviet clones (often built-in) and a common external interface on original Spectrums. Reads from port `#1F`. The "Atari-style" joystick pinout (9-pin D-sub) is used. *See [joystick.md](../03_io/peripherals/joystick.md) and [clone_joysticks.md](../02_hardware/clones/clone_joysticks.md).*

- **Layer 2** — The 256-color (8 bits per pixel) framebuffer introduced by the ZX Spectrum Next. Addressed in banks of 16 KB at `#0000-#3FFF` (selected via `#123B`). Provides the Next's most visually striking graphics mode. *See [next_graphics.md](../05_development/06_graphics/next_graphics.md) and [zx_next.md](../02_hardware/newgen/zx_next.md).*

- **ULA** (Uncommitted Logic Array) — See **Ferranti ULA**. The abbreviation is used far more often than the full form.

- **Z80** — The 8-bit CPU at the heart of every Spectrum and every Spectrum-compatible machine. Manufactured by Zilog from 1976; Soviet clones include the КР1858ВМ1 (T34VM1 is the Soviet 8080 clone — not the same thing). *See [z80_architecture.md](../01_cpu/z80_architecture.md) and [z80_instruction_set.md](../01_cpu/z80_instruction_set.md).*

- **Z80N** — The custom Z80-compatible CPU core in the ZX Spectrum Next. Binary-compatible with the original Z80 but adds new instructions including `MUL D,E`, `SWAPNIB`, `PIXELADD`, `MIRROR`, and several `LDIX`/`LDWS`/`LDIRSCALE` block operations. Designed by the Next team. *See [zx_next.md](../02_hardware/newgen/zx_next.md).*

---

## 2. Display Terms

- **ATTR byte** — One byte in the attribute file at `#5800-#5AFF` (32 bytes × 24 rows = 768 bytes) that describes the colors and effects for one 8×8 pixel cell of the display. Bit layout: `BFP7-PPP-III` (Bright, Flash, unused, Paper color bits 0–2, Ink color bits 0–2). *See [screen_access.md](../05_development/06_graphics/screen_access.md) and [color_palette.md](../10_references/color_palette.md).*

- **Attribute file** — The 768-byte region of RAM (`#5800-#5AFF`) containing the 32×24 grid of ATTR bytes, immediately following the pixel file. *See [memory_maps.md](../10_references/memory_maps.md).*

- **Attribute clash** — See **Color clash**.

- **Border** — The 32-column × 24-row region surrounding the 256×192 display area. Colored by writing bits 0–2 of port `#FE`. Has no associated memory — the color is held in a single register. Sometimes called "paper" in older literature, which is confusing; "border" is the modern term.

- **BRIGHT** — Bit 7 of the ATTR byte. When set, the ink and paper colors are taken from the "bright" variants of the palette (colors 8–15), giving an effectively 15-color palette (8 normal + 7 bright, since bright black is identical to black).

- **Color clash** — The unavoidable visual artifact caused by ATTR bytes controlling an entire 8×8 cell with only one ink and one paper color. When two differently-colored sprites occupy the same cell, one must give up its color. Also called "attribute clash". The defining visual constraint of the platform and a major driver of demoscene innovation. *See [multicolor_techniques.md](../07_demoscene/multicolor_techniques.md).*

- **FLASH** — Bit 6 of the ATTR byte. When set, the ink and paper colors of the cell swap at approximately 2 Hz (driven by the ROM's frame counter in the system variable `FRAMES`). Used for emphasis (e.g., the cursor).

- **Frame** — One complete video refresh, 1/50th of a second on original Spectrums (49.90 Hz on 128K/+2/+2A/+3; 50.08 Hz on 48K; 48.83 Hz on Pentagon). The frame is the fundamental timing unit for animation, music synchronisation, and game loops. *See [video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md).*

- **HiColor mode** (also "Timex HiColor") — An 8×1 pixel attribute mode introduced by the Timex Sinclair 2068 and adopted by some Soviet clones. Each ATTR byte covers two 8×1 cells instead of one 8×8 cell, dramatically reducing color clash at the cost of doubled attribute memory. Not supported on original Sinclair Spectrums. *See [clone_video_modes.md](../05_development/05_display_and_timing/clone_video_modes.md).*

- **HiRes mode** (also "Timex HiRes") — A 512×192 monochrome mode introduced by the Timex Sinclair 2068. Each 8×1 cell has a single color attribute that tints the entire cell, with bits of the attribute byte interleaved with the pixel bytes. Rarely used outside specific Timex software.

- **INK** — Bits 0–2 of the ATTR byte. The foreground color (text, sprite pixels set to 1) within the cell. Combined with BRIGHT bit gives an effective ink palette of 9 colors (8 normal + bright black is identical to normal black).

- **Multicolor** — A demoscene technique for changing the ATTR byte (or sometimes the palette register) multiple times per scanline, effectively giving per-pixel color and defeating color clash. Costs heavy CPU time inside the vertical blanking interval and requires precise cycle counting. Modern variants include **ULAplus** (per-scanline 64-color palette) and **BIFROST**/**nirvana+** engines. *See [multicolor_techniques.md](../07_demoscene/multicolor_techniques.md).*

- **Paper** — (1) Bits 3–5 of the ATTR byte: the background color of a cell. (2) Sometimes used (especially in older literature) to refer to the border color; this usage is deprecated — see **Border**.

- **Palette** — The 15-color (8 normal + 7 bright, since bright black = black) palette of the original Spectrum, stored as 3 bits per color in the ULA. The ZX Spectrum Next and Soviet clones with ULAplus add palette registers allowing 64 (ULAplus) or 256 (Next Layer 2) colors. *See [color_palette.md](../10_references/color_palette.md).*

- **Pixel file** — The 6144-byte region of RAM (`#4000-#57FF`) containing the 256×192 1-bit-per-pixel bitmap, organized as 24 rows × 8 third-rows × 32 bytes per row. The most counter-intuitive aspect of the layout is the third-row interleave. *See [memory_maps.md](../10_references/memory_maps.md) and [screen_access.md](../05_development/06_graphics/screen_access.md).*

- **Raster** — The beam position of the TV/monitor, expressed as (scanline, T-state-within-scanline). Raster effects are those synchronized to specific beam positions; the ZX Spectrum Next's copper is a hardware raster coprocessor.

- **Scanline** — One horizontal pass of the video beam. Original Spectrums have 312 scanlines per frame (48K) or 311 (128K/+2/+2A/+3); the Pentagon has 320. *See [video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md).*

- **ULAplus** — A widely-adopted 64-color palette expansion (6 bits per color, 4 palettes of 64 colors selectable per scanline or per 8×8 cell). Originally a community project; supported by most modern emulators and by several Soviet-clone FPGA cores. Not on original Sinclair Spectrums. *See [clone_video_modes.md](../05_development/05_display_and_timing/clone_video_modes.md).*

- **Vertical blank (VBlank)** — The period at the end of each frame when the video beam returns from the bottom of the screen to the top. During VBlank, the ULA does not access the upper RAM, so there is no memory contention. The 48K VBlank is 64 scanlines × 224 T-states/scanline = 14,336 T-states of "free" time per frame. The vertical blanking interrupt fires at the start of VBlank. *See [video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md) and [z80_interrupts.md](../01_cpu/z80_interrupts.md).*

---

## 3. Memory Terms

- **Bank** — A 16 KB region of RAM (or ROM) that can be paged into a fixed CPU address window. The 128K Spectrum has 8 RAM banks (bank 0 fixed at `#C000-#FFFF` for the screen, banks 0–7 pageable at `#C000`). Soviet clones extend this with up to 64+ banks (Pentagon 1024K, Kay 1024, Scorpion GMX). *See [memory_maps.md](../10_references/memory_maps.md).*

- **Bank switching** — See **Paging**.

- **Contention pattern** — The specific sequence of CPU delays applied during contended memory or I/O access on the original Spectrums: `6-5-4-3-2-1-0-0` for 48K/128K/+2, `1-0-7-6-5-4-3-2` for +2A/+3 (gated by `MREQ`), and **no contention** on Pentagon/ATM Turbo/Profi. The pattern is the dominant per-model difference for timing-critical code. *See [ula_contention.md](../02_hardware/original/ula_contention.md) and [clone_timing.md](../02_hardware/clones/clone_timing.md).*

- **Home bank** — The RAM bank currently paged into the `#C000-#FFFF` window on a 128K-style machine. On the 128K, this is selected by bits 0–2 of the `#7FFD` register. *See [memory_maps.md](../10_references/memory_maps.md) and [zx_spectrum_128.md](../02_hardware/original/zx_spectrum_128.md).*

- **Lower RAM** — The 16 KB region `#4000-#7FFF` on the 48K Spectrum, containing the screen, system variables, and BASIC workspace. On the 16K Spectrum, this region is not installed. Contended on original Spectrums because the ULA reads it for video. *See [memory_maps.md](../10_references/memory_maps.md).*

- **`#1FFD`** — The paging register added by the +2A/+3 Amstrad ASIC. Bit 0 selects the special paging modes (including a CP/M-compatible 64 KB configuration with all 4 ROM banks and no screen paging). *See [zx_spectrum_plus2a_plus3.md](../02_hardware/original/zx_spectrum_plus2a_plus3.md) and [io_port_map.md](../10_references/io_port_map.md).*

- **`#7FFD`** — The standard 128K paging register. Bit layout: bit 0–2 = RAM bank for `#C000` window, bit 3 = screen select (bank 5 or 7), bit 4 = ROM 0/1 select, bit 5 = disable further writes. Inherited by every later Sinclair model and by every Soviet clone. *See [zx_spectrum_128.md](../02_hardware/original/zx_spectrum_128.md) and [io_port_map.md](../10_references/io_port_map.md).*

- **`#EFF7`** — The extended memory paging register on the Pentagon 1024 and some other Soviet clones. Bit layout varies; on the Pentagon selects among the upper banks beyond the standard 128 KB. *See [pentagon_1024.md](../02_hardware/clones/pentagon_1024.md).*

- **Paging** — The act of switching a different bank of RAM or ROM into a fixed CPU address window. Sometimes called "bank switching". The 128K paging at `#7FFD` is the canonical example. *See [zx_spectrum_128.md](../02_hardware/original/zx_spectrum_128.md).*

- **Pixel file** — See Display Terms. Located in the lower RAM (`#4000-#57FF`) on bank 5 (or bank 7 when shadow screen is selected).

- **ROM 0 / ROM 1** — The two switchable 16 KB ROM banks in the 128K, +2, +2A, +3. ROM 0 contains the 128K editor + 48K BASIC API; ROM 1 contains the original 48K ROM for backward compatibility. Selected via bit 4 of `#7FFD`. *See [rom_128k.md](../04_operating_systems/rom_128k.md) and [rom_versions.md](../04_operating_systems/rom_versions.md).*

- **Shadow screen** — The alternative screen location in bank 7 (`#C000` window on a 128K) used when bit 3 of `#7FFD` is set. Used for double-buffering — code writes to bank 7 while the ULA displays bank 5, then flips. *See [zx_spectrum_128.md](../02_hardware/original/zx_spectrum_128.md).*

- **Upper RAM** — The 32 KB region `#8000-#FFFF` on the 48K Spectrum. Uncontended at `#8000-#BFFF`, contended at `#C000-#FFFF` (which is where the screen and ROM-related I/O live on a paged machine). Becomes the bank-paged region on the 128K.

---

## 4. Storage Terms

- **`+3DOS`** — The disk operating system in the +2A/+3 ROM, derived from AMSDOS and CP/M's BDOS. Operates on 3-inch floppy disks via the +3's internal drive. Snapshot format `.DSK` images are +3DOS-compatible. *See [plus3dos.md](../04_operating_systems/plus3dos.md) and [plus3_dos_format.md](../03_io/storage/plus3_dos_format.md).*

- **AMSDOS** — The Amstrad CPC's disk operating system; the ancestor of +3DOS. The file format is byte-compatible with +3DOS but the disk geometry differs (CPC uses 40 tracks × 9 sectors, +3 uses 40 tracks × 8 sectors of 512 bytes).

- **Beta 128 interface** — See Hardware Terms. The disk interface used with TR-DOS.

- **CSW** (Compressed Square Wave) — A tape archive format that stores tape signals as a sequence of pulse durations with run-length compression. More accurate than `.TAP` for tapes with non-standard loaders. *See [csw_format.md](../03_io/storage/csw_format.md).*

- **DivIDE / DivMMC** — See Hardware Terms. Modern interfaces for IDE/SD storage.

- **ESXDOS** — A resident DOS for the DivIDE/DivMMC, providing a Unix-like API (open/read/write/close) and a basic command shell. Developed by Garry Lancaster from 2005 onward. The de facto standard for modern IDE/SD storage on original Spectrums. *See [esxdos.md](../04_operating_systems/esxdos.md).*

- **FDI** (Flexible Disk Image) — A disk image format that captures low-level disk geometry (track/sector layout, sector IDs, and even some weak bits). Used by emulator authors for forensic-quality preservation of copy-protected disks. *See [dsk_fdi_formats.md](../03_io/storage/dsk_fdi_formats.md).*

- **MFM encoding** (Modified Frequency Modulation) — The magnetic encoding used on 3-inch (and 3.5-inch) floppies for the +3 and Beta 128 interface. Each bit cell uses clock and data transitions; the format is what FDC chips like the VG-93/WD1793 read/write. *See [mfm_encoding.md](../03_io/storage/mfm_encoding.md).*

- **PZX** — A modern tape archive format that separates the pulse-level signal from the block-level data, allowing both perfect playback and efficient storage. Less widely supported than `.TAP` or `.TZX`. *See [pzx_format.md](../03_io/storage/pzx_format.md).*

- **SCL** (Sinclair Clone List) — A Soviet-era disk image format used with TR-DOS. Contains a header with file metadata followed by raw sector dumps of all files in the disk. Simpler than `.TRD`. *See [trd_scl_formats.md](../03_io/storage/trd_scl_formats.md).*

- **SNA** — A snapshot file format that stores the complete machine state (registers, memory, banking). Originally from the Soviet emulators; widely supported. *See [sna_format.md](../03_io/snapshots/sna_format.md).*

- **TAP** — A tape archive format that stores the byte-level content of tape blocks. Each block is preceded by a 2-byte length. The simplest tape format; cannot represent non-standard loaders. *See [tap_format.md](../03_io/storage/tap_format.md).*

- **TZX** — A tape archive format that stores tape signals at the pulse level, capable of representing any tape including non-standard loaders and copy-protected tapes. The most accurate tape format; the de facto standard for preservation. *See [tzx_format.md](../03_io/storage/tzx_format.md).*

- **TR-DOS** — The disk operating system used with the Beta 128 interface on Soviet clones (and on Western Spectrums with the Western Beta interface). Written by Vladimir Yurzin (Badman) in the early 1990s. Snapshot format `.TRD` is a TR-DOS disk image. *See [trdos.md](../04_operating_systems/trdos.md) and [trd_disk_format.md](../03_io/storage/trd_disk_format.md).*

- **TRD** — The disk image format used with TR-DOS. Stores the disk as a sequence of 40-track × 16-sector dumps of 256 bytes each (640 KB total). *See [trd_disk_format.md](../03_io/storage/trd_disk_format.md).*

- **Z80** — (1) The CPU. (2) A snapshot file format introduced by the eponymous Z80 emulator, storing complete machine state with optional memory compression. Supports multiple snapshot variants for different Spectrum models. *See [z80_format.md](../03_io/snapshots/z80_format.md).*

---

## 5. Software and System Terms

- **Bank-switched code** — Code that lives in paged banks and uses banking tricks (self-modifying jumps, trampolines) to execute. Common on 128K-only software. *See [memory_maps.md](../10_references/memory_maps.md).*

- **Beeper engine** — A 1-bit music/sound synthesis routine that drives the beeper via bit 4 of port `#FE`. Engines include Follin's, Holtz, and Shiru's, supporting 2–6 voices with PWM, frequency modulation, and sampled drums. *See [beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md).*

- **ISR** (Interrupt Service Routine) — The routine called when the vertical blanking interrupt fires. The default 48K ROM ISR increments the `FRAMES` counter and reads the keyboard; games and demos replace it with custom code that does frame-synced effects. *See [z80_interrupts.md](../01_cpu/z80_interrupts.md).*

- **IM0 / IM1 / IM2** (Interrupt Modes 0, 1, 2) — The three Z80 interrupt modes. IM0 reads a byte from the data bus as an instruction (rarely used). IM1 calls `#0038` unconditionally (the 48K default). IM2 reads a vector from the data bus, combines it with the I register, and calls the address in the vector table — the most powerful mode and the basis for custom interrupt-driven effects on the Spectrum. *See [z80_interrupts.md](../01_cpu/z80_interrupts.md).*

- **NMI** (Non-Maskable Interrupt) — A Z80 interrupt that cannot be disabled by the IFF flag. On the Spectrum, the NMI line is wired to the `#0066` vector and was historically unused. Modern interfaces (DivIDE, DivMMC) use NMI to trigger their resident ROM/resident menu, and the ZX Spectrum Next has a programmable NMI button for debuggers. *See [z80_interrupts.md](../01_cpu/z80_interrupts.md).*

- **Player** — In the AY/beeper music context, the small machine-code routine that reads a stored score and writes to the AY/beeper registers in real time. Players are typically compiled into the parent program (game, demo, etc.) and called once per frame. *See [ay_player_routines.md](../06_sound/players/ay_player_routines.md) and [player_comparison.md](../06_sound/players/player_comparison.md).*

- **PT3** — The most popular Soviet-era AY music format. Files have extension `.pt3`; editors include Vortex Tracker II. The PT3 player is small (~600 bytes) and runs in a few hundred T-states per frame. *See [pt3_format.md](../06_sound/trackers_and_formats/pt3_format.md) and [vortex_tracker.md](../06_sound/trackers_and_formats/vortex_tracker.md).*

- **ROM routine** — A subroutine in the Spectrum's ROM, callable from machine code via a documented entry point. The 48K ROM contains many useful routines (`RST #10` for print, `BEEP` at `#03B5`, `CLS` at `#0DAF`, etc.) that games and demos call to save code size. *See [rom_routines.md](../10_references/rom_routines.md) and [rom_48k.md](../04_operating_systems/rom_48k.md).*

- **RST** (Restart instruction) — A single-byte Z80 instruction that calls a fixed address (`#0000`, `#0008`, `#0010`, … `#0038`). Used by the Spectrum ROM for compact calls to frequently used routines. *See [z80_instruction_set.md](../01_cpu/z80_instruction_set.md) and [rom_routines.md](../10_references/rom_routines.md).*

- **System variables** — A block of RAM at `#5C00-#5CBF` containing the ROM's working state: key buffer, cursor position, `FRAMES` counter, error code, channel definitions. Used by both BASIC programs and machine-code routines. *See [system_variables.md](../04_operating_systems/system_variables.md).*

- **Tracker** — An AY/beeper music editor used to compose the music stored in `.pt3`/`.asc`/`.stp` files. Examples: Vortex Tracker II (for `.pt3`), Sound Tracker, Pro Tracker, E-Tracker, ASC Sound Master. *See [tracker_history.md](../06_sound/trackers_and_formats/tracker_history.md).*

---

## 6. Cultural and Demoscene Terms

- **1-bit music** — Music synthesized using only the beeper (1-bit output), without a dedicated sound chip. A distinctive Soviet/Russian scene specialty. Pioneers include Follin, Holtz, and (Russian) Shiru. *See [1bit_music_scene.md](../07_demoscene/1bit_music_scene.md) and [beeper_synthesis.md](../06_sound/synthesis/beeper_synthesis.md).*

- **AY music** — Music composed for and played back on the AY-3-8912 (or YM2149) PSG. The dominant genre on original Spectrums from the 128K onward and on every Soviet clone. *See [ay_music_formats.md](../06_sound/trackers_and_formats/ay_music_formats.md).*

- **Disk-mag** — A magazine distributed as a disk image, with articles, graphics, and sometimes embedded music. The dominant publication form in the Soviet scene from the mid-1990s. Examples include *Spectrophoby*, *ZX-Format*, *Echo*, *Body*, *ZX-Power*, *Futuris*. *See [soviet_demo_scene.md](../07_demoscene/soviet_demo_scene.md).*

- **Demo** — A non-interactive audiovisual production, typically with self-contained code, music, and graphics. Demoscene productions range from 1 KB "intros" to multi-megabyte megados. *See [effects_catalog.md](../07_demoscene/effects_catalog.md) and [notable_demos.md](../07_demoscene/notable_demos.md).*

- **Demoscene** — The community of programmers, musicians, and graphics artists who create demos, intros, music disks, and related productions. On the Spectrum, the demoscene spans the Western scene (early 1990s), the Russian scene (1990s to present), and modern cross-platform activity. *See [demoscene_history.md](../07_demoscene/demoscene_history.md).*

- **Forever** — A long-running annual demoscene party held in Slovakia since 1996. One of the main ZX Spectrum-only parties in the West.

- **Group** — A team of sceners who collaborate on demos and other productions. Groups may include coders, musicians, graphics artists, and "swappers" (distributors). Famous Spectrum groups include ESI, AY Riders, Busy Bee, Empire, Flash Inc., Skrju, Chaos Constructions, X-Trade, Booze Design.

- **Handle** — A scener's pseudonym ("nom de scene"). Often stylised (mixed case, numbers, special characters). Multiple handles are common (a scener might have one for coding, one for music, one for graphics).

- **Intro** — A small demo, typically with size constraints (4K, 1K, 256 bytes). The demoscene's "size coding" specialty. *See [size_coding.md](../07_demoscene/size_coding.md).*

- **Party** — A demoscene gathering where productions are entered into competitions ("compos") and judged by attendees. Major Spectrum parties: **Forever** (Slovakia), **DiHalt** (Russia), **Chaos Constructions** (Russia), **CAFe** (Cuba; multiplatform), **Evoke** (Germany; multiplatform). *See [demoscene_platforms.md](../07_demoscene/demoscene_platforms.md).*

- **Scene** — The international demoscene community. Used as shorthand for "the demoscene" (e.g., "the Spectrum scene", "the Russian scene", "the 1-bit scene").

- **Scener** — A member of the demoscene.

- **TurboSound** — A multi-AY-chip configuration with two AY-3-8912/2149 chips (TS) for 6 simultaneous voices, or three chips (TS-FM). Standard on the ZX Evolution, ZX Uno, and ZX Spectrum Next. *See [turbosound.md](../06_sound/hardware/turbosound.md).*

---

## 7. Track-Specific Terms

- **BaseConf** — The original CPLD-based Pentagon-evolution configuration for the ZX Evolution board. Provides Pentagon-compatible memory paging, Beta 128, IDE, and SMUC ISA bridge. Older sibling of TS-Conf. *See [baseconf.md](../02_hardware/newgen/baseconf.md).*

- **Family A / B / C** — A loose categorisation of frame timing families used in this knowledge base: **Family A** (Sinclair-derived, 69,888–70,908 T-states/frame, includes 48K/128K/+2/+2A/+3, Scorpion, ATM Turbo), **Family B** (Pentagon-derived, 71,680 T-states/frame, includes Pentagon and most Soviet clones), **Family C** (divergent, e.g., Sprinter ~70 Hz, ATM Turbo 7 MHz). Software written for one family may not work on another. *See [video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md).*

- **Karabas** — A modern Russian-designed FPGA Spectrum recreation family (Karabas 128, Karabas 128 Rev C, Peridot). Aims for accurate 48K/128K behavior plus modern conveniences. *See [karabas.md](../02_hardware/newgen/karabas.md).*

- **Original** — In this knowledge base, the term refers to hardware designed and built by Sinclair Research or Amstrad under the Sinclair brand: 16K, 48K, Spectrum+, 128K, +2, +2A, +3. Every clone and every FPGA implementation aims to be compatible with at least one Original model.

- **Pentagon timing** — The de facto timing standard for the Russian scene: 320 scanlines per frame, 224 T-states per scanline, 71,680 T-states per frame, ~48.83 Hz frame rate, no memory contention. Software written for Pentagon timing will run too slowly on real Sinclair hardware. *See [clone_timing.md](../02_hardware/clones/clone_timing.md) and [pentagon.md](../02_hardware/clones/pentagon.md).*

- **Russian ROM** (also "Russian 48K ROM", "TR-DOS ROM") — Soviet/Russian replacement ROMs for the 48K mode, often adding built-in TR-DOS support, keyboard layout options (Latin/Cyrillic), and bug fixes. Several variants exist (TR-DOS 5.03, 5.04, 6.x; ProfROM for Scorpion). *See [rom_versions.md](../04_operating_systems/rom_versions.md).*

- **Sizif** — A modern FPGA-based recreation of the 48K/128K Spectrum with optional Pentagon extensions. Often paired with the Harlequin as a "Sizif-512". *See [sizif_harlequin.md](../02_hardware/clones/sizif_harlequin.md).*

- **Soviet clones** — The hardware track covering unauthorized Russian/Ukrainian/Belarusian/Polish Spectrum-compatible machines from 1987 onward: Leningrad, Pentagon, Scorpion, ATM Turbo, Kay, Profi, Byte, Hobbit, Quorum, LEC, Moscow, Balansir, and dozens more. Most were built from discrete TTL chips because Soviet hobbyists could not fabricate custom ULAs. *See [other_clones.md](../02_hardware/clones/other_clones.md) and [demoscene_history.md](../07_demoscene/demoscene_history.md).*

- **Sprinter** — A late-generation Spectrum-compatible machine by Peters Plus Ltd (Sprinter is the Peters+ logo). CPLD-based with a real Z80, SVGA output, ~70 Hz frame rate, and PC-like expansion. The most "PC-like" of the New Gen machines. *See [sprinter.md](../02_hardware/newgen/sprinter.md).*

- **TS-Conf** — The advanced CPLD configuration for the ZX Evolution board, adding tile-based video, hardware sprites, and 640×200 modes on top of BaseConf. The leading New Gen hardware for modern Russian demos. *See [ts_conf.md](../02_hardware/newgen/ts_conf.md).*

- **New Gen** — In this knowledge base, the term refers to modern (post-2010) Spectrum-compatible hardware: ZX Spectrum Next, ZX Uno, ZX Evolution (BaseConf/TS-Conf), Sprinter, Karabas, Harlequin, Sizif. Most are FPGA-based. *See [02_hardware/newgen/](../02_hardware/newgen/README.md).*

- **ZX Spectrum Next** — The flagship modern Spectrum-compatible machine, designed by Rick Dickinson, Jim Bagley, Garry Lancaster, Victor Trucco, Fabio Belavenuto, Henrique Olivi, and the Next team. FPGA-based (Spartan-6 LX16) with custom Z80N CPU at 28 MHz, Layer 2, hardware sprites, tilemap, copper, 3× AY (TurboSound), DMA sample playback, and a Raspberry Pi socket. Crowdfunded in 2017, shipped 2020. *See [zx_next.md](../02_hardware/newgen/zx_next.md).*

- **ZX Uno** — A Spanish-designed FPGA Spectrum (Altera Cyclone IV) with 28 MHz accelerator, expanded memory, and SD storage. The most popular New Gen machine in the Spanish-speaking scene. *See [zx_uno.md](../02_hardware/newgen/zx_uno.md).*

---

## Cross-References

### Within this section

- [history.md](history.md) — The full chronological narrative behind the terms in this glossary.
- [hardware_models.md](hardware_models.md) — The cross-track model catalog with comparison matrices.

### Deeper articles referenced from this glossary

- [01_cpu/z80_interrupts.md](../01_cpu/z80_interrupts.md) — IM0/IM1/IM2, ISR, NMI, vector tables.
- [02_hardware/original/ula_architecture.md](../02_hardware/original/ula_architecture.md) — Ferranti ULA internals, floating bus.
- [02_hardware/original/ula_contention.md](../02_hardware/original/ula_contention.md) — The contention pattern in detail.
- [02_hardware/clones/clone_timing.md](../02_hardware/clones/clone_timing.md) — Per-clone timing and contention differences.
- [04_operating_systems/trdos.md](../04_operating_systems/trdos.md), [esxdos.md](../04_operating_systems/esxdos.md), [plus3dos.md](../04_operating_systems/plus3dos.md) — The three main disk operating systems.
- [05_development/05_display_and_timing/video_frame_comparison.md](../05_development/05_display_and_timing/video_frame_comparison.md) — Per-model frame timing families (A/B/C).
- [06_sound/hardware/ay_3_8912.md](../06_sound/hardware/ay_3_8912.md) — AY chip internals.
- [07_demoscene/demoscene_history.md](../07_demoscene/demoscene_history.md) — The cultural context for Scene terminology.
- [10_references/io_port_map.md](../10_references/io_port_map.md) — The canonical port address reference.
- [10_references/memory_maps.md](../10_references/memory_maps.md) — The canonical memory map reference.
- [10_references/color_palette.md](../10_references/color_palette.md) — The canonical palette reference.

---

## Pitfalls

1. **"Spectrum" vs "Speccy" vs "Speccy scene".** "Spectrum" refers to the hardware. "Speccy" is informal and is used in community discussions, scene parties, and forum names. Use "Spectrum" in formal technical writing.

2. **"Pentagon timing" is not "Pentagon" the chip or the building.** Always capitalize "Pentagon" as the model name and clarify with "timing" or "architecture" when the meaning is ambiguous.

3. **"Rom" has three meanings.** (1) The 16 KB ROM chip image in the Spectrum. (2) A specific ROM *version* (48K, 128K, Russian, +3, etc.). (3) Colloquially, any firmware image ("the ProfROM for Scorpion"). Context determines which meaning.

4. **The ZX Spectrum Next is not "Spectrum 16/48/128".** It is a different hardware family. Software written for the Next using Z80N instructions or Layer 2 will not run on original Spectrums without an emulator.

5. **"AY" and "PSG" are sometimes used interchangeably but not always.** The AY-3-8910/8912/8913 are specific General Instruments chips; PSG (Programmable Sound Generator) is the chip family. The Yamaha YM2149 is pin-compatible and software-compatible with the AY but a different chip; the SN76489 is a *different* PSG and is not AY-compatible.

---

## References

- [history.md](history.md) — Narrative history behind the platform.
- [hardware_models.md](hardware_models.md) — Hardware model catalog.
- [AGENTS.md](../AGENTS.md) — Repository conventions, three-track awareness, port decoding rules.
- [10_references/README.md](../10_references/README.md) — Canonical reference data (port maps, memory maps, opcode tables, palette, ROM routines).
- Chris Smith, *The ZX Spectrum ULA: How to Design a Microcomputer* (2010) — The definitive reference on the Ferranti ULA and the source of much ULA-related terminology.
- The Complete Spectrum ROM Disassembly ( Logan & O'Hara, 1983) — Source for ROM routine names and entry points.
- [zx-pk.ru](https://zx-pk.ru) — The primary Russian-language forum for clone terminology and discussion.
- [speccy.info](https://speccy.info) — Russian-language wiki, especially useful for clone-specific jargon.
- [Demozoo](https://demozoo.org) — Cross-platform demoscene terminology reference.

---
