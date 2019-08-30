#!/usr/bin/env python3
import sys
sys.path.append('..')

import specrel.spacetime as st
import specrel.visualize as vis

# A color changing signal
duration = 3
v = 4/5
# The color change starts at (t = 0, x = 0), and ends at (t = 3, x = 0)
colorchange = st.gradient_line((0, 0), (duration, 0), 'red', 'blue')
# Set the limits with the magic of foresight
tlim = (0, 5/3*duration)
xlim = (-5/3*duration*v, 0.1)
title = 'A gradual color change'
plotters = vis.compare_frames(colorchange, v, tlim=tlim, xlim=xlim,
    title=title, marker='None')
p = plotters[0]
p.save('5-timedilation_full.png')
p.show()

pre = colorchange.pop(0)
post = colorchange.pop()
markersize = 20
anim = vis.compare_frames_animated_with_worldline(colorchange, v,
    tlim=tlim, xlim=xlim, markersize=markersize, title=title,
    current_time_color='cyan')
anim.save('5-timedilation.mp4')
anim.show()

# One seconds in the lab frame
duration = 5
# The two boundary lines have a direction vector (t = 0, x = 1), and the bottom
# and top boundaries pass through (t = 0, x = 0) and (t = 5, x = 0),
# respectively
onesecond = st.lateral_gradient_ribbon((0, 1), (0, 0), (duration, 0),
    'red', 'blue')
onesecond[0].tag = 'Start'
onesecond[-1].tag = 'Finish'
tlim = (0, duration + 0.5)
xlim = (-0.5, 0.5)
anim = vis.compare_frames_animated_with_worldline(onesecond, v,
    tlim=tlim, xlim=xlim, instant_pause_time=0, linewidth=10,
    title='Two clock ticks in different frames', current_time_color='cyan')
anim.save('5-timedilation2.mp4')
anim.show()

# Length contraction of a meterstick
meterstick = st.MovingObject(-0.5, 1)
tlim = (0, 2)
xlim = (-2, 0.5)
meterstick = st.longitudinal_gradient_ribbon(
    [(tlim[0], meterstick.left_pos(tlim[0])),
        (tlim[1], meterstick.left_pos(tlim[1]))],
    [(tlim[0], meterstick.right_pos(tlim[0])),
        (tlim[1], meterstick.right_pos(tlim[1]))],
    'red', 'blue'
)
anim = vis.compare_frames_animated_with_worldline(meterstick, v,
    tlim=tlim, xlim=xlim, title='Meterstick in different frames',
    instant_pause_time=0, linewidth=10, current_time_color='cyan')
anim.save('5-lengthcontraction.mp4')
anim.show()
