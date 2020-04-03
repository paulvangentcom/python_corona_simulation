import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from config import Configuration, config_error
from environment import build_hospital
from infection import find_nearby, infect, recover_or_die, compute_mortality,\
healthcare_infection_correction
from motion import update_positions, out_of_bounds, update_randoms,\
get_motion_parameters
from path_planning import go_to_location, set_destination, check_at_destination,\
keep_at_destination, reset_destinations
from population import initialize_population, initialize_destination_matrix,\
set_destination_bounds, save_data, Population_trackers
from visualiser import build_fig, draw_tstep, set_style

#set seed for reproducibility
#np.random.seed(100)

class Simulation():
    #TODO: if lockdown or otherwise stopped: destination -1 means no motion
    def __init__(self, *args, **kwargs):
        #load default config data
        self.Config = Configuration()
        self.frame = 0

        #initialize default population
        self.population_init()

        self.pop_tracker = Population_trackers()

        #initalise destinations vector
        self.destinations = initialize_destination_matrix(self.Config.pop_size, 1)

        self.fig, self.spec, self.ax1, self.ax2 = build_fig(self.Config)

        #set_style(self.Config)


    def population_init(self):
        '''(re-)initializes population'''
        self.population = initialize_population(self.Config, self.Config.mean_age, 
                                                self.Config.max_age, self.Config.xbounds, 
                                                self.Config.ybounds)

    def tstep(self):
        '''
        takes a time step in the simulation
        '''

        #check destinations if active
        #define motion vectors if destinations active and not everybody is at destination
        active_dests = len(self.population[self.population[:,11] != 0]) # look op this only once

        if active_dests > 0 and len(self.population[self.population[:,12] == 0]) > 0:
            self.population = set_destination(self.population, self.destinations)
            self.population = check_at_destination(self.population, self.destinations, 
                                                   wander_factor = self.Config.wander_factor_dest)

        if active_dests > 0 and len(self.population[self.population[:,12] == 1]) > 0:
            #keep them at destination
            self.population = keep_at_destination(self.population, self.destinations,
                                                  self.Config.wander_factor)

        #out of bounds
        #define bounds arrays, excluding those who are marked as having a custom destination
        if len(self.population[:,11] == 0) > 0:
            _xbounds = np.array([[self.Config.xbounds[0] + 0.02, self.Config.xbounds[1] - 0.02]] * len(self.population[self.population[:,11] == 0]))
            _ybounds = np.array([[self.Config.ybounds[0] + 0.02, self.Config.ybounds[1] - 0.02]] * len(self.population[self.population[:,11] == 0]))
            self.population[self.population[:,11] == 0] = out_of_bounds(self.population[self.population[:,11] == 0], 
                                                                        _xbounds, _ybounds)
        
        #set randoms
        if self.Config.lockdown:
            if len(self.pop_tracker.infectious) == 0:
                mx = 0
            else:
                mx = np.max(self.pop_tracker.infectious)

            if len(self.population[self.population[:,6] == 1]) >= len(self.population) * self.Config.lockdown_percentage or\
               mx >= (len(self.population) * self.Config.lockdown_percentage):
                #reduce speed of all members of society
                self.population[:,5] = np.clip(self.population[:,5], a_min = None, a_max = 0.001)
                #set speeds of complying people to 0
                self.population[:,5][self.Config.lockdown_vector == 0] = 0
            else:
                #update randoms
                self.population = update_randoms(self.population, self.Config)
        else:
            #update randoms
            self.population = update_randoms(self.population, self.Config)

        #for dead ones: set speed and heading to 0
        self.population[:,3:5][self.population[:,6] == 3] = 0
        
        #update positions
        self.population = update_positions(self.population)

        #find new infections
        self.population, self.destinations = infect(self.population, self.Config, self.frame, 
                                                    send_to_location = self.Config.self_isolate, 
                                                    location_bounds = self.Config.isolation_bounds,  
                                                    destinations = self.destinations, 
                                                    location_no = 1, 
                                                    location_odds = self.Config.self_isolate_proportion)

        #recover and die
        self.population = recover_or_die(self.population, self.frame, self.Config)

        #send cured back to population if self isolation active
        #perhaps put in recover or die class
        #send cured back to population
        self.population[:,11][self.population[:,6] == 2] = 0

        #update population statistics
        self.pop_tracker.update_counts(self.population)

        #visualise
        draw_tstep(self.Config, self.population, self.pop_tracker, self.frame, 
                   self.fig, self.spec, self.ax1, self.ax2)
        

        #run callback
        self.callback()

        #update frame
        self.frame += 1


    def callback(self):
        '''placeholder function that can be overwritten.

        By ovewriting this method any custom behaviour can be implemented.
        The method is called after every simulation timestep.
        '''

        if self.frame == 50:
            print('infecting person')
            self.population[0][6] = 1
            self.population[0][8] = 50
            self.population[0][10] = 1


    def run(self):
        for t in range(self.Config.simulation_steps):
            try:
                sim.tstep()
                sys.stdout.write('\r')
                sys.stdout.write('%i / %i' %(t, self.Config.simulation_steps))
            except KeyboardInterrupt:
                print('\nCTRL-C caught, exiting')
                sys.exit(1)

        if self.Config.save_data:
            save_data(self.population, self.pop_tracker)


if __name__ == '__main__':

    #initialize
    sim = Simulation()

    #set number of simulation steps
    sim.Config.simulation_steps = 2000

    #set color mode
    sim.Config.plot_style = 'default' #can also be dark

    #set colorblind mode if needed
    #sim.Config.colorblind_mode = True
    #set colorblind type (default deuteranopia)
    #sim.Config.colorblind_type = 'deuteranopia'

    #set reduced interaction
    sim.Config.set_reduced_interaction()
    sim.population_init()

    #set lockdown scenario
    #sim.Config.set_lockdown(lockdown_percentage = 0.1, lockdown_compliance = 0.95)

    #set self-isolation scenario
    #sim.Config.set_self_isolation(self_isolate_proportion = 0.9,
    #                              isolation_bounds = [0.02, 0.02, 0.09, 0.98],
    #                              traveling_infects=False)
    #sim.population_init() #reinitialize population to enforce new roaming bounds

    #run, hold CTRL+C in terminal to end scenario early
    sim.run()