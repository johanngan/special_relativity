#!/usr/bin/env python3
import sys
sys.path.append('..')

import specrel.geom as geom
import specrel.spacetime as st
import specrel.visualize as vis

# Plot a spacetime grid
tlim = (-5, 5)
xlim = (-5, 5)
stgrid = st.stgrid(tlim, xlim)
plotter = vis.stplot(stgrid,
    title='Spacetime diagram\n(Also known as "Minkowski" or "Worldline" diagram)',
    lim_padding=0)
plotter.save('1-spacetime_grid.png')
plotter.show()

# Plot a spacetime event
tlim = (0, 2)
xlim = (-2, 2)
event = geom.STVector(1, 1, draw_options={'label': 'Event'})
p = vis.stplot(event, title='An event in spacetime',
    tlim=tlim, xlim=xlim, grid=True, legend=True)
p.save('1-spacetime_event.png')
p.show()