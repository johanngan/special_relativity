#!/usr/bin/env python3
import sys
sys.path.append('..')

import specrel.geom as geom
import specrel.spacetime as st
import specrel.visualize as vis

# Shared parameters
include_grid = True
include_legend = True
tlim = (0, 2)
xlim = (-2, 2)

# A stationary point object
stationary = st.MovingObject(0, draw_options={'label': '$v = 0$'})
## Alternate:
# direction = (1, 0)
# point = (0, 0)
# stationary = geom.Line(direction, point, draw_options={'label': '$v = 0$'})
title='Stationary object'
p = vis.stplot(stationary, title=title, tlim=tlim, xlim=xlim,
    grid=include_grid, legend=include_legend)
p.save('2-objects_stationary_point.png')
p.show()

# A stationary point object, animated
anim = vis.stanimate(stationary, title=title, tlim=tlim, xlim=xlim,
    grid=include_grid, legend=include_legend)
anim.save('2-objects_stationary_point_anim.mp4')
anim.show()

# A stationary point object, animated with worldline
anim = vis.stanimate_with_worldline(stationary, title=title,
    tlim=tlim, xlim=xlim, grid=include_grid, legend=include_legend,
    legend_loc='upper right')
anim.save('2-objects_stationary_point_anim_worldline.mp4')
anim.show()

# A bunch of moving point objects, animated
moving = st.MovingObject(0, velocity=1/2,
    draw_options={'color': 'red', 'label': '$v = c/2$'})
light = st.MovingObject(0, velocity=1,
    draw_options={'color': 'gold', 'label': '$v = c$'})
ftl = st.MovingObject(0, velocity=3/2,
    draw_options={'color': 'cyan', 'label': '$v = 3c/2$'})
objects = geom.Collection([stationary, moving, light, ftl])
title = 'Various objects'
anim = vis.stanimate_with_worldline(objects, title=title,
    current_time_color='magenta', tlim=tlim, xlim=xlim, grid=include_grid,
    legend=include_legend, legend_loc='upper left')
anim.save('2-objects_moving_points.mp4')
anim.show()

# A moving meterstick
meterstick = st.MovingObject(-1/2, length=1, velocity=1/2,
    draw_options={'label': 'Meterstick'})
# # Alternate:
# direction = (1, 1/2)
# left = geom.Line(direction, (0, -1/2))
# right = geom.Line(direction, (0, 1/2))
# meterstick = geom.Ribbon(left, right, draw_options={'label': 'Meterstick'})
title = 'Moving meterstick ($v = c/2$)'
anim = vis.stanimate_with_worldline(meterstick, title=title,
    tlim=tlim, xlim=xlim, grid=include_grid, legend=include_legend,
    legend_loc='upper left')
anim.save('2-objects_moving_meterstick.mp4')
anim.show()
