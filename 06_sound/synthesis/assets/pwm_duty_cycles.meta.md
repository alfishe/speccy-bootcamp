# Generation Metadata: `pwm_duty_cycles.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_pwm_duty_cycles()`

```python
def create_pwm_duty_cycles():
    fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    t = np.linspace(0, 100, 2000)
    
    duties = [0.5, 0.25, 0.1]
    titles = ['50% Duty Cycle (Full Volume Square Wave)', '25% Duty Cycle (Quieter)', '10% Duty Cycle (Very Quiet)']
    
    for i, duty in enumerate(duties):
        period = 20
        digital = np.where((t % period) < (period * duty), 1, 0)
        analog = np.zeros_like(t)
        analog[0] = duty 
        rc = 20.0
        for j in range(1, len(t)):
            dt = t[j] - t[j-1]
            analog[j] = analog[j-1] + (digital[j-1] - analog[j-1]) * (1 - np.exp(-dt/rc))
            
        axs[i].plot(t, digital, color=THEME['digital'], drawstyle='steps-pre', alpha=0.5, lw=1, label='Digital')
        axs[i].plot(t, analog, color=THEME['analog'], lw=2, label='Speaker (Average)')
        axs[i].set_ylim(-0.3, 1.3)
        axs[i].set_yticks([0, 1])
        axs[i].set_title(titles[i], loc='left', fontsize=10)
        
        texts = []
        if duty == 0.5:
            texts.append(axs[i].text(50, 0.5, 'max displacement (full cone excursion)', ha='center', color=THEME['text'], bbox=bbox_props))
        elif duty == 0.25:
            texts.append(axs[i].text(50, 0.25, '~half displacement (reduced excursion)', ha='center', color=THEME['text'], bbox=bbox_props))
        elif duty == 0.1:
            texts.append(axs[i].text(50, 0.1, '~20% displacement (barely moving)', ha='center', color=THEME['text'], bbox=bbox_props))

        if texts:
            adjust_text(texts, ax=axs[i], arrowprops=arrow_props, expand=(1.2, 1.5))
            
        if i == 0:
            axs[i].legend(loc='upper right')

    axs[3].set_title('Varying Duty Cycle (Arbitrary Waveform / Sine)', loc='left', fontsize=10)
    sine = (np.sin(t * 2 * np.pi / 100) + 1) / 2
    period = 5
    digital = np.zeros_like(t)
    for j in range(len(t)):
        phase = (t[j] % period) / period
        digital[j] = 1 if phase < sine[j] else 0
        
    analog = np.zeros_like(t)
    analog[0] = sine[0]
    rc = 10.0
    for j in range(1, len(t)):
        dt = t[j] - t[j-1]
        analog[j] = analog[j-1] + (digital[j-1] - analog[j-1]) * (1 - np.exp(-dt/rc))
        
    axs[3].plot(t, digital, color=THEME['digital'], drawstyle='steps-pre', alpha=0.5, lw=1)
    axs[3].plot(t, analog, color=THEME['analog'], lw=2, label='Speaker (Traces the Average)')
    axs[3].plot(t, sine, color=THEME['text'], linestyle='--', alpha=0.5, lw=1, label='Target Waveform')
    axs[3].set_ylim(-0.3, 1.3)
    axs[3].set_yticks([0, 1])
    axs[3].set_xlabel('Time')
    axs[3].legend(loc='upper right', facecolor=bbox_props['facecolor'], edgecolor=bbox_props['edgecolor'])
    
    texts = [axs[3].text(75, 0.5, 'Traces the average', ha='center', color=THEME['text'], bbox=bbox_props)]
    adjust_text(texts, ax=axs[3], arrowprops=arrow_props, expand=(1.2, 1.5))

    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/pwm_duty_cycles.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/pwm_duty_cycles.svg', create_pwm_duty_cycles)
```
