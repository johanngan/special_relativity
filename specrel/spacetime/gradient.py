"""Objects that form color gradients across regions of spacetime, representing
continuous change of some sort.
"""

from matplotlib.colors import to_rgba

import specrel.geom as geom

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
