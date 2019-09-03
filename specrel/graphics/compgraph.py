"""Composite graphics that glue together one or more simple spacetime plots and
animations in special relativity.
"""

from abc import abstractmethod
import copy
import os
import subprocess

import matplotlib.pyplot as plt

from specrel.graphics import graphrc
import specrel.graphics.simpgraph as simpg

class MultiAnimator(simpg.FigureCreator, simpg.BaseAnimator):
    """Runs multiple animations simultaneously on different subplots.

    Args:
        n_animations (int): Number of animations to run simultaneously.
        fig (matplotlib.figure.Figure, optional): Figure window. If `None`, a
            new figure window is created.
        axs (list, optional): List of axes in row major format. If `None`, a
            new set of axes is created under a new figure window.
        others: See `specrel.graphics.simpgraph.BaseAnimator`.

    Attributes:
        axs (list): List of axes to draw on in row major format.
    """
    def __init__(self,
        n_animations,
        fig=graphrc['fig'],
        axs=graphrc['axs'],
        stepsize=None,
        fps=graphrc['anim.fps'],
        display_current=graphrc['anim.display_current'],
        display_current_decimals=
            graphrc['anim.display_current_decimals'],
        title=graphrc['title'],
        frame_lim=(0, 0)):

        simpg.FigureCreator.__init__(self)
        # Make a new figure if necessary
        if fig is None and axs is None:
            # Default to a (1 x n) subplot
            fig, axs = plt.subplots(1, n_animations)
        elif fig is None or axs is None:
            raise ValueError('Must give both figure and axes, or neither.')
        self.axs = axs
        simpg.BaseAnimator.__init__(self, fig, stepsize, fps, display_current,
            display_current_decimals, title, frame_lim)

        # Make sure there's at least one animation
        if n_animations == 0:
            raise ValueError('Number of animations must be nonzero.')
        # Make sure animations and axes match
        if n_animations != len(self.axs):
            raise ValueError('Number of animations and axes must match.')

        # Set up animators
        self._animators = []

        # Text in the suptitle
        self._current_title_text = None
        if self.title:
            self._current_title_text = fig.suptitle(self.title)
        elif self.display_current:
            self._current_title_text = fig.suptitle('')

    def clear(self):
        for anim in self._animators:
            anim.clear()

    def init_func(self):
        return [anim.init_func() for anim in self._animators]

    @abstractmethod
    def _val_text(self, val):
        """Return formatted display text for the given frame value."""
        return ''

    def _update_current_text(self, val):
        """Update the current title text for a given frame value."""
        new_text = ''
        if self.title:
            new_text += self.title + '\n'
        new_text += self._val_text(val)
        self._current_title_text.set_text(new_text)

    def update(self, frame):
        artists = []
        if self.display_current:
            self._update_current_text(self.calc_frame_val(frame))
            artists.append(self._current_title_text)
        else:
            # Still update title every frame in case it changes
            self._current_title_text.set_text(self.title)
        return artists + [anim.update(frame) for anim in self._animators]

    def get_frame_lim(self):
        # Expand the frame lim enough to be able to encompass the frame limits
        # of every animator
        start_frame = None
        frame_lim = super().get_frame_lim()
        if frame_lim[0] is not None:
            start_frame = frame_lim[0]
        else:
            start_frame = min(
                [anim.get_frame_lim()[0] for anim in self._animators])

        end_frame = None
        if frame_lim[1] is not None:
            end_frame = frame_lim[1]
        else:
            end_frame = max(
                [anim.get_frame_lim()[1] for anim in self._animators])

        return (start_frame, end_frame)

"""Runs multiple time-evolution animations simultaneously on different subplots
"""
"""
    animation_params = list of dictionaries containing parameters for animators
        in each subplot, in the following format:
        [
            {
                "animator": <STAnimator constructor>,
                "animator_options":
                {
                    <kwargs except fig, ax, ct_per_sec, instant_pause_time,
                        fps, display_current_time,
                        display_current_time_decimals>
                },
                "transformable": <LorentzTransformable object>,
                "draw_options":
                {
                    <kwargs except plotter>
                }
            }
        ]
    """
class MultiTimeAnimator(MultiAnimator, simpg.TimeAnimator):
    """Runs multiple time-evolution animations simultaneously on different
    subplots.

    Args:
        animations_params (list): List of dictionaries containing parameters for
            animators in each subplot. Each individual dictionary has the
            following items:

            - **animator**: `type`, initializer for the
                `specrel.graphics.simpgraph.STAnimator` to use.
            - **transformable**: `specrel.geom.LorentzTransformable` object to
                animate.
            - **animator_options**: optional, dictionary of certain keyword
                arguments for `animator`, *except* for the following:
                - `fig`
                - `ax`
                - `ct_per_sec`
                - `instant_pause_time`
                - `fps`
                - `display_current_time`
                - `display_current_time_decimals`
            - **draw_options**: optional, dictionary of keyword arguments to
                `specrel.geom.LorentzTransformable.draw`, except for the
                `plotter` argument.

        fig (matplotlib.figure.Figure, optional): See
            `specrel.graphics.compgraph.MultiAnimator`.
        axs (list, optional): See `specrel.graphics.compgraph.MultiAnimator`.
        tlim (tuple, optional): Start and end time of the animation.
        others: See `specrel.graphics.simpgraph.TimeAnimator`.
    """
    def __init__(self,
        animations_params,
        fig=graphrc['fig'],
        axs=graphrc['axs'],
        tlim=(0, 0),
        ct_per_sec=graphrc['anim.time.ct_per_sec'],
        instant_pause_time=graphrc['anim.time.instant_pause_time'],
        fps=graphrc['anim.fps'],
        display_current_time=graphrc['anim.display_current'],
        display_current_time_decimals=
            graphrc['anim.display_current_decimals'],
        title=graphrc['title']):

        simpg.TimeAnimator.__init__(self, fig, ct_per_sec, instant_pause_time,
            fps, display_current_time, display_current_time_decimals)
        frame_lim = (self.calc_frame_idx(tlim[0]), self.calc_frame_idx(tlim[1]))
        MultiAnimator.__init__(self, len(animations_params), fig, axs,
            self.stepsize, fps, display_current_time,
            display_current_time_decimals, title, frame_lim)

        # Set up animators and draw the objects
        for params, ax in zip(animations_params, self.axs):
            # Construct animator
            anim_kwargs = {}
            if 'animator_options' in params:
                anim_kwargs = dict(params['animator_options'])
                for omit in ['fig', 'ax', 'ct_per_sec', 'instant_pause_time',
                    'fps', 'display_current_time',
                    'display_current_time_decimals']:
                    anim_kwargs.pop(omit, None)
            anim = params['animator'](
                fig=self.fig, ax=ax,
                ct_per_sec=ct_per_sec,
                instant_pause_time=instant_pause_time,
                fps=fps,
                display_current_time=False,
                **anim_kwargs)

            # Draw object with animator
            draw_kwargs = {}
            if 'draw_options' in params:
                draw_kwargs = dict(params['draw_options'])
                draw_kwargs.pop('plotter', None)
            params['transformable'].draw(plotter=anim, **draw_kwargs)

            # Add animator to the master list
            self._animators.append(anim)

        # Broaden the frame lists across all animators
        broadened_flim = self.get_frame_lim()
        broadened_tlim = (self.calc_frame_val(broadened_flim[0]),
                          self.calc_frame_val(broadened_flim[1]))
        for anim in self._animators:
            anim.resize(broadened_tlim)

    def _val_text(self, val):
        return f'Time = {{:.{self.display_current_decimals}f}} s'.format(val)

    """Get dict with keys corresponding to frame indexes, and boolean values
    for whether or not any animator has flagged the frame for pause"""
    def _get_frame_pause_flags(self):
        frame_pause_flags = {}
        for anim in self._animators:
            for frame, flag in anim.frame_pause_flags.items():
                if frame not in frame_pause_flags:
                    frame_pause_flags[frame] = False
                # Pause if any animator pauses at a specific frame
                frame_pause_flags[frame] = max(frame_pause_flags[frame], flag)
        return frame_pause_flags

    def _get_frame_list(self):
        # Insert pause frames where necessary
        return [f for f in MultiAnimator._get_frame_list(self)
            for repeat in range(
                self._pause_frames if self._get_frame_pause_flags()[f] else 1)]

class MultiTransformAnimator(MultiAnimator):
    """Runs multiple Lorentz transform animations simultaneously on different
    subplots.

    Args:
        animation_params (list): List of dictionaries containing parameters for
            animators in each subplot. Each individual dictionary has the
            following items:

            - **transformable**: `specrel.geom.LorentzTransformable` object to
                animate.
            - **animator_options**: optional, dictionary of certain keyword
                arguments for `specrel.graphics.simpgraph.TransformAnimator`
                initialization, from the following list:
                - `origin`
                - `stanimator`
                - `stanimator_options`
                - `tlim`
                - `xlim`
                - `time`
                - `title`

        fig (matplotlib.figure.Figure, optional): See
            `specrel.graphics.compgraph.MultiAnimator`.
        axs (list, optional): See `specrel.graphics.compgraph.MultiAnimator`.
        others: See `specrel.graphics.simpgraph.TransformAnimator`.
    """
    def __init__(self,
        animations_params,
        velocity,
        fig=graphrc['fig'],
        axs=graphrc['axs'],
        transition_duration=graphrc['anim.transform.transition_duration'],
        fps=graphrc['anim.fps'],
        display_current_velocity=graphrc['anim.display_current'],
        display_current_velocity_decimals=
            graphrc['anim.display_current_decimals'],
        title=graphrc['title']):

        nsteps = round(transition_duration * fps)
        super().__init__(len(animations_params), fig, axs, velocity / nsteps,
            fps, display_current_velocity, display_current_velocity_decimals,
            title, (0, 0))

        # Set up animators
        for params, ax in zip(animations_params, self.axs):
            # Construct animator
            anim_kwargs = {}
            if 'animator_options' in params:
                anim_kwargs = dict(params['animator_options'])
                for omit in ['lorentz_transformable', 'velocity', 'fig', 'ax',
                    'transition_duration', 'fps', 'display_current_velocity',
                    'display_current_velocity_decimals']:
                    anim_kwargs.pop(omit, None)
            # Add animator to the master list
            self._animators.append(
                simpg.TransformAnimator(
                    copy.deepcopy(params['transformable']),
                    velocity,
                    fig=self.fig,
                    ax=ax,
                    transition_duration=transition_duration,
                    fps=fps,
                    display_current_velocity=False,
                    **anim_kwargs
                )
            )

    def _val_text(self, val):
        return f'$v = {{:.{self.display_current_decimals}f}}c$'.format(val)

class Rewinder(simpg.BaseAnimator):
    """Animates the "rewinding" of an animator's animation.

    Args:
        animator (specrel.graphics.simpgraph.BaseAnimator): Animator to rewind.
        rewind_rate (int, optional): See `rewind_rate` attribute.
        rewind_title (str, optional): Rewind animation title; overrides title of
            the original animation.
        end_pause (float, optional): Pause length in seconds to insert at the
            beginning and end of the rewind animation.

    Attributes:
        animator (specrel.graphics.simpgraph.BaseAnimator): Animator to rewind.
        end_pause_frames (int): Number of pause frame at the beginning and end
            of the rewind animation.
        rewind_rate (int): Speedup factor of the rewind animation relative to
            the original.
    """

    def __init__(self, animator, rewind_rate=2,
        rewind_title='Rewinding \u25C0 \u25C0', end_pause=1):
        super().__init__(animator.fig, animator.stepsize, animator.fps,
            animator.display_current, animator.display_current_decimals,
            rewind_title, animator.get_frame_lim())
        self.animator = animator
        self.rewind_rate = rewind_rate
        self.end_pause_frames = round(end_pause * self.fps)

    def clear(self):
        self._cached_anim = None

    def init_func(self):
        return self.animator.init_func()

    def update(self, frame):
        old_title = self.animator.title
        # Temporarily change the title of the animator if actually rewinding
        frame_lim = self.get_frame_lim()
        if frame != frame_lim[0] and frame != frame_lim[1]:
            self.animator.title = self.title
        artist = self.animator.update(frame)
        self.animator.title = old_title
        return artist

    def _get_frame_list(self):
        # Run through frames backwards, at rewind_rate times the rate of the
        # original
        frame_lim = self.get_frame_lim()
        frame_list = list(range(
            frame_lim[1], frame_lim[0]-1, -self.rewind_rate))
        # Explicitly make sure the starting frame is included
        if frame_lim[0] not in frame_list:
            frame_list.append(frame_lim[0])
        # Pause at the start and end
        # if self.end_pause_frames is 0, -1*[entry] will add an empty list
        frame_list = (self.end_pause_frames - 1)*frame_list[:1] \
            + frame_list + (self.end_pause_frames - 1)*frame_list[-1:]
        return frame_list

def concat_demuxer(input_files, output_file):
    """Concatenate video files.

    Args:
        input_files (list): List of input file names.
        output_file (str): Output file name.
    """
    # Write temporary file list as input for FFmpeg
    tempfilename = 'concat_demuxer_temp_input_file.txt'
    with open(tempfilename, 'w+') as tempfile:
        for i in input_files:
            tempfile.write(f"file '{i}'\n")

    # Concatenate the video files with FFmpeg's concat demuxer
    subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', tempfilename,
        '-c', 'copy', output_file])

    # Delete temporary file list
    try:
        os.remove(tempfilename)
    except OSError as e:
        print(f"[Error] {e.strerror}: '{tempfilename}'")
