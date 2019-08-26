"""Visualization tools for special relativity

For higher level, aggregate graphics generation, and for more convenient
plotting API.
Core graphics code is in graphics subpackage
"""
import copy

import matplotlib.pyplot as plt

import specrel.geom as geom
import specrel.graphics.simpgraph as simpg
import specrel.graphics.compgraph as compg

# Commonly used default values shared by multiple visualize functions
visrc = {
    'default_fig_max_height': 10,
    'default_fig_max_width': 10,
}

"""Prepare a default figure and subplot axis set in tight layout, if both the
given fig and axs are None"""
def _prepare_fig_and_axs(fig, axs, nrow, ncol, rect, w_pad=None, h_pad=None):
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

"""Plots the worldline of a LorentzTransformable"""
def stplot(lorentz_transformable,
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=simpg.graphrc['fig'],
    ax=simpg.graphrc['ax'],
    grid=simpg.graphrc['grid'],
    legend=simpg.graphrc['legend'],
    legend_loc=simpg.graphrc['legend_loc'],
    lim_padding=simpg.graphrc['worldline.lim_padding'],
    equal_lim_expand=simpg.graphrc['worldline.equal_lim_expand'],
    title=simpg.graphrc['title'],
    **kwargs):
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

"""Animates a LorentzTransformable"""
def stanimate(lorentz_transformable,
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=simpg.graphrc['fig'],
    ax=simpg.graphrc['ax'],
    grid=simpg.graphrc['grid'],
    legend=simpg.graphrc['legend'],
    legend_loc=simpg.graphrc['legend_loc'],
    ct_per_sec=simpg.graphrc['anim.time.ct_per_sec'],
    instant_pause_time=simpg.graphrc['anim.time.instant_pause_time'],
    fps=simpg.graphrc['anim.fps'],
    display_current_time=simpg.graphrc['anim.display_current'],
    display_current_time_decimals=
        simpg.graphrc['anim.display_current_decimals'],
    title=simpg.graphrc['title'],
    **kwargs):
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

"""Override None entries of tlim_base with those in tlim_override"""
def _override_tlim(tlim_base, tlim_override):
    return tuple([override if override is not None else base
        for base, override in zip(tlim_base, tlim_override)])

"""Animates a LorentzTransformable alongside an animated worldline diagram"""
def stanimate_with_worldline(lorentz_transformable,
    tlim_anim=geom.geomrc['tlim'],
    tlim_worldline=geom.geomrc['tlim'],
    tlim=(None, None),
    xlim=geom.geomrc['xlim'],
    fig=simpg.graphrc['fig'],
    axs=simpg.graphrc['axs'],
    grid=simpg.graphrc['grid'],
    legend=simpg.graphrc['legend'],
    legend_loc=simpg.graphrc['legend_loc'],
    ct_per_sec=simpg.graphrc['anim.time.ct_per_sec'],
    instant_pause_time=simpg.graphrc['anim.time.instant_pause_time'],
    fps=simpg.graphrc['anim.fps'],
    display_current_time=simpg.graphrc['anim.display_current'],
    display_current_time_decimals=
        simpg.graphrc['anim.display_current_decimals'],
    title=simpg.graphrc['title'],
    lim_padding=simpg.graphrc['worldline.lim_padding'],
    equal_lim_expand=simpg.graphrc['worldline.equal_lim_expand'],
    current_time_style=simpg.graphrc['anim.worldline.current_time_style'],
    current_time_color=simpg.graphrc['anim.worldline.current_time_color'],
    **kwargs):
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

"""Return lists of a LorentzTransformable and vrels in different frames,
where the input vrels can be a scalar or a list of values"""
def _get_transformable_and_vrel_in_all_frames(lorentz_transformable, vrels,
    origin):
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
"""Raise error if there's a mismatch between number of plots to make and number
of axes to plot onto"""
def _check_axs_match_frames(axs, nplots):
    # Make there are the right number of axes for the number of frames
    if len(axs) != nplots:
        raise ValueError('Number of axes much match number of frame plots,'
            + ' including for the lab frame.'
            + f' {len(axs)} axes given, {nplots} needed.')

"""Plots the worldlines of a LorentzTransformable in some number of different
frames moving at some relative velocity"""
def compare_frames(lorentz_transformable,
    vrels,
    origin=geom.geomrc['origin'],
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=simpg.graphrc['fig'],
    axs=simpg.graphrc['axs'],
    grid=simpg.graphrc['grid'],
    legend=simpg.graphrc['legend'],
    legend_loc=simpg.graphrc['legend_loc'],
    lim_padding=simpg.graphrc['worldline.lim_padding'],
    equal_lim_expand=simpg.graphrc['worldline.equal_lim_expand'],
    title=simpg.graphrc['title'],
    **kwargs):
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

"""Animates a LorentzTransformable in some number of different frames moving at
some relative velocity"""
def compare_frames_animated(lorentz_transformable,
    vrels,
    origin=geom.geomrc['origin'],
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=simpg.graphrc['fig'],
    axs=simpg.graphrc['axs'],
    grid=simpg.graphrc['grid'],
    legend=simpg.graphrc['legend'],
    legend_loc=simpg.graphrc['legend_loc'],
    ct_per_sec=simpg.graphrc['anim.time.ct_per_sec'],
    instant_pause_time=simpg.graphrc['anim.time.instant_pause_time'],
    fps=simpg.graphrc['anim.fps'],
    display_current_time=simpg.graphrc['anim.display_current'],
    display_current_time_decimals=
        simpg.graphrc['anim.display_current_decimals'],
    title=simpg.graphrc['title'],
    **kwargs):
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

"""Animates a LorentzTransformable alongside an animated worldline diagram in
some number of different frames moving at some relative velocity"""
def compare_frames_animated_with_worldline(lorentz_transformable,
    vrels,
    origin=geom.geomrc['origin'],
    tlim_anim=geom.geomrc['tlim'],
    tlim_worldline=geom.geomrc['tlim'],
    tlim=(None, None),
    xlim=geom.geomrc['xlim'],
    fig=simpg.graphrc['fig'],
    axs=simpg.graphrc['axs'],
    grid=simpg.graphrc['grid'],
    legend=simpg.graphrc['legend'],
    legend_loc=simpg.graphrc['legend_loc'],
    ct_per_sec=simpg.graphrc['anim.time.ct_per_sec'],
    instant_pause_time=simpg.graphrc['anim.time.instant_pause_time'],
    fps=simpg.graphrc['anim.fps'],
    display_current_time=simpg.graphrc['anim.display_current'],
    display_current_time_decimals=
        simpg.graphrc['anim.display_current_decimals'],
    title=simpg.graphrc['title'],
    lim_padding=simpg.graphrc['worldline.lim_padding'],
    equal_lim_expand=simpg.graphrc['worldline.equal_lim_expand'],
    current_time_style=simpg.graphrc['anim.worldline.current_time_style'],
    current_time_color=simpg.graphrc['anim.worldline.current_time_color'],
    **kwargs):
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

"""Animates the Lorentz transformation from one frame to another on a
worldline plot"""
def animate_lt(lorentz_transformable,
    vrel,
    origin=geom.geomrc['origin'],
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    fig=simpg.graphrc['fig'],
    ax=simpg.graphrc['ax'],
    grid=simpg.graphrc['grid'],
    legend=simpg.graphrc['legend'],
    legend_loc=simpg.graphrc['legend_loc'],
    transition_duration=simpg.graphrc['anim.transform.transition_duration'],
    fps=simpg.graphrc['anim.fps'],
    display_current_velocity=simpg.graphrc['anim.display_current'],
    display_current_velocity_decimals=
        simpg.graphrc['anim.display_current_decimals'],
    title=simpg.graphrc['title'],
    lim_padding=simpg.graphrc['worldline.lim_padding'],
    equal_lim_expand=simpg.graphrc['worldline.equal_lim_expand']):
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
        fig=fig,
        ax=ax,
        transition_duration=transition_duration,
        fps=fps,
        display_current_velocity=display_current_velocity,
        display_current_velocity_decimals=display_current_velocity_decimals,
        title=title)
    return animator

"""Animates the Lorentz transformation from one frame to another in real space,
fixing the frame-local time value"""
def animate_lt_realspace(lorentz_transformable,
    vrel,
    origin=geom.geomrc['origin'],
    xlim=geom.geomrc['xlim'],
    time=simpg.graphrc['anim.transform.time'],
    fig=simpg.graphrc['fig'],
    ax=simpg.graphrc['ax'],
    grid=simpg.graphrc['grid'],
    legend=simpg.graphrc['legend'],
    legend_loc=simpg.graphrc['legend_loc'],
    transition_duration=simpg.graphrc['anim.transform.transition_duration'],
    fps=simpg.graphrc['anim.fps'],
    display_current_velocity=simpg.graphrc['anim.display_current'],
    display_current_velocity_decimals=
        simpg.graphrc['anim.display_current_decimals'],
    title=simpg.graphrc['title']):
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

"""Animates the Lorentz transformation from one frame to another in both a
worldline diagram and real space, fixing the frame-local time value"""
def animate_lt_worldline_and_realspace(lorentz_transformable,
    vrel,
    origin=geom.geomrc['origin'],
    tlim=geom.geomrc['tlim'],
    xlim=geom.geomrc['xlim'],
    time=simpg.graphrc['anim.transform.time'],
    fig=simpg.graphrc['fig'],
    axs=simpg.graphrc['axs'],
    grid=simpg.graphrc['grid'],
    legend=simpg.graphrc['legend'],
    legend_loc=simpg.graphrc['legend_loc'],
    transition_duration=simpg.graphrc['anim.transform.transition_duration'],
    fps=simpg.graphrc['anim.fps'],
    display_current_velocity=simpg.graphrc['anim.display_current'],
    display_current_velocity_decimals=
        simpg.graphrc['anim.display_current_decimals'],
    title=simpg.graphrc['title'],
    lim_padding=simpg.graphrc['worldline.lim_padding'],
    equal_lim_expand=simpg.graphrc['worldline.equal_lim_expand'],
    current_time_style=simpg.graphrc['anim.worldline.current_time_style'],
    current_time_color=simpg.graphrc['anim.worldline.current_time_color']):

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
