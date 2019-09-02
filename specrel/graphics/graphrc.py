"""Default parameters shared by various classes and functions in
`specrel.graphics`.
"""

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
"""
## Items
#### Top-level
- **fig**: `None`
    - Matplotlib figure to draw on.
- **ax**: `None`
    - Single Matplotlib axis to draw on.
- **axs**: `None`
    - List of Matplotlib axes to draw on.
- **grid**: `False`
    - Flag for whether or not to plot background grid lines.
- **legend**: False
    - Flag for whether or not to plot a legend.
- **legend_loc**: 'best'
    - Legend location according to the Matplotlib `loc` parameter.
- **title**: None
    - Plot title.
- **tlabel**: 'Time (seconds)'
    - Plot y-axis label (corresponding to the time axis).
- **xlabel**: 'Position (light-seconds)'
    - Plot x-axis label (corresponding to the position axis).
#### Worldline
- **worldline.lim_padding**: 0.1
    - Extra padding on spacetime diagram axis limits, relative to the axis
        sizes.
- **worldline.equal_lim_expand**: 1
    - If the limits on an axis are specified to be equal, they will be expanded
        symmetrically until the axis size is this value.
#### Animators
- **anim.fps**: 50
    - Animation frames per second.
- **anim.display_current**: True
    - Flag for displaying the current "control value" (e.g. time or velocity)
        in each animation frame.
- **anim.display_current_decimals**: 3
    - Number of decimals to display the current control value to.
- **anim.time.ct_per_sec**: 1
    - Amount of time to pass within an animation for every second of real time.
- **anim.time.instant_pause_time**: 1
    - Amount of animation pause time in seconds for instantaneous events.
- **anim.transform.time**: 0
    - Time value to fix while animating a Lorentz transformation.
- **anim.transform.transition_duration**: 2
    - Real-time duratio in seconds of a Lorentz transform animation.
- **anim.worldline.current_time_style**: '--'
    - Matplotlib linestyle for the line of current in animated spacetime plot.
- **anim.worldline.current_time_color**: 'red'
    - Matplotlib color for the line of current time in animated spacetime plot.
"""
