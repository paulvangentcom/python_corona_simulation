'''
contains methods related to goal-directed traveling behaviour 
and path planning
'''

import numpy as np

from motion import get_motion_parameters, update_randoms

def go_to_location(patient, destination, location_bounds, dest_no=1):
    '''sends patient to defined location

    Function that takes a patient an destination, and sets the location
    as active for that patient.

    Keyword arguments
    -----------------
    patient : 1d array
        1d array of the patient data, is a row from population matrix

    destination : 1d array
        1d array of the destination data, is a row from destination matrix

    location_bounds : list or tuple
        defines bounds for the location the patient will be roam in when sent
        there. format: [xmin, ymin, xmax, ymax]

    dest_no : int
        the location number, used as index for destinations array if multiple possible
        destinations are defined`.


    TODO: vectorize

    '''

    x_center, y_center, x_wander, y_wander = get_motion_parameters(location_bounds[0],
                                                                    location_bounds[1],
                                                                    location_bounds[2],
                                                                    location_bounds[3])
    patient[13] = x_wander
    patient[14] = y_wander
    
    destination[(dest_no - 1) * 2] = x_center
    destination[((dest_no - 1) * 2) + 1] = y_center

    patient[11] = dest_no #set destination active

    return patient, destination


def set_destination(population, destinations):
    '''sets destination of population

    Sets the destination of population if destination marker is not 0.
    Updates headings and speeds as well.

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information

    destinations : ndarray
        the array containing all destinations information
    '''
    
    #how many destinations are active
    active_dests = np.unique(population[:,11][population[:,11] != 0])

    #set destination
    for d in active_dests:
        dest_x = destinations[:,int((d - 1) * 2)]
        dest_y = destinations[:,int(((d - 1) * 2) + 1)]

        #compute new headings
        head_x = dest_x - population[:,1]
        head_y = dest_y - population[:,2]

        #head_x = head_x / np.sqrt(head_x)
        #head_y = head_y / np.sqrt(head_y)

        #reinsert headings into population of those not at destination yet
        population[:,3][(population[:,11] == d) &
                        (population[:,12] == 0)] = head_x[(population[:,11] == d) &
                                                            (population[:,12] == 0)]
        population[:,4][(population[:,11] == d) &
                        (population[:,12] == 0)] = head_y[(population[:,11] == d) &
                                                            (population[:,12] == 0)]
        #set speed to 0.01
        population[:,5][(population[:,11] == d) &
                        (population[:,12] == 0)] = 0.02

    return population


def check_at_destination(population, destinations, wander_factor=1.5, speed = 0.01):
    '''check who is at their destination already

    Takes subset of population with active destination and
    tests who is at the required coordinates. Updates at destination
    column for people at destination.    

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information

    destinations : ndarray
        the array containing all destinations information

    wander_factor : int or float
        defines how far outside of 'wander range' the destination reached
        is triggered
    '''

    #how many destinations are active
    active_dests = np.unique(population[:,11][(population[:,11] != 0)])

    #see who is at destination
    for d in active_dests:
        dest_x = destinations[:,int((d - 1) * 2)]
        dest_y = destinations[:,int(((d - 1) * 2) + 1)]

        #see who arrived at destination and filter out who already was there
        at_dest = population[(np.abs(population[:,1] - dest_x) < (population[:,13] * wander_factor)) & 
                                (np.abs(population[:,2] - dest_y) < (population[:,14] * wander_factor)) &
                                (population[:,12] == 0)]

        if len(at_dest) > 0:
            #mark those as arrived
            at_dest[:,12] = 1
            #insert random headings and speeds for those at destination
            at_dest = update_randoms(at_dest, pop_size = len(at_dest), speed = speed,
                                     heading_update_chance = 1, speed_update_chance = 1)

            #at_dest[:,5] = 0.001

            #reinsert into population
            population[(np.abs(population[:,1] - dest_x) < (population[:,13] * wander_factor)) & 
                        (np.abs(population[:,2] - dest_y) < (population[:,14] * wander_factor)) &
                        (population[:,12] == 0)] = at_dest


    return population
        

def keep_at_destination(population, destinations, wander_factor=1):
    '''keeps those who have arrived, within wander range

    Function that keeps those who have been marked as arrived at their
    destination within their respective wander ranges

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information

    destinations : ndarray
        the array containing all destinations information

    wander_factor : int or float
        defines how far outside of 'wander range' the destination reached
        is triggered
    ''' 

    #how many destinations are active
    active_dests = np.unique(population[:,11][(population[:,11] != 0) &
                                                (population[:,12] == 1)])

    for d in active_dests:
        dest_x = destinations[:,int((d - 1) * 2)][(population[:,12] == 1) &
                                                    (population[:,11] == d)]
        dest_y = destinations[:,int(((d - 1) * 2) + 1)][(population[:,12] == 1) &
                                                        (population[:,11] == d)]

        #see who is marked as arrived
        arrived = population[(population[:,12] == 1) &
                                (population[:,11] == d)]

        ids = np.int32(arrived[:,0]) # find unique IDs of arrived persons
        
        #check if there are those out of bounds
        #replace x oob
        #where x larger than destination + wander, AND heading wrong way, set heading negative
        shp = arrived[:,3][arrived[:,1] > (dest_x + (arrived[:,13] * wander_factor))].shape

        arrived[:,3][arrived[:,1] > (dest_x + (arrived[:,13] * wander_factor))] = -np.random.normal(loc = 0.5,
                                                                scale = 0.5 / 3,
                                                                size = shp)


        #where x smaller than destination - wander, set heading positive
        shp = arrived[:,3][arrived[:,1] < (dest_x - (arrived[:,13] * wander_factor))].shape
        arrived[:,3][arrived[:,1] < (dest_x - (arrived[:,13] * wander_factor))] = np.random.normal(loc = 0.5,
                                                            scale = 0.5 / 3,
                                                            size = shp)
        #where y larger than destination + wander, set heading negative
        shp = arrived[:,4][arrived[:,2] > (dest_y + (arrived[:,14] * wander_factor))].shape
        arrived[:,4][arrived[:,2] > (dest_y + (arrived[:,14] * wander_factor))] = -np.random.normal(loc = 0.5,
                                                                scale = 0.5 / 3,
                                                                size = shp)
        #where y smaller than destination - wander, set heading positive
        shp = arrived[:,4][arrived[:,2] < (dest_y - (arrived[:,14] * wander_factor))].shape
        arrived[:,4][arrived[:,2] < (dest_y - (arrived[:,14] * wander_factor))] = np.random.normal(loc = 0.5,
                                                            scale = 0.5 / 3,
                                                            size = shp)

        #slow speed
        arrived[:,5] = np.random.normal(loc = 0.005,
                                        scale = 0.005 / 3, 
                                        size = arrived[:,5].shape)

        #reinsert into population
        population[(population[:,12] == 1) &
                    (population[:,11] == d)] = arrived
                                
    return population


def reset_destinations(population, ids=[]):
    '''clears destination markers

    Function that clears all active destination markers from the population

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information

    ids : ndarray or list
        array containing the id's of the population members that need their
        destinations reset
    '''
    
    
    if len(ids) == 0:
        #if ids empty, reset everyone
        population[:,11] = 0
    else:
        pass
        #else, reset id's

    
    pass


def update_positions(population):
    '''update positions of all people

    Uses heading and speed to update all positions for
    the next time step

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information
    '''

    #update positions
    #x
    population[:,1] = population[:,1] + (population[:,3] * population[:,5])
    #y
    population[:,2] = population[:,2] + (population [:,4] * population[:,5])

    return population


def out_of_bounds(population, xbounds, ybounds):
    '''checks which people are about to go out of bounds and corrects

    Function that updates headings of individuals that are about to 
    go outside of the world boundaries.
    
    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information

    xbounds, ybounds : list or tuple
        contains the lower and upper bounds of the world [min, max]
    '''
    #update headings and positions where out of bounds
    #update x heading
    #determine number of elements that need to be updated

    shp = population[:,3][(population[:,1] <= xbounds[:,0]) &
                            (population[:,3] < 0)].shape
    population[:,3][(population[:,1] <= xbounds[:,0]) &
                    (population[:,3] < 0)] = np.clip(np.random.normal(loc = 0.5, 
                                                                        scale = 0.5/3,
                                                                        size = shp),
                                                        a_min = 0.05, a_max = 1)

    shp = population[:,3][(population[:,1] >= xbounds[:,1]) &
                            (population[:,3] > 0)].shape
    population[:,3][(population[:,1] >= xbounds[:,1]) &
                    (population[:,3] > 0)] = np.clip(-np.random.normal(loc = 0.5, 
                                                                        scale = 0.5/3,
                                                                        size = shp),
                                                        a_min = -1, a_max = -0.05)

    #update y heading
    shp = population[:,4][(population[:,2] <= ybounds[:,0]) &
                            (population[:,4] < 0)].shape
    population[:,4][(population[:,2] <= ybounds[:,0]) &
                    (population[:,4] < 0)] = np.clip(np.random.normal(loc = 0.5, 
                                                                        scale = 0.5/3,
                                                                        size = shp),
                                                        a_min = 0.05, a_max = 1)

    shp = population[:,4][(population[:,2] >= ybounds[:,1]) &
                            (population[:,4] > 0)].shape
    population[:,4][(population[:,2] >= ybounds[:,1]) &
                    (population[:,4] > 0)] = np.clip(-np.random.normal(loc = 0.5, 
                                                                        scale = 0.5/3,
                                                                        size = shp),
                                                        a_min = -1, a_max = -0.05)

    return population


def update_randoms(population, pop_size, speed=0.01, heading_update_chance=0.02, 
                   speed_update_chance=0.02, heading_multiplication=1,
                   speed_multiplication=1):
    '''updates random states such as heading and speed
    
    Function that randomized the headings and speeds for population members
    with settable odds.

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information
    
    pop_size : int
        the size of the population

    heading_update_chance : float
        the odds of updating the heading of each member, each time step

    speed_update_chance : float
        the oodds of updating the speed of each member, each time step

    heading_multiplication : int or float
        factor to multiply heading with (default headings are between -1 and 1)

    speed_multiplication : int or float
        factor to multiply speed with (default speeds are between 0.0001 and 0.05

    speed : int or float
        mean speed of population members, speeds will be taken from gaussian distribution
        with mean 'speed' and sd 'speed / 3'
    '''

    #randomly update heading
    #x
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,3][update <= heading_update_chance] = np.random.normal(loc = 0, 
                                                        scale = 1/3,
                                                        size = shp) * heading_multiplication
    #y
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,4][update <= heading_update_chance] = np.random.normal(loc = 0, 
                                                        scale = 1/3,
                                                        size = shp) * heading_multiplication
    #randomize speeds
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,5][update <= heading_update_chance] = np.random.normal(loc = speed, 
                                                        scale = speed / 3,
                                                        size = shp) * speed_multiplication

    population[:,5] = np.clip(population[:,5], a_min=0.0001, a_max=0.05)
    return population


def get_motion_parameters(xmin, ymin, xmax, ymax):
    '''gets destination center and wander ranges

    Function that returns geometric parameters of the destination
    that the population members have set.

    Keyword arguments:
    ------------------
        xmin, ymin, xmax, ymax : int or float
        lower and upper bounds of the destination area set.

    '''

    x_center = xmin + ((xmax - xmin) / 2)
    y_center = ymin + ((ymax - ymin) / 2)

    x_wander = (xmax - xmin) / 2
    y_wander = (ymax - ymin) / 2

    return x_center, y_center, x_wander, y_wander