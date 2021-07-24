import numpy as np
from path_planning import go_to_location, set_destination, check_at_destination,\
keep_at_destination, reset_destinations
from motionHelper import out_of_bounds, update_positions, update_randoms

class Motion:

    #This function will set basic movement information for the crowd at each frame
    def set_general_rule_motion(simul,population, destinations,Config):

        #check destinations if active
        #define motion vectors if destinations active and not everybody is at destination
        active_dests = len(population[population[:,11] != 0]) # look op this only once
        if active_dests > 0:
            if len(population[population[:,12] == 0]) > 0:
                population = set_destination(population, destinations)
                population = check_at_destination(population, destinations,
                                                   wander_factor = Config.wander_factor_dest,
                                                   speed = Config.speed)
            else:
                #keep them at destination
                population = keep_at_destination(population, destinations,
                                                  Config.wander_factor)

        #out of bounds
        #define bounds arrays, excluding those who are marked as having a custom destination  
        if len(population[:,11] == 0) > 0:
            _xbounds = np.array([[Config.xbounds[0] + 0.02, Config.xbounds[1] - 0.02]] * len(population[population[:,11] == 0]))
            _ybounds = np.array([[Config.ybounds[0] + 0.02, Config.ybounds[1] - 0.02]] * len(population[population[:,11] == 0]))
            population[population[:,11] == 0] = out_of_bounds(population[population[:,11] == 0],
                                                                            _xbounds, _ybounds)
            
        #for dead ones: set speed and heading to 0
        population[:,3:5][population[:,6] == 3] = 0
        
    #special event happen  *here we just have lockdown
    def special_event(simul,population, destinations,Config,pop_tracker):
              
        if Config.lockdown:
            if len(pop_tracker.infectious) == 0:
                mx = 0
            else:
                mx = np.max(pop_tracker.infectious)

            if len(population[population[:,6] == 1]) >= len(population) * Config.lockdown_percentage or\
            mx >= (len(population) * Config.lockdown_percentage):
                #reduce speed of all members of society
                population[:,5] = np.clip(population[:,5], a_min = None, a_max = 0.001)
                #set speeds of complying people to 0
                population[:,5][Config.lockdown_vector == 0] = 0
            else:
                #update randoms
                population = update_randoms(population, Config.pop_size, Config.speed)
        else:
            #update randoms
            population = update_randoms(population, Config.pop_size, Config.speed)

        #TODO If the person has other special behaviors, we can add them here

        update_positions(population)


    def update_positions(obj, population):
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


