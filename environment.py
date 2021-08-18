'''
file that contains all functions to define destinations in the 
environment of the simulated world.
'''

import numpy as np

class environment:
    def __init__(self, xmin, xmax, ymin, ymax, plt, addcross=True):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.plt = plt
        self.addcross = addcross

    def build_hospital(self):
        # plot walls
        self.plt.plot([self.xmin, self.xmin], [self.ymin, self.ymax], color='black')
        self.plt.plot([self.xmax, self.xmax], [self.ymin, self.ymax], color='black')
        self.plt.plot([self.xmin, self.xmax], [self.ymin, self.ymin], color='black')
        self.plt.plot([self.xmin, self.xmax], [self.ymax, self.ymax], color='black')

        # plot red cross
        if self.addcross:
            xmiddle = self.xmin + ((self.xmax - self.xmin) / 2)
            height = np.min([0.3, (self.ymax - self.ymin) / 5])
            self.plt.plot([xmiddle, xmiddle], [self.ymax, self.ymax + height], color='red',
                     linewidth=3)
            self.plt.plot([xmiddle - (height / 2), xmiddle + (height / 2)],
                     [self.ymax + (height / 2), self.ymax + (height / 2)], color='red',
                     linewidth=3)

    def set(self, xmin, xmax, ymin, ymax, plt, addcross):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.plt = plt
        self.addcross = addcross
        build_hospital()
