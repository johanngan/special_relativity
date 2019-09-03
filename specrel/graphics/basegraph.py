"""Basic graphics and base classes for spacetime plots and animations in
special relativity."""

from abc import ABC, abstractmethod

import matplotlib.pyplot as plt

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
            `specrel.graphics.basegraph.SingleAxisFigureCreator`.
        ax (matplotlib.axes.Axes, optional): See
            `specrel.graphics.basegraph.SingleAxisFigureCreator`.
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
        """See `specrel.graphics.basegraph.STPlotter.draw_point`.

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
        """See `specrel.graphics.basegraph.STPlotter.draw_line_segment`.

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
        """See `specrel.graphics.basegraph.STPlotter.draw_shaded_polygon`.

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
