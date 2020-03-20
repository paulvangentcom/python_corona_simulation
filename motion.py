'''
file that contains all function related to population mobility
and related computations
'''

import numpy as np

def update_positions(population):
    '''update positions of all people

    Uses heading and speed to update all positions for
    the next time step

    Keyword arguments
    -----------------
    population : ndarray
        the array numpy containing all the population information
    '''

    #update positions
    #x
    population[:,1] = population[:,1] + (population[:,3] * population[:,5])
    #y
    population[:,2] = population[:,2] + (population [:,4] * population[:,5])

    return population


def out_of_bounds(population, xbounds, ybounds):
    '''checks which people are about to go out of bounds and corrects
    
    
    '''
    #update headings and positions where out of bounds
    #update x heading
    #determine number of elements that need to be updated
    shp = population[:,3][(population[:,1] <= xbounds[:,0]) &
                          (population[:,3] < 0)].shape
    population[:,3][(population[:,1] <= xbounds[:,0]) &
                    (population[:,3] < 0)] = np.random.normal(loc = 0.5, 
                                                              scale = 0.5/3,
                                                              size = shp)

    shp = population[:,3][(population[:,1] >= xbounds[:,1]) &
                          (population[:,3] > 0)].shape
    population[:,3][(population[:,1] >= xbounds[:,1]) &
                    (population[:,3] > 0)] = -np.random.normal(loc = 0.5, 
                                                                scale = 0.5/3,
                                                                size = shp)

    #update y heading
    shp = population[:,4][(population[:,2] <= ybounds[:,0]) &
                          (population[:,4] < 0)].shape
    population[:,4][(population[:,2] <= ybounds[:,0]) &
                    (population[:,4] < 0)] = np.random.normal(loc = 0.5, 
                                                              scale = 0.5/3,
                                                              size = shp)

    shp = population[:,4][(population[:,2] >= ybounds[:,1]) &
                          (population[:,4] > 0)].shape
    population[:,4][(population[:,2] >= ybounds[:,1]) &
                    (population[:,4] > 0)] = -np.random.normal(loc = 0.5, 
                                                               scale = 0.5/3,
                                                               size = shp)

    return population


def update_randoms(population, pop_size, heading_update_chance=0.02, 
                   speed_update_chance=0.02):
    '''updates random states such as heading and speed'''

    #randomly update heading
    #x
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,3][update <= heading_update_chance] = np.random.normal(loc = 0, 
                                                       scale = 1/3,
                                                       size = shp)
    #y
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,4][update <= heading_update_chance] = np.random.normal(loc = 0, 
                                                       scale = 1/3,
                                                       size = shp)
    #randomize speeds
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,5][update <= heading_update_chance] = np.random.normal(loc = 0.01, 
                                                       scale = 0.01/3,
                                                       size = shp)    
    return population