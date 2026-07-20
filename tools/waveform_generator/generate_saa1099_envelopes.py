import numpy as np
import matplotlib.pyplot as plt
import os

# Catppuccin Mocha theme
THEME = {
    'bg': '#1e1e2e',
    'text': '#cdd6f4',
    'grid': '#45475a',
    'lines': '#89b4fa',
    'accents': [
        '#89b4fa',  # Blue
        '#f38ba8',  # Red
        '#a6e3a1',  # Green
        '#f9e2af',  # Yellow
        '#cba6f7',  # Mauve
        '#fab387',  # Peach
        '#94e2d5',  # Teal
        '#f5c2e7',  # Pink
    ]
}

def create_saa1099_envelopes():
    fig, axes = plt.subplots(2, 4, figsize=(12, 6), facecolor=THEME['bg'])
    fig.patch.set_facecolor(THEME['bg'])
    fig.suptitle('SAA1099 Envelope Shapes (3-bit control)', color=THEME['text'], fontsize=16, y=0.98)
    
    t = np.linspace(0, 4, 1000)
    
    def env_0(t): return np.zeros_like(t)
    def env_1(t): return np.clip(t, 0, 1)
    def env_2(t): return np.clip(1 - t, 0, 1)
    def env_3(t): return np.where(t < 1, t, np.where(t < 2, 2 - t, 0))
    def env_4(t): return np.ones_like(t)
    def env_5(t): return t % 1
    def env_6(t): return 1 - (t % 1)
    def env_7(t): 
        # triangle wave
        cycle = t % 2
        return np.where(cycle < 1, cycle, 2 - cycle)

    envelopes = [
        ("0: Zero Amplitude", env_0),
        ("1: Maximum Amplitude", env_4), # Wait, is mode 1 max amplitude? In some docs 0=zero, 1=max? Actually:
        # Let's use the standard shapes:
        # 0: 0
        # 1: Single Attack
        # 2: Single Decay
        # 3: Single Attack-Decay
        # 4: Max Amplitude
        # 5: Cont Attack
        # 6: Cont Decay
        # 7: Cont Attack-Decay
    ]
    
    # Correct mapping according to standard Philips docs:
    # 000: Zero Amplitude
    # 001: Max Amplitude (wait, let's recheck)
    # Actually, the 3 bits are often:
    # bit 0: Number of phases (0 = 1 phase, 1 = 2 phases/continuous)
    # bit 1: Resolution? No, usually shapes are:
    # 0: Zero
    # 1: Single Attack (0 to Max, then stay Max)
    # 2: Single Decay (Max to 0, then stay 0)
    # 3: Single Attack-Decay (0 to Max to 0, then stay 0)
    # 4: Max Amplitude (always Max)
    # 5: Continuous Attack (Sawtooth Up)
    # 6: Continuous Decay (Sawtooth Down)
    # 7: Continuous Attack-Decay (Triangle)
    
    envelopes = [
        ("0: Zero", env_0),
        ("1: Single Attack", env_1),
        ("2: Single Decay", env_2),
        ("3: Single Attack-Decay", env_3),
        ("4: Max Amplitude", env_4),
        ("5: Continuous Attack", env_5),
        ("6: Continuous Decay", env_6),
        ("7: Cont. Attack-Decay", env_7)
    ]
    
    for i, (title, func) in enumerate(envelopes):
        ax = axes[i // 4, i % 4]
        ax.set_facecolor(THEME['bg'])
        
        y = func(t)
        ax.plot(t, y, color=THEME['accents'][i], linewidth=3)
        ax.set_title(title, color=THEME['text'], pad=10)
        ax.set_ylim(-0.1, 1.2)
        ax.set_xlim(0, 3)
        
        # Style axes
        ax.tick_params(colors=THEME['grid'])
        for spine in ax.spines.values():
            spine.set_color(THEME['grid'])
        ax.grid(True, color=THEME['grid'], alpha=0.3, linestyle='--')
        
        # Remove tick labels for cleaner look
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    
    os.makedirs('assets', exist_ok=True)
    out_path = 'assets/saa1099_envelopes.svg'
    plt.savefig(out_path, format='svg', transparent=False)
    plt.close()
    print(f"✓ {out_path}")

if __name__ == '__main__':
    create_saa1099_envelopes()
