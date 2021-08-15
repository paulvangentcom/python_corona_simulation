import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from config import Configuration, config_error
from environment import build_hospital
from infection import find_nearby, infect, recover_or_die, compute_mortality,\
healthcare_infection_correction
from motion import Motion,Human_behavior,COVID_19_behavior
from population import initialize_population, initialize_destination_matrix,\
set_destination_bounds, save_data, save_population, Population_trackers
from visualiser import build_fig, draw_tstep, set_style, plot_sir

#set seed for reproducibility
#np.random.seed(100)

# i'm supposed to make productive changes so this is going to be a
# productive comment. YAY!

class Simulation():
    #TODO: if lockdown or otherwise stopped: destination -1 means no motion
    def __init__(self, *args, **kwargs):
        #load default config data
        self.Config = Configuration(*args, **kwargs)
        self.frame = 0

        #initialize default population
        self.population_init()

        self.pop_tracker = Population_trackers()

        #initalise destinations vector
        self.destinations = initialize_destination_matrix(self.Config.pop_size, 1)

        #initalise human behavior
        human_behavior= Human_behavior()

        #initalise virus behavior
        virus_behavior = COVID_19_behavior()

        #Control all behavior here
        self.motion_control = Motion(human_behavior,virus_behavior)


    def reinitialise(self):
        '''reset the simulation'''

        self.frame = 0
        self.population_init()
        self.pop_tracker = Population_trackers()
        self.destinations = initialize_destination_matrix(self.Config.pop_size, 1)


    def population_init(self):
        '''(re-)initializes population'''
        self.population = initialize_population(self.Config, self.Config.mean_age,
                                                self.Config.max_age, self.Config.xbounds,
                                                self.Config.ybounds)


    def tstep(self):
        '''
        takes a time step in the simulation
        '''

        if self.frame == 0 and self.Config.visualise:
            #initialize figure
            self.fig, self.spec, self.ax1, self.ax2 = build_fig(self.Config)

        self.motion_control.simulation_motion(self.population, self.destinations, \
                                                self.Config, self.pop_tracker, self.frame)

        #send cured back to population if self isolation active
        #perhaps put in recover or die class
        #send cured back to population
        self.population[:,11][self.population[:,6] == 2] = 0

        #update population statistics
        self.pop_tracker.update_counts(self.population)

        #visualise
        if self.Config.visualise:
            draw_tstep(self.Config, self.population, self.pop_tracker, self.frame,
                       self.fig, self.spec, self.ax1, self.ax2)

        #report stuff to console
        sys.stdout.write('\r')
        sys.stdout.write('%i: healthy: %i, infected: %i, immune: %i, in treatment: %i, \
dead: %i, of total: %i' %(self.frame, self.pop_tracker.susceptible[-1], self.pop_tracker.infectious[-1],
                        self.pop_tracker.recovered[-1], len(self.population[self.population[:,10] == 1]),
                        self.pop_tracker.fatalities[-1], self.Config.pop_size))

        #save popdata if required
        if self.Config.save_pop and (self.frame % self.Config.save_pop_freq) == 0:
            save_population(self.population, self.frame, self.Config.save_pop_folder)
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
            print('\ninfecting patient zero')
            self.population[0][6] = 1
            self.population[0][8] = 50
            self.population[0][10] = 1


    def run(self):
        '''run simulation'''

        i = 0

        while i < self.Config.simulation_steps:
            try:
                self.tstep()
            except KeyboardInterrupt:
                print('\nCTRL-C caught, exiting')
                sys.exit(1)

            #check whether to end if no infecious persons remain.
            #check if self.frame is above some threshold to prevent early breaking when simulation
            #starts initially with no infections.
            if self.Config.endif_no_infections and self.frame >= 500:
                if len(self.population[(self.population[:,6] == 1) |
                                       (self.population[:,6] == 4)]) == 0:
                    i = self.Config.simulation_steps

        if self.Config.save_data:
            save_data(self.population, self.pop_tracker)

        #report outcomes
        print('\n-----stopping-----\n')
        print('total timesteps taken: %i' %self.frame)
        print('total dead: %i' %len(self.population[self.population[:,6] == 3]))
        print('total recovered: %i' %len(self.population[self.population[:,6] == 2]))
        print('total infected: %i' %len(self.population[self.population[:,6] == 1]))
        print('total infectious: %i' %len(self.population[(self.population[:,6] == 1) |
                                                          (self.population[:,6] == 4)]))
        print('total unaffected: %i' %len(self.population[self.population[:,6] == 0]))


    def plot_sir(self, size=(6,3), include_fatalities=False,
                 title='S-I-R plot of simulation'):
        plot_sir(self.Config, self.pop_tracker, size, include_fatalities,
                 title)



if __name__ == '__main__':

    #initialize
    sim = Simulation()

    #set number of simulation steps
    sim.Config.simulation_steps = 20000

    #set color mode
    sim.Config.plot_style = 'default' #can also be dark

    #set colorblind mode if needed
    #sim.Config.colorblind_mode = True
    #set colorblind type (default deuteranopia)
    #sim.Config.colorblind_type = 'deuteranopia'

    #set reduced interaction
    #sim.Config.set_reduced_interaction()
    #sim.population_init()

    #set lockdown scenario
    #sim.Config.set_lockdown(lockdown_percentage = 0.1, lockdown_compliance = 0.95)

    #set self-isolation scenario
    #sim.Config.set_self_isolation(self_isolate_proportion = 0.9,
    #                              isolation_bounds = [0.02, 0.02, 0.09, 0.98],
    #                              traveling_infects=False)
    #sim.population_init() #reinitialize population to enforce new roaming bounds

    #run, hold CTRL+C in terminal to end scenario early
    sim.run()
