# Generation Metadata: `click_drum.svg`

This graphic is procedurally generated. To reproduce or modify it, run or edit the source script:
`python3 ../../tools/waveform_generator/generate_waveforms.py`

## Generator Function: `create_click_drum()`

```python
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
```
