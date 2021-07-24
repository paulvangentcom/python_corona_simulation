import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.animation import FuncAnimation

from config import Configuration, config_error
from infection import infect, recover_or_die, compute_mortality,\
healthcare_infection_correction
from motion import update_positions, out_of_bounds, update_randoms,\
get_motion_parameters
from path_planning import go_to_location, set_destination, check_at_destination,\
keep_at_destination, reset_destinations
from population import initialize_population, initialize_destination_matrix,\
set_destination_bounds, save_data, save_population, Population_trackers
from utils import check_folder
from finder import find_nearby

#set seed for reproducibility
#np.random.seed(100)

class Environment():
    '''
    file that contains all functions to define destinations in the
    environment of the simulated world.
    '''

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

class Visualiser():
    '''
    contains all methods for visualisation tasks
    '''

    def set_style(Config):
        '''sets the plot style

        '''
        if Config.plot_style.lower() == 'dark':
            mpl.style.use('plot_styles/dark.mplstyle')


    def build_fig(Config, figsize=(5,7)):
        set_style(Config)
        fig = plt.figure(figsize=(5,7))
        spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])

        ax1 = fig.add_subplot(spec[0,0])
        plt.title('infection simulation')
        plt.xlim(Config.xbounds[0], Config.xbounds[1])
        plt.ylim(Config.ybounds[0], Config.ybounds[1])

        ax2 = fig.add_subplot(spec[1,0])
        ax2.set_title('number of infected')
        #ax2.set_xlim(0, simulation_steps)
        ax2.set_ylim(0, Config.pop_size + 100)

        #if

        return fig, spec, ax1, ax2


    def draw_tstep(Config, population, pop_tracker, frame,
                   fig, spec, ax1, ax2):
        #construct plot and visualise

        #set plot style
        set_style(Config)

        #get color palettes
        palette = Config.get_palette()

        spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])
        ax1.clear()
        ax2.clear()

        ax1.set_xlim(Config.x_plot[0], Config.x_plot[1])
        ax1.set_ylim(Config.y_plot[0], Config.y_plot[1])

        if Config.self_isolate and Config.isolation_bounds != None:
            build_hospital(Config.isolation_bounds[0], Config.isolation_bounds[2],
                           Config.isolation_bounds[1], Config.isolation_bounds[3], ax1,
                           addcross = False)

        #plot population segments
        healthy = population[population[:,6] == 0][:,1:3]
        ax1.scatter(healthy[:,0], healthy[:,1], color=palette[0], s = 2, label='healthy')

        infected = population[population[:,6] == 1][:,1:3]
        ax1.scatter(infected[:,0], infected[:,1], color=palette[1], s = 2, label='infected')

        immune = population[population[:,6] == 2][:,1:3]
        ax1.scatter(immune[:,0], immune[:,1], color=palette[2], s = 2, label='immune')

        fatalities = population[population[:,6] == 3][:,1:3]
        ax1.scatter(fatalities[:,0], fatalities[:,1], color=palette[3], s = 2, label='dead')


        #add text descriptors
        ax1.text(Config.x_plot[0],
                 Config.y_plot[1] + ((Config.y_plot[1] - Config.y_plot[0]) / 100),
                 'timestep: %i, total: %i, healthy: %i infected: %i immune: %i fatalities: %i' %(frame,
                                                                                                 len(population),
                                                                                                 len(healthy),
                                                                                                 len(infected),
                                                                                                 len(immune),
                                                                                                 len(fatalities)),
                    fontsize=6)

        ax2.set_title('number of infected')
        ax2.text(0, Config.pop_size * 0.05,
                    'https://github.com/paulvangentcom/python-corona-simulation',
                    fontsize=6, alpha=0.5)
        #ax2.set_xlim(0, simulation_steps)
        ax2.set_ylim(0, Config.pop_size + 200)

        if Config.treatment_dependent_risk:
            infected_arr = np.asarray(pop_tracker.infectious)
            indices = np.argwhere(infected_arr >= Config.healthcare_capacity)

            ax2.plot([Config.healthcare_capacity for x in range(len(pop_tracker.infectious))],
                     'r:', label='healthcare capacity')

        if Config.plot_mode.lower() == 'default':
            ax2.plot(pop_tracker.infectious, color=palette[1])
            ax2.plot(pop_tracker.fatalities, color=palette[3], label='fatalities')
        elif Config.plot_mode.lower() == 'sir':
            ax2.plot(pop_tracker.susceptible, color=palette[0], label='susceptible')
            ax2.plot(pop_tracker.infectious, color=palette[1], label='infectious')
            ax2.plot(pop_tracker.recovered, color=palette[2], label='recovered')
            ax2.plot(pop_tracker.fatalities, color=palette[3], label='fatalities')
        else:
            raise ValueError('incorrect plot_style specified, use \'sir\' or \'default\'')

        ax2.legend(loc = 'best', fontsize = 6)

        plt.draw()
        plt.pause(0.0001)

        if Config.save_plot:
            try:
                plt.savefig('%s/%i.png' %(Config.plot_path, frame))
            except:
                check_folder(Config.plot_path)
                plt.savefig('%s/%i.png' %(Config.plot_path, frame))


    def plot_sir(Config, pop_tracker, size=(6,3), include_fatalities=False,
                 title='S-I-R plot of simulation'):
        '''plots S-I-R parameters in the population tracker

        Keyword arguments
        -----------------
        Config : class
            the configuration class

        pop_tracker : ndarray
            the population tracker, containing

        size : tuple
            size at which the plot will be initialised (default: (6,3))

        include_fatalities : bool
            whether to plot the fatalities as well (default: False)
        '''

        #set plot style
        set_style(Config)

        #get color palettes
        palette = Config.get_palette()

        #plot the thing
        plt.figure(figsize=size)
        plt.title(title)
        plt.plot(pop_tracker.susceptible, color=palette[0], label='susceptible')
        plt.plot(pop_tracker.infectious, color=palette[1], label='infectious')
        plt.plot(pop_tracker.recovered, color=palette[2], label='recovered')
        if include_fatalities:
            plt.plot(pop_tracker.fatalities, color=palette[3], label='fatalities')

        #add axis labels
        plt.xlabel('time in hours')
        plt.ylabel('population')

        #add legend
        plt.legend()

        #beautify
        plt.tight_layout()

        #initialise
        plt.show()

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

        #check destinations if active
        #define motion vectors if destinations active and not everybody is at destination
        active_dests = len(self.population[self.population[:,11] != 0]) # look op this only once

        if active_dests > 0 and len(self.population[self.population[:,12] == 0]) > 0:
            self.population = set_destination(self.population, self.destinations)
            self.population = check_at_destination(self.population, self.destinations,
                                                   wander_factor = self.Config.wander_factor_dest,
                                                   speed = self.Config.speed)

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
