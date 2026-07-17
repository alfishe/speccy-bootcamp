# 1-Bit Waveform & Synthesis Generator

The **Waveform Generator** is a Python-based visualization tool designed specifically to illustrate 1-bit audio synthesis concepts. It simulates how discrete digital logic (like the ZX Spectrum's ULA port `#FE`) interacts with the physical inertia of a speaker cone. 

## 🎯 Goal

The primary goal of this tool is to replace static ASCII art and hand-drawn approximations with mathematically accurate, scalable vector graphics (SVG). By applying an RC lowpass filter approximation to digital pulse trains, the tool visually proves how ultrasonic switching frequencies and Pulse-Width Modulation (PWM) translate into physical speaker movement and audible tone generation. 

## ✨ Capabilities

The script currently features four specialized visualization engines, each producing a distinct SVG diagram:

1. **`create_single_pulse()`**: Demonstrates the atomic unit of 1-bit sound. It plots a fast digital pulse alongside the speaker's asymmetrical physical response (fast cone excursion driven by voltage, slow return via the rubber surround).
2. **`create_pwm_duty_cycles()`**: Visualizes the core of 1-bit synthesis. It compares 50%, 25%, and 10% duty cycles to show how average displacement changes. It also plots a varying duty cycle against a target sine wave, demonstrating how pulse density traces arbitrary analog waveforms.
3. **`create_ultrasonic()`**: Illustrates the concept of an ultrasonic carrier. It plots a 78.8 kHz toggle loop (the theoretical maximum on a 48K Spectrum) and proves that the physical speaker cannot follow the transitions, resulting in the cone hovering at a midpoint without producing audible sound.
4. **`create_click_drum()`**: Visualizes channel interruption. It shows standard interleaved tone channels being momentarily hijacked by dense, pseudo-random toggles to synthesize percussion (a "click drum").

**Automatic Layout Engine**: The tool utilizes the `adjustText` library to automatically calculate non-overlapping bounding boxes for all annotations. Text boxes intelligently repel from data lines, meaning waveforms can be altered without manually readjusting text coordinates.

**Accessible Color Palette (Catppuccin Mocha)**: To ensure readability across all devices and GitHub themes (both Light and Dark modes), the script explicitly enforces a solid dark background. The entire visual language is controlled by a centralized `THEME` dictionary at the top of the script:
- **Base/Background**: `#1e1e2e` (Mocha Base)
- **Grid & Spines**: `#313244` (Surface0)
- **Digital Signals**: `#a6e3a1` (Green - sharp, high contrast)
- **Analog Signals**: `#89b4fa` (Blue - smooth)
- **Text**: `#cdd6f4` (Text)
- **Accent/Highlights**: `#f38ba8` (Red)
- **Annotation Background**: `#181825` (Mantle - a slightly darker shade than the base to make the text boxes distinct but integrated)
- **Annotation Frames & Arrows**: `#585b70` (Surface2 - provides a crisp, visible border and pointer without clashing)

## 🛠 Usage Scenarios

You should use and extend this tool when:
- **Documenting New Engines**: When writing articles about novel beeper engines (e.g., Octode, Phaser, Squeeker), use this tool to visualize their specific pulse-interleaving or PFM (Pulse Frequency Modulation) patterns.
- **Visualizing Hardware Artifacts**: If documenting audio artifacts (like ULA contention gaps or frame-rendering delays), you can simulate these gaps in the digital array and visualize the resulting drop in speaker displacement.
- **Comparing Filters**: The script uses a configurable RC filter (`rc_up` / `rc_down`). You can adjust these values to visualize how different speakers (e.g., the 48K's internal speaker vs. the 128K's television output) respond differently to the same code.

## 🚀 Installation & Usage

**Prerequisites:**
- Python 3.x
- `numpy` (for array/waveform math)
- `matplotlib` (for rendering)
- `adjustText` (for automatic annotation collision avoidance)

**Setup:**
```bash
pip install numpy matplotlib adjustText
```

**Running the Tool:**
Execute the script from the directory where you want the `assets/` folder to be generated. By default, running the script with no arguments generates **all** diagrams.

```bash
cd 06_sound/synthesis
python3 ../../tools/waveform_generator/generate_waveforms.py
```

**Selectively Generating Diagrams:**
If you are tweaking a specific diagram and don't want to wait for all of them to render, you can specify exactly which diagrams to regenerate using CLI arguments:

```bash
# Generate only the click drum diagram
python3 ../../tools/waveform_generator/generate_waveforms.py click_drum

# Generate multiple specific diagrams
python3 ../../tools/waveform_generator/generate_waveforms.py single_pulse ultrasonic
```
Available targets: `single_pulse`, `pwm_duty_cycles`, `ultrasonic`, `click_drum`, `delta_modulation`, `all`.

## 📄 Managing Metadata Files

Every time a diagram is generated, the tool automatically dumps a corresponding `.meta.md` file right next to the SVG in the `assets/` directory (e.g., `assets/click_drum.meta.md`).

**Why is this important?**
- **Reproducibility**: You never have to guess how an image was generated. The `.meta.md` file automatically uses `inspect.getsource()` to dump the *exact* Python function code that generated that specific iteration of the SVG.
- **Portability**: The meta file includes the exact CLI command used to trigger the generation. If a diagram needs a slight color or axis adjustment months later, the exact recipe is stored right beside the result.

## 🧩 Extending the Tool (Examples)

To add a new visualization, create a new function following this standard pattern:

```python
def create_custom_engine_view():
    fig, ax = plt.subplots(1, 1, figsize=(10, 3))
    t = np.linspace(0, 100, 2000)
    
    # 1. Define your digital pulse train
    digital = np.zeros_like(t)
    digital[(t % 10) < 2] = 1  # Example pattern
    
    # 2. Simulate physical speaker inertia (RC Filter)
    analog = np.zeros_like(t)
    rc = 10.0
    for j in range(1, len(t)):
        dt = t[j] - t[j-1]
        analog[j] = analog[j-1] + (digital[j-1] - analog[j-1]) * (1 - np.exp(-dt/rc))
        
    # 3. Plot both signals
    ax.plot(t, digital, color=color_digital, drawstyle='steps-pre', label='Digital Signal')
    ax.plot(t, analog, color=color_analog, label='Speaker Cone')
    
    # 4. Add smart annotations
    texts = [ax.text(50, 0.5, "My Custom Engine", color=color_text)]
    adjust_text(texts, ax=ax, arrowprops=arrow_props)
    
    # 5. Save and cleanup
    plt.tight_layout()
    plt.savefig('assets/custom_engine.svg', format='svg', transparent=True)
    plt.close()
```
Don't forget to call your new function at the bottom of the script.
