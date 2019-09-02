import unittest

import specrel.geom as geom
import specrel.spacetime as st
import specrel.visualize as vis

def _arrays_to_lists(arrarr, precision=7):
    """Get the data of a nested numpy array as a list of lists, rounded to some
    precision.
    """
    return [[round(p, precision) for p in arr] for arr in arrarr]

class VisualizationTests(unittest.TestCase):
    """Set up a scenario to perform tests on."""
    def setUp(self):
        # Set up a scene to visualize
        self.meterstick = st.MovingObject(0, length=3/5, velocity=4/5)
        self.tlim = (0, 2)
        self.xlim = (0, 2.2)
        self.vertices_moving = [[0, 0], [3/5, 0], [2.2, 2], [1.6, 2], [0, 0]]
        self.vertices_rest = [[0, 0], [1, 0], [1, 2], [0, 2], [0, 0]]
        # Over 3 frames of time
        self.fps = 1
        self.ct_per_sec = 1
        self.xdata_moving = [[0, 3/5], [4/5, 7/5], [8/5, 11/5]]
        self.xdata_rest = 3*[[0, 1]]

class VisualizationInertialTests(VisualizationTests):
    """Visualization within inertial frames."""

    def _worldline_anim_tester(self, animator, ax, xydata, nframes):
        """Tester for worldline animators for this scene."""
        poly = ax.patches[0]
        self.assertEqual(_arrays_to_lists(poly.get_xy()), xydata)

        for i in range(nframes):
            animator.update(i)
            ln = ax.lines[-1]
            p = i / (nframes - 1)
            self.assertEqual(_arrays_to_lists(ln.get_data()),
                [list(self.xlim), 2*[(1-p)*self.tlim[0] + p*self.tlim[1]]])

    def _obj_anim_tester(self, animator, ax, xdata):
        """Tester for object animators for this scene."""
        for i, xvals in enumerate(xdata):
            animator.update(i)
            ln = ax.lines[0]
            self.assertEqual(_arrays_to_lists(ln.get_data()), [xvals, [0, 0]])

    def test_stplot(self):
        plotter = vis.stplot(self.meterstick, tlim=self.tlim, xlim=self.xlim)
        poly = plotter.ax.patches[0]
        self.assertEqual(_arrays_to_lists(poly.get_xy()), self.vertices_moving)

    def test_stanimate(self):
        animator = vis.stanimate(self.meterstick, tlim=self.tlim,
            xlim=self.xlim, fps=1, ct_per_sec=1)
        animator.init_func()
        self._obj_anim_tester(animator, animator.ax, self.xdata_moving)

    def test_stanimate_with_worldline(self):
        animator = vis.stanimate_with_worldline(self.meterstick,
            tlim=self.tlim, xlim=self.xlim, fps=self.fps,
            ct_per_sec=self.ct_per_sec)
        animator.init_func()
        self._worldline_anim_tester(animator, animator.axs[0],
            self.vertices_moving, len(self.xdata_moving))
        self._obj_anim_tester(animator, animator.axs[1], self.xdata_moving)

    def test_compare_frames(self):
        plotters = vis.compare_frames(self.meterstick,
            self.meterstick.velocity(), tlim=self.tlim, xlim=self.xlim)
        poly1, poly2 = [p.ax.patches[0] for p in plotters]
        self.assertEqual(_arrays_to_lists(poly1.get_xy()), self.vertices_moving)
        self.assertEqual(_arrays_to_lists(poly2.get_xy()), self.vertices_rest)

    def test_compare_frames_animated(self):
        animator = vis.compare_frames_animated(self.meterstick,
            self.meterstick.velocity(), tlim=self.tlim, xlim=self.xlim,
            fps=self.fps, ct_per_sec=self.ct_per_sec)
        self._obj_anim_tester(animator, animator.axs[0], self.xdata_moving)
        self._obj_anim_tester(animator, animator.axs[1], self.xdata_rest)

    def test_compare_frames_animated_with_worldline(self):
        animator = vis.compare_frames_animated_with_worldline(self.meterstick,
            self.meterstick.velocity(), tlim=self.tlim, xlim=self.xlim,
            fps=self.fps, ct_per_sec=self.ct_per_sec)
        animator.init_func()
        self._worldline_anim_tester(animator, animator.axs[0],
            self.vertices_moving, len(self.xdata_moving))
        self._obj_anim_tester(animator, animator.axs[1], self.xdata_moving)
        self._worldline_anim_tester(animator, animator.axs[2],
            self.vertices_rest, len(self.xdata_rest))
        self._obj_anim_tester(animator, animator.axs[3], self.xdata_rest)

class VisualizationAccelTests(VisualizationTests):
    """Visualization within accelerating frames."""
    def setUp(self):
        super().setUp()
        # Over 3 frames of transformation
        self.transition_duration = 2
        mid_meterstick = geom.lorentz_transformed(self.meterstick, 2/5)
        mid_vel = mid_meterstick.velocity()
        mid_length = mid_meterstick.length()
        # Round
        self.vertices_mid = _arrays_to_lists([
            [0, 0],
            [mid_length, 0],
            [mid_vel*self.tlim[1] + mid_length, self.tlim[1]],
            [mid_vel*self.tlim[1], self.tlim[1]],
            [0, 0]
        ])
        # Round
        self.xdata_mid = [0, round(mid_length, 7)]

    def _worldline_anim_tester(self, animator, ax):
        """Tester for worldline animators for this scene."""
        for i, vertices in enumerate(
            [self.vertices_moving, self.vertices_mid, self.vertices_rest]):
            animator.update(i)
            poly = ax.patches[0]
            self.assertEqual(_arrays_to_lists(poly.get_xy()), vertices)

    def _obj_anim_tester(self, animator, ax):
        """Tester for object animators for this scene."""
        for i, xdata in enumerate(
            [self.xdata_moving[0], self.xdata_mid, self.xdata_rest[0]]):
            animator.update(i)
            ln = ax.lines[0]
            self.assertEqual(_arrays_to_lists(ln.get_data()), [xdata, [0, 0]])

    def test_animate_lt(self):
        animator = vis.animate_lt(self.meterstick, self.meterstick.velocity(),
            tlim=self.tlim, xlim=self.xlim, fps=self.fps,
            transition_duration=self.transition_duration)
        animator.init_func()
        self._worldline_anim_tester(animator, animator.ax)

    def test_animate_lt_realspace(self):
        animator = vis.animate_lt_realspace(self.meterstick,
            self.meterstick.velocity(), xlim=self.xlim, fps=self.fps,
            transition_duration=self.transition_duration)
        animator.init_func()
        self._obj_anim_tester(animator, animator.ax)

    def test_animate_lt_worldline_and_realspace(self):
        animator = vis.animate_lt_worldline_and_realspace(self.meterstick,
            self.meterstick.velocity(), tlim=self.tlim, xlim=self.xlim,
            fps=self.fps, transition_duration=self.transition_duration)
        animator.init_func()
        self._worldline_anim_tester(animator, animator.axs[0])
        self._obj_anim_tester(animator, animator.axs[1])
