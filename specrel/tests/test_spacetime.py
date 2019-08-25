import unittest

import specrel.geom as geom
import specrel.spacetime as st

class GridTests(unittest.TestCase):
    def test_stgrid(self):
        grid = st.stgrid((-1, 1), (-1, 1))
        self.assertEqual(len(grid), 6)
        self.assertEqual(grid[0], geom.Line((0, 1), (-1, 0)))
        self.assertEqual(grid[1], geom.Line((0, 1), (1, 0)))
        self.assertEqual(grid[2], geom.Line((1, 0), (0, -1)))
        self.assertEqual(grid[3], geom.Line((1, 0), (0, 1)))
        self.assertEqual(grid[4], geom.Line((0, 1), (0, 0)))
        self.assertEqual(grid[5], geom.Line((1, 0), (0, 0)))

class MovingObjectTests(unittest.TestCase):
    def setUp(self):
        self.obj = st.MovingObject(1, length=1, velocity=0.5)

    def test_init(self):
        self.assertEqual(self.obj[0], geom.Line((1, 0.5), (0, 1)))
        self.assertEqual(self.obj[1], geom.Line((1, 0.5), (0, 2)))

    def test_left_pos(self):
        self.assertEqual(self.obj.left_pos(1), 1.5)

    def test_right_pos(self):
        self.assertEqual(self.obj.right_pos(1), 2.5)

    def test_center_pos(self):
        self.assertEqual(self.obj.center_pos(1), 2)

    def test_time_for_left_pos(self):
        self.assertEqual(self.obj.time_for_left_pos(2), 2)

    def test_time_for_right_pos(self):
        self.assertEqual(self.obj.time_for_right_pos(3), 2)

    def test_time_for_center_pos(self):
        self.assertEqual(self.obj.time_for_center_pos(2.5), 2)

    def test_length(self):
        self.assertEqual(self.obj.length(), 1)

    def test_has_extent(self):
        self.assertTrue(self.obj.has_extent())
        self.assertFalse(st.MovingObject(1, 0, 0.5).has_extent())

    def test_velocity(self):
        self.assertEqual(self.obj.velocity(), 0.5)

class TimeIntervalTests(unittest.TestCase):
    def setUp(self):
        self.interval = st.TimeInterval(1, 1, 0.5)

    def test_init(self):
        self.assertEqual(self.interval[0], geom.Line((0.5, 1), (1, 0)))
        self.assertEqual(self.interval[1], geom.Line((0.5, 1), (2, 0)))

    def test_start_time(self):
        self.assertEqual(self.interval.start_time(1), 1.5)

    def test_end_time(self):
        self.assertEqual(self.interval.end_time(1), 2.5)

    def test_duration(self):
        self.assertEqual(self.interval.duration(), 1)

    def test_has_extent(self):
        self.assertTrue(self.interval.has_extent())
        self.assertFalse(st.TimeInterval(1, 0, 0.5).has_extent())

    def test_unit_delay(self):
        self.assertEqual(self.interval.unit_delay(), 0.5)

# Almost equal tuples
def _tuple_eq(testcase, c1, c2):
    for x, y in zip(c1, c2):
        testcase.assertAlmostEqual(x, y)

class GradLineTests(unittest.TestCase):
    def test_gradient_line(self):
        grad = st.gradient_line((0, 0), (1, 1), (1, 0, 0, 1), (0, 0, 1, 1),
            divisions=3)
        self.assertEqual(len(grad), 5)
        self.assertEqual(grad[0], geom.Ray((-1, -1), (0, 0)))
        _tuple_eq(self, grad[0].draw_options['color'], (1, 0, 0, 1))
        self.assertEqual(grad[1][0], (0, 0))
        self.assertEqual(grad[1][1], (1/3, 1/3))
        _tuple_eq(self, grad[1].draw_options['color'], (5/6, 0, 1/6, 1))
        self.assertEqual(grad[2][0], (1/3, 1/3))
        self.assertEqual(grad[2][1], (2/3, 2/3))
        _tuple_eq(self, grad[2].draw_options['color'], (3/6, 0, 3/6, 1))
        self.assertEqual(grad[3][0], (2/3, 2/3))
        self.assertEqual(grad[3][1], (1, 1))
        _tuple_eq(self, grad[3].draw_options['color'], (1/6, 0, 5/6, 1))
        self.assertEqual(grad[4], geom.Ray((1, 1), (1, 1)))
        _tuple_eq(self, grad[4].draw_options['color'], (0, 0, 1, 1))

    def test_extrapolate_color(self):
        grad = st.gradient_line((1/3, 1/3), (2/3, 2/3),
            (2/3, 0, 1/3, 1), (1/3, 0, 2/3, 1), divisions=1)
        self.assertEqual(len(grad), 5)
        self.assertEqual(grad[0], geom.Ray((-1, -1), (0, 0)))
        _tuple_eq(self, grad[0].draw_options['color'], (1, 0, 0, 1))
        self.assertEqual(grad[1][0], (0, 0))
        self.assertEqual(grad[1][1], (1/3, 1/3))
        _tuple_eq(self, grad[1].draw_options['color'], (5/6, 0, 1/6, 1))
        self.assertEqual(grad[2][0], (1/3, 1/3))
        self.assertEqual(grad[2][1], (2/3, 2/3))
        _tuple_eq(self, grad[2].draw_options['color'], (3/6, 0, 3/6, 1))
        self.assertEqual(grad[3][0], (2/3, 2/3))
        self.assertEqual(grad[3][1], (1, 1))
        _tuple_eq(self, grad[3].draw_options['color'], (1/6, 0, 5/6, 1))
        self.assertEqual(grad[4], geom.Ray((1, 1), (1, 1)))
        _tuple_eq(self, grad[4].draw_options['color'], (0, 0, 1, 1))

class LongGradRibbonTests(unittest.TestCase):
    def test_longitudinal_gradient_ribbon(self):
        grad = st.longitudinal_gradient_ribbon(
            ((0, 0), (1, 0)), ((0, 1), (1, 1)),
            (1, 0, 0, 1), (0, 0, 1, 1), divisions=1)
        self.assertEqual(len(grad), 3)
        self.assertEqual(grad[0][0], geom.Ray((-1, 0), (0.5, 0)))
        self.assertEqual(grad[0][1], geom.Ray((-1, 0), (0.5, 1)))
        _tuple_eq(self, grad[0].draw_options['facecolor'], (1, 0, 0, 1))
        self.assertEqual(grad[1][0], (0, 0))
        self.assertEqual(grad[1][1], (1.5, 0))
        self.assertEqual(grad[1][2], (1.5, 1))
        self.assertEqual(grad[1][3], (0, 1))
        _tuple_eq(self, grad[1].draw_options['facecolor'], (1/2, 0, 1/2, 1))
        self.assertEqual(grad[2][0], geom.Ray((1, 0), (1, 0)))
        self.assertEqual(grad[2][1], geom.Ray((1, 0), (1, 1)))
        _tuple_eq(self, grad[2].draw_options['facecolor'], (0, 0, 1, 1))

class LatGradRibbonTests(unittest.TestCase):
    def test_lateral_gradient_ribbon(self):
        grad = st.lateral_gradient_ribbon((1, 0), (0, 0), (0, 1),
            (1, 0, 0, 1), (0, 0, 1, 1), divisions=3)
        self.assertEqual(len(grad), 3)
        self.assertEqual(grad[0][0], geom.Line((1, 0), (0, 0)))
        self.assertEqual(grad[0][1], geom.Line((1, 0), (0, 3/6)))
        _tuple_eq(self, grad[0].draw_options['facecolor'], (5/6, 0, 1/6, 1))
        self.assertEqual(grad[1][0], geom.Line((1, 0), (0, 1/3)))
        self.assertEqual(grad[1][1], geom.Line((1, 0), (0, 5/6)))
        _tuple_eq(self, grad[1].draw_options['facecolor'], (3/6, 0, 3/6, 1))
        self.assertEqual(grad[2][0], geom.Line((1, 0), (0, 2/3)))
        self.assertEqual(grad[2][1], geom.Line((1, 0), (0, 1)))
        _tuple_eq(self, grad[2].draw_options['facecolor'], (1/6, 0, 5/6, 1))
