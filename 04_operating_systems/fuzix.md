[← Home](../README.md) · [Operating Systems](README.md)

# FUZIX — Unix on the Spectrum

Every other operating system in this section is, in one way or another, a product of the 1980s. **FUZIX** is the exception. Started in 2014 by **Alan Cox** — the longtime Linux kernel developer — FUZIX is a from-scratch reimplementation of Unix for 8-bit microcomputers, with the ZX Spectrum as one of its primary targets. It is multi-user, multi-tasking, comes with a C compiler and a Bourne-style shell, and boots on real Spectrum hardware in under two seconds.

FUZIX matters because it answers a question the 1980s never properly answered: *what would a "serious" Spectrum operating system have looked like if the platform had survived?* CP/M gave the Spectrum business software but no multitasking and no memory protection. +3 DOS was a single-user DOS. TR-DOS and ESXDOS are disk loaders, not operating systems in the modern sense. FUZIX is the only Spectrum OS that provides processes, a hierarchical filesystem with permissions, device files, signals, pipes, fork/exec, and a kernel/user mode separation — the basic architecture of every modern operating system.

This article covers FUZIX as a system: its origins in the UZI project, its kernel architecture, how it fits into 128 KB of Spectrum RAM, its filesystem, its Unix-flavoured syscall API, the machines it supports, its userland, how to write programs for it, and its current status in 2024. For CP/M — the historical "serious" Spectrum OS — see [cpm.md](cpm.md). For the +3's native DOS, see [plus3dos.md](plus3dos.md).

---

## Roadmap

1. **What FUZIX is** — Alan Cox, UZI, the 2014 origins, why Unix on a Speccy
2. **Architecture** — kernel/user split, process model, the syscall boundary
3. **Memory layout** — how a multitasking Unix fits into 128 KB
4. **The filesystem** — UZI-style fs, FAT bridge, devices, permissions
5. **The Unix API** — the syscall table, calling conventions, ~70 calls
6. **FUZIX on the Spectrum** — 128K, +2, +3, Pentagon, ATM Turbo, boot flow
7. **The userland** — init, getty, sh, vi, and what software actually runs
8. **Programming for FUZIX** — the Fuzix C compiler, building binaries
9. **Modern status** — active development, where to get it, the community
10. **Cross-references** — where to go next

---

## §1. What FUZIX Is

### 1.1 The lineage: UZI, UZI180, Fuzix

To understand FUZIX, you have to understand its lineage. Unix-on-small-machines is an idea almost as old as Unix itself, and FUZIX is the most recent chapter in a story that stretches back to the early 1980s.

The direct ancestors:

- **VENIX/81 (1981)** — a port of Unix V7 to DEC Pro-350 and similar PDP-11-class machines. Proved that Unix could run in 64 KB. Not a Spectrum target, but established the design pattern.
- **Minix (1987)** — Andrew Tanenbaum's Unix-like teaching OS for the IBM PC. Inspired Linux. Not a Spectrum target either, but the source of much educational material that influenced later projects.
- **UZI (1997)** — written by **Douglas Braun**. A from-scratch Unix V7-flavoured kernel for the Z80, targetting the RC2014 and similar hobbyist Z80 machines. UZI was the first credible "Unix on a stock Z80" implementation. Source code ~6,000 lines of C.
- **UZI180 (2000s)** — a port of UZI to the Hitachi HD64180 (Z180) CPU, used in various Z180-based hobbyist machines. Added MMU support.
- **FUZIX (2014–present)** — Alan Cox's rewrite and massive expansion of UZI. Took the UZI kernel as a starting point, modernised it, fixed the design flaws, added a proper userland, ported it to ~30 targets including the Spectrum family.

Alan Cox needs no introduction to anyone who has used Linux. He was the second-ever Linux kernel maintainer (after Linus Torvalds himself), maintained the Linux 2.4 stable series, wrote or rewrote substantial portions of the Linux networking, filesystem, and device driver layers, and was one of the most prolific kernel contributors from 1992 to ~2010. FUZIX is, in a sense, his retirement project: a return to the kind of small-machine hacking where he started in the 1980s.

### 1.2 Why bother putting Unix on a Spectrum?

The honest answer is: because you can. FUZIX does not make a Spectrum into a practical daily-use computer in 2024 — a Raspberry Pi costs less in real terms than a 128K Spectrum did in 1986 and is several thousand times faster. What FUZIX does is:

1. **Provide a research platform.** If you want to understand how a Unix kernel actually works — processes, files, signals, scheduling — reading the FUZIX source is far more approachable than reading Linux. The whole kernel fits in 64 KB.
2. **Rescue old hardware.** A real 128K Spectrum with a DivIDE or DivMMC interface can run real Unix software: vi, ls, cat, grep, make, awk, a C compiler. This is a remarkable thing for hardware designed in 1986 to run Manic Miner.
3. **Provide a bridge to the present.** The Fuzix C compiler (`fcc`) produces binaries that run on FUZIX but can be cross-compiled on a modern Linux box. Software written for FUZIX feels like modern Unix software, not like 1980s 8-bit programming.
4. **Provide the architecture that 1980s Spectrums deserved.** Sinclair's 128K BASIC, the +3 DOS, TR-DOS, and even ESXDOS all share a limitation: they are single-tasking, single-user, with no isolation between programs. FUZIX shows what the platform could have been with a different design philosophy.

For hobbyists in 2024, FUZIX is also a wonderful way to learn Unix internals. The kernel source is in C, compiles in a few seconds, runs on cheap real hardware, and is small enough to hold in your head.

### 1.3 What FUZIX actually provides

A FUZIX installation on a Spectrum 128K consists of:

- **A kernel image** (~24 KB), loaded from disk at boot.
- **A root filesystem** (typically on a CF card via DivIDE, an SD card via DivMMC, or a `.trd`/`.dsk` image in an emulator), containing:
  - `/init` — the first userland process (PID 1).
  - `/bin/sh` — a Bourne-compatible shell.
  - `/bin/login`, `/bin/getty` — for multi-user logins.
  - `/bin/ls`, `/bin/cat`, `/bin/cp`, `/bin/mv`, `/bin/rm` — core utilities.
  - `/usr/bin/vi` — the vi editor.
  - `/usr/bin/make`, `/usr/bin/fcc`, `/usr/bin/as` — the C compiler toolchain.
  - `/etc/passwd`, `/etc/termcap`, `/etc/rc` — system configuration.
  - `/dev/` — device files (`/dev/tty`, `/dev/fd0`, `/dev/rd0`, `/dev/null`, etc.).
  - `/tmp/` — temporary files.
- **Optional swap space** (on the same disk as the root filesystem), used to timeshare more processes than fit in RAM.

When FUZIX boots on a Spectrum 128K, you see:

```
FUZIX version 1.21
Copyright (C) 1998-2024 Alan Cox and others

Tuned for ZX Spectrum 128K
CPU: Z80 at 3.55 MHz
RAM: 128 KB (4 banks of 32 KB)
Disk: /dev/fd0 (2048 blocks)
Checking root filesystem... OK
Mounting /dev/fd0 read-only... OK
Initializing devices... OK
Starting init...

login: root
Password: (none)
# 
```

That `#` prompt is a real Bourne shell. From here you can `ls`, `cd`, `cat /etc/passwd`, run `vi /etc/rc`, edit boot scripts, compile C programs — everything you would expect from a Unix system, just smaller and slower.

### 1.4 Versions

FUZIX has been under continuous development since 2014. Version history (major milestones):

| Version | Year | Notable change |
|---|---|---|
| 0.1 | 2014 | First public release; boots on RC2014, basic shell |
| 0.2 | 2015 | Z80 Spectrum 128K port added; floppy disk support |
| 0.3 | 2016 | Networking stack (TCP/IP via SLIP over serial) |
| 1.0 | 2018 | Multi-user support; proper /etc/passwd authentication |
| 1.1 | 2020 | TCP/IP stack overhaul; improved FAT support |
| 1.2 | 2022 | MMC/SD card support for DivMMC; +3 disk support |
| 1.21 | 2024 | Current stable; bug fixes, performance tuning |

The Spectrum port is one of the most actively maintained FUZIX targets. Source code lives at `github.com/EtchedPixels/FUZIX`, with binaries and documentation for each target in the `Standalone` directory of the repository.

### 1.5 Why FUZIX beats UZI on the Spectrum

The original UZI was a proof of concept. FUZIX is the production version. The differences:

| Feature | UZI (1997) | FUZIX (2024) |
|---|---|---|
| Multi-user | No | Yes (proper uid/gid, /etc/passwd) |
| Multi-tasking | Cooperative (one process at a time) | Pre-emptive with priorities |
| Networking | None | TCP/IP via SLIP/PPP, sockets API |
| Filesystems | UZI only | UZI, FAT12/16/32, RT-11 |
| C compiler | None (write ASM, link by hand) | Full `fcc` toolchain (cc1, assembler, linker) |
| Targets | 1 (RC2014) | ~30 (Spectrum family, MSX, CPC, Apple II, TRS-80, etc.) |
| Source size | ~6,000 lines | ~50,000 lines |
| Userland | 4 utilities | ~150 utilities |

FUZIX is, in 2024, the most capable Spectrum operating system ever written — by a substantial margin. It is also, by 8-bit standards, the most modern.

---
## §2. Architecture

FUZIX is a Unix V7-flavoured kernel. Anyone who has read the classic Lion's Commentary on Unix 6th Edition will recognize the basic shape: a process table, an inode table, a buffer cache, a syscall dispatcher, and a set of kernel-side functions that implement the syscall semantics. What makes FUZIX unusual is that all of this fits into 24 KB of compiled Z80 code.

### 2.1 The kernel/user split

Like all Unixes, FUZIX has a strict separation between **kernel mode** and **user mode**. On a real 32-bit Unix system, this separation is enforced by the CPU's MMU: kernel pages are marked supervisor-only, and user code that tries to touch them triggers a hardware fault. The Z80 has no such protection — any code can read or write any byte of memory.

FUZIX emulates the kernel/user split in software:

- The **kernel** occupies the top of the address space (`#C000`–`#FFFF` on a Spectrum 128K, plus the lower 16 KB of banked RAM when needed). User processes cannot accidentally jump into kernel code because the kernel is in a different RAM bank from the running user process — switching banks requires writing to port `#7FFD`, which is a privileged operation only the kernel performs.
- **System calls** are made via a software interrupt (`RST 8` on most Spectrum targets, occasionally `RST 30`). The kernel handles the RST vector, inspects the syscall number and arguments in the user's registers, and dispatches to the appropriate kernel function.
- The **kernel/user boundary** is the syscall dispatcher. User code that does not invoke a syscall cannot access kernel memory, kernel data structures, or another process's memory — because none of that is mapped into the user's address space.

This is **software isolation** rather than hardware isolation. A buggy or malicious user program could in principle write to port `#7FFD` and remap kernel memory, breaking the kernel. FUZIX does not defend against this; it assumes user programs are cooperative. This is the same trust model as classic Unix V7 or MS-DOS — and it is fine for a single-user hobbyist system.

### 2.2 The process model

A FUZIX **process** is represented by an entry in the kernel's process table (`struct p_tab`). Each entry contains:

- The process ID (PID), a 16-bit integer (1–32767).
- The parent PID (PPID).
- The real and effective user IDs (uid, euid) and group IDs.
- The process state: RUNNING, READY, WAITING, SLEEPING, ZOMBIE.
- A pointer to the process's `u_data` block (the "u area" — analogous to Unix's `u` structure).
- Saved register state (the registers at the time of the last context switch).
- Pending signals.
- The current working directory and root directory inodes.
- Open file descriptors (a fixed-size table, typically 10 per process).
- Resource usage: CPU time consumed, memory used.

The process lifecycle follows Unix conventions exactly:

1. **fork()** — creates a near-identical copy of the calling process. The child gets a new PID, a new entry in the process table, and a copy of the parent's memory (using copy-on-write where possible).
2. **exec()** — replaces the current process image with a new program loaded from disk. PID and open file descriptors are preserved; memory, registers, and stack are reset.
3. **exit()** — terminates the calling process. The process becomes a ZOMBIE until its parent calls wait().
4. **wait()** — blocks the calling process until one of its children exits, then returns the child's exit status.
5. **kill()** — sends a signal to another process.

The process table has a fixed size (typically 16 slots on the Spectrum port — i.e., at most 16 processes can exist simultaneously). This is small by modern Unix standards but plenty for the kind of work a Spectrum is asked to do.

### 2.3 Scheduling

FUZIX uses **pre-emptive priority-based scheduling**. Each process has a priority (0–9, lower = higher priority). The scheduler runs on every timer tick (50 Hz on a Spectrum, synced to the vertical blanking interrupt). At each tick:

1. The current process's quantum (remaining CPU time slice) is decremented.
2. If the quantum reaches zero, or the process is no longer in the RUNNING state, the scheduler scans the process table for the highest-priority READY process.
3. If that process differs from the current one, a context switch occurs: the current process's registers are saved in its p_tab entry, the new process's registers are loaded, and the memory bank containing the new process's code/data is mapped in.

Context switches are expensive by modern standards (~2 ms on a 3.5 MHz Z80), so FUZIX uses a relatively long quantum (default 4 ticks = 80 ms). This means foreground interactive processes feel responsive while CPU-bound background jobs are not starved.

The Spectrum's 50 Hz timer interrupt is the heartbeat of the entire system. Without it, nothing works — which is why FUZIX cannot run on a 48K Spectrum (the 48K has no useful timer interrupt; the 128K's interrupt structure is more capable).

### 2.4 Signals

FUZIX implements Unix signals: SIGINT (Ctrl-C), SIGQUIT, SIGKILL, SIGTERM, SIGALRM, SIGCHLD, SIGHUP, SIGSEGV, and a handful of others. A signal is a software notification delivered to a process asynchronously. The receiving process can either:

- Accept the default action (usually terminate, sometimes core dump).
- Ignore the signal.
- Catch the signal with a user-supplied handler function.

Signal delivery happens at the next syscall return or timer tick — the kernel checks the pending signal mask and either calls the user's handler or performs the default action. This is exactly Unix V7 semantics.

The classic use case: a user presses Ctrl-C in the shell. The terminal driver sees the break, sends SIGINT to the foreground process group, the kernel interrupts whatever that process is doing and either runs its SIGINT handler (if registered) or terminates it. The shell then sees the child has died and prints a new prompt.

### 2.5 Pipes and I/O redirection

FUZIX supports **anonymous pipes** (`pipe()` syscall) and **I/O redirection** (file descriptors can be dup'd to standard input/output/error). This is the basic Unix shell plumbing — `ls | grep foo > out.txt` — and it all works on FUZIX just as it does on Linux.

A pipe is a fixed-size kernel buffer (typically 512 bytes on the Spectrum). The `pipe()` syscall returns two file descriptors: one for reading, one for writing. A read blocks if the pipe is empty; a write blocks if the pipe is full. When all write ends are closed, a read returns end-of-file.

Combined with `fork()` and the fact that file descriptors are inherited across fork, this allows the classic Unix pattern for plumbing commands together — which is exactly what the shell does when it sees a `|` character.

### 2.6 The buffer cache

Like all Unix kernels, FUZIX maintains a **buffer cache**: a pool of fixed-size buffers (typically 512 bytes each) holding recently-accessed disk blocks. When the kernel needs to read a block, it first checks the cache; on a hit, no disk I/O is needed. On a miss, the kernel reads the block from disk and adds it to the cache (evicting the least-recently-used buffer if the cache is full).

The buffer cache is critical for performance. Disk I/O on a Spectrum 128K with a DivIDE interface is on the order of 30 KB/s; cache hits are essentially free (memory copy speeds, ~200 KB/s). A well-tuned workload (e.g., compiling a small C program) can achieve 80%+ cache hit rate, dramatically reducing disk accesses.

The cache is small (typically 8 buffers = 4 KB on the Spectrum port), which limits its effectiveness for large random-access workloads but is fine for typical 8-bit usage.

---

## §3. Memory Layout

The hardest design problem in any Z80 operating system is: *where do you put the kernel?* The Z80 has a 16-bit address bus (64 KB) and no MMU. The original Unix design assumed a PDP-11 with split I/D space and hardware memory protection. Forcing Unix onto a Z80 requires creativity.

### 3.1 The basic problem

A Unix-like OS needs space for:

1. The kernel itself (code + data) — ~24 KB on FUZIX.
2. Kernel data structures: process table, inode table, buffer cache, file table — ~6 KB.
3. The currently-running user process (code + data + stack) — typically 32–48 KB.
4. The current user process's kernel stack and `u area` — ~1 KB.

Total: ~60+ KB. This does not fit in 64 KB without overlap, and certainly does not leave room for a useful user process.

FUZIX solves this by **banking**. The Spectrum 128K has 128 KB of RAM divided into 8 banks of 16 KB, with the top 16 KB (`#C000`–`#FFFF`) switchable via port `#7FFD`. FUZIX exploits this aggressively.

### 3.2 FUZIX memory map on a Spectrum 128K

FUZIX divides the Spectrum 128K's memory as follows:

```
        Bank 0 (#0000-#3FFF)   Bank 1 (#4000-#7FFF)   Bank 2-3 (#8000-#FFFF)
        ─────────────────────  ─────────────────────  ─────────────────────
Common: +-------------------+  +-------------------+  +-------------------+
        | Spectrum ROM      |  | User process      |  | Common area       |
        | (NOT used by      |  | code and data     |  | (kernel stubs,    |
        | FUZIX after boot) |  |                   |  |  syscall vectors, |
        |                   |  |                   |  |  shared routines) |
        +-------------------+  +-------------------+  +-------------------+
                                                      
Banked: +-------------------+                          +-------------------+
        | User process      |                          | Kernel            |
        | continuation      |                          | (code + data +    |
        |                   |                          |  process table,   |
        |                   |                          |  inode table,     |
        |                   |                          |  buffer cache)    |
        +-------------------+                          +-------------------+
        (mapped into one                (mapped into top 16 KB via port #7FFD)
         of 3 user banks
         #0, #1, #2)
```

The key insight: the **top 16 KB of address space** (`#C000`–`#FFFF`) is the common area. It is mapped to one of the four 16 KB RAM banks (bank 0, 1, 2, or 3) via port `#7FFD`. FUZIX keeps:

- **Kernel code and data** in this top 16 KB most of the time. The kernel runs in this bank.
- **User processes** in the lower 48 KB (`#0000`–`#BFFF`). The user's code lives in the bottom 16 KB (bank 0 of the user's allocated bank pair) and middle 16 KB (bank 1).

When the kernel needs to access a user process's memory (e.g., to copy arguments into a syscall), it temporarily remaps the lower 32 KB to point at the user's bank. This is the **bank switching dance** that defines FUZIX's performance characteristics.

### 3.3 Per-process address space

Each FUZIX process sees a 48 KB virtual address space (`#0000`–`#BFFF`):

| Address range | Content |
|---|---|
| `#0000`–`#00FF` | Zero page: syscall vectors, signal trampolines |
| `#0100`–`xxxx` | Program code (.text) |
| `#xxxx`–`#yyyy` | Initialised data (.data) |
| `#yyyy`–`#zzzz` | Uninitialised data (.bss) — zeroed on exec |
| `#zzzz`–`#BDEF` | Heap (grows up via brk/sbrk) |
| `#BDF0`–`#BFFF` | Stack (grows down) — typically 256 bytes of slack |

The top 16 KB (`#C000`–`#FFFF`) is **kernel space** from the user's perspective. User code cannot read or write this region — attempts to do so hit kernel data structures and either return nonsense or crash the process.

This 48 KB user address space is small but enough for serious work. A typical Fuzix C compiler invocation fits comfortably (`fcc hello.c`); even small Unix utilities (`ls`, `grep`, `awk`) leave several KB of headroom.

### 3.4 Multi-banking: more than 4 user processes

A Spectrum 128K has 4 user RAM banks. If each process needs its own bank, FUZIX can run at most 4 simultaneous processes — which would be very limiting.

FUZIX works around this with **swapping**. When the kernel needs to start a new process but no free bank is available, it picks a victim process, writes its entire memory image to disk (swap space), and frees the bank for the new process. When the victim is next scheduled, its image is read back from swap.

Swapping is expensive — a full bank swap is ~16 KB of disk I/O, taking a substantial fraction of a second. But it allows FUZIX to run as many processes as the process table allows (typically 16), even on a 128 KB machine.

Machines with more RAM (Pentagon 512, ATM Turbo, Spectrum +3 with all 128 KB available, ZX Evolution with 512 KB) can run more processes without swapping. The Spectrum Next with 2 MB of RAM can run the full 16 processes simultaneously with no swapping at all.

### 3.5 Boot-time memory initialisation

When FUZIX boots:

1. The boot loader (in the Spectrum ROM's wake-up state, or a DivIDE/DivMMC ROM) loads the kernel image from disk into RAM.
2. The kernel initialises the buffer cache, process table, and inode table (clearing them to zero).
3. The kernel mounts the root filesystem.
4. The kernel creates PID 1 (init) by reading `/init` from the root filesystem into a fresh process image.
5. The kernel performs an "return to user mode" — restoring PID 1's register state and jumping to its entry point.

From this point, the kernel runs only in response to syscalls (from PID 1 or its descendants) and timer interrupts. The Spectrum ROM is no longer needed and is not banked back in except for some hardware-specific operations (tape I/O, certain beeper routines).

### 3.6 Comparison with other Spectrum OSes

| OS | Address space layout | Kernel/user isolation | Max processes |
|---|---|---|---|
| 48K BASIC | ROM at low half, RAM above | None | 1 (BASIC) |
| 128K editor | ROM banked, RAM paged | None | 1 |
| TR-DOS | DOS in high 16 KB when invoked | None | 1 |
| +3 DOS | DOS in ROM banked as needed | None | 1 |
| ESXDOS | DOS in 8 KB ROM overlay | None | 1 |
| CP/M | OS at top of flat 64 KB | None | 1 |
| **FUZIX** | **Kernel in top 16 KB, user in lower 48 KB, banked** | **Software isolation** | **16** |

FUZIX's memory model is more sophisticated than any other Spectrum OS. The cost is complexity: the kernel is doing more work on every context switch, and the per-process address space is smaller than CP/M's TPA. The benefit is that FUZIX supports real multitasking, isolation between processes, and fork/exec — features none of the other Spectrum OSes provide.

---
## §4. The Filesystem

A Unix without a Unix filesystem is just a kernel. FUZIX ships with a real hierarchical filesystem, with permissions, device files, mount points, and the standard `/bin`, `/etc`, `/usr`, `/dev`, `/tmp` layout that every Unix user expects.

### 4.1 The UZI filesystem

FUZIX's native filesystem is **UZI fs** — a flat-hierarchy Unix V7-style filesystem originally defined by Douglas Braun's UZI project. UZI fs is similar in spirit to the original Unix V6/V7 filesystem but with adjustments for 8-bit machines.

Key parameters:

| Parameter | Value |
|---|---|
| Block size | 512 bytes (vs. Unix V7's 512 or 1024) |
| Max filename | 30 characters (vs. Unix V7's 14) |
| Max path | 256 characters |
| Max file size | 16 MB (theoretical; disk capacity usually smaller) |
| Inode size | 32 bytes |
| Inodes per block | 16 |
| Direct block pointers per inode | 10 |
| Indirect block pointers per inode | 1 (single indirect) |
| Double indirect pointers per inode | 1 |
| Triple indirect pointers per inode | 0 (not used on Spectrum-scale disks) |

The filesystem layout on disk:

```
Block 0:  Boot block (unused by FUZIX; reserved for boot code)
Block 1:  Superblock (filesystem metadata)
Block 2-N:  Inode blocks (16 inodes per block)
Block N+1:  Inode free map bitmap
Block N+2:  Block free map bitmap
Block N+3+ : Data blocks
```

Each inode contains the standard Unix fields: type (regular, directory, device, pipe, etc.), permissions (9 bits: rwx for user/group/other), uid, gid, size, timestamps (mtime, ctime, atime — though atime updates are often skipped for performance), and the direct/indirect block pointers.

Directories are files containing 32-byte entries: a 16-bit inode number followed by a 30-character filename (null-padded). The root directory `/` always lives in inode 1 — a hardcoded convention shared with Unix V7.

### 4.2 Permissions

UZI fs supports the standard Unix permission model:

- Each file has a 12-bit mode: 9 permission bits (rwx for owner/group/other), plus setuid, setgid, and sticky bits.
- Each file has a 16-bit uid (owner) and 16-bit gid (group).
- Processes have a real uid/gid and an effective uid/gid. The effective IDs are used for permission checks.
- File operations are checked: a process can read a file only if its effective uid matches the file's uid and the owner-read bit is set, or if the file's group matches the process's group and group-read is set, or if other-read is set.

This is the model that Linux, macOS, FreeBSD, and every other modern Unix uses. FUZIX implements it faithfully.

### 4.3 Mount points and multiple filesystems

FUZIX supports **mounting**: attaching a filesystem (from a separate disk or partition) onto an existing directory in the filesystem tree. After mounting, accessing files under that directory transparently accesses the mounted filesystem.

```sh
# Mount a FAT-formatted SD card partition onto /mnt
mount /dev/rd0 /mnt
# Now /mnt/foo is the file 'foo' on the SD card
ls /mnt/
cp /mnt/somefile /tmp/localcopy
umount /mnt
```

This is exactly the Unix `mount` semantics. The Spectrum port supports mounting at most 4 filesystems simultaneously (the root filesystem plus three others).

### 4.4 Device files

Like Unix, FUZIX exposes hardware via **device files** in `/dev`. These are special inodes — they have a `type` of "block device" or "character device" and contain a major/minor device number rather than data blocks.

Typical `/dev` entries on a Spectrum 128K:

| Path | Type | Major | Minor | Purpose |
|---|---|---|---|---|
| `/dev/tty` | char | 1 | 0 | Current controlling terminal |
| `/dev/console` | char | 1 | 1 | System console (keyboard + screen) |
| `/dev/null` | char | 1 | 2 | Discard sink (like /dev/null on Linux) |
| `/dev/zero` | char | 1 | 3 | Endless zero source |
| `/dev/fd0` | block | 2 | 0 | First floppy/CF/SD disk (whole disk) |
| `/dev/fd1` | block | 2 | 1 | Second disk |
| `/dev/rd0` | block | 3 | 0 | RAM disk (if configured) |
| `/dev/ttyS0` | char | 4 | 0 | First serial port |
| `/dev/lp0` | char | 5 | 0 | Printer port (ZX printer or parallel) |

A read or write to a device file invokes the device's driver (selected by major number) with the operation and minor number. This is exactly the Unix device file model.

### 4.5 The FAT bridge

UZI fs is a perfectly good filesystem, but it has one big practical problem: it is not readable on a modern PC. If you have a CF card with a UZI filesystem on it and you plug it into your laptop's CF reader, the laptop will not understand it.

To bridge this gap, FUZIX includes a **FAT12/16/32 driver**. You can format your CF/SD card as FAT on a modern PC, copy FUZIX files onto it from your PC, then mount the FAT card on the Spectrum:

```sh
mount -t fat /dev/fd0 /mnt
```

Files on the FAT partition appear in `/mnt` and can be read/written like any other files. This is how most FUZIX users transfer software between their PC and their Spectrum.

The FAT driver is read/write but does not support long filenames on older FUZIX versions (only 8.3 short names). Recent versions support VFAT long names as well.

### 4.6 Filesystem creation

To create a UZI filesystem, use the `mkfs` utility (run on the Spectrum itself, or on a Linux box with the Fuzix toolchain installed):

```sh
# Make a UZI filesystem on the second disk, with 256 inodes
mkfs /dev/fd1 256
```

Then mount the new filesystem, populate it with files from a master FAT-partitioned card, and reboot. The full FUZIX userland distribution comes as a disk image (`fuzix-128k.img`) which can be written directly to a CF card with `dd` on Linux.

### 4.7 Comparison with native Spectrum filesystems

| Feature | +3 DOS / TR-DOS | ESXDOS / NextZXOS | UZI fs (FUZIX) |
|---|---|---|---|
| Hierarchical directories | No (flat) | No (flat) | Yes |
| Permissions | No | No | Yes (full Unix rwx) |
| Device files | No | No | Yes |
| Mount points | No | No | Yes |
| Long filenames | No (8+1 or 8+3) | Yes (LFN) | Yes (30 chars) |
| Max file size | ~640 KB | Disk-limited | 16 MB |
| Atomic rename | No | Yes | Yes |
| Hard links | No | No | Yes |
| Symlinks | No | No | Yes (in 1.2+) |
| PC-readable | No (.DSK/.TRD only) | Yes (FAT) | No (FAT bridge needed) |

FUZIX's filesystem is dramatically more capable than any other Spectrum OS filesystem. The cost is complexity: UZI fs is more code than TR-DOS, +3 DOS, and ESXDOS put together.

---

## §5. The Unix API

FUZIX presents a Unix V7-flavoured **system call interface**. Programs make syscalls by loading registers with the syscall number and arguments, then invoking a software interrupt. The kernel dispatches on the syscall number and returns the result in registers.

### 5.1 The syscall table

FUZIX implements approximately 70 system calls. The exact set has evolved over time but includes:

**Process management:**
- `fork()` — create a new process (clone of caller)
- `execve(path, argv, envp)` — replace process image
- `wait(pid)` — wait for a child to exit
- `exit(status)` — terminate the calling process
- `getpid()` — return the caller's PID
- `getppid()` — return the parent's PID
- `getuid()`, `setuid()`, `geteuid()`, `seteuid()` — user ID management
- `getgid()`, `setgid()`, `getegid()`, `setegid()` — group ID management
- `nice(delta)` — change process priority
- `kill(pid, sig)` — send a signal
- `signal(sig, handler)` — install a signal handler
- `alarm(seconds)` — schedule a SIGALRM
- `pause()` — sleep until a signal arrives

**File I/O:**
- `open(path, flags, mode)` — open or create a file
- `close(fd)` — close a file descriptor
- `read(fd, buf, len)` — read bytes from a file descriptor
- `write(fd, buf, len)` — write bytes to a file descriptor
- `lseek(fd, offset, whence)` — seek within a file
- `dup(fd)`, `dup2(oldfd, newfd)` — duplicate a file descriptor
- `pipe(fildes)` — create an anonymous pipe
- `fcntl(fd, cmd, arg)` — file descriptor control (non-blocking, append, etc.)
- `ioctl(fd, cmd, arg)` — device-specific control
- `fstat(fd, buf)`, `stat(path, buf)` — get file metadata
- `link(old, new)`, `unlink(path)` — hard link / remove
- `rename(old, new)` — rename or move a file
- `chmod(path, mode)`, `chown(path, uid, gid)` — change permissions/ownership
- `mkdir(path)`, `rmdir(path)` — create/remove directories
- `chdir(path)`, `chroot(path)` — change directory / change root
- `getcwd(buf, len)` — get current working directory
- `umask(mask)` — set file creation mask
- `mount(dev, dir, fstype, flags)` — mount a filesystem
- `umount(dir)` — unmount a filesystem
- `sync()` — flush all filesystem buffers to disk

**Memory:**
- `brk(addr)`, `sbrk(incr)` — change the heap boundary
- `getmem()` — query free memory

**Time:**
- `time(t)` — get current time (seconds since epoch)
- `stime(t)` — set the time (root only)
- `times(buf)` — get process CPU time statistics
- `sleep(seconds)` — sleep for a number of seconds
- `usleep(usec)` — sleep for microseconds (rounded to tick granularity)

**System:**
- `ioctl(fd, cmd, arg)` — terminal control (baud rate, raw mode, etc.)
- `reboot()` — reboot the machine (root only)
- `uname(buf)` — get system name and version
- `sysinfo(buf)` — get memory and process statistics

**Networking (when configured):**
- `socket(domain, type, protocol)` — create a network socket
- `bind(fd, addr, len)`, `connect(fd, addr, len)` — bind/connect a socket
- `listen(fd, backlog)`, `accept(fd, addr, len)` — server-side socket operations
- `send(fd, buf, len, flags)`, `recv(fd, buf, len, flags)` — send/receive data

### 5.2 The calling convention

FUZIX uses a register-based syscall convention adapted to the Z80:

```z80
         LD   DE,addr_of_arguments   ; 16-bit arg pointer
         LD   C,syscall_number       ; 8-bit syscall number
         RST  8                      ; trap to kernel
         ; Returns:
         ;   Carry clear = success, A = return value (or HL for 16-bit)
         ;   Carry set = error, A = errno
```

The arguments are typically passed via a small structure pointed to by DE (because the Z80 has few general-purpose registers and many syscalls need 3+ arguments). The exact layout depends on the syscall.

From C, the user does not see this convention — the Fuzix C library wraps each syscall in a normal-looking C function (`open()`, `read()`, etc.) that handles the argument packing and register setup.

### 5.3 Example: the `open()` syscall in C

A user C program calls `open()`:

```c
int fd = open("/etc/passwd", O_RDONLY, 0);
if (fd < 0) {
    perror("open");
    exit(1);
}
```

The C library translates this to:

```z80
         LD   HL,mode_flags|O_RDONLY<<8     ; build mode word
         LD   (arg_buf),HL
         LD   HL,path_to_passwd             ; pointer to "/etc/passwd"
         LD   (arg_buf+2),HL
         LD   DE,arg_buf
         LD   C,SYS_OPEN                    ; syscall number
         RST  8
         JR   C,.error
         LD   A,L                           ; fd returned in L
         RET
.error:
         LD   (errno),A                     ; store errno
         LD   HL,-1
         RET
```

The C library further wraps the error return so that `open()` returns `-1` on error and sets `errno`, exactly as on a modern Unix.

### 5.4 Example: a complete FUZIX C program

A trivial example — a program that prints "Hello, FUZIX!" and exits:

```c
#include <unistd.h>

int main(void) {
    const char msg[] = "Hello, FUZIX!\n";
    write(1, msg, sizeof(msg) - 1);
    return 0;
}
```

Compile and run on FUZIX:

```sh
$ fcc hello.c -o hello
$ ./hello
Hello, FUZIX!
$
```

This compiles to a `.S` (assembly) intermediate, then to a FUZIX a.out-style binary, then runs as a normal user process under the shell. From the user's perspective, this is indistinguishable from writing the same program on Linux.

### 5.5 Error codes

FUZIX error codes follow Unix V7 conventions:

| Mnemonic | Value | Meaning |
|---|---|---|
| `EPERM` | 1 | Operation not permitted |
| `ENOENT` | 2 | No such file or directory |
| `EIO` | 5 | I/O error |
| `EBADF` | 9 | Bad file descriptor |
| `ENOMEM` | 12 | Out of memory |
| `EACCES` | 13 | Permission denied |
| `EBUSY` | 16 | Device or resource busy |
| `EEXIST` | 17 | File already exists |
| `ENOTDIR` | 20 | Not a directory |
| `EISDIR` | 21 | Is a directory |
| `EINVAL` | 22 | Invalid argument |
| `ENOSPC` | 28 | No space left on device |
| `EPIPE` | 32 | Broken pipe |

These are the same values used by every modern Unix. Code written against FUZIX's `<errno.h>` is portable to Linux with no changes.

---
## §6. FUZIX on the Spectrum

FUZIX is portable across roughly 30 different 8-bit target machines. The Spectrum family is among its best-supported targets, with separate ports for several Spectrum-compatible machines.

### 6.1 Supported Spectrum machines

| Machine | Support level | Notes |
|---|---|---|
| Spectrum 128K (1986) | Full | The "canonical" FUZIX Spectrum target |
| Spectrum +2 (1987) | Full | Identical to 128K from FUZIX's perspective |
| Spectrum +2A (1987) | Full | Uses the +3 paging scheme |
| Spectrum +3 (1987) | Full | Supports +3 floppy as well as DivIDE/DivMMC |
| Pentagon 128/512/1024 | Full | Russian clone; banking extensions used |
| ATM Turbo 2+ | Full | With its own disk hardware |
| Sprinter | Partial | Boot works; some drivers incomplete |
| ZX Evolution | Full | 512 KB or 1 MB configurations |
| ZX Spectrum Next | Full | Uses 2 MB RAM; runs FUZIX with no swapping |
| Timex TS2068 | Partial | Different display and banking from 128K |
| Harlequin (FPGA clone) | Full | Treated as 128K |
| 48K Spectrum | **Not supported** | Insufficient RAM and no useful timer interrupt |

The 48K is the obvious gap. The 48K's only useful interrupt is the 50 Hz VBLANK, which FUZIX *could* use as a timer — but the 48K has no banked RAM, so FUZIX cannot fit a kernel + a user process into the same 64 KB. Adding 48K support would require substantial rework for negligible benefit (the resulting system would have ~32 KB user processes, no swap, no cache).

### 6.2 Required hardware

To run FUZIX on a real Spectrum, you need:

1. **A 128K-or-better Spectrum** (or a clone).
2. **A disk interface** — one of:
   - **DivIDE** (CompactFlash, IDE) — the most common
   - **DivMMC** (SD card) — modern alternative
   - **+3 floppy** (for +3 / +2A machines)
   - **SMC reader** (custom hardware)
3. **A keyboard** and **a video output** (TV or monitor) — the standard Spectrum setup.
4. **Optionally: a serial interface** (for TCP/IP over SLIP, or for terminal access from a modern PC).

A real-hardware FUZIX setup typically looks like: a Spectrum 128K (the "toastrack" model is favored for its compact form), a DivMMC Clone board plugged into the rear port, a 32 GB microSD card (FUZIX partition is small but the rest can hold FAT-formatted asset files), and a TV output. Total cost in 2024: roughly £80–£120 depending on the Spectrum model.

### 6.3 Boot flow

When a Spectrum 128K with a DivIDE/DivMMC is powered on:

1. The Spectrum ROM runs as normal and tries to load from the disk interface (the DivIDE's ROM intercepts the boot ROM call).
2. The DivIDE ROM presents a boot menu: load +3 DOS, load TR-DOS, or load FUZIX. The user selects FUZIX.
3. The FUZIX boot loader is read from disk into the lower 16 KB of RAM (overlaying the Spectrum ROM at `#0000`–`#3FFF`).
4. The boot loader disables interrupts, switches the top 16 KB to point at RAM bank 0, copies the kernel image into bank 0, and jumps to the kernel entry point.
5. The kernel re-enables interrupts (now using the 128K's programmable interrupt source instead of the ROM's VBLANK handler), initialises its data structures, mounts the root filesystem, and starts PID 1.
6. `/init` runs, reads `/etc/inittab`, and forks a `getty` process for the console.
7. `getty` prints the `login:` prompt. The user logs in. The shell runs.

Total boot time: about 1.5 seconds on a DivIDE with a CF card; 2.5 seconds on a DivMMC with an SD card (the SD card has slightly higher latency).

### 6.4 Storage configurations

The disk hardware determines what storage is available:

**DivIDE (CompactFlash):**
- `/dev/fd0` = master IDE device (the CF card)
- `/dev/fd1` = slave IDE device (rare)
- CF cards up to 512 MB supported via FAT32
- Typical FUZIX partition sizes: 4 MB root filesystem, 8 MB swap, rest FAT

**DivMMC (SD card):**
- `/dev/fd0` = SD card
- SDHC cards up to 32 GB supported
- Slightly slower than DivIDE due to SPI overhead

**+3 floppy:**
- `/dev/fd0` = drive A (3-inch floppy, 180 KB)
- `/dev/fd1` = drive B (if fitted)
- Very slow (~3 KB/s); practical only for booting then mounting other disks

**ZX Evolution:**
- `/dev/fd0`, `/dev/fd1` = IDE/CF
- `/dev/fd2`, `/dev/fd3` = SD card
- `/dev/fd4` = +3 floppy
- Most flexible configuration

Most users put the root filesystem on the CF or SD card, where I/O is fast enough to make FUZIX feel responsive. Booting from +3 floppy then mounting CF/SD is also supported.

### 6.5 The console terminal

FUZIX presents the user with a **terminal interface** — text on a video screen, typed at a keyboard. On a Spectrum, this is implemented via a custom terminal driver that:

- Renders text in the Spectrum's 32-column or 64-column text mode.
- Reads keys from the Spectrum keyboard matrix.
- Supports a subset of ANSI escape codes (cursor movement, color, clearing regions).
- Implements the standard Unix terminal ioctls (TCGETS, TCSETS, raw mode, etc.).

The 32-column mode is the default (large, readable text). 64-column mode is selectable for users who want to see more on screen at once (using the 8×8 font with attribute clash).

For users who want a more authentic Unix experience, FUZIX can be configured to use a serial port as the console. Connect the Spectrum's RS232 port to a modern PC's serial port (via a USB-serial adapter), run a terminal emulator (minicom, screen, etc.) at 9600 or 19200 baud, and FUZIX uses the modern PC's screen and keyboard instead of the Spectrum's. This is also how networking (TCP/IP over SLIP) is wired up.

### 6.6 Networking

FUZIX has a **TCP/IP stack** (originally derived from W. Richard Stevens' classic implementation, modernised and shrunk for the Z80). Networking is exposed via the standard BSD sockets API.

The Spectrum has no built-in networking hardware. FUZIX supports two transport mechanisms:

1. **SLIP over RS232** — encapsulates IP packets in a serial stream. Requires a Spectrum with an RS232 port (the 128K's edge connector exposes one via the KE pad). Speeds up to 19200 baud (~1.9 KB/s) on real hardware.
2. **ESP32 WiFi bridge** — a modern addition (ZX Spectrum Next only). An ESP32 module attached to the Spectrum acts as a WiFi modem, exchanging packets over SPI. Speeds up to ~30 KB/s.

With networking, FUZIX can:
- `telnet` to a remote host
- Serve a single HTTP request (via a small `httpd` server)
- Synchronise the system clock via NTP
- Ping remote hosts
- Act as a (very slow) terminal server

Networking on FUZIX is best understood as a curiosity that works, not a practical alternative to using a modern computer. It is excellent for demos and education.

---

## §7. The Userland

The kernel is interesting to systems programmers, but most users interact with FUZIX through its **userland** — the set of programs that ship with the system.

### 7.1 init, getty, login

When FUZIX finishes booting, it runs `/init` as PID 1. The init program is responsible for:

- Reading `/etc/inittab`, which specifies which terminals should have login prompts and what to run on each.
- Forking a `getty` process for each enabled terminal.
- Waiting for child processes to exit (via `wait()`), restarting any `getty` that has died.
- Handling `init` signals: e.g., `kill -HUP 1` causes init to re-read `/etc/inittab`.

A typical `/etc/inittab` on a Spectrum (single console, no serial):

```
# Format: id:runlevels:action:process
# Run getty on the console at all run levels
c1:1234:respawn:/bin/getty /dev/console 9600
```

When `getty` starts, it:
1. Opens `/dev/console` for reading and writing.
2. Sets the baud rate (irrelevant for a screen console, but matters for serial).
3. Prints `login: ` and reads a username.
4. `exec()`s `/bin/login username`.

`/bin/login` then:
1. Reads `/etc/passwd` to find the user's record.
2. Prompts for a password.
3. Checks the password against the encrypted form in `/etc/passwd` (or `/etc/shadow` if configured).
4. Sets the process's uid/gid to the user's.
5. `chdir`s to the user's home directory.
6. `exec()`s the user's shell (typically `/bin/sh`).

This is the standard Unix login flow, unchanged since 1976. FUZIX implements it faithfully.

### 7.2 The shell: `/bin/sh`

FUZIX's shell is a port of **asmsh** — a small Bourne-compatible shell originally written for the Amstrad CPC and adapted for FUZIX. It supports:

- Command execution: `ls`, `cat foo.txt`, `fcc hello.c -o hello`.
- Pipes: `ls | grep foo`.
- I/O redirection: `cmd > out`, `cmd < in`, `cmd >> append`, `cmd 2>&1`.
- Background: `cmd &`.
- Variable assignment: `FOO=bar`, `PATH=/bin:/usr/bin`.
- Environment variables: `export FOO`.
- Quoting: `echo "hello $NAME"`, `echo 'literal $NOTVAR'`.
- Conditionals: `if [ -f /etc/passwd ]; then ... ; fi`.
- Loops: `for i in 1 2 3; do echo $i; done`, `while [ ... ]; do ... ; done`.
- Functions: `greet() { echo hello $1; }`.
- Comments: `# this is a comment`.

The shell is small (~10 KB binary) but remarkably complete. Most non-trivial shell scripts (configure scripts, simple build pipelines, system administration scripts) work unchanged. The main gap is the absence of arithmetic expansion (`$((1+2))` is not supported in older versions).

### 7.3 Core utilities

FUZIX ships with a subset of the GNU Coreutils / BusyBox set. The catalog on a typical installation:

**File operations:** `ls`, `cp`, `mv`, `rm`, `ln`, `mkdir`, `rmdir`, `cd`, `pwd`, `touch`, `chmod`, `chown`, `find`.

**File display:** `cat`, `more`, `less` (simplified), `head`, `tail`, `wc`, `od`, `xxd`, `strings`.

**Text processing:** `grep`, `sed`, `awk` (a simplified awk), `sort`, `uniq`, `cut`, `tr`, `tee`, `diff` (basic).

**Archives:** `tar` (read-only on most installations, write supported on versions 1.2+), `compress` / `uncompress` (LZW), `gzip` / `gunzip` (DEFLATE — slow on a Z80).

**System:** `ps`, `kill`, `mount`, `umount`, `df`, `du`, `free`, `uname`, `hostname`, `date`, `uptime`, `sync`, `reboot`, `halt`.

**Editors:** `vi` (a port of the classic vi — modal, ex commands, the works), `ed` (line editor for emergencies).

**Networking:** `telnet`, `ftp` (client), `ping`, `hostname`, `ifconfig`, `route`, `httpd`.

**Development:** `fcc` (C compiler driver), `as` (assembler), `ld` (linker), `make` (GNU make compatible), `ar`, `nm`, `size`, `objdump`, `strip`.

**Misc:** `cal`, `banner`, `fortune`, `bc`, `dc`, `man` (a simple manual reader).

That is roughly 100 programs. A full FUZIX installation with all utilities fits in under 4 MB of disk space — small by modern standards but a substantial library for an 8-bit machine.

### 7.4 What does not run

The FUZIX userland is impressively complete but has visible limits compared to a modern Linux distribution:

- **No X11 or graphical environment.** The Spectrum's display is too limited and the CPU too slow.
- **No Python, Perl, Ruby, or other scripting languages.** (A small Perl subset runs on some configurations; full ports are impractical.)
- **No modern shell features.** Bash-specific features (arrays, extended globbing) are not in `/bin/sh`.
- **No SSH.** Cryptographic primitives are too slow on a 3.5 MHz Z80.
- **No GUI editors.** Emacs and nano are not available; you use vi.
- **Limited concurrency.** With 4–16 processes and a slow CPU, you cannot run many things at once.

What you get is a clean, classic, Unix V7-flavoured environment. For learning Unix, exploring operating system design, or just running a small interactive system on real Spectrum hardware, this is more than enough.

### 7.5 Performance: realistic expectations

Real-world timings on a Spectrum 128K with a DivIDE (3.5 MHz Z80, CF card at ~30 KB/s):

| Operation | Time |
|---|---|
| Boot to login prompt | 1.5 s |
| Login to shell prompt | 0.3 s |
| `ls` of /bin (30 files) | 0.1 s |
| `cat /etc/passwd` (1 KB) | <0.1 s |
| Compile a 100-line C program with `fcc` | ~12 s |
| `grep` over a 100 KB text file | ~2 s |
| Boot + login + `gcc hello.c` + run + reboot | ~30 s |
| Network ping (over SLIP at 9600 baud) | ~600 ms RTT |
| Boot + run a small makefile (5 small C files) | ~70 s |

These numbers feel slow by 21st-century standards but are astonishing by 1980s Spectrum standards. FUZIX is a real multitasking Unix running on hardware designed in 1986 to run single-tasking BASIC games.

---
## §8. Programming for FUZIX

One of FUZIX's biggest selling points is that you can write programs for it the same way you write programs for any Unix — using C. No other Spectrum OS offers this.

### 8.1 The Fuzix C compiler: `fcc`

FUZIX programs are typically written in C and compiled with **`fcc`** — the Fuzix C compiler driver. `fcc` is a wrapper around several tools:

- **`cc1`** — the actual compiler, originally derived from Fabrice Bellard's TinyCC, then heavily modified by Alan Cox to generate Z80 code instead of x86. Supports most of ANSI C89 / ISO C90 with some C99 extensions.
- **`opt`** — a peephole optimiser that cleans up the Z80 code generator's output.
- **`as`** — the Fuzix assembler (a port of the GNU assembler syntax, slightly simplified).
- **`ld`** — the Fuzix linker, producing FUZIX a.out-style binaries.

A typical invocation:

```sh
fcc hello.c -o hello
```

This is identical to running `gcc hello.c -o hello` on Linux. The resulting `./hello` binary can be run directly:

```sh
./hello
Hello, FUZIX!
```

### 8.2 What kind of C does FUZIX support?

`fcc` targets roughly the C89 / ANSI C standard, with some C99 features backported:

**Supported:**
- Function prototypes, `void`, `const`, `volatile`.
- `struct`, `union`, `enum`, typedef.
- Pointers (including function pointers).
- `static`, `extern`, `auto` storage classes.
- Standard preprocessor (`#include`, `#define`, `#ifdef`, `#if`, conditional compilation).
- All standard C library functions declared in `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<unistd.h>`, etc.
- Some C99 features: `//` comments, mixed declarations and statements, `long long`.

**Not supported:**
- Floating point (`double`, `float`). The Z80 has no FPU, and including soft-float would explode binary sizes. Programs that need floating point must implement it themselves.
- Bitfields larger than 8 bits.
- Variable-length arrays (C99 VLAs).
- Complex C++ features (no C++ compiler at all).

These limitations are not as severe as they sound. Most Unix utilities (the ones in the FUZIX userland, for example) do not use floating point and do not need VLAs. Code written in a conservative C89 style works perfectly.

### 8.3 A complete FUZIX program

A more realistic example — a small program that counts lines in a file:

```c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <file>\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(argv[1], "r");
    if (!f) {
        perror(argv[1]);
        return 1;
    }

    int c, lines = 0;
    int prev = '\n';
    while ((c = fgetc(f)) != EOF) {
        if (c == '\n') lines++;
        prev = c;
    }
    if (prev != '\n') lines++;  /* count unterminated last line */

    fclose(f);
    printf("%d\n", lines);
    return 0;
}
```

Compile and run:

```sh
$ fcc linecount.c -o linecount
$ ./linecount /etc/passwd
17
```

This program is portable to any Unix without modification. Compile it with `gcc linecount.c -o linecount` on Linux and it produces the same binary behavior.

### 8.4 Cross-compilation

Most FUZIX development is done on a modern Linux box, with binaries cross-compiled and then transferred to the Spectrum (via the FAT bridge or by writing a disk image).

The FUZIX source tree includes a cross-compiler configuration. To build it:

```bash
# On a Linux host
git clone https://github.com/EtchedPixels/FUZIX
cd FUZIX
make -C Applications/tools   # build host-side tools
make -C Application/fcc      # build the cross-compiler
```

After this, `fcc` runs on the Linux host but produces FUZIX binaries:

```bash
./fcc hello.c -o hello      # produces a FUZIX a.out
file hello
# hello: FUZIX executable (Z80)
```

Copy the resulting binaries onto a FAT-formatted SD card, plug the card into the Spectrum, mount the FAT partition under FUZIX, and copy the binaries into the local filesystem. The result: software written and compiled on a 2024-era Linux box runs on real 1986 Spectrum hardware.

### 8.5 Assembly language

For performance-critical code (device drivers, graphics routines, tight loops), FUZIX programs can drop to **Z80 assembly**. The Fuzix assembler accepts the standard Zilog syntax plus GNU-style directives.

A small assembly example — write "Hi\n" to stdout (file descriptor 1) and exit:

```z80
        .text
        .globl  _start
_start:
        LD   C,4               ; SYS_write
        LD   DE,args
        RST  8
        LD   C,1               ; SYS_exit
        LD   DE,exit_args
        RST  8
        ; exit does not return

        .data
args:   .word 1                ; fd = 1 (stdout)
        .word msg              ; buffer
        .word 3                ; length
msg:    .ascii "Hi\n"
exit_args:
        .word 0                ; exit status

```

Save as `hi.s`, assemble with `as hi.s -o hi.o`, link with `ld hi.o -o hi`, run as `./hi`.

### 8.6 Kernel programming

If you want to modify the FUZIX kernel itself — to add a device driver, fix a bug, or experiment with the scheduler — the source is in C and the build is straightforward:

```bash
git clone https://github.com/EtchedPixels/FUZIX
cd FUZIX/Kernel/platform-zx128
make
```

This produces a `kernel.bin` that can be loaded onto a FUZIX boot disk. The kernel source is heavily commented and follows a familiar Unix V7 layout (`main.c`, `inode.c`, `process.c`, `traps.c`, `device.c`, etc.).

To add a new device driver, write a small C file implementing the standard `open`, `close`, `read`, `write`, `ioctl` entry points and register it in `devices.c`. This is the same basic pattern as writing a Linux character device driver, just simpler.

---

## §9. Modern Status (2024)

FUZIX is one of the most actively developed ZX Spectrum projects in 2024. The community is small but dedicated, with most activity on GitHub and the World of Spectrum forums.

### 9.1 Where to get FUZIX

- **Source:** `github.com/EtchedPixels/FUZIX`
- **Pre-built disk images:** `github.com/EtchedPixels/FUZIX/tree/master/Standalone`
- **Documentation:** `github.com/EtchedPixels/FUZIX/wiki`
- **Community:** World of Spectrum forums, FUZIX Discord, comp.os.sinclair/clr.spectrum Usenet (still active)

To run FUZIX in an emulator:

1. Download the latest ZX Spectrum 128K FUZIX image (`fuzix-zx128-*.img`).
2. Launch Fuse, ZEsarUX, or your preferred emulator with a 128K Spectrum profile.
3. Attach the FUZIX image as a DivIDE/DivMMC storage device.
4. Boot. Select FUZIX from the boot menu. Login as `root` with no password.

To run FUZIX on real hardware:

1. Acquire a Spectrum 128K / +2 / +3 / Pentagon / Next.
2. Acquire a DivIDE or DivMMC interface (DivMMC clones cost ~£30 in 2024).
3. Acquire a CF card (DivIDE) or SD card (DivMMC).
4. Download the FUZIX disk image, write it to the card with `dd` or a dedicated tool.
5. Plug the card into the interface, plug the interface into the Spectrum, power on.

Most FUZIX users run a mix of emulator (for development) and real hardware (for the experience).

### 9.2 Recent and upcoming work

Active areas of FUZIX development in 2024:

- **ZX Spectrum Next support.** The Next's 2 MB RAM, DMA controller, and ESP32 WiFi make it the most capable FUZIX target. Recent work has focused on using the DMA for fast disk I/O and the ESP32 for native WiFi.
- **TCP/IP and network stack.** Continuous improvements to the in-kernel network stack, including support for HTTP client libraries and MQTT.
- **Performance optimisation.** The kernel's bank-switching code paths are being constantly tuned for faster context switches.
- **New filesystem features.** Symlink support, larger file sizes, and better FAT interoperability.
- **Userland expansion.** Ongoing ports of classic Unix utilities (`tar`, `gzip`, `awk`) to make the FUZIX userland more complete.

The current stable version (1.21, mid-2024) is well-tested and recommended for general use. Development snapshots are usually usable but occasionally broken.

### 9.3 Limitations in 2024

FUZIX's biggest practical limitations:

- **Slow on real hardware.** A 3.5 MHz Z80 is just slow. Compiling even a small C program takes several seconds; a large one takes minutes.
- **No networking on stock Spectrum hardware.** A real Spectrum 128K has no built-in networking; FUZIX networking requires a serial interface and a SLIP-capable host on the other end, or an ESP32-equipped Next.
- **No floating point in C.** Programs that need math must implement it themselves or use fixed-point.
- **Limited terminal capabilities.** The Spectrum's 32-column text mode is cramped for modern Unix software; the 64-column mode is more usable but has attribute clash.
- **Single-user usage in practice.** Although FUZIX supports multi-user, almost all real deployments are single-user: one person at the keyboard, no remote users.

### 9.4 FUZIX in the wider retro-Unix scene

FUZIX is not the only modern Unix-like for retro hardware. Other projects in this space:

- **Contiki** — an Internet-connected operating system for 8-bit machines, but more focused on IoT/networking than Unix compatibility.
- **OS/9** — a 1980s multi-user OS for the 6809 and 68K, still maintained by hobbyists, but not Z80.
- **Multicomp** — a SPARTAN6 FPGA soft-core system that often runs FUZIX.
- **CP/M-86 / GEM** — different ecosystems, different goals.

Among 8-bit Z80 Unix-like systems, FUZIX is the most capable, most actively developed, and best documented. It is the natural choice for anyone wanting to run Unix on a Spectrum.

---

## §10. Cross-References

- **[cpm.md](cpm.md)** — The other "serious" Spectrum OS. CP/M was the 1980s business option; FUZIX is the modern hobbyist option. Comparing them (§3.6) shows how much more capable FUZIX is — and how much more hardware it needs.
- **[plus3dos.md](plus3dos.md)** — +3 DOS provides a CP/M-compatible file API but no multitasking or isolation. FUZIX provides the same CP/M software library (via recompilation) plus a real Unix layer underneath.
- **[trdos.md](trdos.md)** — The Soviet disk standard. Most Pentagon users today use TR-DOS for games and FUZIX for "real computing" — the two coexist on the same CF card.
- **[esxdos.md](esxdos.md)** — ESXDOS is closer to a "DOS extension" than a real OS. FUZIX is the only Spectrum OS that provides true multi-process isolation; ESXDOS just gives you file I/O.
- **[../02_hardware/original/README.md](../02_hardware/original/README.md)** — Original Sinclair hardware reference. FUZIX runs on every 128K-or-better original Spectrum.
- **[../02_hardware/clones/README.md](../02_hardware/clones/README.md)** — Pentagon, ATM Turbo, Sprinter, ZX Evolution, etc. Most of these run FUZIX with additional features (more RAM, faster CPUs).
- **[../02_hardware/newgen/README.md](../02_hardware/newgen/README.md)** — The ZX Spectrum Next, the most capable FUZIX target. 2 MB RAM, DMA, WiFi via ESP32.
- **[../05_development/03_memory_and_io/memory_and_io_128k.md](../05_development/03_memory_and_io/memory_and_io_128k.md)** — The 128K's banked memory model is the foundation of FUZIX's address space layout (§3).
- **[../05_development/03_memory_and_io/memory_and_io_pentagon.md](../05_development/03_memory_and_io/memory_and_io_pentagon.md)** — Pentagon's banking extensions allow FUZIX to scale to 512 KB / 1024 KB.

---

## References

### External references

- [FUZIX project repository](https://github.com/EtchedPixels/FUZIX) — the canonical source for the FUZIX kernel, the Z80 port, and the Spectrum-specific device drivers; the primary reference for behavior under all edge cases.
- **Unix V6 / V7 documentation** (Bell Labs, 1979) — the historical reference for the UNIX ancestry that FUZIX inherits; documents the process model, the inode filesystem, and the system-call API that FUZIX faithfully replicates on 8-bit hardware.
- [`z88dk` FUZIX build instructions](https://github.com/z88dk/z88dk) — the canonical reference for cross-compiling C programs against the FUZIX userland on a modern host.
- [zx-pk.ru / `smol.viziv` Russian FUZIX threads](https://zx-pk.ru) — Russian-language forum discussions of FUZIX ports to Soviet clone hardware (Pentagon 1024, Scorpion ZS-256, ATM Turbo, ZX Evolution).
- **FUZIX on the Spectrum — community blog posts** — practical user experiences and installation walkthroughs documenting the supported hardware configurations (DivIDE, DivMMC, ZX Spectrum Next, inner-side SD on clones).

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same license.
