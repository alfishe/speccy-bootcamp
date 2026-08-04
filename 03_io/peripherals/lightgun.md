[← Home](../../README.md) · [Peripherals](README.md)

# Magnum Light Phaser — ZX Spectrum Light Gun

## Overview

The **Magnum Light Phaser** is a light gun peripheral for the ZX Spectrum, released by **Amstrad** in **1987** (commercial launch 1987 in the UK, with wider European distribution in 1988 and the action-pack bundles shipping through 1989). It was Amstrad's **last first-party peripheral** for the ZX Spectrum line, and one of the very few light guns ever produced for an 8-bit home computer (the others being the Comvc Cheetah Defender, the Stack Light Rifle, and the official Commodore 64/128 and Amstrad CPC variants of the Magnum itself).

The Magnum detects where on the screen the user is pointing by sensing the **CRT raster beam's fly-back pulse** through a photo-sensor in the gun's muzzle. When the trigger is pulled, the game software reads the exact video-frame T-state at which the photo-sensor detected the bright pulse, and from that timing computes the (x, y) screen coordinate at which the gun was aimed. This is the same basic principle used by the NES Zapper, the Sega Light Phaser (Master System, 1986 — the Magnum's visual and functional inspiration), and the Atari XG-1 light gun.

This article covers the Magnum's hardware, the per-machine interface variants (+2/+3 AUX port vs 48K/128K edge connector), the raster-detection programming model, the full software library (around 15 known compatible titles), the rebranded variants (Trojan Phazer, Cheetah Defender, MARPES), and the modern reality of using a 1980s light gun in an LCD-display world.

---

## Why the Magnum Mattered

The late 1980s were the golden age of arcade light-gun games. **Operation Wolf** (Taito, 1987) was a smash arcade hit, and **Duck Hunt** (NES, 1985) plus the Master System's **Safari Hunt** (1986) had established the home-console light-gun genre. Amstrad, having acquired Sinclair Research in 1986, wanted a piece of this market for the ZX Spectrum — still the UK's best-selling home computer in 1987 — and the Magnum Light Phaser was their answer.

The Magnum mattered for several reasons:

1. **It brought arcade-style gun gaming to the home micro.** Before the Magnum, UK Spectrum owners wanting a light-gun experience had to buy a separate console (NES or Master System). After it, the Spectrum itself could do it — albeit with a smaller game library.

2. **It was widely distributed.** Amstrad's bundling strategy was aggressive: the Magnum was included in the £159 "James Bond 007 Action Pack" (a ZX Spectrum +2 plus the Magnum plus three Bond games) and the £199 "+3 Action Pack" (a +3 plus the Magnum plus six games). Standalone, it was £29.95 with six games. As a result, far more Magnums were sold than the small library of compatible software would suggest.

3. **It was Amstrad's last word on the Spectrum.** After the Magnum, Amstrad released no further first-party peripherals for the Spectrum line. The +3 (1987) was the last new Spectrum model. The Magnum is, in a sense, the period at the end of the Sinclair-peripherals sentence.

4. **It was the first light gun for a UK home computer.** The Cheetah Defender followed shortly after, but the Magnum was the first — and was the only one with serious marketing muscle behind it.

What the Magnum did **not** do was start a thriving UK light-gun-game ecosystem. The library stayed small (around 15 known compatible titles on the Spectrum, plus some that supported it incidentally). Developers found the raster-detection approach fiddly, the per-model timing differences painful, and the audience (Spectrum owners with CRT TVs who wanted gun games) small. Most Spectrum owners who wanted to play Operation Wolf at home used a joystick.

---

## Hardware

### Physical construction

The Magnum is a black plastic pistol, approximately 25 cm long, modeled (per Amstrad's marketing copy) on "Clint Eastwood's .44 Magnum" — the visual reference is to Dirty Harry. The grip is a 90-degree molded handle sized for a teenage-or-adult hand. The barrel has two sighting posts (a front blade and a rear notch) for aiming, though the actual aiming point is determined by the photo-sensor in the muzzle, not by the sights.

The gun's internals are minimal:

| Component | Function | Notes |
|-----------|----------|-------|
| **Photo-diode** (in the muzzle, behind a lens) | Detects the CRT raster beam's bright pulse | The lens focuses the photo-diode on a small area of the screen (~5 mm diameter at normal viewing distance), giving the gun its ~10-pixel resolution |
| **Trigger microswitch** | Signals "fire" | A simple momentary switch; debouncing is done in software |
| **Lens** (in front of the photo-diode) | Focuses light from the screen onto the sensor | Glued in place at the factory; alignment is critical |
| **Cable** (~1.5 m) | Connects gun to computer | Exits from the bottom of the grip |
| **(Sometimes) 9V battery compartment** | Power for the photo-diode amplifier | Present on the C64 version; not needed on the ZX Spectrum or CPC versions which draw power from the host machine |

The C64 version of the Magnum contains a 4011 NAND gate used as a photo-diode amplifier — an unconventional but functional choice. The ZX Spectrum version uses a simpler transistor amplifier, sufficient because the host machine provides clean `+5V` and `+9V` rails.

### Interface variants

The Magnum shipped in **three hardware interface variants**, each with a different cable and connector. The gun itself (photo-diode, trigger, lens) is identical across all three; only the host-side interface differs.

#### ZX Spectrum +2 / +2A / +2B / +3 / +3B — "AUX port" version

This is the most common variant. It plugs into the **AUX port** on the side of the +2 / +3 — a small 8-pin connector otherwise used for the +3's auxiliary peripherals (notably the +3's external keypad). The AUX port provides:

- `+5V` (current-limited via a 100 Ω resistor on the +3 motherboard)
- `GND`
- A trigger-sense line (read via a port decode)
- A light-sensor line (connected to the ULA's interrupt input, or to the gate array's LPEN-equivalent input on the +2A/+3)

This variant requires no external power supply — all power is drawn from the AUX port. It is the simplest variant to use: plug and play.

#### ZX Spectrum 48K / 128K "Toastrack" — "Edge connector + MIC" version

This variant uses a small interface box that plugs into the **ZX Bus edge connector** (for trigger-sense) and the **MIC socket** (for audio feedback in some games). The interface box contains a small amount of decoding logic and the trigger-sense flip-flop. This variant draws `+9V` from the edge connector for the photo-diode amplifier — which means it **does not work on the +2A/+3** (where the +9V rail was removed — see [zx_bus.md](zx_bus.md)).

#### Commodore 64 / 128 — "User port + Control port" version

This variant uses the C64's **user port** (for trigger, via the paddle X/Y lines) and the **control port** (for the light-sensor signal, which feeds the VIC-II chip's light-pen input). On the C64, the Magnum is functionally equivalent to a light pen — the VIC-II captures the beam position in hardware when the sensor pulses, and software reads the position from VIC-II registers `$D013` (X, divided by 2) and `$D014` (Y).

This C64 variant is included in this article for completeness and for the contrast it provides with the ZX Spectrum version's software-driven approach. The C64 hardware support (light-pen input on the VIC-II) makes C64 light-gun games much easier to write than their Spectrum equivalents.

### Photo-diode amplifier

The photo-diode in the Magnum produces a small current when illuminated by a bright CRT pixel. This current is amplified by a single-stage transistor amplifier inside the gun, producing a clean TTL-level pulse whenever the raster beam passes the gun's aim point. The amplifier's output drives either:

- The **ULA's interrupt input** on the 48K (causing a maskable interrupt at the moment of detection)
- The **gate array's lpen input** on the +2A/+3 (captured by the gate array, read by software via a port)
- The **VIC-II light-pen input** on the C64 (hardware position capture)

The ZX Spectrum's ULA was not designed with light-pen support in mind — unlike the VIC-II or the Amstrad CPC's CRTC, it has no dedicated "light pen position" register. The Magnum therefore has to use a software-driven detection scheme, described in the next section.

---

## How the Magnum Detects Position

Light guns work by **timing the delay** between a known reference point in the video frame (typically the start of vertical sync) and the moment the photo-sensor detects the bright raster beam. From that delay, the software can compute the (x, y) coordinate of the gun's aim point:

- The **y coordinate** is determined by the delay between vertical sync and the photo-sensor pulse, measured in scanlines. If the pulse comes 100 scanlines after VSync, the gun is pointing at scanline 100.
- The **x coordinate** is determined by the delay between horizontal sync (start of the scanline) and the photo-sensor pulse, measured in T-states (or pixel-clocks). If the pulse comes 100 T-states after HSync, the gun is pointing at column ~50 (each Spectrum pixel is 2 T-states wide — see [ULA Architecture](../../02_hardware/original/ula_architecture.md)).

### The ZX Spectrum's problem

The 48K/128K ULA has **no hardware support for this**. There is no "light pen" register that captures the beam position when the photo-sensor pulses. The ULA does generate a maskable interrupt (`/INT`) at a fixed point in the frame (the start of vertical blanking), but it cannot tell the software when the photo-sensor fired.

The Magnum's solution is to use the **light-sensor pulse itself as an interrupt source**. When the trigger is pulled and the photo-sensor sees the raster beam, the sensor's output drives the ULA's `/INT` line (via the AUX port or the interface box). The game software, which has been carefully counting T-states since the previous VSync, can read the current T-state count at the moment of the interrupt and thereby determine the y coordinate. The x coordinate is computed similarly from the offset within the current scanline.

This is delicate. The software has to:

1. **Disable the normal VSync interrupt** (or distinguish the sensor interrupt from the VSync interrupt — they look identical to the Z80)
2. **Pull the trigger** (read the trigger-sense port)
3. **Wait for the sensor interrupt** (which may take up to one full frame to arrive, ~20 ms)
4. **Read the current T-state count** (via the `R` register, or via carefully-timed code, or via the contention pattern — see [ULA Timing](../../02_hardware/original/ula_timing.md))
5. **Convert T-state count to (x, y) coordinates** using a per-model calibration table
6. **Re-enable the VSync interrupt** and return to normal operation

The "blank-the-screen-and-flash-white-targets" trick is needed because the photo-sensor detects **any bright pixel**, not just the one at the gun's aim point. If the screen is showing a normal game scene with many bright pixels, the sensor will pulse on the first one it sees each scanline, which is not necessarily the one the gun is pointing at. By blanking the screen to black and then making only the target rectangles white, the game ensures the sensor only pulses when the raster beam is actually on a target.

### Per-model timing

Because each Spectrum model has slightly different video timing (see [ULA Timing](../../02_hardware/original/ula_timing.md) and [Clone Timing](../../02_hardware/clones/clone_timing.md)), the T-state-to-coordinate conversion table is **per-model**. A Magnum game calibrated for the 48K will read positions incorrectly on the 128K, and completely incorrectly on the +2A/+3 (whose gate-array-based contention pattern is fundamentally different).

Most commercial Magnum games handle this by **asking the user which model they have at startup** and selecting the appropriate calibration table. A few (notably the Code Masters titles like *Billy the Kid* and *Bronx Street Cop*) auto-detect by measuring the frame T-state count.

---

## Software Library

The Magnum Light Phaser had a small but dedicated software library. Around **15 known ZX Spectrum titles** support it explicitly; a handful of others use it incidentally (e.g. as a joystick replacement). The list below is from contemporary magazine reviews (Crash, Sinclair User, Your Sinclair) and the Spectrum Computing database.

### The bundled six (Sinclair Action Pack — Lightgun Games)

These six titles shipped with the Magnum standalone and in the +2/+3 Action Packs. They were target-shooting games designed specifically to showcase the peripheral:

| Title | Developer | Year | Notes |
|-------|-----------|------|-------|
| **Bullseye** | Macsen Software | 1986 | Dart-throwing game based on the UK TV game show; light gun aims at the dartboard |
| **Missile: Ground Zero** | Software Creations | 1989 | Incoming-missile shooter; one of the more technically ambitious titles, rated 56% in Crash |
| **Operation Wolf** | Ocean Software (arcade port) | 1988 | The flagship title — port of the Taito arcade game. Best with the Magnum, but supports joystick too |
| **Robot Attack** | Zeppelin Games | 1989 | Robot-shooting gallery; rated 35% in Crash (the lowest-rated bundled game) |
| **Rookie** | Zeppelin Games | 1988 | Police-training-target shooter; rated 90% in Crash (the highest-rated bundled game) |
| **Solar Invasion** | Mastertronic | 1989 | Space-invaders-style alien shooter |

### Other Magnum-compatible Spectrum titles

These were sold separately and support the Magnum explicitly (usually via an in-game menu option):

| Title | Publisher | Year | Notes |
|-------|-----------|------|-------|
| **Billy the Kid** | Code Masters | 1989 | Western shooter; auto-detects the Magnum |
| **Bronx Street Cop** | Code Masters | 1989 | Side-scrolling action shooter with light-gun mode |
| **F-16 Fighting Falcon** | Code Masters | 1989 | Flight sim with optional light-gun enemy-targeting mode |
| **Jungle Warfare** | Toposoft | 1989 | Action shooter with Magnum support |
| **Lord Bromley's Estate** | The Dee Dee Corporation | 1990 | Part of the James Bond 007 Action Pack |
| **Make My Day** | The Dee Dee Corporation | 1990 | Western-themed shooting-gallery game (clint Eastwood reference) |
| **Q's Armoury** | The Software Exchange | 1989 | Part of the James Bond 007 Action Pack |
| **Super Car Trans Am** | Code Masters | 1989 | Driving game with optional light-gun combat mode |
| **The Living Daylights** | Domark | 1987 | James Bond tie-in; originally joystick-only, re-released with Magnum support |

### Promotional bundles

Amstrad released two major hardware-software bundles featuring the Magnum:

- **James Bond 007 Action Pack** (£159, 1989): ZX Spectrum +2 (grey) + Magnum Light Phaser + *The Living Daylights*, *Lord Bromley's Estate*, *Q's Armoury*. Marketed as the "ultimate secret agent bundle".
- **ZX Spectrum +3 Action Pack** (£199, 1989): ZX Spectrum +3 + Magnum + the standard six-game Sinclair Action Pack cassette. The premium home-computer bundle of 1989.

### The Russian clone situation

The Magnum was a UK/European product and was never officially distributed in the Soviet Union. However, the hardware is simple enough that several Russian clone manufacturers produced compatible light guns in the 1990s, usually as part of a multi-peripheral adapter or as a stand-alone unit cabled to the Pentagon's edge connector. Software support on Russian clones is limited to ports of the original Spectrum titles; no original Russian Magnum-targeted games are known.

---

## Rebranded and Compatible Variants

The Magnum's hardware was widely rebranded and cloned. The same physical gun appears under several names:

| Variant | Marketing region | Connector | Notes |
|---------|------------------|-----------|-------|
| **Magnum Light Phaser** (Amstrad/Sinclair) | UK, Europe | Per-machine (AUX, edge, or user port) | The original; 1987-1989 |
| **Trojan Phazer** (Trojan) | UK, Europe | Per-machine | White plastic instead of black; otherwise identical. Compatible with all Magnum software. |
| **Cheetah Defender** (Cheetah Marketing) | UK | Per-machine | Independent design but fully Magnum-compatible. The Defender was marketed for the Spectrum, C64, and Amstrad CPC separately. |
| **MARPES Light Gun** | Europe (Germany?) | Per-machine | Clone of the Cheetah Defender; marketed for the NES as well. Notable for unusually high build quality: micro-switch trigger, glued lens, internal shielding, internal 4011 NAND amplifier. PCB has "ATARI" markings (likely a sourced OEM part). |
| **Stack Light Rifle** (Stack Computer Services) | UK | ZX Bus edge connector | A different, more sophisticated design that emulates a Kempston joystick in light-gun mode. **Not** Magnum-compatible — uses a different protocol. |

For software purposes, only the Magnum, Trojan Phazer, Cheetah Defender, and MARPES are interchangeable. The Stack Light Rifle uses a completely different interface and is incompatible.

---

## Modern Use and the LCD Problem

The Magnum Light Phaser — like all CRT-based light guns — **does not work on modern LCD, plasma, or OLED displays**. This is a fundamental hardware limitation, not a software one, and there is no easy fix.

### Why LCDs don't work

The Magnum's photo-diode detects the **single bright pixel** of the CRT raster beam as it sweeps across the screen at the speed of light. An LCD panel, by contrast, illuminates the entire frame simultaneously (or in large blocks) at the start of each frame, with no moving "beam" to detect. The Magnum's photo-diode, when pointed at an LCD, sees either a constant brightness (no pulse to detect) or a single frame-wide pulse (no spatial information).

This is the same problem that affects the NES Zapper, the Sega Light Phaser, and every other CRT-based light gun. There are no software-only solutions.

### Workarounds

There are three known ways to use a Magnum (or any CRT light gun) in the modern era:

1. **Use a CRT TV.** This is the obvious answer and the one most Magnum owners use. A working CRT with a SCART or composite input gives the authentic Magnum experience. CRT availability is decreasing but they are still obtainable.

2. **Use a CRT-emulating display.** A few modern displays (notably the Sony BVM and PVM professional CRTs, and the now-discontinued Sony FW-900 computer monitor) have sufficiently CRT-like behavior to work with some light guns. These are expensive and rare.

3. **Use a modern "light gun" replacement.** Several companies make modern light guns that work on LCDs by using two IR LEDs mounted on the display edges and a camera in the gun to triangulate position. Examples include the **GUN4IR** and the **Sinden Lightgun**. These are not Magnum-compatible out of the box — they emulate modern consoles (PS2, Wii) — but enthusiasts have built adapter boards that convert their output to the Magnum's trigger-and-sensor protocol.

4. **Emulate.** Most ZX Spectrum emulators (Fuse, ZEsarUX, Spectaculator) support the Magnum in software, mapping the mouse position to the gun's position and the mouse button to the trigger. This is the lowest-friction way to play Magnum-compatible games today, though obviously it lacks the physical-gun experience.

### Magnum in 2024 and beyond

Working Magnum Light Phasers in good condition sell for £50–£100 on eBay — substantially more than the £10–£20 the Planet Sinclair site lists as "typical value" (that figure is from the late 1990s). The +2/+3 AUX-port variant is the most common and most sought-after; the 48K edge-connector variant is rarer. The C64 and CPC variants turn up occasionally.

For software preservation, all known Magnum-compatible titles are available from the Spectrum Computing archive and World of Spectrum. Playing them in an emulator is straightforward. Playing them on original hardware requires a CRT TV, a working Magnum of the correct variant, and a Spectrum of the matching model — a non-trivial setup in 2024.

---

## Common Pitfalls

| # | Pitfall | Consequence | Fix |
|---|---------|-------------|-----|
| 1 | **Pointing the Magnum at an LCD/plasma/OLED TV** | No detection — the photo-diode sees either constant brightness or a frame-wide flash with no spatial information | Use a CRT. There is no software fix. (See [video_output.md](video_output.md) for the CRT-vs-LCD issue at the display level.) |
| 2 | **Assuming the +2A/+3 AUX port is identical to the +2 AUX port** | Cable may fit but pinout differs across the +2 grey, +2A, and +3 — particularly the +12V and audio pin positions | Verify the exact pinout for the specific model before plugging in. The +2 grey and +2A/+3 AUX ports are *physically* compatible but *electrically* different. |
| 3 | **Using a 48K-targeted Magnum game on a 128K / +2 / +2A / +3** | Wrong coordinates — the per-model calibration table differs because each Spectrum model has different video timing | Use games that auto-detect (Code Masters titles) or that prompt for the model at startup. See [ULA Timing](../../02_hardware/original/ula_timing.md) and [Clone Timing](../../02_hardware/clones/clone_timing.md). |
| 4 | **Expecting the Magnum to work like the C64 light pen** | It does not — the ZX Spectrum ULA has no light-pen position register; all position capture is in software via T-state counting | Read the "How the Magnum Detects Position" section above. The C64's VIC-II hardware support makes C64 light-gun games much easier to write. |
| 5 | **Mixing up Magnum, Trojan Phazer, Cheetah Defender, MARPES, Stack Light Rifle** | The first four are interchangeable; the Stack Light Rifle is a different design entirely (emulates a Kempston joystick in light-gun mode) and is **not** Magnum-compatible | Check the label. If it says "Stack", it's a different protocol. |
| 6 | **Pulling the trigger with no bright target on screen** | Photo-sensor never pulses, software hangs waiting for the sensor interrupt (typically with a frame timeout) | Most games time out after one frame (~20 ms) and report a "miss". Some buggy titles hang indefinitely. |
| 7 | **Aiming at a bright background element (a window, lamp reflection) instead of the white target block** | Photo-sensor pulses on the wrong bright pixel — game registers a hit at the wrong coordinate | The "blank-the-screen-and-flash-the-target" trick exists for this reason; do not bypass it in homebrew code. |
| 8 | **Assuming Russian clone light guns are Magnum-compatible** | They usually are *electrically* compatible (same port decode) but may use different trigger-sense ports depending on the clone's I/O map | Test on a case-by-case basis. Pentagon and Scorpion convention differs. |
| 9 | **Using a Magnum with a SCART cable that wires composite video (pin 20) instead of composite sync (pin 4) to the AUX port's sync line** | Detection unreliable on some CRTs — composite video contains active picture that the gun's photo-diode may pick up as a false target pulse | Use the proper Magnum cable, not a generic +2/+3 RGB SCART cable. See [video_output.md](video_output.md) for SCART pinout details. |
| 10 | **Assuming the Magnum works through RF** | It does, but with significant lag and noise — the RF modulator adds a frame of latency and the demodulator adds noise to the luminance signal, both of which corrupt the timing measurement | Use composite or RGB output (128K / +2 / +2A / +3 only — 48K is RF-only without modification). |
| 11 | **Expecting modern emulators to support the Magnum out of the box** | Most do (Fuse, ZEsarUX, Spectaculator) but the mouse-to-gun mapping has to be configured per-game because the calibration tables differ | Configure the emulator's "light gun" input device explicitly. |
| 12 | **Treating the Magnum's `R`-register T-state counter as cycle-accurate** | It is not — `R` is only 7 bits and refreshes every 128 M-cycles; high-coordinate values overflow | Use frame-relative T-state counting via timed loops, not the `R` register, for the y coordinate. |

---

## When to Use What

| Use case | Recommendation |
|----------|----------------|
| **Playing Magnum games on original hardware in 2024+** | Find a working CRT TV with composite or SCART input; obtain a +2 or +3 with the AUX-port Magnum variant (the most common). Forget the 48K edge-connector variant unless you already have a 48K and a CRT. |
| **Playing Magnum games without original hardware** | Use Fuse, ZEsarUX, or Spectaculator with the Magnum emulated as a mouse-mapped light gun. ROM and TAP images are on Spectrum Computing and World of Spectrum. |
| **Writing new light-gun homebrew today** | Strongly consider the Sinden Lightgun or GUN4IR (which work on LCDs via IR LED bars) instead of the Magnum — the Magnum's CRT-only constraint severely limits your audience. If you must target the Magnum, write the detection code to auto-detect the Spectrum model (measure frame T-state count) and ship per-model calibration tables. |
| **Buying a Magnum today** | Verify the variant matches your Spectrum model: AUX port for +2/+2A/+2B/+3/+3B, edge-connector box for 48K/128K Toastrack. Test the trigger microswitch and the photo-diode (point at a bright CRT pixel and listen for the sensor pulse via the trigger-sense port). Expect to pay £50–£100 in 2024. |
| **Distinguishing Magnum from rebranded variants** | The original Magnum is black plastic with "MAGNUM LIGHT PHASER" and the Amstrad/Sinclair logo on the grip. The Trojan Phazer is the same hardware in white plastic. The Cheetah Defender is a different shell but the same trigger-and-sensor protocol. The MARPES has "ATARI" PCB markings. The Stack Light Rifle is incompatible — different protocol entirely. |

---

## Comparison with Other Light Guns

The Magnum was one of several 8-bit light guns. The most relevant comparisons:

| Light gun | Host | Year | Detection method | Hardware position capture? | Works on LCD? |
|-----------|------|------|------------------|----------------------------|---------------|
| **Magnum Light Phaser** | ZX Spectrum (+2/+3 AUX), C64, Amstrad CPC | 1987 | Photo-diode senses raster beam; Spectrum version is software-driven, C64 version uses VIC-II LPEN hardware | Spectrum: no. C64: yes (VIC-II `$D013`/`$D014`). CPC: yes (CRTC `$46`/`$47`). | No |
| **Stack Light Rifle** | ZX Spectrum (ZX Bus edge) | 1988 | Emulates a Kempston joystick — the gun encodes its aim point as a joystick position via internal decoding hardware | N/A (gun is the decoder) | No (still needs CRT, though some later Stack variants supported CRT-only LCD workarounds) |
| **NES Zapper** | Nintendo Entertainment System | 1985 | Photo-diode senses raster beam; the NES PPU captures a "bright pixel detected" flag in `$2002` bit 3 | Partial — PPU sets a flag, but software must still time | No |
| **Sega Light Phaser** | Sega Master System | 1986 | Same as NES Zapper — software-timed photo-diode pulse | Partial | No |
| **Atari XG-1** | Atari 2600 / 7800 / 8-bit | 1987 | TIA/GTIA light-pen input on some models; joystick-button-only on others | Varies | No |
| **C64 light pen** (Commodore 1351 mouse in pen mode, or third-party pens) | C64 | 1984+ | VIC-II hardware light-pen input — `$D013` (X/2), `$D014` (Y) latched on sensor pulse | Yes — full hardware capture | No |
| **Amstrad CPC light pen** | Amstrad CPC 464/664/6128 | 1985+ | CRTC type 1 (404086059) hardware LPEN input — `$46`/`$47` X, `$47` Y latched on sensor pulse | Yes — full hardware capture | No |
| **Sinden Lightgun** | Modern PC, Raspberry Pi | 2014+ | Camera in the gun tracks IR LED bars mounted on the display edges; sub-pixel position via triangulation | Yes — but requires IR border | **Yes** (with IR border) |
| **GUN4IR** | Modern PC, Wiimote hardware | 2015+ | Wiimote camera tracks IR LEDs; custom firmware | Yes — IR-based | **Yes** (with IR border) |

The Magnum's distinctive position in this landscape:

- **Software-driven on the ZX Spectrum, hardware-driven on the C64 and CPC.** The same physical gun is much easier to write games for on the C64/CPC because those machines have hardware light-pen registers; on the Spectrum, the software has to do all the timing work.
- **CRT-only.** Like all 1980s light guns, the Magnum cannot work on modern displays. The Sinden and GUN4IR are the modern alternatives.
- **Small library.** Around 15 known compatible Spectrum titles, versus hundreds for the NES Zapper. The Magnum was a niche peripheral even in its day.

---

## Modern Analogies

The Magnum's design pattern — **"a passive optical sensor + a clever software protocol that makes up for missing hardware support"** — recurs throughout retro and embedded computing:

- **Software-driven light pens on machines without hardware LPEN.** The Apple II and the IBM CGA card both have no hardware light-pen register; light pens for these machines work on the same software-timed principle as the Magnum.
- **The Wiimote's IR camera.** Modern "light guns" (Sinden, GUN4IR) invert the Magnum's design: instead of a passive photo-sensor in the gun pointing at a moving raster beam, they put a camera in the gun looking at stationary IR LEDs at the display edges. Same end result (position triangulation), completely different physical principle.
- **Capacitive touch sensing on early PDAs.** The Apple Newton's touch screen used a similar software-driven scanning approach to detect stylus position, before resistive and then capacitive multi-touch hardware took over.
- **Camera-based QR code scanners.** The "decode position from a sensed pulse" pattern reappears in modern fiducial-marker tracking (AprilTag, ArUco), where a camera detects known patterns and software computes the camera's pose.

The Magnum is, in a sense, the ZX Spectrum equivalent of an early light-pen peripheral: a piece of clever engineering that works around the host machine's missing hardware support by cleverly using the resources that *are* available — in this case, the ULA's interrupt and the Z80's cycle-counter.

---

## Cross-References

- [zx_bus.md](zx_bus.md) — the ZX Bus edge connector that the 48K/128K Magnum interface box plugs into; the `+9V` rail it depends on (removed on +2A/+3)
- [video_output.md](video_output.md) — the physical video output path on each Spectrum model; why the Magnum cannot work through RF and prefers composite/RGB; the CRT-vs-LCD issue at the display level
- [joystick.md](joystick.md) — the joystick interfaces that the Stack Light Rifle emulates (Kempston at `#1F`); the alternative input device for "light gun" games that support joystick mode
- [mouse.md](mouse.md) — Kempston Mouse ports (`#FBDF`/`#FFDF`/`#FADF`); the analogous absolute-position input device for pointing
- [ULA Architecture](../../02_hardware/original/ula_architecture.md) — the ULA's `/INT` line that the Magnum's sensor drives; the lack of any light-pen register in the ULA's design
- [ULA Timing](../../02_hardware/original/ula_timing.md) — per-model video timing (the source of the Magnum's per-model calibration tables); the `R`-register cycle-counting trick; the contention pattern that some Magnum detection schemes exploit
- [Clone Timing](../../02_hardware/clones/clone_timing.md) — Russian clone video timing; why a Magnum calibrated for an original Sinclair Spectrum will read wrong on a Pentagon or Scorpion
- [02_hardware/original/keyboard_matrix.md](../../02_hardware/original/keyboard_matrix.md) — for context on the Spectrum's I/O port decoding conventions (low address bits select row/column; same convention reused by the AUX port's trigger-sense decode)

---

## Primary Sources

- **Wikipedia** — ["Magnum Light Phaser"](https://en.wikipedia.org/wiki/Magnum_Light_Phaser) (archived; the live article was redirected). Overview, release date, software library, rebranded variants.
- **CPCWiki** — [Magnum Light Phaser](https://www.cpcwiki.eu/index.php/Magnum_Light_Phaser). Hardware description, photo-diode amplifier details, C64/CPC variants.
- **Planet Sinclair** — [Peripherals: Magnum Light Phaser](https://www.sinclair.hu/peripherals.html). Original 1990s pricing and availability; per-model variant list.
- **Janderogee.com** — [C64 Light Gun Pinout](https://janderogee.com/projects/c64_lightgun/c64_lightgun.htm). C64 user-port pinout; the 4011 NAND amplifier schematic; trigger-sense wiring.
- **Grokipedia** — [Magnum Light Phaser](https://grokipedia.com/wiki/Magnum_Light_Phaser). Independent summary; cross-check of release dates and bundle contents.
- **Crash Magazine** issue 51 (1988) — review of the Magnum's launch titles (*Rookie* 90%, *Operation Wolf* 79%, *Missile: Ground Zero* 56%, *Robot Attack* 35%). Contemporary critical reception.
- **Sinclair User** issue 76 (1988) — Amstrad's launch advertising for the Magnum and the James Bond 007 Action Pack.
- **Your Sinclair** issue 32 (1988) — round-up of light-gun games, including the Cheetah Defender comparison.
- **Spectrum Computing archive** — [spectrumcomputing.co.uk](https://spectrumcomputing.co.uk). Searchable database of all known Magnum-compatible titles; TAP and TZX images for software preservation.
- **World of Spectrum** (archived at the Internet Archive) — historical magazine archive; per-title review scores; bundle contents.

---

*Article 10 of 10 in the [Peripherals](README.md) section. This is the final article in the peripherals series — covering Amstrad's last first-party Spectrum peripheral, the Magnum Light Phaser, and its software-driven light-gun detection scheme that worked around the ZX Spectrum ULA's lack of any hardware light-pen register.*
