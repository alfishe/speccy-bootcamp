"""
Generate SVG diagrams specific to the Covox & SounDrive engine analysis.
Uses the Catppuccin Mocha theme.

Run from: /Volumes/TB4-4Tb/Projects/Knowledge/zx/06_sound/hardware/
Command:  python3 ../../tools/waveform_generator/generate_covox.py
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

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
bbox_props = dict(boxstyle="round,pad=0.4", facecolor=THEME['box_bg'], edgecolor=THEME['box_edge'], alpha=1.0)

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

def create_dac_resolution_comparison():
    """Compare 1-bit, 4-bit, and 8-bit DAC resolution."""
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    
    t = np.linspace(0, 2*np.pi, 200)
    ideal = np.sin(t)
    
    # 1-bit (Beeper)
    bit1 = np.where(ideal >= 0, 1.0, -1.0)
    axs[0].plot(t, bit1, color=THEME['accent'], drawstyle='steps-mid', lw=2)
    axs[0].plot(t, ideal, color=THEME['text'], alpha=0.3, ls='--')
    axs[0].set_title('1-Bit DAC (ZX Spectrum Beeper): Only 2 states. High distortion.', fontsize=12, fontweight='bold', loc='left')
    axs[0].set_ylim(-1.5, 1.5)
    axs[0].set_yticks([-1, 1])
    
    # 4-bit (AY-3-8910)
    # AY is actually logarithmic, but let's show a generic 4-bit linear for simplicity,
    # or actually let's show a 16-level curve
    levels_4bit = 16
    bit4 = np.round((ideal + 1) / 2 * (levels_4bit - 1)) / (levels_4bit - 1) * 2 - 1
    axs[1].plot(t, bit4, color=THEME['yellow'], drawstyle='steps-mid', lw=2)
    axs[1].plot(t, ideal, color=THEME['text'], alpha=0.3, ls='--')
    axs[1].set_title('4-Bit DAC (AY-3-8910 Volume Regs): 16 states. Noticeable stepping (quantization noise).', fontsize=12, fontweight='bold', loc='left')
    axs[1].set_ylim(-1.5, 1.5)
    axs[1].set_yticks([-1, 0, 1])
    
    # 8-bit (Covox)
    levels_8bit = 256
    bit8 = np.round((ideal + 1) / 2 * (levels_8bit - 1)) / (levels_8bit - 1) * 2 - 1
    axs[2].plot(t, bit8, color=THEME['digital'], drawstyle='steps-mid', lw=2)
    axs[2].plot(t, ideal, color=THEME['text'], alpha=0.3, ls='--')
    axs[2].set_title('8-Bit DAC (Covox / SounDrive): 256 states. Nearly perfect analog reconstruction.', fontsize=12, fontweight='bold', loc='left')
    axs[2].set_ylim(-1.5, 1.5)
    axs[2].set_yticks([-1, 0, 1])
    axs[2].set_xlabel('Time', fontsize=11)
    
    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/covox_dac_resolution.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    print('✓ assets/covox_dac_resolution.svg')

def create_software_vs_hardware_mixing():
    """Visualize Software Mixing (Covox) vs Hardware Mixing (SounDrive)."""
    fig, axs = plt.subplots(2, 1, figsize=(12, 8))
    
    # Let's draw timelines
    # Software Mixing: Read1, Read2, Read3, Read4, Add, Add, Add, Div, Out
    axs[0].set_xlim(0, 100)
    axs[0].set_ylim(0, 2)
    axs[0].axis('off')
    
    axs[0].text(2, 1.6, 'Single Covox (Z80 Software Mixing)', color=THEME['text'], fontsize=14, fontweight='bold')
    axs[0].text(2, 1.2, 'The Z80 must do all the math. Output is delayed by dozens of T-states, tanking sample rate.', color=THEME['text'], fontsize=10)
    
    # Draw blocks for software mixing
    blocks_soft = [
        (10, 10, 'LD A,(Ch1)', THEME['digital']),
        (20, 10, 'ADD (Ch2)', THEME['yellow']),
        (30, 10, 'ADD (Ch3)', THEME['mauve']),
        (40, 10, 'ADD (Ch4)', THEME['analog']),
        (50, 15, 'RRA x 2 (Div)', THEME['grid']),
        (65, 10, 'OUT (Covox)', THEME['accent'])
    ]
    
    for x, w, label, color in blocks_soft:
        rect = patches.Rectangle((x, 0.4), w-1, 0.6, facecolor=color, edgecolor=THEME['bg'], lw=2)
        axs[0].add_patch(rect)
        axs[0].text(x + w/2, 0.7, label, ha='center', va='center', color='#11111b', fontsize=8, fontweight='bold')
    
    # Bracket showing total time
    axs[0].annotate('', xy=(10, 0.2), xytext=(75, 0.2), arrowprops=dict(arrowstyle='<->', color=THEME['text']))
    axs[0].text(42.5, 0.05, '~80+ T-states per combined sample', ha='center', va='top', color=THEME['text'], fontsize=10)


    # Hardware Mixing: Out1, Out2, Out3, Out4
    axs[1].set_xlim(0, 100)
    axs[1].set_ylim(0, 2)
    axs[1].axis('off')
    
    axs[1].text(2, 1.6, 'SounDrive (Hardware Op-Amp Mixing)', color=THEME['text'], fontsize=14, fontweight='bold')
    axs[1].text(2, 1.2, 'The Z80 just throws bytes at ports. The analog Op-Amps add the voltages instantly.', color=THEME['text'], fontsize=10)
    
    blocks_hard = [
        (10, 10, 'OUTI (Ch1)', THEME['digital']),
        (20, 10, 'OUTI (Ch2)', THEME['yellow']),
        (30, 10, 'OUTI (Ch3)', THEME['mauve']),
        (40, 10, 'OUTI (Ch4)', THEME['analog'])
    ]
    
    for x, w, label, color in blocks_hard:
        rect = patches.Rectangle((x, 0.4), w-1, 0.6, facecolor=color, edgecolor=THEME['bg'], lw=2)
        axs[1].add_patch(rect)
        axs[1].text(x + w/2, 0.7, label, ha='center', va='center', color='#11111b', fontsize=8, fontweight='bold')

    # Op amp sum indicator
    axs[1].annotate('Analog Circuit\nmixes voltages\nINSTANTLY', xy=(55, 0.7), xytext=(65, 0.7), 
                    arrowprops=dict(arrowstyle='<-', color=THEME['accent'], lw=2),
                    va='center', color=THEME['accent'], fontsize=10, fontweight='bold')

    # Bracket showing total time
    axs[1].annotate('', xy=(10, 0.2), xytext=(50, 0.2), arrowprops=dict(arrowstyle='<->', color=THEME['text']))
    axs[1].text(30, 0.05, 'Much faster! High sample rates possible.', ha='center', va='top', color=THEME['digital'], fontsize=10)
    
    apply_theme(fig, axs)
    plt.tight_layout()
    plt.savefig('assets/soundrive_mixing_comparison.svg', format='svg', facecolor=fig.get_facecolor())
    plt.close()
    print('✓ assets/soundrive_mixing_comparison.svg')


if __name__ == '__main__':
    create_dac_resolution_comparison()
    create_software_vs_hardware_mixing()
    print('\nAll Covox diagrams generated.')
