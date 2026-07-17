# Generation Metadata: `ultrasonic_carrier.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_ultrasonic()`

```python
def create_ultrasonic():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 4), sharex=True)
    t = np.linspace(0, 50, 1000)
    period = 10
    digital = np.where((t % period) < (period * 0.4), 1, 0)
    
    analog = np.zeros_like(t)
    analog[0] = 0.4 
    rc = 50.0  
    for j in range(1, len(t)):
        dt = t[j] - t[j-1]
        analog[j] = analog[j-1] + (digital[j-1] - analog[j-1]) * (1 - np.exp(-dt/rc))
        
    ax1.plot(t, digital, color=THEME['digital'], drawstyle='steps-pre', lw=2)
    ax1.set_ylim(-0.4, 1.5)
    ax1.set_yticks([0, 1])
    ax1.set_ylabel('Digital (78.8 kHz)')
    ax1.set_title('Ultrasonic Toggle (Carrier Frequency)')
    
    texts1 = []
    texts1.append(ax1.text(2, 1.0, '← 18T →', ha='center', color=THEME['text'], bbox=bbox_props))
    texts1.append(ax1.text(7, 0.0, '← 27T →', ha='center', color=THEME['text'], bbox=bbox_props))
    texts1.append(ax1.text(5, 0.5, '←── 45 T-states ──→\none cycle @ 78.8 kHz', ha='center', color=THEME['text'], fontsize=9, bbox=bbox_props))
    adjust_text(texts1, ax=ax1, arrowprops=arrow_props, expand=(1.2, 1.5))
    
    ax2.plot(t, analog, color=THEME['analog'], lw=2)
    ax2.set_ylim(-0.2, 1.2)
    ax2.set_yticks([0, 0.4, 1])
    ax2.set_yticklabels(['rest', '~half displ.', 'max'])
    ax2.set_ylabel('Speaker Hovering\nat Midpoint')
    ax2.set_xlabel('Time')
    
    texts2 = []
    texts2.append(ax2.text(25, 0.4, 'Cone oscillates around its midpoint\nbecause 78.8 kHz is ultrasonic\n(speaker cannot follow individual transitions)',
                 ha='center', color=THEME['text'], bbox=bbox_props))
    adjust_text(texts2, ax=ax2, arrowprops=arrow_props, expand=(1.2, 1.5))
    
    apply_theme(fig, [ax1, ax2])
    plt.tight_layout()
    plt.savefig('assets/ultrasonic_carrier.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/ultrasonic_carrier.svg', create_ultrasonic)
```
