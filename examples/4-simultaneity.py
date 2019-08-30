#!/usr/bin/env python3
import sys
sys.path.append('..')

import specrel.geom as geom
import specrel.visualize as vis

# Set up "simultaneous events"
xvals = [-0.5, 0, 0.5]
colors = ['red', 'green', 'blue']
points = geom.PointGroup(
    [geom.STVector(0, x, draw_options={'color': c})
        for x, c in zip(xvals, colors)]
)

# Compare spacetime diagrams in different frames
v = 4/5 # Relative velocity between frames
tlim = (-0.75, 0.75)
xlim = (-1, 1)
markersize = 20
title = '"Simultaneous" events in different frames'
plotters = vis.compare_frames(points, v, tlim=tlim, xlim=xlim, title=title,
    markersize=markersize)
p = plotters[0]
p.save('4-simultaneity.png')
p.show()

# Compare the animated scene in different frames
ct_per_sec = 0.5
instant_pause_time = 0.2
anim = vis.compare_frames_animated(points, v,
    tlim=tlim, xlim=xlim,
    ct_per_sec=ct_per_sec,
    instant_pause_time=instant_pause_time,
    title=title,
    markersize=markersize)
anim.save('4-simultaneity_anim.mp4')
anim.show()

# Compare the animated scene in different frames alongside spacetime diagrams
anim = vis.compare_frames_animated_with_worldline(points, v,
    tlim=tlim, xlim=xlim,
    ct_per_sec=ct_per_sec,
    instant_pause_time=instant_pause_time,
    title=title,
    markersize=markersize)
anim.save('4-simultaneity_anim_worldline.mp4')
anim.show()