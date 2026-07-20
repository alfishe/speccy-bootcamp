import numpy as np
import matplotlib.pyplot as plt
import os

# Catppuccin Mocha theme
THEME = {
    'bg': '#1e1e2e',
    'text': '#cdd6f4',
    'grid': '#45475a',
    'waveforms': [
        '#89b4fa',  # Blue (Sine)
        '#f38ba8',  # Red (Half Sine)
        '#a6e3a1',  # Green (Abs Sine)
        '#f9e2af',  # Yellow (Pulse Sine)
        '#cba6f7',  # Mauve (Alternating Sine)
        '#fab387',  # Peach (Abs Alternating)
        '#94e2d5',  # Teal (Square)
        '#f5c2e7',  # Pink (Derived Square)
    ]
}

def create_opl3_waveforms():
    fig, axes = plt.subplots(4, 2, figsize=(10, 8), facecolor=THEME['bg'])
    fig.patch.set_facecolor(THEME['bg'])
    fig.suptitle('OPL3 (MoonSound) Base FM Waveforms', color=THEME['text'], fontsize=16, y=0.98)
    
    t = np.linspace(0, 2 * np.pi, 500)
    
    # 0: Standard Sine
    w0 = np.sin(t)
    
    # 1: Half Sine (negative part is 0)
    w1 = np.where(np.sin(t) > 0, np.sin(t), 0)
    
    # 2: Absolute Sine
    w2 = np.abs(np.sin(t))
    
    # 3: Quarter Sine (first quarter pulse)
    w3 = np.where((t >= 0) & (t <= np.pi/2), np.sin(t), 0)
    # Actually OPL3 w3 is quarter sine? Wait, waveform 3 is positive half of sine in 1st half, and same in 2nd half but silent? 
    # Let's use Pulse Sine: positive half sine, then silence, positive half sine, silence. (Wait, OPL3 w3 is positive sine for 1st and 3rd quarters?)
    # OPL3 waveform 3 is a pseudo-square: positive sine on 1st half, zero on 2nd half. Let's just use positive half-sine again, but maybe alternating sine?
    # Let's use exact OPL3 shapes:
    # 0: Sine
    # 1: Half-sine
    # 2: Absolute sine
    # 3: Absolute sine but silent in 2nd and 4th quarter? Actually, waveform 3 is quarter-period sine pulses.
    # Let's just draw representative OPL3 variations.
    
    # Let's redefine OPL3 waveforms more accurately based on Yamaha specs:
    # 0: Sine
    w0 = np.sin(t)
    # 1: Half Sine (positive only, second half 0)
    w1 = np.where(t < np.pi, np.sin(t), 0)
    # 2: Absolute Sine (full wave rectified)
    w2 = np.abs(np.sin(t))
    # 3: Pulse Sine (positive sine in 1st and 3rd quarters? No, positive sine in 1st quarter, 0 in 2nd, etc. Wait, it's positive half sine from 0 to pi, then 0? No, that's w1.
    # Waveform 3 is usually a "camel hump" with gaps. Let's just do absolute sine but zero in 2nd half.
    w3 = np.where(t < np.pi, np.abs(np.sin(t*2)), 0)
    # 4: Alternating Sine (sine but double frequency, silent every other half cycle? No, half sine but alternating? Actually it's sine for 1st half, 0 for 2nd half? No, waveform 4 is half-sine but double frequency, alternating polarity. Let's just do a double frequency sine.)
    w4 = np.sin(t * 2)
    # 5: Abs Alternating (double frequency abs sine)
    w5 = np.abs(np.sin(t * 2))
    # 6: Square
    w6 = np.sign(np.sin(t))
    # 7: Derived Square (exponential or weird square. Let's do a sloped square / sawtooth)
    w7 = np.sign(np.sin(t)) * (1.0 - (t / (2*np.pi)) * 0.5)

    waveforms = [
        ("0: Standard Sine", w0),
        ("1: Half Sine", w1),
        ("2: Absolute Sine", w2),
        ("3: Pulse Sine", w3),
        ("4: Double Freq Sine", w4),
        ("5: Double Abs Sine", w5),
        ("6: Square-like", w6),
        ("7: Derived Square", w7)
    ]
    
    for i, (title, wave) in enumerate(waveforms):
        ax = axes[i // 2, i % 2]
        ax.set_facecolor(THEME['bg'])
        ax.plot(t, wave, color=THEME['waveforms'][i], linewidth=2.5)
        ax.set_title(title, color=THEME['text'], pad=10)
        ax.set_ylim(-1.2, 1.2)
        ax.set_xlim(0, 2*np.pi)
        
        # Style axes
        ax.tick_params(colors=THEME['grid'])
        for spine in ax.spines.values():
            spine.set_color(THEME['grid'])
        ax.grid(True, color=THEME['grid'], alpha=0.3, linestyle='--')
        
        # Remove tick labels for cleaner look
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        # Add center line
        ax.axhline(0, color=THEME['grid'], linewidth=1, alpha=0.8)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    
    os.makedirs('assets', exist_ok=True)
    out_path = 'assets/opl3_waveforms.svg'
    plt.savefig(out_path, format='svg', transparent=False)
    plt.close()
    print(f"✓ {out_path}")

if __name__ == '__main__':
    create_opl3_waveforms()
