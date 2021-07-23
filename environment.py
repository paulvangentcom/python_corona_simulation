'''
file that contains all functions to define destinations in the 
environment of the simulated world.
'''

import numpy as np
class Enviroment:
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
    
    # getter methods
    def getxmin(self):
        return self.xmin
    
    def getxmax(self):
        return self.xmax
    
    def getymin(self):
        return self.ymin
   
    def getymax(self):
        return self.ymax

    def getxmid(self):
        return self.xmin + ((self.xmax - self.xmin) / 2)
    
    def getHeight(self):
        return np.min([0.3, (self.ymax - self.ymin) / 5])
    
    def getxminxmin(self):
        return [self.xmin, self.xmin]
    
    def getxmaxxmax(self):
        return [self.xmax, self.xmax] 
    
    def getxminxmax(self):
        return [self.xmin, self.xmax]  
    
    def getyminymin(self):
        return [self.ymin, self.ymin]

    def getymaxymax(self):
        return [self.ymax, self.ymax]  
    
    def getyminymax(self):
        return [self.ymin, self.ymax]       

    
    
    
    # setter method
    def setxmin(self, newxmin):
        self.xmin = newxmin
    def setxmax(self, newxmax):
        self.xmax = newxmax
    def setymin(self, newymin):
        self.ymin = newymin
    def setymax(self, newymax):
        self.ymax = newymax
    
def build_hospital(env, plt, addcross=True):
    '''builds hospital
    
    Defines hospital and returns wall coordinates for 
    the hospital, as well as coordinates for a red cross
    above it
    
    Keyword arguments
    -----------------
    env : enviroment
        contains the 4 following wall coordinates
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
    plt.plot(env.getxminxmin(), env.getyminymax(), color = 'black')
    plt.plot(env.getxmaxxmax(), env.getyminymax(), color = 'black')
    plt.plot(env.getxminxmax(), env.getyminymin(), color = 'black')
    plt.plot(env.getxminxmax(), env.getxmaxxmax(), color = 'black')

    #plot red cross
    if addcross:
        xmiddle = env.getxmid()
        height = env.getHeight()
        plt.plot([xmiddle, xmiddle], [env.getymax, env.getymax + height], color='red',
                 linewidth = 3)
        plt.plot([xmiddle - (height / 2), xmiddle + (height / 2)],
                 [env.getymax + (height / 2), env.getymax + (height / 2)], color='red',
                 linewidth = 3)
