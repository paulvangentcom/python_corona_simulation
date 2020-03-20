import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def initialize_population(pop_size, mean_age=45, max_age=105,
                          xbounds = [0, 1], ybounds = [0, 1]):
    '''initialized the population for the simulation

    the population matrix for this simulation has the following columns:

    0 : unique ID
    1 : current x coordinate
    2 : current y coordinate
    3 : current heading in x direction
    4 : current heading in y direction
    5 : current speed
    6 : current state (0=healthy, 1=sick, 2=immune, 3=dead)
    7 : age
    8 : infected_since (frame the person got infected)
    9 : recovery vector (used in determining when someone recovers or dies)
    10 : in treatment

    Keyword arguments
    -----------------
    pop_size : int
        the size of the population

    mean_age : int
        the mean age of the population. Age affects mortality chances

    max_age : int
        the max age of the population

    xbounds : 2d array
        lower and upper bounds of x axis

    ybounds : 2d array
        lower and upper bounds of y axis
    '''

    #initialize population matrix
    population = np.zeros((pop_size, 11))

    #initalize unique IDs
    population[:,0] = [x for x in range(pop_size)]

    #initialize random coordinates
    population[:,1] = np.random.uniform(low = xbounds[0] - 0.05, high = xbounds[1] + 0.05, 
                                        size = (pop_size,))
    population[:,2] = np.random.uniform(low = ybounds[0] - 0.05, high = ybounds[1] + 0.05, 
                                        size=(pop_size,))

    #initialize random headings -1 to 1
    population[:,3] = np.random.normal(loc = 0, scale = 1/3, 
                                       size=(pop_size,))
    population[:,4] = np.random.normal(loc = 0, scale = 1/3, 
                                       size=(pop_size,))

    #initialize random speeds
    population[:,5] = np.random.normal(0.01, 0.01/3)

    #initalize ages
    std_age = (max_age - mean_age) / 3
    population[:,7] = np.int32(np.random.normal(loc = mean_age, 
                                                scale = std_age, 
                                                size=(pop_size,)))

    population[:,7] = np.clip(population[:,7], a_min = 0, 
                              a_max = max_age) #clip those younger than 0 years

    #build recovery_vector
    population[:,9] = np.random.normal(loc = 0.5, scale = 0.5 / 3, size=(pop_size,))

    return population


def update_positions(population):
    '''update positions of all people

    Uses heading and speed to update all positions for
    the next time step

    Keyword arguments
    -----------------
    population : ndarray
        the array numpy containing all the population information
    '''

    #update positions
    #x
    population[:,1] = population[:,1] + (population[:,3] * population[:,5])
    #y
    population[:,2] = population[:,2] + (population [:,4] * population[:,5])

    return population


def out_of_bounds(population, xbounds, ybounds):
    '''checks which people are about to go out of bounds and corrects
    
    
    '''
    #update headings and positions where out of bounds
    #update x heading
    #determine number of elements that need to be updated
    shp = population[:,3][(population[:,1] <= xbounds[:,0]) &
                          (population[:,3] < 0)].shape
    population[:,3][(population[:,1] <= xbounds[:,0]) &
                    (population[:,3] < 0)] = np.random.normal(loc = 0.5, 
                                                              scale = 0.5/3,
                                                              size = shp)

    shp = population[:,3][(population[:,1] >= xbounds[:,1]) &
                          (population[:,3] > 0)].shape
    population[:,3][(population[:,1] >= xbounds[:,1]) &
                    (population[:,3] > 0)] = -np.random.normal(loc = 0.5, 
                                                                scale = 0.5/3,
                                                                size = shp)

    #update y heading
    shp = population[:,4][(population[:,2] <= ybounds[:,0]) &
                          (population[:,4] < 0)].shape
    population[:,4][(population[:,2] <= ybounds[:,0]) &
                    (population[:,4] < 0)] = np.random.normal(loc = 0.5, 
                                                              scale = 0.5/3,
                                                              size = shp)

    shp = population[:,4][(population[:,2] >= ybounds[:,1]) &
                          (population[:,4] > 0)].shape
    population[:,4][(population[:,2] >= ybounds[:,1]) &
                    (population[:,4] > 0)] = -np.random.normal(loc = 0.5, 
                                                               scale = 0.5/3,
                                                               size = shp)

    return population


def update_randoms(population, heading_update_chance=0.02, 
                   speed_update_chance=0.02):
    '''updates random states such as heading and speed'''

    #randomly update heading
    #x
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,3][update <= heading_update_chance] = np.random.normal(loc = 0, 
                                                       scale = 1/3,
                                                       size = shp)
    #y
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,4][update <= heading_update_chance] = np.random.normal(loc = 0, 
                                                       scale = 1/3,
                                                       size = shp)
    #randomize speeds
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,5][update <= heading_update_chance] = np.random.normal(loc = 0.01, 
                                                       scale = 0.01/3,
                                                       size = shp)    
    return population


def infect(population, infection_range, infection_chance, frame, healthcare_capacity, verbose):
    '''finds new infections'''

    #find new infections
    infected_previous_step = population[population[:,6] == 1]

    new_infections = []

    #if less than half are infected, slice based on infected (to speed up computation)
    if len(infected_previous_step) < (pop_size // 2):
        for patient in infected_previous_step:
            #define infection zone for patient
            infection_zone = [patient[1] - infection_range, patient[2] - infection_range,
                              patient[1] + infection_range, patient[2] + infection_range]

            #find healthy people surrounding infected patient
            indices = np.int32(population[:,0][(infection_zone[0] < population[:,1]) & 
                                               (population[:,1] < infection_zone[2]) &
                                               (infection_zone[1] < population [:,2]) & 
                                               (population[:,2] < infection_zone[3]) &
                                               (population[:,6] == 0)])
            for idx in indices:
                #roll die to see if healthy person will be infected
                if np.random.random() < infection_chance:
                    population[idx][6] = 1
                    population[idx][8] = frame
                    if len(population[population[:,10] == 1]) <= healthcare_capacity:
                        population[idx][10] = 1
                    new_infections.append(idx)

    else:
        #if more than half are infected slice based in healthy people (to speed up computation)
        healthy_previous_step = population[population[:,6] == 0]
        for person in healthy_previous_step:
            #define infecftion range around healthy person
            infection_zone = [person[1] - infection_range, person[2] - infection_range,
                              person[1] + infection_range, person[2] + infection_range]

            if person[6] == 0: #if person is not already infected, find if infected are nearby
                #find infected nearby healthy person
                if len(population[:,6][(infection_zone[0] < population[:,1]) & 
                                       (population[:,1] < infection_zone[2]) &
                                       (infection_zone[1] < population [:,2]) & 
                                       (population[:,2] < infection_zone[3]) &
                                       (population[:,6] == 1)]) > 0:

                    if np.random.random() < infection_chance:
                        #roll die to see if healthy person will be infected
                        population[np.int32(person[0])][6] = 1
                        population[np.int32(person[0])][8] = frame
                        if len(population[population[:,10] == 1]) <= healthcare_capacity:
                            population[np.int32(person[0])][10] = 1
                        new_infections.append(np.int32(person[0]))

    if len(new_infections) > 0 and verbose:
        print('at timestep %i these people got sick: %s' %(frame, new_infections))

    return population


def recover_or_die(population, frame, recovery_duration, mortality_chance, 
                   risk_age, critical_age, critical_mortality_chance, 
                   risk_increase, no_treatment_factor, age_dependent_risk,
                   treatment_dependent_risk, treatment_factor, verbose):
    '''see whether to recover or die

    '''

    #find sick people
    sick_people = population[population[:,6] == 1]

    #define vector of how long everyone has been sick
    illness_duration_vector = frame - sick_people[:,8]
    
    recovery_odds_vector = (illness_duration_vector - recovery_duration[0]) / np.ptp(recovery_duration)
    recovery_odds_vector = np.clip(recovery_odds_vector, a_min = 0, a_max = None)

    #update states of sick people 
    indices = sick_people[:,0][recovery_odds_vector >= sick_people[:,9]]

    cured = []
    died = []

    #decide whether to die or recover
    for idx in indices:
        #check if we want risk to be age dependent
        #if age_dependent_risk:
        if age_dependent_risk:
            updated_mortality_chance = compute_mortality(sick_people[sick_people[:,0] == idx][:,7][0], 
                                                         mortality_chance,
                                                         risk_age, critical_age, 
                                                         critical_mortality_chance, 
                                                         risk_increase)
        else:
            updated_mortality_chance = mortality_chance

        if sick_people[sick_people[:,0] == int(idx)][:,10] == 0 and treatment_dependent_risk:
            #if person is not in treatment, increase risk by no_treatment_factor
            updated_mortality_chance = updated_mortality_chance * no_treatment_factor
        elif sick_people[sick_people[:,0] == int(idx)][:,10] == 1 and treatment_dependent_risk:
            #if person is in treatment, decrease risk by 
            updated_mortality_chance = updated_mortality_chance * treatment_factor

        if np.random.random() <= updated_mortality_chance:
            #die
            sick_people[:,6][sick_people[:,0] == idx] = 3
            sick_people[:,10][sick_people[:,0] == idx] = 0
            died.append(np.int32(sick_people[sick_people[:,0] == idx][:,0][0]))
        else:
            #recover (become immune)
            sick_people[:,6][sick_people[:,0] == idx] = 2
            sick_people[:,10][sick_people[:,0] == idx] = 0
            cured.append(np.int32(sick_people[sick_people[:,0] == idx][:,0][0]))

    if len(died) > 0 and verbose:
        print('at timestep %i these people died: %s' %(frame, died))
    if len(cured) > 0 and verbose:
        print('at timestep %i these people recovered: %s' %(frame, cured))

    #put array back into population
    population[population[:,6] == 1] = sick_people

    return population


def compute_mortality(age, mortality_chance, risk_age=50,
                      critical_age=80, critical_mortality_chance=0.5,
                      risk_increase='linear'):

    '''compute mortality based on age

    The risk is computed based on the age, with the risk_age marking
    the age where risk starts increasing, and the crticial age marks where
    the 'critical_mortality_odds' become the new mortality chance.

    Whether risk increases linearly or quadratic is settable.

    Keyword arguments
    -----------------
    age : int
        the age of the person

    mortality_chance : float
        the base mortality chance
        can be very small but cannot be zero if increase is quadratic.

    risk_age : int
        the age from which risk starts increasing

    critical_age : int
        the age where mortality risk equals the specified 
        critical_mortality_odds

    critical_mortality_chance : float
        the odds of dying at the critical age

    risk_increase : str
        defines whether the mortality risk between the at risk age
        and the critical age increases linearly or exponentially
    '''

    if risk_age < age < critical_age: # if age in range
        if risk_increase == 'linear':
            #find linear risk
            step_increase = (critical_mortality_chance) / ((critical_age - risk_age) + 1)
            risk = critical_mortality_chance - ((critical_age - age) * step_increase)
            return risk
        elif risk_increase == 'quadratic':
            #define exponential function between risk_age and critical_age
            pw = 15
            A = np.exp(np.log(mortality_chance / critical_mortality_chance)/pw)
            a = ((risk_age - 1) - critical_age * A) / (A - 1)
            b = mortality_chance / ((risk_age -1) + a ) ** pw

            #define linespace
            x = np.linspace(0, critical_age, critical_age)
            #find values
            risk_values = ((x + a) ** pw) * b
            return risk_values[np.int32(age- 1)]
    elif age <= risk_age:
        #simply return the base mortality chance
        return mortality_chance
    elif age >= critical_age:
        #simply return the maximum mortality chance
        return critical_mortality_chance


def update(frame, population, infection_range=0.01, infection_chance=0.03, 
           recovery_duration=(200, 500), mortality_chance=0.02,
           xbounds=[0.02, 0.98], ybounds=[0.02, 0.98], wander_range=0.05,
           risk_age=55, critical_age=75, critical_mortality_chance=0.1,
           risk_increase='quadratic', no_treatment_factor=3, 
           treatment_factor=0.5, healthcare_capacity=250, age_dependent_risk=True, 
           treatment_dependent_risk=True, visualise=True, verbose=True):

    #add one infection to jumpstart
    if frame == 50:
        population[0][6] = 1
        population[0][8] = 75
        population[0][10] = 1

    #update out of bounds
    #define bounds arrays
    _xbounds = np.array([[xbounds[0] - 0.02, xbounds[1] + 0.02]] * len(population))
    _ybounds = np.array([[ybounds[0] - 0.02, ybounds[1] + 0.02]] * len(population))
    population = out_of_bounds(population, _xbounds, _ybounds)

    #update randoms
    population = update_randoms(population)

    #for dead ones: set speed and heading to 0
    population[:,3:5][population[:,6] == 3] = 0

    #update positions
    population = update_positions(population)
    
    #find new infections
    population = infect(population, infection_range, infection_chance, frame, 
                        healthcare_capacity, verbose)
    infected.append(len(population[population[:,6] == 1]))

    #recover and die
    population = recover_or_die(population, frame, recovery_duration, mortality_chance,
                                risk_age, critical_age, critical_mortality_chance,
                                risk_increase, no_treatment_factor, age_dependent_risk,
                                treatment_dependent_risk, treatment_factor, verbose)

    deaths.append(len(population[population[:,6] == 3]))

    if visualise:
        #construct plot and visualise
        spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=[5,2])
        ax1.clear()
        ax2.clear()

        ax1.set_xlim(xbounds[0] - 0.1, xbounds[1] + 0.1)
        ax1.set_ylim(ybounds[0] - 0.1, ybounds[1] + 0.1)

        healthy = population[population[:,6] == 0][:,1:3]
        ax1.scatter(healthy[:,0], healthy[:,1], color='gray', s = 2, label='healthy')
    
        sick = population[population[:,6] == 1][:,1:3]
        ax1.scatter(sick[:,0], sick[:,1], color='red', s = 2, label='infected')

        immune = population[population[:,6] == 2][:,1:3]
        ax1.scatter(immune[:,0], immune[:,1], color='green', s = 2, label='immune')
    
        dead = population[population[:,6] == 3][:,1:3]
        ax1.scatter(dead[:,0], dead[:,1], color='black', s = 2, label='dead')
    
        #add text descriptors
        ax1.text(xbounds[0], 
                 ybounds[1] + ((ybounds[1] - ybounds[0]) / 8), 
                 'timestep: %i healthy: %i, sick: %i immune: %i dead: %i' %(frame, 
                                                                            len(healthy),
                                                                            len(sick), 
                                                                            len(immune), 
                                                                            len(dead)),
                 fontsize = 8)
    
        ax2.set_title('number of infected')
        ax2.set_xlim(0, simulation_steps)
        ax2.set_ylim(0, pop_size + 100)
        ax2.plot(infected, color='gray')
        ax2.plot(deaths, color='black', label='deaths')

        if treatment_dependent_risk:
            ax2.plot([healthcare_capacity for x in range(simulation_steps)], color='red', 
                     label='healthcare capacity')

            infected_arr = np.asarray(infected)
            indices = np.argwhere(infected_arr >= healthcare_capacity)

            ax2.plot(indices, infected_arr[infected_arr >= healthcare_capacity], 
                     color='red')



            ax2.legend(loc = 1, fontsize = 6)

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
    wander_range=0.05 

    #illness parameters
    infection_range=0.01 #range surrounding sick patient that infections can take place
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
    

    population = initialize_population(pop_size)

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

    infected = []
    deaths = []
    
    #define arguments for visualisation loop
    fargs = (population, infection_range, infection_chance, 
             recovery_duration, mortality_chance, xbounds, ybounds, 
             wander_range, risk_age, critical_age, critical_mortality_chance,
             risk_increase, no_treatment_factor, treatment_factor, 
             healthcare_capacity, age_dependent_risk, treatment_dependent_risk, 
             visualise, verbose,)

    #start animation loop through matplotlib visualisation
    if visualise:
        animation = FuncAnimation(fig, update, fargs = fargs, frames = simulation_steps, interval = 33)
        plt.show()
    else:
        #alternatively dry run simulation without visualising
        for i in range(simulation_steps):
            population = update(i, population, infection_range, infection_chance, 
                                recovery_duration, mortality_chance, xbounds, ybounds, 
                                wander_range, risk_age, critical_age, critical_mortality_chance,
                                risk_increase, no_treatment_factor, treatment_factor, 
                                healthcare_capacity, age_dependent_risk, treatment_dependent_risk, 
                                visualise, verbose)
            if len(population[population[:,6] == 1]) == 0 and i > 100:
                print('\n-----stopping-----\n')
                print('total dead: %i' %len(population[population[:,6] == 3]))
                print('total immune: %i' %len(population[population[:,6] == 2]))
                sys.exit(0)
            sys.stdout.write('\r')
            sys.stdout.write('%i: healthy: %i, infected: %i, immune: %i, in treatment: %i, \
dead: %i, of total: %i' %(i, len(population[population[:,6] == 0]),
                          len(population[population[:,6] == 1]),
                          len(population[population[:,6] == 2]), 
                          len(population[population[:,10] == 1]),
                          len(population[population[:,6] == 3]),
                          pop_size))

        print('\n-----stopping-----\n')
        print('total dead: %i' %len(population[population[:,6] == 3]))
        print('total immune: %i' %len(population[population[:,6] == 2]))
    