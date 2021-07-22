import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from infection import infect, recover_or_die, compute_mortality
from motion import update_positions, out_of_bounds, update_randoms
from path_planning import set_destination, check_at_destination, keep_at_destination
from population import initialize_population, initialize_destination_matrix


def update(frame, population, destinations, pop_size, infection_range=0.01, 
           infection_chance=0.03, recovery_duration=(200, 500), mortality_chance=0.02,
           xbounds=[0.02, 0.98], ybounds=[0.02, 0.98], wander_range_x=0.05, wander_range_y=0.05,
           risk_age=55, critical_age=75, critical_mortality_chance=0.1,
           risk_increase='quadratic', no_treatment_factor=3, 
           treatment_factor=0.5, healthcare_capacity=250, age_dependent_risk=True, 
           treatment_dependent_risk=True, visualise=True, verbose=True):

    #add one infection to jumpstart
    if frame == 100:
        #make C
        #first leg
        #THIS IS MY CHANGR IN THIS:
        destinations[:,0][0:100] = 0.05
        destinations[:,1][0:100] = 0.7
        population[:,13][0:100] = 0.01
        population[:,14][0:100] = 0.05
        #set all destinations active
        population[:,11] = 1

    elif frame == 400:
        population[:,11] = 0
        population[:,12] = 0
        population = update_randoms(population, pop_size, 1, 1)

    #define motion vectors if destinations active and not everybody is at destination
    active_dests = len(population[population[:,11] != 0]) # look op this only once

    if active_dests > 0 and len(population[population[:,12] == 0]) > 0:
        population = set_destination(population, destinations)
        population = check_at_destination(population, destinations)

    if active_dests > 0 and len(population[population[:,12] == 1]) > 0:
        #keep them at destination
        population = keep_at_destination(population, destinations,
                                         wander_factor = 1)

    #update out of bounds
    #define bounds arrays
    _xbounds = np.array([[xbounds[0] + 0.02, xbounds[1] - 0.02]] * len(population))
    _ybounds = np.array([[ybounds[0] + 0.02, ybounds[1] - 0.02]] * len(population))
    population = out_of_bounds(population, _xbounds, _ybounds)

    #update randoms
    population = update_randoms(population, pop_size)

    #for dead ones: set speed and heading to 0
    population[:,3:5][population[:,6] == 3] = 0

    #update positions
    population = update_positions(population)
    
    #find new infections
    population = infect(population, pop_size, infection_range, infection_chance, frame, 
                        healthcare_capacity, verbose)
    infected_plot.append(len(population[population[:,6] == 1]))

    #recover and die
    population = recover_or_die(population, frame, recovery_duration, mortality_chance,
                                risk_age, critical_age, critical_mortality_chance,
                                risk_increase, no_treatment_factor, age_dependent_risk,
                                treatment_dependent_risk, treatment_factor, verbose)

    fatalities_plot.append(len(population[population[:,6] == 3]))

    if visualise:
        #construct plot and visualise
        spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])
        ax1.clear()
        ax2.clear()

        ax1.set_xlim(xbounds[0], xbounds[1])
        ax1.set_ylim(ybounds[0], ybounds[1])
        
        healthy = population[population[:,6] == 0][:,1:3]
        ax1.scatter(healthy[:,0], healthy[:,1], color='gray', s = 2, label='healthy')
    
        infected = population[population[:,6] == 1][:,1:3]
        ax1.scatter(infected[:,0], infected[:,1], color='red', s = 2, label='infected')

        immune = population[population[:,6] == 2][:,1:3]
        ax1.scatter(immune[:,0], immune[:,1], color='green', s = 2, label='immune')
    
        fatalities = population[population[:,6] == 3][:,1:3]
        ax1.scatter(fatalities[:,0], fatalities[:,1], color='black', s = 2, label='fatalities')
        
    
        #add text descriptors
        ax1.text(xbounds[0], 
                 ybounds[1] + ((ybounds[1] - ybounds[0]) / 100), 
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
        ax2.set_xlim(0, simulation_steps)
        ax2.set_ylim(0, pop_size + 100)
        ax2.plot(infected_plot, color='gray')
        ax2.plot(fatalities_plot, color='black', label='fatalities')

        if treatment_dependent_risk:
            #ax2.plot([healthcare_capacity for x in range(simulation_steps)], color='red', 
            #         label='healthcare capacity')

            infected_arr = np.asarray(infected_plot)
            indices = np.argwhere(infected_arr >= healthcare_capacity)

            ax2.plot(indices, infected_arr[infected_arr >= healthcare_capacity], 
                     color='red')

            #ax2.legend(loc = 1, fontsize = 6)

        #plt.savefig('render/%i.png' %frame)

    return population


if __name__ == '__main__':

    ###############################
    ##### SETTABLE PARAMETERS #####
    ###############################
    #set simulation parameters
    simulation_steps = 5000 #total simulation steps performed
    #size of the simulated world in coordinates
    xbounds = [0, 1] 
    ybounds = [0, 1]

    visualise = True #whether to visualise the simulation 
    verbose = True #whether to print infections, recoveries and fatalities to the terminal

    #population parameters
    pop_size = 3300
    mean_age=45
    max_age=105

    #motion parameters
    mean_speed = 0.01 # the mean speed (defined as heading * speed)
    std_speed = 0.01 / 3 #the standard deviation of the speed parameter
    #the proportion of the population that practices social distancing, simulated
    #by them standing still
    proportion_distancing = 0
    #when people have an active destination, the wander range defines the area
    #surrounding the destination they will wander upon arriving
    wander_range_x = 0.05
    wander_range_y = 0.1

    #illness parameters
    infection_range=0.01 #range surrounding infected patient that infections can take place
    infection_chance=0.03 #chance that an infection spreads to nearby healthy people each tick
    recovery_duration=(200, 500) #how many ticks it may take to recover from the illness
    mortality_chance=0.02 #global baseline chance of dying from the disease

    #healthcare parameters
    healthcare_capacity = 300 #capacity of the healthcare system
    treatment_factor = 0.5 #when in treatment, affect risk by this factor

    #risk parameters
    age_dependent_risk = True #whether risk increases with age
    risk_age = 55 #age where mortality risk starts increasing
    critical_age = 75 #age at and beyond which mortality risk reaches maximum
    critical_mortality_chance = 0.1 #maximum mortality risk for older age
    treatment_dependent_risk = True #whether risk is affected by treatment
    #whether risk between risk and critical age increases 'linear' or 'quadratic'
    risk_increase = 'quadratic' 
    no_treatment_factor = 3 #risk increase factor to use if healthcare system is full
   
    ######################################
    ##### END OF SETTABLE PARAMETERS #####
    ######################################
    
    #initalize population
    population = initialize_population(pop_size, mean_age, max_age, xbounds, ybounds)
    population[:,13] = wander_range_x #set wander ranges to default specified value
    population[:,14] = wander_range_y #set wander ranges to default specified value

    #initialize destination matrix
    destinations = initialize_destination_matrix(pop_size, 1)

    #create render folder if doesn't exist
    if not os.path.exists('render/'):
        os.makedirs('render/')

    #define figure
    fig = plt.figure(figsize=(5,7))
    spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])

    ax1 = fig.add_subplot(spec[0,0])
    plt.title('infection simulation')
    plt.xlim(xbounds[0] - 0.1, xbounds[1] + 0.1)
    plt.ylim(ybounds[0] - 0.1, ybounds[1] + 0.1)

    ax2 = fig.add_subplot(spec[1,0])
    ax2.set_title('number of infected')
    ax2.set_xlim(0, simulation_steps)
    ax2.set_ylim(0, pop_size + 100)

    infected_plot = []
    fatalities_plot = []
    
    #define arguments for visualisation loop
    fargs = (population, destinations, pop_size, infection_range, infection_chance, 
             recovery_duration, mortality_chance, xbounds, ybounds, 
             wander_range_x, wander_range_y, risk_age, critical_age, 
             critical_mortality_chance, risk_increase, no_treatment_factor, 
             treatment_factor, healthcare_capacity, age_dependent_risk, 
             treatment_dependent_risk, visualise, verbose,)


    animation = FuncAnimation(fig, update, fargs = fargs, frames = simulation_steps, interval = 33)
    plt.show()