[← Home](../../README.md) · [Software Emulators](README.md)

# Emulator Comparison — Choosing a ZX Spectrum Emulator

The ZX Spectrum has been emulated in software since the early 1990s, with dozens of emulators having been written over the intervening three decades. Today, a handful of **actively-maintained, high-quality emulators** dominate the scene, each with its own strengths: some emphasise **accuracy** (cycle-exact timing, perfect compatibility with the original hardware), others **features** (beyond-Spectrum capabilities, modern development tools), and others **portability** (running on every desktop and mobile platform).

This article provides a comprehensive comparison of ZX Spectrum emulators, helping you choose the right tool for your use case — whether that's casual retro gaming, software development for original hardware, demoscene production, preservation and archiving, or hardware research. Individual emulators have their own dedicated deep-dive articles: see [fuse.md](fuse.md), [zesarux.md](zesarux.md), and [cspect.md](cspect.md).

For technical discussion of emulation accuracy and the specific challenges of cycle-exact Spectrum emulation, see [cycle_exact_accuracy.md](cycle_exact_accuracy.md). For test suites used to validate emulator correctness, see [test_suites.md](test_suites.md).

---

## The Emulator Landscape

### Why So Many Emulators?

The ZX Spectrum is one of the most emulated computers in history, for several reasons:

- **Simplicity of the hardware** — the Spectrum is a Z80 CPU plus a custom ULA (Uncommitted Logic Array) plus a few peripheral chips (AY-3-8912 sound, Kempston joystick interface, etc.). The architecture is small enough that a single developer can write a working emulator in a few weeks.
- **Nostalgia and cultural significance** — the Spectrum was the dominant home computer in the UK and many other markets, with millions of former users who want to relive their childhood software libraries.
- **Demoscene activity** — the Spectrum demoscene has remained active for 30+ years, with emulator-based development being far easier than developing on real hardware.
- **Historic importance** — emulators are essential tools for preserving and studying the Spectrum's software heritage.

The result is that new Spectrum emulators have been written for almost every major computing platform: DOS, Windows, Linux, macOS, Android, iOS, web browsers, even embedded systems and other retro computers. The scene has consolidated somewhat in the 2010s–2020s, but the major surviving emulators represent **decades of accumulated refinement**.

### Categories of Emulators

Modern Spectrum emulators can be grouped into several categories:

**1. Cross-platform accuracy-focused emulators** — written to run on multiple operating systems with an emphasis on cycle-exact timing and faithful hardware reproduction. Examples: **Fuse**, **ZEsarUX**. These are the standard choice for serious Spectrum work.

**2. Windows-focused emulators** — optimised for Windows, often with rich feature sets (debuggers, development tools, modern UI). Examples: **Spectaculator**, **UnrealSpeccy**, **CSpect**.

**3. Modern, Next-aware emulators** — emulators that include support for the ZX Spectrum Next and its enhanced capabilities (Z80N CPU, layer 2 graphics, etc.). Examples: **CSpect**, **ZEsarUX**, **UnoSCII**.

**4. Web-based emulators** — run in a browser via WebAssembly or JavaScript. Examples: **JSSpeccy**, **Speccy.net**, various retroweb projects.

**5. Mobile emulators** — Android and iOS ports of desktop emulators or standalone mobile projects. Examples: **Speccy** (Marat Fayzullin's mobile port), **Spectaculator Mobile**, **Fuse Android port**.

**6. Retro-platform emulators** — emulators that run *on* other retro platforms, e.g., a Spectrum emulator running on a Commodore 64 or Amiga. Mostly curiosities, but technically interesting.

**7. Embedded / console emulators** — for platforms like the GP2X, Pandora, PSP, Nintendo DS, etc. These are usually ports of desktop emulators, adapted to the platform's controls and screen.

This article focuses primarily on the first three categories — the actively-maintained desktop emulators that are the workhorses of the modern Spectrum scene.

---


## The Major Emulators

### Fuse (Free Unix Spectrum Emulator)

**Fuse** is the workhorse cross-platform Spectrum emulator. Originally developed for Linux by **Philip Kendall** (first released 1999), Fuse has since been ported to macOS, Windows, Android, and other platforms. It is **open-source** (GPL) and forms the basis of several derivative projects.

**Strengths**:

- **Cross-platform** — runs on Linux, macOS, Windows, Android, and more
- **Highly accurate** — passes the major test suites (see [test_suites.md](test_suites.md)) for the Spectrum 16K/48K/128K/+2/+2A/+3 and many clones
- **Open source** — actively developed by a community
- **Comprehensive hardware support** — emulates Interface 1, microdrives, ZX Net, +D, Opus, Kempston, Fuller, Multiface, Spectrum +3e, Russian clones (Pentagon, Scorpion), Brazilian Spectrum clones
- **Mature feature set** — save states, screenshots, video recording, debugging tools, RZX playback (for verified speedruns)

**Weaknesses**:

- **UI varies across platforms** — the GTK+ UI on Linux differs from the Win32 UI on Windows, and the macOS UI is yet another variant
- **No ZX Spectrum Next support** — Fuse focuses on original Sinclair and clone hardware, not the modern Next
- **Development has slowed** — releases are less frequent than in the 2000s

**Best for**: cross-platform users, accuracy-focused testing, hardware research, library development.

### ZEsarUX

**ZEsarUX** (ZX Spectrum Emulator Revised And Universal eXtension) is developed by **Cesar Hernandez Nuñez** (Chernandezba), starting in 2013. It runs on Linux, macOS, Windows, and others, and has a strong focus on **faithful emulation of all Spectrum variants and clones**, with extensive **hardware debugging tools**.

**Strengths**:

- **Broadest hardware coverage** of any emulator — Spectrum 16K/48K/128K/+2/+2A/+3, Inves Spectrum+, TK90X, TK95, Pentagon, Scorpion, ATM Turbo, ZX-Uno, Chrome, BaseConf, Spectrum Next, and many more
- **Excellent debugging tools** — register view, memory map view, disassembler, breakpoints, watchpoints, ML (machine learning)-assisted reverse engineering tools
- **TSConf and other advanced configurations** — supports modern Spectrum-compatible hardware like the TSConf (a Russian ZX-Next-class machine)
- **Real-time assembly editing** — modify running code, see results immediately
- **ZX Spectrum Next support** — partial implementation of the Next's enhanced features

**Weaknesses**:

- **UI is less polished** than commercial Windows emulators — the interface is functional but visually dated
- **Configuration complexity** — the huge number of options can be overwhelming
- **Linux/Unix-oriented** — Windows builds exist but Linux is the primary platform

**Best for**: reverse engineering, demoscene production on unusual hardware, deep debugging, hardware research.

### CSpect

**CSpect** is a modern Windows-based emulator developed by **Mike Dailly** (a former DMA Design / Rockstar North programmer with credentials including Lemmings and GTA). CSpect is distinguished by its **ZX Spectrum Next support** — it is one of the two reference emulators for the Next (alongside ZEsarUX).

**Strengths**:

- **Best ZX Spectrum Next emulation** — actively tracks NextOS firmware updates and the Next hardware specification
- **Modern, polished UI** — Windows-native interface with tabs, dockable windows, modern widgets
- **Excellent development tools** — disassembler, memory viewer, tile/sprite viewers, layer-2 graphics viewers, breakpoint support
- **Active development** — frequent updates aligned with NextOS releases
- **Layer 2 / hardware sprite support** — visualises and debugs the Next's enhanced graphics modes

**Weaknesses**:

- **Windows-only** — no native macOS or Linux builds (though it runs well under Wine)
- **Closed source** — freeware but not open-source
- **Narrower hardware focus** — optimised for Next and modern Spectrum-compatible machines; less coverage of original clones than ZEsarUX
- **Limited original-hardware accuracy testing** — not the go-to for verifying 48K timings

**Best for**: ZX Spectrum Next development, modern Spectrum-compatible software development, anyone working with the Next.

### Spectaculator

**Spectaculator** is a long-running commercial Windows emulator developed by **Thunderware Ltd** (Mark Woodmass). Released first in 1997, it has been continuously developed since. It is known for **polished presentation** and **good accuracy on original Sinclair hardware**.

**Strengths**:

- **Excellent UI** — the most polished of any Spectrum emulator
- **Strong original-hardware accuracy** — passes the standard test suites for 16K/48K/128K/+2/+2A/+3
- **Comprehensive peripheral support** — Interface 1, microdrive, +D, Opus, Currah µSpeech, SpecDrum, Melodik, Fuller, Kempston, etc.
- **Active commercial development** — still updated regularly
- **Good value** — shareware with reasonable registration price

**Weaknesses**:

- **Windows-only**
- **Commercial licence** — not free (though inexpensive)
- **No ZX Spectrum Next support**

**Best for**: casual users wanting a polished experience on Windows, original-hardware purists.

### UnrealSpeccy

**UnrealSpeccy** (sometimes Unreal Speccy) is a Russian-developed emulator with a long history. Written originally by **Sandra C. Lowe / Mike Blum** and later maintained by various contributors including **Stefan Drissen**, it is popular in the Russian scene.

**Strengths**:

- **Strong support for Russian clones** — Pentagon, Scorpion, Profi, ATM Turbo, etc.
- **Lightweight and fast**
- **Good demoscene support** — handles trick timing and Russian demoscene effects well
- **Free**

**Weaknesses**:

- **Windows-focused** (though there are ports)
- **UI is dated**
- **Smaller community than Fuse or ZEsarUX**

**Best for**: Russian hardware emulation, demoscene effects on Russian clones.

### Other Notable Emulators

- **Klive** — a modern emulator by **Pavel Žáček** (Czech scene) focused on accuracy and developer experience; gaining popularity in the 2020s
- **Speccy** (Marat Fayzullin) — part of the **fMSX** family of multi-platform emulators; widely ported to mobile and embedded platforms
- **JSSpeccy** — a JavaScript/WebAssembly port of Fuse, runs in any modern browser
- **x128** — an early (1996) emulator, now defunct but historically important
- **RealSpectrum** — DOS-era emulator by **Ramon Miranda** (Ramsoft), historically important for its debugging tools; superseded by modern emulators
- **EmuZ** (Ramil Zelenin) — Russian emulator with TSConf support
- **SpeccySDL** — SDL-based Fuse variant for embedded systems

---


## Comparison Matrix

### Platform Support

| Emulator | Windows | macOS | Linux | Android | iOS | Web |
|---|---|---|---|---|---|---|
| **Fuse** | ✅ | ✅ | ✅ | ✅ (port) | ❌ | ✅ (via JSSpeccy) |
| **ZEsarUX** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **CSpect** | ✅ | ✅ (Wine) | ✅ (Wine) | ❌ | ❌ | ❌ |
| **Spectaculator** | ✅ | ❌ | ❌ | ✅ (mobile) | ❌ | ❌ |
| **UnrealSpeccy** | ✅ | ❌ | ❌ (Linux port exists) | ❌ | ❌ | ❌ |
| **Klive** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Speccy (fMSX family)** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

### Hardware Coverage

| Emulator | 16K/48K | 128K/+2/+2A/+3 | Pentagon | Scorpion | ZX Spectrum Next | Russian TSConf |
|---|---|---|---|---|---|---|
| **Fuse** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **ZEsarUX** | ✅ | ✅ | ✅ | ✅ | ✅ (partial) | ✅ |
| **CSpect** | ✅ | ✅ | ✅ | ✅ | ✅ (best) | ✅ |
| **Spectaculator** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **UnrealSpeccy** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Klive** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

### Accuracy

| Emulator | 48K cycle-exact | Contended memory | Audio timing | Demoscene effects |
|---|---|---|---|---|
| **Fuse** | ✅ Strong | ✅ Strong | ✅ Strong | ✅ Strong |
| **ZEsarUX** | ✅ Strong | ✅ Strong | ✅ Strong | ✅ Strong |
| **CSpect** | ✅ Good | ✅ Good | ✅ Good | ✅ Good (Next-focused) |
| **Spectaculator** | ✅ Strong | ✅ Strong | ✅ Strong | ✅ Strong |
| **UnrealSpeccy** | ✅ Good | ✅ Good | ✅ Good | ✅ Strong (Russian scene) |
| **Klive** | ✅ Strong | ✅ Strong | ✅ Strong | ✅ Strong |

### Development Tools

| Emulator | Disassembler | Memory viewer | Breakpoints | Sprite/tile viewer | RMX playback |
|---|---|---|---|---|---|
| **Fuse** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **ZEsarUX** | ✅ (excellent) | ✅ | ✅ | ✅ | ✅ |
| **CSpect** | ✅ | ✅ | ✅ | ✅ (Next-specific) | ❌ |
| **Spectaculator** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **UnrealSpeccy** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Klive** | ✅ | ✅ | ✅ | ❌ | ❌ |

### Other Features

| Emulator | Open source | Free | Active dev | Native debugger UI |
|---|---|---|---|---|
| **Fuse** | ✅ (GPL) | ✅ | ✅ (slow) | ✅ |
| **ZEsarUX** | ✅ (GPL) | ✅ | ✅ | ✅ |
| **CSpect** | ❌ | ✅ (freeware) | ✅ | ✅ |
| **Spectaculator** | ❌ | ❌ (shareware) | ✅ | ✅ |
| **UnrealSpeccy** | ✅ | ✅ | ✅ (slow) | ✅ |
| **Klive** | ✅ | ✅ | ✅ | ✅ |

---

## Selection Guide

### Use Case: Casual Retro Gaming

**Recommendation: Fuse (cross-platform) or Spectaculator (Windows)**

For casual gaming — loading old Spectrum games and playing them — you want an emulator that's easy to set up, has a polished UI, and supports the common game formats (`.tap`, `.tzx`, `.z80`, `.sna`). Both Fuse and Spectaculator excel here. Fuse has the advantage of cross-platform support; Spectaculator is the most polished Windows-native option.

### Use Case: Software Development for Original Hardware

**Recommendation: Fuse or ZEsarUX**

For Spectrum software development — writing Z80 assembly or BASIC that will run on original hardware — accuracy is paramount. You need an emulator that catches timing bugs and correctly models contended memory, the ULA's video timing, and the AY-3-8912's audio behaviour. Fuse and ZEsarUX are the standards here; ZEsarUX has better debugging tools, Fuse has broader cross-platform availability.

### Use Case: ZX Spectrum Next Development

**Recommendation: CSpect (primary) or ZEsarUX (secondary)**

For Next-specific development, CSpect is the reference emulator — it tracks the NextOS specification most closely and has the best tools for working with layer 2 graphics, hardware sprites, and the Z80N's enhanced instructions. ZEsarUX is a capable second choice. Other emulators (Fuse, Spectaculator) lack Next support entirely.

### Use Case: Reverse Engineering and ROM Hacking

**Recommendation: ZEsarUX**

ZEsarUX has the most sophisticated reverse engineering tools of any Spectrum emulator — disassembler, memory map view, watchpoints, hardware breakpoint support, real-time assembly editing, and ML-assisted analysis features. For cracking copy protection, modifying existing games, or studying how classic Spectrum software works, ZEsarUX is the strongest choice.

### Use Case: Demoscene Production

**Recommendation: depends on the target hardware**

- **For original 48K/128K demos**: Fuse or ZEsarUX (accuracy is critical for trick-timing effects)
- **For Russian clone demos** (Pentagon, Scorpion): UnrealSpeccy or ZEsarUX (these handle the Russian timing variants best)
- **For ZX Spectrum Next demos**: CSpect (only realistic option for Next-specific features)
- **For cycle-exact testing on real hardware**: typically you'd test on actual hardware, but Fuse and ZEsarUX give the closest software emulation

### Use Case: Hardware Research and Preservation

**Recommendation: ZEsarUX**

ZEsarUX's coverage of obscure clones (TK90X, TK95, Inves Spectrum+, Chrome, BaseConf, etc.) and unusual peripherals is unmatched. If you're researching the history of Spectrum clones or studying how an obscure peripheral worked, ZEsarUX is the only emulator that's likely to model it.

### Use Case: Mobile Gaming

**Recommendation: Fuse (Android port), Speccy (iOS/Android), or Spectaculator Mobile**

For gaming on phones and tablets, you have several options. The Android port of Fuse is good. Marat Fayzullin's "Speccy" is the leading iOS option. Spectaculator Mobile is a polished commercial option on Android.

### Use Case: Web-Based / Browser Emulation

**Recommendation: JSSpeccy**

For running Spectrum software in a web browser (e.g., for a website that lets visitors play games), JSSpeccy is the standard choice. It's a port of Fuse to WebAssembly/JavaScript, retaining Fuse's accuracy in a browser-friendly package.

### Use Case: Embedded Systems

**Recommendation: Fuse (via SDL) or custom builds**

For embedded use (Raspberry Pi, custom handhelds, retro console ports), the SDL-based Fuse is commonly used as a base. Marat Fayzullin's Speccy is also widely ported. Most embedded emulators are forks or ports of these.

---


## FAQ

**Q: Which emulator is "best"?**

A: There is no single best — it depends on your use case. For cross-platform accuracy, **Fuse**. For reverse engineering and broadest clone coverage, **ZEsarUX**. For ZX Spectrum Next work, **CSpect**. For Windows casual gaming, **Spectaculator**. The right tool depends on what you're doing.

**Q: Do I need to install multiple emulators?**

A: Many serious Spectrum enthusiasts have **at least two** installed — typically Fuse or ZEsarUX for general use plus CSpect (if they work with the Next) or UnrealSpeccy (if they work with Russian clones). Different emulators can render the same software differently due to timing subtleties, so cross-checking is standard practice for serious development.

**Q: Are there any emulators that beat real hardware?**

A: In terms of compatibility, modern Fuse, ZEsarUX, and CSpect pass virtually all known test suites and run essentially all original Spectrum software correctly. However, they cannot reproduce every subtle hardware behaviour (RF interference, CRT screen phosphor decay, joystick paddle drift, audio amplifier distortion). For some demoscene work that depends on these subtle effects, real hardware remains the ultimate test. See [cycle_exact_accuracy.md](cycle_exact_accuracy.md) for details.

**Q: Why are most Spectrum emulators free or cheap?**

A: The Spectrum community has a strong tradition of free software, dating back to the early 1990s when emulation began. Many emulator authors are themselves demoscene or preservation contributors who see their emulator as a contribution to the wider community. Commercial Spectrum emulators (like Spectaculator) exist but typically charge modest prices to be sustainable without excluding users.

**Q: What about the emulators bundled with retro mini-consoles (like the Sinclair ZX Spectrum Vega)?**

A: These devices typically run **embedded versions of Fuse or Spectaculator** adapted to the device's hardware. The emulation is usually competent but the user interface is simplified for the consumer market. For serious use, a desktop emulator is always better.

**Q: Are there emulators for other platforms that emulate the Spectrum?**

A: Yes — the Spectrum has been emulated on the Amiga (early 1990s), the PC running DOS (x128, Z80Em), modern browsers (JSSpeccy), mobile phones, and even on other retro computers like the Commodore 64. These are mostly curiosities now that fast desktop emulators exist, but the cross-platform Spectrum emulation scene is part of the broader retro-computing hobby.

**Q: Can emulators run software that real hardware can't?**

A: Yes, in some cases — modern emulators can sometimes run "broken" software that crashes on real hardware due to subtle timing issues, because emulators may paper over the timing discrepancies. Conversely, some demos rely on hardware behaviour that emulators don't model (e.g., CPU register contents at reset). For software that targets real hardware, real hardware remains the gold standard.

---

## Summary

The ZX Spectrum emulator scene is mature and diverse, with multiple high-quality options catering to different use cases. For most users, **one of the major four — Fuse, ZEsarUX, CSpect, or Spectaculator — will be the right choice**, depending on platform preferences and what kind of Spectrum work they're doing. Casual users should pick Fuse (cross-platform) or Spectaculator (Windows); serious developers should pick ZEsarUX or CSpect depending on whether they target original hardware or the Next.

The modern emulator scene is the result of 30+ years of accumulated refinement, with each generation of emulators building on the discoveries of the previous one. The technical details of how these emulators achieve their accuracy — cycle-exact timing, contended memory modelling, audio clock management — are covered in [cycle_exact_accuracy.md](cycle_exact_accuracy.md). The test suites that validate emulator correctness are covered in [test_suites.md](test_suites.md). Individual emulators have their own dedicated deep-dive articles: [fuse.md](fuse.md), [zesarux.md](zesarux.md), [cspect.md](cspect.md).

---

## References

### Per-Emulator Documentation

- **Fuse** — source code, manual, and release notes at the official Fuse site
- **ZEsarUX** — documentation and tutorials at the ZEsarUX website
- **CSpect** — release notes at the CSpect download site
- **Spectaculator** — official website with feature list
- **UnrealSpeccy** — documentation in Russian and English at the UnrealSpeccy project pages
- **Klive** — source and docs at the Klive GitHub repository

### Comparison Resources

- **World of Spectrum** forums — emulator comparison discussions
- **comp.sys.sinclair** Usenet archives — historical emulator comparisons (1990s–2000s)
- **Retro Gamer magazine** — periodic emulator reviews
- **ZX Spectrum Discord / Telegram groups** — community advice on emulator choice

### Test Suites and Validation

- See [test_suites.md](test_suites.md) for the standardised test ROMs and snapshots used to validate emulator accuracy

### Cross-References

- [Fuse](fuse.md) — the cross-platform accuracy-focused standard
- [ZEsarUX](zesarux.md) — broadest hardware coverage, reverse engineering tools
- [CSpect](cspect.md) — ZX Spectrum Next reference emulator
- [Cycle-Exact Accuracy](cycle_exact_accuracy.md) — the technical challenges of faithful Spectrum emulation
- [Test Suites](test_suites.md) — validation ROMs and test software
