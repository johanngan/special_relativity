"""Simple (one set of axes) spacetime animations in special relativity."""

from abc import ABC, abstractmethod
import copy
import warnings

import matplotlib.pyplot as plt

from specrel.graphics import graphrc
import specrel.graphics.basegraph as bgraph

class TimeAnimator(bgraph.BaseAnimator):
    """Animator where the frame variable is time, i.e. depicts a sequence
    evolving in time.

    Args:
        ct_per_sec (float, optional): Amount of time to pass within an animation
            for every second of real time.
        instant_pause_time (float, optional): Amount of pause time in seconds
            for instantaneous events (appear in a single instant of time).
        display_current_time (bool, optional): Same as `display_current` in
            `specrel.graphics.basegraph.BaseAnimator`.
        display_current_time_decimals (int, optional): Same as
            `display_current_decimals` in
            `specrel.graphics.basegraph.BaseAnimator`.
        others: See `specrel.graphics.basegraph.BaseAnimator`.
    """
    def __init__(self,
        fig=graphrc['fig'],
        ct_per_sec=graphrc['anim.time.ct_per_sec'],
        instant_pause_time=graphrc['anim.time.instant_pause_time'],
        fps=graphrc['anim.fps'],
        display_current_time=graphrc['anim.display_current'],
        display_current_time_decimals=
            graphrc['anim.display_current_decimals'],
        title=graphrc['title']):

        super().__init__(fig, ct_per_sec / fps, fps, display_current_time,
            display_current_time_decimals, title)
        # Number of frames corresponding to the desired pause time
        self._pause_frames = round(instant_pause_time * fps)

class STAnimator(TimeAnimator, bgraph.STPlotter, ABC):
    """TimeAnimator that fulfills the `specrel.graphics.basegraph.STPlotter`
    interface, and hence can be used by
    `specrel.geom.LorentzTransformable.draw`.

    Attributes:
        frame_pause_flags (dict): Maps frame indexes to a flag for whether or
            not the animation should pause on that frame.
        frame_plotters (dict): Maps frame indexes to lists of plotting functions
            that should be called to draw that frame.
        grid (bool): Flag for whether or not to plot background grid lines.
        legend (bool): Flag for whether or not to plot a legend.
        legend_loc (str): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this attribute is ignored.
        xlim (tuple): Position axis draw limits.
    """
    def __init__(self,
        fig=graphrc['fig'],
        ax=graphrc['ax'],
        grid=graphrc['grid'],
        legend=graphrc['legend'],
        legend_loc=graphrc['legend_loc'],
        ct_per_sec=graphrc['anim.time.ct_per_sec'],
        instant_pause_time=graphrc['anim.time.instant_pause_time'],
        fps=graphrc['anim.fps'],
        display_current_time=graphrc['anim.display_current'],
        display_current_time_decimals=graphrc['anim.display_current_decimals'],
        title=graphrc['title']):

        bgraph.STPlotter.__init__(self, fig, ax)
        TimeAnimator.__init__(self, self.fig, ct_per_sec, instant_pause_time,
            fps, display_current_time, display_current_time_decimals, title)
        self.grid = grid
        self.legend = legend
        self.legend_loc = legend_loc
        self.clear()

    def clear(self):
        super().clear()
        self.xlim = (0, 0)
        # At each key corresponding to a frame index, a list of function
        # handles to be called to plot the frame
        self.frame_plotters = {}
        # Flags for whether each frame should be paused
        self.frame_pause_flags = {}

    def _init_frame(self, idx):
        """Initialize the frame plotters at some frame index."""
        self.frame_plotters[idx] = []
        # Set the given title, current time, both, or neither
        titles = []
        if self.title:
            titles.append(self.title)
        if self.display_current:
            titles.append(
                f'Time = {{:.{self.display_current_decimals}f}} s'.format(
                    self.calc_frame_val(idx)))
        if titles:
            title_str = '\n'.join(titles)
            self.frame_plotters[idx] += [lambda: self.ax.set_title(title_str)]
        self.frame_pause_flags[idx] = False

    def resize(self, tlim):
        """Expand the animator's stored frame range to accomodate a given time
        range. Otherwise, the animator won't know how to plot an out-of-range
        time value.

        Args:
            tlim (tuple): Time range to accomodate, in the form (min, max).
        """
        # Convert tlim to frame indexes
        flims = [
            self.calc_frame_idx(tlim[0]),
            self.calc_frame_idx(tlim[1]),
        ]
        if not self.frame_plotters:
            # Initialize all frame within the limits
            new_fidx = list(range(flims[0], flims[1]+1))
        else:
            # Initialize frames that don't exist yet
            keys = self.frame_plotters.keys()
            new_fidx = list(range(flims[0], min(keys))) \
                + list(range(max(keys)+1, flims[1]+1))
        # Initialize the necessary frames
        for idx in new_fidx:
            self._init_frame(idx)

    def set_lims(self, tlim, xlim):
        self.xlim = xlim
        self._frame_lim = (
            self.calc_frame_idx(tlim[0]),
            self.calc_frame_idx(tlim[1]),
        )
        self.resize(tlim)

    @abstractmethod
    def draw_point(self, point, tag, **kwargs):
        # Flush cache upon drawing a new thing
        self._cached_anim = None

        # Add any necessary new frames
        self.resize(2*[point[0]])

        # Pause if specified
        if self._pause_frames:
            frame = self.calc_frame_idx(point[0])
            self.frame_pause_flags[frame] = True

    @abstractmethod
    def draw_line_segment(self, point1, point2, tag, **kwargs):
        # Flush cache upon drawing a new thing
        self._cached_anim = None

        # Add any necessary new frames
        self.resize([
            min(point1[0], point2[0]),
            max(point1[0], point2[0])
        ])

        # If the line is horizontal, treat it like an instantaneous point,
        # and pause if specified
        if point1[0] == point2[0]:
            if self._pause_frames:
                frame = self.calc_frame_idx(point1[0])
                self.frame_pause_flags[frame] = True

    @abstractmethod
    def draw_shaded_polygon(self, vertices, tag, **kwargs):
        # Flush cache upon drawing a new thing
        self._cached_anim = None

        # Add any necessary new frames
        tvals = self._decouple_stvectors(vertices)[0]
        if tvals:
            self.resize([min(tvals), max(tvals)])

    def init_func(self):
        return [self.ax]

    def update(self, frame):
        for plotter in self.frame_plotters[frame]:
            plotter()
        return [self.ax]

    def _get_frame_list(self):
        # Prolong any frames that have been flagged for a pause
        return [f for f in super()._get_frame_list() for repeat in range(
            self._pause_frames if self.frame_pause_flags[f] else 1)]

class WorldlineAnimator(STAnimator):
    """Animates a spacetime plot with a sweeping horizontal line overlaid to
    indicate the current time.

    Args:
        current_time_style (linestyle, optional): See attributes.
        current_time_color (color, optional): See attributes.
        lim_padding (float, optional): See
            `specrel.graphics.basegraph.WorldlinePlotter`.
        equal_lim_expand (float, optional): See
            `specrel.graphics.basegraph.WorldlinePlotter`.
        others: See `specrel.graphics.simpanim.STAnimator`.

    Attributes:
        current_time_color (TYPE): Matplotlib color for the line of current
            time.
        current_time_style (TYPE): Matplotlib linestyle for the line of current
            time.
    """
    def __init__(self,
        fig=graphrc['fig'],
        ax=graphrc['ax'],
        grid=graphrc['grid'],
        legend=graphrc['legend'],
        legend_loc=graphrc['legend_loc'],
        ct_per_sec=graphrc['anim.time.ct_per_sec'],
        instant_pause_time=graphrc['anim.time.instant_pause_time'],
        fps=graphrc['anim.fps'],
        display_current_time=graphrc['anim.display_current'],
        display_current_time_decimals=graphrc['anim.display_current_decimals'],
        title=graphrc['title'],
        lim_padding=graphrc['worldline.lim_padding'],
        equal_lim_expand=graphrc['worldline.equal_lim_expand'],
        current_time_style=graphrc['anim.worldline.current_time_style'],
        current_time_color=graphrc['anim.worldline.current_time_color']):

        super().__init__(fig,
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
        # Form a WorldlinePlotter to meet the animator's needs
        self._worldline_plotter = bgraph.WorldlinePlotter(self.fig, self.ax,
            self.grid, self.legend, self.legend_loc, lim_padding,
            equal_lim_expand)
        self.current_time_style = current_time_style
        self.current_time_color = current_time_color

    def clear(self):
        super().clear()
        # Plotters to call on all frames
        self._plotters_all_frames = []
        # Line object for current time
        self._current_time = None

    def _draw_current_time(self, t):
        """Draw the actual line marking the current time."""
        # Update the line's position
        self._current_time.set_data(self.xlim, (t, t))

    def _init_frame(self, idx):
        super()._init_frame(idx)

        # Draw the current line of constant time
        self.frame_plotters[idx] += [
            lambda: self._draw_current_time(self.calc_frame_val(idx))
        ]

    def draw_point(self, point, tag=None, **kwargs):
        super().draw_point(point, tag, **kwargs)

        # Draw the point in every frame
        self._plotters_all_frames += [
            lambda: self._worldline_plotter.draw_point(point, tag, **kwargs)
        ]

    def draw_line_segment(self, point1, point2, tag=None, **kwargs):
        super().draw_line_segment(point1, point2, tag, **kwargs)

        # Draw the line in every frame
        self._plotters_all_frames += [
            lambda: self._worldline_plotter.draw_line_segment(
                point1, point2, tag, **kwargs)
        ]

    def draw_shaded_polygon(self, vertices, tag=None, **kwargs):
        super().draw_shaded_polygon(vertices, tag, **kwargs)

        # Draw the polygon in every frame
        self._plotters_all_frames += [
            lambda: self._worldline_plotter.draw_shaded_polygon(
                vertices, tag, **kwargs)
        ]

    def init_func(self):
        self.ax.clear()
        tlim = [self.calc_frame_val(f) for f in self.get_frame_lim()]
        # Do the all-frames plotting first
        for plotter in self._plotters_all_frames:
            plotter()
        # Make sure the limits are set properly after calling the all-frames
        # plotters
        self._worldline_plotter.set_lims(tlim, self.xlim)
        # Create the current time line
        self._current_time, = self.ax.plot([], [],
            linestyle=self.current_time_style,
            color=self.current_time_color)
        # Set axis labels for the plot
        self._worldline_plotter.set_labels()
        return [self.ax]

class ObjectAnimator(STAnimator):
    """Animates objects in real space over time.

    Args:
        tag_height (float, optional): See attributes.
        others: See `specrel.graphics.simpanim.STAnimator`.

    Attributes:
        tag_height (float): The height (relative to the axis height) above the
            actual objects of any tag text that's drawn.
    """

    def __init__(self,
        fig=graphrc['fig'],
        ax=graphrc['ax'],
        grid=graphrc['grid'],
        legend=graphrc['legend'],
        legend_loc='upper right',
        ct_per_sec=graphrc['anim.time.ct_per_sec'],
        instant_pause_time=graphrc['anim.time.instant_pause_time'],
        fps=graphrc['anim.fps'],
        display_current_time=graphrc['anim.display_current'],
        display_current_time_decimals=graphrc['anim.display_current_decimals'],
        title=graphrc['title'],
        tag_height=0.025):

        super().__init__(fig=fig,
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
        self.tag_height = tag_height

    def _disable_y_axis(self):
        """Hide the y-axis ticks because they mean nothing."""
        # Hard-coded fixed y-axis size with length 1
        self.ax.set_ylim((-0.5, 0.5))
        self.ax.set_yticks([])

    def init_func(self):
        self._disable_y_axis()
        self._set_labels()
        self.ax.set_xlim(self.xlim)
        return super().init_func()

    def _init_frame(self, idx):
        super()._init_frame(idx)

        # Wipe the axis before doing anything else
        self.frame_plotters[idx].insert(0, self.ax.clear)
        # Perform other frame setup
        self.frame_plotters[idx] += [
            lambda: self.ax.set_xlim(self.xlim),
            # Disable the y axis because it's meaningless
            self._disable_y_axis,
            self._set_labels,
        ]
        if self.grid:
            # Set the x grid
            self.frame_plotters[idx] += [self._set_grid]

    def _set_grid(self):
        """Set the x-grid."""
        self.ax.grid(True, axis='x')   # Only the x grid
        # Ensure grid lines are behind other objects
        self.ax.set_axisbelow(True)

    def _set_labels(self):
        """Set the x-label."""
        self.ax.set_xlabel(graphrc['xlabel'])

    def _generate_point_drawer(self, xval, tag, **kwargs):
        """Factory function for point drawing functions. Needed to save
        persistent copies of xval calculated in loops."""
        marker = kwargs.pop('marker', '.')
        # Force linestyle to be none for a point
        kwargs['linestyle'] = 'None'
        def point_drawer():
            self.ax.plot(xval, 0, marker=marker, **kwargs)
            if tag:
                self.ax.text(xval, self.tag_height, tag)
        return point_drawer

    def _generate_line_drawer(self, xval1, xval2, tag, **kwargs):
        """Factory function for line drawing functions. Needed to save
        persistent copies of xval calculated in loops."""
        def line_drawer():
            self.ax.plot([xval1, xval2], [0, 0], **kwargs)
            if tag:
                self.ax.text((xval1 + xval2)/2, self.tag_height, tag,
                    ha='center')
        return line_drawer

    def _draw_legend(self):
        """Draw a plot legend."""
        self.ax.legend(loc=self.legend_loc)

    def draw_point(self, point, tag=None, **kwargs):
        super().draw_point(point, tag, **kwargs)

        # Draw the point in the frame it corresponds to
        self.frame_plotters[self.calc_frame_idx(point[0])] += [
            self._generate_point_drawer(point[1], tag, **kwargs)
        ]
        # Ensure the legend is updated on that frame
        if self.legend:
            self.frame_plotters[self.calc_frame_idx(point[0])] += [
                self._draw_legend
            ]

    def _interpolate(self, point1, point2, t):
        """Linearly interpolate the position value at a specific time value
        between two points. Assumes the two points have different time values.
        """
        return point1[1] + \
            (t - point1[0]) / (point2[0] - point1[0]) * (point2[1] - point1[1])

    def _strict_interpolate(self, point1, point2, t, precision):
        """If the time value isn't between the two points, return None."""
        # Do bounds checking at a given precision level
        if (t < round(min(point1[0], point2[0]), precision) or
            t > round(max(point1[0], point2[0]), precision)):
            return None
        return self._interpolate(point1, point2, t)

    def _loose_interpolate(self, point1, point2, t):
        """Only looking at the internal frame resolution, if the time value
        isn't between the two points, return None."""
        # Do bounds checking at the internal frame resolution
        snapped_t, snapped_t1, snapped_t2 = [
            self.calc_frame_val(val) for val in [t, point1[0], point2[0]]]
        if (snapped_t < min(snapped_t1, snapped_t2) or
            snapped_t > max(snapped_t1, snapped_t2)):
            return None
        return self._interpolate(point1, point2, t)

    def draw_line_segment(self, point1, point2, tag=None, **kwargs):
        super().draw_line_segment(point1, point2, tag, **kwargs)

        # For a line of constant time, draw the whole line in one frame
        if point1[0] == point2[0]:
            idx = self.calc_frame_idx(point1[0])
            self.frame_plotters[idx] += [
                self._generate_line_drawer(point1[1], point2[1], tag, **kwargs)
            ]
            # Ensure the legend is updated on that frame
            if self.legend:
                self.frame_plotters[idx] += [self._draw_legend]
            return

        # Otherwise, spread out the points across different frames
        start_idx = self.calc_frame_idx(min(point1[0], point2[0]))
        end_idx = self.calc_frame_idx(max(point1[0], point2[0]))
        for idx in range(start_idx, end_idx+1):
            snapped_tval = self.calc_frame_val(idx)
            # The bounds checking won't screw up the general line shape, so
            # use loose interpolation
            xval = self._loose_interpolate(point1, point2, snapped_tval)
            if xval is not None:
                self.frame_plotters[idx] += [
                    self._generate_point_drawer(xval, tag, **kwargs)
                ]
                # Ensure the legend is updated on each modified frame
                if self.legend:
                    self.frame_plotters[idx] += [self._draw_legend]

    def draw_shaded_polygon(self, vertices, tag=None, **kwargs):
        # If no vertices, just return
        if not vertices:
            return
        super().draw_shaded_polygon(vertices, tag, **kwargs)

        # Use 'color' over 'facecolor', but if no 'color',
        # then apply 'facecolor'
        if 'facecolor' in kwargs and 'color' not in kwargs:
            kwargs['color'] = kwargs.pop('facecolor')

        # Spread out the points/lines across different frames
        tvals = self._decouple_stvectors(vertices)[0]
        start_idx = self.calc_frame_idx(min(tvals))
        end_idx = self.calc_frame_idx(max(tvals))
        for idx in range(start_idx, end_idx+1):
            snapped_tval = self.calc_frame_val(idx)

            # Gather a list of all the intersections between the line of
            # constant time and the polygon edges
            intersections = []
            # Wrap around to the beginning for the last iteration
            for start_vertex, end_vertex in zip(
                vertices, vertices[1:] + vertices[:1]):
                # Skip when the edge is at a fixed time; the endpoints will
                # individually be identified in the prior and next iterations
                try:
                    precision = min(start_vertex.precision,
                        end_vertex.precision)
                except AttributeError:
                    # Default precision level
                    precision = 7
                if round(start_vertex[0], precision) == \
                    round(end_vertex[0], precision):
                    continue
                # Whether or not points are between the vertices will strongly
                # affect how the polygon is drawn, so use strict interpolation
                intersection = self._strict_interpolate(
                    start_vertex, end_vertex, snapped_tval, precision)
                if intersection is not None:
                    intersections.append(round(intersection, precision))

            # Sort in ascending order of position
            intersections.sort()

            # Draw line segments between every even-odd pair (0-1, 2-3, etc.),
            # If there's a corner point (two equal, adjacent intersections)
            # possibly flip polarity (even-odd to odd-even)
            i = 0
            first_patch = True
            line_tag = tag
            line_kwargs = dict(kwargs)
            while i < len(intersections) - 1:
                x1 = intersections[i]
                x2 = intersections[i+1]
                # If x1 and x2 are equal, we've hit a corner point.
                # Use ray-casting to figure out whether to reverse polarity
                # I.e. count the distinct points after x2. If there's an odd
                # number, reverse polarity.
                if x1 == x2 and len(set(intersections[i+2:])) % 2 == 1:
                    # Reverse polarity by incrementing by just +1 instead of
                    # by +2
                    i += 1
                else:
                    # Connect x1 and x2 by a line segment and move onto the
                    # next pair
                    self.frame_plotters[idx] += [
                        self._generate_line_drawer(x1, x2, line_tag, **line_kwargs)
                    ]
                    if first_patch:
                        first_patch = False
                        # Only give a legend entry to the first patch
                        if self.legend:
                            self.frame_plotters[idx] += [self._draw_legend]
                            line_kwargs.pop('label', None)
                        # Only give a tag to the first patch
                        if line_tag:
                            line_tag = None
                    i += 2

class TransformAnimator(bgraph.BaseAnimator, bgraph.SingleAxisFigureCreator):
    """Animator where the frame variable is velocity, i.e. animates a spacetime
    transformation as the object is accelerated instantaneously.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            animate.
        velocity (float): Relative velocity of the frame to transform to.
        origin (tuple, optional): See attributes.
        stanimator (type, optional): initializer of the
            `specrel.graphics.simpanim.STAnimator` to take drawing
            functionality from.
        stanimator_options (dict, optional): Dictionary of certain keyword
            arguments for `stanimator`, *except* for the following:

            - `fig`
            - `ax`
            - `instant_pause_time`
            - `fps`
            - `display_current_time`
            - `title`

        tlim (tuple, optional): See attributes.
        xlim (tuple, optional): See attributes.
        time (float, optional): Frame-local time value to fix during
            transformation animation.
        fig (matplotlib.figure.Figure, optional): See
            `specrel.graphics.basegraph.SingleAxisFigureCreator`.
        ax (matplotlib.axes.Axes, optional): See
            `specrel.graphics.basegraph.SingleAxisFigureCreator`.
        transition_duration (float, optional):
        fps (float, optional): Animation frames per second.
        display_current_velocity (bool, optional): Same as `display_current` in
            `specrel.graphics.basegraph.BaseAnimator`.
        display_current_velocity_decimals (int, optional): Same as
            `display_current_decimals` in
            `specrel.graphics.basegraph.BaseAnimator`.
        title (str, optional): Animation title.

    Attributes:
        origin (tuple): Origin used for Lorentz transformation, in the form
            (t, x).
        tlim (tuple): Time drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
        transformable (specrel.geom.LorentzTransformable): Object to animate.
        xlim (tuple): Position drawing limits. See
            `specrel.geom.LorentzTransformable.draw`.
    """
    def __init__(self,
        lorentz_transformable,
        velocity,
        origin=(0, 0),
        stanimator=WorldlineAnimator,
        stanimator_options={},
        tlim=(None, None),
        xlim=(None, None),
        time=graphrc['anim.transform.time'],
        fig=graphrc['fig'],
        ax=graphrc['ax'],
        transition_duration=graphrc['anim.transform.transition_duration'],
        fps=graphrc['anim.fps'],
        display_current_velocity=graphrc['anim.display_current'],
        display_current_velocity_decimals=
            graphrc['anim.display_current_decimals'],
        title=graphrc['title']):

        bgraph.SingleAxisFigureCreator.__init__(self, fig, ax)
        nsteps = round(transition_duration * fps)
        bgraph.BaseAnimator.__init__(self, self.fig, velocity / nsteps, fps,
            display_current_velocity, display_current_velocity_decimals, title,
            (0, nsteps))
        self.transformable = lorentz_transformable
        self.origin = origin
        self.xlim = xlim
        self.tlim = tlim

        # Set up the STAnimator
        anim_opts = dict(stanimator_options)
        for omit in ['fig', 'ax', 'instant_pause_time', 'fps',
            'display_current_time', 'title']:
            anim_opts.pop(omit, None)
        self._stanimator = stanimator(
            fig=self.fig,
            ax=self.ax,
            instant_pause_time=0,
            fps=self.fps,
            display_current_time=False,
            title=None,
            **stanimator_options)
        self._stanimator_frame = self._stanimator.calc_frame_idx(time)

    def clear(self):
        self._stanimator.clear()

    def init_func(self):
        return [self.ax]

    def update(self, frame):
        self._stanimator.clear()
        # Transform the object with the current velocity and plot it with some
        # STAnimator
        v = self.calc_frame_val(frame)
        obj = copy.deepcopy(self.transformable)
        obj.lorentz_transform(v, origin=self.origin)
        obj.draw(plotter=self._stanimator, tlim=self.tlim, xlim=self.xlim)
        self._stanimator.init_func()
        try:
            artists = self._stanimator.update(self._stanimator_frame)
        except KeyError:
            # Don't know what to draw; the fixed time is out of the range of
            # the plotter's tlim (either auto-generated or set manually)
            warnings.warn(
                'Failed to draw. Fixed time value is outside of limits.')
            artists = self.ax
        # Display the given title, current velocity, both, or neither
        titles = []
        if self.title:
            titles.append(self.title)
        if self.display_current:
            titles.append(
                f'$v = {{:.{self.display_current_decimals}f}}c$'.format(v))
        if titles:
            self.ax.set_title('\n'.join(titles))
        return artists
