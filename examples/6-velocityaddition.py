#!/usr/bin/env python3
import sys
sys.path.append('..')

import specrel.geom as geom
import specrel.spacetime as st
import specrel.visualize as vis

# A Lorentz-boosted satellite system
v = 4/5
earth = st.MovingObject(0,
    draw_options={'label': 'Earth', 'color': 'blue'})
rocket = st.MovingObject(0, velocity=v,
    draw_options={'label': 'Rocket', 'color': 'gray'})
satellite = st.MovingObject(0, velocity=v,
    draw_options={'label': 'Satellite', 'color': 'red'})
light = st.MovingObject(0, velocity=1,
    draw_options={'label': 'Light', 'color': 'gold'})
satellite.lorentz_boost(v)
objects = geom.Collection([earth, rocket, satellite, light])

tlim = (0, 1)
xlim = (-1, 1)
anim = vis.compare_frames_animated_with_worldline(objects, v, tlim=tlim,
    xlim=xlim, title='Relativistic addition of velocities',
    legend=True, legend_loc='lower left')
anim.save('6-velocityaddition.mp4')
anim.show()

# Animating the boost as it happens
objects.lorentz_transform(v)
anim = vis.animate_lt_worldline_and_realspace(objects, -v,
    tlim=tlim, xlim=xlim, title='Lorentz boosting',
    legend=True, legend_loc='lower left', time=tlim[1])
anim.save('6-velocityaddition_boost.mp4')
anim.show()
