import unittest

import matplotlib.pyplot as plt

import specrel.geom as geom
import specrel.graphics.simpanim as sanim

class WorldlineAnimatorTests(unittest.TestCase):
    def setUp(self):
        self.animator = sanim.WorldlineAnimator(fps=1, ct_per_sec=1,
            display_current_time=True, display_current_time_decimals=3)
        # Set up a scene
        self.animator.draw_point((0, 0))
        self.animator.draw_line_segment((0, 0), (1, 1))
        self.animator.draw_shaded_polygon([(0, 0), (0, 1), (1, 0)])
        self.animator.set_lims((0, 1), (0, 1))
        self.animator.init_func()
    
    def tearDown(self):
        self.animator.clear()
        self.animator.close()

    def test_init_func(self):
        pt, ln, _ = self.animator.ax.lines
        poly = self.animator.ax.patches[0]
        self.assertEqual(pt.get_data(), (0, 0))
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 1], [0, 1]])
        self.assertEqual([list(xy) for xy in poly.get_xy()],
            [[0, 0], [1, 0], [0, 1], [0, 0]])

    def test_update(self):
        tline = self.animator.ax.lines[-1]
        self.animator.update(0)
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 1], [0, 0]])
        self.assertEqual(self.animator.ax.get_title(), 'Time = 0.000 s')
        self.animator.update(1)
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 1], [1, 1]])

class ObjectAnimatorBasicTests(unittest.TestCase):
    def setUp(self):
        self.animator = sanim.ObjectAnimator(fps=1, ct_per_sec=1)
        # Set up a scene
        self.animator.draw_point((0, 0))
        self.animator.draw_line_segment((0, 0), (1, 1))
        self.animator.draw_shaded_polygon([(0, 0), (0, 1), (1, 0)])
        self.animator.set_lims((0, 1), (0, 1))
        self.animator.init_func()
    
    def tearDown(self):
        self.animator.clear()
        self.animator.close()
    
    def test_init_func(self):
        self.assertEqual(len(self.animator.ax.get_yticks()), 0)
    
    def test_update(self):
        self.animator.update(0)
        pt, ln, poly = self.animator.ax.lines
        self.assertEqual(pt.get_data(), (0, 0))
        self.assertEqual(ln.get_data(), (0, 0))
        self.assertEqual([list(d) for d in poly.get_data()],
            [[0, 1], [0, 0]])

        self.animator.update(1)
        ln, poly = self.animator.ax.lines
        self.assertEqual(ln.get_data(), (1, 0))
        self.assertEqual([list(d) for d in poly.get_data()],
            [[0, 0], [0, 0]])

"""Tests specifically for polygon drawing logic"""
class ObjectAnimatorPolygonTests(unittest.TestCase):
    def setUp(self):
        self.animator = sanim.ObjectAnimator(fps=1, ct_per_sec=0.5)
    
    def tearDown(self):
        self.animator.clear()
        self.animator.close()
    
    def test_simple_convex_polygon(self):
        self.animator.draw_shaded_polygon([(0, 0), (0, 1), (1, 0)])
        self.animator.set_lims((0, 1), (0, 1))
        self.animator.init_func()

        self.animator.update(0)
        poly = self.animator.ax.lines[0]
        self.assertEqual([list(d) for d in poly.get_data()],
            [[0, 1], [0, 0]])

        self.animator.update(1)
        poly = self.animator.ax.lines[0]
        self.assertEqual([list(d) for d in poly.get_data()],
            [[0, 1/2], [0, 0]])
        
        self.animator.update(2)
        poly = self.animator.ax.lines[0]
        self.assertEqual([list(d) for d in poly.get_data()],
            [[0, 0], [0, 0]])

    
    def test_concave_polygon_multiple_segments(self):
        self.animator.draw_shaded_polygon(
            [(0, 0), (1, 1/2), (1/2, 3/4), (1, 1), (1, 0)])
        self.animator.set_lims((0, 1), (0, 1))
        self.animator.init_func()

        self.animator.update(0)
        poly = self.animator.ax.lines[0]
        self.assertEqual([list(d) for d in poly.get_data()],
            [[0, 0], [0, 0]])

        self.animator.update(1)
        poly1, poly2 = self.animator.ax.lines
        self.assertEqual([list(d) for d in poly1.get_data()],
            [[0, 1/4], [0, 0]])
        self.assertEqual([list(d) for d in poly2.get_data()],
            [[3/4, 3/4], [0, 0]])
        
        self.animator.update(2)
        poly1, poly2 = self.animator.ax.lines
        self.assertEqual([list(d) for d in poly1.get_data()],
            [[0, 1/2], [0, 0]])
        self.assertEqual([list(d) for d in poly2.get_data()],
            [[1/2, 1], [0, 0]])

class TransformAnimatorTests(unittest.TestCase):
    def setUp(self):
        self.transformable = geom.STVector(2, 3)
        self.animator = sanim.TransformAnimator(self.transformable, 3/5,
            fps=2, transition_duration=1, display_current_velocity=True,
            display_current_velocity_decimals=3, tlim=(0, 5), xlim=(0, 5))
        self.animator.init_func()
    
    def tearDown(self):
        self.animator.clear()
        self.animator.close()
    
    def test_update(self):
        self.animator.update(0)
        pt = self.animator.ax.lines[0]
        t, x = self.transformable
        self.assertEqual(pt.get_data(), (x, t))

        self.animator.update(1)
        pt = self.animator.ax.lines[0]
        t, x = geom.lorentz_transformed(self.transformable, 3/10)
        self.assertEqual(pt.get_data(), (x, t))

        self.animator.update(2)
        pt = self.animator.ax.lines[0]
        t, x = geom.lorentz_transformed(self.transformable, 3/5)
        self.assertEqual(pt.get_data(), (x, t))
