import unittest

import specrel.geom as geom
from specrel.graphics.simpgraph import STPlotter

class _MockSTPlotter(STPlotter):
    """Mock plotter for draw() methods.

    Just tabulates the objects it's told to draw, but doesn't actually draw
    anything.
    """
    def __init__(self):
        # Tuples with all the given object info
        self.points = []
        self.segments = []
        self.polygons = []

        self.tlim = [None, None]
        self.xlim = [None, None]

    def draw_point(self, point, tag, **kwargs):
        self.points.append((tuple(point), tag, kwargs))

    def draw_line_segment(self, point1, point2, tag, **kwargs):
        self.segments.append((tuple(point1), tuple(point2), tag, kwargs))

    def draw_shaded_polygon(self, vertices, tag, **kwargs):
        self.polygons.append(([tuple(v) for v in vertices], tag, kwargs))

    def set_lims(self, tlim, xlim):
        self.tlim = tlim
        self.xlim = xlim

    # Only for interactive mode; doesn't matter here, but abstract method must
    # be overridden
    def show(self):
        pass

    # For testing stored draw objects within numerical precision
    @staticmethod
    def points_equal(testcase, p1, p2):
        for x, y in zip(p1[0], p2[0]):
            testcase.assertAlmostEqual(x, y)
        testcase.assertEqual(p1[1:], p2[1:])

    @staticmethod
    def segments_equal(testcase, s1, s2):
        for x, y in zip(s1[0] + s1[1], s2[0] + s2[1]):
            testcase.assertAlmostEqual(x, y)
        testcase.assertEqual(s1[2:], s2[2:])

    @staticmethod
    def polygons_equal(testcase, p1, p2):
        for v1, v2 in zip(p1[0], p2[0]):
            for x, y in zip(v1, v2):
                testcase.assertAlmostEqual(x, y)
        testcase.assertEqual(p1[1:], p2[1:])

class STVectorInitTests(unittest.TestCase):
    """Instance initialization."""
    def test_init_from_timepos(self):
        stvec = geom.STVector(2, 3)
        self.assertEqual(stvec.t, 2)
        self.assertEqual(stvec.x, 3)

    def test_init_from_iterable(self):
        stvec = geom.STVector((2, 3))
        self.assertEqual(stvec.t, 2)
        self.assertEqual(stvec.x, 3)

    def test_copy_ctor(self):
        stvec = geom.STVector(2, 3,
            tag='test', precision=4, draw_options={'color': 'red'})
        stvec_cpy = geom.STVector(stvec)
        self.assertEqual(stvec.t, stvec_cpy.t)
        self.assertEqual(stvec.x, stvec_cpy.x)
        self.assertEqual(stvec.tag, 'test')
        self.assertEqual(stvec.precision, stvec_cpy.precision)
        self.assertEqual(stvec.draw_options, {'color': 'red'})

    def test_copy_ctor_with_override(self):
        stvec = geom.STVector(2, 3, precision=4)
        stvec_cpy = geom.STVector(stvec, precision=6, tag='test')
        self.assertEqual(stvec_cpy.precision, 6)
        self.assertEqual(stvec_cpy.tag, 'test')

    def test_init_invalid_nargs(self):
        self.assertRaises(TypeError, geom.STVector, 2, 3, 4)

class STVectorOverloadTests(unittest.TestCase):
    """Overloaded operators and special methods."""
    def test_getitem(self):
        stvec = geom.STVector(2, 3)
        self.assertEqual(stvec[0], 2)
        self.assertEqual(stvec[1], 3)

    def test_str(self):
        self.assertEqual(str(geom.STVector(2, 3)), 'STVector(2, 3)')

    def test_str_within_precision(self):
        self.assertEqual(str(geom.STVector(2.001, 2.999, precision=3)),
            'STVector(2.001, 2.999)')
        self.assertEqual(str(geom.STVector(2.0001, 2.9999, precision=3)),
            'STVector(2.0, 3.0)')

    def test_iter(self):
        for cmp, answer in zip(geom.STVector(2, 3), [2, 3]):
            self.assertEqual(cmp, answer)

    def test_eq(self):
        self.assertEqual(geom.STVector(2, 3), (2, 3))

    def test_eq_within_precision(self):
        self.assertEqual(geom.STVector(2, 3, precision=3), (2.0001, 3))
        self.assertNotEqual(geom.STVector(2, 3, precision=3), (2.001, 3))

    def test_neg(self):
        self.assertEqual(-geom.STVector(2, 3), geom.STVector(-2, -3))

    def test_add(self):
        self.assertEqual(geom.STVector(2, 3) + geom.STVector(3, 3), (5, 6))

    def test_abs(self):
        self.assertEqual(abs(geom.STVector(2, 3)), 5)

class STVectorCoreTests(unittest.TestCase):
    """Actual core functionality as spacetime objects."""
    def test_lorentz_transform(self):
        stvec = geom.STVector(2, 3)
        stvec.lorentz_transform(3/5)
        self.assertAlmostEqual(stvec.t, 1/4)
        self.assertAlmostEqual(stvec.x, 9/4)

    def test_lorentz_transform_origin_1_1(self):
        stvec = geom.STVector(3, 4)
        stvec.lorentz_transform(3/5, origin=(1, 1))
        self.assertAlmostEqual(stvec.t, 1/4 + 1)
        self.assertAlmostEqual(stvec.x, 9/4 + 1)

    def test_draw_in_bounds(self):
        p = _MockSTPlotter()
        geom.STVector(3, 4, tag='test', draw_options={'color': 'red'}).draw(p)
        self.assertEqual(len(p.points), 1)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 0)
        self.assertEqual(p.points[0], ((3, 4), 'test', {'color': 'red'}))
        self.assertEqual(p.tlim, (3, 3))
        self.assertEqual(p.xlim, (4, 4))

    def test_draw_out_of_bounds(self):
        p = _MockSTPlotter()
        geom.STVector(3, 4).draw(p, tlim=(4, 5))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 0)

    def test_auto_draw_lims(self):
        self.assertEqual(geom.STVector(2, 3)._auto_draw_lims(),
            ((2, 2), (3, 3)))

    def test_in_bounds(self):
        stvec = geom.STVector(2, 3)
        self.assertTrue(stvec._in_bounds((0, 3), (2, 4)))
        self.assertFalse(stvec._in_bounds((3, 4), (1, 2)))

    def test_in_bounds_within_precision(self):
        stvec1 = geom.STVector(2.0001, 3.0001, precision=3)
        self.assertTrue(stvec1._in_bounds((0, 2), (2, 3)))

        stvec2 = geom.STVector(2.001, 3.001, precision=3)
        self.assertFalse(stvec2._in_bounds((0, 2), (2, 3)))

    def test_in_bounds_exact_equality(self):
        self.assertTrue(geom.STVector(2, 3)._in_bounds((2, 2), (3, 3)))

    # Tests specifically for the gamma_factor() static method
    def test_gamma_factor_stationary(self):
        self.assertEqual(geom.STVector.gamma_factor(0), 1)

    def test_gamma_factor_at_c(self):
        self.assertRaises(ZeroDivisionError, geom.STVector.gamma_factor, 1)

    def test_gamma_factor_ftl(self):
        self.assertIsInstance(geom.STVector.gamma_factor(2), complex)

    def test_gamma_factor_three_fifths(self):
        self.assertAlmostEqual(geom.STVector.gamma_factor(3/5), 5/4)

class test_lorentz_transformed(unittest.TestCase):
    def setUp(self):
        self.original = geom.STVector(2, 3)
        self.transformed = geom.lorentz_transformed(self.original, 3/5)

    def test_transformed_values(self):
        self.assertAlmostEqual(self.transformed[0], 1/4)
        self.assertAlmostEqual(self.transformed[1], 9/4)

    def test_deep_copied(self):
        # Check that the original wasn't mutated
        self.assertNotAlmostEqual(self.original[0], self.transformed[0])
        self.assertNotAlmostEqual(self.original[1], self.transformed[1])

class CollectionTests(unittest.TestCase):
    def setUp(self):
        group = geom.PointGroup([(0, 1), (2, 3)])
        line = geom.Line((0, 1), (2, 3))
        ribbon = geom.Ribbon(geom.Line((0, 1), (2, 3)),
            geom.Line((0, 1), (0, 0)))
        self.collection = geom.Collection([group, line, ribbon])

    def test_init(self):
        self.assertEqual(self.collection[0][0], (0, 1))
        self.assertEqual(self.collection[0][1], (2, 3))
        self.assertEqual(self.collection[1].direction(), (0, 1))
        self.assertEqual(self.collection[1].point(), (2, 3))
        self.assertEqual(self.collection[2][0].direction(), (0, 1))
        self.assertEqual(self.collection[2][0].point(), (2, 3))
        self.assertEqual(self.collection[2][1].direction(), (0, 1))
        self.assertEqual(self.collection[2][1].point(), (0, 0))

    def test_append(self):
        self.collection.append(geom.STVector(5, 5))
        self.assertEqual(len(self.collection), 4)
        self.assertEqual(self.collection[3], (5, 5))

    def test_append_nontransformable(self):
        self.assertRaises(ValueError, self.collection.append, 1)

    def test_lorentz_transform(self):
        v = 3/5
        group_transformed = geom.lorentz_transformed(
            geom.PointGroup([(0, 1), (2, 3)]), v)
        line_transformed = geom.lorentz_transformed(
            geom.Line((0, 1), (2, 3)), v)
        ribbon_transformed = geom.lorentz_transformed(
            geom.Ribbon(geom.Line((0, 1), (2, 3)), geom.Line((0, 1), (0, 0))),
            v)
        self.collection.lorentz_transform(v)

        self.assertAlmostEqual(self.collection[0][0], group_transformed[0])
        self.assertAlmostEqual(self.collection[0][1], group_transformed[1])
        self.assertAlmostEqual(self.collection[1].direction(),
            line_transformed.direction())
        self.assertAlmostEqual(self.collection[1].point(),
            line_transformed.point())
        self.assertAlmostEqual(self.collection[2][0].direction(),
            ribbon_transformed[0].direction())
        self.assertAlmostEqual(self.collection[2][0].point(),
            ribbon_transformed[0].point())
        self.assertAlmostEqual(self.collection[2][1].direction(),
            ribbon_transformed[1].direction())
        self.assertAlmostEqual(self.collection[2][1].point(),
            ribbon_transformed[1].point())

    def test_draw(self):
        p = _MockSTPlotter()
        self.collection.draw(p, tlim=(-5, 5), xlim=(-5, 5))
        self.assertEqual(len(p.points), 2)
        p.points_equal(self, p.points[0], ((0, 1), None, {}))
        p.points_equal(self, p.points[1], ((2, 3), None, {}))
        self.assertEqual(len(p.segments), 3)
        p.segments_equal(self, p.segments[0], ((2, -5), (2, 5), None, {}))
        self.assertEqual(len(p.polygons), 1)
        p.polygons_equal(self, p.polygons[0],
            ([(0, -5), (0, 5), (2, 5), (2, -5)], None, {}))
        p.segments_equal(self, p.segments[1], ((2, -5), (2, 5), None,
                {'color': geom.geomrc['ribbon.default_edgecolor'], 'zorder': 1}))
        p.segments_equal(self, p.segments[2], ((0, -5), (0, 5), None,
                {'color': geom.geomrc['ribbon.default_edgecolor'], 'zorder': 1}))
        self.assertEqual(p.tlim, (-5, 5))
        self.assertEqual(p.xlim, (-5, 5))

    def test_auto_draw_lims(self):
        self.assertEqual(self.collection._auto_draw_lims(), ((0, 2), (-1, 4)))

class PointGroupTests(unittest.TestCase):
    def setUp(self):
        self.group = geom.PointGroup([(0, 0), (0, 1), (1, 0)], tag='test')

    def test_init(self):
        self.assertEqual(self.group[0].t, 0)
        self.assertEqual(self.group[0].x, 0)
        self.assertEqual(self.group[1].t, 0)
        self.assertEqual(self.group[1].x, 1)
        self.assertEqual(self.group[2].t, 1)
        self.assertEqual(self.group[2].x, 0)
        self.assertEqual(self.group.mode, geom.PointGroup.POINT)

    def test_draw(self):
        p = _MockSTPlotter()
        self.group.draw(p)
        self.assertEqual(len(p.points), 3)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 0)
        self.assertEqual(p.points[0], ((0, 0), None, {}))
        self.assertEqual(p.points[1], ((0, 1), None, {}))
        self.assertEqual(p.points[2], ((1, 0), None, {}))
        self.assertEqual(p.tlim, (0, 1))
        self.assertEqual(p.xlim, (0, 1))

    def test_draw_connect(self):
        self.group.mode = geom.PointGroup.CONNECT
        p = _MockSTPlotter()
        self.group.draw(p)
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 2)
        self.assertEqual(len(p.polygons), 0)
        p.segments_equal(self, p.segments[0], ((0, 0), (0, 1), 'test', {}))
        p.segments_equal(self, p.segments[1], ((0, 1), (1, 0), 'test', {}))
        self.assertEqual(p.tlim, (0, 1))
        self.assertEqual(p.xlim, (0, 1))

    def test_draw_polygon(self):
        self.group.mode = geom.PointGroup.POLYGON
        p = _MockSTPlotter()
        self.group.draw(p)
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 1)
        p.polygons_equal(self, p.polygons[0],
            ([(0, 0), (0, 1), (1, 0)], 'test', {}))
        self.assertEqual(p.tlim, (0, 1))
        self.assertEqual(p.xlim, (0, 1))

class LineInitTests(unittest.TestCase):
    """Instance initialization."""
    def test_init(self):
        line = geom.Line((0, 1), (2, 3), precision=7, tag='test',
            draw_options={'color': 'red'})
        self.assertEqual(line.direction().t, 0)
        self.assertEqual(line.direction().x, 1)
        self.assertEqual(line.point().t, 2)
        self.assertEqual(line.point().x, 3)
        self.assertEqual(line.precision(), 7)
        self.assertEqual(line.tag, 'test')
        self.assertEqual(line.draw_options, {'color': 'red'})

    def test_init_error_on_zero_direction(self):
        self.assertRaises(ValueError, geom.Line, (0, 0), (2, 3))

    def test_init_with_override(self):
        line = geom.Line(geom.STVector(0, 1, precision=7),
            geom.STVector(2, 3, precision=7), precision=5, tag='test')
        self.assertEqual(line.precision(), 5)
        self.assertEqual(line.tag, 'test')

class LineOverloadTests(unittest.TestCase):
    """Overloaded operators and special methods."""
    def test_str(self):
        self.assertEqual(str(geom.Line((0, 1), (2, 3))),
            'Line( [t, x] = [2, 3] + k*[0, 1] )')

    def test_str_within_precision(self):
        self.assertEqual(str(
            geom.Line((0.001, 1.001), (2.001, 2.999), precision=3)),
            'Line( [t, x] = [2.001, 2.999] + k*[0.001, 1.001] )')
        self.assertEqual(str(
            geom.Line((0.0001, 1.0001), (2.0001, 2.9999), precision=3)),
            'Line( [t, x] = [2.0, 3.0] + k*[0.0, 1.0] )')

    def test_eq_same(self):
        self.assertEqual(geom.Line((1, 1), (2, 3)), geom.Line((1, 1), (2, 3)))

    def test_eq_diff_params(self):
        self.assertEqual(geom.Line((1, 1), (2, 3)), geom.Line((2, 2), (1, 2)))

    def test_eq_within_precision(self):
        self.assertEqual(geom.Line((1.0001, 1), (2, 3), precision=3),
            geom.Line((1, 1), (2, 3)))
        self.assertNotEqual(geom.Line((1.001, 1), (2, 3), precision=3),
            geom.Line((1, 1), (2, 3)))

    def test_cannot_append(self):
        self.assertRaises(TypeError, geom.Line((0, 1), (2, 3)).append,
            geom.STVector(1, 1))

class LineCoreTests(unittest.TestCase):
    """Actual core functionality as spacetime objects."""
    def test_lorentz_transform_origin_1_1(self):
        line = geom.Line((2, 3), (3, 4))
        line.lorentz_transform(3/5, origin=(1, 1))
        self.assertAlmostEqual(line.direction().t, 1/4)
        self.assertAlmostEqual(line.direction().x, 9/4)
        self.assertAlmostEqual(line.point().t, 1/4 + 1)
        self.assertAlmostEqual(line.point().x, 9/4 + 1)

    def test_draw_in_bounds(self):
        line = geom.Line((1, 1), (2, 3))
        p = _MockSTPlotter()
        line.draw(p, tlim=(-1, 2), xlim=(0, 2))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 1)
        self.assertEqual(len(p.polygons), 0)
        p.segments_equal(self, p.segments[0], ((-1, 0), (1, 2), None, {}))
        self.assertEqual(p.tlim, (-1, 2))
        self.assertEqual(p.xlim, (0, 2))

    def test_draw_out_of_bounds(self):
        line = geom.Line((1, 1), (2, 3))
        p = _MockSTPlotter()
        line.draw(p, tlim=(2, 3), xlim=(0, 1))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 0)

    def test_auto_draw_lims(self):
        line = geom.Line((1, -1), (2, 3))
        self.assertEqual(line._auto_draw_lims(), ((1, 3), (2, 4)))

    def test_slope_nonvertical(self):
        self.assertEqual(geom.Line((1, 2), (2, 3)).slope(), 0.5)

    def test_slope_vertical(self):
        self.assertIsNone(geom.Line((1, 0), (2, 3)).slope())

class LineIntersectTests(unittest.TestCase):
    """Line intersection logic."""
    def test_boundary_intersections_diag(self):
        line = geom.Line((1, 1), (0.5, 0))
        tlim = (0, 1)
        xlim = (0, 1)
        self.assertEqual(line._boundary_intersections(tlim, xlim),
            [(0, -0.5), (0.5, 0), (1, 0.5), (1.5, 1)])

    def test_boundary_intersections_horz(self):
        line = geom.Line((0, 1), (0.5, 0))
        tlim = (0, 1)
        xlim = (0, 1)
        self.assertEqual(line._boundary_intersections(tlim, xlim),
            [(0.5, 0), (0.5, 1)])

    def test_boundary_intersections_corner(self):
        line = geom.Line((1, -1), (1, 0))
        tlim = (0, 1)
        xlim = (0, 1)
        self.assertEqual(line._boundary_intersections(tlim, xlim),
            [(0, 1), (1, 0)])

    def test_intersect_is_symmetric(self):
        line1 = geom.Line((1, 1), (0, 0))
        line2 = geom.Line((1, -1), (0, 2))
        self.assertEqual(line1.intersect(line2), line2.intersect(line1))

    def test_intersect_point_slanted_lines(self):
        line1 = geom.Line((1, 1), (0, 0))
        line2 = geom.Line((1, -1), (0, 2))
        self.assertEqual(line1.intersect(line2), (1, 1))

    def test_intersect_point_one_vertical(self):
        vertline = geom.Line((1, 0), (0, 0))
        otherline = geom.Line((1, -1), (0, 2))
        self.assertEqual(otherline.intersect(vertline), (2, 0))

    def test_intersect_point_one_horizontal(self):
        horzline = geom.Line((0, 1), (0, 0))
        otherline = geom.Line((1, -1), (2, 0))
        self.assertEqual(otherline.intersect(horzline), (0, 2))

    def test_intersect_point_vertical_and_horizontal(self):
        vertline = geom.Line((1, 0), (0, 1))
        horzline = geom.Line((0, 1), (1, 0))
        self.assertEqual(vertline.intersect(horzline), (1, 1))

    def test_intersect_parallel(self):
        self.assertIsNone(
            geom.Line((1, 1), (0, 0)).intersect(geom.Line((2, 2), (0, 1))))

    def test_intersect_equal_lines_diff_direction_diff_point(self):
        line1 = geom.Line((1, 1), (2, 3))
        line2 = geom.Line((2, 2), (3, 4))
        intersection = line1.intersect(line2)
        self.assertIsInstance(intersection, geom.Line)
        self.assertEqual(intersection.direction(), line1.direction())
        self.assertEqual(intersection.point(), line1.point())

class RayOverloadTests(unittest.TestCase):
    """Overloaded operators and special methods."""
    def test_str(self):
        self.assertEqual(str(geom.Ray((0, 1), (2, 3))),
            'Ray( [t, x] = [2, 3] + k*[0, 1] where k >= 0 )')

    def test_eq(self):
        self.assertEqual(geom.Ray((1, 1), (2, 3)), geom.Ray((1, 1), (2, 3)))

    def test_eq_scaled_dir(self):
        self.assertEqual(geom.Ray((1, 1), (2, 3)), geom.Ray((2, 2), (2, 3)))

    def test_neq_diff_point(self):
        self.assertNotEqual(geom.Ray((1, 1), (2, 3)), geom.Ray((1, 1), (1, 2)))

    def test_neq_opp_dir(self):
        self.assertNotEqual(geom.Ray((1, 1), (2, 3)),
            geom.Ray((-1, -1), (2, 3)))

class RayCoreTests(unittest.TestCase):
    """Actual core functionality as spacetime objects."""
    def test_draw_endpoint_out_of_bounds(self):
        ray = geom.Ray((-1, -1), (2, 3))
        p = _MockSTPlotter()
        ray.draw(p, tlim=(-1, 2), xlim=(0, 2))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 1)
        self.assertEqual(len(p.polygons), 0)
        p.segments_equal(self, p.segments[0], ((-1, 0), (1, 2), None, {}))

    def test_draw_endpoint_in_bounds(self):
        ray = geom.Ray((1, 1), (0, 1))
        p = _MockSTPlotter()
        ray.draw(p, tlim=(-1, 2), xlim=(0, 2))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 1)
        self.assertEqual(len(p.polygons), 0)
        p.segments_equal(self, p.segments[0], ((0, 1), (1, 2), None, {}))

    def test_draw_totally_out_of_bounds(self):
        ray = geom.Ray((1, 1), (2, 3))
        p = _MockSTPlotter()
        ray.draw(p, tlim=(-1, 2), xlim=(0, 2))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 0)

    def test_auto_draw_lims(self):
        ray = geom.Ray((1, -1), (2, 3))
        self.assertEqual(ray._auto_draw_lims(), ((2, 3), (2, 3)))

class RayIntersectTests(unittest.TestCase):
    """Ray-line intersection logic."""
    def test_boundary_intersections_exterior_endpoint(self):
        ray = geom.Ray((0, 1), (0.5, -1))
        tlim = (0, 1)
        xlim = (0, 1)
        self.assertEqual(ray._boundary_intersections(tlim, xlim),
            [(0.5, -1), (0.5, 0), (0.5, 1)])

    def test_boundary_intersections_interior_endpoint(self):
        ray = geom.Ray((0, 1), (0.5, 0.5))
        tlim = (0, 1)
        xlim = (0, 1)
        self.assertEqual(ray._boundary_intersections(tlim, xlim),
            [(0.5, 0.5), (0.5, 1)])

    def test_intersect_parallel(self):
        ray = geom.Ray((1, 1), (0, 0))
        line = geom.Line((2, 2), (0, 1))
        self.assertIsNone(ray.intersect(line))

    def test_intersect_equal_lines_diff_direction_diff_point(self):
        ray = geom.Ray((1, 1), (2, 3))
        line = geom.Line((2, 2), (3, 4))
        intersection = ray.intersect(line)
        self.assertIsInstance(intersection, geom.Ray)
        self.assertEqual(intersection.direction(), ray.direction())
        self.assertEqual(intersection.point(), ray.point())

    def test_actual_intersection_full_crossing(self):
        ray = geom.Ray((1, 0), (0, 1))
        line = geom.Line((0, 1), (1, 0))
        self.assertEqual(ray.intersect(line), (1, 1))

    def test_actual_intersection_tangent(self):
        ray = geom.Ray((1, 0), (1, 1))
        line = geom.Line((0, 1), (1, 0))
        self.assertEqual(ray.intersect(line), (1, 1))

    def test_ghost_intersection(self):
        ray = geom.Ray((1, 0), (2, 1))
        line = geom.Line((0, 1), (1, 0))
        self.assertIsNone(ray.intersect(line))

class RibbonBasicTests(unittest.TestCase):
    """Basic functionality tests."""
    def test_init(self):
        ribbon = geom.Ribbon(geom.Line((0, 1), (2, 3)),
            geom.Line((0, 1), (0, 0)), tag='test',
            draw_options={'color': 'red'})
        self.assertEqual(ribbon[0].direction().t, 0)
        self.assertEqual(ribbon[0].direction().x, 1)
        self.assertEqual(ribbon[0].point().t, 2)
        self.assertEqual(ribbon[0].point().x, 3)
        self.assertEqual(ribbon[1].direction().t, 0)
        self.assertEqual(ribbon[1].direction().x, 1)
        self.assertEqual(ribbon[1].point().t, 0)
        self.assertEqual(ribbon[1].point().x, 0)
        self.assertEqual(ribbon.tag, 'test')
        self.assertEqual(ribbon.draw_options, {'color': 'red'})

    def test_init_not_parallel(self):
        self.assertRaises(ValueError, geom.Ribbon,
            geom.Line((0, 1), (2, 3)), geom.Line((1, 1), (2, 3)))

    def test_cannot_append(self):
        self.assertRaises(TypeError, geom.Line((0, 1), (2, 3)).append,
            geom.STVector(1, 1))

    def test_draw(self):
        p = _MockSTPlotter()
        ribbon = geom.Ribbon(geom.Line((0, 1), (2, 3)),
            geom.Line((0, 1), (0, 0)), tag='test',
                draw_options={'facecolor': 'red', 'label': 'test2'})
        ribbon.draw(p, tlim=(-2, 3), xlim=(0, 1))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 2)
        self.assertEqual(len(p.polygons), 1)
        p.polygons_equal(self, p.polygons[0],
            ([(0, 0), (0, 1), (2, 1), (2, 0)], 'test',
                {'facecolor': 'red', 'label': 'test2'}))
        p.segments_equal(self, p.segments[0], ((2, 0), (2, 1), None,
            {'color': geom.geomrc['ribbon.default_edgecolor'], 'zorder': 1}))
        p.segments_equal(self, p.segments[1], ((0, 0), (0, 1), None,
            {'color': geom.geomrc['ribbon.default_edgecolor'], 'zorder': 1}))
        self.assertEqual(p.tlim, (-2, 3))
        self.assertEqual(p.xlim, (0, 1))

    def test_draw_no_edges(self):
        p = _MockSTPlotter()
        ribbon = geom.Ribbon(geom.Line((0, 1), (2, 3)),
            geom.Line((0, 1), (0, 0)), draw_options={'edgecolor': 'None'})
        ribbon.draw(p, tlim=(-2, 3), xlim=(0, 1))
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 1)

    def test_draw_out_of_bounds(self):
        p = _MockSTPlotter()
        ribbon = geom.Ribbon(geom.Line((0, 1), (2, 3)),
            geom.Line((0, 1), (0, 0)))
        ribbon.draw(p, tlim=(4, 5), xlim=(0, 1))
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 0)

class RibbonBoundaryTests(unittest.TestCase):
    """Tests for bounds checking logic."""
    def test_point_inside(self):
        ribbon = geom.Ribbon(geom.Line((1, 1), (0, 2)),
            geom.Line((1, 1), (0, 0)))
        self.assertTrue(ribbon._point_inside((0, 1)))

    def test_point_not_inside(self):
        ribbon = geom.Ribbon(geom.Line((1, 1), (0, 2)),
            geom.Line((1, 1), (0, 0)))
        self.assertFalse(ribbon._point_inside((0, 3)))

    def test_point_on_boundary(self):
        ribbon = geom.Ribbon(
            geom.Line((1, 1), (0, 2)),
            geom.Line((1, 1), (0, 0))
        )
        self.assertTrue(ribbon._point_inside((0, 2)))

class RibbonGetVerticesTests(unittest.TestCase):
    def test_get_vertices_flat_lines(self):
        ribbon = geom.Ribbon(
            geom.Line((0, 1), (1, 0)),
            geom.Line((0, 1), (2, 0)),
        )
        self.assertEqual(ribbon._get_vertices((0, 3), (0, 3)),
            [
                (1, 0),
                (1, 3),
                (2, 3),
                (2, 0)
            ]
        )

    def test_get_vertices_exact_boundary(self):
        ribbon = geom.Ribbon(
            geom.Line((0, 1), (1, 0)),
            geom.Line((0, 1), (3, 0)),
        )
        self.assertEqual(ribbon._get_vertices((0, 3), (0, 3)),
            [
                (1, 0),
                (1, 3),
                (3, 3),
                (3, 0)
            ]
        )

    def test_get_vertices_lines_straddle_corner(self):
        ribbon = geom.Ribbon(
            geom.Line((1, 1), (1, 0)),
            geom.Line((1, 1), (0, 1)),
        )
        self.assertEqual(ribbon._get_vertices((0, 2), (0, 2)),
            [
                (0, 0),
                (0, 1),
                (1, 2),
                (2, 2),
                (2, 1),
                (1, 0)
            ]
        )

    def test_get_vertices_line_on_corner(self):
        ribbon = geom.Ribbon(
            geom.Line((1, 1), (1, 0)),
            geom.Line((1, 1), (0, 2)),
        )
        self.assertEqual(ribbon._get_vertices((0, 2), (0, 2)),
            [
                (0, 0),
                (0, 2),
                (2, 2),
                (2, 1),
                (1, 0)
            ]
        )

    def test_get_vertices_one_line_out_of_bounds(self):
        ribbon = geom.Ribbon(
            geom.Line((1, 1), (1, 0)),
            geom.Line((1, 1), (0, 3)),
        )
        self.assertEqual(ribbon._get_vertices((0, 2), (0, 2)),
            [
                (0, 0),
                (0, 2),
                (2, 2),
                (2, 1),
                (1, 0)
            ]
        )

    def test_get_vertices_both_lines_out_of_bounds(self):
        ribbon = geom.Ribbon(
            geom.Line((1, 1), (3, 0)),
            geom.Line((1, 1), (0, 3)),
        )
        self.assertEqual(ribbon._get_vertices((0, 2), (0, 2)),
            [
                (0, 0),
                (0, 2),
                (2, 2),
                (2, 0)
            ]
        )

class HalfRibbonBasicTests(unittest.TestCase):
    """Basic functionality tests."""
    def test_init_error_on_antiparallel(self):
        self.assertRaises(ValueError, geom.HalfRibbon,
            geom.Ray((0, 1), (0, 0)), geom.Ray((0, -1), (2, 3)))

    def test_draw_endpoints_out_of_bounds(self):
        p = _MockSTPlotter()
        h = geom.HalfRibbon(geom.Ray((0, 1), (2, -3)),
            geom.Ray((0, 1), (0, -1)), draw_options={'edgecolor': 'None'})
        h.draw(p, tlim=(-2, 3), xlim=(0, 1))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 1)
        p.polygons_equal(self, p.polygons[0],
            ([(0, 0), (0, 1), (2, 1), (2, 0)], None, {}))

    def test_draw_totally_out_of_bounds(self):
        p = _MockSTPlotter()
        h = geom.HalfRibbon(geom.Ray((0, 1), (2, 3)), geom.Ray((0, 1), (0, 2)))
        h.draw(p, tlim=(-2, 3), xlim=(0, 1))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 0)

    def test_draw_endpoints_both_in_bounds(self):
        p = _MockSTPlotter()
        h = geom.HalfRibbon(geom.Ray((0, 1), (2, 0.5)),
            geom.Ray((0, 1), (0, 0.25)), draw_options={'edgecolor': 'None'})
        h.draw(p, tlim=(-2, 3), xlim=(0, 1))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 1)
        p.polygons_equal(self, p.polygons[0],
            ([(0, 0.25), (0, 1), (2, 1), (2, 0.5)], None, {}))

    def test_draw_endpoints_one_endpoint_out_of_bounds(self):
        p = _MockSTPlotter()
        h = geom.HalfRibbon(geom.Ray((0, 1), (2, 0.5)),
            geom.Ray((0, 1), (0, -0.5)), draw_options={'edgecolor': 'None'})
        h.draw(p, tlim=(-2, 3), xlim=(0, 1))
        self.assertEqual(len(p.points), 0)
        self.assertEqual(len(p.segments), 0)
        self.assertEqual(len(p.polygons), 1)
        p.polygons_equal(self, p.polygons[0],
            ([(0, 0), (0, 1), (2, 1), (2, 0.5), (1, 0)], None, {}))
