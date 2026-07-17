# Generation Metadata: `ay_sid_sound.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_ay_sid_sound()`

```python
def create_ay_sid_sound():
    fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    t = np.linspace(0, 100, 1000)
    
    # Ultrasonic Carrier
    carrier = (np.sin(t * 2 * np.pi * 3) > 0).astype(float)
    
    axs[0].plot(t, carrier, color=THEME['digital'], drawstyle='steps-pre', lw=1.5, zorder=1)
    axs[0].set_ylim(-0.2, 1.2)
    axs[0].set_yticks([0, 1])
    axs[0].set_title('1. Ultrasonic Carrier (Period = 0 or 1, ~111 kHz)')
    
    # Zoom-in callout for carrier
    axins = axs[0].inset_axes([0.65, 0.3, 0.3, 0.6])
    axins.set_zorder(10)
    axins.plot(t, carrier, color=THEME['digital'], drawstyle='steps-pre', lw=1.5)
    x1, x2 = 40, 43
    axins.set_xlim(x1, x2)
    axins.set_ylim(-0.2, 1.2)
    axins.set_xticks([])
    axins.set_yticks([])
    axins.set_facecolor(THEME['bg'])
    for spine in axins.spines.values():
        spine.set_color(THEME['accent'])
        spine.set_linewidth(2)
        spine.set_alpha(1.0)
    
    import matplotlib.patches as patches
    
    # Draw the source box manually (x=40..43, y=-0.2..1.2)
    rect = patches.Rectangle((40, -0.2), 3, 1.4, fill=False, edgecolor=THEME['accent'], lw=2, zorder=10)
    axs[0].add_patch(rect)
    
    # Connect top-right of source box to top-left of inset
    con1 = patches.ConnectionPatch(
        xyA=(43, 1.2), xyB=(0, 1), 
        coordsA="data", coordsB="axes fraction",
        axesA=axs[0], axesB=axins, 
        color=THEME['accent'], lw=2, zorder=10
    )
    axs[0].add_artist(con1)
    
    # Connect bottom-right of source box to bottom-left of inset
    con2 = patches.ConnectionPatch(
        xyA=(43, -0.2), xyB=(0, 0), 
        coordsA="data", coordsB="axes fraction",
        axesA=axs[0], axesB=axins, 
        color=THEME['accent'], lw=2, zorder=10
    )
    axs[0].add_artist(con2)
    
    # Target waveform (sine wave)
    target = np.sin(t * 2 * np.pi / 40) * 0.5 + 0.5
    target_quant = np.floor(target * 15) / 15.0
    
    axs[1].plot(t, target_quant, color=THEME['text'], drawstyle='steps-post', lw=1.5, label='Volume Register (4-bit)')
    axs[1].plot(t, target, color=THEME['grid'], linestyle='--', label='Target Analog Wave')
    axs[1].set_ylim(-0.1, 1.1)
    axs[1].set_title('2. Envelope / Volume Modulation (CPU writing 4-bit samples to R8/R9/R10)')
    axs[1].legend(loc='upper right', framealpha=0.9)
    
    # Result: Carrier * Volume
    modulated = carrier * target_quant
    import scipy.ndimage
    speaker = scipy.ndimage.gaussian_filter1d(modulated, sigma=5)
    
    axs[2].plot(t, modulated, color=THEME['digital'], alpha=0.3, drawstyle='steps-pre', lw=1)
    axs[2].plot(t, speaker * 2, color=THEME['analog'], lw=2, label='Speaker Reconstructed Output')
    axs[2].set_ylim(-0.1, 1.1)
    axs[2].set_title('3. SID-Sound Result (Speaker acts as lowpass filter, removing carrier)')
    axs[2].legend(loc='upper right', framealpha=0.9)
    
    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/ay_sid_sound.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/ay_sid_sound.svg', create_ay_sid_sound)
```
