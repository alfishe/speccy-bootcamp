"""
Generate SVG diagrams specific to the Ear Shaver engine analysis.
Uses the same Catppuccin Mocha theme as the main waveform generator.

Run from: /Volumes/TB4-4Tb/Projects/Knowledge/zx/06_sound/synthesis/
Command:  python3 ../../tools/waveform_generator/generate_earshaver.py
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import struct

os.makedirs('assets', exist_ok=True)
plt.style.use('dark_background')

THEME = {
    'bg': '#1e1e2e',
    'grid': '#313244',
    'digital': '#a6e3a1',
    'analog': '#89b4fa',
    'text': '#cdd6f4',
    'accent': '#f38ba8',
    'yellow': '#f9e2af',
    'mauve': '#cba6f7',
    'box_bg': '#181825',
    'box_edge': '#585b70',
}
bbox_props = dict(boxstyle="round,pad=0.4", facecolor=THEME['box_bg'],
                  edgecolor=THEME['box_edge'], alpha=1.0)

def apply_theme(fig, axs):
    fig.patch.set_facecolor(THEME['bg'])
    if not isinstance(axs, (list, np.ndarray)):
        axs = [axs]
    for ax in axs:
        ax.set_facecolor(THEME['bg'])
        ax.grid(True, color=THEME['grid'], alpha=0.5)
        for spine in ax.spines.values():
            spine.set_color(THEME['grid'])
        ax.tick_params(colors=THEME['text'])
        ax.xaxis.label.set_color(THEME['text'])
        ax.yaxis.label.set_color(THEME['text'])
        ax.title.set_color(THEME['text'])


def create_phase_accumulator():
    """Visualize the DDS phase accumulator stepping through a sawtooth wave."""
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    delta = 0x0500  # Frequency delta
    n_samples = 180
    hl_values = np.zeros(n_samples, dtype=np.uint16)
    h_values = np.zeros(n_samples, dtype=np.uint8)

    acc = 0
    for i in range(n_samples):
        hl_values[i] = acc & 0xFFFF
        h_values[i] = (acc >> 8) & 0xFF
        acc = (acc + delta) & 0xFFFF

    t = np.arange(n_samples)

    # Panel 1: Full 16-bit accumulator
    axs[0].plot(t, hl_values, color=THEME['analog'], lw=1.5)
    axs[0].set_ylabel('HL (16-bit)', fontsize=10)
    axs[0].set_title('Phase Accumulator: ADD HL, DE  (DE = #0500)', fontsize=12, fontweight='bold')
    axs[0].set_ylim(-500, 0x10500)
    axs[0].set_yticks([0, 0x4000, 0x8000, 0xC000, 0xFFFF])
    axs[0].set_yticklabels(['#0000', '#4000', '#8000', '#C000', '#FFFF'])

    # Mark the overflow points
    for i in range(1, n_samples):
        if hl_values[i] < hl_values[i-1]:
            axs[0].axvline(i, color=THEME['accent'], alpha=0.6, lw=1, ls='--')
            axs[0].text(i+1, 0xF000, 'overflow', color=THEME['accent'], fontsize=8, rotation=90, va='top')

    # Panel 2: High byte only = sawtooth
    axs[1].plot(t, h_values, color=THEME['digital'], lw=1.5)
    axs[1].set_ylabel('H (high byte)', fontsize=10)
    axs[1].set_title('Extracted Sawtooth Wave: H = HL >> 8', fontsize=12, fontweight='bold')
    axs[1].set_ylim(-10, 265)
    axs[1].set_yticks([0, 64, 128, 192, 255])
    axs[1].axhline(128, color=THEME['accent'], alpha=0.4, ls=':', lw=1)
    axs[1].text(2, 135, 'IXH threshold (128)', color=THEME['accent'], fontsize=9, bbox=bbox_props)

    # Panel 3: After XOR and CP — the PWM output
    xor_mask = 0xE0
    threshold = 128  # IXH
    pwm_output = np.zeros(n_samples, dtype=np.uint8)
    for i in range(n_samples):
        val = h_values[i] ^ xor_mask
        pwm_output[i] = 0xFF if val < threshold else 0x00

    axs[2].fill_between(t, 0, pwm_output, step='pre', color=THEME['yellow'], alpha=0.6)
    axs[2].plot(t, pwm_output, color=THEME['yellow'], drawstyle='steps-pre', lw=1.5)
    axs[2].set_ylabel('OUT (#FE)', fontsize=10)
    axs[2].set_title('PWM Output: (H XOR #E0) compared against IXH, converted via SBC A,A', fontsize=12, fontweight='bold')
    axs[2].set_ylim(-20, 280)
    axs[2].set_yticks([0, 255])
    axs[2].set_yticklabels(['#00 (silent)', '#FF (speaker ON)'])
    axs[2].set_xlabel('Loop Iterations (each = 120 T-states)', fontsize=10)

    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/earshaver_phase_accumulator.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    print('✓ assets/earshaver_phase_accumulator.svg')


def create_pwm_comparison():
    """Show the same sawtooth with different IXH thresholds side by side."""
    thresholds = [224, 192, 128, 64, 32]
    labels = ['IXH=#E0 (88%) — Thin pulse, quiet',
              'IXH=#C0 (75%) — Reedy timbre',
              'IXH=#80 (50%) — Full square wave, loudest',
              'IXH=#40 (25%) — Nasal, thinner',
              'IXH=#20 (12%) — Very quiet, wispy']

    fig, axs = plt.subplots(len(thresholds), 1, figsize=(12, 10), sharex=True)

    delta = 0x0500
    n_samples = 180

    h_values = np.zeros(n_samples, dtype=np.uint8)
    acc = 0
    for i in range(n_samples):
        h_values[i] = (acc >> 8) & 0xFF
        acc = (acc + delta) & 0xFFFF

    for idx, (thresh, label) in enumerate(zip(thresholds, labels)):
        xor_mask = 0xE0
        pwm = np.array([0xFF if (h ^ xor_mask) < thresh else 0x00 for h in h_values])

        # Compute analog average for perceived volume
        rc = 8.0
        analog = np.zeros(n_samples)
        for i in range(1, n_samples):
            target = pwm[i] / 255.0
            analog[i] = analog[i-1] + (target - analog[i-1]) * (1 - np.exp(-1/rc))

        axs[idx].fill_between(range(n_samples), 0, pwm, step='pre',
                              color=THEME['yellow'], alpha=0.3)
        axs[idx].plot(range(n_samples), pwm, color=THEME['yellow'],
                      drawstyle='steps-pre', lw=1, alpha=0.7)
        axs[idx].plot(range(n_samples), analog * 255, color=THEME['analog'],
                      lw=2, label='Perceived volume')
        axs[idx].set_ylim(-20, 280)
        axs[idx].set_yticks([0, 255])
        axs[idx].set_yticklabels(['OFF', 'ON'])
        axs[idx].set_title(label, fontsize=10, fontweight='bold', loc='left')

    axs[-1].set_xlabel('Loop Iterations', fontsize=10)
    fig.suptitle('Duty-Cycle PWM: Varying IXH Threshold Changes Timbre and Volume',
                 fontsize=13, fontweight='bold', color=THEME['text'], y=0.98)

    apply_theme(fig, axs)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('assets/earshaver_pwm_comparison.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    print('✓ assets/earshaver_pwm_comparison.svg')


def create_interleaving():
    """Show the two-channel interleaving timing diagram."""
    fig, axs = plt.subplots(4, 1, figsize=(12, 8), sharex=True)

    # Simulate two channels with different frequencies
    delta_ch1 = 0x0400
    delta_ch2 = 0x0600
    n_samples = 120
    xor1, xor2 = 0xE0, 0xF0
    ixh, ixl = 128, 96

    ch1_out = np.zeros(n_samples)
    ch2_out = np.zeros(n_samples)
    acc1, acc2 = 0, 0

    for i in range(n_samples):
        h1 = (acc1 >> 8) & 0xFF
        ch1_out[i] = 1 if (h1 ^ xor1) < ixh else 0
        acc1 = (acc1 + delta_ch1) & 0xFFFF

        h2 = (acc2 >> 8) & 0xFF
        ch2_out[i] = 1 if (h2 ^ xor2) < ixl else 0
        acc2 = (acc2 + delta_ch2) & 0xFFFF

    t = np.arange(n_samples)

    # Channel 1
    axs[0].plot(t, ch1_out, color=THEME['digital'], drawstyle='steps-pre', lw=2)
    axs[0].fill_between(t, 0, ch1_out, step='pre', color=THEME['digital'], alpha=0.2)
    axs[0].set_ylim(-0.2, 1.4)
    axs[0].set_yticks([0, 1])
    axs[0].set_yticklabels(['OFF', 'ON'])
    axs[0].set_title('Channel 1 (Primary Registers: HL, DE, IXH)', fontsize=11, fontweight='bold', loc='left')

    # Channel 2
    axs[1].plot(t, ch2_out, color=THEME['mauve'], drawstyle='steps-pre', lw=2)
    axs[1].fill_between(t, 0, ch2_out, step='pre', color=THEME['mauve'], alpha=0.2)
    axs[1].set_ylim(-0.2, 1.4)
    axs[1].set_yticks([0, 1])
    axs[1].set_yticklabels(['OFF', 'ON'])
    axs[1].set_title("Channel 2 (Alternate Registers: HL', DE', IXL)", fontsize=11, fontweight='bold', loc='left')

    # Interleaved output at port #FE (what the speaker actually sees)
    interleaved = np.zeros(n_samples * 2)
    for i in range(n_samples):
        interleaved[i*2] = ch1_out[i]
        interleaved[i*2 + 1] = ch2_out[i]

    t_interleaved = np.arange(n_samples * 2) * 0.5
    axs[2].plot(t_interleaved, interleaved, color=THEME['yellow'], drawstyle='steps-pre', lw=1.5, alpha=0.8)
    axs[2].fill_between(t_interleaved, 0, interleaved, step='pre', color=THEME['yellow'], alpha=0.15)
    axs[2].set_ylim(-0.2, 1.4)
    axs[2].set_yticks([0, 1])
    axs[2].set_yticklabels(['OFF', 'ON'])
    axs[2].set_title('Interleaved Output at Port #FE (Ch1, Ch2, Ch1, Ch2...every 60 T-states)',
                      fontsize=11, fontweight='bold', loc='left')

    # Analog reconstruction (what the ear hears)
    analog = np.zeros(len(interleaved))
    rc = 4.0
    for i in range(1, len(interleaved)):
        analog[i] = analog[i-1] + (interleaved[i-1] - analog[i-1]) * (1 - np.exp(-1/rc))

    axs[3].plot(t_interleaved, analog, color=THEME['analog'], lw=2.5)
    axs[3].set_ylim(-0.1, 1.1)
    axs[3].set_yticks([0, 0.5, 1])
    axs[3].set_yticklabels(['0', '0.5', '1.0'])
    axs[3].set_title('Perceived Audio (Speaker averages the 59.1 kHz interleaving)',
                      fontsize=11, fontweight='bold', loc='left')
    axs[3].set_xlabel('Loop Iterations (each = 120 T-states total, 60 T-states per output)', fontsize=10)

    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/earshaver_interleaving.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    print('✓ assets/earshaver_interleaving.svg')


def create_smc_diagram():
    """Show how self-modifying code patches the XOR operand inside the loop."""
    fig, axs = plt.subplots(2, 1, figsize=(12, 5), sharex=True)

    delta = 0x0500
    n_samples = 180

    h_values = np.zeros(n_samples, dtype=np.uint8)
    acc = 0
    for i in range(n_samples):
        h_values[i] = (acc >> 8) & 0xFF
        acc = (acc + delta) & 0xFFFF

    # XOR #E0 vs XOR #80 — dramatically different waveforms from same sawtooth
    for idx, (xor_val, color, title) in enumerate([
        (0xE0, THEME['digital'], 'XOR #E0 (default) — Inverts top 3 bits → asymmetric pulse'),
        (0x80, THEME['accent'],  'XOR #80 (patched via SMC) — Inverts top bit only → different phase'),
    ]):
        threshold = 128
        pwm = np.array([0xFF if (h ^ xor_val) < threshold else 0x00 for h in h_values])

        axs[idx].fill_between(range(n_samples), 0, pwm, step='pre', color=color, alpha=0.3)
        axs[idx].plot(range(n_samples), pwm, color=color, drawstyle='steps-pre', lw=1.5)
        axs[idx].set_ylim(-20, 280)
        axs[idx].set_yticks([0, 255])
        axs[idx].set_yticklabels(['OFF', 'ON'])
        axs[idx].set_title(title, fontsize=11, fontweight='bold', loc='left')

    axs[-1].set_xlabel('Loop Iterations', fontsize=10)
    fig.suptitle('Self-Modifying Code: Patching XOR Operand Changes Timbre Without Branching',
                 fontsize=13, fontweight='bold', color=THEME['text'], y=0.98)

    apply_theme(fig, axs)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('assets/earshaver_smc.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    print('✓ assets/earshaver_smc.svg')


def create_memory_map():
    """Generate a visual memory map of the Ear Shaver snapshot.
    
    Narrow regions get external labels with leader lines to avoid overlap.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    regions = [
        (0x4000, 0x5AFF, 'Screen + Sys Vars',         THEME['grid'],    0.6),
        (0x5B00, 0xCDFF, 'Pattern Data (~29 KB)',      THEME['analog'],  0.7),
        (0xCE00, 0xCFFF, 'Track Select',               THEME['mauve'],   0.7),
        (0xD000, 0xD04C, 'Decompressor',               THEME['yellow'],  0.7),
        (0xD04D, 0xD2D4, 'Player / Sequencer',         THEME['digital'], 0.7),
        (0xD2D5, 0xD34D, 'Synthesis Loop (120T)',       THEME['accent'],  0.9),
        (0xD34E, 0xFFFF, 'Lookup Tables + Stack',       THEME['grid'],    0.5),
    ]

    bar_y = 2.0
    bar_height = 1.2
    min_width_for_inline = 0x1800  # regions narrower than this get external labels

    # Draw all region bars
    for start, end, label, color, alpha in regions:
        width = end - start + 1
        rect = patches.FancyBboxPatch(
            (start, bar_y), width, bar_height,
            boxstyle="round,pad=0", facecolor=color, alpha=alpha,
            edgecolor=THEME['box_edge'], lw=1.5
        )
        ax.add_patch(rect)

    # Place labels: inline for wide regions, external for narrow ones
    # Stagger external labels at different y-levels to avoid overlap
    external_positions = [
        # (region_index, y_offset, ha)
        (2, 4.8, 'center'),   # Track Select — top
        (3, 0.4, 'center'),   # Decompressor — bottom
        (4, 5.4, 'center'),   # Player / Sequencer — top (higher)
        (5, -0.2, 'center'),  # Synthesis Loop — bottom (lower)
    ]
    external_indices = {ep[0] for ep in external_positions}
    ext_map = {ep[0]: (ep[1], ep[2]) for ep in external_positions}

    for idx, (start, end, label, color, alpha) in enumerate(regions):
        width = end - start + 1
        mid_x = start + width / 2

        if idx not in external_indices:
            # Inline label — text inside the bar
            ax.text(mid_x, bar_y + bar_height / 2,
                    f'{label}\n#{start:04X}–#{end:04X}',
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    color='#11111b' if color != THEME['grid'] else THEME['text'])
        else:
            # External label — placed above or below with a leader line
            label_y, ha = ext_map[idx]
            label_text = f'{label}\n#{start:04X}–#{end:04X}'

            ax.annotate(
                label_text,
                xy=(mid_x, bar_y + bar_height if label_y > bar_y else bar_y),
                xytext=(mid_x, label_y),
                ha='center', va='center' if label_y > bar_y else 'top',
                fontsize=9, fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.4', facecolor=THEME['box_bg'],
                          edgecolor=color, alpha=0.95, lw=1.5),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5,
                                connectionstyle='arc3,rad=0.0'),
            )

    ax.set_xlim(0x3800, 0x10800)
    ax.set_ylim(-1.0, 6.5)
    ax.set_yticks([])
    ax.set_xticks([0x4000, 0x6000, 0x8000, 0xA000, 0xC000, 0xD000, 0xE000, 0xFFFF])
    ax.set_xticklabels(['#4000', '#6000', '#8000', '#A000', '#C000', '#D000', '#E000', '#FFFF'])
    ax.set_title('Ear Shaver Memory Map (48K Spectrum)', fontsize=14, fontweight='bold')

    apply_theme(fig, [ax])
    ax.grid(False)
    plt.tight_layout()
    plt.savefig('assets/earshaver_memory_map.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    print('✓ assets/earshaver_memory_map.svg')


def create_counter_vs_dds():
    """Compare decrementing counter pitch quantization vs DDS precision."""
    fig, axs = plt.subplots(2, 1, figsize=(12, 6))

    # Panel 1: Decrementing counter — discrete available frequencies
    loop_tstates = 45  # typical simple loop
    clock = 3546900
    counters = np.arange(5, 80)
    freqs_counter = clock / (counters * loop_tstates * 2)

    axs[0].stem(counters, freqs_counter, linefmt='-', markerfmt='o',
                basefmt=' ')
    # Color the stems
    markerline, stemlines, baseline = axs[0].stem(counters, freqs_counter,
                                                   linefmt='-', markerfmt='o', basefmt=' ')
    plt.setp(stemlines, color=THEME['accent'], alpha=0.6, lw=1)
    plt.setp(markerline, color=THEME['accent'], markersize=3)

    # Highlight the huge gaps at high frequencies
    axs[0].annotate('400 Hz gap!', xy=(6, freqs_counter[1]), xytext=(15, freqs_counter[1]+2000),
                    color=THEME['text'], fontsize=9, bbox=bbox_props,
                    arrowprops=dict(arrowstyle='->', color=THEME['text'], lw=1.5))
    axs[0].set_ylabel('Frequency (Hz)', fontsize=10)
    axs[0].set_title('Decrementing Counter: Only Discrete Pitches Available (huge gaps at high freq)',
                     fontsize=11, fontweight='bold', loc='left')
    axs[0].set_ylim(0, max(freqs_counter) * 1.15)

    # Panel 2: DDS — near-continuous
    deltas = np.arange(0x0100, 0x2000, 1)
    loop_t = 120
    freqs_dds = (clock / loop_t) * (deltas / 65536.0)

    axs[1].plot(deltas, freqs_dds, color=THEME['digital'], lw=2)
    axs[1].set_ylabel('Frequency (Hz)', fontsize=10)
    axs[1].set_xlabel('Pitch Parameter Value', fontsize=10)
    axs[1].set_title('DDS Phase Accumulator: Near-Continuous Pitch (16-bit resolution, 65536 steps per octave)',
                     fontsize=11, fontweight='bold', loc='left')

    axs[1].annotate('Smooth glissando possible', xy=(0x1000, freqs_dds[len(deltas)//2]),
                    xytext=(0x0800, freqs_dds[len(deltas)//2]+100),
                    color=THEME['text'], fontsize=9, bbox=bbox_props,
                    arrowprops=dict(arrowstyle='->', color=THEME['text'], lw=1.5))

    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/earshaver_counter_vs_dds.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    print('✓ assets/earshaver_counter_vs_dds.svg')


def create_envelope_diagram():
    """Visualize how INC HX sweeps the duty cycle over time to create a volume envelope."""
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    n_samples = 400
    delta = 0x0A00
    
    h_values = np.zeros(n_samples, dtype=np.uint8)
    acc = 0
    for i in range(n_samples):
        h_values[i] = (acc >> 8) & 0xFF
        acc = (acc + delta) & 0xFFFF

    # Simulate INC HX over time (envelope sweep from 128 to 255)
    # IXH increases linearly over the n_samples from 128 to 255
    ixh_values = np.linspace(128, 255, n_samples)
    
    xor_mask = 0xE0
    pwm = np.zeros(n_samples, dtype=np.uint8)
    for i in range(n_samples):
        pwm[i] = 0xFF if (h_values[i] ^ xor_mask) < ixh_values[i] else 0x00

    # Panel 1: IXH threshold sweeping up
    axs[0].plot(range(n_samples), ixh_values, color=THEME['accent'], lw=2.5)
    axs[0].fill_between(range(n_samples), 0, ixh_values, color=THEME['accent'], alpha=0.1)
    axs[0].set_ylim(0, 270)
    axs[0].set_yticks([0, 128, 255])
    axs[0].set_yticklabels(['0', '128', '255'])
    axs[0].set_ylabel('IXH Value', fontsize=10)
    axs[0].set_title('Envelope Sweep: IXH increments on each outer loop (INC HX)', fontsize=11, fontweight='bold', loc='left')

    # Panel 2: Resulting PWM wave
    axs[1].fill_between(range(n_samples), 0, pwm, step='pre', color=THEME['yellow'], alpha=0.3)
    axs[1].plot(range(n_samples), pwm, color=THEME['yellow'], drawstyle='steps-pre', lw=1.5)
    axs[1].set_ylim(-20, 280)
    axs[1].set_yticks([0, 255])
    axs[1].set_yticklabels(['OFF', 'ON'])
    axs[1].set_ylabel('OUT (#FE)', fontsize=10)
    axs[1].set_title('Resulting PWM Wave: Duty cycle shrinks as threshold rises', fontsize=11, fontweight='bold', loc='left')

    # Panel 3: Analog average (Volume)
    rc = 8.0
    analog = np.zeros(n_samples)
    for i in range(1, n_samples):
        target = pwm[i] / 255.0
        analog[i] = analog[i-1] + (target - analog[i-1]) * (1 - np.exp(-1/rc))
        
    axs[2].plot(range(n_samples), analog, color=THEME['analog'], lw=2.5)
    axs[2].fill_between(range(n_samples), 0, analog, color=THEME['analog'], alpha=0.2)
    axs[2].set_ylim(0, 1.1)
    axs[2].set_yticks([0, 0.5, 1.0])
    axs[2].set_ylabel('Perceived Vol', fontsize=10)
    axs[2].set_xlabel('Time (Loop Iterations)', fontsize=10)
    axs[2].set_title('Sawtooth Volume Envelope: Sound thins and fades as pulse width approaches 0%', fontsize=11, fontweight='bold', loc='left')

    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/earshaver_envelope.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    print('✓ assets/earshaver_envelope.svg')


if __name__ == '__main__':
    create_phase_accumulator()
    create_pwm_comparison()
    create_interleaving()
    create_smc_diagram()
    create_memory_map()
    create_counter_vs_dds()
    create_envelope_diagram()
    print('\nAll Ear Shaver diagrams generated.')
