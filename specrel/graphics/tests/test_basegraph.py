import unittest

import matplotlib.pyplot as plt
from matplotlib.patches import BoxStyle

import specrel.graphics.basegraph as bgraph

class SingleAxisFigureCreatorTests(unittest.TestCase):
    def test_none_given(self):
        creator = bgraph.SingleAxisFigureCreator()
        self.assertTrue(creator._created_own_fig)
        self.assertIsNotNone(creator.fig)
        self.assertIsNotNone(creator.ax)
    
    def test_fig_given(self):
        fig, ax = plt.subplots()
        creator = bgraph.SingleAxisFigureCreator(fig=fig)
        self.assertIs(creator.fig, fig)
        self.assertIs(creator.ax, ax)
    
    def test_ax_given(self):
        fig, ax = plt.subplots()
        creator = bgraph.SingleAxisFigureCreator(ax=ax)
        self.assertIs(creator.fig, fig)
        self.assertIs(creator.ax, ax)
    
    def test_fig_and_ax_given(self):
        fig, ax = plt.subplots()
        creator = bgraph.SingleAxisFigureCreator(fig=fig, ax=ax)
        self.assertIs(creator.fig, fig)
        self.assertIs(creator.ax, ax)

class WorldlinePlotterTests(unittest.TestCase):
    def setUp(self):
        self.plotter = bgraph.WorldlinePlotter(lim_padding=0.1)
    
    def tearDown(self):
        self.plotter.close()

    def test_draw_point(self):
        self.plotter.draw_point((1, 2), tag='pt')
        pt = self.plotter.ax.lines[0]
        tag = self.plotter.ax.texts[0]
        self.assertEqual(pt.get_data(), (2, 1))
        self.assertEqual(pt.get_linestyle(), 'None')
        self.assertEqual(tag.get_text(), 'pt')
        self.assertEqual(tag._x, 2)
        self.assertEqual(tag._y, 1)
    
    def test_draw_line_segment(self):
        self.plotter.draw_line_segment((1, 2), (3, 4), tag='ln')
        ln = self.plotter.ax.lines[0]
        tag = self.plotter.ax.texts[0]
        tag_box = tag.get_bbox_patch()
        self.assertEqual([list(d) for d in ln.get_data()], [[2, 4], [1, 3]])
        self.assertEqual(ln.get_marker(), 'None')
        self.assertEqual(tag.get_text(), 'ln')
        self.assertEqual(tag._x, 3)
        self.assertEqual(tag._y, 2)
        self.assertEqual(tag.get_ha(), 'center')
        self.assertEqual(tag.get_va(), 'center')
        self.assertIsInstance(tag_box.get_boxstyle(), BoxStyle.Round)
        self.assertEqual(tag_box.get_ec(), (0, 0, 0, 1))
        self.assertEqual(tag_box.get_fc(), (1, 1, 1, 0.5))
    
    def test_draw_shaded_polygon(self):
        self.plotter.draw_shaded_polygon([(0, 0), (0, 1), (1, 0)], tag='poly')
        poly = self.plotter.ax.patches[0]
        tag = self.plotter.ax.texts[0]
        tag_box = tag.get_bbox_patch()
        self.assertEqual([list(xy) for xy in poly.get_xy()],
            [[0, 0], [1, 0], [0, 1], [0, 0]])
        self.assertEqual(tag.get_text(), 'poly')
        self.assertAlmostEqual(tag._x, 1/3)
        self.assertAlmostEqual(tag._y, 1/3)
        self.assertEqual(tag.get_ha(), 'center')
        self.assertEqual(tag.get_va(), 'center')
        self.assertIsInstance(tag_box.get_boxstyle(), BoxStyle.Round)
        self.assertEqual(tag_box.get_ec(), (0, 0, 0, 1))
        self.assertEqual(tag_box.get_fc(), (1, 1, 1, 0.5))

    def test_set_lims(self):
        self.plotter.draw_line_segment((1, 2), (2, 3))
        pt = self.plotter.ax.lines[0]
        self.plotter.set_lims((0, 1), (0, 2))
        self.assertEqual(self.plotter.ax.get_xlim(), (-0.1, 2.1))
        self.assertEqual(self.plotter.ax.get_ylim(), (-0.05, 1.05))
        self.assertEqual(
            [list(xy) for xy in pt.get_clip_path()._patch.get_xy()],
            [[0, 0], [0, 1], [2, 1], [2, 0], [0, 0]])
