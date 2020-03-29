import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from environment import build_hospital
from infection import infect, recover_or_die, compute_mortality
from motion import update_positions, out_of_bounds, update_randoms,\
set_destination, check_at_destination, keep_at_destination, get_motion_parameters
from population import initialize_population, initialize_destination_matrix,\
set_destination_bounds, save_data

#set seed for reproducibility
np.random.seed(100)

def update(frame, population, destinations, pop_size, infection_range=0.01, 
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
        population[0][8] = 75
        population[0][10] = 1

    #define motion vectors if destinations active and not everybody is at destination
    active_dests = len(population[population[:,11] != 0]) # look op this only once

    if active_dests > 0 and len(population[population[:,12] == 0]) > 0:
        population = set_destination(population, destinations)
        population = check_at_destination(population, destinations, wander_factor = 1.5)

    if active_dests > 0 and len(population[population[:,12] == 1]) > 0:
        #keep them at destination
        population = keep_at_destination(population, destinations,
                                         wander_factor = 1)

    #update out of bounds
    #define bounds arrays, excluding those who are marked as having a custom destination
    if len(population[:,11] == 0) > 0:
        _xbounds = np.array([[xbounds[0] + 0.02, xbounds[1] - 0.02]] * len(population[population[:,11] == 0]))
        _ybounds = np.array([[ybounds[0] + 0.02, ybounds[1] - 0.02]] * len(population[population[:,11] == 0]))
        population[population[:,11] == 0] = out_of_bounds(population[population[:,11] == 0], 
                                                          _xbounds, _ybounds)

    
    if lockdown:
        if len(infected_plot) == 0:
            mx = 0
        else:
            mx = np.max(infected_plot)

        if len(population[population[:,6] == 1]) >= len(population) * lockdown_percentage or\
           mx >= (len(population) * lockdown_percentage):
            #reduce speed of all members of society
            population[:,5] = np.clip(population[:,5], a_min = None, a_max = 0.001)
            #set speeds of complying people to 0
            population[:,5][lockdown_vector == 0] = 0
        else:
            #update randoms
            population = update_randoms(population, pop_size, speed=speed)
    else:
        #update randoms
        population = update_randoms(population, pop_size, speed=speed)

        
    #for dead ones: set speed and heading to 0
    population[:,3:5][population[:,6] == 3] = 0

    #update positions
    population = update_positions(population)
    
    #find new infections
    population, destinations = infect(population, pop_size, infection_range, infection_chance, frame, 
                                      healthcare_capacity, verbose, send_to_location = self_isolate,
                                      location_bounds = isolation_bounds, destinations = destinations,
                                      location_no = 1, location_odds = self_isolate_proportion,
                                      traveling_infects = traveling_infects)
   

    infected_plot.append(len(population[population[:,6] == 1]))

    #recover and die
    population = recover_or_die(population, frame, recovery_duration, mortality_chance,
                                risk_age, critical_age, critical_mortality_chance,
                                risk_increase, no_treatment_factor, age_dependent_risk,
                                treatment_dependent_risk, treatment_factor, verbose)

    #send cured back to population
    population[:,11][population[:,6] == 2] = 0

    fatalities_plot.append(len(population[population[:,6] == 3]))

    
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
            infected_arr = np.asarray(infected_plot)
            indices = np.argwhere(infected_arr >= healthcare_capacity)

            ax2.plot([healthcare_capacity for x in range(len(infected_plot))], 
                     color='red', label='healthcare capacity')

            ax2.plot(infected_plot, color='gray')
            ax2.plot(fatalities_plot, color='black', label='fatalities')
        
        if treatment_dependent_risk:
            ax2.plot(indices, infected_arr[infected_arr >= healthcare_capacity], 
                     color='red')

        ax2.legend(loc = 'best', fontsize = 6)
        #plt.savefig('render/%i.png' %frame)

    return population


if __name__ == '__main__':

    ###############################
    ##### SETTABLE PARAMETERS #####
    ###############################
    #set simulation parameters
    simulation_steps = 10000 #total simulation steps performed
    save_population = False #whether to dump population to data/population_{num}.npy
    #size of the simulated world in coordinates
    xbounds = [0, 1] 
    ybounds = [0, 1]

    x_plot = [0, 1]
    y_plot = [0, 1]

    visualise = True #whether to visualise the simulation 
    verbose = True #whether to print infections, recoveries and fatalities to the terminal
    plot_style = 'SIR' #whether to plot SIR parameters ('sir') or just infections and mortalities ('default')

    #population parameters
    pop_size = 2000
    mean_age=55
    max_age=105
    speed=0.01

    #motion parameters
    mean_speed = 0.01 # the mean speed (defined as heading * speed)
    std_speed = 0.01 / 3 #the standard deviation of the speed parameter
    #the proportion of the population that practices social distancing, simulated
    #by them standing still
    proportion_distancing = 0
    #when people have an active destination, the wander range defines the area
    #surrounding the destination they will wander upon arriving
    wander_range=0.05 

    #illness parameters
    infection_range=0.01 #range surrounding sick patient that infections can take place
    infection_chance=0.03   #chance that an infection spreads to nearby healthy people each tick
    recovery_duration=(200, 500) #how many ticks it may take to recover from the illness
    mortality_chance=0.02 #global baseline chance of dying from the disease

    #self isolation
    self_isolate = False #whether infected people will self-isolate
    self_isolate_proportion = 0.85 #proportion of infected
    isolation_bounds = [0.01, 0.01, 0.1, 0.99] #[xmin, ymin, xmax, ymax]
    traveling_infects = False #Whether those traveling to isolation can still infect others

    #lock down
    lockdown = False #whether to implement a lockdown
    lockdown_percentage = 0.1 #after this proportion is infected, lock-down begins
    lockdown_compliance = 0.95 #fraction of the population that will obey the lockdown
    lockdown_vector = np.zeros((pop_size,))
    #lockdown vector is 1 for those not complying
    lockdown_vector[np.random.uniform(size=(pop_size,)) >= lockdown_compliance] = 1

    #healthcare parameters
    healthcare_capacity = 300 #capacity of the healthcare system
    treatment_factor = 0.5 #when in treatment, affect risk by this factor
    no_treatment_factor = 3 #risk increase factor to use if healthcare system is full
    #risk parameters
    age_dependent_risk = True #whether risk increases with age
    risk_age = 55 #age where mortality risk starts increasing
    critical_age = 75 #age at and beyond which mortality risk reaches maximum
    critical_mortality_chance = 0.1 #maximum mortality risk for older age
    treatment_dependent_risk = True #whether risk is affected by treatment
    #whether risk between risk and critical age increases 'linear' or 'quadratic'
    risk_increase = 'quadratic' 
    
   
    ######################################
    ##### END OF SETTABLE PARAMETERS #####
    ######################################

    #create render folder if doesn't exist
    if not os.path.exists('render/'):
        os.makedirs('render/')

    #initialise population
    population = initialize_population(pop_size, mean_age, max_age, xbounds, ybounds)

    #initalise destinations vector
    destinations = initialize_destination_matrix(pop_size, 1)

    #define figure
    if visualise:
        fig = plt.figure(figsize=(5,7))
        spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])

        ax1 = fig.add_subplot(spec[0,0])
        plt.title('infection simulation')
        plt.xlim(xbounds[0], xbounds[1])
        plt.ylim(ybounds[0], ybounds[1])

        ax2 = fig.add_subplot(spec[1,0])
        ax2.set_title('number of infected')
        #ax2.set_xlim(0, simulation_steps)
        ax2.set_ylim(0, pop_size + 100)

    infected_plot = []
    fatalities_plot = []

    #define arguments for visualisation loop
    fargs = (population, destinations, pop_size, infection_range, 
             infection_chance, speed, recovery_duration, mortality_chance, 
             xbounds, ybounds, x_plot, y_plot, wander_range, risk_age, 
             critical_age, critical_mortality_chance,
             risk_increase, no_treatment_factor, treatment_factor, 
             healthcare_capacity, age_dependent_risk, treatment_dependent_risk, 
             visualise, verbose, self_isolate, self_isolate_proportion,
             isolation_bounds,traveling_infects, lockdown, lockdown_percentage, 
             lockdown_vector, plot_style,)

    #start animation loop through matplotlib visualisation
    if visualise:
        animation = FuncAnimation(fig, update, fargs = fargs, frames = simulation_steps, interval = 33)
        plt.show()
    else:
        #alternatively dry run simulation without visualising
        i = 0
        while i < simulation_steps:
            population, pop_tracker = update(i, population, destinations, pop_size, infection_range, 
                                             infection_chance, speed, recovery_duration, mortality_chance, 
                                             xbounds, ybounds, x_plot, y_plot, wander_range, risk_age, 
                                             critical_age, critical_mortality_chance,
                                             risk_increase, no_treatment_factor, treatment_factor, 
                                             healthcare_capacity, age_dependent_risk, treatment_dependent_risk, 
                                             visualise, verbose, self_isolate, self_isolate_proportion,
                                             isolation_bounds,traveling_infects, lockdown, lockdown_percentage, 
                                             lockdown_vector,plot_style)
            if len(population[population[:,6] == 1]) == 0 and i > 100:
                print('\n-----stopping-----\n')
                print('total dead: %i' %len(population[population[:,6] == 3]))
                print('total immune: %i' %len(population[population[:,6] == 2]))
                if save_population:
                    save_data(population, infected_plot, fatalities_plot)
                i = simulation_steps + 1

            sys.stdout.write('\r')
            sys.stdout.write('%i: healthy: %i, infected: %i, immune: %i, in treatment: %i, \
dead: %i, of total: %i' %(i, len(population[population[:,6] == 0]),
                          len(population[population[:,6] == 1]),
                          len(population[population[:,6] == 2]), 
                          len(population[population[:,10] == 1]),
                          len(population[population[:,6] == 3]),
                          pop_size))

            i += 1

        print('\n-----stopping after all sick recovered or died-----\n')
        print('total dead: %i' %len(population[population[:,6] == 3]))
        print('total immune: %i' %len(population[population[:,6] == 2]))

    if save_population:
        save_data(population, infected_plot, fatalities_plot)