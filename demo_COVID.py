import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from infection import infect, recover_or_die, compute_mortality
from motionHelper import update_positions, out_of_bounds, update_randoms
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
        destinations[:,0][0:100] = 0.05
        destinations[:,1][0:100] = 0.7
        population[:,13][0:100] = 0.01
        population[:,14][0:100] = 0.05

        #Top
        destinations[:,0][100:200] = 0.1
        destinations[:,1][100:200] = 0.75
        population[:,13][100:200] = 0.05
        population[:,14][100:200] = 0.01

        #Bottom
        destinations[:,0][200:300] = 0.1
        destinations[:,1][200:300] = 0.65
        population[:,13][200:300] = 0.05
        population[:,14][200:300] = 0.01


        #make O
        #first leg
        destinations[:,0][300:400] = 0.2
        destinations[:,1][300:400] = 0.7
        population[:,13][300:400] = 0.01
        population[:,14][300:400] = 0.05

        #Top
        destinations[:,0][400:500] = 0.25
        destinations[:,1][400:500] = 0.75
        population[:,13][400:500] = 0.05
        population[:,14][400:500] = 0.01

        #Bottom
        destinations[:,0][500:600] = 0.25
        destinations[:,1][500:600] = 0.65
        population[:,13][500:600] = 0.05
        population[:,14][500:600] = 0.01

        #second leg
        destinations[:,0][600:700] = 0.3
        destinations[:,1][600:700] = 0.7
        population[:,13][600:700] = 0.01
        population[:,14][600:700] = 0.05


        #make V
        #First leg
        destinations[:,0][700:800] = 0.35
        destinations[:,1][700:800] = 0.7
        population[:,13][700:800] = 0.01
        population[:,14][700:800] = 0.05

        #Bottom
        destinations[:,0][800:900] = 0.4
        destinations[:,1][800:900] = 0.65
        population[:,13][800:900] = 0.05
        population[:,14][800:900] = 0.01

        #second leg
        destinations[:,0][900:1000] = 0.45
        destinations[:,1][900:1000] = 0.7
        population[:,13][900:1000] = 0.01
        population[:,14][900:1000] = 0.05

        #Make I
        #leg
        destinations[:,0][1000:1100] = 0.5
        destinations[:,1][1000:1100] = 0.7
        population[:,13][1000:1100] = 0.01
        population[:,14][1000:1100] = 0.05

        #I dot
        destinations[:,0][1100:1200] = 0.5
        destinations[:,1][1100:1200] = 0.8
        population[:,13][1100:1200] = 0.01
        population[:,14][1100:1200] = 0.01

        #make D
        #first leg
        destinations[:,0][1200:1300] = 0.55
        destinations[:,1][1200:1300] = 0.67
        population[:,13][1200:1300] = 0.01
        population[:,14][1200:1300] = 0.03

        #Top
        destinations[:,0][1300:1400] = 0.6
        destinations[:,1][1300:1400] = 0.75
        population[:,13][1300:1400] = 0.05
        population[:,14][1300:1400] = 0.01

        #Bottom
        destinations[:,0][1400:1500] = 0.6
        destinations[:,1][1400:1500] = 0.65
        population[:,13][1400:1500] = 0.05
        population[:,14][1400:1500] = 0.01

        #second leg
        destinations[:,0][1500:1600] = 0.65
        destinations[:,1][1500:1600] = 0.7
        population[:,13][1500:1600] = 0.01
        population[:,14][1500:1600] = 0.05

        #dash
        destinations[:,0][1600:1700] = 0.725
        destinations[:,1][1600:1700] = 0.7
        population[:,13][1600:1700] = 0.03
        population[:,14][1600:1700] = 0.01

        #Make 1
        destinations[:,0][1700:1800] = 0.8
        destinations[:,1][1700:1800] = 0.7
        population[:,13][1700:1800] = 0.01
        population[:,14][1700:1800] = 0.05


        #Make 9
        #right leg
        destinations[:,0][1800:1900] = 0.91
        destinations[:,1][1800:1900] = 0.675
        population[:,13][1800:1900] = 0.01
        population[:,14][1800:1900] = 0.08

        #roof
        destinations[:,0][1900:2000] = 0.88
        destinations[:,1][1900:2000] = 0.75
        population[:,13][1900:2000] = 0.035
        population[:,14][1900:2000] = 0.01

        #middle
        destinations[:,0][2000:2100] = 0.88
        destinations[:,1][2000:2100] = 0.7
        population[:,13][2000:2100] = 0.035
        population[:,14][2000:2100] = 0.01

        #left vertical leg
        destinations[:,0][2100:2200] = 0.86
        destinations[:,1][2100:2200] = 0.72
        population[:,13][2100:2200] = 0.01
        population[:,14][2100:2200] = 0.01

        ###################
        ##### ROW TWO #####
        ###################

        #S
        #first leg
        destinations[:,0][2200:2300] = 0.115
        destinations[:,1][2200:2300] = 0.5
        population[:,13][2200:2300] = 0.01
        population[:,14][2200:2300] = 0.03

        #Top
        destinations[:,0][2300:2400] = 0.15
        destinations[:,1][2300:2400] = 0.55
        population[:,13][2300:2400] = 0.05
        population[:,14][2300:2400] = 0.01

        #second leg
        destinations[:,0][2400:2500] = 0.2
        destinations[:,1][2400:2500] = 0.45
        population[:,13][2400:2500] = 0.01
        population[:,14][2400:2500] = 0.03

        #middle
        destinations[:,0][2500:2600] = 0.15
        destinations[:,1][2500:2600] = 0.48
        population[:,13][2500:2600] = 0.05
        population[:,14][2500:2600] = 0.01

        #bottom
        destinations[:,0][2600:2700] = 0.15
        destinations[:,1][2600:2700] = 0.41
        population[:,13][2600:2700] = 0.05
        population[:,14][2600:2700] = 0.01

        #Make I
        #leg
        destinations[:,0][2700:2800] = 0.25
        destinations[:,1][2700:2800] = 0.45
        population[:,13][2700:2800] = 0.01
        population[:,14][2700:2800] = 0.05

        #I dot
        destinations[:,0][2800:2900] = 0.25
        destinations[:,1][2800:2900] = 0.55
        population[:,13][2800:2900] = 0.01
        population[:,14][2800:2900] = 0.01

        #M
        #Top
        destinations[:,0][2900:3000] = 0.37
        destinations[:,1][2900:3000] = 0.5
        population[:,13][2900:3000] = 0.07
        population[:,14][2900:3000] = 0.01

        #Left leg
        destinations[:,0][3000:3100] = 0.31
        destinations[:,1][3000:3100] = 0.45
        population[:,13][3000:3100] = 0.01
        population[:,14][3000:3100] = 0.05

        #Middle leg
        destinations[:,0][3100:3200] = 0.37
        destinations[:,1][3100:3200] = 0.45
        population[:,13][3100:3200] = 0.01
        population[:,14][3100:3200] = 0.05

        #Right leg
        destinations[:,0][3200:3300] = 0.43
        destinations[:,1][3200:3300] = 0.45
        population[:,13][3200:3300] = 0.01
        population[:,14][3200:3300] = 0.05

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