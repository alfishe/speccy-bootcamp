# Generation Metadata: `ay_buzzer_bass.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_ay_buzzer_bass()`

```python
def create_ay_buzzer_bass():
    fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    t = np.linspace(0, 100, 1000)
    
    # Tone
    tone = (np.sin(t * 2 * np.pi / 8.0) > 0).astype(float)
    axs[0].plot(t, tone, color=THEME['digital'], drawstyle='steps-pre', lw=1.5)
    axs[0].set_ylim(-0.2, 1.2)
    axs[0].set_yticks([0, 1])
    axs[0].set_title('1. Tone Generator (e.g. 110 Hz)')
    
    # Envelope
    env = (t % 8.5) / 8.5
    env = 1.0 - env
    axs[1].plot(t, env, color=THEME['text'], lw=1.5)
    axs[1].set_ylim(-0.2, 1.2)
    axs[1].set_title('2. Envelope Generator (e.g. 104 Hz Sawtooth)')
    
    # Interference
    out = tone * env
    import scipy.ndimage
    perceived = scipy.ndimage.gaussian_filter1d(out, sigma=3)
    
    axs[2].plot(t, out, color=THEME['digital'], alpha=0.3, drawstyle='steps-pre', lw=1)
    axs[2].plot(t, perceived * 2.0, color=THEME['analog'], lw=2, label='Perceived Squelch / Beating')
    axs[2].set_ylim(-0.2, 1.2)
    axs[2].set_title('3. Phase Interference (Buzzer Bass) — Frequencies drift in and out of alignment')
    axs[2].legend(loc='upper right', framealpha=0.9)
    
    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/ay_buzzer_bass.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/ay_buzzer_bass.svg', create_ay_buzzer_bass)
```
