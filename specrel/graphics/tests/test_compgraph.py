import unittest

import specrel.geom as geom
import specrel.graphics.simpgraph as simpg
import specrel.graphics.compgraph as compg

class MultiTimeAnimatorTests(unittest.TestCase):
    def setUp(self):
        trans = geom.Line((1, 1), (0, 0))
        xlim = (0, 2)
        tlim = (0, 2)
        draw_options = {'tlim': tlim, 'xlim': xlim}
        self.multi = compg.MultiTimeAnimator(
            [
                {
                    'animator': simpg.WorldlineAnimator,
                    'transformable': trans,
                    'draw_options':draw_options,
                },
                {
                    'animator': simpg.ObjectAnimator,
                    'transformable': trans,
                    'draw_options': draw_options,
                }
            ],
            fps=1, ct_per_sec=1, tlim=tlim,
            display_current_time=True, display_current_time_decimals=3)
        self.multi.init_func()

    def tearDown(self):
        self.multi.clear()
        self.multi.close()

    def test_worldline_and_object_animators(self):
        ax1, ax2 = self.multi.axs

        self.multi.update(0)
        ln, tline = ax1.lines
        pt = ax2.lines[0]
        title = self.multi.fig.texts[0]
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 2], [0, 2]])
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 2], [0, 0]])
        self.assertEqual(pt.get_data(), (0, 0))
        self.assertEqual(title.get_text(), 'Time = 0.000 s')

        self.multi.update(1)
        ln, tline = ax1.lines
        pt = ax2.lines[0]
        title = self.multi.fig.texts[0]
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 2], [0, 2]])
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 2], [1, 1]])
        self.assertEqual(pt.get_data(), (1, 0))
        self.assertEqual(title.get_text(), 'Time = 1.000 s')

        self.multi.update(2)
        ln, tline = ax1.lines
        pt = ax2.lines[0]
        title = self.multi.fig.texts[0]
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 2], [0, 2]])
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 2], [2, 2]])
        self.assertEqual(pt.get_data(), (2, 0))
        self.assertEqual(title.get_text(), 'Time = 2.000 s')

class MultiTransformAnimatorTests(unittest.TestCase):
    def setUp(self):
        trans = geom.Line((1, 0), (0, 0))
        xlim = (0, 2)
        tlim = (0, 2)
        time = 1
        anim_opt = {'tlim': tlim, 'xlim': xlim, 'time': time}
        self.multi = compg.MultiTransformAnimator(
            [
                {
                    'animator_options': {
                        'stanimator': simpg.WorldlineAnimator, **anim_opt},
                    'transformable': trans,
                },
                {
                    'animator_options': {
                        'stanimator': simpg.ObjectAnimator, **anim_opt},
                    'transformable': trans,
                },
            ], -4/5, fps=1, transition_duration=2,
            display_current_velocity=True, display_current_velocity_decimals=3)
        self.multi.init_func()

    def tearDown(self):
        self.multi.clear()
        self.multi.close()

    def test_worldline_and_object_animators(self):
        ax1, ax2 = self.multi.axs

        self.multi.update(0)
        ln, tline = ax1.lines
        pt = ax2.lines[0]
        title = self.multi.fig.texts[0]
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 0], [0, 2]])
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 2], [1, 1]])
        self.assertEqual(pt.get_data(), (0, 0))
        self.assertEqual(title.get_text(), '$v = -0.000c$')

        self.multi.update(1)
        ln, tline = ax1.lines
        pt = ax2.lines[0]
        title = self.multi.fig.texts[0]
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 4/5], [0, 2]])
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 2], [1, 1]])
        self.assertEqual(pt.get_data(), (2/5, 0))
        self.assertEqual(title.get_text(), '$v = -0.400c$')

        self.multi.update(2)
        ln, tline = ax1.lines
        pt = ax2.lines[0]
        title = self.multi.fig.texts[0]
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 8/5], [0, 2]])
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 2], [1, 1]])
        self.assertEqual(pt.get_data(), (4/5, 0))
        self.assertEqual(title.get_text(), '$v = -0.800c$')

class RewinderTests(unittest.TestCase):
    def setUp(self):
        trans = geom.Line((1, 1), (0, 0))
        xlim = (0, 3)
        tlim = (0, 3)
        draw_options = {'tlim': tlim, 'xlim': xlim}
        multi = compg.MultiTimeAnimator(
            [
                {
                    'animator': simpg.WorldlineAnimator,
                    'transformable': trans,
                    'draw_options':draw_options,
                },
                {
                    'animator': simpg.ObjectAnimator,
                    'transformable': trans,
                    'draw_options': draw_options,
                }
            ],
            fps=1, ct_per_sec=1, tlim=tlim,
            display_current_time=True, display_current_time_decimals=3,
            title='Title')
        self.rew = compg.Rewinder(multi, end_pause=2)
        self.rew.init_func()

    def test_rewind(self):
        ax1, ax2 = self.rew.animator.axs
        fig = self.rew.animator.fig

        self.assertEqual(self.rew._get_frame_list(), [3, 3, 1, 0, 0])

        self.rew.update(3)
        ln, tline = ax1.lines
        pt = ax2.lines[0]
        title = fig.texts[0]
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 3], [0, 3]])
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 3], [3, 3]])
        self.assertEqual(pt.get_data(), (3, 0))
        self.assertEqual(title.get_text(), 'Title\nTime = 3.000 s')

        self.rew.update(1)
        ln, tline = ax1.lines
        pt = ax2.lines[0]
        title = fig.texts[0]
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 3], [0, 3]])
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 3], [1, 1]])
        self.assertEqual(pt.get_data(), (1, 0))
        self.assertEqual(title.get_text(),
            'Rewinding \u25C0 \u25C0\nTime = 1.000 s')

        self.rew.update(0)
        ln, tline = ax1.lines
        pt = ax2.lines[0]
        title = fig.texts[0]
        self.assertEqual([list(d) for d in ln.get_data()], [[0, 3], [0, 3]])
        self.assertEqual([list(d) for d in tline.get_data()], [[0, 3], [0, 0]])
        self.assertEqual(pt.get_data(), (0, 0))
        self.assertEqual(title.get_text(), 'Title\nTime = 0.000 s')
