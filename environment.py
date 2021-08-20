'''
file that contains all functions to define destinations in the 
environment of the simulated world.
'''

import numpy as np

def build_hospital(xmin, xmax, ymin, ymax, plt, addcross=True):
    '''builds hospital
    
    Defines hospital and returns wall coordinates for 
    the hospital, as well as coordinates for a red cross
    above it
    
    Keyword arguments
    -----------------
    xmin : int or float
        lower boundary on the x axis
        
    xmax : int or float
        upper boundary on the x axis
        
    ymin : int or float
        lower boundary on the y axis
        
    ymax : int or float 
        upper boundary on the y axis
        
    plt : matplotlib.pyplot object
        the plot object to which to append the hospital drawing
        if None, coordinates are returned
        
    Returns
    -------
    None
    '''
    
    #plot walls
    plt.plot([xmin, xmin], [ymin, ymax], color = 'black')
    plt.plot([xmax, xmax], [ymin, ymax], color = 'black')
    plt.plot([xmin, xmax], [ymin, ymin], color = 'black')
    plt.plot([xmin, xmax], [ymax, ymax], color = 'black')

    #plot red cross
    if addcross:
        xmiddle = xmin + ((xmax - xmin) / 2)
        height = np.min([0.3, (ymax - ymin) / 5])
        plt.plot([xmiddle, xmiddle], [ymax, ymax + height], color='red',
                 linewidth = 3)
        plt.plot([xmiddle - (height / 2), xmiddle + (height / 2)],
                 [ymax + (height / 2), ymax + (height / 2)], color='red',
                 linewidth = 3)