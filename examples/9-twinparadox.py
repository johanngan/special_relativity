#!/usr/bin/env python3
import sys
sys.path.append('..')

import specrel.geom as geom
import specrel.graphics.compgraph as compg
import specrel.spacetime as st
import specrel.visualize as vis

# Planets
origin = 0
planetdist = 1
x_planet = origin + planetdist
earth = st.MovingObject(origin,
    draw_options={'color': 'blue', 'markersize': 20, 'label': 'Earth'})
planet = st.MovingObject(x_planet,
    draw_options={'color': 'purple', 'markersize': 15, 'label': 'Planet'})

# Rocket
v = 3/5
rocket_forward_alltime = st.MovingObject(origin, velocity=v)
t_turnaround = rocket_forward_alltime.time_for_left_pos(x_planet)
rocket_forward = geom.line_segment((0, 0), (t_turnaround, x_planet),
    draw_options={
        'color': 'cyan',
        'marker': '>',
        'markersize': 5,
        'linestyle': ':',
        'label': 'Traveler (forward)',
    }
)
rocket_backward_alltime = st.MovingObject(origin + 2*planetdist, velocity=-v)
t_return = rocket_backward_alltime.time_for_left_pos(origin)
rocket_backward = geom.line_segment((t_turnaround, x_planet), (t_return, 0),
    draw_options={
        'color': 'darkorange',
        'marker': '<',
        'markersize': 5,
        'linestyle': ':',
        'label': 'Traveler (backward)',
    }
)

# Mark events
turnaround_event = geom.STVector(t_turnaround, x_planet,
    draw_options={
        'color': 'green',
        'marker': '*',
        'markersize': 10,
        'label': 'Turning around',
    }
)
return_event = geom.STVector(t_return, origin,
    draw_options={
        'color': 'red',
        'marker': '*',
        'markersize': 10,
        'label': 'Arrive home',
    }
)

# Collect scene
scene = geom.Collection([
    earth, planet,
    rocket_forward, rocket_backward,
    turnaround_event, return_event,
])

# Plot the scene
tlim = (0, geom.STVector.gamma_factor(v)*t_return)
pad = planetdist/5
xlim = (geom.lorentz_transformed(return_event, v).x - pad,
        geom.lorentz_transformed(return_event, -v).x + pad)

# From Earth's point of view
current_time_color = 'limegreen'
instant_pause_time = 0.5
fps = 100
legend = True
earth_fname = '9-twinparadox_earth.mp4'
anim_earth = vis.stanimate_with_worldline(scene,
    tlim_anim=(0, return_event.t), tlim_worldline=tlim, xlim=xlim,
    legend=legend, legend_loc='upper left', fps=fps,
    title="Twin paradox (Earth's POV)",
    current_time_color=current_time_color,
    instant_pause_time=instant_pause_time)
anim_earth.save(earth_fname)
# Rewind
rew_fname = '9-twinparadox_rewind.mp4'
anim_rew = compg.Rewinder(anim_earth, rewind_rate=5)
anim_rew.save(rew_fname)
# Transformation
lt_fname = '9-twinparadox_transform.mp4'
anim_lt = vis.animate_lt_worldline_and_realspace(scene, v,
    tlim=tlim, xlim=xlim, legend=legend, fps=fps,
    title=f'Transforming frames...',
    current_time_color=current_time_color)
anim_lt.save(lt_fname)

# From the traveler's point of view during the first half of the journey
scene.lorentz_transform(v)
forward_fname = '9-twinparadox_forward.mp4'
anim_forward = vis.stanimate_with_worldline(scene,
    tlim_anim=(0, turnaround_event.t), tlim_worldline=tlim, xlim=xlim,
    legend=legend, legend_loc='upper right', fps=fps,
    title="Twin paradox (traveler's POV)",
    current_time_color=current_time_color,
    instant_pause_time=instant_pause_time)
anim_forward.save(forward_fname)
# Change directions mid-travel. Set the origin to the twin's current point, so
# that it doesn't change mid-acceleration.
dv = geom.lorentz_transformed(rocket_backward_alltime, v).velocity()
# Time value of the turnaround, within the time resolution of a frame
tval = round(turnaround_event.t * fps) / fps
accel_fname = '9-twinparadox_accel.mp4'
anim_accel = vis.animate_lt_worldline_and_realspace(scene, dv,
    origin=turnaround_event, tlim=tlim, xlim=xlim, legend=legend, fps=fps,
    title=f'Changing direction...\nTime = {tval:.3f}',
    current_time_color='limegreen', time=turnaround_event.t,
    display_current_velocity=False)
anim_accel.save(accel_fname)
# From the traveler's point of view during the second half of the journey
scene.lorentz_transform(dv, origin=turnaround_event)
backward_fname = '9-twinparadox_backward.mp4'
anim_backward = vis.stanimate_with_worldline(scene,
    tlim_anim=(turnaround_event.t, return_event.t), tlim_worldline=tlim,
    xlim=xlim, legend=legend, legend_loc='upper left', fps=fps,
    title="Twin paradox (traveler's POV)",
    current_time_color=current_time_color,
    instant_pause_time=instant_pause_time)
anim_backward.save(backward_fname)

# Glue all the parts together
compg.concat_demuxer([earth_fname, rew_fname, lt_fname,
    forward_fname, accel_fname, backward_fname], '9-twinparadox.mp4')

