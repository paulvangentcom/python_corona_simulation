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
set_destination_bounds, save_data, population_trackers
from visualiser import build_fig, draw_tstep

#set seed for reproducibility
np.random.seed(100)

class Simulation():
    #init, run, visualise
    
    #TODO: if lockdown or otherwise stopped: destination -1 means no motion
    def __init__(self, *args, **kwargs):
        #load default config data
        self.Config = Configuration()
        self.frame = 0

        #initialize default population
        self.population = initialize_population(self.Config.pop_size, self.Config.mean_age, 
                                                self.Config.max_age, self.Config.xbounds, 
                                                self.Config.ybounds)

        self.pop_tracker = population_trackers()

        #initalise destinations vector
        self.destinations = initialize_destination_matrix(self.Config.pop_size, 1)

        self.fig, self.spec, self.ax1, self.ax2 = build_fig(self.Config)


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
                self.population[:,5][self.lockdown_vector == 0] = 0
            else:
                #update randoms
                self.population = update_randoms(self.population, self.Config.pop_size, self.Config.speed)
        else:
            #update randoms
            self.population = update_randoms(self.population, self.Config.pop_size, self.Config.speed)


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



def update(frame, population, pop_tracker, destinations, pop_size, infection_range=0.01, 
           infection_chance=0.03, speed=0.01, recovery_duration=(200, 500), mortality_chance=0.02,
           xbounds=[0.02, 0.98], ybounds=[0.02, 0.98], x_plot=[0, 1], 
           y_plot=[0, 1], wander_range=0.05, risk_age=55, 
           critical_age=75, critical_mortality_chance=0.1,
           risk_increase='quadratic', no_treatment_factor=3, 
           treatment_factor=0.5, healthcare_capacity=250, age_dependent_risk=False, 
           treatment_dependent_risk=False, visualise=False, verbose=False,
           self_isolate=True, self_isolate_proportion=0.6, isolation_bounds=[0, 0, 0.1, 0.1],
           traveling_infects=False, lockdown=False, lockdown_percentage=0.1, 
           lockdown_vector=[], plot_style='default'):

    #add one infection to jumpstart
    if frame == 50:
        population[0][6] = 1
        population[0][8] = 50
        population[0][10] = 1


    if visualise:
        #construct plot and visualise
        spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])
        ax1.clear()
        ax2.clear()

        ax1.set_xlim(x_plot[0], x_plot[1])
        ax1.set_ylim(y_plot[0], y_plot[1])

        if self_isolate and isolation_bounds != None:
            build_hospital(isolation_bounds[0], isolation_bounds[2],
                           isolation_bounds[1], isolation_bounds[3], ax1,
                           addcross = False)
        
        #plot population segments
        healthy = population[population[:,6] == 0][:,1:3]
        ax1.scatter(healthy[:,0], healthy[:,1], color='gray', s = 2, label='healthy')
    
        infected = population[population[:,6] == 1][:,1:3]
        ax1.scatter(infected[:,0], infected[:,1], color='red', s = 2, label='infected')

        immune = population[population[:,6] == 2][:,1:3]
        ax1.scatter(immune[:,0], immune[:,1], color='green', s = 2, label='immune')
    
        fatalities = population[population[:,6] == 3][:,1:3]
        ax1.scatter(fatalities[:,0], fatalities[:,1], color='black', s = 2, label='dead')
        
    
        #add text descriptors
        ax1.text(x_plot[0], 
                 y_plot[1] + ((y_plot[1] - y_plot[0]) / 100), 
                 'timestep: %i, total: %i, healthy: %i infected: %i immune: %i fatalities: %i' %(frame,
                                                                                              len(population),
                                                                                              len(healthy), 
                                                                                              len(infected), 
                                                                                              len(immune), 
                                                                                              len(fatalities)),
                 fontsize=6)
    
        ax2.set_title('number of infected')
        ax2.text(0, pop_size * 0.05, 
                 'https://github.com/paulvangentcom/python-corona-simulation',
                 fontsize=6, alpha=0.5)
        #ax2.set_xlim(0, simulation_steps)
        ax2.set_ylim(0, pop_size + 200)

        if treatment_dependent_risk:
            infected_arr = np.asarray(pop_tracker.infectious)
            indices = np.argwhere(infected_arr >= healthcare_capacity)

            ax2.plot([healthcare_capacity for x in range(len(pop_tracker.infectious))], 
                     color='red', label='healthcare capacity')

        if plot_style.lower() == 'default':
            ax2.plot(pop_tracker.infectious, color='gray')
            ax2.plot(pop_tracker.fatalities, color='black', label='fatalities')
        elif plot_style.lower() == 'sir':
            ax2.plot(pop_tracker.infectious, color='gray')
            ax2.plot(pop_tracker.fatalities, color='black', label='fatalities')
            ax2.plot(pop_tracker.susceptible, color='blue', label='susceptible')
            ax2.plot(pop_tracker.recovered, color='green', label='recovered')
        else:
            raise ValueError('incorrect plot_style specified, use \'sir\' or \'default\'')

        if treatment_dependent_risk:
            ax2.plot(indices, infected_arr[infected_arr >= healthcare_capacity], 
                     color='red')

        ax2.legend(loc = 'best', fontsize = 6)
        #plt.savefig('render/%i.png' %frame)

    return population


if __name__ == '__main__':

    tstep = 2000

    sim = Simulation()
    

    for t in range(tstep):
        sim.tstep()
        sys.stdout.write('\r')
        sys.stdout.write('%i / %i' %(t, tstep))
