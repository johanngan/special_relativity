"""Graphics default config parameters"""

# Commonly used default parameters shared by multiple graphics classes
graphrc = {
    'fig': None,
    'ax': None,
    'axs': None,
    'grid': False,
    'legend': False,
    'legend_loc': 'best',
    'title': None,
    'tlabel': 'Time (seconds)',
    'xlabel': 'Position (light-seconds)',
    'worldline.lim_padding': 0.1,
    'worldline.equal_lim_expand': 1,
    'anim.fps': 50,
    'anim.display_current': True,
    'anim.display_current_decimals': 3,
    'anim.time.ct_per_sec': 1,
    'anim.time.instant_pause_time': 1,
    'anim.transform.time': 0,
    'anim.transform.transition_duration': 2,
    'anim.worldline.current_time_style': '--',
    'anim.worldline.current_time_color': 'red',
}