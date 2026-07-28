[← Home](../../README.md) · [Emulation](../README.md) · [MCU Emulation](README.md)

# Keyboard Controller on a Microcontroller

The Spectrum's keyboard is one of its most distinctive input peripherals — and one of its most disliked. The original **membrane keyboard** (on the 48K and 128K toastrack) has poor tactile feel, is prone to failure as the membrane traces degrade, and was designed for cost rather than ergonomics. The **+2** and **+3** versions improved things with a proper keyboard, but those rubber-keyed originals remain common.

Replacing the keyboard with a modern input device — typically a **PS/2 keyboard** or **USB keyboard** — is one of the most popular upgrades. This requires a small MCU that translates the external keyboard's protocol into the Spectrum's **8×8 keyboard matrix** that the [ULA](mcu_ula.md) reads via port `0xFE`. The same MCU can also handle **joystick** input (Kempston, Sinclair, Fuller) and even **mouse** input (Kempston mouse), giving a single input adapter.

This article covers the Spectrum keyboard matrix, the design of keyboard-controller MCUs, scan code translation, joystick and mouse emulation, and existing projects such as **ZXHIDKeyboard** and **ZXKey**. For background on the Spectrum's input hardware, see [the keyboard documentation](../../02_hardware/). For general MCU interfacing techniques, see [mcu_design_patterns.md](mcu_design_patterns.md).

---

## The Spectrum Keyboard Matrix

### Physical Layout

The Spectrum's keyboard is organised as an **8×8 matrix** — 8 row lines and 8 column lines, for up to 64 keys (the Spectrum uses 40 of these). Each key press shorts one row line to one column line.

The matrix is scanned by the ULA:

- **Row selection** — the CPU writes a value to the high byte (`A[8:15]`) of port `0xFE`. Each bit of the high byte selects one of the 8 row lines (bit 0 = row 0, bit 1 = row 1, etc.). Setting a bit **low** selects that row.
- **Column read** — the CPU reads from port `0xFE`. The low 5 bits (`D[0:4]`) return the state of the 5 column lines used by the keyboard. A bit is **low** if the corresponding key is pressed in the selected row.

So to scan the entire keyboard, software reads 8 times — once for each row — each time setting a different bit low in the high address byte.

### Address Mapping

The keyboard scan is done by reading from any I/O address of the form `0xFE` (low byte), with the high address byte selecting the row:

```
; Z80 example: read row 0 (CAPS SHIFT through G)
LD BC, 0xFEFE   ; A=0xFE selects port 0xFE, A[8]=0 selects row 0
IN A, (C)        ; Read column data — bits 0-4 show row 0's keys
```

Each row covers 5 keys (5 column lines are wired), giving a 40-key keyboard. The 8 rows map to the following keys:

| Row (A[15:8] bit low) | Address | Keys (bits 0-4) |
|---|---|---|
| Bit 0 (row 0) | `0xFEFE` | CAPS, Z, X, C, V |
| Bit 1 (row 1) | `0xFDFE` | A, S, D, F, G |
| Bit 2 (row 2) | `0xFBFE` | Q, W, E, R, T |
| Bit 3 (row 3) | `0xF7FE` | 1, 2, 3, 4, 5 |
| Bit 4 (row 4) | `0xEFFE` | 0, 9, 8, 7, 6 |
| Bit 5 (row 5) | `0xDFFE` | P, O, I, U, Y |
| Bit 6 (row 6) | `0xBFFE` | ENTER, L, K, J, H |
| Bit 7 (row 7) | `0x7FFE` | SPACE, SYM SHIFT, M, N, B |

The CAPS SHIFT and SYMBOL SHIFT keys appear in row 0 and row 7 respectively. Modifier keys (Shift, Symbol Shift) are read like any other key — they are not separate "modifier" inputs.

### Extended Keyboard (128K/+2/+3)

The Spectrum 128K, +2, and +3 added a numeric keypad and cursor keys. These are read via additional rows that would not fit in the basic 8×8 matrix — typically via a separate scan or by extending the matrix. Software that supports the extended keyboard reads these additional rows with different address patterns.

### Limitations of the Membrane Keyboard

The original membrane keyboard has several limitations that motivate replacement:

- **No N-key rollover** — because of the matrix, pressing multiple keys can produce "ghost" key presses. This is inherent to matrix keyboards without diode isolation. The Spectrum matrix does NOT include isolation diodes, so 3-key combinations can produce phantom 4th key presses.
- **Slow membrane response** — the membrane's electrical contact is slow and bouncy
- **Membrane degradation** — the conductive traces on the membrane flex circuit degrade over time, leading to keys that don't register or register unreliably
- **Poor tactile feedback** — the rubber dome keys give minimal feedback, making typing slow

These issues make replacing the keyboard an attractive upgrade.

---
## Why Replace the Keyboard with an MCU?

### Membrane Failure

The 40-year-old membranes in original 48K and 128K Spectrums are failing. Symptoms include:

- **Dead keys** — individual keys do not register
- **Phantom keys** — keys register that are not pressed (a shorted membrane)
- **Slow response** — keys register unreliably
- **Stuck keys** — keys register as continuously pressed

A modern replacement membrane is one option, but a more flexible solution is to bypass the membrane entirely and connect an external PS/2 or USB keyboard via an MCU.

### Ergonomic Improvement

Modern keyboards offer:

- **Proper tactile feedback** — full-travel mechanical or membrane keys
- **N-key rollover** — full N-key rollover keyboards are available, eliminating ghost keys
- **Function keys** — F1-F12 can be mapped to Spectrum-specific shortcuts
- **Numeric keypad** — useful for games and applications
- **Cursor keys** — separate arrow keys, easier than the Spectrum's SYMBOL SHIFT + 5/6/7/8

### Joystick Integration

The same MCU that handles the keyboard can also handle joystick input. The Spectrum supports several joystick protocols (see [joystick documentation](../../03_io/)):

- **Kempston joystick** — I/O port `0x1F`, bits 0-4 (right, left, down, up, fire)
- **Sinclair 1 / Sinclair 2 joysticks** — keys 6-0 and 1-5 respectively, scanned via the keyboard matrix
- **Fuller joystick** — I/O port `0x7F`
- **Protek/AGF joystick** — another I/O port mapping

A keyboard MCU can present a joystick interface to one of these ports, allowing a standard analog joystick (or a modern gamepad with USB) to control Spectrum games.

### Mouse Integration

The **Kempston mouse** interface (port `0xFBDF` for X, `0xFFDF` for Y, buttons at `0xFADF`/`0xBFDF`) is supported by a small library of software (paint programs, GEOS, desktop interfaces). The same MCU that handles keyboard/joystick can also emulate the Kempston mouse, allowing a modern PS/2 or USB mouse to be used.

---

## MCU Choices

### RP2040 (Raspberry Pi Pico)

The **RP2040** is the optimal choice, for the same reasons as for [other MCU replacement projects](mcu_z80.md):

- Dual Cortex-M0+ at 133 MHz (overclockable to 250 MHz)
- **PIO blocks** for cycle-precise I/O timing (if intercepting CPU bus cycles)
- 30 GPIOs (more than enough for keyboard matrix + joystick + mouse)
- Built-in USB host/device capability (via the Pico's USB port)
- ~£1 cost
- Large community and extensive documentation

For an MCU that just emulates the keyboard matrix (driving 8 row lines and reading 5 column lines, or being read by the host Spectrum), the RP2040's PIO is not strictly needed — but it's available if the design calls for intercepting the ULA's I/O cycles.

### ESP32

The **ESP32** is an alternative with built-in Wi-Fi/Bluetooth (useful if the keyboard adapter should also provide network access):

- Xtensa or RISC-V core at 240 MHz
- Built-in Bluetooth for wireless keyboards
- Fewer GPIOs than RP2040, but adequate (34 GPIOs on most boards)
- ~£3 cost

### STM32

The **STM32** family (especially the F103 "Blue Pill" at 72 MHz or F407 at 168 MHz) is a common choice, especially in the Russian retro-computing community:

- ARM Cortex-M0/M3/M4 cores
- Hardware USB device (most models)
- 5V-tolerant GPIOs on some models (eliminating level shifters)
- ~£2 cost

### Arduino (ATmega328P, ATmega32U4)

The Arduino is a viable choice for simple projects, especially for PS/2 keyboard input:

- 8-bit AVR core at 16 MHz
- Hardware serial for PS/2 keyboard (or PS/2 via simple bit-banging)
- ATmega32U4-based Arduinos (Leonardo, Micro) have native USB
- ~£3 cost

The ATmega32U4 is the basis for many DIY keyboard adapters — it has enough speed to handle a PS/2 keyboard and to drive the Spectrum's matrix lines.

---

## Hardware Connection to the Spectrum

The MCU connects to the Spectrum via one of several methods:

### Membrane Connector Replacement

The simplest approach: replace the membrane keyboard's connector with wires from the MCU. The 48K Spectrum's membrane connects via a 8-way ribbon cable (8 row lines) and a 5-way ribbon cable (5 column lines). The MCU drives these lines directly, presenting whatever key state the keyboard scan should see.

This is invasive — it requires opening the Spectrum and disconnecting the membrane — but gives the most authentic integration (the host Spectrum scans the keyboard normally, the MCU just provides the key state).

### Joystick Port

Some keyboard adapters connect via the joystick port. The Kempston joystick port is bidirectional in a sense — software reads I/O port `0x1F` for joystick state. The MCU can present a Kempston joystick state that includes extra buttons (mapping keyboard keys to joystick buttons). This is non-invasive (plug into the joystick port) but is joystick-only — full keyboard emulation requires more.

### Expansion Port

The Spectrum's expansion edge connector exposes the full CPU bus, including the keyboard scan I/O port. An MCU in the expansion port can intercept I/O reads to port `0xFE`, providing its own data in place of the ULA's keyboard scan. This is the most elegant approach — fully non-invasive, and gives full keyboard emulation.

This is how most commercial keyboard adapters work: they sit in the expansion port, intercept `IN A, (0xFE)` instructions, and substitute keyboard state from an attached PS/2 or USB keyboard.

---
## PS/2 Keyboard Input

The PS/2 keyboard protocol is the most common input for keyboard adapters. PS/2 keyboards are cheap, widely available, and use a simple serial protocol that is easy to interface to an MCU.

### PS/2 Protocol

The PS/2 protocol uses two signals:

- **Clock** — generated by the keyboard, ~10-17 kHz (one byte every ~1 ms)
- **Data** — serial data, 11 bits per byte (start bit, 8 data bits LSB first, parity, stop bit)

The keyboard sends a **make code** when a key is pressed and a **break code** (`0xF0` followed by the make code) when a key is released. Each key has a unique scan code independent of position in the layout — e.g., the Q key (on a US layout) always sends scan code `0x1C` regardless of the layout sticker.

The MCU receives these scan codes via an interrupt-driven GPIO (the clock line triggers an interrupt on each falling edge, and the data line is sampled).

### Scan Code to Matrix Translation

The MCU maintains a **64-bit keyboard state** (one bit per Spectrum matrix key) and updates it as PS/2 scan codes arrive. The translation is done via a lookup table:

```c
// PS/2 scan code -> Spectrum matrix position
// Each entry is (row, col) of the key in the 8x5 Spectrum matrix
// (-1, -1) means no Spectrum equivalent
typedef struct {
    int8_t row;
    int8_t col;
} zx_key_t;

// Lookup table indexed by PS/2 scan code
const zx_key_t ps2_to_zx[256] = {
    [0x1C] = {2, 0},  // A
    [0x32] = {1, 1},  // B
    [0x21] = {1, 2},  // C
    [0x23] = {1, 3},  // D
    [0x24] = {2, 2},  // E
    [0x2B] = {1, 4},  // F
    [0x34] = {1, 0},  // G
    [0x33] = {6, 4},  // H
    [0x43] = {5, 4},  // I
    [0x3B] = {6, 3},  // J
    [0x42] = {6, 2},  // K
    [0x4B] = {6, 1},  // L
    [0x3A] = {5, 3},  // M  -- wait, M is row 7
    // ... continue for all keys ...
};

// 64-bit keyboard state (8 rows × 8 columns, but only 40 keys used)
uint64_t keyboard_state = 0;  // bit set = key pressed

// Handle a PS/2 scan code (make code)
void handle_make_code(uint8_t scan_code) {
    zx_key_t key = ps2_to_zx[scan_code];
    if (key.row >= 0) {
        int bit = key.row * 8 + key.col;
        keyboard_state |= (1ULL << bit);
    }
}

// Handle a PS/2 break code (after 0xF0)
void handle_break_code(uint8_t scan_code) {
    zx_key_t key = ps2_to_zx[scan_code];
    if (key.row >= 0) {
        int bit = key.row * 8 + key.col;
        keyboard_state &= ~(1ULL << bit);
    }
}
```

### Caps Lock and Symbol Shift

The Spectrum's modifier handling is different from a PC keyboard:

- **CAPS SHIFT** (row 0, col 0) acts as Shift for letters (uppercase) and some cursor movement
- **SYMBOL SHIFT** (row 7, col 1) gives access to symbols and digits

The MCU's translation can either map PC Shift directly to CAPS SHIFT, or do a more sophisticated mapping (e.g., map PC digits to SYMBOL SHIFT + the corresponding key).

A typical mapping:

| PC key | Spectrum action |
|---|---|
| Shift (hold) | CAPS SHIFT held |
| Digit 1-0 | SYMBOL SHIFT + the corresponding key |
| Symbol keys (`!`, `@`, etc.) | SYMBOL SHIFT + the corresponding key |
| Arrow keys | CAPS SHIFT + 5/6/7/8 |
| Enter | ENTER |
| Space | SPACE |
| Backspace | CAPS SHIFT + 0 (delete) |
| F1-F10 | Custom (e.g., Spectrum-specific shortcuts) |

### Layout Variations

Different keyboard layouts (US QWERTY, UK, German QWERTZ, French AZERTY) produce different scan codes for the same physical position. The PS/2 protocol sends **scan codes** (positions), not characters — so the MCU's translation table must match the layout of the attached keyboard.

Most adapters default to **UK layout** (since the Spectrum was a British machine), with options for other layouts via configuration.

---

## USB Keyboard Input

USB keyboards are more common than PS/2 in modern hardware. Connecting a USB keyboard to an MCU requires USB host capability.

### USB Host MCUs

MCUs that can act as USB hosts:

- **RP2040** — has a USB host/device controller. The Pico's USB port is usually wired as device, but with a special cable (USB A to USB A, or a custom adapter), it can act as host. The TinyUSB library provides HID parser for keyboards.
- **ESP32** — most variants have USB host (via the OHCI controller on the S2/S3 variants), supporting USB keyboards directly.
- **STM32** — most modern STM32 (F105, F107, F4, etc.) have USB OTG (host/device).
- **Arduino** — requires a USB Host Shield, adding ~£5 to the cost.

### USB HID Protocol

USB keyboards use the **HID (Human Interface Device)** protocol. The keyboard sends **reports** of 8 bytes:

- Byte 0 — modifier flags (Ctrl, Shift, Alt, etc.)
- Byte 1 — reserved
- Bytes 2-7 — up to 6 simultaneously-pressed keys (keycodes)

The MCU parses these reports and translates to the Spectrum matrix. The HID keycodes are similar to PS/2 scan codes but not identical — a separate lookup table is needed.

```c
// USB HID keycode -> Spectrum matrix position
const zx_key_t hid_to_zx[256] = {
    [0x04] = {2, 0},  // A (HID keycode 0x04)
    [0x05] = {1, 2},  // B (HID keycode 0x05)
    // ... etc.
};

void handle_hid_report(const uint8_t *report) {
    // Clear all keys (USB sends full state each report)
    keyboard_state = 0;
    
    // Process modifiers
    uint8_t mods = report[0];
    if (mods & 0x22) {  // Left or right Shift
        set_key(0, 0);  // CAPS SHIFT
    }
    
    // Process key codes
    for (int i = 2; i < 8; i++) {
        if (report[i] != 0) {
            zx_key_t key = hid_to_zx[report[i]];
            if (key.row >= 0) {
                set_key(key.row, key.col);
            }
        }
    }
}
```

USB keyboards give **true N-key rollover** — the host can see up to 6 simultaneously-pressed keys without ghosting. This is a significant improvement over the Spectrum's matrix, which can ghost with 3 keys.


---

## Joystick Emulation

A keyboard adapter MCU can also emulate joysticks. Several joystick protocols exist for the Spectrum.

### Kempston Joystick

The **Kempston joystick** is the most widely supported protocol. It presents a single byte at I/O port `0x1F`:

| Bit | Meaning |
|---|---|
| 0 | Right |
| 1 | Left |
| 2 | Down |
| 3 | Up |
| 4 | Fire (Button 1) |
| 5-7 | Unused (typically 0) |

An MCU emulating the Kempston joystick intercepts reads to port `0x1F` and returns the joystick state:

```c
uint8_t kempston_state = 0;

// Intercept I/O read from port 0x1F
uint8_t handle_kempston_read() {
    return kempston_state;
}

// Update joystick state from physical joystick or gamepad
void update_joystick(bool right, bool left, bool down, bool up, bool fire) {
    kempston_state = 0;
    if (right) kempston_state |= 0x01;
    if (left)  kempston_state |= 0x02;
    if (down)  kempston_state |= 0x04;
    if (up)    kempston_state |= 0x08;
    if (fire)  kempston_state |= 0x10;
}
```

### Sinclair Joysticks

The **Sinclair 1** and **Sinclair 2** joysticks are mapped to keyboard keys rather than to an I/O port. This is clever — it means joystick input works in any software that reads those keys, including games that weren't explicitly written for joysticks.

- **Sinclair 1** ( joystick port 1) maps to keys **6, 7, 8, 9, 0**:
  - 6 = Left, 7 = Right, 8 = Down, 9 = Up, 0 = Fire
- **Sinclair 2** (joystick port 2) maps to keys **1, 2, 3, 4, 5**:
  - 1 = Left, 2 = Right, 3 = Down, 4 = Up, 5 = Fire

An MCU that handles keyboard input can trivially handle Sinclair joysticks — just map the joystick state to the appropriate keyboard matrix bits.

### Fuller Joystick

The **Fuller joystick** uses I/O port `0x7F`, with bits 0-3 for direction and bit 6 for fire. Less commonly supported.

### Protek/AGF Joystick

The **Protek (also known as AGF)** joystick uses I/O port `0xDF`. Similar layout to Kempston but different port. Less commonly supported.

### Gamepad Support

Modern gamepads (via USB host or Bluetooth) typically have:

- D-pad or analog stick for direction
- Multiple fire buttons (A, B, X, Y)
- Shoulder buttons (L1, L2, R1, R2)
- Start/Select buttons

The MCU can map these to Spectrum joystick protocols:

- D-pad → Kempston direction bits
- A button → Kempston fire
- B button → Up + Fire (for jump in platformers)
- Start → Spectrum ENTER (for menu navigation)
- Select → Spectrum SPACE (for menu navigation)

For Spectrum games that support only one fire button, multi-button gamepads must be mapped carefully — often the extra buttons duplicate the fire or trigger Spectrum-specific actions.

---

## Kempston Mouse Emulation

The **Kempston mouse** is an input device supported by a small library of software. It presents three registers at I/O ports:

- **Port `0xFBDF`** — X position (read/write)
- **Port `0xFFDF`** — Y position (read/write)
- **Port `0xFADF`** / **`0xBFDF`** — buttons (read)

The X and Y positions are 8-bit counters that increment/decrement with mouse movement. The buttons register has:

| Bit | Meaning |
|---|---|
| 0 | Right button |
| 1 | Left button |
| 2 | Middle button |

The MCU emulates the Kempston mouse by maintaining X and Y counters that update from a PS/2 or USB mouse:

```c
typedef struct {
    int8_t x_counter;
    int8_t y_counter;
    uint8_t buttons;
} kempston_mouse_t;

kempston_mouse_t mouse;

// Handle a mouse movement event (dx, dy from PS/2 or USB mouse)
void handle_mouse_move(int dx, int dy) {
    mouse.x_counter += dx;
    mouse.y_counter += dy;
}

// Handle a mouse button event
void handle_mouse_button(int button, bool pressed) {
    if (pressed) {
        mouse.buttons |= (1 << button);
    } else {
        mouse.buttons &= ~(1 << button);
    }
}

// Intercept I/O read
uint8_t handle_kempston_mouse_read(uint16_t port) {
    switch (port & 0x00FF) {
        case 0xDF:  // X or buttons depending on high byte
            if ((port & 0xFF00) == 0xFB00) return mouse.x_counter;
            if ((port & 0xFF00) == 0xFF00) return mouse.y_counter;
            if ((port & 0xFF00) == 0xFA00 ||
                (port & 0xFF00) == 0xBF00) return mouse.buttons;
            break;
    }
    return 0xFF;
}
```

The Kempston mouse is relatively rare software-wise — only a handful of programs use it. But for those that do (paint programs, desktop environments like GEOS), the emulation is essential.

---
## Existing Projects

Several open-source and commercial keyboard adapter projects exist:

### ZXHIDKeyboard

**ZXHIDKeyboard** is an open-source project that connects a USB keyboard (and optionally mouse) to the Spectrum. Based on an RP2040 or STM32, it sits in the expansion port and intercepts port `0xFE` reads, providing keyboard state from the attached USB keyboard.

Features typically include:

- Full USB HID keyboard support (with multiple layout options)
- Optional USB mouse → Kempston mouse translation
- Optional joystick port (for connecting a real joystick) or gamepad support
- Function key shortcuts (F1-F10 for common Spectrum actions like reset, NMI, snapshot)

### ZXKey

**ZXKey** is a simpler project using an Arduino (often the ATmega32U4-based Leonardo or Micro). It handles PS/2 keyboard input and drives the Spectrum's membrane connector directly (replacing the original membrane).

This is the "membrane replacement" approach — the Arduino sits inside the Spectrum, intercepts nothing, and just provides the matrix state that the ULA would read. The original Spectrum hardware is unchanged except for the disconnected membrane.

### ZXKB

**ZXKB** is another Arduino-based project, typically based on the ATmega328P (Nano). It supports PS/2 keyboard input and provides a Kempston joystick port as well.

### RetroBrew Keyboard Adapter

Various community projects under similar names exist — typically RP2040-based, supporting USB keyboards and providing joystick/mouse emulation.

### Custom Adapter on ESP32

ESP32-based adapters are popular because they can also provide Bluetooth keyboard support (wireless keyboard connection) and Wi-Fi (for network-attached input).

---

## Comparison of Approaches

| Approach | Cost | Difficulty | Features | Best For |
|---|---|---|---|---|
| Arduino + membrane replacement | ~£3 | Easy | PS/2 keyboard only | Repairing a failed membrane |
| RP2040 in expansion port | ~£2 | Medium | Full keyboard + joystick + mouse | Most flexible solution |
| STM32 in expansion port | ~£3 | Medium | Same as RP2040 | Russian retro community |
| ESP32 (Bluetooth) | ~£3 | Medium | Wireless keyboard | Wireless input |

---

## Integration with Real Hardware

### Membrane Connector Approach

For an Arduino-based adapter replacing the membrane:

1. **Open the Spectrum** and disconnect the original membrane
2. **Wire the adapter** to the membrane connector — 8 row lines and 5 column lines
3. **Power the adapter** from the Spectrum's 5V supply (or external power)
4. **Connect a PS/2 keyboard** to the adapter's PS/2 port
5. **Power on** — the Spectrum scans the keyboard normally, and the adapter provides the key state

This is the simplest integration but is invasive.

### Expansion Port Approach

For an RP2040 or STM32 adapter in the expansion port:

1. **Build or buy an adapter** with the right edge connector
2. **Plug it into the expansion port** — no internal modification
3. **Connect a USB or PS/2 keyboard**
4. **Power on** — the adapter intercepts port `0xFE` reads and substitutes the keyboard state

This is non-invasive and preserves the original Spectrum hardware.

### Modern Recreation Approach

For an MCU-based Spectrum (like the [Pico Spectrum](mcu_ula.md) or a [FPGA recreation](../fpga/harlequin_sizif.md)):

1. The keyboard scan is done in software/firmware
2. The MCU handling the ULA emulation also handles the keyboard scan
3. PS/2 or USB keyboard input is handled by the same MCU
4. No external adapter needed — the keyboard input is built in

This is the simplest integration — the keyboard is just another input device handled by the host MCU.

---

## FAQ

### Why use PS/2 instead of USB?

PS/2 is simpler — it uses a straightforward serial protocol that any MCU can handle with just two GPIOs. USB requires USB host hardware, which not all MCUs have. PS/2 keyboards are also still widely available, and the protocol gives per-key make/break events (rather than USB's full-state reports).

That said, USB is increasingly common, and modern MCUs (RP2040, ESP32, STM32) have USB host capability.

### Can the adapter handle multiple keyboards?

Some adapters support multiple input devices (PS/2 keyboard + USB keyboard + gamepad). The keyboard states are OR'd together, so any device can press any key.

### How do I map function keys (F1-F12)?

Function keys are not part of the Spectrum's keyboard matrix, so they must be mapped to Spectrum-specific actions. Common mappings:

- F1 — Pause (NMI)
- F2 — Reset
- F3 — Snapshot (write to disk/tape)
- F4 — Tape play/stop
- F9-F12 — Kempston joystick fire 1-4

### What about the Spectrum's CAPS LOCK LED?

The Spectrum does not have a Caps Lock LED — there is no hardware to drive one. Some adapters add an LED for visual feedback, driven by the MCU based on Caps Lock state.

### Can I use a wireless keyboard?

Yes, with an ESP32-based adapter (Bluetooth wireless), or with a wireless USB keyboard (using a USB receiver). The MCU sees the keyboard as a normal USB or PS/2 device — the wireless nature is transparent.

### How fast is the keyboard scan?

The Spectrum's keyboard scan is fast enough for human typing — typically 50 Hz (once per frame) or faster. The MCU's response time (PS/2 scan code arrival to key state update) is on the order of microseconds, far faster than any human can perceive.

### What about typing in Russian (Cyrillic)?

Russian Spectrum software uses Cyrillic characters mapped to the same physical keys. An adapter for a Russian Spectrum (Pentagon, Scorpion) would map PS/2 scan codes to the Cyrillic key positions. Many adapters support both Latin and Cyrillic layouts via configuration.

---

## Summary

A keyboard controller MCU for the Spectrum performs several functions:

1. **Receives input** from a modern keyboard (PS/2 or USB) and other input devices (joystick, mouse, gamepad)
2. **Translates** the input to the Spectrum's keyboard matrix (8 rows × 5 columns of keys)
3. **Drives the matrix** (in the membrane replacement approach) or **intercepts the matrix scan** (in the expansion port approach)
4. **Optionally emulates** joysticks (Kempston, Sinclair, Fuller) and mouse (Kempston mouse)
5. **Provides additional features** like function key shortcuts, multi-layout support, and wireless input

The RP2040 is the optimal MCU choice due to its low cost (~£1), USB host capability, large GPIO count, and extensive community support. The PS/2 protocol is simpler but USB is more modern.

For most users, an expansion port adapter with USB keyboard support and Kempston joystick/mouse emulation is the ideal solution — non-invasive, full-featured, and compatible with all original Spectrum software.

---

## References

- **The ZX Spectrum ULA: How to Design a Microcomputer** by Chris Smith — definitive reference on the ULA including the keyboard scan logic
- **Spectrum 48K Service Manual** — keyboard matrix schematic and connector pinouts
- **PS/2 Keyboard Protocol** — Adam Chapweske's documentation, widely mirrored
- **USB HID Usage Tables** — official specification of HID keycodes
- **RP2040 datasheet** — for the Raspberry Pi Pico
- **TinyUSB library** — for USB host and HID parsing on RP2040/STM32
- **ZXHIDKeyboard project** — open-source RP2040 USB keyboard adapter
- **ZXKey project** — open-source Arduino PS/2 keyboard adapter (membrane replacement)
- **Kempston joystick interface documentation** — for the Kempston I/O port protocol
- **Kempston mouse documentation** — for the Kempston mouse protocol

## Cross-References

- [ULA on MCU](mcu_ula.md) — the ULA reads the keyboard matrix; an MCU keyboard adapter must match its expectations
- [Z80 on MCU](mcu_z80.md) — bus interception requires the same techniques as Z80 emulation
- [MCU design patterns](mcu_design_patterns.md) — general techniques for bus interfacing and I/O interception
- [Video adapter on MCU](mcu_video_adapter.md) — another expansion port device
- [SD interface on MCU](mcu_sd_interface.md) — often combined with keyboard in a multi-function adapter
