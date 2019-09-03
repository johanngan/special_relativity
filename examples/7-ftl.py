#!/usr/bin/env python3
import sys
sys.path.append('..')

import specrel.geom as geom
import specrel.spacetime.physical as phy
import specrel.visualize as vis

# An FTL meterstick
v_ftl = 2
v_frame = 4/5
meterstick = phy.MovingObject(-0.5, 1, velocity=v_ftl)
tlim = (-1, 1)
xlim = (-2, 2)
include_grid = True
anim = vis.animate_lt(meterstick, v_frame, tlim=tlim, xlim=xlim,
    title='FTL meterstick in different frames', grid=include_grid)
anim.save('7-ftl_meterstick.mp4')
anim.show()

# FTL communication
# Set up this system in the "median" frame
tlim = (0.5, 1.9)
xlim = (-1.6, 1.6)
v_away = 1/2
v_message = 4
t_send = 1
person1 = phy.MovingObject(0, velocity=-v_away,
    draw_options={'color': 'red', 'label': 'Person 1', 'markersize': 15})
person2 = phy.MovingObject(0, velocity=v_away,
    draw_options={'color': 'blue', 'label': 'Person 2', 'markersize': 15})
# Extensions of the messages to all time, even though they don't exist for all
# time. The lines are useful for intersection calculations
joke_alltime = phy.MovingObject(person2.center_pos(t_send), start_time=t_send,
    velocity=-v_message)
# Get the left edge of the MovingObject; since it's a point object it's just
# the worldline
joke_sent = joke_alltime.left().intersect(person1.left())
# The actual joke object to draw
joke = geom.Ray((-1, v_message), joke_sent, tag='*Joke*',
    draw_options={'color': 'red', 'linestyle': '--', 'marker': '>'})
# Mark the point of receipt
joke_received = joke.intersect(person2.left())
joke_received.draw_options = {
    'color': 'limegreen',
    'marker': '*',
    'markersize': 10,
    'label': 'Joke received'
}
# Repeat for the response stuff
response_alltime = phy.MovingObject(person1.center_pos(t_send),
    start_time=t_send, velocity=v_message, tag='Hahaha!',
    draw_options={'color': 'blue', 'linestyle': '--', 'marker': '<'})
response_sent = response_alltime.left().intersect(person2.left())
response = geom.Ray((-1, -v_message), response_sent, tag='Hahaha!',
    draw_options={'color': 'blue', 'linestyle': '--', 'marker': '<'})
response_received = response.intersect(person1.left())
response_received.draw_options = {
    'color': 'orange',
    'marker': '*',
    'markersize': 10,
    'label': 'Response received'
}
ftl_convo = geom.Collection([person1, person2, joke, response,
    joke_received, response_received])
# Person 2's perspective
ftl_convo.lorentz_transform(v_away)

anim = vis.stanimate_with_worldline(ftl_convo, tlim=tlim, xlim=xlim,
    title="FTL messages (Person 2's POV)", grid=include_grid, legend=True,
    legend_loc='upper right')
anim.save('7-ftl_person2.mp4')
anim.show()

# Person 1's perspective
ftl_convo.lorentz_transform(-4/5)
anim = vis.stanimate_with_worldline(ftl_convo, tlim=tlim, xlim=xlim,
    title="FTL messages (Person 1's POV)", grid=include_grid, legend=True,
    legend_loc='upper left')
anim.save('7-ftl_person1.mp4')
anim.show()

# Transformation from Person 2 to Person 1
ftl_convo.lorentz_transform(4/5)
anim = vis.animate_lt(ftl_convo, -4/5, tlim=tlim, xlim=xlim,
    title='FTL messages', grid=include_grid, legend=True,
    legend_loc='lower left')
anim.save('7-ftl_messages.mp4')
anim.show()