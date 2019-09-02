"""Contains convenience classes and synthesis functions for common spacetime
objects whose functionality would be possible to implement through just the
`specrel.geom` API, but would be rather annoying in practice.

Core geometric classes are in `specrel.geom`.
"""

import copy
import math

from matplotlib.colors import to_rgba

import specrel.geom as geom

def stgrid(tlim, xlim, origin=geom.geomrc['origin'], t_spacing=1, x_spacing=1,
    axis_draw_options=geom.geomrc['draw_options'],
    grid_draw_options=geom.geomrc['draw_options']):
    """Spacetime grid with some spacing on some range

    Args:
        tlim (tuple): Minimum and maximum time values for the grid.
        xlim (tuple): Minimum and maximum position values for the grid.
        origin (tuple, optional): (t, x) value defining the grid "center".
        t_spacing (float, optional): The spacing between grid lines of constant
            time.
        x_spacing (float, optional): The spacing between grid lines of constant
            position.
        axis_draw_options (dict, optional): Draw options for the axis lines
            passing through the origin. See `specrel.geom.LorentzTransformable`
            for details.
        grid_draw_options (dict, optional): Draw options for the grid lines
            not including the axis lines. See
            `specrel.geom.LorentzTransformable` for details.

    Returns:
        specrel.geom.Collection:
            collection of grid lines in the order
            `[constant t lines in ascending order of t,
            constant x lines in ascending order of x,
            t axis,
            x axis]`
    """
    # Default draw options if none are specified
    axis_draw_options = {'color': 'black', 'linewidth': 2, **axis_draw_options}
    grid_draw_options = {'color': 'darkgray', 'linewidth': 1, **grid_draw_options}

    gridlines = geom.Collection()
    # Add all the minor grid lines that fit within the limits
    down_steps = math.ceil((tlim[0] - origin[0]) / t_spacing)
    up_steps = math.floor((tlim[1] - origin[0]) / t_spacing)
    left_steps = math.ceil((xlim[0] - origin[1]) / x_spacing)
    right_steps = math.floor((xlim[1] - origin[1]) / x_spacing)
    for tstep in range(down_steps, up_steps+1):
        if tstep != 0:  # Add axes later
            gridlines.append(
                geom.Line((0, 1), (origin[0] + tstep*t_spacing, origin[1]),
                    draw_options=grid_draw_options))
    for xstep in range(left_steps, right_steps+1):
        if xstep != 0:
            gridlines.append(
                geom.Line((1, 0), (origin[0], origin[1] + xstep*x_spacing),
                    draw_options=grid_draw_options))

    # Add the axes if in range
    if origin[0] >= tlim[0] and origin[0] <= tlim[1]:
        gridlines.append(
            geom.Line((0, 1), origin, draw_options=axis_draw_options))
    if origin[1] >= xlim[0] and origin[1] <= xlim[1]:
        gridlines.append(
            geom.Line((1, 0), origin, draw_options=axis_draw_options))
    return gridlines

"""An object moving at some velocity"""
"""
    left_start_pos is the position of the left end of the object at
    t = start_time
    """
class MovingObject(geom.Ribbon):
    """An object moving at a constant velocity.

    Args:
        left_start_pos (float): Position of the object's left end at
            t = `start_time`.
        length (float, optional): Length of the object.
        velocity (float, optional): Velocity of the object.
        start_time (float, optional): Time corresponding to `left_start_pos`.
        tag (str, optional): See `specrel.geom.LorentzTransformable`.
        draw_options (dict, optional): See `specrel.geom.LorentzTransformable`.
    """
    def __init__(self, left_start_pos, length=0, velocity=0, start_time=0,
        tag=geom.geomrc['tag'], draw_options=geom.geomrc['draw_options']):
        super().__init__(
            geom.Line((1, velocity), (start_time, left_start_pos)),
            geom.Line((1, velocity), (start_time, left_start_pos + length)),
            tag=tag,
            draw_options=draw_options
        )

    def left(self):
        """
        Returns:
            specrel.geom.Line:
                Left end of the object throughout time.
        """
        return self[0]

    def right(self):
        """
        Returns:
            specrel.geom.Line:
                Right end of the object throughout time.
        """
        return self[1]

    @staticmethod
    def _pos_at_time(line, time):
        """Returns position of an object (represented by a line) at a given
        time."""
        return line.intersect(geom.fixedtime(time)).x

    @staticmethod
    def _time_for_pos(line, pos):
        """Returns time at which an object (represented by a line) will reach a
        specified position."""
        # Throw an error if the object isn't moving
        if line.slope() is None:
            raise RuntimeError('Object is not moving.')
        return line.intersect(geom.fixedspace(pos)).t

    def left_pos(self, time):
        """Returns the left end position at some time.

        Args:
            time (float): Time at which to get the position.

        Returns:
            float:
                Position of the object's left end at t = `time`.
        """
        return self._pos_at_time(self.left(), time)

    def right_pos(self, time):
        """Returns the right end position at some time.

        Args:
            time (float): Time at which to get the position.

        Returns:
            float:
                Position of the object's right end at t = `time`.
        """
        return self._pos_at_time(self.right(), time)

    def center_pos(self, time):
        """Returns the middle position at some time.

        Args:
            time (float): Time at which to get the position.

        Returns:
            float:
                Position of the object's midpoint at t = `time`.
        """
        return (self.left_pos(time) + self.right_pos(time)) / 2

    def time_for_left_pos(self, pos):
        """Returns the time when the left end reaches some position.

        Args:
            pos (float): Target position.

        Returns:
            float:
                Time at which the object's left end is at the target position.

        Raises:
            RuntimeError:
                If the object isn't moving.
        """
        return self._time_for_pos(self.left(), pos)

    def time_for_right_pos(self, pos):
        """Returns the time when the right end reaches some position.

        Args:
            pos (float): Target position.

        Returns:
            float:
                Time at which the object's right end is at the target position.

        Raises:
            RuntimeError:
                If the object isn't moving.
        """
        return self._time_for_pos(self.right(), pos)

    def time_for_center_pos(self, pos):
        """Returns the time when the center reaches some position.

        Args:
            pos (float): Target position.

        Returns:
            float:
                Time at which the object's midpoint is at the target position.

        Raises:
            RuntimeError:
                If the object isn't moving.
        """
        return (self.time_for_left_pos(pos) + self.time_for_right_pos(pos)) / 2

    def length(self):
        """
        Returns:
            float:
                The physical length of the object.
        """
        # Compare when fixing to t = 0
        return self.right_pos(0) - self.left_pos(0)

    def has_extent(self):
        """Checks whether the object has spatial extent or not.

        Returns:
            bool:
                Flag for whether the object has a nonzero length.
        """
        return self.length() != 0

    def velocity(self):
        """
        Returns:
            float:
                The velocity of the object.
        """
        return self[0].direction().x / self[0].direction().t

class TimeInterval(geom.Ribbon):
    """A time interval moving with some amount of spatial lag (starts at
    different times at different positions).

    Args:
        start_time (float): Start time of the interval at x = `start_pos`.
        duration (float, optional): Interval duration.
        unit_delay (float, optional): Delay between start times at x and x + 1.
        start_pos (float, optional): Position corresponding to `start_time`.
        tag (str, optional): See `specrel.geom.LorentzTransformable`.
        draw_options (dict, optional): See `specrel.geom.LorentzTransformable`.
    """
    def __init__(self, start_time, duration=0, unit_delay=0, start_pos=0,
        tag=geom.geomrc['tag'], draw_options=geom.geomrc['draw_options']):
        super().__init__(
            geom.Line((unit_delay, 1), (start_time, start_pos)),
            geom.Line((unit_delay, 1), (start_time + duration, start_pos)),
            tag=tag,
            draw_options=draw_options
        )

    def start(self):
        """
        Returns:
            specrel.geom.Line:
                The start of the interval across all space.
        """
        return self[0]

    def end(self):
        """
        Returns:
            specrel.geom.Line:
                The end of the interval across all space.
        """
        return self[1]

    @staticmethod
    def _time_at_pos(line, position):
        """Returns the time value of an event (represented by a line) at a given
        position."""
        return line.intersect(geom.fixedspace(position)).t

    def start_time(self, position):
        """Returns start time at some position.

        Args:
            position (float): Position at which to get the starting time.

        Returns:
            float:
                The starting time at x = `position`.
        """
        return self._time_at_pos(self.start(), position)

    def end_time(self, position):
        """Returns end time at some position.

        Args:
            position (float): Position at which to get the ending time.

        Returns:
            float:
                The ending time at x = `position`.
        """
        return self._time_at_pos(self.end(), position)

    def duration(self):
        """
        Returns:
            float:
                The duration of the time interval.
        """
        # Compare when fixing to x = 0
        return self.end_time(0) - self.start_time(0)

    def has_extent(self):
        """Checks whether the interval has temporal extent or not.

        Returns:
            bool:
                Flag for whether the object has a nonzero duration.
        """
        return self.duration() != 0

    def unit_delay(self):
        """Return the delay between start times at positions separated by
        one spatial unit. A delay of 0 implies simultaneity.

        Returns:
            float:
                Unit delay between the interval at x and x + 1.
        """
        return self[0].direction().t / self[0].direction().x

def _calc_colorgrad(x, point1, point2, color1, color2):
    """Calculate a linear color gradient value between two points at some
    proportion x, where 0 is the start point/color, and 1 is the end
    point/color.
    """
    color1 = to_rgba(color1)
    color2 = to_rgba(color2)
    xpoint = tuple([p1 + x*(p2 - p1) for p1, p2 in zip(point1, point2)])
    xcolor = tuple([c1 + x*(c2 - c1) for c1, c2 in zip(color1, color2)])
    return xpoint, xcolor

def _valid_color(col):
    """Checks whether an rgba value is a valid color or not."""
    for c in col:
        if c < 0 or c > 1:
            return False
    return True

def _colorgrad_extremes(point1, point2, color1, color2, divisions):
    """Extrapolates a linear color gradient between two points to the extreme
    endpoints of colorspace, at some interval resolution.
    """
    # Extend the range backwards
    i1 = 0
    while _valid_color(_calc_colorgrad(
        -(i1+1)/divisions, point1, point2, color1, color2)[1]):
        i1 += 1
    # Extend the range forwards
    i2 = 0
    while _valid_color(_calc_colorgrad(
        1 + (i2+1)/divisions, point1, point2, color1, color2)[1]):
        i2 += 1

    # Get the final extremes of the range
    ext_point1, ext_color1 = _calc_colorgrad(-i1/divisions,
        point1, point2, color1, color2)
    ext_point2, ext_color2 = _calc_colorgrad(1 + i2/divisions,
        point1, point2, color1, color2)
    return ext_point1, ext_point2, ext_color1, ext_color2, divisions + i1 + i2

def gradient_line(point1, point2, color1, color2, divisions=100,
    extrapolate_color=True, draw_options=geom.geomrc['draw_options']):
    """A line with a color gradient. The gradient transition will happen over
    a finite range in spacetime, and be monochromatic at either end.

    Args:
        point1 (specrel.geom.STVector or iterable): Starting point of the
            gradient.
        point2 (specrel.geom.STVector or iterable): Ending point of the
            gradient.
        color1 (color): A Matplotlib color for the gradient starting color.
        color2 (color): A Matplotlib color for the gradient ending color.
        divisions (int, optional): The number of line segment divisions in the
            gradient. More divisions means a smoother gradient.
        extrapolate_color (bool, optional): Flag for whether or not to
            extrapolate the color gradient across the line past the specified
            endpoints so that the color change spans as far as possible across
            the line.
        draw_options (dict, optional): See `specrel.geom.LorentzTransformable`.

    Returns:
        specrel.geom.Collection:
            Collection containing the color gradient increments, in the order:

            1. `specrel.geom.Ray` before `point1` with `color1`.
            2. Line segments changing color from `point1` to `point2`.
            3. `specrel.geom.Ray` after `point2` with `color2`.
    """
    # Copy draw_options and remove color if it's there
    draw_options = dict(draw_options)
    draw_options.pop('color', None)

    # If extrapolating color, calculate the color gradient extremes
    if extrapolate_color:
        point1, point2, color1, color2, divisions = _colorgrad_extremes(
            point1, point2, color1, color2, divisions)

    # Color gradient calculator for the given points and colors
    def this_colorgrad(x):
        return _calc_colorgrad(x, point1, point2, color1, color2)

    # Line direction vector
    direc = geom.STVector(point2) - geom.STVector(point1)

    grad = geom.Collection()
    # Monochromatic ray at the tail end of the gradient line
    grad.append(geom.Ray(-direc, point1,
        draw_options={'color': color1, **draw_options}))
    # The line segments comprising the color gradient
    for i in range(divisions):
        start_point, _ = this_colorgrad(i/divisions)
        end_point, _ = this_colorgrad((i+1)/divisions)
        _, grad_color = this_colorgrad((i+1/2)/divisions)
        grad.append(geom.line_segment(start_point, end_point,
            draw_options={'color': grad_color, **draw_options}))
    # Monochromatic ray at the head end of the gradient line
    grad.append(geom.Ray(direc, point2,
        draw_options={'color': color2, **draw_options}))
    return grad

def longitudinal_gradient_ribbon(line1_endpoints, line2_endpoints, color1,
    color2, divisions=100, extrapolate_color=True,
    draw_options=geom.geomrc['draw_options']):
    """A `specrel.geom.Ribbon`-esque object with a longitudinal color gradient
    (across the infinite direction).

    Args:
        line1_endpoints (list): list of two `specrel.geom.STVector`-convertible
            points defining the start and end positions of the gradient along
            the first edge of the ribbon.
        line2_endpoints (list): Same as `line1_endpoints`, but for the second
            edge of the ribbon.
        color1 (color): A Matplotlib color for the gradient starting color.
        color2 (color): A Matplotlib color for the gradient ending color.
        divisions (int, optional): The number of line segment divisions in the
            gradient. More divisions means a smoother gradient.
        extrapolate_color (bool, optional): Flag for whether or not to
            extrapolate the color gradient across the ribbon past the specified
            endpoints so that the color change spans as far as possible across
            the ribbon.
        draw_options (TYPE, optional): See `specrel.geom.LorentzTransformable`.

    Returns:
        specrel.geom.Collection:
            Collection containing the color gradient increments, in the order:

            1. `specrel.geom.HalfRibbon` with `color1` before both line starting
                points.
            2. Polygons changing color from starts of the lines to the ends.
            3. `specrel.geom.HalfRibbon` with `color2` after both line ending
                points.
    """
    # Copy draw_options and remove color, facecolor, and edgecolor if they're
    # there
    draw_options = dict(draw_options)
    draw_options.pop('color', None)
    draw_options.pop('facecolor', None)
    draw_options.pop('edgecolor', None)

    # If extrapolating color, calculate the color gradient extremes
    if extrapolate_color:
        point1, point2, color1, color2, divisions = _colorgrad_extremes(
            *line1_endpoints, color1, color2, divisions)
        line1_endpoints = (point1, point2)
        point1, point2, _, _, _ = _colorgrad_extremes(
            *line2_endpoints, color1, color2, divisions)
        line2_endpoints = (point1, point2)

    # Color gradient calculators for each line with the given colors
    def line1_colorgrad(x):
        return _calc_colorgrad(x, *line1_endpoints, color1, color2)
    def line2_colorgrad(x):
        return _calc_colorgrad(x, *line2_endpoints, color1, color2)

    # Direction vectors of each line
    direc1 = geom.STVector(line1_endpoints[1]) - geom.STVector(line1_endpoints[0])
    direc2 = geom.STVector(line2_endpoints[1]) - geom.STVector(line2_endpoints[0])
    grad = geom.Collection()
    # Form the monochromatic half ribbon at the tail end of the gradient
    # Overlap with the first polygon by half a division to mitigate any
    # boundary gaps
    start_point1, _ = line1_colorgrad(1/(2*divisions))
    start_point2, _ = line2_colorgrad(1/(2*divisions))
    grad.append(geom.HalfRibbon(
        geom.Ray(-direc1, start_point1),
        geom.Ray(-direc2, start_point2),
        # Explicitly turn off edge coloring
        draw_options={'facecolor': color1, 'edgecolor': 'None', **draw_options}))
    # Interior polygons comprising the color gradient
    for i in range(divisions):
        start_point1, _ = line1_colorgrad(i/divisions)
        # Overlap bands by half a division
        end_point1, _ = line1_colorgrad((i+1+1/2)/divisions)
        start_point2, _ = line2_colorgrad(i/divisions)
        end_point2, _ = line2_colorgrad((i+1+1/2)/divisions)
        _, grad_color = line1_colorgrad((i+1/2)/divisions)
        grad.append(geom.polygon(
            [start_point1, end_point1, end_point2, start_point2],
            draw_options={'facecolor': grad_color, **draw_options}))
    # Monochromatic half ribon at the head end of the gradient
    grad.append(geom.HalfRibbon(
        geom.Ray(direc1, line1_endpoints[1]),
        geom.Ray(direc2, line2_endpoints[1]),
        draw_options={'facecolor': color2, 'edgecolor': 'None', **draw_options}))
    return grad

def lateral_gradient_ribbon(direction, point1, point2, color1, color2,
    divisions=100, draw_options=geom.geomrc['draw_options']):
    """A `specrel.geom.Ribbon`-esque object with a lateral color gradient
    (across the finite direction).

    Args:
        direction (specrel.geom.STVector or iterable): Direction vector for the
            gradient.
        point1 (specrel.geom.STVector or iterable): A point that the first edge
            of the ribbon passes through.
        point2 (specrel.geom.STVector or iterable): A point that the second edge
            of the ribbon passes through.
        color1 (color): A Matplotlib color for the gradient starting color.
        color2 (color): A Matplotlib color for the gradient ending color.
        divisions (int, optional): The number of line segment divisions in the
            gradient. More divisions means a smoother gradient.
        draw_options (TYPE, optional): See `specrel.geom.LorentzTransformable`.

    Returns:
        specrel.geom.Collection:
            Collection containing the `specrel.geom.Ribbon` objects of slowly
            changing color from `point1` to `point2`.
    """
    # Copy draw_options and remove color, facecolor, and edgecolor if they're
    # there
    draw_options = dict(draw_options)
    draw_options.pop('color', None)
    draw_options.pop('facecolor', None)
    draw_options.pop('edgecolor', None)

    # Color gradient calculator for the given points and colors
    def this_colorgrad(x):
        return _calc_colorgrad(x, point1, point2, color1, color2)

    grad = geom.Collection()
    # Ribbons comprising the color gradient, as we move from point1 to point2
    for i in range(divisions):
        start_point, _ = this_colorgrad(i/divisions)
        # Overlap bands by half a division, except the last one
        end_point, _ = this_colorgrad(min((i+1+1/2)/divisions, 1))
        _, grad_color = this_colorgrad((i+1/2)/divisions)
        # Explicitly turn off edge coloring
        grad.append(geom.Ribbon(
            geom.Line(direction, start_point),
            geom.Line(direction, end_point),
            draw_options={'facecolor': grad_color, 'edgecolor': 'None',
                **draw_options}
        ))
    return grad
