import numpy as np
import matplotlib.pyplot as plt
import os
import inspect

# Create assets directory relative to where the script is executed
os.makedirs('assets', exist_ok=True)

# Set common styling
plt.style.use('dark_background')

# Catppuccin Mocha Theme Definition
THEME = {
    'bg': '#1e1e2e',           # Mocha Base
    'grid': '#313244',         # Surface0
    'digital': '#a6e3a1',      # Green
    'analog': '#89b4fa',       # Blue
    'text': '#cdd6f4',         # Text
    'accent': '#f38ba8',       # Red
    'box_bg': '#181825',       # Mantle (darker than base)
    'box_edge': '#585b70',     # Surface2 (visible frame)
}

def apply_theme(fig, axs):
    fig.patch.set_facecolor(THEME['bg'])
    if not isinstance(axs, (list, np.ndarray)):
        axs = [axs]
    for ax in axs:
        ax.set_facecolor(THEME['bg'])
        ax.grid(True, color=THEME['grid'], alpha=0.8)
        ax.spines['bottom'].set_color(THEME['grid'])
        ax.spines['top'].set_color(THEME['grid'])
        ax.spines['right'].set_color(THEME['grid'])
        ax.spines['left'].set_color(THEME['grid'])
        ax.tick_params(colors=THEME['text'])
        ax.xaxis.label.set_color(THEME['text'])
        ax.yaxis.label.set_color(THEME['text'])
        ax.title.set_color(THEME['text'])

def save_meta(svg_path, func):
    meta_path = svg_path.replace('.svg', '.meta.md')
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(f"# Generation Metadata: `{os.path.basename(svg_path)}`\n\n")
        f.write(f"This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:\n")
        f.write(f"`python3 ../../tools/waveform_generator/generate_fm_waveforms.py`\n\n")
        f.write(f"## Generator Function: `{func.__name__}()`\n\n")
        f.write(f"```python\n")
        f.write(inspect.getsource(func))
        f.write(f"```\n")

def create_fm_waveforms():
    fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    
    t = np.linspace(0, 4 * np.pi, 2000)
    
    # 1. Pure Sine (Carrier only)
    y1 = np.sin(t)
    axs[0].plot(t, y1, color=THEME['analog'], lw=2)
    axs[0].set_title('1. Carrier Only (Pure Sine Wave)', loc='left', color=THEME['text'])
    
    # 2. Carrier + Modulator at 1:1 Ratio (Harmonic)
    I2 = 1.5 # Modulation Index
    y2 = np.sin(t + I2 * np.sin(t))
    axs[1].plot(t, y2, color=THEME['digital'], lw=2)
    axs[1].set_title('2. Carrier + Modulator (Ratio 1:1, Index 1.5) -> Sawtooth-like', loc='left', color=THEME['text'])
    
    # 3. Carrier + Modulator at 1:2 Ratio (Inharmonic / Different timbre)
    I3 = 1.5
    y3 = np.sin(t + I3 * np.sin(2 * t))
    axs[2].plot(t, y3, color=THEME['accent'], lw=2)
    axs[2].set_title('3. Carrier + Modulator (Ratio 1:2, Index 1.5) -> Square/Hollow timbre', loc='left', color=THEME['text'])
    
    # 4. Carrier with Feedback
    y4 = np.zeros_like(t)
    I4 = 1.5
    y_prev = 0
    for i, ti in enumerate(t):
        y4[i] = np.sin(ti + I4 * y_prev)
        y_prev = y4[i]
        
    axs[3].plot(t, y4, color='#f9e2af', lw=2) # Yellow/Gold
    axs[3].set_title('4. Carrier with Feedback -> Rich harmonics / Noise', loc='left', color=THEME['text'])
    
    for ax in axs:
        ax.set_ylim(-1.2, 1.2)
        ax.set_yticks([])
        ax.set_xticks([])
        
    apply_theme(fig, axs)
    plt.tight_layout()
    
    out_path = 'assets/fm_waveforms.svg'
    plt.savefig(out_path, format='svg', transparent=False)
    save_meta(out_path, create_fm_waveforms)
    print(f"✓ {out_path}")

if __name__ == "__main__":
    create_fm_waveforms()
