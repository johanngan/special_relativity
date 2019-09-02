"""Visualization tools for special relativity.

Common spacetime visualization functions with API that's less general than
`specrel.graphics`, but easier to use. These functions handle much of the
nitty-gritty interfacing with the core graphics API automatically.

All `visualization` functions adhere to the same style of usage:

1. Pass in a `specrel.geom.LorentzTransformable` to plot or animate, along with
a variety of keyword arguments controlling plot specifications.
2. Some sort of plotter, animator, or list thereof is returned, on which `show`
and `save` methods can be called to show the plot interactively or save it to
a file, respectively.

Core graphics code is in `specrel.graphics`.
"""

import copy

import matplotlib.pyplot as plt

import specrel.geom as geom
from specrel.graphics.graphrc import graphrc
import specrel.graphics.simpgraph as simpg
import specrel.graphics.compgraph as compg

# Commonly used default values shared by multiple visualize functions
visrc = {
    'default_fig_max_height': 10,
    'default_fig_max_width': 10,
}
"""
Contains default parameters shared by various `visualize` functions.

## Items
- **default_fig_max_height**: `10`
    - Maximum total figure height for functions that create new Matplotlib
        figures. Corresponds to the first element of the `figsize` parameter.
    - Figure height will be equal to this unless the width is a bigger
        bottleneck at a given aspect ratio, in which case figure height will be
        less.
- **default_fig_max_width**: `10`
    - Maximum total figure width for functions that create new Matplotlib
        figures. Corresponds to the first element of the `figsize` parameter.
    - Figure width will be equal to this unless the height is a bigger
        bottleneck at a given aspect ratio, in which case figure width will be
        less.
"""

def _prepare_fig_and_axs(fig, axs, nrow, ncol, rect, w_pad=None, h_pad=None):
    """Prepare a default figure and subplot axis set in tight layout, if both
    the given fig and axs are None."""
    # Create new figure
    if fig is None and axs is None:
        # Determine the "unit side length" based on max height and width
        # parameters, and the number of rows and columns in the subplot
        unit = min(visrc['default_fig_max_height']/nrow,
            visrc['default_fig_max_width']/ncol)
        fig, axs = plt.subplots(nrow, ncol, figsize=(ncol*unit, nrow*unit))
        # Return axis list in flattened, row-major format
        axs = axs.flatten()
        fig.tight_layout(rect=rect, w_pad=w_pad, h_pad=h_pad)
    # Can't have half a specification
    elif fig is None or axs is None:
        raise ValueError('Must give both figure and axes, or neither.')
    return fig, axs

def stplot(lorentz_transformable,
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=graphrc['fig'],
    ax=graphrc['ax'],
    grid=graphrc['grid'],
    legend=graphrc['legend'],
    legend_loc=graphrc['legend_loc'],
    lim_padding=graphrc['worldline.lim_padding'],
    equal_lim_expand=graphrc['worldline.equal_lim_expand'],
    title=graphrc['title'],
    **kwargs):
    """Plots the spacetime plot of a `specrel.geom.LorentzTransformable`.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            plot.
        tlim (tuple, optional): Time drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        xlim (tuple, optional): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        fig (matplotlib.figure.Figure, optional): Figure window. See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        ax (matplotlib.axes.Axes, optional): Plotting axes. See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        grid (bool, optional): Flag for whether or not to plot background grid
            lines.
        legend (bool, optional): Flag for whether or not to plot a legend.
        legend_loc (str, optional): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this parameter is ignored.
        lim_padding (float, optional): Extra padding on spacetime diagram axis
            limits, relative to the axis sizes.
        equal_lim_expand (float, optional): If the limits on an axis are
            specified to be equal, they will be expanded symmetrically until the
            axis size is this value.
        title (str, optional): Plot title.
        **kwargs: Keyword arguments to forward to Matplotlib when drawing the
            object.

    Returns:
        specrel.graphics.simpgraph.WorldlinePlotter:
            Plotter for the spacetime diagram of the object.
    """
    plotter = simpg.WorldlinePlotter(
        fig=fig,
        ax=ax,
        grid=grid,
        legend=legend,
        legend_loc=legend_loc,
        lim_padding=lim_padding,
        equal_lim_expand=equal_lim_expand)
    lorentz_transformable.draw(plotter=plotter, tlim=tlim, xlim=xlim, **kwargs)
    plotter.set_labels()
    if title:
        plotter.ax.set_title(title)
    return plotter

def stanimate(lorentz_transformable,
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=graphrc['fig'],
    ax=graphrc['ax'],
    grid=graphrc['grid'],
    legend=graphrc['legend'],
    legend_loc=graphrc['legend_loc'],
    ct_per_sec=graphrc['anim.time.ct_per_sec'],
    instant_pause_time=graphrc['anim.time.instant_pause_time'],
    fps=graphrc['anim.fps'],
    display_current_time=graphrc['anim.display_current'],
    display_current_time_decimals=
        graphrc['anim.display_current_decimals'],
    title=graphrc['title'],
    **kwargs):
    """Animates a `specrel.geom.LorentzTransformable` in real space.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            animate.
        tlim (tuple, optional): Time drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        xlim (tuple, optional): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        fig (matplotlib.figure.Figure, optional): Figure window. See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        ax (matplotlib.axes.Axes, optional): Plotting axes. See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        grid (bool, optional): Flag for whether or not to plot background grid
            lines.
        legend (bool, optional): Flag for whether or not to plot a legend.
        legend_loc (str, optional): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this parameter is ignored.
        ct_per_sec (float, optional): Amount of time to pass within an animation
            for every second of real time.
        instant_pause_time (float, optional): Amount of pause time in seconds
            for instantaneous events (appear in a single instant of time).
        fps (float, optional): Animation frames per second.
        display_current_time (bool, optional): Flag for displaying the time of
            the current animation frame.
        display_current_time_decimals (int, optional): Number of decimals to
            display the current time to. If `display_current_time` is `False`,
            this parameter is ignored.
        title (str, optional): Animation title.
        **kwargs: Keyword arguments to forward to Matplotlib when drawing the
            object.

    Returns:
        specrel.graphics.simpgraph.ObjectAnimator:
            Animator for the real space animation of the object.
    """
    animator = simpg.ObjectAnimator(
        fig=fig,
        ax=ax,
        grid=grid,
        legend=legend,
        legend_loc=legend_loc,
        ct_per_sec=ct_per_sec,
        instant_pause_time=instant_pause_time,
        fps=fps,
        display_current_time=display_current_time,
        display_current_time_decimals=display_current_time_decimals,
        title=title)
    lorentz_transformable.draw(plotter=animator, tlim=tlim, xlim=xlim, **kwargs)
    return animator

def _override_tlim(tlim_base, tlim_override):
    """Override None entries of tlim_base with those in tlim_override."""
    return tuple([override if override is not None else base
        for base, override in zip(tlim_base, tlim_override)])

def stanimate_with_worldline(lorentz_transformable,
    tlim_anim=geom.geomrc['tlim'],
    tlim_worldline=geom.geomrc['tlim'],
    tlim=(None, None),
    xlim=geom.geomrc['xlim'],
    fig=graphrc['fig'],
    axs=graphrc['axs'],
    grid=graphrc['grid'],
    legend=graphrc['legend'],
    legend_loc=graphrc['legend_loc'],
    ct_per_sec=graphrc['anim.time.ct_per_sec'],
    instant_pause_time=graphrc['anim.time.instant_pause_time'],
    fps=graphrc['anim.fps'],
    display_current_time=graphrc['anim.display_current'],
    display_current_time_decimals=
        graphrc['anim.display_current_decimals'],
    title=graphrc['title'],
    lim_padding=graphrc['worldline.lim_padding'],
    equal_lim_expand=graphrc['worldline.equal_lim_expand'],
    current_time_style=graphrc['anim.worldline.current_time_style'],
    current_time_color=graphrc['anim.worldline.current_time_color'],
    **kwargs):
    """Animates a `specrel.geom.LorentzTransformable` alongside an animated
    spacetime diagram.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            animate.
        tlim_anim (tuple, optional): Time drawing limits for the animation
            itself.
        tlim_worldline (tuple, optional): Time drawing limits for the spacetime
            diagram. See `specrel.geom.LorentzTransformable.draw`.
        tlim (tuple, optional): Time drawing limits for both the animation and
            the spacetime diagram. Entries that are not `None` override those
            in `tlim_anim` and `tlim_worldline`.
        xlim (tuple, optional): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        fig (matplotlib.figure.Figure, optional): Figure window. If `None`, a
            new figure window is created.
        axs (list, optional): List of axes in row major format. If `None`, a
            new set of axes is created under a new figure window.
        grid (bool, optional): Flag for whether or not to plot background grid
            lines.
        legend (bool, optional): Flag for whether or not to plot a legend.
        legend_loc (str, optional): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this parameter is ignored.
        ct_per_sec (float, optional): Amount of time to pass within an animation
            for every second of real time.
        instant_pause_time (float, optional): Amount of pause time in seconds
            for instantaneous events (appear in a single instant of time).
        fps (float, optional): Animation frames per second.
        display_current_time (bool, optional): Flag for displaying the time of
            the current animation frame.
        display_current_time_decimals (int, optional): Number of decimals to
            display the current time to. If `display_current_time` is `False`,
            this parameter is ignored.
        title (str, optional): Animation title.
        lim_padding (float, optional): Extra padding on spacetime diagram axis
            limits, relative to the axis sizes.
        equal_lim_expand (float, optional): If the limits on an axis are
            specified to be equal, they will be expanded symmetrically until the
            axis size is this value.
        current_time_style (linestyle, optional): Matplotlib linestyle for the
            line of current time in animated spacetime plot.
        current_time_color (color, optional): Matplotlib color for the line of
            current time in animated spacetime plot.
        **kwargs: Keyword arguments to forward to Matplotlib when drawing the
            object.

    Returns:
        specrel.graphics.compgraph.MultiTimeAnimator:
            Animator for the spacetime diagram + real space animation of the
            object.
    """
    # Make new figure if necessary
    fig, axs = _prepare_fig_and_axs(fig, axs, 1, 2,
        rect=[0.03, 0.03, 1, 0.89], w_pad=0)

    tlim_anim = _override_tlim(tlim_anim, tlim)
    tlim_worldline = _override_tlim(tlim_worldline, tlim)

    animator = compg.MultiTimeAnimator(
        [
            {
                'animator': simpg.WorldlineAnimator,
                'animator_options':
                {
                    'title': 'Spacetime Diagram',
                    'grid': grid,
                    'legend': legend,
                    'legend_loc': legend_loc,
                    'lim_padding': lim_padding,
                    'equal_lim_expand': equal_lim_expand,
                    'current_time_style': current_time_style,
                    'current_time_color': current_time_color,
                },
                'transformable': copy.deepcopy(lorentz_transformable),
                'draw_options': {'tlim': tlim_worldline, 'xlim': xlim,
                    **kwargs},
            },
            {
                'animator': simpg.ObjectAnimator,
                'animator_options': {
                    'grid': grid,
                    'legend': legend,
                    'legend_loc': legend_loc,
                    'title': 'Actual Scene',
                },
                'transformable': copy.deepcopy(lorentz_transformable),
                'draw_options': {'tlim': tlim_worldline, 'xlim': xlim,
                    **kwargs},
            },
        ],
        fig=fig,
        axs=axs,
        tlim=tlim_anim,
        ct_per_sec=ct_per_sec,
        instant_pause_time=instant_pause_time,
        fps=fps,
        display_current_time=display_current_time,
        display_current_time_decimals=display_current_time_decimals,
        title=title)
    return animator

def _get_transformable_and_vrel_in_all_frames(lorentz_transformable, vrels,
    origin):
    """Return lists of a LorentzTransformable and vrels in different frames,
    where the input vrels can be a scalar or a list of values."""
    transformables = [lorentz_transformable]
    try:
        transformables += [geom.lorentz_transformed(
            lorentz_transformable, vrel, origin) for vrel in vrels]
        return transformables, vrels
    except TypeError:
        # Single vrel
        transformables += [geom.lorentz_transformed(
            lorentz_transformable, vrels, origin)]
        return transformables, [vrels]

def _check_axs_match_frames(axs, nplots):
    """Raise error if there's a mismatch between number of plots to make and
    number of axes to plot onto."""
    # Make there are the right number of axes for the number of frames
    if len(axs) != nplots:
        raise ValueError('Number of axes much match number of frame plots,'
            + ' including for the lab frame.'
            + f' {len(axs)} axes given, {nplots} needed.')

def compare_frames(lorentz_transformable,
    vrels,
    origin=geom.geomrc['origin'],
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=graphrc['fig'],
    axs=graphrc['axs'],
    grid=graphrc['grid'],
    legend=graphrc['legend'],
    legend_loc=graphrc['legend_loc'],
    lim_padding=graphrc['worldline.lim_padding'],
    equal_lim_expand=graphrc['worldline.equal_lim_expand'],
    title=graphrc['title'],
    **kwargs):
    """Plots the spacetime diagrams of a `specrel.geom.LorentzTransformable` in
    some number of different frames moving at some relative velocity to a lab
    frame.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            plot.
        vrels (list): List of relative velocities of frames to compare with the
            lab frame.
        origin (tuple, optional): Origin used for Lorentz transformations, in
            the form (t, x).
        tlim (tuple, optional): Time drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        xlim (tuple, optional): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        fig (matplotlib.figure.Figure, optional): Figure window. If `None`, a
            new figure window is created.
        axs (list, optional): List of axes in row major format. If `None`, a
            new set of axes is created under a new figure window.
        grid (bool, optional): Flag for whether or not to plot background grid
            lines.
        legend (bool, optional): Flag for whether or not to plot a legend.
        legend_loc (str, optional): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this parameter is ignored.
        lim_padding (float, optional): Extra padding on spacetime diagram axis
            limits, relative to the axis sizes.
        equal_lim_expand (float, optional): If the limits on an axis are
            specified to be equal, they will be expanded symmetrically until the
            axis size is this value.
        title (str, optional): Plot title.
        **kwargs: Keyword arguments to forward to Matplotlib when drawing the
            object.

    Returns:
        list:
            List of `specrel.graphics.simpgraph.WorldlinePlotter` objects, one
            for the object plotted in each reference frame.
    """
    transformables, vrels = _get_transformable_and_vrel_in_all_frames(
        lorentz_transformable, vrels, origin)

    # Make new figure if necessary
    fig, axs = _prepare_fig_and_axs(fig, axs, 1, len(transformables),
        rect=[0.03, 0.03, 1, 0.93], w_pad=3)

    _check_axs_match_frames(axs, len(transformables))

    plotters = []
    for ax, transformable in zip(axs, transformables):
        plotter = simpg.WorldlinePlotter(
            fig=fig,
            ax=ax,
            grid=grid,
            legend=legend,
            legend_loc=legend_loc,
            lim_padding=lim_padding,
            equal_lim_expand=equal_lim_expand)
        transformable.draw(plotter=plotter, tlim=tlim, xlim=xlim, **kwargs)
        plotter.set_labels()
        plotters.append(plotter)
    axs[0].set_title('Lab Frame')
    for ax, vrel in zip(axs[1:], vrels):
        ax.set_title(f'Frame Moving at ${vrel:.3g}c$')
    if title:
        fig.suptitle(title)
    return tuple(plotters)

def compare_frames_animated(lorentz_transformable,
    vrels,
    origin=geom.geomrc['origin'],
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=graphrc['fig'],
    axs=graphrc['axs'],
    grid=graphrc['grid'],
    legend=graphrc['legend'],
    legend_loc=graphrc['legend_loc'],
    ct_per_sec=graphrc['anim.time.ct_per_sec'],
    instant_pause_time=graphrc['anim.time.instant_pause_time'],
    fps=graphrc['anim.fps'],
    display_current_time=graphrc['anim.display_current'],
    display_current_time_decimals=
        graphrc['anim.display_current_decimals'],
    title=graphrc['title'],
    **kwargs):
    """Animates a `specrel.geom.LorentzTransformable` in some number of
    different frames moving at some relative velocity to a lab frame.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            animate.
        vrels (list): List of relative velocities of frames to compare with the
            lab frame.
        origin (tuple, optional): Origin used for Lorentz transformations, in
            the form (t, x).
        tlim (tuple, optional): Time drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        xlim (tuple, optional): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        fig (matplotlib.figure.Figure, optional): Figure window. If `None`, a
            new figure window is created.
        axs (list, optional): List of axes in row major format. If `None`, a
            new set of axes is created under a new figure window.
        grid (bool, optional): Flag for whether or not to plot background grid
            lines.
        legend (bool, optional): Flag for whether or not to plot a legend.
        legend_loc (str, optional): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this parameter is ignored.
        ct_per_sec (float, optional): Amount of time to pass within an animation
            for every second of real time.
        instant_pause_time (float, optional): Amount of pause time in seconds
            for instantaneous events (appear in a single instant of time).
        fps (float, optional): Animation frames per second.
        display_current_time (bool, optional): Flag for displaying the time of
            the current animation frame.
        display_current_time_decimals (int, optional): Number of decimals to
            display the current time to. If `display_current_time` is `False`,
            this parameter is ignored.
        title (str, optional): Animation title.
        **kwargs: Keyword arguments to forward to Matplotlib when drawing the
            object.

    Returns:
        specrel.graphics.compgraph.MultiTimeAnimator:
            Animator for the object animated in real space in each of the
            different reference frames.
    """
    transformables, vrels = _get_transformable_and_vrel_in_all_frames(
        lorentz_transformable, vrels, origin)

    # Make new figure if necessary
    fig, axs = _prepare_fig_and_axs(fig, axs, 1, len(transformables),
        rect=[0.03, 0.03, 1, 0.89], w_pad=0)

    _check_axs_match_frames(axs, len(transformables))

    ax_titles = ['Scene in Lab Frame'] + \
        [f'Scene in Frame Moving at ${vrel:.3g}c$' for vrel in vrels]
    draw_options = {'tlim': tlim, 'xlim': xlim, **kwargs}
    animator = compg.MultiTimeAnimator(
        [
            {
                'animator': simpg.ObjectAnimator,
                'animator_options': {
                    'grid': grid,
                    'legend': legend,
                    'legend_loc': legend_loc,
                    'title': ax_title,
                },
                'transformable': transformed_obj,
                'draw_options': draw_options,
            } for transformed_obj, ax_title in zip(transformables, ax_titles)
        ],
        fig=fig,
        axs=axs,
        tlim=tlim,
        ct_per_sec=ct_per_sec,
        instant_pause_time=instant_pause_time,
        fps=fps,
        display_current_time=display_current_time,
        display_current_time_decimals=display_current_time_decimals,
        title=title)
    return animator

def compare_frames_animated_with_worldline(lorentz_transformable,
    vrels,
    origin=geom.geomrc['origin'],
    tlim_anim=geom.geomrc['tlim'],
    tlim_worldline=geom.geomrc['tlim'],
    tlim=(None, None),
    xlim=geom.geomrc['xlim'],
    fig=graphrc['fig'],
    axs=graphrc['axs'],
    grid=graphrc['grid'],
    legend=graphrc['legend'],
    legend_loc=graphrc['legend_loc'],
    ct_per_sec=graphrc['anim.time.ct_per_sec'],
    instant_pause_time=graphrc['anim.time.instant_pause_time'],
    fps=graphrc['anim.fps'],
    display_current_time=graphrc['anim.display_current'],
    display_current_time_decimals=
        graphrc['anim.display_current_decimals'],
    title=graphrc['title'],
    lim_padding=graphrc['worldline.lim_padding'],
    equal_lim_expand=graphrc['worldline.equal_lim_expand'],
    current_time_style=graphrc['anim.worldline.current_time_style'],
    current_time_color=graphrc['anim.worldline.current_time_color'],
    **kwargs):
    """Animates a `specrel.geom.LorentzTransformable` alongside an animated
    spacetime diagram in some number of different frames moving at some relative
    velocity to a lab frame.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            animate.
        vrels (list): List of relative velocities of frames to compare with the
            lab frame.
        origin (tuple, optional): Origin used for Lorentz transformations, in
            the form (t, x).
        tlim_anim (tuple, optional): Time drawing limits for the animation
            itself.
        tlim_worldline (tuple, optional): Time drawing limits for the spacetime
            diagram. See `specrel.geom.LorentzTransformable.draw`.
        tlim (tuple, optional): Time drawing limits for both the animation and
            the spacetime diagram. Entries that are not `None` override those
            in `tlim_anim` and `tlim_worldline`.
        xlim (tuple, optional): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        fig (matplotlib.figure.Figure, optional): Figure window. If `None`, a
            new figure window is created.
        axs (list, optional): List of axes in row major format. If `None`, a
            new set of axes is created under a new figure window.
        grid (bool, optional): Flag for whether or not to plot background grid
            lines.
        legend (bool, optional): Flag for whether or not to plot a legend.
        legend_loc (str, optional): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this parameter is ignored.
        ct_per_sec (float, optional): Amount of time to pass within an animation
            for every second of real time.
        instant_pause_time (float, optional): Amount of pause time in seconds
            for instantaneous events (appear in a single instant of time).
        fps (float, optional): Animation frames per second.
        display_current_time (bool, optional): Flag for displaying the time of
            the current animation frame.
        display_current_time_decimals (int, optional): Number of decimals to
            display the current time to. If `display_current_time` is `False`,
            this parameter is ignored.
        title (str, optional): Animation title.
        lim_padding (float, optional): Extra padding on spacetime diagram axis
            limits, relative to the axis sizes.
        equal_lim_expand (float, optional): If the limits on an axis are
            specified to be equal, they will be expanded symmetrically until the
            axis size is this value.
        current_time_style (linestyle, optional): Matplotlib linestyle for the
            line of current time in animated spacetime plot.
        current_time_color (color, optional): Matplotlib color for the line of
            current time in animated spacetime plot.
        **kwargs: Keyword arguments to forward to Matplotlib when drawing the
            object.

    Returns:
        specrel.graphics.compgraph.MultiTimeAnimator:
            Animator for the spacetime + real space animations of the object in
            each of the different reference frames.
    """
    transformables, vrels = _get_transformable_and_vrel_in_all_frames(
        lorentz_transformable, vrels, origin)

    # Make new figure if necessary
    fig, axs = _prepare_fig_and_axs(fig, axs, len(transformables), 2,
        rect=[0.03, 0.03, 1, 0.93], h_pad=3)

    _check_axs_match_frames(axs, 2*len(transformables))

    tlim_anim = _override_tlim(tlim_anim, tlim)
    tlim_worldline = _override_tlim(tlim_worldline, tlim)

    ax_worldline_titles = ['Spacetime Diagram (Lab Frame)'] \
        + [f'Spacetime Diagram ($v = {vrel:.3g}c$)' for vrel in vrels]
    ax_obj_titles = ['Scene in Lab Frame'] \
        + [f'Scene in Frame Moving at ${vrel:.3g}c$' for vrel in vrels]
    worldline_anim_opts = {
        'grid': grid,
        'legend': legend,
        'legend_loc': legend_loc,
        'lim_padding': lim_padding,
        'equal_lim_expand': equal_lim_expand,
        'current_time_style': current_time_style,
        'current_time_color': current_time_color,
    }
    object_anim_opts = {
        'grid': grid,
        'legend': legend,
        'legend_loc': legend_loc,
    }

    anim_objs = []
    for transformable, ax_worldline_title, ax_obj_title in zip(
        transformables, ax_worldline_titles, ax_obj_titles):
        anim_objs += [
            {
                'animator': simpg.WorldlineAnimator,
                'animator_options': {'title': ax_worldline_title,
                    **worldline_anim_opts},
                'transformable': transformable,
                'draw_options': {'tlim': tlim_worldline, 'xlim': xlim,
                    **kwargs},
            },
            {
                'animator': simpg.ObjectAnimator,
                'animator_options': {'title': ax_obj_title,
                    **object_anim_opts},
                'transformable': transformable,
                'draw_options': {'tlim': tlim_worldline, 'xlim': xlim,
                    **kwargs},
            },
        ]

    animator = compg.MultiTimeAnimator(
        anim_objs,
        fig=fig,
        axs=axs,
        tlim=tlim_anim,
        ct_per_sec=ct_per_sec,
        instant_pause_time=instant_pause_time,
        fps=fps,
        display_current_time=display_current_time,
        display_current_time_decimals=display_current_time_decimals,
        title=title)
    return animator

def animate_lt(lorentz_transformable,
    vrel,
    origin=geom.geomrc['origin'],
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=graphrc['fig'],
    ax=graphrc['ax'],
    grid=graphrc['grid'],
    legend=graphrc['legend'],
    legend_loc=graphrc['legend_loc'],
    transition_duration=graphrc['anim.transform.transition_duration'],
    fps=graphrc['anim.fps'],
    display_current_velocity=graphrc['anim.display_current'],
    display_current_velocity_decimals=
        graphrc['anim.display_current_decimals'],
    title=graphrc['title'],
    lim_padding=graphrc['worldline.lim_padding'],
    equal_lim_expand=graphrc['worldline.equal_lim_expand']):
    """Animates the Lorentz transformation of a
    `specrel.geom.LorentzTransformable` from one frame to another on a spacetime
    diagram.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            animate.
        vrel (float): Relative velocities of frame to transform to.
        origin (tuple, optional): Origin used for Lorentz transformation, in the
            form (t, x).
        tlim (tuple, optional): Time drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        xlim (tuple, optional): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        fig (matplotlib.figure.Figure, optional): Figure window. See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        ax (matplotlib.axes.Axes, optional): Plotting axes. See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        grid (bool, optional): Flag for whether or not to plot background grid
            lines.
        legend (bool, optional): Flag for whether or not to plot a legend.
        legend_loc (str, optional): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this parameter is ignored.
        transition_duration (float, optional): Real-time duration in seconds of
            the transformation animation.
        fps (float, optional): Animation frames per second.
        display_current_velocity (bool, optional): Flag for displaying the
            velocity of the current animation frame.
        display_current_velocity_decimals (int, optional): Number of decimals to
            display the current velocity to. If `display_current_velocity` is
            `False`, this parameter is ignored.
        title (str, optional): Animation title.
        lim_padding (float, optional): Extra padding on spacetime diagram axis
            limits, relative to the axis sizes.
        equal_lim_expand (float, optional): If the limits on an axis are
            specified to be equal, they will be expanded symmetrically until the
            axis size is this value.

    Returns:
        specrel.graphics.simpgraph.TransformAnimator:
            Animator for the transformation animation of the object from one
            reference frame to the other.
    """
    # Attempt to make sure the time value falls within the limits so we don't
    # get warnings
    time = graphrc['anim.transform.time']
    if tlim[0] is not None and time < tlim[0]:
        time = tlim[0]
    elif tlim[1] is not None and time > tlim[1]:
        time = tlim[1]

    animator = simpg.TransformAnimator(
        copy.deepcopy(lorentz_transformable),
        vrel,
        origin=origin,
        stanimator=simpg.WorldlineAnimator,
        stanimator_options={
            'current_time_color': 'None',   # Transparent
            'grid': grid,
            'legend': legend,
            'legend_loc': legend_loc,
            'lim_padding': lim_padding,
            'equal_lim_expand': equal_lim_expand,
        },
        tlim=tlim,
        xlim=xlim,
        time=time,
        fig=fig,
        ax=ax,
        transition_duration=transition_duration,
        fps=fps,
        display_current_velocity=display_current_velocity,
        display_current_velocity_decimals=display_current_velocity_decimals,
        title=title)
    return animator

def animate_lt_realspace(lorentz_transformable,
    vrel,
    origin=geom.geomrc['origin'],
    xlim=geom.geomrc['xlim'],
    time=graphrc['anim.transform.time'],
    fig=graphrc['fig'],
    ax=graphrc['ax'],
    grid=graphrc['grid'],
    legend=graphrc['legend'],
    legend_loc=graphrc['legend_loc'],
    transition_duration=graphrc['anim.transform.transition_duration'],
    fps=graphrc['anim.fps'],
    display_current_velocity=graphrc['anim.display_current'],
    display_current_velocity_decimals=
        graphrc['anim.display_current_decimals'],
    title=graphrc['title']):
    """Animates the Lorentz transformation of a
    `specrel.geom.LorentzTransformable` from one frame to another in real space,
    fixing the frame-local time value.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            animate.
        vrel (float): Relative velocities of frame to transform to.
        origin (tuple, optional): Origin used for Lorentz transformation, in the
            form (t, x).
        xlim (tuple, optional): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        time (float, optional): Frame-local time value to fix during
            transformation animation.
        fig (matplotlib.figure.Figure, optional): Figure window. See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        ax (matplotlib.axes.Axes, optional): Plotting axes. See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        grid (bool, optional): Flag for whether or not to plot background grid
            lines.
        legend (bool, optional): Flag for whether or not to plot a legend.
        legend_loc (str, optional): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this parameter is ignored.
        transition_duration (float, optional): Real-time duration in seconds of
            the transformation animation.
        fps (float, optional): Animation frames per second.
        display_current_velocity (bool, optional): Flag for displaying the
            velocity of the current animation frame.
        display_current_velocity_decimals (int, optional): Number of decimals to
            display the current velocity to. If `display_current_velocity` is
            `False`, this parameter is ignored.
        title (str, optional): Animation title.

    Returns:
        specrel.graphics.simpgraph.TransformAnimator:
            Animator for the transformation animation of the object in real
            space from one reference frame to the other.
    """
    animator = simpg.TransformAnimator(
        copy.deepcopy(lorentz_transformable),
        vrel,
        origin=origin,
        stanimator=simpg.ObjectAnimator,
        stanimator_options={
            'grid': grid,
            'legend': legend,
            'legend_loc': legend_loc,
        },
        # Draw just the desired and surrounding frames to save computation
        tlim=(time - 1/fps, time + 1/fps),
        xlim=xlim,
        time=time,
        fig=fig,
        ax=ax,
        transition_duration=transition_duration,
        fps=fps,
        display_current_velocity=display_current_velocity,
        display_current_velocity_decimals=display_current_velocity_decimals,
        title=title)
    return animator

def animate_lt_worldline_and_realspace(lorentz_transformable,
    vrel,
    origin=geom.geomrc['origin'],
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    time=graphrc['anim.transform.time'],
    fig=graphrc['fig'],
    axs=graphrc['axs'],
    grid=graphrc['grid'],
    legend=graphrc['legend'],
    legend_loc=graphrc['legend_loc'],
    transition_duration=graphrc['anim.transform.transition_duration'],
    fps=graphrc['anim.fps'],
    display_current_velocity=graphrc['anim.display_current'],
    display_current_velocity_decimals=
        graphrc['anim.display_current_decimals'],
    title=graphrc['title'],
    lim_padding=graphrc['worldline.lim_padding'],
    equal_lim_expand=graphrc['worldline.equal_lim_expand'],
    current_time_style=graphrc['anim.worldline.current_time_style'],
    current_time_color=graphrc['anim.worldline.current_time_color']):
    """Animates the Lorentz transformation of a
    `specrel.geom.LorentzTransformable` from one frame to another in both a
    spacetime diagram and real space, fixing the frame-local time value.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            animate.
        vrel (float): Relative velocities of frame to transform to.
        origin (tuple, optional): Origin used for Lorentz transformation, in the
            form (t, x).
        tlim (tuple, optional): Time drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        xlim (tuple, optional): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        time (float, optional): Frame-local time value to fix during
            transformation animation.
        fig (matplotlib.figure.Figure, optional): Figure window. If `None`, a
            new figure window is created.
        axs (list, optional): List of axes in row major format. If `None`, a
            new set of axes is created under a new figure window.
        grid (bool, optional): Flag for whether or not to plot background grid
            lines.
        legend (bool, optional): Flag for whether or not to plot a legend.
        legend_loc (str, optional): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this parameter is ignored.
        transition_duration (float, optional): Real-time duration in seconds of
            the transformation animation.
        fps (float, optional): Animation frames per second.
        display_current_velocity (bool, optional): Flag for displaying the
            velocity of the current animation frame.
        display_current_velocity_decimals (int, optional): Number of decimals to
            display the current velocity to. If `display_current_velocity` is
            `False`, this parameter is ignored.
        title (str, optional): Animation title.
        lim_padding (float, optional): Extra padding on spacetime diagram axis
            limits, relative to the axis sizes.
        equal_lim_expand (float, optional): If the limits on an axis are
            specified to be equal, they will be expanded symmetrically until the
            axis size is this value.
        current_time_style (linestyle, optional): Matplotlib linestyle for the
            line of current time in animated spacetime plot.
        current_time_color (color, optional): Matplotlib color for the line of
            current time in animated spacetime plot.

    Returns:
        specrel.graphics.compgraph.MultiTransformAnimator:
            Animator for the transformation animation of the object in a
            spacetime diagram and real space from one reference frame to the
            other.
    """
    # Make new figure if necessary
    fig, axs = _prepare_fig_and_axs(fig, axs, 1, 2,
        rect=[0.03, 0.03, 1, 0.89], w_pad=0)

    _check_axs_match_frames(axs, 2)

    animator = compg.MultiTransformAnimator(
        [
            {
                'animator_options':
                {
                    'stanimator': simpg.WorldlineAnimator,
                    'title': 'Spacetime Diagram',
                    'origin': origin,
                    'tlim': tlim,
                    'xlim': xlim,
                    'time': time,
                    'stanimator_options':
                    {
                        'grid': grid,
                        'legend': legend,
                        'legend_loc': legend_loc,
                        'lim_padding': lim_padding,
                        'equal_lim_expand': equal_lim_expand,
                        'current_time_style': current_time_style,
                        'current_time_color': current_time_color,
                    },
                },
                'transformable': copy.deepcopy(lorentz_transformable),
            },
            {
                'animator_options':
                {
                    'stanimator': simpg.ObjectAnimator,
                    'title': 'Actual Scene',
                    'origin': origin,
                    'xlim': xlim,
                    'time': time,
                    'stanimator_options': {
                        'grid': grid,
                        'legend': legend,
                        'legend_loc': legend_loc,
                    }
                },
                'transformable': copy.deepcopy(lorentz_transformable),
            },
        ],
        vrel,
        fig=fig,
        axs=axs,
        transition_duration=transition_duration,
        fps=fps,
        display_current_velocity=display_current_velocity,
        display_current_velocity_decimals=display_current_velocity_decimals,
        title=title)
    return animator
