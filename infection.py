'''
this file contains all functions required in computing
new infections, recoveries, and deaths
'''

import numpy as np
from path_planning import go_to_location


def find_nearby(population, infection_zone, traveling_infects=False,
                kind='healthy', infected_previous_step=[]):
    '''finds nearby IDs

    Keyword Arguments
    -----------------

    kind : str (can be 'healthy' or 'infected')
        determines whether infected or healthy individuals are returned
        within the infection_zone


    Returns
    -------
    if kind='healthy', indices of healthy agents within the infection
    zone is returned. This is because for each healthy agent, the chance to
    become infected needs to be tested

    if kind='infected', only the number of infected within the infection zone is
    returned. This is because in this situation, the odds of the healthy agent at
    the center of the infection zone depend on how many infectious agents are around
    it.
    '''

    if kind.lower() == 'healthy':
        indices = np.int32(population[:,0][(infection_zone[0] < population[:,1]) & 
                                            (population[:,1] < infection_zone[2]) &
                                            (infection_zone[1] < population [:,2]) & 
                                            (population[:,2] < infection_zone[3]) &
                                            (population[:,6] == 0)])
        return indices

    elif kind.lower() == 'infected':
        if traveling_infects:
            infected_number = len(infected_previous_step[:,6][(infection_zone[0] < infected_previous_step[:,1]) & 
                                                            (infected_previous_step[:,1] < infection_zone[2]) &
                                                            (infection_zone[1] < infected_previous_step [:,2]) & 
                                                            (infected_previous_step[:,2] < infection_zone[3]) &
                                                            (infected_previous_step[:,6] == 1)])
        else:
            infected_number = len(infected_previous_step[:,6][(infection_zone[0] < infected_previous_step[:,1]) & 
                                                            (infected_previous_step[:,1] < infection_zone[2]) &
                                                            (infection_zone[1] < infected_previous_step [:,2]) & 
                                                            (infected_previous_step[:,2] < infection_zone[3]) &
                                                            (infected_previous_step[:,6] == 1) &
                                                            (infected_previous_step[:,11] == 0)])
        return infected_number
        
    else:
        raise ValueError('type to find %s not understood! Must be either \'healthy\' or \'ill\'')
        
        



def infect(population, Config, frame, send_to_location=False, 
           location_bounds=[], destinations=[], location_no=1, 
           location_odds=1.0):
    '''finds new infections.
    
    Function that finds new infections in an area around infected persens
    defined by infection_range, and infects others with chance infection_chance
    
    Keyword arguments
    -----------------
    population : ndarray
        array containing all data on the population

    pop_size : int
        the number if individuals in the population
    
    infection_range : float
        the radius around each infected person where transmission of virus can take place

    infection_chance : float
        the odds that the virus infects someone within range (range 0 to 1)

    frame : int
        the current timestep of the simulation

    healthcare_capacity : int
        the number of places available in the healthcare system

    verbose : bool
        whether to report illness events

    send_to_location : bool
        whether to give infected people a destination

    location_bounds : list
        the location bounds where the infected person is sent to and can roam
        within (xmin, ymin, xmax, ymax)

    destinations : list or ndarray
        the destinations vector containing destinations for each individual in the population.
        Needs to be of same length as population

    location_no : int
        the location number, used as index for destinations array if multiple possible
        destinations are defined

    location_odds: float
        the odds that someone goes to a location or not. Can be used to simulate non-compliance
        to for example self-isolation.

    traveling_infects : bool
        whether infected people heading to a destination can still infect others on the way there
    '''

    #mark those already infected first
    infected_previous_step = population[population[:,6] == 1]
    healthy_previous_step = population[population[:,6] == 0]

    new_infections = []

    #if less than half are infected, slice based on infected (to speed up computation)
    if len(infected_previous_step) < (Config.pop_size // 2):
        for patient in infected_previous_step:
            #define infection zone for patient
            infection_zone = [patient[1] - Config.infection_range, patient[2] - Config.infection_range,
                                patient[1] + Config.infection_range, patient[2] + Config.infection_range]

            #find healthy people surrounding infected patient
            if Config.traveling_infects or patient[11] == 0:
                indices = find_nearby(population, infection_zone, kind = 'healthy')
            else:
                indices = []

            for idx in indices:
                #roll die to see if healthy person will be infected
                if np.random.random() < Config.infection_chance:
                    population[idx][6] = 1
                    population[idx][8] = frame
                    if len(population[population[:,10] == 1]) <= Config.healthcare_capacity:
                        population[idx][10] = 1
                        if send_to_location:
                            #send to location if die roll is positive
                            if np.random.uniform() <= location_odds:
                                population[idx],\
                                destinations[idx] = go_to_location(population[idx],
                                                                   destinations[idx],
                                                                   location_bounds, 
                                                                   dest_no=location_no)
                        else:
                            pass
                    new_infections.append(idx)

    else:
        #if more than half are infected slice based in healthy people (to speed up computation)
            
        
        
        for person in healthy_previous_step:
            #define infecftion range around healthy person
            infection_zone = [person[1] - Config.infection_range, person[2] - Config.infection_range,
                                person[1] + Config.infection_range, person[2] + Config.infection_range]

            if person[6] == 0: #if person is not already infected, find if infected are nearby
                #find infected nearby healthy person
                if Config.traveling_infects:
                    poplen = find_nearby(population, infection_zone, 
                                         traveling_infects = True,
                                         kind = 'infected')
                else:
                    poplen = find_nearby(population, infection_zone, 
                                         traveling_infects = True,
                                         kind = 'infected',
                                         infected_previous_step = infected_previous_step)
                
                if poplen > 0:
                    if np.random.random() < (Config.infection_chance * poplen):
                        #roll die to see if healthy person will be infected
                        population[np.int32(person[0])][6] = 1
                        population[np.int32(person[0])][8] = frame
                        if len(population[population[:,10] == 1]) <= Config.healthcare_capacity:
                            population[np.int32(person[0])][10] = 1
                            if send_to_location:
                                #send to location and add to treatment if die roll is positive
                                if np.random.uniform() < location_odds:
                                    population[np.int32(person[0])],\
                                    destinations[np.int32(person[0])] = go_to_location(population[np.int32(person[0])],
                                                                                        destinations[np.int32(person[0])],
                                                                                        location_bounds, 
                                                                                        dest_no=location_no)


                        new_infections.append(np.int32(person[0]))

    if len(new_infections) > 0 and Config.verbose:
        print('at timestep %i these people got sick: %s' %(frame, new_infections))

    if len(destinations) == 0:
        return population
    else:
        return population, destinations


def recover_or_die(population, frame, Config):
    '''see whether to recover or die


    Keyword arguments
    -----------------
    population : ndarray
        array containing all data on the population

    frame : int
        the current timestep of the simulation

    recovery_duration : tuple
        lower and upper bounds of duration of recovery, in simulation steps

    mortality_chance : float
        the odds that someone dies in stead of recovers (between 0 and 1)

    risk_age : int or flaot
        the age from which mortality risk starts increasing

    critical_age: int or float
        the age where mortality risk equals critical_mortality_change

    critical_mortality_chance : float
        the heightened odds that an infected person has a fatal ending

    risk_increase : string
        can be 'quadratic' or 'linear', determines whether the mortality risk
        between the at risk age and the critical age increases linearly or
        exponentially

    no_treatment_factor : int or float
        defines a change in mortality odds if someone cannot get treatment. Can
        be larger than one to increase risk, or lower to decrease it.

    treatment_dependent_risk : bool
        whether availability of treatment influences patient risk

    treatment_factor : int or float
        defines a change in mortality odds if someone is in treatment. Can
        be larger than one to increase risk, or lower to decrease it.

    verbose : bool
        whether to report to terminal the recoveries and deaths for each simulation step
    '''

    #find infected people
    infected_people = population[population[:,6] == 1]

    #define vector of how long everyone has been sick
    illness_duration_vector = frame - infected_people[:,8]
    
    recovery_odds_vector = (illness_duration_vector - Config.recovery_duration[0]) / np.ptp(Config.recovery_duration)
    recovery_odds_vector = np.clip(recovery_odds_vector, a_min = 0, a_max = None)

    #update states of sick people 
    indices = infected_people[:,0][recovery_odds_vector >= infected_people[:,9]]

    recovered = []
    fatalities = []

    #decide whether to die or recover
    for idx in indices:
        #check if we want risk to be age dependent
        #if age_dependent_risk:
        if Config.age_dependent_risk:
            updated_mortality_chance = compute_mortality(infected_people[infected_people[:,0] == idx][:,7][0], 
                                                            Config.mortality_chance,
                                                            Config.risk_age, Config.critical_age, 
                                                            Config.critical_mortality_chance, 
                                                            Config.risk_increase)
        else:
            updated_mortality_chance = Config.mortality_chance

        if infected_people[infected_people[:,0] == int(idx)][:,10] == 0 and Config.treatment_dependent_risk:
            #if person is not in treatment, increase risk by no_treatment_factor
            updated_mortality_chance = updated_mortality_chance * Config.no_treatment_factor
        elif infected_people[infected_people[:,0] == int(idx)][:,10] == 1 and Config.treatment_dependent_risk:
            #if person is in treatment, decrease risk by 
            updated_mortality_chance = updated_mortality_chance * Config.treatment_factor

        if np.random.random() <= updated_mortality_chance:
            #die
            infected_people[:,6][infected_people[:,0] == idx] = 3
            infected_people[:,10][infected_people[:,0] == idx] = 0
            fatalities.append(np.int32(infected_people[infected_people[:,0] == idx][:,0][0]))
        else:
            #recover (become immune)
            infected_people[:,6][infected_people[:,0] == idx] = 2
            infected_people[:,10][infected_people[:,0] == idx] = 0
            recovered.append(np.int32(infected_people[infected_people[:,0] == idx][:,0][0]))

    if len(fatalities) > 0 and Config.verbose:
        print('at timestep %i these people died: %s' %(frame, fatalities))
    if len(recovered) > 0 and Config.verbose:
        print('at timestep %i these people recovered: %s' %(frame, recovered))

    #put array back into population
    population[population[:,6] == 1] = infected_people

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


def healthcare_infection_correction(worker_population, healthcare_risk_factor=0.2):
    '''corrects infection to healthcare population.

    Takes the healthcare risk factor and adjusts the sick healthcare workers
    by reducing (if < 0) ir increasing (if > 0) sick healthcare workers

    Keyword arguments
    -----------------
    worker_population : ndarray
        the array containing all variables related to the healthcare population.
        Is a subset of the 'population' matrix.

    healthcare_risk_factor : int or float
        if other than one, defines the change in odds of contracting an infection.
        Can be used to simulate healthcare personell having extra protections in place (< 1)
        or being more at risk due to exposure, fatigue, or other factors (> 1)
    '''

    if healthcare_risk_factor < 0:
        #set 1 - healthcare_risk_factor workers to non sick
        sick_workers = worker_population[:,6][worker_population[:,6] == 1]
        cure_vector = np.random.uniform((len(sick_workers)))
        sick_workers[:,6][cure_vector >= healthcare_risk_factor] = 0
    elif healthcare_risk_factor > 0:
        #TODO: make proportion of extra workers sick
        pass
    else:
        pass #if no changed risk, do nothing

    return worker_population