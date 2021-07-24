'''
file that contains all functions to define destinations in the 
environment of the simulated world.
'''

import numpy as np
from hospital import Hospital
'''
    This class is used to save all environment change operations, 
    such as adding hospitals, adding residences, etc.
'''
class Environment:
    def __init__(self):
        self.building = []


    def build_hospitals(self,xmin, xmax, ymin, ymax, plt):
        '''builds hospital
    
        Defines hospital and returns wall coordinates for 
        the hospital, as well as coordinates for a red cross
        above it
        
        Keyword arguments
        -----------------
        xmin : int or float
        xmax : int or float
        ymin : int or float
        ymax : int or float
        location showing below:

        (xmin,ymax)----------(xmax,ymax)
            |                   |
            |     Hosipital     |
            |                   |
        (xmin,ymin)----------(xmax,ymin)

        plt : matplotlib.pyplot object
            the plot object to which to append the hospital drawing
            if None, coordinates are returned
            
        Returns
        -------
        None
        '''
        hospital = Hospital(xmin, xmax, ymin, ymax, plt, addcross=True)
        self.building.append(hospital)

    #TODO: Build dormitory or 
    