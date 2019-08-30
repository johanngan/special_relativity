#!/usr/bin/env python3
import sys
sys.path.append('..')

import specrel.geom as geom
import specrel.spacetime as st
import specrel.visualize as vis

tlim = (-5, 5)
xlim = (-5, 5)
# Draw more lines than needed right now; they will appear once we transform
stgrid = st.stgrid([2*t for t in tlim], [2*x for x in xlim])
light_draw_options = {'color': 'gold'}
left_light = st.MovingObject(0, velocity=-1, draw_options=light_draw_options)
right_light = st.MovingObject(0, velocity=1, draw_options=light_draw_options)
grid_with_light = geom.Collection([stgrid, left_light, right_light])

v = 3/5
anim = vis.animate_lt(grid_with_light, v, tlim=tlim, xlim=xlim,
    lim_padding=0, title='The Lorentz transformation')
anim.save('3-lorentztransform.mp4')
anim.show()

# Transform about a different origin
origin = geom.STVector(2, 1, tag='origin',
    draw_options={'marker': '*', 'color': 'limegreen'})
grid_with_light.append(origin)
anim = vis.animate_lt(grid_with_light, v, origin=origin,
    tlim=tlim, xlim=xlim, lim_padding=0,
    title='The Lorentz transformation (about t = 2, x = 1)')
anim.save('3-lorentztransform_origin.mp4')
anim.show()

# Transform specific object by copying
tlim = (0, 2)
xlim = (-2, 2)
meterstick = st.MovingObject(-1/2, length=1, velocity=1/2)
meterstick_copy = geom.lorentz_transformed(meterstick, 1/2)
p = vis.stplot(meterstick_copy, tlim=tlim, xlim=xlim,
    title='Stationary meterstick')
p.save('3-lorentztransform_stationary_meterstick.png')
p.show()

# Transform specific object in place
meterstick.lorentz_transform(4/5)
p = vis.stplot(meterstick, tlim=tlim, xlim=xlim,
    title='Left-moving meterstick')
p.save('3-lorentztransform_reversed_meterstick.png')
p.show()