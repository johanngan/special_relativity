import unittest

import specrel.geom as geom
import specrel.spacetime.physical as phy

class GridTests(unittest.TestCase):
    def test_stgrid(self):
        grid = phy.stgrid((-1, 1), (-1, 1))
        self.assertEqual(len(grid), 6)
        self.assertEqual(grid[0], geom.Line((0, 1), (-1, 0)))
        self.assertEqual(grid[1], geom.Line((0, 1), (1, 0)))
        self.assertEqual(grid[2], geom.Line((1, 0), (0, -1)))
        self.assertEqual(grid[3], geom.Line((1, 0), (0, 1)))
        self.assertEqual(grid[4], geom.Line((0, 1), (0, 0)))
        self.assertEqual(grid[5], geom.Line((1, 0), (0, 0)))

class MovingObjectTests(unittest.TestCase):
    def setUp(self):
        self.obj = phy.MovingObject(1, length=1, velocity=0.5)

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
        self.assertFalse(phy.MovingObject(1, 0, 0.5).has_extent())

    def test_velocity(self):
        self.assertEqual(self.obj.velocity(), 0.5)

class TimeIntervalTests(unittest.TestCase):
    def setUp(self):
        self.interval = phy.TimeInterval(1, 1, 0.5)

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
        self.assertFalse(phy.TimeInterval(1, 0, 0.5).has_extent())

    def test_unit_delay(self):
        self.assertEqual(self.interval.unit_delay(), 0.5)
