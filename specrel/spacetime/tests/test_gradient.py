import unittest

import specrel.geom as geom
import specrel.spacetime.gradient as grad

# Almost equal tuples
def _tuple_eq(testcase, c1, c2):
    for x, y in zip(c1, c2):
        testcase.assertAlmostEqual(x, y)

class GradLineTests(unittest.TestCase):
    def test_gradient_line(self):
        gradln = grad.gradient_line((0, 0), (1, 1), (1, 0, 0, 1), (0, 0, 1, 1),
            divisions=3)
        self.assertEqual(len(gradln), 5)
        self.assertEqual(gradln[0], geom.Ray((-1, -1), (0, 0)))
        _tuple_eq(self, gradln[0].draw_options['color'], (1, 0, 0, 1))
        self.assertEqual(gradln[1][0], (0, 0))
        self.assertEqual(gradln[1][1], (1/3, 1/3))
        _tuple_eq(self, gradln[1].draw_options['color'], (5/6, 0, 1/6, 1))
        self.assertEqual(gradln[2][0], (1/3, 1/3))
        self.assertEqual(gradln[2][1], (2/3, 2/3))
        _tuple_eq(self, gradln[2].draw_options['color'], (3/6, 0, 3/6, 1))
        self.assertEqual(gradln[3][0], (2/3, 2/3))
        self.assertEqual(gradln[3][1], (1, 1))
        _tuple_eq(self, gradln[3].draw_options['color'], (1/6, 0, 5/6, 1))
        self.assertEqual(gradln[4], geom.Ray((1, 1), (1, 1)))
        _tuple_eq(self, gradln[4].draw_options['color'], (0, 0, 1, 1))

    def test_extrapolate_color(self):
        gradln = grad.gradient_line((1/3, 1/3), (2/3, 2/3),
            (2/3, 0, 1/3, 1), (1/3, 0, 2/3, 1), divisions=1)
        self.assertEqual(len(gradln), 5)
        self.assertEqual(gradln[0], geom.Ray((-1, -1), (0, 0)))
        _tuple_eq(self, gradln[0].draw_options['color'], (1, 0, 0, 1))
        self.assertEqual(gradln[1][0], (0, 0))
        self.assertEqual(gradln[1][1], (1/3, 1/3))
        _tuple_eq(self, gradln[1].draw_options['color'], (5/6, 0, 1/6, 1))
        self.assertEqual(gradln[2][0], (1/3, 1/3))
        self.assertEqual(gradln[2][1], (2/3, 2/3))
        _tuple_eq(self, gradln[2].draw_options['color'], (3/6, 0, 3/6, 1))
        self.assertEqual(gradln[3][0], (2/3, 2/3))
        self.assertEqual(gradln[3][1], (1, 1))
        _tuple_eq(self, gradln[3].draw_options['color'], (1/6, 0, 5/6, 1))
        self.assertEqual(gradln[4], geom.Ray((1, 1), (1, 1)))
        _tuple_eq(self, gradln[4].draw_options['color'], (0, 0, 1, 1))

class LongGradRibbonTests(unittest.TestCase):
    def test_longitudinal_gradient_ribbon(self):
        gradribbon = grad.longitudinal_gradient_ribbon(
            ((0, 0), (1, 0)), ((0, 1), (1, 1)),
            (1, 0, 0, 1), (0, 0, 1, 1), divisions=1)
        self.assertEqual(len(gradribbon), 3)
        self.assertEqual(gradribbon[0][0], geom.Ray((-1, 0), (0.5, 0)))
        self.assertEqual(gradribbon[0][1], geom.Ray((-1, 0), (0.5, 1)))
        _tuple_eq(self, gradribbon[0].draw_options['facecolor'], (1, 0, 0, 1))
        self.assertEqual(gradribbon[1][0], (0, 0))
        self.assertEqual(gradribbon[1][1], (1.5, 0))
        self.assertEqual(gradribbon[1][2], (1.5, 1))
        self.assertEqual(gradribbon[1][3], (0, 1))
        _tuple_eq(self, gradribbon[1].draw_options['facecolor'],
            (1/2, 0, 1/2, 1))
        self.assertEqual(gradribbon[2][0], geom.Ray((1, 0), (1, 0)))
        self.assertEqual(gradribbon[2][1], geom.Ray((1, 0), (1, 1)))
        _tuple_eq(self, gradribbon[2].draw_options['facecolor'], (0, 0, 1, 1))

class LatGradRibbonTests(unittest.TestCase):
    def test_lateral_gradient_ribbon(self):
        gradribbon = grad.lateral_gradient_ribbon((1, 0), (0, 0), (0, 1),
            (1, 0, 0, 1), (0, 0, 1, 1), divisions=3)
        self.assertEqual(len(gradribbon), 3)
        self.assertEqual(gradribbon[0][0], geom.Line((1, 0), (0, 0)))
        self.assertEqual(gradribbon[0][1], geom.Line((1, 0), (0, 3/6)))
        _tuple_eq(self, gradribbon[0].draw_options['facecolor'],
            (5/6, 0, 1/6, 1))
        self.assertEqual(gradribbon[1][0], geom.Line((1, 0), (0, 1/3)))
        self.assertEqual(gradribbon[1][1], geom.Line((1, 0), (0, 5/6)))
        _tuple_eq(self, gradribbon[1].draw_options['facecolor'],
            (3/6, 0, 3/6, 1))
        self.assertEqual(gradribbon[2][0], geom.Line((1, 0), (0, 2/3)))
        self.assertEqual(gradribbon[2][1], geom.Line((1, 0), (0, 1)))
        _tuple_eq(self, gradribbon[2].draw_options['facecolor'],
            (1/6, 0, 5/6, 1))
