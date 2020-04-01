import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from environment import build_hospital
from infection import infect, recover_or_die, compute_mortality, \
healthcare_infection_correction
from motion import update_positions, out_of_bounds, update_randoms,\
set_destination, check_at_destination, keep_at_destination, get_motion_parameters
from population import initialize_population, initialize_destination_matrix,\
set_destination_bounds, save_data

from plot import figInit, figUpdate, personStateColors


def update(frame, population, destinations, pop_size, infection_range=0.01, 
           infection_chance=0.03, recovery_duration=(200, 500), mortality_chance=0.02,
           xbounds=[0.02, 0.98], ybounds=[0.02, 0.98], x_plot=[-0.1, 1], 
           y_plot=[-0.1, 1], wander_range_x=0.05, wander_range_y=0.05,
           risk_age=55, critical_age=75, critical_mortality_chance=0.1,
           risk_increase='quadratic', no_treatment_factor=3, 
           treatment_factor=0.5, healthcare_capacity=250, age_dependent_risk=True, 
           treatment_dependent_risk=True, visualise=True, verbose=True,
           healthcare_workers=50, hospital_bounds=None, healthcare_worker_risk=0):

    #add one infection to jumpstart
    if frame == 1:
        population[healthcare_workers + 1][6] = 1


    #define motion vectors if destinations active and not everybody is at destination
    active_dests = len(population[population[:,11] != 0]) # look op this only once

    if active_dests > 0 and len(population[population[:,12] == 0]) > 0:
        population = set_destination(population, destinations)
        population = check_at_destination(population, destinations, wander_factor = 1)

    if active_dests > 0 and len(population[population[:,12] == 1]) > 0:
        #keep them at destination
        population = keep_at_destination(population, destinations,
                                         wander_factor = 1)

    #update out of bounds
    #define bounds arrays
    if len(population[:,11] == 0) > 0:
        _xbounds = np.array([[xbounds[0] + 0.02, xbounds[1] - 0.02]] * len(population[population[:,11] == 0]))
        _ybounds = np.array([[ybounds[0] + 0.02, ybounds[1] - 0.02]] * len(population[population[:,11] == 0]))
        population[population[:,11] == 0] = out_of_bounds(population[population[:,11] == 0], 
                                                          _xbounds, _ybounds)

    #update randoms
    population = update_randoms(population, pop_size)

    #for dead ones: set speed and heading to 0
    population[:,3:5][population[:,6] == 3] = 0

    #update positions
    population = update_positions(population)
    
    #find new infections
    population, destinations = infect(population, pop_size, infection_range, infection_chance, frame, 
                                      healthcare_capacity, verbose, send_to_location = True,
                                      location_bounds = hospital_bounds, destinations = destinations,
                                      location_no = 1)
    #apply risk factor to healthcare worker pool
    if healthcare_worker_risk != 0: #if risk is not zero, affect workers
        workers = population[0:healthcare_workers]
        workers = healthcare_infection_correction(workers, healthcare_worker_risk)
        population[0:healthcare_workers] = workers

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
        ax1.clear()
        ax2.clear()

        figUpdate(ax1, ax2, x_plot, y_plot)

        if hospital_bounds != None:
            build_hospital(hospital_bounds[0], hospital_bounds[2],
                           hospital_bounds[1], hospital_bounds[3], ax1)
        
        healthy = population[population[:,6] == 0][:,1:3]
        ax1.scatter(healthy[:healthcare_workers][:,0], 
                    healthy[:healthcare_workers][:,1], 
                    marker= 'P', s = 2, color=personStateColors[2], 
                    label='healthy')

        ax1.scatter(healthy[healthcare_workers:][:,0], 
                    healthy[healthcare_workers:][:,1], 
                    color=personStateColors[0], s = 2, label='healthy')
    
        infected = population[population[:,6] == 1][:,1:3]
        ax1.scatter(infected[:,0], infected[:,1], color=personStateColors[1], s = 2, label='infected')

        immune = population[population[:,6] == 2][:,1:3]
        ax1.scatter(immune[:,0], immune[:,1], color=personStateColors[2], s = 2, label='immune')
    
        fatalities = population[population[:,6] == 3][:,1:3]
        ax1.scatter(fatalities[:,0], fatalities[:,1], color=personStateColors[3], s = 2, label='dead')
        
    
        #add text descriptors
        ax1.text(x_plot[0], 
                 y_plot[1] + ((y_plot[1] - y_plot[0]) / 8), 
                 'timestep: %i, total: %i, healthy: %i infected: %i immune: %i fatalities: %i' %(frame,
                                                                                              len(population),
                                                                                              len(healthy), 
                                                                                              len(infected), 
                                                                                              len(immune), 
                                                                                              len(fatalities)),
                 fontsize=6)
    
        ax2.text(0, pop_size * 0.05, 
                 'https://github.com/paulvangentcom/python-corona-simulation',
                 fontsize=6, alpha=0.5)
        #ax2.set_xlim(0, simulation_steps)
        ax2.set_ylim(0, pop_size + 100)

        if treatment_dependent_risk:
            infected_arr = np.asarray(infected_plot)
            indices = np.argwhere(infected_arr >= healthcare_capacity)

            ax2.plot([healthcare_capacity for x in range(len(infected_plot))], color='red', 
                     label='healthcare capacity')

        ax2.plot(infected_plot, color='gray')
        ax2.plot(fatalities_plot, color='black', label='fatalities')
        ax2.legend(loc = 1, fontsize = 6)

        if treatment_dependent_risk:
            ax2.plot(indices, infected_arr[infected_arr >= healthcare_capacity], 
                     color='red')


        #plt.savefig('render/%i.png' %frame)

    return population


if __name__ == '__main__':

    ###############################
    ##### SETTABLE PARAMETERS #####
    ###############################
    #set simulation parameters
    simulation_steps = 5000 #total simulation steps performed
    save_population = True #whether to dump population to data/population_{num}.npy
    #size of the simulated world in coordinates
    xbounds = [0.3, 1.3] 
    ybounds = [0, 1]

    x_plot = [0, 1.3]
    y_plot = [0, 1]

    visualise = True #whether to visualise the simulation 
    verbose = True #whether to print infections, recoveries and deaths to the terminal

    #population parameters
    pop_size = 2000
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
    healthcare_workers = 0 #number of healthcare workers, must be smaller than population size
    hospital_bounds = [0.05, 0.4, 0.25, 0.7] #[xmin, ymin, xmax, ymax]
    healthcare_worker_risk = 0.2 #affect odds to get sick for healthcare workers with this factor

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
    population = initialize_population(pop_size, xbounds = xbounds, ybounds = ybounds)
    population[:,13] = wander_range_x #set wander ranges to default specified value
    population[:,14] = wander_range_y #set wander ranges to default specified value

    #initialize destination matrix
    destinations = initialize_destination_matrix(pop_size, 1)

    #place hospital on map x(-2, -1.5) y(-0.5, 0.5)
    #put hospital workers (first 50?) in their own bounds
    
    #population[0:healthcare_workers], \
    #destinations[0:healthcare_workers] = set_destination_bounds(population[0:healthcare_workers], 
    #                                                            destinations[0:healthcare_workers],
    #                                                            hospital_bounds[0],
    #                                                            hospital_bounds[1],
    #                                                            hospital_bounds[2],
    #                                                            hospital_bounds[3],
    #                                                            dest_no=1)

    #define figure
    fig, ax1, ax2 = figInit(xbounds, ybounds, pop_size)

    infected_plot = []
    fatalities_plot = []
    
    #define arguments for visualisation loop
    fargs = (population, destinations, pop_size, infection_range, infection_chance, 
             recovery_duration, mortality_chance, xbounds, ybounds, x_plot, y_plot,
             wander_range_x, wander_range_y, risk_age, critical_age, 
             critical_mortality_chance, risk_increase, no_treatment_factor, 
             treatment_factor, healthcare_capacity, age_dependent_risk, 
             treatment_dependent_risk, visualise, verbose, healthcare_workers,
             hospital_bounds, healthcare_worker_risk)


    #start animation loop through matplotlib visualisation
    if visualise:
        animation = FuncAnimation(fig, update, fargs = fargs, frames = simulation_steps, interval = 33)
        plt.show()
    else:
        #alternatively dry run simulation without visualising
        for i in range(simulation_steps):
            population = update(i, population, destinations, pop_size, infection_range, infection_chance, 
                                recovery_duration, mortality_chance, xbounds, ybounds, x_plot, y_plot,
                                wander_range_x, wander_range_y, risk_age, critical_age, 
                                critical_mortality_chance, risk_increase, no_treatment_factor, 
                                treatment_factor, healthcare_capacity, age_dependent_risk, 
                                treatment_dependent_risk, visualise, verbose, healthcare_workers,
                                healthcare_bounds, healthcare_worker_risk)
            if len(population[population[:,6] == 1]) == 0 and i > 100:
                print('\n-----stopping-----\n')
                print('total dead: %i' %len(population[population[:,6] == 3]))
                print('total immune: %i' %len(population[population[:,6] == 2]))
                if save_population:
                    save_data(population, infected_plot, fatalities_plot)
                sys.exit(0)
            sys.stdout.write('\r')
            sys.stdout.write('%i: healthy: %i, infected: %i, immune: %i, in treatment: %i, \
dead: %i, of total: %i' %(i, len(population[population[:,6] == 0]),
                          len(population[population[:,6] == 1]),
                          len(population[population[:,6] == 2]), 
                          len(population[population[:,10] == 1]),
                          len(population[population[:,6] == 3]),
                          pop_size))

        print('\n-----stopping after all infected recovered or died-----\n')
        print('total dead: %i' %len(population[population[:,6] == 3]))
        print('total immune: %i' %len(population[population[:,6] == 2]))

    if save_population:
        save_data(population, infected_plot, fatalities_plot)