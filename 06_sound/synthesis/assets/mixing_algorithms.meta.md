# Generation Metadata: `mixing_algorithms.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_mixing_algorithms()`

```python
def create_mixing_algorithms():
    fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    t = np.linspace(0, 100, 1000)
    
    # Generate two frequencies
    ch_a = (np.sin(t * 2 * np.pi / 20) > 0).astype(int)
    ch_b = (np.sin(t * 2 * np.pi / 33) > 0).astype(int)
    
    axs[0].plot(t, ch_a, color=THEME['digital'], drawstyle='steps-pre', lw=1.5, label='Ch A')
    axs[0].plot(t, ch_b + 1.5, color=THEME['accent'], drawstyle='steps-pre', lw=1.5, label='Ch B')
    axs[0].set_ylim(-0.4, 3.0)
    axs[0].set_yticks([0, 1, 1.5, 2.5])
    axs[0].set_yticklabels(['0', '1', '0', '1'])
    axs[0].set_title('Original Channels (A and B)')
    
    # XOR Mixing
    xor_out = ch_a ^ ch_b
    axs[1].plot(t, xor_out, color=THEME['digital'], drawstyle='steps-pre', lw=1.5)
    axs[1].set_ylim(-0.4, 1.4)
    axs[1].set_yticks([0, 1])
    axs[1].set_title('1. Logical XOR Mixing (Creates dense, chaotic intermodulation distortion)')
    
    # Interleaved
    interleaved = np.zeros_like(t)
    for i in range(len(t)):
        interleaved[i] = ch_a[i] if (i // 5) % 2 == 0 else ch_b[i]
    
    rc = 5.0
    analog_tdm = np.zeros_like(t)
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        analog_tdm[i] = analog_tdm[i-1] + (interleaved[i-1] - analog_tdm[i-1]) * (1 - np.exp(-dt/rc))
        
    axs[2].plot(t, interleaved, color=THEME['digital'], alpha=0.3, drawstyle='steps-pre', lw=1)
    axs[2].plot(t, analog_tdm, color=THEME['analog'], lw=2, label='Speaker Average')
    axs[2].set_ylim(-0.4, 1.4)
    axs[2].set_yticks([0, 1])
    axs[2].set_title('2. Time-Division Multiplexing (Speaker naturally averages rapidly interleaved channels)')
    
    # PWM DAC
    # Sum is 0, 1, or 2
    sum_val = ch_a + ch_b
    pwm = np.zeros_like(t)
    for i in range(len(t)):
        cycle = i % 4
        if sum_val[i] == 0:
            pwm[i] = 0
        elif sum_val[i] == 1:
            pwm[i] = 1 if cycle == 0 else 0
        else:
            pwm[i] = 1 if cycle in (0, 2) else 0
            
    analog_pwm = np.zeros_like(t)
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        analog_pwm[i] = analog_pwm[i-1] + (pwm[i-1] - analog_pwm[i-1]) * (1 - np.exp(-dt/rc))
        
    axs[3].plot(t, pwm, color=THEME['digital'], alpha=0.3, drawstyle='steps-pre', lw=1)
    axs[3].plot(t, analog_pwm * 2, color=THEME['analog'], lw=2, label='Speaker Output')
    axs[3].plot(t, sum_val/2, color=THEME['text'], linestyle='--', alpha=0.5, label='Target Sum')
    axs[3].set_ylim(-0.4, 1.4)
    axs[3].set_yticks([0, 0.5, 1])
    axs[3].set_yticklabels(['0', '1', '2 (sum)'])
    axs[3].set_title('3. Pre-Summing & PWM (Fast density patterns cleanly reconstruct the mixed amplitude)')
    
    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/mixing_algorithms.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/mixing_algorithms.svg', create_mixing_algorithms)
```
