# AGENTS.md — Waveform Generator Quality Control

> **Scope:** This rule file applies exclusively to modifications and executions within `tools/waveform_generator/`.

## Purpose
The `generate_waveforms.py` script exists to mathematically simulate and visualize ZX Spectrum 1-bit audio physics and DSP concepts. It replaces the need for ASCII art in documentation.

## Usage Guidelines
When asked to visualize a waveform concept (e.g., a new PWM engine or aliasing artifact), you must:
1. **Never use ASCII art.** Always extend this script or use an existing function.
2. **Execute Locally:** Run the script from the target documentation directory so the `assets/` folder is generated correctly.
   ```bash
   cd zx/06_sound/synthesis
   python3 ../../tools/waveform_generator/generate_waveforms.py
   ```
3. **Selective Generation:** To save time during iteration, pass the specific diagram name to the script:
   ```bash
   python3 ../../tools/waveform_generator/generate_waveforms.py click_drum
   ```

## Quality Control & Modification Rules

When editing `generate_waveforms.py` to add a new diagram, you must strictly adhere to these rules:

1. **Theme Compliance (MANDATORY)**
   - Never hardcode colors like `'red'` or `'blue'`.
   - You MUST use the `THEME` dictionary defined at the top of the script (e.g., `THEME['digital']`, `THEME['analog']`, `THEME['text']`).
   - You MUST call `apply_theme(fig, axs)` before `plt.tight_layout()` to ensure the background and grids match the dark-mode aesthetic.

2. **Annotation Rendering**
   - Never allow text boxes to obscure the data lines.
   - Always use the `adjustText` library to automatically repel text boxes from the data.
   - Set initial text coordinates safely *away* from the lines so `adjustText` can draw clean pointer arrows.

3. **Metadata Enforcement**
   - Every `plt.savefig()` call MUST be immediately followed by `save_meta('assets/filename.svg', create_filename_function)`.
   - This ensures the script automatically drops a `.meta.md` file alongside the SVG, containing the exact `inspect.getsource()` snippet for 100% reproducibility.

4. **CLI Registration**
   - When adding a new generator function, you MUST add it to the `generators` dictionary in the `if __name__ == "__main__":` block so it can be selectively generated via the CLI.
