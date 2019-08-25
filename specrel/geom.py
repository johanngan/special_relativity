"""The geometry of special relativity"""
from abc import ABC, abstractmethod
import copy
from math import atan2
import warnings

# Commonly used default parameters shared by multiple geom classes
geomrc = {
    # Origin for Lorentz transformations
    'origin': (0, 0),
    # Draw limits
    'tlim': (None, None),
    'xlim': (None, None),
    # "Name" for an object, to be overlaid when an object is drawn
    'tag': None,
    # Numerical precision for internal comparison logic, and also for string
    # representations of objects
    'precision': 7,
    # kwargs to pass onto MPL when drawing an object
    # Okay to have a mutable dict here; ctors will copy
    'draw_options': {},
    'ribbon.default_edgecolor': 'black',
}

"""Something that obeys Lorentz transformations"""
class LorentzTransformable(ABC):
    @abstractmethod
    def __init__(self, tag, draw_options):
        self.tag = tag
        self.draw_options = dict(draw_options)

    """Lorentz transform the object with some velocity about some origin"""
    @abstractmethod
    def lorentz_transform(self, velocity, origin):
        raise NotImplementedError

    """Lorentz boost the object with some velocity about some origin.
    Just a convenience function."""
    def lorentz_boost(self, velocity, origin=geomrc['origin']):
        self.lorentz_transform(-velocity, origin)

    """Drawing logic for an object, contingent on a DI for boilerplate plotting
    implementation via plotter (a graphics.simpgraph.STPlotter instance)"""
    @abstractmethod
    def draw(self, plotter, tlim, xlim, **kwargs):
        raise NotImplementedError

    """Determine automatic draw limits if one or more aren't given,
    in the format (tmin, tmax), (xmin, xmax)"""
    @abstractmethod
    def _auto_draw_lims(self):
        raise NotImplementedError

    """Fill in automatic limits only where explicit limits aren't given, and
    return in the format (tmin, tmax), (xmin, xmax)"""
    def _fill_auto_lims(self, tlim, xlim):
        tmin, tmax, xmin, xmax = tlim + xlim
        if None in tlim + xlim:
            # Only compute automatic limits if needed
            (tminauto, tmaxauto), (xminauto, xmaxauto) = self._auto_draw_lims()
            if tmin is None:
                tmin = tminauto
            if tmax is None:
                tmax = tmaxauto
            if xmin is None:
                xmin = xminauto
            if xmax is None:
                xmax = xmaxauto
        return (tmin, tmax), (xmin, xmax)

"""Return a Lorentz transformed copy of a LorentzTransformable"""
def lorentz_transformed(transformable, velocity, origin=geomrc['origin']):
    transformed = copy.deepcopy(transformable)
    transformed.lorentz_transform(velocity, origin)
    return transformed

"""Return a Lorentz-boosted copy of a LorentzTransformable"""
def lorentz_boosted(transformable, velocity, origin=geomrc['origin']):
    boosted = copy.deepcopy(transformable)
    boosted.lorentz_boost(velocity, origin)
    return boosted

"""(1+1)-D spacetime vector (i.e. 1 space + 1 time)"""
class STVector(LorentzTransformable):
    def __init__(self, *args, **kwargs):
        # args can either be:
        #   - 2 arguments: [t, x]
        #   - 1 argument: an existing STVector() to copy
        #   - 1 argument: some other iterable representing (t, x)
        # kwargs can include: 'tag', 'precision', 'draw_options'
        if len(args) == 2:
            # t and x were individually provided
            self.constructor(*args, **kwargs)
        elif len(args) == 1:
            # An iterable representing (t, x) was provided
            # This can function as a copy ctor if said iterable was an STVector
            self.constructor(*args[0], **kwargs)
            # If no tag is given explicitly, copy over the old tag if it exists
            # i.e. if the object is an STVector, not just a tuple or something
            if 'tag' not in kwargs:
                try:
                    self.tag = args[0].tag
                except:
                    pass
            # If no precision given, copy over the old precision if it exists
            if 'precision' not in kwargs:
                try:
                    self.precision = args[0].precision
                except:
                    pass
            # If no draw options given, copy over the old ones if they exist
            if 'draw_options' not in kwargs:
                try:
                    self.draw_options = dict(args[0].draw_options)
                except:
                    pass
        else:
            raise TypeError('Too many positional arguments.')

    """The actual constructor underlying __init__"""
    def constructor(self, time, position, tag=geomrc['tag'],
        precision=geomrc['precision'], draw_options=geomrc['draw_options']):
        super().__init__(tag=tag, draw_options=draw_options)
        self.t = time
        self.x = position
        self.precision = precision

    """The order is (t, x), consistent with standard notation for 4-position
    in physics"""
    def __getitem__(self, key):
        return [self.t, self.x][key]

    """String representation of vector components as an ordered pair, (t, x)"""
    def __str__(self):
        return f'STVector({round(self.t, self.precision)}, ' \
            + f'{round(self.x, self.precision)})'

    def __iter__(self):
        yield self.t
        yield self.x

    """Equality within internal precision settings"""
    def __eq__(self, other):
        # Compare up to the precision of the two objects
        try:
            precision = min(self.precision, other.precision)
        except AttributeError:  # other has no precision field
            precision = self.precision

        for selfcmp, othercmp in zip(self, other):
            if round(selfcmp, precision) != round(othercmp, precision):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def __neg__(self):
        return STVector((-cmp for cmp in self))

    """Vector-vector addition"""
    def __add__(self, other):
        return STVector((left + right for left, right in zip(self, other)))

    """Vector-vector subtraction"""
    def __sub__(self, other):
        return self + -other

    """Spacetime interval"""
    def __abs__(self):
        return -self.t**2 + self.x**2

    def lorentz_transform(self, velocity, origin=geomrc['origin']):
        gamma = self.gamma_factor(velocity)
        t, x = self
        t0, x0 = origin
        self.t = gamma*((t - t0) - velocity*(x - x0)) + t0
        self.x = gamma*((x - x0) - velocity*(t - t0)) + x0

    def draw(self, plotter, tlim=geomrc['tlim'], xlim=geomrc['xlim'], **kwargs):
        # Only draw if in bounds
        tlim, xlim = self._fill_auto_lims(tlim, xlim)
        if self._in_bounds(tlim, xlim):
            kwargs = {**self.draw_options, **kwargs}
            plotter.draw_point(self, tag=self.tag, **kwargs)
            plotter.set_lims(tlim, xlim)

    def _auto_draw_lims(self):
        return (self.t, self.t), (self.x, self.x)

    """Check if the point is in a given set of bounds"""
    def _in_bounds(self, tlim, xlim):
        return (round(self.t, self.precision) >= round(tlim[0], self.precision) \
            and round(self.t, self.precision) <= round(tlim[1], self.precision) \
            and round(self.x, self.precision) >= round(xlim[0], self.precision) \
            and round(self.x, self.precision) <= round(xlim[1], self.precision))

    """Calculate the relativistic gamma factor for a given velocity"""
    @staticmethod
    def gamma_factor(velocity):
        return 1/(1 - velocity**2)**0.5

"""Collection of LorentzTransformables
Holds references, rather than copies, similar to a list"""
class Collection(LorentzTransformable):
    def __init__(self, transformables=(), tag=geomrc['tag'],
        draw_options=geomrc['draw_options']):
        super().__init__(tag=tag, draw_options=draw_options)
        self.transformables = []
        for tr in transformables:
            self.transformables.append(tr)

    def __getitem__(self, key):
        return self.transformables[key]

    def __iter__(self):
        yield from self.transformables

    def __len__(self):
        return len(self.transformables)

    def append(self, transformable):
        if not isinstance(transformable, LorentzTransformable):
            raise ValueError('Appended object must be LorentzTransformable')
        self.transformables.append(transformable)

    def pop(self, pos=-1):
        return self.transformables.pop(pos)

    def lorentz_transform(self, velocity, origin=geomrc['origin']):
        for tr in self:
            tr.lorentz_transform(velocity, origin)

    def draw(self, plotter, tlim=geomrc['tlim'], xlim=geomrc['xlim'], **kwargs):
        # Cannot draw an empty collection, so just do nothing
        if len(self) == 0:
            warnings.warn('Nothing to draw')
            return
        kwargs = {**self.draw_options, **kwargs}
        # Fill in automatic limits
        tlim, xlim = self._fill_auto_lims(tlim, xlim)
        # Plot each transformable with the same limits
        for tr in self:
            tr.draw(plotter, tlim, xlim, **kwargs)
        # Make sure plot limits are properly set
        plotter.set_lims(tlim, xlim)

    def _auto_draw_lims(self):
        tmin, tmax, xmin, xmax = None, None, None, None
        for tr in self:
            (new_tmin, new_tmax), (new_xmin, new_xmax) = tr._auto_draw_lims()
            tmin = new_tmin if tmin is None else min(tmin, new_tmin)
            tmax = new_tmax if tmax is None else max(tmax, new_tmax)
            xmin = new_xmin if xmin is None else min(xmin, new_xmin)
            xmax = new_xmax if xmax is None else max(xmax, new_xmax)
        return (tmin, tmax), (xmin, xmax)

"""Collection of spacetime points"""
class PointGroup(Collection):
    # Modes for how to treat a PointGroup
    POINT = 0   # Individual points
    CONNECT = 1 # Points connected by line segments
    POLYGON = 2 # Points define vertices of a polygon

    def __init__(self, points, mode=POINT, tag=geomrc['tag'],
        draw_options=geomrc['draw_options']):
        # Registered drawing methods for each mode
        self.MODE_DRAW_METHODS = {
            PointGroup.POINT: self._draw_point,
            PointGroup.CONNECT: self._draw_connect,
            PointGroup.POLYGON: self._draw_polygon
        }
        self.mode = mode
        super().__init__([STVector(p) for p in points],
            tag=tag, draw_options=draw_options)

    def draw(self, plotter, tlim=geomrc['tlim'], xlim=geomrc['xlim'], **kwargs):
        kwargs = {**self.draw_options, **kwargs}
        # Fill in automatic limits
        tlim, xlim = self._fill_auto_lims(tlim, xlim)
        # Dispatch based on mode
        self.MODE_DRAW_METHODS[self.mode](plotter, tlim, xlim, **kwargs)
        # Make sure plot limits are properly set
        plotter.set_lims(tlim, xlim)

    """Drawing for unconnected points"""
    def _draw_point(self, plotter, tlim, xlim, **kwargs):
        super().draw(plotter, tlim, xlim, **kwargs)

    """Drawing for connected line segments"""
    def _draw_connect(self, plotter, tlim, xlim, **kwargs):
        # Use the overall collection's tag on each line segment
        for p1, p2 in zip(self[:-1], self[1:]):
            plotter.draw_line_segment(p1, p2, tag=self.tag, **kwargs)

    """Drawing for points specifying polygon vertices"""
    def _draw_polygon(self, plotter, tlim, xlim, **kwargs):
        # Use the overall collection's tag
        plotter.draw_shaded_polygon(self, tag=self.tag, **kwargs)

"""A finite line segment"""
def line_segment(point1, point2, tag=geomrc['tag'],
    draw_options=geomrc['draw_options']):
    return PointGroup([point1, point2], PointGroup.CONNECT, tag, draw_options)

"""A finite polygon"""
def polygon(points, tag=geomrc['tag'], draw_options=geomrc['draw_options']):
    return PointGroup(points, PointGroup.POLYGON, tag, draw_options)

"""An infinite line in spacetime"""
class Line(Collection):
    def __init__(self, direction, point, tag=geomrc['tag'],
        precision=geomrc['precision'], draw_options=geomrc['draw_options']):
        # Zero direction would give a point geometrically, but would make
        # intersection calculation, etc. more annoying
        if STVector(direction, precision=precision) == (0, 0):
            raise ValueError('Direction vector cannot be zero')
        super().__init__([STVector(direction, precision=precision),
            STVector(point, precision=precision)],
            tag=tag, draw_options=draw_options)

    """Vector parameterization of the line as a string.
    E.g. Line( [t, x] = [3, 4] + k*[1, 1] )"""
    def __str__(self):
        precision = self.precision()
        return f'Line( [t, x] = [{round(self.point()[0], precision)}, ' \
            + f'{round(self.point()[1], precision)}]' \
            + f' + k*[{round(self.direction()[0], precision)}, ' \
            + f'{round(self.direction()[1], precision)}] )'

    def __eq__(self, other):
        # Equality is just one of the outcomes in the intersection method
        # The returned value will be a Line iff the lines are equal
        return isinstance(self.intersect(other), Line)

    def __ne__(self, other):
        return not (self == other)

    def append(self, other):
        raise TypeError("Cannot append to object of type 'Line'")

    def lorentz_transform(self, velocity, origin=geomrc['origin']):
        # If the origin is shifted, apply the shifted transform only to the
        # point, and not the direction
        self.point().lorentz_transform(velocity, origin)
        self.direction().lorentz_transform(velocity)

    """Direction vector"""
    def direction(self):
        return self[0]

    """A point that the line passes through"""
    def point(self):
        return self[1]

    """The precision of the internal STVectors"""
    def precision(self):
        return min([p.precision for p in self])

    """Slope of the line. None if vertical."""
    def slope(self):
        if self.direction().x == 0:
            return None
        return self.direction().t / self.direction().x

    """Intersection point between two lines. Returns the intersection point
    as an STVector in normal cases,
    or a Line if the two are equal,
    or None if parallel."""
    def intersect(self, other):
        # Compare up to the precision of the two lines
        precision = min(self.precision(), other.precision())

        # Solution for the parameterization variable at the intersection point
        # from doing algebra
        # self is the line: self.point() + lineparam * self.direction()
        lineparam_numerator = (
            other.point().x * other.direction().t
            - other.point().t * other.direction().x
            + other.direction().x * self.point().t
            - other.direction().t * self.point().x)
        lineparam_denominator = (
            self.direction().x * other.direction().t
            - self.direction().t * other.direction().x)

        # Zero denominator means the lines have equal slope
        if round(lineparam_denominator, precision) == 0:
            # 0/0 means the lines are equal
            # otherwise, the lines are parallel
            if round(lineparam_numerator, precision) == 0:
                return copy.deepcopy(self)
            else:
                return None

        # Lines intersect at a point
        lineparam = lineparam_numerator / lineparam_denominator
        return STVector(
            self.point().t + lineparam * self.direction().t,
            self.point().x + lineparam * self.direction().x,
            precision=precision)

    """Returns a list of point intersections of a line with the time and
    space boundaries, sorted in ascending order by time, then space"""
    def _boundary_intersections(self, tlim, xlim):
        # The four sides of the bounding box
        boundaries = [
            fixedtime(tlim[0]), fixedtime(tlim[1]),
            fixedspace(xlim[0]), fixedspace(xlim[1])
        ]
        boundary_points = []    # Intersected points on the bounding box
        for bound in boundaries:
            # If the line is parallel to one set of bounds, it will cross the
            # perpendicular bounds; just skip
            crossing = self.intersect(bound)
            if isinstance(crossing, Line) or crossing is None:
                continue
            # Add it to the boundary point list if it's not already there
            if crossing not in boundary_points:
                boundary_points.append(crossing)
        return sorted(boundary_points, key=lambda p:(p.t, p.x))

    def draw(self, plotter, tlim=geomrc['tlim'], xlim=geomrc['xlim'], **kwargs):
        kwargs = {**self.draw_options, **kwargs}
        # Fill in automatic limits
        tlim, xlim = self._fill_auto_lims(tlim, xlim)

        # Clip to the bounding box, and add keep points if they're in-bounds
        boundary_points = [p for p in self._boundary_intersections(tlim, xlim)
            if p._in_bounds(tlim, xlim)]
        # This shouldn't happen, but issue a warning and fall back to the first
        # and last points if it does
        if len(boundary_points) > 2:
            warnings.warn('Clipped line has more than two endpoints. '
                'Floating point error with a corner clip?')
            boundary_points = [boundary_points[0], boundary_points[-1]]

        # Plot the clipped line segment
        if len(boundary_points) == 2:
            plotter.draw_line_segment(*boundary_points, tag=self.tag, **kwargs)
        # One boundary point means the line clips a corner; just plot the point
        elif len(boundary_points) == 1:
            # Use the line's tag
            STVector(boundary_points[0], tag=self.tag).draw(
                plotter, tlim, xlim, **kwargs)
        # No boundary points means the line is completely out of frame, so
        # do nothing

        # Make sure plot limits are properly set
        plotter.set_lims(tlim, xlim)

    def _auto_draw_lims(self):
        # Go one step of the direction vector forward and backward from the
        # anchor point
        forward = self.point() + self.direction()
        backward = self.point() - self.direction()
        tmin = min(forward.t, backward.t)
        tmax = max(forward.t, backward.t)
        xmin = min(forward.x, backward.x)
        xmax = max(forward.x, backward.x)
        return (tmin, tmax), (xmin, xmax)

"""Returns a line of fixed space across all time"""
def fixedspace(position, draw_options=geomrc['draw_options']):
    return Line((1, 0), (0, position), draw_options=draw_options)

"""Returns a line of fixed time across all space"""
def fixedtime(time, draw_options=geomrc['draw_options']):
    return Line((0, 1), (time, 0), draw_options=draw_options)

"""An infinite ray in spacetime. Note that intersection only works if the
argument is a vanilla Line, not a Ray"""
class Ray(Line):
    """Same format as a line, but with a qualifier that k >= 0"""
    def __str__(self):
        raystr = super().__str__().replace('Line', 'Ray')
        close_paren = raystr.rfind(')')
        return raystr[:close_paren] + 'where k >= 0 ' + raystr[close_paren:]

    def __eq__(self, other):
        return (
            self.point() == other.point() and
            self.slope() == other.slope() and
            self.direction().t * other.direction().t >= 0 and
            self.direction().x * other.direction().x >= 0
        )

    def __ne__(self, other):
        return not (self == other)

    def append(self, other):
        raise TypeError("Cannot append to object of type 'Ray'")

    """Calculates the dot product between the vector from the Ray's anchor to
    a point, and the Ray's direction vector"""
    def point_dotprod(self, point):
        return sum([(x - p)*d for x, p, d in zip(
            point, self.point(), self.direction())])

    """Intersection point between a ray and a line. Returns the intersection
    point as an STVector in normal cases, or a Ray if the two are coincide,
    or None if no intersection."""
    def intersect(self, line):
        # Pretend this is a full line to start
        ll_intersect = super().intersect(line)
        if ll_intersect is None:
            # If no intersection, one object being a Ray won't change anything
            return ll_intersect
        if isinstance(ll_intersect, Line):
            return copy.deepcopy(self)  # Replace the full line with the Ray

        precision = min(self.precision(), line.precision())
        if round(self.point_dotprod(ll_intersect), precision) < 0:
            # The intersection is opposite to the Ray's direction; i.e. no
            # actual intersection
            return None
        return ll_intersect

    def _auto_draw_lims(self):
        # Go one step of the direction vector forward from the anchor point
        forward = self.point() + self.direction()
        tmin = min(forward.t, self.point().t)
        tmax = max(forward.t, self.point().t)
        xmin = min(forward.x, self.point().x)
        xmax = max(forward.x, self.point().x)
        return (tmin, tmax), (xmin, xmax)

    """Returns a list of point intersections of a ray with the time and
    space boundaries, sorted in ascending order by time, then space, including
    the ray endpoint"""
    def _boundary_intersections(self, tlim, xlim):
        boundary_points = super()._boundary_intersections(tlim, xlim)
        # Add the ray endpoint
        if self.point() not in boundary_points:
            boundary_points.append(self.point())
        # Re-sort, since a new point was added
        return sorted(boundary_points, key=lambda p:(p.t, p.x))

"""The region between two parallel spacetime lines"""
class Ribbon(Collection):
    def __init__(self, line1, line2, tag=geomrc['tag'],
        draw_options=geomrc['draw_options']):
        if line1.slope() != line2.slope():
            raise ValueError('Lines must be parallel')
        super().__init__([copy.deepcopy(line1), copy.deepcopy(line2)],
            tag=tag, draw_options=draw_options)

    def append(self, other):
        raise TypeError("Cannot append to object of type 'Ribbon'")

    """Test whether a point lies inside the two line boundaries"""
    def _point_inside(self, point):
        # Compare up to the precision of the two lines and the point
        precision = min(self[0].precision(), self[1].precision())
        try:    # If point is an STVector
            precision = min(precision, point.precision)
        except:
            pass

        # The lines will be parallel, so just take the direction vector from
        # the first line
        direction = self[0].direction()
        # Lines follow the equation dx*t - dt*x = k
        # The constant "k" of the point (t, x) must be between those of the two
        # line boundaries
        def calc_line_constant(p):
            return round(direction.x * p[0] - direction.t * p[1], precision)
        boundary_constants = sorted(
            [calc_line_constant(line.point()) for line in self]
        )
        point_constant = calc_line_constant(point)
        return (round(point_constant, precision)
            >= round(boundary_constants[0], precision)
            and round(point_constant, precision)
            <= round(boundary_constants[1], precision))

    """Get a list of hard boundaries (i.e. the line boundaries)"""
    def _boundaries(self):
        return list(self)

    """Get the polygon vertices for drawing the ribbon in a given view range"""
    def _get_vertices(self, tlim, xlim):
        vertices = []
        # Gather all the unique candidates for vertices; all intersections
        # between all boundaries, essentially
        for line in self._boundaries():
            for p in line._boundary_intersections(tlim, xlim):
                if p not in vertices:
                    vertices.append(p)
        # Corners of the bounds, too
        for tcorner in tlim:
            for xcorner in xlim:
                corner = STVector(tcorner, xcorner)
                if corner not in vertices:
                    vertices.append(corner)

        # Filter out candidate points, keeping only those that are both in
        # bounds, and inside the HalfRibbon region
        vertices = [p for p in vertices if
            (p._in_bounds(tlim, xlim) and self._point_inside(p))]
        # If no vertices, just return empty
        if not vertices:
            return vertices
        # Otherwise, order the vertices by the angle they make with the
        # centroid of the polygon
        tvals, xvals = tuple(zip(*vertices))
        t_center = sum(tvals) / len(tvals)
        x_center = sum(xvals) / len(xvals)
        return sorted(vertices, key=lambda v: atan2(
            v.t - t_center, v.x - x_center))

    def draw(self, plotter, tlim=geomrc['tlim'], xlim=geomrc['xlim'], **kwargs):
        kwargs = {**self.draw_options, **kwargs}
        tlim, xlim = self._fill_auto_lims(tlim, xlim)

        # If the two lines are equal, treat it like a line, but use the main
        # ribbon tag
        if self[0] == self[1]:
            ln = copy.deepcopy(self[0])
            ln.tag = self.tag
            ln.draw(plotter, tlim, xlim, **kwargs)
            return

        # Only draw if there are vertices in bounds
        vertices = self._get_vertices(tlim, xlim)
        if not vertices:
            return

        # Set aside "edgecolor" for special treatment
        edgecolor = kwargs.pop('edgecolor', geomrc['ribbon.default_edgecolor'])
        plotter.draw_shaded_polygon(vertices, tag=self.tag, **kwargs)
        # Plot the ribbon edges
        if edgecolor.lower() != 'none':
            # Remove facecolor
            kwargs.pop('facecolor', None)
            # Only include a label for the face, not the edges
            kwargs.pop('label', None)
            # If color was given, override edgecolor
            if 'color' in kwargs:
                edgecolor = kwargs.pop('color')
            # Make the zorder of the borders match that of the patch
            # zorder of 1 by default
            zorder = kwargs.pop('zorder', 1)
            for line in self:
                line.draw(plotter, tlim, xlim, color=edgecolor, zorder=zorder,
                    **kwargs)

"""The region between two parallel spacetime rays"""
class HalfRibbon(Ribbon):
    def __init__(self, ray1, ray2, tag=geomrc['tag'],
        draw_options=geomrc['draw_options']):
        # PARALLEL; antiparallel isn't good enough
        if (ray1.slope() != ray2.slope() or
            ray1.direction().t * ray2.direction().t < 0 or
            ray1.direction().x * ray2.direction().x < 0):
            raise ValueError('Rays must be parallel')
        super().__init__(copy.deepcopy(ray1), copy.deepcopy(ray2),
            tag=tag, draw_options=draw_options)

    def append(self, other):
        raise TypeError("Cannot append to object of type 'HalfRibbon'")

    """Get a list of hard boundaries (ray anchors and line boundaries)"""
    def _boundaries(self):
        # Add the separation line between the two Ray anchors as a hard
        # boundary
        direction = self[1].point() - self[0].point()
        return super()._boundaries() + [Line(direction, self[0].point())]

    """Test whether a point lies between the two ray boundaries"""
    def _point_inside(self, point):
        def dotprod(vec1, vec2):
            return sum([v1*v2 for v1, v2 in zip(vec1, vec2)])

        # Compare up to the precision of the two rays and the point
        precision = min(self[0].precision(), self[1].precision())
        try:    # If point is an STVector
            precision = min(precision, point.precision)
        except:
            pass

        # Get a normal vector to the line connecting the two anchors of the
        # HalfRibbon's rays. Namely, get the separation vector, then swap the
        # components and make one of them negative. There are two options.
        # Pick the normal vector that points outwards from the interior;
        # i.e. the dot product between the normal vector and the ray direction
        # vectors should be negative.
        sep_vec = self[1].point() - self[0].point()
        normal_vecs = [STVector(-sep_vec[1], sep_vec[0]),
                       STVector(sep_vec[1], -sep_vec[0])]
        # Pick the normal vector that points outward.
        # The equality is for when the two rays coincide; the normal vectors
        # will both either be zero or orthogonal to the rays, so neither will
        # get filtered out. Just pick the first one; it won't matter in this
        # case.
        normal_vec = [n for n in normal_vecs
            if dotprod(n, self[0].direction()) <= 0][0]

        # Get the displacement vector from the point to one of the ray's
        # anchors (it doesn't matter which). The point is on the "interior"
        # side of the anchors if and only if the dot product between this
        # separation vector and the normal vector is nonnegative.
        #
        # The full Ribbon's _point_inside method can check for whether or not
        # the point lies laterally between the two rays
        disp_vec = self[0].point() - STVector(point)
        return (round(dotprod(disp_vec, normal_vec), precision) >= 0
            and super()._point_inside(point))
