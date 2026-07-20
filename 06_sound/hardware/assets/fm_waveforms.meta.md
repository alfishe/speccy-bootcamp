# Generation Metadata: `fm_waveforms.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_fm_waveforms.py`

## Generator Function: `create_fm_waveforms()`

```python
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
```
