"""Physical objects, events, and other useful compound objects in spacetime.
Core geometric classes are in geom.py"""
import copy
import math

from matplotlib.colors import to_rgba

import specrel.geom as geom

"""Spacetime grid with some spacing on some range"""
def stgrid(tlim, xlim, origin=geom.geomrc['origin'], t_spacing=1, x_spacing=1,
    axis_draw_options=geom.geomrc['draw_options'],
    grid_draw_options=geom.geomrc['draw_options']):
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
class MovingObject(geom.Ribbon):
    """
    left_start_pos is the position of the left end of the object at
    t = start_time
    """
    def __init__(self, left_start_pos, length=0, velocity=0, start_time=0,
        tag=geom.geomrc['tag'], draw_options=geom.geomrc['draw_options']):
        super().__init__(
            geom.Line((1, velocity), (start_time, left_start_pos)),
            geom.Line((1, velocity), (start_time, left_start_pos + length)),
            tag=tag,
            draw_options=draw_options
        )

    """Returns the left end"""
    def left(self):
        return self[0]

    """Returns the right end"""
    def right(self):
        return self[1]

    """Returns position of an object (represented by a line) at a given time"""
    @staticmethod
    def _pos_at_time(line, time):
        return line.intersect(geom.fixedtime(time)).x

    """Returns time at which an object (represented by a line) will reach a
    specified position"""
    @staticmethod
    def _time_for_pos(line, pos):
        # Throw an error if the object isn't moving
        if line.slope() is None:
            raise RuntimeError('Object is not moving.')
        return line.intersect(geom.fixedspace(pos)).t

    """Returns left end position at some time"""
    def left_pos(self, time):
        return self._pos_at_time(self.left(), time)

    """Returns right end position at some time"""
    def right_pos(self, time):
        return self._pos_at_time(self.right(), time)

    """Returns the centroid position at some time"""
    def center_pos(self, time):
        return (self.left_pos(time) + self.right_pos(time)) / 2

    """Returns the time when the left end reaches some position"""
    def time_for_left_pos(self, pos):
        return self._time_for_pos(self.left(), pos)

    """Returns the time when the right end reaches some position"""
    def time_for_right_pos(self, pos):
        return self._time_for_pos(self.right(), pos)

    """Returns the time when the centroid reaches some position"""
    def time_for_center_pos(self, pos):
        return (self.time_for_left_pos(pos) + self.time_for_right_pos(pos)) / 2

    """Returns the current physical length of the object"""
    def length(self):
        # Compare when fixing to t = 0
        return self.right_pos(0) - self.left_pos(0)

    """Has spatial extent and isn't just a 0-D point object"""
    def has_extent(self):
        return self.length() != 0

    """Return the velocity of the object"""
    def velocity(self):
        return self[0].direction().x / self[0].direction().t

"""A point or interval of time (exists across all space), possibly with a
possible delay across space"""
class TimeInterval(geom.Ribbon):
    """
    unit_delay is the delay between start times at the x and x + 1
    start_time is the starting time of the interval at x = start_pos
    """
    def __init__(self, start_time, duration=0, unit_delay=0, start_pos=0,
        tag=geom.geomrc['tag'], draw_options=geom.geomrc['draw_options']):
        super().__init__(
            geom.Line((unit_delay, 1), (start_time, start_pos)),
            geom.Line((unit_delay, 1), (start_time + duration, start_pos)),
            tag=tag,
            draw_options=draw_options
        )

    """Returns the interval start"""
    def start(self):
        return self[0]

    """Returns the interval end"""
    def end(self):
        return self[1]

    """Returns the time value of an event (represented by a line) at a given
    position"""
    @staticmethod
    def _time_at_pos(line, position):
        return line.intersect(geom.fixedspace(position)).t

    """Returns start time at some position"""
    def start_time(self, position):
        return self._time_at_pos(self.start(), position)

    """Returns the end time at some position"""
    def end_time(self, position):
        return self._time_at_pos(self.end(), position)

    """Return the current duration of the interval"""
    def duration(self):
        # Compare when fixing to x = 0
        return self.end_time(0) - self.start_time(0)

    """Has temporal extent and isn't just a single time value"""
    def has_extent(self):
        return self.duration() != 0

    """Return the delay between start times at positions separated by
    one spatial unit. A delay of 0 implies simultaneity"""
    def unit_delay(self):
        return self[0].direction().t / self[0].direction().x

"""Calculate a linear color gradient value between two points at some
proportion x, where 0 is the start point/color, and 1 is the end point/color"""
def _calc_colorgrad(x, point1, point2, color1, color2):
    color1 = to_rgba(color1)
    color2 = to_rgba(color2)
    xpoint = tuple([p1 + x*(p2 - p1) for p1, p2 in zip(point1, point2)])
    xcolor = tuple([c1 + x*(c2 - c1) for c1, c2 in zip(color1, color2)])
    return xpoint, xcolor
"""Checks whether an rgba value is a valid color or not"""
def _valid_color(col):
    for c in col:
        if c < 0 or c > 1:
            return False
    return True
"""Extrapolates a linear color gradient between two points to the extreme
endpoints of colorspace, at some interval resolution"""
def _colorgrad_extremes(point1, point2, color1, color2, divisions):
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

"""Forms a line with a color gradient. Divisions is the number of line segment
divisions in the gradient."""
def gradient_line(point1, point2, color1, color2, divisions=100,
    extrapolate_color=True, draw_options=geom.geomrc['draw_options']):
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
