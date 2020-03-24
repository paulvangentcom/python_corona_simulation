'''
this file contains functions that help initialize the population
parameters for the simulation
'''

from glob import glob
import os

import numpy as np

from motion import get_motion_parameters

def initialize_population(pop_size, mean_age=45, max_age=105,
                          xbounds = [0, 1], ybounds = [0, 1]):
    '''initialized the population for the simulation

    the population matrix for this simulation has the following columns:

    0 : unique ID
    1 : current x coordinate
    2 : current y coordinate
    3 : current heading in x direction
    4 : current heading in y direction
    5 : current speed
    6 : current state (0=healthy, 1=sick, 2=immune, 3=dead)
    7 : age
    8 : infected_since (frame the person got infected)
    9 : recovery vector (used in determining when someone recovers or dies)
    10 : in treatment
    11 : active destination (0 = random wander, 1, .. = destination matrix index)
    12 : at destination: whether arrived at destination (0=traveling, 1=arrived)
    13 : wander_range_x : wander ranges on x axis for those who are confined to a location
    14 : wander_range_y : wander ranges on y axis for those who are confined to a location

    Keyword arguments
    -----------------
    pop_size : int
        the size of the population

    mean_age : int
        the mean age of the population. Age affects mortality chances

    max_age : int
        the max age of the population

    xbounds : 2d array
        lower and upper bounds of x axis

    ybounds : 2d array
        lower and upper bounds of y axis
    '''

    #initialize population matrix
    population = np.zeros((pop_size, 15))

    #initalize unique IDs
    population[:,0] = [x for x in range(pop_size)]

    #initialize random coordinates
    population[:,1] = np.random.uniform(low = xbounds[0] + 0.05, high = xbounds[1] - 0.05, 
                                        size = (pop_size,))
    population[:,2] = np.random.uniform(low = ybounds[0] + 0.05, high = ybounds[1] - 0.05, 
                                        size=(pop_size,))

    #initialize random headings -1 to 1
    population[:,3] = np.random.normal(loc = 0, scale = 1/3, 
                                       size=(pop_size,))
    population[:,4] = np.random.normal(loc = 0, scale = 1/3, 
                                       size=(pop_size,))

    #initialize random speeds
    population[:,5] = np.random.normal(0.01, 0.01/3)

    #initalize ages
    std_age = (max_age - mean_age) / 3
    population[:,7] = np.int32(np.random.normal(loc = mean_age, 
                                                scale = std_age, 
                                                size=(pop_size,)))

    population[:,7] = np.clip(population[:,7], a_min = 0, 
                              a_max = max_age) #clip those younger than 0 years

    #build recovery_vector
    population[:,9] = np.random.normal(loc = 0.5, scale = 0.5 / 3, size=(pop_size,))

    return population


def initialize_destination_matrix(pop_size, total_destinations):
    '''intialized the destination matrix

    '''

    destinations = np.zeros((pop_size, total_destinations * 2))

    return destinations


def set_destination_bounds(population, destinations, xmin, ymin, xmax, ymax,
                           dest_no=1, teleport=True):
    '''teleports all persons within limits

    Function that takes the population and coordinates,
    teleports everyone there, sets destination active and
    destination as reached

    Keyword arguments
    -----------------
    population : ndarray

    '''

    #teleport
    if teleport:
        population[:,1] = np.random.uniform(low = xmin, high = xmax, size = len(population))
        population[:,2] = np.random.uniform(low = ymin, high = ymax, size = len(population))

    #get parameters
    x_center, y_center, x_wander, y_wander = get_motion_parameters(xmin, ymin, xmax, ymax)

    #set destination centers
    destinations[:,(dest_no - 1) * 2] = x_center
    destinations[:,((dest_no - 1) * 2) + 1] = y_center

    #set wander bounds
    population[:,13] = x_wander
    population[:,14] = y_wander

    population[:,11] = dest_no #set destination active
    population[:,12] = 1 #set destination reached

    return population, destinations

def save_data(population, infected, fatalities):
    '''dumps simulation data to disk
    
    ''' 
    num_files = len(glob('data/*'))
    os.makedirs('data/%i' %num_files)
    np.save('data/%i/population.npy' %num_files, population)
    np.save('data/%i/infected.npy' %num_files, infected)
    np.save('data/%i/fatalities.npy' %num_files, fatalities)