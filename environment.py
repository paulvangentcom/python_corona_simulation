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
        
        
def load_province_data(names=['noordholland']):
    '''returns the polygons defining individual provinces
    
    Function that returns polygons for each province in a dict object
    
    Keyword arguments
    -----------------
    names : list
        list containing province names to load, without spaces.
    
    Returns
    -------
    provinces : dict
        keyed dictionary object, containing provinces
        
    '''
    provinces = {}
    
    for name in names:
        provinces[name] = np.genfromtxt('source_data/%s.csv' %name, delimiter = ',', 
                                        skip_header = 1)
        
    return provinces


def build_country(provinces, province_origins={}):
    '''takes province coordinates and builds country
    
    All province coordinates are normalised 0-1, this function
    takes all the coordinate arrays and correctly constructs the Netherlands
    from them. Returns all provinces in separate arrays 
    
    Keyword arguments
    -----------------
    provinces : dict
        dict object containing provinces, as returned by load_province_data function
        
    province_origins : dict
        keyed dict of centers for each province, determines where to place them.
        keys need to be the same as for provinces
    
    Returns
    -------
    country : dict
        dict object containing all provinces with revised coordinates
    '''
    
    country = {}
    province_origins['noordholland'] = [0, 0]
    
    #load province data
    for province in provinces:
        prov = np.copy(provinces[province])
        
        prov[:,0] += province_origins[province][0]
        prov[:,1] += province_origins[province][1]
        #place province based on center
        
        country[province] = np.copy(prov)
    
    return country