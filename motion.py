import numpy as np
from path_planning import go_to_location, set_destination, check_at_destination,\
keep_at_destination, reset_destinations
from motionHelper import out_of_bounds, update_positions, update_randoms

from infection import find_nearby, infect, recover_or_die, compute_mortality,\
healthcare_infection_correction

class Motion:

    #This class is responsible for managing all behavior in the simulator, 
    #including population changes, virus proliferation, etc.


    def __init__(self, sub_motion1,  sub_motion2) -> None:
        # human behavior will init here
        self._human_behavior = sub_motion1
        # virus behavior will init here
        self._virus_behavior = sub_motion2
    
    def simulation_motion(self,population,destinations,Config,pop_tracker, frame):

        #Monitor the basic actions of all people such as moving, out of bounding, or dead.
        self._human_behavior.set_general_rule_motion(population, destinations, Config)

        #special event happen(such as lockdown) and set randoms
        self._human_behavior.special_event(population,destinations,Config,pop_tracker)

        #The spread of the virus and whether humans infected with the virus can heal themselves
        self._virus_behavior.infection(population, destinations, Config, frame)





class Human_behavior:
    '''
    This class aggregates all human behaviors.
    
    TODO: The Judgment based on age whether someone should go to school and work, could 
    design in here.
    '''


    #This function will set basic movement information for the crowd at each frame
    def set_general_rule_motion(self,population, destinations, Config):

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
    def special_event(self,population, destinations,Config,pop_tracker):
              
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


    def update_positions(self, population):
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


class COVID_19_behavior:
    '''
        This class aggregates all virus behaviors.If in the future there are functions 
        based on temperature, vaccines, etc. that can affect the spread of the virus 
        and the lethality, the relevant functions can be defined here
    '''

    #Base infection
    def infection(self, population, destinations, Config, frame):

        #find new infections
        population, destinations = infect(population, Config, frame,
                                                    send_to_location = Config.self_isolate,
                                                    location_bounds = Config.isolation_bounds,
                                                    destinations = destinations,
                                                    location_no = 1,
                                                    location_odds = Config.self_isolate_proportion)
        
        #recover and die
        population = recover_or_die(population, frame, Config)


