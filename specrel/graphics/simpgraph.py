"""Core graphics for simple (1 set of axes) spacetime plots and animations in
special relativity"""
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt

"""Something that can create and own a figure"""
class FigureCreator:
    def __init__(self):
        self.fig = None
        self._created_own_fig = False

    def close(self):
        if self._created_own_fig:
            plt.close(self.fig)

"""Something that creates and owns a figure with a single axis
(i.e. not a subplot)"""
class SingleAxisFigureCreator(FigureCreator):
    def __init__(self, fig=None, ax=None):
        super().__init__()
        if fig is None and ax is None:
            self.fig, self.ax = plt.subplots()
            self._created_own_fig = True
        elif fig is not None and ax is None:
            self.fig = fig
            self.ax = fig.gca()
        elif fig is None and ax is not None:
            self.fig = ax.figure
            self.ax = ax
        else:
            self.fig = fig
            self.ax = ax
