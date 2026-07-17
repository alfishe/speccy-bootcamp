# Generation Metadata: `ay_frequency_ranges.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_ay_frequency_ranges()`

```python
def create_ay_frequency_ranges():
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Ranges based on 1.7734 MHz clock
    ranges = [
        ('Envelope (16-bit)\n0.1 Hz - 6.9 kHz', 0.105, 6927, THEME['analog'], 2),
        ('Tone (12-bit)\n27 Hz - 110 kHz', 27.06, 110837, THEME['digital'], 1),
        ('Noise (5-bit)\n3.5 kHz - 110 kHz', 3575, 110837, THEME['accent'], 0)
    ]
    
    for label, min_f, max_f, color, y in ranges:
        ax.plot([min_f, max_f], [y, y], color=color, lw=20, solid_capstyle='butt', alpha=0.8)
        ax.text(min_f, y + 0.3, label, color=color, va='bottom', ha='left', fontsize=9, fontweight='bold')
        
    ax.set_xscale('log')
    # add human hearing range indicator
    ax.axvspan(20, 20000, color=THEME['grid'], alpha=0.1)
    ax.text(600, -0.8, 'Human Hearing Range (20 Hz - 20 kHz)', color=THEME['text'], alpha=0.5, ha='center')
    
    ax.set_xlim(0.05, 200000)
    ax.set_ylim(-1, 3)
    ax.set_yticks([])
    ax.set_xlabel('Frequency (Hz) - Log Scale')
    ax.set_title('AY-3-8910 Physical Frequency Working Ranges (ZX Spectrum Clock: 1.7734 MHz)')
    
    apply_theme(fig, [ax])
    plt.tight_layout()
    plt.savefig('assets/ay_frequency_ranges.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/ay_frequency_ranges.svg', create_ay_frequency_ranges)
```
