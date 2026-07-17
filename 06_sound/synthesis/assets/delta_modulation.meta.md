# Generation Metadata: `delta_modulation.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_delta_modulation()`

```python
def create_delta_modulation():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
    t = np.linspace(0, 100, 500)
    
    # Target signal (slow sine wave)
    target = np.sin(t * 2 * np.pi / 100)
    
    # Delta modulation
    analog = np.zeros_like(t)
    digital = np.zeros_like(t)
    
    step_size = 0.05
    for i in range(1, len(t)):
        if target[i] > analog[i-1]:
            digital[i] = 1
            analog[i] = analog[i-1] + step_size
        else:
            digital[i] = 0
            analog[i] = analog[i-1] - step_size
            
    ax1.plot(t, target, color=THEME['text'], linestyle='--', alpha=0.5, label='Target Signal (Absolute)')
    ax1.plot(t, analog, color=THEME['analog'], lw=2, label='Reconstructed Signal (Integrated Deltas)')
    ax1.set_ylim(-1.5, 1.5)
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Delta Modulation: Tracking an Absolute Signal with 1-Bit Deltas')
    
    texts1 = []
    texts1.append(ax1.text(25, 1.2, 'Signal rising: Output 1s (+Δ)', ha='center', color=THEME['text'], bbox=bbox_props))
    texts1.append(ax1.text(75, -1.2, 'Signal falling: Output 0s (-Δ)', ha='center', color=THEME['text'], bbox=bbox_props))
    adjust_text(texts1, ax=ax1, arrowprops=arrow_props, expand=(1.2, 1.5))
    ax1.legend(loc='upper right', facecolor=bbox_props['facecolor'], edgecolor=bbox_props['edgecolor'])
    
    # Just draw steps
    ax2.plot(t, digital, color=THEME['digital'], drawstyle='steps-pre', lw=1.5)
    ax2.set_ylim(-0.4, 1.4)
    ax2.set_yticks([0, 1])
    ax2.set_ylabel('1-Bit Delta Stream\n(1=Up, 0=Down)')
    ax2.set_xlabel('Time')
    
    apply_theme(fig, [ax1, ax2])
    plt.tight_layout()
    plt.savefig('assets/delta_modulation.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/delta_modulation.svg', create_delta_modulation)
```
