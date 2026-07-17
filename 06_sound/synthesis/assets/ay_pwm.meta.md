# Generation Metadata: `ay_pwm.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_ay_pwm()`

```python
def create_ay_pwm():
    fig, axs = plt.subplots(2, 1, figsize=(10, 4), sharex=True)
    t = np.linspace(0, 100, 1000)
    
    # 1. Normal AY Square Wave (50% duty)
    period = 20
    ay_normal = (np.floor(t / period) % 2).astype(int)
    
    axs[0].plot(t, ay_normal, color=THEME['digital'], drawstyle='steps-pre', lw=1.5)
    axs[0].set_ylim(-0.2, 1.2)
    axs[0].set_yticks([0, 1])
    axs[0].set_title('1. Normal AY Generator (Locked to 50% duty cycle)')
    
    # 2. Sync-Square PWM
    loop = 35
    ay_pwm = np.zeros_like(t)
    for i, time in enumerate(t):
        phase = time % loop
        if phase < period:
            ay_pwm[i] = 1
        else:
            ay_pwm[i] = 0
            
    axs[1].plot(t, ay_pwm, color=THEME['accent'], drawstyle='steps-pre', lw=1.5)
    axs[1].set_ylim(-0.2, 1.2)
    axs[1].set_yticks([0, 1])
    axs[1].set_title('2. Sync-Square PWM (CPU forces phase reset before natural cycle ends, creating thin pulse)')
    
    for sync_t in np.arange(0, 100, loop):
        axs[1].axvline(sync_t, color=THEME['text'], linestyle='--', alpha=0.5)
        
    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/ay_pwm.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/ay_pwm.svg', create_ay_pwm)
```
