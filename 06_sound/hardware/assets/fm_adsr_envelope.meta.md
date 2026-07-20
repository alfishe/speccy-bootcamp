# Generation Metadata: `fm_adsr_envelope.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_turbosound.py`

## Generator Function: `create_fm_adsr()`

```python
def create_fm_adsr():
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Points:
    # A starts at 0, ends at peak (127) at t=1
    # D goes from peak down to sustain level (e.g. 70) at t=3
    # S stays at sustain level until t=7
    # R goes from sustain level down to 0 at t=9
    t_points = [0, 1, 3, 7, 9]
    v_points = [0, 127, 70, 70, 0]
    
    ax.plot(t_points, v_points, color=THEME['analog'], linewidth=3)
    ax.fill_between(t_points, v_points, alpha=0.2, color=THEME['analog'])
    
    # Draw vertical dashed lines for phases
    ax.axvline(1, color=THEME['grid'], linestyle='--', alpha=0.8)
    ax.axvline(3, color=THEME['grid'], linestyle='--', alpha=0.8)
    ax.axvline(7, color=THEME['grid'], linestyle='--', alpha=0.8)
    
    # Draw sustain level horizontal dashed line
    ax.axhline(70, color=THEME['grid'], linestyle=':', alpha=0.8)
    
    # Labels for phases
    ax.text(0.5, 60, 'Attack', ha='center', va='center', color=THEME['text'], fontsize=12)
    ax.text(2.0, 95, 'Decay', ha='center', va='center', color=THEME['text'], fontsize=12)
    ax.text(5.0, 35, 'Sustain', ha='center', va='center', color=THEME['text'], fontsize=12)
    ax.text(8.0, 35, 'Release', ha='center', va='center', color=THEME['text'], fontsize=12)
    
    # Key on/off labels
    ax.annotate('Key On', xy=(0, 0), xytext=(-0.5, -20),
                arrowprops=dict(arrowstyle="->", color=THEME['accent']),
                color=THEME['accent'], ha='center', va='top')
                
    ax.annotate('Key Off', xy=(7, 70), xytext=(7.5, 90),
                arrowprops=dict(arrowstyle="->", color=THEME['accent']),
                color=THEME['accent'], ha='center', va='bottom')
                
    # Formatting
    ax.set_ylim(-5, 140)
    ax.set_xlim(-1, 10)
    ax.set_yticks([0, 70, 127])
    ax.set_yticklabels(['0', 'Sustain Level', '127 (Max)'])
    ax.set_xticks([])
    
    ax.set_ylabel('Output Level')
    ax.set_title('FM Operator ADSR Envelope Generator')
    
    apply_theme(fig, ax)
    plt.tight_layout()
    
    out_path = 'assets/fm_adsr_envelope.svg'
    plt.savefig(out_path, format='svg', transparent=False)
    save_meta(out_path, create_fm_adsr)
    print(f"✓ {out_path}")
```
