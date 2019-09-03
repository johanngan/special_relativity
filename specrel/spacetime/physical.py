"""Spacetime objects with direct physical relevance that ease measurement and
calculation of physical properties.
"""

import math

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
