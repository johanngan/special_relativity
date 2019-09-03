#!/usr/bin/env python3
import sys
sys.path.append('..')

import specrel.graphics.companim as canim
import specrel.geom as geom
import specrel.spacetime as st
import specrel.visualize as vis

# Ladder information
v = 4/5
ladder_left_start = 0
ladder_length = 1
alpha = 0.5 # For transparency
ladder = st.MovingObject(ladder_left_start, ladder_length, v,
    draw_options={'color': (0, 0, 1, alpha), 'label': 'Ladder'})

# Garage information
garage_left_start = 4
garage = st.MovingObject(garage_left_start, ladder_length,
    draw_options={
        'facecolor': (1, 0.5, 0, alpha),
        'edgecolor': 'limegreen',
        'label': 'Garage',
    }
)
# Add a few more frills to the drawing
door_draw_options = {'linestyle': '--', 'marker': '|', 'markersize': 10}
garage[0].draw_options = door_draw_options
garage[1].draw_options = door_draw_options

# Time range
t_start = 0
# End when the ladder totally clears the garage
t_end = ladder.time_for_left_pos(garage.right_pos(0))
# Time when the garage doors are opened/closd
t_transition = ladder.time_for_left_pos(garage.left_pos(0))

# Whole period when each door is closed
closed_draw_options = {'color': 'red', 'marker': '|', 'markersize': 10}
left_closed = geom.Ray((1, 0), (t_transition, garage.left_pos(0)),
    draw_options=closed_draw_options)
right_closed = geom.Ray((-1, 0), (t_transition, garage.right_pos(0)),
    draw_options=closed_draw_options)

# Exact event of closing/opening each door
close_event_draw_options = {
    'color': 'red',
    'marker': 'v',
    'markersize': 10,
    'label': 'Close door',
}
open_event_draw_options = {
    'color': 'limegreen',
    'marker': '^',
    'markersize': 10,
    'label': 'Open door',
}
left_close_event = geom.STVector(t_transition, garage.left_pos(t_transition),
    draw_options=close_event_draw_options)
right_open_event = geom.STVector(t_transition, garage.right_pos(t_transition),
    draw_options=open_event_draw_options)

# Synthesize the scene
scene = geom.Collection([
    garage, ladder,
    left_closed, right_closed,
    left_close_event, right_open_event,
])

tlim = (t_start, t_end)
xlim = (ladder_left_start - ladder_length, ladder.right_pos(t_end))

# Plot the frames
legend = True
p = vis.compare_frames(scene, v, tlim=tlim, xlim=xlim, legend=legend,
    title='The ladder paradox')
p[0].save('8-ladderparadox.png')
p[0].show()

# Animate the lab frame
fps = 50
current_time_color = 'cyan'
lab_fname = '8-ladderparadox_stationary.mp4'
anim_lab = vis.stanimate_with_worldline(scene, tlim=tlim, xlim=xlim,
    fps=fps, legend=True, legend_loc='upper left',
    title='The ladder paradox (stationary POV)',
    current_time_color=current_time_color)
anim_lab.save(lab_fname)
# Animate the ladder frame
ladder_fname = '8-ladderparadox_ladder.mp4'
anim_ladder = vis.stanimate_with_worldline(geom.lorentz_transformed(scene, v),
    tlim=tlim, xlim=xlim, fps=fps, legend=True, legend_loc='upper right',
    title='The ladder paradox (ladder POV)',
    current_time_color=current_time_color)
anim_ladder.save(ladder_fname)
# Animate the transformation
lt_fname = '8-ladderparadox_transform.mp4'
anim_lt = vis.animate_lt_worldline_and_realspace(scene, v,
    tlim=tlim, xlim=xlim, fps=fps, legend=True, title='Transforming frames...',
    current_time_color=current_time_color)
anim_lt.save(lt_fname)
# Animate the rewind from the lab frame
rew_fname = '8-ladderparadox_rewind.mp4'
anim_rew = canim.Rewinder(anim_lab, rewind_rate=5)
anim_rew.save(rew_fname)

# Glue the animations together
canim.concat_demuxer([lab_fname, rew_fname, lt_fname, ladder_fname],
    '8-ladderparadox.mp4')
