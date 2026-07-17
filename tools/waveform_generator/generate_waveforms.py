import numpy as np
import matplotlib.pyplot as plt
import os
import inspect
from adjustText import adjust_text

# Create assets directory relative to where the script is executed
os.makedirs('assets', exist_ok=True)

# Set common styling
plt.style.use('dark_background')

# Set common styling
plt.style.use('dark_background')

# Catppuccin Mocha Theme Definition
THEME = {
    'bg': '#1e1e2e',           # Mocha Base
    'grid': '#313244',         # Surface0
    'digital': '#a6e3a1',      # Green
    'analog': '#89b4fa',       # Blue
    'text': '#cdd6f4',         # Text
    'accent': '#f38ba8',       # Red
    'box_bg': '#181825',       # Mantle (darker than base)
    'box_edge': '#585b70',     # Surface2 (visible frame)
}

bbox_props = dict(boxstyle="round,pad=0.4", facecolor=THEME['box_bg'], edgecolor=THEME['box_edge'], alpha=1.0)
arrow_props = dict(arrowstyle="-|>", color=THEME['box_edge'], lw=1.5)

def apply_theme(fig, axs):
    fig.patch.set_facecolor(THEME['bg'])
    if not isinstance(axs, (list, np.ndarray)):
        axs = [axs]
    for ax in axs:
        ax.set_facecolor(THEME['bg'])
        ax.grid(True, color=THEME['grid'], alpha=0.8)
        ax.spines['bottom'].set_color(THEME['grid'])
        ax.spines['top'].set_color(THEME['grid'])
        ax.spines['right'].set_color(THEME['grid'])
        ax.spines['left'].set_color(THEME['grid'])
        ax.tick_params(colors=THEME['text'])
        ax.xaxis.label.set_color(THEME['text'])
        ax.yaxis.label.set_color(THEME['text'])
        ax.title.set_color(THEME['text'])

def save_meta(svg_path, func):
    meta_path = svg_path.replace('.svg', '.meta.md')
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(f"# Generation Metadata: `{os.path.basename(svg_path)}`\n\n")
        f.write(f"This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:\n")
        f.write(f"`python3 ../../tools/waveform_generator/generate_waveforms.py`\n\n")
        f.write(f"## Generator Function: `{func.__name__}()`\n\n")
        f.write(f"```python\n")
        f.write(inspect.getsource(func))
        f.write(f"```\n")

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

def create_click_drum():
    fig, ax = plt.subplots(1, 1, figsize=(10, 3))
    t = np.linspace(0, 100, 2000)
    digital = np.zeros_like(t)
    
    np.random.seed(42)
    for j in range(len(t)):
        if t[j] < 30 or t[j] > 70:
            if (t[j] % 10) < 1:  
                digital[j] = 1
            elif (t[j] % 15) < 1: 
                digital[j] = 1
        else:
            if np.random.rand() > 0.5:
                digital[j] = 1
                
    ax.plot(t, digital, color=THEME['digital'], drawstyle='steps-pre', lw=1.5)
    ax.axvspan(30, 70, color=THEME['accent'], alpha=0.2, label='Drum Interruption (Clicks)')
    ax.set_ylim(-0.4, 1.4)
    ax.set_yticks([0, 1])
    ax.set_title('Click Drum Interrupting Tone Channels')
    
    texts = []
    texts.append(ax.text(15, 1.0, 'Normal loop tone', ha='center', color=THEME['text'], bbox=bbox_props))
    texts.append(ax.text(50, 0.0, 'Drum replaces tone momentarily', ha='center', color=THEME['text'], bbox=bbox_props))
    texts.append(ax.text(85, 1.0, 'Normal loop tone', ha='center', color=THEME['text'], bbox=bbox_props))
    adjust_text(texts, ax=ax, arrowprops=arrow_props, expand=(1.2, 1.5))

    ax.legend(loc='upper right', facecolor=bbox_props['facecolor'], edgecolor=bbox_props['edgecolor'])
    
    apply_theme(fig, [ax])
    plt.tight_layout()
    plt.savefig('assets/click_drum.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    save_meta('assets/click_drum.svg', create_click_drum)

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

if __name__ == "__main__":
    import argparse

    generators = {
        'single_pulse': create_single_pulse,
        'pwm_duty_cycles': create_pwm_duty_cycles,
        'ultrasonic': create_ultrasonic,
        'click_drum': create_click_drum,
        'delta_modulation': create_delta_modulation,
        'mixing': create_mixing_algorithms,
        'aliasing': create_aliasing_and_blep,
        'ay_pwm': create_ay_pwm,
        'ay_sid_sound': create_ay_sid_sound,
        'ay_buzzer_bass': create_ay_buzzer_bass,
        'ay_freq_ranges': create_ay_frequency_ranges
    }

    parser = argparse.ArgumentParser(
        description="Generate 1-bit synthesis waveform SVG diagrams.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'diagrams', 
        nargs='*', 
        default=['all'], 
        choices=list(generators.keys()) + ['all'],
        help="Specify which diagram to generate, or 'all' for everything."
    )
    args = parser.parse_args()

    targets = list(generators.keys()) if 'all' in args.diagrams else args.diagrams

    for target in targets:
        print(f"Generating {target}...")
        generators[target]()
        print(f"✓ Created assets/{target}.svg and assets/{target}.meta.md")
