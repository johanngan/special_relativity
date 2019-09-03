"""Simple (one set of axes) spacetime plots and animations in special
relativity.
"""

from abc import ABC, abstractmethod
import copy
import math
import warnings

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from specrel.graphics import graphrc

class FigureCreator:
    """Something that can create and own a figure.

    Attributes:
        fig (matplotlib.figure.Figure): Figure handle.
    """
    def __init__(self):
        self.fig = None
        self._created_own_fig = False

    def close(self):
        """Close the figure window if it was created by the class."""
        if self._created_own_fig:
            plt.close(self.fig)

class SingleAxisFigureCreator(FigureCreator):
    """Something that creates and owns a figure with a single axis
    (i.e. not a subplot).

    Args:
        fig (matplotlib.figure.Figure, optional): Figure window. If `None` and
            `ax` is not `None`, will be set to `ax.figure`. If both are `None`,
            a new figure will be created.
        ax (matplotlib.axes.Axes, optional): Axes to draw on. If `None` and
            `fig` is not `None`, will be set to `fig.gca()`. If both are `None`,
            a new set of axes will be created.

    Attributes:
        ax (matplotlib.axes.Axes): Axes to draw on.
        fig (matplotlib.figure.Figure): Figure window.
    """
    def __init__(self, fig=graphrc['fig'], ax=graphrc['ax']):
        super().__init__()
        if fig is None and ax is None:
            self.fig, self.ax = plt.subplots()
            self._created_own_fig = True
        elif fig is not None and ax is None:
            self.fig = fig
            self.ax = fig.gca()
        elif fig is None and ax is not None:
            self.fig = ax.figure
            self.ax = ax
        else:
            self.fig = fig
            self.ax = ax

class STPlotter(SingleAxisFigureCreator, ABC):
    """Base-level plotting interface."""

    @abstractmethod
    def draw_point(self, point, tag, **kwargs):
        """Draws a single spacetime point.

        Args:
            point (specrel.geom.STVector): Point to draw.
            tag (str): Tag to draw with the point.
            **kwargs: Matplotlib plot keyword arguments.

        Raises:
            NotImplementedError:
                Abstract method.
        """
        raise NotImplementedError

    @abstractmethod
    def draw_line_segment(self, point1, point2, tag, **kwargs):
        """Draws a line segment between two spacetime points.

        Args:
            point1 (specrel.geom.STVector): One line segment endpoint.
            point2 (specrel.geom.STVector): Other line segment endpoint.
            tag (str): Tag to draw with the point.
            **kwargs: Matplotlib plot keyword arguments.

        Raises:
            NotImplementedError:
                Abstract method.
        """
        raise NotImplementedError

    @abstractmethod
    def draw_shaded_polygon(self, vertices, tag, **kwargs):
        """Draws a shaded polygon in spacetime.

        Args:
            vertices (list): List of `specrel.geom.STVector` objects defining
                the polygon vertices.
            tag (str): Tag to draw with the point.
            **kwargs: Matplotlib plot keyword arguments.

        Raises:
            NotImplementedError:
                Abstract method.
        """
        raise NotImplementedError

    @staticmethod
    def _decouple_stvectors(stvectors):
        """Separate time and space values in a list of STVectors."""
        if stvectors:
            return tuple(zip(*stvectors))
        return tuple(), tuple()

    @abstractmethod
    def set_lims(self, tlim, xlim):
        """Sets the plotting limits for the plotter.

        Args:
            tlim (tuple): Minimum and maximum time values of the plot. `None`
                values are filled automatically.
            xlim (tuple): Minimum and maximum position values of the plot.
                `None` values are filled automatically.

        Raises:
            NotImplementedError:
                Abstract method.
        """
        raise NotImplementedError

    @abstractmethod
    def show(self):
        """Shows the plot in interactive mode.

        Raises:
            NotImplementedError:
                Abstract method.
        """
        raise NotImplementedError

    def save(self, filename, **kwargs):
        """Saves the plot to a file.

        Args:
            filename (str): Output file name.
            **kwargs: Keyword arguments to `matplotlib.figure.Figure.savefig`.
        """
        self.fig.savefig(filename, **kwargs)

class WorldlinePlotter(STPlotter):
    """Plotter for creating static spacetime diagrams.

    Args:
        fig (matplotlib.figure.Figure, optional): See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        ax (matplotlib.axes.Axes, optional): See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        others: See attributes.

    Attributes:
        equal_lim_expand (float): If the limits on an axis are specified to be
            equal, they will be expanded symmetrically until the axis size is
            this value.
        grid (bool): Flag for whether or not to plot background grid lines.
        legend (bool): Flag for whether or not to plot a legend.
        legend_loc (str): Legend location according to the Matplotlib
            `loc` parameter. If `legend` is `False`, this attribute is ignored.
        lim_padding (float): Extra padding on spacetime diagram axis limits,
            relative to the axis sizes.
    """

    def __init__(self,
        fig=graphrc['fig'],
        ax=graphrc['ax'],
        grid=graphrc['grid'],
        legend=graphrc['legend'],
        legend_loc=graphrc['legend_loc'],
        lim_padding=graphrc['worldline.lim_padding'],
        equal_lim_expand=graphrc['worldline.equal_lim_expand']):

        super().__init__(fig, ax)
        self.grid = grid
        self.legend = legend
        self.legend_loc = legend_loc
        self.lim_padding = lim_padding
        self.equal_lim_expand = equal_lim_expand

    def _prepare_ax(self):
        """Do any axis preparation before drawing stuff."""
        self.ax.grid(self.grid)
        # Ensure grid lines are behind other objects
        self.ax.set_axisbelow(True)

    def _set_legend(self):
        """Turn on the legend, or do nothing, depending on self.legend"""
        if self.legend:
            self.ax.legend(loc=self.legend_loc)

    def draw_point(self, point, tag=None, **kwargs):
        """See `specrel.graphics.simpgraph.STPlotter.draw_point`.

        Kwargs:
            linestyle: Forced to be `'None'`
            marker: Default is `'.'`.
        """
        self._prepare_ax()
        marker = kwargs.pop('marker', '.')
        # Force linestyle to be none for a point
        kwargs['linestyle'] = 'None'
        self.ax.plot(point[1], point[0], marker=marker, **kwargs)
        if tag:
            self.ax.text(point[1], point[0], tag)
        self._set_legend()

    def draw_line_segment(self, point1, point2, tag=None, **kwargs):
        """See `specrel.graphics.simpgraph.STPlotter.draw_line_segment`.

        Kwargs:
            marker: Forced to be `None`.
        """
        self._prepare_ax()
        # Ignore the "marker" parameter
        kwargs.pop('marker', None)
        self.ax.plot((point1[1], point2[1]), (point1[0], point2[0]), **kwargs)
        # Put the tag at the midpoint
        if tag:
            self.ax.text((point1[1] + point2[1])/2, (point1[0] + point2[0])/2,
                tag, ha='center', va='center', bbox={'boxstyle': 'round',
                    'ec': 'black', 'fc': (1, 1, 1, 0.5)})
        self._set_legend()

    def draw_shaded_polygon(self, vertices, tag=None, **kwargs):
        """See `specrel.graphics.simpgraph.STPlotter.draw_shaded_polygon`.

        Kwargs:
            linewidth: Forced to be `None`.
        """
        self._prepare_ax()
        tvals, xvals = self._decouple_stvectors(vertices)
        # Ignore the "linewidth" parameter
        kwargs.pop('linewidth', None)
        self.ax.fill(xvals, tvals, **kwargs)
        # Put tag at the centroid
        if vertices and tag:
            self.ax.text(sum(xvals)/len(xvals), sum(tvals)/len(tvals), tag,
                ha='center', va='center', bbox={'boxstyle': 'round',
                    'ec': 'black', 'fc': (1, 1, 1, 0.5)})
        self._set_legend()

    def set_lims(self, tlim, xlim):
        # Pad the limits
        tpad = self.lim_padding/2 * (tlim[1] - tlim[0])
        xpad = self.lim_padding/2 * (xlim[1] - xlim[0])
        # If the limits are identical, expand them
        if tlim[0] == tlim[1]:
            tpad = self.equal_lim_expand/2
        if xlim[0] == xlim[1]:
            xpad = self.equal_lim_expand/2

        padded_tlim = (tlim[0] - tpad, tlim[1] + tpad)
        padded_xlim = (xlim[0] - xpad, xlim[1] + xpad)

        # Set the actual limits
        self.ax.set_xlim(padded_xlim)
        self.ax.set_ylim(padded_tlim)

        # Clip lines and polygons objects to the actual limits
        clipbox = self.ax.fill([xlim[0], xlim[0], xlim[1], xlim[1]],
            [tlim[0], tlim[1], tlim[1], tlim[0]], color='None')[0]
        # Only clip lines, not points
        for artist in [ln for ln in self.ax.lines if len(ln.get_xdata()) > 1] \
            + self.ax.patches[:-1]:
            artist.set_clip_path(clipbox)
        self.ax.patches.pop()

    def show(self):
        plt.show()

    def set_labels(self):
        """Set labels for the time and space axes. See
        `specrel.graphics.graphrc`.
        """
        self.ax.set_xlabel(graphrc['xlabel'])
        self.ax.set_ylabel(graphrc['tlabel'])

class BaseAnimator(ABC):
    """Base class for animators that animate over some changing control
    variable, like time or velocity.

    Args:
        frame_lim (tuple, optional): Minimum and maximum frame index of the
            animation. See `BaseAnimator.calc_frame_idx`.
        others: See attributes.

    Attributes:
        display_current (bool): Flag for displaying the control variable value
            of the current animation frame.
        display_current_decimals (int): Number of decimals to display the
            current control variable to.
        fig (matplotlib.figure.Figure): Matplotlib figure window.
        fps (float): Animation frames per second.
        stepsize (float): Change in control variable value over one frame.
        title (str): Animation title; static throughout all frames.
    """
    def __init__(self,
        fig=graphrc['fig'],
        stepsize=None,
        fps=graphrc['anim.fps'],
        display_current=graphrc['anim.display_current'],
        display_current_decimals=graphrc['anim.display_current_decimals'],
        title=graphrc['title'],
        frame_lim=(0, 0)):

        self.fig = fig
        self.display_current = display_current
        self.display_current_decimals = display_current_decimals
        self.stepsize = stepsize
        self.fps = fps
        self.title = title
        self._frame_lim = frame_lim
        # Cached animation if already created previously
        self._cached_anim = None

    def clear(self):
        """Clear persistent data from the last animation."""
        self._frame_lim = (0, 0)
        self._cached_anim = None

    def calc_frame_idx(self, val):
        """Snap a value to the closest corresponding frame. Frames are indexed
        as multiples of the stepsize. Note that frame indexes can be either
        positive or negative.

        Args:
            val (float): Value of the frame.

        Returns:
            int:
                Closest frame index corresponding to `val`.
        """
        return round(val / self.stepsize)

    def calc_frame_val(self, idx):
        """Get the corresponding value of a frame at a specified index, rounded
        to the same precision as the stepsize, but with one extra decimal place.

        Args:
            idx (int): Frame index.

        Returns:
            float:
                Value of the frame.
        """
        # Round to the same order of magnitude (one smaller for safety) as the
        # stepsize to ensure precision, but to mitigate floating-point error
        def order_of_mag(x):
            return int(math.floor(math.log10(abs(x))))
        return round(idx * self.stepsize, 1-order_of_mag(self.stepsize))

    @abstractmethod
    def init_func(self):
        """Initialization function for `matplotlib.animation.FuncAnimation`.

        Returns:
            matplotlib.artist.Artist

        Raises:
            NotImplementedError:
                Abstract method.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, frame):
        """Update the animation frame.

        Args:
            frame (int): Index of the frame to draw.

        Returns:
            matplotlib.artist.Artist

        Raises:
            NotImplementedError:
                Abstract method.
        """
        raise NotImplementedError

    def get_frame_lim(self):
        """
        Returns:
            tuple:
                The animation frame index limits.
        """
        return self._frame_lim

    def _get_frame_list(self):
        """Get a full list of all frame values to be played in the animation."""
        frame_lim = self.get_frame_lim()
        return list(range(frame_lim[0], frame_lim[1]+1))

    def animate(self):
        """Synthesize an animation. If an animation was already synthesized and
        cached, return the cached animation.

        Returns:
            matplotlib.animation.FuncAnimation
        """
        # Only create a new animation if the cache is empty
        if self._cached_anim is None:
            self._cached_anim = FuncAnimation(self.fig, self.update,
                init_func=self.init_func,
                frames=self._get_frame_list(),
                interval=1e3/self.fps,
                repeat=False)
        return self._cached_anim

    def show(self):
        """Play the animation in interactive mode."""
        plt.show(self.animate())

    def save(self, filename, **kwargs):
        """Save the animation to a file.

        Kwargs:
            fps: Fixed to the animator's `fps` attribute.
        """
        kwargs.pop('fps', None) # FPS is fixed
        self.animate().save(filename, fps=self.fps, **kwargs)

class TimeAnimator(BaseAnimator):
    """Animator where the frame variable is time, i.e. depicts a sequence
    evolving in time.

    Args:
        ct_per_sec (float, optional): Amount of time to pass within an animation
            for every second of real time.
        instant_pause_time (float, optional): Amount of pause time in seconds
            for instantaneous events (appear in a single instant of time).
        display_current_time (bool, optional): Same as `display_current` in
            `specrel.graphics.simpgraph.BaseAnimator`.
        display_current_time_decimals (int, optional): Same as
            `display_current_decimals` in
            `specrel.graphics.simpgraph.BaseAnimator`.
        others: See `specrel.graphics.simpgraph.BaseAnimator`.
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

class STAnimator(TimeAnimator, STPlotter, ABC):
    """TimeAnimator that fulfills the `specrel.graphics.simpgraph.STPlotter`
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

        STPlotter.__init__(self, fig, ax)
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
            `specrel.graphics.simpgraph.WorldlinePlotter`.
        equal_lim_expand (float, optional): See
            `specrel.graphics.simpgraph.WorldlinePlotter`.
        others: See `specrel.graphics.simpgraph.STAnimator`.

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
        self._worldline_plotter = WorldlinePlotter(self.fig, self.ax,
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
        others: See `specrel.graphics.simpgraph.STAnimator`.

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

"""
    lorentz_transformable = a LorentzTransformable to animate a transformation
        for
    velocity = final velocity for the transformation. Initial velocity is
        assumed to be 0
    origin = origin to be used for the transformation
    stanimator = STAnimator initializer (NOT and instance). This is because
        many properties depend on the TransformAnimator's params, and must be
        initialized properly from within
    stanimator_options = dict of allowed initializer options for the STAnimator
        {
            <STAnimator kwargs except
            fig, ax, instant_pause_time, fps, display_current_time, title>
        }
    tlim, xlim = (min, max) tuples for the plotting limits for the animation.
        Any element that's None will be automatically filled
    time = fixed time value at which to carry out the transformation
    transition_duration = duration in seconds of the animation
    title = static title to be displayed throughout the animation
    """
class TransformAnimator(BaseAnimator, SingleAxisFigureCreator):
    """Animator where the frame variable is velocity, i.e. animates a spacetime
    transformation as the object is accelerated instantaneously.

    Args:
        lorentz_transformable (specrel.geom.LorentzTransformable): Object to
            animate.
        velocity (float): Relative velocity of the frame to transform to.
        origin (tuple, optional): See attributes.
        stanimator (type, optional): initializer of the
            `specrel.graphics.simpgraph.STAnimator` to take drawing
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
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        ax (matplotlib.axes.Axes, optional): See
            `specrel.graphics.simpgraph.SingleAxisFigureCreator`.
        transition_duration (float, optional):
        fps (float, optional): Animation frames per second.
        display_current_velocity (bool, optional): Same as `display_current` in
            `specrel.graphics.simpgraph.BaseAnimator`.
        display_current_velocity_decimals (int, optional): Same as
            `display_current_decimals` in
            `specrel.graphics.simpgraph.BaseAnimator`.
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

        SingleAxisFigureCreator.__init__(self, fig, ax)
        nsteps = round(transition_duration * fps)
        BaseAnimator.__init__(self, self.fig, velocity / nsteps, fps,
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
