# Generation Metadata: `aliasing_blep.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_aliasing_and_blep()`

```python
def create_aliasing_and_blep():
    fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    
    # High res Z80 clock
    t_z80 = np.linspace(0, 50, 5000)
    z80_wave = (np.sin(t_z80 * 2 * np.pi / 7.3) > 0).astype(float)
    
    axs[0].plot(t_z80, z80_wave, color=THEME['digital'], drawstyle='steps-pre', lw=1.5)
    axs[0].set_ylim(-0.2, 1.2)
    axs[0].set_yticks([0, 1])
    axs[0].set_title('1. Z80 CPU Output (Continuous time, transitions occur at arbitrary sub-sample times)')
    
    # Naive sampling
    sample_points = np.arange(0, 50, 2.0)
    sampled_wave = np.zeros_like(sample_points)
    for i, sp in enumerate(sample_points):
        idx = np.argmin(np.abs(t_z80 - sp))
        sampled_wave[i] = z80_wave[idx]
        
    axs[1].plot(sample_points, sampled_wave, color=THEME['accent'], marker='o', drawstyle='steps-post', lw=1.5)
    for sp in sample_points:
        axs[1].axvline(sp, color=THEME['grid'], alpha=0.3)
    axs[1].set_ylim(-0.2, 1.2)
    axs[1].set_yticks([0, 1])
    axs[1].set_title('2. Naive 48kHz Sampling (Missed edges and varying pulse widths = Phase Jitter / Aliasing)')
    
    import scipy.ndimage
    blep_smooth = scipy.ndimage.gaussian_filter1d(z80_wave, sigma=30)
    
    axs[2].plot(t_z80, blep_smooth, color=THEME['analog'], lw=2)
    axs[2].plot(sample_points, np.interp(sample_points, t_z80, blep_smooth), color=THEME['text'], marker='o', linestyle='none')
    for sp in sample_points:
        axs[2].axvline(sp, color=THEME['grid'], alpha=0.3)
    axs[2].set_ylim(-0.2, 1.2)
    axs[2].set_yticks([0, 1])
    axs[2].set_title('3. Band-Limited Step Synthesis (Smooth mathematical edges prevent aliasing when sampled)')
    
    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/aliasing_blep.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/aliasing_blep.svg', create_aliasing_and_blep)
```
