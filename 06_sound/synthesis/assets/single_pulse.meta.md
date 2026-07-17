# Generation Metadata: `single_pulse.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_single_pulse()`

```python
def create_single_pulse():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 4), sharex=True)
    t = np.linspace(0, 100, 1000)
    digital = np.zeros_like(t)
    digital[(t >= 20) & (t < 40)] = 1
    
    analog = np.zeros_like(t)
    rc_up = 0.1 
    rc_down = 15.0 
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        rc = rc_up if digital[i-1] > analog[i-1] else rc_down
        analog[i] = analog[i-1] + (digital[i-1] - analog[i-1]) * (1 - np.exp(-dt/rc))
        
    ax1.plot(t, digital, color=THEME['digital'], drawstyle='steps-pre', lw=2)
    ax1.set_ylim(-0.4, 1.4)
    ax1.set_yticks([0, 1])
    ax1.set_ylabel('Digital Port #FE')
    ax1.set_title('A Single Beep: Digital Pulse vs Physical Speaker Response')
    
    texts1 = []
    # Place text above the pulse line
    texts1.append(ax1.text(30, 1.3, '← OUT (bit 4=1) →', ha='center', color=THEME['text'], bbox=bbox_props))
    # Place text above the low line
    texts1.append(ax1.text(70, 0.4, '← XOR, OUT (bit 4=0) →', ha='center', color=THEME['text'], bbox=bbox_props))
    texts1.append(ax1.text(30, 0.5, '~18T', ha='center', color=THEME['text'], bbox=bbox_props))
    texts1.append(ax1.text(50, 0.5, '~15T', ha='center', color=THEME['text'], bbox=bbox_props))
    # adjustText pushes text to avoid lines
    adjust_text(texts1, ax=ax1, arrowprops=arrow_props, expand=(1.2, 1.5))

    ax2.plot(t, analog, color=THEME['analog'], lw=2)
    ax2.set_ylim(-0.2, 1.2)
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['rest', 'max'])
    ax2.set_ylabel('Speaker Cone\nDisplacement')
    ax2.set_xlabel('Time')
    
    texts2 = []
    # Place safely to the left and high
    texts2.append(ax2.text(10, 1.0, 'Cone pushed out by voltage...', ha='center', color=THEME['text'], bbox=bbox_props))
    # Place safely to the right and high
    texts2.append(ax2.text(80, 0.8, '...then slowly returns via rubber surround', ha='center', color=THEME['text'], bbox=bbox_props))
    adjust_text(texts2, ax=ax2, arrowprops=arrow_props, expand=(1.2, 1.5))

    apply_theme(fig, [ax1, ax2])
    plt.tight_layout()
    plt.savefig('assets/single_pulse.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/single_pulse.svg', create_single_pulse)
```
