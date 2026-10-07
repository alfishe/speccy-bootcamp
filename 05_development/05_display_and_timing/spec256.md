[← Home](../../README.md) · [Display & Timing](README.md)

# Spec256 — 256 Colors Without New Hardware: the Z80_GFX Co-Processing Model

Spec256 is the strangest answer to attribute clash the Spectrum world ever produced: **256 colors per pixel with no new video hardware and no port writes** — because it is not a video mode at all. Created by Iñigo Ayo Blázquez's 1999 DOS emulator of the same name, Spec256 is an **emulator-level co-processing model**: a fictitious **64-bit-wide "Z80_GFX" processor** executes in lockstep with the real Z80, mirroring every instruction with 8-byte-wide operands. Every Z80 address has **8 shadow bytes** — one color plane per bit of the palette index. A game's *unmodified* bitmap-drawing code, the same `LD (HL),A` loops that move screen bytes, simultaneously moves 8 bytes of pre-authored color data per byte. The 256-color screen renders from the shadow ("GFX") memory instead of the ULA screen; activation is a user/emulator toggle (**F2/F3**), completely invisible to the running program.

The price: games need **authored color data** (`.gfx` files), **per-game correction profiles** (`.cfg`), and an emulator willing to run what the original readme called "several Z80 processors simultaneously" (486DX4-100 minimum in 1999).

> [!NOTE]
> This article documents the **execution model and formats**, verified against the original 1999 readme, EmuZWin's documentation (Vladimir Kladov), the zxpoly Java implementation and the FPGA cores' sources. For the multi-CPU platform that inspired the modern implementations, see [ZX-Poly](../../02_hardware/clones/zxpoly.md).

---

## The Execution Model

| Z80 (bitmap machine) | Z80_GFX (color machine) |
|---|---|
| `LD A,n` → A = *n* | A_gfx = 8 bytes, each = *n* (all planes get the same index bits) |
| `LD A,(HL)` → the bitmap byte | the 8 **plane bytes** at GFX[HL] — the colors of those 8 pixels |
| `LD (HL),A` → writes the bitmap byte | writes the 8 plane bytes → **the blit moves the sprite's colors too** |
| `XOR (HL)` and other RMW ops | per-plane 8-bit logical op on color bytes — usually visually meaningless; see profiles |

- Instruction fetch comes from the Z80's memory (same PC, same flag-driven control flow); all **data** reads/writes go to the GFX machine's own memory.
- **MEMORY_GFX = 65,536 addresses × 8 bytes = 512 KB**; shadow byte *p* of address *A* holds bit *p* of the palette index of every pixel covered by the bitmap byte at *A*. A "page" is 16,384 addresses × 8 = 128 KB, mapped through the standard 48K/128K window scheme (`#7FFD` banking included).
- Timing: per-instruction lockstep, same T-states.

### Register alignment — the per-game profiles

The color machine's flags and pointers can diverge from the bitmap machine's (a color byte's zero flag is not the bitmap byte's zero flag), so real implementations periodically **realign the GFX machine's registers** with the main CPU. zxpoly exposes this as `zxpAlignRegs` (e.g. `1PSsT`: realign **P**C every 1 instruction, **S**P/**s**tack semantics, **T**ake pointer registers from the main CPU); EmuZWin-era profiles carry the same idea, plus "leveled logicals" to tame the RMW ops. The defaults realign PC, SP and F (minus carry) every iteration; some games need the full profile — each game ships its correction settings in its `.cfg`.

## Palette and Files

- **Palette**: 256 entries; standard games ship a palette file, and EmuZWin added probe palettes and background layers (a full-size image behind the playfield).
- **`.gfx` file**: the persisted 48K-visible shadow memory (plane order per the format spec; one disputed bit-order detail is flagged in the references).
- **`.cfg` file**: the per-game profile — register alignment, logical-op leveling, activation.
- **Containers**: `.sze` snapshots (zxpoly) and EmuZWin's `.ezx` wrap the SNA/Z80 + `.gfx` + `.cfg` + palette set; the original DOS emulator used plain sidecar files. Known-good sizes: SNA = 49,179 bytes, GFX = 393,216 (the FPGA loader validates exactly these).

## Implementations

No 1999-era hardware exists — Spec256 became "silicon" only as FPGA soft-cores:

| Implementation | What it is |
|---|---|
| **Spec256 v1.2** (DOS, 1999) | the creator; 48K only, F2/F3 toggle ([archived site](http://web.archive.org/web/2022/http://www.emulatronia.com/emusdaqui/spec256/historia-eng.htm)) |
| **EmuZWin ≥2.4** (Kladov) | full support **plus authoring tools**: the GFX Editor for painting color data, backgrounds, `.ezx` packaging |
| **[raydac/zxpoly](https://github.com/raydac/zxpoly)** (Java) | Spec256 as a board mode: 1 master module + 8 GFX cores (the ZX-Poly scheduler), per-game database |
| **[oozx](https://github.com/fpetrola/oozx)** | "nine Z80s in lockstep"; 29 public game releases tested at 95–100% visual accuracy |
| **[GZX](https://github.com/jxsvoboda/gzx)** | renderer + palette + background loader (`video/spec256.c`) |
| **ReVerSE-U16 `u16_spec256`** (2016–17, [mvvproject](https://github.com/mvvproject/ReVerSE-U16)) | first FPGA core: 8× T80, one CPU per color plane; HDMI 640×480 |
| **DivGMX `divgmx_spec256`** (2017) | T80_GFX core, VGA, background layer |
| **karabas-go-core-spec256** (2026, Andy Karpov) | the U16 core ported to Karabas Go hardware ([core](https://github.com/andykarpov/karabas-go-core-spec256)) |

Not supported (verified): Xpeccy (its "256color" is IBM-PC VGA emulation), ZXMAK2, ZX Spin, zxsp, Spectaculator, UnrealSpeccy.

> [!WARNING]
> **Do not confuse Spec256 with RAM upgrades.** "Pentagon 256", "Scorpion 256T+" and similar names are memory extensions. Spec256 is the color co-processing model — no port exists to detect, no bit to set; a program literally cannot tell it is running in color.

## Emulation Notes

- The lockstep shadow-execution engine must mirror **every memory-affecting instruction**, including RMW opcodes — the classic hard part.
- The 512 KB GFX RAM is addressed by no Z80 instruction: it lives outside both the Z80 address space and any I/O latch, which stresses snapshot formats (a "device RAM region").
- Register-alignment profiles are part of the *game data*, not the model: the same emulator runs different games with different realign schedules.
- Each screen pixel maps to **two** addresses — a bitmap byte (master plane) and 8 plane bytes (color) — which any debug/pixel-probe tooling must understand.

---

## Cross-References

- [ZX-Poly](../../02_hardware/clones/zxpoly.md) — the 4-CPU platform whose scheduler powers the modern implementations
- [Pentagon 1024 — 16-color mode](../../02_hardware/clones/pentagon_1024.md) — 16 colors per pixel done in real memory-plane hardware
- [Clone video modes](clone_video_modes.md) — the conventional extension-family overview
- [TS-Conf](../../02_hardware/newgen/ts_conf.md) — the FPGA-era answer to the same desire

## References

- **Original**: Spec256 v1.2 `readme.txt` (Iñigo Ayo Blázquez, 09/1999), via the [archived Emulatronia site](http://web.archive.org/web/20060510135706id_/http://www.emulatronia.com:80/spec256/Sp256v12.zip)
- **EmuZWin** documentation (`256_color_games.htm`, `EZXFormat_Eng.htm`, Vladimir Kladov, 2004–2006, archived)
- **[raydac/zxpoly](https://github.com/raydac/zxpoly)**, **[fpetrola/oozx](https://github.com/fpetrola/oozx)**, **[jxsvoboda/gzx](https://github.com/jxsvoboda/gzx)** — open implementations (verified live, September 2026)
- **FPGA cores** — [mvvproject/ReVerSE-U16](https://github.com/mvvproject/ReVerSE-U16), [mvvproject/DivGMX](https://github.com/mvvproject/DivGMX), [andykarpov/karabas-go-core-spec256](https://github.com/andykarpov/karabas-go-core-spec256)
